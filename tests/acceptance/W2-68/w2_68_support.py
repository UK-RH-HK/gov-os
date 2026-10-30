"""Support code for W2-68's acceptance tests: batched closes, reuse on the same code, and two fingerprints.

How the tests run (README, "How the suite runs"):

- **Through public interfaces only:** ``python3 -m gov.close.batch run <ticket> [<ticket> ...] --root <project>
  --json`` and ``python3 -m gov.close.batch refresh --root <project> --json`` (API-0002 envelopes), ``gov close``
  and its evidence block and close record, ``gov rebuild``, ``gov check`` (through a declared check that tells each
  run), ``gov checkpoint``, the batch's run record under ``docs/close/nightly/`` (``kind: batch``) and the lexical
  freshness check ``python3 -m gov.retrieval.lexical`` in the project root. Every process runs this worktree's
  ``src/`` (W1-07's console-script stand-in, ``PYTHONPATH``; DEC-732).
- **Nothing is written in this worktree.** Every project is a temporary git repository built from scratch under
  pytest's temporary folders: W2-66's fixture project (``w2_66_support.Fixture``, imported, never copied), with a
  few files of this suite's own.
- **What ran is told by the tests themselves** (W1-30's telling tests): each run of a fixture test adds a line to
  a file of its own outside the project. The two planted reds of the red batch also tell the commit they ran at, so
  a run at another commit than the batch's head (a bisect) is seen.
- **Deterministic, no network.** The embedding endpoint is down in every command (a dead local address, and a
  stand-in for its program that only records a start); nothing needs a model.

No ``conftest.py``: the fixtures are here and in the test modules (DEC-919).
"""

from __future__ import annotations

import json
import os
import re
import socket
import subprocess
import sys
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parent
_W2_66 = str(_HERE.parent / "W2-66")
if _W2_66 not in sys.path:
    sys.path.insert(0, _W2_66)

import w2_66_support as scoped  # noqa: E402

close_support = scoped.close_support
cli_support = scoped.cli_support

# --------------------------------------------------------------------------
# The interface (README, "Interface")
# --------------------------------------------------------------------------

BATCH_MODULE = "gov.close.batch"
RUN, REFRESH = "run", "refresh"
BATCH_KIND = "batch"
REUSED = "reused"                                     # evidence.scope of a close that reuses a run
REUSED_KEY = "reused"                                 # the block that cites the reused run
CODE_FINGERPRINT = "code_fingerprint"
RECORDS_FINGERPRINT = "records_fingerprint"
GOVERNANCE_CHECKS_REUSED = "governance_checks_reused"
STORE_STALE = "STORE_STALE"
STORE_CODE_CHANGED = "STORE_CODE_CHANGED"
CHECKPOINT_MISSING = "CHECKPOINT_MISSING"
NIGHTLY_DIR_REL = scoped.NIGHTLY_DIR_REL
PATH_MAP_REL = scoped.PATH_MAP_REL
TEST_MAP_REL = scoped.TEST_MAP_REL
LEXICAL_MODULE = "gov.retrieval.lexical"

EXIT_OK = close_support.EXIT_OK
EXIT_GOV_ERROR = close_support.EXIT_GOV_ERROR
COMMAND_TIMEOUT_S = 900

# --------------------------------------------------------------------------
# The fixture project: W2-66's, with what a batch needs
# --------------------------------------------------------------------------

A, A_WBS = "PROJ-aaaa", "W2-aa"          # widget; in progress in every project
C, C_WBS = "PROJ-cccc", "W2-cc"          # gadget; in progress in every project of this suite
D_TICKET = "PROJ-dddd"                    # W1-dd's ticket (closed): the red test's own ticket
WIDGET = scoped.WIDGET
GADGET = "src/gov/gadget/other.py"
RR_CASE = "test_rr_reads_the_register"
UNIT_CASE = "test_in_unit"
CASE = scoped.case_of                     # the telling case of a suite: CASE("W2-cc") == "test_in_W2_cc"
ALL_SUITES = tuple(scoped.SUITES)
SERIAL_CASES = ("test_apart_W1_bb", "test_apart_W1_dd")

# The record-reading set and the shared core of W2-66's fixture map; no every-close target, so that what a
# reused close runs is its own suite and the record-reading set alone (README, "Interface", item 5).
TEST_MAP = {key: value for key, value in scoped.DEFAULT_TEST_MAP.items() if key != "every_close"}

# The gitleaks rules a rebuild's secret filter needs in the project (W1-07's minimal configuration).
GITLEAKS = 'title = "Minimal gitleaks configuration"\n\n[extend]\nuseDefault = true\n'
# The path map of every project: W2-66's settings, and one governance namespace that holds every path, so that the
# lexical index holds chunks (an index without any is "empty", never fresh) and every path has one namespace.
NAMESPACE = {"paths": ["**"], "memory_class": "governance", "sensitivity": "internal",
             "permitted_roles": ["orchestrator", "engineer", "independent-test-designer"],
             "retention": "kept in git history", "export_policy": "allowed", "embedding_policy": "not embedded",
             "provenance": "written by the W2-68 tests", "deletion_rebuild": "authoritative; restored from git only"}
PATH_MAP = {"namespaces": {"all": NAMESPACE}, **close_support.SUITE_SETTINGS}
CHECK_ID = "w2-68-told"
CHECK_REL = f"{close_support.CHECKS_REL}/{CHECK_ID}.yaml"
GOV_CHECK_TOLD = "gov-check"

# A planted skip of the regression, in a suite no closed ticket of the cases owns.
SKIP_REL = "tests/acceptance/W2-zz/test_zz_planted_skip.py"
SKIP_CASE = "test_zz_planted_skip"
SKIP_REASON = "W2-68 planted skip, carried by the reused run"

# The red batch: W1-dd's test reads the gadget, which ticket C's work breaks; W1-cp's test fails on its first
# run only (a flaky candidate).
RED_REL = "tests/acceptance/W1-dd/test_dd.py"
RED_CASE = CASE("W1-dd")
RED_TEXT = "the gadget is broken"
FLAKY_REL = "tests/acceptance/W1-cp/test_cp.py"
FLAKY_CASE = CASE("W1-cp")
FLAKY_TEXT = "planted flaky failure: it fails on its first run only"


def _committing_test(name, told, counts, body):
    """A telling test that also tells the commit its file stands in (``git rev-parse HEAD`` of its folder)."""
    return (
        "import os\nimport subprocess\nimport time\n\n\n"
        f"def {name}():\n"
        "    here = os.path.dirname(os.path.abspath(__file__))\n"
        "    commit = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=here, capture_output=True,\n"
        "                            text=True).stdout.strip() or 'none'\n"
        "    case = os.environ['PYTEST_CURRENT_TEST'].split('::')[-1].split(' ')[0]\n"
        f"    with open(os.path.join({str(told)!r}, case), 'a', encoding='utf-8') as told:\n"
        f"        told.write(os.environ.get({close_support.WORKER_VARIABLE!r}, {close_support.NO_WORKER!r})"
        " + ' ' + repr(time.time()) + ' ' + commit + '\\n')\n"
        f"    counts = {str(counts)!r}\n"
        f"{body}"
    )


def red_test(told, counts):
    return _committing_test(RED_CASE, told, counts, (
        "    gadget = open(os.path.join(here, '..', '..', '..', 'src', 'gov', 'gadget', 'other.py'),\n"
        "                  encoding='utf-8').read()\n"
        f"    assert 'BROKEN' not in gadget, {RED_TEXT!r} + ': ' + gadget\n"))


def flaky_test(told, counts):
    return _committing_test(FLAKY_CASE, told, counts, (
        "    first = os.path.join(counts, 'flaky-first-run')\n"
        "    if not os.path.exists(first):\n"
        "        open(first, 'w', encoding='utf-8').close()\n"
        f"        raise AssertionError({FLAKY_TEXT!r})\n"))


def skip_test():
    return ("import pytest\n\n\n"
            f"def {SKIP_CASE}():\n"
            f"    pytest.skip({SKIP_REASON!r})\n")


def check_declaration(counts):
    """A declared check of the project's own: each ``gov check`` that runs it adds a line to a file of its own."""
    command = f"echo checked >> '{Path(counts) / GOV_CHECK_TOLD}'"
    fields = (("id", CHECK_ID), ("family", "schema/invariants"), ("tier", "G1"), ("severity", "hard-block"),
              ("command", command))
    return "".join(f"{key}: {json.dumps(value)}\n" for key, value in fields)


class Project(scoped.Fixture):
    """W2-66's fixture project (``scoped.Fixture``), with:

    - ticket C (``PROJ-cccc``, ``src/gov/gadget/**``) in progress beside ticket A;
    - the gitleaks rules the rebuild's secret filter needs, a path map with one governance namespace for every path
      (``PATH_MAP``), and a declared check that tells each ``gov check``;
    - with ``plant_skip``, a skipping test in W2-zz's suite; with ``plant_reds``, W1-dd's red and W1-cp's flaky test.

    All of it lands in one commit that a green nightly record names (``based``): the base, not the change.
    ``counts`` is a folder outside the project for what the gov check and the planted tests tell.
    """

    def __init__(self, root, told, test_map=TEST_MAP, plant_skip=False, plant_reds=False):
        super().__init__(root, told, test_map=test_map)
        self.counts = Path(str(self.told) + ".counts")
        self.counts.mkdir(parents=True, exist_ok=True)
        files = {
            ".gitleaks.toml": GITLEAKS,
            PATH_MAP_REL: yaml.safe_dump(PATH_MAP, sort_keys=False),
            CHECK_REL: check_declaration(self.counts),
            close_support.ticket_path(C): close_support.ticket_text(C, C_WBS, allowed_paths=["src/gov/gadget/**"],
                                                                    status="in_progress"),
        }
        if plant_skip:
            files[SKIP_REL] = skip_test()
        if plant_reds:
            files[RED_REL] = red_test(self.told, self.counts)
            files[FLAKY_REL] = flaky_test(self.told, self.counts)
        self.setting = self.based(files, "the batch's setting")

    # -- what the project tells ---------------------------------------------

    def runs(self):
        """``{case: number of runs}`` so far."""
        return {case: len(runs) for case, runs in self.told_runs().items()}

    def runs_since(self, before):
        """``{case: runs since before}`` of every case that ran since ``before`` (a ``runs()``)."""
        now = self.runs()
        return {case: count - before.get(case, 0) for case, count in now.items() if count - before.get(case, 0)}

    def commits_told(self, case):
        """``[(time, commit)]`` of each run of a committing test, in the order they ran."""
        path = self.told / case
        if not path.is_file():
            return []
        found = []
        for line in path.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            found.append((float(parts[1]), parts[2] if len(parts) > 2 else "none"))
        return sorted(found)

    def gov_checks_run(self):
        path = self.counts / GOV_CHECK_TOLD
        return len(path.read_text(encoding="utf-8").splitlines()) if path.is_file() else 0

    # -- commits ----------------------------------------------------------------

    def code_commit(self, rel="notes/later.txt", text="a later commit\n"):
        """The orchestrator's commit of a path no ticket owns and no record-only pattern holds: code."""
        return self.record_commit({rel: text}, "a later commit")

    def path_map_commit(self):
        """A commit that changes the path map's bytes and nothing it says (a comment line): code (DEC-880)."""
        text = (self.root / PATH_MAP_REL).read_text(encoding="utf-8")
        return self.record_commit({PATH_MAP_REL: text + "# the path map is in the shared core (DEC-880)\n"},
                                  "a comment in the path map")

    def commit_left(self):
        """What a batch or a close left in the working tree, committed by the orchestrator; None when nothing."""
        if not close_support.git(self.root, "status", "--porcelain", "-uall").strip():
            return None
        return self.commit_what_the_close_left()


def env_without_endpoint(sandbox):
    """``sandbox_env`` with the embedding endpoint down: a dead local address, and a stand-in for its program that
    records a start (as W1-30's rebuild case)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        dead = f"127.0.0.1:{probe.getsockname()[1]}"
    program = Path(sandbox.home).parent / "endpoint" / "ollama"
    program.parent.mkdir(parents=True, exist_ok=True)
    program.write_text(f"#!/bin/sh\necho started >> '{program.parent / 'started'}'\n", encoding="utf-8")
    program.chmod(0o755)
    return {**close_support.sandbox_env(sandbox), "OLLAMA_HOST": dead, "GOV_QUERY_OLLAMA_HOST": dead,
            "GOV_OLLAMA_BIN": str(program)}


def make_sandbox(base):
    return cli_support.make_sandbox(Path(base) / "sandbox")


# --------------------------------------------------------------------------
# The commands
# --------------------------------------------------------------------------

class Answer:
    """What a command printed: its exit code and its API-0002 envelope, or why it gave none."""

    def __init__(self, what, done):
        self.what, self.returncode, self.stdout, self.stderr = what, done.returncode, done.stdout, done.stderr
        try:
            data = json.loads(done.stdout)
            self.data = data if isinstance(data, dict) else None
        except ValueError:
            self.data = None

    def describe(self):
        return (f"{self.what}\nexit code: {self.returncode}\nstdout:\n{self.stdout[-4000:]}\n"
                f"stderr:\n{self.stderr[-2000:]}")

    def envelope(self):
        assert self.data is not None, f"{self.what} gave no API-0002 envelope\n{self.describe()}"
        return self.data

    def ok(self):
        envelope = self.envelope()
        assert envelope.get("ok") is True and self.returncode == EXIT_OK, f"{self.what} did not pass\n{self.describe()}"
        return envelope.get("result") or {}

    def refused(self):
        envelope = self.envelope()
        assert envelope.get("ok") is False and self.returncode != EXIT_OK, \
            f"{self.what} was not refused\n{self.describe()}"
        return envelope.get("error") or {}

    def text(self):
        return self.stdout + "\n" + self.stderr


def _module(project, env, module, *args, cwd=None):
    cmd = [sys.executable, "-m", module, *args]
    try:
        done = subprocess.run(cmd, cwd=str(cwd or project.root), env=env, capture_output=True, text=True,
                              timeout=COMMAND_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"python3 -m {module} {' '.join(args)} did not end within {COMMAND_TIMEOUT_S} s") \
            from None
    return Answer(f"python3 -m {module} {' '.join(args)}", done)


def batch(project, env, *tickets):
    """``python3 -m gov.close.batch run <tickets> --root <project> --json``."""
    return _module(project, env, BATCH_MODULE, RUN, *tickets, "--root", str(project.root), "--json")


def refresh(project, env):
    """``python3 -m gov.close.batch refresh --root <project> --json``: the incremental record load."""
    return _module(project, env, BATCH_MODULE, REFRESH, "--root", str(project.root), "--json")


def lexical_check(project, env):
    """The lexical index's freshness check, in the project root: exit 0 only on a fresh index."""
    return _module(project, env, LEXICAL_MODULE)


def rebuild(project, sandbox, env):
    run = close_support.run_gov(project.root, sandbox, "rebuild", "--no-embeddings", "--json", env=env)
    envelope = run.envelope()
    assert envelope.get("ok") is True and run.returncode == EXIT_OK, f"gov rebuild failed\n{run.describe()}"
    return envelope["result"]


def close_without_load(project, sandbox, env, ticket=A):
    """``gov close <ticket> --json`` on the store as it stands (no load first)."""
    return close_support.run_gov(project.root, sandbox, "close", ticket, "--json", env=env)


# --------------------------------------------------------------------------
# Reading what was recorded
# --------------------------------------------------------------------------

def batch_records(project):
    """``[(rel, record, text)]`` of every run record under ``docs/close/nightly/`` whose ``kind`` is ``batch``."""
    found = []
    for path in sorted((project.root / NIGHTLY_DIR_REL).glob("*")):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        try:
            record = json.loads(text)
        except ValueError:
            try:
                record = yaml.safe_load(text)
            except yaml.YAMLError:
                continue
        if isinstance(record, dict) and record.get("kind") == BATCH_KIND:
            found.append((path.relative_to(project.root).as_posix(), record, text))
    return found


def the_batch_record(project):
    records = batch_records(project)
    assert len(records) == 1, (f"one run record of kind {BATCH_KIND!r} under {NIGHTLY_DIR_REL}/ is expected, found "
                               f"{[rel for rel, _, _ in records]}")
    return records[0]


def strings_in(value):
    """Every string at any depth of a JSON-like value."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from strings_in(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from strings_in(item)


def values_of(value, wanted):
    """Every value at any depth of ``value`` whose key satisfies ``wanted(key)``."""
    if isinstance(value, dict):
        for key, item in value.items():
            if wanted(str(key)):
                yield item
            yield from values_of(item, wanted)
    elif isinstance(value, list):
        for item in value:
            yield from values_of(item, wanted)


def names_commit(value, commit):
    """Whether ``value`` (a JSON-like value or text) names ``commit``: its full id or its first 12 digits."""
    text = value if isinstance(value, str) else json.dumps(value)
    return commit in text or commit[:12] in text


def xml_files(project, value):
    """``[(named, path)]`` of every JUnit XML file a value names (a string ending ``.xml``), relative to the
    project or absolute."""
    found = []
    for named in dict.fromkeys(s for s in strings_in(value) if s.endswith(".xml")):
        path = Path(named) if os.path.isabs(named) else project.root / named
        found.append((named, path))
    return found


def junit_names(path):
    """The case names a JUnit XML file holds."""
    import xml.etree.ElementTree as ElementTree
    return {case.get("name") for case in ElementTree.parse(path).iter("testcase")}


def close_evidence(project, ticket):
    """The evidence block of the ticket's one close record."""
    return scoped.record_evidence(project, ticket)


def the_close_record(project, ticket):
    return close_support.the_close_record(project, ticket)


def cited_run(evidence):
    """What a close's evidence says of a reused run: ``(scope, reused block or None)``."""
    block = evidence.get(REUSED_KEY)
    return evidence.get("scope"), block if isinstance(block, dict) else None


def evidence_of_any(run):
    """The evidence block of a close, passed or refused; None when it states none (a refusal before any test)."""
    try:
        envelope = run.envelope()
    except AssertionError:
        return None
    holder = envelope.get("result") if envelope.get("ok") is True else (envelope.get("error") or {}).get("details")
    evidence = (holder or {}).get(scoped.EVIDENCE_KEY)
    return evidence if isinstance(evidence, dict) else None


def assert_does_not_cite(run, head, what):
    """The close (passed or refused) neither states ``scope: reused`` nor cites a run on ``head``."""
    evidence = evidence_of_any(run)
    if evidence is None:
        return
    scope, block = cited_run(evidence)
    assert scope != REUSED, f"{what}: the close reused a run (scope {scope!r}): {json.dumps(block)[:1500]}"
    assert block is None or not names_commit(block, head), \
        f"{what}: the close cites the run on {head[:12]}: {json.dumps(block)[:1500]}"


def ticket_closed(project, ticket):
    """Whether the ticket's file says ``closed``, in the working tree or in ``HEAD``."""
    in_tree = close_support.ticket_status(project.root, ticket) == "closed"
    at_head = close_support.git(project.root, "show", f"HEAD:{close_support.ticket_path(ticket)}", check=False)
    return in_tree or bool(re.search(r"^status:\s*closed\s*$", at_head, re.MULTILINE))


def normalised(text):
    return re.sub(r"[-_\s]+", " ", text.lower())
