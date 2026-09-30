"""Citation checks. A citation is not proof, so the harness checks each claim:

1. valid:    every cited number points to a passage that was actually retrieved
2. numbers:  every number in the claim (years, $, %) appears in the cited passages
3. overlap:  share of the claim's content words found in the cited passages

A claim is "supported" if 1 and 2 hold and overlap >= 0.5, "weak" if 1 and 2 hold but
overlap is lower, and "unsupported" otherwise. If an answer has no supported or weak
claims, the harness reports insufficient evidence instead of showing it as an answer.
These are heuristics that flag problems; the final judgement is a human reading the
cited passage (recorded in each evidence card).
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

from .retrieval import tokenize

NUM = re.compile(r"\d[\d,.]*")
OVERLAP_OK = 0.5


def numbers(text: str) -> set[str]:
    return {n.rstrip(".,").replace(",", "") for n in NUM.findall(text)}


@dataclass
class ClaimCheck:
    text: str
    citations: list[int]
    invalid_citations: list[int] = field(default_factory=list)
    missing_numbers: list[str] = field(default_factory=list)
    overlap: float = 0.0
    verdict: str = "unsupported"


CITE_MARK = re.compile(r"\s*\[\d+(?:\s*,\s*\d+)*\]")


def check_claim(text: str, cites: list[int], passages: list[dict]) -> ClaimCheck:
    # Models sometimes also write "[1]" inside the claim text. Fold those markers into the
    # citation list and strip them, so "1" is not mistaken for a factual number.
    inline = [int(n) for m in CITE_MARK.findall(text) for n in re.findall(r"\d+", m)]
    text = CITE_MARK.sub("", text).strip()
    c = ClaimCheck(text, sorted(set(cites) | set(inline)))
    valid = [n for n in c.citations if 1 <= n <= len(passages)]
    c.invalid_citations = [n for n in c.citations if n not in valid]
    if not valid:
        return c
    evidence = " ".join(passages[n - 1]["text"] for n in valid)
    c.missing_numbers = sorted(numbers(text) - numbers(evidence))
    words = set(tokenize(text))
    ev_words = set(tokenize(evidence))
    c.overlap = round(len(words & ev_words) / len(words), 2) if words else 0.0
    if not c.invalid_citations and not c.missing_numbers:
        c.verdict = "supported" if c.overlap >= OVERLAP_OK else "weak"
    return c


@dataclass
class Verification:
    status: str                       # final status after checks
    model_status: str                 # what the model itself said
    claims: list[ClaimCheck]
    downgraded: bool = False
    reason: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def verify_answer(result: dict, passages: list[dict]) -> Verification:
    model_status = result.get("status", "insufficient_evidence")
    claims = [check_claim(c.get("text", ""), c.get("citations", []), passages)
              for c in result.get("claims", []) if c.get("text", "").strip()]
    v = Verification(model_status, model_status, claims)
    if model_status == "answered":
        usable = [c for c in claims if c.verdict in ("supported", "weak")]
        if not usable:
            v.status, v.downgraded = "insufficient_evidence", True
            v.reason = "The model answered, but no claim passed the citation checks."
    elif claims:
        v.reason = "The model reported insufficient evidence; any partial claims are shown with their checks."
    return v


def chat_citation_issues(text: str, n_passages: int) -> list[int]:
    """Citation numbers in a chat reply that do not match a retrieved note."""
    cited = {int(x) for group in re.findall(r"\[([\d,\s]+)\]", text) for x in re.findall(r"\d+", group)}
    return sorted(n for n in cited if not 1 <= n <= n_passages)
