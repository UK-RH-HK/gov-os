"""Helpers for the W1-37 acceptance tests: the copied skills, their record file and the DEC-199 digest.

Nothing here installs, downloads or writes anything. The vendor folder, the
copy and the record file are read from the working tree.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

VENDOR_REL = "template/governance/kernel/vendor/superpowers"
VENDOR_SKILLS_REL = f"{VENDOR_REL}/skills"
COPY_REL = "template/governance/kernel/skills/superpowers"
RECORD_NAME = "vendored.yaml"
RECORD_REL = f"{COPY_REL}/{RECORD_NAME}"
LICENCE_NAME = "LICENSE"

VERSION = "6.4.2"

# DEC-247: floor(characters / 4) of SKILL.md, at or below these, no tolerance.
CEILINGS = {
    "test-driven-development": 2389,
    "systematic-debugging": 2360,
    "verification-before-completion": 899,
}
SKILLS = tuple(CEILINGS)

SHA256 = re.compile(r"[0-9a-f]{64}")

PLUGIN_FILES = ("plugin.json", "marketplace.json")
HOOK_FILES = ("hooks.json",)
EXCLUDED_SKILL = "subagent-driven-development"


class Missing(AssertionError):
    """A file or folder the tests read is not there, or cannot be read."""


def load_folder(rel):
    """``{relative posix path: bytes}`` of every file on disk under the folder ``rel``."""
    root = REPO_ROOT / rel
    return {path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*")) if path.is_file()}


def symlinks(rel):
    """The symbolic links under the folder ``rel``, relative to it."""
    root = REPO_ROOT / rel
    return sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_symlink())


def load_vendor():
    """The vendor folder W1-06 committed (DEC-194): the only source of the copy (DEC-244)."""
    if not (REPO_ROOT / VENDOR_REL).is_dir():
        raise Missing(f"{VENDOR_REL}/ does not exist: the source W1-06 committed is missing")
    return load_folder(VENDOR_REL)


def load_copy():
    """The files under ``skills/superpowers/``, the record file among them."""
    if not (REPO_ROOT / COPY_REL).is_dir():
        raise Missing(f"{COPY_REL}/ does not exist: W1-37 has not copied the three skills")
    return load_folder(COPY_REL)


def load_record():
    """The record file of DEC-246, as a plain YAML load gives it."""
    path = REPO_ROOT / RECORD_REL
    if not path.is_file():
        raise Missing(f"{RECORD_REL} does not exist: W1-37 has not written the record of DEC-246")
    import yaml  # PyYAML is the project's declared dependency (pyproject.toml)

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise Missing(f"{RECORD_REL} is not YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise Missing(f"{RECORD_REL} is not a YAML mapping")
    return data


def folder_digest(files):
    """DEC-199's digest of a folder, given as ``{relative posix path: the file's bytes}``.

    One line per file: the file's sha256 in lowercase hexadecimal, two spaces,
    the path, one line feed. The lines are encoded as UTF-8, sorted as bytes,
    concatenated, and hashed with sha256.
    """
    lines = sorted(f"{hashlib.sha256(content).hexdigest()}  {rel}\n".encode("utf-8")
                   for rel, content in files.items())
    return hashlib.sha256(b"".join(lines)).hexdigest()


def copied(copy):
    """The copy without its record file: what the record's ``sha256`` covers."""
    return {rel: content for rel, content in copy.items() if rel != RECORD_NAME}


def under(files, folder):
    """The files of ``files`` inside ``folder``, relative to it."""
    prefix = f"{folder}/"
    return {rel[len(prefix):]: content for rel, content in files.items() if rel.startswith(prefix)}


def token_size(content):
    """DEC-247: floor(characters / 4), the characters being those of the UTF-8 text."""
    return len(content.decode("utf-8")) // 4


def norm_version(value):
    """``v6.4.2`` and ``6.4.2`` are the same version."""
    text = str(value).strip()
    return text[1:] if text[:1] in "vV" else text


def recorded_sha256(record, field):
    """The value of ``field``: 64 lowercase hexadecimal characters, or the test fails."""
    value = record.get(field)
    assert isinstance(value, str) and SHA256.fullmatch(value), (
        f"{RECORD_REL}: `{field}` must be a string of 64 lowercase hexadecimal characters, got {value!r}"
    )
    return value


def parts(rel):
    return [part.lower() for part in rel.split("/")]


def is_plugin(rel):
    return parts(rel)[-1] in PLUGIN_FILES or any("plugin" in part for part in parts(rel)[:-1])


def is_hook(rel):
    name = parts(rel)[-1]
    return "hooks" in parts(rel)[:-1] or name in HOOK_FILES or name.startswith(("session-start", "sessionstart"))
