"""Round 3, KPI success 1 & 5: doctor must distinguish unmeasured-absence
from unmeasured-error, and adoption level must respect it.

The current ``src/gov/doctor/command.py`` has
``healthy = all(s.get("status") not in ("fail", "drift"))``.
A section that returns ``"status": "unmeasured"`` because its measurement
*raised an error* (e.g. "canary runner failed", "cannot check index
freshness") is not a failure under this logic, so doctor exits 0 and says
``healthy: true`` even though a measurement failed.

What is decided (DEC-416, DEC-425):

- A section whose measurement **raised an error** or whose input exists
  and cannot be read is a **failure**, with the error named.
- A section whose component is **not installed** (no tool registry, no
  hook config, no index yet) stays "unmeasured" with its reason, does
  not make the project unhealthy, and adoption never says
  ADOPTED_HEALTHY for a project with an unmeasured section.

Section-by-section classification of unmeasured states
------------------------------------------------------
1.  tools: "no tool-registry.yaml" → absence (OK)
2.  hooks: no ``lefthook.yml`` → absence (OK)
3.  path_map: "no path-map.yaml" → absence (OK)
4.  path_compliance: no unmeasured state
5.  index_freshness: exception in ``freshness()`` → **ERROR → fail**;
    status "missing"/"empty" → absence (OK)
6.  canaries: exception in ``run_canaries()`` → **ERROR → fail**;
    "no canary results" → absence (OK);
    all FACET_UNAVAILABLE → absence (OK)
7.  framework_lock: "no framework.lock" → absence (OK)
8.  isolation: no ``.gov-runtime`` → absence (OK);
    "cannot determine git root" (runtime exists, git broken) → **ERROR → fail**
9.  adoption_level: no unmeasured state
10. claude_code: no unmeasured state
11. held_out: no unmeasured state (uses "report" status)

Predecessor analysis
--------------------
Round 2's ``test_w1_27_isolation_r2.py`` tests that isolation is measured,
not a constant stub.  There are no round-1 or round-2 tests for the
unmeasured-vs-error distinction in index_freshness, canaries, or
isolation's git-root case.  The predecessor was **absent**: no test
covers the error-masking bug.
"""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import tempfile
from pathlib import Path

import pytest

import w1_27_support as support


def _doctor_sections(envelope):
    """Extract doctor's full result dict from a healthy or unhealthy envelope."""
    if envelope.get("ok"):
        return envelope.get("result", {})
    return envelope.get("error", {}).get("details", {})


def _strip_confounders(project):
    """Remove tool-registry so the tools section doesn't fail for unrelated
    reasons (node version, missing openspec/ccusage) and confound the test."""
    reg = project / "governance" / "project" / "tool-registry.yaml"
    if reg.exists():
        reg.unlink()
    support.commit_all(project, "strip tool-registry for isolated test")


# --------------------------------------------------------------------------- #
# Case 1: index_freshness exception → doctor exits non-zero, section is "fail"
# --------------------------------------------------------------------------- #

def test_doctor_index_freshness_error_is_fail(gov, project, interface):
    """When ``freshness()`` raises an error, doctor must exit non-zero and
    the index_freshness section must have status "fail", not "unmeasured".

    KPI: "non-zero on any failure" [CAP-02.a]; DEC-425.
    Currently fails: the exception produces ``"unmeasured"`` with
    ``"cannot check index freshness"``, doctor exits 0.
    """
    _strip_confounders(project)
    support.write_path_map(project, support.minimal_valid_path_map())

    store_dir = project / ".gov-runtime"
    store_dir.mkdir(parents=True, exist_ok=True)
    store_path = store_dir / "store.db"
    store_path.write_text("this is not a valid SQLite database", encoding="utf-8")
    support.commit_all(project, "corrupt store.db for freshness error")

    run = gov("doctor", "--json")
    envelope = run.envelope()
    sections = _doctor_sections(envelope)
    freshness = sections.get("index_freshness", {})

    assert freshness.get("status") == "fail", (
        f"index_freshness should be 'fail' when freshness() raises an "
        f"error (corrupt store.db), but got status='{freshness.get('status')}'\n"
        f"section: {freshness}\n{run.describe()}"
    )


# --------------------------------------------------------------------------- #
# Case 2: canary runner exception → doctor exits non-zero, section is "fail"
# --------------------------------------------------------------------------- #

def test_doctor_canary_error_is_fail(gov, project, interface):
    """When ``run_canaries()`` raises an exception, doctor must exit
    non-zero and the canaries section must have status "fail", not
    "unmeasured".

    KPI: "non-zero on any failure" [CAP-02.a]; DEC-425.
    Currently fails: ``_check_canaries`` catches the exception and
    returns ``"unmeasured"`` with ``"canary runner failed"``.

    Trigger: corrupt the canary module in the project so that importing
    ``run_canaries`` from it raises.  ``_check_canaries`` does
    ``from gov.retrieval.canary import run_canaries`` inside a
    ``try/except Exception`` — the import error is caught and the
    section gets ``"unmeasured"`` instead of ``"fail"``.
    """
    _strip_confounders(project)
    support.write_path_map(project, support.minimal_valid_path_map())

    canary_module = project / "src" / "gov" / "retrieval" / "canary.py"
    canary_module.write_text(
        "raise RuntimeError('canary module corrupted for test')\n",
        encoding="utf-8",
    )
    support.commit_all(project, "corrupt canary module for error test")

    run = gov("doctor", "--json")
    envelope = run.envelope()
    sections = _doctor_sections(envelope)
    canaries = sections.get("canaries", {})

    assert canaries.get("status") == "fail", (
        f"canaries should be 'fail' when run_canaries() raises an error "
        f"(import failure), but got status='{canaries.get('status')}'\n"
        f"section: {canaries}\n{run.describe()}"
    )


# --------------------------------------------------------------------------- #
# Case 3: isolation with .gov-runtime but no git → section is "fail"
# --------------------------------------------------------------------------- #

def test_doctor_isolation_broken_git_is_fail():
    """When ``.gov-runtime`` exists but git root cannot be determined,
    doctor's isolation section must be "fail", not "unmeasured".

    KPI: "non-zero on any failure" [CAP-02.a]; DEC-425.
    Currently fails: returns ``"unmeasured"`` with ``"cannot determine
    git root"``.

    Tested via the ``_check_isolation`` function directly because the
    scenario requires a directory with ``.gov-runtime`` but no ``.git``
    — a state that cannot be produced by a ``gov`` command.
    """
    from gov.doctor.command import _check_isolation

    with tempfile.TemporaryDirectory() as tmpdir:
        broken = Path(tmpdir) / "broken-project"
        broken.mkdir()
        runtime = broken / ".gov-runtime"
        runtime.mkdir()
        (runtime / "store.db").write_text("placeholder", encoding="utf-8")

        result = _check_isolation(broken)

    assert result.get("status") == "fail", (
        f"isolation should be 'fail' when .gov-runtime exists but git "
        f"root cannot be determined, but got status='{result.get('status')}'\n"
        f"result: {result}"
    )


# --------------------------------------------------------------------------- #
# Case 4: unmeasured-absence must not be ADOPTED_HEALTHY
# --------------------------------------------------------------------------- #

def test_unmeasured_absence_prevents_adopted_healthy(gov, project, interface):
    """A project with an unmeasured section (absence, not error) must
    never be reported as ADOPTED_HEALTHY.

    KPI: "adoption level" [CAP-54.a]; DEC-416.
    Currently fails: ``_check_adoption_level`` checks only the path
    map's systems and capabilities, ignoring whether other sections
    are unmeasured.
    """
    _strip_confounders(project)

    systems_yaml = "".join(
        f"  {name}:\n    status: minimal\n    where: ['**']\n"
        for name in support.SYSTEMS
    )
    path_map = (
        "state_class: AUTHORITATIVE\n"
        "namespaces:\n"
        f"{support.minimal_namespace_yaml()}"
        "capabilities:\n"
        "  code_intelligence:\n    enabled: false\n"
        "  research_corpus:\n    enabled: true\n"
        f"policies:\n{support.minimal_policies_yaml()}"
        f"systems:\n{systems_yaml}"
    )
    support.write_path_map(project, path_map)

    run = gov("doctor", "--json")
    envelope = run.envelope()
    sections = _doctor_sections(envelope)

    adoption = sections.get("adoption_level", {})
    level = adoption.get("level", "")

    unmeasured_sections = [
        k for k, v in sections.items()
        if isinstance(v, dict) and v.get("status") == "unmeasured"
        and k != "adoption_level"
    ]
    assert unmeasured_sections, (
        f"expected at least one unmeasured section (absence) in the "
        f"project but found none — test fixture is wrong\n"
        f"sections: {list(sections.keys())}\n{run.describe()}"
    )
    assert level != "ADOPTED_HEALTHY", (
        f"adoption level is ADOPTED_HEALTHY but the project has "
        f"unmeasured sections: {unmeasured_sections} — a project with "
        f"unmeasured sections is never ADOPTED_HEALTHY\n"
        f"adoption: {adoption}\n{run.describe()}"
    )


# --------------------------------------------------------------------------- #
# Case 5: healthy=true must never be true when a measurement raised an error
# --------------------------------------------------------------------------- #

def test_healthy_false_when_measurement_error(gov, project, interface):
    """Doctor ``healthy: true`` must never be true when a measurement
    raised an error.

    KPI: "non-zero on any failure" [CAP-02.a]; DEC-425.
    Currently fails: ``healthy`` considers only "fail"/"drift", not
    "unmeasured" with an error cause.  With tool-registry removed, the
    only abnormality is the corrupt store (measurement error), yet
    doctor reports healthy.
    """
    _strip_confounders(project)
    support.write_path_map(project, support.minimal_valid_path_map())

    store_dir = project / ".gov-runtime"
    store_dir.mkdir(parents=True, exist_ok=True)
    store_path = store_dir / "store.db"
    store_path.write_text("this is not a valid SQLite database", encoding="utf-8")
    support.commit_all(project, "corrupt store.db to trigger measurement error")

    run = gov("doctor", "--json")
    envelope = run.envelope()

    if envelope.get("ok"):
        healthy = envelope.get("result", {}).get("healthy")
    else:
        healthy = envelope.get("error", {}).get("details", {}).get("healthy")

    assert healthy is not True, (
        f"doctor reports healthy=true even though a measurement raised "
        f"an error (corrupt store.db); healthy must be false when any "
        f"measurement fails\n{run.describe()}"
    )
    assert run.returncode != 0, (
        f"doctor exits 0 (healthy) with a corrupt store.db — a "
        f"measurement error must make doctor exit non-zero\n{run.describe()}"
    )
