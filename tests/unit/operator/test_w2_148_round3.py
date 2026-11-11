"""W2-148 round 3 (DEC-1106), the engineer's unit tests: the restore rule (F15) after the G8 dry run and in the (a)
after-check's undo, the two new test-hook points `in-G8` and `in-apply-checks`, and the commit freeze in the install
folder. Everything on planted folders (test_w2_148_kit); stub channels and a stub crontab only."""
import json
import os
import subprocess
import sys
import threading
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_w2_148_kit import DAY, OPDIR, Kit, sh, write  # noqa: E402

sys.path.insert(0, str(OPDIR))
sys.dont_write_bytecode = True
import opcommon  # noqa: E402
import operator_run  # noqa: E402

ORIG = b"one\ntwo\nthree\n"
AFTER = b"one\nthree\n"
OPTIN = "tests/optin-x.txt"
PMAP = "governance/project/path-map.yaml"


@pytest.fixture
def kit(tmp_path):
    return Kit(tmp_path)


def removal():
    return {("repo", OPTIN): AFTER}


def settings(kit, **over):
    conf = json.loads(kit.config.read_text())
    conf.update(over)
    kit.config.write_text(json.dumps(conf))
    return opcommon.load_settings(str(kit.config))


def hooked(kit, point, body):
    """An env whose test hook runs `body` (bash) at `point` only; $2 is the frozen folder."""
    hook = write(kit.tmp / f"hook-{point}.sh", f'#!/bin/bash\n[ "$1" = {point} ] || exit 0\n{body}\n', 0o755)
    env = kit.env()
    env["GOV_OPERATOR_TEST_HOOK"] = str(hook)
    return env


def commit_cmd(kit, *paths):
    """The tests' hooks commit only their own paths (`git commit -- <paths>`), with their own git identity."""
    ps = " ".join(paths)
    return (f"git -C {kit.repo} add -- {ps} && git -C {kit.repo} -c user.email=h@h -c user.name=h "
            f"commit -q -m 'concurrent: someone else' -- {ps}")


def p1s(kit):
    return [n for n in kit.notices() if n["priority"] == "P1"]


def locked(kit):
    return (kit.root / "log/operator.lock").exists()


def stateful_crontab(kit):
    f = kit.tmp / "crontab.txt"
    write(kit.bin / "crontab", f'#!/bin/bash\nf={f}\ncase "$1" in\n  -l) [ -f "$f" ] && {{ cat "$f"; exit 0; }}; '
                               f'exit 1 ;;\n  -r) rm -f "$f" ;;\n  -) cat > "$f" ;;\n  *) cat "$1" > "$f" ;;\nesac\n',
          0o755)
    write(f, "0 5 * * * true\n")
    return f


# ======================================================================================= the commit freeze (DEC-1106 (3))
def test_the_freeze_defaults_to_the_install_folder(kit):
    conf = json.loads(kit.config.read_text())
    assert "freeze" not in conf
    s = opcommon.load_settings(str(kit.config))
    assert s["freeze"] == str(kit.root / "install" / "act-in-progress.txt")
    assert "/log/" not in s["freeze"]


def test_the_approved_check_and_the_control_hash_never_count_the_freeze(kit):
    s = opcommon.load_settings(str(kit.config))
    before = operator_run.control_snapshot(s, kit.env())
    write(kit.install / "act-in-progress.txt", "ACT-X 00 stale\n")
    ok, _, why, _ = opcommon.approved_state(str(kit.install))
    assert ok, why
    assert operator_run.control_snapshot(s, kit.env()) == before
    write(kit.install / "other.txt", "x\n")                            # any other file still refuses
    assert not opcommon.approved_state(str(kit.install))[0]


def test_the_freeze_is_claimed_once_and_released_only_by_its_writer(kit):
    s = opcommon.load_settings(str(kit.config))
    token = opcommon.claim_freeze(s, "ACT-A", "0" * 64)
    assert token and Path(s["freeze"]).read_text() == token
    assert opcommon.claim_freeze(s, "ACT-B", "1" * 64) is None        # held: no second writer
    assert opcommon.release_freeze(s, "someone else's\n") is False and Path(s["freeze"]).exists()
    assert opcommon.release_freeze(s, token) is True and not Path(s["freeze"]).exists()
    write(s["freeze"], "stale\n")
    assert opcommon.release_freeze(s, token) is False and Path(s["freeze"]).read_text() == "stale\n"


def test_the_freeze_exists_during_the_apply_in_install_never_in_a_log_and_is_gone_after(kit):
    rec = kit.tmp / "seen.txt"
    msha = kit.bundle("ACT-FZ1", removal())
    env = hooked(kit, "in-apply-checks",
                 f'{{ [ -e {kit.install}/act-in-progress.txt ] && echo install-freeze; '
                 f'[ -e {kit.root}/log/act-in-progress.txt ] && echo log-freeze; '
                 f'[ -e {kit.scratch}/log/act-in-progress.txt ] && echo scratch-freeze; '
                 f'[ -e {kit.repo}/.git/index.lock ] && echo index-lock; '
                 f'{sys.executable} {kit.install}/operator_run.py --config {kit.config} digest | tail -1; }} > {rec}')
    rc, res, _ = kit.run("run", "ACT-FZ1", msha, env=env)
    assert res["result"] == "applied", res
    seen = rec.read_text().splitlines()
    assert seen[0] == "install-freeze" and len(seen) == 2, seen       # no log freeze, no index.lock
    assert json.loads(seen[1])["result"] == "digest"                    # the APPROVED check passed meanwhile
    assert not (kit.install / "act-in-progress.txt").exists()
    assert not (kit.root / "log/act-in-progress.txt").exists()


def test_a_stale_freeze_holds_g9_and_is_never_removed_by_the_run(kit):
    settings(kit, hold_max_s=1)
    stale = write(kit.install / "act-in-progress.txt", "ACT-OLD 1234 an earlier run\n")
    msha = kit.bundle("ACT-FZ2", removal())
    rc, res, _ = kit.run("run", "ACT-FZ2", msha)
    assert res["gate"] == "G9" and res["approved_sha256"], res           # held (then the test's limit), not APPROVED
    assert stale.read_text() == "ACT-OLD 1234 an earlier run\n"
    held = [e for e in kit.log() if e["gate"] == "G9" and e["result"] == "held"]
    assert held and any("act-in-progress.txt" in w for w in held[0]["why"])
    assert (kit.repo / OPTIN).read_bytes() == ORIG


def test_a_stale_freeze_holds_until_it_is_gone_then_the_run_proceeds(kit):
    stale = write(kit.install / "act-in-progress.txt", "stale\n")
    msha = kit.bundle("ACT-FZ3", removal())
    threading.Timer(2.0, stale.unlink).start()
    rc, res, _ = kit.run("run", "ACT-FZ3", msha)
    assert res["result"] == "applied", res
    assert [e["result"] for e in kit.log() if e["gate"] == "G9"] == ["held", "pass"]
    assert not stale.exists()


def test_the_launcher_holds_on_a_stale_freeze_with_a_g9_line(kit):
    write(kit.install / "act-in-progress.txt", "stale\n")
    msha = kit.bundle("ACT-FZ4", removal())
    write(kit.root / "queue/one.req", f"ACT-FZ4 {msha}\n")
    rc, res, _ = kit.launch()
    assert res["result"] == "held" and res["gate"] == "G9", res
    assert [e["result"] for e in kit.log() if e["gate"] == "G9"] == ["held"]
    assert (kit.install / "act-in-progress.txt").read_text() == "stale\n"


def test_the_owners_undo_never_writes_over_a_stale_freeze(kit):
    msha = kit.bundle("ACT-FZ5", removal())
    assert kit.run("run", "ACT-FZ5", msha)[1]["result"] == "applied"
    write(kit.install / "act-in-progress.txt", "stale\n")
    kit.say(f"undo ACT-FZ5 {msha[:8]}", f"{DAY}T11:30:00+00:00")
    kit.set_clock(f"{DAY}T13:00:00+01:00")
    rc, res, _ = kit.run("undo", "ACT-FZ5", msha)
    assert res["result"] == "refused" and "freeze" in res["reason"], res
    assert (kit.install / "act-in-progress.txt").read_text() == "stale\n"
    assert (kit.repo / OPTIN).read_bytes() == AFTER                     # nothing written
    (kit.install / "act-in-progress.txt").unlink()
    rc, res, _ = kit.run("undo", "ACT-FZ5", msha)
    assert res["result"] == "undone" and (kit.repo / OPTIN).read_bytes() == ORIG
    assert not (kit.install / "act-in-progress.txt").exists()


@pytest.mark.parametrize("own", [True, False])
def test_the_journals_undo_removes_only_the_freeze_its_run_wrote(kit, own):
    """A session dies mid-apply (killed in the hook): the next recover undoes it and removes the freeze only when it
    still holds the token the dead run recorded in its journal."""
    msha = kit.bundle("ACT-FZ6", removal())
    env = hooked(kit, "in-apply-checks", "kill -9 $PPID")
    r = subprocess.run([sys.executable, str(kit.install / "operator_run.py"), "--config", str(kit.config), "run",
                        "ACT-FZ6", msha], capture_output=True, env=env, timeout=120)
    assert r.returncode != 0
    freeze = kit.install / "act-in-progress.txt"
    j = json.loads((kit.root / "log/journal.json").read_text())
    assert freeze.read_text() == j["freeze"]
    if not own:
        freeze.write_text("someone else's freeze\n")
    rc, res, _ = kit.run("recover")
    assert res["result"] == "undone", res
    assert (kit.repo / OPTIN).read_bytes() == ORIG
    assert freeze.exists() is (not own)


# =============================================================================== the restore rule after G8 (DEC-1106 (1))
def test_g8_the_dry_runs_own_change_is_restored_and_refused_without_the_lock(kit):
    msha = kit.bundle("ACT-R8A", removal())
    env = hooked(kit, "in-G8", f"cp {kit.scratch}/acts/ACT-R8A/after/repo/{OPTIN} {kit.repo}/{OPTIN}")
    rc, res, _ = kit.run("run", "ACT-R8A", msha, env=env)
    assert rc != 0 and res["gate"] == "G8" and "live files changed" in res["reason"], res
    assert res["restored_files"] == [f"repo:{OPTIN}"] and res["left"] == [] and res["restored"] is True
    assert (kit.repo / OPTIN).read_bytes() == ORIG
    p1 = p1s(kit)
    assert p1 and "live files changed" in p1[-1]["text"] and OPTIN in p1[-1]["text"]
    assert not locked(kit)


def test_g8_a_concurrent_commit_to_the_path_map_is_left_with_the_lock(kit):
    pm = kit.repo / PMAP
    new = pm.read_text().replace('hidden: ["fixtures/a/**"]', 'hidden: ["fixtures/a/**", "fixtures/z/**"]')
    write(kit.tmp / "pm.new", new)
    msha = kit.bundle("ACT-R8B", removal())
    env = hooked(kit, "in-G8", f"cp {kit.tmp}/pm.new {pm} && {commit_cmd(kit, PMAP)}")
    head = kit.head()
    rc, res, _ = kit.run("run", "ACT-R8B", msha, env=env)
    assert res["gate"] == "G8" and res["left"] == [f"repo:{PMAP}"] and res["restored_files"] == [], res
    assert pm.read_text() == new                                         # the tightening stays in force
    log = sh("git", "log", "--format=%s", f"{head}..HEAD", cwd=kit.repo).stdout.decode()
    assert "concurrent: someone else" in log
    assert sh("git", "status", "--porcelain", cwd=kit.repo).stdout.decode().strip() == ""
    assert locked(kit) and PMAP in p1s(kit)[-1]["text"]
    # S22's form: the lock refuses the next run and the next launch, and neither changes the file
    m2 = kit.bundle("ACT-R8B2", {("repo", "data/plain.txt"): None})
    assert kit.run("run", "ACT-R8B2", m2)[1]["gate"] == "lock"
    write(kit.root / "queue/two.req", f"ACT-R8B2 {m2}\n")
    assert kit.launch()[1]["gate"] == "lock"
    assert pm.read_text() == new and (kit.repo / "data/plain.txt").exists()


def test_g8_a_new_skill_file_committed_meanwhile_is_left(kit):
    skill = ".claude/skills/new/SKILL.md"
    msha = kit.bundle("ACT-R8C", removal())
    env = hooked(kit, "in-G8", f"mkdir -p {kit.repo}/.claude/skills/new && echo skill > {kit.repo}/{skill} && "
                               f"{commit_cmd(kit, skill)}")
    rc, res, _ = kit.run("run", "ACT-R8C", msha, env=env)
    assert res["gate"] == "G8" and res["left"] == [f"repo:{skill}"], res
    assert (kit.repo / skill).read_text() == "skill\n"
    assert locked(kit) and skill in p1s(kit)[-1]["text"]


def test_g8_a_touched_file_at_third_bytes_is_left(kit):
    msha = kit.bundle("ACT-R8D", removal())
    env = hooked(kit, "in-G8", f"echo someone >> {kit.repo}/{OPTIN}")
    rc, res, _ = kit.run("run", "ACT-R8D", msha, env=env)
    assert res["gate"] == "G8" and res["left"] == [f"repo:{OPTIN}"], res
    assert (kit.repo / OPTIN).read_bytes() == ORIG + b"someone\n"
    assert locked(kit) and OPTIN in p1s(kit)[-1]["text"]


def test_g8_both_at_once_its_own_restored_the_rest_left(kit):
    msha = kit.bundle("ACT-R8E", removal())
    env = hooked(kit, "in-G8", f"cp {kit.scratch}/acts/ACT-R8E/after/repo/{OPTIN} {kit.repo}/{OPTIN} && "
                               f"echo '{{}}' > {kit.repo}/.claude/settings.json && {commit_cmd(kit, '.claude/settings.json')}")
    rc, res, _ = kit.run("run", "ACT-R8E", msha, env=env)
    assert res["gate"] == "G8", res
    assert res["restored_files"] == [f"repo:{OPTIN}"] and res["left"] == ["repo:.claude/settings.json"]
    assert (kit.repo / OPTIN).read_bytes() == ORIG
    assert (kit.repo / ".claude/settings.json").read_text() == "{}\n"
    text = p1s(kit)[-1]["text"]
    assert locked(kit) and ".claude/settings.json" in text and "live files changed" in text


def test_the_hook_is_waited_for_its_exit_code_ignored_and_no_git_lock_held(kit):
    rec = kit.tmp / "g8.txt"
    msha = kit.bundle("ACT-R8F", removal())
    env = hooked(kit, "in-G8", f"sleep 1; {{ [ -e {kit.repo}/.git/index.lock ] && echo lock || echo free; }} > {rec}; "
                               "exit 7")
    rc, res, _ = kit.run("run", "ACT-R8F", msha, env=env)
    assert res["result"] == "applied", res
    assert rec.read_text() == "free\n"


# ================================================================ the restore rule in the (a) after-check's undo (S15)
def test_a_concurrent_control_commit_during_the_checks_is_left_and_the_acts_own_file_undone(kit):
    sj = kit.repo / ".claude/settings.json"
    msha = kit.bundle("ACT-R9A", removal())
    env = hooked(kit, "in-apply-checks", f"echo '{{\"x\": 1}}' > {sj} && {commit_cmd(kit, '.claude/settings.json')}")
    rc, res, _ = kit.run("run", "ACT-R9A", msha, env=env)
    assert res["result"] in ("undone", "refused") and res["gate"] == "after-check", res
    assert res["left"] == ["repo:.claude/settings.json"] and res["lock"] is True
    assert sj.read_text() == '{"x": 1}\n'
    assert (kit.repo / OPTIN).read_bytes() == ORIG
    subjects = sh("git", "log", "--format=%s", "-3", cwd=kit.repo).stdout.decode().splitlines()
    assert subjects[0] == "ACT-R9A: undone by the operator" and subjects[1] == "concurrent: someone else"
    files = sh("git", "show", "--name-only", "--format=", "HEAD", cwd=kit.repo).stdout.decode().split()
    assert files == [OPTIN]                                              # the undo commit holds only the ACT's own
    assert locked(kit) and ".claude/settings.json" in p1s(kit)[-1]["text"]


def test_a_control_file_written_but_not_committed_during_the_checks_is_left(kit):
    msha = kit.bundle("ACT-R9B", removal())
    env = hooked(kit, "in-apply-checks", f"echo '# them' >> {kit.repo}/.claude/hooks/pretooluse.py")
    rc, res, _ = kit.run("run", "ACT-R9B", msha, env=env)
    assert res["gate"] == "after-check" and res["left"] == ["repo:.claude/hooks/pretooluse.py"], res
    assert (kit.repo / ".claude/hooks/pretooluse.py").read_text().endswith("# them\n")
    assert (kit.repo / OPTIN).read_bytes() == ORIG and locked(kit)


def test_a_crontab_change_during_the_checks_is_left(kit):
    cron = stateful_crontab(kit)
    msha = kit.bundle("ACT-R9C", removal())
    env = hooked(kit, "in-apply-checks", f"{{ crontab -l; echo '*/5 * * * * them'; }} > {kit.tmp}/c.new && "
                                         f"crontab {kit.tmp}/c.new")
    rc, res, _ = kit.run("run", "ACT-R9C", msha, env=env)
    assert res["gate"] == "after-check" and res["left"] == ["crontab:crontab"], res
    assert cron.read_text() == "0 5 * * * true\n*/5 * * * * them\n"
    assert (kit.repo / OPTIN).read_bytes() == ORIG
    assert locked(kit) and "crontab" in p1s(kit)[-1]["text"]


def test_the_acts_touched_file_at_third_bytes_in_the_undo_is_left_too(kit):
    msha = kit.bundle("ACT-R9D", removal())
    env = hooked(kit, "in-apply-checks", f"echo them >> {kit.repo}/{OPTIN} && echo '{{}}' > {kit.repo}/.claude/settings.json")
    rc, res, _ = kit.run("run", "ACT-R9D", msha, env=env)
    assert res["gate"] == "after-check", res
    assert res["left"] == ["repo:.claude/settings.json", f"repo:{OPTIN}"]
    assert (kit.repo / OPTIN).read_bytes() == AFTER + b"them\n"         # not written over by apply.sh undo
    assert locked(kit)


def test_the_in_apply_checks_point_runs_for_a_b_act_too(kit):
    rec = kit.tmp / "b.txt"
    ch = {("repo", OPTIN): ORIG + b"four\n"}
    msha = kit.bundle("ACT-R9E", ch, claimed="b")
    kit.say(f"yes ACT-R9E {msha[:8]}", f"{DAY}T11:00:00+00:00")
    env = hooked(kit, "in-apply-checks", f"git -C {kit.repo} log -1 --format=%s > {rec}")
    rc, res, _ = kit.run("run", "ACT-R9E", msha, env=env)
    assert res["result"] == "applied", res
    assert rec.read_text().startswith("ACT-R9E: applied by the operator agent")


def test_a_clean_a_act_with_no_concurrent_change_is_applied_without_the_lock(kit):
    msha = kit.bundle("ACT-R9F", removal())
    rc, res, _ = kit.run("run", "ACT-R9F", msha, env=hooked(kit, "in-apply-checks", "true"))
    assert res["result"] == "applied" and not locked(kit), res
