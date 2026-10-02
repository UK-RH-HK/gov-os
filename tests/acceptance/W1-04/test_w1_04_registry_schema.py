"""W1-04 — the tool-registry schema requires the six facts of an approved install.

KPI success 3: "The tool-registry schema requires version, sha256, install and
uninstall commands, date and approving decision id" [CAP-25.a].

DEC-121 accepted the test designer's schema; these tests are its record:

- one file, ``tool-registry.schema.json``, a JSON Schema of draft 2020-12, as
  the schemas under ``schemas/records/`` are;
- a registry is a mapping with a ``tools`` list;
- each entry requires ``name``, ``version``, ``sha256``, ``install``,
  ``uninstall``, ``date`` and ``approved_by`` (a decision id such as
  ``DEC-083``).

DEC-127: the schema lives in the kernel template, at
``template/governance/kernel/schemas/``. The registry itself is project data at
``governance/project/tool-registry.yaml``; W1-04 ships no registry file, and
W1-06 creates it at the first install.

"Requires" is tested by giving the schema a registry with one fact missing and
expecting it to be refused. The registry is YAML on disk; the schema judges the
data it holds, so the tests build that data directly.
"""

from __future__ import annotations

import copy
import hashlib

import pytest

import w1_04_schema as validator
import w1_04_support as support

REQUIRED = ("name", "version", "sha256", "install", "uninstall", "date", "approved_by")

ENTRY = {
    "name": "ccusage",
    "version": "17.1.0",
    "sha256": hashlib.sha256(b"ccusage-17.1.0.tgz").hexdigest(),
    "install": "npm install -g ccusage@17.1.0",
    "uninstall": "npm uninstall -g ccusage",
    "date": "2026-10-02",
    "approved_by": "DEC-083",
}
SECOND_ENTRY = {
    "name": "ruff",
    "version": "0.6.9",
    "sha256": hashlib.sha256(b"ruff-0.6.9.tar.gz").hexdigest(),
    "install": "uv tool install ruff==0.6.9",
    "uninstall": "uv tool uninstall ruff",
    "date": "2026-10-03",
    "approved_by": "DEC-083",
}


def _registry(*entries):
    return {"tools": [copy.deepcopy(entry) for entry in entries]}


def test_the_schema_is_the_one_tool_registry_file_of_the_kernel_schemas(schema):
    directory = support.REPO_ROOT / support.SCHEMA_DIR_REL
    names = sorted(p.name for p in directory.glob(support.SCHEMA_GLOB))
    assert names == [support.SCHEMA_NAME], (
        f"{support.SCHEMA_DIR_REL}/{support.SCHEMA_GLOB} matches {names}; expected {support.SCHEMA_NAME} alone"
    )


def test_the_schema_is_a_json_schema_of_draft_2020_12(schema):
    assert isinstance(schema, dict), "the schema file does not hold a JSON object"
    assert schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", (
        f"$schema is {schema.get('$schema')!r}, not draft 2020-12 as in schemas/records/"
    )


def test_a_complete_registry_is_accepted(schema):
    for registry in (_registry(ENTRY), _registry(ENTRY, SECOND_ENTRY)):
        found = validator.errors(registry, schema)
        assert found == [], f"a registry whose entries hold all seven keys was refused: {found}"


@pytest.mark.parametrize("field", REQUIRED)
def test_an_entry_without_a_required_fact_is_refused(schema, field):
    registry = _registry(ENTRY, SECOND_ENTRY)
    del registry["tools"][1][field]
    assert validator.errors(registry, schema), (
        f"a registry entry without `{field}` was accepted: the schema does not require it"
    )


def test_a_registry_without_a_tools_list_is_refused(schema):
    shapes = {
        "an empty mapping": {},
        "a list of entries with no `tools` key": [copy.deepcopy(ENTRY)],
        "`tools` as one entry instead of a list": {"tools": copy.deepcopy(ENTRY)},
        "an entry that is a name instead of a mapping": {"tools": ["ccusage"]},
    }
    for name, registry in shapes.items():
        assert validator.errors(registry, schema), f"{name} was accepted as a registry"


def test_the_kernel_template_ships_no_registry_file(schema):
    """DEC-127: the registry is project data, created by W1-06 at the first install."""
    template = support.REPO_ROOT / "template"
    shipped = sorted(str(p.relative_to(support.REPO_ROOT)) for p in template.rglob("tool-registry*")
                     if p.name != support.SCHEMA_NAME)
    assert shipped == [], f"the kernel template ships a registry file: {shipped}"
