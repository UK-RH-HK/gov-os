"""The planted gate (``--gate-cmd <exe>``; Interface item 8): called with no arguments, exit 0 is open, anything else busy.

Answers from ``gate_plan.json`` in ``W172_STATE``: ``{"codes": [1, 1, 0]}``, the n-th call takes the n-th code (the last
repeats; default 0). Logs each call to ``gate_calls.jsonl``: the time, the argv, and what the highest ``memory-audit-*``
folder of the sets root (``world.json``'s ``sets``) held at that moment: DECLARATION.json, FIGURES.json, POOL.json.
"""
import fcntl
import json
import os
import sys
import time

STATE = os.environ.get("W172_STATE") or os.path.join(os.path.dirname(os.path.realpath(__file__)), "state")


def read_json(name, default):
    try:
        with open(os.path.join(STATE, name), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def main():
    os.makedirs(STATE, exist_ok=True)
    world = read_json("world.json", {})
    plan = read_json("gate_plan.json", {})
    seen = {}
    runs = os.path.join(world.get("sets", ""), "runs")
    names = sorted(n for n in os.listdir(runs) if n.startswith("memory-audit-")) if os.path.isdir(runs) else []
    if names:
        folder = os.path.join(runs, names[-1])
        seen = {k: os.path.exists(os.path.join(folder, k)) for k in ("DECLARATION.json", "FIGURES.json", "POOL.json")}
    fd = os.open(os.path.join(STATE, "gate_calls.jsonl"), os.O_RDWR | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        with open(os.path.join(STATE, "gate_calls.jsonl"), encoding="utf-8") as f:
            n = sum(1 for x in f if x.strip())
        os.write(fd, (json.dumps({"t": time.time(), "argv": sys.argv[1:], "seen": seen}) + "\n").encode())
    finally:
        os.close(fd)
    codes = plan.get("codes") or [0]
    return int(codes[min(n, len(codes) - 1)])


if __name__ == "__main__":
    sys.exit(main())
