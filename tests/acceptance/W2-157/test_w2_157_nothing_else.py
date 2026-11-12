"""S5 (it changes nothing else) and F4 (no change outside the ticket's paths).

S5's filesystem spy snapshots every file under the planted HOME and the planted project (path, size, mtime, bytes)
before and after a run, so any other write (the gate's own samples, a lock, a temporary file, the gate file itself, an
embedder log) shows.
"""

from __future__ import annotations

import fnmatch
import os
import re
import subprocess

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

def allowed_paths() -> list[str]:
    """The ticket's ``allowed_paths`` (the list in its front matter), without their comments."""
    lines = TICKET.read_text().splitlines()
    found = []
    for line in lines[lines.index("allowed_paths:") + 1:]:
        match = re.match(r"^- (\S+)", line)
        if not match:
            break
        found.append(match.group(1))
    return found


def test_f4_the_branch_changes_only_the_tickets_allowed_paths(tmp_path):
    """``git diff --name-only <merge-base with w2/integrate>...HEAD`` lists only paths matched by the ticket's
    ``allowed_paths`` or under ``tests/acceptance/W2-157/``. It is green only when the branch is clean: a change to
    any other path (a ticket file, another module, a test of another ticket) makes it fail, and it fails, naming the
    gap, where ``w2/integrate`` does not resolve."""
    env = {"PATH": support.SAFE_PATH, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null", "LC_ALL": "C",
           "HOME": str(tmp_path)}

    def git(*args):
        return subprocess.run(["git", "-C", str(ROOT), *args], env=env, capture_output=True, text=True, timeout=60)

    base = git("merge-base", "HEAD", "w2/integrate")
    assert base.returncode == 0 and base.stdout.strip(), f"w2/integrate does not resolve: {base.stderr}"
    diff = git("diff", "--name-only", f"{base.stdout.strip()}...HEAD")
    assert diff.returncode == 0, f"git diff failed: {diff.stderr}"
    patterns = allowed_paths()
    assert patterns, f"no allowed_paths read from {TICKET}"
    outside = [path for path in diff.stdout.splitlines()
               if not path.startswith(ACCEPTANCE) and not any(fnmatch.fnmatch(path, pattern) for pattern in patterns)]
    assert not outside, f"changed paths not matched by the ticket's allowed_paths {patterns}: {outside}"
