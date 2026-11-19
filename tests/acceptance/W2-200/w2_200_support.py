"""Support code for the W2-200 acceptance tests (DAEO-r4xc; standard library and PyYAML only).

W2-200 retires ``gov context``, its library ``gov.context`` and its check, and makes ``gov close`` record the decisions
that govern a change from the ticket's own sources (DEC-1214 M1 (c)). Every case drives a public interface as a child
process: ``python3 -m gov.cli.main`` on this worktree's ``src`` (the runner's ``PYTHONPATH`` when it has one), with a
fixture ``HOME`` under the test's ``tmp_path``, ``TZ=UTC`` and every ``GIT_*`` and ``GOV_*`` variable of the caller
removed. It reads what the ticket names: exit codes, stdout and stderr, the ``--json`` envelope, the close record file,
the repair ticket file, the facts file, ``git`` and the files. Nothing of the implementation is imported in this
process; an import is tried only in a child process.

Every project is a temporary git repository built from nothing under ``tmp_path``. The close fixture is the smallest
project a strict ``gov close`` passes in: a path map naming the register, one declared check that passes, the kernel's
ticket tool, a ticket in progress whose commits are made by the roles that may make them (the orchestrator's ticket
file, the test designer's acceptance test, the engineer's source file, each with its trailers), a checkpoint, and the
record store rebuilt for ``HEAD`` with ``gov rebuild`` before the close. No network, no model, no vector.
"""

from __future__ import annotations

import hashlib
import json
import os
import pwd
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
TIMEOUT_S = 300.0
REAL_GIT = shutil.which("git")

KERNEL = REPO_ROOT / "template" / "governance" / "kernel"
KERNEL_CHECKS = KERNEL / "checks"
KERNEL_SCHEMAS = KERNEL / "schemas"
KERNEL_TK = KERNEL / "bin" / "tk"
KERNEL_TEMPLATES = KERNEL / "templates"

PATH_MAP_REL = "governance/project/path-map.yaml"
FACTS_REL = "governance/project/facts.yaml"
REGISTER_REL = "docs/DECISION_REGISTER.md"
CHECKS_REL = "template/governance/kernel/checks"
TK_REL = "governance/kernel/bin/tk"

# The ticket closed in the close fixtures, and its acceptance folder.
TICKET = "PROJ-w200"
WBS = "W9-200"
EXIT_OK = 0
RETIRED_CODES = ("CONTEXT_OVER_CEILING", "CONTEXT_FAILED", "CONTEXT_SETTING_INVALID")

# The identities of the fixture's commits (W1-30's roles: the orchestrator writes tickets, the test designer the
# acceptance tests, the engineer the code), dated after the trailer rule (DEC-182).
OWNER = ("The Owner", "owner@example.invalid", ())
ORCHESTRATOR = ("The Orchestrator", "orch@example.invalid", ("Role: orchestrator",))
DESIGNER = ("The Test Designer", "designer@example.invalid",
            (f"Task: {TICKET}", "Role: independent-test-designer", "Implements: CAP-01"))
ENGINEER = ("The Implementer", "impl@example.invalid", (f"Task: {TICKET}", "Role: engineer", "Implements: CAP-01"))
DATE = "2026-11-10T12:{minute:02d}:00+00:00"


# A strict close runs ``gov check``, whose built-in ``openspec-validate`` check needs ``openspec`` on PATH (RED when
# absent). The fixtures hold no specification; a stand-in that validates keeps the close independent of whether node
# and openspec are installed where the suite runs. It is not what any case measures.
STAND_INS = {"openspec": "#!/bin/sh\necho 'nothing to validate: the W2-200 stand-in'\nexit 0\n"}


def python_path() -> str:
    return os.environ.get("PYTHONPATH") or str(REPO_ROOT / "src")


def user_base() -> str:
    return os.environ.get("PYTHONUSERBASE") or str(Path(pwd.getpwuid(os.getuid()).pw_dir) / ".local")


def write(path, text: str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def make_home(base: Path) -> Path:
    """A fixture HOME with a git identity and ``main`` as the default branch, and its ``bin`` with a stand-in
    ``openspec`` that validates (``STAND_INS``)."""
    home = Path(base).resolve() / "home"
    home.mkdir(parents=True, exist_ok=True)
    for name, text in STAND_INS.items():
        tool = write(home / "bin" / name, text)
        tool.chmod(0o755)
    write(home / ".gitconfig",
          "[user]\n\tname = Fixture\n\temail = fixture@example.invalid\n"
          "[init]\n\tdefaultBranch = main\n[commit]\n\tgpgsign = false\n[tag]\n\tgpgsign = false\n")
    return home


def make_env(home: Path, **extra: str) -> dict:
    """The child's environment: the caller's, less every GIT_* and GOV_* variable, with the fixture HOME (its
    ``bin`` first on ``PATH``), offline."""
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "GOV_", "PYTEST_"))}
    dead = "127.0.0.1:9"
    env.update(HOME=str(home), TZ="UTC", PATH=os.pathsep.join([str(Path(home) / "bin"), os.environ.get("PATH", "")]), PYTHONPATH=python_path(), PYTHONUSERBASE=user_base(),
               PYTHONDONTWRITEBYTECODE="1", GIT_CONFIG_NOSYSTEM="1", LC_ALL="C.UTF-8",
               OLLAMA_HOST=dead, GOV_QUERY_OLLAMA_HOST=dead, HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1",
               http_proxy=f"http://{dead}", https_proxy=f"http://{dead}")
    env.update(extra)
    return env


@dataclass
class Run:
    code: int
    out: str
    err: str
    args: tuple = ()

    @property
    def both(self) -> str:
        return self.out + self.err

    def describe(self) -> str:
        return f"gov {' '.join(self.args)}: exit {self.code}\nstdout: {self.out[-3000:]}\nstderr: {self.err[-3000:]}"

    def envelope(self) -> dict:
        text = self.out.strip()
        assert text, f"no JSON envelope on stdout\n{self.describe()}"
        try:
            data = json.loads(text)
        except ValueError:
            raise AssertionError(f"stdout is not one JSON envelope\n{self.describe()}") from None
        assert isinstance(data, dict) and "ok" in data, f"not an envelope\n{self.describe()}"
        return data

    def result(self) -> dict:
        data = self.envelope()
        assert data["ok"] is True, f"the command refused\n{self.describe()}"
        return data["result"]

    def error(self) -> dict:
        data = self.envelope()
        assert data["ok"] is False, f"the command did not refuse\n{self.describe()}"
        return data["error"]


def gov(args, *, env: dict, cwd, timeout: float = TIMEOUT_S) -> Run:
    args = tuple(str(a) for a in args)
    try:
        done = subprocess.run([sys.executable, "-m", "gov.cli.main", *args], cwd=str(cwd), env=env,
                              capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"gov {' '.join(args)} did not end within {timeout:.0f} s") from None
    return Run(done.returncode, done.stdout, done.stderr, args)


def python(code: str, *, env: dict, cwd) -> subprocess.CompletedProcess:
    """``python3 -c <code>`` in a child process, in ``env``."""
    return subprocess.run([sys.executable, "-c", code], cwd=str(cwd), env=env, capture_output=True, text=True,
                          timeout=TIMEOUT_S, stdin=subprocess.DEVNULL)


def git(*args, cwd, env: dict, who=OWNER, minute: int = 0, check: bool = True) -> str:
    env = dict(env)
    name, email, _ = who
    date = DATE.format(minute=minute % 60)
    env.update(GIT_AUTHOR_NAME=name, GIT_AUTHOR_EMAIL=email, GIT_COMMITTER_NAME=name, GIT_COMMITTER_EMAIL=email,
               GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
    done = subprocess.run([REAL_GIT, *[str(a) for a in args]], cwd=str(cwd), env=env, capture_output=True,
                          text=True, timeout=60)
    if check:
        assert done.returncode == 0, f"fixture git {args} failed: {done.stderr}"
    return done.stdout.strip()


def tree_files(root: Path, skip=(".git", ".gov-runtime")) -> dict:
    """Every file under ``root`` outside ``skip`` (relative path -> sha256 of its bytes)."""
    root = Path(root)
    found = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if rel.parts and rel.parts[0] in skip:
            continue
        if path.is_file():
            found[str(rel)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return found


# --------------------------------------------------------------------------
# The register
# --------------------------------------------------------------------------

REGISTER_HEAD = "# Decision register\n\nThe planted project's decisions, oldest first.\n\n"


def entry(number: int, title: str, status: str = "ACCEPTED (owner, 2026-11-01)", lines=(), body: str | None = None) -> str:
    """One register entry: its heading, its status line, any further lines, then its text and a blank line."""
    out = [f"### DEC-{number} — {title}", f"- **Status:** {status}", *lines, "",
           body if body is not None else f"The text of DEC-{number}: {title.lower()}.", ""]
    return "\n".join(out) + "\n"


def done_tags() -> str:
    return "- **Tags:** domain: close · scope: repository · lands in: governance/project/notes.md · done"


def register(*entries: str) -> str:
    return REGISTER_HEAD + "".join(entries)


def spans(text: str) -> dict:
    """``DEC-n -> its span``: the text from its heading line to the line before the next heading of any level, as the
    register's grammar (W2-03) cuts it; the last entry runs to the end of the file."""
    lines = text.split("\n")
    heads = [n for n, line in enumerate(lines) if re.match(r"#{1,6}(\s|$)", line)]
    found = {}
    for at, n in enumerate(heads):
        hit = re.match(r"### (DEC-[0-9]{3,})(?=[ :\-–—])", lines[n])
        if hit:
            end = heads[at + 1] if at + 1 < len(heads) else len(lines)
            found[hit.group(1)] = "\n".join(lines[n:end])
    return found


def span_hashes(text: str, number_ids) -> dict:
    """``id -> {"sha256:<hex>" of the span's UTF-8 bytes, with and without its trailing newlines}``: the span's own
    bytes, whether or not the line break that ends it is counted as its own."""
    found = spans(text)
    out = {}
    for rid in number_ids:
        span = found[rid]
        forms = {span, span.rstrip("\n"), span.rstrip("\n") + "\n", span + "\n"}
        out[rid] = {"sha256:" + hashlib.sha256(form.encode("utf-8")).hexdigest() for form in forms}
    return out


def by_number(ids) -> list:
    return sorted(ids, key=lambda rid: int(rid.split("-")[1]))


# --------------------------------------------------------------------------
# The close fixture
# --------------------------------------------------------------------------

def ticket_text(ticket: str = TICKET, wbs: str = WBS, sources=(), decisions=None, success=("It works.",),
                failure=("It does not work.",), body: str = "Body text.\n", profile: str = "STANDARD") -> str:
    """A ticket file as this repository's tickets are written: tk's own fields, then the task contract."""
    front = {"id": ticket, "status": "in_progress", "deps": [], "links": [], "created": "2026-11-01T12:00:00Z",
             "type": "task", "priority": 2, "assignee": "engineer", "external-ref": wbs, "tags": ["test"],
             "wbs_id": wbs, "title": f"Ticket {wbs}", "class": "implementation", "state_class": "AUTHORITATIVE",
             "role": "engineer", "depends_on": [], "allowed_paths": ["src/example/**"],
             "kpis": {"success": list(success), "failure": list(failure)}, "profile": profile,
             "sources": list(sources)}
    if decisions is not None:
        front["decisions"] = list(decisions)
    front.update({"est_loc": 10, "acceptance_tests": {"path": f"tests/acceptance/{wbs}/",
                                                      "author": "independent-test-designer"}})
    text = yaml.safe_dump(front, sort_keys=False, allow_unicode=True, width=100_000)
    return f"---\n{text}---\n# {wbs} A ticket\n\n{body}"


def path_map(register_rel: str | None = REGISTER_REL) -> str:
    text = "namespaces: {all: {paths: ['**']}}\nclose_workers: 2\n"
    if register_rel is not None:
        text += f"decision_register: {register_rel}\n"
    return text


PASSING_TEST = "def test_pass():\n    assert True\n"
FAILING_TEST = "def test_fail():\n    assert False, 'planted failure'\n"


class CloseProject:
    """A temporary git repository a strict ``gov close`` runs in (module docstring)."""

    def __init__(self, base: Path, env: dict, register_text: str | None, register_rel: str | None = REGISTER_REL,
                 extra_files: dict | None = None):
        self.root = Path(base) / "proj"
        self.root.mkdir(parents=True)
        self.env = env
        self.minute = 0
        git("init", "-q", "-b", "main", cwd=self.root, env=env)
        files = {"README.md": "# A project\n", ".gitignore": ".gov-runtime/\n",
                 PATH_MAP_REL: path_map(register_rel),
                 f"{CHECKS_REL}/fixture-passes.yaml":
                     'id: "fixture-passes"\nfamily: "schema/invariants"\ntier: "G1"\nseverity: "hard-block"\n'
                     'command: "true"\n',
                 "docs/notes/plain.md": "# Notes\n\nA plain page the ticket may cite by path.\n"}
        if register_text is not None and register_rel is not None:
            files[register_rel] = register_text
        files.update(extra_files or {})
        for rel, text in files.items():
            write(self.root / rel, text)
        tk = self.root / TK_REL
        tk.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(KERNEL_TK, tk)
        tk.chmod(0o755)
        shutil.copytree(KERNEL_SCHEMAS, self.root / "template" / "governance" / "kernel" / "schemas")
        self.commit("the planted project", OWNER)

    # git
    def commit(self, message: str, who, paths=None) -> str:
        self.minute += 1
        if paths is None:
            git("add", "-A", cwd=self.root, env=self.env, who=who, minute=self.minute)
        else:
            git("add", "-A", "--", *paths, cwd=self.root, env=self.env, who=who, minute=self.minute)
        args = ["commit", "-q", "--allow-empty", "--no-gpg-sign", "-m", message]
        for trailer in who[2]:
            args += ["--trailer", trailer]
        git(*args, cwd=self.root, env=self.env, who=who, minute=self.minute)
        return git("rev-parse", "HEAD", cwd=self.root, env=self.env)

    def status(self) -> str:
        return git("status", "--porcelain=v1", "-uall", cwd=self.root, env=self.env)

    def head(self) -> str:
        return git("rev-parse", "HEAD", cwd=self.root, env=self.env)

    def gov(self, *args) -> Run:
        return gov([*args, "--root", self.root], env=self.env, cwd=self.root)

    # the ticket's work, by the roles that may do it
    def add_ticket(self, text: str, failing: bool = False, ticket: str = TICKET, wbs: str = WBS) -> None:
        write(self.root / f".tickets/{ticket}.md", text)
        self.commit("ticket", ORCHESTRATOR, [".tickets"])
        write(self.root / f"tests/acceptance/{wbs}/README.md", f"# {wbs}\n")
        write(self.root / f"tests/acceptance/{wbs}/{'test_fail' if failing else 'test_pass'}.py",
              FAILING_TEST if failing else PASSING_TEST)
        self.commit("acceptance tests", DESIGNER, ["tests/acceptance"])
        write(self.root / "src/example/feature.py", "# feature\n")
        self.commit("implement", ENGINEER)
        run = self.gov("checkpoint", "--ticket", ticket, "--trigger", "stop", "--next", "resume", "--json")
        assert run.code == 0, f"the fixture's checkpoint failed\n{run.describe()}"
        self.commit("checkpoint", ORCHESTRATOR)

    def rebuild(self) -> None:
        """The record store for ``HEAD`` (the close's store gate, unchanged by this ticket)."""
        run = self.gov("rebuild", "--json")
        assert run.code == 0, f"the fixture's gov rebuild failed\n{run.describe()}"

    def close(self, *extra, ticket: str = TICKET, rebuild: bool = True, env: dict | None = None) -> Run:
        """``gov close <ticket> --json [extra]``, the store rebuilt for ``HEAD`` first unless ``rebuild`` is False."""
        if rebuild:
            self.rebuild()
        args = ["close", ticket, "--json", *extra, "--root", self.root]
        return gov(args, env=env or self.env, cwd=self.root)

    def record_path(self, ticket: str = TICKET) -> Path:
        return self.root / "docs" / "close" / ticket / f"CL-{ticket}.md"

    def record(self, ticket: str = TICKET) -> dict:
        """The close record's frontmatter (``docs/close/<ticket>/CL-<ticket>.md``)."""
        path = self.record_path(ticket)
        assert path.is_file(), f"no close record at {path.relative_to(self.root)}"
        return front_of(path.read_text(encoding="utf-8"))

    def checkpoints(self, ticket: str = TICKET) -> list:
        folder = self.root / "docs" / "checkpoints" / ticket
        return sorted(p.name for p in folder.glob("*")) if folder.is_dir() else []

    def iteration_file(self, ticket: str = TICKET) -> Path:
        """Where the close counts a ticket's refused attempts (its state, W1-30 A6)."""
        return self.root / ".gov-runtime" / "iterations" / f"{ticket}.json"

    def clone(self, base: Path) -> "CloseProject":
        """A second repository at the same commit, cloned from this one (the same ticket at the same commit)."""
        twin = object.__new__(CloseProject)
        twin.root = Path(base) / "twin"
        twin.env = self.env
        twin.minute = self.minute
        git("clone", "-q", "--no-local", str(self.root), str(twin.root), cwd=base, env=self.env)
        assert twin.head() == self.head()
        return twin

    def repair_tickets(self, ticket: str = TICKET) -> list:
        """The ticket files whose ``parent`` is ``ticket``."""
        found = []
        for path in sorted((self.root / ".tickets").glob("*.md")):
            if path.stem != ticket and front_of(path.read_text(encoding="utf-8")).get("parent") == ticket:
                found.append(path)
        return found


def front_of(text: str) -> dict:
    parts = text.split("---", 2)
    assert len(parts) == 3, f"no frontmatter: {text[:200]!r}"
    data = yaml.safe_load(parts[1])
    assert isinstance(data, dict), f"the frontmatter is not a map: {parts[1][:200]!r}"
    return data


def closed(run: Run) -> dict:
    """The close passed: exit 0 and an ok envelope; its result."""
    data = run.envelope()
    assert run.code == EXIT_OK and data["ok"] is True, f"the close did not pass\n{run.describe()}"
    return data["result"]


def input_hashes(record: dict) -> dict:
    """``id -> hash`` of the record's ``inputs``."""
    inputs = record.get("inputs")
    assert isinstance(inputs, list), f"the record has no list of inputs: {sorted(record)}"
    return {item["id"]: item.get("hash") for item in inputs if isinstance(item, dict) and "id" in item}


def ticket_hash(project: CloseProject, commit: str, ticket: str = TICKET) -> str:
    """``sha256:<hex>`` of the ticket file as the commit the close measured holds it (the close's ``tk close`` rewrites
    the file afterwards, ``status: closed``, so the working file is not what was measured)."""
    done = subprocess.run([REAL_GIT, "show", f"{commit}:.tickets/{ticket}.md"], cwd=str(project.root),
                          env=project.env, capture_output=True, timeout=60)
    assert done.returncode == 0, f"git show {commit}:.tickets/{ticket}.md failed: {done.stderr!r}"
    return "sha256:" + hashlib.sha256(done.stdout).hexdigest()


# --------------------------------------------------------------------------
# The import sentinel (F2): records every attempt to import gov.context in any Python process
# --------------------------------------------------------------------------

SENTINEL = '''
import os, sys

class _W200ContextSentinel:
    """Writes one line to $W200_IMPORT_LOG for every import of gov.context or a module under it."""
    def find_spec(self, name, path=None, target=None):
        if name == "gov.context" or name.startswith("gov.context."):
            log = os.environ.get("W200_IMPORT_LOG")
            if log:
                with open(log, "a", encoding="utf-8") as handle:
                    handle.write(f"{os.getpid()} {name} {' '.join(sys.argv)[:200]}\\n")
        return None

sys.meta_path.insert(0, _W200ContextSentinel())
'''


def sentinel_env(env: dict, folder: Path) -> tuple[dict, Path]:
    """``env`` with a ``sitecustomize`` first on ``PYTHONPATH`` that logs each import of ``gov.context`` to a file
    (in this process and in every Python child that inherits the environment); the log's path."""
    folder = Path(folder)
    write(folder / "site" / "sitecustomize.py", SENTINEL)
    log = folder / "imports.log"
    out = dict(env)
    out["PYTHONPATH"] = os.pathsep.join([str(folder / "site"), env["PYTHONPATH"]])
    out["W200_IMPORT_LOG"] = str(log)
    return out, log


def imports_logged(log: Path) -> list:
    return log.read_text(encoding="utf-8").splitlines() if log.is_file() else []


# --------------------------------------------------------------------------
# The code under test, found as the child process finds it
# --------------------------------------------------------------------------

def package_dir(env: dict, cwd) -> Path:
    """The folder of the ``gov`` package the child process imports (the code under test)."""
    done = python("import gov, pathlib; print(pathlib.Path(gov.__file__).resolve().parent)", env=env, cwd=cwd)
    assert done.returncode == 0, f"the gov package cannot be imported: {done.stderr[-2000:]}"
    return Path(done.stdout.strip().splitlines()[-1])


def source_files(folder: Path, skip=("__pycache__",)):
    """Every file under ``folder`` outside the ``skip`` folders (bytecode is not source)."""
    for path in sorted(Path(folder).rglob("*")):
        if path.is_file() and not any(part in skip for part in path.relative_to(folder).parts):
            yield path


# --------------------------------------------------------------------------
# A project holding the kernel's check declarations (S1, F2)
# --------------------------------------------------------------------------

def kernel_checks_project(base: Path, env: dict) -> Path:
    """A committed project holding this tree's kernel check declarations, as an adopted project holds its kernel,
    a path map naming a register, and a one-entry register."""
    root = Path(base) / "kernelproj"
    root.mkdir(parents=True)
    git("init", "-q", "-b", "main", cwd=root, env=env)
    write(root / "README.md", "# A project\n")
    write(root / ".gitignore", ".gov-runtime/\n")
    write(root / PATH_MAP_REL, path_map())
    write(root / REGISTER_REL, register(entry(110, "The plain decision")))
    shutil.copytree(KERNEL_CHECKS, root / CHECKS_REL)
    git("add", "-A", cwd=root, env=env)
    git("commit", "-q", "--no-gpg-sign", "-m", "a project with the kernel's checks", cwd=root, env=env)
    return root


# --------------------------------------------------------------------------
# The adopted project of S8: gov adopt --facts, then gov brief lead
# --------------------------------------------------------------------------

BRIEF_TICKET = "DAEO-w2a0"
BRIEF_W2 = "W9-201"


def brief_ticket_text(ticket_id: str = BRIEF_TICKET, w2: str = BRIEF_W2) -> str:
    """A ticket READY for a brief (every field the ready check reads; each KPI line with its verify)."""
    return (
        "---\n"
        f"id: {ticket_id}\nstatus: in_progress\ndeps: []\nlinks: []\ncreated: 2026-11-18T09:00:00Z\ntype: task\n"
        f"priority: 1\nassignee: engineer\nexternal-ref: {w2}\ntags:\n- fixture\nwbs_id: {w2}\n"
        f"title: Fixture ticket {w2}\nclass: tool\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: []\n"
        "allowed_paths:\n- src/widget/**\n- tests/unit/widget/**\nreads:\n- src/widget/**\nneeds: []\nwaits_on: []\n"
        "kpis:\n  success:\n  - 'The widget prints its name [DEC-1]. Verify: a unit test of the name'\n"
        "  failure:\n  - 'The widget prints nothing [DEC-1]. Verify: a unit test of the empty name'\n"
        "non_goals:\n- No graphical interface.\ndone_when:\n- DOD-1\n- DOD-2\n- DOD-3\nprofile: STANDARD\n"
        f"sources:\n- DEC-1\nest_loc: 120\nacceptance_tests:\n  path: tests/acceptance/{w2}/\ntrack: A\n"
        f"---\n# {w2} Fixture ticket {w2}\n\nThe widget prints its name when asked, and refuses an empty one.\n"
    )


def adopted_project(base: Path, env: dict) -> Path:
    """A folder with the kernel's templates and one READY ticket, then ``gov adopt --facts`` (asserted to write)."""
    root = Path(base) / "adopted"
    (root / ".tickets").mkdir(parents=True)
    shutil.copytree(KERNEL_TEMPLATES, root / "template" / "governance" / "kernel" / "templates")
    write(root / ".tickets" / f"{BRIEF_TICKET}.md", brief_ticket_text())
    return root


def fill_unset_commands(root: Path) -> dict:
    """The adopted facts file with each command it leaves unset (``{UNSET_<NAME>}``) given a form, as the project's
    CTO fills them; every other entry stays as ``gov adopt`` wrote it. Returns the facts as written."""
    path = Path(root) / FACTS_REL
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    for name, forms in (data.get("commands") or {}).items():
        if isinstance(forms, dict) and str(forms.get("run", "")).startswith("{UNSET_"):
            forms["run"] = f"echo fixture-{name}"
            forms["check"] = f"echo fixture-{name} --help"
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=1000), encoding="utf-8")
    return data


# --------------------------------------------------------------------------
# The planted worlds of S3 to S7 and F1 (the ids are the ticket's, moved into the register's grammar: README)
# --------------------------------------------------------------------------

# S3: one decision cited in each place, two of them twice, one numbered past a thousand (sorted by number, not as
# text), beside ids of other forms and look-alikes that are no whole-word decision id.
S3_REGISTER = register(entry(110, "The record names the decisions it applied"),
                       entry(111, "A decision list beside the sources"),
                       entry(112, "A decision cited only in a KPI line"),
                       entry(150, "A decision no ticket cites"),
                       entry(1013, "A decision numbered past a thousand"))
S3_SOURCES = ["DEC-1013", "DEC-110", "CAP-1", "W2-9", "docs/notes/plain.md", "EMERGENCY-2 5.5"]
S3_DECISIONS = ["DEC-111", "DEC-110"]
S3_SUCCESS = ["S1 The widget names its rule [DEC-112, DEC-111]. Verify: a unit test of the rule.",
              "S2 The widget keeps PREDEC-141 and DEC-1400x apart from its rules."]
S3_FAILURE = ["F1 The widget forgets its rule [DEC-112]."]
S3_APPLIED = ["DEC-110", "DEC-111", "DEC-112", "DEC-1013"]
S3_NOT_DECISIONS = ["CAP-1", "W2-9", "docs/notes/plain.md", "EMERGENCY-2 5.5", "DEC-141", "DEC-1400", "DEC-150"]

# S4: a cited decision whose span is over 1,200,000 characters, and a ticket whose own text is about 300,000.
BIG_LINE = "Line {n:05d}: the harbour master reads every line of this text before the tide turns, and keeps it.\n"


def big_text(characters: int) -> str:
    lines, size, n = [], 0, 0
    while size <= characters:
        line = BIG_LINE.format(n=n)
        lines.append(line)
        size += len(line)
        n += 1
    return "".join(lines)


S4_REGISTER = register(entry(130, "A very long decision", body=big_text(1_200_000)), entry(131, "A short one"))
S4_SOURCES = ["DEC-130"]
S4_TICKET_BODY = big_text(300_000)
S4_INVALID_FACTS = 'budgets:\n  close_context_tokens: "abc"\n'

# S5: one cited decision in each state.
S5_REGISTER = register(
    entry(120, "A decision that stands"),
    entry(121, "Superseded by its status word", status="SUPERSEDED (owner, 2026-11-02)"),
    entry(122, "Superseded by a successor's Supersedes line"),
    entry(123, "Superseded by name", status="SUPERSEDED by DEC-128"),
    entry(124, "A retired decision", status="RETIRED (owner, 2026-11-03)"),
    entry(125, "A rejected decision", status="REJECTED (owner, 2026-11-03)"),
    entry(126, "A one-off already done", lines=[done_tags()]),
    entry(127, "The successor of DEC-122", status="ACCEPTED (owner, 2026-11-04) · **Supersedes:** DEC-122"),
    entry(128, "The successor of DEC-123"))
S5_SOURCES = [f"DEC-{n}" for n in range(120, 127)]
S5_APPLIED = ["DEC-120", "DEC-126"]
S5_NOT_STANDING = [{"id": "DEC-121", "status": "SUPERSEDED"}, {"id": "DEC-122", "status": "SUPERSEDED"},
                   {"id": "DEC-123", "status": "SUPERSEDED"}, {"id": "DEC-124", "status": "RETIRED"},
                   {"id": "DEC-125", "status": "REJECTED"}]

# S6 and F1
PLAIN_REGISTER = register(entry(110, "The plain decision"))
S6_MISSING = ["DEC-198", "DEC-199"]          # DEC-199 in sources, DEC-198 in decisions; the register holds neither
S6_KPI_ONLY = "DEC-199"
S6_UNNAMED = ["DEC-110", "DEC-111", "DEC-112"]  # cited where the path map names no register
S6_UNNAMED_REGISTER = register(entry(110, "Held by a file no path map names"), entry(111, "Also unnamed"),
                               entry(112, "Also unnamed"))
