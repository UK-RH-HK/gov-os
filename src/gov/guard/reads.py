"""Policy 2's read refusals (DEC-820, DEC-821): reads are open but for (a)
secrets and keys, (c) the counterpart's work on the session's ticket and
(d) the hidden part of an evaluation set that measures the session.  (b),
the held-out material, is ``heldout.names_held_out``'s.

(a) is refused by name, to every role: a content read that names such a
file.  (c) and (d) are a role's protected parts: globs of the project.  A
call aimed at a path at or under a part is refused whether or not it
exists; a search or listing from a folder above takes a part in only where
its files exist, unless a path or a glob keeps them out.

Nothing is opened but the protected folders that are walked for their
files, the ticket file and the path map.  No message carries a path.
"""

from __future__ import annotations

import fnmatch
import os
import re
import subprocess

from gov.guard.decide import (ACCEPTANCE, KNOWN_ROLES, LONG_REFUSAL, _ASSIGN_RE,
                              _copy_args, _expand_token, _has_glob, _is_punct,
                              _load_ticket)
from gov.guard.heldout import _words, load_yaml_unique
from gov.guard.protected import (_FIND_NAMED, _GLUED_RE, _GREP_VALUED, _MOST_RESOLVED,
                                 _PATTERN_OPTIONS, _PIECE_RE, _RG_VALUED, _Glob,
                                 _behind, _braces,
                                 _options, _shell_search, _spans, _uncommented)

PATH_MAP_REL = "governance/project/path-map.yaml"
SETS_KEY = "evaluation_sets"
BASE_BRANCH = "w2/integrate"  # DEC-826 Q2: the base is the merge base with it
# The test designer's own work, which it reads (DEC-826 Q2).
_OWN = (ACCEPTANCE + "/", ".tickets/")
# The most files of a protected part, and the most a glob word expands to,
# that the rule reads: beyond, no answer comes in bounded time (DEC-562).
_MOST_FILES = 10000
# The deepest folder a glob with ``**`` is matched against, below the path itself.
_MOST_DEPTH = 64
_GIT_TIMEOUT_S = 5
_WBS_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
_GIT_QUIET = frozenset({"--stat", "--name-only", "--name-status", "--shortstat",
                        "--numstat"})
_GIT_GREP_VALUED = frozenset("-e -f -A -B -C -m --max-depth --threads --context "
                             "--after-context --before-context --max-count".split())

SECRET_REFUSAL = ("the call reads a secret or a key (.env, .env.*, *.pem, *.key, "
                  "config/secrets*, ~/.ssh/, the CLI's key file), which is refused "
                  "to every role (DEC-820 (a))")
TESTS_REFUSAL = ("the call reads the ticket's acceptance tests, the counterpart's "
                 "work, which is refused to the ticket's engineer (DEC-820 (c)): "
                 "run them with pytest, which shows their names, results and "
                 "failure messages")
CHANGED_REFUSAL = ("the call reads code the ticket's branch changes against its "
                   "base, the counterpart's work, which is refused to the ticket's "
                   "test designer (DEC-820 (c), DEC-826 Q2): git show "
                   "w2/integrate:<path> shows the base's version")
HIDDEN_REFUSAL = ("the call reads the hidden part of an evaluation set that "
                  "measures this session, which is refused to it (DEC-820 (d), "
                  "DEC-845)")


class PolicyError(Exception):
    """What a session is refused cannot be worked out: its calls are refused
    (fail closed).  The text is fixed: it carries nothing of a file."""


class _Long(Exception):
    """The call holds more paths than the rule resolves (DEC-562, DEC-570)."""


# -- the parts -----------------------------------------------------------------

class _Part:
    """One protected part of a project: project-relative globs in the path
    map's language (``*`` stays in one folder, ``**`` crosses folders); a
    path at or under one is in the part."""

    def __init__(self, root: str, globs: list[str], reason: str,
                 files: list[str] | None = None, base: str | None = None):
        self.root, self.globs, self.reason, self.base = root, globs, reason, base
        # A literal path, or a literal folder and ``/**``, is matched by its
        # words; another glob against the path and its folders, each of the
        # glob's depth when it has one (no ``**``, no braces).
        self.lead: list[str] = []
        self.rx: list[tuple[_Glob, int | None]] = []
        for g in globs:
            head = g[:-3] if g.endswith("/**") else g
            if not any(_has_glob(p) for p in head.split("/")):
                self.lead.append(head.rstrip("/"))
                continue
            for one in ([g, head] if head != g else [g]):
                free = "**" in one or "{" in one
                self.rx.append((_Glob(one), None if free else one.count("/") + 1))
        self._files = files

    def rel(self, path: str) -> str | None:
        return path[len(self.root) + 1:] if path.startswith(self.root + "/") else None

    def inside(self, path: str) -> bool:
        rel = self.rel(path)
        if not rel:
            return False
        if any(rel == p or rel.startswith(p + "/") for p in self.lead):
            return True
        parts = rel.split("/")
        for rx, depth in self.rx:
            depths = ([depth] if depth else
                      [*range(1, min(len(parts), _MOST_DEPTH) + 1), len(parts)])
            if any(k <= len(parts) and rx.match("/".join(parts[:k])) for k in depths):
                return True
        return False

    @property
    def files(self) -> list[str]:
        """The part's files that exist, as real paths."""
        if self._files is None:
            found: set[str] = set()
            for g in self.globs:
                parts = g.split("/")
                n = next((i for i, p in enumerate(parts) if _has_glob(p)), len(parts))
                start = os.path.join(self.root, *parts[:n])
                walk = os.walk(start) if os.path.isdir(start) else (
                    [(os.path.dirname(start), [], [os.path.basename(start)])]
                    if os.path.lexists(start) else [])
                for folder, dirs, names in walk:
                    dirs[:] = [d for d in dirs if d != ".git"]
                    found |= {f for f in (os.path.join(folder, n) for n in names)
                              if self.inside(f)}
                    if len(found) > _MOST_FILES:
                        raise PolicyError("a protected part holds more files than "
                                          "the guard reads in bounded time")
            self._files = sorted(found)
        return self._files

    def below(self, folder: str | None) -> list[str]:
        if not folder:
            return []
        return [f for f in self.files if folder == "/" or f.startswith(folder + "/")]


def _ticket_wbs(root: str, ticket_id: str | None) -> str | None:
    """The WBS id of the session's ticket; ``None`` when it has no ticket
    file.  A ticket file that cannot be read for one refuses (fail closed)."""
    if not ticket_id or "/" in ticket_id:
        return None
    path = os.path.join(root, ".tickets", f"{ticket_id}.md")
    if not os.path.lexists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        head = text.split("\n---", 1)[0][4:] if text.startswith("---\n") else None
        ticket = load_yaml_unique(head) if head is not None else None
    except Exception:
        ticket = None
    wbs = ticket.get("wbs_id") if isinstance(ticket, dict) else ""
    if wbs is not None and not (isinstance(wbs, str) and _WBS_RE.fullmatch(wbs)):
        raise PolicyError("the session's ticket file cannot be read for its WBS id")
    return wbs  # None: a ticket with no WBS id names no acceptance folder


def _git(root: str, *args: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    try:
        return subprocess.run(["git", "-C", root, *args], capture_output=True,
                              text=True, timeout=_GIT_TIMEOUT_S, env=env)
    except (OSError, subprocess.SubprocessError):
        raise PolicyError("a git command the guard runs failed") from None


def _changed(root: str) -> tuple[str, list[str]] | None:
    """The merge base with ``w2/integrate`` and the files the branch changes
    against it but the tests and the tickets; ``None`` with no such branch."""
    if not os.path.lexists(os.path.join(root, ".git")):
        return None
    has = _git(root, "rev-parse", "--verify", "--quiet", BASE_BRANCH + "^{commit}")
    if has.returncode == 1 and not has.stdout.strip():
        return None
    base = _git(root, "merge-base", BASE_BRANCH, "HEAD")
    if has.returncode or base.returncode:
        raise PolicyError("git cannot name the branch's base")
    names = _git(root, "diff", "--name-only", "--no-renames", "-z",
                 base.stdout.strip(), "HEAD")
    if names.returncode:
        raise PolicyError("git cannot name the files the branch changes")
    return base.stdout.strip(), [n for n in names.stdout.split("\0")
                                 if n and not n.startswith(_OWN)]


# -- the evaluation sets (DEC-845) ---------------------------------------------

def _paths_ok(value, need: bool) -> bool:
    return isinstance(value, list) and (bool(value) or not need) and all(
        isinstance(p, str) and p and not p.startswith("/") and "\0" not in p
        and ".." not in p.split("/") for p in value)


def _measures_ok(m) -> bool:
    return isinstance(m, dict) and all(
        isinstance(m.get(k, []), list) and all(isinstance(x, str) for x in m.get(k, []))
        for k in ("roles", "tickets")) and bool(m.get("roles") or m.get("tickets"))


def set_fault(entry) -> str | None:
    """Why one evaluation set is not of the stated shape, or ``None``."""
    if not isinstance(entry, dict):
        return "a set is not a map"
    if not _paths_ok(entry.get("visible", []), False):
        return "a set's visible part is not a list of project-relative paths"
    if not _paths_ok(entry.get("hidden"), True):
        return "a set's hidden part is not a non-empty list of project-relative paths"
    if not _measures_ok(entry.get("measures")):
        return "a set's measures name no role and no ticket"
    return None


def evaluation_sets(root: str) -> dict:
    """The path map's ``evaluation_sets`` block; ``{}`` when there is none.
    A path map that cannot be read, or a block that is not a map of sets,
    raises ``PolicyError`` (fail closed, as DEC-218 for the held-out list)."""
    path = os.path.join(root, PATH_MAP_REL)
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return {}
    except (OSError, UnicodeDecodeError):
        raise PolicyError(f"{PATH_MAP_REL} cannot be read") from None
    if SETS_KEY not in text:
        return {}
    # The block alone is parsed when it is written once, as a key at the
    # start of a line, so that every call does not parse the whole map.
    lines = text.splitlines(keepends=True)
    at = [i for i, line in enumerate(lines) if line.startswith(SETS_KEY + ":")]
    if len(at) == 1:
        end = next((j for j in range(at[0] + 1, len(lines))
                    if lines[j][:1] not in ("", " ", "\t", "#", "\n", "\r")), len(lines))
        text = "".join(lines[at[0]:end])
    try:
        data = load_yaml_unique(text)
    except Exception:
        raise PolicyError(f"{PATH_MAP_REL} cannot be read") from None
    block = data.get(SETS_KEY, {}) if isinstance(data, dict) else None
    if not isinstance(block, dict):
        raise PolicyError(f"{PATH_MAP_REL}: {SETS_KEY} is not a map of sets")
    return block


def check_sets(root: str) -> None:
    """Raise ``PolicyError`` when a set is malformed (``gov launch``)."""
    for entry in evaluation_sets(root).values():
        fault = set_fault(entry)
        if fault:
            raise PolicyError(f"{PATH_MAP_REL}: {SETS_KEY}: {fault}")


def _hidden(root: str, role: str, ticket_id: str | None) -> list[str]:
    """The hidden globs of the sets that measure the session.  A malformed
    set refuses the sessions it could concern: all, unless its measures
    are well formed and name neither the role nor the ticket."""
    out: list[str] = []
    for entry in evaluation_sets(root).values():
        m = entry.get("measures") if isinstance(entry, dict) else None
        if _measures_ok(m):
            tickets = m.get("tickets", [])
            ids = {ticket_id} | ({(_load_ticket(root, ticket_id) or {}).get("wbs_id")}
                                 if tickets and ticket_id else set())
            if role not in m.get("roles", []) and ids.isdisjoint(tickets):
                continue
        fault = set_fault(entry)
        if fault:
            raise PolicyError(f"{PATH_MAP_REL}: {SETS_KEY}: {fault}")
        out += entry["hidden"]
    return out


def parts(root: str, role: str, ticket_id: str | None) -> list[_Part]:
    """The protected parts of a session of *role* on *ticket_id* (DEC-820
    (c), (d)); ``PolicyError`` when they cannot be worked out."""
    root = os.path.realpath(root)
    out: list[_Part] = []
    if role in ("engineer", "independent-test-designer"):
        wbs = _ticket_wbs(root, ticket_id)
        if role == "engineer" and wbs:
            out.append(_Part(root, [f"{ACCEPTANCE}/{wbs}"], TESTS_REFUSAL))
        changed = _changed(root) if role == "independent-test-designer" else None
        if changed:
            base, names = changed
            out.append(_Part(root, names, CHANGED_REFUSAL, base=base, files=[
                f for f in (os.path.realpath(os.path.join(root, n)) for n in names)
                if os.path.isfile(f)]))
    hidden = _hidden(root, role, ticket_id)
    if hidden:
        out.append(_Part(root, hidden, HIDDEN_REFUSAL))
    return out


def read_denials(root, role: str, ticket_id: str) -> list[str]:
    """The sandbox's ``Read`` deny rules for the session's protected parts.
    Each holds a wildcard: the CLI binds the file tools with it and, on
    Linux, skips it for the commands' sandbox, so pytest still reads them."""
    check_sets(str(root))
    rules: list[str] = []
    for part in parts(str(root), role, ticket_id):
        base = os.path.realpath(str(root))
        for g in part.globs:
            tails = ([""] if any(_has_glob(p) for p in g.split("/"))
                     else ["/**"] if part.reason == TESTS_REFUSAL
                     else ["*"] if part.base else ["*", "/**"])
            rules += [f"Read(/{base}/{g}{tail})" for tail in tails]
    return rules


# -- the judge -----------------------------------------------------------------

class _Judge:
    def __init__(self, root: str, protected: list[_Part]):
        self.root = os.path.realpath(root)
        self.parts = protected
        home = os.path.expanduser("~")
        self.ssh = os.path.realpath(os.path.join(home, ".ssh"))
        self.key = os.path.realpath(os.path.join(home, ".claude", ".credentials.json"))
        self.spent = 0  # the folders of the paths resolved so far (DEC-570)
        self.seen: dict[tuple[str, str], list[str]] = {}

    def secret(self, path: str) -> bool:
        name = os.path.basename(path)
        return (name == ".env" or name.startswith(".env.")
                or name.endswith((".pem", ".key"))
                or (name.startswith("secrets")
                    and os.path.basename(os.path.dirname(path)) == "config")
                or path == self.ssh or path.startswith(self.ssh + "/")
                or path == self.key)

    def spellings(self, text: str, cwd: str) -> list[str]:
        """A path as written and resolved, once for each path of a call; a
        call whose paths hold more folders than the rule resolves is more
        than it reads (DEC-570)."""
        key = (text, cwd)
        if key not in self.seen:
            self.spent += text.count("/") + cwd.count("/") + 1
            if self.spent > _MOST_RESOLVED:
                raise _Long
            try:
                plain = os.path.abspath(os.path.join(cwd, text))
                self.seen[key] = list(dict.fromkeys((plain, os.path.realpath(plain))))
            except (OSError, ValueError):
                self.seen[key] = []
        return self.seen[key]

    def at(self, text: str, cwd: str, secrets: bool = True) -> str:
        """Why a path at or in a protected thing is refused, or ``""``."""
        for p in self.spellings(text, cwd):
            if secrets and self.secret(p):
                return SECRET_REFUSAL
            for part in self.parts:
                if part.inside(p):
                    return part.reason
        return ""

    def above(self, text: str, cwd: str, globs: list[str] = (),
              names: list[str] | None = None, fold: bool = False) -> str:
        """Why a search or listing from *text* takes a part's files in: no
        positive glob keeps them out (a glob with no slash is a name at any
        depth), nor any of *names* (find's tests on a name)."""
        real = (self.spellings(text, cwd) or [None])[-1]
        keep = [b for g in globs if not g.startswith("!") for b in _braces(g)]
        for part in self.parts:
            for f in part.below(real):
                rel = f[len(real.rstrip("/")) + 1:]
                name = os.path.basename(f)
                cased = (lambda s: s.lower()) if fold else (lambda s: s)
                if names is not None:
                    hit = any(fnmatch.fnmatchcase(cased(name), cased(n)) for n in names)
                elif keep:
                    hit = any(_Glob(cased(g.lstrip("/"))).match(
                        cased(name if "/" not in g else rel)) for g in keep)
                else:
                    hit = True
                if hit:
                    return part.reason
        return ""

    def glob_word(self, word: str, cwd: str, secrets: bool = True) -> str:
        """A word the shell expands: refused when its folder is in a part,
        when it matches a part's file, or, with its wildcards in its last
        name alone, when a name of that one folder it matches is a secret.
        Nothing else is listed: the answer comes in bounded time."""
        segs = word.split("/")
        n = next(i for i, p in enumerate(segs) if _has_glob(p))
        lead = "/".join(segs[:n]) or ("/" if word.startswith("/") else ".")
        why = self.at(lead, cwd, False)
        start = (self.spellings(lead, cwd) or [None])[-1]
        rx = _Glob("/".join(segs[n:]))
        for part in ([] if why else self.parts):
            if any(rx.match(f[len(start.rstrip("/")) + 1:]) for f in part.below(start)):
                return part.reason
        if why or not secrets or n != len(segs) - 1 or not start:
            return why
        try:
            names = os.listdir(start)
        except OSError:
            return ""
        if len(names) > _MOST_FILES:
            return LONG_REFUSAL
        return next((SECRET_REFUSAL for name in names if (
            not name.startswith(".") or segs[-1].startswith("."))
            and rx.match(name) and self.secret(os.path.join(start, name))), "")

    def word(self, word: str, cwd: str, secrets: bool = True) -> str:
        """A word of a command: itself, each word its braces make, and the
        paths inside it that exist (a script, <rev>:<path>, --opt=<path>)."""
        exp = _expand_token(word) or word
        for one in _braces(exp):
            if one.startswith("-") and one != "-":
                continue
            why = (self.glob_word(one, cwd, secrets) if _has_glob(one)
                   else self.at(one, cwd, secrets))
            if why:
                return why
        pieces = [p for p in _PIECE_RE.split(exp) if p and p != exp]
        if _GLUED_RE.match(exp):
            pieces.append(exp[2:])
        for p in pieces:
            if not _has_glob(p) and os.path.lexists(os.path.join(cwd, p)):
                why = self.at(p, cwd, secrets)
                if why:
                    return why
        return ""

    # -- the tools ---------------------------------------------------------

    def tool(self, tool_name: str, tool_input: dict, cwd: str) -> str:
        try:
            return self._tool(tool_name, tool_input, cwd)
        except _Long:
            return LONG_REFUSAL

    def _tool(self, tool_name: str, tool_input: dict, cwd: str) -> str:
        def text(key: str) -> str:
            value = tool_input.get(key)
            return value if isinstance(value, str) else ""

        if tool_name == "Read":
            return self.at(text("file_path"), cwd) if text("file_path") else ""
        if tool_name == "Grep":
            path = text("path") or "."
            return self.at(path, cwd) or self.above(path, cwd, text("glob").split())
        if tool_name == "Glob":
            base, pattern = text("path") or ".", text("pattern")
            if pattern.startswith("/"):
                base, pattern = "/", pattern.lstrip("/")
            if not pattern:
                return self.at(base, cwd, False)
            start = (self.spellings(base, cwd) or [cwd])[-1]
            why = self.at(base, cwd, False) or (
                self.glob_lead(pattern, start) if _has_glob(pattern)
                else self.at(pattern, start, False))
            if why:
                return why
            for part in self.parts:
                for f in part.below(start):
                    rel = f[len(start.rstrip("/")) + 1:]
                    if any(_Glob(p).match(rel) for p in _braces(pattern)):
                        return part.reason
            return ""
        if tool_name == "Bash":
            command = text("command")
            for whole in [command, *(command[s:e] for s, e in _spans(command))]:
                for c in dict.fromkeys((whole, _uncommented(whole))):
                    why = self.command(c, cwd)
                    if why:
                        return why
        return ""

    def glob_lead(self, pattern: str, start: str) -> str:
        segs = pattern.split("/")
        n = next(i for i, p in enumerate(segs) if _has_glob(p))
        return self.at("/".join(segs[:n]), start, False) if n else ""

    # -- the shell ---------------------------------------------------------

    def command(self, command: str, cwd: str) -> str:
        """A Bash command, one simple command at a time; the target of an
        input redirect is read, that of an output redirect is not."""
        tokens = _words(command)
        ecwd: str | None = cwd
        cur: list[str] = []
        skip = False
        for i, tok in enumerate(tokens + [";"]):
            if skip:
                skip = False
                continue
            if not _is_punct(tok):
                cur.append(tok)
                continue
            if ("<" in tok or ">" in tok) and i + 1 < len(tokens):
                skip = True
                if "<" in tok and not tok.endswith("<<") and ">" not in tok:
                    why = self.word(tokens[i + 1], ecwd or self.root)
                    if why:
                        return why
                continue
            why, ecwd = self.simple(cur, ecwd)
            if why:
                return why
            cur = []
        return ""

    def simple(self, words: list[str], ecwd: str | None) -> tuple[str, str | None]:
        while words and _ASSIGN_RE.match(words[0]):
            words = words[1:]
        words = _behind(words)
        if not words:
            return "", ecwd
        name, args = os.path.basename(words[0]), words[1:]
        if name in ("cd", "pushd", "popd"):
            args = [a for a in args if not a.startswith("-")]
            exp = (_expand_token(args[0]) if args else
                   os.environ.get("HOME") if name == "cd" else None)
            if exp is None or _has_glob(exp) or name == "popd" or (
                    ecwd is None and not os.path.isabs(exp)):
                return "", None
            return "", os.path.join(ecwd or "/", exp)
        cwd = ecwd or self.root
        # DEC-820 (c): the engineer runs its tests and sees their results.
        if name in ("pytest", "py.test") or (
                name.startswith("python") and args[:2] == ["-m", "pytest"]):
            return "", ecwd
        if name == "git":
            return self.git(args, cwd), ecwd
        return self.reads(name, args, cwd), ecwd

    def reads(self, name: str, args: list[str], cwd: str) -> str:
        name = "grep" if name in ("egrep", "fgrep") else name
        named = not _FIND_NAMED.isdisjoint(args)
        search = _shell_search(name, list(args), named)
        for path in (search[0] if search else ()):
            exp = _expand_token(path) or path
            why = self.at(exp, cwd) or self.above(exp, cwd, search[1] + search[2],
                                                  fold=bool(search[2]))
            if why:
                return why
        if name == "find" and named:
            starts = [a for a in args[:next((i for i, a in enumerate(args)
                                             if a.startswith("-") or a in "!("),
                                            len(args))]] or ["."]
            names = [v for o, v in zip(args, args[1:]) if o in ("-name", "-iname")]
            exact = not (_FIND_NAMED - {"-name", "-iname"}).intersection(args)
            for s in starts:
                why = self.above(_expand_token(s) or s, cwd,
                                 names=names if exact else None,
                                 fold="-iname" in args)
                if why:
                    return why
        if name == "ls":  # a listing shows the names of the files in a folder
            for t in [a for a in args if not a.startswith("-")] or ["."]:
                t = _expand_token(t) or t
                real = (self.spellings(t, cwd) or [None])[-1]
                why = self.at(t, cwd, False) or next(
                    (p.reason for p in self.parts
                     if any(os.path.dirname(f) == real for f in p.files)), "")
                if why:
                    return why
        if name in ("cp", "mv"):
            parsed = _copy_args(name, list(args))
            sources = (args if parsed is None else parsed[0] if "t" in parsed[1]
                       else parsed[0][:-1])
            for s in sources:
                why = self.above(_expand_token(s) or s, cwd)
                if why:
                    return why
        skip = None
        if name in ("grep", "rg"):
            operands, options = _options(list(args), _GREP_VALUED if name == "grep"
                                         else _RG_VALUED)
            if operands and _PATTERN_OPTIONS.isdisjoint(o for o, _ in options):
                skip = operands[0]  # the text looked for
        for w in args:
            if w is skip:
                skip = None
                continue
            why = self.word(w, cwd)
            if why:
                return why
        return ""

    def git(self, args: list[str], cwd: str) -> str:
        i = 0
        while i < len(args) and args[i].startswith("-"):
            if args[i] == "-C" and i + 1 < len(args):
                cwd = os.path.join(cwd, _expand_token(args[i + 1]) or args[i + 1])
            i += 2 if args[i] in ("-C", "-c", "--git-dir", "--work-tree") else 1
        sub, rest = (args[i], args[i + 1:]) if i < len(args) else ("", [])
        if sub not in ("show", "log", "diff", "grep", "whatchanged"):
            return self.reads("git", args, cwd)
        dd = rest.index("--") if "--" in rest else len(rest)
        before, specs = rest[:dd], rest[dd + 1:]
        operands = [a for a in before if not a.startswith("-")]
        if sub == "grep":
            operands, options = _options(before, _GIT_GREP_VALUED)
            if _PATTERN_OPTIONS.isdisjoint(o for o, _ in options):
                operands = operands[1:]
            specs = [o for o in operands if os.path.lexists(os.path.join(cwd, o))] + specs
            for s in specs or ["."]:
                why = self.spec(s, cwd, True)
                if why:
                    return why
            return ""
        shown = [o for o in operands if ":" in o] if sub == "show" else []
        for o in shown:
            rev, _, path = o.partition(":")
            if not path:
                continue
            at = cwd if path.startswith(("./", "../")) else self.root
            if any(self.secret(p) for p in self.spellings(path, at)):
                return SECRET_REFUSAL
            for part in self.parts:
                if any(part.inside(p) for p in self.spellings(path, at)) and not (
                        part.base and self.base_version(rev, part.rel(
                            os.path.abspath(os.path.join(at, path))))):
                    return part.reason
        quiet = (any(a in _GIT_QUIET or a.startswith("--stat=") for a in before)
                 and not any(a in ("-p", "--patch", "-u") or a.startswith("-U")
                             for a in before))
        if sub in ("log", "whatchanged"):
            patch = not quiet and any(a in ("-p", "--patch", "-u") or a.startswith("-U")
                                      for a in before)
        else:
            patch = not quiet and (sub == "diff" or len(shown) < len(operands)
                                   or not operands)
        if patch:  # with no pathspec, the whole tree
            for s in specs or [self.root]:
                why = self.spec(s, cwd, False)
                if why:
                    return why
        return ""

    def spec(self, spec: str, cwd: str, secrets: bool) -> str:
        """A git pathspec: what it names, and the parts' files it takes in
        (``*`` in a pathspec crosses folders)."""
        if _has_glob(spec):
            for part in self.parts:
                for f in part.files:
                    rel = os.path.relpath(f, cwd)
                    if fnmatch.fnmatchcase(rel, spec) or fnmatch.fnmatchcase(
                            rel, spec.rstrip("/") + "/*"):
                        return part.reason
            return ""
        return self.at(spec, cwd, secrets) or self.above(spec, cwd)

    def base_version(self, rev: str, rel: str | None) -> bool:
        """True when *rev*'s version of a changed file is the base's."""
        base = next((p.base for p in self.parts if p.base), None)
        if not rel or not base:
            return False
        out = _git(self.root, "rev-parse", f"{rev}:{rel}", f"{base}:{rel}")
        lines = out.stdout.split()
        return out.returncode == 0 and len(lines) == 2 and lines[0] == lines[1]


def acting_role(role: str | None, subagent_type: str | None) -> str:
    """The role whose reads are judged: the subagent's type when it is a
    role, as the write rules take it; the session's otherwise."""
    if subagent_type and subagent_type in KNOWN_ROLES:
        return subagent_type
    return (role or "").strip()


def policy_refusal(tool_name: str, tool_input: dict, project_root: str, cwd: str,
                   role: str | None, ticket_id: str | None,
                   subagent_type: str | None = None) -> str:
    """Why a read tool's or a Bash call is refused under Policy 2's (a),
    (c) and (d), or ``""``.  Any error refuses (fail closed)."""
    try:
        protected = parts(project_root, acting_role(role, subagent_type), ticket_id)
        return _Judge(project_root, protected).tool(tool_name, tool_input, cwd)
    except PolicyError as exc:
        return f"{exc}: the call is refused (fail closed, DEC-820)"
    except Exception:
        return ("the guard could not work out the reads this session is refused: "
                "the call is refused (fail closed, DEC-820)")
