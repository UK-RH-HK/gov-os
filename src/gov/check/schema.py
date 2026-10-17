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
    # the record types in use beside them (DEC-612, DEC-620): each owes the shared frontmatter and nothing more
    "change-execution-record": "change-execution-record.schema.json",
    "change-impact-proposal": "change-impact-proposal.schema.json",
    "capability": "capability.schema.json",
    "specification": "specification.schema.json",
    "plan": "plan.schema.json",
    # the record types of W2-02: the close record gov close writes, an audit report in DEC-441's form, and the
    # adoption verdict of CAP-44.h (DEC-722); a decision entry (register-entry) has a schema and no record file
    # (DEC-274)
    "close": "close.schema.json",
    "audit-report": "audit-report.schema.json",
    "adoption-verdict": "adoption-verdict.schema.json",
}

# A type whose schema stands alone (DEC-565): its records owe what the schema requires, the shared frontmatter
# only where the schema takes it in, and each field a record states is held to the shape the schema gives. The
# audit report's form has no shared frontmatter (DEC-441); the adoption verdict is held to its three verdicts.
STANDALONE_TYPES = ("probe", "audit-report", "adoption-verdict")

# The audit-report folder (DEC-626, the audit-reproducibility declaration): a record there that states no `type`
# is an audit report.
AUDIT_REPORT_DIR, AUDIT_REPORT_TYPE = "docs/audit", "audit-report"

_JSON_TYPES = {"string": str, "boolean": bool, "array": list, "object": dict}
_SHAPE_KEYWORDS = {"description", "const", "enum", "type", "minLength", "pattern"}
# What a list or a map adds, and no more (DEC-741 I (ii), the verdict's named conditions): a list's items; a map's
# properties, the keys it requires, and one conditional, an `if` that tests constants and the `then` it brings.
_NESTED_KEYWORDS = {"array": {"items"}, "object": {"properties", "required", "if", "then"}}
_UNMEASURABLE = "has a shape the check cannot measure"


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
    if not isinstance(spec, dict):
        return None
    ref = spec.get("$ref")
    if ref is None:
        return spec
    source, _, name = str(ref).partition("#/$defs/")
    owner = schema if not source else common if source == "common.schema.json" else None
    target = (owner or {}).get("$defs", {}).get(name)
    return target if isinstance(target, dict) else None


def _tested_constants(test) -> dict | None:
    """``{key: constant}`` an ``if`` tests, or None when the ``if`` is not a test of constants on properties."""
    tests = test.get("properties") if isinstance(test, dict) and set(test) == {"properties"} else None
    if not isinstance(tests, dict) or not tests \
            or any(not isinstance(each, dict) or set(each) != {"const"} for each in tests.values()):
        return None
    return {key: each["const"] for key, each in tests.items()}


def _shape_fault(value, shape: dict | None, schema: dict, common: dict | None, where: str) -> tuple | None:
    """Where and why ``value`` does not have ``shape``, or None; ``where`` is the place, as ``conditions[1].state``.
    A shape this check cannot read is a fault, never a pass, at every depth."""
    kind = shape.get("type", "string") if isinstance(shape, dict) else None
    if not isinstance(kind, str) or kind not in _JSON_TYPES \
            or set(shape) - _SHAPE_KEYWORDS - _NESTED_KEYWORDS.get(kind, set()):
        return where, _UNMEASURABLE
    required, properties = shape.get("required", []), shape.get("properties", {})
    if not isinstance(required, list) or not all(isinstance(key, str) for key in required) \
            or not isinstance(properties, dict):
        return where, _UNMEASURABLE
    # the one conditional: an `if` that tests constants on properties, and its `then`; any other is unread
    if ("if" in shape or "then" in shape) \
            and (_tested_constants(shape.get("if")) is None or not isinstance(shape.get("then"), dict)):
        return where, _UNMEASURABLE
    if "const" in shape and value != shape["const"]:
        return where, f"is not {shape['const']!r}"
    if "enum" in shape and not any(value == word and type(value) is type(word) for word in shape["enum"]):
        return where, f"is not one of {shape['enum']}"
    if "type" in shape and not isinstance(value, _JSON_TYPES[shape["type"]]):
        return where, f"is not a {shape['type']}"
    if isinstance(value, str):
        if len(value) < shape.get("minLength", 0):
            return where, "is empty"
        if "pattern" in shape and not re.search(shape["pattern"], value):
            return where, f"does not match {shape['pattern']}"
    if kind == "array" and "items" in shape:
        items = _resolve(shape["items"], schema, common)
        if items is None:
            return where, _UNMEASURABLE
        for index, item in enumerate(value):
            fault = _shape_fault(item, items, schema, common, f"{where}[{index}]")
            if fault:
                return fault
    if kind == "object":
        for key in required:
            if key not in value:
                return where, f"has no '{key}'"
        for key, spec in properties.items():
            fault = _shape_fault(value[key], _resolve(spec, schema, common), schema, common, f"{where}.{key}") \
                if key in value else None
            if fault:
                return fault
        # as JSON Schema reads it, the `if` holds when each key it tests is absent or has its constant
        tests = _tested_constants(shape.get("if")) or {}
        if tests and all(key not in value or value[key] == const for key, const in tests.items()):
            return _shape_fault(value, {"type": "object", **shape["then"]}, schema, common, where)
    return None


def _validate_shapes(front: dict, schema: dict, common: dict | None, rel: str) -> list[dict]:
    findings = []
    for field, spec in schema.get("properties", {}).items():
        if field not in front:
            continue
        fault = _shape_fault(front[field], _resolve(spec, schema, common), schema, common, field)
        if fault:
            # a fault inside a list or a map is the top-level field's, and its message says where inside it
            where, why = fault
            place = "" if where == field else f": {where}"
            findings.append({"code": "SCHEMA_INVALID_FIELD", "path": rel, "field": field,
                             "message": f"{rel}: field '{field}'{place} {why}"})
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
            in_audit_dir = md_file.is_relative_to(root / AUDIT_REPORT_DIR)
            record_type = front.get("type", AUDIT_REPORT_TYPE if in_audit_dir else None)
            if not isinstance(record_type, str):
                findings.append({"code": "SCHEMA_INVALID_TYPE", "path": str(rel),
                                 "message": f"{rel}: 'type' field is missing or not a string"})
                continue
            standalone = record_type in STANDALONE_TYPES
            owed = []
            if not standalone:
                for field in ("id", "type", "status", "state_class"):
                    if field not in front:
                        owed.append({"code": "SCHEMA_MISSING_FIELD", "path": rel, "field": field,
                                     "message": f"{rel}: missing required field '{field}'"})
            schema_file = SCHEMA_MAP.get(record_type)
            if schema_file:
                measured, held = False, owed  # a shared field the schema asks for too is one finding
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
                if not measured:
                    findings.append({"code": "SCHEMA_UNREADABLE", "path": rel, "type": record_type,
                                     "message": f"{rel}: unmeasured, the schema {schema_file} cannot be read"})
            else:
                findings.extend(owed)
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
