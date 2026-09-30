"""`wiki` command-line interface. Each command hands off to the harness; this file only
parses arguments and displays results."""
from __future__ import annotations

import time
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from .config import RAW, ROOT, load_settings
from .llm import ModelUnavailable

HELP = """
POLECON 156 personal wiki: a local Gemma + RAG CLI. Works offline after setup.

\b
Commands
  ingest   read sources in vault/raw/, generate linked wiki notes, rebuild the index
  search   show original matching passages and paths (no AI answer, no model needed)
  ask      neutral, cited answer from the sources only, or "insufficient evidence"
  chat     personal assistant (Sol) with conversation memory; looks up notes only when needed
  eval     run the fixed ask-mode tests and chat/search mode checks, save evidence cards
  bench    measure memory and response time for one or more local models
  status   show model, runtime, index and network status
  merge    fold a duplicate note into another (cleanup; survives re-ingest)
  rename   give a note a better name (cleanup; survives re-ingest)

\b
Configuration: config.toml (model, embedding model, context size, retrieval settings)
Required: Ollama running locally with the configured models pulled (see README).
Local mode is the default. `--mode online` is an optional extension (needs GEMINI_API_KEY).
"""

app = typer.Typer(help=HELP, no_args_is_help=True, add_completion=False, rich_markup_mode=None)
console = Console()


def header(mode: str, model: str) -> None:
    from .evidence import network_status
    console.print(f"[dim]model: {model} · execution: {mode} · network: {network_status()}[/dim]")


def fail(msg: str) -> None:
    console.print(Panel(msg, title="error", border_style="red"))
    raise typer.Exit(1)


def make_harness(mode: str, model: str | None):
    from .harness import Harness
    if mode not in ("local", "online"):
        fail("--mode must be 'local' or 'online'")
    return Harness(load_settings(), mode, model)


@app.command()
def ingest(path: Path = typer.Argument(RAW, help="A file or folder inside vault/raw/"),
           force: bool = typer.Option(False, "--force", help="Re-run the model even for unchanged sources"),
           model: str = typer.Option(None, help="Override the local model from config.toml")):
    """Read local sources, generate linked wiki pages, and update the index."""
    from .ingest import ingest as run_ingest
    s = load_settings()
    if not path.exists():
        fail(f"Path not found: {path}")
    header("local", model or s.model)
    try:
        r = run_ingest(path, s, model, force, progress=lambda m: console.print(m))
    except (ModelUnavailable, FileNotFoundError, ValueError) as e:
        fail(str(e))
    t = Table(title="Ingestion report", show_header=False)
    for k in ("sources", "skipped_sources", "created", "updated", "merged", "removed", "kept_reviewed",
              "rejected_titles"):
        t.add_row(k, ", ".join(map(str, r.get(k, []))) or "—")
    t.add_row("notes in wiki", str(r["notes_total"]))
    t.add_row("files written", str(r["files_written"]))
    t.add_row("index", f"{r['index']['sources']} source passages + {r['index']['wiki']} wiki notes "
                       f"(embeddings: {r['index']['embed_model'] or 'none, keyword only'})")
    t.add_row("time", f"{r['seconds_total']}s total, {r['model_seconds']}s in the model")
    console.print(t)


@app.command()
def merge(source: str = typer.Argument(..., help="Title of the duplicate note to fold in"),
          target: str = typer.Argument(..., help="Title of the note to keep")):
    """Merge a duplicate note into another; links, index and future re-ingests follow."""
    from .ingest import merge_notes
    try:
        r = merge_notes(source, target, load_settings())
    except ValueError as e:
        fail(str(e))
    console.print(f"merged: {r['merged'][0]} · index rebuilt")


@app.command()
def rename(old: str = typer.Argument(..., help="Current note title"),
           new: str = typer.Argument(..., help="New short descriptive title"),
           category: str = typer.Option(None, help="Move to another folder, e.g. 'Policies and Events'")):
    """Rename a note (file, heading, incoming links); future re-ingests keep the new name."""
    from .ingest import rename_note
    try:
        r = rename_note(old, new, load_settings(), category)
    except ValueError as e:
        fail(str(e))
    console.print(f"renamed: {r['renamed'][0]} · index rebuilt")


@app.command()
def search(query: str, k: int = typer.Option(8, "-k", help="Number of passages"),
           keyword_only: bool = typer.Option(False, "--keyword-only", help="BM25 only, no embedding model"),
           sources_only: bool = typer.Option(False, "--sources-only", help="Exclude generated wiki notes"),
           save: bool = typer.Option(False, "--save", help="Save an evidence card")):
    """Show original matching passages and source paths. Never generates an answer."""
    from .harness import Harness
    h = Harness(load_settings())
    try:
        hits, method = h.search(query, k, keyword_only, ("source",) if sources_only else ("source", "wiki"))
    except FileNotFoundError as e:
        fail(str(e))
    console.print(f"[dim]search · retrieval: {method} · no language model used[/dim]")
    if not hits:
        console.print("No matching passages.")
    for n, hit in enumerate(hits, 1):
        p = hit.passage
        tag = "source" if p["kind"] == "source" else "wiki note (generated)"
        sim = f" · cosine {hit.dense_sim:.2f}" if hit.dense_sim is not None else ""
        console.print(Panel(p["text"], title=f"[{n}] {p['label']}, {p['locator']} · {tag}",
                            subtitle=f"vault/{p['path']} · id {p['id']}{sim}", title_align="left",
                            subtitle_align="left"))
    if save:
        from .evidence import passages_md, save_card
        from .harness import hit_dict
        hd = [hit_dict(x) for x in hits]
        name = time.strftime("%Y%m%d-%H%M%S") + "-search"
        path = save_card("runs", name, f"# Search: {query}\n\nMethod: {method}\n\n{passages_md(hd)}",
                         {"query": query, "method": method, "hits": hd})
        console.print(f"[dim]saved {path.relative_to(ROOT)}[/dim]")


def render_answer(r) -> None:
    v = r.verification
    if v.status == "answered":
        body = []
        for c in v.claims:
            mark = {"supported": "", "weak": " ⚠ weak support", "unsupported": " ✗ unsupported"}[c.verdict]
            cites = "".join(f"[{n}]" for n in c.citations)
            body.append(f"- {c.text.rstrip()} {cites}{mark}")
        console.print(Panel(Markdown("\n".join(body)), title="answer", border_style="green"))
    else:
        msg = "**Insufficient evidence.** The wiki's sources do not support an answer to this question."
        if v.reason:
            msg += f"\n\n{v.reason}"
        console.print(Panel(Markdown(msg), title="answer", border_style="yellow"))
    cited = sorted({n for c in v.claims for n in c.citations if 1 <= n <= len(r.hits)})
    if v.status == "answered":
        t = Table("#", "citation", "file", "check", show_lines=False, title="citations")
        for n in cited:
            p = r.hits[n - 1]["passage"]
            ok = [c.verdict for c in v.claims if n in c.citations]
            t.add_row(str(n), f"{p['label']}, {p['locator']}", f"vault/{p['path']}", ", ".join(sorted(set(ok))))
        console.print(t)
    console.print(f"[dim]retrieval: {r.retrieval_method} ({r.seconds_retrieval}s) · model {r.model} "
                  f"({r.mode}) {r.seconds_model}s · checks: "
                  f"{sum(c.verdict == 'supported' for c in v.claims)}/{len(v.claims)} claims supported"
                  f"{' · downgraded' if v.downgraded else ''}[/dim]")


@app.command()
def ask(question: str,
        mode: str = typer.Option("local", "--mode", help="local (default, offline) or online (optional)"),
        model: str = typer.Option(None, help="Override the model"),
        show_context: bool = typer.Option(False, "--show-context", help="Print the retrieved passages"),
        save: bool = typer.Option(False, "--save", help="Save an evidence card")):
    """Standalone factual answer with citations, or 'insufficient evidence'. No chat history."""
    h = make_harness(mode, model)
    header(mode, h.llm.model)
    try:
        r = h.ask(question)
    except (ModelUnavailable, FileNotFoundError) as e:
        fail(str(e))
    if show_context:
        for n, hit in enumerate(r.hits, 1):
            p = hit["passage"]
            console.print(Panel(p["text"], title=f"[{n}] {p['label']}, {p['locator']}", title_align="left",
                                border_style="dim"))
    render_answer(r)
    if save:
        from .evaluate import ask_card
        name = time.strftime("%Y%m%d-%H%M%S") + "-ask"
        path = ask_card("runs", name, r, None)
        console.print(f"[dim]saved {path.relative_to(ROOT)}[/dim]")


@app.command()
def chat(mode: str = typer.Option("local", "--mode", help="local (default) or online"),
         model: str = typer.Option(None, help="Override the model")):
    """Personal assistant with conversation context. Retrieves notes only when useful."""
    from .harness import ChatSession
    h = make_harness(mode, model)
    try:
        h.llm.check()
    except ModelUnavailable as e:
        fail(str(e))
    header(mode, h.llm.model)
    session = ChatSession(h)
    console.print(Panel("Hi, I'm [bold]Sol[/bold], your POLECON 156 teaching assistant. Ask me anything, or "
                        "try \"what can you help me with?\"\n[dim]/notes <q> force a notes lookup · /save keep "
                        "last reply · /reset · /exit[/dim]", border_style="cyan"))
    while True:
        try:
            msg = console.input("[bold cyan]you ›[/bold cyan] ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not msg:
            continue
        if msg in ("/exit", "/quit"):
            break
        if msg == "/reset":
            session.reset()
            console.print("[dim]conversation cleared[/dim]")
            continue
        if msg.startswith("/save"):
            path = session.save_last(msg[5:].strip() or None)
            console.print(f"[dim]{'saved ' + str(path.relative_to(ROOT)) if path else 'nothing to save yet'}[/dim]")
            continue
        if msg == "/help":
            console.print("[dim]/notes <question> · /save [name] · /reset · /exit[/dim]")
            continue
        console.print("[bold magenta]sol ›[/bold magenta] ", end="")
        try:
            for piece in session.turn(msg):
                if isinstance(piece, str):
                    console.print(piece, end="", markup=False, highlight=False)
                else:
                    console.print()
                    if piece["retrieved"]:
                        console.print(f"[dim]notes used ({piece['route_reason']}; query: {piece['query']}):[/dim]")
                        for n, c in enumerate(piece["passages"], 1):
                            console.print(f"[dim]  [{n}] {c}[/dim]")
                    else:
                        console.print(f"[dim]no notes lookup ({piece['route_reason']})[/dim]")
                    if piece["invalid_citations"]:
                        console.print(f"[yellow]⚠ citations {piece['invalid_citations']} do not match any "
                                      f"retrieved note[/yellow]")
        except (ModelUnavailable, FileNotFoundError) as e:
            console.print()
            console.print(f"[red]{e}[/red]")


@app.command("eval")
def evaluate(tests: bool = typer.Option(True, "--tests/--no-tests", help="Run the ask-mode test set"),
             checks: bool = typer.Option(True, "--checks/--no-checks", help="Run chat/search mode checks"),
             mode: str = typer.Option("local", "--mode"),
             model: str = typer.Option(None, help="Override the model"),
             label: str = typer.Option("", help="Suffix for the evidence folder, e.g. 'e4b'")):
    """Run the fixed test set and mode checks; write evidence cards to evidence/."""
    from .evaluate import run_checks, run_tests
    h = make_harness(mode, model)
    header(mode, h.llm.model)
    try:
        h.llm.check()
        if tests:
            run_tests(h, console, label)
        if checks:
            run_checks(h, console, label)
    except (ModelUnavailable, FileNotFoundError) as e:
        fail(str(e))


@app.command()
def bench(models: list[str] = typer.Argument(None, help="Models to measure (default: config model)")):
    """Measure load time, memory and response time for a RAG answer on this device."""
    from .evaluate import run_bench
    s = load_settings()
    try:
        run_bench(models or [s.model], console)
    except (ModelUnavailable, FileNotFoundError) as e:
        fail(str(e))


@app.command()
def status():
    """Show model, runtime, index and network status."""
    import json
    from .config import INDEX_DIR
    from .evidence import device_specs, network_status
    from .llm import LocalGemma
    s = load_settings()
    llm = LocalGemma(s)
    t = Table(show_header=False, title="status")
    t.add_row("runtime", f"Ollama {llm.runtime_version() or 'NOT RUNNING'} at {s.runtime_url}")
    installed = llm.installed_models()
    for m in (s.model, s.embed_model):
        t.add_row("model", f"{m} {'✓ downloaded' if m in installed else '✗ missing: ollama pull ' + m}")
    man = INDEX_DIR / "manifest.json"
    t.add_row("index", json.loads(man.read_text()).__repr__() if man.exists() else "none (run wiki ingest)")
    t.add_row("network", network_status())
    for k, v in device_specs().items():
        t.add_row(k, str(v))
    console.print(t)


if __name__ == "__main__":
    app()
