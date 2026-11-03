"""S3: a retrieval miss is recorded as a memory-quality event with its root cause, its repair and a held-out
regression case [CAP-19.c: a miss is a memory-quality event -> root cause -> repair -> held-out regression test].

No specification names the event's interface; these cases assume the one the README states ("The interface these
cases assume", S3) and the test designer's return proposes: ``gov.retrieval.learning.record(root, miss)`` and
``gov.retrieval.learning.events(root)``. What they judge is the line's substance:

- the event is a durable record (a file in the project, outside the disposable ``.gov-runtime/``) of the miss, its
  root cause and its repair, typed ``memory-quality``;
- an event without its root cause, its repair, its regression case or the miss itself is refused, and nothing is
  written;
- the regression case is a question in the standing measure's form (``question``, ``gold_answer``, ``sources``; W2-61)
  that asks the missed question with the expected sources, in a file of its own;
- held out: the case is kept out of what memory embeds (DEC-1052: tests and probe records stay out of the vectors).
"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

import w2_32_support as s

QUESTION, GOLD = s.QUESTIONS[0]
MISS = {
    "question": QUESTION,
    "expected": [{"path": GOLD}],
    "observed": ["docs/bakery.md", "docs/lighthouse.md", "README.md"],
    "root_cause": "the harbour note was chunked after its heading only, so its tide-table sentence had no vector",
    "repair": "chunking keeps a heading with its first paragraph; the store re-embedded",
    "regression": {"question": QUESTION, "gold_answer": "Every Monday at dawn.", "sources": [{"path": GOLD}]},
}
REQUIRED = ("question", "expected", "root_cause", "repair", "regression")


def _record(box, project, miss=MISS):
    return box.call("learning_record", root=str(project), miss=miss)


def _load(project, rel):
    path = Path(project) / rel
    assert path.is_file(), f"the file the event names is not in the project: {rel}"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_a_miss_is_recorded_as_a_memory_quality_event_with_its_root_cause_and_repair(project, box):
    event = s.result(_record(box, project))
    assert event["type"] == "memory-quality" and event.get("id"), event
    assert (event["question"], event["root_cause"], event["repair"]) == \
        (MISS["question"], MISS["root_cause"], MISS["repair"]), event
    rel = event["path"]
    assert not Path(rel).is_absolute() and not rel.startswith(".gov-runtime/"), \
        f"the event is a durable record in the project, not in the disposable runtime folder: {rel}"
    stored = _load(project, rel)
    for field in ("question", "root_cause", "repair"):
        assert stored[field] == MISS[field], f"the event file holds its {field}: {stored}"
    assert stored.get("type") == "memory-quality", stored
    assert event["regression_case"] in yaml.safe_dump(stored), "the event file names its regression case"


@pytest.mark.parametrize("field", REQUIRED)
@pytest.mark.parametrize("how", ["missing", "empty"])
def test_an_event_without_one_of_its_parts_is_refused_and_nothing_is_written(project, box, field, how):
    miss = copy.deepcopy(MISS)
    if how == "missing":
        del miss[field]
    else:
        miss[field] = {"expected": [], "regression": {}}.get(field, "")
    before = s.files_of(project)
    data = _record(box, project, miss)
    raised = data.get("raised")
    assert raised is not None, f"an event without its {field} was recorded: {data.get('result')}"
    assert any(kind in raised["types"] for kind in ("ValueError", "GovError")), \
        f"the refusal is a named error (a ValueError or a GovError), not {raised['type']}: {raised['message']}"
    assert field in raised["message"], f"the refusal names the missing part ({field}): {raised['message']}"
    assert s.files_of(project) == before, "a refused event writes nothing"


@pytest.mark.parametrize("part", ["question", "gold_answer", "sources"])
def test_a_regression_case_not_in_the_measures_form_is_refused(project, box, part):
    miss = copy.deepcopy(MISS)
    del miss["regression"][part]
    before = s.files_of(project)
    raised = _record(box, project, miss).get("raised")
    assert raised is not None and part in raised["message"], \
        f"a regression case without its {part} is refused, naming it: {raised}"
    assert s.files_of(project) == before


def test_the_regression_case_is_a_question_in_the_measures_form_in_a_file_of_its_own(project, box):
    event = s.result(_record(box, project))
    rel = event["regression_case"]
    assert rel != event["path"], "the regression case is a file of its own"
    case = _load(project, rel)
    assert case["question"] == QUESTION, case
    assert str(case.get("gold_answer") or "").strip(), case
    assert [source["path"] for source in case["sources"]] == [GOLD], case


def test_the_regression_case_is_held_out_of_what_memory_embeds(project, box, standin):
    event = s.result(_record(box, project))
    s.commit(project, "the memory-quality event")
    box.built(project)
    embedded = s.vector_paths(project)
    assert GOLD in embedded, "premise: the planted notes are embedded"
    assert event["regression_case"] not in embedded, \
        f"the held-out regression case was embedded into memory: {event['regression_case']}"


def test_recorded_events_are_read_back(project, box):
    first = s.result(_record(box, project))
    other = copy.deepcopy(MISS)
    other["question"] = other["regression"]["question"] = s.QUESTIONS[1][0]
    other["expected"] = other["regression"]["sources"] = [{"path": s.QUESTIONS[1][1]}]
    second = s.result(_record(box, project, other))
    assert first["id"] != second["id"], "each event has an id of its own"
    events = {event["id"]: event for event in s.result(box.call("learning_events", root=str(project)))}
    assert set(events) >= {first["id"], second["id"]}, events
    for recorded in (first, second):
        read = events[recorded["id"]]
        assert (read["type"], read["question"], read["root_cause"], read["repair"]) == \
            ("memory-quality", recorded["question"], recorded["root_cause"], recorded["repair"]), read
