"""The role a worker is launched as: its role file, its skills and its default line (W2-60a; DEC-826 Q1, DEC-839).

The role file ``template/governance/kernel/roles/<role>.md`` carries a version
line and a default line (model and effort, nothing else), and may name its skills.
In a tree with no ``template/`` (an adopted repository) it is ``governance/kernel/roles/<role>.md``.
The skills the session can load are the project's copies under ``.claude/skills/``
and its command files under ``.claude/commands/``; each is described from that copy.
The user settings file's ask and deny rules are read here for the launcher to carry
into the session's settings (``--setting-sources project,local`` drops it). The text appended to the session's prompt is the
role file's bytes, then each named skill's ``SKILL.md``, in the order named.
Whatever cannot be read or is not of the stated form refuses the launch.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from pathlib import Path

import yaml

from gov.cli.errors import GovError
from gov.guard.heldout import load_yaml_unique

ROLES_REL = "template/governance/kernel/roles"
ADOPTED_ROLES_REL = "governance/kernel/roles"  # P-W2-60a-4 (a): an adopted repository's kernel, read when no template/
SKILLS_REL = ".claude/skills"
COMMANDS_REL = ".claude/commands"  # each Markdown file loads as a skill too
USER_SETTINGS_REL = ".claude/settings.json"  # under the caller's home; --setting-sources project,local drops it
EFFORTS = ("low", "medium", "high", "xhigh", "max")  # the CLI's --effort values
NO_VERSION = "no version"  # as gov close writes it
VERSION_HEAD, DEFAULT_HEAD, SKILLS_HEAD = "- **Version:**", "- **Launch default:**", "- **Skills:**"
VERSION_LINE = re.compile(r"- \*\*Version:\*\* (\d+\.\d+\.\d+)")
MODEL = r"claude(?:-[a-z0-9]+)+"
DEFAULT_LINE = re.compile(rf"- \*\*Launch default:\*\* model ({MODEL}), effort ({'|'.join(EFFORTS)})")
SKILLS_LINE = re.compile(r"- \*\*Skills:\*\* ([a-z0-9-]+(?:, [a-z0-9-]+)*)")
DEFAULT_FORM = "- **Launch default:** model <model>, effort <effort>"


def _refuse(reason: str) -> GovError:
    return GovError("LAUNCH_REFUSED", reason)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _one_line(lines: list[str], head: str, form: re.Pattern, rel: str, shown: str, required: bool):
    """The match of the one line of ``form`` that begins with ``head``; ``None`` when none does and none is needed."""
    found = [line for line in lines if line.lstrip().startswith(head)]
    if not found:
        if required:
            raise _refuse(f"the role file {rel} has no line '{shown}'")
        return None
    match = form.fullmatch(found[0]) if len(found) == 1 else None
    if match is None:
        raise _refuse(f"the role file {rel} must hold its line '{shown}' once, whole and of that form")
    return match


def _front_matter(text: str, rel: str) -> dict:
    """The YAML front matter of a ``SKILL.md``: empty when it has none; refused when it is not a YAML map."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
        front = load_yaml_unique("\n".join(lines[1:end]))
    except (StopIteration, yaml.YAMLError):
        raise _refuse(f"the skill {rel} has a front matter that is not YAML") from None
    if front is None:
        return {}
    if not isinstance(front, dict):
        raise _refuse(f"the skill {rel} has a front matter that is not a YAML map")
    return front


def _version(front: dict) -> str:
    """A skill's or command's version: its top-level ``version``, else ``metadata.version`` when ``metadata`` is a
    map (the kernel's generated copies carry it there); neither is ``no version``."""
    version = front.get("version")
    metadata = front.get("metadata")
    if not version and isinstance(metadata, dict):
        version = metadata.get("version")
    return str(version) if version else NO_VERSION


def _folder_sha256(folder: Path, rel: str) -> str:
    """The sha256 of each regular file's path and sha256, in path order; a link or another kind of entry refuses."""
    entries = []
    for here, dirs, files in os.walk(folder):
        for name in dirs + files:
            path = Path(here, name)
            mode = os.lstat(path).st_mode
            if stat.S_ISLNK(mode):
                raise _refuse(f"the skill folder {rel} holds a link, {path.relative_to(folder)}")
            if stat.S_ISREG(mode):
                entries.append((path.relative_to(folder).as_posix(), sha256(path.read_bytes())))
            elif not stat.S_ISDIR(mode):
                raise _refuse(f"the skill folder {rel} holds an entry that is not a file or a folder")
    return sha256("".join(f"{sha}  {path}\n" for path, sha in sorted(entries)).encode())


def _skills(root: Path) -> dict[str, dict]:
    """Every skill the session can load, by name: each folder directly under ``.claude/skills/`` with a ``SKILL.md``."""
    base = root / SKILLS_REL
    if not os.path.lexists(base):
        return {}
    if base.is_symlink() or not base.is_dir():
        raise _refuse(f"{SKILLS_REL} is a link or not a folder")
    skills: dict[str, dict] = {}
    try:
        for name in sorted(os.listdir(base)):
            folder, rel = base / name, f"{SKILLS_REL}/{name}"
            if folder.is_symlink():
                raise _refuse(f"the skill folder {rel} is a link")
            if not folder.is_dir() or not os.path.lexists(folder / "SKILL.md"):
                continue
            folder_hash = _folder_sha256(folder, rel)
            data = (folder / "SKILL.md").read_bytes()
            front = _front_matter(data.decode("utf-8"), f"{rel}/SKILL.md")
            skill_name = str(front.get("name") or name)
            if skill_name in skills:
                raise _refuse(f"two skill folders of {SKILLS_REL} give the name '{skill_name}'")
            skills[skill_name] = {"name": skill_name, "path": f"{rel}/SKILL.md", "version": _version(front),
                                  "sha256": sha256(data), "folder_sha256": folder_hash,
                                  "named": False, "text": data}
    except (OSError, UnicodeDecodeError):
        raise _refuse(f"the skills under {SKILLS_REL} cannot be read, so the record could not say what the session "
                      f"may load") from None
    return skills


def _raise(error: OSError) -> None:
    raise error


def _commands(root: Path) -> list[dict]:
    """The project's command files, which the session loads as skills: ``.claude/commands/<name>.md`` as ``<name>``,
    ``<namespace>/<name>.md`` as ``<namespace>:<name>``; each described from that file, as a skill folder is."""
    base = root / COMMANDS_REL
    if not os.path.lexists(base):
        return []
    if base.is_symlink() or not base.is_dir():
        raise _refuse(f"{COMMANDS_REL} is a link or not a folder")
    commands = []
    try:
        for here, dirs, files in os.walk(base, onerror=_raise):
            for name in sorted(dirs + files):
                path = Path(here, name)
                rel = f"{COMMANDS_REL}/{path.relative_to(base).as_posix()}"
                if path.is_symlink():
                    raise _refuse(f"the command {rel} is a link, so the record could not say what the session may load")
                if not name.endswith(".md") or not path.is_file():
                    continue
                data = path.read_bytes()
                front = _front_matter(data.decode("utf-8"), rel)
                commands.append({"name": ":".join(path.relative_to(base).with_suffix("").parts), "path": rel,
                                 "version": _version(front), "sha256": sha256(data),
                                 "folder_sha256": sha256(data), "named": False})
    except (OSError, UnicodeDecodeError):
        raise _refuse(f"the commands under {COMMANDS_REL} cannot be read, so the record could not say what the "
                      f"session may load") from None
    return sorted(commands, key=lambda command: command["path"])


def user_rules(home: Path) -> dict[str, list[str]]:
    """The ``permissions.ask`` and ``permissions.deny`` rules of the user's settings file, which
    ``--setting-sources project,local`` drops: carried so the session keeps them. Nothing else of the file is read
    into the session, and an absent file carries nothing."""
    path = home / USER_SETTINGS_REL
    if not os.path.lexists(path):
        return {"ask": [], "deny": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError):
        raise _refuse(f"~/{USER_SETTINGS_REL} cannot be read, so its ask and deny rules cannot be kept") from None
    permissions = data.get("permissions", {}) if isinstance(data, dict) else None
    if not isinstance(permissions, dict):
        raise _refuse(f"~/{USER_SETTINGS_REL} is not a map, or its permissions is not: its ask and deny rules "
                      f"cannot be kept")
    rules = {}
    for key in ("ask", "deny"):
        rules[key] = permissions.get(key, [])
        if not isinstance(rules[key], list) or not all(isinstance(rule, str) for rule in rules[key]):
            raise _refuse(f"~/{USER_SETTINGS_REL}: permissions.{key} is not a list of rules, so it cannot be kept")
    return rules


def read_role(root: Path, role: str) -> dict:
    """The role file read once: its path, bytes, version, sha256, default model and effort, and the skills.

    ``skills`` holds every loadable skill, named or not, in the record's form; ``appended`` the bytes of the text
    appended to the session's prompt: the role file, then each named skill's ``SKILL.md`` in the order named.
    """
    roles_rel = ROLES_REL if os.path.lexists(root / ROLES_REL.split("/")[0]) else ADOPTED_ROLES_REL
    rel = f"{roles_rel}/{role}.md"
    try:
        data = (root / rel).read_bytes()
        lines = data.decode("utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        raise _refuse(f"the role file {rel} cannot be read: the session would start without its role (DEC-826 Q1)") \
            from None
    version = _one_line(lines, VERSION_HEAD, VERSION_LINE, rel, "- **Version:** <major>.<minor>.<patch>", True)
    default = _one_line(lines, DEFAULT_HEAD, DEFAULT_LINE, rel, DEFAULT_FORM, True)
    named_line = _one_line(lines, SKILLS_HEAD, SKILLS_LINE, rel, "- **Skills:** <name>, <name>", False)
    named = named_line.group(1).split(", ") if named_line else []
    if len(set(named)) != len(named):
        raise _refuse(f"the role file {rel} names a skill twice in its line '- **Skills:**'")
    skills = _skills(root)
    appended = [data]
    for name in named:
        skill = skills.get(name)
        if skill is None or skill["path"] != f"{SKILLS_REL}/{name}/SKILL.md":
            raise _refuse(f"the role file {rel} names the skill '{name}', which is not at {SKILLS_REL}/{name}/SKILL.md")
        if skill["version"] == NO_VERSION:
            raise _refuse(f"the skill '{name}' that {rel} names carries no version in its front matter")
        skill["named"] = True
        appended.append(skill["text"])
    text = b"".join(part if part.endswith(b"\n") else part + b"\n" for part in appended)
    return {"role_text": {"path": rel, "version": version.group(1), "sha256": sha256(data)},
            "model": default.group(1), "effort": default.group(2), "appended": text,
            "skills": [{k: v for k, v in skill.items() if k != "text"} for skill in skills.values()] + _commands(root)}
