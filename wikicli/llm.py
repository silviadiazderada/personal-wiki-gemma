"""Model backends. The harness talks to Gemma only through this module.

LocalGemma  -> Ollama's HTTP API on 127.0.0.1 (default, works offline)
OnlineGemma -> Google AI Studio's hosted Gemma (optional extension, needs internet + API key)

Both expose the same `chat()` method so the rest of the harness does not care where
the model runs. Embeddings are always local.
"""
from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, field
from typing import Iterator

import httpx

from .config import Settings


class ModelUnavailable(RuntimeError):
    """Raised with a user-facing explanation when a model cannot be reached."""


@dataclass
class ChatResult:
    text: str
    model: str
    backend: str                      # "local" or "online"
    seconds: float
    stats: dict = field(default_factory=dict)


class LocalGemma:
    backend = "local"

    def __init__(self, settings: Settings, model: str | None = None):
        self.s = settings
        self.model = model or settings.model
        self.http = httpx.Client(base_url=settings.runtime_url, timeout=httpx.Timeout(600, connect=3))

    # ---- health -------------------------------------------------------------
    def runtime_version(self) -> str | None:
        try:
            return self.http.get("/api/version").json().get("version")
        except httpx.HTTPError:
            return None

    def installed_models(self) -> list[str]:
        try:
            return [m["name"] for m in self.http.get("/api/tags").json().get("models", [])]
        except httpx.HTTPError:
            return []

    def check(self, model: str | None = None) -> None:
        model = model or self.model
        if self.runtime_version() is None:
            raise ModelUnavailable(
                f"The local model runtime (Ollama) is not reachable at {self.s.runtime_url}.\n"
                "Start it by opening the Ollama app, or run `ollama serve` in another terminal."
            )
        if model not in self.installed_models():
            raise ModelUnavailable(
                f"Model '{model}' is not downloaded yet. While online, run: ollama pull {model}"
            )

    def loaded_models(self) -> list[dict]:
        """What Ollama currently holds in memory (used for memory measurements)."""
        try:
            return self.http.get("/api/ps").json().get("models", [])
        except httpx.HTTPError:
            return []

    # ---- generation ---------------------------------------------------------
    def _payload(self, messages, schema, num_ctx, temperature, stream):
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "keep_alive": self.s.keep_alive,
            "think": False,
            "options": {
                "num_ctx": num_ctx or self.s.num_ctx,
                "temperature": self.s.temperature if temperature is None else temperature,
                "seed": self.s.seed,                 # fixed seed: repeatable outputs
            },
        }
        if schema is not None:
            payload["format"] = schema   # Ollama constrains decoding to this JSON schema
        return payload

    def chat(self, messages: list[dict], schema: dict | None = None,
             num_ctx: int | None = None, temperature: float | None = None) -> ChatResult:
        self.check()
        t0 = time.perf_counter()
        try:
            r = self.http.post("/api/chat", json=self._payload(messages, schema, num_ctx, temperature, False))
            r.raise_for_status()
        except httpx.HTTPError as e:
            raise ModelUnavailable(f"Local model call failed: {e}") from e
        data = r.json()
        stats = {k: data.get(k) for k in ("total_duration", "load_duration", "prompt_eval_count",
                                          "prompt_eval_duration", "eval_count", "eval_duration")}
        return ChatResult(data["message"]["content"], self.model, "local", time.perf_counter() - t0, stats)

    def stream_chat(self, messages: list[dict], num_ctx: int | None = None) -> Iterator[str | ChatResult]:
        """Yield text pieces as they are generated, then a final ChatResult."""
        self.check()
        t0 = time.perf_counter()
        parts, stats = [], {}
        with self.http.stream("POST", "/api/chat", json=self._payload(messages, None, num_ctx, None, True)) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                chunk = json.loads(line)
                piece = chunk.get("message", {}).get("content", "")
                if piece:
                    parts.append(piece)
                    yield piece
                if chunk.get("done"):
                    stats = {k: chunk.get(k) for k in ("total_duration", "load_duration", "prompt_eval_count",
                                                        "eval_count", "eval_duration")}
        yield ChatResult("".join(parts), self.model, "local", time.perf_counter() - t0, stats)

    # ---- embeddings ---------------------------------------------------------
    def embed(self, texts: list[str], batch: int = 32) -> list[list[float]]:
        out: list[list[float]] = []
        for i in range(0, len(texts), batch):
            try:
                r = self.http.post("/api/embed", json={"model": self.s.embed_model, "input": texts[i:i + batch],
                                                       "keep_alive": self.s.keep_alive})
                r.raise_for_status()
            except httpx.HTTPError as e:
                raise ModelUnavailable(f"Local embedding model unavailable: {e}") from e
            out.extend(r.json()["embeddings"])
        return out

    def embeddings_available(self) -> bool:
        return self.runtime_version() is not None and self.s.embed_model in self.installed_models()


class OnlineGemma:
    """Optional: hosted Gemma through Google AI Studio (Gemini API). Same interface as LocalGemma."""
    backend = "online"

    def __init__(self, settings: Settings, model: str | None = None):
        self.s = settings
        self.model = model or settings.online_model
        self.key = os.environ.get(settings.online_api_key_env)
        self.http = httpx.Client(base_url=settings.online_api_url, timeout=120)

    def check(self, model: str | None = None) -> None:
        if not self.key:
            raise ModelUnavailable(
                f"Online mode needs an API key in the environment variable {self.s.online_api_key_env}. "
                "Local mode (the default) does not."
            )

    def chat(self, messages: list[dict], schema: dict | None = None,
             num_ctx: int | None = None, temperature: float | None = None) -> ChatResult:
        self.check()
        # Hosted Gemma has no separate system role: fold instructions into the first user turn.
        system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
        contents = []
        for m in messages:
            if m["role"] == "system":
                continue
            contents.append({"role": "model" if m["role"] == "assistant" else "user",
                             "parts": [{"text": m["content"]}]})
        if system and contents:
            contents[0]["parts"][0]["text"] = f"{system}\n\n{contents[0]['parts'][0]['text']}"
        if schema is not None and contents:
            contents[-1]["parts"][0]["text"] += (
                "\n\nRespond with JSON only, matching this JSON schema:\n" + json.dumps(schema))
        t0 = time.perf_counter()
        try:
            r = self.http.post(f"/models/{self.model}:generateContent", params={"key": self.key},
                               json={"contents": contents,
                                     "generationConfig": {"temperature": self.s.temperature
                                                          if temperature is None else temperature}})
            r.raise_for_status()
        except httpx.HTTPError as e:
            raise ModelUnavailable(f"Online model call failed (are you connected?): {e}") from e
        data = r.json()
        text = "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"])
        return ChatResult(text, self.model, "online", time.perf_counter() - t0, data.get("usageMetadata", {}))

    def stream_chat(self, messages, num_ctx=None):
        result = self.chat(messages)
        yield result.text
        yield result


def get_model(settings: Settings, mode: str = "local", model: str | None = None):
    if mode == "online":
        return OnlineGemma(settings, model)
    return LocalGemma(settings, model)


def parse_json(text: str) -> dict:
    """Parse a model's JSON reply, tolerating code fences or stray prose around it."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            return json.loads(m.group(0))
        raise
