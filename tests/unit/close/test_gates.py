"""The gates of a close: containment as W1-50 judges it, the probe record, the commits and their models."""
from __future__ import annotations

from collections import namedtuple
from unittest.mock import patch

import pytest
import yaml

from gov.cli.errors import GovError
from gov.close import command
from gov.close import repo as close_repo
from gov.close.command import (NOT_MEASURED, _check_containment, _check_probe, _check_trailers, _commit_models,
                               _commits_since, _Finding, _git, _ticket_commits)
from gov.guard.containment import ContainmentError

TICKET = "T-0001"
TRAILERS = (f"Task: {TICKET}", "Role: engineer", "Implements: CAP-01")
Judged = namedtuple("Judged", "commit paths reason")


# ---- containment (DEC-453) ----

@pytest.mark.parametrize("path", ["docs/close/T-0001/CL.md", ".tickets/T-0002.md", "tests/unit/test_x.py",
                                  "governance/project/x.md", "template/a.md", "README.md", "src/in/paths.py"])
def test_every_finding_of_the_judgement_refuses_as_returned(path):
    judged = [Judged("c" * 40, [path], "outside the ticket's paths")]
    with patch("gov.guard.containment.judge_commits", return_value=judged) as judge:
        with pytest.raises(_Finding) as raised:
            _check_containment("/p", [{"sha": "c" * 40}])
    judge.assert_called_once_with("/p", ["c" * 40])
    assert raised.value.code == "CONTAINMENT_FINDING"
    assert raised.value.details["containment"] == [
        {"commit": "c" * 40, "paths": [path], "reason": "outside the ticket's paths"}]
    assert path in raised.value.message and "c" * 12 in raised.value.message
    assert "outside the ticket's paths" in raised.value.message


def test_no_finding_passes():
    with patch("gov.guard.containment.judge_commits", return_value=[]):
        _check_containment("/p", [{"sha": "c" * 40}])


def test_a_judgement_that_cannot_run_is_an_error_not_a_pass():
    with patch("gov.guard.containment.judge_commits", side_effect=ContainmentError("git failed")):
        with pytest.raises(GovError) as raised:
            _check_containment("/p", [{"sha": "c" * 40}])
    assert raised.value.code == "CONTAINMENT_ERROR" and "git failed" in raised.value.message


def test_the_command_has_no_rule_of_its_own():
    assert not hasattr(command, "_is_close_infra") and not hasattr(command, "_GOV_DOC_PREFIXES")
    assert "fnmatch" not in open(command.__file__, encoding="utf-8").read()


# ---- commits, trailers and models (DEC-470) ----

def test_a_git_failure_is_an_error(tmp_path):
    with pytest.raises(GovError) as raised:
        _ticket_commits(tmp_path, TICKET)
    assert raised.value.code == "GIT_FAILURE"


def test_an_exit_code_outside_the_expected_ones_is_an_error(repo):
    repo.commit()
    assert _git(repo.root, "rev-parse", "--verify", "--quiet", "0" * 40 + "^{commit}", ok=(0, 1), code=True) == 1
    with pytest.raises(GovError):
        _git(repo.root, "merge-base", "--is-ancestor", "0" * 40, "HEAD", ok=(0, 1), code=True)


def test_the_tickets_commits_are_those_whose_task_trailer_is_the_ticket(repo):
    repo.commit("another ticket", f"Task: {TICKET}0", "Role: engineer")
    mine = repo.commit("mine", *TRAILERS, files={"src/a.py": "a\n"})
    repo.commit(f"no trailer, but the text Task: {TICKET}")
    commits = _ticket_commits(repo.root, TICKET)
    assert [(c["sha"], c["paths"]) for c in commits] == [(mine, ["src/a.py"])]
    assert commits[0]["trailers"]["Implements"] == ["CAP-01"]


def test_missing_trailers_are_findings():
    with pytest.raises(_Finding):
        _check_trailers([], TICKET)
    with pytest.raises(_Finding):
        _check_trailers([{"sha": "a" * 40, "trailers": {"Task": [TICKET]}}], TICKET)


def test_each_commit_is_listed_with_its_role_and_the_model_of_its_line_as_read(repo):
    line = "Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
    first = repo.commit("tests", f"Task: {TICKET}", "Role: independent-test-designer", f"Co-Authored-By: {line}")
    second = repo.commit("code", *TRAILERS)
    third = repo.commit("no role", f"Task: {TICKET}", "Co-authored-by: Someone <s@example.invalid>")
    assert _commit_models(_ticket_commits(repo.root, TICKET)) == [
        {"commit": first, "role": "independent-test-designer", "model": line},
        {"commit": second, "role": "engineer", "model": NOT_MEASURED},
        {"commit": third, "role": NOT_MEASURED, "model": "Someone <s@example.invalid>"},
    ]


# ---- the probe gate (A5, DEC-137) ----

def _probe(repo, probed, **keys):
    front = {"id": f"PR-{TICKET}", "type": "probe", "task": TICKET, "reviewer_session": "reviewer-001",
             "implementer_session": "impl-001", "reviewer_wrote_nothing": True, "commissioned_by": "orchestrator",
             "judged_by": "orchestrator", "judgement": "pass", "probed_commit": probed, **keys}
    front = {key: value for key, value in front.items() if value is not None}
    repo.commit("the probe record", "Role: orchestrator",
                files={f"docs/probes/{TICKET}/PR.md": "---\n" + yaml.safe_dump(front) + "---\n\n# Probe\n"})


def _inside(path):
    return path.startswith("src/")


def _own(path):
    return _inside(path) or path == f".tickets/{TICKET}.md" or path.startswith(f"tests/acceptance/{TICKET}/")


def _gate(repo):
    commits = _ticket_commits(repo.root, TICKET)
    _check_probe(repo.root, TICKET, commits, _commits_since(repo.root, commits), _inside, _own, frozenset({TICKET}))


def _refused(repo):
    with pytest.raises(_Finding) as raised:
        _gate(repo)
    return raised.value


def test_a_valid_probe_passes(repo):
    _probe(repo, repo.commit("work", *TRAILERS, files={"src/a.py": "a\n"}))
    _gate(repo)


def test_no_probe_record_is_a_finding(repo):
    repo.commit("work", *TRAILERS)
    assert _refused(repo).code == "PROBE_MISSING"


@pytest.mark.parametrize("session", [(), ("Session: reviewer-001",)])
def test_a_reviewers_commit_of_the_ticket_before_the_probed_commit_refuses(repo, session):
    repo.commit("work", *TRAILERS, files={"src/a.py": "a\n"})
    reviewers = repo.commit("the reviewer", f"Task: {TICKET}", "Role: independent-auditor", "Implements: CAP-01",
                            *session)
    _probe(repo, reviewers)
    finding = _refused(repo)
    assert "reviewer's role" in finding.message and reviewers[:12] in finding.message


def test_a_reviewers_commit_after_the_probed_commit_refuses(repo):
    _probe(repo, repo.commit("work", *TRAILERS, files={"src/a.py": "a\n"}))
    reviewers = repo.commit("the reviewer", "Role: independent-auditor")
    assert reviewers[:12] in str(_refused(repo).details)


def test_a_ticket_commit_naming_the_reviewers_session_refuses(repo):
    work = repo.commit("work", *TRAILERS, "Session: reviewer-001", files={"src/a.py": "a\n"})
    _probe(repo, work)
    assert "reviewer session" in _refused(repo).message


@pytest.mark.parametrize("path", ["src/b.py", f"tests/acceptance/{TICKET}/test_a.py", f".tickets/{TICKET}.md"])
def test_ticket_work_after_the_probed_commit_refuses_and_a_path_outside_it_does_not(repo, path):
    """DEC-581: the ticket's allowed paths, its acceptance tests and its own file refuse; nothing else does."""
    _probe(repo, repo.commit("work", *TRAILERS, files={"src/a.py": "a\n"}))
    repo.commit("outside the ticket's work", *TRAILERS, files={
        "docs/residuals.md": "n\n", "tests/unit/test_a.py": "def test_a(): pass\n",
        f"tests/acceptance/{TICKET}0/test_a.py": "def test_a(): pass\n", ".tickets/T-0002.md": "t\n"})
    _gate(repo)
    later = repo.commit("one inside, one outside", *TRAILERS, files={"docs/a-note.md": "n\n", path: "b\n"})
    finding = _refused(repo)
    assert finding.details["path"] == path and later[:12] in finding.message
    assert "docs/a-note.md" not in finding.message


def test_a_probed_commit_that_is_no_commit_or_no_ancestor_refuses(repo):
    work = repo.commit("work", *TRAILERS, files={"src/a.py": "a\n"})
    _probe(repo, "0" * 40)
    assert "not an ancestor" in _refused(repo).message
    repo.git("checkout", "-q", "-b", "side", work)
    aside = repo.commit("aside")
    repo.git("checkout", "-q", "main")
    _probe(repo, aside)
    assert "not an ancestor" in _refused(repo).message


@pytest.mark.parametrize("keys", [{"commissioned_by": "engineer"}, {"judged_by": "engineer"}, {"judgement": " "},
                                  {"reviewer_wrote_nothing": False}, {"reviewer_wrote_nothing": None},
                                  {"implementer_session": "reviewer-001"}, {"probed_commit": None}])
def test_a_probe_record_that_does_not_hold_what_it_must_refuses(repo, keys):
    _probe(repo, repo.commit("work", *TRAILERS, files={"src/a.py": "a\n"}), **keys)
    assert _refused(repo).code == "PROBE_INVALID"


def test_a_probe_file_that_cannot_be_read_refuses(repo):
    repo.commit("work", *TRAILERS,
                files={f"docs/probes/{TICKET}/PR.md": "---\nnot valid yaml: [[[broken\n---\n"})
    assert "frontmatter" in _refused(repo).message


def test_a_git_failure_while_the_probes_commits_are_read_is_an_error_not_a_finding(repo, monkeypatch):
    probed = repo.commit("work", *TRAILERS, files={"src/a.py": "a\n"})
    _probe(repo, probed)
    commits = _ticket_commits(repo.root, TICKET)
    real = close_repo.git

    for calls_before_the_failure in range(3):
        seen = []

        def counting(root, *args, **keys):
            named = any(probed in argument for argument in args)
            seen.append(named)
            if named and sum(seen) > calls_before_the_failure:
                raise GovError("GIT_FAILURE", "planted")
            return real(root, *args, **keys)

        monkeypatch.setattr(command, "_git", counting)
        monkeypatch.setattr(close_repo, "git", counting)
        with pytest.raises(GovError) as raised:
            _check_probe(repo.root, TICKET, commits, [], _inside, _own, frozenset({TICKET}))
        assert raised.value.code == "GIT_FAILURE"
        assert sum(seen) == calls_before_the_failure + 1
