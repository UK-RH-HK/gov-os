"""Planted faults for W2-67 batch 1b (throwaway; never in the tracked tree).

Imported by the launcher a case writes (``w2_67b_plant`` wraps ``w1_07_support.write_launcher``), in that ``gov``
process only, before the command runs. ``apply(names)`` replaces one function of the code under test per fault.
"""

from __future__ import annotations

import copy
import functools
import importlib


def _wrap(module_name, function_name, make):
    module = importlib.import_module(module_name)
    original = getattr(module, function_name)
    setattr(module, function_name, functools.wraps(original)(make(original)))


def _doctor(function_name, make):
    _wrap("gov.doctor.command", function_name, make)


def _section(function_name, change):
    """Wrap a doctor check: its result passes through ``change`` (a copy)."""
    def make(original):
        def planted(*args, **kwargs):
            result = copy.deepcopy(original(*args, **kwargs))
            return change(result) if isinstance(result, dict) else result
        return planted
    _doctor(function_name, make)


def _p27_1(result):        # a moved-path reference never reported (CAP-06.d)
    result["moved_references"] = []
    result["status"] = "pass"
    return result


def _p27_4(result):        # never an unclassified path (CAP-06.d)
    result["unclassified"] = []
    result["unclassified_count"] = 0
    result["status"] = "pass"
    return result


FAULTS = {
    "P27-1": lambda: _section("_check_path_compliance", _p27_1),
    "P27-4": lambda: _section("_check_path_map", _p27_4),
    # the path matcher matches no pattern: every tracked path unclassified (CAP-06.a; the reverse of P27-8)
    "P67B-1": lambda: _doctor("_match_pattern", lambda original: lambda path, pattern: False),
    # src/gov/cli/ (the live CLI) left out of the stale-path check as if it were the old cli/ tree (DEC-456 point 2)
    "P67B-2": lambda: _doctor("_excluded_from_stale_check",
                              lambda original: lambda path: original(path) or path.startswith("src/gov/cli/")),
    # every document under docs/ left out of the stale-path check, not docs/SOURCES.md alone (DEC-456 point 1)
    "P67B-3": lambda: _doctor("_excluded_from_stale_check",
                              lambda original: lambda path: original(path) or path.startswith("docs/")),
    # DEC-456 point 3 too broad: a file that names the new path is never reported, a standalone old path included
    "P67B-4": lambda: _doctor("_has_standalone_old_path", lambda original: lambda content, old, new: False),
    # an unrelated section fails, so doctor is unhealthy whatever the section under test says (I4: 'ok is false on
    # every machine for the tools section alone'); combined with another fault
    "P67B-5": lambda: _section("_check_tools", lambda result: {**result, "status": "fail"}),
    # group 2: doctor's sections
    "P27-11": lambda: _section("_check_tools", _p27_11),
    "P67B-6": lambda: _section("_check_tools", _p67b_6),
    "P67B-7": lambda: _section("_check_framework_lock", lambda result: {"status": "pass", "match": "MATCH"}),
    "P67B-8": lambda: _section("_check_hooks", lambda result: {"status": "pass", "config_present": True,
                                                               "binary_installed": True}),
    "P67B-9": lambda: _section("_check_index_freshness", lambda result: {"status": "pass", "index_status": "fresh",
                                                                         "stale": []}),
    "P67B-10": lambda: _section("_check_canaries", _p67b_10),
    "P67B-11": lambda: _section("_check_canaries", _p67b_11),
    "P27-9": lambda: _section("_check_isolation", _p27_9),
    "P67B-12": lambda: _section("_check_isolation", lambda result: {"status": "pass", "isolated": True}),
    # group 3: Claude Code drift (DEC-210, DEC-214): one rule of the claude_code section removed
    "P27-6": lambda: _without_issues(lambda detail: "newer than registry" in detail and detail.startswith("CLI")),
    "P67B-13": lambda: _without_issues(lambda detail: "differs from extension" in detail),
    "P67B-14": lambda: _without_issues(lambda detail: "extension binary sha256 mismatch" in detail),
    "P67B-15": lambda: _without_issues(lambda detail: detail.startswith("CLI version") and "below minimum" in detail),
    "P67B-16": lambda: _without_issues(lambda detail: detail.startswith("extension version")
                                       and "below minimum" in detail),
    "P67B-17": lambda: _without_issues(lambda detail: "has sha256 mismatch" in detail),
}


def _rebuild(make):
    _wrap("gov.rebuild.command", "run", make)


def _rebuild_after(change):
    """``gov rebuild`` runs, then ``change(root, result)``."""
    def make(original):
        def planted(root, args, config):
            result = original(root, args, config)
            return change(root, result) if isinstance(result, dict) else result
        return planted
    _rebuild(make)


def _p27_7(root, result):           # a reversed digest (CAP-20.a)
    result["digest"] = str(result.get("digest"))[::-1]
    return result


def _p67b_18(root, result):         # rebuild writes outside .gov-runtime
    (root / "rebuild-wrote-here.txt").write_text("planted\n", encoding="utf-8")
    return result


def _p67b_20(original):             # rebuild fails
    def planted(root, args, config):
        raise RuntimeError("planted: rebuild fails")
    return planted


def _p67b_21(original):             # rebuild reports stores it never builds
    def planted(root, args, config):
        return {"digest": "0" * 64, "stores": {"lexical": {"status": "recreated"},
                                              "semantic": {"status": "not_recreated", "reason": "planted"},
                                              "codeintel": {"status": "not_recreated", "reason": "planted"}}}
    return planted


def _p67b_22(original):             # rebuild needs the state an earlier run left, which is not in git
    def planted(root, args, config):
        if not (root / ".gov-runtime" / "store.db").is_file():
            raise RuntimeError("planted: no earlier store")
        return original(root, args, config)
    return planted


def _p67b_23(original):             # rebuild needs a tool other than git and gitleaks on PATH
    def planted(root, args, config):
        import shutil
        if shutil.which("codebase-memory-mcp") is None:
            raise RuntimeError("planted: codebase-memory-mcp not on PATH")
        return original(root, args, config)
    return planted


def _p67b_24(root, result):         # a store not rebuilt reported recreated
    for entry in (result.get("stores") or {}).values():
        if isinstance(entry, dict) and entry.get("status") == "not_recreated":
            entry["status"] = "recreated"
            entry.pop("reason", None)
    return result


def _p67b_25(root, result):         # a constant reason for every store not rebuilt
    for entry in (result.get("stores") or {}).values():
        if isinstance(entry, dict) and entry.get("status") == "not_recreated":
            entry["reason"] = "requires ollama and qwen3-embedding model"
    return result


def _p67b_26(original):             # rebuild keeps every lexical row an earlier store held
    def planted(root, args, config):
        import sqlite3
        store = root / ".gov-runtime" / "store.db"
        rows = []
        if store.is_file():
            connection = sqlite3.connect(store)
            try:
                rows = connection.execute("SELECT * FROM lexical_file").fetchall()
            except sqlite3.Error:
                rows = []
            connection.close()
        result = original(root, args, config)
        if rows:
            connection = sqlite3.connect(store)
            marks = ", ".join("?" * len(rows[0]))
            connection.executemany(f"INSERT OR IGNORE INTO lexical_file VALUES ({marks})", rows)
            connection.commit()
            connection.close()
        return result
    return planted


FAULTS.update({
    "P27-7": lambda: _rebuild_after(_p27_7),
    "P67B-18": lambda: _rebuild_after(_p67b_18),
    "P67B-20": lambda: _rebuild(_p67b_20),
    "P67B-21": lambda: _rebuild(_p67b_21),
    "P67B-22": lambda: _rebuild(_p67b_22),
    "P67B-23": lambda: _rebuild(_p67b_23),
    "P67B-24": lambda: _rebuild_after(_p67b_24),
    "P67B-25": lambda: _rebuild_after(_p67b_25),
    "P67B-26": lambda: _rebuild(_p67b_26),
})


def _p67b_27():                     # the recovery check fails open: it exits 0 whatever it found
    import sys
    original = sys.exit
    sys.exit = lambda code=0: original(0)


def _p67b_28():                     # the recovery check always finds a mismatch (a new digest each call)
    import os
    import gov.store
    gov.store.digest = lambda root: os.urandom(32).hex()


def _p67b_29():                     # the recovery check exits non-zero without saying unmeasured
    import builtins
    original = builtins.print

    def planted(*args, **kwargs):
        return original(*(str(arg).replace("unmeasured", "store.db missing") for arg in args), **kwargs)
    builtins.print = planted


FAULTS.update({"P67B-27": _p67b_27, "P67B-28": _p67b_28, "P67B-29": _p67b_29})


def _p67b_31(root, result):         # rebuild writes in the home it is given
    import os
    from pathlib import Path
    (Path(os.environ["HOME"]) / ".gov-planted").write_text("planted\n", encoding="utf-8")
    return result


FAULTS["P67B-31"] = lambda: _rebuild_after(_p67b_31)


def _p67b_32(result):               # a no-binary tool whose file is found passes without its hash compared
    if "not found" not in str(result.get("reason") or ""):
        result.update({"ok": True, "sha256_match": True})
        result.pop("reason", None)
    return result


FAULTS["P67B-32"] = lambda: _section("_check_no_binary_tool", _p67b_32)


def _without_issues(dropped):
    """The claude_code section without the issues of one rule; drift and status follow the issues left."""
    def change(result):
        issues = [issue for issue in result.get("issues", []) if not dropped(str(issue.get("detail", "")))]
        result["issues"] = issues
        result["drift"] = any(issue.get("type") == "drift" for issue in issues)
        result["status"] = ("fail" if any(issue.get("type") == "failure" for issue in issues)
                            else "drift" if result["drift"] else "pass")
        return result
    _section("_check_claude_code", change)


def _p27_11(result):       # a tool doctor cannot find reported with its pinned version only (nothing says why)
    result["tools"] = [entry if entry.get("ok") is True else
                       {key: entry[key] for key in ("name", "pinned_version", "ok") if key in entry}
                       for entry in result.get("tools", [])]
    return result


def _p67b_6(result):       # the found version is the pin: doctor reads the registry, not the tool
    for entry in result.get("tools", []):
        if "pinned_version" in entry:
            entry["found_version"] = entry["pinned_version"]
    return result


def _p67b_10(result):      # every canary passes, measured or not
    for index in (result.get("indices") or {}).values():
        index.update({"passed": True, "status": "AVAILABLE", "misses": []})
    result["status"] = "pass"
    return result


def _p67b_11(result):      # the lexical canary never passes
    lexical = (result.get("indices") or {}).get("lexical")
    if isinstance(lexical, dict):
        lexical.update({"passed": False, "misses": lexical.get("misses") or ["planted miss"]})
    return result


def _p27_9(result):        # isolation reported whatever the runtime folder's parent (DEC-425)
    if "git_root" in result:
        result.update({"status": "pass", "isolated": True})
    return result


def apply(names):
    for name in names:
        FAULTS[name]()
