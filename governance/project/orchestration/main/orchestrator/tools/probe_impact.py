"""At merge time (owner, standing, DEC-895 item 2): which merged-but-not-closed FULL tickets' probes does a merge make
stale? Run right after each merge into w2/integrate (or into a ticket branch):

    PYTHONPATH=<main tree>/src python3 probe_impact.py <merge commit>

A ticket counts when its ticket file says `profile: FULL` and `status: in_progress`, its own commits (`Task: <id>`) are
in the merge's first parent (merged, not closed), and it has a probe record under `docs/probes/<id>/`. Its judged
files are the files its own commits changed (the probe gate's "probed paths"). The merge's changes are its diff
against its first parent. Prints each ticket whose judged files the merge changes, with the files; exits 1 if any,
so that its fresh probe is scheduled straight away and noted in the queue. Row W2-M403 stays as the close's backstop.
"""
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path("/home/usain/Dynamic-Agentic-Engineering-OS")


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True).stdout


merge = sys.argv[1]
changed = set(git("diff", "--name-only", f"{merge}^1", merge).split())
first = f"{merge}^1"
hits = []
for tf in sorted((ROOT / ".tickets").glob("DAEO-*.md")):
    try:
        front = yaml.safe_load(tf.read_text().split("---")[1]) or {}
    except Exception:
        continue
    if front.get("profile") != "FULL" or front.get("status") != "in_progress":
        continue
    tid = front.get("id")
    if not (ROOT / "docs/probes" / tid).is_dir():
        continue
    own = git("log", "--format=%H", f"--grep=^Task: {tid}$", first).split()
    if not own:
        continue
    judged = set()
    for sha in own:
        if len(git("rev-list", "--parents", "-1", sha).split()) > 2:  # a merge brings others' work
            continue
        judged |= set(git("show", "--name-only", "--format=", sha).split())
    hit = sorted(judged & changed)
    if hit:
        hits.append((tid, front.get("wbs_id"), hit))
for tid, wbs, files in hits:
    print(f"STALE PROBE: {wbs} ({tid}): the merge changes {len(files)} judged file(s): {', '.join(files[:8])}")
print(f"probe impact of {merge[:12]}: {len(hits)} ticket(s)")
sys.exit(1 if hits else 0)
