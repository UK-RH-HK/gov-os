"""S5 (it changes nothing else) and F4 (no change outside the ticket's paths, judged on W2-157's own branch only).

S5's filesystem spy snapshots every file under the planted HOME and the planted project (path, size, mtime, bytes)
before and after a run, so any other write (the gate's own samples, a lock, a temporary file, the gate file itself, an
embedder log) shows.
"""

from __future__ import annotations

import fnmatch
import os
import re
import subprocess
from pathlib import Path

import pytest

import w2_157_support as support
from w2_157_support import ROOT, TOTAL_MIB, model

TICKET = ROOT / ".tickets" / "DAEO-ozyt.md"
ACCEPTANCE = "tests/acceptance/W2-157/"
INBOX_FOLDERS = (".gov-runtime", ".gov-runtime/dispatch", ".gov-runtime/dispatch/inbox")


def spy_difference(machine, before: dict, folders_before: set) -> tuple[set, set, set]:
    """(new files, changed files, new folders) under the planted HOME and project since the snapshots."""
    after = machine.snapshot(machine.home, machine.project)
    new = set(after) - set(before)
    changed = {path for path, value in before.items() if after.get(path) != value}
    folders = machine.folders(machine.home, machine.project) - folders_before
    return new, changed, folders


def test_s5_a_run_with_no_trip_writes_only_its_own_log(machine):
    """Two stand-in servers (answering ``/api/ps``, with planted logs), a quiet GPU, a job that ends first: of every file
    under the planted HOME and project only ``$HOME/.gov-os/machine/gpu-backstop.log`` is new, nothing changed (the gate
    file byte for byte, the servers' logs), no folder is new, the servers got only ``GET /api/ps``, and nvidia-smi was
    asked only L3's form."""
    first = machine.add_embedder(models=[model("a", size=1000)], log_text="load_tensors: offloaded 33/33 layers to GPU\n")
    second = machine.add_embedder(models=[model("b", size=1000)], log_text="")
    machine.plant_smi([(1000, TOTAL_MIB)])
    job = machine.start_job()
    machine.write_gate()
    before = machine.snapshot(machine.home, machine.project)
    folders_before = machine.folders(machine.home, machine.project)
    watch = machine.start_watch([job.pgid], plant=False)
    outcome = machine.watch_quietly(watch, job, polls=4)
    result = outcome.result()
    assert result["tripped"] is False and result["inbox_item"] is None, outcome.text()

    new, changed, folders = spy_difference(machine, before, folders_before)
    assert new == {str(machine.log_file)}, f"files written other than the log: {sorted(new - {str(machine.log_file)})}"
    assert not changed, f"files changed: {sorted(changed)}"
    assert not folders, f"folders made: {sorted(folders)}"
    assert machine.log_file.read_text().strip(), "the log is empty"
    for embedder in (first, second):
        assert embedder.requests and set(embedder.requests) == {("GET", "/api/ps")}, (
            f"a server was asked something else than GET /api/ps: {embedder.requests}")
    assert machine.smi_argvs() and all(argv == support.SMI_ARGV for argv in machine.smi_argvs()), machine.smi_argvs()


def test_s5_a_trip_writes_only_its_log_and_the_one_inbox_item(machine):
    """A trip: the new files are the log and the one inbox item (and the inbox folder and its parents, which were
    absent); nothing existing changed, the gate file included."""
    machine.add_embedder(models=[model("a", size=1000)], log_text="")
    machine.plant_smi([(15900, TOTAL_MIB)])
    job = machine.start_job()
    machine.write_gate()
    before = machine.snapshot(machine.home, machine.project)
    folders_before = machine.folders(machine.home, machine.project)
    outcome = machine.finish(machine.start_watch([job.pgid], plant=False))
    result = outcome.result()
    assert result["tripped"] is True and result["inbox_item"], outcome.text()

    new, changed, folders = spy_difference(machine, before, folders_before)
    others = [path for path in new if path != str(machine.log_file)]
    assert str(machine.log_file) in new and len(others) == 1, f"files written: {sorted(new)}"
    assert support.same_path(others[0], result["inbox_item"]), f"the new file {others[0]} is not the inbox item"
    assert not changed, f"files changed: {sorted(changed)}"
    allowed = {str(machine.project / folder) for folder in INBOX_FOLDERS}
    assert folders <= allowed, f"folders made other than the inbox's: {sorted(folders - allowed)}"
    assert job.stopped()


# --- F4 ---------------------------------------------------------------------------------------------------------------
# Judged only on W2-157's own branch (``w2/W2-157``): there, ``git diff --name-only <base>...HEAD`` (the base being the
# branch's merge-base with ``w2/integrate``) lists only paths matched by the ticket's ``allowed_paths`` or under
# ``tests/acceptance/W2-157/``. On any other checkout the case is SKIPPED with its reason, never red: another ticket's
# branch (its own paths are not W2-157's), the merge queue's candidate merge (a detached HEAD), ``w2/integrate`` itself,
# a clone's checkout. Also skipped, with the reason, where ``w2/integrate`` does not resolve or the ticket file is absent
# (a plain clone). The branch is read from the repository named (``git symbolic-ref -q HEAD``), never from the current
# directory or an environment variable. Revision of W2-181 (DAEO-ywb5), the form of W2-180's revision of W2-170's F5.
OWN_BRANCH = "w2/W2-157"
TICKET_NAME = "DAEO-ozyt.md"


def allowed_paths(ticket: Path = TICKET) -> list[str]:
    """The ticket's ``allowed_paths`` (the list in its front matter), without their comments."""
    lines = ticket.read_text().splitlines()
    found = []
    for line in lines[lines.index("allowed_paths:") + 1:]:
        match = re.match(r"^- (\S+)", line)
        if not match:
            break
        found.append(match.group(1))
    return found


def judge_f4_paths(root: Path) -> None:
    """Judge ``root``'s checkout: skip (with the reason) unless HEAD is the branch ``w2/W2-157``; there, assert that every
    path changed against the merge-base with ``w2/integrate`` is allowed by W2-157's ticket or is in its test folder."""
    root = Path(root)
    env = {"PATH": support.SAFE_PATH, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null", "LC_ALL": "C",
           "HOME": "/nonexistent"}

    def git(*args):
        return subprocess.run(["git", "-C", str(root), *args], env=env, capture_output=True, text=True, timeout=60)

    ticket = root / ".tickets" / TICKET_NAME
    if git("rev-parse", "--verify", "--quiet", "w2/integrate^{commit}").returncode != 0:
        pytest.skip("F4 needs the w2/integrate reference, absent in this repository: not judged here")
    if not ticket.is_file():
        pytest.skip(f"F4 needs the ticket file .tickets/{TICKET_NAME}, absent here: not judged here")
    head = git("symbolic-ref", "-q", "HEAD")
    ref = head.stdout.strip() if head.returncode == 0 else ""
    if not ref.startswith("refs/heads/"):
        pytest.skip(f"F4 judges only the branch {OWN_BRANCH}; this is a detached HEAD: not judged here")
    branch = ref.removeprefix("refs/heads/")
    if branch != OWN_BRANCH:
        pytest.skip(f"F4 judges only the branch {OWN_BRANCH}; this is the branch {branch}: not judged here")
    base = git("merge-base", "HEAD", "w2/integrate")
    assert base.returncode == 0 and base.stdout.strip(), f"w2/integrate does not resolve: {base.stderr}"
    diff = git("diff", "--name-only", f"{base.stdout.strip()}...HEAD")
    assert diff.returncode == 0, f"git diff failed: {diff.stderr}"
    patterns = allowed_paths(ticket)
    assert patterns, f"no allowed_paths read from {ticket}"
    outside = [path for path in diff.stdout.splitlines()
               if not path.startswith(ACCEPTANCE) and not any(fnmatch.fnmatch(path, pattern) for pattern in patterns)]
    assert not outside, f"changed paths not matched by the ticket's allowed_paths {patterns}: {outside}"


def test_f4_the_branch_changes_only_the_tickets_allowed_paths():
    """On ``w2/W2-157``: ``git diff --name-only <merge-base with w2/integrate>...HEAD`` lists only paths matched by the
    ticket's ``allowed_paths`` or under ``tests/acceptance/W2-157/``; a change to any other path makes it fail. On any
    other branch, a detached HEAD, or without ``w2/integrate`` or the ticket file, it is skipped with its reason."""
    judge_f4_paths(ROOT)


# -- the planted cases: each in its own repository under tmp_path, judged by the same function ----------------------
OUTSIDE = "src/gov/resources/slots.py"        # not W2-157's (W2-121c's own module)
INSIDE = "src/gov/resources/backstop.py"      # W2-157's own module


def _plant(tmp_path: Path, *, branch: str, path: str, detach_merge: bool = False) -> Path:
    """A ``git init`` repository: ``w2/integrate`` holds a base commit and W2-157's ticket file (copied from this tree);
    ``branch`` (``w2/integrate`` itself, or a branch off it) holds one more commit adding ``path``. With
    ``detach_merge``: the branch is made, then HEAD is detached at ``w2/integrate`` and ``branch`` merged with
    ``--no-ff`` (the merge queue's candidate merge). Nothing of the true home's git config is read."""
    if not TICKET.is_file():
        pytest.skip(f"the planted cases copy the ticket file .tickets/{TICKET_NAME}, absent here: not judged here")
    home = tmp_path / "home"
    home.mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    env = {"PATH": support.SAFE_PATH, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null", "LC_ALL": "C",
           "HOME": str(home)}
    ident = ["-c", "user.name=Planted", "-c", "user.email=planted@example.invalid", "-c", "commit.gpgsign=false",
             "-c", "core.hooksPath=/dev/null"]

    def git(*args):
        done = subprocess.run(["git", "-C", str(repo), *ident, *args], env=env, capture_output=True, text=True,
                              timeout=60)
        assert done.returncode == 0, f"planting failed: git {' '.join(args)}: {done.stderr}"

    git("init", "-q")
    git("checkout", "-q", "-b", "w2/integrate")
    (repo / ".tickets").mkdir()
    (repo / ".tickets" / TICKET_NAME).write_text(TICKET.read_text(encoding="utf-8"), encoding="utf-8")
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    if branch != "w2/integrate":
        git("checkout", "-q", "-b", branch)
    (repo / path).parent.mkdir(parents=True, exist_ok=True)
    (repo / path).write_text("changed\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", f"adds {path}")
    if detach_merge:
        git("checkout", "-q", "--detach", "w2/integrate")
        git("merge", "-q", "--no-ff", "-m", "candidate merge", branch)
    return repo


def _skipped(repo: Path) -> str:
    with pytest.raises(pytest.skip.Exception) as info:
        judge_f4_paths(repo)
    return info.value.msg


def test_f4_the_planted_paths_are_outside_and_inside_the_ticket_s_paths():
    patterns = allowed_paths()
    assert not any(fnmatch.fnmatch(OUTSIDE, pattern) for pattern in patterns) and not OUTSIDE.startswith(ACCEPTANCE), (
        OUTSIDE, patterns)
    assert any(fnmatch.fnmatch(INSIDE, pattern) for pattern in patterns), (INSIDE, patterns)


def test_f4_planted_w2_157_branch_with_a_change_outside_its_paths_fails(tmp_path):
    repo = _plant(tmp_path, branch="w2/W2-157", path=OUTSIDE)
    with pytest.raises(AssertionError) as info:
        judge_f4_paths(repo)
    assert OUTSIDE in str(info.value)


def test_f4_planted_w2_157_branch_with_a_change_inside_its_paths_passes(tmp_path):
    repo = _plant(tmp_path, branch="w2/W2-157", path=INSIDE)
    judge_f4_paths(repo)


def test_f4_planted_other_ticket_branch_with_the_same_change_is_skipped_with_its_reason(tmp_path):
    repo = _plant(tmp_path, branch="w2/W2-121c", path=OUTSIDE)
    reason = _skipped(repo)
    assert "w2/W2-121c" in reason, reason


def test_f4_planted_candidate_merge_on_a_detached_head_is_skipped_with_its_reason(tmp_path):
    repo = _plant(tmp_path, branch="w2/W2-121c", path=OUTSIDE, detach_merge=True)
    head = subprocess.run(["git", "-C", str(repo), "symbolic-ref", "-q", "HEAD"], capture_output=True, text=True)
    assert head.returncode != 0, "the planted candidate merge must stand on a detached HEAD"
    merged = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%p"], capture_output=True, text=True)
    assert len(merged.stdout.split()) == 2, "the planted candidate merge must be a merge commit"
    reason = _skipped(repo)
    assert "detached HEAD" in reason, reason


def test_f4_planted_integrate_branch_itself_is_skipped_with_its_reason(tmp_path):
    repo = _plant(tmp_path, branch="w2/integrate", path=OUTSIDE)
    reason = _skipped(repo)
    assert "this is the branch w2/integrate" in reason, reason
