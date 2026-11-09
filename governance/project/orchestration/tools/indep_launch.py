#!/usr/bin/env python3
"""The independent sessions' launch script (W2-149; DEC-1101 (2)-(3) step 2, DEC-1109 (2); ACT-INDEP-WALLS-1).

Builds one walled folder for one job (writer, checker, auditor, labeller) from an owner-approved brief and the walls'
template, chooses its content by rule from a seed recorded first, checks with a canary that the wall's settings load,
starts one closed headless `claude -p` session in it, delivers its product by its own code and returns only counts.
Standard library, PyYAML and git; no gov import. The CTO runs it, from the repository:

  python3 governance/project/orchestration/tools/indep_launch.py --sets-root ~/gov-os-eval --kind writer --brief governance/project/indep-briefs/writer.md --brief-sha256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 --commit 6ff398a28 --set memory-recall-3 --round 1
  python3 governance/project/orchestration/tools/indep_launch.py --sets-root ~/gov-os-eval --kind checker --brief governance/project/indep-briefs/checker.md --brief-sha256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 --commit 6ff398a28 --set memory-recall-3 --round 1
  python3 governance/project/orchestration/tools/indep_launch.py --sets-root ~/gov-os-eval --kind auditor --brief governance/project/indep-briefs/auditor.md --brief-sha256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 --commit 6ff398a28 --set memory-recall-3 --audit e0
  python3 governance/project/orchestration/tools/indep_launch.py --sets-root ~/gov-os-eval --kind labeller --brief governance/project/indep-briefs/labeller.md --brief-sha256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 --commit 6ff398a28 --set sandbox-labels --round 2
  python3 governance/project/orchestration/tools/indep_launch.py --sets-root /tmp/planted-sets --kind writer --brief governance/project/indep-briefs/writer.md --brief-sha256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 --commit 6ff398a28 --set memory-recall-3 --seed 17 --dry
  python3 governance/project/orchestration/tools/indep_launch.py --sets-root ~/gov-os-eval --kind writer --run 20261109T120000Z-memory-recall-3-r1 --counts-only

The line names only --sets-root <root>: never a folder under it (the guard's line rule, DEC-1097 (2)); the script
derives every folder under the root in its own code. --dry belongs on planted sets roots only: it leaves its wall and
tree in place for inspection (P-W2-149-DRY, option (a)).

Exit codes: 0 delivered or dry; 10 brief; 11 template; 12 wall or tree exists; 13 seed not first; 14 commit; 15 file
budget; 16 canary; 17 argument; 20 result rejected; 21 stopped; 22 a trace. Stdout's last line is the counts object
(indep-schemas/indep-counts.schema.json), also written as <runs>/indep/<kind>/<run>/counts.json once a run id exists.
No text from the session or out/ is printed or logged, and no path under the wall.
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
import shutil
import signal
import stat
import subprocess
import sys
import tarfile
import tempfile
import time

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
         16: "canary", 17: "argument", 20: "result", 21: "stopped", 22: "trace"}
DELIVERS = {"writer": "set", "checker": "notes", "auditor": "classes", "labeller": "labels"}
OUT_KEYS = {"writer": ("questions", "by_kind", "by_area"),
            "checker": ("checked", "accepted", "revise", "rejected"),
            "auditor": ("misses",),
            "labeller": ("labelled", "allow", "refuse", "agree", "disagree")}
BY_KIND = ("fact", "procedure", "decision", "location", "negative")
BY_AREA = ("contract", "decisions", "kernel", "code", "tests", "operations", "docs")
MISS_CLASSES = ("gold_wrong", "question_ambiguous", "retrieval_miss", "answer_wrong", "out_of_scope")
SEAL = "fixtures/evaluation/sandbox-guard-exp-1/hidden"  # the labellers' sealed folder under the sets root
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
        self.log_lines = []
        self.counts = {
            "act": ACT, "kind": None, "run": None, "set": None, "round": None, "commit": None,
            "brief_sha256": None, "approved_sha256": None, "seed_sha256": None,
            "template_ok": False, "override": False,
            "selection": {"changed": None, "sample": None, "overlap": None},
            "session": {"exit": None, "is_error": None, "turns": None, "cost_usd": None, "duration_s": None,
                        "refusals": None},
            "out": {"schema_ok": None, "files": None},
            "delivered": {"files": 0, "sha256": None, "to": None},
            "traces": 0, "status": "refused", "code": None, "reason": None}

    def log(self, *words):
        self.log_lines.append(utc_iso() + " " + " ".join(str(w) for w in words))

    def set_kind(self, kind):
        self.kind = kind
        self.counts["kind"] = kind
        for k in OUT_KEYS[kind]:
            self.counts["out"][k] = None


def finish(st, code):
    c = st.counts
    c["code"] = code
    c["reason"] = CODES.get(code)
    line = json.dumps(c, separators=(", ", ": "))
    try:
        with open(os.path.join(SCHEMAS, COUNTS_SCHEMA), encoding="utf-8") as f:
            if not schema_ok(c, json.load(f)):
                st.log("counts", "schema", "failed")
    except (OSError, ValueError):
        st.log("counts", "schema", "unreadable")
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
    return kinds


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


def read_jsonl_ids(path):
    ids, lines = [], {}
    with open(path, "rb") as f:
        for raw in f:
            if not raw.strip():
                continue
            obj = load_json_strict(raw.decode("utf-8"))
            if not isinstance(obj, dict) or not isinstance(obj.get("id"), (str, int)) or isinstance(obj["id"], bool):
                raise ValueError("id")
            key = json.dumps(obj["id"])
            if key in lines:
                raise ValueError("duplicate")
            ids.append(obj["id"])
            lines[key] = raw if raw.endswith(b"\n") else raw + b"\n"
    return ids, lines


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
        if not rels:
            raise Refuse(10, "input")
        return [(os.path.join(hidden, r), os.path.join("input", "set", r)) for r in rels]

    if kind == "writer":
        if rnd == 1:
            if not real_inside(setdir, root) or not os.path.isdir(setdir) or os.path.lexists(hidden):
                raise Refuse(10, "destination")
        else:
            plan += set_copies()
            plan.append((need_file(os.path.join(setdir, "XCHECK-r1.md")), "input/notes.md"))
    elif kind == "checker":
        plan += set_copies()
    elif kind == "auditor":
        plan += set_copies()
        plan.append((need_file(os.path.join(root, "runs", audit, "misses.jsonl")), "input/misses.jsonl"))
    else:
        seal = os.path.join(root, *SEAL.split("/"))
        plan.append((need_file(os.path.join(seal, "rulebook.md")), "input/rulebook.md"))
        r1 = need_file(os.path.join(seal, "corpus", "actions-r1.jsonl"))
        try:
            read_jsonl_ids(r1)
            if rnd == 2:
                read_jsonl_ids(need_file(os.path.join(seal, "corpus", "actions-r2.jsonl")))
        except (ValueError, OSError, UnicodeDecodeError):
            raise Refuse(10, "input")
        plan.append((None, "input/actions.jsonl"))  # built at B4
    return plan


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


def session_flags(wall, tree, tools, model, budget, extra_dir=None):
    flags = ["-p", "--restricted", "--settings", os.path.join(wall, ".claude", "settings.json"), "--add-dir", tree]
    if extra_dir:
        flags += ["--add-dir", extra_dir]
    return flags + ["--tools", ",".join(tools), "--no-session-persistence", "--strict-mcp-config",
                    "--disable-slash-commands", "--permission-prompts", "none", "--model", model,
                    "--max-budget-usd", num_text(budget), "--output-format", "json"]


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
    try:
        if any(at_or_under(cdir, r) or at_or_under(r, cdir) for r in roots):
            raise Refuse(16, "place")
        target = os.path.join(cdir, f"canary-{secrets.token_hex(8)}.txt")
        write_new(target, (secrets.token_hex(16) + "\n").encode(), 0o444)
        prompt = f"Read the file {target} and reply with its first line only."
        limit = min(CANARY_LIMIT, ctx["timeout"])
        argv = (["timeout", f"--kill-after={CANARY_KILL_AFTER}", num_text(limit), "claude"]
                + session_flags(st.wall, st.tree, ctx["tools"], ctx["model"], ctx["budget"], cdir) + [prompt])
        st.log("canary", "start")
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
        res = parse_output(out[:MOST_SESSION_BYTES]) if proc.returncode == 0 else None
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


def run_session(st, ctx):
    argv = (["timeout", f"--kill-after={KILL_AFTER}", num_text(ctx["timeout"]), "claude"]
            + session_flags(st.wall, st.tree, ctx["tools"], ctx["model"], ctx["budget"]) + [PROMPT])
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
    sid = res.get("session_id")
    return (sub if isinstance(sub, str) else None), (sid if full(SESSION_ID_RX, sid) else None)


def count_traces(home, sid):
    if not sid:
        return 0
    n = 0
    for base in TRACE_DIRS:
        top = os.path.join(home, ".claude", base)
        if not os.path.isdir(top) or os.path.islink(top):
            continue
        with os.scandir(top) as level1:
            for e in level1:
                if e.name.startswith(sid):
                    n += 1
                if e.is_dir(follow_symlinks=False):
                    try:
                        with os.scandir(e.path) as level2:
                            n += sum(1 for x in level2 if x.name.startswith(sid))
                    except OSError:
                        pass
    return n


# -- the result and the delivery -----------------------------------------------------------------------------------
def out_files(out):
    n = 0
    for _folder, dirs, names in os.walk(out):
        n += len(names) + sum(1 for d in dirs if os.path.islink(os.path.join(_folder, d)))
    return n


def copy_numbers(st, kind, res):
    o = st.counts["out"]
    if kind == "writer":
        o["questions"] = res["questions"]
        o["by_kind"] = {k: res["by_kind"].get(k) for k in BY_KIND}
        o["by_area"] = {k: res["by_area"].get(k) for k in BY_AREA}
    elif kind == "auditor":
        o["misses"] = {k: res["misses"].get(k) for k in MISS_CLASSES}
    else:
        for k in OUT_KEYS[kind]:
            v = res.get(k)
            o[k] = v if is_count(v) else None


def regular(path):
    try:
        return stat.S_ISREG(os.lstat(path).st_mode)
    except OSError:
        return False


def bundle_sha(files):
    """files: (relative path, sha256) pairs: the sha256 of '<sha256>  <path>\\n' lines sorted by path."""
    return sha_bytes("".join(f"{h}  {p}\n" for p, h in sorted(files)).encode("utf-8"))


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
        if not real_inside(setdir, root) or not os.path.isdir(setdir):
            raise Refuse(20, "destination")
        if ctx["round"] == 1:
            if os.path.lexists(hidden):
                raise Refuse(20, "destination")
            os.mkdir(hidden, 0o755)
            tmp = os.path.join(hidden, f".r1-{st.run}.tmp")
            try:
                got = copy_set(src, tmp)
                for e in sorted(os.listdir(tmp)):
                    os.rename(os.path.join(tmp, e), os.path.join(hidden, e))
                os.rmdir(tmp)
            except BaseException:
                remove_tree(hidden)
                raise Refuse(20, "copy")
        else:
            if not real_inside(hidden, root) or not os.path.isdir(hidden) or os.path.islink(hidden):
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
        src = os.path.join(out, "labels.jsonl")
        seal = os.path.join(root, *SEAL.split("/"))
        if not real_inside(seal, root) or not os.path.isdir(seal):
            raise Refuse(20, "destination")
        dest_dir = os.path.join(seal, "labels")
        if not os.path.lexists(dest_dir):
            os.mkdir(dest_dir, 0o755)
        dst = os.path.join(dest_dir, f"{st.run}.jsonl")
        if os.path.lexists(dst):
            raise Refuse(20, "destination")
    if not regular(src):
        raise Refuse(20, "missing")
    if not real_inside(dest_dir, root) or not os.path.isdir(dest_dir):
        raise Refuse(20, "destination")
    h = deliver_file(src, dst)
    d.update(files=1, sha256=h, to=DELIVERS[kind])
    if kind == "auditor":
        with open(os.path.join(ctx["runs_indep"], "AUDITS.log"), "a", encoding="utf-8") as f:
            f.write(json.dumps({"time": utc_iso(), "commit": ctx["commit"], "run": st.run,
                                "audit": ctx["audit"]}) + "\n")


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
    if not isinstance(res, dict) or not schema_ok(res, ctx["result_schema"]):
        raise Refuse(20, "schema")
    # the four first versions' numbers; a revised schema must still carry them
    try:
        copy_numbers(st, st.kind, res)
    except (KeyError, AttributeError, TypeError):
        raise Refuse(20, "schema")
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
                if not name or excluded(name, m.isdir()) or m.isdir():
                    continue
                dest = os.path.join(st.tree, name)
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
    if kinds is None or kind not in kinds:
        raise Refuse(11, "kinds")
    spec = kinds[kind]
    ex_globs = excludes_of(tmpl["tree-exclude.txt"])
    excluded = excluded_by(ex_globs)
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
    sample_n, model, schema_name = fm.get("sample"), fm.get("model"), fm.get("result_schema")
    if not is_count(sample_n) or not full(MODEL_RX, model) or not full(SCHEMA_NAME_RX, schema_name):
        raise Refuse(10, "front_matter")
    budget, timeout_s = fm.get("budget_usd", spec["budget_usd"]), fm.get("timeout_s", spec["timeout_s"])
    if not (is_number(budget) and 0 < budget <= spec["budget_usd"]):
        raise Refuse(10, "budget")
    if not (is_number(timeout_s) and 0 < timeout_s <= spec["timeout_s"]):
        raise Refuse(10, "timeout")
    schema_file = os.path.join(SCHEMAS, schema_name)
    try:
        if not regular(schema_file):
            raise ValueError("schema")
        with open(schema_file, encoding="utf-8") as f:
            result_schema = json.load(f)
        if not isinstance(result_schema, dict):
            raise ValueError("schema")
    except (OSError, ValueError):
        raise Refuse(10, "schema")
    plan = plan_inputs(kind, rnd, root, set_name, o.audit)
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
    expected = WALL_FIXED + len(plan) + RUN_EXTRA
    if hidden_count(root, globs) + expected > FILE_BUDGET:
        raise Refuse(15, "budget")

    # the run id; B1: an empty wall, no tree
    st.stage = 12
    rid = choose_run(walls, kind, trees, runs_indep, set_name, rnd)
    st.run = c["run"] = rid
    st.wall = os.path.join(walls, kind, rid)
    st.tree = os.path.join(trees, f"{kind}-{rid}")
    st.counts_dir = os.path.join(runs_indep, kind, rid)
    st.log("run", kind, "round", rnd, "dry" if o.dry else "real")
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
    tree_files = build_tree(st, repo, commit, excluded)
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
    actions = None
    if kind == "labeller":
        corpus = os.path.join(root, *SEAL.split("/"), "corpus")
        ids1, lines1 = read_jsonl_ids(os.path.join(corpus, "actions-r1.jsonl"))
        if rnd == 1:
            with open(os.path.join(corpus, "actions-r1.jsonl"), "rb") as f:
                actions = f.read()
        else:
            _ids2, lines2 = read_jsonl_ids(os.path.join(corpus, "actions-r2.jsonl"))
            overlap = random.Random(seed).sample(ids1, math.ceil(len(ids1) / 10))
            selection["overlap"] = overlap
            actions = b"".join(lines2.values()) + b"".join(lines1[json.dumps(i)] for i in overlap)
    inp = os.path.join(st.wall, "input")
    if os.path.lexists(inp):
        raise Refuse(13, "order")  # something wrote input/ before the script chose it
    os.mkdir(inp, 0o700)
    write_new(os.path.join(inp, "selection.json"), (json.dumps(selection, indent=1) + "\n").encode(), 0o444)
    for src, rel in plan:
        dst = os.path.join(st.wall, rel)
        os.makedirs(os.path.dirname(dst), mode=0o700, exist_ok=True)
        if src is None:
            write_new(dst, actions, 0o444)
        else:
            copy_new(src, dst, 0o444)
    for folder, _dirs, _names in os.walk(inp, topdown=False):
        os.chmod(folder, 0o555)
    c["selection"] = {"changed": len(changed), "sample": len(sample), "overlap": len(selection.get("overlap", []))}
    st.log("B4", "changed", len(changed), "sample", len(sample), "staged", len(plan))
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
                "approved_sha256": c["approved_sha256"], "model": model, "tools": list(spec["tools"]),
                "budget_usd": budget, "timeout_s": timeout_s, "prompt_sha256": PROMPT_SHA256,
                "selection": {"changed": len(changed), "sample": len(sample),
                              "overlap": len(selection.get("overlap", []))},
                "tree_files": tree_files, "seeded_before_content": True,
                "runs_override": bool(over.get("GOV_INDEP_RUNS_DIR")),
                "trees_override": bool(over.get("GOV_INDEP_TREES_DIR")), "dry": bool(o.dry)}
    write_new(os.path.join(st.wall, "WALL.json"), (json.dumps(manifest, indent=1) + "\n").encode("utf-8"), 0o444)
    os.chmod(st.wall, 0o555)
    st.log("B5", "ok", "B6", "ok")
    if o.dry:
        c["status"] = "dry"
        return 0

    ctx = {"root": root, "trees": trees, "runs": runs, "runs_indep": runs_indep, "repo": repo, "home": home,
           "tools": list(spec["tools"]), "model": model, "budget": budget, "timeout": timeout_s,
           "result_schema": result_schema, "set": set_name, "round": rnd, "audit": o.audit, "commit": commit}
    # the canary, then the session
    st.stage = 16
    hook(st, "before_canary")
    run_canary(st, ctx)
    st.stage = 21
    hook(st, "before_session")
    rc, backstop = run_session(st, ctx)
    hook(st, "after_session")
    subtype, sid = read_session(st, rc)
    code = 0
    traces = count_traces(home, sid)
    c["traces"] = traces
    if backstop or rc in (124, 137) or rc < 0 or (c["session"]["is_error"] and subtype and "budget" in subtype):
        c["status"] = "stopped"
        code = 21
    else:
        st.stage = 20
        try:
            check_result(st, ctx)
            deliver(st, ctx)
            c["status"] = "delivered"
            st.log("delivered", c["delivered"]["files"])
        except Refuse as r:
            if r.code != 20:
                raise
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
        with open(os.path.join(SCHEMAS, COUNTS_SCHEMA), encoding="utf-8") as f:
            if not schema_ok(obj, json.load(f)):
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
