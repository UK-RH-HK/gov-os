"""Builder tests of ``gov.close.select`` (W2-66): the test map, the base, the change and the selection's form."""
from __future__ import annotations

import json

import yaml

from gov.close import select

from .conftest import Repo

TICKET_TEXT = "---\nid: P-{wbs}\nwbs_id: {wbs}\nallowed_paths:\n{paths}---\n"
MAP = {"version": 1, "shared_core": ["src/core/**"], "record_only": [".tickets/**.md", "docs/close/**.md",
                                                                "docs/close/nightly/*.json"],
       "record_reading": ["tests/acceptance/W1-rr/test_rr.py::test_reads"], "every_close": [],
       "couplings": [{"paths": ["data/*.txt"], "suites": ["tests/acceptance/W1-cc/"], "why": "a text read"}]}


def _ticket(wbs: str, *paths: str) -> str:
    return TICKET_TEXT.format(wbs=wbs, paths="".join(f"- {p}\n" for p in paths))


def _project(repo: Repo, test_map: dict | None = MAP) -> str:
    files = {
        ".tickets/P-W1-aa.md": _ticket("W1-aa", "src/a/**"),
        ".tickets/P-W1-own.md": _ticket("W1-own", "src/own/**"),
        "src/a/x.py": "x = 1\n", "src/own/y.py": "y = 1\n", "src/core/z.py": "z = 1\n", "data/t.txt": "t\n",
        "tests/unit/test_u.py": "def test_u():\n    pass\n",
        "tests/acceptance/W1-aa/test_aa.py": "def test_aa():\n    pass\n",
        "tests/acceptance/W1-own/test_own.py": "def test_own():\n    pass\n",
        "tests/acceptance/W1-hh/hh_support.py": "H = 1\n",
        "tests/acceptance/W1-hh/test_hh.py": "def test_hh():\n    pass\n",
        "tests/acceptance/W1-uu/test_uu.py": "import hh_support\n\ndef test_uu():\n    pass\n",
        "tests/acceptance/W1-cc/test_cc.py": "def test_cc():\n    pass\n",
        "tests/acceptance/W1-rr/test_rr.py": "def test_reads():\n    pass\n\ndef test_reads_too():\n    pass\n\n"
                                             "def test_other():\n    pass\n",
        "tests/acceptance/W1-rr/test_rr_more.py": "def test_more():\n    pass\n",
        "tests/acceptance/W1-zz/test_zz.py": "def test_zz():\n    pass\n",
    }
    if test_map is not None:
        files[select.MAP_REL] = yaml.safe_dump(test_map)
    return repo.commit("base", files=files)


def _green(repo: Repo, head: str, *, verdict: str = "green") -> None:
    repo.commit("night", files={f"{select.NIGHTLY_REL}/NR-1.json": json.dumps({"head": head, "verdict": verdict})})


def _targets(plan: dict) -> dict:
    return {entry["target"]: [why["reason"] for why in entry["why"]] for entry in plan["selected"]}


def test_the_pattern_grammar_is_allowed_paths_one():
    assert select.match("docs/plan/a/b.md", "docs/plan/**.md")
    assert not select.match("docs/plan/tools/v.py", "docs/plan/**.md")
    assert select.match("src/a/x.py", "src/a/*.py") and not select.match("src/a/b/x.py", "src/a/*.py")


def test_a_missing_or_invalid_map_is_named_and_never_read_as_a_map(repo, tmp_path):
    assert select.load_map(repo.root) == (None, "TEST_MAP_MISSING")
    for text in ("a: [", "- a list\n", yaml.safe_dump({"version": 1, "shared_core": []}),
                 yaml.safe_dump({"version": 1, "shared_core": "src/**"})):
        (repo.root / select.MAP_REL).parent.mkdir(parents=True, exist_ok=True)
        (repo.root / select.MAP_REL).write_text(text, encoding="utf-8")
        assert select.load_map(repo.root) == (None, "TEST_MAP_UNREADABLE"), text
    (repo.root / select.MAP_REL).write_text(yaml.safe_dump(MAP), encoding="utf-8")
    assert select.load_map(repo.root) == (MAP, None)


def test_the_base_is_the_newest_green_ancestor_and_a_red_night_is_none(repo):
    first = _project(repo)
    assert select.base(repo.root) is None
    _green(repo, first, verdict="red")
    assert select.base(repo.root) is None
    _green(repo, first)
    assert select.base(repo.root) == first
    _green(repo, "0" * 40)
    assert select.base(repo.root) is None


def test_a_one_module_change_selects_its_overlap_the_unit_tests_and_the_declared_sets(repo):
    _green(repo, _project(repo))
    repo.commit("work", files={"src/a/x.py": "x = 2\n"})
    plan = select.plan(repo.root, "W1-own")
    assert plan["scope"] == "scoped" and plan["why_full"] == []
    assert plan["changed"] == [f"{select.NIGHTLY_REL}/NR-1.json", "src/a/x.py"]  # the record since the base too
    assert _targets(plan) == {"tests/acceptance/W1-own/": ["OWN"], "tests/unit": ["UNIT"],
                              "tests/acceptance/W1-aa/": ["OVERLAP"],
                              "tests/acceptance/W1-rr/test_rr.py::test_reads": ["RECORD_READING"]}
    left = {entry["target"] for entry in plan["left_out"]}
    assert left == {"tests/acceptance/W1-hh/", "tests/acceptance/W1-uu/", "tests/acceptance/W1-cc/",
                    "tests/acceptance/W1-zz/", "tests/acceptance/W1-rr/test_rr_more.py"}
    assert "tests/acceptance/W1-rr/test_rr.py::test_other" in plan["deselect"]
    assert "tests/acceptance/W1-rr/test_rr.py::test_reads" not in plan["deselect"]  # its prefix would take it
    assert plan["tmp_path_retention_policy"] == "failed"


def test_a_changed_helper_selects_the_suite_importing_it_and_a_coupling_its_suites(repo):
    _green(repo, _project(repo))
    repo.commit("work", files={"tests/acceptance/W1-hh/hh_support.py": "H = 2\n", "data/t.txt": "u\n"})
    targets = _targets(select.plan(repo.root, "W1-own"))
    assert targets["tests/acceptance/W1-uu/"] == ["HELPER"]
    assert targets["tests/acceptance/W1-hh/"] == ["TEST_CHANGED"]
    assert targets["tests/acceptance/W1-cc/"] == ["COUPLING"]


def test_the_shared_core_an_unplaced_path_and_full_asked_widen_to_the_full_run(repo):
    _green(repo, _project(repo))
    repo.commit("work", files={"src/core/z.py": "z = 2\n", "README": "r\n"})
    plan = select.plan(repo.root, "W1-own", full_asked=True)
    assert plan["scope"] == "full" and plan["left_out"] == [] and plan["ignore"] == ["tests/acceptance/W1-own/"]
    assert [w["reason"] for w in plan["why_full"]] == ["FULL_ASKED", "SHARED_CORE", "UNPLACED"]
    assert plan["why_full"][1]["paths"] == ["src/core/z.py"] and plan["why_full"][2]["paths"] == ["README"]
    assert _targets(plan)["tests"] == ["FULL"]
    assert plan["tmp_path_retention_policy"] == "failed"


def test_a_moved_file_is_in_the_change_at_both_its_paths(repo):
    _green(repo, _project(repo))
    repo.git("config", "diff.renames", "true")  # rename detection asked for by the repository is not followed
    repo.git("mv", "src/core/z.py", "src/a/z.py")
    repo.commit("move")
    plan = select.plan(repo.root, "W1-own")
    assert {"src/core/z.py", "src/a/z.py"} <= set(plan["changed"])
    assert plan["scope"] == "full" and plan["why_full"] == [{"reason": "SHARED_CORE", "paths": ["src/core/z.py"]}]


def test_a_ticket_s_suite_is_the_folder_its_file_declares(repo):
    declared = "---\nid: P-W1-dd\nwbs_id: W1-dd\nacceptance_tests:\n  path: tests/acceptance/W1-zz/\n" \
               "allowed_paths:\n- src/d/**\n---\n"
    _project(repo)
    _green(repo, repo.commit("declared", files={".tickets/P-W1-dd.md": declared, "src/d/w.py": "w = 1\n"}))
    repo.commit("work", files={"src/d/w.py": "w = 2\n"})
    targets = _targets(select.plan(repo.root, "W1-own"))
    assert targets["tests/acceptance/W1-zz/"] == ["OVERLAP"] and "tests/acceptance/W1-dd/" not in targets
    plan = select.plan(repo.root, "W1-dd", ticket="P-W1-dd")
    assert _targets(plan)["tests/acceptance/W1-zz/"] == ["OWN", "OVERLAP"]
    assert not any(e["target"].startswith("tests/acceptance/W1-zz/") for e in plan["left_out"])
    assert plan["ignore"][0] == "tests/acceptance/W1-zz/"


def test_a_path_only_suiteless_tickets_hold_is_unplaced(repo):
    _project(repo)
    _green(repo, repo.commit("suiteless", files={".tickets/P-W1-nn.md": _ticket("W1-nn", "scripts/**"),
                                                 "tests/acceptance/W1-nn/nn_support.py": "N = 1\n"}))
    repo.commit("work", files={"scripts/s.py": "s = 1\n"})
    plan = select.plan(repo.root, "W1-own")
    assert plan["scope"] == "full" and plan["why_full"] == [{"reason": "UNPLACED", "paths": ["scripts/s.py"]}]


def test_every_run_of_a_close_is_given_the_retention_option_with_its_per_test_limit(tmp_path):
    import os
    import sys
    from gov.close.command import _scope_limit

    scope = {"check_result": None, "limit": None, "per_test_timeout": 900, "tmp_path_retention_policy": "failed"}
    env = {**os.environ, "PYTHONPATH": os.pathsep.join(p for p in sys.path if p)}
    limit = _scope_limit(tmp_path, scope, env)
    assert limit[-2:] == ["-o", "tmp_path_retention_policy=failed"] and "--timeout=900" in limit
    assert scope["limit"] == limit  # the run alone of a red and the nightly's runs take the same list


def test_a_record_only_commit_selects_nothing_by_itself(repo):
    _green(repo, _project(repo))
    repo.commit("record", files={"docs/close/x/CL-x.md": "---\nid: x\n---\n"})
    plan = select.plan(repo.root, "W1-own")
    assert plan["scope"] == "scoped" and set(_targets(plan)) == {
        "tests/acceptance/W1-own/", "tests/unit", "tests/acceptance/W1-rr/test_rr.py::test_reads"}


def test_a_serial_case_runs_only_where_the_run_reaches_it():
    ignore, deselect = ["tests/acceptance/W1-zz/"], ["tests/acceptance/W1-rr/test_rr.py::test_other"]
    assert not select.runs("tests/acceptance/W1-zz/test_zz.py::test_zz", ignore, deselect)
    assert not select.runs("tests/acceptance/W1-rr/test_rr.py::test_other", ignore, deselect)
    assert select.runs("tests/acceptance/W1-rr/test_rr.py::test_reads", ignore, deselect)
