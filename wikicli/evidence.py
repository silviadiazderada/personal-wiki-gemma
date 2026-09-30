"""Saved outputs: a JSONL run log for every command, plus readable evidence cards."""
from __future__ import annotations

import json
import platform
import socket
import subprocess
import time
from pathlib import Path

import psutil

from .config import EVIDENCE, RUN_LOG


def network_status() -> str:
    """'online' or 'offline', by trying to open a TCP connection to a public DNS server."""
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=1.5).close()
        return "online"
    except OSError:
        return "offline"


def device_specs() -> dict:
    def sysctl(key):
        try:
            return subprocess.run(["sysctl", "-n", key], capture_output=True, text=True).stdout.strip()
        except OSError:
            return ""
    vm = psutil.virtual_memory()
    return {"os": f"macOS {platform.mac_ver()[0]}" if platform.system() == "Darwin" else platform.platform(),
            "chip": sysctl("machdep.cpu.brand_string") or platform.processor(),
            "memory_total_gb": round(vm.total / 2**30, 1),
            "memory_available_gb": round(vm.available / 2**30, 1),
            "disk_free_gb": round(psutil.disk_usage("/").free / 2**30, 1)}


def memory_snapshot(llm) -> dict:
    """Memory Ollama reports for loaded models, plus RSS of the Ollama processes and system use."""
    loaded = [{"model": m["name"], "size_gb": round(m.get("size", 0) / 1e9, 2),
               "gpu_gb": round(m.get("size_vram", 0) / 1e9, 2)} for m in llm.loaded_models()] \
        if hasattr(llm, "loaded_models") else []
    rss = 0
    for p in psutil.process_iter(["name", "memory_info"]):
        try:
            if p.info["name"] and "ollama" in p.info["name"].lower():
                rss += p.info["memory_info"].rss
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    vm = psutil.virtual_memory()
    return {"ollama_loaded": loaded, "ollama_process_rss_gb": round(rss / 2**30, 2),
            "system_used_gb": round((vm.total - vm.available) / 2**30, 2)}


def log_run(record: dict) -> None:
    RUN_LOG.parent.mkdir(parents=True, exist_ok=True)
    record = {"time": time.strftime("%Y-%m-%d %H:%M:%S"), **record}
    with open(RUN_LOG, "a") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def save_card(folder: str, name: str, markdown: str, data: dict) -> Path:
    d = EVIDENCE / folder
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    path = d / f"{name}.md"
    path.write_text(markdown)
    return path


def passages_md(hits: list[dict]) -> str:
    out = []
    for n, h in enumerate(hits, 1):
        p = h["passage"]
        scores = f"rrf={h['score']:.4f}, bm25 rank={h['bm25_rank']}, embedding rank={h['dense_rank']}" + \
                 (f", cosine={h['dense_sim']:.2f}" if h.get("dense_sim") is not None else "")
        text = p["text"].replace("\n", "\n> ")
        out.append(f"**[{n}] {p['label']}, {p['locator']}** · `{p['path']}` · id `{p['id']}` · {p['kind']}  \n"
                   f"<sub>{scores}</sub>\n\n> {text}\n")
    return "\n".join(out) or "_(no passages retrieved)_"
