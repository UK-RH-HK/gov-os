#!/usr/bin/env python3
"""Build the register in force from the archived one, and check it (EMERGENCY-2 §11.3; audit 8; DEC-1214 G4; W2-203).

    python3 docs/emergency-2/audits/08-new-register.py [--root <repo>] [--archive <file>] [--register <file>]
                                                       (--out <file> | --check)

The archive is the file the path map of ``--root`` names under ``decision_register_archive`` (or ``--archive``); the
register is the one it names under ``decision_register`` (or ``--register``). ``--root`` defaults to the repository
this script is in.

- ``--out <file>`` writes the register: a short head, then, verbatim and in the archive's order, every entry of the
  archive whose first ``**Class:**`` is ``kept`` and every entry from DEC-1211 on, whatever the last id is. The same
  archive gives the same bytes.
- ``--check`` compares the register with what the archive requires, one line per failure: ``REGISTER_KEPT_MISSING
  <id>`` for an entry the register must hold and does not, ``REGISTER_ENTRY_DIFFERS <id>`` for a kept entry (below DEC-1211; the later ones are live) both files
  hold with different text. Exit 1 where there is one; otherwise a line starting ``ok`` and exit 0. An entry the
  archive does not hold (a decision made since) is no failure.

An entry runs from its ``### DEC-n`` heading to the line before the next such heading, a ``## `` heading or a ``---``
line, its trailing blank lines dropped.
"""
import argparse
import re
import sys
from pathlib import Path

PATH_MAP_REL = "governance/project/path-map.yaml"
ARCHIVE_KEY, REGISTER_KEY = "decision_register_archive", "decision_register"
FIRST_SINCE = 1211  # the first decision made after audit 8's classes (DEC-001 to DEC-1210)
HEADING = re.compile(r"### (DEC-\d+)")
CLASS = re.compile(r"\*\*Class:\*\* (\w+)")
HEAD = """# Governance OS — Decision Register (in force)

**Register ID:** GOV-DR · **Built from:** the archived register `{archive}` (archived read-only,
EMERGENCY-2 §11.3), by `docs/emergency-2/audits/08-new-register.py`.

This file is the decision register in force. The earlier decisions are in the archive, by id: `{archive}`.
Each entry below is copied verbatim from it: the decisions audit 8 (`docs/emergency-2/audits/08-register.md`) classed
**kept** (the owner approved the classes by group, DEC-1214 G4) and every decision since (DEC-1211 and later). The
`**Class:**` field at the end of an entry's status line says which items of a kept entry no longer hold. A decision that
is not here is in the archive; the archive is not in memory's index. New ids continue from the last entry's.

---

## Decisions

"""


def entries(text):
    """``[(id, text)]`` of a register's entries, in the file's order."""
    lines = text.split("\n")
    heads = [i for i, line in enumerate(lines) if HEADING.match(line)]
    out = []
    for k, i in enumerate(heads):
        end = heads[k + 1] if k + 1 < len(heads) else len(lines)
        j = i + 1
        while j < end and not lines[j].startswith("## ") and lines[j] != "---":
            j += 1
        out.append((HEADING.match(lines[i]).group(1), "\n".join(lines[i:j]).rstrip("\n")))
    return out


def required(entry_id, text):
    """Whether the register in force must hold this entry of the archive."""
    if int(entry_id[4:]) >= FIRST_SINCE:
        return True
    found = CLASS.search(text)
    return bool(found) and found.group(1) == "kept"


def build(archive_text, archive_rel):
    kept = [text for entry_id, text in entries(archive_text) if required(entry_id, text)]
    return HEAD.format(archive=archive_rel) + "\n\n".join(kept) + "\n"


def check(archive_text, register_text):
    """The failure lines of a register against its archive."""
    held = {}
    for entry_id, text in entries(register_text):
        held.setdefault(entry_id, text)
    lines, seen = [], set()
    for entry_id, text in entries(archive_text):
        if entry_id in seen:
            continue
        seen.add(entry_id)
        if entry_id not in held:
            if required(entry_id, text):
                lines.append(f"REGISTER_KEPT_MISSING {entry_id}")
        elif held[entry_id] != text and _live(entry_id) is False:
            lines.append(f"REGISTER_ENTRY_DIFFERS {entry_id}")
    return lines


def _live(entry_id):
    """True for a decision made after audit 8's classes (DEC-1211 and later): the register in force is live there, an
    entry is amended in place (DEC-1215's revert is recorded in its entry) and the frozen archive never follows; so
    only the kept entries below it are held to the archive's text. None where the id carries no number."""
    digits = "".join(ch for ch in entry_id.split("-")[-1] if ch.isdigit())
    return int(digits) >= FIRST_SINCE if digits else None


def _named(root, key, given=None):
    """The path the path map of ``root`` names under ``key``; ``given`` where it names none and one was given."""
    import yaml
    try:
        data = yaml.safe_load((root / PATH_MAP_REL).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as e:
        if given:
            return given
        sys.exit(f"the path map {PATH_MAP_REL} of {root} cannot be read: {e}")
    value = data.get(key) if isinstance(data, dict) else None
    if not isinstance(value, str) or not value:
        if given:
            return given
        sys.exit(f"the path map {PATH_MAP_REL} of {root} names no {key}")
    return value


def _read(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        sys.exit(f"{path} cannot be read: {e}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[3]))
    parser.add_argument("--archive")
    parser.add_argument("--register")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(args.root)
    archive_text = _read(args.archive or root / _named(root, ARCHIVE_KEY))
    if args.out:
        text = build(archive_text, _named(root, ARCHIVE_KEY, args.archive))  # the head names the archive by its path
        Path(args.out).write_bytes(text.encode("utf-8"))
        print(f"archive {len(entries(archive_text))} entries; register {len(entries(text))} entries -> {args.out}")
        return 0
    register_text = _read(args.register or root / _named(root, REGISTER_KEY))
    lines = check(archive_text, register_text)
    for line in lines:
        print(line)
    if lines:
        return 1
    print(f"ok: the register holds every entry the archive requires ({len(entries(register_text))} entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
