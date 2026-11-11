"""K4 (the configured base, any adopted repository) [DEC-1014 item 6, DEC-982].

``gov rebuild --seed`` with no folder reads the warm base from the project's configuration: the key
``integration_store`` in ``governance/project/rebuild.yaml``, an absolute path. A project with no such key, or one
whose path holds no base, rebuilds cold with ``seed.status`` ``none`` and a ``reason`` that names it (``refused`` for
a base that is there but does not match). Nothing of this repository or machine is in the code: every project here is
a planted repository with its own ``rebuild.yaml`` naming its own base; and a base planted where this machine's
integration store lives (``~/gov-os-worktrees/W2-00-store`` under the ``HOME`` the rebuild is given) is never read.
"""

from __future__ import annotations

import os

import w2_122_support as support

W = support.WORDS


def _cold(run, embedder):
    sent = embedder.sent()
    assert W[support.KEPT] in sent and W[support.KEPT_TOO] in sent, \
        f"the kept files were not embedded: the rebuild did not run cold\n{run.describe()}"


def test_seed_without_a_folder_reads_the_configured_base(box, base, env, embedder):
    tree = support.make_tree(box, base, integration_store=base)

    run = support.built(tree, env, "--seed")

    seed = support.seed_of(run)
    assert seed.get("status") == support.SEEDED, f"the configured base was not seeded: seed = {seed}"
    assert os.path.realpath(str(seed.get("base"))) == os.path.realpath(base), \
        f"the seed names {seed.get('base')!r}, not the configured base {base}"
    sent = embedder.sent()
    assert W[support.KEPT] not in sent and W[support.KEPT_TOO] not in sent, \
        "seeded from the configured base, the kept files were embedded again"
    seeded = support.snapshot(tree, run)
    support.remove_store(tree)
    support.assert_same_store(seeded, support.snapshot(tree, support.built(tree, env)))


def test_a_project_with_no_configured_base_rebuilds_cold_named(box, base, env, embedder):
    """No ``integration_store`` key. A base is planted where this machine's integration store lives, under the
    ``HOME`` the rebuild is given: a path of this machine written into the code would find it."""
    machine_place = box.home / "gov-os-worktrees" / "W2-00-store"
    machine_place.parent.mkdir(parents=True)
    machine_place.symlink_to(base, target_is_directory=True)
    tree = support.make_tree(box, base)

    run = support.built(tree, env, "--seed")

    seed = support.seed_of(run)
    assert seed.get("status") == support.NONE, f"a project with no configured base was not answered none: {seed}"
    reason = str(seed.get("reason") or "")
    assert "integration_store" in reason or "rebuild.yaml" in reason, \
        f"the reason does not name the missing configuration (integration_store in rebuild.yaml): {reason!r}"
    _cold(run, embedder)


def test_a_configured_path_that_holds_no_base_rebuilds_cold_named(box, base, env, embedder):
    missing = box.base / "no-base-here"
    tree = support.make_tree(box, base, integration_store=missing)

    run = support.built(tree, env, "--seed")

    seed = support.seed_of(run)
    assert seed.get("status") == support.NONE, f"a configured path with no base was not answered none: {seed}"
    assert str(missing) in str(seed.get("reason") or ""), \
        f"the reason does not name the configured path {missing}: {seed.get('reason')!r}"
    _cold(run, embedder)


def test_a_configured_base_that_does_not_match_is_refused_and_the_rebuild_runs_cold(box, base, env, embedder):
    support.change_record(base, lambda record: record.update(schema=f"other-{record.get('schema')}"))
    tree = support.make_tree(box, base, integration_store=base)

    run = support.built(tree, env, "--seed")

    seed = support.seed_of(run)
    assert seed.get("status") == support.REFUSED, f"a configured base of another schema was not refused: {seed}"
    assert "schema" in str(seed.get("reason") or "").lower(), f"the refusal does not name the schema: {seed}"
    _cold(run, embedder)
