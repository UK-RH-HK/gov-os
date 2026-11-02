"""The local merge queue (DEC-959 item 1, DEC-979 item 3, DEC-968, DEC-953 item 4): the CTO's tool, the one writer of
w2/integrate. A ticket enters only by its approval file; the queue merges every approved ticket (--no-ff, in approval
order) onto the integration head in a clean clone, runs the scoped set once on that merged result (or skips it when
the code is what the lead tested, saying why), and moves the branch by fast-forward only, to exactly the commit it
tested. On red the branch stays; the ticket that caused the red is ejected, the rest go on. It never pushes.

    python3 merge_queue.py enqueue --queue <dir> --ticket <W2> --task <id> --branch <branch> --commit <commit>
    python3 merge_queue.py approve --queue <dir> --ticket <W2> --by <who>
    python3 merge_queue.py run --repo <repo> --queue <dir> [--integration <branch>] [--work <dir>] [--test-cmd <cmd>]
                               [--select-cmd <cmd>] [--prepare-cmd <cmd>] [--rounds <n>]
                               [--integration-store <link> [--nightly-log <dir> --nightly-junit <dir>]]

With --integration-store (DEC-1032 (iv)): clones without a store are seeded from it, the landed result's stores are
promoted into it, and the head without the batch is read from that head's nightly or re-run in it, never rebuilt.

Exit codes of run: 0 every approved entry landed (or none); 3 at least one ejected; 4 a step could not be done, or
another run holds the queue's lock (entries kept, the branch unmoved by that step). See README.md beside this file.
Standard library only; the red attribution and the culprit search are close_build.py's reviewed functions.
"""
import argparse
import fcntl
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

ORCH_TOOLS = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools")
WORK = Path.home() / "gov-os-runs/W2-00/merge-queue"
REBUILD_LOCK = "/tmp/gov-os-rebuild.lock"
REBUILD_SLOT = ORCH_TOOLS / "rebuild_slot.sh"  # DEC-1001 (d): a rebuild in a heavy-job slot, a lock of its own tree
# DEC-1032 (iv): a clone with no store is seeded from the integration store before its rebuild; the landed result's
# stores become the integration store's; the head without the batch is never rebuilt. MERGE_QUEUE_SEEDER and
# MERGE_QUEUE_REFRESH name stand-ins (tests only).
SEEDER = Path(os.environ.get("MERGE_QUEUE_SEEDER") or ORCH_TOOLS / "seed_store.py")
REFRESH = Path(os.environ.get("MERGE_QUEUE_REFRESH") or ORCH_TOOLS / "refresh_integration_store.sh")
STORE_REL = ".gov-runtime/store.db"
QUERY_REL = ".gov-runtime/query-vector-cache.db"
HEAD_TREE = "head-"  # the throwaway worktrees of the head without the batch: <work>/head-<id>-<n>
SLOT = ORCH_TOOLS / "verify_lock.sh"  # a heavy-job slot (DEC-979 D1, DEC-983): waits for one, exits with the run's code
NODE = "/home/usain/.nvm/versions/node/v22.23.3/bin"
MAP_REL = "governance/project/test-map.yaml"
GOVERNANCE = [  # select_tests.py's governance paths, left out of the skip's comparison (DEC-953 item 4a)
    "governance/project/briefs/**",
    "governance/project/prompts/**",
    "governance/project/orchestration/**",
    ".gov-runtime/**",
]
HEAD_TRIES = 3  # re-merges onto a moved head before the run stops (entries kept)
RESULT_REF = "refs/heads/merge-queue-result"  # in the clone only: how the repository fetches the tested commit


# ---- close_build.py's reviewed functions (2026-10-31), copied; their cases are in the unit tests -------------------

def decisive(w_fail, wo_fail, rounds, absent):
    """Whether the traced rounds so far settle the case (no more rounds needed)."""
    return absent is not None or (w_fail == rounds and wo_fail == 0) or bool(wo_fail and w_fail <= wo_fail)


def attribute(w_fail, wo_fail, rounds, absent):
    """DEC-968's verdict on one traced red: "flaky" (green with the change in every round), "owned" (the change's:
    it cannot run without the change, or is green without it in every round, or is red with it in at least half the
    rounds more than without it) or "unowned" (not the change's; investigated at once)."""
    if absent is not None:
        return "owned"
    if w_fail == 0:
        return "flaky"
    return "owned" if wo_fail == 0 or 2 * (w_fail - wo_fail) >= rounds else "unowned"


def trace_node(with_rc, without_rc, rounds=3):
    """Trace one red: with_rc() and without_rc() each run the case alone once and return its exit code, interleaved,
    `rounds` rounds and as many more unless decisive. Without the change only exit 1 is red; any other non-zero exit
    there (the case cannot run without the change, e.g. a test the change added) ends the trace as the change's."""
    w_fail = wo_fail = done = 0
    absent = None
    for batch in (rounds, rounds):
        for _ in range(batch):
            w_fail += with_rc() != 0
            rc = without_rc()
            if rc not in (0, 1):
                absent = rc
                break
            wo_fail += rc == 1
            done += 1
        if decisive(w_fail, wo_fail, done, absent):
            break
    return attribute(w_fail, wo_fail, done, absent), {"rounds": done, "red_with": w_fail,
                                                      "red_without": wo_fail, "without_exit": absent}


def explained_without(run_once, rounds=3):
    """One candidate's verdict on a red the batch caused, with that ticket taken out: "yes" when green (0) in every
    round; "no" on a red (1) or any other exit in a round: blame needs proof (DEC-979 item 3)."""
    for _ in range(rounds):
        if run_once() != 0:
            return "no"
    return "yes"


def red_alone(run_once, rounds=3):
    """Whether a case fails (exit 1, a real failure) in every round: the proof that a ticket alone causes it."""
    return all(run_once() == 1 for _ in range(rounds))


def assign_culprits(reds, candidates, prepare, explains, confirm):
    """DEC-979 item 3. Every candidate is tried: prepare(candidate) builds the result without it (False when it
    cannot); explains(red) answers "yes", "no" or "absent" (the case cannot run without it: the ticket added it).
    "absent" is blamed only if confirm(red, candidate) proves the red with that ticket alone. Returns
    ({red: [candidates]}, [unexplained reds], [skipped candidates]); the caller fails closed on either of the last."""
    culprit, absent, skipped = {red: [] for red in reds}, [], []
    for cand in candidates:
        if not prepare(cand):
            skipped.append(cand)
            continue
        for red in reds:
            v = explains(red)
            if v == "yes":
                culprit[red].append(cand)
            elif v == "absent":
                absent.append((red, cand))
    for red, cand in absent:
        if confirm(red, cand):
            culprit[red].append(cand)
    unexplained = [r for r in reds if not culprit[r]]
    return {r: c for r, c in culprit.items() if c}, unexplained, skipped


def own_commits(git_fn, base, commit, task):
    """Whether every non-merge commit the approved commit brings onto `base` carries `Task: <task>` (merge_is_own's
    rule on base..commit): else taking the ticket out would not take out only its own work."""
    commits = git_fn("rev-list", "--no-merges", f"{base}..{commit}").split()
    if not commits:
        return False
    return all(task in git_fn("log", "-1", "--format=%(trailers:key=Task,valueonly)", c).split() for c in commits)


# ---- paths, JUnit -------------------------------------------------------------------------------------------------

def match(path, pattern):
    """allowed_paths' grammar (gov.guard.decide._match_pattern)."""
    segs = [re.escape(p).replace(r"\*", "[^/]*") for p in pattern.split("**")]
    return bool(re.match("^" + ".*".join(segs) + (".*" if pattern.endswith("**") else "") + "$", path))


WARM_KEEP = ("store.db", "codeintel", "query-vector-cache.db", "secrets-clean.json")  # the rebuild's own stores
MARK = "queue-fresh.json"  # in .git/: the fingerprint of a fresh clone's config and exclude file


def fingerprint(clone):
    """What a warm clone must still match from when it was made: its .git/config and .git/info/exclude."""
    out = {}
    for rel in ("config", "info/exclude"):
        f = Path(clone) / ".git" / rel
        out[rel] = f.read_text(encoding="utf-8", errors="replace") if f.is_file() else None
    return out


def write_mark(clone):
    (Path(clone) / ".git" / MARK).write_text(json.dumps(fingerprint(clone)), encoding="utf-8")


def read_mark(clone):
    try:
        return json.loads((Path(clone) / ".git" / MARK).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None  # a clone without the mark is never reused


def scrub(clone):
    """A warm clone made as clean as a fresh one, but for the rebuild's stores (review of 2026-11-01): every git hook a
    run installed removed, and everything under .gov-runtime but the stores (store.db*, codeintel/,
    query-vector-cache.db*, secrets-clean.json) removed. False when anything cannot be removed."""
    try:
        hooks = Path(clone) / ".git" / "hooks"
        for h in (hooks.iterdir() if hooks.is_dir() else []):
            if not h.name.endswith(".sample"):
                shutil.rmtree(h) if h.is_dir() and not h.is_symlink() else h.unlink()
        rt = Path(clone) / ".gov-runtime"
        for item in (rt.iterdir() if rt.is_dir() else []):
            if any(item.name == k or item.name.startswith(k + "-") or item.name.startswith(k + ".") for k in WARM_KEEP) \
                    and (item.name != "codeintel" or item.is_dir()):
                continue
            shutil.rmtree(item) if item.is_dir() and not item.is_symlink() else item.unlink()
        return True
    except OSError:
        return False


def map_list(root, key):
    """A top-level list of the test map (block or flow form), read without YAML; none when it cannot be read."""
    try:
        lines = (Path(root) / MAP_REL).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    found, inside = [], False
    for line in lines:
        flow = re.match(r"^" + re.escape(key) + r":\s*\[(.*)\]\s*$", line)
        if flow:
            return [x.strip().strip("'\"") for x in flow.group(1).split(",") if x.strip()]
        if re.match(r"^" + re.escape(key) + r":\s*$", line):
            inside = True
        elif inside:
            item = re.match(r"^\s+-\s+(.+?)\s*$", line)
            if item:
                found.append(item.group(1).strip("'\""))
            elif line.strip() and not line.lstrip().startswith("#"):
                break
    return found


def record_places(root):
    """The test map's record_only list (block or flow form), read without YAML; none when it cannot be read."""
    return map_list(root, "record_only")


RECORD_SUFFIXES = (".md", ".txt", ".patch", ".log", ".jsonl")  # an allowlist (review of 2026-11-01): nothing else


def record_only_change(names, places):
    """DEC-1001 (a): whether every changed path is a record: one of the test map's record_only places, or a governance
    path (briefs, prompts, the orchestration record, .gov-runtime) ending in a record suffix (.md, .txt, .patch, .log,
    .jsonl). Any other file (scripts, configuration, .conf, .yaml, no suffix) is not, and an empty change is not one."""
    if not names:
        return False
    for n in names:
        if any(match(n, p) for p in places):
            continue
        if any(match(n, p) for p in GOVERNANCE) and n.endswith(RECORD_SUFFIXES):
            continue
        return False
    return True


def failing_cases(xml_paths, where, targets):
    """The failing cases (path::name, their failure kinds) of JUnit files, paths relative to `where`."""
    return [(node, kinds) for node, kinds, failed in junit_cases(xml_paths, where, targets) if failed]


def passing_cases(xml_paths, where, targets):
    """The cases that ran and passed (no failure, error or skip) in JUnit files, paths relative to `where`."""
    return [node for node, _, failed in junit_cases(xml_paths, where, targets, skipped=False) if not failed]


def junit_cases(xml_paths, where, targets, skipped=True):
    """Every case of JUnit files as (path::name, failure kinds, failed), paths relative to `where` (skipped cases
    left out when `skipped` is false). pytest names a case by its path
    relative to its rootdir, which without an ini file is the targets' common folder: each folder from there up to
    `where` is tried for the file the dotted classname names."""
    where = Path(where)
    tops = [where / t.split("::")[0] for t in targets if (where / t.split("::")[0]).exists()]
    base = Path(os.path.commonpath(tops)) if tops else where
    base = base.parent if base.is_file() else base
    bases = [base] + [p for p in base.parents if p == where or where in p.parents]
    bases += [] if where in bases else [where]

    def locate(parts, name):  # a rootdir above `where` (an ini file further up) puts its own folders first: skipped
        for k in range(len(parts), 0, -1):
            for j in range(k):
                for b in bases:
                    f = b.joinpath(*parts[j:k]).with_suffix(".py")
                    if f.is_file():
                        return "::".join([str(f.relative_to(where)), *parts[k:], *([name] if name else [])])
        return "::".join(["/".join(parts) + ".py", *([name] if name else [])])

    out = []
    for p in xml_paths:
        for case in ET.parse(p).iter("testcase"):
            failed = case.find("failure") is not None or case.find("error") is not None
            if not failed and not skipped and case.find("skipped") is not None:
                continue
            if case.get("file"):
                node = f"{case.get('file')}::{case.get('name')}"
            elif case.get("classname"):
                node = locate(case.get("classname").split("."), case.get("name"))
            else:  # a collection error: pytest names the module (dotted) in `name`
                node = locate(case.get("name", "").split("."), None)
            out.append((node, case_kinds(case) if failed else set(), failed))
    return out


def failing(xml_paths, where, targets):
    """The failing test ids (path::name) of JUnit files, paths relative to `where` (failing_cases' nodes, once each)."""
    return list(dict.fromkeys(node for node, _ in failing_cases(xml_paths, where, targets)))


def case_kinds(case):
    """One JUnit testcase's failure kinds (the exception types its failure or error names, a bare `assert` counted as
    AssertionError), as a set."""
    found = set()
    for el in [case.find("failure"), case.find("error")]:
        if el is None:
            continue
        msg = el.get("message") or ""
        inner = re.search(r'failed on \w+ with "(.*)', msg, re.S)
        msg = inner.group(1) if inner else msg
        if re.match(r"\s*assert\b", msg):  # pytest gives a bare assert's message without its type
            found.add("AssertionError")
            continue
        m = re.match(r"\s*([A-Za-z_][\w.]*)\s*(:|$)", msg)
        found.add(m.group(1) if m else el.tag)
    return found


def failure_kinds(xml_paths):
    """The exception types the JUnit files name for their failing cases (`<failure message="Type: ...">`, or an
    error's `failed on setup with "Type: ..."`), as a sorted list: close_build.py's same-failure rule (DEC-989: a red
    is cleared only if the baseline has it red with the same failure)."""
    found = set()
    for p in xml_paths:
        try:
            cases = list(ET.parse(p).iter("testcase"))
        except (OSError, ET.ParseError):
            continue
        for case in cases:
            found |= case_kinds(case)
    return sorted(found)


def same_failure(a, b):
    """Two failure lists match only when both are known: an empty list (a timeout, no JUnit file) never matches."""
    return bool(a) and bool(b) and a == b


def totals(xml_paths):
    t = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    for p in xml_paths:
        r = ET.parse(p).getroot()
        for s in ([r] if r.tag == "testsuite" else r.iter("testsuite")):
            for k in t:
                t[k] += int(s.get(k, 0))
    return t


def copy_store_file(source, target):
    """One store file copied: an SQLite file through its backup (a consistent state while it may be read), any other
    file as bytes; the target replaced whole."""
    import sqlite3
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(target.name + ".copy")
    with open(source, "rb") as f:
        is_sqlite = f.read(16) == b"SQLite format 3\0"
    if is_sqlite:
        reading = sqlite3.connect(Path(source).resolve().as_uri() + "?mode=ro", uri=True, timeout=60.0)
        try:
            writing = sqlite3.connect(tmp, timeout=60.0)
            try:
                reading.backup(writing)
            finally:
                writing.close()
        finally:
            reading.close()
    else:
        shutil.copyfile(source, tmp)
    os.replace(tmp, target)


def snapshot(tree):
    """A tree's state for the re-runs: HEAD, its tracked and untracked changes, its ignored entries (caches left out)
    and the stamps of every file under .gov-runtime. Any difference: the tree is not used again."""
    def git_out(*a):
        return subprocess.run(["git", "-C", str(tree), *a], capture_output=True, text=True).stdout
    ignored = sorted(x for x in git_out("status", "--porcelain", "--ignored", "-uall").splitlines()
                     if not re.search(r"(__pycache__/|\.pyc$|\.pytest_cache/|^!! \.gov-runtime/)", x))
    stamps = []
    rt = Path(tree) / ".gov-runtime"
    for p in sorted(rt.rglob("*")) if rt.is_dir() else []:
        rel = str(p.relative_to(tree))
        # left out: SQLite's shared-memory index and an empty write-ahead log (a reader makes them), the query-vector
        # cache (a search writes it; it changes no answer) and the code-graph tool's logs
        if rel.endswith("-shm") or (rel.endswith("-wal") and p.is_file() and p.stat().st_size == 0) \
                or QUERY_REL in rel or "/codeintel/home/logs" in "/" + rel:
            continue
        try:
            st = p.lstat()
            stamps.append((str(p.relative_to(tree)), st.st_size, st.st_mtime_ns))
        except OSError:
            stamps.append((str(p), None, None))
    return git_out("rev-parse", "HEAD").strip(), tuple(ignored), tuple(stamps)


# ---- the queue folder ---------------------------------------------------------------------------------------------

class Stop(Exception):
    """A step that cannot be done: nothing advances, nothing is ejected for it, run exits 4."""


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def valid_name(ticket):
    return bool(ticket) and "/" not in ticket and not ticket.startswith(".")


def enqueue(a):
    if not valid_name(a.ticket):
        sys.exit(f"merge queue: not a ticket name: {a.ticket!r}")
    r = sh(["git", "-C", a.repo, "rev-parse", "--verify", "-q", a.commit + "^{commit}"])
    commit = r.stdout.strip() if r.returncode == 0 else a.commit if re.fullmatch(r"[0-9a-f]{40}", a.commit) else None
    if not commit:
        sys.exit(f"merge queue: {a.commit} does not name a commit in {a.repo} (give --repo, or the full id)")
    write_json(Path(a.queue) / "requested" / f"{a.ticket}.json",
               {"ticket": a.ticket, "task": a.task, "branch": a.branch, "commit": commit, "requested_at": now()})
    return 0


def approve(a):
    req = Path(a.queue) / "requested" / f"{a.ticket}.json"
    if not valid_name(a.ticket) or not req.is_file():
        sys.exit(f"merge queue: no request for {a.ticket} in {a.queue}; nothing approved")
    data = json.loads(req.read_text(encoding="utf-8"))
    data.update(approved_by=a.by, approved_at=datetime.now().isoformat(timespec="microseconds"))
    write_json(Path(a.queue) / "approved" / f"{a.ticket}.json", data)
    req.unlink()
    return 0


# ---- run ----------------------------------------------------------------------------------------------------------

class Queue:
    def __init__(self, a, queue):
        self.a, self.q = a, queue
        self.repo = Path(a.repo).resolve()
        self.ref = f"refs/heads/{a.integration}"
        self.rounds = a.rounds
        self.ejected, self.handled, self.n, self.with_rc = [], set(), 0, {}
        self.log = self.work = self.clone = self.alt = self.base = self._base_record = None
        # DEC-1032 (iv): the integration store (a link to the ready one of two worktrees of this repository): the seed
        # of every clone without a store, the tree the head without the batch is re-run in, and where a landed
        # result's stores go. None: the earlier way (no seed, the alt clone rebuilt at the head, no promotion).
        store = getattr(a, "integration_store", None)
        self.store = Path(store).expanduser() if store else None
        self.built = {}  # tree -> the commit its stores were last rebuilt at, successfully, in this run
        self._head_record = {}  # head -> the nightly's record of exactly that head (or None)
        self.head_trees, self.head_trees_made = {}, []  # head -> (throwaway worktree, its state when made)
        name = sh(["git", "-C", str(self.repo), "config", "user.name"]).stdout.strip()
        email = sh(["git", "-C", str(self.repo), "config", "user.email"]).stdout.strip()
        self.ident = ["-c", f"user.name={name or 'orchestrator'}", "-c", f"user.email={email or 'orchestrator@localhost'}"]

    # -- plumbing
    def note(self, msg):
        line = time.strftime("%F %T ") + msg
        print(line, flush=True)
        with open(self.log / "queue.txt", "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def git(self, where, *args):
        r = sh(["git", *self.ident, "-C", str(where), *args])
        if r.returncode:
            raise Stop(f"git {' '.join(args[:3])} in {where} failed: {r.stderr.strip()[:300]}")
        return r.stdout.strip()

    def head(self):
        r = sh(["git", "-C", str(self.repo), "rev-parse", "--verify", "-q", self.ref])
        if r.returncode:
            raise Stop(f"{self.ref} cannot be read in {self.repo}")
        return r.stdout.strip()

    def env(self, where):
        env = {k: v for k, v in os.environ.items() if k not in ("PYTEST_ADDOPTS", "PYTEST_PLUGINS")}
        env["PYTHONPATH"] = f"{where}/src"  # the checkout's own code (DEC-732)
        return env

    def approved(self):
        entries = []
        for p in sorted((self.q / "approved").glob("*.json")):
            try:
                e = json.loads(p.read_text(encoding="utf-8"))
                assert all(isinstance(e.get(k), str) and e[k] for k in ("ticket", "task", "branch", "commit"))
            except (OSError, ValueError, AssertionError):
                raise Stop(f"{p} cannot be read as an approval (ticket, task, branch, commit)")
            if e["ticket"] != p.stem:
                raise Stop(f"{p} names ticket {e['ticket']}, not {p.stem}")
            full = sh(["git", "-C", str(self.repo), "rev-parse", "--verify", "-q", e["commit"] + "^{commit}"])
            if re.fullmatch(r"[0-9a-f]{7,40}", e["commit"]) and full.returncode == 0:  # an id enqueued outside the
                e["commit"] = full.stdout.strip()  # repository (never a branch name): its full id from here on
            entries.append(e)
        return sorted(entries, key=lambda e: (str(e.get("approved_at", "")), e["ticket"]))

    # -- the queue folder's outcomes
    def eject(self, e, reason, tests, head):
        self.ejected.append({"ticket": e["ticket"], "reason": reason, "failing": tests})
        write_json(self.q / "ejected" / f"{e['ticket']}.json",
                   dict(e, reason=reason, failing=tests, log=str(self.log), tested_on=head, ejected_at=now()))
        (self.q / "approved" / f"{e['ticket']}.json").unlink(missing_ok=True)
        self.note(f"EJECTED {e['ticket']}: {reason}" + (f"; failing: {', '.join(tests)}" if tests else ""))

    def eject_all(self, entries, tests, reason, head):
        for e in entries:
            self.eject(e, reason, tests, head)
        return []

    # -- the trees
    def fresh(self, name):
        """A clean clone to work in. With --warm (DEC-1001 (b)), the clone of that name kept from earlier runs, its
        stores kept so the rebuild is incremental, once it proves healthy (its origin is this repository, a fetch, a
        forced checkout and a clean all work); a clone that does not is set aside in this run's work folder (removed
        with it) and a fresh one made in its place."""
        if not self.a.warm:
            path = self.work / name
            if not path.exists() and sh(["git", "clone", "-q", "--no-hardlinks", str(self.repo), str(path)]).returncode:
                raise Stop(f"the clean clone of {self.repo} failed")
            return path
        warm = Path(self.a.warm).expanduser().resolve()
        warm.mkdir(parents=True, exist_ok=True)
        path = warm / name
        if path.exists():
            url = sh(["git", "-C", str(path), "remote", "get-url", "origin"]).stdout.strip()
            healthy = (url and Path(url).resolve() == self.repo and fingerprint(path) == read_mark(path)
                       and not sh(["git", "-C", str(path), "fetch", "-q", "origin"]).returncode
                       and not sh(["git", "-C", str(path), "checkout", "-q", "--force", "--detach", "HEAD"]).returncode
                       and not sh(["git", "-C", str(path), "clean", "-ffdxq", "-e", ".gov-runtime"]).returncode
                       and scrub(path))
            if healthy:
                self.note(f"warm clone {name} reused ({path}); its stores kept, the rest of .gov-runtime cleared")
                return path
            aside = self.work / f"broken-{name}"
            try:
                path.rename(aside)
                self.note(f"warm clone {name} could not be reset; set aside, a fresh one made")
            except OSError:
                path = warm / f"{name}-{self.work.name}"
                self.note(f"warm clone {name} could not be reset or set aside; a fresh one at {path}")
        if sh(["git", "clone", "-q", "--no-hardlinks", str(self.repo), str(path)]).returncode:
            raise Stop(f"the clean clone of {self.repo} failed")
        write_mark(path)
        return path

    def build(self, where, head, entries):
        """head + each entry's approved commit merged --no-ff in turn. Returns ([(entry, merge)], [(entry, why)])."""
        if any(sh(["git", "-C", str(where), "cat-file", "-e", c + "^{commit}"]).returncode
               for c in [head] + [e["commit"] for e in entries]):  # a head or an approval newer than the clone
            self.git(where, "fetch", "-q", "origin")
        self.git(where, "checkout", "-q", "--force", "--detach", head)
        self.git(where, "clean", "-fdxq", "-e", ".gov-runtime")
        merged, failed = [], []
        for e in entries:
            c = e["commit"]
            if sh(["git", "-C", str(where), "cat-file", "-e", c + "^{commit}"]).returncode:
                failed.append((e, "missing: the approved commit is not in the repository"))
                continue
            if not sh(["git", "-C", str(where), "merge-base", "--is-ancestor", c, "HEAD"]).returncode:
                failed.append((e, "already merged: the approved commit is on the integration head"))
                continue
            r = sh(["git", *self.ident, "-C", str(where), "merge", "-q", "--no-ff", "--no-edit",
                    "-m", f"Merge {e['branch']} ({e['task']}): merge queue",
                    "-m", f"Task: {e['task']}\nRole: orchestrator", c])
            if r.returncode:
                conflicted = self.git(where, "diff", "--name-only", "--diff-filter=U")
                sh(["git", "-C", str(where), "merge", "--abort"])
                if not conflicted:
                    raise Stop(f"git merge of {c[:12]} failed without a conflict: {r.stderr.strip()[:300]}")
                failed.append((e, "conflict"))
                continue
            merged.append((e, self.git(where, "rev-parse", "HEAD")))
        return merged, failed

    def seed(self, where, base, *more):
        """DEC-1032 (iv): `where` seeded from `base` by the seeder (seed_store.py) before its rebuild; the extra rebuild
        arguments it answers (the product's `--seed <base>`), none when it seeded by copy, or did not seed. Fail
        closed: a seed refused or a seeder that cannot answer leaves the normal rebuild, named."""
        if not SEEDER.is_file():
            self.note(f"no seeder at {SEEDER}: {where.name} rebuilds without a seed")
            return []
        r = sh([sys.executable, str(SEEDER), "seed", str(where), "--base", str(base), "--json",
                "--who", f"queue {where.name}", *more])
        try:
            ans = json.loads(r.stdout.strip().splitlines()[-1])
            assert isinstance(ans, dict) and isinstance(ans.get("rebuild_args", []), list)
        except (IndexError, ValueError, AssertionError):
            self.note(f"seed of {where.name} not applied (the seeder answered exit {r.returncode}: "
                      f"{(r.stderr or r.stdout).strip()[-200:]}): a normal rebuild")
            return []
        what = ans.get("reason") or (f"{ans.get('kept')}, {ans.get('vectors')} vectors" if ans.get("status") == "seeded"
                                     else " ".join(ans.get("rebuild_args") or []))
        self.note(f"seed of {where.name} from {base}: {ans.get('status')} ({ans.get('mode')}): {what}"
                  + ("" if ans.get("status") in ("seeded", "deferred") else "; a normal rebuild"))
        return [str(x) for x in ans.get("rebuild_args") or []]

    def prepared(self, where, extra=None, seed=True):
        """The rebuild of `where` (the prepare command), after its seed when it has no store (DEC-1032 (iv)). Records
        the commit it was built at, for the promotion."""
        extra = list(extra or [])
        if seed and self.store and not (where / STORE_REL).exists():
            extra += self.seed(where, self.store)
        cmd = shlex.split(self.a.prepare_cmd) if self.a.prepare_cmd else \
            (["env", f"GOV_REBUILD_PYTHON={sys.executable}", "bash", str(REBUILD_SLOT), str(where)] if REBUILD_SLOT.is_file()
             else ["flock", REBUILD_LOCK, sys.executable, "-m", "gov.cli.main", "rebuild", "--json"])
        t0 = time.time()
        r = sh(cmd + extra, cwd=where, env=self.env(where))
        (self.log / f"prepare-{where.name}.txt").write_text(r.stdout[-4000:] + r.stderr[-4000:], encoding="utf-8")
        at = sh(["git", "-C", str(where), "rev-parse", "HEAD"]).stdout.strip()
        with open(self.log / "prepares.jsonl", "a", encoding="utf-8") as f:  # one line per rebuild (rebuild_counts.py)
            f.write(json.dumps({"tree": where.name, "at": at, "rc": r.returncode, "seconds": round(time.time() - t0, 1),
                                "args": extra, "finished": now()}) + "\n")
        if r.returncode == 0 and at:
            self.built[str(where)] = at
        else:
            self.built.pop(str(where), None)
        return r.returncode == 0

    # -- the tests
    def tests(self, where, tag, args):
        """One run: (exit, [JUnit files]); exit 0 green, 1 red, anything else did not complete."""
        self.n += 1
        junit = (self.log if tag == "run" else self.work) / f"{tag}-{self.n}.xml"
        if self.a.test_cmd:
            try:
                r = sh(shlex.split(self.a.test_cmd) + [f"--junitxml={junit}", *args], cwd=where,
                       env=self.env(where), timeout=None if tag == "run" else 1800)
            except subprocess.TimeoutExpired:
                return 1, []  # an alone re-run that hangs counts as red (close_build.py)
            if tag == "run":
                (self.log / f"run-{self.n}.txt").write_text(r.stdout[-20000:] + r.stderr[-5000:], encoding="utf-8")
            return r.returncode, [junit]
        return self.default_tests(where, junit, tag, args)

    def default_tests(self, where, junit, tag, args):
        """The close's form (close_build.py): one parallel run, then the selected serial-only cases."""
        env = dict(self.env(where), PYTHONPATH=f"{where}/src:{where}/src/gov/close/pytest_plugin",
                   GOV_CLOSE_SERIAL_ONLY_OF=str(where), PATH=NODE + ":" + os.environ.get("PATH", ""))
        common = ["-q", "-p", "no:cacheprovider", "--no-header", "-o", "tmp_path_retention_policy=failed"]
        if tag != "run":
            try:
                return sh([sys.executable, "-m", "pytest", *common, f"--junitxml={junit}", *args], cwd=where, env=env,
                          timeout=1800).returncode, [junit]
            except subprocess.TimeoutExpired:
                return 1, []
        common += ["-p", "gov_close_serial_only", "-rs"]
        par = sh(["bash", str(SLOT), sys.executable, "-m", "pytest", *args, "-n", "auto", *common, f"--junitxml={junit}"],
                 cwd=where, env=env)
        (self.log / f"run-{self.n}.txt").write_text(par.stdout[-20000:] + par.stderr[-5000:], encoding="utf-8")
        listing = sh([sys.executable, "-c", "import json, sys; from pathlib import Path; from gov.close.pytest_plugin."
                      "gov_close_serial_only import entries; from gov.close.serial import phase; r = Path(sys.argv[1]); "
                      "print(json.dumps(phase(r, entries(r))))", str(where)], cwd=where, env=env)
        if listing.returncode:
            return 2, [junit]
        targets = [t.rstrip("/") for t in args if not t.startswith("-")]
        serial = [e for e in json.loads(listing.stdout)
                  if any(e == t or e.startswith(t + "/") or e.startswith(t + "::") for t in targets)]
        if not serial:
            return par.returncode, [junit]
        sjunit = junit.with_name(junit.stem + "-serial.xml")
        ser = sh(["bash", str(SLOT), sys.executable, "-m", "pytest", *serial, *common, f"--junitxml={sjunit}"], cwd=where,
                 env=dict(env, GOV_CLOSE_SERIAL_ONLY_GIVEN="\n".join(serial)))
        if par.returncode not in (0, 1) or ser.returncode not in (0, 1, 5):
            return 2, [junit, sjunit]
        return int(1 in (par.returncode, ser.returncode)), [junit] + ([sjunit] if ser.returncode != 5 else [])

    def alone(self, where, node):
        return self.tests(where, "alone", [node])[0]

    def select(self, where, e, merge):
        cmd = shlex.split(self.a.select_cmd) if self.a.select_cmd else [sys.executable, str(ORCH_TOOLS / "select_tests.py")]
        r = sh(cmd + [str(where), e["ticket"], e["task"], "--merge", merge], cwd=where, env=self.env(where))
        (self.log / f"select-{e['ticket']}.json").write_text(r.stdout + r.stderr[-4000:], encoding="utf-8")
        try:
            sel = json.loads(r.stdout) if r.returncode == 0 else None
        except ValueError:
            sel = None
        if not isinstance(sel, dict):
            raise Stop(f"the selection for {e['ticket']} cannot be made (exit {r.returncode})")
        if sel.get("scope") != "scoped":  # DEC-968, DEC-983: only a scoped selection runs here
            raise Stop(f"the selection for {e['ticket']} answered scope {sel.get('scope')!r}, not 'scoped'"
                       + ("; the full suite runs only in the nightly" if sel.get("scope") == "full" else ""))
        if not isinstance(sel.get("selected"), list):
            raise Stop(f"the selection for {e['ticket']} names no list of targets")
        return sel

    # -- the steps
    def skip_reason(self, result, merged):
        """KPI 3: the reason to skip, when the merged code is what a lead tested (governance paths left out)."""
        places = GOVERNANCE + record_places(self.clone)
        for e, _ in merged:
            names = self.git(self.clone, "-c", "core.quotePath=false", "diff", "-z", "--no-renames", "--name-only",
                             e["commit"], result).split("\0")
            names = [n for n in names if n]
            if all(any(match(n, p) for p in places) for n in names):
                return (f"the merged code is identical to {e['commit']}, {e['ticket']}'s approved commit, which its "
                        f"lead tested; governance paths left out of the comparison: {', '.join(names) or 'none differ'}"
                        f" (patterns: {', '.join(places)})")
        return None

    def run_tests(self, head, merged):
        """KPI 3: prepare, select, one run on the union; each red re-run alone, then traced without the batch."""
        if not self.prepared(self.clone):
            raise Stop("the prepare command failed on the merged result")
        sels = [self.select(self.clone, e, m) for e, m in merged]
        targets = list(dict.fromkeys(x["target"] for s in sels for x in s["selected"]))
        if not targets:
            raise Stop("the selection named no tests")
        opts = list(sels[0].get("pytest_options") or []) if len(merged) == 1 else []
        rc, junits = self.tests(self.clone, "run", opts + targets)
        try:
            if rc not in (0, 1) or not junits:
                raise ValueError
            counts, reds = totals(junits), failing(junits, self.clone, targets)
        except (OSError, ValueError, ET.ParseError):
            raise Stop(f"the test run did not complete (exit {rc}; JUnit files {[str(j) for j in junits]})")
        if rc == 1 and not reds:
            raise Stop("the test run was red with no failing test named in its JUnit file")
        out = {"kinds": {n: sorted(k) for n, k in failing_cases(junits, self.clone, targets)} if rc == 1 else {},
               "selection": {"targets": targets, "core_changed": sorted({p for s in sels for p in s.get("core_changed") or []}),
                             "unplaced": sorted({p for s in sels for p in s.get("unplaced") or []})},
               "counts": counts, "flaky": [], "unowned": [], "owned": [], "with_rc": {}}
        for node in reds:
            out["with_rc"][node] = rc1 = self.alone(self.clone, node)
            if rc1 == 0:
                out["flaky"].append(node)
                self.note(f"flaky candidate (passes alone, decides nothing): {node}")
        reds = [n for n in reds if out["with_rc"][n] != 0]
        out["trace_base"] = self.base or head
        where = f"the baseline {self.base[:12]}" if self.base else "the head without the batch"
        need = []
        for node in reds:
            # DEC-1001 (c): the baseline nightly's own record clears a red without a baseline build when it holds the
            # case red alone with the same failure; else (no record, not red alone there, another failure) the trace.
            known = self.base_known(node)
            if known is not None and same_failure(self.kinds(self.clone, node), known):
                out["unowned"].append(node)
                out.setdefault("cleared_by_results", []).append(node)
                self.note(f"red alone, red alone at {where} in its nightly's record with the same failure "
                          f"({sorted(known)}): unowned (no baseline build): {node}")
            else:
                need.append(node)
        reds = need
        if reds:
            # DEC-988, DEC-989: with --base, a red is traced against a known state (the last nightly with a verdict,
            # its reds known), never against code made by undoing merges; without it, the head without the batch,
            # which is never rebuilt where the integration store is given (DEC-1032 (iv), head_tree).
            if self.base:
                self.alt = self.fresh("alt")
                self.build(self.alt, self.base, [])
                if not self.prepared(self.alt):
                    raise Stop(f"the prepare command failed on {where}")
            for node in reds:
                other = self.alt if self.base else self.head_tree(head)  # a throwaway tree, checked before each case
                verdict, c = trace_node(lambda: self.alone(self.clone, node), lambda: self.alone(other, node),
                                        self.rounds)
                if self.base and verdict == "unowned":  # cleared only if it fails there the same way (DEC-989)
                    kw, kb = self.kinds(self.clone, node), self.kinds(other, node)
                    if not same_failure(kw, kb):
                        verdict = "owned"
                        self.note(f"red at {where} too but not the same failure ({kw} here, {kb} there): {node}")
                out[verdict].append(node)
                self.note(f"red alone, traced against {where} ({c}): {verdict}: {node}")
        if self.base and (out["owned"] or out["unowned"]):
            # The head without the batch decides the rest (code that exists; nothing is undone). A red the
            # baseline had stays cleared only if that head has it too, the same way: else the batch broke again
            # what a later merge had fixed (review of 2026-11-01). A red the baseline did not clear that the head
            # has too, the same way, came from a merge already on the branch since the baseline: nothing
            # advances and nobody is ejected; the CTO investigates at once (DEC-968, DEC-989). Fail closed.
            # DEC-1032 (iv): that head is never rebuilt: the nightly's record of exactly that head answers first (a
            # case green there is not on the head; a case red alone there with the same failure is, for a red that
            # would stop the queue, never for one it would clear), else the case is re-run alone, as before, in a
            # throwaway worktree of that head holding the integration store's stores (head_tree): never in the
            # integration store's own tree.
            def on_head(n, clearing):
                known = self.head_known(head, n)
                if known == "passed":
                    self.note(f"green on the head without the batch in that head's own nightly (no run): {n}")
                    return False
                if known is not None and not clearing and same_failure(known, self.kinds(self.clone, n)):
                    self.note(f"red alone on the head without the batch in that head's own nightly, the same "
                              f"failure ({known}; no run): {n}")
                    return True
                tree = self.head_tree(head)
                return red_alone(lambda: self.alone(tree, n), self.rounds) and \
                    same_failure(self.kinds(tree, n), self.kinds(self.clone, n))
            for n in list(out["unowned"]):
                if not on_head(n, clearing=True):
                    out["unowned"].remove(n)
                    out["owned"].append(n)
                    self.note(f"red at the baseline but not, the same way, on the head without the batch: the "
                              f"batch's: {n}")
            since = [n for n in out["owned"] if on_head(n, clearing=False)]
            if since:
                rest = [n for n in out["owned"] if n not in since]
                raise Stop(f"red since the baseline {self.base[:12]}, already on {head[:12]} without the batch "
                           f"(not this batch's; investigate at once, DEC-968, DEC-989): {', '.join(since)}"
                           + (f"; also red, the batch's: {', '.join(rest)}" if rest else ""))
        return out

    def base_known(self, node):
        """DEC-1001 (c): the failure kinds the baseline nightly's own record gives this case when that nightly had it
        red alone (its run file's `red-alone <case>:` line) and its JUnit names the failure; None when either is
        missing, unreadable, or the case is not there (the trace then runs, fail closed)."""
        if not (self.base and getattr(self.a, "base_results", None) and getattr(self.a, "base_run", None)):
            return None
        if self._base_record is None:
            self._base_record = {}
            try:
                text = Path(self.a.base_run).read_text(encoding="utf-8")
                if not re.search(r"^head " + re.escape(self.base[:12]) + r"\b", text, re.M):
                    self.note(f"the nightly's run file is not for the baseline {self.base[:12]}; the trace runs")
                    return None
                alone = {m.group(1) for m in re.finditer(r"^red-alone (.+?): \d+ \w+", text, re.M)}  # ids may hold spaces
                xmls = sorted(Path(self.a.base_results).glob("*.xml"))
                if alone and xmls:
                    for n, k in failing_cases(xmls, self.clone, ["tests"]):
                        if n in alone and k:
                            self._base_record.setdefault(n, set()).update(k)
            except (OSError, UnicodeDecodeError, ET.ParseError) as exc:
                self.note(f"the baseline nightly's record cannot be read ({exc.__class__.__name__}); the trace runs")
                self._base_record = {}
        k = self._base_record.get(node)
        return sorted(k) if k else None

    def kinds(self, where, node):
        """The failure's exception types for one case run alone (the same-failure rule)."""
        _, junits = self.tests(where, "alone", [node])
        return failure_kinds(junits)

    # -- DEC-1032 (iv): the integration store: the head without the batch, never rebuilt; the landed result promoted
    def store_lock(self):
        return self.store.with_name(self.store.name + ".lock")  # refresh_integration_store.sh takes the same

    def head_tree(self, head):
        """A tree at `head` (the head without the batch) with its stores, never rebuilt and never the integration
        store's own tree (review of 2026-11-02, A1, A2): a throwaway detached worktree of `head`, made in this run's
        work folder, holding a copy of the integration store's stores built at that head (the whole store, the same
        commit: nothing to embed) and its code index made anew (no embedding). It is checked before every use against
        its state when made (HEAD, no tracked or untracked change, the same ignored files, its stores' stamps); a
        case that changed anything gets a new one. Removed when the run ends (remove_head_trees); one a killed run
        left is removed at the next run's start (sweep_head_trees). When the integration store is not at `head`: its
        normal refresh first, and a Stop if it still is not. Without --integration-store, the earlier way: the alt
        clone checked out and rebuilt at the head (once per head while it stays there)."""
        if self.store is None:
            if self.alt and self.built.get(str(self.alt)) == head and \
                    sh(["git", "-C", str(self.alt), "rev-parse", "HEAD"]).stdout.strip() == head:
                return self.alt
            self.alt = self.alt or self.fresh("alt")
            self.build(self.alt, head, [])
            if not self.prepared(self.alt):
                raise Stop("the prepare command failed on the head without the batch")
            return self.alt
        have = self.head_trees.get(head)
        if have:
            if snapshot(have[0]) == have[1]:
                return have[0]
            self.note(f"a re-run changed the throwaway tree {have[0].name}: a new one is made")
            self.remove_head_tree(have[0])
            del self.head_trees[head]
        tree = self.work / f"{HEAD_TREE}{head[:12]}-{len(self.head_trees_made)}"
        self.head_trees_made.append(tree)
        r = sh(["git", "-C", str(self.repo), "worktree", "add", "-q", "--detach", str(tree), head])
        if r.returncode:
            raise Stop(f"the throwaway worktree of the head {head[:12]} cannot be added: {r.stderr.strip()[:200]}")
        copied = self.copy_head_stores(head, tree)
        index = sh([sys.executable, "-c", "import sys; from gov.codeintel import index; index(sys.argv[1])", str(tree)],
                   cwd=tree, env=self.env(tree))
        self.note(f"the head without the batch: a throwaway worktree {tree.name} at {head[:12]} with the integration "
                  f"store's stores ({', '.join(copied)}; no rebuild, nothing embedded); its code index "
                  + ("made anew" if index.returncode == 0 else f"not made ({(index.stderr.strip().splitlines() or ['?'])[-1][:120]})"))
        self.head_trees[head] = (tree, snapshot(tree))
        return tree

    def copy_head_stores(self, head, tree):
        """The integration store's stores, built at `head`, copied into `tree` under a shared hold of the store's lock
        (a refresh or a promotion takes it whole, so the ready half cannot move while it is copied); only read there.
        A store behind the head is refreshed first (its standby half, incrementally), then a Stop if it still is not.
        Returns the files copied."""
        for attempt in (0, 1):
            ready = self.store.resolve()
            with open(self.store_lock(), "a") as hold:
                fcntl.flock(hold, fcntl.LOCK_SH)
                ready = self.store.resolve()
                at = sh(["git", "-C", str(ready), "rev-parse", "HEAD"]).stdout.strip()
                if at == head and (ready / STORE_REL).is_file():
                    copied = []
                    for rel in (STORE_REL, QUERY_REL):
                        if (ready / rel).is_file():
                            copy_store_file(ready / rel, tree / rel)
                            copied.append(rel)
                    return copied
            if attempt == 0:
                self.note(f"the integration store {ready} is at {at[:12] or 'an unreadable head'}, not at the head "
                          f"{head[:12]}: its normal refresh first (its standby half, incrementally; no clone rebuilt)")
                if not self.refresh(wait=True):
                    break
        raise Stop(f"the head without the batch cannot be judged without rebuilding a clone: the integration store "
                   f"{self.store} is not at {head[:12]} and its refresh did not bring it there")

    def remove_head_tree(self, tree):
        """One throwaway worktree of this queue's own removed (git worktree remove --force); never another path."""
        if not tree.name.startswith(HEAD_TREE):
            return
        sh(["git", "-C", str(self.repo), "worktree", "remove", "--force", str(tree)])
        shutil.rmtree(tree, ignore_errors=True)

    def remove_head_trees(self):
        for tree in self.head_trees_made:
            self.remove_head_tree(tree)
        sh(["git", "-C", str(self.repo), "worktree", "prune"])

    def sweep_head_trees(self, root):
        """The throwaway worktrees a killed run left (their path: <work root>/<stamp>/head-..., registered in this
        repository) removed before this run makes any; nothing else is touched."""
        root, cur = Path(root).resolve(), None
        for line in sh(["git", "-C", str(self.repo), "worktree", "list", "--porcelain"]).stdout.splitlines():
            if not line.startswith("worktree "):
                continue
            path = Path(line[len("worktree "):])
            if path.parent.parent == root and path.name.startswith(HEAD_TREE) and path.parent != self.work:
                self.note(f"a throwaway worktree a killed run left removed: {path}")
                self.remove_head_tree(path)
        sh(["git", "-C", str(self.repo), "worktree", "prune"])

    def head_known(self, head, node):
        """What the nightly of exactly `head` (its run file's `head <id>` line; its JUnit folder beside the others;
        a verdict line, so its reds were re-run alone) says of a case: "passed" (it ran and passed in its suites),
        the failure kinds (red alone there, its JUnit naming the failure), or None (no such nightly, a record that
        cannot be read, or the case is in neither: the case is then re-run on the head)."""
        nlog, njunit = getattr(self.a, "nightly_log", None), getattr(self.a, "nightly_junit", None)
        if not (nlog and njunit):
            return None
        if head not in self._head_record:
            rec = None
            for run in sorted(Path(nlog).glob("*/run.txt"), reverse=True):
                try:
                    text = run.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue
                if not re.search(r"^head " + re.escape(head[:12]) + r"\b", text, re.M):
                    continue
                xmls = sorted((Path(njunit) / run.parent.name).glob("*.xml"))
                if xmls and re.search(r"^verdict:", text, re.M):
                    try:
                        alone = {m.group(1) for m in re.finditer(r"^red-alone (.+?): ", text, re.M)}
                        cases = junit_cases(xmls, self.clone, ["tests"], skipped=False)
                        failed = {n for n, _, bad in cases if bad}
                        red = {}
                        for n, k, bad in cases:
                            if bad and n in alone and k:
                                red.setdefault(n, set()).update(k)
                        rec = {"red": red, "passed": {n for n, _, bad in cases if not bad} - failed}
                        self.note(f"the head without the batch has its own nightly: {run.parent.name}")
                    except (OSError, ET.ParseError) as exc:
                        self.note(f"the nightly of {head[:12]} cannot be read ({exc.__class__.__name__}): re-run")
                break
            self._head_record[head] = rec
        rec = self._head_record[head]
        if rec is None:
            return None
        if node in rec["red"]:
            return sorted(rec["red"][node])
        return "passed" if node in rec["passed"] else None

    def refresh(self, wait):
        """The integration store's normal refresh (refresh_integration_store.sh: its standby half rebuilt at the head
        of the integration branch, incrementally, the link moved on success; it takes the store's lock itself). With
        `wait`, run now: whether it succeeded. Else started apart, its output in this run's log: True."""
        if not REFRESH.is_file():
            self.note(f"no refresh tool at {REFRESH}: the integration store is not refreshed")
            return False
        env = dict(os.environ, GOV_STORE_LINK=str(self.store), GOV_STORE_REPO=str(self.repo),
                   GOV_STORE_REF=self.a.integration)
        out = open(self.log / "refresh.txt", "a", encoding="utf-8")
        try:
            if wait:
                return subprocess.run(["bash", str(REFRESH)], env=env, stdout=out, stderr=subprocess.STDOUT,
                                      stdin=subprocess.DEVNULL).returncode == 0
            subprocess.Popen(["bash", str(REFRESH)], env=env, stdout=out, stderr=subprocess.STDOUT,
                             stdin=subprocess.DEVNULL, start_new_session=True)
            return True
        finally:
            out.close()

    def promote(self, result):
        """After a landing, the merged clone's stores, rebuilt at exactly the landed commit, become the integration
        store's instead of building it again: its standby half checked out at that commit, seeded from the clone
        (the whole store: the same commit), its rebuild (nothing is left to embed; the code index is made anew, as it
        holds its tree's absolute path), then the link moved, as refresh_integration_store.sh moves it. Where the
        clone's stores are not at that commit (a skipped run, a rebuild elsewhere, the branch moved on), the store's
        lock is held, or a step fails: the normal refresh, started apart, named."""
        if self.store is None:
            return
        why = None
        if self.built.get(str(self.clone)) != result:
            why = (f"the merged clone's stores were not rebuilt at the landed commit {result[:12]} (the run was "
                   f"skipped, or its last rebuild was at {str(self.built.get(str(self.clone)))[:12]})")
        elif sh(["git", "-C", str(self.clone), "rev-parse", "HEAD"]).stdout.strip() != result:
            why = "the merged clone is no longer at the landed commit"
        elif self.head() != result:
            why = f"{self.ref} moved on past the landed commit {result[:12]}"
        if why is None:
            lock = open(self.store_lock(), "a")
            try:
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except OSError:
                    why = "a refresh holds the integration store's lock"
                else:
                    why = self._promote(result)
            finally:
                lock.close()
        if why:
            self.note(f"integration store not promoted: {why}; its normal refresh runs apart")
            self.refresh(wait=False)

    def _promote(self, result):
        """The promotion's steps, under the store's lock; None when done, else why not (the link unmoved)."""
        cur = self.store.resolve()
        standby = self.store.with_name(self.store.name + ("-b" if cur.name.endswith("-a") else "-a"))
        if standby.resolve() == cur or not (standby / ".git").exists():
            return f"no standby half at {standby}"
        if sh(["git", "-C", str(standby), "checkout", "-q", "--force", "--detach", result]).returncode:
            return f"the standby half {standby.name} cannot be checked out at {result[:12]}"
        extra = self.seed(standby, self.clone, "--replace")
        if not self.prepared(standby, extra, seed=False) or self.built.get(str(standby)) != result:
            return f"the rebuild of the standby half {standby.name} at {result[:12]} failed"
        tmp = self.store.with_name(self.store.name + ".tmp")
        tmp.unlink(missing_ok=True)
        os.symlink(standby, tmp)
        os.replace(tmp, self.store)
        self.note(f"integration store promoted: the merged clone's stores at {result[:12]} into {standby.name}; "
                  f"the link moved (its own rebuild of the landing's change not needed)")
        return None

    def culprits(self, head, merged, owned):
        """DEC-979 item 3: eject only the tickets that caused the reds; the rest are returned for a new run."""
        entries = [e for e, _ in merged]
        for e in entries:
            if not own_commits(lambda *a: self.git(self.clone, *a), head, e["commit"], e["task"]):
                return self.eject_all(entries, owned, f"red: {e['ticket']}'s approved commit brings commits without "
                                      f"its Task: {e['task']} trailer (another ticket's work); not bisectable (fail "
                                      "closed)", head)
        files = {e["ticket"]: set(self.git(self.clone, "diff", "--name-only", m + "^1", m).split()) for e, m in merged}
        cur = {}
        self.alt = self.alt or self.fresh("alt")  # the head without the batch may have been judged without it

        def prepare(cand):
            cur["c"] = cand
            built, failed = self.build(self.alt, head, [e for e in entries if e is not cand])
            return not failed and self.prepared(self.alt)

        def explains(node):
            first = [self.alone(self.alt, node)]
            if first[0] not in (0, 1):
                return "absent" if self.with_rc.get(node) == 1 else "no"
            v = explained_without(lambda: first.pop() if first else self.alone(self.alt, node), self.rounds)
            return "absent" if v == "yes" and node.split("::")[0] in files[cur["c"]["ticket"]] else v

        def confirm(node, cand):
            built, failed = self.build(self.alt, head, [cand])
            return not failed and self.prepared(self.alt) and red_alone(lambda: self.alone(self.alt, node), self.rounds)

        culprit, unexplained, skipped = assign_culprits(owned, entries, prepare, explains, confirm)
        if skipped:
            return self.eject_all(entries, owned, "red: the batch cannot be bisected: without "
                                  f"{', '.join(c['ticket'] for c in skipped)} the merge or the prepare command failed "
                                  "(fail closed)", head)
        if unexplained:
            return self.eject_all(entries, owned, f"red: no single ticket explains {', '.join(unexplained)} "
                                  "(fail closed)", head)
        back = {}
        for node, cands in culprit.items():
            for c in cands:
                back.setdefault(c["ticket"], []).append(node)
        for e in entries:
            if e["ticket"] in back:
                self.eject(e, "red", back[e["ticket"]], head)
        return [e for e in entries if e["ticket"] not in back]

    def advance(self, head, result):
        """KPI 1: the branch moves by fast-forward only, to exactly the tested commit; any failure leaves it."""
        self.git(self.clone, "update-ref", RESULT_REF, result)
        self.git(self.repo, "fetch", "-q", "--no-tags", "--no-write-fetch-head", str(self.clone), RESULT_REF)
        wt, cur = None, None
        for line in sh(["git", "-C", str(self.repo), "worktree", "list", "--porcelain"]).stdout.splitlines() + [""]:
            if line.startswith("worktree "):
                cur = line[len("worktree "):]
            elif line == f"branch {self.ref}":
                wt = cur
        if wt:
            if self.git(wt, "rev-parse", "HEAD") != head:
                raise Stop(f"the worktree {wt} holding {self.ref} is not at the tested head")
            self.git(wt, "merge", "-q", "--ff-only", result)
        else:
            self.git(self.repo, "update-ref", "-m", "merge queue: fast-forward to the tested merge", self.ref, result, head)
        if self.head() != result:
            raise Stop(f"{self.ref} did not end on the tested commit {result[:12]}")

    def batch(self, pending, started):
        moves = 0
        while pending:
            head = self.head()
            merged, failed = self.build(self.clone, head, pending)
            for e, why in failed:
                self.eject(e, why, [], head)
            if not merged:
                return
            result = merged[-1][1]
            self.note(f"merged {', '.join(e['ticket'] for e, _ in merged)} onto {head[:12]}: {result[:12]}")
            skipped, out = self.skip_reason(result, merged), None
            if skipped:
                self.note("run skipped: " + skipped)
            else:
                out = self.run_tests(head, merged)
                self.with_rc = out["with_rc"]
                if out["owned"]:  # KPI 2: the branch stays; KPI 4: only the cause goes back, the rest get a new run
                    if len(merged) == 1:
                        self.eject(merged[0][0], "red", out["owned"], head)
                        return
                    pending = self.culprits(head, merged, out["owned"])
                    continue
            light = None
            while self.head() != head:  # KPI 6: never advanced onto a head it was not tested on
                moves += 1
                if moves >= HEAD_TRIES:
                    raise Stop(f"{self.ref} moved during each of {HEAD_TRIES} attempts")
                new = self.head()
                step = self.light_rerun(head, new, merged, out) if out is not None else None
                if step is None:
                    self.note(f"{self.ref} moved while under test; merged again onto the new head ({moves})")
                    break
                light = dict({k: v for k, v in step.items() if k != "merged"}, previous=light)
                head, merged, result = new, step["merged"], step["result"]
            else:
                self.advance(head, result)
                self._landed(head, result, merged, skipped, out, light, started)
                self.promote(result)  # DEC-1032 (iv): the landed result's stores become the integration store's
                return
            pending = [e for e, _ in merged]
            continue

    def light_rerun(self, old, new, merged, out):
        """DEC-1001 (a): the head moved while under test. When it moved only by records (record_only_change), the same
        approved commits are merged onto the new head and only the record-reading tests (the test map's
        record_reading and every_close lists) run again on the result; the rest of the selection stands. Returns the
        new merges and result, or None for a full re-run (a code change, a merge that differs, no list, a prepare that
        fails, a run that does not complete, or a red that is not one this batch's run already cleared)."""
        names = [n for n in sh(["git", "-C", str(self.repo), "-c", "core.quotePath=false", "diff", "-z",
                                "--no-renames", "--name-only", old, new]).stdout.split("\0") if n]
        if not record_only_change(names, record_places(self.clone)):
            return None
        entries = [e for e, _ in merged]
        merged2, failed = self.build(self.clone, new, entries)
        if failed or len(merged2) != len(entries):
            return None
        result = merged2[-1][1]
        targets = list(dict.fromkeys(map_list(self.clone, "record_reading") + map_list(self.clone, "every_close")))
        targets = [t for t in targets if (self.clone / t.split("::")[0]).exists()]
        if not targets:
            self.note("the head moved by records only, but the record-reading tests cannot be named: a full re-run")
            return None
        if not self.prepared(self.clone):
            return None
        rc, junits = self.tests(self.clone, "run", targets)
        try:
            if rc not in (0, 1) or not junits:
                raise ValueError
            cases = failing_cases(junits, self.clone, targets) if rc == 1 else []
            reds = list(dict.fromkeys(n for n, _ in cases))
            counts = totals(junits)
        except (OSError, ValueError, ET.ParseError):
            return None
        known = out.get("kinds") or {}
        cleared = set(out.get("unowned") or [])
        if rc == 1 and (not reds or any(n not in cleared or not same_failure(sorted(k), known.get(n) or [])
                                        for n, k in cases)):
            self.note(f"the record-reading re-run is red ({', '.join(reds) or 'unnamed'}): a full re-run")
            return None
        self.note(f"{self.ref} moved by records only ({len(names)} path(s)); merged again onto {new[:12]}: "
                  f"{result[:12]}; the record-reading tests re-run: {counts}")
        return {"merged": merged2, "result": result, "from": old, "to": new, "paths": names, "targets": targets,
                "counts": counts, "reds": reds}

    def _landed(self, head, result, merged, skipped, out, light, started):
        """The record of an advance and the landed entries (KPI 1)."""
        rec = self.q / "records" / f"{result[:12]}.json"
        write_json(rec, {"head": result, "base": head, "skipped": skipped,
                         "tickets": [{"ticket": e["ticket"], "task": e["task"], "commit": e["commit"], "merge": m}
                                     for e, m in merged],
                         "selection": out["selection"] if out else {"targets": [], "core_changed": [], "unplaced": []},
                         "counts": out["counts"] if out else None, "flaky": out["flaky"] if out else [],
                         "unowned": out["unowned"] if out else [], "ejected": list(self.ejected),
                         "trace_base": out["trace_base"] if out else None,
                         "record_rerun": light, "cleared_by_results": (out or {}).get("cleared_by_results", []),
                         "log": str(self.log), "started": started, "finished": now()})
        for e, m in merged:
            write_json(self.q / "landed" / f"{e['ticket']}.json", dict(e, merge=m, record=str(rec), landed_at=now()))
            (self.q / "approved" / f"{e['ticket']}.json").unlink(missing_ok=True)
        self.note(f"ADVANCED {self.ref} {head[:12]} -> {result[:12]}; record {rec}")

    def run(self):
        started = now()
        if getattr(self.a, "base", None):
            r = sh(["git", "-C", str(self.repo), "rev-parse", "--verify", "-q", self.a.base + "^{commit}"])
            if r.returncode:
                raise Stop(f"the baseline {self.a.base} is not a commit in {self.repo}")
            self.base = r.stdout.strip()
        while True:
            pending = [e for e in self.approved() if e["ticket"] not in self.handled]
            if not pending:
                return 3 if self.ejected else 0
            if self.log is None:
                stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
                self.log = self.q / "log" / stamp
                self.log.mkdir(parents=True)
                self.work = Path(self.a.work or WORK).resolve() / stamp
                self.work.mkdir(parents=True)
                if self.store is not None:
                    self.sweep_head_trees(self.work.parent)
                self.clone = self.fresh("merged")
            self.handled.update(e["ticket"] for e in pending)
            self.batch(pending, started)


def run(a):
    os.environ["GOV_HEAVY_PRIORITY"] = "1"  # DEC-1011: a landing takes the next free heavy-job slot before any lead's step
    queue = Path(a.queue).resolve()
    queue.mkdir(parents=True, exist_ok=True)
    lock = open(queue / "run.lock", "a")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("merge queue: another run holds the queue's lock; nothing done", file=sys.stderr)
        return 4
    q = Queue(a, queue)
    if getattr(a, "warm", None):  # one run at a time uses the warm clones, whichever queue folder it serves
        Path(a.warm).expanduser().mkdir(parents=True, exist_ok=True)
        warm_lock = open(Path(a.warm).expanduser() / "warm.lock", "a")
        try:
            fcntl.flock(warm_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            print("merge queue: another run holds the warm clones' lock; nothing done", file=sys.stderr)
            return 4
    try:
        return q.run()
    except Stop as why:
        if q.log:
            q.note(f"STOPPED: {why}; nothing advanced by this step, entries kept")
        print(f"merge queue: stopped: {why}; entries kept", file=sys.stderr)
        return 4
    finally:
        if q.work:
            q.remove_head_trees()  # its own throwaway worktrees, before their folder goes
            shutil.rmtree(q.work, ignore_errors=True)
        lock.close()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("enqueue")
    e.add_argument("--repo", default=".", help="where --commit is resolved (default: the current folder)")
    for k in ("queue", "ticket", "task", "branch", "commit"):
        e.add_argument(f"--{k}", required=True)
    p = sub.add_parser("approve")
    for k in ("queue", "ticket", "by"):
        p.add_argument(f"--{k}", required=True)
    r = sub.add_parser("run")
    r.add_argument("--repo", required=True)
    r.add_argument("--queue", required=True)
    r.add_argument("--integration", default="w2/integrate")
    r.add_argument("--work")
    r.add_argument("--test-cmd")
    r.add_argument("--select-cmd")
    r.add_argument("--prepare-cmd")
    r.add_argument("--rounds", type=int, default=3)
    r.add_argument("--warm", help="keep the work clones here between runs, their stores kept (DEC-1001 (b))")
    r.add_argument("--base-results", help="the baseline nightly's JUnit folder (DEC-1001 (c)); with --base-run")
    r.add_argument("--base-run", help="the baseline nightly's run file, whose `red-alone <case>:` lines it reads")
    r.add_argument("--base", help="the known state reds are traced against: the last nightly with a verdict until a "
                                  "green one after ACT 1, then the last green one (DEC-989); default the head")
    r.add_argument("--integration-store", help="the link to the integration store's ready half (DEC-1032 (iv)): "
                   "the seed of a clone without a store, the tree the head without the batch is re-run in (never "
                   "rebuilt), and where a landed result's stores are promoted")
    r.add_argument("--nightly-log", help="the nightlies' run folders (<stamp>/run.txt): the head without the batch "
                                         "is read from the nightly of exactly that head, where there is one")
    r.add_argument("--nightly-junit", help="the nightlies' JUnit folders (<stamp>/*.xml), with --nightly-log")
    a = ap.parse_args(argv)
    return {"enqueue": enqueue, "approve": approve, "run": run}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
