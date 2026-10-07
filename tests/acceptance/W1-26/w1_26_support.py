"""Support code for the W1-26 acceptance tests (``gov check``).

W1-26 builds the ``gov check`` command: it runs every declared check, reports
each of the 17 governance test families as RED/YELLOW/GREEN, records provenance,
and fails planted defects.

How the tests run:

- **Through public interfaces only**: the ``gov check`` command line (W1-07's
  console-script stand-in), its API-0002 envelope and exit code; and the Python
  functions ``gov.decisions.checker.check``, ``gov.readiness.checker.check``,
  ``gov.store.load``, each called through the CLI or in a new process.
- **Nothing is written in this worktree** (DEC-322). Every project is a
  temporary git repository: its own ``.tickets/``, its own ``openspec/`` (a copy
  of ``template/openspec/``), its own store, and whatever records the test plants.
  The code under test is this worktree's ``src/``.
- **Before ``gov check`` runs, the project is committed**, so the checker may
  read from the working tree or the record graph.
- **Deterministic, no network.** External tools (``openspec``, ``gitleaks``) are
  never on PATH unless a test provides a stand-in.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
for _name in ("W1-07", "W1-09", "W1-11", "W1-13"):
    _folder = str(_HERE.parent / _name)
    if _folder not in sys.path:
        sys.path.insert(0, _folder)

import w1_07_support as cli_support  # noqa: E402
import w1_09_support as tasks_support  # noqa: E402
import w1_11_support as decisions_support  # noqa: E402
import w1_13_support as readiness_support  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
COMMAND = "check"
NOT_IMPLEMENTED = cli_support.NOT_IMPLEMENTED
CHECKS_REL = cli_support.CHECKS_REL
TEMPLATE_OPENSPEC = readiness_support.TEMPLATE_OPENSPEC

# The 17 governance test families (CAP-38.b, Contract v3 O2).
FAMILIES = (
    "schema/invariants",
    "graph integrity",
    "index freshness",
    "retrieval regression",
    "authority/role limits",
    "mutation scope",
    "path-map compliance",
    "context reproducibility",
    "concurrency/claims",
    "adapter/model portability",
    "skill regression",
    "command-contract consistency",
    "secrets indexing",
    "recovery/rebuild",
    "fresh-agent reconstruction",
    "product traceability",
    "audit reproducibility",
)
assert len(FAMILIES) == 17

# The 7 core checks this ticket registers.
CORE_CHECKS = {
    "core-schema": {"family": "schema/invariants", "tier": "G1", "severity": "hard-block",
                    "command": "python3 -m gov.check.schema"},
    "core-graph": {"family": "graph integrity", "tier": "G1", "severity": "hard-block",
                   "command": "python3 -m gov.check.graph"},
    "core-authority": {"family": "authority/role limits", "tier": "G1", "severity": "hard-block",
                       "command": "python3 -m gov.check.authority"},
    "core-mutation": {"family": "mutation scope", "tier": "G1", "severity": "hard-block",
                      "command": "python3 -m gov.check.mutation"},
    "core-pathmap": {"family": "path-map compliance", "tier": "G1", "severity": "hard-block",
                     "command": "python3 -m gov.check.pathmap"},
    "core-claims": {"family": "concurrency/claims", "tier": "G1", "severity": "hard-block",
                    "command": "python3 -m gov.check.claims"},
    "core-commands": {"family": "command-contract consistency", "tier": "G2", "severity": "warning",
                      "command": "python3 -m gov.check.commands"},
}

# The 3 checks already declared by other tickets.
ALREADY_DECLARED = ("index-freshness", "secrets-indexing", "fresh-agent-reconstruction")

# The 7 families not yet registered by any ticket.
NOT_YET_REGISTERED = (
    "retrieval regression",
    "context reproducibility",
    "adapter/model portability",
    "skill regression",
    "recovery/rebuild",
    "product traceability",
    "audit reproducibility",
)

# Status values for check results.
RED, YELLOW, GREEN = "RED", "YELLOW", "GREEN"
HARD_BLOCK, WARNING = "hard-block", "warning"

# Reserved commands (from W1-07).
RESERVED_COMMANDS = cli_support.RESERVED_COMMANDS

# Exit codes.
EXIT_OK = 0
EXIT_GOV_ERROR = 1
EXIT_CHECK_FAILED = 3  # API-0002: verification failed / unhealthy

# Policies from path-map.yaml (D-0003).
POLICIES = {
    "security": "hard-block",
    "authority": "hard-block",
    "test": "hard-block",
    "change": "hard-block",
    "human_gate": "hard-block",
    "tool": "hard-block",
    "memory": "warning",
    "context": "warning",
    "checkpoint": "warning",
    "model_routing": "informational",
    "budget": "informational",
    "learning": "informational",
    "archive": "informational",
}

CALL_TIMEOUT_S = 60.0

# Schema files for records in this repository.
TICKET_SCHEMA = "template/governance/kernel/schemas/ticket.schema.json"
DECISION_SCHEMA = "template/governance/kernel/schemas/madr.schema.json"
PATH_MAP_REL = cli_support.PATH_MAP_REL
READINESS_DIMENSIONS_REL = "docs/contract/readiness-dimensions.yaml"

# Check declaration fields.
CHECK_FIELDS = ("id", "family", "tier", "severity", "command")


# --------------------------------------------------------------------------
# git and the temporary project
# --------------------------------------------------------------------------

OWNER = decisions_support.OWNER
AGENT = decisions_support.AGENT
FIRST_DATE = decisions_support.FIRST_DATE


def git(project, *args, who=AGENT, check=True):
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(Path(project).parent),
        "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_AUTHOR_NAME": who["name"], "GIT_AUTHOR_EMAIL": who["email"],
        "GIT_COMMITTER_NAME": who["name"], "GIT_COMMITTER_EMAIL": who["email"],
        "GIT_AUTHOR_DATE": FIRST_DATE.format(minute=0),
        "GIT_COMMITTER_DATE": FIRST_DATE.format(minute=0),
    }
    done = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True, env=env)
    if check and done.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {project}:\n{done.stderr}")
    return done.stdout


def write(root, rel, text):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def commit_all(project, message="fixture", who=OWNER):
    git(project, "add", "-A", who=who)
    git(project, "commit", "-q", "--allow-empty", "-m", message, who=who)
    return git(project, "rev-parse", "HEAD", who=who).strip()


# --------------------------------------------------------------------------
# Record helpers
# --------------------------------------------------------------------------

def record(record_id, record_type, status, title=None, **keys):
    if title is None:
        title = f"Record {record_id}"
    return decisions_support.record(record_id, record_type, status, title=title, **keys)


def decision(record_id, status, **keys):
    return decisions_support.decision(record_id, status, **keys)


def ticket_text(ticket_id, wbs, **keys):
    return tasks_support.ticket_text(ticket_id, wbs, **keys)


def ticket_path(ticket_id):
    return f".tickets/{ticket_id}.md"


def adr_path(record_id):
    return f"docs/adr/{record_id}.md"


# --------------------------------------------------------------------------
# Skill file helpers
# --------------------------------------------------------------------------

def skill_file(name, version, content_marker="default content"):
    return (f"---\nid: {name}\ntype: skill\nstatus: ACTIVE\nstate_class: AUTHORITATIVE\n"
            f"version: {version}\ntitle: Skill {name}\n---\n# {name}\n\n{content_marker}\n")


# --------------------------------------------------------------------------
# A temporary project for gov check
# --------------------------------------------------------------------------

class Project:
    """A temporary git repository that gov check can run in."""

    def __init__(self, root, copy_tree=False):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        if copy_tree:
            cli_support.copy_working_tree(self.root)
        else:
            self._init_minimal()

    def _init_minimal(self):
        git(self.root, "init", "-q", "-b", "main")
        write(self.root, "README.md", "# A project\n")
        write(self.root, ".gitignore", ".gov-runtime/\n")
        write(self.root, "pyproject.toml",
              (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        shutil.copytree(REPO_ROOT / "src", self.root / "src")
        self._copy_kernel_templates()
        commit_all(self.root, "initial project")

    def _copy_kernel_templates(self):
        checks_src = REPO_ROOT / CHECKS_REL
        checks_dst = self.root / CHECKS_REL
        if checks_src.is_dir():
            shutil.copytree(checks_src, checks_dst, dirs_exist_ok=True)
        schemas_src = REPO_ROOT / "template" / "governance" / "kernel" / "schemas"
        schemas_dst = self.root / "template" / "governance" / "kernel" / "schemas"
        if schemas_src.is_dir():
            shutil.copytree(schemas_src, schemas_dst, dirs_exist_ok=True)
        skills_src = REPO_ROOT / "template" / "governance" / "kernel" / "skills"
        skills_dst = self.root / "template" / "governance" / "kernel" / "skills"
        if skills_src.is_dir():
            shutil.copytree(skills_src, skills_dst, dirs_exist_ok=True)
        if TEMPLATE_OPENSPEC.is_dir():
            shutil.copytree(TEMPLATE_OPENSPEC, self.root / "openspec", dirs_exist_ok=True)

    def write(self, rel, text):
        return write(self.root, rel, text)

    def commit(self, message="fixture"):
        return commit_all(self.root, message)

    def add_check_declaration(self, check_id, family, tier="G1", severity="hard-block",
                              command="true"):
        text = "\n".join(f'{field}: "{value}"' for field, value in [
            ("id", check_id), ("family", family), ("tier", tier),
            ("severity", severity), ("command", command),
        ]) + "\n"
        write(self.root, f"{CHECKS_REL}/{check_id}.yaml", text)
        return check_id

    def add_core_declarations(self):
        for check_id, decl in CORE_CHECKS.items():
            self.add_check_declaration(check_id, **decl)

    def remove_check_declaration(self, check_id):
        path = self.root / CHECKS_REL / f"{check_id}.yaml"
        if path.exists():
            path.unlink()

    def add_ticket(self, ticket_id, wbs, **keys):
        write(self.root, ticket_path(ticket_id), ticket_text(ticket_id, wbs, **keys))
        tests_dir = self.root / "tests" / "acceptance" / wbs
        tests_dir.mkdir(parents=True, exist_ok=True)
        write(self.root, f"tests/acceptance/{wbs}/README.md", f"# {wbs}\n")
        return ticket_id

    def add_record(self, rel, record_id, record_type, status, **keys):
        write(self.root, rel, record(record_id, record_type, status, **keys))
        return rel

    def add_decision(self, record_id, status, **keys):
        rel = adr_path(record_id)
        write(self.root, rel, decision(record_id, status, **keys))
        return rel

    def add_skill(self, name, version, content_marker="default content"):
        rel = f"template/governance/kernel/vendor/{name}.md"
        write(self.root, rel, skill_file(name, version, content_marker))
        return rel

    def add_specification(self, rows, spec_id="SPEC-zz01", change="zz01-fixture",
                          profile="FULL", spine=False, status="DRAFT"):
        folder = f"openspec/changes/{change}"
        write(self.root, f"{folder}/.openspec.yaml", "schema: feature-readiness\n")
        front = (f"---\nid: {spec_id}\ntype: specification\nstatus: {status}\n"
                 f"state_class: AUTHORITATIVE\ntitle: Specification {spec_id}\n"
                 f"profile: {profile}\nspine: {'true' if spine else 'false'}\n"
                 f"capability_types: []\n---\n# Proposal\n\nA fixture.\n")
        write(self.root, f"{folder}/proposal.md", front)
        import yaml
        text = "# Readiness record.\n" + yaml.safe_dump({"rows": rows}, sort_keys=False)
        write(self.root, f"{folder}/readiness.yaml", text)
        return spec_id

    def add_path_map(self, namespaces):
        """Write a path-map.yaml that defines the given namespaces: name -> list of globs."""
        import yaml
        data = {
            "version": 1,
            "namespaces": {name: {"paths": paths, "sensitivity": "internal",
                                  "permitted_roles": ["engineer"],
                                  "retention": "permanent", "export_policy": "allowed",
                                  "embedding_policy": "not embedded",
                                  "provenance": "fixture",
                                  "deletion_rebuild": "from git"}
                          for name, paths in namespaces.items()},
            "policies": dict(POLICIES),
        }
        write(self.root, PATH_MAP_REL, yaml.safe_dump(data, sort_keys=False))

    def add_readiness_dimensions(self):
        src = REPO_ROOT / READINESS_DIMENSIONS_REL
        if src.is_file():
            (self.root / READINESS_DIMENSIONS_REL).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, self.root / READINESS_DIMENSIONS_REL)

    def gov(self, sandbox, *args):
        return cli_support.run_gov_with_code(REPO_ROOT, self.root, sandbox, *args)


# --------------------------------------------------------------------------
# Full-tree project (copies the working tree)
# --------------------------------------------------------------------------

class FullProject:
    """A copy of the working tree, committed, with its own store: for tests that need the real project shape."""

    def __init__(self, root):
        self.root = Path(root)
        cli_support.copy_working_tree(self.root)

    def write(self, rel, text):
        return write(self.root, rel, text)

    def commit(self, message="fixture"):
        return commit_all(self.root, message)

    def gov(self, sandbox, *args):
        return cli_support.run_gov_with_code(REPO_ROOT, self.root, sandbox, *args)


# --------------------------------------------------------------------------
# Parsing gov check results
# --------------------------------------------------------------------------

def run_check(project, sandbox, *extra_args):
    """Run ``gov check --json`` and return the Run."""
    return project.gov(sandbox, COMMAND, "--json", *extra_args)


def envelope_of(run, interface):
    """Parse the API-0002 envelope and assert basic structure."""
    envelope = cli_support.assert_envelope(run, interface, command=COMMAND)
    code = (envelope.get("error") or {}).get("code")
    assert code != NOT_IMPLEMENTED, f"gov check is not built yet\n{run.describe()}"
    return envelope


def result_of(run, interface):
    """The result dict when gov check succeeds."""
    envelope = envelope_of(run, interface)
    assert envelope["ok"] is True, f"gov check did not succeed\n{run.describe()}"
    assert run.returncode == EXIT_OK, f"exit code is not 0\n{run.describe()}"
    return envelope["result"]


def families_of(result):
    """Extract the per-family status dict from a check result: family name -> status."""
    families = result.get("families") or result.get("checks") or {}
    if isinstance(families, list):
        return {entry["family"]: entry for entry in families}
    return families


def checks_of(result):
    """Extract the per-check results from a check result."""
    return result.get("checks") or result.get("results") or []


def family_status(result, family_name):
    """The status of one family in a check result."""
    fam = families_of(result)
    if isinstance(fam, dict) and family_name in fam:
        entry = fam[family_name]
        if isinstance(entry, dict):
            return entry.get("status")
        return entry
    return None


def provenance_of(check_result):
    """The provenance dict from a check result entry."""
    if isinstance(check_result, dict):
        return check_result.get("provenance") or {}
    return {}


def finding_codes(result):
    """All finding codes from a check result."""
    codes = set()
    for entry in checks_of(result):
        if isinstance(entry, dict):
            for finding in entry.get("findings", []):
                if isinstance(finding, dict) and "code" in finding:
                    codes.add(finding["code"])
    return codes


# --------------------------------------------------------------------------
# Assertions
# --------------------------------------------------------------------------

def assert_red(run, interface):
    """The run failed with at least one hard-block RED."""
    envelope = envelope_of(run, interface)
    assert envelope["ok"] is False or run.returncode != EXIT_OK, \
        f"gov check passed but a hard-block RED was expected\n{run.describe()}"
    return envelope


def assert_green(run, interface):
    """The run succeeded: all checks GREEN."""
    envelope = envelope_of(run, interface)
    assert envelope["ok"] is True and run.returncode == EXIT_OK, \
        f"gov check did not pass\n{run.describe()}"
    return envelope


def assert_family_red(result, family_name):
    """The family is RED in the check result."""
    status = family_status(result, family_name)
    assert status == RED, f"family {family_name!r} is {status!r}, expected RED"


def assert_family_green(result, family_name):
    """The family is GREEN in the check result."""
    status = family_status(result, family_name)
    assert status == GREEN, f"family {family_name!r} is {status!r}, expected GREEN"


def assert_family_present(result, family_name):
    """The family is named in the check result (any status)."""
    fam = families_of(result)
    assert family_name in fam, f"family {family_name!r} is not in the result: {sorted(fam)}"


def assert_all_families_named(result):
    """All 17 families are named in the result."""
    fam = families_of(result)
    for family in FAMILIES:
        assert family in fam, f"family {family!r} is not named in the result: {sorted(fam)}"


# --------------------------------------------------------------------------
# Fresh readiness rows (from W1-13)
# --------------------------------------------------------------------------

def fresh_rows():
    return readiness_support.fresh_rows()


def satisfy(rows, numbers):
    return readiness_support.satisfy(rows, numbers)


def complete_rows(profile="FULL"):
    return readiness_support.complete_rows(profile)
