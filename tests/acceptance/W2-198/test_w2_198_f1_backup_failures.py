"""F1: a failed backup loses no backup."""

from __future__ import annotations

import pytest

import w2_198_support as s

NOW = "2026-11-18T12:30:00Z"
OLD = ["proj-20260901T000000Z.bundle", "proj-20260902T000000Z.bundle", "proj-20260903T000000Z.bundle",
       "proj-20260904T000000Z.bundle"]


def _plant(dest):
    """Older bundles a retention pass at --keep 1 --days 1 would delete all but one of."""
    for name in OLD:
        s.write(dest / name, f"older bundle {name}\n")
    return s.listing(dest)


def _refused(run, code: str, json_form: bool):
    assert run.code == 1, f"exit {run.code}, not 1: {run.both[-600:]}"
    if json_form:
        envelope = run.envelope()
        assert envelope["ok"] is False and envelope["error"]["code"] == code, envelope
    else:
        assert code in run.err, f"stderr does not name {code}: {run.err[-600:]}"


def _no_bundle_under(home):
    root = home / ".gov-os"
    assert not root.exists() or not any(p.is_file() for p in root.rglob("*")), "a file was written under ~/.gov-os"


@pytest.mark.parametrize("json_form", [False, True], ids=["text", "json"])
def test_f1_a_bundle_failing_verify_exits_1_and_the_dest_is_unchanged(tmp_path, home, env, json_form):
    repo = s.simple_repo(tmp_path, env, "proj")
    dest = tmp_path / "dest"
    before = _plant(dest)
    args = ["backup", "--root", repo, "--dest", dest, "--keep", "1", "--days", "1"] + (["--json"] if json_form else [])
    run = s.gov(args, env=s.git_stub_env(tmp_path, {**env, "GOV_BACKUP_NOW": NOW}), cwd=tmp_path)
    _refused(run, "BACKUP_VERIFY_FAILED", json_form)
    assert s.listing(dest) == before, "the dest changed: a file of this run remains or an older bundle is gone"


def test_f1_a_repository_with_no_commit_exits_1_and_deletes_nothing(tmp_path, home, env):
    repo = tmp_path / "proj"
    repo.mkdir()
    s.git("init", "-q", cwd=repo, env=env)
    dest = tmp_path / "dest"
    before = _plant(dest)
    run = s.gov(["backup", "--root", repo, "--dest", dest, "--keep", "1", "--days", "1"],
                env={**env, "GOV_BACKUP_NOW": NOW}, cwd=tmp_path)
    _refused(run, "BACKUP_FAILED", json_form=False)
    assert s.listing(dest) == before


@pytest.mark.parametrize("inside", ["main", "linked"])
def test_f1_a_dest_inside_the_repository_or_a_worktree_exits_1_and_writes_nothing(tmp_path, home, env, inside):
    world = s.backup_world(tmp_path, env)
    dest = world[inside] / "backups"
    before = _plant(dest)
    run = s.gov(["backup", "--root", world["main"], "--dest", dest, "--keep", "1", "--days", "1"],
                env={**env, "GOV_BACKUP_NOW": NOW}, cwd=tmp_path)
    _refused(run, "BACKUP_DEST_INSIDE", json_form=False)
    assert s.listing(dest) == before
    _no_bundle_under(home)
