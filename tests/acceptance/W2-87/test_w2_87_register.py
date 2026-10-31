"""W2-87 part 1: the register is its entries (DEC-952 item 1, DEC-866, DEC-423, DEC-791 item 1).

A chunk of the decision register belongs to the entry whose span holds its first line, never to the register as a
whole (today every register chunk takes the id and status of the register's last entry by id).
"""

from __future__ import annotations

import w2_87_support as support
from w2_87_support import CLOSED_OVER, CLOSURE, KEPT_A, KEPT_B, LAST, LAST_SUPERSEDED, NEIGHBOUR, NEW, OLD, PHRASE


def _routes_by_label(bundle, register_text=support.REGISTER_TEXT):
    return {support.label(item, register_text): item["routes"] for item in bundle["evidence"]}


def test_r1_the_closure_route_takes_an_older_entry_by_its_own_id(api, planted):
    """With ``ids=[DEC-104]`` (not the register's last entry), DEC-104's chunk joins through the closure route,
    and a neighbouring entry's chunk does not."""
    root = planted("absent")
    bundle = api.retrieve(root, support.UNRELATED, ids=[CLOSED_OVER])
    routes = _routes_by_label(bundle)
    assert CLOSED_OVER in routes, \
        f"the chunk of {CLOSED_OVER}'s span did not join the bundle when {CLOSED_OVER} was closed over " \
        f"(the register's last entry is {LAST}); evidence: {list(routes)}"
    assert CLOSURE in routes[CLOSED_OVER], f"{CLOSED_OVER}'s chunk came by {routes[CLOSED_OVER]}, not by the closure"
    for other in (NEIGHBOUR, LAST, OLD, NEW):
        assert CLOSURE not in routes.get(other, []), \
            f"{other}'s chunk joined through the closure of {CLOSED_OVER}: a register chunk is its own entry"


def test_r2_a_superseded_last_entry_does_not_drop_the_other_entries(api, planted):
    """The register's last entry by id (DEC-203) is SUPERSEDED by its status line: the chunks of DEC-201 and
    DEC-202, both ACCEPTED, stay in the bundle, and the drop names no accepted entry."""
    text = support.SUPERSEDED_LAST_REGISTER_TEXT
    root = planted("absent", text)
    bundle = api.retrieve(root, PHRASE, batch_size=50)
    names = support.labels(bundle, text)
    for entry in (KEPT_A, KEPT_B):
        assert entry in names, \
            f"{entry} (ACCEPTED) was left out because the register's last entry {LAST_SUPERSEDED} is superseded; " \
            f"evidence: {names}; dropped: {bundle['merge']['dropped']}"
    dropped_ids = {entry.get("id") for entry in bundle["merge"]["dropped"]}
    assert not dropped_ids & {KEPT_A, KEPT_B}, f"an accepted entry is named as dropped: {bundle['merge']['dropped']}"


def test_r2_a_superseded_entry_that_is_kept_today_stays_kept(api, planted):
    """Nothing newly dropped (leaving superseded entries out is W2-55's): with the last entry ACCEPTED, the chunk of
    DEC-101, superseded by DEC-102's status line, is kept as today's code keeps it, beside DEC-102's."""
    root = planted("absent")
    bundle = api.retrieve(root, PHRASE, batch_size=50)
    names = support.labels(bundle)
    assert OLD in names and NEW in names, \
        f"a register chunk that today's code keeps was left out: evidence {names}; dropped {bundle['merge']['dropped']}"
    assert support.REGISTER not in {entry.get("path") for entry in bundle["merge"]["dropped"]}, \
        f"the register is named as dropped: {bundle['merge']['dropped']}"
