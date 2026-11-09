"""SANDBOX-GUARD-EXP-1's harness: what every part shares (DEC-1098 (4), DEC-1099 (1)).

The places, the action record, the sealed folder (derived in code from --sets-root, never written on a command line),
hashing, and the rule that no part prints an action's contents: every part prints counts, ids and digests only.

An action record (one JSON line):
  id            "a-" + the first 16 hex of sha256 over (tool, input, cwd, role, agent, ticket)
  session       the top session's id, hashed (sha256, first 16 hex); a subagent's calls carry its parent's
  role, agent   the session's role (inferred as the G-14 replay does) and the subagent's type, or null
  ticket, wbs   the session's ticket and work item (from its tree's name; the CTO's W2-00 in the main tree)
  tool, input   the tool call's name and its input, normalised (temp names; nothing else is rewritten)
  cwd           the call's folder, normalised the same way
  tool_use_ids  every tool_use id the record stands for (the duplicates folded into it)
  first_ts      the earliest timestamp among them
  executable    false for the not-executed stratum (an agent, the network, real processes, a Windows binary)
  strata        e.g. ["ledger"], ["rehearsal-24"], ["not-executed:network"]
  half          "tuning" or "held-out" (by session)
  source        "replay", "planted-1" (writer 1, tuning) or "planted-2" (writer 2, held-out)
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

MAIN = "/home/usain/Dynamic-Agentic-Engineering-OS"
HOME = os.path.realpath(os.path.expanduser("~"))
EXP = os.path.join(HOME, "gov-os-runs", "SANDBOX-GUARD-EXP-1")  # the experiment's open folder (DEC-1099 (1))
PROJECTS = os.path.join(HOME, ".claude", "projects")
PIN_LINE = os.path.join(HOME, ".local", "bin", "gov")
LIVE_HOOKS = (".claude/hooks/pretooluse.py", ".claude/hooks/role_reads.py", ".claude/hooks/bash_writes.py")
LIVE_FILES = LIVE_HOOKS + ("governance/project/path-map.yaml", ".claude/settings.json")
# The sealed folder, relative to the sets root (ACT-SANDBOX-SEAL-1). Joined here, in code, from --sets-root.
SEALED_REL = ("fixtures", "evaluation", "sandbox-guard-exp-1", "hidden")
HALVES = ("tuning", "held-out")
FILE_TOOLS = ("Read", "Grep", "Glob", "Write", "Edit", "MultiEdit", "NotebookEdit")
TOOLS = FILE_TOOLS + ("Bash",)
WRITE_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")
WINDOW = ("2026-11-02T00:00:00", "2026-11-09T00:00:00")  # the real replay's window, UTC (package §2 (a))


def sha(data) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def file_sha(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def action_id(tool, tin, cwd, role, agent, ticket) -> str:
    return "a-" + sha(canon([tool, tin, cwd, role, agent, ticket]))[:16]


def sealed_dir(sets_root: str, *more: str) -> str:
    """The sealed folder under the given sets root (or a planted one in tests), joined in code."""
    return os.path.join(os.path.realpath(os.path.expanduser(sets_root)), *SEALED_REL, *more)


def half_dir(half: str, sets_root: str | None, exp: str, *more: str) -> str:
    """Where a half's files go: the tuning half in the open folder, the held-out half in the sealed folder."""
    if half not in HALVES:
        raise SystemExit(f"unknown half {half!r}")
    if half == "tuning":
        return os.path.join(exp, "tuning", *more)
    if not sets_root:
        raise SystemExit("the held-out half needs --sets-root (its folder is derived from it in code)")
    return sealed_dir(sets_root, *more)


def read_jsonl(path: str):
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def write_jsonl(path: str, rows) -> tuple[int, str]:
    """Write rows, return (count, sha256 of the file). Atomic: a temp file renamed into place."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    n = 0
    with open(tmp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(canon(r) + "\n")
            n += 1
    os.replace(tmp, path)
    return n, file_sha(path)


def pin_python() -> str:
    with open(PIN_LINE, encoding="utf-8") as f:
        return f.readline()[2:].strip()


# -- normalising temp names (package §2 (a): about 20,000 once tree and temp names are normalised) -----------------
_TEMP = [
    (re.compile(r"/tmp/gov-launch-([a-z-]+?)-[A-Za-z0-9_]{6,}"), r"/tmp/gov-launch-\1-EXP"),
    (re.compile(r"/tmp/tmp\.[A-Za-z0-9]{6,}"), "/tmp/tmp.EXP"),
    (re.compile(r"/tmp/tmp[a-z0-9_]{8}\b"), "/tmp/tmpEXP"),
    (re.compile(r"/tmp/pytest-of-([a-z0-9_-]+)/pytest-\d+"), r"/tmp/pytest-of-\1/pytest-EXP"),
    (re.compile(r"(/tmp/claude-\d+/[^/\s'\"]+/)[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"),
     r"\1EXP-SESSION"),
]


def norm_text(s: str) -> str:
    for rx, rep in _TEMP:
        s = rx.sub(rep, s)
    return s


def normalise(v):
    if isinstance(v, str):
        return norm_text(v)
    if isinstance(v, list):
        return [normalise(x) for x in v]
    if isinstance(v, dict):
        return {k: normalise(x) for k, x in v.items()}
    return v


# -- the not-executed stratum (package §2 (a)) ------------------------------------------------------------------------
_AGENT = re.compile(r"(?:^|[\s;&|(`$])(?:claude|codex|gov\s+launch|launch_worker\.sh|dispatch[\w-]*\.sh)(?=$|[\s;&|)])")
_NET = re.compile(r"(?:^|[\s;&|(`])(?:curl|wget|ssh|scp|rsync|gh|nc|ncat|telnet|ollama|pip3?\s+(?:install|download)"
                  r"|uv\s+pip|npm\s+(?:install|i|ci)|git\s+(?:push|fetch|pull|clone|ls-remote|remote\s+update))"
                  r"(?=$|[\s;&|)])")
_PROC = re.compile(r"(?:^|[\s;&|(`])(?:kill|pkill|killall|proc\.sh|systemctl|service|tmux|screen|nvidia-smi|reboot"
                   r"|shutdown|wsl\.exe|crontab)(?=$|[\s;&|)])")
_WIN = re.compile(r"\b[\w.-]+\.exe\b")


def not_executed(tool: str, tin: dict) -> str:
    """Why an action is not executed (judged by the hook alone, in a stratum of its own), or ""."""
    if tool != "Bash":
        return ""
    c = tin.get("command") or ""
    if _AGENT.search(c):
        return "agent"
    if _NET.search(c):
        return "network"
    if _PROC.search(c):
        return "process"
    if _WIN.search(c):
        return "windows-binary"
    return ""


# -- the planted home (the declaration §4): every action is rewritten onto it, and runs with HOME set to it ----------
REAL_HOME = "/home/usain"
_REAL_HOME_RX = re.compile(r"/home/usain(?=/|$|[\s'\"\\;|&)<>`:,\]}])")


def planted_home(exp: str) -> str:
    return os.path.join(exp, "home")


def rewrite(v, home: str):
    """The real home's absolute spelling put onto the planted home (~, $HOME and ${HOME} stay: they expand to the
    planted home, since the hook, the runner and the session run with HOME set to it). Nothing else changes."""
    if isinstance(v, str):
        return _REAL_HOME_RX.sub(home, v)
    if isinstance(v, list):
        return [rewrite(x, home) for x in v]
    if isinstance(v, dict):
        return {k: rewrite(x, home) for k, x in v.items()}
    return v


def escapes(text: str, home: str) -> bool:
    """True when a rewritten action still names the real home (a spelling the rewrite cannot place, such as
    /home/$USER or a path cut in pieces): such an action is dropped and counted, never run or judged."""
    rest = text.replace(home, "")
    return "/home/usain" in rest or re.search(r"/home/(?:\$USER|\$\{USER\}|\$LOGNAME|\*|\?)", rest) is not None


def say(*parts):
    """Counts, ids and digests only; never an action's input, output or a file's contents."""
    print(*parts, flush=True)


def die(msg: str):
    print(f"error: {msg}", file=sys.stderr, flush=True)
    raise SystemExit(2)
