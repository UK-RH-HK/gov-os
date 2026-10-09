"""The command, and stages A0, A1 and A2 [CAP-44.b].

Success line 1: "stages A0-A4, A5, A6 and A8 each write an evidence record: A0 clean tree and backup ref; A1
inventory; A2 classification; ...". Every case runs the tool on a project it built in its own temporary folder.
"""

from __future__ import annotations

import pytest

import w1_41_support as support


def _state(project):
    return {"tree": support.snapshot(project, skip=(".git",)), "git": support.git_state(project),
            "porcelain": support.porcelain(project)}


def _assert_untouched(project, before, run):
    after = _state(project)
    changed = support.snapshot_difference(before["tree"], after["tree"])
    assert not changed, f"the refusal wrote in the project: {changed}\n{run.describe()}"
    assert after["git"] == before["git"], f"the refusal moved HEAD or created a ref\n{run.describe()}"
    assert after["porcelain"] == before["porcelain"], run.describe()


# --------------------------------------------------------------------------
# The command line
# --------------------------------------------------------------------------

def test_adopt_without_lite_is_still_reserved(project, sandbox, interface):
    """DEC-090: Wave 1 delivers ``gov adopt --lite``; the full transaction with its verdict is Wave 3. ``gov adopt``
    alone stays what a reserved command that is not built answers, and writes nothing. (Green before
    implementation; it must stay green.)"""
    before = _state(project)
    run = support.run_gov(project, sandbox, "adopt", "--json")
    support.base.assert_error(run, interface, "NOT_IMPLEMENTED", exit_code=1, command="adopt")
    _assert_untouched(project, before, run)


def test_lite_without_a_stage_is_a_usage_error(project, sandbox):
    before = _state(project)
    run = support.run_gov(project, sandbox, "adopt", "--lite", "--json")
    assert run.returncode == 2, f"gov adopt --lite without --stage must end with exit code 2\n{run.describe()}"
    _assert_untouched(project, before, run)


def test_a_folder_that_is_no_git_repository_is_refused(tmp_path, sandbox, interface):
    """A0 needs a tree it can measure as clean and a ref it can create: without a repository it refuses."""
    folder = tmp_path / "loose"
    support.write(folder, "README.md", "# No repository here\n")
    run = support.Adoption(folder, sandbox, interface).run("A0")
    support.assert_refused(run, interface)
    assert sorted(path.name for path in folder.iterdir()) == ["README.md"], \
        f"the refusal wrote in the folder\n{run.describe()}"


# --------------------------------------------------------------------------
# A0: clean tree and backup ref
# --------------------------------------------------------------------------

def test_a0_records_the_clean_tree_and_a_backup_ref(adoption, project):
    baseline = support.head(project)
    refs_before = support.git_state(project)["refs"]
    stage = adoption.ok("A0")
    front = stage.front
    assert front.get("baseline_commit") == baseline, \
        f"{stage.record}: baseline_commit is not the commit the stage found ({baseline})"
    ref = front.get("backup_ref")
    assert isinstance(ref, str) and ref.startswith("refs/"), f"{stage.record}: backup_ref is not a full ref name"
    assert support.resolve(project, ref) == baseline, \
        f"the backup ref {ref} does not resolve to the baseline commit {baseline}"
    assert ref not in refs_before, "the backup ref existed before the stage"
    assert stage.result.get("backup_ref") == ref, "the result and the record name different backup refs"


def _untracked(project):
    support.write(project, "scratch.txt", "left behind\n")
    return "scratch.txt"


def _modified(project):
    support.write(project, support.GUIDE, "# Guide\n\nEdited and not committed.\n")
    return support.GUIDE


def _staged(project):
    support.write(project, "docs/new.md", "# New\n")
    support.git(project, "add", "docs/new.md")
    return "docs/new.md"


@pytest.mark.parametrize("dirty", [_untracked, _modified, _staged], ids=["untracked", "modified", "staged"])
def test_a0_refuses_a_dirty_tree_and_writes_nothing(adoption, project, interface, dirty):
    """"A0 clean tree": a dirty tree is refused, the dirty path is named, and nothing is written beyond the
    refusal: no record, no ref, no commit."""
    rel = dirty(project)
    before = _state(project)
    run = adoption.run("A0")
    support.assert_refused(run, interface, rel)
    _assert_untouched(project, before, run)


# --------------------------------------------------------------------------
# A1: inventory
# --------------------------------------------------------------------------

def test_a1_inventory_lists_every_tracked_artefact(adoption, project):
    baseline = set(support.tree(project))
    adoption.through("A1")
    stage = adoption.stages["A1"]
    listed = set(support.entries_by_path(stage.front, stage.record))
    missing = sorted(baseline - listed)
    assert not missing, f"{stage.record}: the inventory leaves out tracked artefacts: {missing}"
    invented = sorted(listed - set(support.tree(project)))
    assert not invented, f"{stage.record}: the inventory lists paths the project does not track: {invented}"


# --------------------------------------------------------------------------
# A2: classification
# --------------------------------------------------------------------------

def test_a2_classifies_every_inventoried_artefact(adoption, project):
    """Every artefact of the inventory has an entry in the classification, with the namespace of the project's
    path map that holds it; nothing is unknown in this project."""
    baseline = set(support.tree(project))
    adoption.through("A2")
    stage = adoption.stages["A2"]
    entries = support.entries_by_path(stage.front, stage.record)
    missing = sorted(baseline - set(entries))
    assert not missing, f"{stage.record}: artefacts without a classification: {missing}"
    unnamed = sorted(rel for rel in baseline if entries[rel].get("namespace") != "harbour")
    assert not unnamed, f"{stage.record}: artefacts not classified by their namespace 'harbour': {unnamed}"
    assert stage.front.get("unknown") == [], f"{stage.record}: 'unknown' is not an empty list in a classified project"


def test_a_project_without_a_path_map_is_not_classified(tmp_path, adopt_in, interface):
    """DEC-449: what could not be established is not a clean answer. Without a path map no artefact's class is
    known; the tool refuses by A2 at the latest, and no record says that nothing is unknown."""
    project = support.build_project(tmp_path / "unmapped", path_map_file=False)
    adoption = adopt_in(project)
    for stage in ("A0", "A1", "A2"):
        run = adoption.run(stage)
        assert not support.not_built(run), f"gov adopt --lite is not built\n{run.describe()}"
        if run.returncode != 0:
            support.assert_refused(run, interface, any_of=("path-map", "path map"))
            return
    pytest.fail("stages A0 to A2 all succeeded in a project that has no path map: nothing there is classified")


# --------------------------------------------------------------------------
# One record per stage; a stage stands on the one before it
# --------------------------------------------------------------------------

def test_stages_a0_to_a4_each_leave_their_own_evidence_record(adoption):
    adoption.through("A4", support.legacy_proposal())
    records = [adoption.stages[stage].record for stage in ("A0", "A1", "A2", "A3", "A4")]
    assert len(set(records)) == 5, f"the five stages did not leave five records: {records}"
    ids = [adoption.stages[stage].front["id"] for stage in ("A0", "A1", "A2", "A3", "A4")]
    assert len(set(ids)) == 5, f"the five records do not have five ids: {ids}"


@pytest.mark.parametrize("stage", ["A1", "A2", "A3", "A4", "A6", "A8"])
def test_a_stage_without_the_record_of_the_stage_before_it_refuses(adoption, project, interface, stage):
    """CAP-44: a staged transaction. On a project where no stage has run, a later stage refuses and writes
    nothing."""
    before = _state(project)
    extra = adoption.map_argument(support.legacy_proposal()) if stage == "A3" else ()
    run = adoption.run(stage, *extra)
    support.assert_refused(run, interface)
    _assert_untouched(project, before, run)
