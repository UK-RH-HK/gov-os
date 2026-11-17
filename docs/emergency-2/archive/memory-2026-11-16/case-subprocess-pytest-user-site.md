---
name: case-subprocess-pytest-user-site
description: "pytest lives in ~/.local user site; a test that starts `python -m pytest` with its own HOME and no PYTHONUSERBASE fails under lead_verify (\"No module named pytest\")"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 89b1ca32-6712-49cd-a23c-727748f78929
  modified: 2026-11-16T16:20:23.474Z
---

pytest is installed only in the user site (/home/usain/.local/lib/python3.12/site-packages). A test case that starts
`sys.executable -m pytest` as a subprocess with HOME set to a temp folder finds pytest only when PYTHONUSERBASE is
inherited. The heavy-slot runs set it, so the case passes there. lead_verify does not set it, so the case fails there
(W2-191 td-2 run-line case, 2026-11-16).

**Why:** this cost a fix round; gov accept and the worker's runs were green, and only lead_verify showed the red.

**How to apply:** every test-designer or engineer brief whose cases start pytest or python as a subprocess says: keep
the parent's import path (for example, PYTHONPATH naming the folder that holds the running pytest, or
site.getuserbase()), never rely on PYTHONUSERBASE being set. Also: in the lead's own shell $TMPDIR is empty; use
/tmp/gov-os-lead-<W2>/ for heavy-slot runs. A fix round's tests worktree starts at the test designer's last commit,
never at the ticket head ([[tests-branch-never-ff-to-ticket]]).
