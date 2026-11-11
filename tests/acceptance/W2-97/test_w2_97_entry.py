"""KPI 1 (DEC-959 item 1, DEC-848): a ticket enters only with its approval; the queue merges it --no-ff onto the
integration head in a clean clone, runs the scoped set once on that merged result, and on green moves the branch by
fast-forward to that same merge commit: the commit tested is the commit landed. One writer: a second run waits for
nothing and changes nothing (exit 4)."""

from __future__ import annotations

import re
import subprocess

import pytest

import w2_97_support as S


def test_only_an_approved_ticket_enters(q):
    q.plant()
    h1 = q.code_moves_on()
    t = q.ticket(901, {"app/e.txt": "ok\n"})

    refused = q.approve(t.name)
    assert refused.returncode != 0, f"a ticket with no request was approved:\n{S.said(refused)}"
    assert q.names("approved") == [], "an approval with no request wrote an approval file"

    done = q.enqueue(t, commit=t.commit[:12])
    assert done.returncode == 0, S.said(done)
    request = q.entry("requested", t.name)
    assert request is not None, f"enqueue wrote no requested/{t.name}.json"
    assert (request["ticket"], request["task"], request["branch"]) == (t.name, t.task, t.branch), request
    assert request["commit"] == t.commit, f"the request's commit is not resolved to its full id: {request['commit']}"

    done = q.run()
    assert done.returncode == 0, f"a run with nothing approved: {S.said(done)}"
    assert q.head() == h1, "a request alone moved the integration branch"
    assert q.names("landed") == [] and q.names("ejected") == [], "a request alone entered the queue"
    assert q.test_calls() == [], "a request alone was tested"
    S.assert_main_unmoved(q)


def test_green_advances_to_the_very_merge_commit_tested(q):
    q.plant()
    t = q.ticket(901, {"app/e.txt": "ok\n"})
    h1 = q.code_moves_on()  # the head moved on since the ticket was cut: the merged code differs from the lead's
    q.submit(t)
    approval = q.entry("approved", t.name)
    assert approval["approved_by"] == "CTO" and approval["approved_at"], approval
    assert (approval["ticket"], approval["task"], approval["branch"], approval["commit"]) == \
        (t.name, t.task, t.branch, t.commit), approval
    assert q.entry("requested", t.name) is None, "approve left the request in requested/ (it moves it)"

    done = q.run()
    assert done.returncode == 0, S.said(done)

    head = q.head()
    assert q.parents(head) == [h1, t.commit], \
        f"the new head is not a --no-ff merge of the old head and the approved commit: {q.parents(head)}"
    runs = q.runs()
    assert len(runs) == 1, f"the merged result was not run exactly once: {len(runs)} runs"
    assert runs[0]["head"] == head, \
        f"the commit tested ({runs[0]['head']}) is not the commit landed ({head})"
    assert not str(runs[0]["cwd"]).startswith(str(q.repo)), "the run was not in a clone of its own"
    S.assert_landed_as(q, t, head)

    subject = q.git("log", "-1", "--format=%s", head)
    assert subject == f"Merge {t.branch} ({t.task}): merge queue", subject
    trailers = q.git("log", "-1", "--format=%(trailers:only,unfold)", head)
    assert re.search(rf"^Task: {re.escape(t.task)}$", trailers, re.M), trailers
    assert re.search(r"^Role: orchestrator$", trailers, re.M), trailers

    # The integration branch is checked out in the planted repository: that worktree is fast-forwarded.
    assert q.git("symbolic-ref", "HEAD") == f"refs/heads/{S.INTEGRATION}"
    assert q.git("status", "--porcelain") == "", "the checked-out integration worktree was left unclean"
    assert (q.repo / "app/e.txt").is_file(), "the checked-out integration worktree was not fast-forwarded"
    S.assert_main_unmoved(q)


def test_a_second_run_while_one_holds_the_lock_exits_4(q):
    q.plant()
    t = q.ticket(901, {"app/e.txt": "ok\n"})
    h1 = q.code_moves_on()
    q.submit(t)
    started, release = q.tmp / "first-run-started", q.tmp / "first-run-release"
    q.configure_tests(block={"started": str(started), "release": str(release)})

    first = q.start_run()
    try:
        S.wait_for(started)
        try:
            second = q.tool(*q.run_args(), timeout=60)
        except subprocess.TimeoutExpired:
            pytest.fail("a second run while one holds the lock did not exit at once (it waited or ran)")
        assert second.returncode == 4, f"a second run while one holds the lock: {S.said(second)}"
        assert second.stderr.strip(), "the second run gave no reason on stderr"
        assert q.head() == h1, "the second run moved the integration branch"
        assert len(q.runs()) == 1, "the second run tested while the first held the lock"
    finally:
        release.write_text("go")
        out, err = first.communicate(timeout=S.RUN_TIMEOUT_S)
    assert first.returncode == 0, f"the first run: exit {first.returncode}\n{out[-2000:]}\n{err[-2000:]}"
    S.assert_landed_as(q, t, q.head())
    S.assert_main_unmoved(q)
