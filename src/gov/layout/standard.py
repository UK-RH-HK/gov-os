"""The standard as Gov OS ships it (``fabric.shipped``): never a default, and no class, folder or pattern of its own
here."""

from __future__ import annotations

import fnmatch
from pathlib import Path

from gov.cli.errors import GovError
from gov.layout import CannotRun
from gov.util.patterns import _match_pattern

REL = "template/governance/kernel/standard.yaml"
_MOVES, _MEMORY = ("yes", "no", "whole"), ("embedded", "keyword", "out")  # the values the check knows how to read
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
    """The shipped standard for the repository ``root``; ``CannotRun`` where it is not there, cannot be read or does
    not hold what the check reads. Its published schema judges the file in the kit; an installed release carries the
    standard alone, so the check asks here only for the shape it relies on."""
    import yaml

    from gov.adopt import fabric

    try:
        path = fabric.shipped(REL, root)
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        standard = Standard(data)
        fault = _fault(data, standard)
    except GovError as error:
        raise CannotRun(error.message) from None
    except (OSError, ValueError, yaml.YAMLError, KeyError, TypeError, AttributeError) as error:
        raise CannotRun(f"{REL} cannot be read as the standard: {type(error).__name__}: {error}"[:400]) from None
    if fault:
        raise CannotRun(f"{REL} ({path}) is not the standard: {fault}")
    return standard


def _fault(data: dict, standard: Standard) -> str | None:
    """A value the check would misread, else None."""
    texts = [data["folders"], data["record_paths"], data["document_suffixes"], standard.stale_classes,
             data["secret_patterns"], data["generated_patterns"]]
    if not all(isinstance(each, list) and all(isinstance(text, str) and text for text in each) for each in texts):
        return "a list of names holds something else"
    if type(standard.version) is not int or standard.version < 1:
        return "version is no whole number of 1 or more"
    if not standard.classes or len(standard.classes) != len(data["classes"]):
        return "classes is empty or names a class twice"
    for name, entry in standard.classes.items():
        if not isinstance(entry["destination"], str) or entry["moves"] not in _MOVES or entry["memory"] not in _MEMORY:
            return f"class {name} lacks a destination, a move rule or a memory policy the check knows"
    if not all(each["class"] in standard.classes for each in data["fixed"]):
        return "a fixed pattern names no class of the list"
    if not all(type(standard.ceiling[key]) is int for key in ("import_chunks", "repository_chunks")):
        return "the study ceiling is no whole number"
    return None
