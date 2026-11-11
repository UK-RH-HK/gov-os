"""W2-148 S20 (the log), S21 (the pushes and the digest, by an injected clock and stub channels), S22 (undo: a red check,
the owner's undo line on day 3 and day 8, the next ACT on the same files, a failing undo, an apply failing partway, an
unfinished journal undone at the next launch)."""

from __future__ import annotations

import json

import pytest

import w2_148_support as support
from w2_148_support import human, wait_for

FIELDS = ("time", "act", "manifest_sha256", "votes", "gate", "result", "commit", "checks", "undo")


def restored(w, b):
    for t in b.manifest["touched"]:
        data = w.read(t["root"], t["path"])
        assert (None if data is None else support.sha256_bytes(data)) == t["before"], f"{t['path']} not undone"


def is_after(w, b):
    return all(support.sha256_bytes(w.read(t["root"], t["path"]) or b"") == t["after"] for t in b.manifest["touched"])


# --- S20 the log ----------------------------------------------------------------------------------------------------

def test_s20_a_full_run_logs_one_line_per_gate_with_every_field(world):
    b = world.ready("ACT-T-L1", [world.optin_removal()])
    r = world.run(b)
    assert r.out.get("result") == "applied", (r.out, r.stderr[-3000:])
    lines = world.gate_lines(b.act)
    gates = [line.get("gate") for line in lines]
    for g in ("G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9"):
        assert any(line.get("gate") == g and line.get("result") == "pass" for line in lines), (g, gates)
    for line in lines:
        assert all(k in line for k in FIELDS), (line, FIELDS)
        assert line["manifest_sha256"] == b.sha
    assert any(line.get("commit") == world.head() for line in lines), "no line carries the commit"


def test_s20_a_refused_run_logs_each_gate_reached_and_no_further(world):
    b = world.ready("ACT-T-L2", [world.optin_removal()], rehearsal=support.REHEARSAL_OK.replace("failures: 0",
                                                                                               "failures: 1"))
    r = world.run(b)
    assert r.out.get("result") == "refused" and r.out.get("gate") == "G3", r.out
    lines = world.gate_lines(b.act)
    gates = {line.get("gate") for line in lines}
    assert {"G1", "G2", "G3"} <= gates and not gates & {"G4", "G5", "G6", "G7", "G8"}, gates
    assert [line for line in lines if line.get("gate") == "G3"][-1].get("result") == "refused"
    for line in lines:
        assert all(k in line for k in FIELDS), (line, FIELDS)


# --- S21 the pushes and the digest ----------------------------------------------------------------------------------

DAY1, DAY14, DAY15, DAY30 = ("2026-11-10T10:00:00+00:00", "2026-11-23T10:00:00+00:00", "2026-11-24T11:00:00+00:00",
                             "2026-12-09T10:00:00+00:00")


@pytest.fixture(scope="module")
def series(tmp_path_factory):
    w = support.World(tmp_path_factory.mktemp("w2-148-series") / "w").build()
    acts = {}
    for name, day, path in (("ACT-T-D1", DAY1, "tests/optin-lifted.txt"),
                            ("ACT-T-D14", DAY14, "tests/optin-lifted-guard.txt"),
                            ("ACT-T-D15", DAY15, "tests/optin-lifted-breadth.txt")):
        w.set_clock(day)
        b = w.ready(name, [w.optin_removal(path)], review_kw={"at": day.replace("T10:00", "T09:00")
                                                                .replace("T11:00", "T09:00")})
        r = w.run(b)
        assert r.out.get("result") == "applied", (name, r.out, r.stderr[-3000:])
        acts[name] = b
    w.set_clock(DAY30)
    b = w.ready("ACT-T-D30", [w.optin_removal()], apply_extra="echo stray > stray.txt",
                review_kw={"at": "2026-12-09T09:00:00+00:00"})
    r = w.run(b)
    assert r.out.get("result") == "refused" and r.out.get("gate") == "G8", r.out
    acts["ACT-T-D30"] = b
    return w, acts


def test_s21_an_a_act_is_pushed_for_the_first_14_days_then_the_digest_only(series):
    w, acts = series
    applied = lambda act: [n for n in w.notices(act) if n.get("kind") == "applied"]
    assert applied("ACT-T-D1"), "day 1: no push"
    assert applied("ACT-T-D14"), "day 14: no push"
    assert w.notices("ACT-T-D15") == [], "day 15: pushed, though only the digest should show it"


def test_s21_a_refusal_after_g7_on_day_30_is_pushed_as_a_p1(series):
    w, acts = series
    assert w.p1s("ACT-T-D30")


def test_s21_the_digest_lists_every_applied_act_and_a_notice_missing_from_the_channels(series):
    w, acts = series
    assert w.pings.is_file() and support.names("ACT-T-D1", w.pings.read_text()), "the D1 notice is not in pings_log"
    kept = [line for line in w.pings.read_text().splitlines() if not support.names("ACT-T-D1", line)]
    w.pings.write_text("".join(line + "\n" for line in kept))
    r = w.digest()
    assert r.code == 0, r.stderr[-3000:]
    d = r.out
    assert d.get("approved_sha256") == w.approved_sha()
    listed = {a.get("act"): a for a in d.get("applied", [])}
    for name in ("ACT-T-D1", "ACT-T-D14", "ACT-T-D15"):
        b = acts[name]
        a = listed.get(name)
        assert a, (name, list(listed))
        assert a.get("class") == "a" and a.get("votes") == {"code": "a", "claim": "a", "review": "a"}
        assert [t.get("path") for t in a.get("touched", [])] == [b.manifest["touched"][0]["path"]] or \
            a.get("touched") == [b.manifest["touched"][0]["path"]]
        assert isinstance(a.get("commit"), str) and len(a["commit"]) == 40
        assert f"undo {name} {b.sha8}" in str(a.get("undo"))
    assert "ACT-T-D30" not in listed
    assert support.names("ACT-T-D1", json.dumps(d.get("missing_notices"))), d.get("missing_notices")
    assert not support.names("ACT-T-D14", json.dumps(d.get("missing_notices")))


# --- S22 undo -------------------------------------------------------------------------------------------------------

def test_s22_a_red_check_undoes_at_once_with_a_p1(world):
    b = world.ready("ACT-T-U1", [world.optin_removal()],
                    checks=[{"cmd": f"test ! -e {support.LIVE_MARKER}", "exit": 0, "count": None}])
    r = world.run(b)
    assert r.out.get("result") == "undone", (r.out, r.stderr[-3000:])
    restored(world, b)
    assert world.p1s(b.act)


def test_s22_the_owner_s_undo_line_on_day_3_undoes_and_none_refuses(world):
    b = world.ready("ACT-T-U2", [world.optin_removal()])
    assert world.run(b).out.get("result") == "applied"
    world.set_clock("2026-11-12T10:00:00+00:00")
    r = world.run(b, step="undo")
    assert r.out.get("result") == "refused" and is_after(world, b), "undone with no undo line"
    world.say(human(f"undo {b.act} {b.sha8}", ts="2026-11-12T09:00:00.000Z"))
    r = world.run(b, step="undo")
    assert r.out.get("result") == "undone" and r.code == 0, (r.out, r.stderr[-3000:])
    restored(world, b)
    assert world.p1s(b.act), "an undo was not pushed as a P1"


def test_s22_the_owner_s_undo_line_on_day_8_is_refused(world):
    b = world.ready("ACT-T-U3", [world.optin_removal()])
    assert world.run(b).out.get("result") == "applied"
    world.say(human(f"undo {b.act} {b.sha8}", ts="2026-11-17T11:00:00.000Z"))
    world.set_clock("2026-11-17T12:00:00+00:00")
    r = world.run(b, step="undo")
    assert r.out.get("result") == "refused", r.out
    assert is_after(world, b)


def test_s22_an_undo_after_the_next_act_on_the_same_files_is_refused(world):
    b1 = world.ready("ACT-T-U4", [world.optin_removal()])
    assert world.run(b1).out.get("result") == "applied"
    world.set_clock("2026-11-11T10:00:00+00:00")
    b2 = world.ready("ACT-T-U5", [world.optin_removal()], review_kw={"at": "2026-11-11T09:00:00+00:00"})
    assert world.run(b2).out.get("result") == "applied"
    world.say(human(f"undo {b1.act} {b1.sha8}", ts="2026-11-12T09:00:00.000Z"))
    world.set_clock("2026-11-12T10:00:00+00:00")
    r = world.run(b1, step="undo")
    assert r.out.get("result") == "refused", r.out
    assert is_after(world, b2)


def test_s22_a_failing_undo_holds_the_lock_and_the_next_queued_act_is_not_run(world):
    b = world.ready("ACT-T-U6", [world.optin_removal()], live_undo="exit 1",
                    checks=[{"cmd": f"test ! -e {support.LIVE_MARKER}", "exit": 0, "count": None}])
    r = world.run(b)
    assert r.out.get("result") != "applied", r.out
    assert world.p1s(b.act), "a failing undo was not pushed as a P1"
    nxt = world.ready("ACT-T-U7", [world.optin_removal("tests/optin-lifted-guard.txt")])
    world.queue(f"{nxt.act} {nxt.sha}\n")
    r = world.launch()
    assert r.out.get("result") != "launched", r.out
    assert len(world.claude_calls()) <= 1, "a real session started while an undo had failed"
    restored(world, nxt)


def test_s22_an_apply_failing_partway_is_undone_from_the_backups_with_a_p1(world):
    b = world.ready("ACT-T-U8", [world.optin_removal(), world.optin_removal("tests/optin-lifted-guard.txt")],
                    live_apply_mid="exit 1")
    head = world.head()
    r = world.run(b)
    assert r.out.get("result") != "applied", r.out
    assert world.head() == head
    restored(world, b)
    assert world.p1s(b.act)


def test_s22_an_unfinished_journal_is_undone_at_the_next_launch_with_a_p1(world):
    applying = world.marks / "applying"
    b = world.ready("ACT-T-U9", [world.optin_removal(), world.optin_removal("tests/optin-lifted-guard.txt")],
                    live_apply_mid=f"touch {applying}; sleep 120")
    proc = world.start(b)
    try:
        assert wait_for(lambda: applying.exists() or proc.poll() is not None, 120), "the apply never started"
        assert proc.poll() is None, proc.communicate()
    finally:
        world.stop(proc)  # the session dies mid-apply: stopped by its process group id
    assert not all(support.sha256_bytes(world.read(t["root"], t["path"]) or b"") == t["before"]
                   for t in b.manifest["touched"]), "nothing was applied before the stop"
    world.launch()
    restored(world, b)
    assert world.p1s(b.act), "the journal's undo was not pushed as a P1"
