"""ACT-OPERATOR-1's code parts (the CTO's, reviewed with the ACT): F26 and the commit freeze in the commit path.

- F26 (W2-148 review r3): Claude Code's own `.claude/scheduled_tasks.lock` is not a control file; every other file
  under `.claude/**`, `.claude/settings.local.json` included, still is.
- freeze_gate.py (DEC-1106 (3), DEC-1028 (6)): run by the reference-transaction hook in the `prepared` state while
  the operator's freeze exists, it refuses an update of the live branch that touches the ACT's repository paths or
  the operator's control paths unless its commits carry the operator's own Act:/Act-sha: trailers; every other
  update goes on.

Planted folders only (tmp_path): a repository with its own hook, a planted operator root, a crontab stub.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
OPDIR = REPO / "governance" / "project" / "operator"
GATE = OPDIR / "freeze_gate.py"
ACT = "ACT-PLANTED-1"
SHA = "ab" * 32


def git(repo, *args, env=None, check=True):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    e.update(env or {})
    r = subprocess.run(["git", "-C", str(repo)] + list(args), capture_output=True, env=e)
    if check and r.returncode != 0:
        raise AssertionError(f"git {args}: {r.stderr.decode()}")
    return r


# ----------------------------------------------------------------------------------------------------------- F26
def test_f26_the_scheduled_tasks_lock_is_not_a_control_file_and_the_rest_of_dot_claude_is(tmp_path, monkeypatch):
    sys.path.insert(0, str(OPDIR))
    try:
        import operator_run
    finally:
        sys.path.remove(str(OPDIR))
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    for rel, data in ((".claude/scheduled_tasks.lock", '{"sessionId":"x","pid":1}'),
                      (".claude/settings.local.json", '{"permissions":{"allow":[]}}'),
                      (".claude/settings.json", "{}"), (".claude/hooks/pretooluse.py", "# hook\n"),
                      (".claude/skills/x/scheduled_tasks.lock", "a nested file of the same name\n")):
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(data)
    bindir = tmp_path / "bin"
    bindir.mkdir()
    (bindir / "crontab").write_text("#!/bin/sh\nexit 1\n")
    (bindir / "crontab").chmod(0o755)
    env = {"PATH": f"{bindir}:/usr/bin:/bin", "HOME": str(tmp_path)}
    s = {"repo": str(repo), "home": str(tmp_path), "install": str(tmp_path / "install"),
         "freeze": str(tmp_path / "install" / "act-in-progress.txt")}
    (tmp_path / "install").mkdir()
    snap = operator_run.control_snapshot(s, env)
    keys = {k[1] for k in snap if k[0] == "repo"}
    assert ".claude/scheduled_tasks.lock" not in keys
    for rel in (".claude/settings.local.json", ".claude/settings.json", ".claude/hooks/pretooluse.py",
                ".claude/skills/x/scheduled_tasks.lock"):
        assert rel in keys, rel
    assert operator_run.CONTROL_RUNTIME_SKIP == frozenset({".claude/scheduled_tasks.lock"})
    # a rewrite of the lock is no difference; a rewrite of settings.local.json is one
    (repo / ".claude/scheduled_tasks.lock").write_text('{"sessionId":"y","pid":2}')
    assert operator_run.control_snapshot(s, env) == snap
    (repo / ".claude/settings.local.json").write_text('{"permissions":{"allow":["Bash(*)"]}}')
    assert operator_run.control_snapshot(s, env) != snap


# --------------------------------------------------------------------------------------------- the commit freeze
@pytest.fixture
def world(tmp_path):
    repo = tmp_path / "repo"
    git(tmp_path, "init", "-q", "-b", "w2/integrate", str(repo))
    for rel in ("README", "src/a.py", "tests/optin-x.txt", ".claude/settings.json", "governance/project/path-map.yaml"):
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"{rel}\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    git(repo, "branch", "ticket")
    root = tmp_path / "op"
    freeze = root / "install" / "act-in-progress.txt"
    (root / "install").mkdir(parents=True)
    bundle = root / "acts" / f"{ACT}-{SHA[:12]}"
    bundle.mkdir(parents=True)
    (bundle / "manifest.json").write_text(json.dumps({"act": ACT, "touched": [
        {"root": "repo", "path": "tests/optin-x.txt", "before": "0" * 64, "after": "1" * 64},
        {"root": "home", "path": ".cache/gov-os/x", "before": None, "after": "1" * 64}]}))
    hook = repo / ".git" / "hooks" / "reference-transaction"
    hook.write_text("#!/bin/sh\n"
                    'if [ "$1" = prepared ]; then\n'
                    f"  f={freeze}\n"
                    '  { [ -e "$f" ] || [ -L "$f" ]; } || exit 0\n'
                    f'  exec env -u PYTHONPATH /usr/bin/python3 -I {GATE} "$f"\n'
                    "fi\nexit 0\n")
    hook.chmod(0o755)
    return {"repo": repo, "root": root, "freeze": freeze, "bundle": bundle, "tmp": tmp_path}


def commit(repo, rel, trailers=()):
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a") as f:
        f.write("more\n")
    git(repo, "add", "--", rel)
    args = ["commit", "-q", "-m", f"change {rel}"]
    if trailers:
        args += ["-m", "\n".join(trailers)]
    return git(repo, *args, check=False)


def plant_freeze(w, act=ACT, sha=SHA):
    w["freeze"].write_text(f"{act} {sha} 2026-11-09T18:00:00+00:00 operator 1-x\n")


def head(repo):
    return git(repo, "rev-parse", "HEAD").stdout.decode().strip()


def test_no_freeze_every_commit_goes_on(world):
    r = commit(world["repo"], "tests/optin-x.txt")
    assert r.returncode == 0, r.stderr


def test_the_acts_path_is_refused_while_the_freeze_holds_and_the_branch_stays(world):
    plant_freeze(world)
    before = head(world["repo"])
    r = commit(world["repo"], "tests/optin-x.txt", ("Task: DAEO-sdxk", "Role: orchestrator"))
    assert r.returncode != 0
    assert b"commit freeze" in r.stderr and b"tests/optin-x.txt" in r.stderr
    assert head(world["repo"]) == before


@pytest.mark.parametrize("rel", [".claude/settings.json", ".claude/skills/new/SKILL.md",
                                 "governance/project/path-map.yaml", ".rulesync/permissions.jsonc"])
def test_a_control_path_is_refused_while_the_freeze_holds(world, rel):
    plant_freeze(world)
    r = commit(world["repo"], rel)
    assert r.returncode != 0 and b"commit freeze" in r.stderr


def test_another_path_goes_on_while_the_freeze_holds(world):
    plant_freeze(world)
    r = commit(world["repo"], "src/a.py", ("Task: DAEO-sdxk", "Role: orchestrator"))
    assert r.returncode == 0, r.stderr


def test_the_operators_own_commit_and_undo_go_on(world):
    plant_freeze(world)
    r = commit(world["repo"], "tests/optin-x.txt", ("Role: operator", f"Act: {ACT}", f"Act-sha: {SHA}", "Class: a"))
    assert r.returncode == 0, r.stderr
    r = commit(world["repo"], "tests/optin-x.txt", ("Role: operator", f"Act: {ACT}", f"Act-sha: {SHA}", "Undo: yes"))
    assert r.returncode == 0, r.stderr


def test_another_acts_trailers_do_not_pass(world):
    plant_freeze(world)
    r = commit(world["repo"], "tests/optin-x.txt", ("Role: operator", "Act: ACT-OTHER-1", f"Act-sha: {SHA}"))
    assert r.returncode != 0
    r = commit(world["repo"], "tests/optin-x.txt", ("Role: operator", f"Act: {ACT}", "Act-sha: " + "cd" * 32))
    assert r.returncode != 0


def test_a_merge_landing_the_acts_path_is_refused_and_a_rewind_too(world):
    repo = world["repo"]
    git(repo, "checkout", "-q", "ticket")
    assert commit(repo, "tests/optin-x.txt", ("Task: DAEO-ab12",)).returncode == 0
    git(repo, "checkout", "-q", "w2/integrate")
    assert commit(repo, "src/a.py").returncode == 0
    plant_freeze(world)
    r = git(repo, "merge", "-q", "--no-ff", "-m", "merge ticket", "ticket", check=False)
    assert r.returncode != 0 and b"commit freeze" in r.stderr
    git(repo, "merge", "--abort", check=False)
    world["freeze"].unlink()
    assert commit(repo, ".claude/settings.json").returncode == 0
    plant_freeze(world)
    r = git(repo, "reset", "-q", "--soft", "HEAD~1", check=False)
    assert r.returncode != 0 and b"back over" in r.stderr


def test_another_branch_is_never_judged(world):
    plant_freeze(world)
    wt = world["tmp"] / "wt"
    git(world["repo"], "worktree", "add", "-q", str(wt), "ticket")
    r = commit(wt, "tests/optin-x.txt")
    assert r.returncode == 0, r.stderr


def test_an_unreadable_manifest_freezes_every_path(world):
    plant_freeze(world)
    (world["bundle"] / "manifest.json").write_text("not json")
    r = commit(world["repo"], "src/a.py")
    assert r.returncode != 0 and b"manifest cannot be read" in r.stderr


def test_a_malformed_freeze_freezes_every_path(world):
    world["freeze"].write_text("garbage\n")
    r = commit(world["repo"], "src/a.py")
    assert r.returncode != 0 and b"commit freeze" in r.stderr


def test_pack_refs_and_gc_go_on_while_the_freeze_holds(world):
    """Review F3: git reports old as zeros for pack-refs and gc; the ref's own value is the old one."""
    plant_freeze(world)
    r = git(world["repo"], "pack-refs", "--all", check=False)
    assert r.returncode == 0, r.stderr
    r = git(world["repo"], "gc", "-q", "--prune=now", check=False)
    assert r.returncode == 0, r.stderr


def test_update_ref_without_an_old_value_is_judged_on_its_change(world):
    repo = world["repo"]
    git(repo, "checkout", "-q", "ticket")
    assert commit(repo, "tests/optin-x.txt").returncode == 0
    frozen = head(repo)
    git(repo, "checkout", "-q", "-b", "side", "w2/integrate")
    assert commit(repo, "src/a.py").returncode == 0
    free = head(repo)
    git(repo, "checkout", "-q", "w2/integrate")
    plant_freeze(world)
    r = git(repo, "update-ref", "refs/heads/w2/integrate", frozen, check=False)
    assert r.returncode != 0 and b"commit freeze" in r.stderr
    r = git(repo, "update-ref", "refs/heads/w2/integrate", free, check=False)
    assert r.returncode == 0, r.stderr


def test_a_detached_main_tree_judges_only_the_live_branch_by_name(world):
    """Review F4: with no symbolic HEAD the gate judges refs/heads/w2/integrate, never every ref."""
    repo = world["repo"]
    git(repo, "checkout", "-q", "--detach")
    plant_freeze(world)
    wt = world["tmp"] / "wt2"
    git(repo, "worktree", "add", "-q", str(wt), "ticket")
    assert commit(wt, "tests/optin-x.txt").returncode == 0
    r = git(repo, "update-ref", "refs/heads/w2/integrate", head(wt), check=False)
    assert r.returncode != 0 and b"commit freeze" in r.stderr


def test_the_merge_queue_does_not_advance_while_the_freeze_holds(tmp_path, monkeypatch):
    """DEC-1106 (3): the CTO's landing tool reads the freeze before it moves the main tree (review F5)."""
    freeze = tmp_path / "act-in-progress.txt"
    monkeypatch.setenv("MERGE_QUEUE_OPERATOR_FREEZE", str(freeze))
    tools = REPO / "governance" / "project" / "orchestration" / "tools"
    sys.path.insert(0, str(tools))
    try:
        import importlib
        import merge_queue
        mq = importlib.reload(merge_queue)
    finally:
        sys.path.remove(str(tools))
    freeze.write_text(f"{ACT} {SHA} t operator 1-x\n")
    with pytest.raises(mq.Stop, match="commit freeze"):
        mq.Queue.advance(object(), "h" * 40, "r" * 40)
    freeze.unlink()
    with pytest.raises(AttributeError):        # past the freeze check: it goes on to the landing itself
        mq.Queue.advance(object(), "h" * 40, "r" * 40)
