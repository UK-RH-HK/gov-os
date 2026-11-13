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

import copy
import fnmatch
import os
import re
import shlex
import stat
import subprocess

from gov.guard import bash_writes, runs
from gov.guard.decide import (ACCEPTANCE, KNOWN_ROLES, LONG_REFUSAL, _ASSIGN_RE,
                              _copy_args, _expand_token, _line_write_targets,
                              _get_allowed_paths, _has_glob, _is_punct,
                              _path_allowed)
from gov.guard.heldout import CONFIG_REL, SETTINGS_REL, _words
from gov.guard.protected import (_FIND_NAMED, _GLUED_RE, _GREP_VALUED, _LS_RECURSIVE_RE,
                                 _MOST_RESOLVED, _PATTERN_OPTIONS, _PIECE_RE,
                                 _RECURSIVE_RE, _RG_VALUED, _Glob, _behind, _braces,
                                 _options, _shell_search, _spans, _uncommented)
# W2-150 (DEC-1109 (2)): the parts, the ticket's names and the evaluation sets live in gov.util.parts, so that memory
# reads them without the guard; every name stays a name of this module.
from gov.util.parts import (_LONG_PART, _MOST_DEPTH, _MOST_FILES, _TICKET_FAULT,  # noqa: F401
                            _WALK_FAULT, _WBS_RE, HIDDEN_REFUSAL, PATH_MAP_REL, SETS_KEY,
                            PolicyError, _front, _measures_ok, _Part, _paths_ok, _read_text,
                            _related, _ticket, _walk, _walk_fault, evaluation_sets, set_fault)

BASE_BRANCH = "w2/integrate"  # DEC-826 Q2: the base is the merge base with it
# The test designer's own work, which it reads (DEC-826 Q2).
_OWN = (ACCEPTANCE + "/", ".tickets/")
_GIT_TIMEOUT_S = 5
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
# The interpreter's flags that take no code and no file, before -m pytest
# (DEC-880 item 1); -W and -X take a word.
_PYTHON_FLAGS = frozenset("-B -u -O -OO -E -s -I".split())
# coverage run's options before -m pytest: --rcfile, which reads a file, is
# none of them.
_COVERAGE_FLAGS = frozenset("-a --append --branch -L --pylib -p --parallel-mode "
                            "--timid".split())
_COVERAGE_VALUED = frozenset("--concurrency --context --data-file --debug --include "
                             "--omit --source --save-signal".split())
# A substitution's place in a command once it is set aside (item 1).
_SUB_RE = re.compile(r"__gov_sub(\d+)__")
_NUMERIC_RE = re.compile(r"[-+]?[0-9]+(\.[0-9]+)?")
# date +FORMAT of numeric fields only: its output is digits and separators, no slash (W2-42a).
_DATE_FORMAT_RE = re.compile(r"\+(%[sYmdHMSNjuwyekIFTRGgVUWCz]|[-_:.T0-9])+")
_WC_COUNTS = frozenset("-l -c -w -m -L --lines --bytes --words --chars --max-line-length".split())
# The words of a program's code in a heredoc, judged as paths (W2-42a): split where no path goes on.
_CODE_PIECE_RE = re.compile(r"""[\s'"()\[\]{},;=<>|&`]+""")
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
# W2-84: the hidden part under every tree, fail closed (DEC-950 item 1).
_TREES_FAULT = "the repository's worktrees cannot be listed"
_RUNS_FAULT = "the runs root cannot be read"
_CLONE_FAULT = "the repository's trees cannot be found from this run clone"
_REV_FAULT = "git cannot say whether a revision holds the hidden part"
# The options of a patch route that widen or choose its sides, carried into
# the guard's own question; a count is carried too (W2-84).
_GIT_SIDES = frozenset("--all --branches --tags --remotes -g --walk-reflogs --reflog "
                       "--cached --staged --merge-base".split())
_COUNT_RE = re.compile(r"-\d+|-n\d+|--max-count=\d+")
_GIT_LOG_VALUED = frozenset("-S -G -O -L --author --committer --grep --since --until "
                            "--after --before --skip --max-age --min-age".split())
_ARCHIVE_VALUED = frozenset("-o --output --format --prefix --remote --exec "
                            "--add-file --add-virtual-file".split())
_NO_CONVERT = ("--no-ext-diff", "--no-textconv", "--name-only", "--no-renames")


class _Long(Exception):
    """The call holds more paths than the rule resolves (DEC-562, DEC-570)."""


# -- the parts: _Part is gov.util.parts' (W2-150) ------------------------------

class _Runs(_Part):
    """The runs root's hidden part (W2-84): a path below the root is in it when
    the globs match it relative to any folder below the root, at any depth,
    whatever the clone's layout.  *names* are the root as named and real."""

    def __init__(self, names: list[str], globs: list[str], entries: list[str]):
        super().__init__(names[-1], globs, HIDDEN_REFUSAL)
        self.names, self.entries = names, entries
        self._walked: dict[str, list[str]] = {}

    def inside(self, path: str) -> bool:
        for top in self.names:
            if path.startswith(top + "/"):
                parts = path[len(top) + 1:].split("/")
                return any(self.match("/".join(parts[k:])) for k in range(len(parts)))
        return False

    def under(self, path: str) -> bool:
        return any(_related(path, top) for top in self.names)

    def held(self) -> bool:
        return bool(self.entries)

    @property
    def files(self) -> list[str]:
        return self.below(self.root)

    def below(self, folder: str | None) -> list[str]:
        """Walked below the start, or whole from above it, never into ``.git``;
        bounded, and a folder that cannot be walked refuses."""
        if not folder or not _related(folder, self.root):
            return []
        start = folder if len(folder) > len(self.root) else self.root
        if start not in self._walked:
            found: list[str] = []
            spent = 0
            for top, dirs, names in _walk(start, True):
                dirs[:] = [d for d in dirs if d != ".git"]
                found += [f for f in (os.path.join(top, n) for n in names) if self.inside(f)]
                spent += 1
                if spent + len(found) > _MOST_FILES:
                    raise PolicyError(_LONG_PART)
            self._walked[start] = found
        return self._walked[start]


def _pathspecs(hidden: list[_Part]) -> list[str]:
    """The hidden globs as git pathspecs from the tree's top: each and all below it."""
    heads = {b[:-3] if b.endswith("/**") else b for h in hidden for g in h.globs
             for b in _braces(g) if "{" not in b}
    return [f":(top,glob){one}" for h in sorted(heads) for one in (h, h + "/**")]


# -- _related, _walk, _walk_fault and the session's ticket (_read_text, _front, _ticket): gov.util.parts' (W2-150)

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


# -- the evaluation sets (DEC-845): _paths_ok, _measures_ok, set_fault and evaluation_sets are gov.util.parts' (W2-150)

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


def _worktrees(at: str, fault: str) -> list[str]:
    """The real paths of the trees ``git worktree list`` names for the
    repository at *at*; one that cannot be listed refuses with *fault*."""
    try:
        out = _git(at, "worktree", "list", "--porcelain", "-z")
    except PolicyError:
        raise PolicyError(fault) from None
    if out.returncode:
        raise PolicyError(fault)
    return [os.path.realpath(f[9:]) for f in out.stdout.split("\0")
            if f.startswith("worktree ")]


def _clone_trees(own: str) -> list[str]:
    """The trees of the repository whose launch made the own folder *own*,
    from its marker (DEC-751): a regular file, not a link, naming a git
    common directory."""
    try:
        fd = os.open(os.path.join(own, runs.MARKER), os.O_RDONLY | os.O_NOFOLLOW)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise PolicyError(_CLONE_FAULT)
            common = os.read(fd, 4097).decode("utf-8").strip()
        finally:
            os.close(fd)
    except (OSError, UnicodeDecodeError):
        raise PolicyError(_CLONE_FAULT) from None
    if not os.path.isabs(common) or not os.path.isfile(os.path.join(common, "HEAD")):
        raise PolicyError(_CLONE_FAULT)
    return _worktrees(common, _CLONE_FAULT)


def _trees(root: str) -> tuple[list[str], list[str], list[str]]:
    """The trees of the session's repository, the runs root's names (as
    named and real) and its entries (W2-84).  The trees are *root* and
    those ``git worktree list`` names; for a session in a run clone, also
    the repository's whose launch made its own folder.  Whatever cannot be
    had refuses: nothing falls back to the session's own tree."""
    trees = [root]
    if os.path.lexists(os.path.join(root, ".git")):
        trees += _worktrees(root, _TREES_FAULT)
    named = runs.root()
    names = [] if named is None else list(dict.fromkeys((named, os.path.realpath(named))))
    entries: list[str] = []
    if names:
        try:
            entries = os.listdir(names[-1])
        except FileNotFoundError:
            pass
        except OSError:
            raise PolicyError(_RUNS_FAULT) from None
        top = next((n for n in names if root.startswith(n + "/")), None)
        if top:
            trees += _clone_trees(os.path.join(top, root[len(top) + 1:].split("/")[0]))
    return list(dict.fromkeys(trees)), names, entries


def parts(root: str, role: str, ticket_id: str | None,
          found: dict | None = None) -> list[_Part]:
    """The protected parts of a session of *role* on *ticket_id* (DEC-820
    (c), (d)); ``PolicyError`` when they cannot be worked out.  The hidden
    part lies under every tree and the runs root, found once per call in
    *found* (W2-84)."""
    root = os.path.realpath(root)
    out: list[_Part] = []
    if role in ("engineer", "independent-test-designer"):
        wbs = _ticket(root, ticket_id)[1]
        if role == "engineer" and wbs:
            own = _Part(root, [f"{ACCEPTANCE}/{wbs}/**"], TESTS_REFUSAL)
            own.wbs = wbs  # W2-141: a search that can reach it is told how to keep it out
            out.append(own)
        changed = _changed(root) if role == "independent-test-designer" else None
        if changed:
            base, names = changed
            out.append(_Part(root, names, CHANGED_REFUSAL, base=base, files=[
                f for f in (os.path.realpath(os.path.join(root, n)) for n in names)
                if os.path.isfile(f)]))
    hidden = _hidden(root, role, ticket_id)
    if hidden:
        found = {} if found is None else found
        if "trees" not in found:
            found["trees"] = _trees(root)
        trees, names, entries = found["trees"]
        out += [_Part(t, hidden, HIDDEN_REFUSAL) for t in trees]
        if names:
            out.append(_Runs(names, hidden, entries))
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


def _coverage_pytest(args: list[str]) -> bool:
    """True when *args* are ``run [its options] -m pytest …``; an option
    that reads a file (--rcfile) is none of them."""
    if args[:1] != ["run"]:
        return False
    i = 1
    while i < len(args) and args[i] != "-m":
        a = args[i]
        if a in _COVERAGE_FLAGS or ("=" in a and a.split("=", 1)[0] in _COVERAGE_VALUED):
            i += 1
        elif a in _COVERAGE_VALUED:
            i += 2
        else:
            return False
    return args[i:i + 2] == ["-m", "pytest"]


def _tests_run(name: str, args: list[str]) -> bool:
    """True when the command runs pytest (DEC-820 (c)): itself, an
    interpreter with flags that take no code or file, or under coverage
    (DEC-880 item 1)."""
    if name in ("pytest", "py.test"):
        return True
    if name == "coverage":
        return _coverage_pytest(args)
    if not name.startswith("python"):
        return False
    i = 0
    while i < len(args) and args[i] != "-m":
        a = args[i]
        if a in _PYTHON_FLAGS or (a[:2] in ("-W", "-X") and len(a) > 2):
            i += 1
        elif a in ("-W", "-X"):
            i += 2
        else:
            return False
    rest = args[i + 1:]
    return rest[:1] == ["pytest"] or (rest[:1] == ["coverage"]
                                      and _coverage_pytest(rest[1:]))


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


def _arithmetic(command: str, s: int, e: int) -> bool:
    """Whether the ``$(`` whose command runs from *s* to *e* (its closing
    parenthesis) is an arithmetic expansion ``$((...))``, as bash reads it:
    the parenthesis after ``$(`` closes just before the one that ends it
    (W2-42a, KPI 6)."""
    if command[s:s + 1] != "(" or e - 1 <= s:
        return False
    depth = 0
    for i in range(s, e):
        if command[i] == "(":
            depth += 1
        elif command[i] == ")":
            depth -= 1
            if depth == 0:
                return i == e - 1
    return False


def _names_used(loop: list[str], command: str, subs: list[str]) -> bool:
    """Whether the names a ``for`` loop's list gives can reach a command
    (W2-42a, KPI 10): its variable is named anywhere in the command but at
    the loop's own head (after the loop too: it keeps its last value), or the
    command may read a variable by another name (``${!``, ``eval``, a name
    reference, ``declare``/``typeset``/``local``/``export``).  A wait loop
    over ``$(seq ...)`` that greps one literal file uses none."""
    if len(loop) < 2 or not re.fullmatch(r"[A-Za-z_]\w*", loop[1]):
        return True
    text = command + "\n" + "\n".join(subs)
    if re.search(r"\$\{!|\beval\b|\bdeclare\b|\btypeset\b|\blocal\b|\bexport\b|\bsource\b|(?<![\w/.-])\.\s", text):
        return True
    uses = re.findall(rf"(?<![\w]){re.escape(loop[1])}(?!\w)", text)
    return len(uses) > 1


def _single_quoted(command: str) -> list[tuple[int, int]]:
    """Where *command*'s single-quoted text lies, as the shell reads it
    (W2-42a): an apostrophe inside double quotes or after a backslash opens
    none.  Unsure (a heredoc is left in the text, or a quote is not closed):
    none, so every substitution is taken as one (fail closed)."""
    if "'" not in command or "<<" in command or "$'" in command:
        return []
    out: list[tuple[int, int]] = []
    double, i = False, 0
    while i < len(command):
        c = command[i]
        if c == "\\":
            i += 2
            continue
        if c == '"':
            double = not double
        elif c == "'" and not double:
            end = command.find("'", i + 1)
            if end < 0:
                return []
            out.append((i, end + 1))
            i = end + 1
            continue
        i += 1
    return [] if double else out


def _set_aside(command: str) -> tuple[str, list[str]]:
    """*command* with each outermost ``$(...)`` and backtick substitution
    replaced by a word of its own, and the commands they hold.  An
    arithmetic expansion is none (W2-42a): what it holds is set aside on its
    own."""
    outer: list[tuple[int, int, int, int]] = []  # its text's ends, its command's
    quoted = _single_quoted(command)
    for s, e in sorted(_spans(command)):
        if command[s - 2:s] == "$(" and _arithmetic(command, s, e):
            continue
        if any(a <= s - 1 < b for a, b in quoted):
            continue  # inside single quotes: text, not a substitution (W2-42a)
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


# -- W2-141: what a search keeps out (DEC-1093 (2), DEC-1102) ------------------
# An engineer's search that can reach its own ticket's acceptance folder is
# refused unless the call keeps the folder out, and the refusal says how.  A
# file is taken in or kept out as the tool itself would: rg's globs (the Grep
# tool's too) as gitignore lines from the session's folder, the last that
# matches winning; grep's --exclude-dir (a folder's base name), --include and
# --exclude; ag's --ignore; ack's --ignore-dir; find's -prune and its negated
# -path and -name tests, -maxdepth; Glob's pattern; git grep's and git
# ls-files's pathspecs, their exclusions (:!, :^, :(exclude)) too.  An option
# word with braces is read as the words Bash makes of it.  The same block is
# in the hook's role_reads.py, which does not import it from the pinned product.
# BEGIN W2-141 BLOCK

SEARCH_REFUSAL = ("the search can reach {folder}, the ticket's own acceptance tests, the "
                  "counterpart's work, which is refused to the ticket's engineer (DEC-820 "
                  "(c), DEC-1093 (2)): {how}")
X_HOW = {
    "Grep": ("exclude it with the glob !tests/acceptance/{w}/** (Grep's glob, from the "
             "session's folder; !**/{w}/** from any folder), or search a path that does "
             "not hold it"),
    "grep": ("exclude it with --exclude-dir={w} (grep matches a folder's base name, never "
             "a path), or search a folder that does not hold it"),
    "rg": ("exclude it with -g '!tests/acceptance/{w}/**' (from the session's folder; "
           "-g '!**/{w}/**' from any folder), or search a folder that does not hold it"),
    "ag": "exclude it with --ignore-dir={w}, or search a folder that does not hold it",
    "ack": "exclude it with --ignore-dir={w}, or search a folder that does not hold it",
    "find": ("exclude it with -name {w} -prune -o ... (or -not -path '*/{w}/*'), or "
             "start from a folder that does not hold it"),
    "Glob": ("Glob has no exclusion: give a path or a pattern that cannot reach it (src/, "
             "or a pattern under another folder)"),
    "git": ("exclude it with the pathspec ':!tests/acceptance/{w}' after -- (git grep "
            "PATTERN -- . ':!tests/acceptance/{w}', from the repository's root), or give "
            "pathspecs that do not hold it"),
}
_X_GIT_VALUED = {
    "grep": frozenset("-e -f -m -A -B -C --max-count --context --after-context "
                      "--before-context --max-depth --threads".split()),
    "ls-files": frozenset("-x -X --exclude --exclude-from --exclude-per-directory "
                          "--format --with-tree".split()),
}
_X_BRACE = re.compile(r"\{([^{},]*,[^{}]*)\}")
_X_GREP_VALUED = frozenset(
    "-e -f -m -A -B -C -d -D --regexp --file --include --exclude --exclude-dir "
    "--exclude-from --max-count --context --after-context --before-context "
    "--directories --devices --label --binary-files --group-separator".split())
_X_RG_VALUED = frozenset(
    "-e -f -g -t -T -m -A -B -C -j -M -d -E -r --regexp --file --glob --iglob --type "
    "--type-not --type-add --type-clear --max-count --context --after-context "
    "--before-context --threads --max-columns --max-depth --maxdepth --encoding --sort "
    "--sortr --replace --ignore-file --pre --pre-glob --max-filesize "
    "--path-separator --context-separator --field-match-separator --engine".split())
_X_AG_VALUED = frozenset(
    "-A -B -C -G -g -m -p -W --after --before --context --file-search-regex --ignore "
    "--ignore-dir --max-count --depth --path-to-ignore --pager --workers "
    "--width".split())
_X_ACK_VALUED = frozenset(
    "-A -B -C -m -g --after-context --before-context --context --max-count "
    "--ignore-dir --ignore-directory --noignore-dir --noignore-directory --ignore-file "
    "--type --type-add --type-set --type-del --output --pager --match "
    "--files-from".split())
_X_PATTERN = frozenset({"-e", "-f", "--regexp", "--file"})
# The readers a find's action or an xargs runs: they print or copy what they open.
X_READERS = frozenset(
    "cat tac nl less more bat batcat head tail cmp diff colordiff od xxd hexdump "
    "strings base64 uniq sort cut fold fmt paste column expand unexpand rev iconv "
    "grep egrep fgrep zgrep rg ag ack sed awk gawk mawk nawk jq yq cp".split())
_X_FIND_PATHS = frozenset("-path -wholename -ipath -iwholename".split())
_X_FIND_NAMES = frozenset("-name -iname".split())
_X_FIND_OPENS = frozenset("-exec -execdir -ok -okdir".split())


def x_glob(pattern: str) -> "re.Pattern[str]":
    """A glob as a whole-path matcher: ``**`` crosses folders, ``*`` and
    ``?`` stay in one name, ``[...]`` one character, ``{a,b}`` either."""
    def part(p: str) -> str:
        out, i = [], 0
        while i < len(p):
            if p.startswith("**/", i):
                out.append("(?:.*/)?")
                i += 3
            elif p.startswith("**", i):
                out.append(".*")
                i += 2
            elif p[i] == "*":
                out.append("[^/]*")
                i += 1
            elif p[i] == "?":
                out.append("[^/]")
                i += 1
            elif p[i] == "[" and p.find("]", i + 2) > 0:
                j = p.find("]", i + 2)
                body = p[i + 1:j]
                body = "^" + body[1:] if body[:1] in "!^" else body
                out.append("[" + body.replace("\\", "\\\\") + "]")
                i = j + 1
            elif p[i] == "{" and p.find("}", i) > 0 and "," in p[i:p.find("}", i)]:
                j = p.find("}", i)
                out.append("(?:" + "|".join(part(a) for a in p[i + 1:j].split(",")) + ")")
                i = j + 1
            else:
                out.append(re.escape(p[i]))
                i += 1
        return "".join(out)
    return re.compile("(?s)" + part(pattern) + r"\Z")


def _x_parse(args: list[str], valued: frozenset):
    """(operands, [(option, value)], short flag letters): a value glued, after
    ``=``, or the next word; after ``--`` every word is an operand."""
    operands, options, letters = [], [], set()
    i = 0
    while i < len(args):
        a = args[i]
        i += 1
        if a == "--":
            operands += args[i:]
            break
        if not a.startswith("-") or a == "-":
            operands.append(a)
        elif a.startswith("--"):
            opt, eq, val = a.partition("=")
            if opt in valued and not eq and i < len(args):
                val, i = args[i], i + 1
            options.append((opt, val))
        else:
            for j in range(1, len(a)):
                opt = "-" + a[j]
                if opt in valued:
                    val = a[j + 1:]
                    if not val and i < len(args):
                        val, i = args[i], i + 1
                    options.append((opt, val))
                    break
                letters.add(a[j])
                options.append((opt, ""))
    return operands, options, letters


def _x_rel(f: str, start: str) -> list[str]:
    return f[len(start.rstrip("/")) + 1:].split("/")


def _x_depth(keep, depth):
    try:
        most = int(depth)
    except (TypeError, ValueError):
        return keep
    return lambda f, start, word, cwd: (len(_x_rel(f, start)) <= most
                                        and keep(f, start, word, cwd))


def _x_rg(globs: list[tuple[str, bool]]):
    """rg's -g/--iglob (and the Grep tool's globs): gitignore lines matched
    against the path from the session's folder; the last that matches wins; a
    folder kept out is not walked; with a positive glob, a file no glob
    matches is not searched."""
    rules = []
    for g, fold in globs:
        neg = g.startswith("!")
        body = g[1:] if neg else g
        body = body.lower() if fold else body
        only_dir = body.endswith("/")
        body = body.rstrip("/")
        if body.startswith("/"):
            body = body[1:]
        elif "/" not in body:
            body = "**/" + body
        if body:
            rules.append((x_glob(body), only_dir, neg, fold))
    white = any(not neg for _rx, _d, neg, _f in rules)

    def verdict(path: str, is_dir: bool):
        last = None
        for rx, only_dir, neg, fold in rules:
            if (is_dir or not only_dir) and rx.match(path.lower() if fold else path):
                last = neg
        return last

    def keep(f: str, start: str, word: str, cwd: str | None) -> bool:
        def view(p: str) -> str:
            if cwd and p.startswith(cwd.rstrip("/") + "/"):
                return p[len(cwd.rstrip("/")) + 1:]
            return p
        at = start.rstrip("/")
        for name in _x_rel(f, start)[:-1]:
            at += "/" + name
            if verdict(view(at), True) is True:
                return False
        found = verdict(view(f), False)
        return not (found is True or (found is None and white))
    return keep


def _x_grep(rules: list[tuple[str, str]]):
    """grep -r's --exclude-dir (a folder's base name), --include and
    --exclude (a file's base name: the last that matches wins; none, and the
    file is searched unless the first is --include)."""
    import fnmatch as fm
    dirs = [g.rstrip("/") for k, g in rules if k == "exclude-dir"]
    files = [(k, g) for k, g in rules if k in ("include", "exclude")]

    def keep(f: str, start: str, word: str, cwd: str | None) -> bool:
        rel = _x_rel(f, start)
        if any(fm.fnmatchcase(d, g) for d in rel[:-1] for g in dirs):
            return False
        last = None
        for k, g in files:
            if fm.fnmatchcase(rel[-1], g):
                last = k
        return (not files or files[0][0] != "include") if last is None else last == "include"
    return keep


def _x_ag(pats: list[str]):
    """ag's --ignore and --ignore-dir: a name at any depth, or a path from
    where the search starts."""
    import fnmatch as fm

    def keep(f: str, start: str, word: str, cwd: str | None) -> bool:
        rel = _x_rel(f, start)
        for p in pats:
            q = p.strip("/") or p
            if "/" in q:
                rx = x_glob(q)
                if any(rx.match("/".join(rel[:k])) for k in range(1, len(rel) + 1)):
                    return False
            elif any(fm.fnmatchcase(n, q) for n in rel):
                return False
        return True
    return keep


def _x_ack(rules: list[tuple[bool, str]]):
    """ack's --ignore-dir (NAME, is:NAME, match:REGEX), undone by a later
    --noignore-dir."""
    def gone(d: str) -> bool:
        out = False
        for add, spec in rules:
            if spec.startswith("match:"):
                try:
                    hit = bool(re.search(spec[6:], d))
                except re.error:
                    hit = False
            else:
                hit = (spec[3:] if spec.startswith("is:") else spec).rstrip("/") == d
            out = add if hit else out
        return out

    def keep(f: str, start: str, word: str, cwd: str | None) -> bool:
        return not any(gone(d) for d in _x_rel(f, start)[:-1])
    return keep


def _x_test(t: str, v: str, printed: str, name: str) -> bool:
    import fnmatch as fm
    s = printed if t in _X_FIND_PATHS else name
    if t.startswith("-i"):
        s, v = s.lower(), v.lower()
    return fm.fnmatchcase(s, v)


def _x_find(expr: list[str]):
    """find's expression: TEST -prune -o ... and ( TEST -o TEST ) -prune -o
    ... keep a folder out (not under -depth); with no -o after them, a
    negated -path or -name keeps a file out and a positive one must hold;
    -maxdepth bounds the depth."""
    pruned: list[tuple[str, str]] = []
    rest = list(expr)
    tests = _X_FIND_PATHS | _X_FIND_NAMES
    harmless = {"-type": "d", "-maxdepth": None, "-mindepth": None, "-xdev": "",
                "-mount": ""}
    while "-prune" in rest and "-depth" not in expr:
        k = rest.index("-prune")
        if rest[k + 1:k + 2] not in (["-o"], ["-or"]):
            break
        head = rest[:k]
        if head[-1:] == [")"] and "(" in head:
            m = len(head) - 1 - head[::-1].index("(")
            inner, pre, group = head[m + 1:-1], head[:m], []
            alts = [[]]
            for a in inner:
                if a in ("-o", "-or"):
                    alts.append([])
                else:
                    alts[-1].append(a)
            if not all(len(x) == 2 and x[0] in tests for x in alts):
                break
            group = [(x[0], x[1]) for x in alts]
        elif len(head) >= 2 and head[-2] in tests:
            group, pre = [(head[-2], head[-1])], head[:-2]
        else:
            break
        i, ok = 0, True
        while i < len(pre):  # only -type d and the global options before it
            a = pre[i]
            if a in ("-a", "-and"):
                i += 1
            elif a in harmless and harmless[a] == "":
                i += 1
            elif a in harmless and i + 1 < len(pre) and (harmless[a] is None
                                                         or pre[i + 1] == harmless[a]):
                i += 2
            else:
                ok = False
                break
        if not ok:
            break
        pruned += group
        rest = rest[k + 2:]
    negated: list[tuple[str, str]] = []
    positive: list[tuple[str, str]] | None = []
    if any(a in ("-o", "-or", ",") for a in rest):
        positive = None  # an alternative: no test on the file is trusted
    else:
        i = 0
        while i < len(rest):
            a = rest[i]
            if a in ("!", "-not") and i + 2 < len(rest) and rest[i + 1] in tests:
                negated.append((rest[i + 1], rest[i + 2]))
                i += 3
            elif a in tests and i + 1 < len(rest):
                positive.append((a, rest[i + 1]))
                i += 2
            else:
                i += 1
    depth = next((expr[k + 1] for k, a in enumerate(expr[:-1]) if a == "-maxdepth"), None)

    def keep(f: str, start: str, word: str, cwd: str | None) -> bool:
        rel = _x_rel(f, start)
        base = word.rstrip("/")
        for k in range(1, len(rel) + 1):
            printed = base + "/" + "/".join(rel[:k])
            if any(_x_test(t, v, printed, rel[k - 1]) for t, v in pruned):
                return False
        printed = base + "/" + "/".join(rel)
        if any(_x_test(t, v, printed, rel[-1]) for t, v in negated):
            return False
        return positive is None or all(_x_test(t, v, printed, rel[-1]) for t, v in positive)
    return _x_depth(keep, depth)


def x_glob_tool(pattern: str):
    """The Glob tool's pattern, from its path (a pattern with no folder in it
    at any depth, as rg's --files reads it) or from the session's folder."""
    rx = x_glob(pattern.lstrip("/"))

    def keep(f: str, start: str, word: str, cwd: str | None) -> bool:
        rel = "/".join(_x_rel(f, start))
        if rx.match(rel) or ("/" not in pattern and rx.match(os.path.basename(f))):
            return True
        return bool(cwd) and f.startswith(cwd.rstrip("/") + "/") and bool(
            rx.match(f[len(cwd.rstrip("/")) + 1:]))
    return keep


def x_grep_tool_globs(glob: str) -> list[tuple[str, bool]]:
    """The Grep tool's glob parameter as the globs it gives rg: split on
    whitespace, and on commas outside braces."""
    out: list[tuple[str, bool]] = []
    for g in (glob or "").split():
        out += [(g, False)] if "{" in g and "}" in g else [(p, False) for p in g.split(",") if p]
    return out


def _x_braces(word: str) -> list[str]:
    """The words Bash makes of *word*'s braces ({a,b}), at most 256."""
    out, todo = [], [word]
    while todo and len(out) + len(todo) <= 256:
        w = todo.pop(0)
        m = _X_BRACE.search(w)
        if m:
            todo += [w[:m.start()] + alt + w[m.end():] for alt in m.group(1).split(",")]
        else:
            out.append(w)
    return out + todo


def _x_top(cwd: str | None) -> str | None:
    """The tree that holds *cwd*: the nearest folder at or above it with a .git."""
    at = cwd
    while at and at != "/":
        if os.path.lexists(os.path.join(at, ".git")):
            return at
        at = os.path.dirname(at)
    return None


def _x_pathspec(spec: str):
    """A git pathspec as (exclude, top, icase, glob, pattern): its long magic
    :(exclude,top,icase,glob) or its short magic :! :^ :/."""
    ex = top = fold = glob = False
    if spec.startswith(":(") and ")" in spec:
        magic = spec[2:spec.index(")")].split(",")
        ex, top = "exclude" in magic, "top" in magic
        fold, glob = "icase" in magic, "glob" in magic
        spec = spec[spec.index(")") + 1:]
    elif spec.startswith(":"):
        i = 1
        while i < len(spec) and spec[i] in "/!^":
            ex, top = ex or spec[i] in "!^", top or spec[i] == "/"
            i += 1
        spec = spec[i + 1:] if spec[i:i + 1] == ":" else spec[i:]
    return ex, top, fold, glob, spec


def _x_spec_hit(rel: str, pattern: str, fold: bool, glob: bool, wide: bool) -> bool:
    """Whether a path (from where the pathspec is read) matches it: a plain
    pathspec names a path and what is below it; with a wildcard, ``*``
    crosses folders (``:(glob)``: ``**`` only).  *wide*: a leading folder
    that matches takes the path in too (a positive pathspec, read wide)."""
    import fnmatch as fm
    if fold:
        rel, pattern = rel.lower(), pattern.lower()
    if not any(c in pattern for c in "*?["):
        p = os.path.normpath(pattern) if pattern else "."
        return p == "." or rel == p or rel.startswith(p + "/")
    names = rel.split("/")
    tries = ["/".join(names[:k]) for k in range(1, len(names) + 1)] if wide else [rel]
    if glob:
        rx = x_glob(pattern.rstrip("/"))
        return any(rx.match(t) for t in tries)
    return any(fm.fnmatchcase(t, pattern.rstrip("/")) for t in tries)


def _x_git(sub: str, rest: list[str], cwd: str | None):
    """git grep's or git ls-files's (starts, keep): its pathspecs (after --;
    before it, ls-files's operands, and git grep's words that are magic,
    wildcards or paths from *cwd*, the folder git runs in; another word is a
    revision, which leaves the start at *cwd*); a file is taken in when a
    positive pathspec (or none) takes it and no exclusion does."""
    dd = rest.index("--") if "--" in rest else len(rest)
    operands, options, _letters = _x_parse(rest[:dd], _X_GIT_VALUED[sub])
    if sub == "grep" and _X_PATTERN.isdisjoint(o for o, _ in options):
        operands = operands[1:]
    base = os.path.realpath(cwd) if cwd else None
    specs = [o for o in operands if sub == "ls-files" or o.startswith(":") or any(
        c in o for c in "*?[") or (base and os.path.lexists(os.path.join(base, o)))]
    specs += rest[dd + 1:]
    pos, neg, starts = [], [], []
    for s in specs:
        ex, top, fold, glob, pat = _x_pathspec(s)
        (neg if ex else pos).append((top, fold, glob, pat))
        if ex:
            continue
        lead = []
        for seg in pat.split("/"):
            if any(c in seg for c in "*?["):
                break
            lead.append(seg)
        lead = "." if fold else "/".join(lead) or "."
        if top:
            t = _x_top(base)
            lead = os.path.join(t, lead) if t else "/"
        starts.append(lead)

    def keep(f: str, start: str, word: str, here: str | None) -> bool:
        at = base or here

        def hit(item, wide: bool) -> bool:
            top, fold, glob, pat = item
            frm = _x_top(at) if top else at
            if not frm:
                return wide  # not placed: taken in, never kept out
            return _x_spec_hit(os.path.relpath(f, frm), pat, fold, glob, wide)
        if pos and not any(hit(i, True) for i in pos):
            return False
        return not any(hit(i, False) for i in neg)
    return starts or ["."], keep


def x_search(name: str, args: list[str], cwd: str | None = None):
    """A recursive search's (start operands, keep, how, names only), or None:
    keep(f, start, word, cwd) says whether it takes in the file ``f`` (real
    paths; ``word``: the start as written).  Names only: a listing (rg
    --files, ag -g, ack -f/-g, a find with no action that reads, git
    ls-files), a search only when its names go to a reader.  git: *args*
    from its subcommand on (grep or ls-files), *cwd* the folder it runs in."""
    name = os.path.basename(name)
    # An option word with braces is the options Bash makes of it
    # (--exclude-dir={.git,W2-1} is --exclude-dir=.git --exclude-dir=W2-1).
    args = [b for a in args for b in (_x_braces(a) if a.startswith("-") else [a])]
    if name == "git":
        if not args or args[0] not in _X_GIT_VALUED:
            return None
        starts, keep = _x_git(args[0], args[1:], cwd)
        return starts, keep, "git", args[0] == "ls-files"
    if name in ("grep", "egrep", "fgrep", "zgrep"):
        operands, options, letters = _x_parse(args, _X_GREP_VALUED)
        if not (letters & {"r", "R"} or any(
                o in ("--recursive", "--dereference-recursive")
                or (o in ("-d", "--directories") and v == "recurse") for o, v in options)):
            return None
        if _X_PATTERN.isdisjoint(o for o, _ in options):
            operands = operands[1:]
        rules = [(o[2:], v) for o, v in options if o in ("--include", "--exclude", "--exclude-dir")]
        return ["." if p in ("*", "./*") else p for p in operands] or ["."], _x_grep(rules), "grep", False
    if name == "rg":
        operands, options, letters = _x_parse(args, _X_RG_VALUED)
        files = any(o == "--files" for o, _ in options)
        if not files and _X_PATTERN.isdisjoint(o for o, _ in options):
            operands = operands[1:]
        fold = any(o == "--glob-case-insensitive" for o, _ in options)
        globs = [(v, fold or o == "--iglob") for o, v in options if o in ("-g", "--glob", "--iglob")]
        depth = next((v for o, v in options if o in ("-d", "--max-depth", "--maxdepth")), None)
        return operands, _x_depth(_x_rg(globs), depth), "rg", files
    if name == "ag":
        operands, options, letters = _x_parse(args, _X_AG_VALUED)
        names = any(o == "-g" for o, _ in options) or "--list-file-types" in args
        if not names:
            operands = operands[1:]
        pats = [v for o, v in options if o in ("--ignore", "--ignore-dir")]
        depth = next((v for o, v in options if o == "--depth"), None)
        return operands, _x_depth(_x_ag(pats), depth), "ag", names
    if name == "ack":
        operands, options, letters = _x_parse(args, _X_ACK_VALUED)
        names = "f" in letters or any(o == "-g" for o, _ in options)
        if not names and not any(o == "--match" for o, _ in options):
            operands = operands[1:]
        rules = [(o.startswith("--ignore"), v) for o, v in options if o in (
            "--ignore-dir", "--ignore-directory", "--noignore-dir", "--noignore-directory")]
        return operands, _x_ack(rules), "ack", names
    if name == "find":
        i = 0
        while i < len(args) and args[i] in ("-H", "-L", "-P"):
            i += 1
        j = i
        while j < len(args) and not (args[j].startswith("-") or args[j] in ("!", "(", ")", ",")):
            j += 1
        expr = args[j:]
        reads = any(a in _X_FIND_OPENS and k + 1 < len(expr)
                    and os.path.basename(expr[k + 1]) in X_READERS for k, a in enumerate(expr))
        return args[i:j] or ["."], _x_find(expr), "find", not reads
    return None


def x_how(wbs: str, how: str) -> str:
    """The refusal of a search that can reach the folder, saying how to keep it out."""
    return SEARCH_REFUSAL.format(folder=f"tests/acceptance/{wbs}/",
                                 how=X_HOW[how].format(w=wbs))

# END W2-141 BLOCK


def x_spread(word: str, keep):
    """W2-141 (F4): a search start the shell expands, as (its literal folder,
    keep): a file is taken in when a leading part of its path from that
    folder matches the glob (``**`` read as crossing folders, the wider
    reading) and *keep* takes it."""
    segs = word.split("/")
    n = next(i for i, p in enumerate(segs) if _has_glob(p))
    lead = "/".join(segs[:n]) or ("/" if word.startswith("/") else ".")
    rx = x_glob("/".join(segs[n:]).rstrip("/"))

    def spread(f: str, start: str, w: str, cwd: str | None) -> bool:
        names = _x_rel(f, start)
        return any(rx.match("/".join(names[:k])) for k in range(1, len(names) + 1)) and (
            keep(f, start, w, cwd))
    return lead, spread


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
              names: list[str] | None = None, fold: bool = False,
              searched=None, how: str = "", word: str | None = None,
              only_own: bool = False) -> str:
        """Why a search or listing from *text* takes a part's files in: no
        positive glob keeps them out (a glob with no slash is a name at any
        depth), nor any of *names* (find's tests on a name).  The engineer's
        own acceptance folder (W2-141): *searched* (``x_search``'s keep) says
        what the call takes in, and with *how* the refusal says how to keep
        the folder out; *only_own*: no other part is judged."""
        real = (self.spellings(text, cwd) or [None])[-1]
        keep = [b for g in globs if not g.startswith("!") for b in _braces(g)]
        here = os.path.realpath(cwd) if cwd else None
        # W2-141 (F4): a start the shell expands (*/, tests/*, tests/acc*) is,
        # for the engineer's own folder, a search from its literal folder of
        # what lies at or below a path the glob matches.
        mine, spread, said = real, searched, (text if word is None else word)
        if searched is not None and _has_glob(text):
            said, spread = x_spread(text, searched)
            mine = (self.spellings(said, cwd) or [None])[-1]
        for part in self.parts:
            own = getattr(part, "wbs", None)
            if only_own and not own:
                continue
            base = mine if own and searched is not None else real
            for f in part.below(base):
                rel = f[len(base.rstrip("/")) + 1:]
                name = os.path.basename(f)
                cased = (lambda s: s.lower()) if fold else (lambda s: s)
                if own and searched is not None:
                    hit = spread(f, base, said, here)
                elif names is not None:
                    hit = any(fnmatch.fnmatchcase(cased(name), cased(n)) for n in names)
                elif keep:
                    hit = any(_Glob(cased(g.lstrip("/"))).match(
                        cased(name if "/" not in g else rel)) for g in keep)
                else:
                    hit = True
                if hit:
                    return x_how(own, how) if own and how else part.reason
        return ""

    def _wide(self, name: str, args: list[str], cwd: str | None = None):
        """``x_search`` for a session with its own acceptance folder, else None."""
        if not any(getattr(p, "wbs", None) for p in self.parts):
            return None
        return x_search(name, list(args), cwd)

    def _not_own(self) -> "_Judge":
        """This judge without the engineer's own part (judged on its own)."""
        others = copy.copy(self)
        others.parts = [p for p in self.parts if not getattr(p, "wbs", None)]
        return others

    def _own_git(self, sub: str, rest: list[str], cwd: str) -> str:
        """W2-141: why git grep or git ls-files from *cwd* takes in the
        engineer's own folder (its pathspec exclusions honoured)."""
        wide = self._wide("git", [sub, *rest], cwd)
        own = [p for p in self.parts if getattr(p, "wbs", None)]
        for s in (wide[0] if wide else ()):
            exp = _expand_token(s) or s
            # a pathspec in the folder names it: its own refusal, as a direct read
            why = next((p.reason for p in own for q in self.spellings(exp, cwd)
                        if p.inside(q)), "") or self.above(
                exp, cwd, searched=wide[1], how="git", word=exp, only_own=True)
            if why:
                return why
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
            return self.at(path, cwd) or self.above(
                path, cwd, text("glob").split(),
                searched=_x_rg(x_grep_tool_globs(text("glob"))), how="Grep")
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
            here = os.path.realpath(cwd) if cwd else None
            for part in self.parts:
                if getattr(part, "wbs", None):
                    # W2-141: the engineer's own folder, with ** too: refused
                    # when the pattern can reach one of its files.
                    reach = x_glob_tool(pattern)
                    if any(reach(f, start, base, here) for f in part.below(start)):
                        return x_how(part.wbs, "Glob")
                    continue
                if "**" in pattern:
                    continue  # with **, a listing from above, which shows names
                # Without **, the pattern names the files it lists: aimed at them.
                for f in part.below(start):
                    rel = f[len(start.rstrip("/")) + 1:]
                    if any(_Glob(p).match(rel) for p in _braces(pattern)):
                        return part.reason
            return ""
        if tool_name == "Bash":
            # W2-42a (KPI 6, 10): a data heredoc's body is no command, nor $((...)) a substitution; a program's
            # code in a heredoc is judged by the paths it names, as a python3 -c string is.
            whole = text("command")
            if "\\\n" in whole:
                # KPI 7: a name continued over a line is read joined too (it only names more).
                why = self._tool(tool_name, dict(tool_input, command=whole.replace("\\\n", "")), cwd)
                if why:
                    return why
            command, codes = bash_writes.read_view(whole)
            for code in codes:
                for piece in _CODE_PIECE_RE.split(code):
                    if piece and not piece.startswith("-"):
                        why = self.word(piece, cwd)
                        if why:
                            return why
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
        return next((p.reason for p in self.parts for f in p.below(real)
                     if os.path.dirname(f) == real and (names is None or any(
                         fnmatch.fnmatchcase(cased(os.path.basename(f)), cased(n))
                         for n in names))), "")

    def reads(self, name: str, args: list[str], cwd: str, fed: bool = False) -> str:
        name = "grep" if name in ("egrep", "fgrep") else name
        # W2-141: what the search keeps out of the engineer's own folder.
        wide = self._wide(name, args) if name in (
            "grep", "zgrep", "rg", "find", "ag", "ack") else None
        kept, how = (wide[1], wide[2]) if wide else (None, "")
        # Not judged here before, so only its own folder: ag, ack, zgrep -r and
        # a grep recursive by a form the search rule does not read (-d recurse).
        alone = name in ("ag", "ack", "zgrep") or (
            name == "grep" and _shell_search(name, list(args), False) is None)
        if wide and alone and not wide[3] and (wide[0] or not fed):
            for path in wide[0] or ["."]:
                exp = _expand_token(path) or path
                why = self.at(exp, cwd) or self.above(exp, cwd, searched=kept, how=how,
                                                      word=exp, only_own=True)
                if why:
                    return why
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
                exp, cwd, search[1] + search[2], fold=bool(search[2]),
                searched=kept, how=how, word=exp))
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
                why = (self.above(s, cwd, names=names, fold="-iname" in args,
                                  searched=kept, how=how, word=s) if opens
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
        written = set(_line_write_targets(
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
        # W2-141: a find's test on a name or a path (-path ./tests/acceptance/<T>
        # -prune) holds a pattern it matches, not a file it opens: the
        # engineer's own folder named there is no read (a secret or a hidden
        # part named there still refuses, as before).
        tested = {k + 1 for k, a in enumerate(args) if name == "find" and a in _FIND_NAMED}
        for k, w in enumerate(args):
            if w is skip:
                skip = None
                continue
            if theirs(w):
                continue
            why = self.word(w, cwd)
            if why and not (k in tested and why == TESTS_REFUSAL):
                return why
        return ""

    def git(self, args: list[str], cwd: str) -> str:
        i, addr = 0, []  # the repository and tree the command addresses
        while i < len(args) and args[i].startswith("-"):
            if args[i] == "-C" and i + 1 < len(args):
                cwd = os.path.join(cwd, _expand_token(args[i + 1]) or args[i + 1])
            elif args[i] in ("--git-dir", "--work-tree") and i + 1 < len(args):
                addr.append(f"{args[i]}={args[i + 1]}")
            elif args[i].startswith(("--git-dir=", "--work-tree=")):
                addr.append(args[i])
            i += 2 if args[i] in ("-C", "-c", "--git-dir", "--work-tree") else 1
        sub, rest = (args[i], args[i + 1:]) if i < len(args) else ("", [])
        hidden = [p for p in self.parts if p.strict]
        if sub not in ("show", "log", "diff", "grep", "whatchanged"):
            why = self.reads("git", args, cwd)
            if why or not hidden or sub not in ("cat-file", "format-patch", "archive"):
                return why
        dd = rest.index("--") if "--" in rest else len(rest)
        before, specs = rest[:dd], rest[dd + 1:]
        operands = [a for a in before if not a.startswith("-")]
        if sub == "grep":
            # W2-141 (F1): the engineer's own folder, with the pathspecs'
            # exclusions; the other parts as before.
            why = self._own_git(sub, rest, cwd)
            if why:
                return why
            others = self._not_own()
            operands, options = _options(before, _GIT_GREP_VALUED)
            if _PATTERN_OPTIONS.isdisjoint(o for o, _ in options):
                operands = operands[1:]
            specs = [o for o in operands if os.path.lexists(os.path.join(cwd, o))] + specs
            for s in specs or ["."]:
                why = others.spec(s, cwd, True)
                if why:
                    return why
            revs = [o for o in operands if not os.path.lexists(os.path.join(cwd, o))]
            if hidden and (revs or "--cached" in before) and self.covers(specs, cwd, hidden):
                return self.stored(revs, "--cached" in before, cwd, addr, hidden)
            return ""
        if sub == "archive":  # its tree-ish, then its paths
            operands = _options(before, _ARCHIVE_VALUED)[0] + specs
            return self.stored(operands[:1], False, cwd, addr, hidden) if (
                self.covers(operands[1:], cwd, hidden)) else ""
        shown = [o for o in operands if ":" in o] if sub in ("show", "cat-file") else []
        for o in shown:
            rev, _, path = o.partition(":")
            if not path:
                continue
            at = cwd if path.startswith(("./", "../")) else self.root
            if sub == "show" and any(self.secret(p) for p in self.spellings(path, at)):
                return SECRET_REFUSAL
            for part in (self.parts if sub == "show" else []):
                if any(part.inside(p) for p in self.spellings(path, at)) and not (
                        part.base and self.base_version(rev, part.rel(
                            os.path.abspath(os.path.join(at, path))))):
                    return part.reason
            # The hidden part's path names it in whichever tree (W2-84).
            if any(h.inside(p) for h in hidden for p in self.spellings(path, at)) or (
                    at == self.root and any(h.match(os.path.normpath(path)) for h in hidden)):
                return HIDDEN_REFUSAL
        if sub == "cat-file":
            return ""
        quiet = (any(a in _GIT_QUIET or a.startswith("--stat=") for a in before)
                 and not any(a in ("-p", "--patch", "-u") or a.startswith("-U")
                             for a in before))
        if sub in ("log", "whatchanged"):
            patch = not quiet and any(a in ("-p", "--patch", "-u") or a.startswith("-U")
                                      for a in before)
        else:
            patch = sub == "format-patch" or not quiet and (
                sub == "diff" or len(shown) < len(operands) or not operands)
        if patch and sub != "format-patch":  # with no pathspec, the whole tree
            others = copy.copy(self)
            others.parts = [p for p in self.parts if not p.strict]
            for s in specs or [self.root]:
                why = others.spec(s, cwd, False)
                if why:
                    return why
        # git show :/<text> names a commit by its message: a patch, too.
        patch = patch or any(o.startswith(":/") for o in shown if sub == "show")
        return self.patched(sub, before, specs, cwd, addr, hidden) if (
            patch and hidden) else ""

    def covers(self, specs: list[str], cwd: str, hidden: list[_Part]) -> bool:
        """Whether pathspecs take the hidden part in: none, a glob or magic
        one, one at or above a glob's literal folder, or one inside it."""
        if not specs:
            return True
        for s in specs:
            exp = _expand_token(s)
            if exp is None or exp.startswith(":") or _has_glob(exp) or any(
                    h.inside(p) or h.under(p) for h in hidden
                    for p in self.spellings(exp, cwd)):
                return True
        return False

    def patched(self, sub: str, before: list[str], specs: list[str], cwd: str,
                addr: list[str], hidden: list[_Part]) -> str:
        """Why a patch shows the hidden part, asked of git in a fixed
        read-only form: the changed paths alone, filtered by the hidden
        globs, with the command's revisions and the options that widen or
        choose its sides; merges parent by parent (W2-84)."""
        sides, revs, paths, negated = [], [], [], False
        j = 0
        while j < len(before):
            a = before[j]
            if a in _GIT_SIDES or a.startswith(("--branches=", "--tags=", "--remotes=",
                                                "--glob=")) or _COUNT_RE.fullmatch(a):
                sides.append(a)
            elif a in ("-n", "--max-count") and j + 1 < len(before):
                sides += before[j:j + 2]
                j += 1
            elif a in _GIT_LOG_VALUED:
                j += 1
            elif a == "--not":  # what follows is taken whole: never fewer sides
                negated = True
            elif not a.startswith("-") and not (
                    sub == "show" and ":" in a and not a.startswith(":/")):
                if os.path.lexists(os.path.join(cwd, a)):
                    paths.append(a)
                else:
                    revs += ([e or "HEAD" for e in re.split(r"\.\.\.?", a.lstrip("^"))]
                             if negated else [a])
            j += 1
        if "--no-index" in before:  # two files, no revision
            return HIDDEN_REFUSAL if any(h.inside(p) for a in paths for h in hidden
                                         for p in self.spellings(a, cwd)) else ""
        if not self.covers(paths + specs, cwd, hidden):
            return ""
        if sub == "diff":
            query = ["diff", *_NO_CONVERT]
        else:
            query = ["log", *_NO_CONVERT, "--format=", "--diff-merges=separate",
                     "--full-history"]
            counted = any(a in ("-n", "--max-count") or _COUNT_RE.fullmatch(a)
                          for a in sides)
            if sub == "show" and not counted:
                query.append("--no-walk")
            if (sub == "format-patch" and len(revs) == 1 and ".." not in revs[0]
                    and not counted and "--root" not in before):
                revs = [revs[0] + "..HEAD"]  # <since> means <since>..HEAD
        words = [_expand_token(w) for w in sides + revs]
        if None in words or "--stdin" in before:  # a revision it cannot resolve
            raise PolicyError(_REV_FAULT)
        # Each revision must be a commit: git log passes over a blob or tree.
        ends = [e for w in words[len(sides):] if not w.startswith(":/")
                for e in re.split(r"\.\.\.?", w.lstrip("^")) if e]
        if ends:
            self.ask(cwd, addr, "rev-parse", "--end-of-options",
                     *(e + "^{commit}" for e in ends), "--")
        out = self.ask(cwd, addr, *query, *words[:len(sides)], "--end-of-options",
                       *words[len(sides):], "--", *_pathspecs(hidden))
        return HIDDEN_REFUSAL if out.strip() else ""

    def stored(self, revs: list[str], cached: bool, cwd: str, addr: list[str],
               hidden: list[_Part]) -> str:
        """Why a revision's tree (or the index) holds the hidden part, asked
        of git in a fixed read-only form (W2-84)."""
        for rev in revs:
            word = _expand_token(rev)
            if word is None:
                raise PolicyError(_REV_FAULT)
            prefix = os.path.normpath(word.partition(":")[2] or ".")
            prefix = "" if prefix == "." else prefix
            out = self.ask(cwd, addr, "ls-tree", "-r", "--full-tree", "--name-only", "-z",
                           "--end-of-options", word)
            if any(h.match(os.path.join(prefix, n) if prefix else n) for h in hidden
                   for n in out.split("\0") if n):
                return HIDDEN_REFUSAL
        if cached and self.ask(cwd, addr, "ls-files", "--cached", "-z", "--",
                               *_pathspecs(hidden)):
            return HIDDEN_REFUSAL
        return ""

    @staticmethod
    def ask(cwd: str, addr: list[str], *args: str) -> str:
        """git's answer in the repository the command addresses; one that
        cannot be had refuses."""
        words = [_expand_token(a) for a in addr]
        if None in words:
            raise PolicyError(_REV_FAULT)
        try:
            out = _git(cwd, *words, *args)
        except PolicyError:
            raise PolicyError(_REV_FAULT) from None
        if out.returncode:
            raise PolicyError(_REV_FAULT)
        return out.stdout

    def spec(self, spec: str, cwd: str, secrets: bool) -> str:
        """A git pathspec: what it names, and the parts' files it takes in
        (``*`` in a pathspec crosses folders)."""
        if _has_glob(spec):
            here = os.path.realpath(cwd)
            for part in self.parts:
                for f in ([] if part.strict and not _related(here, part.root)
                          else part.files):
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
                    (self._body_reads(cmds, i) and _names_used(bare, command, subs))
                    if bare[:1] == ["for"] else _reads_files(words)):
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
        if not any(p.held() for p in self.parts):
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
            wide = self._wide("find", args)
            kept, how = (wide[1], "find") if wide else (None, "")
            return True, next((why for s in args[:n] or ["."] for why in [
                self.at(s, cwd, False) or self.above(s, cwd, names=names, fold=fold,
                                                     searched=kept, how=how, word=s)]
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
            # W2-141 (F2): the engineer's own folder, with the pathspecs'
            # exclusions; the other parts as before.
            why = self._own_git(sub, rest, cwd)
            if why:
                return True, why
            if not specs or any(s.startswith(":") for s in specs):
                specs = ["."]  # a magic pathspec is not read: the whole tree
            others = self._not_own()
            return True, next((why for s in specs for why in [others.spec(s, cwd, False)]
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
            wide = self._wide(name, args)
            kept, how = (wide[1], wide[2]) if wide else (None, "")
            for p in search[0]:
                why = self.at(p, cwd) or self.above(p, cwd, search[1] + search[2],
                                                    fold=bool(search[2]),
                                                    searched=kept, how=how, word=p)
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
        if (name == "seq" and args and all(_NUMERIC_RE.fullmatch(a) or a == "-w" for a in args)) or (
                name == "nproc" and all(a in ("--all",) for a in args)):
            # W2-42a (KPI 10): numbers, read as names in the folder it runs in; placed there.
            return True, self.at(".", cwd, False) or self.numbered(cwd)
        if name == "date" and len(args) == 1 and _DATE_FORMAT_RE.fullmatch(args[0]):
            return True, self.at(".", cwd, False) or self.numbered(cwd)  # a date in digits
        if name == "wc" and all(a in _WC_COUNTS for a in args if a.startswith("-")):
            # Counts, and the names of the files it was given (its own words, judged as paths).
            operands = [a for a in args if not a.startswith("-")]
            return True, next((why for a in operands for why in [self.at(a, cwd, False)] if why), "") or \
                self.at(".", cwd, False) or self.numbered(cwd)
        if name in _FILTERS:
            return False, ""
        return None, ""

    def numbered(self, cwd: str) -> str:
        """Why a name made of digits, read in *cwd*, may take a part's file
        in: a part's file below *cwd* whose first name there starts with a
        digit or a sign (W2-42a)."""
        real = (self.spellings(".", cwd) or [None])[-1]
        if real is None:
            return RUNTIME_REFUSAL
        for part in self.parts:
            for f in part.below(real):
                if f[len(real.rstrip("/")) + 1:].split("/")[0][:1] in "0123456789-.":
                    return part.reason
        return ""


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
        found: dict = {}
        protected = [p for r in dict.fromkeys((session, acting))
                     for p in parts(project_root, r, ticket_id, found)]
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
