"""Support code for W2-66's acceptance tests: the path-scoped regression at close, its selection and its evidence.

How the tests run (README, "How the suite runs"):

- **Through public interfaces only:** ``gov close`` (W1-07's console-script stand-in, run with this worktree's
  ``src/`` on ``PYTHONPATH``, as W1-30's suite runs it), its API-0002 envelope, the close record it writes, the
  test map, and the nightly command ``python3 -m gov.close.nightly`` (README, "Interface").
- **Nothing is written in this worktree.** Every project is a temporary git repository built from scratch under
  pytest's ``tmp_path``: a few files of its own, no copy of this repository's tree.
- **What ran is told by the tests themselves:** every test of a fixture project is a "telling test" (W1-30's
  ``telling_test``): each run of it adds a line to a file of its own, outside the project, with the parallel
  worker it ran in.
- **Deterministic, no network.**
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ElementTree
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parent
_W1_30 = str(_HERE.parent / "W1-30")
if _W1_30 not in sys.path:
    sys.path.insert(0, _W1_30)

import w1_30_support as close_support  # noqa: E402

cli_support = close_support.cli_support

REPO_ROOT = close_support.REPO_ROOT
SRC = close_support.SRC

# --------------------------------------------------------------------------
# The interface (README, "Interface")
# --------------------------------------------------------------------------

TEST_MAP_REL = "governance/project/test-map.yaml"
TEST_MAP_SCHEMA_REL = "template/governance/kernel/schemas/test-map.schema.json"
TEMPLATE_TEST_MAP_REL = "template/governance/project/test-map.yaml"
PATH_MAP_REL = close_support.PATH_MAP_REL
SERIAL_ONLY_REL = close_support.SERIAL_ONLY_REL
REGISTER_REL = "docs/DECISION_REGISTER.md"
NIGHTLY_DIR_REL = "docs/close/nightly"

EVIDENCE_KEY = "evidence"
SCOPED, FULL = "scoped", "full"

# Why a target was selected.
OWN, UNIT, OVERLAP, TEST_CHANGED, HELPER, COUPLING, EVERY_CLOSE, RECORD_READING = (
    "OWN", "UNIT", "OVERLAP", "TEST_CHANGED", "HELPER", "COUPLING", "EVERY_CLOSE", "RECORD_READING")
# Why a target was left out.
NOT_REACHED = "NOT_REACHED"
# Why a close ran the full regression.
FULL_ASKED, SHARED_CORE, UNPLACED, TEST_MAP_MISSING, TEST_MAP_UNREADABLE, BASE_UNKNOWN = (
    "FULL_ASKED", "SHARED_CORE", "UNPLACED", "TEST_MAP_MISSING", "TEST_MAP_UNREADABLE", "BASE_UNKNOWN")

FULL_OPTION = "--full"
CHECK_RESULT_OPTION = "--check-result"
CHECK_RESULT_VARIABLE = "GOV_CLOSE_CHECK_RESULT"

PER_TEST_TIMEOUT_KEY = "per_test_timeout"
DEFAULT_PER_TEST_TIMEOUT = 900
DISTRIBUTION_KEY = "distribution"
DEFAULT_DISTRIBUTION = "load"
TIMEOUT_PLUGIN_ABSENT = "TIMEOUT_PLUGIN_ABSENT"

NIGHTLY_MODULE = "gov.close.nightly"
GREEN, RED = "green", "red"
FLAKY_CANDIDATE = "flaky_candidate"
P1 = "P1"
BISECT, SELECTION_MISS = "bisect", "selection_miss"

EXIT_OK = close_support.EXIT_OK
EXIT_GOV_ERROR = close_support.EXIT_GOV_ERROR
EXIT_CHECK_FAILED = close_support.EXIT_CHECK_FAILED

# --------------------------------------------------------------------------
# Patterns: the grammar of a ticket's ``allowed_paths`` as the close reads them on the base
# (``**`` any characters, ``/`` included; ``*`` any characters but ``/``; the rest literal; the whole path)
# --------------------------------------------------------------------------

_PATTERN_SPECIALS = re.compile(r"[?\[\]{}]")


def matches(pattern, path):
    parts = pattern.split("**")
    rx = "^" + ".*".join(re.escape(part).replace(r"\*", "[^/]*") for part in parts)
    if pattern.endswith("**"):
        rx += ".*"
    return re.match(rx + "$", path) is not None


def readable_pattern(pattern):
    """Whether a pattern uses only the grammar above (README, "Interface": no ``?``, ``[]`` or ``{}``)."""
    return isinstance(pattern, str) and bool(pattern) and not _PATTERN_SPECIALS.search(pattern)


def covers(entry, target):
    """Whether a pytest target ``entry`` (a folder, a file or a node id, relative to the project) holds
    ``target``: it is the target, or begins it at a boundary (``/``, ``::`` or ``[``)."""
    entry, target = entry.rstrip("/"), target.rstrip("/")
    return target == entry or (target.startswith(entry) and target[len(entry):].startswith(("/", "::", "[")))


def within(target, folder):
    """Whether ``target`` lies inside ``folder`` (or is it)."""
    return covers(folder, target)


# --------------------------------------------------------------------------
# The fixture project
# --------------------------------------------------------------------------

TICKET, WBS = "PROJ-aaaa", "W2-aa"

# wbs -> (ticket, allowed_paths); every ticket but TICKET is closed.
SUITES = {
    "W2-aa": ("PROJ-aaaa", ["src/gov/widget/**"]),         # the ticket closed by every case
    "W1-bb": ("PROJ-bbbb", ["src/gov/widget/**"]),         # overlaps a widget change; W1-35's bare conftest import
    "W2-bz": ("PROJ-bzbz", ["src/gov/widget/thing.py"]),   # overlaps it too, with a conftest of its own
    "W2-cc": ("PROJ-cccc", ["src/gov/gadget/**"]),
    "W1-dd": ("PROJ-dddd", ["src/gov/gizmo/**"]),
    "W1-gg": ("PROJ-gggg", ["src/gov/gear/**"]),           # holds gg_support
    "W1-hh": ("PROJ-hhhh", ["src/gov/hinge/**"]),          # holds hh_support, which imports gg_support
    "W2-ii": ("PROJ-iiii", ["src/gov/idle/**"]),           # imports hh_support
    "W1-rr": ("PROJ-rrrr", ["src/gov/reader/**"]),         # test_rr_records.py is the record-reading set
    "W1-ec": ("PROJ-ecec", ["src/gov/contract/**"]),       # test_ec_contract.py runs on every close
    "W1-cp": ("PROJ-cpcp", ["src/gov/coupled/**"]),        # coupled to src/gov/textread/data.txt
    "W2-zz": ("PROJ-zzzz", ["src/gov/close/**"]),          # another ticket's shared-core work
}
OTHER_SUITES = tuple(wbs for wbs in SUITES if wbs != WBS)
NOT_REACHED_BY_A_WIDGET_CHANGE = ("W2-cc", "W1-dd", "W1-gg", "W1-hh", "W2-ii", "W1-cp", "W2-zz")

WIDGET = "src/gov/widget/thing.py"
CORE = "src/gov/close/core.py"
UNPLACED_FILE = "src/unplaced/odd.py"
COUPLED_INPUT = "src/gov/textread/data.txt"
GG_HELPER = "tests/acceptance/W1-gg/gg_support.py"
RR_RECORDS = "tests/acceptance/W1-rr/test_rr_records.py"
RR_OTHER = "tests/acceptance/W1-rr/test_rr_other.py"
EC_CONTRACT = "tests/acceptance/W1-ec/test_ec_contract.py"
EC_OTHER = "tests/acceptance/W1-ec/test_ec_other.py"
BB_APART = "tests/acceptance/W1-bb/test_bb_apart.py::test_apart_W1_bb"
DD_APART = "tests/acceptance/W1-dd/test_dd_apart.py::test_apart_W1_dd"
BROKEN = "BROKEN"
# Beside the told folder: what the record-reading test found of the gate's check result.
CHECK_RESULT_SEEN = ".check-result"

DEFAULT_TEST_MAP = {
    "version": 1,
    "shared_core": ["src/gov/close/**", PATH_MAP_REL, TEST_MAP_REL],
    "record_only": [".tickets/**", "docs/checkpoints/**", "docs/close/**", "docs/probes/**", REGISTER_REL,
                    "docs/plan/*.md", "governance/project/orchestration/**.md"],
    "record_reading": [RR_RECORDS],
    "every_close": [EC_CONTRACT],
    "couplings": [{"paths": [COUPLED_INPUT], "suites": ["tests/acceptance/W1-cp"],
                   "why": "W1-cp reads the file as text"}],
}


def suite_of(wbs):
    return f"tests/acceptance/{wbs}"


def case_of(wbs):
    """The name of a suite's telling test."""
    return "test_in_" + wbs.replace("-", "_")


def node_of(wbs):
    return f"{suite_of(wbs)}/test_{wbs.split('-')[1]}.py::{case_of(wbs)}"


def _telling(name, told, body="assert True", head=""):
    return head + close_support.telling_test(name, told, body=body)


_STAND_IN = (
    '"""The fixture\'s stand-in for the package: the code under test is this worktree\'s (W2-66 README).\n\n'
    "A child process of the close that imports ``gov`` finds this worktree's subpackages behind the fixture's\n"
    'own folders, which hold only the files a case changes."""\n'
    "__path__.append({gov!r})\n"
)

_SYS_PATH = "import sys\nfrom pathlib import Path\n"


def _helper_import(folder, module):
    return (f"_HELPER = str(Path(__file__).resolve().parents[1] / {folder!r})\n"
            "if _HELPER not in sys.path:\n    sys.path.insert(0, _HELPER)\n"
            f"import {module}  # noqa: E402\n")


def project_files(told):
    """Every file of the fixture project, but its two maps: ``{path: text}``."""
    told = str(told)
    files = {
        "README.md": "# A project\n",
        ".gitignore": ".gov-runtime/\n",
        f"docs/adr/{close_support.BASE_SOURCE}.md":
            close_support.decision(close_support.BASE_SOURCE, "ACTIVE", title="The base decision"),
        REGISTER_REL: "# The decision register\n\nNothing decided yet.\n",
        "src/gov/__init__.py": _STAND_IN.format(gov=str(SRC / "gov")),
        CORE: "# the fixture's shared core\n",
        WIDGET: "# the widget\n",
        "src/gov/gadget/other.py": "# a gadget\n",
        "src/gov/gizmo/third.py": "# a gizmo\n",
        "src/gov/gear/g.py": "# gear\n",
        "src/gov/hinge/h.py": "# hinge\n",
        "src/gov/idle/i.py": "# idle\n",
        "src/gov/reader/r.py": "# reader\n",
        "src/gov/contract/c.py": "# contract\n",
        "src/gov/coupled/c.py": "# coupled\n",
        COUPLED_INPUT: "data\n",
        UNPLACED_FILE: "# a file no ticket and no list places\n",
        "tests/unit/test_unit_one.py": _telling("test_in_unit", told),
        SERIAL_ONLY_REL: f"{BB_APART}  # latency: planted\n{DD_APART}  # latency: planted\n",
    }
    for wbs, (ticket, allowed) in SUITES.items():
        status = "in_progress" if ticket == TICKET else "closed"
        files[close_support.ticket_path(ticket)] = close_support.ticket_text(ticket, wbs, allowed_paths=allowed,
                                                                             status=status)
        files[f"{suite_of(wbs)}/README.md"] = f"# {wbs}\n"
        files[node_of(wbs).split("::")[0]] = _telling(case_of(wbs), told)
    # W1-35's form (lens H finding 17): a module imports a constant from a bare ``conftest``.
    files["tests/acceptance/W1-bb/conftest.py"] = 'BB_NAME = "bb"\n'
    files[node_of("W1-bb").split("::")[0]] = _telling(case_of("W1-bb"), told, body="assert BB_NAME == 'bb'",
                                                      head="from conftest import BB_NAME  # noqa: E402\n")
    files["tests/acceptance/W2-bz/conftest.py"] = 'BZ_NAME = "bz"\n'
    files[node_of("W2-bz").split("::")[0]] = _telling(case_of("W2-bz"), told, body="assert BZ_NAME == 'bz'",
                                                      head="from conftest import BZ_NAME  # noqa: E402\n")
    # Test-side imports of shared helpers: W2-ii imports W1-hh's helper, which imports W1-gg's.
    files[GG_HELPER] = "VALUE = 1\n"
    files[node_of("W1-gg").split("::")[0]] = _telling(case_of("W1-gg"), told, body="assert gg_support.VALUE",
                                                      head=_SYS_PATH + _helper_import("W1-gg", "gg_support"))
    files["tests/acceptance/W1-hh/hh_support.py"] = (_SYS_PATH + _helper_import("W1-gg", "gg_support")
                                                     + "VALUE = gg_support.VALUE\n")
    files[node_of("W1-hh").split("::")[0]] = _telling(case_of("W1-hh"), told, body="assert hh_support.VALUE",
                                                      head=_SYS_PATH + _helper_import("W1-hh", "hh_support"))
    files[node_of("W2-ii").split("::")[0]] = _telling(case_of("W2-ii"), told, body="assert hh_support.VALUE",
                                                      head=_SYS_PATH + _helper_import("W1-hh", "hh_support"))
    # The record-reading test reads the register, and tells what the close handed it of the gate's check.
    files[RR_RECORDS] = _telling(
        "test_rr_reads_the_register", told,
        body=(f"register = open({REGISTER_REL!r}, encoding='utf-8').read()\n"
              f"    given = os.environ.get({CHECK_RESULT_VARIABLE!r})\n"
              f"    with open({told + CHECK_RESULT_SEEN!r}, 'w', encoding='utf-8') as out:\n"
              "        out.write(open(given, encoding='utf-8').read() if given and os.path.isfile(given) else '')\n"
              f"    assert {BROKEN!r} not in register, 'the register is broken: ' + register"))
    files[RR_OTHER] = _telling("test_rr_other", told)
    files[EC_CONTRACT] = _telling("test_ec_contract", told)
    files[EC_OTHER] = _telling("test_ec_other", told)
    # One serial-only case in a suite a widget change selects, one in a suite it leaves out.
    files[BB_APART.split("::")[0]] = _telling("test_apart_W1_bb", told)
    files[DD_APART.split("::")[0]] = _telling("test_apart_W1_dd", told)
    return files


def map_text(data):
    return yaml.safe_dump(data, sort_keys=False)


class Fixture:
    """A temporary project ``gov close`` can run in, with the suites of ``SUITES``.

    ``test_map`` is the test map's content (a dict, or text written as given); ``None`` is a project without one.
    ``green`` plants the record of a green nightly run naming the initial commit (the base); ``False`` plants
    none. The initial commit holds everything, both maps included, so that only what a case commits later is
    in the change.
    """

    def __init__(self, root, told, test_map=DEFAULT_TEST_MAP, green=True, settings=None):
        self.root = Path(root)
        self.told = Path(told)
        self.root.mkdir(parents=True, exist_ok=True)
        self.told.mkdir(parents=True, exist_ok=True)
        self._minute = 0
        close_support.git(self.root, "init", "-q", "-b", "main")
        for rel, text in project_files(self.told).items():
            close_support.write(self.root, rel, text)
        path_map = dict(close_support.SUITE_SETTINGS, **(settings or {}))
        close_support.write(self.root, PATH_MAP_REL, close_support.path_map_text(path_map))
        if test_map is not None:
            close_support.write(self.root, TEST_MAP_REL,
                                test_map if isinstance(test_map, str) else map_text(test_map))
        self.initial = self._commit("initial project", close_support.OWNER, ())
        self.nightly_record = self.plant_green_night(self.initial) if green else None

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

    def merged(self, files, message="another ticket's merged work"):
        """Work merged since the base, before the ticket's own: it is in the change, not in the ticket's range."""
        for rel, text in files.items():
            self.write(rel, text)
        return self._commit(message, close_support.OWNER, ())

    def record_commit(self, files, message="a record"):
        """The orchestrator's record-only commit."""
        for rel, text in files.items():
            self.write(rel, text)
        return self._commit(message, close_support.ORCHESTRATOR, close_support.ORCHESTRATOR["trailers"])

    def work(self, files, ticket=TICKET):
        """The ticket's engineer's commit."""
        for rel, text in files.items():
            self.write(rel, text)
        return self._commit("work on the ticket", close_support.IMPLEMENTER, close_support.trailers_of(ticket))

    def ready(self, sandbox, ticket=TICKET):
        """The orchestrator's checkpoint, committed: the project is ready for the ticket's close."""
        run = close_support.run_gov(self.root, sandbox, "checkpoint", "--ticket", ticket, "--trigger", "stop",
                                    "--next", "resume", "--json")
        assert run.returncode == 0, f"gov checkpoint failed in the fixture:\n{run.describe()}"
        return self._commit("checkpoint", close_support.ORCHESTRATOR, close_support.ORCHESTRATOR["trailers"])

    def commit_what_the_close_left(self):
        return self._commit("what the close left", close_support.ORCHESTRATOR,
                            close_support.ORCHESTRATOR["trailers"])

    def plant_green_night(self, head, verdict=GREEN):
        """The record of a nightly full run on ``head`` (README, "Interface", the nightly record), committed by the
        orchestrator: a record-only commit."""
        rel = f"{NIGHTLY_DIR_REL}/NR-20261001T0{self._minute % 10}0000Z-{head[:12]}.json"
        tree = close_support.git(self.root, "rev-parse", f"{head}^{{tree}}", check=False).strip() or None
        record = {"branch": "main", "head": head, "tree": tree, "scope": FULL,
                  "verdict": verdict, "base": None, "junit_xml": [], "failures": [], "packages": []}
        return self.record_commit({rel: json.dumps(record, indent=2) + "\n"}, "the nightly run's record") and rel

    def head(self):
        return close_support.git(self.root, "rev-parse", "HEAD").strip()

    # -- the close ------------------------------------------------------------

    def close(self, sandbox, *args, ticket=TICKET, env=None):
        """``gov close <ticket> --json <args>``, after loading the record store (as W1-30's ``run_close``)."""
        close_support.load_store(self, sandbox, check=False)
        return close_support.run_gov(self.root, sandbox, "close", ticket, "--json", *args, env=env)

    def told_runs(self):
        return close_support.told_by(self.told)

    def ran(self, case):
        return case in self.told_runs()

    def check_result_seen(self):
        """What the record-reading test read from the file ``GOV_CLOSE_CHECK_RESULT`` names; None if it did not run."""
        path = Path(str(self.told) + CHECK_RESULT_SEEN)
        return path.read_text(encoding="utf-8") if path.is_file() else None


def tree_of(root, commit="HEAD"):
    return close_support.git(root, "rev-parse", f"{commit}^{{tree}}").strip()


def widget_change(fixture, sandbox, text="# the widget, changed\n"):
    """The ticket's one-module change outside the shared core, ready to close."""
    fixture.work({WIDGET: text})
    fixture.ready(sandbox)


# --------------------------------------------------------------------------
# Reading what the close says
# --------------------------------------------------------------------------

def envelope_of(run):
    return run.envelope()


def passed(run):
    envelope = envelope_of(run)
    assert envelope.get("ok") is True and run.returncode == EXIT_OK, f"the close did not pass\n{run.describe()}"
    return envelope["result"]


def refused(run, exit_code=EXIT_CHECK_FAILED):
    envelope = envelope_of(run)
    assert envelope.get("ok") is False, f"the close was not refused\n{run.describe()}"
    assert run.returncode == exit_code, f"expected exit code {exit_code}\n{run.describe()}"
    return envelope["error"]


def evidence_of(run):
    """The evidence block of a close: ``result.evidence`` of a passed close (and the same block in its close
    record), ``error.details.evidence`` of a refused one."""
    envelope = envelope_of(run)
    if envelope.get("ok") is True:
        holder, where = envelope.get("result") or {}, "the result"
    else:
        holder, where = (envelope.get("error") or {}).get("details") or {}, "the refusal's details"
    evidence = holder.get(EVIDENCE_KEY)
    assert isinstance(evidence, dict), f"{where}: no evidence block under {EVIDENCE_KEY!r}\n{run.describe()}"
    return evidence


def record_evidence(fixture, ticket=TICKET):
    front = close_support.the_close_record(fixture, ticket)
    evidence = front.get(EVIDENCE_KEY)
    assert isinstance(evidence, dict), f"the close record holds no evidence block: {sorted(front)}"
    return evidence


def reasons(entry):
    why = entry.get("why")
    assert isinstance(why, list) and why and all(isinstance(w, dict) and w.get("reason") for w in why), \
        f"an entry names no reason: {entry!r}"
    return why


def entries_covering(entries, target):
    """The entries of ``selected`` or ``left_out`` that hold ``target``."""
    assert isinstance(entries, list), f"not a list of entries: {entries!r}"
    return [entry for entry in entries if isinstance(entry, dict) and covers(str(entry.get("target", "")), target)]


def selected_for(evidence, target):
    """The reasons the evidence gives for running ``target``; empty when it names none."""
    return [w for entry in entries_covering(evidence.get("selected"), target) for w in reasons(entry)]


def left_out_for(evidence, target):
    """The reasons the evidence gives for leaving ``target`` out; empty when it names none. A suite is named left
    out by an entry that holds it, or by entries for each of its test files."""
    return [w for entry in entries_covering(evidence.get("left_out"), target) for w in reasons(entry)]


def suite_named_left_out(fixture, evidence, wbs):
    folder = suite_of(wbs)
    if left_out_for(evidence, folder):
        return True
    files = sorted(p.relative_to(fixture.root).as_posix() for p in (fixture.root / folder).glob("test_*.py"))
    return bool(files) and all(left_out_for(evidence, rel) for rel in files)


def why_full(evidence):
    why = evidence.get("why_full")
    assert isinstance(why, list), f"the evidence of a full run gives no why_full: {evidence!r}"
    return {w.get("reason") for w in why if isinstance(w, dict)}, why


def assert_full(run, fixture, reason, path=None):
    """The close ran the full regression, said so, and said why; every suite ran."""
    evidence = evidence_of(run)
    assert evidence.get("scope") == FULL, f"the run is not stated full: scope {evidence.get('scope')!r}"
    codes, why = why_full(evidence)
    assert reason in codes, f"the full run does not give {reason} among its reasons: {why}"
    if path is not None:
        assert any(path in json.dumps(w) for w in why if w.get("reason") == reason), \
            f"the reason {reason} does not name {path}: {why}"
    assert not evidence.get("left_out"), f"a full run left something out: {evidence.get('left_out')}"
    ran = fixture.told_runs()
    missing = [case_of(wbs) for wbs in SUITES if case_of(wbs) not in ran]
    assert not missing, f"a full run did not run these suites: {missing}"
    return evidence


def junit_cases(root, evidence):
    """``{name: (outcome, text)}`` of every test case of the run's JUnit XML files; the files must exist."""
    paths = evidence.get("junit_xml")
    assert isinstance(paths, list) and paths, f"the evidence names no JUnit XML file: {evidence.get('junit_xml')!r}"
    cases = {}
    for rel in paths:
        path = Path(root) / rel
        assert path.is_file(), f"the JUnit XML file {rel} named by the evidence does not exist"
        tree = ElementTree.parse(path)
        for case in tree.iter("testcase"):
            outcome, text = "passed", ""
            for child in case:
                if child.tag in ("failure", "error", "skipped"):
                    outcome = child.tag
                    text = (child.get("message") or "") + "\n" + (child.text or "")
            cases[case.get("name")] = (outcome, text)
    return cases


def environment_without_module(base, sandbox, prefixes):
    """``sandbox_env`` in which the interpreter running the suite finds every installed package of its per-user
    folder but those whose names begin with ``prefixes`` (as W1-30's ``environment_without_parallel_runner``).
    Where the per-user folder is not in use, the plain environment (nothing of it to take away)."""
    import site

    env = close_support.sandbox_env(sandbox)
    if not site.ENABLE_USER_SITE or not Path(site.getusersitepackages()).is_dir():
        return env
    real = Path(site.getusersitepackages())
    mirror = Path(base) / "userbase" / real.relative_to(site.getuserbase())
    mirror.mkdir(parents=True)
    for entry in real.iterdir():
        name = entry.name.lower()
        if name.startswith(prefixes) or name.endswith(".pth"):
            continue
        (mirror / entry.name).symlink_to(entry)
    return {**env, "PYTHONUSERBASE": str(Path(base) / "userbase")}


# --------------------------------------------------------------------------
# The nightly command
# --------------------------------------------------------------------------

NIGHTLY_TIMEOUT_S = 600


def run_nightly(fixture, sandbox, *args):
    """``python3 -m gov.close.nightly <args> --root <project> --json``, with this worktree's ``src/``."""
    cmd = [sys.executable, "-m", NIGHTLY_MODULE, *args, "--root", str(fixture.root), "--json"]
    try:
        done = subprocess.run(cmd, cwd=str(fixture.root), env=close_support.sandbox_env(sandbox),
                              capture_output=True, text=True, timeout=NIGHTLY_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"the nightly command did not end within {NIGHTLY_TIMEOUT_S} s") from None
    return cli_support.Run(tuple(cmd[2:]), done.returncode, done.stdout, done.stderr, 0.0)


def nightly_record(fixture, run):
    """The nightly run's record: the file the result names under ``record``, read as JSON."""
    envelope = run.envelope()
    body = envelope.get("result") if envelope.get("ok") else (envelope.get("error") or {}).get("details")
    rel = (body or {}).get("record")
    assert isinstance(rel, str) and rel.startswith(NIGHTLY_DIR_REL + "/"), \
        f"the nightly run names no record under {NIGHTLY_DIR_REL}/\n{run.describe()}"
    path = fixture.root / rel
    assert path.is_file(), f"the nightly record {rel} does not exist\n{run.describe()}"
    return json.loads(path.read_text(encoding="utf-8")), rel


def os_environ_path():
    return os.environ.get("PATH", "/usr/bin:/bin")
