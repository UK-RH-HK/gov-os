"""KPI success 5 (DEC-889): everything a rebuild builds is unchanged: the same stores, the same digest on the same
tree, and every key of today's result kept."""

from __future__ import annotations

import w2_76_support as support
from test_w2_76_timings import _healthy_endpoint  # the healthy stand-in endpoint (DEC-1027 C), defined beside its first use

pytestmark = support.needs_tools

TODAYS_KEYS = ("digest", "store", "stores", "compaction", "timing")


def test_two_full_rebuilds_of_the_same_tree_give_the_same_digest(box, lock, env):
    """Rewrite-Reason: DEC-1027 C (the rebuild refuses an embedded namespace with no embedder); P1-L (a), DEC-1150 (3):
    the project's namespace is embedded, so a full rebuild with no endpoint answering now fails instead of reporting
    the semantic stage ``not_recreated`` as it did. The two full rebuilds are given an endpoint that answers (the
    stand-in of ``test_w2_76_timings``), and the semantic line now asserts the stage ``recreated`` in both, with the
    same stores (so the same semantic answer) in both; every other assertion is as it was."""
    project = support.make_project(box, "project", lock)

    with _healthy_endpoint() as host:
        runs = [support.rebuild(project, {**env, "OLLAMA_HOST": host, "GOV_QUERY_OLLAMA_HOST": host})
                for _ in range(2)]

    for run in runs:
        assert run.returncode == 0 and run.envelope().get("ok") is True, run.describe()
        missing = [key for key in TODAYS_KEYS if key not in run.result]
        assert not missing, f"keys of today's result are gone: {missing}\n{run.describe()}"
        assert "lexical_s" in run.result["timing"], "today's lexical_s is gone"
        assert run.result["store"].get("digest") == run.result["digest"]
        stores = run.result["stores"]
        assert stores["lexical"]["status"] == "recreated", f"the lexical store was not rebuilt: {stores}"
        assert stores["semantic"]["status"] == "recreated", \
            f"with an endpoint answering, the full rebuild recreates the semantic store: {stores}"
    assert runs[0].result["digest"] == runs[1].result["digest"], "two rebuilds of the same tree gave two digests"
    assert runs[0].result["stores"] == runs[1].result["stores"], "two rebuilds of the same tree built different stores"
    assert runs[0].result["compaction"] == runs[1].result["compaction"]
