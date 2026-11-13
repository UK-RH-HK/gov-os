"""S3: ``CONTINUATION_INVALID`` names the commit the token was made on and the store's commit now; the token carries
its store's commit (README).

A token is made on one planted store (``a``, C1) with ``--batch-size 1`` and replayed, with the same question and
arguments, on another (``b``, C2): given as two folders, and through one link switched between the two calls (as a
refresh between two pages). The refusal's message or details name both commits (each by its full id or at least
its first 12 hex digits).
"""

from __future__ import annotations

import json

import pytest

import w2_138_support as support

QUESTION = "lantern"
PAGED = ("--batch-size", "1")


def _token(capsys, root):
    run = support.search(capsys, QUESTION, "--root", root, *PAGED)
    assert run.ok, run.describe()
    token = run.result.get("continuation")
    assert token, f"premise: the first page carries a continuation\n{run.describe()}"
    return token


def _assert_refused_naming(run, made_on, now):
    assert not run.ok and run.error.get("code") == "CONTINUATION_INVALID", (
        f"a token made on the store at {made_on[:12]} replayed on the store at {now[:12]} was not refused "
        f"CONTINUATION_INVALID\n{run.describe(1500)}")
    said = f"{run.error.get('message', '')}\n{json.dumps(run.error.get('details'))}"
    for commit, what in ((made_on, "the commit the token was made on"), (now, "the store's commit now")):
        assert support.names_commit(said, commit), f"the refusal does not name {what} ({commit}): {said}"


@pytest.mark.parametrize("given", ["two-folders", "one-link-switched"])
def test_s3_a_token_made_on_one_store_and_replayed_on_another_is_refused_naming_both_commits(stores, capsys, tmp_path,
                                                                                            given):
    if given == "two-folders":
        token = _token(capsys, stores.a)
        replay = support.search(capsys, QUESTION, "--root", stores.b, *PAGED, "--continue", token)
    else:
        link = support.link_to(tmp_path / "stores" / "integration", stores.a)
        token = _token(capsys, link)
        support.switch(link, stores.b)
        replay = support.search(capsys, QUESTION, "--root", link, *PAGED, "--continue", token)
    _assert_refused_naming(replay, stores.c1, stores.c2)


def test_s3_guard_a_token_replayed_on_the_store_it_was_made_on_carries_on(stores, capsys):
    token = _token(capsys, stores.a)
    run = support.search(capsys, QUESTION, "--root", stores.a, *PAGED, "--continue", token)
    # its page may hold only repeats of a parent the first page sent (W2-32 S7): the guard asks that it is accepted
    assert run.ok, f"the token, replayed on its own store, was refused\n{run.describe()}"
    assert run.result.get("batches"), f"the replay gave no page\n{run.describe()}"
