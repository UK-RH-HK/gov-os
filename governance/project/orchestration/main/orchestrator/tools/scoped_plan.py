"""A lead's scoped verification (owner, DEC-952, replacing DEC-880 item 2 (b)): the tests a scoped close of this
ticket would select, computed by the close's own selection (gov.close.select.plan, W2-66) on this worktree.
Run with this worktree's src first on PYTHONPATH (DEC-732):
    PYTHONPATH=<worktree>/src python3 <this file> <worktree> <W2 id> <ticket id>
Prints one JSON object: scope ("scoped" or "full"), why_full, the selected suites with their reasons, and
"pytest_options" (the --ignore and --deselect options to add to the close-form commands of the common brief's step 4).
A "full" scope means the close would run everything (shared core, an unplaced path, no green base...): then the lead
runs the full suite, under the verification lock."""
import json
import sys
from pathlib import Path

from gov.close import select

root, wbs, ticket = Path(sys.argv[1]).resolve(), sys.argv[2], sys.argv[3]
scope = select.plan(root, wbs, ticket=ticket)
opts = [f"--ignore={root / rel}" for rel in scope.get("ignore", []) if rel != "tests"]
for node in scope.get("deselect", []):
    opts.append(f"--deselect={node}")
    if node.startswith("tests/"):
        opts.append(f"--deselect={node[len('tests/'):]}")
print(json.dumps({"scope": scope["scope"], "why_full": scope.get("why_full", []), "base": scope.get("base"),
                  "selected": scope.get("selected", []), "pytest_options": opts,
                  "per_test_timeout": scope.get("per_test_timeout")}, indent=1))
