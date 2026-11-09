"""W2-148 S14 (the apply and its commit), S15 (the post-apply control-file check and the guard replay for (a)), S16 (the
landing check on a planted range of first-parent commits)."""

from __future__ import annotations

import json
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
    holds = " || ".join(f"[ -e {p} ]" for p in (world.op / "log/act-in-progress.txt",
                                                 world.scratch / "log/act-in-progress.txt"))
    b = world.ready("ACT-T-AP", [world.optin_removal(), world.optin_removal("tests/optin-lifted-guard.txt")],
                    live_apply=f"if {holds}; then echo seen > {freeze}; fi")
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
    assert freeze.exists(), "log/act-in-progress.txt (the commit freeze) was not there during the apply"
    assert not (world.op / "log/act-in-progress.txt").exists() and not (world.scratch / "log/act-in-progress.txt").exists()
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


def _calls(w, rows):
    now = datetime.fromisoformat(support.NOW)
    with open(w.calls, "w") as f:
        for cid, hours, path in rows:
            f.write(json.dumps({"id": cid, "time": (now - timedelta(hours=hours)).isoformat(), "role": "engineer",
                                "ticket": None, "event": {"tool_name": "Read", "tool_input": {"file_path": path},
                                                          "cwd": "."}}) + "\n")


CALLS = [("c1", 1, "fixtures/evaluation/new-set/hidden/q.txt"),     # newly refused, listed by the review
         ("c3", 2, "docs/notes.md"),                                 # stays allowed
         ("c-old", 72, "fixtures/evaluation/new-set/hidden/old.txt")]  # newly refused, older than 48 hours


def test_s15_guard_a_path_map_addition_whose_replay_refuses_only_listed_calls_stays(world):
    _calls(world, CALLS)
    b = world.ready("ACT-T-PM", [world.pathmap_addition()], review_kw={"extra": {"replay_refused": ["c1"]}})
    r = world.run(b)
    assert r.out.get("result") == "applied", (r.out, r.stderr[-3000:])
    assert support.sha256_bytes(world.read("repo", "governance/project/path-map.yaml")) == b.manifest["touched"][0]["after"]


def test_s15_a_path_map_addition_whose_replay_refuses_an_unlisted_call_is_undone(world):
    _calls(world, CALLS + [("c2", 3, "fixtures/evaluation/new-set/hidden/r.txt")])
    b = world.ready("ACT-T-PM", [world.pathmap_addition()], review_kw={"extra": {"replay_refused": ["c1"]}})
    r = world.run(b)
    assert r.out.get("result") == "undone", (r.out, r.stderr[-3000:])
    restored(world, b)
    assert world.p1s(b.act)


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
