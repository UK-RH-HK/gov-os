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
    """Where the daemon directories of this process stand: the test session's own folder (``CODEINTEL_DAEMON_BASE``, or
    for a repository ``root`` under a test process's temp base, the folder its mark names: ``marked_base``), else the
    launched session's temp folder (``launch_folder``), else ``DAEMON_BASE``."""
    env = os.environ if env is None else env
    given = env.get(BASE_ENV) or ""
    if os.path.isabs(given):
        return Path(os.path.normpath(given))
    marked = marked_base(root) if root is not None else None
    if marked is not None:
        return marked
    launched = launch_folder(env)
    return launched / LAUNCH_SUB if launched is not None else DAEMON_BASE


def make_session_base(env=None) -> Path:
    """A new folder for one test session's daemon directories (W2-56 S1), short enough for the tool's socket: in the
    launched session's temp folder, else under ``/tmp``, else under the temp folder. The caller removes it."""
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
        except (OSError, ValueError, LookupError, TypeError, AttributeError):
            pass
        finally:
            limit.cancel()
        raise RuntimeError(f"{TOOL} {tool} failed (exit code {self._end()})")


def index(root: Path) -> None:
    """Build the code index of the repository anew, from the files the pre-index filter returns and no other."""
    root = _checked(root)  # first of all: a refused root loses nothing
    base, staged = root / BASE_REL, root / BASE_REL / "files"
    if base.exists():  # first, so that a filter that cannot decide leaves no index behind
        shutil.rmtree(base)
    _graph.cache_clear()
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


@functools.cache
def _graph(root: Path) -> tuple[dict, dict]:
    """The symbols of the index by qualified name, and for each the symbols that use it with the kind of use.

    Both queries, pages included, are asked in one session of the tool: one start of its daemon (DEC-561).
    """
    with _Session(root) as session:
        found = _rows(session, "MATCH (n) RETURN n.qualified_name, n.name, n.label, n.file_path")
        edges = _rows(session, "MATCH (a)-[r]->(b) RETURN a.qualified_name, type(r), b.qualified_name")
    nodes = {key: {"path": path, "name": name, "label": label} for key, name, label, path in found
             if label not in _PLACES and (root / BASE_REL / "files" / path).is_file()}
    users = defaultdict(list)
    for source, kind, target in edges:
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
