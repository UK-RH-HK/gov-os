"""A6 S1 and F1 (L2 §3 A6): ``gov queue <T>... --dry-run`` runs the landing's steps 0 to 5 and moves nothing.

Success line 1 (A6 S1) and the dry runs of failure line 1 (A6 F1). README, "The planted runs": dry.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import w2_206_support as support
from w2_206_support import A, B, kit

SAME_AS_THE_LANDING = ("candidates", "culprits", "refused", "reds", "base_reds", "flaky", "selection")


@pytest.fixture(scope="module")
def dry(landing):
    return landing("dry")


def _answer(dry, name, code):
    """The answer of a dry-run step (on the base the flag is unknown: exit 2 and no envelope)."""
    return kit.answer(dry.extra["steps"][name]["run"], code)


def _files(dry, name):
    taken = dry.extra["steps"][name]
    return taken, {f["rel"]: f for f in taken["files"]}


# -- success line 1 (A6 S1) ---------------------------------------------------------------------------------------

def test_a_dry_run_of_a_green_ticket_answers_and_exits_as_its_landing_does(dry):
    result = _answer(dry, "dry", kit.EXIT_LANDED)
    assert result.get("candidates") == [A.id] and result.get("culprits") == [], f"the dry run's answer: {result}"
    assert result.get("head") is None and not result.get("closes"), \
        f"the dry run names a landed head or a close: {result.get('head')!r}, {result.get('closes')!r}"
    landed = kit.answer(dry.run, kit.EXIT_LANDED)
    assert landed.get("landed") == [A.id], f"fixture: the landing after the dry runs landed {landed.get('landed')}"
    for key in SAME_AS_THE_LANDING:
        assert result.get(key) == landed.get(key), f"{key}: the dry run says {result.get(key)!r}, the landing " \
                                                   f"{landed.get(key)!r}"


def test_a_dry_run_runs_the_acceptance_folder_and_the_selection_on_the_merged_result(dry):
    _answer(dry, "dry", kit.EXIT_LANDED)
    taken = dry.extra["steps"]["dry"]
    for told in ("test_aa.jsonl", "test_uses_widget.jsonl"):
        ran = taken["after"]["told"].get(told, 0) - taken["before"]["told"].get(told, 0)
        assert ran >= 1, f"{told[:-6]} did not run in the dry run"
    seen = [r["seen"] for r in dry.told_runs("test_uses_widget")]
    assert seen and all("CHANGED" in (s.get(support.module_rel("widget")) or "") for s in seen), \
        "the selection's test ran on a tree without the candidate's change"


def test_a_dry_run_moves_no_branch_and_writes_no_close_commit_and_no_close_record(dry):
    _answer(dry, "dry", kit.EXIT_LANDED)
    taken = dry.extra["steps"]["dry"]
    before, after = taken["before"], taken["after"]
    assert kit.heads(after) == kit.heads(before), f"a branch moved: {kit.heads(before)} -> {kit.heads(after)}"
    assert after["log"] == before["log"], "the dry run made a commit a ref of the root names"
    assert not [p for p in after["places"] if p.startswith(f"docs/close/{A.id}")], \
        f"docs/close/{A.id}/ exists at the root: {after['places']}"
    assert after["clone_closes"] == [], f"a commit of the warm clone holds a close record: {after['clone_closes']}"
    assert taken["at_tested"]["records"] == [], f"the tested commit holds a close record: {taken['at_tested']}"
    assert kit.status_at(dry.root, dry.old_head, A.id) == "open" and after["files"] == before["files"]


def test_the_dry_run_writes_its_five_files_under_out_with_verify_exit_last(dry):
    _answer(dry, "dry", kit.EXIT_LANDED)
    taken, files = _files(dry, "dry")
    for name in support.OUT_NAMES:
        assert name in files, f"{name} is not under --out ({taken['out']}): {sorted(files)}"
    runs = [rel for rel in files if rel.endswith(".xml")]
    assert len(runs) >= 2, f"the run files (JUnit) under --out: {runs}; all files: {sorted(files)}"
    cases = {}
    for rel in runs:
        cases.update(kit.junit_outcomes(files[rel]["path"]))
    assert cases.get(kit.USES_WIDGET_NODE) == "passed", f"the run files do not hold the selection's run: {cases}"
    assert files["verify.exit"]["text"] == "0\n", f"verify.exit holds {files['verify.exit']['text']!r}"
    assert not [rel for rel in files if rel.endswith(".tmp")], f"a part-written file is left: {sorted(files)}"
    last = max(f["mtime_ns"] for f in files.values())
    assert files["verify.exit"]["mtime_ns"] == last, "verify.exit is not the last file written under --out"
    chosen = support.one_object(files["select.json"]["text"])
    assert chosen and kit.USES_WIDGET[0] in (chosen.get("suites") or []), f"select.json: {files['select.json']}"
    assert files["summary.txt"]["text"].strip(), "summary.txt is empty"
    assert Path(taken["out"]).is_absolute() and not Path(taken["out"]).is_relative_to(dry.root)


def test_gov_wait_on_verify_exit_returns_the_dry_run_s_exit_code(dry):
    for name, code in (("dry", kit.EXIT_LANDED), ("dry_culprit", kit.EXIT_NOT_ALL_LANDED)):
        _answer(dry, name, code)
        waited = dry.extra["steps"][name]["wait"]
        assert waited["code"] == code and f"DONE exit {code}" in waited["stdout"], \
            f"{name}: gov wait did not return {code}\n{support.said(waited)}"


def test_a_planted_culprit_gives_exit_3_in_the_answer_and_in_verify_exit(dry):
    result = _answer(dry, "dry_culprit", kit.EXIT_NOT_ALL_LANDED)
    assert result.get("culprits") == [B.id], f"culprits: {result.get('culprits')!r}"
    assert result.get("head") is None and not result.get("closes")
    taken, files = _files(dry, "dry_culprit")
    assert Path(taken["out"]) == dry.root / support.DRY_REL / f"{A.id}+{B.id}"
    for name in support.OUT_NAMES:
        assert name in files, f"{name} is not under the default folder {taken['out']}: {sorted(files)}"
    assert files["verify.exit"]["text"] == "3\n", f"verify.exit holds {files['verify.exit']['text']!r}"
    assert files["verify.exit"]["mtime_ns"] == max(f["mtime_ns"] for f in files.values())


def test_a_dry_run_refused_as_a_whole_exits_1_as_the_landing_would(dry):
    taken = dry.extra["steps"]["dry_unknown"]
    kit.refusal(taken["run"], "TICKET_UNKNOWN", kit.EXIT_REFUSED_TO_RUN)
    support.moved_nothing(taken)


# -- failure line 1 (A6 F1), the dry runs -------------------------------------------------------------------------

@pytest.mark.parametrize("name, code", [("dry", kit.EXIT_LANDED), ("dry_culprit", kit.EXIT_NOT_ALL_LANDED)],
                         ids=["green", "culprit"])
def test_a_dry_run_leaves_the_root_clean_and_creates_no_branch_no_ref_and_no_commit(dry, name, code):
    _answer(dry, name, code)
    taken = dry.extra["steps"][name]
    support.moved_nothing(taken)
    for ref in ("refs/gov-queue/land", "refs/gov-close/land"):
        assert ref not in taken["after"]["refs"], f"{ref} is left at the root"


@pytest.mark.parametrize("name, code", [("dry", kit.EXIT_LANDED), ("dry_culprit", kit.EXIT_NOT_ALL_LANDED)],
                         ids=["green", "culprit"])
def test_a_dry_run_leaves_the_warm_clone_at_the_base(dry, name, code):
    _answer(dry, name, code)
    after = dry.extra["steps"][name]["after"]
    assert after["clone_head"] == dry.old_head, f"the warm clone is at {after['clone_head']}, not the base"
    assert after["clone_status"] == "", f"the warm clone's status: {after['clone_status']!r}"
