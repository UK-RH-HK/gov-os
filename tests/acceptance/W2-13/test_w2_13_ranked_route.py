"""KPI success 1: the ranked lexical route [DEC-725, W2-M102, W2-L233, W2-M292, W2-M072, W2-M100].

The lexical index is an SQLite FTS5 table over the same parents and spans as today, built by ``gov rebuild``. A
plain-word question returns hits ranked by BM25, with field weights for id, title and body. An exact identifier
still ranks first: the exact-match route is kept as a boost, not replaced (CAP-11, W1-17).

The route's ranking is read from ``gov.retrieval.lexical.search(root, question, refresh=False)``: its ``ranked`` list
(DEC-1000), best first, each file at the place of its first chunk. Its ``hits`` stay W1-17's exact list (every line
that holds the string, case and all, by path and line), read by the exact-string case and by W2-M100's case (outside
DEC-1000's rewrite). Every case reads the one fixture store that ``gov rebuild --json`` built (fixture ``built``);
none writes it.
"""

from __future__ import annotations

import pytest

import w2_13_support as support

pytestmark = pytest.mark.needs("git", "gitleaks", "sqlite_vec")


def order(box, root, question):
    return support.ranked_paths(box.search(root, question))


def ranking(box, root, question):
    """The paths of the route's ``ranked`` list, each once, best first (DEC-1000)."""
    return support.ranked_list_paths(box.search(root, question), question)


def before(paths, first, second):
    """Whether ``first`` is ranked above ``second``; both must be in the route's ranked list."""
    missing = [rel for rel in (first, second) if rel not in paths]
    assert not missing, f"{missing} are not in the lexical route's ranked list; it ranked {paths}"
    return paths.index(first) < paths.index(second)


# ---- the index

def test_the_lexical_index_is_an_fts5_table_that_gov_rebuild_builds(box, built):
    """``gov rebuild`` made the store, the store holds an FTS5 table, and the facet answers from it read-only."""
    assert support.fts5_tables(built), f"{support.STORE_REL} holds no FTS5 table after gov rebuild"
    answer = box.search(built, support.EXACT_STRING)
    assert answer["available"] is True, f"the index gov rebuild built is not answered as fresh: {answer!r}"


def test_the_index_keeps_the_parents_and_spans_of_today(box, built):
    """The chunks of a document of sections and of a Python file, and their parents (DEC-343), are those the base
    gives through W1-17's interface (``chunks`` and ``parent``)."""
    outcome = box.run([(support.LEXICAL, "chunks", [support.path_arg(built)], {"path": rel})
                       for rel in (support.SPANS_DOC, support.SPANS_CODE)])
    chunks = outcome.value(0) + outcome.value(1)
    parents = box.run([(support.LEXICAL, "parent", [support.path_arg(built), chunk["parent_id"]], {})
                       for chunk in chunks])
    found = []
    for index, chunk in enumerate(chunks):
        parent = parents.value(index)
        assert isinstance(parent, dict), f"the parent of {chunk!r} is not found: {parent!r}"
        found.append((chunk["path"], chunk["start_line"], chunk["end_line"], parent["kind"], parent["start_line"],
                      parent["end_line"]))
    assert sorted(found) == sorted(support.SPANS_TODAY), \
        f"the chunks and parents are not those of today:\n  found: {sorted(found)}\n  today: {support.SPANS_TODAY}"


# ---- a plain-word question (W2-M292) and BM25

def test_a_plain_word_question_returns_ranked_lexical_chunks(box, built):
    """W2-M292: no line holds the question as a phrase; its words are matched, and the file that holds them all is
    in the route's ranked list. The exact list (``hits``) stays W1-17's: no line holds the question, so it is empty."""
    assert not any(support.PLAIN_QUESTION in text for text in support.corpus().values()), \
        "premise: a line of the fixture holds the question verbatim"
    answer = box.search(built, support.PLAIN_QUESTION)
    paths = support.ranked_list_paths(answer, support.PLAIN_QUESTION)
    assert paths, f"the plain-word question {support.PLAIN_QUESTION!r} returns no ranked lexical chunk"
    assert support.BEST in paths, \
        f"{support.BEST} holds every word of the question and is not in the ranked list: {paths}"
    assert support.exact_lines(answer) == support.lines_holding(support.PLAIN_QUESTION), \
        f"`hits` is not W1-17's exact list: no line holds {support.PLAIN_QUESTION!r}, and it holds " \
        f"{support.exact_lines(answer)}"


def test_ranked_chunks_are_best_first_by_how_well_they_match_the_words(box, built):
    """Three files of the same length hold three, two and one of the question's words; their paths sort the other
    way round, so an order by path, by row or by line is red. BM25 ranks them three, two, one."""
    paths = ranking(box, built, support.PLAIN_QUESTION)
    assert before(paths, support.BEST, support.SECOND) and before(paths, support.SECOND, support.THIRD), \
        f"not ranked best first ({support.BEST}, {support.SECOND}, {support.THIRD}): {paths}"
    assert paths[0] == support.BEST, \
        f"the file that matches the question best is not first in the ranked list: {paths}"


@pytest.mark.parametrize("pair", list(support.FIELD_PAIRS), ids=list(support.FIELD_PAIRS))
def test_a_word_in_the_id_or_the_title_ranks_above_the_same_word_in_the_body(box, built, pair):
    """The two files of a pair hold the same words, the same number of times: only whether the question's word is
    in the record's id (or the heading) or in the body tells them apart, so a ranking with no field weights ties
    them. Each pair has a mirror whose paths sort the other way, so a tie broken by path, row or insertion order
    passes at most one of the two."""
    question, weighted, body = support.FIELD_PAIRS[pair]
    paths = ranking(box, built, question)
    assert before(paths, weighted, body), \
        f"{weighted} (the word in its {pair.split(',')[0]}) is not ranked above {body} (the word in its body) " \
        f"for {question!r}: {paths}"


# ---- the exact identifier: a boost, not replaced

@pytest.mark.parametrize("question", support.EXACT_QUESTIONS, ids=["the identifier alone", "the identifier and words"])
def test_an_exact_identifier_ranks_first(box, built, question):
    """One file holds ``QX-4471``; two others hold ``QX`` and ``4471``, and the question's other words, far more
    often. The file that holds the identifier verbatim is first in the route's ranked list, whose exact chunks come
    before the others (the boost); ``hits`` stays W1-17's exact list (the holder's line asked alone, none with
    words)."""
    answer = box.search(built, question)
    ranked = support.ranked_list(answer, question)
    paths = list(dict.fromkeys(chunk["path"] for chunk in ranked))
    assert paths and paths[0] == support.EXACT_HOLDER, \
        f"{support.EXACT_HOLDER} holds {support.EXACT_ID} verbatim and is not first in the ranked list for " \
        f"{question!r}: {paths}"
    flags = [chunk["exact"] for chunk in ranked]
    assert flags == sorted(flags, reverse=True), \
        f"a chunk that holds the exact string is ranked below one that does not for {question!r}: " \
        f"{[(chunk['path'], chunk['exact']) for chunk in ranked]}"
    if question == support.EXACT_ID:
        assert ranked[0]["exact"] is True, \
            f"the first ranked chunk holds {support.EXACT_ID} verbatim and is not marked exact: {ranked[0]!r}"
    assert support.exact_lines(answer) == support.lines_holding(question), \
        f"`hits` is not W1-17's exact list for {question!r}: found {support.exact_lines(answer)}, " \
        f"expected {support.lines_holding(question)}"


def test_every_line_that_holds_an_exact_string_is_found_with_its_file_and_line(box, built):
    """CAP-11 and W1-17: the exact-match route is kept, so each line that holds the string is a hit of its own."""
    answer = box.search(built, support.EXACT_STRING)
    expected = sorted((rel, number) for rel, text in support.EXACT_FILES.items()
                      for number in support.line_numbers(text, support.EXACT_STRING))
    holding = sorted({(hit["path"], hit["line"]) for hit in answer["hits"] if support.EXACT_STRING in hit["text"]})
    assert holding == expected, f"the lines that hold {support.EXACT_STRING!r}: found {holding}, expected {expected}"
    for hit in answer["hits"]:
        if (hit["path"], hit["line"]) in expected:
            lines = support.corpus()[hit["path"]].splitlines()
            assert hit["text"] == lines[hit["line"] - 1], f"the hit's text is not its line: {hit!r}"


# ---- W2-M072 (case) and W2-M100 (whole tokens)

def test_letter_case_does_not_change_what_a_plain_word_question_finds(box, built):
    """W2-M072: the same words in capitals find the same files in the route's ranked list."""
    lower, upper = support.PLAIN_QUESTION, support.PLAIN_QUESTION.upper()
    found_lower, found_upper = ranking(box, built, lower), ranking(box, built, upper)
    assert support.BEST in found_lower, f"{lower!r} does not find {support.BEST}: {found_lower}"
    assert set(found_upper) == set(found_lower), \
        f"{upper!r} finds {sorted(found_upper)}, {lower!r} finds {sorted(found_lower)}"


def test_a_word_matches_whole_tokens_only(box, built):
    """W2-M100: ``tern`` finds the file where it is a word, and not the one where it is the middle of a longer
    word (``lanternfish``)."""
    paths = order(box, built, support.WHOLE_WORD)
    assert support.WHOLE_FILE in paths, f"{support.WHOLE_WORD!r} does not find {support.WHOLE_FILE}: {paths}"
    assert support.INSIDE_FILE not in paths, \
        f"{support.WHOLE_WORD!r} matched inside a longer word in {support.INSIDE_FILE}: {paths}"
