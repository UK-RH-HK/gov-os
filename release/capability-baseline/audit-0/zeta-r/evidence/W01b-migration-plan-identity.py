"""W1 Stable artefact identity, W1 type "migration plans" (Contract v3 line 1080), and "audit findings" of adoption.

Brownfield adoption (fixtures/brownfield) through A0-A4 exactly as the product's certification harness does it
(tests/certification/common.rs run_brownfield_to_a6: chat_history.sql materialised into sqlite first), then the
migration plan the product persisted (spec/audits/GOVERNANCE-ADOPTION/05-plan.yaml + 05-ADOPTION-MIGRATION-PLAN.md)
is inspected for the nine W1 attributes.
"""
import sys, os, json, sqlite3, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from zprobe import *
import yaml

root, g = new_project("w1b", fixture="brownfield", init=False)
sql = read_text(root, "memory/chat_history.sql")
con = sqlite3.connect(os.path.join(root, "memory/chat_history.sqlite"))
con.executescript("PRAGMA journal_mode=DELETE; " + sql)
con.close()
os.remove(os.path.join(root, "memory/chat_history.sql"))
commit(root, "with chat db")
planner = g.with_(session="S-planner")
for s in ["baseline", "inventory", "classify", "map", "plan"]:
    planner.ok("adopt", s, limit=1200)
ev = "spec/audits/GOVERNANCE-ADOPTION"
plan_yaml = os.path.join(root, ev, "05-plan.yaml")
plan_md = os.path.join(root, ev, "05-ADOPTION-MIGRATION-PLAN.md")
obs("W1-migplan-persisted", os.path.exists(plan_yaml) and os.path.exists(plan_md), f"product persisted {ev}/05-plan.yaml and 05-ADOPTION-MIGRATION-PLAN.md")
doc = yaml.safe_load(open(plan_yaml))
log("05-plan.yaml top-level keys: " + str(sorted(doc.keys())))
log("05-plan.yaml (excerpt): " + json.dumps(doc)[:1500])
md = open(plan_md).read()
log("05-ADOPTION-MIGRATION-PLAN.md head:\n" + md[:800])
top = set(doc.keys())
obs("W1-b1-migplan-stable-id", "id" in top, f"05-plan.yaml carries a stable artefact id: keys={sorted(top)}")
obs("W1-b2-migplan-type", "type" in top, "05-plan.yaml carries an artefact type")
obs("W1-b4-migplan-authority", "state_class" in top or "status" in top, "05-plan.yaml carries authoritative status / lifecycle")
obs("W1-b6-migplan-version-hash", any(k in top for k in ("version", "content_hash", "hash")), "05-plan.yaml carries version/content hash")
obs("W1-b7-migplan-provenance", any(k in top for k in ("provenance", "created_by", "session", "role", "producer")), "05-plan.yaml carries producer/provenance (created_at only is a timestamp, not a producer)")
obs("W1-b8-migplan-lineage", any(k in top for k in ("supersedes", "superseded_by")), "05-plan.yaml carries supersedes lineage (re-running A4 overwrites the file in place)")
obs("W1-b9-migplan-consumers", any(k in top for k in ("consumers", "expected_consumers")), "05-plan.yaml declares expected downstream consumers")
# re-run A4: is the earlier plan preserved/superseded, or overwritten?
before = open(plan_yaml).read()
time.sleep(1.2)
planner.run("adopt", "plan", quiet=True)
after = open(plan_yaml).read()
files = sorted(os.listdir(os.path.join(root, ev)))
log("adoption evidence dir after re-plan: " + str(files))
obs("W1-b8-migplan-replan-keeps-history", any("05-plan" in f and f != "05-plan.yaml" for f in files), f"re-running A4 keeps a superseded plan version (file rewritten in place: {before != after}; created_at before={yaml.safe_load(before)['created_at']} after={yaml.safe_load(after)['created_at']}); files={[f for f in files if f.startswith('05')]}")
summary()
