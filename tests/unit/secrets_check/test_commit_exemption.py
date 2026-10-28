"""Builder tests for W2-71: row W2-L423's rule passes a real commit of the project only (DEC-911 item 4).

Regression evidence only (DEC-136). The rule's keyword is joined at run time and every 40-hex string is a real object's
id or random hex, so no file holds a token whole. Real git and gitleaks run in a repository built here from scratch.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

from gov import secrets

REPO = Path(__file__).resolve().parents[3]
KEYWORD = "".join(("source", "graph"))


def _git(root, *args, text=None):
    return subprocess.run(["git", "-C", str(root), *args], input=text, capture_output=True, text=True,
                          check=True).stdout.strip()


def _repository(root: Path) -> dict:
    root.mkdir()
    _git(root, "init", "-q")
    (root / "page.md").write_text("Ordinary page.\n")
    _git(root, "add", "page.md")
    _git(root, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "-m", "one")
    _git(root, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "tag", "-a", "v1", "-m", "tag")
    return {"commit": _git(root, "rev-parse", "HEAD"), "tree": _git(root, "rev-parse", "HEAD^{tree}"),
            "blob": _git(root, "rev-parse", "HEAD:page.md"), "tag": _git(root, "rev-parse", "v1")}


@pytest.fixture
def project(tmp_path):
    ids = _repository(tmp_path / "project")
    shutil.copyfile(REPO / ".gitleaks.toml", tmp_path / "project" / ".gitleaks.toml")
    return tmp_path / "project", ids


def _text(name: str) -> bytes:
    return f"The review names {KEYWORD} at {name} today.\n".encode()


def test_only_a_commit_of_the_project_itself_is_a_commit(project, tmp_path):
    root, ids = project
    other = _repository(tmp_path / "other")
    names = {ids["commit"], ids["tree"], ids["blob"], ids["tag"], other["commit"], os.urandom(20).hex()}
    assert secrets._commits(root, names) == {ids["commit"]}


def test_git_is_asked_of_the_project_whatever_the_environment_names(project, tmp_path, monkeypatch):
    root, ids = project
    other = _repository(tmp_path / "other")
    monkeypatch.setenv("GIT_DIR", str(tmp_path / "other" / ".git"))
    assert secrets._commits(root, {ids["commit"], other["commit"]}) == {ids["commit"]}
    # a folder that is not itself a repository is not answered by the repository above it
    (root / "inner").mkdir()
    assert secrets._commits(root / "inner", {ids["commit"]}) == set()


def test_a_git_that_cannot_answer_answers_nothing(project, monkeypatch):
    root, ids = project
    monkeypatch.setenv("PATH", str(root / "no-such-folder"))
    assert secrets._commits(root, {ids["commit"]}) == set()
    monkeypatch.undo()

    def timing_out(command, **options):
        raise subprocess.TimeoutExpired(command, options["timeout"])

    monkeypatch.setattr(secrets.subprocess, "run", timing_out)
    assert secrets._commits(root, {ids["commit"]}) == set()


def test_only_that_rule_and_exactly_forty_digits_are_candidates(project):
    _, ids = project
    sha = ids["commit"]
    assert secrets._exempt({"RuleID": secrets._COMMIT_RULE, "Secret": sha}, Path(".")) == sha
    assert secrets._exempt({"RuleID": secrets._COMMIT_RULE, "Secret": sha}, None) is None
    assert secrets._exempt({"RuleID": "generic-api-key", "Secret": sha}, Path(".")) is None
    for secret in (sha[:39], sha + "a", sha[:12], "x" + sha[1:]):
        assert secrets._exempt({"RuleID": secrets._COMMIT_RULE, "Secret": secret}, Path(".")) is None


def test_the_scan_passes_a_commit_of_the_project_and_nothing_else(project):
    root, ids = project
    rules = secrets._rules(root)
    assert secrets._holds_secret(rules, _text(ids["commit"]), root) is False
    assert secrets._holds_secret(rules, _text(ids["commit"]), None) is True  # no project named: nothing exempt
    for name in (ids["tree"], ids["blob"], ids["tag"], os.urandom(20).hex()):
        assert secrets._holds_secret(rules, _text(name), root) is True
    assert secrets._holds_secret(rules, _text(ids["commit"]) + _text(os.urandom(20).hex()), root) is True
