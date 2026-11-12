"""S4 and failure line 2 (its classes part): the memory auditor's ``classes.json`` checked at delivery against the audit
auditor brief's fixed form (auditor.md §6): one entry per line of ``input/misses.jsonl`` and none for another id, each
``class`` one of the five, each ``reason`` one line of at most 200 characters, and the five ``misses`` counts of
``result.json`` equal to the classes' counts. Anything else delivers nothing and ends 20 (DEC-1101 (2)).

The form, as the lead's brief reads it: an object ``{"<id>": {"class": ..., "reason": ...}}``. The misses are W2-149's
planted ``runs/audit-1/misses.jsonl`` (ids m1, m2, m3). This is the memory auditor (``auditor-result.schema.json``),
not set-up A's overlap auditor.

Readings: "nothing delivered" is no ``miss-classes.json``, no new ``AUDITS.log`` line and the audit's folder
``runs/audit-1/`` identical entry for entry before and after; the good results name all five counts (zeros included),
so whether a result that leaves out a zero count still delivers is not tested; "at most 200 characters" counts
characters (code points), and a reason of exactly 200 is delivered.
"""

from __future__ import annotations

import json

import pytest

import w2_173_support as s
from w2_173_support import support


def launch_auditor(world, out):
    folder = s.audit_folder(world)
    before, log_before = s.snapshot(folder), s.audits_log(world)
    run = world.deliver("auditor", out=out)
    return run, folder, before, log_before


def assert_refused_20(world, run, folder, before, log_before):
    assert run.code == 20, run.why()
    line = run.line
    assert line["status"] == "rejected" and line["reason"] == "result", line
    assert line["delivered"]["files"] == 0 and line["delivered"]["to"] is None, line["delivered"]
    assert not (folder / "miss-classes.json").exists(), "the classes were delivered"
    assert s.snapshot(folder) == before, "the audit's folder changed"
    assert s.audits_log(world) == log_before, "AUDITS.log gained a line"
    assert s.schema_errors(line) == [], s.schema_errors(line)


def classes_with(**changes):
    c = {k: dict(v) for k, v in s.GOOD_CLASSES.items()}
    for k, v in changes.items():
        if v is None:
            c.pop(k, None)
        else:
            c[k] = v
    return c


# -- well formed -----------------------------------------------------------------------------------------------------

def test_s4_well_formed_classes_are_delivered(world):
    out = s.auditor_out()
    run, folder, _before, log_before = launch_auditor(world, out)
    assert run.code == 0, run.why()
    line = run.line
    assert line["status"] == "delivered" and line["delivered"]["to"] == "classes", line
    assert (folder / "miss-classes.json").read_text() == out["classes.json"]
    assert s.audits_log(world) != log_before, "AUDITS.log did not gain the audit's line"


def test_s4_well_formed_classes_using_all_five_classes_are_delivered(world):
    """Five misses, one of each class (W2-149's three planted misses topped up to five)."""
    rows = [{"id": f"m{n}", "question": "planted", "gold": "x", "answer": "y"} for n in range(1, 6)]
    support.write_file(world.sr, "runs/audit-1/misses.jsonl", "".join(json.dumps(r) + "\n" for r in rows))
    classes = {f"m{n}": {"class": c, "reason": "the item and its form in general terms"}
               for n, c in enumerate(s.MISS_CLASSES, start=1)}
    run, folder, _b, _l = launch_auditor(world, s.auditor_out(classes))
    assert run.code == 0, run.why()
    assert (folder / "miss-classes.json").is_file()


def test_s4_a_reason_of_exactly_200_characters_is_delivered(world):
    run, folder, _b, _l = launch_auditor(world, s.auditor_out(classes_with(
        m3={"class": "gold_wrong", "reason": "r" * 200})))
    assert run.code == 0, run.why()
    assert (folder / "miss-classes.json").is_file()


# -- anything else: 20, nothing delivered -----------------------------------------------------------------------------

BAD = {
    # S4's Verify, by name
    "a-missing-id": classes_with(m3=None),
    "an-extra-id": classes_with(m4={"class": "out_of_scope", "reason": "the answer is in no indexed file"}),
    "a-sixth-class": classes_with(m3={"class": "search_wrong", "reason": "the gold span ends early"}),
    "a-two-line-reason": classes_with(m3={"class": "gold_wrong", "reason": "the gold span ends\nbefore the line"}),
    # the form's other limits (S4: "anything else")
    "a-201-character-reason": classes_with(m3={"class": "gold_wrong", "reason": "r" * 201}),
    "a-class-as-a-bare-word": classes_with(m3="gold_wrong"),
    "no-reason": classes_with(m3={"class": "gold_wrong"}),
}


@pytest.mark.parametrize("which", sorted(BAD))
def test_s4_classes_that_do_not_fit_the_form_are_refused_20(world, which):
    """Failure line 2. The result's five counts are taken from the classes as written (a word outside the five
    counted in none), so only the form can refuse."""
    classes = BAD[which]
    run, folder, before, log_before = launch_auditor(world, s.auditor_out(classes))
    assert_refused_20(world, run, folder, before, log_before)


@pytest.mark.parametrize("misses", (
    {"gold_wrong": 2, "question_ambiguous": 0, "retrieval_miss": 1, "answer_wrong": 0, "out_of_scope": 0},
    {"gold_wrong": 1, "question_ambiguous": 0, "retrieval_miss": 2, "answer_wrong": 1, "out_of_scope": 0},
    {"gold_wrong": 0, "question_ambiguous": 1, "retrieval_miss": 2, "answer_wrong": 0, "out_of_scope": 0},
), ids=("swapped", "one-too-many", "moved"))
def test_s4_result_counts_that_disagree_with_the_classes_are_refused_20(world, misses):
    run, folder, before, log_before = launch_auditor(world, s.auditor_out(misses=misses))
    assert_refused_20(world, run, folder, before, log_before)
