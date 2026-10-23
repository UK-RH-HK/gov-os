"""What ``gov close`` asks before any test, and what it judges a ticket by besides its tests (W2-07).

- A ticket is judged by its class (W2-H045): an evidence class on the files its ``acceptance_tests.evidence``
  names, a specification on its closed readiness record; any ticket's acceptance run is the folder its
  ``acceptance_tests.path`` declares (DEC-892, DEC-896 item 3).
- A decision-record commit of governance records only, under an ACCEPTED owner decision, is measured by that
  decision (DEC-896 item 1).
- The commit gates and the pre-close gate refuse before any test and spend no attempt (DEC-868): the ratchet's
  reading of its lists, the collection in one process, the disk's free space and inodes (DEC-898).
- A failed probe record whose every finding an ACCEPTED owner decision names is accepted (DEC-790, W2-M371).
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

from gov.cli.errors import GovError
from gov.close import history as _history, ratchet as _ratchet
from gov.close.repo import git as _git, read_commits as _read_commits

EVIDENCE_CLASSES = ("research", "audit", "integration", "coordination")
SPECIFICATION_CLASS = "specification"
# The governance records a decision-record commit may change (DEC-896 item 1), beside the register itself.
RECORD_PREFIXES = ("docs/plan/", "governance/project/prompts/", "governance/project/briefs/",
                   "governance/project/orchestration/")
DECISION_RECORD_TASK = "decision-record"  # the Task: of the orchestrator's decision-record commits (DEC-896)
DECISION_ID = re.compile(r"\bDEC-\d+\b")
ROW_ID = re.compile(r"\bW\d+-[A-Z]+\d+\b")
# DEC-898: the floors of the shared disk until W2-20's reading lands, as top-level keys of the path map.
GIB_FLOOR_KEY, INODES_FLOOR_KEY = "close_free_gib_floor", "close_free_inodes_floor"
DEFAULT_GIB_FLOOR, DEFAULT_INODES_FLOOR = 100, 10_000_000


def _finding(code: str, message: str, details: dict | None = None, findings: list[str] | None = None):
    from gov.close.command import _Finding

    return _Finding(code, message, details, findings)


# ---------------------------------------------------------------------------
# By class (W2-H045, DEC-892)
# ---------------------------------------------------------------------------

def ticket_class(front: dict) -> str:
    return str(front.get("class") or "").strip().lower()


def acceptance_folder(root: Path, front: dict, wbs: str) -> Path:
    """The ticket's acceptance folder: the one its file declares in ``acceptance_tests.path``, else
    ``tests/acceptance/<wbs>/``."""
    declared = (front.get("acceptance_tests") or {}).get("path") if isinstance(front.get("acceptance_tests"),
                                                                                dict) else None
    if isinstance(declared, str) and declared.strip().strip("/"):
        return Path(root) / declared.strip().strip("/")
    return Path(root) / "tests" / "acceptance" / wbs


def has_tests(folder: Path) -> bool:
    return folder.is_dir() and any(folder.rglob("test_*.py"))


def check_evidence(root: Path, ticket: str, front: dict) -> list[str]:
    """The evidence of a research, audit, integration or coordination ticket: each path its
    ``acceptance_tests.evidence`` names, committed, and for research a record of ``type: research``, for audit a
    report the audit validator passes. The paths judged; ``EVIDENCE_REFUSED`` naming each missing or failing
    piece."""
    from gov.check.audit_validator import validate_file
    from gov.tasks.tickets import frontmatter

    kind = ticket_class(front)
    named = (front.get("acceptance_tests") or {}).get("evidence") if isinstance(front.get("acceptance_tests"),
                                                                                dict) else None
    if not isinstance(named, list) or not named or not all(isinstance(p, str) and p.strip() for p in named):
        raise _finding("EVIDENCE_REFUSED", f"the {kind} ticket {ticket} names no evidence record under "
                       "acceptance_tests.evidence", {"ticket": ticket, "class": kind})
    lines = []
    for rel in named:
        rel = rel.strip()
        if not (Path(root) / rel).is_file():
            lines.append(f"the evidence {rel} of {ticket} does not exist")
        elif not _git(root, "ls-tree", "--name-only", "HEAD", "--", rel).strip():
            lines.append(f"the evidence {rel} of {ticket} is not committed")
        elif kind == "research" and (frontmatter(Path(root) / rel) or {}).get("type") != "research":
            lines.append(f"the evidence {rel} of {ticket} is no record of type: research")
        elif kind == "audit":
            found = validate_file(Path(root) / rel, str(root))
            if found is None or found:
                codes = sorted({str(f.get("code")) for f in found or []}) or ["unreadable"]
                lines.append(f"the audit report {rel} of {ticket} fails the audit validator: {', '.join(codes)}")
    if lines:
        raise _finding("EVIDENCE_REFUSED", "; ".join(lines), {"ticket": ticket, "class": kind}, lines)
    return [rel.strip() for rel in named]


def check_specification(root: Path, ticket: str) -> None:
    """A specification ticket's readiness record is closed: ``gov readiness --ticket`` passes (DEC-307)."""
    from gov.readiness import checker

    try:
        checker.check(root, checker.of_ticket(root, ticket))
    except GovError as e:
        raise _finding(e.code, f"the readiness record of {ticket} is not closed: {e.code}: {e.message}",
                       {"ticket": ticket, "readiness": e.code})


# ---------------------------------------------------------------------------
# Decision records (DEC-896 item 1)
# ---------------------------------------------------------------------------

def decision_records(root: Path, commits: list[dict], settings: dict) -> set[str]:
    """The commits of ``commits`` that are measured by their decision: decision-record commits (``Task:
    decision-record``) that change only governance records and name, in their subject or an ``Implements:``
    trailer, an ACCEPTED owner decision of the register. Any other commit that names no task stays unmeasured."""
    register = settings.get(_history.REGISTER_KEY)

    def a_record(path: str) -> bool:
        return path.startswith(RECORD_PREFIXES) or path in (register, _history.PATH_MAP_REL)

    candidates = [c for c in commits if c["trailers"].get("Task") == [DECISION_RECORD_TASK]
                  and c["paths"] and all(a_record(p) for p in c["paths"])]
    if not candidates:
        return set()
    entries = _history.register_entries(root, register)
    measured = set()
    for c in candidates:
        subject = _git(root, "log", "-1", "--format=%s", c["sha"])
        named = set(DECISION_ID.findall(subject + " " + " ".join(c["trailers"].get("Implements", []))))
        if any(_history.owner_decision(dec, entries)[0] is None for dec in named):
            measured.add(c["sha"])
    return measured


# ---------------------------------------------------------------------------
# The commit gates' reading of the ratchet's lists (DEC-757, P-IS-4 (a))
# ---------------------------------------------------------------------------

def check_ratchet_lists(root: Path, key: str) -> None:
    """Each entry of the path map's list ``key`` that the ratchet would not count, named before any test."""
    _, found = _ratchet.counted_entries(root, key)
    if found:
        lines = [f["message"] for f in found]
        raise _finding(_ratchet.REFUSED[key], "; ".join(lines), {"refused": found}, lines)


# ---------------------------------------------------------------------------
# The pre-close gate (DEC-868 item 1 (a)) and the disk (DEC-898)
# ---------------------------------------------------------------------------

def check_collection(root: Path, suites: list[tuple[Path, Path | None]], timeout) -> None:
    """Every suite the close will run, each ``(folder, ignored)`` collected in one process as the close runs it
    (the acceptance folder; ``tests/`` without it): a collection error refuses, naming each file that cannot be
    collected."""
    from gov.close.command import _INTERPRETER_PLACES, _INTERPRETER_VARIABLES, _TEST_RUNNER_VARIABLES, _started

    env = {key: value for key, value in os.environ.items()
           if key not in _TEST_RUNNER_VARIABLES
           and (not key.startswith(_INTERPRETER_VARIABLES) or key in _INTERPRETER_PLACES)}
    env["PYTHONPATH"] = str(Path(root) / "src")
    lines, collected = [], []
    for folder, ignored in suites:
        if not folder.is_dir():
            continue
        collected.append(folder.relative_to(root).as_posix())
        cmd = [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider", "--no-header",
               str(folder)] + (["--ignore", str(ignored)] if ignored is not None else [])
        try:
            done = _started(root, cmd, env, timeout)
        except subprocess.TimeoutExpired:
            lines.append(f"the collection of {collected[-1]} exceeded the time limit of {timeout}s")
            continue
        if done.returncode not in (0, 5):
            lines += sorted({line.strip() for line in done.stdout.split("\n") if line.startswith("ERROR ")}) or \
                [f"the collection of {collected[-1]} exited {done.returncode}: "
                 f"{(done.stdout + done.stderr).strip()[-300:]}"]
    if lines:
        lines = list(dict.fromkeys(lines))
        raise _finding("COLLECTION_FAILED", "the suites the close runs cannot be collected: " + "; ".join(lines),
                       {"collected": collected}, [f"collect: {line}" for line in lines])


def check_disk(root: Path, settings: dict) -> dict:
    """The free space and free inodes of the file system that holds the project, against the floors of the path
    map (DEC-898); ``DISK_BELOW_FLOOR`` (exit code 3, no attempt spent, no repair ticket) below either."""
    from gov.close.command import EXIT_CHECK_FAILED

    floors = {}
    for key, default in ((GIB_FLOOR_KEY, DEFAULT_GIB_FLOOR), (INODES_FLOOR_KEY, DEFAULT_INODES_FLOOR)):
        value = settings.get(key, default)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            raise GovError("INVALID_DISK_FLOOR", f"the floor {key} must be a number from zero up, got {value!r}",
                           {"argument": key, "floor": str(value)})
        floors[key] = value
    st = os.statvfs(root)
    reading = {"free_gib": round(st.f_bavail * st.f_frsize / 2 ** 30, 2), "free_inodes": st.f_favail,
               GIB_FLOOR_KEY: floors[GIB_FLOOR_KEY], INODES_FLOOR_KEY: floors[INODES_FLOOR_KEY]}
    below = []
    if reading["free_gib"] < floors[GIB_FLOOR_KEY]:
        below.append(f"free disk space {reading['free_gib']} GiB is below the floor of {floors[GIB_FLOOR_KEY]} GiB")
    if st.f_files and reading["free_inodes"] < floors[INODES_FLOOR_KEY]:  # a file system without inode counts
        below.append(f"free inodes {reading['free_inodes']} are below the floor of {floors[INODES_FLOOR_KEY]}")
    if below:
        raise GovError("DISK_BELOW_FLOOR", f"the disk of the project ({root}): " + "; ".join(below)
                       + ": the close does not run its regression", reading, exit_code=EXIT_CHECK_FAILED)
    return reading


# ---------------------------------------------------------------------------
# Probe findings accepted by an owner's decision (DEC-790, W2-M371)
# ---------------------------------------------------------------------------

def register_of(root: Path):
    """The register the project's path map names (DEC-479), or None."""
    import yaml

    try:
        path_map = yaml.safe_load((Path(root) / _history.PATH_MAP_REL).read_text(encoding="utf-8")) or {}
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return None
    return path_map.get(_history.REGISTER_KEY) if isinstance(path_map, dict) else None


def _brought_by_owner(root: Path, register: str, dec_id: str) -> bool:
    """Every commit that brought the entry's heading into the register carries ``Role: owner`` alone."""
    from gov.close.state import _entries

    def held(commit: str) -> bool:
        return bool(_entries(root, commit, register, dec_id))

    brought = [c for c in _read_commits(root, "HEAD", "--", register)
               if held(c["sha"]) and not any(held(parent) for parent in c["parents"])]
    return bool(brought) and all(c["trailers"].get("Role") == ["owner"] for c in brought)


def probe_accepted_by(root: Path, rel: str, front: dict, register) -> tuple[list[str], str | None]:
    """``(decisions, why)`` of a failed probe record: the ACCEPTED owner decisions that name the record (its id
    and path), its probed commit (full id) and, each with its list row, every finding it lists; or why not,
    naming each finding no such decision names."""
    findings = front.get("findings")
    if not isinstance(findings, list) or not findings:
        return [], "the record lists no findings an owner's decision could accept"
    entries = _history.register_entries(root, register)
    if isinstance(entries, str):
        return [], entries
    record_id, probed = str(front.get("id") or ""), str(front.get("probed_commit") or "")
    deciding = []
    for dec_id in sorted(entries):
        why, text = _history.owner_decision(dec_id, entries)
        if why is None and (not record_id or record_id in text) and rel in text and probed and probed in text \
                and _brought_by_owner(root, register, dec_id):
            deciding.append((dec_id, text))

    def named(finding: str, text: str) -> bool:
        word = re.compile(rf"(?<![\w-]){re.escape(finding)}(?![\w-])")
        return any(word.search(line) and ROW_ID.search(word.sub("", line)) for line in text.splitlines())

    unnamed = [str(f) for f in findings if not any(named(str(f), text) for _, text in deciding)]
    if unnamed:
        return [], (f"finding {', '.join(unnamed)} of the probe record {rel} is named, with its row, in no ACCEPTED "
                    "owner decision that names the record and its probed commit")
    return sorted({dec for dec, text in deciding if any(named(str(f), text) for f in findings)}), None


# ---------------------------------------------------------------------------
# An interrupted close (W2-M158)
# ---------------------------------------------------------------------------

def take_back_interrupted(root: Path, ticket: str, close_rel: str) -> list[str]:
    """Remove what an interrupted close of ``ticket`` left untracked: its close record and the checkpoints it
    writes (``ticket-transition``, "ticket closed"); the paths removed. Nothing else is touched."""
    from gov.tasks.tickets import frontmatter

    untracked = [p for p in _git(root, "ls-files", "--others", "--exclude-standard", "-z", "--",
                                 close_rel, f"docs/checkpoints/{ticket}/").split("\0") if p]
    removed = []
    for rel in untracked:
        front = frontmatter(Path(root) / rel) or {}
        ours = (rel == close_rel and front.get("type") == "close" and front.get("task") == ticket) or \
            (front.get("type") == "checkpoint" and front.get("task") == ticket
             and front.get("trigger") == "ticket-transition" and front.get("next_action") == "ticket closed")
        if ours:
            (Path(root) / rel).unlink()
            removed.append(rel)
    return removed
