"""The one test-selection tool for every level (owner, DEC-953 item 4): workers, leads, the close and the nightly.

It runs the product's own selection (gov.close.select.plan, W2-66) unchanged, with two inputs set by DEC-953:
  1. the governance files are left out of the change before tests are chosen (item 4a): briefs, prompts, the
     orchestration record (the nightly's folder included), the record places of the test map's record_only list,
     and .gov-runtime/. They never widen a run to the full suite. No test-map change.
  2. the change is the ticket's own: by default the merge base with w2/integrate (a lead's worktree), or, with
     --merge <commit>, that merge's first parent (the close on the merged code). The nightly runs everything.

Run with the tree's own src first on PYTHONPATH (DEC-732):
    PYTHONPATH=<tree>/src python3 select_tests.py <tree> <W2 id> <ticket id> [--merge <commit>] [--base <commit>]
Prints one JSON object: scope ("scoped" or "full"), why_full, base, the governance paths left out, the change that
counted, the selected suites with their reasons, and pytest_options (--ignore/--deselect to add to `pytest tests`).
"full" means the change touched shared core code (or something unplaceable): then run the full suite."""
import argparse
import json
import subprocess
from pathlib import Path

from gov.close import select

GOVERNANCE = [
    "governance/project/briefs/**",
    "governance/project/prompts/**",
    "governance/project/orchestration/**",
    ".gov-runtime/**",
]


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tree")
    ap.add_argument("wbs")
    ap.add_argument("ticket")
    ap.add_argument("--merge")
    ap.add_argument("--base")
    ap.add_argument("--integration", default="w2/integrate")
    a = ap.parse_args()
    root = Path(a.tree).resolve()

    merges = [git(root, "rev-parse", m) for m in (a.merge or "").split(",") if m]
    if a.base:
        since = git(root, "rev-parse", a.base)
    elif merges:
        since = git(root, "rev-parse", merges[-1] + "^1")  # the oldest merge's parent
    else:
        since = git(root, "merge-base", "HEAD", a.integration)
    # the change: each merge's own (parent..merge), all of a ticket's merges together; else since..HEAD
    spans = [(m + "^1", m) for m in merges] if merges and not a.base else [(since, "HEAD")]

    test_map, _ = select.load_map(root)
    record_places = list((test_map or {}).get("record_only") or [])
    left_out = []

    def is_governance(path):
        return any(select.match(path, p) for p in GOVERNANCE + record_places)

    def changed(root_, since_):
        # the merges' own change, not everything merged after them; tests still run on HEAD
        paths = set()
        for lo, hi in spans:
            names = select._git(root_, "-c", "core.quotePath=false", "diff", "-z", "--no-renames", "--name-only",
                                lo, hi)
            paths.update(filter(None, names.split("\0")))
        paths = sorted(paths)
        keep = []
        for p in paths:
            (left_out if is_governance(p) else keep).append(p)
        return keep

    select.changed = changed
    select.base = lambda root_: since
    scope = select.plan(root, a.wbs, ticket=a.ticket)

    opts = [f"--ignore={root / rel}" for rel in scope.get("ignore", []) if rel != "tests"]
    for node in scope.get("deselect", []):
        opts.append(f"--deselect={node}")
        if node.startswith("tests/"):
            opts.append(f"--deselect={node[len('tests/'):]}")
    print(json.dumps({"scope": scope["scope"], "why_full": scope.get("why_full", []), "base": since,
                      "head": scope.get("head"), "governance_left_out": sorted(set(left_out)),
                      "changed": scope.get("changed", []), "selected": scope.get("selected", []),
                      "pytest_options": opts, "ignore": scope.get("ignore", []),
                      "deselect": scope.get("deselect", []), "per_test_timeout": scope.get("per_test_timeout")}, indent=1))


if __name__ == "__main__":
    main()
