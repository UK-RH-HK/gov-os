"""W1-48 — the three new entries meet the committed schema, and the record is the committed one.

KPI success 1 and 3: "recorded in governance/project/tool-registry.yaml … with
install and uninstall commands, date and approving decision". The schema
(``template/governance/kernel/schemas/tool-registry.schema.json``, W1-04)
requires seven facts of every entry; W1-06's suite checks the whole registry
against it. Here the three entries of this ticket are checked by name, so the
cases are red until each is there.
"""

from __future__ import annotations

import pytest

import w1_48_support as support

ENTRIES = {
    "claude code": support.CLAUDE_CODE,
    "bubblewrap": support.BUBBLEWRAP,
    "socat": support.SOCAT,
}


@pytest.mark.parametrize("tool", sorted(ENTRIES))
def test_an_entry_of_this_ticket_states_every_fact_the_schema_requires(registry, schema, tool):
    item = schema["properties"]["tools"]["items"]
    entry = support.one(registry, ENTRIES[tool])
    wrong = []
    for key in item["required"]:
        value = entry.get(key)
        if item["properties"].get(key, {}).get("type") == "string" and not isinstance(value, str):
            wrong.append(f"{key} is {value!r}, not a string")
        elif not str(value).strip():
            wrong.append(f"{key} is blank")
    assert wrong == [], f"the {tool} entry does not meet {support.SCHEMA_REL}: {wrong}"


def test_the_registry_as_read_is_the_committed_one():
    """ "Recorded" means committed: git tracks the registry and the working-tree file equals ``HEAD``'s."""
    assert support.is_committed_unchanged(support.REGISTRY_REL), (
        f"{support.REGISTRY_REL} is untracked or differs from HEAD: the record is not committed"
    )
