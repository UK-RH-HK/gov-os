"""S9 (the canary), S10 (the headless, closed session), S15 (budget and timeout), S21 (waits and stops by pid).

The stub ``claude`` (``w2_149_support.STUB``) records every call and models Claude Code: ``--restricted`` refuses a
Read outside the working folders by itself, an invalid ``--settings`` file is ignored without a word, and with the
settings loaded the canary's Read is refused only when the wall's own hook (run as Claude Code runs it) refuses it.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time

import pytest

import w2_149_support as support
from w2_149_support import assert_good_launch, assert_nothing_built, assert_refused

BOOL_FLAGS = ("--restricted", "--no-session-persistence", "--strict-mcp-config", "--disable-slash-commands")


def inside(p, d):
    p, d = os.path.realpath(p), os.path.realpath(d)
    return p == d or p.startswith(d + "/")


def no_session_output(world, line):
    side = world.walls / line["kind"] / f"{line['run']}.session.json"
    assert not side.exists(), "the real session's output exists"
    if world.tar(line).exists():
        assert not any(n.endswith(".session.json") for n in world.tar_names(line))


def timeout_duration(parent):
    """The duration a ``timeout`` command line gives, and whether it carries --kill-after."""
    assert parent and os.path.basename(parent[0]) == "timeout", f"the session's parent is not timeout: {parent}"
    args, kill, i = parent[1:], False, 0
    while i < len(args):
        a = args[i]
        if a.startswith("--kill-after") or a.startswith("-k"):
            kill = True
            i += 1 if ("=" in a or (a.startswith("-k") and len(a) > 2)) else 2
            continue
        if a.startswith("-s") or a.startswith("--signal"):
            i += 1 if ("=" in a or (a.startswith("-s") and len(a) > 2)) else 2
            continue
        if a.startswith("-"):
            i += 1
            continue
        return float(a.rstrip("s")), kill
    raise AssertionError(f"no duration in {parent}")


# -- S9 -------------------------------------------------------------------------------------------------------------

def test_s9_settings_made_invalid_refuse_16_before_the_session(world):
    """TS holds the template with hooks.PreToolUse corrupted, approved in APPROVED: the stub ignores the file, the
    canary's Read (inside its own --add-dir folder) is allowed, the launch refuses."""
    world.approve(template={"settings.json.tmpl": "TS"})
    world.write_stub(session={"out": support.good_out("writer")})
    run = world.launch(*world.args("writer", commit="TS"))
    assert_refused(world, run, 16)
    canaries = world.canary_calls()
    assert len(canaries) == 1, "the canary was not run once"
    assert world.session_calls() == [], "the real session started"
    no_session_output(world, run.line)
    assert not (world.sr / "fixtures/evaluation/memory-verdict-4").exists(), "something was delivered"
    assert_good_launch(world, "writer")


def test_s9_the_canary_s_target_is_one_only_the_wall_s_settings_and_hook_refuse(world):
    """Reading 1: the canary plants its file in its own folder, adds that folder with --add-dir (otherwise the session's
    flags), so restricted mode alone allows the Read; valid settings refuse it and the session starts."""
    run = world.deliver("writer")
    assert run.code == 0, run.why()
    line = run.line
    wall, tree = world.wall(line), world.tree(line)
    (canary,) = world.canary_calls()
    (session,) = world.session_calls()
    assert canary["t"] < session["t"], "the canary did not run before the session"
    target = canary["target"]
    assert not inside(target, wall) and not inside(target, tree), "the canary's target lies in the wall or its tree"
    adds = [os.path.realpath(os.path.join(canary["cwd"], d)) for d in canary["adds"]]
    assert any(inside(target, d) for d in adds), "the canary's target is outside every --add-dir folder"
    assert os.path.realpath(str(tree)) in adds, "the canary lacks the session's --add-dir <tree>"
    for flag in BOOL_FLAGS:
        assert canary["flags"].get(flag) is True, f"the canary lacks {flag}"
    for flag in ("--settings", "--tools", "--output-format"):
        assert canary["flags"].get(flag) == session["flags"].get(flag), f"the canary's {flag} differs"
    assert os.path.realpath(canary["cwd"]) == str(wall)
    assert set(canary["env"]) == {"HOME", "PATH", "LANG", "USER"}


def test_s9_a_canary_whose_output_cannot_be_read_refuses_16(world):
    world.write_stub(canary="garbage", session={"out": support.good_out("writer")})
    run = world.launch(*world.args("writer"))
    assert_refused(world, run, 16)
    assert world.session_calls() == []
    no_session_output(world, run.line)
    assert_good_launch(world, "writer")


def test_s9_a_canary_that_times_out_refuses_16(world):
    """writer-short.md: timeout_s 2, so the canary's limit is 2 s (README); the stub's canary sleeps 30 s."""
    world.write_stub(canary="sleep", canary_sleep=30, session={"out": support.good_out("writer")})
    start = time.monotonic()
    run = world.launch(*world.args("writer", brief="writer-short"))
    assert time.monotonic() - start < 25, "the canary was not stopped at its limit"
    assert_refused(world, run, 16)
    assert world.session_calls() == []
    no_session_output(world, run.line)
    assert_good_launch(world, "writer")


def test_s9_a_denial_of_some_other_read_is_not_the_canary_s_refusal(world):
    world.write_stub(canary="wrong_denial", session={"out": support.good_out("writer")})
    run = world.launch(*world.args("writer"))
    assert_refused(world, run, 16)
    assert world.session_calls() == []
    assert_good_launch(world, "writer")


# -- S10 ------------------------------------------------------------------------------------------------------------

def test_s10_the_session_s_line_cwd_environment_and_stdin_flag_by_flag(world):
    run = world.deliver("writer")
    assert run.code == 0, run.why()
    line = run.line
    wall, tree = world.wall(line), world.tree(line)
    (s,) = world.session_calls()
    f = s["flags"]
    assert f.get("-p") is True or f.get("--print") is True, "no -p"
    for flag in BOOL_FLAGS:
        assert f.get(flag) is True, f"no {flag}"
    assert os.path.realpath(os.path.join(s["cwd"], f["--settings"])) == str(wall / ".claude/settings.json")
    assert [os.path.realpath(os.path.join(s["cwd"], d)) for d in s["adds"]] == [str(tree)], "--add-dir is not the tree alone"
    tools = {t for t in re.split(r"[,\s]+", f.get("--tools") or "") if t}
    assert tools == support.KIND_TOOLS["writer"], tools
    assert not tools & support.FORBIDDEN_TOOLS and not any(t.startswith("mcp__") for t in tools)
    assert f.get("--permission-prompts") == "none" and f.get("--output-format") == "json"
    assert f.get("--model") == support.STUB_MODEL, "the model is not the brief's"
    assert float(f["--max-budget-usd"]) == 0.5, "the budget is not the brief's"
    prompt = s["prompt"]
    assert prompt and "\n" not in prompt and "brief.md" in prompt and "out/result.json" in prompt
    assert not re.search(r"(?:^|\s)/", prompt), "the launch prompt names a path of its own"
    assert support.sha256(prompt.encode()) in support.SCRIPT.read_text(), "the prompt's sha256 is not a constant in the script"
    assert os.path.realpath(s["cwd"]) == str(wall)
    env = world.base_env()
    assert s["env"] == {k: env[k] for k in ("HOME", "PATH", "LANG", "USER")}, sorted(s["env"])
    assert s["stdin_devnull"] is True
    duration, kill = timeout_duration(s["parent"])
    assert duration == 30 and kill, (s["parent"], "the brief's timeout_s under timeout --kill-after")


def test_s10_tools_budget_and_timeout_come_from_kinds_yaml_when_the_brief_names_none(world):
    run = world.deliver("checker")
    assert run.code == 0, run.why()
    (s,) = world.session_calls()
    tools = {t for t in re.split(r"[,\s]+", s["flags"].get("--tools") or "") if t}
    assert tools == support.KIND_TOOLS["checker"]
    assert float(s["flags"]["--max-budget-usd"]) == support.KIND_BUDGET["checker"]
    assert timeout_duration(s["parent"])[0] == support.KIND_TIMEOUT["checker"]


def setting_sources(argv):
    """Every value the argv gives --setting-sources (both forms), in order."""
    vals = []
    for i, a in enumerate(argv):
        if a == "--setting-sources":
            vals.append(argv[i + 1] if i + 1 < len(argv) else None)
        elif a.startswith("--setting-sources="):
            vals.append(a.partition("=")[2])
    return vals


def plant_user_settings(world):
    """A user settings file in the planted HOME, as F11 found the real one: allow-all lines, acceptEdits, and (added
    here to make its loading visible) a SessionStart and a PreToolUse hook that each append a line to a log."""
    log = world.rec / "user-hook.log"

    def hook(event):
        return {"type": "command", "command": f"printf '%s\\n' {event} >> {log}"}

    doc = {"permissions": {"allow": ["Bash(*)", "Read(*)", "Edit(*)", "Write(*)"], "defaultMode": "acceptEdits"},
           "hooks": {"SessionStart": [{"hooks": [hook("SessionStart")]}],
                     "PreToolUse": [{"matcher": "*", "hooks": [hook("PreToolUse")]}]}}
    path = world.home / ".claude" / "settings.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n")
    return path, log


def test_s10_the_session_and_the_canary_carry_setting_sources_project_and_no_user_settings_load(world):
    """S10 [changed, DEC-1112 (3): F11]: both calls carry ``--setting-sources project`` exactly, so the planted HOME's
    ``~/.claude/settings.json`` never loads into the wall; the launch still delivers and the wall's own settings (by
    ``--settings``) still refuse the canary."""
    path, log = plant_user_settings(world)
    world.write_stub()
    probe = world.scratch / "probe"
    probe.mkdir()
    env = {"PATH": f"{world.bin}:/usr/bin:/bin", "HOME": str(world.home), "LANG": "C.UTF-8"}
    # The premise: the stub loads the planted user file unless --setting-sources leaves "user" out.
    for extra, loads in (([], True), (["--setting-sources", "user,project"], True),
                         (["--setting-sources", "project"], False)):
        subprocess.run([str(world.bin / "claude"), "-p", *extra, "--output-format", "json", "say ok"],
                       cwd=str(probe), env=env, capture_output=True, text=True, timeout=60)
        (call,) = world.calls()
        assert call["user_settings"]["present"] is True and call["user_settings"]["loaded"] is loads, (extra, call)
        assert log.exists() is loads, (extra, "the user's SessionStart hook ran" if log.exists() else "did not run")
        for name in ("calls.jsonl", "outcomes.jsonl", "user-hook.log"):
            (world.rec / name).unlink(missing_ok=True)

    run = world.deliver("writer")
    calls = world.calls()
    for call in calls:
        kind = "canary" if call["canary"] else "session"
        vals = setting_sources(call["argv"])
        assert vals == ["project"], f"the {kind}'s line gives --setting-sources {vals}; want exactly ['project']"
        assert call["user_settings"]["loaded"] is False, f"the {kind} loaded {path}"
    assert not log.exists(), f"the user's hooks ran in the wall: {log.read_text()!r}"
    assert run.code == 0 and run.line and run.line["status"] == "delivered", run.why()
    assert len(world.canary_calls()) == 1 and len(world.session_calls()) == 1, [c["canary"] for c in calls]
    outcomes = [json.loads(x) for x in (world.rec / "outcomes.jsonl").read_text().splitlines() if x.strip()]
    (canary,) = [o for o in outcomes if o["canary"]]
    assert canary["settings_loaded"] is True and canary["why"] == "hook", \
        f"the canary was not refused by the wall's own settings: {canary}"
    assert canary["user_settings_loaded"] is False


def test_s10_a_brief_asking_more_than_the_kind_s_budget_refuses_10(world):
    world.write_stub(session={"out": support.good_out("writer")})
    before = world.built_state("writer")
    run = world.launch(*world.args("writer", brief="writer-overbudget"))
    assert_refused(world, run, 10)
    assert_nothing_built(world, "writer", before)
    assert_good_launch(world, "writer")


def test_s10_a_kinds_yaml_naming_bash_refuses_11(world):
    """TK's kinds.yaml (approved) gives the writer Bash: never launched."""
    world.approve(template={"kinds.yaml": "TK"})
    world.write_stub(session={"out": support.good_out("writer")})
    before = world.built_state("writer")
    run = world.launch(*world.args("writer", commit="TK"))
    assert_refused(world, run, 11)
    assert_nothing_built(world, "writer", before)
    assert_good_launch(world, "writer")


# -- S15 ------------------------------------------------------------------------------------------------------------

def stopped(world, run):
    assert run.code == 21, run.why()
    line = run.line
    assert line["status"] == "stopped" and line["reason"] == "stopped"
    assert not (world.sr / "fixtures/evaluation/memory-verdict-4").exists(), "something was delivered"
    assert line["delivered"]["files"] == 0
    assert world.tar(line).is_file() and not world.wall(line).exists() and not world.tree(line).exists()
    (s,) = world.session_calls()
    pgid = s["pgid"]
    assert pgid != os.getpgrp(), "the session ran in the script's process group"
    assert support.wait_gone(lambda: support.proc_group(pgid)), f"the session's process group {pgid} survived"
    return s


def test_s15_a_session_past_its_timeout_is_stopped(world):
    world.write_stub(session={"out": support.good_out("writer"), "sleep": 60})
    start = time.monotonic()
    run = world.launch(*world.args("writer", brief="writer-short"))
    assert time.monotonic() - start < 45
    stopped(world, run)


def test_s15_a_session_s_child_is_stopped_with_its_process_group(world):
    world.write_stub(session={"out": support.good_out("writer"), "sleep": 60, "child": True})
    run = world.launch(*world.args("writer", brief="writer-short"))
    stopped(world, run)
    child = int((world.rec / "child.pid").read_text())
    assert support.wait_gone(lambda: support.pid_alive(child)), "the session's child survived"


def test_s15_a_session_ended_by_its_budget_is_stopped_and_nothing_delivered(world):
    """The stub leaves a good result in out/ and ends with is_error and the budget's subtype."""
    world.write_stub(session={"out": support.good_out("writer"), "budget": True})
    run = world.launch(*world.args("writer"))
    s = stopped(world, run)
    assert s["flags"].get("--max-budget-usd") is not None


# -- S21 ------------------------------------------------------------------------------------------------------------

def test_s21_the_script_holds_no_name_matched_wait_or_stop():
    if not support.SCRIPT.is_file():
        pytest.fail("governance/project/orchestration/tools/indep_launch.py does not exist yet (W2-149 builds it)")
    text = support.SCRIPT.read_text()
    assert "pkill" not in text and "killall" not in text
    assert not re.search(r"pgrep[^\n]*-\w*f", text), "pgrep -f in the script"


def test_s21_the_session_s_pid_and_pgid_are_recorded_in_the_run_s_counts_folder(world):
    run = world.deliver("writer")
    assert run.code == 0, run.why()
    folder = world.counts_dir(run.line)
    pid = int((folder / "session.pid").read_text().strip())
    pgid = int((folder / "session.pgid").read_text().strip())
    (s,) = world.session_calls()
    assert s["pgid"] == pgid, "session.pgid is not the session's process group"
    assert pid > 1 and not support.pid_alive(pid), "the session's recorded process is still running"
    assert json.loads((folder / "counts.json").read_text())["status"] == "delivered"
