"""W2-116 S1, F2 and freshness: ``gov rebuild --integration <branch>`` keeps the branch's head in two detached
worktrees outside the project, builds into the one not in use and switches the link only when the build succeeded;
a search during a build is answered from the ready one, with its facets available (README)."""

from __future__ import annotations

import contextlib

import w2_116_support as support
from w2_116_support import KEPT, KEPT_WORD, MERGED, MERGED_WORD


@contextlib.contextmanager
def held_build(project, env, embedder, what):
    """A build of the integration store started in the background and held half-way (in its semantic stage); it is
    released, and killed if it still runs, when the block ends."""
    embedder.hold()
    process = support.start_integration_build(project, env)
    try:
        support.wait_until_held(embedder, process, what)
        yield process
    finally:
        embedder.release()
        if process.poll() is None:
            try:
                process.communicate(timeout=support.COMMAND_TIMEOUT_S)
            except Exception:
                support.kill_build(process)


def test_s1_the_build_keeps_the_branch_head_in_a_detached_worktree_outside_the_project_behind_the_link(
        box, env, project):
    support.built_integration(project, env)
    ready = support.assert_link(box)
    assert support.outside(ready, project), f"the link points inside the project: {ready}"
    halves = support.worktrees(project)
    assert ready in halves, f"the link's target {ready} is no worktree of the project: {sorted(halves)}"
    assert halves[ready]["detached"], f"the half {ready} is not detached: {halves[ready]}"
    assert halves[ready]["head"] == support.head(project, support.BRANCH), (
        f"the half {ready} is at {halves[ready]['head']}, not the branch's head")
    run = support.search(project, env, KEPT_WORD, root=box.link)
    support.assert_answers(run, KEPT_WORD, KEPT, "a search through the link after the first build")


def test_s1_the_next_build_goes_into_the_other_half_and_the_two_alternate(box, env, project):
    support.built_integration(project, env)
    first = support.assert_link(box)
    h1 = support.head(project)
    h2 = support.land_h2(project)
    support.built_integration(project, env)
    second = support.assert_link(box)
    assert second != first, f"the second build did not switch the link to the other half (still {first})"
    halves = support.worktrees(project)
    assert halves.get(first, {}).get("head") == h1, f"the half not in use was not left at H1: {halves}"
    assert halves.get(second, {}).get("head") == h2, f"the new half is not at H2: {halves}"
    h3 = support.land(project, {"docs/third.md": support.note("cardamom")}, message="W2-116 H3")
    support.built_integration(project, env)
    third = support.assert_link(box)
    assert third == first, f"the third build did not go back into the first half: {third} (halves {first}, {second})"
    halves = support.worktrees(project)
    assert set(halves) == {first, second}, f"not exactly two worktrees behind the link: {sorted(halves)}"
    assert all(entry["detached"] for entry in halves.values()), f"a half is not detached: {halves}"
    assert halves[third]["head"] == h3 and halves[second]["head"] == h2, halves


def test_s1_failure2_a_search_during_a_build_is_answered_from_the_ready_half(box, env, embedder, project):
    support.built_integration(project, env)
    ready = support.assert_link(box)
    support.land_h2(project)
    with held_build(project, env, embedder, "the H2 build") as process:
        assert support.target(box) == ready, "the link moved while the build was still half-way"
        run = support.search(project, env, KEPT_WORD, root=box.link)
        support.assert_answers(run, KEPT_WORD, KEPT, "a search through the link during the build")
        run = support.search(project, env, MERGED_WORD, root=box.link)
        assert run.ok, f"a search through the link during the build did not answer\n{run.describe()}"
        support.assert_not_answered_with(run, MERGED, "a search through the link during the build")
        embedder.release()
        done = support.finish(process)
    assert done.ok, f"the held build did not succeed once released\n{done.describe()}"
    now = support.assert_link(box)
    assert now != ready, "the build succeeded but the link was not switched to the half it built"
    run = support.search(project, env, MERGED_WORD, root=box.link)
    support.assert_answers(run, MERGED_WORD, MERGED, "a search through the link after the build")


def test_s1_failure2_freshness_a_search_through_the_link_while_the_other_half_rebuilds_is_never_stale(
        box, env, embedder, project):
    support.built_integration(project, env)
    support.land_h2(project)
    with held_build(project, env, embedder, "the H2 build"):
        for question in (KEPT_WORD, support.CHANGED_WORD, "marjoram ledger harbour"):
            run = support.search(project, env, question, root=box.link)
            assert run.ok, f"a search through the link during the build did not answer\n{run.describe()}"
            support.assert_facets_available(run, f"a search for {question!r} through the link during the build")
            assert "stale" not in str(support.facets(run)).lower(), support.facets(run)


def test_s1_failure2_failure3_a_build_killed_half_way_leaves_the_link_and_the_ready_store_answers(
        box, env, embedder, project):
    support.built_integration(project, env)
    ready = support.assert_link(box)
    h1, vectors = support.head(project), support.vector_count(ready)
    support.land_h2(project)
    embedder.hold()
    process = support.start_integration_build(project, env)
    try:
        support.wait_until_held(embedder, process, "the H2 build")
        support.kill_build(process)
    finally:
        embedder.release()
        if process.poll() is None:
            support.kill_build(process)
    assert support.target(box) == ready, f"a build killed half-way moved the link to {support.target(box)}"
    assert support.worktrees(project).get(ready, {}).get("head") == h1, "the ready half was moved by the killed build"
    assert support.vector_count(ready) == vectors, "the ready half's semantic index changed under a killed build"
    run = support.search(project, env, KEPT_WORD, root=box.link)
    support.assert_answers(run, KEPT_WORD, KEPT, "a search through the link after a killed build")
    support.assert_not_answered_with(support.search(project, env, MERGED_WORD, root=box.link), MERGED,
                                     "a search through the link after a killed build")
    support.built_integration(project, env)   # the next build recovers the half the killed one left
    assert support.assert_link(box) != ready, "the build after the killed one did not switch to the other half"
    run = support.search(project, env, MERGED_WORD, root=box.link)
    support.assert_answers(run, MERGED_WORD, MERGED, "a search through the link after the recovering build")
