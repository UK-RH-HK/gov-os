"""S3: a project's change to a shipped file is kept and reported, never silently overwritten."""

from __future__ import annotations

import subprocess

import w2_17_support as support


def _lists(updated):
    run = updated.run
    assert run.returncode == 0, f"`gov update {support.B} --json` did not exit 0\n{run.describe()}"
    return support.outcome_lists(run.result().get("files"))


def test_a_clean_three_way_merge_holds_both_changes(updated):
    lists = _lists(updated)
    data = (updated.project / support.MERGED).read_bytes()
    assert data == support.MERGED_RESULT.encode(), (
        f"{support.MERGED}, changed by the project (line 2) and by release B (line 12), does not hold both changes:\n"
        f"{data.decode('utf-8', 'replace')}")
    assert support.MERGED in lists["merged"], f"{support.MERGED} is not reported merged: {lists}"


def test_a_conflicting_change_keeps_the_projects_file_and_writes_release_b_copy_aside(updated, source):
    lists = _lists(updated)
    project = updated.project
    assert (project / support.CONFLICT).read_bytes() == updated.before_bytes[support.CONFLICT], (
        f"{support.CONFLICT}, changed by both in the same line, does not keep the project's bytes")
    aside = project / support.RELEASE_COPY_DIR / support.CONFLICT
    assert aside.is_file() and aside.read_bytes() == source.template_bytes(support.TAG_B, support.CONFLICT), (
        f"release B's copy of {support.CONFLICT} is not written to {support.RELEASE_COPY_DIR}/{support.CONFLICT}")
    assert support.CONFLICT in lists["conflicts"], f"{support.CONFLICT} is not named under conflicts: {lists}"


def test_no_file_the_update_wrote_holds_a_conflict_marker(updated):
    _lists(updated)
    project = updated.project
    before = updated.before["head"]
    written = subprocess.run(["git", "-C", str(project), "diff", "--name-only", "--diff-filter=AM", before, "HEAD"],
                             capture_output=True, text=True, check=True).stdout.split()
    assert support.MERGED in written, f"fixture reading: the update commit does not change {support.MERGED}: {written}"
    marked = [rel for rel in written if support.CONFLICT_MARKER in (project / rel).read_bytes()]
    assert not marked, f"files the update wrote hold a conflict marker (<<<<<<<): {marked}"
