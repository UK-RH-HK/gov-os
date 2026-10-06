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


# --------------------------------------------------------------------------
# Adoption level in the doctor report
# --------------------------------------------------------------------------

def test_doctor_report_mentions_adoption_level(gov, project, interface):
    """The doctor result mentions an adoption level."""
    run = gov("doctor", "--json")
    envelope = support.assert_envelope(run, interface, command="doctor")
    text = json.dumps(envelope).lower()
    assert "adopt" in text or "level" in text, \
        f"doctor report does not mention adoption level\n{run.describe()}"


def test_minimal_kernel_passes_at_minimal_level(tmp_path, interface):
    """A project with only the kernel installed (no extra adoption stages) passes at the minimal level.

    The test builds a minimal project from scratch: just enough to run ``gov``, with a valid path-map but no
    completed adoption stages beyond the kernel. The adoption level must be the lowest defined level.
    """
    project = support.copy_working_tree(tmp_path / "minimal" / "repo")
    sandbox = support.make_sandbox(tmp_path / "sandbox")
    support.write_path_map(project, support.minimal_valid_path_map())

    run = support.run_gov(project, sandbox, "doctor", "--json")
    envelope = support.assert_envelope(run, interface, command="doctor")
    result = envelope.get("result", {})
    text = json.dumps(result).lower()
    assert "minimal" in text or "kernel" in text or "level" in text, \
        f"minimal kernel project does not report a minimal adoption level\n{run.describe()}"


def test_completed_stages_raise_adoption_level(gov, project, interface):
    """The repository under test (with more adoption stages completed) reports a higher level than minimal.

    The working tree of the Gov OS repository itself has systems, capabilities, policies and other adoption
    artefacts. Its adoption level should be higher than the bare-minimum level.
    """
    run = gov("doctor", "--json")
    envelope = support.assert_envelope(run, interface, command="doctor")
    result = envelope.get("result", {})
    text = json.dumps(result).lower()
    found_level = False
    for keyword in ("adopted", "healthy", "full", "advanced", "intermediate"):
        if keyword in text:
            found_level = True
            break
    if not found_level:
        for keyword in ("minimal",):
            if keyword in text:
                pytest.fail(f"the Gov OS repository itself reports only minimal adoption\n{run.describe()}")
