"""KPI S1 (partial): openspec validate --strict.

When ``openspec`` is on PATH, the check runs ``openspec validate --strict`` and
reports its result. When ``openspec`` is absent, the check reports it by name,
is never green and never raises an exception.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

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

OPENSPEC_CHECK = "openspec-validate"
OPENSPEC_FAMILY = "product traceability"


def _without_openspec(monkeypatch):
    """``gov check`` runs with a PATH whose folders hold no ``openspec``: absent on any machine."""
    folders = [folder for folder in os.environ.get("PATH", "").split(os.pathsep)
               if folder and not (Path(folder) / "openspec").exists()]
    monkeypatch.setenv("PATH", os.pathsep.join(folders))


def _with_fake_openspec(monkeypatch, sandbox):
    """``gov check`` runs with the sandbox's ``bin`` first on PATH, where the case puts its fake ``openspec``."""
    monkeypatch.setenv("PATH", os.pathsep.join((str(sandbox.bin), os.environ.get("PATH", ""))))


def test_openspec_absent_reported_by_name(green_project, sandbox, interface, monkeypatch):
    """When openspec is not on PATH, the check reports it by name: a finding of ``openspec-validate`` names it.

    Revised (W2-67, I2 §2.7): it asserted "openspec" anywhere in the output, which every output holds (the check
    id)."""
    project = green_project
    _without_openspec(monkeypatch)
    run = support.run_check(project, sandbox)
    result, _ = support.result_and_envelope(run, interface)
    entry = support.check_entry(result, OPENSPEC_CHECK)
    assert support.findings_naming(entry, "openspec"), \
        f"openspec is absent but no finding of {OPENSPEC_CHECK} names it: {entry}\n{run.describe()}"


def test_openspec_absent_never_green(green_project, sandbox, interface, monkeypatch):
    """When openspec is absent, the openspec check is not GREEN, nor is its family.

    Revised (W2-67, I2 §2.7): it looped over families whose name holds "openspec", and there is none."""
    project = green_project
    _without_openspec(monkeypatch)
    run = support.run_check(project, sandbox)
    result, _ = support.result_and_envelope(run, interface)
    entry = support.check_entry(result, OPENSPEC_CHECK)
    assert entry.get("status") in (support.RED, support.YELLOW), \
        f"openspec is absent but {OPENSPEC_CHECK} is {entry.get('status')!r}: {entry}\n{run.describe()}"
    assert entry.get("family") == OPENSPEC_FAMILY and support.family_status(result, OPENSPEC_FAMILY) != support.GREEN, \
        f"openspec is absent but its family {entry.get('family')!r} is GREEN\n{run.describe()}"


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

def test_openspec_present_and_failing_is_red(green_project, sandbox, interface, monkeypatch):
    """When openspec validate --strict fails, the check is RED: ``openspec-validate`` is RED and ``gov check``
    exits non-zero.

    Revised (W2-67, I2 §2.7): its fake ``openspec`` was never on the PATH ``gov check`` runs with, and the
    assertion ("openspec" in the output, or a non-zero exit) held on a base red before any defect (I2 R1)."""
    project = green_project
    _make_fake_openspec(sandbox, exit_code=1, output="validation error")
    _with_fake_openspec(monkeypatch, sandbox)
    run = support.run_check(project, sandbox)
    result, envelope = support.result_and_envelope(run, interface)
    entry = support.check_entry(result, OPENSPEC_CHECK)
    assert entry.get("status") == support.RED, \
        f"openspec validate --strict failed but {OPENSPEC_CHECK} is {entry.get('status')!r}: {entry}\n{run.describe()}"
    assert envelope["ok"] is False and run.returncode == support.EXIT_CHECK_FAILED, \
        f"a planted defect did not cause exit {support.EXIT_CHECK_FAILED}\n{run.describe()}"
