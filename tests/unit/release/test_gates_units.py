"""Unit tests of the gates G0 and G2 (W2-209 S3, S4, F3) on a small git repository."""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from gov.release import gates

ENV = {"PATH": os.environ["PATH"], "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_AUTHOR_NAME": "A",
       "GIT_AUTHOR_EMAIL": "a@example.invalid", "GIT_COMMITTER_NAME": "A", "GIT_COMMITTER_EMAIL": "a@example.invalid"}


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], env=ENV, check=True, capture_output=True, text=True).stdout


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    (root / "a.txt").write_text("a\n", encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "first")
    return root


def authority(root: Path, text: str, message: str) -> None:
    path = root / gates.AUTHORITY_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", message)


ON = "patch_releases: on\ndecision: DEC-1223\nbake_hours: 4\n"
OWNER = "Decided-by: owner (standing, DEC-1223)"


def check_of(root: Path) -> str:
    with pytest.raises(gates.GateRefused) as red:
        gates.g0(root)
    assert red.value.gate == "G0"
    return red.value.check


def test_g0_absent_off_decision_uncommitted_and_trailer_each_refuse(repo):
    assert check_of(repo) == "absent"
    authority(repo, "patch_releases: off\ndecision: DEC-1223\n", f"off\n\n{OWNER}")
    assert check_of(repo) == "off"
    authority(repo, ": : not yaml [", f"broken\n\n{OWNER}")
    assert check_of(repo) == "unreadable"
    authority(repo, "patch_releases: on\n", f"no decision\n\n{OWNER}")
    assert check_of(repo) == "decision"
    authority(repo, ON, "on without the trailer\n\nRole: orchestrator")
    assert check_of(repo) == "trailer"
    (repo / gates.AUTHORITY_REL).write_text(ON + "# edited\n", encoding="utf-8")
    assert check_of(repo) == "uncommitted"


def test_g0_passes_for_on_committed_with_the_owner_trailer(repo):
    authority(repo, ON, f"on\n\nRole: orchestrator\n{OWNER}")
    assert gates.g0(repo) == {"decision": "DEC-1223", "bake_hours": 4}


def record(tmp_path: Path, repo: Path, **change) -> Path:
    head = git(repo, "rev-parse", "HEAD").strip()
    body = {"head": head, "tree": git(repo, "rev-parse", "HEAD^{tree}").strip(), "scope": "full", "verdict": "green",
            "optin": ["weekly"], **change}
    path = tmp_path / "NR-1.json"
    path.write_text(json.dumps(body), encoding="utf-8")
    return path


def refused_check(repo: Path, suite) -> str:
    with pytest.raises(gates.GateRefused) as red:
        gates.g2(repo, suite, git(repo, "rev-parse", "HEAD").strip())
    assert red.value.gate == "G2"
    return red.value.check


def test_g2_passes_only_for_the_exact_commit_full_green_with_the_weekly_tier(repo, tmp_path):
    good = gates.g2(repo, record(tmp_path, repo), git(repo, "rev-parse", "HEAD").strip())
    assert good["record"] == "NR-1.json" and good["optin"] == ["weekly"]
    assert refused_check(repo, None) == "missing"
    assert refused_check(repo, record(tmp_path, repo, scope="scoped")) == "scope"
    assert refused_check(repo, record(tmp_path, repo, verdict="red")) == "verdict"
    assert refused_check(repo, record(tmp_path, repo, optin=["lifted"])) == "optin"
    assert refused_check(repo, record(tmp_path, repo, optin=None)) == "optin"
    assert refused_check(repo, record(tmp_path, repo, head="1" * 40)) == "head"
    assert refused_check(repo, record(tmp_path, repo, tree="2" * 40)) == "tree"


@pytest.mark.parametrize("content", ["not json", "[]", '{"head": "main"}', '{"head": "abc123"}', ""])
def test_g2_a_record_that_cannot_be_read_is_refused_as_unreadable_never_as_a_pass(repo, tmp_path, content):
    path = tmp_path / "bad.json"
    path.write_text(content, encoding="utf-8")
    assert refused_check(repo, path) == "unreadable"
    assert refused_check(repo, tmp_path / "absent.json") == "unreadable"
