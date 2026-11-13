"""W2-155: the live shared reranker's round trip by request shape (a handful of ordinary-size requests)."""
import json
import socket
import statistics
import sys
import time
from pathlib import Path

SOCK = str(Path.home() / ".cache/gov-os/rerank.sock")
Q = "Which files implement the leapfrog integrator?"


def ask(texts):
    start = time.perf_counter()
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as c:
        c.connect(SOCK)
        c.sendall((json.dumps([Q, texts]) + "\n").encode())
        line = c.makefile("rb").readline()
    s = time.perf_counter() - start
    assert "scores" in json.loads(line), line[:200]
    return s


def text(n, i):
    base = f"[path: docs/part-{i}.md]\n" + ("The integrator advances position and velocity by half steps. " * 200)
    return base[:n]


shapes = [("1 x 10", [text(10, 0)]), ("1 x 600", [text(600, 0)]), ("16 x 600", [text(600, i) for i in range(16)]),
          ("30 x 600", [text(600, i) for i in range(30)]), ("15 x 1300", [text(1300, i) for i in range(15)]),
          ("18 x 1300", [text(1300, i) for i in range(18)]), ("30 x 1300", [text(1300, i) for i in range(30)]),
          ("33 x 600", [text(600, i) for i in range(33)])]
out = {}
for name, texts in shapes:
    times = [ask(texts) for _ in range(5)]
    out[name] = {"median_ms": round(1000 * statistics.median(times), 1), "min_ms": round(1000 * min(times), 1)}
    print(name, out[name], flush=True)
