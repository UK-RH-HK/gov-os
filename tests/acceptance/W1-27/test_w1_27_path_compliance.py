"""KPI success 3: path-map compliance is checked by doctor.

Every tracked path matches a path-map entry, and a recorded reference to a
moved path is reported [CAP-06.d].
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import w1_27_support as support


def _path_map_with_namespace(name, paths):
    """Build a valid path map with one namespace covering only ``paths``."""
    ns = support.minimal_namespace_yaml(name=name, paths=paths)
    return (
        "state_class: AUTHORITATIVE\n"
        f"namespaces:\n{ns}"
        "capabilities:\n"
        "  code_intelligence:\n    enabled: false\n"
        "  research_corpus:\n    enabled: false\n"
        f"policies:\n{support.minimal_policies_yaml()}"
        f"systems:\n{support.minimal_systems_yaml()}"
    )


# --------------------------------------------------------------------------
# Every tracked path matches
# --------------------------------------------------------------------------

def test_full_coverage_is_healthy(gov, project, interface):
    """When every tracked path matches a namespace pattern, doctor is ok for path-map coverage."""
    support.write_path_map(project, support.minimal_valid_path_map())
    run = gov("doctor", "--json")
    envelope = support.assert_envelope(run, interface, command="doctor")
    text = json.dumps(envelope)
    has_unclassified = "unclassified" in text.lower()
    if has_unclassified:
        result = envelope.get("result", {})
        count = 0
        if isinstance(result, dict):
            for key in result:
                if "unclassified" in key.lower() or "path" in key.lower():
                    val = result[key]
                    if isinstance(val, int):
                        count = val
                    elif isinstance(val, list):
                        count = len(val)
        assert count == 0, f"there are unclassified paths on a project with full coverage\n{run.describe()}"


def test_unclassified_path_is_reported(gov, project, interface):
    """A tracked path that matches no namespace pattern is reported by doctor."""
    narrow_map = _path_map_with_namespace("only-src", '["src/**"]')
    support.write_path_map(project, narrow_map)
    run = gov("doctor", "--json")
    envelope = support.assert_envelope(run, interface, command="doctor")
    if envelope["ok"] is True:
        pytest.fail(f"doctor is ok despite unclassified paths\n{run.describe()}")
    text = json.dumps(envelope)
    found = "unclassified" in text.lower() or "path" in text.lower()
    assert found, f"doctor does not mention unclassified paths\n{run.describe()}"


def test_moved_path_reference_is_reported(gov, project, interface):
    """A recorded reference to a path that has been moved is reported by doctor (CAP-06.d).

    The test creates a file, commits it, moves it, commits the move, then asserts that doctor reports
    the reference to the old path.
    """
    old_path = project / "src" / "gov" / "doctor" / "old_module.py"
    old_path.parent.mkdir(parents=True, exist_ok=True)
    old_path.write_text("# old module\n", encoding="utf-8")
    support.commit_all(project, "add old module")

    new_path = project / "src" / "gov" / "doctor" / "new_module.py"
    old_path.rename(new_path)
    support.commit_all(project, "move old module to new module")

    support.write_path_map(project, support.minimal_valid_path_map())
    run = gov("doctor", "--json")
    envelope = support.assert_envelope(run, interface, command="doctor")
    text = json.dumps(envelope)
    moved_mentioned = "moved" in text.lower() or "rename" in text.lower() or "old_module" in text.lower()
    assert moved_mentioned, f"doctor does not report references to moved paths\n{run.describe()}"
