"""F1 (a), DEC-1163 (7): G-24's "no record names the item" counts the store's stated links too.

KPI line S2's Verify clause: "G-24's 'no record names the item' counts the store's stated links too (a ticket's
sources and closes, the register's Under and Changes lines): a planted decision named only by a ticket's sources is
not deletable".

Reading R8 (README) says an item is deletable only when nothing depends on it, no record edge naming it. The store
keeps a second kind of naming outside ``edges``: ``stated_links`` (``src/gov/store/loader.py``'s module docstring):
a record's frontmatter id keys (``sources``, ``closes``, ... as CITES) and the register's statements (``**Under:**``
as UNDER; a ``**Changes:**`` or an amendment as AMENDS, a supersession of ids alone as SUPERSEDES). The owner decided
that a decision such a link names is not deletable. Direction is as for edges: the item named is the one that is not
deletable; what the item itself names does not count (R8).

One temporary repository, built once: the suite's fixture, plus five decisions and what names them. The store is
loaded at HEAD with nothing uncommitted, so the record graph reads current. No case builds a code index.

| decision | named by                                                  | stated link (store)                    |
|----------|-----------------------------------------------------------|----------------------------------------|
| DEC-401  | ticket PROJ-st01, frontmatter ``sources: [DEC-401]``       | CITES   PROJ-st01 -> DEC-401           |
| DEC-402  | ticket PROJ-st02, frontmatter ``closes: [DEC-402]``        | CITES   PROJ-st02 -> DEC-402           |
| DEC-403  | register entry DEC-406, ``**Under:** DEC-403``             | UNDER   DEC-406   -> DEC-403           |
| DEC-404  | register entry DEC-407, ``**Changes:** DEC-404``           | AMENDS  DEC-407   -> DEC-404           |
| DEC-405  | nothing                                                   | none                                   |

No edge names any of them (a ``**Changes:**`` line and an ``**Under:**`` line make no edge; a ``**Supersedes:**`` of
ids alone would, so it is not used for case 4).
"""

from __future__ import annotations

import sqlite3

import pytest

import w2_37_support as support

BY_SOURCES, BY_CLOSES, BY_UNDER, BY_CHANGES, BY_NOTHING = "DEC-401", "DEC-402", "DEC-403", "DEC-404", "DEC-405"
SOURCES_TICKET, CLOSES_TICKET = "PROJ-st01", "PROJ-st02"
UNDER_ENTRY, CHANGES_ENTRY = "DEC-406", "DEC-407"
PLANTED = (BY_SOURCES, BY_CLOSES, BY_UNDER, BY_CHANGES, BY_NOTHING, SOURCES_TICKET, CLOSES_TICKET, UNDER_ENTRY,
           CHANGES_ENTRY)

STATED = {
    ("CITES", SOURCES_TICKET, BY_SOURCES), ("CITES", CLOSES_TICKET, BY_CLOSES),
    ("UNDER", UNDER_ENTRY, BY_UNDER), ("AMENDS", CHANGES_ENTRY, BY_CHANGES),
}

REGISTER_ADDED = (
    f"\n### {UNDER_ENTRY} — A decision that stands under another\n"
    "- **Status:** ACCEPTED (owner, 2026-10-09) · **Basis:** a fixture\n"
    f"- **Under:** {BY_UNDER}\n"
    "- **Decision:** the fixture's entry that names another decision as the one it stands under.\n"
    f"\n### {CHANGES_ENTRY} — A decision that changes another\n"
    "- **Status:** ACCEPTED (owner, 2026-10-09) · **Basis:** a fixture\n"
    f"- **Changes:** {BY_CHANGES}\n"
    "- **Decision:** the fixture's entry that names another decision as the one it changes.\n"
)


def planted_files():
    return {
        f"docs/adr/{BY_SOURCES}.md": support.decision(BY_SOURCES),
        f"docs/adr/{BY_CLOSES}.md": support.decision(BY_CLOSES),
        f"docs/adr/{BY_UNDER}.md": support.decision(BY_UNDER),
        f"docs/adr/{BY_CHANGES}.md": support.decision(BY_CHANGES),
        f"docs/adr/{BY_NOTHING}.md": support.decision(BY_NOTHING),
        f".tickets/{SOURCES_TICKET}.md": support.ticket(SOURCES_TICKET, sources=[BY_SOURCES]),
        f".tickets/{CLOSES_TICKET}.md": support.ticket(CLOSES_TICKET, closes=[BY_CLOSES]),
    }


@pytest.fixture(scope="module")
def stated_repo(built, base, box, tmp_path_factory):
    """A clone of the suite's fixture with the planted records committed and the store loaded at that commit."""
    root = support.clone(base, tmp_path_factory.mktemp("w2-37-stated") / "repo")
    project = support.Project.__new__(support.Project)
    project.root, project.minute = root, 100
    for rel, text in planted_files().items():
        project.write(rel, text)
    project.write(support.REGISTER_REL, support.REGISTER + REGISTER_ADDED)
    project.commit("plant the decisions the stated links name")
    support.load_store(root, box)
    return root


@pytest.fixture(scope="module")
def tables(stated_repo):
    """``(edges, stated_links)`` of the store, read from its documented tables (loader.py's docstring)."""
    store = stated_repo / ".gov-runtime" / "store.db"
    assert store.is_file(), f"gov.store.load wrote no store at {store}"
    connection = sqlite3.connect(f"file:{store}?mode=ro", uri=True)
    try:
        edges = set(connection.execute("SELECT type, source, target FROM edges"))
        links = set(connection.execute("SELECT type, source, target FROM stated_links"))
    finally:
        connection.close()
    return edges, links


@pytest.fixture(scope="module")
def asked_stated(stated_repo, box):
    kept = {}

    def get(change):
        if change not in kept:
            kept[change] = support.ask(stated_repo, change, box)
        return kept[change]

    return get


def premise(tables, found, wanted):
    """The fixture is what the module says: the store holds the stated links and no edge names a planted
    decision, and the record graph reads current."""
    edges, links = tables
    missing = STATED - links
    assert not missing, f"the fixture is wrong: stated_links lacks {sorted(missing)}; it holds {sorted(links)}"
    named = sorted(edge for edge in edges if edge[1] in PLANTED or edge[2] in PLANTED)
    assert not named, f"the fixture is wrong: an edge names or leaves a planted record: {named}"
    assert found["graphs"]["record"] == support.GRAPH_OK, \
        f"the record graph is not current for {wanted}: {found['graphs']}"


def entry(found, wanted):
    entries = [one for one in found["change"] if one["id"] == wanted]
    assert len(entries) == 1, f"`change` does not name {wanted} once: {found['change']}"
    assert isinstance(entries[0].get("deletable"), bool), \
        f"the change {wanted} does not say whether it is deletable: {entries[0]}"
    return entries[0]


def assert_not_deletable(asked_stated, tables, wanted, naming, how):
    found = asked_stated(wanted)
    premise(tables, found, wanted)
    assert entry(found, wanted)["deletable"] is False, \
        f"{wanted} is called deletable although {naming} names it ({how}, a stated link the store holds); " \
        f"radius {found['radius']}, change {found['change']}"
    assert found["radius"] != "R0", \
        f"{wanted} is named by {naming} ({how}) yet its radius is {found['radius']}, the radius of a change " \
        f"nothing names"


def test_a_decision_named_only_by_a_tickets_sources_is_not_deletable(asked_stated, tables):
    assert_not_deletable(asked_stated, tables, BY_SOURCES, SOURCES_TICKET, "frontmatter `sources:`")


def test_a_decision_named_only_by_a_tickets_closes_is_not_deletable(asked_stated, tables):
    assert_not_deletable(asked_stated, tables, BY_CLOSES, CLOSES_TICKET, "frontmatter `closes:`")


def test_a_decision_named_only_by_a_register_under_line_is_not_deletable(asked_stated, tables):
    assert_not_deletable(asked_stated, tables, BY_UNDER, UNDER_ENTRY, "the register's `**Under:**` line")


def test_a_decision_named_only_by_a_register_changes_line_is_not_deletable(asked_stated, tables):
    assert_not_deletable(asked_stated, tables, BY_CHANGES, CHANGES_ENTRY, "the register's `**Changes:**` line")


def test_a_decision_no_edge_and_no_stated_link_names_is_still_deletable(asked_stated, tables):
    """The success guard: in the repository where four decisions are named by stated links, DEC-405 is named by
    nothing and is deletable at radius R0, affecting nothing. Likewise the two register entries that do the naming:
    what an item names itself does not count (R8)."""
    found = asked_stated(BY_NOTHING)
    premise(tables, found, BY_NOTHING)
    assert entry(found, BY_NOTHING)["deletable"] is True, f"{BY_NOTHING}: nothing names it, {found['change']}"
    assert found["radius"] == "R0", f"{BY_NOTHING} affects nothing, yet its radius is {found['radius']}"
    assert support.ids_of(found) == [], f"{BY_NOTHING} affects {support.ids_of(found)}"
    for namer in (UNDER_ENTRY, CHANGES_ENTRY):
        said = asked_stated(namer)
        assert entry(said, namer)["deletable"] is True, \
            f"{namer} only names others and nothing names it, yet it is not deletable: {said['change']}"
