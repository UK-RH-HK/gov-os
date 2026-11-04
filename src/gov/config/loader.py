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
# The secrets scan's switch (DEC-1045, as DEC-953 switched the other lifted gates): one key ``scan``, ``on`` or ``off``.
# The file absent, or the key absent, is on; any other value is CONFIG_INVALID, never off.
SECRETS_FILE = "secrets.yaml"
SECRETS_SCHEMA = {"scan": {"required": False, "type": str}}
SCAN_VALUES = ("on", "off")
# Routing by question type (W2-32 S8, DEC-1067 (a)): ``routing.code_first`` and ``routing.named_first``, each a whole
# number of 0 or more (absent or 0: off, today's order). Any other key or value is CONFIG_INVALID.
RETRIEVAL_FILE = "retrieval.yaml"
RETRIEVAL_SCHEMA = {"routing": {"required": False, "type": dict}}
ROUTING_KEYS = ("code_first", "named_first")
KNOWN_FILES = {"path-map.yaml": PATH_MAP_SCHEMA, SECRETS_FILE: SECRETS_SCHEMA, RETRIEVAL_FILE: RETRIEVAL_SCHEMA}
# A namespace's keyword-index policy (DEC-1066 (3)): optional, one of two values; absent is indexed. Any other value is
# CONFIG_INVALID in either form of the path map, so a misspelt exclusion never leaves its files in the index.
LEXICAL_POLICY = "lexical_policy"
INDEXED, NOT_INDEXED = "indexed", "not indexed"
LEXICAL_POLICIES = (INDEXED, NOT_INDEXED)
# ``not indexed`` with ``embedding_policy: embedded`` is refused (the CTO, P2): the vectors are built from the keyword
# index's chunks, so such a namespace would get no vectors while claiming them. The value semantic retrieval embeds.
EMBEDDED = "embedded"

_TYPE_NAMES = {dict: "map", list: "list", str: "string"}


def read_yaml(path: Path, code: str, rel: str, plain: bool = False):
    """The YAML document at ``path``. ``plain``: every scalar as the string written (so ``off`` is not a boolean)."""
    try:
        import yaml
    except ImportError:
        raise GovError(code, f"{rel}: cannot be read, PyYAML is not available", {"file": rel, "key": None}) from None
    try:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            if not plain:
                raise
            raise GovError(code, f"{rel}: cannot be read: {exc.strerror or exc}", {"file": rel, "key": None}) from None
        return yaml.load(text, Loader=yaml.BaseLoader) if plain else yaml.safe_load(text)
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
    validate_lexical_policy(ns_name, ns_value, rel)


def lexical_policy_fault(ns_value: dict) -> str | None:
    """Why the namespace's ``lexical_policy`` is refused, or None: a value other than ``LEXICAL_POLICIES`` (absent is
    ``indexed``), or ``not indexed`` with ``embedding_policy: embedded``."""
    if LEXICAL_POLICY not in ns_value:
        return None
    if ns_value[LEXICAL_POLICY] not in LEXICAL_POLICIES:
        return f"must be one of {LEXICAL_POLICIES} (absent: {INDEXED})"
    if ns_value[LEXICAL_POLICY] == NOT_INDEXED and ns_value.get("embedding_policy") == EMBEDDED:
        return (f"{NOT_INDEXED} cannot be embedded: the vectors are built from the keyword index's chunks "
                f"(embedding_policy is {EMBEDDED})")
    return None


def validate_lexical_policy(ns_name, ns_value, rel):
    """CONFIG_INVALID, naming the namespace, when ``lexical_policy_fault`` refuses its ``lexical_policy``."""
    fault = lexical_policy_fault(ns_value)
    if fault:
        raise _invalid(rel, f"namespaces.{ns_name}.{LEXICAL_POLICY}", fault)


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
    if rel.endswith(RETRIEVAL_FILE):
        _validate_retrieval(document, rel)
    if rel.endswith(SECRETS_FILE):
        for key in document:
            if key not in schema:
                raise _invalid(rel, str(key), "unknown key (the only key is 'scan')")
        if "scan" in document and document["scan"] not in SCAN_VALUES:
            raise _invalid(rel, "scan", f"must be one of {SCAN_VALUES}")


def _validate_retrieval(document, rel):
    for key in document:
        if key not in RETRIEVAL_SCHEMA:
            raise _invalid(rel, str(key), "unknown key (the only key is 'routing')")
    for key, value in (document.get("routing") or {}).items():
        if key not in ROUTING_KEYS:
            raise _invalid(rel, f"routing.{key}", f"unknown key (the keys are {', '.join(ROUTING_KEYS)})")
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise _invalid(rel, f"routing.{key}", "must be a whole number of 0 or more (0: off)")


def _validate_namespace_minimal(ns_name, ns_value, rel):
    if not isinstance(ns_value, dict):
        raise _invalid(rel, f"namespaces.{ns_name}", "must be a map")
    paths = ns_value.get("paths")
    if paths is not None and (not isinstance(paths, list) or not paths):
        raise _invalid(rel, f"namespaces.{ns_name}.paths", "must be a non-empty list")
    validate_lexical_policy(ns_name, ns_value, rel)


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


def _load(root: Path, name: str, schema: dict):
    """The known file ``name`` validated, or None when it is absent."""
    rel = f"{PROJECT_DIR}/{name}"
    path = Path(root) / rel
    if not path.is_file():
        return None
    secrets = name == SECRETS_FILE
    document = read_yaml(path, "CONFIG_INVALID", rel, plain=secrets)
    if (secrets or name == RETRIEVAL_FILE) and document is None:  # a file of comments alone holds no key
        document = {}
    if name == RETRIEVAL_FILE and isinstance(document, dict) and document.get("routing", {}) is None:
        document = {**document, "routing": {}}  # a ``routing:`` block with its keys commented out: off (S8-F4)
    validate(document, schema, rel)
    return document


def load_config(root: Path) -> dict:
    loaded = {}
    for name, schema in KNOWN_FILES.items():
        document = _load(root, name, schema)
        if document is not None:
            loaded[name] = document
    return loaded


def secrets_scan_on(root: Path) -> bool:
    """Whether the secrets scan is on at ``root`` (DEC-1045): reads ``secrets.yaml`` alone. Absent file or key: on.
    A file that cannot be read or holds another value raises CONFIG_INVALID: the switch fails closed, never off."""
    document = _load(root, SECRETS_FILE, SECRETS_SCHEMA) or {}
    return document.get("scan", "on") == "on"
