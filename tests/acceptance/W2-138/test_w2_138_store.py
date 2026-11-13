"""S1: every ``gov retrieve`` result names the store it answered from (README).

``--json`` carries ``result.store = {"commit": <the full commit the store was built at>, "root": <the store folder,
the link resolved once>}``; the text form's first line is ``store: <commit, 12 digits> (<folder>)``.
"""

from __future__ import annotations

import os
import re

import w2_138_support as support

FIRST_LINE = re.compile(r"store: ([0-9a-f]{12}) \((.+)\)")
QUESTION = "quillwort"


def _assert_names(run, commit, folder, link=None):
    assert run.ok, run.describe()
    store = support.store_of(run)
    assert store.get("commit") == commit, f"result.store.commit is {store.get('commit')!r}, the store's is {commit}"
    root = store.get("root")
    assert isinstance(root, str) and os.path.realpath(root) == str(folder), (
        f"result.store.root is {root!r}; the store folder is {folder}")
    if link is not None:
        assert root != str(link) and not os.path.islink(root), (
            f"result.store.root is the link {root!r}, not the folder it points to ({folder})")


def _first_line(run):
    assert run.code == 0, run.describe()
    lines = run.out.splitlines()
    assert lines, f"the text form printed nothing\n{run.describe()}"
    found = FIRST_LINE.fullmatch(lines[0])
    assert found, f"the text form's first line is {lines[0]!r}, not 'store: <12 digits> (<folder>)'"
    return found.group(1), found.group(2)


def test_s1_the_json_result_names_the_store_s_full_commit_and_folder(stores, capsys):
    run = support.search(capsys, QUESTION, "--root", stores.a)
    assert run.result.get("evidence"), f"premise: the question finds evidence in the store\n{run.describe()}"
    _assert_names(run, stores.c1, stores.a)


def test_s1_the_text_form_s_first_line_is_store_commit_12_digits_and_folder(stores, capsys):
    run = support.gov(capsys, "retrieve", "--root", stores.a, QUESTION)
    commit, folder = _first_line(run)
    assert commit == stores.c1[:12], f"the first line names {commit}, the store was built at {stores.c1}"
    assert os.path.realpath(folder) == str(stores.a), f"the first line names {folder!r}, the store is {stores.a}"


def test_s1_through_a_link_given_as_root_the_root_is_the_half_it_points_to(stores, capsys, tmp_path):
    link = support.link_to(tmp_path / "stores" / "integration", stores.a)
    _assert_names(support.search(capsys, QUESTION, "--root", link), stores.c1, stores.a, link)
    commit, folder = _first_line(support.gov(capsys, "retrieve", "--root", link, QUESTION))
    assert (commit, os.path.realpath(folder)) == (stores.c1[:12], str(stores.a)) and folder != str(link), (
        f"the text form names {commit} ({folder}) through the link to {stores.a}")
    support.switch(link, stores.b)
    _assert_names(support.search(capsys, QUESTION, "--root", link), stores.c2, stores.b, link)
    commit, folder = _first_line(support.gov(capsys, "retrieve", "--root", link, QUESTION))
    assert (commit, os.path.realpath(folder)) == (stores.c2[:12], str(stores.b)) and folder != str(link), (
        f"the text form names {commit} ({folder}) through the link switched to {stores.b}")


def test_s1_through_gov_store_with_no_root_the_root_is_the_half_the_link_points_to(stores, capsys, tmp_path,
                                                                                   monkeypatch):
    link = support.link_to(tmp_path / "stores" / "integration", stores.a)
    monkeypatch.setenv("GOV_STORE", str(link))
    _assert_names(support.search(capsys, QUESTION), stores.c1, stores.a, link)
    support.switch(link, stores.b)
    _assert_names(support.search(capsys, QUESTION), stores.c2, stores.b, link)
    commit, folder = _first_line(support.gov(capsys, "retrieve", QUESTION))
    assert (commit, os.path.realpath(folder)) == (stores.c2[:12], str(stores.b)), (
        f"the text form names {commit} ({folder}) through GOV_STORE's link to {stores.b}")


def test_s1_the_commit_is_the_one_the_store_was_built_at_not_a_later_head_of_its_folder(capsys, tmp_path,
                                                                                       monkeypatch):
    from gov.retrieval import lexical

    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    own = support.make_stores(tmp_path / "own")  # this case moves a folder's head, so it has stores of its own
    support.git(own.a, "commit", "-q", "--allow-empty", "-m", "a later commit, no rebuild")
    later = support.head(own.a)
    assert later != own.c1, "premise: the folder's head moved past the commit its store was built at"
    run = support.search(capsys, QUESTION, "--root", own.a)
    assert run.ok, run.describe()
    assert support.store_of(run).get("commit") == own.c1, (
        f"result.store.commit is {support.store_of(run).get('commit')!r}: the store was built at {own.c1}, "
        f"the folder's head is now {later}")


def test_s1_a_stated_gap_result_names_the_store_too(stores, capsys):
    run = support.search(capsys, "DEC-4242", "--root", stores.a)
    assert run.ok and run.result.get("stopping_reason") == "UNRESOLVED_IDS", (
        f"premise: an id that exists nowhere is a stated gap\n{run.describe()}")
    _assert_names(run, stores.c1, stores.a)
