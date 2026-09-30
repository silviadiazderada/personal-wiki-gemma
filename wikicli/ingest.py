"""Ingestion: original sources -> Gemma -> reviewed, linked Obsidian notes -> retrieval index.

Pipeline for `wiki ingest vault/raw`:
  1. Read each source into slide passages (sources.py). Hash the file.
  2. Unchanged hash + already ingested -> skip the model (unless --force).
  3. Gemma extracts 4-8 topics per source as JSON (title, category, summary, facts + slide numbers).
  4. The harness validates everything the model returns: titles become short readable
     filenames, slide numbers must exist, and each topic is matched to an existing note by
     a normalised key, so re-ingesting UPDATES notes instead of creating duplicates.
  5. Gemma picks related notes for changed notes (constrained to real titles, so no broken links).
  6. Notes, one session note per source, index.md and Source Catalog.md are rendered.
     Notes marked `reviewed: true` by a human are never overwritten.
  7. The retrieval index is rebuilt from original passages + wiki notes.

Machine state (data/wiki_state.json, data/source_catalog.json) lives outside the vault.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Callable

from . import prompts
from .config import CATALOG_JSON, CATALOG_MD, INDEX_MD, RAW, STATE_FILE, VAULT, WIKI, Settings
from .evidence import log_run, memory_snapshot
from .llm import LocalGemma, parse_json
from .retrieval import build_index
from .sources import Passage, discover, load_source, sha256, slugify

FOLDERS = {"Concepts": "Concepts", "People": "People", "Organizations": "Organizations",
           "Policies and Events": "Policies and Events", "Course Logistics": "Course"}
SMALL_WORDS = {"a", "an", "and", "as", "at", "by", "for", "in", "of", "on", "or", "the", "to", "vs"}
BAD_TITLE = re.compile(r"\b(week|slide|section|reflection|prompt|today|agenda|summary)\b|\?|^\d+$", re.I)


# ---- title hygiene ------------------------------------------------------------------

def clean_title(raw: str) -> str | None:
    """Turn a model-proposed title into a short, readable, filesystem-safe note name, or reject it."""
    t = re.sub(r"[\[\]#^|\\/:*?\"<>]", " ", raw)
    t = re.sub(r"\s*\(.*?\)\s*", " ", t)          # drop parentheticals: "SBIC (1958)" -> "SBIC"
    t = re.sub(r"\s+", " ", t).strip(" .,-–—'\"")
    words = t.split()
    if not 1 <= len(words) <= 6 or BAD_TITLE.search(t):
        return None
    out = []
    for i, w in enumerate(words):
        if w.isupper() or any(c.isupper() for c in w[1:]):      # keep acronyms / camel case: SBIC, iPhone
            out.append(w)
        elif i and w.lower() in SMALL_WORDS:
            out.append(w.lower())
        else:
            out.append(w[0].upper() + w[1:])
    return " ".join(out)


def title_key(title: str) -> str:
    """Normalised identity used to merge topics: case, 'the', plurals and punctuation ignored."""
    words = [w for w in re.findall(r"[a-z0-9]+", title.lower()) if w != "the"]
    return " ".join(w[:-1] if len(w) > 3 and w.endswith("s") and not w.endswith("ss") else w for w in words)


# ---- state --------------------------------------------------------------------------

def load_json(path: Path, default):
    return json.loads(path.read_text()) if path.exists() else default


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def note_path(note: dict) -> Path:
    return WIKI / FOLDERS.get(note["category"], "Concepts") / f"{note['title']}.md"


def is_reviewed(path: Path) -> bool:
    return path.exists() and re.search(r"^reviewed:\s*true\s*$", path.read_text(), re.M) is not None


# ---- model steps --------------------------------------------------------------------

def extract_topics(llm: LocalGemma, s: Settings, label: str, passages: list[Passage]) -> tuple[dict, float]:
    msgs = prompts.topics_messages(label, [p.to_dict() for p in passages])
    r = llm.chat(msgs, schema=prompts.TOPICS_SCHEMA, num_ctx=s.ingest_num_ctx, temperature=0)
    return parse_json(r.text), r.seconds


def pick_links(llm: LocalGemma, s: Settings, note: dict, candidates: list[str]) -> list[dict]:
    facts = [f["text"] for fs in note["facts"].values() for f in fs]
    summary = next(iter(note["summaries"].values()), "")
    r = llm.chat(prompts.links_messages(note["title"], summary, facts, candidates),
                 schema=prompts.links_schema(candidates), num_ctx=s.num_ctx, temperature=0)
    seen, out = set(), []
    for item in parse_json(r.text).get("related", []):
        if item.get("connection") != "direct":
            continue          # keep only links the model itself rates as a direct connection
        if item.get("title") in candidates and item["title"] not in seen and item["title"] != note["title"]:
            seen.add(item["title"])
            out.append({"title": item["title"], "reason": item.get("reason", "").strip()})
    return out[:3]


SIMILAR = 0.6   # embedding cosine above which an existing note is a merge candidate


def find_same_subject(llm: LocalGemma, s: Settings, title: str, summary: str, notes: dict,
                      vec_cache: dict) -> str | None:
    """Embedding prefilter + Gemma judge. Returns the key of an existing note on the same subject."""
    import numpy as np
    if not notes or not llm.embeddings_available():
        return None
    def vec(text):
        if text not in vec_cache:
            v = np.array(llm.embed([text])[0]); vec_cache[text] = v / (np.linalg.norm(v) + 1e-9)
        return vec_cache[text]
    new = vec(f"{title}: {summary}")
    scored = []
    for key, n in notes.items():
        desc = next(iter(n["summaries"].values()), "")
        scored.append((float(new @ vec(f"{n['title']}: {desc}")), key))
    candidates = [k for sim, k in sorted(scored, reverse=True)[:4] if sim >= SIMILAR]
    if not candidates:
        return None
    listing = {notes[k]["title"]: next(iter(notes[k]["summaries"].values()), "") for k in candidates}
    r = llm.chat(prompts.same_subject_messages(title, summary, listing),
                 schema=prompts.same_subject_schema(list(listing)), temperature=0)
    match = parse_json(r.text).get("match")
    return next((k for k in candidates if notes[k]["title"] == match), None)


# ---- rendering ----------------------------------------------------------------------

def src_link(catalog: dict, sid: str, slides: list[int] | None = None) -> str:
    c = catalog[sid]
    where = ""
    if slides:
        where = ", slide " + ", ".join(str(n) for n in slides) if len(slides) == 1 else \
                ", slides " + ", ".join(str(n) for n in slides)
    return f"[[{c['path']}|{c['label']}]]{where}"


def render_note(note: dict, catalog: dict, model: str) -> str:
    sids = [sid for sid in note["facts"] if sid in catalog]
    summary = " ".join(note["summaries"][sid] for sid in sids if note["summaries"].get(sid))
    lines = ["---",
             f"id: {note['id']}",
             f"type: {note['category'].lower()}",
             "sources:"] + [f"  - \"{catalog[sid]['path']}\"" for sid in sids] + [
             f"source_ids: [{', '.join(sids)}]",
             f"generated_by: {model}",
             f"updated: {time.strftime('%Y-%m-%d')}",
             "reviewed: false",
             "---",
             f"# {note['title']}", "", summary, "", "## Key points"]
    for sid in sids:
        for f in note["facts"][sid]:
            lines.append(f"- {f['text']} ({src_link(catalog, sid, f['slides'])})")
    if note.get("links"):
        lines += ["", "## Related notes"]
        lines += [f"- [[{l['title']}]]: {l['reason']}" for l in note["links"]]
    sessions = sorted({catalog[sid]["label"] for sid in sids})
    lines += ["", "## Sources"]
    lines += [f"- Original slides: [[{catalog[sid]['path']}|{catalog[sid]['filename']}]] · session note: "
              f"[[{catalog[sid]['label']}]]" for sid in sids]
    return "\n".join(lines).rstrip() + "\n"


def render_session(sid: str, c: dict, notes: dict, model: str) -> str:
    topics = sorted((n for n in notes.values() if sid in reviewed_view(n)[1]), key=lambda n: n["title"])
    lines = ["---", f"id: session-{sid}", "type: session", f"source: \"{c['path']}\"",
             f"source_id: {sid}", f"original_filename: \"{c['filename']}\"", f"sha256: {c['sha256'][:16]}",
             f"generated_by: {model}", "reviewed: false", "---", f"# {c['label']}", "", c.get("summary", ""), "",
             "## Topics covered"]
    lines += [f"- [[{n['title']}]]: {n['summaries'].get(sid) or reviewed_view(n)[0]}" for n in topics]
    lines += ["", "## Original source", f"- [[{c['path']}|{c['filename']}]] ({c['units']} slides)"]
    return "\n".join(lines) + "\n"


def reviewed_view(n: dict) -> tuple[str, list[str]]:
    """Summary and source ids for a note, taken from the human-reviewed file when there is one,
    so the index and catalog show the corrected text rather than the model's first draft."""
    path = note_path(n)
    summary = next((v for v in n["summaries"].values() if v), "")
    sids = list(n["facts"])
    if is_reviewed(path):
        text = path.read_text()
        m = re.search(r"^# .*\n\n(.+?)\n", text, re.M)
        if m:
            summary = m.group(1).strip()
        ids = re.search(r"^source_ids: \[(.*)\]$", text, re.M)
        if ids:
            sids = [x.strip() for x in ids.group(1).split(",") if x.strip()]
    return summary, sids


def render_index(notes: dict, catalog: dict) -> str:
    lines = ["# POLECON 156 Course Wiki", "",
             "Personal course memory for **POLECON 156: Silicon Valley & the Global Economy** (UC Berkeley, "
             "Fall 2026), built from Silvia's discussion-section slides. Notes are generated by local Gemma, "
             "reviewed, and linked back to the original slides in `raw/`. See [[Source Catalog]] for every source.",
             "", "## Sessions", ""]
    for sid, c in sorted(catalog.items(), key=lambda kv: kv[1]["label"]):
        lines.append(f"- [[{c['label']}]]: {c.get('summary', '').split('. ')[0].rstrip('.')}.")
    for cat, folder in FOLDERS.items():
        group = sorted((n for n in notes.values() if n["category"] == cat), key=lambda n: n["title"])
        if not group:
            continue
        lines += ["", f"## {folder if folder != 'Course' else 'Course Logistics'}", ""]
        for n in group:
            first = reviewed_view(n)[0]
            lines.append(f"- [[{n['title']}]]: {first.split('. ')[0].rstrip('.')}.")
    return "\n".join(lines) + "\n"


def render_catalog(catalog: dict, notes: dict) -> str:
    lines = ["# Source Catalog", "",
             "Every original source in `raw/`, its stable source ID, and the wiki notes built from it. "
             "Originals are never edited by the harness.", "",
             "| Source ID | Session note | Original file | Slides | SHA-256 | Notes built from it |",
             "|---|---|---|---|---|---|"]
    for sid, c in sorted(catalog.items(), key=lambda kv: kv[1]["label"]):
        derived = sorted(n["title"] for n in notes.values() if sid in reviewed_view(n)[1])
        lines.append(f"| `{sid}` | [[{c['label']}]] | [[{c['path']}\\|{c['filename']}]] | {c['units']} | "
                     f"`{c['sha256'][:12]}` | " + ", ".join(f"[[{t}]]" for t in derived) + " |")
    notes_md = [c.get("note") for c in catalog.values() if c.get("note")]
    if notes_md:
        lines += ["", "## Notes on sources", ""] + [f"- {n}" for n in notes_md]
    return "\n".join(lines) + "\n"


def write_if_changed(path: Path, text: str) -> bool:
    """Write unless unchanged. Ignores the `updated:` date so re-runs don't churn files."""
    strip = lambda t: re.sub(r"^updated: .*$", "", t, flags=re.M)
    if path.exists() and strip(path.read_text()) == strip(text):
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return True


# ---- wiki notes as retrieval passages -----------------------------------------------

def wiki_passages() -> list[dict]:
    out = []
    for path in sorted(WIKI.rglob("*.md")):
        text = re.sub(r"^---.*?---\n", "", path.read_text(), flags=re.S)
        text = re.sub(r"\[\[([^\]|]+\|)?([^\]]+)\]\]", r"\2", text)   # [[a|b]] -> b for readability
        rel = path.relative_to(VAULT).as_posix()
        out.append(Passage(f"wiki:{slugify(path.stem)}", "wiki", "wiki", path.stem, rel, "wiki note", 0,
                           path.stem, text.strip()[:2500]).to_dict())
    return out


# ---- main entry point ---------------------------------------------------------------

SOURCE_NOTES = {
    "week-3-section": "Slides 4-5 of the original deck (team rosters with student names) were removed before "
                      "adding it to this public repo (student privacy / FERPA). Slide numbers here refer to "
                      "the redacted file.",
}


def ingest(target: Path, settings: Settings, model: str | None = None, force: bool = False,
           progress: Callable[[str], None] = print) -> dict:
    t_start = time.perf_counter()
    llm = LocalGemma(settings, model)
    llm.check()
    files = discover(target)
    if not files:
        raise FileNotFoundError(f"No supported sources found in {target}")
    for f in files:
        if RAW.resolve() not in f.resolve().parents:
            raise ValueError(f"{f} is outside vault/raw/. Copy originals into vault/raw/ first so "
                             "citations stay traceable.")

    state = load_json(STATE_FILE, {"notes": {}, "aliases": {}})
    state.setdefault("aliases", {})
    notes: dict = state["notes"]
    catalog: dict = load_json(CATALOG_JSON, {})
    report = {"sources": [], "created": [], "updated": [], "skipped_sources": [], "rejected_titles": [],
              "kept_reviewed": [], "removed": [], "model_seconds": 0.0}
    touched: set[str] = set()
    vec_cache: dict = {}
    all_passages: dict[str, list[Passage]] = {}

    for f in discover(RAW):   # the index always covers every raw source, not just the target
        ps = load_source(f, settings.max_passage_words)
        all_passages[ps[0].source_id] = ps

    for f in files:
        passages = load_source(f, settings.max_passage_words)
        sid, label = passages[0].source_id, passages[0].label
        digest = sha256(f)
        slide_numbers = {p.number for p in passages}
        report["sources"].append(sid)
        if not force and catalog.get(sid, {}).get("sha256") == digest:
            report["skipped_sources"].append(sid)
            progress(f"  = {label}: unchanged since last ingest, skipping the model")
            continue

        progress(f"  → {label}: {len(passages)} passages, asking {llm.model} for topics…")
        # One passage per slide for the prompt (split parts re-joined), to keep slide numbers clean.
        by_slide: dict[int, Passage] = {}
        for p in passages:
            if p.number in by_slide:
                by_slide[p.number].text += "\n" + p.text.split("\n", 1)[-1]
            else:
                by_slide[p.number] = Passage(**p.to_dict())
        data, secs = extract_topics(llm, settings, label, list(by_slide.values()))
        report["model_seconds"] += secs

        # Remove this source's previous contributions: re-ingest replaces, never duplicates.
        for key, n in notes.items():
            if sid in n["facts"]:
                n["facts"].pop(sid, None)
                n["summaries"].pop(sid, None)
                touched.add(key)

        for topic in data.get("topics", []):
            title = clean_title(topic.get("title", ""))
            if not title:
                report["rejected_titles"].append(topic.get("title", ""))
                continue
            facts = []
            for fact in topic.get("facts", []):
                slides = sorted({n for n in fact.get("slides", []) if n in slide_numbers})
                if slides and fact.get("text", "").strip():
                    facts.append({"text": fact["text"].strip(), "slides": slides})
            if not facts:
                report["rejected_titles"].append(f"{title} (no facts with valid slide numbers)")
                continue
            key = title_key(title)
            key = state["aliases"].get(key, key)     # a human merge/rename decided this before
            if key not in notes:
                # Only compare against notes from OTHER sources: topics within one source are distinct.
                others = {k: n for k, n in notes.items() if set(n["facts"]) - {sid}}
                same = find_same_subject(llm, settings, title, topic.get("summary", ""), others, vec_cache)
                if same:
                    report.setdefault("merged", []).append(f"{title} → {notes[same]['title']}")
                    state["aliases"][key] = same       # remember the decision for future re-ingests
                    key = same
            if key not in notes:
                category = topic.get("category") if topic.get("category") in FOLDERS else "Concepts"
                notes[key] = {"id": slugify(title), "title": title, "category": category,
                              "summaries": {}, "facts": {}, "links": []}
                report["created"].append(title)
            elif notes[key]["title"] not in report["updated"]:
                report["updated"].append(notes[key]["title"])
            notes[key]["summaries"][sid] = topic.get("summary", "").strip()
            notes[key]["facts"].setdefault(sid, []).extend(facts)
            notes[key]["model"] = llm.model
            touched.add(key)

        catalog[sid] = {"label": label, "path": passages[0].path, "filename": f.name, "sha256": digest,
                        "units": max(slide_numbers), "summary": data.get("source_summary", "").strip(),
                        "ingested_at": time.strftime("%Y-%m-%d %H:%M:%S"), "model": llm.model,
                        "note": SOURCE_NOTES.get(sid, "")}

    # Drop notes that lost all their facts (e.g. a topic the model no longer extracts).
    for key in [k for k, n in notes.items() if not n["facts"]]:
        path = note_path(notes[key])
        if not is_reviewed(path):
            if path.exists():
                path.unlink()
            report["removed"].append(notes.pop(key)["title"])

    # Links: only for notes whose content changed; constrained to existing titles.
    titles = sorted(n["title"] for n in notes.values())
    for key in sorted(touched):
        if key in notes:
            progress(f"  ↔ linking {notes[key]['title']}")
            notes[key]["links"] = pick_links(llm, settings, notes[key], [t for t in titles if t != notes[key]["title"]])
    for n in notes.values():                     # drop links to notes that no longer exist
        n["links"] = [l for l in n.get("links", []) if l["title"] in titles]

    written, manifest = publish(state, catalog, settings, llm.model, report, all_passages, progress)

    report.update({"notes_total": len(notes), "files_written": written, "index": manifest,
                   "model": llm.model, "seconds_total": round(time.perf_counter() - t_start, 1),
                   "model_seconds": round(report["model_seconds"], 1), "memory": memory_snapshot(llm)})
    log_run({"command": "ingest", "target": str(target), **{k: v for k, v in report.items() if k != "index"}})
    return report


def publish(state: dict, catalog: dict, settings: Settings, model: str, report: dict,
            all_passages: dict | None = None, progress: Callable[[str], None] = print) -> tuple[int, dict]:
    """Render notes, session notes, index and catalog from state, then rebuild the retrieval index."""
    notes = state["notes"]
    report.setdefault("kept_reviewed", [])
    report.setdefault("removed", [])
    if all_passages is None:
        all_passages = {}
        for f in discover(RAW):
            ps = load_source(f, settings.max_passage_words)
            all_passages[ps[0].source_id] = ps
    # Render. Reviewed notes are preserved exactly as the human left them.
    written = 0
    expected_files = set()
    for n in notes.values():
        path = note_path(n)
        expected_files.add(path.resolve())
        if is_reviewed(path):
            report["kept_reviewed"].append(n["title"])
            continue
        written += write_if_changed(path, render_note(n, catalog, n.get("model", model)))
    for sid, c in catalog.items():
        path = WIKI / "Sessions" / f"{c['label']}.md"
        expected_files.add(path.resolve())
        if not is_reviewed(path):
            written += write_if_changed(path, render_session(sid, c, notes, c.get("model", model)))
    # Remove stale generated notes (e.g. a renamed title); never touch reviewed or hand-written files.
    for path in WIKI.rglob("*.md"):
        if path.resolve() not in expected_files and "generated_by:" in path.read_text() and not is_reviewed(path):
            path.unlink()
            report["removed"].append(path.stem)
    write_if_changed(INDEX_MD, render_index(notes, catalog))
    write_if_changed(CATALOG_MD, render_catalog(catalog, notes))
    save_json(STATE_FILE, state)
    save_json(CATALOG_JSON, catalog)

    progress("  ⌕ rebuilding retrieval index (sources + wiki notes)…")
    source_passages = [p.to_dict() for ps in all_passages.values() for p in ps]
    return written, build_index(source_passages + wiki_passages(), settings)


# ---- human cleanup: merge / rename (no model calls) ---------------------------------

def _find(notes: dict, title: str) -> str:
    key = title_key(title)
    if key not in notes:
        raise ValueError(f"No note titled '{title}'. Existing: {', '.join(sorted(n['title'] for n in notes.values()))}")
    return key


def _relink_files(old: str, new: str) -> None:
    """Update incoming links in every note on disk, including reviewed ones."""
    for path in list(WIKI.rglob("*.md")) + [INDEX_MD]:
        if path.exists():
            text = path.read_text()
            updated = text.replace(f"[[{old}]]", f"[[{new}]]").replace(f"[[{old}|", f"[[{new}|")
            if updated != text:
                path.write_text(updated)


def merge_notes(src_title: str, dst_title: str, settings: Settings) -> dict:
    state = load_json(STATE_FILE, {"notes": {}, "aliases": {}})
    state.setdefault("aliases", {})
    notes, catalog = state["notes"], load_json(CATALOG_JSON, {})
    src, dst = _find(notes, src_title), _find(notes, dst_title)
    if src == dst:
        raise ValueError("Source and target are the same note.")
    a, b = notes[src], notes[dst]
    for sid, facts in a["facts"].items():
        b["facts"].setdefault(sid, []).extend(facts)
        if a["summaries"].get(sid) and not b["summaries"].get(sid):
            b["summaries"][sid] = a["summaries"][sid]
    have = {l["title"] for l in b["links"]}
    b["links"] += [l for l in a["links"] if l["title"] not in have and l["title"] != b["title"]]
    for n in notes.values():
        for l in n["links"]:
            if l["title"] == a["title"]:
                l["title"] = b["title"]
        seen, uniq = set(), []
        for l in n["links"]:
            if l["title"] not in seen and l["title"] != n["title"]:
                seen.add(l["title"]); uniq.append(l)
        n["links"] = uniq
    old_path = note_path(a)
    del notes[src]
    state["aliases"] = {k: (dst if v == src else v) for k, v in state["aliases"].items()}
    state["aliases"][src] = dst
    if old_path.exists():
        old_path.unlink()
    _relink_files(a["title"], b["title"])
    report = {"merged": [f"{a['title']} → {b['title']}"]}
    publish(state, catalog, settings, b.get("model", "human edit"), report, progress=lambda m: None)
    return report


def rename_note(old_title: str, new_title: str, settings: Settings, category: str | None = None) -> dict:
    state = load_json(STATE_FILE, {"notes": {}, "aliases": {}})
    state.setdefault("aliases", {})
    notes, catalog = state["notes"], load_json(CATALOG_JSON, {})
    old = _find(notes, old_title)
    clean = clean_title(new_title)
    if not clean:
        raise ValueError(f"'{new_title}' is not a valid note name (1-6 words, no dates, questions or week numbers).")
    new = title_key(clean)
    if new in notes and new != old:
        raise ValueError(f"A note called '{notes[new]['title']}' already exists. Use `wiki merge` instead.")
    note = notes.pop(old)
    old_name, old_path = note["title"], note_path(note)
    note["title"], note["id"] = clean, slugify(clean)
    if category:
        if category not in FOLDERS:
            raise ValueError(f"Category must be one of: {', '.join(FOLDERS)}")
        note["category"] = category
    notes[new] = note
    for n in notes.values():
        for l in n["links"]:
            if l["title"] == old_name:
                l["title"] = clean
    state["aliases"] = {k: (new if v == old else v) for k, v in state["aliases"].items()}
    if old != new:
        state["aliases"][old] = new
    new_path = note_path(note)
    if old_path.exists() and is_reviewed(old_path):     # keep human edits: move the file, fix its heading
        new_path.parent.mkdir(parents=True, exist_ok=True)
        text = old_path.read_text().replace(f"# {old_name}\n", f"# {clean}\n", 1)
        old_path.unlink()
        new_path.write_text(text)
    elif old_path.exists():
        old_path.unlink()
    _relink_files(old_name, clean)
    report = {"renamed": [f"{old_name} → {clean}"]}
    publish(state, catalog, settings, note.get("model", "human edit"), report, progress=lambda m: None)
    return report
