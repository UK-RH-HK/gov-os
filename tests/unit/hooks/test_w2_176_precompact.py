"""W2-176 (DAEO-ktiw) S1 and F1 for precompact.py: the compaction summary opens with the read-first line.

The hook runs as a subprocess fed planted PreCompact events (trigger auto and manual) for GOV_ROLE orchestrator, in a
main tree and in a linked worktree, and for engineer [DEC-1140 (1)(b), DEC-208, DEC-250, DEC-838 (1)].
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOKS = REPO_ROOT / "template" / "governance" / "kernel" / "hooks"
HOOK = HOOKS / "precompact.py"

ORCH = ".gov-runtime/scratch/orchestrator/CHECKPOINT.md"
LEAD = ".gov-runtime/scratch/lead/CHECKPOINT.md"
BRIEFS = ".gov-runtime/scratch/brief"
RECORDS = ".gov-runtime/scratch/checkpoints"
SCRATCH = ".gov-runtime/scratch"
TICKET = "DAEO-test"
INSTRUCTION = "Begin the compaction summary with this line:"
WRITTEN = "# C\n\n## RESUME HERE\n\n- ZQ-176\n"
BEGIN = "<!-- GENERATED STATE BLOCK BEGIN -->"


def _run(root, role, ticket=None, trigger="auto"):
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(root.parent / "home"),
        "CLAUDE_PROJECT_DIR": str(root),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": str(REPO_ROOT / "src"),
        "GIT_CONFIG_GLOBAL": os.devnull,
    }
    if role is not None:
        env["GOV_ROLE"] = role
    if ticket is not None:
        env["GOV_TICKET"] = ticket
    event = {"session_id": "s-176", "transcript_path": str(root.parent / "t.jsonl"), "cwd": str(root),
             "hook_event_name": "PreCompact", "trigger": trigger,
             "custom_instructions": None if trigger == "auto" else "keep the plan"}
    return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(event), capture_output=True, text=True,
                          cwd=str(root), env=env, timeout=30, check=False)


def _lines(done):
    return [line for line in done.stdout.splitlines() if line.strip()]


def _no_decision(done):
    for line in _lines(done):
        try:
            data = json.loads(line)
        except ValueError:
            continue
        assert not (isinstance(data, dict) and "decision" in data), f"a decision field was produced: {line!r}"


def _snapshot(root):
    return {str(p.relative_to(root)): (p.stat().st_size, p.stat().st_mtime_ns)
            for p in root.rglob("*") if p.is_file()}


@pytest.fixture()
def main_tree(tmp_path):
    root = tmp_path / "main"
    (root / ORCH).parent.mkdir(parents=True)
    (root / ORCH).write_text(WRITTEN)
    return root


@pytest.fixture()
def linked_tree(tmp_path):
    root = tmp_path / "wt"
    (root / LEAD).parent.mkdir(parents=True)
    (root / LEAD).write_text(WRITTEN)
    (root / ".git").write_text("gitdir: /nowhere/.git/worktrees/wt\n")
    return root


@pytest.fixture()
def worker_tree(tmp_path):
    root = tmp_path / "worker"
    (root / BRIEFS).mkdir(parents=True)
    old, new = root / BRIEFS / "eng-0.md", root / BRIEFS / "eng-1.md"
    old.write_text("old brief\n")
    new.write_text("new brief\n")
    os.utime(old, (time.time() - 600, time.time() - 600))
    (root / ".tickets").mkdir()
    (root / ".tickets" / f"{TICKET}.md").write_text(f"---\nid: {TICKET}\nstatus: in_progress\n---\n# planted\n")
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false"]
    env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
    subprocess.run([*git, "init", "-q"], cwd=root, env=env, check=True)
    subprocess.run([*git, "add", ".tickets"], cwd=root, env=env, check=True)
    subprocess.run([*git, "commit", "-q", "-m", "planted"], cwd=root, env=env, check=True)
    return root


# S1: orchestrator in the main tree and in a linked worktree


@pytest.mark.parametrize("trigger", ["auto", "manual"])
def test_the_orchestrator_in_the_main_tree_gets_one_read_first_line_naming_its_checkpoint(main_tree, trigger):
    done = _run(main_tree, "orchestrator", trigger=trigger)
    assert done.returncode == 0
    lines = _lines(done)
    assert len(lines) == 1, f"not exactly one stdout line: {done.stdout!r}"
    line = lines[0]
    assert line.startswith(INSTRUCTION) and "READ FIRST:" in line, line
    assert str(main_tree / ORCH) in line and "RESUME HERE" in line, line
    assert LEAD not in line


@pytest.mark.parametrize("trigger", ["auto", "manual"])
def test_the_orchestrator_in_a_linked_worktree_gets_the_leads_checkpoint(linked_tree, trigger):
    done = _run(linked_tree, "orchestrator", trigger=trigger)
    assert done.returncode == 0
    lines = _lines(done)
    assert len(lines) == 1, f"not exactly one stdout line: {done.stdout!r}"
    assert lines[0].startswith(INSTRUCTION) and "READ FIRST:" in lines[0]
    assert str(linked_tree / LEAD) in lines[0] and "RESUME HERE" in lines[0]
    assert ORCH not in lines[0]


def test_the_checkpoint_writing_is_unchanged_the_state_block_is_still_appended(main_tree):
    done = _run(main_tree, "orchestrator")
    assert done.returncode == 0
    text = (main_tree / ORCH).read_text()
    assert text.startswith(WRITTEN) and BEGIN in text


# S1: workers


@pytest.mark.parametrize("trigger", ["auto", "manual"])
def test_an_engineer_gets_its_brief_and_its_record_named(worker_tree, trigger):
    done = _run(worker_tree, "engineer", ticket=TICKET, trigger=trigger)
    assert done.returncode == 0
    lines = _lines(done)
    assert len(lines) == 1, f"not exactly one stdout line: {done.stdout!r}"
    line = lines[0]
    assert line.startswith(INSTRUCTION) and "READ FIRST: your brief and your record" in line, line
    assert str(worker_tree / BRIEFS / "eng-1.md") in line and "eng-0.md" not in line, line
    records = sorted((worker_tree / RECORDS / TICKET).iterdir())
    assert records, "the automatic record was not written"
    assert str(records[-1]) in line, line
    assert "RESUME HERE" not in line


def test_a_worker_without_a_brief_or_record_is_given_the_folders(tmp_path):
    root = tmp_path / "bare"
    root.mkdir()
    done = _run(root, "independent-test-designer")
    assert done.returncode == 0
    lines = _lines(done)
    assert len(lines) == 1, done.stdout
    assert "READ FIRST: your brief and your record" in lines[0]
    assert str(root / BRIEFS) in lines[0] and str(root / RECORDS) in lines[0]


# The error path: the systemMessage unchanged, the line still first


def test_a_missing_checkpoint_still_gives_the_line_first_then_the_system_message(tmp_path):
    root = tmp_path / "nocp"
    root.mkdir()
    done = _run(root, "orchestrator")
    assert done.returncode == 0
    lines = _lines(done)
    assert len(lines) == 2, done.stdout
    assert lines[0].startswith(INSTRUCTION) and str(root / ORCH) in lines[0]
    message = json.loads(lines[1])
    assert set(message) == {"systemMessage"}
    assert ORCH in message["systemMessage"] and message["systemMessage"].endswith("The compaction proceeds.")
    assert not (root / ORCH).exists()


def test_a_failed_record_write_still_gives_the_line(worker_tree):
    (worker_tree / RECORDS).write_text("a file where the folder should be\n")
    done = _run(worker_tree, "engineer", ticket=TICKET)
    assert done.returncode == 0
    lines = _lines(done)
    assert len(lines) == 2, done.stdout
    assert "READ FIRST: your brief and your record" in lines[0]
    assert "checkpoint not written" in json.loads(lines[1])["systemMessage"]


# F1


@pytest.mark.parametrize("case", ["main", "linked", "worker", "missing"])
def test_no_output_carries_a_decision_and_writes_stay_in_the_scratch(tmp_path, main_tree, linked_tree, worker_tree,
                                                                     case):
    root = {"main": main_tree, "linked": linked_tree, "worker": worker_tree, "missing": tmp_path}[case]
    role, ticket = ("engineer", TICKET) if case == "worker" else ("orchestrator", None)
    before = _snapshot(root)
    done = _run(root, role, ticket=ticket)
    assert done.returncode == 0
    _no_decision(done)
    after = _snapshot(root)
    changed = {path for path in set(before) | set(after) if before.get(path) != after.get(path)}
    outside = sorted(path for path in changed if not path.startswith(SCRATCH + "/"))
    assert not outside, f"written outside {SCRATCH}: {outside}"


def test_the_source_sets_and_reads_no_compaction_threshold():
    text = HOOK.read_text().lower()
    assert "claude_code_auto_compact_window" not in text and "autocompact" not in text


def _module():
    sys.path.insert(0, str(HOOKS))
    try:
        import precompact
    finally:
        sys.path.remove(str(HOOKS))
    return precompact


def test_the_names_sessionstart_imports_are_kept():
    precompact = _module()
    assert precompact.STAMP and callable(precompact.checkpoint_rel) and callable(precompact.split)


# R7: a file deleted between the listing and the stat


class _Gone:
    """A directory entry whose file was deleted after the listing: its stat raises."""

    def __init__(self, path):
        self.path = str(path)

    def is_file(self):
        return True

    def stat(self):
        raise FileNotFoundError(2, "No such file or directory", self.path)


def test_a_brief_deleted_before_its_stat_gives_the_next_newest(worker_tree, monkeypatch):
    precompact = _module()
    folder = worker_tree / BRIEFS
    real = os.scandir

    def listing(path):  # only the brief folder's listing is planted; os.scandir is global
        return [_Gone(folder / "gone.md"), *real(path)] if str(path) == str(folder) else real(path)

    monkeypatch.setattr(precompact.os, "scandir", listing)
    assert precompact.newest(str(folder)) == str(folder / "eng-1.md")


def test_when_every_brief_is_gone_the_folder_is_named_and_the_line_is_printed(tmp_path, monkeypatch, capsys):
    precompact = _module()
    folder = tmp_path / BRIEFS
    folder.mkdir(parents=True)
    real = os.scandir
    monkeypatch.setattr(precompact.os, "scandir", lambda path: [_Gone(folder / "a.md"), _Gone(folder / "b.md")]
                        if str(path) == str(folder) else real(path))
    assert precompact.newest(str(folder)) == str(folder)
    monkeypatch.setenv("GOV_ROLE", "engineer")
    monkeypatch.delenv("GOV_TICKET", raising=False)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    precompact.main()
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 1 and lines[0].startswith(INSTRUCTION), lines
    assert f"READ FIRST: your brief and your record, {folder} and " in lines[0], lines
