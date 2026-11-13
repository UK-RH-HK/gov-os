"""S7: a move to a target that no namespace holds is refused before it runs.

Interface item 4: "A3 refuses ``ADOPT_TARGET_UNHELD``, naming each target no namespace holds, before its record is
written (tree unchanged); A6 refuses the same before any batch."

``vault/`` is held by no namespace of the planted path map. Moves need the code graph, so both cases need
``/tmp/gov-cbm-<uid>`` writable where the check comes after the code graph (README, known limit).
"""

from __future__ import annotations

import json

import yaml

import w2_23_support as support

UNHELD = ("vault/guide.md", "vault/archive/notes.txt")


def test_s7_a3_refuses_moves_to_unheld_targets_naming_each_before_its_record(tmp_path, box):
    project = support.plant_project(tmp_path / "harbour", code_intelligence=True)
    adoption = support.Adoption(project, box)
    adoption.through("A2")
    before, tree_before = support.head(project), support.git(project, "ls-files", "-s")
    done = adoption.run("A3", *adoption.map_argument([support.entry(support.GUIDE, "MOVE", UNHELD[0], batch=1),
                                                      support.entry(support.NOTES, "MOVE", UNHELD[1], batch=1)]))
    error = support.refusal(done, "ADOPT_TARGET_UNHELD")
    said = json.dumps(error)
    for target in UNHELD:
        assert target in said, f"the refusal does not name the unheld target {target}\n{done.describe()}"
    assert support.head(project) == before, f"A3 moved HEAD\n{done.describe()}"
    assert support.git(project, "ls-files", "-s") == tree_before, f"A3 changed the index\n{done.describe()}"
    assert support.porcelain(project) == "", f"A3 left the tree dirty:\n{support.porcelain(project)}"
    assert not (project / support.RECORD["A3"]).exists(), f"A3 wrote its record\n{done.describe()}"
    assert (project / support.GUIDE).is_file() and not (project / "vault").exists(), "a file was moved"


def test_s7_a6_refuses_a_target_the_path_map_no_longer_holds_before_any_batch(tmp_path, box):
    project = support.plant_project(tmp_path / "harbour", code_intelligence=True)
    adoption = support.Adoption(project, box)
    target = "modules/guide.md"
    adoption.through("A5", [support.entry(support.GUIDE, "MOVE", target, batch=1)])
    narrower = tuple(pattern for pattern in support.NAMESPACE_PATHS if pattern != "modules/**")
    support.write(project, support.PATH_MAP_REL, yaml.safe_dump(support.path_map(narrower, True), sort_keys=False))
    before = support.commit_all(project, "the path map no longer holds modules/")
    done = adoption.run("A6")
    error = support.refusal(done, "ADOPT_TARGET_UNHELD")
    assert target in json.dumps(error), f"the refusal does not name {target}\n{done.describe()}"
    assert support.head(project) == before, f"A6 committed something\n{done.describe()}"
    assert support.rollback_refs(project) == {}, f"A6 set rollback refs: a batch began\n{done.describe()}"
    assert (project / support.GUIDE).is_file() and not (project / target).exists(), f"a file moved\n{done.describe()}"
    assert support.porcelain(project) == "", f"A6 left the tree dirty:\n{support.porcelain(project)}"
