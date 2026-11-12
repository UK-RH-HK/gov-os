"""Support code for W2-115's acceptance tests: the smart close (README, "How the suite runs").

- **Public interfaces only:** ``gov close <ticket>``, ``gov close --select <ticket>``, ``gov close --verify <ticket>``
  (W1-07's console-script stand-in, this worktree's ``src/``), the close record ``docs/close/<ticket>/CL-<ticket>.md``,
  the files the close writes, ``python3 -m gov.close.batch`` and ``python3 -m gov.close.nightly``.
- **Planted projects under pytest's tmp_path**, built from a few files (W2-66's form: a stand-in ``gov`` package that
  points at this worktree's code; no copy of this repository).
- **Telling tests:** every planted test appends one JSON line per run to a file of its own outside the project: the
  tree it ran in, what it saw of the watched files, whether it passed.
- Deterministic, no network, no model.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parent
for _name in ("W1-30", "W2-66"):
    _folder = str(_HERE.parent / _name)
    if _folder not in sys.path:
        sys.path.insert(0, _folder)

import w1_30_support as close_support  # noqa: E402

cli_support = close_support.cli_support
REPO_ROOT = close_support.REPO_ROOT
SRC = close_support.SRC

# --------------------------------------------------------------------------
# The interface (README, "Interface")
# --------------------------------------------------------------------------

CLOSE_YAML_REL = "governance/project/close.yaml"
TEMPLATE_CLOSE_YAML_REL = "template/governance/project/close.yaml"
TEST_MAP_REL = "governance/project/test-map.yaml"
PATH_MAP_REL = close_support.PATH_MAP_REL
SERIAL_ONLY_REL = close_support.SERIAL_ONLY_REL
REGISTER_REL = "docs/DECISION_REGISTER.md"
NIGHTLY_DIR_REL = "docs/close/nightly"
CLONE_REL = ".gov-runtime/close/clone"
VERIFY_DIR_REL = ".gov-runtime/close/verify"
RESEARCH_REL = "docs/research/W2-115-smart-close.md"

SCOPED, STRICT = "scoped", "strict"
SELECTION_REFUSED = "SELECTION_REFUSED"
BATCH_UNEXPLAINED = "BATCH_UNEXPLAINED"
CANDIDATE_NOT_ISOLATED = "CANDIDATE_NOT_ISOLATED"
VERDICT_MALFORMED = "VERDICT_MALFORMED"
VERDICT_NOT_REVIEWER = "VERDICT_NOT_REVIEWER"
FINDING_BLOCKS = "FINDING_BLOCKS"
READY = "READY"

RECORD_KEYS = ("close", "commit", "selection", "runs", "review", "reds", "culprits", "clone", "nightly")
RED_KEYS = ("test", "failure_type", "caused", "reason", "repair_ticket")
RUN_COUNT_KEYS = ("passed", "failed", "errors", "skipped")

BATCH_MODULE = "gov.close.batch"
NIGHTLY_MODULE = "gov.close.nightly"
VERIFY_EXIT_GREEN, VERIFY_EXIT_RED, VERIFY_EXIT_REFUSED, VERIFY_EXIT_INCOMPLETE = 0, 1, 2, 3

GOV_TIMEOUT_S = 300

# --------------------------------------------------------------------------
# The planted project
# --------------------------------------------------------------------------

TICKET, WBS = "PROJ-aaaa", "W2-aa"
SECOND, SECOND_WBS = "PROJ-ffff", "W2-ff"

WIDGET = "src/gov/widget/thing.py"      # the ticket's own module
GADGET = "src/gov/gadget/other.py"      # another module, coupled to the shared core in the map
CORE = "src/gov/core/base.py"           # the shared core
GIZMO = "src/gov/gizmo/third.py"        # reached by nothing the cases change
EDGE = "src/gov/edge/e.py"
UNPLACED = "src/unplaced/odd.py"        # nothing maps it
GOVERNANCE_FILE = "governance/project/notes.yaml"
ADDED_TEST = "tests/unit/widget/test_w2_115_added.py"

TICKET_PATHS = ["src/gov/widget/**", "src/gov/core/**", "tests/unit/widget/**", "governance/project/notes.yaml"]

# wbs -> (ticket, allowed_paths)
SUITES = {
    "W2-aa": (TICKET, TICKET_PATHS),
    "W2-bb": ("PROJ-bbbb", ["src/gov/widget/**"]),     # reached by a widget change (overlap and import)
    "W2-cc": ("PROJ-cccc", ["src/gov/gadget/**"]),     # coupled to the shared core in the map
    "W2-dd": ("PROJ-dddd", ["src/gov/gizmo/**"]),      # reached by nothing: runs only in a full run
    "W2-ee": ("PROJ-eeee", ["src/gov/edge/**"]),       # imports the shared core
    "W2-rr": ("PROJ-rrrr", ["src/gov/reader/**"]),     # the record-reading suite
    "W2-ff": (SECOND, ["src/gov/widget/**"]),          # a second ticket on the widget (S10's second close)
}
IMPORTS = {"W2-aa": "gov.widget.thing", "W2-bb": "gov.widget.thing", "W2-cc": "gov.gadget.other",
           "W2-dd": "gov.gizmo.third", "W2-ee": "gov.core.base", "W2-rr": None, "W2-ff": "gov.widget.thing"}
WATCHED = (WIDGET, GADGET, CORE, REGISTER_REL)


def suite_of(wbs):
    return f"tests/acceptance/{wbs}"


def case_of(wbs):
    return "test_in_" + wbs.replace("-", "_")


def file_of(wbs, stem=None):
    return f"{suite_of(wbs)}/test_{stem or wbs.split('-')[1]}.py"


def node_of(wbs, stem=None, case=None):
    return f"{file_of(wbs, stem)}::{case or case_of(wbs)}"


RR_RECORDS = node_of("W2-rr", "rr_records", "test_rr_reads_the_register")

DEFAULT_TEST_MAP = {
    "version": 1,
    "shared_core": ["src/gov/core/**"],
    "record_only": [".tickets/**", "docs/checkpoints/**", "docs/close/**", "docs/probes/**", REGISTER_REL],
    "record_reading": [RR_RECORDS],
    "every_close": [],
    "couplings": [{"paths": ["src/gov/core/**"], "suites": [suite_of("W2-cc")],
                   "why": "W2-cc reads the shared core's constants as text"}],
    "test_inputs": ["fixtures/**"],
    "per_test_timeout": 20,
}

# What a store rebuild needs in a planted project (W2-68's form): the gitleaks rules of its secret filter, and one
# governance namespace that holds every path.
GITLEAKS = 'title = "Minimal gitleaks configuration"\n\n[extend]\nuseDefault = true\n'
NAMESPACE = {"paths": ["**"], "memory_class": "governance", "sensitivity": "internal",
             "permitted_roles": ["orchestrator", "engineer", "independent-test-designer"],
             "retention": "kept in git history", "export_policy": "allowed", "embedding_policy": "not embedded",
             "provenance": "written by the W2-115 tests", "deletion_rebuild": "authoritative; restored from git only"}


def quiet_env(sandbox):
    """``sandbox_env`` with the embedding endpoint down (a dead local address) and a stand-in for its program, so no
    rebuild a command makes can reach or start a model (W2-68's ``env_without_endpoint``)."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        dead = f"127.0.0.1:{probe.getsockname()[1]}"
    program = Path(sandbox.home).parent / "endpoint" / "ollama"
    program.parent.mkdir(parents=True, exist_ok=True)
    program.write_text(f"#!/bin/sh\necho started >> '{program.parent / 'started'}'\n", encoding="utf-8")
    program.chmod(0o755)
    env = {**close_support.sandbox_env(sandbox), "OLLAMA_HOST": dead, "GOV_QUERY_OLLAMA_HOST": dead,
           "GOV_OLLAMA_BIN": str(program)}
    env.pop("GOV_SECRETS_FULL_SCAN", None)
    return env


_STAND_IN = (
    '"""The planted project\'s stand-in for the package: the code under test is this worktree\'s."""\n'
    "__path__.append({gov!r})\n"
)

# Bodies of the telling tests: ``seen`` is what the test saw of WATCHED, ``_tell(ok)`` writes the run's line.
PASS = "    _tell(True)\n"
WIDGET_NOT_BROKEN = (f"    ok = 'BROKEN' not in (seen[{WIDGET!r}] or '')\n"
                     "    _tell(ok)\n    assert ok, 'the widget is broken'\n")
GADGET_NOT_BROKEN = (f"    ok = 'BROKEN' not in (seen[{GADGET!r}] or '')\n"
                     "    _tell(ok)\n    assert ok, 'the gadget is broken'\n")
KNOWN_RED = "    _tell(False)\n    assert False, 'a known red'\n"
TYPE_FLIP = (f"    _tell(False)\n    if 'CHANGED' in (seen[{WIDGET!r}] or ''):\n"
             "        raise ZeroDivisionError('another failure on the changed widget')\n"
             "    assert False, 'a known red'\n")
SLEEPS = "    _tell(False)\n    time.sleep(120)\n"
REGISTER_NOT_BROKEN = (f"    ok = 'BROKEN' not in (seen[{REGISTER_REL!r}] or '')\n"
                       "    _tell(ok)\n    assert ok, 'the register is broken'\n")
# Kills the test run it is in: the parallel runner's controller from a worker, else its own process.
KILLS_ITS_RUN = ("    _tell(False)\n    import signal\n"
                 "    os.kill(os.getppid() if os.environ.get('PYTEST_XDIST_WORKER') else os.getpid(), signal.SIGKILL)\n")


def telling(name, told, body=PASS, imports=None, depth=3):
    """A test file with one test ``name`` that appends a JSON line at each run to ``told/name``."""
    imp = f"    import {imports}  # noqa: F401\n" if imports else "    pass\n"
    return (
        "import json\nimport os\nimport sys\nimport time\nfrom pathlib import Path\n\n"
        f"ROOT = Path(__file__).resolve().parents[{depth}]\n"
        "if str(ROOT / 'src') not in sys.path:\n    sys.path.insert(0, str(ROOT / 'src'))\n"
        f"try:\n{imp}except Exception:\n    pass\n\n"
        f"WATCH = {list(WATCHED)!r}\n\n\n"
        "def _seen():\n"
        "    return {rel: ((ROOT / rel).read_text(encoding='utf-8') if (ROOT / rel).is_file() else None) for rel in WATCH}\n\n\n"
        "def _tell(ok):\n"
        f"    with open(os.path.join({str(told)!r}, {name!r}), 'a', encoding='utf-8') as out:\n"
        "        out.write(json.dumps({'root': str(ROOT), 'worker': os.environ.get('PYTEST_XDIST_WORKER', 'none'),\n"
        "                              'seen': _seen(), 'ok': ok, 'time': time.time()}) + '\\n')\n\n\n"
        f"def {name}():\n    seen = _seen()\n{body}"
    )


def map_text(data):
    return yaml.safe_dump(data, sort_keys=False)


class Smart:
    """A planted project ``gov close`` can run in.

    ``close`` is the switch's value written to ``governance/project/close.yaml`` (text written as given; ``None`` is
    a project without the file). ``reds`` are extra test files ``{rel: text}`` planted in the initial commit.
    ``nightly`` is ``"green"``, ``None`` (no record) or a list of failures for a red record on the base.
    ``path_map`` adds keys to the path map. The initial commit holds everything; only what a case commits later is in
    the change.
    """

    def __init__(self, root, told, close=SCOPED, test_map=DEFAULT_TEST_MAP, nightly="green", reds=None,
                 path_map=None, serial=None, files=None):
        self.root = Path(root)
        self.told = Path(told)
        self.root.mkdir(parents=True, exist_ok=True)
        self.told.mkdir(parents=True, exist_ok=True)
        self._minute = 0
        close_support.git(self.root, "init", "-q", "-b", "main")
        for rel, text in self.files(reds or {}, files or {}).items():
            self.write(rel, text)
        settings = {"namespaces": {"all": NAMESPACE}, **close_support.SUITE_SETTINGS, **(path_map or {})}
        self.write(PATH_MAP_REL, yaml.safe_dump(settings, sort_keys=False))
        if test_map is not None:
            self.write(TEST_MAP_REL, test_map if isinstance(test_map, str) else map_text(test_map))
        if close is not None:
            self.write(CLOSE_YAML_REL, close if "\n" in close else f"close: {close}\n")
        if serial:
            self.write(SERIAL_ONLY_REL, "".join(f"{entry}  # latency: planted\n" for entry in serial))
        self.initial = self._commit("initial project", close_support.OWNER, ())
        self.nightly_record = None
        if nightly is not None:
            self.nightly_record = self.plant_night(self.initial, [] if nightly == "green" else nightly)

    def files(self, reds, extra):
        told = self.told
        files = {
            "README.md": "# A project\n",
            ".gitignore": ".gov-runtime/\n",
            ".gitleaks.toml": GITLEAKS,
            f"docs/adr/{close_support.BASE_SOURCE}.md":
                close_support.decision(close_support.BASE_SOURCE, "ACTIVE", title="The base decision"),
            REGISTER_REL: "# The decision register\n\nNothing decided yet.\n",
            "src/gov/__init__.py": _STAND_IN.format(gov=str(SRC / "gov")),
            "src/gov/widget/__init__.py": "", WIDGET: "# the widget\n",
            "src/gov/gadget/__init__.py": "", GADGET: "# the gadget\n",
            "src/gov/core/__init__.py": "", CORE: "# the shared core\n",
            "src/gov/gizmo/__init__.py": "", GIZMO: "# a gizmo\n",
            "src/gov/edge/__init__.py": "", EDGE: "from gov.core import base  # noqa: F401\n",
            "src/gov/reader/__init__.py": "", "src/gov/reader/r.py": "# reader\n",
        }
        for wbs, (ticket, allowed) in SUITES.items():
            status = "in_progress" if ticket in (TICKET, SECOND) else "closed"
            files[close_support.ticket_path(ticket)] = close_support.ticket_text(ticket, wbs, allowed_paths=allowed,
                                                                                 status=status)
            files[f"{suite_of(wbs)}/README.md"] = f"# {wbs}\n"
            if wbs != "W2-rr":
                files[file_of(wbs)] = telling(case_of(wbs), told, imports=IMPORTS[wbs])
        files[RR_RECORDS.split("::")[0]] = telling("test_rr_reads_the_register", told, REGISTER_NOT_BROKEN)
        files.update(reds)
        files.update(extra)
        return files

    # -- commits --------------------------------------------------------------

    def _commit(self, message, who, trailers):
        self._minute += 1
        date = close_support.FIRST_DATE.format(minute=self._minute % 60)
        close_support.git(self.root, "add", "-A", who=who, date=date)
        args = ["commit", "-q", "--allow-empty", "--no-gpg-sign", "-m", message]
        for trailer in trailers:
            args += ["--trailer", trailer]
        close_support.git(self.root, *args, who=who, date=date)
        return self.head()

    def write(self, rel, text):
        return close_support.write(self.root, rel, text)

    def git(self, *args, **keys):
        return close_support.git(self.root, *args, **keys)

    def merged(self, files, message="another ticket's merged work"):
        for rel, text in files.items():
            self.write(rel, text)
        return self._commit(message, close_support.OWNER, ())

    def record_commit(self, files, message="a record"):
        for rel, text in files.items():
            self.write(rel, text)
        return self._commit(message, close_support.ORCHESTRATOR, close_support.ORCHESTRATOR["trailers"])

    def work(self, files, ticket=TICKET):
        for rel, text in files.items():
            self.write(rel, text)
        return self._commit("work on the ticket", close_support.IMPLEMENTER, close_support.trailers_of(ticket))

    def slip(self, files):
        """The engineer's commit without a ``Task:`` trailer (an honest slip): ``Role: engineer`` only."""
        for rel, text in files.items():
            self.write(rel, text)
        return self._commit("work on the ticket, its trailer forgotten", close_support.IMPLEMENTER,
                            (close_support.ENGINEER_ROLE,))

    def elsewhere(self, files, branch="elsewhere"):
        """A commit on another branch made from the current head; ``main`` is checked out again. Returns it."""
        self.git("checkout", "-q", "-b", branch)
        commit = self.merged(files, "work on another branch")
        self.git("checkout", "-q", "main")
        return commit

    def tickets(self):
        return {p.stem for p in (self.root / ".tickets").glob("*.md")}

    def ready(self, sandbox, ticket=TICKET):
        run = close_support.run_gov(self.root, sandbox, "checkpoint", "--ticket", ticket, "--trigger", "stop",
                                    "--next", "resume", "--json")
        assert run.returncode == 0, f"gov checkpoint failed in the planted project:\n{run.describe()}"
        return self._commit("checkpoint", close_support.ORCHESTRATOR, close_support.ORCHESTRATOR["trailers"])

    def commit_what_the_close_left(self):
        return self._commit("what the close left", close_support.ORCHESTRATOR, close_support.ORCHESTRATOR["trailers"])

    def plant_night(self, head, failures):
        rel = f"{NIGHTLY_DIR_REL}/NR-20261001T0{self._minute % 10}0000Z-{head[:12]}.json"
        tree = self.git("rev-parse", f"{head}^{{tree}}").strip()
        record = {"branch": "main", "head": head, "tree": tree, "scope": "full",
                  "verdict": "red" if failures else "green", "base": None, "junit_xml": [],
                  "failures": failures, "packages": []}
        self.record_commit({rel: json.dumps(record, indent=2) + "\n"}, "the nightly run's record")
        return rel

    def head(self):
        return self.git("rev-parse", "HEAD").strip()

    # -- the commands ---------------------------------------------------------

    def gov(self, sandbox, *args, env=None):
        """``gov <args>`` in the project, with the embedding endpoint down (``quiet_env``) unless ``env`` is given."""
        return close_support.run_gov(self.root, sandbox, *args, env=env or quiet_env(sandbox))

    def close(self, sandbox, ticket=TICKET, env=None):
        """``gov close <ticket> --json``, after loading the record store (W1-30's ``run_close`` does the same)."""
        close_support.load_store(self, sandbox, check=False)
        return self.gov(sandbox, "close", ticket, "--json", env=env)

    def select(self, sandbox, ticket=TICKET):
        return self.gov(sandbox, "close", "--select", ticket)

    def verify(self, sandbox, ticket=TICKET, out=None):
        close_support.load_store(self, sandbox, check=False)
        args = ["close", "--verify", ticket] + (["--out", str(out)] if out else [])
        return self.gov(sandbox, *args)

    # -- what the tests told --------------------------------------------------

    def told_runs(self, case):
        path = self.told / case
        if not path.is_file():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def ran(self, case):
        return bool(self.told_runs(case))

    def record(self, ticket=TICKET):
        """The close record's front matter at ``docs/close/<ticket>/CL-<ticket>.md``."""
        path = self.root / "docs" / "close" / ticket / f"CL-{ticket}.md"
        assert path.is_file(), f"no close record at {path.relative_to(self.root)}"
        return close_support.frontmatter_of(path)

    def ticket_status(self, ticket=TICKET):
        return close_support.ticket_status(self.root, ticket)


# --------------------------------------------------------------------------
# Reading what the commands say
# --------------------------------------------------------------------------

def envelope(run):
    try:
        return json.loads(run.stdout)
    except ValueError:
        raise AssertionError(f"no JSON envelope on stdout\n{run.describe()}") from None


def passed(run):
    env = envelope(run)
    assert env.get("ok") is True and run.returncode == 0, f"the close did not pass\n{run.describe()}"
    return env.get("result") or {}


def refusal_text(run):
    """What a refused command said, as one text: its envelope's error (when it printed one) and stderr."""
    try:
        error = json.loads(run.stdout).get("error")
    except (ValueError, AttributeError):
        error = None
    return (json.dumps(error, ensure_ascii=False) if error else run.stdout) + "\n" + run.stderr


def assert_refused(run, code=None):
    """The command was refused (no ``ok: true``, a non-zero exit); with ``code``, its text names that code."""
    try:
        ok = json.loads(run.stdout).get("ok")
    except (ValueError, AttributeError):
        ok = None
    assert ok is not True and run.returncode != 0, f"the command was not refused\n{run.describe()}"
    text = refusal_text(run)
    if code is not None:
        assert code in text, f"the refusal does not name {code}\n{run.describe()}"
    return text


def selection(run):
    """The JSON object ``gov close --select`` printed, checked for its form."""
    assert run.returncode == 0, f"gov close --select did not exit 0\n{run.describe()}"
    try:
        data = json.loads(run.stdout)
    except ValueError:
        raise AssertionError(f"gov close --select printed no JSON object\n{run.describe()}") from None
    assert isinstance(data, dict) and set(data) >= {"ticket", "suites", "pytest_options"}, \
        f"the selection lacks ticket, suites or pytest_options: {data!r}"
    assert isinstance(data["suites"], list) and isinstance(data["pytest_options"], list), f"bad form: {data!r}"
    assert data["suites"] == sorted(data["suites"]), f"the suites are not sorted: {data['suites']}"
    return data


def names(suites, target):
    """Whether the selection's suites hold ``target`` (a folder, a file or a node id), or a part of it."""
    target = target.rstrip("/")
    return any(s.rstrip("/") == target or s.startswith(target + "/") or s.startswith(target + "::")
               or target.startswith(s.rstrip("/") + "/") or target.startswith(s + "::") for s in suites)


def head_side(runs):
    """The runs of a telling test made on a tree that holds the ticket's change (the widget says CHANGED)."""
    return [r for r in runs if "CHANGED" in (r["seen"].get(WIDGET) or "")]


def base_side(runs):
    return [r for r in runs if "CHANGED" not in (r["seen"].get(WIDGET) or "")]


def red_entry(front, node):
    reds = front.get("reds")
    assert isinstance(reds, list), f"the close record holds no reds list: {sorted(front)}"
    found = [r for r in reds if isinstance(r, dict) and r.get("test") == node]
    assert len(found) == 1, f"the close record does not name the red {node} once: {reds}"
    return found[0]


def paths_named(root, words):
    """Every folder under ``root`` whose name holds one of ``words`` (case-insensitive), ``.git`` aside."""
    found = []
    for dirpath, dirnames, _ in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for d in dirnames:
            if any(w in d.lower() for w in words):
                found.append(os.path.join(dirpath, d))
    return found


def run_module(project, sandbox, module, *args, env=None):
    """``python3 -m <module> <args> --root <project> --json`` with this worktree's ``src/``."""
    cmd = [sys.executable, "-m", module, *args, "--root", str(project.root), "--json"]
    started = time.perf_counter()
    try:
        done = subprocess.run(cmd, cwd=str(project.root), env=env or quiet_env(sandbox),
                              capture_output=True, text=True, timeout=GOV_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{module} did not end within {GOV_TIMEOUT_S} s") from None
    return cli_support.Run(tuple(cmd[2:]), done.returncode, done.stdout, done.stderr, time.perf_counter() - started)


def probe_text(ticket, verdict_body, probed_commit, judgement="pass"):
    """A probe record: W1-30's front matter, then the reviewer's fenced ``verdict`` block (JUDGEMENT.md)."""
    text = close_support.probe_record(ticket, judgement=judgement, probed_commit=probed_commit)
    body = verdict_body if isinstance(verdict_body, str) else json.dumps(verdict_body, indent=2)
    return text + "\n## Verdict\n\n```verdict\n" + body + "\n```\n"


def candidate_ticket(ticket, wbs, allowed, told):
    """The files of one more ticket in progress, with its acceptance folder and a passing telling test."""
    return {close_support.ticket_path(ticket): close_support.ticket_text(ticket, wbs, allowed_paths=allowed,
                                                                         status="in_progress"),
            f"{suite_of(wbs)}/README.md": f"# {wbs}\n",
            file_of(wbs): telling(case_of(wbs), told)}


def plant_candidates(project, sandbox, candidates):
    """Each candidate ``(ticket, wbs, files, on)`` on its own branch ``w2/<wbs>``, made from ``on`` (another
    candidate's branch) or from ``main``'s head: the engineer's commit and the orchestrator's checkpoint. ``main``
    is checked out again at the end; nothing is merged. Returns ``{ticket: engineer's commit}``."""
    base = project.head()
    made = {}
    for ticket, wbs, files, on in candidates:
        project.git("checkout", "-q", "-b", f"w2/{wbs}", on or base)
        made[ticket] = project.work(files, ticket=ticket)
        project.ready(sandbox, ticket=ticket)
    project.git("checkout", "-q", "main")
    return made


def is_ancestor(project, commit, of="main"):
    done = subprocess.run(["git", "-C", str(project.root), "merge-base", "--is-ancestor", commit, of],
                          capture_output=True, text=True)
    return done.returncode == 0


def verdict(kpis):
    """``{"kpis": [...]}`` from ``[(kpi, pass|fail, [(id, scope, ordinary_work, consequence)])]``."""
    return {"kpis": [{"kpi": kpi, "verdict": v,
                      "findings": [{"id": f, "scope": s, "ordinary_work": o, "consequence": c}
                                   for f, s, o, c in findings]} for kpi, v, findings in kpis]}
