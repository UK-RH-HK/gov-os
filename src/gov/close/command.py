"""``gov close`` command module (W1-30, DEC-317).

Closes a ticket after verifying acceptance tests, trailers, containment,
and (for FULL-profile tickets) the probe record. Tracks iteration counts
and opens repair tickets on failure.

Nothing is closed, and nothing is recorded, that was not measured (DEC-454,
DEC-470): an error of something this command calls refuses the close with
that thing's reason.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from gov.cli.errors import GovError

DISPOSITIONS = ("repair", "reuse", "delete", "narrow", "defer", "owner")
DEFAULT_TIMEOUT = 120
NOT_MEASURED = "not measured"
REVIEWER_ROLE = "independent-auditor"
ESCALATION_AT = 3

ACT_PATHS = (
    "docs/close/**",
    "docs/checkpoints/**",
    ".tickets/**",
    ".gov-runtime/iterations/**",
)
EXIT_CHECK_FAILED = 3
EXIT_BLOCKED = 4
EXIT_CODES = {
    EXIT_CHECK_FAILED: "verification failed (tests, stale evidence, containment)",
    EXIT_BLOCKED: "blocked by escalation or human gate",
}

_GOVERNANCE_PREFIXES = (
    "template/governance/kernel/checks/",
    "template/governance/kernel/schemas/",
    "governance/project/",
    "template/governance/kernel/hooks/",
    "template/governance/kernel/skills/",
    "template/governance/kernel/policies/",
    "template/governance/kernel/roles/",
)

_ESCALATION_OPTIONS = [
    "fix_differently", "narrow", "split", "defer", "delete", "continue",
]
_ESCALATION_REASON = "three consecutive non-converging iterations"


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
    timeout = args.timeout or config.get("close_timeout", DEFAULT_TIMEOUT)
    disposition = getattr(args, "disposition", None)
    owner_decision = getattr(args, "owner_decision", None)

    if disposition and disposition not in DISPOSITIONS:
        raise GovError("INVALID_DISPOSITION",
                        f"disposition must be one of {', '.join(DISPOSITIONS)}",
                        {"disposition": disposition, "valid": list(DISPOSITIONS)})

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
    if owner_decision:
        if state["count"] < ESCALATION_AT:
            raise GovError("INVALID_DECISION",
                            "owner decision given but no escalation in force",
                            {"ticket": ticket})
        _validate_owner_decision(root, owner_decision)
        _write_count(root, ticket, {"count": 0, "last_failures": [],
                                    "outcomes": [], "decision": owner_decision})
    elif state["count"] >= ESCALATION_AT:
        raise GovError("ESCALATION_BLOCKED",
                        "three consecutive non-converging iterations reached",
                        {"outcomes": state["outcomes"][-1:],
                         "reason": _ESCALATION_REASON,
                         "options": _ESCALATION_OPTIONS},
                        exit_code=EXIT_BLOCKED)

    commits = _ticket_commits(root, ticket)
    ticket_input = {"id": ticket, "hash":
                    "sha256:" + hashlib.sha256(ticket_path.read_bytes()).hexdigest()}

    try:
        if profile == "FULL":
            _check_probe(root, ticket, commits)
        _check_trailers(commits, ticket)
        _check_containment(root, commits)
    except _Finding as f:
        _refuse(root, ticket, f.code, f.message, f.findings, f.details)

    acceptance_dir = root / "tests" / "acceptance" / wbs
    if not acceptance_dir.is_dir() or not list(acceptance_dir.glob("test_*.py")):
        raise GovError("NO_ACCEPTANCE_TESTS",
                        f"no acceptance tests for {ticket} in tests/acceptance/{wbs}/",
                        {"ticket": ticket, "wbs": wbs},
                        exit_code=EXIT_CHECK_FAILED)

    # Acceptance tests, then the regression tests (A2): all of tests/ except
    # the ticket's acceptance folder. Both run to their end.
    findings, test_counts = _run_tests(root, acceptance_dir, timeout)
    more, counts = _run_tests(root, root / "tests", timeout,
                              ignore=acceptance_dir, none_collected_ok=True)
    findings += more
    for key in test_counts:
        test_counts[key] += counts[key]

    # Governance checks (A7)
    gov_check_result = None
    try:
        gov_check_result = _check_governance(root, commits)
    except GovError as e:
        if e.exit_code != EXIT_CHECK_FAILED:
            raise
        findings.append(e.message)

    if findings:
        details = {"findings": findings, "disposition": disposition or "unclassed"}
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
    if gov_check_result is not None:
        record["governance_checks"] = gov_check_result
        record["check_commit"] = _git(root, "rev-parse", "HEAD").strip()

    checkpoint_info = _write_checkpoint(root, ticket)
    try:
        close_record_path = _write_close_record(
            root, ticket, record, commit_files, checkpoint_info["path"])
    except OSError as e:
        raise GovError("CLOSE_RECORD_FAILED",
                        f"cannot write close record: {e}",
                        {"ticket": ticket})

    _tk(root, "close", ticket)

    # Reset iteration count on success (A6)
    if state["count"] or state.get("decision"):
        reset = {"count": 0, "last_failures": [], "outcomes": []}
        if state.get("decision"):
            reset["decision"] = state["decision"]
        _write_count(root, ticket, reset)

    return {"ticket": ticket, "close_record": close_record_path,
            "checkpoint": checkpoint_info["path"]}


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

def _git(root: Path, *args: str, ok: tuple = (0,), code: bool = False):
    """The output of a git command, or its exit code with ``code``; ``GIT_FAILURE`` outside ``ok``."""
    try:
        done = subprocess.run(["git", "-C", str(root), *args],
                              capture_output=True, text=True)
    except OSError as e:
        raise GovError("GIT_FAILURE", f"git {args[0]} cannot run: {e}",
                        {"root": str(root)})
    if done.returncode not in ok:
        raise GovError("GIT_FAILURE",
                        f"git {args[0]} failed: {done.stderr.strip()[:200]}",
                        {"root": str(root), "arguments": list(args)})
    return done.returncode if code else done.stdout


def _ticket_commits(root: Path, ticket: str) -> list[dict]:
    """The commits of HEAD's history whose trailers hold ``Task: <ticket>``, newest first."""
    commits = []
    for sha in _git(root, "log", "HEAD", "--format=%H",
                    f"--grep=Task: {ticket}").split():
        trailers = _read_trailers(root, sha)
        if any(v == ticket for v in trailers.get("Task", [])):
            commits.append({"sha": sha, "trailers": trailers,
                            "paths": _commit_paths(root, sha)})
    return commits


def _read_trailers(root: Path, sha: str) -> dict[str, list[str]]:
    trailers: dict[str, list[str]] = {}
    for line in _git(root, "log", "-1", "--format=%(trailers:only,unfold)",
                     sha).split("\n"):
        key, _, value = line.partition(":")
        if key.strip() and value.strip():
            trailers.setdefault(key.strip(), []).append(value.strip())
    return trailers


def _commit_paths(root: Path, sha: str) -> list[str]:
    out = _git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", sha)
    return [p.strip() for p in out.split("\n") if p.strip()]


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
        if not c["trailers"].get("Implements"):
            raise _Finding("TRAILER_MISSING",
                           f"commit {c['sha'][:12]} lacks Implements: trailer",
                           {"commit": c["sha"][:12], "ticket": ticket})


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

def _check_probe(root: Path, ticket: str, commits: list[dict]) -> None:
    from gov.tasks.tickets import frontmatter

    def invalid(message: str, **details):
        return _Finding("PROBE_INVALID", message, {"ticket": ticket, **details})

    probe_dir = root / "docs" / "probes" / ticket
    if not probe_dir.is_dir():
        raise _Finding("PROBE_MISSING",
                       f"FULL-profile ticket {ticket} has no probe record",
                       {"ticket": ticket})

    # DEC-137: the reviewer wrote nothing. A commit of the ticket with the
    # reviewer's role refuses wherever it lies, whatever else it names.
    for c in commits:
        if REVIEWER_ROLE in c["trailers"].get("Role", []):
            raise invalid(f"commit {c['sha'][:12]} of the ticket carries the "
                          f"reviewer's role ({REVIEWER_ROLE})", commit=c["sha"][:12])

    for path in sorted(probe_dir.glob("*.md")):
        pf = frontmatter(path)
        if pf is None:
            raise invalid(f"probe file {path.name} has no readable YAML frontmatter",
                          file=path.name)
        if pf.get("type") != "probe" or pf.get("task") != ticket:
            continue

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
        if not str(pf.get("judgement", "")).strip():
            raise invalid("probe has no judgement")
        if not pf.get("probed_commit"):
            raise invalid("probe record does not name the probed commit")
        probed = str(pf["probed_commit"])

        # Exit code 1 is git's answer "no" to both questions; any other failure is an error.
        if _git(root, "rev-parse", "--verify", "--quiet", probed + "^{commit}",
                ok=(0, 1), code=True) or _git(
                root, "merge-base", "--is-ancestor", probed, "HEAD",
                ok=(0, 1), code=True):
            raise invalid("probed commit is not an ancestor of HEAD",
                          probed_commit=probed)

        after = _git(root, "log", f"{probed}..HEAD", "--format=%H").split()
        for sha in after:
            if REVIEWER_ROLE in _read_trailers(root, sha).get("Role", []):
                raise invalid("a commit between the probed commit and HEAD "
                              "carries the reviewer's role", commit=sha[:12])
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
    env = dict(os.environ)
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

def _check_governance(root: Path, commits: list[dict]) -> dict | None:
    changed_gov_paths = []
    for c in commits:
        for p in c["paths"]:
            if any(p.startswith(prefix) for prefix in _GOVERNANCE_PREFIXES):
                changed_gov_paths.append(p)

    if not changed_gov_paths:
        return None

    checks_prefix = "template/governance/kernel/checks/"
    check_commit_map: dict[str, list[str]] = {}
    for c in commits:
        for p in c["paths"]:
            if p.startswith(checks_prefix) and p.endswith(".yaml"):
                cid = p[len(checks_prefix):-len(".yaml")]
                check_commit_map.setdefault(cid, []).append(c["sha"])

    stale = sorted(cid for cid, shas in check_commit_map.items()
                   if len(shas) > 1)
    if stale:
        raise GovError("STALE_EVIDENCE",
                        f"governance evidence is stale: "
                        f"{', '.join(stale)} changed after evidence was collected",
                        {"stale_checks": stale},
                        exit_code=EXIT_CHECK_FAILED)

    changed_check_ids = set(check_commit_map.keys())

    from gov.check.runner import run_checks
    result, _has_hard_block = run_checks(root)

    if changed_check_ids:
        failing = []
        for check in result.get("checks", []):
            cid = check.get("id", "")
            if (cid in changed_check_ids
                    and check.get("severity") == "hard-block"
                    and check.get("status") == "RED"):
                failing.append(cid)

        if failing:
            raise GovError("CHECK_FAILED",
                            f"governance checks failed: {', '.join(failing)}",
                            {"failing_checks": failing, "result": result},
                            exit_code=EXIT_CHECK_FAILED)

    return result


# ---------------------------------------------------------------------------
# The count of a ticket's consecutive refused closes (A6)
# ---------------------------------------------------------------------------

def _count_path(root: Path, ticket: str) -> Path:
    return root / ".gov-runtime" / "iterations" / f"{ticket}.json"


def _read_count(root: Path, ticket: str) -> dict:
    """The ticket's count file; a count of zero without a file.
    ``ITERATION_CORRUPT`` when it cannot be read or has another shape."""
    path = _count_path(root, ticket)
    if not path.is_file():
        return {"count": 0, "last_failures": [], "outcomes": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        raise GovError("ITERATION_CORRUPT",
                        f"iteration count file cannot be read or parsed: {e}",
                        {"ticket": ticket})
    if not isinstance(data, dict) or type(data.setdefault("count", 0)) is not int \
            or not isinstance(data.setdefault("outcomes", []), list):
        raise GovError("ITERATION_CORRUPT",
                        "iteration count file has wrong shape",
                        {"ticket": ticket})
    return data


def _write_count(root: Path, ticket: str, data: dict) -> None:
    path = _count_path(root, ticket)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
    except OSError as e:
        raise GovError("ITERATION_UNWRITABLE",
                        f"iteration count file cannot be written: {e}",
                        {"ticket": ticket})


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
    outcomes = state["outcomes"] + [{
        "failures": sorted(set(findings)),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }]
    counted = {"count": state["count"] + 1,
               "last_failures": sorted(set(findings)), "outcomes": outcomes}
    if state.get("decision"):
        counted["decision"] = state["decision"]
    _write_count(root, ticket, counted)

    if counted["count"] >= ESCALATION_AT:
        esc_file = root / ".gov-runtime" / "escalations" / f"{ticket}.json"
        try:
            esc_file.parent.mkdir(parents=True, exist_ok=True)
            esc_file.write_text(json.dumps({
                "ticket": ticket, "outcomes": outcomes,
                "reason": _ESCALATION_REASON, "options": _ESCALATION_OPTIONS,
            }), encoding="utf-8")
        except OSError as e:
            raise GovError("ESCALATION_UNWRITABLE",
                            f"the escalation package cannot be written: {e}",
                            {"ticket": ticket, "findings": findings})

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
        path.write_text("\n".join(lines[:end] + fields + lines[end:]), encoding="utf-8")
    except (OSError, ValueError) as e:
        return f"{repair_id} opened by tk; its class could not be recorded: {e}"
    try:
        _tk(root, "dep", repair_id, ticket)
    except GovError as e:
        return f"{repair_id} opened; its dependency on {ticket} was not recorded: {e.message}"
    return repair_id


# ---------------------------------------------------------------------------
# Owner decision validation (A6)
# ---------------------------------------------------------------------------

def _validate_owner_decision(root: Path, dec_id: str) -> None:
    from gov.decisions import check as check_decisions
    from gov.tasks.tickets import frontmatter

    def invalid(why: str):
        return GovError("INVALID_DECISION", f"decision {dec_id} {why}",
                         {"decision": dec_id})

    candidates = [root / "docs" / "adr" / f"{dec_id}.md",
                  root / "governance" / "decisions" / f"{dec_id}.md",
                  *sorted((root / "docs").rglob(f"{dec_id}.md"))]
    found = next((path for path in candidates if path.is_file()), None)
    if found is None:
        raise invalid("not found")
    df = frontmatter(found)
    if df is None:
        raise invalid("has no readable frontmatter")
    status = str(df.get("status", "")).upper()
    if status != "ACTIVE":
        raise invalid(f"is not ACTIVE (status: {status})")
    for f in check_decisions(root):
        if f.get("code") == "ACTIVE_UNAPPROVED" and dec_id in f.get("ids", []):
            raise invalid("is ACTIVE but unapproved")


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


def _write_close_record(root: Path, ticket: str, record: dict,
                        commit_files: list[str], checkpoint_path: str) -> str:
    import yaml
    from datetime import datetime, timezone

    close_id = f"CL-{ticket}"
    close_rel = f"docs/close/{ticket}/{close_id}.md"
    close_path = root / close_rel
    close_path.parent.mkdir(parents=True, exist_ok=True)

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
    close_path.write_text(text, encoding="utf-8")
    return close_rel
