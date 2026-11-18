"""The close's commit check (W1-50, DEC-453): each commit judged by its ``Role`` and ``Task`` trailers against the
paths the ticket they name allows.

``judge_commits`` is the one entry point, read-only, called by ``gov close`` (``close/command.py``). It is the half of
the old post-command containment check (W1-03, ``gov.guard.containment``) that judged a call's commits; the half that
snapshotted and restored the working tree around each call ran from the PreToolUse and PostToolUse hooks and was
retired with the guard (EMERGENCY-2 6.1). A path's scope comes from ``gov.containment.scope``.
"""

from __future__ import annotations

import os
import re
import subprocess
from typing import NamedTuple

from gov.util.gitenv import git_binary, git_env
from gov.util.patterns import ACCEPTANCE, _is_under_acceptance  # noqa: F401 - names of this module too
from gov.util.tickets import _parse_frontmatter

_GIT_TIMEOUT = 10


# ---- git helper --------------------------------------------------

class _NotARepo(Exception):
    pass


class _GitError(Exception):
    pass


class ContainmentError(Exception):
    """Raised by ``judge_commits`` for an empty list of commits, an unknown
    commit id, a path that is not a repository, or a git failure."""


# Every git call reads the real objects of the repository at its root,
# whatever refs/replace/, .git/info/grafts, .git/shallow or a commit-graph
# file holds, whatever repository an inherited variable names, and whatever
# the person's git configuration sets (W2-M105, W2-M113); and the git run
# is the system's, by absolute path, never the first on PATH (W2-L160).
_GIT_OPTIONS = ("--no-replace-objects", "-c", "core.commitGraph=false")


def _git_command(root: str, *args: str) -> list:
    """The command line of a git call in *root*.  ``_GitError`` when no git
    is resolved by absolute path: the check is not passed for want of one
    (DEC-580)."""
    git = git_binary()
    if git is None:
        raise _GitError("no git resolved by absolute path")
    return [git, *_GIT_OPTIONS, "-C", root, *args]


def _git_env(root: str) -> dict:
    env = git_env(root, pinned=True)
    env.update(GIT_GRAFT_FILE=os.devnull, GIT_SHALLOW_FILE=os.devnull)
    return env


def _git(root: str, *args: str, ok: tuple = (0,)) -> str:
    """Run a git command and return stdout.  Raises on failure: an exit
    code that is not among *ok*."""
    try:
        p = subprocess.run(
            _git_command(root, *args),
            capture_output=True, text=True,
            timeout=_GIT_TIMEOUT, check=False, env=_git_env(root),
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        raise _GitError(str(e)) from e
    if p.returncode == 128 and "not a git repository" in p.stderr.lower():
        raise _NotARepo(p.stderr.strip())
    if p.returncode not in ok:
        raise _GitError(p.stderr.strip())
    return p.stdout


# ---- NUL-separated status parsing (repair 6) --------------------


def _is_ancestor(root: str, old: str, new: str) -> bool:
    """True when *old* is an ancestor of *new*.  Raises on failure."""
    try:
        p = subprocess.run(
            _git_command(root, "merge-base", "--is-ancestor", old, new),
            capture_output=True, timeout=_GIT_TIMEOUT, check=False,
            env=_git_env(root),
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        raise _GitError(str(e)) from e
    return p.returncode == 0

# ---- commits of a forward move (W1-50, DEC-255) -------------------

_LOG_FORMAT = "--format=%x00%H %P%x00%(trailers)%x00"
# What the repository's local configuration could set otherwise: how a
# trailer block is told from text, the message's encoding, a root
# commit's changes, renames, and submodule entries.
_LOG_DEFAULTS = ("-c", "trailer.separators=:", "-c", "core.commentChar=#",
                 "log", "--encoding=UTF-8", "--root", "--no-renames",
                 "--ignore-submodules=none")
_COMMIT_IDS = re.compile(r"([0-9a-f]{40,64} ?)+")
_TRAILER = re.compile(r"([A-Za-z0-9-]+)[ \t]*:(.*)", re.S)


def _role_and_task(block: str) -> list:
    """``(key, value)`` for each ``Role`` and ``Task`` trailer of a
    trailer block, read as git reads one with default settings: a key
    of letters, digits and ``-``, then ``:``; a line that begins with
    whitespace goes on with the line before it."""
    found: list = []
    lines = None  # the value's lines of the Role or Task being read
    for line in block.split("\n"):
        if line[:1] in ("", " ", "\t", "\r"):
            if lines is not None:
                lines.append(line)
            continue
        m = _TRAILER.fullmatch(line)
        lines = [m[2]] if m and m[1].lower() in ("role", "task") else None
        if lines is not None:
            found.append((m[1].lower(), lines))
    return [(key, " ".join(filter(None, (v.strip(" \t\r") for v in ls))))
            for key, ls in found]


def _parse_log_output(out: str) -> list:
    """Parse NUL-separated ``git log`` output produced with
    ``_LOG_FORMAT`` and ``--raw`` into ``[id, parents, roles, tasks,
    paths]`` lists.  Read by ``_read_one_commit`` and ``_lifted``."""
    commits: list = []
    tokens = iter(out.split("\0"))
    for tok in tokens:
        if tok.lstrip("\n").startswith(":"):
            path = next(tokens, "")
            if not commits or not path:
                raise _GitError("the commits cannot be read")
            commits[-1][4].append(path)
        elif _COMMIT_IDS.fullmatch(tok):
            ids = tok.split()
            commits.append([ids[0], ids[1:], set(), set(), []])
            for key, value in _role_and_task(next(tokens, "")):
                if value:
                    commits[-1][2 if key == "role" else 3].add(value)
        elif tok.strip("\n"):
            raise _GitError("the commits cannot be read")
    return commits


def _read_one_commit(root: str, commit_id: str):
    """Read one commit's parents, trailers and paths: trailers from the
    final trailer block only, as git finds it (DEC-182, DEC-267), paths
    without rename detection (repair 7)."""
    out = _git(root, *_LOG_DEFAULTS, "-z", "-c", "--raw", "--no-abbrev",
               _LOG_FORMAT, "--no-walk", commit_id)
    commits = _parse_log_output(out)
    if len(commits) != 1:
        raise _GitError(f"commit {commit_id} not found")
    c = commits[0]
    return (c[0], c[1], sorted(c[2]), sorted(c[3]), c[4])


def _ticket_at(root: str, rev: str, ticket_file: str):
    """The ticket's frontmatter as committed at *rev*, or ``None``."""
    try:
        return _parse_frontmatter(
            _git(root, "cat-file", "blob", f"{rev}:{ticket_file}"))
    except (_GitError, _NotARepo, ValueError):
        return None


def _close_commit(root: str, head: str, ticket_file: str):
    """The latest commit in *head*'s history in which the ticket's
    status becomes ``closed`` (DEC-358), or ``None``.

    The file's first version is no such commit, nor is a merge commit:
    what cannot be shown to be a close is not one.
    """
    def status(rev: str):
        return (_ticket_at(root, rev, ticket_file) or {}).get("status")

    try:
        revs = _git(root, "rev-list", "--topo-order", "--no-merges",
                    head, "--", ticket_file).split()
    except (_GitError, _NotARepo, ValueError):
        return None
    for rev in revs:
        if status(rev) == "closed" and status(rev + "^") not in (None, "closed"):
            return rev
    return None


def _merge_own(commit) -> list:
    """A merge commit's own paths under ``.tickets/**`` and
    ``tests/acceptance/**`` (DEC-410, DP-21 and DP-27)."""
    return [p for p in commit[4] if len(commit[1]) > 1
            and p.startswith((".tickets/", ACCEPTANCE + "/"))]


# DEC-572: the most commits that may have brought one version, and the
# most git processes the lifts of one HEAD move (or of one call of
# ``judge_commits``) may start, beyond ``MAX_MOVE_PROCESSES`` of the merge
# reading: one ticket file with 50 merge commits on each side (608), or
# a hundred with a few ordinary commits.  Beyond either nothing is
# lifted: the path stays a finding.
_LIFT_COMMITS = 50
_LIFT_PROCESSES = 1000
_LIFT_LEFT = "git processes left for the lifts"  # a key of *closes*


def _lifted(root, commit, path, head, decide_fn, closes):
    """``None`` when the ticket file *path*, a merge commit's own change
    as ``read_merge`` reads it, is not its own change by DEC-572; else
    the id of a commit that brought the version and does not pass, or
    ``""`` where the check cannot tell.

    Lifted: the merge commit has two parents with one merge base and
    holds the file exactly as a parent has it (content and mode); that
    version is not the merge base's; and every commit that brought it,
    on each side that has it, is no finding when it is judged alone as
    ``judge_commits`` judges it, a merge commit among them as merges
    were read before DEC-572.  A commit brought the version when it is
    in that parent's history and not in the merge base's, and its
    content of the path differs from that of one of its parents.

    At most 5 git processes, one more for each side that has the
    version, one to read the commits that brought it and what
    ``read_merge`` needs for each merge commit among them; all are
    counted against ``_LIFT_PROCESSES``.
    """
    from gov.containment.merge import processes, read_merge

    def git(*args, cost=1, ok=(0,)):
        closes[_LIFT_LEFT] = closes.get(_LIFT_LEFT, _LIFT_PROCESSES) - cost
        if closes[_LIFT_LEFT] < 0:
            raise _GitError("too many git processes for the lifts")
        return _git(root, "--literal-pathspecs", *args, ok=ok) if args else ""

    def held(rev):
        return git("ls-tree", "-z", "--full-tree", rev, "--", path)

    try:
        parents = commit[1]
        if len(parents) != 2 or parents[0] == parents[1]:
            return ""
        bases = git("merge-base", "--all", *parents, ok=(0, 1)).split()
        mine = held(commit[0])
        if len(bases) != 1 or not mine.endswith(f"\t{path}\0") or (
                mine.split(" ")[1:2] != ["blob"] or mine == held(bases[0])):
            return ""
        brought: list = []
        for p in [p for p in parents if held(p) == mine]:
            # Every commit of the side is listed (--sparse), each with
            # the path where it differs from a parent, any of them (-m).
            found = list(dict.fromkeys(c[0] for c in _parse_log_output(git(
                *_LOG_DEFAULTS, "-z", "-m", "--raw", "--no-abbrev",
                "--full-history", "--sparse", _LOG_FORMAT,
                f"{bases[0]}..{p}", "--", path)) if c[4]))
            if not 0 < len(found) <= _LIFT_COMMITS:
                return ""
            brought += found
        if not brought:
            return ""
        commits = _parse_log_output(git(
            *_LOG_DEFAULTS, "-z", "-c", "--raw", "--no-abbrev", _LOG_FORMAT,
            "--no-walk=unsorted", *brought))
        if [c[0] for c in commits] != brought:
            return ""
        for c in commits:
            if len(c[1]) > 1:
                git(cost=processes(len(set(c[1]))))
                c[4][:] = read_merge(root, c[0]).own
            if _judge_commit(
                    root, (c[0], c[1], sorted(c[2]), sorted(c[3]), c[4]),
                    "orchestrator", None, None, True, head, decide_fn,
                    closes, lift=False) is not None:
                return c[0]
        return None
    except (_GitError, _NotARepo, ValueError):  # MergeReadError too
        return ""


_TREE_ID = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")


def _counted(root, closes, *args, ok=(0,)) -> str:
    """One git process counted against ``_LIFT_PROCESSES``."""
    closes[_LIFT_LEFT] = closes.get(_LIFT_LEFT, _LIFT_PROCESSES) - 1
    if closes[_LIFT_LEFT] < 0:
        raise _GitError("too many git processes for the lifts")
    return _git(root, *args, ok=ok)


def _acc_changed(root, closes, a, b) -> set:
    """The acceptance tests whose content, mode or presence differs
    between the trees *a* and *b*, without rename detection."""
    return {p for p in _counted(
        root, closes, "--literal-pathspecs", "diff-tree", "-r", "-z",
        "--name-only", "--no-renames", "--ignore-submodules=none", a, b,
        "--", ACCEPTANCE).split("\0") if p}


def _git_merge_diff(root, commit, closes):
    """D for the merge commit *commit* (DEC-918): the acceptance tests
    where its tree differs from git's own merge of its two parents
    (``git merge-tree --write-tree``) in content, mode or presence,
    over the whole of ``tests/acceptance/``, together with every
    acceptance test git reports as conflicted (a moved-aside
    ``<path>~<commit>`` included).

    ``None`` where git's own merge cannot be shown: an octopus merge,
    parents with several merge bases or none, a merge-tree that fails or
    whose output cannot be read, a spent budget.  Three git processes,
    counted against ``_LIFT_PROCESSES``; the answer is kept in *closes*.
    """
    key = "git's own merge of " + commit[0]
    if key not in closes:
        closes[key] = None
        parents = list(dict.fromkeys(commit[1]))
        try:
            if len(parents) != 2 or len(_counted(
                    root, closes, "merge-base", "--all", *parents,
                    ok=(0, 1)).split()) != 1:
                return None
            # The tree id, then the conflicted paths; exit 1 is a conflict.
            out = _counted(root, closes, "merge-tree", "--write-tree",
                           "--no-messages", "-z", "--name-only", *parents,
                           ok=(0, 1)).split("\0")
            if not _TREE_ID.fullmatch(out[0]):
                return None
            closes[key] = _acc_changed(root, closes, out[0], commit[0]) | {
                p for p in out[1:] if p.startswith(ACCEPTANCE + "/")}
        except (_GitError, _NotARepo, ValueError):
            return None
    return closes[key]


def _git_merged(root, commit, closes) -> set:
    """The acceptance tests among the merge commit's own paths that are
    not its own change by DEC-918: those outside D (``_git_merge_diff``),
    where the merge commit holds exactly the entry (blob and mode, or
    absence) that git's own merge of its two parents writes, with no
    conflict on it, whether or not both parents changed the path.

    Empty where it cannot be shown (D is ``None``), and empty when D
    holds a path that ``read_merge`` does not count as the merge commit's
    own: a drop behind a rename, or of a moved-aside copy, is then not
    compared at all, and the merge is judged as before DEC-918.  No git
    process for a merge commit with no own acceptance test.
    """
    acc = {p for p in commit[4] if p.startswith(ACCEPTANCE + "/")}
    if len(set(commit[1])) != 2 or not acc:
        return set()
    d = _git_merge_diff(root, commit, closes)
    if d is None or not d <= set(commit[4]):
        return set()
    return acc - d

def _judge_commit(root, commit, role, tid, sub, orch_own, head,
                  decide_fn, closes, lift=True):
    """``(paths, why)`` when *commit* of a forward move is a finding,
    else ``None`` (W1-50).

    Only in an orchestrator session's own call is a commit judged by its
    own ``Role`` and ``Task`` trailers; in any other call it is judged
    against the caller, and another role's trailer is a finding
    (DEC-319, DEC-327).

    An acceptance test a merge commit holds exactly as git's own merge
    of its parents writes it (``_git_merged``) is not judged at all,
    neither as the merge commit's own change nor against the scope,
    unless the merge differs from git's own merge at a path that is not
    its own (DEC-918).
    """
    from gov.containment.scope import _path_allowed
    from gov.util.freeze import FREEZE_FLAG
    from gov.util.tickets import _load_ticket
    if len(commit[1]) > 1:
        same = _git_merged(root, commit, closes)
        commit = (*commit[:4], [p for p in commit[4] if p not in same])
    sha, _, roles, tasks, paths = commit
    rr = os.path.realpath(root)

    def outside(c_role, c_tid, c_sub, fn=decide_fn):
        # A path is judged by its name in the commit: where a directory
        # on the way to it is a symbolic link in the working tree, the
        # name is not where a write would go, and the path is a finding.
        return [p for p in paths
                if os.path.realpath(os.path.dirname(os.path.join(rr, p)))
                != os.path.dirname(os.path.join(rr, p))
                or not _in_scope(
                    os.path.join(rr, p), root, c_role, c_tid, c_sub, fn)]

    # Role: owner, whatever whitespace and characters that do not show
    # stand in or around the word.
    if any("".join(c for c in r if c.isprintable() and c != " ").lower()
           == "owner" for r in roles):
        return paths, "a Role: owner commit made during an agent's call"
    # DEC-390, DP-16: a worker's commit changes no ticket file, whatever
    # the ticket's paths say.  DEC-394, DP-17: nor does any commit of a
    # worker's call, with or without trailers.
    tickets = [p for p in paths if p.startswith(".tickets/")
               ] if not orch_own or any(
                   r != "orchestrator" for r in roles) else []
    if not orch_own:
        if roles and roles != [sub or role]:
            return paths, "its Role trailer is not the caller's role"
        bad = outside(role, tid, sub)
    elif not (roles and tasks):
        bad = outside(role, tid, sub)  # DEC-267: against the caller
    elif len(roles) > 1 or len(tasks) > 1:
        bad = paths  # DEC-268: several different values allow nothing
    else:
        c_role, c_task = roles[0], tasks[0]
        fn = decide_fn
        # DEC-359: the orchestrator's scope does not depend on the ticket.
        t = None if c_role == "orchestrator" else _load_ticket(root, c_task)
        if t:
            # The ticket's file as committed at HEAD and as the working
            # tree holds it: the commit passes only if both allow it.
            tfile = f".tickets/{t.get('id', '')}.md"
            if "at HEAD:" + tfile not in closes:
                closes["at HEAD:" + tfile] = _ticket_at(root, head, tfile)
            h = closes["at HEAD:" + tfile]
            if not h or c_task not in (h.get("id"), h.get("wbs_id")):
                return paths, "names a ticket whose file is not committed at HEAD"
            closed = "closed" in (t.get("status"), h.get("status"))
            if closed:
                # DEC-318: by the ticket only before its close commit.
                if tfile not in closes:
                    closes[tfile] = _close_commit(root, head, tfile)
                close = closes[tfile]
                try:
                    before = bool(close) and close != sha and _is_ancestor(
                        root, sha, close)
                except _GitError:
                    before = False
                if not before:
                    return paths, ("names a closed ticket, "
                                   "not before its close commit")

            def pats(tk):
                if not closed and tk.get("status") != "in_progress":
                    return []
                if c_role == "independent-test-designer":
                    return [ACCEPTANCE + "/**"]
                if tk.get("role") != c_role:
                    return []
                return [p for p in tk.get("allowed_paths", [])
                        if not _is_under_acceptance(p.rstrip("*/ "))]
            both = pats(t), pats(h)

            def fn(tool, ti, r, c_r, c_t, c_s):
                # A closed ticket's paths as they were: nothing while
                # frozen, and no held-out path (decide refuses every
                # tool there).  A ticket in progress: as decide allows.
                ok = (not os.path.exists(os.path.join(r, FREEZE_FLAG))
                      and decide_fn("Read" if closed else tool,
                                    ti, r, c_r, c_t, c_s)[0] == "allow"
                      and all(_path_allowed(ti["file_path"], r, p, c_r)
                              for p in both))
                return ("allow" if ok else "deny"), ""
        bad = outside(c_role, c_task, None, fn)
    # DEC-410, DP-21 and DP-27: whatever the merge commit's trailers.
    merged = _merge_own(commit)
    # DEC-572: but a ticket file it holds as one parent has it is not its
    # own change when every commit that brought that version passes.
    named = ""
    for p in [p for p in merged if lift and p.startswith(".tickets/")]:
        fails = _lifted(root, commit, p, head, decide_fn, closes)
        if fails is None:
            merged.remove(p)
        elif fails:
            named += (f"; commit {fails[:12]} brought the version of {p}"
                      " and does not pass")
    if merged:
        return (bad + [p for p in merged if p not in bad],
                "a merge commit's own change to a ticket file or an"
                " acceptance test" + named)
    if tickets:
        return (bad + [p for p in tickets if p not in bad],
                "a ticket file in a commit with a worker's Role trailer"
                " or made in a worker's call")
    return (bad, "committed path(s) outside allowed paths") if bad else None


# ---- scope check (handles symlinks -- repair 3) -------------------

def _in_scope(abs_p, root, role, tid, sub, decide_fn):
    """True when *abs_p* is inside the caller's allowed paths.

    A symbolic link is judged by its own location (the directory it
    sits in), not by where it points.  We ask ``decide`` about a
    stand-in path in the same directory that is not a link.
    """
    if os.path.islink(abs_p):
        parent = os.path.realpath(os.path.dirname(abs_p))
        stand = os.path.join(
            parent, os.path.basename(abs_p) + ".__containment__")
        d, _ = decide_fn("Write", {"file_path": stand},
                         root, role, tid, sub)
    else:
        d, _ = decide_fn("Write", {"file_path": abs_p},
                         root, role, tid, sub)
    return d == "allow"

# ---- public read-only judgement (DEC-453) ----------------------------

class _CommitFinding(NamedTuple):
    commit: str
    paths: list
    reason: str


def judge_commits(root: str, commit_ids: list) -> list:
    """Judge each commit by its trailers exactly as the post-command check
    judges the commits of an orchestrator session's own call, and return
    the findings.

    Read-only: nothing is restored, no finding record is written, nothing
    is created or changed under ``.gov-runtime/``, and HEAD, the index
    and the working tree are unchanged.

    Raises ``ContainmentError`` for an empty list, an unknown commit id,
    a path that is not a repository, or a git failure.
    """
    from gov.containment.merge import MergeReadError, read_merge
    from gov.containment.scope import decide

    if not commit_ids:
        raise ContainmentError("nothing to judge")

    try:
        head = _git(root, "rev-parse", "HEAD").strip()
    except _NotARepo as e:
        raise ContainmentError(str(e)) from e
    except _GitError as e:
        raise ContainmentError(str(e)) from e

    findings: list = []
    closes: dict = {}

    for cid in commit_ids:
        try:
            commit = _read_one_commit(root, cid)
        except (_GitError, _NotARepo) as e:
            raise ContainmentError(str(e)) from e

        if len(commit[1]) > 1:
            try:
                commit = (commit[0], commit[1], commit[2], commit[3],
                          list(read_merge(root, commit[0]).own))
            except MergeReadError as e:
                raise ContainmentError(str(e)) from e

        res = _judge_commit(
            root, commit,
            role="orchestrator", tid=None, sub=None,
            orch_own=True, head=head,
            decide_fn=decide, closes=closes,
        )
        if res is not None:
            paths, reason = res
            findings.append(_CommitFinding(
                commit=cid, paths=paths, reason=reason))

    return findings
