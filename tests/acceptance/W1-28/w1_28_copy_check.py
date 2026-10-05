"""The check behind KPI success 4 (DEC-385): no test fixture copies ``governance/project/held-out.yaml``.

Two routes, both without ever opening the committed file:

- **By running.** ``copiers`` finds, in the sources under ``tests/acceptance/``,
  every module-level function that takes the repository root as a parameter
  (a parameter whose default is ``REPO_ROOT``) and copies files. ``run_copier``
  calls one with a **synthetic** source repository in place of the root: a
  temporary git repository this module builds, whose
  ``governance/project/held-out.yaml`` holds made-up text. What the function
  produced is then searched for a file of that path.
- **By reading.** ``whole_tree_copiers`` finds every function that copies the
  whole tree of the repository: a listing of all of it (``git ls-files`` with no
  path limit, ``os.walk``, ``rglob``, ...) followed by a copy, or a whole-tree
  route (``copytree``, ``git clone``, ``git archive``, ``git worktree``,
  ``cp -r``, ``rsync``, ``tar``) with the repository root as its source. Such a
  function must be one ``copiers`` finds, so that the first route runs it.

Only the sources of the test suites are parsed (``ast``); nothing here names,
opens, hashes or compares the committed held-out file. The README says what
the two routes cannot catch.
"""

from __future__ import annotations

import ast
import importlib.util
import inspect
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ACCEPTANCE = REPO_ROOT / "tests" / "acceptance"
HELD_OUT_REL = "governance/project/held-out.yaml"   # the path, never the content
ROOT_NAME = "REPO_ROOT"                             # every suite's name for the repository root
MODULE_LEVEL = "<module>"

# Made-up content: the key of DEC-218 and a path that exists nowhere.
SYNTHETIC_HELD_OUT = "held_out_paths:\n- /w1-28-synthetic/not-a-held-out-path\n"
MARKER = "W1_28_SYNTHETIC_SOURCE = True\n"
SYNTHETIC_FILES = {
    "README.md": "# W1-28 synthetic source repository\n",
    ".gitignore": ".gov-runtime/\n__pycache__/\n",
    ".claude/settings.json": "{}\n",
    "pyproject.toml": "[project]\nname = \"w1-28-synthetic\"\nversion = \"0\"\n",
    "src/gov/w1_28_marker.py": MARKER,
    "template/governance/kernel/hooks/w1_28_marker.py": MARKER,
    "governance/project/w1_28_marker.yaml": "marker: true\n",
}

_UNWRAPPED = {"str", "Path", "fspath", "realpath", "abspath", "resolve"}
_COPY_CALLS = {"copy2", "copyfile", "copytree", "symlink_to", "hardlink_to", "write_bytes"}
_MODULE_COPY_CALLS = {("shutil", "copy"), ("shutil", "move"), ("os", "link"), ("os", "symlink")}
_LISTERS = {"walk", "rglob", "glob", "iterdir", "scandir", "listdir"}
_ARGV_ROUTES = {"clone", "archive", "worktree", "checkout-index", "bundle"}
_SHELL_ROUTE = re.compile(r"\b(cp\s+-\w*[rRa]\w*|rsync|git\s+(?:archive|clone|worktree)|tar\s+-?\w*c\w*)\b")


@dataclass(frozen=True)
class Function:
    """One function of a test source file, or the file's top-level code (``MODULE_LEVEL``)."""
    path: Path
    name: str
    root_parameters: tuple   # the parameters whose default is the repository root
    top_level: bool          # a module-level ``def``: something a check can import and call
    copies: bool
    lists_whole_tree: bool
    whole_tree_route: bool

    @property
    def label(self):
        return f"{self.path.parent.name}/{self.path.name}::{self.name}"

    @property
    def runnable(self):
        """It takes the repository root as a parameter and copies: the check can run it on a synthetic root."""
        return self.top_level and bool(self.root_parameters) and (self.copies or self.whole_tree_route)

    @property
    def copies_whole_tree(self):
        return (self.lists_whole_tree and self.copies) or self.whole_tree_route


# --------------------------------------------------------------------------
# Reading the sources
# --------------------------------------------------------------------------

def _callee(call):
    func = call.func
    return func.id if isinstance(func, ast.Name) else func.attr if isinstance(func, ast.Attribute) else None


def _is_root(node, names):
    """``REPO_ROOT``, ``<module>.REPO_ROOT`` or a parameter that defaults to it, also inside ``str()`` or ``Path()``."""
    while isinstance(node, ast.Call) and _callee(node) in _UNWRAPPED:
        if node.args:
            node = node.args[0]
        elif isinstance(node.func, ast.Attribute):
            node = node.func.value   # ``root.resolve()``
        else:
            return False
    if isinstance(node, ast.Name):
        return node.id in names
    return isinstance(node, ast.Attribute) and node.attr == ROOT_NAME


def _whole_roots(node, names):
    """True when ``node`` holds the repository root itself, not a path below it (``REPO_ROOT / "docs"``)."""
    if _is_root(node, names):
        return True
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        return False
    if isinstance(node, ast.Call) and _callee(node) == "joinpath":
        return False
    return any(_whole_roots(child, names) for child in ast.iter_child_nodes(node))


def _strings(node):
    return [item.value for item in ast.walk(node) if isinstance(item, ast.Constant) and isinstance(item.value, str)]


def _unlimited_listing(sequence):
    """An argument list with ``ls-files`` and no path limit: no pathspec constant, no ``*PATHSPECS``."""
    items = list(sequence)
    for index, item in enumerate(items):
        if isinstance(item, ast.Constant) and item.value == "ls-files":
            rest = items[index + 1:]
            if any(isinstance(later, ast.Starred) for later in rest):
                return False
            return all(not isinstance(later, ast.Constant) or not isinstance(later.value, str)
                       or later.value.startswith("-") for later in rest)
    return False


def _analyse(path, name, body, root_parameters, top_level):
    names = {ROOT_NAME, *root_parameters}
    nodes = [node for statement in body for node in ast.walk(statement)]
    mentions_root = any(_is_root(node, names) for node in nodes
                        if isinstance(node, (ast.Name, ast.Attribute)))
    copies = lists = route = False
    for node in nodes:
        if isinstance(node, (ast.List, ast.Tuple)) and _unlimited_listing(node.elts) and mentions_root:
            lists = True
        if not isinstance(node, ast.Call):
            continue
        callee = _callee(node)
        owner = node.func.value.id if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) \
            else None
        if callee in _COPY_CALLS or (owner, callee) in _MODULE_COPY_CALLS:
            copies = True
        if _unlimited_listing(node.args) and mentions_root:
            lists = True
        whole = any(_whole_roots(argument, names) for argument in (*node.args, *(k.value for k in node.keywords)))
        receiver = isinstance(node.func, ast.Attribute) and _whole_roots(node.func.value, names)
        if callee in _LISTERS and (whole or receiver):
            lists = True
        if callee == "copytree" and node.args and _whole_roots(node.args[0], names):
            route = True
        if whole and any(text in _ARGV_ROUTES or _SHELL_ROUTE.search(text) for text in _strings(node)):
            route = True
    return Function(path, name, tuple(root_parameters), top_level, copies, lists, route)


def _root_parameters(function):
    arguments = function.args
    positional = [*arguments.posonlyargs, *arguments.args]
    pairs = list(zip(positional[len(positional) - len(arguments.defaults):], arguments.defaults))
    pairs += [(argument, default) for argument, default in zip(arguments.kwonlyargs, arguments.kw_defaults)
              if default is not None]
    return [argument.arg for argument, default in pairs if _is_root(default, {ROOT_NAME})]


def functions(tests_root=ACCEPTANCE, skip=()):
    """Every function, and each file's top-level code, of the Python sources under ``tests_root``."""
    found = []
    for path in sorted(Path(tests_root).rglob("*.py")):
        if "__pycache__" in path.parts or path in skip:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        top = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
        rest = [node for node in tree.body
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
        found.append(_analyse(path, MODULE_LEVEL, rest, (), False))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                found.append(_analyse(path, node.name, node.body, _root_parameters(node), node in top))
    return found


def copiers(tests_root=ACCEPTANCE, skip=()):
    """The functions the check can run: they take the repository root as a parameter and copy files."""
    return [function for function in functions(tests_root, skip) if function.runnable]


def whole_tree_copiers(tests_root=ACCEPTANCE, skip=()):
    """The functions that copy the whole tree of the repository, by any route this module reads."""
    return [function for function in functions(tests_root, skip) if function.copies_whole_tree]


# --------------------------------------------------------------------------
# Running a copier on a synthetic source repository
# --------------------------------------------------------------------------

def _git(directory, *args):
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(directory), "LC_ALL": "C",
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}
    subprocess.run(["git", "-C", str(directory), "-c", "user.name=W1-28 tests",
                    "-c", "user.email=w1-28@example.invalid", "-c", "commit.gpgsign=false", *args],
                   check=True, capture_output=True, text=True, env=env)


def make_source(directory, tracked=True):
    """A synthetic source repository with a made-up held-out file, tracked or untracked and not ignored."""
    directory = Path(directory)
    assert REPO_ROOT not in (directory, *directory.parents), f"{directory} is inside this repository"
    for rel, text in SYNTHETIC_FILES.items():
        (directory / rel).parent.mkdir(parents=True, exist_ok=True)
        (directory / rel).write_text(text, encoding="utf-8")
    held_out = directory / HELD_OUT_REL
    _git(directory, "init", "-q", "-b", "main")
    if tracked:
        held_out.write_text(SYNTHETIC_HELD_OUT, encoding="utf-8")
    _git(directory, "add", "-A")
    _git(directory, "commit", "-q", "-m", "synthetic source")
    if not tracked:
        held_out.write_text(SYNTHETIC_HELD_OUT, encoding="utf-8")
    return directory


def load(function):
    """The function object, from its file, loaded under a name of its own with its suite's folder importable."""
    folder = str(function.path.parent)
    if folder not in sys.path:
        sys.path.insert(0, folder)
    name = f"w1_28_checked_{function.path.parent.name.replace('-', '_')}_{function.path.stem}"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, function.path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        try:
            spec.loader.exec_module(module)
        except BaseException:
            del sys.modules[name]
            raise
    return getattr(sys.modules[name], function.name)


def run_copier(function, source, destination):
    """Call the copier with ``source`` as the repository root; the folder it filled."""
    callable_ = load(function)
    required = [name for name, parameter in inspect.signature(callable_).parameters.items()
                if parameter.default is inspect.Parameter.empty
                and parameter.kind in (parameter.POSITIONAL_ONLY, parameter.POSITIONAL_OR_KEYWORD)]
    assert len(required) == 1, (
        f"{function.label} takes {required} without a default: this check calls a copier as "
        f"`copier(<destination>, {function.root_parameters[0]}=<synthetic root>)`"
    )
    callable_(destination, **{name: source for name in function.root_parameters})
    return Path(destination)


def held_out_copies(directory):
    """Every path under ``directory`` that is the held-out file's path in some tree; nothing is opened."""
    wanted = tuple(HELD_OUT_REL.split("/"))
    found = []
    for folder, names, files in os.walk(directory):
        for name in (*names, *files):
            parts = Path(folder, name).relative_to(directory).parts
            if parts[-len(wanted):] == wanted:
                found.append(str(Path(folder, name)))
    return sorted(found)


def arrived(directory):
    """The synthetic marker files that reached ``directory``: the copier did read the synthetic root."""
    return sorted(rel for rel, text in SYNTHETIC_FILES.items()
                  if text in (MARKER, "marker: true\n") and (Path(directory) / rel).is_file()
                  and (Path(directory) / rel).read_text(encoding="utf-8") == text)
