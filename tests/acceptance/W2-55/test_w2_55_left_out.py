"""KPI 3 and failure 2: what agents see leaves out superseded and done entries, and says how many (S4).

``gov retrieve <query> --json`` and ``gov context <ticket> --json`` leave out evidence from the register whose entry
is superseded (its status word, or another entry's ``**Supersedes:**``) or done (its tags' ``· done``); the bundle and
the packet then carry ``left_out: {count, superseded, done}``. A changed entry is still served. With nothing to
leave out the key is absent. Lens B's Q05 (a superseded decision served unmarked, F4) is a case.
"""

from __future__ import annotations

import pytest

import w2_55_support as s

PHRASE = "vermilion beacon clause"
K = s.KERNEL_PLACE

REGISTER_TEXT = s.register(
    s.entry("DEC-101", "The first beacon rule", "SUPERSEDED by DEC-102 · **Basis:** OWNER",
            s.tags("retrieval", "kernel", "none"), f"The {PHRASE} applies to every harbour light."),
    s.entry("DEC-102", "The beacon rule, restated", "ACCEPTED · **Basis:** OWNER · **Supersedes:** DEC-101",
            s.tags("retrieval", "kernel", K), f"The {PHRASE} applies to every light and every buoy."),
    s.entry("DEC-103", "The one-off beacon count", "ACCEPTED · **Basis:** OWNER",
            s.tags("records", "repository", "none", done=True), f"The {PHRASE} was counted once, in October."),
    s.entry("DEC-104", "The beacon colour", "ACCEPTED · **Basis:** OWNER · **Changed by:** DEC-105",
            s.tags("retrieval", "kernel", K), f"The {PHRASE} names the colour and the height of each beacon."),
    s.entry("DEC-105", "The beacon height", "ACCEPTED · **Basis:** OWNER · **Changes:** DEC-104",
            s.tags("retrieval", "kernel", K), f"The {PHRASE} sets a new height; the colour of DEC-104 stands."),
    s.entry("DEC-106", "The beacon keeper", "ACCEPTED · **Basis:** OWNER",
            s.tags("roles", "kernel", K), f"The {PHRASE} gives each beacon a keeper."),
    s.entry("DEC-107", "The beacon keepers, pooled", "ACCEPTED · **Basis:** OWNER · **Supersedes:** DEC-106",
            s.tags("roles", "kernel", K), f"The {PHRASE} pools the keepers of all beacons."),
    s.entry("DEC-108", "The tide gauge", tags_line=s.tags("records", "kernel", K),
            body="The tide gauge is read at dawn."),
)
LEFT_OUT = {"count": 3, "superseded": ["DEC-101", "DEC-106"], "done": ["DEC-103"]}
NOT_SERVED = {"DEC-101", "DEC-103", "DEC-106"}
SERVED = {"DEC-102", "DEC-104", "DEC-105", "DEC-107"}   # DEC-104 is changed, not superseded

# Nothing superseded or done: the same phrase, every entry in force.
PLAIN_REGISTER = s.register(
    s.entry("DEC-201", "The lamp rule", tags_line=s.tags("retrieval", "kernel", K),
            body=f"The {PHRASE} governs every lamp."),
    s.entry("DEC-202", "The mast rule", "ACCEPTED · **Basis:** OWNER · **Changed by:** DEC-203",
            s.tags("retrieval", "kernel", K), f"The {PHRASE} governs every mast."),
    s.entry("DEC-203", "The mast rule's height", "ACCEPTED · **Basis:** OWNER · **Changes:** DEC-202",
            s.tags("retrieval", "kernel", K), f"The {PHRASE} sets the height of every mast."),
)


def ticket(ticket_id, sources):
    """A ticket whose title begins with the word its supplementary lookup asks for (``vermilion``)."""
    listed = "".join(f"- {source}\n" for source in sources)
    return (f"---\nid: {ticket_id}\nstatus: open\ntype: task\ntitle: 'vermilion beacons for the harbour'\n"
            f"sources:\n{listed}---\n# {ticket_id}\n\nThe harbour's beacons.\n")


TICKETS = {".tickets/HARB-0001.md": ticket("HARB-0001", ["DEC-102"]),
           ".tickets/HARB-0002.md": ticket("HARB-0002", ["DEC-101"]),
           ".tickets/HARB-0003.md": ticket("HARB-0003", ["DEC-103"])}


@pytest.fixture(scope="module")
def harbour(retrieval_api, tmp_path_factory):
    project = s.build_project(tmp_path_factory.mktemp("w2-55-left-out") / "repo", REGISTER_TEXT, TICKETS)
    retrieval_api.build(project.root)
    return project.root


@pytest.fixture(scope="module")
def plain_harbour(retrieval_api, tmp_path_factory):
    files = {".tickets/HARB-0001.md": ticket("HARB-0001", ["DEC-201"])}
    project = s.build_project(tmp_path_factory.mktemp("w2-55-plain") / "repo", PLAIN_REGISTER, files)
    retrieval_api.build(project.root)
    return project.root


# --------------------------------------------------------------------------
# gov retrieve
# --------------------------------------------------------------------------

def test_retrieve_leaves_out_superseded_and_done_entries(retrieval_api, harbour):
    bundle = retrieval_api.gov(harbour, "retrieve", PHRASE).result
    got = s.served(bundle["evidence"], REGISTER_TEXT)
    assert not got & NOT_SERVED, f"superseded or done entries reached the bundle: {sorted(got & NOT_SERVED)}"
    assert SERVED <= got, f"entries in force (one of them changed) are missing: {sorted(SERVED - got)}"


def test_retrieve_says_how_many_it_left_out(retrieval_api, harbour):
    bundle = retrieval_api.gov(harbour, "retrieve", PHRASE).result
    assert bundle.get("left_out") == LEFT_OUT, f"the bundle's left_out is {bundle.get('left_out')!r}, not {LEFT_OUT}"


def test_retrieve_with_nothing_to_leave_out_has_no_key(retrieval_api, plain_harbour):
    bundle = retrieval_api.gov(plain_harbour, "retrieve", PHRASE).result
    assert "left_out" not in bundle, f"nothing was left out, yet the bundle has left_out: {bundle['left_out']!r}"
    got = s.served(bundle["evidence"], PLAIN_REGISTER)
    assert {"DEC-201", "DEC-202", "DEC-203"} <= got, f"entries in force are missing: {sorted(got)}"


# Lens B's Q05 ("How is the old repository archived, and which decision is in force?"): a chain of supersessions
# (DEC-038 -> DEC-048 -> DEC-051, and DEC-049 superseded by DEC-053 Q5). Offline only the lexical route answers, and
# it matches an exact string on a line, so the question is asked in the words every entry of the chain holds.
Q05 = "old repository is archived"
Q05_REGISTER = s.register(
    s.entry("DEC-138", "Freeze and archive the Rust repository", "SUPERSEDED by DEC-148 · **Basis:** SUGGESTION",
            s.tags("records", "repository", "none"),
            "The old repository is archived as a frozen copy, read-only, as an asset."),
    s.entry("DEC-148", "Archive is one inert git bundle outside any working tree",
            "SUPERSEDED by DEC-151 (owner decision) · **Basis:** OWNER · **Supersedes:** DEC-138",
            s.tags("records", "repository", "none"),
            "The old repository is archived as one inert bundle, and its working copy is deleted."),
    s.entry("DEC-149", "Original documents stay out of the new repository",
            "SUPERSEDED by DEC-153 Q5 (originals kept in-tree under `docs/source/`) · **Basis:** OWNER",
            s.tags("records", "repository", "none"),
            "The originals stay out: the old repository is archived without them, provenance by hash."),
    s.entry("DEC-151", "Same repository; the archive is git history, not a folder",
            "ACCEPTED (owner) · **Basis:** OWNER · **Supersedes:** DEC-148",
            s.tags("records", "repository", s.PROJECT_PLACE),
            "Nothing is deleted: the old repository is archived as git history, under an annotated tag."),
    s.entry("DEC-153", "Owner answers to the inventory questions", "ACCEPTED (owner) · **Basis:** OWNER",
            s.tags("records", "repository", s.PROJECT_PLACE),
            "Q5: the originals are kept in-tree under `docs/source/`; the old repository is archived by its tag."),
)


@pytest.fixture(scope="module")
def q05(retrieval_api, tmp_path_factory):
    project = s.build_project(tmp_path_factory.mktemp("w2-55-q05") / "repo", Q05_REGISTER)
    retrieval_api.build(project.root)
    return project.root


def test_lens_b_q05_serves_the_decision_in_force_and_no_superseded_one(retrieval_api, q05):
    bundle = retrieval_api.gov(q05, "retrieve", Q05).result
    got = s.served(bundle["evidence"], Q05_REGISTER)
    assert {"DEC-151", "DEC-153"} <= got, f"the decisions in force, DEC-151 and DEC-153, are not served: {sorted(got)}"
    stale = got & {"DEC-138", "DEC-148", "DEC-149"}
    assert not stale, f"Q05: superseded decisions were served unmarked (F4): {sorted(stale)}"
    left = bundle.get("left_out") or {}
    assert left.get("superseded") == ["DEC-138", "DEC-148", "DEC-149"] and left.get("count") == 3, \
        f"Q05: the bundle does not say it left out the three superseded entries: {bundle.get('left_out')!r}"


# --------------------------------------------------------------------------
# gov context <ticket>
# --------------------------------------------------------------------------

def test_context_leaves_out_superseded_and_done_entries_from_the_supplementary_context(retrieval_api, harbour):
    packet = retrieval_api.gov(harbour, "context", "HARB-0001").result
    got = s.served(packet["supplementary"], REGISTER_TEXT)
    assert not got & NOT_SERVED, f"superseded or done entries reached the packet: {sorted(got & NOT_SERVED)}"
    assert "DEC-104" in got, f"the changed entry DEC-104 is not in the supplementary context: {sorted(got)}"


def test_context_says_how_many_it_left_out(retrieval_api, harbour):
    packet = retrieval_api.gov(harbour, "context", "HARB-0001").result
    assert packet.get("left_out") == LEFT_OUT, f"the packet's left_out is {packet.get('left_out')!r}, not {LEFT_OUT}"


def test_context_with_nothing_to_leave_out_has_no_key(retrieval_api, plain_harbour):
    packet = retrieval_api.gov(plain_harbour, "context", "HARB-0001").result
    assert "left_out" not in packet, f"nothing was left out, yet the packet has left_out: {packet['left_out']!r}"
    got = s.served(packet["supplementary"], PLAIN_REGISTER)
    assert {"DEC-202", "DEC-203"} <= got, f"entries in force are missing from the supplementary context: {sorted(got)}"


def test_a_superseded_mandatory_input_still_refuses(retrieval_api, harbour):
    answer = retrieval_api.gov(harbour, "context", "HARB-0002")
    envelope = answer.envelope
    assert envelope["ok"] is False and (envelope.get("error") or {}).get("code") == "BLOCKED", answer.describe()


def test_a_done_entry_declared_as_a_source_is_still_read(retrieval_api, harbour):
    packet = retrieval_api.gov(harbour, "context", "HARB-0003").result
    assert "DEC-103" in [item["id"] for item in packet["mandatory"]], \
        f"the done source DEC-103 is not a mandatory input of the packet: {packet['mandatory']}"
