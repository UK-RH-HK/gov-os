"""A8 (L2 §3 A8; L2 §2 step 8): after a move, the integration store's refresh and the structural pass, as notices.

Success lines 5 (A8 S1) and 6 (A8 S2), failure line 3 (A8 F1). README, "The planted runs": after_store, after_plain,
after_failing.
"""

from __future__ import annotations

import pytest

import w2_206_support as support
from w2_206_support import A, B, kit


@pytest.fixture(scope="module")
def after_store(landing):
    return landing("after_store")


@pytest.fixture(scope="module")
def after_plain(landing):
    return landing("after_plain")


@pytest.fixture(scope="module")
def after_failing(landing):
    return landing("after_failing")


def _landed(landing):
    result = kit.answer(landing.run, kit.EXIT_LANDED)
    assert result.get("landed") == [A.id], f"the landing landed {result.get('landed')!r}"
    return result


# -- success line 5 (A8 S1) ---------------------------------------------------------------------------------------

def test_after_the_move_queue_json_holds_the_store_s_rebuild_at_the_landed_head(after_store):
    result = _landed(after_store)
    rebuild = support.after_of(after_store, result).get("rebuild")
    assert isinstance(rebuild, dict) and rebuild.get("ok") is True, f"after.rebuild: {rebuild!r}"
    assert rebuild.get("head") == result["head"] == kit.rev(after_store.root, "main"), \
        f"after.rebuild was built at {rebuild.get('head')!r}, the landed head is {result['head']}"


def test_gov_retrieve_s_store_line_names_the_new_head_and_no_stale_store(after_store):
    result = _landed(after_store)
    line = after_store.extra["line_after"]
    assert line and line.startswith(f"store: {result['head'][:12]} "), \
        f"the store line after the landing is {line!r}, the landed head {result['head'][:12]} (before the " \
        f"landing: {after_store.extra['line_before']!r})\n{after_store.extra['asked_after']}"
    assert "stale" not in line and ", head " not in line, f"the store line names a stale store: {line!r}"


def test_a_project_whose_rebuild_yaml_names_no_store_is_not_configured_and_no_rebuild_is_run(after_plain):
    result = _landed(after_plain)
    rebuild = support.after_of(after_plain, result).get("rebuild")
    assert support.not_configured(rebuild), f"after.rebuild is {rebuild!r}, not not_configured"
    assert not (after_plain.root / ".gov-runtime" / "store.db").exists(), "a store was built at the root"


# -- success line 6 (A8 S2) ---------------------------------------------------------------------------------------

def test_queue_json_holds_the_structural_pass_s_exit_code_and_its_lines(after_plain):
    result = _landed(after_plain)
    structural = support.after_of(after_plain, result).get("structural")
    assert isinstance(structural, dict), f"after.structural: {structural!r}"
    assert structural.get("exit") == 0 == after_plain.extra["own_code"], f"after.structural: {structural}"
    assert isinstance(structural.get("ok"), bool), f"after.structural names no ok: {structural}"
    lines = support.unstamped(support.lines_of(structural.get("lines")))
    assert f"schema: NOTICE {support.NOTICED}" in lines, f"the pass's notice is not in its lines: {lines}"
    own = support.unstamped(after_plain.extra["own_lines"])
    assert lines == own, f"after.structural's lines are not the pass's own on the landed head:\n{lines}\n{own}"


def test_the_structural_pass_ran_once_after_the_move_with_the_landing_s_base(after_plain):
    result = _landed(after_plain)
    told = support.rows(after_plain.told, support.STRUCTURAL_TOLD)
    assert len(told) == 1, f"the planted check ran {len(told)} time(s) in the landing, not once: {told}"
    ran = told[0]
    assert ran["main_at_root"] == result["head"], \
        f"the pass ran while main stood at {ran['main_at_root']}, not at the landed head (before the move)"
    assert ran["head"] == result["head"] and ran["changed"] is True, f"the pass ran on another tree: {ran}"
    lines = support.lines_of(support.after_of(after_plain, result)["structural"].get("lines"))
    assert "portability: skipped (no such change)" in [str(line).rstrip() for line in lines], \
        f"the pass was given no base it can read the change from: {lines}"


# -- failure line 3 (A8 F1) ---------------------------------------------------------------------------------------

def _notice(after, name):
    notice = after.get(name)
    assert isinstance(notice, dict) and notice.get("ok") is False, f"after.{name} is no notice: {notice!r}"
    assert isinstance(notice.get("reason"), str) and notice["reason"].strip(), f"after.{name} gives no reason"
    return notice


def test_a_store_that_cannot_be_built_is_a_notice_and_the_landing_stands(after_failing):
    result = _landed(after_failing)
    closes = kit.assert_landed_through_close_commits(after_failing, result, "main", after_failing.old_head)
    assert list(closes) == [A.id] and kit.status_at(after_failing.root, "main", A.id) == "closed"
    assert kit.rev(after_failing.root, "main") == closes[A.id], "main is not at the last close commit"
    _notice(support.after_of(after_failing, result), "rebuild")


def test_a_structural_pass_that_exits_2_is_a_notice_and_the_landing_stands(after_failing):
    result = _landed(after_failing)
    notice = _notice(support.after_of(after_failing, result), "structural")
    assert notice.get("exit") == 2, f"after.structural's exit is {notice.get('exit')!r}, not 2"
    assert kit.rev(after_failing.root, "main") == result["head"] and after_failing.run["code"] == 0


def test_a_landing_that_landed_nothing_runs_neither_after_step(after_failing):
    support.after_of(after_failing, _landed(after_failing))
    culprit = after_failing.extra["culprit"]
    result = kit.answer(culprit["run"], kit.EXIT_NOT_ALL_LANDED)
    assert result.get("landed") == [] and result.get("culprits") == [B.id], f"fixture: the culprit's run: {result}"
    held = support.queue_record(after_failing, result)
    assert not held.get("after"), f"a landing that landed nothing holds an after-step: {held.get('after')!r}"
    assert kit.heads(culprit["after"]) == kit.heads(culprit["before"])
