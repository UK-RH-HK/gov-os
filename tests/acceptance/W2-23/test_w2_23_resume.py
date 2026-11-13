"""S4: a failed or interrupted batch leaves a resumable record and no half-staged state.

Interface item 2: "running ``gov adopt --lite --stage A6`` again resumes. A failed batch commits the A6 record with
``status: failed``, ``failed_batch: <n>``, the batches done with their commits and dispositions, and per-run rollback
refs (``refs/gov/adoption/rollback/<run-id>/batch-<n>``); refusal code stays ``ADOPT_BATCH_FAILED``. A killed batch
(moves staged, no commit): the next A6 run finds the staged set equal to a recorded in-progress batch, unstages it to
its rollback point and continues there; anything else staged is refused naming the paths (never reset)."

The plan is three batches, each one DELETE_FROM_ACTIVE_TREE (no move, so no code graph is needed). The failure is a
planted pre-commit hook that refuses batch 3's commit. The kill is the same hook sending SIGKILL to the process that
runs the stage (git's parent) at batch 2's commit: the batch is staged and not committed, exactly between its steps.
"""

from __future__ import annotations

import json

import w2_23_support as support

A6 = support.RECORD["A6"]


def _record_at_head(project, done):
    data = support.at_head(project, A6)
    assert data is not None, f"no A6 record ({A6}) is committed after the failed batch\n{done.describe()}"
    return support.frontmatter(data.decode("utf-8"), A6)


def test_s4_a_batch_failing_at_its_third_step_commits_a_record_and_the_stage_resumes_there(project, box):
    adoption = support.Adoption(project, box)
    adoption.through("A5", support.drops_proposal())
    support.install_hook(project, [{"when": [support.DROPS[2]], "refuse": True}])
    done = adoption.run("A6")
    support.refusal(done, "ADOPT_BATCH_FAILED")

    record = _record_at_head(project, done)
    assert record.get("status") == "failed", f"{A6}: status is {record.get('status')!r}, not 'failed'"
    assert record.get("failed_batch") == 3, f"{A6}: failed_batch is {record.get('failed_batch')!r}, not 3"
    batches = {item.get("batch"): item for item in record.get("batches") or [] if isinstance(item, dict)}
    for number in (1, 2):
        item = batches.get(number)
        assert item, f"{A6} does not name batch {number}, which was done: {record.get('batches')}"
        commit = item.get("commit")
        assert isinstance(commit, str) and support.git(project, "cat-file", "-t", commit, check=False).strip() \
            == "commit", f"{A6}: batch {number} names no commit ({commit!r})"
        listed = {artefact.get("path"): artefact for artefact in item.get("artefacts") or []}
        artefact = listed.get(support.DROPS[number - 1])
        assert artefact and isinstance(artefact.get("disposition"), str) and artefact["disposition"].strip(), \
            f"{A6}: batch {number} gives no disposition for {support.DROPS[number - 1]}: {item}"
    assert support.staged(project) == [], f"something is left staged: {support.staged(project)}"
    assert support.porcelain(project) == "", f"the tree is not clean:\n{support.porcelain(project)}"

    refs = support.rollback_refs(project)
    named = {support.ROLLBACK_REF.match(ref).groups(): sha for ref, sha in refs.items()
             if support.ROLLBACK_REF.match(ref)}
    runs = {run for run, _ in named}
    assert len(runs) == 1 and {number for _, number in named} >= {"1", "2"}, \
        f"the rollback refs are not one run's refs/gov/adoption/rollback/<run-id>/batch-<n> for batches 1 and 2: " \
        f"{sorted(refs)}"
    first_refs = dict(refs)
    assert (project / support.DROPS[2]).is_file() and support.at_head(project, support.DROPS[2]) is not None, \
        f"{support.DROPS[2]} (batch 3's) is not back in the tree"

    support.remove_hook(project)
    resumed = adoption.run("A6")
    support.succeeded(resumed)
    for rel in support.DROPS:
        assert support.at_head(project, rel) is None, f"{rel} is still in HEAD after the resumed stage\n" \
            f"{resumed.describe()}"
    for rel in support.DROPS[:2]:
        assert len(support.commits_deleting(project, rel)) == 1, \
            f"{rel} was removed by {len(support.commits_deleting(project, rel))} commits: the resumed stage did " \
            f"not continue at batch 3\n{resumed.describe()}"
    later = support.rollback_refs(project)
    assert all(later.get(ref) == sha for ref, sha in first_refs.items()), \
        f"the resumed run reused or moved the first run's rollback refs: {first_refs} -> {later}"
    assert support.staged(project) == [] and support.porcelain(project) == "", \
        f"the resumed stage left the tree dirty:\n{support.porcelain(project)}"


def _kill_at_batch_two(project, box, adoption):
    marker = box.elsewhere / "killed.pid"
    support.install_hook(project, [{"when": [support.DROPS[1]], "kill": str(marker), "refuse": True}])
    done = adoption.run("A6")
    assert marker.is_file(), f"the planted kill did not happen (no commit hook ran at batch 2)\n{done.describe()}"
    assert done.returncode == -9, f"the stage was not killed (exit {done.returncode})\n{done.describe()}"
    support.remove_hook(project)
    assert support.staged(project), "the kill left nothing staged: the planted state is not a killed batch"
    return done


def test_s4_a_batch_killed_between_its_steps_is_unstaged_and_the_stage_continues_there(project, box):
    adoption = support.Adoption(project, box)
    adoption.through("A5", support.drops_proposal())
    _kill_at_batch_two(project, box, adoption)
    resumed = adoption.run("A6")
    support.succeeded(resumed)
    for rel in support.DROPS:
        assert support.at_head(project, rel) is None, f"{rel} is still in HEAD after the resumed stage\n" \
            f"{resumed.describe()}"
    for rel in support.DROPS[:2]:
        assert len(support.commits_deleting(project, rel)) == 1, \
            f"{rel} was removed by {len(support.commits_deleting(project, rel))} commits\n{resumed.describe()}"
    assert support.staged(project) == [] and support.porcelain(project) == "", \
        f"the resumed stage left the tree dirty:\n{support.porcelain(project)}"


def test_s4_after_a_killed_batch_anything_else_staged_is_refused_by_name_and_left_as_it_is(project, box):
    adoption = support.Adoption(project, box)
    adoption.through("A5", support.drops_proposal())
    _kill_at_batch_two(project, box, adoption)
    support.write(project, "README.md", "# Harbour\n\nThe owner's own change, staged.\n")
    support.git(project, "add", "--", "README.md")
    index_before, head_before = support.git(project, "write-tree").strip(), support.head(project)
    done = adoption.run("A6")
    error = support.refusal(done)
    assert "README.md" in json.dumps(error), f"the refusal does not name README.md\n{done.describe()}"
    assert support.git(project, "write-tree").strip() == index_before, \
        f"what was staged was changed (reset or unstaged)\n{done.describe()}"
    assert support.head(project) == head_before, f"HEAD moved\n{done.describe()}"
