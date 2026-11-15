"""W2-174 r2b (r2's F1; DEC-802, DEC-1189 (1)): the ticket schemas the Verify pass reads are in the wheel.

Regression evidence only (DEC-136). ``verify_pass._validator`` reads ``ticket.schema.json`` and ``common.schema.json``
from gov's source tree, else from ``<gov>/_shipped/template/governance/kernel/schemas/``: the two copies there are
byte-identical to the kernel's, listed in ``pyproject.toml``'s package data under ``"gov"``, and ``jsonschema`` is a
declared dependency. S29's scan cannot see them (verify_pass calls no ``shipped``), so this file checks them by name,
with S29's ``problems``.
"""
from __future__ import annotations

import re
import tomllib

from .test_w2_88_s29 import PACKAGE_DIR, REPO, SHIPPED_DIR, package_data, problems

from gov.adopt import verify_pass

RELS = [(verify_pass.SCHEMA_REL / name).as_posix() for name in verify_pass.SCHEMA_FILES]


# ---- the fast check

def test_the_two_schemas_are_shipped_byte_identical_and_listed_in_the_package_data():
    assert RELS == ["template/governance/kernel/schemas/ticket.schema.json",
                    "template/governance/kernel/schemas/common.schema.json"]
    assert problems(RELS, REPO, SHIPPED_DIR, package_data(), PACKAGE_DIR) == []


def test_jsonschema_is_a_declared_dependency():
    dependencies = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))["project"]["dependencies"]
    names = [re.split(r"[<>=!~\[; ]", item, maxsplit=1)[0].strip().lower() for item in dependencies]
    assert "jsonschema" in names, dependencies
    assert "pyyaml" in names, dependencies
