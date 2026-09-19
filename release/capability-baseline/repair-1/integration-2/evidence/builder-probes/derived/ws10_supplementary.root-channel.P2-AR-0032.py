#!/usr/bin/env python3
# DERIVED COPY (P2-AR-0032, round-2 integration builder) of
#   release/capability-baseline/repair-1/r2-ws10/evidence/probes/ws10_supplementary.py (P2-AR-0031, WS-10).
# ORIGINAL-PROBE-ID: ws10-r2-supplementary
# Changes, and nothing else:
#  (1) WT is resolved from this copy's location (same worktree, one directory deeper);
#  (2) human_decide(): P2-ADJ-0001 (WS-3, merged) turned the standalone human-gate anchor off, so instead of
#      provisioning one the machine is provisioned with the throw-away root that delegates `human-gate` to the same
#      test owner key and the installed kernel is re-verified (p2ar0032_root_channel.provision, WS-3's own method);
#  (3) WS10-J1-8 fixture: WS-6 (P2-AR-0027, BC-P2-30) made `memory select` the governed change — the first call raises
#      the R5 change gate and applies nothing; the owner answers it and the same select runs with --gate. The line's
#      check and PASS criterion are unchanged.
# Every other check, its scenario and its PASS criterion are P2-AR-0031's.
"""P2-AR-0031 (WS-10, repair iteration 1 round 2) — builder regression probe for BC-P2-46/47/48.

REGRESSION EVIDENCE ONLY (Contract v3 O3): written by the builder, never an acceptance test. Every check drives the
`gov` binary through its CLI JSON contract on a disposable project (its own machine state via XDG_STATE_HOME), and
prints `CHECK <id> PASS|FAIL <statement>` plus a detail line, then a SUMMARY. Run it against the base binary as the
negative control.

Human answers are owner-signed with WS-3's TEST-MATERIAL reference signer (repair-1/ws03/evidence/hc_owner.py, a
published seed: its keys are public and fit for tests only); the anchor is provisioned from outside the repository.

Environment: GOV_BIN (the gov binary), PROBE_SCRATCH (a directory for disposable projects).
Run:  GOV_BIN=<gov> PROBE_SCRATCH=<dir> python3 ws10_supplementary.py
"""
import json
import os
import subprocess
import sys
import tempfile
import uuid

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, *[".."] * 7))  # (1)
sys.path.insert(0, HERE)
import p2ar0032_root_channel  # noqa: E402  (2)
GOV = os.environ.get("GOV_BIN", os.path.join(WT, "target", "release", "gov"))
SCRATCH = os.environ.get("PROBE_SCRATCH", os.path.join(tempfile.gettempdir(), "p2-ar-0031-probes"))
HCO = os.path.join(WT, "release", "capability-baseline", "repair-1", "ws03", "evidence", "hc_owner.py")
RESULTS = []
PKG = {"why_now": "the next step depends on it", "current_state": "analysed", "impact": "dependent work is re-planned",
       "reversibility": "reversible: roll back", "cost_rework": "one task", "recommendation": "A", "confidence": 0.6,
       "impact_radius": "R2"}
COMPLETE_RES = {"question": "Is gateway X faster?", "reason": "choose a payment gateway", "method": "A/B on staging for one day",
                "sources": ["staging request logs 2026-09-01"], "measurements": {"p95_ms": {"X": 18, "Y": 40}},
                "uncertainty": "one day of traffic; weekday only", "conclusion": "X is faster at p95", "confidence": 0.7}


def check(cid, ok, statement, detail=None):
    RESULTS.append((cid, bool(ok)))
    print(f"CHECK {cid} {'PASS' if ok else 'FAIL'} {statement}", flush=True)
    if detail is not None:
        print("      detail: " + (detail if isinstance(detail, str) else json.dumps(detail, sort_keys=True, default=str)[:1500]), flush=True)


class Proj:
    def __init__(self, name):
        os.makedirs(SCRATCH, exist_ok=True)
        self.base = tempfile.mkdtemp(prefix=f"{name}-", dir=SCRATCH)
        self.root = os.path.join(self.base, "proj")
        self.state = os.path.join(self.base, "state")
        os.makedirs(self.root)
        os.makedirs(self.state)
        self.session = "S-main"
        self.git("init", "-q", ".")
        self.git("config", "user.email", "probe@example.invalid")
        self.git("config", "user.name", "probe")
        r = self.run(["init", "--name", name])
        assert r["ok"], r
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "init")
        print(f"# project {self.root}", flush=True)

    def env(self):
        e = dict(os.environ)
        for k in list(e):
            if k.startswith("GOV_"):
                e.pop(k)
        e["XDG_STATE_HOME"] = self.state
        return e

    def git(self, *a):
        return subprocess.run(["git", *a], cwd=self.root, capture_output=True, text=True)

    def run(self, args, role="orchestrator", session=None):
        cmd = [GOV, "--json", "--root", self.root, "--session", session or self.session]
        if role:
            cmd += ["--role", role]
        cmd += [str(a) for a in args]
        p = subprocess.run(cmd, cwd=self.root, capture_output=True, text=True, env=self.env())
        try:
            v = json.loads(p.stdout)
        except Exception:
            v = {"ok": False, "error": {"code": "NO_JSON", "message": (p.stderr or p.stdout)[-800:]}}
        v["_exit"] = p.returncode
        shown = " ".join(a if " " not in a else repr(a) for a in [str(x) for x in args])
        print(f"$ gov{' --role ' + role if role else ''} --session {session or self.session} {shown[:300]}", flush=True)
        print("  -> ok" if v.get("ok") else f"  -> ERROR [{(v.get('error') or {}).get('code')}] {str((v.get('error') or {}).get('message'))[:400]}", flush=True)
        return v

    def res(self, args, **kw):
        v = self.run(args, **kw)
        return v.get("result") if v.get("ok") else None

    def code(self, v):
        return None if v.get("ok") else (v.get("error") or {}).get("code")

    def path(self, rel):
        return os.path.join(self.root, rel)

    def write(self, rel, text):
        os.makedirs(os.path.dirname(self.path(rel)), exist_ok=True)
        with open(self.path(rel), "w") as f:
            f.write(text)

    def put(self, rel, data):
        self.write(rel, yaml.safe_dump(data, sort_keys=False))

    def load(self, rel):
        with open(self.path(rel)) as f:
            return yaml.safe_load(f)

    def jfile(self, name, obj):
        p = os.path.join(self.base, f"{name}-{uuid.uuid4().hex[:6]}.json")
        with open(p, "w") as f:
            json.dump(obj, f)
        return p

    def gate(self, question, derived_from=None, extra=None):
        f = dict(PKG, options=[{"id": "A", "description": "yes"}, {"id": "B", "description": "no"}])
        if derived_from:
            f["derived_from"] = [x for x in derived_from if x]
        f.update(extra or {})
        r = self.res(["gate", "create", "--question", question, "--fields", json.dumps(f)])
        return r["id"] if r else None

    def human_decide(self, gate, option="A"):
        """Render the package, have the owner (test-material key) sign an answer for it, relay it as orchestrator."""
        if not gate:
            return {"ok": False, "error": {"code": "NO_GATE"}}
        self.run(["gate", "present", gate])
        g = (self.res(["gate", "show", gate]) or {}).get("gate") or {}
        inst, sha = g.get("gate_instance"), (g.get("presentation") or {}).get("package_sha256")
        if not inst or not sha:
            return {"ok": False, "error": {"code": "GATE_NOT_RENDERED"}}
        p2ar0032_root_channel.provision(lambda *a: self.run(list(a)), self.root,  # (2)
                                        os.path.join(self.base, "admin-domain"))
        ans = os.path.join(self.base, f"answer-{gate}-{uuid.uuid4().hex[:6]}.json")
        subprocess.run([sys.executable, HCO, "answer", ans, gate, str(inst), str(sha), option], check=True, capture_output=True)
        return self.run(["decide", gate, "--option", option, "--answer-file", ans])

    def cit(self, tag, ops):
        """propose → (owner-answered gate if raised) → approve → execute; returns the execute envelope."""
        r = self.res(["cit", "propose", "--proposal", f"probe {tag}", "--manifest", self.jfile(f"m-{tag}", ops), "--trigger", "behaviour_change"])
        if not r:
            return {"ok": False, "error": {"code": "PROPOSE_FAILED"}}
        cid = r["id"]
        sim = r.get("simulation") or self.res(["cit", "simulate", cid]) or {}
        gid = sim.get("human_gate")
        if gid:
            self.human_decide(gid)
        a = self.run(["cit", "approve", cid])
        if not a.get("ok"):
            return a
        return self.run(["cit", "execute", cid])


def findings(v):
    return (v.get("result") or {}).get("findings") or [] if v.get("ok") else []


def has(fs, code, record=None):
    return any(f.get("code") == code and (record is None or f.get("record") == record) for f in fs)


def audit_findings(p):
    a = p.run(["audit", "--no-persist"])
    body = a.get("result") or (a.get("error") or {}).get("details") or {}
    return body.get("findings", [])


# ======================================================================================================== J1 research
print("\n## J1 — research becomes evidence", flush=True)
p = Proj("ws10-j1")
v = p.run(["research", "record", "--fields", json.dumps({"question": "Is X faster?", "conclusion": "yes"})])
check("WS10-J1-1.incomplete-refused", p.code(v) == "RESEARCH_INCOMPLETE" and "method" in json.dumps(v.get("error")),
      "recording research with only question+conclusion as governed evidence is refused, naming what is missing", v.get("error"))
r = p.res(["research", "record", "--fields", json.dumps(COMPLETE_RES)])
rid = (r or {}).get("research", {}).get("id")
show = p.res(["research", "show", rid]) if rid else None
check("WS10-J1-2.complete-is-governed-evidence",
      bool(show) and show["standing"]["standing"] == "GOVERNED_EVIDENCE" and show["research"]["state_class"] == "EVIDENCE"
      and show["research"]["research_state"] == "CONCLUDED" and show["t2"]["binding"] == "VERIFIED",
      "complete research is recorded CONCLUDED as EVIDENCE, OS-sealed (T2 VERIFIED)", show and {"standing": show["standing"], "t2": show["t2"]})
d = p.res(["research", "record", "--draft", "--fields", json.dumps({"question": "Should we shard?", "reason": "growth"})])
did = (d or {}).get("research", {}).get("id")
check("WS10-J1-3a.draft-reference-only", bool(d) and d["research"]["state_class"] == "NARRATIVE" and d["research"]["research_state"] == "FRAMED"
      and d["standing"]["standing"] == "REFERENCE_ONLY", "a draft is FRAMED and held reference-only (NARRATIVE), not citable", d and d["standing"])
v = p.run(["research", "record", "--draft", "--fields", json.dumps({"question": "q?", "state_class": "EVIDENCE"})])
check("WS10-J1-3b.draft-cannot-claim-evidence", p.code(v) == "RESEARCH_DRAFT_NOT_EVIDENCE", "a draft cannot be presented as EVIDENCE", v.get("error"))
u = p.res(["research", "update", did, "--fields", json.dumps({"method": "load test"})]) if did else None
c = p.res(["research", "conclude", did, "--fields", json.dumps({k: COMPLETE_RES[k] for k in ("sources", "measurements", "uncertainty", "conclusion", "confidence")})]) if did else None
check("WS10-J1-3c.draft-lifecycle", bool(u) and u["research"]["research_state"] == "IN_PROGRESS" and bool(c) and c["research"]["state_class"] == "EVIDENCE"
      and c["standing"]["standing"] == "GOVERNED_EVIDENCE", "FRAMED → IN_PROGRESS (method) → CONCLUDED (every J1 field) becomes EVIDENCE",
      {"update": u and u["research"]["research_state"], "conclude": c and c["standing"]})
v = p.run(["research", "conclude", did, "--fields", "{}"]) if did else {}
check("WS10-J1-3d.no-reconclude", p.code(v) == "RESEARCH_TRANSITION_INVALID", "concluded research is not concluded again (it is superseded by new research)", v.get("error"))
ex = p.cit("res-incomplete", [{"op": "append_record", "record": {"id": "RES-0100", "type": "research", "title": "Gateway latency study", "status": "ACTIVE",
                                                                 "question": "Is gateway X faster?", "conclusion": "Yes, X is faster.", "state_class": "EVIDENCE"}}])
check("WS10-J1-4a.cit-refuses-incomplete-evidence", not ex.get("ok"), "a CIT appending incomplete research as EVIDENCE is refused (schema)", ex.get("error") or ex.get("result"))
ex = p.cit("res-note", [{"op": "append_record", "record": {"id": "RES-0200", "type": "research", "title": "Shard note", "status": "ACTIVE",
                                                           "question": "Should we shard later?", "state_class": "NARRATIVE"}}])
check("WS10-J1-4b.cit-accepts-reference-note (control)", ex.get("ok"), "the same CIT path accepts an incomplete research note held reference-only (NARRATIVE)", ex.get("error") or (ex.get("result") or {}).get("cit_status"))
p.put("spec/research/RES-0101.yaml", {"id": "RES-0101", "type": "research", "title": "Unsupported claim", "status": "ACTIVE",
                                      "question": "Does caching help?", "conclusion": "Caching halves latency.", "state_class": "EVIDENCE"})
p.put("spec/research/RES-0102.yaml", {"id": "RES-0102", "type": "research", "title": "Question only", "status": "ACTIVE", "question": "Should we shard?"})
p.run(["rebuild-memory", "--incremental"])
af = audit_findings(p)
check("WS10-J1-5a.audit-schema-flags-incomplete", any("RES-0101" in f.get("message", "") for f in af) and any("RES-0102" in f.get("message", "") for f in af)
      and not any("RES-0200" in f.get("message", "") for f in af),
      "the governance suite (schema_invariants) flags hand-written incomplete research presented as evidence, not the reference-only note",
      [f["message"][:100] for f in af if "RES-" in f.get("message", "")][:6])
rc = p.run(["research", "check"])
check("WS10-J1-5b.research-check", has(findings(rc), "RESEARCH_INCOMPLETE_EVIDENCE", "RES-0101") and has(findings(rc), "RESEARCH_INCOMPLETE_EVIDENCE", "RES-0102")
      and not has(findings(rc), "RESEARCH_INCOMPLETE_EVIDENCE", "RES-0200"),
      "`gov research check` names each incomplete research record presented as evidence", [(f["code"], f["record"]) for f in findings(rc)])
g_bad = p.gate("Adopt caching?", derived_from=["RES-0101"])
p.human_decide(g_bad)
g_ok = p.gate("Adopt gateway X?", derived_from=[rid])
dec = (p.human_decide(g_ok).get("result") or {}).get("decision")
fs = findings(p.run(["research", "check"]))
bad = [f for f in fs if f["code"] == "RELIES_ON_UNGOVERNED_EVIDENCE"]
check("WS10-J1-6.decision-on-unsupported-research",
      any(f["record"] == g_bad and f["severity"] == "high" for f in bad) and any(f["record"].startswith("D-") and "RES-0101" in f["message"] for f in bad)
      and not any(rid in f["message"] for f in bad),
      "a gate and the decision taken on incomplete research are reported (high); a decision on governed research is not", [(f["severity"], f["record"], f["message"][:90]) for f in bad])
check("WS10-J1-7a.influence-not-recorded-detected", has(fs, "INFLUENCE_NOT_RECORDED", rid), "the research a decision relied on is reported until it records that decision", [(f["code"], f["record"]) for f in fs if f["code"].startswith("INFLUENCE")])
p.run(["research", "sync"])
s = p.res(["research", "show", rid]) or {}
check("WS10-J1-7b.influence-backlink", dec in ((s.get("research") or {}).get("influences") or []) and g_ok in s["research"]["influences"]
      and s["t2"]["binding"] == "VERIFIED" and not s["influences"]["not_recorded"],
      "after `gov research sync` the research records the gate and the decision it influenced, and stays OS-sealed", {"influences": s.get("influences"), "t2": s.get("t2")})
bm = p.res(["memory", "benchmark", "--candidate", "current", "--candidate", "builtin:128", "--record"])
brid = (bm or {}).get("research_record")
sel = p.res(["memory", "select", "builtin:128", "--research", brid]) if brid else None
if sel and sel.get("applied") is False and sel.get("human_gate"):  # (3)
    p.human_decide(sel["human_gate"], "A")
    sel = p.res(["memory", "select", "builtin:128", "--research", brid, "--gate", sel["human_gate"]])
p.run(["research", "sync"])
bs = p.res(["research", "show", brid]) if brid else {}
check("WS10-J1-8.benchmark-research-influence", bool(sel) and sel["decision"] in (((bs or {}).get("research") or {}).get("influences") or []),
      "the product's own research producer (memory benchmark → memory select): the decision is recorded as influenced once reconciled", {"decision": sel and sel["decision"], "influences": (bs or {}).get("influences")})
hs = p.res(["health", "skills", "--include-deferred", "--skill", "SKL-RESEARCH-BENCHMARK"])
v1 = [sc for x in ((hs or {}).get("detail") or {}).get("skills", []) if isinstance(x, dict) and x.get("skill") == "SKL-RESEARCH-BENCHMARK"
      for sc in x.get("scenarios", []) if sc.get("scenario") == "V1"]
met = bool(v1) and (v1[0].get("status") == "passed" or (v1[0].get("deferred_check") or {}).get("expectation_met") is True)
check("WS10-J1-9.skill-scenario-now-true", met,
      "SKL-RESEARCH-BENCHMARK V1's executable check (a research record without method fails schema validation) is true on this product (IP-WS02-21: WS-2 may now declare it executable)",
      v1[0] if v1 else hs)

# ======================================================================================================== J2 experiments
print("\n## J2 — experiment lifecycle", flush=True)
p = Proj("ws10-j2")
p.write("fixtures/traffic.csv", "t,ms\n1,40\n2,18\n")
p.git("add", "-A"); p.git("commit", "-q", "-m", "fx")
DESIGN = {"hypothesis": "an async client halves p95", "method": "replay one day of traffic", "inputs": [{"path": "fixtures/traffic.csv"}],
          "reproducibility": {"acceptance": {"mode": "tolerance", "relative": 0.05}}}
CONC = {"interpretation": "the async client helps at p95", "decision_influence": "supports adopting the async client", "confidence": 0.8,
        "reproducibility": {"procedure": "replay fixtures/traffic.csv with the harness", "environment": "staging, 4 vCPU"}}
v1 = p.run(["experiment", "design", "--fields", json.dumps({"title": "no design"})])
v2 = p.run(["experiment", "design", "--fields", json.dumps(dict(DESIGN, outputs=["product/**"]))])
v3 = p.run(["experiment", "design", "--fields", json.dumps(dict(DESIGN, production_merge_allowed=True))])
v4 = p.run(["experiment", "design", "--fields", json.dumps(dict(DESIGN, runs=[{"kind": "primary"}]))])
check("WS10-J2-1.design-refusals", [p.code(x) for x in (v1, v2, v3, v4)] == ["EXPERIMENT_DESIGN_INCOMPLETE", "EXPERIMENT_OUTPUT_IN_PRODUCTION", "PRODUCTION_MERGE_NOT_ALLOWED", "OS_OWNED_FIELD"],
      "a design without hypothesis/method/data, with output in production, asking to merge, or asserting OS-owned runs is refused", [p.code(x) for x in (v1, v2, v3, v4)])
e = p.res(["experiment", "design", "--fields", json.dumps(dict(DESIGN, outputs=["spec/experiments/EXP-0001/**"]))])
eid = (e or {}).get("experiment", {}).get("id")
v_early = p.run(["experiment", "conclude", eid, "--fields", json.dumps(CONC)])
run = p.res(["experiment", "run", eid, "--results", json.dumps({"p95_ms": 18.0})])
v_twice = p.run(["experiment", "run", eid, "--results", json.dumps({"p95_ms": 18.0})])
v_res = p.run(["experiment", "conclude", eid, "--fields", json.dumps(dict(CONC, results={"p95_ms": 1.0}))])
v_inc = p.run(["experiment", "conclude", eid, "--fields", json.dumps({"interpretation": "x"})])
cc = p.res(["experiment", "conclude", eid, "--fields", json.dumps(CONC)])
check("WS10-J2-2.transitions", p.code(v_early) == "EXPERIMENT_TRANSITION_INVALID" and bool(run) and run["run"]["inputs"][0]["sha256"]
      and p.code(v_twice) == "EXPERIMENT_ALREADY_RUN" and p.code(v_res) == "EXPERIMENT_DESIGN_FROZEN" and p.code(v_inc) == "EXPERIMENT_CONCLUSION_INCOMPLETE"
      and bool(cc) and cc["experiment"]["results"] == {"p95_ms": 18.0},
      "DESIGNED→CONCLUDED refused; the run binds its inputs by SHA-256; a second primary run refused; results cannot be asserted at conclusion (the run's are copied); an incomplete conclusion refused",
      {"early": p.code(v_early), "inputs": run and run["run"]["inputs"], "twice": p.code(v_twice), "results": p.code(v_res), "incomplete": p.code(v_inc)})
check("WS10-J2-3a.unreproduced-is-not-evidence", bool(cc) and cc["standing"]["standing"] == "IRREPRODUCIBLE" and cc["experiment"]["state_class"] == "NARRATIVE",
      "a concluded experiment nobody reproduced is not governed evidence (reproducibility UNVERIFIED)", cc and cc["standing"])
rp = p.res(["experiment", "reproduce", eid, "--results", json.dumps({"p95_ms": 18.6})], session="S-repro")
check("WS10-J2-3b.reproduced-under-tolerance", bool(rp) and rp["run"]["agrees"] and rp["run"]["independent"] and rp["reproducibility"]["status"] == "REPRODUCED"
      and rp["standing"]["standing"] == "GOVERNED_EVIDENCE",
      "an independent reproduction within the tolerance fixed at design makes it REPRODUCED and governed evidence", rp and {"run": rp["run"], "standing": rp["standing"]["standing"]})
# irreproducible: a second experiment whose reproduction disagrees
e2 = (p.res(["experiment", "design", "--fields", json.dumps(DESIGN)]) or {}).get("experiment", {}).get("id")
p.res(["experiment", "run", e2, "--results", json.dumps({"p95_ms": 18.0})])
p.res(["experiment", "conclude", e2, "--fields", json.dumps(CONC)])
bad = p.res(["experiment", "reproduce", e2, "--results", json.dumps({"p95_ms": 31.0})], session="S-repro")
later = p.res(["experiment", "reproduce", e2, "--results", json.dumps({"p95_ms": 18.0})], session="S-repro2")
g_ex = p.gate("Adopt the async client?", derived_from=[e2])
ck = findings(p.run(["experiment", "check"]))
check("WS10-J2-4.irreproducible-detected", bool(bad) and not bad["run"]["agrees"] and bad["reproducibility"]["status"] == "NOT_REPRODUCED"
      and bool(later) and later["reproducibility"]["status"] == "NOT_REPRODUCED" and has(ck, "EXPERIMENT_IRREPRODUCIBLE", e2)
      and any(f["code"] == "RELIES_ON_UNGOVERNED_EVIDENCE" and f["record"] == g_ex and f["severity"] == "high" for f in ck),
      "Gate J challenge 'irreproducible experiment': a disagreeing reproduction makes it NOT_REPRODUCED (a later agreeing run does not erase it), reported, and a gate relying on it is reported (high)",
      {"bad": bad and bad["run"].get("differences"), "later": later and later["reproducibility"], "findings": [(f["code"], f["record"]) for f in ck]})
p.write("fixtures/traffic.csv", "t,ms\n1,41\n2,18\n")
drift = p.res(["experiment", "show", eid]) or {}
p.write("fixtures/traffic.csv", "t,ms\n1,40\n2,18\n")
back = p.res(["experiment", "show", eid]) or {}
check("WS10-J2-5.input-drift", drift.get("standing", {}).get("standing") == "IRREPRODUCIBLE" and any("fixtures/traffic.csv" in x for x in drift["standing"]["reasons"])
      and back.get("standing", {}).get("standing") == "GOVERNED_EVIDENCE",
      "when an input the runs were bound to changes, the experiment is irreproducible from the tree as it stands; restoring the bytes restores it",
      {"drift": drift.get("standing"), "restored": back.get("standing", {}).get("standing")})
e3 = (p.res(["experiment", "design", "--fields", json.dumps(DESIGN)]) or {}).get("experiment", {}).get("id")
p.res(["experiment", "run", e3, "--results", json.dumps({"p95_ms": 18.0})])
p.res(["experiment", "conclude", e3, "--fields", json.dumps(CONC)])
rel = f"spec/experiments/{e3}.yaml"
d = p.load(rel) if e3 and os.path.exists(p.path(rel)) else {"runs": [{"inputs": []}], "reproducibility": {}}
d["runs"].append({"run_id": "R2", "kind": "reproduction", "session": "S-forger", "results": {"p95_ms": 18.0}, "inputs": d["runs"][0]["inputs"],
                  "same_inputs": True, "agrees": True, "independent": True})
d["reproducibility"]["status"] = "REPRODUCED"
d["state_class"] = "EVIDENCE"
p.put(rel, d)
fs3 = p.res(["experiment", "show", e3]) or {}
v_rep = p.run(["experiment", "reproduce", e3, "--results", json.dumps({"p95_ms": 18.0})])
ck = findings(p.run(["experiment", "check"]))
check("WS10-J2-6.forged-lifecycle-not-honoured", fs3.get("standing", {}).get("standing") == "UNGOVERNED" and fs3.get("t2", {}).get("binding") == "BROKEN"
      and p.code(v_rep) == "T2_UNBOUND" and has(ck, "EXPERIMENT_LIFECYCLE_NOT_OS_WRITTEN", e3),
      "a hand-forged reproduction (REPRODUCED, EVIDENCE) breaks the T2 seal: not honoured, reported (high), and gov will not build on it",
      {"standing": fs3.get("standing"), "t2": fs3.get("t2"), "reproduce": p.code(v_rep)})
# promotion
v_np = p.run(["experiment", "promote", e2, "--paths", "product/gateway_async.py"])
v_self = None
e4 = (p.res(["experiment", "design", "--fields", json.dumps(dict(DESIGN, outputs=["spec/experiments/EXP-0004/**"]))]) or {}).get("experiment", {}).get("id")
p.res(["experiment", "run", e4, "--results", json.dumps({"p95_ms": 18.0})])
p.res(["experiment", "conclude", e4, "--fields", json.dumps(CONC)])
p.res(["experiment", "reproduce", e4, "--results", json.dumps({"p95_ms": 18.2})])
v_self = p.run(["experiment", "promote", e4, "--paths", "product/gateway_async.py"])
p.res(["experiment", "reproduce", e4, "--results", json.dumps({"p95_ms": 17.9})], session="S-repro")
v_l2 = p.run(["experiment", "promote", e4, "--paths", "product/gateway_async.py"], role="product-spec-agent")
pr = p.res(["experiment", "promote", e4, "--paths", "product/gateway_async.py"]) or {}
gid = pr.get("gate")
v_unans = p.run(["experiment", "promote", e4, "--paths", "product/gateway_async.py", "--gate", gid]) if gid else {}
p.human_decide(gid, "A") if gid else None
v_other = p.run(["experiment", "promote", e4, "--paths", "product/other.py", "--gate", gid]) if gid else {}
done = p.res(["experiment", "promote", e4, "--paths", "product/gateway_async.py", "--gate", gid]) if gid else None
check("WS10-J2-7.governed-promotion",
      p.code(v_np) == "EXPERIMENT_NOT_PROMOTABLE" and p.code(v_self) == "EXPERIMENT_NOT_PROMOTABLE" and p.code(v_l2) == "AUTHORITY_DENIED"
      and bool(gid) and p.code(v_unans) not in (None,) and p.code(v_other) == "APPROVAL_STALE" and bool(done) and done["experiment_state"] == "PROMOTED"
      and done["promotion"]["approved_by_kind"] == "human",
      "promotion needs governed evidence and an independent reproduction, L3 authority, and an owner-signed answer on the OS-raised gate whose subject binds exactly these paths",
      {"irreproducible": p.code(v_np), "same-session-only": p.code(v_self), "L2": p.code(v_l2), "gate": gid, "unanswered": p.code(v_unans),
       "other-paths": p.code(v_other), "promotion": done and done["promotion"]})
# production merge detection
p.write("spec/experiments/EXP-0001/gateway_async.py", "async def charge():\n    return 'async'\n")
p.write("product/charge_async.py", "async def charge():\n    return 'async'\n")
p.write("spec/experiments/EXP-0004/gateway_async.py", "async def charge_v4():\n    pass\n")
p.write("product/gateway_async.py", "async def charge_v4():\n    pass\n")
ck = findings(p.run(["experiment", "check"]))
check("WS10-J2-8.output-copied-into-production",
      any(f["code"] == "EXPERIMENT_OUTPUT_IN_PRODUCTION" and f["record"] == eid and "product/charge_async.py" in f["message"] for f in ck)
      and not any(f["code"] == "EXPERIMENT_OUTPUT_IN_PRODUCTION" and "product/gateway_async.py" in f["message"] for f in ck),
      "experimental output copied into production is reported whatever its name; a copy the approved promotion covers is not",
      [(f["code"], f["record"], f["message"][:120]) for f in ck if f["code"] == "EXPERIMENT_OUTPUT_IN_PRODUCTION"])
t = p.res(["task", "create", "--objective", "prototype async gateway client", "--class", "experiment", "--status", "READY", "--allowed", "product/**"])
tid = (t or {}).get("id")
p.run(["task", "claim", tid])
p.write("product/gateway_proto.py", "async def proto():\n    pass\n")
p.run(["rebuild-memory", "--incremental"])
v_close = p.run(["task", "close", tid, "--report", p.jfile("rep", {"work_completed": "prototype", "files_changed": ["product/gateway_proto.py"], "tests": {"status": "passed"}})])
p.git("add", "-A"); p.git("commit", "-q", "-m", "merge experimental prototype into product")
ck = findings(p.run(["experiment", "check"]))
check("WS10-J2-9.experimental-task-merge-detected", p.code(v_close) == "PRODUCTION_MERGE_NOT_ALLOWED"
      and any(f["code"] == "EXPERIMENTAL_TASK_OUTPUT_IN_PRODUCTION" and f["record"] == tid and "gateway_proto.py" in json.dumps(f) for f in ck),
      "delta-r J2.merge.detected's scenario: after the refused close the output is committed anyway — `gov experiment check` names the task and the file (the WS-2 family wires the same check)",
      {"close": p.code(v_close), "findings": [(f["code"], f["record"]) for f in ck if "TASK" in f["code"]]})
rv = p.run(["gate", "revoke", gid, "--reason", "probe: withdraw the promotion approval"]) if gid else {}
ck = findings(p.run(["experiment", "check"]))
check("WS10-J2-11.revoked-promotion-withdrawn", rv.get("ok") and has(ck, "EXPERIMENT_PROMOTION_NOT_HONOURED", e4)
      and any(f["code"] == "EXPERIMENT_OUTPUT_IN_PRODUCTION" and "product/gateway_async.py" in f["message"] for f in ck),
      "revoking the promotion gate withdraws the promotion: it is reported and the copy in production is no longer covered",
      [(f["code"], f["record"]) for f in ck if f["code"] in ("EXPERIMENT_PROMOTION_NOT_HONOURED", "EXPERIMENT_OUTPUT_IN_PRODUCTION")])
p.put("spec/experiments/EXP-0099.yaml", {"id": "EXP-0099", "type": "experiment", "title": "Async client", "status": "ACTIVE", "hypothesis": "async halves p95",
                                         "method": "A/B on staging", "data_provenance": "staging traffic 2026-09", "result": "p95 -40%", "confidence": 0.6, "production_merge_allowed": True})
ck0 = findings(p.run(["experiment", "check"]))
ad = p.res(["experiment", "design", "--fields", json.dumps({"id": "EXP-0099"})]) or {}
check("WS10-J2-10.legacy-experiment-adopted", has(ck0, "EXPERIMENT_NOT_GOVERNED", "EXP-0099") and has(ck0, "EXPERIMENT_MERGE_PERMITTED", "EXP-0099")
      and ad.get("experiment", {}).get("experiment_state") == "DESIGNED" and ad["experiment"]["production_merge_allowed"] is False,
      "an experiment written outside the lifecycle is reported (and its merge flag), then taken into the lifecycle under its own id with the flag corrected",
      {"before": [(f["code"]) for f in ck0 if f["record"] == "EXP-0099"], "after": ad.get("experiment", {}).get("experiment_state")})

# ======================================================================================================== H4 chain
print("\n## H4 — scenarios drive data and tests", flush=True)
p = Proj("ws10-h4")
A = "ACTIVE"
p.put("spec/features/F-0001.yaml", {"id": "F-0001", "type": "feature", "title": "Order totals", "status": A, "capability_category": "backend", "readiness": {}, "scenarios": ["SCN-0001"], "acceptance_tests": ["TST-0001"]})
p.put("spec/scenarios/SCN-0001.yaml", {"id": "SCN-0001", "type": "scenario", "title": "Append two orders and total", "status": A, "feature": "F-0001", "given": ["an empty ledger"],
                                       "when": ["two orders are appended"], "then": ["total_cents is 399"], "data_requirements": ["DATA-0001"],
                                       "success_criteria": ["exact integer total"], "failure_criteria": ["duplicate order ids accepted"]})
p.put("spec/data/DATA-0001.yaml", {"id": "DATA-0001", "type": "data", "title": "Data requirement: order lines", "status": A, "author_role": "backend-engineer"})
p.put("spec/data/TD-0001.yaml", {"id": "TD-0001", "type": "data", "title": "Test dataset: 1k synthetic orders", "status": A, "author_role": "backend-engineer"})
p.put("spec/tasks/TST-0001.yaml", {"id": "TST-0001", "type": "test-obligation", "title": "Ledger acceptance tests", "status": A, "feature": "F-0001", "scenario": "SCN-0001",
                                   "family": "acceptance", "test_path": "tests/ledger_test.rs", "author_role": "independent-test-designer", "independent_of_implementer": True,
                                   "data_provenance": "TD-0001 (synthetic, generated)"})
p.put("spec/tasks/TST-0002.yaml", {"id": "TST-0002", "type": "test-obligation", "title": "no provenance", "status": A, "feature": "F-0001", "scenario": "SCN-0001", "family": "acceptance", "independent_of_implementer": True})
p.put("spec/tasks/TASK-0001.yaml", {"id": "TASK-0001", "type": "task", "title": "Implement totals", "status": A, "class": "implementation", "task_status": "READY",
                                    "objective": "implement totals", "feature": "F-0001", "role": "backend-engineer", "allowed_paths": ["src/**"]})
p.git("add", "-A"); p.git("commit", "-q", "-m", "h4")
tr = p.res(["scenario", "trace", "F-0001"]) or {}
codes = sorted({(g["code"], g["record"]) for g in tr.get("gaps", [])})
want = {("DATA_REQUIREMENT_WITHOUT_TEST_DATA", "DATA-0001"), ("TEST_DATA_UNDECLARED", "TST-0002"), ("TEST_DATA_WITHOUT_PROVENANCE", "TD-0001"),
        ("DATA_AUTHOR_NOT_INDEPENDENT", "TD-0001"), ("DATA_AUTHORSHIP_NOT_ESTABLISHED", "TD-0001"), ("TEST_DATA_NOT_FOR_SCENARIO", "TST-0001")}
check("WS10-H4-1.gamma-r-fixture-gaps", want <= set(codes) and tr.get("complete") is False,
      "gamma-r H4's fixture: DATA→TEST DATA missing, a test without provenance, a dataset without provenance authored by the implementer role — each missing link is named", codes)
sc = p.load("spec/scenarios/SCN-0001.yaml")
sc.pop("success_criteria"); sc.pop("failure_criteria")
p.put("spec/scenarios/SCN-0001.yaml", sc)
chk = findings(p.run(["scenario", "check"]))
check("WS10-H4-2.criteria-gaps", has(chk, "SCENARIO_WITHOUT_SUCCESS_CRITERIA", "SCN-0001") and has(chk, "SCENARIO_WITHOUT_FAILURE_CRITERIA", "SCN-0001"),
      "a scenario without success/failure criteria is a named gap", [(f["code"], f["record"]) for f in chk if f["record"] == "SCN-0001"])
sc["success_criteria"] = ["exact integer total"]; sc["failure_criteria"] = ["duplicate order ids accepted"]
p.put("spec/scenarios/SCN-0001.yaml", sc)
p.write("tests/data/orders.csv", "id,cents\n1,199\n2,200\n")
DS = {"data_kind": "test-dataset", "implements": ["DATA-0001"], "location": "tests/data/orders.csv", "provenance": {"source_kind": "synthetic", "origin": "gen_orders.py --seed 7"}}
r1 = p.run(["data", "register", "--fields", json.dumps({"data_kind": "test-dataset", "implements": ["DATA-0001"]})])
r2 = p.run(["data", "register", "--fields", json.dumps(dict(DS, implements=["DATA-0404"]))])
r3 = p.run(["data", "register", "--fields", json.dumps(dict(DS, provenance={"source_kind": "approved-real", "origin": "production export", "approval": "D-0404"}))])
r4 = p.run(["data", "register", "--fields", json.dumps(dict(DS, provenance={"source_kind": "scraped", "origin": "web"}))])
check("WS10-H4-3a.register-refusals", [p.code(x) for x in (r1, r2, r3, r4)] == ["DATA_PROVENANCE_REQUIRED", "DATA_REFERENCE_UNKNOWN", "DATA_REAL_DATA_UNAPPROVED", "DATA_PROVENANCE_REQUIRED"],
      "a test dataset without provenance, realising no known requirement, of real data without an approving decision, or of an unknown source kind is refused", [p.code(x) for x in (r1, r2, r3, r4)])
# an implementation task designated for product-spec-agent: that role may not author the scenario's test data
p.put("spec/tasks/TASK-0002.yaml", {"id": "TASK-0002", "type": "task", "title": "Implement totals UI", "status": A, "class": "implementation", "task_status": "READY",
                                    "objective": "ui", "feature": "F-0001", "role": "product-spec-agent", "allowed_paths": ["ui/**"]})
r5 = p.run(["data", "register", "--fields", json.dumps(DS)], role="product-spec-agent", session="S-psa")
r6 = p.run(["data", "register", "--fields", json.dumps(dict(DS, id="TD-0002"))], role="architecture-agent", session="S-da")
ds = p.res(["data", "show", "TD-0002"]) or {}
check("WS10-H4-3b.registered-with-os-authorship", p.code(r5) == "DATA_AUTHOR_NOT_INDEPENDENT" and r6.get("ok") and ds.get("authorship", {}).get("established")
      and ds["authorship"]["role"] == "architecture-agent" and ds.get("t2", {}).get("binding") == "VERIFIED" and ds["data"]["provenance"].get("content_sha256"),
      "the implementer's role may not author the scenario's test data; an independent role registers it — authorship stamped by the OS (T2) and the content bound by SHA-256",
      {"implementer": p.code(r5), "authorship": ds.get("authorship"), "provenance": (ds.get("data") or {}).get("provenance")})
t1 = p.load("spec/tasks/TST-0001.yaml"); t1["test_data"] = ["TD-0002"]; t1.pop("data_provenance"); p.put("spec/tasks/TST-0001.yaml", t1)
t2 = p.load("spec/tasks/TST-0002.yaml"); t2["test_data"] = ["TD-0002"]; p.put("spec/tasks/TST-0002.yaml", t2)
p.put("spec/data/TD-0001.yaml", dict(p.load("spec/data/TD-0001.yaml"), status="RETIRED"))
tr = p.res(["scenario", "trace", "SCN-0001"]) or {}
check("WS10-H4-4.complete-chain", tr.get("complete") is True and ((tr.get("data_requirements") or [{}])[0]).get("test_datasets") == ["TD-0002"],
      "with the dataset realising the requirement and the tests naming it, the chain FEATURE→SCENARIO→DATA→TEST DATA→CRITERIA→INDEPENDENT TESTS is complete",
      {"gaps": tr.get("gaps"), "requirements": tr.get("data_requirements")})
p.write("tests/data/orders.csv", "id,cents\n1,199\n2,201\n")
ds = p.res(["data", "show", "TD-0002"]) or {}
check("WS10-H4-5.provenance-read", any(g["code"] == "TEST_DATA_CHANGED" for g in ds.get("gaps", [])),
      "provenance is read: the dataset's bytes changing after registration is reported", ds.get("gaps"))
p.write("tests/data/orders.csv", "id,cents\n1,199\n2,200\n")
g_real = p.gate("May the production order export be used as test data?", extra={"options": [{"id": "A", "description": "approve"}, {"id": "B", "description": "decline"}]})
dreal = (p.human_decide(g_real).get("result") or {}).get("decision")
r7 = p.run(["data", "register", "--fields", json.dumps(dict(DS, id="TD-0003", provenance={"source_kind": "approved-real", "origin": "production export, anonymised", "approval": dreal}))],
           role="architecture-agent", session="S-da")
g_w = p.gate("Waive data-author independence for TD-0004?", extra={"options": [{"id": "A", "description": "waive"}, {"id": "B", "description": "keep"}]})
dw = (p.human_decide(g_w).get("result") or {}).get("decision")
r8 = p.run(["data", "register", "--fields", json.dumps(dict(DS, id="TD-0004", independence_waiver={"decision": dw, "reason": "single-person team"}))], role="product-spec-agent", session="S-psa")
check("WS10-H4-6.human-decisions", r7.get("ok") and r8.get("ok"),
      "real data with an owner-approved decision, and an implementer-authored dataset under an owner-approved independence waiver, are accepted", {"real": p.code(r7), "waiver": p.code(r8)})

# ======================================================================================================== G0 / authority
print("\n## G0 — every new command is classified", flush=True)
p = Proj("ws10-g0")
v_l0 = p.run(["research", "record", "--fields", json.dumps(COMPLETE_RES)], role=None)
v_l1 = p.run(["research", "record", "--fields", json.dumps(COMPLETE_RES)], role="research-agent")
p.run(["freeze-writes", "--reason", "probe"])
v_fz = p.run(["research", "record", "--fields", json.dumps(COMPLETE_RES)])
v_rd = p.run(["research", "check"])
v_sc = p.run(["scenario", "check"])
p.run(["resume"])
check("WS10-G0-1.guarded", p.code(v_l0) == "AUTHORITY_DENIED" and p.code(v_l1) == "AUTHORITY_DENIED" and p.code(v_fz) == "FROZEN" and v_rd.get("ok") and v_sc.get("ok"),
      "writes need the declared role's authority (L0/undeclared and L1 refused under mutate_spec_other, L2) and are refused under FREEZE_WRITES; reads still answer",
      {"undeclared": p.code(v_l0), "research-agent": p.code(v_l1), "frozen": p.code(v_fz), "check": v_rd.get("ok")})

n = len(RESULTS)
failed = [c for c, ok in RESULTS if not ok]
print(f"SUMMARY checks={n} pass={n - len(failed)} fail={len(failed)} failed={failed}", flush=True)
