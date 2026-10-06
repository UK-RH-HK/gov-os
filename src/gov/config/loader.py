"""Load the ``governance/project/`` files the CLI knows (DEC-185).

A missing file is not an error. An invalid one is ``CONFIG_INVALID``, naming the
file and the key. ``path-map.yaml`` is validated against the W1-08 schema (DEC-228).
"""

from __future__ import annotations

from pathlib import Path

from gov.cli.errors import GovError
from gov.config.path_map_schema import (
    ANY_STRENGTH,
    CAPABILITIES,
    HARD_BLOCK_ONLY,
    HARD_BLOCK_STRENGTHS,
    MEMORY_CLASSES,
    NAMESPACE_FIELDS,
    NAMESPACE_OPTIONAL_FIELDS,
    PATH_MAP_SCHEMA,
    POLICY_KEYS,
    STRENGTHS,
    SYSTEM_KEYS,
    SYSTEM_STATUSES,
    W1_08_EXTENDED_KEYS,
    WARNING_OR_STRONGER,
    WARNING_STRENGTHS,
)

PROJECT_DIR = "governance/project"
KNOWN_FILES = {"path-map.yaml": PATH_MAP_SCHEMA}

_TYPE_NAMES = {dict: "map", list: "list", str: "string"}


def read_yaml(path: Path, code: str, rel: str):
    try:
        import yaml
    except ImportError:
        raise GovError(code, f"{rel}: cannot be read, PyYAML is not available", {"file": rel, "key": None}) from None
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, UnicodeDecodeError) as exc:
        reason = " ".join(str(exc).split())
        raise GovError(code, f"{rel}: not valid YAML: {reason}", {"file": rel, "key": None}) from None


def _invalid(rel: str, key: str | None, reason: str) -> GovError:
    where = f"{rel}: key '{key}'" if key else rel
    return GovError("CONFIG_INVALID", f"{where}: {reason}", {"file": rel, "key": key})


def _validate_namespace_field(ns_name, field, val, rel):
    if field == "permitted_roles":
        if not isinstance(val, list) or not val:
            raise _invalid(rel, f"namespaces.{ns_name}.{field}", "must be a non-empty list")
        for item in val:
            if not isinstance(item, str) or not item:
                raise _invalid(rel, f"namespaces.{ns_name}.{field}", "each item must be a non-empty string")
    else:
        if not isinstance(val, str) or not val:
            raise _invalid(rel, f"namespaces.{ns_name}.{field}", "must be a non-empty string")


def _validate_namespace(ns_name, ns_value, rel):
    if not isinstance(ns_value, dict):
        raise _invalid(rel, f"namespaces.{ns_name}", "must be a map")
    for field in NAMESPACE_FIELDS:
        if field not in ns_value:
            raise _invalid(rel, f"namespaces.{ns_name}.{field}", "required field is missing")
    paths = ns_value.get("paths")
    if not isinstance(paths, list) or not paths:
        raise _invalid(rel, f"namespaces.{ns_name}.paths", "must be a non-empty list")
    for item in paths:
        if not isinstance(item, str) or not item:
            raise _invalid(rel, f"namespaces.{ns_name}.paths", "each path must be a non-empty string")
    mc = ns_value.get("memory_class")
    if mc not in MEMORY_CLASSES:
        raise _invalid(rel, f"namespaces.{ns_name}.memory_class", f"must be one of {MEMORY_CLASSES}")
    for field in NAMESPACE_FIELDS:
        if field in ("paths", "memory_class"):
            continue
        _validate_namespace_field(ns_name, field, ns_value[field], rel)
    for field in NAMESPACE_OPTIONAL_FIELDS:
        if field in ns_value:
            _validate_namespace_field(ns_name, field, ns_value[field], rel)


def _validate_capabilities(caps, rel):
    if not isinstance(caps, dict):
        raise _invalid(rel, "capabilities", "must be a map")
    for cap_name in CAPABILITIES:
        if cap_name not in caps:
            raise _invalid(rel, f"capabilities.{cap_name}", "required capability is missing")
    for key in caps:
        if key not in CAPABILITIES:
            raise _invalid(rel, f"capabilities.{key}", "unknown capability (closed list)")
    ci = caps.get("code_intelligence")
    if not isinstance(ci, dict):
        raise _invalid(rel, "capabilities.code_intelligence", "must be a map")
    if "enabled" not in ci:
        raise _invalid(rel, "capabilities.code_intelligence.enabled", "required field is missing")
    if not isinstance(ci["enabled"], bool):
        raise _invalid(rel, "capabilities.code_intelligence.enabled", "must be a boolean")
    if ci["enabled"]:
        langs = ci.get("languages")
        if not isinstance(langs, list) or not langs:
            raise _invalid(rel, "capabilities.code_intelligence.languages",
                           "required and must be non-empty when code_intelligence is enabled")
        for item in langs:
            if not isinstance(item, str) or not item:
                raise _invalid(rel, "capabilities.code_intelligence.languages",
                               "each language must be a non-empty string")
    else:
        langs = ci.get("languages")
        if langs is not None and not isinstance(langs, list):
            raise _invalid(rel, "capabilities.code_intelligence.languages", "must be a list when present")
    rc = caps.get("research_corpus")
    if not isinstance(rc, dict):
        raise _invalid(rel, "capabilities.research_corpus", "must be a map")
    if "enabled" not in rc:
        raise _invalid(rel, "capabilities.research_corpus.enabled", "required field is missing")
    if not isinstance(rc["enabled"], bool):
        raise _invalid(rel, "capabilities.research_corpus.enabled", "must be a boolean")


def _validate_policies(policies, rel):
    if not isinstance(policies, dict):
        raise _invalid(rel, "policies", "must be a map")
    for key in POLICY_KEYS:
        if key not in policies:
            raise _invalid(rel, f"policies.{key}", "required policy is missing")
    for key in policies:
        if key not in POLICY_KEYS:
            raise _invalid(rel, f"policies.{key}", "unknown policy (closed list)")
    for key in POLICY_KEYS:
        val = policies[key]
        if key in HARD_BLOCK_ONLY:
            if val not in HARD_BLOCK_STRENGTHS:
                raise _invalid(rel, f"policies.{key}", "must be hard-block")
        elif key in WARNING_OR_STRONGER:
            if val not in WARNING_STRENGTHS:
                raise _invalid(rel, f"policies.{key}", "must be warning or hard-block")
        elif key in ANY_STRENGTH:
            if val not in STRENGTHS:
                raise _invalid(rel, f"policies.{key}", f"must be one of {sorted(STRENGTHS)}")


def _validate_systems(systems, rel):
    if not isinstance(systems, dict):
        raise _invalid(rel, "systems", "must be a map")
    for key in SYSTEM_KEYS:
        if key not in systems:
            raise _invalid(rel, f"systems.{key}", "required system is missing")
    for key in systems:
        if key not in SYSTEM_KEYS:
            raise _invalid(rel, f"systems.{key}", "unknown system (closed list)")
    for key in SYSTEM_KEYS:
        sys_val = systems[key]
        if not isinstance(sys_val, dict):
            raise _invalid(rel, f"systems.{key}", "must be a map")
        status = sys_val.get("status")
        if status not in SYSTEM_STATUSES:
            raise _invalid(rel, f"systems.{key}.status", f"must be one of {SYSTEM_STATUSES}")
        if status == "absent":
            if not isinstance(sys_val.get("reason"), str) or not sys_val.get("reason"):
                raise _invalid(rel, f"systems.{key}.reason", "required when status is absent")
        else:
            where = sys_val.get("where")
            if not isinstance(where, list) or not where:
                raise _invalid(rel, f"systems.{key}.where", "required when status is implemented or minimal")


def validate(document, schema: dict, rel: str) -> None:
    if not isinstance(document, dict):
        raise _invalid(rel, None, "the top level must be a map")
    for key, rule in schema.items():
        if key not in document:
            if rule.get("required"):
                raise _invalid(rel, key, "required key is missing")
            continue
        value = document[key]
        if not isinstance(value, rule["type"]):
            raise _invalid(rel, key, f"must be a {_TYPE_NAMES[rule['type']]}")
        if "values" in rule:
            for name, item in value.items():
                if not isinstance(item, rule["values"]):
                    raise _invalid(rel, f"{key}.{name}", f"must be a {_TYPE_NAMES[rule['values']]}")
    if rel.endswith("path-map.yaml"):
        _validate_path_map(document, rel)


def _validate_namespace_minimal(ns_name, ns_value, rel):
    if not isinstance(ns_value, dict):
        raise _invalid(rel, f"namespaces.{ns_name}", "must be a map")
    paths = ns_value.get("paths")
    if paths is not None and (not isinstance(paths, list) or not paths):
        raise _invalid(rel, f"namespaces.{ns_name}.paths", "must be a non-empty list")


def _validate_path_map(document, rel):
    present = [k for k in W1_08_EXTENDED_KEYS if k in document]
    w1_08 = len(present) == len(W1_08_EXTENDED_KEYS)
    if not w1_08 and len(present) > 1:
        missing = [k for k in W1_08_EXTENDED_KEYS if k not in document]
        raise _invalid(rel, missing[0], "required key is missing")
    if "namespaces" in document and isinstance(document["namespaces"], dict):
        for ns_name, ns_value in document["namespaces"].items():
            if w1_08:
                _validate_namespace(ns_name, ns_value, rel)
            else:
                _validate_namespace_minimal(ns_name, ns_value, rel)
    if w1_08:
        if "capabilities" in document:
            _validate_capabilities(document["capabilities"], rel)
        if "policies" in document:
            _validate_policies(document["policies"], rel)
        if "systems" in document:
            _validate_systems(document["systems"], rel)


def load_config(root: Path) -> dict:
    loaded = {}
    for name, schema in KNOWN_FILES.items():
        rel = f"{PROJECT_DIR}/{name}"
        path = Path(root) / rel
        if not path.is_file():
            continue
        document = read_yaml(path, "CONFIG_INVALID", rel)
        validate(document, schema, rel)
        loaded[name] = document
    return loaded
