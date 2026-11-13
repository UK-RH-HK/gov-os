"""W2-113 acceptance support: a planted product adopted at stage A0, and the install rule judged in it.

Everything is read relative to the repository this file sits in (``REPO_ROOT``), so that merged into the ticket's
worktree the cases judge that worktree's ``src/`` and ``template/`` (DEC-732).

- **The planted repository** (Interface I3): W2-90's ``generate_project`` (copier, then ``rulesync generate``), copied
  into a folder named ``PROJECT`` (the product's name: the template asks no name, so the name is the repository's
  folder), the fixture tickets planted and committed, the tree clean. Generated once per session.
- **Adopted:** ``gov adopt --lite --stage A0`` as a child process (W2-23's ``run_gov``: ``python -m gov.cli.main``,
  this worktree's ``src`` on ``PYTHONPATH``, the repository as the working folder and root). No hand edit of the roster
  or of a ticket between that run and the guard's calls.
- **The guard's decision** is the kernel hook's, as W2-110's suite puts a call through it (``w2_110_support.call``:
  every PreToolUse line the generated settings register for Bash, through ``sh -c``, ``GOV_ROLE`` and ``GOV_TICKET`` as
  the session declares them). Commands are only text in the hook's input: nothing is installed.

W2-110's own module is imported, not copied (``w110``): the product generator, sessions, ``call``, and two predicates.
"""

from __future__ import annotations

import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
_TESTS = REPO_ROOT / "tests" / "acceptance"
for _suite in ("W2-110", "W2-23"):
    if str(_TESTS / _suite) not in sys.path:
        sys.path.insert(0, str(_TESTS / _suite))

import w2_110_support as w110  # noqa: E402  (the product, its sessions, ``call``, the predicates)
import w2_23_support as w23  # noqa: E402  (``gov adopt`` as a child process, git, the clean-tree check)

ROSTER_REL = w110.ROSTER_REL            # governance/project/roster.yaml
KEY = w110.KEY                          # coordination_ticket
TICKETS_REL = ".tickets"
TK_REL = "governance/kernel/bin/tk"
A0_RECORD = w23.RECORD["A0"]            # governance/adoption/A0-safety-baseline.md
PROJECT = "harbour"                     # the folder name of every planted repository: "<PROJECT> coordination"
TITLE = f"{PROJECT} coordination"
ADOPTER = "adopter-w2-113"
INSTALLS = ("pip3 install requests", "npm i left-pad")
INSTALL = INSTALLS[0]

# Tickets every planted repository holds before adoption (committed). The coordination ticket is not among them: A0
# creates it. ``OTHER`` is a second orchestration ticket; the others are the workers' own.
OTHER = w110.OTHER_ORCHESTRATION
ENGINEERING = w110.ENGINEERING
AUDIT = w110.AUDIT
PLANTED_TICKETS = (OTHER, ENGINEERING, AUDIT)


# ---------------------------------------------------------------------------------------------------------------
# What a repository holds: tickets, roster, commits
# ---------------------------------------------------------------------------------------------------------------

def ticket_files(project: Path) -> set:
    folder = Path(project) / TICKETS_REL
    return {p.name for p in folder.glob("*.md")} if folder.is_dir() else set()


def roster_bytes(project: Path):
    path = Path(project) / ROSTER_REL
    return path.read_bytes() if path.is_file() else None


def roster_data(project: Path):
    """The roster parsed, or ``None`` where there is none."""
    raw = roster_bytes(project)
    return None if raw is None else yaml.safe_load(raw.decode("utf-8"))


def commit_count(project: Path) -> int:
    return int(w23.git(project, "rev-list", "--count", "HEAD").strip())


def refs(project: Path) -> list:
    return w23.git(project, "for-each-ref", "--format=%(refname)", "refs/gov/").split()


@dataclass(frozen=True)
class Before:
    """What the planted repository held just before A0."""
    head: str
    commits: int
    tickets: frozenset
    roster: object          # the roster's bytes, or None
    refs: tuple


def snapshot(project: Path) -> Before:
    return Before(w23.head(project), commit_count(project), frozenset(ticket_files(project)),
                  roster_bytes(project), tuple(refs(project)))


def read_ticket(project: Path, ticket_id: str):
    """``(frontmatter, title)`` of ``.tickets/<id>.md``: the frontmatter parsed; the title is the frontmatter's
    ``title`` if it has one, else the first ``# `` heading of the body (where the vendored ``tk create`` writes it)."""
    text = (Path(project) / TICKETS_REL / f"{ticket_id}.md").read_text(encoding="utf-8")
    lines = text.split("\n")
    assert lines[0].strip() == "---", f"{ticket_id}.md has no frontmatter"
    end = [line.strip() for line in lines[1:]].index("---") + 1
    front = yaml.safe_load("\n".join(lines[1:end])) or {}
    title = front.get("title")
    if not isinstance(title, str):
        title = next((line[2:].strip() for line in lines[end + 1:] if line.startswith("# ")), None)
    return front, title


# ---------------------------------------------------------------------------------------------------------------
# The planted repository
# ---------------------------------------------------------------------------------------------------------------

def plant(generated: Path, destination: Path, roster: str | None = None, without_tk: bool = False) -> Path:
    """A copy of the generated product, as the folder ``destination/PROJECT``, with the fixture tickets and (if given)
    the roster's text, committed: a clean tree. ``without_tk`` removes the vendored ``tk`` (committed)."""
    project = w110.wiring.copy_project(generated, Path(destination) / PROJECT)
    path = project / ROSTER_REL
    if path.exists() or path.is_symlink():
        path.unlink()                       # whatever the template ships there: the case decides (none today)
    files = {}
    for ticket in PLANTED_TICKETS:
        files[f"{TICKETS_REL}/{ticket.id}.md"] = w110.w104.ticket_text(ticket.id, ticket.wbs, ticket.role, ticket.paths)
    for rel, content in w110.PRODUCT_FILES.items():
        files[rel] = content
    if roster is not None:
        files[ROSTER_REL] = roster
    for rel, text in files.items():
        target = project / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    if without_tk:
        (project / TK_REL).unlink()
    w110.wiring.copier_support.commit_all(project, "W2-113 fixture: the planted repository")
    assert w23.porcelain(project) == "", f"the planted repository is not clean:\n{w23.porcelain(project)}"
    return project


# ---------------------------------------------------------------------------------------------------------------
# The adoption
# ---------------------------------------------------------------------------------------------------------------

def run_a0(project: Path, box):
    """``gov adopt --lite --stage A0 --json`` in ``project`` (a child process)."""
    return w23.run_gov(project, box, "adopt", "--lite", "--stage", "A0", "--json", "--session", ADOPTER)


@dataclass
class Adopted:
    project: Path
    before: Before
    done: object            # the run of A0 (w2_23_support.Done)

    @property
    def created(self) -> set:
        """The ticket files A0 added to ``.tickets/``."""
        return ticket_files(self.project) - self.before.tickets

    def new_ticket(self) -> str:
        assert len(self.created) == 1, (
            f"A0 must create exactly one ticket in {TICKETS_REL}/ (the coordination ticket); the files it added: "
            f"{sorted(self.created)}\n{self.done.describe()}")
        return next(iter(self.created))[:-3]

    def key(self):
        data = roster_data(self.project)
        return data.get(KEY) if isinstance(data, dict) else None

    def a0_commit_files(self) -> list:
        return w23.changed_in(self.project, "HEAD")


def adopt(generated: Path, destination: Path, box, roster: str | None = None, without_tk: bool = False) -> Adopted:
    project = plant(generated, destination, roster, without_tk)
    before = snapshot(project)
    return Adopted(project, before, run_a0(project, box))


def assert_succeeded(adopted: Adopted):
    w23.succeeded(adopted.done)


# ---------------------------------------------------------------------------------------------------------------
# Rosters that are planted before adoption (Interface I2)
# ---------------------------------------------------------------------------------------------------------------

OTHER_CONTENT = (
    "# The project's roster: who may do what (planted by the W2-113 tests).\n"
    "roles:\n"
    "  orchestrator:\n"
    "    role_file: governance/kernel/roles/orchestrator.md   # the lead\n"
    "  engineer:\n"
    "    role_file: governance/kernel/roles/engineer.md\n"
    "\n"
    "budget_per_ticket: 12\n"
)


def roster_naming(value: str) -> str:
    return f"# planted: the coordination ticket is named already\n{KEY}: {value}\nroles:\n  engineer:\n    role_file: x.md\n"


# ---------------------------------------------------------------------------------------------------------------
# What a refusal must say (KPI success 2)
# ---------------------------------------------------------------------------------------------------------------

NAMES_THE_VARIABLE = "GOV_TICKET"

# "Claims a key was set" (README, "Success 2: the words"). A text that tells the reader the key exists, was written, or
# was written at adoption, as a fact. Narrow on purpose: a true text ("the key is not set", "adoption writes it when it
# runs", "set it ...", "to be set at adoption") passes.
_NOT_A_FACT = r"(?<!to be )(?<!should be )(?<!must be )(?<!will be )(?<!can be )(?<!shall be )"
_FALSE_CLAIMS = (
    # "set at adoption" / "was set at adoption" / "is set at adoption" stated, not asked for
    re.compile(_NOT_A_FACT + r"\bset at adoption\b", re.IGNORECASE),
    # "was set by adoption", "has been written at the last adoption", ...: a key said to be written by adoption
    re.compile(r"\b(?:was|were|has been|have been|is|are)\s+(?:set|written|added|created)\s+(?:at|by|during|in)\s+"
               r"(?:the\s+)?(?:last\s+|earlier\s+)?adoption\b", re.IGNORECASE),
    # "the key is already set" (not "is not already set")
    re.compile(r"(?<!not )(?<!never )\balready\s+(?:set|written)\b", re.IGNORECASE),
)
# Only where there is no key at all (no roster, or a roster without the key): a text that speaks of the key's value.
_CLAIMS_A_VALUE = re.compile(
    r"\bthe\s+(?:top-level\s+)?key\s+(?:'?coordination_ticket'?\s+)?(?:names|holds|is set|has the value|points)\b",
    re.IGNORECASE)


def claims_a_key_was_set(reason: str, key_exists: bool) -> list:
    """The false claims the refusal makes, as the matched phrases: ``[]`` for a text that makes none.

    For every case: "set at adoption" as a fact (not preceded by "to be", "should be", "must be", "will be", "can be",
    "shall be"); "was/were/has been/have been/is/are" + "set/written/added/created" + "at/by/during/in" + "[the]
    [last|earlier] adoption"; "already set/written" (not after "not"/"never"). Phrases such as "no key has been set",
    "the key is not set" and "adoption writes the key" are not claims.
    Where no key exists (``key_exists`` False): also "the key names/holds/is set/has the value/points ..."."""
    found = [m.group(0) for pattern in _FALSE_CLAIMS for m in pattern.finditer(reason)]
    if not key_exists:
        found += [m.group(0) for m in _CLAIMS_A_VALUE.finditer(reason)]
    return found


def names_the_variable(reason: str) -> bool:
    return NAMES_THE_VARIABLE in reason


def says_how_to_set_the_key(reason: str) -> bool:
    """W2-110's predicate: the file ``governance/project/roster.yaml`` and the key ``coordination_ticket`` are named."""
    return w110.says_how_to_set_the_key(reason)


# ---------------------------------------------------------------------------------------------------------------
# What A0's record must say when ``tk`` is missing (Interface I2 (iii), PKG-3 (b), DEC-1157 (15))
# ---------------------------------------------------------------------------------------------------------------

# The interface fixes no field name, so the record's TEXT is judged, not a key: the record names ``tk`` and, within a
# short span of the same text (YAML folding and line breaks are collapsed first), says a ticket was not made. Narrow on
# purpose: a record that is silent about ``tk`` fails; a record that names ``tk`` but says nothing negative about a
# ticket fails; "tk is missing: no coordination ticket was created", "coordination_ticket: none (tk missing)" and
# "skipped: tk not found, so the ticket and the key were not created" pass. (README, "The record says so".)
_TK_WORD = re.compile(r"(?<!\w)tk(?!\w)", re.IGNORECASE)
_NOT_MADE = re.compile(r"\b(?:no|not|none|null|never|without|skipped|skip|nothing)\b|n't\b", re.IGNORECASE)
_A_TICKET = re.compile(r"ticket", re.IGNORECASE)
_SPAN = 160


def says_no_ticket_was_created_because_tk_is_missing(record_text: str) -> bool:
    """The record names ``tk`` and, within ``_SPAN`` characters of it, speaks of a ticket in a negative way (no, not,
    none, null, never, without, skipped, nothing, n't)."""
    flat = " ".join(record_text.split())
    for found in _TK_WORD.finditer(flat):
        window = flat[max(0, found.start() - _SPAN): found.end() + _SPAN]
        if _NOT_MADE.search(window) and _A_TICKET.search(window):
            return True
    return False


def remove_tree(path: Path) -> None:
    w110.remove_tree(Path(path))
