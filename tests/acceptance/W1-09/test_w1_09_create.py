"""DEC-229: "W1-09 adds the key when a ticket is created".

No KPI line of the ticket names this duty (package DP-7). ``create`` runs the
project's vendored ticket script and gives the new ticket ``state_class``.
"""

from __future__ import annotations

import w1_09_support as support


def test_a_created_ticket_carries_state_class(api, project, vendored):
    project.settle()
    ticket = api.call("create", project.root, "A new ticket")
    assert isinstance(ticket, str) and ticket, f"create did not return the new ticket's id: {ticket!r}"
    path = project.root / ".tickets" / f"{ticket}.md"
    assert path.is_file(), f"create returned {ticket!r} and wrote no .tickets/{ticket}.md"
    lines = support.frontmatter_lines(path)
    assert "state_class: AUTHORITATIVE" in lines, f"the new ticket has no state_class: AUTHORITATIVE\n{lines}"


def test_a_created_ticket_is_the_ticket_the_script_writes(api, project, vendored):
    """The fields of tk are kept, and the ticket is open with its title."""
    project.settle()
    ticket = api.call("create", project.root, "A new ticket")
    path = project.root / ".tickets" / f"{ticket}.md"
    lines = support.frontmatter_lines(path)
    for expected in (f"id: {ticket}", "status: open", "deps: []", "type: task"):
        assert expected in lines, f"the new ticket lacks the line {expected!r}\n{lines}"
    assert len([line for line in lines if line.startswith("state_class:")]) == 1
    assert "# A new ticket" in path.read_text(encoding="utf-8").split("\n")
    assert ticket not in api.call("ready", project.root), \
        "a ticket just created, with no acceptance tests folder, appears as READY"
