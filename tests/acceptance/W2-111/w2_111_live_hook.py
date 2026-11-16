"""Support for W2-111's S9 and S10 on the live hook's patched copy, judged by DEC-1187 (1)'s own target (every case
within 100 ms at p95, paired against the applied ACT-GUARD-FIX-6 hook, decisions unchanged, the measured drop recorded;
S9 amended by P-W2-111-S9-DROP (a), DEC-1157 (12): the 30 ms drop is no longer judged); standard library only.

The interface (the ticket's S9 and S10 lines): the engineer's diff, ``docs/changes/W2-111-live-hook/live-hook.diff``,
a git-style diff of ``.claude/hooks/`` (paths ``a/.claude/hooks/...``, ``b/...``) against the applied ACT-GUARD-FIX-6
bytes, which applies with ``git apply`` to a clean copy of the tree's ``.claude/hooks/``. The diff is used here by its
path, at run time; the test designer never opened it.

Two copies under pytest's temporary folder: **before** (the tree's ``.claude/hooks/`` as it is, its hashes checked
against ACT-GUARD-FIX-6's) and **after** (the same with the diff applied by ``git apply``). Each is run as
``.claude/settings.json``'s PreToolUse command runs the live hook: ``sh`` starts the pinned interpreter (the first line
of ``$HOME/.local/bin/gov``, else of the real home's ``.local/bin/gov`` from the password database, else of the ``gov``
on ``PATH``) with ``-E`` and the hook file, here the copy's; ``CLAUDE_PROJECT_DIR`` and the working folder are the
repository root the tests run in (its real config, tickets and registered worktrees: "on the live repository"); the
guard's call log goes to the temporary folder (``GOV_GUARD_CALLS_DIR``), as ``measure.py`` does.

The measure is W2-111's (``~/gov-os-runs/W2-111/gf6-measure/measure.py``, the 15 revised cases, DEC-979, DEC-1163
(3)): per call, the CPU time of the hook's process and its children (``RUSAGE_CHILDREN`` before and after the one
call), less the median CPU time of a reference hook timed beside it; nearest-rank p95 over 40 calls after 3 warm-up
calls; a round over the bound repeated, up to 3 rounds. Here the before and after copies are timed **paired in the
same run**: each of the 40 samples times a reference and the before copy, and a reference and the after copy, in
alternating order.
"""

from __future__ import annotations

import hashlib
import json
import os
import pwd
import shutil
import statistics
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

import w2_111_support as support

guard = support.guard
REPO_ROOT = support.REPO_ROOT

LIVE_HOOKS_REL = ".claude/hooks"
HOOK_NAME = "pretooluse.py"
DIFF_REL = "docs/changes/W2-111-live-hook/live-hook.diff"
BEFORE_SHA256_PREFIX = {"pretooluse.py": "9b4228ea095a", "bash_writes.py": "f03f9ac3e431"}   # ACT-GUARD-FIX-6

BOUND_S = support.BOUND_S          # 100 ms at p95 (S9 and S10: DEC-1187 (1)'s target; the drop is recorded, not judged)
SAMPLES, WARM_UP, ROUNDS = support.SAMPLES, support.WARM_UP, support.ROUNDS
TICKET = "DAEO-qvff"
CTO_TICKET = "DAEO-sdxk"
ENG, TD, ORC, AUD = guard.ENGINEER, guard.TEST_DESIGNER, guard.ORCHESTRATOR, guard.AUDITOR

# --------------------------------------------------------------------------------------------------------------------
# measure.py's 20 cases, in its order: the first 15 are the mapped W1-05, W1-02 and W2-57 cases, the last 5 the Bash
# cases. Each: (name, tool, input builder (repo root, scratch folder), role, ticket, the decision measure.py recorded).
# --------------------------------------------------------------------------------------------------------------------


def _r(root, rel):
    return str(Path(root) / rel)


CASES = [
    ("W1-05 Edit-engineer", "Edit",
     lambda r, s: {"file_path": f"{s}/source.py", "old_string": "a", "new_string": "b"}, ENG, TICKET, "allow"),
    ("W1-05 Glob-engineer", "Glob", lambda r, s: {"pattern": "**/*.py", "path": _r(r, "src")}, ENG, TICKET, "allow"),
    ("W1-05 Glob-no-role", "Glob", lambda r, s: {"pattern": "**/*.py", "path": _r(r, "src")}, None, None, "allow"),
    ("W1-05 Grep-engineer", "Grep", lambda r, s: {"pattern": "guard", "path": _r(r, "src")}, ENG, TICKET, "allow"),
    ("W1-05 Grep-no-role", "Grep", lambda r, s: {"pattern": "guard", "path": _r(r, "src")}, None, None, "allow"),
    ("W1-05 NotebookEdit-engineer", "NotebookEdit",
     lambda r, s: {"notebook_path": f"{s}/notes.ipynb", "new_source": "print('e')", "cell_type": "code",
                   "edit_mode": "insert"}, ENG, TICKET, "allow"),
    ("W1-05 Read-engineer", "Read", lambda r, s: {"file_path": _r(r, "README.md")}, ENG, TICKET, "allow"),
    ("W1-05 Read-no-role", "Read", lambda r, s: {"file_path": _r(r, "README.md")}, None, None, "allow"),
    ("W1-05 Write-engineer", "Write", lambda r, s: {"file_path": f"{s}/source.py", "content": "x = 1\n"},
     ENG, TICKET, "allow"),
    ("W1-02 no-role Write (scratch)", "Write", lambda r, s: {"file_path": f"{s}/decide.py", "content": "x\n"},
     None, None, "allow"),
    ("W1-02 engineer Write src (allow)", "Write",
     lambda r, s: {"file_path": _r(r, "src/gov/guard/decide.py"), "content": "x\n"}, ENG, TICKET, "allow"),
    ("W1-02 engineer Write acceptance (deny r1)", "Write",
     lambda r, s: {"file_path": _r(r, "tests/acceptance/W2-111/test_fixture.py"), "content": "x\n"},
     ENG, TICKET, "deny"),
    ("W1-02 test-designer Write acceptance", "Write",
     lambda r, s: {"file_path": _r(r, "tests/acceptance/W2-111/test_fixture.py"), "content": "x\n"},
     TD, TICKET, "allow"),
    ("W1-02 auditor Write src (deny r5)", "Write",
     lambda r, s: {"file_path": _r(r, "src/gov/guard/decide.py"), "content": "x\n"}, AUD, TICKET, "deny"),
    ("W2-57 test-designer Read ordinary", "Read", lambda r, s: {"file_path": _r(r, "README.md")}, TD, TICKET, "allow"),
    ("Bash ls (engineer)", "Bash", lambda r, s: {"command": "ls", "description": "list"}, ENG, TICKET, "allow"),
    ("Bash pipeline (engineer)", "Bash",
     lambda r, s: {"command": "ls -la src | grep -v pyc | sort | head -5", "description": "p"}, ENG, TICKET, "allow"),
    ("Bash write to scratch (engineer)", "Bash",
     lambda r, s: {"command": f"mkdir -p {s}/b && echo hi > {s}/b/f.txt", "description": "w"}, ENG, TICKET, "allow"),
    ("Bash git status (CTO)", "Bash",
     lambda r, s: {"command": "git status --short | head", "description": "g"}, ORC, CTO_TICKET, "allow"),
    ("Bash grep|wc (test-designer)", "Bash",
     lambda r, s: {"command": "grep -rn guard src | wc -l", "description": "c"}, TD, TICKET, "allow"),
]
MAPPED = 15
NAMES = [c[0] for c in CASES]
assert len(CASES) == 20


def case_id(name):
    """A pytest id for a case name (letters, digits and dashes)."""
    out = "".join(ch if ch.isalnum() else "-" for ch in name)
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")


# --------------------------------------------------------------------------------------------------------------------
# The copies
# --------------------------------------------------------------------------------------------------------------------

class LiveHookUnavailable(AssertionError):
    """The copies or the interpreter cannot be set up: the case fails with this reason."""


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _copy_hooks(dest_root):
    source = REPO_ROOT / LIVE_HOOKS_REL
    if not source.is_dir():
        raise LiveHookUnavailable(f"the tree has no {LIVE_HOOKS_REL}/ to copy")
    dest = Path(dest_root) / LIVE_HOOKS_REL
    shutil.copytree(source, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return dest


def _git(where, *args):
    return subprocess.run(["git", "-C", str(where), "-c", "core.hooksPath=/dev/null", *args],
                          capture_output=True, text=True, check=False)


@dataclass
class Copies:
    before: Path    # the before copy's pretooluse.py
    after: Path     # the after copy's pretooluse.py
    after_root: Path


def make_copies(base):
    """The before and after copies under ``base``; ``LiveHookUnavailable`` names what is missing."""
    base = Path(base)
    before_hooks = _copy_hooks(base / "before")
    for name, prefix in BEFORE_SHA256_PREFIX.items():
        path = before_hooks / name
        if not path.is_file():
            raise LiveHookUnavailable(f"the before copy has no {LIVE_HOOKS_REL}/{name}")
        digest = _sha256(path)
        if not digest.startswith(prefix):
            raise LiveHookUnavailable(
                f"the tree's {LIVE_HOOKS_REL}/{name} is not ACT-GUARD-FIX-6's bytes (sha256 {digest[:12]}, expected "
                f"{prefix}): the diff is judged against the applied ACT-GUARD-FIX-6 hook")
    diff = REPO_ROOT / DIFF_REL
    if not diff.is_file():
        raise LiveHookUnavailable(
            f"the live hook's diff {DIFF_REL} is absent: S10's diff of {LIVE_HOOKS_REL}/ against the applied "
            "ACT-GUARD-FIX-6 bytes is not prepared")
    after_root = base / "after"
    after_hooks = _copy_hooks(after_root)
    init = _git(after_root, "init", "-q")
    if init.returncode != 0:
        raise LiveHookUnavailable(f"git init of the after copy failed: {init.stderr.strip()}")
    listed = _git(after_root, "apply", "--numstat", str(diff))
    if listed.returncode != 0:
        raise LiveHookUnavailable(f"the diff {DIFF_REL} cannot be read by git apply: {listed.stderr.strip()}")
    paths = [line.split("\t", 2)[2] for line in listed.stdout.splitlines() if line.count("\t") >= 2]
    if not paths:
        raise LiveHookUnavailable(f"the diff {DIFF_REL} changes no file")
    outside = [p for p in paths if not p.startswith(LIVE_HOOKS_REL + "/")]
    if outside:
        raise LiveHookUnavailable(f"the diff {DIFF_REL} changes paths outside {LIVE_HOOKS_REL}/: {outside}")
    applied = _git(after_root, "apply", str(diff))
    if applied.returncode != 0:
        raise LiveHookUnavailable(
            f"the diff {DIFF_REL} does not apply to a clean copy of the tree's {LIVE_HOOKS_REL}/: "
            f"{applied.stderr.strip()}")
    after = after_hooks / HOOK_NAME
    if not after.is_file():
        raise LiveHookUnavailable(f"the after copy has no {LIVE_HOOKS_REL}/{HOOK_NAME}")
    return Copies(before_hooks / HOOK_NAME, after, after_root)


# --------------------------------------------------------------------------------------------------------------------
# The planted 150 ms hook (failure-5), in place of a copy's pretooluse.py
# --------------------------------------------------------------------------------------------------------------------

PLANTED_COPY = "w2_111_live_pretooluse.py"


def plant_slow_hook(copies, base):
    """A copy of the after copy whose ``pretooluse.py`` is the planted hook: 150 ms of its own CPU work per call (a
    busy loop on ``time.process_time()``, not a sleep), then the after copy's own hook, run beside it as
    ``__main__`` (``w2_111_support.SLOW_HOOK``, as ``test_w2_111_slow_hook.py`` plants it)."""
    dest = Path(base) / LIVE_HOOKS_REL
    shutil.copytree(copies.after.parent, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    product = dest / PLANTED_COPY
    (dest / HOOK_NAME).rename(product)
    (dest / HOOK_NAME).write_text(support.SLOW_HOOK.format(plant=support.PLANT_CPU_S, product=str(product)),
                                  encoding="utf-8")
    return dest / HOOK_NAME


# --------------------------------------------------------------------------------------------------------------------
# One call, as settings.json's PreToolUse command runs the hook
# --------------------------------------------------------------------------------------------------------------------

def pinned_interpreter():
    """The interpreter settings.json's command runs the hook with: the first line of ``$HOME/.local/bin/gov`` (its
    ``#!`` taken off), else of the real home's (the password database's: the whole-folder run sets ``HOME`` to an
    empty folder; used for the interpreter only), else of the ``gov`` on ``PATH``; it must be executable."""
    candidates = [Path(os.environ.get("HOME", "/nonexistent")) / ".local/bin/gov",
                  Path(pwd.getpwuid(os.getuid()).pw_dir) / ".local/bin/gov"]
    gov = next((c for c in candidates if c.is_file()), None)
    if gov is None:
        found = shutil.which("gov")
        gov = Path(found) if found else None
    if gov is None:
        raise LiveHookUnavailable("no pinned gov at $HOME/.local/bin/gov, the real home's, or on PATH")
    with open(gov, encoding="utf-8", errors="replace") as f:
        first = f.readline().strip()
    interpreter = first[2:] if first.startswith("#!") else first
    if not interpreter or not os.access(interpreter, os.X_OK):
        raise LiveHookUnavailable(f"{gov} names no interpreter that runs: {interpreter!r}")
    return interpreter


@dataclass(frozen=True)
class Call:
    name: str
    tool: str
    tool_input: dict
    role: str | None
    ticket: str | None
    recorded: str      # the decision measure.py recorded for the applied ACT-GUARD-FIX-6 hook


def calls(scratch):
    scratch = Path(scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    return {name: Call(name, tool, build(str(REPO_ROOT), str(scratch)), role, ticket, recorded)
            for name, tool, build, role, ticket, recorded in CASES}


@dataclass
class Runner:
    interpreter: str
    tmp: Path
    log: Path

    def environment(self, role, ticket):
        env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
               "HOME": os.environ.get("HOME", str(self.tmp)), "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
               "TZ": "UTC", "TMPDIR": str(self.tmp), "CLAUDE_PROJECT_DIR": str(REPO_ROOT),
               "PYTHONDONTWRITEBYTECODE": "1", "GOV_GUARD_CALLS_DIR": str(self.log)}
        if role:
            env["GOV_ROLE"] = role
        if ticket:
            env["GOV_TICKET"] = ticket
        return env

    def run(self, hook, call):
        """One call of ``hook``; (decision, CPU seconds of the hook and its children, wall seconds, output)."""
        payload = json.dumps({"session_id": "w2-111-live-hook", "cwd": str(REPO_ROOT),
                              "hook_event_name": "PreToolUse", "tool_name": call.tool, "tool_input": call.tool_input,
                              "permission_mode": "default", "tool_use_id": "toolu_w2_111_live"})
        before = guard.children_cpu_seconds()
        started = time.perf_counter()
        proc = subprocess.run(["sh", "-c", '"$0" -E "$1"', self.interpreter, str(hook)], input=payload,
                              capture_output=True, text=True, cwd=str(REPO_ROOT),
                              env=self.environment(call.role, call.ticket), timeout=60, check=False)
        wall = time.perf_counter() - started
        cpu = guard.children_cpu_seconds() - before
        return guard.classify(proc.returncode, proc.stdout), cpu, wall, (proc.stderr or proc.stdout).strip()[:300]


def make_runner(base):
    base = Path(base)
    for sub in ("tmp", "calls"):
        (base / sub).mkdir(parents=True, exist_ok=True)
    return Runner(pinned_interpreter(), base / "tmp", base / "calls")


# --------------------------------------------------------------------------------------------------------------------
# The paired measure
# --------------------------------------------------------------------------------------------------------------------

@dataclass
class Paired:
    name: str
    mapped: bool    # one of the 15 mapped W1-05, W1-02 and W2-57 cases (else a Bash case); judged alike, reported
    rounds: list = field(default_factory=list)   # (before judged, after judged, before wall p95, after wall p95, load)
    decisions: set = field(default_factory=set)  # {(before decision, after decision)}

    def round_passes(self, r):
        """DEC-1187 (1)'s target: the after figure under the bound (the decisions are asserted call by call). The drop
        (before less after) is recorded, never judged: P-W2-111-S9-DROP (a) removed S9's 30 ms clause."""
        return r[1] < BOUND_S

    @property
    def passed(self):
        return any(self.round_passes(r) for r in self.rounds)

    def describe(self):
        def ms(i):
            return ", ".join(f"{r[i] * 1000:.1f}" for r in self.rounds)
        kind = "mapped" if self.mapped else "Bash"
        verdict = "PASS" if self.passed else "FAIL"
        return (f"{verdict} {self.name} ({kind}): p95 CPU time of the hook and its children per call less the median "
                f"CPU time of the reference hook timed beside it, per round (ms): before {ms(0)}; after {ms(1)}; "
                f"drop (recorded, not judged) {', '.join(f'{(r[0] - r[1]) * 1000:.1f}' for r in self.rounds)}; the "
                f"judgement: after under {BOUND_S * 1000:.0f} ms in one round, every decision the same in both copies "
                f"(for information: wall p95 before {ms(2)}, after {ms(3)}; load "
                f"{', '.join(f'{r[4]:.1f}' for r in self.rounds)}; decisions {sorted(self.decisions)})")


def measure_paired(runner, call, before_hook, after_hook, mapped):
    """W2-111's measure of one case, the before and after copies paired sample by sample."""
    out = Paired(call.name, mapped)

    def sample(hook):
        reference = support.reference_cpu_seconds()
        decision, cpu, wall, message = runner.run(hook, call)
        return decision, cpu, reference, wall, message

    def pair(k):
        order = (("before", before_hook), ("after", after_hook))
        if k % 2:
            order = order[::-1]
        got = {side: sample(hook) for side, hook in order}
        b, a = got["before"], got["after"]
        out.decisions.add((b[0], a[0]))
        assert a[0] == b[0], (
            f"{call.name}: the after copy decided {a[0]}, the before copy {b[0]} (a decision changed by the "
            f"speed-up): before {b[4]!r}; after {a[4]!r}")
        assert b[0] == call.recorded, (
            f"{call.name}: the before copy (the applied ACT-GUARD-FIX-6 hook) decided {b[0]}, not {call.recorded} as "
            f"measure.py recorded on the live repository: {b[4]!r}")
        return b, a

    for k in range(WARM_UP):
        pair(k)
    for _ in range(ROUNDS):
        bs, as_ = [], []
        for k in range(SAMPLES):
            b, a = pair(k)
            bs.append(b)
            as_.append(a)
        before = guard.p95([x[1] for x in bs]) - statistics.median([x[2] for x in bs])
        after = guard.p95([x[1] for x in as_]) - statistics.median([x[2] for x in as_])
        out.rounds.append((before, after, guard.p95([x[3] for x in bs]), guard.p95([x[3] for x in as_]),
                           os.getloadavg()[0]))
        if out.round_passes(out.rounds[-1]):
            break
    print(out.describe())
    return out


def porcelain():
    """``git status --porcelain`` of the repository the tests run in (untracked files listed one by one)."""
    proc = subprocess.run(["git", "-C", str(REPO_ROOT), "status", "--porcelain", "--untracked-files=all"],
                          capture_output=True, text=True, check=False)
    return proc.stdout
