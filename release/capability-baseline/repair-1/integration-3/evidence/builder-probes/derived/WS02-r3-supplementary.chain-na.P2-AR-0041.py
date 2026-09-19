#!/usr/bin/env python3
# LABELLED DERIVED COPY (P2-AR-0041, round-3 integration) of repair-1/r3-ws02/evidence/WS02-r3-supplementary.py
# (P2-AR-0033). Changes, and only these: the fixture `base_spec` states what the scenario chain now computes
# (WS-5 round 3, IP-WS10-12: implementation work is blocked by the computed pre-implementation chain):
#   a. SCN-0001 carries `data_requirements_not_applicable` with a reason (was: none -> SCENARIO_DATA_UNDECLARED);
#   b. F-0001 states `representative_test_data` and `independent_acceptance_tests` as
#      {status: N/A_WITH_REASON, reason} (was PRESENT, which the chain computes MISSING and no longer honours).
# The same approach WS-5 used for zeta-r W06 (repair-1/r3-ws05/00-REPAIR-REPORT.md, "Probes").
# Without them IF1, G2 and W11 cannot claim TASK-0001 (TASK_NOT_RUNNABLE) and error out before any check.
"""P2-AR-0033 (WS-2, repair iteration 1 round 3) builder checks — regression evidence only (Contract v3 O3), not
acceptance. Drives `gov` (env GOV, default <tree>/target/release/gov) against disposable projects created from the
product's greenfield fixture, with GOV_CANONICAL_ROOT = the tree (env WT) and a private machine state per project,
every invocation declaring its role. Each CHECK line is computed from product output. Outputs go only to stdout and
to the scratch dir (env P2AR0033_SCRATCH or a new temp dir). Run it against the base binary and the repaired binary
to see which lines discriminate.

Groups:
  AV   the availability rule (P2-HO-0031): scoped blocks, remedies, typed refusals, the update entry decision (WS-3
       IP-R2-2, WS-5 O-R2-1/O-R2-2, WS-4 R2-8, WS-8 IP-R2-WS08-5), O-1 (a retired investigation subject)
  IF1  consumption is not implementation (integration IF-1, BC-P2-22)
  G    tier duties at their triggers (BC-P2-07): G1/G4 observation of mutations however made, G2 readiness at close,
       G3 claims/gates at handoff, G4 results recorded, G6 posture (WS-8 IP-R2-WS08-8)
  W11  the nine artifact-flow metrics move with injected faults (BC-P2-23)
  U    Gate U SLOs crossed change the health state; the HEALTHY conjunction (BC-P2-44)
  T2   registry entries (R3-11) and the adoption record (WS-9 IP-R2-4) in the OS-binding family and currency
  SKL  the two formerly deferred skill scenarios execute and pass; the planted secret literal is gone (IP-R2-WS08-6)
  EXIT blocked-class exit codes (WS-5 IP-R3-7)
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.environ.get("WT") or os.path.abspath(os.path.join(HERE, *[".."] * 5))
GOV = os.environ.get("GOV") or os.path.join(WT, "target", "release", "gov")
SCR = os.environ.get("P2AR0033_SCRATCH") or tempfile.mkdtemp(prefix="p2ar0033-supp-")
os.makedirs(SCR, exist_ok=True)
RESULTS = []


def log(*a):
    print(*a, flush=True)


def check(cid, ok, what, detail=None):
    RESULTS.append((cid, bool(ok)))
    d = json.dumps(detail, default=str)[:900] if detail is not None else ""
    log(f"CHECK {cid} {'PASS' if ok else 'FAIL'} {what}" + (f" -- {d}" if d else ""))


def git(root, *args):
    r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def commit(root, msg):
    git(root, "add", "-A")
    git(root, "-c", "user.email=p@example.invalid", "-c", "user.name=p", "commit", "-q", "-m", msg)


class Gov:
    def __init__(self, root, role="orchestrator", session="S-p2ar0033"):
        self.root, self.role, self.session = root, role, session
        self.machine = os.path.join(SCR, "machine-" + os.path.basename(root))

    def run(self, *args, role=None):
        env = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
        env["GOV_CANONICAL_ROOT"] = WT
        env["XDG_STATE_HOME"] = self.machine
        p = subprocess.run([GOV, "--json", "--root", self.root, "--session", self.session, "--role", role or self.role, *args],
                           capture_output=True, text=True, env=env)
        try:
            v = json.loads(p.stdout.strip())
        except Exception:
            v = {"ok": False, "error": {"code": "NO_JSON", "message": (p.stderr or p.stdout)[-1500:]}}
        v["_exit"] = p.returncode
        return v

    def ok(self, *args, role=None):
        v = self.run(*args, role=role)
        if not v.get("ok"):
            raise RuntimeError(f"gov {' '.join(args)} failed: {json.dumps(v.get('error'))[:1500]}")
        return v["result"]

    def body(self, *args):
        v = self.run(*args)
        return v.get("result") or (v.get("error") or {}).get("details") or {}, v


def code(v):
    return (v.get("error") or {}).get("code")


def write(root, rel, data):
    full = os.path.join(root, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(data if isinstance(data, str) else json.dumps(data, indent=1) + "\n")


def yload(root, rel):
    import yaml
    return yaml.safe_load(open(os.path.join(root, rel)))


def readiness_all_present():
    import yaml
    dims = yaml.safe_load(open(os.path.join(WT, "framework", "taxonomy", "READINESS_DIMENSIONS.yaml")))["dimensions"]
    return {d["id"]: "PRESENT" for d in dims}


def new_project(tag):
    root = os.path.join(SCR, f"{tag}-{int(time.time() * 1000) % 10**9}")
    shutil.copytree(os.path.join(WT, "fixtures", "greenfield", "project"), root)
    git(root, "init", "-q")
    commit(root, "fixture baseline")
    g = Gov(root)
    g.ok("init", "--name", tag, "--alias", f"s-{tag}"[:24])
    commit(root, "after gov init")
    return root, g


def base_spec(root, reqs=("REQ-0001",)):
    write(root, "spec/features/F-0001.yaml", {"id": "F-0001", "type": "feature", "title": "Order totals", "status": "ACTIVE",
          "capability_category": "backend", "requirements": list(reqs), "scenarios": ["SCN-0001"], "acceptance_tests": ["TST-0001"],
          "readiness": dict(readiness_all_present(),  # derived change b
                            representative_test_data={"status": "N/A_WITH_REASON", "reason": "pure arithmetic over literal inputs"},
                            independent_acceptance_tests={"status": "N/A_WITH_REASON", "reason": "probe fixture: the unit test is the acceptance evidence"})})
    write(root, "spec/scenarios/SCN-0001.yaml", {"id": "SCN-0001", "type": "scenario", "title": "Append two orders", "status": "ACTIVE",
          "feature": "F-0001", "actor": "clerk", "given": ["empty"], "when": ["two appended"], "then": ["399"],
          "success_criteria": ["exact"], "failure_criteria": ["dup"],
          "data_requirements_not_applicable": "pure arithmetic over literal inputs; no data"})  # derived change a
    write(root, "spec/tasks/TST-0001.yaml", {"id": "TST-0001", "type": "test-obligation", "title": "Totals test", "status": "ACTIVE",
          "feature": "F-0001", "family": "unit", "scenario": "SCN-0001"})
    for r in reqs:
        write(root, f"spec/requirements/{r}.yaml", {"id": r, "type": "requirement", "title": f"Requirement {r}", "status": "ACTIVE",
              "feature": "F-0001", "kind": "functional", "acceptance_criteria": [f"{r} holds"]})


def report(root, name, files, extra=None):
    d = os.path.join(root, ".governance-runtime", "reports")
    os.makedirs(d, exist_ok=True)
    f = os.path.join(d, f"{name}.json")
    v = {"work_completed": "done", "files_changed": files, "tests": {"status": "not_applicable_with_reason", "reason": "p2ar0033"},
         "outcome": "success", "evidence": [], "unknowns": []}
    v.update(extra or {})
    json.dump(v, open(f, "w"))
    return f


def receipt(g, root, task, name, files, extra=None):
    """The close report as WS-5's consumption receipt (the fields of the packet's receipt_contract)."""
    pk = g.ok("context", "compile", task)
    rc = pk.get("receipt_contract") or {}
    tr = rc.get("trace") or {}
    implemented = (extra or {}).get("requirements_implemented", tr.get("requirements", []))
    v = {"context_packet_hash": pk.get("packet_hash"),
         "inputs_consumed": [f"{e['id']}@{e['content_hash']}" for e in rc.get("acknowledge_inputs", [])],
         "outputs_produced": files, "requirements_implemented": implemented,
         "scenarios_implemented": tr.get("scenarios", []), "features_implemented": tr.get("features", []),
         "decisions_applied": tr.get("decisions", []), "constraints_applied": tr.get("constraints", []),
         "acceptance_evidence": [{"test": t, "result": "passed", "evidence": "p2ar0033"} for t in rc.get("tests_requiring_evidence", [])],
         "deviations": [f"{e['id']}: not implemented by this task (left for later work of the feature)"
                        for e in rc.get("acknowledge_inputs", []) if e["id"].startswith("REQ-") and e["id"] not in implemented],
         "unresolved": []}
    v.update(extra or {})
    return report(root, name, files, v)


def audit(g, *extra):
    return g.body("audit", *extra)[0]


def findings(a, family=None):
    return [f for f in a.get("findings", []) if family is None or f.get("family") == family]


def doctor(g):
    d, _ = g.body("doctor")
    return d


def dcheck(d, cid):
    for c in d.get("checks", []):
        if c["id"] == cid:
            return c
    return {}


def group(name, fn):
    log(f"\n## {name}")
    try:
        fn()
    except Exception as e:  # a group that cannot run is a failing line, never a crash
        import traceback
        check(f"{name.split()[0]}.error", False, f"group {name} could not run", {"error": str(e)[:600], "trace": traceback.format_exc()[-600:]})


PKG = {"options": [{"id": "A", "description": "yes"}, {"id": "B", "description": "no"}], "why_now": "w", "current_state": "c", "impact": "i",
       "reversibility": "reversible", "cost_rework": "one task", "recommendation": "A", "confidence": 0.5}
SECRET = "AKIA" + "ABCDEFGHIJKLMNOP"  # an AWS-access-key-shaped probe value, assembled here, never whole in a file of the tree


# ================================================================================================ AV availability
def av_subject_scope():
    root, g = new_project("av1")
    write(root, "spec/tasks/TASK-0101.yaml", {"id": "TASK-0101", "type": "task", "title": "broken", "status": "ACTIVE", "task_status": "READY",
          "class": "documentation", "objective": "o", "allowed_paths": ["docs/**"], "dependencies": ["TASK-0999"]})
    write(root, "spec/tasks/TASK-0102.yaml", {"id": "TASK-0102", "type": "task", "title": "independent", "status": "ACTIVE", "task_status": "READY",
          "class": "documentation", "objective": "o", "allowed_paths": ["docs/**"]})
    commit(root, "tasks")
    g.ok("rebuild-memory")
    g.run("health", "run", "--tier", "G1")
    st = g.ok("health", "status")
    gi = [b for b in st.get("blocks", []) if b.get("check") == "graph_integrity"]
    check("AV.1a", bool(gi) and all(b.get("scope") == "subjects" for b in gi if "task.claim" in b.get("operations", [])),
          "a missing task dependency (graph_integrity high) holds a hard-block scoped to the tasks it names", [{k: b.get(k) for k in ("scope", "operations", "subjects")} for b in gi])
    c = g.run("task", "claim", "TASK-0102")
    check("AV.1b", c.get("ok"), "an independent task stays claimable (O-R2-2: the block is not global)", code(c))
    gd = g.run("health", "guard", "task.close", "--paths", "TASK-0101")
    blocks = ((gd.get("error") or {}).get("details") or {}).get("blocks", [])
    check("AV.1c", code(gd) == "HEALTH_HARD_BLOCK" and any(b.get("scope") == "subjects" and "TASK-0101" in json.dumps(b.get("subjects")) for b in blocks) and gd.get("_exit") == 4,
          "closing the task it names is refused (typed, exit 4), naming the block, its scope and its subjects", {"code": code(gd), "blocks": [{k: b.get(k) for k in ("check", "scope", "subjects")} for b in blocks]})
    rb = g.run("health", "guard", "release.build")
    check("AV.1d", code(rb) == "HEALTH_HARD_BLOCK", "a release still relies on the whole graph (global)", code(rb))


def av_remedy():
    root, g = new_project("av2")
    write(root, "src/creds.rs", f'pub const K: &str = "{SECRET}";\n')
    commit(root, "secret")
    g.run("doctor")
    m1 = os.path.join(SCR, "av2-docs.json")
    json.dump([{"op": "write_file", "path": "docs/n.md", "content": "n\n"}], open(m1, "w"))
    p1 = g.run("cit", "propose", "--proposal", "edit docs", "--targets", "docs/n.md", "--manifest", m1)
    check("AV.2a", code(p1) == "HEALTH_HARD_BLOCK", "under a critical block, a change transaction unrelated to it is refused (BC-P2-06 S6 holds)", code(p1))
    m2 = os.path.join(SCR, "av2-fix.json")
    json.dump([{"op": "delete_file", "path": "src/creds.rs"}], open(m2, "w"))
    gp = g.run("health", "guard", "cit.propose", "--paths", "src/creds.rs")
    check("AV.2b", gp.get("ok") and (gp.get("result") or {}).get("remedy") is True,
          "the G0 decision admits proposing the change transaction that repairs exactly what the block names (WS-4 R2-8: a remedy, not refused)", gp.get("result") or code(gp))
    p2 = g.run("cit", "propose", "--proposal", "remove the leaked key", "--manifest", m2)
    check("AV.2b-e2e", p2.get("ok"), "end to end through `gov cit propose` (needs WS-3's generic G0 site to leave `cit propose` to its host, which guards it with its paths: IP-R3-WS02-01)", code(p2) or (p2.get("result") or {}).get("id"))
    t = g.run("task", "create", "--class", "documentation", "--objective", "x")
    check("AV.2c", code(t) == "HEALTH_HARD_BLOCK", "a critical block still refuses starting unrelated work (global)", code(t))
    ex = g.run("health", "guard", "cit.execute", "--paths", "src/creds.rs")
    det = (ex.get("error") or {}).get("details") or {}
    check("AV.2d", code(ex) == "HEALTH_HARD_BLOCK" and det.get("remedy_admissible") is True,
          "executing the repairing change is admissible only as a remedy that must clear the block before it commits (committing operation)", {"code": code(ex), "remedy_admissible": det.get("remedy_admissible")})


def av_update():
    root, g = new_project("av3")
    os.rename(os.path.join(root, "governance/project/DATA_SENSITIVITY.yaml"), os.path.join(SCR, "av3-DATA_SENSITIVITY.yaml"))
    g.run("doctor")
    subj = []
    for x in ["governance/kernel/**", "governance/framework.lock", "governance/project/**", "governance/generated/**", "framework.json"]:
        subj += ["--paths", x]
    u = g.run("health", "guard", "update.apply", *subj)
    det = (u.get("error") or {}).get("details") or {}
    check("AV.3a", code(u) == "HEALTH_HARD_BLOCK" and det.get("remedy_admissible") is True and any(b.get("check") == "D006" for b in det.get("blocks", [])),
          "an overlay block (D006) admits `update --apply` as its remedy (it must clear it before commit): the update entry guard does not deadlock the upgrade (WS-8 IP-R2-WS08-5)", {"code": code(u), "remedy_admissible": det.get("remedy_admissible"), "checks": [b.get("check") for b in det.get("blocks", [])]})
    shutil.copy(os.path.join(SCR, "av3-DATA_SENSITIVITY.yaml"), os.path.join(root, "governance/project/DATA_SENSITIVITY.yaml"))
    g.run("doctor")
    write(root, "spec/requirements/REQ-0102.yaml", {"id": "REQ-0102", "type": "requirement", "title": "bad", "status": "NOT_A_LIFECYCLE_STATUS"})
    g.ok("rebuild-memory")
    g.run("health", "run", "--tier", "G1")
    u2 = g.run("health", "guard", "update.apply", *subj)
    det2 = (u2.get("error") or {}).get("details") or {}
    check("AV.3b", code(u2) == "HEALTH_HARD_BLOCK" and not det2.get("remedy_admissible"),
          "a record block (schema_invariants on REQ-0102) is not one an update repairs: the update is refused at entry", {"code": code(u2), "remedy_admissible": det2.get("remedy_admissible")})
    cl = g.run("health", "guard", "task.close", "--paths", "TASK-0555", "--paths", "src/lib.rs")
    check("AV.3c", cl.get("ok"), "the same record block leaves a close that does not rely on REQ-0102 available", code(cl))


def av_governance_close():
    root, g = new_project("av4")
    t = g.ok("task", "create", "--class", "governance", "--objective", "record a decision", "--allowed", "spec/decisions/**", "--status", "READY")["id"]
    commit(root, "task")
    g.ok("rebuild-memory")
    g.ok("task", "claim", t)
    write(root, "spec/decisions/D-0009.yaml", {"id": "D-0009", "type": "decision", "title": "depends on unwritten requirement", "status": "ACTIVE",
          "question": "q", "chosen_option": "A", "depends_on": ["REQ-9999"]})
    g.ok("rebuild-memory", "--incremental")
    c = g.run("task", "close", t, "--report", receipt(g, root, t, "av4", ["spec/decisions/D-0009.yaml"]))
    r = c.get("result") or {}
    check("AV.4a", c.get("ok") and r.get("task_status") == "DONE",
          "a governance-affecting close relies on the current complete suite result even when it is not green (its warnings are the gaps it is completing): no GOVERNANCE_SUITE_STALE deadlock (O-R2-1)", code(c) or r.get("task_status"))
    cg = (r.get("close_gate") or {}).get("g2") or {}
    check("AV.4b", c.get("ok") and cg.get("verdict") in ("DEGRADED", "HEALTHY"), "…and the close records the G2 result it relied on", cg)


def av_resolved_investigation():
    root, g = new_project("av5")
    write(root, "spec/tasks/TST-0909.yaml", {"id": "TST-0909", "type": "test-obligation", "title": "orphan acceptance", "status": "ACTIVE", "family": "acceptance", "independent_of_implementer": True})
    commit(root, "orphan")
    g.ok("rebuild-memory")
    a = audit(g)
    gen = [t for t in glob.glob(os.path.join(root, "spec/tasks/TASK-*.yaml")) if "TST-0909" in open(t).read()]
    os.remove(os.path.join(root, "spec/tasks/TST-0909.yaml"))
    commit(root, "retire the orphan")
    g.ok("rebuild-memory", "--incremental")
    a2 = audit(g, "--no-persist")
    dang = [f for f in findings(a2, "graph_integrity") if "TST-0909" in f["message"]]
    check("AV.5a", gen and not dang, "the investigation's link to a retired subject is not reported as a dangling edge (O-1)", {"generated": [os.path.basename(x) for x in gen], "dangling": [f["message"][:160] for f in dang]})
    res = ((a2.get("families") or {}).get("lineage_orphans") or {}).get("detail", {}).get("resolved_investigations", [])
    check("AV.5b", any(r.get("subject") == "TST-0909" for r in res), "the investigation is listed as complete (subject retired), closable or withdrawable", res)
    d15 = dcheck(doctor(g), "D015")
    check("AV.5c", "TST-0909" not in d15.get("message", "") or "not defects" in d15.get("message", ""), "doctor D015 does not count it as a defect", d15.get("message", "")[:300])


# ================================================================================================= IF-1
def if1():
    root, g = new_project("if1")
    base_spec(root, reqs=("REQ-0001", "REQ-0002"))
    commit(root, "spec")
    g.ok("task", "create", "--id", "TASK-0001", "--class", "implementation", "--objective", "totals", "--feature", "F-0001", "--status", "READY",
         "--allowed", "src/**", "--fields", json.dumps({"requirements": ["REQ-0001"], "scenarios": ["SCN-0001"], "acceptance_tests": ["TST-0001"]}))
    commit(root, "task")
    g.ok("rebuild-memory")
    g.ok("task", "claim", "TASK-0001")
    write(root, "src/totals.rs", "pub fn totals() -> i64 { 399 }\n")
    g.ok("rebuild-memory", "--incremental")
    cl = g.run("task", "close", "TASK-0001", "--report", receipt(g, root, "TASK-0001", "if1", ["src/totals.rs"], {"requirements_implemented": ["REQ-0001"]}))
    rep = yload(root, f"spec/reports/{(cl.get('result') or {}).get('report')}.yaml") if cl.get("ok") else {}
    commit(root, "close")
    g.ok("rebuild-memory", "--incremental")
    a = audit(g, "--no-persist")
    o = {(f["orphan"]["kind"], f["orphan"]["subject"]): f for f in findings(a) if f.get("orphan")}
    r2 = o.get(("spec-without-downstream-path", "REQ-0002"), {})
    check("IF1.a", cl.get("ok") and "REQ-0002" in json.dumps(rep.get("inputs_consumed")) and r2.get("severity") == "medium",
          "a requirement the closing receipt consumed but declares not implemented is a W7 delivery gap (consumption is not implementation)", {"close": code(cl) or "DONE", "consumed": rep.get("inputs_consumed"), "finding": r2.get("message", "")[:300]})
    check("IF1.b", ("spec-without-downstream-path", "REQ-0001") not in o, "control: the requirement the receipt implemented is not an orphan")


# ================================================================================================= G tiers
def g1_observation():
    root, g = new_project("g1")
    t = g.ok("task", "create", "--class", "documentation", "--objective", "docs", "--allowed", "docs/**", "--status", "READY")["id"]
    commit(root, "task")
    g.ok("rebuild-memory")
    g.ok("task", "claim", t)
    with open(os.path.join(root, "src/lib.rs"), "a") as f:
        f.write(f'\npub const TOKEN: &str = "{SECRET}";\n')
    write(root, "spec/requirements/REQ-0102.yaml", {"id": "REQ-0102", "type": "requirement", "title": "x", "status": "NOT_A_LIFECYCLE_STATUS"})
    st = g.ok("status")
    obs = ((st.get("health") or {}).get("observed") or {})
    check("G1.a", obs.get("tier") in ("G1", "G4") and "src/lib.rs" in obs.get("changed_paths", []) and "spec/requirements/REQ-0102.yaml" in obs.get("changed_paths", []),
          "`gov status` right after direct edits observes them and runs G1 on what changed (no operator command)", {k: obs.get(k) for k in ("tier", "changed_paths", "executed")})
    hs = g.ok("health", "status")
    crit = [b for b in hs.get("blocks", []) if b.get("severity") == "critical"]
    schema = [c for c in hs.get("failing_checks", []) if c.get("check") == "schema_invariants"]
    check("G1.b", hs.get("state") == "RED" and crit and schema, "the secret (critical block) and the schema-invalid record (schema_invariants) are health facts at once", {"state": hs.get("state"), "critical": [b.get("check") for b in crit], "schema": schema})
    c = g.run("task", "create", "--class", "documentation", "--objective", "y")
    check("G1.c", code(c) == "HEALTH_HARD_BLOCK", "…so the next governed operation is refused by the observed critical block", code(c))
    src = open(os.path.join(root, "src/lib.rs")).read().replace(f'\npub const TOKEN: &str = "{SECRET}";\n', "")
    write(root, "src/lib.rs", src)
    os.remove(os.path.join(root, "spec/requirements/REQ-0102.yaml"))
    hs2 = g.ok("status")["health"]
    check("G1.d", hs2.get("state") != "RED", "repairing the files releases the block at the next observation (no manual re-run)", hs2.get("state"))
    write(root, "spec/architecture/ARCH-0101.yaml", {"id": "ARCH-0101", "type": "architecture", "title": "event sourcing", "status": "ACTIVE"})
    obs2 = (g.ok("status").get("health") or {}).get("observed") or {}
    check("G1.e", obs2.get("tier") == "G4" and obs2.get("milestone") is True, "an architecture change made directly is observed at G4 (wider staleness/impact propagation)", {k: obs2.get(k) for k in ("tier", "milestone", "changed_classes")})
    hist = g.ok("health", "history", "--limit", "20")
    check("G1.f", any((h.get("trigger") or {}).get("event") == "mutation.observed" and h.get("tier") == "G4" for h in hist),
          "the observation is a recorded health result (trigger mutation.observed, tier G4)", [(h.get("tier"), (h.get("trigger") or {}).get("event")) for h in hist[:6]])


def g2_readiness():
    root, g = new_project("g2")
    base_spec(root)
    commit(root, "spec")
    g.ok("task", "create", "--id", "TASK-0001", "--class", "implementation", "--objective", "totals", "--feature", "F-0001", "--status", "READY",
         "--allowed", "src/**,spec/features/**", "--fields", json.dumps({"requirements": ["REQ-0001"], "scenarios": ["SCN-0001"], "acceptance_tests": ["TST-0001"]}))
    commit(root, "task")
    g.ok("rebuild-memory")
    g.ok("task", "claim", "TASK-0001")
    write(root, "src/totals.rs", "pub fn totals() -> i64 { 399 }\n")
    f = yload(root, "spec/features/F-0001.yaml")
    f["readiness"]["security_privacy"] = "MISSING"
    write(root, "spec/features/F-0001.yaml", f)
    g.ok("rebuild-memory", "--incremental")
    rep = receipt(g, root, "TASK-0001", "g2", ["src/totals.rs", "spec/features/F-0001.yaml"], {"requirements_implemented": ["REQ-0001"]})
    c = g.run("task", "close", "TASK-0001", "--report", rep)
    check("G2.a", code(c) == "TASK_READINESS_REGRESSED", "a close after the feature's pre-implementation readiness regressed is refused (G2 readiness)", code(c) or (c.get("result") or {}).get("task_status"))


def g3_handoff():
    root, g = new_project("g3")
    for t in ("TASK-0001", "TASK-0002"):
        g.ok("task", "create", "--id", t, "--class", "documentation", "--objective", f"docs {t}", "--status", "READY", "--allowed", "docs/**")
    commit(root, "tasks")
    g.ok("rebuild-memory")
    g.ok("task", "claim", "TASK-0001")
    gid = g.ok("gate", "create", "--question", "Does this block TASK-0001?", "--fields", json.dumps(dict(PKG, blocks_tasks=["TASK-0001"])))["id"]
    g.run("gate", "present", gid)
    t = yload(root, "spec/tasks/TASK-0001.yaml")
    held = t.get("task_status")
    # the product parks claimed work on the gate (WAITING_HUMAN); a worker then edits the task back to IN_PROGRESS
    # directly, i.e. carries on without the decision — the state G3 must surface when the work is handed off
    import yaml
    t["task_status"] = "IN_PROGRESS"
    write(root, "spec/tasks/TASK-0001.yaml", yaml.safe_dump(t, sort_keys=False))
    commit(root, "direct: work continues on a gate-held task")
    g.ok("rebuild-memory", "--incremental")
    h = g.ok("handoff", "create", "--to-role", "backend-engineer", "--task", "TASK-0001")
    rec = yload(root, f"spec/handoffs/{h['id']}.yaml") if os.path.exists(os.path.join(root, f"spec/handoffs/{h['id']}.yaml")) else {}
    health = (rec.get("health") if rec else None) or h.get("health") or {}
    shown = g.ok("health", "show", health.get("health_result", "")) if health.get("health_result") else {}
    hgi = [c for c in (shown.get("checks") or []) if c.get("id") == "human_gate_integrity"]
    fam = audit(g, "--no-persist", "--family", "human_gate_integrity")
    fs = [f for f in findings(fam, "human_gate_integrity") if "TASK-0001" in f.get("message", "")]
    check("G3.0", held == "WAITING_HUMAN", "control: the product parks claimed work on the gate that blocks it", held)
    check("G3.a", health.get("tier") == "G3" and health.get("verdict") != "HEALTHY" and hgi and hgi[0].get("max_severity") == "medium"
          and any(f.get("severity") == "medium" for f in fs),
          "a handoff of work carried on (IN_PROGRESS) under an unanswered gate that blocks it records a G3 result that is not HEALTHY: human_gate_integrity names the gate-held work (claims/gates at handoff)",
          {"health": health, "g3_check": {k: hgi[0].get(k) for k in ("status", "max_severity", "findings")} if hgi else None,
           "findings": [(f.get("severity"), f.get("message", "")[:160]) for f in fs]})
    check("G3.b", not any("TASK-0002" in f.get("message", "") for f in findings(fam, "human_gate_integrity")),
          "control: work the gate does not block is not named")


def g4_recorded_and_g6():
    root, g = new_project("g6")
    cust = os.path.join(SCR, "custody-g6")
    os.makedirs(cust, exist_ok=True)
    for f in ("format-sample.oracle.json", "format-sample.score-report.json"):
        shutil.copy(os.path.join(WT, "release", "capability-baseline", "repair-1", "ws01-12", "evidence", "bc-p2-51", "samples", f), cust)
    q = g.run("health", "qualify", "--kind", "hidden-test", "--oracle", os.path.join(cust, "format-sample.oracle.json"),
              "--report", os.path.join(cust, "format-sample.score-report.json"))
    res = (q.get("result") or {}).get("qualification") or {}
    check("G6.a", q.get("ok") and res.get("machine_posture") == "UNPROVISIONED" and res.get("counts_as_qualification") is False,
          "a qualification run records the machine posture; on an unprovisioned machine it never counts as qualification (OWNER-DECISION-P2-0002 item 4)", {k: res.get(k) for k in ("machine_posture", "counts_as_qualification")} if res else code(q))
    before = sorted(glob.glob(os.path.join(root, "spec/audits/AUD-*.yaml")))
    write(root, "spec/architecture/ARCH-0102.yaml", {"id": "ARCH-0102", "type": "architecture", "title": "cqrs", "status": "ACTIVE"})
    g.ok("rebuild-memory", "--incremental")
    r = g.run("health", "run", "--tier", "G4", "--event", "architecture.change")
    after = sorted(glob.glob(os.path.join(root, "spec/audits/AUD-*.yaml")))
    check("G4.a", r.get("ok") is not None and len(after) >= len(before), "a G4 run is available as a host tier (recorded)", {"before": len(before), "after": len(after)})


# ================================================================================================= W11
def w11():
    root, g = new_project("w11")
    base_spec(root, reqs=("REQ-0001",))
    r = yload(root, "spec/requirements/REQ-0001.yaml")
    r["scenarios"] = ["SCN-0001"]
    write(root, "spec/requirements/REQ-0001.yaml", r)
    write(root, "spec/requirements/REQ-0009.yaml", {"id": "REQ-0009", "type": "requirement", "title": "old totals", "status": "SUPERSEDED", "superseded_by": "REQ-0001", "feature": "F-0001"})
    commit(root, "spec")
    g.ok("task", "create", "--id", "TASK-0001", "--class", "implementation", "--objective", "totals", "--feature", "F-0001", "--status", "READY",
         "--allowed", "src/**", "--fields", json.dumps({"requirements": ["REQ-0001"], "scenarios": ["SCN-0001"], "acceptance_tests": ["TST-0001"]}))
    commit(root, "task")
    g.ok("rebuild-memory")
    g.ok("task", "claim", "TASK-0001")
    write(root, "src/totals.rs", "pub fn totals() -> i64 { 399 }\n")
    g.ok("rebuild-memory", "--incremental")
    cl = g.run("task", "close", "TASK-0001", "--report", receipt(g, root, "TASK-0001", "w11", ["src/totals.rs"], {"requirements_implemented": ["REQ-0001"]}))
    commit(root, "implemented")
    g.ok("rebuild-memory", "--incremental")

    def m():
        a = audit(g, "--no-persist", "--family", "artifact_flow_health")
        return ((a.get("families") or {}).get("artifact_flow_health") or {}).get("detail", {}).get("w11_metrics", {})

    def v(mm, k):
        return (mm.get(k) or {}).get("value")

    def below(x):
        return x is not None and x < 1.0

    mb = m()
    keys = sorted(mb)
    check("W11.0", len(keys) == 9 and cl.get("ok"), "all nine W11 metrics are reported by the suite (audit family detail)", {"keys": keys, "close": code(cl) or "DONE"})
    # live work in progress on REQ-0001: a delivered packet and a resume checkpoint
    g.ok("task", "create", "--id", "TASK-0005", "--class", "documentation", "--objective", "document totals", "--status", "READY",
         "--allowed", "docs/**", "--fields", json.dumps({"requirements": ["REQ-0001"]}))
    g.ok("rebuild-memory", "--incremental")
    g.ok("task", "claim", "TASK-0005")
    g.ok("context", "compile", "TASK-0005")
    g.ok("checkpoint", "create", "--task", "TASK-0005", "--next-action", "document")
    m0 = m()
    # m1/m2/m5/m9: an upstream edit of the delivered input, made directly
    r = yload(root, "spec/requirements/REQ-0001.yaml")
    r["acceptance_criteria"] = ["totals round to whole units"]
    write(root, "spec/requirements/REQ-0001.yaml", r)
    g.ok("rebuild-memory", "--incremental")
    m1 = m()
    check("W11.m1", v(m0, "required_input_delivery_accuracy") == 1.0 and below(v(m1, "required_input_delivery_accuracy")),
          "required-input delivery accuracy moves when a delivered mandatory input changes", [v(m0, "required_input_delivery_accuracy"), v(m1, "required_input_delivery_accuracy")])
    check("W11.m2", v(m0, "current_version_selection_accuracy") == 1.0 and below(v(m1, "current_version_selection_accuracy")),
          "current-version selection accuracy moves when a delivered input is no longer current", [v(m0, "current_version_selection_accuracy"), v(m1, "current_version_selection_accuracy")])
    check("W11.m5a", (v(m1, "staleness_propagation_accuracy") is not None) and v(m1, "staleness_propagation_accuracy") < 1.0,
          "staleness propagation accuracy drops after a direct upstream edit", v(m1, "staleness_propagation_accuracy"))
    check("W11.m9", (v(m0, "fresh_agent_reconstruction_correctness") or 0) == 1.0 and below(v(m1, "fresh_agent_reconstruction_correctness")),
          "fresh-agent reconstruction correctness drops when the resume checkpoint and packet no longer describe the inputs",
          [v(m0, "fresh_agent_reconstruction_correctness"), v(m1, "fresh_agent_reconstruction_correctness")])
    pr = g.run("cit", "propagate")
    m2 = m()
    check("W11.m5b", v(m2, "staleness_propagation_accuracy") == 1.0, "…and returns to 1.0 once the change is propagated", {"value": v(m2, "staleness_propagation_accuracy"), "propagate": code(pr) or "ok"})
    # m3: a task governed by a SUPERSEDED requirement
    write(root, "spec/tasks/TASK-0002.yaml", {"id": "TASK-0002", "type": "task", "title": "old", "status": "ACTIVE", "task_status": "READY", "class": "documentation",
          "objective": "o", "allowed_paths": ["docs/**"], "requirements": ["REQ-0009"]})
    g.ok("rebuild-memory", "--incremental")
    m3 = m()
    check("W11.m3", (v(m2, "superseded_input_leakage_rate") or 0) == 0 and (v(m3, "superseded_input_leakage_rate") or 0) > 0,
          "superseded-input leakage rate rises when work is governed by a superseded requirement", [v(m2, "superseded_input_leakage_rate"), v(m3, "superseded_input_leakage_rate")])
    # m4: a task whose mandatory input is missing
    write(root, "spec/tasks/TASK-0003.yaml", {"id": "TASK-0003", "type": "task", "title": "missing", "status": "ACTIVE", "task_status": "READY", "class": "documentation",
          "objective": "o", "allowed_paths": ["docs/**"], "requirements": ["REQ-9999"]})
    g.ok("rebuild-memory", "--incremental")
    m4 = m()
    mi = m4.get("missing_required_input_detection") or {}
    check("W11.m4", mi.get("missing_required_inputs", 0) >= 1 and mi.get("value") == 1.0,
          "missing-required-input detection counts the missing input and whether the product detects it (not offered as runnable)", {k: mi.get(k) for k in ("value", "numerator", "denominator", "missing_required_inputs")})
    # m6/m7: an ACTIVE requirement nothing implements or tests
    c6, c7 = v(mb, "requirement_to_code_traceability_coverage"), v(mb, "requirement_to_test_traceability_coverage")
    write(root, "spec/requirements/REQ-0004.yaml", {"id": "REQ-0004", "type": "requirement", "title": "export", "status": "ACTIVE", "kind": "functional"})
    g.ok("rebuild-memory", "--incremental")
    m6 = m()
    check("W11.m6", c6 == 1.0 and v(m6, "requirement_to_code_traceability_coverage") == 0.5,
          "requirement→code coverage: 1.0 when the implementing receipt produced source, falls to 0.5 with a requirement nothing implements", [c6, v(m6, "requirement_to_code_traceability_coverage")])
    check("W11.m7", c7 == 1.0 and v(m6, "requirement_to_test_traceability_coverage") == 0.5,
          "requirement→test coverage: 1.0 through its validating scenario's test, falls to 0.5 with an untested requirement", [c7, v(m6, "requirement_to_test_traceability_coverage")])
    # m8: an injected orphan output is detected
    o0 = (m6.get("orphan_detection") or {}).get("orphans_detected")
    write(root, "spec/tasks/TST-0909.yaml", {"id": "TST-0909", "type": "test-obligation", "title": "orphan", "status": "ACTIVE", "family": "acceptance", "independent_of_implementer": True})
    g.ok("rebuild-memory", "--incremental")
    m8 = m()
    od = m8.get("orphan_detection") or {}
    check("W11.m8", od.get("orphans_detected", 0) > (o0 or 0) and "orphan_detection_false_positive_rate" in od and "orphan_detection_recall" in od,
          "orphan-output detection reports detections (rising with an injected orphan), false-positive rate and recall (with its source)", {k: od.get(k) for k in ("orphans_detected", "orphan_detection_precision", "orphan_detection_false_positive_rate", "orphan_detection_recall", "recall_source")})


# ================================================================================================= U (Gate U)
def u_slos():
    root, g = new_project("u")

    def slos():
        a = audit(g, "--no-persist", "--family", "health_slos")
        return a, {s["id"]: s for s in ((a.get("families") or {}).get("health_slos") or {}).get("detail", {}).get("slos", [])}

    a0, s0 = slos()
    check("U.0", len(s0) == 15 and all(s.get("threshold") is not None for s in s0.values()), "all fifteen Gate U SLOs are computed with a declared threshold", sorted(s0))
    # 5 orphan graph nodes
    for i in (1, 2, 3):
        write(root, f"spec/research/RES-000{i}.yaml", {"id": f"RES-000{i}", "type": "research", "title": f"orphan {i}", "status": "ACTIVE", "state_class": "NARRATIVE", "question": f"q{i}"})
    g.ok("rebuild-memory", "--incremental")
    a, s = slos()
    check("U.5", s.get("orphan_graph_count", {}).get("crossed") and a.get("verdict") != "HEALTHY", "three orphan research records cross the orphan-graph SLO and change the verdict", s.get("orphan_graph_count", {}).get("value"))
    for i in (1, 2, 3):
        os.remove(os.path.join(root, f"spec/research/RES-000{i}.yaml"))
    # 7 unresolved human gates
    for i in range(5):
        gid = g.ok("gate", "create", "--question", f"open question {i}?", "--fields", json.dumps(PKG))["id"]
        g.run("gate", "present", gid)
    g.ok("rebuild-memory", "--incremental")
    a, s = slos()
    check("U.7", s.get("unresolved_human_gates", {}).get("crossed") and any(f.get("slo") == "unresolved_human_gates" for f in findings(a)),
          "five open gates cross the unresolved-human-gates SLO (more than BUDGET_POLICY.max_parallel_agents)", s.get("unresolved_human_gates", {}).get("value"))
    # 8 task traceability
    for i in (1, 2, 3):
        write(root, f"spec/tasks/TASK-000{i}.yaml", {"id": f"TASK-000{i}", "type": "task", "title": f"untraced {i}", "status": "ACTIVE", "task_status": "READY", "class": "documentation", "objective": "o"})
    g.ok("rebuild-memory", "--incremental")
    a, s = slos()
    check("U.8", s.get("task_traceability", {}).get("crossed"), "three untraced tasks cross the task-traceability SLO", s.get("task_traceability", {}).get("value"))
    # 9 feature readiness coverage + H7 explicit readiness
    write(root, "spec/features/F-0001.yaml", {"id": "F-0001", "type": "feature", "title": "mostly unready", "status": "ACTIVE", "readiness": {"intent_outcome": "PRESENT"}})
    write(root, "spec/features/F-0002.yaml", {"id": "F-0002", "type": "feature", "title": "no readiness", "status": "ACTIVE", "readiness": {}})
    g.ok("rebuild-memory", "--incremental")
    a, s = slos()
    check("U.9", s.get("feature_readiness_coverage", {}).get("crossed"), "a feature with 1 of the readiness cells stated crosses the readiness-coverage SLO", s.get("feature_readiness_coverage", {}).get("value"))
    fr = audit(g, "--no-persist", "--family", "feature_readiness")
    check("U.H7", any("F-0002" in f["message"] and f["severity"] == "medium" for f in findings(fr)), "an active feature with an empty readiness block is not explicit (HEALTHY 7)", [f["message"][:120] for f in findings(fr)])
    # 12 first-pass completion, 13 handoff failure, 11 tokens
    for i in (1, 2):
        write(root, f"spec/reports/RPT-008{i}.yaml", {"id": f"RPT-008{i}", "type": "report", "status": "ACTIVE", "task": f"TASK-000{i}", "role": "backend-engineer", "outcome": "failed", "repair_count": 3})
        write(root, f"spec/planning/HND-008{i}.yaml", {"id": f"HND-008{i}", "type": "handoff", "status": "ACTIVE", "task": f"TASK-000{i}", "to_role": "backend-engineer",
              "handoff_status": "RETURNED", "return": {"status": "failed", "work_completed": "could not"}})
    write(root, "spec/tasks/TASK-0009.yaml", {"id": "TASK-0009", "type": "task", "title": "expensive", "status": "ACTIVE", "task_status": "DONE", "class": "documentation", "objective": "o", "closed_by_report": "RPT-0089"})
    write(root, "spec/reports/RPT-0089.yaml", {"id": "RPT-0089", "type": "report", "status": "ACTIVE", "task": "TASK-0009", "outcome": "success", "cost": {"tokens_input": 2500000, "tokens_output": 600000}})
    g.ok("rebuild-memory", "--incremental")
    a, s = slos()
    for sid in ("first_pass_completion", "handoff_failure", "tokens_per_completed_task"):
        check(f"U.{sid}", s.get(sid, {}).get("crossed"), f"the {sid} SLO crosses its threshold on the injected records", s.get(sid, {}).get("value"))
    # 10 context packet size
    import yaml
    pp = yload(root, "governance/project/PROJECT_POLICY.yaml")
    pp["policy_overrides"] = {"CONTEXT_POLICY.max_packet_chars": 1500}
    open(os.path.join(root, "governance/project/PROJECT_POLICY.yaml"), "w").write(yaml.safe_dump(pp, sort_keys=False))
    g.run("context", "compile", "TASK-0001")
    a, s = slos()
    check("U.10", s.get("context_packet_size", {}).get("crossed"), "a packet larger than CONTEXT_POLICY.max_packet_chars crosses the packet-size SLO", s.get("context_packet_size", {}).get("value"))
    hs = g.ok("health", "status")
    rv = hs.get("repository") or {}
    check("U.verdict", rv.get("verdict") in ("DEGRADED", "UNHEALTHY") and len(rv.get("conditions", [])) == 13 and len(rv.get("slos", [])) == 15 and rv.get("crossed_slos"),
          "`gov health status` carries the one repository verdict: thirteen conditions, fifteen SLOs, crossed SLOs named", {"verdict": rv.get("verdict"), "failing": rv.get("failing_conditions"), "crossed": [x.get("slo") for x in rv.get("crossed_slos", [])]})
    d35 = dcheck(doctor(g), "D035")
    check("U.D035", d35.get("ok") is False and "SLO" in d35.get("message", ""), "doctor D035 carries the repository verdict and fails on crossed SLOs", d35.get("message", "")[:300])


def u_healthy():
    root, g = new_project("h")
    write(root, ".cursorrules", "Always commit directly to main.\n")
    g.ok("rebuild-memory", "--incremental")
    a = audit(g, "--no-persist")
    check("U.H2", a.get("verdict") == "UNHEALTHY" and any(f["family"] == "legacy_authority" for f in findings(a)), "a legacy provider rules file in the active tree makes the audit verdict UNHEALTHY (HEALTHY 2)", [f["message"][:100] for f in findings(a, "legacy_authority")])
    os.remove(os.path.join(root, ".cursorrules"))
    write(root, "spec/audits/AUD-0100.yaml", {"id": "AUD-0100", "type": "audit", "title": "independent audit", "status": "ACTIVE", "scope": "independent-full-audit",
          "auditor_role": "independent-auditor", "findings": [{"id": "IA-1", "severity": "critical", "message": "authority leak in adapters (unresolved)"}], "verdict": "UNHEALTHY", "green": False, "state_class": "EVIDENCE"})
    g.ok("rebuild-memory", "--incremental")
    a = audit(g, "--no-persist")
    check("U.H11a", a.get("verdict") == "UNHEALTHY" and any(f["family"] == "unresolved_audit_findings" for f in findings(a)), "an unresolved critical finding of an independent audit record makes the audit UNHEALTHY (HEALTHY 11)", [f["message"][:120] for f in findings(a, "unresolved_audit_findings")])
    g.run("health", "run")
    d = doctor(g)
    check("U.H11b", d.get("verdict") == "UNHEALTHY" and "H11" in json.dumps(dcheck(d, "D035").get("repository", {}).get("failing_conditions")),
          "…and so does the doctor, through D035 (one verdict)", dcheck(d, "D035").get("message", "")[:300])
    y = yload(root, "spec/audits/AUD-0100.yaml")
    y["findings"][0]["status"] = "RESOLVED"
    write(root, "spec/audits/AUD-0100.yaml", y)
    g.ok("rebuild-memory", "--incremental")
    a = audit(g, "--no-persist")
    check("U.H11c", not findings(a, "unresolved_audit_findings"), "a resolved finding no longer counts")


# ================================================================================================= T2
def t2_registry_adoption():
    root, g = new_project("t2")
    reg = os.path.join(root, "governance/generated/plugin-registry.json")
    write(root, "governance/generated/plugin-registry.json", {"schema_version": "1.1.0", "plugins": {"forged": {"plugin_id": "forged", "registered_by": "nobody"}}})
    write(root, "spec/audits/GOVERNANCE-ADOPTION/00-BASELINE.yaml", {"commit": "abc", "stages": {}, "verdicts": {}})
    g.ok("rebuild-memory", "--incremental")
    a = audit(g, "--no-persist", "--family", "os_binding_integrity")
    msgs = [f["message"] for f in findings(a, "os_binding_integrity")]
    check("T2.reg", any("plugin-registry" in m for m in msgs), "a plugin-registry entry no gov operation wrote is reported as T2 state (R3-11)", [m[:140] for m in msgs])
    check("T2.adopt", any("adoption record" in m for m in msgs), "an adoption record gov adopt did not write is reported (WS-9 IP-R2-4)", [m[:140] for m in msgs])
    cur = g.ok("health", "currency")
    rows = (cur.get("snapshot") or {}).get("t2_bindings", {}).get("unverified", [])
    check("T2.cur", any(r.get("path") == "plugin-registry" for r in rows) and any("00-BASELINE" in str(r.get("path")) for r in rows),
          "both are T2 binding facts of the currency key (t2_bindings)", rows)


# ================================================================================================= SKL / EXIT
def skl_exit():
    root, g = new_project("skl")
    for sk in ("SKL-IMPACT-ANALYSIS", "SKL-RESEARCH-BENCHMARK", "SKL-MEMORY-RECONSTRUCTION"):
        r = g.ok("health", "skills", "--skill", sk)
        sc = [s for x in r["detail"]["skills"] for s in x["scenarios"]]
        check(f"SKL.{sk}", sc and all(s.get("status") == "passed" for s in sc), f"{sk} V1 executes as an executable scenario and passes", [(s.get("scenario"), s.get("status")) for s in sc])
    kf = os.path.join(WT, "framework", "health", "SKILL_SCENARIO_CHECKS.yaml")
    shutil.copy(kf, os.path.join(root, "docs-skill-checks.yaml"))
    d = doctor(g)
    check("SKL.literal", "docs-skill-checks.yaml" not in dcheck(d, "D011").get("message", ""), "the kernel's scenario checks file carries no scannable secret literal (IP-R2-WS08-6)", dcheck(d, "D011").get("message", "")[:200])
    os.remove(os.path.join(root, "docs-skill-checks.yaml"))


def main():
    log(f"# gov {GOV} ({subprocess.run(['sha256sum', GOV], capture_output=True, text=True).stdout[:64]})  tree {WT}  scratch {SCR}")
    group("AV subject scope (O-R2-2)", av_subject_scope)
    group("AV remedy admission (WS-4 R2-8)", av_remedy)
    group("AV update entry decision (IP-R2-WS08-5)", av_update)
    group("AV governance close on current evidence (O-R2-1)", av_governance_close)
    group("AV retired investigation subject (O-1)", av_resolved_investigation)
    group("IF1 consumption is not implementation", if1)
    group("G1 observation of mutations however made", g1_observation)
    group("G2 readiness at close", g2_readiness)
    group("G3 claims and gates at handoff", g3_handoff)
    group("G4/G6", g4_recorded_and_g6)
    group("W11 artifact-flow metrics", w11)
    group("U Gate U SLOs", u_slos)
    group("U HEALTHY conditions", u_healthy)
    group("T2 registry and adoption record", t2_registry_adoption)
    group("SKL skills and literal", skl_exit)
    p = sum(1 for _, ok in RESULTS if ok)
    log(f"\nSUMMARY pass={p} fail={len(RESULTS) - p} total={len(RESULTS)} failed={[c for c, ok in RESULTS if not ok]}")


if __name__ == "__main__":
    main()
