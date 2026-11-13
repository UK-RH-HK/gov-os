"""W2-148 S17 (the queue and the launch), S18 (the canary), S19 (what the walled session may run: the wall hook the
launcher built, driven as Claude Code drives it), S24 (planted roots; the owner's hand operator untouched; the session's
cwd is the wall folder). A stub `claude` on PATH records argv, cwd, environment, pid and pgid; no real session runs."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

import w2_148_support as support
from w2_148_support import last_json

CLEAN_ENV_PROBE = {"GOV_ROLE": "orchestrator", "GOV_TICKET": "W2-00", "CLAUDE_PROJECT_DIR": "/planted/project"}


def wall_of(w) -> Path:
    return (w.op / "wall").resolve()


# --- S17 the queue and the launch -----------------------------------------------------------------------------------

def test_s17_the_launcher_starts_the_walled_session_for_the_oldest_request_clean_and_by_pid(world):
    b1 = world.ready("ACT-T-Q1", [world.optin_removal()])
    b2 = world.ready("ACT-T-Q2", [world.optin_removal("tests/optin-lifted-guard.txt")])
    world.queue(f"{b1.act} {b1.sha}\n")
    world.queue(f"{b2.act} {b2.sha}\n")
    r = world.launch(env_extra=CLEAN_ENV_PROBE)
    assert r.out.get("result") == "launched", (r.out, r.stderr[-3000:])
    assert r.out.get("approved_sha256") == world.approved_sha()
    assert r.out.get("request") == {"act": b1.act, "sha256": b1.sha}
    calls = world.claude_calls()
    assert len(calls) == 2, "expected the canary, then the real session"
    wall = wall_of(world)
    assert wall != world.op.resolve() and wall.is_dir()
    for c in calls:
        argv = c["argv"]
        assert Path(c["cwd"]).resolve() == wall
        assert "-p" in argv or "--print" in argv
        for flag in ("--restricted", "--no-session-persistence", "--strict-mcp-config", "--max-budget-usd"):
            assert flag in argv, (flag, argv)
        assert Path(argv[argv.index("--settings") + 1]).resolve() == wall / ".claude" / "settings.json"
        assert not [k for k in c["env"] if k.startswith("GOV_")], c["env"]
        assert "CLAUDE_PROJECT_DIR" not in c["env"]
    settings = json.loads((wall / ".claude" / "settings.json").read_text())
    assert settings["permissions"]["deny"] and settings["hooks"]["PreToolUse"]
    session = r.out.get("session") or {}
    assert isinstance(session.get("pid"), int) and session.get("pgid") == calls[1]["pgid"]


BAD_LINES = {"no-sha": "ACT-T-Q1\n", "short-sha": "ACT-T-Q1 abc123\n", "extra-field": "ACT-T-Q1 {sha} now\n",
             "two-requests": "ACT-T-Q1 {sha}\nACT-T-Q1 {sha}\n", "not-an-act": "DEC-9001 {sha}\n"}


@pytest.mark.parametrize("case", list(BAD_LINES))
def test_s17_a_malformed_request_line_is_refused_and_moved_aside(world, case):
    b = world.ready("ACT-T-Q1", [world.optin_removal()])
    req = world.queue(BAD_LINES[case].format(sha=b.sha), name="20261110T100000Z-bad.req")
    r = world.launch()
    assert r.out.get("result") != "launched", r.out
    assert r.out.get("approved_sha256") == world.approved_sha()
    assert world.claude_calls() == [], "a session started for a malformed request"
    assert not req.exists(), "the malformed request was left in the queue"
    assert [p for p in world.op.rglob(req.name) if p != req], "the malformed request was not moved aside"


def test_s17_an_install_file_changed_by_a_byte_refuses_the_launch(world):
    b = world.ready("ACT-T-Q1", [world.optin_removal()])
    world.queue(f"{b.act} {b.sha}\n")
    with open(world.install / "act_class.py", "a") as f:
        f.write("#")
    r = world.launch()
    assert r.out.get("result") == "refused", (r.out, r.stderr[-3000:])
    assert r.out.get("approved_sha256") == world.approved_sha()
    assert world.claude_calls() == []


def test_s17_an_install_file_changed_by_a_byte_refuses_a_run_by_hand(world):
    b = world.ready("ACT-T-Q1", [world.optin_removal()])
    with open(world.install / "class-rules.yaml", "a") as f:
        f.write("#")
    snap = world.snapshot()
    r = world.run(b)
    assert r.out.get("result") == "refused" and r.code != 0, r.out
    assert r.out.get("approved_sha256") == world.approved_sha()
    assert world.snapshot() == snap


def test_s17_no_name_matched_kill_in_the_operator_code():
    support.require_operator()
    found = []
    for p in sorted(support.OPERATOR_SRC.rglob("*")):
        if p.suffix not in (".py", ".sh") or "__pycache__" in p.parts:
            continue
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip().startswith("#"):
                continue
            if re.search(r"\bpkill\b|\bkillall\b|\bpgrep\b[^\n]*\s-f\b", line):
                found.append(f"{p.name}:{n}")
    assert found == []


# --- S18 the canary -------------------------------------------------------------------------------------------------

def test_s18_settings_that_did_not_load_fail_the_canary_and_no_real_session_starts(tmp_path):
    w = support.World(tmp_path / "w", claude_mode="ignored").build()
    b = w.ready("ACT-T-Q1", [w.optin_removal()])
    w.queue(f"{b.act} {b.sha}\n")
    r = w.launch()
    assert r.out.get("result") == "refused", (r.out, r.stderr[-3000:])
    assert len(w.claude_calls()) == 1, "the canary did not run once, or a real session started after it failed"


# --- S19 the wall hook ----------------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def walled(tmp_path_factory):
    w = support.World(tmp_path_factory.mktemp("w2-148-wall") / "w").build()
    b = w.ready("ACT-T-W1", [w.optin_removal()],
                checks=[{"cmd": "test -f tests/optin-lifted.txt", "exit": 0, "count": None}])
    r = w.run(b)
    assert r.out.get("result") == "applied", (r.out, r.stderr[-3000:])
    w.queue(f"{b.act} {b.sha}\n")
    r = w.launch()
    assert r.out.get("result") == "launched", (r.out, r.stderr[-3000:])
    wall = wall_of(w)
    settings = json.loads((wall / ".claude" / "settings.json").read_text())
    frozen = w.frozen_dirs(b)
    assert len(frozen) == 1
    return w, b, wall, settings, frozen[0]


def decide(w, wall, settings, tool, event_or_raw):
    commands = []
    for group in settings.get("hooks", {}).get("PreToolUse", []):
        matcher = group.get("matcher") or "*"
        if matcher == "*" or re.fullmatch(matcher, tool or ""):
            commands += [h["command"] for h in group.get("hooks", []) if h.get("type") == "command"]
    assert commands, "the wall's settings name no PreToolUse hook"
    raw = event_or_raw if isinstance(event_or_raw, str) else json.dumps(event_or_raw)
    verdicts = []
    for cmd in commands:
        p = subprocess.run(["bash", "-c", cmd], input=raw, cwd=wall, env=w.env(CLAUDE_PROJECT_DIR=wall),
                           capture_output=True, text=True, timeout=30)
        if p.returncode == 2:
            verdicts.append("deny")
        elif p.returncode != 0:
            verdicts.append(f"error {p.returncode}")
        else:
            out = last_json(p.stdout)
            hso = out.get("hookSpecificOutput") or {}
            deny = hso.get("permissionDecision") == "deny" or out.get("decision") == "block"
            verdicts.append("deny" if deny else "allow")
    return "deny" if "deny" in verdicts else ("allow" if all(v == "allow" for v in verdicts) else verdicts[0])


def bash(cmd):
    return ("Bash", {"command": cmd, "description": "planted"})


ALLOWED = {
    "operator-run-step": lambda c: bash(f"python3 {c['install']}/operator_run.py run {c['act']} {c['sha']}"),
    "frozen-apply-check": lambda c: bash(f"bash {c['frozen']}/apply.sh check"),
    "frozen-apply-apply": lambda c: bash(f"bash {c['frozen']}/apply.sh apply"),
    "frozen-apply-undo": lambda c: bash(f"bash {c['frozen']}/apply.sh undo"),
    "a-manifest-check": lambda c: bash("test -f tests/optin-lifted.txt"),
    "git-add-a-listed-file": lambda c: bash(f"git -C {c['repo']} add tests/optin-lifted.txt"),
    "read-the-cto-transcript": lambda c: ("Read", {"file_path": f"{c['transcripts']}/{support.SID}.jsonl"}),
}

REFUSED = {
    "sudo": lambda c: bash("sudo true"),
    "git-push": lambda c: bash(f"git -C {c['repo']} push origin main"),
    "git-tag": lambda c: bash(f"git -C {c['repo']} tag v9"),
    "history-rewrite": lambda c: bash(f"git -C {c['repo']} reset --hard HEAD~1"),
    "deletion-outside-the-project": lambda c: bash(f"rm -rf {c['home']}/old-builds"),
    "a-secret": lambda c: ("Read", {"file_path": f"{c['home']}/.ssh/id_ed25519"}),
    "the-held-out-material": lambda c: ("Read", {"file_path": f"{c['home']}/gov-os-workbench/qualification-oracle/a.txt"}),
    "the-sets-root": lambda c: ("Read", {"file_path": f"{c['home']}/gov-os-eval/fixtures/evaluation/planted-set/hidden/q.txt"}),
    "tests-acceptance-write": lambda c: ("Write", {"file_path": f"{c['repo']}/tests/acceptance/W2-1/test_x.py",
                                                   "content": "def test_x(): pass\n"}),
    "tests-acceptance-by-bash": lambda c: bash(f"echo x > {c['repo']}/tests/acceptance/W2-1/test_x.py"),
    "claude-folder-beyond-the-transcript": lambda c: ("Read", {"file_path": f"{c['home']}/.claude/settings.json"}),
    "its-own-approved": lambda c: ("Write", {"file_path": f"{c['install']}/APPROVED", "content": ""}),
    "its-own-brief": lambda c: ("Edit", {"file_path": f"{c['install']}/brief.md", "old_string": "a", "new_string": "b"}),
    "its-own-rule-table": lambda c: bash(f"cp /dev/null {c['install']}/class-rules.yaml"),
    "operator-run-with-an-option": lambda c: bash(
        f"python3 {c['install']}/operator_run.py --config /tmp/other.json run {c['act']} {c['sha']}"),
    "operator-run-chained": lambda c: bash(
        f"python3 {c['install']}/operator_run.py run {c['act']} {c['sha']} && rm -rf {c['home']}"),
    "git-add-an-unlisted-file": lambda c: bash(f"git -C {c['repo']} add src/gov/planted.py"),
    "a-command-not-on-the-list": lambda c: bash("ls"),
    "another-tool": lambda c: ("WebFetch", {"url": "https://example.org", "prompt": "x"}),
}


def _ctx(w, b, frozen):
    return {"install": w.install, "act": b.act, "sha": b.sha, "frozen": frozen, "repo": w.repo, "home": w.home,
            "transcripts": w.transcripts}


def _event(wall, tool, tin):
    return {"session_id": "stub-session", "transcript_path": "/dev/null", "cwd": str(wall),
            "hook_event_name": "PreToolUse", "permission_mode": "default", "tool_name": tool, "tool_input": tin}


@pytest.mark.parametrize("form", list(ALLOWED))
def test_s19_the_wall_hook_allows_each_allowed_form(walled, form):
    w, b, wall, settings, frozen = walled
    tool, tin = ALLOWED[form](_ctx(w, b, frozen))
    assert decide(w, wall, settings, tool, _event(wall, tool, tin)) == "allow"


@pytest.mark.parametrize("cls", list(REFUSED))
def test_s19_the_wall_hook_refuses_each_refused_class(walled, cls):
    w, b, wall, settings, frozen = walled
    tool, tin = REFUSED[cls](_ctx(w, b, frozen))
    assert decide(w, wall, settings, tool, _event(wall, tool, tin)) == "deny"


@pytest.mark.parametrize("raw", ["not json", '{"tool_name": "Bash"}'], ids=["not-json", "no-tool-input"])
def test_s19_the_wall_hook_fails_closed_on_malformed_input(walled, raw):
    w, b, wall, settings, frozen = walled
    assert decide(w, wall, settings, "Bash", raw) == "deny"


# --- S24 planted roots; the owner's operator untouched --------------------------------------------------------------

def test_s24_a_full_run_and_launch_leave_the_owner_s_operator_files_unchanged(tmp_path):
    w = support.World(tmp_path / "w").build(owner_files=True)
    owner = {rel: support.sha256_file(w.op / rel) for rel in w.OWNER_FILES}
    listing = {d: sorted(p.name for p in (w.op / d).iterdir()) for d in (".claude", "hooks")}
    b = w.ready("ACT-T-S24", [w.optin_removal()])
    r = w.run(b)
    assert r.out.get("result") == "applied", (r.out, r.stderr[-3000:])
    b2 = w.ready("ACT-T-S24B", [w.optin_removal("tests/optin-lifted-guard.txt")])
    w.queue(f"{b2.act} {b2.sha}\n")
    r = w.launch()
    assert r.out.get("result") == "launched", (r.out, r.stderr[-3000:])
    assert {rel: support.sha256_file(w.op / rel) for rel in w.OWNER_FILES} == owner
    assert {d: sorted(p.name for p in (w.op / d).iterdir()) for d in (".claude", "hooks")} == listing
    tops = {p.name for p in w.op.iterdir()}
    assert tops <= {"install", "queue", "acts", "log", "wall", "CLAUDE.md", ".claude", "hooks"}, tops
    wall = wall_of(w)
    for c in w.claude_calls():
        assert Path(c["cwd"]).resolve() == wall and wall != w.op.resolve()
        assert Path(c["argv"][c["argv"].index("--settings") + 1]).resolve() != (w.op / ".claude/settings.json").resolve()
    if (wall / "CLAUDE.md").exists():
        assert (wall / "CLAUDE.md").read_text() != w.OWNER_FILES["CLAUDE.md"]
