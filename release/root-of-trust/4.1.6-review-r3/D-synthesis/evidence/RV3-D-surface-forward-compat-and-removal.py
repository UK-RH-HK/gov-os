#!/usr/bin/env python3
"""AR-0004 (review r3 synthesis D) held-out injections with the pack's OWN coverage checker (constitutional-surface/csi_check.py
run_check, unmodified). Kernel copies and inventory copies live in scratch only.

RV3-D-A09  Forward compatibility (HO-0001 §4): Gate W artifact-flow policy with a keyed requirement collection, receipt
           field floor and strict booleans; G0-G6 scheduler with a severity order that is not in the vocabulary and
           duration strings; owner contract Markdown + compiled YAML hash binding; a new key under a project_tunable
           parent. Positive (classified by inventory data only) and negative (weakening) variants.
RV3-D-A10  Removal of constitutional files and structured policy files (default deny covers additions; does E7 cover
           deletions?). Includes deletion of POLICY_PRECEDENCE.yaml, whose absence makes every kernel rule `immutable`.
Usage: REVIEW_REPO=<worktree> python3 RV3-D-surface-forward-compat-and-removal.py <scratch-dir>
"""
import copy, json, os, shutil, sys, tempfile

W = os.environ["REVIEW_REPO"]
CS = os.path.join(W, "release/root-of-trust/4.1.6/constitutional-surface")
sys.dont_write_bytecode = True
sys.path.insert(0, CS)
import yaml  # noqa: E402
import csi_lib as L  # noqa: E402
import csi_check as C  # noqa: E402

SCRATCH = sys.argv[1]
os.makedirs(SCRATCH, exist_ok=True)
BASE = tempfile.mkdtemp(prefix="rv3d-fc-", dir=SCRATCH)
KERNEL = os.path.join(W, "framework")
INV = yaml.safe_load(open(os.path.join(CS, "CONSTITUTIONAL_SURFACE_INVENTORY.yaml")))
results = []


def ydump(p, d):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as fh:
        yaml.safe_dump(d, fh, sort_keys=False)


def case(cid, title, expect_note, mutate=None, inv_patch=None):
    k = os.path.join(BASE, cid)
    shutil.copytree(KERNEL, k)
    if mutate:
        mutate(k)
    i = copy.deepcopy(INV)
    if inv_patch:
        inv_patch(i, k)
    rep = C.run_check(k, i, quiet=True)
    row = {"id": cid, "title": title, "expectation": expect_note, "exit": rep["exit"]}
    for kk in ("unclassified_files", "unclassified_leaves", "violations", "consistency", "malformed", "stronger_than_registered", "structure"):
        if rep.get(kk):
            row[kk] = json.loads(json.dumps(rep[kk], default=str))[:8]
    row["precedence_weaker_key_count"] = rep.get("precedence_weaker_key_count")
    results.append(row)
    return k, i, rep


# ------------------------------------------------------------------ RV3-D-A09 forward compatibility
GATE_W = {"policy": "ARTIFACT_FLOW_POLICY", "version": "1.0.0", "require_input_manifest": True, "require_consumption_receipt": True,
          "receipt_required_fields": ["task_id", "input_digest", "consumer", "consumed_at"],
          "requirements": [{"id": "W-01", "statement": "every task input is listed in a digest-bound manifest"},
                           {"id": "W-02", "statement": "every consumed artefact yields a receipt naming its digest"}]}


def gate_w_kernel(k, doc=None):
    ydump(os.path.join(k, "policies/ARTIFACT_FLOW_POLICY.yaml"), doc or GATE_W)


def gate_w_inventory(i, k):
    i["precedence"]["rules"][0:0] = [
        {"key": "ARTIFACT_FLOW_POLICY.receipt_required_fields", "mode": "additive", "kind": None, "order": None, "strict_value": None, "exception_relaxable": False},
        {"key": "ARTIFACT_FLOW_POLICY.require_input_manifest", "mode": "strengthen_only_bool", "kind": None, "order": None, "strict_value": True, "exception_relaxable": False},
        {"key": "ARTIFACT_FLOW_POLICY.require_consumption_receipt", "mode": "strengthen_only_bool", "kind": None, "order": None, "strict_value": True, "exception_relaxable": False},
        {"key": "ARTIFACT_FLOW_POLICY.*", "mode": "immutable", "kind": None, "order": None, "strict_value": None, "exception_relaxable": False}]
    leaves = [
        {"key": "ARTIFACT_FLOW_POLICY.policy", "class": "pinned", "digests": {"ARTIFACT_FLOW_POLICY.policy": [L.vdigest("ARTIFACT_FLOW_POLICY")]}},
        {"key": "ARTIFACT_FLOW_POLICY.version", "class": "pinned", "digests": {"ARTIFACT_FLOW_POLICY.version": [L.vdigest("1.0.0")]}},
        {"key": "ARTIFACT_FLOW_POLICY.require_input_manifest", "class": "floor", "op": "bool_toward", "strict": True, "value": True},
        {"key": "ARTIFACT_FLOW_POLICY.require_consumption_receipt", "class": "floor", "op": "bool_toward", "strict": True, "value": True},
        {"key": "ARTIFACT_FLOW_POLICY.receipt_required_fields", "class": "floor", "op": "set_superset", "value": GATE_W["receipt_required_fields"]},
        {"key": "ARTIFACT_FLOW_POLICY.requirements[id]#members", "class": "members", "op": "ids_superset", "registered": ["W-01", "W-02"]},
        {"key": "ARTIFACT_FLOW_POLICY.requirements[id=*].id", "class": "collection_id"},
        {"key": "ARTIFACT_FLOW_POLICY.requirements[id=*].statement", "class": "covered_by_collection"},
        {"key": "ARTIFACT_FLOW_POLICY.requirements[id=W-01].statement", "class": "pinned",
         "digests": {"ARTIFACT_FLOW_POLICY.requirements[id=W-01].statement": [L.vdigest(GATE_W["requirements"][0]["statement"])]}},
        {"key": "ARTIFACT_FLOW_POLICY.requirements[id=W-02].statement", "class": "pinned",
         "digests": {"ARTIFACT_FLOW_POLICY.requirements[id=W-02].statement": [L.vdigest(GATE_W["requirements"][1]["statement"])]}}]
    i["files"].append({"path": "policies/ARTIFACT_FLOW_POLICY.yaml", "mode": "structured", "name": "ARTIFACT_FLOW_POLICY", "policy_file": True,
                       "collections": [{"path": "requirements", "id_field": "id", "rationale": "additional requirements only strengthen"}], "leaves": leaves})


case("F01", "Gate W policy classified by inventory data only", "exit 0", gate_w_kernel, gate_w_inventory)
case("F02", "Gate W: registered requirement W-02 removed", "exit 3 (surface_membership)",
     lambda k: gate_w_kernel(k, dict(GATE_W, requirements=GATE_W["requirements"][:1])), gate_w_inventory)
case("F03", "Gate W: receipt field input_digest dropped", "exit 3 (floor_violation)",
     lambda k: gate_w_kernel(k, dict(GATE_W, receipt_required_fields=["task_id", "consumer", "consumed_at"])), gate_w_inventory)
case("F04", "Gate W: require_consumption_receipt false", "exit 3 (floor_violation)",
     lambda k: gate_w_kernel(k, dict(GATE_W, require_consumption_receipt=False)), gate_w_inventory)
case("F05", "Gate W: additional requirement W-03 (strengthening)", "exit 0",
     lambda k: gate_w_kernel(k, dict(GATE_W, requirements=GATE_W["requirements"] + [{"id": "W-03", "statement": "lineage recorded"}])), gate_w_inventory)

SCHED = {"policy": "HEALTH_SCHEDULER_POLICY", "version": "1.0.0", "min_severity_to_block": "high",
         "levels": {"G0": {"max_interval": "P1D"}, "G6": {"max_interval": "P30D"}}}


def sched_kernel(k, doc=None):
    ydump(os.path.join(k, "policies/HEALTH_SCHEDULER_POLICY.yaml"), doc or SCHED)


def sched_inventory(i, k):
    i["vocabulary"]["orders"]["severity"] = ["low", "medium", "high", "critical"]
    i["precedence"]["rules"][0:0] = [{"key": "HEALTH_SCHEDULER_POLICY.*", "mode": "immutable", "kind": None, "order": None, "strict_value": None, "exception_relaxable": False}]
    i["files"].append({"path": "policies/HEALTH_SCHEDULER_POLICY.yaml", "mode": "structured", "name": "HEALTH_SCHEDULER_POLICY", "policy_file": True, "collections": [], "leaves": [
        {"key": "HEALTH_SCHEDULER_POLICY.policy", "class": "pinned", "digests": {"HEALTH_SCHEDULER_POLICY.policy": [L.vdigest("HEALTH_SCHEDULER_POLICY")]}},
        {"key": "HEALTH_SCHEDULER_POLICY.version", "class": "pinned", "digests": {"HEALTH_SCHEDULER_POLICY.version": [L.vdigest("1.0.0")]}},
        {"key": "HEALTH_SCHEDULER_POLICY.min_severity_to_block", "class": "floor", "op": "equals", "value": "high"},
        {"key": "HEALTH_SCHEDULER_POLICY.levels.G0.max_interval", "class": "pinned", "digests": {"HEALTH_SCHEDULER_POLICY.levels.G0.max_interval": [L.vdigest("P1D")]}},
        {"key": "HEALTH_SCHEDULER_POLICY.levels.G6.max_interval", "class": "pinned", "digests": {"HEALTH_SCHEDULER_POLICY.levels.G6.max_interval": [L.vdigest("P30D")]}}]})


def sched_inventory_ordered(i, k):
    sched_inventory(i, k)
    for f in i["files"]:
        if f.get("name") == "HEALTH_SCHEDULER_POLICY":
            for l in f["leaves"]:
                if l["key"].endswith("min_severity_to_block"):
                    l.update({"op": "ordered_at_most", "order": ["low", "medium", "high", "critical"], "value": "high"})
    i["precedence"]["rules"][0:0] = [{"key": "HEALTH_SCHEDULER_POLICY.min_severity_to_block", "mode": "ceiling", "kind": "ordered", "order": ["low", "medium", "high", "critical"], "strict_value": None, "exception_relaxable": False}]


case("F06", "G0-G6 scheduler: durations pinned, severity equals (no new operator)", "exit 0", sched_kernel, sched_inventory)
case("F07", "G0-G6 scheduler: severity as ordered_at_most over a new inventory-declared order", "observe (does a new order need a vocabulary change?)", sched_kernel, sched_inventory_ordered)
case("F08", "G0-G6 scheduler: G6 max_interval P30D -> P365D (weakening of a non-orderable duration)", "exit 3 (surface_unregistered)",
     lambda k: sched_kernel(k, dict(SCHED, levels={"G0": {"max_interval": "P1D"}, "G6": {"max_interval": "P365D"}})), sched_inventory)

MD = "# Capability Acceptance Contract\nOwner-supplied normative source.\n"


def contract_kernel(k, md=MD, bind=None):
    p = os.path.join(k, "constitution/CAPABILITY_ACCEPTANCE_CONTRACT.md")
    open(p, "w").write(md)
    import hashlib
    ydump(os.path.join(k, "policies/CAPABILITY_ACCEPTANCE_CONTRACT.yaml"), {"policy": "CAPABILITY_ACCEPTANCE_CONTRACT", "version": "1.0.0",
                                                                           "source_md_sha256": bind or ("sha256:" + hashlib.sha256(MD.encode()).hexdigest())})


def contract_inventory(i, k):
    import hashlib
    i["precedence"]["rules"][0:0] = [{"key": "CAPABILITY_ACCEPTANCE_CONTRACT.*", "mode": "immutable", "kind": None, "order": None, "strict_value": None, "exception_relaxable": False}]
    i["files"].append({"path": "constitution/CAPABILITY_ACCEPTANCE_CONTRACT.md", "mode": "pinned_file", "rationale": "owner-supplied normative source",
                       "digests": {"constitution/CAPABILITY_ACCEPTANCE_CONTRACT.md": ["sha256:" + hashlib.sha256(MD.encode()).hexdigest()]}})
    i["files"].append({"path": "policies/CAPABILITY_ACCEPTANCE_CONTRACT.yaml", "mode": "structured", "name": "CAPABILITY_ACCEPTANCE_CONTRACT", "policy_file": True, "collections": [], "leaves": [
        {"key": "CAPABILITY_ACCEPTANCE_CONTRACT.policy", "class": "pinned", "digests": {"CAPABILITY_ACCEPTANCE_CONTRACT.policy": [L.vdigest("CAPABILITY_ACCEPTANCE_CONTRACT")]}},
        {"key": "CAPABILITY_ACCEPTANCE_CONTRACT.version", "class": "pinned", "digests": {"CAPABILITY_ACCEPTANCE_CONTRACT.version": [L.vdigest("1.0.0")]}},
        {"key": "CAPABILITY_ACCEPTANCE_CONTRACT.source_md_sha256", "class": "pinned",
         "digests": {"CAPABILITY_ACCEPTANCE_CONTRACT.source_md_sha256": [L.vdigest("sha256:" + hashlib.sha256(MD.encode()).hexdigest())]}}]})


case("F09", "Capability contract: Markdown + compiled YAML hash binding", "exit 0", contract_kernel, contract_inventory)
case("F10", "Capability contract: Markdown edited, YAML binding unchanged", "exit 3", lambda k: contract_kernel(k, md=MD + "Agents may self-accept.\n"), contract_inventory)
case("F11", "Capability contract: Markdown and binding both replaced consistently", "exit 3",
     lambda k: contract_kernel(k, md=MD + "x\n", bind="sha256:" + "0" * 64), contract_inventory)


def tunable_parent(k):
    # add a new key beside an existing project_tunable leaf
    tun = None
    for f in INV["files"]:
        for l in f.get("leaves", []):
            if l.get("class") == "project_tunable" and l["key"].count(".") >= 2:
                tun = (f, l)
                break
        if tun:
            break
    f, l = tun
    parts = l["key"].split(".")
    path = os.path.join(k, f["path"])
    d = yaml.safe_load(open(path))
    node = d
    for p in parts[1:-1]:
        node = node[p]
    node["allow_remote_upload_rv3d"] = True
    ydump(path, d)
    results.append({"id": "F12-context", "tunable_leaf_used": l["key"], "file": f["path"]})


case("F12", "new key beside an existing project_tunable leaf", "exit 2 (default deny)", tunable_parent)

# ------------------------------------------------------------------ RV3-D-A10 removal of constitutional content


def rm(rel):
    def f(k):
        p = os.path.join(k, rel)
        if os.path.isdir(p):
            shutil.rmtree(p)
        elif os.path.exists(p):
            os.remove(p)
        else:
            results.append({"id": "missing-in-framework", "path": rel})
    return f


schemas = sorted(os.listdir(os.path.join(KERNEL, "schemas")))
for cid, rel in (("R01", "policies/SECURITY_POLICY.yaml"), ("R02", "constitution/HARD_INVARIANTS.yaml"), ("R03", "policies/ENFORCEMENT_MAP.yaml"),
                 ("R04", "schemas/" + schemas[0]), ("R05", "roles/ROLES.yaml"), ("R06", "adapters/generic/template.md"),
                 ("R07", "policies/POLICY_PRECEDENCE.yaml"), ("R08", "policies/HUMAN_GATE_POLICY.yaml"), ("R09", "policies/AUTHORITY_POLICY.yaml")):
    k, i, rep = case(cid, f"constitutional file removed: {rel}", "observe: is a missing constitutional file refused by E7?", rm(rel))
    if cid == "R07":
        # effective project-layer rule per registered key when the kernel has no POLICY_PRECEDENCE file
        reg = i["precedence"]["rules"]
        lost = {}
        for r in reg:
            key = r["key"].replace("*", "p3probe")
            a = L.effective_rule([], "immutable", key)
            b = L.effective_rule(reg, i["precedence"]["default_mode"], key)
            j = L.rule_join(a, b)
            if b["mode"] != "immutable" and j["mode"] == "immutable":
                lost[r["key"]] = b["mode"]
        results.append({"id": "R07-effect", "registered_rules": len(reg), "keys_whose_project_layer_rule_becomes_immutable": len(lost),
                        "by_registered_mode": {m: sum(1 for v in lost.values() if v == m) for m in sorted(set(lost.values()))},
                        "examples": dict(list(lost.items())[:12])})

print(json.dumps({"probe": "RV3-D surface forward compatibility and removal", "checker": "release/root-of-trust/4.1.6/constitutional-surface/csi_check.py run_check (unmodified)",
                  "kernel": "framework/ (copied to scratch)", "cases": results}, indent=1, default=str))
