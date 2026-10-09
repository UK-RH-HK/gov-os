"""core-schema: validate record frontmatter against JSON schemas (schema/invariants)."""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

VERSION = "1.0.0"

RECORD_PATHS = (".tickets", "docs")
SCHEMA_DIR = "template/governance/kernel/schemas"
# The kernel's two layouts (DEC-579): a record is held to the schemas of each layout the project holds.
SCHEMA_DIRS = (SCHEMA_DIR, "governance/kernel/schemas")

SCHEMA_MAP = {
    "task": "ticket.schema.json",
    "decision": "madr.schema.json",
    "decision-package": "decision-package.schema.json",
    "research": "research.schema.json",
    "failure": "failure.schema.json",
    "lesson": "lesson.schema.json",
    "checkpoint": "checkpoint.schema.json",
    "probe": "probe.schema.json",
}

# A type whose schema stands alone (DEC-565): the shared frontmatter is not owed by its records, and each
# field a record states is held to the shape the schema gives.
STANDALONE_TYPES = ("probe",)

_JSON_TYPES = {"string": str, "boolean": bool}
_SHAPE_KEYWORDS = {"description", "const", "enum", "type", "minLength", "pattern"}


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


def _load_schema(root: Path, schema_dir: str, schema_file: str) -> dict | None:
    path = root / schema_dir / schema_file
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


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


def _resolve(spec: dict, schema: dict, common: dict | None) -> dict | None:
    """The shape a property names: itself, or the definition its ``$ref`` points to here or in the common file."""
    ref = spec.get("$ref")
    if ref is None:
        return spec
    source, _, name = ref.partition("#/$defs/")
    owner = schema if not source else common if source == "common.schema.json" else None
    target = (owner or {}).get("$defs", {}).get(name)
    return target if isinstance(target, dict) else None


def _shape_fault(value, shape: dict | None) -> str | None:
    """Why ``value`` does not have ``shape``, or None. A shape this check cannot read is a fault, never a pass."""
    if shape is None or set(shape) - _SHAPE_KEYWORDS or shape.get("type", "string") not in _JSON_TYPES:
        return "has a shape the check cannot measure"
    if "const" in shape and value != shape["const"]:
        return f"is not {shape['const']!r}"
    if "enum" in shape and not any(value == word and type(value) is type(word) for word in shape["enum"]):
        return f"is not one of {shape['enum']}"
    if "type" in shape and not isinstance(value, _JSON_TYPES[shape["type"]]):
        return f"is not a {shape['type']}"
    if isinstance(value, str):
        if len(value) < shape.get("minLength", 0):
            return "is empty"
        if "pattern" in shape and not re.search(shape["pattern"], value):
            return f"does not match {shape['pattern']}"
    return None


def _validate_shapes(front: dict, schema: dict, common: dict | None, rel: str) -> list[dict]:
    findings = []
    for field, spec in schema.get("properties", {}).items():
        if field not in front:
            continue
        fault = _shape_fault(front[field], _resolve(spec, schema, common))
        if fault:
            findings.append({"code": "SCHEMA_INVALID_FIELD", "path": rel, "field": field,
                             "message": f"{rel}: field '{field}' {fault}"})
    return findings


def check(root: Path) -> list[dict]:
    root = Path(root)
    findings = []
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
            standalone = record_type in STANDALONE_TYPES
            if not standalone:
                for field in ("id", "type", "status", "state_class"):
                    if field not in front:
                        findings.append({"code": "SCHEMA_MISSING_FIELD", "path": rel, "field": field,
                                         "message": f"{rel}: missing required field '{field}'"})
            schema_file = SCHEMA_MAP.get(record_type)
            if schema_file:
                measured, held = False, []
                for schema_dir in SCHEMA_DIRS:
                    schema = _load_schema(root, schema_dir, schema_file)
                    if not schema:
                        continue
                    measured = True
                    common = _load_schema(root, schema_dir, "common.schema.json")
                    found = _validate(front, schema, common, rel)
                    if standalone:
                        found.extend(_validate_shapes(front, schema, common, rel))
                    # a finding under either layout is a finding; one both layouts give is not doubled
                    held += [finding for finding in found if finding not in held]
                findings.extend(held)
                if standalone and not measured:
                    findings.append({"code": "SCHEMA_UNREADABLE", "path": rel, "type": record_type,
                                     "message": f"{rel}: unmeasured, the schema {schema_file} cannot be read"})
            else:
                findings.append({"code": "SCHEMA_UNKNOWN_TYPE", "path": rel,
                                 "type": record_type,
                                 "message": f"{rel}: unknown record type '{record_type}'"})
    return findings


if __name__ == "__main__":
    import sys
    root = Path.cwd()
    results = check(root)
    if results:
        print(json.dumps(results, indent=2))
        sys.exit(1)
    sys.exit(0)
