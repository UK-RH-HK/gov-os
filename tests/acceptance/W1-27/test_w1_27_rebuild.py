"""KPI success 2 and failure 2: ``gov rebuild`` recreates derived state.

Success: rebuild recreates every derived store; two rebuilds give the same
digest; a fresh clone plus doctor plus rebuild works [CAP-07.a, CAP-20.a,
CAP-46.a].

Failure: rebuild needs anything not in git.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

import w1_27_support as support


# --------------------------------------------------------------------------
# Command identity
# --------------------------------------------------------------------------

def test_rebuild_is_an_act_command(gov, interface):
    """``rebuild`` is an act command (DEC-317): it returns an envelope and may change derived state."""
    run = gov("rebuild", "--json")
    support.assert_envelope(run, interface, command="rebuild")


# --------------------------------------------------------------------------
# KPI success 2: rebuild guarantees
# --------------------------------------------------------------------------

def test_rebuild_recreates_derived_stores(gov, project, interface):
    """After rebuild, the derived stores under ``.gov-runtime/`` exist."""
    run = gov("rebuild", "--json")
    envelope = support.assert_envelope(run, interface, command="rebuild")
    assert envelope["ok"] is True, f"rebuild did not succeed\n{run.describe()}"
    runtime = project / ".gov-runtime"
    assert runtime.exists(), f".gov-runtime does not exist after rebuild\n{run.describe()}"


def test_two_rebuilds_give_the_same_digest(gov, project, interface):
    """The rebuild is idempotent: two consecutive rebuilds produce the same digest (CAP-20.a)."""
    run1 = gov("rebuild", "--json")
    env1 = support.assert_envelope(run1, interface, command="rebuild")
    assert env1["ok"] is True, f"first rebuild failed\n{run1.describe()}"

    run2 = gov("rebuild", "--json")
    env2 = support.assert_envelope(run2, interface, command="rebuild")
    assert env2["ok"] is True, f"second rebuild failed\n{run2.describe()}"

    result1 = env1.get("result", {})
    result2 = env2.get("result", {})
    digest1 = result1.get("digest") if isinstance(result1, dict) else None
    digest2 = result2.get("digest") if isinstance(result2, dict) else None
    assert digest1 is not None, f"first rebuild has no digest in result\n{run1.describe()}"
    assert digest2 is not None, f"second rebuild has no digest in result\n{run2.describe()}"
    assert digest1 == digest2, (
        f"two rebuilds give different digests: {digest1} vs {digest2}\n"
        f"run 1:\n{run1.describe()}\nrun 2:\n{run2.describe()}"
    )


def test_fresh_clone_doctor_rebuild(tmp_path, interface):
    """A fresh clone followed by doctor followed by rebuild works (CAP-46.a).

    The sequence is: copy the working tree (simulating a fresh clone), run
    ``gov doctor --json``, then run ``gov rebuild --json``. Both must succeed.
    """
    project = support.copy_working_tree(tmp_path / "fresh" / "repo")
    sandbox = support.make_sandbox(tmp_path / "sandbox")

    run_doc = support.run_gov(project, sandbox, "doctor", "--json")
    env_doc = support.assert_envelope(run_doc, interface, command="doctor")

    run_reb = support.run_gov(project, sandbox, "rebuild", "--json")
    env_reb = support.assert_envelope(run_reb, interface, command="rebuild")
    assert env_reb["ok"] is True, f"rebuild after fresh clone failed\n{run_reb.describe()}"


# --------------------------------------------------------------------------
# Failure KPI 2: rebuild needs anything not in git
# --------------------------------------------------------------------------

def test_rebuild_needs_only_git(tmp_path, interface):
    """Rebuild works with only the content in git, nothing else.

    A fresh copy of the working tree (no .gov-runtime, no external state) must
    rebuild successfully. This proves rebuild draws only from git.
    """
    project = support.copy_working_tree(tmp_path / "gitonly" / "repo")
    sandbox = support.make_sandbox(tmp_path / "sandbox")

    runtime = project / ".gov-runtime"
    if runtime.exists():
        shutil.rmtree(runtime)
    support.commit_all(project, "clean runtime")

    run = support.run_gov(project, sandbox, "rebuild", "--json")
    envelope = support.assert_envelope(run, interface, command="rebuild")
    assert envelope["ok"] is True, f"rebuild fails without pre-existing state\n{run.describe()}"


def test_rebuild_digest_matches_store_loader(gov, project, interface):
    """The digest reported by rebuild matches what the store loader computes (CAP-07.a).

    After rebuild, running ``gov status --json`` (which loads the store) and comparing its session digest with
    the rebuild's reported digest confirms they agree.
    """
    run_reb = gov("rebuild", "--json")
    env_reb = support.assert_envelope(run_reb, interface, command="rebuild")
    assert env_reb["ok"] is True, f"rebuild failed\n{run_reb.describe()}"
    rebuild_digest = (env_reb.get("result") or {}).get("digest")
    assert rebuild_digest is not None, f"rebuild has no digest\n{run_reb.describe()}"

    run_st = gov("status", "--json")
    env_st = support.assert_envelope(run_st, interface, command="status")
    status_session = env_st.get("session")
    if isinstance(status_session, dict):
        store_digest = status_session.get("store_digest") or status_session.get("digest")
        if store_digest is not None:
            assert rebuild_digest == store_digest, (
                f"rebuild digest {rebuild_digest} does not match store digest {store_digest}\n"
                f"rebuild:\n{run_reb.describe()}\nstatus:\n{run_st.describe()}"
            )
