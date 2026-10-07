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
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from gov.cli.errors import GovError
from gov.close import state as _state
from gov.close.repo import (commits_since as _commits_since, git as _git, names_no_task as _names_no_task,
                            read_commits as _read_commits, store_is_of_head as _store_is_of_head,
                            ticket_commits as _ticket_commits, tree_differences as _tree_differences)
from gov.close.state import (ESCALATION_AT, ESCALATION_OPTIONS as _ESCALATION_OPTIONS,
                             ESCALATION_REASON as _ESCALATION_REASON, count_path as _count_path,
                             read_count as _read_count, write_count as _write_count)

DISPOSITIONS = ("repair", "reuse", "delete", "narrow", "defer", "owner")
DEFAULT_TIMEOUT = 120
NOT_MEASURED = "not measured"
REVIEWER_ROLE = "independent-auditor"
PROBE_ROLE = "orchestrator"
PROBE_PASSED = ("pass", "passed")
_TEST_RUNNER_VARIABLES = ("PYTEST_ADDOPTS", "PYTEST_PLUGINS")

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
                 findings: list[str] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}
        self.findings = findings or [message]


def add_arguments(parser) -> None:
    parser.add_argument("ticket", help="the ticket id to close")
    parser.add_argument("--disposition", default=None,
                        help="finding disposition class")
    parser.add_argument("--owner-decision", default=None,
                        help="owner decision register id")
    parser.add_argument("--timeout", type=int, default=None,
                        help="test timeout in seconds")


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
    timeout = _time_limit(args.timeout, config)

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

    # What is measured is the commit that is recorded, with records of that commit (DEC-487)
    _check_tree(root, ticket)
    _check_store(root)
    if owner_decision:
        state = _state.lift_escalation(root, ticket, owner_decision, state)

    commits = _ticket_commits(root, ticket)
    others = _commits_since(root, commits)
    inside, own = _work_of(front, ticket, wbs)
    ticket_input = {"id": ticket, "hash":
                    "sha256:" + hashlib.sha256(ticket_path.read_bytes()).hexdigest()}

    try:
        if profile == "FULL":
            _check_probe(root, ticket, commits, others, inside)
        _check_trailers(commits, ticket)
        _check_unmeasured(ticket, others, own)
        _check_containment(root, commits)
        # The acceptance tests are part of the ticket's work (DEC-480)
        acceptance_dir = root / "tests" / "acceptance" / wbs
        if not acceptance_dir.is_dir() or not any(acceptance_dir.rglob("test_*.py")):
            raise _Finding("NO_ACCEPTANCE_TESTS",
                           f"no acceptance tests for {ticket} in tests/acceptance/{wbs}/",
                           {"ticket": ticket, "wbs": wbs})
    except _Finding as f:
        _refuse(root, ticket, f.code, f.message, f.findings, f.details)

    # Acceptance tests, then the regression tests (A2): all of tests/ except
    # the ticket's acceptance folder. Both run to their end.
    findings, test_counts = _run_tests(root, acceptance_dir, timeout)
    more, counts = _run_tests(root, root / "tests", timeout,
                              ignore=acceptance_dir, none_collected_ok=True)
    findings += more
    for key in test_counts:
        test_counts[key] += counts[key]

    # Governance checks (A7, DEC-480): where the runner blocks, what it reports
    # as blocking is a finding like a failing test
    # A commit of the range that names no task and changes a governance file has them run too (DEC-490)
    checked, blocking = _check_governance(root, commits + [c for c in others if _names_no_task(c)])
    if blocking is not None:
        at = f"at commit {checked['check_commit'][:12]}"
        findings += [f"governance check {check['id']} is RED {at}: "
                     f"{json.dumps(check.get('findings'), ensure_ascii=False)}"
                     for check in blocking["red_checks"]]
        findings += [f"governance check family {name!r} is RED {at}" for name in blocking["red_families"]]
        if not any(blocking.values()):
            findings.append(f"the governance checks block {at}; the runner names no red check or family")

    if findings:
        details = {"findings": findings, "disposition": disposition or "unclassed"}
        if blocking is not None:
            details.update(check_commit=checked["check_commit"], **blocking)
        packet, context_reason = None, None
        if disposition:  # DEC-454: with a class, the context is built first
            try:
                packet = _build_context(root, ticket)
            except _Finding as f:
                context_reason = details["context"] = f.message
        else:
            details["note"] = "findings await their class; use --disposition to classify"
        _refuse(root, ticket, "CHECK_FAILED",
                "tests or checks failed" if disposition else
                "tests or checks failed; findings are unclassed and await disposition",
                findings, details, disposition=disposition,
                context_hash=packet["hash"] if packet else None,
                context_reason=context_reason)

    # Watchdog (B1)
    from gov.checkpoint.command import MAX_AGE_MINUTES, MAX_COMMITS, MAX_CONTEXT
    from gov.checkpoint.record import watch as checkpoint_watch
    try:
        checkpoint_watch(root, ticket, max_age_minutes=MAX_AGE_MINUTES,
                         max_commits=MAX_COMMITS,
                         max_context=MAX_CONTEXT, context_utilisation=None)
    except GovError as e:
        _refuse(root, ticket, e.code, e.message, [e.message], e.details,
                exit_code=e.exit_code)

    # Context (DEC-454, DEC-470)
    try:
        packet = _build_context(root, ticket)
    except _Finding as f:
        _refuse(root, ticket, f.code, f.message, f.findings, f.details)

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
        "deviations": NOT_MEASURED,
        "skill_versions": _read_skill_versions(root),
        "commits": _commit_models(commits),
    }
    record.update(checked)

    close_record_path, checkpoint_path = _record_and_close(root, ticket, record, commit_files)

    # Reset iteration count on success (A6)
    if state["count"] or state.get("decision"):
        reset = {"count": 0, "last_failures": [], "outcomes": []}
        reset.update({key: state[key] for key in ("decision", "decisions") if state.get(key)})
        _write_count(root, ticket, reset)

    return {"ticket": ticket, "close_record": close_record_path,
            "checkpoint": checkpoint_path}


def _time_limit(given, config: dict):
    """The time limit of a test run in seconds: the argument's, else the project's, else the default.
    ``INVALID_TIMEOUT`` when it is not a positive number: nothing has run (DEC-487)."""
    import math

    named = "--timeout" if given is not None else "close_timeout"
    limit = given if given is not None else config.get("close_timeout", DEFAULT_TIMEOUT)
    if isinstance(limit, bool) or not isinstance(limit, (int, float)) or not math.isfinite(limit) or limit <= 0:
        raise GovError("INVALID_TIMEOUT",
                        f"the time limit ({named}) must be a positive number of seconds, got {limit!r}",
                        {"argument": named, "timeout": str(limit)})
    return limit


# ---------------------------------------------------------------------------
# Before anything is measured (DEC-487, DEC-490): "could not measure" is not a finding
# ---------------------------------------------------------------------------

def _check_tree(root: Path, ticket: str) -> None:
    """``TREE_NOT_COMMITTED`` when the working tree is not ``HEAD``, with the paths.

    The one path that refuses nothing is what a refused close of this ticket left: an untracked ticket
    file whose parent is the ticket (its repair ticket, DEC-490).
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
        _tk(root, "close", ticket)
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

def _check_trailers(commits: list[dict], ticket: str) -> None:
    if not commits:
        raise _Finding("TRAILER_MISSING",
                       f"no commits found with Task: {ticket} trailer",
                       {"ticket": ticket})
    for c in commits:
        for key in ("Implements", "Role"):  # a commit of the ticket is somebody's (DEC-487)
            if not c["trailers"].get(key):
                raise _Finding("TRAILER_MISSING",
                               f"commit {c['sha'][:12]} lacks {key}: trailer",
                               {"commit": c["sha"][:12], "ticket": ticket})


def _check_unmeasured(ticket: str, others: list[dict], own) -> None:
    """A commit in the ticket's range that names no task and changes the ticket's work (its acceptance
    tests, a path inside its allowed paths, its own file) refuses: no ticket measured it. What a commit
    that names another ticket changes is that ticket's, and any other path refuses nothing (DEC-490)."""
    for c in others:
        changed = [p for p in c["paths"] if own(p)] if _names_no_task(c) else []
        if changed:
            raise _Finding("WORK_WITHOUT_TASK",
                           f"commit {c['sha'][:12]} names no task and changes {', '.join(changed)}: "
                           f"work on {ticket} that no ticket measured",
                           {"commit": c["sha"][:12], "ticket": ticket, "paths": changed})


def _check_containment(root: Path, commits: list[dict]) -> None:
    """W1-50's judgement of the ticket's commits (DEC-453): every finding
    refuses, as returned. This command has no rule of its own."""
    from gov.guard.containment import ContainmentError, judge_commits

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

def _check_probe(root: Path, ticket: str, commits: list[dict], others: list[dict], inside) -> None:
    """The probe record of a FULL-profile ticket is evidence only if the implementer could not have written
    it (DEC-137, DEC-487). ``others`` are the other commits of the ticket's range, ``inside`` says whether a
    path is inside the ticket's allowed paths."""
    from gov.tasks.tickets import frontmatter

    def invalid(message: str, **details):
        return _Finding("PROBE_INVALID", message, {"ticket": ticket, **details})

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

    for path in sorted(probe_dir.glob("*.md")):
        pf = frontmatter(path)
        if pf is None:
            raise invalid(f"probe file {path.name} has no readable YAML frontmatter",
                          file=path.name)
        if pf.get("type") != "probe" or pf.get("task") != ticket:
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
        if judgement not in PROBE_PASSED:
            raise invalid(f"the probe's judgement is {judgement!r}, not {' or '.join(PROBE_PASSED)}",
                          judgement=judgement)
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
        for sha, c in after.items():
            if REVIEWER_ROLE in c["trailers"].get("Role", []):
                raise invalid("a commit between the probed commit and HEAD "
                              "carries the reviewer's role", commit=sha[:12])
            changed = [p for p in c["paths"] if inside(p)] if _names_no_task(c) else []
            if changed:  # DEC-490: work on the ticket's paths the probe did not see
                raise invalid(f"commit {sha[:12]} names no task and changes {', '.join(changed)} "
                              "after the probed commit: the probe is stale", commit=sha[:12])
        for c in commits:
            sha = c["sha"][:12]
            if any(str(reviewer) in value
                   for values in c["trailers"].values() for value in values):
                raise invalid(f"commit {sha} trailer names the reviewer session",
                              commit=sha)
            if c["sha"] in after:
                for p in c["paths"]:
                    if not p.startswith(("tests/", "docs/probes/")):
                        raise invalid(f"ticket commit {sha} changes {p} "
                                      "after the probed commit", commit=sha, path=p)
        return

    raise _Finding("PROBE_MISSING",
                   f"FULL-profile ticket {ticket} has no valid probe record",
                   {"ticket": ticket})


# ---------------------------------------------------------------------------
# Test runner (A2)
# ---------------------------------------------------------------------------

def _run_tests(root: Path, test_path: Path, timeout: int,
               ignore: Path | None = None,
               none_collected_ok: bool = False) -> tuple[list[str], dict]:
    """Run pytest on ``test_path`` to its end: its findings and its counts.

    A run over the time limit is a finding like a failing test (DEC-454).
    ``TEST_RUNNER_ABSENT`` when this interpreter has no pytest: nothing ran.
    """
    import importlib.util
    import os
    import re

    counts = {"passed": 0, "failed": 0, "errors": 0}
    if not test_path.is_dir():
        if none_collected_ok:
            return [], counts
        raise GovError("TESTS_MISSING", f"{test_path} is not a folder",
                        {"test_path": str(test_path)})
    if importlib.util.find_spec("pytest") is None:
        raise GovError("TEST_RUNNER_ABSENT",
                        f"pytest is not installed for {sys.executable}: no test was run",
                        {"python": sys.executable})

    rel = str(test_path.relative_to(root))
    # The run is the suite's own (DEC-487): what the caller's environment would add to the test runner
    # (options, plugins) is not passed on.
    env = {key: value for key, value in os.environ.items() if key not in _TEST_RUNNER_VARIABLES}
    env["PYTHONPATH"] = os.pathsep.join(
        [str(root / "src")] + [p for p in env.get("PYTHONPATH", "").split(os.pathsep) if p])
    cmd = [sys.executable, "-m", "pytest", str(test_path), "-q",
           "-p", "no:cacheprovider", "--tb=line", "--no-header"]
    if ignore is not None:
        cmd += ["--ignore", str(ignore)]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                cwd=str(root), env=env, timeout=timeout)
    except subprocess.TimeoutExpired:
        return [f"the test run of {rel} exceeded the time limit of {timeout}s"], counts

    for line in reversed(result.stdout.split("\n")):
        found = {key: re.search(rf"(\d+)\s+{word}", line) for key, word in
                 (("passed", "passed"), ("failed", "failed"), ("errors", "error"))}
        if any(found.values()):
            counts.update({key: int(m.group(1)) for key, m in found.items() if m})
            break

    rc = result.returncode
    if rc == 0 and not none_collected_ok and not counts["passed"]:
        return [f"no test passed in {rel}: nothing of it was measured"], counts
    if rc == 0 or (rc == 5 and none_collected_ok):
        return [], counts
    if rc == 5:
        return [f"no test was collected in {rel}"], counts
    if rc == 2:
        failures = [line.strip() for line in
                    (result.stdout + "\n" + result.stderr).split("\n")
                    if "ERROR" in line or "SyntaxError" in line]
        counts["errors"] = counts["errors"] or len(failures)
        return failures or [f"collection error in {rel}"], counts
    failures = [line.strip() for line in result.stdout.split("\n") if "FAILED" in line]
    return failures or [f"the test run of {rel} exited {rc}: "
                        f"{result.stderr.strip()[-200:]}"], counts


# ---------------------------------------------------------------------------
# Governance checks (A7)
# ---------------------------------------------------------------------------

def _check_governance(root: Path, commits: list[dict]) -> tuple[dict, dict | None]:
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
    the commit being closed.
    """
    if not any(p.startswith(_GOVERNANCE_PREFIXES) for c in commits for p in c["paths"]):
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


# ---------------------------------------------------------------------------
# The one path of a refusal for a finding about the ticket's work (DEC-455)
# ---------------------------------------------------------------------------

def _refuse(root: Path, ticket: str, code: str, message: str,
            findings: list[str], details: dict | None = None, *,
            exit_code: int = EXIT_CHECK_FAILED,
            disposition: str | None = None, context_hash: str | None = None,
            context_reason: str | None = None):
    """Count the refusal, open its repair ticket, write the escalation at the
    third, and raise the refusal. The next attempt after the third is blocked
    in ``run`` before anything runs."""
    from datetime import datetime, timezone

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
        root, ticket, findings, disposition, context_hash, context_reason)
    raise GovError(code, message, details, exit_code=exit_code)


# ---------------------------------------------------------------------------
# The ticket tool (B2, B3)
# ---------------------------------------------------------------------------

def _tk(root: Path, *args: str) -> str:
    """The output of the project's ticket tool; ``TICKET_TOOL_ABSENT`` or ``TICKET_TOOL_FAILED``."""
    import os
    from gov.tasks.tickets import TICKETS_REL, TK_REL

    tk_path = root / TK_REL
    if not tk_path.is_file():
        raise GovError("TICKET_TOOL_ABSENT",
                        f"the ticket tool (tk) is not available at {TK_REL}",
                        {"command": args[0]})
    try:
        done = subprocess.run(
            [str(tk_path), *args], capture_output=True, text=True, cwd=str(root),
            env={**os.environ, "TICKETS_DIR": str(root / TICKETS_REL)})
    except OSError as e:
        raise GovError("TICKET_TOOL_FAILED", f"tk {args[0]} cannot run: {e}",
                        {"command": args[0]})
    if done.returncode != 0:
        raise GovError("TICKET_TOOL_FAILED",
                        f"tk {args[0]} failed with exit code {done.returncode}: "
                        f"{done.stderr.strip()[:200]}",
                        {"command": args[0]})
    return done.stdout


def _open_repair_ticket(root: Path, ticket: str, findings: list[str],
                        disposition: str | None = None,
                        context_hash: str | None = None,
                        context_reason: str | None = None) -> str:
    """Open the repair ticket of a refused close through the ticket tool: its
    parent and its findings with ``tk create``, its dependency on ``ticket``
    with ``tk dep``. Returns what the answer says of it: its id, or that none
    was opened and why. No ticket file is written by any other means.
    """
    from gov.tasks.tickets import TICKETS_REL

    description = [f"Findings of the refused close of {ticket} "
                   f"(disposition: {disposition or 'unclassed'}):"]
    description += [f"- {finding}" for finding in findings]
    if context_reason:
        description.append(f"The class was given without whole-system context: {context_reason}")
    try:
        created = _tk(root, "create", f"Repair {ticket}: {findings[0][:60]}",
                      "--parent", ticket, "-d", "\n".join(description))
    except GovError as e:
        return f"not opened: {e.message}"
    repair_id = created.strip().split("\n")[-1]
    path = root / TICKETS_REL / f"{repair_id}.md"

    # What tk has no option for, as lines of the frontmatter tk wrote (as
    # gov.tasks.tickets.create adds state_class): the class and the context hash.
    fields = ["state_class: AUTHORITATIVE", f"disposition: {disposition or 'unclassed'}"]
    if context_hash:
        fields.append(f"context_hash: {context_hash}")
    try:
        lines = path.read_text(encoding="utf-8").split("\n")
        end = lines.index("---", 1)
        _state.write_whole(path, "\n".join(lines[:end] + fields + lines[end:]))
    except (OSError, ValueError) as e:
        return f"{repair_id} opened by tk; its class could not be recorded: {e}"
    try:
        _tk(root, "dep", repair_id, ticket)
    except GovError as e:
        return f"{repair_id} opened; its dependency on {ticket} was not recorded: {e.message}"
    return repair_id


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


def _read_skill_versions(root: Path) -> list[dict]:
    """The kernel's skills with the version each ``SKILL.md`` states, and the
    vendored ones, which carry none. A skill file whose frontmatter cannot be
    read is listed under its folder's name with "not measured"."""
    from gov.tasks.tickets import frontmatter

    kernel = root / "template" / "governance" / "kernel"
    versions = []
    for files, versioned in ((sorted((kernel / "skills").glob("*/SKILL.md")), True),
                             (sorted((kernel / "vendor").rglob("SKILL.md")), False)):
        for skill_file in files:
            front = frontmatter(skill_file)
            if front is None:
                versions.append({"name": skill_file.parent.name, "version": NOT_MEASURED})
                continue
            version = front.get("version") if versioned else None
            versions.append({"name": str(front.get("name", skill_file.parent.name)),
                             "version": str(version) if version else "no version"})
    return versions


# ---------------------------------------------------------------------------
# Writing records
# ---------------------------------------------------------------------------

def _write_checkpoint(root: Path, ticket: str) -> dict:
    from gov.checkpoint.record import write as checkpoint_write
    return checkpoint_write(root, ticket, "ticket-transition",
                            "ticket closed", [])


def _close_record_rel(ticket: str) -> str:
    return f"docs/close/{ticket}/CL-{ticket}.md"


def _write_close_record(root: Path, ticket: str, record: dict,
                        commit_files: list[str], checkpoint_path: str) -> str:
    import yaml
    from datetime import datetime, timezone

    close_id = f"CL-{ticket}"
    close_rel = _close_record_rel(ticket)

    front = {
        "id": close_id,
        "type": "close",
        "status": "ACTIVE",
        "state_class": "AUTHORITATIVE",
        "task": ticket,
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "outputs": list(commit_files) + [close_rel, checkpoint_path],
        **record,
    }
    text = ("---\n"
            + yaml.safe_dump(front, sort_keys=False, allow_unicode=True)
            + "---\n\n")
    text += f"# {close_id} — Close record for {ticket}\n"
    _state.write_whole(root / close_rel, text)
    return close_rel
