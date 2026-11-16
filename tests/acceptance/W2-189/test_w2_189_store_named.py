"""S2 and F3: every answer names the store it came from, how far it lags, and what it may not change (README).

``store.commit`` is the commit the store was built at (the fingerprints row's ``head``, W2-138), ``store.head`` the
store folder's HEAD at the call (the full hash) and ``store.stale`` the sorted tracked paths that changed between
the two, ``[]`` when they are equal. The function is ``gov.retrieval.retrieve.store_of(root)``; the command line's
form is ``result.store`` of ``gov retrieve --json``. The text form is held to its commit and the count only.
"""

from __future__ import annotations

import os
import re

import pytest
import w2_189_support as support

from gov.retrieval import retrieve as retrieve_module


def _named(store, commit, head, stale, where):
    assert store.get("commit") == commit, f"{where}: store.commit is {store.get('commit')!r}, the store was built at {commit}"
    assert store.get("head") == head, f"{where}: store.head is {store.get('head')!r}, HEAD is {head}"
    assert store.get("stale") == stale, f"{where}: store.stale is {store.get('stale')!r}, expected {stale!r}"


def _function_store(repo):
    return retrieve_module.store_of(retrieve_module.resolved(repo))


# --- S2 ------------------------------------------------------------------------------------------------------

def test_s2_store_of_names_the_commit_the_head_and_exactly_the_added_record(tmp_path):
    plant = support.plant(tmp_path)
    moved = support.add_record(plant.repo)
    _named(_function_store(plant.repo), plant.x, moved, [support.RECORD], "store_of")


def test_s2_the_json_output_carries_the_same_three_values_as_the_function(tmp_path, capsys):
    plant = support.plant(tmp_path)
    moved = support.add_record(plant.repo)
    run = support.search(capsys, plant.repo, support.STEADY_NOTE_WORD)
    assert run.ok, run.describe()
    store = support.store_entry(run)
    _named(store, plant.x, moved, [support.RECORD], "gov retrieve --json")
    function = _function_store(plant.repo)
    assert {key: store.get(key) for key in ("commit", "head", "stale")} == {key: function.get(key)
                                                                           for key in ("commit", "head", "stale")}


def test_s2_a_store_built_at_head_gives_empty_stale_and_a_commit_equal_to_head(tmp_path, capsys):
    plant = support.plant(tmp_path)
    assert plant.head == plant.x
    _named(_function_store(plant.repo), plant.x, plant.x, [], "store_of")
    run = support.search(capsys, plant.repo, support.STEADY_NOTE_WORD)
    assert run.ok, run.describe()
    _named(support.store_entry(run), plant.x, plant.x, [], "gov retrieve --json")


def test_s2_stale_is_sorted_and_names_a_path_once_however_many_commits_changed_it(tmp_path):
    plant = support.plant(tmp_path)
    support.commit(plant.repo, {"zz/last.md": "# Last\n\nAdded first, sorted last.\n"}, message="add zz")
    support.commit(plant.repo, {support.CHANGING: "# The changing note\n\nOnce.\n"}, message="change once")
    support.commit(plant.repo, {"aa/first.md": "# First\n\nAdded later, sorted first.\n"}, message="add aa")
    support.commit(plant.repo, {support.CHANGING: "# The changing note\n\nTwice.\n"}, message="change twice")
    store = _function_store(plant.repo)
    assert store.get("stale") == ["aa/first.md", support.CHANGING, "zz/last.md"], f"store.stale {store.get('stale')!r}"
    assert store.get("commit") == plant.x and store.get("head") == plant.head


def test_s2_an_empty_commit_moves_the_head_and_leaves_stale_empty(tmp_path):
    plant = support.plant(tmp_path)
    moved = support.commit(plant.repo, message="an empty commit")
    assert moved != plant.x
    _named(_function_store(plant.repo), plant.x, moved, [], "store_of")


def test_s2_the_text_form_names_the_store_s_commit_and_the_count_of_stale_paths(tmp_path, capsys):
    """Only what the ticket states: the output names the commit (12 digits, as W2-138's text case checks) and the
    count of stale paths as a number; the wording is open. The count is read from the line that names the commit,
    with the commit and the folder taken out of it, so a digit of a path is no count."""
    plant = support.plant(tmp_path)
    support.ordinary_commits(plant.repo)  # two stale paths
    run = support.gov(capsys, "retrieve", "--root", plant.repo, support.STEADY_NOTE_WORD)
    assert run.code == 0, run.describe()
    named = [line for line in run.out.splitlines() if plant.x[:12] in line]
    assert named, f"the text output names no store commit {plant.x[:12]}:\n{run.out[:600]}"
    line = named[0].replace(plant.x, " ").replace(plant.x[:12], " ").replace(str(plant.repo), " ")
    line = line.replace(os.path.realpath(plant.repo), " ")
    assert re.search(r"(?<![\w.])2(?![\w.])", line), (
        f"the line naming the commit holds no count of stale paths (two here): {named[0]!r}")


# --- F3: always named; tracked paths only; the walls as before ---------------------------------------------------

def _kind_result(kind, tmp_path, capsys):
    """A moved-head answer of each kind: an ordinary bundle, the stated gap (``UNRESOLVED_IDS``), and a bundle whose
    lexical facet stays unavailable (the index-time recipe changed)."""
    plant = support.plant(tmp_path)
    support.add_record(plant.repo)
    if kind == "bundle":
        return plant, support.search(capsys, plant.repo, support.STEADY_NOTE_WORD), [support.RECORD]
    if kind == "stated-gap":
        run = support.search(capsys, plant.repo, "DEC-4242")
        assert run.ok and run.result.get("stopping_reason") == "UNRESOLVED_IDS", (
            f"premise: an id that exists nowhere is a stated gap at the moved HEAD\n{run.describe(1500)}")
        return plant, run, [support.RECORD]
    rebuild = {support.REBUILD_REL: "lexical_split_identifiers: true\n"}
    support.commit(plant.repo, rebuild, message="switch an index-time method on")
    run = support.search(capsys, plant.repo, support.STEADY_NOTE_WORD)
    assert run.ok and run.result["stopping_reason"] == "FACET_UNAVAILABLE", f"premise: the recipe changed\n{run.describe(1500)}"
    return plant, run, sorted([support.RECORD, support.REBUILD_REL])


@pytest.mark.parametrize("kind", ["bundle", "stated-gap", "recipe-changed"])
def test_f3_the_moved_head_result_always_carries_commit_head_and_stale(kind, tmp_path, capsys):
    plant, run, stale = _kind_result(kind, tmp_path, capsys)
    store = support.store_entry(run)
    assert {"commit", "head", "stale"} <= set(store), f"{kind}: result.store carries {sorted(store)}"
    assert store["commit"] == plant.x and store["head"] == plant.head, f"{kind}: {store}"
    assert store["head"] != store["commit"]
    assert store["stale"] == stale, f"{kind}: store.stale {store['stale']!r}"


def test_f3_stale_holds_tracked_paths_only_untracked_and_ignored_files_never_appear(tmp_path, capsys):
    plant = support.plant(tmp_path)
    support.commit(plant.repo, {support.ENGINE: '"""The engine."""\n\n\ndef spin():\n    return "changed"\n'})
    support.write(plant.repo, {"scratch/early.txt": "an untracked note, changed after X\n",
                               "scratch/new.txt": "an untracked note, added after X\n",
                               "ignored/cache.txt": "an ignored cache, changed after X\n",
                               "ignored/new.txt": "an ignored file, added after X\n"})
    status = support.git(plant.repo, "status", "--porcelain", "--ignored").splitlines()
    assert any(line.startswith("??") for line in status) and any(line.startswith("!!") for line in status), (
        f"premise: the repository holds untracked and ignored changes: {status}")
    run = support.search(capsys, plant.repo, support.STEADY_NOTE_WORD)
    assert run.ok, run.describe()
    store = support.store_entry(run)
    assert store.get("stale") == [support.ENGINE], f"store.stale {store.get('stale')!r}: tracked paths only"
    assert store.get("stale") == _function_store(plant.repo).get("stale")


def test_f3_untracked_and_ignored_changes_alone_leave_stale_empty(tmp_path, capsys):
    plant = support.plant(tmp_path)
    support.write(plant.repo, {"scratch/new.txt": "untracked\n", "ignored/new.txt": "ignored\n",
                               "ignored/cache.txt": "an ignored cache, changed after X\n"})
    run = support.search(capsys, plant.repo, support.STEADY_NOTE_WORD)
    assert run.ok, run.describe()
    _named(support.store_entry(run), plant.x, plant.x, [], "gov retrieve --json")


def test_f3_a_walled_path_is_withheld_from_the_role_through_a_moved_head_search(tmp_path, capsys, monkeypatch):
    """The path map's ``role_paths`` wall (the way the existing wall cases plant one) holds at a moved head as at a
    fresh store: the walled ledger is retrievable from this store (no role), and the role is not handed it."""
    plant = support.plant(tmp_path)
    support.add_record(plant.repo)
    assert plant.head != plant.x
    open_run = support.search(capsys, plant.repo, support.WALLED_WORD)
    support.answered(open_run, path=support.WALLED)  # premise: with no role the walled file is served from the store
    monkeypatch.setenv("GOV_ROLE", support.WALLED_ROLE)
    walled = support.search(capsys, plant.repo, support.WALLED_WORD)
    assert walled.ok, walled.describe()
    assert support.WALLED not in support.evidence_paths(walled.result)
    assert all(support.WALLED_WORD not in item["text"] for item in walled.result["evidence"]), "its text is not served"
    shown = walled.result.get("role_filter") or {}
    assert shown.get("roles") == [support.WALLED_ROLE] and shown.get("withheld", {}).get("paths") == 1, (
        f"the filter is named, one path withheld: {shown}")
    other = support.search(capsys, plant.repo, support.STEADY_NOTE_WORD)  # the role still reads what is not walled
    support.answered(other, path=support.STEADY_NOTE)


def test_f3_the_role_s_search_through_the_function_is_walled_at_a_moved_head_too(tmp_path, monkeypatch):
    plant = support.plant(tmp_path)
    support.add_record(plant.repo)
    monkeypatch.setenv("GOV_ROLE", support.WALLED_ROLE)
    bundle = retrieve_module.retrieve(plant.repo, support.STEADY_NOTE_WORD, reranker=lambda: None)
    assert bundle["facets"]["lexical"]["available"] is True, f"premise: answered from the store: {bundle['facets']}"
    walled = retrieve_module.retrieve(plant.repo, support.WALLED_WORD, reranker=lambda: None)
    assert support.WALLED not in [item["path"] for item in walled["evidence"]]
    assert walled["role_filter"]["withheld"]["paths"] == 1, f"role_filter {walled['role_filter']}"
