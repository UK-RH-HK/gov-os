"""Round 2, KPI success 8: W1-08 schema validation backward compatibility.

``load_config()`` (called by every command) must remain backward-compatible
with a minimal path-map that has only ``namespaces`` as a map of maps.

``gov doctor`` (or ``gov`` generally) validates the full W1-08 schema and
reports missing top-level keys as health findings — but it must not crash
with ``CONFIG_INVALID`` on a minimal fixture.

Predecessor analysis
--------------------
The first round's ``test_w1_27_schema.py`` tests that all five required
top-level keys trigger ``CONFIG_INVALID`` when missing.  It does not test
that ``load_config`` (used by every command) accepts a minimal path-map
with only ``namespaces``.  The predecessor's case was **missing**: there
is no test for backward compatibility with the minimal schema.
"""

from __future__ import annotations

import json

import pytest

import w1_27_support as support


def _minimal_namespaces_only_path_map():
    """A path-map with only ``namespaces`` — the minimal backward-compatible shape."""
    return (
        "namespaces:\n"
        f"{support.minimal_namespace_yaml()}"
    )


# --------------------------------------------------------------------------- #
# load_config backward compatibility
# --------------------------------------------------------------------------- #

def test_status_accepts_minimal_path_map_with_only_namespaces(gov, project, interface):
    """``gov status`` must not reject a path-map that has only ``namespaces``.

    ``load_config()`` is called by every command.  It must accept a minimal
    path-map (just ``namespaces`` required as a map of maps) so that other
    tickets' test fixtures are not broken (DEC-185, DEC-228).
    """
    support.write_path_map(project, _minimal_namespaces_only_path_map())
    run = gov("status", "--json")
    envelope = run.envelope()
    error = envelope.get("error")
    if isinstance(error, dict):
        assert error.get("code") != support.CONFIG_INVALID, (
            f"load_config rejects a minimal path-map with only namespaces "
            f"— this breaks other tickets' fixtures (DEC-228)\n{run.describe()}"
        )


# --------------------------------------------------------------------------- #
# Doctor reports schema findings without crashing
# --------------------------------------------------------------------------- #

def test_doctor_does_not_crash_on_minimal_path_map(gov, project, interface):
    """``gov doctor`` with a minimal path-map must not crash with ``CONFIG_INVALID``.

    Doctor should validate the full W1-08 schema and report the missing
    keys as health findings in its result — not raise ``CONFIG_INVALID``
    before it can run.
    """
    support.write_path_map(project, _minimal_namespaces_only_path_map())
    run = gov("doctor", "--json")
    envelope = run.envelope()
    error = envelope.get("error")
    if isinstance(error, dict):
        assert error.get("code") != support.CONFIG_INVALID, (
            f"doctor crashes with CONFIG_INVALID on a minimal path-map "
            f"instead of reporting schema findings\n{run.describe()}"
        )
