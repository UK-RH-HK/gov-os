"""S2 and S4 (with F3's "twice in 5 days without --force" and "started while another runs"): what starts an audit and
what refuses it before anything starts (Interface item 3).

The audit commit is the store link's HEAD (``git -C <link> rev-parse HEAD``); the audit's name is
``memory-audit-<yyyymmdd>`` of ``GOV_MEMAUDIT_NOW``'s UTC date. The checks, in order: ``RN-LOCK``, ``RN-NOBASE``,
``RN-RECENT``, ``RN-REBUILD``, ``RN-SIDE``, ``RN-STALE``, ``RN-NAME`` (the last judged by a ``STARTS.log`` line naming the audit, not by the
folder: PKG-W2-172-TESTS-1 TD-2 (b)). A refusal prints ``REFUSED <code>``, exits 1, starts no
child, adds nothing to ``STARTS.log`` and writes ``COUNTS.json`` with ``refused`` only where the audit's folder is new.

A start is shown by the planted launch script stopping at its first call (exit 10): the driver printed ``STEP writer-1``,
``STARTS.log`` has the line, and the run is a stop (exit 2), never a refusal. No search, no model, no build is made by
any case here (the fake ``gov`` and ``claude`` logs stay empty).
"""

from __future__ import annotations

import shutil
import time
from datetime import datetime, timedelta

import pytest

import w2_172_checks as C
import w2_172_world as W

STOP_AT_WRITER = {"writer-1": [{"exit": 10}]}
CODES = ["RN-LOCK", "RN-NOBASE", "RN-RECENT", "RN-REBUILD", "RN-SIDE", "RN-STALE", "RN-NAME"]


def started(world, run, *, audit=None, commit=None, force=False):
    """A start: the first launch was reached, the start is recorded, the run stopped there (exit 2)."""
    audit = audit or world.audit
    assert run.code == 2, run
    assert W.step_names(run)[:1] == ["writer-1"], run.out
    assert "STOPPED writer-1 10" in run.lines, run.out
    assert not any(line.startswith("REFUSED") for line in run.lines)
    line = world.starts()[-1]
    assert line["audit"] == audit and line["commit"] == (commit or world.audit_commit) and line["force"] is force, line
    assert datetime.fromisoformat(line["at"].replace("Z", "+00:00"))
    return line


def forget(world):
    """Remove the folder a refusal's ``COUNTS.json`` made. Under PKG-W2-172-TESTS-1 TD-2 (b) (DEC-1112 (3)) ``RN-NAME`` is
    judged by a ``STARTS.log`` line naming the audit (an audit started), never by the folder or by a refusal's
    ``COUNTS.json``, so a refused run can be retried on the same date with or without this call; the cases that call it
    keep their steps as they were, and ``test_s4_a_refused_run_is_not_a_start_and_the_same_date_can_be_retried`` shows
    the retry without it.

    Rewrite-Reason: PKG-W2-172-TESTS-1 TD-2 (b)"""
    shutil.rmtree(world.audit_dir, ignore_errors=True)


def hours_before(world, hours):
    return W.iso(W.parse_iso(world.now) - timedelta(hours=hours))


# -- S2 ---------------------------------------------------------------------------------------------------------------
def test_s2_a_fresh_commit_that_is_an_ancestor_starts_and_names_the_audit_by_the_date(make_world):
    world = make_world()
    world.plan_launch(STOP_AT_WRITER)
    run = world.go()
    assert world.audit == "memory-audit-20261110"
    line = started(world, run)
    assert (world.audit_dir / "COUNTS.json").is_file()
    assert world.stub_calls()[0]["argv"][world.stub_calls()[0]["argv"].index("--set") + 1] == "memory-audit-20261110"
    assert len(world.starts()) == 1 and line["audit"] == "memory-audit-20261110"
    assert world.gov_calls() == [] and world.claude_calls() == [], "nothing is searched or judged on the way"


def test_s2_the_audit_commit_is_the_commit_the_link_names_not_the_repositorys_head(make_world):
    world = make_world(now="2026-11-11T12:00:00Z", link_commit=None)
    meta = world.later_commit
    world.make_link(meta)  # the integration store's build is the later commit (an ancestor of main, 12 hours old)
    assert world.git_out("rev-parse", "HEAD").strip() != meta, "the repository's own head is a later commit still"
    world.plan_launch(STOP_AT_WRITER)
    run = world.go()
    started(world, run, commit=meta)
    assert world.audit == "memory-audit-20261111"
    argv = world.stub_calls()[0]["argv"]
    assert argv[argv.index("--commit") + 1] == meta and argv[argv.index("--set") + 1] == "memory-audit-20261111"


@pytest.mark.parametrize("hours,refused", [(23, False), (30, True)])
def test_s2_a_commit_more_than_24_hours_old_is_refused_and_nothing_is_built(make_world, hours, refused):
    now = W.iso(W.AUDIT_TIME + timedelta(hours=hours))
    world = make_world(now=now)
    world.plan_launch(STOP_AT_WRITER)
    before = W.W171.snapshot(world.link, world.sets)
    run = world.go()
    if refused:
        C.refused_without_a_start(world, run, "RN-STALE")
        assert W.W171.snapshot(world.link, world.sets) == before, "builds nothing"
    else:
        started(world, run)


def test_s2_a_commit_on_a_side_branch_is_refused_rn_side(make_world):
    world = make_world(link=True)
    side = world.commit_in_link(branch="side", date="2026-11-10T06:00:00+00:00")
    assert side != world.audit_commit
    run = world.go()
    C.refused_without_a_start(world, run, "RN-SIDE")


def test_s2_the_integrate_branch_is_the_main_line_when_it_exists(make_world):
    """``refs/heads/w2/integrate`` takes precedence over ``refs/heads/main``: the audit commit is an ancestor of main but not
    of an integrate branch at the base commit (refused); an integrate branch that holds it starts."""
    world = make_world()
    world.repo_git("branch", "w2/integrate", world.base_commit)
    run = world.go()
    C.refused_without_a_start(world, run, "RN-SIDE")
    forget(world)
    world.repo_git("branch", "-f", "w2/integrate", world.later_commit)
    world.plan_launch(STOP_AT_WRITER)
    started(world, world.go())


def test_s2_a_store_being_rebuilt_is_a_held_lock_not_a_file(make_world):
    world = make_world()
    lock = world.link.with_name(world.link.name + ".lock")
    with W.held_flock(lock):
        run = world.go()
    C.refused_without_a_start(world, run, "RN-REBUILD")
    assert lock.exists()
    forget(world)
    world.plan_launch(STOP_AT_WRITER)
    started(world, world.go())  # the lock file is still there, but no longer held: no rebuild is running


# -- the audits' log before anything (O3) -------------------------------------------------------------------------------
def test_s2_run_refuses_rn_nobase_while_the_audits_log_has_no_line(make_world):
    world = make_world()
    world.audits_log.unlink()
    C.refused_without_a_start(world, world.go(), "RN-NOBASE")
    forget(world)
    world.audits_log.write_text("")
    C.refused_without_a_start(world, world.go(force=True), "RN-NOBASE")
    forget(world)
    world.plant_audits({"time": "2026-11-02T00:00:00Z", "commit": world.base_commit, "run": "baseline",
                        "audit": "baseline"})
    world.plan_launch(STOP_AT_WRITER)
    started(world, world.go(), audit=world.audit)


# -- S4 ---------------------------------------------------------------------------------------------------------------
def test_s4_a_second_start_while_the_lock_is_held_is_refused_rn_lock(make_world):
    world = make_world()
    with W.held_flock(world.mem / "LOCK"):
        run = world.go()
    C.refused_without_a_start(world, run, "RN-LOCK")
    assert W.flock_free(world.mem / "LOCK")


def test_s4_two_runs_at_once_the_second_is_refused_and_the_lock_is_released_when_the_first_ends(make_world):
    world = make_world()
    world.plan_launch({"writer-1": [{"exit": 10, "sleep": 4}]})
    first = world.popen(*world.run_args())
    try:
        deadline = time.monotonic() + 60
        while not world.stub_calls() and time.monotonic() < deadline:
            time.sleep(0.2)
        assert world.stub_calls(), "the first run reached its first launch"
        second = world.go()
        assert second.code == 1 and "REFUSED RN-LOCK" in second.lines, second
    finally:
        out, err = first.communicate(timeout=120)
    assert first.returncode == 2 and "STOPPED writer-1 10" in out, (out, err)
    assert W.flock_free(world.mem / "LOCK"), "the lock goes when the run exits"
    assert len(world.starts()) == 1, "the refused second run is not a started audit"


@pytest.mark.parametrize("hours,force,outcome", [
    (72, False, "refused"),          # 3 days before now
    (119, False, "refused"),         # 4 days 23 hours: still under 5 x 24 h
    (121, False, "starts"),          # 5 days 1 hour
    (72, True, "starts"),            # --force lifts the refusal
])
def test_s4_a_start_within_5_days_of_the_last_is_refused_unless_force_is_given(make_world, hours, force, outcome):
    world = make_world()
    last = world.start_line(hours_before(world, hours))
    world.plant_starts(last)
    world.plan_launch(STOP_AT_WRITER)
    run = world.go(force=force)
    if outcome == "refused":
        C.refused_without_a_start(world, run, "RN-RECENT", starts_before=[last])
    else:
        line = started(world, run, force=force)
        assert world.starts() == [last, line]
        counts = world.counts()
        assert counts["force"] is force, counts
        assert counts.get("refused") in (None, False), counts


def test_s4_force_lifts_only_the_5_day_refusal(make_world):
    world = make_world()
    world.plant_starts(world.start_line(hours_before(world, 24)))
    world.audits_log.unlink()
    before = world.starts()
    C.refused_without_a_start(world, world.go(force=True), "RN-NOBASE", starts_before=before)
    forget(world)
    world.plant_audits({"time": "2026-11-02T00:00:00Z", "commit": world.base_commit, "run": "baseline",
                        "audit": "baseline"})
    with W.held_flock(world.link.with_name(world.link.name + ".lock")):
        run = world.go(force=True)
    C.refused_without_a_start(world, run, "RN-REBUILD", starts_before=before)
    forget(world)
    world.commit_in_link(branch="side", date="2026-11-10T06:00:00+00:00")
    C.refused_without_a_start(world, world.go(force=True), "RN-SIDE", starts_before=before)


def test_s4_a_second_start_on_the_same_date_is_refused_rn_name_and_writes_nothing_there(make_world):
    """``RN-NAME`` is judged by ``STARTS.log`` (an audit of that name started), so the first audit is planted as it leaves
    itself: its ``STARTS.log`` line and its folder with a digest and counts. ``--force`` lifts ``RN-RECENT`` only, so the
    refusal is ``RN-NAME``; the folder existed, so nothing is written into it.

    Rewrite-Reason: PKG-W2-172-TESTS-1 TD-2 (b)"""
    world = make_world()
    first = world.start_line(world.now, audit=world.audit)
    world.plant_starts(first)
    world.audit_dir.mkdir(parents=True)
    (world.audit_dir / "DIGEST.txt").write_text("the first audit's digest\n")
    (world.audit_dir / "COUNTS.json").write_text('{"audit": "first"}\n')
    before = W.W171.snapshot(world.audit_dir)
    run = world.go(force=True)
    C.refused_without_a_start(world, run, "RN-NAME", had_folder=True, starts_before=[first])
    assert W.W171.snapshot(world.audit_dir) == before, "the first audit's folder is left as it was"


@pytest.mark.parametrize("cause", ["RN-NOBASE", "RN-REBUILD"])
def test_s4_a_refused_run_is_not_a_start_and_the_same_date_can_be_retried(make_world, cause):
    """A refusal that wrote ``<R>/<A>/COUNTS.json`` (the folder was new) is no started audit: ``STARTS.log`` has no line
    naming ``<A>``, so once the cause is removed a retry on the same date starts (it reaches ``writer-1``) and is not
    ``RN-NAME``. The folder is not removed in between.

    Added: PKG-W2-172-TESTS-1 TD-2 (b)"""
    world = make_world()
    if cause == "RN-NOBASE":
        world.audits_log.unlink()
        refused = world.go()
    else:
        with W.held_flock(world.link.with_name(world.link.name + ".lock")):
            refused = world.go()
    C.refused_without_a_start(world, refused, cause)
    assert world.audit_dir.is_dir() and world.counts()["refused"] == cause, "the refusal wrote its counts there"
    if cause == "RN-NOBASE":
        world.plant_audits({"time": "2026-11-02T00:00:00Z", "commit": world.base_commit, "run": "baseline",
                            "audit": "baseline"})
    world.plan_launch(STOP_AT_WRITER)
    run = world.go()  # the same date, the folder as the refusal left it
    assert "REFUSED RN-NAME" not in run.lines, run.out
    line = started(world, run)
    assert world.starts() == [line], "only the start is a line of STARTS.log"
    assert world.counts().get("refused") in (None, False), world.counts()


@pytest.mark.parametrize("first,second", list(zip(CODES, CODES[1:])))
def test_s2_the_first_check_that_fails_refuses(make_world, first, second):
    """Each check wins over its successor when both would refuse: the order of item 3. RN-STALE holds from the start (the
    commit is 30 hours old).

    ``RN-NAME`` is judged by ``STARTS.log`` (a line naming the audit), with the first audit's folder as it leaves it. A
    line less than 5 days old is itself ``RN-RECENT``, which comes before ``RN-NAME``; so the line planted for
    ``RN-NAME`` is 6 days before now (older than 5 x 24 h) and ``RN-RECENT`` does not hold from it. Only the
    ``(RN-STALE, RN-NAME)`` pair holds ``RN-NAME`` and shows the order the case means to show: ``RN-STALE`` first.

    Rewrite-Reason: PKG-W2-172-TESTS-1 TD-2 (b)"""
    world = make_world(now=W.iso(W.AUDIT_TIME + timedelta(hours=30)))
    held = []

    def make_fail(code):
        if code == "RN-LOCK":
            held.append(W.held_flock(world.mem / "LOCK"))
        elif code == "RN-NOBASE":
            world.audits_log.unlink()
        elif code == "RN-RECENT":
            world.plant_starts(world.start_line(hours_before(world, 24)))
        elif code == "RN-REBUILD":
            held.append(W.held_flock(world.link.with_name(world.link.name + ".lock")))
        elif code == "RN-SIDE":
            world.commit_in_link(branch="side", date="2026-11-09T00:00:00+00:00")
        elif code == "RN-NAME":
            world.plant_starts(*world.starts(), world.start_line(hours_before(world, 6 * 24), audit=world.audit))
            world.audit_dir.mkdir(parents=True, exist_ok=True)

    for code in (first, second):
        make_fail(code)
    for cm in held:
        cm.__enter__()
    try:
        starts_before = world.starts()
        run = world.go()
    finally:
        for cm in held:
            cm.__exit__(None, None, None)
    C.refused_without_a_start(world, run, first, had_folder="RN-NAME" in (first, second), starts_before=starts_before)


def test_f3_every_refusal_prints_its_code_and_is_not_a_started_audit(make_world):
    """The printed form of a refusal: the one line ``REFUSED RN-<CODE>``, and the digest's own refusal line when a digest
    is written for it."""
    from w2_172_digest import by_word
    world = make_world()
    world.audits_log.unlink()
    run = world.go()
    C.refused_without_a_start(world, run, "RN-NOBASE")
    assert [x for x in run.lines if x.startswith("REFUSED")] == ["REFUSED RN-NOBASE"]
    digest = world.audit_dir / "DIGEST.txt"
    if digest.exists():
        words = by_word(digest.read_text().splitlines(), strict=False)
        assert words["STOP"]["refused"] == "RN-NOBASE" and words["OWNER"]["word"] == "OWNER none"
        assert run.lines[-12:] == digest.read_text().splitlines()
