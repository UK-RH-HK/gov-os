"""S1 and F1: the restore a failed stage or batch runs keeps every untracked file the tool did not write.

Interface item 1: "the restore a failed stage or batch runs (``project.restore``, called by ``project.commit`` and
``_batch``), not a new command. It deletes only paths the tool wrote and names in the call; every other untracked
path stays byte for byte; an untracked directory does not raise."

A stage starts on a clean tree, so the owner's untracked files that a restore can meet are the ones made while the
run is under way. A planted pre-commit hook (the owner's, not the tool's) writes them at one commit of the run: a
file, a file in a new directory, and a nested clone (an untracked directory git lists as such), and then refuses the
commit the case wants to fail. Ignored untracked files stand in the tree from the start.
"""

from __future__ import annotations

import w2_23_support as support


def test_s1_a_failed_stage_commit_keeps_the_owners_untracked_files_and_removes_its_record(project, box):
    """``project.commit``'s restore: stage A1's record commit is refused by the hook."""
    adoption = support.Adoption(project, box)
    adoption.ok("A0")
    before = support.head(project)
    rule = support.user_material_rule([support.RECORD["A1"]])
    support.install_hook(project, [{**rule, "refuse": True}])
    done = adoption.run("A1")
    support.refusal(done)  # the stage fails, as a refusal (an untracked directory does not raise)
    problems = support.user_material_problems(project)
    assert not problems, "the restore after the failed stage did not keep the owner's untracked files: " \
        + "; ".join(problems) + f"\n{done.describe()}"
    assert not (project / support.RECORD["A1"]).exists(), \
        f"the record the failed stage wrote ({support.RECORD['A1']}) was not removed\n{done.describe()}"
    assert support.head(project) == before, f"the failed stage moved HEAD\n{done.describe()}"
    assert support.staged(project) == [], f"the failed stage left something staged: {support.staged(project)}"


def test_s1_a_failed_move_batch_keeps_the_owners_untracked_files_and_removes_its_target(tmp_path, box):
    """``_batch``'s restore: batch 1 moves and commits (the owner's files appear then); batch 2's commit is refused.
    A move needs the code graph, so this case needs ``/tmp/gov-cbm-<uid>`` writable (README, known limit)."""
    project = support.plant_project(tmp_path / "harbour", code_intelligence=True)
    adoption = support.Adoption(project, box)
    adoption.through("A5", [support.entry(support.GUIDE, "MOVE", support.GUIDE_TARGET, batch=1),
                            support.entry(support.NOTES, "MOVE", support.NOTES_TARGET, batch=2)])
    support.install_hook(project, [support.user_material_rule([support.GUIDE_TARGET]),
                                   {"when": [support.NOTES_TARGET], "refuse": True}])
    done = adoption.run("A6")
    support.refusal(done)
    problems = support.user_material_problems(project)
    assert not problems, "the restore after the failed batch did not keep the owner's untracked files: " \
        + "; ".join(problems) + f"\n{done.describe()}"
    assert not (project / support.NOTES_TARGET).exists(), \
        f"the file the failed batch made ({support.NOTES_TARGET}) was not removed\n{done.describe()}"
    assert (project / support.NOTES).is_file(), f"{support.NOTES} is not back at its origin\n{done.describe()}"
    assert support.staged(project) == [], f"the failed batch left something staged: {support.staged(project)}"


def test_f1_instruction_and_untracked_files_survive_an_adoption_ending_in_a_rollback(project, box):
    """sha256 of the instruction files and of every untracked file, listed before; equal after a failed batch."""
    adoption = support.Adoption(project, box)
    paths = sorted(set(support.INSTRUCTION_FILES) | set(support.untracked_files(project)))
    assert set(support.IGNORED_FILES) <= set(paths), f"the planted ignored files are not untracked here: {paths}"
    before = support.listing(project, paths)
    before.update({rel: support.sha256(data) for rel, data in support.USER_MATERIAL.items()})  # made during the run
    adoption.through("A5", support.drops_proposal())
    support.install_hook(project, [{"when": [support.DROPS[0]], "write": support.USER_MATERIAL},
                                   {"when": [support.DROPS[1]], "refuse": True}])
    done = adoption.run("A6")
    support.refusal(done)
    after = support.listing(project, list(before))
    differ = {rel: (before[rel], after[rel]) for rel in before if before[rel] != after[rel]}
    assert not differ, "after the adoption and its rollback these files differ from the listing before (sha256 " \
        "before -> after, None where gone): " + "; ".join(f"{rel}: {old} -> {new}" for rel, (old, new) in
                                                          differ.items()) + f"\n{done.describe()}"
