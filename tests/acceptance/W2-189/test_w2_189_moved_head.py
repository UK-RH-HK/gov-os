"""S1 and S3: a store whose commit is not HEAD answers (README).

S1: one commit after the store's build that adds only a stage record under governance/adoption/. S3: two ordinary
commits later in the repository's life (one changes a source file, one adds a note), with no refresh hook installed.
In both, a query for a phrase in a file no commit touched since X returns that file in its evidence and the search
does not stop ``FACET_UNAVAILABLE``: through ``gov retrieve --json`` in process, through ``gov.retrieval.retrieve``,
and with the semantic facet's own status gate unpatched (``semantic_endpoint``).
"""

from __future__ import annotations

import w2_189_support as support

from gov.retrieval import retrieve as retrieve_module
from gov.retrieval import semantic


def _bundle(repo, question):
    return retrieve_module.retrieve(repo, question, reranker=lambda: None)


def _bundle_answered(bundle, path):
    paths = [item["path"] for item in bundle["evidence"]]
    assert bundle["facets"]["lexical"]["available"] is True, f"lexical facet: {bundle['facets']['lexical']}"
    assert bundle["stopping_reason"] != "FACET_UNAVAILABLE", (
        f"the search stopped FACET_UNAVAILABLE (facets {bundle['facets']}), evidence {paths}")
    assert path in paths, f"{path} is not in the evidence {paths}"


# --- S1: the adoption's closing commit -------------------------------------------------------------------------

def test_s1_guard_a_store_built_at_head_answers_from_its_unchanged_file(tmp_path, capsys):
    plant = support.plant(tmp_path)
    assert plant.head == plant.x, "premise: HEAD is the commit the store was built at"
    support.answered(support.search(capsys, plant.repo, support.STEADY_NOTE_WORD), path=support.STEADY_NOTE)


def test_s1_gov_retrieve_after_a_stage_record_commit_returns_the_unchanged_file(tmp_path, capsys):
    plant = support.plant(tmp_path)
    moved = support.add_record(plant.repo)
    assert moved != plant.x and plant.head == moved, "premise: HEAD moved past the commit the store was built at"
    run = support.search(capsys, plant.repo, support.STEADY_NOTE_WORD)
    support.answered(run, path=support.STEADY_NOTE)
    assert all(support.RECORD_WORD not in item["text"] for item in run.result["evidence"])


def test_s1_gov_retrieve_returns_a_source_file_the_commit_did_not_touch_too(tmp_path, capsys):
    plant = support.plant(tmp_path)
    support.add_record(plant.repo)
    support.answered(support.search(capsys, plant.repo, support.STEADY_SRC_WORD), path=support.STEADY_SRC)


def test_s1_gov_retrieval_retrieve_after_a_stage_record_commit_returns_the_unchanged_file(tmp_path):
    plant = support.plant(tmp_path)
    support.add_record(plant.repo)
    assert plant.head != plant.x
    _bundle_answered(_bundle(plant.repo, support.STEADY_NOTE_WORD), support.STEADY_NOTE)


def test_s1_the_semantic_facet_s_own_gate_is_available_at_the_moved_head(tmp_path, capsys, semantic_endpoint):
    """The status gate (``semantic._status`` over ``lexical._checked``) and the vectors built at X are the real ones;
    only the model calls are stand-ins. The facet answers at the moved HEAD, and so does the whole search."""
    plant = support.plant(tmp_path, semantic=True)
    support.add_record(plant.repo)
    assert plant.head != plant.x
    sent = list(semantic_endpoint["sent"])
    answer = semantic.search(plant.repo, support.STEADY_NOTE_WORD, refresh=False)
    assert answer["available"] is True, f"the semantic facet at the moved HEAD: {answer.get('reason')!r}"
    assert support.STEADY_NOTE in {hit["path"] for hit in answer["hits"]}, "the unchanged note has its vectors' hit"
    run = support.search(capsys, plant.repo, support.STEADY_NOTE_WORD)
    support.answered(run, path=support.STEADY_NOTE)
    assert run.result["facets"]["semantic"]["available"] is True, f"facets {run.result['facets']}"
    new = semantic_endpoint["sent"][len(sent):]
    assert all(text.startswith(semantic.INSTRUCTION) for text in new), (
        f"no chunk is embedded again (no rebuild inside gov retrieve): the vectors built at X are served; sent {new}")


# --- S3: ordinary commits later, no refresh hook ---------------------------------------------------------------

def test_s3_no_refresh_hook_is_installed_in_the_planted_repository(tmp_path):
    plant = support.plant(tmp_path)
    support.ordinary_commits(plant.repo)
    assert support.hooks_installed(plant.repo) == [], "premise of S3: nothing rebuilds the store after a commit"


def test_s3_gov_retrieve_after_two_ordinary_commits_answers_queries_on_unchanged_files(tmp_path, capsys):
    plant = support.plant(tmp_path)
    support.ordinary_commits(plant.repo)
    assert support.hooks_installed(plant.repo) == [] and plant.head != plant.x
    note = support.search(capsys, plant.repo, support.STEADY_NOTE_WORD)
    support.answered(note, path=support.STEADY_NOTE, also_not=(support.NEWCOMER, support.ENGINE))
    source = support.search(capsys, plant.repo, support.STEADY_SRC_WORD)
    support.answered(source, path=support.STEADY_SRC, also_not=(support.NEWCOMER, support.ENGINE))


def test_s3_gov_retrieval_retrieve_after_two_ordinary_commits_answers_from_the_store(tmp_path):
    plant = support.plant(tmp_path)
    support.ordinary_commits(plant.repo)
    assert plant.head != plant.x
    _bundle_answered(_bundle(plant.repo, support.STEADY_NOTE_WORD), support.STEADY_NOTE)
    _bundle_answered(_bundle(plant.repo, support.STEADY_SRC_WORD), support.STEADY_SRC)


def test_s3_the_answer_after_both_kinds_of_commit_is_still_named_by_its_commit(tmp_path, capsys):
    """S3 'named as in S2': after a record commit and two ordinary ones, the answer names X, the HEAD and the three
    paths changed since."""
    plant = support.plant(tmp_path)
    support.add_record(plant.repo)
    support.ordinary_commits(plant.repo)
    run = support.search(capsys, plant.repo, support.STEADY_NOTE_WORD)
    support.answered(run, path=support.STEADY_NOTE)
    store = support.store_entry(run)
    assert store.get("commit") == plant.x, f"store.commit {store.get('commit')!r}, the store was built at {plant.x}"
    assert store.get("head") == plant.head, f"store.head {store.get('head')!r}, HEAD is {plant.head}"
    assert store.get("stale") == sorted([support.RECORD, support.ENGINE, support.NEWCOMER]), (
        f"store.stale {store.get('stale')!r}")


def test_s3_the_semantic_facet_s_own_gate_is_available_after_ordinary_commits(tmp_path, capsys, semantic_endpoint):
    plant = support.plant(tmp_path, semantic=True)
    support.ordinary_commits(plant.repo)
    assert plant.head != plant.x and support.hooks_installed(plant.repo) == []
    answer = semantic.search(plant.repo, support.STEADY_SRC_WORD, refresh=False)
    assert answer["available"] is True, f"the semantic facet after two ordinary commits: {answer.get('reason')!r}"
    run = support.search(capsys, plant.repo, support.STEADY_SRC_WORD)
    support.answered(run, path=support.STEADY_SRC)
    assert run.result["facets"]["semantic"]["available"] is True, f"facets {run.result['facets']}"
