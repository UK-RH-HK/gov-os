"""KPI line 2: a path map that cannot be judged is a finding naming the cause, never green.

Missing where the project declares one (a repository with ``governance/project/``),
unreadable, unparsable, a top level that is not a map, no ``namespaces``, ``namespaces``
of neither form, or entries of a form the schema does not state. No finding code is
pinned for these new faults: the check is not green, and a finding about the path map
itself (not one of the per-path codes) names the path map's file and what is wrong
with it.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_95_support as s  # noqa: E402

FILES = ["README.md", "src/app/main.py"]
PM_NAME = "path-map.yaml"

# Words of which at least one names the cause, by case (lower case, any one suffices).
UNREADABLE = ("read", "permission", "access", "utf", "decod", "encod")
UNPARSABLE = ("yaml", "pars", "syntax", "invalid")
NOT_A_MAP = ("map", "mapping", "object", "dict", "top")
NAMESPACES = ("namespaces",)
ENTRY = ("namespace", "entry", "entries", "paths")
MISSING = ("missing", "not found", "no such", "absent", "does not exist", "not exist")

_FIELDS = "memory_class: governance\n    sensitivity: internal\n"

CASES = {
    "unparsable_yaml": (b"namespaces: [\n  code: {paths: ['src/**'\n", UNPARSABLE),
    "top_level_a_list": (b"- namespaces\n- code\n", NOT_A_MAP),
    "top_level_a_string": (b"just a string\n", NOT_A_MAP),
    "no_namespaces": (b"state_class: AUTHORITATIVE\n", NAMESPACES),
    "namespaces_a_string": (b"namespaces: src/**\n", NAMESPACES),
    "namespaces_a_number": (b"namespaces: 3\n", NAMESPACES),
    "mapping_entry_a_list": (b"namespaces:\n  code: ['src/**', '*', 'governance/**']\n", ENTRY),
    "mapping_entry_without_paths": (("namespaces:\n  code:\n    " + _FIELDS).encode(), ENTRY),
    "mapping_entry_paths_a_string": (
        ("namespaces:\n  code:\n    paths: '**'\n    " + _FIELDS).encode(),
        ENTRY,
    ),
    "list_entry_a_string": (b"namespaces:\n  - code\n  - docs\n", ENTRY),
    "not_utf8": (b"namespaces:\n  code:\n    paths: ['\xff\xfe**']\n", UNREADABLE),
}


def _assert_finding_naming_cause(result, words, case):
    """Not green, and a finding about the path map itself (not a per-path finding) names the file and the cause."""
    assert result.code != 0, f"{case}: the path map cannot be judged, yet the check is green:\n" + result.describe()
    assert result.stdout.strip(), f"{case}: not green but no finding on stdout:\n" + result.describe()
    assert result.findings, f"{case}: no finding as JSON on stdout:\n" + result.describe()
    # A per-path finding ("README.md matches no namespace in path-map.yaml") does not name the cause.
    about_map = [
        json.dumps(f)
        for f in result.findings
        if not (isinstance(f, dict) and f.get("code") in (s.NO_NAMESPACE, s.MULTIPLE_NAMESPACES))
    ]
    assert about_map, f"{case}: no finding about the path map itself, only per-path findings:\n" + result.describe()
    assert any(PM_NAME in f for f in about_map), (
        f"{case}: no finding names the path map's file:\n" + result.describe()
    )
    assert any(PM_NAME in f and s.mentions_any(f, words) for f in about_map), (
        f"{case}: no finding names what is wrong (one of {words}):\n" + result.describe()
    )


@pytest.mark.parametrize("case", sorted(CASES))
def test_w2_95_path_map_that_cannot_be_judged_is_a_finding(tmp_path, case):
    data, words = CASES[case]
    repo = s.Planted(tmp_path, FILES, path_map_bytes=data)
    _assert_finding_naming_cause(repo.declared(), words, case)


@pytest.mark.skipif(hasattr(os, "geteuid") and os.geteuid() == 0, reason="root reads any file")
def test_w2_95_path_map_without_read_permission_is_a_finding(tmp_path):
    repo = s.Planted(
        tmp_path, FILES, s.mapping_form({"code": ["src/**"], "root": ["*"], "governance": ["governance/**"]})
    )
    pm = repo.root / s.PATH_MAP
    pm.chmod(0)
    try:
        result = repo.declared()
    finally:
        pm.chmod(0o644)
    _assert_finding_naming_cause(result, UNREADABLE, "no read permission")


def test_w2_95_missing_path_map_under_governance_project_is_a_finding(tmp_path):
    # The repository has governance/project/ (with a tracked file) and so declares a path map there.
    repo = s.Planted(tmp_path, FILES + ["governance/project/README.md"])
    assert not (repo.root / s.PATH_MAP).exists()
    _assert_finding_naming_cause(repo.declared(), MISSING, "missing path map")


def test_w2_95_missing_path_map_is_never_green_in_gov_check(tmp_path):
    repo = s.Planted(tmp_path, FILES + ["governance/project/README.md"])
    result = repo.gov_check()
    assert result.envelope is not None, "gov check --json printed no JSON:\n" + result.describe()
    check = result.pathmap()
    if result.envelope.get("ok") is False:
        # The command refused the project as a whole: not green, and it must say why.
        assert PM_NAME in str(result.envelope.get("error")), result.describe()
        return
    assert check is not None, "core-pathmap is not in gov check's result:\n" + result.describe()
    assert check.get("status") != "GREEN", "a missing path map is reported green:\n" + result.describe()
    assert check.get("findings"), result.describe()
    assert (result.family() or {}).get("status") != "GREEN", result.describe()
