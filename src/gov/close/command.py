"""``gov close`` command module (W1-30, DEC-317).

Closes a ticket after verifying acceptance tests, trailers, containment,
and (for FULL-profile tickets) the probe record. Tracks iteration counts
and opens repair tickets on failure.
"""

from __future__ import annotations

from pathlib import Path

DISPOSITIONS = ("repair", "reuse", "delete", "narrow", "defer", "owner")
DEFAULT_TIMEOUT = 120

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

_INFRA_PREFIXES = (
    ".tickets/", ".gitignore", ".gov-runtime/", "tests/", "docs/",
    "governance/", "template/", "openspec/",
)

_GOVERNANCE_PREFIXES = (
    "template/governance/kernel/checks/",
    "template/governance/kernel/schemas/",
    "governance/project/",
    "template/governance/kernel/hooks/",
    "template/governance/kernel/skills/",
)

_ESCALATION_OPTIONS = [
    "fix_differently", "narrow", "split", "defer", "delete", "continue",
]


def add_arguments(parser) -> None:
    parser.add_argument("ticket", help="the ticket id to close")
    parser.add_argument("--disposition", default=None,
                        help="finding disposition class")
    parser.add_argument("--owner-decision", default=None,
                        help="owner decision register id")
    parser.add_argument("--timeout", type=int, default=None,
                        help="test timeout in seconds")


def run(root: Path, args, config: dict):
    import json

    from gov.cli.errors import GovError
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

    ticket_status = str(front.get("status", ""))
    if ticket_status == "closed":
        raise GovError("STALE_EVIDENCE",
                        f"ticket {ticket} is already closed",
                        {"ticket": ticket},
                        exit_code=EXIT_CHECK_FAILED)

    profile = str(front.get("profile", "STANDARD")).upper()
    wbs = front.get("wbs_id") or front.get("external-ref") or ticket
    allowed_paths = front.get("allowed_paths", [])

    # Owner decision or escalation check (A6)
    iter_file = root / ".gov-runtime" / "iterations" / f"{ticket}.json"
    if owner_decision:
        _validate_owner_decision(root, owner_decision)
        if iter_file.is_file():
            iter_file.write_text(json.dumps(
                {"count": 0, "last_failures": [], "outcomes": []}
            ), encoding="utf-8")
    elif iter_file.is_file():
        try:
            iter_data = json.loads(iter_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            raise GovError("ITERATION_CORRUPT",
                            "iteration count file cannot be read or parsed",
                            {"ticket": ticket})
        if iter_data.get("count", 0) >= 3:
            safe_outcomes = [
                {k: v for k, v in o.items() if k != "iteration"}
                for o in (iter_data.get("outcomes") or [])[-1:]
            ]
            raise GovError("ESCALATION_BLOCKED",
                            "three consecutive non-converging iterations reached",
                            {"outcomes": safe_outcomes,
                             "reason": "three consecutive non-converging iterations",
                             "options": _ESCALATION_OPTIONS},
                            exit_code=EXIT_BLOCKED)

    if profile == "FULL":
        _check_probe(root, ticket)

    commits = _ticket_commits(root, ticket)
    _check_trailers(commits, ticket)
    _check_commit_containment(commits, allowed_paths)

    acceptance_dir = root / "tests" / "acceptance" / wbs
    if not acceptance_dir.is_dir() or not list(acceptance_dir.glob("test_*.py")):
        raise GovError("NO_ACCEPTANCE_TESTS",
                        f"no acceptance tests for {ticket} in tests/acceptance/{wbs}/",
                        {"ticket": ticket, "wbs": wbs},
                        exit_code=EXIT_CHECK_FAILED)

    # Run acceptance tests
    test_failures = []
    total_counts = {"passed": 0, "failed": 0, "errors": 0}

    rc, failures, counts = _run_tests(root, str(acceptance_dir), timeout)
    if rc != 0:
        test_failures.extend(failures or ["acceptance tests failed"])
    _merge_counts(total_counts, counts)

    # Run regression tests (A2): all tests/ except the ticket's acceptance folder
    tests_dir = root / "tests"
    if tests_dir.is_dir():
        rc, failures, counts = _run_tests(
            root, str(tests_dir), timeout,
            ignore_dirs=[str(acceptance_dir)])
        if rc != 0 and rc != 5:
            test_failures.extend(failures or ["regression tests failed"])
        _merge_counts(total_counts, counts)

    # Governance checks (A7)
    gov_check_result = _check_governance(root, commits)

    all_findings = list(test_failures)

    if all_findings:
        context_hash = None
        if disposition:
            try:
                from gov.context import context as build_context
                ctx = build_context(root, ticket)
                context_hash = ctx.get("hash", "")
            except Exception:
                import hashlib
                context_hash = hashlib.sha256(
                    ticket_path.read_bytes()).hexdigest()
        _handle_failure(root, ticket, all_findings, front,
                        disposition=disposition, context_hash=context_hash)
        details = {"findings": all_findings}
        if not disposition:
            details["disposition"] = "unclassed"
            details["note"] = "findings await their class; use --disposition to classify"
        else:
            details["disposition"] = disposition
        raise GovError(
            "CHECK_FAILED",
            "tests or checks failed; findings are unclassed and await disposition"
            if not disposition else "tests or checks failed",
            details,
            exit_code=EXIT_CHECK_FAILED)

    # Watchdog (B1): any GovError refuses, use W1-25 thresholds
    from gov.checkpoint.command import MAX_AGE_MINUTES, MAX_COMMITS, MAX_CONTEXT
    from gov.checkpoint.record import watch as checkpoint_watch
    try:
        checkpoint_watch(root, ticket, max_age_minutes=MAX_AGE_MINUTES,
                         max_commits=MAX_COMMITS,
                         max_context=MAX_CONTEXT, context_utilisation=None)
    except GovError:
        raise

    # Context: try to get packet hash and decisions from gov context
    try:
        from gov.context import context as build_context
        ctx = build_context(root, ticket)
        packet_hash = ctx.get("hash", "")
        decisions = [item.get("id", "") for item in ctx.get("mandatory", [])
                     if item.get("authority") == "decision"]
    except Exception:
        import hashlib
        packet_hash = hashlib.sha256(ticket_path.read_bytes()).hexdigest()
        decisions = []

    # A4: refuse on decision-register contradictions
    try:
        from gov.decisions import check as check_decisions
        dec_findings = check_decisions(root)
        cycles = [f for f in dec_findings
                  if f.get("code") in ("SUPERSESSION_CYCLE",)]
        if cycles:
            raise GovError("CONTEXT_FAILED",
                            "gov context cannot be built: decision register "
                            "has contradictions",
                            {"ticket": ticket,
                             "findings": [f.get("code") for f in cycles]})
    except GovError:
        raise
    except Exception:
        pass

    requirements = _collect_requirements(commits)
    test_paths = _collect_test_paths(root, wbs)
    skill_versions = _read_skill_versions(root)
    commit_files = _collect_commit_files(commits)
    head_commit = _head(root)

    _set_ticket_closed(root, ticket)
    inputs = _build_inputs(root, ticket, front)

    checkpoint_info = _write_checkpoint(root, ticket)
    close_record_path = _write_close_record(
        root, ticket, packet_hash, inputs, requirements,
        decisions, test_paths, skill_versions, checkpoint_info,
        total_counts, gov_check_result, head_commit, commit_files,
    )

    # Reset iteration count on success (A6)
    if iter_file.is_file():
        iter_file.write_text(json.dumps(
            {"count": 0, "last_failures": [], "outcomes": []}
        ), encoding="utf-8")

    return {"ticket": ticket, "close_record": close_record_path,
            "checkpoint": checkpoint_info.get("path", "")}


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def _head(root: Path) -> str:
    import subprocess
    from gov.cli.errors import GovError
    try:
        return subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, OSError) as e:
        raise GovError("GIT_FAILURE", f"cannot determine HEAD: {e}",
                        {"root": str(root)})


def _ticket_commits(root: Path, ticket: str) -> list[dict]:
    import subprocess
    from gov.cli.errors import GovError

    result = subprocess.run(
        ["git", "-C", str(root), "log", "HEAD", "--format=%H",
         f"--grep=Task: {ticket}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise GovError("GIT_FAILURE",
                        f"git log failed: {result.stderr.strip()[:200]}",
                        {"ticket": ticket})

    shas = [s.strip() for s in result.stdout.strip().split("\n") if s.strip()]
    commits = []
    for sha in shas:
        trailers = _read_trailers(root, sha)
        task_values = trailers.get("Task", [])
        if not any(v.strip() == ticket for v in task_values):
            continue
        paths = _commit_paths(root, sha)
        commits.append({"sha": sha, "trailers": trailers, "paths": paths})
    return commits


def _read_trailers(root: Path, sha: str) -> dict[str, list[str]]:
    import subprocess
    result = subprocess.run(
        ["git", "-C", str(root), "log", "-1", "--format=%(trailers)", sha],
        capture_output=True, text=True,
    )
    trailers: dict[str, list[str]] = {}
    for line in result.stdout.split("\n"):
        line = line.strip()
        if ": " in line:
            key, _, value = line.partition(": ")
            key = key.strip()
            value = value.strip()
            if key and value:
                trailers.setdefault(key, []).append(value)
        elif ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if key and value:
                trailers.setdefault(key, []).append(value)
    return trailers


def _commit_paths(root: Path, sha: str) -> list[str]:
    import subprocess
    result = subprocess.run(
        ["git", "-C", str(root), "diff-tree", "--no-commit-id",
         "--name-only", "-r", sha],
        capture_output=True, text=True,
    )
    return [p.strip() for p in result.stdout.strip().split("\n") if p.strip()]


# ---------------------------------------------------------------------------
# Verification helpers
# ---------------------------------------------------------------------------

def _check_trailers(commits: list[dict], ticket: str) -> None:
    from gov.cli.errors import GovError
    if not commits:
        raise GovError("TRAILER_MISSING",
                        f"no commits found with Task: {ticket} trailer",
                        {"ticket": ticket})
    for c in commits:
        impl_vals = c["trailers"].get("Implements", [])
        if not impl_vals:
            raise GovError("TRAILER_MISSING",
                            f"commit {c['sha'][:12]} lacks Implements: trailer",
                            {"commit": c["sha"][:12], "ticket": ticket})


def _is_infra(path: str) -> bool:
    if any(path.startswith(p) for p in _INFRA_PREFIXES):
        return True
    return path in ("README.md", "pyproject.toml", ".gitignore", "LICENSE")


def _check_commit_containment(commits: list[dict],
                               allowed_paths: list[str]) -> None:
    import fnmatch
    from gov.cli.errors import GovError

    for c in commits:
        for p in c["paths"]:
            if not p or _is_infra(p):
                continue
            if not any(fnmatch.fnmatch(p, pat) for pat in allowed_paths):
                raise GovError(
                    "CONTAINMENT_FINDING",
                    f"commit {c['sha'][:12]} changes {p} outside allowed_paths",
                    {"commit": c["sha"][:12], "path": p},
                )


# ---------------------------------------------------------------------------
# Probe gate (FULL-profile tickets, A5)
# ---------------------------------------------------------------------------

def _check_probe(root: Path, ticket: str) -> None:
    import subprocess
    import yaml
    from gov.cli.errors import GovError

    probe_dir = root / "docs" / "probes" / ticket
    if not probe_dir.is_dir():
        raise GovError("PROBE_MISSING",
                        f"FULL-profile ticket {ticket} has no probe record",
                        {"ticket": ticket})

    for path in probe_dir.glob("*.md"):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            raise GovError("PROBE_INVALID",
                            f"probe file {path.name} is unreadable",
                            {"ticket": ticket, "file": path.name})
        if not text.startswith("---"):
            raise GovError("PROBE_INVALID",
                            f"probe file {path.name} has no YAML frontmatter",
                            {"ticket": ticket, "file": path.name})
        end = text.find("---", 3)
        if end < 0:
            raise GovError("PROBE_INVALID",
                            f"probe file {path.name} has unterminated frontmatter",
                            {"ticket": ticket, "file": path.name})
        try:
            pf = yaml.safe_load(text[3:end])
        except yaml.YAMLError:
            raise GovError("PROBE_INVALID",
                            f"probe file {path.name} has malformed YAML",
                            {"ticket": ticket, "file": path.name})
        if not isinstance(pf, dict) or pf.get("type") != "probe":
            continue
        if pf.get("task") != ticket:
            continue

        reviewer = pf.get("reviewer_session", "")
        implementer = pf.get("implementer_session", "")
        if not reviewer or not implementer:
            raise GovError("PROBE_INVALID",
                            "probe record missing session identifiers",
                            {"ticket": ticket})
        if reviewer == implementer:
            raise GovError("PROBE_INVALID",
                            "the probe reviewer is the implementer",
                            {"ticket": ticket})
        if pf.get("reviewer_wrote_nothing") is not True:
            raise GovError("PROBE_INVALID",
                            "the probe reviewer wrote to the repository",
                            {"ticket": ticket})

        commissioned = pf.get("commissioned_by", "")
        if commissioned != "orchestrator":
            raise GovError("PROBE_INVALID",
                            f"probe commissioned_by must be 'orchestrator', got '{commissioned}'",
                            {"ticket": ticket})
        judged = pf.get("judged_by", "")
        if judged != "orchestrator":
            raise GovError("PROBE_INVALID",
                            f"probe judged_by must be 'orchestrator', got '{judged}'",
                            {"ticket": ticket})
        judgement = pf.get("judgement", "")
        if not str(judgement).strip():
            raise GovError("PROBE_INVALID",
                            "probe has no judgement",
                            {"ticket": ticket})

        # A5: probed_commit must be named
        probed_commit = pf.get("probed_commit")
        if not probed_commit:
            raise GovError("PROBE_INVALID",
                            "probe record does not name the probed commit",
                            {"ticket": ticket})

        # A5: probed_commit must be ancestor of HEAD
        anc = subprocess.run(
            ["git", "-C", str(root), "merge-base", "--is-ancestor",
             str(probed_commit), "HEAD"],
            capture_output=True, text=True,
        )
        if anc.returncode != 0:
            raise GovError("PROBE_INVALID",
                            "probed commit is not an ancestor of HEAD",
                            {"ticket": ticket,
                             "probed_commit": str(probed_commit)})

        # A5: no commit between probed_commit..HEAD with reviewer role
        between = subprocess.run(
            ["git", "-C", str(root), "log",
             f"{probed_commit}..HEAD", "--format=%H"],
            capture_output=True, text=True,
        )
        for sha in between.stdout.strip().split("\n"):
            sha = sha.strip()
            if not sha:
                continue
            tr = _read_trailers(root, sha)
            if "independent-auditor" in tr.get("Role", []):
                raise GovError(
                    "PROBE_INVALID",
                    "a commit between the probed commit and HEAD "
                    "carries the reviewer's role",
                    {"ticket": ticket, "commit": sha[:12]})

        # A5: no ticket commit outside tests/ and docs/probes/ after probe
        after_probe = subprocess.run(
            ["git", "-C", str(root), "log",
             f"{probed_commit}..HEAD", "--format=%H",
             f"--grep=Task: {ticket}"],
            capture_output=True, text=True,
        )
        for sha in after_probe.stdout.strip().split("\n"):
            sha = sha.strip()
            if not sha:
                continue
            tr = _read_trailers(root, sha)
            task_values = tr.get("Task", [])
            if not any(v.strip() == ticket for v in task_values):
                continue
            paths = _commit_paths(root, sha)
            for p in paths:
                if not p.startswith("tests/") and not p.startswith("docs/probes/"):
                    raise GovError(
                        "PROBE_INVALID",
                        f"ticket commit {sha[:12]} changes {p} "
                        "after the probed commit",
                        {"ticket": ticket, "commit": sha[:12], "path": p})

        # A5: reviewer session name not in any ticket commit's trailers
        all_tc = subprocess.run(
            ["git", "-C", str(root), "log", "HEAD", "--format=%H",
             f"--grep=Task: {ticket}"],
            capture_output=True, text=True,
        )
        for sha in all_tc.stdout.strip().split("\n"):
            sha = sha.strip()
            if not sha:
                continue
            tr = _read_trailers(root, sha)
            task_values = tr.get("Task", [])
            if not any(v.strip() == ticket for v in task_values):
                continue
            for values in tr.values():
                for val in values:
                    if reviewer in val:
                        raise GovError(
                            "PROBE_INVALID",
                            f"commit {sha[:12]} trailer names the "
                            "reviewer session",
                            {"ticket": ticket, "commit": sha[:12]})

        return

    raise GovError("PROBE_MISSING",
                    f"FULL-profile ticket {ticket} has no valid probe record",
                    {"ticket": ticket})


# ---------------------------------------------------------------------------
# Test runner (A2)
# ---------------------------------------------------------------------------

def _run_tests(root: Path, test_path: str, timeout: int,
               ignore_dirs: list[str] | None = None,
               ) -> tuple[int, list[str], dict]:
    import os
    import shutil
    import subprocess
    import sys

    from gov.cli.errors import GovError

    env = dict(os.environ)
    src = str(root / "src")
    pythonpath = env.get("PYTHONPATH", "")
    if src not in pythonpath:
        env["PYTHONPATH"] = src + (":" + pythonpath if pythonpath else "")

    if "PYTHONUSERBASE" not in env:
        pytest_bin = shutil.which("pytest")
        if pytest_bin:
            env["PYTHONUSERBASE"] = str(Path(pytest_bin).resolve().parent.parent)

    cmd = [sys.executable, "-m", "pytest", test_path, "-q",
           "-p", "no:cacheprovider", "--tb=line", "--no-header"]
    if ignore_dirs:
        for d in ignore_dirs:
            cmd.extend(["--ignore", d])

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=str(root),
            env=env, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise GovError("TIMEOUT",
                        f"test run exceeded {timeout}s time limit",
                        {"test_path": test_path, "timeout": timeout},
                        exit_code=EXIT_CHECK_FAILED)

    failures = []
    counts = {"passed": 0, "failed": 0, "errors": 0}

    if result.returncode == 2:
        for line in (result.stdout + "\n" + result.stderr).split("\n"):
            stripped = line.strip()
            if stripped and ("ERROR" in stripped or "SyntaxError" in stripped):
                failures.append(stripped)
        if not failures:
            failures = [f"collection error in {test_path}"]
        counts["errors"] = len(failures)
    elif result.returncode != 0 and result.returncode != 5:
        for line in result.stdout.split("\n"):
            if "FAILED" in line:
                failures.append(line.strip())
        if not failures:
            failures = [f"tests exited {result.returncode}"]

    counts = _parse_test_counts(result.stdout, counts)
    return result.returncode, failures, counts


def _parse_test_counts(output: str, counts: dict) -> dict:
    import re
    for line in reversed(output.split("\n")):
        line = line.strip()
        if not line:
            continue
        m_passed = re.search(r"(\d+)\s+passed", line)
        m_failed = re.search(r"(\d+)\s+failed", line)
        m_errors = re.search(r"(\d+)\s+error", line)
        if m_passed or m_failed or m_errors:
            if m_passed:
                counts["passed"] = int(m_passed.group(1))
            if m_failed:
                counts["failed"] = int(m_failed.group(1))
            if m_errors:
                counts["errors"] = int(m_errors.group(1))
            break
    return counts


def _merge_counts(total: dict, new: dict) -> None:
    for key in ("passed", "failed", "errors"):
        total[key] = total.get(key, 0) + new.get(key, 0)


# ---------------------------------------------------------------------------
# Governance checks (A7)
# ---------------------------------------------------------------------------

def _check_governance(root: Path, commits: list[dict]) -> dict | None:
    import yaml as _yaml
    from gov.cli.errors import GovError

    has_gov_change = False
    ticket_check_ids = set()
    checks_prefix = "template/governance/kernel/checks/"
    for c in commits:
        for p in c["paths"]:
            if any(p.startswith(prefix) for prefix in _GOVERNANCE_PREFIXES):
                has_gov_change = True
            if p.startswith(checks_prefix) and p.endswith(".yaml"):
                check_path = root / p
                if check_path.is_file():
                    try:
                        decl = _yaml.safe_load(
                            check_path.read_text(encoding="utf-8"))
                        if isinstance(decl, dict) and "id" in decl:
                            ticket_check_ids.add(decl["id"])
                    except Exception:
                        pass

    if not has_gov_change:
        return None

    from gov.check.runner import run_checks
    result, _has_hard_block = run_checks(root)

    if ticket_check_ids:
        failing = []
        for check in result.get("checks", []):
            cid = check.get("id")
            if cid not in ticket_check_ids:
                continue
            sev = check.get("severity", "")
            status = check.get("status", "")
            if sev == "hard-block" or status == "RED":
                failing.append(cid or "unknown")
        if failing:
            raise GovError("CHECK_FAILED",
                            f"governance checks failed: {', '.join(failing)}",
                            {"failing_checks": failing},
                            exit_code=EXIT_CHECK_FAILED)

    return result


# ---------------------------------------------------------------------------
# Failure handling and iteration tracking (A6)
# ---------------------------------------------------------------------------

def _handle_failure(root: Path, ticket: str, failures: list[str],
                    front: dict, disposition: str | None = None,
                    context_hash: str | None = None) -> None:
    import json
    from datetime import datetime, timezone

    from gov.cli.errors import GovError

    iterations_dir = root / ".gov-runtime" / "iterations"
    iterations_dir.mkdir(parents=True, exist_ok=True)
    iter_file = iterations_dir / f"{ticket}.json"

    failure_set = sorted(set(failures))
    prev = {"count": 0, "last_failures": [], "outcomes": []}
    if iter_file.is_file():
        try:
            prev = json.loads(iter_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            raise GovError("ITERATION_CORRUPT",
                            "iteration count file cannot be read or parsed",
                            {"ticket": ticket})

    count = prev.get("count", 0) + 1
    outcomes = prev.get("outcomes", [])
    outcomes.append({
        "failures": failure_set,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    })

    iter_file.write_text(json.dumps({
        "count": count,
        "last_failures": failure_set,
        "outcomes": outcomes,
    }), encoding="utf-8")

    if count >= 3:
        esc_dir = root / ".gov-runtime" / "escalations"
        esc_dir.mkdir(parents=True, exist_ok=True)
        esc_file = esc_dir / f"{ticket}.json"
        esc_file.write_text(json.dumps({
            "ticket": ticket,
            "outcomes": outcomes,
            "reason": "three consecutive non-converging iterations",
            "options": _ESCALATION_OPTIONS,
        }), encoding="utf-8")

        safe_outcomes = [
            {k: v for k, v in o.items() if k != "iteration"}
            for o in outcomes[-1:]
        ]
        raise GovError(
            "ESCALATION_BLOCKED",
            "three consecutive non-converging iterations reached",
            {
                "outcomes": safe_outcomes,
                "reason": "three consecutive non-converging iterations",
                "options": _ESCALATION_OPTIONS,
            },
            exit_code=EXIT_BLOCKED,
        )

    _open_repair_ticket(root, ticket, failures, disposition, context_hash)


# ---------------------------------------------------------------------------
# Repair tickets (B3)
# ---------------------------------------------------------------------------

def _create_repair_ticket_fallback(root: Path, title: str) -> str | None:
    import hashlib
    import yaml
    from datetime import datetime, timezone
    from gov.tasks.tickets import TICKETS_REL

    ts = datetime.now(timezone.utc)
    h = hashlib.sha256(f"{title}:{ts.isoformat()}".encode()).hexdigest()[:6]
    repair_id = f"tt-{h}"

    tickets_dir = root / TICKETS_REL
    tickets_dir.mkdir(parents=True, exist_ok=True)
    repair_path = tickets_dir / f"{repair_id}.md"

    front = {
        "id": repair_id,
        "title": title[:100],
        "type": "task",
        "status": "open",
        "state_class": "AUTHORITATIVE",
        "created": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    try:
        text = ("---\n"
                + yaml.safe_dump(front, sort_keys=False, allow_unicode=True)
                + "---\n\n"
                + f"# {repair_id}\n\n{title}\n")
        repair_path.write_text(text, encoding="utf-8")
        return repair_id
    except Exception:
        return None


def _open_repair_ticket(root: Path, ticket: str, failures: list[str],
                        disposition: str | None = None,
                        context_hash: str | None = None) -> None:
    import yaml
    from gov.tasks.tickets import create

    title = f"Repair {ticket}: {failures[0][:60] if failures else 'close failure'}"
    try:
        repair_id = create(root, title)
    except Exception:
        repair_id = _create_repair_ticket_fallback(root, title)
    if not repair_id:
        return

    repair_path = root / ".tickets" / f"{repair_id}.md"
    if repair_path.is_file():
        text = repair_path.read_text(encoding="utf-8")
        if text.startswith("---"):
            end = text.find("---", 3)
            if end > 0:
                try:
                    rf = yaml.safe_load(text[3:end])
                except yaml.YAMLError:
                    rf = {}
                if isinstance(rf, dict):
                    rf["parent"] = ticket
                    rf["findings"] = failures[:10]
                    rf["disposition"] = disposition or "unclassed"
                    if context_hash is not None:
                        rf["context_hash"] = context_hash
                    body = text[end + 3:]
                    new_text = ("---\n"
                                + yaml.safe_dump(rf, sort_keys=False,
                                                 allow_unicode=True)
                                + "---" + body)
                    repair_path.write_text(new_text, encoding="utf-8")


# ---------------------------------------------------------------------------
# Owner decision validation (A6)
# ---------------------------------------------------------------------------

def _validate_owner_decision(root: Path, dec_id: str) -> None:
    import yaml
    from gov.cli.errors import GovError

    found = None
    for candidate in [
        root / "docs" / "adr" / f"{dec_id}.md",
        root / "governance" / "decisions" / f"{dec_id}.md",
    ]:
        if candidate.is_file():
            found = candidate
            break

    if found is None:
        docs_dir = root / "docs"
        if docs_dir.is_dir():
            for md in docs_dir.rglob(f"{dec_id}.md"):
                found = md
                break

    if found is None:
        raise GovError("INVALID_DECISION",
                        f"decision {dec_id} not found",
                        {"decision": dec_id})

    text = found.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise GovError("INVALID_DECISION",
                        f"decision {dec_id} has no frontmatter",
                        {"decision": dec_id})
    end_idx = text.find("---", 3)
    if end_idx < 0:
        raise GovError("INVALID_DECISION",
                        f"decision {dec_id} has invalid frontmatter",
                        {"decision": dec_id})
    try:
        df = yaml.safe_load(text[3:end_idx])
    except yaml.YAMLError:
        raise GovError("INVALID_DECISION",
                        f"decision {dec_id} has invalid YAML",
                        {"decision": dec_id})

    if not isinstance(df, dict):
        raise GovError("INVALID_DECISION",
                        f"decision {dec_id} is not a valid record",
                        {"decision": dec_id})

    status = str(df.get("status", "")).upper()
    if status != "ACTIVE":
        raise GovError("INVALID_DECISION",
                        f"decision {dec_id} is not ACTIVE (status: {status})",
                        {"decision": dec_id})

    try:
        from gov.decisions import check as check_decisions
        findings = check_decisions(root)
        for f in findings:
            if (f.get("code") == "ACTIVE_UNAPPROVED"
                    and dec_id in f.get("ids", [])):
                raise GovError("INVALID_DECISION",
                                f"decision {dec_id} is ACTIVE but unapproved",
                                {"decision": dec_id})
    except GovError:
        raise
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Data collection for the close record
# ---------------------------------------------------------------------------

def _collect_requirements(commits: list[dict]) -> list[str]:
    reqs = set()
    for c in commits:
        for val in c["trailers"].get("Implements", []):
            for item in val.replace(",", " ").split():
                if item.strip():
                    reqs.add(item.strip())
    return sorted(reqs)


def _collect_test_paths(root: Path, wbs: str) -> list[str]:
    paths = []
    tests_dir = root / "tests"
    if not tests_dir.is_dir():
        return paths
    acc = tests_dir / "acceptance" / wbs
    if acc.is_dir():
        for f in sorted(acc.rglob("test_*.py")):
            paths.append(str(f.relative_to(root)))
    for f in sorted(tests_dir.rglob("test_*.py")):
        rel = str(f.relative_to(root))
        if rel.startswith(f"tests/acceptance/{wbs}/"):
            continue
        if rel not in paths:
            paths.append(rel)
    return paths


def _collect_commit_files(commits: list[dict]) -> list[str]:
    files = set()
    for c in commits:
        for p in c["paths"]:
            files.add(p)
    return sorted(files)


def _read_skill_versions(root: Path) -> list[dict]:
    import yaml

    versions = []

    skill_dir = root / "template" / "governance" / "kernel" / "skills"
    if skill_dir.is_dir():
        for folder in sorted(skill_dir.iterdir()):
            skill_file = folder / "SKILL.md"
            if not skill_file.is_file():
                continue
            try:
                text = skill_file.read_text(encoding="utf-8")
            except OSError:
                continue
            if not text.startswith("---"):
                continue
            end = text.find("---", 3)
            if end < 0:
                continue
            try:
                front = yaml.safe_load(text[3:end])
            except yaml.YAMLError:
                continue
            if isinstance(front, dict):
                name = str(front.get("name", folder.name))
                version = front.get("version")
                versions.append({
                    "name": name,
                    "version": str(version) if version else "no version",
                })

    vendor_dir = root / "template" / "governance" / "kernel" / "vendor"
    if vendor_dir.is_dir():
        for skill_file in sorted(vendor_dir.rglob("SKILL.md")):
            try:
                text = skill_file.read_text(encoding="utf-8")
            except OSError:
                continue
            if not text.startswith("---"):
                continue
            end = text.find("---", 3)
            if end < 0:
                continue
            try:
                front = yaml.safe_load(text[3:end])
            except yaml.YAMLError:
                continue
            if isinstance(front, dict):
                name = str(front.get("name", skill_file.parent.name))
                versions.append({"name": name, "version": "no version"})

    return versions


def _build_inputs(root: Path, ticket: str, front: dict) -> list[dict]:
    import hashlib
    inputs = []

    ticket_path = root / ".tickets" / f"{ticket}.md"
    if ticket_path.is_file():
        h = hashlib.sha256(ticket_path.read_bytes()).hexdigest()
        inputs.append({"id": ticket, "hash": f"sha256:{h}"})

    for source_id in (front.get("sources") or []):
        source_path = _find_source(root, str(source_id))
        if source_path and source_path.is_file():
            h = hashlib.sha256(source_path.read_bytes()).hexdigest()
            inputs.append({"id": str(source_id), "hash": f"sha256:{h}"})
        else:
            inputs.append({"id": str(source_id), "hash": None,
                           "reason": "source file not found"})

    return inputs


def _find_source(root: Path, source_id: str) -> Path | None:
    candidate = root / source_id
    if candidate.is_file():
        return candidate
    candidate = root / ".tickets" / f"{source_id}.md"
    if candidate.is_file():
        return candidate
    candidate = root / "docs" / "adr" / f"{source_id}.md"
    if candidate.is_file():
        return candidate
    candidate = root / "governance" / "project" / f"{source_id}.yaml"
    if candidate.is_file():
        return candidate
    return None


# ---------------------------------------------------------------------------
# Writing records
# ---------------------------------------------------------------------------

def _write_checkpoint(root: Path, ticket: str) -> dict:
    from gov.checkpoint.record import write as checkpoint_write
    return checkpoint_write(root, ticket, "ticket-transition",
                            "ticket closed", [])


def _write_close_record(root: Path, ticket: str, packet_hash: str,
                         inputs: list[dict], requirements: list[str],
                         decisions: list[str], test_paths: list[str],
                         skill_versions: list[dict],
                         checkpoint_info: dict,
                         test_counts: dict,
                         gov_check_result: dict | None,
                         head_commit: str,
                         commit_files: list[str]) -> str:
    import yaml
    from datetime import datetime, timezone

    close_id = f"CL-{ticket}"
    close_dir = root / "docs" / "close" / ticket
    close_dir.mkdir(parents=True, exist_ok=True)
    close_path = close_dir / f"{close_id}.md"
    close_rel = f"docs/close/{ticket}/{close_id}.md"
    cp_path = checkpoint_info.get("path", "")

    outputs = list(commit_files) + [close_rel, cp_path]

    front = {
        "id": close_id,
        "type": "close",
        "status": "ACTIVE",
        "state_class": "AUTHORITATIVE",
        "task": ticket,
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "packet_hash": packet_hash,
        "inputs": inputs,
        "outputs": outputs,
        "requirements_implemented": requirements,
        "decisions_applied": decisions,
        "tests_produced": test_paths,
        "tests_run": test_counts,
        "deviations": "not measured",
        "skill_versions": skill_versions,
    }

    if gov_check_result is not None:
        front["governance_checks"] = gov_check_result
        front["check_commit"] = head_commit

    text = ("---\n"
            + yaml.safe_dump(front, sort_keys=False, allow_unicode=True)
            + "---\n\n")
    text += f"# {close_id} — Close record for {ticket}\n"
    close_path.write_text(text, encoding="utf-8")
    return close_rel


def _set_ticket_closed(root: Path, ticket: str) -> None:
    import yaml
    from gov.cli.errors import GovError

    path = root / ".tickets" / f"{ticket}.md"
    if not path.is_file():
        raise GovError("TICKET_UNKNOWN",
                        f"ticket file not found: {ticket}",
                        {"ticket": ticket})
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise GovError("TICKET_INVALID",
                        f"ticket {ticket} has no frontmatter",
                        {"ticket": ticket})
    end = text.find("---", 3)
    if end < 0:
        raise GovError("TICKET_INVALID",
                        f"ticket {ticket} has unterminated frontmatter",
                        {"ticket": ticket})
    try:
        front = yaml.safe_load(text[3:end])
    except yaml.YAMLError:
        raise GovError("TICKET_INVALID",
                        f"ticket {ticket} has malformed YAML",
                        {"ticket": ticket})
    if not isinstance(front, dict):
        raise GovError("TICKET_INVALID",
                        f"ticket {ticket} frontmatter is not a dict",
                        {"ticket": ticket})
    front["status"] = "closed"
    body = text[end + 3:]
    new_text = ("---\n"
                + yaml.safe_dump(front, sort_keys=False, allow_unicode=True)
                + "---" + body)
    path.write_text(new_text, encoding="utf-8")
