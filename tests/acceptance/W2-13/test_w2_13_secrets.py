"""KPI failure 2: the secrets filter applies to the FTS5 table as to the old index: a planted canary is never indexed
[W1-17, W2-107, DEC-911].

A tracked file of the fixture (``secret/leaky.md``) holds a string of the project's canary rule, joined at run time;
a clean file beside it holds none. After ``gov rebuild --json`` (W2-107's content-hash cache on, in a place of the
case's own, in front of the filter):

- no row of any ordinary table of the store (the FTS5 tables read through their shadow tables) holds the canary, its
  own word, or the leaky file's own word; no term of any FTS5 table's vocabulary holds the canary's word; the store's
  files hold none of them as bytes;
- no lexical search for the canary, its words or the leaky file's words returns a hit in that file;
- ``gov retrieve`` cites nothing from that file;
- and the clean file is indexed, found and cited (so each check above can see what it looks for).

A second rebuild, answered from the cache, indexes the canary no more than the first.
"""

from __future__ import annotations

import pytest

import w2_13_support as support

pytestmark = pytest.mark.needs("git", "gitleaks", "sqlite_vec")


def leaked_needles():
    """The canary and the leaky file's own word: long enough that no vector's bytes hold them by chance (the
    canary's four-character word is looked for in the FTS5 vocabulary only)."""
    return [support.canary(), support.LEAKY_ONLY]


def check_store(root, workdir):
    """The rows, the bytes and the FTS5 terms of the store. The terms' check has a positive control (the clean
    file's word); the rows' has none, since an index may keep its text outside the store's rows (contentless)."""
    held = support.rows_holding(root, leaked_needles())
    assert not held, f"rows of the store hold the canary or the words of the file that holds it: {held}"
    for path in support.store_files(root):
        data = path.read_bytes().lower()
        found = [needle for needle in leaked_needles() if needle.lower().encode() in data]
        assert not found, f"{path.name} holds {len(found)} of the planted strings as bytes"
    # Whatever the tokenizer (words, stems or trigrams): the clean file's word stands in some term at least three
    # characters long, and no term holds three characters of the canary's own word.
    terms = support.vocabulary(root, workdir)
    assert terms, f"{support.STORE_REL} holds no FTS5 table"
    assert any(len(term) >= 3 and term.startswith(support.CLEAN_TERM[:3]) and
               (term in support.CLEAN_TERM or support.CLEAN_TERM in term) for words in terms.values() for term in words), \
        "premise: no FTS5 term holds the clean file's word, so the vocabulary check sees nothing"
    tail = support.CANARY_TAIL.lower()
    grams = {tail[start:start + 3] for start in range(len(tail) - 2)}
    leaked = {table: [term for term in words if any(gram in term for gram in grams)] for table, words in terms.items()}
    assert not any(leaked.values()), f"FTS5 tables hold terms of the canary: {sorted(t for t, v in leaked.items() if v)}"


def test_no_row_or_term_of_the_store_holds_the_canary(built, tmp_path):
    check_store(built, tmp_path)


def test_no_lexical_search_for_the_canary_or_its_words_finds_its_file(box, built):
    questions = [support.canary(), "ARGUS", support.CANARY_TAIL, "ARGUS TOKEN", support.LEAKY_WORDS,
                 support.LEAKY_ONLY]
    answers = box.searches(built, questions)
    for question, answer in answers.items():
        assert "raised" not in answer, f"search raised {answer.get('raised')} for a planted word"
        found = [hit["line"] for hit in support.check_answer(answer, question)["hits"] if hit["path"] == support.LEAKY]
        assert not found, f"a search for a planted word returned lines {found} of {support.LEAKY}"
    assert support.CLEAN in support.ranked_paths(box.search(built, support.CLEAN_WORDS)), \
        f"premise: the clean file {support.CLEAN} is not found by its own words"


def test_gov_retrieve_cites_nothing_from_the_file_that_holds_the_canary(box, built, ollama):
    for question in (support.LEAKY_WORDS, support.canary()):
        bundle = support.check_bundle(box.retrieve(built, question, host=ollama.host).result(), root=built)
        assert support.LEAKY not in support.cited_paths(bundle), f"gov retrieve cites {support.LEAKY}"
    bundle = support.check_bundle(box.retrieve(built, support.CLEAN_WORDS, host=ollama.host).result(), root=built)
    assert support.CLEAN in support.cited_paths(bundle), f"premise: the clean file {support.CLEAN} is not cited"


def test_a_second_rebuild_answered_from_the_secrets_cache_indexes_the_canary_no_more(box, repo, tmp_path):
    """The session's cache (``GOV_SECRETS_CACHE``, the box's own) already holds the fixture's clean verdicts from the
    shared store's rebuild; two more rebuilds of a fresh clone read from it."""
    box.rebuild(repo)
    box.rebuild(repo)
    check_store(repo, tmp_path)
    assert support.CLEAN in support.ranked_paths(box.search(repo, support.CLEAN_WORDS)), \
        f"the clean file {support.CLEAN} is not found after the second rebuild"
