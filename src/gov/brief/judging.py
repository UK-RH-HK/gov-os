"""The judging-work skill in briefs (W2-195; DEC-1204 (5)): the one rule every brief that judges work carries.

A judging brief (the reviewer's and the probe's, briefed as ``independent-auditor``; the QA engineer's; the lead's
``review`` run, whose steps brief the reviewer and the probe) carries sections 1 to 3 of the installed skill file, byte
for byte as the file holds them at brief time, after one line naming the skill's version. The installed file is the
kernel's (``template/governance/kernel/skills/judging-work/SKILL.md`` in a tree with ``template/``, else
``governance/kernel/skills/judging-work/SKILL.md``, the same rule as ``gov.launch.role``); the session preloads its
copy ``.claude/skills/judging-work/SKILL.md``, whose version must be the kernel file's. Whatever is missing, unreadable
or of another version refuses the brief, ``BRIEF_JUDGING_RULE_MISSING``. Nothing here writes.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import yaml

from gov.cli.errors import GovError

SKILL = "judging-work"
KERNEL_REL = f"template/governance/kernel/skills/{SKILL}/SKILL.md"
ADOPTED_KERNEL_REL = f"governance/kernel/skills/{SKILL}/SKILL.md"
PRELOADED_REL = f".claude/skills/{SKILL}/SKILL.md"
JUDGING_ROLES = ("independent-auditor", "qa-engineer")
JUDGING_RUNS = ("review",)  # the lead's runs whose steps brief a reviewer or a probe
CODE = "BRIEF_JUDGING_RULE_MISSING"
# Sections 1 to 3: from the start of the line "## 1. The threat model" up to, not including, the line "## 4. Doing it"
FIRST = re.compile(rb"^## 1\. The threat model\r?$", re.MULTILINE)
FOURTH = re.compile(rb"^## 4\. Doing it\r?$", re.MULTILINE)


def judges(role: str, run: str | None) -> bool:
    """Whether the brief of ``role`` (with the lead's ``run``) judges work."""
    return role in JUDGING_ROLES or (role == "lead" and run in JUDGING_RUNS)


def kernel_rel(root: Path) -> str:
    """The installed skill file's path from ``root``: the kernel's under ``template/`` where there is one."""
    return ADOPTED_KERNEL_REL if not os.path.lexists(Path(root) / "template") else KERNEL_REL


def version_of(data: bytes) -> str | None:
    """A skill file's version: its front matter's top-level ``version``, else ``metadata.version`` (the form rulesync
    writes the generated copy in); None when it has neither, or no front matter that is a YAML map."""
    text = data.decode("utf-8")
    lines = text.split("\n")
    if not lines or lines[0].rstrip("\r") != "---":
        return None
    end = next((n for n in range(1, len(lines)) if lines[n].rstrip("\r") == "---"), None)
    if end is None:
        return None
    try:
        front = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError:
        return None
    if not isinstance(front, dict):
        return None
    version = front.get("version")
    if not version and isinstance(front.get("metadata"), dict):
        version = front["metadata"].get("version")
    return str(version) if version not in (None, "") else None


def sections(data: bytes) -> bytes | None:
    """Sections 1 to 3 of the skill file's bytes, unchanged: from the start of the line ``## 1. The threat model`` up
    to, not including, the line ``## 4. Doing it``; None when either line is missing or they are out of order."""
    first, fourth = FIRST.search(data), FOURTH.search(data)
    if first is None or fourth is None or fourth.start() <= first.start():
        return None
    return data[first.start():fourth.start()]


def _refuse(detail: str, **details) -> GovError:
    return GovError(CODE, f"the judging brief cannot carry the judging-work skill (DEC-1204 (5)): {detail}", details)


def _bytes(root: Path, rel: str, what: str) -> bytes:
    path = Path(root) / rel
    try:
        return path.read_bytes()
    except OSError:
        raise _refuse(f"no {what} at {rel}", path=rel) from None


def block(root: Path) -> str:
    """The text a judging brief carries: the line naming the skill's version, then sections 1 to 3 of the installed
    file as its bytes are. Refused (``BRIEF_JUDGING_RULE_MISSING``) when the installed file or the preloaded copy is
    missing, unreadable or without a version, the installed file has no sections 1 to 3, or the two versions differ."""
    rel = kernel_rel(root)
    data = _bytes(root, rel, "installed skill file")
    try:
        version, carried = version_of(data), sections(data)
        carried_text = carried.decode("utf-8") if carried is not None else None
    except UnicodeDecodeError:
        raise _refuse(f"{rel} is not UTF-8", path=rel) from None
    if version is None:
        raise _refuse(f"{rel} names no version in its front matter", path=rel)
    if carried_text is None:
        raise _refuse(f"{rel} has no sections 1 to 3 (a line '## 1. The threat model' before a line '## 4. Doing it')", path=rel)
    copy = _bytes(root, PRELOADED_REL, "preloaded copy")
    try:
        preloaded = version_of(copy)
    except UnicodeDecodeError:
        raise _refuse(f"{PRELOADED_REL} is not UTF-8", path=PRELOADED_REL) from None
    if preloaded != version:
        raise _refuse(f"the preloaded copy {PRELOADED_REL} is version {preloaded or 'none'}, the installed file {rel} "
                      f"is version {version}", path=PRELOADED_REL, version=version, preloaded=preloaded)
    return f"Judging work: the judging-work skill, version {version} (sections 1 to 3 of {rel}, verbatim):\n" \
           + carried_text
