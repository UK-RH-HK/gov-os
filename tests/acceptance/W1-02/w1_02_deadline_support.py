"""Support code for the DEC-580 round of W1-02: the guard's hook program keeps its own deadline of 20 seconds.

DEC-580: "The guard's hook program keeps its own deadline of 20 seconds and
answers "refuse" when it reaches it."

Every case asks the hook, run as a process on a hook input, in a temporary
project of its own. Nothing of this repository is opened, and neither protected
file's path is typed: where a case needs one, it comes from
``w1_02_protected_support``.

**How a decision is made slow.** Never by a slow machine, never by a weaker
rule, never by a switch of the product. Three stand-ins, all placed through what
the suite already uses to reach the hook (its environment, its input, the
temporary project):

- **a stand-in for the program the hook starts** (``git``), first on the search
  path of the hook's environment. It writes its process id to a file of the
  case, may start a child of its own that does the same, sleeps for the time the
  case names, and then runs the real program with the same arguments, so that a
  step that ends gives the hook what the real program gives. Which start sleeps
  is named by its number (the first, or every one), never by its arguments.
  Every stand-in ends by itself after ``STAND_IN_ENDS_S`` at the latest;
- **a named pipe in the hook's bookkeeping folder** of the temporary project.
  The program as built opens what it finds there and waits on a pipe for ever;
  no process is involved. The folder and the counter's name are taken from the
  guard's own module, not typed;
- **an input that arrives late** on the hook's stdin, inside the bound the
  program has on reading its input.

**Side by side.** A case that waits for the deadline is slow. All hook
processes of one module are started together by ``run_side_by_side``, each in
its own project with its own stand-in, and each case asserts on one outcome
afterwards: a module waits once.

**The hook is started as the suite starts it**: as a child of the test, in the
test's own process group. A program that ended its whole group at the deadline
would end the test run.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

import w1_02_protected_support as protected
import w1_02_support as support

_SRC = str(support.REPO_ROOT / support.GOV_PACKAGE_PARENT_REL)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

# Where the hook keeps its bookkeeping for the check after a call: imported, never typed.
from gov.guard.containment import SEQ_FILE, SNAPSHOT_DIR_REL  # noqa: E402

DECISION = "DEC-580"
DEADLINE_S = 20.0
# An answer of the deadline is not there before LOWER_S and is there by UPPER_S, on the test's clock from the start of
# the hook's process to its end. The lower bound says "not at once": the slow step was waited for. The upper bound is
# the deadline and a margin for a loaded machine, a little more than the 5 s the earlier time cases of this revision
# give a decision that takes well under a second; it is far below the 60 s at which the harness gives up.
LOWER_S = 19.0
UPPER_S = 26.0
# The test's own limit on a hook process, so that a run cannot hang: a hook still running then has given no answer.
PROCESS_LIMIT_S = 32.0
# Every stand-in ends by itself after this long: well over UPPER_S, well under the harness's 60 s.
STAND_IN_ENDS_S = 40.0
# Once the hook has answered, everything it started is gone within this long.
GONE_WITHIN_S = 5.0

# A step that is slow and ends before the deadline.
SHORT_STEP_S = 4.0
# The bound the program has today on reading its input, and the window a case holds around it.
INPUT_BOUND_S = 3.0
INPUT_LOWER_S = 2.5
INPUT_UPPER_S = 8.0
# A decision reached in time is answered well before the deadline.
IN_TIME_UPPER_S = 15.0

REAL_GIT = shutil.which("git")

# Who makes a call: name -> (GOV_ROLE, GOV_TICKET).
ENGINEER = "engineer"
ORCHESTRATOR = "orchestrator"
NO_ROLE = "no-role"
ACTORS = {
    ENGINEER: (support.ENGINEER, support.TICKET_ID),
    ORCHESTRATOR: (support.ORCHESTRATOR, support.ORCHESTRATOR_TICKET_ID),
    NO_ROLE: (None, None),
}

IN_TICKET_REL = "src/gov/guard/decide.py"     # the engineer's ticket names it
OUTSIDE_TICKET_REL = "README.md"              # the engineer's ticket does not
MARKER = "w1-02-deadline-case-marker"         # a word of the call's input that no answer may carry

_STAND_IN = '''#!{python}
"""A stand-in for a program the hook starts (W1-02 acceptance, DEC-580). It ends by itself."""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "plan.json"), encoding="utf-8") as handle:
    PLAN = json.load(handle)
with open(os.path.join(HERE, "started.log"), "a", encoding="utf-8") as handle:
    handle.write(str(os.getpid()) + "\\n")
with open(os.path.join(HERE, "started.log"), encoding="utf-8") as handle:
    NUMBER = sum(1 for _ in handle)
SLEEPS = PLAN["sleeps"]
SECONDS = min(float(SLEEPS[NUMBER - 1] if NUMBER <= len(SLEEPS) else PLAN["every"]), {ends})
if SECONDS > 0 and PLAN["child"]:
    CHILD = ("import os, sys, time\\n"
             "with open(sys.argv[1], 'a') as handle:\\n"
             "    handle.write(str(os.getpid()) + '\\\\n')\\n"
             "time.sleep(float(sys.argv[2]))\\n")
    subprocess.Popen([sys.executable, "-c", CHILD, os.path.join(HERE, "children.log"), str(SECONDS)]).wait()
elif SECONDS > 0:
    time.sleep(SECONDS)
os.execv({real!r}, [{real!r}] + sys.argv[1:])
'''


# --------------------------------------------------------------------------
# One hook process of a module
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Call:
    """One hook process: the call, who makes it, and what makes its decision slow.

    ``tool_input`` is a mapping, or a function of the project that returns one.
    ``sleeps`` are the seconds the stand-in sleeps on its first, second, ...
    start; ``every`` the seconds on each later start; ``child`` lets a sleeping
    stand-in start a child of its own that does the sleeping. ``prepare`` is
    called with the project before the hook starts. ``top`` are further fields
    of the hook input; ``env`` further variables of the hook's environment.
    ``send_after`` delays the input; ``send`` is ``whole``, ``half`` (half of
    the object, the input left open) or ``nothing`` (the input left open);
    ``raw`` is an input sent as it is.
    """
    label: str
    tool_name: str
    tool_input: object
    who: str = ENGINEER
    sleeps: tuple = ()
    every: float = 0.0
    child: bool = False
    prepare: object = None
    top: dict = field(default_factory=dict)
    env: dict = field(default_factory=dict)
    send_after: float = 0.0
    send: str = "whole"
    raw: object = None


@dataclass
class Outcome:
    label: str
    project: Path
    result: support.HookResult
    stand_in_starts: int = 0     # how often the hook started the stand-in program
    children: int = 0            # how many of those stand-ins started a child of their own
    left_running: int = 0        # processes the hook started that were still there GONE_WITHIN_S after its answer
    before: tuple = ()           # the findings file's lines before the hook ran

    @property
    def answered(self):
        return self.result.decision != "timeout"

    def describe(self):
        """Decision, exit code and time: never the hook's output, which may carry what it must not."""
        result = self.result
        if not self.answered:
            return f"no answer: the hook was still running after {result.seconds:.0f} s and was ended by the case"
        return f"decision={result.decision} exit={result.returncode} after {result.seconds:.1f} s"


def bash(words="echo " + MARKER):
    return support.bash_tool_input(words)


def write_to(rel):
    return lambda project: {"file_path": str(Path(project) / rel), "content": MARKER + "\n"}


def read_of(rel):
    return lambda project: {"file_path": str(Path(project) / rel)}


def _alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    try:
        with open(f"/proc/{pid}/stat", encoding="utf-8", errors="replace") as handle:
            return handle.read().rsplit(")", 1)[1].split()[0] != "Z"
    except FileNotFoundError:
        return False
    except (OSError, IndexError):
        return True


def _pids(bin_dir):
    found = []
    for name in ("started.log", "children.log"):
        try:
            text = (bin_dir / name).read_text(encoding="utf-8")
        except OSError:
            continue
        found.extend(int(line) for line in text.split() if line.isdigit())
    return found


def _starts(bin_dir, name):
    try:
        return len((bin_dir / name).read_text(encoding="utf-8").split())
    except OSError:
        return 0


def _make_stand_in(bin_dir, call):
    bin_dir.mkdir(parents=True)
    (bin_dir / "plan.json").write_text(
        json.dumps({"sleeps": list(call.sleeps), "every": call.every, "child": call.child}), encoding="utf-8")
    program = bin_dir / "git"
    program.write_text(_STAND_IN.format(python=sys.executable, real=REAL_GIT, ends=STAND_IN_ENDS_S), encoding="utf-8")
    program.chmod(0o755)


def _stdin_text(call, project, sandbox):
    if call.raw is not None:
        return call.raw
    if call.send == "nothing":
        return ""
    tool_input = call.tool_input(project) if callable(call.tool_input) else dict(call.tool_input)
    data = support.payload(project, call.tool_name, tool_input, sandbox)
    data.update(call.top)
    text = json.dumps(data)
    return text[:len(text) // 2] if call.send == "half" else text


def _attend(call, proc, started, text, bin_dir, limit_s, slot):
    """Send the input, wait for the hook's end, then watch what it started."""
    try:
        if call.send_after:
            time.sleep(call.send_after)
        if text:
            proc.stdin.write(text.encode("utf-8"))
            proc.stdin.flush()
        if call.send == "whole" or call.raw is not None:
            proc.stdin.close()
    except OSError:
        pass
    try:
        returncode = proc.wait(timeout=max(0.1, limit_s - (time.perf_counter() - started)))
    except subprocess.TimeoutExpired:
        returncode = None
        proc.kill()
        proc.wait()
    slot["seconds"] = time.perf_counter() - started
    slot["returncode"] = returncode
    until = time.monotonic() + GONE_WITHIN_S
    alive = [pid for pid in _pids(bin_dir) if _alive(pid)]
    while alive and returncode is not None and time.monotonic() < until:
        time.sleep(0.1)
        alive = [pid for pid in _pids(bin_dir) if _alive(pid)]
    slot["left"] = len(alive)
    slot["starts"] = _starts(bin_dir, "started.log")
    slot["children"] = _starts(bin_dir, "children.log")


def _end_everything(bin_dir, project):
    """Leave nothing behind: end every stand-in process, and let go whatever waits on a named pipe."""
    for _ in range(3):
        for pid in _pids(bin_dir):
            if _alive(pid):
                try:
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    pass
        time.sleep(0.05)
    for path in pipes_in(project):
        try:
            fd = os.open(path, os.O_RDWR | os.O_NONBLOCK)
        except OSError:
            continue
        time.sleep(0.1)
        os.close(fd)


def run_side_by_side(base, calls, limit_s=PROCESS_LIMIT_S):
    """Start one hook process per call, all together; return ``{label: Outcome}`` when every one has ended.

    Each call gets a project, a sandbox and a stand-in of its own under
    ``base``. A hook still running at ``limit_s`` is ended and has no answer.
    Nothing a call started is left running when this returns.
    """
    base = Path(base)
    running = []
    for call in calls:
        home = base / call.label
        sandbox = support.make_sandbox(home / "sandbox")
        project = support.make_project(home / "project")
        bin_dir = home / "bin"
        _make_stand_in(bin_dir, call)
        if call.prepare is not None:
            call.prepare(project)
        role, ticket = ACTORS[call.who]
        env = support.hook_environment(project, sandbox, role, ticket, call.env)
        env["PATH"] = str(bin_dir) + os.pathsep + env["PATH"]
        text = _stdin_text(call, project, sandbox)
        before = tuple(support.findings(project))
        out, err = home / "stdout.txt", home / "stderr.txt"
        # The hook's output goes to files: a process the hook leaves behind cannot hold the case on a pipe.
        with open(out, "wb") as out_handle, open(err, "wb") as err_handle:
            started = time.perf_counter()
            proc = subprocess.Popen(support._argv(project / support.installed_hook_rel()), stdin=subprocess.PIPE,
                                    stdout=out_handle, stderr=err_handle, cwd=str(project), env=env)
        slot = {}
        thread = threading.Thread(target=_attend, args=(call, proc, started, text, bin_dir, limit_s, slot),
                                  daemon=True)
        thread.start()
        running.append((call, project, bin_dir, proc, thread, slot, out, err, before))

    outcomes = {}
    for call, project, bin_dir, proc, thread, slot, out, err, before in running:
        thread.join()
        try:
            proc.stdin.close()
        except OSError:
            pass
        _end_everything(bin_dir, project)
        stdout = out.read_text(encoding="utf-8", errors="replace")
        stderr = err.read_text(encoding="utf-8", errors="replace")
        returncode = slot["returncode"]
        decision = "timeout" if returncode is None else support.classify(returncode, stdout)
        result = support.HookResult(decision, returncode, stdout, stderr, slot["seconds"])
        outcomes[call.label] = Outcome(call.label, project, result, slot["starts"], slot["children"],
                                       slot["left"], before)
    return outcomes


# --------------------------------------------------------------------------
# What makes a decision slow, in the temporary project
# --------------------------------------------------------------------------

def pipes_in(project):
    folder = Path(project) / SNAPSHOT_DIR_REL
    try:
        return [str(path) for path in folder.iterdir() if path.is_fifo()]
    except OSError:
        return []


def a_pipe_among_the_pending_calls(project):
    """The bookkeeping before the decision: the hook looks through the calls that are pending, and one is a pipe."""
    folder = Path(project) / SNAPSHOT_DIR_REL
    folder.mkdir(parents=True, exist_ok=True)
    os.mkfifo(folder / "toolu_w1_02_deadline_pending.json")


def a_pipe_at_the_counter(project):
    """The bookkeeping after the rules have allowed the call: the hook counts the call, and the counter is a pipe."""
    folder = Path(project) / SNAPSHOT_DIR_REL
    folder.mkdir(parents=True, exist_ok=True)
    os.mkfifo(folder / SEQ_FILE)


def pending_entries(project):
    """What the hook has noted for the check after a call: the names in its folder that carry the call's id."""
    folder = Path(project) / SNAPSHOT_DIR_REL
    try:
        return sorted(path.name for path in folder.iterdir() if "toolu_w1_02_acceptance" in path.name)
    except OSError:
        return []


# --------------------------------------------------------------------------
# Names like a time limit (point 4)
# --------------------------------------------------------------------------

# The names a reader would guess for a variable that sets the deadline, and for one that switches it off.
LIMIT_VARIABLES = (
    "GOV_GUARD_DEADLINE_S", "GOV_GUARD_DEADLINE", "GOV_GUARD_TIMEOUT_S", "GOV_GUARD_TIMEOUT",
    "GOV_HOOK_DEADLINE_S", "GOV_HOOK_DEADLINE", "GOV_HOOK_TIMEOUT_S", "GOV_HOOK_TIMEOUT",
    "GOV_PRETOOLUSE_DEADLINE_S", "GOV_PRETOOLUSE_TIMEOUT_S", "GOV_DECISION_DEADLINE_S", "GOV_DECISION_TIMEOUT_S",
    "GOV_DEADLINE_S", "GOV_DEADLINE", "GOV_TIMEOUT_S", "GOV_TIMEOUT", "GOV_PENDING_SNAPSHOT_TIMEOUT_S",
    "GUARD_DEADLINE_S", "GUARD_TIMEOUT_S", "HOOK_DEADLINE_S", "HOOK_TIMEOUT_S", "HOOK_TIMEOUT", "DEADLINE_S",
    "DECISION_DEADLINE_S", "STDIN_DEADLINE_S", "CLAUDE_HOOK_TIMEOUT", "CLAUDE_CODE_HOOK_TIMEOUT", "TIMEOUT", "TMOUT",
)
SWITCH_VARIABLES = (
    "GOV_GUARD_NO_DEADLINE", "GOV_GUARD_DEADLINE_OFF", "GOV_GUARD_DISABLE_DEADLINE", "GOV_GUARD_NO_TIMEOUT",
    "GOV_NO_DEADLINE", "GOV_NO_TIMEOUT", "GOV_HOOK_NO_DEADLINE", "GOV_TEST_MODE", "GOV_TESTING",
)
LARGE = 600
TINY = 0.001


def limit_environment(value, switch="1"):
    env = {name: value for name in LIMIT_VARIABLES}
    env.update({name: switch for name in SWITCH_VARIABLES})
    return env


def limit_fields(value):
    """Fields named like a time limit, as a hook input or a tool input might carry them."""
    return {
        "timeout": value, "timeout_s": value, "timeout_ms": value * 1000, "deadline": value, "deadline_s": value,
        "time_limit": value, "guard_deadline_s": value, "hook_timeout": value, "no_deadline": True,
    }


# Files a worker may write: under its scratch folder, and in the paths of the engineer's ticket.
LIMIT_FILES = (
    f"{support.SCRATCH_REL}/guard.json", f"{support.SCRATCH_REL}/deadline.json", f"{support.SCRATCH_REL}/gov.json",
    f"{support.SCRATCH_REL}/guard.toml", f"{support.SCRATCH_REL}/deadline", f"{support.SCRATCH_REL}/guard-deadline",
    "src/gov/guard/deadline.json", "src/gov/guard/guard.json", "src/gov/guard/config.json",
    "src/gov/guard/guard.toml", "src/gov/guard/deadline", "pyproject.toml",
)


def files_that_name_a_limit(value):
    """``prepare``: every file of ``LIMIT_FILES`` names ``value`` as the limit, in the form its name suggests."""

    def prepare(project):
        fields = limit_fields(value)
        table = "".join(f"{key} = {json.dumps(item)}\n" for key, item in fields.items())
        for rel in LIMIT_FILES:
            path = Path(project) / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            if rel.endswith(".json"):
                path.write_text(json.dumps({**fields, "guard": fields, "hook": fields}) + "\n", encoding="utf-8")
            elif rel == "pyproject.toml":
                path.write_text(support.PROJECT_FILES[rel] + "\n[tool.gov]\n" + table + "\n[tool.gov.guard]\n" + table
                                + "\n[tool.gov.hooks]\n" + table, encoding="utf-8")
            elif rel.endswith(".toml"):
                path.write_text(table + "\n[guard]\n" + table + "\n[hook]\n" + table, encoding="utf-8")
            else:
                path.write_text(f"{value}\n", encoding="utf-8")

    return prepare


# --------------------------------------------------------------------------
# Assertions
# --------------------------------------------------------------------------

_IN_TIME_RE = re.compile(r"(?i)\b(in time|deadline|time limit|too long|timed? ?out)")


def said(outcome):
    """Everything the hook wrote."""
    return outcome.result.stdout + "\n" + outcome.result.stderr


def refusal_of(outcome):
    """The hook's answer when it is a refusal in the form a rule's refusal has today, else ``None``.

    The form (from the program as built and the suite's classifier): exit code 0
    and one JSON object on stdout whose ``hookSpecificOutput`` names the event
    ``PreToolUse``, the decision ``deny`` and a reason.
    """
    result = outcome.result
    if result.returncode != 0:
        return None
    try:
        specific = json.loads(result.stdout)["hookSpecificOutput"]
    except (ValueError, KeyError, TypeError):
        return None
    if not isinstance(specific, dict) or specific.get("hookEventName") != "PreToolUse":
        return None
    reason = specific.get("permissionDecisionReason")
    if specific.get("permissionDecision") != "deny" or not isinstance(reason, str) or not reason.strip():
        return None
    return reason


def assert_refused_at_the_deadline(outcome, what):
    """A refusal in a rule's form, whose reason says the guard could not decide in time and names DEC-580."""
    assert outcome.answered, f"{what}: {outcome.describe()}; the guard keeps no deadline of its own"
    reason = refusal_of(outcome)
    assert reason is not None, (
        f"{what} was not refused in the form a refusal has (exit code 0, a deny decision with a reason): "
        f"{outcome.describe()}"
    )
    assert DECISION in reason, f"the refusal of {what} does not name {DECISION}: {outcome.describe()}"
    assert _IN_TIME_RE.search(reason), (
        f"the refusal of {what} names {DECISION} and does not say that the guard could not decide in time"
    )


def assert_within_the_deadline_s_window(outcome, what):
    assert outcome.answered, f"{what}: {outcome.describe()}"
    seconds = outcome.result.seconds
    assert seconds >= LOWER_S, (
        f"{what} was answered after {seconds:.1f} s: before the deadline of {DEADLINE_S:.0f} s (not before "
        f"{LOWER_S:.0f} s)"
    )
    assert seconds <= UPPER_S, (
        f"{what} was answered after {seconds:.1f} s: the deadline is {DEADLINE_S:.0f} s and the answer is due by "
        f"{UPPER_S:.0f} s"
    )


def assert_not_the_deadline_s_answer(outcome, what):
    assert DECISION not in said(outcome), f"{what} was answered with the deadline's answer ({DECISION})"


def secrets_of(outcome):
    """What no answer of the deadline may carry: the call's own words, its paths, and either protected file's path."""
    held = protected.HELD_REL
    return (MARKER, str(outcome.project), IN_TICKET_REL, OUTSIDE_TICKET_REL, protected.SETTINGS_REL, held,
            os.path.basename(held), os.path.dirname(held), "echo ")


def new_findings(outcome):
    """The lines the hook added to the findings file."""
    after = support.findings(outcome.project)
    return after[len(outcome.before):]
