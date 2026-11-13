"""W2-150 S6: one source each for ``_Glob``, ``load_yaml_unique`` and the git runner (DAEO-ijf5; DEC-1109 (2)).

The review found three helpers left as copies (R1, R2): ``_Glob`` (``gov.guard.protected`` and ``gov.util.parts``),
``load_yaml_unique`` (``gov.guard.heldout`` and ``gov.util.parts``) and the git runner (``gov.close.repo.git`` and the
fingerprint's runner in ``gov.store.loader``). A fix to one copy alone would leave the other on the old code.

The static scan reads ``src/gov`` as data only (``ast``, never imported): it lists every class and function defined
at module level, including inside module-level ``if``/``try``/``with`` blocks, but not inside a class or a function
body. ``_Glob`` and ``load_yaml_unique`` are found by name. The git runner is found by name in ``gov.close.repo``
(``git``) and, everywhere, by its body: a module-level function that holds the ``"--no-replace-objects"`` option and
calls ``git_env`` (today ``gov.close.repo.git`` and ``gov.store.loader._commit_git`` only; README N-6). The identity
checks run in a fresh subprocess on this tree's own ``src``.
"""

from __future__ import annotations

import ast
import hashlib
import textwrap

from w2_150_run import run_json
from w2_150_walk import SRC, Walk, in_package, is_gate

NEW_HOMES = ("gov.util", "gov.store")


def _module_level_defs(tree: ast.Module):
    """Every class and function a module defines at its own level (through ``if``/``try``/``with`` blocks)."""
    todo = list(tree.body)
    while todo:
        node = todo.pop(0)
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            yield node
        elif isinstance(node, (ast.If, ast.While, ast.For, ast.With)):
            todo.extend(node.body + getattr(node, "orelse", []))
        elif isinstance(node, ast.Try) or type(node).__name__ == "TryStar":
            todo.extend(node.body + node.orelse + node.finalbody)
            for handler in node.handlers:
                todo.extend(handler.body)


def _is_git_runner(node) -> bool:
    """A function whose body holds the ``--no-replace-objects`` option and calls ``git_env``."""
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    option = calls_env = False
    for each in ast.walk(node):
        if isinstance(each, ast.Constant) and each.value == "--no-replace-objects":
            option = True
        elif isinstance(each, ast.Call):
            func = each.func
            name = func.id if isinstance(func, ast.Name) else func.attr if isinstance(func, ast.Attribute) else None
            calls_env = calls_env or name == "git_env"
    return option and calls_env


def _scan():
    """``[(module, name, line, is_git_runner)]`` for every module-level class and function of ``src/gov``."""
    walk = Walk()
    found = []
    for module, path in sorted(walk.modules.items()):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in _module_level_defs(tree):
            found.append((module, node.name, node.lineno, _is_git_runner(node)))
    return walk, found


def _where(walk, hits) -> str:
    return ", ".join(f"{walk.modules[m].relative_to(SRC.parent).as_posix()}:{line} ({m}.{n})"
                     for m, n, line, _ in hits)


def _defined_once_in_util(name: str, original: str):
    walk, found = _scan()
    hits = [f for f in found if f[1] == name]
    assert len(hits) == 1, f"`{name}` is defined {len(hits)} times in src/gov, not once: {_where(walk, hits)}"
    module = hits[0][0]
    assert module != original and any(in_package(module, p) for p in NEW_HOMES), (
        f"`{name}`'s one definition is in {module}, not in its new home under {NEW_HOMES}")


# -- one definition each (static) ---------------------------------------------

def test_s6_glob_defined_once_not_in_guard_protected():
    _defined_once_in_util("_Glob", "gov.guard.protected")


def test_s6_load_yaml_unique_defined_once_not_in_guard_heldout():
    _defined_once_in_util("load_yaml_unique", "gov.guard.heldout")


def test_s6_git_runner_defined_once_not_in_close_repo():
    walk, found = _scan()
    own = [f for f in found if f[0] == "gov.close.repo" and f[1] == "git"]
    runners = [f for f in found if f[3]]
    problems = []
    if own:
        problems.append(f"gov.close.repo defines its own `git`: {_where(walk, own)}")
    if len(runners) > 1:
        problems.append(f"{len(runners)} git runners (a function holding `--no-replace-objects` and calling "
                        f"`git_env`) are defined in src/gov, not one: {_where(walk, runners)}")
    for module, name, line, _ in runners:
        if not any(in_package(module, p) for p in NEW_HOMES):
            problems.append(f"the git runner {module}.{name} (line {line}) is not in a new home under {NEW_HOMES}")
    assert not problems, "\n".join(problems)


# -- the originals import (a fresh process) -----------------------------------

IDENTITY = textwrap.dedent("""
    import json
    import gov.guard.protected, gov.guard.heldout, gov.close.repo, gov.store.loader, gov.util.parts
    git = gov.close.repo.git
    in_store = sorted(k for k, v in vars(gov.store.loader).items() if v is git)
    print(json.dumps({
        "glob": gov.guard.protected._Glob is gov.util.parts._Glob,
        "glob_home": gov.guard.protected._Glob.__module__,
        "yaml": gov.guard.heldout.load_yaml_unique is gov.util.parts.load_yaml_unique,
        "yaml_home": gov.guard.heldout.load_yaml_unique.__module__,
        "git_home": git.__module__,
        "git_in_store": in_store,
    }))
""")


def test_s6_old_names_are_the_new_homes_objects():
    got = run_json(IDENTITY)
    problems = []
    if not got["glob"]:
        problems.append(f"gov.guard.protected._Glob is not gov.util.parts._Glob (it comes from {got['glob_home']})")
    if not got["yaml"]:
        problems.append("gov.guard.heldout.load_yaml_unique is not gov.util.parts.load_yaml_unique "
                        f"(it comes from {got['yaml_home']})")
    if not any(in_package(got["git_home"], p) for p in NEW_HOMES):
        problems.append(f"gov.close.repo.git comes from {got['git_home']}, not from a new home under {NEW_HOMES}")
    if not got["git_in_store"]:
        problems.append("gov.store.loader holds no name bound to gov.close.repo.git: the fingerprint runs its own "
                        "git runner")
    assert not problems, "\n".join(problems)


# -- guards (green today) -------------------------------------------------------

def test_s6_guard_new_homes_reach_no_gate():
    """Each helper's definitions outside the gates, and their static import closure: no gate reached."""
    walk, found = _scan()
    homes = {"_Glob": set(), "load_yaml_unique": set(), "git runner": set()}
    for module, name, _, runner in found:
        if is_gate(module):
            continue
        if name in homes:
            homes[name].add(module)
        if runner:
            homes["git runner"].add(module)
    assert all(homes.values()), f"a helper has no definition outside the gates: {homes}"
    problems = []
    for helper, modules in sorted(homes.items()):
        reached = walk.closure(sorted(modules))
        hits = walk.report(reached, is_gate)
        if hits:
            problems.append(f"{helper}'s home {sorted(modules)} reaches a gate:\n{hits}")
    assert not problems, "\n".join(problems)


OLD_NAMES = textwrap.dedent("""
    import inspect, json, os, sys, tempfile
    from pathlib import Path
    from gov.guard.protected import _Glob
    from gov.guard.heldout import load_yaml_unique
    from gov.close.repo import git
    from gov.cli.errors import GovError
    globs = [_Glob(p).match(s) for p, s in [("src/**/x.py", "src/a/b/x.py"), ("src/*.py", "src/a/b.py"),
                                            ("{a,b}/c", "b/c"), ("a?c", "a/c"), ("**/z", "z")]]
    loaded = load_yaml_unique("a: 1\\nb: [2]\\n")
    try:
        load_yaml_unique("a: 1\\na: 2\\n")
        twice = None
    except Exception as e:
        twice = type(e).__name__
    params = list(inspect.signature(git).parameters)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        git(root, "init", "-q")
        inside = git(root, "rev-parse", "--is-inside-work-tree")
        blob = git(root, "hash-object", "--stdin", given="x\\n").strip()
        missing = git(root, "cat-file", "-e", "0" * 40, ok=(0, 1, 128), code=True)
        try:
            git(root, "cat-file", "-e", "0" * 40)
            failure = None
        except GovError as e:
            failure = e.code
    print(json.dumps({"globs": globs, "loaded": loaded, "twice": twice, "params": params, "inside": inside,
                      "blob": blob, "missing": missing, "failure": failure}))
""")


def test_s6_guard_old_names_importable_and_behave_as_today():
    """S3 for the three: importable from the old modules, ``git`` keeps its whole call (``ok``, ``code``,
    ``given``, ``pinned``), not the store copy's narrower one."""
    got = run_json(OLD_NAMES)
    assert got["globs"] == [True, False, True, False, True]
    assert got["loaded"] == {"a": 1, "b": [2]}
    assert got["twice"] == "ConstructorError"
    assert got["params"] == ["root", "args", "ok", "code", "given", "pinned"]
    assert got["inside"] == "true\n"
    assert got["blob"] == hashlib.sha1(b"blob 2\0x\n").hexdigest()
    assert isinstance(got["missing"], int) and got["missing"] != 0
    assert got["failure"] == "GIT_FAILURE"
