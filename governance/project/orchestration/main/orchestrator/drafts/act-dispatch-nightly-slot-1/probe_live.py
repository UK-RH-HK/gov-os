"""The dispatcher's outside-slot list over the real process table, for one pid: `probe_live.py <dispatcher.py> <pid>`
with DISPATCH_ORCH / DISPATCH_STATE / DISPATCH_SLOT_GLOB / DISPATCH_NIGHTLY_RUNS set to the planted bed. Prints
`outside` or `in-slot` for that pid (limit 0 s, so its age does not matter) and exits 0; exits 2 when the pid is not a
heavy step the dispatcher sees at all."""
import importlib.util
import sys

path, pid = sys.argv[1], int(sys.argv[2])
spec = importlib.util.spec_from_file_location("dispatcher_probe", path)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
facts = d.proc_facts()
mine = [f for f in facts if f["pid"] == pid]
if not mine:
    print(f"pid {pid} not in the process table")
    sys.exit(2)
f = mine[0]
a = f["argv"]
if not (d.is_pytest(a) and not d.single_file_pytest(a)):
    print(f"pid {pid} is not a heavy step: {' '.join(a)[:80]}")
    sys.exit(2)
found = [x for x in d.heavy_outside_slots(facts, -1) if f"(pid {pid}," in x]
print("outside" if found else "in-slot")
