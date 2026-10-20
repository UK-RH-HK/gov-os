"""Second names of the settings file and of the held-out file, and the
calls the guard cannot read in bounded time (DEC-548, DEC-553, DEC-562).

Reads of the two files are open to every role (DEC-821 item 3, DEC-857
item 3).  A command that gives either file, a copy of one under another
folder, or a folder that holds one a second name (a move, a link, a
linking copy, an in-place edit with a backup) is refused to every role: a
second name can make a writable alias of a file the role may not write
(DEC-821 item 4).  A write to either file stays with the allow-list.  The
read rules of Policy 2 are ``gov.guard.reads``'s; the parsing they share
is here.

Nothing is listed or opened here: there are two known files, and the
question is whether a target takes one of them in.  No message of this
module carries a path.
"""

from __future__ import annotations

import os
import re

from gov.guard.decide import (LONG_REFUSAL, MOST_READ, _ASSIGN_RE, _copy_args,
                              _expand_token, _has_glob, _is_punct)
from gov.guard.heldout import CONFIG_REL, SETTINGS_REL, _words

SECOND_NAME_REFUSAL = ("the command gives the settings file or the held-out file, "
                       "a copy of one or a folder that holds one a second name (a "
                       "move, a link, a linking copy, an in-place edit with a "
                       "backup), which could make a writable alias of a file the "
                       "role may not write: refused to every role (DEC-548, "
                       "DEC-553, DEC-821 item 4); a plain copy is allowed")
NUL_REFUSAL = ("a NUL byte in a path or a command is refused to every role "
               "(DEC-562): no file has one in its name")
# The fields of a call that are read as a path, a glob or a command.
_FIELDS = {"Read": ("file_path",), "Grep": ("path", "glob"),
           "Glob": ("path", "pattern"), "Bash": ("command",)}
# What separates a file name from the text around it in one shell word: a
# script on the command line, <commit>:<file>, --option=<file>, @<file>.
_PIECE_RE = re.compile(r"""[\s'"()=:,;@]+""")
# A short option with its value glued to it: -f<file>.
_GLUED_RE = re.compile(r"-[A-Za-z].")
# The innermost braces of a word that hold a comma: {a,b}.
_BRACE_RE = re.compile(r"\{([^{},]*,[^{}]*)\}")
# The options with which grep searches a folder: -r, -R, a cluster, the long forms.
_RECURSIVE_RE = re.compile(r"-[A-Za-z0-9]*[rR]|--(dereference-)?recursive\Z")
# The options with which ls lists a folder and every folder below it.
_LS_RECURSIVE_RE = re.compile(r"-[A-Za-z0-9]*R|--recursive\Z")
# The options of grep and of rg that take the next word as their value.
_GREP_VALUED = frozenset(
    "-e -f -m -A -B -C -d -D --regexp --file --include --exclude --exclude-dir "
    "--exclude-from --max-count --context --after-context --before-context".split())
_RG_VALUED = frozenset(
    "-e -f -g -t -T -m -A -B -C -j -M -d -E --regexp --file --glob --iglob --type "
    "--type-not --type-add --max-count --context --after-context --before-context "
    "--threads --max-columns --max-depth --encoding --sort --sortr --color".split())
# The options that give the text to look for: no operand is that text then.
_PATTERN_OPTIONS = frozenset({"-e", "-f", "--regexp", "--file"})
# The tests of find on a file's name: a find that has one is not judged as
# a search of everything below its start.
_FIND_NAMED = frozenset({"-name", "-iname", "-path", "-ipath", "-wholename",
                         "-iwholename", "-regex", "-iregex", "-lname", "-ilname"})
# The most a search in the shell holds, its paths times what its name
# filters expand to, and the most words the brace expansions of one call
# make.  Each is matched, so the count bounds the time.
_MOST_PAIRS = 4096
# The most folders the paths resolved for one call hold together: a path is
# resolved once, and resolving one costs its folders (DEC-570).
_MOST_RESOLVED = 131072
# What stands before the command that is run and is not it (DEC-570): the
# keywords of the shell, and the commands that run the words after them.
_KEYWORDS = frozenset({"do", "then", "else", "elif", "if", "while", "until", "!"})
_PREFIXES = frozenset({"timeout", "command", "env", "nice", "nohup", "time"})
# What a word of a command starts after: a # there opens a comment.
_BEFORE_A_WORD = frozenset(" \t\n;&|()<>")
# The two files' project-relative paths, in parts.
_RELS = [rel.split("/") for rel in (CONFIG_REL, SETTINGS_REL)]


def _real(path: str, cwd: str) -> str | None:
    try:
        return os.path.realpath(os.path.join(cwd, path))
    except (OSError, ValueError):
        return None  # not a path


class _Glob:
    """A glob as a matcher of whole paths: ``**`` crosses folders, ``*`` and
    ``?`` stay inside one name, ``{a,b}`` is either, ``[...]`` any one
    character.

    The places of the path the pattern has reached are the bits of one
    number, and no place is tried twice: a match costs the length of the
    pattern, whatever stars it holds (DEC-562)."""

    def __init__(self, pattern: str):
        self.pattern = pattern

    def match(self, path: str) -> bool:
        pattern, n = self.pattern, len(path)
        at: dict[str, int] = {}  # a character -> the places where the path has it
        for k, c in enumerate(path):
            at[c] = at.get(c, 0) | 1 << k
        slash = at.get("/", 0)
        every = (1 << n + 1) - 1
        inside = (every >> 1) & ~slash  # the places of a character that is no slash
        last = pattern.rfind("]")
        groups: list[tuple[int, int]] = []  # open braces: where each began, what its alternatives reached
        cur, i = 1, 0
        while i < len(pattern) and (cur or groups):
            c = pattern[i]
            i += 1
            if pattern.startswith("**/", i - 1):
                cur |= (every & -(cur & -cur) & slash) << 1
                i += 2
            elif c == "*" and pattern.startswith("*", i):
                cur = every & -(cur & -cur)  # every place from the first one on
                i += 1
            elif c == "*":
                # The carry of the sum runs from a place to the end of its name.
                cur |= ((cur & inside) + inside) ^ inside
            elif c == "?" or (c == "[" and last > i):
                if c == "[":
                    i = pattern.index("]", i + 1) + 1
                cur = (cur & inside) << 1
            elif c == "{":
                groups.append((cur, 0))
            elif c == "}" and groups:
                cur |= groups.pop()[1]
            elif c == "," and groups:
                start, reached = groups[-1]
                groups[-1] = (start, reached | cur)
                cur = start
            else:
                cur = (cur & at.get(c, 0)) << 1
        for _, reached in groups:
            cur |= reached
        return bool(cur >> n & 1)


_glob_rx = _Glob  # the name the callers and the builder cases know


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


def _spans(command: str) -> list[tuple[int, int]]:
    """Where the commands inside a command's substitutions start and end:
    between backticks, and in ``$(...)``, ``<(...)`` and ``>(...)`` at any
    depth.  One that is not closed runs to the end."""
    ticks = [i for i, c in enumerate(command) if c == "`"]
    out = list(zip([t + 1 for t in ticks[::2]], ticks[1::2] + [len(command)]))
    stack: list[int | None] = []
    for i, c in enumerate(command):
        if c == "(":
            stack.append(i + 1 if i and command[i - 1] in "$<>" else None)
        elif c == ")" and stack:
            start = stack.pop()
            if start is not None:
                out.append((start, i))
    return out + [(s, len(command)) for s in stack if s is not None]


def _substitutions(command: str) -> list[str]:
    """The commands inside a command's substitutions."""
    return [command[start:end] for start, end in _spans(command)]


def _options(args: list[str], valued: frozenset) -> tuple[list[str], list[tuple[str, str]]]:
    """The operands of a command, and each of its options of *valued* with
    its value: glued to the option, after ``=``, or the next word.  After
    ``--`` every word is an operand."""
    operands: list[str] = []
    options: list[tuple[str, str]] = []
    i = 0
    while i < len(args):
        a = args[i]
        i += 1
        if a == "--":
            operands += args[i:]
            break
        if not a.startswith("-") or a == "-":
            operands.append(a)
            continue
        if a.startswith("--"):
            opt, eq, val = a.partition("=")
        else:
            # A cluster: the first letter that takes a value takes the rest.
            j = next((j for j in range(1, len(a)) if "-" + a[j] in valued), len(a))
            opt, val = "-" + a[j:j + 1], a[j + 1:]
            eq = val
        if opt in valued:
            if not eq and i < len(args):
                val = args[i]
                i += 1
            options.append((opt, val))
    return operands, options


def _shell_search(name: str, args: list[str],
                  named: bool) -> tuple[list[str], list[str], list[str]] | None:
    """The paths a search in the shell starts from, its name filters, and
    those of them read in any case of letter (DEC-557, DEC-562); ``None``
    for another command.  A search is a recursive grep, rg, a recursive ls,
    and a find unless the command holds a test on a name (*named*)."""
    globs: list[str] = []
    iglobs: list[str] = []
    if name == "grep" and any(_RECURSIVE_RE.match(a) for a in args):
        paths, options = _options(args, _GREP_VALUED)
        if _PATTERN_OPTIONS.isdisjoint(o for o, _ in options):
            paths = paths[1:]
        globs = [v for o, v in options if o == "--include"]
        # A star over everything in the folder, in its two plain spellings,
        # takes in the folders below it: the search starts at the folder.
        paths = ["." if p in ("*", "./*") else p for p in paths]
    elif name == "rg":
        paths, options = _options(args, _RG_VALUED)
        if _PATTERN_OPTIONS.isdisjoint(o for o, _ in options) and "--files" not in args:
            paths = paths[1:]
        globs = [v for o, v in options if o in ("-g", "--glob")]
        iglobs = [v for o, v in options if o == "--iglob"]
    elif name == "find" and not named:
        while args and args[0] in ("-H", "-L", "-P"):
            args = args[1:]
        n = next((i for i, a in enumerate(args) if a.startswith("-") or a == "!"),
                 len(args))
        paths = args[:n]
    elif name == "ls" and any(_LS_RECURSIVE_RE.match(a) for a in args):
        paths = [a for a in args if not a.startswith("-")]
    else:
        return None
    return paths or ["."], globs, iglobs


def _behind(words: list[str]) -> list[str]:
    """The command behind what stands before it (DEC-570): the keywords of
    the shell, assignments, and timeout <n>, command, env, nice, nice -n <n>,
    nohup and time, in any number and order."""
    i = 0
    while i < len(words):
        w = words[i]
        if w == "nice" and words[i + 1:i + 2] == ["-n"]:
            i += 3
        elif w == "timeout":
            i += 2
        elif w in _KEYWORDS or w in _PREFIXES or _ASSIGN_RE.match(w):
            i += 1
        else:
            break
    return words[i:]


def _uncommented(command: str) -> str:
    """*command* without its comments (DEC-570): each from a ``#`` that
    starts a word outside quotes to the end of its line.  A ``#`` inside a
    word opens none, nor does one inside a quote, closed or not."""
    if "#" not in command:
        return command
    out: list[str] = []
    quote, kept, i = "", 0, 0
    while i < len(command):
        c = command[i]
        if c == "\\" and quote != "'":
            i += 1  # the character after it is itself
        elif quote:
            quote = "" if c == quote else quote
        elif c in "'\"":
            quote = c
        elif c == "#" and (not i or command[i - 1] in _BEFORE_A_WORD):
            out.append(command[kept:i])
            end = command.find("\n", i)
            i = kept = len(command) if end < 0 else end
            continue
        i += 1
    return "".join(out) + command[kept:]


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
    """The words of a command whose files and folders get a second name
    (DEC-548, DEC-553): the
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
    if name in ("mv", "cp"):
        # DEC-778: read as the write rule reads it (DEC-765): an option's
        # value is a value, and nothing after "--" is an option.  A call
        # whose options cannot be read gives every word; with an option
        # after an operand, every operand but a last word that both
        # readings take as the destination.
        parsed = _copy_args(name, args)
        if parsed is None:
            return args
        operands, opts, after = parsed
        if name == "cp" and "l" not in opts:
            return []
        if "t" in opts or (after is not None and args[-1:] != operands[-1:]):
            return operands
        return operands[:-1]
    return []


class _Protected:
    """The two files of one project, those that exist."""

    def __init__(self, project_root: str):
        self.root = os.path.realpath(project_root)
        self.files = [os.path.realpath(os.path.join(project_root, rel))
                      for rel in (CONFIG_REL, SETTINGS_REL)
                      if os.path.lexists(os.path.join(project_root, rel))]
        self.long = False  # a command was found to hold more than is read
        self.made = 0  # the words the brace expansions made so far
        self.spent = 0  # the folders of the paths resolved so far
        self.seen: dict[tuple[str, str], str | None] = {}  # the paths resolved
        self.copies: dict[str | None, list[tuple[str, str]]] = {}  # per target

    def real(self, path: str, cwd: str) -> str | None:
        """``_real``, once for each path of a call (DEC-570).  A call whose
        paths hold more folders than the rule resolves is more than it
        reads: no further path is resolved, and the call is refused."""
        key = (path, cwd)
        if key not in self.seen:
            self.spent += path.count("/") + cwd.count("/") + 1
            self.long = self.long or self.spent > _MOST_RESOLVED
            self.seen[key] = None if self.long else _real(path, cwd)
        return self.seen[key]

    def braces(self, word: str) -> list[str]:
        """``_braces``; an expansion that stopped at its bound leaves words
        unexpanded, and the call is then more than the rule reads (DEC-570)."""
        ones = _braces(word)
        self.long = self.long or any(_BRACE_RE.search(w) for w in ones[1:])
        return ones

    def near(self, target: str | None) -> list[tuple[str, str]]:
        """The files *target* may take in, each with the folder that plays
        the project root's part for it: the project's, and the copies."""
        if target not in self.copies:
            self.copies[target] = _copies(target)  # looked for once
        return [(f, self.root) for f in self.files] + self.copies[target]

    def taken_by(self, target: str | None) -> str | None:
        """*target* when it is one of the files, or a folder above one
        inside the project; the project root and what is above it are not."""
        for f, root in self.near(target):
            if target == f or (target and f.startswith(target + "/")
                               and target.startswith(root + "/")):
                return target
        return None

    def matched_by(self, pattern: str, cwd: str, by_name: bool = False,
                   fold: bool = False) -> str | None:
        """The file a glob matches, read from *cwd*.  The words before the
        first wildcard are a folder; the rest is matched against the file's
        path below it, with *by_name* against its name alone, and with
        *fold* in any case of letter."""
        parts = pattern.split("/")
        n = next((i for i, p in enumerate(parts) if _has_glob(p)), len(parts))
        base = self.real("/".join(parts[:n]) or ("/" if pattern[:1] == "/" else "."), cwd)
        if n == len(parts):
            return self.taken_by(base)
        cased = str.lower if fold else str
        rx = _glob_rx(cased("/".join(parts[n:])))
        for f, _ in self.near(base):
            if base and (f.startswith(base + "/") or base == "/") and (
                    rx.match(cased(f[len(base.rstrip("/")) + 1:]))
                    or (by_name and rx.match(cased(os.path.basename(f))))):
                return f
        return None

    def read_by(self, text: str, cwd: str) -> str | None:
        return (self.matched_by(text, cwd) if _has_glob(text)
                else self.taken_by(self.real(text, cwd)))


def _gives_second_name(prot: _Protected, command: str, cwd: str) -> bool:
    """A Bash command that gives one of the files, a copy of one or a folder
    that holds one a second name (DEC-548, DEC-553, DEC-821 item 4); and,
    with ``prot.long`` set, one that holds more than the rule reads
    (DEC-562, DEC-570).  The command behind keywords of the shell and
    prefix commands is judged as the command it is."""
    ecwd: str | None = cwd

    def judge(words: list[str]) -> bool:
        nonlocal ecwd
        while words and _ASSIGN_RE.match(words[0]):
            words = words[1:]
        words = _behind(words)
        if not words:
            return False
        name, args = os.path.basename(words[0]), words[1:]
        if name in ("egrep", "fgrep"):
            name = "grep"  # DEC-570: judged as grep is
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
        # DEC-562: a search holds no more paths times name filters than the
        # rule reads in bounded time.
        search = _shell_search(name, args, named)
        if search and len(search[0]) * sum(
                len(prot.braces(g)) for g in search[1] + search[2]) > _MOST_PAIRS:
            prot.long = True
            return True
        second = _second_names(name, args)
        for word in args:
            exp = _expand_token(word) or word
            if ecwd is None and not os.path.isabs(exp):
                continue
            ones = prot.braces(exp)
            prot.made += len(ones) - 1
            if prot.made > _MOST_PAIRS:
                prot.long = True
                return True
            if word in second and any(prot.read_by(one, ecwd or "/") for one in ones):
                return True
        return False

    cur: list[str] = []
    tokens = _words(command)
    named = not _FIND_NAMED.isdisjoint(tokens)
    for i, tok in enumerate(tokens):
        if not _is_punct(tok):
            # The target of a redirect is not a word of the command.
            if not (i and _is_punct(tokens[i - 1])
                    and ("<" in tokens[i - 1] or ">" in tokens[i - 1])):
                cur.append(tok)
        elif ">" not in tok and "<" not in tok:
            if judge(cur):
                return True
            cur = []
    return judge(cur)


def read_refusal(tool_name: str, tool_input: dict, project_root: str,
                 cwd: str) -> str:
    """Why a call is refused for a second name of the settings file or of
    the held-out file, or ``""``.  A call the rule cannot judge is refused
    too: one with a NUL byte in a path or a command, and one whose command,
    substitutions, brace expansions or search hold more than the rule reads
    (DEC-562, DEC-570).  Reads of the two files are not refused (DEC-821)."""
    prot = _Protected(project_root)

    def text(key: str) -> str:
        value = tool_input.get(key)
        return value if isinstance(value, str) else ""

    if any("\x00" in text(key) for key in _FIELDS.get(tool_name, ())):
        return NUL_REFUSAL
    # Each substitution is read as a command of its own: what they hold
    # together is bounded, so that the answer comes in bounded time.
    spans = _spans(text("command")) if tool_name == "Bash" else []
    if sum(end - start for start, end in spans) > MOST_READ:
        return LONG_REFUSAL
    second = False
    if tool_name == "Grep":
        for glob in text("glob").split():
            prot.braces(glob)
    elif tool_name == "Glob":
        prot.braces(text("pattern"))
    elif tool_name == "Bash":
        # DEC-570: each is read as it is written, and without its comments.
        second = any(_gives_second_name(prot, c, cwd) for whole in
                     [text("command"), *(text("command")[start:end]
                                         for start, end in spans)]
                     for c in dict.fromkeys((whole, _uncommented(whole))))
    if prot.long:
        return LONG_REFUSAL
    return SECOND_NAME_REFUSAL if second else ""
