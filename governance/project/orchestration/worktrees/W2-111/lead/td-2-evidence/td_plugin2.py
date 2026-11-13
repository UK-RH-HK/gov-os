"""Scratch only (W2-111 run 2, measuring): one JSON line per timed call of the 15 latency cases: the call's CPU and wall,
and, just before it, two reference jobs timed beside it (a stub hook: python start + read the event + answer; a bare
python start). The references' CPU is taken out of the cases' own CPU readings, so the cases judge what they judged
in round 1. Optional TD_PLANT_S plants a busy-loop hook (own process_time) as round 1's plant did.
Nothing of this is in a committed test."""
import json, os, resource, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIG = os.environ.get("TD_FIGURES2")
PLANT = os.environ.get("TD_PLANT_S")
STUB = ("import sys,json\nd=json.load(sys.stdin)\n"
        "print(json.dumps({'hookSpecificOutput':{'hookEventName':'PreToolUse','permissionDecision':'allow'}}))")
EXCL = [0.0]
_real_rusage = resource.getrusage
_counter = {}


def _cpu_now():
    u = _real_rusage(resource.RUSAGE_CHILDREN)
    return u.ru_utime + u.ru_stime


def _ref(argv, stdin=None):
    c0 = _cpu_now()
    subprocess.run(argv, input=stdin, capture_output=True, text=True)
    d = _cpu_now() - c0
    EXCL[0] += d
    return d


def _refs():
    return {"stub": _ref([sys.executable, "-c", STUB], "{}"), "start": _ref([sys.executable, "-c", "pass"])}


def _record(refs, cpu, wall):
    if not FIG:
        return
    test = os.environ.get("PYTEST_CURRENT_TEST", "").split(" ")[0]
    k = _counter[test] = _counter.get(test, 0) + 1
    with open(FIG, "a") as h:
        h.write(json.dumps({"test": test, "k": k, "cpu": round(cpu * 1000, 3), "wall": round(wall * 1000, 3),
                            "stub": round(refs["stub"] * 1000, 3), "start": round(refs["start"] * 1000, 3),
                            "la": open("/proc/loadavg").read().split()[0]}) + "\n")


class _SubprocessProxy:
    def __init__(self, real): self._real = real
    def __getattr__(self, name): return getattr(self._real, name)
    def _plant(self, args):
        argv = list(args) if not isinstance(args, str) else None
        if argv and any("pretooluse" in str(p) for p in argv):
            return [sys.executable, str(HERE / "plant_launch.py"), PLANT] + argv
        return args
    def run(self, args, *a, **kw): return self._real.run(self._plant(args), *a, **kw)
    def Popen(self, args, *a, **kw): return self._real.Popen(self._plant(args), *a, **kw)


def pytest_collection_finish(session):
    s02 = sys.modules.get("w1_02_support")
    s05 = sys.modules.get("w1_05_support")
    if s02 is not None:
        real_raw = s02.run_hook_raw
        def raw(*a, **kw):
            refs = _refs()
            r = real_raw(*a, **kw)
            _record(refs, r.cpu_seconds or 0.0, r.seconds)
            return r
        s02.run_hook_raw = raw
        real_cpu = s02.children_cpu_seconds
        s02.children_cpu_seconds = lambda: real_cpu() - EXCL[0]
        if PLANT: s02.subprocess = _SubprocessProxy(subprocess)
    if s05 is not None:
        real_t = s05.timed_pre_tool_use
        box = {}
        def timed(*a, **kw):
            refs = _refs()
            c0 = _cpu_now() - EXCL[0]
            res, seconds = real_t(*a, **kw)
            _record(refs, _cpu_now() - EXCL[0] - c0, seconds)
            return res, seconds
        s05.timed_pre_tool_use = timed
        if PLANT: s05.subprocess = _SubprocessProxy(subprocess)
    # the W1-05 case reads children CPU through its own helper
    for name, mod in list(sys.modules.items()):
        if name.endswith("test_w1_05_live_hooks") and hasattr(mod, "_children_cpu_seconds"):
            real_c = mod._children_cpu_seconds
            mod._children_cpu_seconds = lambda real_c=real_c: real_c() - EXCL[0]

    if PLANT and os.environ.get("TD_ROUNDS"):
        for name, mod in list(sys.modules.items()):
            if name.endswith(("test_w1_02_guard_hook", "test_w1_05_live_hooks", "test_w2_57_designer_read_p95")):
                for attr in ("LATENCY_ROUNDS", "ROUNDS"):
                    if hasattr(mod, attr): setattr(mod, attr, int(os.environ["TD_ROUNDS"]))
                if os.environ.get("TD_SAMPLES"):
                    for attr in ("LATENCY_SAMPLES", "SAMPLES"):
                        if hasattr(mod, attr): setattr(mod, attr, int(os.environ["TD_SAMPLES"]))
