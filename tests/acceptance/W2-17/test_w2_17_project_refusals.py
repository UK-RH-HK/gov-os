"""F2: an update refuses a tree it cannot roll back to, or a project it cannot read."""

from __future__ import annotations

import pytest
import yaml

import w2_17_support as support

CHANGED_TRACKED, NEW_UNTRACKED = "changed-tracked", "new-untracked"
UNTRACKED = "openspec/specs/w2-17-untracked.md"


def _refused(project, sandbox, reason, what):
    """``gov update B --json`` refused as UPDATE_REFUSED with ``reason``; nothing changed. The error."""
    before, before_pin = support.tree_state(project), support.pin_state(project)
    run = support.update(project, sandbox)
    assert run.returncode != 0, f"`gov update {support.B}` exited 0 although {what}\n{run.describe()}"
    error = run.error()
    details = error.get("details") or {}
    assert error.get("code") == support.UPDATE_REFUSED and details.get("reason") == reason, (
        f"`gov update {support.B}` is not refused as {support.UPDATE_REFUSED} with reason {reason!r} although "
        f"{what}\n{run.describe()}")
    changed = support.tree_difference(before, support.tree_state(project))
    assert not changed, f"the refused update ({what}) changed HEAD or files outside .git: {changed[:20]}"
    assert support.pin_state(project) == before_pin, f"the refused update ({what}) changed <common>/gov/"
    support.assert_never_applied(run, what)
    return run, str(error.get("message", ""))


@pytest.mark.parametrize("change", [CHANGED_TRACKED, NEW_UNTRACKED])
def test_an_uncommitted_change_is_refused_naming_its_path(change, own_project, sandbox):
    if change == CHANGED_TRACKED:
        rel = support.OWN_FILE
        (own_project / rel).write_text("W2-17: an uncommitted change\n", encoding="utf-8")
    else:
        rel = UNTRACKED
        (own_project / rel).write_text("W2-17: an untracked file\n", encoding="utf-8")
    assert rel in support.porcelain_paths(own_project), "fixture: the change does not show in git status"
    run, message = _refused(own_project, sandbox, "dirty", f"{rel} is uncommitted")
    assert rel in message, f"the refusal does not name the uncommitted path {rel}\n{run.describe()}"


def test_a_project_without_a_lock_is_refused_naming_the_lock(own_project, sandbox):
    support.git(own_project, "rm", "-q", support.LOCK_REL)
    support.commit_all(own_project, "W2-17: the lock removed")
    run, message = _refused(own_project, sandbox, "not_adopted", f"the project has no {support.LOCK_REL}")
    assert "framework.lock" in message, f"the refusal does not name the lock\n{run.describe()}"


def test_a_lock_stating_release_null_is_refused_naming_the_lock(own_project, sandbox):
    path = own_project / support.LOCK_REL
    text = path.read_text(encoding="utf-8")
    header = "".join(line for line in text.splitlines(keepends=True) if line.startswith("#"))
    data = yaml.safe_load(text)
    data["release"] = None
    path.write_text(header + yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    support.commit_all(own_project, "W2-17: the lock states release: null")
    assert support.lock_release(own_project) is None, "fixture: the lock does not state release: null"
    run, message = _refused(own_project, sandbox, "not_adopted", f"{support.LOCK_REL} states release: null")
    assert "framework.lock" in message, f"the refusal does not name the lock\n{run.describe()}"


def test_a_project_already_at_b_is_refused_saying_so(project_at_b, tmp_path, sandbox):
    project = support.copy_project(project_at_b, tmp_path / "product")
    assert (support.lock_release(project) or {}).get("version") == support.B, "fixture: the project is not at B"
    run, message = _refused(project, sandbox, "same", f"the project is already at {support.B}")
    assert support.B in message, f"the refusal does not say the project is at {support.B}\n{run.describe()}"
