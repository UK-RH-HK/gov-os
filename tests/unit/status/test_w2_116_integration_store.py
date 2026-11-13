"""``gov status``'s ``integration_store`` part (W2-116 pass 2b, S2; P-W2-116-S2-INTERFACE Q1 (a), DEC-1157 (12)):
the store's head and age, the branch's head, the stale rule and the parts not read.

Regression evidence only (MR-3). The project is a temporary git repository on a branch ``integrate``; the store's half
is a detached worktree of it, its W2-122 record written by hand (``written_at``), the link a symbolic link to it. No
store is built and no model is asked. The clock is ``GOV_NOW``; a verdict file's time is planted with ``os.utime``.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.rebuild import integration  # noqa: E402
from gov.status import command  # noqa: E402
from gov.status.integration_store import read  # noqa: E402

_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
DAY = "2026-11-13"
CONFIG = ("integration_refresh:\n  branch: integrate\n  after_nightly:\n    verdict: verdicts/*.txt\n"
          "    latest: \"10:00\"\n  second: \"18:00\"\n")


def _git(where, *args):
    return subprocess.run(["git", "-C", str(where), *args], check=True, capture_output=True, text=True,
                          env={**_ENV, "HOME": str(where)}).stdout.strip()


def _commit(root, message):
    (root / "file.txt").write_text(message, encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", message)
    return _git(root, "rev-parse", "HEAD")


def _at(text):
    return datetime.fromisoformat(text).astimezone()


@pytest.fixture()
def project(tmp_path, monkeypatch):
    """A project at its branch's head, its store built at that head at 08:00 on the day, the clock at noon."""
    root = tmp_path / "project"
    root.mkdir()
    _git(root, "init", "-q", "-b", "integrate")
    head = _commit(root, "one")
    (root / ".gitignore").write_text(".gov-runtime/\n", encoding="utf-8")
    link = tmp_path / "stores" / "store"
    half = tmp_path / "stores" / "store-a"
    _git(root, "worktree", "add", "-q", "--detach", str(half), head)
    link.symlink_to(half)
    monkeypatch.setenv("GOV_NOW", f"{DAY}T12:00:00+00:00")
    world = {"root": root, "link": link, "half": half.resolve(), "head": head}
    _settings(world, CONFIG)
    _built(world, f"{DAY}T11:00:00+00:00")  # after yesterday's second, and after today's latest...
    _verdict(world, "run.txt", f"{DAY}T10:30:00+00:00")  # ... which a verdict at 10:30 stood in for
    return world


def _settings(world, refresh):
    folder = world["root"] / "governance" / "project"
    folder.mkdir(parents=True, exist_ok=True)
    text = f"integration_store: {world['link']}\n" + ("" if refresh is None else refresh)
    (folder / "rebuild.yaml").write_text(text, encoding="utf-8")


def _built(world, when):
    record = world["half"] / ".gov-runtime" / "rebuild" / "stores.json"
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(json.dumps({"code": "sha256:x", "written_at": when}), encoding="utf-8")


def _verdict(world, name, when, text="verdict: PASS\n"):
    path = world["root"] / "verdicts" / name
    path.parent.mkdir(exist_ok=True)
    path.write_text(text, encoding="utf-8")
    stamp = _at(when).timestamp()
    os.utime(path, (stamp, stamp))


def _now(monkeypatch, when):
    monkeypatch.setenv("GOV_NOW", when)


def _unread(value):
    return isinstance(value, dict) and value.get("read") is False


# the part --------------------------------------------------------------------------------------------------------------

def test_a_fresh_store_names_its_head_age_and_branch_and_is_not_stale(project):
    part = read(project["root"])
    assert part == {"link": str(project["link"]), "half": str(project["half"]), "head": project["head"],
                    "branch": "integrate", "branch_head": project["head"],
                    "built_at": f"{DAY}T11:00:00+00:00", "age_seconds": 3600,
                    "stale": False, "stale_reason": None, "last_refresh": None}


def test_the_last_refresh_is_the_record_beside_the_link(project):
    record = {"at": f"{DAY}T10:30:00+00:00", "reason": "after_nightly", "head": project["head"],
              "status": "switched", "branch": "integrate"}
    integration.record_path(project["link"]).write_text(json.dumps(record), encoding="utf-8")
    assert read(project["root"])["last_refresh"] == record


def test_the_age_is_in_whole_seconds_of_the_planted_clock(project, monkeypatch):
    _now(monkeypatch, f"{DAY}T11:00:42.9+00:00")
    assert read(project["root"])["age_seconds"] == 42
    _now(monkeypatch, f"{DAY}T07:00:00-05:00")  # 12:00 UTC: the offset is an instant
    assert read(project["root"])["age_seconds"] == 3600


def test_the_part_is_a_json_value_in_the_commands_answer(project):
    answer = command.run(project["root"], argparse.Namespace(json=True), {})
    assert json.loads(json.dumps(answer["integration_store"]))["head"] == project["head"]
    assert answer["integration_store"]["stale"] is False
    assert not [reason for reason in answer["not_read"] if reason.startswith("integration_store")]


# stale: behind the branch ----------------------------------------------------------------------------------------------

def test_a_store_behind_its_branch_is_stale_and_names_both_heads(project):
    new = _commit(project["root"], "two")
    part = read(project["root"])
    assert part["stale"] is True and part["branch_head"] == new and part["head"] == project["head"]
    assert part["stale_reason"].startswith("behind_branch: ")
    assert project["head"][:12] in part["stale_reason"] and new[:12] in part["stale_reason"]
    assert "built_before_due" not in part["stale_reason"]


def test_a_store_ahead_of_its_branch_is_not_at_its_head_either(project):
    _git(project["root"], "branch", "other")
    _commit(project["root"], "two")
    _git(project["root"], "checkout", "-q", "--detach", "other")  # the half's repository: the main tree
    _settings(project, CONFIG.replace("branch: integrate", "branch: other"))
    new = _commit(project["root"], "three")  # detached: moves HEAD only
    _git(project["root"], "branch", "-f", "other", project["head"])
    part = read(project["root"])
    assert part["branch_head"] == project["head"] and part["stale"] is False
    assert new != project["head"]


# stale: built before a refresh fell due ----------------------------------------------------------------------------------

def test_a_store_built_before_the_nightly_verdict_is_stale_and_names_that_time(project, monkeypatch):
    _built(project, f"{DAY}T10:00:00+00:00")
    part = read(project["root"])
    assert part["stale"] is True and part["stale_reason"].startswith("built_before_due: ")
    assert f"{DAY}T10:30:00+00:00" in part["stale_reason"] and "behind_branch" not in part["stale_reason"]


def test_a_store_built_after_the_verdict_is_not_stale(project):
    _built(project, f"{DAY}T10:30:01+00:00")
    assert read(project["root"])["stale"] is False


def test_a_store_built_at_the_time_it_fell_due_is_not_stale(project):
    _built(project, f"{DAY}T10:30:00+00:00")
    assert read(project["root"])["stale"] is False


@pytest.mark.parametrize("now, built, due, stale", [
    # no verdict file at all: ``latest`` and ``second`` are the times a refresh falls due, today's and yesterday's
    ("T09:00:00", "2026-11-12T18:00:00+00:00", "2026-11-12T18:00:00+00:00", False),
    ("T09:00:00", "2026-11-12T17:59:59+00:00", "2026-11-12T18:00:00+00:00", True),
    ("T10:00:00", "2026-11-13T09:59:59+00:00", "2026-11-13T10:00:00+00:00", True),
    ("T10:00:00", "2026-11-13T10:00:00+00:00", "2026-11-13T10:00:00+00:00", False),
    ("T17:59:59", "2026-11-13T10:00:00+00:00", "2026-11-13T10:00:00+00:00", False),
    ("T18:00:00", "2026-11-13T17:59:59+00:00", "2026-11-13T18:00:00+00:00", True),
    ("T18:00:00", "2026-11-13T18:00:00+00:00", "2026-11-13T18:00:00+00:00", False),
])
def test_without_a_verdict_the_latest_and_second_times_are_when_a_refresh_fell_due(project, monkeypatch, now, built,
                                                                                   due, stale):
    (project["root"] / "verdicts" / "run.txt").unlink()
    _now(monkeypatch, DAY + now + "+00:00")
    _built(project, built)
    part = read(project["root"])
    assert part["stale"] is stale
    if stale:
        assert due in part["stale_reason"]


def test_a_verdict_file_that_holds_no_verdict_is_no_refresh_due(project, monkeypatch):
    _verdict(project, "running.txt", f"{DAY}T11:45:00+00:00", text="nightly: step 2 of 9\n")  # not counted
    _built(project, f"{DAY}T10:31:00+00:00")
    assert read(project["root"])["stale"] is False


def test_both_reasons_are_given_joined_each_with_its_code(project):
    _commit(project["root"], "two")
    _built(project, f"{DAY}T10:00:00+00:00")
    reason = read(project["root"])["stale_reason"]
    codes = [piece.split(":")[0] for piece in reason.split("; ")]
    assert codes == ["behind_branch", "built_before_due"], reason


def test_the_verdict_after_now_is_not_yet_a_time_that_fell_due(project, monkeypatch):
    _verdict(project, "later.txt", f"{DAY}T13:00:00+00:00")
    os.remove(project["root"] / "verdicts" / "run.txt")
    _built(project, f"{DAY}T10:00:01+00:00")
    assert read(project["root"])["stale"] is False  # today's latest (10:00): the verdict at 13:00 is not before it...
    # ... but it falls on today's date after ``latest``, so ``latest`` still counts; the built time is after it


# the parts not read ----------------------------------------------------------------------------------------------------

def test_no_integration_store_configured_is_a_part_not_read(project):
    (project["root"] / "governance" / "project" / "rebuild.yaml").write_text(CONFIG, encoding="utf-8")
    part = read(project["root"])
    assert _unread(part) and "integration_store" in part["reason"]


def test_no_rebuild_yaml_is_a_part_not_read(project):
    (project["root"] / "governance" / "project" / "rebuild.yaml").unlink()
    assert _unread(read(project["root"]))


def test_a_setting_that_is_not_an_absolute_path_is_a_part_not_read_never_a_refusal(project):
    (project["root"] / "governance" / "project" / "rebuild.yaml").write_text("integration_store: relative/path\n",
                                                                             encoding="utf-8")
    assert _unread(read(project["root"]))


def test_no_link_is_a_part_not_read(project):
    project["link"].unlink()
    part = read(project["root"])
    assert _unread(part) and str(project["link"]) in part["reason"]


def test_a_link_that_leads_to_no_folder_is_a_part_not_read(project, tmp_path):
    project["link"].unlink()
    project["link"].symlink_to(tmp_path / "nowhere")
    assert _unread(read(project["root"]))


@pytest.mark.parametrize("refresh, named", [
    (None, "integration_refresh"),
    ("integration_refresh:\n  branch: integrate\n  after_nightly: {latest: \"10:00\"}\n  second: \"9:5\"\n",
     "integration_refresh.second"),
    ("integration_refresh:\n  after_nightly: {latest: \"10:00\"}\n  second: \"18:00\"\n", "integration_refresh.branch"),
])
def test_without_a_valid_refresh_block_the_branch_and_the_stale_rule_are_not_read_and_the_rest_is_given(
        project, refresh, named):
    _settings(project, refresh)
    part = read(project["root"])
    for name in ("branch", "branch_head", "stale", "stale_reason"):
        assert _unread(part[name]) and named in part[name]["reason"], name
    assert part["link"] == str(project["link"]) and part["half"] == str(project["half"])
    assert part["head"] == project["head"] and part["built_at"] == f"{DAY}T11:00:00+00:00"
    assert part["age_seconds"] == 3600 and part["last_refresh"] is None


def test_an_invalid_clock_leaves_the_age_and_the_time_rule_not_read_but_never_refuses(project, monkeypatch):
    _now(monkeypatch, "noon")
    part = read(project["root"])
    assert _unread(part["age_seconds"]) and "GOV_NOW" in part["age_seconds"]["reason"]
    assert part["head"] == project["head"] and part["branch_head"] == project["head"]
    assert _unread(part["stale"]) and "built_before_due" in part["stale"]["reason"]


def test_an_invalid_clock_does_not_hide_a_store_behind_its_branch(project, monkeypatch):
    _now(monkeypatch, "noon")
    _commit(project["root"], "two")
    part = read(project["root"])
    assert part["stale"] is True and part["stale_reason"].startswith("behind_branch")


def test_a_half_with_no_record_has_no_built_time_and_its_stale_rule_for_time_is_not_read(project):
    (project["half"] / ".gov-runtime" / "rebuild" / "stores.json").unlink()
    part = read(project["root"])
    assert _unread(part["built_at"]) and _unread(part["age_seconds"]) and _unread(part["stale"])
    assert part["head"] == project["head"]


def test_a_branch_not_known_in_the_project_is_not_read_and_so_is_the_rule(project):
    _settings(project, CONFIG.replace("branch: integrate", "branch: nowhere"))
    part = read(project["root"])
    assert part["branch"] == "nowhere" and _unread(part["branch_head"]) and _unread(part["stale"])
    assert "nowhere" in part["branch_head"]["reason"]


def test_each_place_not_read_is_named_in_the_commands_not_read(project, monkeypatch):
    _settings(project, None)
    answer = command.run(project["root"], argparse.Namespace(json=True), {})
    named = [reason for reason in answer["not_read"] if reason.startswith("integration_store.")]
    assert [reason.split(":")[0] for reason in named] == ["integration_store.branch", "integration_store.branch_head",
                                                          "integration_store.stale", "integration_store.stale_reason"]


def test_a_project_without_the_store_still_answers_and_names_the_part_in_not_read(tmp_path):
    root = tmp_path / "bare"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    answer = command.run(root, argparse.Namespace(json=True), {})
    assert _unread(answer["integration_store"])
    assert any(reason.startswith("integration_store:") for reason in answer["not_read"])
