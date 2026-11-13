"""W2-148 F21 (DEC-1107), the engineer's unit tests: the owner's undo step and the journal's recovery say "refused" and
exit non-zero whenever they leave a file untouched that is not the ACT's own (a file someone else changed, or a touched
file at third bytes); the ACT's own touched files are undone all the same, a P1 names each file left and the lock is
held. With nothing left both still say "undone". Everything on planted folders (test_w2_148_kit)."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_w2_148_kit import DAY, Kit, sh, write  # noqa: E402

ORIG = b"one\ntwo\nthree\n"
AFTER = b"one\nthree\n"
OPTIN = "tests/optin-x.txt"
PLAIN = "data/plain.txt"
OPTIN2 = "tests/optin-y.txt"
OPT2 = b"a\nb\n"
OPT2_AFTER = b"a\n"
THIRD = b"someone else's\n"
HOOK = ".claude/hooks/pretooluse.py"
# the frozen apply.sh's undo, live only (the dry run's clone has no .live-marker), also writes a control file the ACT
# does not list: to the agent that is someone else's change made during the undo
UNDO_WRITES_HOOK = f'[ "$step" = undo ] && [ -e "$PWD/.live-marker" ] && echo "# them" >> "$PWD/{HOOK}"'
DIE_IN_APPLY = '[ "$step" = apply ] && [ -e "$PWD/.live-marker" ] && kill -9 $PPID'


def p1s(kit):
    return [n for n in kit.notices() if n["priority"] == "P1"]


def locked(kit):
    return (kit.root / "log/operator.lock").exists()


@pytest.fixture
def kit(tmp_path):
    k = Kit(tmp_path)
    write(k.repo / OPTIN2, OPT2)                                         # a second (a) list file, committed
    sh("git", "add", OPTIN2, cwd=k.repo)
    sh("git", "commit", "-q", "-m", "a second opt-in list", cwd=k.repo)
    return k


def two_files():
    return {("repo", OPTIN): AFTER, ("repo", OPTIN2): OPT2_AFTER}


def applied_and_said(kit, act, changes, **kw):
    msha = kit.bundle(act, changes, **kw)
    rc, res, _ = kit.run("run", act, msha)
    assert res["result"] == "applied", res
    kit.say(f"undo {act} {msha[:8]}", f"{DAY}T11:30:00+00:00")
    kit.set_clock(f"{DAY}T13:00:00+01:00")
    return msha


def no_undone_anywhere(stdout):
    """No JSON object on stdout, nested ones included, carries result "undone"."""
    def walk(o):
        if isinstance(o, dict):
            if o.get("result") == "undone":
                return False
            return all(walk(v) for v in o.values())
        if isinstance(o, list):
            return all(walk(v) for v in o)
        return True
    objs = []
    for line in stdout.decode().splitlines():
        try:
            objs.append(json.loads(line))
        except ValueError:
            continue
    assert objs
    return all(walk(o) for o in objs)


def dead_session(kit, act, changes, extra=""):
    msha = kit.bundle(act, changes, extra_apply=DIE_IN_APPLY + ("\n" + extra if extra else ""))
    p = subprocess.run([sys.executable, str(kit.install / "operator_run.py"), "--config", str(kit.config), "run",
                        act, msha], capture_output=True, env=kit.env(), timeout=120)
    assert p.returncode != 0 and (kit.root / "log/journal.json").exists()
    return msha


# ================================================================================================ the owner's undo
def test_the_owners_undo_leaving_a_foreign_file_says_refused_and_exits_non_zero(kit):
    hook_before = (kit.repo / HOOK).read_bytes()
    msha = applied_and_said(kit, "ACT-F1", {("repo", OPTIN): AFTER}, extra_apply=UNDO_WRITES_HOOK)
    rc, res, r = kit.run("undo", "ACT-F1", msha)
    assert rc != 0 and res["result"] == "refused" and res["gate"] == "undo", res
    assert no_undone_anywhere(r.stdout)
    assert res["undo"] == "done" and res["left"] == [f"repo:{HOOK}"] and res["lock"] is True
    assert (kit.repo / OPTIN).read_bytes() == ORIG                       # the ACT's own file undone
    assert (kit.repo / HOOK).read_bytes() == hook_before + b"# them\n"   # left exactly as written
    assert locked(kit) and HOOK in p1s(kit)[-1]["text"] and "refused" in p1s(kit)[-1]["text"]
    line = [e for e in kit.log() if e["gate"] == "undo"][-1]
    assert line["result"] == "refused" and line["undo"] == "done" and line["left"] == [f"repo:{HOOK}"]
    m2 = kit.bundle("ACT-F1B", {("repo", PLAIN): None})                 # the lock refuses the next run
    assert kit.run("run", "ACT-F1B", m2)[1]["gate"] == "lock"


def test_the_owners_undo_with_a_touched_file_at_third_bytes_undoes_its_own_and_says_refused(kit):
    msha = applied_and_said(kit, "ACT-F2", two_files())
    applied_head = kit.head()
    write(kit.repo / OPTIN2, THIRD)                                     # third bytes: neither before nor after
    rc, res, r = kit.run("undo", "ACT-F2", msha)
    assert rc != 0 and res["result"] == "refused" and res["gate"] == "undo", res
    assert no_undone_anywhere(r.stdout)
    assert res["left"] == [f"repo:{OPTIN2}"] and res["lock"] is True and res["undo"] == "done"
    assert (kit.repo / OPTIN).read_bytes() == ORIG                       # its own, at the after-copy: undone
    assert (kit.repo / OPTIN2).read_bytes() == THIRD                     # left exactly as written
    files = sh("git", "show", "--name-only", "--format=", "HEAD", cwd=kit.repo).stdout.decode().split()
    assert kit.head() != applied_head and files == [OPTIN]              # the undo commit holds only its own file
    assert locked(kit) and OPTIN2 in p1s(kit)[-1]["text"]
    assert not (kit.root / "log/journal.json").exists()


def test_the_owners_undo_after_the_lock_is_cleared_is_already_undone(kit):
    msha = applied_and_said(kit, "ACT-F3", two_files())
    write(kit.repo / OPTIN2, THIRD)
    assert kit.run("undo", "ACT-F3", msha)[1]["result"] == "refused"
    (kit.root / "log/operator.lock").unlink()                           # the owner clears the lock
    rc, res, _ = kit.run("undo", "ACT-F3", msha)
    assert rc != 0 and res["result"] == "refused" and res["reason"] == "already undone", res
    assert (kit.repo / OPTIN2).read_bytes() == THIRD


def test_the_owners_undo_with_nothing_left_still_says_undone_with_exit_0(kit):
    msha = applied_and_said(kit, "ACT-F4", two_files())
    rc, res, _ = kit.run("undo", "ACT-F4", msha)
    assert rc == 0 and res["result"] == "undone" and res["left"] == [] and res["lock"] is False, res
    assert (kit.repo / OPTIN).read_bytes() == ORIG and (kit.repo / OPTIN2).read_bytes() == OPT2
    assert not locked(kit)


def test_the_owners_undo_after_the_next_act_on_the_same_files_stays_a_plain_refusal(kit):
    msha = applied_and_said(kit, "ACT-F5", {("repo", OPTIN): AFTER})
    m2 = kit.bundle("ACT-F5B", {("repo", OPTIN): b"three\n"})
    assert kit.run("run", "ACT-F5B", m2)[1]["result"] == "applied"
    rc, res, _ = kit.run("undo", "ACT-F5", msha)
    assert rc != 0 and res["result"] == "refused" and "later ACT" in res["reason"], res
    assert (kit.repo / OPTIN).read_bytes() == b"three\n" and not locked(kit)


def test_the_owners_undo_with_a_touched_file_back_at_its_before_copy_refuses_up_front(kit):
    msha = applied_and_said(kit, "ACT-F6", two_files())
    write(kit.repo / OPTIN2, OPT2)                                      # back at its before-copy, no third bytes
    rc, res, _ = kit.run("undo", "ACT-F6", msha)
    assert rc != 0 and res["result"] == "refused" and "moved since the apply" in res["reason"], res
    assert (kit.repo / OPTIN).read_bytes() == AFTER and not locked(kit)  # nothing written


# ================================================================================================ the recovery
def test_the_recovery_leaving_a_touched_file_at_third_bytes_says_refused_on_the_launchers_stdout(kit):
    dead_session(kit, "ACT-J2", two_files())
    write(kit.repo / OPTIN2, THIRD)
    rc, res, r = kit.launch()
    assert rc != 0 and res["result"] == "refused" and res["gate"] == "journal", res
    assert no_undone_anywhere(r.stdout)
    assert res["left"] == [f"repo:{OPTIN2}"] and res["lock"] is True and res["undo"] == "done"
    assert (kit.repo / OPTIN).read_bytes() == ORIG
    assert (kit.repo / OPTIN2).read_bytes() == THIRD
    assert locked(kit) and any(n["kind"] == "recovered" and OPTIN2 in n["text"] for n in p1s(kit))
    line = [e for e in kit.log() if e["gate"] == "journal"][-1]
    assert line["result"] == "refused" and line["undo"] == "done"


def test_the_recovery_leaving_a_foreign_file_says_refused_through_the_recover_step(kit):
    hook_before = (kit.repo / HOOK).read_bytes()
    dead_session(kit, "ACT-J3", {("repo", OPTIN): AFTER}, extra=UNDO_WRITES_HOOK)
    rc, res, r = kit.run("recover")
    assert rc != 0 and res["result"] == "refused" and res["left"] == [f"repo:{HOOK}"], res
    assert no_undone_anywhere(r.stdout)
    assert (kit.repo / OPTIN).read_bytes() == ORIG
    assert (kit.repo / HOOK).read_bytes() == hook_before + b"# them\n"
    assert locked(kit) and HOOK in p1s(kit)[-1]["text"]


def test_the_recovery_with_nothing_left_still_says_undone(kit):
    dead_session(kit, "ACT-J4", two_files())
    rc, res, _ = kit.launch()
    assert rc == 0 and res["result"] == "recovered" and res["recovered"]["result"] == "undone", res
    assert res["recovered"]["left"] == [] and res["recovered"]["lock"] is False
    assert (kit.repo / OPTIN).read_bytes() == ORIG and not locked(kit)
