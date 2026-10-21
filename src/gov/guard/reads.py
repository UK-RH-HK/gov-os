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
import shlex
import subprocess

from gov.guard.decide import (ACCEPTANCE, KNOWN_ROLES, LONG_REFUSAL, _ASSIGN_RE,
                              _copy_args, _expand_token, _extract_bash_write_targets,
                              _get_allowed_paths, _has_glob, _is_punct,
                              _parse_frontmatter, _path_allowed)
from gov.guard.heldout import CONFIG_REL, SETTINGS_REL, _words, load_yaml_unique
from gov.guard.protected import (_FIND_NAMED, _GLUED_RE, _GREP_VALUED, _LS_RECURSIVE_RE,
                                 _MOST_RESOLVED, _PATTERN_OPTIONS, _PIECE_RE,
                                 _RECURSIVE_RE, _RG_VALUED, _Glob, _behind, _braces,
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
# The actions of find that open the files it finds.
_FIND_OPENS = frozenset({"-exec", "-execdir", "-ok", "-okdir"})
_GIT_QUIET = frozenset({"--stat", "--name-only", "--name-status", "--shortstat",
                        "--numstat"})
_GIT_GREP_VALUED = frozenset("-e -f -A -B -C -m --max-depth --threads --context "
                             "--after-context --before-context --max-count".split())
# The commands that open the files their words name, and git's that show a
# file's text: one fed file names at run time reads what they name.
_READERS = frozenset(
    "cat tac nl head tail less more most bat view vi vim nvim nano emacs grep egrep "
    "fgrep rg ag ack sed awk gawk mawk cut sort uniq paste join comm diff sdiff cmp "
    "colordiff od xxd hexdump strings base64 cp scp rsync tar zip gzip gunzip zcat "
    "bzip2 xz jq yq perl ruby node sh bash zsh dash source . iconv fold fmt pr "
    "column expand unexpand".split())
_GIT_SHOWS = frozenset({"show", "log", "diff", "grep", "blame", "annotate",
                        "cat-file", "whatchanged", "archive", "format-patch"})
# What passes the names of a listing on, or picks some of them.
_FILTERS = frozenset("grep egrep fgrep rg head tail sort uniq cut tr tac sed awk "
                     "cat".split())
_XARGS_VALUED = frozenset("-a -d -E -I -L -n -P -s --arg-file --delimiter "
                          "--max-args --max-procs --max-chars --process-slot-var".split())
_LS_FILES_VALUED = frozenset("-x -X --exclude --exclude-from --exclude-per-directory "
                             "--format --with-tree --abbrev".split())
# A substitution's place in a command once it is set aside (item 1).
_SUB_RE = re.compile(r"__gov_sub(\d+)__")
# The writes the write rules do not read as writes (DEC-821, no write rule
# widens): the files they write, for the two files the read rule once covered.
_SORT_VALUED = frozenset("-o -k -t -S -T --output --key --field-separator "
                         "--buffer-size --temporary-directory --parallel "
                         "--batch-size --files0-from --compress-program "
                         "--random-source --sort".split())
_RSYNC_VALUED = frozenset("-e -f --rsh --filter --exclude --include --exclude-from "
                          "--include-from --files-from --link-dest --compare-dest "
                          "--copy-dest --backup-dir --suffix --chmod --chown "
                          "--log-file --password-file --temp-dir --partial-dir".split())
_PATCH_VALUED = frozenset("-i -o -p -d -D -F -z -B -Y -V -r -g --input --output "
                          "--strip --directory --ifdef --fuzz --suffix --prefix "
                          "--basename-prefix --version-control --reject-file "
                          "--get".split())

SECRET_REFUSAL = ("the call reads a secret or a key (.env, *.env, .env.*, *.pem, *.key, "
                  "config/secrets*, a file under a .secrets folder, ~/.ssh/, the "
                  "CLI's key file), which is refused to every role (DEC-820 (a))")
RUNTIME_REFUSAL = ("the call reads files whose names another command gives at run "
                   "time, from a listing whose start the guard cannot place, and this "
                   "session is refused a part of the project (DEC-820 (c), (d)): "
                   "name the folder the listing starts at")
WRITE_FORM_REFUSAL = ("the command writes the held-out list or the settings file by a "
                      "form the write rules do not read as a write (dd of=, truncate, "
                      "sort -o, rsync, patch, git checkout, git restore), and the "
                      "role's allowed paths do not name it: refused (DEC-821, no "
                      "write rule widens)")
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


_TICKET_FAULT = "the session's ticket file cannot be read for its WBS id"


def _read_text(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        raise PolicyError(_TICKET_FAULT) from None


def _front(text: str) -> tuple[str | None, str | None]:
    """A ticket file's WBS id and id; one that cannot be read for them
    refuses (fail closed)."""
    head = text.split("\n---", 1)[0][4:] if text.startswith("---\n") else None
    try:
        import yaml  # the C parser when there is one: the guard runs on every call
        ticket = (yaml.load(head, Loader=getattr(yaml, "CSafeLoader", yaml.SafeLoader))
                  if head is not None else None)
    except Exception:
        ticket = None
    if not isinstance(ticket, dict):
        # Not YAML: the line reader the write rules use (a fixture's
        # allowed_paths may start with a *).  No front matter at all, refused.
        ticket = _parse_frontmatter(text)
        if ticket is None:
            raise PolicyError(_TICKET_FAULT)
    wbs, tid = ticket.get("wbs_id") or None, ticket.get("id") or None
    if wbs is not None and not (isinstance(wbs, str) and _WBS_RE.fullmatch(wbs)):
        raise PolicyError(_TICKET_FAULT)
    return wbs, tid if isinstance(tid, str) else None


def _ticket(root: str, ticket_id: str | None) -> tuple[set[str], str | None]:
    """The names the session's ticket goes by (the id it was given, its
    file's name, its id, its WBS id) and its WBS id.  A ticket is named by
    its file or, as the launcher and the write rules take it, by its WBS id
    (item 3); with no such ticket, the id alone and no WBS id."""
    if not ticket_id or "/" in ticket_id:
        return set(), None
    folder = os.path.join(root, ".tickets")
    path = os.path.join(folder, f"{ticket_id}.md")
    if os.path.lexists(path):
        wbs, tid = _front(_read_text(path))
        return {ticket_id, tid, wbs} - {None}, wbs
    try:
        names = sorted(os.listdir(folder))
    except FileNotFoundError:
        return {ticket_id}, None
    except OSError:
        raise PolicyError(_TICKET_FAULT) from None
    # A file that gives the WBS id a line of its own is read in full.
    line = re.compile(r"^wbs_id:[ \t]*['\"]?" + re.escape(ticket_id) + r"['\"]?[ \t]*$",
                      re.M)
    for name in names:
        if not name.endswith(".md"):
            continue
        text = _read_text(os.path.join(folder, name))
        if not line.search(text):
            continue
        wbs, tid = _front(text)
        if wbs == ticket_id:
            return {ticket_id, name[:-3], tid} - {None}, wbs
    return {ticket_id}, None


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
    are well formed and name neither the role nor the ticket (by any name
    it goes by)."""
    out: list[str] = []
    for entry in evaluation_sets(root).values():
        m = entry.get("measures") if isinstance(entry, dict) else None
        if _measures_ok(m):
            tickets = m.get("tickets", [])
            ids = _ticket(root, ticket_id)[0] if tickets else set()
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
        wbs = _ticket(root, ticket_id)[1]
        if role == "engineer" and wbs:
            out.append(_Part(root, [f"{ACCEPTANCE}/{wbs}/**"], TESTS_REFUSAL))
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


# -- the shell's words ---------------------------------------------------------

def _moved(name: str, args: list[str], ecwd: str | None) -> str | None:
    """The folder a cd, pushd or popd moves to; ``None`` when it is not known."""
    args = [a for a in args if not a.startswith("-")]
    exp = (_expand_token(args[0]) if args else
           os.environ.get("HOME") if name == "cd" else None)
    if exp is None or _has_glob(exp) or name == "popd" or (
            ecwd is None and not os.path.isabs(exp)):
        return None
    return os.path.join(ecwd or "/", exp)


def _tests_run(name: str, args: list[str]) -> bool:
    return name in ("pytest", "py.test") or (
        name.startswith("python") and args[:2] == ["-m", "pytest"])


def _xargs(args: list[str]) -> tuple[list[str], bool]:
    """The command xargs runs, and whether its names come from a file (-a)."""
    i, from_file = 0, False
    while i < len(args) and args[i].startswith("-") and args[i] != "-":
        a = args[i]
        from_file = from_file or a in ("-a", "--arg-file") or a.startswith(
            ("--arg-file=", "-a"))
        i += 2 if a in _XARGS_VALUED else 1
    return args[i:], from_file


def _reads_files(words: list[str]) -> bool:
    """True when the command opens the files its words name (item 1)."""
    words = _behind(words)
    if not words:
        return False
    name, args = os.path.basename(words[0]), words[1:]
    if _tests_run(name, args):
        return False
    if name == "xargs":
        return _reads_files(_xargs(args)[0])
    if name == "git":
        i = 0
        while i < len(args) and args[i].startswith("-"):
            i += 2 if args[i] in ("-C", "-c", "--git-dir", "--work-tree") else 1
        return args[i:i + 1] != [] and args[i] in _GIT_SHOWS
    return name in _READERS or name.startswith("python")


def _simples(tokens: list[str]) -> list[tuple[list[str], str]]:
    """The simple commands of a token list, each with the punctuation after
    it; a redirect and its target are no words of the command."""
    out: list[tuple[list[str], str]] = []
    cur: list[str] = []
    skip = False
    for i, tok in enumerate(tokens):
        if skip:
            skip = False
            continue
        if not _is_punct(tok):
            if not (tok.isdigit() and tokens[i + 1:i + 2]
                    and _is_punct(tokens[i + 1]) and tokens[i + 1][0] in "<>"):
                cur.append(tok)
            continue
        if ("<" in tok or ">" in tok) and i + 1 < len(tokens):
            skip = True
            continue
        out.append((cur, tok.strip(" \t") or ";"))
        cur = []
    out.append((cur, ""))
    return out


def _pipelines(cmds: list[tuple[list[str], str]]) -> list[list[list[str]]]:
    """The pipelines of a list of simple commands, each as its stages' words."""
    out: list[list[list[str]]] = [[]]
    for words, sep in cmds:
        out[-1].append(words)
        if sep not in ("|", "|&"):
            out.append([])
    return [p for p in out if any(p)]


def _set_aside(command: str) -> tuple[str, list[str]]:
    """*command* with each outermost ``$(...)`` and backtick substitution
    replaced by a word of its own, and the commands they hold."""
    outer: list[tuple[int, int, int, int]] = []  # its text's ends, its command's
    for s, e in sorted(_spans(command)):
        if command[s - 2:s] == "$(":
            a, b = s - 2, min(e + 1, len(command))
        elif command[s - 1:s] == "`":
            a, b = s - 1, min(e + 1, len(command))
        else:
            continue  # <(...) and >(...) give a file, not names
        if outer and a < outer[-1][1]:
            continue  # inside one set aside already
        outer.append((a, b, s, e))
    text, subs, at = [], [], 0
    for a, b, s, e in outer:
        text.append(command[at:a] + f" __gov_sub{len(subs)}__ ")
        subs.append(command[s:e])
        at = b
    return "".join(text) + command[at:], subs


# -- the judge -----------------------------------------------------------------

class _Judge:
    def __init__(self, root: str, protected: list[_Part], may_write=None):
        self.root = os.path.realpath(root)
        self.parts = protected
        # Whether the acting role's allowed paths take a path in (item 5).
        self.may_write = may_write
        home = os.path.expanduser("~")
        self.ssh = os.path.realpath(os.path.join(home, ".ssh"))
        self.key = os.path.realpath(os.path.join(home, ".claude", ".credentials.json"))
        self.two = {os.path.join(self.root, rel) for rel in (CONFIG_REL, SETTINGS_REL)}
        self.two |= {os.path.realpath(p) for p in self.two}
        self.spent = 0  # the folders of the paths resolved so far (DEC-570)
        self.seen: dict[tuple[str, str], list[str]] = {}

    def secret(self, path: str) -> bool:
        name = os.path.basename(path)
        # *.env and a .secrets folder at any depth: the repository's own
        # names for provider credentials (.gitignore; item 4).
        return (name.endswith(".env") or name.startswith(".env.")
                or name == ".secrets" or "/.secrets/" in path
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
            if why or "**" in pattern:
                return why  # with **, a listing from above, which shows names
            # Without **, the pattern names the files it lists: aimed at them.
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
            for c in dict.fromkeys((command, _uncommented(command))):
                why = self.runtime(c, cwd)
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
        # DEC-557: an rg fed by a pipe or an input redirect searches what
        # feeds it; in a line with a background job nothing is taken as fed.
        jobs = any(_is_punct(t) and t.strip("\n;()") == "&" for t in tokens)
        fed = False
        for i, tok in enumerate(tokens + [";"]):
            if skip:
                skip = False
                continue
            if not _is_punct(tok):
                # The number of a redirect (2>&1, 0<x) is no word (DEC-570).
                if not (tok.isdigit() and tokens[i + 1:i + 2]
                        and _is_punct(tokens[i + 1]) and tokens[i + 1][0] in "<>"):
                    cur.append(tok)
                continue
            if ("<" in tok or ">" in tok) and i + 1 < len(tokens):
                skip = True
                if "<" in tok and not tok.endswith("<<") and ">" not in tok:
                    why = self.word(tokens[i + 1], ecwd or self.root)
                    if why:
                        return why
                    fed = fed or (tok == "<" and not jobs)
                continue
            why, ecwd = self.simple(cur, ecwd, fed)
            if why:
                return why
            cur = []
            fed = tok in ("|", "|&") and not jobs
        return ""

    def simple(self, words: list[str], ecwd: str | None,
               fed: bool = False) -> tuple[str, str | None]:
        while words and _ASSIGN_RE.match(words[0]):
            words = words[1:]
        words = _behind(words)
        if not words:
            return "", ecwd
        name, args = os.path.basename(words[0]), words[1:]
        if name in ("cd", "pushd", "popd"):
            return "", _moved(name, args, ecwd)
        cwd = ecwd or self.root
        why = self.rewrites(name, args, cwd)
        if why:
            return why, ecwd
        # DEC-820 (c): the engineer runs its tests and sees their results.
        if _tests_run(name, args):
            return "", ecwd
        if name == "git":
            return self.git(args, cwd), ecwd
        return self.reads(name, args, cwd, fed), ecwd

    # -- the writes the write rules do not see (item 5) ----------------------

    def rewrites(self, name: str, args: list[str], cwd: str) -> str:
        """Why a write the write rules do not read as one, of the held-out
        list or the settings file, is refused: the acting role's allowed
        paths do not take the file in."""
        if self.may_write is None:
            return ""
        targets: list[str] = []
        if name == "dd":
            targets = [a[3:] for a in args if a.startswith("of=")]
        elif name == "truncate":
            targets = _options(args, frozenset({"-s", "-r", "--size", "--reference"}))[0]
        elif name == "sort":
            targets = [v for o, v in _options(args, _SORT_VALUED)[1]
                       if o in ("-o", "--output")]
        elif name == "rsync":
            targets = _options(args, _RSYNC_VALUED)[0][1:][-1:]
        elif name == "patch":
            operands, options = _options(args, _PATCH_VALUED)
            targets = operands[:1] + [v for o, v in options if o in (
                "-o", "--output", "-r", "--reject-file")]
        elif name == "git":
            i = 0
            while i < len(args) and args[i].startswith("-"):
                if args[i] == "-C" and i + 1 < len(args):
                    cwd = os.path.join(cwd, _expand_token(args[i + 1]) or args[i + 1])
                i += 2 if args[i] in ("-C", "-c", "--git-dir", "--work-tree") else 1
            if args[i:i + 1] in (["checkout"], ["restore"]):
                targets = [a for a in args[i + 1:] if a != "--" and not a.startswith("-")]
        for t in targets:
            exp = _expand_token(t)
            if exp is None:
                continue  # a word the hook cannot resolve names neither file
            hits = [p for p in self.spellings(exp, cwd) if p in self.two]
            if hits and not all(self.may_write(p) for p in hits):
                return WRITE_FORM_REFUSAL
        return ""

    def listed(self, text: str, cwd: str, names: list[str] | None = None,
               fold: bool = False) -> str:
        """Why a listing of the folder *text* shows a part's file by name: one
        that lies in it, matched by one of *names* when there are any."""
        real = (self.spellings(text, cwd) or [None])[-1]
        cased = (lambda s: s.lower()) if fold else (lambda s: s)
        return next((p.reason for p in self.parts for f in p.files
                     if os.path.dirname(f) == real and (names is None or any(
                         fnmatch.fnmatchcase(cased(os.path.basename(f)), cased(n))
                         for n in names))), "")

    def reads(self, name: str, args: list[str], cwd: str, fed: bool = False) -> str:
        name = "grep" if name in ("egrep", "fgrep") else name
        named = not _FIND_NAMED.isdisjoint(args)
        search = _shell_search(name, list(args), named)
        if name == "rg" and fed and "--files" not in args:
            operands, options = _options(list(args), _RG_VALUED)
            if len(operands) <= _PATTERN_OPTIONS.isdisjoint(o for o, _ in options):
                search = None  # it names no path: it searches what feeds it
        # A listing shows names (ls, find with no action that opens a file,
        # rg --files): from a folder above it takes no part in.
        opens = name == "find" and not _FIND_OPENS.isdisjoint(args)
        listing = name == "ls" or (name == "find" and not opens) or (
            name == "rg" and "--files" in args)
        for path in (search[0] if search else ()):
            exp = _expand_token(path) or path
            why = self.at(exp, cwd) or (not listing and self.above(
                exp, cwd, search[1] + search[2], fold=bool(search[2])))
            if why:
                return why
        if name == "find" and named:
            starts = [a for a in args[:next((i for i, a in enumerate(args)
                                             if a.startswith("-") or a in "!("),
                                            len(args))]] or ["."]
            names = [v for o, v in zip(args, args[1:]) if o in ("-name", "-iname")]
            names = names if not (_FIND_NAMED - {"-name", "-iname"}).intersection(args) else None
            for s in starts:
                s = _expand_token(s) or s
                why = (self.above(s, cwd, names=names, fold="-iname" in args) if opens
                       else self.listed(s, cwd, names, "-iname" in args))
                if why:
                    return why
        if name == "ls":  # a listing shows the names of the files in a folder
            for t in [a for a in args if not a.startswith("-")] or ["."]:
                t = _expand_token(t) or t
                why = self.at(t, cwd, False) or self.listed(t, cwd)
                if why:
                    return why
        # A write target of its own command is the allow-list's (as the read
        # rule of the two files left it): it judges it and names it.
        written = set(_extract_bash_write_targets(
            " ".join(shlex.quote(w) for w in [name, *args]), cwd) or ())

        # The destination of a copy, a move or an install (its -t value, or
        # its last operand), also where it replaces a link (DEC-774).
        parsed = _copy_args(name, list(args)) if name in ("cp", "mv", "install") else None
        dests = set(parsed[1].get("t", []) or parsed[0][-1:] if parsed and (
            "t" in parsed[1] or len(parsed[0]) > 1) else [])

        def theirs(word: str) -> bool:
            """A write target, or the folder one lands in (cp -t <folder>)."""
            exp = _expand_token(word) or word
            if word in dests:
                return True
            return bool(written) and not _has_glob(exp) and any(
                t == s or t.startswith(s.rstrip("/") + "/")
                for s in self.spellings(exp, cwd) for t in written)

        if name in ("cp", "mv"):
            parsed = _copy_args(name, list(args))
            sources = (args if parsed is None else parsed[0] if "t" in parsed[1]
                       else parsed[0][:-1])
            for s in sources:
                why = "" if theirs(s) else self.above(_expand_token(s) or s, cwd)
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
            if theirs(w):
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

    # -- file names given at run time (item 1) -------------------------------

    def runtime(self, command: str, cwd: str) -> str:
        """Why a read whose file names another command gives at run time is
        refused: a pipe into xargs, a ``while read`` loop fed by a pipe, a
        substitution in a reading command's words (or in a ``for`` loop's
        list that a reading command walks).  The listing is judged as a
        search from where it starts."""
        text, subs = _set_aside(command)
        for body in subs:  # one inside another
            why = self.runtime(body, cwd)
            if why:
                return why
        cmds = _simples(_words(text))
        ecwd: str | None = cwd
        where: list[str | None] = []
        for words, _ in cmds:
            where.append(ecwd)
            plain = _behind(words)
            if plain and os.path.basename(plain[0]) in ("cd", "pushd", "popd"):
                ecwd = _moved(os.path.basename(plain[0]), plain[1:], ecwd)
        for i, (words, _) in enumerate(cmds):
            bare = [w for w in words if not _ASSIGN_RE.match(w)]
            plain = _behind(words)
            if not plain:
                continue
            # The stages of the pipeline that feeds this command.
            k = i
            while k and cmds[k - 1][1] in ("|", "|&"):
                k -= 1
            feed = [w for w, _ in cmds[k:i]]
            listings: list[list[list[str]]] = []
            if bare[:1] in (["while"], ["until"]) and "read" in bare:
                if self._body_reads(cmds, i):
                    # Not fed by a pipe: names from a redirect, no listing it can place.
                    listings.append(feed or [["cat", "--"]])
            elif os.path.basename(plain[0]) == "xargs":
                run, from_file = _xargs(plain[1:])
                if _reads_files(run):
                    if from_file:
                        listings.append([["cat", "--"]])  # no listing it can place
                    elif feed:
                        listings.append(feed)
            held = [int(n) for w in words for n in _SUB_RE.findall(w)]
            if held and not _SUB_RE.search(plain[0]) and (
                    self._body_reads(cmds, i) if bare[:1] == ["for"]
                    else _reads_files(words)):
                for n in held:
                    if n < len(subs):
                        listings += _pipelines(_simples(_words(subs[n])))
            for stages in listings:
                why = self.listing(stages, where[k] if stages is feed else where[i])
                if why:
                    return why
        return ""

    @staticmethod
    def _body_reads(cmds: list[tuple[list[str], str]], i: int) -> bool:
        """True when the loop that starts at command *i* runs a reading
        command (up to its ``done``)."""
        depth = 0
        for words, _ in cmds[i:]:
            first = next((w for w in words if not _ASSIGN_RE.match(w)), "")
            if first in ("while", "until", "for", "select"):
                depth += 1
            elif first == "done":
                depth -= 1
                if depth <= 0:
                    return False
            elif _reads_files(words):  # behind a do, too
                return True
        return False

    def listing(self, stages: list[list[str]], cwd: str | None) -> str:
        """Why the names a listing gives take in a part's files that exist;
        a listing whose start the guard cannot place refuses a session that
        has such files, and no other (fail closed)."""
        if not any(p.files for p in self.parts):
            return ""
        if cwd is None:
            return RUNTIME_REFUSAL
        placed = False
        for words in stages:
            words = _behind(words)
            if not words or any(_SUB_RE.search(w) for w in words):
                return RUNTIME_REFUSAL
            kind, why = self.lists(os.path.basename(words[0]), words[1:], cwd)
            if why:
                return why
            # A listing with a word the hook cannot resolve is not placed.
            if kind is None or (kind and any(_expand_token(w) is None for w in words)):
                return RUNTIME_REFUSAL
            placed = placed or kind
        return "" if placed else RUNTIME_REFUSAL

    def lists(self, name: str, args: list[str], cwd: str) -> tuple[bool | None, str]:
        """``(True, why)`` for a listing judged from where it starts,
        ``(False, "")`` for a filter of names, ``(None, "")`` for a command
        whose output the guard cannot place."""
        args = [_expand_token(a) or a for a in args]
        name = "grep" if name in ("egrep", "fgrep") else name
        if name == "find":
            while args and args[0] in ("-H", "-L", "-P"):
                args = args[1:]
            n = next((i for i, a in enumerate(args) if a.startswith("-") or a in "!("),
                     len(args))
            tests = args[n:]
            names = [v for o, v in zip(tests, tests[1:]) if o in ("-name", "-iname")]
            if not names or {"!", "-not"} & set(tests) or (
                    _FIND_NAMED - {"-name", "-iname"}) & set(tests):
                names = None  # only a positive test on the name narrows it
            fold = "-iname" in tests
            return True, next((why for s in args[:n] or ["."] for why in [
                self.at(s, cwd, False) or self.above(s, cwd, names=names, fold=fold)]
                if why), "")
        if name == "git":
            i = 0
            while i < len(args) and args[i].startswith("-"):
                if args[i] == "-C" and i + 1 < len(args):
                    cwd = os.path.join(cwd, args[i + 1])
                i += 2 if args[i] in ("-C", "-c", "--git-dir", "--work-tree") else 1
            sub, rest = (args[i], args[i + 1:]) if i < len(args) else ("", [])
            if sub == "ls-files":
                specs = _options(rest, _LS_FILES_VALUED)[0]
            elif sub == "grep":
                dd = rest.index("--") if "--" in rest else len(rest)
                operands, options = _options(rest[:dd], _GIT_GREP_VALUED)
                if _PATTERN_OPTIONS.isdisjoint(o for o, _ in options):
                    operands = operands[1:]
                specs = [o for o in operands if os.path.lexists(os.path.join(cwd, o))]
                specs += rest[dd + 1:]
            else:
                return None, ""
            if not specs or any(s.startswith(":") for s in specs):
                specs = ["."]  # a magic pathspec is not read: the whole tree
            return True, next((why for s in specs for why in [self.spec(s, cwd, False)]
                               if why), "")
        if name in ("grep", "rg"):
            listed = name == "rg" and not {"--files", "-l", "--files-with-matches", "-L",
                                           "--files-without-match"}.isdisjoint(args)
            search = _shell_search(name, list(args), False)
            if name == "grep" and search is None:
                operands, options = _options(list(args), _GREP_VALUED)
                if _PATTERN_OPTIONS.isdisjoint(o for o, _ in options):
                    operands = operands[1:]
                if not operands:
                    return False, ""  # it picks some of the names fed to it
                search = (operands, [], [])
            elif name == "rg" and not listed:
                return False, ""
            for p in search[0]:
                why = self.at(p, cwd) or self.above(p, cwd, search[1] + search[2],
                                                    fold=bool(search[2]))
                if why:
                    return True, why
            return True, ""
        if name == "ls":
            deep = any(_LS_RECURSIVE_RE.match(a) for a in args)
            for t in [a for a in args if not a.startswith("-")] or ["."]:
                why = self.at(t, cwd, False) or (
                    self.above(t, cwd) if deep else self.listed(t, cwd))
                if why:
                    return True, why
            return True, ""
        if name in ("echo", "printf"):
            return True, next((why for a in args for why in [self.at(a, cwd, False)]
                               if why), "")
        if name in _FILTERS:
            return False, ""
        return None, ""


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
    (c) and (d), or ``""``.  A subagent is refused what its session's role
    is refused on the ticket and what its own type is refused (item 2).
    A Bash write of the held-out list or the settings file that the write
    rules do not read as one is judged by the acting role's allowed paths
    (item 5).  Any error refuses (fail closed)."""
    try:
        session = (role or "").strip()
        acting = acting_role(role, subagent_type)
        protected = [p for r in dict.fromkeys((session, acting))
                     for p in parts(project_root, r, ticket_id)]
        may_write = None
        if tool_name == "Bash":
            pats: list[str] | None = None

            def may_write(path: str) -> bool:
                nonlocal pats
                if pats is None:
                    pats = _get_allowed_paths(acting, ticket_id, project_root,
                                              session_role=session)
                return _path_allowed(path, project_root, pats, acting)
        return _Judge(project_root, protected, may_write).tool(tool_name, tool_input, cwd)
    except PolicyError as exc:
        return f"{exc}: the call is refused (fail closed, DEC-820)"
    except Exception:
        return ("the guard could not work out the reads this session is refused: "
                "the call is refused (fail closed, DEC-820)")
