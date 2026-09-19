#!/usr/bin/env python3
"""P2-AR-0023 (WS-2, repair iteration 1 round 2) builder checks — regression evidence only (Contract v3 O3), not
acceptance. Drives `gov` (env GOV, default <tree>/target/release/gov) against disposable projects created from the
product's greenfield fixture, with GOV_CANONICAL_ROOT = the tree (env WT, default: the tree this file is in) and a
private machine state per project, every invocation declaring its role. Each CHECK line is computed from product
output. Outputs only go to stdout and to the scratch dir (env P2AR0023_SCRATCH or a new temp dir).

Groups: W7 (BC-P2-22 orphans + remediation), T2 (IP-5 / IP-WS02-22), IDS (stable finding ids), EXIT (HEALTH_HARD_BLOCK),
G6 (qualification entry), DOC (D015/D017/D019/D032/D033/D034), SUITE (the reporting families other workstreams' APIs
feed), CUR (T2 binding in the currency key).
"""
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.environ.get("WT") or os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
GOV = os.environ.get("GOV") or os.path.join(WT, "target", "release", "gov")
SCR = os.environ.get("P2AR0023_SCRATCH") or tempfile.mkdtemp(prefix="p2ar0023-supp-")
os.makedirs(SCR, exist_ok=True)
RESULTS = []


def log(*a):
    print(*a, flush=True)


def check(cid, ok, what, detail=None):
    RESULTS.append((cid, bool(ok)))
    d = json.dumps(detail)[:700] if detail is not None else ""
    log(f"CHECK {cid} {'PASS' if ok else 'FAIL'} {what}" + (f" -- {d}" if d else ""))


def git(root, *args):
    r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def commit(root, msg):
    git(root, "add", "-A")
    git(root, "-c", "user.email=p@example.invalid", "-c", "user.name=p", "commit", "-q", "-m", msg)


class Gov:
    def __init__(self, root, role="orchestrator", session="S-p2ar0023", env=None):
        self.root, self.role, self.session = root, role, session
        self.machine = os.path.join(SCR, "machine-" + os.path.basename(root))
        self.env = env or {}

    def as_(self, role=None, env=None):
        e = dict(self.env)
        e.update(env or {})
        return Gov(self.root, role or self.role, self.session, e)

    def run(self, *args):
        env = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
        env["GOV_CANONICAL_ROOT"] = WT
        env["XDG_STATE_HOME"] = self.machine
        env.update(self.env)
        p = subprocess.run([GOV, "--json", "--root", self.root, "--session", self.session, "--role", self.role, *args],
                           capture_output=True, text=True, env=env)
        try:
            v = json.loads(p.stdout.strip())
        except Exception:
            v = {"ok": False, "error": {"code": "NO_JSON", "message": (p.stderr or p.stdout)[-1500:]}}
        v["_exit"] = p.returncode
        return v

    def ok(self, *args):
        v = self.run(*args)
        if not v.get("ok"):
            raise RuntimeError(f"gov {' '.join(args)} failed: {json.dumps(v.get('error'))[:1500]}")
        return v["result"]

    def body(self, *args):
        v = self.run(*args)
        return v.get("result") or (v.get("error") or {}).get("details") or {}, v


def write(root, rel, data):
    full = os.path.join(root, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(data if isinstance(data, str) else json.dumps(data, indent=1) + "\n")


def read_yaml(root, rel):
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
          "readiness": readiness_all_present()})
    write(root, "spec/scenarios/SCN-0001.yaml", {"id": "SCN-0001", "type": "scenario", "title": "Append two orders", "status": "ACTIVE",
          "feature": "F-0001", "actor": "clerk", "given": ["empty"], "when": ["two appended"], "then": ["399"],
          "success_criteria": ["exact"], "failure_criteria": ["dup"]})
    write(root, "spec/tasks/TST-0001.yaml", {"id": "TST-0001", "type": "test-obligation", "title": "Totals test", "status": "ACTIVE",
          "feature": "F-0001", "family": "unit", "scenario": "SCN-0001"})
    for r in reqs:
        write(root, f"spec/requirements/{r}.yaml", {"id": r, "type": "requirement", "title": f"Requirement {r}", "status": "ACTIVE",
              "feature": "F-0001", "kind": "functional"})


def audit(g, *extra):
    return g.body("audit", *extra)[0]


def msgs(a, family=None):
    return [f["message"] for f in a.get("findings", []) if family is None or f.get("family") == family]


def orphans(a):
    return {(f["orphan"]["kind"], f["orphan"]["subject"]): f for f in a.get("findings", []) if f.get("orphan")}


def doctor_check(g, cid):
    d, _ = g.body("doctor")
    for c in d.get("checks", []):
        if c["id"] == cid:
            return c
    return {}


def tasks(g):
    return g.ok("task", "list")


def task_records(root):
    import glob
    import yaml
    return [yaml.safe_load(open(f)) for f in sorted(glob.glob(os.path.join(root, "spec", "tasks", "TASK-*.yaml")))]


def report(root, name, files, extra=None):
    d = os.path.join(root, ".governance-runtime", "reports")
    os.makedirs(d, exist_ok=True)
    f = os.path.join(d, f"{name}.json")
    v = {"work_completed": "done", "files_changed": files, "tests": {"status": "not_applicable_with_reason", "reason": "p2ar0023"},
         "outcome": "success", "evidence": [], "unknowns": []}
    v.update(extra or {})
    json.dump(v, open(f, "w"))
    return f


log(f"# gov {GOV} ({subprocess.run(['sha256sum', GOV], capture_output=True, text=True).stdout[:64]})  tree {WT}  scratch {SCR}")

# =============================================================================================== W7 orphans (BC-P2-22)
log("\n## W7 orphan / unexplained-output detection and remediation")
root, g = new_project("w7")
base_spec(root, reqs=("REQ-0001", "REQ-0002"))
write(root, "spec/interfaces/API-0001.yaml", {"id": "API-0001", "type": "interface", "title": "export", "status": "ACTIVE", "contract": {"sig": "x"}, "consumers": ["TASK-0001"]})
write(root, "spec/interfaces/API-0002.yaml", {"id": "API-0002", "type": "interface", "title": "import", "status": "ACTIVE", "contract": {"sig": "y"}, "consumers": ["TASK-0001"]})
write(root, "spec/research/RES-0001.yaml", {"id": "RES-0001", "type": "research", "title": "rounding", "status": "ACTIVE", "question": "which?", "conclusion": "banker's", "influences": ["D-0001"]})
write(root, "spec/research/RES-0002.yaml", {"id": "RES-0002", "type": "research", "title": "overflow", "status": "ACTIVE", "question": "i64?", "conclusion": "yes", "influences": ["D-0002"]})
write(root, "spec/decisions/D-0001.yaml", {"id": "D-0001", "type": "decision", "title": "Rounding", "status": "ACTIVE", "chosen_option": "A", "rationale": "none"})
write(root, "spec/decisions/D-0002.yaml", {"id": "D-0002", "type": "decision", "title": "Width", "status": "ACTIVE", "chosen_option": "A", "rationale": "see research", "evidence_refs": ["RES-0002"]})
write(root, "spec/tasks/TST-0009.yaml", {"id": "TST-0009", "type": "test-obligation", "title": "orphan acceptance", "status": "ACTIVE", "family": "acceptance", "independent_of_implementer": True})
write(root, "spec/tasks/TST-0010.yaml", {"id": "TST-0010", "type": "test-obligation", "title": "linked acceptance", "status": "ACTIVE", "family": "acceptance", "tests": ["REQ-0001"], "independent_of_implementer": True})
write(root, "src/unexplained.rs", "pub fn unexplained() -> i64 { 7 }\n")
commit(root, "orphans and controls")
g.ok("task", "create", "--id", "TASK-0001", "--class", "implementation", "--objective", "totals", "--feature", "F-0001", "--status", "READY",
     "--allowed", "src/**", "--fields", json.dumps({"requirements": ["REQ-0001"], "scenarios": ["SCN-0001"], "interfaces": ["API-0002"]}))
commit(root, "task")
g.ok("rebuild-memory")
n0 = len(tasks(g))
a = audit(g, "--no-persist")
o = orphans(a)
check("W7.1a", (("unconsumed-output", "API-0001") in o), "an output whose declared consumer does not declare it is named", sorted(o))
check("W7.1c", ("unconsumed-output", "API-0002") not in o, "control: an output its consumer declares (interfaces) is not an orphan")
check("W7.2a", ("spec-without-downstream-path", "REQ-0002") in o and o[("spec-without-downstream-path", "REQ-0002")]["severity"] == "low",
      "a requirement no work or test reaches is named (low: no work of its feature is DONE yet)", o.get(("spec-without-downstream-path", "REQ-0002"), {}).get("severity"))
check("W7.2c", ("spec-without-downstream-path", "REQ-0001") not in o, "control: a requirement a task governs and a test validates is not an orphan")
check("W7.3a", ("unconsumed-research", "RES-0001") in o and o[("unconsumed-research", "RES-0001")]["severity"] == "medium",
      "research whose declared decision was decided without it is named (medium)")
check("W7.3c", ("unconsumed-research", "RES-0002") not in o, "control: research the decision cites (evidence_refs) is consumed")
check("W7.4a", ("unjustified-acceptance-test", "TST-0009") in o, "an acceptance test with no requirement/scenario is named")
check("W7.4c", ("unjustified-acceptance-test", "TST-0010") not in o, "control: an acceptance test that tests a requirement is not an orphan")
check("W7.5a", ("unjustified-code", "file:src/unexplained.rs") in o, "code added after the governance baseline that nothing justifies is named")
check("W7.5c", ("unjustified-code", "file:src/lib.rs") not in o and any("src/lib.rs" in m and "predate governance" in m for m in msgs(a, "lineage_orphans")),
      "control: baseline code is disclosed as baseline (low), not as unexplained output")
check("W7.6a", len(tasks(g)) == n0, "`--no-persist` generates no remediation (side-effect free)", {"before": n0, "after": len(tasks(g))})
a1 = audit(g)
n1 = len(tasks(g))
gen = [t for t in task_records(root) if t.get("generated_by") == "health:lineage_orphans"]
keys = {t["investigates"]["key"] for t in gen}
okeys = {f["orphan"]["key"] for f in a1.get("findings", []) if f.get("orphan")}
check("W7.6b", n1 > n0 and keys == okeys, "a persisted audit generates exactly one linked investigation task per orphan",
      {"generated": len(gen), "orphans": len(okeys)})
t0 = gen[0] if gen else {}
check("W7.6c", t0.get("task_status") == "READY" and t0.get("role") == "change-controller" and any(r.get("type") == "AFFECTS" and r.get("target") == t0.get("investigates", {}).get("subject") for r in t0.get("relations", [])),
      "the investigation is governed work: READY, designated change-controller, linked (AFFECTS) to its subject", {k: t0.get(k) for k in ("task_status", "role", "relations", "investigates")})
a2 = audit(g)
check("W7.6d", len(tasks(g)) == n1 and okeys <= set(f["orphan"]["key"] for f in a2.get("findings", []) if f.get("orphan")),
      "idempotent: a second audit creates no new task, and remediation does not hide the orphans (still reported)")
check("W7.6e", all(os.path.exists(os.path.join(root, p)) for p in ("spec/requirements/REQ-0002.yaml", "src/unexplained.rs", "spec/tasks/TST-0009.yaml")),
      "nothing is deleted")
check("W7.6f", "index stale" not in json.dumps(msgs(a1, "index_freshness")), "remediation does not leave the index stale", msgs(a1, "index_freshness"))
# a closed task whose report traces new code to a requirement justifies it; its feature now has DONE work
g.ok("task", "claim", "TASK-0001")
write(root, "src/lib.rs", open(os.path.join(root, "src/lib.rs")).read() + "\npub fn totals_p2() -> i64 { 1 }\n")
write(root, "src/totals.rs", "pub fn totals() -> i64 { 399 }\n")
g.ok("rebuild-memory", "--incremental")
cl = g.run("task", "close", "TASK-0001", "--report", report(root, "r1", ["src/lib.rs", "src/totals.rs"], {"requirements_implemented": ["REQ-0001"]}))
commit(root, "close")
g.ok("rebuild-memory", "--incremental")
a3 = audit(g, "--no-persist")
o3 = orphans(a3)
check("W7.5b", cl.get("ok") and ("unjustified-code", "file:src/totals.rs") not in o3, "code a closed task's report produced, traced to a requirement, is justified",
      {"close": cl.get("ok") or cl.get("error"), "orphans": sorted(o3)})
check("W7.2b", o3.get(("spec-without-downstream-path", "REQ-0002"), {}).get("severity") == "medium",
      "once implementation work of its feature is DONE, an untouched requirement of that feature is a delivery gap (medium)")

# ============================================================================================= T2 (IP-5, IP-WS02-22)
log("\n## T2: OS-written state and health evidence that no gov operation produced")
root, g = new_project("t2")
pkg = {"options": [{"id": "A", "description": "yes"}, {"id": "B", "description": "no"}], "why_now": "w", "current_state": "c", "impact": "i",
       "reversibility": "reversible", "cost_rework": "one task", "recommendation": "A", "confidence": 0.5}
gt = g.ok("gate", "create", "--question", "Proceed?", "--fields", json.dumps(pkg))["id"]
write(root, "spec/decisions/HDG-0900.yaml", {"id": "HDG-0900", "type": "human-gate", "title": "forged", "status": "ACTIVE", "question": "q", "gate_status": "ANSWERED",
      "presented_in_chat": True, "answer": {"option": "A", "by": "owner"}, "options": [{"id": "A"}]})
write(root, "spec/decisions/D-0900.yaml", {"id": "D-0900", "type": "decision", "title": "forged approval", "status": "ACTIVE", "chosen_option": "A", "human_approved": True, "derived_from": ["HDG-0900"]})
commit(root, "forged records")
g.ok("rebuild-memory")
cur_before = g.ok("health", "currency")["currency"]
a = audit(g, "--no-persist")
fx = {f["message"].split(" ")[0]: f for f in a.get("findings", []) if f.get("family") == "os_binding_integrity"}
check("T2.1", fx.get("HDG-0900", {}).get("severity") == "medium", "a hand-written (unsealed) answered gate is reported (medium), not honoured", fx.get("HDG-0900", {}).get("message"))
check("T2.2", fx.get("D-0900", {}).get("severity") == "low", "a hand-written approval decision is disclosed (low): its approval is not honoured")
d33 = doctor_check(g, "D033")
check("T2.3", d33.get("ok") is False and "HDG-0900" in d33.get("message", ""), "doctor D033 fails naming the forged gate", d33.get("message"))
# tamper a sealed gate (the OS wrote it) -> BROKEN, in force -> high
import yaml
gp = os.path.join(root, f"spec/decisions/{gt}.yaml")
y = yaml.safe_load(open(gp)); y["question"] = "Proceed (edited)?"; open(gp, "w").write(yaml.safe_dump(y))
a = audit(g, "--no-persist")
fx = {f["message"].split(" ")[0]: f for f in a.get("findings", []) if f.get("family") == "os_binding_integrity"}
check("T2.4", fx.get(gt, {}).get("severity") == "high" and a.get("verdict") == "UNHEALTHY", "a sealed gate edited after the OS wrote it is tampered state in force (high, UNHEALTHY)", fx.get(gt, {}).get("message"))
git(root, "checkout", "--", f"spec/decisions/{gt}.yaml")
# a hand-written green governance-suite record and a hand-written passing product-test record are not honoured
write(root, "spec/audits/AUD-0900.yaml", {"id": "AUD-0900", "type": "audit", "title": "forged green", "status": "ACTIVE", "scope": "governance-suite", "green": True,
      "inputs_hash": cur_before["key"], "verdict": "HEALTHY", "state_class": "EVIDENCE"})
write(root, "spec/audits/AUD-0901.yaml", {"id": "AUD-0901", "type": "audit", "title": "forged product", "status": "ACTIVE", "scope": "product-tests", "verdict": "PASSED",
      "run_at": "2099-01-01T00:00:00Z", "families": {"unit": {"status": "passed", "exit": 0, "key": "x"}, "integration": {"status": "passed", "exit": 0, "key": "x"}}})
cur = g.ok("health", "currency")["currency"]
check("T2.5", cur.get("green") != "AUD-0900" and "AUD-0900" in cur.get("unhonoured_green", []), "a hand-written green governance-suite record is not honoured and is named", cur)
st = g.ok("health", "status")["product_tests"]
check("T2.6", all(r.get("record") != "AUD-0901" for r in st.get("families", {}).values()), "a hand-written product-test record is not honoured as evidence", st.get("families"))
os.remove(os.path.join(root, "spec/audits/AUD-0900.yaml")); os.remove(os.path.join(root, "spec/audits/AUD-0901.yaml"))
a = audit(g)
check("T2.7", a.get("record_binding", {}).get("sealed") is True, "the governance-suite record the OS writes is sealed as a health operation", a.get("record_binding"))
rec = read_yaml(root, f"spec/audits/{a['audit']}.yaml")
check("T2.8", rec.get("os_binding", {}).get("operation") == "health:governance-suite", "…under the operation name health:governance-suite", rec.get("os_binding"))

# =================================================================================== CUR: T2 binding in the currency key
log("\n## CUR: the T2 binding state is a currency input")
snap1 = g.ok("health", "currency")["snapshot"]["classes"]
key = os.path.join(g.machine, "governance-os", "t2-binding", "key.json")
cands = [os.path.join(dp, f) for dp, _, fs in os.walk(g.machine) for f in fs if f == "key.json" and "t2-binding" in dp]
moved = None
if cands:
    moved = cands[0] + ".moved"
    os.rename(cands[0], moved)
snap2 = g.ok("health", "currency")["snapshot"]["classes"]
changed = sorted(k for k in snap1 if snap1[k]["digest"] != snap2[k]["digest"])
check("CUR.1", changed == ["t2_bindings"], "removing this machine's binding key (sealed records become unverifiable) changes exactly the t2_bindings class", {"changed": changed, "key": cands[:1]})
if moved:
    os.rename(moved, cands[0])

# ======================================================================================================== IDS / EXIT
log("\n## IDS: one stable finding-id scheme; EXIT: HEALTH_HARD_BLOCK is the blocked class")
root, g = new_project("ids")
base_spec(root)
write(root, "spec/scenarios/REQ-0007.yaml", {"id": "REQ-0007", "type": "requirement", "title": "misplaced", "status": "ACTIVE", "feature": "F-0001"})
commit(root, "x"); g.ok("rebuild-memory")
a1 = audit(g, "--no-persist")
write(root, "spec/requirements/AAA-0001.yaml", {"id": "AAA-0001", "type": "requirement", "title": "x", "status": "BOGUS"})
a2 = audit(g, "--no-persist")
m2 = {f["message"]: f["id"] for f in a2["findings"]}
shifted = [(f["message"][:60], f["id"], m2.get(f["message"])) for f in a1["findings"] if f["message"] in m2 and m2[f["message"]] != f["id"]]
check("IDS.1", not shifted and all(f["id"].startswith("GF-") and len(f["id"]) >= 13 for f in a2["findings"]), "finding ids are content-derived: an earlier new finding renumbers nothing", shifted[:3])
sys.path.insert(0, os.path.join(WT, "runtime"))
import hashlib
f0 = a2["findings"][0]
h = hashlib.sha256(f"governance-os/finding\n{f0['family']}\n{f0['message']}\n{f0.get('path') or ''}".encode()).hexdigest()[:10]
check("IDS.2", f0["id"].split("-")[0] + "-" + f0["id"].split("-")[1] == f"GF-{h}", "the suite uses the adoption audit's scheme (migrations::identity::finding_id)", {"id": f0["id"], "expected": f"GF-{h}"})
check("SUITE.misplaced", any("REQ-0007" in m and "canonical" in m for m in msgs(a1, "graph_integrity")), "graph_integrity names a record outside its canonical location (W1)")
os.remove(os.path.join(root, "spec/requirements/AAA-0001.yaml"))
write(root, "src/leak.rs", 'const K: &str = "AKIAABCDEFGHIJKLMNOP";\n')  # an AWS-key-shaped secret outside the secret class
g.run("doctor")
gd, gv = g.body("health", "guard", "task.create")
check("EXIT.1", gv.get("_exit") == 4 and (gv.get("error") or {}).get("code") == "HEALTH_HARD_BLOCK", "a governed operation refused by an active hard-block exits 4 (blocked class, API-0002)",
      {"exit": gv.get("_exit"), "code": (gv.get("error") or {}).get("code")})
os.remove(os.path.join(root, "src/leak.rs"))

# ====================================================================================================== G6 entry point
log("\n## G6: a qualification run is recorded only against a conforming, separate oracle and a bound report")
root, g = new_project("g6")
samples = os.path.join(WT, "release", "capability-baseline", "repair-1", "ws01-12", "evidence", "bc-p2-51", "samples")
cust = os.path.join(SCR, "verifier-custody-" + os.path.basename(root)); os.makedirs(cust, exist_ok=True)
for f in ("format-sample.oracle.json", "format-sample.score-report.json"):
    shutil.copy(os.path.join(samples, f), cust)
q = g.run("health", "qualify", "--kind", "hidden-test", "--oracle", os.path.join(cust, "format-sample.oracle.json"), "--report", os.path.join(cust, "format-sample.score-report.json"))
res = q.get("result") or {}
hr = (res.get("health") or {}).get("health_result")
shown = g.ok("health", "show", hr) if hr else {}
check("G6.1", q.get("ok") and res["qualification"]["counts_as_qualification"] is False and shown.get("tier") == "G6" and shown.get("qualification", {}).get("kind") == "hidden-test",
      "a conforming oracle and bound report are accepted; the G6 health result records the qualification (a FORMAT_SAMPLE is marked not counting)", {"ok": q.get("ok"), "err": q.get("error"), "tier": shown.get("tier")})
odoc = json.load(open(os.path.join(cust, "format-sample.oracle.json")))
leaks = []
for dp, dn, fs in os.walk(root):
    if ".git" in dp.split(os.sep):
        continue
    for fn in fs:
        try:
            t = open(os.path.join(dp, fn), "rb").read().decode("utf-8", "replace")
        except Exception:
            continue
        if odoc["oracle_id"] in t:
            leaks.append(os.path.relpath(os.path.join(dp, fn), root))
check("G6.1b", not leaks, "what G6 records in the qualification repository carries no trace of the hidden oracle (no oracle id or digest; a one-way commitment only)", leaks[:5])
inside = os.path.join(root, "qual"); os.makedirs(inside, exist_ok=True)
shutil.copy(os.path.join(cust, "format-sample.oracle.json"), inside)
n_hist = len(g.ok("health", "history", "--limit", "200"))
q2 = g.run("health", "qualify", "--oracle", os.path.join(inside, "format-sample.oracle.json"), "--report", os.path.join(cust, "format-sample.score-report.json"))
check("G6.2", (q2.get("error") or {}).get("code") == "ORACLE_SEPARATION_VIOLATED" and len(g.ok("health", "history", "--limit", "200")) == n_hist,
      "an oracle stored inside the governed repository is refused and no health is recorded", (q2.get("error") or {}).get("code"))
shutil.rmtree(inside)
rep = json.load(open(os.path.join(cust, "format-sample.score-report.json")))
rep["binding"]["oracle_sha256"] = "0" * 64
bad = os.path.join(cust, "bad-report.json"); json.dump(rep, open(bad, "w"))
q3 = g.run("health", "qualify", "--oracle", os.path.join(cust, "format-sample.oracle.json"), "--report", bad)
check("G6.3", (q3.get("error") or {}).get("code") in ("ORACLE_SCORE_BINDING_MISMATCH", "ORACLE_RECORD_INVALID"), "a report not bound to the oracle is refused", (q3.get("error") or {}).get("code"))
q4 = g.run("health", "qualify", "--kind", "vibes", "--oracle", os.path.join(cust, "format-sample.oracle.json"), "--report", os.path.join(cust, "format-sample.score-report.json"))
check("G6.4", (q4.get("error") or {}).get("code") == "USAGE", "an unknown qualification kind is a usage error")

# ============================================================================================================= DOCTOR
log("\n## DOC: doctor checks")
root, g = new_project("doc")
gid = g.ok("gate", "create", "--question", "Ship?", "--fields", json.dumps(pkg))["id"]
c = doctor_check(g, "D019")
check("DOC.D019a", c.get("ok") is False and gid in c.get("message", "") and "never rendered" in c.get("message", ""), "a gate never rendered exists only in files and fails D019 (INV-008)", c.get("message"))
g.ok("gate", "present", gid)
c = doctor_check(g, "D019")
check("DOC.D019b", c.get("ok") is True and gid in c.get("message", "") and "awaiting" in c.get("message", ""),
      "a rendered gate awaiting the owner's signed receipt or answer is reported, not failed (presented = signed receipt/answer)", c.get("message"))
c = doctor_check(g, "D032")
check("DOC.D032", c.get("ok") is False and c.get("posture", {}).get("machine_posture") == "UNPROVISIONED" and c.get("severity") == "medium",
      "an installation whose authenticity is not established fails D032 (the doctor verdict is never HEALTHY without disclosing it)", c.get("message", "")[:200])
a = audit(g, "--no-persist")
ia = [f for f in a.get("findings", []) if f.get("family") == "installation_authenticity"]
check("DOC.audit-disclosure", len(ia) == 1 and ia[0]["severity"] == "low", "the audit discloses it too (low on an unprovisioned bootstrap machine)", ia[:1])
c = doctor_check(g, "D017")
check("DOC.D017", ".governance-runtime/claims.db" in c.get("message", ""), "D017 names the claims store in use", c.get("message"))
write(root, "spec/reports/failures/FAIL-0001.yaml", {"id": "FAIL-0001", "type": "failure", "title": "adapter crashed", "status": "ACTIVE", "failure_kind": "tool-failure",
      "follow_up": {"status": "open", "required_actions": ["fix"]}})
c = doctor_check(g, "D034")
check("DOC.D034", c.get("ok") is False and "FAIL-0001" in c.get("message", ""), "an open tool failure in failure memory is reported and degrades (D034)", c.get("message"))
st = g.ok("health", "status")
check("DOC.status-failure-memory", st.get("failure_memory", {}).get("open") == 1, "`gov health status` reports open failure memory", st.get("failure_memory"))

# ============================================================================================ SUITE reporting families
log("\n## SUITE: the reporting side of other workstreams' checks")
root, g = new_project("suite")
base_spec(root, reqs=("REQ-0002",))
write(root, "spec/requirements/REQ-0001.yaml", {"id": "REQ-0001", "type": "requirement", "title": "old", "status": "SUPERSEDED", "superseded_by": "REQ-0002", "feature": "F-0001"})
write(root, "spec/research/FM-0001.yaml", {"id": "FM-0001", "type": "fault-manifest", "title": "a hidden oracle fault manifest", "status": "ACTIVE"})
shutil.copy(os.path.join(WT, "release", "capability-baseline", "repair-1", "ws01-12", "evidence", "bc-p2-51", "samples", "format-sample.oracle.json"),
            os.path.join(root, "qa-oracle.json"))
write(root, "spec/decisions/CIT-0901.yaml", {"id": "CIT-0901", "type": "cit", "title": "done change", "status": "ACTIVE", "cit_status": "COMMITTED", "targets": ["REQ-0001"]})
write(root, "spec/decisions/CIT-0902.yaml", {"id": "CIT-0902", "type": "cit", "title": "open change", "status": "ACTIVE", "cit_status": "PROPOSED", "targets": ["REQ-0001"]})
commit(root, "spec")
g.ok("task", "create", "--id", "TASK-0001", "--class", "implementation", "--objective", "t", "--feature", "F-0001", "--status", "READY", "--allowed", "src/**",
     "--fields", json.dumps({"requirements": ["REQ-0001"], "scenarios": ["SCN-0001"]}))
g.ok("task", "create", "--id", "TASK-0002", "--class", "implementation", "--objective", "t2", "--feature", "F-0001", "--status", "READY", "--allowed", "src/**",
     "--fields", json.dumps({"requirements": ["REQ-9999"], "scenarios": ["SCN-0001"]}))
commit(root, "tasks"); g.ok("rebuild-memory")
a = audit(g, "--no-persist")
fam = a.get("families", {})
check("SUITE.families", all(k in fam for k in ("lineage_orphans", "os_binding_integrity", "installation_authenticity", "contract_binding", "index_content_coverage", "task_contract_integrity")),
      "every round-2 reporting family runs in the full suite", sorted(k for k in fam))
check("SUITE.stale", any("TASK-0001" in m and "REQ-0001" in m and "stale lineage link" in m for m in msgs(a, "graph_integrity")), "graph_integrity names a stale lineage link (W8)")
check("SUITE.stale-cit", any("CIT-0902" in m for m in msgs(a, "graph_integrity")) and not any("CIT-0901" in m for m in msgs(a, "graph_integrity")),
      "an open CIT targeting a superseded record is stale; a committed CIT's targets are its change subjects, not stale links")
check("SUITE.delivery", any("TASK-0002" in m and "REQ-9999" in m for m in msgs(a, "context_reproducibility")), "context_reproducibility names a dispatchable task whose declared input is not delivered (W4)",
      msgs(a, "context_reproducibility"))
check("SUITE.hidden-oracle", any("FM-0001" in (f.get("path") or "") and f["severity"] == "high" for f in a.get("findings", []) if f.get("family") == "schema_invariants")
      and any("qa-oracle.json" in (f.get("path") or "") and f["severity"] == "high" for f in a.get("findings", []) if f.get("family") == "path_map_compliance"),
      "hidden-oracle material inside the governed repository is HIGH: a governed record (schema_invariants) and any other file (path_map_compliance) (Contract v3:1014, :1062)",
      [(f["family"], f.get("path")) for f in a.get("findings", []) if "oracle" in f["message"].lower()])
cb = fam.get("contract_binding", {}).get("detail", {})
check("SUITE.contract", cb.get("applicable") is True and cb.get("verdict") == "CONTRACT_SOURCE_BOUND", "contract_binding runs `gov contract verify` at G5 over the developer checkout", cb)
cov = fam.get("index_content_coverage", {}).get("detail", {})
check("SUITE.coverage", isinstance(cov.get("checked_artifacts"), int) and cov.get("checked_artifacts", 0) > 0, "index_content_coverage checks the whole live index", {k: cov.get(k) for k in ("checked_artifacts", "uncovered_lines", "complete")})
# a mutated contract chain in a checkout -> HIGH
mir = os.path.join(SCR, "contract-mirror-" + os.path.basename(root))
if not os.path.exists(mir):
    shutil.copytree(os.path.join(WT, "framework"), os.path.join(mir, "framework"))
    for rel in ("Governance_OS_Capability_Acceptance_Contract_v3.md", "tests/governance/capability-evidence-map.yaml", "docs/generated/GOVERNANCE_CAPABILITY_ACCEPTANCE.md"):
        os.makedirs(os.path.dirname(os.path.join(mir, rel)) or mir, exist_ok=True)
        shutil.copy(os.path.join(WT, rel), os.path.join(mir, rel))
    gv = os.path.join(mir, "docs/generated/GOVERNANCE_CAPABILITY_ACCEPTANCE.md")
    t = open(gv).read(); open(gv, "w").write(t.replace("- [ ]", "- [x]", 1))
a = g.as_(env={"GOV_CANONICAL_ROOT": mir}).body("audit", "--no-persist", "--family", "contract_binding")[0]
check("SUITE.contract-mutated", any(f["severity"] == "high" and "CONTRACT_" in f["message"] for f in a.get("findings", [])), "a derived view that diverges from the owner source is a HIGH contract_binding finding",
      msgs(a)[:2])

log("\n==== SUMMARY ====")
for cid, ok in RESULTS:
    log(f"{cid}: {'PASS' if ok else 'FAIL'}")
log(f"total={len(RESULTS)} pass={sum(1 for r in RESULTS if r[1])} fail={sum(1 for r in RESULTS if not r[1])}")
