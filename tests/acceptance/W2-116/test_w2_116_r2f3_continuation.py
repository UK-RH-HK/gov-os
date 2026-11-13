"""W2-116 R2-F3 (pass 2b, Q3 (a)): the continuation token ``gov retrieve`` makes carries the store folder it was made on
(the root as resolved once: a token made through the link names the half the link pointed at). Used against a store whose
resolved root is another folder it refuses ``CONTINUATION_INVALID`` naming both folders, even when the two folders are at
the same commit; used against the folder it was made on it pages as before (README, "Pass 2b").

Two folders at one commit are two detached worktrees of the planted project's branch head, each with its own full store.
A token without the mark (made before this pass) is not planted here: its form is the implementation's.
"""

from __future__ import annotations

import json
import os

import w2_116_s2_support as s2
import w2_116_support as support


def assert_refused_naming_both(run, made_on, now, what):
    error = run.envelope().get("error") or {}
    assert run.returncode != 0 and error.get("code") == "CONTINUATION_INVALID", (
        f"{what}: a token made on {made_on} was not refused CONTINUATION_INVALID on {now}\n{run.describe(1500)}")
    said = f"{error.get('message', '')}\n{json.dumps(error.get('details'))}"
    for folder, name in ((made_on, "the folder the token was made on"), (now, "the folder it was used against")):
        assert str(folder) in said, f"{what}: the refusal does not name {name} ({folder}): {said}"


def test_r2f3_a_token_made_on_one_folder_is_refused_on_another_at_the_same_commit(box, env, project):
    a = s2.built_half(project, box, env, "a")
    b = s2.built_half(project, box, env, "b")
    assert support.head(a) == support.head(b), "premise: the two folders are at one commit"
    token = s2.first_page_token(project, env, a)
    replay = s2.with_token(project, env, b, token)
    assert_refused_naming_both(replay, a, b, "two folders at one commit")


def test_r2f3_guard_a_token_used_on_the_folder_it_was_made_on_pages(box, env, project):
    a = s2.built_half(project, box, env, "a")
    token = s2.first_page_token(project, env, a)
    run = s2.with_token(project, env, a, token)
    assert run.ok, f"the token, used on its own folder, was refused\n{run.describe()}"
    assert run.result.get("batches"), f"the second page is empty\n{run.describe()}"


def test_r2f3_a_token_made_through_the_link_is_refused_once_the_link_points_at_the_other_half(box, env, project):
    a = s2.built_half(project, box, env, "a")
    b = s2.built_half(project, box, env, "b")
    s2.point(box.link, a)
    token = s2.first_page_token(project, env, box.link)
    # the link still points at the half the token was made on: the next page is that half's
    same = s2.with_token(project, env, box.link, token)
    assert same.ok, f"the token, used through the link while it still points at its half, was refused\n{same.describe()}"
    s2.point(box.link, b)                       # a switch between two pages, at the same commit
    assert os.path.realpath(box.link) == str(b)
    replay = s2.with_token(project, env, box.link, token)
    assert_refused_naming_both(replay, a, b, "the link switched to the other half at the same commit")


def test_r2f3_a_token_made_through_the_link_is_refused_on_the_other_half_used_directly(box, env, project):
    a = s2.built_half(project, box, env, "a")
    b = s2.built_half(project, box, env, "b")
    s2.point(box.link, a)
    token = s2.first_page_token(project, env, box.link)
    replay = s2.with_token(project, env, b, token)
    assert_refused_naming_both(replay, a, b, "a token made through the link names the half it pointed at")
