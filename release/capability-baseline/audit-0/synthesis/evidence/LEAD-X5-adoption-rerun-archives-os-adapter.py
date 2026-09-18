#!/usr/bin/env python3
"""P2-AR-0007 cross-family lead X5 (beta-r OBS-2 -> S4/B2/R1/T3): when adoption stages are run again on a repository that
already carries the Governance OS's own generated state (e.g. after an interrupted or remediated adoption, which A0
'detect interrupted prior governance work' anticipates), does classification treat the OS's generated IDE adapter as a
legacy provider-rules file and archive it; and does the migration ledger identify moved artefacts by the catalogue's ids?

Fixture: fixtures/brownfield/project with memory/chat_history.sql materialised as SQLite, exactly as its README says a
harness does. Pass 1 runs A0-A7; pass 2 re-runs A0-A7 on the result.
Run from the worktree root after `~/.cargo/bin/cargo build --release`:
  SYNTH_SCRATCH=<scratch> python3 release/capability-baseline/audit-0/synthesis/evidence/LEAD-X5-adoption-rerun-archives-os-adapter.py
"""
import glob
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from synth import *  # noqa

root, g = new_project("x5", fixture="brownfield", init=False)
sqlf = os.path.join(root, "memory/chat_history.sql")
con = sqlite3.connect(os.path.join(root, "memory/chat_history.sqlite"))
con.executescript("PRAGMA journal_mode=DELETE;" + open(sqlf).read())
con.close()
os.remove(sqlf)
commit(root, "chat store materialised as sqlite (fixture README)")
EV = os.path.join(root, "spec/audits/GOVERNANCE-ADOPTION")
planner = g.as_(role="orchestrator", session="S-planner")
reviewer = g.as_(role="migration-reviewer", session="S-reviewer")
executor = g.as_(role="migration-executor", session="S-executor")
verifier = g.as_(role="migration-verifier", session="S-verifier")


def adopt_pass(tag):
    planner.ok("adopt", "baseline", quiet=True)
    planner.ok("adopt", "inventory", quiet=True)
    planner.ok("adopt", "classify", quiet=True)
    planner.ok("adopt", "map", quiet=True)
    planner.ok("adopt", "plan", quiet=True)
    planner.ok("adopt", "test-design", quiet=True)
    reviewer.ok("adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED", quiet=True)
    m = executor.run("adopt", "migrate", "--name", "shipping-quotes", "--alias", f"fx-{tag}", quiet=True)
    cat = [json.loads(l) for l in open(os.path.join(EV, "04-TARGET-PATH-MAP.jsonl"))]
    gates = [e["human_gate"] for e in cat if e.get("requires_human_gate") and e.get("human_gate")]
    for gid in gates:
        executor.run("gate", "present", gid, quiet=True)
        g.as_(role="human", session="S-owner").run("decide", gid, "--option", "A", "--by", "owner", quiet=True)
    if gates:
        executor.run("adopt", "migrate", "--batch", "7", quiet=True)
    v = verifier.run("adopt", "verify-migration", quiet=True)
    note(f"pass {tag}: migrate ok={m.get('ok')} gates={gates} A7 verdict={(v.get('result') or {}).get('verdict') or (v.get('error') or {}).get('code')}")
    commit(root, f"adoption pass {tag}")
    return cat


cat1 = adopt_pass("1")
os_adapter = "governance/generated/adapters/ide/RULES.md"
note(f"after pass 1: OS IDE adapter present at {os_adapter}: {os.path.exists(os.path.join(root, os_adapter))}")
cat2 = adopt_pass("2")
cls = {json.loads(l)["path"]: json.loads(l) for l in open(os.path.join(EV, "02-CLASSIFICATION.jsonl"))}
ent = {e["current_path"]: e for e in cat2}
c = cls.get(os_adapter, {})
e = ent.get(os_adapter, {})
ids1 = {x_["current_path"]: x_.get("artifact_id") for x_ in cat1}
ids2 = {x_["current_path"]: x_.get("artifact_id") for x_ in cat2}
changed = {p_: (ids1[p_], ids2[p_]) for p_ in ids1 if p_ in ids2 and ids1[p_] != ids2[p_]}
x("X5-W1-catalogue-ids-stable-across-passes", not changed, "W1:1070 a path keeps its catalogue artefact id when adoption stages are re-run",
  {"paths_whose_id_changed": len(changed), "examples": dict(list(changed.items())[:5])})
x("X5-S4xB2-os-generated-adapter-not-legacy", c.get("authority") != "LEGACY" and e.get("action") in (None, "KEEP_IN_PLACE", "KEEP"),
  "S4 A2/A3 on re-run: the Governance OS's own generated IDE adapter is not classified as legacy provider rules or moved to the legacy archive",
  {"classification": {k: c.get(k) for k in ("class", "authority", "kinds", "id")}, "map": {k: e.get(k) for k in ("artifact_id", "action", "target_path")},
   "still_at_original_path": os.path.exists(os.path.join(root, os_adapter)),
   "archived_copies": [p.replace(root + "/", "") for p in glob.glob(os.path.join(root, "archive/governance/legacy-rules/*RULES*"))]})
# ledger vs catalogue ids for executed moves
ledgers = sorted(glob.glob(os.path.join(EV, "*LEDGER*")) + glob.glob(os.path.join(root, "spec/audits/**/*ledger*"), recursive=True))
note("ledger files: " + json.dumps([p.replace(root + "/", "") for p in ledgers]))
mismatch = []
for lp in ledgers:
    txt = open(lp).read()
    rows = []
    for line in txt.splitlines():
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    if not rows:
        try:
            import yaml
            y = yaml.safe_load(txt)
            rows = y if isinstance(y, list) else (y.get("entries") or y.get("events") or []) if isinstance(y, dict) else []
        except Exception:
            rows = []
    by_id = {x_["artifact_id"]: x_ for x_ in cat2 if "artifact_id" in x_}
    for r in rows:
        if not isinstance(r, dict):
            continue
        aid = r.get("artifact_id") or r.get("artefact_id") or r.get("id")
        src = r.get("from") or r.get("source") or r.get("current_path") or r.get("path")
        if aid in by_id and src and by_id[aid].get("current_path") != src:
            mismatch.append({"ledger": os.path.basename(lp), "ledger_id": aid, "ledger_path": src, "catalogue_path_for_that_id": by_id[aid].get("current_path")})
x("X5-T3-ledger-ids-match-catalogue", not mismatch, "T3:972 / S5:945 the migration ledger identifies each moved artefact by the id the catalogue gives that path",
  {"mismatches": mismatch[:10], "count": len(mismatch)})
summary()
