"""S2: a landing never waits for a close it does not conflict with; two record commits never collide (ticket DAEO-ifgf,
Interface item 2).

A running close is a planted ``/proc`` entry whose command line holds ``job_markers["close"]`` (``gov-close-stub``) and
the ticket arguments: a W2 id or a ticket id. ``gov.dispatch.landing.commit_records`` is driven in child processes
against a repository planted under ``tmp_path`` (the Interface states no return value, so none is pinned).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time

import pytest

import w2_121b_support as s
from w2_121b_support import HEAD_A

W7 = f"W2-7={HEAD_A}"


def setup_tickets(p) -> None:
    p.add_ticket(7)  # W2-7, ticket DAEO-a7: the landing's ticket
    p.add_ticket(8)  # W2-8, ticket DAEO-a8: another ticket (not in the landing)


def assert_blocked(p, why: str = "clos") -> None:
    run = p.tick()
    assert run.code == 0, run
    p.settle_none()
    assert p.land_runs() == [], "the landing went ahead although it must wait"
    assert p.land_file.exists() and p.claimed_files() == [], "a blocked landing is not claimed"
    lines = p.land_lines_in_status()
    assert lines, f"the reason is a `land:` line in status.txt\n{run}"
    assert any(re.search(why, l, re.I) for l in lines), f"the `land:` line should name the reason ({why}): {lines}"


def test_a_close_with_a_ticket_in_the_landing_blocks_it_while_it_runs_w2_id(landing):
    p = landing
    setup_tickets(p)
    pid = p.plant_close("--verbose", "W2-7")
    p.plant_land(W7)
    assert_blocked(p)
    p.remove_process(pid)
    assert p.claim_and_run(1)["argv"] == [W7], "the landing goes once the close is gone"


def test_a_close_with_a_ticket_in_the_landing_blocks_it_while_it_runs_ticket_id(landing):
    p = landing
    setup_tickets(p)
    pid = p.plant_close("DAEO-a7", "--verbose")  # the ticket id of W2-7 (from .tickets/)
    p.plant_land(W7)
    assert_blocked(p)
    p.remove_process(pid)
    assert p.claim_and_run(1)["argv"] == [W7]


@pytest.mark.parametrize("arguments", [["W2-8", "DAEO-a8"], ["W2-70"], ["W2-77", "--verbose"], []],
                         ids=["another-ticket", "w2-id-prefix-only", "w2-id-prefix-with-flag", "no-ticket-argument"])
def test_a_close_with_no_shared_ticket_does_not_block_the_landing(landing, arguments):
    p = landing
    setup_tickets(p)
    p.plant_close(*arguments)  # stays running through the landing
    p.plant_land(W7)
    batch = p.claim_and_run(1)
    assert batch["argv"] == [W7], batch["argv"]


def test_a_close_committing_its_records_blocks_while_the_index_lock_exists(landing):
    p = landing
    setup_tickets(p)
    p.plant_close("W2-8")  # shares no ticket with the landing
    lock = p.root / ".git" / "index.lock"
    lock.write_text("", encoding="utf-8")
    p.plant_land(W7)
    assert_blocked(p, why="clos|index|lock|record|commit")
    lock.unlink()  # the close is still running, but its commit is done
    assert p.claim_and_run(1)["argv"] == [W7]


def test_a_close_committing_its_records_blocks_while_the_changes_lie_under_close_record_paths(landing):
    p = landing
    setup_tickets(p)
    record = p.root / "docs" / "records" / "closes.md"
    record.parent.mkdir(parents=True)
    record.write_text("closes\n", encoding="utf-8")
    s.git(p.root, "add", "-A")
    s.git(p.root, "commit", "-q", "-m", "planted records")
    p.cfg(close_record_paths=["docs/records/"])
    p.plant_close("W2-8")  # shares no ticket with the landing
    record.write_text("closes\none more record, uncommitted\n", encoding="utf-8")
    p.plant_land(W7)
    assert_blocked(p, why="clos|record|commit")
    s.git(p.root, "add", "-A")
    s.git(p.root, "commit", "-q", "-m", "the close's records")  # committed: the close is still running
    assert p.claim_and_run(1)["argv"] == [W7]


# --- commit_records -----------------------------------------------------------------------------------------------------

SCRIPT = '''
import json, os, sys, time
root, go, out, paths_json, message, attempts, wait_s = sys.argv[1:8]
from gov.dispatch.landing import commit_records
while not os.path.exists(go):
    time.sleep(0.005)
open(out + ".started", "w").close()
t0 = time.monotonic()
try:
    for rel in json.loads(paths_json):
        commit_records(root, [rel], message + " " + rel, ["Task: DAEO-test"], attempts=int(attempts), wait_s=float(wait_s))
    result = {"ok": True}
except BaseException as error:
    result = {"ok": False, "error": repr(error)}
result["seconds"] = time.monotonic() - t0
with open(out, "w") as handle:
    handle.write(json.dumps(result))
'''


def records_repo(tmp_path, names):
    repo = tmp_path / "records-repo"
    repo.mkdir()
    s.git(repo, "init", "-q", "-b", "main")
    for name in names:
        (repo / name).parent.mkdir(parents=True, exist_ok=True)
        (repo / name).write_text(f"{name}\n", encoding="utf-8")
    s.git(repo, "add", "-A")
    s.git(repo, "commit", "-q", "-m", "planted records")
    for name in names:  # one modified tracked file per path to commit
        with open(repo / name, "a", encoding="utf-8") as handle:
            handle.write("a record\n")
    return repo


def env_for(tmp_path) -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "GOV_"))}
    home = tmp_path / "commit-home"
    home.mkdir(exist_ok=True)
    env.update(PYTHONPATH=str(s.SRC), PYTHONDONTWRITEBYTECODE="1", HOME=str(home), GIT_CONFIG_NOSYSTEM="1",
               GIT_CONFIG_GLOBAL=os.devnull, GIT_AUTHOR_NAME="planted", GIT_AUTHOR_EMAIL="planted@example.invalid",
               GIT_COMMITTER_NAME="planted", GIT_COMMITTER_EMAIL="planted@example.invalid")
    return env


def start_committer(tmp_path, repo, tag, paths, attempts, wait_s):
    script = tmp_path / "commit_records_run.py"
    script.write_text(SCRIPT, encoding="utf-8")
    out = tmp_path / f"result-{tag}.json"
    proc = subprocess.Popen([sys.executable, "-B", str(script), str(repo), str(tmp_path / "go"), str(out),
                             json.dumps(paths), f"record {tag}", str(attempts), str(wait_s)], cwd=tmp_path,
                            env=env_for(tmp_path), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return proc, out


def finish(proc, out, timeout=30.0) -> dict:
    stdout, stderr = proc.communicate(timeout=timeout)
    assert proc.returncode == 0 and out.exists(), f"commit_records run failed (exit {proc.returncode}):\n{stderr[-1500:]}"
    result = json.loads(out.read_text(encoding="utf-8"))
    assert result["ok"], f"commit_records raised: {result.get('error')}"
    return result


def count(repo) -> int:
    return int(s.git(repo, "rev-list", "--count", "HEAD"))


def committed_paths(repo) -> list[str]:
    return [l for l in s.git(repo, "log", "--name-only", "--format=").splitlines() if l.strip()]


def test_two_record_commits_at_the_same_time_both_land(tmp_path):
    repo = records_repo(tmp_path, ["one/a.md", "two/b.md"])
    before = count(repo)
    first, out1 = start_committer(tmp_path, repo, "one", ["one/a.md"], attempts=5, wait_s=0.3)
    second, out2 = start_committer(tmp_path, repo, "two", ["two/b.md"], attempts=5, wait_s=0.3)
    try:
        (tmp_path / "go").write_text("", encoding="utf-8")
        finish(first, out1)
        finish(second, out2)
    finally:
        for proc in (first, second):
            if proc.poll() is None:
                proc.kill()
    assert count(repo) == before + 2, "both record commits land, each as its own commit"
    landed = committed_paths(repo)
    assert "one/a.md" in landed and "two/b.md" in landed
    assert s.git(repo, "status", "--porcelain", "--untracked-files=no") == "", "a path was left uncommitted"
    assert not (repo / ".git" / "index.lock").exists()


def test_many_record_commits_at_once_all_land_none_is_lost(tmp_path):
    names = [f"{who}/r{n}.md" for who in ("one", "two") for n in range(4)]
    repo = records_repo(tmp_path, names)
    first, out1 = start_committer(tmp_path, repo, "one", [n for n in names if n.startswith("one/")], attempts=8, wait_s=0.2)
    second, out2 = start_committer(tmp_path, repo, "two", [n for n in names if n.startswith("two/")], attempts=8, wait_s=0.2)
    try:
        (tmp_path / "go").write_text("", encoding="utf-8")
        finish(first, out1)
        finish(second, out2)
    finally:
        for proc in (first, second):
            if proc.poll() is None:
                proc.kill()
    landed = set(committed_paths(repo))
    assert set(names) <= landed, f"never committed: {sorted(set(names) - landed)}"
    assert s.git(repo, "status", "--porcelain", "--untracked-files=no") == ""
    assert not (repo / ".git" / "index.lock").exists()


def test_a_record_commit_retries_while_another_holds_index_lock(tmp_path):
    repo = records_repo(tmp_path, ["one/a.md"])
    before = count(repo)
    lock = repo / ".git" / "index.lock"
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)  # another process holds the lock
    os.close(fd)
    (tmp_path / "go").write_text("", encoding="utf-8")
    proc, out = start_committer(tmp_path, repo, "retry", ["one/a.md"], attempts=6, wait_s=0.5)
    try:
        s.wait_for(lambda: (tmp_path / "result-retry.json.started").exists() or proc.poll() is not None, 20.0,
                   what="the committer to start")
        assert proc.poll() is None, "the committer ended before it tried (is gov.dispatch.landing importable?): " + proc.communicate()[1][-1500:]
        began = time.monotonic()
        time.sleep(0.5)
        assert proc.poll() is None, "commit_records gave up while the lock was held (it retries)"
        assert count(repo) == before and lock.exists(), "commit_records committed through (or removed) a lock another holds"
        time.sleep(max(0.0, 1.0 - (time.monotonic() - began)))
        lock.unlink()  # the other commit is done
        result = finish(proc, out)
    finally:
        if proc.poll() is None:
            proc.kill()
        if lock.exists():
            lock.unlink()
    assert result["seconds"] >= 0.8, f"it cannot have landed before the lock was released ({result['seconds']:.2f}s)"
    assert count(repo) == before + 1, "the retried commit lands"
    assert "one/a.md" in committed_paths(repo)
    assert s.git(repo, "status", "--porcelain", "--untracked-files=no") == ""
