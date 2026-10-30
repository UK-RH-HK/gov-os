"""W2-57, KPI line 3: the serial-only list's form, as P-IS-6's first table reworks it (DEC-889 item 5).

The list stays readable by today's readers as they are: one entry on a line, the beginning of a node id, the text
after `` #`` a comment (``gov close``'s plugin and the orchestrator's nightly script take every entry this way, and
the nightly runs every entry alone after its parallel run). Within that form every entry's comment says its route,
its kind and its reason in words (``<route>: <kind>: <reason>``; held entry by entry in W1-30's r11), and its
header documents the form, the kinds, the nightly route and the rule that a case is never listed merely because
it is slow. A reader of the list tells a nightly entry from a serial one by its first word.

These cases read the list as text, and ask the close's own plugin, in a fresh interpreter with this worktree's code,
which entries it takes. Nothing runs.
"""

from __future__ import annotations

import re

import w2_57_list_support as support


def test_the_header_documents_the_form_the_routes_the_kinds_and_the_rule_on_slow_cases():
    """The header names the entry's form and its comment's form, each route with what it means (the nightly
    route: collected by the close and left out of both its phases, run alone in the nightly), each kind, and the
    rule that a case is never listed merely because it is slow."""
    text = support.header()
    plain = " ".join(text.lower().split())
    missing = []
    if "<route>: <kind>: <reason>" not in plain:
        missing.append("the comment's form `<route>: <kind>: <reason>`")
    if not ("node id" in plain and " #" in text):
        missing.append("the entry's form (the beginning of a node id; the text after ` #` a comment)")
    for route in support.ROUTES:
        if not re.search(rf"(?m)^\s*{route}\b\s+\S", text):
            missing.append(f"the route `{route}` with what it means")
    for kind in support.KINDS:
        if not re.search(rf"(?m)^\s*{re.escape(kind)}\b\s+\S", text):
            missing.append(f"the kind `{kind}` with what it means")
    if not all(word in plain for word in ("collected", "left out", "nightly", "alone")):
        missing.append("the nightly route's meaning (collected by the close, left out of both its phases, run "
                       "alone in the nightly)")
    if "merely because it is slow" not in plain:
        missing.append("the rule that a case is never listed merely because it is slow")
    assert not missing, f"the header of {support.LIST_REL} does not document: {missing}"


def test_every_reader_takes_the_same_entries_and_each_is_the_beginning_of_a_node_id():
    """The close's own plugin and a reader that takes the text before `` #`` find the same entries in the same
    order; no entry carries its route or its kind inside it (an entry is a node id's beginning and nothing else)."""
    read = [entry for entry, _ in support.entries()]
    assert read, f"{support.LIST_REL} holds no entry"
    assert support.plugin_entries(support.REPO_ROOT) == list(dict.fromkeys(read)), (
        "the close's plugin reads other entries from the list than a reader of the text before ` #` does"
    )
    shaped = [entry for entry in read
              if not re.fullmatch(r"tests/[\w./-]+\.py(::[A-Za-z_]\w*)?", entry)]
    assert not shaped, f"entries that are not the beginning of a node id: {shaped}"
