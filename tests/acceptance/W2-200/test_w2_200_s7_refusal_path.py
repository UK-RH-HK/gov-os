"""S7: the refusal path carries no packet.

``s7_world``: the ticket's acceptance test fails; ``gov close --disposition repair`` is refused and writes its repair
ticket and class. The repair ticket's fields are those the close wrote before this ticket, less ``context_hash``.
"""

from __future__ import annotations

import json

import w2_200_support as s

# The repair ticket's fields as gov close wrote them at the base (tk's own, then the close's), less context_hash.
REPAIR_FIELDS = {"id", "status", "deps", "links", "created", "type", "priority", "assignee", "parent", "state_class",
                 "disposition", "role", "allowed_paths", "kpis", "repair_of_findings"}


def _repair(world):
    found = world.project.repair_tickets()
    assert len(found) == 1, f"{len(found)} repair tickets, not one\n{world.run.describe()}"
    return found[0]


def test_s7_the_refusal_keeps_its_code_and_class(s7_world):
    run = s7_world.run
    error = run.error()
    assert run.code == 3 and error.get("code") == "CHECK_FAILED", f"the refusal is not as before\n{run.describe()}"
    assert error["details"].get("disposition") == "repair", run.describe()
    assert "CONTEXT_FAILED" not in json.dumps(run.envelope()), run.describe()
    assert "context" not in error["details"], f"the refusal carries a context entry: {error['details'].get('context')!r}"


def test_s7_the_repair_ticket_has_the_fields_of_before_less_context_hash(s7_world):
    front = s.front_of(_repair(s7_world).read_text(encoding="utf-8"))
    assert set(front) == REPAIR_FIELDS, f"the repair ticket's fields: extra {sorted(set(front) - REPAIR_FIELDS)}, " \
                                        f"missing {sorted(REPAIR_FIELDS - set(front))}"
    assert front["parent"] == s.TICKET and front["disposition"] == "repair" and front["state_class"] == "AUTHORITATIVE"
    assert front["deps"] == [s.TICKET], f"deps: {front['deps']!r}"


def test_s7_no_line_of_the_repair_ticket_speaks_of_a_context(s7_world):
    text = _repair(s7_world).read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if "context" in line.lower()]
    assert not lines, f"the repair ticket still holds packet lines: {lines}"
