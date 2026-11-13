"""A stand-in for ``gov.rebuild.command.run`` for run 6's Case C (NC-1, P1-W2-88-NC-1 (a); ``test_w2_88_nc1_commit.py``).

Python loads it as ``sitecustomize`` in the child process when this folder is first on that child's ``PYTHONPATH`` (the case sets
it through the adoption's ``extra_env``). Stage A9 calls ``gov.rebuild.command.run`` in full (I3), after its copy step has written
and staged the kernel files and before its one record commit. This stand-in **acts on the planted repository, then calls the real
``run``** (the store is built as A9 always builds it, with the suite's stand-in embedder), so A9 reaches its record commit, where
the planted ``pre-commit`` hook refuses it.

The action (in the repository ``root``): rewrites the tracked ``docs/notes.txt`` (not staged) and stages a new file
``staged-during-run.md``.

It reports on stderr: ``nc1-standin: <json>`` (the HEAD it saw and which of ``W2_88_NC1_COPIES`` (a JSON list: A9's copy plan) were
in the tree and in the index when it acted) before it acts, and ``nc1-standin-returned: {"head": <HEAD>}`` once the real rebuild
has returned (A9 then proceeds to its record commit). A case reads those lines to know the plant took, the copy step had run and A9
reached the commit.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def _git(root, *args):
    return subprocess.run(["git", "-C", str(root), "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", *args],
                          check=True, capture_output=True, text=True).stdout


def _write(root, rel, text):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def act(root):
    _write(root, "docs/notes.txt", "Edited during the run by the stand-in.\n")
    _write(root, "staged-during-run.md", "# Staged during the run\n\nSomeone else's new file.\n")
    _git(root, "add", "staged-during-run.md")


def _install():
    import gov.rebuild.command as rebuild
    real = rebuild.run

    def run(*args, **keywords):
        root = Path(args[0] if args else keywords["root"])
        copies = json.loads(os.environ.get("W2_88_NC1_COPIES") or "[]")
        staged = set(_git(root, "ls-files").splitlines())
        seen = {"head": _git(root, "rev-parse", "HEAD").strip(), "in_tree": sorted(c for c in copies if (root / c).is_file()),
                "in_index": sorted(c for c in copies if c in staged)}
        sys.stderr.write("nc1-standin: " + json.dumps(seen) + "\n")
        sys.stderr.flush()
        act(root)
        result = real(*args, **keywords)
        sys.stderr.write("nc1-standin-returned: " + json.dumps({"head": _git(root, "rev-parse", "HEAD").strip()}) + "\n")
        sys.stderr.flush()
        return result

    rebuild.run = run


try:
    _install()
except Exception as exc:  # noqa: BLE001
    sys.stderr.write(f"standin_nc1: not installed: {exc!r}\n")
