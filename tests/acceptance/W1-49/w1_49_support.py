"""Support code for the W1-49 acceptance tests (standard library only).

W1-49 builds two hooks, ``precompact.py`` and ``sessionstart.py``, and registers
them in ``.claude/settings.json``. The tests use public interfaces only:

- the registration, read from the ``hooks`` key of ``.claude/settings.json``;
- each hook as the harness calls it: the registered shell command, the hook
  event's JSON object on stdin, ``CLAUDE_PROJECT_DIR``, ``GOV_ROLE`` and
  ``GOV_TICKET`` in the environment, and the answer in the exit code, stdout,
  stderr and the checkpoint file on disk;
- ``tk`` and ``git`` as the hook finds them on ``PATH``: a stand-in ``tk``
  that prints invented tickets in progress, and the real ``git`` in the
  temporary repository (or a stand-in that fails);
- the ``env`` key of ``.claude/settings.json``.

**The settings file.** It carries the held-out deny line. This module loads the
JSON and hands out the ``hooks`` and ``env`` values only; nothing here prints,
returns or compares the rest of the document, and no assertion message carries
more than a hook command or an env value.

**The project.** ``.gov-runtime/`` is not tracked, so every test builds stand-in
checkpoints in a temporary git repository that holds this repository's
``template/governance/kernel/hooks`` and ``src/gov`` (copied from git's listing)
and a stand-in orchestrator prompt. The worktree cases add a real linked
worktree with ``git worktree add``. No test reads a real checkpoint.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SETTINGS_REL = ".claude/settings.json"
HOOKS_REL = "template/governance/kernel/hooks"
PRECOMPACT_REL = f"{HOOKS_REL}/precompact.py"
SESSIONSTART_REL = f"{HOOKS_REL}/sessionstart.py"
GUARD_REL = f"{HOOKS_REL}/pretooluse.py"
CONTAINMENT_REL = f"{HOOKS_REL}/posttooluse.py"

PROMPT_REL = "governance/project/prompts/w1-orchestrator.md"
ORCHESTRATOR_CHECKPOINT_REL = ".gov-runtime/scratch/orchestrator/CHECKPOINT.md"
LEAD_CHECKPOINT_REL = ".gov-runtime/scratch/lead/CHECKPOINT.md"

ORCHESTRATOR = "orchestrator"
WORKER_ROLES = ("engineer", "independent-test-designer", "independent-auditor")

# Claude Code 2.1.288, hooks reference, "Add context for Claude": 10,000 characters for each of additionalContext,
# systemMessage, initialUserMessage and plain stdout; over it, the text is replaced by a file path and a preview.
SIZE_CAP_CHARS = 10_000
TRUNCATED = "truncated"                    # the word the SessionStart hook uses when it cuts the section

# DEC-264: the generated state block the PreCompact hook appends, and the SessionStart warning. Fixed by the README.
BLOCK_BEGIN = "<!-- GENERATED STATE BLOCK BEGIN -->"
BLOCK_END = "<!-- GENERATED STATE BLOCK END -->"
OLDER = "CHECKPOINT OLDER THAN STATE BLOCK"   # the phrase of the SessionStart warning
UNAVAILABLE = "unavailable"                # the word the block uses for what the hook could not read
DECISIONS_LABEL = "pending owner decisions"
TK_LINES = (                               # what the stand-in tk gives for `tk ls --status=in_progress`
    "GEN-41 [in_progress] - Invented generated ticket alpha <- [GEN-07]",
    "GEN-58 [in_progress] - Invented generated ticket beta",
)
TK_STAND_IN = (
    "#!/bin/sh\n"
    "# Stand-in tk (W1-49 acceptance tests): the tickets in progress, invented.\n"
    'case "$1 $2" in\n'
    '  "ls --status=in_progress"|"list --status=in_progress") cat "$(dirname "$0")/tk-in-progress.txt" ;;\n'
    '  *) echo "stand-in tk: unexpected call: $*" >&2; exit 64 ;;\n'
    "esac\n"
)
FAILING_STAND_IN = "#!/bin/sh\necho \"$(basename \"$0\"): stand-in failure\" >&2\nexit 1\n"

WINDOW_KEY = "CLAUDE_CODE_AUTO_COMPACT_WINDOW"
WINDOW_TOKENS = 300_000
WINDOW_TOLERANCE = 30_000                  # "about 300k": 270,000 to 330,000

HOOK_TIMEOUT_S = 30.0
HOUR_S = 3600.0
STALE_AGE_S = 3 * 24 * HOUR_S              # a checkpoint three days old: older than the last commit and the transcript
RECENT_AGE_S = 300.0                       # five minutes old: written after the last commit, before the compaction
SESSION_ID = "w1-49-acceptance-session"

PROJECT_PATHSPECS = (HOOKS_REL, "src/gov")
STAND_IN_PROMPT = (
    "# Stand-in orchestrator prompt (W1-49 acceptance tests, invented)\n\n"
    "You orchestrate the invented project Zephyr. After a compaction, a clear or a resume, continue from the\n"
    "RESUME HERE section of your checkpoint. When you say where you stand, name the active tickets, the open\n"
    "owner decisions and the loop counts.\n"
)


# --------------------------------------------------------------------------
# The settings file: the ``hooks`` and ``env`` keys, nothing else
# --------------------------------------------------------------------------

def load_hooks_and_env(root=REPO_ROOT):
    """``(hooks, env)`` of ``.claude/settings.json``. The rest of the document never leaves this function."""
    path = Path(root) / SETTINGS_REL
    assert path.is_file(), f"{SETTINGS_REL} does not exist"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        raise AssertionError(f"{SETTINGS_REL} is not valid JSON") from None
    assert isinstance(data, dict), f"{SETTINGS_REL} does not hold a JSON object"
    hooks, env = data.get("hooks"), data.get("env")
    del data
    return (hooks if isinstance(hooks, dict) else {}), (env if isinstance(env, dict) else {})


def matcher_matches(matcher, value):
    """No matcher, an empty one and ``*`` match everything; otherwise the whole value, as a name or a regex."""
    if matcher is None or matcher in ("", "*"):
        return True
    if not isinstance(matcher, str):
        return False
    try:
        return re.fullmatch(matcher, value) is not None
    except re.error:
        return matcher == value


def hook_commands(hooks, event, value):
    """The shell commands registered for ``event`` that the harness runs for the matcher value ``value``."""
    entries = hooks.get(event)
    commands = []
    for entry in entries if isinstance(entries, list) else []:
        if not isinstance(entry, dict) or not matcher_matches(entry.get("matcher"), value):
            continue
        for hook in entry.get("hooks") if isinstance(entry.get("hooks"), list) else []:
            if isinstance(hook, dict) and hook.get("type", "command") == "command" \
                    and isinstance(hook.get("command"), str) and hook["command"].strip():
                commands.append(hook["command"])
    return commands


def hook_entries(hooks, event, filename):
    """The registration entries of ``event`` with a command that names ``filename`` (for the temporary settings)."""
    entries = hooks.get(event)
    return [entry for entry in entries if isinstance(entry, dict)
            and any(isinstance(hook, dict) and filename in str(hook.get("command", ""))
                    for hook in entry.get("hooks") or [])] if isinstance(entries, list) else []


def command_for(hooks, event, value, rel):
    """The registered command of ``event`` for ``value`` that runs the hook file ``rel``; ``None`` when there is none."""
    name = rel.rsplit("/", 1)[-1]
    for command in hook_commands(hooks, event, value):
        if name in command:
            return command
    return None


# --------------------------------------------------------------------------
# The temporary project
# --------------------------------------------------------------------------

def git(directory, *args, when=None):
    env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
    if when is not None:
        stamp = f"{int(when)} +0000"
        env.update(GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    return subprocess.run(
        ["git", "-C", str(directory), "-c", "user.name=W1-49 tests", "-c", "user.email=w1-49@example.invalid",
         "-c", "commit.gpgsign=false", *args],
        capture_output=True, text=True, check=True, env=env).stdout


def make_project(directory, root=REPO_ROOT):
    """A git repository with the kernel hooks, ``src/gov`` and a stand-in prompt, committed an hour ago."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    listing = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--",
         *PROJECT_PATHSPECS],
        capture_output=True, text=True, check=True).stdout
    for rel in sorted(set(item for item in listing.split("\0") if item)):
        source = Path(root) / rel
        if source.is_file() and not source.is_symlink():
            target = directory / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    write(directory, PROMPT_REL, STAND_IN_PROMPT)
    write(directory, ".gitignore", ".gov-runtime/\n__pycache__/\n")
    write(directory, "README.md", "# W1-49 fixture project\n")
    git(directory, "init", "-q", "-b", "main")
    git(directory, "add", "-A")
    git(directory, "commit", "-q", "-m", "fixture project", when=time.time() - HOUR_S)
    return directory


def add_worktree(project, path, branch="w1/lead-fixture"):
    """A real linked worktree of ``project``, as a ticket lead works in."""
    git(project, "worktree", "add", "-q", "-b", branch, str(path))
    return Path(path)


def write(tree, rel, text):
    path = Path(tree) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def write_checkpoint(tree, rel, text, age_s=0.0):
    """A stand-in checkpoint whose modification time is ``age_s`` seconds ago."""
    path = write(tree, rel, text)
    stamp = time.time() - age_s
    os.utime(path, (stamp, stamp))
    return path


def checkpoint_text(resume_body, heading="## RESUME HERE", before="", after=""):
    """A checkpoint document: an optional preamble, the RESUME HERE section, an optional later section."""
    return (f"# Checkpoint (stand-in, invented)\n\n{before}{heading}\n\n{resume_body.rstrip()}\n"
            + (f"\n{after}" if after else ""))


def resume_section(prefix):
    """The body of an invented RESUME HERE section; ``prefix`` makes its tickets and decisions distinct."""
    return (
        f"- Active tickets: {prefix}-71 (engineer implementing), {prefix}-88 (waiting for its audit)\n"
        f"- Open owner decisions: OD-{prefix}-913 (rename the ledger module?), OD-{prefix}-927 (keep the slow parser?)\n"
        "\n"
        "### Loop counts\n"
        "\n"
        f"- {prefix}-71 review-repair loop: 17\n"
        f"- {prefix}-88 test-fix loop: 23\n"
        "\n"
        f"Next action: start the audit of {prefix}-88, then read the review of {prefix}-71.\n"
    )


def split_checkpoint(text):
    """``(written part, generated block or None)``, by the README's rule.

    The file holds a block only when its last line that is not empty is the end marker; the block then starts at
    the last line that is the begin marker and nothing else. Everything before that line is the written part.
    """
    lines = text.splitlines(keepends=True)
    last = len(lines)
    while last and not lines[last - 1].strip():
        last -= 1
    if not last or lines[last - 1].strip() != BLOCK_END:
        return text, None
    for index in range(last - 1, -1, -1):
        if lines[index].strip() == BLOCK_BEGIN:
            return "".join(lines[:index]), "".join(lines[index:])
    return text, None


def read_block(path, original):
    """The generated block of the checkpoint at ``path``, after asserting the written part ``original`` is intact."""
    data = Path(path).read_bytes()
    kept = original.encode("utf-8")
    assert data.startswith(kept), (
        "the written part of the checkpoint is no longer byte-for-byte what it was, or no longer comes first: "
        f"the file now begins {data[:120]!r}"
    )
    rest = data[len(kept):].decode("utf-8")
    assert rest.strip(), f"no generated state block was appended to {path.name}: the file is unchanged"
    assert rest.strip().splitlines()[0] == BLOCK_BEGIN and rest.strip().splitlines()[-1] == BLOCK_END, (
        f"what follows the written part is not one block from `{BLOCK_BEGIN}` to `{BLOCK_END}`: {rest[:300]!r}"
    )
    return rest.strip()


def marker_lines(text, marker=BLOCK_BEGIN):
    """How many lines of ``text`` are the marker and nothing else."""
    return sum(1 for line in text.splitlines() if line.strip() == marker)


# --------------------------------------------------------------------------
# Running a hook as the harness does
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Sandbox:
    home: Path
    tmpdir: Path
    bin: Path

    def tk_gives(self, lines=TK_LINES):
        """Put the stand-in ``tk`` first on the hook's ``PATH``; it prints ``lines`` for the tickets in progress."""
        (self.bin / "tk-in-progress.txt").write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")
        return _executable(self.bin / "tk", TK_STAND_IN)

    def tk_fails(self):
        """The stand-in ``tk`` ends with 1 and prints nothing on stdout."""
        return _executable(self.bin / "tk", FAILING_STAND_IN)

    def git_fails(self):
        """A ``git`` that ends with 1 for every call, first on the hook's ``PATH`` (the tests' own git is not this one)."""
        return _executable(self.bin / "git", FAILING_STAND_IN)

    @property
    def path(self):
        """The hook's ``PATH``: the stand-ins first, then the caller's."""
        return f"{self.bin}{os.pathsep}{os.environ.get('PATH', '/usr/local/bin:/usr/bin:/bin')}"

    @property
    def path_without_tk(self):
        """A ``PATH`` on which no ``tk`` is found, and ``python3``, ``git`` and ``sh`` still are."""
        kept = [entry for entry in os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin").split(os.pathsep)
                if entry and not (Path(entry) / "tk").exists()]
        path = os.pathsep.join(kept)
        for tool in ("python3", "git", "sh"):
            assert shutil.which(tool, path=path), f"without the directories that hold tk, {tool} is not on PATH"
        return path

    def transcript(self, age_s=600.0):
        """The session's transcript file, last written ``age_s`` seconds ago."""
        path = self.home / ".claude" / "projects" / "w1-49" / f"{SESSION_ID}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('{"type":"user"}\n', encoding="utf-8")
        stamp = time.time() - age_s
        os.utime(path, (stamp, stamp))
        return path


def _executable(path, text):
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)
    return path


def make_sandbox(base):
    box = Sandbox(Path(base) / "home", Path(base) / "systmp", Path(base) / "bin")
    for directory in (box.home, box.tmpdir, box.bin):
        directory.mkdir(parents=True, exist_ok=True)
    box.tk_gives()
    return box


def hook_input(tree, sandbox, event, transcript_age_s=600.0, **fields):
    """The JSON object Claude Code 2.1.288 sends on stdin: the common fields and the event's own."""
    data = {
        "session_id": SESSION_ID,
        "transcript_path": str(sandbox.transcript(transcript_age_s)),
        "cwd": str(tree),
        "hook_event_name": event,
    }
    data.update(fields)
    return data


def precompact_input(tree, sandbox, trigger, transcript_age_s=600.0):
    return hook_input(tree, sandbox, "PreCompact", transcript_age_s, trigger=trigger, custom_instructions=None)


def sessionstart_input(tree, sandbox, source):
    return hook_input(tree, sandbox, "SessionStart", source=source, model="claude-haiku-4-5-20251001")


@dataclass(frozen=True)
class HookRun:
    command: str
    returncode: int | None
    stdout: str
    stderr: str

    def _json(self):
        try:
            data = json.loads(self.stdout.strip() or "null")
        except ValueError:
            return None
        return data if isinstance(data, dict) else None

    @property
    def injection(self):
        """What reaches the model: ``hookSpecificOutput.additionalContext``, or stdout when it is plain text."""
        data = self._json()
        if data is None:
            return self.stdout.strip()
        specific = data.get("hookSpecificOutput")
        context = specific.get("additionalContext") if isinstance(specific, dict) else None
        return context if isinstance(context, str) else ""

    @property
    def measured(self):
        """Each string Claude Code measures against the cap, by name."""
        data = self._json()
        if data is None:
            return {"stdout": self.stdout}
        specific = data.get("hookSpecificOutput") if isinstance(data.get("hookSpecificOutput"), dict) else {}
        found = {"additionalContext": specific.get("additionalContext"), "systemMessage": data.get("systemMessage"),
                 "initialUserMessage": specific.get("initialUserMessage")}
        return {name: text for name, text in found.items() if isinstance(text, str)}

    @property
    def said(self):
        """Everything the hook said to anyone: stderr, and stdout as text or as its JSON strings."""
        data = self._json()
        parts = [self.stderr]
        if data is None:
            parts.append(self.stdout)
        else:
            parts.extend(str(data.get(key, "")) for key in ("systemMessage", "reason", "stopReason"))
            parts.extend(self.measured.values())
        return "\n".join(parts)

    def describe(self):
        return (f"exit={self.returncode} stdout={self.stdout.strip()[:400]!r} stderr={self.stderr.strip()[:400]!r}")


def run_hook(command, tree, sandbox, stdin, role=ORCHESTRATOR, ticket=None, path=None):
    """Run one registered command through the shell, in ``tree``, with ``stdin`` (an object, or raw text).

    ``ticket`` is ``GOV_TICKET`` (unset when ``None``). ``path`` replaces the hook's ``PATH``, which otherwise
    starts with the sandbox's stand-in ``tk``: no test calls the real one.
    """
    env = {
        "PATH": path if path is not None else sandbox.path,
        "HOME": str(sandbox.home),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "TZ": "UTC",
        "TMPDIR": str(sandbox.tmpdir),
        "CLAUDE_PROJECT_DIR": str(tree),
        "PYTHONDONTWRITEBYTECODE": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
    }
    if role is not None:
        env["GOV_ROLE"] = role
    if ticket is not None:
        env["GOV_TICKET"] = ticket
    text = stdin if isinstance(stdin, str) else json.dumps(stdin)
    try:
        proc = subprocess.run(["sh", "-c", command], input=text, capture_output=True, text=True, cwd=str(tree),
                              env=env, timeout=HOOK_TIMEOUT_S, check=False)
    except subprocess.TimeoutExpired:
        return HookRun(command, None, "", f"did not end within {HOOK_TIMEOUT_S:.0f} s")
    return HookRun(command, proc.returncode, proc.stdout, proc.stderr)


def assert_within_cap(run):
    for name, text in run.measured.items():
        assert len(text) <= SIZE_CAP_CHARS, (
            f"the hook's {name} is {len(text)} characters; Claude Code 2.1.288 replaces anything over "
            f"{SIZE_CAP_CHARS} with a file path and a 2,000-character preview"
        )


def assert_not_blocked(run, what):
    """DEC-264: exit code 0, and no JSON answer that blocks (``decision: block``, ``continue: false``)."""
    assert run.returncode == 0, f"{what}: the hook ended with {run.returncode}, not 0: {run.describe()}"
    data = run._json() or {}
    assert data.get("decision") != "block" and data.get("continue") is not False, (
        f"{what}: the hook answered with a blocking decision: {run.describe()}"
    )


def assert_warns_older(text, checkpoint_rel):
    """DEC-264: the warning, the checkpoint it is about, and the instruction to re-derive state before acting."""
    assert OLDER in text and checkpoint_rel in text, (
        f"the written part is older than the state block and the injection does not say `{OLDER}` with the path "
        f"{checkpoint_rel}: {text[:400]!r}"
    )
    lowered = text.lower()
    missing = [word for word in ("re-derive", "git", "tickets", "before acting") if word not in lowered]
    assert not missing, (
        f"the warning does not tell the session to re-derive state from git and the tickets before acting "
        f"(missing {missing}): {text[:400]!r}"
    )


def assert_reads_both_now(text, *paths):
    """The injection names each path and tells the session to read them now."""
    for path in paths:
        assert path in text, f"the injection does not carry the path {path}: {text[:300]!r}"
    lowered = text.lower()
    assert re.search(r"\bread\b", lowered) and re.search(r"\bnow\b", lowered), (
        f"the injection carries no instruction to read both now: {text[:300]!r}"
    )
