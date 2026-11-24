"""Builder tests for the fix under W2-88 (DAEO-2bdu): ``FABRIC_INCOMPLETE`` names each file in neither list, and each in
both. Regression evidence only (MR-3)."""
from __future__ import annotations

import pytest

from gov.adopt import fabric
from gov.cli.errors import GovError

OFF = {"requested": False}
LEXICAL = {"indexed": ["a.md", "b.md", "x.py"], "refused": []}


def stores(vectors=None, codegraph=None, lexical=LEXICAL):
    return {"stores": {"lexical": lexical, "vectors": vectors or OFF, "codegraph": codegraph or OFF}}


def refusal(record, tracked=("a.md", "b.md", "x.py")):
    with pytest.raises(GovError) as raised:
        fabric.check_coverage(record, tracked)
    assert raised.value.code == "FABRIC_INCOMPLETE"
    return raised.value


def test_a_vectors_file_judged_and_in_neither_list_is_named():
    vectors = {"judged": 3, "judged_files": ["a.md", "b.md", "x.py"], "indexed": ["a.md"],
               "refused": [{"path": "b.md", "reason": "not-embedded"}]}
    error = refusal(stores(vectors))
    assert error.details["missing"] == ["x.py"] and error.details["both"] == []
    assert "vectors" in error.message and "x.py" in error.message


def test_the_missing_paths_are_collected_over_every_store_and_sorted():
    lexical = {"indexed": ["a.md"], "refused": []}
    vectors = {"judged": 1, "judged_files": ["z.md"], "indexed": [], "refused": []}
    code = {"judged": 1, "judged_files": ["m.py"], "indexed": [], "refused": []}
    error = refusal(stores(vectors, code, lexical), ["a.md", "b.md"])
    assert error.details["missing"] == ["b.md", "m.py", "z.md"]
    assert all(path in error.message for path in ("b.md", "m.py", "z.md"))


def test_a_file_in_both_lists_is_named_and_raises():
    code = {"judged": 1, "judged_files": ["x.py"], "indexed": ["x.py"], "refused": [{"path": "x.py", "reason": "secrets"}]}
    error = refusal(stores(codegraph=code))
    assert error.details["both"] == ["x.py"] and error.details["missing"] == [] and "x.py" in error.message


def test_a_record_without_judged_files_keeps_the_count_message_and_still_raises():
    vectors = {"judged": 2, "indexed": ["a.md"], "refused": []}
    error = refusal(stores(vectors))
    assert "vectors: 1 file(s) judged and in neither list" in error.message
    assert error.details["missing"] == [] and error.details["both"] == []


def test_a_complete_record_that_names_its_judged_files_raises_nothing():
    vectors = {"judged": 2, "judged_files": ["a.md", "b.md"], "indexed": ["a.md"],
               "refused": [{"path": "b.md", "reason": "not-embedded"}]}
    fabric.check_coverage(stores(vectors), ["a.md", "b.md", "x.py"])
