"""KPI success 9 (DEC-1073 (2)) and the failure line "a register chunk in a bundle without its status": status in
the bundle.

Every register chunk a bundle carries names its entry's status word and the entries that change it; a PROPOSED,
REJECTED, WITHDRAWN or SUPERSEDED decision is marked not in force, so no agent takes it as a rule.

The form is the implementation's. What an agent is told about a chunk (``support.what_the_item_says``) is its text,
every field its evidence item carries beyond its place (path, lines, ids, hash, routes, batch), and any entry outside
the evidence that names the chunk or its entry. "Names" is the status word in capitals, or a changer's id, anywhere
in that. "Marked not in force" is a field ``not_in_force: true`` or ``in_force: false`` (``_``, ``-`` or a space
between the words), else the words "not in force". An entry in force must not be so marked
(``support.status_faults``). The planted texts hold none of these words.

The marina's register (``support.REGISTER_ENTRIES``) holds DEC-432, long enough for four chunks, the last three
without its status line, changed by DEC-431 (``**Changes:**``, stated on the changer) and DEC-433 (``**Changed
by:**``, on its own status line); one entry of each status not in force; and the partial supersessions' targets,
which stay in force.
"""

from __future__ import annotations

import pytest

import w2_92_support as support

T = support.TITLE_OF

CASES = [
    ("a long entry changed twice, every chunk", "DEC-432", {}),
    ("a long entry, its chunks alone (no parent)", "DEC-432", {"bundle_budget": 1}),
    ("PROPOSED", "DEC-451", {}),
    ("REJECTED", "DEC-452", {}),
    ("WITHDRAWN", "DEC-453", {}),
    ("SUPERSEDED", "DEC-454", {}),
    ("in force though superseded in part", "DEC-437", {}),
    ("in force though superseded in part, in free text (a guard)", "DEC-438", {}),
    ("in force, changed by nothing (a guard)", "DEC-455", {}),
]


@pytest.mark.parametrize("case, named, kwargs", CASES, ids=[case[0] for case in CASES])
def test_s9_every_register_chunk_names_its_status_and_its_changers(marina_ask, case, named, kwargs):
    bundle = marina_ask(T[named], **kwargs)
    _, spans = support.links_register()
    own = [item for item, entry in support.register_items(bundle, spans) if entry == named]
    assert own, f"premise: the bundle for {T[named]!r} holds no chunk of {named}: {support.items(bundle)}"
    if named == "DEC-432":
        assert len({(item["start_line"], item["end_line"]) for item in own}) >= 2, (
            f"premise: the bundle holds fewer than two chunks of {named}: {support.items(bundle)}")
    faults = support.status_faults(bundle, spans)
    assert not faults, f"{case}: the register chunks of the bundle for {T[named]!r}:\n  " + "\n  ".join(faults)
