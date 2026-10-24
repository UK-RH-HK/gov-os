"""``gov close`` command module (W1-30, DEC-317).

Closes a ticket after verifying acceptance tests, trailers, containment,
and (for FULL-profile tickets) the probe record. Tracks iteration counts
and opens repair tickets on failure.

Nothing is closed, and nothing is recorded, that was not measured (DEC-454,
DEC-470): an error of something this command calls refuses the close with
that thing's reason.

Two ways a close ends without closing, and neither becomes the other
(DEC-487, DEC-490). A finding about the ticket's work goes through
``_refuse``: counted, with a repair ticket, exit code 3. "Could not measure"
(the tree is not its commit, the record store is older than the commit, a
state file is no state, an invalid argument, an error of a tool) is a
``GovError`` raised as it is: exit code 1, not counted, no repair ticket.

A run does not end at its first finding (DEC-492): every gate is asked, and
the one refusal names every finding, counted once, with one repair ticket.
What a finding left unmeasurable is named in it as not measured.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from gov.cli.errors import GovError
from gov.close import (evidence as _evidence, gates as _gates, history as _history, ratchet as _ratchet,
                       select as _select, state as _state, tool as _tool)
from gov.close.repo import (commits_since as _commits_since, git as _git, names_no_task as _names_no_task,
                            read_commits as _read_commits, store_is_of_head as _store_is_of_head,
                            ticket_commits as _ticket_commits, tickets_of_head as _tickets_of_head,
                            tree_differences as _tree_differences)
from gov.close.state import (ESCALATION_AT, ESCALATION_OPTIONS as _ESCALATION_OPTIONS,
                             ESCALATION_REASON as _ESCALATION_REASON, count_path as _count_path,
                             read_count as _read_count, write_count as _write_count)
from gov.close.tool import open_repair_ticket as _open_repair_ticket, tk as _tk  # noqa: F401

DISPOSITIONS = ("repair", "reuse", "delete", "narrow", "defer", "owner")
DEFAULT_TIMEOUT = 120
# The project's settings for a close (DEC-549): top-level keys of its path map, as DEC-479's two are.
SETTINGS_FILE = "path-map.yaml"
TIMEOUT_KEY, WORKERS_KEY = "close_timeout", "close_workers"
AUTO_WORKERS = "auto"
NOT_MEASURED = "not measured"
# The counter's three shares (DEC-495), as the close record and the result state them.
SHARE_KEY, SHARE_PARTS = "governance_share", ("measured", "estimated", "total")
REGISTER_KEY = "decision_register"  # DEC-479's key of the path map: the register an owner's decision may be in
REVIEWER_ROLE = "independent-auditor"
PROBE_ROLE = "orchestrator"
PROBE_PASSED = ("pass", "passed")
_TEST_RUNNER_VARIABLES = ("PYTEST_ADDOPTS", "PYTEST_PLUGINS")
# The caller's environment gives the test runs no interpreter switch (DEC-500): no variable that speaks to
# Python is passed on but these, which say where installed packages are and where compiled files go, and
# change nothing of how a test runs.
_INTERPRETER_VARIABLES = "PYTHON"
_INTERPRETER_PLACES = ("PYTHONUSERBASE", "PYTHONPYCACHEPREFIX", "PYTHONDONTWRITEBYTECODE")

ACT_PATHS = (
    "docs/close/**",
    "docs/checkpoints/**",
    ".tickets/**",
    ".gov-runtime/iterations/**",
)
EXIT_CHECK_FAILED = 3
EXIT_BLOCKED = 4
EXIT_CODES = {
    EXIT_CHECK_FAILED: "verification failed (tests, governance checks, containment)",
    EXIT_BLOCKED: "blocked by escalation or human gate",
}

_GOVERNANCE_PREFIXES = (
    "governance/kernel/",  # the installed kernel (DEC-487)
    "template/governance/kernel/checks/",
    "template/governance/kernel/schemas/",
    "governance/project/",
    "template/governance/kernel/hooks/",
    "template/governance/kernel/skills/",
    "template/governance/kernel/policies/",
    "template/governance/kernel/roles/",
)


class _Finding(Exception):
    """A finding about the ticket's work, raised by a gate; ``run`` gives it to ``_refuse`` (DEC-455)."""

    def __init__(self, code: str, message: str, details: dict | None = None,
                 findings: list[str] | None = None, *, exit_code: int = EXIT_CHECK_FAILED,
                 not_measured: list[str] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}
        self.findings = findings or [message]
        self.exit_code = exit_code
        self.not_measured = not_measured or []  # what this finding left unmeasurable, by name (DEC-492)


def add_arguments(parser) -> None:
    parser.add_argument("ticket", help="the ticket id to close")
    parser.add_argument("--disposition", default=None,
                        help="finding disposition class")
    parser.add_argument("--owner-decision", default=None,
                        help="owner decision register id")
    parser.add_argument("--timeout", type=int, default=None,
                        help="test timeout in seconds")
    parser.add_argument("--ticket-session", metavar="<session id>[=<role>]", action="append", default=[],
                        help="a session of the ticket, as gov telemetry takes it, for the governance share "
                             "the close record states; repeatable")
    parser.add_argument("--full", action="store_true", default=False,
                        help="run the full regression, whatever the change (W2-66)")
    parser.add_argument("--check-result", metavar="<file>", default=None,
                        help="the pre-close gate's own gov check --json output, given to every test run "
                             "of the close as GOV_CLOSE_CHECK_RESULT (W2-66)")


def run(root: Path, args, config: dict):
    from gov.tasks.tickets import frontmatter, TICKETS_REL

    root = Path(root)
    ticket = args.ticket
    disposition = getattr(args, "disposition", None)
    owner_decision = getattr(args, "owner_decision", None)

    if disposition and disposition not in DISPOSITIONS:
        raise GovError("INVALID_DISPOSITION",
                        f"disposition must be one of {', '.join(DISPOSITIONS)}",
                        {"disposition": disposition, "valid": list(DISPOSITIONS)})
    settings = config.get(SETTINGS_FILE) or {}
    timeout = _time_limit(args.timeout, settings)
    workers = _workers(settings)

    ticket_path = root / TICKETS_REL / f"{ticket}.md"
    front = frontmatter(ticket_path)
    if front is None:
        raise GovError("TICKET_UNKNOWN",
                        f"{ticket} is not a ticket of this project",
                        {"ticket": ticket})
    if str(front.get("status", "")) == "closed":
        raise GovError("STALE_EVIDENCE",
                        f"ticket {ticket} is already closed",
                        {"ticket": ticket},
                        exit_code=EXIT_CHECK_FAILED)

    profile = str(front.get("profile", "STANDARD")).upper()
    wbs = front.get("wbs_id") or front.get("external-ref") or ticket

    # Owner decision or escalation in force (A6): before anything runs
    state = _read_count(root, ticket)
    if owner_decision and state["count"] < ESCALATION_AT:
        raise GovError("INVALID_DECISION",
                        "owner decision given but no escalation in force",
                        {"ticket": ticket})
    if not owner_decision and state["count"] >= ESCALATION_AT:
        raise _state.blocked("three consecutive non-converging iterations reached", state)

    # What is measured is the commit that is recorded, with records of that commit (DEC-487); what an
    # interrupted close of this ticket left is taken back first (W2-M158)
    _gates.take_back_interrupted(root, ticket, _close_record_rel(ticket))
    _check_tree(root, ticket)
    _check_store(root)
    if owner_decision:
        state = _state.lift_escalation(root, ticket, owner_decision, state, settings.get(REGISTER_KEY))

    # What the trailer gate judges: the base, the accepted history, a move of the base (DEC-704, DEC-734)
    try:
        history = _history.judged_history(root, settings)
    except ValueError as e:
        raise GovError("TRAILERS_BASE_UNKNOWN", str(e), {"ticket": ticket, _history.BASE_KEY:
                                                         str(settings.get(_history.BASE_KEY))})
    report = history["report"]

    commits = _ticket_commits(root, ticket)
    others = _commits_since(root, commits)
    tickets = _tickets_of_head(root)  # a Task: that names none of them names no task (DEC-500)
    inside, own = _work_of(front, ticket, wbs)
    ticket_input = {"id": ticket, "hash":
                    "sha256:" + hashlib.sha256(ticket_path.read_bytes()).hexdigest()}

    # Every gate is asked, whatever an earlier one found (DEC-492)
    found: list[_Finding] = []

    def gate(check, *given, **named):
        try:
            return check(*given, **named)
        except _Finding as f:
            found.append(f)

    # The commit gates, before any test (DEC-868 item 3, DEC-896 item 3): a refusal here spends no attempt
    brought = frozenset()  # the merges that are git's own merge on the probed paths (DEC-754); none on a refusal
    accepted_probes: dict = {}  # failed probe records accepted by an owner's decision (DEC-790)
    if profile == "FULL":
        brought = gate(_check_probe, root, ticket, commits, others, inside, own, tickets,
                       accepted=accepted_probes) or frozenset()
    gate(_check_trailers, root, commits, ticket, history)
    gate(_check_accepted_history, history["refused"])
    recorded = _gates.decision_records(root, others, settings)  # measured by their decision (DEC-896 item 1)
    gate(_check_unmeasured, ticket, [c for c in others if c["sha"] not in brought | recorded], own, tickets)
    for key in (_ratchet.ACCEPTED_REDS, _ratchet.LOAD_SENSITIVE):
        gate(_gates.check_ratchet_lists, root, key)
    if found:
        _refuse_for(root, ticket, found, disposition, None, [], report, counted=False)

    # The pre-close gate (DEC-868 item 1): the collection of every suite in one process, gov check, the checkpoint
    kind = _gates.ticket_class(front)
    folder = _gates.acceptance_folder(root, front, wbs)
    gate(_gates.check_collection, root, [(folder, None), (root / "tests", folder)], timeout)
    checked = gate(_check_governance_blocks, root, commits + [c for c in others if _names_no_task(c, tickets)],
                   every=True)
    gate(_check_checkpoint, root, ticket)  # Watchdog (B1)
    if found:
        _refuse_for(root, ticket, found, disposition, None, [], report, counted=False)
    disk = _gates.check_disk(root, settings)  # DEC-898: before the regression

    gate(_check_containment, root, commits)
    if kind == _gates.SPECIFICATION_CLASS:
        gate(_gates.check_specification, root, ticket)
    judged_on = gate(_gates.check_evidence, root, ticket, front) if kind in _gates.EVIDENCE_CLASSES else None
    # Acceptance tests, then the regression tests (A2): all of tests/ except
    # the ticket's acceptance folder. Both run to their end, in parallel, and the cases the project declares
    # as serial-only afterwards (DEC-527); ``test_runs`` are the runs as they were made.
    test_runs: list[dict] = []
    # DEC-757: where the path map has a list of known reds or load-sensitive cases, each run tells each test's
    # result, and the reds of the runs are judged by the lists, after both runs.
    told = {"results": {}, "rootdirs": {}, "env": None} \
        if any(settings.get(key) for key in (_ratchet.ACCEPTED_REDS, _ratchet.LOAD_SENSITIVE)) else None
    scope = _scope(root, ticket, wbs, args)  # W2-66: what the regression run selects, and its evidence
    no_counts = dict.fromkeys(("passed", "failed", "errors", "skipped"), 0)
    if kind in _gates.EVIDENCE_CLASSES and not _gates.has_tests(folder):  # judged on its evidence (W2-H045)
        test_counts = no_counts
    else:
        test_counts = gate(_check_acceptance, root, ticket, wbs, timeout, test_runs, workers, told, scope,
                           folder=folder)
    counts = gate(_check_tests, root, root / "tests", timeout, folder, test_runs, workers, told, scope)
    reds = gate(_check_reds, root, told, timeout) if told is not None else None
    packet = gate(_build_context, root, ticket)  # Context (DEC-454, DEC-470)

    evidence = _scope_evidence(root, scope)
    if found:
        _refuse_for(root, ticket, found, disposition, packet, test_runs, report, evidence)
    test_counts = {key: test_counts[key] + counts[key] for key in test_counts}

    mandatory = packet["mandatory"]
    commit_files = sorted({p for c in commits for p in c["paths"]})
    record = {
        "packet_hash": packet["hash"],
        "inputs": [ticket_input] + [{"id": item["id"], "hash": f"sha256:{item['sha256']}"}
                                    for item in mandatory],
        "requirements_implemented": _collect_requirements(commits),
        "decisions_applied": [item["id"] for item in mandatory
                              if item["authority"] == "decision"],
        "tests_produced": _collect_test_paths(root, wbs, commit_files),
        "tests_run": test_counts,
        "test_runs": test_runs,
        _evidence.KEY: evidence,
        "deviations": NOT_MEASURED,
        "skill_versions": _read_skill_versions(root),
        "commits": _commit_models(commits),
    }
    record.update(checked)
    record.update(reds or {})
    judged = _judged_by(kind, judged_on, accepted_probes, disk)  # what this close judged besides its tests
    record.update(judged)
    record[SHARE_KEY] = dict.fromkeys(SHARE_PARTS, NOT_MEASURED)
    record["created"] = _now()  # one time of the record, whether or not it is written again with its share

    close_record_path, checkpoint_path = _record_and_close(root, ticket, record, commit_files)
    # The record first, the share after it (DEC-495): the counter counts the close record itself.
    share = _governance_share(root, ticket, getattr(args, "ticket_session", None) or [])
    if share != record[SHARE_KEY]:
        try:
            _write_close_record(root, ticket, {**record, SHARE_KEY: share}, commit_files, checkpoint_path)
        except OSError:  # the record stays as it was written: it says "not measured", and so does the answer
            share = record[SHARE_KEY]

    # Reset iteration count on success (A6)
    if state["count"] or state.get("decision"):
        reset = {"count": 0, "last_failures": [], "outcomes": []}
        reset.update({key: state[key] for key in ("decision", "decisions") if state.get(key)})
        _write_count(root, ticket, reset)

    return {"ticket": ticket, "close_record": close_record_path,
            "checkpoint": checkpoint_path, "test_runs": test_runs, SHARE_KEY: share, **report, **(reds or {}),
            _evidence.KEY: evidence, **judged}


def _judged_by(kind: str, judged_on: list[str] | None, accepted_probes: dict, disk: dict) -> dict:
    """What the close record and the answer state of the gates of W2-07: the ticket's class, the evidence it was
    judged on (``class_evidence``: ``evidence`` is the regression's evidence block, W2-66), the decisions that
    accepted a failed probe's findings, the disk's reading."""
    judged = {"ticket_class": kind or "implementation", "disk": disk}
    if judged_on is not None:
        judged["class_evidence"] = judged_on
    if accepted_probes:
        judged["probe_accepted_by"] = accepted_probes
    return judged


def _time_limit(given, settings: dict):
    """The time limit of a test run in seconds: the argument's, else the project's (``settings``, its path
    map), else the default. ``INVALID_TIMEOUT`` when it is not a positive number: nothing has run (DEC-487)."""
    import math

    named = "--timeout" if given is not None else TIMEOUT_KEY
    limit = given if given is not None else settings.get(TIMEOUT_KEY, DEFAULT_TIMEOUT)
    if isinstance(limit, bool) or not isinstance(limit, (int, float)) or not math.isfinite(limit) or limit <= 0:
        raise GovError("INVALID_TIMEOUT",
                        f"the time limit ({named}) must be a positive number of seconds, got {limit!r}",
                        {"argument": named, "timeout": str(limit)})
    return limit


def _workers(settings: dict):
    """The number of workers of each parallel test run (DEC-549): the whole number the project's path map
    gives, else ``auto``, as many as the runner chooses. ``INVALID_WORKERS`` when the project wrote anything
    else: nothing has run, and nothing is read as ``auto`` or as a serial run."""
    workers = settings.get(WORKERS_KEY, AUTO_WORKERS)
    if workers != AUTO_WORKERS and (isinstance(workers, bool) or not isinstance(workers, int) or workers <= 0):
        raise GovError("INVALID_WORKERS",
                        f"the number of workers ({WORKERS_KEY}) must be a positive whole number or "
                        f"{AUTO_WORKERS}, got {workers!r}",
                        {"argument": WORKERS_KEY, "workers": str(workers)})
    return workers


def _refuse_for(root: Path, ticket: str, found: list[_Finding], disposition: str | None,
                packet: dict | None, test_runs: list[dict] | None = None, report: dict | None = None,
                evidence: dict | None = None, counted: bool = True) -> None:
    """The one refusal of a run, for every finding of its gates (DEC-492): each named once, in the gates'
    order. One gate's refusal is that gate's, with its code; several are ``CHECK_FAILED`` with each gate's
    part under ``parts``. ``test_runs`` are the runs made, stated as a passed close states them (DEC-566);
    ``report`` is what the trailer gate judged by (the base, the accepted history), stated as a passed close
    states it. A refusal of the commit gates or the pre-close gate is not ``counted`` (DEC-868 item 3)."""
    lines = list(dict.fromkeys(line for f in found for line in f.findings))
    not_measured = list(dict.fromkeys(part for f in found for part in f.not_measured))
    codes = sorted({f.code for f in found})
    if len(found) == 1:
        message, details = found[0].message, dict(found[0].details)
    else:
        message = ("tests or checks failed" if codes == ["CHECK_FAILED"] else
                   f"{len(lines)} findings refuse the close of {ticket} ({', '.join(codes)})")
        details = {"parts": [{"code": f.code, "message": f.message, **f.details} for f in found]}
    details["disposition"] = disposition or "unclassed"
    details["test_runs"] = test_runs or []
    details.update(report or {})
    if evidence is not None:  # W2-66: the refusal states its evidence as a passed close does
        details[_evidence.KEY] = evidence
    if not_measured:
        details["not_measured"] = not_measured
    context_reason = None
    if disposition:  # DEC-454: a class is given with the whole-system context, or says that it had none
        context_reason = next((f.message for f in found if f.code == "CONTEXT_FAILED"), None)
        if context_reason:
            details["context"] = context_reason
    else:
        message += "; findings are unclassed and await disposition"
        details["note"] = "findings await their class; use --disposition to classify"
    _refuse(root, ticket, codes[0] if len(codes) == 1 else "CHECK_FAILED", message, lines, details,
            exit_code=found[0].exit_code if len(found) == 1 else EXIT_CHECK_FAILED,
            disposition=disposition, context_hash=packet["hash"] if packet and disposition else None,
            context_reason=context_reason, not_measured=not_measured, counted=counted)


# ---------------------------------------------------------------------------
# Before anything is measured (DEC-487, DEC-490): "could not measure" is not a finding
# ---------------------------------------------------------------------------

def _check_tree(root: Path, ticket: str) -> None:
    """``TREE_NOT_COMMITTED`` when the working tree is not ``HEAD``, with the paths.

    The one path that refuses nothing is what a refused close of this ticket left: an untracked ticket
    file whose parent is the ticket (its repair ticket, DEC-490), where it could not be committed (AR-9).
    """
    from gov.tasks.tickets import TICKETS_REL, frontmatter

    def left_by_a_refusal(state: str, path: str) -> bool:
        if state != "??" or not path.endswith(".md") or path.rsplit("/", 1)[0] != TICKETS_REL:
            return False
        return (frontmatter(root / path) or {}).get("parent") == ticket

    differing = sorted({path for state, path in _tree_differences(root)
                        if not left_by_a_refusal(state, path)})
    if differing:
        raise GovError("TREE_NOT_COMMITTED",
                        "the working tree is not the commit being closed, so the close would measure "
                        f"another tree than it records: {', '.join(differing)}",
                        {"ticket": ticket, "paths": differing})


def _check_store(root: Path) -> None:
    """``STORE_STALE`` when the record store was built from another commit than the one being closed: the
    context would be built from superseded records. A project without a store is refused where its context
    is built (DEC-470)."""
    if _store_is_of_head(root) is False:
        raise GovError("STORE_STALE",
                        "the record store is not of the commit being closed; run gov rebuild, then close again",
                        {"head": _git(root, "rev-parse", "HEAD").strip()})


def _work_of(front: dict, ticket: str, wbs: str):
    """``(inside, own)``: whether a path is inside the ticket's allowed paths, and whether it is work on the
    ticket at all (inside them, one of its acceptance tests, or its own file; DEC-490).

    The patterns are read as the guard reads a ticket's ``allowed_paths``; this command has no pattern
    grammar of its own.
    """
    from gov.guard.decide import _match_pattern
    from gov.tasks.tickets import TICKETS_REL

    patterns = front.get("allowed_paths") or []
    if not isinstance(patterns, list) or not all(isinstance(p, str) for p in patterns):
        raise GovError("TICKET_INVALID",
                        f"the allowed_paths of {ticket} are not a list of patterns",
                        {"ticket": ticket})

    def inside(path: str) -> bool:
        return any(_match_pattern(path, pattern) for pattern in patterns)

    def own(path: str) -> bool:
        return (inside(path) or path == f"{TICKETS_REL}/{ticket}.md"
                or path.startswith(f"tests/acceptance/{wbs}/"))

    return inside, own


# ---------------------------------------------------------------------------
# The last step (DEC-487): nothing says the ticket closed unless it closed
# ---------------------------------------------------------------------------

def _record_and_close(root: Path, ticket: str, record: dict, commit_files: list[str]) -> tuple[str, str]:
    """Write the checkpoint and the close record, then close the ticket through the ticket tool; the paths
    of the two records. When the record cannot be written or the tool does not close the ticket, both
    records are taken back before the error is raised."""
    import os

    def cannot_record(e: OSError):
        return GovError("CLOSE_RECORD_FAILED", f"cannot write close record: {e}", {"ticket": ticket})

    close_path = root / _close_record_rel(ticket)
    try:  # the record of an earlier close of a reopened ticket is put back as it was
        earlier = close_path.read_bytes() if os.path.lexists(close_path) else None
    except OSError as e:
        raise cannot_record(e)
    checkpoint_path = _write_checkpoint(root, ticket)["path"]
    try:
        try:
            close_rel = _write_close_record(root, ticket, record, commit_files, checkpoint_path)
        except OSError as e:
            raise cannot_record(e)
        _tool.close(root, ticket)
    except GovError as failed:
        left = []
        for path, before in ((root / checkpoint_path, None), (close_path, earlier)):
            try:
                if before is not None:
                    _state.write_whole(path, before)
                elif os.path.lexists(path):
                    path.unlink()
            except OSError as e:
                left.append(f"{path.relative_to(root).as_posix()}: {e}")
        if left:
            failed.details["not_taken_back"] = left
            failed.message += "; a record of the close could not be taken back: " + "; ".join(left)
        raise
    return close_rel, checkpoint_path


# ---------------------------------------------------------------------------
# Context (DEC-454, DEC-470)
# ---------------------------------------------------------------------------

_REGISTER_HAZARDS = ("ACTIVE_SUPERSEDED", "DUPLICATE_ID", "OVERLAPPING_ID")


def _build_context(root: Path, ticket: str) -> dict:
    """The ticket's context packet, built by ``gov.context`` from the store as it is.

    A ``_Finding`` with the reason when the context gives an error (no store,
    a missing or superseded input, a contradiction), when W1-11's checker
    cannot run, or when it finds the register itself contradictory.
    """
    import sqlite3
    from gov.context import context as build_context
    from gov.decisions import check as check_decisions

    try:
        packet = build_context(root, ticket)
    except GovError as e:
        raise _Finding("CONTEXT_FAILED",
                       f"the context of {ticket} cannot be built: {e.code}: {e.message}",
                       {"ticket": ticket, "context_error": e.code, **e.details})
    except (sqlite3.Error, OSError) as e:
        raise _Finding("CONTEXT_FAILED",
                       f"the context of {ticket} cannot be built: the store cannot be read: {e}",
                       {"ticket": ticket})
    try:
        hazards = [f for f in check_decisions(root)
                   if f.get("code") in _REGISTER_HAZARDS]
    except GovError as e:
        raise _Finding("CONTEXT_FAILED",
                       f"the context of {ticket} cannot be built: the decisions "
                       f"could not be checked: {e.code}: {e.message}",
                       {"ticket": ticket, "decisions_error": e.code, **e.details})
    if hazards:
        codes = sorted({f["code"] for f in hazards})
        raise _Finding("CONTEXT_FAILED",
                       f"the context of {ticket} cannot be built: the decision "
                       f"register has findings ({', '.join(codes)})",
                       {"ticket": ticket, "decision_findings": hazards})
    return packet


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def _commit_models(commits: list[dict]) -> list[dict]:
    """Each of the ticket's commits, oldest first, with its role and the model
    its ``Co-Authored-By`` line names, as read; "not measured" without one (DEC-470)."""
    listed = []
    for c in reversed(commits):
        lines = [v for key, values in c["trailers"].items()
                 if key.lower() == "co-authored-by" for v in values]
        listed.append({
            "commit": c["sha"],
            "role": "; ".join(c["trailers"].get("Role", [])) or NOT_MEASURED,
            "model": "; ".join(lines) or NOT_MEASURED,
        })
    return listed


# ---------------------------------------------------------------------------
# Verification helpers
# ---------------------------------------------------------------------------

def _check_trailers(root: Path, commits: list[dict], ticket: str, history: dict) -> None:
    """Every commit of the ticket is somebody's and implements something (DEC-487): each trailer a commit
    lacks is a finding. Without a commit, what is judged of the ticket's commits was not measured.

    Judged are the commits after the project's trailers base (DEC-704) that no owner's decision accepted as
    history (DEC-734); a merge with nothing of its own needs no ``Implements:`` (DEC-436's merge form)."""
    if not commits:
        raise _Finding("TRAILER_MISSING",
                       f"no commits found with Task: {ticket} trailer",
                       {"ticket": ticket},
                       not_measured=[f"the containment of the commits of {ticket}: not measured, it has no commit"])
    judged = [c for c in commits if (history["after"] is None or c["sha"] in history["after"])
              and c["sha"] not in history["accepted"]]
    if not judged:  # nothing judged is not a clean history (DEC-479)
        raise _Finding("TRAILER_MISSING",
                       f"no commit of {ticket} is after the trailers base and outside the accepted history: "
                       "its trailers were not measured", {"ticket": ticket})
    lacking = [(c["sha"][:12], key) for c in judged for key in ("Implements", "Role")
               if not c["trailers"].get(key)
               and not (key == "Implements" and len(c["parents"]) > 1 and _history.adds_nothing(root, c["sha"]))]
    if lacking:
        lines = [f"commit {sha} lacks {key}: trailer" for sha, key in lacking]
        raise _Finding("TRAILER_MISSING", "; ".join(lines),
                       {"commit": lacking[0][0], "commits": sorted({sha for sha, _ in lacking}), "ticket": ticket},
                       lines)


def _check_accepted_history(refused: list[dict]) -> None:
    """An entry of the accepted history without an ACCEPTED owner decision that names its commit refuses
    (DEC-734); its commit stays judged."""
    if refused:
        lines = [entry["message"] for entry in refused]
        raise _Finding(_history.REFUSED, "; ".join(lines), {"refused": refused}, lines)


def _check_unmeasured(ticket: str, others: list[dict], own, tickets: frozenset[str]) -> None:
    """A commit in the ticket's range that names no task and changes the ticket's work (its acceptance
    tests, a path inside its allowed paths, its own file) refuses: no ticket measured it. What a commit
    that names another ticket changes is that ticket's, and any other path refuses nothing (DEC-490).
    ``tickets`` are the project's: a ``Task:`` that names none of them names no task (DEC-500)."""
    found = []
    for c in others:
        changed = [p for p in c["paths"] if own(p)] if _names_no_task(c, tickets) else []
        if changed:
            found.append({"commit": c["sha"][:12], "paths": changed})
    if found:
        lines = [f"commit {f['commit']} names no task and changes {', '.join(f['paths'])}: "
                 f"work on {ticket} that no ticket measured" for f in found]
        raise _Finding("WORK_WITHOUT_TASK", "; ".join(lines),
                       {**found[0], "ticket": ticket, "work_without_task": found}, lines)


def _check_containment(root: Path, commits: list[dict]) -> None:
    """W1-50's judgement of the ticket's commits (DEC-453): every finding
    refuses, as returned. This command has no rule of its own."""
    from gov.guard.containment import ContainmentError, judge_commits

    if not commits:  # nothing to judge: the finding "no commits" says of containment that it was not measured
        return
    try:
        judged = judge_commits(str(root), [c["sha"] for c in commits])
    except ContainmentError as e:
        raise GovError("CONTAINMENT_ERROR",
                        f"the containment judgement could not run: {e}",
                        {"commits": [c["sha"] for c in commits]})
    if judged:
        found = [{"commit": f.commit, "paths": list(f.paths), "reason": f.reason}
                 for f in judged]
        lines = [f"containment: commit {f['commit'][:12]}: "
                 f"{', '.join(f['paths'])}: {f['reason']}" for f in found]
        raise _Finding("CONTAINMENT_FINDING",
                       f"containment findings: {'; '.join(lines)}",
                       {"containment": found}, lines)


# ---------------------------------------------------------------------------
# Probe gate (FULL-profile tickets, A5)
# ---------------------------------------------------------------------------

def _check_probe(root: Path, ticket: str, commits: list[dict], others: list[dict], inside, own,
                 tickets: frozenset[str], accepted: dict | None = None) -> None:
    """The probe record of a FULL-profile ticket is evidence only if the implementer could not have written
    it (DEC-137, DEC-487). ``others`` are the other commits of the ticket's range, ``inside`` says whether a
    path is inside the ticket's allowed paths, ``own`` whether it is the ticket's work (``_work_of``),
    ``tickets`` are the project's. ``accepted`` gets, of each failed record an owner's decision accepts, the
    decisions (DEC-790).

    A commit of the ticket after the probed one refuses only for a path that is the ticket's work: inside its
    allowed paths, one of its acceptance tests, or its own file (DEC-581).

    Every probe record of the ticket is read (DEC-500): each is asked everything, so one that does not say
    that the probe of the final code passed refuses whatever another says, and the close needs one.

    Returns the merges after the probed commit that are git's own merge of their parents on the probed paths
    (DEC-739, DEC-754): neither stale nor work without a task."""
    from gov.tasks.tickets import TICKETS_REL, frontmatter

    def invalid(message: str, **details):
        return _Finding("PROBE_INVALID", message, {"ticket": ticket, **details}, not_measured=[
            f"what the probe gate of {ticket} asks after this finding: not measured, the gate ends at its first"])

    probe_dir = root / "docs" / "probes" / ticket
    if not probe_dir.is_dir():
        raise _Finding("PROBE_MISSING",
                       f"FULL-profile ticket {ticket} has no probe record",
                       {"ticket": ticket})

    # DEC-137: the reviewer wrote nothing. A commit with the reviewer's role
    # refuses wherever it lies in the ticket's range, whatever else it names.
    for c in commits + others:
        if REVIEWER_ROLE in c["trailers"].get("Role", []):
            raise invalid(f"commit {c['sha'][:12]} in the range of the ticket carries the "
                          f"reviewer's role ({REVIEWER_ROLE})", commit=c["sha"][:12])

    found = []
    for path in sorted(probe_dir.glob("*.md")):
        pf = frontmatter(path)
        if pf is None:
            raise invalid(f"probe file {path.name} has no readable YAML frontmatter",
                          file=path.name)
        if pf.get("type") == "probe" and pf.get("task") == ticket:
            found.append((path, pf))
    # W2-M209: a record whose probed commit (a full id) is an ancestor of another record's is of an earlier
    # round; it neither passes nor refuses. The record of the final code decides.
    probed_of = {path: _full_id(root, str(pf.get("probed_commit") or "")) for path, pf in found}
    rounds = set(filter(None, probed_of.values()))

    def earlier_round(path) -> bool:
        mine = probed_of[path]
        return bool(mine) and any(other != mine and not _git(root, "merge-base", "--is-ancestor", mine, other,
                                                             ok=(0, 1), code=True) for other in rounds)

    records, brought = 0, set()
    for path, pf in found:
        if earlier_round(path):
            continue

        # Committed, and by the orchestrator: every commit that wrote the record carries that role alone.
        rel = path.relative_to(root).as_posix()
        wrote = _read_commits(root, "HEAD", "--", rel)
        if not wrote:
            raise invalid(f"probe record {rel} is not committed", file=rel)
        for c in wrote:
            if c["trailers"].get("Role") != [PROBE_ROLE]:
                raise invalid(f"probe record {rel} was committed by {c['sha'][:12]} without the "
                              f"{PROBE_ROLE}'s role", file=rel, commit=c["sha"][:12])

        reviewer = pf.get("reviewer_session", "")
        implementer = pf.get("implementer_session", "")
        if not reviewer or not implementer:
            raise invalid("probe record missing session identifiers")
        if reviewer == implementer:
            raise invalid("the probe reviewer is the implementer")
        if pf.get("reviewer_wrote_nothing") is not True:
            raise invalid("the probe reviewer wrote to the repository")
        for field in ("commissioned_by", "judged_by"):
            if pf.get(field) != "orchestrator":
                raise invalid(f"probe {field} must be 'orchestrator', "
                              f"got '{pf.get(field, '')}'")
        judgement = str(pf.get("judgement", "")).strip()
        if not judgement:
            raise invalid("probe has no judgement")
        if judgement not in PROBE_PASSED:  # DEC-790: unless an owner's decision accepts its every finding
            decisions, why = _gates.probe_accepted_by(root, rel, pf, _gates.register_of(root))
            if why:
                raise invalid(f"the probe's judgement is {judgement!r}, not {' or '.join(PROBE_PASSED)}: {why}",
                              judgement=judgement)
            if accepted is not None:
                accepted[rel] = decisions
        if not pf.get("probed_commit"):
            raise invalid("probe record does not name the probed commit")
        probed = str(pf["probed_commit"])

        # Exit code 1 is git's answer "no" to both questions; any other failure is an error.
        commit_id = _git(root, "rev-parse", "--verify", "--quiet", probed + "^{commit}",
                         ok=(0, 1)).strip()
        if commit_id and commit_id != probed:
            raise invalid(f"the probed commit is given as {probed!r}, a name that moves, "
                          "not as a full commit id", probed_commit=probed)
        if not commit_id or _git(root, "merge-base", "--is-ancestor", probed, "HEAD",
                                 ok=(0, 1), code=True):
            raise invalid("probed commit is not an ancestor of HEAD",
                          probed_commit=probed)

        after = {c["sha"]: c for c in _read_commits(root, f"{probed}..HEAD")}
        measured = []  # the merges measured against git's own merge of their parents, oldest last
        for sha, c in after.items():
            if REVIEWER_ROLE in c["trailers"].get("Role", []):
                raise invalid("a commit between the probed commit and HEAD "
                              "carries the reviewer's role", commit=sha[:12])
            holds = any(not _git(root, "merge-base", "--is-ancestor", probed, p, ok=(0, 1), code=True)
                        for p in c["parents"]) if len(c["parents"]) > 1 else False
            if holds or (len(c["parents"]) > 1 and ticket in c["trailers"].get("Task", [])):
                # DEC-750, DEC-754 (P-5 (c)): every merge that holds the probed commit (the merge-back, a later
                # merge, inward, an octopus), and the ticket's own merge, whatever task it names, is measured on
                # the probed paths against git's own merge of its parents. Where git cannot compute that merge
                # (a conflict, an object it cannot read) the measure is the probed code itself: never a pass.
                expected = _history.own_merge(root, c["parents"])
                against = "git's own merge of its parents" if expected else \
                    "the probed code (git cannot compute its own merge of its parents)"
                dropped = [p for p in _history.differing(root, expected or probed, sha) if own(p)]
                if dropped:
                    raise invalid(f"merge {sha[:12]} {'holds' if holds else 'of the ticket does not hold'} the "
                                  f"probed commit and its probed paths are not {against}: {', '.join(dropped)}",
                                  commit=sha[:12])
                measured.append(sha)
                continue
            judged = own if len(c["parents"]) < 2 else inside  # a merge on neither side: as before (DEC-750)
            changed = [p for p in c["paths"] if judged(p)] if _names_no_task(c, tickets) else []
            if changed:  # DEC-490: work on the ticket's paths the probe did not see
                raise invalid(f"commit {sha[:12]} names no task and changes {', '.join(changed)} "
                              "after the probed commit: the probe is stale", commit=sha[:12])
        brought.update(measured)
        ticket_file = f"{TICKETS_REL}/{ticket}.md"
        for c in commits:
            sha = c["sha"][:12]
            if any(str(reviewer) in value
                   for values in c["trailers"].values() for value in values):
                raise invalid(f"commit {sha} trailer names the reviewer session",
                              commit=sha)
            if c["sha"] not in after or len(c["parents"]) > 1:
                continue  # a merge of the ticket after the probed commit is measured above
            if c["paths"] == [ticket_file] and c["trailers"].get("Role") in (["orchestrator"], ["owner"]):
                continue  # DEC-757 item 3: an integration-side edit of the ticket file is not the ticket's change
            for p in c["paths"]:
                if own(p):
                    # R-7: the refusal names the edit and the merge-backs that carry it in
                    carried = [m[:12] for m in measured if _carries(root, m, after[m]["parents"], c["sha"])]
                    raise invalid(f"ticket commit {sha} changes {p} after the probed commit"
                                  + (f", carried in by merge {', '.join(carried)}" if carried else ""),
                                  commit=sha, path=p)
        records += 1

    if not records:
        raise _Finding("PROBE_MISSING",
                       f"FULL-profile ticket {ticket} has no valid probe record",
                       {"ticket": ticket})
    return frozenset(brought)


def _carries(root: Path, merge: str, parents: list[str], commit: str) -> bool:
    """Whether ``merge`` brings ``commit`` to its first parent: it holds the commit and its first parent does not."""
    return bool(_git(root, "merge-base", "--is-ancestor", commit, parents[0], ok=(0, 1), code=True)) and \
        not _git(root, "merge-base", "--is-ancestor", commit, merge, ok=(0, 1), code=True)


def _full_id(root: Path, given: str) -> str | None:
    """``given`` where it is the full id of a commit; None otherwise."""
    commit = _history.commit_of(root, given)
    return commit if commit == given else None


# ---------------------------------------------------------------------------
# Test runner (A2)
# ---------------------------------------------------------------------------

def _check_tests(root: Path, test_path: Path, timeout: int, ignore: Path | None = None,
                 stated: list | None = None, workers=AUTO_WORKERS, told: dict | None = None,
                 scope: dict | None = None) -> dict:
    """The counts of a test run without a finding; ``CHECK_FAILED`` with its findings. With ``ignore`` the run
    is the regression run, which may collect nothing. ``stated`` gets the runs as they were made, ``told`` each
    test's result, ``scope`` the selection and the evidence (``_run_tests``)."""
    findings, counts = _run_tests(root, test_path, timeout, ignore=ignore, none_collected_ok=ignore is not None,
                                  stated=stated, workers=workers, told=told,
                                  **({"scope": scope} if scope is not None else {}))
    if findings:
        raise _Finding("CHECK_FAILED", "tests or checks failed", {"tests_run": counts}, findings)
    return counts


def _check_acceptance(root: Path, ticket: str, wbs: str, timeout: int, stated: list | None = None,
                      workers=AUTO_WORKERS, told: dict | None = None, scope: dict | None = None,
                      folder: Path | None = None) -> dict:
    """The counts of the ticket's acceptance run. The acceptance tests are part of the ticket's work
    (DEC-480): without one there is no run, and the refusal says of it that it was not measured (DEC-492).
    ``folder`` is the one the ticket declares (DEC-892), else ``tests/acceptance/<wbs>/``."""
    folder = folder or root / "tests" / "acceptance" / wbs
    if not folder.is_dir() or not any(folder.rglob("test_*.py")):
        raise _Finding("NO_ACCEPTANCE_TESTS",
                       f"no acceptance tests for {ticket} in {folder.relative_to(root).as_posix()}/",
                       {"ticket": ticket, "wbs": wbs},
                       not_measured=[f"the acceptance run of {ticket}: not measured, it has no acceptance tests"])
    return _check_tests(root, folder, timeout, stated=stated, workers=workers, told=told, scope=scope)


_HAS_PARALLEL_RUNNER = "import importlib.util, sys; sys.exit(importlib.util.find_spec('xdist') is None)"


def _run_tests(root: Path, test_path: Path, timeout: int,
               ignore: Path | None = None,
               none_collected_ok: bool = False,
               stated: list | None = None, workers=AUTO_WORKERS, told: dict | None = None,
               scope: dict | None = None) -> tuple[list[str], dict]:
    """Run pytest on ``test_path`` to its end: its findings and its counts, every case counted once.

    The run is parallel (DEC-527): the installed runner's ``-n`` with ``workers``, the project's number or
    ``auto`` (DEC-549), which changes how many workers run and never which tests. The cases the project's list declares
    for this run are kept out of it and run afterwards, alone and serially, as a run of their own with the
    time limit of a run. Where the test runner has no parallel plugin the one run is serial, list or no list,
    and says so. ``stated`` gets one object for each run made (its form, its seconds, its counts).

    A run over the time limit is a finding like a failing test (DEC-454).
    ``TEST_RUNNER_ABSENT`` when this interpreter has no pytest: nothing ran.
    A list that is no UTF-8 text is ``SERIAL_ONLY_LIST_UNREADABLE``, and a file of the project that would be
    loaded in the place of the plugin is a finding: in both no test is run (DEC-555).

    With ``told`` (a project whose path map has DEC-757's lists) every run tells each test's result into it, and
    a run whose every red is a test it named leaves them to ``_check_reds``: no finding of its own.
    """
    import importlib.machinery
    import importlib.util
    import os
    from gov.close.pytest_plugin import gov_close_results as results, gov_close_serial_only as serial_only

    counts = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}  # a skip is counted, not refused (DEC-500)
    if not test_path.is_dir():
        if none_collected_ok:
            return [], counts
        raise GovError("TESTS_MISSING", f"{test_path} is not a folder",
                        {"test_path": str(test_path)})
    if importlib.util.find_spec("pytest") is None:
        raise GovError("TEST_RUNNER_ABSENT",
                        f"pytest is not installed for {sys.executable}: no test was run",
                        {"python": sys.executable})

    rel = test_path.relative_to(root).as_posix()
    # The run is the suite's own (DEC-487): what the caller's environment would add to the test runner
    # (options, plugins), put before the project's own code (the caller's PYTHONPATH) or switch in the
    # interpreter (DEC-500: for one, PYTHONOPTIMIZE, which removes assertions) is not passed on.
    env = {key: value for key, value in os.environ.items()
           if key not in _TEST_RUNNER_VARIABLES
           and (not key.startswith(_INTERPRETER_VARIABLES) or key in _INTERPRETER_PLACES)}
    env["PYTHONPATH"] = str(root / "src")
    pytest = [sys.executable, "-m", "pytest"]
    options = ["-q", "-p", "no:cacheprovider", "--tb=line", "--no-header"]
    whole = [str(test_path)] + (["--ignore", str(ignore)] if ignore is not None else [])
    if scope is not None:  # W2-66: the selection, the per-test limit and the check result
        whole += _scope_form(root, scope, ignore)
        options += _scope_limit(root, scope, env)
        if told is not None:  # a run alone of a load-sensitive red has the same limit
            told["limit"] = _scope_limit(root, scope, env)

    # Asked of the interpreter of the run, in the run's environment: this process may have the plugin from
    # the caller's PYTHONPATH alone.
    parallel = _started(root, [sys.executable, "-c", _HAS_PARALLEL_RUNNER], env).returncode == 0
    if parallel:
        def within(entry: str, folder: Path | None) -> bool:
            return folder is not None and (entry.partition("::")[0] + "/").startswith(
                folder.relative_to(root).as_posix() + "/")

        try:
            listed = serial_only.entries(root)
        except UnicodeDecodeError as e:  # nothing is read as "no list" (DEC-555)
            raise _Finding("SERIAL_ONLY_LIST_UNREADABLE",
                           f"the serial-only list {serial_only.LIST_REL} is not UTF-8 text ({e}): which cases it "
                           "declares is not known, and no test was run",
                           {"list": serial_only.LIST_REL},
                           not_measured=[f"the test run of {rel}: not measured, the serial-only list cannot be read"])
        declared = [entry for entry in listed if within(entry, test_path) and not within(entry, ignore)
                    and (scope is None or ignore is None or _select.runs(entry, scope["ignore"], scope["deselect"]))]
        runs = [("parallel", pytest + whole + options + ["-n", str(workers)]
                 + (["--dist", str(scope["distribution"])] if scope is not None else []),
                 env, f"the test run of {rel}")]
        if declared:  # the plugin keeps them out of the parallel run; its folder holds nothing else
            # A file of the project found under the plugin's name before the plugin's folder would be loaded in
            # its place (DEC-555): the run's import path begins with the project's root and its src/.
            before = importlib.machinery.PathFinder.find_spec(serial_only.PLUGIN, [str(root), env["PYTHONPATH"]])
            if before is not None and before.origin:
                return [f"the test run of {rel}: {os.path.relpath(before.origin, root)} of the project is named "
                        f"like the plugin of the close ({serial_only.PLUGIN}) and would be loaded in its place: "
                        "no test was run"], counts
            plugin_env = {**env, serial_only.ROOT_VARIABLE: str(root), "PYTHONPATH": os.pathsep.join(
                [env["PYTHONPATH"], str(Path(serial_only.__file__).resolve().parent)])}
            plugin_env.pop(serial_only.GIVEN_VARIABLE, None)  # a close inside a run afterwards is given its own
            # In the run afterwards the plugin holds that every entry given names a case (DEC-549).
            runs = [("parallel", runs[0][1] + ["-p", serial_only.PLUGIN], plugin_env, runs[0][3]),
                    ("serial-afterwards", pytest + declared + options + ["-p", serial_only.PLUGIN],
                     {**plugin_env, serial_only.GIVEN_VARIABLE: "\n".join(declared)},
                     f"the serial run afterwards of the declared cases of {rel}")]
    else:
        declared = []
        runs = [("serial", pytest + whole + options, env, f"the test run of {rel}")]
    if told is not None:  # DEC-757: every run tells each test's result, under the plugin's name (DEC-555)
        before = importlib.machinery.PathFinder.find_spec(results.PLUGIN, [str(root), env["PYTHONPATH"]])
        if before is not None and before.origin:
            return [f"the test run of {rel}: {os.path.relpath(before.origin, root)} of the project is named like "
                    f"the plugin of the close ({results.PLUGIN}) and would be loaded in its place: no test was run"
                    ], counts
        folder = str(Path(results.__file__).resolve().parent)
        runs = [(form, cmd + ["-p", results.PLUGIN], {**run_env, results.ROOT_VARIABLE: str(root), "PYTHONPATH":
                 os.pathsep.join([run_env["PYTHONPATH"], folder])}, what) for form, cmd, run_env, what in runs]
        told["env"] = runs[0][2]

    findings: list[str] = []
    collected = False
    for form, cmd, run_env, what in runs:
        junit = None
        if scope is not None:  # W2-66: every run keeps its JUnit XML
            junit = _scope_junit(root, scope, "regression" if ignore is not None else "acceptance", form)
            cmd = cmd + ["--junitxml", str(root / junit), "-o", "junit_family=xunit1"]
        if told is None:
            found, ran = _one_test_run(root, cmd, run_env, timeout, what, rel)
        else:
            found, ran, results_of_run = _told_run(root, cmd, run_env, timeout, what, rel)
            told["results"].update(results_of_run.get("results", {}))
            told["rootdirs"].update(dict.fromkeys(results_of_run.get("results", {}), results_of_run.get("rootdir")))
            reds = [test for test, outcome in results_of_run.get("results", {}).items() if _ratchet.red(outcome)]
            if found and reds and len(reds) == ran["failed"] + ran["errors"] and \
                    all(line.startswith(("FAILED", "ERROR")) for line in found):
                found = []  # each red of the run is a test the plugin named: the path map's lists judge them
        collected = collected or found is not None
        findings += found or []
        counts = {key: counts[key] + ran[key] for key in counts}
        if junit is not None:
            scope["runs"].append(_evidence.read_junit(root, root / junit, test_path))
        if stated is not None:
            run = {"run": "regression" if ignore is not None else "acceptance", "form": form, **ran}
            if form == "parallel":
                run["workers"] = workers
                if scope is not None:
                    run["distribution"] = scope["distribution"]
            if form == "serial-afterwards":
                run["cases"] = declared
            if form == "serial":
                run["note"] = (f"not parallel: the test runner of {sys.executable} has no parallel plugin "
                               "(pytest-xdist), so every case ran in one serial run")
            stated.append(run)

    if not findings and not none_collected_ok:
        if not collected:
            findings = [f"no test was collected in {rel}"]
        elif not counts["passed"]:
            findings = [f"no test passed in {rel}: nothing of it was measured"]
    return findings, counts


def _started(root: Path, cmd: list[str], env: dict, timeout: int | None = None):
    """``cmd`` run to its end in the project's folder, in a process group of its own: its exit code and what it
    printed. At the time limit the whole group is ended before ``subprocess.TimeoutExpired`` is raised, so no
    worker of a parallel run lives on to write into the project (DEC-555); so it is when this command is
    itself ended."""
    import os
    import signal

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=str(root),
                               env=env, start_new_session=True)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except BaseException:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
        raise
    return subprocess.CompletedProcess(cmd, process.returncode, stdout, stderr)


def _one_test_run(root: Path, cmd: list[str], env: dict, timeout: int, what: str,
                  rel: str) -> tuple[list[str] | None, dict]:
    """One run of the test runner to its end: its findings (``None`` when it collected no test) and what the
    close states of it (its seconds and its counts)."""
    import re
    import time

    ran = {"seconds": 0.0, "passed": 0, "failed": 0, "errors": 0, "skipped": 0}
    started = time.monotonic()
    try:
        result = _started(root, cmd, env, timeout)
    except subprocess.TimeoutExpired:
        ran["seconds"] = round(time.monotonic() - started, 2)
        return [f"{what} exceeded the time limit of {timeout}s"], ran
    ran["seconds"] = round(time.monotonic() - started, 2)

    for line in reversed(result.stdout.split("\n")):
        found = {key: re.search(rf"(\d+)\s+{word}", line) for key, word in
                 (("passed", "passed"), ("failed", "failed"), ("errors", "error"), ("skipped", "skipped"))}
        if any(found.values()):
            ran.update({key: int(m.group(1)) for key, m in found.items() if m})
            break
    # The runner's last line of a run that came to its end: its counts, whatever they count, and its seconds.
    stated = any(re.search(r"\b\d+ [a-z]+\b.* in \d[\d.]*s\b", line) for line in result.stdout.split("\n"))

    rc = result.returncode
    if rc == 1 and "No module named pytest" in result.stderr:  # this process had it from the caller's PYTHONPATH
        raise GovError("TEST_RUNNER_ABSENT",
                        f"pytest is not installed for {sys.executable} without the caller's PYTHONPATH: "
                        "no test was run", {"python": sys.executable})
    if rc == 0 and not stated:  # a case that ended the runner's own process: no other run covers it (DEC-555)
        return [f"{what} ended with exit code 0 and stated no result: nothing of it was measured"], ran
    if rc == 0:
        return [], ran
    if rc == 5:
        return None, ran
    if rc == 2:
        failures = [line.strip() for line in
                    (result.stdout + "\n" + result.stderr).split("\n")
                    if "ERROR" in line or "SyntaxError" in line]
        ran["errors"] = ran["errors"] or len(failures)
        return failures or [f"collection error in {rel}"], ran
    # A parallel run goes on after a file that cannot be collected, and names it as an error beside the
    # failing cases; in the order of the names, since the workers end in any order.
    failures = sorted(line.strip() for line in result.stdout.split("\n")
                      if "FAILED" in line or line.startswith("ERROR "))
    return failures or [f"{what} exited {rc}: {result.stderr.strip()[-200:]}"], ran


def _told_run(root: Path, cmd: list[str], env: dict, timeout: int, what: str, rel: str):
    """``_one_test_run`` with the results plugin's file: its findings, its counts, and what the plugin told
    (``{}`` where it told nothing: a run cut short, or one that never reached its end)."""
    import os
    import tempfile
    from gov.close.pytest_plugin import gov_close_results as results

    handle, to = tempfile.mkstemp(prefix="gov-close-results-", suffix=".json")
    os.close(handle)
    try:
        found, ran = _one_test_run(root, cmd, {**env, results.TO_VARIABLE: to}, timeout, what, rel)
        try:
            told = json.loads(Path(to).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            told = {}
    finally:
        Path(to).unlink(missing_ok=True)
    return found, ran, told if isinstance(told, dict) and isinstance(told.get("results"), dict) else {}


def _check_reds(root: Path, told: dict, timeout: int) -> dict:
    """The reds of the close's runs judged by the path map's lists (DEC-757 items 2 and 4); what the close states
    of them (``accepted_reds``, ``load_sensitive``), or ``CHECK_FAILED`` with a finding for each.

    A red that a counted ``load_sensitive`` entry names is run again alone, in its own process (R-4); it counts as
    passed only when that run passes, and each re-run is reported with both results. No other test is run again.
    The results, so read, then go to the ratchet (``gov.close.ratchet.apply_accepted_reds``)."""
    results = told["results"]
    quarantined, found = _ratchet.counted_entries(root, _ratchet.LOAD_SENSITIVE)
    reruns = []
    for test, outcome in sorted(results.items()):
        entry = next((e for e in quarantined if _ratchet.covers(e["test"], test)), None)
        if entry is None or not _ratchet.red(outcome):
            continue
        alone = _alone(root, test, told, timeout)
        reruns.append({"test": test, "decision": entry["decision"], "in_run": _ratchet.FAILED, "alone": alone})
        if alone == _ratchet.PASSED:
            results[test] = _ratchet.PASSED
        else:
            found.append({"code": "LOAD_SENSITIVE_FAILED_ALONE", "test": test,
                          "message": f"the load-sensitive test {test} failed in the run and failed alone too"})
    verdict = _ratchet.apply_accepted_reds(root, results)
    found += verdict["findings"]
    stated = {_ratchet.ACCEPTED_REDS: verdict[_ratchet.ACCEPTED_REDS], _ratchet.LOAD_SENSITIVE: reruns}
    if found:
        raise _Finding("CHECK_FAILED", "tests or checks failed", {**stated, "red_findings": found},
                       [f["message"] for f in found])
    return stated


def _alone(root: Path, test: str, told: dict, timeout: int) -> str:
    """``passed`` when ``test`` passes run alone: a process of its own whose session holds that one node id, with
    the run's root folder and environment; ``failed`` otherwise, a run cut at the time limit included."""
    from gov.close.pytest_plugin import gov_close_results as results

    path, sep, rest = test.partition("::")
    cmd = [sys.executable, "-m", "pytest", str(root / path) + sep + rest, "--rootdir", told["rootdirs"][test],
           "-q", "-p", "no:cacheprovider", "--tb=line", "--no-header", "-p", results.PLUGIN] + told.get("limit", [])
    found, _, alone = _told_run(root, cmd, told["env"], timeout, f"the run alone of {test}", path)
    return _ratchet.PASSED if found == [] and alone.get("results") == {test: _ratchet.PASSED} else _ratchet.FAILED


# ---------------------------------------------------------------------------
# Governance checks (A7)
# ---------------------------------------------------------------------------

def _check_governance(root: Path, commits: list[dict], every: bool = False) -> tuple[dict, dict | None]:
    """W1-26's judgement of the project at the commit being closed, when the
    ticket's commits change a governance file (DEC-454, DEC-480).

    Returns what the close record states of it (``check_commit`` and the
    runner's result under ``governance_checks``; nothing when no governance
    file changed) and, where the runner says it blocks (the answer it returns
    beside its result, on which ``gov check`` forms its exit code), what it
    reports as blocking: the ``red_checks`` at hard-block and the
    ``red_families``, as it gave them; ``None`` where it does not block. This
    command has no rule of its own about checks and stands on no result but
    this run's: ``CHECKS_NOT_MEASURED`` when the runner's answer is not one of
    the commit being closed. With ``every`` it runs whatever the commits change (the pre-close gate, DEC-868).
    """
    if not every and not any(p.startswith(_GOVERNANCE_PREFIXES) for c in commits for p in c["paths"]):
        return {}, None

    from gov.check.runner import HARD_BLOCK, RED, run_checks

    def not_measured(why: str, **details):
        return GovError("CHECKS_NOT_MEASURED",
                        f"the governance checks were not measured: {why}", details)

    head = _git(root, "rev-parse", "HEAD").strip()
    result, blocks = run_checks(root)
    try:
        checks = result["checks"]
        ran_at = sorted({check["provenance"]["commit"] for check in checks})
        red = [check for check in checks
               if (check["id"], check["severity"], check["status"])[1:] == (HARD_BLOCK, RED)]
        red_families = sorted(name for name, family in result["families"].items() if family["status"] == RED)
    except (KeyError, TypeError, AttributeError) as e:
        raise not_measured(f"the runner's result has another shape ({e!r})")
    if ran_at != [head]:
        raise not_measured(f"the runner's result is of {', '.join(ran_at) or 'no check'}, "
                           f"not of the commit being closed ({head})",
                           commit=head, checked=ran_at)
    stated = {"check_commit": head, "governance_checks": result}
    return stated, {"red_checks": red, "red_families": red_families} if blocks else None


def _check_governance_blocks(root: Path, commits: list[dict], every: bool = False) -> dict:
    """What the close record states of the governance checks (A7, DEC-480); where the runner blocks, what it
    reports as blocking is a finding like a failing test."""
    changed = any(p.startswith(_GOVERNANCE_PREFIXES) for c in commits for p in c["paths"])
    checked, blocking = _check_governance(root, commits, True) if every and not changed else \
        _check_governance(root, commits)
    if blocking is None:
        return checked
    at = f"at commit {checked['check_commit'][:12]}"
    findings = [f"governance check {check['id']} is RED {at}: "
                f"{json.dumps(check.get('findings'), ensure_ascii=False)}" for check in blocking["red_checks"]]
    findings += [f"governance check family {name!r} is RED {at}" for name in blocking["red_families"]]
    if not any(blocking.values()):
        findings.append(f"the governance checks block {at}; the runner names no red check or family")
    raise _Finding("CHECK_FAILED", "tests or checks failed",
                   {"check_commit": checked["check_commit"], **blocking}, findings)


def _check_checkpoint(root: Path, ticket: str) -> None:
    """The watchdog's judgement of the ticket's latest checkpoint, with W1-25's thresholds (B1): any error of
    it refuses, with its own code."""
    from gov.checkpoint.command import MAX_AGE_MINUTES, MAX_COMMITS, MAX_CONTEXT
    from gov.checkpoint.record import watch as checkpoint_watch
    try:
        checkpoint_watch(root, ticket, max_age_minutes=MAX_AGE_MINUTES, max_commits=MAX_COMMITS,
                         max_context=MAX_CONTEXT, context_utilisation=None)
    except GovError as e:
        raise _Finding(e.code, e.message, e.details, exit_code=e.exit_code)


# ---------------------------------------------------------------------------
# The one path of a refusal for a finding about the ticket's work (DEC-455)
# ---------------------------------------------------------------------------

def _refuse(root: Path, ticket: str, code: str, message: str,
            findings: list[str], details: dict | None = None, *,
            exit_code: int = EXIT_CHECK_FAILED,
            disposition: str | None = None, context_hash: str | None = None,
            context_reason: str | None = None, not_measured: list[str] | None = None, counted: bool = True):
    """Count the refusal, open its repair ticket, write the escalation at the
    third, and raise the refusal. The next attempt after the third is blocked
    in ``run`` before anything runs. A refusal that is not ``counted`` (a gate before any test: an adoption gap,
    a baseline, DEC-868 item 3, W2-H038) leaves the counter as it is."""
    from datetime import datetime, timezone

    if not counted:
        details = {"findings": findings, **(details or {}), "counted": False}
        details["repair_ticket"] = _open_repair_ticket(
            root, ticket, findings, disposition, context_hash, context_reason, not_measured)
        raise GovError(code, message, details, exit_code=exit_code)
    state = _read_count(root, ticket)
    earlier = _state.read_escalation(root, ticket)
    outcomes = state["outcomes"] + [{
        "failures": sorted(set(findings)),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }]
    counted = {"count": state["count"] + 1,
               "last_failures": sorted(set(findings)), "outcomes": outcomes}
    counted.update({key: state[key] for key in ("decision", "decisions", "escalated_at") if state.get(key)})
    if counted["count"] >= ESCALATION_AT:
        # Where the escalation began: only a decision recorded after this commit lifts it (DEC-487)
        counted.setdefault("escalated_at", _git(root, "rev-parse", "HEAD").strip())
    _write_count(root, ticket, counted)

    if counted["count"] >= ESCALATION_AT:
        _state.write_escalation(root, ticket, {
            "ticket": ticket, "outcomes": outcomes,
            "reason": _ESCALATION_REASON, "options": _ESCALATION_OPTIONS,
            "escalated_at": counted["escalated_at"],
            "decisions_used": _state.decisions_used(state, earlier),
        }, findings=findings)

    details = {"findings": findings, **(details or {})}
    details["repair_ticket"] = _open_repair_ticket(
        root, ticket, findings, disposition, context_hash, context_reason, not_measured)
    cut = len(findings) - _tool.findings_held(findings)
    if cut and not details["repair_ticket"].startswith(_tool.NOT_OPENED):
        details["repair_ticket_findings_cut"] = cut  # what the ticket leaves out, said in it too
    raise GovError(code, message, details, exit_code=exit_code)


# ---------------------------------------------------------------------------
# Data collection for the close record
# ---------------------------------------------------------------------------

def _collect_requirements(commits: list[dict]) -> list[str]:
    return sorted({item for c in commits
                   for val in c["trailers"].get("Implements", [])
                   for item in val.replace(",", " ").split()})


def _collect_test_paths(root: Path, wbs: str, commit_files: list[str]) -> list[str]:
    paths = [f for f in commit_files
             if f.startswith("tests/") and f.endswith(".py") and "test_" in f]
    acc = root / "tests" / "acceptance" / wbs
    for f in sorted(acc.rglob("test_*.py")):
        rel = str(f.relative_to(root))
        if rel not in paths:
            paths.append(rel)
    return paths


def _governance_share(root: Path, ticket: str, sessions: list[str]) -> dict:
    """The three shares of the counter (``gov.telemetry``) for the sessions the caller names, each its figure
    or "not measured" as the counter gave it (DEC-495). With no session named, and where the counter refuses
    or cannot read, all three say "not measured": the share refuses no close. Counts only: nothing else of
    the counter's record is taken."""
    from gov.telemetry.counter import measure

    unmeasured = dict.fromkeys(SHARE_PARTS, NOT_MEASURED)
    if not sessions:
        return unmeasured
    try:
        shares = measure(root, ticket, sessions)[SHARE_KEY]
    except (GovError, OSError):
        return unmeasured
    return {part: shares[part] if type(shares.get(part)) in (int, float) else NOT_MEASURED for part in SHARE_PARTS}


def _read_skill_versions(root: Path) -> list[dict]:
    """The kernel's skills with the version each ``SKILL.md`` states, and the
    vendored ones, which carry none. A skill file whose frontmatter cannot be
    read is listed under its folder's name with "not measured".

    The kernel is the template's and the installed one (``governance/kernel/``), both where a project has
    both: a skill the two hold with one version is listed once, and one whose versions differ with each."""
    from gov.tasks.tickets import frontmatter

    versions = []
    for kernel in (root / "template" / "governance" / "kernel", root / "governance" / "kernel"):
        for files, versioned in ((sorted((kernel / "skills").glob("*/SKILL.md")), True),
                                 (sorted((kernel / "vendor").rglob("SKILL.md")), False)):
            for skill_file in files:
                front = frontmatter(skill_file)
                if front is None:
                    listed = {"name": skill_file.parent.name, "version": NOT_MEASURED}
                else:
                    version = front.get("version") if versioned else None
                    listed = {"name": str(front.get("name", skill_file.parent.name)),
                              "version": str(version) if version else "no version"}
                if listed not in versions:
                    versions.append(listed)
    return versions


# ---------------------------------------------------------------------------
# The scope of the regression run and its evidence (W2-66)
# ---------------------------------------------------------------------------

CHECK_RESULT_VARIABLE = "GOV_CLOSE_CHECK_RESULT"
_TIMEOUT_PLUGIN = "pytest_timeout"


def _scope(root: Path, ticket: str, wbs: str, args) -> dict:
    """What the regression run selects (``gov.close.select``), with what every run of the close needs: the
    folder of its JUnit XML (under ``.gov-runtime/``) and the pre-close gate's ``gov check`` result, copied byte
    for byte, where ``--check-result`` gives one. ``CHECK_RESULT_UNREADABLE`` when it cannot be read: nothing ran."""
    from datetime import datetime, timezone

    given = getattr(args, "check_result", None)
    content = None
    if given is not None:
        try:
            content = Path(given).read_bytes()
        except OSError as e:
            raise GovError("CHECK_RESULT_UNREADABLE", f"the check result {given} cannot be read: {e}",
                            {"check_result": str(given)})
    scope = _select.plan(root, wbs, full_asked=bool(getattr(args, "full", False)), ticket=ticket)
    folder = f"{_evidence.JUNIT_DIR}/{ticket}/{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}"
    (root / folder).mkdir(parents=True, exist_ok=True)
    check = None
    if content is not None:
        check = root / folder / "check-result.json"
        check.write_bytes(content)
    return {**scope, "folder": folder, "check_result": str(check) if check else None, "runs": [],
            "junit_xml": [], "limit": None}


def _scope_form(root: Path, scope: dict, ignore: Path | None) -> list[str]:
    """The regression run's ``--ignore`` and ``--deselect`` options; none for the acceptance run. A node id is
    given as the project's and as the ``tests`` folder's, the run's root folder where the project names none."""
    if ignore is None:
        return []
    form = [f"--ignore={root / rel}" for rel in scope["ignore"] if (root / rel).resolve() != Path(ignore).resolve()]
    for node in scope["deselect"]:
        form.append(f"--deselect={node}")
        if node.startswith("tests/"):
            form.append(f"--deselect={node[len('tests/'):]}")
    return form


def _scope_limit(root: Path, scope: dict, env: dict) -> list[str]:
    """The per-test limit of every run (pytest-timeout, the signal method) with its temp-folder retention
    (DEC-905), and the check result in ``env``.
    ``TIMEOUT_PLUGIN_ABSENT`` when the runs' interpreter cannot load pytest-timeout: nothing ran, nothing is
    recorded (DEC-892 b)."""
    import os

    if scope["check_result"]:
        env[CHECK_RESULT_VARIABLE] = scope["check_result"]
    else:
        env.pop(CHECK_RESULT_VARIABLE, None)
    for key, value in (scope.get("env") or {}).items():  # the nightly's coverage shim (gov.close.nightly)
        if key == "PYTHONPATH":
            if value not in env["PYTHONPATH"].split(os.pathsep):
                env[key] = os.pathsep.join([env[key], value])
        else:
            env[key] = value
    if scope["limit"] is None:
        if _started(root, [sys.executable, "-c", f"import {_TIMEOUT_PLUGIN}"], env).returncode != 0:
            raise GovError("TIMEOUT_PLUGIN_ABSENT",
                            f"pytest-timeout cannot be loaded by {sys.executable}: no test was run without its "
                            "per-test limit", {"python": sys.executable})
        scope["limit"] = (["-p", _TIMEOUT_PLUGIN] if env.get("PYTEST_DISABLE_PLUGIN_AUTOLOAD") else []) + \
            [f"--timeout={scope['per_test_timeout']}", "--timeout_method=signal",
             "-o", f"tmp_path_retention_policy={scope['tmp_path_retention_policy']}"]
    return list(scope["limit"])


def _scope_junit(root: Path, scope: dict, run: str, form: str) -> str:
    """The JUnit XML file of the next run, relative to the project."""
    rel = f"{scope['folder']}/{len(scope['junit_xml']) + 1:02d}-{run}-{form}.xml"
    scope["junit_xml"].append(rel)
    return rel


def _scope_evidence(root: Path, scope: dict | None) -> dict | None:
    """The evidence block (``gov.close.evidence``); a run that wrote no JUnit XML (one cut at the time limit)
    has a file that says so, so that each file the block names exists."""
    if scope is None:
        return None
    for rel in scope["junit_xml"]:
        if not (root / rel).exists():
            (root / rel).write_text('<?xml version="1.0" encoding="utf-8"?>\n'
                                    "<!-- the run wrote no JUnit XML: it did not come to its end -->\n<testsuites/>\n",
                                    encoding="utf-8")
    return _evidence.block(scope, scope["runs"], scope["junit_xml"])


# ---------------------------------------------------------------------------
# Writing records
# ---------------------------------------------------------------------------

def _write_checkpoint(root: Path, ticket: str) -> dict:
    from gov.checkpoint.record import write as checkpoint_write
    return checkpoint_write(root, ticket, "ticket-transition",
                            "ticket closed", [])


def _close_record_rel(ticket: str) -> str:
    return f"docs/close/{ticket}/CL-{ticket}.md"


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_close_record(root: Path, ticket: str, record: dict,
                        commit_files: list[str], checkpoint_path: str) -> str:
    import yaml

    close_id = f"CL-{ticket}"
    close_rel = _close_record_rel(ticket)

    front = {
        "id": close_id,
        "type": "close",
        "status": "ACTIVE",
        "state_class": "AUTHORITATIVE",
        "task": ticket,
        "created": _now(),  # the record's own where it gives one
        "outputs": list(commit_files) + [close_rel, checkpoint_path],
        **record,
    }
    text = ("---\n"
            + yaml.safe_dump(front, sort_keys=False, allow_unicode=True)
            + "---\n\n")
    text += f"# {close_id} — Close record for {ticket}\n"
    _state.write_whole(root / close_rel, text)
    return close_rel
