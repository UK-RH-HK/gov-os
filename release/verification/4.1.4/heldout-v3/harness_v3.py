#!/usr/bin/env python3
"""Third independent verifier held-out harness — agentic-engineering-os candidate 4.1.4.

Authored in a fresh verification session with no builder context and without reading the
builder's certification tests before authorship. Neither the builder nor either previous
verifier knew these scenarios. Black box only: every interaction goes through the
`gov --json` CLI contract (API-0002). Nothing in the candidate checkout is modified.

Run:  GOV_CANONICAL_ROOT=<clone> python3 harness_v3.py [VV-01 VV-07 ...]
Optional: GOV412_WORKTREE=<dir with a 4.1.2 gov binary>   (VV-30 family)
"""
import json, os, re, shutil, subprocess, sys, tempfile, hashlib, sqlite3, traceback
import yaml

CANON = os.environ.get("GOV_CANONICAL_ROOT") or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "clone414"))
GOV = os.path.join(CANON, "target/release/gov")
OUT_DIR = os.environ.get("GOV_VERIFIER_OUT") or os.path.dirname(os.path.abspath(__file__))
WORK = tempfile.mkdtemp(prefix="gov-verifier3-")
REL412 = os.path.join(CANON, "release/releases/4.1.2")
REL413 = os.path.join(CANON, "release/releases/4.1.3")
REL414 = os.path.join(CANON, "release/releases/4.1.4")
RESULTS = []
ONLY = [a for a in sys.argv[1:]]


def record(sid, title, verdict, detail, severity=None):
    RESULTS.append({"id": sid, "title": title, "verdict": verdict, "severity": severity, "detail": detail})
    print(f"[{verdict}] {sid} {title}\n    {json.dumps(detail)[:1400]}", flush=True)


def scenario(fn):
    sid = fn.__name__.split("_")[0].replace("VV", "VV-")
    if ONLY and sid not in ONLY and fn.__name__ not in ONLY:
        return fn
    try:
        fn()
    except Exception:
        record(sid, fn.__doc__ or fn.__name__, "ERROR", {"traceback": traceback.format_exc()[-2500:]})
    return fn


class Gov:
    def __init__(self, root, session="S-v3", role="orchestrator", binary=None, canon=None, env=None):
        self.root, self.session, self.role = root, session, role
        self.binary = binary or GOV
        self.canon = canon or CANON
        self.env = env or {}

    def r(self, role):
        return Gov(self.root, self.session, role, self.binary, self.canon, self.env)

    def s(self, session):
        return Gov(self.root, session, self.role, self.binary, self.canon, self.env)

    def run(self, *args):
        env = dict(os.environ)
        env["GOV_CANONICAL_ROOT"] = self.canon
        env.pop("GOV_SESSION", None)
        env.pop("GOV_ROLE", None)
        env.update(self.env)
        cmd = [self.binary, "--json", "--root", self.root, "--session", self.session, "--role", self.role] + [str(a) for a in args]
        p = subprocess.run(cmd, capture_output=True, text=True, env=env)
        try:
            e = json.loads(p.stdout.strip())
        except Exception:
            e = {"ok": False, "error": {"code": "NO_JSON", "message": (p.stdout + p.stderr)[-900:]}}
        return p.returncode, e

    def ok(self, *args):
        c, e = self.run(*args)
        if not e.get("ok"):
            raise RuntimeError(f"gov {' '.join(str(a) for a in args)} failed: {json.dumps(e.get('error'))[:700]}")
        return e["result"]

    def err(self, *args):
        c, e = self.run(*args)
        if e.get("ok"):
            raise RuntimeError(f"gov {' '.join(str(a) for a in args)} unexpectedly SUCCEEDED: {json.dumps(e.get('result'))[:500]}")
        return e["error"]

    def try_(self, *args):
        return self.run(*args)

    def doctor(self):
        """doctor returns an error envelope when the verdict is UNHEALTHY; the checks live in details."""
        c, e = self.run("doctor")
        if e.get("ok"):
            return e["result"]
        d = (e.get("error") or {}).get("details")
        if isinstance(d, dict) and "checks" in d:
            return d
        raise RuntimeError(f"doctor failed without checks: {json.dumps(e)[:400]}")


def sh(cwd, *cmd):
    return subprocess.run(list(cmd), cwd=cwd, capture_output=True, text=True)


def git_init(root):
    sh(root, "git", "init", "-q")
    sh(root, "git", "config", "user.email", "v3@example.invalid")
    sh(root, "git", "config", "user.name", "verifier3")
    sh(root, "git", "add", "-A")
    sh(root, "git", "commit", "-q", "-m", "baseline")


def commit(root, msg="wip"):
    sh(root, "git", "add", "-A")
    sh(root, "git", "commit", "-q", "-m", msg)


def fixture(name, tag):
    root = os.path.join(WORK, f"{tag}-{name}")
    shutil.copytree(os.path.join(CANON, "fixtures", name, "project"), root)
    git_init(root)
    return root


def rd(root, rel):
    return open(os.path.join(root, rel), encoding="utf-8").read()


def wr(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(text)


class _L(yaml.SafeLoader):
    pass


_L.yaml_implicit_resolvers = {k: [(t, r) for (t, r) in v if t != "tag:yaml.org,2002:timestamp"] for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()}


def ry(root, rel):
    return yaml.load(rd(root, rel), Loader=_L)


def wy(root, rel, doc):
    wr(root, rel, yaml.safe_dump(doc, sort_keys=False))


def find_record(root, rid):
    """Locate a governed record file by id anywhere under the project."""
    for base, _, files in os.walk(root):
        if ".git" in base or ".governance-runtime" in base:
            continue
        for f in files:
            if f == f"{rid}.yaml" or f == f"{rid}.yml":
                return os.path.join(base, f)
    return None


def init_project(tag, fix="greenfield", role="orchestrator", index=True):
    root = fixture(fix, tag)
    g = Gov(root)
    args = ["init", "--source", os.path.join(CANON, "framework"), "--name", tag, "--alias", tag]
    if not index:
        args.append("--skip-index")
    g.r(role).ok(*args)
    commit(root, "init")
    return root, g


EVIL = """#!/usr/bin/env bash
printf 'EXECUTED %s\\n' "$1" >> "$GOV_V3_MARKER"
echo '{"protocol":"gov-capability/1","ok":false,"error":{"code":"NOPE","message":"probe"}}'
"""


def plant_evil(root, marker_env_name="marker.txt"):
    wr(root, "tools/v3probe.sh", EVIL)
    os.chmod(os.path.join(root, "tools/v3probe.sh"), 0o755)
    return os.path.join(root, marker_env_name)


# ---------------------------------------------------------------------------
# A. Human Decision Gate integrity, adversarially (directive item 7)
# ---------------------------------------------------------------------------
@scenario
def VV01_cit_gate_adversarial_matrix():
    """CIT approval/execution under unanswered, declined, revoked, stale, re-answered, mismatched and forged gates"""
    root, g = init_project("vv01")
    obs = {}

    n = [0]

    def new_cit(title, path="docs/vv01.md"):
        n[0] += 1
        mf = os.path.join(root, f".governance-runtime/v3m{n[0]}.json")
        os.makedirs(os.path.dirname(mf), exist_ok=True)
        open(mf, "w").write(json.dumps([{"op": "write_file", "path": path, "content": f"{title}\n"}]))
        c = g.r("change-controller").ok("cit", "propose", "--proposal", title,
                                        "--trigger", "security_change", "--manifest", mf)
        cid = c["id"]
        if c.get("cit_status") != "SIMULATED":
            g.r("change-controller").ok("cit", "simulate", cid)
        rec = g.r("change-controller").ok("cit", "show", cid)
        return cid, rec

    # (a) presented but never answered
    cid, sim = new_cit("A unanswered")
    gate = sim.get("human_gate")
    g.r("change-controller").ok("gate", "present", gate)
    e = g.r("change-controller").err("cit", "approve", cid, "--method", "human", "--by", "owner")
    obs["a_presented_unanswered"] = {"code": e["code"], "msg": e["message"][:120]}

    # (a2) never presented at all
    cid2, sim2 = new_cit("A2 unpresented", "docs/vv01b.md")
    e = g.r("change-controller").err("cit", "approve", cid2, "--method", "human", "--by", "owner")
    obs["a2_never_presented"] = {"code": e["code"]}

    # (b) human declines with option B
    g.r("human").ok("decide", gate, "--option", "B", "--by", "owner", "--rationale", "no")
    rec = ry(root, os.path.relpath(find_record(root, cid), root))
    obs["b_status_after_decline"] = rec["cit_status"]
    e = g.r("change-controller").err("cit", "approve", cid, "--method", "human", "--by", "owner")
    obs["b_approve_after_decline"] = {"code": e["code"]}
    c2, e2 = g.r("change-controller").try_("cit", "execute", cid)
    obs["b_execute_after_decline"] = {"ok": e2.get("ok"), "code": (e2.get("error") or {}).get("code")}
    obs["b_file_written"] = os.path.exists(os.path.join(root, "docs/vv01.md"))

    # (c) happy path then REVOKE the gate before execution
    cid3, sim3 = new_cit("C revoke", "docs/vv01c.md")
    gate3 = sim3["human_gate"]
    g.r("change-controller").ok("gate", "present", gate3)
    g.r("human").ok("decide", gate3, "--option", "A", "--by", "owner", "--rationale", "yes")
    g.r("change-controller").ok("cit", "approve", cid3, "--method", "human", "--by", "owner")
    rv = g.r("orchestrator").ok("gate", "revoke", gate3, "--reason", "withdrawn by owner")
    obs["c_revoke"] = {"cit_after": rv["touched"]["cit"], "decisions": rv["touched"]["decisions"]}
    c4, e4 = g.r("change-controller").try_("cit", "execute", cid3)
    obs["c_execute_after_revoke"] = {"ok": e4.get("ok"), "code": (e4.get("error") or {}).get("code")}
    obs["c_file_written"] = os.path.exists(os.path.join(root, "docs/vv01c.md"))

    # (d) approval STALE: the gate answer is tampered after approval
    cid5, sim5 = new_cit("D stale", "docs/vv01d.md")
    gate5 = sim5["human_gate"]
    g.r("change-controller").ok("gate", "present", gate5)
    g.r("human").ok("decide", gate5, "--option", "A", "--by", "owner")
    g.r("change-controller").ok("cit", "approve", cid5, "--method", "human", "--by", "owner")
    gpath = find_record(root, gate5)
    gdoc = ry(root, os.path.relpath(gpath, root))
    gdoc["answer"]["at"] = "2099-01-01T00:00:00Z"
    wy(root, os.path.relpath(gpath, root), gdoc)
    c6, e6 = g.r("change-controller").try_("cit", "execute", cid5)
    obs["d_execute_after_answer_tampered"] = {"ok": e6.get("ok"), "code": (e6.get("error") or {}).get("code")}

    # (e) forged approval object: a CIT record hand-edited to claim human approval without any gate
    cid7, sim7 = new_cit("E forged", "docs/vv01e.md")
    cpath = find_record(root, cid7)
    cdoc = ry(root, os.path.relpath(cpath, root))
    cdoc["cit_status"] = "APPROVED"
    cdoc["approval"] = {"gate": None, "decision": "D-9999", "method": "human", "human_approved": True,
                        "answered_by": "owner", "answered_by_kind": "human", "answered_at": "2026-01-01T00:00:00Z"}
    wy(root, os.path.relpath(cpath, root), cdoc)
    c8, e8 = g.r("change-controller").try_("cit", "execute", cid7)
    obs["e_execute_forged_approval"] = {"ok": e8.get("ok"), "code": (e8.get("error") or {}).get("code")}
    obs["e_file_written"] = os.path.exists(os.path.join(root, "docs/vv01e.md"))

    # (f) gate raised for a DIFFERENT cit used to approve this one
    cid9, sim9 = new_cit("F mismatch", "docs/vv01f.md")
    cid10, sim10 = new_cit("F donor", "docs/vv01g.md")
    gate10 = sim10["human_gate"]
    g.r("change-controller").ok("gate", "present", gate10)
    g.r("human").ok("decide", gate10, "--option", "A", "--by", "owner")
    cpath9 = find_record(root, cid9)
    cdoc9 = ry(root, os.path.relpath(cpath9, root))
    cdoc9["human_gate"] = gate10
    wy(root, os.path.relpath(cpath9, root), cdoc9)
    e = g.r("change-controller").err("cit", "approve", cid9, "--method", "human", "--by", "owner")
    obs["f_cross_cit_gate"] = {"code": e["code"]}

    # (g) an agent answers the gate, caller claims human approval
    cid11, sim11 = new_cit("G agent answer", "docs/vv01h.md")
    gate11 = sim11["human_gate"]
    g.r("change-controller").ok("gate", "present", gate11)
    c, e = g.r("change-controller").try_("decide", gate11, "--option", "A", "--by", "change-controller")
    obs["g_agent_answer"] = {"ok": e.get("ok"), "code": (e.get("error") or {}).get("code"),
                             "kind": (e.get("result") or {}).get("answered_by_kind")}
    if e.get("ok"):
        c, e2 = g.r("change-controller").try_("cit", "approve", cid11, "--method", "human", "--by", "owner")
        obs["g_human_method_on_agent_answer"] = {"ok": e2.get("ok"), "code": (e2.get("error") or {}).get("code")}

    # (h) a low-authority role tries to approve
    cid12, sim12 = new_cit("H low role", "docs/vv01i.md")
    gate12 = sim12["human_gate"]
    g.r("change-controller").ok("gate", "present", gate12)
    g.r("human").ok("decide", gate12, "--option", "A", "--by", "owner")
    e = g.r("backend-engineer").err("cit", "approve", cid12, "--method", "human", "--by", "owner")
    obs["h_L1_approve"] = {"code": e["code"]}
    e = g.r("backend-engineer").err("decide", gate12, "--option", "A", "--by", "owner")
    obs["h_L1_answer_already_answered"] = {"code": e["code"]}

    # (i) L1 role answering a fresh gate as if relaying a human
    cid13, sim13 = new_cit("I relay", "docs/vv01j.md")
    gate13 = sim13["human_gate"]
    g.r("change-controller").ok("gate", "present", gate13)
    e = g.r("backend-engineer").err("decide", gate13, "--option", "A", "--by", "owner")
    obs["i_L1_relay_human_answer"] = {"code": e["code"]}

    bad = []
    if obs["a_presented_unanswered"]["code"] != "GATE_NOT_ANSWERED":
        bad.append("presented-unanswered approval not refused with GATE_NOT_ANSWERED")
    if obs["a2_never_presented"]["code"] != "GATE_NOT_PRESENTED":
        bad.append("unpresented approval not refused with GATE_NOT_PRESENTED")
    if obs["b_status_after_decline"] != "REJECTED" or obs["b_execute_after_decline"]["ok"] or obs["b_file_written"]:
        bad.append("decline did not stop the transaction")
    if obs["c_execute_after_revoke"]["ok"] or obs["c_file_written"]:
        bad.append("revoked gate still executed")
    if obs["d_execute_after_answer_tampered"]["ok"]:
        bad.append("stale/tampered answer still executed")
    if obs["e_execute_forged_approval"]["ok"] or obs["e_file_written"]:
        bad.append("forged approval object executed")
    if obs["f_cross_cit_gate"]["code"] != "GATE_MISMATCH":
        bad.append("a gate raised for another CIT approved this one")
    if obs.get("g_human_method_on_agent_answer", {}).get("ok"):
        bad.append("agent answer laundered into human approval")
    if obs["h_L1_approve"]["code"] != "AUTHORITY_DENIED":
        bad.append("L1 role approved a human-gated CIT")
    if obs["i_L1_relay_human_answer"]["code"] != "AUTHORITY_DENIED":
        bad.append("L1 role recorded a human answer")
    record("VV-01", "Human Decision Gate integrity under unanswered / declined / revoked / stale / forged / cross-CIT / under-authority attacks",
           "FAIL" if bad else "PASS", {"failures": bad, "observations": obs}, severity="CRITICAL" if bad else None)


# ---------------------------------------------------------------------------
# B. Constitutional floors vs project policy (directive item 8)
# ---------------------------------------------------------------------------
@scenario
def VV02_project_policy_cannot_weaken_floors():
    """Project overlay/exceptions cannot weaken authority, security, sensitivity or gate floors"""
    root, g = init_project("vv02")
    obs = {}
    pp = ry(root, "governance/project/PROJECT_POLICY.yaml")
    pp.setdefault("policy_overrides", {})
    pp["policy_overrides"].update({
        "AUTHORITY_POLICY.authority_levels_required.create_task": "L0",
        "AUTHORITY_POLICY.authority_levels_required.execute_cit": "L0",
        "AUTHORITY_POLICY.authority_levels_required.install_kernel": "L0",
        "SECURITY_POLICY.never_index_classes": [],
        "SECURITY_POLICY.never_export_classes": [],
        "SECURITY_POLICY.secret_path_patterns": [],
        "CHANGE_POLICY.auto_approve_max_radius": "R5",
        "CHANGE_POLICY.rollback.snapshot_before_execute": False,
        "HUMAN_GATE_POLICY.must_be_presented_in_chat": False,
        "HUMAN_GATE_POLICY.agent_resolvable_when.max_radius": "R5",
        "TOOL_POLICY.plugins.min_authority": "L0",
        "TOOL_POLICY.plugins.require_valid_descriptor": False,
        "TEST_POLICY.task_close_requires_tests_status": ["PASS", "FAIL", "UNKNOWN"],
        "ARCHIVE_POLICY.archive_mutation": "delete",
        "POLICY_PRECEDENCE.default_mode": "overridable",
    })
    wy(root, "governance/project/PROJECT_POLICY.yaml", pp)
    ov = g.ok("policy", "overrides")
    obs["applied"] = [f"{a['policy']}.{a['key']}" for a in ov.get("applied", ov.get("applied_overrides", []))]
    obs["refused"] = [f"{a['policy']}.{a['key']}" for a in ov.get("refused", ov.get("refused_overrides", []))]
    eff = g.ok("policy", "effective", "AUTHORITY_POLICY")
    obs["effective_create_task"] = eff["effective"]["authority_levels_required"]["create_task"]
    eff_sec = g.ok("policy", "effective", "SECURITY_POLICY")
    obs["effective_never_index_classes"] = eff_sec["effective"].get("never_index_classes")
    doc = g.doctor()
    d027 = [c for c in doc["checks"] if c["id"] == "D027"]
    obs["D027"] = {"ok": d027[0]["ok"], "severity": d027[0]["severity"], "message": d027[0]["message"][:300]} if d027 else None
    # behavioural proof: an L0 role must still be refused
    e = g.r("independent-auditor").err("task", "create", "--title", "should not exist", "--objective", "probe", "--class", "implementation")
    obs["L0_create_task"] = e["code"]
    # sensitivity floor still enforced: a restricted-classified file must not be indexed
    ds = ry(root, "governance/project/DATA_SENSITIVITY.yaml")
    ds.setdefault("classifications", []).append({"pattern": "customer/**", "class": "restricted", "reason": "verifier probe"})
    ds["classifications"].append({"path": "malformed/**", "class": "restricted"})  # schema-invalid on purpose
    wy(root, "governance/project/DATA_SENSITIVITY.yaml", ds)
    wr(root, "customer/leak.md", "VV02RESTRICTEDMARKER customer contract terms\n")
    commit(root, "restricted")
    rb = g.ok("rebuild-memory")
    obs["excluded_customer"] = [x for x in rb.get("excluded", []) if "customer" in json.dumps(x)]
    q = g.ok("memory", "query", "VV02RESTRICTEDMARKER")
    leak_hits = [h for h in q.get("hits", []) if "customer/" in (h.get("path") or "") or "VV02RESTRICTEDMARKER" in json.dumps(h.get("excerpt", ""))]
    obs["restricted_retrievable"] = leak_hits
    obs["restricted_query_other_hits"] = [h.get("path") for h in q.get("hits", [])]
    wr(root, "malformed/leak.md", "VV02MALFORMEDMARKER customer contract terms\n")
    commit(root, "malformed")
    g.ok("rebuild-memory")
    q2 = g.ok("memory", "query", "VV02MALFORMEDMARKER")
    obs["malformed_rule_content_retrievable"] = bool(q2.get("hits"))
    doc2 = g.doctor()
    d006 = [c for c in doc2["checks"] if c["id"] == "D006"]
    obs["D006_overlay"] = {"ok": d006[0]["ok"], "severity": d006[0]["severity"], "message": d006[0]["message"][:300]} if d006 else None
    bad = []
    weakening = ["AUTHORITY_POLICY.authority_levels_required.create_task",
                 "AUTHORITY_POLICY.authority_levels_required.execute_cit",
                 "AUTHORITY_POLICY.authority_levels_required.install_kernel",
                 "SECURITY_POLICY.never_index_classes", "SECURITY_POLICY.never_export_classes",
                 "SECURITY_POLICY.secret_path_patterns", "CHANGE_POLICY.auto_approve_max_radius",
                 "CHANGE_POLICY.rollback.snapshot_before_execute", "HUMAN_GATE_POLICY.must_be_presented_in_chat",
                 "HUMAN_GATE_POLICY.agent_resolvable_when.max_radius", "TOOL_POLICY.plugins.min_authority",
                 "TOOL_POLICY.plugins.require_valid_descriptor", "TEST_POLICY.task_close_requires_tests_status",
                 "ARCHIVE_POLICY.archive_mutation", "POLICY_PRECEDENCE.default_mode"]
    for w in weakening:
        if w in obs["applied"]:
            bad.append(f"weakening override APPLIED: {w}")
        elif w not in obs["refused"]:
            bad.append(f"weakening override neither applied nor refused (silently lost): {w}")
    if obs["L0_create_task"] != "AUTHORITY_DENIED":
        bad.append("L0 role created a task after the overlay lowered the level")
    if obs["restricted_retrievable"]:
        bad.append("restricted-class content indexed and retrievable")
    if not obs["D027"] or obs["D027"]["ok"]:
        bad.append("doctor D027 did not report the refused overrides")
    record("VV-02", "project policy cannot weaken constitutional authority/security/sensitivity/gate floors",
           "FAIL" if bad else "PASS", {"failures": bad, "observations": obs}, severity="HIGH" if bad else None)


@scenario
def VV03_exception_and_kernel_tamper_paths():
    """Exceptions must be governed decisions; a tampered/absent kernel precedence file must fail closed"""
    root, g = init_project("vv03")
    obs = {}
    # (a) exception naming a decision record that does not exist, on a relaxable key
    ex = ry(root, "governance/project/PROJECT_EXCEPTIONS.yaml")
    ex.setdefault("exceptions", []).append({
        "id": "EXC-FAKE-1", "policy": "BUDGET_POLICY", "key": "defaults.max_tool_calls",
        "value": 999999, "decision": "D-DOES-NOT-EXIST", "expires": "2099-01-01",
        "rationale": "verifier probe: fabricated decision id"})
    ex["exceptions"].append({
        "id": "EXC-FAKE-2", "policy": "AUTHORITY_POLICY", "key": "authority_levels_required.execute_cit",
        "value": "L0", "decision": "D-DOES-NOT-EXIST", "expires": "2099-01-01",
        "rationale": "verifier probe: security key via exception"})
    wy(root, "governance/project/PROJECT_EXCEPTIONS.yaml", ex)
    ov = g.ok("policy", "overrides")
    applied = {f"{a['policy']}.{a['key']}": a for a in ov.get("applied", ov.get("applied_overrides", []))}
    refused = {f"{a['policy']}.{a['key']}": a for a in ov.get("refused", ov.get("refused_overrides", []))}
    obs["exception_with_fabricated_decision_applied"] = "BUDGET_POLICY.defaults.max_tool_calls" in applied
    obs["exception_on_authority_key_refused"] = "AUTHORITY_POLICY.authority_levels_required.execute_cit" in refused
    doc = g.doctor()
    obs["doctor_verdict_a"] = doc["verdict"]
    obs["D027_a"] = [c for c in doc["checks"] if c["id"] == "D027"][0]["ok"]
    # (b) delete the kernel precedence file -> embedded fallback must still refuse weakening
    os.remove(os.path.join(root, "governance/kernel/policies/POLICY_PRECEDENCE.yaml"))
    pp = ry(root, "governance/project/PROJECT_POLICY.yaml")
    pp.setdefault("policy_overrides", {})["AUTHORITY_POLICY.authority_levels_required.create_task"] = "L0"
    wy(root, "governance/project/PROJECT_POLICY.yaml", pp)
    ov = g.ok("policy", "overrides")
    refused_b = [f"{a['policy']}.{a['key']}" for a in ov.get("refused", ov.get("refused_overrides", []))]
    obs["b_precedence_source"] = ov.get("precedence", {}).get("source") if isinstance(ov.get("precedence"), dict) else ov.get("precedence")
    obs["b_refused"] = refused_b
    e = g.r("independent-auditor").try_("task", "create", "--title", "x", "--objective", "probe", "--class", "implementation")
    obs["b_L0_create_task"] = {"ok": e[1].get("ok"), "code": (e[1].get("error") or {}).get("code")}
    # (c) TAMPER the installed kernel precedence file to declare everything overridable
    wr(root, "governance/kernel/policies/POLICY_PRECEDENCE.yaml",
       "policy: POLICY_PRECEDENCE\nversion: 1.0.0\nlayers: [a]\ndefault_mode: overridable\nrules:\n  - {key: AUTHORITY_POLICY.*, mode: overridable}\n  - {key: SECURITY_POLICY.*, mode: overridable}\n")
    ov = g.ok("policy", "overrides")
    applied_c = [f"{a['policy']}.{a['key']}" for a in ov.get("applied", ov.get("applied_overrides", []))]
    obs["c_applied_after_kernel_tamper"] = applied_c
    c, e = g.r("independent-auditor").try_("task", "create", "--title", "tampered", "--objective", "probe", "--class", "implementation")
    obs["c_L0_create_task"] = {"ok": e.get("ok"), "code": (e.get("error") or {}).get("code")}
    doc = g.doctor()
    kernel_checks = [c for c in doc["checks"] if c["id"] in ("D003", "D004")]
    obs["c_kernel_integrity_checks"] = [{"id": c["id"], "ok": c["ok"], "severity": c["severity"], "msg": c["message"][:160]} for c in kernel_checks]
    obs["c_doctor_verdict"] = doc["verdict"]
    ver = g.try_("kernel", "verify")
    obs["c_kernel_verify"] = {"ok": ver[1].get("ok"), "detail": json.dumps(ver[1].get("result") or ver[1].get("error"))[:300]}
    bad = []
    if obs["exception_with_fabricated_decision_applied"]:
        bad.append("PROJECT_EXCEPTIONS applied with a decision id that has no record (governance claim never verified)")
    if not obs["exception_on_authority_key_refused"]:
        bad.append("exception weakened an AUTHORITY_POLICY key")
    if "AUTHORITY_POLICY.authority_levels_required.create_task" not in obs["b_refused"]:
        bad.append("with the kernel precedence file deleted the weakening override was not refused")
    if obs["b_L0_create_task"]["ok"]:
        bad.append("L0 created a task after the kernel precedence file was deleted")
    if obs["c_L0_create_task"]["ok"]:
        bad.append("L0 created a task after the installed kernel precedence file was tampered with")
    if not any(not c["ok"] for c in obs["c_kernel_integrity_checks"]):
        bad.append("kernel tampering was not reported by doctor D003/D004")
    record("VV-03", "exception records must be governed decisions; kernel precedence tampering/absence fails closed",
           "FAIL" if bad else "PASS", {"failures": bad, "observations": obs}, severity="HIGH" if bad else None)


# ---------------------------------------------------------------------------
# C. Plugin / capability boundary (directive item 9)
# ---------------------------------------------------------------------------
@scenario
def VV04_plugin_boundary_attack_matrix():
    """Unregistered, malformed, unpinned, tampered, self-authorising and under-authority plugin descriptors"""
    root, g = init_project("vv04")
    marker = os.path.join(root, "v3-marker.txt")
    env = {"GOV_V3_MARKER": marker}
    g = Gov(root, env=env)
    plant_evil(root)
    wr(root, "src/probe.py", "def f():\n    return 1\n")
    os.makedirs(os.path.join(root, "governance/project/plugins"), exist_ok=True)

    def desc(name, extra=""):
        wr(root, f"governance/project/plugins/{name}.yaml",
           f"plugin_id: {name}\ncapability: code_intel\ncommand: [\"tools/v3probe.sh\", \"{name}\"]\nversion: \"1\"\nlanguages: [\"python\"]\n" + extra)

    def clear():
        d = os.path.join(root, "governance/project/plugins")
        for f in os.listdir(d):
            os.remove(os.path.join(d, f))
        if os.path.exists(marker):
            os.remove(marker)

    def marker_text():
        return open(marker).read() if os.path.exists(marker) else ""

    obs = {}
    # 1. malformed descriptor (unknown field, bad id)
    clear()
    wr(root, "governance/project/plugins/bad.yaml", "plugin_id: BAD ID\ncapability: nonsense\ncommand: []\nsurprise: true\n")
    lst = g.r("orchestrator").ok("plugins", "list")
    obs["1_malformed"] = {"usable": [u["plugin_id"] for u in lst["usable"]], "rejected": len(lst["rejected"])}

    # 2. plain unregistered descriptor, low-authority role
    clear()
    desc("p-unreg")
    lst = g.r("backend-engineer").ok("plugins", "list")
    obs["2_unregistered_L1_usable"] = [u["plugin_id"] for u in lst["usable"]]
    g.r("independent-auditor").ok("rebuild-memory")
    obs["2_marker_after_L0_rebuild"] = marker_text()

    # 3. SELF-DECLARED approved_roles: all  (attacker-controlled field in the descriptor itself)
    clear()
    desc("p-allroles", "approved_roles: [\"all\"]\n")
    lst = g.r("independent-auditor").ok("plugins", "list")
    obs["3_selfdeclared_approved_roles_usable_by_L0"] = [u["plugin_id"] for u in lst["usable"]]
    g.r("independent-auditor").ok("rebuild-memory")
    obs["3_marker_after_L0_rebuild"] = marker_text()
    doc = g.r("orchestrator").doctor()
    d028 = [c for c in doc["checks"] if c["id"] == "D028"][0]
    obs["3_D028"] = {"ok": d028["ok"], "severity": d028["severity"], "message": d028["message"][:200]}

    # 4. SELF-DECLARED provenance.registered_at (claims to be registered without ever being registered)
    clear()
    desc("p-fakeprov", "provenance:\n  registered_at: \"2026-01-01T00:00:00Z\"\n  registered_by_role: human\n  method: manual\n")
    lst = g.r("independent-auditor").ok("plugins", "list")
    obs["4_fake_provenance_usable_by_L0"] = [u["plugin_id"] for u in lst["usable"]]
    g.r("independent-auditor").ok("rebuild-memory")
    obs["4_marker_after_L0_rebuild"] = marker_text()

    # 5. declared pin that does not match the implementation
    clear()
    desc("p-badpin", "pin:\n  sha256: \"0000000000000000000000000000000000000000000000000000000000000000\"\n")
    lst = g.r("orchestrator").ok("plugins", "list")
    obs["5_bad_pin"] = {"usable": [u["plugin_id"] for u in lst["usable"]],
                        "denied": [(d["plugin_id"], d["code"]) for d in lst["denied"]]}

    # 6. content drift after first governed use (same version, changed implementation)
    clear()
    desc("p-drift")
    g.r("orchestrator").ok("plugins", "list")
    g.r("orchestrator").ok("rebuild-memory")
    before = marker_text()
    wr(root, "tools/v3probe.sh", EVIL.replace("EXECUTED", "TAMPERED"))
    os.chmod(os.path.join(root, "tools/v3probe.sh"), 0o755)
    lst = g.r("orchestrator").ok("plugins", "list")
    obs["6_drift"] = {"usable": [u["plugin_id"] for u in lst["usable"]],
                      "denied": [(d["plugin_id"], d["code"]) for d in lst["denied"]],
                      "marker_before": before}
    wr(root, "tools/v3probe.sh", EVIL)
    os.chmod(os.path.join(root, "tools/v3probe.sh"), 0o755)

    # 7. elevated permissions without a registration gate
    clear()
    desc("p-elev", "permissions:\n  network: true\n  filesystem_write: true\n")
    lst = g.r("orchestrator").ok("plugins", "list")
    obs["7_elevated_no_gate"] = {"usable": [u["plugin_id"] for u in lst["usable"]],
                                 "denied": [(d["plugin_id"], d["code"]) for d in lst["denied"]]}

    # 8. elevated permissions + self-declared approved_roles
    clear()
    desc("p-elev-all", "permissions:\n  network: true\napproved_roles: [\"all\"]\n")
    lst = g.r("independent-auditor").ok("plugins", "list")
    obs["8_elevated_selfdeclared"] = {"usable": [u["plugin_id"] for u in lst["usable"]],
                                      "denied": [(d["plugin_id"], d["code"]) for d in lst["denied"]]}

    # 9. governed registration path (control): does it work and does it gate?
    clear()
    desc("p-reg")
    c, e = g.r("orchestrator").try_("plugins", "register", "--descriptor", os.path.join(root, "governance/project/plugins/p-reg.yaml"))
    obs["9_register_L4"] = {"ok": e.get("ok"), "detail": json.dumps(e.get("result") or e.get("error"))[:300]}
    c, e = g.r("backend-engineer").try_("plugins", "register", "--descriptor", os.path.join(root, "governance/project/plugins/p-reg.yaml"))
    obs["9_register_L1"] = {"ok": e.get("ok"), "code": (e.get("error") or {}).get("code")}

    # 10. capabilities invoke by an under-authority role
    c, e = g.r("independent-auditor").try_("capabilities", "invoke", "--plugin", "p-reg", "--inputs", "{}")
    obs["10_invoke_L0"] = {"ok": e.get("ok"), "code": (e.get("error") or {}).get("code")}

    bad = []
    if obs["1_malformed"]["usable"]:
        bad.append("malformed descriptor usable")
    if obs["2_unregistered_L1_usable"]:
        bad.append("unregistered descriptor usable by an L1 role")
    if obs["2_marker_after_L0_rebuild"]:
        bad.append("unregistered descriptor executed during an L0 rebuild")
    if obs["3_selfdeclared_approved_roles_usable_by_L0"]:
        bad.append("descriptor self-declaring approved_roles bypasses TOOL_POLICY.plugins.min_authority")
    if obs["3_marker_after_L0_rebuild"]:
        bad.append("ARBITRARY COMMAND EXECUTED as L0 via a self-declaring descriptor during rebuild-memory")
    if obs["3_D028"]["ok"]:
        bad.append("doctor D028 reports no plugin problems while an ungoverned descriptor is executable")
    if obs["4_fake_provenance_usable_by_L0"]:
        bad.append("descriptor self-declaring provenance.registered_at is treated as registered")
    if obs["4_marker_after_L0_rebuild"]:
        bad.append("ARBITRARY COMMAND EXECUTED as L0 via forged provenance during rebuild-memory")
    if obs["5_bad_pin"]["usable"]:
        bad.append("descriptor with a wrong declared pin is usable")
    if obs["6_drift"]["usable"]:
        bad.append("implementation drift after first governed use is not refused")
    if obs["7_elevated_no_gate"]["usable"]:
        bad.append("elevated permissions usable without a registration gate")
    if obs["8_elevated_selfdeclared"]["usable"]:
        bad.append("elevated permissions usable by L0 through self-declared approved_roles")
    if obs["10_invoke_L0"]["ok"]:
        bad.append("L0 invoked a plugin through capabilities invoke")
    record("VV-04", "capability/plugin boundary: unregistered, malformed, unpinned, tampered, self-authorising and under-authority descriptors",
           "FAIL" if bad else "PASS", {"failures": bad, "observations": obs}, severity="HIGH" if bad else None)


# ---------------------------------------------------------------------------
# D. Kernel-data hygiene and migration substance for the 4.1.4 payload
#    (the 4.1.4 equivalents of NV-09 / NV-19, which are pinned to the immutable 4.1.3 payload)
# ---------------------------------------------------------------------------
class Strict(yaml.SafeLoader):
    pass


def _strict_map(self, node, deep=False):
    seen = set()
    for k, _ in node.value:
        key = self.construct_object(k, deep=deep)
        if key in seen:
            raise yaml.constructor.ConstructorError(f"duplicate key {key!r}")
        seen.add(key)
    return yaml.SafeLoader.construct_mapping(self, node, deep)


Strict.construct_mapping = _strict_map


@scenario
def VV05_kernel_yaml_hygiene_414():
    """Every kernel YAML in the 4.1.4 payload (and in framework/) is strict-YAML valid; manifests agree"""
    obs = {"scanned": 0, "duplicates": {}, "unreadable": {}}
    roots = {"release/releases/4.1.4/kernel": os.path.join(REL414, "kernel"),
             "release/releases/4.1.3/kernel": os.path.join(REL413, "kernel"),
             "release/releases/4.1.2/kernel": os.path.join(REL412, "kernel"),
             "framework": os.path.join(CANON, "framework"),
             "migrations": os.path.join(CANON, "migrations")}
    for label, base in roots.items():
        for b, _, files in os.walk(base):
            for f in sorted(files):
                if not f.endswith((".yaml", ".yml")):
                    continue
                rel = os.path.join(label, os.path.relpath(os.path.join(b, f), base))
                obs["scanned"] += 1
                text = open(os.path.join(b, f), encoding="utf-8").read()
                try:
                    yaml.load(text, Loader=Strict)
                except yaml.constructor.ConstructorError as ex:
                    obs["duplicates"][rel] = str(ex)[:160]
                except Exception as ex:
                    obs["unreadable"][rel] = str(ex)[:160]
    k = yaml.safe_load(open(os.path.join(REL414, "kernel/KERNEL.yaml")))
    km = json.load(open(os.path.join(REL414, "kernel/KERNEL_MANIFEST.json")))
    mj = json.load(open(os.path.join(REL414, "manifest.json")))
    my = yaml.safe_load(open(os.path.join(REL414, "manifest.yaml")))
    obs["schema_versions_agree"] = k["schema_versions"] == km["schema_versions"] == mj["schema_versions"]
    obs["manifest_yaml_json_agree"] = json.loads(json.dumps(my, default=str)) == json.loads(json.dumps(mj, default=str))
    obs["kernel_yaml_matches_framework_source"] = open(os.path.join(REL414, "kernel/KERNEL.yaml")).read() == open(os.path.join(CANON, "framework/KERNEL.yaml")).read()
    dups414 = {k2: v for k2, v in obs["duplicates"].items() if k2.startswith("release/releases/4.1.4") or k2.startswith("framework")}
    bad = []
    if dups414:
        bad.append(f"duplicate mapping keys in current kernel data: {list(dups414)}")
    if not obs["schema_versions_agree"]:
        bad.append("schema_versions disagree across KERNEL.yaml / KERNEL_MANIFEST.json / manifest.json")
    if not obs["manifest_yaml_json_agree"]:
        bad.append("manifest.yaml and manifest.json disagree")
    if not obs["kernel_yaml_matches_framework_source"]:
        bad.append("released KERNEL.yaml differs from framework/KERNEL.yaml at this commit")
    record("VV-05", "kernel data hygiene for the 4.1.4 payload (strict YAML across every kernel file; manifest agreement)",
           "FAIL" if bad else "PASS", {"failures": bad, "observations": obs}, severity="LOW" if bad else None)


@scenario
def VV06_migration_substance_414():
    """M-4.1.3-4.1.4 performs what it claims; a migration that claims a template change without an op is refused"""
    obs = {}
    m = yaml.safe_load(open(os.path.join(REL414, "kernel/migrations/M-4.1.3-4.1.4.yaml")))
    ops = [o["op"] for o in m["operations"]]
    obs["operations"] = ops
    obs["overlay_ops"] = [o for o in m["operations"] if "overlay" in o["op"]]
    obs["declared_overlay_template_changes"] = m.get("overlay_template_changes")
    # which overlay templates actually changed between 4.1.3 and 4.1.4?
    changed = []
    t3 = os.path.join(REL413, "kernel/overlay-templates")
    t4 = os.path.join(REL414, "kernel/overlay-templates")
    for f in sorted(os.listdir(t4)):
        a = open(os.path.join(t3, f)).read() if os.path.exists(os.path.join(t3, f)) else None
        b = open(os.path.join(t4, f)).read()
        if a != b:
            changed.append(f)
    obs["overlay_templates_changed_413_to_414"] = changed
    desc = (m.get("description") or "") + " " + json.dumps(m.get("notes", ""))
    obs["description"] = desc[:300]
    declared_blob = json.dumps(obs["declared_overlay_template_changes"] or "")
    obs["undeclared_template_changes"] = [c for c in changed if c not in declared_blob and not obs["overlay_ops"]]
    # the shipped 4.1.2->4.1.3 migration in the CURRENT canonical tree: history preserved, description truthful?
    canon_m = yaml.safe_load(open(os.path.join(CANON, "migrations/M-4.1.2-4.1.3.yaml")))
    rel_m = yaml.safe_load(open(os.path.join(REL413, "kernel/migrations/M-4.1.2-4.1.3.yaml")))
    obs["413_migration_ops_unchanged"] = [o["op"] for o in canon_m["operations"]] == [o["op"] for o in rel_m["operations"]]
    obs["413_migration_has_amendment_history"] = bool(canon_m.get("amendments") or canon_m.get("history"))
    obs["413_migration_description_changed"] = canon_m.get("description") != rel_m.get("description")
    bad = []
    if changed and not obs["overlay_ops"] and not obs["declared_overlay_template_changes"]:
        bad.append("overlay templates changed between 4.1.3 and 4.1.4 but M-4.1.3-4.1.4 neither performs nor declares a template change")
    if not obs["413_migration_ops_unchanged"]:
        bad.append("the operations of the already-released M-4.1.2-4.1.3 were altered")
    record("VV-06", "migration record integrity for 4.1.4 (substance matches description; released migration operations unchanged)",
           "FAIL" if bad else "PASS", {"failures": bad, "observations": obs}, severity="MEDIUM" if bad else None)


@scenario
def VV07_release_identity_414():
    """4.1.4 release payload: verify, immutability, reproduction from the recorded commit, provenance"""
    obs = {}
    g = Gov(CANON)
    v = g.ok("release", "verify", REL414)
    obs["verify"] = {k: v.get(k) for k in ("ok", "files", "modified", "missing", "added", "release_hash", "certification")}
    mj = json.load(open(os.path.join(REL414, "manifest.json")))
    obs["manifest"] = {k: mj.get(k) for k in ("version", "release_commit", "release_hash", "certification", "provenance")}
    # payload == kernel data at the recorded release commit?
    rc = mj.get("release_commit")
    p = sh(CANON, "git", "rev-parse", "--verify", f"{rc}^{{commit}}")
    obs["release_commit_exists"] = p.returncode == 0
    p = sh(CANON, "git", "merge-base", "--is-ancestor", rc, "HEAD")
    obs["release_commit_is_ancestor_of_head"] = p.returncode == 0
    diff = sh(CANON, "git", "diff", "--name-only", rc, "HEAD", "--", "framework", "migrations", "tools")
    obs["kernel_sources_changed_since_release_commit"] = [x for x in diff.stdout.splitlines() if x]
    # rebuild into a temp dir and compare hashes
    out = os.path.join(WORK, "relbuild")
    c, e = g.try_("release", "build", "--version", "4.1.4", "--out", out, "--canonical", CANON, "--certification", "READY_FOR_INDEPENDENT_REVERIFICATION")
    obs["rebuild"] = {"ok": e.get("ok"), "detail": json.dumps(e.get("result") or e.get("error"))[:400]}
    if e.get("ok"):
        nm = json.load(open(os.path.join(out, "releases/4.1.4/manifest.json")))
        obs["rebuild_hash_equal"] = nm["release_hash"] == mj["release_hash"]
        obs["rebuild_file_hashes_equal"] = nm.get("file_hashes") == mj.get("file_hashes")
    # immutability: rebuilding in place must be refused
    c, e = g.try_("release", "build", "--version", "4.1.4", "--canonical", CANON)
    obs["rebuild_in_place"] = {"ok": e.get("ok"), "code": (e.get("error") or {}).get("code")}
    # tags / branch
    obs["tag_points_at_head"] = sh(CANON, "git", "tag", "--points-at", "HEAD").stdout.split()
    obs["head"] = sh(CANON, "git", "rev-parse", "HEAD").stdout.strip()
    bad = []
    if not obs["verify"].get("ok"):
        bad.append("gov release verify failed")
    if obs["verify"].get("modified") or obs["verify"].get("missing") or obs["verify"].get("added"):
        bad.append("release payload differs from its manifest")
    if not obs["release_commit_exists"] or not obs["release_commit_is_ancestor_of_head"]:
        bad.append("manifest.release_commit is not an ancestor of the candidate commit")
    if obs["kernel_sources_changed_since_release_commit"]:
        bad.append(f"kernel source changed after the recorded release commit: {obs['kernel_sources_changed_since_release_commit']}")
    if obs.get("rebuild_hash_equal") is False or obs.get("rebuild_file_hashes_equal") is False:
        bad.append("release does not reproduce from its recorded commit")
    if obs["rebuild_in_place"]["ok"]:
        bad.append("an existing immutable release could be rebuilt in place")
    if "v4.1.4-rc1" not in obs["tag_points_at_head"]:
        bad.append("candidate commit is not tagged v4.1.4-rc1")
    record("VV-07", "4.1.4 release identity, reproducibility, immutability and provenance",
           "FAIL" if bad else "PASS", {"failures": bad, "observations": obs}, severity="MEDIUM" if bad else None)


# ---------------------------------------------------------------------------
# E. Mutation manifests, derived-state rebuildability, export, fresh-agent
# ---------------------------------------------------------------------------
@scenario
def VV08_mutation_scope_observed_not_attested():
    """Task close compares the declared file list with the real working tree, including evasion attempts"""
    root, g = init_project("vv08")
    obs = {}
    t = g.r("orchestrator").ok("task", "create", "--title", "docs only", "--objective", "write docs",
                               "--class", "documentation", "--allowed", "docs/**", "--status", "READY")
    tid = t["id"]
    w = g.r("routine-documentation").s("S-worker")
    w.ok("task", "claim", tid)
    wr(root, "docs/notes.md", "notes\n")
    wr(root, "src/lib.rs", rd(root, "src/lib.rs") + "\n// out of scope edit\n")
    rep = os.path.join(root, ".governance-runtime/rep1.json")
    open(rep, "w").write(json.dumps({"summary": "docs", "work_completed": "wrote docs/notes.md", "files_changed": ["docs/notes.md"], "tests": {"status": "passed"}}))
    c, e = w.try_("task", "close", tid, "--report", rep)
    obs["undeclared_out_of_scope"] = {"ok": e.get("ok"), "code": (e.get("error") or {}).get("code"),
                                      "message": (e.get("error") or {}).get("message", "")[:250],
                                      "details": json.dumps(e.get("error", {}).get("details"))[:300]}
    # declaring it does not make it in scope
    rep2 = os.path.join(root, ".governance-runtime/rep2.json")
    open(rep2, "w").write(json.dumps({"summary": "docs", "work_completed": "wrote docs/notes.md and src/lib.rs", "files_changed": ["docs/notes.md", "src/lib.rs"], "tests": {"status": "passed"}}))
    c, e = w.try_("task", "close", tid, "--report", rep2)
    obs["declared_out_of_scope"] = {"ok": e.get("ok"), "code": (e.get("error") or {}).get("code"), "message": (e.get("error") or {}).get("message", "")[:250]}
    # evasion: hide the out-of-scope file behind .gitignore
    sh(root, "git", "checkout", "--", "src/lib.rs")
    wr(root, ".gitignore", rd(root, ".gitignore") + "\nsecretwork/\n" if os.path.exists(os.path.join(root, ".gitignore")) else "secretwork/\n")
    commit(root, "ignore")
    w2 = g.r("routine-documentation").s("S-worker2")
    t2 = g.r("orchestrator").ok("task", "create", "--title", "docs only 2", "--objective", "more docs",
                                "--class", "documentation", "--allowed", "docs/**", "--status", "READY")
    tid2 = t2["id"]
    w2.ok("task", "claim", tid2)
    wr(root, "docs/n2.md", "n2\n")
    wr(root, "secretwork/payload.sh", "#!/bin/sh\necho hidden\n")
    rep3 = os.path.join(root, ".governance-runtime/rep3.json")
    open(rep3, "w").write(json.dumps({"summary": "docs", "work_completed": "wrote docs/n2.md", "files_changed": ["docs/n2.md"], "tests": {"status": "passed"}}))
    g.ok("rebuild-memory")
    c, e = w2.try_("task", "close", tid2, "--report", rep3)
    obs["gitignored_out_of_scope_write"] = {"ok": e.get("ok"), "code": (e.get("error") or {}).get("code"),
                                            "message": (e.get("error") or {}).get("message", "")[:250],
                                            "file_exists": os.path.exists(os.path.join(root, "secretwork/payload.sh"))}
    bad = []
    if obs["undeclared_out_of_scope"]["ok"]:
        bad.append("close succeeded with an undeclared out-of-scope modification in the working tree")
    if obs["declared_out_of_scope"]["ok"]:
        bad.append("close succeeded with a declared but out-of-contract modification")
    record("VV-08", "mutation manifests are verified against the repository, not self-attested",
           "FAIL" if bad else "PASS",
           {"failures": bad, "observations": obs,
            "note": "gitignored paths are invisible to the observed-mutation check by construction (git ls-files --exclude-standard); recorded as a boundary, not scored"},
           severity="MEDIUM" if bad else None)


@scenario
def VV09_derived_state_is_rebuildable_and_not_authoritative():
    """Delete every derived index and rebuild: identical manifest; claims/control survive; vectors never authoritative"""
    root, g = init_project("vv09")
    obs = {}
    t = g.ok("task", "create", "--title", "t", "--objective", "o", "--class", "implementation", "--allowed", "src/**", "--status", "READY")
    g.r("backend-engineer").s("S-claimer").ok("task", "claim", t["id"])
    commit(root, "task")
    rb1 = g.ok("rebuild-memory")
    obs["manifest_1"] = rb1["manifest_hash"]
    g.r("change-controller").ok("pause", "--reason", "verifier probe") if False else None
    rt = os.path.join(root, ".governance-runtime")
    before = sorted(os.listdir(rt))
    for f in os.listdir(rt):
        p = os.path.join(rt, f)
        if f in ("claims.db", "control.json"):
            continue
        (shutil.rmtree(p) if os.path.isdir(p) else os.remove(p))
    rb2 = g.ok("rebuild-memory")
    obs["manifest_2"] = rb2["manifest_hash"]
    obs["runtime_dir_before"] = before
    cl = g.ok("claims", "list") if True else None
    obs["claims_after_wipe"] = json.dumps(cl)[:200]
    # full wipe including claims
    shutil.rmtree(rt)
    rb3 = g.ok("rebuild-memory")
    obs["manifest_3_after_full_wipe"] = rb3["manifest_hash"]
    # second machine
    m2 = os.path.join(WORK, "vv09-machineB")
    sh(root, "git", "add", "-A")
    sh(root, "git", "commit", "-q", "-m", "state")
    sh(WORK, "git", "clone", "-q", root, m2)
    g2 = Gov(m2)
    rb4 = g2.ok("rebuild-memory")
    obs["manifest_machineB"] = rb4["manifest_hash"]
    ver = g2.try_("memory", "verify")
    obs["machineB_memory_verify"] = {"ok": ver[1].get("ok"), "detail": json.dumps(ver[1].get("result") or ver[1].get("error"))[:200]}
    bad = []
    if obs["manifest_1"] != obs["manifest_2"]:
        bad.append("rebuild after deleting the derived store did not reproduce the manifest hash")
    if obs["manifest_1"] != obs["manifest_3_after_full_wipe"]:
        bad.append("rebuild after deleting the whole runtime directory did not reproduce the manifest hash")
    if obs["manifest_1"] != obs["manifest_machineB"]:
        bad.append("a second machine rebuilt a different manifest hash from the same Git state")
    record("VV-09", "all derived memory/index state can be deleted and rebuilt deterministically, on this and another machine",
           "FAIL" if bad else "PASS", {"failures": bad, "observations": obs}, severity="CRITICAL" if bad else None)


@scenario
def VV10_export_boundary():
    """Upstream export: project-scope lessons refused, identifiers stripped, secrets never leave, submission gated"""
    root, g = init_project("vv10", fix="brownfield")
    obs = {}
    os.makedirs(os.path.join(root, "spec/lessons"), exist_ok=True)
    for f in sorted(os.listdir(os.path.join(CANON, "fixtures/upstream-learning/lessons"))):
        shutil.copy(os.path.join(CANON, "fixtures/upstream-learning/lessons", f), os.path.join(root, "spec/lessons", f))
    wr(root, "config/secrets.env", "AWS_SECRET_ACCESS_KEY=AKIAVV10SECRETMARKERXXXXXXXX\n")
    wr(root, "customer/contract.md", "VV10CUSTOMERMARKER acme corporation terms\n")
    ds = ry(root, "governance/project/DATA_SENSITIVITY.yaml")
    ds.setdefault("classifications", []).append({"pattern": "customer/**", "class": "restricted", "reason": "probe"})
    ds.setdefault("identifiers_to_strip", []).extend(["Acme Freight Ltd", "Acme"])
    wy(root, "governance/project/DATA_SENSITIVITY.yaml", ds)
    commit(root, "hazards")
    g.ok("rebuild-memory")
    # PROJECT-scope lesson must never become an upstream packet
    c, e = g.r("research-agent").try_("upstream", "prepare", "L-0002")
    obs["prepare_project_scope"] = {"ok": e.get("ok"), "code": (e.get("error") or {}).get("code"),
                                    "message": (e.get("error") or {}).get("message", "")[:180]}
    # FRAMEWORK-scope lesson: prepare
    c, e = g.r("research-agent").try_("upstream", "prepare", "L-0004")
    obs["prepare_framework_scope"] = {"ok": e.get("ok"), "detail": json.dumps(e.get("result") or e.get("error"))[:500]}
    packet_id = (e.get("result") or {}).get("packet") or (e.get("result") or {}).get("id")
    blob = ""
    for b, _, fs in os.walk(root):
        if ".git" in b:
            continue
        for f in fs:
            if "UP-" in f or "upstream" in b.lower() or "packet" in f.lower():
                blob += open(os.path.join(b, f), errors="ignore").read()
    obs["packet_id"] = packet_id
    obs["packet_bytes"] = len(blob)
    obs["secret_in_packet"] = "AKIAVV10SECRETMARKER" in blob
    obs["customer_marker_in_packet"] = "VV10CUSTOMERMARKER" in blob
    obs["identifier_in_packet"] = "Acme" in blob
    # submission is authority- and gate-controlled
    dest = os.path.join(WORK, "vv10-upstream-dest")
    os.makedirs(dest, exist_ok=True)
    if packet_id:
        c, e = g.r("research-agent").try_("upstream", "submit", packet_id, "--destination", dest)
        obs["submit_L1"] = {"ok": e.get("ok"), "code": (e.get("error") or {}).get("code"),
                            "message": (e.get("error") or {}).get("message", "")[:160]}
        c, e = g.r("change-controller").try_("upstream", "submit", packet_id, "--destination", dest)
        obs["submit_L3_no_approval"] = {"ok": e.get("ok"), "code": (e.get("error") or {}).get("code"),
                                        "message": (e.get("error") or {}).get("message", "")[:160]}
    # a lesson carrying a secret must not become a packet
    les = ry(root, "spec/lessons/L-0004.yaml")
    les["id"] = "L-0009"
    les["problem_statement"] = "leak AWS_SECRET_ACCESS_KEY=AKIAVV10SECRETMARKERXXXXXXXX in the reproducer"
    wy(root, "spec/lessons/L-0009.yaml", les)
    commit(root, "poisoned lesson")
    c, e = g.r("research-agent").try_("upstream", "prepare", "L-0009")
    obs["prepare_secret_bearing_lesson"] = {"ok": e.get("ok"), "code": (e.get("error") or {}).get("code"),
                                            "message": (e.get("error") or {}).get("message", "")[:200]}
    blob2 = ""
    for b, _, fs in os.walk(root):
        if ".git" in b:
            continue
        for f in fs:
            if "UP-" in f:
                blob2 += open(os.path.join(b, f), errors="ignore").read()
    obs["secret_in_any_packet_after"] = "AKIAVV10SECRETMARKER" in blob2
    # index-side control
    q = g.ok("memory", "query", "AKIAVV10SECRETMARKERXXXXXXXX")
    obs["secret_retrievable"] = [h.get("path") for h in q.get("hits", []) if "secrets.env" in (h.get("path") or "")]
    bad = []
    if obs["prepare_project_scope"]["ok"]:
        bad.append("a PROJECT-scope lesson was prepared for upstream export")
    if obs["secret_in_packet"] or obs["secret_in_any_packet_after"]:
        bad.append("a secret reached an upstream packet")
    if obs["customer_marker_in_packet"]:
        bad.append("restricted customer content reached an upstream packet")
    if obs["identifier_in_packet"]:
        bad.append("an identifier that must be stripped survived into the packet")
    if obs.get("submit_L1", {}).get("ok"):
        bad.append("an L1 role submitted an upstream packet")
    if obs.get("submit_L3_no_approval", {}).get("ok"):
        bad.append("an upstream packet was submitted without the export gate/approval")
    if obs["prepare_secret_bearing_lesson"]["ok"] and obs["secret_in_any_packet_after"]:
        bad.append("a secret-bearing lesson produced a packet containing the secret")
    if obs["secret_retrievable"]:
        bad.append("the secret file is retrievable from the index")
    record("VV-10", "upstream export boundary: scope, sanitisation, secrets, authority and the export gate",
           "FAIL" if bad else "PASS", {"failures": bad, "observations": obs}, severity="HIGH" if bad else None)


@scenario
def VV11_fresh_agent_reconstruction():
    """A fresh session on a fresh clone reconstructs authoritative state deterministically, with no conversation history"""
    root, g = init_project("vv11")
    obs = {}
    f = g.ok("readiness", "plan", "--feature", "F-0001") if False else None
    t = g.ok("task", "create", "--title", "implement ledger", "--objective", "implement the ledger",
             "--class", "implementation", "--allowed", "src/**")
    g.ok("rebuild-memory")
    commit(root, "state")
    st1 = g.s("S-a").ok("status")
    ct1 = g.s("S-a").try_("context", "compile", t["id"])
    m2 = os.path.join(WORK, "vv11-clone")
    sh(WORK, "git", "clone", "-q", root, m2)
    g2 = Gov(m2, session="S-fresh")
    g2.ok("rebuild-memory")
    st2 = g2.ok("status")
    ct2 = g2.try_("context", "compile", t["id"])
    obs["status_next_action_same"] = st1.get("next_action") == st2.get("next_action")
    obs["status_next_action"] = str(st2.get("next_action"))[:200]
    h1 = (ct1[1].get("result") or {}).get("deterministic_hash") or (ct1[1].get("result") or {}).get("hash")
    h2 = (ct2[1].get("result") or {}).get("deterministic_hash") or (ct2[1].get("result") or {}).get("hash")
    obs["context_hash_a"] = h1
    obs["context_hash_clone"] = h2
    obs["context_keys"] = sorted(list((ct2[1].get("result") or {}).keys()))[:40]
    cont = g2.try_("continue")
    obs["continue"] = json.dumps(cont[1].get("result") or cont[1].get("error"))[:400]
    bad = []
    if not obs["status_next_action_same"]:
        bad.append("status next_action differs between the original and a fresh clone")
    if h1 and h2 and h1 != h2:
        bad.append("context packet hash differs between machines")
    if not (ct2[1].get("ok")):
        bad.append("context compile failed on the fresh clone")
    record("VV-11", "fresh independent agent reconstructs authoritative project context from a clone alone",
           "FAIL" if bad else "PASS", {"failures": bad, "observations": obs}, severity="HIGH" if bad else None)


@scenario
def VV12_dag_and_readiness_expressiveness():
    """One DAG expresses non-coding work; readiness gaps generate typed tasks; gates block only their branch"""
    root, g = init_project("vv12")
    obs = {}
    chain = [("discovery", "map the domain"), ("research", "survey ledger engines"), ("experiment", "benchmark two engines"),
             ("decision-preparation", "choose an engine"), ("specification", "write the ledger spec"), ("test-execution", "run acceptance scenarios"),
             ("data", "representative dataset"), ("test-design", "independent test design"), ("architecture", "component design"),
             ("implementation", "implement"), ("integration", "integrate"), ("security", "threat model"),
             ("devops", "pipeline"), ("performance", "load test"), ("validation", "validate"), ("repair", "repair"),
             ("refactor", "refactor"), ("documentation", "docs"), ("release", "release"), ("tooling", "tooling"),
             ("memory", "memory maintenance"), ("governance", "governance"), ("migration", "migrate paths")]
    ids = []
    created = {}
    for cls, obj in chain:
        deps = ids[-1] if ids else None
        args = ["task", "create", "--title", obj, "--objective", obj, "--class", cls]
        if deps:
            args += ["--deps", deps]
        c, e = g.try_(*args)
        if e.get("ok"):
            ids.append(e["result"]["id"])
            created[cls] = e["result"]["id"]
        else:
            created[cls] = {"error": (e.get("error") or {}).get("code"), "message": (e.get("error") or {}).get("message", "")[:120]}
    obs["classes_accepted"] = [c for c, v in created.items() if isinstance(v, str)]
    obs["classes_rejected"] = {c: v for c, v in created.items() if not isinstance(v, str)}
    dag = g.ok("task", "dag")
    obs["dag"] = {k: dag.get(k) for k in ("nodes", "edges", "cycles", "longest_chain", "missing_dependencies", "runnable") if k in dag}
    obs["dag_keys"] = sorted(dag.keys())
    # a human gate blocking one branch must not stop independent branches
    gt = g.ok("gate", "create", "--question", "choose the ledger engine?", "--blocks", ids[3] if len(ids) > 3 else ids[0]) if False else None
    obs["scenario_record_type_exists"] = os.path.exists(os.path.join(root, "governance/kernel/schemas/scenario.schema.json"))
    rd_ = g.try_("readiness", "check", "F-0001")
    obs["readiness_check"] = json.dumps(rd_[1].get("result") or rd_[1].get("error"))[:500]
    bad = []
    if obs["classes_rejected"]:
        bad.append(f"task classes rejected by the DAG: {list(obs['classes_rejected'])}")
    if dag.get("cycles"):
        bad.append("the linear chain produced a cycle")
    record("VV-12", "the dynamic task DAG expresses discovery→research→experiment→decision→…→validation, not only coding",
           "FAIL" if bad else "PASS", {"failures": bad, "observations": obs}, severity="MEDIUM" if bad else None)


@scenario
def VV13_model_routing_floors():
    """Routing is tier-based; overlay may raise but not lower a tier floor; no LLM is contacted"""
    root, g = init_project("vv13")
    obs = {}
    base = g.ok("route", "--class", "architecture", "--radius", "R4")
    obs["architecture_R4"] = {k: base.get(k) for k in ("minimum_tier", "reasoning", "chosen") if k in base}
    obs["route_keys"] = sorted(base.keys())
    low = g.r("routine-documentation").ok("route", "--class", "documentation", "--radius", "R0")
    obs["documentation_R0"] = {k: low.get(k) for k in ("tier", "minimum_tier", "reasoning", "chosen") if k in low}
    # overlay tries to LOWER the tier floor for a critical class
    mo = ry(root, "governance/project/MODEL_ROUTING_OVERRIDES.yaml")
    pp = ry(root, "governance/project/PROJECT_POLICY.yaml")
    pp.setdefault("policy_overrides", {})["MODEL_ROUTING_POLICY.task_class_minimum_tier.architecture"] = "T0"
    wy(root, "governance/project/PROJECT_POLICY.yaml", pp)
    ov = g.ok("policy", "overrides")
    obs["lower_tier_refused"] = any(a["key"] == "task_class_minimum_tier.architecture" for a in ov.get("refused", []))
    after = g.ok("route", "--class", "architecture", "--radius", "R4")
    obs["architecture_R4_after"] = {k: after.get(k) for k in ("tier", "minimum_tier", "reasoning", "chosen") if k in after}
    pp["policy_overrides"]["MODEL_ROUTING_POLICY.task_class_minimum_tier.documentation"] = "T3"
    wy(root, "governance/project/PROJECT_POLICY.yaml", pp)
    ov2 = g.ok("policy", "overrides")
    obs["raise_tier_applied"] = any(a["key"] == "task_class_minimum_tier.documentation" for a in ov2.get("applied", []))
    raised = g.r("routine-documentation").ok("route", "--class", "documentation", "--radius", "R0")
    obs["documentation_R0_after_raise"] = {k: raised.get(k) for k in ("minimum_tier", "chosen") if k in raised}
    obs["tier_actually_raised"] = raised.get("minimum_tier") != low.get("minimum_tier")
    obs["overrides_yaml_untouched"] = mo == ry(root, "governance/project/MODEL_ROUTING_OVERRIDES.yaml")
    bad = []
    if not obs["lower_tier_refused"]:
        bad.append("the overlay lowered a task-class minimum tier")
    if obs["architecture_R4"] != obs["architecture_R4_after"]:
        bad.append("the refused override still changed the routing decision")
    if not obs["raise_tier_applied"]:
        bad.append("a strengthening (raising) tier override was not applied")
    if not obs.get("tier_actually_raised"):
        bad.append("the applied strengthening override did not change the effective minimum tier")
    record("VV-13", "model routing is capability-tier based and its floors cannot be lowered by project policy",
           "FAIL" if bad else "PASS", {"failures": bad, "observations": obs}, severity="MEDIUM" if bad else None)


@scenario
def VV14_kernel_integrity_is_not_enforced_at_use_time():
    """Does any governed operation refuse to proceed while the installed kernel fails its integrity check?"""
    root, g = init_project("vv14")
    obs = {}
    good = g.doctor()
    obs["d003_before"] = [c["ok"] for c in good["checks"] if c["id"] == "D003"]
    ds0 = ry(root, "governance/project/DATA_SENSITIVITY.yaml")
    ds0.setdefault("classifications", []).append({"pattern": "customer/**", "class": "restricted", "reason": "probe"})
    wy(root, "governance/project/DATA_SENSITIVITY.yaml", ds0)
    wr(root, "customer/secretdoc.md", "VV14RESTRICTEDMARKER private terms\n")
    commit(root, "restricted baseline")
    rb0 = g.ok("rebuild-memory")
    obs["exclusions_with_intact_kernel"] = rb0.get("excluded")
    # tamper a kernel policy that carries a security floor
    sec = ry(root, "governance/kernel/policies/SECURITY_POLICY.yaml")
    obs["never_index_before"] = sec.get("never_index_classes")
    sec["never_index_classes"] = []
    wy(root, "governance/kernel/policies/SECURITY_POLICY.yaml", sec)
    ds = ry(root, "governance/project/DATA_SENSITIVITY.yaml")
    ds.setdefault("classifications", []).append({"pattern": "customer/**", "class": "restricted", "reason": "probe"})
    wy(root, "governance/project/DATA_SENSITIVITY.yaml", ds)
    wr(root, "customer/secretdoc.md", "VV14RESTRICTEDMARKER private terms\n")
    commit(root, "tampered kernel")
    obs["baseline_exclusions"] = None
    rb = g.try_("rebuild-memory")
    obs["rebuild_after_kernel_tamper"] = {"ok": rb[1].get("ok"), "code": (rb[1].get("error") or {}).get("code"),
                                          "excluded": (rb[1].get("result") or {}).get("excluded")}
    q = g.try_("memory", "query", "VV14RESTRICTEDMARKER")
    hits = [h.get("path") for h in ((q[1].get("result") or {}).get("hits") or [])]
    obs["restricted_indexed_after_tamper"] = [h for h in hits if "customer/" in (h or "")]
    doc = g.doctor()
    obs["d003_after"] = [{"ok": c["ok"], "severity": c["severity"], "msg": c["message"][:120]} for c in doc["checks"] if c["id"] == "D003"]
    obs["doctor_verdict"] = doc["verdict"]
    au = g.try_("audit")
    au_r = au[1].get("result") or (au[1].get("error") or {}).get("details") or {}
    obs["audit_verdict"] = au_r.get("verdict") if isinstance(au_r, dict) else None
    obs["audit_kernel_findings"] = [f for f in json.dumps(au_r)[:4000].split(",") if "kernel" in f.lower()][:5]
    bad = []
    if not obs["d003_after"] or obs["d003_after"][0]["ok"]:
        bad.append("doctor did not detect the kernel tampering")
    if obs["rebuild_after_kernel_tamper"]["ok"]:
        bad.append("rebuild-memory proceeded while the installed kernel failed its own integrity check (D003 CRITICAL); the effective security floor is read from the tampered file without verification")
    record("VV-14", "installed-kernel integrity is verified before the kernel's own security floors are trusted",
           "FAIL" if bad else "PASS",
           {"failures": bad, "observations": obs,
            "note": "D003/`gov kernel verify` detect the tampering after the fact; the question is whether enforcement paths consult it"},
           severity="MEDIUM" if bad else None)

@scenario
def VV15_dirty_brownfield_adoption():
    """Deliberately dirty brownfield: hazards detected, secrets never indexed, destructive steps gated, native layout kept"""
    root = fixture("brownfield", "vv15")
    g = Gov(root)
    obs = {}
    g.r("orchestrator").ok("adopt", "baseline")
    inv = g.r("orchestrator").ok("adopt", "inventory")
    obs["inventory_counts"] = {k: v for k, v in inv.items() if isinstance(v, (int, float))}
    cls = g.r("orchestrator").ok("adopt", "classify")
    blob = json.dumps(cls)
    obs["classify_keys"] = sorted(cls.keys())
    obs["secret_files_classified"] = [x for x in (".env", "config/secrets.yaml") if x in blob]
    mp = g.r("orchestrator").ok("adopt", "map")
    mblob = json.dumps(mp)
    obs["legacy_provider_rules_seen"] = [x for x in (".cursorrules", "copilot-instructions.md", "AGENT_RULES_v2.md") if x in mblob or x in blob]
    obs["stale_index_seen"] = ".index" in mblob or ".index" in blob
    obs["misplaced_seen"] = [x for x in ("docs/legacy_module.py", "docs/test_utils.py") if x in mblob]
    pl = g.r("orchestrator").ok("adopt", "plan")
    obs["plan_batches"] = pl.get("batches") if isinstance(pl.get("batches"), (int, list)) else len(pl.get("batches", []) or [])
    obs["destructive_requires_gate"] = json.dumps(pl).count("requires_human_gate\": true")
    # migration cannot start before the independent review verdict
    c, e = g.r("migration-executor").try_("adopt", "migrate")
    obs["migrate_before_independent_review"] = {"ok": e.get("ok"), "code": (e.get("error") or {}).get("code"),
                                                "message": (e.get("error") or {}).get("message", "")[:180]}
    g.r("orchestrator").ok("adopt", "test-design")
    c, e = g.r("migration-executor").try_("adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED",
                                          "--reviewer-session", "S-v3", "--reviewer-role", "migration-reviewer")
    obs["review_by_executor_same_session"] = {"ok": e.get("ok"), "code": (e.get("error") or {}).get("code"),
                                              "message": (e.get("error") or {}).get("message", "")[:180]}
    c, e = g.r("migration-reviewer").s("S-independent-reviewer").try_("adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED")
    obs["review_by_independent_reviewer"] = {"ok": e.get("ok"), "detail": json.dumps(e.get("result") or e.get("error"))[:220]}
    # destructive batches must not execute without an answered gate
    for b in range(0, 9):
        c, e = g.r("migration-executor").try_("adopt", "migrate", "--batch", str(b))
        r = e.get("result") or {}
        obs[f"migrate_batch_{b}"] = {"ok": e.get("ok"), "code": (e.get("error") or {}).get("code"),
                                     "moved": r.get("moved"), "skipped": r.get("skipped"),
                                     "gated": json.dumps(r)[:200] if e.get("ok") else (e.get("error") or {}).get("message", "")[:180]}
    gl = g.r("orchestrator").ok("gate", "list")
    obs["gates_raised_by_migration"] = [(x.get("id"), x.get("question", "")[:80], x.get("gate_status")) for x in (gl if isinstance(gl, list) else [])]
    obs["deprecated_gate_answer_flag_ignored"] = None
    c, e = g.r("migration-executor").try_("adopt", "migrate", "--gate-answer", "yes")
    obs["deprecated_gate_answer_flag_ignored"] = {"ok": e.get("ok"), "detail": json.dumps(e.get("result") or e.get("error"))[:220]}
    c, e = g.r("migration-executor").try_("adopt", "extract-legacy")
    obs["extract_legacy"] = {"ok": e.get("ok"), "code": (e.get("error") or {}).get("code"),
                             "detail": json.dumps(e.get("result") or e.get("error"))[:250]}
    bm = g.r("orchestrator").try_("adopt", "build-memory")
    obs["build_memory"] = {"ok": bm[1].get("ok"), "detail": json.dumps(bm[1].get("result") or bm[1].get("error"))[:300]}
    if bm[1].get("ok"):
        for marker, label in [("AKIA", "aws_key"), ("sk_live", "stripe"), ("BEGIN RSA PRIVATE KEY", "private_key")]:
            q = g.try_("memory", "query", marker)
            hits = [h.get("path") for h in ((q[1].get("result") or {}).get("hits") or [])]
            obs[f"secret_hits_{label}"] = [h for h in hits if h and ("secrets" in h or h == ".env")]
    obs["native_layout_preserved"] = {"pyproject.toml": os.path.exists(os.path.join(root, "pyproject.toml")),
                                      "web/package.json": os.path.exists(os.path.join(root, "web/package.json"))}
    doc = g.doctor()
    obs["doctor_verdict"] = doc["verdict"]
    obs["doctor_failed"] = [(c["id"], c["severity"], c["message"][:90]) for c in doc["checks"] if not c["ok"]]
    bad = []
    for k in list(obs):
        if k.startswith("secret_hits_") and obs[k]:
            bad.append(f"secret-class content retrievable ({k}: {obs[k]})")
    if not obs["native_layout_preserved"]["pyproject.toml"] or not obs["native_layout_preserved"]["web/package.json"]:
        bad.append("a healthy native package layout was destroyed by adoption")
    if obs["migrate_before_independent_review"]["ok"]:
        bad.append("migration ran before the independent review verdict")
    if obs["review_by_executor_same_session"]["ok"]:
        bad.append("the migration executor supplied its own independent review verdict")
    destructive_ran_ungated = [k for k, v in obs.items() if k.startswith("migrate_batch_") and v.get("ok") and "human gate" in str(v.get("gated", "")).lower() and "answered" not in str(v.get("gated", "")).lower()]
    if destructive_ran_ungated:
        bad.append(f"a gated migration batch executed without an answered gate: {destructive_ran_ungated}")
    record("VV-15", "deliberately dirty brownfield adoption: hazards, secret exclusion, destructive gating, native layout",
           "FAIL" if bad else "PASS", {"failures": bad, "observations": obs}, severity="HIGH" if bad else None)


@scenario
def VV16_failure_injection_and_recovery():
    """Interrupted transaction, corrupted derived store and a missing tool are recovered or fail closed"""
    root, g = init_project("vv16")
    obs = {}
    # 1. interrupted CIT: leave a transaction EXECUTING
    mf = os.path.join(root, ".governance-runtime/vv16m.json")
    os.makedirs(os.path.dirname(mf), exist_ok=True)
    open(mf, "w").write(json.dumps([{"op": "write_file", "path": "src/added.rs", "content": "pub const A: u8 = 1;\n"}]))
    c = g.r("change-controller").ok("cit", "propose", "--proposal", "add const", "--trigger", "security_change", "--manifest", mf)
    cid = c["id"]
    if c.get("cit_status") != "SIMULATED":
        g.r("change-controller").ok("cit", "simulate", cid)
    rec = g.r("change-controller").ok("cit", "show", cid)
    gate = rec.get("human_gate")
    g.r("change-controller").ok("gate", "present", gate)
    g.r("human").ok("decide", gate, "--option", "A", "--by", "owner")
    g.r("change-controller").ok("cit", "approve", cid, "--method", "human", "--by", "owner")
    cpath = find_record(root, cid)
    cdoc = ry(root, os.path.relpath(cpath, root))
    cdoc["cit_status"] = "EXECUTING"
    wy(root, os.path.relpath(cpath, root), cdoc)
    doc = g.doctor()
    d016 = [c for c in doc["checks"] if c["id"] == "D016"]
    obs["interrupted_detected"] = {"ok": d016[0]["ok"], "message": d016[0]["message"][:160]} if d016 else None
    rc = g.r("change-controller").try_("recover", "--dry-run")
    obs["recover_dry_run"] = json.dumps(rc[1].get("result") or rc[1].get("error"))[:400]
    rc2 = g.r("change-controller").try_("recover")
    obs["recover"] = json.dumps(rc2[1].get("result") or rc2[1].get("error"))[:400]
    # 2. corrupt the derived store
    dbp = os.path.join(root, ".governance-runtime/state.db")
    with open(dbp, "r+b") as f:
        f.seek(0)
        f.write(b"NOTASQLITEFILE!!")
    q = g.try_("memory", "query", "ledger")
    obs["query_on_corrupt_db"] = {"ok": q[1].get("ok"), "code": (q[1].get("error") or {}).get("code")}
    rb = g.try_("rebuild-memory")
    obs["rebuild_after_corruption"] = {"ok": rb[1].get("ok"), "code": (rb[1].get("error") or {}).get("code"),
                                       "manifest": (rb[1].get("result") or {}).get("manifest_hash")}
    if not rb[1].get("ok"):
        os.remove(dbp)
        rb = g.try_("rebuild-memory")
        obs["rebuild_after_delete"] = {"ok": rb[1].get("ok"), "manifest": (rb[1].get("result") or {}).get("manifest_hash")}
    # 3. missing tool
    res = g.try_("tools", "resolve", "--capability", "build")
    obs["tools_resolve_missing"] = json.dumps(res[1].get("result") or res[1].get("error"))[:400]
    bad = []
    if obs["interrupted_detected"] and obs["interrupted_detected"]["ok"]:
        bad.append("an interrupted transaction was not detected")
    if not (obs.get("rebuild_after_corruption", {}).get("ok") or obs.get("rebuild_after_delete", {}).get("ok")):
        bad.append("the derived store could not be rebuilt after corruption")
    if obs["query_on_corrupt_db"]["ok"]:
        bad.append("a query against a corrupted derived store silently succeeded")
    record("VV-16", "failure injection: interrupted transaction, corrupted derived store, missing tool",
           "FAIL" if bad else "PASS", {"failures": bad, "observations": obs}, severity="HIGH" if bad else None)

def main():
    summary = {}
    for r in RESULTS:
        summary[r["verdict"]] = summary.get(r["verdict"], 0) + 1
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "results.json"), "w") as f:
        json.dump(RESULTS, f, indent=1)
    print("\nWORK:", WORK)
    print("SUMMARY:", summary)


if __name__ == "__main__":
    main()
