"""core-claims: ticket DAG, field completeness, gap tickets, taxonomy change (concurrency/claims)."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import yaml

VERSION = "1.0.0"

TICKETS_REL = ".tickets"
REQUIRED_TICKET_FIELDS = ("id", "type", "status", "state_class", "role", "allowed_paths", "kpis")
READINESS_DIMENSIONS_REL = "docs/contract/readiness-dimensions.yaml"
CHANGES_REL = "openspec/changes"


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


def _load_tickets(root: Path) -> list[tuple[str, dict]]:
    tickets = []
    tickets_dir = root / TICKETS_REL
    if not tickets_dir.is_dir():
        return tickets
    for md_file in sorted(tickets_dir.glob("*.md")):
        try:
            text = md_file.read_text(encoding="utf-8")
        except OSError:
            continue
        front = _frontmatter(text)
        if front is None:
            continue
        rel = str(md_file.relative_to(root))
        tickets.append((rel, front))
    return tickets


def _check_ticket_dag(tickets: list[tuple[str, dict]]) -> list[dict]:
    findings = []
    id_to_wbs: dict[str, str] = {}
    for rel, front in tickets:
        wbs = front.get("wbs_id")
        ticket_id = str(front.get("id", ""))
        if wbs and ticket_id:
            id_to_wbs[ticket_id] = str(wbs)

    graph: dict[str, set[str]] = {}
    for rel, front in tickets:
        wbs = str(front.get("wbs_id", front.get("id", "")))
        deps = _ids(front.get("depends_on"))
        graph.setdefault(wbs, set())
        for dep in deps:
            resolved = id_to_wbs.get(dep, dep)
            graph[wbs].add(resolved)

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

    for node in list(graph.keys()):
        if node not in visited and dfs(node):
            findings.append({
                "code": "TICKET_DAG_CYCLE",
                "id": node,
                "message": f"cycle in ticket dependency graph involving {node}"
            })

    return findings


def _check_ticket_fields(tickets: list[tuple[str, dict]]) -> list[dict]:
    findings = []
    for rel, front in tickets:
        for field in REQUIRED_TICKET_FIELDS:
            if field not in front:
                findings.append({
                    "code": "TICKET_MISSING_FIELD",
                    "path": rel,
                    "id": str(front.get("id", "")),
                    "field": field,
                    "message": f"{rel}: missing required field '{field}'"
                })
    return findings


def _check_gap_tickets(root: Path, tickets: list[tuple[str, dict]]) -> list[dict]:
    findings = []
    changes_dir = root / CHANGES_REL
    if not changes_dir.is_dir():
        return findings

    ticket_ids: dict[str, str] = {}
    for rel, front in tickets:
        tid = str(front.get("id", ""))
        status = str(front.get("status", "")).lower()
        if tid:
            ticket_ids[tid] = status

    for folder in sorted(changes_dir.glob("*")):
        if not folder.is_dir() or folder.name == "archive":
            continue
        readiness_file = folder / "readiness.yaml"
        if not readiness_file.is_file():
            continue
        try:
            data = yaml.safe_load(readiness_file.read_text(encoding="utf-8"))
        except (yaml.YAMLError, OSError):
            continue
        if not isinstance(data, dict):
            continue
        rows = data.get("rows", [])
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            state = row.get("state", "")
            if state != "MISSING":
                continue
            gap_ticket = row.get("gap_ticket")
            if not gap_ticket or gap_ticket == "UNLINKED":
                findings.append({
                    "code": "GAP_TICKET_MISSING",
                    "path": str(readiness_file.relative_to(root)),
                    "row": row.get("key", row.get("n", "")),
                    "message": f"required MISSING row has no valid gap_ticket (got {gap_ticket!r})"
                })
            elif gap_ticket not in ticket_ids:
                findings.append({
                    "code": "GAP_TICKET_NOT_FOUND",
                    "path": str(readiness_file.relative_to(root)),
                    "row": row.get("key", row.get("n", "")),
                    "gap_ticket": gap_ticket,
                    "message": f"gap_ticket {gap_ticket} does not exist"
                })
            elif ticket_ids[gap_ticket] == "closed":
                findings.append({
                    "code": "GAP_TICKET_CLOSED",
                    "path": str(readiness_file.relative_to(root)),
                    "row": row.get("key", row.get("n", "")),
                    "gap_ticket": gap_ticket,
                    "message": f"gap_ticket {gap_ticket} is closed"
                })

    return findings


def _check_taxonomy_change(root: Path) -> list[dict]:
    findings = []
    dims_path = root / READINESS_DIMENSIONS_REL
    if not dims_path.is_file():
        return findings
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "log", "--oneline", "-1", "--", READINESS_DIMENSIONS_REL],
            capture_output=True, text=True
        )
        if result.returncode != 0 or not result.stdout.strip():
            return findings
        diff_result = subprocess.run(
            ["git", "-C", str(root), "diff", "HEAD~1", "--", READINESS_DIMENSIONS_REL],
            capture_output=True, text=True
        )
        if diff_result.returncode != 0 or not diff_result.stdout.strip():
            return findings
    except (subprocess.CalledProcessError, OSError):
        return findings

    cite_records = []
    for search_dir in ("docs/changes", "docs/adr"):
        base = root / search_dir
        if not base.is_dir():
            continue
        for md_file in base.rglob("*.md"):
            try:
                text = md_file.read_text(encoding="utf-8")
            except OSError:
                continue
            front = _frontmatter(text)
            if front is None:
                continue
            record_type = front.get("type", "")
            if "change-execution" in record_type or "CIT-E" in str(front.get("id", "")):
                target = front.get("target", "")
                if READINESS_DIMENSIONS_REL in str(target) or not target:
                    cite_records.append(front)

    if not cite_records:
        findings.append({
            "code": "TAXONOMY_CHANGE_NO_CITE",
            "path": READINESS_DIMENSIONS_REL,
            "message": f"{READINESS_DIMENSIONS_REL} changed without a linked CIT-E record"
        })

    return findings


def check(root: Path) -> list[dict]:
    root = Path(root)
    findings = []
    tickets = _load_tickets(root)
    findings.extend(_check_ticket_dag(tickets))
    findings.extend(_check_ticket_fields(tickets))
    findings.extend(_check_gap_tickets(root, tickets))
    findings.extend(_check_taxonomy_change(root))
    return findings


if __name__ == "__main__":
    import sys
    root = Path.cwd()
    results = check(root)
    if results:
        print(json.dumps(results, indent=2))
        sys.exit(1)
    sys.exit(0)
