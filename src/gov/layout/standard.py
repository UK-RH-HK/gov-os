"""The standard as Gov OS ships it, read and validated by its published schema (``fabric.shipped``): never a default,
and no class, folder or pattern of its own here."""

from __future__ import annotations

import fnmatch
import json
from pathlib import Path

from gov.cli.errors import GovError
from gov.layout import CannotRun
from gov.util.patterns import _match_pattern

REL = "template/governance/kernel/standard.yaml"
SCHEMA_REL = "template/governance/kernel/schemas/standard.schema.json"
ASK = "ask"  # the answer that is no class


class Standard:
    def __init__(self, data: dict) -> None:
        self.version: int = data["version"]
        self.classes: dict[str, dict] = {entry["id"]: entry for entry in data["classes"]}
        self.stale_classes: list[str] = data["archive"]["stale_classes"]
        self.ceiling: dict = data["study_ceiling"]
        self.record_paths: list[str] = data["record_paths"]
        self.document_suffixes: tuple[str, ...] = tuple(data["document_suffixes"])
        # the longest literal text first: it gives the class where two patterns cover a path
        self._fixed = sorted(data["fixed"], key=lambda each: -len(each["pattern"].replace("*", "")))
        names = data["secret_patterns"]
        self._secret = [name for name in names if not name.startswith("!")]
        self._not_secret = [name[1:] for name in names if name.startswith("!")]
        self._generated = [name.rstrip("/") for name in data["generated_patterns"]]

    def fixed_class(self, path: str) -> str | None:
        """The class of a tool-fixed ``path``, else None."""
        return next((each["class"] for each in self._fixed if _match_pattern(path, each["pattern"])), None)

    def secret_name(self, path: str) -> bool:
        name = path.rsplit("/", 1)[-1]
        return (any(fnmatch.fnmatchcase(name, each) for each in self._secret)
                and not any(fnmatch.fnmatchcase(name, each) for each in self._not_secret))

    def generated_root(self, path: str) -> bool:
        name = path.rsplit("/", 1)[-1]
        return any(fnmatch.fnmatchcase(name, each) for each in self._generated)

    def whole(self, name: str) -> bool:
        """Whether ``name`` is an import class: moved whole, with an import name."""
        return self.classes.get(name, {}).get("moves") == "whole"

    def moves(self, name: str) -> bool:
        return self.classes.get(name, {}).get("moves", "no") != "no"

    def stale(self, name: str) -> bool:
        """Whether a line of class ``name`` states a stale class."""
        return "{stale_class}" in self.classes.get(name, {}).get("destination", "")


def load(root: Path) -> Standard:
    """The shipped standard for the repository ``root``; ``CannotRun`` where it or its schema is not there, cannot be
    read or is refused by the schema."""
    import jsonschema
    import yaml

    from gov.adopt import fabric

    try:
        path, schema = fabric.shipped(REL, root), fabric.shipped(SCHEMA_REL, root)
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(json.loads(schema.read_text(encoding="utf-8")))
        fault = jsonschema.exceptions.best_match(validator.iter_errors(data))
    except GovError as error:
        raise CannotRun(error.message) from None
    except (OSError, ValueError, yaml.YAMLError, jsonschema.exceptions.SchemaError) as error:
        raise CannotRun(f"{REL} cannot be read: {type(error).__name__}") from None
    if fault is not None:
        raise CannotRun(f"{REL} ({path}) is not valid by its schema at {fault.json_path}: {fault.message[:300]}")
    return Standard(data)
