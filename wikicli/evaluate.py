"""Evaluation: fixed ask-mode tests, chat/search mode checks and a device benchmark.

Every run writes evidence cards (Markdown for people, JSON for machines) to evidence/.
Automatic checks are recorded next to a human-review field; they flag problems but the
final assessment comes from opening the cited passage.
"""
from __future__ import annotations

import json
import threading
import time

import psutil
import yaml

from .config import EVIDENCE, TESTS, load_settings
from .evidence import device_specs, memory_snapshot, network_status, passages_md, save_card
from .harness import ChatSession, Harness


def _match(hit_id: str, expected: str) -> bool:
    return hit_id == expected or hit_id.startswith(expected + ".")


def auto_assess(r, test: dict | None) -> dict:
    if not test:
        return {}
    ids = [h["passage"]["id"] for h in r.hits]
    exp = test.get("expected_passages", [])
    ranks = {e: next((i for i, x in enumerate(ids, 1) if _match(x, e)), None) for e in exp}
    cited_ids = {r.hits[n - 1]["passage"]["id"] for c in r.verification.claims for n in c.citations
                 if 1 <= n <= len(r.hits)}
    return {
        "retrieval_found_expected": all(ranks.values()) if exp else None,
        "expected_passage_ranks": ranks,
        "behavior_expected": test["expected_behavior"],
        "behavior_actual": r.status,
        "behavior_ok": r.status == test["expected_behavior"],
        "cites_expected_passage": any(_match(c, e) for c in cited_ids for e in exp) if exp else None,
        "all_claims_supported": all(c.verdict == "supported" for c in r.verification.claims)
        if r.status == "answered" else None,
    }


def ask_card(folder: str, name: str, r, test: dict | None):
    v = r.verification
    a = auto_assess(r, test)
    lines = [f"# {test['id'] if test else 'Ask'}: {r.question}", ""]
    lines += ["| | |", "|---|---|",
              f"| Mode | ask · **{r.mode}** execution |",
              f"| Model | `{r.model}` |",
              f"| Network during run | **{r.network}** |",
              f"| Retrieval | {r.retrieval_method} ({r.seconds_retrieval}s) |",
              f"| Model time | {r.seconds_model}s |",
              f"| Memory | {json.dumps(r.memory)} |"]
    if test:
        lines += ["", "## Expected (written before the run)", "",
                  f"- Test type: {test['kind']}",
                  f"- Expected behavior: `{test['expected_behavior']}`",
                  f"- Expected passages: {', '.join('`'+e+'`' for e in test['expected_passages']) or 'none'}",
                  f"- Expected answer: {test['expected_answer'].strip()}"]
    lines += ["", "## Retrieved passages (what Gemma was shown)", "", passages_md(r.hits)]
    lines += ["", "## Gemma's answer", ""]
    if v.status == "answered":
        for c in v.claims:
            lines.append(f"- {c.text} {''.join(f'[{n}]' for n in c.citations)}")
    else:
        lines.append("**Insufficient evidence.** " + (v.reason or ""))
    lines += ["", "## Citation checks (automatic)", "",
              "| Claim | Cites | Numbers missing from cited text | Word overlap | Verdict |", "|---|---|---|---|---|"]
    for c in v.claims:
        lines.append(f"| {c.text[:90]}… | {c.citations} | {', '.join(c.missing_numbers) or '—'} | "
                     f"{c.overlap} | {c.verdict} |")
    if v.downgraded:
        lines.append(f"\n> Downgraded to insufficient evidence: {v.reason}")
    if a:
        lines += ["", "## Automatic assessment", "", "```json", json.dumps(a, indent=2), "```"]
    lines += ["", "## Human review", "", "_Pending: open each cited slide and confirm it supports the claim._",
              "", "<details><summary>Raw model output</summary>", "", "```json", r.raw_output, "```", "</details>"]
    data = {"test": test, "result": r.to_dict(), "auto_assessment": a}
    return save_card(folder, name, "\n".join(lines) + "\n", data)


def run_tests(h: Harness, console, label: str = "") -> list[dict]:
    tests = yaml.safe_load((TESTS / "questions.yaml").read_text())
    folder = "ask-tests" + (f"-{label}" if label else "")
    summary = []
    for t in tests:
        console.print(f"[bold]{t['id']}[/bold] {t['question']}")
        r = h.ask(t["question"])           # fresh call: no chat history, no persona
        path = ask_card(folder, t["id"], r, t)
        a = auto_assess(r, t)
        summary.append({"id": t["id"], **a, "seconds_model": r.seconds_model, "card": str(path.name)})
        console.print(f"  → {r.status} · retrieval ok: {a['retrieval_found_expected']} · "
                      f"behavior ok: {a['behavior_ok']} · {r.seconds_model}s · saved {folder}/{path.name}")
    rows = ["| Test | Retrieval found expected | Behavior | Cites expected | All claims supported | Model s |",
            "|---|---|---|---|---|---|"]
    for s in summary:
        rows.append(f"| [{s['id']}]({s['id']}.md) | {s['retrieval_found_expected']} | "
                    f"{s['behavior_actual']} ({'ok' if s['behavior_ok'] else 'MISMATCH'}) | "
                    f"{s['cites_expected_passage']} | {s['all_claims_supported']} | {s['seconds_model']} |")
    (EVIDENCE / folder / "README.md").write_text(
        f"# Ask-mode tests ({h.llm.model}, {h.llm.backend}, network {network_status()}, "
        f"{time.strftime('%Y-%m-%d %H:%M')})\n\n" + "\n".join(rows) + "\n")
    return summary


def run_checks(h: Harness, console, label: str = "") -> dict:
    """Mode-boundary checks from the assignment, recorded as a transcript."""
    log, results = [], {}
    session = ChatSession(h)

    def say(msg):
        console.print(f"[cyan]you ›[/cyan] {msg}")
        reply, meta = "", {}
        for piece in session.turn(msg):
            if isinstance(piece, str):
                reply += piece
            else:
                meta = piece
        console.print(f"[magenta]sol ›[/magenta] {reply}\n[dim]{meta.get('route_reason')} · "
                      f"retrieved={meta.get('retrieved')}[/dim]")
        log.append({"mode": "chat", "user": msg, "assistant": reply, "meta": meta})
        return reply, meta

    def words(t):
        return len(t.split())

    # 1-2: capability questions: no notes search, no citations, no refusal
    for q in ("what can we do?", "what can you help me with?"):
        reply, meta = say(q)
        results[q] = {"no_retrieval": not meta["retrieved"],
                      "no_insufficient_evidence": "insufficient evidence" not in reply.lower(),
                      "no_citations": "[" not in reply}

    # 3: draft, then a conversational follow-up
    draft, m1 = say("Draft a short plan for my 50-minute midterm review section.")
    short, m2 = say("make that shorter")
    results["follow-up"] = {"draft_words": words(draft), "shorter_words": words(short),
                            "is_shorter": words(short) < words(draft),
                            "follow_up_skipped_retrieval": not m2["retrieved"]}

    # 4: a false claim made only in chat must not become evidence in ask
    say("Just so you know, Stanford Research Park was founded in 1975.")
    console.print("[bold]search[/bold] Stanford Research Park")
    hits, method = h.search("Stanford Research Park", k=5, kinds=("source",))
    log.append({"mode": "search", "query": "Stanford Research Park", "method": method,
                "passages": [{"id": x.id, "citation": f"{x.passage['label']}, {x.passage['locator']}",
                              "text": x.passage["text"]} for x in hits]})
    results["search"] = {"returned_passages": len(hits), "method": method, "generated_answer": False}
    r = h.ask("When was Stanford Research Park founded?")
    answer = " ".join(c.text for c in r.verification.claims)
    log.append({"mode": "ask", "question": "When was Stanford Research Park founded?", "status": r.status,
                "answer": answer, "citations": [f"{x['passage']['label']}, {x['passage']['locator']}"
                                                for x in r.hits]})
    console.print(f"[green]ask ›[/green] {answer}")
    results["ask_ignores_chat_claim"] = {"mentions_1951": "1951" in answer, "mentions_1975": "1975" in answer}

    # Transcript card
    folder = "mode-checks" + (f"-{label}" if label else "")
    md = [f"# Chat / search / ask mode checks", "",
          f"Model `{h.llm.model}` · execution **{h.llm.backend}** · network **{network_status()}** · "
          f"{time.strftime('%Y-%m-%d %H:%M')}", "", "## Automatic results", "", "```json",
          json.dumps(results, indent=2), "```", "", "## Transcript", ""]
    for e in log:
        if e["mode"] == "chat":
            meta = e["meta"]
            md += [f"**you (chat):** {e['user']}", "",
                   f"**sol:** {e['assistant']}", "",
                   f"<sub>notes lookup: {meta['retrieved']} ({meta['route_reason']})"
                   + (f"; passages: {'; '.join(meta['passages'])}" if meta["retrieved"] else "")
                   + f"; {meta['seconds']}s</sub>", ""]
        elif e["mode"] == "search":
            md += [f"**search:** `{e['query']}` ({e['method']}; no model call, no generated answer)", ""]
            md += [f"- **{p['citation']}** (`{p['id']}`): {p['text'][:220].replace(chr(10), ' ')}…"
                   for p in e["passages"]] + [""]
        else:
            md += [f"**ask (fresh, no chat history):** {e['question']}", "",
                   f"**answer ({e['status']}):** {e['answer']}", ""]
    save_card(folder, "mode-checks", "\n".join(md) + "\n", {"results": results, "transcript": log})
    console.print(f"[dim]saved evidence/{folder}/mode-checks.md[/dim]")
    return results


def run_bench(models: list[str], console) -> None:
    """Cold-load each model, run one real RAG answer, and sample memory while it runs."""
    s = load_settings()
    rows = []
    q = yaml.safe_load((TESTS / "questions.yaml").read_text())[0]["question"]
    for m in models:
        h = Harness(s, "local", m)
        h.llm.check()
        for other in h.llm.loaded_models():                 # unload everything for a clean measurement
            h.llm.http.post("/api/generate", json={"model": other["name"], "keep_alive": 0})
        time.sleep(2)
        base = psutil.virtual_memory()
        peak = {"used": base.total - base.available}
        stop = threading.Event()

        def sample():
            while not stop.is_set():
                vm = psutil.virtual_memory()
                peak["used"] = max(peak["used"], vm.total - vm.available)
                time.sleep(0.2)

        th = threading.Thread(target=sample, daemon=True)
        th.start()
        cold = h.ask(q)                                      # includes model load
        warm = h.ask(q)                                      # model already in memory
        stop.set()
        th.join()
        st = warm.model_stats or {}
        tps = (st.get("eval_count") or 0) / ((st.get("eval_duration") or 1) / 1e9)
        mem = memory_snapshot(h.llm)
        loaded = next((x for x in mem["ollama_loaded"] if x["model"] == m), {})
        rows.append({"model": m, "cold_answer_s": cold.seconds_model,
                     "load_s": round((cold.model_stats.get("load_duration") or 0) / 1e9, 2),
                     "warm_answer_s": warm.seconds_model, "tokens_per_s": round(tps, 1),
                     "prompt_tokens": st.get("prompt_eval_count"),
                     "ollama_model_memory_gb": loaded.get("size_gb"),
                     "system_mem_increase_gb": round((peak["used"] - (base.total - base.available)) / 2**30, 2),
                     "system_mem_peak_gb": round(peak["used"] / 2**30, 2),
                     "status": warm.status})
        console.print(rows[-1])
    spec = device_specs()
    md = ["# Benchmark: one RAG answer per model", "",
          f"Device: {spec}", f"Question: {q}", f"num_ctx: {s.num_ctx} · network: {network_status()} · "
          f"{time.strftime('%Y-%m-%d %H:%M')}", "",
          "| Model | Load s | Cold answer s | Warm answer s | Tokens/s | Model memory (Ollama) GB | "
          "System memory increase GB | Peak system memory GB | Status |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| `{r['model']}` | {r['load_s']} | {r['cold_answer_s']} | {r['warm_answer_s']} | "
                  f"{r['tokens_per_s']} | {r['ollama_model_memory_gb']} | {r['system_mem_increase_gb']} | "
                  f"{r['system_mem_peak_gb']} | {r['status']} |")
    path = save_card("bench", time.strftime("%Y%m%d-%H%M%S"), "\n".join(md) + "\n", {"device": spec, "rows": rows})
    console.print(f"[dim]saved {path}[/dim]")
