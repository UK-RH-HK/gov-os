#!/usr/bin/env python3
"""P2-AR-0034 (WS-3, repair iteration 1, round 3) — black-box supplementary probe. Builder regression evidence
(Contract v3 O3), not acceptance evidence. Every line drives a real `gov` binary on disposable projects and simulated
machines (r3_machine.py; owner material from PUBLISHED seeds only). Run it against the base binary (negative control)
and the round-3 binary.

Sections
  ADJ2    P2-ADJ-0002: OS-written facts (gates, decisions, CIT state, plugin registrations, governed evidence) written on
          one of the owner's provisioned machines are honoured on another after a clone/pull; records from a machine
          provisioned without the owner's binding authority, an unprovisioned machine, another owner's machine and a
          hand edit are refused, typed; no secret in the repository; root succession revokes
  RESEAL  continuity: records sealed while provisioned become portable; unprovisioned-era records do not
  CS      BC-P2-31: emergency-control state in the operational store
  T2C     WS-2 R3-11: the plugin registry in t2::audit
  HOOKS   WS-4 R2-12: generated provider hooks call gov checkpoint / session close
  HO      IP-R2-5 / IP-WS10-15: upstream_export and experiment_promotion gates are human-only
  EV      IP-WS10-02: a gate rests only on governed research
  G0      the reseal is an L4 project write

Usage: R3-WS03-probes.py <gov binary> <scratch dir>
"""
import json
import os
import shutil
import stat
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r3_machine import (BINDING_KEY, FOREIGN_BINDING_KEY, FOREIGN_HUMAN, FOREIGN_ROOT, FOREIGN_T2, PKG,  # noqa: E402
                        Machine, authority_id_of, bundle_text, check, err, root_text, summary)

GOV, SCR = sys.argv[1], sys.argv[2]
os.makedirs(SCR, exist_ok=True)
EMBED_OK = '{"protocol":"gov-capability/1","ok":true,"provider":{"id":"p","version":"1"},"outputs":{"vectors":[],"dim":8}}'


def res(d):
    return d.get("result") or {}


def write(m, rel, text):
    p = os.path.join(m.p, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(text)


def yaml_write(m, rel, obj):
    write(m, rel, json.dumps(obj))  # JSON is valid YAML


_PAYLOAD = []


def payload_of_binary():
    """The kernel payload embedded in the binary under test (a bootstrap install on a throw-away machine), so the
    signed release a provisioned machine installs is exactly this binary's payload."""
    if not _PAYLOAD:
        p0 = Machine(GOV, SCR, "P0", fixture="greenfield")
        r = p0.g("init", "--name", "p0", "--alias", "p0", "--skip-index")
        assert r.get("ok"), r
        stage = os.path.join(p0.base, "payload")
        shutil.copytree(os.path.join(p0.p, "governance/kernel"), stage)
        _PAYLOAD.append(stage)
    return _PAYLOAD[0]


def fresh_provisioned(tag, root=None, binding=True, fixture="greenfield"):
    """The documented first run: provision the owner's root (and, optionally, install the owner's binding authority),
    then install a release signed under that root."""
    m = Machine(GOV, SCR, tag, fixture=fixture)
    assert m.provision(root).get("ok")
    ib = m.install_binding() if binding else None
    r = m.g("init", "--source", m.signed_release(payload_of_binary(), 1), "--name", tag.lower(), "--alias", tag.lower(),
            "--skip-index")
    assert r.get("ok"), r
    m.commit("provisioned, then installed")
    return m, ib


def join_clone(src, tag, root=None, binding=True):
    m = Machine(GOV, SCR, tag, clone_of=src)
    if root is not False:
        assert m.provision(root).get("ok")
        m.reanchor()
        if binding:
            m.install_binding()
    return m


# ============================================================================================ ADJ2
A, ib = fresh_provisioned("A")
check("ADJ2.a", ib and ib.get("ok") and res(ib).get("sealing", {}).get("scope") == "provisioned"
      and res(ib).get("authority_id") == authority_id_of(BINDING_KEY),
      "the owner's T2 binding authority installs on a provisioned machine and new seals take the provisioned scope",
      res(ib) if ib and ib.get("ok") else (ib or {}).get("error") or (ib or {}).get("raw"))
yaml_write(A, "spec/features/F-0001.yaml", {"id": "F-0001", "type": "feature", "title": "Totals", "status": "ACTIVE",
           "state_class": "AUTHORITATIVE", "requirements": ["REQ-0001"], "readiness": {"requirements": "PRESENT"}})
yaml_write(A, "spec/requirements/REQ-0001.yaml", {"id": "REQ-0001", "type": "requirement", "title": "Totals are exact",
           "status": "ACTIVE", "state_class": "AUTHORITATIVE", "feature": "F-0001", "kind": "functional",
           "statement": "totals are integer cents", "acceptance_criteria": ["2 x 199 = 398"]})
write(A, "tools/t2p.sh", "#!/bin/sh\ncat >/dev/null\nprintf '%s\\n' '" + EMBED_OK + "'\n")
yaml_write(A, "governance/project/plugins/t2p.yaml", {"plugin_id": "t2p", "capability": "embed", "version": "1",
           "command": ["sh", "tools/t2p.sh"]})
A.commit("spec and plugin")
A.g("rebuild-memory")
# (1) a gate answered by the owner on A, and its decision
A.gate("HDG-0101", "Adopt integer cents?")
d1 = A.owner_decide("HDG-0101")
dec1 = res(d1).get("decision")
# (2) a gate raised on A, answered elsewhere
A.gate("HDG-0102", "Adopt the ledger layout?")
# (3) CIT state
mf = os.path.join(A.admin, "manifest.json")
open(mf, "w").write(json.dumps([{"op": "set_field", "target": "REQ-0001", "field": "statement", "value": "rounded half-even"}]))
c = A.g("cit", "propose", "--proposal", "rounding", "--trigger", "behaviour_change", "--targets", "REQ-0001", "--manifest", mf)
cid = res(c).get("id")
cgate = (res(c).get("simulation") or {}).get("human_gate")
if cgate:
    A.owner_decide(cgate)
# (4) a plugin registration approved by the owner
reg = A.g("plugins", "register", "--descriptor", os.path.join(A.p, "governance/project/plugins/t2p.yaml"), role="tooling-engineer")
if res(reg).get("human_gate"):
    A.owner_decide(res(reg)["human_gate"])
    reg = A.g("plugins", "register", "--descriptor", os.path.join(A.p, "governance/project/plugins/t2p.yaml"), role="tooling-engineer")
inv_a = A.g("capabilities", "invoke", "--plugin", "t2p", "--inputs", '{"texts": []}', role="tooling-engineer")
# (5) governed evidence
A.g("audit")
A.commit("T2 facts on machine A")
check("ADJ2.setup", d1.get("ok") and cid and res(reg).get("registered") and inv_a.get("ok"),
      "machine A wrote a gate answer + decision, a pending gate, CIT state, a plugin registration and a suite record",
      {"decide": err(d1), "cit": cid, "reg": res(reg).get("registered") or err(reg), "invoke": err(inv_a)})

B = join_clone(A, "B")
B.g("rebuild-memory")
t = B.t2("HDG-0101")
show = res(B.g("gate", "show", "HDG-0101"))
check("ADJ2.b", t.get("binding") == "VERIFIED" and (show.get("answer") or {}).get("verified") is True,
      "a gate the owner answered on machine A is honoured on the owner's machine B (answer verified)", t)
counts_b, fam_b = B.binding_counts()
check("ADJ2.c", counts_b == {}, "every T2 record and every governed evidence record written on A is honoured on B "
      "(os_binding_integrity reports nothing unverified)", counts_b)
d2 = B.owner_decide("HDG-0102")
check("ADJ2.d", d2.get("ok") and res(d2).get("answered_by_kind") == "human",
      "a gate raised on A is answered by the owner on B", err(d2))
ap = B.g("cit", "approve", cid, "--method", "human") if cid else {}
ex = B.g("cit", "execute", cid) if cid else {}
req = open(os.path.join(B.p, "spec/requirements/REQ-0001.yaml")).read()
check("ADJ2.e", ap.get("ok") and ex.get("ok") and "rounded half-even" in req,
      "a CIT simulated and answered on A is approved and executed on B (its sealed state and gate honoured)",
      {"approve": err(ap), "execute": err(ex)})
inv_b = B.g("capabilities", "invoke", "--plugin", "t2p", "--inputs", '{"texts": []}', role="tooling-engineer")
check("ADJ2.f", inv_b.get("ok"), "a plugin registered and approved on A runs on B", err(inv_b) or (inv_b.get("error") or {}).get("message", "")[:300])
suite_records = []
for dp, _dn, fn in os.walk(os.path.join(B.p, "spec")):
    for f in fn:
        txt = open(os.path.join(dp, f), errors="ignore").read()
        if "health:governance-suite" in txt and "hmac-sha256/t2-v2" in txt:
            suite_records.append(os.path.relpath(os.path.join(dp, f), B.p))
check("ADJ2.g", counts_b is not None and suite_records
      and not any(k.startswith("health-output:") for k in counts_b),
      "the governance-suite records written on A (sealed under the owner's authority) are honoured health evidence on B",
      {"suite_records": suite_records, "unverified": counts_b})
B.commit("T2 facts on machine B")
pull = A.pull(B)
t2a = A.t2("HDG-0102")
cit_a = res(A.g("cit", "show", cid)) if cid else {}
check("ADJ2.h", pull.returncode == 0 and t2a.get("binding") == "VERIFIED" and cit_a.get("cit_status") == "COMMITTED",
      "what B wrote (a gate answer, a CIT execution) is honoured on A after a pull", {"t2": t2a, "cit": cit_a.get("cit_status")})

# a machine provisioned for the owner but not given the binding authority
D = join_clone(A, "D", binding=False)
td = D.t2("HDG-0101")
apd = D.g("cit", "approve", cid, "--method", "human") if cid else {}
invd = D.g("capabilities", "invoke", "--plugin", "t2p", "--inputs", '{"texts": []}', role="tooling-engineer")
check("ADJ2.i", td.get("binding") == "FOREIGN" and err(apd) == "T2_UNBOUND" and err(invd) == "PLUGIN_REGISTRATION_UNBOUND",
      "on a machine provisioned WITHOUT the owner's binding authority, A's gate, CIT state and registration are refused",
      {"gate": td, "cit": err(apd), "plugin": err(invd)})
D.gate("HDG-0801", "Written on an unauthorised machine?")
shutil.copy(os.path.join(D.p, "spec/decisions/HDG-0801.yaml"), os.path.join(B.p, "spec/decisions/HDG-0801.yaml"))
tb = B.t2("HDG-0801")
pb = B.g("gate", "present", "HDG-0801")
check("ADJ2.j", tb.get("binding") == "FOREIGN" and tb.get("scope") == "machine" and err(pb) == "T2_UNBOUND",
      "a gate written on that unauthorised machine is refused on B (FOREIGN, machine scope; present T2_UNBOUND)", {"t2": tb, "present": err(pb)})

# an unprovisioned machine
U = join_clone(A, "U", root=False)
iu = U.install_binding()
check("ADJ2.k", err(iu) == "T2_AUTHORITY_UNPROVISIONED" and U.t2("HDG-0101").get("binding") == "FOREIGN",
      "an unprovisioned machine cannot install the authority and honours none of A's records", {"install": err(iu) or iu.get("raw")})
U2 = Machine(GOV, SCR, "U2", fixture="greenfield")
U2.g("init", "--name", "u2", "--alias", "u2", "--skip-index")
U2.gate("HDG-0701", "Written on an unprovisioned machine?")
shutil.copy(os.path.join(U2.p, "spec/decisions/HDG-0701.yaml"), os.path.join(B.p, "spec/decisions/HDG-0701.yaml"))
check("ADJ2.l", B.t2("HDG-0701").get("binding") == "FOREIGN", "a gate an unprovisioned machine wrote is refused on B", B.t2("HDG-0701"))

# another owner's machine
froot = root_text(root_keys=FOREIGN_ROOT, human=FOREIGN_HUMAN, t2=(FOREIGN_T2,))
F, _ = fresh_provisioned("F", root=froot, binding=False)
fi_owner = F.install_binding()  # the owner's bundle on another owner's machine
fi_own = F.install_binding(bundle_text(FOREIGN_BINDING_KEY, (FOREIGN_T2,)))
F.gate("HDG-0702", "Written on another owner's machine?")
shutil.copy(os.path.join(F.p, "spec/decisions/HDG-0702.yaml"), os.path.join(B.p, "spec/decisions/HDG-0702.yaml"))
tf = B.t2("HDG-0702")
check("ADJ2.m", err(fi_owner) == "T2_AUTHORITY_UNAUTHORISED" and fi_own.get("ok") and tf.get("binding") == "FOREIGN"
      and tf.get("scope") == "provisioned",
      "another owner's root does not authorise the owner's bundle; what that machine seals is FOREIGN on B",
      {"owner-bundle": err(fi_owner), "own": err(fi_own), "t2": tf})

# a hand edit on B
rel = os.path.join(B.p, "spec/decisions", f"{dec1}.yaml") if dec1 else None
if rel and os.path.exists(rel):
    good = open(rel).read()
    open(rel, "w").write(good.replace("chosen_option: A", "chosen_option: B"))
    cnt, _ = B.binding_counts()
    open(rel, "w").write(good)
else:
    cnt = None
check("ADJ2.n", (cnt or {}).get("BROKEN") == 1, "a hand-edited decision written on A is BROKEN on B", cnt)

# no secret in any repository; the key is protected machine material
keyhex = BINDING_KEY.hex()
leak = []
for m in (A, B):
    for f in m.git("ls-files").stdout.split():
        try:
            if keyhex in open(os.path.join(m.p, f), errors="ignore").read():
                leak.append(f)
        except IsADirectoryError:
            pass
kf = os.path.join(B.state_dir(), "t2-binding", "authorities", authority_id_of(BINDING_KEY), "key.json")
mode = oct(stat.S_IMODE(os.stat(kf).st_mode)) if os.path.exists(kf) else None
check("ADJ2.o", not leak and mode == "0o600", "the binding key is in no tracked file and is kept 0600 in machine state",
      {"leaks": leak, "mode": mode})

# the owner revokes: a root successor without the `t2-binding` delegation
v2 = B.g("trust", "root-update", "--anchor", B.admin_file("root-v2.json", root_text(version=2, t2=())))
tr = B.t2("HDG-0101")
st = res(B.g("trust", "t2-binding"))
check("ADJ2.p", v2.get("ok") and tr.get("binding") == "UNAUTHORISED" and (st.get("sealing") or {}).get("scope") == "machine",
      "a root successor that drops the binding role revokes the authority on B (UNAUTHORISED) and sealing falls back",
      {"root-update": err(v2), "t2": tr, "sealing": st.get("sealing")})

# ============================================================================================ RESEAL
R = Machine(GOV, SCR, "R", fixture="greenfield")
R.g("init", "--name", "rs", "--alias", "rs", "--skip-index")
R.gate("HDG-0401", "Sealed while unprovisioned?")
time.sleep(1.2)
R.provision()
R.reanchor()
R.gate("HDG-0402", "Sealed while provisioned, before the authority?")
R.install_binding()
dry = R.g("trust", "t2-binding", "--reseal", "--dry-run")
paths = [f.get("path", "") for f in res(dry).get("resealed_files", [])]
rs = R.g("trust", "t2-binding", "--reseal")
R.commit("resealed")
R2 = join_clone(R, "R2")
check("RESEAL.a", any(p.endswith("HDG-0402.yaml") for p in paths) and not any(p.endswith("HDG-0401.yaml") for p in paths)
      and rs.get("ok") and R2.t2("HDG-0402").get("binding") == "VERIFIED" and R2.t2("HDG-0401").get("binding") == "FOREIGN",
      "reseal makes what the machine sealed while provisioned portable, and nothing it sealed while unprovisioned",
      {"dry": paths, "reseal": err(rs), "mid@R2": R2.t2("HDG-0402").get("binding"), "early@R2": R2.t2("HDG-0401").get("binding")})
g0 = R.g("trust", "t2-binding", "--reseal", role="product-spec-agent")
check("G0.a", err(g0) == "AUTHORITY_DENIED", "the reseal is an L4 project write (an L2 role is refused)", err(g0) or g0.get("raw"))

# ============================================================================================ CS (BC-P2-31)
C, _ = fresh_provisioned("C", binding=False)
C.g("freeze-writes", "--reason", "incident")
store = os.path.exists(os.path.join(C.p, ".governance-state/control.json"))
legacy = os.path.exists(os.path.join(C.p, ".governance-runtime/control.json"))
check("CS.a", store and not legacy, "FREEZE_WRITES is recorded in the operational store, not the derived runtime directory",
      {"store": store, "legacy": legacy})
shutil.rmtree(os.path.join(C.p, ".governance-runtime"), ignore_errors=True)
stc = res(C.g("status")).get("control") or {}
tc = C.g("task", "create", "--objective", "x")
check("CS.b", stc.get("writes_frozen") is True and err(tc) == "FROZEN",
      "deleting the whole derived runtime directory does not lift the freeze", {"control": stc, "task create": err(tc)})
C.g("resume")
os.makedirs(os.path.join(C.p, ".governance-runtime"), exist_ok=True)
open(os.path.join(C.p, ".governance-runtime/control.json"), "w").write(json.dumps({"mode": "RUNNING", "writes_frozen": True}))
tl = C.g("task", "create", "--objective", "x")
C.g("resume")
check("CS.c", err(tl) == "FROZEN" and not os.path.exists(os.path.join(C.p, ".governance-runtime/control.json"))
      and res(C.g("status")).get("control", {}).get("writes_frozen") is False,
      "a legacy freeze left by an older binary is honoured, and the next control command resolves it into the store", err(tl))

# ============================================================================================ T2C (registry in t2::audit)
write(C, "tools/rp.sh", "#!/bin/sh\ncat >/dev/null\nprintf '%s\\n' '" + EMBED_OK + "'\n")
yaml_write(C, "governance/project/plugins/rp.yaml", {"plugin_id": "rp", "capability": "embed", "version": "1", "command": ["sh", "tools/rp.sh"]})
r1 = C.g("plugins", "register", "--descriptor", os.path.join(C.p, "governance/project/plugins/rp.yaml"), role="tooling-engineer")
if res(r1).get("human_gate"):
    C.owner_decide(res(r1)["human_gate"])
    C.g("plugins", "register", "--descriptor", os.path.join(C.p, "governance/project/plugins/rp.yaml"), role="tooling-engineer")
rp = os.path.join(C.p, "governance/generated/plugin-registry.json")
if os.path.exists(rp):
    doc = json.load(open(rp))
    if "rp" in doc.get("plugins", {}):
        doc["plugins"]["rp"]["approved_roles"] = ["all", "backend-engineer"]
        json.dump(doc, open(rp, "w"))
cnt, fam = C.binding_counts()
check("T2C.a", (cnt or {}).get("BROKEN", 0) >= 2 and "plugin-registration:rp" in json.dumps(C.g("audit", "--no-persist", "--family", "os_binding_integrity")),
      "a hand-edited plugin-registry entry (and the registry document) is reported by the T2 audit", cnt)

# ============================================================================================ HOOKS
H, _ = fresh_provisioned("H", binding=False)
H.g("adapters", "generate")
hf = os.path.join(H.p, "governance/generated/adapters/hooks/provider-hooks.json")
ok_hooks, detail = False, None
if os.path.exists(hf):
    hooks = {h["event"]: h for h in json.load(open(hf)).get("hooks", [])}
    runs = {}
    for ev in ("pre_compaction", "session_end", "model_switch"):
        h = hooks.get(ev)
        runs[ev] = h and H.g(*h["command"][1:], role="backend-engineer").get("ok")
    ck = os.path.join(H.p, "spec/reports/checkpoints")
    trig = set()
    for f in os.listdir(ck) if os.path.isdir(ck) else []:
        if f.startswith("CKPT-"):
            for line in open(os.path.join(ck, f)):
                if line.startswith("trigger:"):
                    trig.add(line.split(":", 1)[1].strip())
    ok_hooks = all(runs.values()) and {"before_compaction", "before_session_close", "before_model_switch"} <= trig
    detail = {"runs": runs, "triggers": sorted(trig), "verify": res(H.g("adapters", "verify")).get("ok")}
check("HOOKS.a", ok_hooks, "the generated provider hooks call gov checkpoint / session close and record the triggers", detail)

# ============================================================================================ HO, EV
out = {}
for trig in ("upstream_export", "experiment_promotion", "vendor_note"):
    gid = {"upstream_export": "HDG-0601", "experiment_promotion": "HDG-0602", "vendor_note": "HDG-0603"}[trig]
    H.gate(gid, f"resolve {trig}?", {"trigger": trig, "impact_radius": "R1", "confidence": 0.95,
                                   "reversibility": "reversible: revert the change"})
    H.g("gate", "present", gid)
    r = H.g("decide", gid, "--option", "A", "--by", "change-controller", "--rationale", "low impact",
            role="change-controller", session="S-resolver")
    out[trig] = err(r) or "ok"
check("HO.a", out.get("upstream_export") == "AUTHORITY_DENIED" and out.get("experiment_promotion") == "AUTHORITY_DENIED"
      and out.get("vendor_note") == "ok", "agent resolution is refused for upstream_export and experiment_promotion gates "
      "(control: an ordinary low-radius gate resolves)", out)
dr = H.g("research", "record", "--draft", "--fields", json.dumps({"title": "Cache options", "question": "Which cache?", "reason": "latency"}))
did = (res(dr).get("research") or {}).get("id")
ge = H.g("gate", "create", "--question", "Adopt caching?", "--fields", json.dumps(dict(PKG, derived_from=[did])))
check("EV.a", err(ge) == "EVIDENCE_NOT_CITABLE", "a gate resting on non-governed (draft) research is refused", err(ge) or res(ge).get("id"))

summary(GOV)
