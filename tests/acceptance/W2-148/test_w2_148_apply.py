"""W2-148 S14 (the apply and its commit), S15 (the post-apply control-file check and the guard replay for (a)), S16 (the
landing check on a planted range of first-parent commits)."""

from __future__ import annotations

import json
import shlex
import subprocess
from datetime import datetime, timedelta

import pytest

import w2_148_support as support


def restored(w, b):
    for t in b.manifest["touched"]:
        data = w.read(t["root"], t["path"])
        assert (None if data is None else support.sha256_bytes(data)) == t["before"], f"{t['path']} not undone"


# --- S14 the apply and its commit -----------------------------------------------------------------------------------

def test_s14_the_commit_holds_only_the_listed_files_and_the_fixed_trailers(world):
    freeze = world.marks / "freeze-seen"
    install_freeze = world.install / "act-in-progress.txt"  # DEC-1106 (3): in the install folder, in neither log/
    logs = (world.op / "log/act-in-progress.txt", world.scratch / "log/act-in-progress.txt")
    holds = " && ".join([f"[ -e {shlex.quote(str(install_freeze))} ]",
                         *(f"[ ! -e {shlex.quote(str(p))} ]" for p in logs)])
    b = world.ready("ACT-T-AP", [world.optin_removal(), world.optin_removal("tests/optin-lifted-guard.txt")],
                    live_apply=f"if {holds}; then echo seen > {shlex.quote(str(freeze))}; fi")
    head, remote = world.head(), world.snapshot()["remote"]
    r = world.run(b)
    assert r.out.get("result") == "applied" and r.code == 0, (r.out, r.stderr[-3000:])
    assert world.git("rev-parse", "HEAD~1").strip() == head
    assert world.committed_files() == {"tests/optin-lifted.txt", "tests/optin-lifted-guard.txt"}
    t = world.trailers()
    review_sha = support.sha256_file(b.dir / "review.md")
    for pair in (("Role", "operator"), ("Act", b.act), ("Act-sha", b.sha), ("Class", "a"), ("Review", review_sha)):
        assert pair in t, (pair, t)
    assert [v for k, v in t if k == "Role"] == ["operator"]
    assert not [k for k, _ in t if k == "Approved-by"]
    assert freeze.exists(), "install/act-in-progress.txt (the commit freeze) was not there during the apply, or a " \
                            "freeze was in a log/"
    assert not install_freeze.exists() and not any(p.exists() for p in logs), "a freeze was left after the run"
    snap = world.snapshot()
    assert snap["remote"] == remote and snap["tags"] == "", "a push or a tag"
    assert world.forbidden_calls() == ""


def test_s14_an_extra_staged_file_refuses_and_undoes(world):
    b = world.ready("ACT-T-ST", [world.optin_removal()], live_apply="echo extra > extra.txt && git add extra.txt")
    head = world.head()
    r = world.run(b)
    assert r.out.get("result") != "applied", r.out
    assert world.head() == head, "committed with an extra staged file"
    restored(world, b)
    assert world.p1s(b.act), "a refusal after G7 was not pushed as a P1"


def test_s14_a_check_whose_count_differs_from_the_rehearsal_is_red_and_undone(world):
    check = {"cmd": f"if [ -e {support.LIVE_MARKER} ]; then echo 3; else echo 2; fi", "exit": 0, "count": 2}
    b = world.ready("ACT-T-CN", [world.optin_removal()], checks=[check])
    r = world.run(b)
    assert r.out.get("result") == "undone", (r.out, r.stderr[-3000:])
    restored(world, b)
    assert world.p1s(b.act), "a red check was not pushed as a P1"


# --- S15 the post-apply control-file check --------------------------------------------------------------------------

FAMILIES = {
    "hook-folder": ("repo", ".claude/hooks/pretooluse.py", "echo '# changed' >> .claude/hooks/pretooluse.py"),
    "settings": ("repo", ".claude/settings.json",
                 "sed -i 's/\"Bash(git status)\"/\"Bash(git status)\", \"Bash(git push *)\"/' .claude/settings.json"),
    "claude-folder": ("repo", ".claude/agents/engineer.md", "echo changed >> .claude/agents/engineer.md"),
    "git-hooks": ("repo", ".git/hooks/reference-transaction", "echo '# changed' >> .git/hooks/reference-transaction"),
    "crontab": ("crontab", "crontab",  # read whole before writing: a pipe into `crontab -` can truncate first
                "c=\"$(crontab -l)\"; printf '%s\\n%s\\n' \"$c\" '*/5 * * * * /bin/true # added' | crontab -"),
    "pin": ("home", ".local/bin/gov", "echo '# changed' >> \"$HOME/.local/bin/gov\""),
    "dead-man-code": ("repo", "governance/project/orchestration/tools/deadman.py",
                      "echo '# changed' >> governance/project/orchestration/tools/deadman.py"),
    "operator-install": ("install", "brief.md", None),
}

APPENDED = {"hook-folder": b"# changed\n", "claude-folder": b"changed\n", "git-hooks": b"# changed\n",
            "crontab": b"*/5 * * * * /bin/true # added\n", "pin": b"# changed\n", "dead-man-code": b"# changed\n",
            "operator-install": b"changed\n"}


def written(family, before: bytes) -> bytes:
    """The bytes the family's line leaves in the control file."""
    if family == "settings":
        return before.replace(b'"Bash(git status)"', b'"Bash(git status)", "Bash(git push *)"', 1)
    return before + APPENDED[family]


@pytest.mark.parametrize("family", list(FAMILIES))
def test_s15_an_a_act_that_also_changes_a_control_file_is_undone_with_a_p1(world, family):
    """DEC-1106 (1): the agent cannot tell an unlisted control file's change from someone else's, so it leaves it
    exactly as it is, holds the lock and names it in a P1; the ACT's own touched files are undone."""
    root, path, line = FAMILIES[family]
    if root == "install":
        target = world.install / path
        line = f"echo changed >> {target}"
        before = target.read_bytes()
        state = lambda: target.read_bytes()
    else:
        before = world.read(root, path)
        state = lambda: world.read(root, path)
    assert before is not None
    b = world.ready("ACT-T-CF", [world.optin_removal()], live_apply=line)
    r = world.run(b)
    expected = written(family, before)
    assert state() == expected, f"the {family} control file was not left exactly as the apply wrote it"
    restored(world, b)
    assert r.out.get("result") in ("undone", "refused"), (r.out, r.stderr[-3000:])
    missing = support.p1_missing(world, b.act, path)
    assert not missing, ("no P1 names the control file left changed", missing, world.p1s(b.act))
    support.assert_lock_held(world)
    assert state() == expected, f"the next launch changed the {family} control file"


# DEC-1108 (2): the call set carries its header and every call in its window has its line in the guard's log, both
# ways (w2_148_support.replay_set: call-q1 newly refused and listed, call-notes and call-readme allowed, one dropped
# call, call-old before the window), so these two cases test the re-judging, not the check.

def test_s15_guard_a_path_map_addition_whose_replay_refuses_only_listed_calls_stays(world):
    """Rewrite-Reason: DEC-1108 (2). A set and a log that agree both ways (calls and a dropped call): checked, then
    re-judged; the listed call turned to refused and the one before the window leave the ACT applied."""
    support.plant_replay(world, support.replay_set())
    b = world.ready("ACT-T-PM", [world.pathmap_addition()], review_kw={"extra": {"replay_refused": ["call-q1"]}})
    r = world.run(b)
    assert r.out.get("result") == "applied", (r.out, r.stderr[-3000:])
    assert support.sha256_bytes(world.read("repo", "governance/project/path-map.yaml")) == b.manifest["touched"][0]["after"]


def test_s15_a_path_map_addition_whose_replay_refuses_an_unlisted_call_is_undone(world):
    """Rewrite-Reason: DEC-1108 (2). The check passes (header, log both ways); the re-judging turns call-r2, not
    listed, to refused: undone, P1, and the refusal is the re-judging's, not the check's."""
    support.plant_replay(world, support.replay_set() + [support.set_call("call-r2", 3, f"{support.NEW_HIDDEN}/r.txt")])
    b = world.ready("ACT-T-PM", [world.pathmap_addition()], review_kw={"extra": {"replay_refused": ["call-q1"]}})
    r = world.run(b)
    assert r.out.get("result") == "undone", (r.out, r.stderr[-3000:])
    restored(world, b)
    assert world.p1s(b.act)
    text = support.told(world, b, r)
    wrong = [p for p in ("malformed",) + support.CHECK_PHRASES if p in text]
    assert not wrong, ("the replay refused at the check, not at the re-judging", wrong, text)


# --- S16 the landing check ------------------------------------------------------------------------------------------

def test_s16_the_landing_check_flags_control_commits_outside_a_ticket_without_the_trailers(world):
    base = world.head()
    hook = world.repo / ".claude/hooks/pretooluse.py"
    made = {}

    def commit(name, path, trailers):
        p = world.repo / path
        with open(p, "a") as f:
            f.write(f"# {name}\n")
        world.git("add", path)
        world.git("commit", "-q", "-m", f"planted {name}", "-m", trailers)
        made[name] = world.head()

    commit("cto-on-the-hook", ".claude/hooks/pretooluse.py", f"Task: {support.CTO_TASK}\nRole: orchestrator")
    commit("operator-without-act", ".claude/hooks/pretooluse.py", "Role: operator")
    commit("operator-with-act", ".claude/hooks/pretooluse.py", "Role: operator\nAct: ACT-T-1\nAct-sha: " + "a" * 64)
    commit("owner", ".claude/hooks/pretooluse.py", "Role: owner")
    commit("ticket", ".claude/hooks/pretooluse.py", "Task: DAEO-ab12\nRole: engineer")
    commit("cto-records-only", "governance/project/orchestration/CHECKPOINT.md",
           f"Task: {support.CTO_TASK}\nRole: orchestrator")
    assert hook.exists()
    support.require_operator()
    p = subprocess.run([support.PY, "-B", str(support.OPERATOR_SRC / "landing_check.py"), "--repo", str(world.repo),
                        f"{base}..HEAD"], capture_output=True, text=True, env=world.env(), timeout=60)
    assert p.returncode == 0, p.stderr[-3000:]
    items = json.loads(p.stdout)
    flagged = {i["commit"] for i in items}
    assert flagged == {made["cto-on-the-hook"], made["operator-without-act"]}, {
        k: v in flagged for k, v in made.items()}
    assert all(str(i.get("priority", "")).upper() == "P1" for i in items)
