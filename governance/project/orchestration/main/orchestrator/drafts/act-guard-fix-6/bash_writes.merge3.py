"""What a Bash command writes (W2-42a, DEC-1028 item 4, DEC-1040): ACT-GUARD-FIX-3's reviewed module, ported into
the product from the five-rule hook's ``.claude/hooks/bash_writes.py`` (df7be57c6bdd).

The product's write parser (``gov.guard.decide._extract_bash_write_targets``) reads a command through ``judge``:
what it enforces is ``Judgement.targets()``, the shell's own writes (``shell``), the writes the line parser does not
read (``writes``: git checkout, restore, rm and mv on paths, dd of=, truncate, sort -o, rsync, and the patch
appliers' unknown targets) and the runs of a heredoc's script it cannot read (``unread``). Code the product never
read (Python, perl, node, a program reading its standard input) stays opaque to it, as before; ``findings`` keep the
hook's reading of that code, so the hook can call this module in place of its own copy (a later ACT).

The line parser (``gov.guard.decide._line_write_targets``) reads one shell line. It does not know
heredocs (it reads a heredoc's body as shell commands), shell variables the command sets itself, the words a literal
``for`` loop gives a variable, or command substitutions inside double quotes. This module gives it the shell text
only, and judges the rest by what it is:

- a heredoc's body is cut out of the shell text and judged by what reads it: data for cat, tee, grep and the like
  (no write of its own; an unquoted body's substitutions are judged as commands), Python code for ``python3 -``
  (its own opens and calls that write), shell code for ``bash``/``sh`` (judged as a command), and anything else as
  code the guard cannot read;
- a variable the command sets once at its top level, before any use, to a value the guard can expand, is expanded;
  a ``for`` loop over literal words is judged once per word; a variable bound any other way is unresolvable;
- each command substitution, process substitution, ``sh -c`` string and ``eval`` is judged as a command of its own;
- inline Python (``python3 -c``) is read for its own writes: ``open`` in a write mode, the path methods and the
  ``os`` and ``shutil`` calls that write, and the commands it runs. A write whose target cannot be worked out, code
  that runs code (exec, eval, getattr, ...), and code the shell rewrites (``$VAR``) are "unresolvable".

Round 2 (the independent review's F1-F4): variables are expanded in source order; backslash-newline is removed before
the text is read; a data heredoc's body written to a file is judged as code whenever a later word may run that file
(bash name after a cd, ./name, chmod +x and the path, a loop variable, xargs, runpy, ...), and refused under rule 1
when the run cannot be read and the body names the tests; code that names the tests in any spelling and writes
through a path the guard cannot work out (a glob, listdir, walk, chdir or computed path) is refused.

Whatever the scan cannot read for certain (unbalanced quotes, an unterminated heredoc, ``<<`` in arithmetic, an
unknown reader) falls back to the judgement before this fix (fail closed). Nothing here runs the command.

ACT-GUARD-FIX-4 (DEC-1050 (8), (12)): the hook's rules 1 and 5 use only the targets this module resolves (an
unresolvable one is let through), and the module also lists what ``rm`` deletes (``Judgement.deletes``), for the
hook's refusal of the catastrophic deletes, and the folders ``mkdir`` makes (``Judgement.made``, for rule 5: a
reviewer may make its record folder); the reading itself is unchanged.
"""
import ast
import os
import re
import shlex
import warnings
from contextlib import contextmanager
from itertools import product

# The session's environment as the hook received it, before any judgement sets the command's own variables in it.
_SESSION_ENV = dict(os.environ)

ACCEPTANCE = "tests/acceptance/"
SENT = "/<guard-unresolvable>"  # gov.guard.decide._UNRESOLVABLE; checked equal by the hook
UNKNOWN = "/<guard-unknown-folder>"  # the folder of a command whose shell folder the guard cannot place
MOST_DEPTH = 4                  # nested substitutions, sh -c strings and subprocess commands judged
MOST_VARIANTS = 64              # the parses one command may take (literal for-loop words)
MOST_WORDS = 32                 # the words of one literal for loop that are judged one by one

_PUNCT = "();<>|&\n"
_ASSIGN = re.compile(r"^([A-Za-z_]\w*)=(.*)$", re.S)
_NAME_USE = r"\$(?:{0}\b|{{{0}[}}:#%/^,@\[*?+=-])"
_EXPANSION = re.compile(r"(?<!\\)\$[A-Za-z_{(]|(?<!\\)`")
_PY = re.compile(r"python[\d.]*$")
_SHELLS = ("sh", "bash", "dash", "zsh", "ksh")
# Readers of a heredoc that take it as data: nothing in it is run or names a file they open.
_DATA = frozenset("cat tee head tail wc sort uniq cut tr grep egrep fgrep rg jq column base64 md5sum sha1sum "
                  "sha256sum diff cmp true :".split())
# The product's (W2-42a): programs that take a heredoc as data beside those, whose input runs nothing (a commit
# message, a ticket's text, a filter's input). git apply and git am read a patch: KPI 5's unknown targets instead.
_PRODUCT_DATA = _DATA | frozenset("git tk gh yq nl fold fmt paste comm join iconv xxd od less more tac rev "
                                  "expand unexpand".split())
_OPENS = ("{", "(", "!", "if", "then", "else", "elif", "do", "while", "until", "time")
_STARTS = frozenset(("if", "while", "until", "for", "case", "{", "("))
_ENDS = frozenset(("fi", "done", "esac", "}", ")"))
_A_PATH = re.compile(r"[^\s'\"]*tests/acceptance(/[^\s'\"]*)?")
_ARITH = re.compile(r"\$\(\(([A-Za-z0-9_\s+\-*%$]*)\)\)")
_INLINE = re.compile(r"\b(python3?|perl|node|ruby)\s+(-\w*\s+)*-[cei]\b")


class Unreadable(Exception):
    """The scan cannot read the command for certain: the caller judges it as before this fix."""


class UnclosedQuote(Unreadable):
    """A quote the scan finds open outside every comment (DEC-1174 (1)): a reader blind to comments may pair it with
    a comment's apostrophe, so the caller is not to take such a reading for a free one."""


# A comment holding a quote: where the scan cannot read a command, a reader blind to comments may pair that quote
# with another and hide the text between them (DEC-1174 (1)).
COMMENT_QUOTE = re.compile(r"(?:^|[\s;&|(])#[^\n]*['\"`]")


# Code that names the acceptance tests' folder in any spelling an honest script uses: 'tests/acceptance' with or
# without the slash, 'tests', 'acceptance' as separate pieces (os.path.join, Path / ..., '/'.join, %), or a glob.
_CODE_NAMES = re.compile(r"tests\b.{0,40}?accept|ests/accept", re.S)


def names_tests(scope, code=False):
    """Whether ``scope`` names the acceptance tests: the folder with its slash for a shell command (as before), and
    any spelling of it for code (ACT-GUARD-FIX-3 round 2, F4: Python, perl or node code, or a script body)."""
    return ACCEPTANCE in scope or (code and bool(_CODE_NAMES.search(scope)))


def joined(command):
    """``command`` with each backslash-newline removed (round 2, F3), for the checks that read its text whole. Inside
    single quotes the shell keeps them; removing them there too only makes the text name more, never less."""
    return command.replace("\\\n", "")


# -- the shell text: heredocs and substitutions out --------------------------------------------------------------

def _here_word_end(command, i):
    """Where the word that starts at ``i`` ends, as the shell reads it: quotes, escapes, ``$(...)``, backticks and
    ``${...}`` inside it are part of it; an unquoted blank, newline, ``;&|()<>`` ends it. Raises Unreadable when a
    quote or a substitution in it does not close."""
    n, k, stack = len(command), i, []  # stack: '"', ["$(", depth], ["${", 0], or "`"
    while k < n:
        ch = command[k]
        top = stack[-1] if stack else None
        if top is None and ch in " \t\n;&|()<>":
            break
        if ch == "\\":
            k += 2
            continue
        if ch == "'" and top != '"':
            end = command.find("'", k + 1)
            if end < 0:
                raise UnclosedQuote("an unclosed single quote")
            k = end + 1
            continue
        if top == "`":
            if ch == "`":
                stack.pop()
            k += 1
            continue
        if top == '"' and ch == '"':
            stack.pop()
            k += 1
            continue
        if ch == '"':
            stack.append('"')
        elif ch == "`":
            stack.append("`")
        elif command.startswith("${", k):
            stack.append(["${", 0])
            k += 1
        elif command.startswith("$(", k):
            stack.append(["$(", 0])
            k += 1
        elif isinstance(top, list) and top[0] == "$(" and ch in "()":
            if ch == "(":
                top[1] += 1
            elif top[1]:
                top[1] -= 1
            else:
                stack.pop()
        elif isinstance(top, list) and top[0] == "${" and ch == "}":
            stack.pop()
        k += 1
    if stack:
        raise UnclosedQuote("an unclosed quote or substitution in a here-string's word")
    return k


def _here_text(word):
    """The text of a here-string's ``word`` after quote removal, and whether the shell expands it first (an unquoted
    or double-quoted ``$`` or backtick: then the text is not known, and the word's own characters are kept)."""
    out, i, n, expanded = [], 0, len(word), False
    while i < n:
        ch = word[i]
        if ch == "\\":
            if word.startswith("\\\n", i):
                i += 2
            else:
                out.append(word[i + 1:i + 2])
                i += 2
            continue
        if ch == "'":
            end = word.find("'", i + 1)
            out.append(word[i + 1:end])
            i = end + 1
            continue
        if ch == '"':
            i += 1
            while i < n and word[i] != '"':
                if word[i] == "\\" and i + 1 < n and word[i + 1] in '"\\$`\n':
                    if word[i + 1] != "\n":
                        out.append(word[i + 1])
                    i += 2
                    continue
                if word[i] in "$`":
                    expanded = True
                out.append(word[i])
                i += 1
            i += 1
            continue
        if ch in "$`":
            expanded = True
        out.append(ch)
        i += 1
    if expanded and ("$(" in word or "`" in word):
        return word, True  # the substitutions are judged as the commands they are: their own quoting, kept
    return "".join(out), expanded


def heredocs(command, comments=None, legacy=False, hstr=False, lenient=False):
    """``command`` without its heredoc bodies and its comments, and the bodies. Each heredoc operator and its
    delimiter become ``< __gov_hdl_<k>__`` (an input redirect the parser skips), so the reader is known by position.
    A comment's text (a ``#`` that starts a word, outside quotes, to the end of its line) is dropped, so a quote in it
    is no quote (DEC-1174 (1)); its span is added to ``comments`` when a list is given. Raises Unreadable for
    anything the scan cannot read for certain. ``legacy``: ``${`` is not followed, so a ``#`` inside it may start a
    comment, as the scan read it before APOS-3 (judge's fail-closed second reading only). ``hstr`` (judge's
    fail-closed reading, R3, DEC-1164 (18)): a here-string is a heredoc of its own text, so the reader that runs it
    judges it as it judges a body (``bash <<< 'touch x'``, ``xargs touch <<< x``); its body is marked ``hs`` and,
    when the shell expands the word first, not quoted. ``lenient`` (the same): as bash reads it, a heredoc with no end
    line takes the rest of the text as its body, and one at the end of the text an empty one."""
    out, bodies, pending = [], [], []
    # The shell's contexts: "top"; '"' (double quotes); "$(" (a command substitution, whose quoting starts
    # afresh, with the depth of its own parentheses); "`" (a backtick substitution); "((" (arithmetic); "${" (a
    # parameter expansion, quoted or not: a # in it starts no comment, the first plain } closes it, a nested ${
    # nests, quotes pair as outside it, and a << in it is text; APOS-3, DEC-1174 (1)).
    stack = [["top", 0]]
    i, n = 0, len(command)
    while i < n:
        c = command[i]
        ctx = stack[-1]
        if command.startswith("\\\n", i):
            # A line continuation (ACT-GUARD-FIX-3 round 2, F3): the shell removes backslash-newline outside single
            # quotes, so "cp /tmp/x \<newline> tests/..." is one command with both words.
            i += 2
            continue
        if c == "\\" and i + 1 < n:
            out.append(command[i:i + 2])
            i += 2
            continue
        if ctx[0] == '"':
            if c == '"':
                stack.pop()
            elif not legacy and command.startswith("${", i):
                stack.append(["${", 0])
                out.append("${")
                i += 2
                continue
            elif command.startswith("$((", i):
                stack.append(["((", 0])
                out.append("$((")
                i += 3
                continue
            elif command.startswith("$(", i):
                stack.append(["$(", 0])
                out.append("$(")
                i += 2
                continue
            elif c == "`":
                stack.append(["`", 0])
            out.append(c)
            i += 1
            continue
        if ctx[0] == "((":
            if c == "(":
                ctx[1] += 1
            elif c == ")":
                if ctx[1]:
                    ctx[1] -= 1
                elif command.startswith("))", i):
                    stack.pop()
                    out.append("))")
                    i += 2
                    continue
                else:
                    raise Unreadable("an arithmetic expansion the scan cannot close")
            out.append(c)
            i += 1
            continue
        # Unquoted text: at the top, in $( ) or in backticks.
        if c == "'":
            end = command.find("'", i + 1)
            if end < 0:
                raise UnclosedQuote("an unclosed single quote")
            out.append(command[i:end + 1])
            i = end + 1
            continue
        if c == '"':
            stack.append(['"', 0])
            out.append(c)
            i += 1
            continue
        if command.startswith("$((", i):
            stack.append(["((", 0])
            out.append("$((")
            i += 3
            continue
        if command.startswith("$(", i):
            stack.append(["$(", 0])
            out.append("$(")
            i += 2
            continue
        if not legacy and command.startswith("${", i):
            stack.append(["${", 0])
            out.append("${")
            i += 2
            continue
        if c == "`":
            if ctx[0] == "`":
                stack.pop()
            else:
                stack.append(["`", 0])
            out.append(c)
            i += 1
            continue
        if ctx[0] == "$(" and c in "()":
            if c == "(":
                ctx[1] += 1
            elif ctx[1]:
                ctx[1] -= 1
            else:
                stack.pop()
            out.append(c)
            i += 1
            continue
        if ctx[0] == "${":
            if c == "}":
                stack.pop()
            elif c == "\n" and pending:
                raise Unreadable("a heredoc's body after a line ending inside ${...}")
            out.append(c)  # a #, a parenthesis or << here is text to bash
            i += 1
            continue
        if command.startswith("<<<", i):
            # A here-string (APOS-4, DEC-1174 (1)): its word is read as any word, not taken for a heredoc's delimiter.
            if hstr:
                j = i + 3
                while j < n and command[j] in " \t":
                    j += 1
                k = _here_word_end(command, j)
                if k == j:
                    raise Unreadable("a here-string without a word")
                text, expanded = _here_text(command[j:k])
                body = {"text": text, "quoted": not expanded, "span": (i, k), "hs": True}
                pending.append((None, False, not expanded, len(bodies) + len(pending), body))
                out.append(f" < __gov_hdl_{pending[-1][3]}__ ")
                i = k
                continue
            out.append("<<<")
            i += 3
            continue
        if c == "#" and (not out or (out[-1][-1:] in " \t\n;&|(" and out[-1][:1] != "\\")):
            # A comment: the # starts a word (after a blank or an operator that is not escaped: "x\ #y" and "a\;#b"
            # are one word to bash). Its text is dropped; a quote in it is no quote (DEC-1174 (1)).
            end = command.find("\n", i)
            end = n if end < 0 else end
            if comments is not None:
                comments.append((i, end))
            i = end
            continue
        if command.startswith("<<", i):
            line = "".join(out).rsplit("\n", 1)[-1]
            if "((" in line or "$[" in line:
                raise Unreadable("<< in arithmetic")
            j = i + 2
            strip = j < n and command[j] == "-"
            j += strip
            while j < n and command[j] in " \t":
                j += 1
            word, quoted, k = [], False, j
            while k < n and command[k] not in " \t\n;&|()<>":
                ch = command[k]
                if ch in "'\"":
                    end = command.find(ch, k + 1)
                    if end < 0:
                        raise Unreadable("unclosed quote in a heredoc delimiter")
                    word.append(command[k + 1:end])
                    quoted, k = True, end + 1
                elif ch == "\\":
                    word.append(command[k + 1:k + 2])
                    quoted, k = True, k + 2
                elif ch in "$`":
                    raise Unreadable("an expanded heredoc delimiter")
                else:
                    word.append(ch)
                    k += 1
            delim = "".join(word)
            if not delim:
                raise Unreadable("a heredoc without a delimiter")
            pending.append((delim, strip, quoted, len(bodies) + len(pending), None))
            out.append(f" < __gov_hdl_{pending[-1][3]}__ ")
            i = k
            continue
        if c == "\n" and pending:
            out.append("\n")
            i += 1
            for delim, strip, quoted, _, inline in pending:
                if inline is not None:
                    bodies.append(inline)
                    continue
                start, lines = i, []
                while True:
                    if i >= n:
                        if lenient:
                            break  # bash takes the rest of the text as the body
                        raise Unreadable("an unterminated heredoc")
                    e = command.find("\n", i)
                    line = command[i:n if e < 0 else e]
                    i = n if e < 0 else e + 1
                    if (line.lstrip("\t") if strip else line) == delim:
                        break
                    lines.append(line)
                bodies.append({"text": "\n".join(lines), "quoted": quoted, "span": (start, i)})
            pending = []
            continue
        out.append(c)
        i += 1
    if any(ctx[0] in ('"', "`", "${") for ctx in stack):
        # An unclosed ${ too: bash runs nothing of a line it cannot close (APOS-3).
        raise UnclosedQuote("an unclosed double quote, backtick or ${")
    if len(stack) > 1:
        raise Unreadable("unbalanced quotes or a heredoc with no body")
    for delim, strip, quoted, _, inline in pending:
        if inline is not None:
            bodies.append(inline)
        elif lenient:
            bodies.append({"text": "", "quoted": quoted, "span": (n, n)})
        else:
            raise Unreadable("unbalanced quotes or a heredoc with no body")
    return "".join(out), bodies


# Readers that take a here-string's text as data whatever it is, and never run it (DEC-1164 (18), R3 F1): the shell's
# own read builtins, and the filters whose script, when it has one, is read below (sed, awk) or none (bc).
_HS_READ = frozenset(("read", "mapfile", "readarray", "bc"))
# Commands that read their standard input as commands or code: a loop whose body holds one runs the loop's here-string.
_STDIN_RUNNERS = frozenset(("xargs", "parallel", "source", ".", "eval", "perl", "node", "ruby", "php"))


def _sed_reads_only(args):
    """Whether the ``sed`` words (after its name) are a script that only edits its input: no -i, no script file, no
    ``w``, ``W`` or ``e`` command and no flag ``w`` or ``e`` on an ``s``. Anything not understood: not."""
    scripts, positional, i = [], [], 0
    while i < len(args):
        a = args[i]
        if a == "--":
            positional += args[i + 1:]
            break
        if a.startswith("--"):
            if a in ("--quiet", "--silent", "--regexp-extended", "--posix", "--separate", "--null-data",
                     "--unbuffered", "--sandbox"):
                i += 1
            elif a == "--expression" and i + 1 < len(args):
                scripts.append(args[i + 1])
                i += 2
            elif a.startswith("--expression="):
                scripts.append(a.split("=", 1)[1])
                i += 1
            else:
                return False
            continue
        if a.startswith("-") and len(a) > 1:
            letters = a[1:]
            ends_e = letters.endswith("e")
            if not set(letters[:-1] if ends_e else letters) <= set("nErsuz"):
                return False
            if ends_e:
                if i + 1 >= len(args):
                    return False
                scripts.append(args[i + 1])
                i += 2
            else:
                i += 1
            continue
        positional.append(a)
        i += 1
    if not scripts:
        if not positional:
            return False
        scripts = positional[:1]
    return all(_sed_script_reads_only(s) for s in scripts)


def _sed_script_reads_only(script):
    """Scans a sed script command by command; True only when every command is one that writes no file and runs
    nothing."""
    i, n = 0, len(script)
    while i < n:
        c = script[i]
        if c in " \t\n;{}!":
            i += 1
            continue
        if c.isdigit() or c in ",$~+":
            i += 1
            continue
        if c == "\\" and i + 1 < n:  # an address /re/ with its own delimiter: \cREc
            i = _skip_delimited(script, i + 2, script[i + 1])
            if i < 0:
                return False
            continue
        if c == "/":
            i = _skip_delimited(script, i + 1, "/")
            if i < 0:
                return False
            while i < n and script[i] in "IM":
                i += 1
            continue
        if c in "sy" and i + 1 < n:
            delim = script[i + 1]
            if delim in " \t\n\\;":
                return False
            i = _skip_delimited(script, i + 2, delim)
            i = _skip_delimited(script, i, delim) if i >= 0 else -1
            if i < 0:
                return False
            start = i
            while i < n and script[i] not in ";}\n \t#":
                i += 1
            flags = script[start:i]
            if c == "y" and flags or not set(flags) <= set("gpiImM0123456789"):
                return False  # a w or e flag, or one not known
            continue
        if c in "pdqQnNgGhHxlP=D":
            i += 1
            continue
        if c in "aic":  # the rest of the line is text
            end = script.find("\n", i)
            i = n if end < 0 else end
            continue
        return False  # w, W, e, r, R, b, t, T, labels, comments and the rest
    return True


def _skip_delimited(text, i, delim):
    """The index after the next unescaped ``delim`` in ``text`` from ``i``, or -1."""
    n = len(text)
    while i < n:
        if text[i] == "\\":
            i += 2
            continue
        if text[i] == delim:
            return i + 1
        i += 1
    return -1


def _awk_reads_only(args):
    """Whether the ``awk`` words only compute on their input: no program file, in-place include, ``system(``,
    ``getline`` from a command, redirect or pipe (any ``>``, ``|`` or ``system`` in a word: not known to be free)."""
    for a in args:
        if a in ("-f", "--file", "-i", "--include", "-l", "--load", "-E", "--exec") or a.startswith(("-f", "--file=")):
            return False
        if re.search(r"system|[>|]|inplace|getline|\bclose\b|fflush", a):
            return False
    return True


def _hs_data(words, loop_ok):
    """Whether the command ``words`` takes a here-string's text as data (DEC-1164 (18), R3 F1): ``_kind`` says data;
    or it is ``read``, ``mapfile``, ``readarray`` or ``bc``; or ``sed`` or ``awk`` with a script that writes nothing
    and runs nothing; or ``done`` ending a loop none of whose commands reads its input as code (the loop's body is
    judged by its own words)."""
    if _kind(words) == "data":
        return True
    head = lead(words)
    if not head:
        return False
    name = os.path.basename(head[0])
    if name in _HS_READ:
        return True
    if name == "sed":
        return _sed_reads_only(head[1:])
    if name in ("awk", "gawk", "mawk"):
        return _awk_reads_only(head[1:])
    return words == ["done"] and loop_ok


def _runs_stdin(words):
    head = lead(words)
    return bool(head) and (_kind(words) in ("shell", "python") or os.path.basename(head[0]) in _STDIN_RUNNERS)


def _read_bound(cmds):
    """The variables ``read`` binds in the simple commands ``cmds`` (the words that are no option, an ``-a`` array,
    REPLY when it names none). A here-string is data to ``read``, but what it binds may be run as a command later
    (DEC-1164 (18), R3 F1 second batch)."""
    out = set()
    for words, _, _ in cmds:
        head = lead(words)
        if not head or os.path.basename(head[0]) != "read":
            continue
        args, i, bound = head[1:], 0, []
        while i < len(args):
            a = args[i]
            i += 1
            if a == "--":
                bound += args[i:]
                break
            if len(a) > 1 and a[0] == "-":
                k = next((k for k, ch in enumerate(a) if k and ch in "adinNptu"), None)
                if k is not None:  # the option's value: the rest of the word, or the next word
                    value = a[k + 1:]
                    if not value and i < len(args):
                        value, i = args[i], i + 1
                    if a[k] == "a":
                        bound.append(value)
            else:
                bound.append(a)
        out |= {m.group(0) for w in bound or ["REPLY"] for m in [re.match(r"[A-Za-z_]\w*", w)] if m}
    return out


def _uses_var(word, names):
    """Whether ``word`` expands one of the variables ``names``."""
    return any(re.search(_NAME_USE.format(re.escape(n)), word) for n in names)


# Programs that run a command given in their words: a variable there may name the command that runs.
_RUN_WRAPPERS = frozenset("xargs sudo doas parallel watch stdbuf setsid chrt ionice taskset strace ltrace".split())


def _check_here_strings(cmds):
    """Raises Unreadable when a here-string's text reaches, by its own command or through a pipe, a command that
    may run it (``bash <<< ...``, ``cat <<< ... | sh``, an unknown program): such a call is read as it was before
    here-strings were read (APOS-4, DEC-1174 (1)); a here-string only data readers take is read."""
    loop_ok = not any(_runs_stdin(words) for words, _, _ in cmds)
    stage, at = [], None
    for words, reds, sep in cmds:
        stage.append(words)
        if at is None and any(op == "<<<" for op, _ in reds):
            at = len(stage) - 1
        if sep not in ("|", "|&"):
            if at is not None and not all(_hs_data(w, loop_ok) for w in stage[at:]):
                raise Unreadable("a here-string a command may run")
            stage, at = [], None


def comment_spans(command, depth=0):
    """Where a shell reads comment text in ``command`` (DEC-1174 (1)): the (start, end) of each comment in its own
    text and, within the bodies of the heredocs a shell reads as commands (``bash <<EOF``, ``cat <<EOF | sh``), in
    theirs, as offsets into ``command``. A body any other program reads (Python, data) holds none. Raises Unreadable
    for anything the scan cannot read for certain."""
    found = []
    text, bodies = heredocs(command, found)
    if "<<<" in text:
        _check_here_strings(simples(tokens(lift(text)[0])))
    if not bodies or depth >= MOST_DEPTH:
        return found  # a body deeper than the guard reads keeps its text: read as before (fail closed)
    lifted, _ = lift(text)
    stage, at = [], []
    for words, reds, sep in simples(tokens(lifted)):
        stage.append(_kind(words))
        at += [(int(m), len(stage) - 1) for r in reds for m in re.findall(r"^__gov_hdl_(\d+)__$", r[1])]
        if sep not in ("|", "|&"):
            for k, i in at:
                runs = [kind for kind in stage[i:] if kind != "data"]
                if runs == ["shell"] and k < len(bodies):
                    s = bodies[k]["span"][0]
                    found += [(s + a, s + b) for a, b in comment_spans(bodies[k]["text"], depth + 1)]
            stage, at = [], []
    return sorted(found)


def spans(command):
    """Where the commands inside substitutions start and end: backticks, and ``$(`` ``<(`` ``>(`` at any depth (as
    gov.guard.protected._spans); each outermost one with its kind."""
    ticks = [i for i, c in enumerate(command) if c == "`" and (i == 0 or command[i - 1] != "\\")]
    found = [(a - 1, b + 1, a, b) for a, b in zip([t + 1 for t in ticks[::2]], ticks[1::2])]
    if len(ticks) % 2:
        raise Unreadable("an unclosed backtick")
    stack = []
    for i, c in enumerate(command):
        if c == "(":
            stack.append(i + 1 if i and command[i - 1] in "$<>" else None)
        elif c == ")" and stack:
            s = stack.pop()
            if s is not None:
                found.append((s - 2, i + 1, s, i))
    if any(s is not None for s in stack):
        raise Unreadable("an unclosed substitution")
    outer, last = [], -1
    for a, b, s, e in sorted(found):
        if a >= last:
            outer.append((a, b, s, e))
            last = b
    return outer


def lift(text):
    """``text`` with each outermost substitution replaced by a marker word, and the commands they hold. A command
    or backtick substitution becomes a word holding a backtick (unresolvable as a write target); a process
    substitution an input redirect from a marker (it is a pipe, not a file the command writes)."""
    subs, out, at = [], [], 0
    for a, b, s, e in spans(text):
        out.append(text[at:a])
        k = len(subs)
        subs.append(text[s:e])
        out.append(f" < __gov_sub_{k}__ " if text[a] in "<>" else f"`__gov_sub_{k}__`")
        at = b
    out.append(text[at:])
    return "".join(out), subs


def tokens(text):
    lex = shlex.shlex(text, posix=True, punctuation_chars=_PUNCT)
    lex.whitespace_split = True
    lex.whitespace = " \t\r"
    lex.commenters = ""
    try:
        return list(lex)
    except ValueError:
        raise Unreadable("unbalanced quotes") from None


def simples(toks):
    """The simple commands: (words, redirect targets, the separator after it)."""
    out, words, reds = [], [], []
    i = 0
    while i < len(toks):
        t = toks[i]
        if t and all(c in _PUNCT for c in t):
            if ("<" in t or ">" in t) and i + 1 < len(toks) and not all(c in _PUNCT for c in toks[i + 1]):
                if words and words[-1].isdigit():
                    words.pop()
                reds.append((t, toks[i + 1]))
                i += 2
                continue
            if "<" in t or ">" in t:
                i += 1
                continue
            out.append((words, reds, t))
            words, reds = [], []
            i += 1
            continue
        words.append(t)
        i += 1
    out.append((words, reds, ""))
    return out


def _short(word, letter):
    """A short option cluster holding ``letter`` (-c, -ec, -xc)."""
    return word.startswith("-") and not word.startswith("--") and letter in word[1:]


def parser_text(text):
    """``text`` as the product's parser is to read it: the same tokens, with a ``;`` after the shell keywords and
    the prefixes that run a command (do, then, if, !, {, time, timeout 60, env -i, nohup, ...), which the parser
    takes for the command's name; so ``do touch x`` is read as ``touch x``."""
    toks = tokens(text)
    out, words, start = [], [], 0

    def flush():
        cut = len(words) - len(lead([w for w, _ in words]))
        if cut and any(not _ASSIGN.match(w) for w, _ in words[:cut]) and cut < len(words):
            out.insert(words[cut][1], ";")

    i = 0
    while i < len(toks):
        t = toks[i]
        if t and all(c in _PUNCT for c in t):
            if ("<" in t or ">" in t) and i + 1 < len(toks) and not all(c in _PUNCT for c in toks[i + 1]):
                out += [t, shlex.quote(toks[i + 1])]
                i += 2
                continue
            if not ("<" in t or ">" in t):
                flush()
                words = []
            out.append(t)
            i += 1
            continue
        words.append((t, len(out)))
        out.append(shlex.quote(t))
        i += 1
    flush()
    return " ".join(out)


def lead(words):
    """The command behind assignments, keywords and the prefixes that run it (env, timeout, nice, nohup, ...)."""
    i = 0
    while i < len(words):
        w = words[i]
        if _ASSIGN.match(w) or w in _OPENS or w in ("command", "nohup", "exec", "builtin"):
            i += 1
        elif w == "env":
            i += 1
            while i < len(words) and (words[i].startswith("-") or _ASSIGN.match(words[i])):
                i += 2 if words[i] in ("-u", "-C", "-S") else 1
        elif w == "timeout":
            i += 1
            while i < len(words) and words[i].startswith("-"):
                i += 2 if words[i] in ("-s", "-k") else 1
            i += 1
        elif w == "nice":
            i += 3 if words[i + 1:i + 2] == ["-n"] else 1
        elif w in ("stdbuf", "setsid", "chrt", "ionice", "taskset"):
            return []  # options of their own: not read here
        else:
            break
    return words[i:]


# -- shell variables the command sets itself ---------------------------------------------------------------------

def variants(text, expand):
    """The environments to parse ``text`` under: each variable set once at the top level, before any use, to a
    value ``expand`` resolves; the words of each literal ``for`` loop; every other variable the command binds is
    dropped (unresolvable). Returns ({name: value}, {loop variable: [words]}, names to drop)."""
    cmds = simples(tokens(text))
    depth, sets, loops, bare = 0, [], {}, {}
    pos, opaque, before = 0, False, ""
    for whole_words, _, sep in cmds:
        pos += 1
        # The keywords before a command (then, do, else, !, {) are not part of it: "then B=x" assigns B. An
        # opening one (if, while, until, {), and for and case, puts what follows inside.
        k = 0
        while k < len(whole_words) and whole_words[k] in _OPENS:
            depth += whole_words[k] in _STARTS
            k += 1
        words = whole_words[k:]
        head = lead(words)
        first = words[0] if words else ""
        if first in ("for", "case"):
            depth += 1
        if head and os.path.basename(head[0]) in ("source", ".", "eval"):
            opaque = True  # may set any variable
        if words and all(_ASSIGN.match(w) for w in words):
            # In a pipeline or in the background the assignment is a subshell's: not the command's own.
            alone = before not in ("|", "|&", "&") and sep not in ("|", "|&", "&")
            for w in words:
                m = _ASSIGN.match(w)
                sets.append((m.group(1), m.group(2), depth if alone else -1, pos))
        elif first in ("export", "readonly", "declare", "typeset", "local"):
            for w in words[1:]:
                m = _ASSIGN.match(w)
                name = m.group(1) if m else w
                (sets.append((name, m.group(2), depth if first == "export" else -1, pos)) if m
                 else bare.setdefault(name, pos))
        elif first == "for" and len(words) >= 2:
            vals = words[3:] if words[2:3] == ["in"] else None
            loops.setdefault(words[1], []).append((vals, pos))
        else:
            for w in (head[1:] if head else words):
                if re.fullmatch(r"[A-Za-z_]\w*", w):
                    bare.setdefault(w, pos)
        before = sep
        if first in _ENDS or (sep == ")"):
            depth = max(0, depth - 1)
        if sep == "(":
            depth += 1
    # In source order (ACT-GUARD-FIX-3 round 2, F1): a value may use a variable set before it (T=/tmp; H=$T/p), so
    # each is expanded after the ones it can use, and the result never depends on the process's hash seed.
    names = list(dict.fromkeys(name for _, name in sorted(
        [(s[3], s[0]) for s in sets] + [(p, name) for name, l in loops.items() for _, p in l])))
    uses = {}
    for name in names:
        pat = re.compile(_NAME_USE.format(re.escape(name)))
        p = 0
        for words, reds, _ in cmds:
            p += 1
            if any(pat.search(w) for w in words + [r[1] for r in reds]):
                uses[name] = p
                break
    env, drop, loopvals = {}, set(), {}
    if opaque:
        return env, loopvals, set(names) | {"*"}  # "*": any variable may be set
    for name in names:
        mine = [s for s in sets if s[0] == name]
        loop = loops.get(name, [])
        first_use = uses.get(name, 10 ** 9)
        if name in bare and bare[name] <= first_use:
            drop.add(name)
        elif len(mine) == 1 and not loop and mine[0][2] == 0 and mine[0][3] < first_use:
            value = expand(mine[0][1], env)
            if value is None or any(c in value for c in "*?[]{}"):
                drop.add(name)
            else:
                env[name] = value
        elif not mine and len(loop) == 1 and loop[0][0] and loop[0][1] < first_use and \
                len(loop[0][0]) <= MOST_WORDS and \
                all(not re.search(r"[$`*?\[\]{}~]", _tilde(v)) for v in loop[0][0]):
            loopvals[name] = [_tilde(v) for v in loop[0][0]]
        else:
            drop.add(name)
    combos = 1
    for vals in loopvals.values():
        combos *= len(vals)
    if combos > MOST_VARIANTS:
        drop |= set(loopvals)
        loopvals = {}
    return env, loopvals, drop


def _tilde(word):
    """A loop's word with its leading ``~`` or ``~/`` expanded to the home folder, as the shell does (ACT-GUARD-FIX-4:
    ``for d in /tmp/a ~; do rm -rf $d; done`` deletes the home folder); any other ``~`` is left, and the loop is then
    not read, as before."""
    if word == "~" or word.startswith("~/"):
        return os.path.expanduser("~") + word[1:]
    return word


def each(env, loopvals):
    """One environment per combination of the loops' words."""
    keys = sorted(loopvals)
    return [dict(env, **dict(zip(keys, pick))) for pick in product(*(loopvals[k] for k in keys))] or [env]


@contextmanager
def environ(values, drop):
    saved = {k: os.environ.get(k) for k in set(values) | set(drop)}
    try:
        for k in drop:
            os.environ.pop(k, None)
        os.environ.update(values)
        yield
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


# -- inline Python -----------------------------------------------------------------------------------------------

_OPENERS = {"open": 1, "io.open": 1, "codecs.open": 1, "gzip.open": 1, "bz2.open": 1, "lzma.open": 1,
            "builtins.open": 1, "tarfile.open": 1, "zipfile.ZipFile": 1, "dbm.open": 1}
_PATH_WRITES = frozenset("write_text write_bytes touch mkdir unlink rmdir symlink_to hardlink_to link_to chmod "
                         "lchmod".split())
_OS_ONE = frozenset("remove unlink rmdir removedirs mkdir makedirs truncate chmod lchmod chown lchown utime mkfifo "
                    "mknod chflags lchflags setxattr removexattr".split())
_OS_TWO = frozenset("rename renames replace link symlink".split())
_SHUTIL_DST = frozenset("copy copy2 copyfile copytree copymode copystat move".split())
_SHUTIL_SRC = frozenset("move rmtree make_archive".split())
_WRITE_NAMES = frozenset("open system popen run call check_call check_output Popen spawn execv execve execl "
                         "execvp write_text write_bytes touch mkdir makedirs unlink remove rmdir removedirs rename "
                         "renames replace symlink link symlink_to hardlink_to truncate chmod copy copy2 copyfile "
                         "copytree move rmtree make_archive unpack_archive extractall".split())
_SAVES = frozenset("save savefig savetxt savez savez_compressed to_csv to_json to_parquet to_excel to_pickle "
                   "to_feather to_hdf to_html to_latex to_markdown to_stata extractall".split())
_RUNS = frozenset("subprocess.run subprocess.call subprocess.check_call subprocess.check_output subprocess.Popen "
                  "subprocess.getoutput subprocess.getstatusoutput os.system os.popen".split())
_DYNAMIC = frozenset("exec eval compile __import__ importlib.import_module importlib.__import__ "
                     "runpy.run_path runpy.run_module runpy.run_path builtins.exec builtins.eval".split())
_SENSITIVE = ("os", "shutil", "subprocess", "pathlib", "io", "builtins", "importlib", "runpy", "pty", "tarfile",
              "zipfile", "sqlite3", "shelve", "dbm", "fileinput", "asyncio")
_PATHS = frozenset(("Path", "pathlib.Path", "PurePath", "pathlib.PurePath", "PosixPath", "pathlib.PosixPath",
                    "pathlib.PurePosixPath", "PurePosixPath"))


def python_writes(code, ecwd, judge, depth, argv=None, getenv=None):
    """The targets ``code`` writes, as (raw text, absolute path or None); SENT for one it cannot work out. ``judge``
    judges a command the code runs (a literal subprocess or os.system command). ``argv``: the words the command
    gives the code (sys.argv, each None when it does not expand), when known. ``getenv``: name -> (known, value or
    None) for os.environ, when known. Raises SyntaxError."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # an invalid escape in the code is the code's business, not the hook's
        tree = ast.parse(code)
    alias, stores, consts, out = {}, {}, {}, []
    shared = set()  # names a global or nonlocal statement names: never resolved
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                alias[a.asname or a.name.split(".")[0]] = a.name if a.asname else a.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom) and node.module:
            for a in node.names:
                if a.name == "*":
                    if node.module.split(".")[0] in _SENSITIVE:
                        out.append((SENT, None))
                else:
                    alias[a.asname or a.name] = f"{node.module}.{a.name}"
        elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            stores[node.id] = stores.get(node.id, 0) + 1
        elif isinstance(node, ast.arg):
            stores[node.arg] = stores.get(node.arg, 0) + 1
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            stores[node.name] = stores.get(node.name, 0) + 1
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            shared.update(node.names)
    # sys.argv[k] is the command's k-th word, unless the code changes or rebinds sys.argv.
    if argv is not None:
        changed = {id(n) for n in _receivers(tree)}
        if any(isinstance(n, (ast.Attribute, ast.Name)) and qual(n, alias) == "sys.argv" and (
                isinstance(n.ctx, (ast.Store, ast.Del)) or id(n) in changed) for n in ast.walk(tree)):
            argv = None
    # os.environ is the session's, unless the code changes it (a store, update, setdefault, putenv) or names it
    # other than to read one variable.
    if getenv is not None:
        changed = {id(n) for n in _receivers(tree)}
        for n in ast.walk(tree):
            if isinstance(n, (ast.Attribute, ast.Name)) and qual(n, alias) == "os.environ":
                if id(n) in changed or not isinstance(n.ctx, ast.Load):
                    getenv = None
            elif isinstance(n, ast.Assign) and qual(n.value, alias) == "os.environ":
                getenv = None
            elif isinstance(n, ast.Call) and qual(n.func, alias) in ("os.putenv", "os.unsetenv"):
                getenv = None
    # A name bound once in the whole code, by a plain assignment, is that value everywhere (in functions too).
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if stores.get(node.targets[0].id) == 1 and node.targets[0].id not in shared:
                consts[node.targets[0].id] = (node.value, None)
    # The module's own statements run in order: a name has the value its last plain assignment gave it, until a
    # statement binds it otherwise (a loop, a with, a function's body run later sees only the names bound once).
    at = {}
    env = {}
    for stmt in tree.body:
        mine = _bound(stmt)
        target = (stmt.targets[0].id if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1
                  and isinstance(stmt.targets[0], ast.Name) else None)
        inside = {k: v for k, v in env.items() if k not in (mine - {target} if target else mine)}
        for n in ast.walk(stmt):
            if isinstance(n, ast.Call):
                at[id(n)] = inside
        env = {k: v for k, v in env.items() if k not in mine}
        if target and target not in shared and not (mine - {target}):
            env[target] = (stmt.value, inside)
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            for m in ast.walk(n):
                if isinstance(m, ast.Call):
                    at[id(m)] = consts
    cwd_moves = any(isinstance(n, ast.Call) and qual(n.func, alias) in ("os.chdir", "os.fchdir")
                    for n in ast.walk(tree))
    seen = set()
    scope = [consts]

    def ev(node):
        """The text of a path expression, or None."""
        if id(node) in seen:
            return None
        seen.add(id(node))
        try:
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                return node.value
            if isinstance(node, ast.Name):
                if node.id not in scope[-1]:
                    return None
                value, where = scope[-1][node.id]
                scope.append(consts if where is None else where)
                try:
                    return ev(value)
                finally:
                    scope.pop()
            if isinstance(node, ast.Subscript) and getenv is not None and qual(node.value, alias) == "os.environ":
                k = node.slice
                known, value = getenv(k.value) if isinstance(k, ast.Constant) and isinstance(k.value, str) else \
                    (False, None)
                return value if known else None
            if isinstance(node, ast.Subscript) and argv is not None and qual(node.value, alias) == "sys.argv":
                k = node.slice
                if isinstance(k, ast.Constant) and type(k.value) is int and 0 <= k.value < len(argv):
                    return argv[k.value]
                return None
            if isinstance(node, ast.JoinedStr):
                parts = []
                for v in node.values:
                    if isinstance(v, ast.Constant):
                        parts.append(str(v.value))
                    elif isinstance(v, ast.FormattedValue) and v.format_spec is None and v.conversion in (-1, 115):
                        s = ev(v.value)
                        if s is None:
                            return None
                        parts.append(s)
                    else:
                        return None
                return "".join(parts)
            if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Div)):
                a, b = ev(node.left), ev(node.right)
                if a is None or b is None:
                    return None
                return a + b if isinstance(node.op, ast.Add) else os.path.join(a, b)
            if isinstance(node, ast.Attribute) and node.attr == "parent":
                s = ev(node.value)
                return None if s is None else os.path.dirname(s.rstrip("/")) or "."
            if isinstance(node, ast.Call):
                q = qual(node.func, alias)
                args = [ev(a) for a in node.args]
                if node.keywords or None in args:
                    return None
                if q in _PATHS or q == "os.path.join":
                    return os.path.join(*args) if args else "."
                if q in ("str", "os.path.abspath", "os.path.realpath", "os.path.normpath", "os.fspath") and \
                        len(args) == 1:
                    return args[0]
                if q == "os.path.expanduser" and len(args) == 1:
                    return os.path.expanduser(args[0])
                if q in ("os.environ.get", "os.getenv") and getenv is not None and 1 <= len(args) <= 2:
                    known, value = getenv(args[0])
                    return None if not known else value if value is not None else \
                        (args[1] if len(args) == 2 else None)
                if q in ("os.getcwd", "Path.cwd", "pathlib.Path.cwd") and not args:
                    return ecwd
                if q in ("Path.home", "pathlib.Path.home") and not args:
                    return os.path.expanduser("~")
                if isinstance(node.func, ast.Attribute):
                    base = ev(node.func.value)
                    if base is None:
                        return None
                    if node.func.attr in ("resolve", "absolute", "expanduser") and not args:
                        return os.path.expanduser(base)
                    if node.func.attr == "joinpath":
                        return os.path.join(base, *args)
                    if node.func.attr == "with_name" and len(args) == 1:
                        return os.path.join(os.path.dirname(base), args[0])
                    if node.func.attr == "with_suffix" and len(args) == 1:
                        return os.path.splitext(base)[0] + args[0]
            return None
        finally:
            seen.discard(id(node))

    def sink(node):
        raw = None if node is None else ev(node)
        if raw is None or "$" in raw or "`" in raw:
            out.append((SENT, None))
            return
        raw = os.path.expanduser(raw)
        if os.path.isabs(raw):
            out.append((raw, os.path.normpath(raw)))
        elif ecwd is None or cwd_moves:
            out.append((raw, None))
        else:
            out.append((raw, os.path.normpath(os.path.join(ecwd, raw))))

    def handed(node):
        """Whether an argument is (or holds) a path naming the acceptance tests; a call's result is not."""
        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            return any(handed(e) for e in node.elts)
        if isinstance(node, ast.Dict):
            return any(handed(e) for e in node.keys + node.values if e is not None)
        if isinstance(node, ast.Starred):
            return handed(node.value)
        if isinstance(node, ast.Call):
            return False
        if isinstance(node, ast.Name) and node.id in scope[-1] and \
                isinstance(scope[-1][node.id][0], (ast.List, ast.Tuple, ast.Set, ast.Dict)):
            value, where = scope[-1][node.id]
            scope.append(consts if where is None else where)
            try:
                return handed(value)
            finally:
                scope.pop()
        text = ev(node)
        # A path, not a text that mentions one (a brief, a code string): one word naming the tests' folder.
        return bool(text) and bool(_A_PATH.fullmatch(text.strip()))

    def arg(call, i, kw):
        for k in call.keywords:
            if k.arg == kw:
                return k.value
            if k.arg is None:
                return None  # **kwargs: not read
        return call.args[i] if i is not None and len(call.args) > i else None

    def writes_mode(node, default_read=True):
        if node is None:
            return not default_read
        return not (isinstance(node, ast.Constant) and isinstance(node.value, str)
                    and not re.search(r"[wax+]", node.value))

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        scope[:] = [at.get(id(node), consts)]
        q = qual(node.func, alias)
        attr = node.func.attr if isinstance(node.func, ast.Attribute) else None
        if q == "getattr":
            name = node.args[1] if len(node.args) > 1 else None
            if not (isinstance(name, ast.Constant) and isinstance(name.value, str)) or name.value in _WRITE_NAMES:
                out.append((SENT, None))  # getattr(os, "remove"), or a name the guard cannot read
        elif q in _DYNAMIC or (q and q.split(".")[0] in ("pty",)) or \
                (q and re.match(r"os\.(exec|spawn|posix_spawn)", q)) or (q or "").startswith("asyncio.create_sub"):
            out.append((SENT, None))
        elif q in _OPENERS:
            if writes_mode(arg(node, _OPENERS[q], "mode" if q != "dbm.open" else "flag")):
                sink(arg(node, 0, "file"))
        elif q in ("shelve.open",):
            sink(arg(node, 0, "filename"))
        elif q == "sqlite3.connect":
            target = arg(node, 0, "database")
            if ev(target) != ":memory:" if target is not None else True:
                sink(target)
        elif q == "os.open":
            flags = arg(node, 1, "flags")
            names = {n.attr for n in ast.walk(flags) if isinstance(n, ast.Attribute)} if flags is not None else set()
            plain = flags is not None and all(isinstance(n, (ast.Attribute, ast.Name, ast.BinOp, ast.BitOr, ast.Load))
                                              for n in ast.walk(flags))
            if not plain or names & {"O_WRONLY", "O_RDWR", "O_CREAT", "O_TRUNC", "O_APPEND", "O_TMPFILE"}:
                sink(arg(node, 0, "path"))
        elif q in ("fileinput.input", "fileinput.FileInput"):
            if any(k.arg == "inplace" for k in node.keywords):
                out.append((SENT, None))
        elif q and q.startswith("os.") and q[3:] in _OS_ONE:
            sink(arg(node, 0, "path"))
        elif q and q.startswith("os.") and q[3:] in _OS_TWO:
            sink(arg(node, 0, "src"))
            sink(arg(node, 1, "dst"))
        elif q and q.startswith("shutil.") and (q[7:] in _SHUTIL_DST or q[7:] in _SHUTIL_SRC):
            if q[7:] in _SHUTIL_DST:
                sink(arg(node, 1, "dst"))
            if q[7:] in _SHUTIL_SRC:
                sink(arg(node, 0, "path" if q[7:] == "rmtree" else "base_name" if q[7:] == "make_archive"
                         else "src"))
        elif q == "shutil.unpack_archive":
            target = arg(node, 1, "extract_dir")
            sink(target if target is not None else ast.Constant("."))
        elif q in _RUNS:
            cmd = arg(node, 0, "args" if q.startswith("subprocess") else "command")
            text = None
            if isinstance(cmd, (ast.List, ast.Tuple)):
                words = [ev(e) for e in cmd.elts]
                text = None if None in words else shlex.join(words)
            elif cmd is not None:
                text = ev(cmd)
            where = arg(node, None, "cwd") if q.startswith("subprocess") else None
            run_cwd = ecwd if where is None else ev(where)
            if text is None or depth >= MOST_DEPTH:
                out.append((SENT, None))
            else:
                if run_cwd is not None and not os.path.isabs(run_cwd) and ecwd is not None:
                    run_cwd = os.path.join(ecwd, run_cwd)
                out.extend(judge(text, run_cwd, depth + 1))
        elif attr == "open" and not (q or "").split(".")[0] in alias.values():
            if writes_mode(arg(node, 0, "mode")):
                sink(node.func.value)
        elif attr in _PATH_WRITES and q not in ("os.mkdir", "os.chmod"):
            sink(node.func.value)
        elif attr in ("rename", "replace") and len(node.args) == 1 and not node.keywords:
            sink(node.func.value)
            sink(node.args[0])
        elif attr in _SAVES and (node.args or node.keywords):
            target = arg(node, 0, "path")
            if target is not None:
                sink(target)
            elif attr == "extractall":
                sink(ast.Constant("."))
        elif attr == "extract":
            target = arg(node, 1, "path")
            sink(target if target is not None else ast.Constant("."))
        elif not _safe_call(q, attr) and any(handed(a) for a in node.args + [k.value for k in node.keywords]):
            # A function the guard does not know, handed the acceptance tests' path: it may write them.
            out.append((SENT, None))
    return out


_SAFE_MODULES = ("re", "os.path", "json", "yaml", "fnmatch", "glob", "shlex", "textwrap", "difflib", "hashlib", "ast",
                 "math", "itertools", "collections", "functools", "operator", "string", "datetime", "time",
                 "random", "statistics", "pprint", "typing", "dataclasses", "enum", "base64", "binascii",
                 "urllib.parse", "html", "sys", "unicodedata", "decimal", "fractions", "uuid", "heapq", "bisect",
                 "copy", "inspect", "tomllib", "csv")
_SAFE_FUNCS = frozenset("print len str repr sorted set list dict tuple frozenset any all isinstance issubclass "
                        "enumerate zip map filter min max sum int float bool range type id hash iter next abs round "
                        "format chr ord hex bin oct divmod pow reversed slice hasattr callable input Path PurePath "
                        "PosixPath PurePosixPath pathlib.Path pathlib.PurePath pathlib.PosixPath "
                        "pathlib.PurePosixPath os.listdir os.scandir os.walk os.stat os.lstat os.access os.getcwd "
                        "os.fspath os.environ.get os.getenv os.cpu_count os.getpid os.get_terminal_size "
                        "pytest.main".split())
_SAFE_METHODS = frozenset("read_text read_bytes exists is_file is_dir is_symlink is_absolute glob rglob iterdir stat "
                          "lstat resolve absolute relative_to is_relative_to joinpath with_name with_suffix with_stem "
                          "match samefile as_posix as_uri startswith endswith find rfind index rindex count split "
                          "rsplit splitlines partition rpartition strip lstrip rstrip replace format format_map join "
                          "encode decode lower upper title casefold zfill ljust rjust center expandtabs isdigit "
                          "isalpha get items keys values append extend insert add discard pop popitem clear copy "
                          "sort reverse search fullmatch findall finditer sub subn group groups groupdict span "
                          "start end read readline readlines load loads dumps setdefault update remove difference "
                          "union intersection issubset issuperset most_common write writelines close flush seek "
                          "tell __contains__".split())


def _safe_call(q, attr):
    """A call that writes no file it is handed: builtins, read-only modules and the common read and text methods."""
    if q in _SAFE_FUNCS or (q and any(q == m or q.startswith(m + ".") for m in _SAFE_MODULES)):
        return True
    return attr in _SAFE_METHODS


def _receivers(tree):
    """The objects whose methods a call changes in place (x.append(...), x[0] = ...): sys.argv among them is not
    the command's words any more."""
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in (
                "append", "extend", "insert", "pop", "remove", "clear", "reverse", "sort", "__setitem__", "update",
                "setdefault", "popitem", "__delitem__"):
            out.append(n.func.value)
        elif isinstance(n, ast.Subscript) and isinstance(n.ctx, (ast.Store, ast.Del)):
            out.append(n.value)
    return out


def _bound(stmt):
    """The names a statement binds or deletes, anywhere inside it."""
    out = set()
    for n in ast.walk(stmt):
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
            out.add(n.id)
        elif isinstance(n, ast.arg):
            out.add(n.arg)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(n.name)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            out.update((a.asname or a.name).split(".")[0] for a in n.names)
        elif isinstance(n, ast.ExceptHandler) and n.name:
            out.add(n.name)
        elif isinstance(n, (ast.Global, ast.Nonlocal)):
            out.update(n.names)
        elif getattr(n, "name", None) and type(n).__name__ in ("MatchAs", "MatchStar"):
            out.add(n.name)
        elif type(n).__name__ == "MatchMapping" and getattr(n, "rest", None):
            out.add(n.rest)
    return out


def qual(func, alias):
    if isinstance(func, ast.Name):
        return alias.get(func.id, func.id)
    if isinstance(func, ast.Attribute):
        base = qual(func.value, alias)
        return None if base is None else f"{base}.{func.attr}"
    return None


# -- the judgement -----------------------------------------------------------------------------------------------

# The git commands that take the diff option --output=<file> (W2-42a): it writes that file.
_GIT_OUTPUT_SUBS = frozenset("diff show log whatchanged diff-tree diff-index diff-files format-patch range-diff".split())


def _more_targets(name, args, ecwd):
    """The targets of writes the product's parser does not read: git checkout, restore, rm and mv on paths; dd
    of=; truncate; sort -o; rsync's destination; patch's file and -o. Each as (word, the folder it is read in)."""
    out = []
    if name == "git":
        i, where = 0, ecwd
        while i < len(args) and args[i].startswith("-"):
            if args[i] == "-C" and i + 1 < len(args):
                where = None if where is None else os.path.join(where, args[i + 1])
            i += 2 if args[i] in ("-C", "-c", "--git-dir", "--work-tree", "--namespace") else 1
        sub, rest = (args[i], args[i + 1:]) if i < len(args) else ("", [])
        if sub in ("checkout", "restore", "rm", "mv"):
            if "--" in rest:
                words = rest[rest.index("--") + 1:]
            else:
                words, skip = [], False
                for w in rest:
                    if skip:
                        skip = False
                    elif w in ("-s", "--source", "-b", "-B", "--orphan", "--conflict"):
                        skip = True
                    elif not w.startswith("-"):
                        words.append(w)
            out = [(w, where) for w in words]
        elif sub in _GIT_OUTPUT_SUBS or (sub == "stash" and rest[:1] == ["show"]):
            # W2-42a: git's own --output=<file> and --output <file> write that file (read from the command's cwd,
            # after -C); a word after -- is a path, no option.
            for k, w in enumerate(rest):
                if w == "--":
                    break
                if w == "--output" and k + 1 < len(rest):
                    out.append((rest[k + 1], where))
                elif w.startswith("--output="):
                    out.append((w[len("--output="):], where))
        elif sub == "archive":
            # DECIDED-NOT-DONE row 215 (W2-42a r4 return, the archive form): git archive -o <file>, -o<file>,
            # --output <file> and --output=<file> write that file; a word after -- is a path, no option.
            for k, w in enumerate(rest):
                if w == "--":
                    break
                if w in ("-o", "--output") and k + 1 < len(rest):
                    out.append((rest[k + 1], where))
                elif w.startswith("--output="):
                    out.append((w[len("--output="):], where))
                elif w.startswith("-o") and len(w) > 2 and not w.startswith("--"):
                    out.append((w[2:], where))
    elif name == "dd":
        out = [(a[3:], ecwd) for a in args if a.startswith("of=")]
    elif name == "truncate":
        skip = False
        for a in args:
            if skip:
                skip = False
            elif a in ("-s", "-r", "--size", "--reference"):
                skip = True
            elif not a.startswith("-"):
                out.append((a, ecwd))
    elif name == "sort":
        for k, a in enumerate(args):
            if a in ("-o", "--output") and k + 1 < len(args):
                out.append((args[k + 1], ecwd))
            elif a.startswith("--output="):
                out.append((a[9:], ecwd))
            elif a.startswith("-o") and len(a) > 2 and not a.startswith("--"):
                out.append((a[2:], ecwd))
    elif name == "rsync":
        operands = [a for a in args if not a.startswith("-")]
        out = [(operands[-1], ecwd)] if len(operands) >= 2 else []
    elif name == "patch":
        operands = [a for a in args if not a.startswith("-")]
        out = [(operands[0], ecwd)] if operands else []
        for k, a in enumerate(args):
            if a in ("-o", "--output") and k + 1 < len(args):
                out.append((args[k + 1], ecwd))
    return out


def _is_rev(word, where):
    """Whether ``git checkout <word>`` reads ``word`` as a revision, as git does when it names one (W2-42a): then the
    words after it are the paths it writes. Unsure (no folder, git does not answer): not a revision, so every word
    is a path (fail closed)."""
    if where is None or where.startswith(UNKNOWN) or not word or word.startswith("-"):
        return False
    from gov.guard.reads import PolicyError, _git  # the read policy's git (AR-2's sweep, row 61)
    try:
        return _git(where, "rev-parse", "--verify", "--quiet", word + "^{commit}").returncode == 0
    except (PolicyError, ValueError):
        return False


def checkout_paths(args, ecwd):
    """The paths git checkout, restore, rm and mv write, as ``_more_targets`` reads them, except that a checkout
    without ``--`` whose first word git reads as a revision does not write that word (``git checkout main`` switches
    branches: a wholesale move, left open as before; ``git checkout main x`` writes x)."""
    out = _more_targets("git", args, ecwd)
    i = 0
    while i < len(args) and args[i].startswith("-"):
        i += 2 if args[i] in ("-C", "-c", "--git-dir", "--work-tree", "--namespace") else 1
    if args[i:i + 1] == ["checkout"] and "--" not in args[i + 1:] and out and _is_rev(out[0][0], out[0][1]):
        return out[1:]
    return out


def _written(stages, raw=False):
    """The names of the files a pipeline's stages write by a redirect or tee (a heredoc's body lands there); with
    ``raw``, the target words themselves."""
    out = []
    for words, reds in stages:
        out += [t for op, t in reds if ">" in op and op not in (">&",) and not t.isdigit()]
        head = lead(words)
        if head and os.path.basename(head[0]) == "tee":
            out += [a for a in head[1:] if not a.startswith("-")]
    return [w for w in out if w] if raw else [w for w in map(os.path.basename, out) if w]


# Commands that take a file's name and never run the file (round 2, F2): a script named by any other command may be
# run by it.
_NOT_RUNNERS = frozenset(
    "cat head tail less more wc grep egrep fgrep rg ls stat file diff cmp chmod chown chgrp touch cp mv rm ln install "
    "echo printf test [ [[ md5sum sha1sum sha256sum sha512sum b2sum cksum base64 sed jq sort uniq cut tr nl column "
    "xxd od hexdump strings realpath readlink dirname basename true false : mkdir rmdir tee shellcheck shfmt bat "
    "dos2unix unix2dos fold fmt iconv expand unexpand du df wait sleep cd pushd popd pwd export unset read set "
    "declare local typeset readonly shift exit return break continue git ruff black flake8 pyflakes pylint mypy "
    "isort yamllint for select case in esac done fi".split())  # a loop's words: a run inside it is judged there
# What a mapfile/readarray -C callback may be and still be judged as the command it is: a command the walker knows
# (anything else may be a function the guard cannot read).
_CALLBACK_KNOWN = _NOT_RUNNERS | frozenset(_SHELLS)
# xargs options that take no value (xargs runs its command with the words of a here-string, R3).
_XARGS_FLAGS = frozenset(("--no-run-if-empty", "--verbose", "--exit", "--open-tty", "--interactive"))
# Programs that run the file they are given as Python.
_PY_RUNNERS = frozenset("pytest py.test coverage ipython".split())


def _script_words(head, reds):
    """The words of a simple command that name a file it may run, each with how it runs it: (word, "shell" |
    "python" | "exec" | "code"), and the code strings it runs (-c, -e) that may name one."""
    if not head:
        return [], []
    name, args = os.path.basename(head[0]), head[1:]
    inputs = [t for op, t in reds if op in ("<", "<<<", "<>")]
    out, code = [(head[0], "exec")], []
    if name in _SHELLS or name in ("source", "."):
        i = 0
        while i < len(args) and args[i].startswith(("-", "+")) and args[i] not in ("-", "--"):
            if _short(args[i], "c"):
                code += args[i + 1:i + 2]
                return out, code
            a = args[i]  # -o, -O, +o, +O take a value, once for each in a cluster (-euo pipefail; round 1, F1)
            i += 2 if a in ("--rcfile", "--init-file") else 1 if a.startswith("--") else \
                1 + sum(ch in "oO" for ch in a[1:])
        i += i < len(args) and args[i] in ("-", "--")
        out += [(args[i], "shell")] if i < len(args) else [(t, "shell") for t in inputs]
    elif _PY.match(name) or name in _PY_RUNNERS:
        i = 0
        while i < len(args) and args[i].startswith("-") and args[i] != "-" and _PY.match(name):
            if not args[i].startswith("--") and "c" in args[i][1:]:
                code += args[i + 1:i + 2]
                return out, code
            if not args[i].startswith("--") and args[i].endswith("m"):
                return out + [(w, "python") for w in args[i + 1:] + inputs], code  # -m runpy, pytest, ...
            i += 2 if args[i] in ("-W", "-X") else 1
        if name in _PY_RUNNERS:
            return out + [(w, "python") for w in args if not w.startswith("-")], code
        out += [(args[i], "python")] if i < len(args) and args[i] != "-" else [(t, "python") for t in inputs]
    elif name not in _NOT_RUNNERS:
        # perl, node, make, xargs, find -exec, uv run, an unknown program: any file it is given may be run.
        out += [(w, "code") for w in args + inputs]
        code += args
    return out, code


def _applies_patch(name, args):
    """git apply, git am, git stash apply or pop, and patch: they write the files the patch names."""
    if name == "patch":
        return "--dry-run" not in args
    if name != "git":
        return False
    i = 0
    while i < len(args) and args[i].startswith("-"):
        i += 2 if args[i] in ("-C", "-c", "--git-dir", "--work-tree", "--namespace") else 1
    sub, rest = (args[i], args[i + 1:]) if i < len(args) else ("", [])
    if sub == "apply":
        return not (set(rest) & {"--check", "--stat", "--numstat", "--summary"}) or "--apply" in rest
    if sub == "am":
        return True
    return sub == "stash" and rest[:1] in (["apply"], ["pop"])


def _stash(name, args):
    """git stash apply or pop: a patch applier for the hook's rule 1, not one of the product's KPI-5 writes (left as
    the product read it, like git merge, pull and reset)."""
    if name != "git":
        return False
    i = 0
    while i < len(args) and args[i].startswith("-"):
        i += 2 if args[i] in ("-C", "-c", "--git-dir", "--work-tree", "--namespace") else 1
    return args[i:i + 1] == ["stash"]


def _prefix(words, head):
    """The names a simple command sets in its own environment before what it runs (X=1 cmd, env X=1 cmd); "*" when
    it may change any (env -i, env -u, env -S)."""
    out = set()
    for w in words[:len(words) - len(head)]:
        m = _ASSIGN.match(w)
        if m:
            out.add(m.group(1))
        elif w.startswith("-") and not w.startswith("--") or w in ("--ignore-environment", "--unset", "--split-string"):
            out.add("*")
    return out


def _shebang(text):
    """How a file run by its own name is run, by its #! line. With none, bash runs it as shell whatever it holds:
    the guard cannot tell what the file was meant to be (unknown)."""
    first = text.split("\n", 1)[0]
    if not first.startswith("#!"):
        return "unknown"
    return "python" if "python" in first else "shell" if re.search(r"\b(ba|da|z|k)?sh\b", first) else "code"


def _kind(words):
    """How a command reads a heredoc on its standard input: data, python, shell or code (unknown)."""
    words = lead(words)
    if not words:
        return "code"
    name, args = os.path.basename(words[0]), words[1:]
    if _PY.match(name):
        i = 0
        while i < len(args) and args[i].startswith("-") and args[i] != "-":
            if args[i][-1:] in "cm" and not args[i].startswith("--"):
                return "data"  # the program is in the words (-c) or a module (-m): stdin is its data
            i += 2 if args[i] in ("-W", "-X") else 1
        return "python" if i >= len(args) or args[i] == "-" else "data"
    if name in _SHELLS:
        opts = [a for a in args if a.startswith("-")]
        if any("c" in o.lstrip("-") for o in opts if not o.startswith("--")):
            return "data"
        if "-s" in opts or len(opts) == len(args):
            return "shell"  # the reading before the fix, kept as its floor (fail closed)
        script = _shell_script(args)
        # No script, a script that is standard input, or an option the guard does not know: the shell reads the
        # body as commands (review round 1, F1: an option's value is no script name).
        return "shell" if script is None or script in _STDIN else "data"
    return "data" if name in _DATA else "code"


_PARAM = re.compile(r"\$\{([A-Za-z_]\w*)([^}]*)\}|\$([A-Za-z_]\w*)|\$[0-9@*#?$!-]")


def emptied(word):
    """The text ``word`` gives if every variable the environment does not set, and every substitution, were empty
    (ACT-GUARD-FIX-4): ``${X:-d}`` gives d; None when the word guards itself against an empty value (``${X:?}``,
    ``${X?}``, ``${X:+...}``) or holds an expansion this does not know."""
    text = re.sub(r"`__gov_sub_\d+__`", "", word)
    if "`" in text or "$(" in text:
        return None
    guarded = []

    def value(m):
        name = m.group(1) or m.group(3)
        rest = m.group(2) or ""
        if name is None:
            return ""  # $1, $@, $$, ...
        val = os.environ.get(name)
        if rest[:2] in (":?", ":+") or rest[:1] in ("?", "+"):
            guarded.append(name)
            return ""
        if rest[:2] in (":-", ":="):
            return val if val else rest[2:]
        if rest[:1] in ("-", "="):
            return val if val is not None else rest[1:]
        if rest:
            guarded.append(name)  # ${X#...}, ${X/...}: not read here
            return ""
        return val or ""
    text = _PARAM.sub(value, text)
    if guarded or "$" in text:
        return None
    if text.startswith("~"):
        text = os.path.expanduser(text)
    return text


_STDIN = ("/dev/stdin", "/dev/fd/0", "/proc/self/fd/0")
_SHELL_LETTERS = frozenset("abefhiklmnprstuvxBCDEHIPTV")  # bash's and dash's one-letter options, o, O and c apart
_SHELL_LONG = frozenset(("--debug", "--debugger", "--dump-po-strings", "--dump-strings", "--help", "--login",
                         "--noediting", "--noprofile", "--norc", "--posix", "--pretty-print", "--restricted",
                         "--verbose", "--version"))


def _shell_script(args):
    """The script word a shell is given after its options (review round 1, F1), or None when it reads its commands
    from standard input: no script word, ``-s`` in a cluster, or an option it does not know (fail closed). ``-o``,
    ``+o``, ``-O`` and ``+O`` take the next word as their value, once for each such letter in a cluster
    (``-euo pipefail``); ``--rcfile`` and ``--init-file`` take the next word."""
    i = 0
    while i < len(args):
        a = args[i]
        if a in ("-", "--"):
            i += 1
            break
        if a.startswith("--"):
            if a in ("--rcfile", "--init-file"):
                i += 2
            elif a in _SHELL_LONG or a.startswith(("--rcfile=", "--init-file=")):
                i += 1
            else:
                return None
            continue
        if len(a) > 1 and a[0] in "-+":
            letters = a[1:]
            if "s" in letters or any(ch not in _SHELL_LETTERS and ch not in "oO" for ch in letters):
                return None
            i += 1 + sum(ch in "oO" for ch in letters)
            continue
        break
    return args[i] if i < len(args) else None


class Judgement:
    """What a Bash command writes: the shell's own targets (rule 5 reads these), and the findings in the code it
    runs inline (rule 1 reads both). ``findings`` is a list of (targets, scope, code): ``scope`` is the text whose
    naming of the acceptance tests refuses an unresolvable target; ``code``: it is code (Python, perl or node, a
    script body), whose naming counts in any spelling (names_tests)."""

    def __init__(self, parse, expand, bodies=None, loose=frozenset(), readvars=None):
        self.parse = parse    # the product's parser: (command, cwd) -> targets or None
        self.expand = expand  # the product's word expansion: (word) -> text or None
        # judge's second readings of a command the first cannot read (APOS-3/APOS-4): "strings", a here-string a
        # command may run is taken as data; "legacy", a # inside ${...} may start a comment, as before APOS-3.
        self.loose = loose
        self.shell, self.findings = [], []
        # What rm deletes (ACT-GUARD-FIX-4, DEC-1050 (8)): (the word, the path, "names" when the word expands to it,
        # "if-empty" when it is the path the word names if every variable the guard cannot resolve were empty).
        self.deletes = []
        # The folders mkdir makes, resolved to a path (ACT-GUARD-FIX-4, rule 5: a reviewer may make its record
        # folder itself, never delete or move it).
        self.made = []
        # The product's (W2-42a): the writes the line parser does not read, and the runs it cannot read.
        self.writes, self.unread = [], []
        self.recovered = False  # set by ``judge`` on a command only a second reading could read
        self.bodies = [] if bodies is None else bodies  # every heredoc body met, nested commands' too
        self.ctx = ({}, {}, set())  # the variables of the command being walked
        self.prefix = set()  # the variables the simple command being judged sets for itself (X=1 cmd, env X=1 cmd)
        # The variables ``read`` binds in a command with a here-string, shared with the commands nested in it
        # (DEC-1164 (18), R3 F1 second batch): one used as a command's name is a command the guard cannot know.
        self.readvars = set() if readvars is None else readvars

    def targets(self):
        """What the product's write parser enforces (W2-42a): the shell's own writes, the writes the line parser
        does not read, and a sentinel for each run of a script the parser cannot read."""
        return self.shell + self.writes + self.unread

    def adopt(self, sub):
        """A nested judgement's product lists, taken into this one (the hook's ``deletes`` and ``made`` too)."""
        self.writes += sub.writes
        self.unread += sub.unread
        self.deletes += sub.deletes
        self.made += sub.made

    def run(self, command, cwd, whole, depth=0):
        outer = self.ctx
        try:
            self._run(command, cwd, whole, depth)
        finally:
            self.ctx = outer  # a nested command's variables are not this one's

    def _run(self, command, cwd, whole, depth):
        if depth > MOST_DEPTH:
            self.shell.append(SENT)
            return
        text, bodies = heredocs(command, legacy="legacy" in self.loose, hstr="hstr" in self.loose,
                                lenient="open" in self.loose)
        base = len(self.bodies)
        self.bodies += bodies
        # This command's own heredocs get their number among all met so far (a nested command's marks are
        # already numbered so).
        text = re.sub(r"__gov_hdl_(\d+)__", lambda m: f"__gov_heredoc_{base + int(m.group(1))}__", text)
        text, subs = lift(text)
        if "<<<" in text and "strings" not in self.loose:
            _check_here_strings(simples(tokens(text)))
        if "<<<" in text:
            self.readvars |= _read_bound(simples(tokens(text)))

        def expand(value, env):
            with environ(env, ()):
                return self.expand(value)
        env, loopvals, drop = variants(text, expand)
        self.ctx = (env, loopvals, drop)
        ptext = parser_text(text)
        for one in each(env, loopvals):
            with environ(one, drop):
                self.shell += self.parse(ptext, cwd) or []
        # The walk below reads the folder the shell is in; a loop's word is not one value there: dropped.
        ecwd, stage, held, staged = cwd, [], [], []
        scripts = []  # the files data heredocs were written to: (their names, the body)
        with environ(env, drop | set(loopvals)):
            for words, reds, sep in simples(tokens(text)):
                for w in words + [r[1] for r in reds]:
                    for k in map(int, re.findall(r"__gov_sub_(\d+)__", w)):
                        if k < len(subs):  # a mark the text held already (the hook's parser text) is a word
                            self.sub(subs[k], ecwd, whole, depth)
                self.ctx = (env, loopvals, drop)
                head = lead(words)
                self.prefix = _prefix(words, head)
                name = os.path.basename(head[0]) if head else ""
                args = head[1:]
                part = " ".join(words)
                if self.readvars and self.names_read_var(words, head):
                    self.unread.append(SENT)
                for names, body in scripts:
                    self.script(names, body, words, reds, subs, part, ecwd, whole, depth, staged)
                if name == "rm":
                    self.removal(args, ecwd, env, loopvals, drop)
                if name == "mkdir":
                    self.making(args, ecwd, env, loopvals, drop)
                if name in ("cd", "pushd", "popd"):
                    ecwd = self.cd(name, args, ecwd)
                elif name in _SHELLS and any(_short(a, "c") for a in args):
                    i = next(i for i, a in enumerate(args) if _short(a, "c"))
                    if i + 1 < len(args):
                        self.inner(args[i + 1], ecwd, whole, depth)
                elif name == "eval":
                    self.inner(" ".join(args), ecwd, whole, depth)
                elif _PY.match(name):
                    self.inline_python(args, part, ecwd, whole, depth)
                elif name in ("git", "dd", "truncate", "sort", "rsync", "patch"):
                    # Writes the product's parser does not read (rule 1 judges them; rule 5 as before). A patch
                    # applied writes the files it names: unknown targets, judged by the whole command.
                    if _applies_patch(name, args):
                        self.findings.append(([(SENT, None)], whole, False))
                        if not _stash(name, args):
                            self.writes.append(SENT)  # git apply, git am, patch (KPI 5)
                    targets = [self.place(t, where) for t, where in _more_targets(name, args, ecwd)]
                    if targets:
                        self.findings.append((targets, part, False))
                    mine = checkout_paths(args, ecwd) if name == "git" else _more_targets(name, args, ecwd)
                    for t, where in mine:
                        raw, full = self.place(t, where)
                        self.writes.append(SENT if full is None else os.path.realpath(full))
                elif name in ("mapfile", "readarray"):
                    self.callback(args, ecwd, whole, depth)
                elif _INLINE.search(part):
                    # perl, node, ruby: code the guard does not read (ACT-GUARD-FIX-2's judgement of the part; any
                    # spelling of the tests' folder counts, round 2, F4)
                    self.findings.append(([(SENT, None)], part, True))
                stage.append(_kind(words))
                staged.append((words, reds))
                held += [(int(m), len(stage) - 1, part, ecwd)
                         for r in reds for m in re.findall(r"^__gov_heredoc_(\d+)__$", r[1])
                         if int(m) < len(self.bodies)]  # a mark the text held already (the hook's) is none
                if sep not in ("|", "|&"):
                    for k, at, part_, where in held:
                        # The body is read by its own command and, through a pipe, by the stages after it:
                        # data if all of them take it as data; the one that runs it otherwise; code (unknown)
                        # if more than one could.
                        runs = [kind for kind in stage[at:] if kind != "data"]
                        kind = "data" if not runs else runs[0] if len(runs) == 1 else "code"
                        full = next((w for (w, _), kd in zip(staged[at:], stage[at:]) if kd == kind), [])
                        reader = lead(full)
                        self.prefix = _prefix(full, reader)
                        self.body(self.bodies[k], kind, part_, where, whole, depth, argv=self.py_argv(reader),
                                  reader=reader)
                        if kind == "data":
                            targets = _written(staged[at:], raw=True)
                            if targets:
                                scripts.append(({self.basename(t) for t in targets}, self.bodies[k]))
                    stage, held, staged = [], [], []

    def names_read_var(self, words, head):
        """Whether the simple command ``words`` runs a command named by a variable ``read`` bound from a here-string,
        or hands one to a program that runs its words (xargs, sudo, find -exec, ...): the guard cannot know it."""
        if head:
            name = os.path.basename(head[0])
            if _uses_var(head[0], self.readvars):
                return True
            if name in _RUN_WRAPPERS or (name == "find" and any(a in ("-exec", "-execdir", "-ok", "-okdir")
                                                                 for a in head[1:])):
                return any(_uses_var(w, self.readvars) for w in head[1:])
            return False
        first = next((w for w in words if not _ASSIGN.match(w) and w not in _OPENS), "")
        return os.path.basename(first) in _RUN_WRAPPERS and any(_uses_var(w, self.readvars) for w in words)

    def callback(self, args, ecwd, whole, depth):
        """``mapfile``/``readarray -C CALLBACK`` (also joined, ``-tC``) runs the callback as a command: a literal one is
        judged as that command; one the guard cannot know (a variable, a substitution, a function or a program it does
        not read) is unresolvable (DEC-1164 (18), R3 F1 second batch)."""
        cb, i = None, 0
        while i < len(args) and len(args[i]) > 1 and args[i][0] == "-" and args[i] != "--":
            a = args[i]
            i += 1
            k = next((k for k, ch in enumerate(a) if k and ch in "dnOsuCc"), None)
            if k is not None:  # the option's value: the rest of the word, or the next word
                value = a[k + 1:]
                if not value and i < len(args):
                    value, i = args[i], i + 1
                if a[k] == "C":
                    cb = value
        if not cb:
            return
        text = self.expand(cb)
        if text is None or "`" in text:
            self.unread.append(SENT)
            return
        try:
            self.sub(text, ecwd, whole, depth)
            known = all(not (h := lead(w)) or os.path.basename(h[0]) in _CALLBACK_KNOWN or _PY.match(
                os.path.basename(h[0])) for w, _, _ in simples(tokens(text)))
        except Unreadable:
            known = False
        if not known:
            self.unread.append(SENT)

    def basename(self, word):
        """The name of the file a word names, or None when it does not expand."""
        exp = self.expand(word)
        return None if exp is None or "`" in exp else os.path.basename(exp.rstrip("/"))

    def script(self, names, body, all_words, reds, subs, part, ecwd, whole, depth, piped=()):
        """A command after one that wrote a data heredoc's body to a file (ACT-GUARD-FIX-3 round 2, F2): when it may
        run that file, the body is judged as the code it then is. A run the guard reads (bash or sh, source, python,
        the file's own name, after a cd too) is judged as shell or Python; any other command given the file's name
        (a word, a pipe into xargs or a shell, a -c string or a substitution naming it), and a run whose script word
        does not expand (a loop's variable, $S), is code the guard cannot read: refused under rule 1 when the body
        names the tests, and judged as shell under rule 5, as before this fix."""
        head = lead(all_words)
        words, code = _script_words(head, reds)
        unsure = None in names
        how = None
        for w, kind in words:
            base = self.basename(w)
            if base is not None and base in names:
                how = kind
                break
            if (base is None or unsure) and kind in ("exec", "shell", "python") and \
                    (kind != "exec" or base is None or "/" in w):
                how = how or ("unknown-python" if kind == "python" else "unknown")
        if how is None and head and piped and (os.path.basename(head[0]) in ("xargs", "parallel") or
                                               (len(words) == 1 and _kind(head) in ("shell", "python"))):
            # A pipe hands the file's name to xargs, or its text to a shell or python reading its input.
            if any(self.basename(w) in names for ws, rs in piped for w in ws + [r[1] for r in rs]):
                how = "unknown"
        if how is None:
            texts = code + [subs[int(k)] for w in all_words + [r[1] for r in reds]
                            for k in re.findall(r"__gov_sub_(\d+)__", w) if int(k) < len(subs)]
            if any(n and n in t for n in names for t in texts):
                how = "unknown-python" if head and _PY.match(os.path.basename(head[0])) else "unknown"
        name = os.path.basename(head[0]) if head else ""
        if how is None:
            if name in ("cp", "mv", "ln", "install") and len(head) > 2 and \
                    any(self.basename(w) in names for w in head[1:-1] if not w.startswith("-")):
                names.add(self.basename(head[-1]))  # a copy of the script, which a later command may run
            return
        if how == "exec":
            how = _shebang(body["text"])
        if how == "python":
            i = next((i for i, w in enumerate(head) if self.basename(w) in names), None)
            argv = [self.expand(w) for w in head[i:]] if i is not None else None
            at = len(self.findings)
            self.code(body["text"], part, ecwd, whole, depth, shell_text=not body["quoted"], argv=argv)
            # The product (W2-42a, KPI 8): a Python file the command writes and runs is judged as its code.
            for targets, _scope, _code in self.findings[at:]:
                self.writes += [SENT if raw == SENT or full is None else os.path.realpath(full)
                                for raw, full in targets]
        elif how == "shell" and (body["quoted"] or not _EXPANSION.search(body["text"])):
            self.script_shell(body["text"], part, ecwd, whole, depth)
        else:
            self.unknown_script(body["text"], part, ecwd, whole, depth, shell=how != "unknown-python")

    def script_shell(self, text, part, ecwd, whole, depth):
        """A script file's shell body, run by this command: its writes are the command's (rule 5); under rule 1 a
        target that names the tests refuses wherever the script runs, and one it cannot work out refuses when the
        body names them."""
        sub = Judgement(self.parse, self.expand, self.bodies, self.loose, self.readvars)
        try:
            sub.run(text, UNKNOWN if ecwd is None or ecwd.startswith(UNKNOWN) else ecwd, whole, depth + 1)
        except Unreadable:
            self.unknown_script(text, part, ecwd, whole, depth, shell=True)
            return
        shell = [SENT if t.startswith(UNKNOWN) else t for t in sub.shell]
        self.shell += shell
        self.adopt(sub)
        self.findings += sub.findings
        self.findings.append(([(SENT, None) if t == SENT else (t, os.path.normpath(t) if os.path.isabs(t) else None)
                               for t in shell], part + "\n" + text, True))

    def unknown_script(self, text, part, ecwd, whole, depth, shell):
        """A script file run by a form the guard cannot read: refused under rule 1 when the body names the tests;
        under rule 5 its body is read as shell, as before this fix (``shell``; not a Python body run by Python,
        which rule 5 never read). For the product (W2-42a, KPI 8) a shell or unknown run it cannot read is
        unresolvable; a Python run stays opaque to it, as any Python script is."""
        self.findings.append(([(SENT, None)], part + "\n" + text, True))
        if shell:
            self.unread.append(SENT)
            sub = Judgement(self.parse, self.expand, self.bodies, self.loose, self.readvars)
            try:
                sub.run(text, UNKNOWN if ecwd is None or ecwd.startswith(UNKNOWN) else ecwd, whole, depth + 1)
                self.shell += [SENT if t.startswith(UNKNOWN) else t for t in sub.shell]
                self.adopt(sub)
            except Unreadable:
                self.shell.append(SENT)

    def getenv(self, name):
        """os.environ[name] as the code the command runs sees it: (known, value or None). The session's value when the
        command does not set the variable itself; unknown when it does (or may: source, eval)."""
        env, loops, drop = self.ctx
        if name in env or name in loops or name in drop or "*" in drop or name in self.prefix or "*" in self.prefix:
            return False, None
        return True, _SESSION_ENV.get(name)

    def py_argv(self, head):
        """sys.argv of the Python a command runs (its words after the program: -c's code, -, or the script), each
        expanded (None when it does not); None when the guard cannot tell."""
        if not head or not _PY.match(os.path.basename(head[0])):
            return None
        args, i = head[1:], 0
        while i < len(args) and args[i].startswith("-") and args[i] != "-":
            a = args[i]
            if not a.startswith("--") and a.endswith("c"):
                return ["-c"] + [self.expand(w) for w in args[i + 2:]]
            if not a.startswith("--") and ("c" in a[1:] or a.endswith("m")):
                return None
            i += 2 if a in ("-W", "-X") else 1
        return [self.expand(w) for w in args[i:]] or ["-"]

    def inner(self, command, ecwd, whole, depth):
        """An sh -c string or eval's words (W2-42a, failure line 2): a word that does not expand to text the guard
        knows, or a string the scan cannot read, is unresolvable; otherwise it is judged as a command."""
        if re.fullmatch(r"\$\{?[A-Za-z_]\w*\}?|\$[0-9@*#?]", command.strip()):
            value = self.expand(command.strip())
            if value is None:
                self.unread.append(SENT)
                return
            command = value
        try:
            self.sub(command, ecwd, whole, depth)
        except Unreadable:
            self.unread.append(SENT)

    def sub(self, command, ecwd, whole, depth):
        """A command inside this one (a substitution, an sh -c string, eval's words, a shell heredoc)."""
        if ecwd is None or ecwd.startswith(UNKNOWN):
            self.unknown_cwd(command, whole, depth)
        else:
            self.run(command, ecwd, whole, depth + 1)

    def unknown_cwd(self, command, whole, depth):
        """A command judged where the shell's folder is unknown: its relative targets are unresolvable."""
        sub = Judgement(self.parse, self.expand, self.bodies, self.loose, self.readvars)
        sub.run(command, UNKNOWN, whole, depth + 1)
        self.shell += [SENT if t.startswith(UNKNOWN) else t for t in sub.shell]
        self.adopt(sub)
        self.findings += sub.findings

    def making(self, args, ecwd, env, loopvals, drop):
        """mkdir's operands that expand to a path (ACT-GUARD-FIX-4, rule 5), into ``made``; options skipped
        (-m takes a value)."""
        skip = False
        for a in args:
            if skip:
                skip = False
                continue
            if a in ("-m", "--mode", "--context"):
                skip = a != "--context"
                continue
            if a.startswith("-") and len(a) > 1:
                continue
            for one in each(env, loopvals):
                with environ(one, drop):
                    exp = self.expand(a)
                if not exp or "`" in exp:
                    continue
                if not os.path.isabs(exp):
                    if ecwd is None or ecwd.startswith(UNKNOWN):
                        continue
                    exp = os.path.join(ecwd, exp)
                self.made.append(os.path.normpath(exp))

    def removal(self, args, ecwd, env, loopvals, drop):
        """rm's operands (ACT-GUARD-FIX-4, DEC-1050 (8)), into ``deletes``: each word once for each value of the loop
        words it uses; a word that does not expand is kept as the path it names if every variable the guard cannot
        resolve were empty (``rm -rf "$D"/`` is ``rm -rf /`` when D is empty), unless it guards itself (``${D:?}``).
        A relative word where the shell's folder is unknown names no path the guard can place."""
        ends = False
        for a in args:
            if not ends and a == "--":
                ends = True
                continue
            if not ends and a.startswith("-") and len(a) > 1:
                continue
            values = []
            for one in each(env, loopvals):
                with environ(one, drop):
                    exp = self.expand(a)
                    values.append(("names", exp) if exp is not None and "`" not in exp else
                                  ("if-empty", emptied(a)))
            for how, exp in dict.fromkeys(values):
                if exp is None or exp == "":
                    continue
                if exp.startswith("~"):
                    exp = os.path.expanduser(exp)  # a loop's word ~ is the home folder (the shell expands it there)
                if not os.path.isabs(exp):
                    if ecwd is None or ecwd.startswith(UNKNOWN):
                        continue
                    exp = os.path.join(ecwd, exp)
                self.deletes.append((a, exp, how))

    def place(self, raw, ecwd):
        """A target word as (text, absolute path or None); SENT when it does not expand."""
        exp = self.expand(raw)
        if exp is None or "`" in exp:
            return SENT, None
        if os.path.isabs(exp):
            return exp, os.path.normpath(exp)
        return exp, (None if ecwd is None or ecwd.startswith(UNKNOWN) else os.path.normpath(os.path.join(ecwd, exp)))

    def cd(self, name, args, ecwd):
        if name != "cd" or ecwd is None:
            return None
        if not args:
            return os.environ.get("HOME")
        if args[0].startswith("-"):
            return None
        exp = self.expand(args[0])
        if exp is None or any(c in exp for c in "*?[]{}"):
            return None
        return os.path.normpath(os.path.join(ecwd, exp))

    def inline_python(self, args, part, ecwd, whole, depth):
        i = 0
        while i < len(args) and args[i].startswith("-") and args[i] != "-":
            a = args[i]
            if not a.startswith("--") and a.endswith("c"):
                if i + 1 >= len(args):
                    return
                at = len(self.findings)
                self.code(args[i + 1], part, ecwd, whole, depth, shell_text=True,
                          argv=["-c"] + [self.expand(w) for w in args[i + 2:]])
                # The product: a -c string's writes are the command's, as a Python file it writes and runs (KPI 8);
                # the apostrophe that made the call unreadable no longer refuses it (DEC-1174 (1)).
                for targets, _scope, _code in self.findings[at:]:
                    self.writes += [SENT if raw == SENT or full is None else os.path.realpath(full)
                                    for raw, full in targets]
                return
            if not a.startswith("--") and "c" in a[1:]:
                self.findings.append(([(SENT, None)], part, True))  # -cXYZ: the code glued to the option
                return
            if a in ("-m",) or (not a.startswith("--") and a.endswith("m")):
                return
            i += 2 if a in ("-W", "-X") else 1

    def code(self, code, scope, ecwd, whole, depth, shell_text, argv=None):
        """Python code: its writes. Code the shell rewrites first is read once for each value of the variables it
        uses when the guard resolves them all (the command's own, a literal loop's words); otherwise ($(...),
        backticks, a variable it cannot resolve) it is code the guard cannot read, with the whole command as its
        scope. A target it cannot work out refuses when the code or its command names the tests in any spelling
        (round 2, F4: a glob, listdir, walk, chdir or computed path). ``argv``: the words the command gives it."""
        texts = [code]
        if shell_text and _EXPANSION.search(code):
            texts = []
            env, loops, drop = self.ctx
            if "$(" not in code and not re.search(r"(?<!\\)`", code):
                for one in each(env, loops):
                    with environ(one, drop):
                        texts.append(self.expand(code))
            if not texts or None in texts:
                texts = [code]
                self.findings.append(([(SENT, None)], whole, False))
                self.unread.append(SENT)  # the product: code the shell rewrites unpredictably (W2-42a)
        for text in dict.fromkeys(texts):
            try:
                targets = python_writes(text, ecwd, self.nested(whole), depth, argv, self.getenv)
            except (SyntaxError, ValueError, RecursionError):
                targets = [(SENT, None)]
            self.findings.append((targets, scope + "\n" + text, True))

    def nested(self, whole):
        def judge(text, cwd, depth):
            sub = Judgement(self.parse, self.expand, loose=self.loose)
            if cwd is None:
                sub.unknown_cwd(text, whole, depth)
            else:
                sub.run(text, cwd, whole, depth)
            out = [(t, t) if t != SENT else (SENT, None) for t in sub.shell]
            for targets, _scope, _code in sub.findings:
                out += targets
            return out
        return judge

    def foreign(self, body, reader, ecwd, whole, depth):
        """The product's reading of a heredoc an unknown program reads (W2-42a): a program that takes its input as
        data writes nothing by it; any other may run it as shell (flock, make, docker exec, ssh, ...), so its body
        is judged as commands, as the line parser read it before, and a body the scan cannot read is unresolvable."""
        name = os.path.basename(reader[0]) if reader else ""
        if name in _PRODUCT_DATA:
            return
        sub = Judgement(self.parse, self.expand, self.bodies, self.loose, self.readvars)
        try:
            sub.run(body["text"], UNKNOWN if ecwd is None or ecwd.startswith(UNKNOWN) else ecwd, whole, depth + 1)
        except Unreadable:
            self.unread.append(SENT)
            return
        self.writes += [SENT if t.startswith(UNKNOWN) else t for t in sub.targets()]
        self.deletes += sub.deletes  # the hook (ACT-GUARD-FIX-4): an rm in a body an unknown reader may run

    def xargs(self, reader, body, ecwd, whole, depth):
        """``xargs [options] CMD <<< WORDS`` runs CMD with the text's words as its arguments (R3, DEC-1164 (18)), and
        is judged as that command. A text the guard cannot know, an option it does not read (a replacement string, a
        delimiter, an argument file) or words it cannot split are unresolvable."""
        if not body["quoted"]:
            return  # unknown text: already unresolvable
        args, i = reader[1:], 0
        while i < len(args) and args[i].startswith("-"):
            a = args[i]
            if a == "--":
                i += 1
                break
            if a in _XARGS_FLAGS or (not a.startswith("--") and len(a) > 1 and set(a[1:]) <= set("rtxop")):
                i += 1
            elif a in ("-n", "-P", "-L", "-s", "-E") and i + 1 < len(args):
                i += 2
            elif re.fullmatch(r"-[nPLsE].+|--(max-args|max-procs|max-lines|max-chars|eof)=.*", a):
                i += 1
            else:
                self.unread.append(SENT)
                return
        cmd = args[i:]
        if not cmd:
            return  # xargs runs echo
        try:
            words = cmd + shlex.split(body["text"])
        except ValueError:
            self.unread.append(SENT)
            return
        try:
            self.sub(" ".join(shlex.quote(w) for w in words), ecwd, whole, depth)
        except Unreadable:
            self.unread.append(SENT)

    def body(self, body, kind, part, ecwd, whole, depth, argv=None, reader=None):
        if body.get("hs") and kind != "data" and not body["quoted"]:
            # A here-string's word the shell expands before its reader runs the text (R3, DEC-1164 (18)): the text is
            # known when the command's own variables give it, otherwise the reader runs code the guard cannot know.
            text = body["text"]
            value = None if "$(" in text or "`" in text else self.expand(text)
            if value is None:
                self.unread.append(SENT)
            else:
                body = dict(body, text=value, quoted=True)
        if not body["quoted"]:
            # The shell runs an unquoted body's substitutions before its reader sees the text, whoever reads it
            # (W2-42a: the Python reader and an unknown one too, not only a data reader). A shell reader too: the
            # body's comments are text to the shell that expands it, so a substitution in one runs (DEC-1174 (1)).
            text = re.sub(r"\\[\\$`]", "  ", body["text"])
            for _, _, s, e in spans(text):
                self.sub(text[s:e], ecwd, whole, depth)
        if kind == "data":
            pass
        elif kind == "python":
            self.code(body["text"], part, ecwd, whole, depth, shell_text=not body["quoted"], argv=argv)
        elif kind == "shell" and body["quoted"]:
            self.sub(body["text"], ecwd, whole, depth)
        elif kind == "shell":
            # A shell body the shell rewrites first: the hook's code it does not read (below); the product judges
            # it as the commands it is, its variables as the command's (W2-42a, KPI 1).
            self.sub(body["text"], ecwd, whole, depth)
            self.findings.append(([(SENT, None)], part + "\n" + body["text"], False))
        else:
            if kind == "code":
                if body.get("hs") and reader and os.path.basename(reader[0]) == "xargs":
                    self.xargs(reader, body, ecwd, whole, depth)
                else:
                    self.foreign(body, reader, ecwd, whole, depth)
            # code the guard does not read (an unknown reader, or a shell body the shell rewrites first)
            self.findings.append(([(SENT, None)], part + "\n" + body["text"],
                                  bool(re.search(r"\b(perl|node|ruby|php)\b", part))))


def judge(command, cwd, parse, expand):
    """The Judgement of ``command`` run at ``cwd``; Unreadable when the scan cannot read it for certain."""
    # A line continuation is removed before the text is read (round 2, F3); the whole command's naming of the tests
    # is read on both spellings.
    whole = command if "\\\n" not in command else command + "\n" + joined(command)
    j = Judgement(parse, expand)
    try:
        j.run(command, cwd, whole)
        return j
    except Unreadable as unread:
        first = unread
    # Fail closed (APOS-3/APOS-4, DEC-1174 (1)): a command the reading above cannot read (a here-string a command may
    # run; a # inside ${...} that the scan once took for a comment, which hid a later form it cannot read) is also
    # read with here-strings as data and with the earlier comment rule. Where one of those readings works, its
    # targets join what the caller gives an unreadable command (the line parser, and the unresolvable target for a
    # quote open or in a comment), so no target either reading gives is lost.
    # R3 (DEC-1164 (18)): a here-string is also read as a heredoc of its own text ("hstr", so the shell or xargs that
    # runs it is judged by it), and a heredoc with no end line as bash reads it, its rest as the body ("open").
    found, deletes = [], []
    for base, legacy, opened in product(((), ("strings",), ("hstr",)), ((), ("legacy",)), ((), ("open",))):
        loose = base + legacy + opened
        if not loose:
            continue
        try:
            again = Judgement(parse, expand, loose=frozenset(loose))
            again.run(command, cwd, whole)
        except Unreadable:
            continue
        found += again.targets()
        deletes += again.deletes
    if not found:
        raise first
    out = Judgement(parse, expand)
    out.recovered = True  # the hook (ACT-GUARD-FIX-6): the first reading failed; rm is read crudely too
    out.deletes = deletes
    out.writes = found + list(parse(command, cwd) or [])
    if "\\\n" in command:
        out.writes += list(parse(joined(command), cwd) or [])
    if isinstance(first, UnclosedQuote) or COMMENT_QUOTE.search(command):
        out.unread.append(SENT)
    return out


def reads_view(command):
    """The command as the read rules (2 and 3) are to see it: the bodies of heredocs that cat, tee and the like
    take as data cut out (they are not read from any file; an unquoted body's substitutions are kept, each as a
    command of its own), and each plain arithmetic expansion $((...)) written as 0. Anything the scan cannot read
    leaves the command as it is."""
    command2 = _ARITH.sub("0", command)
    try:
        text, bodies = heredocs(command2)
        lifted, _ = lift(text)
        cmds = simples(tokens(lifted))
    except Unreadable:
        return command2
    kinds, names, stage, staged, at = {}, {}, [], [], []
    for words, reds, sep in cmds:
        stage.append(_kind(words))
        staged.append((words, reds))
        at += [(int(m), len(stage) - 1) for r in reds for m in re.findall(r"^__gov_hdl_(\d+)__$", r[1])]
        if sep not in ("|", "|&"):
            for k, i in at:
                kinds[k] = "data" if set(stage[i:]) <= {"data"} else "code"
                names[k] = _written(staged[i:])
            stage, staged, at = [], [], []
    out, last, extra = [], 0, []
    for k, b in enumerate(bodies):
        s, e = b["span"]
        # A body written to a file the command then runs is code: kept, as before.
        if kinds.get(k) != "data" or any(n in command2[e:] for n in names.get(k, [])):
            continue
        out.append(command2[last:s])
        last = e
        if not b["quoted"]:
            text = re.sub(r"\\[\\$`]", "  ", b["text"])
            try:
                extra += [text[s2:e2] for _, _, s2, e2 in spans(text)]
            except Unreadable:
                return command2
    out.append(command2[last:])
    return "".join(out) + "".join("\n" + x for x in extra)


# -- the product's read view (W2-42a, DEC-1040 item 2) -------------------------------------------------------------

def _may_run(names, later, subs):
    """Whether a command after the one that wrote a heredoc's body to the files ``names`` (their base names) may run
    one of them: by its own name, as a shell's or Python's script, given to a program not on the list of readers, in
    a -c string or a substitution, through a pipe into xargs or a shell, or through a word that does not expand.
    Unsure: it may (fail closed). A copy of the file is followed (cp, mv, ln, install)."""
    names = set(names)
    for words, reds, _ in later:
        head = lead(words)
        if not head:
            continue
        found, code = _script_words(head, reds)
        for w, kind in found:
            base = os.path.basename(w.rstrip("/"))
            if base in names:
                return True
            if re.search(r"[$`]", w) and kind in ("exec", "shell", "python", "code"):
                return True
        texts = code + [subs[int(k)] for w in words + [r[1] for r in reds]
                        for k in re.findall(r"__gov_sub_(\d+)__", w) if int(k) < len(subs)]
        if any(n in t for n in names for t in texts):
            return True
        name = os.path.basename(head[0])
        if name in ("xargs", "parallel") or (len(found) == 1 and _kind(head) in ("shell", "python")):
            if any(n in " ".join(w + [r[1] for r in rs]) for n in names for w, rs, _ in later):
                return True
        if name in ("cp", "mv", "ln", "install") and len(head) > 2 and \
                any(os.path.basename(w.rstrip("/")) in names for w in head[1:-1] if not w.startswith("-")):
            names.add(os.path.basename(head[-1].rstrip("/")))
    return False


def read_view(command):
    """The command as the product's read judge is to read it (W2-42a, KPI 6 and 10): ``(text, codes)``.

    ``text``: the command with each plain arithmetic expansion ``$((...))`` written as 0, and without the bodies of
    the heredocs that are not shell: a data body (cat, tee, grep and the like) is read from no file, and is cut
    unless a later command may run the file it is written to (then it is kept as shell, as before); the body of a
    program's code (``python3 -``, an unknown reader) is cut and given back in ``codes``, to be judged by the files
    it names, as a ``python3 -c`` string is. An unquoted body's substitutions are run by the shell: each is kept as a
    command of its own. A shell's body (``bash <<EOF``) is kept: it is commands. Anything the scan cannot read for
    certain leaves the text as before (fail closed)."""
    command2 = _ARITH.sub("0", command)
    try:
        text, bodies = heredocs(command2)
        lifted, subs = lift(text)
        cmds = simples(tokens(lifted))
    except Unreadable:
        return command2, []
    kinds, cut_at, stage, staged, at = {}, {}, [], [], []
    for n, (words, reds, sep) in enumerate(cmds):
        stage.append(_kind(words))
        staged.append((words, reds))
        at += [(int(m), len(stage) - 1) for r in reds for m in re.findall(r"^__gov_hdl_(\d+)__$", r[1])]
        if sep not in ("|", "|&"):
            for k, i in at:
                runs = [kind for kind in stage[i:] if kind != "data"]
                kind = "data" if not runs else runs[0] if len(runs) == 1 else "code"
                if kind == "data" and _may_run(_written(staged[i:]), cmds[n + 1:], subs):
                    kind = "shell"  # a script the command may run: read as shell, as before
                kinds[k] = kind
                cut_at[k] = n
            stage, staged, at = [], [], []
    out, last, extra, codes = [], 0, [], []
    for k, b in enumerate(bodies):
        kind = kinds.get(k, "shell")
        if kind == "shell":
            continue
        s, e = b["span"]
        out.append(command2[last:s])
        last = e
        if kind != "data":
            codes.append(b["text"])
        if not b["quoted"]:
            body = re.sub(r"\\[\\$`]", "  ", b["text"])
            try:
                extra += [body[s2:e2] for _, _, s2, e2 in spans(body)]
            except Unreadable:
                return command2, []
    out.append(command2[last:])
    return "".join(out) + "".join("\n" + x for x in extra), codes
