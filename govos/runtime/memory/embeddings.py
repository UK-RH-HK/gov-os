"""Embedding providers. The kernel ships a deterministic, dependency-free baseline (hashed n-gram vectors).

This is NOT a neural embedding model. It is a reproducible lexical-semantic approximation that makes semantic routing,
fusion, manifests and regression tests fully testable offline. Repositories select a stronger embedder through
MEMORY_POLICY.embedding after a measured benchmark (framework section 14.3); the manifest pins the choice.
"""
from __future__ import annotations

import hashlib
import math
import re
from typing import Iterable, Protocol

TOKEN_RX = re.compile(r"[A-Za-z_][A-Za-z0-9_]{1,}|\d+")
STOP = {"the", "a", "an", "of", "to", "and", "or", "in", "on", "for", "is", "are", "be", "by", "with", "as", "at", "it",
        "this", "that", "from", "was", "we", "our", "not", "no", "yes", "if", "then", "than", "so", "do", "does"}


class Embedder(Protocol):
    id: str
    version: str
    dim: int

    def embed(self, text: str) -> list[float]: ...


def _split_camel(tok: str) -> list[str]:
    parts = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", tok).replace("_", " ").lower().split()
    return parts if len(parts) > 1 else []


def tokenize(text: str) -> list[str]:
    toks = []
    for t in TOKEN_RX.findall(text):
        low = t.lower()
        if low in STOP:
            continue
        toks.append(low)
        toks.extend(p for p in _split_camel(t) if p not in STOP)
    return toks


class HashedNgramEmbedder:
    id = "hashed-ngram"

    def __init__(self, dim: int = 512, version: str = "1"):
        self.dim = int(dim)
        self.version = str(version)

    def _features(self, text: str) -> Iterable[str]:
        toks = tokenize(text)
        yield from toks
        for a, b in zip(toks, toks[1:]):
            yield a + "_" + b

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        counts: dict[str, int] = {}
        for f in self._features(text):
            counts[f] = counts.get(f, 0) + 1
        for f, c in counts.items():
            h = hashlib.sha1(f.encode("utf-8")).digest()
            idx = int.from_bytes(h[:4], "big") % self.dim
            sign = 1.0 if h[4] & 1 else -1.0
            w = 1.0 + math.log(c)
            if len(f) > 12 or "_" in f:
                w *= 1.3  # bigrams and long identifiers carry more meaning
            vec[idx] += sign * w
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [round(v / norm, 6) for v in vec]


def cosine(a: list[float], b: list[float]) -> float:
    return float(sum(x * y for x, y in zip(a, b)))


def make_embedder(config: dict) -> Embedder:
    provider = (config or {}).get("provider", "hashed-ngram")
    if provider == "hashed-ngram":
        return HashedNgramEmbedder(dim=int(config.get("dimensions", 512)), version=str(config.get("version", "1")))
    raise ValueError(f"Unknown embedding provider '{provider}'. Register it via MEMORY_POLICY.embedding and a provider adapter.")
