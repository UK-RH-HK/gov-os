"""W2-148, DEC-1106 (1) and (3).

(1) F15, the restore rule: after the G8 dry run (S12) the agent re-hashes the live touched files and the control files;
it restores only its own dry-run change (a touched file whose live bytes equal the frozen after-copy); any other live
difference is left exactly as written, the run refused, the lock held and a P1 pushed naming each file. The same rule
in the (a) after-check's undo (S15): the ACT's own touched files undone, any other difference left as written, the lock
held, a P1 naming each file. The concurrent changes are made by the test hook at the points ``in-G8`` and
``in-apply-checks`` (README), never by a race.

(3) The commit freeze is ``<operator root>/install/act-in-progress.txt`` (S14): never counted by the APPROVED check; a
stale one holds G9 (S13) and never refuses the run.
"""

from __future__ import annotations

import subprocess

import pytest

import w2_148_support as support
from w2_148_support import last_json, wait_for

OPTIN = "tests/optin-lifted.txt"
PATH_MAP = "governance/project/path-map.yaml"
SKILL = ".claude/skills/planted-new/SKILL.md"
HOOK = "GOV_OPERATOR_TEST_HOOK"


def clean(w) -> str:
    """The live tree against its HEAD: empty when clean (the live marker is excluded)."""
    return w.git("status", "--porcelain", "--untracked-files=all")


def refused_at_g8(w, r):
    assert r.out.get("result") == "refused", (r.out, r.stderr[-3000:])
    assert r.code != 0
    assert r.out.get("gate") == "G8", r.out
    assert r.out.get("approved_sha256") == w.approved_sha()
    assert w.forbidden_calls() == ""


# --- S12, F15: a concurrent change in the live repository during the dry run ----------------------------------------

def concurrent_g8(w, case):
    """(repo-relative path, the bytes the CTO's concurrent commit writes there)."""
    if case == "control-file-path-map":
        text = w.read("repo", PATH_MAP).decode()
        old = '"transcripts/**"]'
        assert old in text
        return PATH_MAP, text.replace(old, '"transcripts/**", "fixtures/evaluation/cto-set/hidden/**"]').encode()
    if case == "new-file-under-claude-skills":
        return SKILL, b"---\nname: planted-new\ndescription: a skill the CTO's commit adds (planted)\n---\n# planted\n"
    if case == "touched-file-neither-before-nor-after":
        return OPTIN, w.read("repo", OPTIN) + b"tests/acceptance/W1-54/test_cto.py  # the CTO's own line (planted)\n"
    raise ValueError(case)


@pytest.mark.parametrize("case", ["control-file-path-map", "new-file-under-claude-skills",
                                  "touched-file-neither-before-nor-after"])
def test_s12_f15_a_concurrent_commit_during_the_dry_run_is_left_untouched_refused_and_held(world, tmp_path, case):
    b = world.ready("ACT-T-F15", [world.optin_removal()])
    base = world.head()
    path, data = concurrent_g8(world, case)
    hook = support.concurrent_hook(world, tmp_path / "hook.py", "in-G8", [
        ("write", world.repo / path, data), ("commit", [path], f"the CTO's concurrent commit ({case}, planted)")])
    r = world.run(b, env_extra={HOOK: hook})
    assert support.hook_ran(world, "in-G8"), ("the run never called the test hook at in-G8", r.out, r.stderr[-3000:])
    cto = support.hook_head(world)
    refused_at_g8(world, r)
    assert world.read("repo", path) == data, f"{path}: the concurrent change was not left as the commit wrote it"
    assert world.head() == cto and world.git("rev-parse", "HEAD~1").strip() == base, "HEAD is not the CTO's commit"
    assert clean(world) == "", "the live tree is not clean against its new HEAD"
    if path != OPTIN:
        support.assert_touched(world, b, "before")
    missing = support.p1_missing(world, b.act, path)
    assert not missing, ("no P1 names each file left changed", missing, world.p1s(b.act))
    support.assert_lock_held(world)
    assert world.read("repo", path) == data and world.head() == cto and clean(world) == "", \
        "the next launch changed the concurrent change"


def test_s12_f15_the_dry_run_s_own_change_reaching_the_live_tree_is_restored_and_refused(world, tmp_path):
    """A script writing the live tree during the dry run despite the path rule, simulated by the hook: the live touched
    file made equal to the frozen after-copy. That is the agent's own change: restored to its before bytes."""
    b = world.ready("ACT-T-F15O", [world.optin_removal()])
    snap = world.snapshot()
    after = (b.dir / "after" / "repo" / OPTIN).read_bytes()
    hook = support.concurrent_hook(world, tmp_path / "hook.py", "in-G8", [("write", world.repo / OPTIN, after)])
    r = world.run(b, env_extra={HOOK: hook})
    assert support.hook_ran(world, "in-G8"), ("the run never called the test hook at in-G8", r.out, r.stderr[-3000:])
    refused_at_g8(world, r)
    support.assert_touched(world, b, "before")
    assert world.snapshot() == snap, "the live state is not back at its pre-dry-run bytes"
    missing = support.p1_missing(world, b.act, OPTIN, phrase="live files changed")
    assert not missing, ("the P1 does not say live files changed, naming the file", missing, world.p1s(b.act))


def test_s12_f15_with_its_own_change_and_a_concurrent_one_it_restores_only_its_own(world, tmp_path):
    """Both at once: the touched file at the after-copy (its own) and the pin re-written in HOME (not its own)."""
    b = world.ready("ACT-T-F15M", [world.optin_removal()])
    pin = world.home / ".local/bin/gov"
    pin_new = b"#!/bin/sh\necho 'the pinned gov, re-pinned by the owner (planted)'\n"
    after = (b.dir / "after" / "repo" / OPTIN).read_bytes()
    hook = support.concurrent_hook(world, tmp_path / "hook.py", "in-G8", [
        ("write", world.repo / OPTIN, after), ("write", pin, pin_new)])
    r = world.run(b, env_extra={HOOK: hook})
    assert support.hook_ran(world, "in-G8"), ("the run never called the test hook at in-G8", r.out, r.stderr[-3000:])
    refused_at_g8(world, r)
    support.assert_touched(world, b, "before")
    assert pin.read_bytes() == pin_new, "the pin re-written during the dry run was not left as written"
    assert clean(world) == ""
    missing = support.p1_missing(world, b.act, ".local/bin/gov")
    assert not missing, ("no P1 names the pin", missing, world.p1s(b.act))
    support.assert_lock_held(world)
    assert pin.read_bytes() == pin_new, "the next launch changed the pin"


# --- S15, F15: a concurrent change to an unlisted control file during the (a) apply's checks -------------------------

UNDO_CASES = {
    "hook-file-written": ("repo", ".claude/hooks/pretooluse.py", False),
    "claude-file-committed": ("repo", ".claude/agents/engineer.md", True),
    "crontab": ("crontab", "crontab", False),
}


@pytest.mark.parametrize("case", list(UNDO_CASES))
def test_s15_f15_a_concurrent_control_change_during_the_apply_is_left_as_written_and_the_act_undone(world, tmp_path,
                                                                                                    case):
    root, path, commit = UNDO_CASES[case]
    b = world.ready("ACT-T-F15A", [world.optin_removal()])
    target = world.crontab_store if root == "crontab" else world.repo / path
    data = target.read_bytes() + (b"*/5 * * * * /bin/true # the CTO's line (planted)\n" if root == "crontab"
                                  else b"# the CTO's concurrent change (planted)\n")
    actions = [("write", target, data)]
    if commit:
        actions.append(("commit", [path], f"the CTO's concurrent commit ({case}, planted)"))
    hook = support.concurrent_hook(world, tmp_path / "hook.py", "in-apply-checks", actions)
    r = world.run(b, env_extra={HOOK: hook})
    assert support.hook_ran(world, "in-apply-checks"), ("the run never called the test hook at in-apply-checks",
                                                        r.out, r.stderr[-3000:])
    assert r.out.get("result") in ("undone", "refused"), (r.out, r.stderr[-3000:])
    assert target.read_bytes() == data, f"{path}: the concurrent change was not left exactly as written"
    if commit:
        cto = support.hook_head(world)
        anc = subprocess.run(["git", "merge-base", "--is-ancestor", cto, "HEAD"], cwd=world.repo, env=world.env())
        assert anc.returncode == 0, "the CTO's concurrent commit is no longer in HEAD's history"
    support.assert_touched(world, b, "before")
    missing = support.p1_missing(world, b.act, path)
    assert not missing, ("no P1 names the control file left changed", missing, world.p1s(b.act))
    support.assert_lock_held(world)
    assert target.read_bytes() == data, "the next launch changed the concurrent change"


# --- S14, S13: the commit freeze in the install folder (DEC-1106 (3)) ----------------------------------------------

def test_s14_a_stale_freeze_in_the_install_holds_g9_and_never_refuses_on_approved(world):
    freeze = world.install / "act-in-progress.txt"
    b = world.ready("ACT-T-FZ", [world.optin_removal()])
    freeze.write_text("ACT-T-OLD a stale freeze (planted)\n")
    approved = world.approved_sha()
    proc = world.start(b)
    try:
        held = wait_for(lambda: proc.poll() is not None or any(
            line.get("gate") == "G9" and line.get("result") == "held" for line in world.gate_lines(b.act)), 90)
        assert proc.poll() is None, f"the run ended with a stale freeze in install/ (refused on APPROVED?): " \
                                    f"{proc.communicate()}"
        assert held, "no G9 held line for a stale freeze in install/"
        assert freeze.exists(), "the run removed a freeze it did not write"
        support.assert_touched(world, b, "before")
        freeze.unlink()
        out, err = proc.communicate(timeout=120)
    finally:
        world.stop(proc)
    assert proc.returncode == 0, err[-3000:]
    res = last_json(out)
    assert res.get("result") == "applied", res
    assert res.get("approved_sha256") == approved and world.approved_sha() == approved
    support.assert_touched(world, b, "after")
    assert not freeze.exists(), "the run's own freeze was left in install/"
