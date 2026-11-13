"""W2-116 S5, F2 and F3: a re-index never empties the semantic index; a model-less re-index reports the semantic
facet unavailable instead; a re-index that fails leaves the previous index and reports the failure (README)."""

from __future__ import annotations

import w2_116_support as support
from w2_116_support import KEPT, KEPT_WORD, MERGED, MERGED_WORD


def test_s5_failure2_failure3_a_model_less_re_index_of_the_integration_store_keeps_its_index_and_says_so(
        box, env, project):
    support.built_integration(project, env)
    ready = support.assert_link(box)
    h1, vectors = support.head(project), support.vector_count(ready)
    assert vectors, f"premise: the first build left no vectors at {ready}"
    support.land_h2(project)
    run = support.integration_build(project, {**env, "OLLAMA_HOST": support.closed_host()})
    semantic = (run.result.get("stores") or {}).get("semantic") or {}
    assert not (run.ok and semantic.get("status") == "recreated"), f"a model-less re-index succeeded\n{run.describe()}"
    assert "semantic" in (run.stdout + run.stderr).lower(), (
        f"a model-less re-index does not report the semantic facet\n{run.describe()}")
    assert support.target(box) == ready, f"a model-less re-index switched the link\n{run.describe()}"
    assert support.worktrees(project).get(ready, {}).get("head") == h1, "the ready half was moved"
    assert support.vector_count(ready) == vectors, "a model-less re-index changed the ready half's semantic index"
    answer = support.search(project, env, KEPT_WORD, root=box.link)
    support.assert_answers(answer, KEPT_WORD, KEPT, "a search through the link after a model-less re-index")
    support.built_integration(project, env)   # the model back: the next re-index switches
    answer = support.search(project, env, MERGED_WORD, root=box.link)
    support.assert_answers(answer, MERGED_WORD, MERGED, "a search through the link once the model is back")


def test_s5_guard_a_model_less_re_index_of_a_tree_keeps_its_vectors_and_reports_the_facet_unavailable(
        box, env, project):
    built = support.rebuild(project, env)
    assert built.ok, built.describe()
    vectors = support.vector_count(project)
    assert vectors, "premise: the tree's full rebuild left no vectors"
    support.land_h2(project)
    run = support.rebuild(project, {**env, "OLLAMA_HOST": support.closed_host()})
    # Rewrite-Reason: DEC-1027 C (the rebuild refuses an embedded namespace with no embedder); P1-L (a), DEC-1150 (3):
    # the model-less re-index now fails (exit 1, ``REBUILD_FAILED``, ``store: semantic``) and the semantic facet's
    # refusal is read from the stores in ``error.details``, not from a result.
    error = run.envelope().get("error") or {}
    assert run.returncode == 1 and run.envelope().get("ok") is False and error.get("code") == "REBUILD_FAILED", (
        f"a model-less re-index did not fail with REBUILD_FAILED\n{run.describe()}")
    assert (error.get("details") or {}).get("store") == "semantic", f"the failure names no semantic store\n{run.describe()}"
    semantic = ((error.get("details") or {}).get("stores") or {}).get("semantic") or {}
    assert semantic.get("status") != "recreated" and semantic.get("reason"), (
        f"a model-less re-index does not report the semantic facet unavailable\n{run.describe()}")
    assert support.vector_count(project) == vectors, (
        f"a model-less re-index changed the semantic index: {vectors} vectors before, "
        f"{support.vector_count(project)} after")
