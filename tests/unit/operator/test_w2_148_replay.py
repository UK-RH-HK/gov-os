"""W2-148, the engineer's unit tests for S15's replay checked against the guard's call log (DEC-1108 (2)): each rule
refusing on its own, the re-judging with the log's role and ticket, and the live log untouched. Planted folders only."""
import hashlib
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_w2_148_kit import DAY, OPDIR, Kit, sh, write  # noqa: E402

sys.path.insert(0, str(OPDIR))
import opcommon as oc  # noqa: E402
import operator_run as orun  # noqa: E402

SESS = "0f1e2d3c-4b5a-6978-8796-a5b4c3d2e1f0"
SESS2 = "aaaabbbb-cccc-dddd-eeee-ffff00001111"
SINCE, UNTIL = "2026-11-08T10:00:00+00:00", f"{DAY}T10:30:00+00:00"   # the kit's clock: 11:00Z
READ_B = {"tool_name": "Read", "tool_input": {"file_path": "fixtures/b/q.md"}, "cwd": "."}
READ_C = {"tool_name": "Read", "tool_input": {"file_path": "data/plain.txt"}, "cwd": "."}


def h(ev):
    return hashlib.sha256(json.dumps({"tool": ev["tool_name"], "input": ev["tool_input"]}, sort_keys=True,
                                     separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def call(cid, ev, t=f"{DAY}T09:00:00+00:00", session=SESS, role="engineer"):
    return {"id": cid, "time": t, "session": session, "role": role, "ticket": "W2-1", "agent": "", "sha256": "x",
            "event": ev}


def logline(ev_or_sha, t=f"{DAY}T09:00:00.120Z", session=SESS, role="engineer", tree="worktree"):
    digest = ev_or_sha if not isinstance(ev_or_sha, dict) else h(ev_or_sha)
    return {"v": 1, "time": t, "session": session, "role": role, "agent": "", "ticket": "W2-1", "tool": "Read",
            "decision": "allow", "rule": "", "tree": tree, "ms": 3, "sha256": digest, "keyed": None}


def plant(kit, lines, log, since=SINCE, until=UNTIL, header=True):
    rows = ([json.dumps({"v": 1, "window": {"since": since, "until": until}, "built_by": "t"})] if header else [])
    rows += [x if isinstance(x, str) else json.dumps(x) for x in lines]
    write(kit.root / "log/calls.jsonl", "\n".join(rows) + "\n")
    gdir = kit.home / ".gov-os/guard-calls"
    gdir.mkdir(parents=True, exist_ok=True)
    days = {}
    for r in log:
        days.setdefault(r["time"][:10], []).append(r if isinstance(r, str) else json.dumps(r))
    for d, rs in days.items():
        write(gdir / f"{d}.jsonl", "\n".join(rs) + "\n")
    return gdir


def check(kit):
    """The check alone, as the replay runs it before anything is re-judged."""
    s = oc.load_settings(str(kit.config))
    since, until, lines = orun.read_call_set(s)
    return orun.check_against_log(s, since, until, lines), lines


def refused(kit):
    with pytest.raises(oc.Refused) as e:
        check(kit)
    return e.value.reason


@pytest.fixture
def kit(tmp_path):
    return Kit(tmp_path)


# ----------------------------------------------------------------------------------------------- each rule on its own
def test_agreeing_set_and_log_pass_and_dropped_calls_are_checked(kit):
    dropped = {"id": "d1", "time": f"{DAY}T08:00:00+00:00", "session": SESS, "sha256": "ab" * 32, "dropped": "sets root"}
    plant(kit, [call("c1", READ_B), dropped], [logline(READ_B), logline("ab" * 32, t=f"{DAY}T08:00:01.000Z")])
    matched, lines = check(kit)
    assert len(lines) == 2 and all(id(c) in matched for c in lines)


def test_the_hash_is_the_guards():
    ev = {"tool_name": "Bash", "tool_input": {"command": "echo é", "b": [1, {"z": 1, "a": 2}]}}
    raw = json.dumps({"tool": "Bash", "input": ev["tool_input"]}, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=False).encode("utf-8")
    assert orun.action_sha("Bash", ev["tool_input"]) == hashlib.sha256(raw).hexdigest()


@pytest.mark.parametrize("since,until,header,phrase", [
    (SINCE, UNTIL, False, "no header"),
    ("2026-11-09T10:00:00+00:00", UNTIL, True, "window short"),
    ("2026-11-07T10:00:00+00:00", "2026-11-09T22:00:00+00:00", True, "window stale"),
    ("2026-11-08T11:00:00+00:00", f"{DAY}T11:10:00+00:00", True, "ahead of the clock"),
])
def test_the_window(kit, since, until, header, phrase):
    plant(kit, [call("c1", READ_B)], [logline(READ_B)], since=since, until=until, header=header)
    assert phrase in refused(kit)


@pytest.mark.parametrize("bad", ['{"id": "x", "time": "t"}', "not json", '{"id": "d", "sha256": "ab", "dropped": "r"}',
                                 '{"id": "d", "sha256": "' + "ab" * 32 + '", "dropped": ""}'])
def test_a_malformed_set_line_refuses(kit, bad):
    plant(kit, [call("c1", READ_B), bad], [logline(READ_B)])
    assert "malformed" in refused(kit)


def test_the_log_missing_capped_or_malformed(kit):
    gdir = plant(kit, [call("c1", READ_B)], [logline(READ_B)])
    write(gdir / f"{DAY}.jsonl.capped", "")
    assert f"log capped ({DAY}" in refused(kit)
    (gdir / f"{DAY}.jsonl.capped").unlink()
    with open(gdir / f"{DAY}.jsonl", "a") as f:
        f.write('{"time": "no time", "session": "s"}\n')
    assert f"log malformed ({DAY}" in refused(kit)
    for p in gdir.iterdir():
        p.unlink()
    gdir.rmdir()
    assert "log missing" in refused(kit)


def test_a_set_call_with_no_log_line_is_named_by_id(kit):
    plant(kit, [call("c1", READ_B), call("c2", READ_C, session=SESS2)], [logline(READ_B), logline(READ_C)])
    why = refused(kit)
    assert why.split("no line in the guard's log: ")[1].split(";")[0] == "c2" and "data/plain.txt" not in why


def test_a_logged_live_call_missing_from_the_set_is_named(kit):
    plant(kit, [call("c1", READ_B)], [logline(READ_B), logline(READ_C, t=f"{DAY}T07:15:30.500Z")])
    why = refused(kit)
    assert f"{SESS[:8]} {h(READ_C)[:12]} {DAY}T07:15:30.500Z" in why and "data/plain.txt" not in why


def test_a_null_log_sha_counts_as_missing_and_other_sessions_and_trees_are_not_required(kit):
    plant(kit, [call("c1", READ_B)], [logline(READ_B), logline(READ_C, session="suite-fixed-name"),
                                      logline(READ_C, tree="run"), logline(READ_C, tree="scratch")])
    check(kit)
    plant(kit, [call("c1", READ_B)], [logline(READ_B), logline(None)])
    assert "missing from the set" in refused(kit)


def test_calls_outside_the_window_are_neither_checked_nor_re_judged(kit):
    plant(kit, [call("c1", READ_B), call("old", READ_C, t="2026-11-01T09:00:00+00:00")],
          [logline(READ_B), logline(READ_C, t="2026-11-08T09:00:00.000Z")])     # the log line before since + 2 min
    _, lines = check(kit)
    assert [c["id"] for c in lines] == ["c1"]


# ------------------------------------------------------------------------------------- end to end, through S15's undo
def path_map_act(kit, act, **kw):
    pm = (kit.repo / "governance/project/path-map.yaml").read_text()
    new = pm.replace('hidden: ["fixtures/a/**"]', 'hidden: ["fixtures/a/**", "fixtures/b/**"]')
    return pm, kit.bundle(act, {("repo", "governance/project/path-map.yaml"): new.encode()}, **kw)


def commit_guard(kit, text):
    write(kit.repo / ".claude/hooks/pretooluse.py", text)
    sh("git", "commit", "-q", "-am", "guard variant", cwd=kit.repo)


def test_a_mismatch_undoes_the_act_and_pushes_a_p1_naming_it(kit):
    plant(kit, [call("c1", READ_B), call("ghost", READ_C)], [logline(READ_B)])
    pm, msha = path_map_act(kit, "ACT-RP1", replay_refused=["c1"])
    rc, res, _ = kit.run("run", "ACT-RP1", msha)
    assert res["result"] == "undone" and res["gate"] == "after-check" and "ghost" in res["reason"], res
    assert (kit.repo / "governance/project/path-map.yaml").read_text() == pm
    p1 = [n for n in kit.notices() if n["priority"] == "P1"][-1]["text"]
    assert "ghost" in p1 and "data/plain.txt" not in p1


def test_the_log_role_wins_when_re_judging(kit):
    guard = (Path(__file__).resolve().parent / "test_w2_148_kit.py").read_text()
    role_aware = guard.split("GUARD = r'''", 1)[1].split("'''", 1)[0].replace(
        'if ev.get("tool_name") == "Read"',
        'if os.environ.get("GOV_ROLE") in ((pm.get("sets_root_hidden") or {}).get("refused_roles") or []) and '
        'ev.get("tool_name") == "Read"')
    commit_guard(kit, role_aware)
    # the set says research (not refused); the guard logged engineer (refused): the call turns, undone
    plant(kit, [call("c1", READ_B, role="research")], [logline(READ_B, role="engineer")])
    _, msha = path_map_act(kit, "ACT-RR1")
    rc, res, _ = kit.run("run", "ACT-RR1", msha)
    assert res["result"] == "undone" and "c1" in res["reason"] and "did not list" in res["reason"], res
    # the reverse: the set says engineer, the log research: nothing turns, applied
    plant(kit, [call("c1", READ_B, role="engineer")], [logline(READ_B, role="research")])
    _, msha = path_map_act(kit, "ACT-RR2")
    rc, res, _ = kit.run("run", "ACT-RR2", msha)
    assert res["result"] == "applied", res


def test_the_replays_hook_runs_never_write_the_live_log(kit):
    guard = (Path(__file__).resolve().parent / "test_w2_148_kit.py").read_text()
    record = guard.split("GUARD = r'''", 1)[1].split("'''", 1)[0].replace(
        "ev = json.loads(sys.stdin.read())",
        "ev = json.loads(sys.stdin.read())\n"
        "open(os.path.join(os.environ['HOME'], '..', 'guard-runs.jsonl'), 'a').write(json.dumps({'dir': "
        "os.environ.get('GOV_GUARD_CALLS_DIR'), 'role': os.environ.get('GOV_ROLE'), 'path': "
        "(ev.get('tool_input') or {}).get('file_path')}) + '\\n')")
    commit_guard(kit, record)
    gdir = plant(kit, [call("c1", READ_B, role="research")], [logline(READ_B, role="engineer")])
    before = {p.name: p.read_bytes() for p in gdir.iterdir()}
    _, msha = path_map_act(kit, "ACT-RL1", replay_refused=["c1"])
    rc, res, _ = kit.run("run", "ACT-RL1", msha)
    assert res["result"] == "applied", res
    runs = [json.loads(x) for x in (kit.tmp / "guard-runs.jsonl").read_text().splitlines()]
    assert len(runs) == 2 and all(r["role"] == "engineer" for r in runs)
    for r in runs:
        d = r["dir"]
        assert d and os.path.isabs(d) and "gov-operator-replay-" in d
        assert not d.startswith(str(gdir)) and ".gov-os" not in d
    assert {p.name: p.read_bytes() for p in gdir.iterdir()} == before
