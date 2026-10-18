"""Behaviour already met in this worktree (DEC-718), held here so that the ticket does not lose it. Green today.

- **W2-M056**: a change to the readiness taxonomy without a linked CIT-E record fails the W1-26 check family
  (DEC-309). Re-checked through ``gov check --json``: the ``core-claims`` check reports ``TAXONOMY_CHANGE_NO_CITE``
  and a linked CIT-E clears it. The project holds that one check's declaration, copied by name.
- **CAP-33.a**: the kernel states the two record types, CIT-P and CIT-E.
"""

from __future__ import annotations

import json

import pytest

import w2_37_support as support

DECLARATION = "core-claims.yaml"     # the declaration that holds the taxonomy rule today (re-checked, DEC-718)


def taxonomy_project(root, linked):
    project = support.Project(root)
    project.write(".gitignore", ".gov-runtime/\n")
    project.write("README.md", "# A project\n")
    project.write(support.DIMENSIONS_REL, (support.REPO_ROOT / support.DIMENSIONS_REL).read_text(encoding="utf-8"))
    project.write(f"template/governance/kernel/checks/{DECLARATION}",
                  (support.CHECKS / DECLARATION).read_text(encoding="utf-8"))
    project.commit("start")
    text = (project.root / support.DIMENSIONS_REL).read_text(encoding="utf-8")
    project.write(support.DIMENSIONS_REL,
                  text.replace("capability_types:", "capability_types:\n  new_type:\n    extra_rows_for_standard: []", 1))
    if linked:
        project.write("docs/changes/CIT-E-001.md", support.rec("CIT-E-001", support.CITE_TYPE, status="APPLIED",
                                                               state_class="EVIDENCE", target=support.DIMENSIONS_REL))
    project.commit("extend the taxonomy")
    return project.root


def findings_naming(run, rel):
    document = support.envelope(run, command="check")
    found = document.get("result") or (document.get("error") or {}).get("details") or {}
    return [(check.get("id"), check.get("status"), finding) for check in found.get("checks", [])
            for finding in check.get("findings", []) if rel in json.dumps(finding)]


@pytest.mark.parametrize("linked", [False, True], ids=["without-cit-e", "with-linked-cit-e"])
def test_regression_a_taxonomy_change_without_a_linked_cit_e_fails_a_check(box, tmp_path, linked):
    root = taxonomy_project(tmp_path / "repo", linked)
    run = support.gov(box, "check", "--json", "--root", str(root), path=box.full)
    named = findings_naming(run, support.DIMENSIONS_REL)
    if linked:
        assert named == [], f"a taxonomy change with a linked CIT-E is still flagged: {named}\n{run.describe()}"
    else:
        assert any(status == "RED" for _, status, _ in named) and run.returncode != 0, \
            f"a taxonomy change without a CIT-E is not flagged red: {named}\n{run.describe()}"


@pytest.mark.parametrize("type_name", [support.CITP_TYPE, support.CITE_TYPE])
def test_regression_the_kernel_states_both_change_record_types(type_name):
    schema = json.loads((support.SCHEMAS / f"{type_name}.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["type"]["const"] == type_name
