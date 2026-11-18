"""Unit tests of the memory-use log (W2-197 S8, S9, F2; DAEO-3d3o): the writer, its path, the reader and the command."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from gov import memory_use
from gov.cli.main import main

GIT_ENV = {"GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}


def git(folder: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(folder), "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", *args],
                   check=True, capture_output=True, env={"PATH": "/usr/bin:/bin", "HOME": str(folder), **GIT_ENV})


def record(**over) -> dict:
    base = {"command": "retrieve", "role": "engineer", "ticket": "DAEO-aaaa", "session": None,
            "query_sha256": "0123456789abcdef", "stop_reason": "SATURATED", "items": 2, "characters": 40,
            "latency_ms": 5, "refusal": None, "store_commit": "f" * 40, "reranked": False}
    return {**base, **over}


def lines(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


@pytest.fixture
def log(tmp_path, monkeypatch) -> Path:
    path = tmp_path / "logs" / "memory-use.jsonl"
    monkeypatch.setenv("GOV_MEMORY_LOG", str(path))
    return path


def test_append_writes_one_line_with_a_utc_timestamp(log, tmp_path):
    memory_use.append(record(), tmp_path)
    [line] = lines(log)
    assert line["command"] == "retrieve" and line["items"] == 2 and line["search_number"] is None
    assert line["ts"].endswith("+00:00") and line["ts"][:4].isdigit()


def test_search_number_counts_this_sessions_calls_of_the_command(log, tmp_path):
    for session in ("s1", "s2", "s1"):
        memory_use.append(record(session=session), tmp_path)
    memory_use.append(record(session="s1", command="brief"), tmp_path)
    assert [line["search_number"] for line in lines(log)] == [1, 1, 2, 1]


def test_append_never_raises_where_the_log_cannot_be_written(tmp_path, monkeypatch):
    folder = tmp_path / "a-folder"
    folder.mkdir()
    monkeypatch.setenv("GOV_MEMORY_LOG", str(folder))
    memory_use.append(record(session="s"), tmp_path)  # no exception
    memory_use.append({"not": object()}, tmp_path)  # not JSON: no exception either
    assert list(folder.iterdir()) == []


def test_default_path_is_the_main_worktree_of_a_linked_tree(tmp_path, monkeypatch):
    monkeypatch.delenv("GOV_MEMORY_LOG", raising=False)
    main_tree = tmp_path / "repo"
    main_tree.mkdir()
    git(main_tree, "init", "-q", "-b", "main")
    git(main_tree, "commit", "-q", "--allow-empty", "-m", "c")
    git(main_tree, "worktree", "add", "-q", "--detach", str(tmp_path / "linked"))
    assert memory_use.log_path(tmp_path / "linked") == main_tree.resolve() / ".gov-runtime/memory-use.jsonl"
    memory_use.append(record(), tmp_path / "linked")
    assert len(lines(main_tree / ".gov-runtime/memory-use.jsonl")) == 1


def test_default_path_outside_git_is_the_tree_itself(tmp_path, monkeypatch):
    monkeypatch.delenv("GOV_MEMORY_LOG", raising=False)
    assert memory_use.log_path(tmp_path) == tmp_path.resolve() / ".gov-runtime/memory-use.jsonl"


PLANTED = [
    {"ts": "2026-11-15T10:00:00+00:00", "command": "retrieve", "role": "engineer", "refusal": None},
    {"ts": "2026-11-15T11:00:00+00:00", "command": "retrieve", "role": "engineer", "refusal": "STORE_MISSING"},
    {"ts": "2026-11-15T12:00:00+00:00", "command": "brief", "role": "engineer", "refusal": None},
    {"ts": "2026-11-16T09:00:00+00:00", "command": "retrieve", "role": "research", "refusal": None},
    {"ts": "2026-11-16T09:30:00+00:00", "command": "brief", "role": None, "refusal": None},
]


def plant_log(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = [json.dumps(item) for item in PLANTED[:2]] + ["{not json", "[1, 2]"] + \
        [json.dumps(item) for item in PLANTED[2:]]
    path.write_text("\n".join(text) + "\n", encoding="utf-8")
    return path


def test_read_skips_and_counts_unreadable_lines(tmp_path):
    records = memory_use.read(plant_log(tmp_path / "log.jsonl"))
    assert list(records) == PLANTED and records.skipped == 2


def test_read_since_keeps_the_later_days_and_a_missing_log_is_empty(tmp_path, monkeypatch):
    path = plant_log(tmp_path / "log.jsonl")
    assert [item["ts"][:10] for item in memory_use.read(path, since="2026-11-16")] == ["2026-11-16"] * 2
    monkeypatch.setenv("GOV_MEMORY_LOG", str(tmp_path / "absent.jsonl"))
    empty = memory_use.read()
    assert list(empty) == [] and empty.skipped == 0


def test_read_by_root_finds_the_default_log(tmp_path, monkeypatch):
    monkeypatch.delenv("GOV_MEMORY_LOG", raising=False)
    plant_log(tmp_path / ".gov-runtime/memory-use.jsonl")
    assert len(memory_use.read(root=tmp_path)) == len(PLANTED)


def test_per_role_day_counts_retrieves_briefs_and_refusals():
    counted = memory_use.per_role_day(PLANTED)
    assert counted == {
        ("2026-11-15", "engineer"): {"retrieves": 2, "briefs": 1, "refused": 1},
        ("2026-11-16", "none"): {"retrieves": 0, "briefs": 1, "refused": 0},
        ("2026-11-16", "research"): {"retrieves": 1, "briefs": 0, "refused": 0},
    }
    assert list(counted) == sorted(counted)


def test_command_prints_one_line_per_day_and_role(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("GOV_MEMORY_LOG", str(plant_log(tmp_path / "log.jsonl")))
    assert main(["memory-use", "--root", str(tmp_path)]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "2026-11-15 engineer retrieves 2 briefs 1 refused 1",
        "2026-11-16 none retrieves 0 briefs 1 refused 0",
        "2026-11-16 research retrieves 1 briefs 0 refused 0",
    ]
    assert main(["memory-use", "--root", str(tmp_path), "--since", "2026-11-16", "--json"]) == 0
    envelope = json.loads(capsys.readouterr().out)
    assert envelope["ok"] is True and envelope["command"] == "memory-use"
    assert [row["day"] for row in envelope["result"]["rows"]] == ["2026-11-16"] * 2
    assert envelope["result"]["skipped"] == 2


def test_command_refuses_a_since_that_is_not_a_day(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("GOV_MEMORY_LOG", str(tmp_path / "log.jsonl"))
    assert main(["memory-use", "--root", str(tmp_path), "--since", "yesterday"]) == 1
    assert "SINCE_INVALID" in capsys.readouterr().err
