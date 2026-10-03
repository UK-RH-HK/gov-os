"""W1-06 — the registry file itself: committed, valid, and every entry complete.

CAP-25.a: "Tool registry with pins, sha256, install/uninstall commands, date,
approving decision". DEC-127: the registry is project data at
``governance/project/tool-registry.yaml``, created by W1-06, and judged by the
schema in the kernel template (W1-04, DEC-121).

KPI failure 2: "A registry entry lacks an uninstall command".
"""

from __future__ import annotations

import copy
import datetime

import w1_06_schema as validator
import w1_06_support as support


def _label(entry, index):
    return f"entry {index} ({entry.get('name', 'no name')!r})"


def test_the_registry_is_committed(registry):
    assert support.is_tracked(support.REGISTRY_REL), f"{support.REGISTRY_REL} exists but git does not track it"
    assert support.is_committed_unchanged(support.REGISTRY_REL), (
        f"{support.REGISTRY_REL} differs from the committed file: the registry of record is the committed one"
    )


def test_the_registry_is_valid_against_the_committed_schema(registry, schema):
    found = validator.errors(registry, schema)
    assert found == [], f"{support.REGISTRY_REL} breaks {support.SCHEMA_REL}: {found}"


def test_the_registry_records_at_least_one_tool(registry):
    assert support.entries(registry), f"{support.REGISTRY_REL} records no tool"


def test_every_entry_states_all_seven_facts(registry):
    """A key with an empty value states nothing: every required fact is a non-blank string."""
    blank = []
    for index, entry in enumerate(support.entries(registry)):
        for field in support.REQUIRED:
            value = entry.get(field)
            if not isinstance(value, str) or not value.strip():
                blank.append(f"{_label(entry, index)}: `{field}` is {value!r}")
    assert blank == [], f"entries of {support.REGISTRY_REL} with a missing or empty fact: {blank}"


def test_each_tool_is_recorded_once(registry):
    names = [support.norm_name(entry.get("name", "")) for entry in support.entries(registry)]
    twice = sorted({name for name in names if names.count(name) > 1})
    assert twice == [], f"{support.REGISTRY_REL} records these tools more than once: {twice}"


def test_every_sha256_is_a_sha256_digest(registry):
    """CAP-25.a: 64 hexadecimal characters, nothing else."""
    wrong = [f"{_label(entry, index)}: {entry.get('sha256')!r}"
             for index, entry in enumerate(support.entries(registry))
             if not support.SHA256.fullmatch(str(entry.get("sha256", "")).strip())]
    assert wrong == [], f"entries of {support.REGISTRY_REL} whose sha256 is not a SHA-256 digest: {wrong}"


def test_every_date_is_a_calendar_date(registry):
    wrong = []
    for index, entry in enumerate(support.entries(registry)):
        value = str(entry.get("date", "")).strip()
        try:
            datetime.date.fromisoformat(value[:10])
        except ValueError:
            wrong.append(f"{_label(entry, index)}: {entry.get('date')!r}")
    assert wrong == [], f"entries of {support.REGISTRY_REL} whose date does not start with YYYY-MM-DD: {wrong}"


# --------------------------------------------------------------------------
# KPI failure 2: a registry entry lacks an uninstall command
# --------------------------------------------------------------------------

def test_every_entry_has_an_uninstall_command(registry):
    lacking = []
    for index, entry in enumerate(support.entries(registry)):
        value = entry.get("uninstall")
        if not isinstance(value, str) or not value.strip():
            lacking.append(_label(entry, index))
    assert lacking == [], f"entries of {support.REGISTRY_REL} without an uninstall command: {lacking}"


def test_no_uninstall_command_is_the_install_command(registry):
    """An entry that repeats its install command as its uninstall command has no uninstall command."""
    same = [_label(entry, index) for index, entry in enumerate(support.entries(registry))
            if isinstance(entry.get("uninstall"), str) and isinstance(entry.get("install"), str)
            and entry["uninstall"].strip() == entry["install"].strip()]
    assert same == [], f"entries of {support.REGISTRY_REL} whose uninstall command is their install command: {same}"


def test_the_schema_refuses_this_registry_once_an_entry_loses_its_uninstall_command(registry, schema):
    """The failure line is caught by the committed schema on this registry's own entries."""
    assert support.entries(registry), f"{support.REGISTRY_REL} records no tool"
    for index, entry in enumerate(registry["tools"]):
        if not isinstance(entry, dict):
            continue
        broken = copy.deepcopy(registry)
        broken["tools"][index].pop("uninstall", None)
        assert validator.errors(broken, schema), (
            f"the schema accepted {support.REGISTRY_REL} with {_label(entry, index)} stripped of `uninstall`"
        )
