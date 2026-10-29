"""Builder tests for the batch's reuse, its refusals and attribution, and the close's record lines (W2-68).

Regression evidence only (DEC-136): the last fully passing run is reused on the same code and never where it
failed, was cut short, hides a skip or ran on other code (section 4, conditions 1 to 7); its check result stands
for the close's own only where it ran at its head and does not block; the reused regression is the record-reading
set alone; the batch refuses before anything runs; a red that fails alone is attributed, a flaky one is not; a close
on the code of a red batch waits for a green run (point F).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from gov.cli.errors import GovError
from gov.close import batch, command
from gov.close.fingerprint import of_commit

REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_REL = "template/governance/kernel/schemas/test-map.schema.json"
MAP_REL = "governance/project/test-map.yaml"
MAP = ('version: 1\nshared_core: ["src/core/**"]\nrecord_reading: ["tests/acceptance/R/"]\n'
       'record_only:\n  - "docs/close/**"\n')
JUNIT_REL = ".gov-runtime/nightly/run/01-parallel.xml"
JUNIT = ('<?xml version="1.0" encoding="utf-8"?>\n<testsuites><testsuite>'
         '<testcase classname="tests.unit.test_a" name="test_one" file="tests/unit/test_a.py"/>'
         '<testcase classname="tests.unit.test_a" name="test_two" file="tests/unit/test_a.py">'
         '<skipped message="no network"/></testcase></testsuite></testsuites>\n')


def _green(repo, junit: str = JUNIT, **record) -> tuple[str, str]:
    """A project at H with a committed green batch record of H and its JUnit XML: ``(H, the record's path)``."""
    head = repo.commit("the code", files={SCHEMA_REL: (REPO_ROOT / SCHEMA_REL).read_text(encoding="utf-8"),
                                          MAP_REL: MAP, ".gitignore": ".gov-runtime/\n", "src/a.py": "A = 1\n"})
    (repo.root / JUNIT_REL).parent.mkdir(parents=True)
    (repo.root / JUNIT_REL).write_text(junit, encoding="utf-8")
    rel = "docs/close/nightly/NR-20261029T000000Z-run.json"
    data = {"head": head, "verdict": "green", "scope": "full", "kind": "batch", "junit_xml": [JUNIT_REL],
            "failures": [], "findings": [], "tests_run": {"passed": 1, "skipped": 1}, "skip_count": 1,
            "code_fingerprint": of_commit(repo.root)["code"], **record}
    repo.commit("the run record", files={rel: json.dumps(data)})
    return head, rel


def test_the_last_passing_run_on_the_same_code_is_reused_with_its_skips(repo):
    head, rel = _green(repo)
    repo.commit("a close record", files={"docs/close/T/CL-T.md": "closed\n"})
    reused = batch.reuse(repo.root, {"why_full": []})
    assert reused["record"] == rel and reused["head"] == head and reused["skip_count"] == 1
    assert [s["reason"] for s in reused["skips"]] == ["no network"]
    assert reused["code_fingerprint"] == of_commit(repo.root)["code"]


@pytest.mark.parametrize("record, junit", [
    ({"failures": [{"test": "t"}]}, JUNIT),
    ({"verdict": "red"}, JUNIT),
    ({"scope": "scoped"}, JUNIT),
    ({}, JUNIT.replace('<skipped message="no network"/>', '<failure message="red"/>')),
    ({}, '<?xml version="1.0" encoding="utf-8"?>\n<testsuites/>\n'),
    ({"junit_xml": []}, JUNIT),
    ({"skip_count": 0}, JUNIT),
    ({"code_fingerprint": "sha256:other"}, JUNIT),
], ids=["failed", "red", "scoped", "junit-failure", "cut-short", "no-junit", "hidden-skip", "other-fingerprint"])
def test_a_run_that_failed_was_cut_short_hides_a_skip_or_states_other_code_is_never_reused(repo, record, junit):
    _green(repo, junit, **record)
    assert batch.reuse(repo.root, {"why_full": []}) is None


def test_a_code_commit_a_full_close_or_an_unread_map_runs_fresh(repo):
    _green(repo)
    assert batch.reuse(repo.root, {"why_full": []}, full_asked=True) is None
    assert batch.reuse(repo.root, {"why_full": [{"reason": "TEST_MAP_UNREADABLE"}]}) is None
    assert batch.reuse(repo.root, {"why_full": [{"reason": "UNRESOLVED_TARGET"}]}) is None
    repo.commit("code", files={"src/a.py": "A = 2\n"})
    assert batch.reuse(repo.root, {"why_full": []}) is None


def test_a_missing_junit_xml_file_is_never_reused(repo):
    _green(repo)
    (repo.root / JUNIT_REL).unlink()
    assert batch.reuse(repo.root, {"why_full": []}) is None


def _check(repo, at: str, ok: bool = True) -> str:
    rel = ".gov-runtime/close/batch/x/check.json"
    result = {"families": {}, "checks": [{"id": "C-1", "provenance": {"commit": at}}]}
    envelope = {"ok": True, "result": result} if ok else {"ok": False, "error": {"details": result}}
    (repo.root / rel).parent.mkdir(parents=True, exist_ok=True)
    (repo.root / rel).write_text(json.dumps(envelope), encoding="utf-8")
    return rel


def test_the_reused_record_s_check_stands_only_where_it_ran_at_its_head_and_does_not_block(repo):
    head, rel = _green(repo)
    reused = {"record": rel, "head": head, "code_fingerprint": "sha256:x",
              "check_result": {"path": _check(repo, head), "commit": head, "blocks": False}}
    assert batch.reused_check(repo.root, reused) == {"record": rel, "commit": head, "code_fingerprint": "sha256:x",
                                                     "check_result": reused["check_result"]["path"]}
    assert batch.reused_check(repo.root, {**reused, "check_result": None}) is None
    assert batch.reused_check(repo.root, {**reused, "check_result": {
        "path": _check(repo, "0" * 40), "commit": head, "blocks": False}}) is None
    assert batch.reused_check(repo.root, {**reused, "check_result": {
        "path": _check(repo, head, ok=False), "commit": head, "blocks": True}}) is None
    (repo.root / reused["check_result"]["path"]).unlink()
    assert batch.reused_check(repo.root, {**reused, "check_result": {
        "path": reused["check_result"]["path"], "commit": head, "blocks": False}}) is None


def test_the_reused_regression_is_the_record_reading_set_alone(repo):
    files = {f"tests/{rel}/test_x.py": "def test_x():\n    pass\n"
             for rel in ("unit", "other", "acceptance/X", "acceptance/R", "acceptance/OWN")}
    repo.commit("tests", files={SCHEMA_REL: (REPO_ROOT / SCHEMA_REL).read_text(encoding="utf-8"),
                                MAP_REL: MAP, **files})
    form = batch.reused_form(repo.root, "tests/acceptance/OWN/", {"scope": "scoped", "why_full": [], "head": "h"})
    assert form["scope"] == "reused" and form["deselect"] == []
    assert sorted(form["ignore"]) == ["tests/acceptance/OWN/", "tests/acceptance/X/", "tests/other/", "tests/unit/"]
    assert [s["target"] for s in form["selected"]] == ["tests/acceptance/R/"]


def test_the_batch_refuses_before_anything_runs(root, project):
    with pytest.raises(GovError) as unknown:
        batch.run(root, ["T-9999"])
    assert unknown.value.code == "TICKET_UNKNOWN" and unknown.value.exit_code == 1
    ticket = root / ".tickets" / "T-0001.md"
    project.commit("closed", files={ticket.relative_to(root).as_posix():
                                    ticket.read_text(encoding="utf-8").replace("in_progress", "closed")})
    with pytest.raises(GovError) as closed:
        batch.run(root, ["T-0001"])
    assert closed.value.code == "TICKET_CLOSED"
    (root / "loose.txt").write_text("x\n", encoding="utf-8")
    with pytest.raises(GovError) as dirty:
        batch.run(root, ["T-0001"])
    assert dirty.value.code == "TREE_NOT_COMMITTED"
    assert not (root / ".gov-runtime").exists()


def test_a_red_that_fails_alone_is_attributed_and_a_flaky_one_is_not(root, project):
    first_bad = project.commit("the cause", "Task: T-0001", "Role: engineer",
                               files={"tests/acceptance/T-0002/test_x.py": "def test_x():\n    pass\n"})
    project.commit("another ticket", files={".tickets/T-0002.md": "---\nid: T-0002\nstatus: open\n---\n# T\n"})
    test = "tests/acceptance/T-0002/test_x.py::test_x"
    night = {"failures": [{"test": test, "text": "boom", "alone": "failed", "class": "red"},
                          {"test": "tests/unit/test_y.py::test_y", "alone": "failed", "class": "red"},
                          {"test": "tests/unit/test_z.py::test_z", "alone": "passed", "class": "flaky_candidate"}],
             "packages": [{"kind": "bisect", "test": test, "range": "a..b", "first_bad": first_bad}]}
    found = batch._attribute(root, night)
    assert [(f["test"], f["ticket"], f["by"]) for f in found] == [
        (test, "T-0001", "bisect"), ("tests/unit/test_y.py::test_y", "outside", "outside")]
    assert found[0]["first_bad"] == first_bad and found[0]["text"] == "boom"
    night["packages"] = []
    assert batch._attribute(root, night)[0] == {
        "test": test, "text": "boom", "alone": "failed", "range": None, "first_bad": None, "ticket": "T-0002",
        "by": "folder", "folder": "tests/acceptance/T-0002/"}


def test_the_close_s_evidence_states_both_fingerprints_and_the_reused_run():
    scope = {key: None for key in ("scope", "why_full", "base", "head", "tree", "changed", "selected", "left_out",
                                   "per_test_timeout", "distribution", "tmp_path_retention_policy")}
    scope.update({"runs": [], "junit_xml": [], "fingerprints": None, "reused": None})
    evidence = command._scope_evidence(Path("."), scope)
    assert evidence["code_fingerprint"] is None and evidence["records_fingerprint"] is None
    assert "reused" not in evidence
    reused = {"record": "r", "head": "h", "code_fingerprint": "c", "junit_xml": ["j"], "skip_count": 1,
              "skips": [{"test": "t", "reason": "x"}], "tests_run": {}, "check_result": None}
    scope.update({"scope": "reused", "fingerprints": {"code": "c", "records": "r"}, "reused": reused})
    evidence = command._scope_evidence(Path("."), scope)
    assert (evidence["scope"], evidence["code_fingerprint"], evidence["records_fingerprint"]) == ("reused", "c", "r")
    assert evidence["reused"] == {key: reused[key] for key in command.REUSED_KEYS}


def _run(repo, name: str, head: str, verdict: str, **record) -> None:
    data = {"head": head, "verdict": verdict, "scope": "full", "kind": "batch",
            "code_fingerprint": of_commit(repo.root)["code"], **record}
    repo.commit(f"the run {name}", files={f"docs/close/nightly/NR-{name}.json": json.dumps(
        {key: value for key, value in data.items() if value is not None})})


def test_a_close_on_the_code_of_a_red_batch_waits_for_a_green_run(repo):
    head, _ = _green(repo)
    _run(repo, "20261029T010000Z-red", head, "red")
    with pytest.raises(GovError) as waits:
        batch.check_red_run(repo.root)
    assert waits.value.code == "RED_RUN_ON_CODE" and waits.value.exit_code == 1
    assert waits.value.details["record"] == "docs/close/nightly/NR-20261029T010000Z-red.json"
    assert waits.value.details["head"] == head


def test_a_newer_green_run_on_the_same_code_lets_the_close_go_on(repo):
    head, _ = _green(repo)
    _run(repo, "20261029T010000Z-red", head, "red")
    later = repo.commit("a record", files={"docs/close/T/CL-T.md": "closed\n"})
    _run(repo, "20261029T020000Z-night", later, "green", kind="night", code_fingerprint=None)  # a night states none
    assert batch.check_red_run(repo.root) is None


def test_a_red_batch_on_other_code_asks_nothing(repo):
    head, _ = _green(repo)
    _run(repo, "20261029T010000Z-red", head, "red")
    repo.commit("code", files={"src/a.py": "A = 2\n"})
    assert batch.check_red_run(repo.root) is None
    repo.commit("a map that does not parse", files={MAP_REL: "version: [1\n"})
    assert batch.check_red_run(repo.root) is None
