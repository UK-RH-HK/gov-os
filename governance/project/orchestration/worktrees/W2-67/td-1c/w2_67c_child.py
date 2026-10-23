"""Planted faults for W2-67 batch 1c (throwaway; never in the tracked tree).

Imported by the launcher a case writes (``w2_67c_plant`` wraps ``w1_07_support.write_launcher``), in that ``gov``
process only, before the command runs. ``apply(names)`` replaces one function of the code under test per fault.
"""

from __future__ import annotations

import functools
import importlib


def _wrap(module_name, function_name, make):
    module = importlib.import_module(module_name)
    original = getattr(module, function_name)
    setattr(module, function_name, functools.wraps(original)(make(original)))


def _codeintel_after(change):
    """``gov rebuild`` runs as it is, then its code index entry passes through ``change``."""
    def make(original):
        def planted(root, args, config):
            result = original(root, args, config)
            stores = result.get("stores") if isinstance(result, dict) else None
            if isinstance(stores, dict) and isinstance(stores.get("codeintel"), dict):
                stores["codeintel"] = change(dict(stores["codeintel"]))
            return result
        return planted
    _wrap("gov.rebuild.command", "run", make)


def _p67c_1(entry):         # a constant reason for a code index not rebuilt, whatever the tool answered
    if entry.get("status") == "not_recreated":
        entry["reason"] = "codebase-memory-mcp did not answer"
    return entry


def _p67c_2(entry):         # the outcome does not follow the measurement: always "absent", whatever the tool did
    return {"status": "not_recreated", "reason": "[Errno 2] No such file or directory: 'codebase-memory-mcp'"}


def _p67c_3():              # round 4's fault: the tool is never asked, and the reason is the old constant sentence
    import gov.codeintel

    def index(root):
        raise RuntimeError("no code index module exists")
    gov.codeintel.index = index


def _p67c_4(entry):         # the tool's answer dropped from the reason: every digit (the exit code) removed
    if entry.get("status") == "not_recreated":
        entry["reason"] = "".join(ch for ch in str(entry.get("reason", "")) if not ch.isdigit())
    return entry


FAULTS = {
    "P67C-1": lambda: _codeintel_after(_p67c_1),
    "P67C-2": lambda: _codeintel_after(_p67c_2),
    "P67C-3": _p67c_3,
    "P67C-4": lambda: _codeintel_after(_p67c_4),
}


def apply(names):
    for name in names:
        FAULTS[name]()
