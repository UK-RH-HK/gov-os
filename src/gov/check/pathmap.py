"""core-pathmap: every tracked path in exactly one namespace (path-map compliance).

A Gov OS project (one with ``governance/project/``) whose path map is missing, unreadable, unparsable or of a form
the schema does not state is a finding naming the cause, as is a repository git cannot list: never green (W2-95,
DEC-959 item 9). A namespace's ``lexical_policy`` is ``indexed`` or ``not indexed``, or absent; any other value, or
``not indexed`` with ``embedding_policy: embedded``, is such a finding (W2-13 S6, DEC-1066 (3)).
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import yaml

from gov.config.loader import LEXICAL_POLICY, lexical_policy_fault
from gov.util.gitenv import git_env

VERSION = "1.2.0"

PROJECT_REL = "governance/project"
PATH_MAP_REL = "governance/project/path-map.yaml"


def _finding(code: str, cause: str) -> list[dict]:
    return [{"code": code, "path": PATH_MAP_REL, "message": f"{PATH_MAP_REL}: {cause}"}]


def _git_ls_files(root: Path) -> list[str] | None:
    """The tracked paths, or None when git does not answer."""
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            capture_output=True, encoding="utf-8", errors="surrogateescape", check=True,
            env=git_env(root, pinned=True)
        )
        return [f for f in result.stdout.split("\0") if f]
    except (subprocess.CalledProcessError, OSError):
        return None


def _matches(path: str, pattern: str) -> bool:
    """``*`` stays inside one folder, ``**`` crosses folders (the language of the path map)."""
    parts = [re.escape(part).replace(r"\*", "[^/]*") for part in pattern.split("**")]
    return re.fullmatch(".*".join(parts), path) is not None


def _namespaces(data) -> list[tuple[str, list[str]]] | str:
    """Each namespace's name and patterns, in the mapping form the schema states or the older list form; else the cause."""
    if not isinstance(data, dict):
        return "its top level is not a map"
    if "namespaces" not in data:
        return "it has no namespaces"
    namespaces = data["namespaces"]
    if isinstance(namespaces, dict):
        entries = list(namespaces.items())
    elif isinstance(namespaces, list):
        entries = [(entry.get("name") if isinstance(entry, dict) else None, entry) for entry in namespaces]
    else:
        return "namespaces is neither a mapping of name to entry nor a list of entries"
    result = []
    for name, entry in entries:
        paths = entry.get("paths") if isinstance(entry, dict) else None
        if not (isinstance(name, str) and name and isinstance(paths, list) and paths
                and all(isinstance(p, str) and p for p in paths)):
            return f"namespace {name!r} is not a named entry whose paths are a non-empty list of patterns"
        fault = lexical_policy_fault(entry)
        if fault:
            return f"namespace {name!r} states {LEXICAL_POLICY} {entry[LEXICAL_POLICY]!r}: {fault}"
        result.append((name, paths))
    return result


def check(root: Path) -> list[dict]:
    root = Path(root)
    findings = []
    if not (root / PROJECT_REL).is_dir():
        return findings  # no Gov OS project: nothing declares a path map
    try:
        text = (root / PATH_MAP_REL).read_text(encoding="utf-8")
    except FileNotFoundError:
        return _finding("PATH_MAP_MISSING", "missing")
    except (OSError, UnicodeDecodeError) as exc:
        return _finding("PATH_MAP_UNREADABLE", f"cannot be read as UTF-8 text ({exc})")
    try:
        ns_patterns = _namespaces(yaml.safe_load(text))
    except yaml.YAMLError as exc:
        return _finding("PATH_MAP_INVALID", f"cannot be parsed ({exc})")
    if isinstance(ns_patterns, str):
        return _finding("PATH_MAP_INVALID", ns_patterns)

    tracked = _git_ls_files(root)
    if tracked is None:
        return [{"code": "TRACKED_PATHS_UNLISTED", "path": ".",
                 "message": f"git ls-files did not answer in {root}: the tracked paths cannot be judged"}]
    for filepath in tracked:
        matched = [name for name, patterns in ns_patterns if any(_matches(filepath, p) for p in patterns)]
        if len(matched) == 0:
            findings.append({
                "code": "PATH_NO_NAMESPACE",
                "path": filepath,
                "message": f"{filepath} matches no namespace in path-map.yaml"
            })
        elif len(matched) > 1:
            findings.append({
                "code": "PATH_MULTIPLE_NAMESPACES",
                "path": filepath,
                "namespaces": matched,
                "message": f"{filepath} matches {len(matched)} namespaces: {', '.join(matched)}"
            })
    return findings


if __name__ == "__main__":
    import sys
    root = Path.cwd()
    results = check(root)
    if results:
        print(json.dumps(results, indent=2))
        sys.exit(1)
    sys.exit(0)
