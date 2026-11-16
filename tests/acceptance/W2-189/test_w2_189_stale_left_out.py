"""F1: text from a file changed since the store's commit is never served as current (README).

A path in ``store.stale`` is left out whole (a chunk of it, a hit of it, an evidence item of it) and named; a phrase
planted only after X is found nowhere. Each case first proves the store answers at the moved HEAD (a file no commit
touched is returned), so an empty answer cannot pass for a left-out one.
"""

from __future__ import annotations

import w2_189_support as support

from gov.retrieval import lexical, semantic


def _stale(run):
    return support.store_entry(run).get("stale")


def _texts(run):
    return [item.get("text", "") for item in run.result.get("evidence") or []]


def _premise(capsys, plant):
    """The store answers at the moved HEAD: the unchanged note is returned."""
    support.answered(support.search(capsys, plant.repo, support.STEADY_NOTE_WORD), path=support.STEADY_NOTE)


def test_f1_a_phrase_removed_from_a_file_after_x_is_not_returned_from_it_and_the_file_is_named(tmp_path, capsys):
    plant = support.plant(tmp_path)
    support.commit(plant.repo, {support.CHANGING: "# The changing note\n\nThe clause was rewritten.\n"})
    _premise(capsys, plant)
    run = support.search(capsys, plant.repo, support.CHANGING_WORD)
    assert run.ok, run.describe()
    assert lexical_available(run), f"premise: the lexical facet answers at the moved HEAD: {run.result.get('facets')}"
    assert support.CHANGING not in support.evidence_paths(run.result), "the file's old text is served as current"
    assert all(support.CHANGING_WORD not in text for text in _texts(run)), "the removed phrase is quoted"
    assert support.CHANGING in _stale(run), f"the left-out file is named: store.stale {_stale(run)!r}"


def test_f1_the_lexical_facet_gives_no_hit_and_no_ranked_chunk_of_a_stale_path(tmp_path):
    plant = support.plant(tmp_path)
    support.commit(plant.repo, {support.CHANGING: "# The changing note\n\nThe clause was rewritten.\n"})
    answer = lexical.search(plant.repo, support.STEADY_NOTE_WORD, refresh=False)
    assert answer["available"] is True, f"premise: the facet answers at the moved HEAD: {answer['reason']!r}"
    assert support.STEADY_NOTE in {hit["path"] for hit in answer["hits"]}
    stale = lexical.search(plant.repo, support.CHANGING_WORD, refresh=False)
    assert stale["available"] is True, f"the facet answers at the moved HEAD: {stale['reason']!r}"
    assert support.CHANGING not in {hit["path"] for hit in stale["hits"]}, f"hits {stale['hits']}"
    assert support.CHANGING not in {chunk["path"] for chunk in stale["ranked"]}, "a stale chunk is ranked"
    anything = lexical.search(plant.repo, "clause", refresh=False)  # a word the changed file holds before and after
    assert support.CHANGING not in {hit["path"] for hit in anything["hits"]}
    assert support.CHANGING not in {chunk["path"] for chunk in anything["ranked"]}


def test_f1_a_changed_file_is_left_out_whole_even_where_the_phrase_still_stands_in_it(tmp_path, capsys):
    """Two lines are put before the phrase: the file still holds it, at lines 5 and 6 now, and the store says 3. The
    old lines are never quoted: the path is stale, so none of it is returned."""
    plant = support.plant(tmp_path)
    old = (plant.repo / support.SHIFTED).read_text(encoding="utf-8")
    support.commit(plant.repo, {support.SHIFTED: "A preface the later commit adds.\n\n" + old})
    _premise(capsys, plant)
    run = support.search(capsys, plant.repo, support.SHIFTED_WORD)
    assert run.ok, run.describe()
    assert lexical_available(run), f"premise: the lexical facet answers at the moved HEAD: {run.result.get('facets')}"
    assert support.SHIFTED not in support.evidence_paths(run.result), "a changed file's chunk is served"
    assert support.SHIFTED in _stale(run)


def test_f1_a_phrase_planted_only_after_x_is_returned_from_no_file(tmp_path, capsys):
    plant = support.plant(tmp_path)
    support.ordinary_commits(plant.repo)  # the engine gains a function (the new word), a new note holds the other
    _premise(capsys, plant)
    for word, path in ((support.ENGINE_NEW_WORD, support.ENGINE), (support.NEWCOMER_WORD, support.NEWCOMER)):
        run = support.search(capsys, plant.repo, word)
        assert run.ok, run.describe()
        assert lexical_available(run), f"premise: the lexical facet answers at the moved HEAD: {run.result.get('facets')}"
        assert run.result["evidence"] == [], f"{word} is invented: {support.evidence_paths(run.result)}"
        assert path in _stale(run), f"{path} is named in store.stale {_stale(run)!r}"
    answer = lexical.search(plant.repo, support.NEWCOMER_WORD, refresh=False)
    assert answer["available"] is True and answer["hits"] == [] and answer["ranked"] == [], (
        f"the lexical facet at the moved HEAD: {answer}")


def test_f1_a_file_changed_after_x_is_not_quoted_by_its_old_text_either(tmp_path, capsys):
    """A changed source file keeps the word it held at X (the engine's gear) and gains a function: the word is gone
    from the answer because the path is stale, not because it was removed."""
    plant = support.plant(tmp_path)
    support.ordinary_commits(plant.repo)
    assert support.ENGINE_OLD_WORD in (plant.repo / support.ENGINE).read_text(encoding="utf-8")
    _premise(capsys, plant)
    run = support.search(capsys, plant.repo, support.ENGINE_OLD_WORD)
    assert run.ok, run.describe()
    assert lexical_available(run), f"premise: the lexical facet answers at the moved HEAD: {run.result.get('facets')}"
    assert support.ENGINE not in support.evidence_paths(run.result)
    assert support.ENGINE in _stale(run)


def test_f1_a_file_deleted_after_x_is_left_out_and_named_and_the_search_does_not_fail(tmp_path, capsys):
    """Key edge: a deleted file is a changed tracked path; its chunks are in the store and its text is gone."""
    plant = support.plant(tmp_path)
    support.commit(plant.repo, remove=[support.DOOMED], message="remove a note")
    assert not (plant.repo / support.DOOMED).exists()
    _premise(capsys, plant)
    run = support.search(capsys, plant.repo, support.DOOMED_WORD)
    assert run.ok, run.describe()
    assert lexical_available(run), f"premise: the lexical facet answers at the moved HEAD: {run.result.get('facets')}"
    assert support.DOOMED not in support.evidence_paths(run.result)
    assert support.DOOMED in _stale(run), f"the deleted path is named: store.stale {_stale(run)!r}"


def test_f1_the_semantic_facet_leaves_out_the_chunks_of_stale_paths(tmp_path, semantic_endpoint):
    plant = support.plant(tmp_path, semantic=True)
    support.ordinary_commits(plant.repo)
    support.commit(plant.repo, {support.CHANGING: "# The changing note\n\nThe clause was rewritten.\n"})
    answer = semantic.search(plant.repo, support.STEADY_NOTE_WORD, refresh=False)
    assert answer["available"] is True, f"premise: the semantic facet answers at the moved HEAD: {answer.get('reason')!r}"
    paths = {hit["path"] for hit in answer["hits"]}
    assert {support.STEADY_NOTE, support.STEADY_SRC} <= paths, f"the unchanged files have their hits: {sorted(paths)}"
    assert not paths & {support.ENGINE, support.CHANGING}, f"a stale path's chunk is a hit: {sorted(paths)}"


def lexical_available(run) -> bool:
    return support.lexical_facet(run.result).get("available") is True
