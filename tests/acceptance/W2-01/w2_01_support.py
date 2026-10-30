"""Support code for the W2-01 acceptance tests (``gov close`` and product traceability).

W2-01 (DAEO-g0ip): ``gov close``'s own trailer gate reads the project's ``trailers_base``; a merge of the
integration branch into a ticket branch in DEC-436's merge form passes it; history that an ACCEPTED owner
decision names is accepted history (DEC-734); the probe gate after a merge-back and on a reopened ticket.

How the tests run (README, "How the tests run"):

- **Through public interfaces only**: ``gov close <ticket> --json`` and ``gov check --json`` (API-0002
  envelope, exit codes, findings by code), the command the trailers check's declaration names, the project's
  path map, ticket files, probe records, the decision register and commit trailers.
- **The code under test is this worktree's ``src/``** (DEC-732): every ``gov`` process gets the ``src/``
  folder beside this file's ``tests/`` on its ``PYTHONPATH`` (W1-07's console-script stand-in and
  ``sandbox_env``, both of which derive it from the support file's own location).
- **Every project is a temporary git repository built from scratch** with the commits its case needs. No
  folder of this repository is copied into it: it receives single named files only (the ticket tool, the
  trailers check's declaration). This repository's history and path map are never read by a case.
- **Deterministic, no network.**
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_W1_30 = str(_HERE.parent / "W1-30")
if _W1_30 not in sys.path:
    sys.path.insert(0, _W1_30)

import w1_30_support as base  # noqa: E402  (W1-30's public support: git, tickets, probe records, run_gov)

cli_support = base.cli_support

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
assert base.SRC == SRC, "W1-30's support must run the same src/ as this suite"

EXIT_OK = base.EXIT_OK
EXIT_GOV_ERROR = base.EXIT_GOV_ERROR
EXIT_CHECK_FAILED = base.EXIT_CHECK_FAILED

OWNER = base.OWNER
ORCHESTRATOR = base.ORCHESTRATOR
IMPLEMENTER = base.IMPLEMENTER
TEST_DESIGNER = base.TEST_DESIGNER
AGENT = base.AGENT

PATH_MAP_REL = base.PATH_MAP_REL
CHECKS_REL = base.CHECKS_REL
TRAILERS_CHECK = "product-traceability-trailers"
TRAILERS_CHECK_FILE = f"{TRAILERS_CHECK}.yaml"

# The keys of the path map (DEC-479, DEC-482; DEC-734 and README, "Accepted history").
BASE_KEY = "trailers_base"
REGISTER_KEY = "decision_register"
ACCEPTED_KEY = "accepted_history"
REGISTER = "docs/DECISION_REGISTER.md"

# What the answers say (README, "The forms this suite fixes").
ACCEPTED_FIELD = "accepted_history"          # the list of accepted commits in an answer
BASE_FIELD = "trailers_base"                 # the base used, in an answer
MOVED_COUNT_FIELD = "commits_out_of_judgement"
HISTORY_REFUSED = "ACCEPTED_HISTORY_REFUSED"  # the finding of an entry that is refused
TRAILER_MISSING = "TRAILER_MISSING"

ENGINEER_ROLE = "Role: engineer"
CAPABILITY = "CAP-01"
SUITE_SETTINGS = dict(base.SUITE_SETTINGS)


def trailers_of(ticket, role="engineer", implements=CAPABILITY):
    return (f"Task: {ticket}", f"Role: {role}", f"Implements: {implements}")


def merge_form(ticket, role="orchestrator"):
    """DEC-436's merge form: ``Task:`` and ``Role:``, no ``Implements:``."""
    return (f"Task: {ticket}", f"Role: {role}")


def git(project, *args, who=AGENT, check=True):
    return base.git(project.root if isinstance(project, base.Project) else project, *args, who=who, check=check)


def head_of(project):
    return git(project, "rev-parse", "HEAD").strip()


def path_map_text(settings):
    """W1-30's path map text, and the accepted-history list (DEC-734) written as a YAML list of mappings."""
    plain = {key: value for key, value in settings.items() if key != ACCEPTED_KEY}
    text = base.path_map_text(plain)
    if ACCEPTED_KEY in settings:
        entries = settings[ACCEPTED_KEY]
        if not entries:
            text += f"{ACCEPTED_KEY}: []\n"
        else:
            text += f"{ACCEPTED_KEY}:\n"
            for entry in entries:
                text += "".join(f"  {'-' if n == 0 else ' '} {key}: {json.dumps(str(value))}\n"
                                for n, (key, value) in enumerate(entry.items()))
    return text


class Project(base.Project):
    """A temporary git repository that ``gov close`` can run in, built from scratch.

    Unlike W1-30's project it copies no folder of this repository: it receives the ticket tool and the
    trailers check's declaration, each a single named file. The path map holds the suite's settings and names
    the project's decision register (DEC-479); the register itself is written by the cases that need it.
    """

    def __init__(self, root, settings=None):
        self.settings = dict(SUITE_SETTINGS if settings is None else settings)
        self.settings.setdefault(REGISTER_KEY, REGISTER)
        super().__init__(root, checks=None, settings=self.settings)

    def _init_minimal(self):
        git(self.root, "init", "-q", "-b", "main")
        self.write("README.md", "# A project\n")
        self.write(".gitignore", ".gov-runtime/\n")
        self._copy_named_files()
        self.write(PATH_MAP_REL, path_map_text(self.settings))
        self.write(REGISTER, "# Decision register\n\n")
        self.write(f"docs/adr/{base.BASE_SOURCE}.md",
                   base.decision(base.BASE_SOURCE, "ACTIVE", title="The base decision"))
        self.add_decision(CAPABILITY, "ACTIVE", title="The capability")
        base.commit_all(self.root, "initial project", who=OWNER, trailers=("Task: setup", "Role: owner"))

    def _copy_named_files(self):
        declaration = REPO_ROOT / CHECKS_REL / TRAILERS_CHECK_FILE
        target = self.root / CHECKS_REL / TRAILERS_CHECK_FILE
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(declaration, target)
        tool = REPO_ROOT / "template" / "governance" / "kernel" / "bin" / "tk"
        tool_target = self.root / "governance" / "kernel" / "bin" / "tk"
        tool_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(tool, tool_target)
        tool_target.chmod(0o755)

    # ---- settings -----------------------------------------------------------------------------------

    def set_path_map(self, commit=True, **settings):
        """The path map gains (or loses, for a value ``None``) ``settings``; committed by the owner."""
        for key, value in settings.items():
            if value is None:
                self.settings.pop(key, None)
            else:
                self.settings[key] = value
        self.write(PATH_MAP_REL, path_map_text(self.settings))
        if commit:
            return self.commit("the project's path map", who=OWNER, trailers=("Task: setup", "Role: owner"),
                               exact=True)
        return None

    def record_decision(self, decision_id, status, text, who=OWNER, role="owner"):
        """An entry of the project's register (DEC-473's heading, a status line), committed by ``who`` with
        ``role`` (the owner's entries with ``Role: owner``, DEC-724)."""
        path = self.root / REGISTER
        entry = (f"### {decision_id} — A decision of the fixture\n"
                 f"- **Status:** {status} · **Basis:** the fixture\n"
                 f"- **Decision:** {text}\n\n")
        self.write(REGISTER, path.read_text(encoding="utf-8") + entry)
        return self.commit(f"register: {decision_id}", who=who,
                           trailers=("Task: decision-record", f"Role: {role}"), exact=True)

    # ---- branches -----------------------------------------------------------------------------------

    def checkout(self, branch, create=False, start=None):
        args = ["checkout", "-q"] + (["-b", branch] if create else [branch])
        if start is not None:
            args.append(start)
        git(self, *args)

    def merge(self, head, trailers, who=ORCHESTRATOR, edit=None, message="merge"):
        """Merge ``head`` into the branch checked out, in one commit carrying ``trailers`` in its final block.
        ``edit`` (``{path: text}``) is written into the merge itself before it is committed (a hand-resolved
        conflict or an own change). Returns the merge commit."""
        text = message + "\n\n" + "\n".join(trailers) + "\n"
        done = git(self, "merge", "-q", "--no-ff", "--no-commit", "--no-gpg-sign", head, who=who, check=False)
        if edit:
            for rel, content in edit.items():
                self.write(rel, content)
        git(self, "add", "-A", who=who)
        unmerged = git(self, "diff", "--name-only", "--diff-filter=U").strip()
        assert not unmerged, f"the fixture left a conflict unresolved: {unmerged}\n{done}"
        git(self, "commit", "-q", "--no-gpg-sign", "-m", text, who=who)
        merge = head_of(self)
        parents = git(self, "rev-list", "--parents", "-n", "1", merge).split()
        assert len(parents) == 3, "the fixture is wrong: the merge is not a merge commit"
        return merge


def merge_by_hand(project, head, trailers, edit=None, remove=(), strategy=None, who=ORCHESTRATOR, message="merge"):
    """Like ``Project.merge``, and the merge may also remove ``remove`` (paths) or be made with git's merge
    ``strategy`` (``"ours"``). Returns the merge commit. (Added after implementation began, DEC-136.)"""
    text = message + "\n\n" + "\n".join(trailers) + "\n"
    args = ["merge", "-q", "--no-ff", "--no-commit", "--no-gpg-sign"] + (["-s", strategy] if strategy else [])
    done = git(project, *args, head, who=who, check=False)
    for rel, content in (edit or {}).items():
        project.write(rel, content)
    for rel in remove:
        git(project, "rm", "-q", "-f", "--", rel, who=who)
    git(project, "add", "-A", who=who)
    unmerged = git(project, "diff", "--name-only", "--diff-filter=U").strip()
    assert not unmerged, f"the fixture left a conflict unresolved: {unmerged}\n{done}"
    git(project, "commit", "-q", "--no-gpg-sign", "-m", text, who=who)
    merge = head_of(project)
    assert len(git(project, "rev-list", "--parents", "-n", "1", merge).split()) == 3, \
        "the fixture is wrong: the merge is not a merge commit"
    return merge


def content_at(project, commit, rel):
    """The text of ``rel`` at ``commit``, or ``None`` when the commit does not hold it."""
    if git(project, "ls-tree", "--name-only", commit, "--", rel).strip() != rel:
        return None
    return git(project, "show", f"{commit}:{rel}")


# --------------------------------------------------------------------------
# A ticket's life
# --------------------------------------------------------------------------

def create_ticket(project, ticket, wbs, profile="STANDARD", allowed_paths=("src/example/**",),
                  trailers=None, who=ORCHESTRATOR):
    """The ticket-creating commit (the ticket file alone, by the orchestrator), then the test designer's commit
    of the ticket's acceptance folder with one passing test. The creating commit carries ``trailers``; by
    default every trailer (``Task:``, ``Role: orchestrator``, ``Implements:``), as this repository's claim
    commits do. Returns the creating commit."""
    project.add_ticket(ticket, wbs, profile=profile, allowed_paths=list(allowed_paths))
    project.add_passing_test(wbs)
    effective = trailers_of(ticket, role="orchestrator") if trailers is None else trailers
    created = project._commit(f"ticket {ticket} created", who, effective, [base.ticket_path(ticket)])
    project.commit("acceptance tests", who=TEST_DESIGNER,
                   trailers=trailers_of(ticket, role="independent-test-designer"), exact=True)
    return created


def engineer_commit(project, ticket, files, trailers=None, who=IMPLEMENTER, message="work on the ticket"):
    for rel, text in files.items():
        project.write(rel, text)
    effective = trailers_of(ticket) if trailers is None else trailers
    return project.commit(message, who=who, trailers=effective, exact=True)


def checkpointed(project, ticket):
    project.add_checkpoint(ticket)
    return project.commit("checkpoint", who=ORCHESTRATOR, trailers=("Role: orchestrator",), exact=True)


def probe_recorded(project, ticket, probed, judgement="pass", name=None, trailers=("Role: orchestrator",)):
    """The orchestrator's probe record of ``probed`` in ``docs/probes/<ticket>/`` (DEC-137, DEC-487), committed
    with the orchestrator's role. ``name`` is the file's stem (default ``PR-<ticket>``)."""
    stem = name or f"PR-{ticket}"
    text = base.probe_record(ticket, judgement=judgement, probed_commit=probed)
    text = text.replace(f"PR-{ticket}", stem)
    project.write(f"docs/probes/{ticket}/{stem}.md", text)
    return project.commit(f"probe record {stem}", who=ORCHESTRATOR, trailers=trailers, exact=True)


def set_status(project, ticket, status, who=ORCHESTRATOR, trailers=None):
    path = project.root / base.ticket_path(ticket)
    text = path.read_text(encoding="utf-8")
    current = base.read_ticket_frontmatter(project.root, ticket).get("status")
    path.write_text(text.replace(f"status: {current}", f"status: {status}", 1), encoding="utf-8")
    effective = ("Role: orchestrator",) if trailers is None else trailers
    return project.commit(f"{ticket} {status}", who=who, trailers=effective, exact=True)


# --------------------------------------------------------------------------
# Running and reading
# --------------------------------------------------------------------------

def run_close(project, sandbox, ticket, *args):
    return base.run_close(project, sandbox, ticket, *args)


def closed(run, interface):
    """The close succeeded: exit code 0, ``ok`` true. Returns the result."""
    return base.result_of(run, interface)


def refused(run, interface, exit_code=EXIT_CHECK_FAILED):
    return base.refused(run, interface, exit_code)


def answer_of(run):
    """The whole envelope, parsed."""
    return run.envelope()


def text_of(value):
    return json.dumps(value, ensure_ascii=False)


def findings_of(error):
    """Every object with a ``code`` at any depth of a refusal's ``error`` (the refusal itself included)."""
    return cli_support.find_records(error, key="code")


def codes_of(error):
    return [finding.get("code") for finding in findings_of(error)]


def strings_of(value):
    """Every string at any depth of ``value``: the statements of an answer."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in strings_of(item)]
    if isinstance(value, list):
        return [text for item in value for text in strings_of(item)]
    return []


def mentions(value, commit):
    """Whether ``value`` names ``commit`` anywhere (by its first 7 characters)."""
    return commit[:7] in text_of(value)


def statements_naming(value, commit):
    """The statements (strings) of ``value`` that name ``commit``: a refusal states each finding in one, and
    groups several commits under one code, so a commit is told apart in its own statement."""
    return [text for text in strings_of(value) if commit[:7] in text]


def check_entry(project, sandbox, interface, check_id=TRAILERS_CHECK):
    """The entry of ``check_id`` in ``gov check --json`` (from ``result``, or from ``error.details`` on exit
    code 3), and the run."""
    run = base.run_check(project, sandbox)
    envelope = base.check_envelope_of(run, interface)
    body = envelope.get("result") if envelope.get("ok") else (envelope.get("error") or {}).get("details")
    entries = [entry for entry in base.checks_of(body or {}) if entry.get("id") == check_id]
    assert len(entries) == 1, f"{check_id} is not reported once by gov check\n{run.describe()}"
    return entries[0], run


def run_check_command(project, sandbox):
    """The trailers check run by the command its declaration names, in the project root, as W1-26's runner
    runs it: ``(exit code, stdout, stderr)``."""
    declaration = (project.root / CHECKS_REL / TRAILERS_CHECK_FILE).read_text(encoding="utf-8")
    command = next(line.split(":", 1)[1].strip().strip('"') for line in declaration.splitlines()
                   if line.startswith("command:"))
    done = subprocess.run(command, shell=True, cwd=str(project.root), env=base.sandbox_env(sandbox),
                          capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=180)
    return done.returncode, done.stdout, done.stderr


def accepted_entries(value):
    """The entries listed as accepted history anywhere in ``value``: every object of a list held under the key
    ``accepted_history`` at any depth."""
    found = []

    def walk(node):
        if isinstance(node, dict):
            for key, item in node.items():
                if key == ACCEPTED_FIELD and isinstance(item, list):
                    found.extend(entry for entry in item if isinstance(entry, dict))
                walk(item)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(value)
    return found


def listed_as_accepted(value, commit, decision):
    """Whether ``value`` lists ``commit`` (full id) as accepted history with ``decision``."""
    return any(str(entry.get("commit", "")) == commit and entry.get("decision") == decision
               for entry in accepted_entries(value))


def bases_named(value):
    """Every value held under the key ``trailers_base`` at any depth of ``value``."""
    found = []

    def walk(node):
        if isinstance(node, dict):
            for key, item in node.items():
                if key == BASE_FIELD:
                    found.append(item)
                walk(item)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(value)
    return found
