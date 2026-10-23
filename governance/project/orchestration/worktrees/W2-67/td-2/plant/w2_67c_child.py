"""W2-67 batch 2 (throwaway, never in the tracked tree): planted faults in one ``gov`` process.

``apply(names)`` is called by the launcher header ``w2_67c_plant`` writes; each name is one fault. ``src/`` is
never written: a fault replaces one behaviour in memory, in that ``gov`` process, or in a declared check's own
process through ``w2_67c_run_patched.py`` (one exact text change of the check's module, compiled in memory, as
I2 §2.7 made its PF-n in a clone).
"""

from __future__ import annotations

import functools
import importlib
import inspect
import json
import sys
from pathlib import Path

PLANT_DIR = Path(__file__).resolve().parent
RUN_PATCHED = PLANT_DIR / "w2_67c_run_patched.py"

# A declared check's module, one exact text change, in the check's own process (I2's PF7, PF8, PF17, PF24).
CHILD_TEXT = {
    # the schema check no longer reads ticket files (I2 PF7)
    "PF7": ("gov.check.schema", 'RECORD_PATHS = (".tickets", "docs")', 'RECORD_PATHS = ("docs",)'),
    # the schema check reads no record (I2 PF17)
    "PF17": ("gov.check.schema", 'RECORD_PATHS = (".tickets", "docs")', "RECORD_PATHS = ()"),
    # the graph check reads no record (I2 PF8)
    "PF8": ("gov.check.graph", 'RECORD_PATHS = (".tickets", "docs")', "RECORD_PATHS = ()"),
    # the schema check says a type is unmeasured but names neither the type nor its schema file (I4 F7)
    "P67C-1": ("gov.check.schema",
               '"path": rel, "type": record_type,\n'
               '                                     "message": f"{rel}: unmeasured, the schema {schema_file} '
               'cannot be read"})',
               '"path": rel,\n'
               '                                     "message": f"{rel}: unmeasured, a schema cannot be read"})'),
    # the schema check reads a hand-kept list of directories: tickets and docs/adr only (DEC-436, F-2)
    "P67C-3": ("gov.check.schema", 'RECORD_PATHS = (".tickets", "docs")', 'RECORD_PATHS = (".tickets", "docs/adr")'),
    # the schema check skips a record of a type it does not know, silently (DEC-436)
    "P67C-4": ("gov.check.schema", 'findings.append({"code": "SCHEMA_UNKNOWN_TYPE", "path": rel,',
               '(lambda finding: None)({"code": "SCHEMA_UNKNOWN_TYPE", "path": rel,'),
    # the commands check measures nothing (I2 PF24)
    "PF24": ("gov.check.commands", "def check(root: Path) -> list[dict]:\n",
             "def check(root: Path) -> list[dict]:\n    return []\n"),
}

# A declared check whose command measures nothing: it exits 0 before it reads anything (I2 PF3's form).
MUTE_MODULE = {
    "MUTE-schema": "gov.check.schema",
    "MUTE-graph": "gov.check.graph",
    "MUTE-authority": "gov.check.authority",
    "MUTE-mutation": "gov.check.mutation",
    "MUTE-claims": "gov.check.claims",
    "PF3": "gov.check.pathmap",
}

# One exact text change of one function of the gov process (I2 PF21, PF22, PF23).
FUNC_TEXT = {
    # gov check fails whatever its checks say (I2 PF21)
    "PF21": ("gov.check.command", "run", "    if has_hard_block_red:\n", "    if True:\n"),
    # the runner's readiness check ignores check_all's answer (I2 PF22)
    "PF22": ("gov.check.runner", "_check_readiness",
             'if isinstance(result, dict) and not result.get("closed", True):', "if False:"),
    # the runner's readiness check swallows an error of check_all (I2 PF23)
    "PF23": ("gov.check.runner", "_check_readiness",
             'findings.append({"code": code, "message": msg})', "pass"),
}

_BUILT_IN = ("_check_openspec", "_check_skill_version", "_check_readiness")


def _quiet(entry):
    """A check result that measured nothing: GREEN, no finding."""
    if isinstance(entry, dict):
        entry = dict(entry, status="GREEN", findings=[])
    return entry


def _wrap(module, name, after):
    original = getattr(module, name)

    @functools.wraps(original)
    def wrapper(*args, **kwargs):
        return after(original(*args, **kwargs), *args, **kwargs)

    setattr(module, name, wrapper)


def _wrap_declared(runner, change):
    """``change(decl) -> decl``: the declaration the runner runs, in place of the declared one."""
    original = runner._run_declared_check

    @functools.wraps(original)
    def wrapper(decl, root, commit):
        return original(change(dict(decl)), root, commit)

    runner._run_declared_check = wrapper


def _retext(module_name, function_name, old, new):
    module = importlib.import_module(module_name)
    function = getattr(module, function_name)
    source = inspect.getsource(function)
    if source.count(old) != 1:
        raise RuntimeError(f"W2-67 plant: {old!r} is not once in {module_name}.{function_name}")
    namespace = {}
    exec(compile(source.replace(old, new), inspect.getsourcefile(function), "exec"), module.__dict__, namespace)
    setattr(module, function_name, namespace[function_name])


def apply(names):
    runner = importlib.import_module("gov.check.runner")
    for name in names:
        if name in CHILD_TEXT:
            module = CHILD_TEXT[name][0]
            _wrap_declared(runner, lambda decl, module=module, name=name: dict(
                decl, command=f"python3 {RUN_PATCHED} {name}") if decl["command"].strip() == f"python3 -m {module}"
                else decl)
        elif name in MUTE_MODULE:
            module = MUTE_MODULE[name]
            _wrap_declared(runner, lambda decl, module=module: dict(decl, command="true")
                           if decl["command"].strip() == f"python3 -m {module}" else decl)
        elif name in FUNC_TEXT:
            _retext(*FUNC_TEXT[name])
        elif name == "P67C-2":
            # the runner counts a check that answers "unmeasured" as GREEN with no finding (DEC-425)
            def unmeasured_green(entry, *a, **k):
                findings = entry.get("findings") if isinstance(entry, dict) else None
                if findings and all("unmeasured" in json.dumps(finding).lower() for finding in findings):
                    return _quiet(entry)
                return entry
            _wrap(runner, "_run_declared_check", unmeasured_green)
        elif name == "MUTE-skill-version":
            # the skill version check measures nothing
            _wrap(runner, "_check_skill_version", lambda entry, *a, **k: _quiet(entry))
        elif name == "MUTE-policy":
            # the policy coverage check reports no policy key
            _wrap(runner, "_check_policy_enforcement", lambda entries, *a, **k: [_quiet(e) for e in entries])
        elif name == "MUTE-readiness":
            _wrap(runner, "_check_readiness", lambda entry, *a, **k: _quiet(entry))
        elif name == "MUTE-openspec":
            _wrap(runner, "_check_openspec", lambda entry, *a, **k: _quiet(entry))
        elif name == "PF20":
            # every check reports GREEN with no finding (I2 PF20, on a base that has no index-freshness check)
            _wrap(runner, "_run_declared_check", lambda entry, *a, **k: _quiet(entry))
            for built_in in _BUILT_IN:
                _wrap(runner, built_in, lambda entry, *a, **k: _quiet(entry))
            _wrap(runner, "_check_policy_enforcement", lambda entries, *a, **k: [_quiet(e) for e in entries])
        else:
            raise RuntimeError(f"W2-67 plant: no fault named {name!r}")
