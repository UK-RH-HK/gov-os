"""S2 and failure line 2 (its stopped part): a memory writer's or checker's ``result.json`` may carry ``stopped``, one of
the seven closed words; any word but ``none`` delivers nothing and ends 21 (``stopped``), the word in the counts'
``out.stopped``, instead of the schema or missing-file code 20 (DEC-1101 (2)).

Readings (the lead's brief; the ticket does not spell these out):
- "instead of 20" holds whatever else would refuse 20: the set or the notes missing from out/, or the rest of the
  result failing its schema (a result holding only ``stopped``): a stop word is honoured first;
- "nothing delivered" for a writer's round 1 is: the set's folder ``fixtures/evaluation/<set>/`` not made (it did not
  exist before); for a checker: no ``XCHECK-r<n>.md`` and the set's folder byte-identical before and after;
- a ``stopped`` value outside the seven fails the result's schema: 20, nothing delivered;
- the auditor's result is not in S2 and set-up A's flows are unchanged (a set-up A stop still ends 20: see
  ``test_w2_173_unchanged.py``).
"""

from __future__ import annotations

import json

import pytest

import w2_173_support as s
from w2_173_support import support

WRITER_SET = support.DEFAULT_SET["writer"]          # round 1 makes this set: its folder does not exist before


def writer_set_folder(world):
    return world.sr / "fixtures" / "evaluation" / WRITER_SET


def assert_stopped(world, run, word):
    assert run.code == 21, run.why()
    line = run.line
    assert line["status"] == "stopped" and line["code"] == 21 and line["reason"] == "stopped", line
    assert line["out"].get("stopped") == word, line["out"]
    assert line["delivered"]["files"] == 0 and line["delivered"]["to"] is None, line["delivered"]
    assert s.counts_file(world, line) == line, "counts.json is not the printed line"
    assert s.schema_errors(line) == [], s.schema_errors(line)


def schema(name):
    return json.loads((support.SCHEMAS / name).read_text())


# -- the two result schemas ------------------------------------------------------------------------------------------

@pytest.mark.parametrize("kind", ("writer", "checker"))
def test_s2_the_result_schema_gains_stopped_an_optional_closed_word(kind):
    sch = schema(f"{kind}-result.schema.json")
    good = support.GOOD_RESULT[kind]
    assert support.validate(sch, good) == [], "the first version's result without stopped no longer validates"
    for word in s.STOPPED:
        assert support.validate(sch, dict(good, stopped=word)) == [], f"stopped: {word} is refused by the schema"
    for bad in ("halted", "None", "", 0, None, ["none"]):
        assert support.validate(sch, dict(good, stopped=bad)) != [], f"stopped: {bad!r} passes the schema"
    assert "stopped" not in sch.get("required", []), "stopped is required"


# -- a stop word: nothing delivered, 21 ------------------------------------------------------------------------------

@pytest.mark.parametrize("word", s.STOP_WORDS)
def test_s2_a_writer_result_that_stopped_delivers_nothing_and_ends_21(world, word):
    """Its out/ holds a good set as well: the stop word still wins."""
    assert not writer_set_folder(world).exists()
    run = world.deliver("writer", out=support.good_out("writer", stopped=word))
    assert_stopped(world, run, word)
    assert not writer_set_folder(world).exists(), "the set's folder was made"


@pytest.mark.parametrize("word", s.STOP_WORDS)
def test_s2_a_checker_result_that_stopped_delivers_nothing_and_ends_21(world, word):
    """Its out/ holds well-formed notes as well: the stop word still wins."""
    folder = s.plant_audit_set(world)
    before = s.snapshot(folder)
    run = world.deliver("checker", set_=s.AUDIT_SET, out=s.checker_out(stopped=word))
    assert_stopped(world, run, word)
    assert not (folder / "XCHECK-r1.md").exists(), "the notes were delivered"
    assert s.snapshot(folder) == before, "the set's folder changed"


def test_s2_a_writer_that_stopped_with_no_set_ends_21_not_20(world):
    out = support.good_out("writer", stopped="input-missing")
    out = {k: v for k, v in out.items() if not k.startswith("set/")}
    run = world.deliver("writer", out=out)
    assert_stopped(world, run, "input-missing")
    assert not writer_set_folder(world).exists()


def test_s2_a_checker_that_stopped_with_no_notes_ends_21_not_20(world):
    folder = s.plant_audit_set(world)
    before = s.snapshot(folder)
    out = s.checker_out(stopped="input-malformed")
    del out["notes.md"]
    run = world.deliver("checker", set_=s.AUDIT_SET, out=out)
    assert_stopped(world, run, "input-malformed")
    assert s.snapshot(folder) == before


def test_s2_a_checker_result_holding_only_its_stop_word_ends_21_not_20(world):
    """The rest of the result would fail the schema (its four counts missing): the stop word is honoured first."""
    folder = s.plant_audit_set(world)
    before = s.snapshot(folder)
    run = world.deliver("checker", set_=s.AUDIT_SET,
                        out={"result.json": json.dumps({"stopped": "forbidden-read-needed"})})
    assert_stopped(world, run, "forbidden-read-needed")
    assert s.snapshot(folder) == before


# -- none, or no stopped: delivered as before ------------------------------------------------------------------------

def test_s2_a_writer_result_with_none_and_a_set_delivers_as_before(world):
    run = world.deliver("writer", out=support.good_out("writer", stopped="none"))
    assert run.code == 0, run.why()
    assert run.line["status"] == "delivered" and run.line["delivered"]["to"] == "set", run.line
    assert (writer_set_folder(world) / "hidden" / "q01.yaml").is_file()


def test_s2_a_checker_result_with_none_and_good_notes_delivers_as_before(world):
    folder = s.plant_audit_set(world)
    out = s.checker_out(stopped="none")
    run = world.deliver("checker", set_=s.AUDIT_SET, out=out)
    assert run.code == 0, run.why()
    assert run.line["status"] == "delivered" and run.line["delivered"]["to"] == "notes", run.line
    assert (folder / "XCHECK-r1.md").read_text() == out["notes.md"]


@pytest.mark.parametrize("kind", ("writer", "checker"))
def test_s2_a_result_without_stopped_still_delivers(world, kind):
    """Green today: the first versions' results (no stopped) deliver."""
    if kind == "writer":
        run = world.deliver("writer")
    else:
        s.plant_audit_set(world)
        run = world.deliver("checker", set_=s.AUDIT_SET, out=s.checker_out())
    assert run.code == 0, run.why()
    assert run.line["status"] == "delivered", run.line


# -- a word outside the seven ----------------------------------------------------------------------------------------

@pytest.mark.parametrize("kind", ("writer", "checker"))
def test_s2_a_stopped_word_outside_the_seven_is_a_schema_refusal_20(world, kind):
    if kind == "writer":
        run = world.deliver("writer", out=support.good_out("writer", stopped="halted"))
        delivered_somewhere = writer_set_folder(world).exists()
    else:
        folder = s.plant_audit_set(world)
        before = s.snapshot(folder)
        run = world.deliver("checker", set_=s.AUDIT_SET, out=s.checker_out(stopped="halted"))
        delivered_somewhere = s.snapshot(folder) != before
    assert run.code == 20, run.why()
    assert run.line["status"] == "rejected" and run.line["reason"] == "result", run.line
    assert run.line["delivered"]["files"] == 0 and not delivered_somewhere, "something was delivered"
