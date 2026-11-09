"""What only a real sandboxed CLI session shows: four cases, skipped unless ``GOV_W2_56_REAL=1`` (the CTO, outside
the launch sandbox; DEC-1112 (1)).

Each case starts real ``claude -p`` sessions through ``gov launch`` (this tree's code, the real CLI at
``~/.local/bin/claude``, the real ``HOME`` so the CLI can sign in), on a fixture project under the test's own temp
folder. Each session is asked to run one Bash command: ``python3 <script>``, a script the test wrote outside the
project, which does the one thing the case is about and writes what happened to ``.w56-real/<label>.json`` in the
worktree (the CLI's sandbox lets a session write its own working folder). The fixture's guard hook is a no-op that
allows every call, so the operating system is the only fence measured. The cheapest model the CLI takes:
``GOV_W2_56_REAL_MODEL`` (default ``haiku``; empty for none).

- ``test_s2_real_sandbox_a_script_write_into_another_worktree_or_a_denied_name_is_refused`` (S2, F1): a script
  writes into a sibling worktree and into ``tests/acceptance/`` (a literal deny rule for the engineer); both refused.
- ``test_s9_real_sandbox_a_second_unix_socket_is_refused`` (S9, F4): a script connects to a Unix socket the test
  listens on, other than the reranker's; refused, and the listener sees no connection.
- ``test_s7_real_sandbox_three_sessions_at_once_in_worktrees_sharing_one_git_start_and_commit`` (S7): three sessions
  started at once in three worktrees of one repository each commit; none fails on a ``.git/*.lock`` source path.
- ``test_s13_real_sandbox_gov_check_gov_rebuild_and_a_code_graph_suite_run_inside_the_sandbox`` (S13, S1): after a
  rebuild made outside (so ``.gov-runtime/`` holds entries the launcher's literal deny rules name), a script runs
  ``gov check --list``, ``gov rebuild --no-embeddings`` and S1's probe suite; all end 0, and the suite's daemon
  folders lie under the session's temp folder.

What they cost and prove is in the README. They write what ``gov launch`` writes: a run folder under
``~/gov-os-runs`` for the fixture's ticket, and the machine-wide registry entry while each session runs. They never
touch the live reranker's socket.
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

import w2_56_support as s

REAL = os.environ.get("GOV_W2_56_REAL") == "1"
MODEL = os.environ.get("GOV_W2_56_REAL_MODEL", "haiku")
SESSION_TIMEOUT_S = 420
pytestmark = pytest.mark.skipif(not REAL, reason="real_sandbox: starts real CLI sessions; set GOV_W2_56_REAL=1 "
                                                 "(the CTO, outside the launch sandbox)")
NO_OP_GUARD = "#!/usr/bin/env python3\nimport sys\nsys.stdin.read()\nsys.exit(0)\n"
RESULTS_REL = ".w56-real"


def _box(tmp_path) -> s.Box:
    if not (Path.home() / ".local/bin/claude").is_file():
        pytest.skip("no CLI at ~/.local/bin/claude")
    base = tmp_path.resolve()
    box = s.Box(base, Path.home(), base / "systmp", base / "elsewhere", base / "pycache")
    for folder in (box.tmpdir, box.elsewhere, box.pycache):
        folder.mkdir(parents=True, exist_ok=True)
    return box


def _project(box: s.Box, name: str = "W2-77") -> Path:
    project = box.base / "wt" / name
    s.make_project(box, project=project, extra={"governance/kernel/hooks/pretooluse.py": NO_OP_GUARD})
    return project


def _env() -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = s.python_path()     # gov launch runs this tree's code; the launcher keeps it from the session
    return env


def _script(box: s.Box, label: str, text: str) -> Path:
    path = box.elsewhere / f"{label}.py"
    path.write_text(text, encoding="utf-8")
    return path


def _cli_args(command: str) -> list[str]:
    prompt = (f"Use the Bash tool to run exactly this one command, once and unchanged, then reply DONE and stop. "
              f"Do nothing else.\n\n{command}")
    args = ["-p", prompt, "--allowedTools", "Bash", "--max-turns", "4"]
    return args + (["--model", MODEL] if MODEL else [])


def _start(project: Path, ticket: str, command: str, role: str = s.ENGINEER) -> subprocess.Popen:
    return subprocess.Popen(s.launch_argv(role, ticket, _cli_args(command), gate_override=False), cwd=str(project),
                            env=_env(),
                            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def _finish(process: subprocess.Popen) -> tuple[int, str]:
    try:
        out, err = process.communicate(timeout=SESSION_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        process.kill()
        out, err = process.communicate()
        raise AssertionError(f"the real session did not end within {SESSION_TIMEOUT_S} s") from None
    return process.returncode, (out + "\n" + err)[-2500:]


def _result(project: Path, label: str, output: str) -> dict:
    path = project / RESULTS_REL / f"{label}.json"
    assert path.is_file(), f"the session did not run its command (no {path}):\n{output}"
    return json.loads(path.read_text(encoding="utf-8"))


def _launcher_folder(tmpdir: str) -> str:
    """The launcher's temp folder: the folder named gov-launch-* that the command's TMPDIR lies in."""
    path = Path(tmpdir)
    for folder in (path, *path.parents):
        if folder.name.startswith(s.TEMP_PREFIX):
            return str(folder)
    raise AssertionError(f"the command's TMPDIR {tmpdir} is not under a {s.TEMP_PREFIX}* folder")


WRITE_SCRIPT = """import json, os, sys
out, targets = sys.argv[1], sys.argv[2:]
seen = {}
for target in targets:
    try:
        with open(target, "w") as handle:
            handle.write("x")
        seen[target] = "written"
    except OSError as error:
        seen[target] = "%s errno %s" % (type(error).__name__, error.errno)
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w") as handle:
    json.dump({"seen": seen}, handle)
"""


def test_s2_real_sandbox_a_script_write_into_another_worktree_or_a_denied_name_is_refused(tmp_path):
    box = _box(tmp_path)
    project = _project(box)
    other = s.add_worktree(project, "W2-78")
    targets = [str(other / "w56-script-write.txt"), str(project / "tests/acceptance/W2-77/w56_script_write.py")]
    out = project / RESULTS_REL / "write.json"
    script = _script(box, "write", WRITE_SCRIPT)
    code, output = _finish(_start(project, s.T.tk, f"python3 {script} {out} {' '.join(targets)}"))
    seen = _result(project, "write", output)["seen"]
    written = [target for target in targets if seen.get(target) == "written" or os.path.exists(target)]
    assert not written, f"the sandbox let a script write {written}: {seen}"


SOCKET_SCRIPT = """import json, os, socket, sys
out, path = sys.argv[1], sys.argv[2]
try:
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.settimeout(5)
    client.connect(path)
    client.sendall(b"w56\\n")
    outcome = "connected"
except OSError as error:
    outcome = "%s errno %s" % (type(error).__name__, error.errno)
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w") as handle:
    json.dump({"outcome": outcome}, handle)
"""


def test_s9_real_sandbox_a_second_unix_socket_is_refused(tmp_path):
    box = _box(tmp_path)
    project = _project(box)
    path = str(box.elsewhere / "o.sock")
    if len(path) > 100:
        pytest.skip(f"the planted socket path is too long here: {path}")
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(path)
    server.listen(4)
    server.settimeout(0.2)
    accepted, stop = [], threading.Event()

    def serve():
        while not stop.is_set():
            try:
                connection, _ = server.accept()
                accepted.append(time.time())
                connection.close()
            except OSError:
                continue

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    try:
        out = project / RESULTS_REL / "socket.json"
        script = _script(box, "socket", SOCKET_SCRIPT)
        code, output = _finish(_start(project, s.T.tk, f"python3 {script} {out} {path}"))
        outcome = _result(project, "socket", output)["outcome"]
    finally:
        stop.set()
        thread.join(timeout=5)
        server.close()
    assert outcome != "connected" and not accepted, (
        f"a sandboxed session connected to a Unix socket other than the reranker's: {outcome}, {len(accepted)} seen")


COMMIT_SCRIPT = """import json, os, subprocess, sys
out, name = sys.argv[1], sys.argv[2]
with open(os.path.join("src", name + ".txt"), "w") as handle:
    handle.write(name + "\\n")
steps = {}
for label, argv in (("add", ["git", "add", "-A"]), ("commit", ["git", "commit", "-q", "-m", "w56 real " + name])):
    done = subprocess.run(argv, capture_output=True, text=True)
    steps[label] = {"code": done.returncode, "stderr": done.stderr[-800:]}
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w") as handle:
    json.dump(steps, handle)
"""


def test_s7_real_sandbox_three_sessions_at_once_in_worktrees_sharing_one_git_start_and_commit(tmp_path):
    box = _box(tmp_path)
    project = _project(box)
    script = _script(box, "commit", COMMIT_SCRIPT)
    trees = {name: s.add_worktree(project, name) for name in ("wt-a", "wt-b", "wt-c")}
    tickets = {"wt-a": s.T, "wt-b": s.T2, "wt-c": s.T3}
    processes = {name: _start(tree, tickets[name].tk,
                              f"python3 {script} {tree / RESULTS_REL / 'commit.json'} {name}")
                 for name, tree in trees.items()}
    ended = {name: _finish(process) for name, process in processes.items()}
    for name, tree in trees.items():
        code, output = ended[name]
        assert code == 0, f"the launch in {name} ended with {code}:\n{output}"
        steps = _result(tree, "commit", output)
        assert steps["commit"]["code"] == 0, f"the commit in {name} failed: {steps}"
        files = s.git(tree, "show", "--name-only", "--format=", "HEAD").stdout.split()
        assert f"src/{name}.txt" in files, f"the commit in {name} does not hold its file: {files}"


SUITE_SCRIPT = """import json, os, subprocess, sys
out, src, repo, probe, tools = sys.argv[1:6]
env = dict(os.environ, PYTHONPATH=src, PYTHONDONTWRITEBYTECODE="1")
record, calls = os.path.join(os.path.dirname(out), "probe.jsonl"), os.path.join(tools, "calls.txt")
runs = {}
for label, argv, cwd, extra in (
        ("check", [sys.executable, "-m", "gov.cli.main", "check", "--list"], os.getcwd(), {}),
        ("rebuild", [sys.executable, "-m", "gov.cli.main", "rebuild", "--no-embeddings"], os.getcwd(), {}),
        ("suite", [sys.executable, "-m", "pytest", probe, "--rootdir=" + repo, "-q", "-p", "no:cacheprovider"], repo,
         {"W2_56_PROBE_RECORD": record, "W2_56_PROBE_STANDIN": tools})):
    done = subprocess.run(argv, cwd=cwd, env=dict(env, **extra), capture_output=True, text=True)
    runs[label] = {"code": done.returncode, "tail": (done.stdout + done.stderr)[-1200:]}
daemons = sorted(set(open(calls).read().split())) if os.path.exists(calls) else []
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w") as handle:
    json.dump({"runs": runs, "daemons": daemons, "tmpdir": os.environ.get("TMPDIR", "")}, handle)
"""
STAND_IN_TOOL = """#!/bin/sh
printf '%s\\n' "$CBM_RUNTIME_DIR" >> "@CALLS@"
case "$1" in config) exit 0;; esac
printf '%s\\n' '{"isError": false, "content": [{"type": "text", "text": "{\\"projects\\": []}"}]}'
"""


def test_s13_real_sandbox_gov_check_gov_rebuild_and_a_code_graph_suite_run_inside_the_sandbox(tmp_path):
    box = _box(tmp_path)
    project = _project(box)
    before = subprocess.run(s.gov_argv("rebuild", "--no-embeddings"), cwd=str(project), env=_env(),
                            capture_output=True, text=True, timeout=SESSION_TIMEOUT_S)
    assert before.returncode == 0, f"the rebuild outside the sandbox (the premise) failed:\n{before.stderr[-1500:]}"
    tools = box.elsewhere / "tools"
    tools.mkdir()
    tool = tools / "codebase-memory-mcp"
    tool.write_text(STAND_IN_TOOL.replace("@CALLS@", str(project / RESULTS_REL / "calls.txt")), encoding="utf-8")
    tool.chmod(0o755)
    out = project / RESULTS_REL / "suite.json"
    script = _script(box, "suite", SUITE_SCRIPT.replace('os.path.join(tools, "calls.txt")',
                                                        repr(str(project / RESULTS_REL / "calls.txt"))))
    probe = s.HERE / "w2_56_daemon_probe.py"
    command = f"python3 {script} {out} {s.python_path().split(os.pathsep)[0]} {s.REPO_ROOT} {probe} {tools}"
    code, output = _finish(_start(project, s.T.tk, command))
    found = _result(project, "suite", output)
    failed = {label: run for label, run in found["runs"].items() if run["code"] != 0}
    assert not failed, f"inside the sandbox these did not run: {json.dumps(failed)[:2500]}"
    folder = _launcher_folder(found["tmpdir"])
    outside = [d for d in found["daemons"] if not (d == folder or d.startswith(folder + "/"))]
    assert found["daemons"] and not outside, (
        f"the suite's daemon folders are not under the session's temp folder {folder}: {found['daemons']}")
