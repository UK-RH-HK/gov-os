"""W2-152: the refusals of the filling (S2, S5). Each case builds its own repository (README)."""

from __future__ import annotations

import w2_152_support as s


# --- S2: a placeholder left unfilled, a KPI line without a verify --------------------------------------------------

def test_s2_each_unknown_placeholder_is_named(repo):
    repo.append_template_line("brief.md", "Extra: {NOT_A_KEY} and {ANOTHER_UNKNOWN: a description of it}.")
    findings = s.refusal(repo.run("engineer", s.TICKET_ID, json_out=True))
    assert s.has(findings, "PLACEHOLDER_LEFT", "NOT_A_KEY"), f"PLACEHOLDER_LEFT NOT_A_KEY is not named: {findings}"
    assert s.has(findings, "PLACEHOLDER_LEFT", "ANOTHER_UNKNOWN"), \
        f"PLACEHOLDER_LEFT ANOTHER_UNKNOWN is not named: {findings}"
    s.plain_refusal(repo.run("engineer", s.TICKET_ID),
                    ("PLACEHOLDER_LEFT", "NOT_A_KEY"), ("PLACEHOLDER_LEFT", "ANOTHER_UNKNOWN"))


def test_s2_a_command_placeholder_with_no_such_command_is_named(repo):
    repo.append_template_line("brief.md", "Run {CMD:no_such_command} first.")
    findings = s.refusal(repo.run("engineer", s.TICKET_ID, json_out=True))
    assert s.has(findings, "PLACEHOLDER_LEFT", "no_such_command"), \
        f"PLACEHOLDER_LEFT for {{CMD:no_such_command}} is not named: {findings}"
    s.plain_refusal(repo.run("engineer", s.TICKET_ID), ("PLACEHOLDER_LEFT", "no_such_command"))


def test_s2_a_string_kpi_line_without_verify_text_is_named(repo):
    """A string line with no ``Verify:`` (S2), and one with ``Verify:`` and nothing after it (S3), each lack a verify."""
    front = s.ready_front()
    front["kpis"]["success"] = [
        front["kpis"]["success"][0],
        "S2 The widget refuses an empty name [DEC-1].",
        "S3 The widget logs each call [DEC-1]. Verify:   ",
    ]
    repo.ticket(front)
    findings = s.refusal(repo.run("engineer", s.TICKET_ID, json_out=True))
    assert s.has(findings, "KPI_NO_VERIFY", "S2", exact_first=True), f"KPI_NO_VERIFY S2 is not named: {findings}"
    assert s.has(findings, "KPI_NO_VERIFY", "S3", exact_first=True), f"KPI_NO_VERIFY S3 is not named: {findings}"
    assert not s.has(findings, "KPI_NO_VERIFY", "S1", exact_first=True), \
        f"S1 ({{line, verify}} with a verify) is named as lacking one: {findings}"
    s.plain_refusal(repo.run("engineer", s.TICKET_ID), ("KPI_NO_VERIFY", "S2"), ("KPI_NO_VERIFY", "S3"))


def test_s2_an_object_kpi_line_with_an_empty_verify_is_named(repo):
    front = s.ready_front()
    front["kpis"]["failure"] = [{"line": "The widget prints nothing.", "verify": ""}]
    repo.ticket(front)
    findings = s.refusal(repo.run("engineer", s.TICKET_ID, json_out=True))
    assert s.has(findings, "KPI_NO_VERIFY", "F1", exact_first=True), f"KPI_NO_VERIFY F1 is not named: {findings}"
    s.plain_refusal(repo.run("engineer", s.TICKET_ID), ("KPI_NO_VERIFY", "F1"))


def test_s2_either_verify_form_counts_as_a_verify(repo):
    """``{line, verify}`` with text and a string holding ``Verify:`` and text both have a verify: no refusal."""
    front = s.ready_front()
    front["kpis"]["failure"] = [
        {"line": "The widget prints nothing.", "verify": "the unit test of S1 fails"},
        "The widget crashes on a long name. Verify: a unit test with a 10,000-character name",
    ]
    repo.ticket(front)
    done = repo.run("engineer", s.TICKET_ID)
    s.ok(done)
    assert "KPI_NO_VERIFY" not in done.stderr, f"a line with a verify is named as lacking one: {done.stderr}"


# --- S5: "until <ticket>" once that ticket is closed ----------------------------------------------------------------

def _closed_and_open(repo):
    repo.ticket(s.closed_ticket("DAEO-fx09", "W2-909", status="closed"))
    repo.ticket(s.closed_ticket("DAEO-fx08", "W2-908", status="in_progress"))


def test_s5_a_template_line_until_a_closed_ticket_is_refused(repo):
    _closed_and_open(repo)
    repo.append_template_line("brief.md", "Keep the old parser until DAEO-fx09 closes.")
    findings = s.refusal(repo.run("engineer", s.TICKET_ID, json_out=True))
    assert s.has(findings, "UNTIL_CLOSED", "DAEO-fx09") or s.has(findings, "UNTIL_CLOSED", "W2-909"), \
        f"UNTIL_CLOSED DAEO-fx09 is not named: {findings}"
    s.plain_refusal(repo.run("engineer", s.TICKET_ID), ("UNTIL_CLOSED", "fx09"))


def test_s5_a_part_line_until_a_closed_ticket_is_refused(repo):
    _closed_and_open(repo)
    part = repo.file("parts/part.md", "Use the old parser until W2-909 lands.\n")
    findings = s.refusal(repo.run("lead", s.TICKET_ID, "--run", "build", "--part", str(part), json_out=True))
    assert s.has(findings, "UNTIL_CLOSED", "W2-909") or s.has(findings, "UNTIL_CLOSED", "DAEO-fx09"), \
        f"UNTIL_CLOSED W2-909 is not named: {findings}"


def test_s5_until_a_ticket_still_open_is_not_refused(repo):
    _closed_and_open(repo)
    repo.append_template_line("brief.md", "Keep the old parser until DAEO-fx08 closes.")
    part = repo.file("parts/part.md", "Use the old parser until W2-908 lands.\n")
    done = repo.run("engineer", s.TICKET_ID, "--part", str(part))
    out = s.ok(done)
    assert "Keep the old parser until DAEO-fx08 closes." in out, f"the template's until line is not in the brief:\n{out}"
    assert "Use the old parser until W2-908 lands." in out, f"the part's until line is not in the brief:\n{out}"
    assert "UNTIL_CLOSED" not in done.stderr
