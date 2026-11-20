"""S7 (fix, DEC-1223 (6)): `gov update --rollback` restores the previous release in one command (CAP-45.a).

The update undone is S2's: a copy of the adopted project updated A to B, with A pinned before (`gov install A`,
the pinned update) or with no pin before (S2's own update). Each rollback runs in its own copy, from the root: with
A's environment's gov (`<common>/gov/envs/<A>/bin/gov update --rollback`, without PYTHONPATH) where the copy holds
that environment, else with this worktree's gov (`python -m gov.cli.main`).
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import w2_17_support as support


def _succeeded(run, what):
    assert run.returncode == 0, f"{what}: `gov update --rollback --json` did not exit 0\n{run.describe()}"
    return run.result()


def _record_pin(value):
    """``pin_before.record`` as JSON: the record may hold pin.json as an object or as its text."""
    return json.loads(value) if isinstance(value, (str, bytes)) else value


def _same_resolved(first, second):
    return first is not None and Path(first).resolve() == Path(second).resolve()


def _assert_release_a_restored(project, commit_before, what):
    """Every tracked file at HEAD but the rolled-back record is A's (the commit before the update), the record is
    in HEAD, and the status is clean."""
    expected, actual = support.tracked(project, commit_before), support.tracked(project, "HEAD")
    assert support.ROLLED_BACK_REL in actual, f"{what}: HEAD does not hold {support.ROLLED_BACK_REL}"
    actual.pop(support.ROLLED_BACK_REL)
    differing = support.tracked_difference(expected, actual)
    assert not differing, (
        f"{what}: tracked files at HEAD differ from release A's commit {commit_before} (bytes or mode): "
        f"{differing[:20]}")
    assert support.porcelain_paths(project) == [], (
        f"{what}: `git status --porcelain` is not empty after the rollback: {support.porcelain_paths(project)}")


def _assert_refused(project, sandbox, reason, what, *args, binary=None):
    """``gov update --rollback`` refused as UPDATE_REFUSED with ``reason``; HEAD, the tree and the pin unchanged."""
    before, before_pin = support.tree_state(project), support.pin_state(project)
    run = support.rollback(project, sandbox, *args, binary=binary)
    assert run.returncode != 0, f"{what}: the rollback exited 0\n{run.describe()}"
    error = run.error()
    assert error.get("code") == support.UPDATE_REFUSED and (error.get("details") or {}).get("reason") == reason, (
        f"{what}: the rollback is not refused as {support.UPDATE_REFUSED} with reason {reason!r}\n{run.describe()}")
    changed = support.tree_difference(before, support.tree_state(project))
    assert not changed, f"{what}: the refused rollback changed HEAD or files outside .git: {changed[:20]}"
    assert support.pin_state(project) == before_pin, f"{what}: the refused rollback changed <common>/gov/"
    assert not support.revert_in_progress(project), f"{what}: the refused rollback left a revert in progress"
    return run, error


# --- the record the update writes ---------------------------------------------------------------------------

def test_the_update_records_the_pin_it_found_in_pin_before(pinned_updated, updated):
    pinned = support.show_json(pinned_updated.project, "HEAD", support.RECORD_REL) or {}
    found = pinned.get("pin_before")
    assert isinstance(found, dict), f"the update's record {support.RECORD_REL} has no pin_before: {pinned!r}"
    assert found.get("existed") is True and found.get("link") == pinned_updated.link_before \
        and _record_pin(found.get("record")) == pinned_updated.record_before, (
            f"pin_before does not hold the pin of A as it was before the update (existed true, link "
            f"{pinned_updated.link_before}, record {pinned_updated.record_before!r}): {found!r}")
    plain = (support.show_json(updated.project, "HEAD", support.RECORD_REL) or {}).get("pin_before")
    assert isinstance(plain, dict) and (plain.get("existed"), plain.get("link"), plain.get("record")) \
        == (False, None, None) and {"link", "record"} <= set(plain), (
        f"a project with no pin before the update: pin_before is not existed false, link and record null: {plain!r}")


# --- the rollback of the pinned update, by A's gov ------------------------------------------------------------

def test_rollback_restores_every_tracked_file_of_release_a(rolled_back):
    _succeeded(rolled_back.run, "the pinned update")
    _assert_release_a_restored(rolled_back.project, rolled_back.commit_before, "the pinned update")
    release = support.lock_release(rolled_back.project) or {}
    assert release.get("version") == support.A, f"the lock does not name {support.A}: {release!r}"


def test_rollback_is_one_revert_commit_holding_its_record(rolled_back):
    _succeeded(rolled_back.run, "the pinned update")
    project, update_commit = rolled_back.project, rolled_back.update_commit
    new = support.git(project, "rev-list", f"{update_commit}..HEAD").split()
    assert len(new) == 1 and support.git(project, "rev-parse", "HEAD^").strip() == update_commit, (
        f"the rollback is not one new commit on top of the update commit {update_commit}: {new}")
    history = support.git(project, "rev-list", "HEAD").split()
    assert update_commit in history and rolled_back.commit_before in history, (
        "the history no longer holds the update commit and the commit before it")
    record = support.show_json(project, "HEAD", support.ROLLED_BACK_REL)
    assert isinstance(record, dict), f"the rollback commit does not hold {support.ROLLED_BACK_REL}"
    missing = [key for key in ("from", "to", "update_commit", "revert_commit", "pin") if key not in record]
    assert not missing, f"{support.ROLLED_BACK_REL} lacks {missing}: {record!r}"
    named = (record.get("from"), record.get("to"), record.get("update_commit"))
    assert named == (support.B, support.A, update_commit), (
        f"{support.ROLLED_BACK_REL} does not name from {support.B}, to {support.A} and the update commit "
        f"{update_commit}: {record!r}")


def test_rollback_puts_the_pin_back_to_a_and_keeps_b_environment(rolled_back, pinned_updated):
    _succeeded(rolled_back.run, "the pinned update")
    project = rolled_back.project
    # The case runs in a copy of the pinned update, so the link and pin.json recorded before the update name the
    # origin's A environment; the copy's own <common>/gov/envs/<A> is accepted as well.
    environment = support.common_dir(project) / "gov" / "envs" / support.A
    link, record = support.pin_link(project), support.pin_record(project) or {}
    assert link == pinned_updated.link_before or _same_resolved(link, environment / "bin" / "gov"), (
        f"<common>/gov/bin/gov names {link!r}, not A's environment as before the update "
        f"{pinned_updated.link_before!r}")
    assert record == pinned_updated.record_before or (
            record.get("version") == support.A and _same_resolved(record.get("environment"), environment)), (
        f"<common>/gov/pin.json is not A's as before the update ({pinned_updated.record_before!r}): {record!r}")
    assert (support.common_dir(project) / "gov" / "envs" / support.B).is_dir(), (
        f"B's environment <common>/gov/envs/{support.B} was not left for diagnosis")


def test_rollback_rebuilds_the_store_at_the_rollback_commit(rolled_back):
    _succeeded(rolled_back.run, "the pinned update")
    retrieved = support.pinned(rolled_back.project, rolled_back.sandbox, "retrieve", "--json", "audit skill")
    store = retrieved.result().get("store") or {}
    assert store.get("commit") == support.head(rolled_back.project), (
        f"the memory store was not rebuilt at the rollback commit {support.head(rolled_back.project)}: {store!r}")


# --- no pin before the update -----------------------------------------------------------------------------------

def test_a_project_with_no_pin_before_the_update_has_none_after(rolled_back_no_pin):
    what = "S2's update, no pin before it"
    _succeeded(rolled_back_no_pin.run, what)
    project = rolled_back_no_pin.project
    _assert_release_a_restored(project, rolled_back_no_pin.commit_before, what)
    root = support.common_dir(project) / "gov"
    assert not os.path.lexists(root / "bin" / "gov") and not os.path.lexists(root / "pin.json"), (
        f"{what}: the rollback left a pin link or pin.json: {support.pin_state(project)!r}")
    assert (root / "envs" / support.B).is_dir(), f"{what}: B's environment was not left for diagnosis"
    retrieved = support.gov(project, rolled_back_no_pin.sandbox, "retrieve", "--json", "audit skill")
    store = retrieved.result().get("store") or {}
    assert store.get("commit") == support.head(project), (
        f"{what}: the memory store was not rebuilt at the rollback commit {support.head(project)}: {store!r}")


# --- a record written before pin_before existed --------------------------------------------------------------

def test_a_record_without_pin_before_rolls_back_through_the_fallback(pinned_updated, tmp_path, sandbox):
    project = support.copy_project(pinned_updated.project, tmp_path / "product")
    support.amend_record_without_pin_before(project)
    run = support.rollback(project, sandbox, binary=support.env_gov(project, support.A))
    what = "a record without pin_before"
    _succeeded(run, what)
    _assert_release_a_restored(project, pinned_updated.before["head"], what)
    environment = support.common_dir(project) / "gov" / "envs" / support.A
    assert _same_resolved(support.pin_link(project), environment / "bin" / "gov"), (
        f"{what}: <common>/gov/bin/gov names {support.pin_link(project)!r}, not {environment}/bin/gov")
    record = support.pin_record(project) or {}
    assert record.get("version") == support.A and _same_resolved(record.get("environment"), environment), (
        f"{what}: <common>/gov/pin.json does not name {support.A} and {environment}: {record!r}")


def test_the_fallback_without_a_environment_is_refused_no_previous_pin(pinned_updated, tmp_path, sandbox):
    project = support.copy_project(pinned_updated.project, tmp_path / "product")
    support.amend_record_without_pin_before(project)
    shutil.rmtree(support.common_dir(project) / "gov" / "envs" / support.A)
    _assert_refused(project, sandbox, "no_previous_pin",
                    f"a record without pin_before and no <common>/gov/envs/{support.A}")


# --- refusals ---------------------------------------------------------------------------------------------------

def test_a_later_commit_that_conflicts_is_refused_naming_the_path(pinned_updated, tmp_path, sandbox):
    project = support.copy_project(pinned_updated.project, tmp_path / "product")
    path = project / support.UPDATED
    path.write_text(path.read_text(encoding="utf-8") + "W2-17: a later change the revert conflicts with\n",
                    encoding="utf-8")
    support.commit_all(project, "W2-17: a later commit changing a file the update changed")
    run, error = _assert_refused(project, sandbox, "rollback_conflict", f"a later commit changing {support.UPDATED}",
                                 binary=support.env_gov(project, support.A))
    told = str(error.get("message", "")) + " " + json.dumps(error.get("details"))
    assert support.UPDATED in told, (
        f"the refusal does not name the conflicting path {support.UPDATED}\n{run.describe()}")


def test_a_version_given_with_rollback_is_refused_usage(updated, tmp_path, sandbox):
    project = support.copy_project(updated.project, tmp_path / "product")
    _assert_refused(project, sandbox, "usage", f"`gov update {support.B} --rollback`", support.B)


def test_a_project_with_no_update_to_undo_is_refused_no_update(own_project, sandbox):
    _assert_refused(own_project, sandbox, "no_update", "a project adopted at A and never updated")


def test_an_uncommitted_change_is_refused_dirty(updated, tmp_path, sandbox):
    project = support.copy_project(updated.project, tmp_path / "product")
    (project / support.OWN_FILE).write_text("W2-17: an uncommitted change\n", encoding="utf-8")
    assert support.OWN_FILE in support.porcelain_paths(project), "fixture: the change does not show in git status"
    _assert_refused(project, sandbox, "dirty", f"{support.OWN_FILE} is uncommitted")
