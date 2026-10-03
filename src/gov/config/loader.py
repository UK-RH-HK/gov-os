"""Load the ``governance/project/`` files the CLI knows (DEC-185).

A missing file is not an error. An invalid one is ``CONFIG_INVALID``, naming the
file and the key. ``path-map.yaml`` is the only file known today; the tickets
that add the other overlay files add them to ``KNOWN_FILES``.
"""

from __future__ import annotations

from pathlib import Path

from gov.cli.errors import GovError
from gov.config.path_map_schema import PATH_MAP_SCHEMA

PROJECT_DIR = "governance/project"
KNOWN_FILES = {"path-map.yaml": PATH_MAP_SCHEMA}

_TYPE_NAMES = {dict: "map", list: "list", str: "string"}


def read_yaml(path: Path, code: str, rel: str):
    """The YAML document in ``path``; a GovError ``code`` naming ``rel`` when it cannot be read as YAML."""
    try:
        import yaml  # imported here: ``gov --help`` and a project without YAML files do not pay for it
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


def load_config(root: Path) -> dict:
    """``file name -> document`` for every known file that exists under ``governance/project/`` of ``root``."""
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
