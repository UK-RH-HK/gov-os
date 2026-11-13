"""W2-148, the engineer's unit tests: the classifier on the table's rows, the wall hook, the landing check, the pinned
verdict.py and the name-match search."""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_w2_148_kit import OPDIR, Kit, sh, write  # noqa: E402

sys.path.insert(0, str(OPDIR))
import act_class  # noqa: E402


def sha(b):
    return hashlib.sha256(b).hexdigest()


def bundle(tmp, files, commands=(), apply_sh="#!/bin/bash\nexit 0\n"):
    """files: {(root, path): (before bytes or None, after bytes or None)} -> the classifier's result."""
    touched = []
    for (root, path), (b, a) in files.items():
        if b is not None:
            write(tmp / "before" / root / path, b)
        if a is not None:
            write(tmp / "after" / root / path, a)
        touched.append({"root": root, "path": path, "before": sha(b) if b is not None else None,
                        "after": sha(a) if a is not None else None})
    write(tmp / "apply.sh", apply_sh)
    write(tmp / "manifest.json", json.dumps({"touched": touched, "commands": list(commands), "checks": []}))
    r = subprocess.run([sys.executable, str(OPDIR / "act_class.py"), str(tmp)], capture_output=True)
    assert r.returncode == 0
    return json.loads(r.stdout.decode().strip().splitlines()[-1])


PM = b"""version: 1
acceptance_exemptions: []
sets_root_hidden:
  root: "~/gov-os-eval"
  hidden: ["a/**"]
  refused_roles: [engineer]
role_paths:
  engineer:
    reads_denied: ["x"]
evaluation_sets:
  one:
    hidden: ["f/one/**"]
    measures: {roles: [engineer]}
"""
TM = b"""version: 1
shared_core: ["src/a/**"]
record_only: ["docs/**.md"]
record_reading: ["tests/r.py"]
couplings:
  - paths: ["src/a.py"]
    suites: ["tests/a.py"]
    why: "x"
per_test_timeout: 900
distribution: load
"""
SET = json.dumps({"permissions": {"allow": ["Read"], "deny": ["Bash(sudo *)"]}, "hooks": {}}).encode()
RS = b'{\n  // c\n  "permission": {"bash": {"sudo:*": "deny"}, "edit": {}},\n}\n'


@pytest.mark.parametrize("path,before,after,want", [
    ("governance/project/path-map.yaml", PM, PM.replace(b'["a/**"]', b'["a/**", "b/**"]'), "a"),
    ("governance/project/path-map.yaml", PM, PM.replace(b"refused_roles: [engineer]", b"refused_roles: [engineer, research]"), "a"),
    ("governance/project/path-map.yaml", PM, PM.replace(b'reads_denied: ["x"]', b'reads_denied: ["x", "y"]'), "a"),
    ("governance/project/path-map.yaml", PM, PM + b"  two:\n    hidden: [\"f/two/**\"]\n", "a"),
    ("governance/project/path-map.yaml", PM, PM.replace(b'["a/**"]', b"[]"), "b"),
    ("governance/project/path-map.yaml", PM, PM.replace(b"role_paths:", b"role_paths:\n  research:\n    reads_denied: []"), "b"),
    ("governance/project/path-map.yaml", PM, PM.replace(b"acceptance_exemptions: []", b"acceptance_exemptions: [x]"), "O"),
    ("governance/project/path-map.yaml", PM, b"version: [1\n", "b"),
    ("governance/project/test-map.yaml", TM, TM.replace(b'["tests/a.py"]', b'["tests/a.py", "tests/b.py"]'), "a"),
    ("governance/project/test-map.yaml", TM, TM + b"every_close: []\n", "b"),
    ("governance/project/test-map.yaml", TM, TM.replace(b'record_reading: ["tests/r.py"]', b'record_reading: ["tests/r.py", "tests/s.py"]'), "a"),
    ("governance/project/test-map.yaml", TM, TM.replace(b'    why: "x"\n', b'    why: "x"\n  - paths: ["c"]\n    suites: ["d"]\n    why: "y"\n'), "a"),
    ("governance/project/test-map.yaml", TM, TM.replace(b'record_only: ["docs/**.md"]', b'record_only: ["docs/**.md", "x"]'), "b"),
    ("governance/project/test-map.yaml", TM, TM.replace(b"per_test_timeout: 900", b"per_test_timeout: 60"), "b"),
    ("governance/project/test-map.yaml", TM, TM.replace(b'shared_core: ["src/a/**"]', b"shared_core: []"), "b"),
    ("tests/optin-lifted.txt", b"a\nb\nc\n", b"a\nc\n", "a"),
    ("tests/optin-lifted.txt", b"a\nb\nc\n", b"a\nb\nc\nd\n", "b"),
    ("tests/optin-lifted.txt", b"a\nb\nc\n", b"a\nB\nc\n", "b"),
    ("tests/optin-lifted.txt", b"a\n", b"\xff\xfe", "b"),
    (".claude/settings.json", SET, SET.replace(b'"Bash(sudo *)"', b'"Bash(sudo *)", "Bash(git push*)"'), "a"),
    (".claude/settings.json", SET, SET.replace(b'"Read"', b'"Read", "Bash"'), "b"),
    (".claude/settings.local.json", SET, SET.replace(b'"hooks": {}', b'"hooks": {"x": 1}'), "b"),
    (".rulesync/permissions.jsonc", RS, RS.replace(b'"edit": {}', b'"edit": {"x": "deny"}'), "a"),
    (".rulesync/permissions.jsonc", RS, RS.replace(b'"edit": {}', b'"edit": {"x": "allow"}'), "b"),
])
def test_list_shaped_rows(tmp_path, path, before, after, want):
    assert bundle(tmp_path, {("repo", path): (before, after)})["class"] == want


@pytest.mark.parametrize("root,path,want", [
    ("repo", ".claude/hooks/pretooluse.py", "b"), ("repo", ".claude/agents/engineer.md", "b"),
    ("repo", "template/governance/kernel/roles/x.md", "b"), ("repo", ".git/hooks/reference-transaction", "b"),
    ("home", ".gov-os/machine/gate.json", "b"), ("home", ".config/gov-os/x.json", "b"),
    ("home", ".cache/gov-os/x", "a"), ("repo", "governance/project/orchestration/tools/gov_reranker_gpu_slot.py", "a"),
    ("crontab", "crontab", "b"), ("repo", "governance/project/orchestration/tools/deadman.py", "b"),
    ("repo", "governance/project/orchestration/tools/sentinel-brief.md", "b"), ("home", ".local/bin/gov", "O"),
    ("home", ".local/share/x/lib.py", "b"), ("repo", "src/gov/x.py", "O"), ("repo", "docs/DECISION_REGISTER.md", "O"),
    ("repo", ".gov-runtime/scratch/orchestrator/tools/record_checks.sh", "O"), ("home", "gov-os-writer/settings.json", "O"),
    ("repo", "governance/project/operator/class-rules.yaml", "O"), ("home", "gov-os-operator/install/APPROVED", "O"),
    ("home", "somewhere/else", "O"),
])
def test_fixed_rows(tmp_path, root, path, want):
    assert bundle(tmp_path, {(root, path): (b"x\n", b"y\n")})["class"] == want


@pytest.mark.parametrize("cmd,want", [
    ("sudo systemctl restart x", "O"), ("git -C /r push origin main", "O"), ("git tag v1", "O"),
    ("pip install foo", "b"), ("python3 -m pip install foo", "b"), ("curl -s https://example.com/x", "b"),
    ("curl -s http://127.0.0.1:11434/api/version", "a"), ("rm -rf ~/old", "O"), ("rm -f /tmp/x", "a"),
    ("rm -f build/x", "a"), ("powershell.exe -Command x", "O"), ("git reflog expire --all", "O"),
    ("git commit -m 'never a push or a tag' --trailer 'Role: owner'", "a"), ("echo $(sudo id)", "O"),
    ("setsid -f nice -n 10 taskset -c 12-19 ollama serve", "a"), ("bash -c 'git push'", "O"),
])
def test_script_hits_raise_the_class(tmp_path, cmd, want):
    assert bundle(tmp_path, {("home", ".cache/gov-os/x"): (b"x", b"y")}, commands=[cmd])["class"] == want


@pytest.mark.parametrize("cmd,want", [
    ("if true; then sudo systemctl restart x; fi", "O"),
    ("for r in a b; do git push origin $r; done", "O"),
    ("{ git tag v1; }", "O"),
    ("if [ -d ~/x ]; then rm -rf ~/x; fi", "O"),
    ("for u in a; do curl -s https://example.com/$u; done", "b"),
    ("if ! python3 -c 'import x'; then pip install x; fi", "b"),
    ("! git push", "O"),
    ("if false; then :; else git push; fi", "O"),
    ("if a; then b; elif c; then git push; fi", "O"),
    ("while true; do git push; break; done", "O"),
    ("until git push; do sleep 1; done", "O"),
    ("( git tag v2 )", "O"),
    ("for r in a b\ndo\n  git push origin $r\ndone", "O"),
    ("f() {\n  git push\n}\nf", "O"),
    ("function g { sudo true; }", "O"),
    ("bash <<'EOF'\ngit push origin main\nEOF", "O"),
    ("case $x in\n  y) git tag v3 ;;\nesac", "O"),
    ("for u in a b; do curl -s http://127.0.0.1:11434/api/$u; done", "a"),
    ("if true; then echo do then else; fi", "a"),
])
def test_reserved_words_are_stepped_over(tmp_path, cmd, want):
    """F1: a command after a shell reserved word gives its hit, in commands and in apply.sh."""
    assert bundle(tmp_path / "c", {("home", ".cache/gov-os/x"): (b"x", b"y")}, commands=[cmd])["class"] == want
    assert bundle(tmp_path / "s", {("home", ".cache/gov-os/x"): (b"x", b"y")},
                  apply_sh="#!/bin/bash\n" + cmd + "\n")["class"] == want


def test_an_empty_touched_list_with_commands_is_at_least_b(tmp_path):
    """F14: commands with no file trace are never (a)."""
    r = bundle(tmp_path / "c", {}, commands=["curl -s http://127.0.0.1:11434/api/pull -d '{\"name\": \"m\"}'"])
    assert r["class"] == "b" and any(h["kind"] == "commands-only" for h in r["hits"])
    assert bundle(tmp_path / "s", {}, apply_sh="#!/bin/bash\nollama pull m\n")["class"] == "b"
    assert bundle(tmp_path / "n", {})["class"] == "a"                           # nothing at all: nothing governs agents
    assert bundle(tmp_path / "t", {}, apply_sh="#!/bin/bash\nset -eu\ncd \"$(dirname \"$0\")\"\nexit 0\n")["class"] == "a"


def test_a_hit_in_apply_sh_and_the_highest_file_win(tmp_path):
    r = bundle(tmp_path, {("home", ".cache/gov-os/x"): (b"x", b"y"),
                          ("repo", "tests/optin-a.txt"): (b"a\nb\n", b"a\n"),
                          ("crontab", "crontab"): (b"x", b"y")})
    assert r["class"] == "b"
    assert bundle(tmp_path / "s", {("home", ".cache/gov-os/x"): (b"x", b"y")},
                  apply_sh="#!/bin/bash\nsudo true\n")["class"] == "O"


def test_an_unreadable_manifest_is_o(tmp_path):
    write(tmp_path / "manifest.json", "{not json")
    assert act_class.classify(str(tmp_path))["class"] == "O"


def test_a_list_file_not_held_as_hashed_is_never_a(tmp_path):
    r = bundle(tmp_path, {("repo", "tests/optin-a.txt"): (b"a\nb\n", b"a\n")})
    assert r["class"] == "a"
    write(tmp_path / "after/repo/tests/optin-a.txt", b"a\nb\nc\n")
    assert act_class.classify(str(tmp_path))["class"] == "b"


def test_the_pinned_verdict_is_the_ctos_byte_for_byte():
    assert sha((OPDIR / "verdict.py").read_bytes()) == "30214f3de29dacdf9bb443371c05a4392e8da3c305aeb9b7845b9a433d5cf4a5"


def test_no_wait_or_stop_by_a_name_match():
    for f in OPDIR.rglob("*"):
        if f.is_file():
            assert not re.search(r"pkill|killall|pgrep", f.read_text(errors="replace")), f


def test_the_install_imports_no_gov():
    for f in OPDIR.rglob("*.py"):
        assert not re.search(r"^\s*(from|import)\s+gov\b", f.read_text(), re.M), f


# ------------------------------------------------------------------------------------------------------ the wall hook
@pytest.fixture
def wall(tmp_path):
    k = Kit(tmp_path)
    msha = k.bundle("ACT-W1", {("repo", "tests/optin-x.txt"): b"one\n"},
                    checks=[{"cmd": "python3 -c 'print(1)' | tail -1", "exit": 0, "count": 1}])
    write(k.scratch / "log/cto-session.txt", "sess-1\n")
    write(k.root / "queue/a.req", f"ACT-W1 {msha}\n")
    rc, res, r = k.launch()
    assert res["result"] == "launched", res
    settings = json.loads((k.root / "wall/.claude/settings.json").read_text())
    assert settings["permissions"]["deny"]
    cmd = settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
    return k, msha, cmd


def drive(k, cmd, event):
    env = {k2: v for k2, v in os.environ.items() if not k2.startswith("GOV_")}
    env["CLAUDE_PROJECT_DIR"] = str(k.root / "wall")
    r = subprocess.run(["bash", "-c", cmd], input=json.dumps(event).encode() if isinstance(event, dict) else event,
                       capture_output=True, cwd=str(k.root / "wall"), env=env)
    if r.returncode == 2:
        return "deny"
    assert r.returncode == 0, r.stderr
    out = r.stdout.decode().strip()
    dec = json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out else "allow"
    return "deny" if dec == "deny" else "allow"


def test_the_wall_hook_allows_only_the_operators_forms(wall):
    k, msha, cmd = wall
    w = str(k.root / "wall")
    frozen = k.root / "acts" / f"ACT-W1-{msha[:12]}"
    ok = [f"python3 {k.install}/operator_run.py run ACT-W1 {msha}", f"bash {frozen}/apply.sh check",
          f"bash {frozen}/apply.sh undo", "python3 -c 'print(1)' | tail -1", f"git -C {k.repo} add tests/optin-x.txt"]
    for c in ok:
        assert drive(k, cmd, {"tool_name": "Bash", "tool_input": {"command": c}, "cwd": w}) == "allow", c
    assert drive(k, cmd, {"tool_name": "Read", "tool_input": {"file_path": str(k.tx / "sess-1.jsonl")}, "cwd": w}) == "allow"
    bad = ["sudo true", f"git -C {k.repo} push", f"git -C {k.repo} tag v1", f"git -C {k.repo} reset --hard HEAD~1",
           "rm -rf /tmp/x", f"python3 {k.install}/operator_run.py --config /tmp/c run ACT-W1 {msha}",
           f"python3 {k.install}/operator_run.py run ACT-W2 {msha}", f"git -C {k.repo} add data/plain.txt",
           f"git -C {k.repo} commit --amend -m x", f"bash {frozen}/apply.sh check; sudo true", "curl https://x.y"]
    for c in bad:
        assert drive(k, cmd, {"tool_name": "Bash", "tool_input": {"command": c}, "cwd": w}) == "deny", c
    for p in (k.install / "brief.md", k.install / "APPROVED", k.install / "class-rules.yaml", k.home / ".claude/x",
              k.repo / "tests/acceptance/W2-1/t.py", Path("/etc/shadow"), k.tx / "other.jsonl"):
        assert drive(k, cmd, {"tool_name": "Read", "tool_input": {"file_path": str(p)}, "cwd": w}) == "deny", p
    for t in ("Write", "Edit", "WebFetch", "Task", "mcp__x__y"):
        assert drive(k, cmd, {"tool_name": t, "tool_input": {"file_path": f"{w}/x"}, "cwd": w}) == "deny"
    assert drive(k, cmd, b"{not json") == "deny"


# --------------------------------------------------------------------------------------------------- the landing check
def test_the_landing_check_flags_commits_outside_a_ticket_on_control_paths(tmp_path):
    repo = tmp_path / "r"
    repo.mkdir()
    sh("git", "init", "-q", "-b", "main", cwd=repo)
    sh("git", "config", "user.email", "t@t", cwd=repo)
    sh("git", "config", "user.name", "t", cwd=repo)
    write(repo / "README", "x")
    sh("git", "add", "-A", cwd=repo)
    sh("git", "commit", "-q", "-m", "base", cwd=repo)
    base = sh("git", "rev-parse", "HEAD", cwd=repo).stdout.decode().strip()
    want = {}

    def commit(path, msg, trailers, flagged):
        with open(repo / path if (repo / path).parent.exists() else write(repo / path, ""), "a") as f:
            f.write(msg + "\n")
        sh("git", "add", "-A", cwd=repo)
        sh("git", "commit", "-q", "-m", msg, "-m", "\n".join(trailers), cwd=repo)
        want[sh("git", "rev-parse", "HEAD", cwd=repo).stdout.decode().strip()] = flagged

    commit(".claude/hooks/pretooluse.py", "cto hook", ["Task: DAEO-sdxk", "Role: orchestrator"], True)
    commit(".claude/hooks/pretooluse.py", "op no act", ["Role: operator"], True)
    commit(".claude/hooks/pretooluse.py", "op act", ["Role: operator", "Act: ACT-X"], False)
    commit(".claude/hooks/pretooluse.py", "owner", ["Role: owner"], False)
    commit(".claude/hooks/pretooluse.py", "ticket", ["Task: DAEO-abcd", "Role: engineer"], False)
    commit("CHECKPOINT.md", "records", ["Task: decision-record", "Role: orchestrator"], False)
    commit("tests/optin-x.txt", "cto optin", ["Role: orchestrator"], True)
    r = subprocess.run([sys.executable, str(OPDIR / "landing_check.py"), "--repo", str(repo), f"{base}..HEAD"],
                       capture_output=True)
    items = json.loads(r.stdout.decode().strip().splitlines()[-1])
    assert {i["commit"] for i in items} == {c for c, f in want.items() if f}
    assert all(i["priority"] == "P1" and re.match(r"^[0-9a-f]{40}$", i["commit"]) for i in items)
