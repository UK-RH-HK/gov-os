"""S1: `gov backup` bundles every ref of the repository into one dated, verified file outside the tree."""

from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest

import w2_198_support as s

NOW = "2026-11-18T12:30:00Z"
NOW_FILE = "proj-20261118T123000Z.bundle"


def _check_bundle(bundle: Path, world: dict, env: dict) -> set:
    heads = s.list_heads(bundle, env)
    missing = s.for_each_ref(world["main"], env) - heads
    assert not missing, f"refs of `git for-each-ref` missing from the bundle: {sorted(missing)}"
    assert world["loose"] in {sha for sha, _ in heads}, "the detached worktree's commit is not in the bundle"
    return heads


def test_s1_default_dest_holds_one_verified_bundle_of_every_ref(tmp_path, home, env):
    world = s.backup_world(tmp_path, env)
    run = s.gov(["backup", "--root", world["main"], "--json"], env={**env, "GOV_BACKUP_NOW": NOW}, cwd=tmp_path)
    assert run.code == 0, f"exit {run.code}: {run.err[-600:]}"
    dest = home / ".gov-os" / "backups" / "proj"
    assert dest.is_dir() and sorted(p.name for p in dest.iterdir()) == [NOW_FILE]
    bundle = dest / NOW_FILE
    result = run.envelope()["result"]
    assert Path(result["file"]).resolve() == bundle.resolve()
    assert result["bytes"] == bundle.stat().st_size
    assert result["verified"] is True
    assert isinstance(result["refs"], int) and result["refs"] >= len(s.for_each_ref(world["main"], env))
    assert "kept" in result and "removed" in result
    _check_bundle(bundle, world, env)
    clone = tmp_path / "clone"
    subprocess.run([s.REAL_GIT, "clone", "-q", "--mirror", str(bundle), str(clone)], env=env, check=True,
                   capture_output=True)
    branches = {sha for sha, ref in s.for_each_ref(world["main"], env) if ref.startswith("refs/heads/")}
    for sha in branches | {world["dev"], world["feature"]}:
        done = subprocess.run([s.REAL_GIT, "cat-file", "-e", f"{sha}^{{commit}}"], cwd=clone, env=env)
        assert done.returncode == 0, f"the clone of the bundle lacks commit {sha}"


def test_s1_text_form_is_one_line_naming_file_refs_verified_and_counts(tmp_path, home, env):
    world = s.backup_world(tmp_path, env)
    before = datetime.now(timezone.utc)
    run = s.gov(["backup", "--root", world["main"]], env=env, cwd=tmp_path)
    after = datetime.now(timezone.utc)
    assert run.code == 0, f"exit {run.code}: {run.err[-600:]}"
    dest = home / ".gov-os" / "backups" / "proj"
    files = sorted(p.name for p in dest.iterdir())
    assert len(files) == 1
    found = s.name_form("proj").match(files[0])
    assert found, files
    when = datetime.strptime(found.group(1), "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    assert before.replace(microsecond=0).timestamp() - 2 <= when.timestamp() <= after.timestamp() + 2, \
        "the name's time is not the UTC time of the run"
    lines = run.out.splitlines()
    assert len(lines) == 1, f"stdout is not one line: {run.out!r}"
    line = lines[0]
    assert files[0] in line and "verified" in line
    fewest = len(s.for_each_ref(world["main"], env))
    most = len(s.list_heads(dest / files[0], env))
    words = " ".join(word for word in line.split() if "/" not in word and files[0] not in word)
    numbers = [int(n) for n in re.findall(r"(?<![\w.])\d+(?![\w.])", words)]
    assert 1 in numbers and 0 in numbers, f"kept 1 and removed 0 are not in {line!r}"
    assert any(fewest <= n <= most for n in numbers), f"no ref count ({fewest} to {most}) in {line!r}"


@pytest.mark.parametrize("where", ["GOV_BACKUP_ROOT", "--dest", "--name"])
def test_s1_backup_root_dest_and_name_place_the_file(tmp_path, home, env, where):
    world = s.backup_world(tmp_path, env)
    run_env = {**env, "GOV_BACKUP_NOW": NOW}
    args = ["backup", "--root", world["main"]]
    if where == "GOV_BACKUP_ROOT":
        run_env["GOV_BACKUP_ROOT"] = str(tmp_path / "vault")
        expected = tmp_path / "vault" / "proj" / NOW_FILE
    elif where == "--dest":
        args += ["--dest", tmp_path / "elsewhere"]
        expected = tmp_path / "elsewhere" / NOW_FILE
    else:
        args += ["--name", "other"]
        expected = home / ".gov-os" / "backups" / "other" / "other-20261118T123000Z.bundle"
    run = s.gov(args, env=run_env, cwd=tmp_path)
    assert run.code == 0, f"exit {run.code}: {run.err[-600:]}"
    assert expected.is_file(), f"no bundle at {expected}"
    assert sorted(p.name for p in expected.parent.iterdir()) == [expected.name]
    if where != "--name":
        assert not (home / ".gov-os" / "backups").exists() or not any((home / ".gov-os" / "backups").rglob("*.bundle"))
    _check_bundle(expected, world, env)


def test_s1_run_from_the_linked_worktree_bundles_the_same_refs(tmp_path, home, env):
    world = s.backup_world(tmp_path, env)
    first = s.gov(["backup", "--root", world["main"]], env={**env, "GOV_BACKUP_NOW": NOW}, cwd=tmp_path)
    assert first.code == 0, f"exit {first.code}: {first.err[-600:]}"
    second = s.gov(["backup", "--root", world["linked"]], env={**env, "GOV_BACKUP_NOW": "2026-11-18T13:30:00Z"},
                   cwd=world["linked"])
    assert second.code == 0, f"exit {second.code}: {second.err[-600:]}"
    dest = home / ".gov-os" / "backups" / "proj"
    from_main = _check_bundle(dest / NOW_FILE, world, env)
    from_linked = _check_bundle(dest / "proj-20261118T133000Z.bundle", world, env)
    assert {h for h in from_main if h[1] != "HEAD"} == {h for h in from_linked if h[1] != "HEAD"}
