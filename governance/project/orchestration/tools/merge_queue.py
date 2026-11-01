"""The local merge queue (DEC-959 item 1, DEC-979 item 3, DEC-968, DEC-953 item 4): the CTO's tool, the one writer of
w2/integrate. A ticket enters only by its approval file; the queue merges every approved ticket (--no-ff, in approval
order) onto the integration head in a clean clone, runs the scoped set once on that merged result (or skips it when
the code is what the lead tested, saying why), and moves the branch by fast-forward only, to exactly the commit it
tested. On red the branch stays; the ticket that caused the red is ejected, the rest go on. It never pushes.

    python3 merge_queue.py enqueue --queue <dir> --ticket <W2> --task <id> --branch <branch> --commit <commit>
    python3 merge_queue.py approve --queue <dir> --ticket <W2> --by <who>
    python3 merge_queue.py run --repo <repo> --queue <dir> [--integration <branch>] [--work <dir>] [--test-cmd <cmd>]
                               [--select-cmd <cmd>] [--prepare-cmd <cmd>] [--rounds <n>]

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


def record_places(root):
    """The test map's record_only list (block or flow form), read without YAML; none when it cannot be read."""
    try:
        lines = (Path(root) / MAP_REL).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    found, inside = [], False
    for line in lines:
        flow = re.match(r"^record_only:\s*\[(.*)\]\s*$", line)
        if flow:
            return [x.strip().strip("'\"") for x in flow.group(1).split(",") if x.strip()]
        if re.match(r"^record_only:\s*$", line):
            inside = True
        elif inside:
            item = re.match(r"^\s+-\s+(.+?)\s*$", line)
            if item:
                found.append(item.group(1).strip("'\""))
            elif line.strip() and not line.lstrip().startswith("#"):
                break
    return found


def failing(xml_paths, where, targets):
    """The failing test ids (path::name) of JUnit files, paths relative to `where`. pytest names a case by its path
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
            if case.find("failure") is None and case.find("error") is None:
                continue
            if case.get("file"):
                out.append(f"{case.get('file')}::{case.get('name')}")
            elif case.get("classname"):
                out.append(locate(case.get("classname").split("."), case.get("name")))
            else:  # a collection error: pytest names the module (dotted) in `name`
                out.append(locate(case.get("name", "").split("."), None))
    return list(dict.fromkeys(out))


def totals(xml_paths):
    t = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    for p in xml_paths:
        r = ET.parse(p).getroot()
        for s in ([r] if r.tag == "testsuite" else r.iter("testsuite")):
            for k in t:
                t[k] += int(s.get(k, 0))
    return t


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
        self.log = self.work = self.clone = self.alt = None
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
        path = self.work / name
        if not path.exists() and sh(["git", "clone", "-q", "--no-hardlinks", str(self.repo), str(path)]).returncode:
            raise Stop(f"the clean clone of {self.repo} failed")
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

    def prepared(self, where):
        cmd = shlex.split(self.a.prepare_cmd) if self.a.prepare_cmd else \
            ["flock", REBUILD_LOCK, sys.executable, "-m", "gov.cli.main", "rebuild", "--json"]
        r = sh(cmd, cwd=where, env=self.env(where))
        (self.log / f"prepare-{where.name}.txt").write_text(r.stdout[-4000:] + r.stderr[-4000:], encoding="utf-8")
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
        out = {"selection": {"targets": targets, "core_changed": sorted({p for s in sels for p in s.get("core_changed") or []}),
                             "unplaced": sorted({p for s in sels for p in s.get("unplaced") or []})},
               "counts": counts, "flaky": [], "unowned": [], "owned": [], "with_rc": {}}
        for node in reds:
            out["with_rc"][node] = rc1 = self.alone(self.clone, node)
            if rc1 == 0:
                out["flaky"].append(node)
                self.note(f"flaky candidate (passes alone, decides nothing): {node}")
        reds = [n for n in reds if out["with_rc"][n] != 0]
        if reds:
            self.alt = self.fresh("alt")
            self.build(self.alt, head, [])
            if not self.prepared(self.alt):
                raise Stop("the prepare command failed on the head without the batch")
            for node in reds:
                verdict, c = trace_node(lambda: self.alone(self.clone, node), lambda: self.alone(self.alt, node),
                                        self.rounds)
                out[verdict].append(node)
                self.note(f"red alone, traced without the batch ({c}): {verdict}: {node}")
        return out

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
            if self.head() != head:  # KPI 6: never advanced onto a head it was not tested on
                moves += 1
                self.note(f"{self.ref} moved while under test; merged again onto the new head ({moves})")
                if moves >= HEAD_TRIES:
                    raise Stop(f"{self.ref} moved during each of {HEAD_TRIES} attempts")
                pending = [e for e, _ in merged]
                continue
            self.advance(head, result)
            rec = self.q / "records" / f"{result[:12]}.json"
            write_json(rec, {"head": result, "base": head, "skipped": skipped,
                             "tickets": [{"ticket": e["ticket"], "task": e["task"], "commit": e["commit"], "merge": m}
                                         for e, m in merged],
                             "selection": out["selection"] if out else {"targets": [], "core_changed": [], "unplaced": []},
                             "counts": out["counts"] if out else None, "flaky": out["flaky"] if out else [],
                             "unowned": out["unowned"] if out else [], "ejected": list(self.ejected),
                             "log": str(self.log), "started": started, "finished": now()})
            for e, m in merged:
                write_json(self.q / "landed" / f"{e['ticket']}.json", dict(e, merge=m, record=str(rec), landed_at=now()))
                (self.q / "approved" / f"{e['ticket']}.json").unlink(missing_ok=True)
            self.note(f"ADVANCED {self.ref} {head[:12]} -> {result[:12]}; record {rec}")
            return

    def run(self):
        started = now()
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
                self.clone = self.fresh("merged")
            self.handled.update(e["ticket"] for e in pending)
            self.batch(pending, started)


def run(a):
    queue = Path(a.queue).resolve()
    queue.mkdir(parents=True, exist_ok=True)
    lock = open(queue / "run.lock", "a")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("merge queue: another run holds the queue's lock; nothing done", file=sys.stderr)
        return 4
    q = Queue(a, queue)
    try:
        return q.run()
    except Stop as why:
        if q.log:
            q.note(f"STOPPED: {why}; nothing advanced by this step, entries kept")
        print(f"merge queue: stopped: {why}; entries kept", file=sys.stderr)
        return 4
    finally:
        if q.work:
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
    a = ap.parse_args(argv)
    return {"enqueue": enqueue, "approve": approve, "run": run}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
