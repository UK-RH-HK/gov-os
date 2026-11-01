"""The determinism matrix: single-text requests, one in flight on a -np 1 server (the baseline), against servers at
-np 2, 4 and 8 with one in flight and with n in flight; and the rebuild's own batched form repeated at -np 1.
    det_matrix.py <port> <store.db> <n_chunks> <cpu list lo-hi>"""
import json
import math
import os
import signal
import sqlite3
import struct
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from gov.retrieval import semantic

PORT, STORE, N = int(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3])
LO, HI = (int(x) for x in sys.argv[4].split("-"))
assert PORT not in (11434, 11435)
HOST = f"127.0.0.1:{PORT}"
connection = sqlite3.connect(STORE.resolve().as_uri() + "?mode=ro", uri=True)
rows = connection.execute(
    "SELECT f.text, v.embedding FROM semantic_vector v JOIN lexical_chunk c ON c.chunk_id = v.chunk_id "
    "JOIN lexical_fts f ON f.rowid = c.id ORDER BY c.id").fetchall()
connection.close()
refs = [(t[:semantic.EMBED_CHARS], bytes(b)) for t, b in rows][::max(1, len(rows) // N)][:N]


def compare(a_list, b_list):
    differ, max_abs, min_cos = 0, 0.0, 1.0
    for a, b in zip(a_list, b_list):
        if a == b:
            continue
        differ += 1
        fa, fb = struct.unpack(f"{len(a) // 4}f", a), struct.unpack(f"{len(b) // 4}f", b)
        max_abs = max(max_abs, max(abs(x - y) for x, y in zip(fa, fb)))
        dot = sum(x * y for x, y in zip(fa, fb))
        min_cos = min(min_cos, dot / math.sqrt(sum(x * x for x in fa) * sum(y * y for y in fb)))
    return {"differ": differ, "of": len(a_list), "max_abs": round(max_abs, 6), "min_cos": round(min_cos, 6)}


def cap():
    os.sched_setaffinity(0, set(range(LO, HI + 1)))
    os.setpriority(os.PRIO_PROCESS, 0, 10)


def serve(parallel):
    env = {**os.environ, "OLLAMA_HOST": HOST, "OLLAMA_NUM_PARALLEL": str(parallel)}
    server = subprocess.Popen(["/home/usain/.local/ollama/bin/ollama", "serve"], env=env, stdin=subprocess.DEVNULL,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True,
                              preexec_fn=cap)
    for _ in range(100):
        if semantic._ask("/api/version", host=HOST):
            break
        time.sleep(0.2)
    semantic._embed(["warm"], HOST)
    return server


def stop(server):
    os.killpg(server.pid, signal.SIGTERM)
    server.wait(timeout=30)
    time.sleep(1)


def single(width):
    began = time.monotonic()
    with ThreadPoolExecutor(width) as pool:
        out = list(pool.map(lambda r: semantic._embed([r[0]], HOST)[0], refs))
    return out, round(time.monotonic() - began, 2)


def batched():
    began, out = time.monotonic(), []
    for at in range(0, len(refs), 32):
        out += semantic._embed([x for x, _ in refs[at:at + 32]], HOST)
    return out, round(time.monotonic() - began, 2)


server = serve(1)
try:
    base, base_s = single(1)
    again, _ = single(1)
    b1, b1_s = batched()
    b2, _ = batched()
finally:
    stop(server)
print(json.dumps({"np": 1, "single_seq_s": base_s, "single_seq_repeat": compare(base, again), "batched_s": b1_s,
                  "batched_repeat": compare(b1, b2), "batched_vs_single": compare(b1, base),
                  "stored_vs_single": compare([b for _, b in refs], base)}), flush=True)
for parallel in (2, 4, 8):
    server = serve(parallel)
    try:
        seq, seq_s = single(1)
        par, par_s = single(parallel)
        bp, bp_s = batched()
    finally:
        stop(server)
    print(json.dumps({"np": parallel, "single_seq_s": seq_s, "seq_vs_base": compare(seq, base),
                      "single_par_s": par_s, "par_vs_base": compare(par, base), "batched_s": bp_s,
                      "batched_vs_base_batched": compare(bp, b1)}), flush=True)
