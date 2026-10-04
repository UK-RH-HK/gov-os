"""The code index: a wrapper of codebase-memory-mcp 0.11.0 (W1-16; DEC-076, CAP-12, CAP-03.e).

Each repository has its own home for the tool, under its ``.gov-runtime/``. The tool
never reads the repository: ``index(root)`` copies the files ``gov.secrets.indexable``
returns into a folder next to that home and the tool indexes the copy, so a file the
filter leaves out is not in the index at all. Neither is a file whose path holds a secret
by the same rules: the index stores paths. Every index is built anew; if the filter
cannot decide, there is no index. The answers are read from the graph the tool built.
The root must be the top level of a git repository whose ``.gov-runtime/`` is no link:
any other root is refused before anything is written or deleted.
"""

from __future__ import annotations

import functools
import json
import os
import shutil
import subprocess
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from gov.secrets import _holds_secret, _rules, indexable

TOOL = "codebase-memory-mcp"
BASE_REL = ".gov-runtime/codeintel"
PROJECT = "code"
_PAGE, _BUDGET = 50000, 100_000_000  # rows and output tokens of one answer of the tool; more is paged
# Nodes that say where something stands, and edges that are no use of a symbol by another.
_PLACES = {"Project", "Branch", "Folder", "File", "Module"}
_NO_USE = {"DEFINES", "DEFINES_METHOD", "CONTAINS_FILE", "CONTAINS_FOLDER", "HAS_BRANCH", "SEMANTICALLY_RELATED"}
_FUNCTIONS = {"Function", "Method"}

__all__ = ["callers", "dead_code", "definitions", "home", "impact", "index", "projects", "references"]


def home(root: Path) -> Path:
    """The tool's home for the repository at ``root`` (its ``CBM_CACHE_DIR``)."""
    return Path(root).resolve() / BASE_REL / "home"


def _checked(root: Path) -> Path:
    """``root`` resolved. Raises unless it is the top level of a git repository and its home is under it."""
    root = Path(root).resolve()
    top = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if top.returncode != 0 or Path(top.stdout.removesuffix("\n")).resolve() != root:
        raise RuntimeError(f"{root} is not the top level of a git repository: no code index there")
    if home(root).resolve() != root / BASE_REL / "home":  # a link on the way would put the index somewhere else
        raise RuntimeError(f"{BASE_REL} of {root} is reached through a link: no code index there")
    return root


def _tool(root: Path, tool: str, **args) -> dict:
    """Run one tool of the binary in the repository's home. The rest of the caller's environment is passed on."""
    root = _checked(root)
    done = subprocess.run([TOOL, "cli", "--quiet", "--json", tool, json.dumps(args)], capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, env={**os.environ, "CBM_CACHE_DIR": str(home(root))})
    try:
        envelope = json.loads(done.stdout)
        if done.returncode == 0 and envelope["isError"] is False:
            return json.loads(envelope["content"][0]["text"])
    except (ValueError, LookupError, TypeError):
        pass
    raise RuntimeError(f"{TOOL} {tool} failed (exit code {done.returncode})")


def index(root: Path) -> None:
    """Build the code index of the repository anew, from the files the pre-index filter returns and no other."""
    root = _checked(root)  # first of all: a refused root loses nothing
    base, staged = root / BASE_REL, root / BASE_REL / "files"
    if base.exists():  # first, so that a filter that cannot decide leaves no index behind
        shutil.rmtree(base)
    _graph.cache_clear()
    listed = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                            capture_output=True, text=True, check=True).stdout
    allowed, rules = indexable(root, [rel for rel in listed.split("\0") if rel]), _rules(root)

    def secret_name(rel: str) -> bool:  # the path and each of its names, judged as content is (DEC-287, DEC-298)
        return _holds_secret(rules, os.fsencode("\n".join([rel, *Path(rel).parts])))

    with ThreadPoolExecutor() as pool:
        named = list(pool.map(secret_name, allowed))
    for rel in (rel for rel, secret in zip(allowed, named) if not secret):
        (staged / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / rel, staged / rel)
    home(root).mkdir(parents=True, exist_ok=True)
    staged.mkdir(exist_ok=True)
    _tool(root, "index_repository", repo_path=str(staged), name=PROJECT)


def projects(root: Path) -> list[str]:
    """The project names the tool lists in this repository's home."""
    return [project["name"] for project in _tool(root, "list_projects", format="json")["projects"]]


def _rows(root: Path, query: str) -> list[list]:
    rows, more = [], True
    while more:
        page = _tool(root, "query_graph", project=PROJECT, format="json", query=query, max_rows=_PAGE,
                     max_output_tokens=_BUDGET, offset=len(rows))
        rows += page["rows"]
        more = bool(page.get("has_more")) and bool(page["rows"])
    return rows


@functools.cache
def _graph(root: Path) -> tuple[dict, dict]:
    """The symbols of the index by qualified name, and for each the symbols that use it with the kind of use."""
    nodes = {key: {"path": path, "name": name, "label": label}
             for key, name, label, path in _rows(root, "MATCH (n) RETURN n.qualified_name, n.name, n.label, n.file_path")
             if label not in _PLACES and (root / BASE_REL / "files" / path).is_file()}
    users = defaultdict(list)
    for source, kind, target in _rows(root, "MATCH (a)-[r]->(b) RETURN a.qualified_name, type(r), b.qualified_name"):
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
