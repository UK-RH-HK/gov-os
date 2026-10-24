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
import w2_67_doctor


def test_missing_held_out_yaml_is_reported(tmp_path):
    """On a throwaway project where ``governance/project/held-out.yaml`` is absent, doctor reports it.

    Revised (W2-67, I4 F1; Rewrite-Reason: the assertion matches a key name that doctor always emits): the case
    reads doctor's ``held_out`` section, in ``result`` or ``error.details``: ``missing`` is true and its status is
    not a pass. Its throwaway project is a small committed one of its own, not a copy of the whole tree.
    """
    project = w2_67_doctor.small_project(tmp_path / "no-held-out" / "repo")
    sandbox = support.make_sandbox(tmp_path / "sandbox")

    held_out_path = project / support.HELD_OUT_REL
    assert not held_out_path.exists(), "the throwaway project should not have held-out.yaml"

    run = w2_67_doctor.doctor(project, sandbox)
    held_out = w2_67_doctor.section(run, "held_out")
    assert held_out.get("missing") is True, f"doctor does not report the missing held-out.yaml\n{run.describe()}"
    assert held_out.get("status") != "pass", f"a missing held-out.yaml is reported as a pass\n{run.describe()}"


def test_present_held_out_yaml_is_not_reported(tmp_path):
    """On a throwaway project where ``governance/project/held-out.yaml`` is present (even empty), doctor does not
    report it as missing.

    Revised (W2-67, I4 F1; Rewrite-Reason: the case read only ``result``, which is empty whenever doctor is
    unhealthy, so no check ran): the case reads doctor's ``held_out`` section wherever doctor put it.
    """
    project = w2_67_doctor.small_project(tmp_path / "has-held-out" / "repo")
    sandbox = support.make_sandbox(tmp_path / "sandbox")

    support.write_held_out(project, "")

    run = w2_67_doctor.doctor(project, sandbox)
    held_out = w2_67_doctor.section(run, "held_out")
    assert held_out.get("missing") is False, \
        f"doctor reports held-out.yaml as missing when it is present\n{run.describe()}"
    assert held_out.get("status") == "pass", f"a present held-out.yaml is not a pass\n{run.describe()}"
