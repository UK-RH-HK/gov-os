"""Start Ollama on demand, or say that retrieval is FTS-only (DEC-260, DEC-261, DEC-257).

``gov`` starts ``ollama serve`` when the endpoint is down and never stops it:
Ollama's own 5-minute idle unload frees the model's memory. There is no unit and
no keep-alive override. When the daemon cannot be reached within the deadline,
the result names the facet state and the warning is written once to standard error.

Two daemons are started so (DEC-261 as DEC-798 amends it): the shared one at
``OLLAMA_HOST``, which builds the index, and a CPU-only one at
``GOV_QUERY_OLLAMA_HOST``, which embeds the questions and nothing else. The second
is started with its own ``OLLAMA_HOST`` and the GPU hidden (``NO_GPU``).
"""

from __future__ import annotations

import http.client
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

DEFAULT_HOST = "127.0.0.1:11434"
HEALTH_PATH = "/api/version"
FACET = "semantic"
WARNING = "Ollama is unavailable: semantic retrieval is skipped and results are FTS-only."
QUERY_HOST_SETTING = "GOV_QUERY_OLLAMA_HOST"  # the CPU-only embedder's address, in OLLAMA_HOST's form (DEC-798)
QUERY_DEFAULT_HOST = "127.0.0.1:11435"
NO_GPU = {"CUDA_VISIBLE_DEVICES": "-1"}  # an id that names no device: Ollama's documented way to use no GPU

_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # the endpoint is local: no proxy


def _healthy(url: str, deadline: float) -> bool:
    """True when ``GET /api/version`` answers 200 before the deadline."""
    try:
        with _OPENER.open(url, timeout=max(0.05, min(1.0, deadline - time.monotonic()))) as reply:
            return reply.status == 200
    except (OSError, http.client.HTTPException):
        return False


def _executable(env) -> str | None:
    """``GOV_OLLAMA_BIN``, then ``ollama`` on ``PATH``, then ``~/.local/ollama/bin/ollama``."""
    home = Path(env.get("HOME") or Path.home()) / ".local/ollama/bin/ollama"
    return (env.get("GOV_OLLAMA_BIN") or shutil.which("ollama", path=env.get("PATH"))
            or (str(home) if home.is_file() else None))


def ensure_available(*, timeout_s: float = 20.0, env=None) -> dict:
    """Make the Ollama endpoint answer within ``timeout_s``, starting ``ollama serve`` if needed; never raises
    when it cannot. ``env`` (default: the process environment) is read for the three variables and given to
    the daemon."""
    env = os.environ if env is None else env
    deadline = time.monotonic() + timeout_s
    host = env.get("OLLAMA_HOST") or DEFAULT_HOST
    url = (host if "://" in host else f"http://{host}").rstrip("/") + HEALTH_PATH
    available = _healthy(url, deadline)
    started = False
    executable = None if available else _executable(env)
    if executable:
        try:
            # Its own session and no inherited streams: the daemon outlives this call and is never stopped.
            subprocess.Popen([executable, "serve"], env=dict(env), stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            started = True
        except OSError:
            pass
        while started and not available and time.monotonic() < deadline:
            time.sleep(0.1)
            available = _healthy(url, deadline)
    if available:
        return {"available": True, "started": started, "facet": FACET, "state": "AVAILABLE", "warning": None}
    print(WARNING, file=sys.stderr)
    return {"available": False, "started": started, "facet": FACET, "state": "FACET_UNAVAILABLE",
            "warning": WARNING}


def query_host(env=None) -> str:
    """The CPU-only embedder's address: ``GOV_QUERY_OLLAMA_HOST``, else ``QUERY_DEFAULT_HOST``."""
    env = os.environ if env is None else env
    return env.get(QUERY_HOST_SETTING) or QUERY_DEFAULT_HOST


def ensure_query_available(*, timeout_s: float = 20.0, env=None) -> dict:
    """Make the CPU-only embedder answer at ``query_host``, as ``ensure_available`` does, starting ``ollama serve``
    with ``OLLAMA_HOST`` set to that address and ``NO_GPU`` in its environment; never stopped."""
    env = os.environ if env is None else env
    return ensure_available(timeout_s=timeout_s, env={**env, "OLLAMA_HOST": query_host(env), **NO_GPU})
