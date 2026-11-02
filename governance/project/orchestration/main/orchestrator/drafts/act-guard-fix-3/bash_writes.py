"""What a Bash command writes, for the five-rule hook's rules 1 and 5 (ACT-GUARD-FIX-3, DEC-958).

The product's write parser (gov.guard.decide._extract_bash_write_targets) reads one shell line. It does not know
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

Whatever the scan cannot read for certain (unbalanced quotes, an unterminated heredoc, ``<<`` in arithmetic, an
unknown reader) falls back to the judgement before this fix (fail closed). Nothing here runs the command.
"""
import ast
import os
import re
import shlex
import warnings
from contextlib import contextmanager
from itertools import product

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
_OPENS = ("{", "(", "!", "if", "then", "else", "elif", "do", "while", "until", "time")
_STARTS = frozenset(("if", "while", "until", "for", "case", "{", "("))
_ENDS = frozenset(("fi", "done", "esac", "}", ")"))
_A_PATH = re.compile(r"[^\s'\"]*tests/acceptance(/[^\s'\"]*)?")
_ARITH = re.compile(r"\$\(\(([A-Za-z0-9_\s+\-*%$]*)\)\)")
_INLINE = re.compile(r"\b(python3?|perl|node|ruby)\s+(-\w*\s+)*-[cei]\b")


class Unreadable(Exception):
    """The scan cannot read the command for certain: the caller judges it as before this fix."""


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

def heredocs(command):
    """``command`` without its heredoc bodies, and the bodies. Each heredoc operator and its delimiter become
    ``< __gov_hdl_<k>__`` (an input redirect the parser skips), so the reader is known by position. Raises
    Unreadable for anything the scan cannot read for certain."""
    out, bodies, pending = [], [], []
    # The shell's contexts: "top"; '"' (double quotes); "$(" (a command substitution, whose quoting starts
    # afresh, with the depth of its own parentheses); "`" (a backtick substitution); "((" (arithmetic).
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
                raise Unreadable("an unclosed single quote")
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
        if c == "#" and (not out or out[-1][-1:] in " \t\n;&|("):
            end = command.find("\n", i)
            end = n if end < 0 else end
            out.append(command[i:end])
            i = end
            continue
        if command.startswith("<<", i) and not command.startswith("<<<", i):
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
            pending.append((delim, strip, quoted, len(bodies) + len(pending)))
            out.append(f" < __gov_hdl_{pending[-1][3]}__ ")
            i = k
            continue
        if c == "\n" and pending:
            out.append("\n")
            i += 1
            for delim, strip, quoted, _ in pending:
                start, lines = i, []
                while True:
                    if i >= n:
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
    if len(stack) > 1 or pending:
        raise Unreadable("unbalanced quotes or a heredoc with no body")
    return "".join(out), bodies


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
        return env, loopvals, set(names)
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
                all(not re.search(r"[$`*?\[\]{}~]", v) for v in loop[0][0]):
            loopvals[name] = loop[0][0]
        else:
            drop.add(name)
    combos = 1
    for vals in loopvals.values():
        combos *= len(vals)
    if combos > MOST_VARIANTS:
        drop |= set(loopvals)
        loopvals = {}
    return env, loopvals, drop


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


def python_writes(code, ecwd, judge, depth, argv=None):
    """The targets ``code`` writes, as (raw text, absolute path or None); SENT for one it cannot work out. ``judge``
    judges a command the code runs (a literal subprocess or os.system command). ``argv``: the words the command
    gives the code (sys.argv, each None when it does not expand), when known. Raises SyntaxError."""
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
                "append", "extend", "insert", "pop", "remove", "clear", "reverse", "sort", "__setitem__"):
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
    "isort yamllint".split())
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
            i += 2 if args[i] in ("-o", "+o", "-O", "+O", "--rcfile", "--init-file") else 1
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
        operands = [a for a in args if not a.startswith("-")]
        if any("c" in o.lstrip("-") for o in opts if not o.startswith("--")):
            return "data"
        return "shell" if not operands or "-s" in opts else "data"
    return "data" if name in _DATA else "code"


class Judgement:
    """What a Bash command writes: the shell's own targets (rule 5 reads these), and the findings in the code it
    runs inline (rule 1 reads both). ``findings`` is a list of (targets, scope, code): ``scope`` is the text whose
    naming of the acceptance tests refuses an unresolvable target; ``code``: it is code (Python, perl or node, a
    script body), whose naming counts in any spelling (names_tests)."""

    def __init__(self, parse, expand, bodies=None):
        self.parse = parse    # the product's parser: (command, cwd) -> targets or None
        self.expand = expand  # the product's word expansion: (word) -> text or None
        self.shell, self.findings = [], []
        self.bodies = [] if bodies is None else bodies  # every heredoc body met, nested commands' too
        self.ctx = ({}, {}, set())  # the variables of the command being walked

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
        text, bodies = heredocs(command)
        base = len(self.bodies)
        self.bodies += bodies
        # This command's own heredocs get their number among all met so far (a nested command's marks are
        # already numbered so).
        text = re.sub(r"__gov_hdl_(\d+)__", lambda m: f"__gov_heredoc_{base + int(m.group(1))}__", text)
        text, subs = lift(text)

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
                        self.sub(subs[k], ecwd, whole, depth)
                self.ctx = (env, loopvals, drop)
                head = lead(words)
                name = os.path.basename(head[0]) if head else ""
                args = head[1:]
                part = " ".join(words)
                for names, body in scripts:
                    self.script(names, body, head, reds, subs, part, ecwd, whole, depth)
                if name in ("cd", "pushd", "popd"):
                    ecwd = self.cd(name, args, ecwd)
                elif name in _SHELLS and any(_short(a, "c") for a in args):
                    i = next(i for i, a in enumerate(args) if _short(a, "c"))
                    if i + 1 < len(args):
                        self.sub(args[i + 1], ecwd, whole, depth)
                elif name == "eval":
                    self.sub(" ".join(args), ecwd, whole, depth)
                elif _PY.match(name):
                    self.inline_python(args, part, ecwd, whole, depth)
                elif name in ("git", "dd", "truncate", "sort", "rsync", "patch"):
                    # Writes the product's parser does not read (rule 1 judges them; rule 5 as before). A patch
                    # applied writes the files it names: unknown targets, judged by the whole command.
                    if _applies_patch(name, args):
                        self.findings.append(([(SENT, None)], whole, False))
                    targets = [self.place(t, where) for t, where in _more_targets(name, args, ecwd)]
                    if targets:
                        self.findings.append((targets, part, False))
                elif _INLINE.search(part):
                    # perl, node, ruby: code the guard does not read (ACT-GUARD-FIX-2's judgement of the part; any
                    # spelling of the tests' folder counts, round 2, F4)
                    self.findings.append(([(SENT, None)], part, True))
                stage.append(_kind(words))
                staged.append((words, reds))
                held += [(int(m), len(stage) - 1, part, ecwd)
                         for r in reds for m in re.findall(r"^__gov_heredoc_(\d+)__$", r[1])]
                if sep not in ("|", "|&"):
                    for k, at, part_, where in held:
                        # The body is read by its own command and, through a pipe, by the stages after it:
                        # data if all of them take it as data; the one that runs it otherwise; code (unknown)
                        # if more than one could.
                        runs = [kind for kind in stage[at:] if kind != "data"]
                        kind = "data" if not runs else runs[0] if len(runs) == 1 else "code"
                        reader = next((lead(w) for (w, _), kd in zip(staged[at:], stage[at:]) if kd == kind), [])
                        self.body(self.bodies[k], kind, part_, where, whole, depth, argv=self.py_argv(reader))
                        if kind == "data":
                            targets = _written(staged[at:], raw=True)
                            if targets:
                                scripts.append(({self.basename(t) for t in targets}, self.bodies[k]))
                    stage, held, staged = [], [], []

    def basename(self, word):
        """The name of the file a word names, or None when it does not expand."""
        exp = self.expand(word)
        return None if exp is None or "`" in exp else os.path.basename(exp.rstrip("/"))

    def script(self, names, body, head, reds, subs, part, ecwd, whole, depth):
        """A command after one that wrote a data heredoc's body to a file (ACT-GUARD-FIX-3 round 2, F2): when it may
        run that file, the body is judged as the code it then is. A run the guard reads (bash or sh, source, python,
        the file's own name, after a cd too) is judged as shell or Python; any other command given the file's name,
        and a run whose script word does not expand (a loop's variable, $S), is code the guard cannot read: refused
        under rule 1 when the body names the tests, and judged as shell under rule 5, as before this fix."""
        if not head:
            return
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
        if how is None:
            texts = code + [subs[int(k)] for w in head + [r[1] for r in reds]
                            for k in re.findall(r"__gov_sub_(\d+)__", w)]
            if any(n and n in t for n in names for t in texts):
                how = "unknown-python" if _PY.match(os.path.basename(head[0])) else "unknown"
        name = os.path.basename(head[0])
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
            self.code(body["text"], part, ecwd, whole, depth, shell_text=not body["quoted"], argv=argv)
        elif how == "shell" and (body["quoted"] or not _EXPANSION.search(body["text"])):
            self.script_shell(body["text"], part, ecwd, whole, depth)
        else:
            self.unknown_script(body["text"], part, ecwd, whole, depth, shell=how != "unknown-python")

    def script_shell(self, text, part, ecwd, whole, depth):
        """A script file's shell body, run by this command: its writes are the command's (rule 5); under rule 1 a
        target that names the tests refuses wherever the script runs, and one it cannot work out refuses when the
        body names them."""
        sub = Judgement(self.parse, self.expand, self.bodies)
        try:
            sub.run(text, UNKNOWN if ecwd is None or ecwd.startswith(UNKNOWN) else ecwd, whole, depth + 1)
        except Unreadable:
            self.unknown_script(text, part, ecwd, whole, depth, shell=True)
            return
        shell = [SENT if t.startswith(UNKNOWN) else t for t in sub.shell]
        self.shell += shell
        self.findings += sub.findings
        self.findings.append(([(SENT, None) if t == SENT else (t, os.path.normpath(t) if os.path.isabs(t) else None)
                               for t in shell], part + "\n" + text, True))

    def unknown_script(self, text, part, ecwd, whole, depth, shell):
        """A script file run by a form the guard cannot read: refused under rule 1 when the body names the tests;
        under rule 5 its body is read as shell, as before this fix (``shell``; not a Python body run by Python,
        which rule 5 never read)."""
        self.findings.append(([(SENT, None)], part + "\n" + text, True))
        if shell:
            sub = Judgement(self.parse, self.expand, self.bodies)
            try:
                sub.run(text, UNKNOWN if ecwd is None or ecwd.startswith(UNKNOWN) else ecwd, whole, depth + 1)
                self.shell += [SENT if t.startswith(UNKNOWN) else t for t in sub.shell]
            except Unreadable:
                self.shell.append(SENT)

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

    def sub(self, command, ecwd, whole, depth):
        """A command inside this one (a substitution, an sh -c string, eval's words, a shell heredoc)."""
        if ecwd is None or ecwd.startswith(UNKNOWN):
            self.unknown_cwd(command, whole, depth)
        else:
            self.run(command, ecwd, whole, depth + 1)

    def unknown_cwd(self, command, whole, depth):
        """A command judged where the shell's folder is unknown: its relative targets are unresolvable."""
        sub = Judgement(self.parse, self.expand, self.bodies)
        sub.run(command, UNKNOWN, whole, depth + 1)
        self.shell += [SENT if t.startswith(UNKNOWN) else t for t in sub.shell]
        self.findings += sub.findings

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
                self.code(args[i + 1], part, ecwd, whole, depth, shell_text=True,
                          argv=["-c"] + [self.expand(w) for w in args[i + 2:]])
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
        for text in dict.fromkeys(texts):
            try:
                targets = python_writes(text, ecwd, self.nested(whole), depth, argv)
            except (SyntaxError, ValueError, RecursionError):
                targets = [(SENT, None)]
            self.findings.append((targets, scope + "\n" + text, True))

    def nested(self, whole):
        def judge(text, cwd, depth):
            sub = Judgement(self.parse, self.expand)
            if cwd is None:
                sub.unknown_cwd(text, whole, depth)
            else:
                sub.run(text, cwd, whole, depth)
            out = [(t, t) if t != SENT else (SENT, None) for t in sub.shell]
            for targets, _scope, _code in sub.findings:
                out += targets
            return out
        return judge

    def body(self, body, kind, part, ecwd, whole, depth, argv=None):
        if kind == "data":
            if not body["quoted"]:
                text = re.sub(r"\\[\\$`]", "  ", body["text"])
                for _, _, s, e in spans(text):
                    self.sub(text[s:e], ecwd, whole, depth)
        elif kind == "python":
            self.code(body["text"], part, ecwd, whole, depth, shell_text=not body["quoted"], argv=argv)
        elif kind == "shell" and body["quoted"]:
            self.sub(body["text"], ecwd, whole, depth)
        else:
            # code the guard does not read (an unknown reader, or a shell body the shell rewrites first)
            self.findings.append(([(SENT, None)], part + "\n" + body["text"],
                                  bool(re.search(r"\b(perl|node|ruby|php)\b", part))))


def judge(command, cwd, parse, expand):
    """The Judgement of ``command`` run at ``cwd``; Unreadable when the scan cannot read it for certain."""
    j = Judgement(parse, expand)
    # A line continuation is removed before the text is read (round 2, F3); the whole command's naming of the tests
    # is read on both spellings.
    j.run(command, cwd, command if "\\\n" not in command else command + "\n" + joined(command))
    return j


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
