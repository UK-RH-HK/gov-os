"""Scratch only (W2-111 test designer, run 2): records every p95 the 15 latency cases compute (CPU, then wall, per
round) into $TD_FIGURES, and the CPU time of every reference-hook call of a case (the cases' own reference, read
through their helper) into $TD_FIGURES.ref; and, when TD_PLANT_S is set in the pytest process's environment, runs the
installed PreToolUse hook behind a busy loop of that many seconds of its own CPU time (then the real hook, so the
decision is unchanged). The judged figure of a round is its CPU p95 less the median of that round's reference calls.
Nothing of this is in a committed test."""
import json, os, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIG = os.environ.get("TD_FIGURES")
PLANT = os.environ.get("TD_PLANT_S")


class _SubprocessProxy:
    def __init__(self, real):
        self._real = real

    def __getattr__(self, name):
        return getattr(self._real, name)

    def _plant(self, args):
        argv = list(args) if not isinstance(args, str) else None
        if argv and any("pretooluse" in str(part) for part in argv):
            return [sys.executable, str(HERE / "plant_launch.py"), PLANT] + argv
        return args

    def run(self, args, *a, **kw):
        return self._real.run(self._plant(args), *a, **kw)

    def Popen(self, args, *a, **kw):
        return self._real.Popen(self._plant(args), *a, **kw)


def _record_p95(original):
    def p95(samples):
        value = original(samples)
        if FIG:
            with open(FIG, "a") as handle:
                handle.write(json.dumps({"test": os.environ.get("PYTEST_CURRENT_TEST", "").split(" ")[0],
                                         "p95_ms": round(value * 1000, 2), "n": len(samples)}) + "\n")
        return value
    return p95


def _record_ref(original):
    def reference():
        value = original()
        if FIG:
            with open(FIG + ".ref", "a") as handle:
                handle.write(json.dumps({"test": os.environ.get("PYTEST_CURRENT_TEST", "").split(" ")[0],
                                         "ref_ms": round(value * 1000, 2)}) + "\n")
        return value
    return reference


def pytest_collection_finish(session):
    for name in ("w1_02_support", "w1_05_support"):
        module = sys.modules.get(name)
        if module is None:
            continue
        module.p95 = _record_p95(module.p95)
        if PLANT:
            module.subprocess = _SubprocessProxy(subprocess)
    for name, module in list(sys.modules.items()):
        if name.endswith(("test_w1_02_guard_hook", "test_w1_05_live_hooks", "test_w2_57_designer_read_p95")):
            for attr in ("reference_cpu_seconds", "_reference_cpu_seconds"):
                if hasattr(module, attr):
                    setattr(module, attr, _record_ref(getattr(module, attr)))
