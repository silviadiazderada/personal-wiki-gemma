"""Prompt assembly. The model reads nothing on its own: every instruction and every
passage it sees is put into the messages here, per mode."""
from __future__ import annotations

from .config import PROMPTS


def load(name: str) -> str:
    return (PROMPTS / f"{name}.md").read_text(encoding="utf-8")


def format_passages(passages: list[dict]) -> str:
    """Numbered evidence block. The numbers are what the model cites."""
    blocks = []
    for n, p in enumerate(passages, 1):
        origin = "original source" if p["kind"] == "source" else "wiki note (generated summary)"
        blocks.append(f"[{n}] {p['label']}, {p['locator']} ({origin})\n{p['text']}")
    return "\n\n".join(blocks)


# ---- ask ------------------------------------------------------------------------

ASK_SCHEMA = {
    # Property order matters: Ollama generates keys in this order, so the model writes the
    # supported claims first and only then decides the status (see README, iteration 1).
    "type": "object",
    "properties": {
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "citations": {"type": "array", "items": {"type": "integer"}},
                },
                "required": ["text", "citations"],
            },
        },
        "status": {"type": "string", "enum": ["answered", "insufficient_evidence"]},
        "note": {"type": "string"},
    },
    "required": ["claims", "status", "note"],
}


def ask_messages(question: str, passages: list[dict]) -> list[dict]:
    """Ask mode: research rules + evidence + one standalone question. No history, no persona."""
    return [
        {"role": "system", "content": load("wiki-instructions")},
        {"role": "user", "content": (
            f"Evidence passages:\n\n{format_passages(passages)}\n\n"
            f"Question: {question}\n\n"
            "Return JSON: first the claims the passages support (each with citations), then status, then note."
        )},
    ]


# ---- chat -----------------------------------------------------------------------

ROUTER_SCHEMA = {
    "type": "object",
    "properties": {"needs_notes": {"type": "boolean"}, "query": {"type": "string"}},
    "required": ["needs_notes", "query"],
}


def router_messages(message: str, recent: list[dict]) -> list[dict]:
    convo = "\n".join(f"{m['role']}: {m['content'][:300]}" for m in recent[-4:]) or "(no earlier messages)"
    return [
        {"role": "system", "content": load("router")},
        {"role": "user", "content": f"Recent conversation:\n{convo}\n\nLatest message: {message}"},
    ]


def chat_messages(history: list[dict], message: str, passages: list[dict] | None) -> list[dict]:
    """Chat mode: persona + recent conversation + (only if the router asked) retrieved notes."""
    msgs = [{"role": "system", "content": load("persona")}]
    msgs += history
    if passages:
        msgs.append({"role": "system", "content": (
            "Notes retrieved from Silvia's course wiki for the next message. Cite them as [n] when you "
            "use them; anything else you add is a suggestion, not a course fact.\n\n" + format_passages(passages))})
    msgs.append({"role": "user", "content": message})
    return msgs


# ---- ingest ---------------------------------------------------------------------

CATEGORIES = ["Concepts", "People", "Organizations", "Policies and Events", "Course Logistics"]

TOPICS_SCHEMA = {
    "type": "object",
    "properties": {
        "source_summary": {"type": "string"},
        "topics": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "category": {"type": "string", "enum": CATEGORIES},
                    "summary": {"type": "string"},
                    "facts": {"type": "array", "items": {
                        "type": "object",
                        "properties": {"text": {"type": "string"},
                                       "slides": {"type": "array", "items": {"type": "integer"}}},
                        "required": ["text", "slides"]}},
                },
                "required": ["title", "category", "summary", "facts"],
            },
        },
    },
    "required": ["source_summary", "topics"],
}


def topics_messages(label: str, passages: list[dict]) -> list[dict]:
    """Depends only on the source itself, so re-ingesting the same file gives the same topics.
    Matching topics across sources happens afterwards, in code (see ingest.py)."""
    slides = "\n\n".join(f"(slide {p['number']}) {p['text']}" for p in passages)
    return [
        {"role": "system", "content": load("ingest-topics")},
        {"role": "user", "content": f"Source: {label}\n\n{slides}"},
    ]


def links_schema(candidates: list[str]) -> dict:
    return {
        "type": "object",
        "properties": {"related": {"type": "array", "maxItems": 3, "items": {
            "type": "object",
            "properties": {"title": {"type": "string", "enum": candidates}, "reason": {"type": "string"},
                           "connection": {"type": "string", "enum": ["direct", "loose"]}},
            "required": ["title", "reason", "connection"]}}},
        "required": ["related"],
    }


def links_messages(title: str, summary: str, facts: list[str], candidates: list[str]) -> list[dict]:
    return [
        {"role": "system", "content": load("ingest-links")},
        {"role": "user", "content": (
            f"Note: {title}\nSummary: {summary}\nFacts:\n- " + "\n- ".join(facts[:6]) +
            "\n\nOther note titles:\n- " + "\n- ".join(candidates))},
    ]


def same_subject_messages(title: str, summary: str, candidates: dict[str, str]) -> list[dict]:
    listing = "\n".join(f"- {t}: {d}" for t, d in candidates.items())
    return [
        {"role": "system", "content": (
            "You deduplicate notes in a course wiki. Decide whether a proposed new note is about the SAME "
            "subject as one of the existing notes (same thing under a different name, e.g. 'Immigrant Founders' "
            "and 'Immigration in Silicon Valley'). A narrower or related subject is NOT the same subject "
            "(e.g. 'Fred Terman' is not 'Stanford Research Park'). Answer with the existing title, or NEW.")},
        {"role": "user", "content": f"Proposed note: {title}: {summary}\n\nExisting notes:\n{listing}"},
    ]


def same_subject_schema(titles: list[str]) -> dict:
    return {"type": "object", "properties": {"match": {"type": "string", "enum": titles + ["NEW"]}},
            "required": ["match"]}
