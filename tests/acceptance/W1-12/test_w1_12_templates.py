"""KPI: proposal templates pass `openspec validate --strict` on first use. Failure KPI: a template fails it.

First use: a fresh change of the forked schema, made with `openspec new change` in a temporary project, in which
every artifact (proposal, specs, design, tasks, the readiness record) is its template, copied unchanged.
"""

from __future__ import annotations

import pytest

import w1_12_support as support

local_only = pytest.mark.local_only


def test_every_artifact_has_its_template_in_the_schema_folder(get):
    """OpenSpec reads a template only from the schema's `templates/` folder: each artifact's file is there."""
    artifacts = get(support.artifacts)
    for artifact in artifacts.values():
        path = get(lambda artifact=artifact: support.template_path(artifact))
        assert path.read_text(encoding="utf-8").strip(), f"{path.relative_to(support.REPO_ROOT)} is empty"


@local_only
def test_openspec_accepts_the_forked_schema(project):
    """`openspec schema validate feature-readiness` passes: structure, templates and dependency order."""
    report, done = project.json("schema", "validate", support.SCHEMA_NAME)
    assert done.returncode == 0 and report["valid"] is True, f"schema validate failed: {report.get('issues')}"


@local_only
def test_the_project_resolves_the_schema_and_its_templates(project):
    """The schema and every template come from the project, not from the user's folder or the package."""
    where, done = project.json("schema", "which", support.SCHEMA_NAME)
    assert done.returncode == 0 and where["source"] == "project", f"schema which: {where}"
    templates, done = project.json("templates", "--schema", support.SCHEMA_NAME)
    assert done.returncode == 0, done.stderr
    elsewhere = {name: entry["source"] for name, entry in templates.items() if entry["source"] != "project"}
    assert not elsewhere, f"templates not resolved from the project: {elsewhere}"
    wanted = [*support.BASE_ARTIFACTS, support.readiness_artifact()["id"]]
    assert not [name for name in wanted if name not in templates], f"templates listed: {sorted(templates)}"


@local_only
def test_a_fresh_change_from_the_templates_passes_validate_strict(project):
    """Success KPI: the change validates with exit 0 and no error or warning."""
    written = project.first_use("first-use", support.SCHEMA_NAME)
    assert support.readiness_artifact()["id"] in written
    code, valid, issues = project.validate_strict("first-use")
    assert (code, valid, issues) == (0, True, []), f"validate --strict on first use: exit {code}, {issues}"


@local_only
def test_validating_everything_in_the_fresh_project_passes(project):
    """Edge: `openspec validate --all --strict`, the form CI runs (DEC-087), also passes after first use."""
    project.first_use("first-use", support.SCHEMA_NAME)
    done = project.run("validate", "--all", "--strict", "--no-interactive")
    assert done.returncode == 0, f"validate --all --strict: exit {done.returncode}\n{done.stdout}\n{done.stderr}"


@local_only
def test_first_use_of_the_unforked_templates_fails_validate_strict(project):
    """Failure KPI, as a control: the same first use with the templates of `spec-driven` is refused.

    This is what the fork has to fix, and it shows the check above can fail.
    """
    project.first_use("stock-use", support.BASE_SCHEMA)
    code, valid, issues = project.validate_strict("stock-use")
    assert code != 0 and valid is False and issues, "the stock templates were expected to fail validate --strict"


@local_only
def test_a_template_that_breaks_the_delta_format_fails_validate_strict(project):
    """Failure KPI: a requirement left without a scenario is refused, so a broken template cannot pass."""
    written = project.first_use("broken-use", support.SCHEMA_NAME)
    spec = written["specs"]
    kept = [line for line in spec.read_text(encoding="utf-8").splitlines()
            if not line.lstrip().startswith(("#### ", "- **"))]
    spec.write_text("\n".join(kept) + "\n", encoding="utf-8")
    code, valid, issues = project.validate_strict("broken-use")
    assert code != 0 and valid is False and issues, "a delta without a scenario was expected to fail"
