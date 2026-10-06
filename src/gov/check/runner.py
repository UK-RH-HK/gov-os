"""Check runner (W1-26): load declarations, run checks, compute family statuses, record provenance."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import yaml

from gov.cli.checks import load_declarations

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
            capture_output=True, text=True, check=True,
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


def _run_command(command: str, root: Path) -> tuple[int, str, str]:
    env = dict(os.environ)
    pythonpath = env.get("PYTHONPATH", "")
    src = str(root / "src")
    if src not in pythonpath:
        env["PYTHONPATH"] = src + (":" + pythonpath if pythonpath else "")
    xdg_tmp = tempfile.mkdtemp(prefix="gov-check-")
    env.setdefault("XDG_CONFIG_HOME", xdg_tmp)
    env.setdefault("XDG_DATA_HOME", xdg_tmp)
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            cwd=str(root), env=env, timeout=60,
        )
        return result.returncode, result.stdout, result.stderr
    except (subprocess.TimeoutExpired, OSError) as exc:
        return 1, "", str(exc)
    finally:
        shutil.rmtree(xdg_tmp, ignore_errors=True)


def _run_declared_check(decl: dict, root: Path, commit: str) -> dict:
    check_id = decl["id"]
    family = decl["family"]
    severity = decl["severity"]
    command = decl["command"]

    exit_code, stdout, stderr = _run_command(command, root)
    findings = []
    if stdout.strip():
        try:
            parsed = json.loads(stdout)
            if isinstance(parsed, list):
                findings = parsed
            elif isinstance(parsed, dict):
                findings = parsed.get("findings", [parsed])
        except json.JSONDecodeError:
            if exit_code != 0:
                findings = [{"code": "CHECK_FAILED", "message": stdout.strip()[:200]}]

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
        "provenance": _provenance(check_id, commit),
    }


def _check_openspec(root: Path, commit: str) -> dict:
    check_id = "openspec-validate"
    findings = []
    has_openspec = shutil.which("openspec") is not None
    if has_openspec:
        exit_code, stdout, stderr = _run_command("openspec validate --strict", root)
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
        status = YELLOW

    return {
        "id": check_id,
        "family": "product traceability",
        "severity": HARD_BLOCK,
        "status": status,
        "findings": findings,
        "provenance": _provenance(check_id, commit),
    }


def _frontmatter(text: str) -> dict | None:
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = lines.index("---", 1)
    except ValueError:
        return None
    try:
        front = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError:
        return None
    return front if isinstance(front, dict) else None


def _check_skill_version(root: Path, commit: str) -> dict:
    check_id = "skill-version"
    findings = []
    skill_dir = root / SKILL_DIR
    if skill_dir.is_dir():
        try:
            diff_result = subprocess.run(
                ["git", "-C", str(root), "diff", "HEAD~1", "--name-only", "--", SKILL_DIR],
                capture_output=True, text=True,
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
                        capture_output=True, text=True,
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

    for key, strength in policies.items():
        if strength == "informational":
            continue
        covered = key in check_families or any(key in fam for fam in check_families)
        if not covered:
            severity = HARD_BLOCK if strength == "hard-block" else WARNING
            results.append({
                "id": f"policy-{key}",
                "family": key,
                "severity": severity,
                "status": RED if severity == HARD_BLOCK else YELLOW,
                "findings": [{"code": "POLICY_NOT_COVERED",
                              "policy": key, "strength": strength,
                              "message": f"policy key '{key}' ({strength}) has no associated check"}],
                "provenance": _provenance(f"policy-{key}", commit),
            })
    return results


def run_checks(root: Path) -> tuple[dict, bool]:
    root = Path(root)
    commit = _head(root)
    declarations = load_declarations(root)

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
        elif entry_status == YELLOW and current != RED:
            families[canonical]["status"] = YELLOW

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
    }

    return result, has_hard_block_red
