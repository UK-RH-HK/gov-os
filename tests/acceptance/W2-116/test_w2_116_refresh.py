"""W2-116 S4: the store is refreshed after every merge into the integration branch (the same command, idempotent at
an unchanged head), and it is the warm base ``gov rebuild --seed`` (W2-122) reads; a seed taken from a store behind
the integration head is named, and only what changed since is re-embedded (README)."""

from __future__ import annotations

import json

import w2_116_support as support
from w2_116_support import BEHIND, KEPT_WORD, MERGED, MERGED_WORD

UNCHANGED_WORDS = (KEPT_WORD, "marjoram")   # the two notes H2 leaves as they are


def assert_only_changed_embedded(embedder, what):
    texts = embedder.texts()
    sent = [text for text in texts if any(word in text for word in UNCHANGED_WORDS)]
    assert not sent, f"{what}: an unchanged note was embedded again: {sent[:2]}"
    assert any(MERGED_WORD in text for text in texts), (
        f"{what}: the note the merge added was not embedded ({len(texts)} texts sent)")


def test_s4_after_a_merge_the_refresh_brings_the_store_to_the_new_head(box, env, project):
    support.built_integration(project, env)
    h2 = support.land_h2(project)
    support.built_integration(project, env)
    ready = support.assert_link(box)
    assert support.worktrees(project).get(ready, {}).get("head") == h2, "the refreshed store is not at the new head"
    run = support.search(project, env, MERGED_WORD, root=box.link)
    support.assert_answers(run, MERGED_WORD, MERGED, "a search through the link after the refresh")


def test_s4_at_an_unchanged_head_the_refresh_does_nothing(box, env, embedder, project):
    support.built_integration(project, env)
    ready = support.assert_link(box)
    halves = support.worktrees(project)
    digests = {path: support.file_digest(f"{path}/{support.STORE_REL}") for path in halves}
    embedder.forget()
    again = support.built_integration(project, env)
    assert support.target(box) == ready, f"the refresh at an unchanged head moved the link\n{again.describe()}"
    assert support.worktrees(project) == halves, "the refresh at an unchanged head changed the worktrees"
    assert {path: support.file_digest(f"{path}/{support.STORE_REL}") for path in halves} == digests, (
        "the refresh at an unchanged head rewrote a store")
    assert embedder.texts() == [], f"the refresh at an unchanged head embedded {len(embedder.texts())} texts"


def test_s4_the_refresh_after_a_merge_re_embeds_only_what_the_merge_changed(box, env, embedder, project):
    support.built_integration(project, env)
    support.land_h2(project)
    embedder.forget()
    support.built_integration(project, env)
    assert_only_changed_embedded(embedder, "the refresh after the merge")


def test_s4_the_integration_store_is_the_warm_base_gov_rebuild_seed_reads(box, env, embedder, project):
    support.built_integration(project, env)
    ready = support.assert_link(box)
    tree = support.worktree(project, box.base / "worktrees" / "W2-901", branch="w2/W2-901")
    embedder.forget()
    run = support.rebuild(tree, env, "--seed")
    assert run.ok, run.describe()
    seed = run.result.get("seed") or {}
    assert seed.get("status") == "seeded", f"the integration store was not taken as the warm base: {seed}"
    assert seed.get("base") == ready, f"the seed read {seed.get('base')}, not the link's half {ready}"
    assert embedder.texts() == [], f"a seed at the store's own head embedded {len(embedder.texts())} texts"


def _seed_behind(box, env, embedder, project):
    """A store at H1 (hand-built), a merge to H2, a ticket worktree at H2 seeded from it."""
    support.hand_built_store(box, project, env)
    h1 = support.head(project)
    support.land_h2(project)
    tree = support.worktree(project, box.base / "worktrees" / "W2-901", branch="w2/W2-901")
    embedder.forget()
    run = support.rebuild(tree, env, "--seed")
    assert run.ok, run.describe()
    seed = run.result.get("seed") or {}
    assert seed.get("status") == "seeded", f"the store behind the head was not taken as the warm base: {seed}"
    return h1, seed


def test_s4_a_seed_from_a_store_behind_the_integration_head_is_named(box, env, embedder, project):
    h1, seed = _seed_behind(box, env, embedder, project)
    said = json.dumps(seed)
    assert h1[:12] in said and BEHIND in said.lower(), (
        f"the seed from a store at H1 ({h1[:12]}), behind the head, does not name its head and say {BEHIND!r}: "
        f"{seed}")


def test_s4_guard_a_seed_from_a_store_behind_the_head_re_embeds_only_what_changed(box, env, embedder, project):
    _seed_behind(box, env, embedder, project)
    assert_only_changed_embedded(embedder, "the seeded rebuild from a store behind the head")


def test_s4_guard_a_seed_from_a_store_at_the_head_does_not_say_behind(box, env, embedder, project):
    support.hand_built_store(box, project, env)
    tree = support.worktree(project, box.base / "worktrees" / "W2-901", branch="w2/W2-901")
    run = support.rebuild(tree, env, "--seed")
    assert run.ok, run.describe()
    seed = run.result.get("seed") or {}
    assert seed.get("status") == "seeded", seed
    assert BEHIND not in json.dumps(seed).lower(), f"a seed from a store at the head says {BEHIND!r}: {seed}"
