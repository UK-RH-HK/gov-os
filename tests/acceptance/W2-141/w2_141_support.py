"""Support code for the W2-141 acceptance tests (standard library only).

W2-141 (DEC-1093 (2)): the guard refuses an engineer's Grep, Glob or recursive Bash search that can reach its own
ticket's acceptance folder unless the call excludes it, and the refusal names the folder and says how to exclude it.
The tests drive one public interface, the guard's decide function (``gov.guard.decide.decide``), with planted calls:
no hook process, no real session, no model.

**The code under test** is the tree ``PYTHONPATH`` names (the runner sets it per command, DEC-732), else the ``src``
folder of the worktree that holds this file.

**The planted project** (``make_project``), in pytest's temporary folder, under a temporary ``HOME``::

    <base>/home/proj/
      .tickets/DAEO-zz41.md               the engineer's ticket, WBS id W2-941 (the session's ticket)
      .tickets/DAEO-zz42.md               another ticket, WBS id W2-942
      tests/acceptance/W2-941/            the session ticket's acceptance folder: test_feature.py, README.md
      tests/acceptance/W2-942/            another ticket's tests: test_other.py (readable, DEC-963)
      tests/unit/test_unit.py  src/app/main.py  docs/notes.md  README.md
      governance/project/path-map.yaml    namespaces and the role_paths: block as the main tree holds it (G-14)
      governance/project/held-out.yaml    one held-out path, outside the project
      .claude/settings.json

Every planted file holds the word ``WORD``. Nothing here reads this repository's own tests, nor any engineer tree.
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

ENGINEER = "engineer"
ORCHESTRATOR = "orchestrator"
AUDITOR = "independent-auditor"          # a reviewer's session is an independent auditor's (fresh, read-only)
DESIGNER = "independent-test-designer"
PRODUCT_SPEC = "product-spec"
TICKET_LEAD = "ticket-lead"
RESEARCH = "research"

TICKET = "DAEO-zz41"
WBS = "W2-941"
OTHER_TICKET = "DAEO-zz42"
OTHER_WBS = "W2-942"
OWN = f"tests/acceptance/{WBS}"          # the session ticket's acceptance folder
OTHER = f"tests/acceptance/{OTHER_WBS}"  # another ticket's
# The exclusion the Grep tool's refusal names (the ticket's S1 wording), and the Grep glob that carries it.
GREP_EXCLUSION = f"!{OWN}/**"
# GNU grep's --exclude-dir matches a folder's base name when it recurses: only this form keeps the folder out
# (grep 3.11: --exclude-dir=tests/acceptance/W2-941 does not; README, discovery D-1).
GREP_DIR_EXCLUSION = f"--exclude-dir={WBS}"

WORD = "zqxw141"

PATH_MAP = """namespaces: {}
role_paths:
  engineer:
    reads_denied: ["{ticket_tests}"]
  independent-test-designer:
    reads_denied: ["{ticket_impl}"]
"""


def ticket_text(tk, wbs, role, allowed):
    return "\n".join([
        "---",
        f"id: {tk}",
        "status: in_progress",
        "deps: []",
        "links: []",
        "type: task",
        "priority: 1",
        f"assignee: {role}",
        f"external-ref: {wbs}",
        "tags: [wave-2, implementation, standard]",
        f"wbs_id: {wbs}",
        "title: W2-141 fixture ticket",
        "class: implementation",
        f"role: {role}",
        "depends_on: []",
        "allowed_paths:",
        *[f"- {p}" for p in allowed],
        "profile: STANDARD",
        "acceptance_tests:",
        f"  path: tests/acceptance/{wbs}/",
        "---",
        f"# {wbs} W2-141 fixture ticket",
        "",
    ])


FILES = {
    f".tickets/{TICKET}.md": ticket_text(TICKET, WBS, ENGINEER, ["src/**"]),
    f".tickets/{OTHER_TICKET}.md": ticket_text(OTHER_TICKET, OTHER_WBS, ENGINEER, ["docs/**"]),
    f"{OWN}/test_feature.py": f"# {WORD}\ndef test_the_feature():\n    assert True\n",
    f"{OWN}/README.md": f"# {WORD} the fixture's own acceptance map\n",
    f"{OTHER}/test_other.py": f"# {WORD}\ndef test_other():\n    assert True\n",
    "tests/unit/test_unit.py": f"# {WORD}\n",
    "src/app/main.py": f"VALUE = 1  # {WORD}\n",
    "docs/notes.md": f"notes {WORD}\n",
    "README.md": f"# W2-141 planted project {WORD}\n",
    "governance/project/path-map.yaml": PATH_MAP,
    "governance/project/held-out.yaml": "held_out_paths:\n  - /nowhere/w2-141-held\n",
    ".claude/settings.json": "{}\n",
}


@dataclass(frozen=True)
class Project:
    home: Path
    root: Path


def make_project(base):
    base = Path(base).resolve()
    home = base / "home"
    root = home / "proj"
    for rel, text in FILES.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    assert (root / OWN / "test_feature.py").is_file() and (root / OTHER / "test_other.py").is_file()
    return Project(home, root)


def load_decide():
    """The decide function of the tree under test (PYTHONPATH, else this worktree's src)."""
    if not os.environ.get("PYTHONPATH"):
        src = str(REPO_ROOT / "src")
        if src not in sys.path:
            sys.path.insert(0, src)
    from gov.guard.decide import decide
    return decide


# --------------------------------------------------------------------------
# Calls
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Call:
    """One planted tool call. ``kind`` names the exclusion forms its refusal must state (``HOW``)."""
    tool: str
    input: dict
    label: str
    kind: str = ""

    def __str__(self):
        return self.label


def slug(call):
    """A case's id: its label in letters, digits and dashes."""
    label = re.sub(r"(?<=[\s'])\.(?=[\s'`]|$)", "dot", call.label.replace("{root}", "ROOT"))
    return re.sub(r"[^A-Za-z0-9]+", "-", label).strip("-")


def grep(label, **fields):
    return Call("Grep", {"pattern": WORD, "output_mode": "content", **fields}, label, "Grep")


def glob_call(label, pattern, path=None):
    data = {"pattern": pattern}
    if path is not None:
        data["path"] = path
    return Call("Glob", data, label, "Glob")


def bash(command, kind=""):
    return Call("Bash", {"command": command, "description": "W2-141 acceptance call"}, f"Bash `{command}`", kind)


def read(path):
    return Call("Read", {"file_path": path}, f"Read {path}")


# The exclusion forms a refusal names, by the kind of call (the interface in README.md). A refusal holds the folder
# and at least one of its kind's forms.
HOW = {
    "Grep": (GREP_EXCLUSION,),
    # The Glob tool takes no exclusion: its refusal says to narrow the call's path or pattern.
    "Glob": ("path", "pattern"),
    "grep": (GREP_DIR_EXCLUSION,),
    "rg": ("-g", "--glob"),
    "find": ("-prune", "-not -path", "! -path"),
    # ag and ack: the ticket names no form; any exclusion form, theirs or another tool's, is taken.
    "ag": ("--ignore-dir", "--ignore", "-g", "--exclude-dir", "-prune", "-not -path"),
    "ack": ("--ignore-dir", "--ignore", "-g", "--exclude-dir", "-prune", "-not -path"),
}


@dataclass(frozen=True)
class Decision:
    decision: str
    reason: str

    def describe(self):
        return f"decision={self.decision} reason={self.reason[:500]!r}"


class Guard:
    """decide() for one planted project, the session's cwd its root."""

    def __init__(self, project, decide):
        self.project, self._decide = project, decide

    @property
    def root(self):
        return str(self.project.root)

    def ask(self, call, role=ENGINEER, ticket=TICKET, agent=None):
        """decide()'s answer; ``{root}`` in a field or a command is the planted project's absolute path."""
        data = {k: v.replace("{root}", self.root) if isinstance(v, str) else v for k, v in call.input.items()}
        got = self._decide(call.tool, data, self.root, role, ticket, subagent_type=agent, cwd=self.root)
        return Decision(*got)


def assert_allowed(result, call, who=""):
    assert result.decision == "allow", f"{who}{call} was not allowed: {result.describe()}"


def assert_refused(result, call, who=""):
    assert result.decision == "deny", f"{who}{call} was not refused: {result.describe()}"
    assert result.reason.strip(), f"{who}{call} was refused without a reason: {result.describe()}"


def assert_refused_saying_how(result, call, who=""):
    """Refused, and the reason names the folder and says how to exclude it (S1, S2; the second failure line)."""
    assert_refused(result, call, who)
    assert OWN in result.reason, (
        f"{who}{call} was refused, but the reason does not name the folder {OWN}/: {result.describe()}")
    forms = HOW[call.kind]
    assert any(f in result.reason for f in forms), (
        f"{who}{call} was refused, but the reason does not say how to exclude {OWN}/ "
        f"(one of {forms}): {result.describe()}")
