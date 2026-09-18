"""Freshness / invalidation demonstration for the Gate-W evidence the product holds (Contract v3 lines 95-111; frozen
gate contract AC-10: a relevant input change must be SHOWN to invalidate prior green evidence).

The product's only persisted green evidence is the governance-suite audit record (green=true, inputs_hash), whose
families context_reproducibility / product_traceability / graph_integrity are the suite's Gate-W-relevant checks, and
whose currency is reported by doctor D021. For each input class of Contract v3 lines 97-109 a change is made on top of a
fresh green record, D021 is read, and the tree is reset to the green baseline before the next class.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from zprobe import *
import yaml

root, g = new_project("fr")
base_spec(root, req_ids=("REQ-0001",))
write_record(root, "spec/requirements/REQ-0001.yaml", {"id": "REQ-0001", "type": "requirement", "title": "Totals are exact integer cents", "status": "ACTIVE", "feature": "F-0001", "acceptance_criteria": ["2 x 199 = 398"]})
write_record(root, "spec/decisions/D-0001.yaml", {"id": "D-0001", "type": "decision", "title": "i64 cents", "status": "ACTIVE", "chosen_option": "A", "affects": ["F-0001"]})
write_record(root, "spec/interfaces/API-0001.yaml", {"id": "API-0001", "type": "interface", "title": "Ledger API", "status": "ACTIVE", "contract": {"sig": "total()"}})
write_record(root, "spec/architecture/ARCH-0001.yaml", {"id": "ARCH-0001", "type": "architecture", "title": "Ledger crate owns totals", "status": "ACTIVE"})
commit(root, "spec")
g.ok("task", "create", "--id", "TASK-0001", "--class", "implementation", "--objective", "Implement totals", "--feature", "F-0001", "--status", "READY", "--allowed", "src/**",
     "--fields", json.dumps({"requirements": ["REQ-0001"], "scenarios": ["SCN-0001"], "acceptance_tests": ["TST-0001"], "decisions": ["D-0001"], "interfaces": ["API-0001"]}), quiet=True)
commit(root, "task")
g.ok("rebuild-memory", quiet=True)
au = g.run("audit", quiet=True)
ares = au.get("result") or (au.get("error") or {}).get("details") or {}
log(f"baseline audit {ares.get('audit')}: verdict={ares.get('verdict')} green={ares.get('green')} findings={[f['message'] for f in ares.get('findings', [])]}")
commit(root, "green baseline")
g.ok("memory", "rebuild", "--incremental", quiet=True)
_, base = git(root, "rev-parse", "HEAD")

def d021():
    r = g.run("doctor", quiet=True)
    res = r.get("result") or (r.get("error") or {}).get("details") or {}
    c = [x for x in res.get("checks", []) if x.get("id") == "D021"]
    return c[0] if c else {}

b = d021()
obs("FR-baseline-green-current", b.get("ok") is True, f"D021 at baseline: {b.get('message')}")

def yaml_edit(rel, fn):
    p = os.path.join(root, rel); d = yaml.safe_load(open(p)); fn(d); yaml.safe_dump(d, open(p, "w"), sort_keys=False)

CASES = [
    ("governing policy (PROJECT_POLICY override)", "gate-W relevant: CONTEXT_POLICY drives delivery", lambda: yaml_edit("governance/project/PROJECT_POLICY.yaml", lambda d: d.setdefault("policy_overrides", {}).__setitem__("CONTEXT_POLICY.max_retrieved_slices", 6))),
    ("schema (installed kernel schema)", "context-packet schema", lambda: write_text(root, "governance/kernel/schemas/context-packet.schema.json", read_text(root, "governance/kernel/schemas/context-packet.schema.json").replace('"chars"', '"chars_"'))),
    ("model/retrieval profile (MEMORY_POLICY pin)", "retrieval profile", lambda: yaml_edit("governance/project/PROJECT_POLICY.yaml", lambda d: d.setdefault("policy_overrides", {}).__setitem__("MEMORY_POLICY.retrieval.default_k", 5))),
    ("project path map (REPOSITORY_CONTRACT)", "path map", lambda: yaml_edit("governance/project/REPOSITORY_CONTRACT.yaml", lambda d: next(v for v in d.values() if isinstance(v, list) and v and isinstance(v[0], dict) and "pattern" in v[0]).append({"pattern": "spec/requirements/**", "class": "authoritative", "namespace": "spec", "semantic_index": False}))),
    ("security/sensitivity policy (DATA_SENSITIVITY)", "sensitivity", lambda: write_text(root, "governance/project/DATA_SENSITIVITY.yaml", read_text(root, "governance/project/DATA_SENSITIVITY.yaml") + "\n# zeta probe change\n")),
    ("authoritative decision (spec/decisions)", "mandatory input of TASK-0001", lambda: yaml_edit("spec/decisions/D-0001.yaml", lambda d: d.__setitem__("chosen_option", "B"))),
    ("authoritative requirement (spec/requirements)", "mandatory input of TASK-0001", lambda: yaml_edit("spec/requirements/REQ-0001.yaml", lambda d: d.__setitem__("acceptance_criteria", ["2 x 199 = 400"]))),
    ("authoritative interface (spec/interfaces)", "mandatory input of TASK-0001", lambda: yaml_edit("spec/interfaces/API-0001.yaml", lambda d: d.__setitem__("contract", {"sig": "total(currency)"}))),
    ("authoritative architecture (spec/architecture)", "delivered to every task", lambda: yaml_edit("spec/architecture/ARCH-0001.yaml", lambda d: d.__setitem__("title", "Totals moved to a service"))),
    ("task input manifest (spec/tasks)", "TASK-0001 declared inputs", lambda: yaml_edit("spec/tasks/TASK-0001.yaml", lambda d: d.__setitem__("requirements", ["REQ-0001", "REQ-0002"]))),
    ("relevant source file (src/)", "traced implementation", lambda: write_text(root, "src/lib.rs", read_text(root, "src/lib.rs") + "\npub fn fr() {}\n")),
    ("relevant index manifest (governance/generated)", "retrieval supplement", lambda: write_text(root, "governance/generated/index-manifest.json", read_text(root, "governance/generated/index-manifest.json").replace('"hashed-ngram"', '"hashed-ngram-x"'))),
]
if not os.path.exists(os.path.join(root, "governance/project/DATA_SENSITIVITY.yaml")):
    CASES = [c for c in CASES if "DATA_SENSITIVITY" not in c[0]]
for name, why, change in CASES:
    change()
    commit(root, f"change: {name}")
    c = d021()
    obs(f"FR-invalidates[{name}]", c.get("ok") is False, f"({why}) D021 after change: ok={c.get('ok')} message={c.get('message')!r}")
    git(root, "reset", "-q", "--hard", base)
log("runtime/kernel implementation (the gov binary itself): not attempted - the audited binary is the pinned candidate; inputs_hash() (runtime/src/verification/mod.rs:54-71) hashes governance/kernel, governance/project, governance/tests, spec/decisions and governance/framework.lock only")
summary()
