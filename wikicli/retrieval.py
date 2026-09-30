"""The retrieval tool: find evidence passages for a query.

Two local signals, fused with Reciprocal Rank Fusion (RRF):
  * BM25 keyword search  - exact terms, names, numbers. Needs no model at all.
  * Embedding search     - meaning ("real estate" ~ "land"), using EmbeddingGemma via Ollama.
If the embedding model is not reachable, retrieval falls back to BM25 alone, so
`wiki search` keeps working without any model running.

The index lives in data/index/ (outside the Obsidian vault):
  passages.jsonl   one passage per line (sources + wiki notes)
  embeddings.npy   one unit-normalised vector per passage, same order
  manifest.json    embedding model, counts, build time
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass

import numpy as np
from rank_bm25 import BM25Okapi

from .config import INDEX_DIR, Settings
from .llm import LocalGemma, ModelUnavailable

STOPWORDS = set("""a an and are as at be but by did do does for from had has have how i in into is it its
of on or that the their them then there these they this to was were what when where which who why will
with you your we our us can could would should about after before between during over under than so
not no yes also just""".split())

# EmbeddingGemma was trained with task prefixes; using them improves retrieval quality.
QUERY_PREFIX = "task: search result | query: "
DOC_PREFIX = "title: {title} | text: "


def tokenize(text: str) -> list[str]:
    toks = re.findall(r"[a-z0-9$%]+(?:['’][a-z]+)?", text.lower())
    out = []
    for t in toks:
        if t in STOPWORDS:
            continue
        if len(t) > 4 and t.endswith("s") and not t.endswith("ss"):
            t = t[:-1]                      # crude plural folding: "firms" -> "firm"
        out.append(t)
    return out


@dataclass
class Hit:
    passage: dict
    score: float                 # fused RRF score
    bm25_rank: int | None
    dense_rank: int | None
    dense_sim: float | None

    @property
    def id(self) -> str:
        return self.passage["id"]


def build_index(passages: list[dict], settings: Settings) -> dict:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    with open(INDEX_DIR / "passages.jsonl", "w") as f:
        for p in passages:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    manifest = {"built_at": time.strftime("%Y-%m-%d %H:%M:%S"), "passages": len(passages),
                "sources": sum(p["kind"] == "source" for p in passages),
                "wiki": sum(p["kind"] == "wiki" for p in passages), "embed_model": None}
    llm = LocalGemma(settings)
    emb_file = INDEX_DIR / "embeddings.npy"
    if llm.embeddings_available():
        vecs = np.array(llm.embed([DOC_PREFIX.format(title=p["title"]) + p["text"] for p in passages]),
                        dtype=np.float32)
        vecs /= np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-9
        np.save(emb_file, vecs)
        manifest["embed_model"] = settings.embed_model
    elif emb_file.exists():
        emb_file.unlink()   # never keep vectors that no longer match passages.jsonl
    (INDEX_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


class Retriever:
    def __init__(self, settings: Settings):
        self.s = settings
        pfile = INDEX_DIR / "passages.jsonl"
        if not pfile.exists():
            raise FileNotFoundError("No retrieval index yet. Run `wiki ingest` first.")
        self.passages = [json.loads(line) for line in pfile.read_text().splitlines() if line.strip()]
        self.manifest = json.loads((INDEX_DIR / "manifest.json").read_text())
        self.bm25 = BM25Okapi([tokenize(p["title"] + " " + p["text"]) for p in self.passages])
        emb = INDEX_DIR / "embeddings.npy"
        self.vectors = np.load(emb) if emb.exists() else None
        self.llm = LocalGemma(settings)

    def search(self, query: str, k: int = 6, kinds: tuple[str, ...] = ("source", "wiki"),
               keyword_only: bool = False) -> tuple[list[Hit], str]:
        """Return (hits, method). method says which signals were actually used."""
        allowed = [i for i, p in enumerate(self.passages) if p["kind"] in kinds]
        if not allowed:
            return [], "empty index"

        bm = self.bm25.get_scores(tokenize(query))
        bm_order = [i for i in sorted(allowed, key=lambda i: -bm[i]) if bm[i] > 0]
        bm_rank = {i: r for r, i in enumerate(bm_order, 1)}

        dense_rank, sims, method = {}, {}, "bm25 (keyword only)"
        if not keyword_only and self.vectors is not None:
            try:
                q = np.array(self.llm.embed([QUERY_PREFIX + query])[0], dtype=np.float32)
                q /= np.linalg.norm(q) + 1e-9
                all_sims = self.vectors @ q
                d_order = sorted(allowed, key=lambda i: -all_sims[i])
                dense_rank = {i: r for r, i in enumerate(d_order, 1)}
                sims = {i: float(all_sims[i]) for i in allowed}
                method = f"hybrid: bm25 + {self.manifest.get('embed_model')} (RRF)"
            except ModelUnavailable:
                method = "bm25 (embedding model unavailable, keyword fallback)"

        k_rrf = self.s.rrf_k
        fused = {}
        for i in allowed:
            s = 0.0
            if i in bm_rank:
                s += 1 / (k_rrf + bm_rank[i])
            if i in dense_rank:
                s += 1 / (k_rrf + dense_rank[i])
            if s:
                fused[i] = s
        top = sorted(fused, key=lambda i: -fused[i])[:k]
        return [Hit(self.passages[i], fused[i], bm_rank.get(i), dense_rank.get(i), sims.get(i))
                for i in top], method
