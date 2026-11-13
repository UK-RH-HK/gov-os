"""S5 (DEC-1083, moved from W2-88): a store not built is never ok-and-silent; the result is not complete and names it.

Ticket KPI S5 read by the owner's P2 (b): ``gov rebuild`` keeps exit 0 and ``"ok": true`` and its result carries
``complete: false`` and ``not_built: [{store, reason}]`` for every store not built (no path map, no ``.gitleaks.toml``, a
store the path map calls for not built). A rebuild with ``--no-embeddings`` is ok for the vectors it was told not to build
and says it skipped them. W2-26's finding 2 (an unadopted clone answering ``"ok": true``) stays ok, named in the result.

Naming of the lead's brief: ``not_built`` lists only stores that were to be built and were not; a store with
``requested: false`` is never in it; ``complete`` is true exactly when ``not_built`` is empty.
"""

from __future__ import annotations

import w2_124_support as support


def _not_built(run, label):
    result = run.result
    listed = result.get("not_built")
    if listed is None and result.get("complete") is True:   # a complete rebuild may leave the empty list out
        listed = []
    assert isinstance(listed, list), f"{label}: the result has no not_built list (and does not say complete)\n{run.describe()}"
    for entry in listed:
        assert isinstance(entry, dict) and isinstance(entry.get("store"), str) and entry["store"].strip(), \
            f"{label}: a not_built entry has no store: {entry}"
        assert isinstance(entry.get("reason"), str) and entry["reason"].strip(), \
            f"{label}: a not_built entry has no reason: {entry}"
    assert result.get("complete") is (not listed), \
        f"{label}: complete is {result.get('complete')!r} with not_built {listed}: complete is true exactly when it is empty"
    return listed


def _names(listed, *words):
    return [e for e in listed if any(word in e["reason"].lower() for word in words)]


def test_s5_no_path_map_is_ok_incomplete_and_named(runs):
    run, _, _ = runs.rebuild("s5-no-path-map", embedder="dead", project_options={"path_map": "absent"})
    assert run.prints_ok, f"the rebuild without a path map is not ok (exit 0, ok: true)\n{run.describe()}"
    listed = _not_built(run, "no path map")
    assert run.result.get("complete") is False, f"no path map: the result says complete\n{run.describe()}"
    assert _names(listed, "path map", "path-map"), f"no path map: no not_built entry names the path map: {listed}"


def test_s5_no_gitleaks_toml_is_ok_incomplete_and_named(runs):
    run, _, _ = runs.rebuild("s5-no-gitleaks", embedder="dead", project_options={"gitleaks": False},
                             args=("--json", "--no-embeddings"))
    assert run.prints_ok, f"the rebuild without .gitleaks.toml did not print ok (exit 0, ok: true; P2 (b))\n{run.describe()}"
    listed = _not_built(run, "no .gitleaks.toml")
    assert run.result.get("complete") is False, f"no .gitleaks.toml: the result says complete\n{run.describe()}"
    assert _names(listed, ".gitleaks.toml"), f"no .gitleaks.toml: no not_built entry names it: {listed}"


def test_s5_a_store_the_path_map_calls_for_and_not_built_is_named(runs):
    """The path map asks for code intelligence; no code-graph tool is on PATH, so the code index is not built."""
    run, _, _ = runs.rebuild("s5-code-index", embedder="dead", project_options={"code_intelligence": True},
                             args=("--json", "--no-embeddings"))
    assert run.prints_ok, f"the rebuild is not ok (exit 0, ok: true)\n{run.describe()}"
    listed = _not_built(run, "code index")
    assert run.result.get("complete") is False, f"the result says complete with the code index not built\n{run.describe()}"
    stores = [e["store"] for e in listed]
    assert "codeintel" in stores, f"the code index (stores.codeintel) the path map calls for is not in not_built: {listed}"


def test_s5_a_store_the_path_map_does_not_call_for_is_not_in_not_built(runs):
    """The same project but the path map does not ask for the code index: it is not 'not built', and nothing else is."""
    run, _, _ = runs.rebuild("s5-whole", embedder="healthy", project_options={"files": 5})
    assert run.prints_ok, f"the whole rebuild is not ok\n{run.describe()}"
    listed = _not_built(run, "a whole rebuild")
    assert listed == [] and run.result.get("complete") is True, \
        f"a rebuild that built what it was asked to is not complete: complete {run.result.get('complete')}, not_built {listed}"


def test_s5_no_embeddings_is_ok_and_says_it_skipped_the_vectors(runs):
    run, _, _ = runs.rebuild("s5-no-embeddings", embedder="dead", project_options={"files": 5},
                             args=("--json", "--no-embeddings"))
    assert run.prints_ok, f"--no-embeddings did not print ok\n{run.describe()}"
    listed = _not_built(run, "--no-embeddings")
    semantic = support.semantic_status(run.result)
    assert semantic.get("requested") is False, f"stores.semantic does not say requested: false: {semantic}"
    assert "--no-embeddings" in str(semantic.get("reason")), f"the semantic reason does not name --no-embeddings: {semantic}"
    assert "semantic" not in [e["store"] for e in listed], f"semantic (not asked for) is in not_built: {listed}"
    assert run.result.get("complete") is True, f"--no-embeddings on a project that built all else is not complete\n{run.describe()}"


def test_s5_w2_26_finding_2_an_unadopted_clone_stays_ok_and_is_named_incomplete(runs):
    """W2-26 finding 2, planted: a clone with no path map and no ``.gitleaks.toml`` built nothing and said ok."""
    run, _, _ = runs.rebuild("s5-unadopted-clone", embedder="dead",
                             project_options={"path_map": "absent", "gitleaks": False})
    assert run.prints_ok, f"the unadopted clone is no longer ok (exit 0, ok: true): P2 (b) keeps it ok\n{run.describe()}"
    listed = _not_built(run, "unadopted clone")
    assert run.result.get("complete") is False, f"the unadopted clone says complete\n{run.describe()}"
    assert listed, "the unadopted clone names no store not built"
    assert _names(listed, "path map", "path-map"), f"no not_built entry of the unadopted clone names the path map: {listed}"
