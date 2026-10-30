"""W2-61, KPI success 3 and 4, failure 3 -- the scores, per question and in total, both figures together.

KPI 3: "A measurement script reports, per question and in total, whether the governing source is in the first five
and in the bundle, and repeatability on an unchanged index and after a rebuild; it prints scores, never the hidden
answers [DEC-828 item 4, DEC-820 (d)]".
KPI 4: "Both figures, always together: hit@5 against CAP-10's floor of 85, and the share of questions whose stacked
context holds all their needed evidence, across batches, against the owner's target of 99 % [DEC-833 items 1 to 3]".
Failure 3: "A figure reported without the other."

The planted set ``planted-memory`` (``w2_61_support.standard_questions``), measured as an unmeasured session:

- v01: the governing source at rank 2 of one call: hit@5, in the bundle, full evidence;
- v02: two pieces, the second only in the second batch (rank 5): hit@5, in the bundle, full evidence, 2 calls;
- v03: the set's own report, an evaluation file and a test quote the answer at ranks 1-3, the governing source at
  rank 6: no hit@5, in the bundle, full evidence (failure KPI 4);
- v04: never retrieved: nothing.

Totals: hit@5 2 of 4, in the bundle 3 of 4, full evidence 3 of 4.

Repeatability (``--compare``): the same run against its own earlier record is the same for every question; after
the planted retrieval's answer changes (as after a rebuild), the questions that changed are named with the figures
that differ. The comparison's JSON form is this file's (no other fixes it): each question object carries
``compare``, one object per ``--compare`` record, with ``same`` (true or false) and ``differs`` (the names of what
differs: ``hit_at_5``, ``in_bundle``, ``full_evidence``, ``first_gold_rank``, and a name of the measure's own for
the stacked items' digest).

Red now: ``gov.retrieval.measure`` does not exist.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_61_support as s  # noqa: E402

FIGURES = ("hit_at_5", "in_bundle", "full_evidence", "first_gold_rank")
EXPECTED = {
    # id: (hit_at_5, in_bundle, full_evidence, first_gold_rank, pieces_found, pieces_needed, calls)
    "v01": (True, True, True, 2, 1, 1, 1),
    "v02": (True, True, True, 3, 2, 2, 2),
    "v03": (False, True, True, 6, 1, 1, 1),
    "v04": (False, False, False, None, 0, 1, 1),
}


@pytest.fixture
def world(tmp_path):
    w = s.make_world(tmp_path, commit=False)
    s.standard_questions(w)
    w.commit()
    return w


def test_per_question_figures(world):
    document = world.measure(s.SET, "--json").json()
    assert [q.get("id") for q in s.questions(document)] == list(EXPECTED), "the questions are not in file order"
    for qid, (hit, bundle, full, rank, found, needed, calls) in EXPECTED.items():
        got = s.question(document, qid)
        want = {"hit_at_5": hit, "in_bundle": bundle, "full_evidence": full, "first_gold_rank": rank,
                "pieces_found": found, "pieces_needed": needed, "calls": calls}
        have = {key: got.get(key, "<missing>") for key in want}
        assert have == want, f"{qid}: the measure gives {have}, not {want}"


def test_totals_against_the_floor_and_the_target(world):
    document = world.measure(s.SET, "--json").json()
    total = document.get("total")
    assert isinstance(total, dict), f"no total: {sorted(document)}"
    assert total.get("questions") == 4, f"total questions: {total.get('questions')!r}"
    hit, full = total.get("hit_at_5"), total.get("full_evidence")
    assert isinstance(hit, dict) and isinstance(full, dict), f"the totals are not both given: {total}"
    assert (hit.get("count"), hit.get("of"), hit.get("floor")) == (2, 4, 85), f"total hit@5: {hit}"
    assert (full.get("count"), full.get("of"), full.get("target")) == (3, 4, 99), f"total full evidence: {full}"
    assert abs(float(hit.get("percent")) - 50.0) < 0.6, f"hit@5 percent: {hit.get('percent')!r}"
    assert abs(float(full.get("percent")) - 75.0) < 0.6, f"full evidence percent: {full.get('percent')!r}"


def test_the_text_output_gives_both_figures_together_against_85_and_99(world):
    run = world.measure(s.SET)
    assert run.returncode == 0, run.describe()
    lone = s.lone_figures(run.stdout)
    assert not lone, f"text lines give one figure without the other (failure 3):\n" + "\n".join(lone)
    both = [line for line in run.stdout.splitlines() if s.HIT_LABEL.search(line) and s.FULL_LABEL.search(line)]
    assert both, f"no line gives hit@5 and full evidence\n{run.describe()}"
    assert any("85" in line and "99" in line for line in both), (
        f"no line gives the totals against 85 and 99\n{run.describe()}")
    for qid in EXPECTED:
        assert any(qid in line for line in run.stdout.splitlines()), f"{qid} is not in the text output"


def test_every_json_object_and_the_record_give_both_figures(world):
    out = world.base / "out"
    run = world.measure(s.SET, "--json", "--out", out)
    document = run.json()
    assert not s.lone_objects(document), f"objects give one figure only: {s.lone_objects(document)}"
    records = s.records_in(out)
    assert len(records) == 1, f"--out wrote {len(records)} JSON files, not one: {sorted(map(str, records))}"
    (path, record), = records.items()
    assert record == document, f"the record {path.name} is not the --json document"
    assert not s.lone_objects(record), f"record objects give one figure only: {s.lone_objects(record)}"


def test_a_second_out_run_writes_a_new_record(world):
    out = world.base / "out"
    world.measure(s.SET, "--out", out)
    first = s.records_in(out)
    world.measure(s.SET, "--out", out)
    second = s.records_in(out)
    assert len(first) == 1 and len(second) == 2 and set(first) <= set(second), (
        f"a second run did not add one new record: {sorted(map(str, first))} then {sorted(map(str, second))}")


def test_the_run_ends_with_0_whatever_the_figures(world):
    run = world.measure(s.SET)
    assert run.returncode == 0, f"the measure did not end with 0 on a run with misses\n{run.describe()}"


# --------------------------------------------------------------------------
# Repeatability: --compare
# --------------------------------------------------------------------------

def _compare(question, n=1):
    entries = question.get("compare")
    assert isinstance(entries, list) and len(entries) == n, (
        f"{question.get('id')}: compare is not a list of {n}: {entries!r}")
    for entry in entries:
        assert isinstance(entry, dict) and isinstance(entry.get("same"), bool) and isinstance(
            entry.get("differs"), list), f"{question.get('id')}: a compare entry is not {{same, differs}}: {entry!r}"
    return entries


def _first_record(world):
    out = world.base / "first"
    world.measure(s.SET, "--out", out)
    records = s.records_in(out)
    assert len(records) == 1, f"--out wrote {len(records)} records"
    return next(iter(records))


def test_compare_on_an_unchanged_index_is_the_same_for_every_question(world):
    record = _first_record(world)
    run = world.measure(s.SET, "--json", "--compare", record)
    document = run.json()
    for qid in EXPECTED:
        entry, = _compare(s.question(document, qid))
        assert entry["same"] is True and entry["differs"] == [], f"{qid}: unchanged, but compared as {entry}"
    assert not s.lone_objects(document), f"objects give one figure only: {s.lone_objects(document)}"
    text = world.measure(s.SET, "--compare", record)
    assert text.returncode == 0, text.describe()
    named = [line for line in text.stdout.splitlines()
             if "differ" in line.lower() and any(qid in line for qid in EXPECTED)]
    assert not named, f"the text names a difference on an unchanged index: {named}"


def test_compare_after_a_rebuild_names_each_question_and_figure_that_differs(world):
    record = _first_record(world)
    dec = s.DECISIONS
    # As after a rebuild: v01's governing source falls to rank 6; v04's two items swap places; v02, v03 unchanged.
    world.answer("What is the packet ceiling?",
                 [[world.noise(1), world.noise(2), world.noise(3), world.noise(4), world.noise(5),
                   world.section(dec, "## DEC-1 The packet ceiling")]])
    world.answer("How does a session resume?", [[world.noise(5), world.noise(4)]])
    out = world.base / "second"
    run = world.measure(s.SET, "--json", "--compare", record, "--out", out)
    document = run.json()
    v01, = _compare(s.question(document, "v01"))
    assert v01["same"] is False, f"v01 changed, but compared as {v01}"
    assert {"hit_at_5", "first_gold_rank"} <= set(v01["differs"]), f"v01 differs: {v01['differs']}"
    assert not {"in_bundle", "full_evidence"} & set(v01["differs"]), f"v01 differs: {v01['differs']}"
    assert set(v01["differs"]) - set(FIGURES), f"v01's stacked items changed, but no digest differs: {v01}"
    v04, = _compare(s.question(document, "v04"))
    assert v04["same"] is False and v04["differs"] and not set(v04["differs"]) & set(FIGURES), (
        f"v04's items swapped places, its figures did not: {v04}")
    for qid in ("v02", "v03"):
        entry, = _compare(s.question(document, qid))
        assert entry["same"] is True and entry["differs"] == [], f"{qid}: unchanged, but compared as {entry}"
    (path, saved), = s.records_in(out).items()
    assert saved == document, f"the record {path.name} does not hold the comparison of the run"
    text = world.measure(s.SET, "--compare", record)
    assert any("v01" in line and "differ" in line.lower() for line in text.stdout.splitlines()), (
        f"the text output does not name v01 as differing\n{text.describe()}")
    assert not s.lone_figures(text.stdout), "\n".join(s.lone_figures(text.stdout))


def test_compare_takes_more_than_one_record(world):
    first = _first_record(world)
    out = world.base / "again"
    world.measure(s.SET, "--out", out)
    second = next(iter(s.records_in(out)))
    document = world.measure(s.SET, "--json", "--compare", first, "--compare", second).json()
    for qid in EXPECTED:
        entries = _compare(s.question(document, qid), n=2)
        assert all(entry["same"] for entry in entries), f"{qid}: {entries}"
