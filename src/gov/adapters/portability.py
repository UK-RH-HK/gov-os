"""Adapter/model-portability check (CAP-38.b): the kernel, the rulesync sources and the generated adapters agree.

Three comparisons, each a finding when it fails or cannot be made:
1. the installed rulesync with the version the project's tool registry expects (DEC-127);
2. each kernel role and kernel skill file with its source under ``.rulesync/``;
3. the generated files with what rulesync generates from the sources, read from the structured
   answer of ``rulesync --json generate --dry-run`` (``data.hasDiff``, ``data.features.*.paths``).

Prints ``{"findings": [...], "compared": {...}}`` and exits 0 only without findings.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

REGISTRY = "governance/project/tool-registry.yaml"
KERNEL_ROOTS = ("governance/kernel", "template/governance/kernel")  # adopted project, this repository
SOURCES = ".rulesync"
GENERATE = ("--json", "generate", "--dry-run", "--targets", "claudecode,agentsmd",
            "--features", "rules,hooks,permissions,subagents,commands,skills")
TIME_LIMIT = 10  # seconds, for each of the two rulesync calls


def _finding(code: str, message: str, file: str | None = None) -> dict:
    return {"code": code, "message": message, **({"file": file} if file else {})}


def _expected_version(root: Path) -> tuple[str | None, str]:
    """The rulesync version the tool registry records, or ``(None, reason)``."""
    try:
        data = yaml.safe_load((root / REGISTRY).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        return None, f"{REGISTRY} cannot be read ({type(exc).__name__})"
    tools = data.get("tools") if isinstance(data, dict) else None
    for entry in tools if isinstance(tools, list) else []:
        if isinstance(entry, dict) and entry.get("name") == "rulesync" and entry.get("version"):
            return str(entry["version"]), ""
    return None, f"{REGISTRY} has no rulesync entry with a version"


def _find_rulesync() -> str | None:
    explicit = os.environ.get("RULESYNC_BIN")
    if explicit:
        return explicit if os.path.isfile(explicit) else None
    return shutil.which("rulesync")


def _run(binary: str, *args: str, cwd: Path) -> tuple[int | None, str, str]:
    """``(exit code, stdout, stderr)``; the exit code is None when rulesync gave no answer. stdout goes
    through a file: the JSON answer is about 1 MB and was seen cut short when read through a pipe."""
    with tempfile.TemporaryFile("w+", encoding="utf-8") as out:
        try:
            done = subprocess.run([binary, *args], stdout=out, stderr=subprocess.PIPE, text=True,
                                  cwd=str(cwd), timeout=TIME_LIMIT, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            return None, "", f"no answer within {TIME_LIMIT} seconds"
        except OSError as exc:
            return None, "", str(exc)
        out.seek(0)
        return done.returncode, out.read(), done.stderr


def _version_finding(root: Path, binary: str | None) -> dict | None:
    """Comparison 1. None only when the installed version is the expected one."""
    expected, reason = _expected_version(root)
    if expected is None:
        return _finding("RULESYNC_VERSION_UNKNOWN", f"{reason}: the expected rulesync version is not known")
    if binary is None:
        return _finding("RULESYNC_ABSENT", f"rulesync not found (expected version {expected})")
    code, out, err = _run(binary, "--version", cwd=root)
    if code != 0:
        return _finding("RULESYNC_FAILED", f"rulesync --version: {(err or out).strip() or f'exit {code}'}")
    if out.strip() != expected:
        return _finding("RULESYNC_VERSION_DIFFERS",
                        f"installed rulesync is {out.strip()}, {REGISTRY} expects {expected}")
    return None


def _split(path: Path) -> tuple[object, str]:
    """``(frontmatter, body)`` of a Markdown file. The blank lines between the frontmatter and the
    first line of the body are dropped: rulesync drops them, and it is the one tolerated difference."""
    text = path.read_text(encoding="utf-8")
    end = text.find("\n---", 3) if text.startswith("---") else -1
    if end < 0:
        return None, text.lstrip("\n")
    try:
        front = yaml.safe_load(text[3:end])
    except yaml.YAMLError:
        front = text[3:end]
    return front, text[end + 4:].partition("\n")[2].lstrip("\n")


def _kernel_findings(root: Path) -> tuple[list[dict], int]:
    """Comparison 2, both ways: ``(findings, number of kernel files compared)``. A role is compared by
    body (its source's frontmatter is rulesync's own), a SKILL.md by body and frontmatter, any other
    file of a skill folder by bytes. Each finding names the rulesync source."""
    kernel = next((root / rel for rel in KERNEL_ROOTS if (root / rel).is_dir()), None)
    if kernel is None:
        return [_finding("KERNEL_ABSENT", f"no kernel folder ({' or '.join(KERNEL_ROOTS)})")], 0
    sources = root / SOURCES
    pairs = [(role, sources / "subagents" / role.name) for role in sorted((kernel / "roles").glob("*.md"))]
    held = sorted((sources / "subagents").glob("*.md"))
    for skill in sorted(path.parent for path in (kernel / "skills").rglob("SKILL.md")):
        files = sorted(path for path in skill.rglob("*") if path.is_file())
        pairs += [(path, sources / "skills" / skill.name / path.relative_to(skill)) for path in files]
        held += sorted(path for path in (sources / "skills" / skill.name).rglob("*") if path.is_file())
    if not pairs:
        return [_finding("KERNEL_EMPTY", f"{kernel.relative_to(root)} holds no role and no skill")], 0

    findings = []
    for kernel_file, source in pairs:
        rel, origin = str(source.relative_to(root)), str(kernel_file.relative_to(root))
        if not source.is_file():
            findings.append(_finding("SOURCE_MISSING", f"no rulesync source for {origin}", rel))
            continue
        if kernel_file.parent.name == "roles":
            same = _split(kernel_file)[1] == _split(source)[1]
        elif kernel_file.name == "SKILL.md":
            same = _split(kernel_file) == _split(source)
        else:
            same = kernel_file.read_bytes() == source.read_bytes()
        if not same:
            findings.append(_finding("SOURCE_DIFFERS", f"differs from {origin}", rel))
    expected = {source for _kernel_file, source in pairs}
    findings += [_finding("SOURCE_WITHOUT_KERNEL", "rulesync source with no kernel file",
                          str(path.relative_to(root))) for path in held if path not in expected]
    return findings, len(pairs)


def _generated_findings(root: Path, binary: str) -> list[dict]:
    """Comparison 3: one finding per file rulesync would write, or rulesync's own reason. Without a
    root rule rulesync has no source for CLAUDE.md and AGENTS.md and would not compare them."""
    rules = sorted((root / SOURCES / "rules").glob("*.md"))
    if not any(isinstance(front := _split(rule)[0], dict) and front.get("root") is True for rule in rules):
        return [_finding("ROOT_RULE_ABSENT", f"{SOURCES}/rules/ holds no rule marked root: true: "
                         "CLAUDE.md and AGENTS.md have no source; the generated files were not compared")]
    code, out, err = _run(binary, *GENERATE, cwd=root)
    try:
        answer = json.loads(out if out.strip() else err)
    except json.JSONDecodeError:
        answer = None
    data = answer.get("data") if isinstance(answer, dict) and answer.get("success") is True else None
    features = data.get("features") if isinstance(data, dict) else None
    if code != 0 or not isinstance(features, dict) or not isinstance(data.get("hasDiff"), bool):
        error = answer.get("error") if isinstance(answer, dict) else None
        reason = error.get("message") if isinstance(error, dict) else (err or out).strip()
        return [_finding("RULESYNC_FAILED", f"rulesync generate --dry-run: {reason[-500:] or f'exit {code}'}")]
    paths = sorted({path for feature in features.values() if isinstance(feature, dict)
                    for path in feature.get("paths") or []})
    if data["hasDiff"] and not paths:
        return [_finding("GENERATED_DIFFERS", "rulesync reports a difference and names no file")]
    return [_finding("GENERATED_DIFFERS", "is not what rulesync generates from its sources", path)
            for path in paths]


def main() -> int:
    root = Path.cwd()
    binary = _find_rulesync()
    version = _version_finding(root, binary)
    findings, kernel_files = _kernel_findings(root)
    if version is not None:
        version["message"] += "; the generated files were not compared"
        findings.insert(0, version)
    else:
        findings += _generated_findings(root, binary)
    answered = version is None and not any(
        finding["code"] in ("RULESYNC_FAILED", "ROOT_RULE_ABSENT") for finding in findings)
    compared = {"rulesync_version": version is None, "kernel_files": kernel_files, "generated_files": answered}
    print(json.dumps({"findings": findings, "compared": compared}, indent=1))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
