"""The governance checks of a close (DEC-454, DEC-480) and a ticket without acceptance tests: W1-26's runner is
the authority on whether the checks block; where it says so, what it reports red (hard-block checks, families)
refuses, through the one failure path."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from gov.cli.errors import GovError
from gov.close import command
from gov.close.command import _GOVERNANCE_PREFIXES, EXIT_CHECK_FAILED, _check_governance, _count_path, run

TICKET = "T-0001"
HEAD = "c" * 40
COUNTS = {"passed": 1, "failed": 0, "errors": 0}
NOTES = "governance/project/notes.yaml"
DECLARATION = "template/governance/kernel/checks/mine.yaml"


def _commit(sha: str, *paths: str) -> dict:
    return {"sha": sha, "trailers": {}, "paths": list(paths)}


def _entry(check_id: str, severity: str, status: str, commit: str = HEAD, findings=()) -> dict:
    return {"id": check_id, "family": "mutation scope", "severity": severity, "status": status,
            "findings": list(findings), "provenance": {"commit": commit, "check_version": "1", "inputs_hash": "x"}}


def _families(**statuses) -> dict:
    return {name.replace("_", " "): {"status": status, "family": name.replace("_", " ")}
            for name, status in statuses.items()}


def _judged(commits, *entries, head=HEAD, blocks=False, families=None):
    """``_check_governance`` with the runner answering ``entries``, ``families`` and ``blocks``, and ``HEAD`` at
    ``head``."""
    result = {"families": families or {}, "checks": list(entries)}
    with patch("gov.check.runner.run_checks", return_value=(result, blocks)) as runner, \
            patch.object(command, "_git", return_value=head + "\n"):
        return _check_governance(Path("/p"), commits), result, runner


def test_no_governance_file_changed_runs_no_check_and_claims_no_result():
    with patch("gov.check.runner.run_checks") as runner:
        assert _check_governance(Path("/p"), [_commit("a", "src/app.py", "template/other/x.yaml")]) == ({}, None)
    runner.assert_not_called()


@pytest.mark.parametrize("prefix", _GOVERNANCE_PREFIXES)
def test_a_change_under_each_governance_prefix_has_the_checks_run(prefix):
    (stated, red), result, runner = _judged([_commit("a", f"{prefix}x.yaml")], _entry("ok", "hard-block", "GREEN"))
    runner.assert_called_once_with(Path("/p"))
    assert stated == {"check_commit": HEAD, "governance_checks": result} and red is None


@pytest.mark.parametrize("paths", [(DECLARATION,), ("template/governance/kernel/checks/another.yaml",), (NOTES,)],
                         ids=["declared-by-the-ticket", "not-touched-by-the-ticket", "no-check-declared"])
def test_any_red_hard_block_check_is_returned_whatever_the_ticket_changed(paths):
    mine = _entry("mine", "hard-block", "RED", findings=[{"code": "CHECK_FAILED"}])
    other = _entry("other", "hard-block", "RED")
    (stated, red), result, _ = _judged([_commit("a", *paths)], mine, _entry("ok", "hard-block", "GREEN"), other,
                                       blocks=True)
    assert red == {"red_checks": [mine, other], "red_families": []}
    assert stated["governance_checks"] is result


@pytest.mark.parametrize("severity, status", [("warning", "YELLOW"), ("warning", "RED"), ("hard-block", "YELLOW"),
                                              ("hard-block", "GREEN")])
def test_a_warning_and_a_yellow_refuse_nothing(severity, status):
    (_, red), _, _ = _judged([_commit("a", NOTES)], _entry("x", severity, status))
    assert red is None


def test_the_runner_s_own_answer_decides_whether_the_checks_block():
    """Not a derivation of this command's: the same result blocks or not as the runner says beside it."""
    entries = (_entry("mine", "hard-block", "RED"),)
    families = _families(mutation_scope="RED")
    (_, quiet), _, _ = _judged([_commit("a", NOTES)], *entries, families=families, blocks=False)
    (_, loud), _, _ = _judged([_commit("a", NOTES)], *entries, families=families, blocks=True)
    assert quiet is None
    assert loud == {"red_checks": list(entries), "red_families": ["mutation scope"]}


def test_a_red_family_without_a_red_hard_block_check_is_what_blocks():
    families = _families(licence_hygiene="RED", graph_integrity="GREEN", wanted="YELLOW", another="RED")
    (_, red), _, _ = _judged([_commit("a", NOTES)], _entry("ok", "hard-block", "GREEN"), families=families,
                             blocks=True)
    assert red == {"red_checks": [], "red_families": ["another", "licence hygiene"]}


def test_a_declaration_changed_in_two_commits_is_judged_by_the_run_alone():
    (stated, red), _, runner = _judged([_commit("b", DECLARATION), _commit("a", DECLARATION)],
                                       _entry("mine", "hard-block", "GREEN"))
    runner.assert_called_once()
    assert red is None and stated["check_commit"] == HEAD


@pytest.mark.parametrize("entries", [(_entry("x", "hard-block", "GREEN", commit="d" * 40),),
                                     (_entry("x", "hard-block", "GREEN"), _entry("y", "warning", "GREEN", "unknown")),
                                     ()], ids=["another-commit", "one-check-elsewhere", "no-check"])
def test_a_result_that_is_not_of_the_commit_being_closed_is_an_error(entries):
    with pytest.raises(GovError) as raised:
        _judged([_commit("a", NOTES)], *entries)
    assert (raised.value.code, raised.value.exit_code) == ("CHECKS_NOT_MEASURED", 1)
    assert HEAD in raised.value.message


@pytest.mark.parametrize("result", [{}, {"checks": [{"id": "x", "status": "RED"}]}, {"checks": ["x"]}, None,
                                    {"checks": [_entry("x", "hard-block", "GREEN")]},
                                    {"checks": [_entry("x", "hard-block", "GREEN")], "families": ["x"]},
                                    {"checks": [_entry("x", "hard-block", "GREEN")], "families": {"x": {}}}])
def test_a_result_of_another_shape_is_an_error(result):
    with patch("gov.check.runner.run_checks", return_value=(result, False)), \
            patch.object(command, "_git", return_value=HEAD + "\n"):
        with pytest.raises(GovError) as raised:
            _check_governance(Path("/p"), [_commit("a", NOTES)])
    assert raised.value.code == "CHECKS_NOT_MEASURED"


def test_an_error_of_the_runner_is_not_caught():
    with patch("gov.check.runner.run_checks", side_effect=GovError("CHECKS_INVALID", "a broken declaration")), \
            patch.object(command, "_git", return_value=HEAD + "\n"):
        with pytest.raises(GovError) as raised:
            _check_governance(Path("/p"), [_commit("a", NOTES)])
    assert raised.value.code == "CHECKS_INVALID"


# ---- through the one failure path (DEC-455, DEC-480) ----

def _close(root, *, tests=True, entries=(), test_findings=(), families=None, blocks=True):
    """``run`` on the conftest's project: the gates before the tests pass, the test runs answer
    ``test_findings``, the runner answers ``entries``, ``families`` and ``blocks``."""
    if tests is not None:
        folder = root / "tests" / "acceptance" / TICKET / ("" if tests else "notes")
        folder.mkdir(parents=True)
        (folder / ("test_a.py" if tests else "README.md")).write_text("", encoding="utf-8")
    args = SimpleNamespace(ticket=TICKET, disposition=None, owner_decision=None, timeout=None)
    with patch.object(command, "_ticket_commits", return_value=[_commit(HEAD, NOTES)]), \
            patch.object(command, "_check_trailers"), patch.object(command, "_check_containment"), \
            patch.object(command, "_run_tests", return_value=(list(test_findings), dict(COUNTS))) as ran, \
            patch.object(command, "_git", return_value=HEAD + "\n"), \
            patch("gov.check.runner.run_checks",
                  return_value=({"families": families or {}, "checks": list(entries)}, blocks)):
        with pytest.raises(GovError) as raised:
            run(root, args, {})
    return raised.value, ran


def _counted(root):
    return json.loads(_count_path(root, TICKET).read_text(encoding="utf-8"))


def test_a_red_hard_block_check_refuses_counted_with_a_repair_ticket_and_is_named(root):
    red = _entry("license-present", "hard-block", "RED", findings=[{"code": "CHECK_FAILED", "stderr": "no-tool"}])
    error, _ = _close(root, entries=[red, _entry("wanted", "warning", "YELLOW")])
    assert (error.code, error.exit_code) == ("CHECK_FAILED", EXIT_CHECK_FAILED)
    assert error.details["red_checks"] == [red] and error.details["check_commit"] == HEAD
    [finding] = error.details["findings"]
    assert "license-present" in finding and HEAD[:12] in finding and "no-tool" in finding and "wanted" not in finding
    assert _counted(root)["count"] == 1 and _counted(root)["last_failures"] == [finding]
    assert (root / ".tickets" / f"{error.details['repair_ticket']}.md").is_file()
    assert not (root / "docs" / "close").exists()


def test_a_red_family_without_a_red_check_refuses_counted_with_a_repair_ticket_and_is_named(root):
    error, _ = _close(root, entries=[_entry("feature-present", "hard-block", "GREEN")],
                      families=_families(licence_hygiene="RED", graph_integrity="GREEN"))
    assert (error.code, error.exit_code) == ("CHECK_FAILED", EXIT_CHECK_FAILED)
    assert error.details["red_checks"] == [] and error.details["red_families"] == ["licence hygiene"]
    assert error.details["check_commit"] == HEAD
    [finding] = error.details["findings"]
    assert "licence hygiene" in finding and HEAD[:12] in finding and "graph integrity" not in finding
    assert _counted(root)["count"] == 1 and _counted(root)["last_failures"] == [finding]
    assert (root / ".tickets" / f"{error.details['repair_ticket']}.md").is_file()
    assert not (root / "docs" / "close").exists()


def test_a_block_the_runner_names_nothing_for_still_refuses(root):
    error, _ = _close(root, entries=[_entry("ok", "hard-block", "GREEN")])
    assert error.code == "CHECK_FAILED" and error.details["red_checks"] == error.details["red_families"] == []
    [finding] = error.details["findings"]
    assert "block" in finding and HEAD[:12] in finding


def test_a_red_check_and_a_failing_test_are_one_refusal(root):
    error, _ = _close(root, entries=[_entry("a", "hard-block", "RED")], test_findings=["FAILED test_a"])
    assert len(error.details["findings"]) == 3 and _counted(root)["count"] == 1  # two test runs, one check
    assert len(list((root / ".tickets").glob("*.md"))) == 2


@pytest.mark.parametrize("tests", [None, False], ids=["no-folder", "folder-without-a-test"])
def test_a_ticket_without_acceptance_tests_refuses_counted_with_a_repair_ticket(root, tests):
    error, ran = _close(root, tests=tests)
    assert (error.code, error.exit_code) == ("NO_ACCEPTANCE_TESTS", EXIT_CHECK_FAILED)
    assert "acceptance" in error.message
    ran.assert_not_called()
    assert _counted(root)["count"] == 1
    assert (root / ".tickets" / f"{error.details['repair_ticket']}.md").is_file()
