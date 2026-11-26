"""W2-213 slice 1: the rules code decides alone, and the one place the standard gives an item (SL-7, SL-9).

Regression evidence only (DEC-136). The standard is the committed one; every path is invented.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from gov.layout import rules, standard

REPO = Path(__file__).resolve().parents[3]


@pytest.fixture(scope="module")
def std():
    return standard.load(REPO)


def test_the_committed_standard_loads_by_its_schema_with_eighteen_classes(std):
    assert std.version == 1 and len(std.classes) == 18 and "ask" not in std.classes


@pytest.mark.parametrize("path, expected", [
    ("README.md", "docs"), ("CLAUDE.md", "governance"), ("lefthook.yml", "config"), ("uv.lock", "config"),
    ("governance/project/path-map.yaml", "governance"), ("governance/kernel/standard.yaml", "kit"),
    ("governance/adoption/A1.md", "record"), ("docs/close/x.md", "record"), ("openspec/a/spec.md", "spec"),
    ("src/app/main.py", None), ("docs/guide.md", None), ("vendor/lib/package.json", None),
])
def test_a_tool_fixed_path_has_its_class_by_the_longest_pattern(std, path, expected):
    assert std.fixed_class(path) == expected


@pytest.mark.parametrize("path, secret", [
    (".env", True), ("web/.env.local", True), ("keys/server.pem", True), ("id_rsa", True),
    (".env.example", False), ("src/key.py", False), ("governance/project/secrets.yaml", False),
])
def test_a_secret_name_is_told_by_its_name_and_example_is_none(std, path, secret):
    assert std.secret_name(path) is secret


def test_a_generated_root_is_told_by_its_name(std):
    assert std.generated_root("web/node_modules") and std.generated_root("__pycache__")
    assert not std.generated_root("docs")


def test_the_package_roots_are_the_manifests_folders_and_src_for_a_root_manifest():
    tracked = ["pyproject.toml", "src/a.py", "tools/ui/package.json", "vendor/x/package.json"]
    assert rules.package_roots(tracked, ["vendor/x"]) == {"src", "tools/ui"}
    assert rules.package_roots(["package.json", "index.js"], []) == set()


@pytest.mark.parametrize("name, path, extra, destination", [
    ("spec", "design/login.md", {}, "docs/specs/login.md"),
    ("spec", "docs/specs/login.md", {}, "docs/specs/login.md"),
    ("docs", "notes/guide.md", {}, "docs/guide.md"),
    ("data", "samples", {}, "data/samples"),
    ("archive", "docs/old.md", {"stale_class": "legacy"}, "archive/legacy/docs/old.md"),
    ("archive", "archive/2024/old.md", {"stale_class": "historical"}, "archive/historical/2024/old.md"),
    ("import-use", "vendor/lib", {"import_name": "lib", "root": "vendor/lib"}, "imports/lib"),
    ("import-study", "study/a/b.py", {"import_name": "s", "root": "study"}, "imports/s/a/b.py"),
    ("code", "tool.py", {}, "tool.py"),
])
def test_the_destination_of_a_class_and_path(std, name, path, extra, destination):
    assert rules.destination(std, name, path, **extra) == destination


def test_research_and_record_take_one_folder_of_the_agents_choice(std):
    expected = rules.destination(std, "research", "notes/trial.md")
    assert rules.fits(expected, "docs/research/trial-1/trial.md")
    assert not rules.fits(expected, "docs/research/trial.md")
    assert not rules.fits(expected, "docs/research/a/b/trial.md")
