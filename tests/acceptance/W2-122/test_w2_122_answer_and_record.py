"""The answer and the base's record (the lead's interface for K1, K2 and K4) [DEC-1014, DEC-374].

- A rebuild given ``--seed`` answers a ``seed`` object: ``status`` one of ``seeded``, ``refused``, ``none``; the
  ``base`` it read (or none); a ``reason`` where it is not ``seeded``. Without ``--seed``, ``gov rebuild`` does not
  seed (today's behaviour).
- Every full rebuild writes ``.gov-runtime/rebuild/stores.json``: a JSON object with at least ``code`` (the
  fingerprint of the Gov OS code that built the stores), ``embedder`` (``model`` and ``revision``, as the semantic
  stage records them) and ``schema`` (the stores' schema version).
"""

from __future__ import annotations

import sqlite3

import w2_122_support as support

STATUSES = {support.SEEDED, support.REFUSED, support.NONE}


def _manifest(project):
    connection = sqlite3.connect((project / support.STORE_REL).resolve().as_uri() + "?mode=ro", uri=True)
    try:
        return connection.execute("SELECT embedder_model, embedder_revision FROM semantic_manifest").fetchone()
    finally:
        connection.close()


def test_a_full_rebuild_writes_the_record_of_its_stores(base):
    record = support.read_record(base)

    code = record.get("code")
    assert isinstance(code, str) and code.strip(), f"the record names no code fingerprint: {record}"
    embedder = record.get("embedder")
    assert isinstance(embedder, dict), f"the record names no embedder: {record}"
    model, revision = _manifest(base)
    assert embedder.get("model") == model == support.EMBED_MODEL, \
        f"the record's embedder model {embedder.get('model')!r} is not the semantic stage's {model!r}"
    assert embedder.get("revision") == revision, \
        f"the record's embedder revision {embedder.get('revision')!r} is not the semantic stage's {revision!r}"
    assert "schema" in record and record["schema"] not in (None, ""), f"the record names no schema version: {record}"


def test_the_same_code_and_embedder_write_the_same_record_in_two_trees(base, tree, env):
    support.built(tree, env)

    mine, theirs = support.read_record(tree), support.read_record(base)
    for key in ("code", "embedder", "schema"):
        assert mine.get(key) == theirs.get(key), \
            f"two trees rebuilt by the same code against the same endpoint record another {key}: " \
            f"{mine.get(key)!r} and {theirs.get(key)!r}"


def test_a_seeded_answer_has_its_form(tree, base, env):
    run = support.built(tree, env, "--seed", str(base))

    seed = run.result.get("seed")
    assert isinstance(seed, dict), f"the rebuild given --seed answers no seed object\n{run.describe()}"
    assert seed.get("status") in STATUSES, f"the seed's status {seed.get('status')!r} is none of {sorted(STATUSES)}"
    assert "base" in seed, f"the seed object does not name the base it read (or none): {seed}"
    if seed.get("status") != support.SEEDED:
        assert isinstance(seed.get("reason"), str) and seed["reason"].strip(), \
            f"the seed was not used and no reason names why: {seed}"


def test_without_seed_a_rebuild_does_not_seed(tree, base, env, embedder):
    """Today's behaviour: even with a base beside it, a rebuild without ``--seed`` embeds the whole tree."""
    run = support.built(tree, env)

    seed = support.seed_of(run)
    assert seed.get("status") != support.SEEDED, f"a rebuild without --seed was seeded: {seed}"
    sent = embedder.sent()
    for rel in (support.KEPT, support.KEPT_TOO):
        assert support.WORDS[rel] in sent, f"a rebuild without --seed did not embed {rel}: it was seeded"
