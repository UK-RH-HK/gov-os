"""The ratchet of DEC-757 (``gov.close.ratchet``) and git's own merge of a merge's parents (W2-53, DEC-754).
Builder tests: regression evidence only (MR-3)."""
from __future__ import annotations

import yaml

from gov.close import history, ratchet

REGISTER = "docs/DECISION_REGISTER.md"
FILE = "tests/acceptance/W1-42/test_exit.py"
RED = f"{FILE}::test_query[RETR-X-02]"


def _listed(repo, key, entries, role="owner", text=f"`test_query[RETR-X-02]` in `{FILE}`"):
    files = {REGISTER: f"### DEC-901 — A decision\n- **Status:** ACCEPTED (owner, 2026-10-17)\n- **Decision:** {text}\n",
             history.PATH_MAP_REL: yaml.safe_dump({history.REGISTER_KEY: REGISTER, key: entries})}
    return repo.commit("the list", "Task: setup", f"Role: {role}", files=files)


def _red(test=RED, **more):
    return {"test": test, "decision": "DEC-901", "reason": "known", "fixed_by": "W2-13", **more}


def test_a_listed_red_is_covered_and_any_other_red_refuses(repo):
    _listed(repo, ratchet.ACCEPTED_REDS, [_red()])
    verdict = ratchet.apply_accepted_reds(repo.root, {RED: "error", f"{FILE}::test_other": "failed"})
    assert verdict["accepted_reds"] == [{**_red(), "result": "failed"}]
    assert [(f["code"], f["test"]) for f in verdict["findings"]] == [(ratchet.RED_NOT_ACCEPTED, f"{FILE}::test_other")]


def test_a_listed_red_that_passes_refuses_and_one_not_run_does_not(repo):
    _listed(repo, ratchet.ACCEPTED_REDS, [_red()])
    assert [f["code"] for f in ratchet.apply_accepted_reds(repo.root, {RED: "passed"})["findings"]] == \
        [ratchet.ACCEPTED_RED_PASSES]
    verdict = ratchet.apply_accepted_reds(repo.root, {RED: "skipped"})
    assert verdict["ok"] and verdict["accepted_reds"][0]["result"] == "not run"


def test_an_entry_another_role_added_does_not_count_and_names_its_commit(repo):
    added = _listed(repo, ratchet.ACCEPTED_REDS, [_red()], role="orchestrator")
    counted, findings = ratchet.counted_entries(repo.root, ratchet.ACCEPTED_REDS)
    assert counted == [] and findings[0]["code"] == ratchet.REFUSED[ratchet.ACCEPTED_REDS]
    assert added[:12] in findings[0]["message"]


def test_a_decision_naming_the_function_alone_does_not_name_a_parameter_set(repo):
    _listed(repo, ratchet.ACCEPTED_REDS, [_red()], text=f"`test_query` in `{FILE}`")
    counted, findings = ratchet.counted_entries(repo.root, ratchet.ACCEPTED_REDS)
    assert counted == [] and "does not name" in findings[0]["message"]


def test_a_function_entry_of_load_sensitive_covers_its_parameter_sets_only():
    assert ratchet.covers(f"{FILE}::test_query", RED) and ratchet.covers(RED, RED)
    assert not ratchet.covers(f"{FILE}::test_q", RED) and not ratchet.covers(f"{FILE}::test_query", f"{FILE}::test_query_too")


def test_gits_own_merge_of_an_octopus_and_none_for_a_conflict(repo):
    base = repo.commit("base", files={"a": "1\n2\n3\n4\n5\n"})
    tips = []
    for branch, text in (("x", "X\n2\n3\n4\n5\n"), ("y", "1\n2\nY\n4\n5\n"), ("z", "1\n2\n3\n4\nZ\n")):
        repo.git("checkout", "-q", "-b", branch, base)
        tips.append(repo.commit(branch, files={"a": text}))
    merged = history.own_merge(repo.root, tips)
    assert repo.git("show", f"{merged}:a") == "X\n2\nY\n4\nZ\n"
    repo.git("checkout", "-q", "-b", "w", base)
    assert history.own_merge(repo.root, [tips[0], repo.commit("w", files={"a": "W\n2\n3\n4\n5\n"})]) is None
