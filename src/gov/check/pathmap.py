"""core-pathmap: every tracked path in exactly one namespace (path-map compliance)."""
from __future__ import annotations

import fnmatch
import json
import subprocess
from pathlib import Path

import yaml

VERSION = "1.0.0"

PATH_MAP_REL = "governance/project/path-map.yaml"


def _git_ls_files(root: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            capture_output=True, text=True, check=True
        )
        return [f for f in result.stdout.split("\0") if f]
    except (subprocess.CalledProcessError, OSError):
        return []


def _matches(path: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
    return False


def check(root: Path) -> list[dict]:
    root = Path(root)
    findings = []
    path_map_file = root / PATH_MAP_REL
    if not path_map_file.is_file():
        return findings
    try:
        data = yaml.safe_load(path_map_file.read_text(encoding="utf-8"))
    except (yaml.YAMLError, OSError):
        return findings
    if not isinstance(data, dict):
        return findings

    namespaces = data.get("namespaces", [])
    if not isinstance(namespaces, list):
        return findings

    ns_patterns: list[tuple[str, list[str]]] = []
    for ns in namespaces:
        if isinstance(ns, dict):
            name = ns.get("name", "")
            paths = ns.get("paths", [])
            if isinstance(paths, list):
                ns_patterns.append((name, [str(p) for p in paths]))

    tracked = _git_ls_files(root)
    for filepath in tracked:
        matched = [name for name, patterns in ns_patterns if _matches(filepath, patterns)]
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
