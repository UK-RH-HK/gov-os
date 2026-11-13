"""Generic skill-file validator (DEC-439, CAP-24.c / CAP-38.b).

Validates skill files (.md with YAML frontmatter) for required fields,
token limits, and gov-command references.

Usage::

    python3 -m gov.check.skill_validator <skill-folders-or-files...>
    python3 -m gov.check.skill_validator --both-layouts template/<kernel-skill-folders...>

With ``--both-layouts`` (DEC-521) a path under ``template/`` names a kernel skill in both places it can lie:
as the template holds it, and as an installed kernel holds it (the same path without ``template/``). Each
place whose skills folder exists is measured, and a skill absent from such a folder is unmeasured.

The front matter is closed (DEC-995, DEC-996 item 4, DEC-1156 (2); W2-120). On every copy read, a permission key
(``allowed-tools``, ``permissions``, ``paths``, ``sandbox``, ``network``, ``model``, ``effort``) or any key outside
the skill template's list is one finding naming the file and the key. The list is ``name``, ``version``,
``description``, ``output`` and ``metadata`` (with ``metadata.version`` its one carried key) for the kernel source and
the ``.rulesync`` copies, and ``name``, ``description`` and ``metadata`` for ``.claude/skills/`` (rulesync drops the
rest). Only the ``.rulesync`` and kernel copies must carry a ``version``. A missing ``output`` is not refused.

Which copies (I3): beyond the folders it is given, the validator reads the generated copies relative to the working
directory (the project root): ``.rulesync/skills/``, ``template/.rulesync/skills/`` and ``.claude/skills/``. Given a
skill folder (or a group folder such as ``superpowers``) it reads the copies of the skills in it, found by folder name
in each generated folder that holds one; given a skills root (a folder named ``skills`` with no ``SKILL.md`` of its
own) it reads each generated folder that exists in full. A generated folder that does not exist is not read.

Vendored skills (I4): a skill under ``superpowers/``, a folder named ``openspec-*`` and the generated copies of a
kernel ``superpowers`` skill. A key the closed list would refuse is named with code ``SKILL_VENDORED_KEY`` and does
not change the exit; no ``version`` is required of them.

Output: ``{"findings": [...]}``; every finding carries ``code``, ``file``, ``key`` and ``message`` and the exit is 1
when any finding other than ``SKILL_VENDORED_KEY`` exists. ``key`` is the offending front-matter key (``metadata.<k>``
for a key inside ``metadata``); a missing or invalid field names that field; the description length names
``description``; the body length and an unknown ``gov`` command name ``body``; a file with no front matter has
``key`` null. ``{"unmeasured": true, ...}`` is as before.
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

from gov.check.commands import GOV_COMMANDS
from gov.context import TOKEN_CHARS
from gov.util.frontmatter import with_body as _parse_frontmatter

_MAX_DESC_TOKENS = 60
_MAX_BODY_TOKENS = 2500
_REQUIRED_FIELDS = ("name", "version", "description")
_GOV_CMD_RE = re.compile(r"gov\s+(\w+)")
_BOTH_LAYOUTS = "--both-layouts"
_TEMPLATE_PREFIX = "template/"
_VENDORED_CODE = "SKILL_VENDORED_KEY"
_PERMISSION_KEYS = frozenset(
    ("allowed-tools", "permissions", "paths", "sandbox", "network", "model", "effort"))
_KERNEL_KEYS = frozenset(("name", "version", "description", "output", "metadata"))
_CLAUDE_KEYS = frozenset(("name", "description", "metadata"))
_METADATA_KEYS = frozenset(("version",))
_GENERATED_FOLDERS = (".rulesync/skills", "template/.rulesync/skills", ".claude/skills")
_CLAUDE_FOLDER = ".claude/skills"
_ROOT_NAME = "skills"
_SKILL_FILE = "SKILL.md"


def _finding(code: str, file: str, key: str | None, message: str) -> dict:
    return {"code": code, "file": file, "key": key, "message": message}


def _is_vendored_name(name: str) -> bool:
    return name == "superpowers" or name.startswith("openspec-")


def _is_claude_copy(path: Path) -> bool:
    """True when ``path`` lies under the working directory's ``.claude/skills/`` (a generated copy)."""
    return path.resolve().is_relative_to((Path.cwd() / _CLAUDE_FOLDER).resolve())


def _tokens(text: str) -> int:
    return math.ceil(len(text) / TOKEN_CHARS)


def _extract_code_text(body: str) -> list[str]:
    """Extract text from inline code spans and fenced code blocks."""
    parts: list[str] = []
    lines = body.split("\n")
    in_fence = False
    fence_content: list[str] = []
    for line in lines:
        if not in_fence and re.match(r"^```", line):
            in_fence = True
            fence_content = []
            continue
        if in_fence:
            if re.match(r"^```", line):
                in_fence = False
                parts.append("\n".join(fence_content))
            else:
                fence_content.append(line)
            continue
        for span in re.findall(r"`([^`]+)`", line):
            parts.append(span)
    return parts


def _key_findings(fm: dict, label: str, claude: bool, vendored: bool) -> list[dict]:
    """The front-matter keys outside the closed list, one finding each (I2); named only for a vendored skill (I4)."""
    allowed = _CLAUDE_KEYS if claude else _KERNEL_KEYS
    code = _VENDORED_CODE
    refused: list[str] = []
    for key in fm:
        key = str(key)
        if key not in allowed:
            refused.append(key)
    meta = fm.get("metadata")
    if isinstance(meta, dict):
        refused.extend(f"metadata.{sub}" for sub in meta if str(sub) not in _METADATA_KEYS)
    findings = []
    for key in refused:
        if not vendored:
            code = "SKILL_PERMISSION_KEY" if key in _PERMISSION_KEYS else "SKILL_UNLISTED_KEY"
        kind = "permission key" if key in _PERMISSION_KEYS else "key outside the skill template's list"
        findings.append(_finding(code, label, key, f"{kind} '{key}' in the front matter of {label}"))
    return findings


def validate_file(path: Path, vendored: bool = False) -> list[dict]:
    findings: list[dict] = []
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    label = str(path)
    fm, body = _parse_frontmatter(content)
    if fm is None:
        findings.append(_finding("SKILL_NO_FRONTMATTER", label, None, f"no valid YAML frontmatter in {label}"))
        return findings

    claude = _is_claude_copy(path)
    for field in _REQUIRED_FIELDS:
        val = fm.get(field)
        if field == "version":
            if claude or vendored:
                continue
            if val is None or (isinstance(val, str) and not val):
                findings.append(_finding(
                    "SKILL_MISSING_VERSION", label, field, f"version field missing or empty in {label}"))
            elif not isinstance(val, str):
                findings.append(_finding(
                    "SKILL_INVALID_FIELD", label, field, f"version must be a string in {label}"))
        elif val is None:
            findings.append(_finding(
                "SKILL_MISSING_FIELD", label, field, f"required field '{field}' missing in {label}"))
        elif not isinstance(val, str) or not val:
            findings.append(_finding(
                "SKILL_INVALID_FIELD", label, field, f"field '{field}' must be a non-empty string in {label}"))

    findings.extend(_key_findings(fm, label, claude, vendored))

    desc = fm.get("description")
    # a vendored text is not ours to shorten: its keys are named, its lengths are not measured
    if not vendored and isinstance(desc, str) and _tokens(desc) > _MAX_DESC_TOKENS:
        findings.append(_finding(
            "SKILL_DESCRIPTION_TOO_LONG", label, "description",
            f"description is {_tokens(desc)} tokens (max {_MAX_DESC_TOKENS}) in {label}"))

    if not vendored and _tokens(body) > _MAX_BODY_TOKENS:
        findings.append(_finding(
            "SKILL_BODY_TOO_LONG", label, "body",
            f"body is {_tokens(body)} tokens (max {_MAX_BODY_TOKENS}) in {label}"))

    for code_text in _extract_code_text(body):
        for match in _GOV_CMD_RE.finditer(code_text):
            cmd = match.group(1)
            if cmd not in GOV_COMMANDS:
                findings.append(_finding(
                    "SKILL_UNKNOWN_COMMAND", label, "body", f"unknown gov command '{cmd}' in {label}"))

    return findings


def _find_skill_files(folder: Path) -> list[Path]:
    return sorted(folder.rglob(_SKILL_FILE))


def _kernel_files(folder: Path) -> list[tuple[Path, bool]]:
    """Each skill file under ``folder`` with whether it is vendored (by its folder names, the given one included)."""
    return [(f, any(_is_vendored_name(part) for part in (folder.name, *f.relative_to(folder).parts[:-1])))
            for f in _find_skill_files(folder)]


def _generated_files(folder: Path, kernel: list[tuple[Path, bool]], vendored_names: set[str]) -> list[tuple[Path, bool]]:
    """The generated copies (I3) of what ``folder`` holds: all of each generated folder that exists for a skills
    root, else the copy of each skill found by folder name in each generated folder that holds one."""
    generated = [Path(name) for name in _GENERATED_FOLDERS if Path(name).is_dir()]
    root = folder.name == _ROOT_NAME and not (folder / _SKILL_FILE).exists()
    found: list[tuple[Path, bool]] = []
    for gen in generated:
        if root:
            candidates = _find_skill_files(gen)
        else:
            candidates = [gen / name / _SKILL_FILE for name in sorted({f.parent.name for f, _ in kernel})]
        for cand in candidates:
            if cand.is_file():
                name = cand.parent.name
                found.append((cand, name in vendored_names or _is_vendored_name(name)))
    return found


def _unmeasured(reason: str) -> int:
    print(json.dumps({"unmeasured": True, "reason": reason}))
    return 1


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    both_layouts = _BOTH_LAYOUTS in args
    args = [arg for arg in args if arg != _BOTH_LAYOUTS]

    if both_layouts:
        places: list[str] = []
        for arg in args:
            if not arg.startswith(_TEMPLATE_PREFIX):
                places.append(arg)
                continue
            held = [place for place in (arg, arg[len(_TEMPLATE_PREFIX):]) if Path(place).parent.is_dir()]
            if not held:
                return _unmeasured(f"path does not exist in either layout: {arg}")
            places.extend(held)
        args = places

    if not args:
        return _unmeasured("no skill files or folders specified")

    all_findings: list[dict] = []
    seen: set[Path] = set()

    def measure(path: Path, vendored: bool) -> bool:
        resolved = path.resolve()
        if resolved in seen:
            return True
        seen.add(resolved)
        result = validate_file(path, vendored)
        if result is None:
            return False
        all_findings.extend(result)
        return True

    pending: list[tuple[Path, bool]] = []
    for arg in args:
        p = Path(arg)
        if not p.exists():
            return _unmeasured(f"path does not exist: {arg}")

        if p.is_file():
            if not measure(p, _is_vendored_name(p.parent.name) or _is_vendored_name(p.parent.parent.name)):
                return _unmeasured(f"cannot read file: {arg}")
        elif p.is_dir():
            kernel = _kernel_files(p)
            if not kernel:
                return _unmeasured(f"no skill files found in {arg}")
            for f, vendored in kernel:
                if not measure(f, vendored):
                    return _unmeasured(f"cannot read file: {f}")
            names = {f.parent.name for f, vendored in kernel if vendored}
            pending.extend(_generated_files(p, kernel, names))

    for f, vendored in pending:
        if not measure(f, vendored):
            return _unmeasured(f"cannot read file: {f}")

    if all_findings:
        print(json.dumps({"findings": all_findings}))
        return 0 if all(f["code"] == _VENDORED_CODE for f in all_findings) else 1

    print(json.dumps({"findings": []}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
