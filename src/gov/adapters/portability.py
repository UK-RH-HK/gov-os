"""Adapter/model-portability check (CAP-38.b): the kernel, the rulesync sources and the generated adapters agree.

Three comparisons, each a finding when it fails or cannot be made:
1. the installed rulesync with the version the project's tool registry expects (DEC-127);
2. each kernel role and kernel skill file with its source under ``.rulesync/``, and a role's tools
   with its source's ``claudecode.tools`` (DEC-471);
3. the generated files, byte for byte, with what rulesync generates from the sources into an empty
   temporary folder; a file of the generated folders that rulesync does not write has no source.

Prints ``{"findings": [...], "compared": {...}}`` and exits 0 only without findings.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

REGISTRY = "governance/project/tool-registry.yaml"
KERNEL_ROOTS = ("governance/kernel", "template/governance/kernel")  # adopted project, this repository
SOURCES = ".rulesync"
GENERATE = ("generate", "--targets", "claudecode,agentsmd",
            "--features", "rules,hooks,permissions,subagents,commands,skills", "--input-roots")
GENERATED_FOLDERS = (".claude/agents", ".claude/skills", ".claude/commands")  # rulesync alone writes here (DEC-471)
TOOLS = frozenset("Agent Bash Edit Glob Grep NotebookEdit Read Skill Task TodoWrite WebFetch WebSearch Write".split())
TOOLS_FIELD = re.compile(r"^[-*]\s+\*\*Tools:?\*\*:?(.*(?:\n[ \t]+\S.*)*)", re.MULTILINE)
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
    """``(exit code, stdout, stderr)``; the exit code is None when rulesync gave no answer."""
    try:
        done = subprocess.run([binary, *args], capture_output=True, text=True, cwd=str(cwd),
                              timeout=TIME_LIMIT, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return None, "", f"no answer within {TIME_LIMIT} seconds"
    except OSError as exc:
        return None, "", str(exc)
    return done.returncode, done.stdout, done.stderr


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


def _tools_difference(role_body: str, front: object) -> str:
    """Empty when the tool names in the kernel role's Tools field (whole words, from the label to the
    end of its indented lines) are the set of the source's ``claudecode.tools``; else the difference."""
    field = TOOLS_FIELD.search(role_body)
    adapter = front.get("claudecode") if isinstance(front, dict) else None
    listed = adapter.get("tools") if isinstance(adapter, dict) else None
    if field is None or not isinstance(listed, list):
        return "no Tools field in the kernel role" if field is None else "the source states no claudecode.tools"
    kernel, source = set(re.findall(r"[A-Za-z]+", field.group(1))) & TOOLS, {str(tool) for tool in listed}
    if kernel == source:
        return ""
    return f"only in the source {sorted(source - kernel)}, only in the kernel role {sorted(kernel - source)}"


def _kernel_findings(root: Path) -> tuple[list[dict], int]:
    """Comparison 2, both ways: ``(findings, number of kernel files compared)``. A role is compared by
    body and by tools (the rest of its source's frontmatter is rulesync's own), a SKILL.md by body and
    frontmatter, any other file of a skill folder by bytes. Each finding names the rulesync source."""
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
            (_front, role_body), (front, source_body) = _split(kernel_file), _split(source)
            same = role_body == source_body
            if tools := _tools_difference(role_body, front):
                findings.append(_finding("SOURCE_TOOLS_DIFFER", f"tools are not those of {origin}: {tools}", rel))
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


def _generated_findings(root: Path, binary: str) -> tuple[list[dict], int]:
    """Comparison 3: ``(findings, number of files compared)``. rulesync generates from the project's
    sources into an empty temporary folder; each file it writes there is compared byte for byte with the
    project's, and a file of the generated folders that it did not write is a file without a source.
    Without a root rule rulesync has no source for CLAUDE.md and AGENTS.md and would not write them."""
    rules = sorted((root / SOURCES / "rules").glob("*.md"))
    if not any(isinstance(front := _split(rule)[0], dict) and front.get("root") is True for rule in rules):
        return [_finding("ROOT_RULE_ABSENT", f"{SOURCES}/rules/ holds no rule marked root: true: "
                         "CLAUDE.md and AGENTS.md have no source; the generated files were not compared")], 0
    with tempfile.TemporaryDirectory() as fresh:
        code, out, err = _run(binary, *GENERATE, str((root / SOURCES).resolve()), cwd=Path(fresh))
        made = {str(path.relative_to(fresh)): path.read_bytes()
                for path in sorted(Path(fresh).rglob("*")) if path.is_file()}
    if code != 0 or not made:
        reason = (err or out).strip()[-500:] or f"exit {code}, {len(made)} files written"
        return [_finding("RULESYNC_FAILED", f"rulesync generate: {reason}")], 0
    findings = [_finding("GENERATED_DIFFERS", "is not what rulesync generates from its sources", rel)
                for rel, content in made.items()
                if not (root / rel).is_file() or (root / rel).read_bytes() != content]
    held = sorted(str(path.relative_to(root)) for folder in GENERATED_FOLDERS
                  for path in (root / folder).rglob("*") if path.is_file())
    findings += [_finding("GENERATED_WITHOUT_SOURCE", "rulesync generates no such file from its sources", rel)
                 for rel in held if rel not in made]
    return findings, len(made)


def main() -> int:
    root = Path.cwd()
    binary = _find_rulesync()
    version = _version_finding(root, binary)
    findings, kernel_files = _kernel_findings(root)
    generated_files = 0
    if version is not None:
        version["message"] += "; the generated files were not compared"
        findings.insert(0, version)
    else:
        generated, generated_files = _generated_findings(root, binary)
        findings += generated
    compared = {"rulesync_version": version is None, "kernel_files": kernel_files,
                "generated_files": generated_files}
    print(json.dumps({"findings": findings, "compared": compared}, indent=1))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
