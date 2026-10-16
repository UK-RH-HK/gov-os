"""Readers for the W1-42 acceptance tests: the exit report, its tables and its kept answers.

Nothing here writes, runs ``gov`` or reaches the network. Git is asked two read-only questions
(does a commit exist, is one commit an ancestor of another).
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXIT_REL = "docs/plan/wave-1-exit"
REPORT_REL = f"{EXIT_REL}/EXIT-REPORT.md"
EVIDENCE_REL = f"{EXIT_REL}/evidence"

PROGRAMMES = {"ORION": "a-dev", "ARGUS": "b-dev"}
CRITERIA = ("1", "2", "3", "4", "5", "doctor", "canaries", "check-and-commands")
VERDICTS = ("MET", "NOT MET", "NOT REACHED")
STEPS = ("discovery", "closed specification", "independent specification audit", "linked gap tickets",
         "independent tests", "implementation", "close", "CI", "merge")
WORKER_ROLES = ("engineer", "independent-test-designer", "independent-auditor")
STOPPING_REASONS = ("CLOSURE_COMPLETE", "SATURATED", "DEPTH_LIMIT_REACHED", "BUDGET_EXHAUSTED_WITH_GAPS",
                    "FACET_UNAVAILABLE", "UNRESOLVED_IDS")
OWNER_COMMANDS = ("gov pause", "gov status", "gov pause --off", "gov status")
SHARE_LIMIT = 15

# A backticked token that begins with one of these is read as a path of this repository.
PATH_PREFIXES = ("docs/", "governance/", ".tickets/", "tests/", "src/", "template/")
# Words that stand where a value should be.
PLACEHOLDERS = ("tbd", "todo", "to do", "n/a", "na", "?", "-", "--", "—", "–", "...", "…", "pending", "xxx",
                "none yet", "to be filled", "to be measured")


class Missing(Exception):
    """A file, a section, a table or a value the suite needs is not there."""


def norm(text) -> str:
    return re.sub(r"\s+", " ", str(text).replace("*", "").replace("`", "")).strip().lower()


def is_blank(cell) -> bool:
    """True for an empty cell and for a cell that holds only a placeholder."""
    return norm(cell).strip(" .") in ("",) + PLACEHOLDERS


def not_reached(cell) -> bool:
    return norm(cell).startswith("not reached")


def reason_after(cell, words: str) -> str:
    """What follows ``words`` in the cell (after a colon, a comma, a dash or an opening bracket)."""
    rest = norm(cell)[len(words):].strip(" :,;-–—()")
    return "" if is_blank(rest) else rest


def number(value):
    """``value`` as a number, or None. A truth value is not a number."""
    return value if type(value) in (int, float) else None


# ---------------------------------------------------------------------------
# The report
# ---------------------------------------------------------------------------

def load_report() -> str:
    path = ROOT / REPORT_REL
    if not path.is_file():
        raise Missing(f"{REPORT_REL} does not exist: the exit report has not been written")
    return path.read_text(encoding="utf-8")


def sections(report: str) -> dict:
    """Level-2 sections by normalised title, the leading number removed. Text outside a fence only."""
    found, title, fenced = {}, None, False
    for line in report.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
        heading = None if fenced else re.match(r"##\s+(?:\d+\.?\s+)?(.+?)\s*$", line)
        if heading:
            title = norm(heading.group(1))
            found[title] = []
        elif title is not None:
            found[title].append(line)
    return {name: "\n".join(lines) for name, lines in found.items()}


def section(report: str, title: str) -> str:
    """The one section whose title begins with ``title``."""
    hits = [text for name, text in sections(report).items() if name.startswith(norm(title))]
    if len(hits) != 1:
        raise Missing(f"{REPORT_REL}: {len(hits)} sections titled '## {title}', expected one")
    return hits[0]


def _cells(line: str) -> list:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def tables(text: str) -> list:
    """Every pipe table of ``text`` as a list of rows, each a dict from normalised header to cell."""
    found, lines, i = [], text.splitlines(), 0
    while i < len(lines) - 1:
        if lines[i].lstrip().startswith("|") and re.fullmatch(r"[\s|:\-]+", lines[i + 1]) and "-" in lines[i + 1]:
            header, rows, i = [norm(cell) for cell in _cells(lines[i])], [], i + 2
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                cells = _cells(lines[i])
                rows.append(dict(zip(header, cells + [""] * (len(header) - len(cells)))))
                i += 1
            found.append((header, rows))
        else:
            i += 1
    return found


def table(text: str, where: str, *columns: str) -> list:
    """The rows of the one table of ``text`` whose header holds every one of ``columns``."""
    wanted = [norm(column) for column in columns]
    hits = [rows for header, rows in tables(text) if all(column in header for column in wanted)]
    if len(hits) != 1:
        raise Missing(f"{REPORT_REL}, section '{where}': {len(hits)} tables with the columns "
                      f"{' | '.join(columns)}, expected one")
    return hits[0]


def field(text: str, where: str, key: str) -> str:
    """The value of the line ``- **Key:** value`` of ``text``."""
    for line in text.splitlines():
        hit = re.match(r"\s*[-*]\s+\*\*(.+?):?\*\*:?\s*(.*)$", line)
        if hit and norm(hit.group(1)).rstrip(":") == norm(key):
            if is_blank(hit.group(2)):
                raise Missing(f"{REPORT_REL}, section '{where}': the line '- **{key}:**' holds no value")
            return hit.group(2).strip()
    raise Missing(f"{REPORT_REL}, section '{where}': no line '- **{key}:** ...'")


def paths_in(text: str) -> list:
    """The repository paths ``text`` names: backticked tokens that begin with a known prefix."""
    return [token.split("#")[0] for token in re.findall(r"`([^`\s]+)`", text) if token.startswith(PATH_PREFIXES)]


def evidence_path(text: str, where: str) -> str:
    """The one path under the evidence folder that ``text`` names."""
    hits = sorted({path for path in paths_in(text) if path.startswith(EVIDENCE_REL + "/")})
    if len(hits) != 1:
        raise Missing(f"{REPORT_REL}, {where}: {len(hits)} paths under {EVIDENCE_REL}/ named, expected one")
    return hits[0]


# ---------------------------------------------------------------------------
# Kept answers
# ---------------------------------------------------------------------------

def load_text(name: str) -> str:
    rel = name if name.startswith(EXIT_REL) else f"{EVIDENCE_REL}/{name}"
    path = ROOT / rel
    if not path.is_file():
        raise Missing(f"{rel} does not exist: that answer of the exit run has not been kept")
    return path.read_text(encoding="utf-8")


def load_json(name: str):
    text = load_text(name)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise Missing(f"{name} is not JSON ({exc}): keep the answer as the command printed it under --json")


def find_key(value, key: str) -> list:
    """Every value stored under ``key`` anywhere in a parsed answer."""
    if isinstance(value, dict):
        return [v for k, v in value.items() if k == key] + [hit for v in value.values() for hit in find_key(v, key)]
    if isinstance(value, list):
        return [hit for item in value for hit in find_key(item, key)]
    return []


def family_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(name).lower()).strip("-")


# ---------------------------------------------------------------------------
# The repository
# ---------------------------------------------------------------------------

def wave_1_tickets() -> dict:
    """``{wbs_id: ticket id}`` of every ticket file whose ``wbs_id`` begins with ``W1-``."""
    found = {}
    for path in sorted((ROOT / ".tickets").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        hit = re.search(r"^wbs_id:\s*(W1-\d+)\s*$", text, re.M)
        if hit:
            found[hit.group(1)] = path.stem
    return found


def reserved_commands() -> list:
    """The reserved command names of the command line, read from its source (CAP-28.b)."""
    source = (ROOT / "src/gov/cli/main.py").read_text(encoding="utf-8")
    return re.findall(r'^\s+Command\("([a-z]+)",', source, re.M)


def command_module(name: str) -> bool:
    return any((ROOT / rel).is_file() for rel in (f"src/gov/{name}/command.py", f"src/gov/cli/commands/{name}.py"))


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=False)


def commit_of(text: str):
    """The first commit id in ``text`` that this repository holds, or None."""
    for token in re.findall(r"\b[0-9a-f]{7,40}\b", text):
        if _git("cat-file", "-e", f"{token}^{{commit}}").returncode == 0:
            return token
    return None


def is_ancestor(older: str, newer: str) -> bool:
    return _git("merge-base", "--is-ancestor", older, newer).returncode == 0
