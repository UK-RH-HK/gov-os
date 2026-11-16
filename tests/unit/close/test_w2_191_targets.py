"""W2-191 S1 and F1: the test map accepts any project-relative target, and refuses one that leaves the project."""
from __future__ import annotations

import os
from pathlib import Path

import jsonschema
import pytest
import yaml

from gov.close import select

from . import test_w2_191_support as support
from .conftest import Repo

GOOD = ["governance/scripts/tests", "governance/scripts/tests/", "product/tests/test_a.py",
        "product/tests/test_x.py::case", "product/tests/test_x.py::TestC::test_m[a-b]", "tests/unit",
        "tests/acceptance/W1-own/", "a", "f.py::test[a/../b]", "f.py::test_x[..]", "a..b/test_x.py"]
BAD = ["/etc/passwd", "/abs/tests", "../outside", "..", "tests/../../x", "a/../b", "a/..", "../x.py::case",
       "C:/tests", "c:x", "\\\\host\\share", "a\\b", "\\abs",
       "ab:c/../../x", "x/ab:c/../y", "x\n/../../o", "x\n/..", "x/../f.py::case"]


def _validator(pattern=support.TARGET_PATTERN):
    return jsonschema.Draft202012Validator(support.new_schema(pattern))


def _map_with(target: str) -> dict:
    return {"version": 1, "shared_core": ["src/**"], "record_reading": [target], "every_close": [target],
            "couplings": [{"paths": ["src/**"], "suites": [target], "why": "w"}]}


def _write(repo: Repo, data: dict, pattern=support.TARGET_PATTERN) -> None:
    for rel, text in support.schema_file(pattern).items():
        (repo.root / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo.root / rel).write_text(text, encoding="utf-8")
    (repo.root / select.MAP_REL).parent.mkdir(parents=True, exist_ok=True)
    (repo.root / select.MAP_REL).write_text(yaml.safe_dump(data), encoding="utf-8")


# --- S1: the schema --------------------------------------------------------------

@pytest.mark.parametrize("target", GOOD)
def test_s1_the_schema_accepts_a_project_relative_target_in_each_place(target):
    _validator().validate(_map_with(target))


@pytest.mark.parametrize("target", BAD)
def test_s1_the_schema_refuses_an_absolute_or_dotdot_target_in_each_place(target):
    for place in ("record_reading", "every_close", "couplings"):
        data = _map_with("tests/ok")
        if place == "couplings":
            data["couplings"][0]["suites"] = [target]
        else:
            data[place] = [target]
        with pytest.raises(jsonschema.ValidationError):
            _validator().validate(data)


def test_s1_a_map_naming_outside_suites_loads(repo):
    _write(repo, support.map_data())
    loaded, reason = select.load_map(repo.root)
    assert reason is None and loaded == support.map_data()
    assert select.load_map(repo.root)[0]["couplings"][0]["suites"] == ["governance/scripts/tests"]


def test_s1_the_kernel_s_own_example_map_still_loads(repo):
    _write(repo, {"version": 1, "shared_core": ["src/core/**"], "record_reading": ["tests/acceptance/W1-rr/t.py::c"],
                  "every_close": ["tests/unit"],
                  "couplings": [{"paths": ["data/*.txt"], "suites": ["tests/acceptance/W1-cc/"], "why": "w"}]})
    assert select.load_map(repo.root)[1] is None


# --- F1: the loader's own defence ------------------------------------------------

@pytest.mark.parametrize("target", BAD[:8])
def test_f1_the_loader_refuses_an_escaping_target_whatever_the_schema_says(repo, target):
    """A project may carry an older or edited schema copy that judges no target: the loader refuses on its own."""
    for place in ("record_reading", "every_close", "couplings"):
        data = _map_with("tests/ok")
        if place == "couplings":
            data["couplings"][0]["suites"] = [target]
        else:
            data[place] = [target]
        _write(repo, data, pattern=None)
        assert select.load_map(repo.root) == (None, "TEST_MAP_UNREADABLE"), (place, target)


def test_f1_the_old_schema_s_tests_only_rule_refuses_an_outside_target_with_the_same_reason(repo):
    _write(repo, support.map_data(), pattern="^tests/")
    assert select.load_map(repo.root) == (None, "TEST_MAP_UNREADABLE")


def test_f1_a_dotdot_segment_in_the_path_part_before_the_node_id_is_refused_by_the_loader(repo):
    for target in ("a/../b/test_x.py::case", "tests/x/..::case", "x/../../y"):
        _write(repo, _map_with(target), pattern=None)
        assert select.load_map(repo.root) == (None, "TEST_MAP_UNREADABLE"), target


def test_f1_a_target_through_a_link_that_leaves_the_project_is_refused(repo, tmp_path):
    outside = tmp_path / "elsewhere"
    (outside / "tests").mkdir(parents=True)
    (outside / "tests" / "test_o.py").write_text("def test_o():\n    pass\n")
    (repo.root / "inside").mkdir()
    os.symlink(outside, repo.root / "linked")
    os.symlink(outside / "tests" / "test_o.py", repo.root / "inside" / "test_link.py")
    for target in ("linked", "linked/tests", "linked/tests/test_o.py::test_o", "linked/not/there", "inside/test_link.py",
                   "inside/test_link.py::test_o"):
        _write(repo, _map_with(target), pattern=None)
        assert select.load_map(repo.root) == (None, "TEST_MAP_UNREADABLE"), target
        _write(repo, _map_with(target))  # and with the new schema
        assert select.load_map(repo.root) == (None, "TEST_MAP_UNREADABLE"), target


def test_f1_a_link_that_stays_inside_the_project_is_no_escape(repo):
    (repo.root / "real" / "tests").mkdir(parents=True)
    os.symlink(repo.root / "real", repo.root / "alias")
    os.symlink("real", repo.root / "rel_alias")  # a relative link too
    for target in ("alias/tests", "rel_alias/tests", "real/tests"):
        _write(repo, _map_with(target))
        assert select.load_map(repo.root)[1] is None, target


def test_f1_a_project_reached_through_a_link_itself_is_not_an_escape(repo, tmp_path):
    (repo.root / "governance" / "scripts" / "tests").mkdir(parents=True)
    _write(repo, support.map_data())
    via = tmp_path / "via"
    os.symlink(repo.root, via)
    assert select.load_map(Path(via))[1] is None


def test_f1_a_target_that_names_nothing_is_not_the_loader_s_to_refuse(repo):
    """A missing folder, file or case stays refused at the selection (``unresolved``), as today."""
    _write(repo, _map_with("governance/scripts/gone/test_none.py::test_none"))
    loaded, reason = select.load_map(repo.root)
    assert reason is None and loaded["record_reading"] == ["governance/scripts/gone/test_none.py::test_none"]


def test_f1_a_project_with_tests_targets_loads_to_the_same_map_as_before(repo):
    data = {"version": 1, "shared_core": ["src/core/**"], "record_only": [".tickets/**.md"],
            "record_reading": ["tests/acceptance/W1-rr/test_rr.py::test_reads"], "every_close": [],
            "couplings": [{"paths": ["data/*.txt"], "suites": ["tests/acceptance/W1-cc/"], "why": "a text read"}]}
    _write(repo, data)
    assert select.load_map(repo.root) == (data, None)
