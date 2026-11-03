"""K2 (fail closed) and the failure line's second half [DEC-1014].

A base whose ``code`` fingerprint, ``embedder`` (model or revision) or ``schema`` differs from the tree's own build,
or a base with no readable record, is refused: ``seed.status`` is ``refused``, its ``reason`` names what differed
(``code fingerprint``, ``embedder model``, ``embedder`` for the revision, ``schema``, or that the base has no
``record``), and the rebuild runs cold and succeeds: its store is entry for entry a cold rebuild's, never one that
mixes two embedders.

The mismatch is made by building a base, then changing one value in its record; for the embedder, also by building
the base against a stand-in endpoint that reports another revision and gives other vectors, so that a store mixing
the two would be seen in its vectors.
"""

from __future__ import annotations

import pytest

import w2_122_support as support

W = support.WORDS


def _other(value):
    """Another value of the same kind."""
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 1
    if isinstance(value, float):
        return value + 1.0
    return f"other-{value}"


def _set_code(record):
    record["code"] = _other(record.get("code"))


def _set_schema(record):
    record["schema"] = _other(record.get("schema"))


def _set_model(record):
    record["embedder"]["model"] = "other-embedding:1b"


def _set_revision(record):
    revision = str(record["embedder"].get("revision") or "")
    record["embedder"]["revision"] = support.OTHER_REVISION + revision[len(support.OTHER_REVISION):]


CHANGES = {
    "code": (_set_code, "code fingerprint"),
    "schema": (_set_schema, "schema"),
    "embedder-model": (_set_model, "embedder model"),
    "embedder-revision": (_set_revision, "embedder"),
}


def _refused_then_cold(tree, base, env, embedder, named):
    """Seed ``tree`` from ``base``: refused naming ``named``, the rebuild succeeds and runs cold, and its store is a
    cold rebuild's entry for entry."""
    embedder.forget()
    run = support.rebuild(tree, env, "--seed", str(base))
    assert run.ok, f"a refused seed failed the rebuild (it must run cold and succeed)\n{run.describe()}"
    seed = support.seed_of(run)
    assert seed.get("status") == support.REFUSED, f"the mismatched base was not refused: seed = {seed}"
    reason = str(seed.get("reason") or "")
    assert named.lower() in reason.lower(), f"the refusal's reason does not name {named!r}: {reason!r}"
    sent = embedder.sent()
    assert W[support.KEPT] in sent and W[support.KEPT_TOO] in sent, \
        "after a refused seed the kept files were not embedded: the rebuild did not run cold"
    seeded = support.snapshot(tree, run)

    support.remove_store(tree)
    cold = support.snapshot(tree, support.built(tree, env))
    support.assert_same_store(seeded, cold)
    return run


@pytest.mark.parametrize("case", sorted(CHANGES))
def test_a_base_whose_record_differs_is_refused_named_and_the_rebuild_runs_cold(case, tree, base, env, embedder):
    change, named = CHANGES[case]
    support.change_record(base, change)

    _refused_then_cold(tree, base, env, embedder, named)


def test_a_base_with_no_record_is_refused_and_the_rebuild_runs_cold(tree, base, env, embedder):
    support.read_record(base)   # the premise: the base's full rebuild wrote one
    (base / support.RECORD_REL).unlink()

    _refused_then_cold(tree, base, env, embedder, "record")


def test_a_base_whose_record_cannot_be_read_is_refused_and_the_rebuild_runs_cold(tree, base, env, embedder):
    support.read_record(base)
    (base / support.RECORD_REL).write_bytes(b"\x00\xff not a record {")

    _refused_then_cold(tree, base, env, embedder, "record")


def test_a_base_built_by_another_embedder_revision_is_refused_and_never_mixed(box, embedder):
    """The base is built against an endpoint that reports another revision of the model and gives other vectors;
    the tree's endpoint reports the pin. A seed that used the base would leave the kept files' vectors from the
    other embedder: the store would differ from the cold one in those vectors."""
    other = support.OllamaStandIn(revision=support.OTHER_REVISION, salt="the other embedder ")
    try:
        base = support.make_base(box)
        support.built(base, support.environment(box, other.host))
    finally:
        other.close()
    tree = support.make_tree(box, base)
    env = support.environment(box, embedder.host)

    run = _refused_then_cold(tree, base, env, embedder, "embedder")

    assert run.result.get("stores", {}).get("semantic", {}).get("status") == "recreated", \
        f"the cold rebuild after the refusal did not recreate the semantic store: {run.result.get('stores')}"
