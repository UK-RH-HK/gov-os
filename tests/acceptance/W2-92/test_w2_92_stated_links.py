"""KPI success 7 (DEC-1072 (1), DEC-1073; LINK-INTEGRITY §6.1): the stated links.

At rebuild the store keeps, in a table of its own outside the digest, the links the records state that no edge
holds: the front-matter id keys (``sources``, ``closes``, ``decisions``, ``decisions_applied``, ``decisions_carried``,
``decisions_recorded``, ``decisions_read``, ``requirements_implemented``) as CITES, ``task`` as OF_TASK, the
register's ``**Under:**`` as UNDER, a supersession naming ids alone as SUPERSEDES and every other supersession or
amendment as AMENDS, by the census's patterns in one function (``register_statements``); the closure, ``gov
dangling`` and every reader of edges are unchanged.

The planted marina (``support.links_corpus``) states each kind once in the census's forms. The store this worktree's
code builds is read with sqlite, read-only; "a table of its own" is a table the integrated code's store
(``support.LINKS_BASE``, the same commit) does not have. A row states a link when one of its cells is the type (any
case) and it holds the source and, after it, the target (the order of ``edges``: type, source, target).

Not a case here: "on this repository's register they match the census's statements one for one" needs this
repository's store; it is the CTO's measured check, verified by the evidence file (README map).
"""

from __future__ import annotations

import ast

import pytest

import w2_92_support as support

KINDS = (support.CITES, support.OF_TASK, support.UNDER, support.SUPERSEDES, support.AMENDS)
ONE_EACH = [case for case in support.STATED if case[1] != support.LK_MANY]


@pytest.fixture(scope="module")
def new_tables(marina, marina_at_base):
    """``table -> rows`` of the tables this worktree's store has and the integrated code's store does not."""
    now, before = support.store_tables(marina), support.store_tables(marina_at_base)
    return {name: rows for name, rows in now.items() if name not in before}


def _rows(new_tables):
    return [row for rows in new_tables.values() for row in rows]


@pytest.mark.parametrize("kind, source, target, form", ONE_EACH, ids=[case[3] for case in ONE_EACH])
def test_s7_each_stated_link_is_kept_as_its_type_in_a_table_of_its_own(new_tables, marina_api, marina,
                                                                         kind, source, target, form):
    """The link is a row of a table the integrated store does not have, of its type and of no other of the five;
    it is not an edge."""
    assert new_tables, (
        "the store has no table the integrated code's store lacks: the stated links are kept nowhere "
        f"({form}: {source} -> {target} as {kind})")
    rows = _rows(new_tables)
    found = support.kinds_of(rows, source, target)
    assert kind in found, (
        f"{form}: {source} -> {target} is not kept as {kind} in the store's new tables {sorted(new_tables)} "
        f"(types found for the pair: {found or 'none'})")
    assert found == [kind], f"{form}: {source} -> {target} is kept as {found}; it is {kind} alone"
    edges = marina_api.value("gov.records", "edges", marina)
    assert not [edge for edge in edges if {edge["source"], edge["target"]} == {source, target}], (
        f"{form}: {source} -> {target} became an edge ({edges}); the stated links stay out of the edges")


def test_s7_a_tickets_twenty_sources_are_each_kept(new_tables):
    """DAEO-lk03's twenty ``sources:`` are twenty CITES rows (none dropped at rebuild; the hop's bound is S8's)."""
    rows = _rows(new_tables)
    missing = [target for target in support.MANY_IDS if not support.typed(rows, support.CITES, support.LK_MANY, target)]
    assert not missing, f"{support.LK_MANY}'s sources not kept as CITES: {missing}"


def test_s7_a_supersession_of_ids_alone_on_the_status_line_stays_todays_edge(marina_api, marina, new_tables):
    """``**Supersedes:** DEC-446`` alone on DEC-445's status line is the SUPERSEDES edge the loader makes today
    (a guard); the new tables never call it an amendment."""
    kind, source, target = support.EDGE_ONLY
    edges = marina_api.value("gov.records", "edges", marina)
    assert {"type": kind, "source": source, "target": target} in edges, edges
    assert support.AMENDS not in support.kinds_of(_rows(new_tables), source, target)


def test_s7_the_store_digest_is_unchanged(marina_api, marina, marina_base_api, marina_at_base):
    """The table is outside the digest: the same commit gives the integrated code's digest (a guard)."""
    now = marina_api.value("gov.store.loader", "digest", marina)
    before = marina_base_api.value("gov.store.loader", "digest", marina_at_base)
    assert now == before, f"the store digest changed: integrated {before}, now {now}"


READERS = [("edges", "gov.records", "edges"), ("gov dangling", "gov.records", "dangling"),
           ("records", "gov.records", "records")]


@pytest.mark.parametrize("name, module, function", READERS, ids=[case[0] for case in READERS])
def test_s7_every_reader_of_the_graph_answers_as_today(marina_api, marina, marina_base_api, marina_at_base,
                                                         name, module, function):
    """``edges``, ``gov dangling`` and ``records`` answer as the integrated code does on the same commit (a guard)."""
    now = marina_api.value(module, function, marina)
    before = marina_base_api.value(module, function, marina_at_base)
    assert now == before, f"{name} changed:\n  integrated {before}\n  now        {now}"


CLOSURES = [([support.LK_TICKET], 1), ([support.LK_DEPENDENT], 3), (["DEC-432"], 1), (["DEC-445"], 3),
            (["DEC-421", support.LK_CHECKPOINT], 3)]


@pytest.mark.parametrize("ids, depth", CLOSURES, ids=[f"{'+'.join(ids)} at depth {depth}" for ids, depth in CLOSURES])
def test_s7_the_closure_is_unchanged(marina_api, marina, marina_base_api, marina_at_base, ids, depth):
    """``gov closure`` reaches what it reaches today (a guard): the stated links are not followed by it."""
    now = marina_api.value("gov.closure", "closure", marina, ids, depth)
    before = marina_base_api.value("gov.closure", "closure", marina_at_base, ids, depth)
    assert now == before, f"the closure of {ids} at depth {depth} changed:\n  integrated {before}\n  now        {now}"


def test_s7_the_census_patterns_are_one_function_register_statements():
    """The register's statements are read by one function named ``register_statements`` (which ``gov links``,
    W2-129, reads too): exactly one definition of it in ``src/gov``."""
    found = []
    for path in sorted((support.SRC / "gov").rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        found += [f"{path.relative_to(support.SRC)}:{node.lineno}" for node in ast.walk(tree)
                  if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "register_statements"]
    assert len(found) == 1, f"register_statements is defined {len(found)} times in src/gov: {found}"
