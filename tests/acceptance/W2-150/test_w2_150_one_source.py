"""W2-150 S6: one source each for ``_Glob``, ``load_yaml_unique`` and the git runner (DAEO-ijf5; DEC-1109 (2)).

The review found three helpers left as copies (R1, R2): ``_Glob`` (``gov.guard.protected`` and ``gov.util.parts``, the guard retired since: EMERGENCY-2 6.1),
``load_yaml_unique`` (``gov.guard.heldout`` and ``gov.util.parts``) and the git runner (``gov.close.repo.git`` and the
fingerprint's runner in ``gov.store.loader``). A fix to one copy alone would leave the other on the old code.

The static scan reads ``src/gov`` as data only (``ast``, never imported): it lists every class and function defined
at module level, including inside module-level ``if``/``try``/``with`` blocks, but not inside a class or a function
body. ``_Glob`` and ``load_yaml_unique`` are found by name. The git runner is found by name in ``gov.close.repo``
(``git``) and, everywhere, by its body: a module-level function that holds the ``"--no-replace-objects"`` option and
calls ``git_env`` (today ``gov.close.repo.git`` and ``gov.store.loader._commit_git`` only; README N-6). The identity
checks run in a fresh subprocess on this tree's own ``src``.

Rewrite-Reason: EMERGENCY-2 6.1 (the guard / the sandbox retired), DAEO-gr7t. The cases that read ``gov.guard.protected`` and
``gov.guard.heldout`` (one definition each, the old names, their behaviour) are deleted with the guard.
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


# -- one definition each (static) ---------------------------------------------


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



