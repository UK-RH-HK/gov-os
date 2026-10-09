"""Reads of the settings file and of the held-out file (DEC-508, DEC-525).

The guard refuses any agent tool call whose file targets take in one of
the two files, for every role: the file named, a folder above it inside
the project, or a glob that matches it.  A write to either file is not a
read and stays with the allow-list.  A copy of either file under another
folder is refused as the file is, with that folder in the project root's
part, and so is a command that gives a file or a copy a second name
(DEC-548).

Nothing is listed or opened here: there are two known files, and the
question is whether a target takes one of them in.  No message of this
module carries a path.
"""

from __future__ import annotations

import os
import re
import shlex

from gov.guard.decide import (_ASSIGN_RE, _cp_operands, _expand_token,
                              _extract_bash_write_targets, _has_glob, _is_punct)
from gov.guard.heldout import CONFIG_REL, SETTINGS_REL, _words

READ_REFUSAL = ("the call reads the settings file or the held-out file, which "
                "is refused to every role (DEC-508, DEC-525); the registered "
                "hooks are listed by python3 -m gov.guard.hooks")
# What separates a file name from the text around it in one shell word: a
# script on the command line, <commit>:<file>, --option=<file>, @<file>.
_PIECE_RE = re.compile(r"""[\s'"()=:,;@]+""")
# A short option with its value glued to it: -f<file>.
_GLUED_RE = re.compile(r"-[A-Za-z].")
# The innermost braces of a word that hold a comma: {a,b}.
_BRACE_RE = re.compile(r"\{([^{}]*,[^{}]*)\}")
# The options with which grep searches a folder: -r, -R, a cluster, the long forms.
_RECURSIVE_RE = re.compile(r"-[A-Za-z]*[rR]|--(dereference-)?recursive\Z")
# The options with which git diff and git status print no line of a file.
_GIT_QUIET = frozenset({"--", "--stat", "--short", "-s", "--porcelain"})
# The two files' project-relative paths, in parts.
_RELS = [rel.split("/") for rel in (CONFIG_REL, SETTINGS_REL)]


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


def _braces(word: str) -> list[str]:
    """*word*, and after it the words a brace expansion makes of it."""
    out: list[str] = []
    todo = [word]
    while todo and len(out) + len(todo) <= 256:
        w = todo.pop()
        m = _BRACE_RE.search(w)
        if m:
            todo += [w[:m.start()] + alt + w[m.end():]
                     for alt in m.group(1).split(",")]
        else:
            out.append(w)
    return [word] + [w for w in out + todo if w != word]


def _substitutions(command: str) -> list[str]:
    """The commands inside a command's substitutions: between backticks,
    and in ``$(...)``, ``<(...)`` and ``>(...)`` at any depth.  One that is
    not closed runs to the end."""
    out = command.split("`")[1::2]
    stack: list[int | None] = []
    for i, c in enumerate(command):
        if c == "(":
            stack.append(i + 1 if i and command[i - 1] in "$<>" else None)
        elif c == ")" and stack:
            start = stack.pop()
            if start is not None:
                out.append(command[start:i])
    return out + [command[s:] for s in stack if s is not None]


def _takes_folder(name: str, args: list[str]) -> bool:
    """True for a listing or a recursive search that names no path: it
    takes in the folder it runs in."""
    plain = [a for a in args if not a.startswith("-")]
    if name == "ls":
        return not plain
    return len(plain) <= 1 and (name == "rg" or (
        name == "grep" and any(_RECURSIVE_RE.match(a) for a in args)))


def _copies(target: str | None) -> list[tuple[str, str]]:
    """The copies of the two files at or below *target*, each with its
    folder <P>: an existing file at <P>/<the file's project-relative path>,
    where *target* is <P>, a folder between the two, or the copy (DEC-548)."""
    parts = target.split("/") if target else []
    out: list[tuple[str, str]] = []
    for rel in (_RELS if parts else ()):
        for k in range(len(rel) + 1):
            f = "/".join(parts + rel[k:])
            if parts[len(parts) - k:] == rel[:k] and os.path.lexists(f):
                out.append((f, "/".join(parts[:len(parts) - k])))
    return out


def _second_names(name: str, args: list[str]) -> list[str]:
    """The words of a command whose files get a second name (DEC-548): the
    sources of a move, of a link and of a linking copy, and the files of an
    in-place edit that leaves a backup."""
    if name in ("ln", "link"):
        plain = [a for a in args if not a.startswith("-")]
        return plain[:-1] or plain
    if name == "sed":
        backup = any((a.startswith("-i") and len(a) > 2)
                     or a.startswith("--in-place=")
                     or (a == "-i" and b.startswith("."))
                     for a, b in zip(args, args[1:] + [""]))
        return args if backup else []
    short = "".join(a for a in args if a.startswith("-") and not a.startswith("--"))
    if name == "mv" or (name == "cp" and (
            "l" in short or any(a.startswith("--l") for a in args))):
        operands, dirs = _cp_operands(args) or ([], [])
        return operands if dirs else operands[:-1]
    return []


class _Protected:
    """The two files of one project, those that exist."""

    def __init__(self, project_root: str):
        self.root = os.path.realpath(project_root)
        self.files = [os.path.realpath(os.path.join(project_root, rel))
                      for rel in (CONFIG_REL, SETTINGS_REL)
                      if os.path.lexists(os.path.join(project_root, rel))]

    def near(self, target: str | None) -> list[tuple[str, str]]:
        """The files *target* may take in, each with the folder that plays
        the project root's part for it: the project's, and the copies."""
        return [(f, self.root) for f in self.files] + _copies(target)

    def holds(self, target: str | None) -> bool:
        """True when *target* is one of the files, or a copy of one."""
        return any(target == f for f, _ in self.near(target))

    def taken_by(self, target: str | None) -> str | None:
        """*target* when it is one of the files, or a folder above one
        inside the project; the project root and what is above it are not."""
        for f, root in self.near(target):
            if target == f or (target and f.startswith(target + "/")
                               and target.startswith(root + "/")):
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
        rest = "/".join(parts[n:])
        rx = _glob_rx(rest)
        for f, root in self.near(base):
            # From a copy's own <P>, wildcards alone select no file.
            if root == base != self.root and not rest.strip("*/"):
                continue
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
    if not base or prot.holds(base):
        return bool(base)
    # A glob that only excludes narrows nothing here.
    globs = [g for g in globs if not g.startswith("!")]
    if not globs:
        return bool(prot.taken_by(base))
    # A glob with no slash is a name at any depth, with or without a
    # wildcard; one that starts with a slash is read from the search's folder.
    return any(prot.matched_by(g, base, by_name="/" not in g)
               or prot.matched_by(g.lstrip("/"), base)
               or any(g == os.path.basename(f) and f.startswith(base + "/")
                      for f, _ in prot.near(base))
               for glob in globs for g in _braces(glob))


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
        if name in ("cd", "pushd"):
            while args and args[0].startswith("-") and args[0] != "-":
                args = args[1:]  # an option: -P, --
            exp = (_expand_token(args[0]) if args
                   else os.environ.get("HOME") if name == "cd" else None)
            ecwd = (None if exp is None or exp.startswith("-") or _has_glob(exp)
                    or (name == "pushd" and exp.startswith("+"))
                    or (ecwd is None and not os.path.isabs(exp))
                else os.path.join(ecwd or "/", exp))
            return False
        if name == "popd":
            ecwd = None
            return False
        if (ecwd is not None and _takes_folder(name, args)
                and prot.taken_by(_real(".", ecwd))):
            return True
        hits: list[str] = []
        second = _second_names(name, args)
        for word in args:
            exp = _expand_token(word) or word
            if ecwd is None and not os.path.isabs(exp):
                continue
            found = [hit for one in _braces(exp)
                     if (hit := prot.read_by(one, ecwd or "/"))]
            # DEC-548: a second name for a file is a read of it, also by a
            # role that may write it.
            if word in second and any(prot.holds(hit) for hit in found):
                return True
            hits += found
            pieces = [p for p in _PIECE_RE.split(exp) if p and p != exp]
            if _GLUED_RE.match(exp):
                pieces.append(exp[2:])
            if any(prot.holds(_real(p, ecwd or "/")) for p in pieces
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
        # An input redirect, alone or glued to what precedes it (";<", "<>");
        # "<<" and "<<<" open no file.
        if (_is_punct(tok) and i + 1 < len(tokens) and not tok.endswith("<<")
                and tok.endswith(("<", "<>"))):
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
                     and any(prot.matched_by(p, base)
                             for p in _braces(text("pattern"))))
    elif tool_name == "Bash":
        reads = any(_command_reads(prot, c, cwd) for c in
                    [text("command"), *_substitutions(text("command"))])
    else:
        reads = False
    return READ_REFUSAL if reads else ""
