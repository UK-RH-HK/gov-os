"""KPI S4 (CAP-30.e, DEC-309): CIT-E taxonomy change check.

Fails a change to the capability taxonomy or to ``readiness-dimensions.yaml``
that has no linked CIT-E record.
"""

from __future__ import annotations

import shutil

import w1_26_support as support


DIMENSIONS_REL = support.READINESS_DIMENSIONS_REL


# --------------------------------------------------------------------------
# readiness-dimensions.yaml changed without a linked CIT-E -> RED
# --------------------------------------------------------------------------

def test_dimensions_changed_without_cite_is_red(project, sandbox, interface):
    """Changing readiness-dimensions.yaml without a linked CIT-E record fails."""
    project.add_readiness_dimensions()
    project.commit("add dimensions")
    dims_path = project.root / DIMENSIONS_REL
    text = dims_path.read_text(encoding="utf-8")
    dims_path.write_text(text + "\n# An unlinked change.\n", encoding="utf-8")
    project.commit("change dimensions without CIT-E")
    run = support.run_check(project, sandbox)
    support.assert_red(run, interface)


def test_dimensions_changed_with_cite_passes(project, sandbox, interface):
    """Changing readiness-dimensions.yaml with a linked CIT-E record passes."""
    project.add_readiness_dimensions()
    project.commit("add dimensions")
    dims_path = project.root / DIMENSIONS_REL
    text = dims_path.read_text(encoding="utf-8")
    dims_path.write_text(text + "\n# A governed change.\n", encoding="utf-8")
    project.add_record("docs/changes/CIT-E-001.md", "CIT-E-001",
                        "change-execution-record", "APPLIED",
                        target=DIMENSIONS_REL)
    project.commit("change dimensions with CIT-E")
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)
    for family_name, entry in families.items():
        if "taxonomy" in str(entry).lower() or "CIT-E" in str(entry):
            status = entry.get("status") if isinstance(entry, dict) else entry
            assert status != support.RED, \
                f"CIT-E-linked change still fails {family_name}\n{run.describe()}"


# --------------------------------------------------------------------------
# Capability taxonomy changed without CIT-E -> RED
# --------------------------------------------------------------------------

def test_taxonomy_field_changed_without_cite_is_red(project, sandbox, interface):
    """Adding a new capability type to the taxonomy without a CIT-E record fails."""
    project.add_readiness_dimensions()
    project.commit("add dimensions")
    dims_path = project.root / DIMENSIONS_REL
    text = dims_path.read_text(encoding="utf-8")
    text = text.replace("capability_types:", "capability_types:\n  new_type:\n    extra_rows_for_standard: []")
    dims_path.write_text(text, encoding="utf-8")
    project.commit("extend taxonomy without CIT-E")
    run = support.run_check(project, sandbox)
    support.assert_red(run, interface)


# --------------------------------------------------------------------------
# No change to dimensions -> no finding
# --------------------------------------------------------------------------

def test_no_change_to_dimensions_no_finding(project, sandbox, interface):
    """When readiness-dimensions.yaml is unchanged, no taxonomy finding is raised."""
    project.add_readiness_dimensions()
    project.commit("add dimensions")
    project.write("unrelated.txt", "no taxonomy change\n")
    project.commit("unrelated change")
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)
    for family_name, entry in families.items():
        if "taxonomy" in str(entry).lower() or "CIT-E" in str(entry):
            status = entry.get("status") if isinstance(entry, dict) else entry
            assert status != support.RED, \
                f"no taxonomy change but {family_name} is RED\n{run.describe()}"
