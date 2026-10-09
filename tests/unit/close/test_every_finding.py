"""One run reports every finding (DEC-492): every gate is asked whatever an earlier one found; the one refusal
names each finding once, is counted once and opens one repair ticket; what a finding left unmeasurable is named
as not measured; "could not measure" still ends the run at once, uncounted."""
from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from gov.cli.errors import GovError
from gov.close import command
from gov.close.command import (EXIT_CHECK_FAILED, _check_acceptance, _check_checkpoint, _check_containment,
                               _check_tests, _check_trailers, _check_unmeasured, _count_path, _Finding,
                               _refuse_for, run)
from gov.tasks.tickets import frontmatter

TICKET = "T-0001"
COUNTS = {"passed": 1, "failed": 0, "errors": 0}
WHOLE = {"Task": [TICKET], "Role": ["engineer"], "Implements": ["CAP-01"]}
NO_ACCEPTANCE_RUN = f"the acceptance run of {TICKET}: not measured, it has no acceptance tests"


def _commit(letter, *paths, **without):
    return {"sha": letter * 40, "parents": [], "paths": list(paths),
            "trailers": {key: value for key, value in WHOLE.items() if key not in without}}


def _counted(root):
    return json.loads(_count_path(root, TICKET).read_text(encoding="utf-8"))


def _tickets(root):
    return sorted(path for path in (root / ".tickets").glob("*.md") if path.stem != TICKET)


# ---- each gate gives all of its findings ----

def test_every_trailer_a_commit_lacks_is_a_finding():
    with pytest.raises(_Finding) as raised:
        _check_trailers([_commit("a", Implements=0), _commit("b"), _commit("c", Role=0, Implements=0)], TICKET)
    assert raised.value.findings == [f"commit {'a' * 12} lacks Implements: trailer",
                                     f"commit {'c' * 12} lacks Implements: trailer",
                                     f"commit {'c' * 12} lacks Role: trailer"]
    assert raised.value.details["commits"] == ["a" * 12, "c" * 12] and not raised.value.not_measured


def test_a_ticket_without_a_commit_says_that_its_containment_was_not_measured():
    with pytest.raises(_Finding) as raised:
        _check_trailers([], TICKET)
    assert raised.value.not_measured == [f"the containment of the commits of {TICKET}: not measured, it has no commit"]
    with patch("gov.guard.containment.judge_commits") as judge:
        _check_containment("/p", [])
    judge.assert_not_called()


def test_every_commit_without_a_task_on_the_tickets_work_is_a_finding():
    others = [{"sha": letter * 40, "trailers": {}, "paths": [f"src/{letter}.py", "README.md"]} for letter in "ab"]
    with pytest.raises(_Finding) as raised:
        _check_unmeasured(TICKET, others, lambda path: path.startswith("src/"), frozenset({TICKET}))
    assert len(raised.value.findings) == 2 and all("names no task" in line for line in raised.value.findings)
    assert raised.value.details["work_without_task"] == [{"commit": "a" * 12, "paths": ["src/a.py"]},
                                                         {"commit": "b" * 12, "paths": ["src/b.py"]}]


def test_a_test_run_with_findings_is_a_finding_of_the_tickets_work(tmp_path):
    with patch.object(command, "_run_tests", return_value=(["FAILED test_a"], dict(COUNTS))) as ran:
        with pytest.raises(_Finding) as raised:
            _check_tests(tmp_path, tmp_path / "tests", 60, tmp_path / "ignored")
    assert (raised.value.code, raised.value.findings) == ("CHECK_FAILED", ["FAILED test_a"])
    assert ran.call_args.kwargs == {"ignore": tmp_path / "ignored", "none_collected_ok": True, "stated": None,
                                    "workers": "auto"}
    stated = []
    with patch.object(command, "_run_tests", return_value=([], dict(COUNTS))) as ran:
        assert _check_tests(tmp_path, tmp_path / "tests", 60, stated=stated, workers=2) == COUNTS
    assert ran.call_args.kwargs == {"ignore": None, "none_collected_ok": False, "stated": stated, "workers": 2}


def test_without_acceptance_tests_no_run_is_made_and_it_is_said_as_not_measured(tmp_path):
    with patch.object(command, "_run_tests") as ran:
        with pytest.raises(_Finding) as raised:
            _check_acceptance(tmp_path, TICKET, "W1-01", 60)
    ran.assert_not_called()
    assert raised.value.code == "NO_ACCEPTANCE_TESTS" and raised.value.not_measured == [NO_ACCEPTANCE_RUN]


def test_the_watchdogs_error_is_a_finding_with_its_own_code_and_exit_code(tmp_path):
    stale = GovError("CHECKPOINT_STALE", "stale: age", {"reasons": ["age"]}, exit_code=5)
    with patch("gov.checkpoint.record.watch", side_effect=stale):
        with pytest.raises(_Finding) as raised:
            _check_checkpoint(tmp_path, TICKET)
    assert (raised.value.code, raised.value.exit_code, raised.value.details) == (
        "CHECKPOINT_STALE", 5, {"reasons": ["age"]})


def test_the_probe_gate_ends_at_its_first_finding_and_says_what_it_did_not_ask(repo):
    repo.commit("work", f"Task: {TICKET}", "Role: engineer", "Implements: CAP-01",
                files={f"docs/probes/{TICKET}/PR.md": "---\nnot valid yaml: [[[broken\n---\n"})
    with pytest.raises(_Finding) as raised:
        command._check_probe(repo.root, TICKET, command._ticket_commits(repo.root, TICKET), [], lambda path: True,
                             lambda path: True, frozenset({TICKET}))
    assert raised.value.code == "PROBE_INVALID"
    [said] = raised.value.not_measured
    assert said.startswith(f"what the probe gate of {TICKET} asks after this finding: not measured")


# ---- the one refusal ----

def _refused(root, found, disposition=None, packet=None):
    with pytest.raises(GovError) as raised:
        _refuse_for(root, TICKET, found, disposition, packet)
    return raised.value


def test_one_gates_refusal_is_that_gates(root):
    error = _refused(root, [_Finding("CHECKPOINT_STALE", "stale", {"reasons": ["age"]}, exit_code=5)])
    assert (error.code, error.exit_code) == ("CHECKPOINT_STALE", 5) and error.message.startswith("stale")
    assert error.details["reasons"] == ["age"] and error.details["findings"] == ["stale"]
    assert "parts" not in error.details and "not_measured" not in error.details


def test_several_gates_are_one_refusal_counted_once_with_one_repair_ticket_that_lists_them_all(root):
    found = [_Finding("TRAILER_MISSING", "a; b", {"commit": "a"}, ["commit a lacks Role:", "commit b lacks Role:"]),
             _Finding("NO_ACCEPTANCE_TESTS", "no acceptance tests", not_measured=[NO_ACCEPTANCE_RUN]),
             _Finding("CHECK_FAILED", "tests or checks failed", {"tests_run": COUNTS}, ["FAILED test_x"]),
             _Finding("CHECK_FAILED", "tests or checks failed", {"check_commit": "c"}, ["FAILED test_x", "check red"])]
    error = _refused(root, found)
    lines = ["commit a lacks Role:", "commit b lacks Role:", "no acceptance tests", "FAILED test_x", "check red"]
    assert (error.code, error.exit_code) == ("CHECK_FAILED", EXIT_CHECK_FAILED)
    assert error.details["findings"] == lines and error.message.startswith("5 findings refuse the close")
    assert [part["code"] for part in error.details["parts"]] == [f.code for f in found]
    assert error.details["parts"][0]["commit"] == "a" and error.details["parts"][3]["check_commit"] == "c"
    assert error.details["not_measured"] == [NO_ACCEPTANCE_RUN]
    assert _counted(root)["count"] == 1 and _counted(root)["last_failures"] == sorted(lines)
    [repair] = _tickets(root)
    assert error.details["repair_ticket"] == repair.stem
    text = repair.read_text(encoding="utf-8")
    assert all(f"- {line}" in text for line in lines) and f"- {NO_ACCEPTANCE_RUN}" in text
    assert text.count("FAILED test_x") == 1


def test_gates_with_one_code_keep_it(root):
    error = _refused(root, [_Finding("CHECK_FAILED", "tests or checks failed", None, ["FAILED a"]),
                            _Finding("CHECK_FAILED", "tests or checks failed", None, ["FAILED b"])])
    assert error.code == "CHECK_FAILED" and error.message.startswith("tests or checks failed")


def test_without_a_class_the_findings_await_it_and_no_context_hash_is_recorded(root):
    error = _refused(root, [_Finding("CHECK_FAILED", "tests or checks failed")], packet={"hash": "ab" * 32})
    assert error.details["disposition"] == "unclassed" and "disposition" in error.details["note"]
    assert error.message.endswith("await disposition")
    assert "context_hash" not in frontmatter(_tickets(root)[0])


def test_with_a_class_the_repair_ticket_has_the_context_hash(root):
    error = _refused(root, [_Finding("CHECK_FAILED", "tests or checks failed")], "narrow", {"hash": "ab" * 32})
    assert error.details["disposition"] == "narrow" and "note" not in error.details
    front = frontmatter(_tickets(root)[0])
    assert (front["disposition"], front["context_hash"]) == ("narrow", "ab" * 32)


def test_with_a_class_a_context_that_failed_is_a_finding_and_is_named_on_the_repair_ticket(root):
    error = _refused(root, [_Finding("CHECK_FAILED", "tests or checks failed", None, ["FAILED a"]),
                            _Finding("CONTEXT_FAILED", "the context cannot be built: no store")], "repair")
    assert error.details["findings"] == ["FAILED a", "the context cannot be built: no store"]
    assert error.details["context"] == "the context cannot be built: no store"
    text = _tickets(root)[0].read_text(encoding="utf-8")
    assert "without whole-system context: the context cannot be built: no store" in text
    assert "context_hash" not in frontmatter(_tickets(root)[0])


# ---- the run asks every gate ----

GATES = ("_check_trailers", "_check_unmeasured", "_check_containment", "_check_acceptance", "_check_tests",
         "_check_governance_blocks", "_check_checkpoint", "_build_context")


def _run(root, **answers):
    """``run`` on the conftest's project with every gate patched: each passes unless ``answers`` names what it
    raises. Returns the error and the gates that were asked, in order."""
    asked = []

    def gate(name):
        def check(*given):
            asked.append(name)
            if name in answers:
                raise answers[name]
            return {"_check_acceptance": dict(COUNTS), "_check_tests": dict(COUNTS),
                    "_build_context": {"hash": "h", "mandatory": []}}.get(name, {})
        return check

    args = SimpleNamespace(ticket=TICKET, disposition=None, owner_decision=None, timeout=None)
    with patch.object(command, "_ticket_commits", return_value=[_commit("a", "src/example/a.py")]), \
            patch.object(command, "_commits_since", return_value=[]), patch.object(command, "_check_tree"), \
            patch.multiple(command, **{name: gate(name) for name in GATES}):
        with pytest.raises(GovError) as raised:
            run(root, args, {})
    return raised.value, asked


@pytest.mark.parametrize("early", GATES[:4])
def test_an_early_finding_does_not_end_the_run(root, early):
    error, asked = _run(root, **{early: _Finding("EARLY", "the early finding"),
                                 "_check_tests": _Finding("CHECK_FAILED", "tests or checks failed", None,
                                                          ["FAILED test_fail"])})
    assert asked == list(GATES)
    assert error.details["findings"] == ["the early finding", "FAILED test_fail"]
    assert (error.code, error.exit_code) == ("CHECK_FAILED", EXIT_CHECK_FAILED)
    assert _counted(root)["count"] == 1 and len(_tickets(root)) == 1
    assert frontmatter(root / ".tickets" / f"{TICKET}.md")["status"] == "in_progress"
    assert not (root / "docs" / "close").exists()


def test_a_finding_of_every_gate_is_in_the_one_refusal(root):
    error, asked = _run(root, **{name: _Finding(name.upper(), f"finding of {name}") for name in GATES})
    assert asked == list(GATES) and error.details["findings"] == [f"finding of {name}" for name in GATES]
    assert _counted(root)["count"] == 1 and len(_tickets(root)) == 1


@pytest.mark.parametrize("failing", GATES)
def test_could_not_measure_ends_the_run_at_once_uncounted_whatever_was_found_before(root, failing):
    answers = {name: _Finding("EARLY", f"finding of {name}") for name in GATES[:GATES.index(failing)]}
    error, asked = _run(root, **answers, **{failing: GovError("GIT_FAILURE", "planted")})
    assert (error.code, error.exit_code) == ("GIT_FAILURE", 1)
    assert asked == list(GATES[:GATES.index(failing) + 1])
    assert not _count_path(root, TICKET).exists() and not _tickets(root)


def test_a_full_ticket_has_its_probe_gate_asked_first_and_its_finding_beside_the_others(root):
    path = root / ".tickets" / f"{TICKET}.md"
    path.write_text(path.read_text(encoding="utf-8").replace("priority: 2\n", "priority: 2\nprofile: FULL\n"),
                    encoding="utf-8")
    error, asked = _run(root, _check_tests=_Finding("CHECK_FAILED", "tests or checks failed", None, ["FAILED t"]))
    assert asked == list(GATES)
    assert [part["code"] for part in error.details["parts"]] == ["PROBE_MISSING", "CHECK_FAILED"]
    assert _counted(root)["count"] == 1
