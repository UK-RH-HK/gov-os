"""KPI lines 1, 3 and 5 through ``gov check --json``, and KPI line 3 through the declared command.

KPI 3: a planted adopted repository with a refactored path map written for it: green when
every tracked path is in exactly one namespace, red naming each path otherwise.
KPI 5 (in proportion, STANDARD): the other checks' results do not depend on core-pathmap's.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_95_support as s  # noqa: E402

# A messy repository, as found before adoption.
ADOPTED_FILES = [
    "Makefile",
    "setup.py",
    "app/__init__.py",
    "app/core/engine.py",
    "app/core/legacy/old_engine.py",
    "scripts/deploy.sh",
    "scripts/tools/cleanup.py",
    "vendor/lib/thing.c",
    "notes/2019/meeting.txt",
    "tests/test_engine.py",
]

# The refactored path map written for it: every tracked path in exactly one namespace.
REFACTORED = {
    "product": ["app/**", "setup.py", "Makefile"],
    "operations": ["scripts/**"],
    "third-party": ["vendor/**"],
    "history": ["notes/**"],
    "tests": ["tests/**"],
    "governance": ["governance/**"],
}


def _gov_pathmap(result):
    assert result.envelope is not None, "gov check --json printed no JSON:\n" + result.describe()
    assert result.answered(), "gov check refused the planted project:\n" + result.describe()
    check = result.pathmap()
    assert check is not None, "core-pathmap is not in gov check's result:\n" + result.describe()
    return check


def test_w2_95_adopted_repository_refactored_path_map_is_green(tmp_path):
    repo = s.Planted(tmp_path, ADOPTED_FILES, s.mapping_form(REFACTORED))
    declared = repo.declared()
    assert declared.code == 0, declared.describe()
    assert declared.findings == [], declared.describe()
    check = _gov_pathmap(repo.gov_check())
    assert check.get("status") == "GREEN", str(check)
    assert check.get("findings") == [], str(check)


def test_w2_95_adopted_repository_names_each_unplaced_and_doubly_placed_path(tmp_path):
    # The refactor missed vendor/ and notes/, and placed app/core/legacy/ in two namespaces.
    refactor = dict(REFACTORED)
    del refactor["third-party"], refactor["history"]
    refactor["legacy"] = ["app/core/legacy/**"]
    repo = s.Planted(tmp_path, ADOPTED_FILES, s.mapping_form(refactor))
    expected = {
        "vendor/lib/thing.c": [],
        "notes/2019/meeting.txt": [],
        "app/core/legacy/old_engine.py": ["legacy", "product"],
    }

    declared = repo.declared()
    assert declared.findings is not None, declared.describe()
    assert declared.code != 0, "an adopted repository with paths in none or two is green:\n" + declared.describe()
    named = s.path_findings(declared.findings)
    for path, namespaces in expected.items():
        assert path in named, f"{path} is not named:\n" + declared.describe()
        assert any(s.matched(f) == namespaces for f in named[path]), declared.describe()
    for path in ("app/core/engine.py", "scripts/tools/cleanup.py", "Makefile"):
        assert path not in named, declared.describe()

    check = _gov_pathmap(repo.gov_check())
    assert check.get("status") != "GREEN", "gov check reports core-pathmap green:\n" + str(check)
    named = s.path_findings(check.get("findings"))
    for path, namespaces in expected.items():
        assert path in named, f"gov check does not name {path}: {check}"
        assert any(s.matched(f) == namespaces for f in named[path]), str(check)


def test_w2_95_adopted_repository_kept_valid_a_new_unplaced_file_turns_it_red(tmp_path):
    repo = s.Planted(tmp_path, ADOPTED_FILES, s.mapping_form(REFACTORED))
    assert repo.declared().code == 0
    repo.add("docs/new.md")
    declared = repo.declared()
    assert declared.code != 0, "a newly tracked path in no namespace is green:\n" + declared.describe()
    named = s.path_findings(declared.findings)
    assert list(named) == ["docs/new.md"], declared.describe()
    assert named["docs/new.md"][0].get("code") == s.NO_NAMESPACE, declared.describe()


def test_w2_95_gov_check_family_is_not_green_on_a_mapping_form_path_in_none(tmp_path):
    repo = s.Planted(tmp_path, ["README.md", "src/main.py"], s.mapping_form({"code": ["src/**"]}))
    result = repo.gov_check()
    check = _gov_pathmap(result)
    assert check.get("status") != "GREEN", "a path in no namespace is reported green:\n" + str(check)
    named = s.path_findings(check.get("findings"))
    assert "README.md" in named and s.PATH_MAP in named, str(check)
    assert "src/main.py" not in named, str(check)
    assert (result.family() or {}).get("status") != "GREEN", result.describe()


def _others(result):
    """Every check but core-pathmap, and every family but path-map compliance, without provenance."""
    checks = {
        cid: {k: v for k, v in c.items() if k != "provenance"}
        for cid, c in result.checks().items()
        if cid != s.CHECK_ID
    }
    families = {f: v for f, v in (result.result.get("families") or {}).items() if f != s.FAMILY}
    return checks, families


def test_w2_95_other_checks_results_do_not_change_with_core_pathmap(tmp_path):
    files = ["README.md", "src/main.py"]
    green = s.Planted(tmp_path / "green", files, s.mapping_form({"code": ["src/**"], "root": ["*"], "g": ["governance/**"]}))
    red = s.Planted(tmp_path / "red", files, s.mapping_form({"code": ["src/**"]}))
    green_result, red_result = green.gov_check(), red.gov_check()
    green_check, red_check = _gov_pathmap(green_result), _gov_pathmap(red_result)
    assert green_check.get("status") == "GREEN", str(green_check)
    for check in (green_check, red_check):
        assert check.get("family") == s.FAMILY and check.get("severity") == "hard-block", str(check)
    assert _others(green_result) == _others(red_result), (
        "another check's result changed with core-pathmap's:\n"
        + green_result.describe()
        + "\n----\n"
        + red_result.describe()
    )
