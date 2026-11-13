"""W2-174 S2 and S3: ``gov adopt --verify-apply`` edits text only; the applied ticket is READY (README)."""

from __future__ import annotations

import pytest

import w2_174_support as s

C1 = "a unit test runs the widget and reads its name"
C2 = "a unit test calls the widget with an empty name and expects a refusal"
C3 = "a unit test calls the widget twice and compares the names"
C4 = "the unit test of S1 fails when the widget prints nothing"

# A ticket as a tracker's export leaves it: comments in the front matter (before a key, after a value, on a KPI line,
# between lines), keys not in alphabetical order, five KPI lines in four forms, and a body with a rule and the word Verify.
COMMENTED = """---
# fixture for W2-174 S2: comments, key order and styles must survive
id: DAEO-cm01
wbs_id: W2-950   # the plan's id
title: A fixture ticket with comments
type: task
status: in_progress
# keys are deliberately not in alphabetical order
created: 2026-11-11T08:00:00Z
role: engineer
class: tool
priority: 1
deps: []
links: []
assignee: engineer
external-ref: W2-950
tags:
- fixture
state_class: AUTHORITATIVE
depends_on: []
allowed_paths:
- src/widget/**   # code
- tests/unit/widget/**
reads:
- src/widget/**
needs: []
waits_on: []
kpis:
  # the success lines, one per style
  success:
  - The widget prints its name [DEC-1].   # plain, with a note
  - 'The widget refuses an empty name [DEC-1].'
  - "The widget keeps its name [DEC-1]."   # double quoted, with a note
  - line: "The widget prints its version [DEC-1]."   # a mapping
    verify: "a unit test reads the version"   # carries its verify already

  # the failure line
  failure:
  - The widget prints nothing.
non_goals:
- No graphical interface.
done_when:
- DOD-1
- DOD-2
- DOD-3
- DOD-5
- DOD-6
profile: STANDARD
sources:
- DEC-1
est_loc: 120
acceptance_tests:
  path: tests/acceptance/W2-950/
track: A
---
# W2-950 A fixture ticket with comments

The body says Verify: in prose and holds a rule below.

---

After the rule: more text, a # sign and a `key: value` line.
"""

ANSWERS = {"DAEO-cm01": {"S1": C1, "S2": C2, "S3": C3, "F1": C4}}

# the four edited lines, before and after. A plain scalar cannot hold " Verify: <clause>" (the ": " opens a mapping), so
# an edited plain item (S1 and F1 here) is re-quoted whole, in either quote style, its trailing note kept; the two
# quoted items take the clause inside their quotes; nothing else changes.
PLAIN = [("  - The widget prints its name [DEC-1].", "   # plain, with a note", C1),
         ("  - The widget prints nothing.", "", C4)]
QUOTED = [("  - 'The widget refuses an empty name [DEC-1].'",
           f"  - 'The widget refuses an empty name [DEC-1]. Verify: {C2}'"),
          ('  - "The widget keeps its name [DEC-1]."   # double quoted, with a note',
           f'  - "The widget keeps its name [DEC-1]. Verify: {C3}"   # double quoted, with a note')]
STYLES = ("single", "double")


def _requoted(line: str, tail: str, clause: str, style: str) -> str:
    quote = "'" if style == "single" else '"'
    return f"{line.rstrip()} Verify: {clause}{quote}{tail}".replace("- ", f"- {quote}", 1)


def expected_after(date: str, plain_styles=("single", "single"), session: str = s.SESSION,
                   text: str = COMMENTED) -> str:
    """The ticket as the ticket's S2 line says it must be: the four clauses appended (a plain item re-quoted), one
    added front-matter line before the closing ``---``, and no other byte changed."""
    for (old, tail, clause), style in zip(PLAIN, plain_styles):
        full = old + tail
        assert text.count(full) == 1, f"fixture line occurs {text.count(full)} times: {full!r}"
        text = text.replace(full, _requoted(old, tail, clause, style))
    for old, new in QUOTED:
        assert text.count(old) == 1, f"fixture line occurs {text.count(old)} times: {old!r}"
        text = text.replace(old, new)
    lines = text.split("\n")
    end = lines.index("---", 1)
    lines.insert(end, f"verify_pass: {date} {session}")
    return "\n".join(lines)


def allowed_texts(dates) -> set[str]:
    return {expected_after(date, (a, b)) for date in dates for a in STYLES for b in STYLES}


def run_apply(repo, answers_path, via: str):
    """(ids changed, the set of UTC dates the marker may carry) for an apply through the CLI or the function."""
    if via == "cli":
        before = s.utc_today()
        done = repo.verify_apply(answers_path)
        after = s.utc_today()
        result = s.result_of(done)
        assert "changed" in result, f"the result has no 'changed': {result!r}"
        return result["changed"], {before.isoformat(), after.isoformat()}
    return s.verify_pass().apply(repo.root, answers_path, s.SESSION, s.TODAY), {s.TODAY.isoformat()}


@pytest.fixture(params=["cli", "function"])
def via(request):
    return request.param


def test_s2_byte_diff_shows_only_the_appended_clauses_and_the_one_added_line(repo, via):
    repo.raw_ticket("DAEO-cm01", COMMENTED)
    changed, dates = run_apply(repo, repo.answers(ANSWERS), via)
    assert changed == ["DAEO-cm01"], f"the tickets changed are {changed!r}"
    after = repo.ticket_text("DAEO-cm01")
    assert after in allowed_texts(dates), \
        "the ticket's bytes are not 'the four clauses appended + one verify_pass line':\n" + \
        "\n".join(f"{n}: {a!r} -> {b!r}" for n, a, b in s.differing_lines(expected_after(sorted(dates)[0]), after))


def test_s2_the_mapping_line_and_its_comment_are_byte_identical(repo, via):
    repo.raw_ticket("DAEO-cm01", COMMENTED)
    run_apply(repo, repo.answers(ANSWERS), via)
    after = repo.ticket_text("DAEO-cm01")
    for line in ('  - line: "The widget prints its version [DEC-1]."   # a mapping',
                 '    verify: "a unit test reads the version"   # carries its verify already',
                 "# fixture for W2-174 S2: comments, key order and styles must survive",
                 "wbs_id: W2-950   # the plan's id",
                 "- src/widget/**   # code",
                 "  # the success lines, one per style",
                 "  # the failure line"):
        assert line in after.split("\n"), f"the line was changed or dropped: {line!r}"
    assert after.endswith(COMMENTED[COMMENTED.index("\n---\n# W2-950") + 1:]), "the body was changed"


def test_s2_the_marker_is_one_line_just_before_the_closing_rule(repo, via):
    repo.raw_ticket("DAEO-cm01", COMMENTED)
    _, dates = run_apply(repo, repo.answers(ANSWERS), via)
    lines = repo.ticket_text("DAEO-cm01").split("\n")
    end = lines.index("---", 1)
    assert lines[end - 1] in {f"verify_pass: {date} {s.SESSION}" for date in dates}, \
        f"the line before the closing --- is not 'verify_pass: <date> <session>': {lines[end - 1]!r}"
    assert len(s.marker_lines(repo.ticket_text("DAEO-cm01"))) == 1


def test_s2_the_applied_ticket_reads_back_with_each_clause_and_every_other_value_unchanged(repo, via):
    import yaml

    repo.raw_ticket("DAEO-cm01", COMMENTED)
    before = yaml.safe_load(COMMENTED.split("\n---\n")[0].removeprefix("---\n"))
    run_apply(repo, repo.answers(ANSWERS), via)
    after_text = repo.ticket_text("DAEO-cm01")
    assert s.lacking_labels(after_text) == []
    rows = {label: verify for label, _, verify in s.rows_of(after_text)}
    assert rows == {"S1": C1, "S2": C2, "S3": C3, "S4": "a unit test reads the version", "F1": C4}, \
        f"kpi_rows reads {rows!r}"
    after = s.front_of(after_text)
    marker = after.pop("verify_pass")
    assert isinstance(marker, str) and marker.endswith(f" {s.SESSION}") and s.ISO.match(marker.split(" ")[0])
    assert before["kpis"]["success"][3] == after["kpis"]["success"][3]
    for key in before:
        if key != "kpis":
            assert before[key] == after[key], f"front-matter value {key} changed: {before[key]!r} -> {after[key]!r}"
    assert list(after) == list(before), "the key order changed"


def test_s2_a_clause_the_style_cannot_hold_is_escaped_and_only_its_item_changes(repo, via):
    """Quotes, a backslash, ': ' and ' #' in a clause: it reads back exactly, and no other line changes."""
    single_clause = "a test that checks the widget's name, it isn't empty"
    double_clause = 'a test that checks "the name" in C:\\temp'
    plain_clause = "a unit test: runs the widget # then reads its name"
    original = s.front_text("DAEO-es01", "W2-951", "in_progress",
                            [s.single("The widget has a name [DEC-1]."), s.double("The widget keeps its name [DEC-1]."),
                             s.lacking("The widget prints its name [DEC-1].")],
                            [s.verified("The widget never crashes [DEC-1].")])
    repo.raw_ticket("DAEO-es01", original)
    answers = {"DAEO-es01": {"S1": single_clause, "S2": double_clause, "S3": plain_clause}}
    run_apply(repo, repo.answers(answers), via)
    after_text = repo.ticket_text("DAEO-es01")
    rows = {label: verify for label, _, verify in s.rows_of(after_text)}
    assert (rows["S1"], rows["S2"], rows["S3"]) == (single_clause, double_clause, plain_clause), \
        f"a clause did not read back exactly: {rows!r}"
    assert rows["F1"] == "a unit test of the thing"
    lines = [line for line in after_text.split("\n") if not line.startswith("verify_pass:")]
    old = original.split("\n")
    assert len(lines) == len(old), "the apply added or dropped lines other than the marker"
    touched = [n for n, (a, b) in enumerate(zip(old, lines)) if a != b]
    wanted = [n for n, line in enumerate(old) if line.lstrip().startswith(("- 'The widget has", '- "The widget keeps',
                                                                         "- The widget prints its name"))]
    assert touched == wanted, f"lines {touched} changed, only the three edited items' lines {wanted} may"


def test_s2_an_existing_marker_is_replaced_in_place_and_stays_the_only_one(repo, via):
    lines = s.front_text("DAEO-mk01", "W2-952", "in_progress", [s.lacking("The widget has a line [DEC-1].")],
                         [s.verified("The widget never crashes [DEC-1].")]).split("\n")
    lines.insert(lines.index("kpis:"), "verify_pass: 2026-01-01 an-older-session")
    original = "\n".join(lines)
    repo.raw_ticket("DAEO-mk01", original)
    _, dates = run_apply(repo, repo.answers({"DAEO-mk01": {"S1": C1}}), via)
    after = repo.ticket_text("DAEO-mk01")
    assert len(s.marker_lines(after)) == 1, f"the ticket carries {len(s.marker_lines(after))} verify_pass lines"
    new = after.split("\n")
    assert len(new) == len(lines), "a line was added or dropped: the old marker was not replaced in place"
    changed = [n for n, (a, b) in enumerate(zip(lines, new)) if a != b]
    marker_at = lines.index("verify_pass: 2026-01-01 an-older-session")
    kpi_at = next(n for n, line in enumerate(lines) if "The widget has a line" in line)
    assert changed == [marker_at, kpi_at], f"lines {changed} changed, expected the marker's {marker_at} and the item's {kpi_at}"
    assert new[marker_at] in {f"verify_pass: {date} {s.SESSION}" for date in dates}
    assert s.rows_of(after)[0][2] == C1


def test_s2_two_tickets_are_both_changed_and_each_marked(repo, via):
    repo.ticket("DAEO-aa01", "W2-901", "open", [s.lacking("A one [DEC-1].")], [s.verified("A failure [DEC-1].")])
    repo.ticket("DAEO-bb02", "W2-902", "in_progress", [s.verified("B one [DEC-1].")],
                [s.lacking("B failure [DEC-1].")])
    changed, _ = run_apply(repo, repo.answers({"DAEO-bb02": {"F1": C4}, "DAEO-aa01": {"S1": C1}}), via)
    assert sorted(changed) == ["DAEO-aa01", "DAEO-bb02"] and list(changed) == sorted(changed), \
        f"changed is {changed!r}, expected both ids sorted"
    for ticket in ("DAEO-aa01", "DAEO-bb02"):
        assert len(s.marker_lines(repo.ticket_text(ticket))) == 1 and s.lacking_labels(repo.ticket_text(ticket)) == []
    s.marker_invariant(repo.root)


def test_s2_apply_without_a_session_is_a_usage_error_and_writes_nothing(repo):
    repo.raw_ticket("DAEO-cm01", COMMENTED)
    answers = repo.answers(ANSWERS)
    before = s.snapshot(repo.tmp)
    done = repo.verify_apply(answers, session=None)
    assert done.returncode == 2, f"--verify-apply without --session must be argparse's usage error (exit 2): {s.describe(done)}"
    assert "session" in done.stderr and "unrecognized" not in done.stderr, \
        f"the usage error does not name the missing --session: {s.describe(done)}"
    assert s.snapshot(repo.tmp) == before, "a usage error wrote something"
    assert s.result_of(repo.verify_apply(answers, session="sess-174b")).get("changed") == ["DAEO-cm01"], \
        "the same call with a --session does not apply"


# --- S3 -------------------------------------------------------------------------------------------------------------

def test_s3_after_an_apply_the_ticket_is_ready_and_gov_brief_engineer_builds_its_brief(repo):
    from gov.brief.build import Tickets, ready_check

    repo.kernel_templates()
    repo.filled_facts()
    repo.ticket("DAEO-fx01", "W2-901", "in_progress",
                [s.lacking("The widget prints its name [DEC-1]."), s.single("The widget refuses an empty name [DEC-1]."),
                 s.double("The widget keeps its name [DEC-1].")],
                [s.lacking("The widget prints nothing [DEC-1].")])

    def refusals() -> list[str]:
        tickets = Tickets(repo.root)
        front = tickets.load(repo.tickets / "DAEO-fx01.md")[0]
        return [f"{f['code']} {f['detail']}" for f in ready_check(front, tickets, repo.root, s.NEW_SINCE)[0]]

    assert refusals() == ["KPI_NO_VERIFY S1", "KPI_NO_VERIFY S2", "KPI_NO_VERIFY S3", "KPI_NO_VERIFY F1"], \
        "the fixture is not a ticket lacking its verifies before the apply"
    before = repo.gov("brief", "engineer", "DAEO-fx01", json_out=False)
    assert before.returncode != 0 and "BRIEF_NOT_READY" in before.stderr, \
        f"gov brief built a brief for a ticket with no verifies: {s.describe(before)}"

    answers = repo.answers({"DAEO-fx01": {"S1": C1, "S2": C2, "S3": C3, "F1": C4}})
    s.result_of(repo.verify_apply(answers))

    assert refusals() == [], f"ready_check still refuses the applied ticket: {refusals()}"
    done = repo.gov("brief", "engineer", "DAEO-fx01", json_out=False)
    assert done.returncode == 0 and done.stdout.strip(), f"gov brief engineer did not build a brief: {s.describe(done)}"
    for clause in (C1, C2, C3, C4):
        assert clause in done.stdout, f"the brief's KPI table does not carry the clause {clause!r}"


def test_s3_the_function_applied_ticket_is_ready_too(repo):
    from gov.brief.build import Tickets, ready_check

    repo.kernel_templates()
    repo.filled_facts()
    repo.ticket("DAEO-fx01", "W2-901", "open", [s.lacking("The widget prints its name [DEC-1].")],
                [s.single("The widget prints nothing [DEC-1].")])
    s.verify_pass().apply(repo.root, repo.answers({"DAEO-fx01": {"S1": C1, "F1": C4}}), s.SESSION, s.TODAY)
    tickets = Tickets(repo.root)
    front = tickets.load(repo.tickets / "DAEO-fx01.md")[0]
    refuse, _ = ready_check(front, tickets, repo.root, s.NEW_SINCE)
    assert not [f for f in refuse if f["code"] == "KPI_NO_VERIFY"], f"KPI_NO_VERIFY remains: {refuse}"
    assert repo.gov("brief", "engineer", "DAEO-fx01", json_out=False).returncode == 0
