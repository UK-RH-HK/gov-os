"""KPI success 5: an exact string, identifier or error-message query returns every occurrence with file path and
line [CAP-11.a].

The expected occurrences are computed from the fixture's own text: every line of a corpus file that holds the
query string, as ``(path, line)``. The index is the session's read-only one; the queries do not refresh it.
"""

from __future__ import annotations

import pytest

import w1_17_support as support


def _search(api, indexed, query):
    answer = api.search(indexed.root, query, refresh=False)
    for hit in answer["hits"]:
        assert query in hit["text"], f"a hit's text does not hold the query {query!r}: {hit!r}"
    return support.places(answer)


def test_an_error_message_query_returns_every_occurrence_with_path_and_line(api, indexed):
    """A document, a Python file and a TypeScript file hold the message; a line with its words in another order
    does not hold it."""
    expected = support.occurrences(support.ERROR)
    assert {rel for rel, _ in expected} == {support.RUNBOOK, support.POOL, support.CLIENT}
    assert _search(api, indexed, support.ERROR) == expected


@pytest.mark.parametrize("query", [support.SNAKE, support.CAMEL, support.CALL],
                         ids=["snake-case-identifier", "camel-case-identifier", "call-with-punctuation"])
def test_an_identifier_query_returns_every_occurrence_with_path_and_line(api, indexed, query):
    expected = support.occurrences(query)
    assert len(expected) >= 2, "the fixture no longer holds the identifier in two places"
    assert _search(api, indexed, query) == expected


def test_occurrences_far_into_a_long_file_are_each_reported_once_with_their_line(api, indexed):
    """The file spans many chunks; two of the occurrences are on neighbouring lines, one on the last line."""
    expected = [(support.LONG, number) for number in support.MARKED_LINES]
    assert support.occurrences(support.MARKER) == expected
    assert _search(api, indexed, support.MARKER) == expected


@pytest.mark.parametrize("name", list(support.SYNTAX_QUERIES))
def test_a_string_with_query_syntax_characters_is_read_as_the_string_it_is(api, indexed, name):
    """Operators, quotes, wildcards and brackets are part of the exact string, not a query language."""
    query = support.SYNTAX_QUERIES[name]
    expected = support.occurrences(query)
    assert len(expected) == 1 and expected[0][0] == support.SYNTAX
    assert _search(api, indexed, query) == expected


def test_the_same_content_at_two_paths_is_reported_at_both(api, indexed):
    """Two tracked files are one blob. The index is keyed by blob hash; the occurrences are still two."""
    expected = support.occurrences(support.TWIN)
    assert [rel for rel, _ in expected] == sorted(support.TWINS)
    assert _search(api, indexed, support.TWIN) == expected


def test_a_hit_names_the_chunk_record_it_comes_from(api, indexed):
    """The line of a hit lies inside the chunk the hit names, and the hit's parent is that chunk's parent."""
    chunks = {record["chunk_id"]: record for record in api.chunks(indexed.root, path=support.POOL)}
    answer = api.search(indexed.root, support.SNAKE, refresh=False)
    hits = [hit for hit in answer["hits"] if hit["path"] == support.POOL]
    assert hits, f"no hit in {support.POOL}: {answer!r}"
    for hit in hits:
        chunk = chunks.get(hit["chunk_id"])
        assert chunk is not None, f"the hit names a chunk that chunks() does not list for its file: {hit!r}"
        assert chunk["start_line"] <= hit["line"] <= chunk["end_line"], f"{hit!r} is outside its chunk {chunk!r}"
        assert hit["parent_id"] == chunk["parent_id"], f"{hit!r} and its chunk {chunk!r} name different parents"
