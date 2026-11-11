"""ACT-IDLE-GUARD-1's behaviour check of the dispatcher's idle item (run from the repository root with
`python3 -I - < this file`, in the manifest as a here-document). Imports the dispatcher with its state folder planted in a
fresh temporary directory (nothing live is read or written; no tick runs) and calls watch_headroom() with a planted
truth: the gate open, no lead, a ready line the dispatcher skipped for its used log, the cap at 3. Prints 4 and exits 0
when: one inbox item is written and names the line; the same cause again in the hour writes none; with no cap set
nothing is written; at the cap nothing is written."""
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

T = Path(tempfile.mkdtemp(prefix="idle-guard-check-"))
os.environ["DISPATCH_STATE"] = str(T)
os.environ["DISPATCH_ORCH"] = str(T / "orch")
src = Path("governance/project/orchestration/tools/dispatch/dispatcher.py").resolve()
sys.path.insert(0, str(src.parent))
spec = importlib.util.spec_from_file_location("dispatcher_under_check", src)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)

(T / "ready.txt").write_text("W2-170 DAEO-61vm W2-170-A5-tests.md W2-170-A5-tests.json\n")
truth = {"gate_open": True, "disk_open": True, "admit": True, "lead_count": 0, "pending_launches": [],
         "forecast": {"lead": {"ok": True}}}
waits = {"W2-170 DAEO-61vm": "already started for W2-170-A5-tests.json"}


def items():
    return sorted(p.read_text() for p in (T / "inbox").glob("*-idle-headroom*.txt")) if (T / "inbox").is_dir() else []


d.watch_headroom(truth, None, waits, {"max_leads": 3}, False)
one = items()
assert len(one) == 1 and "skipped for a used or returned log: W2-170 DAEO-61vm (already started for" in one[0], one
assert "the gate is open and 0 of 3 leads run" in one[0] and not any(x.startswith("W2: ") for x in one[0].splitlines())
d.watch_headroom(truth, None, waits, {"max_leads": 3}, False)
assert len(items()) == 1
(T / "inbox" / "x").mkdir()
for p in (T / "inbox").glob("*-idle-headroom*.txt"):
    p.rename(T / "inbox" / "x" / p.name)
(T / "idle-headroom-reported.json").write_text(json.dumps({}))
d.watch_headroom(truth, None, waits, {}, False)
assert items() == []
d.watch_headroom(dict(truth, lead_count=3), None, waits, {"max_leads": 3}, False)
assert items() == []
print(4)
