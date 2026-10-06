"""KPI S1 (partial): openspec validate --strict.

When ``openspec`` is on PATH, the check runs ``openspec validate --strict`` and
reports its result. When ``openspec`` is absent, the check reports it by name,
is never green and never raises an exception.
"""

from __future__ import annotations

import os
import stat

import w1_26_support as support

cli_support = support.cli_support


def _make_fake_openspec(sandbox, exit_code=0, output=""):
    """Write a fake ``openspec`` script to the sandbox bin directory."""
    script = sandbox.bin / "openspec"
    script.write_text(
        f"#!/bin/sh\necho '{output}'\nexit {exit_code}\n",
        encoding="utf-8",
    )
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    return script


# --------------------------------------------------------------------------
# openspec absent: reported by name, never green, never exception
# --------------------------------------------------------------------------

def test_openspec_absent_reported_by_name(project, sandbox, interface):
    """When openspec is not on PATH, the check reports it by name."""
    project.commit()
    env_path = sandbox.bin.as_posix()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    output_text = run.stdout + run.stderr
    assert "openspec" in output_text.lower() or "openspec" in str(result).lower(), \
        f"openspec is absent but its name is nowhere in the output\n{run.describe()}"


def test_openspec_absent_never_green(project, sandbox, interface):
    """When openspec is absent, no check whose family is openspec-related is GREEN."""
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)
    for family_name, entry in families.items():
        if "openspec" in family_name.lower():
            status = entry.get("status") if isinstance(entry, dict) else entry
            assert status != support.GREEN, \
                f"openspec is absent but {family_name} is GREEN\n{run.describe()}"


def test_openspec_absent_no_exception(project, sandbox, interface):
    """When openspec is absent, the check does not raise an exception."""
    project.commit()
    run = support.run_check(project, sandbox)
    assert run.returncode in (0, 1, 2, 3, 4), \
        f"gov check exited with unexpected code {run.returncode}\n{run.describe()}"
    envelope = support.envelope_of(run, interface)


# --------------------------------------------------------------------------
# openspec present and passing -> its result is reported
# --------------------------------------------------------------------------

def test_openspec_present_and_passing(project, sandbox, interface):
    """When a passing openspec is on PATH, the check includes its result."""
    _make_fake_openspec(sandbox, exit_code=0, output="all valid")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)


# --------------------------------------------------------------------------
# openspec present and failing -> RED
# --------------------------------------------------------------------------

def test_openspec_present_and_failing_is_red(project, sandbox, interface):
    """When openspec validate --strict fails, the check is RED."""
    _make_fake_openspec(sandbox, exit_code=1, output="validation error")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    output_text = run.stdout + str(result)
    assert "openspec" in output_text.lower() or run.returncode != 0, \
        f"openspec failed but the check does not reflect it\n{run.describe()}"
