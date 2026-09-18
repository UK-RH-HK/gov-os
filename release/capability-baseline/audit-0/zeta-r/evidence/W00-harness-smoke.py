"""W00 harness smoke: gov init into a copy of fixtures/greenfield, author a minimal spec, compile a context packet.
Establishes that the probe environment reproduces the certification harness environment. No capability verdict."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from zprobe import *

root, g = new_project("smoke")
g.ok("version")
base_spec(root)
write_record(root, "spec/requirements/REQ-0001.yaml", {"id": "REQ-0001", "type": "requirement", "title": "Ledger totals are exact integer cents", "status": "ACTIVE", "feature": "F-0001", "kind": "functional", "acceptance_criteria": ["total_cents sums quantity*unit_cents"]})
commit(root, "spec")
t = g.ok("task", "create", "--class", "implementation", "--objective", "Implement Ledger totals", "--feature", "F-0001", "--status", "READY", "--allowed", "src/**,tests/**", "--fields", '{"requirements": ["REQ-0001"], "scenarios": ["SCN-0001"]}')
g.ok("rebuild-memory")
c = g.ok("context", "compile", t["id"], limit=2500)
obs("W00-1", c["deterministic_authority"]["governing_requirements"][0]["id"] == "REQ-0001", "context packet deterministic block carries REQ-0001: " + str([r["id"] for r in c["deterministic_authority"]["governing_requirements"]]))
summary()
