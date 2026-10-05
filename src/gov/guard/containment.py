"""Post-command containment check (W1-03).

Public entry points, one per hook (DEC-126):

- ``take_snapshot`` -- PreToolUse: captures ``git status --porcelain -z``
  with per-dirty-path fingerprints and ``HEAD``.
- ``check_containment`` -- PostToolUse: compares current tree and HEAD
  with the snapshot; flags / restores; records findings (DEC-122).
- ``mark_concurrent_write`` -- PreToolUse: increments the sequence
  counter when a Write/Edit/NotebookEdit is allowed (DEC-124).

Scope is derived from the guard's ``decide()`` (CAP-58.a).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time

FINDINGS_REL = ".gov-runtime/findings.jsonl"
RECORDS_REL = ".gov-runtime/records.jsonl"
SNAPSHOT_DIR_REL = ".gov-runtime/snapshots"
LAST_HEAD_REL = ".gov-runtime/last_head.json"
SEQ_FILE = ".seq"
ACCEPTANCE = "tests/acceptance"
_GIT_TIMEOUT = 10
_CLEANUP_AGE_S = 3600.0

# DEC-144, DEC-145: a pending snapshot of another actor's call that never
# ended no longer blocks restoration once ten minutes have passed.
PENDING_SNAPSHOT_TIMEOUT_S = 600


def _get_pending_timeout() -> float:
    """Return the pending-snapshot timeout in seconds (DEC-145).

    The override is used only when it is a finite number greater than
    zero.  Anything else (empty, not a number, zero, negative, ``nan``,
    ``inf``) falls back to the default.
    """
    import math
    try:
        v = os.environ.get("GOV_PENDING_SNAPSHOT_TIMEOUT_S")
        if v is not None:
            fv = float(v)
            if math.isfinite(fv) and fv > 0:
                return fv
    except (ValueError, TypeError):
        pass
    return float(PENDING_SNAPSHOT_TIMEOUT_S)


# ---- git helper --------------------------------------------------

class _NotARepo(Exception):
    pass


class _GitError(Exception):
    pass


# Every git call reads the real objects of the repository at its root,
# whatever refs/replace/, .git/info/grafts, .git/shallow or a commit-graph
# file holds, and whatever repository an inherited variable names.
_GIT = ("git", "--no-replace-objects", "-c", "core.commitGraph=false")
_GIT_ELSEWHERE = (
    "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_NAMESPACE")


def _git_env() -> dict:
    env = {k: v for k, v in os.environ.items() if k not in _GIT_ELSEWHERE}
    env.update(GIT_GRAFT_FILE=os.devnull, GIT_SHALLOW_FILE=os.devnull)
    return env


def _git(root: str, *args: str, ok: tuple = (0,)) -> str:
    """Run a git command and return stdout.  Raises on failure: an exit
    code that is not among *ok*."""
    try:
        p = subprocess.run(
            [*_GIT, "-C", root, *args],
            capture_output=True, text=True,
            timeout=_GIT_TIMEOUT, check=False, env=_git_env(),
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        raise _GitError(str(e)) from e
    if p.returncode == 128 and "not a git repository" in p.stderr.lower():
        raise _NotARepo(p.stderr.strip())
    if p.returncode not in ok:
        raise _GitError(p.stderr.strip())
    return p.stdout


# ---- NUL-separated status parsing (repair 6) --------------------

def _parse_status_z(raw: str) -> dict:
    """Parse ``git status --porcelain -z -uall`` into {path: XY}.

    NUL-separated output has no quoting, so non-ASCII and names with
    spaces come through as-is.  Renames produce entries for both the
    old and the new path.
    """
    if not raw:
        return {}
    result: dict = {}
    parts = raw.split("\0")
    i = 0
    while i < len(parts):
        e = parts[i]
        if len(e) < 3:
            i += 1
            continue
        code, path = e[:2], e[3:]
        if code[0] in "RC" and i + 1 < len(parts) and parts[i + 1]:
            result[path] = code
            result[parts[i + 1]] = code
            i += 2
        else:
            result[path] = code
            i += 1
    return result


def _is_under_acceptance(rel: str) -> bool:
    return rel == ACCEPTANCE or rel.startswith(ACCEPTANCE + "/")


def _list_files(root: str, dirpath: str) -> list:
    """Expand a directory entry to individual files."""
    full = os.path.join(root, dirpath)
    out: list = []
    try:
        for dp, _, fnames in os.walk(full):
            for n in fnames:
                out.append(os.path.relpath(os.path.join(dp, n), root))
    except OSError:
        pass
    return out


# ---- fingerprinting dirty paths (repairs 1, 2) ------------------

def _fingerprints(root: str, dirty: dict) -> dict:
    """(size, mtime_ns, staged_blob) per dirty path -- cheap enough
    to run at every snapshot; detects a second change to an
    already-dirty path."""
    blobs: dict = {}
    try:
        raw = _git(root, "ls-files", "-s", "-z")
        for entry in raw.split("\0"):
            tab = entry.find("\t")
            if tab < 0:
                continue
            ps = entry[:tab].split()
            if len(ps) >= 2:
                blobs[entry[tab + 1:]] = ps[1]
    except (_GitError, _NotARepo):
        pass
    rr = os.path.realpath(root)
    fps: dict = {}
    for path in dirty:
        try:
            st = os.lstat(os.path.join(rr, path))
            fps[path] = [st.st_size, st.st_mtime_ns, blobs.get(path, "")]
        except OSError:
            fps[path] = [-1, -1, blobs.get(path, "")]
    return fps


def _fp_changed_batch(root: str, paths_fps: dict) -> set:
    """Return the subset of *paths_fps* whose fingerprint changed.

    *paths_fps* maps ``{path: [size, mtime_ns, staged_blob]}``.
    Stat + one ``git ls-files`` call for all paths (fix 3).
    """
    if not paths_fps:
        return set()
    rr = os.path.realpath(root)
    changed: set = set()
    need_blob: list = []
    for path, old in paths_fps.items():
        try:
            st = os.lstat(os.path.join(rr, path))
            sz, mt = st.st_size, st.st_mtime_ns
        except OSError:
            sz, mt = -1, -1
        if sz != old[0] or mt != old[1]:
            changed.add(path)
        else:
            need_blob.append(path)
    if not need_blob:
        return changed
    # One git ls-files call for all paths that need blob comparison.
    blobs: dict = {}
    try:
        raw = _git(root, "ls-files", "-s", "-z", "--", *need_blob)
        for entry in raw.split("\0"):
            tab = entry.find("\t")
            if tab < 0:
                continue
            ps = entry[:tab].split()
            if len(ps) >= 2:
                blobs[entry[tab + 1:]] = ps[1]
    except (_GitError, _NotARepo):
        # On failure, treat all as changed.
        changed.update(need_blob)
        return changed
    for path in need_blob:
        if blobs.get(path, "") != paths_fps[path][2]:
            changed.add(path)
    return changed


# ---- sequence counter (overlap, DEC-124 reading 4) ---------------

def _seq_path(root: str) -> str:
    return os.path.join(root, SNAPSHOT_DIR_REL, SEQ_FILE)


def _read_seq(root: str) -> int:
    """Counter value = file size (one byte per event)."""
    p = _seq_path(root)
    try:
        return os.path.getsize(p)
    except OSError:
        return 0


def _increment_seq(root: str) -> int:
    """Append one byte atomically (``O_APPEND``).

    Two hooks running at the same instant each append their own byte,
    so no increment is lost.  The counter is the file size.
    """
    p = _seq_path(root)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        os.write(fd, b".")
    finally:
        os.close(fd)
    return _read_seq(root)


# ---- clear actor snapshots (DEC-142, DEC-146) ---------------------

def clear_actor_snapshots(root: str, session_id: str,
                          agent_id: str) -> None:
    """Remove pending snapshots of this actor.

    Called when the PreToolUse hook sees a later tool call of the same
    actor (same ``session_id`` and ``agent_id``).  A later call proves
    the earlier one is over (DEC-142); its snapshot no longer blocks
    restoration for other actors.
    """
    sdir = os.path.join(root, SNAPSHOT_DIR_REL)
    try:
        entries = os.listdir(sdir)
    except OSError:
        return
    for name in entries:
        if not name.endswith(".json"):
            continue
        p = os.path.join(sdir, name)
        try:
            with open(p, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError, ValueError):
            continue
        if (data.get("session_id", ""),
                data.get("agent_id", "")) == (session_id, agent_id):
            try:
                os.unlink(p)
            except OSError:
                pass


# ---- last-HEAD tracking (DEC-132 default 4) ----------------------

def _save_last_head(root: str, commit: str, branch: str) -> None:
    p = os.path.join(root, LAST_HEAD_REL)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    try:
        with open(p, "w") as f:
            json.dump({"commit": commit, "branch": branch}, f)
    except OSError:
        pass


def _load_last_head(root: str):
    try:
        with open(os.path.join(root, LAST_HEAD_REL)) as f:
            d = json.load(f)
        return d.get("commit", ""), d.get("branch", "")
    except (OSError, json.JSONDecodeError, ValueError):
        return None, None


# ---- cleanup ------------------------------------------------------

def _cleanup_old(snapshot_dir: str) -> None:
    try:
        now = time.time()
        for name in os.listdir(snapshot_dir):
            if not name.endswith(".json"):
                continue
            p = os.path.join(snapshot_dir, name)
            try:
                if now - os.path.getmtime(p) > _CLEANUP_AGE_S:
                    os.unlink(p)
            except OSError:
                pass
    except OSError:
        pass


# ---- pending-snapshot overlap (fix 1) -----------------------------

def _check_pending_snapshots(root: str, own_id: str,
                             own_session: str, own_agent: str) -> bool:
    """True when another actor has a pending (not yet consumed) snapshot.

    An actor is the pair ``(session_id, agent_id)``.  A pending snapshot
    of the **same** actor is a leftover (its call was refused or never
    ended); it is silently removed and does not cause overlap.  Snapshots
    older than ``PENDING_SNAPSHOT_TIMEOUT_S`` (DEC-142, DEC-144) are
    known to be over and do not block.
    """
    sdir = os.path.join(root, SNAPSHOT_DIR_REL)
    now = time.time()
    timeout = _get_pending_timeout()
    other_pending = False
    try:
        entries = os.listdir(sdir)
    except OSError:
        return False
    for name in entries:
        if not name.endswith(".json"):
            continue
        stem = name[:-5]
        if stem == own_id:
            continue  # our own snapshot (already consumed by caller)
        p = os.path.join(sdir, name)
        try:
            age = now - os.path.getmtime(p)
        except OSError:
            continue
        if age > timeout:
            continue  # known to be over by time (DEC-142, DEC-144)
        try:
            with open(p, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError, ValueError):
            continue
        snap_session = data.get("session_id", "")
        snap_agent = data.get("agent_id", "")
        if (snap_session, snap_agent) == (own_session, own_agent):
            # Same actor leftover -- remove it silently.
            try:
                os.unlink(p)
            except OSError:
                pass
        else:
            other_pending = True
    return other_pending


# ---- before-snapshot (PreToolUse) ---------------------------------

def take_snapshot(root: str, tool_use_id: str,
                  session_id: str = "", agent_id: str = "") -> bool:
    """Capture git status + fingerprints + HEAD.  False = not a repo."""
    sdir = os.path.join(root, SNAPSHOT_DIR_REL)
    os.makedirs(sdir, exist_ok=True)
    _cleanup_old(sdir)

    try:
        raw = _git(root, "status", "--porcelain", "-z",
                   "--untracked-files=all")
    except _NotARepo:
        return False

    dirty = _parse_status_z(raw)
    fps = _fingerprints(root, dirty)

    hc = hb = ""
    try:
        hc = _git(root, "rev-parse", "HEAD").strip()
    except (_GitError, _NotARepo):
        pass
    try:
        hb = _git(root, "symbolic-ref", "-q", "--short", "HEAD").strip()
    except (_GitError, _NotARepo):
        pass

    seq = _increment_seq(root)
    snap = {
        "tool_use_id": tool_use_id,
        "status": raw,
        "fingerprints": fps,
        "head_commit": hc,
        "head_branch": hb,
        "seq": seq,
        "ts": time.time(),
        "session_id": session_id,
        "agent_id": agent_id,
    }
    with open(os.path.join(sdir, f"{tool_use_id}.json"), "w",
              encoding="utf-8") as f:
        json.dump(snap, f, separators=(",", ":"))

    _save_last_head(root, hc, hb)
    return True


def _load_snapshot(root: str, tool_use_id: str):
    if not tool_use_id:
        return None
    p = os.path.join(root, SNAPSHOT_DIR_REL, f"{tool_use_id}.json")
    try:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError, ValueError):
        return None
    try:
        os.unlink(p)
    except OSError:
        pass
    return data


# ---- write-tool overlap marker (repair 5) -------------------------

def mark_concurrent_write(root: str) -> None:
    """Increment seq when a Write/Edit/NotebookEdit is allowed."""
    _increment_seq(root)


# ---- findings (DEC-122) -------------------------------------------

def _make_finding(sid, agent_type, role, ticket, cmd,
                  paths, action, reason):
    return {
        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "session_id": sid,
        "agent_type": agent_type or "",
        "role": role or "",
        "ticket": ticket or "",
        "tool": "Bash",
        "command": cmd,
        "paths": list(paths),
        "action": action,
        "reason": reason,
    }


def _record_findings(root: str, findings: list) -> None:
    p = os.path.join(root, FINDINGS_REL)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        for fi in findings:
            f.write(json.dumps(fi, separators=(",", ":")) + "\n")


def _write_records(root: str, records: list) -> None:
    """Write JSON lines to ``records.jsonl`` (DEC-177)."""
    p = os.path.join(root, RECORDS_REL)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, separators=(",", ":")) + "\n")


# ---- acceptance-test restoration ----------------------------------

def _restore_from_head(root: str, paths: list,
                       commit: str = "HEAD") -> tuple:
    """Restore acceptance-test paths to *commit* (default ``HEAD``).

    Returns ``(restored, failed)`` -- lists of paths.  When restoring
    from ``HEAD``, git status is checked to verify success (repair 10).
    When restoring from a specific commit (DEC-143), the file may
    still appear in git status because it differs from the current
    ``HEAD``; the verification is skipped.
    """
    rr = os.path.realpath(root)
    checkout: list = []
    remove: list = []

    for rel in paths:
        try:
            _git(root, "cat-file", "-e", f"{commit}:{rel}")
            checkout.append(rel)
        except (_GitError, _NotARepo):
            remove.append(rel)

    if checkout:
        try:
            _git(root, "checkout", commit, "--", *checkout)
        except _GitError:
            pass

    for rel in remove:
        full = os.path.join(rr, rel)
        try:
            if os.path.isfile(full) or os.path.islink(full):
                os.unlink(full)
            elif os.path.isdir(full):
                import shutil
                shutil.rmtree(full)
        except OSError:
            pass
        try:
            _git(root, "rm", "--cached", "-f",
                 "--ignore-unmatch", "--", rel)
        except _GitError:
            pass
        _remove_empty_parents(os.path.dirname(full), rr)

    # When restoring from a specific commit that differs from the
    # current HEAD (DEC-143), the restored paths may stay in git status
    # because their content differs from the current HEAD.  Verification
    # against git status is not meaningful here; instead, verify each
    # path against the target commit's content.
    if commit != "HEAD":
        ok = [p for p in paths if _file_matches_commit(root, p, commit)]
        bad = [p for p in paths if not _file_matches_commit(root, p, commit)]
        return ok, bad

    # Verify (repair 10): a path still in git status was not restored.
    try:
        raw = _git(root, "status", "--porcelain", "-z",
                   "--untracked-files=all")
        still = set(_parse_status_z(raw))
    except (_GitError, _NotARepo):
        return [], list(paths)

    return ([p for p in paths if p not in still],
            [p for p in paths if p in still])


def _remove_empty_parents(d: str, stop: str) -> None:
    rs = os.path.realpath(stop)
    while d and os.path.realpath(d) != rs:
        try:
            if os.path.isdir(d) and not os.listdir(d):
                os.rmdir(d)
                d = os.path.dirname(d)
            else:
                break
        except OSError:
            break


# ---- file-content comparison (DEC-143 reading 3) -----------------

def _file_matches_commit(root: str, rel: str, commit: str) -> bool:
    """True when the working-tree file already has *commit*'s content.

    Used to tell whether a path was explicitly written to by the
    command or only appears changed because the HEAD move shifted the
    reference point.  A missing file matches a missing blob.
    """
    rr = os.path.realpath(root)
    full = os.path.join(rr, rel)
    try:
        committed = _git(root, "show", f"{commit}:{rel}")
    except (_GitError, _NotARepo):
        committed = None
    try:
        if os.path.isfile(full) and not os.path.islink(full):
            with open(full, encoding="utf-8",
                      errors="surrogateescape") as f:
                current = f.read()
        else:
            current = None
    except OSError:
        current = None
    return current == committed


# ---- HEAD-move helpers (DEC-129) ----------------------------------

def _is_ancestor(root: str, old: str, new: str) -> bool:
    """True when *old* is an ancestor of *new*.  Raises on failure."""
    try:
        p = subprocess.run(
            [*_GIT, "-C", root, "merge-base", "--is-ancestor", old, new],
            capture_output=True, timeout=_GIT_TIMEOUT, check=False,
            env=_git_env(),
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


def _move_commits(root: str, old: str, new: str) -> list:
    """The commits of ``old..new``, newest first, each as
    ``(id, parents, Role values, Task values, paths)``.

    One git process.  Trailers are read from the final trailer block
    only, as git finds it (DEC-182, DEC-267); the block comes as the
    message holds it and its lines are read here, so no trailer setting
    of the repository renames or hides a ``Role`` or a ``Task``.  Paths
    are listed without rename detection, so both ends of a rename
    appear (repair 7); a merge commit lists only its own change, as
    ``read_merge`` reads it (DEC-269; DEC-394, DP-18): what it changes
    against its first parent and no other parent brought.

    Everything is separated by NUL, the one byte no trailer and no file
    name can hold, and nothing is unquoted.  The token after a commit's
    ids is its trailer block and the token after a raw entry (``:``) is
    its path, whatever they hold, so no byte a commit's author chooses
    is read as structure.  Output that cannot be read raises, so the
    move becomes a finding.
    """
    from gov.guard.containment_merge import read_merge
    out = _git(root, *_LOG_DEFAULTS, "-z", "-c", "--raw", "--no-abbrev",
               _LOG_FORMAT, f"{old}..{new}")
    unreadable = _GitError("the commits of the HEAD move cannot be read")
    commits: list = []
    tokens = iter(out.split("\0"))
    for tok in tokens:
        if tok.lstrip("\n").startswith(":"):
            path = next(tokens, "")
            if not commits or not path:
                raise unreadable
            commits[-1][4].append(path)
        elif _COMMIT_IDS.fullmatch(tok):
            ids = tok.split()
            commits.append((ids[0], ids[1:], set(), set(), []))
            for key, value in _role_and_task(next(tokens, "")):
                if value:
                    commits[-1][2 if key == "role" else 3].add(value)
        elif tok.strip("\n"):
            raise unreadable
    if not commits:
        raise unreadable
    for c in commits:
        if len(c[1]) > 1:
            c[4][:] = read_merge(root, c[0]).own
    return [(c[0], c[1], sorted(c[2]), sorted(c[3]), c[4]) for c in commits]


def _ticket_at(root: str, rev: str, ticket_file: str):
    """The ticket's frontmatter as committed at *rev*, or ``None``."""
    from gov.guard.decide import _parse_frontmatter
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


def _judge_commit(root, commit, role, tid, sub, orch_own, head,
                  decide_fn, closes):
    """``(paths, why)`` when *commit* of a forward move is a finding,
    else ``None`` (W1-50).

    Only in an orchestrator session's own call is a commit judged by its
    own ``Role`` and ``Task`` trailers; in any other call it is judged
    against the caller, and another role's trailer is a finding
    (DEC-319, DEC-327).
    """
    from gov.guard.decide import (
        FREEZE_FLAG, _load_ticket, _path_allowed)
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


# ---- report formatting (repair 11) --------------------------------

def _format_report(flagged, reverted, failed, head_msg):
    """Build a readable report for the agent.

    Paths appear as ``git status`` spells them so the agent can act
    on them.
    """
    parts: list = []
    if head_msg:
        parts.append(head_msg)
    if reverted:
        ps = ", ".join(sorted(reverted))
        parts.append(f"Acceptance test restored from HEAD: {ps}.")
    if failed:
        ps = ", ".join(sorted(failed))
        parts.append(f"Restore failed, left in place: {ps}.")
    if flagged:
        ps = ", ".join(sorted(flagged))
        parts.append(
            f"Outside allowed paths, left in place: {ps}.")
    return ("Containment: " + " ".join(parts)) if parts else ""


# ---- main entry ---------------------------------------------------

def check_containment(
    project_root: str,
    role: str | None,
    ticket_id: str | None,
    subagent_type: str | None,
    session_id: str,
    agent_type: str | None,
    command: str,
    tool_use_id: str,
) -> str:
    """Compare the current tree + HEAD with the before-snapshot.

    Returns report text (empty = nothing to report).
    Raises ``_GitError`` on hard git failures so the hook can record
    them as findings.
    """
    from gov.guard.decide import decide  # noqa: E402

    snap = _load_snapshot(project_root, tool_use_id)
    has_snap = snap is not None

    # Overlap detection (DEC-124 reading 4).
    overlapping = False
    if has_snap:
        overlapping = _read_seq(project_root) != snap.get("seq")
        # A pending snapshot of a different actor also means overlap.
        if not overlapping:
            snap_session = snap.get("session_id", "")
            snap_agent = snap.get("agent_id", "")
            overlapping = _check_pending_snapshots(
                project_root, tool_use_id,
                snap_session, snap_agent)

    # Current status -- NUL-separated, no quoting (repair 6).
    try:
        cur_raw = _git(project_root, "status", "--porcelain", "-z",
                       "--untracked-files=all")
    except _NotARepo:
        _increment_seq(project_root)
        return ""
    # _GitError propagates intentionally (repair 8).

    cur_head = cur_branch = ""
    try:
        cur_head = _git(project_root, "rev-parse", "HEAD").strip()
    except (_GitError, _NotARepo):
        pass
    try:
        cur_branch = _git(
            project_root, "symbolic-ref", "-q", "--short", "HEAD"
        ).strip()
    except (_GitError, _NotARepo):
        pass

    before = _parse_status_z(snap["status"]) if has_snap else {}
    after = _parse_status_z(cur_raw)
    before_fps = snap.get("fingerprints", {}) if has_snap else {}
    dirty_at_snap = set(before.keys())

    # ---- what THIS call changed (DEC-124) ----
    if has_snap:
        changed: set = set()
        fp_check: dict = {}
        for path, code in after.items():
            if path not in before:
                changed.add(path)
            elif before[path] != code:
                changed.add(path)
            elif path in before_fps:
                fp = before_fps[path]
                if isinstance(fp, list) and len(fp) >= 3:
                    fp_check[path] = fp
        # Batch fingerprint comparison (fix 3: one git call).
        if fp_check:
            changed.update(_fp_changed_batch(project_root, fp_check))
        # Paths dirty before but clean now (reading 5).
        for path in before:
            if path not in after:
                changed.add(path)
    else:
        changed = set(after.keys())

    # Expand directory entries to individual files.
    expanded: set = set()
    for path in changed:
        if path.endswith("/"):
            files = _list_files(project_root, path)
            if files:
                expanded.update(files)
            else:
                expanded.add(path.rstrip("/"))
        else:
            expanded.add(path)
    changed = expanded

    # ---- HEAD-move detection (DEC-129, DEC-132) ----
    head_findings: list = []
    committed_out: set = set()
    non_fwd = False
    head_msg = ""

    old_head = snap.get("head_commit", "") if has_snap else None
    old_branch = snap.get("head_branch", "") if has_snap else None

    # DEC-132 default 4: HEAD move with no before-snapshot.
    if not has_snap and cur_head:
        lh_commit, _ = _load_last_head(project_root)
        if lh_commit and lh_commit != cur_head:
            head_findings.append(_make_finding(
                session_id, agent_type, role, ticket_id, command,
                [], "flagged",
                "HEAD moved with no before-snapshot"))
            non_fwd = True
            head_msg = "HEAD moved with no before-snapshot (flagged)."

    if has_snap and cur_head and old_head and cur_head != old_head:
        # Determine whether the move is a forward move on the same
        # branch.  Any git failure, and a commit list that cannot be
        # read => treat as non-forward (repair 8).  A merge is judged
        # commit by commit only in an orchestrator session's own call
        # (DEC-266); in any other call it stays non-forward.
        orch_own = ((role or "").strip() == "orchestrator"
                    and not subagent_type)
        commits: list = []
        try:
            fwd = (bool(cur_branch) and cur_branch == old_branch
                   and _is_ancestor(project_root, old_head, cur_head))
            if fwd:
                commits = _move_commits(project_root, old_head, cur_head)
                fwd = orch_own or all(len(c[1]) < 2 for c in commits)
        except (_GitError, ValueError):
            fwd = False

        if fwd:
            # Commit by commit, oldest first (DEC-255, DEC-327).  The
            # record keeps the caller's role and ticket; the reason
            # names the commit and its trailers (DEC-270).
            closes: dict = {}
            msgs: list = []
            for c in reversed(commits):
                res = _judge_commit(
                    project_root, c, role, ticket_id, subagent_type,
                    orch_own, cur_head, decide, closes)
                if res is None:
                    continue
                bad, why = res
                committed_out.update(bad)
                named = (f"commit {c[0][:12]} (Role: "
                         f"{', '.join(c[2]) or 'none'}; Task: "
                         f"{', '.join(c[3]) or 'none'})")
                head_findings.append(_make_finding(
                    session_id, agent_type, role, ticket_id, command,
                    bad, "flagged", f"{named}: {why}"))
                msgs.append(f"{named}: {why}: "
                            + (", ".join(sorted(bad)) or "no path") + ".")
            if msgs:
                head_msg = "Flagged, left in place: " + " ".join(msgs)

        if not fwd:
            head_findings.append(_make_finding(
                session_id, agent_type, role, ticket_id, command,
                [], "flagged",
                "HEAD moved (not a forward move on the same branch)"))
            non_fwd = True
            head_msg = "HEAD moved (not a forward move, flagged)."

    # ---- classify by scope (repair 9: also after non-forward) ----
    rr = os.path.realpath(project_root)
    oos: list = []
    acc_breach: list = []

    for path in sorted(changed):
        if path in committed_out:
            continue
        if not _in_scope(os.path.join(rr, path), project_root,
                         role, ticket_id, subagent_type, decide):
            if _is_under_acceptance(path):
                acc_breach.append(path)
            else:
                oos.append(path)

    # ---- orchestrator records (DEC-177) ----
    # When the orchestrator (in its own session) changes a path outside
    # the ticket's specific allowed_paths, that change is a record in
    # records.jsonl, not a containment finding.  Acceptance paths stay
    # findings; paths denied by the guard (DEC-176) are in oos above.
    _acting = subagent_type if subagent_type else role
    _srole = (role or "").strip()
    if _acting == "orchestrator" and _srole == "orchestrator":
        from gov.guard.decide import _load_ticket, _match_pattern
        ticket_pats: list = []
        if ticket_id:
            t = _load_ticket(project_root, ticket_id)
            if t:
                ticket_pats = [p for p in t.get("allowed_paths", []) if p]

        skip = set(committed_out) | set(oos) | set(acc_breach)
        record_set: list = []
        for path in sorted(changed):
            if path in skip:
                continue
            if _is_under_acceptance(path):
                continue
            if ticket_pats and any(_match_pattern(path, p)
                                   for p in ticket_pats):
                continue
            record_set.append(path)

        if record_set:
            _write_records(project_root, [_make_finding(
                session_id, agent_type, role, ticket_id, command,
                record_set, "recorded",
                "change outside ticket paths")])

    # ---- act on findings ----
    findings: list = list(head_findings)
    all_flagged: list = []
    all_reverted: list = []
    all_failed: list = []

    # Acceptance-test breaches.
    if acc_breach:
        certain = has_snap and not overlapping
        can_revert = certain and not non_fwd
        # DEC-143: after a non-forward HEAD move with certain
        # attribution, restore from the pre-call HEAD.
        can_revert_from_snap = (certain and non_fwd
                                and bool(old_head))
        # Never restore paths dirty at the snapshot (repair 2).
        restorable = [p for p in acc_breach if p not in dirty_at_snap]
        dirty_b = [p for p in acc_breach if p in dirty_at_snap]

        if dirty_b:
            findings.append(_make_finding(
                session_id, agent_type, role, ticket_id, command,
                dirty_b, "flagged",
                "acceptance test was already dirty, not restored"))
            all_flagged.extend(dirty_b)

        if restorable and can_revert:
            ok, bad = _restore_from_head(project_root, restorable)
            if ok:
                findings.append(_make_finding(
                    session_id, agent_type, role, ticket_id, command,
                    ok, "reverted",
                    "acceptance test restored from HEAD"))
                all_reverted.extend(ok)
            if bad:
                findings.append(_make_finding(
                    session_id, agent_type, role, ticket_id, command,
                    bad, "flagged",
                    "acceptance test restore failed"))
                all_failed.extend(bad)
        elif restorable and can_revert_from_snap:
            # DEC-143 reading 3: a change the move itself made is
            # part of the move and is never reverted.  Only restore
            # paths whose working-tree content actually differs from
            # the pre-call HEAD.
            written = []
            move_only = []
            for p in restorable:
                if _file_matches_commit(project_root, p, old_head):
                    move_only.append(p)
                else:
                    written.append(p)
            if written:
                ok, bad = _restore_from_head(project_root, written,
                                             commit=old_head)
                if ok:
                    findings.append(_make_finding(
                        session_id, agent_type, role, ticket_id,
                        command, ok, "reverted",
                        "acceptance test restored from pre-call HEAD"))
                    all_reverted.extend(ok)
                if bad:
                    findings.append(_make_finding(
                        session_id, agent_type, role, ticket_id,
                        command, bad, "flagged",
                        "acceptance test restore failed"))
                    all_failed.extend(bad)
            if move_only:
                findings.append(_make_finding(
                    session_id, agent_type, role, ticket_id, command,
                    move_only, "flagged",
                    "acceptance test change (part of HEAD move)"))
                all_flagged.extend(move_only)
        elif restorable:
            findings.append(_make_finding(
                session_id, agent_type, role, ticket_id, command,
                restorable, "flagged",
                "acceptance test change (attribution uncertain)"))
            all_flagged.extend(restorable)

    # Other out-of-scope changes.
    if oos:
        findings.append(_make_finding(
            session_id, agent_type, role, ticket_id, command,
            oos, "flagged",
            "change outside allowed paths"))
        all_flagged.extend(oos)

    if findings:
        _record_findings(project_root, findings)

    # Save last HEAD and advance sequence.
    if cur_head:
        _save_last_head(project_root, cur_head, cur_branch)
    _increment_seq(project_root)

    return _format_report(all_flagged, all_reverted, all_failed,
                          head_msg)
