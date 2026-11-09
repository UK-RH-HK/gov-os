"""Planted worlds for the W2-148 acceptance tests (the operator agent, DEC-1104 (2), OPERATOR-AGENT-1).

Everything lives under one temporary folder per world: the operator root (with the install copied from this tree's
``governance/project/operator/`` and its ``APPROVED``), a live planted repository with a bare remote, a live planted
HOME, the CTO's scratch (bundles, ``log/cto-session.txt``), the transcripts folder, a clock file, the notice channels
(a stub push command and a pings log), a guard call log, and stubs on PATH for ``claude``, ``crontab`` and ``sudo``.
Every subprocess gets HOME and PATH of the world, never the real ones, so no real ``~/gov-os-operator``, ``~/.claude``,
crontab, push channel or ``claude`` is reached. The interface these helpers call is stated in README.md.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import site
import subprocess
import sys
import time
from pathlib import Path
from typing import NamedTuple

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OPERATOR_SRC = ROOT / "governance" / "project" / "operator"
WALLS_SRC = ROOT / "governance" / "project" / "indep-walls"
PACKAGES = ROOT / "governance" / "project" / "orchestration" / "packages"
EVIDENCE = ROOT / "docs" / "changes" / "W2-148-evidence.md"

# The reference verdict.py the CTO's scratch holds (.gov-runtime/scratch/ref/verdict.py), which the install pins.
REF_VERDICT_SHA256 = "277c8ca9f06c90906397579f4d5bd144fb506a40b0836eb2a8f9c1443d909378"

SID = "5b1f0c9e-0d1a-4c4e-9a43-2f6a8d3c7e11"
NOW = "2026-11-10T10:00:00+00:00"
REVIEW_TIME = "2026-11-10T09:00:00+00:00"
YES_TIME = "2026-11-10T09:30:00.000Z"
CTO_TASK = "DAEO-sdxk"
PY = sys.executable
USER_BASE = site.getuserbase()

# --- the planted repository's files (also the "before" of the classifier's cases) ---------------------------------

PATH_MAP = """\
# The planted path map (W2-148 acceptance): the blocks the operator's rule table names.
version: 1
close_timeout: 7200
acceptance_exemptions:
  - "tests/acceptance/W1-01/**"
evaluation_sets:
  planted-set:
    visible: []
    hidden: ["fixtures/evaluation/planted-set/hidden/**"]
    measures:
      roles: [engineer]
role_paths:
  engineer:
    reads_denied: ["{ticket_tests}"]
sets_root_hidden:
  root: "~/gov-os-eval"
  hidden: ["fixtures/evaluation/planted-set/hidden/**", "transcripts/**"]
  refused_roles: [orchestrator, engineer]
"""

TEST_MAP = """\
# The planted test map (W2-148 acceptance).
version: 1
shared_core:
  - "src/gov/close/**"
record_only:
  - ".tickets/**.md"
record_reading:
  - "tests/acceptance/W2-66/test_w2_66_x.py"
every_close:
  - "tests/acceptance/W1-07/test_w1_07_envelope.py"
couplings:
  - paths: ["src/gov/cli/main.py"]
    suites: ["tests/acceptance/W1-42/"]
    why: "text read"
per_test_timeout: 900
distribution: load
"""

SETTINGS = {
    "permissions": {
        "allow": ["Bash(git status)", "Read(./**)"],
        "deny": ["Read(./.env)", "Bash(sudo *)"],
    },
    "hooks": {
        "PreToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": "python3 .claude/hooks/pretooluse.py"}]}]
    },
}


def settings_text(data=None) -> str:
    return json.dumps(SETTINGS if data is None else data, indent=2) + "\n"


def optin_text(tag: str) -> str:
    return (f"# The planted opt-in list {tag} (W2-148 acceptance). One node id per line, then # and why.\n"
            f"tests/acceptance/W1-50/test_{tag}_a.py  # feature off\n"
            f"tests/acceptance/W1-51/test_{tag}_b.py  # feature off\n"
            f"tests/acceptance/W1-52/test_{tag}_c.py  # feature off\n")


OPTINS = {"tests/optin-lifted.txt": optin_text("lifted"),
          "tests/optin-lifted-guard.txt": optin_text("guard"),
          "tests/optin-lifted-breadth.txt": optin_text("breadth")}

REGISTER = """\
# Decision register (planted, W2-148 acceptance)

## 2. Decisions

### DEC-9001 — a planted accepted decision
- **Status:** ACCEPTED (owner, 2026-11-09) · **Basis:** SUGGESTION
- **Decision:** the planted ACTs run under this one.

### DEC-9002 — a planted proposed decision
- **Status:** PROPOSED · **Basis:** SUGGESTION
- **Decision:** not yet decided.
"""

PLANTED_GUARD = '''\
#!/usr/bin/env python3
"""The planted guard (W2-148 acceptance): refuses a Read whose repository-relative file_path matches a glob of the
path map's sets_root_hidden hidden list. It reads <CLAUDE_PROJECT_DIR or cwd>/governance/project/path-map.yaml and
the event on stdin; a deny is printed as hookSpecificOutput; anything it cannot read exits 2 (refused)."""
import fnmatch, json, os, re, sys
root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
try:
    text = open(os.path.join(root, "governance", "project", "path-map.yaml"), encoding="utf-8").read()
    block = text.split("sets_root_hidden:", 1)[1]
    globs = re.findall(r'"([^"]+)"', re.search(r"^\\s*hidden:\\s*\\[(.*?)\\]", block, re.M).group(1))
    event = json.loads(sys.stdin.read())
except Exception as exc:
    sys.stderr.write("planted guard: %s\\n" % exc)
    sys.exit(2)
path = (event.get("tool_input") or {}).get("file_path") or ""
if event.get("tool_name") == "Read" and any(fnmatch.fnmatch(path, g) for g in globs):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": "planted guard: hidden"}}))
sys.exit(0)
'''

REPO_FILES = {
    "README.md": "# The planted repository (W2-148 acceptance)\n",
    "governance/project/path-map.yaml": PATH_MAP,
    "governance/project/test-map.yaml": TEST_MAP,
    "governance/project/orchestration/CHECKPOINT.md": "# The CTO's checkpoint (planted)\n",
    "governance/project/orchestration/tools/deadman.py": "# the dead-man's switch (planted)\nprint('alive')\n",
    "governance/project/orchestration/tools/sentinel-brief.md": "# the sentinel's brief (planted)\n",
    "governance/project/orchestration/tools/gov_reranker_gpu_slot.py": "# the shared reranker's slot module (planted)\n",
    ".claude/settings.json": settings_text(),
    ".claude/hooks/pretooluse.py": PLANTED_GUARD,
    ".claude/agents/engineer.md": "# engineer (planted role file)\n",
    "docs/DECISION_REGISTER.md": REGISTER,
    "docs/notes.md": "planted notes\n",
    "src/gov/planted.py": "VALUE = 1\n",
    **OPTINS,
}

LIVE_MARKER = ".live-marker"  # untracked (excluded), in the live repository only: a clone never has it


# --- small helpers -------------------------------------------------------------------------------------------------

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def require_operator():
    """Red for the right reason on integrate: the operator's code is not built yet."""
    if not (OPERATOR_SRC / "operator_run.py").is_file():
        pytest.fail("governance/project/operator/operator_run.py does not exist on this tree: the operator agent is "
                    "not built yet (W2-148)", pytrace=False)


def last_json(text: str) -> dict:
    for line in reversed((text or "").splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                value = json.loads(line)
            except ValueError:
                continue
            if isinstance(value, dict):
                return value
    return {}


def read_jsonl(path: Path) -> list:
    if not Path(path).is_file():
        return []
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except ValueError:
                out.append({"_unparsed": line})
    return out


class Result(NamedTuple):
    code: int
    out: dict      # the last JSON line of stdout
    stdout: str
    stderr: str


class Change(NamedTuple):
    root: str               # "repo", "home" or "crontab"
    path: str               # relative to the root ("crontab" for the crontab)
    before: bytes | None    # None: the file does not exist before
    after: bytes | None     # None: the file is removed


class Bundle(NamedTuple):
    act: str
    dir: Path
    sha: str
    manifest: dict

    @property
    def sha8(self) -> str:
        return self.sha[:8]


def _target(change: Change) -> str:
    if change.root == "repo":
        return shlex.quote("./" + change.path)
    if change.root == "home":
        return '"$HOME"/' + shlex.quote(change.path)
    raise ValueError(change.root)


def apply_script(changes, *, apply_extra="", live_apply="", live_apply_mid="", undo_extra="", live_undo="",
                 skip_apply=()) -> str:
    """The planted ``apply.sh check|apply|undo``: run with cwd the repository (live or clone) and HOME the live or
    planted HOME. ``live_*`` lines run only in the live repository (it holds the untracked LIVE_MARKER)."""
    check, place_after, place_before = [], [], []
    for c in changes:
        if c.root == "crontab":
            check.append(f'[ "$(crontab -l | sha256sum | cut -d" " -f1)" = "{sha256_bytes(c.before or b"")}" ] || '
                         '{ echo "moved: crontab" >&2; exit 1; }')
            place_after.append('crontab "$B/after/crontab/crontab" || exit 1')
            place_before.append('crontab "$B/before/crontab/crontab" || exit 1')
            continue
        t = _target(c)
        if c.before is None:
            check.append(f'[ ! -e {t} ] || {{ echo "moved: {c.path}" >&2; exit 1; }}')
        else:
            check.append(f'[ "$(sha256sum < {t} 2>/dev/null | cut -d" " -f1)" = "{sha256_bytes(c.before)}" ] || '
                         f'{{ echo "moved: {c.path}" >&2; exit 1; }}')
        for side, data, lines in (("after", c.after, place_after), ("before", c.before, place_before)):
            if side == "after" and c.path in skip_apply:
                continue
            if data is None:
                lines.append(f"rm -f {t} || exit 1")
            else:
                lines.append(f'mkdir -p "$(dirname {t})" && cat "$B/{side}/{c.root}/{c.path}" > {t} || exit 1')
    mid = len(place_after) // 2 or 1
    after_lines = place_after[:mid] + ([f'if [ "$LIVE" = 1 ]; then {live_apply_mid}; fi'] if live_apply_mid else []) \
        + place_after[mid:]
    body = [
        "#!/usr/bin/env bash",
        "# The planted ACT's apply.sh (W2-148 acceptance).",
        "set -u",
        'B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"',
        f"LIVE=0; if [ -e {LIVE_MARKER} ]; then LIVE=1; fi",
        'case "${1:-}" in',
        "check)", *check, ";;",
        "apply)", *after_lines,
        apply_extra or ":",
        f'if [ "$LIVE" = 1 ]; then {live_apply or ":"}; fi',
        ";;",
        "undo)",
        f'if [ "$LIVE" = 1 ]; then {live_undo or ":"}; fi',
        *place_before,
        undo_extra or ":",
        ";;",
        '*) echo "usage: apply.sh check|apply|undo" >&2; exit 2 ;;',
        "esac",
        "exit 0",
        "",
    ]
    return "\n".join(body)


REHEARSAL_OK = ("rehearsal in a clone at the live head (planted)\n"
                "check: exit 0\napply: exit 0\nchecks: 1 of 1 as stated\nundo: byte for byte\nfailures: 0\n")


def write_bundle(folder: Path, act: str, changes, *, claimed="a", dec="DEC-9001", author="orchestrator",
                 checks=None, commands=None, rehearsal=REHEARSAL_OK, rehearsal_field=True, rehearsal_sha=None,
                 script=None, **script_kw) -> Bundle:
    """An ACT bundle: manifest.json, apply.sh, rehearsal.log, before/<root>/<path>, after/<root>/<path>."""
    folder = Path(folder)
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)
    files = {}

    def put(rel, data: bytes):
        p = folder / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        files[rel] = sha256_bytes(data)

    touched = []
    for c in changes:
        if c.before is not None:
            put(f"before/{c.root}/{c.path}", c.before)
        if c.after is not None:
            put(f"after/{c.root}/{c.path}", c.after)
        touched.append({"root": c.root, "path": c.path,
                        "before": None if c.before is None else sha256_bytes(c.before),
                        "after": None if c.after is None else sha256_bytes(c.after)})
    put("apply.sh", (script if script is not None else apply_script(changes, **script_kw)).encode())
    if rehearsal is not None:
        put("rehearsal.log", rehearsal.encode())
    manifest = {
        "act": act,
        "dec": dec,
        "author": author,
        "claimed_class": claimed,
        "touched": touched,
        "files": files,
        "checks": checks if checks is not None else [{"cmd": "true", "exit": 0, "count": None}],
        "commands": commands or [],
    }
    if rehearsal_field:
        manifest["rehearsal"] = {"log": "rehearsal.log",
                                 "sha256": rehearsal_sha or (files.get("rehearsal.log") or "0" * 64)}
    if dec is None:
        del manifest["dec"]
    data = (json.dumps(manifest, indent=1, sort_keys=True) + "\n").encode()
    (folder / "manifest.json").write_bytes(data)
    (folder / "apply.sh").chmod(0o755)
    return Bundle(act, folder, sha256_bytes(data), manifest)


def verdict_block(data) -> str:
    body = data if isinstance(data, str) else json.dumps(data)
    return f"```verdict\n{body}\n```\n"


def classify(bundle_dir: Path) -> dict:
    """``python3 governance/project/operator/act_class.py <bundle dir>``: its JSON."""
    require_operator()
    p = subprocess.run([PY, "-B", str(OPERATOR_SRC / "act_class.py"), str(bundle_dir)], capture_output=True,
                       text=True, timeout=60, env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                                                   "HOME": str(bundle_dir), "LANG": "C.UTF-8",
                                                   "PYTHONUSERBASE": USER_BASE, "PYTHONDONTWRITEBYTECODE": "1"})
    return {"code": p.returncode, **last_json(p.stdout)}


# --- transcripts (Claude Code 2.1.319's shapes, the ticket's reading) ----------------------------------------------

def _line(ts, content, **extra):
    line = {"parentUuid": None, "isSidechain": False, "userType": "external", "cwd": "/planted/repo",
            "sessionId": SID, "version": "2.1.319", "gitBranch": "w2/integrate", "type": "user",
            "message": {"role": "user", "content": content}, "uuid": f"u-{abs(hash((ts, str(content)))) % 10**12}",
            "timestamp": ts}
    line.update(extra)
    return line


def human(text, ts=YES_TIME, blocks=False):
    """A typed owner turn (terminal: a string; Remote Control: text blocks)."""
    content = [{"type": "text", "text": text}] if blocks else text
    return _line(ts, content, origin={"kind": "human"}, promptSource="sdk")


def task_notification(text, ts=YES_TIME):
    return _line(ts, text, origin={"kind": "task-notification", "taskId": "t1"}, promptSource="system")


def tool_result(text, ts=YES_TIME):
    return _line(ts, [{"type": "tool_result", "tool_use_id": "toolu_1", "content": text}], origin=None,
                 toolUseResult={"stdout": text, "stderr": "", "interrupted": False})


def meta(text, ts=YES_TIME):
    return _line(ts, text, isMeta=True, origin=None)


def sidechain(text, ts=YES_TIME):
    return _line(ts, text, origin={"kind": "human"}, promptSource="sdk", isSidechain=True)


def unmarked(text, ts=YES_TIME):
    """A user line with no origin mark at all (a future format): never a yes (fail closed)."""
    return _line(ts, text, promptSource="sdk")


def assistant(text, ts=YES_TIME):
    line = _line(ts, [{"type": "text", "text": text}])
    line["type"] = "assistant"
    line["message"] = {"role": "assistant", "content": [{"type": "text", "text": text}]}
    return line


# --- the world -----------------------------------------------------------------------------------------------------

CLAUDE_STUB = r'''#!@PY@
"""Stub claude (W2-148 acceptance): records argv, cwd, environment, pid and pgid; answers like `claude -p
--output-format json`. In "validate" mode it models a loaded wall: when --settings names a JSON file with a non-empty
permissions.deny and a PreToolUse hook, every absolute path named in the prompt outside its cwd comes back as a Read in
permission_denials. In "ignored" mode it models settings that did not load: no denial ever."""
import json, os, re, sys, time
LOG, MODE = @LOG@, @MODE@
argv = sys.argv[1:]
with open(LOG, "a") as f:
    f.write(json.dumps({"argv": argv, "cwd": os.getcwd(), "env": dict(os.environ), "pid": os.getpid(),
                        "pgid": os.getpgid(0), "time": time.time()}) + "\n")
VALUED = {"--settings", "--add-dir", "--tools", "--model", "--max-budget-usd", "--output-format",
          "--permission-prompts", "--allowedTools", "--allowed-tools", "--disallowedTools", "--disallowed-tools",
          "--permission-mode", "--append-system-prompt", "--system-prompt", "--mcp-config", "--session-id",
          "--fallback-model", "--input-format", "--max-turns", "--setting-sources"}
positional, i = [], 0
while i < len(argv):
    a = argv[i]
    if a in VALUED:
        i += 2
        continue
    if not a.startswith("-"):
        positional.append(a)
    i += 1
def loaded():
    if "--settings" not in argv:
        return False
    try:
        s = json.load(open(argv[argv.index("--settings") + 1]))
        return bool(s["permissions"]["deny"]) and bool(s["hooks"]["PreToolUse"])
    except Exception:
        return False
denials = []
if MODE == "validate" and loaded():
    cwd = os.path.realpath(os.getcwd())
    for text in positional:
        for p in re.findall(r"(/[^\s\"'`()<>]+)", text):
            p = p.rstrip(".,;:")
            rp = os.path.realpath(p)
            if not (rp == cwd or rp.startswith(cwd + "/")):
                denials.append({"tool_name": "Read", "tool_use_id": "toolu_%d" % len(denials),
                                "tool_input": {"file_path": p}})
print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "num_turns": 1, "result": "done",
                  "session_id": "stub-session", "total_cost_usd": 0.0, "permission_denials": denials}))
'''

CRONTAB_STUB = """#!/bin/bash
# Stub crontab (W2-148 acceptance): the table is one file of the world.
STORE=@STORE@
case "${1:-}" in
  -l) cat "$STORE" ;;
  -r) : > "$STORE" ;;
  -|"") cat > "$STORE" ;;
  *) cat "$1" > "$STORE" ;;
esac
"""

RECORDING_STUB = """#!/bin/bash
# Stub @NAME@ (W2-148 acceptance): records that it was called, then refuses.
echo "$0 $*" >> @MARK@
exit 1
"""

PUSH_STUB = """#!@PY@
# Stub push channel (W2-148 acceptance): one JSON line per notice, its argv.
import json, sys
with open(@LOG@, "a") as f:
    f.write(json.dumps({"argv": sys.argv[1:]}) + "\\n")
"""


class World:
    def __init__(self, base: Path, claude_mode: str = "validate"):
        base = Path(base).resolve()
        self.base = base
        self.op = base / "op"
        self.install = self.op / "install"
        self.repo = base / "repo"
        self.remote = base / "remote.git"
        self.home = base / "home"
        self.scratch = base / "scratch"
        self.transcripts = self.home / ".claude" / "projects" / "-planted-repo"
        self.clock = base / "clock.txt"
        self.pings = base / "pings.log"
        self.pushes = base / "pushes.jsonl"
        self.stubs = base / "stubs"
        self.claude_log = base / "claude-calls.jsonl"
        self.crontab_store = base / "crontab.txt"
        self.calls = base / "calls.jsonl"
        self.close_flag = base / "close-queue.running"
        self.config = base / "config.json"
        self.tmp = base / "tmp"
        self.marks = base / "marks"
        self.claude_mode = claude_mode
        self._seq = 0

    # build -------------------------------------------------------------------------------------------------------
    def build(self, owner_files: bool = False) -> "World":
        require_operator()
        for d in (self.op / "queue", self.home, self.scratch / "log", self.scratch / "acts", self.transcripts,
                  self.stubs, self.tmp, self.marks):
            d.mkdir(parents=True, exist_ok=True)
        shutil.copytree(OPERATOR_SRC, self.install, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        self.write_approved()
        if owner_files:
            self.plant_owner_files()
        self._home()
        self._stubs()
        self._repo()
        (self.scratch / "log" / "cto-session.txt").write_text(SID + "\n")
        self.transcript().write_text("")
        self.set_clock(NOW)
        self.crontab_store.write_text("0 4 * * * /bin/true # the nightly (planted)\n")
        self.calls.write_text("")
        self.write_config()
        return self

    def write_config(self, **over):
        cfg = {
            "operator_root": str(self.op), "repo": str(self.repo), "home": str(self.home),
            "scratch": str(self.scratch), "transcripts": str(self.transcripts), "clock": str(self.clock),
            "pings_log": str(self.pings), "push_cmd": str(self.stubs / "push"), "calls": str(self.calls),
            "close_flag": str(self.close_flag), "nightly_window": "21:00-22:00", "poll_s": 0.2,
        }
        cfg.update(over)
        self.config.write_text(json.dumps(cfg, indent=1) + "\n")

    def write_approved(self):
        lines = []
        for p in sorted(self.install.rglob("*")):
            if p.is_file() and p.name != "APPROVED" and "__pycache__" not in p.parts:
                lines.append(f"{sha256_file(p)}  {p.relative_to(self.install).as_posix()}")
        (self.install / "APPROVED").write_text("\n".join(lines) + "\n")

    def approved_sha(self) -> str:
        return sha256_file(self.install / "APPROVED")

    def reviewer_brief_sha(self) -> str:
        p = self.install / "reviewer-brief.md"
        return sha256_file(p) if p.is_file() else "0" * 64

    OWNER_FILES = {"CLAUDE.md": "# The owner's hand operator (planted): never the agent's configuration.\n",
                   ".claude/settings.json": '{"permissions": {"allow": ["Bash(*)"]}, "planted": "owner"}\n',
                   "hooks/notify.sh": "#!/bin/sh\necho owner hook\n",
                   "log/2026-11-08.log": "owner operator session log (planted)\n"}

    def plant_owner_files(self):
        for rel, text in self.OWNER_FILES.items():
            p = self.op / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)

    def _home(self):
        files = {
            ".gitconfig": "[user]\n\tname = Planted\n\temail = planted@example.invalid\n[init]\n\tdefaultBranch = main\n"
                          "[protocol \"file\"]\n\tallow = always\n[advice]\n\tdetachedHead = false\n",
            ".local/bin/gov": "#!/bin/sh\necho 'the pinned gov (planted)'\n",
            ".claude/settings.json": '{"planted": "user settings"}\n',
            ".gov-os/machine/gate.json": '{"planted": true}\n',
            ".cache/gov-os/index.txt": "planted cache\n",
        }
        for rel, text in files.items():
            p = self.home / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
        (self.home / ".local/bin/gov").chmod(0o755)

    def _stubs(self):
        def put(name, text, mode=0o755):
            p = self.stubs / name
            p.write_text(text)
            p.chmod(mode)
        put("claude", CLAUDE_STUB.replace("@PY@", PY).replace("@LOG@", repr(str(self.claude_log)))
            .replace("@MODE@", repr(self.claude_mode)))
        put("crontab", CRONTAB_STUB.replace("@STORE@", shlex.quote(str(self.crontab_store))))
        put("push", PUSH_STUB.replace("@PY@", PY).replace("@LOG@", repr(str(self.pushes))))
        for name in ("sudo", "pkill", "killall"):
            put(name, RECORDING_STUB.replace("@NAME@", name).replace("@MARK@", shlex.quote(str(self.marks / "forbidden"))))

    def _repo(self):
        self.repo.mkdir(parents=True)
        files = dict(REPO_FILES)
        files["governance/project/held-out.yaml"] = (
            f"held_out_paths:\n  - {self.home}/gov-os-workbench/qualification-oracle\n")
        for rel, text in files.items():
            p = self.repo / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
        (self.repo / ".claude/hooks/pretooluse.py").chmod(0o755)
        shutil.copytree(WALLS_SRC, self.repo / "governance/project/indep-walls")
        self.git("init", "-q", "-b", "main")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "planted base", "-m", f"Task: {CTO_TASK}\nRole: orchestrator")
        (self.repo / ".git/info").mkdir(exist_ok=True)
        with open(self.repo / ".git/info/exclude", "a") as f:
            f.write(f"\n{LIVE_MARKER}\n")
        (self.repo / LIVE_MARKER).write_text("the live planted repository\n")
        hook = self.repo / ".git/hooks/reference-transaction"
        hook.write_text("#!/bin/sh\n# planted git hook\nexit 0\n")
        hook.chmod(0o755)
        subprocess.run(["git", "init", "-q", "--bare", str(self.remote)], check=True, env=self.env(),
                       capture_output=True)
        self.git("remote", "add", "origin", str(self.remote))
        self.git("push", "-q", "origin", "main")

    # environment and processes ------------------------------------------------------------------------------------
    def env(self, **extra) -> dict:
        path = os.pathsep.join([str(self.stubs), str(Path(PY).parent), "/usr/local/bin", "/usr/bin", "/bin"])
        env = {"HOME": str(self.home), "PATH": path, "TMPDIR": str(self.tmp), "LANG": "C.UTF-8",
               "USER": os.environ.get("USER", "planted"), "PYTHONDONTWRITEBYTECODE": "1",
               "PYTHONUSERBASE": USER_BASE, "GIT_CONFIG_NOSYSTEM": "1"}
        env.update({k: str(v) for k, v in extra.items()})
        return env

    def git(self, *args, cwd=None) -> str:
        p = subprocess.run(["git", *args], cwd=cwd or self.repo, env=self.env(), capture_output=True, text=True,
                           timeout=60)
        if p.returncode != 0:
            raise AssertionError(f"git {' '.join(args)} failed: {p.stderr.strip()}")
        return p.stdout

    def head(self) -> str:
        return self.git("rev-parse", "HEAD").strip()

    def run_cmd(self, script: str, args, env_extra=None, timeout=180) -> Result:
        cmd = [PY, "-B", str(self.install / script), "--config", str(self.config), *[str(a) for a in args]]
        p = subprocess.run(cmd, cwd=self.base, env=self.env(**(env_extra or {})), capture_output=True, text=True,
                           timeout=timeout)
        return Result(p.returncode, last_json(p.stdout), p.stdout, p.stderr)

    def run(self, bundle: Bundle | None = None, step: str = "run", act=None, sha=None, env_extra=None) -> Result:
        """``python3 <install>/operator_run.py --config <config> <step> <ACT> <manifest sha>``."""
        act = act or (bundle.act if bundle else None)
        sha = sha or (bundle.sha if bundle else None)
        return self.run_cmd("operator_run.py", [step, act, sha], env_extra)

    def start(self, bundle: Bundle, env_extra=None) -> subprocess.Popen:
        """The same run in the background, in its own process group (stopped by pgid, never by name)."""
        cmd = [PY, "-B", str(self.install / "operator_run.py"), "--config", str(self.config), "run", bundle.act,
               bundle.sha]
        return subprocess.Popen(cmd, cwd=self.base, env=self.env(**(env_extra or {})), stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, start_new_session=True)

    @staticmethod
    def stop(proc: subprocess.Popen):
        """Stop a background run by its process group id (its own session), never by a name."""
        if proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            try:
                proc.communicate(timeout=30)
            except Exception:
                pass

    def digest(self, since="2026-11-01T00:00:00+00:00") -> Result:
        return self.run_cmd("operator_run.py", ["digest", "--since", since])

    def launch(self, env_extra=None) -> Result:
        """``python3 <install>/operator_launch.py --config <config>``."""
        return self.run_cmd("operator_launch.py", [], env_extra)

    # state ---------------------------------------------------------------------------------------------------------
    def set_clock(self, iso: str):
        self.clock.write_text(iso + "\n")

    def transcript(self, sid=SID) -> Path:
        return self.transcripts / f"{sid}.jsonl"

    def say(self, *lines, sid=SID):
        with open(self.transcript(sid), "a") as f:
            for line in lines:
                f.write(json.dumps(line) + "\n")

    def read(self, root: str, path: str) -> bytes | None:
        if root == "crontab":
            return self.crontab_store.read_bytes()
        p = (self.repo if root == "repo" else self.home) / path
        return p.read_bytes() if p.is_file() else None

    def queue(self, line: str, name: str | None = None) -> Path:
        self._seq += 1
        p = self.op / "queue" / (name or f"20261110T1000{self._seq:02d}Z-request.req")
        p.write_text(line)
        t = time.time() - 1000 + self._seq
        os.utime(p, (t, t))
        return p

    def log(self) -> list:
        return read_jsonl(self.op / "log" / "operator.jsonl")

    def gate_lines(self, act: str) -> list:
        return [line for line in self.log() if line.get("act") == act]

    def notices(self, act: str | None = None) -> list:
        out = []
        for rec in read_jsonl(self.pushes):
            argv = rec.get("argv") or []
            try:
                n = json.loads(argv[0]) if argv else {}
            except ValueError:
                n = {"text": " ".join(argv)}
            if not isinstance(n, dict):
                n = {"text": str(n)}
            if act is None or n.get("act") == act or names(act, json.dumps(n)):
                out.append(n)
        return out

    def p1s(self, act: str) -> list:
        return [n for n in self.notices(act) if str(n.get("priority", "")).upper() == "P1"]

    def claude_calls(self) -> list:
        return read_jsonl(self.claude_log)

    def trailers(self, rev="HEAD") -> list:
        out = self.git("log", "-1", "--format=%(trailers:only,unfold)", rev)
        pairs = []
        for line in out.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                pairs.append((k.strip(), v.strip()))
        return pairs

    def committed_files(self, rev="HEAD") -> set:
        return {x for x in self.git("show", "--name-only", "--format=", rev).splitlines() if x.strip()}

    def frozen_dirs(self, bundle: Bundle) -> list:
        acts = self.op / "acts"
        return sorted(p for p in acts.glob(f"*{bundle.sha[:12]}*") if p.is_dir()) if acts.is_dir() else []

    def snapshot(self) -> dict:
        """Every live file's hash (repository without .git but its hooks, HOME), HEAD, the index, the crontab."""
        snap = {}
        for top, name in ((self.repo, "repo"), (self.home, "home")):
            for p in sorted(top.rglob("*")):
                rel = p.relative_to(top).as_posix()
                if name == "repo" and (rel == ".git" or rel.startswith(".git/")) and not rel.startswith(".git/hooks/"):
                    continue
                if p.is_file() and not p.is_symlink():
                    snap[f"{name}:{rel}"] = sha256_file(p)
        snap["HEAD"] = self.head()
        snap["index"] = self.git("diff", "--cached", "--name-status")
        snap["crontab"] = sha256_file(self.crontab_store)
        snap["remote"] = subprocess.run(["git", "--git-dir", str(self.remote), "show-ref"], env=self.env(),
                                        capture_output=True, text=True).stdout
        snap["tags"] = self.git("tag", "--list")
        return snap

    def forbidden_calls(self) -> str:
        p = self.marks / "forbidden"
        return p.read_text() if p.exists() else ""

    # bundles -------------------------------------------------------------------------------------------------------
    def bundle(self, act: str, changes, **kw) -> Bundle:
        return write_bundle(self.scratch / "acts" / act, act, changes, **kw)

    def review(self, b: Bundle, *, cls=None, sha=None, reviewer="independent-reviewer-7", brief_sha=None,
               at=REVIEW_TIME, kpis=None, rounds=1, raw_block=None, extra=None, no_block=False) -> Path:
        block = {"manifest_sha256": sha or b.sha, "class": cls or b.manifest["claimed_class"], "reviewer": reviewer,
                 "reviewer_brief_sha256": brief_sha or self.reviewer_brief_sha(), "time": at,
                 "kpis": kpis or [{"kpi": "S1", "verdict": "pass", "findings": []}]}
        block.update(extra or {})
        text = f"# Review of {b.act} (planted)\n\nThe reviewer read the manifest and the rehearsal log.\n\n"
        if not no_block:
            for r in range(rounds):
                text += f"## Round {r + 1}\n\n" + verdict_block(raw_block if raw_block is not None else block) + "\n"
        p = b.dir / "review.md"
        p.write_text(text)
        return p

    def ready(self, act: str, changes, *, claimed="a", review_cls=None, review_kw=None, **kw) -> Bundle:
        b = self.bundle(act, changes, claimed=claimed, **kw)
        self.review(b, cls=review_cls or claimed, **(review_kw or {}))
        return b

    # common changes ------------------------------------------------------------------------------------------------
    def change(self, root, path, after: bytes | None) -> Change:
        return Change(root, path, self.read(root, path), after)

    def optin_removal(self, path="tests/optin-lifted.txt", index=1) -> Change:
        """(a): one line removed from an opt-in list."""
        lines = self.read("repo", path).decode().splitlines(keepends=True)
        del lines[index]
        return self.change("repo", path, "".join(lines).encode())

    def deny_addition(self, item="Bash(git push *)") -> Change:
        """(a): one item added to the settings' permissions.deny."""
        data = json.loads(self.read("repo", ".claude/settings.json"))
        data["permissions"]["deny"].append(item)
        return self.change("repo", ".claude/settings.json", settings_text(data).encode())

    def hook_change(self) -> Change:
        """(b): the guard hook's code."""
        return self.change("repo", ".claude/hooks/pretooluse.py",
                           self.read("repo", ".claude/hooks/pretooluse.py") + b"# tightened (planted)\n")

    def src_change(self) -> Change:
        """(O): src/** is not an ACT's business."""
        return self.change("repo", "src/gov/planted.py", b"VALUE = 2\n")

    def pathmap_addition(self, glob="fixtures/evaluation/new-set/hidden/**") -> Change:
        """(a): one glob added to sets_root_hidden's hidden list."""
        text = self.read("repo", "governance/project/path-map.yaml").decode()
        old = '"transcripts/**"]'
        assert old in text
        return self.change("repo", "governance/project/path-map.yaml",
                           text.replace(old, f'"transcripts/**", "{glob}"]').encode())


# --- DEC-1106 (1): concurrent changes at a test hook point, the lock, the P1's names ------------------------------

CONCURRENT_HOOK = r'''#!@PY@
"""A planted concurrent change (W2-148 acceptance, DEC-1106 (1)): at one point of GOV_OPERATOR_TEST_HOOK it writes
files and makes commits in the live planted repository, as the CTO's session might while the operator runs, then
records that it ran and the live HEAD. Absolute paths and its own git environment: the cwd it is run with is free.
A commit names its paths (git commit's --only form), so anything the operator has staged stays staged and uncommitted."""
import base64, json, os, subprocess, sys
POINT, MARKS, REPO = @POINT@, @MARKS@, @REPO@
ACTIONS, ENV = json.loads(@ACTIONS@), json.loads(@ENV@)
if len(sys.argv) < 2 or sys.argv[1] != POINT:
    sys.exit(0)
for kind, target, arg in ACTIONS:
    if kind == "write":
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "wb") as f:
            f.write(base64.b64decode(arg))
    elif kind == "commit":
        subprocess.run(["git", "add", "--", *target], cwd=REPO, env=ENV, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-q", "-m", arg, "-m", "Task: @TASK@\nRole: orchestrator", "--", *target],
                       cwd=REPO, env=ENV, check=True, capture_output=True)
head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, env=ENV, capture_output=True, text=True).stdout.strip()
with open(os.path.join(MARKS, "hook-head"), "w") as f:
    f.write(head)
with open(os.path.join(MARKS, "hook-" + POINT), "w") as f:
    f.write(sys.argv[2] if len(sys.argv) > 2 else "")
'''


def concurrent_hook(w: "World", path: Path, point: str, actions) -> Path:
    """Write a GOV_OPERATOR_TEST_HOOK executable that, at ``point`` only, performs ``actions`` in order:
    ``("write", <absolute path>, <bytes>)`` or ``("commit", [<repo-relative paths>], <subject>)``."""
    enc = []
    for kind, target, arg in actions:
        if kind == "write":
            enc.append([kind, str(target), base64.b64encode(arg).decode()])
        else:
            enc.append([kind, list(target), arg])
    text = (CONCURRENT_HOOK.replace("@PY@", PY).replace("@POINT@", repr(point)).replace("@MARKS@", repr(str(w.marks)))
            .replace("@REPO@", repr(str(w.repo))).replace("@ACTIONS@", repr(json.dumps(enc)))
            .replace("@ENV@", repr(json.dumps(w.env()))).replace("@TASK@", CTO_TASK))
    path = Path(path)
    path.write_text(text)
    path.chmod(0o755)
    return path


def hook_ran(w: "World", point: str) -> bool:
    return (w.marks / f"hook-{point}").exists()


def hook_head(w: "World") -> str:
    p = w.marks / "hook-head"
    return p.read_text().strip() if p.exists() else ""


def assert_touched(w: "World", b: Bundle, side: str):
    """Every touched file of ``b`` at its ``before`` or ``after`` hash (a missing file is the null hash)."""
    for t in b.manifest["touched"]:
        data = w.read(t["root"], t["path"])
        assert (None if data is None else sha256_bytes(data)) == t[side], f"{t['path']} is not at its {side} bytes"


def p1_missing(w: "World", act: str, *paths: str, phrase: str | None = None) -> list:
    """The paths (and the phrase) that no P1 notice's ``text`` for ``act`` names; empty when every one is named."""
    texts = [str(n.get("text", "")) for n in w.p1s(act)]
    missing = [p for p in paths if not any(p in t for t in texts)]
    if phrase and not any(phrase in t for t in texts):
        missing.append(phrase)
    return missing


def assert_lock_held(w: "World", act: str = "ACT-T-NEXT"):
    """The lock is held: a next ACT, ready on its own and queued, is not launched and changes nothing (S22's form:
    the launcher refuses, at most the canary's one stub call, the next ACT's file still at its before bytes)."""
    calls = len(w.claude_calls())
    nxt = w.ready(act, [w.optin_removal("tests/optin-lifted-breadth.txt")])
    w.queue(f"{nxt.act} {nxt.sha}\n")
    r = w.launch()
    assert r.out.get("result") != "launched", ("the lock was not held: the next queued ACT was launched", r.out)
    assert len(w.claude_calls()) - calls <= 1, "a real session started while the lock was held"
    assert_touched(w, nxt, "before")


def names(act: str, text: str) -> bool:
    """Whether ``text`` names ``act`` as a whole id (ACT-T-D1 is not named by ACT-T-D14)."""
    return re.search(re.escape(act) + r"(?![\w-])", text or "") is not None


def wait_for(predicate, timeout=30.0, step=0.1) -> bool:
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if predicate():
            return True
        time.sleep(step)
    return predicate()


def evidence_tables(text: str) -> list:
    """Every Markdown table of the evidence record as (header cells, [row cells]), header cells lower-cased."""
    tables, cur = [], None
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            cur = None
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cur is None:
            cur = ([c.lower() for c in cells], [])
            tables.append(cur)
            continue
        if all(re.fullmatch(r":?-+:?", c) for c in cells if c):
            continue
        cur[1].append(cells)
    return tables


def find_table(text: str, *names: str):
    """The first table whose header holds a cell starting with each of ``names`` (lower case)."""
    for header, rows in evidence_tables(text):
        idx = []
        for n in names:
            i = next((k for k, h in enumerate(header) if h.startswith(n)), None)
            if i is None:
                break
            idx.append(i)
        else:
            return idx, rows
    return [None] * len(names), []
