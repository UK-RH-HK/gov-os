#!/usr/bin/env python3
"""Fourth independent held-out harness (WV-*) for Governance OS candidate 4.1.5.

Authored fresh for this re-verification; unknown to the builder and to the three previous verifier
sessions. Black-box through the `gov --json` contract only. Attacks the NEW 4.1.5 trust roots:
V-H1 (plugin registry), V-H2 (verified kernel), V-M1 (governed exceptions), D-0007 (trust classes),
and the ETXTBSY plugin-execution race.
"""
import json, os, shutil, subprocess, sys, tempfile, hashlib, threading, time, traceback
import yaml

CANON = os.environ["GOV_CANONICAL_ROOT"]
GOV = os.path.join(CANON, "target/release/gov")
OUT = os.environ.get("GOV_WV_OUT", os.path.dirname(os.path.abspath(__file__)))
WORK = tempfile.mkdtemp(prefix="gov-wv-")
RESULTS = []


def rec(sid, title, verdict, detail):
    RESULTS.append({"id": sid, "title": title, "verdict": verdict, "detail": detail})
    print(f"[{verdict}] {sid} {title}\n    {json.dumps(detail)[:1600]}", flush=True)


class Gov:
    def __init__(self, root, session="S-wv", role="orchestrator", env=None):
        self.root, self.session, self.role, self.xenv = root, session, role, env or {}

    def r(self, role): return Gov(self.root, self.session, role, self.xenv)
    def s(self, session): return Gov(self.root, session, self.role, self.xenv)

    def run(self, *args):
        env = dict(os.environ); env["GOV_CANONICAL_ROOT"] = CANON
        env.pop("GOV_SESSION", None); env.pop("GOV_ROLE", None); env.update(self.xenv)
        cmd = [GOV, "--json", "--root", self.root, "--session", self.session, "--role", self.role] + [str(a) for a in args]
        p = subprocess.run(cmd, capture_output=True, text=True, env=env)
        try:
            return json.loads(p.stdout.strip())
        except Exception:
            return {"ok": False, "error": {"code": "NO_JSON", "message": (p.stdout + p.stderr)[-1200:]}}

    def ok(self, *args):
        e = self.run(*args)
        if not e.get("ok"):
            raise RuntimeError(f"gov {' '.join(map(str,args))} FAILED: {json.dumps(e.get('error'))[:600]}")
        return e["result"]

    def err(self, *args):
        e = self.run(*args)
        if e.get("ok"):
            raise RuntimeError(f"gov {' '.join(map(str,args))} unexpectedly OK: {json.dumps(e.get('result'))[:400]}")
        return e["error"]

    def doctor(self):
        e = self.run("doctor")
        if e.get("ok"): return e["result"]
        d = (e.get("error") or {}).get("details")
        if isinstance(d, dict) and "checks" in d: return d
        raise RuntimeError(f"doctor no checks: {json.dumps(e)[:300]}")


def sh(cwd, *cmd): return subprocess.run(list(cmd), cwd=cwd, capture_output=True, text=True)
def git_init(root):
    sh(root, "git", "init", "-q"); sh(root, "git", "config", "user.email", "wv@x.invalid")
    sh(root, "git", "config", "user.name", "wv"); sh(root, "git", "add", "-A"); sh(root, "git", "commit", "-qm", "base")
def commit(root, m="wip"): sh(root, "git", "add", "-A"); sh(root, "git", "commit", "-qm", m)
def wr(root, rel, text):
    p = os.path.join(root, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(text)
def rd(root, rel): return open(os.path.join(root, rel)).read()
def ry(root, rel): return yaml.safe_load(rd(root, rel))
def wy(root, rel, d): wr(root, rel, yaml.safe_dump(d, sort_keys=False))


def init_project(tag, fix="greenfield", role="orchestrator"):
    root = os.path.join(WORK, tag)
    shutil.copytree(os.path.join(CANON, "fixtures", fix, "project"), root)
    git_init(root)
    Gov(root).r(role).ok("init", "--source", os.path.join(CANON, "framework"), "--name", tag, "--alias", tag)
    commit(root, "init")
    return root, Gov(root)


EVIL = """#!/usr/bin/env bash
printf 'EXECUTED %s\\n' "$1" >> "$GOV_WV_MARKER"
echo '{"protocol":"gov-capability/1","ok":false,"error":{"code":"NOPE","message":"probe"}}'
"""


def plant(root):
    wr(root, "tools/wvprobe.sh", EVIL)
    os.chmod(os.path.join(root, "tools/wvprobe.sh"), 0o755)


# ---------------------------------------------------------------------------
def WV01_plugin_registry_cannot_be_manufactured():
    """V-H1: descriptor content, forged provenance and a hand-written registry cannot grant execution."""
    root, g = init_project("wv01")
    marker = os.path.join(root, "wv-marker.txt")
    g = Gov(root, env={"GOV_WV_MARKER": marker})
    plant(root)
    os.makedirs(os.path.join(root, "governance/project/plugins"), exist_ok=True)
    obs = {}

    def desc(name, extra=""):
        wr(root, f"governance/project/plugins/{name}.yaml",
           f'plugin_id: {name}\ncapability: code_intel\ncommand: ["tools/wvprobe.sh", "{name}"]\nversion: "1"\nlanguages: ["python"]\n' + extra)

    def clr():
        d = os.path.join(root, "governance/project/plugins")
        for f in os.listdir(d): os.remove(os.path.join(d, f))
        if os.path.exists(marker): os.remove(marker)

    def mk(): return open(marker).read() if os.path.exists(marker) else ""

    # (a) L0 self-declared approved_roles + forged provenance + status
    clr(); desc("p-self", 'approved_roles: ["all"]\nprovenance:\n  registered_at: "2020-01-01T00:00:00Z"\n  method: manual\nstatus: active\n')
    lst = g.r("independent-auditor").ok("plugins", "list")
    obs["a_L0_usable"] = [u["plugin_id"] for u in lst["usable"]]
    g.r("independent-auditor").ok("rebuild-memory")
    obs["a_marker_after_L0_rebuild"] = mk()

    # (b) HAND-FORGED registry entry granting the plugin to everyone, keyed to the real descriptor bytes
    clr(); desc("p-forge")
    dpath = os.path.join(root, "governance/project/plugins/p-forge.yaml")
    dsha = hashlib.sha256(open(dpath, "rb").read()).hexdigest()
    impl_sha = hashlib.sha256((f"tools/wvprobe.sh:{hashlib.sha256(open(os.path.join(root,'tools/wvprobe.sh'),'rb').read()).hexdigest()}\n").encode()).hexdigest()
    forged = {"schema_version": "1.0.0", "plugins": {"p-forge": {
        "plugin_id": "p-forge", "capability": "code_intel", "version": "1",
        "descriptor_sha256": dsha, "implementation_sha256": impl_sha, "implementation_files": ["tools/wvprobe.sh"],
        "approved_roles": ["all"], "required_permission_classes": [], "permissions": {},
        "registration_gate": None, "registered_by_role": "human", "method": "gov plugins register"}}}
    wr(root, "governance/generated/plugin-registry.json", json.dumps(forged))
    lst = g.r("independent-auditor").ok("plugins", "list")
    obs["b_L0_usable_with_forged_registry"] = [u["plugin_id"] for u in lst["usable"]]
    g.r("independent-auditor").ok("rebuild-memory")
    obs["b_marker_after_L0"] = mk()
    # even L2 cannot be *granted* elevated perms by a forged registry: check floor still applies at L1
    lst1 = g.r("backend-engineer").ok("plugins", "list")  # L1
    obs["b_L1_usable_with_forged_registry"] = [u["plugin_id"] for u in lst1["usable"]]
    os.remove(os.path.join(root, "governance/generated/plugin-registry.json"))

    # (c) genuine registration by L4, then an L0 rebuild must NOT execute it (floor L2 applies to every execution)
    clr(); desc("p-reg")
    reg = g.r("orchestrator").run("plugins", "register", "--descriptor", os.path.join(root, "governance/project/plugins/p-reg.yaml"))
    obs["c_register_L4_ok"] = reg.get("ok")
    obs["c_marker_before"] = mk()
    g.r("independent-auditor").ok("rebuild-memory")
    obs["c_marker_after_L0_rebuild_of_registered"] = mk()
    # an L2 role rebuild: floor is L2, so a registered/hand-declared plugin may run for L2 (design)
    obs["c_marker_reset"] = None
    if os.path.exists(marker): os.remove(marker)
    g.r("security-engineer").ok("rebuild-memory")  # L2
    obs["c_marker_after_L2_rebuild"] = mk()

    # (d) tamper the descriptor after registration -> mismatch, never usable
    if os.path.exists(marker): os.remove(marker)
    desc("p-reg", 'command: ["tools/wvprobe.sh", "EVILNOW"]\n')  # rewrite command; sha changes
    # re-write the descriptor file fully (desc() appends extra but keeps command line first); make it truly different:
    wr(root, "governance/project/plugins/p-reg.yaml",
       'plugin_id: p-reg\ncapability: code_intel\ncommand: ["tools/wvprobe.sh", "TAMPERED"]\nversion: "1"\nlanguages: ["python"]\n')
    lst = g.r("security-engineer").ok("plugins", "list")
    obs["d_after_descriptor_edit_usable"] = [u["plugin_id"] for u in lst["usable"]]
    obs["d_denied_codes"] = [(x["plugin_id"], x["code"]) for x in lst["denied"]]
    g.r("security-engineer").run("rebuild-memory")
    obs["d_marker_after_tampered_descriptor"] = mk()

    bad = []
    if obs["a_L0_usable"]: bad.append("L0: self-declared approved_roles/provenance made a descriptor usable")
    if obs["a_marker_after_L0_rebuild"]: bad.append("L0 executed arbitrary command via self-authorising descriptor")
    if obs["b_L0_usable_with_forged_registry"]: bad.append("L0: a hand-forged registry entry made a plugin usable below the authority floor")
    if obs["b_marker_after_L0"]: bad.append("L0 executed arbitrary command via a forged registry entry")
    if obs["b_L1_usable_with_forged_registry"]: bad.append("L1: forged registry lowered the authority floor")
    if obs["c_marker_after_L0_rebuild_of_registered"]: bad.append("L0 executed a genuinely-registered plugin (floor not applied to every execution)")
    if obs["d_after_descriptor_edit_usable"] or obs["d_marker_after_tampered_descriptor"]: bad.append("an edited descriptor stayed usable after registration")
    # c_marker_after_L2_rebuild being non-empty is EXPECTED (design: floor L2), so it is not a failure.
    rec("WV-01", "plugin descriptors/registry cannot manufacture authorisation (V-H1)", "FAIL" if bad else "PASS",
        {"failures": bad, "observations": obs,
         "note": "L2 executing a hand-declared/registered non-elevated plugin is the declared TOOL_POLICY.plugins.min_authority=L2 contract, not a defect"})


# ---------------------------------------------------------------------------
def WV02_verified_kernel_trust_root():
    """V-H2: a present-but-tampered installed kernel fails closed for mutations; read paths surface the substitution."""
    root, g = init_project("wv02")
    obs = {}
    obs["trust_before"] = g.ok("kernel", "trust")["verified"]
    tid = g.r("orchestrator").ok("task", "create", "--title", "ctx", "--objective", "hold context", "--class", "implementation")["id"]
    # (a) tamper POLICY_PRECEDENCE to declare everything overridable, add a weakening override
    wr(root, "governance/kernel/policies/POLICY_PRECEDENCE.yaml",
       "policy: POLICY_PRECEDENCE\nversion: 1.0.0\nlayers: [a]\ndefault_mode: overridable\nrules:\n  - {key: AUTHORITY_POLICY.*, mode: overridable}\n  - {key: SECURITY_POLICY.*, mode: overridable}\n")
    pp = ry(root, "governance/project/PROJECT_POLICY.yaml")
    pp.setdefault("policy_overrides", {})["AUTHORITY_POLICY.authority_levels_required.create_task"] = "L0"
    wy(root, "governance/project/PROJECT_POLICY.yaml", pp)
    t = g.ok("kernel", "trust")
    obs["a_trust_verified"] = t["verified"]
    obs["a_trust_substituted"] = t["trust"].get("substituted_embedded_baseline")
    ov = g.ok("policy", "overrides")
    obs["a_applied"] = [f"{a['policy']}.{a['key']}" for a in ov.get("applied", [])]
    obs["a_kernel_trust_in_overrides"] = ov.get("kernel_trust", {}).get("verified")
    # mutation must be refused with KERNEL_TAMPERED
    e = g.r("independent-auditor").run("task", "create", "--title", "x", "--objective", "p", "--class", "implementation")
    obs["a_L0_task"] = {"ok": e.get("ok"), "code": (e.get("error") or {}).get("code")}
    e = g.r("orchestrator").run("task", "create", "--title", "x", "--objective", "p", "--class", "implementation")
    obs["a_L4_task"] = {"ok": e.get("ok"), "code": (e.get("error") or {}).get("code")}
    e = g.run("rebuild-memory")
    obs["a_rebuild"] = {"ok": e.get("ok"), "code": (e.get("error") or {}).get("code")}
    e = g.run("cit", "propose", "--proposal", "x", "--trigger", "security_change", "--manifest", "/dev/null")
    obs["a_cit"] = {"ok": e.get("ok"), "code": (e.get("error") or {}).get("code")}
    # read paths still work, from embedded baseline, and surface the substitution
    st = g.run("status"); obs["a_status_ok"] = st.get("ok")
    cx = g.run("context", "compile", tid)
    kt = None
    if cx.get("ok"):
        da = cx["result"].get("deterministic_authority") or {}
        for L in (da.get("authority_layers") or []):
            if L.get("layer") == 2: kt = L.get("kernel_trust")
    obs["a_context_kernel_trust_verified"] = kt.get("verified") if isinstance(kt, dict) else kt
    obs["a_context_surfaces_substitution"] = (isinstance(kt, dict) and kt.get("verified") is False) or (obs["a_kernel_trust_in_overrides"] is False)
    doc = g.doctor()
    obs["a_doctor_verdict"] = doc["verdict"]
    obs["a_D029"] = [{"ok": c["ok"], "sev": c["severity"]} for c in doc["checks"] if c["id"] == "D029"]

    # (b) override flow: under-authority cannot override; L4 raises a fingerprint-bound gate
    ov3 = g.r("change-controller").run("kernel", "override", "--reason", "probe")  # L3
    obs["b_override_L3"] = {"ok": ov3.get("ok"), "code": (ov3.get("error") or {}).get("code")}
    ov4 = g.r("orchestrator").ok("kernel", "override", "--reason", "deliberate local change")
    gate_id = ov4.get("human_gate")
    obs["b_override_L4_gate"] = gate_id
    # still refused before the gate is answered
    e = g.r("orchestrator").run("task", "create", "--title", "x", "--objective", "p", "--class", "implementation")
    obs["b_task_before_answer"] = {"ok": e.get("ok"), "code": (e.get("error") or {}).get("code")}
    g.r("orchestrator").ok("gate", "present", gate_id)
    g.r("human").ok("decide", gate_id, "--option", "A", "--by", "human")
    e = g.r("orchestrator").run("task", "create", "--title", "afteroverride", "--objective", "p", "--class", "implementation")
    obs["b_task_after_answer"] = {"ok": e.get("ok"), "code": (e.get("error") or {}).get("code")}
    # (c) a DIFFERENT subsequent tamper must invalidate the override (fingerprint bound)
    sec = ry(root, "governance/kernel/policies/SECURITY_POLICY.yaml"); sec["never_index_classes"] = []
    wy(root, "governance/kernel/policies/SECURITY_POLICY.yaml", sec)
    e = g.r("orchestrator").run("task", "create", "--title", "afternewtamper", "--objective", "p", "--class", "implementation")
    obs["c_task_after_new_tamper"] = {"ok": e.get("ok"), "code": (e.get("error") or {}).get("code")}

    bad = []
    if obs["a_trust_verified"]: bad.append("kernel trust reported verified after tampering the installed precedence file")
    if "AUTHORITY_POLICY.authority_levels_required.create_task" in obs["a_applied"]: bad.append("weakening override applied from a tampered kernel precedence file")
    if obs["a_L0_task"]["ok"]: bad.append("L0 created a task under a tampered kernel")
    if obs["a_L4_task"]["ok"]: bad.append("L4 created a task under a tampered kernel without an override gate")
    if obs["a_rebuild"]["ok"]: bad.append("rebuild-memory proceeded under a tampered kernel")
    if obs["a_L0_task"]["code"] != "KERNEL_TAMPERED" and obs["a_L4_task"]["code"] != "KERNEL_TAMPERED": bad.append("mutations refused but not with KERNEL_TAMPERED")
    if not obs["a_status_ok"]: bad.append("read-only status broke under a tampered kernel (should read the embedded baseline)")
    if not obs.get("a_context_surfaces_substitution"): bad.append("the kernel substitution is not surfaced anywhere (context/policy-overrides)")
    if obs["b_override_L3"]["ok"]: bad.append("an L3 role obtained a kernel-integrity override")
    if obs["b_task_before_answer"]["ok"]: bad.append("mutation allowed before the override gate was answered")
    if not obs["b_task_after_answer"]["ok"]: bad.append("a properly answered L4 override did not unblock mutations")
    if obs["c_task_after_new_tamper"]["ok"]: bad.append("the override survived a different subsequent tamper (fingerprint not bound)")
    rec("WV-02", "verified kernel trust root fails closed and is fingerprint-bound (V-H2)", "FAIL" if bad else "PASS",
        {"failures": bad, "observations": obs})


# ---------------------------------------------------------------------------
def WV03_exceptions_require_governed_decisions():
    """V-M1: a PROJECT_EXCEPTIONS entry applies only for a valid, current, sufficiently-approved, in-scope decision."""
    root, g = init_project("wv03")
    obs = {}

    def set_exc(entries):
        wy(root, "governance/project/PROJECT_EXCEPTIONS.yaml", {"schema_version": "1.0.0", "exceptions": entries})

    def decision(did, **kw):
        d = {"id": did, "type": "decision", "title": did, "status": "ACTIVE", "state_class": "AUTHORITATIVE",
             "question": "?", "chosen_option": "A", "rationale": "r"}
        d.update(kw)
        wy(root, f"spec/decisions/{did}.yaml", d)

    RELAX = {"id": "EXC-1", "policy": "BUDGET_POLICY", "key": "defaults.max_task_cost_usd", "value": 999, "decision": "D-X", "expires": "2099-01-01", "rationale": "p"}

    def applied():
        ov = g.ok("policy", "overrides")
        return {f"{a['policy']}.{a['key']}": a for a in ov.get("applied", [])}, {a.get("source"): a for a in ov.get("refused", [])}

    cases = {}
    # 1. fabricated (no record)
    set_exc([dict(RELAX, decision="D-NONE")]); a, r = applied(); cases["1_fabricated"] = "BUDGET_POLICY.defaults.max_task_cost_usd" in a
    # 2. points at a non-decision record (a task)
    wy(root, "spec/tasks/T-1.yaml", {"id": "T-1", "type": "task", "title": "t"})
    set_exc([dict(RELAX, decision="T-1")]); a, r = applied(); cases["2_wrong_type"] = "BUDGET_POLICY.defaults.max_task_cost_usd" in a
    # 3. valid, human-approved, in scope -> MUST apply
    decision("D-OK", human_approved=True, authorises_exceptions=["EXC-1"])
    set_exc([dict(RELAX, decision="D-OK")]); a, r = applied(); cases["3_valid_applies"] = "BUDGET_POLICY.defaults.max_task_cost_usd" in a
    # 4. valid decision but names a DIFFERENT key
    decision("D-OTHER", human_approved=True, authorises_exceptions=["EXC-OTHER"])
    set_exc([dict(RELAX, decision="D-OTHER")]); a, r = applied(); cases["4_wrong_scope"] = "BUDGET_POLICY.defaults.max_task_cost_usd" in a
    # 5. superseded
    decision("D-SUP", human_approved=True, authorises_exceptions=["EXC-1"], superseded_by="D-2")
    set_exc([dict(RELAX, decision="D-SUP")]); a, r = applied(); cases["5_superseded"] = "BUDGET_POLICY.defaults.max_task_cost_usd" in a
    # 6. revoked
    decision("D-REV", human_approved=True, authorises_exceptions=["EXC-1"], revoked=True)
    set_exc([dict(RELAX, decision="D-REV")]); a, r = applied(); cases["6_revoked"] = "BUDGET_POLICY.defaults.max_task_cost_usd" in a
    # 7. expired decision
    decision("D-EXP", human_approved=True, authorises_exceptions=["EXC-1"], expires="2000-01-01")
    set_exc([dict(RELAX, decision="D-EXP")]); a, r = applied(); cases["7_expired_decision"] = "BUDGET_POLICY.defaults.max_task_cost_usd" in a
    # 8. insufficient authority (not human, approver role is L1)
    decision("D-LOW", human_approved=False, approved_by_role="research-agent", authorises_exceptions=["EXC-1"])
    set_exc([dict(RELAX, decision="D-LOW")]); a, r = applied(); cases["8_low_authority"] = "BUDGET_POLICY.defaults.max_task_cost_usd" in a
    # 9. valid decision but aimed at a SECURITY key (never relaxable)
    decision("D-SEC", human_approved=True, authorises_exceptions=["EXC-SEC"], permits_policy_keys=["SECURITY_POLICY.*"])
    set_exc([{"id": "EXC-SEC", "policy": "SECURITY_POLICY", "key": "never_index_classes", "value": [], "decision": "D-SEC", "expires": "2099-01-01"}])
    a, r = applied(); cases["9_security_key_via_valid_decision"] = "SECURITY_POLICY.never_index_classes" in a
    # 10. valid decision aimed at an AUTHORITY key
    decision("D-AUTH", human_approved=True, permits_policy_keys=["AUTHORITY_POLICY.*"], authorises_exceptions=["EXC-AUTH"])
    set_exc([{"id": "EXC-AUTH", "policy": "AUTHORITY_POLICY", "key": "authority_levels_required.create_task", "value": "L0", "decision": "D-AUTH", "expires": "2099-01-01"}])
    a, r = applied(); cases["10_authority_key_via_valid_decision"] = "AUTHORITY_POLICY.authority_levels_required.create_task" in a

    obs["cases"] = cases
    bad = []
    for k in ("1_fabricated", "2_wrong_type", "4_wrong_scope", "5_superseded", "6_revoked", "7_expired_decision", "8_low_authority", "9_security_key_via_valid_decision", "10_authority_key_via_valid_decision"):
        if cases[k]: bad.append(f"{k}: exception applied when it must be refused")
    if not cases["3_valid_applies"]: bad.append("3_valid: a properly governed exception on a relaxable key was NOT applied")
    rec("WV-03", "policy exceptions require a real, current, in-scope, sufficiently-approved decision (V-M1)", "FAIL" if bad else "PASS",
        {"failures": bad, "observations": obs})


# ---------------------------------------------------------------------------
def WV04_tool_install_security_review_not_self_attested():
    """D-0007: `gov tools install` must not treat a descriptor's own security_review: passed as evidence."""
    root, g = init_project("wv04")
    obs = {}

    def descriptor(review=None, review_record=None):
        d = {"tool_id": "WVT-tool", "type": "CLI", "name": "wvtool", "version_pin": "1.0.0",
             "capabilities": [], "status": "proposed", "approved_roles": ["tooling-engineer"],
             "license": "MIT", "reversible": True, "cost_usd": 0, "required_permission_classes": [],
             "health_check": {"kind": "command_exists", "command": ["true"]},
             "install_command": ["true"], "uninstall_command": ["true"]}
        if review is not None: d["security_review"] = review
        if review_record is not None: d["security_review_record"] = review_record
        p = os.path.join(root, "wv-tool.json"); open(p, "w").write(json.dumps(d)); return p

    # (a) self-attested passed, no record -> not auto-installed (gate raised)
    r = g.r("tooling-engineer").ok("tools", "install", "--descriptor", descriptor(review="passed"))
    obs["a_selfattested"] = {"installed": r.get("installed"), "gate": r.get("human_gate"),
                             "review_check": [c for c in r.get("checks", []) if c["condition"] == "licence_and_security_satisfied"]}
    # (b) fabricated record id -> not auto-installed
    r = g.r("tooling-engineer").ok("tools", "install", "--descriptor", descriptor(review="passed", review_record="SR-DOES-NOT-EXIST"))
    obs["b_fabricated_record"] = {"installed": r.get("installed"), "gate": r.get("human_gate")}
    # (c) a real governed record -> licence_and_security_satisfied becomes true
    wy(root, "spec/reports/SR-1.yaml", {"id": "SR-1", "type": "report", "title": "security review", "status": "ACTIVE", "outcome": "passed"})
    r = g.r("tooling-engineer").ok("tools", "install", "--descriptor", descriptor(review="passed", review_record="SR-1"))
    obs["c_real_record"] = {"installed": r.get("installed"),
                            "review_check_ok": [c["ok"] for c in r.get("checks", []) if c["condition"] == "licence_and_security_satisfied"]}
    bad = []
    if obs["a_selfattested"]["installed"]: bad.append("tool auto-installed on a self-attested security_review")
    if obs["b_fabricated_record"]["installed"]: bad.append("tool auto-installed on a fabricated security_review_record")
    chk = obs["a_selfattested"]["review_check"]
    if chk and chk[0]["ok"]: bad.append("licence_and_security_satisfied passed on a self-attested review")
    if obs["c_real_record"]["review_check_ok"] and not obs["c_real_record"]["review_check_ok"][0]:
        bad.append("a real governed security-review record did not satisfy the condition")
    rec("WV-04", "tool install security_review is evidenced by a governed record, not self-attested (D-0007)", "FAIL" if bad else "PASS",
        {"failures": bad, "observations": obs})


# ---------------------------------------------------------------------------
def WV05_etxtbsy_plugin_race():
    """The ETXTBSY repair: repeated + concurrent (write-then-execute) plugin invocation never surfaces PLUGIN_SPAWN_FAILED."""
    root, g = init_project("wv05")
    os.makedirs(os.path.join(root, "governance/project/plugins"), exist_ok=True)
    good = '#!/usr/bin/env bash\nread -r _ 2>/dev/null\necho "{\\"protocol\\":\\"gov-capability/1\\",\\"ok\\":true,\\"result\\":{\\"symbols\\":[]}}"\n'
    wr(root, "tools/wvce.sh", good); os.chmod(os.path.join(root, "tools/wvce.sh"), 0o755)
    wr(root, "governance/project/plugins/wvce.yaml",
       'plugin_id: wvce\ncapability: code_intel\ncommand: ["tools/wvce.sh"]\nversion: "1"\nlanguages: ["python"]\n')
    reg = g.r("orchestrator").run("plugins", "register", "--descriptor", os.path.join(root, "governance/project/plugins/wvce.yaml"))
    obs = {"registered": reg.get("ok"), "errors": [], "runs": 0, "etxtbsy": 0}
    lock = threading.Lock()

    def worker(n):
        for i in range(6):
            # rewrite the executable immediately before invoking, to provoke ETXTBSY
            try:
                with open(os.path.join(root, "tools/wvce.sh"), "w") as f:
                    f.write(good)
                os.chmod(os.path.join(root, "tools/wvce.sh"), 0o755)
            except Exception:
                pass
            e = g.r("security-engineer").run("capabilities", "invoke", "--plugin", "wvce", "--inputs", '{"path":"src/x.py","content":"def f():\\n  return 1\\n"}')
            with lock:
                obs["runs"] += 1
                if not e.get("ok"):
                    code = (e.get("error") or {}).get("code"); msg = (e.get("error") or {}).get("message", "")
                    if code == "PLUGIN_SPAWN_FAILED" or "Text file busy" in msg or "os error 26" in msg:
                        obs["etxtbsy"] += 1
                    # a pin-drift refusal from concurrent rewrite is a governance decision, not a spawn failure; note it
                    obs["errors"].append(code)

    threads = [threading.Thread(target=worker, args=(n,)) for n in range(4)]
    [t.start() for t in threads]; [t.join() for t in threads]
    from collections import Counter
    obs["error_codes"] = dict(Counter(obs["errors"]))
    bad = []
    if obs["etxtbsy"]: bad.append(f"PLUGIN_SPAWN_FAILED/ETXTBSY surfaced {obs['etxtbsy']} times under the write-then-exec race")
    rec("WV-05", "ETXTBSY plugin-execution race handled under repeated/concurrent invocation", "FAIL" if bad else "PASS",
        {"failures": bad, "observations": obs,
         "note": "PLUGIN_PIN_MISMATCH from a concurrent rewrite is an expected governance refusal, not a spawn race"})


# ---------------------------------------------------------------------------
def WV06_no_regression_of_confirmed_repairs():
    """Spot-check earlier confirmed repairs still hold on 4.1.5: L0 authority, CIT decline, restricted exclusion, fresh-agent hash."""
    root, g = init_project("wv06")
    obs = {}
    tid = g.r("orchestrator").ok("task", "create", "--title", "ctx", "--objective", "hold", "--class", "implementation")["id"]
    # L0 cannot create a task (intact kernel)
    e = g.r("independent-auditor").run("task", "create", "--title", "x", "--objective", "p", "--class", "implementation")
    obs["L0_create_task"] = {"ok": e.get("ok"), "code": (e.get("error") or {}).get("code")}
    # restricted content excluded from the index (intact kernel)
    ds = ry(root, "governance/project/DATA_SENSITIVITY.yaml")
    ds.setdefault("classifications", []).append({"pattern": "customer/**", "class": "restricted", "reason": "p"})
    wy(root, "governance/project/DATA_SENSITIVITY.yaml", ds)
    wr(root, "customer/secret.md", "WVRESTRICTED terms\n"); commit(root, "restricted")
    rb = g.ok("rebuild-memory")
    obs["restricted_excluded"] = any("customer/" in (x.get("path", "") if isinstance(x, dict) else str(x)) for x in (rb.get("excluded") or []))
    q = g.run("memory", "query", "WVRESTRICTED")
    obs["restricted_retrievable"] = [h.get("path") for h in ((q.get("result") or {}).get("hits") or []) if "customer/" in (h.get("path") or "")]
    # CIT decline is final
    mf = os.path.join(root, ".governance-runtime/wv6m.json"); os.makedirs(os.path.dirname(mf), exist_ok=True)
    open(mf, "w").write(json.dumps([{"op": "write_file", "path": "docs/w.md", "content": "x\n"}]))
    c = g.r("change-controller").ok("cit", "propose", "--proposal", "t", "--trigger", "security_change", "--manifest", mf)
    cid = c["id"]
    if c.get("cit_status") != "SIMULATED": g.r("change-controller").ok("cit", "simulate", cid)
    show = g.r("change-controller").ok("cit", "show", cid)
    gate = show.get("human_gate") or show.get("gate")
    if not gate:
        # find gate that references this cit
        gl = g.ok("gate", "list"); gate = next((x["id"] for x in (gl if isinstance(gl, list) else []) if x.get("cit") == cid), None)
    g.r("orchestrator").ok("gate", "present", gate)
    g.r("human").ok("decide", gate, "--option", "B", "--by", "human")
    ap = g.r("change-controller").run("cit", "approve", cid)
    ex = g.r("change-controller").run("cit", "execute", cid)
    obs["cit_decline_then_approve"] = {"ok": ap.get("ok"), "code": (ap.get("error") or {}).get("code")}
    obs["cit_decline_then_execute"] = {"ok": ex.get("ok"), "code": (ex.get("error") or {}).get("code")}
    obs["cit_file_written"] = os.path.exists(os.path.join(root, "docs/w.md"))
    # fresh-agent deterministic reconstruction across a clone
    h1 = g.ok("context", "compile", tid).get("deterministic_hash")
    clone = os.path.join(WORK, "wv06-cloneB")
    sh(WORK, "git", "clone", "-q", root, clone)
    g2 = Gov(clone, session="S-fresh-agent")
    g2.ok("rebuild-memory")
    h2 = g2.ok("context", "compile", tid).get("deterministic_hash")
    obs["fresh_agent_hash_equal"] = (h1 == h2)
    obs["hashes"] = [h1, h2]
    bad = []
    if obs["L0_create_task"]["ok"]: bad.append("L0 created a task")
    if not obs["restricted_excluded"] or obs["restricted_retrievable"]: bad.append("restricted content indexed/retrievable")
    if obs["cit_decline_then_execute"]["ok"] or obs["cit_file_written"]: bad.append("a declined CIT executed / wrote its file")
    if not obs["fresh_agent_hash_equal"]: bad.append("fresh-agent reconstruction hash differs across a clone")
    rec("WV-06", "no regression: authority, sensitivity, CIT-decline, fresh-agent reconstruction", "FAIL" if bad else "PASS",
        {"failures": bad, "observations": obs})


for fn in [WV01_plugin_registry_cannot_be_manufactured, WV02_verified_kernel_trust_root,
           WV03_exceptions_require_governed_decisions, WV04_tool_install_security_review_not_self_attested,
           WV05_etxtbsy_plugin_race, WV06_no_regression_of_confirmed_repairs]:
    sid = fn.__name__.split("_")[0].replace("WV", "WV-")
    try:
        fn()
    except Exception:
        rec(sid, fn.__doc__ or fn.__name__, "ERROR", {"traceback": traceback.format_exc()[-2500:]})

from collections import Counter
summary = dict(Counter(r["verdict"] for r in RESULTS))
print("\nSUMMARY:", summary)
os.makedirs(OUT, exist_ok=True)
json.dump({"candidate_commit": sh(CANON, "git", "rev-parse", "HEAD").stdout.strip(), "summary": summary, "results": RESULTS},
          open(os.path.join(OUT, "wv-results.json"), "w"), indent=2)
