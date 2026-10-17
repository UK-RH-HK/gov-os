"""Builder tests for the decision checker's exact comparisons (W2-03: W2-M106, W2-L069).

Regression evidence only (DEC-136). They cover what the acceptance tests leave to the builder: a status that is no
string is not canonical, and a file with an empty id that cites a gate is not followed as ``"None"`` or ``""``.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import decisions  # noqa: E402

_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid",
        "GIT_AUTHOR_DATE": "2026-10-09T12:00:00+00:00", "GIT_COMMITTER_DATE": "2026-10-09T12:00:00+00:00"}


def _git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True,
                   env={**_ENV, "HOME": str(root)})


def _checked(root, files):
    _git(root, "init", "-q", "-b", "main")
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "records", "--trailer", "Role: owner")
    return decisions.check(root)


def test_a_status_that_is_no_string_is_not_canonical(tmp_path):
    found = _checked(tmp_path, {"docs/adr/ADR-0101.md": "---\nid: ADR-0101\ntype: decision\nstatus: 1\n---\n"})
    assert [(f["code"], f["ids"]) for f in found] == [("STATUS_NOT_CANONICAL", ["ADR-0101"])]


def test_an_empty_id_that_cites_a_gate_is_not_followed_as_an_id(tmp_path):
    found = _checked(tmp_path, {"docs/a.md": '---\nid: ""\ntype: note\nstatus: ACTIVE\napproval: [DP-1]\n---\n'})
    assert [(f["code"], f["ids"]) for f in found] == [("GATE_NOT_AUTHORISING", ["DP-1"])]
