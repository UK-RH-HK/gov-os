"""FM-5 of the fix under the closed ticket DAEO-ma4q: the writer's check runs in every real writer launch.

A the brief prints the launch line (and ``LAUNCH.txt``); B the wall's settings carry the Stop hook for the writer only;
C ``writer-run`` holds the loop by code for a launch that loads no hooks (a planted fake ``claude`` script, the same
session resumed with ids and codes only); D the real hook command of the launch line blocks on a planted refused set.
B is checked by rendering through the launcher's own ``--dry`` run (the unit tests' planted World, a planted HOME and
sets root), not by the template text alone. No real session; planted sets only."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shlex
import sys
from pathlib import Path

import pytest

import w2_204_support as K
import w2_204_writer_loop_support as L
from w2_204_support import HIDDEN

ROOT = Path(__file__).resolve().parents[3]
SID = "5f0d6c1e-2b7a-4c39-9d41-0a1b2c3d4e5f"
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
TOOLS = {"Read", "Grep", "Glob", "Write", "Edit", "TodoWrite"}


# -- A: the launch line -------------------------------------------------------------------------------------------------
def _launch(world, kind="writer", name="w1", round_no=1):
    out = world.base / "briefs" / name
    run = world.brief(kind, HIDDEN, out, round_no=round_no)
    assert run.code == 0, run
    return out, run


def _launch_tokens(out, run):
    lines = run.lines
    brief_at = next(i for i, x in enumerate(lines) if x.startswith("BRIEF "))
    assert len(lines) > brief_at + 1 and lines[brief_at + 1].startswith("LAUNCH writer "), ("LAUNCH after BRIEF", lines)
    command = lines[brief_at + 1][len("LAUNCH writer "):]
    return command, shlex.split(command)


def _value(tokens, flag):
    assert tokens.count(flag) == 1, (flag, tokens)
    return tokens[tokens.index(flag) + 1]


def test_fm5_the_writer_brief_prints_the_launch_line_with_the_hook_loading_flags(world):
    out, run = _launch(world)
    assert re.fullmatch(r"BRIEF writer round 1 [0-9a-f]{12}", run.lines[0]), run.lines
    command, tokens = _launch_tokens(out, run)
    assert _value(tokens, "--setting-sources") == "project"
    assert _value(tokens, "--settings") == f"{out}/.claude/settings.json"
    assert "--restricted" in tokens and "--strict-mcp-config" in tokens, tokens
    assert set(_value(tokens, "--tools").split(",")) == TOOLS, tokens
    assert _value(tokens, "--model") == "claude-sonnet-5-5"
    assert "-p" in tokens or "--print" in tokens, tokens
    assert "--safe-mode" not in tokens and "--no-session-persistence" not in tokens, tokens


def test_fm5_launch_txt_holds_the_same_command(world):
    out, run = _launch(world)
    command, _ = _launch_tokens(out, run)
    assert (out / "LAUNCH.txt").read_text(encoding="utf-8").strip() == command


def test_fm5_a_round_2_writer_brief_prints_the_launch_line_too(world):
    world.write_half(HIDDEN, K.clean_specs())
    world.write_notes(HIDDEN, 1)
    out, run = _launch(world, name="writer-2", round_no=2)
    command, tokens = _launch_tokens(out, run)
    assert (out / "LAUNCH.txt").read_text(encoding="utf-8").strip() == command
    assert _value(tokens, "--settings") == f"{out}/.claude/settings.json"


def test_fm5_the_checker_brief_prints_no_launch_writer_line(world):
    world.write_half(HIDDEN, K.clean_specs())
    out, run = _launch(world, "checker", "c1")
    assert not any(x.startswith("LAUNCH") for x in run.lines), run.lines
    assert not (out / "LAUNCH.txt").exists()


def test_fm5_nothing_the_brief_prints_or_writes_names_a_question(world):
    world.write_half(HIDDEN, K.clean_specs())
    out, run = _launch(world, name="w1")
    _launch_tokens(out, run)
    assert not any(w in run.text for w in K.planted_words())
    assert K.files_holding(out, K.planted_words(), skip=[out / "input"]) == []


# -- D: the real hook command of the launch line ------------------------------------------------------------------------
def test_fm5_the_hook_the_launch_line_loads_blocks_a_refused_set_with_ids_and_codes_only(world):
    L.briefed(world)
    out, run = _launch(world, name="w1")
    _, tokens = _launch_tokens(out, run)
    settings = Path(_value(tokens, "--settings"))
    assert settings.is_file() and settings.parent.parent == out, settings
    L.put_set(world, out, L.faulty(world, "form"))
    call = L.run_hook(world, out)
    lines = L.reason_lines(call)
    assert "PF-FORM refused 1 q07" in lines, call
    assert all(L.PF_LINE.fullmatch(x) for x in lines), lines
    assert not any(w in call.text for w in K.planted_words())
    doc = L.record(world)
    assert doc["returns"] == 1 and doc["ended"] is None and doc["refused"] == {"PF-FORM": ["q07"]}, doc


# -- B: the wall's settings (rendered through the launcher's own dry run) ------------------------------------------------
def _unit_world(tmp_path):
    path = ROOT / "tests" / "unit" / "orchestration" / "test_w2_149_indep_launch.py"
    spec = importlib.util.spec_from_file_location("fm5_w2_149_unit_world", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod, mod.World(tmp_path)


def _wall_settings(tmp_path, kind):
    tmp_path.mkdir(parents=True, exist_ok=True)
    mod, w = _unit_world(tmp_path)
    if kind != "writer":
        w.plant_set()  # a checker's wall holds the delivered set
    rc, counts, proc = w.launch(kind, seed=1, dry=True)
    assert rc == 0, (rc, counts, proc.stderr[-400:])
    wall = w.wall(counts)
    return w, wall, json.loads((wall / ".claude" / "settings.json").read_text(encoding="utf-8")), counts


def _canon_sha(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True).encode()).hexdigest()


def test_fm5_the_writer_wall_settings_carry_the_stop_hook_filled_from_the_launch(tmp_path):
    w, wall, settings, _ = _wall_settings(tmp_path, "writer")
    stops = settings["hooks"].get("Stop")
    assert stops and len(stops) == 1 and len(stops[0]["hooks"]) == 1, settings["hooks"]
    hook = stops[0]["hooks"][0]
    assert hook["type"] == "command"
    cmd = hook["command"]
    assert "gov.memaudit" in cmd and "writer-check" in cmd, cmd
    tokens = shlex.split(cmd)
    assert _value(tokens, "--sets-root") == str(w.sets), cmd
    assert _value(tokens, "--commit") == w.commit, cmd
    assert _value(tokens, "--folder") == str(wall), cmd
    assert Path(_value(tokens, "--repo")).resolve() == w.repo.resolve(), cmd
    assert re.search(r"memory-recall-3", cmd), ("the launch's set name", cmd)
    assert not re.search(r"@[A-Z_]+@", json.dumps(settings)), "an unfilled token"


def test_fm5_the_writer_wall_keeps_its_other_settings_and_the_checker_wall_has_no_stop_hook(tmp_path):
    _, _, writer, _ = _wall_settings(tmp_path / "a", "writer")
    wall_hook = writer["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
    assert wall_hook.startswith("python3 -I ") and wall_hook.split()[3:4] and ".claude/wall_hook.py" in wall_hook
    assert writer["hooks"]["PreToolUse"][0]["matcher"] == "*"
    assert writer["model"] and writer["enableAllProjectMcpServers"] is False and writer["cleanupPeriodDays"] == 1
    _, _, checker, _ = _wall_settings(tmp_path / "b", "checker")
    assert "Stop" not in checker["hooks"] and list(checker["hooks"]) == ["PreToolUse"], checker["hooks"]


def test_fm5_the_template_s_permissions_and_wall_hook_are_unchanged():
    tmpl = json.loads((ROOT / "governance" / "project" / "indep-walls" / "settings.json.tmpl").read_text(encoding="utf-8"))
    assert _canon_sha(tmpl["permissions"]) == "3cd1cae556bbbbe16bec9fb66847b9ddbdb818314b46c9a45bb60072fc23d55f"
    assert _canon_sha(tmpl["hooks"]["PreToolUse"]) == "9b1a502e7d89834be52bb9cc20d2725f9cf38144a8974a6bf2172ccb0577d29d"
    stop = tmpl["hooks"].get("Stop")
    assert stop and "writer-check" in json.dumps(stop), "no Stop hook running writer-check in the template"
    text = json.dumps(stop)
    for token in ("@SETS_ROOT@", "@SET@", "@COMMIT@", "@REPO@", "@WALL@", "@GOVSRC@"):
        assert token in text, token


# -- C: writer-run ---------------------------------------------------------------------------------------------------------
FAKE = r'''#!{python}
import json, os, shutil, sys
state = os.environ["FM5_STATE"]
argv = sys.argv[1:]
stdin = "" if sys.stdin.isatty() else sys.stdin.read()
log = os.path.join(state, "calls.jsonl")
n = sum(1 for _ in open(log)) if os.path.exists(log) else 0
with open(log, "a") as f:
    f.write(json.dumps({{"argv": argv, "stdin": stdin, "cwd": os.path.realpath(os.getcwd())}}) + "\n")
plan = json.load(open(os.path.join(state, "plan.json")))
which = plan["fix_at"] is not None and n >= plan["fix_at"]
src = os.path.join(state, "good" if which else "bad")
dst = os.path.join(os.getcwd(), "out", "set")
shutil.rmtree(dst, ignore_errors=True)
shutil.copytree(src, dst)
print(json.dumps({{"type": "result", "result": "done"}}))
'''


def _fake(world, tmp_path, fix_at):
    state = tmp_path / "fm5state"
    state.mkdir()
    exe = tmp_path / "bin" / "fake-claude"
    exe.parent.mkdir()
    exe.write_text(FAKE.format(python=sys.executable), encoding="utf-8")
    exe.chmod(0o755)
    world.write_half(HIDDEN, L.faulty(world, "form"), folder=state / "bad")
    world.write_half(HIDDEN, K.clean_specs(), folder=state / "good")
    (state / "plan.json").write_text(json.dumps({"fix_at": fix_at}), encoding="utf-8")
    return exe, state


def _calls(state):
    path = state / "calls.jsonl"
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()] if path.exists() else []


def _writer_run(world, folder, exe, state, *extra):
    return world.run("cli", "writer-run", *world.common(HIDDEN), "--repo", world.repo, "--commit", world.audit_commit,
                     "--folder", folder, "--claude", exe, *extra, env={"FM5_STATE": str(state)})


def _resumed(call):
    a = call["argv"]
    return a[a.index("--resume") + 1] if "--resume" in a else None


def test_fm5_writer_run_resumes_the_same_session_with_ids_and_codes_only_and_ends_pass(world, tmp_path):
    L.briefed(world)
    folder, _ = _launch(world, name="w1")
    exe, state = _fake(world, tmp_path, fix_at=1)
    run = _writer_run(world, folder, exe, state, "--session-id", SID)
    assert run.code == 0, run
    calls = _calls(state)
    assert len(calls) == 2, calls
    first, second = calls
    assert "--resume" not in first["argv"] and first["argv"][first["argv"].index("--session-id") + 1] == SID, first
    assert _resumed(second) == SID and "--session-id" not in second["argv"], second
    assert first["cwd"] == second["cwd"] == str(folder.resolve()), calls
    prompt = " ".join(second["argv"]) + second["stdin"]
    assert "q07" in prompt and "PF-FORM" in prompt, prompt
    assert not any(w in prompt for w in K.planted_words()), "a question's text in the resume prompt"
    doc = L.record(world)
    assert doc["returns"] == 1 and doc["ended"] == "pass", doc
    assert not any(w in run.text for w in K.planted_words())


def test_fm5_writer_run_without_a_session_id_keeps_one_id_for_the_start_and_the_resume(world, tmp_path):
    L.briefed(world)
    folder, _ = _launch(world, name="w1")
    exe, state = _fake(world, tmp_path, fix_at=1)
    run = _writer_run(world, folder, exe, state)
    assert run.code == 0, run
    first, second = _calls(state)
    sid = first["argv"][first["argv"].index("--session-id") + 1]
    assert UUID.fullmatch(sid) and _resumed(second) == sid, (first, second)


def test_fm5_writer_run_a_clean_first_session_is_not_resumed(world, tmp_path):
    L.briefed(world)
    folder, _ = _launch(world, name="w1")
    exe, state = _fake(world, tmp_path, fix_at=0)
    run = _writer_run(world, folder, exe, state, "--session-id", SID)
    assert run.code == 0, run
    assert len(_calls(state)) == 1
    doc = L.record(world)
    assert doc["returns"] == 0 and doc["ended"] == "pass", doc


def test_fm5_writer_run_a_never_fixing_writer_gets_three_returns_then_ends_limit(world, tmp_path):
    L.briefed(world)
    folder, _ = _launch(world, name="w1")
    exe, state = _fake(world, tmp_path, fix_at=None)
    run = _writer_run(world, folder, exe, state, "--session-id", SID)
    assert run.code == 0, run
    calls = _calls(state)
    assert len(calls) == 4, "the start and 3 returns, never a 4th return"
    assert [_resumed(c) for c in calls] == [None, SID, SID, SID], calls
    assert all("--session-id" not in c["argv"] for c in calls[1:])
    for c in calls[1:]:
        prompt = " ".join(c["argv"]) + c["stdin"]
        assert "q07" in prompt and "PF-FORM" in prompt
        assert not any(w in prompt for w in K.planted_words())
    doc = L.record(world)
    assert doc["returns"] == 3 and doc["ended"] == "limit" and doc["refused"] == {"PF-FORM": ["q07"]}, doc
    assert L.landed(world) == {}, "writer-run wrote into hidden/"


# -- the writer's own folder permissions (from the real session: Edit and Write into out/ were denied) --------------------
def _folder_settings(world):
    out, run = _launch(world, name="perm")
    _, tokens = _launch_tokens(out, run)
    return out, tokens, json.loads((out / ".claude" / "settings.json").read_text(encoding="utf-8"))


def _forms(out, tail):
    """The wall's form is ``/`` + the absolute path (so ``//home/...``); the single-slash form is taken too."""
    return {f"/{out}/{tail}", f"{out}/{tail}"}


def test_fm5_the_writer_settings_allow_write_and_edit_into_out_only(world):
    out, _, doc = _folder_settings(world)
    allow = set(doc.get("permissions", {}).get("allow", []))
    for tool in ("Write", "Edit"):
        assert any(f"{tool}({x})" in allow for x in _forms(out, "out/**")), (tool, sorted(allow))
    assert not any(a.startswith(("Write(", "Edit(")) and "/out/**" not in a for a in allow), sorted(allow)


def test_fm5_the_writer_settings_deny_edits_to_its_own_config_input_and_brief(world):
    out, _, doc = _folder_settings(world)
    deny = set(doc.get("permissions", {}).get("deny", []))
    for tail in (".claude/**", "input/**", "brief.md"):
        assert any(f"Edit({x})" in deny for x in _forms(out, tail)), (tail, sorted(deny))


def test_fm5_the_stop_hook_block_is_unchanged_beside_the_permissions(world):
    out, _, doc = _folder_settings(world)
    assert list(doc["hooks"]) == ["Stop"] and len(doc["hooks"]["Stop"]) == 1, doc["hooks"]
    assert "writer-check" in doc["hooks"]["Stop"][0]["hooks"][0]["command"]
    assert doc["hooks"]["Stop"][0]["hooks"][0]["type"] == "command"


def test_fm5_the_launch_line_asks_no_permission_prompts(world):
    _, tokens, _ = _folder_settings(world)
    assert _value(tokens, "--permission-prompts") == "none", tokens
