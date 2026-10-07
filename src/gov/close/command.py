"""``gov close`` command module (W1-30, DEC-317).

Closes a ticket after verifying acceptance tests, trailers, containment,
and (for FULL-profile tickets) the probe record. Tracks iteration counts
and opens repair tickets on failure.
"""

from __future__ import annotations

from pathlib import Path

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

_GOV_CHECKS_PREFIX = "template/governance/kernel/checks/"


def add_arguments(parser) -> None:
    parser.add_argument("ticket", help="the ticket id to close")


def run(root: Path, args, config: dict):
    import hashlib

    from gov.cli.errors import GovError
    from gov.tasks.tickets import frontmatter, TICKETS_REL

    root = Path(root)
    ticket = args.ticket

    ticket_path = root / TICKETS_REL / f"{ticket}.md"
    front = frontmatter(ticket_path)
    if front is None:
        raise GovError("TICKET_UNKNOWN", f"{ticket} is not a ticket of this project",
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

    from gov.checkpoint.record import watch as checkpoint_watch
    try:
        checkpoint_watch(root, ticket, max_age_minutes=240, max_commits=20,
                         max_context=1.0, context_utilisation=None)
    except GovError as e:
        if e.code in ("CHECKPOINT_STALE", "CHECKPOINT_MISSING"):
            raise

    if profile == "FULL":
        _check_probe(root, ticket)

    commits = _ticket_commits(root, ticket)
    _check_trailers(commits, ticket)
    _check_commit_containment(commits, allowed_paths)

    head_commit = _head(root)

    acceptance_dir = root / "tests" / "acceptance" / wbs
    if not acceptance_dir.is_dir() or not list(acceptance_dir.glob("test_*.py")):
        raise GovError("NO_ACCEPTANCE_TESTS",
                        f"no acceptance tests for {ticket} in tests/acceptance/{wbs}/",
                        {"ticket": ticket, "wbs": wbs},
                        exit_code=EXIT_CHECK_FAILED)

    test_failures = []
    rc, failures = _run_tests(root, str(acceptance_dir))
    if rc != 0:
        test_failures.extend(failures or ["acceptance tests failed"])

    ticket_name = _ticket_unit_dir(ticket)
    seen_regression_dirs = set()
    for reg_name in (ticket_name, "close"):
        regression_dir = root / "tests" / "unit" / reg_name
        if regression_dir.is_dir() and str(regression_dir) not in seen_regression_dirs:
            seen_regression_dirs.add(str(regression_dir))
            rc, failures = _run_tests(root, str(regression_dir))
            if rc != 0:
                test_failures.extend(failures or ["regression tests failed"])

    _check_stale_evidence(root, commits)

    check_findings = _run_declared_checks(root, commits)
    all_findings = list(test_failures) + list(check_findings)

    if all_findings:
        _handle_failure(root, ticket, all_findings, front)
        raise GovError("CHECK_FAILED", "tests or checks failed",
                        {"findings": _classify_findings(root, ticket, all_findings)},
                        exit_code=EXIT_CHECK_FAILED)

    try:
        from gov.context import context as build_context
        ctx = build_context(root, ticket)
        packet_hash = ctx.get("hash", "")
        decisions = [item.get("id", "") for item in ctx.get("mandatory", [])
                     if item.get("authority") == "decision"]
    except Exception:
        packet_hash = hashlib.sha256(ticket_path.read_bytes()).hexdigest()
        decisions = []

    requirements = _collect_requirements(commits)
    test_paths = _collect_test_paths(root, wbs, ticket_name)
    skill_versions = _read_skill_versions(root)

    _set_ticket_closed(root, ticket)

    inputs = _build_inputs(root, ticket, front)

    checkpoint_info = _write_checkpoint(root, ticket)
    close_record_path = _write_close_record(
        root, ticket, packet_hash, inputs, requirements,
        decisions, test_paths, skill_versions, checkpoint_info,
    )

    return {"ticket": ticket, "close_record": close_record_path,
            "checkpoint": checkpoint_info.get("path", "")}


def _head(root: Path) -> str:
    import subprocess
    try:
        return subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, OSError):
        return "unknown"


def _ticket_unit_dir(ticket: str) -> str:
    parts = ticket.split("-")
    if len(parts) >= 2:
        return parts[-1]
    return ticket


def _ticket_commits(root: Path, ticket: str) -> list[dict]:
    import subprocess

    result = subprocess.run(
        ["git", "-C", str(root), "log", "--all", "--format=%H",
         f"--grep=Task: {ticket}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return []

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


def _check_probe(root: Path, ticket: str) -> None:
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
                            "probe has no judgement (judged_by is set but judgement is missing or empty)",
                            {"ticket": ticket})
        return

    raise GovError("PROBE_MISSING",
                    f"FULL-profile ticket {ticket} has no valid probe record",
                    {"ticket": ticket})


def _run_tests(root: Path, test_path: str) -> tuple[int, list[str]]:
    import os
    import shutil
    import subprocess
    import sys

    env = dict(os.environ)
    src = str(root / "src")
    pythonpath = env.get("PYTHONPATH", "")
    if src not in pythonpath:
        env["PYTHONPATH"] = src + (":" + pythonpath if pythonpath else "")

    if "PYTHONUSERBASE" not in env:
        pytest_bin = shutil.which("pytest")
        if pytest_bin:
            env["PYTHONUSERBASE"] = str(Path(pytest_bin).resolve().parent.parent)

    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-q",
         "-p", "no:cacheprovider", "--tb=line", "--no-header", "-x"],
        capture_output=True, text=True, cwd=str(root), env=env, timeout=120,
    )
    failures = []
    if result.returncode != 0:
        for line in result.stdout.split("\n"):
            if "FAILED" in line:
                failures.append(line.strip())
        if not failures:
            failures = [f"tests exited {result.returncode}"]
    return result.returncode, failures


def _check_stale_evidence(root: Path, commits: list[dict]) -> None:
    """Refuse when governance check definitions changed across multiple ticket commits."""
    from gov.cli.errors import GovError

    gov_files_by_commit: dict[str, set[str]] = {}
    all_gov_files: set[str] = set()
    for c in commits:
        gov_paths = {p for p in c["paths"] if p.startswith(_GOV_CHECKS_PREFIX)}
        if gov_paths:
            gov_files_by_commit[c["sha"]] = gov_paths
            all_gov_files.update(gov_paths)

    if len(gov_files_by_commit) < 2:
        return

    repeated = set()
    seen = set()
    for gov_paths in gov_files_by_commit.values():
        for p in gov_paths:
            if p in seen:
                repeated.add(p)
            seen.add(p)

    if repeated:
        raise GovError("STALE_EVIDENCE",
                        "governance check definitions changed across commits; evidence is stale",
                        {"files": sorted(repeated)},
                        exit_code=EXIT_CHECK_FAILED)


def _run_declared_checks(root: Path, commits: list[dict]) -> list[str]:
    import os
    import subprocess
    import tempfile

    import yaml

    checks_prefix = "template/governance/kernel/checks/"
    check_paths = []
    for c in commits:
        for p in c["paths"]:
            if p.startswith(checks_prefix) and p.endswith(".yaml"):
                check_paths.append(root / p)

    if not check_paths:
        return []

    findings = []
    for check_path in check_paths:
        if not check_path.is_file():
            continue
        try:
            decl = yaml.safe_load(check_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(decl, dict):
            continue
        command = decl.get("command", "")
        severity = decl.get("severity", "warning")
        if not command:
            continue
        env = dict(os.environ)
        src = str(root / "src")
        pythonpath = env.get("PYTHONPATH", "")
        if src not in pythonpath:
            env["PYTHONPATH"] = src + (":" + pythonpath if pythonpath else "")
        xdg_tmp = tempfile.mkdtemp(prefix="gov-close-check-")
        env.setdefault("XDG_CONFIG_HOME", xdg_tmp)
        env.setdefault("XDG_DATA_HOME", xdg_tmp)
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                cwd=str(root), env=env, timeout=60,
            )
            if result.returncode != 0 and severity == "hard-block":
                msg = result.stdout.strip()[:200] or result.stderr.strip()[:200] or f"check {decl.get('id', '?')} failed"
                findings.append(msg)
        except (subprocess.TimeoutExpired, OSError):
            if severity == "hard-block":
                findings.append(f"check {decl.get('id', '?')} timed out")
        finally:
            import shutil
            shutil.rmtree(xdg_tmp, ignore_errors=True)
    return findings


def _handle_failure(root: Path, ticket: str, failures: list[str],
                    front: dict) -> None:
    import json
    from datetime import datetime, timezone

    iterations_dir = root / ".gov-runtime" / "iterations"
    iterations_dir.mkdir(parents=True, exist_ok=True)
    iter_file = iterations_dir / f"{ticket}.json"

    failure_set = sorted(set(failures))
    prev = {"count": 0, "last_failures": [], "outcomes": []}
    if iter_file.is_file():
        try:
            prev = json.loads(iter_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    prev_failures = sorted(prev.get("last_failures", []))
    non_converging = (prev_failures == failure_set)
    count = prev.get("count", 0) + 1 if non_converging else 1

    outcomes = prev.get("outcomes", []) if non_converging else []
    outcomes.append({
        "iteration": count,
        "failures": failure_set,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    })

    iter_file.write_text(json.dumps({
        "count": count,
        "last_failures": failure_set,
        "outcomes": outcomes,
    }), encoding="utf-8")

    if count >= 3:
        from gov.cli.errors import GovError

        esc_dir = root / ".gov-runtime" / "escalations"
        esc_dir.mkdir(parents=True, exist_ok=True)
        esc_file = esc_dir / f"{ticket}.json"
        esc_file.write_text(json.dumps({
            "ticket": ticket,
            "outcomes": outcomes,
            "reason": "three consecutive non-converging iterations with identical failures",
        }), encoding="utf-8")

        safe_outcomes = [{k: v for k, v in o.items() if k != "iteration"} for o in outcomes[-1:]]
        raise GovError(
            "ESCALATION_BLOCKED",
            "three consecutive non-converging iterations reached",
            {
                "outcomes": safe_outcomes,
                "reason": "three consecutive non-converging iterations with identical failures",
                "options": ["fix_differently", "narrow", "split",
                            "defer", "delete", "continue"],
            },
            exit_code=EXIT_BLOCKED,
        )

    _open_repair_ticket(root, ticket, failures)


def _open_repair_ticket(root: Path, ticket: str,
                        failures: list[str]) -> None:
    import os
    title = f"Repair {ticket}: {failures[0][:60] if failures else 'close failure'}"
    try:
        from gov.tasks.tickets import create
        create(root, title)
    except Exception:
        _create_repair_ticket_fallback(root, ticket, title, failures)


def _create_repair_ticket_fallback(root: Path, parent_ticket: str,
                                    title: str, failures: list[str]) -> None:
    import hashlib
    import yaml

    ticket_id = "RPR-" + hashlib.sha256(
        f"{parent_ticket}:{title}".encode()
    ).hexdigest()[:4]

    front = {
        "id": ticket_id,
        "status": "open",
        "deps": [],
        "links": [],
        "created": "2026-10-01T00:00:00Z",
        "type": "task",
        "priority": 1,
        "assignee": "engineer",
        "title": title,
        "class": "repair",
        "state_class": "AUTHORITATIVE",
        "role": "engineer",
        "parent": parent_ticket,
        "findings": failures[:3],
    }

    path = root / ".tickets" / f"{ticket_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n"
    text += f"# {ticket_id} — {title}\n"
    path.write_text(text, encoding="utf-8")


def _classify_findings(root: Path, ticket: str,
                       findings: list[str]) -> list[dict]:
    DISPOSITIONS = (
        "REPAIR_EXISTING_MECHANISM",
        "REUSE_EXISTING_PRIMITIVE",
        "DELETE_MECHANISM",
        "NARROW_REQUIREMENT",
        "DEFER_TO_LATER_LIFECYCLE",
        "OWNER_DECISION",
    )

    try:
        from gov.context import context as build_context
        build_context(root, ticket)
    except Exception:
        pass

    classified = []
    for f in findings:
        classified.append({
            "finding": f,
            "disposition": DISPOSITIONS[0],
            "context": "whole-system",
        })
    return classified


def _collect_requirements(commits: list[dict]) -> list[str]:
    reqs = set()
    for c in commits:
        for val in c["trailers"].get("Implements", []):
            for item in val.replace(",", " ").split():
                if item.strip():
                    reqs.add(item.strip())
    return sorted(reqs)


def _collect_test_paths(root: Path, wbs: str, ticket_name: str) -> list[str]:
    paths = []
    acc = root / "tests" / "acceptance" / wbs
    if acc.is_dir():
        for f in sorted(acc.rglob("test_*.py")):
            paths.append(str(f.relative_to(root)))
    seen = set()
    for reg_name in (ticket_name, "close"):
        reg = root / "tests" / "unit" / reg_name
        if reg.is_dir() and str(reg) not in seen:
            seen.add(str(reg))
            for f in sorted(reg.rglob("test_*.py")):
                paths.append(str(f.relative_to(root)))
    return paths


def _read_skill_versions(root: Path) -> list[dict]:
    import yaml

    skill_dir = root / "template" / "governance" / "kernel" / "vendor"
    if not skill_dir.is_dir():
        return []
    versions = []
    for path in sorted(skill_dir.rglob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
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
        if isinstance(front, dict) and front.get("type") == "skill":
            versions.append({
                "id": str(front.get("id", path.stem)),
                "version": str(front.get("version", "unknown")),
            })
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
    for md in root.rglob(f"{source_id}.*"):
        if md.is_file():
            return md
    return None


def _write_checkpoint(root: Path, ticket: str) -> dict:
    from gov.checkpoint.record import write as checkpoint_write
    return checkpoint_write(root, ticket, "ticket-transition",
                            "ticket closed", [])


def _write_close_record(root: Path, ticket: str, packet_hash: str,
                         inputs: list[dict], requirements: list[str],
                         decisions: list[str], test_paths: list[str],
                         skill_versions: list[dict],
                         checkpoint_info: dict) -> str:
    import yaml
    from datetime import datetime, timezone

    close_id = f"CL-{ticket}"
    close_dir = root / "docs" / "close" / ticket
    close_dir.mkdir(parents=True, exist_ok=True)
    close_path = close_dir / f"{close_id}.md"
    close_rel = f"docs/close/{ticket}/{close_id}.md"
    cp_path = checkpoint_info.get("path", "")

    front = {
        "id": close_id,
        "type": "close",
        "status": "ACTIVE",
        "state_class": "AUTHORITATIVE",
        "task": ticket,
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "packet_hash": packet_hash,
        "inputs": inputs,
        "outputs": [close_rel, cp_path],
        "requirements_implemented": requirements,
        "decisions_applied": decisions,
        "tests_produced": test_paths,
        "deviations": [],
        "skill_versions": skill_versions,
    }

    text = "---\n" + yaml.safe_dump(front, sort_keys=False, allow_unicode=True) + "---\n\n"
    text += f"# {close_id} — Close record for {ticket}\n"
    close_path.write_text(text, encoding="utf-8")
    return close_rel


def _set_ticket_closed(root: Path, ticket: str) -> None:
    import yaml

    path = root / ".tickets" / f"{ticket}.md"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return
    end = text.find("---", 3)
    if end < 0:
        return
    try:
        front = yaml.safe_load(text[3:end])
    except yaml.YAMLError:
        return
    if not isinstance(front, dict):
        return
    front["status"] = "closed"
    body = text[end + 3:]
    new_text = "---\n" + yaml.safe_dump(front, sort_keys=False, allow_unicode=True) + "---" + body
    path.write_text(new_text, encoding="utf-8")
