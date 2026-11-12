"""Check runner (W1-26): load declarations, run checks, compute family statuses, record provenance."""
from __future__ import annotations

import functools
import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import yaml

from gov.cli.checks import CHECKS_DIRS, ENFORCES_FIELD, TIMEOUT_FIELD, load_declarations
from gov.util.frontmatter import quiet as _frontmatter
from gov.util.gitenv import git_env, program_env

VERSION = "1.0.0"

FAMILIES = (
    "schema/invariants",
    "graph integrity",
    "index freshness",
    "retrieval regression",
    "authority/role limits",
    "mutation scope",
    "path-map compliance",
    "context reproducibility",
    "concurrency/claims",
    "adapter/model portability",
    "skill regression",
    "command-contract consistency",
    "secrets indexing",
    "recovery/rebuild",
    "fresh-agent reconstruction",
    "product traceability",
    "audit reproducibility",
)

RED, YELLOW, GREEN = "RED", "YELLOW", "GREEN"
NA_FIELD = "allows-not-applicable"
EXIT_NOT_APPLICABLE = 2
TIMEOUT_S = 60  # the limit of a check whose declaration states none (DEC-595)
EXIT_TOOL_ABSENT = 127  # the shell's "command not found"; also what a command that cannot be started answers
STOP_GRACE_S = 5  # after the process group is killed, the time its pipes get to close before they are given up


def _normalise_family(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
HARD_BLOCK, WARNING = "hard-block", "warning"
PATH_MAP_REL = "governance/project/path-map.yaml"
SKILL_DIR = "template/governance/kernel/vendor"
READINESS_DIMENSIONS_REL = "docs/contract/readiness-dimensions.yaml"


def _head(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True, env=git_env(root, pinned=True),
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, OSError):
        return "unknown"


def _inputs_hash(check_id: str, commit: str) -> str:
    return hashlib.sha256(f"{check_id}:{commit}".encode()).hexdigest()[:16]


def _provenance(check_id: str, commit: str, version: str = VERSION) -> dict:
    return {
        "commit": commit,
        "check_version": version,
        "inputs_hash": _inputs_hash(check_id, commit),
    }


def _judged(command: str) -> str:
    """``command`` with a leading ``python3`` or ``gov`` run by this judge's own interpreter and package (DEC-822 item 3).

    The project under check supplies only data: nothing first on PATH runs, and ``-P`` keeps the project's root, the
    working folder, off the import path."""
    head, _, rest = command.strip().partition(" ")
    python = shlex.quote(sys.executable)
    if head == "python3":
        return f"{python} -P {rest}"
    if head == "gov":
        return f"{python} -P -m gov.cli.main {rest}"
    return command


def _run_command(command: str, root: Path, timeout: int = TIMEOUT_S) -> tuple[int | None, str, str]:
    """The exit code, output and error output of ``command``. The exit code is None when it passed ``timeout`` seconds."""
    command = _judged(command)
    env = program_env()  # a declared check may start git anywhere: no inherited GIT_* variable, no index (P-1)
    xdg_tmp = tempfile.mkdtemp(prefix="gov-check-")
    env.setdefault("XDG_CONFIG_HOME", xdg_tmp)
    env.setdefault("XDG_DATA_HOME", xdg_tmp)
    try:
        # its own session: on the limit the whole process group is stopped, so a grandchild that holds the
        # pipe cannot keep the runner waiting (W2-M151)
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            cwd=str(root), env=env, start_new_session=True,
        )
    except OSError as exc:
        shutil.rmtree(xdg_tmp, ignore_errors=True)
        return EXIT_TOOL_ABSENT, "", str(exc)  # it could not be started: absent, as the shell says it
    try:
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            return process.returncode, stdout, stderr
        except subprocess.TimeoutExpired:
            _stop(process)
            return None, "", ""  # what it printed before the limit is no answer
    finally:
        shutil.rmtree(xdg_tmp, ignore_errors=True)


def _stop(process: subprocess.Popen) -> None:
    """Stop ``process`` with every process of its group, then collect it and close its pipes."""
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        process.kill()
    try:
        process.communicate(timeout=STOP_GRACE_S)
    except subprocess.TimeoutExpired:  # a descendant that left the group still holds a pipe: it is let go
        for pipe in (process.stdout, process.stderr):
            if pipe is not None:
                pipe.close()
        process.wait()


def _augment_declarations(declarations: list[dict], root: Path) -> None:
    # both layouts of the kernel (DEC-579): the reader refuses one id declared differently in the two
    for decl in declarations:
        for checks_dir in CHECKS_DIRS:
            yaml_path = root / checks_dir / f"{decl['id']}.yaml"
            if not yaml_path.is_file():
                continue
            try:
                raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
            except (yaml.YAMLError, OSError):
                continue
            if isinstance(raw, dict) and raw.get(NA_FIELD) == "true":
                decl[NA_FIELD] = "true"


def _run_declared_check(decl: dict, root: Path, commit: str) -> dict:
    check_id = decl["id"]
    family = decl["family"]
    severity = decl["severity"]
    command = decl["command"]
    allows_na = decl.get(NA_FIELD) == "true"

    limit = decl.get(TIMEOUT_FIELD, TIMEOUT_S)
    started = time.monotonic()
    exit_code, stdout, stderr = _run_command(command, root, limit)
    times = {"elapsed_s": round(time.monotonic() - started, 3), "time_limit_s": limit}

    if exit_code == EXIT_NOT_APPLICABLE and allows_na and stdout.strip():
        try:
            parsed = json.loads(stdout)
            if isinstance(parsed, dict) and parsed.get("not_applicable") is True:
                return {
                    "id": check_id,
                    "family": family,
                    "severity": severity,
                    "status": YELLOW,
                    "reason": parsed.get("reason", ""),
                    "findings": [],
                    **times,
                    "provenance": _provenance(check_id, commit),
                }
        except json.JSONDecodeError:
            pass

    findings = []
    if exit_code is None:
        findings = [{"code": "CHECK_TIMED_OUT", "time_limit_s": limit,
                     "message": f"{check_id} did not end within its time limit of {limit} seconds"}]
    elif exit_code == EXIT_TOOL_ABSENT:
        tool = command.split()[0] if command.split() else command
        findings = [{"code": "CHECK_TOOL_ABSENT", "tool": tool,
                     "message": f"{check_id}: its command '{tool}' is not available (exit code {EXIT_TOOL_ABSENT})",
                     "stderr": stderr.strip()[:200] if stderr.strip() else None}]
    else:
        findings = _answered_findings(check_id, exit_code, stdout)
        if exit_code != 0 and not findings:
            findings = [{"code": "CHECK_FAILED", "message": f"{check_id} exited with code {exit_code}",
                         "stderr": stderr.strip()[:200] if stderr.strip() else None}]

    status = GREEN
    if findings:
        status = RED if severity == HARD_BLOCK else YELLOW

    return {
        "id": check_id,
        "family": family,
        "severity": severity,
        "status": status,
        "findings": findings,
        **times,
        "provenance": _provenance(check_id, commit),
    }


def _answered_findings(check_id: str, exit_code: int, stdout: str) -> list:
    """The findings in what a check printed. A check is green only when it exits 0 with none (W2-M129, W2-M212).

    With exit code 0 there is also a finding where its answer is the success form with findings in its result, where
    a JSON mapping in it (top level or ``result``) says ``"unmeasured": true``, and where output that is no JSON
    holds the word "unmeasured"."""
    if not stdout.strip():
        return []
    try:
        parsed = json.loads(stdout)
    except json.JSONDecodeError:
        if exit_code != 0:
            return [{"code": "CHECK_FAILED", "message": stdout.strip()[:200]}]
        return _unmeasured_text(check_id, stdout)
    if isinstance(parsed, list):
        return parsed
    if not isinstance(parsed, dict):  # a bare JSON value: it is read as the text it is
        return [] if exit_code != 0 else _unmeasured_text(check_id, stdout)
    result = parsed.get("result") if parsed.get("ok") is True and "result" in parsed else None
    success = exit_code == 0 and parsed.get("ok") is True and "result" in parsed
    if success:  # the success form of a gov command is no finding (DEC-612), but its result's findings are
        inner = result.get("findings") if isinstance(result, dict) else None
        findings = inner if isinstance(inner, list) else ([inner] if inner else [])
    else:
        findings = parsed.get("findings", [parsed])
        if exit_code == 0 and parsed.get("unmeasured") is True:
            findings = parsed["findings"] if isinstance(parsed.get("findings"), list) else []
    if exit_code == 0:
        for mapping in (parsed, result):
            if isinstance(mapping, dict) and mapping.get("unmeasured") is True:
                findings = [*findings, {"code": "CHECK_UNMEASURED", "message": f"{check_id} did not measure",
                                        "reason": mapping.get("reason", "")}]
                break
    return findings


def _unmeasured_text(check_id: str, stdout: str) -> list:
    """A finding for output that is no JSON and holds the word "unmeasured"; none otherwise."""
    if re.search(r"\bunmeasured\b", stdout, re.IGNORECASE):
        return [{"code": "CHECK_UNMEASURED", "message": f"{check_id} printed 'unmeasured': {stdout.strip()[:200]}"}]
    return []


def _timed(check):
    """``check`` with ``elapsed_s`` and ``time_limit_s`` (the runner's ``TIMEOUT_S``) added to its result (W2-M151)."""
    @functools.wraps(check)
    def timed(*args, **kwargs) -> dict:
        started = time.monotonic()
        result = check(*args, **kwargs)
        return {**result, "elapsed_s": round(time.monotonic() - started, 3), "time_limit_s": TIMEOUT_S}
    return timed


@_timed
def _check_openspec(root: Path, commit: str) -> dict:
    check_id = "openspec-validate"
    findings = []
    has_openspec = shutil.which("openspec") is not None
    exit_code = stdout = stderr = None
    if has_openspec:
        exit_code, stdout, stderr = _run_command("openspec validate --strict", root)
        has_openspec = exit_code != EXIT_TOOL_ABSENT  # found on PATH and not startable: absent all the same
    if has_openspec:
        combined = (stdout + stderr).lower()
        if exit_code != 0 and "nothing to validate" not in combined:
            findings = [{"code": "OPENSPEC_FAILED", "message": stdout.strip()[:200] or stderr.strip()[:200]}]
            status = RED
        elif exit_code != 0:
            findings = [{"code": "OPENSPEC_NO_SPECS", "message": "openspec: nothing to validate"}]
            status = YELLOW
        else:
            status = GREEN
    else:
        findings = [{"code": "OPENSPEC_ABSENT", "message": "openspec is not on PATH"}]
        status = RED  # a hard-block check whose tool is absent is not measured: never YELLOW (W2-M130, W2-M265)

    return {
        "id": check_id,
        "family": "product traceability",
        "severity": HARD_BLOCK,
        "status": status,
        "findings": findings,
        "provenance": _provenance(check_id, commit),
    }


@_timed
def _check_skill_version(root: Path, commit: str) -> dict:
    check_id = "skill-version"
    findings = []
    skill_dir = root / SKILL_DIR
    if skill_dir.is_dir():
        try:
            diff_result = subprocess.run(
                ["git", "-C", str(root), "diff", "HEAD~1", "--name-only", "--", SKILL_DIR],
                capture_output=True, text=True, env=git_env(root, pinned=True),
            )
            if diff_result.returncode == 0 and diff_result.stdout.strip():
                changed_files = [f for f in diff_result.stdout.strip().split("\n") if f]
                for rel in changed_files:
                    full = root / rel
                    if not full.is_file():
                        continue
                    text = full.read_text(encoding="utf-8")
                    front = _frontmatter(text)
                    if front is None:
                        continue

                    old_result = subprocess.run(
                        ["git", "-C", str(root), "show", f"HEAD~1:{rel}"],
                        capture_output=True, text=True, env=git_env(root, pinned=True),
                    )
                    if old_result.returncode != 0:
                        continue
                    old_front = _frontmatter(old_result.stdout)
                    if old_front is None:
                        continue

                    old_version = str(old_front.get("version", ""))
                    new_version = str(front.get("version", ""))
                    old_content = old_result.stdout
                    new_content = text

                    if old_content != new_content and old_version == new_version:
                        findings.append({
                            "code": "SKILL_CONTENT_CHANGED_VERSION_UNCHANGED",
                            "path": rel,
                            "message": f"{rel}: content changed but version is still {new_version}",
                        })
                    elif old_content != new_content and old_version != new_version:
                        decisions_dir = root / "docs" / "adr"
                        has_decision = False
                        if decisions_dir.is_dir():
                            for md in decisions_dir.rglob("*.md"):
                                try:
                                    dec_front = _frontmatter(md.read_text(encoding="utf-8"))
                                except OSError:
                                    continue
                                if dec_front and dec_front.get("status") == "ACTIVE":
                                    has_decision = True
                                    break
                        if not has_decision:
                            findings.append({
                                "code": "SKILL_VERSION_CHANGED_NO_DECISION",
                                "path": rel,
                                "message": f"{rel}: version changed from {old_version} to {new_version} without a linked decision",
                            })
        except (subprocess.CalledProcessError, OSError):
            pass

    status = RED if findings else GREEN
    return {
        "id": check_id,
        "family": "skill regression",
        "severity": HARD_BLOCK,
        "status": status,
        "findings": findings,
        "provenance": _provenance(check_id, commit),
    }


@_timed
def _check_readiness(root: Path, commit: str) -> dict:
    check_id = "readiness"
    findings = []
    try:
        from gov.readiness.checker import check_all
        result = check_all(root)
        if isinstance(result, dict) and not result.get("closed", True):
            specs = result.get("specifications", [])
            if specs:
                for spec in specs:
                    if isinstance(spec, dict) and not spec.get("closed", True):
                        findings.append({"code": "READINESS_NOT_CLOSED",
                                         "message": f"specification {spec.get('specification', '?')} not closed"})
            if not findings:
                findings.append({"code": "READINESS_NOT_CLOSED",
                                 "message": "readiness check_all returned closed=False"})
    except Exception as exc:
        code = getattr(exc, "code", "READINESS_ERROR")
        msg = getattr(exc, "message", str(exc))
        findings.append({"code": code, "message": msg})

    status = RED if findings else GREEN
    return {
        "id": check_id,
        "family": "product traceability",
        "severity": HARD_BLOCK,
        "status": status,
        "findings": findings,
        "provenance": _provenance(check_id, commit),
    }


def _check_policy_enforcement(root: Path, commit: str, check_families: set[str]) -> list[dict]:
    # a key is covered by a declaration that states it under ``enforces`` and by nothing else: a family
    # name that contains the key covers nothing (DEC-620), so ``check_families`` is not read
    results = []
    path_map = root / PATH_MAP_REL
    if not path_map.is_file():
        return results
    try:
        data = yaml.safe_load(path_map.read_text(encoding="utf-8"))
    except (yaml.YAMLError, OSError):
        return results
    if not isinstance(data, dict):
        return results

    policies = data.get("policies", {})
    if not isinstance(policies, dict):
        return results

    covering: dict[str, list[dict]] = {}  # the declarations that state each key under ``enforces``
    for decl in load_declarations(root):
        for key in decl.get(ENFORCES_FIELD, ()):
            covering.setdefault(key, []).append(decl)
    for key, strength in policies.items():
        if strength == "informational":
            continue
        started = time.monotonic()
        covers = covering.get(key, [])
        severity = HARD_BLOCK if strength == "hard-block" else WARNING
        finding = None
        if not covers:
            finding = {"code": "POLICY_NOT_COVERED", "policy": key, "strength": strength,
                       "message": f"policy key '{key}' ({strength}) has no associated check"}
        elif strength == "hard-block" and all(decl["severity"] != HARD_BLOCK for decl in covers):
            # a hard-block key is covered only by a check of hard-block tier, its ``severity`` (W2-M211, W2-M259)
            ids = [decl["id"] for decl in covers]
            finding = {"code": "POLICY_TIER_TOO_LOW", "policy": key, "checks": ids,
                       "message": f"policy key '{key}' (hard-block) is covered only by checks of severity "
                                  f"warning: {', '.join(ids)}"}
        if finding is not None:
            results.append({
                "id": f"policy-{key}",
                "family": key,
                "severity": severity,
                "status": RED if severity == HARD_BLOCK else YELLOW,
                "findings": [finding],
                "elapsed_s": round(time.monotonic() - started, 3),
                "time_limit_s": TIMEOUT_S,
                "provenance": _provenance(f"policy-{key}", commit),
            })
    return results


def run_checks(root: Path) -> tuple[dict, bool]:
    root = Path(root)
    commit = _head(root)
    declarations = load_declarations(root)
    _augment_declarations(declarations, root)

    check_results = []
    for decl in declarations:
        check_results.append(_run_declared_check(decl, root, commit))

    check_results.append(_check_openspec(root, commit))
    check_results.append(_check_skill_version(root, commit))
    check_results.append(_check_readiness(root, commit))

    families: dict[str, dict] = {}
    normalised_to_canonical: dict[str, str] = {}
    for family in FAMILIES:
        families[family] = {"status": GREEN, "family": family}
        normalised_to_canonical[_normalise_family(family)] = family

    for entry in check_results:
        fam = entry.get("family", "")
        norm = _normalise_family(fam)
        canonical = normalised_to_canonical.get(norm)
        if canonical is None:
            if fam not in families:
                families[fam] = {"status": RED, "family": fam}
            canonical = fam
        current = families[canonical]["status"]
        entry_status = entry.get("status", GREEN)
        if entry_status == RED:
            families[canonical]["status"] = RED
            families[canonical].pop("reason", None)
        elif entry_status == YELLOW and current != RED:
            families[canonical]["status"] = YELLOW
            if entry.get("reason"):
                families[canonical]["reason"] = entry["reason"]

    check_families = set(families.keys())
    policy_results = _check_policy_enforcement(root, commit, check_families)
    for entry in policy_results:
        fam = entry.get("family", "")
        if fam not in families:
            families[fam] = {"status": entry.get("status", GREEN), "family": fam}
        else:
            current = families[fam]["status"]
            entry_status = entry.get("status", GREEN)
            if entry_status == RED:
                families[fam]["status"] = RED
            elif entry_status == YELLOW and current != RED:
                families[fam]["status"] = YELLOW
    check_results.extend(policy_results)

    for family in families:
        norm = _normalise_family(family)
        count = sum(
            1 for cr in check_results
            if _normalise_family(cr.get("family", "")) == norm
        )
        families[family]["check_count"] = count
        if count == 0 and families[family]["status"] == GREEN:
            families[family]["status"] = YELLOW
            families[family]["reason"] = "no registered check"

    has_hard_block_red = any(
        fam.get("status") == RED
        for fam in families.values()
    )

    result = {
        "families": families,
        "checks": check_results,
        "time_limit_s": TIMEOUT_S,
    }

    return result, has_hard_block_red
