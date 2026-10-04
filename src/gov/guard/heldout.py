"""Held-out paths (W1-47, DEC-162, DEC-215, DEC-218).

The paths are held in ``governance/project/held-out.yaml`` under the key
``held_out_paths``, a list of absolute paths.  The guard denies any tool
call whose input names one; the committed ``Read`` deny rules are written
from the same list by ``python3 -m gov.guard.heldout``.

No message of this module carries a path.
"""

from __future__ import annotations

import json
import os
import shlex

from gov.guard.decide import _expand_token

CONFIG_REL = "governance/project/held-out.yaml"
CONFIG_KEY = "held_out_paths"
SETTINGS_REL = ".claude/settings.json"
_EDIT_TOOLS = frozenset({"Write", "Edit"})


class HeldOutError(Exception):
    """``held-out.yaml`` exists and is not of the stated shape (DEC-218)."""


def load_yaml_unique(stream):
    """yaml.safe_load that refuses a mapping with a key written twice:
    a reader that kept the last value would drop the first without a word."""
    import yaml

    class Loader(yaml.SafeLoader):
        def construct_mapping(self, node, deep=False):
            mapping = super().construct_mapping(node, deep=deep)
            if len(mapping) != len(node.value):
                raise yaml.constructor.ConstructorError(
                    None, None, "a key is written twice", node.start_mark)
            return mapping

    return yaml.load(stream, Loader=Loader)


def load_held_out(project_root: str) -> list[str]:
    """Return the held-out paths; ``[]`` when the project has no such file.

    A file that cannot be read, or that does not hold a non-empty list of
    absolute paths under ``held_out_paths``, raises ``HeldOutError``: the
    guard fails closed (DEC-218).
    """
    path = os.path.join(project_root, CONFIG_REL)
    if not os.path.lexists(path):
        return []
    try:
        with open(path, encoding="utf-8") as f:
            data = load_yaml_unique(f)
    except Exception:
        # The parser's own message may quote the file: fixed text only.
        raise HeldOutError(f"{CONFIG_REL} cannot be read") from None
    paths = data.get(CONFIG_KEY) if isinstance(data, dict) else None
    if not isinstance(paths, list) or not paths:
        raise HeldOutError(f"{CONFIG_REL} holds no list under {CONFIG_KEY}")
    for p in paths:
        if (not isinstance(p, str) or not p.startswith("/")
                or not p.rstrip("/") or "\n" in p):
            raise HeldOutError(
                f"{CONFIG_REL}: an entry of {CONFIG_KEY} is not an absolute path")
    return [p.rstrip("/") for p in paths]


def _strings(value):
    """Every string value of a tool input, at any depth."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from _strings(v)
    elif isinstance(value, (list, tuple)):
        for v in value:
            yield from _strings(v)


def _words(command: str) -> list[str]:
    try:
        lex = shlex.shlex(command, posix=True, punctuation_chars="();<>|&\n")
        lex.whitespace_split = True
        lex.whitespace = " \t\r"
        lex.commenters = ""
        return list(lex)
    except ValueError:
        return command.split()


def _reaches(text: str, cwd: str, bases: list[str], shell: bool) -> bool:
    """True when *text*, read as a path, resolves to a held-out path:
    relative to *cwd*, through ``..``, ``~`` or a symbolic link, and in a
    Bash word through ``$HOME`` (DEC-215)."""
    exp = _expand_token(text) if shell else os.path.expanduser(text)
    if not exp:
        return False
    try:
        real = os.path.realpath(os.path.join(cwd, exp))
    except (OSError, ValueError):
        return False  # not a path
    return any(real == b or real.startswith(b + "/") for b in bases)


def names_held_out(tool_name: str, tool_input: dict, project_root: str,
                   cwd: str, paths: list[str]) -> bool:
    """True when the call's input holds a held-out path literally anywhere,
    or reaches one without writing it out (DEC-215)."""
    # Exception: an edit to one of the two files that hold the path is not
    # denied for what it carries; where it goes is still checked.
    if tool_name in _EDIT_TOOLS:
        fp = tool_input.get("file_path")
        if isinstance(fp, str) and fp:
            holders = {os.path.realpath(os.path.join(project_root, rel))
                       for rel in (CONFIG_REL, SETTINGS_REL)}
            if os.path.realpath(os.path.join(cwd, fp)) in holders:
                tool_input = {"file_path": fp}

    bases = list({b for p in paths for b in (p, os.path.realpath(p))})
    for key, value in tool_input.items():
        for text in _strings(value):
            if any(p in text for p in paths):
                return True
            if tool_name == "Bash" and key == "command":
                if any(_reaches(w, cwd, bases, True) for w in _words(text)):
                    return True
            elif _reaches(text, cwd, bases, False):
                return True
    return False


def write_read_rules(project_root: str, settings_path: str | None = None) -> int:
    """Write one ``Read`` deny rule per held-out path into a settings file
    and return how many were added.  Prints nothing (DEC-218)."""
    paths = load_held_out(project_root)
    if not paths:
        raise HeldOutError(f"{CONFIG_REL} does not exist")
    settings_path = settings_path or os.path.join(project_root, SETTINGS_REL)
    with open(settings_path, encoding="utf-8") as f:
        settings = json.load(f)
    deny = settings.setdefault("permissions", {}).setdefault("deny", [])
    added = 0
    for p in paths:
        rule = f"Read(/{p}/**)"  # //<path> is the absolute form in a rule
        if rule not in deny:
            deny.append(rule)
            added += 1
    with open(settings_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(settings, indent=2) + "\n")
    return added


if __name__ == "__main__":
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    print(f"{write_read_rules(root)} Read deny rule(s) added to {SETTINGS_REL}")
