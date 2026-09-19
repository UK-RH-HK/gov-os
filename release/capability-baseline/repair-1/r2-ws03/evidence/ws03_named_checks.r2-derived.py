#!/usr/bin/env python3
# DERIVED COPY (P2-AR-0024, WS-3 round 2) of release/capability-baseline/repair-1/ws03/evidence/ws03_named_checks.py.
# Changes, and nothing else:
#  (1) HC = the round-1 hc_owner.py by absolute path (this copy lives in the round-2 evidence directory);
#  (2) channel(): P2-ADJ-0001 turned the standalone anchor off, so the human channel is the provisioned root's
#      `human-gate` delegation — the machine is provisioned with the throw-away test root (hc_root.py) and the kernel it
#      installed while unprovisioned is re-verified against a signed release of the pinned payload (r2_machine.py);
#  (3) O5-G0: `rebuild-memory` is on both recovery allow-lists since round 2 (O-4), so it is skipped in the
#      "outside the allow-list" loop like `gate present` under PAUSE, and a separate check asserts that under the
#      control it changes nothing but the derived generated manifests.
# Every other check, its scenario and its PASS criterion are P2-AR-0016's.
"""P2-AR-0016 (WS-3) — discriminating re-implementation of the audit-of-record checks repair-delta.md names for
BC-P2-08, -09, -10, -12, -18, -45 and -49. BUILDER REGRESSION EVIDENCE ONLY (Contract v3 O3): not an acceptance test.

Why this exists. Most named probes cannot run to completion unedited on the repaired product, for reasons that ARE the
repairs: their harnesses rely on the removed default-orchestrator role (BC-P2-08: `gov init` without a role is now
refused), create question-only gates (BC-P2-49), and relay human answers with `gov decide --by owner` (BC-P2-10). This
script reproduces each named check's scenario and PASS criterion, adapting only the legitimate path the repair changed:
roles are declared, fixture gates carry a complete package, and a legitimate human answer is an owner-signed document
(`hc_owner.py`, TEST MATERIAL, published seed). Every check id is the audit line it mirrors.

Run against both binaries — the base build is the negative control (the named FAIL lines must FAIL there):
    GOV=<gov> SCR=<scratch> python3 ws03_named_checks.py
"""
import json
import os
import subprocess
import sys
import uuid

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
GOV = os.environ["GOV"]
SCR = os.environ["SCR"]
HC = os.path.join(WT, "release/capability-baseline/repair-1/ws03/evidence/hc_owner.py")  # (1)
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
from r2_machine import REL, SNAP, TS, publish, release_doc, stage_files  # noqa: E402  (2)
RESULTS = []


def check(cid, ok, statement, detail=None):
    RESULTS.append((cid, bool(ok)))
    print(f"CHECK {cid} {'PASS' if ok else 'FAIL'} {statement}" + (f" -- {json.dumps(detail, default=str)[:600]}" if detail is not None else ""), flush=True)


def note(cid, statement, detail=None):
    print(f"NOTE {cid} {statement}" + (f" -- {json.dumps(detail, default=str)[:600]}" if detail is not None else ""), flush=True)


class P:
    def __init__(self, tag, init=True):
        base = os.path.join(SCR, f"{tag}-{uuid.uuid4().hex[:6]}")
        self.root = os.path.join(base, "proj")
        self.machine = os.path.join(base, "machine")
        os.makedirs(self.root)
        os.makedirs(self.machine)
        subprocess.run(["cp", "-r", os.path.join(WT, "fixtures", "greenfield", "project", "."), self.root], check=True)
        self.git("init", "-q")
        self.git("config", "user.email", "p@x")
        self.git("config", "user.name", "p")
        self.commit("fixture")
        if init:
            r = self.run("init", "--name", tag, role="orchestrator")
            assert r["ok"], r
            self.commit("after init")

    def git(self, *a):
        return subprocess.run(["git", *a], cwd=self.root, capture_output=True, text=True)

    def commit(self, m):
        self.git("add", "-A")
        self.git("commit", "-qm", m)

    def env(self, extra=None):
        e = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
        e["XDG_STATE_HOME"] = self.machine
        e.update(extra or {})
        return e

    def run(self, *args, role="orchestrator", session="S-p", env=None):
        cmd = [GOV, "--json", "--root", self.root, "--session", session]
        if role is not None:
            cmd += ["--role", role]
        p = subprocess.run(cmd + list(args), capture_output=True, text=True, env=self.env(env), cwd=self.root)
        try:
            v = json.loads(p.stdout)
        except Exception:
            v = {"ok": False, "error": {"code": "NO_JSON", "message": (p.stderr or p.stdout)[-400:]}}
        return v

    def ok(self, *args, **kw):
        v = self.run(*args, **kw)
        if not v.get("ok"):
            raise SystemExit(f"setup step failed: gov {' '.join(args)}: {v.get('error')}")
        return v["result"]

    def rec(self, rid):
        for d, _, fs in os.walk(os.path.join(self.root, "spec")):
            for f in fs:
                if f == rid + ".yaml":
                    return yaml.safe_load(open(os.path.join(d, f)))
        return None

    def rel(self, rid):
        for d, _, fs in os.walk(os.path.join(self.root, "spec")):
            for f in fs:
                if f == rid + ".yaml":
                    return os.path.join(d, f)
        return None

    def tree_no_generated(self):  # (3)
        import hashlib
        h = hashlib.sha256()
        for top in ("spec", "governance"):
            for d, _, fs in sorted(os.walk(os.path.join(self.root, top))):
                if os.path.relpath(d, self.root).startswith("governance/generated"):
                    continue
                for f in sorted(fs):
                    full = os.path.join(d, f)
                    h.update(os.path.relpath(full, self.root).encode())
                    h.update(open(full, "rb").read())
        return h.hexdigest()

    def tree(self):
        import hashlib
        h = hashlib.sha256()
        for top in ("spec", "governance"):
            for d, _, fs in sorted(os.walk(os.path.join(self.root, top))):
                for f in sorted(fs):
                    full = os.path.join(d, f)
                    h.update(os.path.relpath(full, self.root).encode())
                    h.update(open(full, "rb").read())
        return h.hexdigest()


def package(**extra):
    v = {"why_now": "the next task depends on it", "current_state": "two options analysed", "options": [{"id": "A", "description": "proceed"}, {"id": "B", "description": "do not proceed"}],
         "impact": "dependent tasks re-planned", "reversibility": "reversible", "cost_rework": "one task of rework", "recommendation": "A", "confidence": 0.6, "impact_radius": "R3"}
    v.update(extra)
    return json.dumps(v)


def gate(p, q, session="S-p", **extra):
    return p.ok("gate", "create", "--question", q, "--fields", package(**extra), session=session)["id"]


CANDIDATE = None


def is_candidate(p):
    global CANDIDATE
    if CANDIDATE is None:
        CANDIDATE = p.run("trust", "human-channel").get("ok", False) or "HUMAN_CHANNEL" in json.dumps(p.run("trust", "human-channel"))
    return CANDIDATE


def channel(p):  # (2)
    if not is_candidate(p):
        return
    st = p.run("trust", "human-channel")
    if st.get("ok") and st["result"].get("available"):
        return
    f = os.path.join(os.path.dirname(p.root), f"root-{uuid.uuid4().hex[:6]}.json")
    subprocess.run([sys.executable, os.path.join(HERE, "hc_root.py"), f], check=True, capture_output=True)
    p.ok("trust", "provision", "--anchor", f)
    pin = yaml.safe_load(open(os.path.join(p.root, "governance/framework.lock")))["release_hash"]
    src = next(c for c in (os.path.join(p.root, "governance/kernel"),) if stage_files(c)["payload_hash"] == pin)
    rel = os.path.join(os.path.dirname(p.root), f"reanchor-{uuid.uuid4().hex[:6]}")
    import shutil
    shutil.copytree(src, os.path.join(rel, "kernel"))
    publish(os.path.join(rel, "metadata"), release_doc(os.path.join(rel, "kernel"), sequence=1, version=1), [REL], [SNAP], [TS])
    p.ok("kernel", "reinstall", "--source", os.path.join(rel, "kernel"), role="orchestrator")


def owner_answer(p, g, option, role="orchestrator", session="S-p"):
    """The legitimate human answer: candidate = owner-signed document; base = the old relay (`--by owner`)."""
    r = p.ok("gate", "present", g, role=role)
    if not is_candidate(p):
        return p.run("decide", g, "--option", option, "--by", "owner", role=role, session=session)
    channel(p)
    f = os.path.join(os.path.dirname(p.root), f"ans-{g}-{uuid.uuid4().hex[:6]}.json")
    subprocess.run([sys.executable, HC, "answer", f, g, r["gate"]["gate_instance"], r["gate"]["package_sha256"], option], check=True, capture_output=True)
    return p.run("decide", g, "--option", option, "--answer-file", f, role=role, session=session)


def cit(p, tag, trigger="governance_change"):
    mf = os.path.join(os.path.dirname(p.root), f"m-{tag}.json")
    json.dump([{"op": "write_file", "path": f"docs/{tag}.md", "content": f"{tag}\n"}], open(mf, "w"))
    r = p.ok("cit", "propose", "--proposal", f"change {tag}", "--trigger", trigger, "--manifest", mf)
    cid = r["id"]
    gid = (r.get("simulation") or {}).get("human_gate") or p.ok("cit", "show", cid).get("human_gate")
    return cid, gid


print(f"# GOV={GOV}")

# ================================================================================ BC-P2-08 role resolution + G0
p = P("rr")
v = p.run("gate", "revoke", gate(p, "revocation target?"), role=None)
check("X2-E1-undeclared-role-is-not-orchestrator", not v.get("ok"), "an invocation with no role declared cannot perform an L4-only operation (gate revoke)", (v.get("error") or {}).get("code"))
fresh = P("rr-init", init=False)
v = fresh.run("init", "--name", "x", role=None)
check("S0-E1-01.init-undeclared", not v.get("ok") and not os.path.exists(os.path.join(fresh.root, "governance", "framework.lock")), "gov init with no declared role installs nothing", (v.get("error") or {}).get("code"))
v = p.run("init", "--force", role="independent-auditor")
v2 = p.run("init", "--force", role=None, env={"GOV_ROLE": "independent-auditor"})
check("X2-E1-init-honours-declared-role", not v.get("ok") and not v2.get("ok"), "init --force (install_kernel L4) evaluates the role declared by --role exactly as GOV_ROLE", {"--role": (v.get("error") or {}).get("code"), "GOV_ROLE": (v2.get("error") or {}).get("code")})
before = p.tree()
v = p.run("task", "replan", role="independent-auditor")
v2 = p.run("memory", "heldout-starter", "--force", role="independent-auditor")
check("E1.b2.census.unclassed", not v.get("ok") and not v2.get("ok") and p.tree() == before, "task replan / memory heldout-starter --force carry an authority class and are refused for L0 with no mutation", {"replan": (v.get("error") or {}).get("code"), "heldout": (v2.get("error") or {}).get("code")})
b = P("rr-brown", init=False)
v = b.run("adopt", "baseline", role="independent-auditor")
check("S3-S4.R2.adopt-as-L0", not v.get("ok"), "an adopt stage declared as independent-auditor (L0) is refused", (v.get("error") or {}).get("code"))
# G0 under FREEZE_WRITES / PAUSE (O5-G0 / A5): writes refused, zero mutation, allow-list only
g0 = P("g0")
gid = gate(g0, "pending question?")
g0.ok("task", "create", "--id", "TASK-G0", "--class", "documentation", "--objective", "x", "--status", "READY")
ev = os.path.join(os.path.dirname(g0.root), "route.json")
json.dump({"model": "m", "provider": "p", "task_class": "implementation", "reasoning_effort": "high", "cost": 999, "latency_ms": 1, "pass": True, "repair_count": 0, "reviewer_findings": 0}, open(ev, "w"))
writes = [["gate", "present", gid], ["audit"], ["rebuild-memory"], ["memory", "heldout-starter", "--force"], ["adapters", "generate"], ["tools", "registry"],
          ["context", "compile", "TASK-G0"], ["task", "release", "TASK-G0"], ["continue"], ["route", "--record", ev], ["init", "--force"], ["task", "replan"]]
for mode in ("freeze-writes", "pause"):
    g0.ok(mode, "--reason", "incident")
    mutated = []
    for args in writes:
        if mode == "pause" and args[:2] == ["gate", "present"]:
            continue
        if args == ["rebuild-memory"]:
            continue  # (3) on both allow-lists since round 2 (O-4); checked separately below
        t0 = g0.tree()
        g0.run(*args)
        if g0.tree() != t0:
            mutated.append(" ".join(args))
    t0 = g0.tree_no_generated()  # (3)
    rb = g0.run("rebuild-memory")
    check(f"O5-G0.{mode}.rebuild-derived-only", rb.get("ok") and g0.tree_no_generated() == t0, f"(3) under {mode} the allow-listed rebuild changes only derived generated manifests", (rb.get("error") or {}).get("code"))
    g0.ok("resume")
    check(f"O5-G0.{mode}", not mutated, f"no governed state changes under {mode} outside the explicit allow-list", {"mutated": mutated})
v = g0.run("init", "--force", role="independent-auditor")
check("O5-G0.L0-init-force", not v.get("ok"), "L0 init --force is refused", (v.get("error") or {}).get("code"))

# ================================================================================ BC-P2-10 human channel
h = P("hc")
for label, role, envx in (("default", None, None), ("role-human", "human", None), ("env-GOV_ROLE", None, {"GOV_ROLE": "human"})):
    q = gate(h, f"Proceed with {label}?", impact_radius="R3", reversibility="irreversible", confidence=0.4)
    h.ok("gate", "present", q)
    # the base binary's default role is orchestrator: `role=None` is the X2 "default" attack as written
    h.run("decide", q, "--option", "A", role=role, env=envx)
    kind = ((h.rec(q) or {}).get("answer") or {}).get("by_kind")
    check(f"X2-L3-fabrication-{label}", kind != "human", f"human approval cannot be fabricated by CLI metadata ({label})", {"answer.by_kind": kind})
q = gate(h, "Proceed with an explicit orchestrator relay and the default --by?")
h.ok("gate", "present", q)
v = h.run("decide", q, "--option", "A")
dec = h.rec((v.get("result") or {}).get("decision", "")) if v.get("ok") else {}
check("L3.b5.1", not (v.get("ok") and (dec or {}).get("human_approved") is True), "an agent relaying `gov decide` with the default --by records no human approval", {"ok": v.get("ok"), "code": (v.get("error") or {}).get("code")})
q = gate(h, "Json-only presentation?")
h.ok("gate", "present", q)
check("L3.b2.2", not (h.rec(q) or {}).get("presented_in_chat"), "a gate rendered only into a JSON envelope is not recorded as presented to a human", {"presented_in_chat": (h.rec(q) or {}).get("presented_in_chat")})
c = P("hc-cont")
qc = gate(c, "Continue presents me?")
c.run("continue")
check("L3.b2.3", not (c.rec(qc) or {}).get("presented_in_chat"), "`gov --json continue` does not make a gate count as presented in the human interface", {"presented_in_chat": (c.rec(qc) or {}).get("presented_in_chat")})
q = gate(h, "Research agent renders me?")
h.ok("gate", "present", q, role="research-agent")
r = h.rec(q) or {}
check("L3.b2.5.adapted", (not r.get("presented_in_chat")) or bool(r.get("presentation_receipt")), "a gate is recorded as presented only with a human-side receipt (the literal b2.5 checks for a receipt field after rendering alone)", {k: r.get(k) for k in ("presented_in_chat", "presentation_receipt", "presented_by")})
v = h.run("memory", "select", "builtin:128", "--by", "anyone", role="human")
dsel = h.rec((v.get("result") or {}).get("decision", "")) if v.get("ok") else {}
check("L3.b5.11", not (v.get("ok") and (dsel or {}).get("human_approved") is True), "`gov memory select` with a self-declared --role human records no human approval", {"ok": v.get("ok"), "code": (v.get("error") or {}).get("code")})
if is_candidate(h):
    q = gate(h, "The genuine owner answer?")
    v = owner_answer(h, q, "A")
    dec = h.rec(v["result"]["decision"]) if v.get("ok") else {}
    check("HC-1.positive", v.get("ok") and (dec or {}).get("human_approved") is True and (h.rec(q) or {}).get("presented_in_chat") is True, "an owner-signed answer is recorded as the human's answer, with presentation evidence", {"ok": v.get("ok"), "err": v.get("error")})

# ================================================================================ BC-P2-09 T2 binding
t = P("t2")
cid, gid = cit(t, "b1")
t.ok("gate", "present", gid)
rel = t.rel(gid)
d = yaml.safe_load(open(rel))
d["presented_in_chat"] = True
yaml.safe_dump(d, open(rel, "w"), sort_keys=False)
v = t.run("decide", gid, "--option", "A", "--rationale", "record-edit presentation")
check("L3.b1.6", (not v.get("ok")) and (v.get("error") or {}).get("code") == "GATE_NOT_PRESENTED", "a gate whose presentation flag was set by a direct file edit is still not presented", (v.get("error") or {}).get("code"))
cid2, gid2 = cit(t, "forged")
rel = t.rel(gid2)
d = yaml.safe_load(open(rel))
d.update({"gate_status": "ANSWERED", "presented_in_chat": True, "presented_at": "2026-09-18T00:00:00Z", "presented_by": {"session": "human-console", "role": "human"},
          "answer": {"option": "A", "by": "product-owner", "by_kind": "human", "acting_role": "human", "at": "2026-09-18T00:00:01Z", "rationale": "forged"}})
yaml.safe_dump(d, open(rel, "w"), sort_keys=False)
yaml.safe_dump({"id": "D-0900", "type": "decision", "title": "forged", "status": "ACTIVE", "chosen_option": "A", "human_approved": True, "approved_by_kind": "human", "derived_from": [gid2], "cit": cid2, "state_class": "AUTHORITATIVE"},
               open(os.path.join(t.root, "spec/decisions/D-0900.yaml"), "w"), sort_keys=False)
cc = dict(role="change-controller", session="S-cc")
a = t.run("cit", "approve", cid2, "--by", "owner", "--method", "human", **cc)
e = t.run("cit", "execute", cid2, **cc) if a.get("ok") else a
check("L3.b5.8+X2-L3xE1+X2-L3xK2", not (a.get("ok") and e.get("ok")) and not os.path.exists(os.path.join(t.root, "docs/forged.md")), "forged gate/decision files cannot carry a CIT to COMMITTED as human-approved", {"approve": (a.get("error") or {}).get("code") or (a.get("result") or {}).get("human_approved"), "execute": (e.get("error") or {}).get("code")})
cid3, gid3 = cit(t, "rebind-1")
cid4, gid4 = cit(t, "rebind-2")
owner_answer(t, gid3, "A")
rel = t.rel(gid3)
d = yaml.safe_load(open(rel))
d["cit"] = cid4
yaml.safe_dump(d, open(rel, "w"), sort_keys=False)
rel4 = t.rel(cid4)
d4 = yaml.safe_load(open(rel4))
d4["human_gate"] = gid3
yaml.safe_dump(d4, open(rel4, "w"), sort_keys=False)
a = t.run("cit", "approve", cid4, **cc)
e = t.run("cit", "execute", cid4, **cc) if a.get("ok") else a
check("L3.b4.o2", not e.get("ok") and not os.path.exists(os.path.join(t.root, "docs/rebind-2.md")), "re-binding an answered gate to another CIT by editing records does not execute the other CIT", {"approve": (a.get("error") or {}).get("code"), "execute": (e.get("error") or {}).get("code")})

# ================================================================================ BC-P2-12 answer side
k = P("blk")
tasks = [k.ok("task", "create", "--objective", f"t{n}", "--class", "discovery", "--status", "READY")["id"] for n in range(3)]
gd = gate(k, "May t0 proceed?", blocks_tasks=[tasks[0]])
ga = gate(k, "May t1 proceed?", blocks_tasks=[tasks[1]])
gw = gate(k, "May t2 proceed?", blocks_tasks=[tasks[2]])
owner_answer(k, gd, "B")
st = (k.rec(tasks[0]) or {}).get("task_status")
check("L3.b4.t2.answer-side", st != "READY", "a declining answer does not release the blocked task (task_status)", {"task_status": st})
owner_answer(k, ga, "A")
k.ok("gate", "revoke", ga, "--reason", "withdrawn")
st = (k.rec(tasks[1]) or {}).get("task_status")
check("L3.b4.t3.answer-side", st not in ("READY", "IN_PROGRESS"), "revoking the authorising answer returns the task to blocked (task_status)", {"task_status": st})
k.ok("gate", "revoke", gw, "--reason", "question withdrawn")
st = (k.rec(tasks[2]) or {}).get("task_status")
check("L3.b4.t4.answer-side", st not in ("READY", "IN_PROGRESS"), "withdrawing an unanswered gate leaves the task blocked (task_status)", {"task_status": st})
dag = k.ok("task", "dag")
note("L3.b4.t2-t4.dag-side", "DAG runnable set (dag.rs is WS-5's; it must consult gates::task_gate_authorisation)", {"runnable": dag.get("runnable")})

# ================================================================================ BC-P2-18 agent resolution rules
r = P("agent")
low = dict(impact_radius="R0", confidence=0.95, reversibility="reversible")
g1 = gate(r, "Self-assessed contradiction?", **low)
r.ok("gate", "present", g1)
v = r.run("decide", g1, "--option", "A", "--by", "orchestrator", "--rationale", "x")
check("L1.b2.self", not v.get("ok"), "the same session cannot raise a gate declaring R0/0.95/reversible and resolve it as an agent", (v.get("error") or v.get("result")))
g2 = gate(r, "Unassessed reversibility?", session="S-raiser", impact_radius="R0", confidence=0.95, reversibility="depends on the vendor")
r.ok("gate", "present", g2)
v = r.run("decide", g2, "--option", "A", "--by", "orchestrator", "--rationale", "x")
check("L1.b2.neg.no-reversibility", not v.get("ok") and (v.get("error") or {}).get("code") == "AUTHORITY_DENIED", "agent resolution is refused when reversibility is not assessed", (v.get("error") or {}).get("code"))
g3 = gate(r, "Independently assessed?", session="S-raiser", **low)
r.ok("gate", "present", g3)
v0 = r.run("decide", g3, "--option", "A", "--by", "orchestrator")
check("L1.b4.1", not v0.get("ok"), "an agent resolution without a rationale is refused", (v0.get("error") or {}).get("code"))
v = r.run("decide", g3, "--option", "A", "--by", "orchestrator", "--rationale", "assessed by another session")
check("L1.b2.1.independent", v.get("ok") and (v.get("result") or {}).get("answered_by_kind") == "agent", "an L4 agent may resolve an R0/0.95/reversible question assessed by another session", (v.get("error") or {}).get("code"))

# ================================================================================ BC-P2-45 overlay precedence
o = P("ovl")
mro = yaml.safe_load(open(os.path.join(o.root, "governance/project/MODEL_ROUTING_OVERRIDES.yaml")))
mro["providers"] = [{"name": "prov", "models": [{"id": "light", "tier": "T1", "max_reasoning": "low", "cost_per_1k_in": 0.1}, {"id": "frontier", "tier": "T3", "max_reasoning": "extra_high", "cost_per_1k_in": 9.0}]}]
mro["task_class_overrides"] = {"security": "T1"}
mro["role_overrides"] = {"orchestrator": {"minimum_tier": "T1", "default_reasoning": "low"}, "backend-engineer": {"default_reasoning": "low"}}
yaml.safe_dump(mro, open(os.path.join(o.root, "governance/project/MODEL_ROUTING_OVERRIDES.yaml"), "w"), sort_keys=False)
rs = o.ok("route", "--class", "security", role="test-execution-agent")
check("M1.floor.1", rs["minimum_tier"] == "T3", "MODEL_ROUTING_OVERRIDES.task_class_overrides cannot lower the kernel minimum for security (T3)", rs["minimum_tier"])
tx = o.ok("task", "create", "--objective", "hard", "--class", "implementation", "--fields", json.dumps({"minimum_reasoning": "extra_high"}))["id"]
rw = o.ok("route", "--task", tx, role="backend-engineer")
check("M2.b1.4", rw["reasoning"] == "extra_high", "a project role override cannot lower the reasoning below the task's declared minimum", rw["reasoning"])
rr = o.ok("route", "--class", "documentation", role="orchestrator")
check("M3.b1.floor", rr["minimum_tier"] == "T3" and rr["reasoning"] == "high", "a project role override cannot lower the orchestrator below T3/high", {"tier": rr["minimum_tier"], "reasoning": rr["reasoning"]})
pp = yaml.safe_load(open(os.path.join(o.root, "governance/project/PROJECT_POLICY.yaml")))
pp["readiness"]["enforce_pre_implementation_cells"] = False
yaml.safe_dump(pp, open(os.path.join(o.root, "governance/project/PROJECT_POLICY.yaml"), "w"), sort_keys=False)
readiness = {x["id"]: "PRESENT" for x in yaml.safe_load(open(os.path.join(WT, "framework/taxonomy/READINESS_DIMENSIONS.yaml")))["dimensions"]}
readiness["security_privacy"] = "MISSING"
yaml.safe_dump({"id": "F-0005", "type": "feature", "title": "f", "status": "ACTIVE", "readiness": readiness}, open(os.path.join(o.root, "spec/features/F-0005.yaml"), "w"), sort_keys=False)
o.ok("task", "create", "--id", "TASK-IMPL5", "--class", "implementation", "--objective", "impl", "--feature", "F-0005", "--status", "READY", "--fields", json.dumps({"scenarios": ["SCN-X"], "acceptance_tests": ["TST-X"]}))
dag = o.ok("task", "dag")
ov = o.ok("policy", "overrides")
refused = [f"{x['policy']}.{x['key']}" for x in ov.get("refused", [])]
check("H3.b5.switch", "TASK-IMPL5" not in dag["runnable"] and "PROJECT_POLICY.readiness.enforce_pre_implementation_cells" in refused, "the overlay cannot switch off readiness gating; the refused weakening is reported", {"runnable": "TASK-IMPL5" in dag["runnable"], "refused": refused})

# ================================================================================ BC-P2-49 package
k2 = P("pkg")
v = k2.run("gate", "create", "--question", "Should we proceed?")
g2rec = k2.rec((v.get("result") or {}).get("id", "")) if v.get("ok") else None
FIELDS = ["question", "why_now", "current_state", "options", "impact", "reversibility", "cost_rework", "recommendation", "confidence", "permitted_next_actions"]
defaulted = [f for f in FIELDS if g2rec and g2rec.get(f) in ("not assessed", [], 0.5)]
check("L2.min.1", (not v.get("ok")) or not defaulted, "a gate cannot be raised with package fields merely defaulted", {"created": v.get("ok"), "defaulted": defaulted})
check("L2.b4.min", (not v.get("ok")) or bool((g2rec or {}).get("options")), "a gate always carries at least one option", {"created": v.get("ok")})
check("L2.b10.min", (not v.get("ok")) or all("<" not in a for a in ((g2rec or {}).get("permitted_next_actions") or ["<none>"])), "permitted next actions are exact (no placeholders)", {"created": v.get("ok")})
gx = gate(k2, "Which vendor?")
k2.ok("gate", "present", gx)
v = k2.run("decide", gx, "--option", "C", "--by", "orchestrator", "--rationale", "x")
v2 = k2.run("decide", gx, "--option", "C")
check("L2.b4.answer2", not v.get("ok") and not v2.get("ok"), "an answer 'C' to a gate offering only A/B is refused", {"agent": (v.get("error") or {}).get("code"), "relay": (v2.get("error") or {}).get("code")})
cidx, gcit = cit(k2, "l2cit", trigger="architecture_change")
gr = k2.rec(gcit) or {}
check("L2.cit.b10", all("<" not in a for a in gr.get("permitted_next_actions") or ["<none>"]), "the CIT-P gate's permitted next actions are exact", gr.get("permitted_next_actions"))
ev = os.path.join(os.path.dirname(k2.root), "ev.json")
json.dump({"model": "m", "provider": "p", "task_class": "implementation", "reasoning_effort": "high", "cost": 99.0, "latency_ms": 1, "pass": True, "repair_count": 0, "reviewer_findings": 0, "task": "TASK-X"}, open(ev, "w"))
rb = k2.ok("route", "--record", ev)
bg = k2.rec(rb.get("human_gate") or "") or {}
missing = [f for f in FIELDS if bg.get(f) in (None, "", "not assessed", [])]
check("L2.budget.complete", not missing, "the budget-threshold gate carries every package field with substantive content", {"missing": missing})

f = [c for c, ok in RESULTS if not ok]
print(f"SUMMARY checks={len(RESULTS)} pass={len(RESULTS) - len(f)} fail={len(f)} failed={f}", flush=True)
