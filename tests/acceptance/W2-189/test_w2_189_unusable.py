"""F2: a store that cannot be answered from still stops ``FACET_UNAVAILABLE`` with its reason, as today (README).

One case each: no store, an empty store, a corrupt store file, a changed index-time recipe (the keyword index's
``lexical_split_identifiers``, DEC-1068 M4, and the vectors' ``embed_headers``, DEC-1067 order (5)). Each is combined
with a moved HEAD (a commit after X), so a path that answers from the last good store cannot answer these. They are
guards: the reasons are the ones the code before W2-189 gives (checked on it), and must not change.
"""

from __future__ import annotations

import shutil

import pytest
import w2_189_support as support

from gov.retrieval import lexical, semantic
from gov.store import STORE_REL


def _move(plant, how):
    if how == "unmoved":
        return
    if how == "empty-commit":
        support.commit(plant.repo, message="an empty commit")
    elif how == "record":
        support.add_record(plant.repo)
    else:
        raise AssertionError(how)


def _stops_unavailable(run, reason, *, evidence=True):
    assert run.ok, run.describe()
    result = run.result
    assert result.get("stopping_reason") == "FACET_UNAVAILABLE", f"stopping {result.get('stopping_reason')!r}\n{run.describe(1500)}"
    assert support.lexical_facet(result) == {"available": False, "reason": reason}, support.lexical_facet(result)
    if evidence:
        assert result.get("evidence") == [], f"evidence is served from a store that cannot answer: {support.evidence_paths(result)}"


# --- no store ---------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("how", ["unmoved", "record"])
def test_f2_guard_no_store_is_missing_for_both_facets_and_gov_retrieve_says_so(how, tmp_path, capsys, semantic_endpoint):
    plant = support.plant(tmp_path)
    shutil.rmtree(plant.repo / ".gov-runtime")
    _move(plant, how)
    answer = lexical.search(plant.repo, support.STEADY_NOTE_WORD, refresh=False)
    assert (answer["available"], answer["reason"], answer["hits"]) == (False, "missing", [])
    vectors = semantic.search(plant.repo, support.STEADY_NOTE_WORD, refresh=False)
    assert (vectors["available"], vectors["reason"], vectors["hits"]) == (False, "missing", [])
    run = support.search(capsys, plant.repo, support.STEADY_NOTE_WORD)
    assert run.code != 0 and run.error.get("code") == "STORE_MISSING", run.describe()
    assert run.result.get("evidence") in (None, [])


# --- an empty store ---------------------------------------------------------------------------------------------

@pytest.mark.parametrize("how", ["unmoved", "empty-commit"])
def test_f2_guard_an_empty_store_stays_empty_and_stops_facet_unavailable(how, tmp_path, capsys):
    plant = support.plant(tmp_path, empty=True)
    _move(plant, how)
    answer = lexical.search(plant.repo, support.STEADY_NOTE_WORD, refresh=False)
    assert (answer["available"], answer["reason"], answer["hits"]) == (False, "empty", [])
    _stops_unavailable(support.search(capsys, plant.repo, support.STEADY_NOTE_WORD), "empty")


def test_f2_guard_an_empty_store_at_a_moved_head_with_a_changed_path_stays_unavailable(tmp_path, capsys):
    """The code before W2-189 says ``stale`` here (the changed path is checked first); ``empty`` is as true. Either
    reason; never available, never evidence."""
    plant = support.plant(tmp_path, empty=True)
    support.add_record(plant.repo)
    answer = lexical.search(plant.repo, support.STEADY_NOTE_WORD, refresh=False)
    assert answer["available"] is False and answer["hits"] == [] and answer["reason"] in ("empty", "stale"), answer
    run = support.search(capsys, plant.repo, support.STEADY_NOTE_WORD)
    assert run.ok and run.result.get("stopping_reason") == "FACET_UNAVAILABLE", run.describe()
    assert support.lexical_facet(run.result)["available"] is False
    assert support.lexical_facet(run.result)["reason"] in ("empty", "stale")
    assert run.result.get("evidence") == []


# --- a corrupt store file ---------------------------------------------------------------------------------------

@pytest.mark.parametrize("how", ["unmoved", "record"])
def test_f2_guard_a_corrupt_store_file_is_unreadable_and_stops_facet_unavailable(how, tmp_path, capsys):
    plant = support.plant(tmp_path)
    (plant.repo / STORE_REL).write_bytes(b"this is no database file " * 400)
    _move(plant, how)
    answer = lexical.search(plant.repo, support.STEADY_NOTE_WORD, refresh=False)
    assert (answer["available"], answer["reason"], answer["hits"]) == (False, "unreadable", [])
    _stops_unavailable(support.search(capsys, plant.repo, support.STEADY_NOTE_WORD), "unreadable")


# --- a changed index-time recipe: the keyword index's --------------------------------------------------------------

@pytest.mark.parametrize("how", ["uncommitted", "committed", "committed-and-moved"])
def test_f2_guard_a_changed_keyword_index_recipe_is_stale_and_stops_facet_unavailable(how, tmp_path, capsys):
    """``lexical_split_identifiers: true`` (M4) after the store was built without it: the store is not answered
    from, whether the setting file is a working-tree change, a commit, or a commit followed by another."""
    plant = support.plant(tmp_path)
    setting = {support.REBUILD_REL: "lexical_split_identifiers: true\n"}
    if how == "uncommitted":
        support.write(plant.repo, setting)
    else:
        support.commit(plant.repo, setting, message="switch an index-time method on")
    if how == "committed-and-moved":
        support.add_record(plant.repo)
    answer = lexical.search(plant.repo, support.STEADY_NOTE_WORD, refresh=False)
    assert (answer["available"], answer["reason"], answer["hits"]) == (False, "stale", [])
    _stops_unavailable(support.search(capsys, plant.repo, support.STEADY_NOTE_WORD), "stale")


# --- a changed index-time recipe: the vectors' ---------------------------------------------------------------------

@pytest.mark.parametrize("how", ["uncommitted", "committed", "committed-and-moved"])
def test_f2_guard_a_changed_embed_recipe_is_stale_for_the_semantic_facet_and_stops_facet_unavailable(
        how, tmp_path, capsys, semantic_endpoint):
    """``embed_headers: true`` after the vectors were built without headers (DEC-1067 order (5); DEC-1068's verify
    names 'a changed embed recipe'): the vectors are not answered from, with the moved HEAD or without."""
    plant = support.plant(tmp_path, semantic=True)
    setting = {support.REBUILD_REL: "embed_headers: true\n"}
    if how == "uncommitted":
        support.write(plant.repo, setting)
    else:
        support.commit(plant.repo, setting, message="switch the embedding recipe")
    if how == "committed-and-moved":
        support.add_record(plant.repo)
    sent = len(semantic_endpoint["sent"])
    answer = semantic.search(plant.repo, support.STEADY_NOTE_WORD, refresh=False)
    assert (answer["available"], answer["reason"], answer["hits"]) == (False, "stale", [])
    run = support.search(capsys, plant.repo, support.STEADY_NOTE_WORD)
    assert run.ok, run.describe()
    assert run.result.get("stopping_reason") == "FACET_UNAVAILABLE", run.describe(1500)
    assert run.result["facets"]["semantic"] == {"available": False, "reason": "stale"}, run.result["facets"]
    assert len(semantic_endpoint["sent"]) == sent, "no chunk is embedded: gov retrieve never rebuilds"
