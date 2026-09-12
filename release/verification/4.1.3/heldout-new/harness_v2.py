#!/usr/bin/env python3
"""Fresh independent held-out harness for agentic-engineering-os repair candidate 4.1.3 (commit 26ab5b6).

Authored in a fresh verification session. None of these scenarios exists in the builder's suites
(tests/certification, runtime unit tests) or in the first verifier's harness (release/verification/4.1.2/heldout).
Black-box: every scenario drives `gov --json` (API-0002). Two binaries are used:
  * GOV413 = target/release/gov built from the candidate commit (4.1.3)
  * GOV412 = target/release/gov built from the rejected candidate commit 8ad06be (4.1.2 runtime) in a detached worktree,
    used only to create genuine 4.1.2 consumer state for the version-transition scenario.
Run: python3 release/verification/4.1.3/heldout-new/harness_v2.py [NV01 NV03 ...]
Env: GOV_CANONICAL_ROOT (default: repo root), GOV412_WORKTREE (default: scratchpad worktree), GOV_VERIFIER_OUT.
"""
import hashlib, json, os, re, shutil, sqlite3, subprocess, sys, tempfile, time, traceback
import yaml

CANON = os.environ.get("GOV_CANONICAL_ROOT") or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
GOV413 = os.path.join(CANON, "target/release/gov")
WT412 = os.environ.get("GOV412_WORKTREE") or "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/9eb6de6b-38b7-4c89-9b58-58286a9a599a/scratchpad/wt-412"
GOV412 = os.path.join(WT412, "target/release/gov")
REL413 = os.path.join(CANON, "release/releases/4.1.3")
REL412 = os.path.join(CANON, "release/releases/4.1.2")
OUT_DIR = os.environ.get("GOV_VERIFIER_OUT") or os.path.dirname(os.path.abspath(__file__))
WORK = tempfile.mkdtemp(prefix="gov-verifier2-")
RESULTS = []


def record(sid, title, verdict, detail, severity=None):
    RESULTS.append({"id": sid, "title": title, "verdict": verdict, "severity": severity, "detail": detail})
    print(f"[{verdict}] {sid} {title} :: {json.dumps(detail, default=str)[:500]}")


class Gov:
    def __init__(self, root, session="S-verifier2", role="orchestrator", binary=GOV413, canon=CANON, env=None):
        self.root, self.session, self.role, self.binary, self.canon, self.env = root, session, role, binary, canon, (env or {})
    def with_session(self, s): return Gov(self.root, s, self.role, self.binary, self.canon, self.env)
    def with_role(self, r): return Gov(self.root, self.session, r, self.binary, self.canon, self.env)
    def with_binary(self, b, canon): return Gov(self.root, self.session, self.role, b, canon, self.env)
    def with_env(self, k, v): e = dict(self.env); e[k] = v; return Gov(self.root, self.session, self.role, self.binary, self.canon, e)
    def run(self, *args):
        env = dict(os.environ); env["GOV_CANONICAL_ROOT"] = self.canon; env.pop("GOV_SESSION", None); env.pop("GOV_ROLE", None); env.update(self.env)
        cmd = [self.binary, "--json", "--root", self.root, "--session", self.session, "--role", self.role] + list(args)
        p = subprocess.run(cmd, capture_output=True, text=True, env=env)
        try: envl = json.loads(p.stdout.strip())
        except Exception: envl = {"ok": False, "error": {"code": "NO_JSON", "message": (p.stderr or p.stdout)[-800:]}}
        return p.returncode, envl
    def ok(self, *args):
        code, e = self.run(*args)
        if not e.get("ok"): raise RuntimeError(f"gov {' '.join(args)} failed ({code}): {json.dumps(e.get('error'))[:700]}")
        return e["result"]
    def try_(self, *args):
        return self.run(*args)


def sh(cwd, *cmd): return subprocess.run(list(cmd), cwd=cwd, capture_output=True, text=True)
def git_init(root):
    sh(root, "git", "init", "-q"); sh(root, "git", "config", "user.email", "v2@example.invalid"); sh(root, "git", "config", "user.name", "verifier2")
    sh(root, "git", "add", "-A"); sh(root, "git", "commit", "-q", "-m", "baseline")
def commit(root, msg="wip"): sh(root, "git", "add", "-A"); sh(root, "git", "commit", "-q", "-m", msg)
def head(root): return sh(root, "git", "rev-parse", "HEAD").stdout.strip()
def fixture(name, tag):
    root = os.path.join(WORK, f"{tag}-{name}"); shutil.copytree(os.path.join(CANON, "fixtures", name, "project"), root); git_init(root); return root
def rd(root, rel): return open(os.path.join(root, rel), encoding="utf-8").read()
def wr(root, rel, text):
    p = os.path.join(root, rel); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "w", encoding="utf-8").write(text)
class _L(yaml.SafeLoader): pass
_L.yaml_implicit_resolvers = {k: [(t, r) for (t, r) in v if t != "tag:yaml.org,2002:timestamp"] for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()}
def ry(root, rel): return yaml.load(rd(root, rel), Loader=_L)
def wy(root, rel, data): wr(root, rel, yaml.safe_dump(data, sort_keys=False))
def rj(root, rel): return json.loads(rd(root, rel))
def ex(root, rel): return os.path.exists(os.path.join(root, rel))
def db(root): return sqlite3.connect(os.path.join(root, ".governance-runtime/state.db"))
def sha(path): return hashlib.sha256(open(path, "rb").read()).hexdigest()
def tree_hash(root, skip=(".git", ".governance-runtime"), skip_prefix=()):
    h = hashlib.sha256()
    for dp, dn, fn in os.walk(root):
        dn[:] = sorted(d for d in dn if d not in skip)
        for f in sorted(fn):
            p = os.path.join(dp, f); rel = os.path.relpath(p, root)
            if any(rel.startswith(s) for s in skip_prefix): continue
            h.update(rel.encode()); h.update(sha(p).encode())
    return h.hexdigest()
def report_file(root, name, work, files, tests="not_applicable_with_reason"):
    p = os.path.join(root, ".governance-runtime", "reports"); os.makedirs(p, exist_ok=True)
    f = os.path.join(p, name + ".json"); open(f, "w").write(json.dumps({"work_completed": work, "files_changed": files, "tests": {"status": tests, "reason": "verifier2"}, "outcome": "success", "evidence": []})); return f
def doctor(g, cid):
    code, e = g.run("doctor"); r = e["result"] if e.get("ok") else e["error"]["details"]
    c = next((c for c in r["checks"] if c["id"] == cid), None)
    return (c["ok"], c["message"], r["verdict"]) if c else (None, "check missing", r["verdict"])
def doctor_all(g):
    code, e = g.run("doctor"); r = e["result"] if e.get("ok") else e["error"]["details"]
    return r["verdict"], {c["id"]: (c["ok"], c["severity"], c["message"][:160]) for c in r["checks"]}
def scenario(fn):
    def wrapper():
        try: fn()
        except Exception as e:
            record(fn.__name__, "harness exception", "ERROR", {"error": str(e)[:900], "trace": traceback.format_exc()[-1500:]})
    return wrapper
def write_exec(root, rel, text):
    wr(root, rel, text); os.chmod(os.path.join(root, rel), 0o755); return os.path.join(root, rel)

PY_EMBED_BASE = r'''
import hashlib, json, math, re, sys
TOKEN_RX = re.compile(r"[A-Za-z_][A-Za-z0-9_]{1,}|\d+")
STOP = {"the","a","an","of","to","and","or","in","on","for","is","are","be","by","with","as","at","it","this","that","from","was","we","our","not","no","yes","if","then","than","so","do","does"}
def tokenize(text):
    out=[]
    for t in TOKEN_RX.findall(text):
        low=t.lower()
        if low in STOP: continue
        out.append(low)
        parts=re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", t).replace("_"," ").lower().split()
        if len(parts)>1: out.extend(p for p in parts if p not in STOP)
    return out
def hashed(toks, dim):
    vec=[0.0]*dim; counts={}
    feats=list(toks)+[a+"_"+b for a,b in zip(toks,toks[1:])]
    for f in feats: counts[f]=counts.get(f,0)+1
    for f,c in counts.items():
        h=hashlib.sha1(f.encode()).digest(); idx=int.from_bytes(h[:4],"big")%dim; sign=1.0 if h[4]&1 else -1.0
        w=1.0+math.log(c)
        if len(f)>12 or "_" in f: w*=1.3
        vec[idx]+=sign*w
    n=math.sqrt(sum(v*v for v in vec)) or 1.0
    return [round(v/n,6) for v in vec]
def respond(ok, pid, outputs=None, error=None):
    r={"protocol":"gov-capability/1","ok":ok,"provider":{"id":pid,"version":"1"}}
    if ok: r["outputs"]=outputs
    else: r["error"]=error
    sys.stdout.write(json.dumps(r)); sys.stdout.flush()
req=json.loads(sys.stdin.read() or "{}")
if req.get("protocol")!="gov-capability/1": respond(False, PID, error={"code":"PROTOCOL_MISMATCH","message":"bad protocol"}); sys.exit(0)
inputs=req.get("inputs") or {}
'''

# ------------------------------------------------------------------------------------------------------------------
@scenario
def NV01_cit_approval_requires_an_actual_human_answer():
    """INV-008 / framework §47.2 & §52: CIT approval must rest on a presented AND answered gate, and a human's
    decline (option B) must stop the transaction. Neither the builder suite nor HV-11/HV-14/HV-17 tested this."""
    root = fixture("greenfield", "nv01"); g = Gov(root)
    g.ok("init", "--name", "nv01", "--alias", "nv01-alias")
    mf = os.path.join(root, ".governance-runtime/m1.json"); os.makedirs(os.path.dirname(mf), exist_ok=True)
    open(mf, "w").write(json.dumps([{"op": "write_file", "path": "src/hdr.rs", "content": "pub const H: u8 = 1;\n"}]))
    # (a) gate presented but never answered
    c = g.ok("cit", "propose", "--proposal", "tighten security headers", "--trigger", "security_change", "--manifest", mf)
    cid = c["id"]
    if c.get("cit_status") != "SIMULATED": g.ok("cit", "simulate", cid)
    rec = g.ok("cit", "show", cid); gate = rec.get("human_gate")
    assert gate, f"no human gate raised for a security_change CIT: {rec.get('impact')}"
    g.ok("gate", "present", gate)
    code_a, e_a = g.run("cit", "approve", cid, "--by", "owner", "--method", "human")
    approved_unanswered = bool(e_a.get("ok"))
    gate_after_a = g.ok("gate", "list")
    decision_a = e_a.get("result", {}).get("decision") if approved_unanswered else None
    dec_a = ry(root, f"spec/decisions/{decision_a}.yaml") if decision_a and ex(root, f"spec/decisions/{decision_a}.yaml") else None
    # (b) gate answered B (human declines)
    mf2 = os.path.join(root, ".governance-runtime/m2.json"); open(mf2, "w").write(json.dumps([{"op": "write_file", "path": "src/hdr2.rs", "content": "pub const H2: u8 = 2;\n"}]))
    c2 = g.ok("cit", "propose", "--proposal", "second security change", "--trigger", "security_change", "--manifest", mf2)
    cid2 = c2["id"]
    if c2.get("cit_status") != "SIMULATED": g.ok("cit", "simulate", cid2)
    gate2 = g.ok("cit", "show", cid2).get("human_gate")
    g.ok("gate", "present", gate2)
    d = g.ok("decide", gate2, "--option", "B", "--by", "owner", "--rationale", "declined by the human")
    cit_after_decline = g.ok("cit", "show", cid2).get("cit_status")
    code_b, e_b = g.run("cit", "approve", cid2, "--by", "owner", "--method", "human")
    approved_after_decline = bool(e_b.get("ok"))
    executed_after_decline = None; file_written = None
    if approved_after_decline:
        code_c, e_c = g.run("cit", "execute", cid2)
        executed_after_decline = bool(e_c.get("ok")); file_written = ex(root, "src/hdr2.rs")
    # (c) which AGENT roles can perform (a)? approve_cit_human requires L3: change-controller is an agent role at L3
    mf3 = os.path.join(root, ".governance-runtime/m3.json"); open(mf3, "w").write(json.dumps([{"op": "write_file", "path": "src/hdr3.rs", "content": "pub const H3: u8 = 3;\n"}]))
    c3 = g.ok("cit", "propose", "--proposal", "third security change", "--trigger", "security_change", "--manifest", mf3)
    cid3 = c3["id"]
    if c3.get("cit_status") != "SIMULATED": g.ok("cit", "simulate", cid3)
    gate3 = g.ok("cit", "show", cid3).get("human_gate")
    cc = g.with_role("change-controller")
    cc.ok("gate", "present", gate3)
    code_d, e_d = cc.run("cit", "approve", cid3, "--by", "someone", "--method", "human")
    agent_l3_approved_unanswered = bool(e_d.get("ok"))
    code_e, e_e = g.with_role("backend-engineer").run("cit", "approve", cid3, "--by", "someone", "--method", "human") if not agent_l3_approved_unanswered else (0, {"ok": None})
    fail = approved_unanswered or approved_after_decline or bool(executed_after_decline) or agent_l3_approved_unanswered
    record("NV-01", "CIT approval/execution require a presented AND answered gate; a human decline (option B) stops the transaction (INV-008, framework §47.2/§52)",
           "FAIL" if fail else "PASS",
           {"a_gate_presented_not_answered": {"approve_ok": approved_unanswered, "error_code": None if approved_unanswered else e_a["error"]["code"], "decision_record_written": decision_a, "decision_human_approved_flag": (dec_a or {}).get("human_approved"), "gate_status_after": [x for x in gate_after_a if x["id"] == gate]},
            "b_gate_answered_B": {"decide_result": d.get("option"), "cit_status_after_decline": cit_after_decline, "approve_ok": approved_after_decline, "approve_error": None if approved_after_decline else e_b["error"]["code"], "execute_ok": executed_after_decline, "manifest_file_written": file_written},
            "c_agent_roles": {"change_controller_L3_approved_unanswered_gate_as_human": agent_l3_approved_unanswered, "backend_engineer_L1_error": (e_e.get("error") or {}).get("code")}},
           severity="HIGH" if fail else None)

@scenario
def NV02_project_overlay_cannot_silently_override_security_or_authority_policy():
    """Framework §21: CONSTITUTION > SECURITY+AUTHORITY > PROJECT POLICY; a lower layer may never silently override a
    higher one. PROJECT_POLICY.policy_overrides is an unconstrained object: can it lower authority levels and disable
    never_index_classes without any decision, exception record or finding?"""
    root = fixture("greenfield", "nv02"); g = Gov(root)
    g.ok("init", "--name", "nv02", "--alias", "nv02-alias")
    pp = ry(root, "governance/project/PROJECT_POLICY.yaml")
    pp["policy_overrides"] = {"AUTHORITY_POLICY.authority_levels_required.create_task": "L0", "AUTHORITY_POLICY.authority_levels_required.execute_cit": "L0", "AUTHORITY_POLICY.authority_levels_required.install_kernel": "L0", "SECURITY_POLICY.never_index_classes": [], "SECURITY_POLICY.never_export_classes": []}
    wy(root, "governance/project/PROJECT_POLICY.yaml", pp)
    ds = ry(root, "governance/project/DATA_SENSITIVITY.yaml"); ds["classifications"] = [{"pattern": "product/data/**", "class": "restricted", "reason": "customer data"}]; wy(root, "governance/project/DATA_SENSITIVITY.yaml", ds)
    wr(root, "product/data/customers.md", "# customers\nZULUQUARTZ7 is the restricted customer identifier that must never be retrievable.\n")
    commit(root, "override attempt")
    ok7, msg7, dv = doctor(g, "D007")
    code, e = g.run("audit", "--no-persist"); au = e["result"] if e.get("ok") else e["error"]["details"]
    findings_about_override = [f["message"] for f in au.get("findings", []) if "override" in f["message"].lower() or "AUTHORITY_POLICY" in f["message"] or "SECURITY_POLICY" in f["message"]]
    auditor = g.with_role("independent-auditor")  # L0
    code_t, e_t = auditor.run("task", "create", "--class", "documentation", "--objective", "L0 creates a task via overlay-lowered authority", "--status", "READY")
    l0_created_task = bool(e_t.get("ok"))
    r = g.ok("rebuild-memory")
    con = db(root); rows = con.execute("SELECT path, sensitivity FROM artifacts WHERE path LIKE 'product/data/%'").fetchall(); con.close()
    q = g.ok("memory", "query", "ZULUQUARTZ7", "--k", "5")
    restricted_retrievable = any(h["path"] == "product/data/customers.md" for h in q["hits"])
    excluded = [x for x in r.get("excluded", []) if x.get("path") == "product/data/customers.md"]
    fail = l0_created_task or restricted_retrievable
    record("NV-02", "project overlay policy_overrides cannot silently lower AUTHORITY_POLICY levels or empty SECURITY_POLICY.never_index_classes (framework §21 precedence; INV-006)",
           "FAIL" if fail else "PASS",
           {"doctor_D007_policies": (ok7, msg7, dv), "audit_verdict": au.get("verdict"), "audit_findings_mentioning_override": findings_about_override[:5],
            "L0_task_create_ok": l0_created_task, "L0_error": None if l0_created_task else e_t["error"]["code"],
            "restricted_file_indexed_rows": rows, "restricted_excluded_by_indexer": excluded, "restricted_content_retrievable": restricted_retrievable},
           severity="HIGH" if fail else None)

@scenario
def NV03_real_412_to_413_update_and_rollback():
    """Version transition with GENUINE 4.1.2 consumer state: project initialised and populated by the 4.1.2 binary
    (rejected candidate commit 8ad06be), then inspected/updated/rolled back by the 4.1.3 binary against the immutable
    release payload release/releases/4.1.3. The builder's update fixture only goes synthetic 4.1.1 -> 4.1.3."""
    assert os.path.exists(GOV412), f"4.1.2 binary missing at {GOV412}"
    root = fixture("greenfield", "nv03")
    g412 = Gov(root, binary=GOV412, canon=WT412)
    v = g412.ok("version"); assert v["version"] == "4.1.2", v
    r = g412.ok("init", "--source", os.path.join(WT412, "framework"), "--name", "upg-project", "--alias", "fx-upg", "--intent", "orders ledger")
    lock0 = ry(root, "governance/framework.lock")
    m412 = json.load(open(os.path.join(REL412, "manifest.json"))); m413 = json.load(open(os.path.join(REL413, "manifest.json")))
    # 4.1.2 project state that must survive
    pp = ry(root, "governance/project/PROJECT_POLICY.yaml"); pp["policy_overrides"] = {"MEMORY_POLICY.retrieval.default_k": 5}; wy(root, "governance/project/PROJECT_POLICY.yaml", pp)
    wy(root, "spec/decisions/D-0001.yaml", {"id": "D-0001", "type": "decision", "title": "Use integer cents", "status": "ACTIVE", "question": "money type?", "chosen_option": "A", "rationale": "no floating point", "human_approved": True})
    t = g412.ok("task", "create", "--class", "documentation", "--objective", "Write docs", "--status", "READY")
    wy(root, "governance/tests/memory/heldout.yaml", {"version": "1", "queries": [{"id": "HQ-001", "query": "Use integer cents", "expected_refs": ["D-0001"], "forbidden": [], "k": 3}, {"id": "HQ-002", "query": "\"XYLOPHONE-HELDOUT-MARKER\" only in the held-out file", "expected_refs": ["D-0001"], "forbidden": [], "k": 3}]})
    g412.ok("rebuild-memory")
    contract_before = ry(root, "governance/project/REPOSITORY_CONTRACT.yaml")
    tests_rule_before = next((p for p in contract_before["paths"] if p["pattern"] == "governance/tests/**"), None)
    commit(root, "4.1.2 state")
    lock_412_bytes = rd(root, "governance/framework.lock"); overlay_before = tree_hash(os.path.join(root, "governance/project")); idx_manifest_412 = rj(root, "governance/generated/index-manifest.json")
    # ---- 4.1.3 binary inspects the 4.1.2 project ----
    g = Gov(root)
    dv_pre, checks_pre = doctor_all(g)
    st = g.ok("status")
    chk = g.ok("update", "--check", "--source", os.path.join(REL413, "kernel"))
    # ---- apply ----
    code, e = g.run("update", "--apply", "--source", os.path.join(REL413, "kernel"))
    gate = e.get("error", {}).get("details", {}).get("gate") if not e.get("ok") else None
    approve_flag_only = g.ok("update", "--apply", "--source", os.path.join(REL413, "kernel"), "--approve", "--by", "owner") if gate else None
    if gate:
        g.ok("gate", "present", gate); g.ok("decide", gate, "--option", "A", "--by", "owner", "--rationale", "approve update")
    spec_before = tree_hash(os.path.join(root, "spec"), skip_prefix=("audits", "reports"))
    ap = g.ok("update", "--apply", "--source", os.path.join(REL413, "kernel"), "--approve", "--by", "owner")
    lock1 = ry(root, "governance/framework.lock")
    kv = g.ok("kernel", "verify")
    idx1 = rj(root, "governance/generated/index-manifest.json")
    contract_after = ry(root, "governance/project/REPOSITORY_CONTRACT.yaml")
    tests_rule_after = next((p for p in contract_after["paths"] if p["pattern"] == "governance/tests/**"), None)
    con = db(root); heldout_indexed = con.execute("SELECT path, lexical FROM artifacts WHERE path='governance/tests/memory/heldout.yaml'").fetchall(); con.close()
    qh = g.ok("memory", "query", "XYLOPHONE-HELDOUT-MARKER", "--k", "3")
    leak_hits = [h["artifact_id"] for h in qh["hits"]]
    dv_post, checks_post = doctor_all(g)
    ledger = [json.loads(l) for l in rd(root, "spec/reports/framework-updates.jsonl").splitlines() if l.strip()] if ex(root, "spec/reports/framework-updates.jsonl") else []
    pp2 = ry(root, "governance/project/PROJECT_POLICY.yaml")
    spec_after = tree_hash(os.path.join(root, "spec"), skip_prefix=("audits", "reports"))
    commit(root, "updated to 4.1.3")
    # ---- multi-machine after update ----
    clone = os.path.join(WORK, "nv03-machineB"); sh(WORK, "git", "clone", "-q", root, clone)
    gb = Gov(clone)
    dvb, cb = doctor_all(gb)
    rb = gb.ok("rebuild-memory")
    same_manifest = rb["manifest_hash"] == idx1["manifest_hash"]
    # ---- 4.1.2 binary looking at the upgraded project (downgrade view) ----
    dv_down, checks_down = doctor_all(g412)
    chk_down = g412.try_("update", "--check", "--source", os.path.join(REL413, "kernel"))
    # ---- rollback with 4.1.3 ----
    rbk = g.ok("update", "--rollback")
    lock2 = ry(root, "governance/framework.lock"); lock2_bytes = rd(root, "governance/framework.lock")
    kv2 = g.ok("kernel", "verify")
    dv_rb, checks_rb = doctor_all(g)
    ledger2 = [json.loads(l) for l in rd(root, "spec/reports/framework-updates.jsonl").splitlines() if l.strip()] if ex(root, "spec/reports/framework-updates.jsonl") else []
    rbk2 = g.try_("update", "--rollback")
    overlay_after_rb = tree_hash(os.path.join(root, "governance/project"))
    # 4.1.2 binary on the rolled-back project
    dv_412_rb, checks_412_rb = doctor_all(g412)
    detail = {
        "init_412": {"version": r.get("version"), "lock_release_hash_eq_412_manifest": lock0.get("release_hash") == m412["release_hash"], "lock_source": lock0.get("source"), "lock_release_commit_eq_project_head": lock0.get("release_commit") == head(root)},
        "413_on_412_project": {"doctor_verdict": dv_pre, "D005": checks_pre.get("D005"), "D010": checks_pre.get("D010"), "D025": checks_pre.get("D025"), "status_version": st["framework"]["version"]},
        "update_check": {k: chk.get(k) for k in ["current", "available", "compatible", "migration_path", "migration_path_complete", "certification", "human_gate_required", "recommendation"]}, "impact": chk.get("impact"),
        "apply_without_gate_error": e.get("error", {}).get("code"), "approve_flag_only_applied": (approve_flag_only or {}).get("applied"),
        "apply": {"applied": ap.get("applied"), "from": ap.get("from"), "to": ap.get("to"), "migrations": ap.get("details", {}).get("migrations"), "operations": ap.get("details", {}).get("operations"), "overlay_keys_changed": ap.get("details", {}).get("overlay_keys_changed"), "doctor": ap.get("details", {}).get("doctor"), "audit": ap.get("details", {}).get("audit")},
        "lock_after": {"version": lock1.get("version"), "release_hash_eq_413_manifest": lock1.get("release_hash") == m413["release_hash"], "release_commit": lock1.get("release_commit"), "manifest_release_commit": m413["release_commit"], "release_commit_eq_manifest": lock1.get("release_commit") == m413["release_commit"], "release_commit_eq_project_head": lock1.get("release_commit") == head(root) or lock1.get("release_commit") == sh(root, "git", "rev-parse", "HEAD~1").stdout.strip() or lock1.get("release_commit") == sh(root, "git", "rev-parse", "HEAD~2").stdout.strip(), "source": lock1.get("source"), "lock_schema_version": lock1.get("lock_schema_version"), "cli_version": lock1.get("cli_version")},
        "kernel_verify": kv.get("ok"), "index_version_after": idx1.get("index_version"), "index_embedder_after": idx1.get("embedder"), "index_lexical_after": idx1.get("lexical"),
        "overlay_preserved": {"policy_override": pp2.get("policy_overrides", {}).get("MEMORY_POLICY.retrieval.default_k"), "name": pp2.get("project", {}).get("name")},
        "spec_unchanged": spec_before == spec_after,
        "repository_contract_governance_tests_rule": {"before_update": tests_rule_before, "after_update": tests_rule_after, "template_4.1.3_lexical_index": next(p for p in yaml.safe_load(open(os.path.join(REL413, "kernel/overlay-templates/REPOSITORY_CONTRACT.yaml")))["paths"] if p["pattern"] == "governance/tests/**")["lexical_index"]},
        "heldout_file_in_index_after_update": heldout_indexed, "heldout_marker_query_hits": leak_hits,
        "doctor_after_update": {"verdict": dv_post, "failed": {k: v for k, v in checks_post.items() if not v[0]}},
        "update_ledger_entries": [(l.get("from"), l.get("to"), l.get("result")) for l in ledger],
        "machine_B": {"doctor_verdict_before_rebuild": dvb, "D009": cb.get("D009"), "rebuilt_manifest_equals_A": same_manifest},
        "412_binary_on_413_project": {"doctor_verdict": dv_down, "D005": checks_down.get("D005"), "D002": checks_down.get("D002"), "update_check": (chk_down[1].get("result") or chk_down[1].get("error", {})).get("downgrade") if chk_down[1].get("ok") else chk_down[1].get("error", {}).get("code")},
        "rollback": {"rolled_back_to": rbk.get("rolled_back_to"), "kernel_ok": rbk.get("kernel_ok"), "lock_version": lock2.get("version"), "lock_bytes_identical_to_412": lock2_bytes == lock_412_bytes, "overlay_bytes_identical": overlay_after_rb == overlay_before, "kernel_verify": kv2.get("ok"), "doctor_verdict": dv_rb, "D005": checks_rb.get("D005"), "D010": checks_rb.get("D010"), "ledger_has_rollback_entry": any(l.get("result") not in (None, "committed") for l in ledger2), "ledger_entries_after_rollback": [(l.get("from"), l.get("to"), l.get("result")) for l in ledger2], "second_rollback": rbk2[1].get("result") if rbk2[1].get("ok") else rbk2[1].get("error", {}).get("code")},
        "412_binary_after_rollback": {"doctor_verdict": dv_412_rb, "D005": checks_412_rb.get("D005"), "D010": checks_412_rb.get("D010")},
    }
    defects = []
    if not ap.get("applied"): defects.append("update did not apply")
    if lock1.get("version") != "4.1.3" or not detail["lock_after"]["release_hash_eq_413_manifest"]: defects.append("lock after update does not pin release 4.1.3")
    if not detail["lock_after"]["release_commit_eq_manifest"]: defects.append("framework.lock.release_commit is not the release's commit (provenance)")
    if lock1.get("source", "").startswith("/"): defects.append("framework.lock.source is an absolute machine path after update (init writes a logical label)")
    if not detail["spec_unchanged"]: defects.append("spec/ changed on update (INV-013)")
    if detail["overlay_preserved"]["policy_override"] != 5: defects.append("overlay override lost")
    if heldout_indexed or leak_hits: defects.append("held-out regression file is lexically indexed on an upgraded 4.1.2 project (L5 fix not migrated: M-4.1.2-4.1.3 has no overlay operation for governance/tests/**)")
    if not same_manifest: defects.append("machine B rebuild differs from A after update")
    if rbk.get("rolled_back_to") != "4.1.2" or not detail["rollback"]["lock_bytes_identical_to_412"] or not kv2.get("ok"): defects.append("rollback did not restore 4.1.2 byte-for-byte")
    if not detail["rollback"]["ledger_has_rollback_entry"]: defects.append("rollback leaves no entry in the framework-updates ledger (provenance of the current state)")
    sev = "HIGH" if any("provenance" in d and "release_commit" in d for d in defects) or "update did not apply" in defects or any("rollback did not" in d for d in defects) else ("MEDIUM" if defects else None)
    record("NV-03", "genuine 4.1.2 consumer (created by the 4.1.2 binary) updated to release 4.1.3 by the 4.1.3 binary, verified on a second machine, rolled back; lock/provenance/overlay/spec/index/ledger semantics", "FAIL" if defects else "PASS", {"defects": defects, **detail}, severity=sev)

@scenario
def NV04_plugin_descriptors_bypass_tool_governance():
    """Framework §28-30, §32 and TOOL_PERMISSIONS least authority: an executable capability must be registered,
    version-pinned, health-checked and permission-scoped, otherwise a Human Decision Gate. Plugin descriptors under
    governance/project/plugins/*.yaml are executable capabilities: are they governed at all?"""
    root = fixture("greenfield", "nv04"); g = Gov(root)
    g.ok("init", "--name", "nv04", "--alias", "nv04-alias", "--skip-index")
    marker = os.path.join(root, ".governance-runtime", "rogue-ran.txt")
    script = write_exec(root, ".governance-runtime/rogue.sh", "#!/bin/sh\ncat >/dev/null\necho ran > '%s'\nprintf '{\"protocol\":\"gov-capability/1\",\"ok\":true,\"provider\":{\"id\":\"rogue\",\"version\":\"1\"},\"outputs\":{\"vectors\":[],\"dim\":8}}'\n" % marker)
    # deliberately minimal descriptor: no version, no health, no permissions, no languages
    wy(root, "governance/project/plugins/rogue.yaml", {"plugin_id": "rogue", "capability": "embed", "command": [script]})
    schema = json.load(open(os.path.join(root, "governance/kernel/schemas/plugin-descriptor.schema.json")))
    try:
        import jsonschema; jsonschema.validate({"plugin_id": "rogue", "capability": "embed", "command": [script]}, schema); schema_accepts_minimal = True; schema_error = None
    except Exception as ex_:
        schema_accepts_minimal = False; schema_error = str(ex_)[:200]
    auditor = g.with_role("independent-auditor")  # L0, permissions [READ_REPO, RUN_TESTS]
    code, e = auditor.run("capabilities", "invoke", "--plugin", "rogue", "--inputs", "{}")
    ran_as_l0 = os.path.exists(marker)
    if os.path.exists(marker): os.remove(marker)
    plugins = g.ok("capabilities", "plugins")
    tools = g.ok("tools", "list")
    in_tool_registry = any(t.get("tool_id") == "rogue" or t.get("name") == "rogue" for t in tools.get("tools", []))
    res = g.ok("tools", "resolve", "--capability", "embed", "--role", "independent-auditor")
    dv, checks = doctor_all(g)
    plugin_checks = {k: v for k, v in checks.items() if "plugin" in v[2].lower()}
    code2, e2 = g.run("audit", "--no-persist"); au = e2["result"] if e2.get("ok") else e2["error"]["details"]
    plugin_findings = [f["message"] for f in au.get("findings", []) if "plugin" in f["message"].lower()]
    # pinned plugin runs during a full rebuild launched by an L0 role (rebuild_memory: L0)
    pp = ry(root, "governance/project/PROJECT_POLICY.yaml"); pp["policy_overrides"] = {"MEMORY_POLICY.embedding.provider": "rogue", "MEMORY_POLICY.embedding.dimensions": 8}; wy(root, "governance/project/PROJECT_POLICY.yaml", pp)
    code3, e3 = auditor.run("rebuild-memory")
    ran_on_rebuild_as_l0 = os.path.exists(marker)
    fail = ran_as_l0 or ran_on_rebuild_as_l0
    record("NV-04", "plugin descriptors (arbitrary commands) are governed like tools: registration/approval, version pin, health check, permission classes, schema validation; an L0 role cannot execute them",
           "FAIL" if fail else "PASS",
           {"descriptor_schema_accepts_minimal": schema_accepts_minimal, "schema_error": schema_error, "core_discovered_minimal_descriptor": any(p.get("plugin_id") == "rogue" for p in plugins), "L0_invoke_ok": e.get("ok"), "L0_invoke_error": None if e.get("ok") else e["error"]["code"], "rogue_command_executed_by_L0": ran_as_l0, "rogue_in_tool_registry": in_tool_registry, "tools_resolve_embed_for_auditor": {"tools": res.get("tools"), "gap": res.get("capability_gap")}, "doctor_verdict": dv, "doctor_plugin_checks": plugin_checks, "audit_plugin_findings": plugin_findings, "L0_rebuild_ok": e3.get("ok"), "L0_rebuild_error": None if e3.get("ok") else e3["error"]["code"], "rogue_executed_on_rebuild_by_L0": ran_on_rebuild_as_l0, "schema_enforced_by_core": "grep: plugin-descriptor schema is not referenced anywhere in runtime/src"},
           severity="HIGH" if fail else None)

@scenario
def NV05_task_close_mutation_scope_is_self_attested():
    """H4 was repaired by validating the report's files_changed. But the working tree knows what actually changed:
    does `task close` detect an out-of-scope modification that the worker omitted from files_changed?"""
    root = fixture("greenfield", "nv05"); g = Gov(root)
    g.ok("init", "--name", "nv05", "--alias", "nv05-alias")
    t = g.ok("task", "create", "--class", "documentation", "--objective", "write docs only", "--status", "READY", "--allowed", "docs/**")
    g.ok("task", "claim", t["id"])
    wr(root, "docs/notes.md", "# notes\n")
    with open(os.path.join(root, "src/lib.rs"), "a") as f: f.write("\npub fn injected_out_of_scope() -> u8 { 7 }\n")
    g.ok("rebuild-memory", "--incremental")
    dirty = sh(root, "git", "status", "--porcelain").stdout
    rep = report_file(root, "r1", "docs written", ["docs/notes.md"])
    code, e = g.run("task", "close", t["id"], "--report", rep)
    closed = bool(e.get("ok"))
    ck = None
    if closed:
        ckid = e["result"]["checkpoint"]; ck = ry(root, f"spec/reports/checkpoints/{ckid}.yaml")
    record("NV-05", "task close cross-checks the self-reported files_changed against the actual working-tree changes (git) for out-of-scope mutations",
           "FAIL" if closed else "PASS",
           {"git_dirty_at_close": dirty.strip().splitlines(), "reported_files_changed": ["docs/notes.md"], "close_ok": closed, "close_error": None if closed else e["error"]["code"], "checkpoint_files_changed": (ck or {}).get("files_changed"), "checkpoint_captured_out_of_scope_git_change": "src/lib.rs" in ((ck or {}).get("files_changed") or []), "note": "git status showed src/lib.rs modified while the report omitted it; close succeeded and the checkpoint copied the self-reported list, so the discrepancy was neither enforced nor recorded"},
           severity="MEDIUM" if closed else None)

@scenario
def NV13_framework_update_gate_decline_is_honoured_control():
    """Control for NV-01: the update path implements the same INV-008 rule; a gate answered B must stop `update --apply`."""
    root = fixture("greenfield", "nv13")
    g412 = Gov(root, binary=GOV412, canon=WT412)
    g412.ok("init", "--source", os.path.join(WT412, "framework"), "--name", "nv13", "--alias", "nv13-alias", "--skip-index")
    g412.ok("rebuild-memory"); commit(root, "412")
    g = Gov(root)
    code, e = g.run("update", "--apply", "--source", os.path.join(REL413, "kernel"))
    gate = e.get("error", {}).get("details", {}).get("gate")
    g.ok("gate", "present", gate); g.ok("decide", gate, "--option", "B", "--by", "owner", "--rationale", "stay on 4.1.2")
    ap = g.ok("update", "--apply", "--source", os.path.join(REL413, "kernel"), "--approve", "--by", "owner")
    lock = ry(root, "governance/framework.lock")
    ok = ap.get("applied") is False and lock.get("version") == "4.1.2"
    record("NV-13", "control: a framework-update gate answered B (decline) stops `update --apply --approve` and the lock stays at 4.1.2", "PASS" if ok else "FAIL", {"applied": ap.get("applied"), "reason": ap.get("reason"), "lock_version": lock.get("version")}, severity=None if ok else "HIGH")

@scenario
def NV19_migration_record_integrity():
    """A declarative migration is a governed record: its description and the release notes must not claim
    operations that its `operations` list does not perform (M-4.1.2-4.1.3 vs REPOSITORY_CONTRACT tightening / overlay keys)."""
    m = yaml.safe_load(open(os.path.join(REL413, "kernel/migrations/M-4.1.2-4.1.3.yaml")))
    ops = [o["op"] for o in m["operations"]]
    overlay_ops = [o for o in ops if "overlay" in o]
    claims_overlay_change = "repository-contract" in m["description"] or "tightened" in m["description"]
    notes = open(os.path.join(REL413, "RELEASE_NOTES.md")).read()
    notes_claim = "overlay gains the sensitivity / reranker / lexical keys" in notes
    tpl_changed = open(os.path.join(REL412, "kernel/overlay-templates/REPOSITORY_CONTRACT.yaml")).read() != open(os.path.join(REL413, "kernel/overlay-templates/REPOSITORY_CONTRACT.yaml")).read()
    inconsistent = (claims_overlay_change or notes_claim or tpl_changed) and not overlay_ops
    record("NV-19", "migration M-4.1.2-4.1.3 operations perform what its description and the release notes claim (overlay/contract changes)", "FAIL" if inconsistent else "PASS",
           {"operations": ops, "overlay_operations": overlay_ops, "description_claims_contract_tightening": claims_overlay_change, "release_notes_claim_overlay_keys": notes_claim, "overlay_template_changed_between_releases": tpl_changed, "affected_indexes": m.get("affected_indexes"), "breaking": m.get("breaking"), "human_gate": m.get("human_gate")}, severity="MEDIUM" if inconsistent else None)

SYN_EMBED = PY_EMBED_BASE + r'''
PID="syn-embed"
SYN={"upper":"limit","bound":"limit","maximum":"limit","max":"limit","cap":"limit","capped":"limit","ceiling":"limit",
     "repeated":"retry","attempts":"retry","attempt":"retry","retries":"retry","retried":"retry","retrying":"retry","reattempt":"retry",
     "payment":"gateway","provider":"gateway","processor":"gateway","psp":"gateway","calls":"call","call":"call","against":"call",
     "times":"limit","many":"limit"}
def canon(text): return [SYN.get(t,t) for t in tokenize(text)]
dim=int(inputs.get("dimensions",512))
vecs=[hashed(canon(t), dim) for t in (inputs.get("texts") or [])]
respond(True, PID, outputs={"vectors":vecs,"dim":dim})
'''

def run_brownfield_adoption(tag):
    root = fixture("brownfield", tag)
    sql = rd(root, "memory/chat_history.sql"); con = sqlite3.connect(os.path.join(root, "memory/chat_history.sqlite")); con.executescript(sql); con.commit(); con.close(); os.remove(os.path.join(root, "memory/chat_history.sql")); commit(root, "chat db")
    planner = Gov(root, "S-planner2")
    for s in ["baseline", "inventory", "classify", "map", "plan", "test-design"]: planner.ok("adopt", s)
    planner.with_session("S-reviewer2").with_role("migration-reviewer").ok("adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED")
    executor = planner.with_session("S-executor2").with_role("migration-executor")
    executor.ok("adopt", "migrate", "--name", "shipping-quotes", "--alias", "fx-brown")
    planner.with_session("S-verifier2b").with_role("migration-verifier").ok("adopt", "verify-migration")
    executor.ok("adopt", "extract-legacy"); executor.ok("adopt", "build-memory")
    planner.with_session("S-memverifier2").with_role("memory-verifier").ok("adopt", "verify-memory")
    return root, planner, executor

@scenario
def NV06_paraphrase_retrieval_through_governed_benchmark_and_selection():
    """HV-08b residual re-assessed on architecture, not builder intent: is the governed benchmark/select mechanism
    sufficient to obtain paraphrase retrieval for a repository, end to end, with a genuinely paraphrase-capable
    candidate that neither the builder nor the previous verifier shipped?"""
    root, planner, g = run_brownfield_adoption("nv06")
    queries = [
      {"id": "V-EXACT-1", "category": "exact_id", "query": "D-0002", "expected_refs": ["D-0002"], "forbidden": ["D-0001"], "k": 5},
      {"id": "V-PATH-1", "category": "exact_path", "query": "src/app/billing.py", "expected_refs": ["file:src/app/billing.py"], "forbidden": [], "k": 5},
      {"id": "V-LEX-1", "category": "lexical", "query": "\"failed after\" attempts", "expected_refs": ["file:src/app/retry.py"], "forbidden": [], "k": 5},
      {"id": "V-SYM-1", "category": "symbol", "query": "def with_retry", "expected_refs": ["file:src/app/retry.py"], "forbidden": [], "k": 5},
      {"id": "V-SEM-1", "category": "semantic_paraphrase", "query": "upper bound on repeated attempts against the payment provider", "expected_refs": ["D-0002"], "forbidden": ["D-0001"], "k": 8},
      {"id": "V-SEM-3", "category": "semantic_paraphrase", "query": "what is the maximum number of times a call to the payment processor may be reattempted", "expected_refs": ["D-0002"], "forbidden": ["D-0001"], "k": 8},
      {"id": "V-SUP-1", "category": "superseded_vs_current", "query": "How many times should gateway calls be retried?", "expected_refs": ["D-0002"], "forbidden": ["D-0001"], "k": 5},
      {"id": "V-GRAPH-1", "category": "graph", "query": "what depends on D-0002", "expected_refs": ["D-0002"], "forbidden": [], "k": 8},
      {"id": "V-XFILE-1", "category": "cross_file", "query": "which module imports ../util/http", "expected_refs": ["file:web/src/api/client.ts"], "forbidden": [], "k": 6},
      {"id": "V-MIX-1", "category": "mixed", "query": "ZONE_RATES pricing per zone in billing", "expected_refs": ["file:src/app/billing.py"], "forbidden": [], "k": 5},
    ]
    wy(root, "governance/tests/memory/heldout.yaml", {"version": "verifier2-1", "queries": queries})
    g.ok("rebuild-memory", "--incremental")
    code, e = g.run("memory", "verify"); base = e["result"] if e.get("ok") else e["error"]["details"]
    base_per = {x["id"]: x["recall"] for x in base["results"]}
    plugin = os.path.join(root, ".governance-runtime", "syn_embed.py"); os.makedirs(os.path.dirname(plugin), exist_ok=True); open(plugin, "w").write(SYN_EMBED)
    wy(root, "governance/project/plugins/syn.yaml", {"plugin_id": "syn-embed", "capability": "embed", "version": "1", "command": ["python3", plugin], "languages": []})
    t0 = time.time()
    b = g.ok("memory", "benchmark", "--candidate", "current", "--candidate", "plugin:syn-embed:512", "--candidate", "builtin:128", "--record")
    bench_s = round(time.time() - t0, 1)
    rows = {r["candidate"]: {k: r.get(k) for k in ["usable", "recall_at_k", "mrr", "precision_at_k", "stale_hit_rate", "superseded_hit_rate", "forbidden_violations", "symbol_recall", "avg_query_latency_ms", "index_ms", "vectors", "dimensions", "error"]} for r in b["rows"]}
    sem_by_cand = {r["candidate"]: [c for c in r.get("by_category", []) if c["category"] == "semantic_paraphrase"] for r in b["rows"] if r.get("usable")}
    research = b.get("research_record")
    sel = g.ok("memory", "select", "plugin:syn-embed:512", "--research", research, "--by", "owner")
    dec = ry(root, f"spec/decisions/{sel['decision']}.yaml")
    code, e2 = g.run("memory", "verify"); after = e2["result"] if e2.get("ok") else e2["error"]["details"]
    after_per = {x["id"]: (x["recall"], x["got"][:4]) for x in after["results"]}
    idx = rj(root, "governance/generated/index-manifest.json")
    q = g.ok("memory", "query", "upper bound on repeated attempts against the payment provider", "--k", "8")
    # plugin removed -> no silent fallback anywhere on the query path
    os.remove(os.path.join(root, "governance/project/plugins/syn.yaml"))
    code, e3 = g.run("memory", "query", "upper bound on repeated attempts", "--k", "3")
    no_fallback = (not e3.get("ok")) and e3["error"]["code"] in ("EMBEDDER_UNAVAILABLE", "EMBEDDER_MISMATCH")
    sem_ok_after = all(after_per[k][0] >= 1.0 for k in ("V-SEM-1", "V-SEM-3"))
    sem_fail_before = any(base_per[k] < 1.0 for k in ("V-SEM-1", "V-SEM-3"))
    mechanism_sufficient = sem_ok_after and after.get("pass") and idx["embedder"]["id"] == "syn-embed" and no_fallback and research and dec.get("chosen_option") == "plugin:syn-embed:512" and len(dec.get("options", [])) >= 2
    record("NV-06", "paraphrase retrieval obtained end-to-end through the governed mechanism (benchmark >= 3 candidates on a held-out set -> research record -> selection decision with alternatives -> overlay pin -> full rebuild), with no silent fallback",
           "PASS" if mechanism_sufficient else "FAIL",
           {"baseline_embedder_semantic_recall": {k: base_per[k] for k in ("V-SEM-1", "V-SEM-3")}, "baseline_pass": base.get("pass"), "baseline_recall_at_k": base.get("recall_at_k"), "baseline_mrr": base.get("mrr"),
            "benchmark_seconds": bench_s, "benchmark_rows": rows, "semantic_paraphrase_by_candidate": sem_by_cand, "recommended": b.get("recommended"), "research_record": research,
            "selection": {"decision": sel.get("decision"), "chosen": dec.get("chosen_option"), "alternatives_recorded": len(dec.get("options", [])), "human_approved": dec.get("human_approved"), "pinned": sel.get("pinned")},
            "after_selection": {"pass": after.get("pass"), "status": after.get("status"), "recall_at_k": after.get("recall_at_k"), "mrr": after.get("mrr"), "precision_at_k": after.get("precision_at_k"), "per_query": after_per},
            "live_index_embedder": idx.get("embedder"), "paraphrase_query_top": [h["artifact_id"] for h in q["hits"]][:5], "plugin_removed_query_error": e3.get("error", {}).get("code"), "no_silent_fallback": no_fallback, "baseline_failed_paraphrase_as_expected": sem_fail_before},
           severity=None if mechanism_sufficient else "HIGH")

@scenario
def NV07_incremental_rebuild_after_record_relocation():
    """Incremental indexing after a governed record file is moved (git mv) within spec/: the record must remain in the
    derived index, and freshness must not report a fresh index that lost it."""
    root = fixture("greenfield", "nv07"); g = Gov(root)
    g.ok("init", "--name", "nv07", "--alias", "nv07-alias")
    wy(root, "spec/decisions/D-0001.yaml", {"id": "D-0001", "type": "decision", "title": "Use integer cents", "status": "ACTIVE", "question": "money type?", "chosen_option": "A", "rationale": "no floating point", "human_approved": True})
    commit(root, "decision"); g.ok("rebuild-memory")
    con = db(root); before = con.execute("SELECT path FROM artifacts WHERE artifact_id='D-0001'").fetchall(); con.close()
    os.makedirs(os.path.join(root, "spec/decisions/2026"), exist_ok=True)
    sh(root, "git", "mv", "spec/decisions/D-0001.yaml", "spec/decisions/2026/D-0001.yaml"); commit(root, "moved")
    r = g.ok("rebuild-memory", "--incremental")
    con = db(root); after = con.execute("SELECT path FROM artifacts WHERE artifact_id='D-0001'").fetchall(); con.close()
    fr = g.ok("memory", "freshness")
    q = g.ok("memory", "query", "D-0001", "--k", "3")
    r2 = g.ok("rebuild-memory", "--incremental")
    con = db(root); after2 = con.execute("SELECT path FROM artifacts WHERE artifact_id='D-0001'").fetchall(); con.close()
    lost = not after
    record("NV-07", "a governed record survives an incremental rebuild after being moved (git mv) within spec/", "FAIL" if lost else "PASS",
           {"path_before": before, "path_after_first_incremental": after, "problems_reported": r.get("problems"), "removed": r.get("removed"), "indexed": r.get("indexed"), "fresh_after": fr.get("fresh"), "added": fr.get("added"), "structured_query_hits": [h["artifact_id"] for h in q["hits"]], "path_after_second_incremental": after2},
           severity="MEDIUM" if lost else None)

@scenario
def NV08_lock_provenance_release_commit_and_source():
    """framework.lock must identify the installed RELEASE: release_commit is the framework release commit
    (manifest.release_commit), not the consumer project's HEAD; source must be a machine-independent label."""
    root = fixture("greenfield", "nv08"); g = Gov(root)
    r = g.ok("init", "--source", os.path.join(REL413, "kernel"), "--name", "nv08", "--alias", "nv08-alias", "--skip-index")
    lock = ry(root, "governance/framework.lock"); m = json.load(open(os.path.join(REL413, "manifest.json")))
    root2 = fixture("greenfield", "nv08b"); g2 = Gov(root2)
    g2.ok("init", "--name", "nv08b", "--alias", "nv08b-alias", "--skip-index")  # embedded/canonical source
    lock2 = ry(root2, "governance/framework.lock")
    root3 = fixture("greenfield", "nv08c"); g3 = Gov(root3).with_env("GOV_CANONICAL_ROOT", "/nonexistent")
    g3.ok("init", "--name", "nv08c", "--alias", "nv08c-alias", "--skip-index")  # embedded payload
    lock3 = ry(root3, "governance/framework.lock")
    bad = lock["release_commit"] != m["release_commit"]
    record("NV-08", "framework.lock.release_commit identifies the framework release commit (manifest.release_commit), and source is a logical label on every install path",
           "FAIL" if bad else "PASS",
           {"install_from_release_dir": {"lock_release_commit": lock["release_commit"], "manifest_release_commit": m["release_commit"], "project_head": head(root), "equals_project_head": lock["release_commit"] == head(root), "source": lock["source"], "release_hash_eq_manifest": lock["release_hash"] == m["release_hash"]},
            "install_from_canonical_root": {"release_commit": lock2["release_commit"], "source": lock2["source"], "equals_project_head": lock2["release_commit"] == head(root2)},
            "install_from_embedded_payload": {"release_commit": lock3["release_commit"], "source": lock3["source"], "release_hash_eq_manifest": lock3["release_hash"] == m["release_hash"]}},
           severity="MEDIUM" if bad else None)

@scenario
def NV09_kernel_yaml_duplicate_key_and_manifest_schema_versions():
    """Kernel data hygiene: KERNEL.yaml must be valid YAML 1.2 (unique mapping keys) and its schema_versions must agree
    with the release manifest; strict loaders (serde_yaml Value, ruamel, yamllint) reject duplicate keys."""
    text = open(os.path.join(REL413, "kernel/KERNEL.yaml")).read()
    keys = re.findall(r"^\s{2}([a-z-]+):", text, flags=re.M)
    dups = sorted({k for k in keys if keys.count(k) > 1})
    class Strict(yaml.SafeLoader):
        def construct_mapping(self, node, deep=False):
            seen = set()
            for k, _ in node.value:
                key = self.construct_object(k, deep=deep)
                if key in seen: raise yaml.constructor.ConstructorError(f"duplicate key {key!r}")
                seen.add(key)
            return super().construct_mapping(node, deep)
    try: yaml.load(text, Loader=Strict); strict_ok = True; err = None
    except Exception as ex_: strict_ok = False; err = str(ex_)[:160]
    loose = yaml.safe_load(text); km = json.load(open(os.path.join(REL413, "kernel/KERNEL_MANIFEST.json"))); m = json.load(open(os.path.join(REL413, "manifest.json")))
    agree = loose["schema_versions"] == km["schema_versions"] == m["schema_versions"]
    src_same = open(os.path.join(CANON, "framework/KERNEL.yaml")).read() == text
    record("NV-09", "KERNEL.yaml is strict-YAML valid (no duplicate mapping keys) and schema_versions agree across KERNEL.yaml / KERNEL_MANIFEST.json / manifest.json", "FAIL" if dups or not strict_ok else "PASS",
           {"duplicate_keys": dups, "strict_loader_ok": strict_ok, "strict_error": err, "schema_versions_agree_after_last_wins": agree, "release_manifest_schema_version_in_kernel_yaml_last_wins": loose["schema_versions"].get("release-manifest"), "same_in_framework_source": src_same}, severity="LOW" if dups or not strict_ok else None)

RERANK_PLUGIN = r'''
import json, sys
req=json.loads(sys.stdin.read() or "{}")
if req.get("protocol")!="gov-capability/1":
    sys.stdout.write(json.dumps({"protocol":"gov-capability/1","ok":False,"provider":{"id":"pref-rerank","version":"1"},"error":{"code":"PROTOCOL_MISMATCH","message":"x"}})); sys.exit(0)
c=req.get("inputs",{}).get("candidates",[])
scores=[{"id":x["id"],"score":(10.0 if "PINEAPPLE-PREFERRED" in x.get("text","") else 1.0/(i+2))} for i,x in enumerate(c)]
sys.stdout.write(json.dumps({"protocol":"gov-capability/1","ok":True,"provider":{"id":"pref-rerank","version":"1"},"outputs":{"scores":scores}}))
'''

@scenario
def NV10_reranker_actually_reorders_results():
    """HV-02 proved the reranker is invoked; does its score actually govern the final order, and is the rerank
    score exposed with provenance in the hit?"""
    root = fixture("greenfield", "nv10"); g = Gov(root)
    g.ok("init", "--name", "nv10", "--alias", "nv10-alias", "--skip-index")
    for i, t in enumerate(["Order totals are exact integer cents", "Ledger rejects duplicate order identifiers", "Clerk appends two orders and reads the total PINEAPPLE-PREFERRED", "Order quantity must be positive"], 1):
        wy(root, f"spec/requirements/REQ-{i:04d}.yaml", {"id": f"REQ-{i:04d}", "type": "requirement", "title": t, "status": "ACTIVE", "kind": "functional", "acceptance_criteria": [t]})
    g.ok("rebuild-memory")
    before = [h["artifact_id"] for h in g.ok("memory", "query", "order totals ledger", "--k", "4")["hits"]]
    plugin = os.path.join(root, ".governance-runtime", "rr.py"); open(plugin, "w").write(RERANK_PLUGIN)
    wy(root, "governance/project/plugins/rr.yaml", {"plugin_id": "pref-rerank", "capability": "rerank", "version": "1", "command": ["python3", plugin], "languages": []})
    pp = ry(root, "governance/project/PROJECT_POLICY.yaml"); pp["policy_overrides"] = {"MEMORY_POLICY.reranker.provider": "pref-rerank"}; wy(root, "governance/project/PROJECT_POLICY.yaml", pp)
    code, e0 = g.run("memory", "query", "order totals ledger", "--k", "4")  # pinned but index built without it
    g.ok("rebuild-memory")
    res = g.ok("memory", "query", "order totals ledger", "--k", "4")
    after = [h["artifact_id"] for h in res["hits"]]
    scored = [(h["artifact_id"], h.get("rerank_score")) for h in res["hits"]]
    ok = after and after[0] == "REQ-0003" and res["reranker"]["provider"] == "pref-rerank" and scored[0][1] == 10.0
    record("NV-10", "a pinned reranker's scores govern the final ranking (not just invoked) and are exposed per hit", "PASS" if ok else "FAIL",
           {"order_before_pin": before, "query_with_pin_but_stale_index": e0.get("error", {}).get("code") if not e0.get("ok") else "ok(no mismatch raised)", "order_after": after, "rerank_scores": scored, "reranker_used": res.get("reranker")}, severity=None if ok else "MEDIUM")

@scenario
def NV12_embedder_pin_change_fails_closed_on_continue_and_context():
    """H1/C1 follow-through: after a policy pin change without rebuild, every consumer of the semantic route
    (gov continue -> context compile) must fail closed with EMBEDDER_MISMATCH instead of compiling a packet."""
    root = fixture("greenfield", "nv12"); g = Gov(root)
    g.ok("init", "--name", "nv12", "--alias", "nv12-alias")
    t = g.ok("task", "create", "--class", "documentation", "--objective", "Write docs", "--status", "READY")
    pp = ry(root, "governance/project/PROJECT_POLICY.yaml"); pp["policy_overrides"] = {"MEMORY_POLICY.embedding.dimensions": 64}; wy(root, "governance/project/PROJECT_POLICY.yaml", pp)
    code_c, e_c = g.run("continue")
    code_x, e_x = g.run("context", "compile", t["id"])
    code_s, e_s = g.run("status")
    fr = g.ok("memory", "freshness")
    closed = (not e_c.get("ok")) and e_c["error"]["code"] == "EMBEDDER_MISMATCH" and (not e_x.get("ok")) and e_x["error"]["code"] == "EMBEDDER_MISMATCH" and e_s.get("ok")
    record("NV-12", "after an embedder pin change without rebuild, gov continue / context compile fail closed (EMBEDDER_MISMATCH) while gov status still works", "PASS" if closed else "FAIL",
           {"continue": e_c.get("error", {}).get("code") if not e_c.get("ok") else "ok", "context_compile": e_x.get("error", {}).get("code") if not e_x.get("ok") else "ok", "status_ok": e_s.get("ok"), "freshness_pin_mismatch": fr.get("pin_mismatch"), "fresh": fr.get("fresh")}, severity=None if closed else "HIGH")

@scenario
def NV16_release_identity_reproducibility_and_immutability():
    """Release provenance: the released payload must equal the kernel data at manifest.release_commit, a rebuild of the
    same version from the candidate commit must reproduce the release_hash, and re-building an existing version must be
    refused (immutability)."""
    m = json.load(open(os.path.join(REL413, "manifest.json")))
    ver = subprocess.run([GOV413, "--json", "release", "verify", REL413], capture_output=True, text=True, env={**os.environ, "GOV_CANONICAL_ROOT": CANON}); v = json.loads(ver.stdout)
    rc = m["release_commit"]
    anc = sh(CANON, "git", "merge-base", "--is-ancestor", rc, "HEAD").returncode == 0
    diffs = sh(CANON, "git", "diff", "--stat", rc, "HEAD", "--", "framework", "migrations", "tools").stdout.strip()
    # payload at release_commit vs released kernel (file by file)
    ls = sh(CANON, "git", "ls-tree", "-r", "--name-only", rc, "--", "framework", "migrations", "tools").stdout.split()
    mismatched = []
    for p in ls:
        if p.endswith("README.md") and p.startswith("framework/"): continue
        rel = p[len("framework/"):] if p.startswith("framework/") else p
        blob = subprocess.run(["git", "show", f"{rc}:{p}"], cwd=CANON, capture_output=True).stdout
        target = os.path.join(REL413, "kernel", rel)
        if not os.path.exists(target) or open(target, "rb").read() != blob: mismatched.append(rel)
    extra = [k for k in m["file_hashes"] if not os.path.exists(os.path.join(CANON, "framework", k)) and not os.path.exists(os.path.join(CANON, k))]
    out = os.path.join(WORK, "nv16-release")
    build = subprocess.run([GOV413, "--json", "release", "build", "--version", "4.1.3", "--canonical", CANON, "--out", out, "--certification", "READY_FOR_INDEPENDENT_REVERIFICATION"], capture_output=True, text=True, env={**os.environ, "GOV_CANONICAL_ROOT": CANON}); b = json.loads(build.stdout)
    rebuilt = b.get("result", {})
    same_hash = rebuilt.get("release_hash") == m["release_hash"]
    same_files = rebuilt.get("file_hashes") == m["file_hashes"]
    imm = subprocess.run([GOV413, "--json", "release", "build", "--version", "4.1.3", "--canonical", CANON, "--out", os.path.join(CANON, "release")], capture_output=True, text=True, env={**os.environ, "GOV_CANONICAL_ROOT": CANON}); i = json.loads(imm.stdout)
    untouched = sh(CANON, "git", "status", "--porcelain", "--", "release/releases").stdout.strip() == ""
    ok = v["result"]["ok"] and anc and not mismatched and same_hash and same_files and (not i.get("ok")) and i["error"]["code"] == "RELEASE_IMMUTABLE" and untouched and not extra
    record("NV-16", "release 4.1.3 identity: verify ok, payload == kernel data at manifest.release_commit (ancestor of the candidate), rebuild from the candidate reproduces release_hash + file hashes, second build refused (RELEASE_IMMUTABLE), repository untouched",
           "PASS" if ok else "FAIL",
           {"release_verify": v["result"], "release_commit": rc, "release_commit_is_ancestor_of_HEAD": anc, "kernel_data_diff_release_commit_to_HEAD": diffs or "(none)", "payload_files_differing_from_release_commit": mismatched, "manifest_hashes_without_source_file": extra, "rebuild_release_hash_equal": same_hash, "rebuild_file_hashes_equal": same_files, "rebuild_release_commit": rebuilt.get("release_commit"), "immutability_error": i.get("error", {}).get("code"), "release_dir_untouched": untouched},
           severity=None if ok else "HIGH")

LOG_EMBED = PY_EMBED_BASE + r'''
PID="logging-embed"
import os
with open(os.environ.get("LOGFILE","/dev/null"),"a") as f:
    for t in (inputs.get("texts") or []): f.write(t.replace("\n"," ")+"\n")
dim=int(inputs.get("dimensions",512))
respond(True, PID, outputs={"vectors":[hashed(tokenize(t), dim) for t in (inputs.get("texts") or [])],"dim":dim})
'''

@scenario
def NV17_plugins_never_receive_secret_or_restricted_content():
    """API-0001 invariant and framework §16/§72: secret-class and never-index-class content must never reach an
    external embedding process (a plugin is an outbound boundary)."""
    root = fixture("greenfield", "nv17"); g = Gov(root)
    g.ok("init", "--name", "nv17", "--alias", "nv17-alias", "--skip-index")
    wr(root, "secrets/api.yaml", "token: AKIAIOSFODNN7EXAMPLE\nnote: SECRETMARKER-KUMQUAT\n")
    wr(root, "product/data/customers.md", "# customers\nRESTRICTEDMARKER-LOQUAT customer list\n")
    wr(root, "product/config.py", "API_KEY = 'AKIAIOSFODNN7EXAMPLE'\nPLANTEDMARKER-MANGO = 1\n")
    wr(root, "product/ok.md", "PUBLICMARKER-PAPAYA is fine to embed\n")
    ds = ry(root, "governance/project/DATA_SENSITIVITY.yaml"); ds["classifications"] = [{"pattern": "product/data/**", "class": "restricted", "reason": "customer data"}]; wy(root, "governance/project/DATA_SENSITIVITY.yaml", ds)
    commit(root, "content")
    logf = os.path.join(root, ".governance-runtime", "embed-inputs.log"); plugin = os.path.join(root, ".governance-runtime", "log_embed.py"); os.makedirs(os.path.dirname(plugin), exist_ok=True); open(plugin, "w").write(LOG_EMBED)
    wy(root, "governance/project/plugins/log.yaml", {"plugin_id": "logging-embed", "capability": "embed", "version": "1", "command": ["python3", plugin], "languages": []})
    pp = ry(root, "governance/project/PROJECT_POLICY.yaml"); pp["policy_overrides"] = {"MEMORY_POLICY.embedding.provider": "logging-embed", "MEMORY_POLICY.embedding.dimensions": 32}; wy(root, "governance/project/PROJECT_POLICY.yaml", pp)
    r = g.with_env("LOGFILE", logf).ok("rebuild-memory")
    q = g.with_env("LOGFILE", logf).ok("memory", "query", "PUBLICMARKER-PAPAYA customer list", "--k", "3")
    log = open(logf).read() if os.path.exists(logf) else ""
    leaks = {m: (m in log) for m in ["AKIAIOSFODNN7EXAMPLE", "SECRETMARKER-KUMQUAT", "RESTRICTEDMARKER-LOQUAT", "PLANTEDMARKER-MANGO"]}
    public_seen = "PUBLICMARKER-PAPAYA" in log
    record("NV-17", "an external embed plugin never receives secret-class, secret-content or restricted-class text (API-0001 invariant; framework §16/§72)", "FAIL" if any(leaks.values()) else "PASS",
           {"leaked_markers": leaks, "public_text_reached_plugin": public_seen, "excluded": r.get("excluded"), "secret_blocked": r.get("secret_blocked"), "log_lines": len(log.splitlines())}, severity="HIGH" if any(leaks.values()) else None)

if __name__ == "__main__":
    only = sys.argv[1:]
    for name, fn in list(globals().items()):
        if name.startswith("NV") and callable(fn) and (not only or any(name.startswith(o) for o in only)):
            t0 = time.time(); fn(); print(f"   ({time.time()-t0:.1f}s)")
    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump({"work_dir": WORK, "candidate_commit": sh(CANON, "git", "rev-parse", "HEAD").stdout.strip(), "gov413": subprocess.run([GOV413, "version"], capture_output=True, text=True).stdout, "gov412": subprocess.run([GOV412, "version"], capture_output=True, text=True).stdout if os.path.exists(GOV412) else None, "results": RESULTS}, open(os.path.join(OUT_DIR, "results.json" if not only else "results-partial.json"), "w"), indent=2, default=str)
    print("\nWORK:", WORK)
    print("SUMMARY:", {v: sum(1 for r in RESULTS if r["verdict"] == v) for v in ["PASS", "FAIL", "INFO", "ERROR"]})
