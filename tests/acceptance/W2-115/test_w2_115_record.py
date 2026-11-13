"""S7: each close writes its close record (the commit closed, the runs and their counts, the review's verdict, every
red with its reason, the culprits sent back); a field missing from the record is a failed check.

Read from the session's ``unowned`` close (conftest.py): a scoped close of a STANDARD ticket with two unowned reds.

Red on today's code: today's record holds none of ``close``, ``commit``, ``selection``, ``runs``, ``review``,
``reds``, ``culprits``, ``clone``, ``nightly`` (it states ``test_runs`` and an ``evidence`` block instead), and today's
close refuses the planted reds, so no record is written.
"""

import re

import pytest

import w2_115_support as support


class _NoRecord(dict):
    """Stands for the record of a close that did not pass: any read fails the test that reads it (a failure in the
    test, not an error in its setup)."""

    def __init__(self, why):
        super().__init__()
        self.why = why

    def _fail(self, *_):
        raise AssertionError(self.why)

    __contains__ = __getitem__ = get = _fail


@pytest.fixture(scope="module")
def front(unowned):
    try:
        support.passed(unowned.run)
        return unowned.project.record()
    except AssertionError as why:
        return _NoRecord(f"no close record to read: {why}")


@pytest.mark.parametrize("key", support.RECORD_KEYS)
def test_the_close_record_holds_every_field(front, key):
    """S7: every field of the record is present; a missing one fails this check."""
    assert key in front, f"the close record lacks {key!r}: {sorted(front)}"


def test_the_record_names_the_commit_closed(front, unowned):
    """S7: ``commit`` is the full id of the commit closed."""
    commit = str(front.get("commit"))
    assert re.fullmatch(r"[0-9a-f]{40}", commit), f"commit is not a full id: {commit!r}"
    assert commit == unowned.closed_head, f"the record names another commit: {commit} != {unowned.closed_head}"


def test_the_record_names_the_runs_and_their_counts(front):
    """S7: ``runs`` lists each run by name with its passed, failed, errors and skipped counts."""
    runs = front.get("runs")
    assert isinstance(runs, list) and runs, f"no runs: {runs!r}"
    for run in runs:
        assert isinstance(run, dict) and str(run.get("name") or "").strip(), f"a run has no name: {run!r}"
        for key in support.RUN_COUNT_KEYS:
            assert isinstance(run.get(key), int) and not isinstance(run.get(key), bool), \
                f"a run does not count {key}: {run!r}"
    assert sum(r["failed"] + r["errors"] for r in runs) >= 2, f"the runs do not count the two reds: {runs}"


def test_the_record_names_the_review_s_verdict(front):
    """S7: ``review`` holds the computed verdict (READY for a STANDARD ticket without findings) and the probe record
    it read (none for a STANDARD ticket)."""
    review = front.get("review")
    assert isinstance(review, dict) and review.get("verdict") == support.READY, f"review: {review!r}"
    assert "record" in review, f"the review names no record field: {review!r}"


def test_the_record_names_each_red_with_its_reason(front, unowned):
    """S7: every red is named with its failure type, whether it was caused, its reason and its repair ticket."""
    for node in (unowned.known, unowned.load_sensitive):
        entry = support.red_entry(front, node)
        missing = [k for k in support.RED_KEYS if k not in entry]
        assert not missing, f"the red {node} lacks {missing}: {entry}"
        assert str(entry["reason"]).strip(), f"the red {node} has no reason: {entry}"


def test_the_record_names_the_culprits_sent_back(front):
    """S7: ``culprits`` is a list (empty: a single ticket with no caused red sends nothing back)."""
    assert front.get("culprits") == [], f"culprits: {front.get('culprits')!r}"


def test_the_record_names_the_clone_and_the_nightly_read(front):
    """S7: ``clone`` names its path, whether it was reused and why it was replaced; ``nightly`` whether the nightly's
    result was read and which record."""
    clone = front.get("clone")
    assert isinstance(clone, dict) and clone.get("path") == support.CLONE_REL, f"clone: {clone!r}"
    assert isinstance(clone.get("reused"), bool) and "replaced" in clone, f"clone: {clone!r}"
    nightly = front.get("nightly")
    assert isinstance(nightly, dict) and isinstance(nightly.get("read"), bool) and "record" in nightly, \
        f"nightly: {nightly!r}"
