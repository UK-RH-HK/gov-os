#!/usr/bin/env python3
"""The independent sessions' launch script (W2-149; DEC-1101 (2)-(3) step 2, DEC-1109 (2); ACT-INDEP-WALLS-1).

Builds one walled folder for one job (writer, checker, auditor, labeller) from an owner-approved brief and the walls'
template, chooses its content by rule from a seed recorded first, checks with a canary that the wall's settings load,
starts one closed headless `claude -p` session in it, delivers its product by its own code and returns only counts.
Standard library, PyYAML and git; no gov import. The CTO runs it, from the repository:

  python3 governance/project/orchestration/tools/indep_launch.py --sets-root ~/gov-os-eval --kind writer --brief governance/project/indep-briefs/writer.md --brief-sha256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 --commit 6ff398a28 --set memory-recall-3 --round 1
  python3 governance/project/orchestration/tools/indep_launch.py --sets-root ~/gov-os-eval --kind checker --brief governance/project/indep-briefs/checker.md --brief-sha256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 --commit 6ff398a28 --set memory-recall-3 --round 1
  python3 governance/project/orchestration/tools/indep_launch.py --sets-root ~/gov-os-eval --kind auditor --brief governance/project/indep-briefs/auditor.md --brief-sha256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 --commit 6ff398a28 --set memory-recall-3 --audit e0
  python3 governance/project/orchestration/tools/indep_launch.py --sets-root ~/gov-os-eval --kind writer --brief governance/project/indep-briefs/sgx1/writer-tuning.md --brief-sha256 82134b3dd6b5a077abfc2eb6fa7481f0f5a73eab60396cfbd655042d53027c57 --commit 6ff398a28 --set tuning --round 1
  python3 governance/project/orchestration/tools/indep_launch.py --sets-root ~/gov-os-eval --kind writer --brief governance/project/indep-briefs/sgx1/writer-heldout.md --brief-sha256 137a73d1df4c265fd5ce4e24716797703e2b12dcaeb90663c0170834a60fafe6 --commit 6ff398a28 --set held-out --round 1
  python3 governance/project/orchestration/tools/indep_launch.py --sets-root ~/gov-os-eval --kind labeller --brief governance/project/indep-briefs/sgx1/labeller.md --brief-sha256 bbff1249953bd9d3b2596b33a108712bdddd79a7e86723b9e6955e3d6b0e9068 --commit 6ff398a28 --set tuning --round 2
  python3 governance/project/orchestration/tools/indep_launch.py --sets-root ~/gov-os-eval --kind labeller --brief governance/project/indep-briefs/sgx1/labeller-2.md --brief-sha256 e13b5f96d0e058277f3ec3014f13205d7fe0bc950cfc308e81b3ee3d742ac904 --commit 6ff398a28 --set held-out --round 2
  python3 governance/project/orchestration/tools/indep_launch.py --sets-root ~/gov-os-eval --kind auditor --brief governance/project/indep-briefs/sgx1/overlap-auditor.md --brief-sha256 b212a424062e402b0a25ee4a157ae14a0af798d0ad973aa33dacd730782be6ab --commit 6ff398a28 --set held-out --audit sgx1-overlap
  python3 governance/project/orchestration/tools/indep_launch.py --sets-root /tmp/planted-sets --kind writer --brief governance/project/indep-briefs/writer.md --brief-sha256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 --commit 6ff398a28 --set memory-recall-3 --seed 17 --dry
  python3 governance/project/orchestration/tools/indep_launch.py --sets-root ~/gov-os-eval --kind writer --run 20261109T120000Z-memory-recall-3-r1 --counts-only

The line names only --sets-root <root>: never a folder under it (the guard's line rule, DEC-1097 (2)); the script
derives every folder under the root in its own code. --dry belongs on planted sets roots only: it leaves its wall and
tree in place for inspection (P-W2-149-DRY, option (a)).

Set-up A (SANDBOX-GUARD-EXP-1; DEC-1112 (3), DEC-1113): a brief whose front matter names a `brief:` id takes its
missing `model`, `result_schema` and `sample` from that id's entry under the template kinds.yaml's `briefs:`, and the
entry's `flow`: the two planted-case writers, the two labellers (the labeller kind runs these flows only) and the
overlap auditor. `--set` names the half (`tuning`: <runs>/SANDBOX-GUARD-EXP-1/tuning; `held-out`: the sealed folder
under the sets root); the inputs are staged and the products delivered by the script's own code. The first
labeller's rule script runs confined (bwrap, no network, no process, capped) at its round-1 delivery (else 20, nothing
lands) and again at its round 2 (else code 18). A result whose `stopped` is not `none` delivers nothing (20).

The memory audit's follow-ups (W2-173; DEC-1120 (2)-(3), DEC-1101 (2)): a brief's front matter may name `effort`
(low, medium, high, xhigh or max; any other value 10), passed to the canary and the session as --effort and recorded
in WALL.json and the counts (null when the brief names none). A memory writer's or checker's result whose `stopped` is
not `none` delivers nothing (21). The checker's notes.md and the auditor's classes.json are checked against their
briefs' fixed form (section 6) and the result's counts before they are delivered (else 20, nothing lands).

The auditor's copy of a set (W2-178; W2-170's Interface, DEC-1101 (2)): every file of the set's hidden half except
those under its `hidden/dropped/` folder (any depth below it); the writer's round 2 and the checker's copies are
unchanged. A link anywhere under `hidden/` still refuses 10, and a set empty after the exclusion refuses 10 as any other.

Exit codes: 0 delivered or dry; 10 brief; 11 template; 12 wall or tree exists; 13 seed not first; 14 commit; 15 file
budget; 16 canary; 17 argument; 18 the rule script; 20 result rejected; 21 stopped; 22 a trace. Stdout's last line is
the counts object (indep-schemas/indep-counts.schema.json), also written as <runs>/indep/<kind>/<run>/counts.json
once a run id exists. No text from the session or out/ is printed or logged, and no path under the wall.
"""
import argparse
import fnmatch
import hashlib
import json
import math
import os
import posixpath
import random
import re
import secrets
import selectors
import shutil
import signal
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
import uuid

import yaml

ACT = "ACT-INDEP-WALLS-1"
KINDS = ("writer", "checker", "auditor", "labeller")
TOOLS_OK = ("Read", "Grep", "Glob", "Write", "Edit", "MultiEdit", "TodoWrite")
REFUSAL_KEYS = ("Read", "Grep", "Glob", "Write", "Edit", "MultiEdit", "TodoWrite", "Bash", "WebFetch", "WebSearch",
                "Task", "Agent", "NotebookEdit", "Skill", "other")
WALLS = "indep-" + "walls"  # the walls' folder under the sets root, and the template's folder in the repository
TEMPLATE_DIR = "governance/project/" + WALLS
TEMPLATE_FILES = ("settings.json.tmpl", "wall_hook.py", "CLAUDE.md.tmpl", "kinds.yaml", "tree-exclude.txt",
                  "README.md")
PATH_MAP = "governance/project/path-map.yaml"
SCHEMAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "indep-schemas")
COUNTS_SCHEMA = "indep-counts.schema.json"
NAME_RX = re.compile(r"[a-z0-9][a-z0-9-]{0,63}")
RUN_RX = re.compile(r"[0-9]{8}T[0-9]{6}Z-[a-z0-9][a-z0-9-]*-r[12]")
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
MODEL_RX = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:\[\]-]{0,127}")
SCHEMA_NAME_RX = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\.schema\.json")
COMMIT_RX = re.compile(r"[0-9A-Za-z][0-9A-Za-z._/~^-]{0,255}")
SESSION_ID_RX = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{7,127}")
CODES = {10: "brief", 11: "template", 12: "wall_exists", 13: "seed_order", 14: "commit", 15: "file_budget",
         16: "canary", 17: "argument", 18: "rules", 20: "result", 21: "stopped", 22: "trace"}
DELIVERS = {"writer": "set", "checker": "notes", "auditor": "classes", "labeller": "labels"}
OUT_KEYS = {"writer": ("questions", "by_kind", "by_area"),
            "checker": ("checked", "accepted", "revise", "rejected"),
            "auditor": ("misses",),
            "labeller": ("labelled", "allow", "refuse", "agree", "disagree")}
BY_KIND = ("fact", "procedure", "decision", "location", "negative")
BY_AREA = ("contract", "decisions", "kernel", "code", "tests", "operations", "docs")
MISS_CLASSES = ("gold_wrong", "question_ambiguous", "retrieval_miss", "answer_wrong", "out_of_scope")
SEAL = "fixtures/evaluation/sandbox-guard-exp-1/hidden"  # the held-out half's sealed folder under the sets root
# Set-up A (DEC-1112 (3), DEC-1113): each flow's kind, the halves --set may name and the rounds --round may name.
FLOWS = {"sgx1-writer-1": ("writer", ("tuning",), (1,)),
         "sgx1-writer-2": ("writer", ("held-out",), (1,)),
         "sgx1-labeller-1": ("labeller", ("tuning", "held-out"), (1, 2)),
         "sgx1-labeller-2": ("labeller", ("tuning", "held-out"), (1, 2)),
         "sgx1-overlap-auditor": ("auditor", ("tuning", "held-out"), (1,))}
EXP = "SANDBOX-GUARD-EXP-1"       # <runs>/SANDBOX-GUARD-EXP-1: the experiment's folder (the tuning half under it)
SEAL_SET = "sandbox-guard-exp-1"  # the evaluation set the seal's path-map entry names
ROUND1_FILES = {"sgx1-labeller-1": ("label_rules.py", "rulebook.md"), "sgx1-labeller-2": ("rulebook-2.md",)}
ACTION_FIELDS = ("id", "role", "agent", "ticket", "wbs", "tool", "input", "cwd", "executable", "strata", "source")
DISPUTE_ACTION = ("role", "agent", "ticket", "wbs", "tool", "input", "cwd")
LABEL_PART = ("label", "rule_class", "clauses", "reason")
LABELS = ("allow", "refuse", "ask")
AUDIT_SPLIT = 40                  # the overlap auditor's cases per run (the CTO's delegated split)
SGX_OUT = ("round", "cases", "copies", "near_miss", "not_executable", "rules", "hand_labelled", "ask", "by_class",
           "uncertain_seen", "sample", "decided", "agrees_x", "agrees_y", "neither", "cannot_settle",
           "may_change_verdict", "instructions_ignored", "stopped", "labelled", "allow", "refuse")
STOPPED = ("none", "input-missing", "input-malformed", "decisions-conflict", "forbidden-read-needed",
           "form-not-writable", "not-sealed")
EFFORTS = ("low", "medium", "high", "xhigh", "max")  # a brief's `effort`, passed as --effort (W2-173 S1)
# The checker's notes.md and the auditor's classes.json, as the memory audit's briefs fix them (§6; W2-173 S3, S4).
NOTES_HEAD = "# Cross-check notes"
NOTES_SET = ("domains:", "categories:", "keyword:", "supersession ", "set codes:")
VERDICTS = ("accept", "revise", "reject")
REASON_MOST = 200
# The confined rule script (S25): its caps; the prelude below sets them inside the sandbox before the script's code runs.
RULES_WALL_S = 20                 # wall-clock seconds (at most 60)
RULES_CPU_S = 15
RULES_AS = 1 << 30                # address space, bytes
RULES_NOFILE = 32
RULES_OUT_BASE = 1 << 20          # stdout cap: this much plus RULES_OUT_PER_ID per staged id
RULES_OUT_PER_ID = 4096
FILE_BUDGET = 8000
WALL_FIXED = 7  # seed.txt brief.md CLAUDE.md WALL.json input/selection.json .claude/settings.json .claude/wall_hook.py
RUN_EXTRA = 3   # beside the fixed files and the staged copies: <run>.session.json, out/result.json, the delivered file
KILL_AFTER = 30
CANARY_LIMIT = 60
CANARY_KILL_AFTER = 5
MOST_HIDDEN = 10000
MOST_RESULT_BYTES = 1 << 20
MOST_SESSION_BYTES = 64 << 20
SESSION_ENV = ("HOME", "PATH", "LANG", "USER")
HOOK_POINTS = ("before_wall", "after_seed", "after_tree", "after_input", "before_canary", "before_session",
               "after_session")
TRACE_DIRS = ("projects", "file-history", "session-env", "todos")
# The fixed launch prompt: one line, no content of its own, no absolute path. Its sha256 is the constant below.
PROMPT = ("Follow brief.md in this folder exactly, and finish by writing out/result.json in the schema the brief "
          "names.")
PROMPT_SHA256 = "b86c5a8e5953db3e02c6e5b0128f66e75f0eed8e0b6429e62f71d103042b0189"
# The rule script's prelude, run by the pinned interpreter inside bwrap (`-I -X utf8 -c <prelude> <script>`): it reads
# the script, sets every cap as a hard limit (no process: RLIMIT_NPROC 0; no file written: RLIMIT_FSIZE 0), installs a
# seccomp filter that refuses exec, fork/clone, socket and namespace calls (any other architecture: killed), and only
# then runs the script's code. A failure anywhere exits non-zero, which the launcher takes as code 18.
RULES_PRELUDE = r'''
import ctypes, os, resource, struct, sys
path = sys.argv[1]
with open(path, "rb") as f:
    src = f.read()
for r, v in ((resource.RLIMIT_NPROC, 0), (resource.RLIMIT_FSIZE, 0), (resource.RLIMIT_CORE, 0),
             (resource.RLIMIT_NOFILE, @NOFILE@), (resource.RLIMIT_CPU, @CPU@), (resource.RLIMIT_AS, @AS@)):
    resource.setrlimit(r, (v, v))
if os.uname().machine != "x86_64":
    sys.exit(70)
DENY = (41, 53, 56, 57, 58, 59, 272, 308, 322, 435)  # socket socketpair clone fork vfork execve unshare setns execveat clone3
def ins(code, jt, jf, k):
    return struct.pack("=HBBI", code, jt, jf, k)
d = 6 + len(DENY)
prog = [ins(0x20, 0, 0, 4), ins(0x15, 1, 0, 0xC000003E), ins(0x06, 0, 0, 0x80000000), ins(0x20, 0, 0, 0),
        ins(0x35, d - 5, 0, 0x40000000)]
prog += [ins(0x15, d - (6 + i), 0, nr) for i, nr in enumerate(DENY)]
prog += [ins(0x06, 0, 0, 0x7FFF0000), ins(0x06, 0, 0, 0x00050001)]
buf = ctypes.create_string_buffer(b"".join(prog))
class Prog(ctypes.Structure):
    _fields_ = [("len", ctypes.c_ushort), ("filter", ctypes.c_void_p)]
fprog = Prog(len(prog), ctypes.addressof(buf))
libc = ctypes.CDLL(None, use_errno=True)
libc.prctl.argtypes = [ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong]
if libc.prctl(38, 1, 0, 0, 0) != 0 or libc.prctl(22, 2, ctypes.addressof(fprog), 0, 0) != 0:
    sys.exit(71)
sys.argv = [path]
exec(compile(src, path, "exec"), {"__name__": "__main__", "__file__": path, "__builtins__": __builtins__})
'''.replace("@NOFILE@", str(RULES_NOFILE)).replace("@CPU@", str(RULES_CPU_S)).replace("@AS@", str(RULES_AS))


class Refuse(Exception):
    """A refusal with its exit code."""

    def __init__(self, code, word=""):
        super().__init__(word)
        self.code = code
        self.word = word


class ArgError(Exception):
    pass


class Interrupted(Exception):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgError("parse")


# -- small helpers -------------------------------------------------------------------------------------------------
def utc_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(path):
    h = hashlib.sha256()
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def full(rx, s):
    return isinstance(s, str) and rx.fullmatch(s) is not None


def at_or_under(path, top):
    return path == top or path.startswith(top.rstrip("/") + "/")


def is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def is_count(v):
    return isinstance(v, int) and not isinstance(v, bool) and v >= 0


def num_text(v):
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return repr(v) if isinstance(v, float) else str(v)


def write_new(path, data, mode):
    """A new file (never through a link, never over an existing entry), then its mode."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(data)
    os.chmod(path, mode)


def copy_new(src, dst, mode):
    """Copy one regular file (no link followed) to a new file; returns the copy's sha256 as read back."""
    fd = os.open(src, os.O_RDONLY | os.O_NOFOLLOW)
    if not stat.S_ISREG(os.fstat(fd).st_mode):
        os.close(fd)
        raise ValueError("not a file")
    out = os.open(dst, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "rb") as fi, os.fdopen(out, "wb") as fo:
        shutil.copyfileobj(fi, fo, 1 << 20)
    os.chmod(dst, mode)
    return sha_file(dst)


def plain_files(top):
    """The files below a folder as sorted relative paths; a link or any other entry raises."""
    found = []
    for folder, dirs, names in os.walk(top):
        for d in dirs:
            if os.path.islink(os.path.join(folder, d)):
                raise ValueError("link")
        for n in names:
            p = os.path.join(folder, n)
            if not stat.S_ISREG(os.lstat(p).st_mode):
                raise ValueError("not a file")
            found.append(os.path.relpath(p, top))
    return sorted(found)


def remove_tree(path):
    """Remove a folder this script built (read-only folders included); links are removed, never followed."""
    if not os.path.lexists(path):
        return
    if os.path.islink(path) or not os.path.isdir(path):
        os.unlink(path)
        return
    for folder, _dirs, _names in os.walk(path):
        os.chmod(folder, 0o700)
    shutil.rmtree(path)


def wait_past(ns, folder):
    """Wait until a file made in *folder* carries an mtime (ns) strictly later than *ns* (a coarse clock's tick)."""
    end = time.monotonic() + 5
    while True:
        fd, probe = tempfile.mkstemp(prefix=".tick-", dir=folder)
        try:
            now = os.fstat(fd).st_mtime_ns
        finally:
            os.close(fd)
            os.unlink(probe)
        if now > ns:
            return
        if time.monotonic() > end:
            raise RuntimeError("clock")
        time.sleep(0.002)


def load_json_strict(data):
    def no_constant(_x):
        raise ValueError("constant")
    return json.loads(data, parse_constant=no_constant)


def read_schema(name):
    """One schema of indep-schemas/, read once: (its sha256, the object parsed from those same bytes), or
    (None, None) when it is not a plain file holding a JSON object (F8)."""
    path = os.path.join(SCHEMAS, name)
    try:
        if not stat.S_ISREG(os.lstat(path).st_mode):
            return None, None
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, "rb") as f:
            data = f.read()
        obj = load_json_strict(data.decode("utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return None, None
    return (sha_bytes(data), obj) if isinstance(obj, dict) else (None, None)


# -- a small JSON schema check (the subset the schemas here use; an unknown keyword fails closed) ------------------
_ANNOTATIONS = {"$schema", "$id", "$comment", "title", "description", "examples", "default"}
_KEYWORDS = {"type", "const", "enum", "pattern", "minimum", "maximum", "required", "properties",
             "additionalProperties", "propertyNames", "items", "anyOf", "minLength", "maxLength"}


class _Invalid(Exception):
    pass


def _is_type(v, t):
    return {"null": v is None, "boolean": isinstance(v, bool), "object": isinstance(v, dict),
            "array": isinstance(v, list), "string": isinstance(v, str),
            "integer": isinstance(v, int) and not isinstance(v, bool),
            "number": is_number(v)}.get(t, False)


def _same(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    return a == b


def _check(v, s):
    if s is True:
        return
    if s is False or not isinstance(s, dict):
        raise _Invalid()
    if set(s) - _ANNOTATIONS - _KEYWORDS:
        raise _Invalid()
    if "type" in s:
        types = s["type"] if isinstance(s["type"], list) else [s["type"]]
        if not any(_is_type(v, t) for t in types):
            raise _Invalid()
    if "const" in s and not _same(v, s["const"]):
        raise _Invalid()
    if "enum" in s and not any(_same(v, e) for e in s["enum"]):
        raise _Invalid()
    if isinstance(v, str):
        if "pattern" in s and not re.search(s["pattern"], v):
            raise _Invalid()
        if "minLength" in s and len(v) < s["minLength"]:
            raise _Invalid()
        if "maxLength" in s and len(v) > s["maxLength"]:
            raise _Invalid()
    if is_number(v):
        if "minimum" in s and v < s["minimum"]:
            raise _Invalid()
        if "maximum" in s and v > s["maximum"]:
            raise _Invalid()
    if isinstance(v, dict):
        for k in s.get("required", []):
            if k not in v:
                raise _Invalid()
        props = s.get("properties", {})
        for k, x in v.items():
            if "propertyNames" in s:
                _check(k, s["propertyNames"])
            if k in props:
                _check(x, props[k])
            elif "additionalProperties" in s:
                _check(x, s["additionalProperties"])
    if isinstance(v, list) and "items" in s:
        for x in v:
            _check(x, s["items"])
    if "anyOf" in s:
        for alt in s["anyOf"]:
            try:
                _check(v, alt)
                break
            except _Invalid:
                continue
        else:
            raise _Invalid()


def schema_ok(value, schema):
    try:
        _check(value, schema)
        return True
    except (_Invalid, TypeError, re.error, RecursionError):
        return False


# -- the run's state, its log and its result line ------------------------------------------------------------------
class State:
    def __init__(self):
        self.stage = 17
        self.kind = None
        self.wall = None
        self.tree = None
        self.walls = None
        self.run = None
        self.counts_dir = None
        self.session_file = None
        self.built = False       # the wall folder was made by this run (B1 passed)
        self.tree_made = False
        self.dry = False
        self.replaced = None     # writer round 2: round 1's files moved aside inside hidden/, packed into the tar
        self.pgid = None
        self.home = None
        self.trace_ids = set()   # the canary's and the session's ids, drawn and reported: the trace check's keys only
        self.counts_schema = None  # read once at the start (F8); its sha256 goes into WALL.json
        self.counts_schema_sha = None
        self.log_lines = []
        self.counts = {
            "act": ACT, "kind": None, "run": None, "set": None, "round": None, "commit": None,
            "brief_sha256": None, "approved_sha256": None, "seed_sha256": None, "effort": None,
            "template_ok": False, "override": False,
            "selection": {"changed": None, "sample": None, "overlap": None},
            "session": {"exit": None, "is_error": None, "turns": None, "cost_usd": None, "duration_s": None,
                        "refusals": None},
            "out": dict({"schema_ok": None, "files": None},
                        **{k: None for kind in KINDS for k in OUT_KEYS[kind]}),  # every key on every result
            "delivered": {"files": 0, "sha256": None, "to": None},
            "traces": 0, "status": "refused", "code": None, "reason": None}

    def log(self, *words):
        self.log_lines.append(utc_iso() + " " + " ".join(str(w) for w in words))

    def set_kind(self, kind):
        self.kind = kind
        self.counts["kind"] = kind


def finish(st, code):
    c = st.counts
    c["code"] = code
    c["reason"] = CODES.get(code)
    line = json.dumps(c, separators=(", ", ": "))
    if st.counts_schema is None:
        st.log("counts", "schema", "unreadable")
    elif not schema_ok(c, st.counts_schema):
        st.log("counts", "schema", "failed")
    if st.counts_dir:
        try:
            os.makedirs(st.counts_dir, mode=0o755, exist_ok=True)
            tmp = os.path.join(st.counts_dir, ".counts.json.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(line + "\n")
            os.replace(tmp, os.path.join(st.counts_dir, "counts.json"))
            st.log("end", c["status"], code)
            with open(os.path.join(st.counts_dir, "launch.log"), "a", encoding="utf-8") as f:
                f.write("\n".join(st.log_lines) + "\n")
        except OSError:
            pass
    sys.stderr.write(f"indep_launch: {c['status']} {code}" + (f" {c['reason']}" if c["reason"] else "") + "\n")
    sys.stdout.write(line + "\n")
    sys.stdout.flush()
    return code


# -- git -----------------------------------------------------------------------------------------------------------
def git(repo, *args, stdin=None):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, input=stdin, timeout=600)


def blob(repo, commit, path):
    """The bytes of <commit>:<path> when it is a blob, else None."""
    t = git(repo, "cat-file", "-t", f"{commit}:{path}")
    if t.returncode != 0 or t.stdout.strip() != b"blob":
        return None
    b = git(repo, "cat-file", "blob", f"{commit}:{path}")
    return b.stdout if b.returncode == 0 else None


def z_list(out):
    return [x.decode("utf-8", "surrogateescape") for x in out.split(b"\0") if x]


# -- the argument checks (17), first of all ------------------------------------------------------------------------
def parse_args(argv):
    p = Parser(prog="indep_launch.py", allow_abbrev=False, add_help=True,
               formatter_class=argparse.RawDescriptionHelpFormatter,
               description=__doc__.split("\n\n")[0],
               epilog="The documented lines (the CTO's, from the repository):\n\n"
                      + "\n".join(x.strip() for x in __doc__.splitlines() if x.strip().startswith("python3 "))
                      + "\n\n--dry belongs on planted sets roots only: it leaves its wall and tree in place for "
                        "inspection.\nNo option takes a path list; the content is chosen by rule from the seed.")
    p.add_argument("--sets-root", help="the sets root (its real path); no folder under it is ever named")
    p.add_argument("--kind", help="writer, checker, auditor or labeller")
    p.add_argument("--brief", help="the approved brief's repository path at --commit")
    p.add_argument("--brief-sha256", help="the approved brief's sha256 (its APPROVED line's)")
    p.add_argument("--commit", help="the commit the tree is built at (an ancestor of the main line)")
    p.add_argument("--set", help="the set's name")
    p.add_argument("--round", help="1 (default) or 2")
    p.add_argument("--audit", help="the auditor only: the audit's folder name under the sets root's runs/")
    p.add_argument("--seed", help="new (default: 63 random bits); an integer only with --dry")
    p.add_argument("--dry", action="store_true", help="build the wall and stop (planted sets roots only)")
    p.add_argument("--counts-only", action="store_true", help="print a run's counts.json; build nothing")
    p.add_argument("--run", help="with --counts-only: the run id")
    return p.parse_args(argv)


def check_args(o, st, cwd, home):
    if o.kind not in KINDS:
        raise Refuse(17, "kind")
    st.set_kind(o.kind)
    if not o.sets_root:
        raise Refuse(17, "sets_root")
    given = os.path.expanduser(o.sets_root)
    if WALLS in given.split("/"):
        raise Refuse(17, "sets_root")
    root_abs = os.path.normpath(os.path.join(cwd, given))
    root = os.path.realpath(root_abs)
    if WALLS in root.split("/") or root in ("/", os.path.realpath(home)) or not os.path.isdir(root):
        raise Refuse(17, "sets_root")
    approved = os.path.join(root, WALLS, "APPROVED")
    if regular(approved):  # every result line carries it, an argument refusal's too (reading is no check)
        st.counts["approved_sha256"] = sha_file(approved)
    if o.counts_only:
        if any(v is not None for v in (o.brief, o.brief_sha256, o.commit, o.set, o.round, o.audit, o.seed)) or o.dry:
            raise Refuse(17, "counts_only")
        if not full(RUN_RX, o.run):
            raise Refuse(17, "run")
    else:
        if o.run is not None or not all((o.brief, o.brief_sha256, o.commit, o.set)):
            raise Refuse(17, "missing")
        if not full(NAME_RX, o.set):
            raise Refuse(17, "set")
        st.counts["set"] = o.set
        if o.round not in (None, "1", "2"):
            raise Refuse(17, "round")
        st.counts["round"] = int(o.round or 1)
        if (o.kind == "auditor") != (o.audit is not None) or (o.audit is not None and not full(NAME_RX, o.audit)):
            raise Refuse(17, "audit")
        seed = o.seed if o.seed is not None else "new"
        if seed != "new":
            if not re.fullmatch(r"[0-9]{1,19}", seed) or int(seed) >= 2 ** 63:
                raise Refuse(17, "seed")
            if not o.dry:
                raise Refuse(17, "seed")
    for v in (o.kind, o.brief, o.brief_sha256, o.commit, o.set, o.round, o.audit, o.seed, o.run):
        if v is None:
            continue
        p = os.path.normpath(os.path.join(cwd, os.path.expanduser(v)))
        if any(at_or_under(x, t) for x in (p, os.path.realpath(p)) for t in (root, root_abs)):
            raise Refuse(17, "under_root")
    over = {}
    for var, default in (("GOV_INDEP_RUNS_DIR", os.path.join(home, "gov-os-runs")),
                         ("GOV_INDEP_TREES_DIR", os.path.join(home, "gov-os-wall-trees"))):
        val = os.environ.get(var)
        if val is not None:
            if not os.path.isabs(val):
                raise Refuse(17, "override")
            over[var] = True
        else:
            val = default
        real = os.path.realpath(val)
        if any(at_or_under(x, t) for x in (os.path.normpath(val), real) for t in (root, root_abs)):
            raise Refuse(17, "override")
        over[var + "_path"] = real
    st.counts["override"] = bool(over.get("GOV_INDEP_RUNS_DIR") or over.get("GOV_INDEP_TREES_DIR"))
    return root, over


# -- the build's pre-checks (nothing written) ----------------------------------------------------------------------
def parse_approved(data):
    template, briefs = {}, []
    for line in data.decode("utf-8", "replace").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.fullmatch(r"([0-9a-f]{64})\s+(template|brief)\s+(.+?)\s*", line)
        if not m:
            continue
        if m.group(2) == "template":
            template.setdefault(m.group(3), set()).add(m.group(1))
        else:
            parts = m.group(3).split(None, 1)
            if len(parts) == 2:
                briefs.append((m.group(1), parts[0], parts[1]))
    return template, briefs


def norm_repo_path(p):
    if not isinstance(p, str) or not p or p.startswith("/") or "\x00" in p:
        return None
    n = posixpath.normpath(p)
    if n == "." or n.startswith("../") or n == "..":
        return None
    return n


def front_matter(data):
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return None
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    try:
        fm = yaml.safe_load(text[4:end + 1])
    except yaml.YAMLError:
        return None
    return fm if isinstance(fm, dict) else None


def load_kinds(data):
    try:
        k = yaml.safe_load(data.decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError):
        return None
    kinds = k.get("kinds") if isinstance(k, dict) else None
    if not isinstance(kinds, dict):
        return None
    for name, spec in kinds.items():
        if not isinstance(spec, dict):
            return None
        tools = spec.get("tools")
        if not isinstance(tools, list) or not tools or not all(t in TOOLS_OK for t in tools):
            return None
        if not (is_number(spec.get("budget_usd")) and spec["budget_usd"] > 0
                and is_number(spec.get("timeout_s")) and spec["timeout_s"] > 0):
            return None
        if "model" in spec and not full(MODEL_RX, spec["model"]):
            return None
    return kinds


def load_briefs(data):
    """The template's `briefs:` map (brief id -> entry), {} when absent; None when it is not a map of maps. Each
    entry's values are checked at stage 10, when a brief names it."""
    try:
        k = yaml.safe_load(data.decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError):
        return None
    briefs = k.get("briefs", {}) if isinstance(k, dict) else None
    if briefs is None:
        return {}
    if not isinstance(briefs, dict) or not all(isinstance(v, dict) for v in briefs.values()):
        return None
    return briefs


def resolve_brief(fm, kind, spec, briefs):
    """S22, stage 10: (model, result schema name, sample, brief id, entry or None). Each value from the front matter,
    else from the `briefs:` entry its `brief:` id names (whose kind must be the brief's), else (the model only) from
    the kind's; a value found nowhere, a bad entry, or a labeller brief without an entry: 10."""
    bid, entry = fm.get("brief"), None
    if bid is not None:
        if not isinstance(bid, str) or bid not in briefs:
            raise Refuse(10, "entry")
        entry = briefs[bid]
        flow = entry.get("flow")
        if entry.get("kind") != kind or flow not in FLOWS or FLOWS[flow][0] != kind:
            raise Refuse(10, "entry")
        tex = entry.get("tree_exclude", [])
        if not isinstance(tex, list) or not all(isinstance(g, str) and g for g in tex):
            raise Refuse(10, "entry")
    elif kind == "labeller":
        raise Refuse(10, "entry")  # the labeller kind runs set-up A's flows only

    def pick(key, kind_too=False):
        for src in (fm, entry or {}, spec if kind_too else {}):
            if key in src:
                return src[key]
        return None

    model, schema_name, sample_n = pick("model", True), pick("result_schema"), pick("sample")
    if not is_count(sample_n) or not full(MODEL_RX, model) or not full(SCHEMA_NAME_RX, schema_name):
        raise Refuse(10, "front_matter")
    return model, schema_name, sample_n, bid, entry


def excludes_of(data):
    return [x.strip() for x in data.decode("utf-8", "replace").splitlines()
            if x.strip() and not x.lstrip().startswith("#")]


def excluded_by(globs):
    def excluded(rel, is_dir=False):
        parts = rel.split("/")
        for i in range(1, len(parts) + 1):
            p = "/".join(parts[:i])
            forms = (p, p + "/") if (i < len(parts) or is_dir) else (p,)
            if any(fnmatch.fnmatchcase(f, g) for f in forms for g in globs):
                return True
        return False
    return excluded


def hidden_globs(data):
    try:
        m = yaml.safe_load(data.decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError):
        return None
    block = m.get("sets_root_hidden") if isinstance(m, dict) else None
    globs = block.get("hidden") if isinstance(block, dict) else None
    if not isinstance(globs, list) or not all(isinstance(g, str) and g for g in globs):
        return None
    return globs


def hidden_count(root, globs):
    """The files under the sets root whose root-relative path matches a hidden glob (fnmatch), bounded."""
    found = set()
    for g in globs:
        parts = g.split("/")
        n = next((i for i, p in enumerate(parts) if any(c in p for c in "*?[{")), len(parts))
        start = os.path.join(root, *parts[:n]) if n else root
        if not os.path.lexists(start):
            continue
        if not os.path.isdir(start) or os.path.islink(start):
            rel = os.path.relpath(start, root)
            if fnmatch.fnmatchcase(rel, g):
                found.add(rel)
            continue
        for folder, dirs, names in os.walk(start):
            dirs[:] = [d for d in dirs if d != ".git"]
            for nm in names + [d for d in dirs if os.path.islink(os.path.join(folder, d))]:
                rel = os.path.relpath(os.path.join(folder, nm), root)
                if fnmatch.fnmatchcase(rel, g):
                    found.add(rel)
            if len(found) > MOST_HIDDEN:
                return len(found)
    return len(found)


def real_inside(path, root):
    """The path, built from the real root, holds no link on the way and stays under the root."""
    return os.path.realpath(path) == os.path.normpath(path) and at_or_under(path, root)


def plan_inputs(kind, rnd, root, set_name, audit):
    """The staged copies: (source, wall-relative destination) pairs, each source a plain file under the root;
    a missing input refuses with 10 before anything is written."""
    ev = os.path.join(root, "fixtures", "evaluation")
    setdir = os.path.join(ev, set_name)
    hidden = os.path.join(setdir, "hidden")
    plan = []

    def need_file(p):
        if not real_inside(p, root) or not os.path.isfile(p) or os.path.islink(p):
            raise Refuse(10, "input")
        return p

    def set_copies():
        if not real_inside(hidden, root) or not os.path.isdir(hidden) or os.path.islink(hidden):
            raise Refuse(10, "input")
        try:
            rels = plain_files(hidden)
        except (ValueError, OSError):
            raise Refuse(10, "input")
        if kind == "auditor":  # W2-178: the auditor's copy leaves out hidden/dropped/ (a plain file "dropped" stays)
            rels = [r for r in rels if not r.startswith("dropped" + os.sep)]
        if not rels:
            raise Refuse(10, "input")
        return [(os.path.join(hidden, r), os.path.join("input", "set", r)) for r in rels]

    if kind == "writer":
        if rnd == 2:  # round 1 makes a new set: its folder may not exist yet; its destination is checked at delivery
            plan += set_copies()
            plan.append((need_file(os.path.join(setdir, "XCHECK-r1.md")), "input/notes.md"))
    elif kind == "checker":
        plan += set_copies()
    elif kind == "auditor":
        plan += set_copies()
        plan.append((need_file(os.path.join(root, "runs", audit, "misses.jsonl")), "input/misses.jsonl"))
    else:
        raise Refuse(10, "entry")  # the labeller kind runs set-up A's flows only
    return plan


# -- set-up A's inputs (S20, S24, S27): read and checked before anything is written ---------------------------------
def half_folder(half, root, runs):
    """H: the tuning half's folder under the experiment's, or the held-out half's sealed folder (and its top)."""
    if half == "tuning":
        return os.path.join(runs, EXP, "tuning"), runs
    return os.path.join(root, *SEAL.split("/")), root


def read_plain(path, top):
    """A plain file's bytes (no link on the way, under *top*); None when missing or not plain."""
    if not real_inside(path, top) or not regular(path):
        return None
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as f:
        return f.read()


def jsonl_objects(data):
    """[(raw line with its newline, object)] for each non-blank line; a line that is not an object with a string id,
    or a repeated id, raises ValueError."""
    out, seen = [], set()
    for raw in data.split(b"\n"):
        if not raw.strip():
            continue
        obj = load_json_strict(raw.decode("utf-8"))
        if not isinstance(obj, dict) or not isinstance(obj.get("id"), str) or obj["id"] in seen:
            raise ValueError("line")
        seen.add(obj["id"])
        out.append((raw + b"\n", obj))
    return out


def project(raw, obj, keep):
    """A staged line kept to the brief's fields: the line's own bytes when it holds no other field."""
    if all(k in keep for k in obj):
        return raw
    return (json.dumps({k: v for k, v in obj.items() if k in keep}) + "\n").encode("utf-8")


def staged_half(h, top):
    """The half's staged lines (the actions', then the cases'): [(id, staged bytes, projected object)]; 10 when
    either file is missing or malformed, or an id repeats."""
    lines, seen = [], set()
    for rel, keep in (("corpus/actions.jsonl", ACTION_FIELDS), ("planted/cases.jsonl", ACTION_FIELDS + ("rule_class",))):
        data = read_plain(os.path.join(h, *rel.split("/")), top)
        if data is None:
            raise Refuse(10, "input")
        try:
            for raw, obj in jsonl_objects(data):
                if obj["id"] in seen:
                    raise ValueError("repeat")
                seen.add(obj["id"])
                b = project(raw, obj, keep)
                lines.append((obj["id"], b, {k: v for k, v in obj.items() if k in keep}, rel))
        except (ValueError, UnicodeDecodeError):
            raise Refuse(10, "input")
    return lines


RULE_CLASS_RX = re.compile(r"(?:[1-9]|1[0-4])")


def rule_class(v):
    """(F23, S31) A session's rule class as an integer: a JSON integer 1-14 (never a boolean) or a decimal string
    "1"-"14" (no sign, no leading zero, no space); None for anything else."""
    if isinstance(v, int) and not isinstance(v, bool):
        return v if 1 <= v <= 14 else None
    if isinstance(v, str) and RULE_CLASS_RX.fullmatch(v):
        return int(v)
    return None


def by_rule(seed, word, ident, mod):
    return int(hashlib.sha256((str(seed) + word + ident).encode("utf-8")).hexdigest(), 16) % mod == 0


def round1_files(flow, bid, half, h, top, runs_indep, brief_sha):
    """Round 2's copy of round 1: H/labels/r1-<brief id>/'s files, each sha256 equal to the latest delivered round-1
    run's (same brief sha256 and half) counts.json; 10 otherwise."""
    best = None
    folder = os.path.join(runs_indep, "labeller")
    for run in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        try:
            with open(os.path.join(folder, run, "counts.json"), encoding="utf-8") as f:
                c = load_json_strict(f.read())
        except (OSError, ValueError, UnicodeDecodeError):
            continue
        if (isinstance(c, dict) and c.get("status") == "delivered" and c.get("round") == 1 and c.get("set") == half
                and c.get("brief_sha256") == brief_sha and isinstance(c.get("delivered"), dict)
                and c["delivered"].get("to") == "round1"):
            best = c
    shas = best["delivered"].get("files_sha256") if best else None
    if not isinstance(shas, dict) or set(shas) != set(ROUND1_FILES[flow]):
        raise Refuse(10, "round1")
    files = {}
    for name in ROUND1_FILES[flow]:
        data = read_plain(os.path.join(h, "labels", f"r1-{bid}", name), top)
        if data is None or sha_bytes(data) != shas[name]:
            raise Refuse(10, "round1")
        files[name] = data
    if delivered_sha([(n, sha_bytes(b)) for n, b in files.items()]) != best["delivered"].get("sha256"):
        raise Refuse(10, "round1")
    return files


def label_lines(data):
    """{id: object} of a labels file; ValueError when malformed."""
    out = {}
    for _raw, obj in jsonl_objects(data):
        if obj.get("label") not in LABELS:
            raise ValueError("label")
        out[obj["id"]] = obj
    return out


def decided_ids(audit_dir, top):
    """The ids the earlier audit runs' decisions files name."""
    ids = set()
    if not os.path.lexists(audit_dir):
        return ids
    if not real_inside(audit_dir, top) or not os.path.isdir(audit_dir):
        raise ValueError("audit")
    for n in sorted(os.listdir(audit_dir)):
        if n.endswith(".decisions.jsonl"):
            data = read_plain(os.path.join(audit_dir, n), top)
            if data is None:
                raise ValueError("audit")
            ids.update(o["id"] for _r, o in jsonl_objects(data))
    return ids


def ticket_lines(repo, commit, names):
    """For each ticket file in .tickets/ at the commit whose id or wbs_id is among *names*: {id, role, wbs_id,
    allowed_paths}, nothing else; read in one git cat-file call."""
    lt = git(repo, "ls-tree", "-z", "--name-only", commit, "--", ".tickets/")
    if lt.returncode != 0:
        raise Refuse(14, "tickets")
    paths = [p for p in z_list(lt.stdout) if p.endswith(".md") and "\n" not in p]
    if not paths or not names:
        return []
    cat = git(repo, "cat-file", "--batch", stdin="".join(f"{commit}:{p}\n" for p in paths).encode("utf-8"))
    if cat.returncode != 0:
        raise Refuse(14, "tickets")
    out, data, pos = [], cat.stdout, 0
    for _p in paths:
        nl = data.index(b"\n", pos)
        head = data[pos:nl].split()
        pos = nl + 1
        if len(head) != 3 or head[1] != b"blob":
            continue
        size = int(head[2])
        fm = front_matter(data[pos:pos + size])
        pos += size + 1
        if fm and any(isinstance(fm.get(k), str) and fm[k] in names for k in ("id", "wbs_id")):
            out.append({"id": fm.get("id"), "role": fm.get("role"), "wbs_id": fm.get("wbs_id"),
                        "allowed_paths": fm.get("allowed_paths")})
    return out


def plan_sgx(flow, rnd, half, root, runs, runs_indep, bid, brief_sha, repo, commit):
    """Everything set-up A's flow reads, checked now (a missing input refuses 10 before anything is written):
    a dict the build (B4) and the delivery use."""
    h, top = half_folder(half, root, runs)
    p = {"flow": flow, "half": half, "h": h, "top": top, "staged": None, "round1": None, "labels1": None,
         "labels2": None, "disputes": None, "tickets": None, "seal": None}
    if flow == "sgx1-writer-2":
        p["seal"] = sealed(repo, commit)
    if flow == "sgx1-labeller-1" or (flow == "sgx1-labeller-2" and rnd == 2) or flow == "sgx1-overlap-auditor":
        p["staged"] = staged_half(h, top)
    if rnd == 2:
        p["round1"] = round1_files(flow, bid, half, h, top, runs_indep, brief_sha)
    if flow == "sgx1-overlap-auditor":
        try:
            l1 = read_plain(os.path.join(h, "labels", "labels.jsonl"), top)
            l2 = read_plain(os.path.join(h, "labels", "labels-2.jsonl"), top)
            if l1 is None or l2 is None:
                raise Refuse(10, "input")
            p["labels1_bytes"] = l1
            p["labels1"], p["labels2"] = label_lines(l1), label_lines(l2)
            done = decided_ids(os.path.join(h, "labels", "audit"), top)
        except (ValueError, UnicodeDecodeError):
            raise Refuse(10, "input")
        actions = {i: obj for i, _b, obj, _rel in p["staged"]}
        ids = sorted(i for i in p["labels1"] if i in p["labels2"] and i not in done
                     and p["labels1"][i]["label"] != p["labels2"][i]["label"])[:AUDIT_SPLIT]
        if not ids or any(i not in actions for i in ids):
            raise Refuse(10, "input")
        p["disputes"] = [(i, {k: actions[i][k] for k in DISPUTE_ACTION if k in actions[i]}) for i in ids]
        names = set()
        for _i, act in p["disputes"]:
            names.update(v for v in (act.get("ticket"), act.get("wbs")) if isinstance(v, str))
        p["tickets"] = ticket_lines(repo, commit, names)
    return p


def stage_sgx(sgx, rnd, seed, commit):
    """B4 for set-up A, after the seed: {wall-relative path: bytes} of the flow's input/ (the writers' selection.json
    is added by the caller). Draws by the seed: labeller 1's sample, labeller 2's overlap, the auditor's x/y order."""
    flow, files = sgx["flow"], {}
    half = {"half": sgx["half"], "pin": commit}
    if flow == "sgx1-writer-2":
        files["input/seal.json"] = (json.dumps({"sealed": bool(sgx["seal"])}) + "\n").encode()
        return files
    if flow == "sgx1-writer-1":
        return files
    if flow == "sgx1-overlap-auditor":
        rng = random.Random(seed)
        xmap, lines = {}, []
        for i, action in sgx["disputes"]:
            first = rng.random() < 0.5  # x is labeller 1
            xmap[i] = {"x": 1, "y": 2} if first else {"x": 2, "y": 1}
            a, b = part(sgx["labels1"][i]), part(sgx["labels2"][i])
            a["reason"] = b["reason"] = ""  # (F36) every side's reason blanked: no labeller's text enters the wall
            x, y = (a, b) if first else (b, a)
            lines.append(json.dumps({"id": i, "action": action, "x": x, "y": y}) + "\n")
        sgx["xmap"] = xmap  # written at delivery only, never into the wall
        half["cases"] = len(sgx["disputes"])
        files["input/disputes.jsonl"] = "".join(lines).encode("utf-8")
        files["input/tickets.jsonl"] = "".join(json.dumps(t) + "\n" for t in sgx["tickets"]).encode("utf-8")
    files["input/half.json"] = (json.dumps(half) + "\n").encode()
    staged = sgx["staged"] or []
    if flow == "sgx1-labeller-1":
        files["input/actions.jsonl"] = b"".join(b for _i, b, _o, rel in staged if rel.startswith("corpus/"))
        files["input/cases.jsonl"] = b"".join(b for _i, b, _o, rel in staged if rel.startswith("planted/"))
    if rnd == 2:
        for name, data in sgx["round1"].items():
            files[f"input/round1/{name}"] = data
        if flow == "sgx1-labeller-1":
            files["input/script-labels.jsonl"] = b"".join(sgx["script_raw"])
            sgx["sample_ids"] = [i for i, _b, _o, _r in staged if by_rule(seed, "labeller-sample", i, 20)]
            files["input/sample.json"] = (json.dumps({"ids": sgx["sample_ids"]}) + "\n").encode("utf-8")
        else:
            picked = [(i, b) for i, b, _o, _r in staged if by_rule(seed, "overlap", i, 10)]
            sgx["n_overlap"] = len(picked)
            sgx["overlap_ids"] = [i for i, _b in picked]  # the ids labels-2.jsonl must hold (F20)
            files["input/sample.jsonl"] = b"".join(b for _i, b in picked)
    return files


SGX_INPUTS = {("sgx1-writer-1", 1): 1, ("sgx1-writer-2", 1): 2, ("sgx1-labeller-1", 1): 3,
              ("sgx1-labeller-1", 2): 7, ("sgx1-labeller-2", 1): 1, ("sgx1-labeller-2", 2): 3,
              ("sgx1-overlap-auditor", 1): 3}
SGX_LANDS = {("sgx1-writer-1", 1): 1, ("sgx1-writer-2", 1): 1, ("sgx1-labeller-1", 1): 2, ("sgx1-labeller-1", 2): 1,
             ("sgx1-labeller-2", 1): 1, ("sgx1-labeller-2", 2): 1, ("sgx1-overlap-auditor", 1): 4}


def sgx_expected(sgx, rnd):
    """S18 for set-up A: the wall's six fixed files, its staged inputs, the run's extras, and what lands in the
    sealed folder when the half is the held-out one."""
    key = (sgx["flow"], rnd)
    return 6 + SGX_INPUTS[key] + RUN_EXTRA + (SGX_LANDS[key] if sgx["half"] == "held-out" else 0)


def sealed(repo, commit):
    """writer 2's seal.json: true when the path map at the commit holds the set's hidden glob and a sets root hidden
    glob covers it (the same glob, or one matching a path under that folder)."""
    want = SEAL + "/**"
    data = blob(repo, commit, PATH_MAP)
    try:
        m = yaml.safe_load(data.decode("utf-8")) if data is not None else None
    except (UnicodeDecodeError, yaml.YAMLError):
        m = None
    if not isinstance(m, dict):
        return False
    es = m.get("evaluation_sets")
    entry = es.get(SEAL_SET) if isinstance(es, dict) else None
    globs = entry.get("hidden") if isinstance(entry, dict) else None
    if not isinstance(globs, list) or want not in globs:
        return False
    hidden = hidden_globs(data) or []
    probe = SEAL + "/probe"
    return any(g == want or fnmatch.fnmatchcase(probe, g) for g in hidden)


def last_audit(runs_indep):
    path = os.path.join(runs_indep, "AUDITS.log")
    if not os.path.lexists(path):
        return None
    with open(path, encoding="utf-8") as f:
        lines = [x for x in f.read().splitlines() if x.strip()]
    if not lines:
        return None
    obj = load_json_strict(lines[-1])
    if not isinstance(obj, dict) or not full(HEX40, obj.get("commit")):
        raise ValueError("audits")
    return obj["commit"]


# -- the test hook -------------------------------------------------------------------------------------------------
def hook(st, point):
    exe = os.environ.get("GOV_INDEP_TEST_HOOK")
    if not exe:
        return
    try:
        subprocess.run([exe, point, st.wall, st.tree], stdin=subprocess.DEVNULL, timeout=600)
    except (OSError, subprocess.SubprocessError):
        pass


# -- the session and the canary ------------------------------------------------------------------------------------
def clean_env(home):
    env = {k: os.environ[k] for k in SESSION_ENV if k in os.environ}
    env.setdefault("HOME", home)
    return env


def session_flags(wall, tree, tools, model, budget, session_id, extra_dir=None, effort=None):
    # --setting-sources project (F11, DEC-1112 (3)): only the wall's own settings load, never the user's or local ones
    flags = ["-p", "--restricted", "--setting-sources", "project",
             "--settings", os.path.join(wall, ".claude", "settings.json"), "--add-dir", tree]
    if extra_dir:
        flags += ["--add-dir", extra_dir]
    flags += ["--tools", ",".join(tools), "--no-session-persistence", "--strict-mcp-config",
              "--disable-slash-commands", "--permission-prompts", "none", "--model", model]
    if effort:  # the brief's effort (W2-173 S1, DEC-1120 (2)); none named: no flag
        flags += ["--effort", effort]
    return flags + ["--max-budget-usd", num_text(budget), "--output-format", "json",
                    "--session-id", session_id]  # drawn by the script: the trace check always has its key (F1)


def draw_session_id(st):
    """A session id drawn by the script (F1, F6), kept only as a trace check key: never printed or logged."""
    sid = str(uuid.uuid4())
    st.trace_ids.add(sid)
    return sid


def reported_id(res):
    sid = res.get("session_id") if isinstance(res, dict) else None
    return sid if full(SESSION_ID_RX, sid) else None


def check_traces(st):
    """S12: the entries under ~/.claude's trace folders named by any of the run's ids (drawn or reported), each
    entry once; the count goes to `traces` and the log says the check ran."""
    n = count_traces(st.home, st.trace_ids)
    st.counts["traces"] = n
    st.log("traces", "checked", n)
    return n


def stop_group(pgid):
    """Stop a process group by its id (never by a name) and wait until it is gone."""
    if not pgid:
        return True
    try:
        os.killpg(pgid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass
    end = time.monotonic() + 10
    while time.monotonic() < end:
        try:
            os.killpg(pgid, 0)
        except ProcessLookupError:
            return True
        except PermissionError:
            return False
        time.sleep(0.05)
    return False


# -- the confined rule script (S25; code 18) -----------------------------------------------------------------------
def rules_programs(home):
    """(bwrap, the interpreter's real path): GOV_INDEP_BWRAP / GOV_INDEP_RULES_PYTHON (absolute; tests and the trial
    only), else bwrap on PATH and the interpreter on the first line of ~/.local/bin/gov. Anything missing: 18."""
    bwrap = os.environ.get("GOV_INDEP_BWRAP")
    if bwrap is None:
        bwrap = shutil.which("bwrap")
    py = os.environ.get("GOV_INDEP_RULES_PYTHON")
    if py is None:
        try:
            with open(os.path.join(home, ".local", "bin", "gov"), "rb") as f:
                first = f.readline(4096).decode("utf-8")
        except (OSError, UnicodeDecodeError):
            raise Refuse(18, "python")
        words = first[2:].split() if first.startswith("#!") else []
        py = words[0] if len(words) == 1 else None
    for p in (bwrap, py):
        if not p or not os.path.isabs(p) or not os.path.isfile(p) or not os.access(p, os.X_OK):
            raise Refuse(18, "program")
    return bwrap, os.path.realpath(py)


def rules_binds(py_real, protected):
    """The read-only binds the interpreter needs: /usr (the interpreter, its standard library and the libraries it
    loads), the host's /lib, /lib32, /lib64 as their links (or binds) and the loader's cache; the interpreter's own
    prefix when it lies outside /usr. A bind at, under or above a protected folder (HOME, the sets root, the runs and
    trees folders, the repository): 18."""
    args, sources = [], ["/usr"]
    args += ["--ro-bind", "/usr", "/usr"]
    for top in ("/lib", "/lib32", "/lib64"):
        if os.path.islink(top):
            args += ["--symlink", os.readlink(top), top]
        elif os.path.isdir(top):
            args += ["--ro-bind", top, top]
            sources.append(top)
    args += ["--ro-bind-try", "/etc/ld.so.cache", "/etc/ld.so.cache"]
    if not at_or_under(py_real, "/usr"):
        prefix = os.path.dirname(os.path.dirname(py_real))
        args += ["--ro-bind", prefix, prefix]
        sources.append(prefix)
    for s in sources:
        if s == "/" or any(at_or_under(s, p) or at_or_under(p, s) for p in protected if p):
            raise Refuse(18, "bind")
    return args


def rules_argv(bwrap, py_real, script, protected):
    """bwrap: every namespace unshared (no network), no capability, a new session, killed with its parent; nothing
    bound but the interpreter's files and the script, read-only; the root read-only."""
    return ([bwrap, "--unshare-user", "--unshare-ipc", "--unshare-pid", "--unshare-net", "--unshare-uts",
             "--unshare-cgroup-try", "--die-with-parent", "--new-session", "--cap-drop", "ALL"]
            + rules_binds(py_real, protected)
            + ["--dev", "/dev", "--proc", "/proc", "--ro-bind", script, script, "--remount-ro", "/", "--chdir", "/",
               py_real, "-I", "-X", "utf8", "-c", RULES_PRELUDE, script])


def pump(proc, data, cap, deadline):
    """Feed stdin and read stdout until both end: the output, or None past the deadline or the cap."""
    sel = selectors.DefaultSelector()
    out, pos, view = bytearray(), 0, memoryview(data)
    os.set_blocking(proc.stdin.fileno(), False)
    sel.register(proc.stdin, selectors.EVENT_WRITE)
    sel.register(proc.stdout, selectors.EVENT_READ)
    try:
        while sel.get_map():
            left = deadline - time.monotonic()
            if left <= 0:
                return None
            for key, _ev in sel.select(left):
                if key.fileobj is proc.stdin:
                    try:
                        pos += os.write(proc.stdin.fileno(), view[pos:pos + 65536])
                    except BlockingIOError:
                        continue
                    except OSError:
                        pos = len(data)
                    if pos >= len(data):
                        sel.unregister(proc.stdin)
                        proc.stdin.close()
                else:
                    chunk = os.read(proc.stdout.fileno(), 65536)
                    if not chunk:
                        sel.unregister(proc.stdout)
                    else:
                        out += chunk
                        if len(out) > cap:
                            return None
    finally:
        sel.close()
    return bytes(out)


def check_rule_output(out, ids):
    """Every staged id exactly once: (the raw lines in order, {id: line}); anything else raises ValueError."""
    want, raws, got = set(ids), [], {}
    for raw in out.split(b"\n"):
        if not raw.strip():
            continue
        obj = load_json_strict(raw.decode("utf-8"))
        if not isinstance(obj, dict):
            raise ValueError("line")
        i = obj.get("id")
        if not isinstance(i, str) or i not in want or i in got:
            raise ValueError("id")
        rc = rule_class(obj.get("rule_class"))
        if (obj.get("label") not in LABELS or rc is None
                or not isinstance(obj.get("clauses"), list) or not all(isinstance(c, str) for c in obj["clauses"])
                or not isinstance(obj.get("uncertain"), bool)):
            raise ValueError("value")
        if isinstance(obj["rule_class"], str):  # (F23) stored as an integer
            obj = dict(obj, rule_class=rc)
            raw = json.dumps(obj).encode("utf-8")
        got[i] = obj
        raws.append(raw + b"\n")
    if set(got) != want:
        raise ValueError("missing")
    return raws, got


def staged_rules(sgx, script_bytes, home):
    """The rule script over the half's staged lines (S25): at round 1's delivery and at round 2."""
    staged = sgx["staged"]
    return run_rules(script_bytes, b"".join(b for _i, b, _o, _r in staged), [i for i, _b, _o, _r in staged], home,
                     sgx["protected"])


def run_rules(script_bytes, stdin_bytes, ids, home, protected):
    """S25: round 1's label_rules.py under bwrap on the pinned interpreter, stdin the half's staged lines; its group
    stopped by pgid on every exit. Returns (the output's lines, {id: label}); any failure, cap or bad output: 18."""
    bwrap, py_real = rules_programs(home)
    tmp = os.path.realpath(tempfile.mkdtemp(prefix="indep-rules-"))
    proc = None
    try:
        if any(at_or_under(tmp, p) or at_or_under(p, tmp) for p in protected if p):
            raise Refuse(18, "place")
        script = os.path.join(tmp, "label_rules.py")
        write_new(script, script_bytes, 0o444)
        argv = rules_argv(bwrap, py_real, script, protected)
        try:
            proc = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                    env={}, cwd="/", start_new_session=True, close_fds=True)
        except OSError:
            raise Refuse(18, "start")
        deadline = time.monotonic() + RULES_WALL_S
        out = pump(proc, stdin_bytes, RULES_OUT_BASE + RULES_OUT_PER_ID * len(ids), deadline)
        if out is None:
            raise Refuse(18, "cap")
        try:
            rc = proc.wait(timeout=max(0.1, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            raise Refuse(18, "cap")
        if rc != 0:
            raise Refuse(18, "exit")
        try:
            return check_rule_output(out, ids)
        except (ValueError, UnicodeDecodeError):
            raise Refuse(18, "output")
    finally:
        if proc is not None:  # by its group id, never a name: the group killed, the leader reaped, the group gone
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
            for f in (proc.stdin, proc.stdout):
                try:
                    f.close()
                except (OSError, ValueError):
                    pass
            proc.wait()
            stop_group(proc.pid)
        shutil.rmtree(tmp, ignore_errors=True)


def parse_output(data):
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return None
    for cand in (text, *(x for x in reversed(text.splitlines()) if x.strip())):
        try:
            obj = load_json_strict(cand)
        except ValueError:
            continue
        if isinstance(obj, list):
            obj = next((x for x in reversed(obj) if isinstance(x, dict) and x.get("type") == "result"), None)
        if isinstance(obj, dict):
            return obj
    return None


def run_canary(st, ctx):
    roots = [ctx["root"], ctx["trees"], ctx["runs"], ctx["repo"], st.wall, st.tree]
    cdir = os.path.realpath(tempfile.mkdtemp(prefix="indep-canary-"))
    started = False
    try:
        if any(at_or_under(cdir, r) or at_or_under(r, cdir) for r in roots):
            raise Refuse(16, "place")
        target = os.path.join(cdir, f"canary-{secrets.token_hex(8)}.txt")
        write_new(target, (secrets.token_hex(16) + "\n").encode(), 0o444)
        prompt = f"Read the file {target} and reply with its first line only."
        limit = min(CANARY_LIMIT, ctx["timeout"])
        cid = draw_session_id(st)
        argv = (["timeout", f"--kill-after={CANARY_KILL_AFTER}", num_text(limit), "claude"]
                + session_flags(st.wall, st.tree, ctx["tools"], ctx["model"], ctx["budget"], cid, cdir,
                                ctx["effort"]) + [prompt])
        st.log("canary", "start")
        started = True
        proc = subprocess.Popen(argv, cwd=st.wall, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL, env=clean_env(ctx["home"]), start_new_session=True)
        try:
            out, _ = proc.communicate(timeout=limit + CANARY_KILL_AFTER + 30)
        except subprocess.TimeoutExpired:
            stop_group(proc.pid)
            proc.wait()
            raise Refuse(16, "timeout")
        finally:
            stop_group(proc.pid)
        st.log("canary", "exit", proc.returncode)
        parsed = parse_output(out[:MOST_SESSION_BYTES])
        rid = reported_id(parsed)  # the canary's own traces, under the id it reports too (F6)
        if rid:
            st.trace_ids.add(rid)
        res = parsed if proc.returncode == 0 else None
        if res is None or res.get("is_error") is True:
            raise Refuse(16, "output")
        dens = res.get("permission_denials")
        targets = (target, os.path.realpath(target))
        hit = isinstance(dens, list) and any(
            isinstance(d, dict) and d.get("tool_name") == "Read" and isinstance(d.get("tool_input"), dict)
            and d["tool_input"].get("file_path") in targets for d in dens)
        if not hit:
            raise Refuse(16, "not_refused")
        st.log("canary", "refused", "ok")
    finally:
        shutil.rmtree(cdir, ignore_errors=True)
        if started:  # the canary's traces are counted whether it passed or not; its own 16 still wins (F6)
            check_traces(st)


def run_session(st, ctx):
    sid = draw_session_id(st)
    argv = (["timeout", f"--kill-after={KILL_AFTER}", num_text(ctx["timeout"]), "claude"]
            + session_flags(st.wall, st.tree, ctx["tools"], ctx["model"], ctx["budget"], sid,
                            effort=ctx["effort"]) + [PROMPT])
    st.session_file = st.wall + ".session.json"
    fd = os.open(st.session_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as out:
        st.log("session", "start")
        proc = subprocess.Popen(argv, cwd=st.wall, stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.DEVNULL,
                                env=clean_env(ctx["home"]), start_new_session=True)
    st.pgid = os.getpgid(proc.pid)
    for name, val in (("session.pid", proc.pid), ("session.pgid", st.pgid)):
        with open(os.path.join(st.counts_dir, name), "w", encoding="utf-8") as f:
            f.write(f"{val}\n")
    backstop = False
    try:
        try:
            rc = proc.wait(timeout=ctx["timeout"] + KILL_AFTER + 60)
        except subprocess.TimeoutExpired:
            backstop = True
            stop_group(st.pgid)
            rc = proc.wait()
    finally:
        gone = stop_group(st.pgid)
        if proc.poll() is None:
            proc.wait()
        st.pgid = None
    st.log("session", "exit", rc, "group_gone", gone)
    return rc, backstop


def read_session(st, rc):
    s = st.counts["session"]
    s["exit"] = rc
    try:
        with open(st.session_file, "rb") as f:
            res = parse_output(f.read(MOST_SESSION_BYTES))
    except OSError:
        res = None
    s["refusals"] = {k: 0 for k in REFUSAL_KEYS}
    if not res:
        return None, None
    if isinstance(res.get("is_error"), bool):
        s["is_error"] = res["is_error"]
    if is_count(res.get("num_turns")):
        s["turns"] = res["num_turns"]
    if is_number(res.get("total_cost_usd")) and res["total_cost_usd"] >= 0:
        s["cost_usd"] = res["total_cost_usd"]
    if is_number(res.get("duration_ms")) and res["duration_ms"] >= 0:
        s["duration_s"] = round(res["duration_ms"] / 1000.0, 3)
    for d in res.get("permission_denials") or []:
        if isinstance(d, dict):
            t = d.get("tool_name")
            s["refusals"][t if t in REFUSAL_KEYS and t != "other" else "other"] += 1
    sub = res.get("subtype")
    return (sub if isinstance(sub, str) else None), reported_id(res)


def count_traces(home, ids):
    """Names only (nothing opened): the entries at depth 1 or 2 under ~/.claude/{projects,file-history,session-env,
    todos} whose name begins with any of *ids*, each entry counted once."""
    keys = tuple(sorted({i for i in ids if full(SESSION_ID_RX, i)}))
    if not keys or not home:
        return 0
    seen = set()
    for base in TRACE_DIRS:
        top = os.path.join(home, ".claude", base)
        if not os.path.isdir(top) or os.path.islink(top):
            continue
        with os.scandir(top) as level1:
            for e in level1:
                if e.name.startswith(keys):
                    seen.add(e.path)
                if e.is_dir(follow_symlinks=False):
                    try:
                        with os.scandir(e.path) as level2:
                            seen.update(x.path for x in level2 if x.name.startswith(keys))
                    except OSError:
                        pass
    return len(seen)


# -- the result and the delivery -----------------------------------------------------------------------------------
def out_files(out):
    n = 0
    for _folder, dirs, names in os.walk(out):
        n += len(names) + sum(1 for d in dirs if os.path.islink(os.path.join(_folder, d)))
    return n


def copy_numbers(st, kind, res):
    o = st.counts["out"]
    def counts_of(d, names):  # the fixed names the result gives, numbers only
        return {k: d[k] for k in names if k in d and is_count(d[k])}

    if kind == "writer":
        o["questions"] = res["questions"] if is_count(res["questions"]) else None
        o["by_kind"] = counts_of(res["by_kind"], BY_KIND)
        o["by_area"] = counts_of(res["by_area"], BY_AREA)
    elif kind == "auditor":
        o["misses"] = counts_of(res["misses"], MISS_CLASSES)
    else:
        for k in OUT_KEYS[kind]:
            v = res.get(k)
            o[k] = v if is_count(v) else None


def copy_sgx_numbers(st, res):
    """S28: each number of a set-up A result under its own key in `out`; an object as an object of its numbers keyed
    "1".."14"; `stopped` as its fixed word. Anything else is left out (the result's schema is closed already)."""
    o = st.counts["out"]
    for k in SGX_OUT:
        v = res.get(k)
        if is_count(v):
            o[k] = v
        elif isinstance(v, dict) and all(re.fullmatch(r"[1-9]|1[0-4]", x) and is_count(n) for x, n in v.items()):
            o[k] = {x: v[x] for x in sorted(v, key=int)}
        elif k == "stopped" and v in STOPPED:
            o[k] = v


def regular(path):
    try:
        return stat.S_ISREG(os.lstat(path).st_mode)
    except OSError:
        return False


def bundle_sha(files):
    """files: (relative path, sha256) pairs: the sha256 of '<sha256>  <path>\\n' lines sorted by path."""
    return sha_bytes("".join(f"{h}  {p}\n" for p, h in sorted(files)).encode("utf-8"))


def delivered_sha(files):
    """`delivered.sha256` of set-up A's flows: one file's own sha256, several files' bundle sha256."""
    return files[0][1] if len(files) == 1 else bundle_sha(files)


def copy_set(src, dst):
    """Copy a plain folder into a new folder; returns [(relative path, sha256)] of the copies, checked."""
    rels = plain_files(src)
    os.mkdir(dst, 0o755)
    got = []
    for r in rels:
        d = os.path.join(dst, r)
        os.makedirs(os.path.dirname(d), mode=0o755, exist_ok=True)
        want = sha_file(os.path.join(src, r))
        if copy_new(os.path.join(src, r), d, 0o644) != want:
            raise RuntimeError("copy")
        got.append((r, want))
    return got


def deliver_file(src, dst):
    if os.path.lexists(dst) and not regular(dst):
        raise Refuse(20, "destination")
    tmp = os.path.join(os.path.dirname(dst), "." + os.path.basename(dst) + f".{secrets.token_hex(4)}.tmp")
    try:
        want = sha_file(src)
        if copy_new(src, tmp, 0o644) != want:
            raise Refuse(20, "copy")
        os.rename(tmp, dst)
    except (OSError, ValueError):
        raise Refuse(20, "copy")
    finally:
        if os.path.lexists(tmp):
            os.unlink(tmp)
    return want


def staged_set_ids(wall):
    """(W2-173 S3) The ids of the set staged in the wall: its files' stems (`q01` for `q01.yaml`), sorted; a stem
    twice: 20."""
    try:
        rels = plain_files(os.path.join(wall, "input", "set"))
    except (ValueError, OSError):
        raise Refuse(20, "notes")
    ids = sorted(os.path.splitext(os.path.basename(r))[0] for r in rels)
    if len(set(ids)) != len(ids):
        raise Refuse(20, "notes")
    return ids


def staged_miss_ids(wall):
    """(W2-173 S4) The ids the lines of the wall's staged input/misses.jsonl carry; unreadable or a repeated id: 20."""
    data = read_plain(os.path.join(wall, "input", "misses.jsonl"), wall)
    if data is None:
        raise Refuse(20, "classes")
    try:
        return [o["id"] for _raw, o in jsonl_objects(data)]
    except (ValueError, UnicodeDecodeError):
        raise Refuse(20, "classes")


def check_notes(data, ids, res):
    """(W2-173 S3) The checker's notes.md in its brief's fixed form (§6): `# Cross-check notes`; `## Questions` and one
    line per staged id in id order, `<id> | accept|revise|reject | <codes or -> | also: <...> | <sentence>` (split on
    ` | ` into five fields at most, as the next step reads it); `## The set` and its five lines; nothing else but blank
    lines beside a heading and one final newline. The result's checked, accepted, revise and rejected equal the lines'
    counts. Anything else: 20."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise Refuse(20, "notes")
    if text.endswith("\n"):
        text = text[:-1]
    raw = text.split("\n")
    lines = []
    for i, line in enumerate(raw):
        if line == "":
            if not ((i > 0 and raw[i - 1].startswith("#")) or (i + 1 < len(raw) and raw[i + 1].startswith("#"))):
                raise Refuse(20, "notes")
            continue
        lines.append(line)
    n = len(ids)
    if (len(lines) != n + 8 or lines[0] != NOTES_HEAD or lines[1] != "## Questions"
            or lines[n + 2] != "## The set"):
        raise Refuse(20, "notes")
    tally = {v: 0 for v in VERDICTS}
    for want, line in zip(ids, lines[2:n + 2]):
        f = line.split(" | ", 4)
        if (len(f) != 5 or f[0] != want or f[1] not in VERDICTS or not f[2].strip() or not f[3].startswith("also:")
                or not f[4].strip()):
            raise Refuse(20, "notes")
        tally[f[1]] += 1
    if not all(line.startswith(p) for p, line in zip(NOTES_SET, lines[n + 3:])):
        raise Refuse(20, "notes")
    if (res.get("checked"), res.get("accepted"), res.get("revise"), res.get("rejected")) != (
            n, tally["accept"], tally["revise"], tally["reject"]):
        raise Refuse(20, "notes")


def check_classes(data, ids, res):
    """(W2-173 S4) The auditor's classes.json: a JSON object with one entry for each staged miss id and no other, each
    `{"class": <one of the five>, "reason": <one line of at most 200 characters>}`; the result's five `misses` counts
    (an absent one is 0) equal the classes' counts. Anything else: 20."""
    def no_repeat(pairs):
        obj = {}
        for k, v in pairs:
            if k in obj:
                raise ValueError("repeat")
            obj[k] = v
        return obj

    def no_constant(_x):
        raise ValueError("constant")
    try:
        obj = json.loads(data.decode("utf-8"), object_pairs_hook=no_repeat, parse_constant=no_constant)
    except (ValueError, UnicodeDecodeError, RecursionError):
        raise Refuse(20, "classes")
    if not isinstance(obj, dict) or set(obj) != set(ids):
        raise Refuse(20, "classes")
    tally = {c: 0 for c in MISS_CLASSES}
    for v in obj.values():
        reason = v.get("reason") if isinstance(v, dict) else None
        if (not isinstance(v, dict) or not isinstance(v.get("class"), str) or v["class"] not in MISS_CLASSES
                or not isinstance(reason, str) or "\n" in reason or "\r" in reason or len(reason) > REASON_MOST):
            raise Refuse(20, "classes")
        tally[v["class"]] += 1
    misses = res.get("misses")
    if not isinstance(misses, dict) or any(misses.get(c, 0) != tally[c] for c in MISS_CLASSES):
        raise Refuse(20, "classes")


def deliver(st, ctx):
    kind, root, out = st.kind, ctx["root"], os.path.join(st.wall, "out")
    setdir = os.path.join(root, "fixtures", "evaluation", ctx["set"])
    d = st.counts["delivered"]
    if kind == "writer":
        src = os.path.join(out, "set")
        if os.path.islink(src) or not os.path.isdir(src):
            raise Refuse(20, "missing")
        try:
            files = plain_files(src)
        except (ValueError, OSError):
            raise Refuse(20, "link")
        if not files:
            raise Refuse(20, "missing")
        hidden = os.path.join(setdir, "hidden")
        if ctx["round"] == 1:
            # every check first; a new set's folders are made only after they pass, and removed on a failed copy (F5)
            if os.path.lexists(hidden):
                raise Refuse(20, "destination")
            missing, have = [], setdir
            while not os.path.lexists(have):
                missing.append(have)
                have = os.path.dirname(have)
            if not real_inside(have, root) or not os.path.isdir(have) or os.path.islink(have):
                raise Refuse(20, "destination")
            made = []
            try:
                for folder in reversed(missing):
                    os.mkdir(folder, 0o755)
                    made.append(folder)
                os.mkdir(hidden, 0o755)
                made.append(hidden)
                tmp = os.path.join(hidden, f".r1-{st.run}.tmp")
                got = copy_set(src, tmp)
                for e in sorted(os.listdir(tmp)):
                    os.rename(os.path.join(tmp, e), os.path.join(hidden, e))
                os.rmdir(tmp)
            except BaseException:
                if hidden in made:
                    remove_tree(hidden)
                for folder in reversed([x for x in made if x != hidden]):
                    try:
                        os.rmdir(folder)
                    except OSError:
                        pass
                raise Refuse(20, "copy")
        else:
            if (not real_inside(setdir, root) or not real_inside(hidden, root) or not os.path.isdir(hidden)
                    or os.path.islink(hidden)):
                raise Refuse(20, "destination")
            new = os.path.join(hidden, f".r2-{st.run}.tmp")
            old = os.path.join(hidden, f".r1-{st.run}.old")
            moved_old, moved_new = [], []
            try:
                got = copy_set(src, new)
                os.mkdir(old, 0o700)
                for e in sorted(os.listdir(hidden)):
                    if e not in (os.path.basename(new), os.path.basename(old)):
                        os.rename(os.path.join(hidden, e), os.path.join(old, e))
                        moved_old.append(e)
                for e in sorted(os.listdir(new)):
                    os.rename(os.path.join(new, e), os.path.join(hidden, e))
                    moved_new.append(e)
                os.rmdir(new)
            except BaseException:
                for e in moved_new:
                    os.rename(os.path.join(hidden, e), os.path.join(new, e))
                for e in moved_old:
                    os.rename(os.path.join(old, e), os.path.join(hidden, e))
                remove_tree(new)
                if os.path.isdir(old) and not os.listdir(old):
                    os.rmdir(old)
                raise Refuse(20, "copy")
            st.replaced = old
        d.update(files=len(got), sha256=bundle_sha(got), to="set")
        return
    if kind == "checker":
        src, dst = os.path.join(out, "notes.md"), os.path.join(setdir, f"XCHECK-r{ctx['round']}.md")
        dest_dir = setdir
    elif kind == "auditor":
        src = os.path.join(out, "classes.json")
        dest_dir = os.path.join(root, "runs", ctx["audit"])
        dst = os.path.join(dest_dir, "miss-classes.json")
    else:
        raise Refuse(20, "destination")  # the labeller kind runs set-up A's flows only
    if not regular(src):
        raise Refuse(20, "missing")
    if not real_inside(dest_dir, root) or not os.path.isdir(dest_dir) or os.path.islink(dest_dir):
        raise Refuse(20, "destination")
    data = read_plain(src, out)  # (W2-173 S3, S4) the file's fixed form and the result's counts, before it lands
    if data is None:
        raise Refuse(20, "missing")
    if kind == "checker":
        check_notes(data, staged_set_ids(st.wall), ctx["result"])
    else:
        check_classes(data, staged_miss_ids(st.wall), ctx["result"])
    h = deliver_file(src, dst)
    d.update(files=1, sha256=h, to=DELIVERS[kind])
    if kind == "auditor":
        with open(os.path.join(ctx["runs_indep"], "AUDITS.log"), "a", encoding="utf-8") as f:
            f.write(json.dumps({"time": utc_iso(), "commit": ctx["commit"], "run": st.run,
                                "audit": ctx["audit"]}) + "\n")


# -- set-up A's deliveries (S16, S26, S27): every check first, then a temporary name, hashed, renamed; all or nothing --
class Landing:
    """New files (an existing one refuses 20) and replaced files (the auditor's labels.jsonl and owner.jsonl), each
    written beside its destination under a temporary name and read back; then all renamed in turn. On any failure
    every rename done is undone, every temporary file and every folder this landing made removed: 20."""

    def __init__(self, top):
        self.top, self.made, self.items = top, [], []

    def folder(self, path):
        missing, have = [], path
        while not os.path.lexists(have):
            missing.append(have)
            have = os.path.dirname(have)
        if not real_inside(have, self.top) or not os.path.isdir(have) or os.path.islink(have):
            raise Refuse(20, "destination")
        for f in reversed(missing):
            os.mkdir(f, 0o755)
            self.made.append(f)

    def check(self, dst, replace=False):
        if not real_inside(os.path.dirname(dst), self.top) and os.path.lexists(os.path.dirname(dst)):
            raise Refuse(20, "destination")
        if os.path.lexists(dst) and (not replace or not regular(dst)):
            raise Refuse(20, "destination")

    def add(self, dst, data, replace=False):
        self.check(dst, replace)
        self.folder(os.path.dirname(dst))
        tmp = os.path.join(os.path.dirname(dst), "." + os.path.basename(dst) + f".{secrets.token_hex(4)}.tmp")
        write_new(tmp, data, 0o644)
        self.items.append((tmp, dst, replace))
        if sha_file(tmp) != sha_bytes(data):
            raise Refuse(20, "copy")
        return sha_bytes(data)

    def commit(self):
        done = []
        try:
            for tmp, dst, replace in self.items:
                old = read_plain(dst, self.top) if replace and os.path.lexists(dst) else None
                if replace:
                    os.replace(tmp, dst)
                else:
                    os.link(tmp, dst)  # never over an entry made meanwhile
                    os.unlink(tmp)
                done.append((dst, old))
        except BaseException:
            for dst, old in reversed(done):
                try:
                    if old is None:
                        os.unlink(dst)
                    else:
                        back = dst + f".{secrets.token_hex(4)}.back"
                        write_new(back, old, 0o644)
                        os.replace(back, dst)
                except OSError:
                    pass
            self.abort()
            raise Refuse(20, "copy")

    def abort(self):
        for tmp, _dst, _r in self.items:
            if os.path.lexists(tmp):
                os.unlink(tmp)
        for f in reversed(self.made):
            try:
                os.rmdir(f)
            except OSError:
                pass


def out_file(out, name):
    data = read_plain(os.path.join(out, name), out)
    if data is None:
        raise Refuse(20, "missing")
    return data


def valid_hand(obj, ids):
    return (isinstance(obj, dict) and isinstance(obj.get("id"), str) and obj["id"] in ids
            and obj.get("label") in LABELS and rule_class(obj.get("rule_class")) is not None
            and isinstance(obj.get("clauses"), list) and all(isinstance(c, str) for c in obj["clauses"])
            and isinstance(obj.get("reason"), str))


def merge_labels(ctx, hand_data):
    """S26: the first labeller's round 2: every required id hand-labelled, then one line per staged id."""
    sgx = ctx["sgx"]
    ids = [i for i, _b, _o, _r in sgx["staged"]]
    script = sgx["script_labels"]
    try:
        hand = {}
        for _raw, obj in jsonl_objects(hand_data):
            if not valid_hand(obj, set(ids)):
                raise ValueError("hand")
            hand[obj["id"]] = obj
    except (ValueError, UnicodeDecodeError):
        raise Refuse(20, "hand")
    need = {i for i in ids if script[i]["uncertain"] or script[i]["rule_class"] <= 13} | set(sgx["sample_ids"])
    if not need <= set(hand):
        raise Refuse(20, "hand")
    lines = []
    for i in ids:
        src, how = (hand[i], "hand") if i in hand else (dict(script[i], reason=""), "script")
        lines.append(json.dumps({"id": i, "label": src["label"], "rule_class": rule_class(src["rule_class"]),
                                 "clauses": src["clauses"], "reason": src["reason"], "how": how}) + "\n")
    return "".join(lines).encode("utf-8")


DECISION_KEYS = {"id", "label", "rule_class", "basis", "agrees_with", "flag", "reason"}


def check_decisions(data, cases):
    """S27: one line per case, in the disputes' order, the brief's fields and values; else 20."""
    try:
        rows = [o for _raw, o in jsonl_objects(data)]
    except (ValueError, UnicodeDecodeError):
        raise Refuse(20, "decisions")
    if [o["id"] for o in rows] != cases:
        raise Refuse(20, "decisions")
    for o in rows:
        rc = rule_class(o.get("rule_class"))
        if (set(o) != DECISION_KEYS or o["label"] not in LABELS or rc is None or not isinstance(o["basis"], list)
                or not all(isinstance(b, str) for b in o["basis"]) or o["agrees_with"] not in ("x", "y", "neither")
                or o["flag"] not in ("none", "cannot-settle", "may-change-verdict") or not isinstance(o["reason"], str)
                or (o["reason"] == "") != (o["flag"] == "none")):
            raise Refuse(20, "decisions")
        o["rule_class"] = rc  # (F23) stored as an integer
    return rows


LABEL2_KEYS = {"id", "label", "rule_class", "clauses", "how", "reason"}


def check_labels2(data, sample_ids):
    """S30 (F20): the second labeller's round 2: one valid line per staged sample id and no other id; delivered in its
    order, each line as written but `rule_class` an integer; else 20."""
    try:
        rows = [o for _raw, o in jsonl_objects(data)]  # a repeated id raises
    except (ValueError, UnicodeDecodeError):
        raise Refuse(20, "labels")
    if sorted(o["id"] for o in rows) != sorted(sample_ids):
        raise Refuse(20, "labels")
    lines = []
    for o in rows:
        rc = rule_class(o.get("rule_class"))
        if (set(o) != LABEL2_KEYS or o["label"] not in LABELS or rc is None or not isinstance(o["clauses"], list)
                or not all(isinstance(c, str) for c in o["clauses"]) or o["how"] != "hand"
                or not isinstance(o["reason"], str)):
            raise Refuse(20, "labels")
        lines.append(json.dumps(dict(o, rule_class=rc)) + "\n")
    return "".join(lines).encode("utf-8")


def deliver_sgx(st, ctx):
    sgx, rnd = ctx["sgx"], ctx["round"]
    flow, h, top = sgx["flow"], sgx["h"], sgx["top"]
    out = os.path.join(st.wall, "out")
    labels = os.path.join(h, "labels")
    if sgx.get("stopped", "none") != "none":  # (F19, S29) a result that says it stopped delivers nothing
        raise Refuse(20, "stopped")
    land = Landing(top)
    d = st.counts["delivered"]
    try:
        if flow in ("sgx1-writer-1", "sgx1-writer-2"):
            sha = land.add(os.path.join(h, "planted", "cases.jsonl"), out_file(out, "cases.jsonl"))
            got, to = [("cases.jsonl", sha)], "cases"
        elif flow in ROUND1_FILES and rnd == 1:  # a labeller's round 1: its files kept for round 2
            names = sorted(ROUND1_FILES[flow])
            datas = {n: out_file(out, n) for n in names}
            for n in names:
                land.check(os.path.join(labels, f"r1-{ctx['brief_id']}", n))
            if flow == "sgx1-labeller-1":  # (F18, S25) the rule script passes the confined check before it lands
                try:
                    staged_rules(sgx, datas["label_rules.py"], ctx["home"])
                except (Refuse, OSError):
                    raise Refuse(20, "rules")
            got = [(n, land.add(os.path.join(labels, f"r1-{ctx['brief_id']}", n), datas[n])) for n in names]
            to = "round1"
        elif flow == "sgx1-labeller-1":
            merged = merge_labels(ctx, out_file(out, "hand-labels.jsonl"))
            got, to = [("hand-labels.jsonl", land.add(os.path.join(labels, "labels.jsonl"), merged))], "labels"
        elif flow == "sgx1-labeller-2":
            checked = check_labels2(out_file(out, "labels-2.jsonl"), sgx["overlap_ids"])
            got, to = [("labels-2.jsonl", land.add(os.path.join(labels, "labels-2.jsonl"), checked))], "labels"
        else:
            got, to = deliver_audit(st, ctx, land, out_file(out, "decisions.jsonl")), "decisions"
        land.commit()
    except BaseException:
        land.abort()
        raise
    d.update(files=len(got), sha256=delivered_sha(got), to=to)
    if to == "round1":  # round 2 checks each file against these
        d["files_sha256"] = dict(got)


def deliver_audit(st, ctx, land, data):
    """S27: the decisions mapped back, the map, labels.jsonl rewritten (its old bytes kept in history/), the flagged
    cases appended to owner.jsonl. No AUDITS.log line."""
    sgx = ctx["sgx"]
    labels = os.path.join(sgx["h"], "labels")
    cases = [i for i, _a in sgx["disputes"]]
    rows = check_decisions(data, cases)
    xmap = sgx["xmap"]
    who = {1: "labeller-1", 2: "labeller-2"}
    mapped, owner, settle = [], [], {}
    for o in rows:
        m = dict(o)
        if o["agrees_with"] in ("x", "y"):
            m["agrees_with"] = who[xmap[o["id"]][o["agrees_with"]]]
        mapped.append(m)
        settle[o["id"]] = m
        if o["flag"] != "none":
            owner.append({"id": o["id"], "labeller-1": part(sgx["labels1"][o["id"]]),
                          "labeller-2": part(sgx["labels2"][o["id"]]), "decision": m})
    dec_bytes = "".join(json.dumps(m) + "\n" for m in mapped).encode("utf-8")
    for p in (f"{st.run}.decisions.jsonl", f"{st.run}.map.json"):
        land.check(os.path.join(labels, "audit", p))
    sha = land.add(os.path.join(labels, "audit", f"{st.run}.decisions.jsonl"), dec_bytes)
    land.add(os.path.join(labels, "audit", f"{st.run}.map.json"),
             (json.dumps({i: xmap[i] for i in cases}) + "\n").encode("utf-8"))
    old = read_plain(os.path.join(labels, "labels.jsonl"), sgx["top"])
    if old is None or old != sgx["labels1_bytes"]:
        raise Refuse(20, "destination")  # labels.jsonl changed since the wall was built
    land.add(os.path.join(labels, "history", f"labels.{st.run}.jsonl"), old)
    lines = []
    for raw, obj in jsonl_objects(old):
        if obj["id"] in settle:
            m = settle[obj["id"]]
            if m["flag"] == "none":  # (F22) the auditor's decision replaces both sides' labels
                obj = {"id": obj["id"], "label": m["label"], "rule_class": m["rule_class"], "clauses": m["basis"],
                       "reason": m["reason"], "how": "audit"}
            else:
                obj = dict(obj, how="owner")
            raw = (json.dumps(obj) + "\n").encode("utf-8")
        lines.append(raw)
    land.add(os.path.join(labels, "labels.jsonl"), b"".join(lines), replace=True)
    if owner:
        prev = read_plain(os.path.join(labels, "owner.jsonl"), sgx["top"])
        if prev is None and os.path.lexists(os.path.join(labels, "owner.jsonl")):
            raise Refuse(20, "destination")
        prev = prev or b""
        if prev and not prev.endswith(b"\n"):
            prev += b"\n"
        land.add(os.path.join(labels, "owner.jsonl"),
                 prev + "".join(json.dumps(x) + "\n" for x in owner).encode("utf-8"), replace=True)
    return [("decisions.jsonl", sha)]


def part(obj):
    return {k: obj[k] for k in LABEL_PART if k in obj}


def check_result(st, ctx):
    out = os.path.join(st.wall, "out")
    st.counts["out"]["files"] = out_files(out)
    path = os.path.join(out, "result.json")
    st.counts["out"]["schema_ok"] = False
    if not regular(path) or os.path.getsize(path) > MOST_RESULT_BYTES:
        raise Refuse(20, "missing")
    try:
        with open(path, "rb") as f:
            res = load_json_strict(f.read().decode("utf-8"))
    except (ValueError, UnicodeDecodeError, OSError):
        raise Refuse(20, "unreadable")
    if (not ctx.get("sgx") and st.kind in ("writer", "checker") and isinstance(res, dict)
            and res.get("stopped") in STOPPED[1:]):
        # (W2-173 S2) a result that says it stopped: its word counted, nothing checked further, nothing delivered
        st.counts["out"]["stopped"] = res["stopped"]
        st.counts["out"]["schema_ok"] = None
        raise Refuse(21, "stopped")
    if not isinstance(res, dict) or not schema_ok(res, ctx["result_schema"]):
        raise Refuse(20, "schema")
    if ctx.get("sgx"):
        # set-up A: each round's own form; numbers (an object of numbers as an object) and the fixed `stopped` word
        if "round" in res and res["round"] != ctx["round"]:
            raise Refuse(20, "schema")
        copy_sgx_numbers(st, res)
        ctx["sgx"]["stopped"] = res.get("stopped", "none")  # the delivery refuses a stopped result (F19)
    else:
        # the four first versions' numbers; a revised schema must still carry them
        try:
            copy_numbers(st, st.kind, res)
        except (KeyError, AttributeError, TypeError):
            raise Refuse(20, "schema")
        ctx["result"] = res  # the checker's and the auditor's delivery check their file against its counts (S3, S4)
    st.counts["out"]["schema_ok"] = True
    st.log("result", "schema", "ok")


# -- packing -------------------------------------------------------------------------------------------------------
def pack(st):
    """The wall, its session file (and writer round 2's replaced files) into <run>.tar (0400); the wall, its tree and
    the session file removed."""
    tar_path = os.path.join(os.path.dirname(st.wall), st.run + ".tar")
    tmp = os.path.join(os.path.dirname(st.wall), "." + st.run + ".tar.tmp")
    try:
        if os.path.lexists(tar_path):
            raise RuntimeError("tar exists")
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "wb") as f, tarfile.open(fileobj=f, mode="w", format=tarfile.PAX_FORMAT) as t:
            if os.path.isdir(st.wall):
                t.add(st.wall, arcname=st.run, recursive=True)
            if st.session_file and os.path.lexists(st.session_file):
                t.add(st.session_file, arcname=st.run + ".session.json")
            if st.replaced and os.path.isdir(st.replaced):
                t.add(st.replaced, arcname=st.run + "/replaced-hidden", recursive=True)
        os.chmod(tmp, 0o400)
        os.rename(tmp, tar_path)
    except Exception as exc:
        st.log("pack", "failed", type(exc).__name__)
        if os.path.lexists(tmp):
            os.unlink(tmp)
        if st.tree_made:
            remove_tree(st.tree)
        return False
    remove_tree(st.wall)
    if st.session_file and os.path.lexists(st.session_file):
        os.unlink(st.session_file)
    if st.replaced:
        remove_tree(st.replaced)
    if st.tree_made:
        remove_tree(st.tree)
    st.log("pack", "ok")
    return True


# -- the build -----------------------------------------------------------------------------------------------------
def fill_text(text, vals, escape=False):
    for k, v in vals.items():
        text = text.replace(k, json.dumps(v)[1:-1] if escape else v)
    return text


def choose_run(walls, kind, trees, runs_indep, set_name, rnd):
    for _ in range(5):
        rid = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + f"-{set_name}-r{rnd}"
        taken = (os.path.join(walls, kind, rid), os.path.join(walls, kind, rid + ".tar"),
                 os.path.join(walls, kind, rid + ".session.json"), os.path.join(trees, f"{kind}-{rid}"),
                 os.path.join(runs_indep, kind, rid))
        if not any(os.path.lexists(p) for p in taken):
            return rid
        time.sleep(1.0 - (time.time() % 1.0) + 0.01)
    return rid


def build_tree(st, repo, commit, excluded):
    """B3: git archive <commit> less the exclusions, written file by file (fresh mtimes), read-only."""
    if os.path.lexists(st.tree):
        raise Refuse(13, "order")  # something made the tree before the script did
    os.mkdir(st.tree, 0o700)
    st.tree_made = True
    files = 0
    proc = subprocess.Popen(["git", "-C", repo, "archive", "--format=tar", commit], stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)
    try:
        with tarfile.open(fileobj=proc.stdout, mode="r|") as t:
            for m in t:
                name = m.name
                parts = name.split("/")
                if (name.startswith("/") or ".." in parts or m.issym() or m.islnk()
                        or not (m.isreg() or m.isdir()) or ".git" in parts or "" in parts[:-1]):
                    raise Refuse(14, "archive")
                name = name.rstrip("/")
                if not name or excluded(name, m.isdir()):
                    continue
                dest = os.path.join(st.tree, name)
                if m.isdir():  # the archive's folders less the excluded, an emptied one too
                    os.makedirs(dest, mode=0o700, exist_ok=True)
                    continue
                os.makedirs(os.path.dirname(dest), mode=0o700, exist_ok=True)
                src = t.extractfile(m)
                fd = os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
                with os.fdopen(fd, "wb") as f:
                    shutil.copyfileobj(src, f, 1 << 20)
                os.chmod(dest, 0o444)
                files += 1
    finally:
        if proc.poll() is None:
            proc.stdout.close()
            proc.kill()
        proc.wait()
    if proc.returncode != 0:
        raise Refuse(14, "archive")
    for folder, _dirs, _names in os.walk(st.tree, topdown=False):
        os.chmod(folder, 0o555)
    return files


def content_mtimes(st):
    """(the least mtime, any link) over every file under input/ and the tree."""
    least, link = None, False
    for top in (os.path.join(st.wall, "input"), st.tree):
        for folder, dirs, names in os.walk(top):
            for nm in names + dirs:
                s = os.lstat(os.path.join(folder, nm))
                if stat.S_ISLNK(s.st_mode):
                    link = True
                elif stat.S_ISREG(s.st_mode):
                    least = s.st_mtime_ns if least is None else min(least, s.st_mtime_ns)
    return least, link


def seed_check(st, ledger, seed_sha):
    """13: this run's ledger line, its sha256 the seed file's, and the seed (then the ledger) before all content."""
    seed_path = os.path.join(st.wall, "seed.txt")
    if not regular(seed_path) or sha_file(seed_path) != seed_sha:
        raise Refuse(13, "seed")
    line = None
    try:
        with open(ledger, encoding="utf-8") as f:
            for raw in f:
                try:
                    obj = json.loads(raw)
                except ValueError:
                    continue
                if isinstance(obj, dict) and obj.get("run") == st.run and obj.get("kind") == st.kind:
                    line = obj
    except OSError:
        raise Refuse(13, "ledger")
    if not line or line.get("seed_sha256") != seed_sha:
        raise Refuse(13, "ledger")
    seed_ns = os.lstat(seed_path).st_mtime_ns
    ledger_ns = os.stat(ledger).st_mtime_ns
    least, link = content_mtimes(st)
    if link or least is None or not (seed_ns < ledger_ns < least):
        raise Refuse(13, "order")


def build_and_run(st, o, root, over, cwd, home):
    c = st.counts
    kind, rnd, set_name = o.kind, int(o.round or 1), o.set
    st.dry = o.dry
    runs = over["GOV_INDEP_RUNS_DIR_path"]
    trees = over["GOV_INDEP_TREES_DIR_path"]
    runs_indep = os.path.join(runs, "indep")
    walls = os.path.join(root, WALLS)
    st.walls = walls
    approved_path = os.path.join(walls, "APPROVED")
    approved = None
    if regular(approved_path):
        with open(approved_path, "rb") as f:
            approved = f.read()
        c["approved_sha256"] = sha_bytes(approved)

    # 14: the repository, the commit, the main line
    st.stage = 14
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=cwd, capture_output=True, timeout=60)
    if top.returncode != 0:
        raise Refuse(14, "repo")
    repo = os.path.realpath(top.stdout.decode().strip())
    if not full(COMMIT_RX, o.commit):
        raise Refuse(14, "resolve")
    r = git(repo, "rev-parse", "--verify", "--quiet", o.commit + "^{commit}")
    commit = r.stdout.decode().strip()
    if r.returncode != 0 or not full(HEX40, commit):
        raise Refuse(14, "resolve")
    mainline = next((ref for ref in ("refs/heads/w2/integrate", "refs/heads/main")
                     if git(repo, "show-ref", "--verify", "--quiet", ref).returncode == 0), None)
    if not mainline or git(repo, "merge-base", "--is-ancestor", commit, mainline).returncode != 0:
        raise Refuse(14, "reach")
    c["commit"] = commit

    # 11: the template, as approved
    st.stage = 11
    if approved is None:
        raise Refuse(11, "approved")
    t_lines, b_lines = parse_approved(approved)
    tmpl = {}
    for name in TEMPLATE_FILES:
        rel = f"{TEMPLATE_DIR}/{name}"
        data = blob(repo, commit, rel)
        if data is None or t_lines.get(rel) != {sha_bytes(data)}:
            raise Refuse(11, "template")
        tmpl[name] = data
    kinds = load_kinds(tmpl["kinds.yaml"])
    briefs = load_briefs(tmpl["kinds.yaml"])
    if kinds is None or kind not in kinds or briefs is None:
        raise Refuse(11, "kinds")
    spec = kinds[kind]
    ex_globs = excludes_of(tmpl["tree-exclude.txt"])
    excluded = excluded_by(ex_globs)  # the selection's rule (S5): less tree-exclude.txt only
    c["template_ok"] = True

    # 10: the brief, as approved, and its front matter; the inputs it needs
    st.stage = 10
    brief_path = norm_repo_path(o.brief)
    if brief_path is None:
        raise Refuse(10, "path")
    want = o.brief_sha256.strip().lower()
    brief = blob(repo, commit, brief_path)
    if brief is None or sha_bytes(brief) != want:
        raise Refuse(10, "bytes")
    if not any(h == want and k == kind and norm_repo_path(p) == brief_path for h, k, p in b_lines):
        raise Refuse(10, "approved")
    c["brief_sha256"] = want
    fm = front_matter(brief)
    if fm is None or fm.get("kind") != kind:
        raise Refuse(10, "front_matter")
    model, schema_name, sample_n, brief_id, entry = resolve_brief(fm, kind, spec, briefs)
    effort = fm.get("effort")
    if "effort" in fm and not (isinstance(effort, str) and effort in EFFORTS):
        raise Refuse(10, "effort")  # (W2-173 S1) one of the five, or no line at all
    c["effort"] = effort
    flow = entry["flow"] if entry else None
    budget, timeout_s = fm.get("budget_usd", spec["budget_usd"]), fm.get("timeout_s", spec["timeout_s"])
    if not (is_number(budget) and 0 < budget <= spec["budget_usd"]):
        raise Refuse(10, "budget")
    if not (is_number(timeout_s) and 0 < timeout_s <= spec["timeout_s"]):
        raise Refuse(10, "timeout")
    result_schema_sha, result_schema = read_schema(schema_name)  # read once; checked from these bytes (F8)
    if result_schema is None:
        raise Refuse(10, "schema")
    sgx = None
    if flow:
        # the half and the round the flow allows (17, nothing built), then its inputs (10 before anything is written)
        if set_name not in FLOWS[flow][1]:
            raise Refuse(17, "set")
        if rnd not in FLOWS[flow][2]:
            raise Refuse(17, "round")
        sgx = plan_sgx(flow, rnd, set_name, root, runs, runs_indep, brief_id, want, repo, commit)
        plan = []
        tree_ex = excluded_by(ex_globs + list(entry.get("tree_exclude", [])))  # S23: the entry's globs too
    else:
        plan = plan_inputs(kind, rnd, root, set_name, o.audit)
        tree_ex = excluded
    try:
        last = last_audit(runs_indep)
    except (OSError, ValueError, UnicodeDecodeError):
        raise Refuse(10, "audits")

    # 14: no link or submodule in the commit's tree; the last audit's commit is there
    st.stage = 14
    lt = git(repo, "ls-tree", "-r", "-z", "--full-tree", commit)
    if lt.returncode != 0:
        raise Refuse(14, "tree")
    for entry in z_list(lt.stdout):
        if entry.split(" ", 1)[0] in ("120000", "160000"):
            raise Refuse(14, "links")
    if last and git(repo, "cat-file", "-e", last + "^{commit}").returncode != 0:
        raise Refuse(14, "last_audit")

    # 15: the hidden part's file budget
    st.stage = 15
    pm = blob(repo, commit, PATH_MAP)
    globs = hidden_globs(pm) if pm is not None else None
    if globs is None:
        raise Refuse(15, "path_map")
    expected = WALL_FIXED + len(plan) + RUN_EXTRA if not sgx else sgx_expected(sgx, rnd)
    if hidden_count(root, globs) + expected > FILE_BUDGET:
        raise Refuse(15, "budget")

    # 18: the first labeller's round 2 runs its round-1 rule script, confined, before anything is written
    if sgx:
        sgx["protected"] = [os.path.realpath(home), root, runs, trees, repo]  # no bind may reach these
    if flow == "sgx1-labeller-1" and rnd == 2:
        st.stage = 18
        sgx["script_raw"], sgx["script_labels"] = staged_rules(sgx, sgx["round1"]["label_rules.py"], home)
        st.log("rules", "ok", len(sgx["staged"]))

    # the run id; B1: an empty wall, no tree
    st.stage = 12
    rid = choose_run(walls, kind, trees, runs_indep, set_name, rnd)
    st.run = c["run"] = rid
    st.wall = os.path.join(walls, kind, rid)
    st.tree = os.path.join(trees, f"{kind}-{rid}")
    st.counts_dir = os.path.join(runs_indep, kind, rid)
    st.log("run", kind, "round", rnd, "dry" if o.dry else "real")
    test_hook = bool(os.environ.get("GOV_INDEP_TEST_HOOK"))  # recorded, never refused: the cases use it (F3)
    if test_hook:
        st.log("test_hook", "set")
    hook(st, "before_wall")
    if os.path.lexists(st.wall):
        if os.path.islink(st.wall) or not os.path.isdir(st.wall) or os.listdir(st.wall):
            raise Refuse(12, "wall")
    if os.path.lexists(st.tree):
        raise Refuse(12, "tree")
    os.makedirs(os.path.join(walls, kind), mode=0o755, exist_ok=True)
    if not os.path.lexists(st.wall):
        os.mkdir(st.wall, 0o700)
    st.built = True
    os.chmod(st.wall, 0o700)
    os.makedirs(trees, mode=0o755, exist_ok=True)
    os.makedirs(st.counts_dir, mode=0o755, exist_ok=True)
    st.log("B1", "ok")

    # B2: the seed first, then its ledger line
    st.stage = 13
    seed = secrets.randbits(63) if (o.seed or "new") == "new" else int(o.seed)
    seed_path = os.path.join(st.wall, "seed.txt")
    write_new(seed_path, f"{seed}\n".encode(), 0o444)
    seed_sha = sha_file(seed_path)
    seed_ns = os.lstat(seed_path).st_mtime_ns
    c["seed_sha256"] = seed_sha
    ledger = os.path.join(runs_indep, "SEEDS.log")
    wait_past(seed_ns, runs_indep)
    with open(ledger, "a", encoding="utf-8") as f:
        f.write(json.dumps({"time": utc_iso(), "kind": kind, "run": rid, "commit": commit, "seed": seed,
                            "seed_sha256": seed_sha, "set": set_name, "round": rnd, "dry": bool(o.dry)}) + "\n")
        f.flush()
        os.fsync(f.fileno())
    ledger_ns = os.stat(ledger).st_mtime_ns
    wait_past(ledger_ns, trees)
    wait_past(ledger_ns, st.wall)
    st.log("B2", "ok")
    hook(st, "after_seed")

    # B3: the plain tree
    st.stage = 14
    tree_files = build_tree(st, repo, commit, tree_ex)
    st.log("B3", "files", tree_files)
    hook(st, "after_tree")

    # B4: the input by rule
    st.stage = 10
    tracked = z_list(git(repo, "ls-tree", "-r", "--name-only", "-z", commit).stdout)
    have = set(tracked)
    changed = []
    if last:
        dif = git(repo, "diff", "--name-only", "--no-renames", "-z", last, commit)
        if dif.returncode != 0:
            raise Refuse(14, "diff")
        changed = sorted({p for p in z_list(dif.stdout) if p in have and not excluded(p)})
    chosen = set(changed)
    others = [p for p in tracked if not excluded(p) and p not in chosen]
    sample = random.Random(seed).sample(others, min(sample_n, len(others)))
    selection = {"commit": commit, "last_audit": last, "seed_sha256": seed_sha, "changed": changed,
                 "sample": sample}
    sel_counts = {"changed": len(changed), "sample": len(sample), "overlap": 0}
    staged = {}  # set-up A's files: wall-relative path -> bytes
    if sgx:
        staged = stage_sgx(sgx, rnd, seed, commit)
        if kind == "writer":
            staged["input/selection.json"] = (json.dumps(selection, indent=1) + "\n").encode()
        else:  # no selection in a labeller's or the auditor's wall: its sample and overlap counted instead
            sel_counts = {"changed": 0, "sample": len(sgx.get("sample_ids", [])),
                          "overlap": sgx.get("n_overlap", 0)}
    inp = os.path.join(st.wall, "input")
    if os.path.lexists(inp):
        raise Refuse(13, "order")  # something wrote input/ before the script chose it
    os.mkdir(inp, 0o700)
    if not sgx:
        write_new(os.path.join(inp, "selection.json"), (json.dumps(selection, indent=1) + "\n").encode(), 0o444)
    for rel, data in sorted(staged.items()):
        dst = os.path.join(st.wall, rel)
        os.makedirs(os.path.dirname(dst), mode=0o700, exist_ok=True)
        write_new(dst, data, 0o444)
    for src, rel in plan:
        dst = os.path.join(st.wall, rel)
        os.makedirs(os.path.dirname(dst), mode=0o700, exist_ok=True)
        copy_new(src, dst, 0o444)
    for folder, _dirs, _names in os.walk(inp, topdown=False):
        os.chmod(folder, 0o555)
    c["selection"] = dict(sel_counts)
    st.log("B4", "changed", sel_counts["changed"], "sample", sel_counts["sample"], "staged", len(plan) + len(staged))
    hook(st, "after_input")

    # 13: the seed came first
    st.stage = 13
    seed_check(st, ledger, seed_sha)
    st.log("seed_check", "ok")

    # B5: the session's files
    st.stage = 11
    write_new(os.path.join(st.wall, "brief.md"), brief, 0o444)
    claude_md = fill_text(tmpl["CLAUDE.md.tmpl"].decode("utf-8"),
                          {"@KIND@": kind, "@RUN@": rid, "@BRIEF_SHA@": want, "@TREE@": st.tree, "@COMMIT@": commit})
    write_new(os.path.join(st.wall, "CLAUDE.md"), claude_md.encode("utf-8"), 0o444)
    others_deny = [f"Read(/{walls}/{k}/**)" for k in KINDS if k != kind]
    others_deny += [f"Read(/{walls}/{kind}/{e}/**)" for e in sorted(os.listdir(os.path.join(walls, kind)))
                    if e != rid]
    vals = {"@WALLS@": walls, "@WALL@": st.wall, "@TREE@": st.tree, "@REPO@": repo,
            "@WORKTREES@": os.path.join(os.path.realpath(home), "gov-os-worktrees"), "@RUNS@": runs,
            "@HOME@": os.path.realpath(home), "@SETS_ROOT@": root, "@MODEL@": model}
    settings = fill_text(tmpl["settings.json.tmpl"].decode("utf-8"), vals, escape=True)
    settings = settings.replace('"@OTHER_WALLS@"', ",\n      ".join(json.dumps(x) for x in others_deny))
    cl = os.path.join(st.wall, ".claude")
    os.mkdir(cl, 0o700)
    write_new(os.path.join(cl, "settings.json"), settings.encode("utf-8"), 0o444)
    write_new(os.path.join(cl, "wall_hook.py"), tmpl["wall_hook.py"], 0o444)
    os.chmod(cl, 0o555)
    os.mkdir(os.path.join(st.wall, "out"), 0o700)
    os.chmod(os.path.join(st.wall, "out"), 0o700)

    # B6: the manifest
    manifest = {"act": ACT, "kind": kind, "run": rid, "set": set_name, "round": rnd, "audit": o.audit,
                "commit": commit, "repo": repo, "tree": st.tree, "runs": runs, "home": os.path.realpath(home),
                "sets_root": root, "brief": brief_path, "brief_sha256": want, "seed_sha256": seed_sha,
                "settings_sha256": sha_bytes(settings.encode("utf-8")), "hook_sha256": sha_bytes(tmpl["wall_hook.py"]),
                "template_sha256": {n: sha_bytes(tmpl[n]) for n in TEMPLATE_FILES},
                "approved_sha256": c["approved_sha256"], "model": model, "effort": effort, "tools": list(spec["tools"]),
                "budget_usd": budget, "timeout_s": timeout_s, "prompt_sha256": PROMPT_SHA256,
                "result_schema": schema_name, "brief_id": brief_id if entry else None, "flow": flow,
                "selection": dict(sel_counts),
                "tree_files": tree_files, "seeded_before_content": True,
                "runs_override": bool(over.get("GOV_INDEP_RUNS_DIR")),
                "trees_override": bool(over.get("GOV_INDEP_TREES_DIR")), "dry": bool(o.dry),
                "test_hook": test_hook,
                "schema_sha256": {COUNTS_SCHEMA: st.counts_schema_sha, schema_name: result_schema_sha}}
    write_new(os.path.join(st.wall, "WALL.json"), (json.dumps(manifest, indent=1) + "\n").encode("utf-8"), 0o444)
    os.chmod(st.wall, 0o555)
    st.log("B5", "ok", "B6", "ok")
    if o.dry:
        c["status"] = "dry"
        return 0

    ctx = {"root": root, "trees": trees, "runs": runs, "runs_indep": runs_indep, "repo": repo, "home": home,
           "tools": list(spec["tools"]), "model": model, "effort": effort, "budget": budget, "timeout": timeout_s,
           "result_schema": result_schema, "set": set_name, "round": rnd, "audit": o.audit, "commit": commit,
           "sgx": sgx, "brief_id": brief_id}
    # the canary, then the session
    st.stage = 16
    hook(st, "before_canary")
    run_canary(st, ctx)
    st.stage = 21
    hook(st, "before_session")
    rc, backstop = run_session(st, ctx)
    hook(st, "after_session")
    subtype, sid = read_session(st, rc)
    if sid:  # the id the session reports, when it differs from the drawn one, is a key too (F1)
        st.trace_ids.add(sid)
    code = 0
    traces = check_traces(st)  # always runs: the drawn ids are known even when the output does not parse
    if backstop or rc in (124, 137) or rc < 0 or (c["session"]["is_error"] and subtype and "budget" in subtype):
        c["status"] = "stopped"
        code = 21
    else:
        st.stage = 20
        try:
            check_result(st, ctx)
            if sgx:
                deliver_sgx(st, ctx)
            else:
                deliver(st, ctx)
            c["status"] = "delivered"
            st.log("delivered", c["delivered"]["files"])
        except Refuse as r:
            if r.code == 21:  # (W2-173 S2) a memory writer's or checker's result that says it stopped
                c["status"] = "stopped"
                code = 21
                st.log("stopped", r.word)
            elif r.code != 20:
                raise
            else:
                c["status"] = "rejected"
                code = 20
                st.log("rejected", r.word)
    if code == 21:
        c["out"]["files"] = out_files(os.path.join(st.wall, "out"))
    pack(st)
    if traces:
        return 22
    return code


def counts_only(st, o, over):
    runs_indep = os.path.join(over["GOV_INDEP_RUNS_DIR_path"], "indep")
    path = os.path.join(runs_indep, o.kind, o.run, "counts.json")
    try:
        if not regular(path):
            raise ValueError("missing")
        with open(path, encoding="utf-8") as f:
            obj = load_json_strict(f.read())
        if st.counts_schema is None or not schema_ok(obj, st.counts_schema):
            raise ValueError("schema")
    except (OSError, ValueError, UnicodeDecodeError):
        raise Refuse(17, "counts")
    sys.stdout.write(json.dumps(obj, separators=(", ", ": ")) + "\n")
    sys.stdout.flush()
    return 0


def _on_signal(signum, _frame):
    raise Interrupted(signum)


def main(argv=None):
    st = State()
    cwd = os.getcwd()
    home = os.environ.get("HOME") or os.path.expanduser("~")
    st.home = home
    st.counts_schema_sha, st.counts_schema = read_schema(COUNTS_SCHEMA)  # read once, used from those bytes (F8)
    for s in (signal.SIGTERM, signal.SIGHUP):
        signal.signal(s, _on_signal)
    try:
        if sha_bytes(PROMPT.encode("utf-8")) != PROMPT_SHA256:
            raise Refuse(11, "prompt")
        try:
            o = parse_args(sys.argv[1:] if argv is None else argv)
        except ArgError:
            raise Refuse(17, "parse")
        root, over = check_args(o, st, cwd, home)
        if o.counts_only:
            return counts_only(st, o, over)
        code = build_and_run(st, o, root, over, cwd, home)
    except Refuse as r:
        code = r.code
        st.log("refused", code, r.word)
        _after_refusal(st, code)
    except SystemExit:
        raise
    except BaseException as exc:  # fail closed: the step's own code, the wall packed
        code = st.stage
        st.log("error", type(exc).__name__, "stage", code)
        if st.pgid:
            stop_group(st.pgid)
        if st.trace_ids:
            try:
                check_traces(st)
            except OSError:
                pass
        _after_refusal(st, code)
    return finish(st, code)


def _after_refusal(st, code):
    c = st.counts
    c["status"] = {20: "rejected", 21: "stopped"}.get(code, "refused")
    if st.built:
        pack(st)
    elif st.tree_made:
        remove_tree(st.tree)


if __name__ == "__main__":
    sys.exit(main())
