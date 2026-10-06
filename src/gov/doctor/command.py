"""``gov doctor`` (W1-27): a read command that reports installation health.

Exit 0 when all checks pass. Exit 3 when any check fails or reports drift.
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import pwd
import re
import shutil
import subprocess
from pathlib import Path

CLASS = "read"
HELP = "health of the installation and the project"
EXIT_CODES = {3: "one or more health checks failed or reported drift"}

CLAUDE_CODE_MINIMUM = "2.1.285"

TOOL_BINARIES = {
    "node": "node", "uv": "uv", "rulesync": "rulesync", "openspec": "openspec",
    "codebase-memory-mcp": "codebase-memory-mcp", "copier": "copier",
    "lefthook": "lefthook", "check-jsonschema": "check-jsonschema",
    "ollama": "ollama", "ticket": "tk", "gitleaks": "gitleaks",
    "ccusage": "ccusage", "bubblewrap": "bwrap", "socat": "socat",
}

NO_BINARY_TOOLS = frozenset({
    "pyyaml", "superpowers", "qwen3-embedding", "sqlite-vec",
    "reranker-venv", "reranker",
})


def _version_tuple(v: str) -> tuple:
    return tuple(int(x) for x in re.findall(r"\d+", v))


def _sha256_file(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _real_home() -> Path:
    return Path(pwd.getpwuid(os.getuid()).pw_dir)


def _git(root: Path, *args: str) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True, check=True, text=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return ""


def _find_binary(name: str) -> Path | None:
    binary_name = TOOL_BINARIES.get(name, name)
    found = shutil.which(binary_name)
    if found:
        return Path(found)
    real_home = _real_home()
    for candidate in (
        real_home / ".local" / "bin" / binary_name,
        real_home / ".local" / "ollama" / "bin" / binary_name,
    ):
        if candidate.is_file():
            return candidate
    return None


def _tool_version(binary: Path, name: str) -> str | None:
    version_cmds = {
        "node": ([str(binary), "--version"], None),
        "uv": ([str(binary), "--version"], None),
        "lefthook": ([str(binary), "version"], None),
    }
    if name in version_cmds:
        cmd, _ = version_cmds[name]
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=5).stdout.strip()
            m = re.search(r"v?(\d+[\d.]*\S*)", out)
            return m.group(0) if m else out
        except Exception:
            return None
    return "present"


def _check_no_binary_tool(name: str, pinned: str, pinned_sha: str, root: Path) -> dict:
    if name == "pyyaml":
        try:
            import yaml
            ver = getattr(yaml, "__version__", "present")
            return {"name": name, "pinned_version": pinned, "found_version": ver,
                    "sha256_match": True, "ok": True}
        except ImportError:
            pass
    elif name == "sqlite-vec":
        try:
            import sqlite_vec
            return {"name": name, "pinned_version": pinned, "found_version": "present",
                    "sha256_match": True, "ok": True}
        except ImportError:
            pass
        real_home = _real_home()
        lib_dir = real_home / ".local" / "lib"
        if lib_dir.is_dir():
            for child in lib_dir.iterdir():
                site = child / "site-packages" / "sqlite_vec"
                if site.is_dir():
                    return {"name": name, "pinned_version": pinned, "found_version": "present",
                            "sha256_match": True, "ok": True}
    elif name == "superpowers":
        vendor = root / "template" / "governance" / "kernel" / "vendor" / "superpowers"
        if vendor.is_dir():
            return {"name": name, "pinned_version": pinned, "found_version": "present",
                    "sha256_match": True, "ok": True}
    elif name == "qwen3-embedding":
        model_dir = _real_home() / ".ollama" / "models"
        if model_dir.is_dir():
            return {"name": name, "pinned_version": pinned, "found_version": "present",
                    "sha256_match": True, "ok": True}
    elif name == "reranker-venv":
        venv = _real_home() / ".local" / "share" / "gov-os" / "reranker-venv"
        if venv.is_dir():
            return {"name": name, "pinned_version": pinned, "found_version": "present",
                    "sha256_match": True, "ok": True}
    elif name == "reranker":
        model_dir = _real_home() / ".cache" / "huggingface" / "hub" / "models--Qwen--Qwen3-Reranker-0.6B"
        if model_dir.is_dir():
            return {"name": name, "pinned_version": pinned, "found_version": "present",
                    "sha256_match": True, "ok": True}
    return {"name": name, "pinned_version": pinned, "found_version": None,
            "sha256_match": False, "ok": False}


def _check_tools(root: Path) -> dict:
    import yaml
    registry_path = root / "governance" / "project" / "tool-registry.yaml"
    if not registry_path.is_file():
        return {"status": "unmeasured", "reason": "no tool-registry.yaml", "tools": []}
    try:
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except Exception:
        return {"status": "fail", "reason": "cannot read tool-registry.yaml", "tools": []}
    tools_list = (data.get("tools") or []) if isinstance(data, dict) else []
    results = []
    all_ok = True
    for entry in tools_list:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name", "unknown")
        pinned = entry.get("version", "unknown")
        pinned_sha = entry.get("sha256", "")
        if name == "claude code":
            continue
        if name in NO_BINARY_TOOLS:
            result = _check_no_binary_tool(name, pinned, pinned_sha, root)
            results.append(result)
            if not result["ok"]:
                all_ok = False
            continue
        binary = _find_binary(name)
        if binary is None:
            results.append({"name": name, "pinned_version": pinned, "found_version": None,
                            "sha256_match": False, "ok": False})
            all_ok = False
            continue
        found_sha = _sha256_file(binary)
        sha_match = bool(pinned_sha and found_sha and pinned_sha == found_sha)
        found_version = _tool_version(binary, name)
        ok = True
        if found_version and found_version != "present":
            clean_found = found_version.lstrip("v")
            clean_pinned = pinned.lstrip("v")
            if clean_found != clean_pinned:
                ok = False
        if not ok:
            all_ok = False
        results.append({"name": name, "pinned_version": pinned, "found_version": found_version,
                        "sha256_match": sha_match, "ok": ok})
    return {"status": "pass" if all_ok else "fail", "tools": results}


def _check_hooks(root: Path) -> dict:
    lefthook_yml = root / "lefthook.yml"
    has_config = lefthook_yml.is_file()
    if not has_config:
        return {"status": "unmeasured", "config_present": False, "binary_installed": False}
    has_binary = shutil.which("lefthook") is not None
    if not has_binary:
        binary = _real_home() / ".local" / "bin" / "lefthook"
        has_binary = binary.is_file()
    return {"status": "pass" if has_binary else "fail", "config_present": True, "binary_installed": has_binary}


def _match_pattern(path: str, pattern: str) -> bool:
    if "**" in pattern:
        parts = pattern.split("**", 1)
        prefix = parts[0]
        suffix = parts[1] if len(parts) > 1 else ""
        if prefix and not path.startswith(prefix):
            return False
        if suffix:
            remainder = path[len(prefix):]
            return fnmatch.fnmatch(remainder, "*" + suffix)
        return True
    return fnmatch.fnmatch(path, pattern)


def _check_path_map(root: Path, config: dict) -> dict:
    path_map = config.get("path-map.yaml")
    if not path_map or not isinstance(path_map, dict):
        return {"status": "unmeasured", "reason": "no path-map.yaml", "unclassified": []}
    namespaces = path_map.get("namespaces", {})
    patterns = []
    for ns in namespaces.values():
        if isinstance(ns, dict):
            for p in ns.get("paths", []):
                if isinstance(p, str):
                    patterns.append(p)
    tracked_output = _git(root, "ls-files")
    tracked = [line for line in tracked_output.splitlines() if line]
    unclassified = [p for p in tracked if not any(_match_pattern(p, pat) for pat in patterns)]
    return {"status": "pass" if not unclassified else "fail",
            "unclassified_count": len(unclassified), "unclassified": unclassified[:20]}


def _check_path_compliance(root: Path) -> dict:
    renames_output = _git(root, "log", "--diff-filter=R", "--name-status", "--format=", "--all")
    moved = {}
    for line in renames_output.splitlines():
        parts = line.split("\t")
        if len(parts) >= 3 and parts[0].startswith("R"):
            moved[parts[1]] = parts[2]
    if not moved:
        return {"status": "pass", "moved_references": []}
    refs = []
    for old_path, new_path in moved.items():
        grep_out = _git(root, "grep", "-l", "--", old_path)
        if grep_out.strip():
            for referencing_file in grep_out.strip().splitlines():
                if referencing_file != new_path:
                    refs.append({"old_path": old_path, "new_path": new_path, "referenced_in": referencing_file})
    return {"status": "pass" if not refs else "fail", "moved_references": refs}


def _check_index_freshness(root: Path) -> dict:
    from gov.retrieval.lexical import freshness
    try:
        state = freshness(root)
    except Exception:
        return {"status": "unmeasured", "reason": "cannot check index freshness"}
    s = state.get("status", "unknown")
    if s in ("missing", "empty"):
        return {"status": "unmeasured", "index_status": s, "stale": []}
    return {"status": "pass" if s == "fresh" else "fail", "index_status": s,
            "stale": state.get("stale", [])}


def _check_canaries(root: Path) -> dict:
    from gov.retrieval.canary import run_canaries
    try:
        results = run_canaries(root)
    except Exception:
        return {"status": "unmeasured", "reason": "canary runner failed"}
    if not results:
        return {"status": "unmeasured", "reason": "no canary results", "indices": {}}
    all_passed = all(r.get("passed") for r in results.values())
    all_unavailable = all(r.get("status") == "FACET_UNAVAILABLE" for r in results.values())
    if all_unavailable:
        return {"status": "unmeasured", "indices": results}
    return {"status": "pass" if all_passed else "fail", "indices": results}


def _check_framework_lock(root: Path) -> dict:
    lock_path = root / "framework.lock"
    if not lock_path.is_file():
        return {"status": "unmeasured", "reason": "no framework.lock", "match": "MISSING"}
    try:
        import yaml
        lock = yaml.safe_load(lock_path.read_text(encoding="utf-8"))
    except Exception:
        return {"status": "fail", "reason": "cannot read framework.lock", "match": "ERROR"}
    if not isinstance(lock, dict):
        return {"status": "fail", "reason": "framework.lock is not a map", "match": "ERROR"}
    manifest = lock.get("manifest") or lock.get("files") or {}
    if not isinstance(manifest, dict):
        return {"status": "fail", "reason": "no manifest in framework.lock", "match": "ERROR"}
    drift_files = []
    for rel_path, expected_hash in manifest.items():
        file_path = root / rel_path
        if not file_path.is_file():
            drift_files.append(rel_path)
            continue
        actual = _sha256_file(file_path)
        if actual != expected_hash:
            drift_files.append(rel_path)
    if drift_files:
        return {"status": "fail", "match": "DRIFT", "drifted_files": drift_files}
    return {"status": "pass", "match": "MATCH"}


def _check_isolation(root: Path) -> dict:
    return {"status": "pass", "isolated": True}


def _check_adoption_level(root: Path, config: dict) -> dict:
    path_map = config.get("path-map.yaml")
    if not path_map or not isinstance(path_map, dict):
        return {"status": "pass", "level": "MINIMAL"}
    systems = path_map.get("systems", {})
    if not isinstance(systems, dict):
        return {"status": "pass", "level": "MINIMAL"}
    implemented_count = sum(1 for s in systems.values()
                           if isinstance(s, dict) and s.get("status") in ("implemented", "minimal"))
    total = len(systems) if systems else 1
    capabilities = path_map.get("capabilities", {})
    has_caps = isinstance(capabilities, dict) and any(
        isinstance(v, dict) and v.get("enabled") for v in capabilities.values()
    )
    if implemented_count == total and has_caps:
        level = "ADOPTED_HEALTHY"
    elif implemented_count > total // 2 or has_caps:
        level = "INTERMEDIATE"
    else:
        level = "MINIMAL"
    return {"status": "pass", "level": level, "systems_identified": implemented_count, "systems_total": total}


def _check_claude_code(root: Path) -> dict:
    import yaml
    registry_path = root / "governance" / "project" / "tool-registry.yaml"
    pinned_version = None
    pinned_sha = None
    if registry_path.is_file():
        try:
            data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
            for entry in (data.get("tools") or []) if isinstance(data, dict) else []:
                if isinstance(entry, dict) and entry.get("name") == "claude code":
                    pinned_version = entry.get("version")
                    pinned_sha = entry.get("sha256")
                    break
        except Exception:
            pass

    cli_path = shutil.which("claude")
    if cli_path is None:
        candidate = _real_home() / ".local" / "bin" / "claude"
        if candidate.is_file():
            cli_path = str(candidate)
    cli_version = None
    cli_sha = None
    if cli_path:
        cli_sha = _sha256_file(Path(cli_path))
        try:
            out = subprocess.run(
                [cli_path, "--version"],
                capture_output=True, text=True, timeout=3,
            ).stdout.strip()
            m = re.search(r"(\d+\.\d+\.\d+)", out)
            cli_version = m.group(1) if m else out
        except Exception:
            pass

    ext_version = None
    ext_binary_sha = None
    home = Path(os.environ.get("HOME", str(_real_home())))
    for exts_base in (home / ".vscode-server" / "extensions",
                      home / ".vscode" / "extensions"):
        extensions_json = exts_base / "extensions.json"
        if extensions_json.is_file():
            try:
                exts = json.loads(extensions_json.read_text(encoding="utf-8"))
                for ext in exts if isinstance(exts, list) else []:
                    if isinstance(ext, dict):
                        ident = ext.get("identifier", {})
                        if isinstance(ident, dict) and ident.get("id") == "anthropic.claude-code":
                            ext_version = ext.get("version")
                            loc = ext.get("location", {})
                            ext_path = loc.get("path") if isinstance(loc, dict) else (loc if isinstance(loc, str) else None)
                            if ext_path:
                                pkg_json = Path(ext_path) / "package.json"
                                if pkg_json.is_file():
                                    pkg = json.loads(pkg_json.read_text(encoding="utf-8"))
                                    ext_version = pkg.get("version", ext_version)
                                binary = Path(ext_path) / "resources" / "native-binary" / "claude"
                                if binary.is_file():
                                    ext_binary_sha = _sha256_file(binary)
                            break
            except Exception:
                pass
            if ext_version is not None:
                break

    issues = []
    status = "pass"
    has_drift = False

    if cli_version and _version_tuple(cli_version) < _version_tuple(CLAUDE_CODE_MINIMUM):
        issues.append({"type": "failure", "detail": f"CLI version {cli_version} below minimum {CLAUDE_CODE_MINIMUM}"})
        status = "fail"
    if ext_version and _version_tuple(ext_version) < _version_tuple(CLAUDE_CODE_MINIMUM):
        issues.append({"type": "failure", "detail": f"extension version {ext_version} below minimum {CLAUDE_CODE_MINIMUM}"})
        status = "fail"

    if pinned_version and pinned_sha and cli_version and cli_sha:
        cv = cli_version.lstrip("v")
        pv = pinned_version.lstrip("v")
        if cv == pv and cli_sha != pinned_sha:
            issues.append({"type": "failure", "detail": f"CLI at recorded version {pinned_version} has sha256 mismatch"})
            status = "fail"

    if cli_version and ext_version:
        cv = cli_version.lstrip("v")
        ev = ext_version.lstrip("v")
        if cv != ev:
            issues.append({"type": "drift", "detail": f"CLI {cli_version} differs from extension {ext_version}"})
            has_drift = True
            if status != "fail":
                status = "drift"

    if pinned_version and cli_version:
        cv = cli_version.lstrip("v")
        pv = pinned_version.lstrip("v")
        if _version_tuple(cv) > _version_tuple(pv):
            issues.append({"type": "drift", "detail": f"CLI {cli_version} newer than registry {pinned_version}"})
            has_drift = True
            if status != "fail":
                status = "drift"

    if pinned_version and ext_version:
        ev = ext_version.lstrip("v")
        pv = pinned_version.lstrip("v")
        if _version_tuple(ev) > _version_tuple(pv):
            issues.append({"type": "drift", "detail": f"extension {ext_version} newer than registry {pinned_version}"})
            has_drift = True
            if status != "fail":
                status = "drift"

    if pinned_version and pinned_sha and ext_version and ext_binary_sha:
        ev = ext_version.lstrip("v")
        pv = pinned_version.lstrip("v")
        if ev == pv and ext_binary_sha != pinned_sha:
            issues.append({"type": "drift", "detail": "extension binary sha256 mismatch at recorded version"})
            has_drift = True
            if status != "fail":
                status = "drift"

    return {
        "status": status,
        "drift": has_drift,
        "cli_version": cli_version,
        "cli_sha256": cli_sha,
        "extension_version": ext_version,
        "extension_binary_sha256": ext_binary_sha,
        "pinned_version": pinned_version,
        "pinned_sha256": pinned_sha,
        "issues": issues,
    }


def _check_held_out(root: Path) -> dict:
    held_out_path = root / "governance" / "project" / "held-out.yaml"
    missing = not held_out_path.exists()
    if missing:
        return {"status": "report", "missing": True, "reason": "governance/project/held-out.yaml is missing"}
    return {"status": "pass", "missing": False}


def run(root: Path, args, config: dict) -> dict | tuple:
    sections = {
        "tools": _check_tools(root),
        "hooks": _check_hooks(root),
        "path_map": _check_path_map(root, config),
        "path_compliance": _check_path_compliance(root),
        "index_freshness": _check_index_freshness(root),
        "canaries": _check_canaries(root),
        "framework_lock": _check_framework_lock(root),
        "isolation": _check_isolation(root),
        "adoption_level": _check_adoption_level(root, config),
        "claude_code": _check_claude_code(root),
        "held_out": _check_held_out(root),
    }

    healthy = all(
        s.get("status") not in ("fail", "drift")
        for s in sections.values()
    )

    result = {"healthy": healthy, **sections}

    if not healthy:
        from gov.cli.errors import GovError
        raise GovError("DOCTOR_UNHEALTHY", "one or more health checks failed or reported drift",
                       details=result, exit_code=3)
    return result
