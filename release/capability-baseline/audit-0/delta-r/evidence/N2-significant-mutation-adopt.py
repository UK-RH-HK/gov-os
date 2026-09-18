"""N2 b4 'significant mutation' — the one product path that writes a significant_mutation checkpoint is the brownfield
migration batch executor (runtime/src/adopt.rs, a6_migrate). Exercise it on a copy of fixtures/brownfield/project.

Run:  python3 N2-significant-mutation-adopt.py > N2-significant-mutation-adopt.out 2>&1
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import WT, Proj, check, observe, summary  # noqa: E402

p = Proj("n2adopt", init=False)
src = os.path.join(WT, "fixtures", "brownfield", "project")
for name in os.listdir(src):
    s = os.path.join(src, name)
    d = os.path.join(p.root, name)
    if os.path.isdir(s):
        shutil.copytree(s, d)
    else:
        shutil.copy2(s, d)
p.git("add", "-A"); p.git("commit", "-q", "-m", "brownfield fixture")
# fixture preparation identical to the builder suite (tests/certification/brownfield.rs build_chat_sqlite): the legacy
# chat store ships as SQL text and is materialised into a SQLite file before adoption
import sqlite3  # noqa: E402
sql = open(p.path("memory/chat_history.sql")).read()
con = sqlite3.connect(p.path("memory/chat_history.sqlite")); con.executescript("PRAGMA journal_mode=DELETE; " + sql); con.close()
os.remove(p.path("memory/chat_history.sql"))
p.git("add", "-A"); p.git("commit", "-q", "-m", "with chat db")
for st in ("baseline", "inventory", "classify", "map", "plan", "test-design"):
    p.ok(["adopt", st], session="S-planner")
p.ok(["adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED"], session="S-reviewer", role="migration-reviewer")
mig = p.ok(["adopt", "migrate", "--name", "shipping-quotes", "--alias", "fx-brown"], session="S-executor", role="migration-executor")
observe("N2.adopt.migrate", "A6 result", {k: mig.get(k) for k in ("complete", "batches", "executed", "skipped") if k in mig})
cdir = p.path("spec/reports/checkpoints")
cks = sorted(f for f in os.listdir(cdir) if f.startswith("CKPT-")) if os.path.isdir(cdir) else []
trig = [(f, (p.record(f[:-5]) or {}).get("trigger"), (p.record(f[:-5]) or {}).get("next_action")) for f in cks]
observe("N2.adopt.checkpoints", "checkpoints written during adoption", trig)
check("N2.b4.adopt", any(t == "significant_mutation" for _, t, _ in trig), "migration batches (significant mutations) are preceded by significant_mutation checkpoints", trig)
summary()
