"""W2-61, failure 4 -- a hit counts only from the governing source.

Failure 4: "A hit counted from lens B's own report or from the evaluation files rather than from the governing
source."

An item from a path the set itself declares (its ``visible`` or ``hidden`` parts in the path map; for
memory-retrieval, lens B's report), from ``fixtures/evaluation/**``, or from a test that only quotes the answer is
never a hit, whatever it holds. A question whose ``sources`` name such a path may be refused, naming its id, but is
never counted as a hit.

The planted set ``planted-memory`` declares ``docs/assessment/planted-report.md`` as its visible part (as the real
set declares lens B's report). The planted report, a planted file under ``fixtures/evaluation/`` and a planted test
each quote v03's gold answer word for word, and the planted retrieval ranks them first; the governing source
(``## DEC-3 The gate``) comes sixth.

Red now: ``gov.retrieval.measure`` does not exist.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_61_support as s  # noqa: E402

GATE = "## DEC-3 The gate"


def test_quotes_ranked_first_are_no_hit_and_the_governing_source_sixth_is_no_hit_at_5(tmp_path):
    world = s.make_world(tmp_path, commit=False)
    s.standard_questions(world)
    world.commit()
    for rel in (s.REPORT, s.FIXTURE_QUOTE, s.TEST_QUOTE):
        assert s.GATE_ANSWER in (world.repo / rel).read_text(encoding="utf-8")
    document = world.measure(s.SET, "--json").json()
    v03 = s.question(document, "v03")
    assert v03.get("hit_at_5") is False, f"v03 counted a hit from a quote of its answer: {v03}"
    assert v03.get("first_gold_rank") == 6, f"v03's governing source is sixth: {v03}"
    assert (v03.get("in_bundle"), v03.get("full_evidence")) == (True, True), f"v03: {v03}"


QUOTING = {
    "the-set-s-own-report": s.REPORT,
    "an-evaluation-file": s.FIXTURE_QUOTE,
    "a-hidden-path-the-set-declares": f"fixtures/evaluation/{s.SET}/hidden/notes.md",
}


@pytest.mark.parametrize("case", sorted(QUOTING))
def test_a_source_naming_a_quoting_path_is_never_a_hit(tmp_path, case):
    rel = QUOTING[case]
    world = s.make_world(tmp_path, files={rel: f"The gate needs {s.GATE_ANSWER}.\n"}, commit=False)
    world.question("q01", {"question": "Where does the report say what the gate needs?",
                           "gold_answer": s.GATE_ANSWER, "sources": [{"path": rel}]},
                   [[world.item(rel), world.section(s.DECISIONS, GATE)]])
    world.commit()
    run = world.measure(s.SET, "--json")
    if run.returncode != 0:
        assert "q01" in run.output, f"{case}: the refusal does not name the question\n{run.describe()}"
        return
    q01 = s.question(run.json(), "q01")
    assert q01.get("hit_at_5") is False and q01.get("in_bundle") is False and q01.get("full_evidence") is False, (
        f"{case}: a source naming {rel} was counted: {q01}")


def test_an_alternative_naming_the_report_never_counts_the_governing_alternative_does(tmp_path):
    world = s.make_world(tmp_path, commit=False)
    world.question("q01", {"question": "What does the gate need, by the report or the register?",
                           "gold_answer": s.GATE_ANSWER,
                           "sources": [[{"path": s.REPORT}, {"path": s.DECISIONS, "heading": GATE}]]},
                   [[world.item(s.REPORT), world.noise(1), world.noise(2), world.noise(3), world.noise(4),
                     world.section(s.DECISIONS, GATE)]])
    world.commit()
    run = world.measure(s.SET, "--json")
    if run.returncode != 0:
        assert "q01" in run.output, f"the refusal does not name the question\n{run.describe()}"
        return
    q01 = s.question(run.json(), "q01")
    assert q01.get("hit_at_5") is False, f"the report at rank 1 was counted: {q01}"
    assert q01.get("first_gold_rank") == 6, f"the governing alternative is sixth: {q01}"
