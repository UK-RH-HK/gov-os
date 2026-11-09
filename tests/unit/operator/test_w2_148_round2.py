"""W2-148 round 2, the engineer's unit tests: the review's findings F2 (the path rule and the live re-hash around the
dry run), F4 (the default notice), F6 (the wall's Bash timeout), F8 (an existing frozen copy never replaced), F9 (the
author required), F10 (an error after G7 pushed), F11 (.git/config and core.hooksPath), F12 (NIGHTLY-RUNNING) and F13
(compact summaries). Everything on planted folders (test_w2_148_kit); stub channels only."""
import json
import os
import sys
import threading
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_w2_148_kit import DAY, OPDIR, Kit, sh, write  # noqa: E402

sys.path.insert(0, str(OPDIR))
sys.dont_write_bytecode = True                         # no __pycache__ in the install's source folder
import opcommon  # noqa: E402
import operator_run  # noqa: E402

ORIG = b"one\ntwo\nthree\n"


@pytest.fixture
def kit(tmp_path):
    return Kit(tmp_path)


def removal():
    return {("repo", "tests/optin-x.txt"): b"one\nthree\n"}


def settings(kit, **over):
    conf = json.loads(kit.config.read_text())
    conf.update(over)
    for k in [k for k, v in over.items() if v is None]:
        conf.pop(k)
    kit.config.write_text(json.dumps(conf))
    return opcommon.load_settings(str(kit.config))


def g8_line(kit):
    return [e for e in kit.log() if e["gate"] == "G8"][-1]


# ---------------------------------------------------------------------------------------------- F2: the path rule
def test_the_path_rule_reads_every_form(tmp_path):
    home = str(tmp_path / "h")
    s = {"repo": home + "/repo", "home": home}
    bad = [f"cd {home}/repo", f"git -C {home}/repo status", f"cat {home}/.bashrc", f"echo x > '{home}/repo/a'",
           "test -d ~/repo", "ls $HOME/repo/x", "ls ${HOME}/repo", 'ls "$HOME"/repo', "cd", "cd ~", "cd ~/",
           'cd "$HOME"', "cd ${HOME} && ls", "x; cd; y", "pushd ~", f"cat ~{os.path.basename(home)}/x"]
    for t in bad:
        assert operator_run.live_path_refs(t, s), t
    good = ['cat "$HOME/.config/x"', "mkdir -p ~/.cache/x", 'cd "$(dirname "$0")"', 'cd "$B" && ls',
            f"ls {home}2/x", f"ls /x{home}/repo", "ls ~/repo2", "cd sub/dir", "# cd ~ in a comment",
            'B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"', "cd -", "cd ~/elsewhere"]
    for t in good:
        assert operator_run.live_path_refs(t, s) is None, t


@pytest.mark.parametrize("where", ["apply", "command", "check", "cd", "home"])
def test_g1_refuses_a_script_that_names_the_live_paths(kit, where):
    kw = {}
    if where == "apply":
        kw["extra_apply"] = f'[ "$step" = check ] && test -d {kit.repo}'
    elif where == "command":
        kw["commands"] = [f"git -C {kit.repo} status"]
    elif where == "check":
        kw["checks"] = [{"cmd": f"test -f {kit.repo}/data/plain.txt", "exit": 0, "count": None}]
    elif where == "cd":
        kw["extra_apply"] = '[ "$step" = never ] && { cd; ls; }'
    else:
        kw["extra_apply"] = f'[ "$step" = never ] && cat {kit.home}/x'
    msha = kit.bundle("ACT-PR1", removal(), **kw)
    rc, res, _ = kit.run("run", "ACT-PR1", msha)
    assert rc != 0 and res["gate"] == "G1" and "the path rule" in res["reason"], res
    assert (kit.repo / "tests/optin-x.txt").read_bytes() == ORIG


def test_g1_refuses_the_repository_named_through_home(kit):
    settings(kit, home=str(kit.tmp))                     # the repository now lies under HOME, as it does live
    msha = kit.bundle("ACT-PR2", removal(), extra_apply='[ "$step" = never ] && ls ~/repo')
    rc, res, _ = kit.run("run", "ACT-PR2", msha)
    assert res["gate"] == "G1" and "through HOME" in res["reason"], res


def reversed_path(p):
    return f'"$(printf %s {str(p)[::-1]!r} | rev)"'


@pytest.mark.parametrize("target,how", [
    ("repo:tests/optin-x.txt", "echo z >>"),                      # a touched file
    ("repo:.claude/hooks/pretooluse.py", "echo '# z' >>"),        # a control file
    ("home:.local/bin/gov", "echo z >"),                          # the pin, created
])
def test_a_live_file_changed_by_the_dry_run_is_restored_and_refused(kit, target, how):
    root, rel = target.split(":")
    path = (kit.repo if root == "repo" else kit.home) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    before = path.read_bytes() if path.exists() else None
    # the dry run only (no .live-marker in the clone); the path built at run time, so the rule cannot see it
    msha = kit.bundle("ACT-LV1", removal(), extra_apply=f'[ "$step" = apply ] && [ ! -e "$PWD/.live-marker" ] && '
                                                       f'{how} {reversed_path(path)}')
    rc, res, _ = kit.run("run", "ACT-LV1", msha)
    assert rc != 0 and res["gate"] == "G8" and "LIVE FILES CHANGED" in res["reason"], res
    assert res["restored"] is True and f"{root}:{rel}" in res["live_changed"]
    assert (path.read_bytes() if path.exists() else None) == before
    assert (kit.repo / "tests/optin-x.txt").read_bytes() == ORIG
    line = g8_line(kit)
    assert line["result"] == "refused" and line["restored"] is True and f"{root}:{rel}" in line["live_changed"]
    p1 = [n for n in kit.notices() if n["priority"] == "P1"]
    assert p1 and "LIVE FILES CHANGED" in p1[-1]["text"]
    assert not (kit.root / "log/operator.lock").exists()


# ------------------------------------------------------------------------------------------ F8: the frozen copy kept
def test_a_stale_requeue_never_replaces_an_applied_acts_frozen_copy(kit):
    msha = kit.bundle("ACT-F8", removal())
    assert kit.run("run", "ACT-F8", msha)[1]["result"] == "applied"
    frozen = kit.root / "acts" / f"ACT-F8-{msha[:12]}"
    held = {p.name: p.read_bytes() for p in frozen.iterdir() if p.is_file()}
    with open(kit.scratch / "acts/ACT-F8/apply.sh", "a") as f:       # the bundle edited, re-queued with the old sha
        f.write("# a fix it forgot to re-review\n")
    rc, res, _ = kit.run("run", "ACT-F8", msha)
    assert rc != 0 and res["gate"] == "G7", res                     # the frozen bytes ran; the live file is applied
    assert {p.name: p.read_bytes() for p in frozen.iterdir() if p.is_file()} == held
    kit.say(f"undo ACT-F8 {msha[:8]}", f"{DAY}T11:30:00+00:00")
    kit.set_clock(f"{DAY}T13:00:00+01:00")
    rc, res, _ = kit.run("undo", "ACT-F8", msha)
    assert res["result"] == "undone", res
    assert (kit.repo / "tests/optin-x.txt").read_bytes() == ORIG


def test_an_existing_frozen_copy_that_changed_is_refused_and_left_alone(kit):
    msha = kit.bundle("ACT-F8B", removal(), dec="DEC-2")            # refused at G2: the copy stays
    assert kit.run("run", "ACT-F8B", msha)[1]["gate"] == "G2"
    frozen = kit.root / "acts" / f"ACT-F8B-{msha[:12]}"
    os.chmod(frozen, 0o755)
    os.chmod(frozen / "list.txt", 0o644)
    (frozen / "list.txt").write_text("tampered\n")
    rc, res, _ = kit.run("run", "ACT-F8B", msha)
    assert res["gate"] == "G1" and "changed after review" in res["reason"], res
    assert (frozen / "list.txt").read_text() == "tampered\n"


def test_a_later_review_round_on_the_same_manifest_is_read(kit):
    msha = kit.bundle("ACT-F8C", removal(), reviewer="cto")         # round 1: the reviewer is the author
    assert kit.run("run", "ACT-F8C", msha)[1]["gate"] == "G4"
    p = kit.scratch / "acts/ACT-F8C/review.md"
    p.write_text(p.read_text().replace('"reviewer": "cto"', '"reviewer": "rev"'))
    rc, res, _ = kit.run("run", "ACT-F8C", msha)
    assert res["result"] == "applied", res


# --------------------------------------------------------------------------------------------- F9: the author required
def test_g4_refuses_a_manifest_with_no_author(kit):
    msha = kit.bundle("ACT-F9", removal(), author=None)
    rc, res, _ = kit.run("run", "ACT-F9", msha)
    assert res["gate"] == "G4" and "author" in res["reason"], res


# ------------------------------------------------------------------------------------- F10: an error after G7 pushed
def test_an_unexpected_error_after_g7_is_pushed_and_counted(kit, tmp_path):
    if os.geteuid() == 0:
        pytest.skip("root reads a mode-000 file")
    target = kit.repo / "tests/optin-x.txt"
    msha = kit.bundle("ACT-F10", removal())
    hook = write(tmp_path / "hook.sh", f'#!/bin/bash\n[ "$1" = after-G6 ] && chmod 000 {target}\nexit 0\n', 0o755)
    env = kit.env()
    env["GOV_OPERATOR_TEST_HOOK"] = str(hook)
    try:
        rc, res, _ = kit.run("run", "ACT-F10", msha, env=env)
    finally:
        os.chmod(target, 0o644)
    assert rc != 0 and res["gate"] == "error", res
    line = [e for e in kit.log() if e["gate"] == "error"][-1]
    assert line["notice"] == "refused" and line["at"] in opcommon.AFTER_G7
    assert any(n["priority"] == "P1" and n["kind"] == "refused" for n in kit.notices())
    kit.pings.write_text("")
    rc, d, _ = kit.run("digest")
    assert [(m["act"], m["gate"]) for m in d["missing_notices"]] == [("ACT-F10", "error")]


def test_an_error_before_g7_is_not_pushed(kit):
    msha = kit.bundle("ACT-F10B", removal())
    write(kit.root / "acts", b"")                                       # acts/ a file: G1 errors
    rc, res, _ = kit.run("run", "ACT-F10B", msha)
    assert res["gate"] == "error" and kit.notices() == []


# ------------------------------------------------------------------------------------ F11: git config and hooksPath
def test_the_dry_run_counts_git_config_in_its_changed_set(kit):
    msha = kit.bundle("ACT-F11", removal(), extra_apply='[ "$step" = apply ] && git config core.hooksPath .hooks-x')
    cfg = (kit.repo / ".git/config").read_bytes()
    rc, res, _ = kit.run("run", "ACT-F11", msha)
    assert res["gate"] == "G8" and "repo:.git/config" in res["reason"], res
    assert (kit.repo / ".git/config").read_bytes() == cfg


def test_a_live_git_config_change_is_undone(kit):
    cfg = (kit.repo / ".git/config").read_bytes()
    msha = kit.bundle("ACT-F11B", removal(), extra_apply='[ "$step" = apply ] && [ -e "$PWD/.live-marker" ] && '
                                                         'git config core.hooksPath .hooks-y')
    rc, res, _ = kit.run("run", "ACT-F11B", msha)
    assert res["result"] == "undone", res
    assert (kit.repo / ".git/config").read_bytes() == cfg
    assert (kit.repo / "tests/optin-x.txt").read_bytes() == ORIG


def test_the_folder_core_hookspath_names_is_a_control(kit):
    hooks = kit.tmp / "shared-hooks"
    write(hooks / "pre-commit", "#!/bin/bash\nexit 0\n", 0o755)
    sh("git", "config", "core.hooksPath", str(hooks), cwd=kit.repo)
    before = (hooks / "pre-commit").read_bytes()
    msha = kit.bundle("ACT-F11C", removal(), extra_apply=f'[ "$step" = apply ] && [ -e "$PWD/.live-marker" ] && '
                                                         f'echo "# z" >> {reversed_path(hooks / "pre-commit")}')
    rc, res, _ = kit.run("run", "ACT-F11C", msha)
    assert res["result"] == "undone" and res["gate"] == "after-check", res
    assert (hooks / "pre-commit").read_bytes() == before
    snap = operator_run.control_snapshot(opcommon.load_settings(str(kit.config)), kit.env())
    assert ("path", str(hooks / "pre-commit")) in snap and ("repo", ".git/config") in snap


# ---------------------------------------------------------------------------------------------- F12: NIGHTLY-RUNNING
def test_g9_holds_while_the_nightly_flag_is_fresh(kit):
    msha = kit.bundle("ACT-F12", removal())
    flag = write(kit.scratch / "NIGHTLY-RUNNING", "2026-11-10 04:00:05 nightly: running\n")
    threading.Timer(2.0, flag.unlink).start()
    rc, res, _ = kit.run("run", "ACT-F12", msha)
    assert res["result"] == "applied", res
    held = [e for e in kit.log() if e["gate"] == "G9" and e["result"] == "held"]
    assert held and any("NIGHTLY-RUNNING" in w for w in held[0]["why"])


def test_a_dead_nightlys_old_flag_does_not_hold(kit):
    s = opcommon.load_settings(str(kit.config))
    flag = write(kit.scratch / "NIGHTLY-RUNNING", "old\n")
    assert any("NIGHTLY-RUNNING" in w for w in opcommon.holds(s))
    old = time.time() - 7 * 3600
    os.utime(flag, (old, old))
    assert not any("NIGHTLY-RUNNING" in w for w in opcommon.holds(s))


# ----------------------------------------------------------------------------------------- F13: compact summaries
def test_a_compact_summary_is_never_the_owners_line():
    e = {"type": "user", "origin": {"kind": "human"}, "message": {"role": "user", "content": "yes ACT-X 12345678"}}
    assert opcommon.owner_text(e) == "yes ACT-X 12345678"
    assert opcommon.owner_text(dict(e, isCompactSummary=True)) is None
    assert opcommon.owner_text(dict(e, isMeta=True)) is None


# ------------------------------------------------------------------------------------------- F6: the Bash timeout
def test_the_wall_sizes_the_bash_timeout_to_the_session(kit):
    settings(kit, session_timeout_s=1800)
    msha = kit.bundle("ACT-F6", removal())
    write(kit.root / "queue/one.req", f"ACT-F6 {msha}\n")
    assert kit.launch()[1]["result"] == "launched"
    env = json.loads((kit.root / "wall/.claude/settings.json").read_text())["env"]
    assert env == {"BASH_DEFAULT_TIMEOUT_MS": "1740000", "BASH_MAX_TIMEOUT_MS": "1740000"}
    assert "timeout_ms: 1740000" in (kit.root / "wall/request.txt").read_text()
    assert "timeout_ms" in (kit.root / "wall/brief.md").read_text()


# ---------------------------------------------------------------------------------------------- F4: the notice line
def test_the_notice_line_fits_190_and_keeps_its_head_and_undo():
    line = opcommon.notice_line("P1", "ACT-SOME-LONG-NAME-1", "refused at G8: " + "x" * 400,
                                "to undo, say: undo ACT-SOME-LONG-NAME-1 0123abcd")
    assert len(line) <= 190 and line.startswith("P1 ACT-SOME-LONG-NAME-1 | refused at G8: ")
    assert line.endswith(" | to undo, say: undo ACT-SOME-LONG-NAME-1 0123abcd") and "TEST" not in line
    assert opcommon.notice_line("info", "ACT-A", "applied (a) 12:00") == "info ACT-A | applied (a) 12:00"


def test_the_default_notice_goes_through_the_three_channels(kit):
    rec = kit.tmp / "channels.jsonl"
    stub = f'#!/usr/bin/env python3\nimport json, sys\nopen("{rec}", "a").write(json.dumps(sys.argv) + "\\n")\n'
    write(kit.tmp / "stub-claude", stub, 0o755)
    write(kit.tmp / "stub-ps", stub, 0o755)
    write(kit.tmp / "stub-wslpath", "#!/bin/bash\necho 'C:\\\\toast.ps1'\n", 0o755)
    settings(kit, push_cmd=None, push_claude=str(kit.tmp / "stub-claude"), powershell=str(kit.tmp / "stub-ps"),
             wslpath=str(kit.tmp / "stub-wslpath"))
    assert "push_cmd" not in json.loads(kit.config.read_text())
    msha = kit.bundle("ACT-F4", removal())
    rc, res, _ = kit.run("run", "ACT-F4", msha)
    assert res["result"] == "applied", res
    calls = [json.loads(x) for x in rec.read_text().splitlines()]
    toast = [c for c in calls if c[0].endswith("stub-ps")]
    push = [c for c in calls if c[0].endswith("stub-claude")]
    assert len(toast) == 1 and len(push) == 1
    line = toast[0][toast[0].index("-Body") + 1]
    assert len(line) <= 190 and line.startswith("info ACT-F4 | applied (a) ")
    assert line.endswith(f"to undo, say: undo ACT-F4 {msha[:8]}") and "TEST" not in line
    assert push[0][1:3] == ["-p", "--model"] and line in push[0][-1] and "PushNotification" in push[0][-1]
    n = kit.notices()
    assert [x["kind"] for x in n] == ["applied"] and n[0]["line"] == line
    assert not any("deadman" in " ".join(c) for c in calls)
