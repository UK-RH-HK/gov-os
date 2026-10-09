"""The time limit of the guard's hook entries in a settings object (DEC-580). Standard library only.

DEC-580: "The kernel template's settings carry ``"timeout": 60`` on every guard
hook entry, so that every adopted project gets it." The reason is the evidence
record ``docs/research/EXP-hook-time-limit.md``: a hook that is still running at
its time limit is ended and the call goes through.

This module judges a parsed settings object and nothing else. It reads no file
but the names in a kernel hooks folder it is given, so the suite of the kernel
template (W1-47) and the suite of a project made from the template (W1-39) hold
the same rule with the same words.

What the words are taken to mean (the README of W1-47, "The guard hooks' time
limit"):

- **A hook entry** is one object of the ``hooks`` list of a matcher group, under
  any event: the object that holds ``type`` and ``command``. It is where the
  harness reads a hook's time limit, in seconds, under the key ``timeout``.
- **A guard hook entry** is a hook entry whose command runs a program of the
  kernel's hooks folder: its command names that folder, or names one of the
  folder's programs by file name. The guard before a call and the containment
  check after it are both such programs; so is any other kernel hook a later
  release registers.
- **Carries the limit** is: the entry itself holds ``timeout`` with the JSON
  number 60. A string, another number, zero, ``true``, ``60.0`` written as a
  fraction, or a limit on the matcher group alone do not count.
- A hook entry that runs no kernel hook program is not spoken of: it is left as
  it is, with or without a limit.
"""

from __future__ import annotations

import json
from pathlib import Path

LIMIT_KEY = "timeout"
LIMIT_S = 60
KERNEL_HOOKS_REL = "governance/kernel/hooks"


def load(path, name):
    """The settings object of the file at ``path``; ``name`` is what a failure calls the file."""
    path = Path(path)
    assert path.is_file(), f"{name} does not exist"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise AssertionError(f"{name} is not valid JSON: {exc}") from None
    assert isinstance(data, dict), f"{name} does not hold a JSON object"
    return data


def program_names(hooks_folder):
    """The file names of the programs in a kernel hooks folder (byte-code caches are no programs)."""
    folder = Path(hooks_folder)
    assert folder.is_dir(), f"{folder} is not a folder: the kernel has no hooks folder"
    names = sorted(path.name for path in folder.iterdir() if path.is_file() and not path.name.startswith("."))
    assert names, f"{folder} holds no hook program"
    return tuple(names)


def walk(settings):
    """Every hook entry of the object, as it stands: ``(where, group, entry)``, and what is not of the stated shape.

    ``where`` names the event, the matcher group (by its position and its matcher) and the entry's position.
    Returns ``(entries, misshapen)``; ``misshapen`` is a list of sentences.
    """
    entries, misshapen = [], []
    hooks = settings.get("hooks")
    if not isinstance(hooks, dict):
        return entries, ["the object holds no `hooks` map"]
    for event, groups in hooks.items():
        if not isinstance(groups, list):
            misshapen.append(f"{event}: not a list of matcher groups")
            continue
        for g, group in enumerate(groups):
            if not isinstance(group, dict) or not isinstance(group.get("hooks"), list):
                misshapen.append(f"{event}[{g}]: not a matcher group with a `hooks` list")
                continue
            matcher = group.get("matcher")
            label = f"{event}[{g}] (matcher {matcher!r})" if "matcher" in group else f"{event}[{g}] (no matcher)"
            for e, entry in enumerate(group["hooks"]):
                if not isinstance(entry, dict):
                    misshapen.append(f"{label} hooks[{e}]: not an object")
                    continue
                entries.append((f"{label} hooks[{e}]", group, entry))
    return entries, misshapen


def is_guard_entry(entry, programs):
    """The entry's command runs a program of the kernel's hooks folder."""
    command = entry.get("command")
    if not isinstance(command, str):
        return False
    return KERNEL_HOOKS_REL in command or any(name in command for name in programs)


def guard_entries(settings, programs):
    """``(where, group, entry)`` for every guard hook entry of the object."""
    return [(where, group, entry) for where, group, entry in walk(settings)[0] if is_guard_entry(entry, programs)]


def carries_the_limit(entry):
    value = entry.get(LIMIT_KEY)
    return type(value) is int and value == LIMIT_S


def faults(settings, programs):
    """One sentence for each guard hook entry that does not carry the limit, and for each misshapen part."""
    entries, found = walk(settings)
    found = list(found)
    for where, group, entry in entries:
        if not is_guard_entry(entry, programs) or carries_the_limit(entry):
            continue
        if LIMIT_KEY not in entry:
            state = f"carries no `{LIMIT_KEY}`"
            if LIMIT_KEY in group:
                state += (f" (its matcher group holds `{LIMIT_KEY}`: {group[LIMIT_KEY]!r}, where the harness does not "
                          f"read a hook's time limit)")
        else:
            state = f"carries `{LIMIT_KEY}`: {entry[LIMIT_KEY]!r}, which is not the number {LIMIT_S}"
        found.append(f"{where}, command `{entry.get('command')}`, {state}")
    return found
