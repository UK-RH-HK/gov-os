"""KPI success 5: doctor reports an adoption level.

A repository with only the kernel installed passes at the minimal level, and
each completed adoption stage raises it toward ADOPTED_HEALTHY [CAP-54.a].
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

import w1_27_support as support
import w2_67_doctor


# --------------------------------------------------------------------------
# Adoption level in the doctor report
# --------------------------------------------------------------------------

def test_doctor_report_mentions_adoption_level(gov, project, interface):
    """The doctor result mentions an adoption level."""
    run = gov("doctor", "--json")
    support.assert_envelope(run, interface, command="doctor")
    # Revised (W2-67, I4 F1; Rewrite-Reason: the assertion matches a key name that doctor always emits): the
    # level's value is read; it is a defined level, and not ADOPTED_HEALTHY while another section is unmeasured.
    found = w2_67_doctor.sections(run)
    level = w2_67_doctor.section(run, "adoption_level").get("level")
    assert level in w2_67_doctor.LEVELS, f"the adoption level {level!r} is not a defined level\n{run.describe()}"
    unmeasured = sorted(name for name, value in found.items()
                        if name != "adoption_level" and isinstance(value, dict) and value.get("status") == "unmeasured")
    assert not (unmeasured and level == "ADOPTED_HEALTHY"), (
        f"ADOPTED_HEALTHY although {unmeasured} are unmeasured (DEC-425)\n{run.describe()}"
    )


def test_minimal_kernel_passes_at_minimal_level(tmp_path, interface):
    """A project with only the kernel installed (no extra adoption stages) passes at the minimal level.

    The test builds a minimal project from scratch: just enough to run ``gov``, with a valid path-map but no
    completed adoption stages beyond the kernel. The adoption level must be the lowest defined level.

    Revised after implementation: doctor verifies every registry entry under
    the session's home (DEC-452); the case built its healthy project from
    this repository's registry and so depended on the real machine.
    """
    project = support.copy_working_tree(tmp_path / "minimal" / "repo")
    sandbox = support.make_sandbox(tmp_path / "sandbox")

    tool_dir = tmp_path / "fake-tools" / "bin"
    tool_dir.mkdir(parents=True)
    _, sha = support.fake_tool(tool_dir, "minimal-tool", "1.0.0")
    registry = support.tool_entry_with_location_yaml(
        "minimal-tool", "1.0.0", sha, str(tool_dir),
    )
    support.write_tool_registry(project, registry)
    support.write_path_map(project, support.minimal_valid_path_map())

    run = support.run_gov(project, sandbox, "doctor", "--json")
    support.assert_envelope(run, interface, command="doctor")
    # Revised (W2-67, I4 F1; Rewrite-Reason: the assertion matches a key name that doctor always emits): the
    # adoption section, wherever doctor put it, passes at the lowest defined level.
    adoption = w2_67_doctor.section(run, "adoption_level")
    assert adoption.get("level") == w2_67_doctor.LEVELS[0], \
        f"minimal kernel project does not report the minimal adoption level\n{run.describe()}"
    assert adoption.get("status") == "pass", f"the minimal level does not pass\n{run.describe()}"


def test_completed_stages_raise_adoption_level(gov, project, interface, tmp_path):
    """The repository under test (with more adoption stages completed) reports a higher level than minimal.

    The working tree of the Gov OS repository itself has systems, capabilities, policies and other adoption
    artefacts. Its adoption level should be higher than the bare-minimum level.

    Revised after implementation: doctor verifies every registry entry under
    the session's home (DEC-452); the case built its healthy project from
    this repository's registry and so depended on the real machine.
    """
    tool_dir = tmp_path / "fake-tools" / "bin"
    tool_dir.mkdir(parents=True)
    _, sha = support.fake_tool(tool_dir, "adoption-tool", "1.0.0")
    registry = support.tool_entry_with_location_yaml(
        "adoption-tool", "1.0.0", sha, str(tool_dir),
    )
    support.write_tool_registry(project, registry)

    run = gov("doctor", "--json")
    support.assert_envelope(run, interface, command="doctor")
    # Revised (W2-67, I4 F1; Rewrite-Reason: the assertion matches a key name that doctor always emits): the
    # levels before and after the stages are compared. After: this repository's own path map. Before: the same
    # project with the stages taken out (a minimal path map, no system implemented, no capability enabled).
    after = w2_67_doctor.section(run, "adoption_level").get("level")
    support.write_path_map(project, support.minimal_valid_path_map())
    before_run = gov("doctor", "--json")
    support.assert_envelope(before_run, interface, command="doctor")
    before = w2_67_doctor.section(before_run, "adoption_level").get("level")
    assert after in w2_67_doctor.LEVELS and before in w2_67_doctor.LEVELS, \
        f"undefined levels: before {before!r}, after {after!r}\n{run.describe()}\n{before_run.describe()}"
    assert w2_67_doctor.LEVELS.index(after) > w2_67_doctor.LEVELS.index(before), (
        f"the completed stages do not raise the adoption level: before {before}, after {after}\n"
        f"{run.describe()}\n{before_run.describe()}"
    )
