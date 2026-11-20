"""W2-17 fix S7 (DEC-1223 (6)): ``gov update --rollback`` (``core.rollback``) and the record's ``pin_before``.
Builder evidence on a tmp repository standing for an updated project (no copier, no wheel); the store rebuild is
replaced by a recorder.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from gov.update import command as update_command
from gov.update import core


def git(repo: Path, *args: str, check: bool = True) -> str:
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=env)
    assert done.returncode == 0 or not check, done.stderr
    return done.stdout.strip()


def make_env(common: Path, version: str) -> Path:
    env = common / "gov" / "envs" / version
    (env / "bin").mkdir(parents=True)
    (env / "bin" / "gov").write_text("#!/bin/sh\n")
    return env


def point(common: Path, version: str) -> None:
    env = common / "gov" / "envs" / version
    (common / "gov" / "bin").mkdir(exist_ok=True)
    link = common / "gov" / "bin" / "gov"
    if os.path.lexists(link):
        os.unlink(link)
    os.symlink(env / "bin" / "gov", link)
    (common / "gov" / "pin.json").write_text(json.dumps({"version": version, "environment": str(env)}))


def tree(repo: Path) -> dict:
    out = {}
    for line in git(repo, "ls-tree", "-r", "HEAD").splitlines():
        meta, path = line.split("\t")
        out[path] = meta
    return out


@pytest.fixture
def updated(tmp_path):
    """A project adopted at 1.0.0 pinned at 1.0.0, then updated to 1.0.1 (pin and record as ``gov update`` leaves)."""
    project = tmp_path / "p"
    project.mkdir()
    git(project, "init", "-q", "-b", "main")
    common = project / ".git"
    (project / "governance").mkdir()
    (project / "governance/framework.lock").write_text("release:\n  version: 1.0.0\n")
    (project / "x.md").write_text("a\n")
    (project / "gone.md").write_text("gone\n")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "adopted at 1.0.0")
    before_commit = git(project, "rev-parse", "HEAD")
    env_a = make_env(common, "1.0.0")
    point(common, "1.0.0")
    pin_before = {"existed": True, "link": str(env_a / "bin" / "gov"),
                  "record": json.loads((common / "gov/pin.json").read_text())}
    make_env(common, "1.0.1")
    point(common, "1.0.1")
    (project / "governance/framework.lock").write_text("release:\n  version: 1.0.1\n")
    (project / "x.md").write_text("b\n")
    (project / "new.md").write_text("new\n")
    (project / "gone.md").unlink()
    (project / "governance/updates").mkdir()
    (project / "governance/updates/1.0.1.json").write_text(json.dumps(
        {"from": "1.0.0", "to": "1.0.1", "commit_before": before_commit, "pin_before": pin_before}))
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "gov update: release 1.0.0 -> 1.0.1")
    return project


@pytest.fixture(autouse=True)
def rebuilds(monkeypatch):
    calls = []
    monkeypatch.setattr(core, "_rebuild", lambda project, link: calls.append((project, link)) or (0, ""))
    return calls


def test_the_pin_before_record_is_what_the_state_held():
    state = {"existed": True, "record": b'{"version": "1.0.0"}', "link": "/x/envs/1.0.0/bin/gov", "env_existed": True}
    assert core.pin_before(state) == {"existed": True, "link": "/x/envs/1.0.0/bin/gov",
                                      "record": {"version": "1.0.0"}}
    assert core.pin_before({"existed": False, "record": None, "link": None, "env_existed": False}) == {
        "existed": False, "link": None, "record": None}
    assert core.pin_before({"existed": True, "record": b"not json", "link": None, "env_existed": False})[
        "record"] is None


def test_the_rollback_reverts_the_update_in_one_commit_with_its_record_and_restores_the_pin(updated, rebuilds):
    head_before = git(updated, "rev-parse", "HEAD")
    before = git(updated, "rev-parse", "HEAD~1")
    report = core.rollback(updated)
    assert git(updated, "rev-parse", "HEAD~1") == head_before and git(updated, "status", "--porcelain") == ""
    assert (report["from"], report["to"], report["update_commit"], report["store"]) == (
        "1.0.1", "1.0.0", head_before, "refreshed")
    assert report["commit"] == git(updated, "rev-parse", "HEAD")
    rolled = tree(updated)
    expected = {path: meta for path, meta in git_tree(updated, before).items()}
    record = "governance/updates/1.0.1.rolled-back.json"
    assert set(rolled) - set(expected) == {record}
    assert {path: meta for path, meta in rolled.items() if path != record} == expected
    data = json.loads((updated / record).read_text())
    assert (data["from"], data["to"], data["update_commit"]) == ("1.0.1", "1.0.0", head_before)
    assert data["pin"]["existed"] is True and "revert_commit" not in data
    common = updated / ".git"
    assert os.readlink(common / "gov/bin/gov") == str(common / "gov/envs/1.0.0/bin/gov")
    assert json.loads((common / "gov/pin.json").read_text())["version"] == "1.0.0"
    assert (common / "gov/envs/1.0.1").is_dir()  # B's environment stays for diagnosis
    assert rebuilds == [(updated, common / "gov/bin/gov")]


def git_tree(repo: Path, commit: str) -> dict:
    out = {}
    for line in git(repo, "ls-tree", "-r", commit).splitlines():
        meta, path = line.split("\t")
        out[path] = meta
    return out


def test_a_project_with_no_pin_before_the_update_has_none_after(updated, rebuilds):
    common = updated / ".git"
    path = updated / "governance/updates/1.0.1.json"
    record = json.loads(path.read_text())
    record["pin_before"] = {"existed": False, "link": None, "record": None}
    path.write_text(json.dumps(record))
    git(updated, "commit", "-q", "-a", "--amend", "--no-edit")
    core.rollback(updated)
    assert not os.path.lexists(common / "gov/bin/gov") and not os.path.lexists(common / "gov/pin.json")
    assert (common / "gov/envs/1.0.1").is_dir() and (common / "gov/envs/1.0.0").is_dir()
    assert rebuilds[0][1] is None  # the running gov rebuilds


def test_a_record_without_pin_before_falls_back_to_the_environment_of_the_release_it_came_from(updated):
    path = updated / "governance/updates/1.0.1.json"
    record = json.loads(path.read_text())
    del record["pin_before"]
    path.write_text(json.dumps(record))
    git(updated, "commit", "-q", "-a", "--amend", "--no-edit")
    core.rollback(updated)
    common = updated / ".git"
    assert os.readlink(common / "gov/bin/gov") == str(common / "gov/envs/1.0.0/bin/gov")
    assert json.loads((common / "gov/pin.json").read_text()) == {
        "version": "1.0.0", "environment": str(common / "gov/envs/1.0.0")}


def test_the_fallback_without_the_environment_is_refused_before_anything_changes(updated):
    path = updated / "governance/updates/1.0.1.json"
    record = json.loads(path.read_text())
    del record["pin_before"]
    path.write_text(json.dumps(record))
    git(updated, "commit", "-q", "-a", "--amend", "--no-edit")
    common = updated / ".git"
    import shutil
    shutil.rmtree(common / "gov/envs/1.0.0")
    head = git(updated, "rev-parse", "HEAD")
    with pytest.raises(core.UpdateRefused) as refused:
        core.rollback(updated)
    assert refused.value.reason == "no_previous_pin" and "1.0.0" in str(refused.value)
    assert git(updated, "rev-parse", "HEAD") == head and git(updated, "status", "--porcelain") == ""


def test_a_later_commit_that_conflicts_stops_the_rollback_and_changes_nothing(updated, rebuilds):
    (updated / "x.md").write_text("later\n")
    git(updated, "commit", "-q", "-a", "-m", "a later change to what the update changed")
    head = git(updated, "rev-parse", "HEAD")
    common = updated / ".git"
    link = os.readlink(common / "gov/bin/gov")
    with pytest.raises(core.UpdateRefused) as refused:
        core.rollback(updated)
    assert refused.value.reason == "rollback_conflict" and "x.md" in str(refused.value)
    assert git(updated, "rev-parse", "HEAD") == head and git(updated, "status", "--porcelain") == ""
    assert not (updated / ".git/REVERT_HEAD").exists() and os.readlink(common / "gov/bin/gov") == link
    assert (updated / "x.md").read_text() == "later\n" and rebuilds == []


def test_the_refusals_no_update_dirty_and_not_adopted(updated, tmp_path):
    (updated / "stray.txt").write_text("x")
    with pytest.raises(core.UpdateRefused) as refused:
        core.rollback(updated)
    assert refused.value.reason == "dirty" and "stray.txt" in str(refused.value)
    (updated / "stray.txt").unlink()
    core.rollback(updated)  # now at 1.0.0: the update record of 1.0.0 does not exist
    with pytest.raises(core.UpdateRefused) as refused:
        core.rollback(updated)
    assert refused.value.reason == "no_update"
    plain = tmp_path / "plain"
    plain.mkdir()
    with pytest.raises(core.UpdateRefused) as refused:
        core.rollback(plain)
    assert refused.value.reason == "not_adopted"


def test_a_record_that_is_in_the_tree_but_was_never_committed_is_no_update(updated):
    git(updated, "rm", "-q", "--cached", "governance/updates/1.0.1.json")
    git(updated, "commit", "-q", "-m", "stop tracking the record")
    with pytest.raises(core.UpdateRefused) as refused:
        core.rollback(updated)
    assert refused.value.reason in ("no_update", "dirty")  # untracked file: refused either way, nothing changes


def test_a_failure_before_the_commit_puts_head_the_tree_and_the_pin_back(updated, monkeypatch):
    head = git(updated, "rev-parse", "HEAD")
    common = updated / ".git"
    link = os.readlink(common / "gov/bin/gov")
    monkeypatch.setattr(core, "_commit_rollback", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no commit")))
    with pytest.raises(core.UpdateFailed) as failed:
        core.rollback(updated)
    assert failed.value.rolled_back is True and "no commit" in str(failed.value)
    assert git(updated, "rev-parse", "HEAD") == head and git(updated, "status", "--porcelain") == ""
    assert os.readlink(common / "gov/bin/gov") == link
    assert json.loads((common / "gov/pin.json").read_text())["version"] == "1.0.1"


def test_a_failed_rebuild_leaves_the_rollback_committed_and_says_gov_rebuild_is_to_run(updated, monkeypatch):
    monkeypatch.setattr(core, "_rebuild", lambda project, link: (1, "store is broken"))
    with pytest.raises(core.StoreFailed) as failed:
        core.rollback(updated)
    assert "gov rebuild" in str(failed.value) and failed.value.report["store"] == "failed"
    assert failed.value.report["commit"] == git(updated, "rev-parse", "HEAD")
    assert (updated / "governance/updates/1.0.1.rolled-back.json").is_file()


class Args:
    def __init__(self, version=None, rollback=False, check=False, source=None, wheel=None):
        self.version, self.rollback, self.check, self.source, self.wheel = version, rollback, check, source, wheel


@pytest.mark.parametrize("args", [Args("1.0.1", rollback=True), Args(None), Args(None, rollback=True, check=True),
                                  Args(None, rollback=True, source="/s"), Args(None, rollback=True, wheel="/w")])
def test_the_command_refuses_a_wrong_command_line_as_usage(tmp_path, args):
    from gov.cli.errors import GovError
    with pytest.raises(GovError) as refused:
        update_command.run(tmp_path, args, {})
    assert refused.value.code == "UPDATE_REFUSED" and refused.value.details["reason"] == "usage"


def test_the_command_runs_the_rollback_and_maps_its_refusals(updated):
    from gov.cli.errors import GovError
    (updated / "stray.txt").write_text("x")
    with pytest.raises(GovError) as refused:
        update_command.run(updated, Args(rollback=True), {})
    assert refused.value.code == "UPDATE_REFUSED" and refused.value.details["reason"] == "dirty"
    (updated / "stray.txt").unlink()
    assert update_command.run(updated, Args(rollback=True), {})["to"] == "1.0.0"
