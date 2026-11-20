"""W2-17 fix S5 (DEC-1223 (6)): ``gov.update.pending``, the reading behind doctor's ``updates`` part and the session
start line. Builder evidence: small tmp repositories, no copier, no network.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

from gov.update import pending as pending_module
from gov.update.pending import pending


def git(repo: Path, *args: str) -> str:
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True,
                          env=env).stdout


def record(source: Path, version: str) -> None:
    folder = source / "docs" / "releases" / version
    folder.mkdir(parents=True, exist_ok=True)
    data = json.dumps({"version": version, "files": {"a": "0" * 64}, "wheel": {"name": "w.whl"}}).encode()
    (folder / "manifest.json").write_bytes(data)
    (folder / "manifest.sha256").write_text(hashlib.sha256(data).hexdigest() + "  manifest.json\n")


def release(source: Path, version: str, *, kind=None, fixes: int = 0, tag: bool = True) -> None:
    for number in range(fixes):
        git(source, "commit", "-q", "--allow-empty", "-m", f"fix {version} {number}\n\nFix: a fix {number}")
    git(source, "commit", "-q", "--allow-empty", "-m", f"chore for {version}\n\nClass: C")
    record(source, version)
    if kind is not None:
        (source / "docs" / "releases" / version / "kind.json").write_text(
            kind if isinstance(kind, str) else json.dumps(kind))
    git(source, "add", "-A")
    git(source, "commit", "-q", "-m", f"release {version}")
    if tag:
        git(source, "tag", f"v{version}")


def make_source(tmp_path: Path) -> Path:
    source = tmp_path / "source"
    source.mkdir()
    git(source, "init", "-q", "-b", "main")
    release(source, "0.9.0")
    return source


def make_project(tmp_path: Path, source, held: str | None = "0.9.0") -> Path:
    project = tmp_path / "project"
    (project / "governance").mkdir(parents=True)
    (project / ".copier-answers.yml").write_text(f"_commit: v0.9.0\n_src_path: {source}\n")
    lock = "release: null\n" if held is None else f"release:\n  version: {held}\n"
    (project / "governance/framework.lock").write_text(lock)
    return project


def test_a_newer_patch_release_is_pending_with_its_fixes_and_the_quiet_point(tmp_path):
    source = make_source(tmp_path)
    release(source, "0.9.1", kind={"kind": "patch"}, fixes=2)
    got = pending(make_project(tmp_path, source))
    assert got["status"] == "report" and got["pending"] is True
    assert (got["held"], got["newest"], got["kind"], got["fixes"]) == ("0.9.0", "0.9.1", "patch", 2)
    assert "at the next quiet point" in got["next"] and "0.9.1" in got["summary"]


def test_a_release_with_no_kind_file_is_bigger_and_names_the_owner_step(tmp_path):
    source = make_source(tmp_path)
    release(source, "0.9.1")
    got = pending(make_project(tmp_path, source))
    assert got["kind"] == "bigger" and got["pending"] is True
    assert got["next"] == "bigger: the owner decides, gov update 0.9.1"


def test_an_unreadable_or_other_kind_is_bigger(tmp_path):
    for kind in ("not json", {"kind": "minor"}, ["patch"], {"nokind": 1}):
        source = tmp_path / str(abs(hash(str(kind))))
        source.mkdir()
        git(source, "init", "-q", "-b", "main")
        release(source, "0.9.0")
        release(source, "0.9.1", kind=kind)
        project = tmp_path / f"p{abs(hash(str(kind)))}"
        project.mkdir()
        got = pending(make_project(project, source))
        assert got["kind"] == "bigger", kind


def test_the_newest_verified_release_wins_and_a_tag_without_a_record_is_skipped(tmp_path):
    source = make_source(tmp_path)
    release(source, "0.9.1", kind={"kind": "patch"}, fixes=1)
    release(source, "0.10.0", kind={"kind": "patch"}, fixes=1)  # numeric: 0.10.0 is newer than 0.9.1
    git(source, "commit", "-q", "--allow-empty", "-m", "a decoy")
    git(source, "tag", "v0.11.0")  # no record: never the newest
    got = pending(make_project(tmp_path, source))
    assert got["newest"] == "0.10.0" and got["fixes"] == 2


def test_a_repository_at_the_newest_release_is_up_to_date(tmp_path):
    source = make_source(tmp_path)
    release(source, "0.9.1")
    got = pending(make_project(tmp_path, source, held="0.9.1"))
    assert got["pending"] is False and got["status"] == "report" and "up to date (0.9.1)" in got["summary"]
    assert got["held"] == "0.9.1" and got["reason"]


def test_an_update_rolled_back_here_is_held_until_a_newer_release(tmp_path):
    source = make_source(tmp_path)
    release(source, "0.9.1", kind={"kind": "patch"})
    project = make_project(tmp_path, source)
    (project / "governance/updates").mkdir()
    (project / "governance/updates/0.9.1.rolled-back.json").write_text("{}")
    got = pending(project)
    assert got["pending"] is False and got["rolled_back"] is True and got["newest"] == "0.9.1"
    assert got["next"] == "held: rolled back here; waits for a newer release"
    release(source, "0.9.2", kind={"kind": "patch"})  # a newer release lifts the hold
    again = pending(project)
    assert again["pending"] is True and again["newest"] == "0.9.2" and not again.get("rolled_back")


def test_no_held_release_no_readable_source_or_no_git_report_nothing_pending_and_never_raise(tmp_path):
    source = make_source(tmp_path)
    release(source, "0.9.1")
    (tmp_path / "a").mkdir()
    got = pending(make_project(tmp_path / "a", source, held=None))
    assert got["pending"] is False and got["reason"] and got["status"] == "report"
    (tmp_path / "b").mkdir()
    gone = make_project(tmp_path / "b", tmp_path / "nowhere")
    assert pending(gone)["pending"] is False and pending(gone)["reason"]
    (tmp_path / "c").mkdir()
    plain = make_project(tmp_path / "c", tmp_path)  # a folder that is no git repository
    assert pending(plain)["pending"] is False and pending(plain)["reason"]
    (tmp_path / "d").mkdir()
    empty = tmp_path / "d" / "project"
    empty.mkdir()  # no lock, no answers
    assert pending(empty)["pending"] is False and pending(empty)["reason"]


def test_a_relative_src_path_is_read_from_the_project_and_the_source_can_be_given(tmp_path):
    source = make_source(tmp_path)
    release(source, "0.9.1", kind={"kind": "patch"})
    project = make_project(tmp_path, "../source")
    assert pending(project)["newest"] == "0.9.1"
    (project / ".copier-answers.yml").write_text("_commit: v0.9.0\n")
    assert pending(project)["pending"] is False
    assert pending(project, source=source)["newest"] == "0.9.1"


def test_fixes_are_zero_where_the_held_tag_cannot_be_read(tmp_path):
    source = make_source(tmp_path)
    release(source, "0.9.1", kind={"kind": "patch"}, fixes=3)
    git(source, "tag", "-d", "v0.9.0")
    got = pending(make_project(tmp_path, source))
    assert got["pending"] is True and got["fixes"] == 0


def test_any_failure_inside_the_reading_is_a_reason_not_an_exception(tmp_path, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("boom")
    monkeypatch.setattr(pending_module, "_candidates", boom)
    got = pending(make_project(tmp_path, make_source(tmp_path)))
    assert got["pending"] is False and "boom" in got["reason"] and got["status"] == "report"
