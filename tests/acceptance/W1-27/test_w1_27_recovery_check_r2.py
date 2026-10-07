"""Round 2, KPI success 4: the recovery/rebuild family check detects mismatches.

The check command (``template/governance/kernel/checks/recovery-rebuild.yaml``)
must compare the store digest before and after a delete-and-rebuild cycle.
It must exit non-zero when the digests differ, and report unmeasured when
there is nothing to rebuild (DEC-425).  It must never write to the project
(W1-26's rule: the check uses a throwaway copy).

Predecessor analysis
--------------------
The first round's ``test_w1_27_recovery_check.py`` has five cases:
- ``test_recovery_rebuild_check_declaration_exists``
- ``test_recovery_rebuild_check_has_correct_family``
- ``test_recovery_rebuild_check_has_id``
- ``test_recovery_rebuild_check_is_listed``
- ``test_derived_state_deleted_and_rebuilt_gives_same_digest``

The first four verify the declaration metadata; they cannot detect a
fail-open command.  The fifth tests **gov rebuild** idempotency, not
the **check** command's ability to find a mismatch.  The predecessor's
cases were **weak**: they verified the registration but never ran the
check command to confirm it can fail.
"""

from __future__ import annotations

import os
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

import w1_27_support as support


def _check_command_text(project):
    """The ``command:`` value of the recovery-rebuild check declaration."""
    checks_dir = Path(project) / support.CHECKS_REL
    found = list(checks_dir.glob("recovery-rebuild*"))
    assert found, "no recovery-rebuild check declaration"
    text = found[0].read_text(encoding="utf-8")
    match = re.search(r"^command:\s*(.+)$", text, re.MULTILINE)
    assert match, f"no command: line in {found[0].name}"
    return match.group(1).strip()


def _run_check_command(project, sandbox, code_root=None):
    """Run the recovery-rebuild check command in *project* via ``sh -c``.

    When *code_root* is given, PYTHONPATH points to its ``src/`` instead
    of the project's — the same split ``run_gov_with_code`` uses — and
    the check declaration is read from *code_root* (where the template
    lives) rather than from *project*.
    """
    cmd = _check_command_text(code_root or project)
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(sandbox.home),
        "TMPDIR": str(sandbox.tmpdir),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(Path(code_root or project) / "src"),
        "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
    }
    return subprocess.run(
        ["sh", "-c", cmd], cwd=str(project), env=env,
        capture_output=True, text=True, timeout=30,
    )


# --------------------------------------------------------------------------- #
# The check command must not unconditionally exit 0
# --------------------------------------------------------------------------- #

def test_recovery_rebuild_command_not_unconditionally_exit_zero(project):
    """The check command must not unconditionally exit 0 (CAP-38.b).

    A command that computes one digest and calls ``exit(0)`` without
    comparing two values is a fail-open: it cannot detect a mismatch
    between the current store and a clean rebuild.
    """
    cmd = _check_command_text(project)
    has_unconditional_zero = "exit(0)" in cmd and "!=" not in cmd and "==" not in cmd and " if " not in cmd
    assert not has_unconditional_zero, (
        f"the check command unconditionally exits 0, making it a fail-open:\n{cmd}"
    )


# --------------------------------------------------------------------------- #
# The check must detect a tampered store
# --------------------------------------------------------------------------- #

def test_recovery_rebuild_command_exits_nonzero_on_tampered_store(cli, rebuild_gov, rebuild_project, sandbox, interface):
    """After tampering with store.db, the check must exit non-zero.

    A correct implementation deletes derived state (in a throwaway copy),
    rebuilds, and compares digests.  A tampered store has a different
    digest from a clean rebuild.

    Revised after implementation: rebuild goes through the lexical index's
    owner and its secrets filter (DEC-440); the fixture's size, not the
    behaviour, made it time out.
    """
    run = rebuild_gov("rebuild", "--json")
    support.assert_envelope(run, interface, command="rebuild")
    assert run.returncode == 0, f"rebuild failed\n{run.describe()}"

    store_path = rebuild_project / ".gov-runtime" / "store.db"
    assert store_path.is_file(), "store.db does not exist after rebuild"
    conn = sqlite3.connect(str(store_path))
    conn.execute(
        "INSERT INTO records VALUES "
        "('__tampered__.md', 'TAMPERED', 'test', 'active')"
    )
    conn.commit()
    conn.close()

    result = _run_check_command(rebuild_project, sandbox, code_root=cli)

    assert result.returncode != 0, (
        f"the recovery-rebuild check exits 0 on a tampered store — "
        f"it does not detect a digest mismatch\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


# --------------------------------------------------------------------------- #
# Unmeasured when no store exists
# --------------------------------------------------------------------------- #

def test_recovery_rebuild_check_reports_unmeasured_when_no_store(project, sandbox):
    """When no derived state exists, the check must report unmeasured cleanly (DEC-425).

    It must not crash with a Python traceback, and it must not exit 0
    (green).
    """
    store = project / ".gov-runtime" / "store.db"
    if store.exists():
        store.unlink()

    result = _run_check_command(project, sandbox)

    assert "Traceback" not in result.stderr, (
        f"the recovery-rebuild check crashes instead of reporting "
        f"unmeasured when no store exists (DEC-425):\n{result.stderr}"
    )
    assert result.returncode != 0, (
        f"the check exits 0 (green) when there is no store — "
        f"should be unmeasured, never green (DEC-425)\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
