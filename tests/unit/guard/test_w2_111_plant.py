"""W2-111 (DEC-1184 (3)): the planted repository of its decision corpus and its tree cases. It holds no case.

155 worktrees beside the project, one nested inside it, one registered through a linked folder, a locked tree, a tree
whose folder is gone, an evaluation set with a hidden part, a runs root with a clone, and a branch that changes a file
against w2/integrate (the test designer's changed part).

plant(base) -> dict of the places, all real paths.  Deterministic: the same layout under any base.
"""
from __future__ import annotations

import os
import shutil
import subprocess

TICKET = "DAEO-zz90"
WBS = "W1-90"
N_TREES = 155

TICKET_TEXT = f"""---
id: {TICKET}
status: in_progress
deps: []
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 1
assignee: engineer
external-ref: {WBS}
tags: [wave-1, implementation, full]
wbs_id: {WBS}
title: Guard fixture ticket
class: implementation
role: engineer
depends_on: []
allowed_paths:
- src/gov/guard/**
- tests/unit/guard/**
kpis:
  success:
  - The fixture component exists
  failure:
  - The fixture component is missing
profile: FULL
acceptance_tests:
  path: tests/acceptance/{WBS}/
---
# {WBS} Guard fixture ticket
"""

PATH_MAP = """roles: {}
evaluation_sets:
  bench:
    visible:
    - eval/bench/visible/**
    hidden:
    - eval/bench/hidden/**
    - eval/keys/*.key.txt
    measures:
      roles: [engineer, independent-test-designer, independent-auditor]
"""

FILES = {
    "README.md": "# planted\n",
    ".gitignore": ".gov-runtime/\n.wt/\n__pycache__/\n",
    "src/app/main.py": "VALUE = 1\n",
    "src/gov/guard/decide.py": "VALUE = 1\n",
    "src/gov/guard/notes.txt": "n\n",
    "docs/notes.md": "notes\n",
    f"tests/acceptance/{WBS}/test_fixture.py": "VALUE = 1\n",
    "tests/acceptance/W1/test_a.py": "x\n",
    "tests/unit/guard/test_decide.py": "VALUE = 1\n",
    "governance/project/path-map.yaml": PATH_MAP,
    "eval/bench/hidden/q1.txt": "hidden 1\n",
    "eval/bench/hidden/deep/q2.txt": "hidden 2\n",
    "eval/bench/visible/v1.txt": "visible\n",
    "eval/keys/a.key.txt": "k\n",
    "eval/keys/readme.md": "r\n",
    "config/app.yaml": "a: 1\n",
    f".tickets/{TICKET}.md": TICKET_TEXT,
}


def git(at, *args):
    p = subprocess.run(["git", "-C", at, "-c", "user.name=t", "-c", "user.email=t@t.invalid", "-c",
                        "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", *args],
                       capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f"git {args}: {p.stderr}")
    return p.stdout


def plant(base: str, n: int = N_TREES) -> dict:
    base = os.path.realpath(base)
    proj = os.path.join(base, "proj")
    trees = os.path.join(base, "trees")
    home = os.path.join(base, "home")
    for rel, text in FILES.items():
        p = os.path.join(proj, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(text)
    git(proj, "init", "-q", "-b", "main")
    git(proj, "add", "-A")
    git(proj, "commit", "-q", "-m", "planted")
    git(proj, "branch", "w2/integrate")
    with open(os.path.join(proj, "src/app/main.py"), "w") as f:
        f.write("VALUE = 2\n")
    git(proj, "commit", "-q", "-am", "the branch's change")
    os.makedirs(trees)
    for i in range(n):
        t = os.path.join(trees, f"t{i:03d}")
        if i % 3 == 0:
            git(proj, "worktree", "add", "-q", "--detach", t)
        else:
            git(proj, "worktree", "add", "-q", "-b", f"b{i:03d}", t)
    git(proj, "worktree", "lock", os.path.join(trees, "t001"))
    shutil.rmtree(os.path.join(trees, "t002"))
    git(proj, "worktree", "add", "-q", "--detach", os.path.join(proj, ".wt", "n1"))
    os.symlink(trees, os.path.join(base, "alias"))
    git(proj, "worktree", "add", "-q", "--detach", os.path.join(base, "alias", "t900"))
    os.symlink(os.path.join(trees, "t010", "eval", "bench", "hidden"), os.path.join(base, "link"))
    clone = os.path.join(home, "gov-os-runs", WBS, "clone")
    for rel in ("eval/bench/hidden/q.txt", "src/m.py"):
        p = os.path.join(clone, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write("x\n")
    os.makedirs(os.path.join(base, "elsewhere"))
    with open(os.path.join(base, "elsewhere", "plain.txt"), "w") as f:
        f.write("x\n")
    return {"P": proj, "TR": trees, "B": base, "H": home}
