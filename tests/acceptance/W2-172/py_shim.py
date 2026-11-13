"""A planted interpreter for the cron wrapper (``GOV_MEMAUDIT_PYTHON``; Interface item 8).

It answers ``-m gov.memaudit due ...`` and ``-m gov.memaudit run ...`` from ``shim_plan.json`` in ``W172_STATE`` and logs
each such call (argv, cwd) to ``shim_calls.jsonl``; any other call (the wrapper may use its interpreter for a small
job of its own) is passed on to the real interpreter unchanged.

``shim_plan.json``: ``{"due_lines": [...], "due_exit": 0|1|4, "run_lines": [...], "run_exit": <int>}``.
"""
import json
import os
import sys

STATE = os.environ.get("W172_STATE") or os.path.join(os.path.dirname(os.path.realpath(__file__)), "state")
REAL = "@REAL@"


def main():
    argv = sys.argv[1:]
    if argv[:2] != ["-m", "gov.memaudit"] or argv[2:3] not in (["due"], ["run"]):
        os.execv(REAL, [REAL, *argv])
    os.makedirs(STATE, exist_ok=True)
    try:
        with open(os.path.join(STATE, "shim_plan.json"), encoding="utf-8") as f:
            plan = json.load(f)
    except (OSError, ValueError):
        plan = {}
    with open(os.path.join(STATE, "shim_calls.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps({"sub": argv[2], "argv": argv, "cwd": os.getcwd()}) + "\n")
    key = argv[2]
    for line in plan.get(f"{key}_lines", []):
        print(line)
    return int(plan.get(f"{key}_exit", 0))


if __name__ == "__main__":
    sys.exit(main())
