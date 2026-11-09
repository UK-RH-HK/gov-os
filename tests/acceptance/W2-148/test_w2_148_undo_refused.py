"""W2-148 DEC-1107 (F21, round 3 of this design): the owner's undo (S22's `undo ACT-<id> <sha8>` line) and the crash
recovery (the launcher finding an unfinished journal, S22) exit non-zero and say `refused` whenever they leave another's
file untouched, with the P1 naming each such file and the lock held (F15, DEC-1106 (1)); the ACT's own touched files
are still undone. "Someone else" changes a touched file to third bytes (neither its before- nor its after-copy) before
the undo or the launch is called: a deterministic trigger, no hook point needed."""

from __future__ import annotations

import json

import w2_148_support as support
from w2_148_support import human, wait_for

OTHERS = b"# written by someone else after the ACT (planted), neither its before nor its after\n"


def results(stdout: str) -> list:
    """Every `result` value of every JSON object printed on stdout, nested objects included."""
    found = []

    def walk(value):
        if isinstance(value, dict):
            if isinstance(value.get("result"), str):
                found.append(value["result"])
            for v in value.values():
                walk(v)
        elif isinstance(value, list):
            for v in value:
                walk(v)

    for line in (stdout or "").splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                walk(json.loads(line))
            except ValueError:
                continue
    return found


def run_until_stopped_mid_apply(w, b):
    """S22's planted unfinished journal: the run stopped by its process group id while `apply.sh apply` sleeps after
    placing the first half of the touched files."""
    applying = w.marks / "applying"
    proc = w.start(b)
    try:
        assert wait_for(lambda: applying.exists() or proc.poll() is not None, 120), "the apply never started"
        assert proc.poll() is None, proc.communicate()
    finally:
        w.stop(proc)


def two_file_act(w, act):
    applying = w.marks / "applying"
    return w.ready(act, [w.optin_removal(), w.optin_removal("tests/optin-lifted-guard.txt")],
                   live_apply_mid=f"touch {applying}; sleep 120")


def test_s22_f21_the_owner_s_undo_leaving_another_s_file_exits_non_zero_refused_held(world):
    first, other = "tests/optin-lifted.txt", "tests/optin-lifted-guard.txt"
    b = world.ready("ACT-T-F21A", [world.optin_removal(first), world.optin_removal(other)])
    r = world.run(b)
    assert r.out.get("result") == "applied", (r.out, r.stderr[-3000:])
    (world.repo / other).write_bytes(OTHERS)  # someone else, after the apply and before the undo
    world.set_clock("2026-11-12T10:00:00+00:00")
    world.say(human(f"undo {b.act} {b.sha8}", ts="2026-11-12T09:00:00.000Z"))
    r = world.run(b, step="undo")
    assert r.code != 0, ("the owner's undo left another's file yet exited 0", r.out)
    assert r.out.get("result") == "refused", ("the owner's undo left another's file yet did not say refused", r.out)
    assert world.read("repo", other) == OTHERS, "the other's file was written by the undo"
    assert support.sha256_bytes(world.read("repo", first)) == b.manifest["touched"][0]["before"], \
        "the ACT's own touched file was not undone: " + json.dumps(r.out)
    assert not support.p1_missing(world, b.act, other), ("no P1 names the file left", world.p1s(b.act))
    support.assert_lock_held(world)


def test_s22_f21_the_crash_recovery_leaving_another_s_file_is_refused_non_zero_held(world):
    first, other = "tests/optin-lifted.txt", "tests/optin-lifted-guard.txt"
    b = two_file_act(world, "ACT-T-F21B")
    run_until_stopped_mid_apply(world, b)
    assert support.sha256_bytes(world.read("repo", first)) == b.manifest["touched"][0]["after"], \
        "the first file was not placed before the stop"
    (world.repo / other).write_bytes(OTHERS)  # someone else, before the next launch
    calls = len(world.claude_calls())
    r = world.launch()  # the queue is empty: the launch finds the journal and undoes first
    assert r.code != 0, ("the recovery left another's file yet the launcher exited 0", r.out, r.stdout[-2000:])
    assert r.out.get("result") == "refused", ("the recovery left another's file yet did not say refused", r.out)
    assert "undone" not in results(r.stdout), ("a result on stdout says undone though a file was left", r.stdout[-2000:])
    assert len(world.claude_calls()) == calls, "a session started at the recovery's launch"
    assert world.read("repo", other) == OTHERS, "the other's file was written by the recovery"
    assert support.sha256_bytes(world.read("repo", first)) == b.manifest["touched"][0]["before"], \
        "the ACT's own placed file was not undone"
    assert not support.p1_missing(world, b.act, other), ("no P1 names the file left", world.p1s(b.act))
    support.assert_lock_held(world)


def test_s22_f21_guard_the_crash_recovery_with_nothing_foreign_still_says_undone(world):
    b = two_file_act(world, "ACT-T-F21C")
    run_until_stopped_mid_apply(world, b)
    r = world.launch()
    support.assert_touched(world, b, "before")
    assert "undone" in results(r.stdout), ("the recovery restored everything yet no result says undone", r.stdout[-2000:])
    assert "refused" not in results(r.stdout), ("the recovery left nothing yet a result says refused", r.stdout[-2000:])
    assert world.p1s(b.act), "the journal's undo was not pushed as a P1"
