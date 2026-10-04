"""KPI success 2 (the scale figure) and KPI success 4, on the a-dev tier.

The a-dev tier is a synthetic product repository under ``GOV_DEV_TIERS``. The tests index a clone in a temporary
directory, never the tier itself, adopted with a path map that classes all of it as governance memory. The clone
is built and indexed once for this file; the tests run in the order written, one indexing job at a time.

"2.8 s scale" is tested with a generous bound on one call: the retrieval that follows one edited file, which
re-indexes it (package DP-3; compare DEC-278). The full build is not timed.
"""

from __future__ import annotations

import shutil

import pytest

import w1_17_support as support

pytestmark = pytest.mark.local_only


@pytest.fixture(scope="module")
def tier(api, tmp_path_factory):
    """``(root, tracked files before adoption, first refresh report)`` of an adopted, indexed clone of a-dev."""
    root = support.clone_tier(tmp_path_factory.mktemp("w1-17-tier") / "a-dev")
    if root is None:
        pytest.skip(f"no dev tier at {support.DEV_TIERS / support.DEV_TIER} (GOV_DEV_TIERS)")
    tracked = support.tracked(root)
    with open(root / ".git" / "info" / "exclude", "a", encoding="utf-8") as exclude:
        exclude.write("\n.gov-runtime/\n")  # derived state is never tracked, whatever the tier's own .gitignore says
    support.adopt(root, {"everything": (["**"], "governance")})
    support.commit(root, "adopted by the W1-17 tests")
    return root, tracked, api.refresh(root)


def test_the_whole_tier_is_indexed_and_no_canary_reaches_the_store(api, tier):
    root, tracked, report = tier
    holding = {rel: hits for rel, hits in support.files_holding(root, support.A_DEV_CANARIES).items()
               if not rel.startswith((".git/", support.RUNTIME_REL + "/"))}
    assert holding, "the a-dev tier holds none of its planted values"
    leaked = sorted(set(holding) & set(report["indexed"]))
    assert not leaked, f"files holding a dev canary were indexed: {leaked}"
    left = support.files_holding(root / support.RUNTIME_REL, support.A_DEV_CANARIES)
    assert not left, f"a dev canary stands in the derived store: {sorted(left)}"
    assert "README.md" in report["indexed"], "the tier's README.md was not indexed"
    assert len(report["indexed"]) > len(tracked) // 2, \
        f"{len(report['indexed'])} of {len(tracked)} tracked files were indexed: the corpus is gone"
    assert api.freshness(root)["status"] == "fresh"


def test_a_rebuild_of_the_tier_gives_the_same_digest(api, tier):
    root, _, report = tier
    shutil.rmtree(root / support.RUNTIME_REL)
    assert api.refresh(root)["digest"] == report["digest"]


def test_one_changed_file_is_re_indexed_by_the_next_retrieval_within_the_bound(api, tier):
    root, _, _ = tier
    text = (root / "README.md").read_text(encoding="utf-8").rstrip("\n")
    line = len(text.splitlines()) + 2
    support.write(root, "README.md", text + "\n\nThe magenta osprey was added by the W1-17 tests.\n")
    support.commit(root, "one file changes")
    answer, seconds = api.timed_search(root, "magenta osprey")
    assert support.places(answer) == [("README.md", line)]
    assert seconds < support.REINDEX_LIMIT_S, \
        f"the retrieval after one changed file took {seconds:.2f} s (bound {support.REINDEX_LIMIT_S:.0f} s)"
    assert api.refresh(root)["indexed"] == [], "the retrieval left changed blobs unindexed"
