"""Support code for the W2-56 acceptance tests, the first half (DEC-1099 (1)): standard library and PyYAML only.

The tests drive public interfaces only:

- **``gov launch <role> <ticket> [-- <CLI arguments>]``**, through gov's console entry point (no install), with a
  stand-in for the CLI at ``<HOME>/.local/bin/claude``. The stand-in starts no session. It records what it was
  handed (its arguments, the ``--settings`` value, its whole process environment, its cwd, pid, process group and
  session) and then runs the steps of a plan file written by the test (plant files, run git, start a grandchild,
  wait for a file, end with a code or by SIGKILL). The plan's path is written into the stand-in itself, so the
  stand-in needs nothing from its environment, which is what the launcher cleans.
- **``gov.codeintel``**, run in a pytest session of its own (``w2_56_daemon_probe.py``) with a stand-in for the
  code-graph tool that records the ``CBM_RUNTIME_DIR`` (the daemon folder) it is given.
- **the kernel template's settings**, ``template/governance/kernel/settings.json``, read as a file.

**The code under test** is this worktree's ``src/``: every child gets ``PYTHONPATH`` (the runner's own value when it
has one, DEC-732, else the ``src`` folder of the worktree that holds this file).

**Homes and temp folders.** Every test has its own base folder (pytest's ``tmp_path``) holding disjoint siblings:
``home/`` (the ``HOME`` of the launcher: it holds the project, the stand-in CLI and ``gov-os-runs``), ``systmp/`` (the
launcher's ``TMPDIR``: the launcher makes the session's temp folder in it), ``elsewhere/`` (the plan, the stand-in's
records, the outside target of a link) and ``pycache/``. No real secret, held-out path, ``~/.ssh``, real CLI, real
code-graph daemon or network is used.

**The fixture project** is a git repository built from scratch at ``home/gov-os-worktrees/W2-77``: tickets, a few
files, a ``.claude/settings.json`` that registers the guard (the launcher checks that it is wired; the stand-in never
runs a hook), this worktree's own ``.gitignore`` (so a fix made there counts), and git's identity in the
repository's own config (the session's environment is cleaned, so the identity cannot come from it).
"""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PYPROJECT = REPO_ROOT / "pyproject.toml"
TEMPLATE_SETTINGS = REPO_ROOT / "template/governance/kernel/settings.json"
ALLOWLIST_REL = "template/governance/kernel/launch/research-allowlist.yaml"
GIT = shutil.which("git") or "/usr/bin/git"

ENGINEER = "engineer"
TEST_DESIGNER = "independent-test-designer"
AUDITOR = "independent-auditor"
PRODUCT_SPEC = "product-spec"
RESEARCH = "research"
WORKER_ROLES = (ENGINEER, TEST_DESIGNER, AUDITOR, PRODUCT_SPEC, RESEARCH)

COMMAND_TIMEOUT_S = 60.0
END_WAIT_S = 5          # the launcher's wait before it kills a session asked to end (DEC-392, launcher.END_WAIT_S)
INTERRUPT_EXIT = 130    # the launcher's exit code after an ending signal (DEC-392)
TEMP_PREFIX = "gov-launch-"
MARK = "zqxw56parent"   # in every planted parent value: no session value may hold it


# --------------------------------------------------------------------------
# The fixture tickets
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Ticket:
    tk: str
    role: str
    wbs: str
    allowed: tuple
    status: str = "in_progress"


T = Ticket("DAEO-zw56", ENGINEER, "W2-77", ("src/app/**",))
T2 = Ticket("DAEO-zw57", ENGINEER, "W2-78", ("src/b/**",))
T3 = Ticket("DAEO-zw58", ENGINEER, "W2-79", ("src/c/**",))
SPEC = Ticket("DAEO-zw59", PRODUCT_SPEC, "W2-80", ("docs/spec/**",))
EXPERIMENT = Ticket("DAEO-zw60", RESEARCH, "W2-81", ("experiments/spikes/exp-56/**",))
CLOSED = Ticket("DAEO-zw61", ENGINEER, "W2-82", ("src/closed/**",), status="closed")
TICKETS = (T, T2, T3, SPEC, EXPERIMENT, CLOSED)
# The ticket each worker role is launched on: the two independent roles may take any in_progress ticket.
TICKET_OF = {ENGINEER: T, TEST_DESIGNER: T, AUDITOR: T, PRODUCT_SPEC: SPEC, RESEARCH: EXPERIMENT}


def ticket_text(ticket: Ticket) -> str:
    lines = [
        "---",
        f"id: {ticket.tk}",
        f"status: {ticket.status}",
        "deps: []",
        "links: []",
        "created: 2026-11-09T07:00:00Z",
        "type: task",
        "priority: 1",
        f"assignee: {ticket.role}",
        f"external-ref: {ticket.wbs}",
        "tags: [wave-2, implementation, standard]",
        f"wbs_id: {ticket.wbs}",
        "title: W2-56 fixture ticket",
        "class: implementation",
        f"role: {ticket.role}",
        "depends_on: []",
        "allowed_paths:",
        *[f"- {path}" for path in ticket.allowed],
        "kpis:",
        "  success:",
        "  - The fixture component exists",
        "  failure:",
        "  - The fixture component is missing",
        "profile: STANDARD",
        "acceptance_tests:",
        f"  path: tests/acceptance/{ticket.wbs}/",
        "---",
        f"# {ticket.wbs} W2-56 fixture ticket",
        "",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# The box: home, temp folder and elsewhere, disjoint
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Box:
    base: Path
    home: Path
    tmpdir: Path
    elsewhere: Path
    pycache: Path

    @property
    def project(self) -> Path:
        return self.home / "gov-os-worktrees" / T.wbs

    @property
    def cli(self) -> Path:
        return self.home / ".local/bin/claude"

    @property
    def plan(self) -> Path:
        return self.elsewhere / "plan.json"

    @property
    def calls(self) -> Path:
        return self.elsewhere / "calls"

    @property
    def results(self) -> Path:
        return self.elsewhere / "results"


def make_box(base) -> Box:
    base = Path(base).resolve()
    box = Box(base, base / "home", base / "systmp", base / "elsewhere", base / "pycache")
    for folder in (box.home, box.tmpdir, box.elsewhere, box.pycache, box.calls, box.results):
        folder.mkdir(parents=True, exist_ok=True)
    return box


def python_path() -> str:
    """Every child's PYTHONPATH: the runner's own (DEC-732), else this worktree's src."""
    return os.environ.get("PYTHONPATH") or str(REPO_ROOT / "src")


def base_environment(box: Box) -> dict:
    """The launcher's own environment, before a test adds the parent's variables it plants."""
    return {
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "HOME": str(box.home),
        "TMPDIR": str(box.tmpdir),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "USER": "w2-56-user",
        "LOGNAME": "w2-56-user",
        "TZ": "UTC",
        "PYTHONPATH": python_path(),
        "PYTHONPYCACHEPREFIX": str(box.pycache),
        "PYTHONDONTWRITEBYTECODE": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
    }


# --------------------------------------------------------------------------
# The fixture project, from scratch
# --------------------------------------------------------------------------

GUARD_COMMAND = 'python3 "$CLAUDE_PROJECT_DIR"/governance/kernel/hooks/pretooluse.py'
IDENTITY = (("user.name", "W2-56 acceptance"), ("user.email", "w2-56@example.invalid"),
            ("commit.gpgsign", "false"), ("core.hooksPath", "/dev/null"))


def settings_text(**extra) -> str:
    data = {"hooks": {"PreToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": GUARD_COMMAND}]}]}}
    data.update(extra)
    return json.dumps(data, indent=2) + "\n"


def git(directory, *args, check=True, env=None) -> subprocess.CompletedProcess:
    proc = subprocess.run([GIT, "-C", str(directory), *args], capture_output=True, text=True, check=False,
                          timeout=COMMAND_TIMEOUT_S, env=env)
    if check and proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {directory}: {proc.stderr.strip()}")
    return proc


def write(path, text) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def repo_gitignore() -> str:
    """This worktree's own ``.gitignore`` (so a fix the engineer's package makes there counts), plus nothing."""
    path = REPO_ROOT / ".gitignore"
    return path.read_text(encoding="utf-8") if path.is_file() else ""


BASE_FILES = {
    "README.md": "# W2-56 fixture project\n",
    "src/app/main.py": "def value():\n    return 1\n",
    "src/b/main.py": "VALUE = 2\n",
    "src/c/main.py": "VALUE = 3\n",
    "docs/spec/feature.md": "spec\n",
    "docs/notes.md": "notes\n",
    "experiments/spikes/exp-56/README.md": "# Experiment 56\n",
    "tests/acceptance/W2-77/test_feature.py": "def test_feature():\n    assert True\n",
}


def make_project(box: Box, extra=None, project=None) -> Path:
    """The fixture project: one commit on ``w2/integrate`` holding every ticket, the files and the settings."""
    project = Path(project or box.project)
    files = dict(BASE_FILES)
    files[".gitignore"] = repo_gitignore()
    for ticket in TICKETS:
        files[f".tickets/{ticket.tk}.md"] = ticket_text(ticket)
    files[".claude/settings.json"] = settings_text()
    allowlist = REPO_ROOT / ALLOWLIST_REL
    if allowlist.is_file():
        files[ALLOWLIST_REL] = allowlist.read_text(encoding="utf-8")
    files.update(extra or {})
    for rel, text in files.items():
        if text is not None:
            write(project / rel, text)
    git(project, "init", "-q", "-b", "w2/integrate")
    for key, value in IDENTITY:
        git(project, "config", key, value)
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "W2-56 fixture: the base")
    return project


def add_worktree(project: Path, name: str) -> Path:
    """A worktree of the project sharing its ``.git``, on a branch of its own."""
    where = project.parent / name
    git(project, "worktree", "add", "-q", "-b", f"w2/{name}", str(where))
    return where


# --------------------------------------------------------------------------
# The stand-in CLI
# --------------------------------------------------------------------------

_STUB = r'''#!@PYTHON@
"""Stand-in for the Claude Code CLI (W2-56 acceptance tests). Starts no session: records, then runs its plan."""
import json, os, signal, subprocess, sys, time

PLAN, CALLS, RESULTS, GIT = @PLAN@, @CALLS@, @RESULTS@, @GIT@
args = sys.argv[1:]
cwd = os.getcwd()
name = os.path.basename(cwd)
settings = []
i = 0
while i < len(args):
    value = None
    if args[i] == "--settings" and i + 1 < len(args):
        value, i = args[i + 1], i + 1
    elif args[i].startswith("--settings="):
        value = args[i].split("=", 1)[1]
    if value is not None:
        if value.lstrip().startswith("{"):
            settings.append(value)
        else:
            try:
                with open(value, encoding="utf-8") as handle:
                    settings.append(handle.read())
            except OSError as exc:
                settings.append("unreadable: " + str(exc))
    i += 1
record = {"args": args, "settings": settings, "env": dict(os.environ), "cwd": cwd, "name": name,
          "pid": os.getpid(), "pgid": os.getpgid(0), "sid": os.getsid(0), "ppid": os.getppid(),
          "time": time.time()}
path = os.path.join(CALLS, "%.6f-%d.json" % (time.time(), os.getpid()))
with open(path + ".part", "w", encoding="utf-8") as handle:
    json.dump(record, handle)
os.replace(path + ".part", path)

try:
    with open(PLAN, encoding="utf-8") as handle:
        plans = json.load(handle)
except (OSError, ValueError):
    plans = {}
plan = plans.get(name, plans.get("default", []))
tmp = os.environ.get("TMPDIR", "")


def fill(text):
    return (text.replace("{name}", name).replace("{tmpdir}", tmp).replace("{cwd}", cwd)
            .replace("{uid}", str(os.getuid())))


GRANDCHILD = (
    "import os, signal, sys, time\n"
    "pidfile, ignore, seen = sys.argv[1], sys.argv[2] == '1', sys.argv[3]\n"
    "def note(signum, frame):\n"
    "    with open(seen, 'a') as handle:\n"
    "        handle.write(signal.Signals(signum).name + '\\n')\n"
    "    if not ignore:\n"
    "        os._exit(0)\n"
    "for number in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):\n"
    "    signal.signal(number, note)\n"
    "with open(pidfile + '.part', 'w') as handle:\n"
    "    handle.write(str(os.getpid()))\n"
    "os.replace(pidfile + '.part', pidfile)\n"
    "end = time.time() + 120\n"
    "while time.time() < end:\n"
    "    time.sleep(0.05)\n"
)

count = 0
for step in plan:
    do = step["do"]
    count += 1
    if do == "exit":
        sys.exit(step.get("code", 0))
    elif do == "kill_self":
        os.kill(os.getpid(), signal.SIGKILL)
    elif do == "fill_tmp":
        os.makedirs(os.path.join(tmp, "a/b/c"), exist_ok=True)
        for rel in ("a/one.txt", "a/b/two.txt", "a/b/c/three.txt", "daemon/cbm.lock"):
            os.makedirs(os.path.dirname(os.path.join(tmp, rel)), exist_ok=True)
            with open(os.path.join(tmp, rel), "w") as handle:
                handle.write("x\n")
        if step.get("readonly"):  # as a module cache leaves them: folders the owner may not write
            locked = os.path.join(tmp, "readonly/inner")
            os.makedirs(locked, exist_ok=True)
            with open(os.path.join(locked, "kept.txt"), "w") as handle:
                handle.write("x\n")
            os.chmod(locked, 0o500)
            os.chmod(os.path.dirname(locked), 0o500)
        os.symlink(step["outside"], os.path.join(tmp, "link-outside"))
        os.mkfifo(os.path.join(tmp, "fifo"))
    elif do == "plant":
        for rel in step["names"]:
            target = os.path.join(cwd, rel)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            if not os.path.lexists(target):
                open(target, "w").close()
    elif do == "write":
        target = os.path.join(cwd, fill(step["path"]))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w") as handle:
            handle.write(step.get("text", "x\n"))
    elif do == "git":
        done = subprocess.run([GIT, *[fill(a) for a in step["argv"]]], cwd=cwd, capture_output=True, text=True)
        out = os.path.join(RESULTS, "%s-%s.json" % (name, step.get("label", count)))
        with open(out, "w", encoding="utf-8") as handle:
            json.dump({"argv": step["argv"], "code": done.returncode, "stdout": done.stdout,
                       "stderr": done.stderr}, handle)
    elif do == "run":  # second half: a command in the session's environment, with the overrides the step names
        env = dict(os.environ)
        env.update({key: fill(value) for key, value in step.get("env", {}).items()})
        for folder in step.get("mkdir", []):
            os.makedirs(fill(folder), exist_ok=True)
        done = subprocess.run([fill(a) for a in step["argv"]], cwd=cwd, env=env, capture_output=True, text=True)
        out = os.path.join(RESULTS, "%s-%s.json" % (name, step.get("label", count)))
        with open(out, "w", encoding="utf-8") as handle:
            json.dump({"argv": step["argv"], "code": done.returncode, "stdout": done.stdout,
                       "stderr": done.stderr}, handle)
    elif do == "touch":
        target = fill(step["path"])
        os.makedirs(os.path.dirname(target), exist_ok=True)
        open(target, "a").close()
    elif do == "wait_for":
        end = time.time() + step.get("timeout", 30)
        paths = [fill(p) for p in step["paths"]]
        while not all(os.path.exists(p) for p in paths):
            if time.time() > end:
                sys.exit(step.get("fail_code", 7))
            time.sleep(0.05)
    elif do == "grandchild":
        pidfile = fill(step["pidfile"])
        subprocess.Popen([sys.executable, "-c", GRANDCHILD, pidfile, "1" if step.get("ignore") else "0",
                          fill(step["seen"])], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
        end = time.time() + 20
        while not os.path.exists(pidfile) and time.time() < end:
            time.sleep(0.02)
    elif do == "sleep":
        end = time.time() + step["seconds"]
        while time.time() < end:
            time.sleep(0.05)
sys.exit(0)
'''


def install_stand_in_cli(box: Box) -> Path:
    path = box.cli
    path.parent.mkdir(parents=True, exist_ok=True)
    text = (_STUB.replace("@PYTHON@", sys.executable).replace("@PLAN@", repr(str(box.plan)))
            .replace("@CALLS@", repr(str(box.calls))).replace("@RESULTS@", repr(str(box.results)))
            .replace("@GIT@", repr(GIT)))
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)
    return path


def set_plan(box: Box, plan=None, **by_name) -> None:
    """The stand-in's steps: ``plan`` for every session, ``by_name`` for a session whose cwd has that name."""
    data = dict(by_name)
    data["default"] = plan or []
    box.plan.write_text(json.dumps(data), encoding="utf-8")


def calls(box: Box) -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(box.calls.glob("*.json"))]


def result(box: Box, name: str, label: str) -> dict:
    path = box.results / f"{name}-{label}.json"
    assert path.is_file(), f"the stand-in session in {name} recorded no result {label!r}"
    return json.loads(path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# gov, through its console script entry point (no install)
# --------------------------------------------------------------------------

def _entry_point() -> tuple[str, str]:
    scripts = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]["scripts"]
    module, _, attribute = scripts["gov"].partition(":")
    return module.strip(), attribute.strip()


def gov_argv(*args) -> list[str]:
    module, attribute = _entry_point()
    code = (f"import sys\nimport {module} as _m\n_t = _m\nfor _n in {attribute!r}.split('.'):\n"
            "    _t = getattr(_t, _n)\nsys.argv[0] = 'gov'\nsys.exit(_t())\n")
    return [sys.executable, "-c", code, *args]


# W2-20's resource gate (merged into integrate after the first half) is shut in a planted HOME (no gate.json): every
# launch here passes it with one recorded override, written to the planted HOME's launch log only. The gate is
# W2-20's, not under test here; the real cases (test_w2_56_real_sandbox) keep the machine's own gate.
GATE_OVERRIDE = "DEC-1112"


def launch_argv(role: str, ticket: str, cli_args=None, gate_override: bool = True) -> list[str]:
    args = ["launch", role, ticket]
    if gate_override:
        args += ["--gate-override", GATE_OVERRIDE]
    if cli_args is not None:
        args += ["--", *cli_args]
    return gov_argv(*args)


@dataclass(frozen=True)
class Launch:
    argv: tuple
    returncode: int
    stdout: str
    stderr: str
    calls: tuple

    @property
    def output(self) -> str:
        return self.stdout + "\n" + self.stderr

    def describe(self) -> str:
        return (f"{' '.join(self.argv[3:])}\nexit code: {self.returncode}\nstdout:\n{self.stdout[-1500:]}\n"
                f"stderr:\n{self.stderr[-1500:]}\nsessions recorded: {len(self.calls)}")

    @property
    def started(self) -> bool:
        return len(self.calls) == 1

    @property
    def call(self) -> dict:
        assert len(self.calls) == 1, f"gov launch did not start exactly one session\n{self.describe()}"
        return self.calls[0]

    def settings(self) -> dict:
        entries = self.call["settings"]
        assert len(entries) == 1, f"the session was started with {len(entries)} --settings values\n{self.describe()}"
        data = json.loads(entries[0])
        assert isinstance(data, dict), "the --settings value is not a JSON object"
        return data


def run_launch(box: Box, role: str, ticket: str, cli_args=None, *, env=None, cwd=None,
               timeout=COMMAND_TIMEOUT_S) -> Launch:
    before = {p.name for p in box.calls.glob("*.json")}
    argv = launch_argv(role, ticket, cli_args)
    try:
        done = subprocess.run(argv, cwd=str(cwd or box.project), env=env or base_environment(box),
                              capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"gov launch {role} {ticket} did not end within {timeout:.0f} s") from None
    new = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(box.calls.glob("*.json"))
           if p.name not in before]
    return Launch(tuple(argv), done.returncode, done.stdout, done.stderr, tuple(new))


def start_launch(box: Box, role: str, ticket: str, cli_args=None, *, env=None, cwd=None) -> subprocess.Popen:
    """``gov launch`` started in a session (and process group) of its own, so a signal sent to its pid reaches
    the launcher alone, as a signal sent to the launcher by its caller does."""
    return subprocess.Popen(launch_argv(role, ticket, cli_args), cwd=str(cwd or box.project),
                            env=env or base_environment(box), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, start_new_session=True)


def wait_for(predicate, timeout: float, step: float = 0.05) -> bool:
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if predicate():
            return True
        time.sleep(step)
    return bool(predicate())


def finish(process: subprocess.Popen, timeout: float = COMMAND_TIMEOUT_S) -> tuple[int, str, str]:
    try:
        out, err = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except OSError:
            pass
        out, err = process.communicate()
        raise AssertionError(f"gov launch did not end within {timeout:.0f} s\nstderr:\n{err[-1500:]}") from None
    return process.returncode, out, err


def alive(pid: int) -> bool:
    """Whether the process runs: it exists and is no zombie."""
    try:
        with open(f"/proc/{pid}/stat", encoding="utf-8") as handle:
            state = handle.read().rsplit(")", 1)[1].split()[0]
    except (OSError, IndexError):
        return False
    return state not in ("Z", "X")


def kill_quietly(pid: int) -> None:
    try:
        os.kill(pid, signal.SIGKILL)
    except OSError:
        pass


def temp_folders(box: Box) -> list[str]:
    """The entries the launcher left in its own temp root (its ``TMPDIR``)."""
    return sorted(p.name for p in box.tmpdir.iterdir())


# --------------------------------------------------------------------------
# The launcher's environment (KPI S5)
# --------------------------------------------------------------------------

# The parent's variables of each kind the ticket names (DEC-826 Q5, lens E F13, DEC-784, DEC-877 item 4, W2-M393):
# its session id, messaging socket and token, child-session mark, effort, compaction window, subagent model,
# GOV_DEV_TIERS, the other CLAUDE* and GOV* a parent session holds here, and PYTHONPATH.
PARENT_VARIABLES = {
    "CLAUDECODE": "1",
    "CLAUDE_CODE_CHILD_SESSION": "1",
    "CLAUDE_CODE_SESSION_ID": f"{MARK}-session-id",
    "CLAUDE_CODE_MESSAGING_SOCKET": f"/tmp/{MARK}-messaging.sock",
    "CLAUDE_CODE_MESSAGING_TOKEN": f"{MARK}-token",
    "CLAUDE_EFFORT": f"{MARK}-max",
    "CLAUDE_CODE_EFFORT_LEVEL": f"{MARK}-high",
    "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "400000",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "95",
    "CLAUDE_CODE_SUBAGENT_MODEL": f"{MARK}-subagent-model",
    "CLAUDE_CODE_ENTRYPOINT": f"{MARK}-entrypoint",
    "CLAUDE_PID": "424242",
    "CLAUDE_TMPDIR": f"/tmp/{MARK}-claude-tmpdir",
    "CLAUDE_CODE_TMPDIR": f"/tmp/{MARK}-claude-code-tmpdir",
    "CLAUDE_PROJECT_DIR": f"/tmp/{MARK}-project-dir",
    "CLAUDE_CODE_HOST_HTTP_PROXY_PORT": "42421",
    "CLAUDE_W2_56_ANY": f"{MARK}-any-claude",
    "GOV_DEV_TIERS": "1",
    "GOV_ROLE": f"orchestrator-{MARK}",
    "GOV_TICKET": f"DAEO-{MARK}",
    "GOV_STORE": f"/tmp/{MARK}-store",
    "GOV_REBUILD_LOCK": f"/tmp/{MARK}-rebuild.lock",
    "GOV_VECTOR_CACHE_DIR": f"/tmp/{MARK}-vector-cache",
    "GOV_W2_56_ANY": f"{MARK}-any-gov",
    "PYTHONPATH": None,  # the launcher's own (it needs it to import gov), with a planted entry added
}
# Names the launcher sets itself, from its own values: present, never with the parent's value.
LAUNCHER_OWNED = {"CLAUDE_CODE_TMPDIR", "GOV_ROLE", "GOV_TICKET"}


def parent_value(name: str) -> str:
    if name == "PYTHONPATH":
        return os.pathsep.join([python_path(), f"/tmp/{MARK}-pythonpath"])
    return PARENT_VARIABLES[name]


def leaks(env: dict, planted: dict) -> list[str]:
    """The parent's planted values that reached ``env`` (a process environment or the settings' ``env``)."""
    found = []
    for name, value in planted.items():
        if name not in env:
            continue
        if name == "PYTHONPATH":
            found.append(f"PYTHONPATH={env[name]!r}")
        elif name in LAUNCHER_OWNED:
            if env[name] == value:
                found.append(f"{name}={env[name]!r} (the parent's value)")
        else:
            found.append(f"{name}={env[name]!r}")
    for name, value in env.items():
        if MARK in str(value) and not any(f"{name}=" in entry for entry in found):
            found.append(f"{name}={value!r} (holds the parent's mark)")
    return found


# --------------------------------------------------------------------------
# The placeholders (KPI S4)
# --------------------------------------------------------------------------

# The names the CLI's sandbox puts a placeholder at when nothing is there (its fixed write denials: shell and git
# start-up files, editor folders, the CLI's own command and agent folders), each at the worktree's root.
SANDBOX_NAMES = (".bashrc", ".bash_profile", ".zshrc", ".zprofile", ".profile", ".gitconfig", ".gitmodules",
                 ".ripgreprc", ".mcp.json", ".vscode", ".idea", ".claude/commands", ".claude/agents")
# The names the launcher's own deny rules write literally that need not exist (launcher._runtime_rules: every
# prefix of "scratch" under .gov-runtime/): the sandbox puts a placeholder at each (DEC-402).
DENIED_NAMES = tuple(f".gov-runtime/{'scratch'[:i]}" for i in range(1, len("scratch")))
PLACEHOLDERS = SANDBOX_NAMES + DENIED_NAMES
