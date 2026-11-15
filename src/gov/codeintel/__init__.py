"""The code index: a wrapper of codebase-memory-mcp 0.11.0 (W1-16; DEC-076, CAP-12, CAP-03.e).

Each repository has its own home for the tool, under its ``.gov-runtime/``. The tool
never reads the repository: ``index(root)`` copies the files ``gov.secrets.indexable``
returns into a folder next to that home and the tool indexes the copy, so a file the
filter leaves out is not in the index at all. Neither is a file whose path holds a secret
by the same rules: the index stores paths. Every index is built anew; if the filter
cannot decide, there is no index. The answers are read from the graph the tool built.
The root must be the top level of a git repository whose ``.gov-runtime/`` is no link:
any other root is refused before anything is written or deleted. The tool's daemon keeps
its lock and socket files in ``daemon_dir(root)``, never in the tool's shared default
(DEC-338): in a test session under that session's own folder (also in a process the session starts
with an environment built anew, found from the mark above the repository), in a session ``gov launch``
started under its own temp folder (W2-56 S1, ``daemon_base``); a folder made for a tool that cannot
be started is not left. It does not serve the tool's loopback UI: every start of the tool sets ``ui_enabled``
to ``false`` in the home first (DEC-362). The graph is read in one session of the tool, so that
its daemon starts once for it (DEC-561).
"""

from __future__ import annotations

import functools
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from gov.secrets import indexable, path_holds_secret, pool_size
from gov.util.gitenv import git_env

TOOL = "codebase-memory-mcp"
BASE_REL = ".gov-runtime/codeintel"
# Where the daemon directories stand: short, because a socket path holds at most 107 bytes (DEC-338). This is the
# place outside a test session and outside a launched session (``daemon_base``).
DAEMON_BASE = Path(f"/tmp/gov-cbm-{os.getuid()}")
# W2-56 S1 (DEC-799 item 1): a test session's own folder for its daemon directories (``tests/conftest.py`` makes it,
# sets this variable and removes the folder when the session ends) ...
BASE_ENV = "CODEINTEL_DAEMON_BASE"
# ... named also in a mark the conftest writes in each of its processes' pytest temp base, for a process the session
# starts with an environment built anew (no ``CODEINTEL_DAEMON_BASE``) on a repository under that base: the nearest
# mark above the repository, the user's own regular file, names the folder, unless this process wrote it (a case that
# removes the variable in the session's own process asks for the place outside a test session) ...
MARK = ".gov-cbm-base"
# ... and, in a session ``gov launch`` started, its own temp folder (``gov-launch-`` and a few letters, DEC-159),
# found from ``CLAUDE_CODE_TMPDIR``: the launcher's folder itself, or the CLI's ``claude-<uid>`` folder in it.
LAUNCH_TMP_ENV, LAUNCH_PREFIX, LAUNCH_SUB = "CLAUDE_CODE_TMPDIR", "gov-launch-", "cbm"
PROJECT = "code"
_PAGE, _BUDGET = 50000, 100_000_000  # rows and output tokens of one answer of the tool; more is paged
# Rows of one query's whole answer the tool gives at most: over it the tool refuses the query before its own paging
# (``offset``, ``max_rows``). The tool also cuts an answer short by its size, silently, and answers a string ``>`` in
# ``WHERE`` with 0 rows: no keyset cursor and no ``SKIP``/``LIMIT`` page is sound (the lead's probes, run 8b, items
# 13-14). So the links are read in pieces by their source node's path, one path a piece by equality, and inside a piece
# the tool cuts or that is over the cap, by link type; every piece counted first and its rows checked against its count.
CAP = 100_000
_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")  # an edge type or node label that may stand in a match
_NODES = "MATCH (n) RETURN n.qualified_name, n.name, n.label, n.file_path"
_EDGES = "MATCH (a)-[r]->(b) RETURN a.qualified_name, type(r), b.qualified_name"
_LABELLED = "MATCH (n:{}) RETURN n.qualified_name, n.name, n.label, n.file_path"
_TYPES = "MATCH (a)-[r]->(b) RETURN type(r), count(r)"
_LABELS = "MATCH (n) RETURN n.label, count(n)"
_HOLDERS = "MATCH (a)-[r:CONTAINS_FILE]->(n:File) RETURN a.label, count(r)"
_LINK = "id(r), a.qualified_name, type(r), b.qualified_name"  # the columns of a piece's links
RECORD = "gov-links.json"  # the per-file record of the last read that passed, under ``home(root)`` (S28)
_counted: dict = {}  # the graph's (nodes, edges) as the tool counted them, by the root ``_graph`` read
_stats: dict = {}  # the last read's pieces read, pieces taken from the record and wall time, by root
# Seconds a session of the tool has for one answer, and for its end once its input is closed; then it is killed.
_ANSWER_S, _END_S = 120.0, 10.0
# Nodes that say where something stands, and edges that are no use of a symbol by another.
_PLACES = {"Project", "Branch", "Folder", "File", "Module"}
_NO_USE = {"DEFINES", "DEFINES_METHOD", "CONTAINS_FILE", "CONTAINS_FOLDER", "HAS_BRANCH", "SEMANTICALLY_RELATED"}
_FUNCTIONS = {"Function", "Method"}

__all__ = ["callees", "callers", "daemon_base", "daemon_dir", "dead_code", "definitions", "home", "impact", "index",
           "launch_folder", "make_session_base", "marked_base", "projects", "references", "write_mark"]


def home(root: Path) -> Path:
    """The tool's home for the repository at ``root`` (its ``CBM_CACHE_DIR``)."""
    return Path(root).resolve() / BASE_REL / "home"


def launch_folder(env=None) -> Path | None:
    """The temp folder of the ``gov launch`` session this process runs in (W2-56, D-12), or None outside one."""
    given = (os.environ if env is None else env).get(LAUNCH_TMP_ENV) or ""
    if not os.path.isabs(given):
        return None
    place = Path(os.path.normpath(given))
    for folder in (place, place.parent):
        if folder.name.startswith(LAUNCH_PREFIX) and folder.parent != folder:
            return folder
    return None


def write_mark(folder: Path, base: Path) -> Path:
    """Write the mark (``MARK``) naming ``base`` in ``folder``, a test process's pytest temp base; return its path."""
    mark = Path(folder) / MARK
    staged = mark.with_name(f"{MARK}.{os.getpid()}")
    staged.write_text(json.dumps({"base": str(base), "pid": os.getpid()}), encoding="utf-8")
    os.replace(staged, mark)
    return mark


def marked_base(root) -> Path | None:
    """The test session's folder the nearest mark above ``root`` names (W2-56 S1); None where there is none, where it is
    no regular file of this user's, names no absolute folder, or was written by this process."""
    for folder in Path(os.path.abspath(root)).parents:
        mark = folder / MARK
        try:
            seen = os.lstat(mark)
        except OSError:
            continue
        if not stat.S_ISREG(seen.st_mode) or seen.st_uid != os.getuid():
            return None
        try:
            named = json.loads(mark.read_text(encoding="utf-8"))
            base, pid = named["base"], named["pid"]
        except (OSError, ValueError, LookupError, TypeError):
            return None
        if not isinstance(base, str) or not os.path.isabs(base) or pid == os.getpid():
            return None
        return Path(os.path.normpath(base))
    return None


def daemon_base(env=None, root=None) -> Path:
    """Where the daemon directories of this process stand: the test session's own folder (``CODEINTEL_DAEMON_BASE``),
    else the launched session's temp folder (``launch_folder``), else, for a repository ``root`` under a test process's
    temp base, the folder its mark names (``marked_base``: the shared place is never used during a test session), else
    ``DAEMON_BASE``."""
    env = os.environ if env is None else env
    given = env.get(BASE_ENV) or ""
    if os.path.isabs(given):
        return Path(os.path.normpath(given))
    launched = launch_folder(env)
    if launched is not None:
        return launched / LAUNCH_SUB
    marked = marked_base(root) if root is not None else None
    return marked if marked is not None else DAEMON_BASE


def make_session_base(env=None) -> Path:
    """A new folder for one test session's daemon directories (W2-56 S1), short enough for the tool's socket: in the
    launched session's temp folder, else under ``/tmp``, else under the temp folder. The caller removes it, and holds
    its owner's record in it, by which the next session removes it after a kill (``tests/conftest.py``, W2-56 R3): a
    change to these names is a change to the conftest's too."""
    import secrets
    import tempfile

    launched = launch_folder(env)
    if launched is not None:  # four letters: a launcher's folder of the older, longer name still fits (D-12)
        for _ in range(100):
            made = launched / ("c" + "".join(secrets.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in "xyz"))
            try:
                made.mkdir(mode=0o700)
                return made
            except FileExistsError:
                continue
            except OSError:
                break
    for place in (Path("/tmp"), Path(tempfile.gettempdir())):
        try:
            return Path(tempfile.mkdtemp(prefix=f"gov-cbm-{os.getuid()}-", dir=place))
        except OSError:
            continue
    raise OSError("no folder for the test session's daemon directories can be made")


def daemon_dir(root: Path) -> Path:
    """The tool's runtime directory for the repository at ``root`` (its ``CBM_RUNTIME_DIR``), outside the repository,
    as this process sees it (``daemon_base``)."""
    root = Path(root).resolve()
    return daemon_base(root=root) / hashlib.sha256(os.fsencode(root)).hexdigest()[:16]


def _daemon_dir(root: Path) -> Path:
    """``daemon_dir(root)``, made. Raises unless it and the folder above it are the user's own real directories."""
    made = daemon_dir(root)
    for place in (made.parent, made):  # /tmp is shared: a folder or a link put there by another user is not used
        place.mkdir(mode=0o700, exist_ok=True)
        if place.is_symlink() or place.stat().st_uid != os.getuid():
            raise RuntimeError(f"{place} is not a directory of this user: the code index tool is not run")
    return made


def _checked(root: Path) -> Path:
    """``root`` resolved. Raises unless it is the top level of a git repository and its home is under it."""
    root = Path(root).resolve()
    top = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                         env=git_env(root))
    if top.returncode != 0 or Path(top.stdout.removesuffix("\n")).resolve() != root:
        raise RuntimeError(f"{root} is not the top level of a git repository: no code index there")
    if home(root).resolve() != root / BASE_REL / "home":  # a link on the way would put the index somewhere else
        raise RuntimeError(f"{BASE_REL} of {root} is reached through a link: no code index there")
    return root


def _env(root: Path, tool: str) -> dict:
    """The environment of a start of the binary: the repository's home and the repository's daemon directory.

    Both are set here whatever the caller's environment holds; the rest of that environment is passed on, less the
    inherited ``GIT_*`` variables (``git_env``: the tool starts git in the project, AR-2).
    The tool's loopback UI is turned off in that home first (DEC-362).
    """
    root = _checked(root)
    new = not os.path.lexists(daemon_dir(root))
    env = {**git_env(root),"CBM_CACHE_DIR": str(home(root)), "CBM_RUNTIME_DIR": str(_daemon_dir(root))}
    # A daemon reads the setting of its home when it starts, and an index builds the home anew: set at every start.
    try:
        done = subprocess.run([TOOL, "config", "set", "ui_enabled", "false"], capture_output=True, text=True,
                              stdin=subprocess.DEVNULL, env=env)
    except OSError:  # the tool cannot be started (not on PATH): the folder made for it is not left (W2-56 S1)
        if new:
            try:
                os.rmdir(env["CBM_RUNTIME_DIR"])
            except OSError:
                pass
        raise
    if done.returncode != 0:
        raise RuntimeError(f"{TOOL} config set ui_enabled false failed: {tool} is not run")
    return env


def _tool(root: Path, tool: str, **args) -> dict:
    """Run one tool of the binary in the repository's home, with the repository's daemon directory (``_env``)."""
    done = subprocess.run([TOOL, "cli", "--quiet", "--json", tool, json.dumps(args)], capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, env=_env(root, tool))
    try:
        envelope = json.loads(done.stdout)
        if done.returncode == 0 and envelope["isError"] is False:
            return json.loads(envelope["content"][0]["text"])
    except (ValueError, LookupError, TypeError):
        pass
    raise RuntimeError(f"{TOOL} {tool} failed (exit code {done.returncode})")


class GraphTooLarge(RuntimeError):
    """A piece of the code graph (``what`` ``kind``: a link type inside the source ``file``, a source label, a list of
    paths) of ``count`` rows that no query of the tool can answer soundly: over its ``cap``, or (``refused``) a query
    of it the tool still refused over its cap. ``nodes`` and ``edges`` are the graph's counts as the tool gave them."""

    def __init__(self, what: str, kind: str, count: int, nodes: int, edges: int, refused: bool = False,
                 file: str | None = None) -> None:
        self.what, self.kind, self.count, self.nodes, self.edges = what, kind, count, nodes, edges
        self.cap, self.refused, self.file = CAP, refused, file
        why = "the tool refused its query over its cap all the same" if refused else "over the cap"
        where = f" of the source file {file}" if file is not None else ""
        super().__init__(f"{TOOL} refuses a query whose answer is over its cap of {CAP} rows: the code graph's {what} "
                         f"{kind}{where} has {count} rows ({why}), so it cannot be read in pieces under the cap (the "
                         f"graph: {nodes} nodes, {edges} edges)")


class GraphShort(RuntimeError):
    """A read of the code graph's ``what`` ``kind`` (inside the source ``file`` where one is named) that ended with
    ``read`` rows where the tool counted ``counted``; or (``said``) links missed or read twice over the pieces."""

    def __init__(self, what: str, kind: str, counted: int, read: int, file: str | None = None,
                 said: str | None = None) -> None:
        self.what, self.kind, self.counted, self.read, self.file = what, kind, counted, read, file
        where = f" of the source file {file}" if file is not None else ""
        super().__init__(said or f"the code graph's {what} {kind}{where}: {read} rows read where {TOOL} counted "
                         f"{counted}, so the graph is not whole (never a partial count)")


class _Session:
    """Several tools of the binary under one daemon: the binary as a server on its standard input and output (MCP).

    It is started at the first tool, with ``_env``, and ended when the block is left: its input is closed. An
    answer that does not come within ``_ANSWER_S`` ends it, and so does any failure: both are a refusal.
    """

    def __init__(self, root: Path) -> None:
        self.root, self.server, self.asked = root, None, 0

    def __enter__(self) -> _Session:
        return self

    def __exit__(self, *_error) -> None:
        self._end()

    def _end(self) -> int | None:
        """End the server, if one runs, and return its exit code."""
        if self.server is None:
            return None
        with self.server as server:  # closes its pipes
            try:
                server.stdin.close()  # the end of its input ends the server, and its daemon with it
            except OSError:
                pass
            try:
                return server.wait(_END_S)
            except subprocess.TimeoutExpired:
                server.kill()
                return server.wait()

    def _send(self, method: str, **params) -> None:
        self.server.stdin.write(json.dumps({"jsonrpc": "2.0", "method": method, "params": params} | (
            {} if method.startswith("notifications/") else {"id": self.asked})) + "\n")
        self.server.stdin.flush()

    def _ask(self, method: str, **params) -> dict:
        self.asked += 1
        self._send(method, **params)
        for line in self.server.stdout:
            message = json.loads(line) if line.startswith("{") else {}  # any other line is no answer
            if message.get("id") == self.asked:
                return message["result"]  # an error of the server has none
        raise LookupError("the server ended without an answer")

    def tool(self, tool: str, **args) -> dict:
        """What ``_tool`` returns, from the server of this session."""
        started = self.server is not None
        if not started:
            self.server = subprocess.Popen([TOOL], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                           stderr=subprocess.DEVNULL, text=True, env=_env(self.root, tool))
        limit = threading.Timer(_ANSWER_S, self.server.kill)
        limit.start()
        try:
            if not started:
                self._ask("initialize", protocolVersion="2024-11-05", capabilities={},
                          clientInfo={"name": "gov.codeintel", "version": "1"})
                self._send("notifications/initialized")
            envelope = self._ask("tools/call", name=tool, arguments=args)
            if envelope.get("isError", False) is False:  # MCP: an envelope without the field is no error
                return json.loads(envelope["content"][0]["text"])
            said = envelope["content"][0]["text"]  # what the tool said of its error, kept for the caller to name
            text = " ".join(said.split())[:300] if isinstance(said, str) else ""
        except (OSError, ValueError, LookupError, TypeError, AttributeError):
            text = ""
        finally:
            limit.cancel()
        failed = RuntimeError(f"{TOOL} {tool} failed (exit code {self._end()})" + (f": {text}" if text else ""))
        failed.text = text  # what the tool said of its error ("" for none), for a caller to name the cause
        raise failed


def index(root: Path) -> None:
    """Build the code index of the repository anew, from the files the pre-index filter returns and no other."""
    root = _checked(root)  # first of all: a refused root loses nothing
    base, staged = root / BASE_REL, root / BASE_REL / "files"
    try:  # the per-file record of the last read is kept: a file unchanged is not read again (S28)
        kept = (home(root) / RECORD).read_bytes()
    except OSError:
        kept = None
    if base.exists():  # first, so that a filter that cannot decide leaves no index behind
        shutil.rmtree(base)
    _graph.cache_clear()
    _counted.clear()
    _stats.clear()
    listed = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                            capture_output=True, text=True, check=True, env=git_env(root)).stdout
    allowed = indexable(root, [rel for rel in listed.split("\0") if rel])
    # The index stores paths: a path that holds a secret stays out (DEC-339). The pool is as wide as the CPUs this
    # process may use (its CPU set), never the machine's count (W2-20 S18): inside a slot, at most the slot's share.
    with ThreadPoolExecutor(max_workers=pool_size()) as pool:
        named = list(pool.map(lambda rel: path_holds_secret(root, rel), allowed))
    for rel in (rel for rel, secret in zip(allowed, named) if not secret):
        (staged / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / rel, staged / rel)
    home(root).mkdir(parents=True, exist_ok=True)
    staged.mkdir(exist_ok=True)
    _tool(root, "index_repository", repo_path=str(staged), name=PROJECT)
    if kept is not None:
        (home(root) / RECORD).write_bytes(kept)


def projects(root: Path) -> list[str]:
    """The project names the tool lists in this repository's home."""
    return [project["name"] for project in _tool(root, "list_projects", format="json")["projects"]]


def _rows(session: _Session, query: str) -> list[list]:
    rows, more = [], True
    while more:
        page = session.tool("query_graph", project=PROJECT, format="json", query=query, max_rows=_PAGE,
                            max_output_tokens=_BUDGET, offset=len(rows))
        rows += page["rows"]
        more = bool(page.get("has_more")) and bool(page["rows"])
    return rows


def _number(value, query: str) -> int:
    """A count the tool gave (it answers counts as text); anything else refuses."""
    text = str(value).strip()
    if not text.isdigit():
        raise RuntimeError(f"{TOOL} query_graph answered {query!r} with no count gov can read: {text[:80]!r}")
    return int(text)


def _one(session: _Session, query: str) -> int | None:
    """The one count ``query`` asks; None where the tool answers it with no single count."""
    rows = _rows(session, query)
    if len(rows) != 1 or not isinstance(rows[0], list) or len(rows[0]) != 1 or not str(rows[0][0]).strip().isdigit():
        return None
    return int(str(rows[0][0]).strip())


def _count(session: _Session, query: str) -> int:
    """The one count ``query`` asks (no row: 0); any other answer refuses (an error of the tool still raises)."""
    rows = _rows(session, query)
    if not rows:
        return 0
    if len(rows) != 1 or not isinstance(rows[0], list) or len(rows[0]) != 1:
        raise RuntimeError(f"{TOOL} query_graph answered {query!r} with no count gov can read: {str(rows)[:120]}")
    return _number(rows[0][0], query)


def _pairs(session: _Session, query: str) -> dict[str, int] | None:
    """The count of each link type or node label ``query`` groups, one row each; None where the answer holds rows of
    another shape (a tool, or a stand-in, that does not count: the graph is then read whole as before). A name that
    cannot stand in a match, or one named twice, refuses."""
    rows = _rows(session, query)
    if not all(isinstance(row, list) and len(row) == 2 and str(row[1]).strip().isdigit() for row in rows):
        return None
    found: dict[str, int] = {}
    for name, count in rows:
        if not (isinstance(name, str) and _NAME.fullmatch(name)) or name in found:
            raise RuntimeError(f"{TOOL} query_graph answered {query!r} with a row gov cannot read by name: "
                               f"{str([name, count])[:120]}")
        found[name] = int(str(count).strip())
    return found


def _quoted(path: str) -> str | None:
    """``path`` as a string the tool's ``WHERE`` compares by equality; None where no quoting is sure (a backslash or a
    line end in it, or both quotes)."""
    if "\\" in path or "\n" in path or "\r" in path:
        return None
    if '"' not in path:
        return f'"{path}"'
    return f"'{path}'" if "'" not in path else None


def counted(root: Path) -> tuple[int, int] | None:
    """The code graph's ``(nodes, edges)`` as the tool counted them when ``_graph(root)`` read it; None before."""
    return _counted.get(root)


def read_stats(root: Path) -> dict | None:
    """The last read of ``_graph(root)``: ``pieces_read`` (pieces asked of the tool), ``pieces_from_record`` (files
    unchanged since the last read, taken from the record) and ``read_seconds`` (its wall time); None before."""
    return _stats.get(root)


def record_path(root: Path) -> Path:
    """The per-file record of the last read that passed (S28): paths, digests and links, no file text."""
    return home(root) / RECORD


class _Reader:
    """One read of the graph's nodes and links in pieces (S28; the interface of run 8b, items 15-19 and 23)."""

    def __init__(self, session: _Session, root: Path, types: dict[str, int], labels: dict[str, int],
                 record: dict) -> None:
        self.session, self.root, self.record = session, root, record
        self.edges, self.nodes = sum(types.values()), sum(labels.values())
        self.labels = labels
        self.lists: dict[str, list] = {}  # each label's path list, read whole and checked against its count
        self.read = self.taken = 0

    def rows(self, query: str) -> list[list]:
        return _rows(self.session, query)

    def count(self, query: str) -> int:
        return _count(self.session, query)

    def checked(self, query: str, what: str, kind: str, count: int, file: str | None = None) -> list[list]:
        """The rows of ``query``, a piece of ``count`` rows (over the cap: refused by name, never asked); rows short of
        or over the count refuse (``GraphShort``)."""
        if count > CAP:
            raise GraphTooLarge(what, kind, count, self.nodes, self.edges, file=file)
        try:
            got = self.rows(query)
        except RuntimeError as exc:
            if "exceeded" in getattr(exc, "text", ""):  # the tool's own words for a query over its cap
                raise GraphTooLarge(what, kind, count, self.nodes, self.edges, refused=True, file=file) from exc
            raise
        if len(got) != count:
            raise GraphShort(what, kind, count, len(got), file=file)
        return got

    # ---- (ii) and item 23: the source paths, each list counted first and checked
    def path_lists(self) -> list[str]:
        for label in sorted(self.labels, key=lambda name: name == "File"):  # Folder's list before File's
            count = self.count(f"MATCH (n:{label}) RETURN count(n)")
            if count != self.labels[label]:
                raise GraphShort("list of the paths of the label", label, self.labels[label], count,
                                 said=f"the code graph's label {label}: {TOOL} counted {self.labels[label]} nodes by "
                                      f"label and {count} by its own count, so its path list cannot be checked")
            got = self.rows(f"MATCH (n:{label}) RETURN n.file_path") if count <= CAP else None
            if got is not None and len(got) == count:
                self.lists[label] = [row[0] if isinstance(row, list) and len(row) == 1 else row for row in got]
            elif label == "File":
                self.lists[label] = self.files_by_folder(count)
        return sorted({path for values in self.lists.values() for path in values if isinstance(path, str) and path})

    def bare(self, label: str) -> bool:
        """The label's every node has no string path (on redis Project and Branch, whose path is ``{}``)."""
        values = self.lists.get(label)
        return values is not None and not any(isinstance(path, str) and path for path in values)

    def files_by_folder(self, files: int) -> list[str]:
        """The File paths read per holder by equality on the holder's path (item 23), the pieces' counts summing to the
        File count; where no sound piece exists it refuses by name, never a partial list."""
        holders = _pairs(self.session, _HOLDERS)
        if holders is None:
            raise RuntimeError(f"{TOOL} query_graph answered {_HOLDERS!r} with no count by label gov can read")
        if sum(holders.values()) != files:
            raise GraphShort("list of", "File paths", files, sum(holders.values()),
                             said=f"the code graph's list of File paths: the holders of files count "
                                  f"{sum(holders.values())} where {TOOL} counted {files} File nodes")
        found: list[str] = []
        for holder, held in sorted(holders.items()):
            values = self.lists.get(holder)
            if values is None:  # the holder's own list is cut or over the cap: no sound piece
                count = self.labels.get(holder, 0)
                if count > CAP:
                    raise GraphTooLarge("list of the paths of the label", holder, count, self.nodes, self.edges)
                raise GraphShort("list of the paths of the label", holder, count, 0,
                                 said=f"the code graph's list of the paths of the label {holder} (which holds "
                                      f"{held} files) was cut short by {TOOL}, so the File list cannot be read in "
                                      "sound pieces")
            got: list = []
            if self.bare(holder):
                match = f"MATCH (b:{holder})-[r:CONTAINS_FILE]->(n:File)"
                got += self.checked(f"{match} RETURN n.file_path", "list of the File paths held by", holder,
                                    self.count(f"{match} RETURN count(n)"))
            elif all(isinstance(path, str) and path for path in values):
                for path in sorted(set(values)):
                    quoted = _quoted(path)
                    if quoted is None:
                        raise GraphShort("list of", "File paths", held, len(got),
                                         said=f"the code graph's {holder} path {path!r} cannot be asked by equality")
                    match = f"MATCH (f:{holder})-[r:CONTAINS_FILE]->(n:File) WHERE f.file_path = {quoted}"
                    got += self.checked(f"{match} RETURN n.file_path", f"list of the File paths of the {holder}",
                                        path, self.count(f"{match} RETURN count(n)"))
            else:
                raise GraphShort("list of", "File paths", held, 0,
                                 said=f"the code graph's label {holder} holds files and mixes string and other "
                                      "paths, so the File list cannot be read in sound pieces")
            if len(got) != held:
                raise GraphShort(f"list of the File paths held by the label", holder, held, len(got))
            found += [row[0] if isinstance(row, list) and len(row) == 1 else row for row in got]
        if len(found) != files:
            raise GraphShort("list of", "File paths", files, len(found))
        return found

    # ---- (iii) and 16: one piece a source path; inside it, by link type where it is cut or over the cap
    def path_piece(self, path: str) -> list[list]:
        quoted = _quoted(path)
        if quoted is None:
            raise GraphShort("links of", "a path", 0, 0, file=path,
                             said=f"the code graph's source path {path!r} cannot be asked by equality")
        where = f"WHERE a.file_path = {quoted}"
        count = self.count(f"MATCH (a)-[r]->(b) {where} RETURN count(r)")
        self.read += 1
        if count == 0:
            return []
        if count <= CAP:
            got = self.rows(f"MATCH (a)-[r]->(b) {where} RETURN {_LINK}")
            if len(got) == count and _distinct(got):
                return got
        types = _pairs(self.session, f"MATCH (a)-[r]->(b) {where} RETURN type(r), count(r)")
        if types is None or sum(types.values()) != count:
            raise GraphShort("links by type", "of the file", count, sum((types or {}).values()), file=path)
        rows: list[list] = []
        for kind, number in sorted(types.items()):
            match = f"MATCH (a)-[r:{kind}]->(b) {where}"
            own = self.count(f"{match} RETURN count(r)")
            if own != number:
                raise GraphShort("link type", kind, number, own, file=path)
            got = self.checked(f"{match} RETURN {_LINK}", "link type", kind, own, file=path)
            if not _distinct(got):
                raise GraphShort("link type", kind, own, len({str(row[0]) for row in got}), file=path)
            rows += got
        return rows

    # ---- (iv): one piece a label whose nodes have no string path
    def label_piece(self, label: str) -> list[list]:
        match = f"MATCH (a:{label})-[r]->(b)"
        count = self.count(f"{match} RETURN count(r)")
        self.read += 1
        got = self.checked(f"{match} RETURN {_LINK}", "links out of the source label", label, count) if count else []
        if not _distinct(got):
            raise GraphShort("links out of the source label", label, count, len({str(row[0]) for row in got}))
        return got

    def links(self, paths: list[str]) -> tuple[list[list], dict]:
        """Every link, each once: the pieces' counts sum to the tool's total and their ids are that many distinct."""
        pieces: dict[str, list[list]] = {}
        fresh: dict[str, dict] = {}
        kept = self.record.get("pieces", {}) if isinstance(self.record.get("pieces"), dict) else {}
        for path in paths:
            digest = _digest(self.root, path)
            old = kept.get(path)
            if digest is not None and isinstance(old, dict) and old.get("digest") == digest \
                    and isinstance(old.get("links"), list):
                pieces[path] = old["links"]
                self.taken += 1
            else:
                pieces[path] = self.path_piece(path)
            if digest is not None:
                fresh[path] = {"digest": digest, "links": pieces[path]}
        for label in sorted(self.labels):
            if self.bare(label):
                pieces[f"label {label}"] = self.label_piece(label)
        owner: dict[str, str] = {}
        doubled: set[str] = set()
        for key, rows in pieces.items():
            for row in rows:
                ident = str(row[0])
                if ident in owner:
                    doubled |= {owner[ident], key}
                owner[ident] = key
        summed = sum(len(rows) for rows in pieces.values())
        if summed != self.edges or len(owner) != self.edges:
            gaps = sorted(label for label in self.labels if label not in self.lists or (
                not self.bare(label) and any(not (isinstance(path, str) and path) for path in self.lists[label])))
            raise GraphShort("links of", "all pieces", self.edges, summed, said=(
                f"the code graph's links: {TOOL} counted {self.edges}, the pieces by source path and label hold "
                f"{summed} with {len(owner)} distinct ids, so links are missed or read twice (never a partial read)"
                + (f"; read twice in: {', '.join(sorted(doubled)[:20])}" if doubled else "")
                + (f"; labels whose paths leave a gap: {', '.join(gaps)}" if gaps else "")))
        return [row for rows in pieces.values() for row in rows], fresh

    # ---- the nodes: by label, each checked; a label cut or over the cap by its paths, by equality
    def node_rows(self) -> list[list]:
        found: list[list] = []
        for label, count in sorted(self.labels.items()):
            got = self.rows(_LABELLED.format(label)) if count <= CAP else None
            if got is None or len(got) != count:
                got = self.nodes_by_path(label, count)
            found += got
        return found

    def nodes_by_path(self, label: str, count: int) -> list[list]:
        values = self.lists.get(label)
        if values is None or any(not (isinstance(path, str) and path) for path in values):
            if count > CAP:
                raise GraphTooLarge("node label", label, count, self.nodes, self.edges)
            raise GraphShort("node label", label, count, 0, said=(
                f"the code graph's node label {label}: its {count} nodes were cut short by {TOOL} and cannot be read "
                "by path (its path list is cut or holds paths that are no string)"))
        found: list[list] = []
        for path in sorted(set(values)):
            quoted = _quoted(path)
            if quoted is None:
                raise GraphShort("node label", label, count, len(found), file=path)
            found += self.checked(f"MATCH (n:{label}) WHERE n.file_path = {quoted} RETURN n.qualified_name, n.name, "
                                  "n.label, n.file_path", "node label", label, values.count(path), file=path)
        return found


def _distinct(rows: list[list]) -> bool:
    return all(isinstance(row, list) and len(row) == 4 for row in rows) and len({str(row[0]) for row in rows}) == len(rows)


def _digest(root: Path, path: str) -> str | None:
    """The content digest of the file (or folder) the tool indexed at ``path``; None where the path is neither (its
    links are read every time)."""
    if path.startswith("/") or ".." in Path(path).parts:
        return None
    place = root / BASE_REL / "files" / path
    try:
        if place.is_file() and not place.is_symlink():
            return "file:" + hashlib.sha256(place.read_bytes()).hexdigest()
        if place.is_dir() and not place.is_symlink():
            names = sorted(child.name + ("/" if child.is_dir() else "") for child in place.iterdir())
            return "folder:" + hashlib.sha256("\0".join(names).encode()).hexdigest()
    except OSError:
        return None
    return None


def _load_record(root: Path) -> dict:
    try:
        record = json.loads(record_path(root).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return record if isinstance(record, dict) and record.get("version") == 1 else {}


def _save_record(root: Path, fresh: dict) -> None:
    """Written only after a read that passed; a write that fails leaves the last good record."""
    place = record_path(root)
    staged = place.with_name(f"{RECORD}.{os.getpid()}")
    try:
        place.parent.mkdir(parents=True, exist_ok=True)
        staged.write_text(json.dumps({"version": 1, "pieces": fresh}), encoding="utf-8")
        os.replace(staged, place)
    except OSError:
        try:
            staged.unlink()
        except OSError:
            pass


@functools.cache
def _graph(root: Path) -> tuple[dict, dict]:
    """The symbols of the index by qualified name, and for each the symbols that use it with the kind of use.

    The links are read in pieces by their source node's path (S28, ``_Reader``): the tool's total first, then the
    paths, then one piece a path (by link type inside a piece cut or over the cap), every piece's rows checked against
    its count and the pieces' ids against the total. A file unchanged since the last read that passed is taken from the
    record. Every query, pages included, is asked in one session of the tool: one start of its daemon (DEC-561).
    """
    import time

    _counted.pop(root, None)
    _stats.pop(root, None)
    started = time.monotonic()
    with _Session(root) as session:
        types = _pairs(session, _TYPES)
        if types is None:  # a tool, or a stand-in, that does not count: read whole as before, unchecked
            found = _rows(session, _NODES)
            links = [[None, *row] for row in _rows(session, _EDGES)]
            fresh = reader = None
        else:
            labels = _pairs(session, _LABELS)
            if labels is None:
                raise RuntimeError(f"{TOOL} query_graph answered {_LABELS!r} with no count by label gov can read")
            record = _load_record(root)
            reader = _Reader(session, root, types, labels, record)
            paths = reader.path_lists()
            try:
                links, fresh = reader.links(paths)
            except GraphShort:
                if not reader.taken:
                    raise
                lists, asked = reader.lists, reader.read  # the record is stale: every piece is read again
                reader = _Reader(session, root, types, labels, {})
                reader.lists, reader.read = lists, asked
                links, fresh = reader.links(paths)
            found = reader.node_rows()
    if reader is not None:
        _save_record(root, fresh)
        _counted[root] = (reader.nodes, reader.edges)
        _stats[root] = {"pieces_read": reader.read, "pieces_from_record": reader.taken,
                        "read_seconds": round(time.monotonic() - started, 3)}
    nodes = {key: {"path": path, "name": name, "label": label} for key, name, label, path in found
             if label not in _PLACES and isinstance(path, str) and path
             and (root / BASE_REL / "files" / path).is_file()}
    users = defaultdict(list)
    for _ident, source, kind, target in links:
        if kind not in _NO_USE and source in nodes and target in nodes and (source, kind) not in users[target]:
            users[target].append((source, kind))
    return nodes, users


def _named(root: Path, name: str) -> tuple[dict, dict, list[str]]:
    nodes, users = _graph(Path(root).resolve())
    return nodes, users, [key for key, node in nodes.items() if node["name"] == name]


def _entries(nodes: dict, keys) -> list[dict]:
    return [dict(nodes[key]) for key in dict.fromkeys(keys)]


def definitions(root: Path, name: str) -> list[dict]:
    """Where the symbol ``name`` is defined."""
    nodes, _, named = _named(root, name)
    return _entries(nodes, named)


def references(root: Path, name: str) -> list[dict]:
    """The places that use the symbol ``name``: the enclosing symbol and its file."""
    nodes, users, named = _named(root, name)
    return _entries(nodes, [source for key in named for source, _ in users[key]])


def callers(root: Path, name: str) -> list[dict]:
    """The functions that call ``name``."""
    nodes, users, named = _named(root, name)
    return _entries(nodes, [source for key in named for source, kind in users[key] if kind == "CALLS"])


def callees(root: Path, name: str) -> list[dict]:
    """The functions that ``name`` calls."""
    nodes, users, named = _named(root, name)
    return _entries(nodes, [callee for key in named for callee, by in users.items() if (key, "CALLS") in by])


def impact(root: Path, name: str) -> list[dict]:
    """What a change to ``name`` reaches: its callers and theirs, nearest first."""
    nodes, users, named = _named(root, name)
    reached, front = [], named
    while front:
        front = [source for key in front for source, kind in users[key] if kind == "CALLS" and source not in reached]
        front = list(dict.fromkeys(front))
        reached += front
    return _entries(nodes, reached)


def dead_code(root: Path) -> list[dict]:
    """The functions nothing in the repository refers to."""
    nodes, users = _graph(Path(root).resolve())
    return _entries(nodes, [key for key, node in nodes.items() if node["label"] in _FUNCTIONS and not users[key]])
