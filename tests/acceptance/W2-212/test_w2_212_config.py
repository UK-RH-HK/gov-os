"""W2-212 F1 (the class cannot fail open) and the kernel schema, and SR-4's `gov update` carriage."""
from __future__ import annotations

import json

import pytest
import yaml

from w2_212_support import CLASSES, PATH_MAP, REPO, commit, git, init

from gov.check.pathmap import check
from gov.cli.errors import GovError
from gov.config.loader import load_config


def plant(tmp_path, old):
    root = tmp_path / "r"
    init(root)
    spaces = {"old": {"paths": ["docs/old/**"], **old}, "rest": {"paths": ["*", "docs/*.md", "governance/**"]}}
    commit(root, {PATH_MAP: yaml.safe_dump({"namespaces": spaces}), "README.md": "x\n", "docs/old/a.md": "a\n"})
    return root


GOOD = {"lexical_policy": "not indexed", "embedding_policy": "not embedded"}


@pytest.mark.parametrize("value", CLASSES)
def test_f1_each_class_with_both_policies_is_valid(tmp_path, value):
    root = plant(tmp_path, {"stale_class": value, **GOOD})
    assert load_config(root)["path-map.yaml"]["namespaces"]["old"]["stale_class"] == value
    assert check(root) == []


@pytest.mark.parametrize("value", ["ancient", "archive", "Legacy", ""])
def test_f1_a_class_outside_the_three_is_config_invalid_naming_namespace_and_field(tmp_path, value):
    root = plant(tmp_path, {"stale_class": value, **GOOD})
    with pytest.raises(GovError) as raised:
        load_config(root)
    assert raised.value.code == "CONFIG_INVALID"
    assert "old" in raised.value.message and "stale_class" in raised.value.message
    findings = check(root)
    assert [f["code"] for f in findings] == ["PATH_MAP_INVALID"] and "stale_class" in findings[0]["message"]


@pytest.mark.parametrize("policies", [
    {"lexical_policy": "indexed", "embedding_policy": "not embedded"},
    {"embedding_policy": "not embedded"},
    {"lexical_policy": "not indexed"},
    {},
])
def test_f1_a_class_with_a_policy_that_keeps_it_in_index_or_vectors_is_config_invalid(tmp_path, policies):
    root = plant(tmp_path, {"stale_class": "superseded", **policies})
    with pytest.raises(GovError) as raised:
        load_config(root)
    assert raised.value.code == "CONFIG_INVALID" and "old" in raised.value.message
    assert [f["code"] for f in check(root)] == ["PATH_MAP_INVALID"]


def test_an_unclassed_namespace_is_as_before(tmp_path):
    root = plant(tmp_path, {"lexical_policy": "indexed"})
    assert "stale_class" not in load_config(root)["path-map.yaml"]["namespaces"]["old"]
    assert check(root) == []


def test_the_kernel_schema_declares_the_class():
    schema = json.loads((REPO / "template/governance/kernel/schemas/path-map.schema.json").read_text())
    namespace = schema["$defs"]["namespace"]
    assert sorted(namespace["properties"]["stale_class"]["enum"]) == sorted(CLASSES)
    assert "stale_class" not in namespace["required"]


def test_the_schema_accepts_a_classed_namespace_and_refuses_another_class():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((REPO / "template/governance/kernel/schemas/path-map.schema.json").read_text())
    namespace = {"$schema": schema["$schema"], "$defs": schema["$defs"], "$ref": "#/$defs/namespace"}
    full = {"paths": ["docs/old/**"], "memory_class": "governance", "sensitivity": "s", "permitted_roles": ["engineer"],
            "retention": "r", "export_policy": "e", "embedding_policy": "not embedded", "provenance": "p",
            "deletion_rebuild": "d"}
    jsonschema.validate({**full, "stale_class": "legacy"}, namespace)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({**full, "stale_class": "ancient"}, namespace)


SKILLS = ("template/governance/kernel/skills/adopt/SKILL.md", "template/.rulesync/skills/adopt/SKILL.md")
CARRIED = ("template/governance/kernel/schemas/path-map.schema.json", *SKILLS)


def test_sr4_gov_update_carries_the_route_the_schema_and_both_skill_copies_under_template():
    """``gov update`` renders release B's ``template/`` (copier ``_subdirectory: template``) and copies what it holds:
    the three files are in it, none is excluded or skipped, and they hold the route (not the old text)."""
    copier = yaml.safe_load((REPO / "copier.yml").read_text())
    assert copier["_subdirectory"] == "template"
    for rel in CARRIED:
        assert (REPO / rel).is_file() and not any(
            __import__("fnmatch").fnmatch(rel[len("template/"):], pattern) for pattern in copier.get("_exclude", []))
        assert not any(__import__("fnmatch").fnmatch(rel[len("template/"):], p) for p in copier.get("_skip_if_exists", []))
    assert "stale_class" in (REPO / CARRIED[0]).read_text() and "stale_class" in (REPO / SKILLS[0]).read_text()
