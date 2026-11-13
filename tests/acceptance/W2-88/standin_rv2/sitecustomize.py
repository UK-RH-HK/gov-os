"""A stand-in for ``gov.rebuild.command.run`` for the run 5 undo cases (RV2-1, P1-W2-88-RV2-1 (a); ``test_w2_88_rv2_undo.py``).

Python loads it as ``sitecustomize`` in the child process when this folder is first on that child's ``PYTHONPATH`` (the case
sets it through the adoption's ``extra_env``). Stage A9 calls ``gov.rebuild.command.run`` in full (I3), after its copy step has
written and staged the kernel files; this stand-in **acts on the planted repository, then raises**, so the stage's undo has
something of someone else's to spare and something of its own to take back. It never builds a store and calls nothing of the
product's but ``GovError``.

``W2_88_RV2_ACTION`` is what it does in the repository (``root``):

- ``edit-and-stage``: rewrites the tracked ``docs/notes.txt`` (not staged) and stages a new file ``staged-during-run.md``;
- ``commit-notes``: writes ``notes.md`` and commits it alone (``git commit -- notes.md``: HEAD moves; A9's staged copies are
  not in that commit);
- ``commit-all``: writes ``notes.md`` and commits the whole index (HEAD moves; A9's staged copies are in that commit);
- ``edit-copy`` / ``edit-copy-restaged``: appends a line to A9's copy ``.claude/skills/retrieval/SKILL.md`` (and, for the second,
  stages the edit: the index entry is then no longer the blob A9 staged);
- ``untracked-and-restaged``: writes an untracked ``scratch-untracked.txt`` and edits the tracked ``lib/util.py`` and stages it;
- ``none``: nothing.

``W2_88_RV2_RAISE`` is what it raises: ``KeyboardInterrupt``, or the code of a ``GovError`` (default ``REBUILD_FAILED``).

It reports on stderr: ``rv2-standin: <json>`` with the action, the HEAD it saw, the paths of ``W2_88_RV2_COPIES`` (a JSON
list: A9's copy plan) that were in the tree and in the index when it acted, and, once it has acted, ``rv2-standin-after:
{"head": <HEAD>}``. A case reads those lines to know the plant took and the copy step had run (an undo judged on copies that
were never there proves nothing), and which commit the stand-in made.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

ACTION = os.environ.get("W2_88_RV2_ACTION", "")
RAISE = os.environ.get("W2_88_RV2_RAISE", "REBUILD_FAILED")
COPY_PATH = ".claude/skills/retrieval/SKILL.md"


def _git(root, *args):
    return subprocess.run(["git", "-C", str(root), "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", *args],
                          check=True, capture_output=True, text=True).stdout


def _write(root, rel, text, append=False):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a" if append else "w", encoding="utf-8") as handle:
        handle.write(text)


def act(root):
    if ACTION == "edit-and-stage":
        _write(root, "docs/notes.txt", "Edited during the run by the stand-in.\n")
        _write(root, "staged-during-run.md", "# Staged during the run\n\nSomeone else's new file.\n")
        _git(root, "add", "staged-during-run.md")
    elif ACTION in ("commit-notes", "commit-all"):
        _write(root, "notes.md", "# Notes\n\nCommitted during the run by the stand-in.\n")
        _git(root, "add", "notes.md")
        if ACTION == "commit-notes":
            _git(root, "commit", "-q", "-m", "stand-in commit during the run", "--", "notes.md")
        else:
            _git(root, "commit", "-q", "-m", "stand-in commit of the whole index during the run")
    elif ACTION in ("edit-copy", "edit-copy-restaged"):
        _write(root, COPY_PATH, "\n# edited during the run by the stand-in\n", append=True)
        if ACTION == "edit-copy-restaged":
            _git(root, "add", COPY_PATH)
    elif ACTION == "untracked-and-restaged":
        _write(root, "scratch-untracked.txt", "Made during the run, never added.\n")
        _write(root, "lib/util.py", "def helper():\n    return 42\n")
        _git(root, "add", "lib/util.py")
    elif ACTION != "none":          # ``none``: it only raises (the copy step's own effect is what is judged)
        sys.stderr.write(f"rv2-standin: unknown action {ACTION!r}\n")


def run(*args, **keywords):
    root = Path(args[0] if args else keywords["root"])
    copies = json.loads(os.environ.get("W2_88_RV2_COPIES") or "[]")
    head = _git(root, "rev-parse", "HEAD").strip()
    staged = set(_git(root, "ls-files").splitlines())
    seen = {"action": ACTION, "head": head, "in_tree": sorted(c for c in copies if (root / c).is_file()),
            "in_index": sorted(c for c in copies if c in staged)}
    sys.stderr.write("rv2-standin: " + json.dumps(seen) + "\n")
    sys.stderr.flush()
    act(root)
    sys.stderr.write("rv2-standin-after: " + json.dumps({"head": _git(root, "rev-parse", "HEAD").strip()}) + "\n")
    sys.stderr.flush()
    if RAISE == "KeyboardInterrupt":
        raise KeyboardInterrupt
    from gov.cli.errors import GovError
    raise GovError(RAISE, "planted: the stand-in rebuild acted on the repository and failed", {"planted": True})


def _install():
    import gov.rebuild.command as rebuild
    rebuild.run = run


try:
    _install()
except Exception as exc:  # noqa: BLE001
    sys.stderr.write(f"standin_rv2: not installed: {exc!r}\n")
