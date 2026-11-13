#!/usr/bin/env python3
"""The landing check (OPERATOR-AGENT-1 §3, S16, DEC-1104 (2)): commits outside a ticket on a control path.

    python3 landing_check.py --repo <repo> <rev range>

Prints a JSON list, one item per flagged first-parent commit of the range:
    {"commit": "<40 hex>", "priority": "P1", "paths": [...], "rows": [...], "subject": "...", "reason": "..."}

A commit is outside a ticket as the landing selection reads it (ACT-SELECT-HOOK-1 §1 step 3): it carries
`Role: owner`, or no `Task: DAEO-<ticket>` other than DAEO-sdxk (the CTO's own). It is flagged when its own change
(against its first parent) touches a (b) or (O) control path of the rule table (class-rules.yaml's rows marked
`control: true`; the (O) catch-all and the "none" rows are not control paths, N-5), unless it carries `Role: owner`,
or `Role: operator` together with an `Act:` trailer. Each flagged commit is one inbox P1 item for the trigger to file.
"""
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import act_class  # noqa: E402

CTO_TASK = "DAEO-sdxk"


def git(repo, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    r = subprocess.run(["git", "-C", repo] + list(args), capture_output=True, env=env, stdin=subprocess.DEVNULL)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args[:2])} failed: {r.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return r.stdout.decode("utf-8", "replace")


def trailer_values(repo, commit, key):
    out = git(repo, "log", "-1", f"--format=%(trailers:key={key},valueonly,separator=%x1f)", commit)
    return [v.strip() for v in out.strip().split("\x1f") if v.strip()]


def outside_a_ticket(roles, tasks):
    if any(r.replace(" ", "") == "owner" for r in roles):
        return True
    return not any(re.match(r"^DAEO-[a-z0-9]+$", t.replace(" ", "")) and t.replace(" ", "") != CTO_TASK for t in tasks)


def control_paths(rules, paths):
    hits = []
    for p in paths:
        row = act_class.row_for(rules, "repo", p)
        if row is not None and row.get("control") is True:
            hits.append((p, row.get("id")))
    return hits


def check(repo, rev_range, rules=None):
    rules = rules or act_class.load_rules()
    items = []
    commits = [c for c in git(repo, "rev-list", "--first-parent", rev_range).split() if c]
    for c in commits:
        parents = git(repo, "rev-list", "--parents", "-n", "1", c).split()[1:]
        if not parents:
            continue
        roles = trailer_values(repo, c, "Role")
        tasks = trailer_values(repo, c, "Task")
        if not outside_a_ticket(roles, tasks):
            continue
        if any(r.replace(" ", "") == "owner" for r in roles):
            continue
        acts = trailer_values(repo, c, "Act")
        if any(r.replace(" ", "") == "operator" for r in roles) and acts:
            continue
        paths = [p for p in git(repo, "-c", "core.quotePath=false", "diff", "--no-renames", "--name-only",
                                parents[0], c).splitlines() if p]
        hits = control_paths(rules, paths)
        if not hits:
            continue
        subject = git(repo, "log", "-1", "--format=%s", c).strip()
        why = ("Role: operator without an Act: trailer" if any(r.replace(" ", "") == "operator" for r in roles)
               else "neither Role: owner nor Role: operator with Act:")
        items.append({"commit": c, "priority": "P1", "paths": [p for p, _ in hits],
                      "rows": sorted({r for _, r in hits}), "subject": subject[:200],
                      "reason": f"a commit outside a ticket touches a (b) or (O) control path, {why}"})
    return items


def main(argv):
    if len(argv) != 4 or argv[1] != "--repo":
        sys.stderr.write("usage: landing_check.py --repo <repo> <rev range>\n")
        return 2
    try:
        items = check(argv[2], argv[3])
    except Exception as exc:  # fail closed: a range it cannot read is an item for the owner, not silence
        print(json.dumps([{"commit": None, "priority": "P1", "paths": [], "rows": [],
                           "reason": f"the landing check could not read the range ({exc})"}]))
        return 1
    print(json.dumps(items))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
