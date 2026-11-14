"""A planted interpreter for the cron wrapper (``GOV_MEMAUDIT_PYTHON``; W2-187 Interface I11).

It answers ``-m gov.memaudit <sub>`` for ``standing live``, ``due``, ``due --fresh``, ``maintain``, ``standing run`` and
``run`` from ``shim187_plan.json`` in ``W172_STATE`` and logs each such call (key, argv, cwd, its number) to
``shim187_calls.jsonl``; any other call goes to the real interpreter unchanged.

``shim187_plan.json``: ``{"<key>": {"lines": [...], "exit": <int>}}``; a list of such objects is taken by the call's
number (the last repeats).
"""
import json
import os
import sys

STATE = os.environ.get("W172_STATE") or os.path.join(os.path.dirname(os.path.realpath(__file__)), "state")
REAL = "@REAL@"


def key_of(argv):
    if argv[:2] != ["-m", "gov.memaudit"] or len(argv) < 3:
        return None
    sub = argv[2:]
    if sub[:2] == ["standing", "live"]:
        return "standing live"
    if sub[:2] == ["standing", "run"]:
        return "standing run"
    if sub[0] == "due":
        return "due --fresh" if "--fresh" in sub else "due"
    if sub[0] in ("maintain", "run"):
        return sub[0]
    return None


def main():
    argv = sys.argv[1:]
    key = key_of(argv)
    if key is None:
        os.execv(REAL, [REAL, *argv])
    os.makedirs(STATE, exist_ok=True)
    try:
        with open(os.path.join(STATE, "shim187_plan.json"), encoding="utf-8") as f:
            plan = json.load(f)
    except (OSError, ValueError):
        plan = {}
    calls = os.path.join(STATE, "shim187_calls.jsonl")
    number = sum(1 for x in open(calls, encoding="utf-8") if x.strip() and json.loads(x)["key"] == key) \
        if os.path.exists(calls) else 0
    with open(calls, "a", encoding="utf-8") as f:
        f.write(json.dumps({"key": key, "argv": argv, "cwd": os.getcwd(), "n": number + 1}) + "\n")
    spec = plan.get(key) or {}
    if isinstance(spec, list):
        spec = spec[min(number, len(spec) - 1)] if spec else {}
    for line in spec.get("lines", []):
        print(line)
    return int(spec.get("exit", 0))


if __name__ == "__main__":
    sys.exit(main())
