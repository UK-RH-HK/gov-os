"""A ticket's criticality (RUBRIC-2 at launch, W2-184; DEC-1120 (1), DEC-1167 (2)).

``governance/project/criticality.yaml`` holds the project's rules: a default class, the Opus model a promotion and a
FULL ticket's probe use, and a list of rules, each giving a class (C0..C3) to the tickets whose ``allowed_paths`` match
its globs or whose ``profile`` it names. A ticket's criticality is the highest class among the rules that match, the
default when none does. The ticket's ``class`` key is never read: it is the ticket's kind. The file is read at each
call; one that cannot be read or is not of the stated form refuses the launch (fail closed). A launch of a project with
no file at all does not call here: it is as before W2-184 (interface 1.4, amended 2026-11-14; DEC-1167 (2)). Called
directly with no file, ``ticket_criticality`` and ``opus_model`` refuse (1.3).
"""

from __future__ import annotations

import fnmatch
import os
import re
from pathlib import Path

import yaml

from gov.cli.errors import GovError
from gov.util.parts import load_yaml_unique

REL = "governance/project/criticality.yaml"
CLASSES = ("C0", "C1", "C2", "C3")  # lowest first: the position is the rank
PROFILES = ("FULL", "STANDARD", "LITE")
OPUS = re.compile(r"claude-opus(?:-[a-z0-9]+)+")
_KEYS = frozenset({"version", "default", "opus", "rules"})
_COMMENT = re.compile(r"\s+#.*$")


def _refuse(reason: str) -> GovError:
    return GovError("LAUNCH_REFUSED", f"{REL}: {reason}")


def exists(root: Path) -> bool:
    """True when the file is there (a link counts), whether or not it is well formed."""
    return os.path.lexists(root / REL)


def _rule(rule: object, index: int) -> None:
    where = f"rule {index}"
    if not isinstance(rule, dict):
        raise _refuse(f"{where} is not a map")
    keys = set(rule)
    if "class" not in keys or keys - {"class", "paths", "profile"} or len(keys & {"paths", "profile"}) != 1:
        raise _refuse(f"{where} must hold 'class' and exactly one of 'paths' or 'profile', and no other key")
    if rule["class"] not in CLASSES:
        raise _refuse(f"{where}: class is one of {', '.join(CLASSES)}")
    if "profile" in rule and rule["profile"] not in PROFILES:
        raise _refuse(f"{where}: profile is one of {', '.join(PROFILES)}")
    if "paths" in rule:
        paths = rule["paths"]
        if not isinstance(paths, list) or not paths or not all(isinstance(p, str) and p for p in paths):
            raise _refuse(f"{where}: paths is a non-empty list of non-empty strings")


def load(root: Path) -> dict:
    """The file read and checked whole; a refusal names it."""
    try:
        data = load_yaml_unique((Path(root) / REL).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        raise _refuse("cannot be read, is not YAML, or writes a key twice") from None
    if not isinstance(data, dict) or set(data) != _KEYS:
        raise _refuse(f"must be a map with exactly the keys {', '.join(sorted(_KEYS))}")
    if data["version"] != 1 or isinstance(data["version"], bool):
        raise _refuse("version must be the integer 1")
    if data["default"] not in CLASSES:
        raise _refuse(f"default is one of {', '.join(CLASSES)}")
    if not isinstance(data["opus"], str) or not OPUS.fullmatch(data["opus"]):
        raise _refuse("opus must be an Opus model id (claude-opus-...)")
    if not isinstance(data["rules"], list):
        raise _refuse("rules must be a list")
    for index, rule in enumerate(data["rules"]):
        _rule(rule, index)
    return data


def _matches(glob: str, path: str) -> bool:
    """Either one, read as an fnmatch pattern (``*`` crosses ``/``), matches the other as a string."""
    return fnmatch.fnmatchcase(path, glob) or fnmatch.fnmatchcase(glob, path)


def ticket_criticality(root: Path, ticket: dict) -> str:
    """The highest class among the rules that match ``ticket`` (its front-matter map); the default when none does."""
    data = load(root)
    allowed = ticket.get("allowed_paths") if isinstance(ticket, dict) else None
    paths = [_COMMENT.sub("", p) for p in allowed if isinstance(p, str)] if isinstance(allowed, list) else []
    profile = ticket.get("profile") if isinstance(ticket, dict) else None
    found = []
    for rule in data["rules"]:
        if "profile" in rule:
            hit = profile == rule["profile"]
        else:
            hit = any(_matches(glob, path) for glob in rule["paths"] for path in paths)
        if hit:
            found.append(rule["class"])
    return max(found, key=CLASSES.index, default=data["default"])


def opus_model(root: Path) -> str:
    """The Opus model a promotion and a FULL ticket's probe use."""
    return load(root)["opus"]
