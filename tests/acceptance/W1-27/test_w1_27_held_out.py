"""KPI success 7: doctor reports a missing ``governance/project/held-out.yaml``.

One KPI line: doctor reports that the project's held-out file is missing. That
is an existence check and nothing else: the code never opens, reads, hashes,
copies or prints that file, and no worker, test or lead reads, prints, searches,
diffs or copies it in this repository or in any copy of it, or displays the
settings file's deny line for it. Tests show the line on a throwaway project in
a temporary directory (file absent: reported; an empty file present: not
reported). Put this paragraph word for word in every worker's brief.

DEC-223: a missing ``held-out.yaml`` means no held-out rule.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import w1_27_support as support


def test_missing_held_out_yaml_is_reported(tmp_path, interface):
    """On a throwaway project where ``governance/project/held-out.yaml`` is absent, doctor reports it.

    The copy_working_tree helper already omits the held-out file (DEC-385), so the file is absent by default.
    """
    project = support.copy_working_tree(tmp_path / "no-held-out" / "repo")
    sandbox = support.make_sandbox(tmp_path / "sandbox")

    held_out_path = project / support.HELD_OUT_REL
    assert not held_out_path.exists(), "the throwaway project should not have held-out.yaml"

    run = support.run_gov(project, sandbox, "doctor", "--json")
    envelope = support.assert_envelope(run, interface, command="doctor")
    text = json.dumps(envelope).lower()
    assert "held" in text or "held-out" in text.replace("_", "-") or "held_out" in text, \
        f"doctor does not mention the missing held-out.yaml\n{run.describe()}"


def test_present_held_out_yaml_is_not_reported(tmp_path, interface):
    """On a throwaway project where ``governance/project/held-out.yaml`` is present (even empty), doctor does not
    report it as missing.
    """
    project = support.copy_working_tree(tmp_path / "has-held-out" / "repo")
    sandbox = support.make_sandbox(tmp_path / "sandbox")

    support.write_held_out(project, "")

    run = support.run_gov(project, sandbox, "doctor", "--json")
    envelope = support.assert_envelope(run, interface, command="doctor")
    text = json.dumps(envelope).lower()

    if "held" in text or "held_out" in text:
        result = envelope.get("result", {})
        if isinstance(result, dict):
            for key, value in result.items():
                if "held" in key.lower() or "held_out" in key.lower():
                    if isinstance(value, dict) and value.get("missing") is True:
                        pytest.fail(f"doctor reports held-out.yaml as missing when it is present\n{run.describe()}")
                    if isinstance(value, str) and "missing" in value.lower():
                        pytest.fail(f"doctor reports held-out.yaml as missing when it is present\n{run.describe()}")
