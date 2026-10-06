"""core-schema: validate record frontmatter against JSON schemas (schema/invariants)."""
from __future__ import annotations

import json
from pathlib import Path

import yaml

VERSION = "1.0.0"

RECORD_PATHS = (".tickets", "docs/adr", "docs/research", "docs/lessons", "docs/changes")
SCHEMA_DIR = "template/governance/kernel/schemas"

SCHEMA_MAP = {
    "task": "ticket.schema.json",
    "decision": "madr.schema.json",
    "decision-package": "decision-package.schema.json",
    "research": "research.schema.json",
    "failure": "failure.schema.json",
    "lesson": "lesson.schema.json",
    "checkpoint": "checkpoint.schema.json",
}


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


def _load_schema(root: Path, schema_file: str) -> dict | None:
    path = root / SCHEMA_DIR / schema_file
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _load_common(root: Path) -> dict | None:
    return _load_schema(root, "common.schema.json")


def _validate(front: dict, schema: dict, common: dict | None, rel: str) -> list[dict]:
    findings = []
    required = schema.get("required", [])
    all_of = schema.get("allOf", [])
    for ref_entry in all_of:
        ref = ref_entry.get("$ref", "")
        if "frontmatter" in ref and common:
            fm_def = common.get("$defs", {}).get("frontmatter", {})
            required = list(set(required) | set(fm_def.get("required", [])))
    for field in required:
        if field not in front:
            findings.append({"code": "SCHEMA_MISSING_FIELD", "path": rel, "field": field,
                             "message": f"{rel}: missing required field '{field}'"})
    return findings


def check(root: Path) -> list[dict]:
    root = Path(root)
    findings = []
    common = _load_common(root)
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
            if front is None:
                continue
            record_type = front.get("type")
            if not isinstance(record_type, str):
                findings.append({"code": "SCHEMA_INVALID_TYPE", "path": str(rel),
                                 "message": f"{rel}: 'type' field is missing or not a string"})
                continue
            for field in ("id", "type", "status", "state_class"):
                if field not in front:
                    findings.append({"code": "SCHEMA_MISSING_FIELD", "path": rel, "field": field,
                                     "message": f"{rel}: missing required field '{field}'"})
            schema_file = SCHEMA_MAP.get(record_type)
            if schema_file:
                schema = _load_schema(root, schema_file)
                if schema:
                    findings.extend(_validate(front, schema, common, rel))
    return findings


if __name__ == "__main__":
    import sys
    root = Path.cwd()
    results = check(root)
    if results:
        print(json.dumps(results, indent=2))
        sys.exit(1)
    sys.exit(0)
