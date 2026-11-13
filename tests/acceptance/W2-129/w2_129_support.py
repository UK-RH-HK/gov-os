"""W2-129's planted repositories, the ``gov links`` runner, the output reader and the oracles.

Two planted git repositories, built in a temporary folder, never this repository or its store:

- ``build_full`` (repository A): a register with every statement form, ARCHIVE-SUPERSEDED with §A and §B,
  DECISIONS-IN-FORCE, five tickets, close records, checkpoints, a lesson, plans, a kernel skill, a prompt, a brief,
  a ``contract.yaml`` with its generated master-rule records, code and tests, and a history of worker commits, a
  landing merge and a ``Task: decision-record`` commit. Its first commit (``root``) holds only a README, so
  ``--since <root>`` makes every record and every commit "changed".
- ``build_bare`` (repository B): a path map naming no register, no ``.tickets/``, no ``contract.yaml``.

``PLANTED`` lists every finding the planted defects must give, ``CONTROLS`` the places that must give none. The
oracles (``line_of``, ``status_line``, ``entry_span``, ``statement_pairs``) read the planted text, or the loader's own
``register_statements`` (the one pattern set the ticket names), never ``gov.links``.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]


def src_dir() -> Path:
    """The tree under test: the first entry of ``PYTHONPATH``, else this worktree's ``src``."""
    first = os.environ.get("PYTHONPATH", "").split(os.pathsep)[0]
    return Path(first).resolve() if first else WORKTREE / "src"


REGISTER = "docs/DECISION_REGISTER.md"
ARCHIVE = "governance/project/orchestration/ARCHIVE-SUPERSEDED.md"
IN_FORCE = "governance/project/orchestration/DECISIONS-IN-FORCE.md"
PATH_MAP = "governance/project/path-map.yaml"
CONTRACT = "docs/contract/contract.yaml"
MARK = ".gov-runtime/links/mark"
CODES = ("UNMARKED_CHANGE", "UNKNOWN_ID", "UNLINKED_ID", "STATUS_CONFLICT", "NOT_IN_FORCE_AS_RULE",
         "ENFORCES_SUPERSEDED")
ROLES = ("orchestrator", "product-spec", "engineer", "independent-test-designer", "independent-auditor", "research")
FIRST_LINE = re.compile(r"^gov links: (\d+) new since (\S+), (\d+) standing\b")

# ---------------------------------------------------------------------------------------------------------- git


def git_env(date: str = "2026-11-01T10:00:00+00:00") -> dict:
    """A pinned environment: no system or personal git configuration, a fixed identity and date."""
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_AUTHOR_NAME": "Planted",
                "GIT_AUTHOR_EMAIL": "planted@example.invalid", "GIT_COMMITTER_NAME": "Planted",
                "GIT_COMMITTER_EMAIL": "planted@example.invalid", "GIT_AUTHOR_DATE": date,
                "GIT_COMMITTER_DATE": date, "LC_ALL": "C"})
    return env


def git(repo: Path, *args: str, date: str = "2026-11-01T10:00:00+00:00") -> str:
    done = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, env=git_env(date), check=False)
    if done.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed in {repo}: {done.stderr}")
    return done.stdout.strip()


def write(repo: Path, rel: str, text: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def commit(repo: Path, subject: str, trailers: dict | None, day: int, paths: list[str] | None = None) -> str:
    """Commit ``paths`` (default: everything but the ignored runtime folder) with ``trailers``; its sha."""
    git(repo, "add", "--", *(paths or ["."]))
    body = "\n".join(f"{key}: {value}" for key, value in (trailers or {}).items())
    message = subject + (f"\n\n{body}\n" if body else "\n")
    git(repo, "commit", "-q", "-m", message, date=f"2026-11-{day:02d}T10:00:00+00:00")
    return git(repo, "rev-parse", "HEAD")


# ------------------------------------------------------------------------------------------------- repository A

PATH_MAP_TEXT = """\
# The planted repository's path map (W2-129's acceptance tests).
# The register's place stays where the window rule puts it (DEC-120).
namespaces:
  all:
    paths: ["**"]
decision_register: docs/DECISION_REGISTER.md
"""

REGISTER_TEXT = """\
# Decision register

The planted register of W2-129's acceptance tests.

### DEC-100: The base rule
- **Status:** ACCEPTED
- **Tags:** domain: records · scope: repository · lands in: docs/

The base rule holds.

### DEC-101: The first window rule
- **Status:** ACCEPTED

The first window is short.

### DEC-102: The second window rule
- **Status:** ACCEPTED · **Supersedes:** DEC-101
- **Tags:** domain: records · scope: repository · lands in: docs/

The second window is long.

### DEC-103: The first item list
- **Status:** ACCEPTED

The list has three items.

### DEC-104: The second item list
- **Status:** ACCEPTED · **Changes:** DEC-103 item 2

The second item is new.

### DEC-105: The marked rule
- **Status:** ACCEPTED · **Changed by:** DEC-106 (item 1)

The marked rule has two items.

### DEC-106: The rule over the marked rule
- **Status:** ACCEPTED · **Changes:** DEC-105 item 1

The first item is new.

### DEC-107: The old window
- **Status:** SUPERSEDED by DEC-108

The old window is 300.

### DEC-108: The new window
- **Status:** ACCEPTED · **Supersedes:** DEC-107
- **Tags:** domain: records · scope: repository · lands in: docs/

The new window is 600.

### DEC-109: The three points
- **Status:** ACCEPTED

Three points stand.

### DEC-110: The last point
- **Status:** ACCEPTED · **Supersedes:** the last point of DEC-109

The last point is new.

### DEC-111: The limit
- **Status:** ACCEPTED

The limit is ten.

### DEC-112: The new limit
- **Status:** ACCEPTED

The window of DEC-111 is amended by DEC-112.

### DEC-113: The landing rule
- **Status:** ACCEPTED

Landings carry their trailers.

### DEC-120: The proposed rule
- **Status:** PROPOSED

The proposal waits for the owner.

### DEC-121: The rejected rule
- **Status:** REJECTED

The owner declined it.

### DEC-122: A rule under the proposed rule
- **Status:** ACCEPTED · **Under:** DEC-120

It stands under the proposal.

### DEC-123: A rule under a missing rule
- **Status:** ACCEPTED · **Under:** DEC-999

It stands under nothing.

### DEC-124: The withdrawn rule
- **Status:** WITHDRAWN

It was taken back.

### DEC-130: The archived rule
- **Status:** ACCEPTED

The archived rule holds a window.

### DEC-131: The rule over the archived rule
- **Status:** ACCEPTED

The window is wider.

### DEC-132: The one-off
- **Status:** ACCEPTED

A one-off action.

### DEC-133: The finished one-off
- **Status:** ACCEPTED
- **Tags:** domain: records · scope: repository · lands in: docs/ · done

A finished one-off action.
"""

ARCHIVE_TEXT = """\
# Archive: superseded and spent decisions

The planted archive.

## A. Superseded or changed (from the register's status lines)
- DEC-105: changed by DEC-106.
- DEC-130: amended by DEC-131.

## B. Entries that are spent or product record
- DEC-132: the one-off. Spent.
- DEC-133: the finished one-off. Spent.
"""

IN_FORCE_TEXT = """\
# Decisions in force

The planted list of what holds.

## Standing
- DEC-100: the base rule.
- DEC-107: the old window.
"""


def ticket(tid: str, wbs: str, status: str, body: str) -> str:
    return (f"---\nid: {tid}\nstatus: {status}\ntype: task\nexternal-ref: {wbs}\nwbs_id: {wbs}\n{body}---\n"
            f"# {wbs}\n\nA planted ticket.\n")


T001 = ticket("DAEO-t001", "W2-901", "in_progress", """\
title: 'The planted ticket in progress'
links: [DAEO-gone]
parent: DAEO-t002
depends_on: [DAEO-t002]
sources:
- DEC-100
- DEC-120
- DEC-998
kpis:
  success:
  - 'The base rule holds [DEC-100, DEC-104]'
  - 'The rejected rule is cited [DEC-121]'
  failure:
  - 'Nothing breaks.'
acceptance_tests:
  path: tests/acceptance/W2-901/
""")

T002 = ticket("DAEO-t002", "W2-902", "closed", """\
title: 'The planted closed ticket'
sources:
- DEC-100
- DEC-120
- W2-L001
kpis:
  success:
  - 'The base rule holds [DEC-100]'
acceptance_tests:
  path: tests/acceptance/W2-902/
""")

T003 = ticket("DAEO-t003", "W2-903", "in_progress", """\
title: 'The planted ticket whose close record exists'
sources:
- DEC-100
kpis:
  success:
  - 'The base rule holds [DEC-100]'
acceptance_tests:
  path: tests/acceptance/W2-903/
""")

T004 = ticket("DAEO-t004", "W2-904", "open", """\
title: 'The planted open ticket'
sources:
- DEC-100
- DEC-107
kpis:
  success:
  - 'The base rule holds [DEC-100]'
acceptance_tests:
  path: tests/acceptance/W2-904/
""")

T005 = ticket("DAEO-t005", "W2-905", "in_progress", """\
title: 'The planted clean ticket'
sources:
- DEC-100
kpis:
  success:
  - 'The base rule holds [DEC-100]'
acceptance_tests:
  path: tests/acceptance/W2-905/
""")


def record(rid: str, kind: str, status: str, extra: str = "", body: str = "A planted record.\n") -> str:
    return f"---\nid: {rid}\ntype: {kind}\nstatus: {status}\n{extra}---\n\n{body}"


FILES_A = {
    PATH_MAP: PATH_MAP_TEXT,
    REGISTER: REGISTER_TEXT,
    ARCHIVE: ARCHIVE_TEXT,
    IN_FORCE: IN_FORCE_TEXT,
    ".tickets/DAEO-t001.md": T001,
    ".tickets/DAEO-t002.md": T002,
    ".tickets/DAEO-t003.md": T003,
    ".tickets/DAEO-t004.md": T004,
    ".tickets/DAEO-t005.md": T005,
    "docs/close/DAEO-t002/CL-DAEO-t002.md": record("CL-DAEO-t002", "close", "ACTIVE", "task: DAEO-t002\n"),
    "docs/close/DAEO-t003/CL-DAEO-t003.md": record("CL-DAEO-t003", "close", "ACTIVE", "task: DAEO-t003\n"),
    "docs/checkpoints/DAEO-t001/CP-DAEO-t001-0001.md": record("CP-DAEO-t001-0001", "checkpoint", "ACTIVE",
                                                              "task: DAEO-t001\n"),
    "docs/checkpoints/DAEO-t001/CP-DAEO-t001-0002.md": record("CP-DAEO-t001-0002", "checkpoint", "ACTIVE",
                                                              "task: DAEO-qqqq\n"),
    "docs/research/CP-R-0001.md": record("CP-R-0001", "checkpoint", "ACTIVE", "task: DAEO-rrrr\n"),
    "docs/audit/CL-A-0001.md": record("CL-A-0001", "close", "ACTIVE", "task: DAEO-aaaa\n"),
    "docs/lessons/L-0001.md": record("L-0001", "lesson", "ACTIVE",
                                     "constrains: [DAEO-t001, DAEO-nope]\nsources: [DEC-100, DEC-992]\n"),
    "docs/plan/PLAN-A.md": record("PLAN-A", "plan", "ACCEPTED", "decisions: [DEC-100, DEC-993]\n"),
    "docs/plan/WAVE_2_LIST.md": record("WAVE-2-LIST", "plan", "ACCEPTED", "decisions: [DEC-100]\n",
                                       "# The list\n\n| Row | Item |\n|---|---|\n| W2-L001 | a planted list row |\n"),
    "docs/contract/contract.yaml": "id: CONTRACT-v4\nstatus: ACCEPTED\nmaster_rules:\n- id: MR-1\n"
                                   "  title: Planted rule one\n  provider:\n  - W2-901\n  - W9-999\n"
                                   "- id: MR-2\n  title: Planted rule two\n  provider:\n  - W2-902\n",
    "docs/contract/master-rules/MR-1.md": record("MR-1", "specification", "PROPOSED", "title: Planted rule one\n"),
    "docs/contract/master-rules/MR-2.md": record("MR-2", "specification", "ACCEPTED", "title: Planted rule two\n"),
    "template/governance/kernel/skills/demo/SKILL.md": "---\nname: demo\ndescription: A planted kernel skill\n---\n"
                                                       "# Demo\n\n- Keep the base rule (DEC-100).\n"
                                                       "- Cite the window rule (DEC-120).\n"
                                                       "- Follow the missing rule (DEC-991).\n",
    "governance/project/prompts/w2.md": "# The planted prompt\n\n- Keep the base rule (DEC-100).\n"
                                        "- Apply the rejected rule (DEC-121).\n",
    "governance/project/briefs/b1.md": "# The planted brief\n\n- Use the withdrawn rule (DEC-124).\n",
    "src/app/__init__.py": "",
    "src/app/limits.py": "WINDOW = 300  # DEC-107: the window\n",
    "tests/unit/test_limits.py": "def test_window():\n    # DEC-995 fixes the window\n    assert True\n",
    "tests/acceptance/W2-902/README.md": "# W2-902\n",
    "tests/acceptance/W2-903/README.md": "# W2-903\n",
    "tests/acceptance/W2-905/README.md": "# W2-905\n",
}


def build_full(repo: Path) -> dict:
    """Repository A; ``{"repo", "root", "records", "c2", "c3", "landing", "c4", "c6"}``, each a full sha."""
    repo.mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    write(repo, ".gitignore", ".gov-runtime/\n")
    write(repo, "README.md", "# The planted repository A\n")
    shas = {"repo": repo, "root": commit(repo, "the planted root", None, 1)}
    for rel, text in FILES_A.items():
        write(repo, rel, text)
    shas["records"] = commit(repo, "the planted records",
                             {"Task": "DAEO-t002", "Implements": "DEC-100", "Role": "orchestrator"}, 2)
    git(repo, "checkout", "-q", "-b", "w2/W2-901")
    write(repo, "src/app/feature.py", "def feature():\n    return 1\n")
    shas["c2"] = commit(repo, "the feature", {"Task": "DAEO-t001", "Implements": "DEC-105", "Role": "engineer"}, 3)
    write(repo, "tests/unit/test_feature.py", "def test_feature():\n    assert True\n")
    shas["c3"] = commit(repo, "the feature's test",
                        {"Task": "DAEO-t001", "Implements": "DEC-120", "Role": "independent-test-designer"}, 4)
    git(repo, "checkout", "-q", "main")
    git(repo, "merge", "-q", "--no-ff", "w2/W2-901", "-m",
        "land W2-901\n\nTask: DAEO-t001\nImplements: DEC-113\nRole: orchestrator\n",
        date="2026-11-05T10:00:00+00:00")
    shas["landing"] = git(repo, "rev-parse", "HEAD")
    write(repo, "docs/notes.md", "Planted notes.\n")
    shas["c4"] = commit(repo, "the notes", {"Task": "DAEO-zzzz", "Implements": "DEC-997", "Role": "research"}, 6)
    write(repo, "README.md", "# The planted repository A\n\nThe records are planted.\n")
    shas["c6"] = commit(repo, "a decision record",
                        {"Task": "decision-record", "Implements": "DEC-100", "Role": "orchestrator"}, 7)
    return shas


def build_bare(repo: Path) -> dict:
    """Repository B: a path map naming no register; no tickets, no contract.yaml, no archive."""
    repo.mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    write(repo, ".gitignore", ".gov-runtime/\n")
    write(repo, "README.md", "# The planted repository B\n")
    shas = {"repo": repo, "root": commit(repo, "the bare root", None, 1)}
    write(repo, PATH_MAP, "# A path map that names no register.\nnamespaces:\n  all:\n    paths: [\"**\"]\n")
    write(repo, "src/main.py", "def main():\n    return 0\n")
    write(repo, "docs/guide.md", "# Guide\n\nA plain document.\n")
    shas["head"] = commit(repo, "the bare files", None, 2)
    return shas


def clone(shas: dict, target: Path) -> dict:
    """A copy of a planted repository (its working tree and git directory) a test may change."""
    shutil.copytree(shas["repo"], target, symlinks=True)
    return {**shas, "repo": target}


# ------------------------------------------------------------------------------------------------- running it


def child_env() -> dict:
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update({"PYTHONPATH": str(src_dir()), "PYTHONDONTWRITEBYTECODE": "1", "LC_ALL": "C.UTF-8",
                "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    for key in ("GOV_ROLE", "GOV_TICKET"):
        env.pop(key, None)
    return env


def no_command(done: subprocess.CompletedProcess) -> bool:
    """Whether the ``gov`` that ran has no ``links`` command (argparse's refusal of an unknown choice)."""
    return "invalid choice: 'links'" in done.stderr


def require(done: subprocess.CompletedProcess) -> subprocess.CompletedProcess:
    """Fails the test at once where the tree under test has no ``gov links`` (today's integrate)."""
    if no_command(done):
        pytest.fail("there is no `gov links` command in the tree under test (src/gov/links/command.py)")
    return done


def spawn(repo: Path, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """``gov links --root <repo> <args>`` in a child process of the tree under test, unchecked (for fixtures)."""
    return subprocess.run([sys.executable, "-m", "gov.cli.main", "links", "--root", str(repo), *args],
                          cwd=cwd or repo, capture_output=True, text=True, timeout=300, env=child_env())


def run_links(repo: Path, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """``spawn``, failing the test at once without the command."""
    return require(spawn(repo, *args, cwd=cwd))


class Finding:
    """One per-finding line: ``CODE ids ... | path:line | role | fix``."""

    def __init__(self, raw: str):
        self.raw = raw
        parts = [part.strip() for part in raw.split(" | ")]
        self.parts = parts
        self.head = parts[0]
        self.code = self.head.split()[0] if self.head.split() else ""
        where = parts[1] if len(parts) > 1 else ""
        found = re.fullmatch(r"(.+):(\d+)", where)
        self.path, self.line = (found.group(1), int(found.group(2))) if found else (where, None)
        self.role = parts[2] if len(parts) > 2 else ""
        self.fix = " | ".join(parts[3:]) if len(parts) > 3 else ""
        self.ids = set(re.findall(r"\b(?:DEC|DAEO|W\d+|CAP|MR|L)-[A-Za-z0-9.]+", self.head))

    def names(self, *ids: str) -> bool:
        """Whether the line's first field names each id as a whole word (never inside a path or a longer id)."""
        return all(re.search(rf"(?<![\w/-]){re.escape(i)}(?![\w/-])", self.head) for i in ids)

    def __repr__(self) -> str:
        return self.raw


class Output:
    def __init__(self, done: subprocess.CompletedProcess):
        self.done = require(done)
        self.code = done.returncode
        self.lines = done.stdout.splitlines()
        self.first = self.lines[0] if self.lines else ""
        head = FIRST_LINE.match(self.first)
        self.new, self.since, self.standing = (int(head.group(1)), head.group(2), int(head.group(3))) if head \
            else (None, None, None)
        self.findings = [Finding(line) for line in self.lines[1:] if line.split(" ", 1)[0] in CODES]

    def of(self, code: str, *ids: str, path: str | None = None) -> list[Finding]:
        return [f for f in self.findings if f.code == code and f.names(*ids) and (path is None or f.path == path)]

    def text(self) -> str:
        return self.done.stdout + self.done.stderr


def links(repo: Path, *args: str) -> Output:
    return Output(run_links(repo, *args))


# ------------------------------------------------------------------------------------------------- the oracles


def head_text(repo: Path, rel: str) -> str:
    return git(repo, "show", f"HEAD:{rel}") + "\n"


def line_of(repo: Path, rel: str, needle: str, start: int = 1) -> int:
    """The first line (1-based, from ``start``) of ``rel`` at HEAD that holds ``needle``."""
    for number, line in enumerate(head_text(repo, rel).split("\n"), 1):
        if number >= start and needle in line:
            return number
    raise AssertionError(f"{needle!r} not in {rel}")


def entry_lines(repo: Path, rid: str) -> range:
    """The lines of register entry ``rid``: its heading to the line before the next heading."""
    lines = head_text(repo, REGISTER).split("\n")
    first = next(n for n, line in enumerate(lines, 1) if line.startswith(f"### {rid}:"))
    last = next((n - 1 for n, line in enumerate(lines, 1) if n > first and line.startswith("#")), len(lines))
    return range(first, last + 1)


def entry_span(text: str, rid: str) -> str:
    lines = text.split("\n")
    first = next(n for n, line in enumerate(lines) if line.startswith(f"### {rid}:"))
    last = next((n for n, line in enumerate(lines) if n > first and line.startswith("#")), len(lines))
    return "\n".join(lines[first:last])


def status_line(text: str, rid: str) -> str:
    return next(line for line in entry_span(text, rid).split("\n")[1:] if line.strip())


def statement_pairs(repo: Path) -> set[tuple[str, str]]:
    """``(changed, changer)`` for each supersession or amendment the register (by the loader's
    ``register_statements``) or ARCHIVE-SUPERSEDED §A (by the loader's own ``_BY``, as the drift prototype reads it)
    states, whose changed entry's own text names none of its changers: the drift prototype's "no hint" rule."""
    sys.path.insert(0, str(src_dir()))
    from gov.store import loader

    text = head_text(repo, REGISTER)
    entries, _ = loader.register_entries(text)
    spans = {entry["id"]: entry["span"] for entry in entries}
    changers: dict[str, set] = {}
    for said in loader.register_statements(text, entries):
        if said["cls"] in ("supersede", "amend") and said["target"] in spans:
            changers.setdefault(said["target"], set()).add(said["source"])
    for line in head_text(repo, ARCHIVE).split("## B.")[0].split("\n"):
        if line.startswith("- DEC-"):
            head, _, tail = line[2:].partition(":")
            for by in loader._BY.finditer(tail):
                for target in re.findall(r"DEC-\d{3,}", head):
                    for source in re.findall(r"DEC-\d{3,}", by.group(2)):
                        changers.setdefault(target, set()).add(source)
    return {(target, source) for target, sources in changers.items()
            if not any(s in spans[target] for s in sources) for source in sources}


def role_of(path: str) -> str:
    """The fixed table of the ticket's KPI line, by path."""
    if path.startswith(("template/governance/kernel/", "docs/contract/")):
        return "product-spec"
    if path.startswith("src/"):
        return "engineer"
    if path.startswith("tests/"):
        return "independent-test-designer"
    if path.startswith("docs/audit/"):
        return "independent-auditor"
    if path.startswith("docs/research/"):
        return "research"
    return "orchestrator"


def tracked(repo: Path) -> set[str]:
    return set(git(repo, "ls-files").split("\n"))


def tree_digest(repo: Path) -> dict[str, str]:
    """``path -> sha256`` of every file under ``repo`` outside ``.git``, the mark left out."""
    found = {}
    for path in sorted(repo.rglob("*")):
        rel = path.relative_to(repo).as_posix()
        if rel == ".git" or rel.startswith(".git/") or not path.is_file() or rel == MARK:
            continue
        found[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return found


def git_state(repo: Path) -> str:
    """HEAD, every ref and the working tree's status: what a tool that writes no record leaves alone."""
    return json.dumps([git(repo, "rev-parse", "HEAD"), git(repo, "for-each-ref"),
                       git(repo, "status", "--porcelain", "--untracked-files=all")])


def json_findings(value) -> list[dict]:
    """Every dict carrying a ``code`` of the six, wherever it sits in the envelope."""
    if isinstance(value, dict):
        own = [value] if value.get("code") in CODES else []
        return own + [f for item in value.values() for f in json_findings(item)]
    if isinstance(value, list):
        return [f for item in value for f in json_findings(item)]
    return []
