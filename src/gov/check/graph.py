"""core-graph: check graph structural properties (graph integrity)."""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

VERSION = "1.0.0"

RECORD_PATHS = (".tickets", "docs/adr", "docs/research", "docs/lessons", "docs/changes")
GENERAL_ID = re.compile(r"^[A-Za-z0-9]+-[A-Za-z0-9._-]+$")


def _frontmatter(text: str) -> dict | None:
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = lines.index("---", 1)
    except ValueError:
        return None
    try:
        front = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError:
        return None
    return front if isinstance(front, dict) else None


def _ids(value) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(v) for v in value if v]
    return []


def check(root: Path) -> list[dict]:
    root = Path(root)
    findings = []
    records: dict[str, list[str]] = {}
    edges: list[tuple[str, str]] = []
    all_fronts: list[tuple[str, str, dict]] = []

    for record_dir in RECORD_PATHS:
        base = root / record_dir
        if not base.is_dir():
            continue
        for md_file in sorted(base.rglob("*.md")):
            rel = str(md_file.relative_to(root))
            try:
                text = md_file.read_text(encoding="utf-8")
            except OSError:
                continue
            front = _frontmatter(text)
            if front is None or "id" not in front:
                continue
            record_id = str(front["id"])
            record_type = str(front.get("type", ""))
            records.setdefault(record_id, []).append(rel)
            all_fronts.append((rel, record_id, front))
            if not GENERAL_ID.fullmatch(record_id):
                findings.append({"code": "ID_OUTSIDE_GRAMMAR", "path": rel, "id": record_id,
                                 "message": f"{rel}: id '{record_id}' does not match any id grammar"})
            for dep in _ids(front.get("depends_on")):
                edges.append((record_id, dep))
            for dep in _ids(front.get("supersedes")):
                edges.append((record_id, dep))

    for record_id, paths in records.items():
        if len(paths) > 1:
            findings.append({"code": "DUPLICATE_ID", "id": record_id, "paths": paths,
                             "message": f"{record_id} appears in {len(paths)} files"})

    all_ids = set(records.keys())
    for source, target in edges:
        if target not in all_ids:
            findings.append({"code": "DANGLING_REFERENCE", "source": source, "target": target,
                             "message": f"{source} depends on {target} which does not exist"})

    graph: dict[str, set[str]] = {}
    for source, target in edges:
        graph.setdefault(source, set()).add(target)

    def has_cycle(start: str) -> bool:
        visited: set[str] = set()
        stack: set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            stack.add(node)
            for neighbor in graph.get(node, ()):
                if neighbor in stack:
                    return True
                if neighbor not in visited and dfs(neighbor):
                    return True
            stack.discard(node)
            return False

        return dfs(start)

    checked: set[str] = set()
    for node in graph:
        if node not in checked:
            if has_cycle(node):
                findings.append({"code": "DAG_CYCLE", "id": node,
                                 "message": f"cycle detected in dependency graph involving {node}"})
            checked.add(node)

    return findings


if __name__ == "__main__":
    import sys
    root = Path.cwd()
    results = check(root)
    if results:
        print(json.dumps(results, indent=2))
        sys.exit(1)
    sys.exit(0)
