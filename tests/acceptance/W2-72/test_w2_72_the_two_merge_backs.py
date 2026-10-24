"""W2-72, KPI success 4 — the two merge-backs judge clean (DEC-918 item 3).

The KPI line: "judge_commits returns no finding for 03f470a5 and for 4ef3293a (W2-66's and W2-65's), read in this
repository's objects."

The two commits are the DEC-912 merge-backs of ``w2/integrate`` into ``w2/W2-66`` and ``w2/W2-65``, each made
by a ticket lead (``Role: orchestrator``) in its own call. ``judge_commits`` is called on this repository (the
project root, its own objects), read-only, on each merge commit alone, given by its full id, which the test
obtains with ``git rev-parse`` from the 8-digit form. A repository that does not hold the objects fails the test;
it is not skipped.

The guard ``_assert_the_premise`` shows from git's own answers that each is the shape DEC-918 lifts: two parents
with one merge base; acceptance tests that both parents changed against it; each held by the merge commit
exactly as ``git merge-tree --write-tree <first parent> <other parent>`` writes it, with no conflict on it. For
``03f470a5`` git reports a conflict on a file outside ``tests/acceptance/`` (``src/gov/close/command.py``, resolved
by hand), the per-file case.

``read_merge`` on each still holds those acceptance tests in ``own`` (DEC-918 item 4: the approval check's reading
is unchanged).

Red reason now: ``judge_commits`` returns one finding for each merge commit, "a merge commit's own change to a
ticket file or an acceptance test", naming ``tests/acceptance/W1-30/test_w1_30_close.py`` (``03f470a5``) and
``tests/acceptance/W1-26/README.md`` with ``tests/acceptance/W1-26/test_w1_26_planted_defects.py``
(``4ef3293a``). The ``read_merge`` case passes now.
"""

from __future__ import annotations

import pytest

import w2_72_support as support

ROOT = support.REPO_ROOT

# name: the merge-back's 8-digit form (never its full id: the test asks git for that)
MERGE_BACKS = {
    "W2-66-s-merge-back": "03f470a5",
    "W2-65-s-merge-back": "4ef3293a",
}


def _both_changed(merge_id):
    first, other = support.parents_of(ROOT, merge_id)
    bases = support.merge_bases(ROOT, first, other)
    assert len(bases) == 1, f"the premise fails: the parents of {merge_id[:12]} have the merge bases {bases}"
    return sorted(set(support.changed_since(ROOT, bases[0], first, support.ACCEPTANCE))
                  & set(support.changed_since(ROOT, bases[0], other, support.ACCEPTANCE)))


def _assert_the_premise(name, merge_id):
    parents = support.parents_of(ROOT, merge_id)
    assert len(parents) == 2, f"the premise fails: {merge_id[:12]} has the parents {parents}"
    assert support.trailer_values(ROOT, merge_id, "Role") == [support.ORCHESTRATOR], (
        f"the premise fails: {merge_id[:12]} does not carry Role: orchestrator in its final trailer block"
    )
    assert len(support.trailer_values(ROOT, merge_id, "Task")) == 1, (
        f"the premise fails: {merge_id[:12]} does not carry one Task trailer"
    )
    both = _both_changed(merge_id)
    assert both, f"the premise fails: no acceptance test was changed by both parents of {merge_id[:12]}"
    merged = support.git_s_own_merge(ROOT, *parents)
    for path in both:
        assert path not in merged.conflicted and support.content_at(ROOT, merge_id, path) == support.content_at(
            ROOT, merged.tree, path), (
            f"the premise fails: {merge_id[:12]} does not hold git's own clean merge of {path}"
        )
    if name == "W2-66-s-merge-back":
        assert merged.conflicted and not any(path.startswith(support.ACCEPTANCE + "/") for path in merged.conflicted), (
            f"the premise fails: git's own merge of {merge_id[:12]}'s parents reports the conflicts "
            f"{merged.conflicted}, not only outside {support.ACCEPTANCE}/"
        )
    return both


@pytest.mark.parametrize("name", sorted(MERGE_BACKS), ids=sorted(MERGE_BACKS))
def test_judge_commits_returns_no_finding_for_the_merge_back(judge, name):
    merge_id = support.full_id(ROOT, MERGE_BACKS[name])
    both = _assert_the_premise(name, merge_id)
    findings = judge(ROOT, [merge_id])
    assert findings == [], (
        f"judge_commits on {MERGE_BACKS[name]} ({name}), in this repository's objects, returns "
        f"{[(f.commit[:12], f.paths, f.reason) for f in findings]}, not no finding; the acceptance tests both "
        f"parents changed, {both}, are git's own clean merge (DEC-918 items 1 and 3)"
    )


@pytest.mark.parametrize("name", sorted(MERGE_BACKS), ids=sorted(MERGE_BACKS))
def test_read_merge_still_holds_the_cleanly_merged_acceptance_tests_in_own(read_merge, name):
    merge_id = support.full_id(ROOT, MERGE_BACKS[name])
    both = _assert_the_premise(name, merge_id)
    reading = read_merge(ROOT, merge_id)
    missing = [path for path in both if path not in reading.own]
    assert not missing, (
        f"read_merge on {MERGE_BACKS[name]} ({name}): `own` lacks {missing}, which both parents changed against "
        f"their merge base; the approval check's reading is to stay as it is (DEC-918 item 4, DEC-410 DP-24)"
    )
