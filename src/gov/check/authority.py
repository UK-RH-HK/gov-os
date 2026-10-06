"""core-authority: authority/role limits check, wrapping the decision checker (CAP-01.c)."""
from __future__ import annotations

import json
from pathlib import Path

import yaml

VERSION = "1.0.0"

RECORD_PATHS = (".tickets", "docs/adr", "docs/research", "docs/lessons", "docs/changes")
NON_AUTHORITATIVE_TYPES = ("research", "lesson")


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


def _load_records(root: Path) -> dict[str, tuple[str, dict]]:
    records: dict[str, tuple[str, dict]] = {}
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
            records[str(front["id"])] = (rel, front)
    return records


def check(root: Path) -> list[dict]:
    root = Path(root)
    findings = []

    try:
        from gov.decisions.checker import check as decision_check
        decision_findings = decision_check(root)
        for f in decision_findings:
            code = f.get("code", "DECISION_FINDING")
            if code == "ACTIVE_UNAPPROVED":
                continue
            findings.append({"code": code,
                             "ids": f.get("ids", []), "paths": f.get("paths", []),
                             "message": f.get("message", "")})
    except ImportError:
        pass
    except Exception as exc:
        from gov.cli.errors import GovError
        if not isinstance(exc, GovError):
            findings.append({"code": "DECISION_CHECKER_ERROR",
                             "message": f"decision checker failed: {exc}"})

    records = _load_records(root)
    for record_id, (rel, front) in records.items():
        record_type = front.get("type", "")
        if record_type not in NON_AUTHORITATIVE_TYPES:
            continue
        for other_id, (other_rel, other_front) in records.items():
            if other_id == record_id:
                continue
            deps = _ids(other_front.get("depends_on"))
            sources = _ids(other_front.get("sources"))
            citing_refs = deps + sources
            if record_id in citing_refs:
                other_type = other_front.get("type", "")
                if other_type in ("decision", "task") or other_type.startswith("decision"):
                    findings.append({
                        "code": "AUTHORITY_CLASS_VIOLATION",
                        "ids": [record_id, other_id],
                        "paths": [rel, other_rel],
                        "message": f"{record_id} (type {record_type}) is cited by "
                                   f"{other_id} (type {other_type}) as if it were authoritative"
                    })

    for record_id, (rel, front) in records.items():
        status = front.get("status", "")
        if status != "SUPERSEDED":
            continue
        for other_id, (other_rel, other_front) in records.items():
            if other_id == record_id:
                continue
            sources = _ids(other_front.get("sources"))
            if record_id in sources:
                other_status = other_front.get("status", "")
                if other_status not in ("closed", "SUPERSEDED", "DECLINED", "REVOKED"):
                    findings.append({
                        "code": "SUPERSEDED_SATISFYING_REQUIREMENT",
                        "ids": [record_id, other_id],
                        "paths": [rel, other_rel],
                        "message": f"{record_id} is SUPERSEDED but satisfies a requirement of {other_id}"
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
