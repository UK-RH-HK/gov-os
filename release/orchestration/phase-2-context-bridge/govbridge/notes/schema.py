#!/usr/bin/env python3
"""Loads ``config/notes-schema.yaml`` (the single source of truth for the DERIVED_NOTE shape) and does structural
(shape/required-field) validation against it. Semantic checks -- does a source resolve in Git, does the hash match,
is the note being placed in section A -- live in ``govbridge.notes.validate``, which calls this module first and
never duplicates the field list it defines.
"""
from __future__ import annotations

from typing import Optional

from govbridge.core.yamlutil import load_yaml_file

NOTE_CLASS = "DERIVED_NOTE"


def default_schema_path() -> str:
    from govbridge import GOV_BRIDGE_DOMAIN
    import os
    return os.path.join(GOV_BRIDGE_DOMAIN, "config", "notes-schema.yaml")


def load_schema(path: Optional[str] = None) -> dict:
    return load_yaml_file(path or default_schema_path())


def _check_fields(record: dict, field_defs: dict, where: str, problems: list) -> None:
    if not isinstance(record, dict):
        problems.append(f"{where}: expected a mapping, got {type(record).__name__}")
        return
    for name, spec in field_defs.items():
        if spec.get("required") and name not in record:
            problems.append(f"{where}: missing required field {name!r}")
            continue
        if name not in record:
            continue
        value = record[name]
        const = spec.get("const")
        if const is not None and value != const:
            problems.append(f"{where}.{name}: expected constant {const!r}, got {value!r}")
        if spec.get("type") == "list" or str(spec.get("type", "")).startswith("list of"):
            if not isinstance(value, list):
                problems.append(f"{where}.{name}: expected a list, got {type(value).__name__}")
        elif spec.get("type") == "string" and not isinstance(value, str):
            problems.append(f"{where}.{name}: expected a string, got {type(value).__name__}")
        elif spec.get("type") == "sha256":
            if not isinstance(value, str) or len(value) != 64:
                problems.append(f"{where}.{name}: expected a 64-hex sha256 string, got {value!r}")


def structural_problems(note: dict, schema: Optional[dict] = None) -> list:
    """Every structural (shape/required-field) problem with ``note`` against ``config/notes-schema.yaml``. Returns
    an empty list when the note's shape is sound; does not touch Git or recompute any hash (that is
    ``govbridge.notes.validate``'s job) -- this function is pure and total over any dict."""
    schema = schema or load_schema()
    problems: list = []

    _check_fields(note, schema["fields"], "note", problems)

    claims = note.get("claims")
    if isinstance(claims, list):
        claim_fields = schema["claim_fields"]
        source_fields = schema["source_fields"]
        for i, claim in enumerate(claims):
            where = f"note.claims[{i}]"
            _check_fields(claim, claim_fields, where, problems)
            sources = claim.get("sources") if isinstance(claim, dict) else None
            if isinstance(sources, list):
                min_items = claim_fields.get("sources", {}).get("min_items", 0)
                if len(sources) < min_items:
                    problems.append(f"{where}.sources: has {len(sources)} source(s), a claim with no source is refused")
                for j, source in enumerate(sources):
                    _check_fields(source, source_fields, f"{where}.sources[{j}]", problems)
                    lines = source.get("lines") if isinstance(source, dict) else None
                    if lines is not None and (
                        not isinstance(lines, (list, tuple)) or len(lines) != 2
                        or not all(isinstance(x, int) for x in lines)
                        or lines[0] < 1 or lines[1] < lines[0]
                    ):
                        problems.append(f"{where}.sources[{j}].lines: expected [line_start, line_end], "
                                         f"1-indexed, line_start <= line_end, got {lines!r}")

    return problems
