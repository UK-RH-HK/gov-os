"""K1 (seeded equals cold) and the failure line's first half [DEC-1014, SIZING-1].

``gov rebuild --seed <folder>`` takes the root of a warm base tree (the folder that holds that base's
``.gov-runtime/``; a link is followed), copies the base's stores into the tree, then rebuilds incrementally: only the
files whose content differs from the base's are re-embedded (seen at the embedding endpoint), and the result is the
same store, entry for entry, as a cold rebuild of the same tree (the digests, the stores' outcomes, every lexical
and semantic table row for row, every chunk's vector).

The planted repository: a base built cold at commit 1; a tree at commit 2 that changes one file, removes one and
adds one, seeded from the base, against a cold rebuild of that same tree (its store removed, rebuilt without seed).
"""

from __future__ import annotations

import os

import w2_122_support as support

W = support.WORDS


def _seeded(tree, env, embedder, folder):
    run = support.built(tree, env, "--seed", str(folder))
    seed = support.seed_of(run)
    assert seed.get("status") == support.SEEDED, f"the rebuild was not seeded: seed = {seed}\n{run.describe()}"
    return run


def _cold_again(tree, env, embedder):
    """Remove the tree's store and rebuild it cold; the cold run and the texts it sent."""
    support.remove_store(tree)
    embedder.forget()
    run = support.built(tree, env)
    return run, embedder.sent()


def test_a_seeded_rebuild_is_the_cold_rebuild_entry_for_entry(tree, base, env, embedder):
    seeded_run = _seeded(tree, env, embedder, base)
    seeded = support.snapshot(tree, seeded_run)
    assert support.vector_count(tree) > 0, "the seeded store holds no vector"

    cold_run, _ = _cold_again(tree, env, embedder)
    cold = support.snapshot(tree, cold_run)

    support.assert_same_store(seeded, cold)


def test_the_seed_names_the_base_it_read(tree, base, env, embedder):
    run = _seeded(tree, env, embedder, base)

    named = support.seed_of(run).get("base")
    assert isinstance(named, str) and named, f"the seed names no base: {support.seed_of(run)}"
    assert os.path.realpath(named) == os.path.realpath(base), \
        f"the seed names {named!r}, not the base it was given ({base})"


def test_a_seeded_rebuild_embeds_only_the_files_whose_content_changed(tree, base, env, embedder):
    _seeded(tree, env, embedder, base)
    sent = embedder.sent()

    for rel in (support.KEPT, support.KEPT_TOO):
        assert W[rel] not in sent, \
            f"{rel}, which the base held with the same content, was embedded again by the seeded rebuild"
    assert W[support.REMOVED] not in sent, "the removed file was embedded by the seeded rebuild"
    assert support.CHANGED_WORD in sent, f"the changed {support.CHANGED} was not re-embedded"
    assert W[support.ADDED] in sent, f"the added {support.ADDED} was not embedded"

    # The premise: a cold rebuild of the same tree embeds the kept files, so their absence above measures the seed.
    _, cold_sent = _cold_again(tree, env, embedder)
    assert W[support.KEPT] in cold_sent and W[support.KEPT_TOO] in cold_sent, \
        "the premise fails: a cold rebuild of the tree did not embed the kept files"


def test_a_file_removed_since_the_base_leaves_no_entry_in_the_seeded_store(tree, base, env, embedder):
    _seeded(tree, env, embedder, base)

    tables = support.store_tables(tree)
    held = [name for name, (_, rows) in tables.items()
            if any(support.REMOVED in row or W[support.REMOVED] in row for row in rows)]
    assert not held, f"the seeded store still holds {support.REMOVED} (removed since the base) in {held}"
    chunks = {row for row in tables.get("lexical_chunk", ([], []))[1]}
    assert any(support.ADDED in row for row in chunks), f"the seeded store holds no chunk of {support.ADDED}"


def test_a_link_to_the_base_is_followed(tree, base, env, embedder, box):
    link = box.base / "link-to-base"
    link.symlink_to(base, target_is_directory=True)

    seeded_run = _seeded(tree, env, embedder, link)
    sent = embedder.sent()
    seeded = support.snapshot(tree, seeded_run)

    assert W[support.KEPT] not in sent and W[support.KEPT_TOO] not in sent, \
        "seeded through a link, the kept files were embedded again: the base was not read"
    cold_run, _ = _cold_again(tree, env, embedder)
    support.assert_same_store(seeded, support.snapshot(tree, cold_run))


def test_seeding_leaves_the_base_unchanged(tree, base, env, embedder):
    before = support.store_tables(base)
    record_before = (base / support.RECORD_REL).read_bytes() if (base / support.RECORD_REL).is_file() else None

    _seeded(tree, env, embedder, base)

    assert not support.diff_tables(support.store_tables(base), before), "seeding a tree changed the base's store"
    record_after = (base / support.RECORD_REL).read_bytes() if (base / support.RECORD_REL).is_file() else None
    assert record_after == record_before, "seeding a tree changed the base's record"
