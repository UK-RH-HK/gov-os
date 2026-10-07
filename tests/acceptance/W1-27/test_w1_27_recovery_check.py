"""KPI success 4: the recovery/rebuild family check is registered.

Registers the recovery/rebuild family check: derived state deleted and rebuilt
gives the same digest [CAP-38.b].
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

import w1_27_support as support


RECOVERY_REBUILD_CHECK_PATH = "template/governance/kernel/checks"
RECOVERY_REBUILD_FAMILY = "recovery/rebuild"
RECOVERY_REBUILD_FAMILY_NORMALISED = "recovery-rebuild"


# --------------------------------------------------------------------------
# Check declaration
# --------------------------------------------------------------------------

def test_recovery_rebuild_check_declaration_exists(project):
    """The recovery/rebuild check declaration YAML exists under ``template/governance/kernel/checks/``."""
    checks_dir = project / RECOVERY_REBUILD_CHECK_PATH
    found = list(checks_dir.glob("recovery-rebuild*"))
    assert found, f"no recovery-rebuild check declaration found under {RECOVERY_REBUILD_CHECK_PATH}/"


def test_recovery_rebuild_check_has_correct_family(project):
    """The check declaration's ``family`` normalises to ``recovery-rebuild`` (DEC-436)."""
    import re
    checks_dir = project / RECOVERY_REBUILD_CHECK_PATH
    found = list(checks_dir.glob("recovery-rebuild*"))
    assert found, "no declaration file"
    text = found[0].read_text(encoding="utf-8")
    family_match = re.search(r"^family:\s*(.+)$", text, re.MULTILINE)
    assert family_match, f"no family: line in {found[0].name}"
    raw = family_match.group(1).strip()
    normalised = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")
    assert normalised == RECOVERY_REBUILD_FAMILY_NORMALISED, \
        f"family {raw!r} normalises to {normalised!r}, not {RECOVERY_REBUILD_FAMILY_NORMALISED!r}"


def test_recovery_rebuild_check_has_id(project):
    """The check declaration has an ``id`` field."""
    import re
    checks_dir = project / RECOVERY_REBUILD_CHECK_PATH
    found = list(checks_dir.glob("recovery-rebuild*"))
    assert found, "no declaration file"
    text = found[0].read_text(encoding="utf-8")
    assert re.search(r"^id:\s*\S+", text, re.MULTILINE), f"no id: field in {found[0].name}"


def test_recovery_rebuild_check_is_listed(gov, project, interface):
    """``gov check --list --json`` includes the recovery/rebuild family."""
    run = gov("check", "--list", "--json")
    envelope = support.assert_envelope(run, interface, command="check")
    text = json.dumps(envelope).lower()
    assert RECOVERY_REBUILD_FAMILY_NORMALISED in text or RECOVERY_REBUILD_FAMILY.replace("/", "-") in text, \
        f"recovery-rebuild not listed in gov check --list\n{run.describe()}"


# --------------------------------------------------------------------------
# The actual check: delete and rebuild gives the same digest
# --------------------------------------------------------------------------

def test_derived_state_deleted_and_rebuilt_gives_same_digest(rebuild_gov, rebuild_project, interface):
    """Deleting all derived state and rebuilding gives the same digest as the first build (the check's scenario).

    Revised after implementation: rebuild goes through the lexical index's
    owner and its secrets filter (DEC-440); the fixture's size, not the
    behaviour, made it time out.
    """
    run1 = rebuild_gov("rebuild", "--json")
    env1 = support.assert_envelope(run1, interface, command="rebuild")
    assert env1["ok"] is True, f"first rebuild failed\n{run1.describe()}"
    digest1 = (env1.get("result") or {}).get("digest")
    assert digest1 is not None, f"first rebuild has no digest\n{run1.describe()}"

    runtime = rebuild_project / ".gov-runtime"
    if runtime.exists():
        shutil.rmtree(runtime)

    run2 = rebuild_gov("rebuild", "--json")
    env2 = support.assert_envelope(run2, interface, command="rebuild")
    assert env2["ok"] is True, f"second rebuild (after delete) failed\n{run2.describe()}"
    digest2 = (env2.get("result") or {}).get("digest")
    assert digest2 is not None, f"second rebuild has no digest\n{run2.describe()}"

    assert digest1 == digest2, (
        f"delete-and-rebuild digest {digest2} differs from original {digest1}\n"
        f"run 1:\n{run1.describe()}\nrun 2:\n{run2.describe()}"
    )
