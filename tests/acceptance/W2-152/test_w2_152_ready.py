"""W2-152: the ready check inside gov brief (S3, S8, S9, F2). Each case builds its own repository (README)."""

from __future__ import annotations

import re

import pytest

import w2_152_support as s

BUDGET = 4321  # planted facts: budgets.brief


# --- S3: warnings and the size on stderr; a warning never stops it ---------------------------------------------------

def _advisory_ticket(repo):
    """The READY ticket with both advisory items: no non_goals, est_loc 401."""
    repo.edit_ticket(non_goals=s.DROP, est_loc=401)


def test_s3_warnings_and_size_on_stderr_and_the_brief_unchanged(repo):
    _advisory_ticket(repo)
    done = repo.run("engineer", s.TICKET_ID)
    out = s.ok(done)
    assert s.normal(out) == s.golden("brief-engineer.txt"), f"a warning changed the brief on stdout:\n{out}"
    assert "gov brief:" not in out, f"a warning or the size line went to stdout:\n{out}"
    assert s.stderr_warning(done, "NON_GOALS_MISSING"), f"no 'gov brief: NON_GOALS_MISSING' on stderr: {done.stderr}"
    assert any("401" in line for line in s.stderr_warning(done, "EST_LOC_OVER")), \
        f"no 'gov brief: EST_LOC_OVER 401' on stderr: {done.stderr}"
    sized = [line for line in done.stderr.splitlines()
             if line.startswith("gov brief: ") and str(BUDGET) in line and re.search(r"\d", line.replace(str(BUDGET), ""))]
    assert sized, f"no 'gov brief: <CODE> <detail>' line on stderr gives the size against the budget {BUDGET}: {done.stderr}"


def test_s3_json_carries_warnings_size_and_budget(repo):
    _advisory_ticket(repo)
    done = repo.run("engineer", s.TICKET_ID, json_out=True)
    assert done.returncode == 0, s.describe(done)
    data = s.envelope(done)
    assert data["ok"] is True, data
    result = data["result"]
    assert s.normal(result.get("brief", "")) == s.golden("brief-engineer.txt"), "result.brief is not the brief"
    warnings = s.warning_codes(result.get("warnings"))
    assert s.has(warnings, "NON_GOALS_MISSING"), f"result.warnings lacks NON_GOALS_MISSING: {warnings}"
    assert s.has(warnings, "EST_LOC_OVER", "401"), f"result.warnings lacks EST_LOC_OVER 401: {warnings}"
    size = result.get("size")
    assert isinstance(size, int) and not isinstance(size, bool) and 0 < size <= len(result["brief"]), \
        f"result.size is not the filled size in characters: {size!r}"
    assert result.get("budget") == BUDGET, f"result.budget is not facts.yaml's budgets.brief ({BUDGET}): {result.get('budget')!r}"


def test_s3_a_brief_over_its_budget_still_prints(repo):
    facts = repo.facts()
    facts["budgets"]["brief"] = 10
    repo.write_facts(facts)
    done = repo.run("engineer", s.TICKET_ID, json_out=True)
    assert done.returncode == 0, f"a brief over its budget was stopped: {s.describe(done)}"
    result = s.envelope(done)["result"]
    assert result.get("budget") == 10 and isinstance(result.get("size"), int) and result["size"] > 10, result
    assert s.normal(result.get("brief", "")) == s.golden("brief-engineer.txt")
    plain = repo.run("engineer", s.TICKET_ID)
    assert s.normal(s.ok(plain)) == s.golden("brief-engineer.txt")


# --- S8: required fields refuse, advisory items warn ----------------------------------------------------------------

def test_s8_empty_allowed_paths_is_refused(repo):
    repo.edit_ticket(allowed_paths=[])
    findings = s.refusal(repo.run("engineer", s.TICKET_ID, json_out=True))
    assert s.has(findings, "ALLOWED_PATHS_EMPTY"), f"ALLOWED_PATHS_EMPTY is not named: {findings}"
    s.plain_refusal(repo.run("engineer", s.TICKET_ID), ("ALLOWED_PATHS_EMPTY", "ALLOWED_PATHS_EMPTY"))


@pytest.mark.parametrize("ref, ticket_id, status", [("DAEO-fx05", "DAEO-fx05", "open"),
                                                      ("W2-906", "DAEO-fx06", "in_progress")],
                         ids=["tk-id", "w2-id"])
def test_s8_a_depends_on_not_closed_is_refused(repo, ref, ticket_id, status):
    repo.ticket(s.closed_ticket(ticket_id, f"W2-9{ticket_id[-2:]}", status=status))
    repo.edit_ticket(depends_on=[ref])
    findings = s.refusal(repo.run("engineer", s.TICKET_ID, json_out=True))
    assert s.has(findings, "DEPENDS_NOT_CLOSED", ref) or s.has(findings, "DEPENDS_NOT_CLOSED", ticket_id), \
        f"DEPENDS_NOT_CLOSED {ref} is not named: {findings}"
    s.plain_refusal(repo.run("engineer", s.TICKET_ID), ("DEPENDS_NOT_CLOSED", ref))


def test_s8_depends_on_all_closed_is_ready(repo):
    repo.ticket(s.closed_ticket("DAEO-fx07", "W2-907"))
    repo.ticket(s.closed_ticket("DAEO-fx10", "W2-910"))
    repo.edit_ticket(depends_on=["DAEO-fx07", "W2-910"])
    done = repo.run("engineer", s.TICKET_ID)
    s.ok(done)
    assert "DEPENDS_NOT_CLOSED" not in done.stderr, done.stderr


def test_s8_no_non_goals_warns_and_never_refuses(repo):
    repo.edit_ticket(non_goals=s.DROP)
    done = repo.run("engineer", s.TICKET_ID)
    assert s.normal(s.ok(done)) == s.golden("brief-engineer.txt")
    assert s.stderr_warning(done, "NON_GOALS_MISSING"), f"no NON_GOALS_MISSING warning: {done.stderr}"


def test_s8_est_loc_401_warns_and_never_refuses(repo):
    repo.edit_ticket(est_loc=401)
    done = repo.run("engineer", s.TICKET_ID)
    assert s.normal(s.ok(done)) == s.golden("brief-engineer.txt")
    assert any("401" in line for line in s.stderr_warning(done, "EST_LOC_OVER")), \
        f"no EST_LOC_OVER 401 warning: {done.stderr}"


def test_s8_est_loc_400_does_not_warn(repo):
    repo.edit_ticket(est_loc=400)
    done = repo.run("engineer", s.TICKET_ID)
    s.ok(done)
    assert "EST_LOC_OVER" not in done.stderr, f"est_loc 400 warned: {done.stderr}"


# --- S9: the dependency fields on new tickets ------------------------------------------------------------------------

CODES = {"reads": "READS_MISSING", "needs": "NEEDS_MISSING", "waits_on": "WAITS_ON_MISSING"}


@pytest.mark.parametrize("field", sorted(CODES))
def test_s9_a_ticket_created_on_new_since_without_the_field_is_refused(repo, field):
    repo.edit_ticket(created=s.CREATED_ON, **{field: s.DROP})
    findings = s.refusal(repo.run("engineer", s.TICKET_ID, json_out=True))
    assert s.has(findings, CODES[field]), f"{CODES[field]} is not named: {findings}"
    others = [code for name, code in CODES.items() if name != field and s.has(findings, code)]
    assert not others, f"a field the ticket holds is named missing: {others}"
    s.plain_refusal(repo.run("engineer", s.TICKET_ID), (CODES[field], CODES[field]))


def test_s9_a_ticket_created_after_new_since_without_all_three_names_each(repo):
    repo.edit_ticket(created=s.CREATED_AFTER, reads=s.DROP, needs=s.DROP, waits_on=s.DROP)
    findings = s.refusal(repo.run("engineer", s.TICKET_ID, json_out=True))
    for code in CODES.values():
        assert s.has(findings, code), f"{code} is not named: {findings}"


def test_s9_a_ticket_created_before_new_since_is_not_refused_for_them(repo):
    repo.edit_ticket(created=s.CREATED_BEFORE, reads=s.DROP, needs=s.DROP, waits_on=s.DROP)
    done = repo.run("engineer", s.TICKET_ID)
    assert s.normal(s.ok(done)) == s.golden("brief-engineer.txt")
    for code in CODES.values():
        assert code not in done.stderr, f"{code} on a ticket created before ready.new_since: {done.stderr}"


def test_s9_empty_lists_are_a_declared_none(repo):
    repo.edit_ticket(created=s.CREATED_AFTER, reads=[], needs=[], waits_on=[])
    done = repo.run("engineer", s.TICKET_ID)
    s.ok(done)
    for code in CODES.values():
        assert code not in done.stderr, f"an empty list was read as missing ({code}): {done.stderr}"


@pytest.mark.parametrize("wait, ref", [("DAEO-nope", "DAEO-nope"),
                                       ({"ref": "docs/research/missing.md", "reason": "the method"},
                                        "docs/research/missing.md")],
                         ids=["unknown-id", "unknown-record-path"])
def test_s9_a_waits_on_reference_that_does_not_exist_is_refused(repo, wait, ref):
    repo.edit_ticket(waits_on=[wait])
    findings = s.refusal(repo.run("engineer", s.TICKET_ID, json_out=True))
    assert s.has(findings, "WAITS_ON_UNKNOWN", ref), f"WAITS_ON_UNKNOWN {ref} is not named: {findings}"
    s.plain_refusal(repo.run("engineer", s.TICKET_ID), ("WAITS_ON_UNKNOWN", ref))


def test_s9_waits_on_references_that_exist_are_ready(repo):
    repo.ticket(s.closed_ticket("DAEO-fx07", "W2-907", status="in_progress"))
    repo.file("docs/research/R-1.md", "# R-1\n")
    repo.edit_ticket(waits_on=["DAEO-fx07", {"ref": "docs/research/R-1.md", "reason": "the method"}])
    done = repo.run("engineer", s.TICKET_ID)
    s.ok(done)
    assert "WAITS_ON_UNKNOWN" not in done.stderr, done.stderr


# --- F2: never refused for an advisory item, never READY with a required field missing ------------------------------

def test_f2_advisory_items_alone_exit_0_with_ok_true(repo):
    _advisory_ticket(repo)
    done = repo.run("engineer", s.TICKET_ID, json_out=True)
    assert done.returncode == 0, f"advisory items stopped gov brief: {s.describe(done)}"
    data = s.envelope(done)
    assert data["ok"] is True and "error" not in data, data
    plain = repo.run("engineer", s.TICKET_ID)
    s.ok(plain)
    assert "BRIEF_NOT_READY" not in plain.stderr


def test_f2_every_required_field_missing_is_refused_and_each_named(repo):
    repo.ticket(s.closed_ticket("DAEO-fx05", "W2-905", status="open"))
    front = s.ready_front()
    front["allowed_paths"] = []
    front["depends_on"] = ["DAEO-fx05"]
    front["kpis"]["success"].append("S3 The widget logs each call [DEC-1].")
    repo.ticket(front)
    findings = s.refusal(repo.run("engineer", s.TICKET_ID, json_out=True))
    assert s.has(findings, "ALLOWED_PATHS_EMPTY"), findings
    assert s.has(findings, "KPI_NO_VERIFY", "S3", exact_first=True), findings
    assert s.has(findings, "DEPENDS_NOT_CLOSED", "DAEO-fx05"), findings
