"""The harness: the application code between the CLI and the model.

    CLI command ──► Harness.<mode>() ──► retrieval tool? ──► prompt assembly ──► Gemma ──► checks ──► result + log

  search : retrieval only. Returns original passages. Never calls the language model.
  ask    : RAG. Retrieve evidence -> research rules + evidence + question -> Gemma (JSON)
           -> citation checks -> answer or "insufficient evidence". Stateless: no chat history.
  chat   : persona + recent conversation. A router decides per turn whether notes are
           needed; only then is retrieval called and the notes added to that turn.
"""
from __future__ import annotations

import re
import time
from dataclasses import asdict, dataclass, field

from . import prompts
from .citations import Verification, chat_citation_issues, verify_answer
from .config import OUTPUTS, Settings
from .evidence import log_run, memory_snapshot, network_status
from .llm import get_model, parse_json
from .retrieval import Hit, Retriever


def hit_dict(h: Hit) -> dict:
    return {"passage": h.passage, "score": h.score, "bm25_rank": h.bm25_rank,
            "dense_rank": h.dense_rank, "dense_sim": h.dense_sim}


@dataclass
class AskResult:
    question: str
    mode: str
    model: str
    retrieval_method: str
    hits: list[dict]
    raw_output: str
    verification: Verification
    seconds_retrieval: float
    seconds_model: float
    network: str
    memory: dict
    model_stats: dict = field(default_factory=dict)

    @property
    def status(self) -> str:
        return self.verification.status

    def to_dict(self) -> dict:
        d = asdict(self)
        d["verification"] = self.verification.to_dict()
        return d


class Harness:
    def __init__(self, settings: Settings, mode: str = "local", model: str | None = None):
        self.s = settings
        self.mode = mode
        self.llm = get_model(settings, mode, model)
        self._retriever: Retriever | None = None

    @property
    def retriever(self) -> Retriever:
        if self._retriever is None:
            self._retriever = Retriever(self.s)
        return self._retriever

    # ---- search: retrieval tool only ----------------------------------------------
    def search(self, query: str, k: int = 8, keyword_only: bool = False,
               kinds: tuple[str, ...] = ("source", "wiki")) -> tuple[list[Hit], str]:
        t0 = time.perf_counter()
        hits, method = self.retriever.search(query, k=k, kinds=kinds, keyword_only=keyword_only)
        log_run({"command": "search", "query": query, "method": method, "network": network_status(),
                 "seconds": round(time.perf_counter() - t0, 3), "hits": [h.id for h in hits]})
        return hits, method

    # ---- ask: standalone RAG ----------------------------------------------------------
    def ask(self, question: str) -> AskResult:
        self.llm.check()
        t0 = time.perf_counter()
        # Evidence = original sources only. Generated wiki notes are navigation, not proof.
        hits, method = self.retriever.search(question, k=self.s.top_k, kinds=("source",))
        t1 = time.perf_counter()
        passages = [h.passage for h in hits]
        result = self.llm.chat(prompts.ask_messages(question, passages), schema=prompts.ASK_SCHEMA)
        try:
            parsed = parse_json(result.text)
        except ValueError:
            parsed = {"status": "insufficient_evidence", "claims": [], "note": "Model output was not valid JSON."}
        verification = verify_answer(parsed, passages)
        verification.reason = verification.reason or parsed.get("note", "")
        out = AskResult(question, self.llm.backend, self.llm.model, method, [hit_dict(h) for h in hits],
                        result.text, verification, round(t1 - t0, 3), round(result.seconds, 2),
                        network_status(), memory_snapshot(self.llm), result.stats)
        log_run({"command": "ask", "question": question, "mode": out.mode, "model": out.model,
                 "status": out.status, "hits": [h.id for h in hits], "seconds_model": out.seconds_model,
                 "network": out.network})
        return out


class ChatSession:
    """Conversation state for `wiki chat`. History is conversation, never evidence."""

    SKIP_PATTERNS = re.compile(
        r"^\s*(hi|hello|hey|thanks|thank you|ok|okay|cool|great)\b|what can (you|we) do|"
        r"what can you help|who are you|how do (i|you) use|"
        r"\b(make|write|rewrite|turn) (that|it|this)\b|\b(shorter|longer|more formal|less formal)\b",
        re.I)

    def __init__(self, harness: Harness):
        self.h = harness
        self.history: list[dict] = []
        self.last_reply = ""
        self.last_passages: list[dict] = []

    def route(self, message: str) -> tuple[bool, str, str]:
        """Decide whether this turn needs notes. Returns (needs_notes, query, reason)."""
        if message.lower().startswith("/notes "):
            return True, message[7:].strip(), "forced by /notes"
        if self.SKIP_PATTERNS.search(message):
            return False, "", "rule: conversational / capability / edit request"
        try:
            r = self.h.llm.chat(prompts.router_messages(message, self.history),
                                schema=prompts.ROUTER_SCHEMA, temperature=0)
            d = parse_json(r.text)
            return bool(d.get("needs_notes")), d.get("query") or message, "model router"
        except Exception:  # router failure should never break the conversation
            return True, message, "router failed; retrieving to be safe"

    def turn(self, message: str):
        """Generator: yields reply text pieces, then a final dict with turn metadata."""
        needs, query, reason = self.route(message)
        user_text = message[7:].strip() if message.lower().startswith("/notes ") else message
        passages, hits, method = [], [], ""
        if needs:
            hits, method = self.h.retriever.search(query, k=self.h.s.chat_top_k)
            passages = [h.passage for h in hits]
        recent = self.history[-2 * self.h.s.history_turns:]
        final = None
        for piece in self.h.llm.stream_chat(prompts.chat_messages(recent, user_text, passages)):
            if isinstance(piece, str):
                yield piece
            else:
                final = piece
        reply = final.text if final else ""
        # Store the reply with citations spelled out, so later turns know what [n] meant.
        stored = reply
        for n, p in enumerate(passages, 1):
            stored = stored.replace(f"[{n}]", f"[{p['label']}, {p['locator']}]")
        self.history += [{"role": "user", "content": user_text}, {"role": "assistant", "content": stored}]
        self.last_reply, self.last_passages = reply, passages
        meta = {"retrieved": needs, "route_reason": reason, "query": query if needs else None,
                "method": method, "passages": [f"{p['label']}, {p['locator']}" for p in passages],
                "passage_ids": [p["id"] for p in passages],
                "invalid_citations": chat_citation_issues(reply, len(passages)),
                "seconds": round(final.seconds, 2) if final else None, "model": self.h.llm.model,
                "mode": self.h.llm.backend}
        log_run({"command": "chat", "message": user_text, **meta})
        yield meta

    def save_last(self, name: str | None = None):
        """Explicit user action: save the last reply as a draft (outputs/, never the vault)."""
        if not self.last_reply:
            return None
        OUTPUTS.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%d-%H%M%S")
        path = OUTPUTS / f"{stamp}-{re.sub(r'[^a-z0-9]+', '-', (name or 'draft').lower())}.md"
        sources = "\n".join(f"- [{n}] {p['label']}, {p['locator']} ({p['path']})"
                            for n, p in enumerate(self.last_passages, 1))
        path.write_text(f"<!-- Draft generated in chat by {self.h.llm.model}. Not source evidence. -->\n\n"
                        f"{self.last_reply}\n\n" + (f"## Notes used\n{sources}\n" if sources else ""))
        return path

    def reset(self):
        self.history, self.last_reply, self.last_passages = [], "", []
