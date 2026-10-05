"""The one rerank over the merged candidate set (W1-19; DEC-379, DEC-374; ADR-0002 §2).

A reranker is given as its loader: a function without arguments that returns ``score(query, texts)``, one number
per text, higher is better. The loader is called at the first rerank and not before, so nothing of a model is
loaded by importing this module or by a retrieval that has nothing to rerank. A loader that returns None says the
reranker cannot be loaded: the order given is kept and no candidate carries a score.
"""

from __future__ import annotations

import functools
import json
import os
import subprocess
from pathlib import Path

# The pins of ADR-0002 §2; the index manifest records them.
MODEL = "Qwen/Qwen3-Reranker-0.6B"
REVISION = "e61197ed45024b0ed8a2d74b80b4d909f1255473"
# The interpreter of the reranker environment, under the home folder (DEC-397).
PYTHON_REL = ".local/share/gov-os/reranker-venv/bin/python"
_WORKER = Path(__file__).with_name("rerank_worker.py")


@functools.lru_cache(maxsize=None)
def _started(interpreter: str):
    """``score`` of a reranker process started with ``interpreter``, or None when it ends without the model.

    The process is a child of this one, isolated from this one's Python paths and offline whatever the caller's
    environment says. It is started once and stays loaded until this process ends, which closes its input.
    """
    try:
        process = subprocess.Popen([interpreter, "-I", str(_WORKER), MODEL, REVISION], text=True,
                                   env={**os.environ, "HF_HUB_OFFLINE": "1"},
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    except OSError:
        return None
    if not process.stdout.readline():  # it ended before it had the model: the snapshot or a library is absent
        process.wait()
        return None

    def score(query: str, texts: list[str]) -> list[float]:
        process.stdin.write(json.dumps([query, texts]) + "\n")
        process.stdin.flush()
        return json.loads(process.stdout.readline())

    return score


def default_reranker():
    """The loader of the pinned reranker, which runs as a separate, pinned process (ADR-0002 §2).

    That process starts from ``~/.local/share/gov-os/reranker-venv`` (DEC-397), ``~`` being the folder ``HOME``
    names. None when the environment or the snapshot is absent (DEC-374).
    """
    interpreter = Path(os.environ.get("HOME") or Path.home()) / PYTHON_REL
    return _started(str(interpreter)) if interpreter.is_file() else None


def rerank(query: str, candidates: list[dict], reranker=None) -> list[dict]:
    """``candidates`` in the order of the reranker's scores, each with ``rerank_score``; equal scores keep the order
    given. One call of ``score``, with the ``text`` of every candidate. Without a reranker the candidates are returned
    as given."""
    candidates = [dict(candidate) for candidate in candidates]
    score = (reranker or default_reranker)() if candidates else None
    if score is None:
        return candidates
    scores = [float(value) for value in score(query, [candidate["text"] for candidate in candidates])]
    ranked = sorted(zip(scores, candidates, strict=True), key=lambda pair: -pair[0])
    return [{**candidate, "rerank_score": value} for value, candidate in ranked]
