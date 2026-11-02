"""KPI 2 (and F2): a cached vector is byte for byte what the embedder returned when it was stored; a rebuild of a tree
whose chunks are all cached embeds nothing, and its store equals the one built without the cache."""

from __future__ import annotations

import w2_126_support as S

QUESTION = "who reads the tide tables at the harbour"


def test_a_cached_vector_is_the_one_the_embedder_returned(box, stand_in, tmp_path):
    """The stand-in gives other vectors at every request: a vector computed again would differ."""
    stand_in.varying = True
    first = S.plant(tmp_path / "first")
    cold = box.build(first)
    sent_cold = len(stand_in.texts())
    [asked] = box.run(first, [S.query(QUESTION)])
    stored, returned = S.store_vectors(first), stand_in.returned()
    assert stored and set(stored.values()) <= returned, "the cold build stored vectors the embedder did not return"
    assert bytes.fromhex(asked["vector"]) in returned
    sent = len(stand_in.texts())

    second = S.clone(first, tmp_path / "second")
    warm = box.build(second)
    [again] = box.run(second, [S.query(QUESTION)])
    assert len(stand_in.texts()) == sent, "a tree whose texts are all cached sent texts to the embedder"
    assert S.store_vectors(second) == stored, "a cached vector differs from the one the embedder returned"
    assert again["vector"] == asked["vector"], "the cached question vector differs from the one returned"

    assert S.counts(cold)["hits"] == 0 and S.counts(cold)["misses"] == sent_cold, S.counts(cold)
    assert S.counts(warm)["misses"] == 0 and S.counts(warm)["hits"] > 0, S.counts(warm)
    assert S.counts(cold)["skipped"] is None and S.counts(warm)["skipped"] is None


def test_an_all_cached_rebuild_gives_the_store_built_without_the_cache(box, stand_in, tmp_path):
    """The reference store is built with a cache folder of its own, empty: every vector comes from the embedder."""
    reference = S.plant(tmp_path / "reference")
    box.build(reference, box.env(cache_dir=tmp_path / "empty-cache"))
    assert set(S.store_vectors(reference).values()) <= stand_in.returned()

    box.build(S.plant(tmp_path / "warming"))
    stand_in.reset()
    rebuilt = S.plant(tmp_path / "rebuilt")
    box.build(rebuilt)
    assert stand_in.texts() == [], "the rebuild of an all-cached tree embedded texts"
    assert S.store_vectors(rebuilt) == S.store_vectors(reference), "the store built with the cache differs"
    assert S.store_manifest(rebuilt) == S.store_manifest(reference)
