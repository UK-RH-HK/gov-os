"""Does OLLAMA_NUM_PARALLEL reach the embedding runner? np_check.py <port> <parallel> <log>"""
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from gov.retrieval import semantic

PORT, PARALLEL, LOG = int(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
assert PORT not in (11434, 11435)
HOST = f"127.0.0.1:{PORT}"
env = {**os.environ, "OLLAMA_HOST": HOST, "OLLAMA_NUM_PARALLEL": PARALLEL, "OLLAMA_DEBUG": "1"}
with LOG.open("w") as log:
    server = subprocess.Popen(["/home/usain/.local/ollama/bin/ollama", "serve"], env=env, stdin=subprocess.DEVNULL,
                              stdout=log, stderr=log, start_new_session=True)
try:
    for _ in range(100):
        if semantic._ask("/api/version", host=HOST):
            break
        time.sleep(0.2)
    print("version", semantic._ask("/api/version", host=HOST))
    semantic._embed(["check"], HOST)
    for entry in Path("/proc").iterdir():
        if entry.name.isdigit():
            try:
                stat = (entry / "stat").read_text().rsplit(")", 1)[1].split()
                if int(stat[1]) == server.pid:
                    args = (entry / "cmdline").read_bytes().split(b"\0")
                    print("runner", entry.name, b" ".join(a for a in args if a)[-260:].decode())
            except (OSError, ValueError, IndexError):
                pass
finally:
    os.killpg(server.pid, signal.SIGTERM)
    server.wait(timeout=30)
