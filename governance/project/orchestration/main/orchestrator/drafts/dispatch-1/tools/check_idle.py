"""ACT-DISPATCH-1's behaviour check of the dispatcher's idle item (run from the repository root with `python3 -I - < this
file`, in the manifest as a here-document). Imports the dispatcher with its state folder planted in a fresh temporary
directory (nothing live is read or written; no tick runs) and calls watch_headroom() with a planted truth: the gate open,
two leads, two ready lines whose logs were used, the cap at 5. Prints 5 and exits 0 when: the first pass writes one inbox
item that names both lines; the same waiting set again writes none; a pass in which idle does not hold (a shut gate) and
then the same set again writes none; a changed waiting set writes a second item; a start clears the remembered cause."""
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
T = Path(tempfile.mkdtemp(prefix="dispatch-1-check-"))
os.environ["DISPATCH_STATE"] = str(T)
os.environ["DISPATCH_ORCH"] = str(T / "orch")
src = Path("governance/project/orchestration/tools/dispatch/dispatcher.py").resolve()
sys.path.insert(0, str(src.parent))
spec = importlib.util.spec_from_file_location("dispatcher_under_check", src)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)

(T / "ready.txt").write_text("W2-3 T-3 B3.md W2-3-A5-run1.json\nW2-4 T-4 B4.md W2-4-A5-run1.json\n")
truth = {"gate_open": True, "disk_open": True, "admit": True, "lead_count": 2, "pending_launches": [],
         "forecast": {"lead": {"ok": True}}}
shut = dict(truth, gate_open=False)
waits = {"W2-3 T-3": "already started for W2-3-A5-run1.json", "W2-4 T-4": "already holds a return"}
cfg = {"max_leads": 5}


def items():
    return sorted(p.read_text() for p in (T / "inbox").glob("*-idle-headroom*.txt")) if (T / "inbox").is_dir() else []


d.watch_headroom(truth, None, waits, cfg, False)
one = items()
assert len(one) == 1 and "W2-3 T-3 (already started for" in one[0] and "W2-4 T-4 (already holds a return" in one[0], one
d.watch_headroom(truth, None, waits, cfg, False)
assert len(items()) == 1
d.watch_headroom(shut, None, waits, cfg, False)
d.watch_headroom(truth, None, waits, cfg, False)
assert len(items()) == 1, items()
d.watch_headroom(truth, None, dict(waits, **{"W2-5 T-5": "no brief B5.md"}), cfg, False)
assert len(items()) == 2
d.watch_headroom(truth, "W2-6", waits, cfg, False)
assert json.loads((T / "idle-headroom-reported.json").read_text()) == {}
print(5)
