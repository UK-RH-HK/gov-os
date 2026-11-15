"""Support code for the W2-111 reopen's acceptance cases (DEC-1184 (3)); standard library and PyYAML only.

The interface under test is the product guard's PreToolUse hook (``template/governance/kernel/hooks/pretooluse.py``),
installed in a planted project and run the way W1-02's cases run it: ``w1_02_support.run_hook`` starts it as a process
with the call on stdin, ``GOV_ROLE`` and ``GOV_TICKET`` in a fresh environment, the session's own ``PATH`` inherited,
and reads its decision and the CPU time of the hook and the processes it waited for (``RUSAGE_CHILDREN``).

The measure is W1-02's (``test_w1_02_guard_hook.py::test_decision_p95_is_under_100_ms``, DEC-979, DEC-1163 (3)),
unchanged: 3 warm-up calls; rounds of 40 timed calls, each with a reference hook (a fresh interpreter that reads the
event and answers) timed just before it; the round's figure is the nearest-rank p95 of the 40 calls' CPU times less
the median of the 40 reference CPU times; the bound 100 ms at p95; a round that misses repeats, up to three rounds.
The reference hook is written here, in the same text as W1-02's, rather than imported from that test file, so that
these cases do not move if that file is revised.

Two worlds, both planted under pytest's temporary folders:

- ``bash_world``: W1-02's fixture project (``w1_02_support.make_project``) as it is, the engineer on its ticket;
- ``trees_world``: a small repository with 150 worktrees registered (``git worktree add``), the product hook and the
  kernel template's path map committed in it, and in the map one planted evaluation set whose hidden part
  (``eval/memory/hidden/**``) measures the engineer. Every tree holds the hidden part (it is committed).
"""

from __future__ import annotations

import os
import resource
import shlex
import shutil
import statistics
import subprocess
import sys
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
W1_02_DIR = HERE.parent / "W1-02"
if str(W1_02_DIR) not in sys.path:
    sys.path.insert(0, str(W1_02_DIR))

import w1_02_support as guard  # noqa: E402

REPO_ROOT = guard.REPO_ROOT

# --------------------------------------------------------------------------
# The measure: W1-02's, unchanged
# --------------------------------------------------------------------------

BOUND_S = 0.100
SAMPLES = 40
WARM_UP = 3
ROUNDS = 3

REFERENCE_HOOK = (
    "import json, sys\n"
    "json.load(sys.stdin)\n"
    "print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': 'allow'}}))\n"
)


def reference_cpu_seconds():
    """CPU time (user and system) of one call of the reference hook: ``RUSAGE_CHILDREN`` before and after it."""
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    subprocess.run([sys.executable, "-c", REFERENCE_HOOK], input="{}", capture_output=True, text=True, check=True)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    return (after.ru_utime + after.ru_stime) - (before.ru_utime + before.ru_stime)


def path_entries():
    """How many entries the session's PATH has (the hook inherits it, as a real session's hook does)."""
    return len([d for d in os.environ.get("PATH", "").split(os.pathsep) if d])


@dataclass
class Measure:
    """One case's rounds: the judged figure of each, and beside it the raw CPU p95, the reference median, the wall
    p95 and the 1-minute load at the round's end."""
    label: str
    trees: int
    judged: list = field(default_factory=list)
    figures: list = field(default_factory=list)

    @property
    def passed(self):
        return min(self.judged) < BOUND_S

    def describe(self):
        def ms(values):
            return ", ".join(f"{v * 1000:.1f}" for v in values)
        return (
            f"{self.label}: p95 CPU time of the hook and its children per call, less the median CPU time of the "
            f"reference hook timed beside it, per round (ms): {ms(self.judged)}; the bound is "
            f"{BOUND_S * 1000:.0f} ms (per round, for information: raw CPU p95 {ms(f[0] for f in self.figures)}; "
            f"reference median {ms(f[1] for f in self.figures)}; wall p95 {ms(f[2] for f in self.figures)}; "
            f"load {', '.join(f'{f[3]:.1f}' for f in self.figures)}; PATH entries {path_entries()}; "
            f"trees {self.trees})"
        )


def measure(label, call, expected, trees=1):
    """W1-02's measure of ``call()`` (one hook call, a ``HookResult``), each call decided ``expected``."""
    for _ in range(WARM_UP):
        result = call()
        assert result.decision == expected, (
            f"{label}: the warm-up call was not decided as expected ({expected}): {result.describe()}")
        reference_cpu_seconds()
    out = Measure(label, trees)
    for _ in range(ROUNDS):
        samples, walls, references = [], [], []
        for _ in range(SAMPLES):
            references.append(reference_cpu_seconds())
            result = call()
            assert result.decision == expected, (
                f"{label}: the timed call was not decided as expected ({expected}): {result.describe()}")
            assert result.cpu_seconds is not None, f"{label}: the call's CPU time was not measured"
            samples.append(result.cpu_seconds)
            walls.append(result.seconds)
        out.judged.append(guard.p95(samples) - statistics.median(references))
        out.figures.append((guard.p95(samples), statistics.median(references), guard.p95(walls),
                            os.getloadavg()[0]))
        if out.judged[-1] < BOUND_S:
            break
    print(out.describe())
    return out


# --------------------------------------------------------------------------
# The planted 150 ms hook (failure-5)
# --------------------------------------------------------------------------

PLANT_CPU_S = 0.150
PRODUCT_COPY = "w2_111_product_pretooluse.py"
SLOW_HOOK = '''#!/usr/bin/env python3
"""W2-111's planted slow hook: 150 ms of its own CPU work per call (a busy loop, not a sleep), then the product
hook's own answer, run from its copy beside this file."""
import runpy
import sys
import time

_UNTIL = time.process_time() + {plant!r}
while time.process_time() < _UNTIL:
    pass
sys.argv[0] = {product!r}
runpy.run_path({product!r}, run_name="__main__")
'''


@contextmanager
def slow_hook(project):
    """Put the planted 150 ms hook in place of the product hook installed in ``project``; put it back after."""
    installed = Path(project) / guard.installed_hook_rel()
    product = installed.with_name(PRODUCT_COPY)
    shutil.copy2(installed, product)
    original = installed.read_bytes()
    try:
        installed.write_text(SLOW_HOOK.format(plant=PLANT_CPU_S, product=str(product)), encoding="utf-8")
        yield installed
    finally:
        installed.write_bytes(original)
        product.unlink()


# --------------------------------------------------------------------------
# The worlds
# --------------------------------------------------------------------------

@dataclass
class World:
    project: Path               # the session's project: CLAUDE_PROJECT_DIR, cwd and the hook's folder
    sandbox: guard.Sandbox
    role: str
    ticket: str
    trees: list = field(default_factory=list)   # [main tree, worktrees in the order git lists them]
    above: Path | None = None   # the folder that holds every worktree

    def call(self, tool, tool_input, role="session", ticket="session", project=None):
        role = self.role if role == "session" else role
        ticket = self.ticket if ticket == "session" else ticket
        return guard.run_hook(project or self.project, tool, tool_input, self.sandbox, role=role, ticket=ticket)

    def read(self, path, **kw):
        return self.call("Read", {"file_path": str(path)}, **kw)

    def write(self, path, **kw):
        return self.call("Write", guard.edit_tool_input("Write", path), **kw)

    def bash(self, command, **kw):
        return self.call("Bash", guard.bash_tool_input(command), **kw)


def bash_world(base):
    """W1-02's fixture project, the engineer on its ticket (``DAEO-zz90``, allowed ``src/gov/guard/**``)."""
    base = Path(base)
    project = guard.make_project(base / "project")
    return World(project, guard.make_sandbox(base / "sandbox"), guard.ENGINEER, guard.TICKET_ID, [project])


PATH_MAP_REL = "governance/project/path-map.yaml"
TREE_COUNT = 150
TREES_TICKET = "DAEO-zz11"
TREES_WBS = "W2-911"
TREES_ALLOWED = ("src/app/**",)
EVAL_SET = "w2-111-planted-set"
HIDDEN_FOLDER = "eval/memory/hidden"
HIDDEN_FILE = f"{HIDDEN_FOLDER}/answers.yaml"
VISIBLE_FILE = "eval/memory/visible/questions.yaml"
WORD = "zqxw111"
HIDDEN_WORD = "zqxw111hiddenanswer"
LINK_NAME = "peek"   # an untracked link in the main tree to the last-listed tree's hidden folder


def path_map_text():
    """The kernel template's path map with one planted evaluation set (W2-58's and W2-84's form)."""
    document = yaml.safe_load((REPO_ROOT / "template/governance/project/path-map.yaml").read_text(encoding="utf-8"))
    document["evaluation_sets"] = {EVAL_SET: {
        "visible": ["eval/memory/visible/**"],
        "hidden": [f"{HIDDEN_FOLDER}/**"],
        "measures": {"roles": [guard.ENGINEER]},
    }}
    return yaml.safe_dump(document, sort_keys=False)


def trees_world(base, count=TREE_COUNT):
    """A planted repository with ``count`` worktrees registered; the engineer's session runs in its main tree."""
    base = Path(base).resolve()
    sandbox = guard.make_sandbox(base / "sandbox")
    repo = sandbox.home / "repo"
    above = sandbox.home / "gov-os-worktrees"
    files = {
        "README.md": f"# W2-111 planted repository {WORD}\n",
        ".gitignore": ".gov-runtime/\n__pycache__/\n",
        "src/app/main.py": f"VALUE = 1  # {WORD}\n",
        "docs/notes.md": f"notes {WORD}\n",
        PATH_MAP_REL: path_map_text(),
        HIDDEN_FILE: f"q1: {HIDDEN_WORD}-one\nq2: {HIDDEN_WORD}-two\n",
        VISIBLE_FILE: f"- q1 {WORD}\n- q2 {WORD}\n",
        f".tickets/{TREES_TICKET}.md": guard.ticket_text(ticket_id=TREES_TICKET, wbs_id=TREES_WBS,
                                                         allowed_paths=TREES_ALLOWED),
    }
    for rel, text in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    hooks = repo / guard.PRODUCT_HOOK_DIR_REL
    hooks.mkdir(parents=True, exist_ok=True)
    for source in guard.hook_files():
        shutil.copy2(source, hooks / source.name)
    guard.git(repo, "init", "-q", "-b", "main")
    guard.git(repo, "add", "-A")
    guard.git(repo, "commit", "-q", "-m", "W2-111 planted repository")
    above.mkdir(parents=True, exist_ok=True)
    for n in range(1, count + 1):
        guard.git(repo, "worktree", "add", "-q", "--detach", str(above / f"T{n:03d}"))
    listed = [line[len("worktree "):] for line in guard.git(repo, "worktree", "list", "--porcelain").splitlines()
              if line.startswith("worktree ")]
    trees = [Path(p) for p in listed]
    assert len(trees) == count + 1, f"the planted repository lists {len(trees)} trees, not {count + 1}"
    assert trees[0] == repo, f"git lists {trees[0]} first, not the main tree"
    for tree in trees:
        assert (tree / HIDDEN_FILE).is_file(), f"the planted tree {tree} does not hold the hidden part"
    os.symlink(trees[-1] / HIDDEN_FOLDER, repo / LINK_NAME)
    return World(repo, sandbox, guard.ENGINEER, TREES_TICKET, trees, above)


def q(path):
    return shlex.quote(str(path))


# --------------------------------------------------------------------------
# The timed calls (success-5, success-6), shared with the planted-hook cases (failure-5)
# --------------------------------------------------------------------------

# success-5: the engineer's Bash calls in W1-02's project, each allowed (inside src/gov/guard/**, no install).
BASH_CALLS = {
    "plain": "ls src/gov/guard",
    "pipe": "cat src/gov/guard/decide.py | grep VALUE | wc -l",
    "redirect": "echo VALUE > src/gov/guard/w2_111_out.txt",
}

# success-6: the engineer's Read, Write and Bash calls in the main tree of the planted repository, each allowed.
TREES_CALLS = ("Read", "Write", "Bash")


def bash_call(world, name):
    return lambda: world.bash(BASH_CALLS[name])


def trees_call(world, name):
    target = world.project / "src/app/main.py"
    if name == "Read":
        return lambda: world.read(target)
    if name == "Write":
        return lambda: world.write(target)
    return lambda: world.bash("cat src/app/main.py")
