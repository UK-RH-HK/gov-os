"""W2-148, the engineer's unit tests: the operator's run, undo, digest and launcher on planted folders."""
import json
import os
import sys
import threading
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_w2_148_kit import DAY, Kit, sha, sh, write  # noqa: E402


@pytest.fixture
def kit(tmp_path):
    return Kit(tmp_path)


def optin_removal(kit):
    return {("repo", "tests/optin-x.txt"): b"one\nthree\n"}


def test_an_a_act_is_applied_committed_logged_and_noticed(kit):
    msha = kit.bundle("ACT-T1", optin_removal(kit))
    head = kit.head()
    rc, res, r = kit.run("run", "ACT-T1", msha)
    assert rc == 0, (res, r.stderr.decode())
    assert res["result"] == "applied" and res["class"] == "a" and res["approved_sha256"]
    assert (kit.repo / "tests/optin-x.txt").read_bytes() == b"one\nthree\n"
    assert kit.head() != head
    tr = kit.trailers()
    for t in ("Role: operator", "Act: ACT-T1", f"Act-sha: {msha}", "Class: a", "Review: "):
        assert t in tr
    assert "Role: owner" not in tr
    files = sh("git", "show", "--name-only", "--format=", "HEAD", cwd=kit.repo).stdout.decode().split()
    assert files == ["tests/optin-x.txt"]
    gates = [e["gate"] for e in kit.log()]
    assert gates == ["G1", "G2", "G3", "G4", "G5", "G6", "recompute", "G7", "G8", "G9", "apply"]
    for e in kit.log():
        for k in ("time", "act", "manifest_sha256", "votes", "gate", "result", "commit", "checks", "undo"):
            assert k in e
    assert [n["kind"] for n in kit.notices()] == ["applied"]
    assert not (kit.root / "log/act-in-progress.txt").exists()
    frozen = kit.root / "acts" / f"ACT-T1-{msha[:12]}"
    assert frozen.is_dir() and not os.access(frozen, os.W_OK)


def test_g1_a_byte_changed_before_the_copy_refuses(kit):
    msha = kit.bundle("ACT-T2", optin_removal(kit))
    with open(kit.scratch / "acts/ACT-T2/list.txt", "a") as f:
        f.write("\n")
    rc, res, _ = kit.run("run", "ACT-T2", msha)
    assert rc != 0 and res["gate"] == "G1"
    assert (kit.repo / "tests/optin-x.txt").read_bytes() == b"one\ntwo\nthree\n"


def test_g1_an_edit_in_the_source_after_the_copy_changes_nothing(kit, tmp_path):
    msha = kit.bundle("ACT-T3", optin_removal(kit))
    hook = write(tmp_path / "hook.sh", f'#!/bin/bash\n[ "$1" = after-G1 ] && echo "repo|x|null|null" >> '
                                       f'{kit.scratch}/acts/ACT-T3/list.txt\ntouch "$2/new" 2>/dev/null && exit 9\n'
                                       'exit 0\n', 0o755)
    env = kit.env()
    env["GOV_OPERATOR_TEST_HOOK"] = str(hook)
    rc, res, _ = kit.run("run", "ACT-T3", msha, env=env)
    assert rc == 0 and res["result"] == "applied", res


@pytest.mark.parametrize("dec,ok", [("DEC-1", True), ("DEC-2", False), ("DEC-99", False), ("", False)])
def test_g2_the_decision_must_be_accepted(kit, dec, ok):
    msha = kit.bundle("ACT-T4", optin_removal(kit), dec=dec)
    rc, res, _ = kit.run("run", "ACT-T4", msha)
    assert (res["result"] == "applied") == ok
    if not ok:
        assert res["gate"] == "G2"


@pytest.mark.parametrize("log,ok", [("x\nfailures: 0\n", True), ("x\nfailures: 2\n", False), ("x\n", False)])
def test_g3_the_rehearsal_ends_with_no_failures(kit, log, ok):
    msha = kit.bundle("ACT-T5", optin_removal(kit), rehearsal=log)
    rc, res, _ = kit.run("run", "ACT-T5", msha)
    assert (res["result"] == "applied") == ok
    if not ok:
        assert res["gate"] == "G3"


@pytest.mark.parametrize("kw,phrase", [({"rounds": 3}, "to the owner"), ({"reviewer": "cto"}, "author"),
                                       ({"brief_sha": "0" * 64}, "brief")])
def test_g4_refusals(kit, kw, phrase):
    msha = kit.bundle("ACT-T6", optin_removal(kit), **kw)
    rc, res, _ = kit.run("run", "ACT-T6", msha)
    assert rc != 0 and res["gate"] == "G4" and phrase in res["reason"]


def test_g4_a_fail_without_a_blocking_finding_refuses(kit):
    msha = kit.bundle("ACT-T7", optin_removal(kit))
    p = kit.scratch / "acts/ACT-T7/review.md"
    p.write_text(p.read_text().replace('"verdict": "pass"', '"verdict": "fail"'))
    rc, res, _ = kit.run("run", "ACT-T7", msha)
    assert res["gate"] == "G4"


def test_g5_a_request_naming_another_sha_is_changed_after_review(kit):
    kit.bundle("ACT-T8", optin_removal(kit))
    rc, res, _ = kit.run("run", "ACT-T8", "a" * 64)
    assert rc != 0 and "changed after review" in res["reason"]


def test_g6_o_is_yours_and_nothing_is_applied(kit):
    msha = kit.bundle("ACT-T9", {("repo", "src/x.py"): b"x\n"}, claimed="a")
    rc, res, _ = kit.run("run", "ACT-T9", msha)
    assert res["gate"] == "G6" and "yours" in res["reason"]
    assert not (kit.repo / "src/x.py").exists()
    assert any(n["kind"] == "disagreement" for n in kit.notices())


def test_g6_b_needs_the_owners_typed_yes(kit):
    ch = {("repo", "tests/optin-x.txt"): b"one\ntwo\nthree\nfour\n"}
    msha = kit.bundle("ACT-B1", ch, claimed="b")
    yes = f"yes ACT-B1 {msha[:8]}"
    kit.say(yes, f"{DAY}T09:00:00+00:00")                          # before the review
    kit.say(yes, f"{DAY}T11:00:00+00:00", kind="task-notification")
    kit.say([{"type": "tool_result", "content": yes}], f"{DAY}T11:00:00+00:00")
    kit.say(yes, f"{DAY}T11:00:00+00:00", isMeta=True)
    kit.say(yes, f"{DAY}T11:00:00+00:00", isSidechain=True)
    rc, res, _ = kit.run("run", "ACT-B1", msha)
    assert res["gate"] == "G6"
    kit.say([{"type": "text", "text": yes}], f"{DAY}T11:30:00+00:00")
    rc, res, _ = kit.run("run", "ACT-B1", msha)
    assert res["result"] == "applied", res
    assert "Approved-by: owner (chat, " in kit.trailers()
    assert yes in (kit.root / "log/act-approvals.jsonl").read_text()


def test_votes_rise_and_never_fall(kit):
    msha = kit.bundle("ACT-V1", optin_removal(kit), claimed="a", review_class="b")
    kit.say(f"yes ACT-V1 {msha[:8]}", f"{DAY}T11:00:00+00:00")
    rc, res, _ = kit.run("run", "ACT-V1", msha)
    assert res["class"] == "b" and res["votes"] == {"code": "a", "claim": "a", "review": "b"}
    assert any(e.get("disagreement") for e in kit.log() if e["gate"] == "G6")


def test_recompute_refuses_a_frozen_patch_changed_after_g6(kit, tmp_path):
    msha = kit.bundle("ACT-R1", optin_removal(kit))
    hook = write(tmp_path / "hook.sh", '#!/bin/bash\nif [ "$1" = after-G6 ]; then chmod u+w "$2" "$2/apply.sh"; '
                                       'echo "sudo true" >> "$2/apply.sh"; fi\nexit 0\n', 0o755)
    env = kit.env()
    env["GOV_OPERATOR_TEST_HOOK"] = str(hook)
    rc, res, _ = kit.run("run", "ACT-R1", msha, env=env)
    assert res["gate"] == "recompute"
    assert (kit.repo / "tests/optin-x.txt").read_bytes() == b"one\ntwo\nthree\n"


def test_g7_a_moved_live_file_refuses(kit):
    msha = kit.bundle("ACT-G7", optin_removal(kit))
    write(kit.repo / "tests/optin-x.txt", "moved\n")
    rc, res, _ = kit.run("run", "ACT-G7", msha)
    assert res["gate"] == "G7" and "rebuild, rehearse, re-review" in res["reason"]


@pytest.mark.parametrize("extra", ['echo x > "$PWD/data/unlisted.txt"', 'echo x > "$HOME/unlisted.txt"',
                                   '[ "$1" = undo ] && echo z >> "$PWD/tests/optin-x.txt"'])
def test_g8_the_dry_run_refuses_unlisted_files_and_a_bad_undo(kit, extra):
    msha = kit.bundle("ACT-G8", optin_removal(kit), extra_apply=f'[ "$step" != check ] && {{ {extra}; }}'
                      if "undo" not in extra else extra.replace("$1", "$step"))
    rc, res, _ = kit.run("run", "ACT-G8", msha)
    assert res["gate"] == "G8", res
    assert (kit.repo / "tests/optin-x.txt").read_bytes() == b"one\ntwo\nthree\n"
    assert not (kit.repo / "data/unlisted.txt").exists() and not (kit.home / "unlisted.txt").exists()


def test_g9_holds_then_proceeds(kit):
    msha = kit.bundle("ACT-H1", optin_removal(kit))
    hold = write(kit.scratch / "log/act-in-progress.txt", "FRESH-80\n")
    threading.Timer(2.0, hold.unlink).start()
    rc, res, _ = kit.run("run", "ACT-H1", msha)
    assert res["result"] == "applied"
    assert [e["result"] for e in kit.log() if e["gate"] == "G9"] == ["held", "pass"]


def test_g9_quiet_hours_hold(kit):
    msha = kit.bundle("ACT-H2", optin_removal(kit))
    kit.set_clock(f"{DAY}T03:00:00+01:00")
    threading.Timer(2.0, kit.set_clock, args=(f"{DAY}T09:00:00+01:00",)).start()
    rc, res, _ = kit.run("run", "ACT-H2", msha)
    assert res["result"] == "applied"


def test_a_red_check_live_is_undone_and_pushed(kit):
    checks = [{"cmd": "test ! -e .live-marker", "exit": 0, "count": None}]
    msha = kit.bundle("ACT-C1", optin_removal(kit), checks=checks)
    rc, res, _ = kit.run("run", "ACT-C1", msha)
    assert res["result"] == "undone" and res["gate"] == "checks"
    assert (kit.repo / "tests/optin-x.txt").read_bytes() == b"one\ntwo\nthree\n"
    assert any(n["priority"] == "P1" for n in kit.notices())


def test_a_staged_extra_file_is_refused(kit):
    msha = kit.bundle("ACT-S1", optin_removal(kit))
    write(kit.repo / "data/plain.txt", "staged\n")
    sh("git", "add", "data/plain.txt", cwd=kit.repo)
    rc, res, _ = kit.run("run", "ACT-S1", msha)
    assert res["gate"] == "staged"
    assert (kit.repo / "tests/optin-x.txt").read_bytes() == b"one\ntwo\nthree\n"


def test_an_a_act_changing_a_control_file_live_is_undone_and_the_control_left(kit):
    """DEC-1106 (1): the ACT's own touched file undone; the control file left exactly as the apply wrote it (the
    agent cannot tell that change from someone else's), the lock held, a P1 naming it."""
    hookf = kit.repo / ".claude/hooks/pretooluse.py"
    before = hookf.read_bytes()
    msha = kit.bundle("ACT-K1", optin_removal(kit),
                      extra_apply='[ "$step" = apply ] && [ -e "$PWD/.live-marker" ] && echo "# x" >> '
                                  '"$PWD/.claude/hooks/pretooluse.py"')
    rc, res, _ = kit.run("run", "ACT-K1", msha)
    assert res["result"] == "undone" and res["left"] == ["repo:.claude/hooks/pretooluse.py"], res
    assert hookf.read_bytes() == before + b"# x\n"
    assert (kit.repo / "tests/optin-x.txt").read_bytes() == b"one\ntwo\nthree\n"
    assert (kit.root / "log/operator.lock").exists()
    assert ".claude/hooks/pretooluse.py" in [n for n in kit.notices() if n["priority"] == "P1"][-1]["text"]


def test_a_path_map_addition_whose_replay_refuses_an_unlisted_call_is_undone(kit):
    pm = (kit.repo / "governance/project/path-map.yaml").read_text()
    new = pm.replace('hidden: ["fixtures/a/**"]', 'hidden: ["fixtures/a/**", "fixtures/b/**"]')
    # the CTO's set and the guard's log agreeing both ways (DEC-1108 (2)); the log's role is the one re-judged
    session = "0f1e2d3c-4b5a-6978-8796-a5b4c3d2e1f0"
    tin = {"file_path": "fixtures/b/q.md"}
    digest = sha(json.dumps({"tool": "Read", "input": tin}, sort_keys=True, separators=(",", ":")).encode())
    head = {"v": 1, "window": {"since": "2026-11-08T10:00:00+00:00", "until": f"{DAY}T10:30:00+00:00"}}
    c1 = {"id": "c1", "time": f"{DAY}T10:00:00+00:00", "session": session, "role": "engineer", "ticket": "W2-1",
          "event": {"tool_name": "Read", "tool_input": tin, "cwd": "."}}
    write(kit.root / "log/calls.jsonl", json.dumps(head) + "\n" + json.dumps(c1) + "\n")
    write(kit.home / f".gov-os/guard-calls/{DAY}.jsonl", json.dumps({
        "v": 1, "time": f"{DAY}T10:00:00.250Z", "session": session, "role": "engineer", "agent": "", "ticket": "W2-1",
        "tool": "Read", "decision": "allow", "rule": "", "tree": "worktree", "ms": 2, "sha256": digest,
        "keyed": None}) + "\n")
    msha = kit.bundle("ACT-P1", {("repo", "governance/project/path-map.yaml"): new.encode()})
    rc, res, _ = kit.run("run", "ACT-P1", msha)
    assert res["result"] == "undone" and res["gate"] == "after-check", res
    assert (kit.repo / "governance/project/path-map.yaml").read_text() == pm
    msha = kit.bundle("ACT-P2", {("repo", "governance/project/path-map.yaml"): new.encode()}, replay_refused=["c1"])
    rc, res, _ = kit.run("run", "ACT-P2", msha)
    assert res["result"] == "applied", res


def test_a_failing_undo_holds_the_lock(kit):
    checks = [{"cmd": "test ! -e .live-marker", "exit": 0, "count": None}]
    msha = kit.bundle("ACT-U1", optin_removal(kit), checks=checks,
                      extra_apply='[ "$step" = undo ] && [ -e "$PWD/.live-marker" ] && exit 7')
    rc, res, _ = kit.run("run", "ACT-U1", msha)
    assert rc != 0 and res["undo"] == "failed"
    assert (kit.root / "log/operator.lock").exists()
    m2 = kit.bundle("ACT-U2", {("repo", "data/plain.txt"): None})
    rc, res, _ = kit.run("run", "ACT-U2", m2)
    assert res["gate"] == "lock"


def test_the_owners_undo_day_3_and_day_8(kit):
    msha = kit.bundle("ACT-D1", optin_removal(kit))
    assert kit.run("run", "ACT-D1", msha)[1]["result"] == "applied"
    kit.say(f"undo ACT-D1 {msha[:8]}", "2026-11-13T09:00:00+00:00")
    kit.set_clock("2026-11-18T12:00:00+01:00")
    rc, res, _ = kit.run("undo", "ACT-D1", msha)
    assert res["result"] == "refused"
    kit.set_clock("2026-11-13T12:00:00+01:00")
    rc, res, _ = kit.run("undo", "ACT-D1", msha)
    assert rc == 0 and res["result"] == "undone", res
    assert (kit.repo / "tests/optin-x.txt").read_bytes() == b"one\ntwo\nthree\n"


def test_the_digest_lists_applied_acts_and_missing_notices(kit):
    msha = kit.bundle("ACT-DG", optin_removal(kit))
    kit.run("run", "ACT-DG", msha)
    rc, d, _ = kit.run("digest")
    assert rc == 0 and d["applied"][0]["act"] == "ACT-DG" and d["applied"][0]["undo"] == f"undo ACT-DG {msha[:8]}"
    assert d["missing_notices"] == []
    kit.pings.write_text("")
    rc, d, _ = kit.run("digest")
    assert [m["act"] for m in d["missing_notices"]] == ["ACT-DG"]


def test_pushes_for_a_stop_after_14_days(kit):
    for day, act in (("2026-11-10", "ACT-N1"), ("2026-11-23", "ACT-N2"), ("2026-11-24", "ACT-N3")):
        kit.set_clock(f"{day}T12:00:00+01:00")
        cur = (kit.repo / "tests/optin-x.txt").read_bytes()
        msha = kit.bundle(act, {("repo", "tests/optin-x.txt"): cur.split(b"\n", 1)[1]})
        assert kit.run("run", act, msha)[1]["result"] == "applied"
    assert [n["act"] for n in kit.notices() if n["kind"] == "applied"] == ["ACT-N1", "ACT-N2"]


def test_an_approved_mismatch_refuses_run_and_launch(kit):
    with open(kit.install / "brief.md", "a") as f:
        f.write(" ")
    msha = kit.bundle("ACT-A1", optin_removal(kit))
    rc, res, _ = kit.run("run", "ACT-A1", msha)
    assert rc != 0 and res["gate"] == "approved" and res["approved_sha256"]
    rc, res, _ = kit.launch()
    assert rc != 0 and res["gate"] == "approved"


def test_the_launcher_runs_the_canary_then_the_walled_session(kit):
    msha = kit.bundle("ACT-L1", optin_removal(kit))
    write(kit.root / "queue/one.req", f"ACT-L1 {msha}\n")
    env = kit.env()
    env["GOV_ROLE"] = "orchestrator"
    env["CLAUDE_PROJECT_DIR"] = str(kit.repo)
    import subprocess
    r = subprocess.run([sys.executable, str(kit.install / "operator_launch.py"), "--config", str(kit.config)],
                       capture_output=True, env=env, timeout=120)
    res = json.loads(r.stdout.decode().strip().splitlines()[-1])
    assert r.returncode == 0 and res["result"] == "launched", (res, r.stderr.decode())
    assert res["request"] == {"act": "ACT-L1", "sha256": msha} and res["session"]["pid"]
    calls = [json.loads(x) for x in (kit.tmp / "claude-calls.jsonl").read_text().splitlines()]
    assert len(calls) == 2
    for c in calls:
        assert c["cwd"] == str(kit.root / "wall")
        assert not any(k.startswith("GOV_") or k == "CLAUDE_PROJECT_DIR" for k in c["env"])
        a = c["argv"]
        assert a[:2] == ["-p", "--restricted"] and a[a.index("--settings") + 1] == str(kit.root / "wall/.claude/settings.json")
        for flag in ("--no-session-persistence", "--strict-mcp-config", "--max-budget-usd"):
            assert flag in a


def test_a_malformed_request_is_moved_aside(kit):
    write(kit.root / "queue/bad.req", "ACT-X not-a-sha\n")
    rc, res, _ = kit.launch()
    assert rc != 0 and res["result"] == "refused" and not (kit.root / "queue/bad.req").exists()
    assert not (kit.tmp / "claude-calls.jsonl").exists()


def test_the_canary_refuses_when_the_settings_do_not_load(kit):
    msha = kit.bundle("ACT-L2", optin_removal(kit))
    write(kit.root / "queue/one.req", f"ACT-L2 {msha}\n")
    # a stub modelling settings it cannot load: the canary's Read comes back allowed
    stub = kit.bin / "claude"
    stub.write_text(stub.read_text().replace("loaded = bool(", "loaded = False and bool("))
    rc, res, _ = kit.launch()
    assert rc != 0 and res["gate"] == "canary"
    calls = [json.loads(x) for x in (kit.tmp / "claude-calls.jsonl").read_text().splitlines()]
    assert len(calls) == 1


def test_a_journal_left_by_a_dead_session_is_undone_at_the_next_launch(kit):
    msha = kit.bundle("ACT-J1", optin_removal(kit),
                      extra_apply='[ "$step" = apply ] && [ -e "$PWD/.live-marker" ] && kill -9 $PPID; true')
    import subprocess
    p = subprocess.run([sys.executable, str(kit.install / "operator_run.py"), "--config", str(kit.config), "run",
                        "ACT-J1", msha], capture_output=True, env=kit.env(), timeout=120)
    assert p.returncode != 0
    assert (kit.root / "log/journal.json").exists()
    assert (kit.repo / "tests/optin-x.txt").read_bytes() == b"one\nthree\n"
    rc, res, _ = kit.launch()
    assert rc == 0 and res["result"] == "recovered", res
    assert (kit.repo / "tests/optin-x.txt").read_bytes() == b"one\ntwo\nthree\n"
    assert any(n["kind"] == "recovered" and n["priority"] == "P1" for n in kit.notices())


def test_the_owners_operator_files_are_untouched(kit):
    for rel in ("CLAUDE.md", ".claude/settings.json", "hooks/h.sh", "log/2026-11-01.log"):
        write(kit.root / rel, "owner's\n")
    before = {p: sha(p.read_bytes()) for p in kit.root.rglob("*") if p.is_file() and "install" not in p.parts
              and p.parts[len(kit.root.parts)] in ("CLAUDE.md", ".claude", "hooks") or p.name == "2026-11-01.log"}
    msha = kit.bundle("ACT-O1", optin_removal(kit))
    write(kit.root / "queue/one.req", f"ACT-O1 {msha}\n")
    assert kit.launch()[1]["result"] == "launched"
    assert kit.run("run", "ACT-O1", msha)[1]["result"] == "applied"
    assert {p: sha(p.read_bytes()) for p in before} == before
