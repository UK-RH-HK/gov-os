"""W2-115b IT-3: the evidence block of a landed ticket's close record."""
from __future__ import annotations

from gov.queue import evidence
from queue_support import PASS, Repo

JUNIT = ('<?xml version="1.0"?><testsuites><testsuite><testcase file="tests/t.py" classname="tests.t" name="a">'
         '<skipped message="not here"/></testcase><testcase file="tests/t.py" classname="tests.t" name="b">'
         '<failure message="assert 0">boom</failure></testcase></testsuite></testsuites>')


def _project(tmp_path) -> Repo:
    repo = Repo(tmp_path / "project")
    repo.commit("base", files={"tests/unit/test_a.py": PASS, "tests/acceptance/W-1/test_w.py": PASS})
    return repo


def test_selected_says_why_each_target_held_by_the_tested_commit_ran_and_adds_the_acceptance_folder(tmp_path):
    repo = _project(tmp_path)
    why = {"tests/unit/": ["TEST_FOLDER tests/unit/x.py", "OVERLAP T-b src/a.py", "RECORD_READING"],
           "tests/unit/test_gone.py": ["OWN"]}
    assert evidence.selected(repo.root, repo.sha(), why, "tests/acceptance/W-1/") == [
        {"target": "tests/unit/", "why": [{"reason": "TEST_FOLDER", "paths": ["tests/unit/x.py"]},
                                          {"reason": "OVERLAP", "ticket": "T-b", "paths": ["src/a.py"]},
                                          {"reason": "RECORD_READING"}]},
        {"target": "tests/acceptance/W-1/", "why": [{"reason": "ACCEPTANCE"}]}]


def test_an_own_suite_that_is_the_acceptance_folder_is_named_once(tmp_path):
    repo = _project(tmp_path)
    assert evidence.selected(repo.root, repo.sha(), {"tests/acceptance/W-1/": ["OWN"]}, "tests/acceptance/W-1") == [
        {"target": "tests/acceptance/W-1/", "why": [{"reason": "OWN"}]}]


def test_the_block_holds_what_the_kept_junit_files_state(tmp_path):
    repo = _project(tmp_path)
    kept = repo.root / ".gov-runtime" / "queue" / "run.xml"
    kept.parent.mkdir(parents=True)
    kept.write_text(JUNIT, encoding="utf-8")
    block = evidence.block(repo.root, repo.root, base=repo.sha(), head=repo.sha(), changed=["src/a.py"],
                           selected=[], full=True, junit=[kept, kept.with_name("missing.xml")])
    assert block["scope"] == "full" and block["why_full"] == [{"reason": "FULL_ASKED"}]
    assert block["tree"] == repo.sha("HEAD^{tree}") and block["changed"] == ["src/a.py"]
    assert block["skips"] == [{"test": "tests/t.py::a", "reason": "not here"}] and block["skip_count"] == 1
    assert block["failures"] == [{"test": "tests/t.py::b", "text": "boom"}]
    assert block["junit_xml"] == [".gov-runtime/queue/run.xml"] and block["left_out"] == []
