"""W2-175: the seven role templates carry Policy 2's four refusals (DEC-820), the counterpart refusal in each role's
own half, DEC-861's record rule and brief.md's stop sentence (DEC-1137 (2)), at version 1.0.1 (DEC-1121).

Success 1 to 5 and failure 1 of DAEO-wahn; the README maps each case to its line and gives its red reason on the
base. A statement is a W2-128 unit (a paragraph, a list item or a table row), white space collapsed, case folded.
"""

from __future__ import annotations

import pytest

import w2_128_support as s
import w2_175_support as t


# --- Success 1: reads open, four refusals, ending [DEC-820] ---------------------------------------------------------

@pytest.mark.parametrize("stem", t.SEVEN)
def test_s1_one_statement_says_reads_are_open_and_names_the_four_refusals(stem):
    hits = t.holding(stem, "read", "open", "secret", "held-out", "counterpart", "hidden half", cites="DEC-820")
    assert hits, (f"{stem}.md has no one statement that says reads are open and names the four refusals (secret, "
                  f"held-out, counterpart, hidden half), ending with [DEC-820] (DEC-820 item 2)")


# --- Success 2: the counterpart refusal in each role's own half -----------------------------------------------------

def test_s2_engineer_never_reads_the_acceptance_test_code_and_may_run_the_cases_and_see_results():
    hits = t.holding("role-engineer", "acceptance", "run", "name", "pass", "fail", "message",
                     any_of=("code", "source"), negation=t.NEGATION)
    assert hits, ("role-engineer.md has no one statement, with a never or not, that the engineer does not read the "
                  "ticket's acceptance-test code and may run its cases and see names, pass or fail and failure "
                  "messages (DEC-820 item 2 (c), DEC-957)")


def test_s2_test_designer_never_reads_the_implementation_and_works_from_specification_kpis_and_code():
    hits = t.holding("role-test-designer", "specification", "kpi", "existing code",
                     any_of=("implementation", "branch"), negation=t.NEGATION)
    assert hits, ("role-test-designer.md has no one statement, with a never or not, that the designer does not read "
                  "the ticket's implementation and works from the specification, the KPI lines and the existing "
                  "code (DEC-820 item 2 (c), DEC-963)")


def test_s2_reviewer_reads_everything_tests_and_code_alike():
    hits = t.holding("role-reviewer", "read", "everything", "tests", "code")
    assert hits, "role-reviewer.md has no one statement that the reviewer reads everything, tests and code (DEC-820 item 3)"


# --- Success 3: DEC-861's record rule; role-cto's decision-record line unchanged ------------------------------------

@pytest.mark.parametrize("stem", t.SIX)
def test_s3_one_statement_says_owner_decisions_are_recorded_by_decision_record_commits(stem):
    hits = t.holding(stem, "decision-record", "owner", "Role: owner", "Decided-by", negation=t.NO_WORD,
                     cites="DEC-861")
    assert hits, (f"{stem}.md has no one statement that the owner's decisions are recorded by the orchestrator's "
                  f"decision-record commits and that no `Role: owner` or `Decided-by:` goes on a commit of its "
                  f"role's, ending with [DEC-861]")


def test_s3_role_cto_keeps_its_decision_record_commit_line_byte_for_byte():
    # The base is role-cto.md as the last commit to change it before this ticket left it (t.BASE, a6c83d497035):
    # a base is the last commit to change the file before the ticket, never an older one. Read from git, so the
    # case reads the same line before and after this ticket merges.
    base = t.base_text("role-cto").split("\n")
    lines = [line for line in base if "Task: decision-record" in line]
    assert len(lines) == 1, f"premise: role-cto.md at {t.BASE['role-cto']} has {len(lines)} decision-record lines"
    for needle in ("`Role: orchestrator`", "`Decided-by: owner (chat, {DATE})`", "[DEC-861]"):
        assert needle in lines[0], f"premise: the base's decision-record line lacks {needle}: {lines[0]!r}"
    now = t.text_of("role-cto").split("\n")
    assert lines[0] in now, f"role-cto.md no longer holds its decision-record commit line byte for byte: {lines[0]!r}"


# --- Success 4 and failure 1: the stop sentence, word for word ------------------------------------------------------

@pytest.mark.parametrize("stem", t.SEVEN)
def test_s4_template_holds_the_stop_sentence_word_for_word(stem):
    problem = t.stop_problem(t.text_of(stem), f"{stem}.md")
    assert problem is None, problem


def test_s4_the_stop_sentence_is_brief_md_s_own():
    problem = t.stop_problem(s.template("brief"), "brief.md")
    assert problem is None, f"{problem} (the one source of the wording; TPL-6 F1)"


def test_f1_a_stop_sentence_changed_by_one_letter_fails_the_s4_check(tmp_path):
    # A planted copy of each template, in tmp_path: with the sentence word for word the check passes; with one
    # letter of it changed the check fails. When the template already holds the sentence, that occurrence is the
    # one changed; else the sentence is appended to the copy first.
    letter = t.STOP.index("twice") + 1  # "twice" -> "tvice"
    changed = t.STOP[:letter] + "v" + t.STOP[letter + 1:]
    assert changed != t.STOP
    for stem in t.SEVEN:
        text = t.text_of(stem)
        planted = text if t.STOP in text else text.rstrip("\n") + "\n\n" + t.STOP + "\n"
        good = tmp_path / f"{stem}.good.md"
        good.write_text(planted, encoding="utf-8")
        assert t.stop_problem(good.read_text(encoding="utf-8"), good.name) is None, \
            f"premise: the planted copy of {stem}.md with the sentence word for word fails the check"
        bad = tmp_path / f"{stem}.md"
        bad.write_text(planted.replace(t.STOP, changed), encoding="utf-8")
        assert t.stop_problem(bad.read_text(encoding="utf-8"), bad.name) is not None, \
            f"the S4 check passes a copy of {stem}.md whose stop sentence is changed by one letter"


# --- Success 5: version 1.0.1, every other front matter key the base's ----------------------------------------------

@pytest.mark.parametrize("stem", t.SEVEN)
def test_s5_front_matter_is_version_1_0_1_and_otherwise_the_base_s(stem):
    base, _ = s.split(t.base_text(stem))
    now, _ = s.split(t.text_of(stem))
    assert isinstance(now, dict), f"{stem}.md's front matter does not parse"
    assert now.get("version") == "1.0.1", \
        f"{stem}.md: version is {now.get('version')!r}, not 1.0.1 (DEC-1121's step for a template delta)"
    others = {key for key in set(base) | set(now) if key != "version"}
    changed = {key: (base.get(key), now.get(key)) for key in sorted(others) if base.get(key) != now.get(key)}
    assert not changed, f"{stem}.md: front matter keys other than version differ from the base {t.BASE[stem]}: {changed}"
