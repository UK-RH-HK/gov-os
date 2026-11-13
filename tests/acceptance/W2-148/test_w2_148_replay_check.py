"""W2-148 S15 after DEC-1108 (2): the replay checks the CTO's call set against the guard's call log by sha256 both
ways before it re-judges anything (ACT-GUARD-CALLLOG-1 §2, §3 (a), §7 item 2).

Every case plants a path-map addition (an (a) ACT, so the after-check replays the guard), the call set (the ``calls``
setting) and the guard's log (the ``guard_calls`` setting) in its own world. ``w2_148_support.replay_set`` is a set
that agrees with its log both ways; each refused case breaks it in one way only. The recording guard
(``plant_guard(record=True)``) shows whether anything was re-judged and with which ``GOV_GUARD_CALLS_DIR`` and
``GOV_ROLE``.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

import w2_148_support as support
from w2_148_support import LIVE_SID, NEW_HIDDEN, OTHER_SID

LISTED = {"extra": {"replay_refused": ["call-q1"]}}
INPUTS = ("docs/notes.md", "docs/notez.md", "docs/invented.md", "README.md", f"{NEW_HIDDEN}/q.txt")


def _act(w):
    return w.ready("ACT-T-PM", [w.pathmap_addition()], review_kw=LISTED)


def _restored(w, b):
    support.assert_touched(w, b, "before")


def _refused_at_the_check(w, b, r, *named):
    """Undone with a P1, the reason naming each of ``named``, no input's text in it, and nothing re-judged."""
    assert r.out.get("result") == "undone", ("the replay's check did not refuse: the ACT was not undone", r.out,
                                             r.stderr[-3000:])
    _restored(w, b)
    assert w.p1s(b.act), "the replay's refusal was not pushed as a P1"
    text = support.told(w, b, r)
    missing = [n for n in named if n not in text]
    assert not missing, ("the refusal's reason does not name the mismatch", missing, text)
    leaked = [i for i in INPUTS if i in text]
    assert not leaked, ("the refusal's reason quotes an input's text", leaked)
    assert support.guard_runs(w) == [], "the guard was re-run before the call set passed its check"


def _base(w):
    support.plant_guard(w, record=True)
    return support.replay_set()


# --- refused: set to log ---------------------------------------------------------------------------------------------

def test_s15_dec1108_a_set_call_with_no_log_line_is_refused_and_named(world):
    """An invented call: in the set, in the window, never logged."""
    lines = _base(world)
    log = [support.logged(x) for x in lines if support.in_base_window(x)]
    support.plant_replay(world, lines + [support.set_call("call-invented", 4, "docs/invented.md")], log=log)
    b = _act(world)
    _refused_at_the_check(world, b, world.run(b), "call-invented")


def test_s15_dec1108_a_call_whose_input_was_altered_by_one_character_is_refused_and_named(world):
    """The set's input altered by one character after the call was logged; the line's own sha256 field still holds
    the logged hash, so only a hash recomputed from the event shows it."""
    lines = _base(world)
    log = [support.logged(x) for x in lines if support.in_base_window(x)]
    notes = next(x for x in lines if x["id"] == "call-notes")
    notes["event"]["tool_input"]["file_path"] = "docs/notez.md"
    support.plant_replay(world, lines, log=log)
    b = _act(world)
    _refused_at_the_check(world, b, world.run(b), "call-notes")


def test_s15_dec1108_a_hash_logged_only_under_another_session_is_refused_and_named(world):
    lines = _base(world)
    log = [support.logged(x, session=OTHER_SID) if x["id"] == "call-notes" else support.logged(x)
           for x in lines if support.in_base_window(x)]
    support.plant_replay(world, lines, log=log)
    b = _act(world)
    _refused_at_the_check(world, b, world.run(b), "call-notes")


# --- refused: log to set ---------------------------------------------------------------------------------------------

def test_s15_dec1108_a_logged_live_call_missing_from_the_set_is_refused_and_named(world):
    """The CTO dropped a logged live call from the set: named by its session's first 8, its sha256's first 12, its
    time as the log gives it."""
    lines = _base(world)
    log = [support.logged(x) for x in lines if support.in_base_window(x)]
    notes = next(x for x in lines if x["id"] == "call-notes")
    support.plant_replay(world, [x for x in lines if x is not notes], log=log)
    b = _act(world)
    gone = support.logged(notes)
    _refused_at_the_check(world, b, world.run(b), LIVE_SID[:8], gone["sha256"][:12], gone["time"][:16])


# --- refused: the window ---------------------------------------------------------------------------------------------

def test_s15_dec1108_a_window_shorter_than_48_hours_is_refused(world):
    lines = _base(world)
    support.plant_replay(world, lines, header=support.set_header(since_h=47.0, until_h=0.0))
    b = _act(world)
    _refused_at_the_check(world, b, world.run(b), "window short")


def test_s15_dec1108_a_stale_window_is_refused(world):
    """``until`` 13 hours before the clock (``replay_stale_h`` left at its default, 12); 49 hours long."""
    lines = _base(world)
    support.plant_replay(world, lines, header=support.set_header(since_h=62.0, until_h=13.0))
    b = _act(world)
    _refused_at_the_check(world, b, world.run(b), "window stale")


def test_s15_dec1108_a_set_with_no_header_is_refused(world):
    lines = _base(world)
    support.plant_replay(world, lines, header=None)
    b = _act(world)
    _refused_at_the_check(world, b, world.run(b), "no header")


# --- refused: the log ------------------------------------------------------------------------------------------------

def test_s15_dec1108_a_capped_day_in_the_window_is_refused(world):
    lines = _base(world)
    support.plant_replay(world, lines)
    (world.guard_calls / "2026-11-09.jsonl.capped").write_text("")
    b = _act(world)
    _refused_at_the_check(world, b, world.run(b), "log capped", "2026-11-09")


def test_s15_dec1108_a_malformed_log_line_is_refused(world):
    lines = _base(world)
    support.plant_replay(world, lines)
    with open(world.guard_calls / "2026-11-09.jsonl", "a") as f:
        f.write('{"v": 1, "time": "2026-11-09T05:00:00.000Z", "session": \n')
    b = _act(world)
    _refused_at_the_check(world, b, world.run(b), "log malformed", "2026-11-09")


def test_s15_dec1108_a_missing_log_folder_is_refused(world):
    lines = _base(world)
    support.plant_replay(world, lines)
    shutil.rmtree(world.guard_calls)
    b = _act(world)
    _refused_at_the_check(world, b, world.run(b), "log missing")


# --- not required ----------------------------------------------------------------------------------------------------

def test_s15_dec1108_guard_suite_sessions_other_trees_and_the_window_s_edge_are_not_required(world):
    """Logged calls absent from the set that the check does not require: a suite's fixed session name, a UUID
    session in a run, a scratch and an other tree, and a live call one minute after ``since``."""
    lines = _base(world)
    extra = [support.log_line(support.ago(5), support.action_sha("Read", {"file_path": "a"}), session="guard4-check",
                              tree="main"),
             support.log_line(support.ago(6), support.action_sha("Read", {"file_path": "b"}), tree="run"),
             support.log_line(support.ago(7), support.action_sha("Read", {"file_path": "c"}), session=OTHER_SID,
                              tree="scratch"),
             support.log_line(support.ago(8), support.action_sha("Read", {"file_path": "d"}), session=OTHER_SID,
                              tree="other"),
             support.log_line(support.ago(support.WINDOW_H - 1 / 60), support.action_sha("Read", {"file_path": "e"}),
                              session=OTHER_SID)]
    support.plant_replay(world, lines, extra_log=extra)
    b = _act(world)
    r = world.run(b)
    assert r.out.get("result") == "applied", (r.out, r.stderr[-3000:])
    assert support.guard_runs(world), "the replay re-judged nothing"


# --- the log's role wins ---------------------------------------------------------------------------------------------

@pytest.mark.parametrize("set_role,log_role,outcome", [("research", "engineer", "undone"),
                                                       ("engineer", "research", "applied")],
                         ids=["log-refuses", "log-allows"])
def test_s15_dec1108_the_log_s_role_wins_over_the_set_s_when_re_judging(world, set_role, log_role, outcome):
    """A role-aware planted guard refuses the new hidden glob only to the path map's refused roles (engineer, not
    research). call-role's set line says one role and its log line the other: it is judged with the log's."""
    support.plant_guard(world, record=True, role_aware=True)
    role = support.set_call("call-role", 3, f"{NEW_HIDDEN}/role.txt", role=set_role)
    lines = support.replay_set() + [role]
    log = [support.logged(x, role=log_role) if x is role else support.logged(x)
           for x in lines if support.in_base_window(x)]
    support.plant_replay(world, lines, log=log)
    b = _act(world)
    r = world.run(b)
    assert r.out.get("result") == outcome, (r.out, r.stderr[-3000:])
    runs = [x for x in support.guard_runs(world) if x.get("path") == f"{NEW_HIDDEN}/role.txt"]
    assert runs, "call-role was never re-judged"
    assert {x.get("role") for x in runs} == {log_role}, ("call-role was not judged with its log line's role", runs)
    if outcome == "undone":
        _restored(world, b)
        assert world.p1s(b.act)
        text = support.told(world, b, r)
        wrong = [p for p in ("malformed",) + support.CHECK_PHRASES if p in text]
        assert not wrong, ("refused at the check, not at the re-judging", wrong, text)


# --- the live log untouched ------------------------------------------------------------------------------------------

def test_s15_dec1108_the_replay_s_hook_runs_never_name_or_change_the_live_log(world):
    lines = _base(world)
    support.plant_replay(world, lines)
    before = {p.name: support.sha256_file(p) for p in sorted(world.guard_calls.iterdir())}
    b = _act(world)
    r = world.run(b)
    assert r.out.get("result") == "applied", (r.out, r.stderr[-3000:])
    runs = support.guard_runs(world)
    assert runs, "the replay re-judged nothing"
    live = [world.guard_calls.resolve(), (world.home / ".gov-os" / "guard-calls").resolve()]
    for run in runs:
        d = run.get("dir")
        assert d and Path(d).is_absolute(), ("a replay hook run without an absolute GOV_GUARD_CALLS_DIR", run)
        rd = Path(d).resolve()
        assert not any(rd == x or x in rd.parents for x in live), ("a replay hook run named the live log", run)
    after = {p.name: support.sha256_file(p) for p in sorted(world.guard_calls.iterdir())}
    assert after == before, "a file in the guard's log folder changed"
