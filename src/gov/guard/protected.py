"""Reads of the settings file and of the held-out file (DEC-508, DEC-525).

The guard refuses any agent tool call whose file targets take in one of
the two files, for every role: the file named, a folder above it inside
the project, or a glob that matches it.  A write to either file is not a
read and stays with the allow-list.

Nothing is listed or opened here: there are two known files, and the
question is whether a target takes one of them in.  No message of this
module carries a path.
"""

from __future__ import annotations

import os
import re
import shlex

from gov.guard.decide import (_ASSIGN_RE, _expand_token,
                              _extract_bash_write_targets, _has_glob, _is_punct)
from gov.guard.heldout import CONFIG_REL, SETTINGS_REL, _words

READ_REFUSAL = ("the call reads the settings file or the held-out file, which "
                "is refused to every role (DEC-508, DEC-525); the registered "
                "hooks are listed by python3 -m gov.guard.hooks")
# What separates a file name from the text around it in one shell word: a
# script on the command line, <commit>:<file>, --option=<file>.
_PIECE_RE = re.compile(r"""[\s'"()=:,;]+""")
# The options with which git diff and git status print no line of a file.
_GIT_QUIET = frozenset({"--", "--stat", "--short", "-s", "--porcelain"})


def _real(path: str, cwd: str) -> str | None:
    try:
        return os.path.realpath(os.path.join(cwd, path))
    except (OSError, ValueError):
        return None  # not a path


def _glob_rx(pattern: str) -> re.Pattern:
    """A glob as a regular expression: ``**`` crosses folders, ``*`` and
    ``?`` stay inside one name, ``{a,b}`` is either, ``[...]`` any one
    character."""
    out: list[str] = []
    depth = i = 0
    while i < len(pattern):
        c = pattern[i]
        i += 1
        if pattern.startswith("**/", i - 1):
            out.append("(?:.*/)?")
            i += 2
        elif c == "*":
            out.append(".*" if pattern.startswith("*", i) else "[^/]*")
            i += pattern.startswith("*", i)
        elif c == "?":
            out.append("[^/]")
        elif c == "[" and "]" in pattern[i + 1:]:
            out.append("[^/]")
            i = pattern.index("]", i + 1) + 1
        elif c == "{":
            out.append("(?:")
            depth += 1
        elif c == "}" and depth:
            out.append(")")
            depth -= 1
        elif c == "," and depth:
            out.append("|")
        else:
            out.append(re.escape(c))
    return re.compile("".join(out) + ")" * depth + r"\Z", re.S)


class _Protected:
    """The two files of one project, those that exist."""

    def __init__(self, project_root: str):
        self.root = os.path.realpath(project_root)
        self.files = [os.path.realpath(os.path.join(project_root, rel))
                      for rel in (CONFIG_REL, SETTINGS_REL)
                      if os.path.lexists(os.path.join(project_root, rel))]

    def taken_by(self, target: str | None) -> str | None:
        """*target* when it is one of the files, or a folder above one
        inside the project; the project root and what is above it are not."""
        for f in self.files:
            if target == f or (target and f.startswith(target + "/")
                               and target.startswith(self.root + "/")):
                return target
        return None

    def matched_by(self, pattern: str, cwd: str, by_name: bool = False) -> str | None:
        """The file a glob matches, read from *cwd*.  The words before the
        first wildcard are a folder; the rest is matched against the file's
        path below it, and with *by_name* against its name alone."""
        parts = pattern.split("/")
        n = next((i for i, p in enumerate(parts) if _has_glob(p)), len(parts))
        base = _real("/".join(parts[:n]) or ("/" if pattern[:1] == "/" else "."), cwd)
        if n == len(parts):
            return self.taken_by(base)
        rx = _glob_rx("/".join(parts[n:]))
        for f in self.files:
            if base and (f.startswith(base + "/") or base == "/") and (
                    rx.match(f[len(base.rstrip("/")) + 1:])
                    or (by_name and rx.match(os.path.basename(f)))):
                return f
        return None

    def read_by(self, text: str, cwd: str) -> str | None:
        return (self.matched_by(text, cwd) if _has_glob(text)
                else self.taken_by(_real(text, cwd)))


def _search_reads(prot: _Protected, path, globs: list[str], cwd: str) -> bool:
    """A Grep call: its path, narrowed by its glob when it has one."""
    base = _real(path if isinstance(path, str) and path else ".", cwd)
    if not base or base in prot.files:
        return bool(base)
    # A glob that only excludes narrows nothing here.
    globs = [g for g in globs if not g.startswith("!")]
    if not globs:
        return bool(prot.taken_by(base))
    return any(prot.matched_by(g, base, by_name="/" not in g) for g in globs)


def _command_reads(prot: _Protected, command: str, cwd: str) -> bool:
    """A Bash command: a word, the target of an input redirect or a name
    inside a word that takes in one of the files, unless it is a write
    target of its own command (the allow-list decides that) or the command
    is git diff --stat or git status."""
    ecwd: str | None = cwd

    def reads(words: list[str]) -> bool:
        nonlocal ecwd
        while words and _ASSIGN_RE.match(words[0]):
            words = words[1:]
        if not words:
            return False
        name, args = os.path.basename(words[0]), words[1:]
        if name == "cd":
            exp = _expand_token(args[0]) if args else os.environ.get("HOME")
            ecwd = (None if exp is None or exp.startswith("-") or _has_glob(exp)
                    or (ecwd is None and not os.path.isabs(exp))
                else os.path.join(ecwd or "/", exp))
            return False
        if name in ("pushd", "popd"):
            ecwd = None
            return False
        hits: list[str] = []
        for word in args:
            exp = _expand_token(word) or word
            if ecwd is None and not os.path.isabs(exp):
                continue
            hit = prot.read_by(exp, ecwd or "/")
            if hit:
                hits.append(hit)
            pieces = [p for p in _PIECE_RE.split(exp) if p and p != exp]
            if any(_real(p, ecwd or "/") in prot.files for p in pieces
                   if ecwd is not None or os.path.isabs(p)):
                return not _git_quiet(name, args)
        if not hits or _git_quiet(name, args):
            return False
        written = _extract_bash_write_targets(
            " ".join(shlex.quote(w) for w in words), ecwd or "/") or []
        return any(h not in written for h in hits)

    cur: list[str] = []
    tokens = _words(command)
    for i, tok in enumerate(tokens):
        if tok == "<" and i + 1 < len(tokens):
            exp = _expand_token(tokens[i + 1]) or tokens[i + 1]
            if (ecwd is not None or os.path.isabs(exp)) and prot.read_by(
                    exp, ecwd or "/"):
                return True
        if not _is_punct(tok):
            # The target of a redirect is not a word of the command.
            if not (i and _is_punct(tokens[i - 1])
                    and ("<" in tokens[i - 1] or ">" in tokens[i - 1])):
                cur.append(tok)
        elif ">" not in tok and "<" not in tok:
            if reads(cur):
                return True
            cur = []
    return reads(cur)


def _git_quiet(name: str, args: list[str]) -> bool:
    if name != "git" or not args or args[0] not in ("diff", "status"):
        return False
    options = {a for a in args[1:] if a.startswith("-")}
    return options <= _GIT_QUIET and (args[0] == "status" or "--stat" in options)


def read_refusal(tool_name: str, tool_input: dict, project_root: str,
                 cwd: str) -> str:
    """Why a call is refused as a read of the settings file or of the
    held-out file, or ``""`` when its targets take neither in."""
    prot = _Protected(project_root)
    if not prot.files:
        return ""

    def text(key: str) -> str:
        value = tool_input.get(key)
        return value if isinstance(value, str) else ""

    if tool_name == "Read":
        reads = bool(text("file_path")
                     and prot.taken_by(_real(text("file_path"), cwd)))
    elif tool_name == "Grep":
        reads = _search_reads(prot, text("path"), text("glob").split(), cwd)
    elif tool_name == "Glob":
        base = _real(text("path") or ".", cwd)
        reads = bool(base and text("pattern")
                     and prot.matched_by(text("pattern"), base))
    elif tool_name == "Bash":
        reads = _command_reads(prot, text("command"), cwd)
    else:
        reads = False
    return READ_REFUSAL if reads else ""
