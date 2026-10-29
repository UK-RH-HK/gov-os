"""KPI success 3 (and the "green here" half of KPI success 4): ``gov check`` on this repository gives
context-reproducibility green, and core-schema green, against the store the lead built [DEC-768].

These cases need this worktree's store. One ``gov check --json`` runs for the module (about six minutes at a
load of 12 to 21 on 20 processors), in this worktree, with this worktree's ``src/`` on ``PYTHONPATH``.

Rewrite-Reason: W2-L429 (W2-75, DEC-937; README, "W2-75"). Inside a close (``GOV_CLOSE_CHECK_RESULT`` set) the
fixture reads the envelope of gate (b)'s ``gov check --json`` that the pinned close hands its runs, run on the same
commit in the same tree after the rebuild, and starts no ``gov check``; outside a close it runs ``gov check`` as
above. A result that is missing or not gov check's envelope with its checks fails the cases, naming the file. The
last four cases prove those routes with planted envelopes; none of them runs a real ``gov check``.

Red reasons, today: context-reproducibility is RED ("did not end within its time limit of 60 seconds"), and
core-schema is RED (``SCHEMA_INVALID_TYPE`` on ``docs/audit/wave-1/W1-43-wave-1-exit-audit.md``).
"""

from __future__ import annotations

import json
import os
import subprocess

import pytest

import w2_54_support as S


def test_the_suite_runs_this_worktree_s_code(code_under_test):
    """DEC-732: ``gov`` is imported from this worktree's ``src/``."""
    assert code_under_test.startswith(str(S.SRC)), code_under_test


def test_gov_check_gives_context_reproducibility_green_here(gov_check_here):
    """*Red.* The context-reproducibility check, in ``gov check --json`` on this repository, is GREEN. In a close,
    that ``gov check`` is gate (b)'s, whose output the close hands this run (README, "W2-75")."""
    done, checks = gov_check_here
    entry = checks.get(S.CONTEXT_CHECK_ID)
    assert entry is not None, f"gov check lists no {S.CONTEXT_CHECK_ID}\n{done.describe(1500)}"
    assert entry.get("status") == S.GREEN, \
        f"{S.CONTEXT_CHECK_ID} is {entry.get('status')} here: {S.canonical(entry.get('findings'))[:3000]}"
    assert entry.get("severity") == "hard-block"


def test_gov_check_gives_core_schema_green_here(gov_check_here):
    """*Red.* Core-schema, in ``gov check --json`` on this repository, is GREEN. In a close, that ``gov check`` is
    gate (b)'s, whose output the close hands this run (README, "W2-75")."""
    done, checks = gov_check_here
    entry = checks.get(S.CORE_SCHEMA_ID)
    assert entry is not None, f"gov check lists no {S.CORE_SCHEMA_ID}\n{done.describe(1500)}"
    assert entry.get("status") == S.GREEN, \
        f"{S.CORE_SCHEMA_ID} is {entry.get('status')} here: {S.canonical(entry.get('findings'))[:3000]}"
    assert entry.get("severity") == "hard-block"


def test_the_w1_43_audit_report_is_untouched(gov_check_here):
    """The W1-43 audit report is byte for byte as it was, after ``gov check`` too: its sha256 is
    ``b14e17d6...cdac1d`` (DEC-768 item 1). Passes today.

    In a close, the ``gov check`` it follows is gate (b)'s: the queue runs it in this same tree, on the commit being
    closed, after the rebuild and before the close starts any test run, and the close hands its output to this run
    through the fixture. So the report is read here after that ``gov check`` has run in this tree, as outside a
    close it is read after the fixture's own (README, "W2-75")."""
    assert S.sha256(S.REPO_ROOT / S.W1_43_REL) == S.W1_43_SHA256
    assert (S.REPO_ROOT / S.W1_43_REL).read_bytes() == S.show(S.BASE_COMMIT, S.W1_43_REL)


# --------------------------------------------------------------------------
# W2-75 (DEC-937): the fixture's routes, proved with planted envelopes (no real gov check)
# --------------------------------------------------------------------------

def _envelope(checks, ok=True, command="check"):
    if ok:
        return {"ok": True, "command": command, "result": {"checks": checks}, "session": None}
    return {"ok": False, "command": command, "result": {}, "session": None,
            "error": {"code": "CHECK_FAILED", "message": "a check is red", "details": {"checks": checks}}}


def _check(check_id, status=S.GREEN, severity="hard-block"):
    return {"id": check_id, "status": status, "severity": severity, "findings": []}


GREEN_CHECKS = [_check(S.CONTEXT_CHECK_ID), _check(S.CORE_SCHEMA_ID), _check("secrets-indexing", S.RED)]


@pytest.fixture()
def no_process(monkeypatch):
    """Every process this test's interpreter would start is refused and recorded instead."""
    started = []

    def refuse(*args, **kwargs):
        started.append(args[0] if args else kwargs.get("args"))
        raise AssertionError(f"a process was started: {started[-1]}")

    monkeypatch.setattr(subprocess, "Popen", refuse)
    monkeypatch.setattr(os, "system", refuse)
    return started


def test_in_a_close_the_fixture_reads_the_check_result_and_starts_no_gov_check(tmp_path, no_process):
    """KPI success 1 (W2-75): with GOV_CLOSE_CHECK_RESULT naming gate (b)'s envelope, the fixture's route reads that
    file, a passing run's and a failing run's alike, and starts no process."""
    for name, envelope in (("passing", _envelope(GREEN_CHECKS)), ("failing", _envelope(GREEN_CHECKS, ok=False))):
        result = tmp_path / f"check-result-{name}.json"
        result.write_text(json.dumps(envelope) + "\n", encoding="utf-8")
        done, checks = S.green_here_check({S.CHECK_RESULT_VARIABLE: str(result)})
        assert no_process == [], f"the fixture started a process in a close: {no_process}"
        assert checks == {check["id"]: check for check in GREEN_CHECKS}, f"{name}: {checks}"
        assert str(result) in done.describe(), f"{name}: the result does not name its file: {done.describe()}"


def test_outside_a_close_the_fixture_runs_gov_check_in_this_worktree(monkeypatch):
    """KPI success 2 (W2-75): with GOV_CLOSE_CHECK_RESULT unset or empty, the fixture's route runs ``gov check --json``
    in this worktree, with this worktree's ``src/`` and the same timeout as before (1800 s)."""
    calls = []

    class Done:
        stdout = json.dumps(_envelope(GREEN_CHECKS))

        def envelope(self):
            return json.loads(self.stdout)

    def spy(argv, *, cwd, env, timeout):
        calls.append((list(argv), cwd, env.get("PYTHONPATH"), timeout))
        return Done()

    monkeypatch.setattr(S, "run", spy)
    for environ in ({}, {S.CHECK_RESULT_VARIABLE: ""}):
        calls.clear()
        _, checks = S.green_here_check(environ)
        assert len(calls) == 1, f"{environ}: gov check ran {len(calls)} times"
        argv, cwd, pythonpath, timeout = calls[0]
        assert argv[-2:] == ["check", "--json"] and argv[1:3] == ["-c", S._GOV], f"{environ}: {argv}"
        assert cwd == S.REPO_ROOT and pythonpath == str(S.SRC), f"{environ}: {cwd}, {pythonpath}"
        assert timeout == S.GOV_CHECK_TIMEOUT_S == 1800.0, f"{environ}: {timeout}"
        assert checks[S.CONTEXT_CHECK_ID]["status"] == S.GREEN


def test_a_check_result_that_is_missing_or_broken_is_never_read_as_green(tmp_path, no_process):
    """KPI success 3 (W2-75): a GOV_CLOSE_CHECK_RESULT that is missing, a folder, empty, not JSON, not gov check's
    envelope, or lists no checks fails, naming the file and what is wrong; it is never read as green, and no
    ``gov check`` is started in its place (the route chosen: README, "W2-75")."""
    green = _envelope(GREEN_CHECKS)
    broken = {
        "missing": None,
        "a folder": "folder",
        "empty": "",
        "not JSON": "context-reproducibility GREEN\n",
        "a JSON list": json.dumps(GREEN_CHECKS),
        "another command's envelope": json.dumps(_envelope(GREEN_CHECKS, command="context")),
        "no ok": json.dumps({k: v for k, v in green.items() if k != "ok"}),
        "no checks": json.dumps({**green, "result": {}}),
        "checks not a list": json.dumps({**green, "result": {"checks": {S.CONTEXT_CHECK_ID: GREEN_CHECKS[0]}}}),
        "an empty list of checks": json.dumps(_envelope([])),
        "a check that is no object": json.dumps(_envelope([*GREEN_CHECKS, "GREEN"])),
    }
    for index, (form, text) in enumerate(broken.items()):
        result = tmp_path / f"check-result-{index}.json"
        if text == "folder":
            result.mkdir()
        elif text is not None:
            result.write_text(text, encoding="utf-8")
        with pytest.raises(AssertionError) as refused:
            S.green_here_check({S.CHECK_RESULT_VARIABLE: str(result)})
        assert str(result) in str(refused.value), f"{form}: the failure does not name the file: {refused.value}"
        assert no_process == [], f"{form}: a process was started in place of the result: {no_process}"


def test_a_red_or_missing_check_in_the_close_s_result_still_fails_the_cases(tmp_path, no_process):
    """KPI success 4 (W2-75): read from the close's result, a check that is RED, missing, or not hard-block still
    fails its case, naming the check and its status, exactly as it does from the fixture's own ``gov check``."""
    cases = ((test_gov_check_gives_context_reproducibility_green_here, S.CONTEXT_CHECK_ID),
             (test_gov_check_gives_core_schema_green_here, S.CORE_SCHEMA_ID))
    for case, check_id in cases:
        others = [check for check in GREEN_CHECKS if check["id"] != check_id]
        for form, checks, said in (("RED", [*others, _check(check_id, S.RED)], f"{check_id} is RED"),
                                   ("missing", others, f"lists no {check_id}"),
                                   ("advisory", [*others, _check(check_id, severity="advisory")], "")):
            result = tmp_path / f"check-result-{check_id}-{form}.json"
            result.write_text(json.dumps(_envelope(checks, ok=form == "advisory")) + "\n", encoding="utf-8")
            with pytest.raises(AssertionError) as failed:
                case(S.green_here_check({S.CHECK_RESULT_VARIABLE: str(result)}))
            assert said in str(failed.value), f"{check_id} {form}: the failure does not say {said!r}: {failed.value}"
        assert no_process == [], no_process
