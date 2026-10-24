"""Support code for the W2-07 acceptance tests (DAEO-r9ss).

W2-07: ``gov close`` judges a ticket by its class; the commit gates and DEC-868's pre-close gate run before any
test and spend no ratchet attempt; decision records are measured by their decision; the disk floor; the probe
gate's named-finding acceptance; complete, tracked repair tickets; the governance share of every close.

How the tests run (README, "How the tests run"):

- **Through public interfaces only**: ``gov close <ticket> --json`` (API-0002 envelope, exit codes, findings),
  ``gov check``, the audit validator's command line, the project's path map, ticket files, records, the decision
  register and commit trailers.
- **The code under test is this worktree's ``src/``** (DEC-732): this module reuses W2-53's support (imported by
  path, unchanged), which reuses W2-01's and W1-30's; their sandbox puts the ``src/`` beside this file's
  ``tests/`` first on every process's ``PYTHONPATH``. This module asserts that they agree.
- **Every project is a temporary git repository built from scratch** (W2-01's ``Project``): single named files
  only, no folder of this repository.
- **"No test ran" is seen from outside**: the ticket's acceptance test and a regression test of the project are
  telling tests (W1-30's ``telling_test``), which write a file into a folder outside the project each time they
  run. A gate that refuses before any test leaves that folder empty.
- **Deterministic, no network.**
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parent
_W2_53 = str(_HERE.parent / "W2-53")
if _W2_53 not in sys.path:
    sys.path.insert(0, _W2_53)

import w2_53_support as w253  # noqa: E402  (W2-53's support: the lists of the path map, entries)

w201 = w253.w201
base = w253.base
cli_support = base.cli_support

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
assert w253.SRC == SRC and w201.SRC == SRC and base.SRC == SRC, \
    "W2-53's, W2-01's and W1-30's support must run the same src/ as this suite"

EXIT_OK = base.EXIT_OK
EXIT_GOV_ERROR = base.EXIT_GOV_ERROR
EXIT_CHECK_FAILED = base.EXIT_CHECK_FAILED
EXIT_BLOCKED = base.EXIT_BLOCKED

OWNER = base.OWNER
ORCHESTRATOR = base.ORCHESTRATOR
IMPLEMENTER = base.IMPLEMENTER
TEST_DESIGNER = base.TEST_DESIGNER
AGENT = base.AGENT

PATH_MAP_REL = base.PATH_MAP_REL
CHECKS_REL = base.CHECKS_REL
REGISTER = w201.REGISTER
REGISTER_KEY = w201.REGISTER_KEY
ACCEPTED_KEY = w201.ACCEPTED_KEY
CAPABILITY = w201.CAPABILITY
OWNER_ACCEPTED = "ACCEPTED (owner, 2026-10-22)"
PROPOSED = "PROPOSED"

# --------------------------------------------------------------------------
# The forms this suite assumes (README, "Interface assumptions")
# --------------------------------------------------------------------------

# A1. A ticket names the evidence its class is judged on in its ``acceptance_tests`` mapping, under ``evidence``:
# a list of paths relative to the project's root. (Real tickets already say ``acceptance_tests.judged_by``.)
EVIDENCE_KEY = "evidence"
# A2. The disk floors are top-level keys of the path map, as ``close_timeout`` and ``close_workers`` are
# (DEC-549); without them the floors are DEC-898's: 100 GiB and 10,000,000 inodes free.
FLOOR_GIB_KEY = "close_free_gib_floor"
FLOOR_INODES_KEY = "close_free_inodes_floor"
DEFAULT_FLOOR_GIB = 100
DEFAULT_FLOOR_INODES = 10_000_000
# A3. A probe record lists its findings in its frontmatter, under ``findings``: a list of finding ids.
PROBE_FINDINGS_KEY = "findings"

# The suite's own floors: low, so that no case depends on how full this machine's disk is (README).
SUITE_SETTINGS = {**w201.SUITE_SETTINGS, FLOOR_GIB_KEY: 1, FLOOR_INODES_KEY: 1}

# The class names of the KPI (the ticket file's ``class``) and the role whose commits do each class's work.
CLASS_ROLES = {
    "implementation": "engineer",
    "specification": "product-spec",
    "audit": "independent-auditor",
    "research": "research",
    "integration": "orchestrator",
    "coordination": "orchestrator",
    "test-revision": "independent-test-designer",
}

# The telling tests: one in the ticket's acceptance folder, one in the regression (``tests/unit/``).
ACCEPTANCE_MARK = "test_w207_acceptance_mark"
REGRESSION_MARK = "test_w207_regression_mark"
REGRESSION_MARK_REL = f"tests/unit/{REGRESSION_MARK}.py"
REGRESSION_MARK_ID = f"{REGRESSION_MARK_REL}::{REGRESSION_MARK}"

ITERATION_DIR = base.ITERATION_DIR
ESCALATION_DIR = base.ESCALATION_DIR

trailers_of = w201.trailers_of
git = w201.git
head_of = w201.head_of
checkpointed = w201.checkpointed
probe_recorded = w201.probe_recorded
text_of = w201.text_of
findings_of = w201.findings_of
codes_of = w201.codes_of
strings_of = w201.strings_of
iteration_count = base.iteration_count
other_tickets = base.other_tickets
frontmatter_of = base.frontmatter_of
ticket_status = base.ticket_status
commit_what_a_refusal_left = base.commit_what_a_refusal_left
red_entry = w253.red_entry
quarantine_entry = w253.quarantine_entry


def path_map_text(settings):
    """W2-53's path map text: the plain keys, the accepted history and the two ratchet lists."""
    return w253.path_map_text(settings)


# --------------------------------------------------------------------------
# The project
# --------------------------------------------------------------------------

class Project(w201.Project):
    """W2-01's project (built from scratch, its register named by the path map), with this suite's settings and
    a folder outside it, ``told``, where its telling tests tell that they ran."""

    def __init__(self, root, settings=None):
        root = Path(root)
        self.told = root.parent / f"{root.name}-told"
        self.told.mkdir(parents=True, exist_ok=True)
        super().__init__(root, settings=dict(SUITE_SETTINGS if settings is None else settings))

    def _init_minimal(self):
        super()._init_minimal()
        # W2-01's project wrote its path map with W2-01's writer: the lists of this suite need W2-53's.
        self.write(PATH_MAP_REL, path_map_text(self.settings))
        if self.waiting_paths():
            base.commit_all(self.root, "the path map", who=OWNER, trailers=("Task: setup", "Role: owner"))

    def set_path_map(self, commit=True, **settings):
        """The path map gains (or loses, for a value ``None``) ``settings``; committed by the owner outside any
        ticket."""
        for key, value in settings.items():
            if value is None:
                self.settings.pop(key, None)
            else:
                self.settings[key] = value
        self.write(PATH_MAP_REL, path_map_text(self.settings))
        if commit:
            return self.setup_commit("the project's path map")
        return None

    def setup_commit(self, message="setup"):
        """What the working tree holds, committed by the owner outside any ticket."""
        return self.commit(message, who=OWNER, trailers=("Task: setup", "Role: owner"), exact=True)

    def telling(self, rel, name):
        """A telling test file at ``rel`` whose one test is ``name``."""
        self.write(rel, base.telling_test(name, self.told))

    def ran(self):
        """The telling tests that ran, by name; empty when none did."""
        return sorted(path.name for path in self.told.iterdir())

    def register_entry(self, decision_id, status, text):
        """An entry appended to the project's register (DEC-473's heading, a status line), not committed."""
        path = self.root / REGISTER
        entry = (f"### {decision_id} — A decision of the fixture\n"
                 f"- **Status:** {status} · **Basis:** the fixture\n"
                 f"- **Decision:** {text}\n\n")
        self.write(REGISTER, path.read_text(encoding="utf-8") + entry)

    def add_check(self, check_id, command, severity="hard-block", family="schema/invariants", tier="G1"):
        """A check declaration of the project (W1-26's form), not committed."""
        text = "\n".join(f'{field}: "{value}"' for field, value in [
            ("id", check_id), ("family", family), ("tier", tier), ("severity", severity), ("command", command),
        ]) + "\n"
        self.write(f"{CHECKS_REL}/{check_id}.yaml", text)


def with_regression_mark(project):
    """The project gains a passing regression test that tells when it runs, committed by the owner."""
    project.telling(REGRESSION_MARK_REL, REGRESSION_MARK)
    return project.setup_commit("a regression test")


# --------------------------------------------------------------------------
# Ticket files
# --------------------------------------------------------------------------

def ticket_text(ticket, wbs, cls="implementation", role=None, allowed_paths=("src/example/**",), profile="STANDARD",
                acceptance=None, status="in_progress", **keys):
    """A ticket file as this repository writes them: tk's own fields, then the task contract. ``acceptance`` is
    the ``acceptance_tests`` mapping (default: the ticket's own folder, ``tests/acceptance/<wbs>/``); ``keys``
    are further top-level keys."""
    front = {
        "id": ticket, "status": status, "deps": [], "links": [], "created": "2026-09-01T12:00:00Z",
        "type": "task", "priority": 2, "assignee": role or CLASS_ROLES.get(cls, "engineer"),
        "external-ref": wbs, "tags": ["test"], "wbs_id": wbs, "title": f"Ticket {wbs}",
        "class": cls, "state_class": "AUTHORITATIVE", "role": role or CLASS_ROLES.get(cls, "engineer"),
        "depends_on": [], "allowed_paths": list(allowed_paths),
        "kpis": {"success": ["It works"], "failure": ["It does not work"]},
        "profile": profile, "sources": [base.BASE_SOURCE], "est_loc": 10,
    }
    front.update(keys)
    front["acceptance_tests"] = acceptance if acceptance is not None else {
        "path": f"tests/acceptance/{wbs}/", "author": "independent-test-designer; written before implementation"}
    text = yaml.safe_dump(front, sort_keys=False, allow_unicode=True, default_flow_style=False)
    return "---\n" + text + f"---\n# {wbs} A ticket\n\nBody text.\n"


def judged_by_class(cls, evidence):
    """The ``acceptance_tests`` mapping of a ticket judged by its class (no acceptance tests of its own), naming
    its evidence (assumption A1)."""
    return {"judged_by": f"its class (WBS §0 rule 1, W2-07): its {cls} evidence", EVIDENCE_KEY: list(evidence)}


def create_ticket(project, ticket, wbs, cls="implementation", allowed_paths=("src/example/**",), profile="STANDARD",
                  acceptance=None, tests=True, **keys):
    """The orchestrator's ticket-creating commit (the ticket file alone, with every trailer), then, with
    ``tests``, the test designer's commit of the ticket's acceptance folder holding one telling test. Returns the
    creating commit."""
    project.write(base.ticket_path(ticket), ticket_text(ticket, wbs, cls=cls, allowed_paths=allowed_paths,
                                                         profile=profile, acceptance=acceptance, **keys))
    created = project._commit(f"ticket {ticket} created", ORCHESTRATOR, trailers_of(ticket, role="orchestrator"),
                              [base.ticket_path(ticket)])
    if tests:
        project.write(f"tests/acceptance/{wbs}/README.md", f"# {wbs}\n")
        project.telling(f"tests/acceptance/{wbs}/{ACCEPTANCE_MARK}.py", ACCEPTANCE_MARK)
        project.commit("acceptance tests", who=TEST_DESIGNER,
                       trailers=trailers_of(ticket, role="independent-test-designer"), exact=True)
    return created


def work(project, ticket, files, role="engineer", trailers=None, who=None, message="work on the ticket"):
    """One commit of the ticket's work that writes ``files`` (``{path: text}``) with ``role``'s trailers."""
    for rel, text in files.items():
        project.write(rel, text)
    effective = trailers_of(ticket, role=role) if trailers is None else trailers
    who = who or (IMPLEMENTER if role == "engineer" else ORCHESTRATOR if role == "orchestrator" else AGENT)
    return project.commit(message, who=who, trailers=effective, exact=True)


def ready_ticket(project, ticket, wbs, profile="STANDARD", allowed_paths=("src/example/**",)):
    """A ticket whose work is done and checkpointed: created, its telling acceptance test, the engineer's
    commit, the orchestrator's checkpoint. Returns the engineer's commit."""
    create_ticket(project, ticket, wbs, profile=profile, allowed_paths=allowed_paths)
    done = work(project, ticket, {"src/example/feature.py": "# feature\n"})
    checkpointed(project, ticket)
    return done


# --------------------------------------------------------------------------
# Records a class is judged on
# --------------------------------------------------------------------------

def research_record(record_id, title="An evidence record"):
    """An evidence record as this repository writes them (``docs/research/*.md``: ``type: research``,
    ``state_class: EVIDENCE``)."""
    front = {"id": record_id, "type": "research", "status": "ACTIVE", "state_class": "EVIDENCE", "title": title}
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + f"---\n\n# {title}\n\nWhat was run, and what it showed.\n"


def audit_report(commit, rows, milestone="W9-audit"):
    """An audit report in DEC-441's form: ``milestone``, ``commit``, ``pack_sha256`` and a three-column table of
    ``(item, class, evidence)`` rows."""
    front = {"milestone": milestone, "commit": commit, "pack_sha256": "a" * 64}
    table = "| Item | Class | Evidence |\n|---|---|---|\n" + "".join(f"| {i} | {c} | {e} |\n" for i, c, e in rows)
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n# Audit report\n\n" + table


def audit_validator(project, sandbox, rel):
    """The audit validator's own answer on ``rel`` in the project (``python3 -m gov.check.audit_validator``):
    its exit code. A fixture check only."""
    done = subprocess.run([sys.executable, "-m", "gov.check.audit_validator", rel], cwd=str(project.root),
                          env=base.sandbox_env(sandbox), capture_output=True, text=True, stdin=subprocess.DEVNULL,
                          timeout=120)
    return done.returncode, done.stdout + done.stderr


READINESS_SCHEMA_REL = "openspec/schemas/feature-readiness/schema.yaml"
READINESS_KEYS = (
    "intent", "actor", "journey", "scenarios", "inputs", "data_model", "test_data", "processing", "outputs",
    "functional", "nfr", "ux", "backend", "state", "interfaces", "security", "integrations", "devops",
    "observability", "performance", "cost", "recovery", "success", "failure", "acceptance_tests", "docs_ops")


def specification_files(spec_id, change, open_rows=()):
    """``{path: text}`` of a LITE specification record (``openspec/changes/<change>/proposal.md``) and its
    readiness record: every row PRESENT with evidence, but the rows numbered in ``open_rows``, which are
    MISSING."""
    front = {"id": spec_id, "type": "specification", "status": "ACTIVE", "state_class": "AUTHORITATIVE",
             "title": f"Specification {spec_id}", "profile": "LITE", "spine": False, "capability_types": []}
    proposal = "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n# Proposal\n\n## Why\n\nA fixture.\n"
    rows = []
    for n, key in enumerate(READINESS_KEYS, 1):
        if n in open_rows:
            rows.append({"n": n, "key": key, "state": "MISSING", "evidence": [], "gap_ticket": "UNLINKED"})
        else:
            rows.append({"n": n, "key": key, "state": "PRESENT", "evidence": [f"openspec/changes/{change}/proposal.md"]})
    readiness = "# Feature-readiness record.\n" + yaml.safe_dump({"rows": rows}, sort_keys=False)
    folder = f"openspec/changes/{change}"
    return {f"{folder}/.openspec.yaml": "schema: feature-readiness\n", f"{folder}/proposal.md": proposal,
            f"{folder}/readiness.yaml": readiness}


def readiness_schema_text():
    """The text of the feature-readiness schema of OpenSpec as the kernel's template ships it: a single named
    file, which ``gov readiness`` needs in the project."""
    return (REPO_ROOT / "template" / "openspec" / "schemas" / "feature-readiness" / "schema.yaml").read_text(
        encoding="utf-8")


def readiness(project, sandbox, ticket):
    """``gov readiness --ticket <ticket> --json`` in the project: its exit code. A fixture check only."""
    return project.gov(sandbox, "readiness", "--ticket", ticket, "--json").returncode


# --------------------------------------------------------------------------
# Running and reading
# --------------------------------------------------------------------------

def run_close(project, sandbox, ticket, *args, env=None):
    return base.run_close(project, sandbox, ticket, *args, env=env)


def closed(run, interface):
    """The close succeeded: exit code 0, ``ok`` true, no ``--disposition`` given. Returns the result."""
    assert "--disposition" not in run.args, "the fixture is wrong: a clean close is given no disposition"
    return base.result_of(run, interface)


def refused(run, interface):
    """The close was refused (``ok`` false, a non-zero exit code, not ``NOT_IMPLEMENTED``). Returns ``error``."""
    envelope = base.envelope_of(run, interface)
    assert envelope["ok"] is False, f"gov close was not refused\n{run.describe()}"
    assert run.returncode != EXIT_OK, f"a refused close ended with exit code 0\n{run.describe()}"
    return envelope["error"]


def names(error, *words):
    """Whether the refusal names every one of ``words`` (a code, an id, a word), case not held, anywhere in it."""
    text = text_of(error).lower()
    return all(word.lower() in text for word in words)


def names_any(error, *words):
    text = text_of(error).lower()
    return any(word.lower() in text for word in words)


def assert_no_test_ran(project, run, which=None):
    """No telling test of the project ran (``which``: only these names are looked for)."""
    ran = project.ran()
    if which is not None:
        ran = [name for name in ran if name in which]
    assert not ran, f"tests ran before the close refused: {ran}\n{run.describe()}"


def assert_no_attempt_spent(project, ticket, run, count=0):
    """The refusal spent no ratchet attempt: the ticket's iteration count is still ``count``, and no escalation
    was written."""
    assert iteration_count(project.root, ticket) == count, (
        f"the refusal spent an attempt: the count is {iteration_count(project.root, ticket)}, not {count}\n"
        f"{run.describe()}")
    assert not (project.root / ESCALATION_DIR / f"{ticket}.json").exists(), \
        f"the refusal wrote an escalation\n{run.describe()}"


def tracked(project, rel):
    """Whether git knows ``rel`` (it is in the index or in ``HEAD``)."""
    return bool(git(project, "ls-files", "--", rel).strip())


def ticket_schema_errors(front):
    """The errors of ``front`` (a ticket's frontmatter) against the kernel's ticket schema, as messages."""
    import jsonschema

    folder = REPO_ROOT / "template" / "governance" / "kernel" / "schemas"
    schema = json.loads((folder / "ticket.schema.json").read_text(encoding="utf-8"))
    resolver = jsonschema.RefResolver(base_uri=folder.as_uri() + "/", referrer=schema)
    plain = json.loads(json.dumps(front, default=str))
    validator = jsonschema.Draft202012Validator(schema, resolver=resolver)
    return [f"{'/'.join(map(str, error.path)) or '(root)'}: {error.message}" for error in validator.iter_errors(plain)]


# --------------------------------------------------------------------------
# A ticket tool that is interrupted while it closes the ticket (W2-M158)
# --------------------------------------------------------------------------

INTERRUPTING_TOOL = r"""#!/usr/bin/env python3
# A stand-in of the ticket tool: "close" kills the gov close that called it, as an interruption would
# (SIGKILL: nothing of the close runs after it); every other command is the real tool's.
import os, signal, sys
REAL = {real!r}
if len(sys.argv) > 1 and sys.argv[1] == "close":
    pid = os.getppid()
    while pid > 1:
        try:
            with open(f"/proc/{{pid}}/cmdline", "rb") as handle:
                words = handle.read().split(b"\0")
            with open(f"/proc/{{pid}}/stat", encoding="utf-8") as handle:
                parent = int(handle.read().rsplit(")", 1)[1].split()[1])
        except OSError:
            break
        if b"close" in words and {ticket!r}.encode() in words:
            os.kill(pid, signal.SIGKILL)
            sys.exit(1)
        pid = parent
    sys.exit(1)
os.execv(REAL, [REAL, *sys.argv[1:]])
"""


def install_interrupting_tool(project, ticket, keep):
    """The project's ticket tool becomes ``INTERRUPTING_TOOL``; the real one is kept at ``keep`` (outside the
    project). Committed by the owner outside any ticket."""
    tool = project.root / "governance" / "kernel" / "bin" / "tk"
    keep = Path(keep)
    keep.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(tool, keep)
    keep.chmod(0o755)
    tool.write_text(INTERRUPTING_TOOL.format(real=str(keep), ticket=ticket), encoding="utf-8")
    tool.chmod(0o755)
    return project.setup_commit("an interrupting ticket tool")


def restore_tool(project, keep):
    """The real ticket tool back in the project, in a commit of the owner that holds the tool's file alone: what an
    interrupted close left in the working tree is not committed by it."""
    rel = "governance/kernel/bin/tk"
    tool = project.root / rel
    shutil.copy2(keep, tool)
    tool.chmod(0o755)
    return project._commit("the ticket tool restored", OWNER, ("Task: setup", "Role: owner"), [rel])


def free_on_disk(root):
    """``(free GiB, free inodes)`` of the file system that holds ``root``, as an unprivileged process sees it."""
    stat = os.statvfs(root)
    return stat.f_bavail * stat.f_frsize / 2**30, stat.f_favail
