"""Paths and settings. Everything the harness reads or writes is located here."""
from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

VAULT = ROOT / "vault"            # the Obsidian vault (human-facing)
RAW = VAULT / "raw"               # original sources, never modified by the harness
WIKI = VAULT / "wiki"             # generated + reviewed notes
INDEX_MD = VAULT / "index.md"     # human landing page
CATALOG_MD = VAULT / "Source Catalog.md"

PROMPTS = ROOT / "prompts"        # persona + research rules, loaded per mode
DATA = ROOT / "data"              # machine files: retrieval index, state, logs (outside the vault)
INDEX_DIR = DATA / "index"
STATE_FILE = DATA / "wiki_state.json"
CATALOG_JSON = DATA / "source_catalog.json"
RUN_LOG = DATA / "logs" / "runs.jsonl"

TESTS = ROOT / "tests"            # answer key, outside the vault
EVIDENCE = ROOT / "evidence"      # saved evidence cards
OUTPUTS = ROOT / "outputs"        # explicitly saved chat drafts (never treated as evidence)


@dataclass
class Settings:
    runtime_url: str = "http://127.0.0.1:11434"
    model: str = "gemma4:e2b-it-qat"
    embed_model: str = "embeddinggemma:300m"
    num_ctx: int = 8192
    ingest_num_ctx: int = 16384
    temperature: float = 0.2
    keep_alive: str = "10m"
    seed: int = 42
    online_api_url: str = "https://generativelanguage.googleapis.com/v1beta"
    online_model: str = "gemma-3-27b-it"
    online_api_key_env: str = "GEMINI_API_KEY"
    top_k: int = 6
    chat_top_k: int = 4
    max_passage_words: int = 220
    rrf_k: int = 60
    history_turns: int = 8
    extra: dict = field(default_factory=dict)


def load_settings(path: Path | None = None) -> Settings:
    path = path or ROOT / "config.toml"
    if not path.exists():
        return Settings()
    cfg = tomllib.loads(path.read_text())
    local, online = cfg.get("local", {}), cfg.get("online", {})
    retrieval, chat = cfg.get("retrieval", {}), cfg.get("chat", {})
    s = Settings()
    s.runtime_url = local.get("runtime_url", s.runtime_url)
    s.model = local.get("model", s.model)
    s.embed_model = local.get("embed_model", s.embed_model)
    s.num_ctx = local.get("num_ctx", s.num_ctx)
    s.ingest_num_ctx = local.get("ingest_num_ctx", s.ingest_num_ctx)
    s.temperature = local.get("temperature", s.temperature)
    s.keep_alive = local.get("keep_alive", s.keep_alive)
    s.seed = local.get("seed", s.seed)
    s.online_api_url = online.get("api_url", s.online_api_url)
    s.online_model = online.get("model", s.online_model)
    s.online_api_key_env = online.get("api_key_env", s.online_api_key_env)
    s.top_k = retrieval.get("top_k", s.top_k)
    s.chat_top_k = retrieval.get("chat_top_k", s.chat_top_k)
    s.max_passage_words = retrieval.get("max_passage_words", s.max_passage_words)
    s.rrf_k = retrieval.get("rrf_k", s.rrf_k)
    s.history_turns = chat.get("history_turns", s.history_turns)
    return s
