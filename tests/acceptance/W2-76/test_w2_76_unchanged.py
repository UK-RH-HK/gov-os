"""KPI success 5 (DEC-889): everything a rebuild builds is unchanged: the same stores, the same digest on the same
tree, and every key of today's result kept."""

from __future__ import annotations

import w2_76_support as support

pytestmark = support.needs_tools

TODAYS_KEYS = ("digest", "store", "stores", "compaction", "timing")


def test_two_full_rebuilds_of_the_same_tree_give_the_same_digest(box, lock, env):
    project = support.make_project(box, "project", lock)

    runs = [support.rebuild(project, env) for _ in range(2)]

    for run in runs:
        assert run.returncode == 0 and run.envelope().get("ok") is True, run.describe()
        missing = [key for key in TODAYS_KEYS if key not in run.result]
        assert not missing, f"keys of today's result are gone: {missing}\n{run.describe()}"
        assert "lexical_s" in run.result["timing"], "today's lexical_s is gone"
        assert run.result["store"].get("digest") == run.result["digest"]
        stores = run.result["stores"]
        assert stores["lexical"]["status"] == "recreated", f"the lexical store was not rebuilt: {stores}"
        assert stores["semantic"]["status"] == "not_recreated" and stores["semantic"].get("reason"), \
            f"with no endpoint answering, the semantic stage reports itself as today: {stores}"
    assert runs[0].result["digest"] == runs[1].result["digest"], "two rebuilds of the same tree gave two digests"
    assert runs[0].result["stores"] == runs[1].result["stores"], "two rebuilds of the same tree built different stores"
    assert runs[0].result["compaction"] == runs[1].result["compaction"]
