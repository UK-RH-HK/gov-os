"""W2-59 KPI success 1 and its failure line: the pinned judge runs every declared check with its own interpreter and
its own installed package; the project supplies only data (DEC-822 item 3, DEC-835 item 1).

Failure line: "A check edited in the tree does not change the verdict of the pinned judge."

The judge is the stand-in pin, started through ``<HOME>/.local/bin/gov``. The project under check holds every
check declaration of this worktree's kernel (single named files), and, in the decoy run, a ``gov`` package of its
own under ``src/`` whose schema check is edited to give the opposite verdict. A ``python3`` and a ``gov`` that
leave markers come first on ``PATH``. The control run is the same project without the tree's package.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

import w2_59_support as support


@pytest.fixture(scope="module")
def judged(stand_in, tmp_path_factory):
    """The judge's answer in the decoy project and in the control project, each run once for the module."""
    answers = {}
    for name, with_tree in (("decoy", True), ("control", False)):
        base = tmp_path_factory.mktemp(f"judge-{name}")
        box = support.make_box(base / "box", stand_in, decoy_gov=True)
        files = support.tree_gov_files(box.markers) if with_tree else {"README.md": "w259 control\n"}
        project = support.make_repository(base / "project", files, support.declared_check_copies())
        done = support.judge_check(box, project, decoys_first=True)
        answers[name] = (box, project, done, support.check_results(done))
    return answers


def test_no_declared_check_imports_the_project_s_own_gov_package(judged):
    """Every declared check runs the judge's installed package: the ``gov`` under the project's ``src/`` is never
    imported (it would be with the project's ``src`` on the checks' import path)."""
    box, project, done, _ = judged["decoy"]
    imported = box.marks("tree-gov-")
    assert not imported, (
        f"{len(imported)} declared check process(es) imported the project's own {project}/src/gov instead of the "
        f"judge's installed package\n{done.describe()}")


def test_a_check_edited_in_the_tree_does_not_change_the_pinned_judge_s_verdict(judged):
    """The project's ``src/gov/check/schema.py`` is edited to report a finding; the judge's verdict for the schema
    check is the installed check's, the same as in the control project, and names no finding of the edited one."""
    _, _, done, results = judged["decoy"]
    _, _, control_done, control = judged["control"]
    assert "core-schema" in results and "core-schema" in control, (
        f"the schema check was not run\n{done.describe()}\n{control_done.describe()}")
    assert not any("No module named" in json.dumps(finding) for finding in control["core-schema"]["findings"]), (
        f"in the control project the judge's schema check could not import the judge's own package: "
        f"{control['core-schema']}\n{control_done.describe()}")
    assert support.TREE_EDIT_CODE not in support.finding_codes(results["core-schema"]), (
        f"the pinned judge's verdict came from the check as edited in the project's tree: {results['core-schema']}")
    assert results["core-schema"]["status"] == control["core-schema"]["status"], (
        f"the tree's edited check changed the pinned judge's verdict: {results['core-schema']['status']} in the "
        f"project with the edit, {control['core-schema']['status']} without it")


def test_a_declared_python3_command_does_not_run_the_python3_first_on_path(judged):
    """A declaration's ``python3`` names the check's interpreter: the judge's own, never the first on ``PATH``."""
    for name in ("decoy", "control"):
        box, _, done, _ = judged[name]
        used = box.marks("path-python3-")
        assert not used, (
            f"{len(used)} declared check(s) in the {name} project ran the python3 first on PATH "
            f"({box.decoy_bin / 'python3'})\n{done.describe()}")


def test_a_declared_gov_command_does_not_run_the_gov_first_on_path(judged):
    """A declaration that starts with ``gov`` (``fresh-agent-reconstruction``) runs the judge's own ``gov``: the
    ``gov`` first on ``PATH`` does not run and does not give the verdict."""
    _, _, _, control = judged["control"]
    for name in ("decoy", "control"):
        box, _, done, results = judged[name]
        assert not box.marks("path-gov-"), (
            f"the gov first on PATH ({box.decoy_bin / 'gov'}) ran for a declared check in the {name} project\n"
            f"{done.describe()}")
        entry = results.get("fresh-agent-reconstruction")
        assert entry is not None, f"the declared gov command was not run\n{done.describe()}"
        assert support.PATH_GOV_CODE not in support.finding_codes(entry), (
            f"the verdict of the declared gov command came from the gov first on PATH: {entry}")


@pytest.mark.parametrize("layout", sorted(support.KERNEL_LAYOUTS))
def test_a_declared_check_runs_with_the_judge_s_interpreter_package_and_no_project_pythonpath(
        layout, stand_in, tmp_path):
    """A probe declared in either kernel layout (DEC-579) reports the interpreter that ran it, the ``gov`` package
    it would import and its ``PYTHONPATH``: the judge's environment, the judge's installed package, and no
    ``PYTHONPATH`` entry naming the project (DEC-822 item 3: that variable chooses only the code under test)."""
    box = support.make_box(tmp_path / "box", stand_in, decoy_gov=True)
    out = tmp_path / "probe.json"
    code = ("import importlib.util, json, os, sys; spec = importlib.util.find_spec('gov'); "
            "d = {'prefix': sys.prefix, 'executable': sys.executable, "
            "'pythonpath': os.environ.get('PYTHONPATH', ''), 'gov': spec.origin if spec else None}; "
            f"open({str(out)!r}, 'w').write(json.dumps(d))")
    declaration = {"id": "w259-probe", "family": "schema/invariants", "tier": "G1", "severity": "warning",
                   "command": f'python3 -c "{code}"'}
    rel = f"{support.KERNEL_LAYOUTS[layout]}/checks/w259-probe.yaml"
    project = support.make_repository(tmp_path / "project", {rel: yaml.safe_dump(declaration, sort_keys=False),
                                                             **support.tree_gov_files(box.markers)})
    done = support.judge_check(box, project, decoys_first=True)
    assert out.is_file(), f"the declared probe did not run\n{done.describe()}"
    seen = json.loads(out.read_text(encoding="utf-8"))
    assert Path(seen["prefix"]).resolve() == stand_in.venv.resolve(), (
        f"the declared check ran with the interpreter of {seen['prefix']} ({seen['executable']}), not the judge's "
        f"environment {stand_in.venv}")
    project_paths = [entry for entry in seen["pythonpath"].split(":")
                     if entry and Path(entry).resolve().is_relative_to(project.resolve())]
    assert not project_paths, (
        f"the declared check's PYTHONPATH names the project under check: {seen['pythonpath']!r}")
    assert seen["gov"] and Path(seen["gov"]).resolve().is_relative_to(stand_in.site.resolve()), (
        f"the declared check would import gov from {seen['gov']}, not from the judge's installed package in "
        f"{stand_in.site}")


def test_a_gov_package_at_the_project_s_root_is_not_imported_by_the_checks(stand_in, tmp_path):
    """The project's root is the checks' working folder; a ``gov`` package there is project data like any other
    and is never imported by a declared check (a ``-m`` run puts its working folder first on the import path)."""
    box = support.make_box(tmp_path / "box", stand_in)
    copies = {rel: source for rel, source in support.declared_check_copies().items()
              if Path(rel).name in ("core-schema.yaml", "core-graph.yaml")}
    project = support.make_repository(tmp_path / "project", support.tree_gov_files(box.markers, prefix=""), copies)
    done = support.judge_check(box, project, decoys_first=False)
    results = support.check_results(done)
    imported = box.marks("root-gov-")
    assert not imported, (
        f"{len(imported)} declared check process(es) imported the gov package at the project's root "
        f"{project / 'gov'}\n{done.describe()}")
    assert support.TREE_EDIT_CODE not in support.finding_codes(results.get("core-schema", {})), (
        f"the schema check's verdict came from the project's root package: {results.get('core-schema')}")
