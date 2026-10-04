"""KPI success 1: every chunk record carries ``parent_id``, the section for documents and the function or module for
code (DEC-091) [CAP-18.b].

A chunk record is what ``chunks(root)`` lists; ``parent(root, parent_id)`` gives the parent's file, kind and span
of lines. The child is the chunk, the parent is the span W1-20 expands a hit to.
"""

from __future__ import annotations

import w1_17_support as support


def _hit(api, indexed, query, rel, line):
    answer = api.search(indexed.root, query, refresh=False)
    found = [hit for hit in answer["hits"] if (hit["path"], hit["line"]) == (rel, line)]
    assert len(found) == 1, f"expected one hit for {query!r} at {rel}:{line}: {answer!r}"
    return found[0], api.parent(indexed.root, found[0]["parent_id"])


def test_every_chunk_record_carries_a_parent_that_contains_it(api, indexed):
    """Every file of the corpus has chunks; every chunk names a parent in its own file whose span holds the chunk."""
    chunks = api.chunks(indexed.root)
    ids = [record["chunk_id"] for record in chunks]
    assert len(set(ids)) == len(ids), "two chunk records share a chunk_id"
    assert set(support.CORPUS) <= {record["path"] for record in chunks}
    parents = api.parents(indexed.root, [record["parent_id"] for record in chunks])
    for record in chunks:
        parent = parents[record["parent_id"]]
        assert parent["path"] == record["path"], f"{record!r} has a parent in another file: {parent!r}"
        assert parent["start_line"] <= record["start_line"] and record["end_line"] <= parent["end_line"], \
            f"{record!r} is not inside its parent {parent!r}"


def test_the_chunks_of_one_file_are_listed_by_its_path(api, indexed):
    chunks = api.chunks(indexed.root, path=support.LONG)
    assert len(chunks) > 1, "a 3000-line file is one chunk"
    assert {record["path"] for record in chunks} == {support.LONG}
    covered = {number for record in chunks for number in range(record["start_line"], record["end_line"] + 1)}
    assert covered == set(range(1, support.LONG_LINES + 1)), "the chunks do not cover every line of the file"


def test_a_chunk_of_a_document_has_its_section_as_parent(api, indexed):
    """The hit is in ``## Failures``: the parent starts at that heading and ends before ``## Recovery``."""
    text = support.RUNBOOK_TEXT
    line = support.line_of(text, "The log shows")
    hit, parent = _hit(api, indexed, support.ERROR, support.RUNBOOK, line)
    assert parent["kind"] == "section", parent
    assert parent["start_line"] == support.line_of(text, "## Failures"), parent
    assert line + 1 <= parent["end_line"] < support.line_of(text, "## Recovery"), parent


def test_two_sections_of_one_document_are_two_parents(api, indexed):
    text = support.RUNBOOK_TEXT
    _, starting = _hit(api, indexed, support.SNAKE, support.RUNBOOK, support.line_of(text, "Start the pool"))
    _, failures = _hit(api, indexed, support.ERROR, support.RUNBOOK, support.line_of(text, "The log shows"))
    assert starting["parent_id"] != failures["parent_id"]
    assert starting["start_line"] == support.line_of(text, "## Starting"), starting
    assert starting["end_line"] < failures["start_line"], (starting, failures)


def test_a_chunk_of_code_has_a_function_or_a_module_as_parent(api, indexed):
    """No parser is demanded for TypeScript: the parent is a function, or the module, which is the whole file."""
    line = support.line_of(support.CLIENT_TEXT, "    throw new Error")
    _, parent = _hit(api, indexed, support.ERROR, support.CLIENT, line)
    assert parent["kind"] in ("function", "module"), parent
    assert parent["start_line"] <= line <= parent["end_line"], parent
    if parent["kind"] == "module":
        assert (parent["start_line"], parent["end_line"]) == (1, support.line_count(support.CLIENT_TEXT)), parent


def test_a_chunk_inside_a_python_function_has_that_function_as_parent(api, indexed):
    """Package DP-6, the recommended option: Python is read with the standard library, so the parent of a line
    inside ``def connect`` is that function, from its ``def`` line to its last line."""
    text = support.POOL_TEXT
    line = support.line_of(text, "        raise ")
    _, parent = _hit(api, indexed, support.ERROR, support.POOL, line)
    assert parent["kind"] == "function", parent
    assert parent["start_line"] == support.line_of(text, "def connect("), parent
    assert parent["end_line"] == support.line_count(text), parent


def test_python_code_outside_any_function_has_the_module_as_parent(api, indexed):
    """Package DP-6, the recommended option: a module-level line belongs to the module, the whole file."""
    text = support.POOL_TEXT
    _, parent = _hit(api, indexed, "LIMIT_OF_THE_POOL", support.POOL, support.line_of(text, "LIMIT_OF_THE_POOL"))
    assert parent["kind"] == "module", parent
    assert (parent["start_line"], parent["end_line"]) == (1, support.line_count(text)), parent


def test_chunk_and_parent_ids_are_the_same_in_a_second_build(api, indexed, base, tmp_path):
    """A hit's ``parent_id`` must still name the same span after ``.gov-runtime/`` is deleted and rebuilt."""
    other = support.clone(base, tmp_path / "elsewhere" / "project")
    api.refresh(other)
    assert api.chunks(other) == api.chunks(indexed.root)
    ids = [record["parent_id"] for record in api.chunks(other)]
    assert api.parents(other, ids) == api.parents(indexed.root, ids)
