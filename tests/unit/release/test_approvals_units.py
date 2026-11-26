"""Unit tests of the ``approved`` kind of the release rule (W2-209 RR-1, RR-2): the inputs that must fail closed."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from gov.release import patch, repin

OWNER = "### DEC-1 — yes\n- **Status:** ACCEPTED (owner, 2026-01-01) · **Under:** none\n"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args], check=True,
                          capture_output=True, text=True).stdout


def commit(repo: Path, files: dict[str, str], message: str) -> str:
    for rel, text in files.items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text(text, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "--allow-empty", "-m", message)
    return git(repo, "rev-parse", "HEAD").strip()


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q", "-b", "main")
    commit(tmp_path, {"pyproject.toml": '[project]\nversion = "0.1.0"\n', "docs/releases/0.1.0/manifest.json": "{}\n",
                      "docs/DECISION_REGISTER.md": OWNER}, "the release")
    git(tmp_path, "tag", "v0.1.0")
    commit(tmp_path, {"pyproject.toml": '[project]\nversion = "0.2.0"\n'}, "version\n\nClass: C")
    return tmp_path


def contract(repo: Path, trailer: str = "Approved-by: DEC-1") -> str:
    return commit(repo, {"docs/contract/c.md": "x\n"}, f"contract\n\n{trailer}")


def test_an_owner_accepted_trailer_makes_the_range_approved(repo):
    sha = contract(repo)
    result = patch.evaluate(repo, "0.2.0")
    assert result["kind"] == "approved"
    assert result["approvals"] == [{"item": f"commit {sha[:12]}", "decisions": ["DEC-1"], "ok": True, "lacks": None}]
    assert patch.kind_record(result)["approvals"] == result["approvals"]


@pytest.mark.parametrize("trailer", ["Approved-by: the owner", "Approved-by: DEC-1,", "Approved-by: DEC-1 DEC-2",
                                     "Approved-by: DEC-1, DEC-2", "Decided-by: owner (chat)"])
def test_a_name_that_does_not_wholly_count_is_bigger(repo, trailer):
    contract(repo, trailer)
    assert patch.evaluate(repo, "0.2.0")["kind"] == "bigger"


@pytest.mark.parametrize("register", [
    OWNER + OWNER.replace("ACCEPTED (owner, 2026-01-01)", "PROPOSED"),  # the id twice, one not the owner's
    "### DEC-1 — yes\n- **Under:** ACCEPTED (owner)\n",  # no status field
    "```\n" + OWNER,  # the entry inside a fence
])
def test_a_register_that_does_not_clearly_hold_the_decision_is_bigger(repo, register):
    commit(repo, {"docs/DECISION_REGISTER.md": register}, "register\n\nClass: C")
    contract(repo)
    assert patch.evaluate(repo, "0.2.0")["kind"] == "bigger"


@pytest.mark.parametrize("front", ["approved_by: [DEC-1\n", "approved_by: 1\n", "approved_by: []\n", "other: x\n"])
def test_a_ticket_whose_approval_cannot_be_read_is_bigger(repo, front):
    commit(repo, {".tickets/t.md": f"---\nid: T-1\nstatus: closed\n{front}---\nbody\n"}, "close")
    result = patch.evaluate(repo, "0.2.0")
    assert result["kind"] == "bigger"
    assert [(a["item"], a["ok"]) for a in result["approvals"]] == [("ticket T-1", False)]


def test_a_command_added_by_a_merge_commit_alone_lacks_a_decision(repo):
    git(repo, "checkout", "-q", "-b", "side")
    commit(repo, {"docs/side.md": "s\n"}, "side\n\nClass: C")
    git(repo, "checkout", "-q", "main")
    git(repo, "merge", "-q", "--no-ff", "--no-commit", "side")
    commit(repo, {"src/gov/evil/command.py": "x = 1\n"}, "merge\n\nApproved-by: DEC-1")
    result = patch.evaluate(repo, "0.2.0")
    assert result["kind"] == "bigger"
    assert [(a["item"], a["ok"]) for a in result["approvals"]] == [("command evil", False)]


def test_tickets_that_cannot_be_read_are_never_a_pass(repo):
    contract(repo)
    git(repo, "update-index", "--add", "--cacheinfo", f"160000,{'1' * 40},.tickets/sub")
    git(repo, "commit", "-q", "-m", "gitlink\n\nApproved-by: DEC-1")
    result = patch.evaluate(repo, "0.2.0")
    assert result["kind"] == "bigger" and result["rules"]["P3"]["pass"] is False


def test_the_push_texts_of_an_approved_release_name_no_patch():
    assert "(approved, 2 fixes)" in repin.push_text("0.2.0", 2, "a" * 40, "READY", kind="approved")
    assert repin.failure_text("0.2.0", "hooks", kind="approved").endswith("CTO cuts the next release.")
    assert len(repin.failure_text("99.99.99", "x" * 400, kind="approved")) <= 190
