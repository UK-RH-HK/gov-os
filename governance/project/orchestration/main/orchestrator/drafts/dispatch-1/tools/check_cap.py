"""ACT-DISPATCH-1's behaviour check of the lead cap (run from the repository root with `python3 -I - < this file`, in the
manifest as a here-document). Imports the dispatcher with its state folder planted in a fresh temporary directory (nothing
live is read or written; no tick runs) and asks why_not() about one ready line that passes every other check, with the
checks that need a repository, a worktree or the machine's readings replaced by their planted answers. Prints 4 and exits 0
when: two leads under a cap of 3 leave the line startable; two leads under a cap of 2 refuse it with "lead cap: 2 of 2
running"; one lead and one launch pending under a cap of 2 refuse it the same way; no cap set never refuses."""
import importlib.util
import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

sys.dont_write_bytecode = True
T = Path(tempfile.mkdtemp(prefix="dispatch-1-check-"))
os.environ["DISPATCH_STATE"] = str(T)
os.environ["DISPATCH_ORCH"] = str(T / "orch")
src = Path("governance/project/orchestration/tools/dispatch/dispatcher.py").resolve()
sys.path.insert(0, str(src.parent))
spec = importlib.util.spec_from_file_location("dispatcher_under_check", src)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)

(T / "wt" / "W2-9").mkdir(parents=True)
(T / "wt" / "W2-9" / ".tickets").mkdir()
(T / "wt" / "W2-9" / ".tickets" / "T-9.md").write_text("---\nid: T-9\nstatus: in_progress\n---\n")
(T / "briefs").mkdir()
(T / "briefs" / "B9.md").write_text("a brief\n")
d.WT, d.BRIEFS, d.LOG = T / "wt", T / "briefs", T / "log"
d.LOG.mkdir()
d.sh = lambda *a, **k: SimpleNamespace(returncode=0, stdout="---\nstatus: in_progress\n---\n", stderr="")
d.tree_clean = lambda *a, **k: True
d.launcher_pending = lambda *a, **k: False
d.admit_safely = lambda *a, **k: (True, "planted: admits")
entry = ["W2-9", "T-9", "B9.md", "W2-9-A5-run1.json"]


def ask(cap, leads, pending=()):
    cfg = {} if cap is None else {"max_leads": cap}
    t = {"leads": [f"W2-{i}" for i in range(leads)], "lead_count": leads, "pending_launches": list(pending), "_procs": [],
         "_c": cfg, "disk_open": True}
    return d.why_not(entry, t, set(), set())


assert ask(3, 2) is None
assert ask(2, 2) == "lead cap: 2 of 2 running", ask(2, 2)
assert ask(2, 1, ["W2-7"]) == "lead cap: 2 of 2 running"
assert ask(None, 8) is None
print(4)
