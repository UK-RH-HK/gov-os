"""Support code for the W2-62 acceptance tests (standard library only).

W2-62 changes the session-start hook ``template/governance/kernel/hooks/sessionstart.py``
so that the RESUME HERE section of the checkpoint reaches a resumed session whole, and
the prompt it names comes from the project's roster. The tests use public interfaces only:

- the hook as Claude Code runs it: ``python3 <this worktree>/template/governance/kernel/hooks/sessionstart.py``,
  the SessionStart event's JSON object on stdin, ``CLAUDE_PROJECT_DIR``, ``GOV_ROLE`` and
  ``GOV_TICKET`` in the environment, the answer in the exit code and stdout;
- ``precompact.py`` beside it, run the same way, only to put a real generated state
  block at the end of a checkpoint (for the staleness warning);
- ``tk`` as the hook finds it on ``PATH``: a stand-in that prints a ready list the test chooses;
- the checkpoint skill and the CIT-P record, read as documents.

**The code under test (DEC-732).** Every path below is derived from this file's own
location (``Path(__file__).resolve().parents[3]`` is the repository root), so the hook
that runs is the one in the checkout the tests are in, never an installed copy. Its
``PYTHONPATH`` is this checkout's ``src/``.

**The projects.** Every test builds its own git repository from scratch under pytest's
``tmp_path``: a README, a ``.gitignore``, stand-in prompts, optionally a roster, and the
checkpoint the test writes. Nothing of this repository is copied; no checkpoint of this
repository is read.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
HOOKS_DIR = REPO_ROOT / "template" / "governance" / "kernel" / "hooks"
SESSIONSTART = HOOKS_DIR / "sessionstart.py"
PRECOMPACT = HOOKS_DIR / "precompact.py"
SKILL = REPO_ROOT / "template" / "governance" / "kernel" / "skills" / "checkpoint" / "SKILL.md"
CIT_P = REPO_ROOT / "docs" / "changes" / "W2-62-CIT-P.md"

BOUND = 10_000                       # what a SessionStart hook's additionalContext may hold and arrive whole
OLD_CUT = 9_000                      # the base's SECTION_MAX_CHARS: the cut W2-M372 removes
ORCH = ".gov-runtime/scratch/orchestrator/CHECKPOINT.md"
LEAD = ".gov-runtime/scratch/lead/CHECKPOINT.md"
ROSTER_REL = "governance/project/roster.yaml"
PROMPTS_DIR = "governance/project/prompts/"
W1_PROMPT = "governance/project/prompts/w1-orchestrator.md"
DEFAULT_PROMPT = "governance/project/prompts/w2-orchestrator.md"
OLDER = "CHECKPOINT OLDER THAN STATE BLOCK"
BLOCK_BEGIN = "<!-- GENERATED STATE BLOCK BEGIN -->"
ORCHESTRATOR = "orchestrator"
HOOK_TIMEOUT_S = 30.0
QUICK_S = 15.0                       # "well within the hook's timeout"
STALE_AGE_S = 3 * 24 * 3600.0
# Item 6: what the injection says when there is no section to name (key terms, any one of them).
SAYS_SO = ("missing", "can't be read", "cannot be read", "could not be read", "unreadable", "no resume here",
           "not found", "does not exist", "doesn't exist")

# The public interface of this ticket: `lines <first>-<last>` and `<n> characters`.
RANGE = re.compile(r"\blines (\d+)-(\d+)\b")
SIZE = re.compile(r"(?<![\d,])(\d{1,3}(?:,\d{3})+|\d+) characters\b")

PREAMBLE = (
    "# Orchestrator checkpoint (stand-in, every name invented)\n"
    "\n"
    "## Earlier log\n"
    "\n"
    "- EARLIER-LOG-MARKER merged ZQ-12\n"
    "\n"
)
HISTORY = "\n## History\n\n- HISTORY-MARKER closed ZQ-09\n"

WORDS = ("alpha bravo charlie delta echo foxtrot golf hotel india juliett kilo lima mike november oscar papa "
         "quebec romeo sierra tango uniform victor whiskey xray yankee zulu ")


# --------------------------------------------------------------------------
# Projects
# --------------------------------------------------------------------------

def git(directory, *args):
    env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
    return subprocess.run(
        ["git", "-C", str(directory), "-c", "user.name=W2-62 tests", "-c", "user.email=w2-62@example.invalid",
         "-c", "commit.gpgsign=false", *args],
        capture_output=True, text=True, check=True, env=env).stdout


def write(tree, rel, text):
    path = Path(tree) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(text, bytes):
        path.write_bytes(text)
    else:
        path.write_text(text, encoding="utf-8")
    return path


def roster(prompt=None, other_role_prompt=None):
    """A roster in the project's form; ``prompt`` goes under ``roles: orchestrator: prompt:``."""
    text = (
        "# The project's roster (stand-in, invented)\n"
        "roles:\n"
        "  research:\n"
        "    role_file: template/governance/kernel/roles/research.md\n"
        "    session: gov launch research <ticket>\n"
    )
    if other_role_prompt:
        text += f"    prompt: {other_role_prompt}\n"
    text += (
        "  orchestrator:\n"
        "    role_file: template/governance/kernel/roles/orchestrator.md\n"
        "    agent: .claude/agents/orchestrator.md\n"
    )
    if prompt:
        text += f"    prompt: {prompt}\n"
    text += (
        "  engineer:\n"
        "    role_file: template/governance/kernel/roles/engineer.md\n"
        "    session: gov launch engineer <ticket>\n"
    )
    return text


def make_project(directory, roster_text=None, prompts=(DEFAULT_PROMPT,)):
    """A git repository built from scratch, committed. The Wave 1 prompt is always there as a file, so a
    hook that falls back to it would find it; ``prompts`` are further stand-in prompt files."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    write(directory, ".gitignore", ".gov-runtime/\n__pycache__/\n")
    write(directory, "README.md", "# W2-62 fixture project (invented)\n")
    for rel in (W1_PROMPT, *prompts):
        write(directory, rel, f"# Stand-in orchestrator prompt {rel} (W2-62 acceptance tests, invented)\n")
    if roster_text is not None:
        write(directory, ROSTER_REL, roster_text)
    git(directory, "init", "-q", "-b", "main")
    git(directory, "add", "-A")
    git(directory, "commit", "-q", "-m", "fixture project")
    return directory


def add_worktree(project, path, branch="w2/lead-fixture"):
    """A real linked worktree of the temporary ``project`` (``.git`` is a file there)."""
    git(project, "worktree", "add", "-q", "-b", branch, str(path))
    return Path(path)


# --------------------------------------------------------------------------
# Checkpoints
# --------------------------------------------------------------------------

def section_text(size, token="END", lines=None, heading="## RESUME HERE"):
    """A RESUME HERE section of exactly ``size`` characters (its lines joined by newlines, no newline at the
    end), with a sub-heading, and whose last line ends with ``token``. ``lines`` fixes its number of lines."""
    head = [heading, "", "- Active tickets: ZQ-71 (engineer implementing), ZQ-88 (waiting for its audit)", "",
            "### Loop counts", "", "- ZQ-71 review-repair loop: 17", ""]
    last = f"- LAST-LINE-MARKER the section ends here: {token}"
    count = lines if lines is not None else max(len(head) + 2, size // 110)
    fillers = count - len(head) - 1
    assert fillers >= 1, "too few lines for the section's fixed lines"
    room = size - len("\n".join(head + [last])) - fillers
    assert room >= fillers * 16, f"a section of {size} characters cannot hold {count} lines"
    widths = [room // fillers + (1 if n < room % fillers else 0) for n in range(fillers)]
    body = []
    for n, width in enumerate(widths):
        prefix = f"- note {n:04d}: "
        fill = (WORDS * (width // len(WORDS) + 2))[len(prefix) % 7: len(prefix) % 7 + width - len(prefix)]
        line = prefix + fill
        if line.endswith(" "):
            line = line[:-1] + "x"
        body.append(line)
    text = "\n".join(head + body + [last])
    assert len(text) == size, (len(text), size)
    return text


@dataclass(frozen=True)
class Checkpoint:
    text: str        # the whole file
    section: str     # the RESUME HERE section: heading to its last line that is not empty
    first: int       # its first line in the file, 1-based
    last: int        # its last line in the file, 1-based, inclusive


def checkpoint(section, before=PREAMBLE, after=HISTORY, trailing=""):
    """A checkpoint document: ``before``, the section, ``trailing`` empty lines, then ``after``.

    The expected range is computed from the construction and checked against the rule of the README: lines
    ``first`` to ``last`` of the file, joined by newlines, are the section, character for character."""
    assert before.endswith("\n") and not section.endswith("\n") and not trailing.strip()
    text = before + section + "\n" + trailing + after
    first = before.count("\n") + 1
    last = first + section.count("\n")
    lines = text.split("\n")
    assert "\n".join(lines[first - 1:last]) == section and lines[last - 1].strip()
    return Checkpoint(text, section, first, last)


def write_checkpoint(tree, rel, cp, age_s=0.0):
    """Write ``cp`` (a ``Checkpoint``, text or bytes) at ``rel`` with a modification time ``age_s`` seconds ago."""
    path = write(tree, rel, cp.text if isinstance(cp, Checkpoint) else cp)
    stamp = time.time() - age_s
    os.utime(path, (stamp, stamp))
    return path


# --------------------------------------------------------------------------
# Running the hooks
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Sandbox:
    home: Path
    bin: Path

    def tk_ready(self, text=""):
        """The stand-in ``tk`` prints ``text`` for every call (``tk ready``, ``tk ls ...``)."""
        (self.bin / "tk-ready.txt").write_text(text, encoding="utf-8")

    @property
    def path(self):
        return f"{self.bin}{os.pathsep}{os.environ.get('PATH', '/usr/local/bin:/usr/bin:/bin')}"


TK_STAND_IN = '#!/bin/sh\n# Stand-in tk (W2-62 acceptance tests)\ncat "$(dirname "$0")/tk-ready.txt"\n'


def make_sandbox(base):
    box = Sandbox(Path(base) / "home", Path(base) / "bin")
    box.home.mkdir(parents=True, exist_ok=True)
    box.bin.mkdir(parents=True, exist_ok=True)
    tk = box.bin / "tk"
    tk.write_text(TK_STAND_IN, encoding="utf-8")
    tk.chmod(0o755)
    box.tk_ready("")
    return box


def long_ready_list(chars=30_000):
    """A ready list far longer than the bound, in ``tk ready``'s shape."""
    lines, n = [], 0
    while sum(len(line) + 1 for line in lines) < chars:
        lines.append(f"RDY-{n:04d} [open] - Invented ready ticket number {n:04d} of the long ready list")
        n += 1
    return "\n".join(lines) + "\n"


@dataclass(frozen=True)
class Run:
    returncode: int | None
    stdout: str
    stderr: str
    elapsed: float

    @property
    def data(self):
        try:
            data = json.loads(self.stdout)
        except ValueError:
            return None
        return data

    @property
    def injection(self):
        data = self.data
        if not isinstance(data, dict):
            return ""
        specific = data.get("hookSpecificOutput")
        context = specific.get("additionalContext") if isinstance(specific, dict) else None
        return context if isinstance(context, str) else ""

    def describe(self):
        return f"exit={self.returncode} stdout={self.stdout[:500]!r} stderr={self.stderr[-500:]!r}"


def _env(tree, sandbox, role, ticket):
    env = {
        "PATH": sandbox.path,
        "HOME": str(sandbox.home),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "TZ": "UTC",
        "CLAUDE_PROJECT_DIR": str(tree),
        "PYTHONPATH": str(SRC),
        "PYTHONDONTWRITEBYTECODE": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
    }
    if role is not None:
        env["GOV_ROLE"] = role
    if ticket is not None:
        env["GOV_TICKET"] = ticket
    return env


def event(tree, sandbox, source):
    return {
        "session_id": "w2-62-acceptance-session",
        "transcript_path": str(sandbox.home / ".claude" / "projects" / "w2-62" / "w2-62-acceptance-session.jsonl"),
        "cwd": str(tree),
        "hook_event_name": "SessionStart",
        "source": source,
        "model": "claude-opus-5-5",
    }


def run_sessionstart(tree, sandbox, source="resume", role=ORCHESTRATOR, ticket=None, stdin=None):
    """Run this worktree's ``sessionstart.py`` as Claude Code does. ``stdin`` replaces the event (raw text)."""
    text = stdin if stdin is not None else json.dumps(event(tree, sandbox, source))
    started = time.monotonic()
    try:
        proc = subprocess.run(["python3", str(SESSIONSTART)], input=text, capture_output=True, text=True,
                              cwd=str(tree), env=_env(tree, sandbox, role, ticket), timeout=HOOK_TIMEOUT_S,
                              check=False)
    except subprocess.TimeoutExpired:
        return Run(None, "", f"did not end within {HOOK_TIMEOUT_S:.0f} s", HOOK_TIMEOUT_S)
    return Run(proc.returncode, proc.stdout, proc.stderr, time.monotonic() - started)


def compact(tree, sandbox):
    """Run this worktree's ``precompact.py`` as an orchestrator's compaction: it appends a generated state
    block to the checkpoint and keeps the file's modification time."""
    data = {"session_id": "w2-62-acceptance-session", "transcript_path": "", "cwd": str(tree),
            "hook_event_name": "PreCompact", "trigger": "auto", "custom_instructions": None}
    proc = subprocess.run(["python3", str(PRECOMPACT)], input=json.dumps(data), capture_output=True, text=True,
                          cwd=str(tree), env=_env(tree, sandbox, ORCHESTRATOR, None), timeout=HOOK_TIMEOUT_S,
                          check=False)
    assert proc.returncode == 0, f"precompact.py failed: {proc.stdout[:300]!r} {proc.stderr[-300:]!r}"


# --------------------------------------------------------------------------
# Assertions
# --------------------------------------------------------------------------

def assert_well_formed(run, what="the hook"):
    """Exit 0, within the time, and stdout either nothing or one SessionStart JSON object within the bound."""
    assert run.returncode == 0, f"{what} did not exit 0: {run.describe()}"
    assert run.elapsed < QUICK_S, f"{what} took {run.elapsed:.1f} s"
    if not run.stdout.strip():
        return
    data = run.data
    assert isinstance(data, dict), f"{what} printed something that is not one JSON object: {run.stdout[:300]!r}"
    specific = data.get("hookSpecificOutput")
    assert isinstance(specific, dict) and specific.get("hookEventName") == "SessionStart" \
        and isinstance(specific.get("additionalContext"), str), (
            f"{what} printed JSON that is not of the form "
            f'{{"hookSpecificOutput": {{"hookEventName": "SessionStart", "additionalContext": ...}}}}: '
            f"{run.stdout[:300]!r}")
    assert_within_bound(run)


def assert_within_bound(run):
    size = len(run.injection)
    assert size <= BOUND, (
        f"the injection is {size:,} characters; a SessionStart hook's context arrives whole only up to "
        f"{BOUND:,} (Claude Code 2.1.292 saves a longer one to a file and shows a preview)")


def ranges(text):
    return [(int(a), int(b)) for a, b in RANGE.findall(text)]


def sizes(text):
    return [int(n.replace(",", "")) for n in SIZE.findall(text)]


def assert_instruction(injection, cp, rel):
    """KPI 2: the instruction to read the section in full before anything else, with the path, the exact
    line range (``lines <first>-<last>``) and the size (``<n> characters``)."""
    assert rel in injection, f"the injection does not name the checkpoint {rel}: {injection[:400]!r}"
    found = ranges(injection)
    assert (cp.first, cp.last) in found, (
        f"the injection does not give the section's line range `lines {cp.first}-{cp.last}` "
        f"(ranges found: {found}): {injection[:400]!r}")
    found = sizes(injection)
    assert len(cp.section) in found, (
        f"the injection does not give the section's size `{len(cp.section):,} characters` "
        f"(sizes found: {found}): {injection[:400]!r}")
    lowered = injection.lower()
    assert "resume here" in lowered and re.search(r"\bread\b", lowered), (
        f"the injection carries no instruction to read the RESUME HERE section: {injection[:400]!r}")
    assert re.search(r"in full|\bwhole\b|\bentire|\bcomplete|every line|all of (?:it|the section)", lowered), (
        f"the instruction does not say to read the section in full: {injection[:400]!r}")
    assert re.search(r"before (?:anything|doing anything|any other)|\bfirst\b", lowered), (
        f"the instruction does not say to read the section before anything else: {injection[:400]!r}")


def assert_no_old_cut(injection, cp):
    """KPI 4: never the first 9,000 characters of the section as a cut, never the word "truncated"."""
    if len(cp.section) > OLD_CUT:
        assert cp.section[:OLD_CUT] not in injection, (
            "the injection carries the section's first 9,000 characters, the cut W2-M372 removes")
    assert "truncated" not in injection.lower(), (
        f"the injection says `truncated`: {injection[injection.lower().find('truncated') - 200:][:400]!r}")


def assert_whole(injection, cp):
    """KPI 3: the whole section, character for character."""
    assert cp.section in injection, (
        f"the section ({len(cp.section):,} characters) fits the bound and is not in the injection whole; "
        f"its last line is {'' if cp.section.splitlines()[-1] in injection else 'not '}there: {injection[:300]!r}")


def assert_warns_older(injection, rel):
    lowered = injection.lower()
    assert OLDER in injection and rel in injection and "re-derive" in lowered, (
        f"the injection does not carry the staleness warning `{OLDER}` for {rel}: {injection[:400]!r}")


def assert_names_no_prompt(injection):
    assert PROMPTS_DIR not in injection, (
        f"the roster names no prompt and the injection names one under {PROMPTS_DIR}: "
        f"{injection[max(0, injection.find(PROMPTS_DIR) - 100):][:300]!r}")
