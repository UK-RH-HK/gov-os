"""W2-32 S3 (CAP-19.c): a retrieval miss is recorded as a memory-quality event with its root cause, its repair and a
held-out regression case, in the standing measure's question form. Regression evidence only (DEC-136): no store, no
model; each project is a temporary folder.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.retrieval import learning  # noqa: E402

MISS = {"question": "Who fires the bowls in the kiln?",
        "expected": [{"path": "docs/kiln.md"}],
        "observed": ["docs/glaze.md", "docs/clay.md"],
        "root_cause": "the kiln's section is one chunk past the embedding cut",
        "repair": {"summary": "smaller spans for docs/", "commit": "0123456789ab"},
        "regression": {"question": "Which hand fires the bowls?", "gold_answer": "The potter's apprentice.",
                       "sources": [{"path": "docs/kiln.md", "heading": "## Firing"}]}}


def _files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())


def test_a_miss_is_written_as_an_event_and_a_case_of_its_own(tmp_path):
    event = learning.record(tmp_path, copy.deepcopy(MISS))
    assert event["type"] == "memory-quality" and event["id"].startswith("MQ-")
    assert (event["question"], event["root_cause"], event["repair"]) == \
        (MISS["question"], MISS["root_cause"], MISS["repair"])
    assert event["path"] == f"{learning.EVENTS_REL}/{event['id']}.yaml"
    assert event["regression_case"] == f"{learning.CASES_REL}/{event['id']}.yaml"
    assert not event["path"].startswith(".gov-runtime/") and not event["regression_case"].startswith(".gov-runtime/")
    assert _files(tmp_path) == sorted([tmp_path / event["path"], tmp_path / event["regression_case"]])
    stored = yaml.safe_load((tmp_path / event["path"]).read_text())
    assert stored == event and stored["expected"] == MISS["expected"] and stored["observed"] == MISS["observed"]
    case = yaml.safe_load((tmp_path / event["regression_case"]).read_text())
    assert {key: case[key] for key in ("question", "gold_answer", "sources")} == MISS["regression"]
    assert case["id"] == event["id"]


def test_events_lists_every_event_with_the_same_fields(tmp_path):
    first = learning.record(tmp_path, copy.deepcopy(MISS))
    second = learning.record(tmp_path, {**copy.deepcopy(MISS), "question": "Where is the glaze kept?"})
    third = learning.record(tmp_path, copy.deepcopy(MISS))  # the same miss twice: two events, two cases
    assert len({first["id"], second["id"], third["id"]}) == 3
    (tmp_path / learning.EVENTS_REL / "notes.yaml").write_text("not: an event\n")
    assert sorted(e["id"] for e in learning.events(tmp_path)) == sorted([first["id"], second["id"], third["id"]])
    assert all(set(learning.FIELDS) <= set(e) for e in learning.events(tmp_path))
    assert learning.events(tmp_path / "nowhere") == []


@pytest.mark.parametrize("part", ["question", "expected", "root_cause", "repair", "regression"])
@pytest.mark.parametrize("how", ["absent", "empty"])
def test_a_miss_without_a_part_names_it_and_writes_nothing(tmp_path, part, how):
    miss = copy.deepcopy(MISS)
    if how == "absent":
        del miss[part]
    else:
        miss[part] = "" if isinstance(miss[part], str) else type(miss[part])()
    with pytest.raises(ValueError, match=part):
        learning.record(tmp_path, miss)
    assert _files(tmp_path) == []


@pytest.mark.parametrize("part", ["question", "gold_answer", "sources"])
def test_a_case_without_a_part_names_it_and_writes_nothing(tmp_path, part):
    miss = copy.deepcopy(MISS)
    del miss["regression"][part]
    with pytest.raises(ValueError, match=part):
        learning.record(tmp_path, miss)
    assert _files(tmp_path) == []


@pytest.mark.parametrize("miss", [{"id": "H07"}, {"id": "h07"}, {"id": "H12", "part": "hidden"},
                                  {"id": "q3", "part": "hidden"}])  # h07: the measure's own form (review F-1)
def test_a_hidden_miss_is_recorded_by_its_id_only(tmp_path, miss):
    """The CTO's ruling under S3: nothing of a hidden question is written into the repository, and no case."""
    event = learning.record(tmp_path, dict(miss))
    assert event["type"] == "memory-quality" and event["question_id"] == miss["id"] and event["part"] == "hidden"
    assert event["question"] is None and event["regression_case"] is None
    assert _files(tmp_path) == [tmp_path / event["path"]]
    stored = yaml.safe_load((tmp_path / event["path"]).read_text())
    assert stored == event and not {"expected", "observed", "gold_answer", "sources", "regression"} & set(stored)
    assert [e["id"] for e in learning.events(tmp_path)] == [event["id"]]


@pytest.mark.parametrize("extra", ["question", "expected", "observed", "root_cause", "repair", "regression",
                                   "gold_answer", "sources"])
@pytest.mark.parametrize("marker", [{"id": "H07"}, {"id": "h07"}, {"id": "q3", "part": "hidden"}])
def test_a_hidden_miss_carrying_more_than_its_id_is_refused_and_nothing_is_written(tmp_path, extra, marker):
    miss = {**copy.deepcopy(MISS), **marker}
    miss.setdefault(extra, MISS["regression"].get(extra, "x"))
    miss = {key: value for key, value in miss.items() if key in (extra, *marker)}
    with pytest.raises(ValueError, match=extra):
        learning.record(tmp_path, miss)
    assert _files(tmp_path) == []


def test_a_hidden_miss_without_an_id_is_refused(tmp_path):
    with pytest.raises(ValueError, match="no id"):
        learning.record(tmp_path, {"part": "hidden"})
    assert _files(tmp_path) == []


def test_a_visible_miss_keeps_its_question_id(tmp_path):
    event = learning.record(tmp_path, {**copy.deepcopy(MISS), "id": "q07", "part": "visible"})
    assert (event["question_id"], event["part"]) == ("q07", "visible") and event["regression_case"]


@pytest.mark.parametrize("change", [{"expected": [{"heading": "x"}]}, {"observed": "docs/a.md"},
                                    {"regression": {**MISS["regression"], "sources": [{"lines": [1, 2]}]}},
                                    {"root_cause": 7}])
def test_a_malformed_part_is_refused_and_nothing_is_written(tmp_path, change):
    with pytest.raises(ValueError):
        learning.record(tmp_path, {**copy.deepcopy(MISS), **change})
    assert _files(tmp_path) == []
