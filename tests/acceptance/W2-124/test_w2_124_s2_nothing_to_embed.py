"""S2: a project with nothing to embed is not asked for a semantic store, so its rebuild answers ok.

Ticket KPI S2: two planted projects, one with no path map and one whose path map names no embedded namespace, with the
embedder unavailable: ``gov rebuild`` exits 0 and prints ok for each, and names no semantic store.

Interface: asked for = no ``--no-embeddings`` AND the path map has a namespace with ``embedding_policy: embedded``;
otherwise ``stores.semantic`` = ``{status: not_recreated, requested: false, reason}`` and no embedder is called.
"S2 names no semantic store" = no ``REBUILD_FAILED``, no ``store: semantic`` in the output, ``semantic`` not in ``not_built``.
"""

from __future__ import annotations

import pytest

import w2_124_support as support

PROJECTS = {
    "no-path-map": {"path_map": "absent"},
    "path-map-without-an-embedded-namespace": {"path_map": "not embedded"},
    "template-path-map-no-policy": {"path_map": "template"},
}


def _names_no_semantic_store(run, label):
    output = run.stdout + run.stderr
    assert run.prints_ok, f"{label}: the rebuild did not print ok\n{run.describe()}"
    assert "REBUILD_FAILED" not in output, f"{label}: REBUILD_FAILED in the output\n{run.describe()}"
    assert "store: semantic" not in output, f"{label}: 'store: semantic' in the output\n{run.describe()}"
    listed = support.not_built_stores(run.result)
    assert listed is not None, f"{label}: the result has no not_built list\n{run.describe()}"
    assert "semantic" not in listed, f"{label}: semantic is in not_built: {listed}"


@pytest.mark.parametrize("name", sorted(PROJECTS))
def test_s2_nothing_to_embed_with_the_embedder_unavailable_prints_ok_and_is_not_asked(runs, name):
    run, _, _ = runs.rebuild(f"s2-{name}", embedder="dead", project_options=PROJECTS[name])
    _names_no_semantic_store(run, name)
    semantic = support.semantic_status(run.result)
    assert semantic.get("status") == "not_recreated" and semantic.get("requested") is False, \
        f"{name}: stores.semantic is not {{not_recreated, requested: false, reason}}: {semantic}"
    assert isinstance(semantic.get("reason"), str) and semantic["reason"].strip(), f"{name}: no reason: {semantic}"


@pytest.mark.parametrize("name", ["no-path-map", "path-map-without-an-embedded-namespace"])
def test_s2_no_embedder_is_called_when_nothing_is_to_be_embedded(runs, name):
    run, asked, _ = runs.rebuild(f"s2-called-{name}", embedder="healthy", project_options=PROJECTS[name])
    _names_no_semantic_store(run, name)
    assert asked == 0, f"{name}: the embedder was asked {asked} time(s) for a project with nothing to embed"
    assert support.semantic_status(run.result).get("requested") is False, \
        f"{name}: stores.semantic does not say requested: false: {support.semantic_status(run.result)}"
