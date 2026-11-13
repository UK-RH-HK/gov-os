"""Scratch only (W2-111 test designer): records every p95 the 15 latency cases compute (cpu, then wall, per round),
and, when TD_PLANT_S is set in the pytest process's environment, runs the installed PreToolUse hook behind a
busy loop of that many seconds of its own CPU time (then the real hook, so the decision is unchanged).
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


def _record(module_name, original):
    def p95(samples):
        value = original(samples)
        if FIG:
            with open(FIG, "a") as handle:
                handle.write(json.dumps({"test": os.environ.get("PYTEST_CURRENT_TEST", "").split(" ")[0],
                                         "p95_ms": round(value * 1000, 2), "n": len(samples)}) + "\n")
        return value
    return p95


def pytest_collection_finish(session):
    for name in ("w1_02_support", "w1_05_support"):
        module = sys.modules.get(name)
        if module is None:
            continue
        module.p95 = _record(name, module.p95)
        if PLANT:
            module.subprocess = _SubprocessProxy(subprocess)
