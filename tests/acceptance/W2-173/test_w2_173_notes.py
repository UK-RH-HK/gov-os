"""S3 and failure line 2 (its notes part): the memory checker's ``notes.md`` checked at delivery against the audit
checker brief's fixed form (checker.md §6), and the result's three verdict counts against the notes' lines; a notes file
that does not fit delivers nothing and ends 20 (DEC-1101 (2)).

The form, as the lead's brief reads checker.md §6: the line ``# Cross-check notes``; the line ``## Questions``; one line
per file of the set staged in ``input/set/``, in id order, ``<id> | accept|revise|reject | <codes or -> | also: <...> |
<sentence>``; the line ``## The set``; its five lines (starting ``domains:``, ``categories:``, ``keyword:``,
``supersession ``, ``set codes:``). The result's ``accepted``, ``revise`` and ``rejected`` equal the three words' counts.

Readings: a question's id is its file's name less ``.yaml`` (the planted set's files are flat, each named by the id it
holds, so the two readings agree); "nothing written to the set's folder" is no ``XCHECK-r1.md`` and the folder
``fixtures/evaluation/<set>/`` identical entry for entry before and after. Only what S3's Verify names is tested here:
the codes' and the sentences' inner form is not.
"""

from __future__ import annotations

import pytest

import w2_173_support as s


def launch_checker(world, out):
    folder = s.plant_audit_set(world)
    before = s.snapshot(folder)
    run = world.deliver("checker", set_=s.AUDIT_SET, out=out)
    return run, folder, before


def assert_refused_20(world, run, folder, before):
    assert run.code == 20, run.why()
    line = run.line
    assert line["status"] == "rejected" and line["reason"] == "result", line
    assert line["delivered"]["files"] == 0 and line["delivered"]["to"] is None, line["delivered"]
    assert not (folder / "XCHECK-r1.md").exists(), "the notes were delivered"
    assert s.snapshot(folder) == before, "the set's folder changed"
    assert s.schema_errors(line) == [], s.schema_errors(line)


def test_s3_well_formed_notes_are_delivered(world):
    out = s.checker_out()
    run, folder, _before = launch_checker(world, out)
    assert run.code == 0, run.why()
    line = run.line
    assert line["status"] == "delivered" and line["delivered"]["to"] == "notes", line
    assert (folder / "XCHECK-r1.md").read_text() == out["notes.md"]
    assert (line["out"]["accepted"], line["out"]["revise"], line["out"]["rejected"]) == (2, 1, 0), line["out"]


def test_s3_well_formed_notes_with_every_verdict_word_are_delivered(world):
    """One question line of each word (the counts 1, 1, 1): the form takes all three."""
    qs = [s.QUESTION_LINES[0], s.QUESTION_LINES[1],
          "q03 | reject | R1-WRONG | also: none | the gold answer is not the governing source's"]
    lines = s.notes_lines(questions=qs)
    run, folder, _before = launch_checker(world, s.checker_out(lines))
    assert run.code == 0, run.why()
    assert (folder / "XCHECK-r1.md").read_text() == s.notes_text(lines)


# -- a missing line --------------------------------------------------------------------------------------------------

MISSING = {
    "the-heading": lambda L: L[1:],
    "questions-heading": lambda L: [x for x in L if x != "## Questions"],
    "a-question-line": lambda L: [x for x in L if not x.startswith("q02 ")],
    "the-set-heading": lambda L: [x for x in L if x != "## The set"],
    "a-set-line": lambda L: [x for x in L if not x.startswith("keyword:")],
}


@pytest.mark.parametrize("which", sorted(MISSING))
def test_s3_notes_with_a_missing_line_are_refused_20(world, which):
    """Failure line 2: one line of the form left out. The result's counts are taken from the lines that remain, so
    only the missing line can refuse."""
    lines = MISSING[which](s.notes_lines())
    run, folder, before = launch_checker(world, s.checker_out(lines, result=s.checker_result(lines)))
    assert_refused_20(world, run, folder, before)


# -- a fourth verdict word -------------------------------------------------------------------------------------------

@pytest.mark.parametrize("word", ("maybe", "accepted", "Accept"))
def test_s3_notes_with_a_fourth_verdict_word_are_refused_20(world, word):
    qs = list(s.QUESTION_LINES)
    qs[2] = qs[2].replace("| accept |", f"| {word} |", 1)
    lines = s.notes_lines(questions=qs)
    result = s.checker_result(lines)       # q03 counted in none of the three
    run, folder, before = launch_checker(world, s.checker_out(lines, result=result))
    assert_refused_20(world, run, folder, before)


# -- an id not in the set --------------------------------------------------------------------------------------------

def test_s3_notes_naming_an_id_not_in_the_set_in_place_of_one_are_refused_20(world):
    qs = list(s.QUESTION_LINES)
    qs[2] = qs[2].replace("q03 |", "q04 |", 1)
    lines = s.notes_lines(questions=qs)
    run, folder, before = launch_checker(world, s.checker_out(lines))
    assert_refused_20(world, run, folder, before)


def test_s3_notes_with_an_extra_line_for_an_id_not_in_the_set_are_refused_20(world):
    qs = list(s.QUESTION_LINES) + ["q04 | accept | - | also: none | the question reads one way only"]
    lines = s.notes_lines(questions=qs)
    run, folder, before = launch_checker(world, s.checker_out(lines, result=s.checker_result(lines)))
    assert_refused_20(world, run, folder, before)


# -- counts that disagree --------------------------------------------------------------------------------------------

@pytest.mark.parametrize("override", ({"accepted": 3, "revise": 0}, {"rejected": 1, "accepted": 1},
                                      {"revise": 2, "accepted": 1}),
                         ids=("accepted", "rejected", "revise"))
def test_s3_result_counts_that_disagree_with_the_lines_are_refused_20(world, override):
    """The notes are well formed; the result's three counts (still summing to checked) do not match the lines'."""
    result = s.checker_result(**override)
    run, folder, before = launch_checker(world, s.checker_out(result=result))
    assert_refused_20(world, run, folder, before)
