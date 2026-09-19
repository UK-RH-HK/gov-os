#!/usr/bin/env python3
"""P2-AR-0026 (WS-5, repair iteration 1, round 2) — supplementary builder probe. Builder REGRESSION evidence (Contract v3
O3), not acceptance evidence.

Drives a `gov` binary through its JSON CLI on disposable copies of fixtures/greenfield (each project gets its own HOME
and XDG_STATE_HOME; every GOV_* variable is stripped) and prints one line per check:
    CHECK <id> PASS|FAIL <statement> -- <detail>
Run it against this round's binary and against the round-2 base binary (the integrated round-1 tree) as the negative
control: a check that also passes on the base is marked (control) in its statement.

Human answers come through WS-3's owner channel with the published TEST-MATERIAL signer
(repair-1/ws03/evidence/hc_owner.py, seed 7), as the certification helpers do.

Usage:  GOV_BIN=<gov> PROBE_SCRATCH=<dir> python3 ws05_r2_supplementary.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
GOV = os.environ.get("GOV_BIN", os.path.join(WT, "target", "release", "gov"))
SCR = os.environ.get("PROBE_SCRATCH") or tempfile.mkdtemp(prefix="p2ar0026-supp-")
HC = os.path.join(WT, "release", "capability-baseline", "repair-1", "ws03", "evidence", "hc_owner.py")
RESULTS = []


def check(cid, ok, statement, detail=""):
    RESULTS.append((cid, bool(ok)))
    d = detail if isinstance(detail, str) else json.dumps(detail, sort_keys=True, default=str)
    print(f"CHECK {cid} {'PASS' if ok else 'FAIL'} {statement} -- {d[:900]}", flush=True)


class Gov:
    def __init__(self, root, home, role="orchestrator", session="S-supp"):
        self.root, self.home, self.role, self.session = root, home, role, session

    def as_(self, role=None, session=None):
        return Gov(self.root, self.home, role or self.role, session or self.session)

    def run(self, *args):
        env = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
        env.update({"HOME": self.home, "XDG_STATE_HOME": os.path.join(self.home, "state")})
        cmd = [GOV, "--json", "--root", self.root, "--role", self.role, "--session", self.session, *args]
        p = subprocess.run(cmd, capture_output=True, text=True, env=env)
        try:
            v = json.loads(p.stdout.strip())
        except Exception:
            v = {"ok": False, "error": {"code": "NO_JSON", "message": (p.stdout + p.stderr)[-600:]}}
        return v

    def ok(self, *args):
        v = self.run(*args)
        if not v.get("ok"):
            raise RuntimeError(f"gov {' '.join(args)} failed: {json.dumps(v.get('error'))[:1500]}")
        return v["result"]


def code(v):
    return (v.get("error") or {}).get("code")


def git(root, *a):
    subprocess.run(["git", "-C", root, *a], capture_output=True)


def commit(root, msg):
    git(root, "add", "-A")
    git(root, "commit", "-qm", msg)


def write(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(text)


def wy(root, rel, d):
    write(root, rel, json.dumps(d, indent=1) + "\n")


def ry(root, rel):
    import yaml
    return yaml.safe_load(open(os.path.join(root, rel)))


def project(tag):
    base = os.path.join(SCR, f"{tag}-{uuid.uuid4().hex[:6]}")
    root, home = os.path.join(base, "proj"), os.path.join(base, "home")
    os.makedirs(home)
    shutil.copytree(os.path.join(WT, "fixtures", "greenfield", "project"), root)
    git(root, "init", "-q")
    git(root, "config", "user.email", "supp@example.invalid")
    git(root, "config", "user.name", "supp")
    commit(root, "fixture")
    g = Gov(root, home)
    g.ok("init", "--name", tag, "--alias", f"a-{tag}")
    commit(root, "init")
    return root, g


def dag(g):
    return g.ok("task", "dag")


def runnable(g, t):
    return t in dag(g)["runnable"]


def reasons(g, t):
    d = dag(g)
    return json.dumps([b for k in ("blocked", "waiting_human") for b in d[k] if b["task"] == t])


PACKAGE = {"why_now": "the next task depends on this choice", "current_state": "two options analysed, none chosen",
           "options": [{"id": "A", "description": "proceed as proposed"}, {"id": "B", "description": "do not proceed"}],
           "impact": "the dependent tasks are re-planned", "reversibility": "reversible: the change can be rolled back",
           "cost_rework": "one task of rework if reversed", "recommendation": "A", "confidence": 0.6, "impact_radius": "R3"}


def gate(g, q, extra=None):
    f = dict(PACKAGE)
    f.update(extra or {})
    return g.ok("gate", "create", "--question", q, "--fields", json.dumps(f))["id"]


def human_decide(g, gid, option):
    st = g.run("trust", "human-channel")
    if not ((st.get("result") or {}).get("available")):
        af = os.path.join(g.home, f"anchor-{uuid.uuid4().hex[:6]}.json")
        subprocess.run([sys.executable, HC, "anchor", af, "7"], check=True, capture_output=True)
        g.ok("trust", "human-channel", "--provision", af)
    r = g.ok("gate", "present", gid)["gate"]
    af = os.path.join(g.home, f"answer-{gid}-{uuid.uuid4().hex[:6]}.json")
    subprocess.run([sys.executable, HC, "answer", af, gid, r["gate_instance"], r["package_sha256"], option], check=True, capture_output=True)
    return g.ok("decide", gid, "--option", option, "--answer-file", af)


def receipt(g, root, task, name, files, tests="not_applicable_with_reason", extra=None):
    pk = g.ok("context", "compile", task)
    rc = pk.get("receipt_contract") or {}
    tr = rc.get("trace") or {}
    v = {"work_completed": "work done", "files_changed": files, "tests": {"status": tests, "reason": "probe"}, "outcome": "success", "evidence": [],
         "context_packet_hash": pk.get("packet_hash"), "inputs_consumed": [f"{e['id']}@{e['content_hash']}" for e in rc.get("acknowledge_inputs", [])],
         "outputs_produced": files, "requirements_implemented": tr.get("requirements", []), "scenarios_implemented": tr.get("scenarios", []),
         "features_implemented": tr.get("features", []), "decisions_applied": tr.get("decisions", []), "constraints_applied": tr.get("constraints", []),
         "acceptance_evidence": [{"test": t, "result": "passed", "evidence": "probe"} for t in rc.get("tests_requiring_evidence", [])],
         "deviations": [], "unresolved": []}
    v.update(extra or {})
    d = os.path.join(root, ".governance-runtime", "probe-reports")
    os.makedirs(d, exist_ok=True)
    f = os.path.join(d, name + ".json")
    json.dump(v, open(f, "w"))
    return f


def bare(root, name, files, tests="not_applicable_with_reason"):
    d = os.path.join(root, ".governance-runtime", "probe-reports")
    os.makedirs(d, exist_ok=True)
    f = os.path.join(d, name + ".json")
    json.dump({"work_completed": "work done", "files_changed": files, "tests": {"status": tests, "reason": "probe"}}, open(f, "w"))
    return f


def create(g, cls, obj, status="READY", allowed=None, fields=None):
    a = ["task", "create", "--class", cls, "--objective", obj, "--status", status, "--fields", json.dumps(fields or {})]
    if allowed:
        a += ["--allowed", allowed]
    return g.run(*a)


def section(name, fn):
    print(f"\n## {name}", flush=True)
    try:
        fn()
    except Exception as e:  # a section that cannot run reports it and the probe continues
        check(f"{name}.ran", False, "section ran to completion", f"{type(e).__name__}: {e}")


# ------------------------------------------------------------------------------------------------ A. BC-P2-16
def sec_a():
    root, g = project("a")
    t = create(g, "documentation", "needs REQ-0901", allowed="docs/**", fields={"requirements": ["REQ-0901"]})
    tr = t.get("result") or {}
    tid = tr.get("id")
    check("A1.create-READY-derived", t.get("ok") and tr.get("task_status") != "READY", "task create --status READY with an absent mandatory input is not stored READY", {"task_status": tr.get("task_status"), "reasons": (tr.get("ready_check") or {}).get("dag", {}).get("reasons")})
    v = g.run("task", "status", tid, "READY")
    check("A2.status-READY-refused", not v.get("ok"), "task status READY is refused while a mandatory input is absent", code(v))
    v = g.run("task", "claim", tid)
    check("A3.claim-refused", not v.get("ok"), "claim is refused while a mandatory input is absent", code(v))
    b = create(g, "documentation", "needs REQ-0902", status="BLOCKED", allowed="docs2/**", fields={"requirements": ["REQ-0902"]})["result"]["id"]
    rp = g.ok("task", "replan")
    check("A4.replan-no-promotion", not any(c["task"] in (tid, b) and c["to"] == "READY" for c in rp["changed"]), "replan does not promote a task whose mandatory input is absent (W3-r1-replan)", rp["changed"])
    wy(root, "spec/requirements/REQ-0901.yaml", {"id": "REQ-0901", "type": "requirement", "title": "docs", "status": "ACTIVE", "kind": "functional"})
    g.ok("task", "replan")
    v = g.run("task", "claim", tid)
    check("A5.input-provided-claimable", v.get("ok"), "(control) once the input exists the same task is claimable", code(v))
    d = create(g, "documentation", "plain", allowed="notes/**")["result"]["id"]
    g.ok("task", "status", d, "BLOCKED", "--note", "waiting on vendor")
    c = g.as_(session="S-other").ok("continue")
    check("A6.explicit-hold", not runnable(g, d) and c.get("task") != d, "a task held BLOCKED by `task status` is not runnable and `continue` does not offer it (X2-I4)", {"runnable": dag(g)["runnable"], "continue": c.get("task")})
    v = g.run("task", "status", d, "DONE")
    check("A7.done-only-by-close", not v.get("ok"), "task status DONE is refused (DONE only through an evidence-gated close)", code(v))
    m = create(g, "documentation", "depends on a missing task", status="DRAFT", allowed="misc/**", fields={"dependencies": ["TASK-9998"]})["result"]["id"]
    s = g.run("task", "status", m, "READY")
    cl = g.run("task", "claim", m)
    check("A8.missing-dependency-no-bypass", not s.get("ok") and not cl.get("ok"), "a missing task dependency cannot be bypassed by `task status READY` + claim (W3-r1 bypass)", {"status": code(s), "claim": code(cl)})


# ------------------------------------------------------------------------------------------------ B. BC-P2-12
def sec_b():
    root, g = project("b")
    t1 = create(g, "discovery", "t1", allowed="notes/a/**")["result"]["id"]
    g1 = gate(g, "May t1 proceed?", {"blocks_tasks": [t1]})
    check("B1.pending-not-claimable", not g.run("task", "claim", t1).get("ok") and t1 in json.dumps(dag(g)["waiting_human"]), "(control) a task behind a pending gate waits and is not claimable", reasons(g, t1))
    human_decide(g, g1, "B")
    check("B2.declined-blocks", not runnable(g, t1), "a task whose gate was answered with a non-authorising option is not runnable (L3.b4.t2)", reasons(g, t1))
    t2 = create(g, "discovery", "t2", allowed="notes/b/**")["result"]["id"]
    g2 = gate(g, "May t2 proceed?", {"blocks_tasks": [t2]})
    human_decide(g, g2, "A")
    ok_auth = runnable(g, t2)
    g.ok("gate", "revoke", g2, "--reason", "withdrawn")
    check("B3.revoked-blocks", ok_auth and not runnable(g, t2), "an authorising answer releases the task; revoking it blocks the task again (L3.b4.t3)", reasons(g, t2))
    t4 = create(g, "discovery", "t4", allowed="notes/d/**")["result"]["id"]
    rec = ry(root, f"spec/tasks/{t4}.yaml")
    rec["human_gate"] = "HDG-9999"
    rec["task_status"] = "WAITING_HUMAN"
    wy(root, f"spec/tasks/{t4}.yaml", rec)
    check("B4.missing-gate-blocks", not runnable(g, t4), "a task referencing a gate that does not exist is not runnable (L3.b4.t5)", reasons(g, t4))
    t5 = create(g, "discovery", "t5", allowed="notes/e/**")["result"]["id"]
    gate(g, "May t5 proceed?", {"blocks_tasks": [t5]})
    rec = ry(root, f"spec/tasks/{t5}.yaml")
    rec.pop("human_gate", None)
    rec["task_status"] = "READY"
    wy(root, f"spec/tasks/{t5}.yaml", rec)
    check("B5.field-removal-does-not-release", not runnable(g, t5) and not g.run("task", "claim", t5).get("ok"), "removing `human_gate` from the task record does not release it: the OS-written gate names the task", reasons(g, t5))
    t6 = create(g, "discovery", "t6", allowed="notes/f/**")["result"]["id"]
    g.ok("task", "claim", t6)
    g6 = gate(g, "Is it safe to continue t6?", {"blocks_tasks": [t6]})
    write(root, "notes/f/out.txt", "work\n")
    g.ok("rebuild-memory", "--incremental")
    rep = receipt(g, root, t6, "t6", ["notes/f/out.txt"])
    v1 = g.run("task", "close", t6, "--report", rep)
    v2 = g.run("task", "close", t6, "--report", rep, "--force")
    check("B6.close-refused-while-gated", not v1.get("ok") and not v2.get("ok"), "a task whose blocking gate is pending cannot be closed, not even with --force (L3s.1)", {"close": code(v1), "force": code(v2)})
    human_decide(g, g6, "A")
    g.ok("rebuild-memory", "--incremental")
    v3 = g.run("task", "close", t6, "--report", receipt(g, root, t6, "t6b", ["notes/f/out.txt"]))
    check("B7.authorised-closes", v3.get("ok"), "(control) after an authorising answer the close proceeds", code(v3))


# ------------------------------------------------------------------------------------------------ C. BC-P2-09 close side
def sec_c():
    root, g = project("c")
    w = g.as_(role="backend-engineer", session="S-worker")
    t = create(g, "discovery", "worker task", allowed="notes/**")["result"]["id"]
    w.ok("task", "claim", t)
    gid = gate(g, "An unrelated question")
    gp = f"spec/decisions/{gid}.yaml"
    original = open(os.path.join(root, gp)).read()
    gd = ry(root, gp)
    gd.update({"gate_status": "ANSWERED", "presented_in_chat": True, "answer": {"option": "A", "by": "owner", "by_kind": "human", "acting_role": "human", "at": "2026-09-19T00:00:00Z", "rationale": "forged"}})
    wy(root, gp, gd)
    wy(root, "spec/decisions/D-0901.yaml", {"id": "D-0901", "type": "decision", "title": "forged", "status": "ACTIVE", "chosen_option": "A", "human_approved": True, "approved_by_kind": "human", "derived_from": [gid], "state_class": "AUTHORITATIVE"})
    write(root, "notes/work.txt", "worker output\n")
    w.ok("rebuild-memory", "--incremental")
    v = w.run("task", "close", t, "--report", receipt(w, root, t, "c2", ["notes/work.txt", gp, "spec/decisions/D-0901.yaml"]))
    check("C2.declared-forgery-refused", not v.get("ok"), "(control) declaring the forged records does not make them the worker's to write", code(v))
    v = w.run("task", "close", t, "--report", receipt(w, root, t, "c1", ["notes/work.txt"]))
    det = json.dumps(v.get("error"))
    check("C1.forged-t2-refused", not v.get("ok") and gid in det and "D-0901" in det, "a worker's hand-written gate answer and gate-derived decision inside its task are observed and refused at close (X2-E1xG2, L3.b5.9)", {"code": code(v), "t2": ((v.get("error") or {}).get("details") or {}).get("t2_violations")})
    open(os.path.join(root, gp), "w").write(original)
    os.remove(os.path.join(root, "spec/decisions/D-0901.yaml"))
    w.ok("rebuild-memory", "--incremental")
    v = w.run("task", "close", t, "--report", receipt(w, root, t, "c3", ["notes/work.txt"]))
    check("C3.os-writes-not-attributed", v.get("ok"), "(control) the OS's own sealed gate written inside the window is not attributed to the worker", code(v))
    commit(root, "first closed")
    t2 = create(g, "discovery", "second", allowed="notes/**")["result"]["id"]
    w.ok("task", "claim", t2)
    wy(root, "spec/reports/RPT-0901.yaml", {"id": "RPT-0901", "type": "report", "title": "forged close", "status": "ACTIVE", "task": t2, "work_completed": "x", "tests": {"status": "passed"}})
    write(root, "notes/second.txt", "x\n")
    w.ok("rebuild-memory", "--incremental")
    rep = receipt(w, root, t2, "c4", ["notes/second.txt"])
    v = w.run("task", "close", t2, "--report", rep)
    check("C4.forged-report-refused", not v.get("ok") and "RPT-0901" in json.dumps(v.get("error")), "a hand-written close report is observed and refused", code(v))
    os.remove(os.path.join(root, "spec/reports/RPT-0901.yaml"))
    base = os.path.join(root, ".governance-runtime", "tasks", t2, "claim-tree.json")
    doc = json.load(open(base))
    doc["files"]["notes/second.txt"] = "0" * 64
    json.dump(doc, open(base, "w"))
    w.ok("rebuild-memory", "--incremental")
    v = w.run("task", "close", t2, "--report", rep)
    check("C5.baseline-tamper-refused", not v.get("ok"), "a rewritten claim baseline (hiding a change) is refused", code(v))


# ------------------------------------------------------------------------------------------------ D. BC-P2-20
def sec_d():
    root, g = project("d")
    for rid, d in (("REQ-0300", {"id": "REQ-0300", "type": "requirement", "title": "r", "status": "ACTIVE", "kind": "functional"}),
                   ("SCN-0300", {"id": "SCN-0300", "type": "scenario", "title": "s", "status": "ACTIVE", "actor": "c", "given": ["a"], "when": ["b"], "then": ["c"], "success_criteria": ["x"], "failure_criteria": ["y"]}),
                   ("TST-0300", {"id": "TST-0300", "type": "test-obligation", "title": "t", "status": "ACTIVE", "family": "unit", "scenario": "SCN-0300"})):
        wy(root, {"REQ": "spec/requirements", "SCN": "spec/scenarios", "TST": "spec/tasks"}[rid[:3]] + f"/{rid}.yaml", d)
    commit(root, "inputs")
    g.ok("rebuild-memory", "--incremental")
    fields = {"requirements": ["REQ-0300"], "scenarios": ["SCN-0300"], "acceptance_tests": ["TST-0300"]}
    d1 = create(g, "documentation", "notes", allowed="notes/**")["result"]["id"]
    g.ok("task", "claim", d1)
    write(root, "notes/d1.md", "notes\n")
    g.ok("rebuild-memory", "--incremental")
    v = g.run("task", "close", d1, "--report", bare(root, "d1", ["notes/d1.md"]))
    check("D1.bare-report-refused", not v.get("ok"), "a bare report (no packet, no consumed inputs, no deviations/unknowns) is refused (W5-c1/r6)", code(v))
    x = create(g, "implementation", "implement", allowed="src/**", fields=fields)["result"]["id"]
    g.ok("task", "claim", x)
    write(root, "src/lib.rs", open(os.path.join(root, "src/lib.rs")).read() + "\npub fn supp_d() -> i64 { 1 }\n")
    g.ok("rebuild-memory", "--incremental")
    v = g.run("task", "close", x, "--report", receipt(g, root, x, "d2", ["src/lib.rs"], extra={"requirements_implemented": ["REQ-9999"]}))
    check("D2.fabricated-trace-refused", not v.get("ok"), "a receipt naming a requirement that does not exist is refused (W5-r3r4)", code(v))
    z = create(g, "implementation", "tests for totals", allowed="tests/**", fields=fields)["result"]["id"]
    g.ok("task", "claim", z)
    write(root, "tests/supp_d3.rs", "#[test] fn d3() {}\n")
    g.ok("rebuild-memory", "--incremental")
    wr = json.load(open(receipt(g, root, z, "d3", ["tests/supp_d3.rs"])))
    wr.pop("outcome")
    wr.update({"task": z, "status": "success", "discoveries": [], "risks": [], "lessons": [], "proposed_decisions": [], "recommended_next_action": "close"})
    f = os.path.join(root, ".governance-runtime", "probe-reports", "d3-worker-return.json")
    json.dump(wr, open(f, "w"))
    v = g.run("task", "close", z, "--report", f)
    check("D3.worker-return-is-the-receipt", v.get("ok"), "a worker return in the worker-return shape (status: success) carrying the receipt closes the task (X2-N4xW5)", code(v) or v.get("result", {}).get("receipt_validation"))
    if v.get("ok"):
        rpt = ry(root, f"spec/reports/{v['result']['report']}.yaml")
        tr = ry(root, f"spec/tasks/{z}.yaml")
        check("D4.receipt-persisted", rpt.get("requirements_implemented") == ["REQ-0300"] and rpt.get("inputs_consumed") and tr.get("outputs_produced") == ["tests/supp_d3.rs"] and isinstance(rpt.get("os_binding"), dict),
              "the receipt is persisted on the sealed report and the task records what it produced (task -> output edge)", {"report_keys": sorted(rpt.keys()), "outputs_produced": tr.get("outputs_produced")})


# ------------------------------------------------------------------------------------------------ E. BC-P2-34 task side
def sec_e():
    root, g = project("e")
    rd = {k: "PRESENT" for k in ["intent_outcome", "user_actor", "journey_workflow", "scenarios", "inputs", "data_model_schema", "representative_test_data", "processing_algorithm",
                                  "expected_outputs", "functional_requirements", "non_functional_requirements", "backend_service_behaviour", "database_state_requirements",
                                  "interface_api_event_contracts", "security_privacy", "integrations", "devops_runtime", "observability", "performance_capacity",
                                  "recovery_fallback", "success_criteria", "failure_criteria", "independent_acceptance_tests", "documentation_operations"]}
    rd.update({"ux_interactions": {"status": "N/A_WITH_REASON", "reason": "library crate"}, "cost_constraints": {"status": "N/A_WITH_REASON", "reason": "no infra"}})
    wy(root, "spec/features/F-0200.yaml", {"id": "F-0200", "type": "feature", "title": "Totals", "status": "ACTIVE", "capability_category": "backend", "requirements": ["REQ-0200"], "scenarios": ["SCN-0200"], "acceptance_tests": ["TST-0200"], "readiness": rd})
    wy(root, "spec/requirements/REQ-0200.yaml", {"id": "REQ-0200", "type": "requirement", "title": "exact", "status": "ACTIVE", "feature": "F-0200", "kind": "functional"})
    wy(root, "spec/scenarios/SCN-0200.yaml", {"id": "SCN-0200", "type": "scenario", "title": "two orders", "status": "ACTIVE", "feature": "F-0200", "actor": "c", "given": ["a"], "when": ["b"], "then": ["c"], "success_criteria": ["x"], "failure_criteria": ["y"]})
    tst = {"id": "TST-0200", "type": "test-obligation", "title": "acceptance", "status": "ACTIVE", "feature": "F-0200", "scenario": "SCN-0200", "family": "acceptance", "author_role": "independent-test-designer", "independent_of_implementer": True}
    wy(root, "spec/tasks/TST-0200.yaml", tst)
    commit(root, "feature")
    g.ok("rebuild-memory", "--incremental")
    imp = create(g, "implementation", "implement", allowed="src/**", fields={"feature": "F-0200", "requirements": ["REQ-0200"], "scenarios": ["SCN-0200"], "role": "backend-engineer"})["result"]["id"]
    check("E1.self-declared-independence-rejected", not runnable(g, imp), "an acceptance obligation that only declares itself independent does not satisfy TEST_POLICY independence (E1.b4.b)", reasons(g, imp))
    td = create(g, "test-design", "independent tests", allowed="spec/**", fields={"feature": "F-0200", "role": "independent-test-designer"})["result"]["id"]
    des = g.as_(role="independent-test-designer", session="S-td")
    des.ok("task", "claim", td)
    tst2 = dict(tst, test_path="tests/ledger_test.rs")
    wy(root, "spec/tasks/TST-0200.yaml", tst2)
    des.ok("rebuild-memory", "--incremental")
    des.ok("task", "close", td, "--report", receipt(des, root, td, "td", ["spec/tasks/TST-0200.yaml"]))
    g.ok("task", "replan")
    check("E2.recorded-authorship-satisfies", runnable(g, imp), "(control) an obligation produced by a test-design task closed by an independent role and session satisfies it", reasons(g, imp))
    v = g.as_(role="backend-engineer", session="S-td").run("task", "claim", imp)
    check("E3.author-session-cannot-implement", not v.get("ok"), "the session that authored the independent tests cannot claim the implementation, whatever role it declares", code(v))
    wy(root, "spec/data/TD-0200.yaml", {"id": "TD-0200", "type": "data", "title": "orders", "status": "ACTIVE", "author_role": "backend-engineer"})
    wy(root, "spec/tasks/TST-0200.yaml", dict(tst2, data_provenance="TD-0200 (synthetic)"))
    check("E4.implementer-test-data-blocks", not runnable(g, imp) and "TD-0200" in reasons(g, imp), "test data authored by the implementer's role blocks the implementation (H4.b2)", reasons(g, imp))
    root2, g2 = project("e5")
    wy(root2, "spec/features/F-0001.yaml", {"id": "F-0001", "type": "feature", "title": "Totals", "status": "ACTIVE", "capability_category": "backend", "readiness": {}})
    plan = g2.ok("readiness", "plan", "F-0001")
    roles = {g2.ok("task", "show", x).get("readiness_cell"): g2.ok("task", "show", x).get("role") for x in plan["created_tasks"]}
    # a feature that still lacks the requirement and scenario it lists: the gap work that writes them can start and
    # complete (it does not consume what it produces); implementation of the feature stays blocked until they exist
    wy(root2, "spec/features/F-0009.yaml", {"id": "F-0009", "type": "feature", "title": "Refunds", "status": "ACTIVE", "capability_category": "backend", "requirements": ["REQ-0999"], "scenarios": ["SCN-0999"], "readiness": {}})
    plan9 = g2.ok("readiness", "plan", "F-0009")
    gap = {g2.ok("task", "show", x)["readiness_cell"]: x for x in plan9["created_tasks"]}
    scn = gap.get("scenarios")
    cl9 = None
    if scn and runnable(g2, scn):
        g2.ok("task", "claim", scn)
        wy(root2, "spec/scenarios/SCN-0999.yaml", {"id": "SCN-0999", "type": "scenario", "title": "refund", "status": "ACTIVE", "feature": "F-0009", "actor": "clerk", "given": ["a"], "when": ["b"], "then": ["c"], "success_criteria": ["x"], "failure_criteria": ["y"]})
        g2.ok("rebuild-memory", "--incremental")
        cl9 = g2.run("task", "close", scn, "--report", receipt(g2, root2, scn, "e6", ["spec/scenarios/SCN-0999.yaml"]))
    imp9 = create(g2, "implementation", "refunds", allowed="src/**", fields={"feature": "F-0009"})["result"]["id"]
    # the gap task starts, and its receipt is accepted; the close itself may still be refused by the governance-suite
    # currency gate (WS-2), which requires a GREEN suite while the feature's dangling references keep it DEGRADED —
    # reported as an observation for WS-2, not a WS-5 refusal
    check("E6.gap-work-can-start-and-its-receipt-is-accepted", scn is not None and cl9 is not None and code(cl9) != "RECEIPT_INVALID" and not runnable(g2, imp9),
          "(control) readiness gap work for a feature that still lacks the inputs it lists can start and its receipt is accepted, while the feature's implementation stays blocked (no DAG/receipt planning deadlock)",
          {"scenarios_gap_task": scn, "close": (code(cl9) or "ok") if cl9 else "not reached", "impl_reasons": reasons(g2, imp9)})
    check("E5.planner-designates-independent-roles", roles.get("independent_acceptance_tests") == "independent-test-designer" and roles.get("representative_test_data") == "data-author",
          "the readiness planner's independent-test and test-data gap tasks designate independent roles", {k: v for k, v in roles.items() if v})


# ------------------------------------------------------------------------------------------------ F/G/H/I/J. integration points
def sec_f():
    root, g = project("f")
    t = create(g, "documentation", "d", allowed="docs/**")["result"]["id"]
    g.ok("task", "claim", t)
    pol = os.path.join(root, "governance/kernel/policies/BUDGET_POLICY.yaml")
    orig = open(pol).read()
    open(pol, "a").write("\n# tampered\n")
    v = g.run("task", "release", t)
    open(pol, "w").write(orig)
    check("F1.release-guarded", not v.get("ok"), "task release passes the write guard (kernel trust / §6 allow-list / controls): refused on a tampered kernel (WS-5 IP-4)", code(v))


def sec_g():
    root, g = project("g")
    st = g.ok("status")
    check("G1.status-health", isinstance((st.get("health") or {}).get("state"), str), "gov status reports the health state (IP-WS02-04)", st.get("health", {}).get("state"))
    check("G2.status-release-trust-this-project", "this project" in str((st.get("release_trust") or {}).get("scope")), "gov status reports this project's installation's release trust (WS-8 IP-4)", st.get("release_trust"))
    gate(g, "approve?")
    mf = os.path.join(root, ".governance-runtime", "g3.json")
    json.dump([{"op": "write_file", "path": "docs/g3.md", "content": "x\n"}], open(mf, "w"))
    c = g.ok("cit", "propose", "--proposal", "document", "--trigger", "governance_change", "--manifest", mf)
    g.run("cit", "simulate", c["id"])
    it = g.ok("intent", "approve it")
    check("G3.no-human-identity-proposed", not any("--by human" in c for c in it.get("commands", [])), "the intent router proposes no command asserting a human identity (L3s.2)", it.get("commands"))


def sec_h():
    root, g = project("h")
    t = create(g, "documentation", "before", allowed="docs/**")["result"]["id"]
    ov = os.path.join(root, "governance/project/PROJECT_POLICY.yaml")
    import yaml
    d = yaml.safe_load(open(ov)) or {}
    d["policy_overrides"] = {"AUTHORITY_POLICY.authority_levels_required.create_task": "L0"}
    yaml.safe_dump(d, open(ov, "w"))
    g.run("doctor")
    c = create(g, "documentation", "while weakened", allowed="notes/**")
    cl = g.run("task", "claim", t)
    check("H1.hard-block-refuses-create-and-claim", not c.get("ok") and not cl.get("ok") and code(c) == "HEALTH_HARD_BLOCK", "an active health hard-block refuses task create and claim (IP-WS02-02/03)", {"create": code(c), "claim": code(cl)})


def sec_i():
    root, g = project("i")
    t = create(g, "documentation", "docs", allowed="docs/**")["result"]["id"]
    g.ok("task", "claim", t)
    write(root, "docs/x.md", "x\n")
    g.ok("rebuild-memory", "--incremental")
    v = g.run("task", "close", t, "--report", receipt(g, root, t, "i1", ["docs/x.md"], tests="passed"))
    check("I1.passed-needs-recorded-evidence", not v.get("ok") and str(code(v)).startswith("PRODUCT_TEST"), "a close claiming tests passed without recorded product-test evidence is refused (BC-P2-43 at close, IP-WS02-01)", code(v))


def sec_j():
    root, g = project("j")
    t = create(g, "documentation", "src work", allowed="src/**")["result"]["id"]
    g.as_(session="S-live").ok("task", "claim", t)
    g.ok("rebuild-memory", "--incremental")
    au = g.run("audit", "--no-persist")
    r = au.get("result") or (au.get("error") or {}).get("details") or {}
    scen = [f["message"][:160] for f in r.get("findings", []) if f.get("family") == "skill_regression" and "FAILED" in f.get("message", "")]
    check("J1.sandbox-claims-hermetic", not scen, "a live claim in the project does not make the sandboxed skill scenarios fail (a copied claims store is not the store)", {"verdict": r.get("verdict"), "failed_scenarios": scen})


for name, fn in (("A", sec_a), ("B", sec_b), ("C", sec_c), ("D", sec_d), ("E", sec_e), ("F", sec_f), ("G", sec_g), ("H", sec_h), ("I", sec_i), ("J", sec_j)):
    section(name, fn)
f = [i for i, ok in RESULTS if not ok]
print(f"\nSUMMARY total={len(RESULTS)} pass={len(RESULTS) - len(f)} fail={len(f)} failed={f}")
