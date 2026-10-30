"""Run `gov retrieve --json` and print its answer with every evidence item that names this ticket's acceptance tests
taken out (DEC-820 (c): the engineer never reads tests/acceptance/W2-05/). Usage:

    PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src timeout 300 python3 \
        /home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/retrieve_safe.py "<question>" [more retrieve options]

It prints how many items it withheld, never their contents.
"""
import json
import subprocess
import sys

FORBIDDEN = "tests/acceptance/W2-05"

done = subprocess.run([sys.executable, "-m", "gov.cli.main", "retrieve", *sys.argv[1:], "--json"],
                      capture_output=True, text=True)
try:
    envelope = json.loads(done.stdout)
except json.JSONDecodeError:
    print(f"retrieve exit {done.returncode}; no JSON answer (its output is withheld, it may name the tests)")
    sys.exit(done.returncode or 1)
result = envelope.get("result") or {}
kept, withheld = [], 0
for item in result.get("evidence") or []:
    if FORBIDDEN in json.dumps(item):
        withheld += 1
    else:
        kept.append(item)
result["evidence"] = kept
for key in ("expansions", "gaps"):
    items = result.get(key) or []
    clean = [i for i in items if FORBIDDEN not in json.dumps(i)]
    withheld += len(items) - len(clean)
    result[key] = clean
print(json.dumps(envelope, indent=1))
print(f"# withheld {withheld} item(s) naming {FORBIDDEN}", file=sys.stderr)
