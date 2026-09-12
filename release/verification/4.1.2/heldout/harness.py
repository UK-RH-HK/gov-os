#!/usr/bin/env python3
"""Independent verifier held-out harness for agentic-engineering-os 4.1.2.
Run from the canonical repository after `cargo build --release`:  python3 release/verification/4.1.2/heldout/harness.py [HV01 HV36 ...]
Requires python3 with pyyaml and jsonschema (used only by the harness, never by the core).
Black-box: drives target/release/gov through the API-0002 JSON contract only. Never imports the builder's harness.
Each scenario records an OBSERVATION with verdict PASS (behaviour conforms), FAIL (defect confirmed) or INFO.
"""
import json, os, shutil, subprocess, sys, tempfile, hashlib, sqlite3, math, time, re, traceback
import yaml

CANON = os.environ.get("GOV_CANONICAL_ROOT") or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
GOV = os.path.join(CANON, "target/release/gov")
OUT_DIR = os.environ.get("GOV_VERIFIER_OUT") or os.path.dirname(os.path.abspath(__file__))
WORK = tempfile.mkdtemp(prefix="gov-verifier-")
RESULTS = []
sys.path.insert(0, os.path.join(CANON, "capabilities/python"))
from govos_capabilities.embedder_hashed_ngram import HashedNgramEmbedder  # reference == core builtin (bit-identical per builder test)

def record(sid, title, verdict, detail, severity=None):
    RESULTS.append({"id": sid, "title": title, "verdict": verdict, "severity": severity, "detail": detail})
    print(f"[{verdict}] {sid} {title} :: {json.dumps(detail)[:400]}")

class Gov:
    def __init__(self, root, session="S-verifier", role="orchestrator", env=None):
        self.root, self.session, self.role, self.env = root, session, role, (env or {})
    def with_session(self, s): return Gov(self.root, s, self.role, self.env)
    def with_role(self, r): return Gov(self.root, self.session, r, self.env)
    def with_env(self, k, v): e = dict(self.env); e[k] = v; return Gov(self.root, self.session, self.role, e)
    def run(self, *args):
        env = dict(os.environ); env["GOV_CANONICAL_ROOT"] = CANON; env.pop("GOV_SESSION", None); env.pop("GOV_ROLE", None); env.update(self.env)
        cmd = [GOV, "--json", "--root", self.root, "--session", self.session, "--role", self.role] + list(args)
        p = subprocess.run(cmd, capture_output=True, text=True, env=env)
        try: envl = json.loads(p.stdout.strip())
        except Exception: envl = {"ok": False, "error": {"code": "NO_JSON", "message": p.stderr[-800:]}}
        return p.returncode, envl
    def ok(self, *args):
        code, e = self.run(*args)
        if not e.get("ok"): raise RuntimeError(f"gov {' '.join(args)} failed ({code}): {json.dumps(e.get('error'))[:600]}")
        return e["result"]
    def err(self, *args):
        code, e = self.run(*args)
        if e.get("ok"): raise RuntimeError(f"gov {' '.join(args)} unexpectedly succeeded: {json.dumps(e.get('result'))[:300]}")
        return code, e["error"]
    def try_(self, *args):
        code, e = self.run(*args); return code, e

def sh(cwd, *cmd):
    return subprocess.run(list(cmd), cwd=cwd, capture_output=True, text=True)
def git_init(root):
    sh(root, "git", "init", "-q"); sh(root, "git", "config", "user.email", "v@example.invalid"); sh(root, "git", "config", "user.name", "verifier")
    sh(root, "git", "add", "-A"); sh(root, "git", "commit", "-q", "-m", "baseline")
def commit(root, msg="wip"): sh(root, "git", "add", "-A"); sh(root, "git", "commit", "-q", "-m", msg)
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
def tree_hash(root, skip=(".git", ".governance-runtime")):
    h = hashlib.sha256()
    for dp, dn, fn in os.walk(root):
        dn[:] = sorted(d for d in dn if d not in skip)
        for f in sorted(fn):
            p = os.path.join(dp, f); rel = os.path.relpath(p, root); h.update(rel.encode()); h.update(sha(p).encode())
    return h.hexdigest()
def report_file(root, name, work, files, tests="not_applicable_with_reason"):
    p = os.path.join(root, ".governance-runtime", "reports"); os.makedirs(p, exist_ok=True)
    f = os.path.join(p, name + ".json"); open(f, "w").write(json.dumps({"work_completed": work, "files_changed": files, "tests": {"status": tests, "reason": "verifier"}, "outcome": "success", "evidence": []})); return f
def doctor(g, cid):
    code, e = g.run("doctor"); r = e["result"] if e.get("ok") else e["error"]["details"]
    c = next(c for c in r["checks"] if c["id"] == cid); return c["ok"], c["message"], r["verdict"]
def readiness_all_present(): 
    dims = yaml.safe_load(open(os.path.join(CANON, "framework/taxonomy/READINESS_DIMENSIONS.yaml")))["dimensions"]
    return {d["id"]: "PRESENT" for d in dims}
def cosine(a, b): return sum(x*y for x, y in zip(a, b))

def scenario(fn):
    def wrapper():
        try: fn()
        except Exception as e:
            record(fn.__name__, "harness exception", "ERROR", {"error": str(e)[:800], "trace": traceback.format_exc()[-1200:]})
    return wrapper

# ---------------------------------------------------------------------------------------------------------------------
@scenario
def HV01_embedder_replaceable_at_query_time():
    root = fixture("greenfield", "hv01"); g = Gov(root)
    g.ok("init", "--name", "hv01", "--alias", "hv01-alias", "--skip-index")
    wy(root, "governance/project/plugins/echo.yaml", {"plugin_id": "echo-embedder-sh", "capability": "embed", "version": "1", "command": [os.path.join(CANON, "capabilities/shell/echo_embedder.sh")], "languages": []})
    pp = ry(root, "governance/project/PROJECT_POLICY.yaml"); pp["policy_overrides"] = {"MEMORY_POLICY.embedding.provider": "echo-embedder-sh", "MEMORY_POLICY.embedding.dimensions": 8}; wy(root, "governance/project/PROJECT_POLICY.yaml", pp)
    # a few distinct records so ranking is meaningful
    for i, t in enumerate(["Order totals are exact integer cents", "Ledger rejects duplicate order identifiers", "Clerk appends two orders and reads the total"], 1):
        wy(root, f"spec/requirements/REQ-{i:04d}.yaml", {"id": f"REQ-{i:04d}", "type": "requirement", "title": t, "status": "ACTIVE", "kind": "functional", "acceptance_criteria": [t]})
    r = g.ok("rebuild-memory")
    m = rj(root, "governance/generated/index-manifest.json")
    q = "Ledger rejects duplicate order identifiers"
    res = g.ok("memory", "query", q, "--route", "semantic", "--k", "6")
    gov_rank = [(h["chunk_id"], round(h["score"], 6)) for h in res["hits"]]
    # replicate: what would the ranking be if the query were embedded with the BUILTIN hashed-ngram (8-dim) against the plugin vectors?
    con = db(root); rows = con.execute("SELECT chunk_id, artifact_id, vec, embedder, dim FROM vectors").fetchall(); con.close()
    embedders = sorted({r_[3] for r_ in rows}); dims = sorted({r_[4] for r_ in rows})
    qv_builtin = HashedNgramEmbedder(dim=8, version="1").embed(q)
    scored = sorted(((cosine(qv_builtin, json.loads(v)), cid, aid) for cid, aid, v, _, _ in rows), key=lambda x: (-x[0], x[1]))
    builtin_top = [cid for s, cid, aid in scored if s > 0][:6]
    gov_top = [cid for cid, _ in gov_rank]
    match = gov_top == builtin_top
    expected_hit = any(h["artifact_id"] == "REQ-0002" for h in res["hits"][:3])
    record("HV-01", "embedding model replaceable at query time (index built by plugin, query embedded by whom?)",
           "FAIL" if match else "PASS",
           {"manifest_embedder": m["embedder"], "stored_vector_embedders": embedders, "stored_dims": dims, "gov_semantic_ranking": gov_top, "ranking_if_query_used_builtin_hashed_ngram": builtin_top, "rankings_identical": match, "expected_record_in_top3": expected_hit,
            "interpretation": "identical rankings prove the core embeds the query with the built-in embedder while the index holds plugin vectors: two different vector spaces are compared" if match else "core used the pinned embedder for the query"}, severity="CRITICAL" if match else None)

@scenario
def HV02_reranker_hook_exists():
    root = fixture("greenfield", "hv02"); g = Gov(root)
    g.ok("init", "--name", "hv02", "--alias", "hv02-alias", "--skip-index")
    marker = os.path.join(root, ".governance-runtime", "RERANK_INVOKED"); os.makedirs(os.path.dirname(marker), exist_ok=True)
    script = os.path.join(root, "rerank.sh")
    wr(root, "rerank.sh", "#!/usr/bin/env bash\nREQ=$(cat)\ntouch '%s'\nprintf '{\"protocol\":\"gov-capability/1\",\"ok\":true,\"provider\":{\"id\":\"marker-reranker\",\"version\":\"1\"},\"outputs\":{\"scores\":[]}}'\n" % marker); os.chmod(script, 0o755)
    wy(root, "governance/project/plugins/rerank.yaml", {"plugin_id": "marker-reranker", "capability": "rerank", "version": "1", "command": [script], "languages": []})
    pp = ry(root, "governance/project/PROJECT_POLICY.yaml"); pp["policy_overrides"] = {"MEMORY_POLICY.reranker.provider": "marker-reranker"}; wy(root, "governance/project/PROJECT_POLICY.yaml", pp)
    g.ok("rebuild-memory")
    plugins = g.ok("capabilities", "plugins")
    g.ok("memory", "query", "why was the ledger designed with integer cents", "--k", "5")
    m = rj(root, "governance/generated/index-manifest.json")
    invoked = os.path.exists(marker)
    record("HV-02", "reranker plugin is invoked when pinned (API-0001 rerank capability wired into retrieval?)", "PASS" if invoked else "FAIL",
           {"plugin_discovered": any(p["plugin_id"] == "marker-reranker" for p in plugins), "manifest_reranker": m.get("reranker"), "reranker_invoked_during_query": invoked}, severity=None if invoked else "HIGH")

@scenario
def HV03_authority_levels_enforced():
    root = fixture("greenfield", "hv03"); g = Gov(root)
    g.ok("init", "--name", "hv03", "--alias", "hv03-alias")
    obs = {}
    aud = g.with_role("independent-auditor")   # L0 read-only
    code, e = aud.try_("task", "create", "--class", "documentation", "--objective", "auditor writes a task", "--status", "READY"); obs["L0_task_create"] = e.get("ok") or e["error"]["code"]
    code, e = aud.try_("cit", "propose", "--proposal", "auditor proposes a change", "--trigger", "editorial"); obs["L0_cit_propose"] = e.get("ok") or e["error"]["code"]
    cid = e["result"]["id"] if e.get("ok") else None
    if cid:
        code, e = aud.try_("cit", "simulate", cid); obs["L0_cit_simulate"] = e.get("ok") or e["error"]["code"]
        code, e = aud.try_("cit", "approve", cid, "--by", "auditor-agent", "--method", "auto"); obs["L0_cit_approve_auto"] = e.get("ok") or e["error"]["code"]
        code, e = aud.try_("cit", "execute", cid); obs["L0_cit_execute"] = e.get("ok") or e["error"]["code"]
    worker = g.with_role("research-agent")  # L1
    code, e = worker.try_("gate", "create", "--question", "worker creates a gate?"); gid = e["result"]["id"] if e.get("ok") else None; obs["L1_gate_create"] = e.get("ok") or e["error"]["code"]
    if gid:
        worker.try_("gate", "present", gid)
        code, e = worker.try_("decide", gid, "--option", "A", "--by", "research-agent"); obs["L1_decide_gate_as_agent"] = e.get("ok") or e["error"]["code"]
    code, e = worker.try_("freeze-writes", "--reason", "worker freezes"); obs["L1_freeze_writes"] = e.get("ok") or e["error"]["code"]; worker.try_("resume")
    code, e = worker.try_("kernel", "reinstall"); obs["L1_kernel_reinstall"] = e.get("ok") or e["error"]["code"]
    refused = [k for k, v in obs.items() if v is not True]
    record("HV-03", "authority levels L0-L5 (AUTHORITY_POLICY.authority_levels_required) enforced on mutating operations", "PASS" if len(refused) >= 5 else "FAIL",
           {"operations_by_low_authority_roles": obs, "refused": refused, "note": "AUTHORITY_POLICY.authority_levels_required is never read by the core (grep=0)"}, severity=None if len(refused) >= 5 else "HIGH")

@scenario
def HV04_mutation_scope_enforced_at_task_close():
    root = fixture("greenfield", "hv04"); g = Gov(root)
    g.ok("init", "--name", "hv04", "--alias", "hv04-alias")
    t = g.ok("task", "create", "--class", "implementation", "--objective", "scoped impl", "--status", "READY", "--allowed", "src/**")
    tid = t["id"]; g.ok("task", "claim", tid)
    wr(root, "spec/scenarios/SCN-0099.yaml", "id: SCN-0099\ntype: scenario\ntitle: written outside allowed paths\nstatus: ACTIVE\n")
    wr(root, "README.md", rd(root, "README.md") + "\nedited outside allowed paths\n")
    rep = report_file(root, "hv04", "changed files outside allowed_paths", ["spec/scenarios/SCN-0099.yaml", "README.md"], "passed")
    g.ok("rebuild-memory", "--incremental")
    code, e = g.try_("task", "close", tid, "--report", rep)
    record("HV-04", "task close rejects files_changed outside the task's allowed_paths (mutation manifest scope)", "FAIL" if e.get("ok") else "PASS",
           {"allowed_paths": ["src/**"], "files_changed": ["spec/scenarios/SCN-0099.yaml", "README.md"], "close_result": e.get("result", e.get("error"))}, severity="HIGH" if e.get("ok") else None)

@scenario
def HV05_claims_survive_full_rebuild():
    root = fixture("greenfield", "hv05"); g = Gov(root)
    g.ok("init", "--name", "hv05", "--alias", "hv05-alias")
    t = g.ok("task", "create", "--class", "documentation", "--objective", "claimed work", "--status", "READY"); tid = t["id"]
    a = g.with_session("S-alpha"); b = g.with_session("S-beta")
    a.ok("task", "claim", tid)
    code, e = b.try_("task", "claim", tid); second_before = e.get("ok") or e["error"]["code"]
    before = a.ok("claims", "list")
    a.ok("rebuild-memory")   # full rebuild (the same call `gov recover`, A10 and the deep suite make)
    after = a.ok("claims", "list")
    code, e = b.try_("task", "claim", tid); second_after = e.get("ok") or e["error"]["code"]
    lost = len(before) > 0 and len(after) == 0
    record("HV-05", "session claims (deterministic state) survive a full derived-memory rebuild", "FAIL" if lost or second_after is True else "PASS",
           {"claims_before_rebuild": len(before), "claims_after_rebuild": len(after), "second_session_claim_before": second_before, "second_session_claim_after_rebuild": second_after,
            "task_status_after": g.ok("task", "show", tid)["task_status"]}, severity="HIGH" if lost else None)

@scenario
def HV06_tool_registry_resolves_native_tooling_per_language():
    root = fixture("greenfield", "hv06"); g = Gov(root)
    g.ok("init", "--name", "hv06", "--alias", "hv06-alias")
    r = g.ok("tools", "resolve", "--capability", "run_tests")
    health = g.ok("tools", "health")
    kt = yaml.safe_load(open(os.path.join(CANON, "tools/registry/TOOLS.yaml")))["tools"]
    lang_specific = [t["tool_id"] for t in kt if any(w in json.dumps(t).lower() for w in ["python", "pytest"])]
    rust_tools = [t["tool_id"] for t in kt if any(w in json.dumps(t).lower() for w in ["cargo", "clippy", "rustfmt", "rust-analyzer"])]
    resolved = [t["tool_id"] for t in r["tools"]]
    eco = g.ok("capabilities", "ecosystems")
    record("HV-06", "Tool Capability Registry resolves native run_tests tooling for a Rust governed project (not Python)", "FAIL" if "TOOL-TEST-001" in resolved or not rust_tools else "PASS",
           {"resolved_for_run_tests_on_rust_project": resolved, "registry_python_specific_tools": lang_specific, "registry_rust_tools": rust_tools, "health_checks_run": [(h["tool_id"], h.get("kind"), h.get("ok")) for h in health],
            "ecosystems_detected": [e["id"] for e in eco["ecosystems"]], "note": "ecosystem detection is a hard-coded Rust table, not the registry; kernel payload tools/ is not covered by the language-neutrality test (it scans framework/ only)"}, severity="MEDIUM")

@scenario
def HV07_embedder_pin_change_invalidates_index():
    root = fixture("greenfield", "hv07"); g = Gov(root)
    g.ok("init", "--name", "hv07", "--alias", "hv07-alias")
    m1 = rj(root, "governance/generated/index-manifest.json")["embedder"]
    pp = ry(root, "governance/project/PROJECT_POLICY.yaml"); pp["policy_overrides"] = {"MEMORY_POLICY.embedding.dimensions": 64, "MEMORY_POLICY.embedding.version": "2"}; wy(root, "governance/project/PROJECT_POLICY.yaml", pp)
    fr = g.ok("memory", "freshness"); ok10, msg10, _ = doctor(g, "D010")
    t = g.ok("task", "create", "--class", "documentation", "--objective", "x", "--status", "READY"); g.ok("task", "claim", t["id"])
    rep = report_file(root, "hv07", "w", [])
    g.ok("rebuild-memory", "--incremental")   # incremental: does it notice the embedder pin changed?
    m2 = rj(root, "governance/generated/index-manifest.json")["embedder"]
    con = db(root); dims = con.execute("SELECT DISTINCT dim FROM vectors").fetchall(); con.close()
    record("HV-07", "changing the pinned embedder (version/dimensions) marks the index stale and forces a measured re-index (framework 14.3)",
           "FAIL" if fr["fresh"] and ok10 else "PASS",
           {"embedder_before": m1, "policy_override": pp["policy_overrides"], "freshness_after_pin_change": fr["fresh"], "doctor_D010_ok": ok10, "manifest_embedder_after_incremental_rebuild": m2, "vector_dims_in_db_after_incremental": [d[0] for d in dims]}, severity="MEDIUM")

def run_brownfield_adoption(tag):
    root = fixture("brownfield", tag)
    sql = rd(root, "memory/chat_history.sql"); con = sqlite3.connect(os.path.join(root, "memory/chat_history.sqlite")); con.executescript(sql); con.commit(); con.close(); os.remove(os.path.join(root, "memory/chat_history.sql")); commit(root, "chat db")
    planner = Gov(root, "S-planner")
    planner.ok("adopt", "baseline"); planner.ok("adopt", "inventory"); planner.ok("adopt", "classify"); planner.ok("adopt", "map"); planner.ok("adopt", "plan"); planner.ok("adopt", "test-design")
    planner.with_session("S-reviewer").with_role("migration-reviewer").ok("adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED")
    executor = planner.with_session("S-executor").with_role("migration-executor")
    executor.ok("adopt", "migrate", "--name", "shipping-quotes", "--alias", "fx-brown")
    planner.with_session("S-verifier").with_role("migration-verifier").ok("adopt", "verify-migration")
    executor.ok("adopt", "extract-legacy"); executor.ok("adopt", "build-memory")
    planner.with_session("S-memverifier").with_role("memory-verifier").ok("adopt", "verify-memory")
    return root, planner, executor

@scenario
def HV08_golden_retrieval_queries_brownfield():
    root, planner, executor = run_brownfield_adoption("hv08")
    g = executor
    # my own held-out set (never seen by the builder): categories per verifier directive 3
    queries = [
      {"id": "V-EXACT-1", "cat": "exact id", "query": "D-0002", "expected_refs": ["D-0002"], "forbidden": ["D-0001"], "k": 5},
      {"id": "V-PATH-1", "cat": "exact path", "query": "src/app/billing.py", "expected_refs": ["file:src/app/billing.py"], "forbidden": [], "k": 5},
      {"id": "V-LEX-1", "cat": "lexical literal", "query": "\"failed after\" attempts", "expected_refs": ["file:src/app/retry.py"], "forbidden": [], "k": 5},
      {"id": "V-SYM-1", "cat": "symbol", "query": "def with_retry", "expected_refs": ["file:src/app/retry.py"], "forbidden": [], "k": 5},
      {"id": "V-SYM-2", "cat": "symbol reference", "query": "quote_price", "expected_refs": ["file:src/app/billing.py", "file:src/app/main.py"], "forbidden": [], "k": 6},
      {"id": "V-SEM-1", "cat": "semantic paraphrase (no token overlap)", "query": "upper bound on repeated attempts against the payment provider", "expected_refs": ["D-0002"], "forbidden": ["D-0001"], "k": 8},
      {"id": "V-SEM-2", "cat": "semantic paraphrase (morphological)", "query": "retries for gateway", "expected_refs": ["D-0002"], "forbidden": ["D-0001"], "k": 8},
      {"id": "V-SUP-1", "cat": "superseded vs current", "query": "How many times should gateway calls be retried?", "expected_refs": ["D-0002"], "forbidden": ["D-0001"], "k": 5},
      {"id": "V-GRAPH-1", "cat": "graph impact", "query": "what depends on D-0002", "expected_refs": ["D-0002"], "forbidden": [], "k": 8},
      {"id": "V-XFILE-1", "cat": "cross-file dependency", "query": "which module imports ../util/http", "expected_refs": ["file:web/src/api/client.ts"], "forbidden": [], "k": 6},
      {"id": "V-HIST-1", "cat": "historical evidence (chat-derived lesson)", "query": "lesson learned stale vector index cited the 2024 retry rule", "expected_refs": [], "forbidden": [], "k": 6},
      {"id": "V-MIX-1", "cat": "mixed prose/code", "query": "ZONE_RATES pricing per zone in billing", "expected_refs": ["file:src/app/billing.py"], "forbidden": [], "k": 5},
    ]
    # the chat-derived lesson id is dynamic: find it
    lessons = [f for f in os.listdir(os.path.join(root, "spec/lessons")) if f.startswith("L-C")]
    if lessons:
        for q in queries:
            if q["id"] == "V-HIST-1": q["expected_refs"] = [lessons[0][:-5]]
    wy(root, "governance/tests/memory/heldout.yaml", {"version": "verifier-1", "queries": [{k: v for k, v in q.items() if k != "cat"} for q in queries]})
    g.ok("rebuild-memory", "--incremental")
    code, e = g.run("memory", "verify"); r = e["result"] if e.get("ok") else e["error"]["details"]
    per = {q["id"]: (q["cat"], next(x for x in r["results"] if x["id"] == q["id"])["recall"], next(x for x in r["results"] if x["id"] == q["id"])["got"][:4]) for q in queries}
    # superseded decision must not surface while D-0001 is still ACTIVE-but-superseded (pre-remediation)
    d1 = ry(root, "spec/decisions/D-0001.yaml")["status"]
    con = db(root); sup = con.execute("SELECT artifact_id, status, superseded_by FROM artifacts WHERE artifact_id IN ('D-0001','D-0002')").fetchall(); con.close()
    record("HV-08", "verifier-authored golden retrieval set on the adopted brownfield (recall@k, MRR, stale/superseded hits, by category)", "INFO",
           {"recall_at_k": r["recall_at_k"], "mrr": r["mrr"], "stale_hit_rate": r["stale_hit_rate"], "superseded_hit_rate": r["superseded_hit_rate"], "forbidden_violations": r["forbidden_violations"], "pass_under_policy_thresholds": r["pass"],
            "per_query": per, "D-0001_status_on_disk": d1, "db_supersession": sup}, severity=None)
    fails = [k for k, v in per.items() if v[1] < 1.0]
    sem_fail = [k for k in fails if k.startswith("V-SEM")]
    record("HV-08b", "semantic paraphrase retrieval with the pinned baseline embedder", "FAIL" if sem_fail else "PASS",
           {"failed_queries": fails, "semantic_failures": sem_fail, "note": "baseline hashed n-gram embedder has no paraphrase or morphology capability; no comparative benchmark mechanism exists to select a stronger one"}, severity="MEDIUM" if sem_fail else None)
    return root, g

@scenario
def HV09_restricted_sensitivity_class_never_indexed():
    root = fixture("greenfield", "hv09"); g = Gov(root)
    g.ok("init", "--name", "hv09", "--alias", "hv09-alias", "--skip-index")
    ds = ry(root, "governance/project/DATA_SENSITIVITY.yaml"); ds["classifications"] = [{"pattern": "product/data/customers/**", "class": "restricted", "reason": "customer data"}]; wy(root, "governance/project/DATA_SENSITIVITY.yaml", ds)
    rc = ry(root, "governance/project/REPOSITORY_CONTRACT.yaml"); rc["paths"].append({"pattern": "product/legal/**", "class": "authoritative", "sensitivity": "restricted", "semantic_index": True, "lexical_index": True, "namespace": "product"}); wy(root, "governance/project/REPOSITORY_CONTRACT.yaml", rc)
    wr(root, "product/data/customers/list.csv", "customer,email\nAcme Freight Ltd,ops@acme.example\n")
    wr(root, "product/legal/settlement.md", "# Restricted legal settlement\nConfidential settlement terms with Acme Freight Ltd.\n")
    r = g.ok("rebuild-memory")
    con = db(root); rows = con.execute("SELECT path, sensitivity, path_class FROM artifacts WHERE path LIKE 'product/data/%' OR path LIKE 'product/legal/%'").fetchall(); n_chunks = con.execute("SELECT COUNT(*) FROM chunks c JOIN artifacts a ON a.artifact_id=c.artifact_id WHERE a.path LIKE 'product/legal/%' OR a.path LIKE 'product/data/%'").fetchone()[0]; con.close()
    ok11, msg11, verdict = doctor(g, "D011")
    q = g.ok("memory", "query", "Acme Freight settlement terms", "--k", "5")
    leaked = [h["path"] for h in q["hits"] if h["path"].startswith("product/legal") or h["path"].startswith("product/data")]
    record("HV-09", "SECURITY_POLICY.never_index_classes [secret, restricted]: restricted-class material (DATA_SENSITIVITY classification / contract sensitivity) is excluded from generic memory", "FAIL" if rows else "PASS",
           {"indexed_restricted_artifacts": rows, "chunks_from_restricted": n_chunks, "retrieval_returned_restricted_paths": leaked, "doctor_D011": (ok11, msg11), "note": "never_index_classes, never_export_classes and DATA_SENSITIVITY.classifications are never read by the core (grep=0); only class=secret is honoured"}, severity="HIGH" if rows else None)

@scenario
def HV10_automatic_cit_p_on_threshold_triggers():
    root = fixture("greenfield", "hv10"); g = Gov(root)
    g.ok("init", "--name", "hv10", "--alias", "hv10-alias")
    c = g.ok("cit", "propose", "--proposal", "replace the ledger storage engine", "--trigger", "architecture_change")
    st = g.ok("cit", "show", c["id"])["cit_status"]
    record("HV-10", "CIT-P is automatic for CHANGE_POLICY.auto_simulate_triggers (framework 48: the human should not need to type /impact)", "PASS" if st == "SIMULATED" else "FAIL",
           {"trigger": "architecture_change", "status_after_propose": st, "policy_key_read_by_core": "auto_simulate_triggers grep=0"}, severity="MEDIUM" if st != "SIMULATED" else None)

def make_prev_release(dst):
    shutil.copytree(os.path.join(CANON, "framework"), dst); shutil.copytree(os.path.join(CANON, "tools"), os.path.join(dst, "tools"))
    k = yaml.safe_load(open(os.path.join(dst, "KERNEL.yaml"))); k["version"] = "4.1.1"; k["cli_version"] = "4.1.1"; k["runtime_version"] = "4.1.1"; k["supported_from_versions"] = []
    k["payload_dirs"] = ["constitution", "policies", "schemas", "skills", "adapters", "roles", "taxonomy", "commands", "overlay-templates", "tools"]
    open(os.path.join(dst, "KERNEL.yaml"), "w").write(yaml.safe_dump(k, sort_keys=False))
    for f in ["policies/LEARNING_POLICY.yaml", "policies/ARCHIVE_POLICY.yaml", "overlay-templates/PROJECT_EXCEPTIONS.yaml", "schemas/project-exceptions.schema.json"]: os.remove(os.path.join(dst, f))
    p = os.path.join(dst, "overlay-templates/PROJECT_POLICY.yaml"); t = open(p).read().replace("schema_version: 1.0.0", "schema_version: 0.9.0").replace("gates:\n  presentation_channel: chat\n", "human_gates:\n  channel: chat\n"); open(p, "w").write(t)

@scenario
def HV11_update_approval_requires_presented_gate():
    base = os.path.join(WORK, "hv11"); os.makedirs(base); prev = os.path.join(base, "prev-4.1.1"); make_prev_release(prev)
    root = os.path.join(base, "project"); os.makedirs(root); wr(root, "README.md", "# upd\n"); git_init(root); g = Gov(root)
    g.ok("init", "--source", prev, "--name", "hv11", "--alias", "hv11-alias")
    code, e = g.try_("update", "--apply"); first = e["error"]["code"] if not e.get("ok") else "ok"
    gates_before = g.ok("gate", "list")
    ap = g.ok("update", "--apply", "--approve", "--by", "owner")   # no gate presented, no gate answered
    gates_after = g.ok("gate", "list")
    unpresented = [x["id"] for x in gates_after if not x["presented_in_chat"]]
    ok19, msg19, _ = doctor(g, "D019")
    record("HV-11", "gov update --apply --approve bypasses INV-008 (gate presented+answered) while CIT approval enforces it", "FAIL" if ap.get("applied") and unpresented else "PASS",
           {"first_apply_without_approve": first, "gates_pending_before": [x["id"] for x in gates_before], "applied_with_flag_only": ap.get("applied"), "to": ap.get("to"), "pending_unpresented_gates_after_update": unpresented, "doctor_D019_after": (ok19, msg19)}, severity="MEDIUM")

@scenario
def HV12_delete_all_derived_and_generated_then_rebuild():
    root = fixture("greenfield", "hv12"); g = Gov(root)
    g.ok("init", "--name", "hv12", "--alias", "hv12-alias", "--intent", "ledger")
    wy(root, "spec/features/F-0001.yaml", {"id": "F-0001", "type": "feature", "title": "Totals", "status": "ACTIVE", "readiness": readiness_all_present()})
    g.ok("task", "create", "--class", "implementation", "--objective", "Implement totals", "--feature", "F-0001", "--status", "READY", "--allowed", "src/**")
    g.ok("rebuild-memory"); g.ok("adapters", "generate"); g.ok("tools", "registry")
    before = {"manifest": rj(root, "governance/generated/index-manifest.json")["manifest_hash"], "adapters": {k: v["hash"] for k, v in rj(root, "governance/generated/adapter-manifest.json")["adapters"].items()}, "framework_json": sha(os.path.join(root, "framework.json")), "ctx": g.ok("context", "compile", "TASK-0001")["deterministic_hash"], "status_counts": g.ok("status")["tasks"]["counts"]}
    commit(root, "state")
    shutil.rmtree(os.path.join(root, ".governance-runtime")); shutil.rmtree(os.path.join(root, "governance/generated")); os.remove(os.path.join(root, "framework.json"))
    code, e = g.run("doctor"); dv = (e["result"] if e.get("ok") else e["error"]["details"])["verdict"]
    r = g.ok("rebuild-memory"); g.ok("tools", "registry"); g.ok("adapters", "generate")
    after = {"manifest": rj(root, "governance/generated/index-manifest.json")["manifest_hash"], "adapters": {k: v["hash"] for k, v in rj(root, "governance/generated/adapter-manifest.json")["adapters"].items()}, "framework_json": sha(os.path.join(root, "framework.json")), "ctx": g.ok("context", "compile", "TASK-0001")["deterministic_hash"], "status_counts": g.ok("status")["tasks"]["counts"]}
    code, e = g.run("audit", "--no-persist"); av = (e["result"] if e.get("ok") else e["error"]["details"])["verdict"]
    same = before == after
    record("HV-12", "delete vector/SQLite/graph + ALL generated views + framework.json, then rebuild from Git: identical derived state (framework 19)", "PASS" if same else "FAIL",
           {"identical": same, "before": before, "after": after, "doctor_verdict_while_missing": dv, "audit_verdict_after": av}, severity=None if same else "HIGH")

@scenario
def HV13_go_project_governed_without_go_toolchain():
    root = os.path.join(WORK, "hv13-go"); os.makedirs(root)
    wr(root, "go.mod", "module example.com/svc\n\ngo 1.22\n"); wr(root, "main.go", "package main\n\nimport (\n\t\"fmt\"\n\t\"example.com/svc/internal/handler\"\n)\n\nfunc main() {\n\tfmt.Println(handler.Greet(\"x\"))\n}\n")
    wr(root, "internal/handler/handler.go", "package handler\n\nimport \"strings\"\n\n// Greet returns a greeting.\nfunc Greet(name string) string {\n\treturn strings.ToUpper(\"hi \" + name)\n}\n\ntype Server struct{ addr string }\n")
    wr(root, "internal/handler/handler_test.go", "package handler\n\nimport \"testing\"\n\nfunc TestGreet(t *testing.T) { if Greet(\"a\") != \"HI A\" { t.Fatal() } }\n")
    git_init(root); g = Gov(root)
    r = g.ok("init", "--name", "svc", "--alias", "svc-alias")
    eco = g.ok("capabilities", "ecosystems")
    con = db(root); syms = con.execute("SELECT name, kind FROM symbols WHERE language='go'").fetchall(); imports = con.execute("SELECT src, dst FROM edges WHERE type='IMPORTS'").fetchall(); con.close()
    contract = ry(root, "governance/project/REPOSITORY_CONTRACT.yaml")
    native = [p["pattern"] for p in contract["paths"] if p.get("namespace") == "product" and p["pattern"].startswith("internal")]
    pv = g.ok("verify", "product")
    res = g.ok("tools", "resolve", "--capability", "run_tests")
    record("HV-13", "a Go governed project (language different from the OS core and from every shipped fixture) is inventoried, mapped and indexed", "PASS" if eco["count"] >= 1 and syms else "FAIL",
           {"ecosystems": [(e["id"], e["available"], e.get("gap")) for e in eco["ecosystems"]], "go_symbols": syms, "import_edges": imports, "native_layout_rules": native, "verify_product": {"ran": pv.get("ran"), "status": pv.get("status")}, "tools_resolve_run_tests": [t["tool_id"] for t in res["tools"]], "doctor": r["doctor"]}, severity=None)

@scenario
def HV14_cit_rollback_reverts_propagation():
    root = fixture("greenfield", "hv14"); g = Gov(root)
    g.ok("init", "--name", "hv14", "--alias", "hv14-alias")
    wy(root, "spec/requirements/REQ-0001.yaml", {"id": "REQ-0001", "type": "requirement", "title": "Exact cents", "status": "ACTIVE", "kind": "functional", "acceptance_criteria": ["a"]})
    t = g.ok("task", "create", "--class", "implementation", "--objective", "impl", "--status", "READY", "--fields", '{"requirements": ["REQ-0001"]}'); tid = t["id"]
    g.ok("rebuild-memory")
    mf = os.path.join(root, ".governance-runtime/m.json"); open(mf, "w").write(json.dumps([{"op": "set_field", "target": "REQ-0001", "field": "acceptance_criteria", "value": ["a", "b"]}]))
    c = g.ok("cit", "propose", "--proposal", "tighten criteria", "--trigger", "behaviour_change", "--targets", "REQ-0001", "--manifest", mf); cid = c["id"]
    sim = g.ok("cit", "simulate", cid); gate = sim["human_gate"]; g.ok("gate", "present", gate); g.ok("decide", gate, "--option", "A", "--by", "owner"); ap = g.ok("cit", "approve", cid, "--by", "owner", "--method", "human"); g.ok("cit", "execute", cid)
    retest_after_exec = g.ok("task", "show", tid).get("retest_required")
    decisions_before_rb = sorted(os.listdir(os.path.join(root, "spec/decisions")))
    g.ok("cit", "rollback", cid, "--reason", "verifier")
    retest_after_rb = g.ok("task", "show", tid).get("retest_required")
    req = ry(root, "spec/requirements/REQ-0001.yaml")["acceptance_criteria"]
    record("HV-14", "cit rollback reverts propagation side-effects (retest flags) in addition to file snapshots", "PASS" if retest_after_rb in (False, None) else "FAIL",
           {"retest_required_after_execute": retest_after_exec, "retest_required_after_rollback": retest_after_rb, "REQ_criteria_after_rollback": req, "decision_records_after_rollback": decisions_before_rb, "approval_decision_kept": ap["decision"] + ".yaml" in decisions_before_rb}, severity="MEDIUM" if retest_after_rb else None)

@scenario
def HV15_context_compiler_contradictory_active_decisions():
    root = fixture("greenfield", "hv15"); g = Gov(root)
    g.ok("init", "--name", "hv15", "--alias", "hv15-alias")
    wy(root, "spec/decisions/D-0001.yaml", {"id": "D-0001", "type": "decision", "title": "Retry limit is 3", "status": "ACTIVE", "question": "retries?", "chosen_option": "A", "rationale": "old", "human_approved": True})
    wy(root, "spec/decisions/D-0002.yaml", {"id": "D-0002", "type": "decision", "title": "Retry limit is 5", "status": "ACTIVE", "supersedes": ["D-0001"], "question": "retries?", "chosen_option": "B", "rationale": "new", "human_approved": True})
    t = g.ok("task", "create", "--class", "implementation", "--objective", "align retries", "--status", "READY", "--fields", '{"decisions": ["D-0001", "D-0002"]}')
    g.ok("rebuild-memory")
    c = g.ok("context", "compile", t["id"])
    act = [d["id"] for d in c["deterministic_authority"]["active_decisions"]]
    flagged = json.dumps(c["deterministic_authority"]).count("UNKNOWN_OR_CONFLICTING") + json.dumps(c["deterministic_authority"]).count("superseded")
    inv_in_packet = "INV-" in json.dumps(c["deterministic_authority"])
    policy_in_packet = any(k in c["deterministic_authority"] for k in ["hard_invariants", "project_policy", "policies", "security"])
    record("HV-15", "context compiler: superseded-but-ACTIVE decision is flagged/excluded from the deterministic authority block; hard invariants + project policy precede spec in the packet", "FAIL" if ("D-0001" in act and flagged == 0) or not inv_in_packet else "PASS",
           {"active_decisions_in_packet": act, "contradiction_flags_in_deterministic_block": flagged, "hard_invariants_in_packet": inv_in_packet, "policy_layer_in_packet": policy_in_packet, "packet_top_level_keys": sorted(c["deterministic_authority"].keys())}, severity="MEDIUM")

@scenario
def HV16_emergency_freeze_honoured_by_adopt_and_upstream():
    root = fixture("migration", "hv16"); planner = Gov(root, "S-planner")
    for s in ["baseline", "inventory", "classify", "map", "plan", "test-design"]: planner.ok("adopt", s)
    planner.with_session("S-rev").with_role("migration-reviewer").ok("adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED")
    ex_ = planner.with_session("S-exec").with_role("migration-executor")
    ex_.ok("adopt", "migrate", "--batch", "0", "--name", "libcore", "--alias", "fx-mig")
    ex_.ok("freeze-writes", "--reason", "incident")
    code, e = ex_.try_("adopt", "migrate", "--batch", "1"); b1 = e.get("ok") or e["error"]["code"]
    code, e = ex_.try_("adopt", "migrate", "--batch", "2"); b2 = e.get("ok") or e["error"]["code"]
    moved = ex(root, "spec/requirements/api-spec.md")
    # upstream submit under freeze (greenfield with a FRAMEWORK lesson)
    root2 = fixture("greenfield", "hv16b"); g2 = Gov(root2); g2.ok("init", "--name", "hv16b", "--alias", "hv16b-alias")
    shutil.copy(os.path.join(CANON, "fixtures/upstream-learning/lessons/L-0001.yaml"), os.path.join(root2, "spec/lessons/L-0001.yaml"))
    inbox = os.path.join(WORK, "hv16-inbox", "lessons", "inbox"); os.makedirs(inbox)
    g2.ok("upstream", "prepare", "L-0001"); g2.ok("freeze-writes", "--reason", "incident")
    code, e = g2.try_("upstream", "submit", "PKT-0001", "--destination", inbox, "--approved-by", "owner"); sub = e.get("ok") or e["error"]["code"]
    record("HV-16", "FREEZE_WRITES is honoured by migration batches and upstream submission (framework 74: every mutating operation)", "FAIL" if b1 is True or sub is True else "PASS",
           {"adopt_migrate_batch1_under_freeze": b1, "adopt_migrate_batch2_under_freeze": b2, "files_moved_under_freeze": moved, "upstream_submit_under_freeze": sub, "note": "adopt.rs and upstream.rs never call guard_write"}, severity="MEDIUM" if (b1 is True or sub is True) else None)

@scenario
def HV17_secret_written_through_cit_append_record():
    root = fixture("greenfield", "hv17"); g = Gov(root)
    g.ok("init", "--name", "hv17", "--alias", "hv17-alias")
    mf = os.path.join(root, ".governance-runtime/m.json"); open(mf, "w").write(json.dumps([{"op": "append_record", "record": {"id": "D-0009", "type": "decision", "title": "gateway key", "status": "ACTIVE", "question": "?", "chosen_option": "A", "rationale": "use AWS key AKIAIOSFODNN7EXAMPLE for the gateway"}}]))
    c = g.ok("cit", "propose", "--proposal", "record gateway credential", "--trigger", "editorial", "--manifest", mf); cid = c["id"]
    g.ok("cit", "simulate", cid); g.ok("cit", "approve", cid, "--by", "agent", "--method", "auto")
    code, e = g.try_("cit", "execute", cid); st = e["result"]["cit_status"] if e.get("ok") else e["error"]["code"]
    on_disk = ex(root, "spec/decisions/D-0009.yaml") and "AKIA" in rd(root, "spec/decisions/D-0009.yaml")
    ok11, msg11, verdict = doctor(g, "D011")
    con = db(root); leak = con.execute("SELECT COUNT(*) FROM chunks WHERE text LIKE '%AKIAIOSFODNN7%'").fetchone()[0]; con.close()
    record("HV-17", "CIT-E verification blocks committing a governed record that contains a secret pattern (write-side gate, not only index-side)", "FAIL" if st == "COMMITTED" else "PASS",
           {"cit_status": st, "secret_record_on_disk": on_disk, "doctor_D011_after": (ok11, msg11, verdict), "secret_in_index_chunks": leak, "policy": "SECURITY_POLICY.on_secret_outside_secret_class=block_index_and_report (index-side only)"}, severity="MEDIUM" if st == "COMMITTED" else None)

@scenario
def HV18_intent_routing_sanity():
    root = fixture("greenfield", "hv18"); g = Gov(root); g.ok("init", "--name", "hv18", "--alias", "hv18-alias")
    a = g.ok("intent", "Discover whether adding capability X is worthwhile and tell me the impact")
    c = g.ok("cit", "propose", "--proposal", "add capability X", "--trigger", "behaviour_change"); g.ok("cit", "simulate", c["id"])
    b = g.ok("intent", "Approve it.")
    d = g.ok("intent", "Please roll back the last change")
    e_ = g.ok("intent", "what is the weather")
    record("HV-18", "natural-language intent routing (T0 deterministic patterns) compiles to governance operations", "PASS" if a["intent"] == "DISCOVER" and b["intent"] == "APPROVE" and b["pending_cit"] == c["id"] and d["intent"] == "ROLLBACK" and e_["intent"] == "UNKNOWN" else "FAIL",
           {"discover": a["intent"], "approve": (b["intent"], b["pending_cit"], b["commands"]), "rollback": d["intent"], "unknown": e_["intent"]}, severity="LOW")

@scenario
def HV19_checkpoint_before_handoff():
    root = fixture("greenfield", "hv19"); g = Gov(root); g.ok("init", "--name", "hv19", "--alias", "hv19-alias")
    t = g.ok("task", "create", "--class", "implementation", "--objective", "impl", "--status", "READY", "--allowed", "src/**")
    before = g.ok("checkpoint", "latest"); h = g.ok("handoff", "create", "--to-role", "backend-engineer", "--task", t["id"]); after = g.ok("checkpoint", "latest")
    made = (after or {}).get("id") != (before or {}).get("id")
    record("HV-19", "CHECKPOINT_POLICY mandatory trigger before_handoff is honoured automatically by handoff create", "PASS" if made else "FAIL",
           {"checkpoint_before": (before or {}).get("id"), "checkpoint_after_handoff": (after or {}).get("id"), "handoff": h["id"]}, severity="LOW")

@scenario
def HV20_empty_heldout_is_green():
    root = fixture("greenfield", "hv20"); g = Gov(root); r = g.ok("init", "--name", "hv20", "--alias", "hv20-alias")
    held = ry(root, "governance/tests/memory/heldout.yaml"); v = g.ok("memory", "verify")
    code, e = g.run("audit", "--no-persist"); au = e["result"] if e.get("ok") else e["error"]["details"]
    fam = au["families"]["memory_retrieval_regression"]
    record("HV-20", "governance suite is green while memory recall is unmeasured (0 held-out queries) - framework 17 says that is not healthy", "FAIL" if held["queries"] == [] and v["pass"] and fam["ok"] else "PASS",
           {"heldout_queries": len(held["queries"]), "memory_verify_pass": v["pass"], "family_ok": fam["ok"], "conformance_verdict_at_init": r["conformance"]["verdict"]}, severity="MEDIUM")

@scenario
def HV21_namespace_role_filter_in_retrieval():
    root = fixture("greenfield", "hv21"); g = Gov(root); g.ok("init", "--name", "hv21", "--alias", "hv21-alias")
    q = g.with_role("research-agent").ok("memory", "query", "Ledger append order total_cents", "--k", "5")
    prod = [h["path"] for h in q["hits"] if h["path"].startswith("src/") or h["path"].startswith("tests/")]
    record("HV-21", "retrieval applies MEMORY_POLICY.namespaces roles (product namespace roles=[engineering]) as an authority+namespace filter", "FAIL" if prod else "PASS",
           {"role": "research-agent", "product_namespace_hits": prod, "policy": "namespaces.product.roles=[engineering]"}, severity="LOW")

@scenario
def HV22_dag_expresses_research_to_validation_chain():
    root = fixture("greenfield", "hv22"); g = Gov(root); g.ok("init", "--name", "hv22", "--alias", "hv22-alias")
    chain = ["research", "experiment", "decision-preparation", "specification", "data", "specification", "test-design", "architecture", "implementation", "integration", "validation"]
    prev = None; ids = []
    for i, cls in enumerate(chain):
        args = ["task", "create", "--class", cls, "--objective", f"step {i} {cls}", "--status", "READY"]
        if prev: args += ["--deps", prev]
        t = g.ok(*args); prev = t["id"]; ids.append(prev)
    dag = g.ok("task", "dag"); rp = g.ok("task", "replan")
    record("HV-22", "one dependency-aware DAG expresses research -> experiment -> decision -> scenario -> dataset -> criteria -> test design -> architecture -> implementation -> integration -> validation", "PASS" if len(dag["longest_chain"]) == len(chain) and rp["runnable"] == [ids[0]] else "FAIL",
           {"longest_chain_len": len(dag["longest_chain"]), "runnable_after_replan": rp["runnable"], "blocked": dag["counts"]["blocked"], "cycles": dag["cycles"]}, severity="LOW")

@scenario
def HV23_calls_edges_and_code_intel_plugin():
    root = fixture("migration", "hv23"); g = Gov(root); g.ok("init", "--name", "hv23", "--alias", "hv23-alias", "--skip-index")
    wy(root, "governance/project/plugins/pyast.yaml", {"plugin_id": "python-ast", "capability": "code_intel", "version": "1.0.0", "command": ["python3", "-m", "govos_capabilities.code_intel_python_ast"], "languages": ["python"], "cwd": None})
    env = Gov(root).with_env("PYTHONPATH", os.path.join(CANON, "capabilities/python"))
    r = env.ok("rebuild-memory")
    con = db(root); prov = con.execute("SELECT DISTINCT provider FROM symbols WHERE language='python'").fetchall(); calls = con.execute("SELECT COUNT(*) FROM symbol_refs WHERE kind='call'").fetchone()[0]; edges = dict(con.execute("SELECT type, COUNT(*) FROM edges GROUP BY type").fetchall()); con.close()
    q = env.ok("memory", "query", "slugify", "--route", "symbol", "--k", "5")
    record("HV-23", "code-intelligence plugin (python-ast) is used and CALLS relationships reach the graph (framework 11.2 CALLS edge type)", "FAIL" if edges.get("CALLS", 0) == 0 else "PASS",
           {"symbol_providers": prov, "call_refs_in_symbol_refs": calls, "edge_type_counts": edges, "degradations": r["degradations"], "symbol_route_hits": [(h["artifact_id"], h["section"]) for h in q["hits"]]}, severity="LOW")

@scenario
def HV24_binary_portability_kernel_source():
    out = subprocess.run(["strings", GOV], capture_output=True, text=True).stdout
    baked = [l for l in out.splitlines() if "Dynamic-Agentic-Engineering-OS" in l][:2]
    tmp = os.path.join(WORK, "hv24"); os.makedirs(tmp); wr(tmp, "README.md", "x\n"); git_init(tmp)
    env = dict(os.environ); env.pop("GOV_CANONICAL_ROOT", None); env["GOV_CANONICAL_ROOT"] = "/nonexistent/path"
    p = subprocess.run([GOV, "--json", "--root", tmp, "init", "--name", "p", "--alias", "p-alias", "--skip-index"], capture_output=True, text=True, env=env)
    e = json.loads(p.stdout or "{}") if p.stdout.strip() else {}
    record("HV-24", "portable gov executable: kernel payload obtainable without the build machine's source checkout (D-0002: self-contained executable per OS)", "FAIL" if baked and e.get("ok") else "PASS",
           {"build_path_baked_into_binary": bool(baked), "init_with_bogus_GOV_CANONICAL_ROOT_succeeded_via_baked_path": e.get("ok"), "lock_source": ry(tmp, "governance/framework.lock")["source"] if e.get("ok") else None, "note": "kernel is not embedded in the binary; on another machine gov init needs --source; framework.lock records an absolute machine path"}, severity="MEDIUM")

@scenario
def HV25_no_python_needed_for_core():
    root = fixture("greenfield", "hv25"); bindir = os.path.join(WORK, "hv25-bin"); os.makedirs(bindir)
    os.symlink(shutil.which("git"), os.path.join(bindir, "git"))
    env = {"PATH": bindir, "HOME": os.environ.get("HOME", "/tmp"), "GOV_CANONICAL_ROOT": CANON, "GOV_DISABLE_PLUGINS": "1"}
    def run(*a):
        p = subprocess.run([GOV, "--json", "--root", root, "--session", "S-nopy"] + list(a), capture_output=True, text=True, env=env); return json.loads(p.stdout.strip())
    r = run("init", "--name", "hv25", "--alias", "hv25-alias"); s = run("status"); c = run("continue"); a = run("audit", "--no-persist"); d = run("doctor")
    dv = (d["result"] if d.get("ok") else d["error"]["details"])["verdict"]
    record("HV-25", "deterministic core runs status/continue/audit/doctor with only git on PATH (no Python, no cargo)", "PASS" if r.get("ok") and s.get("ok") and c.get("ok") else "FAIL",
           {"init": r.get("ok"), "status": s.get("ok"), "continue": c.get("ok"), "audit": (a["result"] if a.get("ok") else a["error"]["details"])["verdict"], "doctor": dv, "linked_libs": subprocess.run(["ldd", GOV], capture_output=True, text=True).stdout.count("python")}, severity=None)

@scenario
def HV26_export_gate_unscanned_fields():
    root = fixture("greenfield", "hv26"); g = Gov(root); g.ok("init", "--name", "shipping-quotes", "--alias", "proj-z")
    ds = ry(root, "governance/project/DATA_SENSITIVITY.yaml"); ds["identifiers_to_strip"] = ["Acme Freight Ltd"]; wy(root, "governance/project/DATA_SENSITIVITY.yaml", ds)
    L = yaml.safe_load(open(os.path.join(CANON, "fixtures/upstream-learning/lessons/L-0001.yaml")))
    L["id"] = "L-0010"; L["title"] = "Acme Freight Ltd lost data"; L["category"] = "acme-freight-ltd-outage"; L["tags"] = ["Acme Freight Ltd"]
    wy(root, "spec/lessons/L-0010.yaml", L)
    p = g.ok("upstream", "prepare", "L-0010"); txt = open(p["path"]).read().lower()
    leaks = [w for w in ["acme"] if w in txt]
    record("HV-26", "upstream packet sanitises every emitted field (category/title/tags carry identifiers?)", "FAIL" if leaks else "PASS",
           {"identifier_leaks_in_packet": leaks, "identifiers_redacted": p["scans"]["identifiers_redacted"], "packet_category": yaml.safe_load(open(p["path"]))["category"]}, severity="MEDIUM" if leaks else None)

@scenario
def HV27_generated_artifacts_validate_against_kernel_schemas():
    import jsonschema
    root = fixture("greenfield", "hv27"); g = Gov(root); g.ok("init", "--name", "hv27", "--alias", "hv27-alias", "--intent", "ledger")
    wy(root, "spec/features/F-0001.yaml", {"id": "F-0001", "type": "feature", "title": "Totals", "status": "ACTIVE", "readiness": readiness_all_present()})
    t = g.ok("task", "create", "--class", "implementation", "--objective", "impl", "--feature", "F-0001", "--status", "READY", "--allowed", "src/**"); g.ok("rebuild-memory")
    ctx = g.ok("context", "compile", t["id"]); g.ok("checkpoint", "create", "--next-action", "gov continue"); g.ok("audit")
    sd = os.path.join(root, "governance/kernel/schemas")
    def val(schema, data):
        s = json.load(open(os.path.join(sd, schema + ".schema.json"))); v = jsonschema.Draft202012Validator(s); return [f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message[:120]}" for e in v.iter_errors(data)]
    problems = {}
    for name, schema in [("governance/generated/index-manifest.json", "index-manifest"), ("governance/generated/memory-manifest.json", "memory-manifest"), ("governance/generated/adapter-manifest.json", "adapter-manifest"), ("governance/generated/tool-registry.json", "tool-registry"), ("governance/kernel/KERNEL_MANIFEST.json", "kernel-manifest")]:
        errs = val(schema, rj(root, name));
        if errs: problems[name] = errs
    for name, schema in [("governance/framework.lock", "framework-lock"), ("governance/tests/memory/heldout.yaml", "heldout-tests"), ("spec/audits/GOVERNANCE-ADOPTION/00-BASELINE.yaml", "adoption-baseline")]:
        if ex(root, name):
            errs = val(schema, ry(root, name))
            if errs: problems[name] = errs
    errs = val("context-packet", ctx)
    if errs: problems["context-packet"] = errs
    for dp, dn, fn in os.walk(os.path.join(root, "spec")):
        for f in fn:
            if not f.endswith(".yaml"): continue
            data = yaml.load(open(os.path.join(dp, f)), Loader=_L)
            if not isinstance(data, dict) or "type" not in data: continue
            schema = data["type"] if os.path.exists(os.path.join(sd, data["type"] + ".schema.json")) else "record"
            errs = val(schema, data)
            if errs: problems[os.path.relpath(os.path.join(dp, f), root)] = errs
    record("HV-27", "every generated artefact/record of a fresh project validates against the installed kernel schemas (draft 2020-12, independent validator)", "PASS" if not problems else "FAIL", {"violations": problems}, severity="MEDIUM" if problems else None)

@scenario
def HV28_audit_leaves_index_stale():
    root = fixture("greenfield", "hv28"); g = Gov(root); g.ok("init", "--name", "hv28", "--alias", "hv28-alias")
    ok_before, _, _ = doctor(g, "D010"); g.ok("audit"); ok_after, msg, verdict = doctor(g, "D010")
    record("HV-28", "running gov audit (which writes an audit record) leaves the index fresh", "PASS" if ok_after else "FAIL", {"D010_before": ok_before, "D010_after_audit": ok_after, "message": msg, "doctor_verdict": verdict}, severity="LOW")

@scenario
def HV29_destructive_migration_batch_gate_answer_is_a_flag():
    root, planner, executor = run_brownfield_adoption("hv29")
    cat = [json.loads(l) for l in rd(root, "spec/audits/GOVERNANCE-ADOPTION/04-TARGET-PATH-MAP.jsonl").splitlines()]
    dead = next(e for e in cat if e["current_path"] == "src/app/old_export.py")
    gates_before = executor.ok("gate", "list")
    r = executor.ok("adopt", "migrate", "--batch", "7", "--gate-answer", dead["artifact_id"])
    gone = not ex(root, "src/app/old_export.py")
    record("HV-29", "destructive migration batch requires an answered, presented Human Decision Gate record (not a CLI flag naming the artefact)", "FAIL" if gone and not gates_before else "PASS",
           {"human_gate_records_before": [x["id"] for x in gates_before], "dead_code_deleted_with_flag_only": gone, "batch_result": r["batches"][0].get("applied")}, severity="HIGH" if gone and not gates_before else None)

@scenario
def HV30_multi_machine_after_brownfield_adoption():
    root, planner, executor = run_brownfield_adoption("hv30")
    executor.ok("adopt", "audit"); executor.ok("rebuild-memory"); commit(root, "adopted")
    ma = rj(root, "governance/generated/index-manifest.json")["manifest_hash"]; sa = executor.with_session("S-A").ok("status")
    b = os.path.join(WORK, "hv30-B"); subprocess.run(["git", "clone", "-q", root, b], check=True)
    gb = Gov(b, "S-B"); rb = gb.ok("rebuild-memory"); sb = gb.ok("status")
    same = rb["manifest_hash"] == ma and sa["tasks"]["counts"] == sb["tasks"]["counts"]
    record("HV-30", "multi-machine rebuild after a full brownfield adoption (mixed Python/TypeScript, archived stores, extracted records) is reproducible", "PASS" if same else "FAIL",
           {"manifest_A": ma, "manifest_B": rb["manifest_hash"], "counts_A": sa["tasks"]["counts"], "counts_B": sb["tasks"]["counts"], "next_action_B": sb["next_action"], "excluded_B": rb["excluded"][:6]}, severity=None if same else "HIGH")

@scenario
def HV31_typescript_import_rewrite_on_migration():
    root = fixture("migration", "hv31")
    wr(root, "docs/extra.ts", "export function extra(): string { return 'x'; }\n")
    wr(root, "web/src/util/http.ts", "import { extra } from '../../../docs/extra';\nexport async function get(url: string): Promise<string> { return `GET ${url} ${extra()}`; }\n")
    commit(root, "ts under docs"); planner = Gov(root, "S-planner")
    for s in ["baseline", "inventory", "classify", "map", "plan", "test-design"]: planner.ok("adopt", s)
    cat = [json.loads(l) for l in rd(root, "spec/audits/GOVERNANCE-ADOPTION/04-TARGET-PATH-MAP.jsonl").splitlines()]
    e = next(x for x in cat if x["current_path"] == "docs/extra.ts")
    planner.with_session("S-rev").with_role("migration-reviewer").ok("adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED")
    ex_ = planner.with_session("S-exec").with_role("migration-executor")
    ex_.ok("adopt", "migrate", "--batch", "0", "--name", "libcore", "--alias", "fx-mig")
    for b in ["1", "2"]: ex_.ok("adopt", "migrate", "--batch", b)
    r = ex_.ok("adopt", "migrate", "--batch", "3", "--gate-answer", e["artifact_id"])
    http = rd(root, "web/src/util/http.ts")
    target = e.get("target_path"); moved = target and ex(root, target)
    rewritten = ("docs/extra" not in http) and ("product/extra" in http or "../product/extra" in http)
    record("HV-31", "TypeScript relative import is rewritten when the imported file is relocated by the migration executor", "PASS" if moved and rewritten else "FAIL",
           {"catalogue_entry": {k: e[k] for k in ["class" if "class" in e else "current_class", "action", "target_path", "batch", "requires_human_gate"]}, "moved": moved, "http_ts_after": http.splitlines()[0], "import_rewritten": rewritten}, severity="MEDIUM" if not (moved and rewritten) else None)

@scenario
def HV32_worker_return_promoted_to_state_and_task_close_requires_report():
    root = fixture("greenfield", "hv32"); g = Gov(root); g.ok("init", "--name", "hv32", "--alias", "hv32-alias")
    t = g.ok("task", "create", "--class", "implementation", "--objective", "impl", "--status", "READY", "--allowed", "src/**"); tid = t["id"]
    h = g.ok("handoff", "create", "--to-role", "backend-engineer", "--task", tid)
    ret = os.path.join(root, ".governance-runtime/ret.json"); open(ret, "w").write(json.dumps({"task": tid, "status": "success", "work_completed": "did it", "files_changed": ["src/lib.rs"], "evidence": [], "tests": {"status": "passed"}, "discoveries": ["found a thing"], "risks": [], "lessons": ["lesson text"], "proposed_decisions": [], "unresolved": [], "recommended_next_action": "close"}))
    r = g.ok("handoff", "return", h["id"], "--file", ret)
    rec = ry(root, f"spec/planning/{h['id']}.yaml")
    record("HV-32", "typed worker return is durably promoted into project state (handoff record carries the return; discoveries/lessons are persisted)", "PASS" if rec.get("return", {}).get("discoveries") == ["found a thing"] else "FAIL", {"handoff_status": rec.get("handoff_status"), "return_persisted": bool(rec.get("return")), "lessons_became_records": any(f.startswith("L-") for f in os.listdir(os.path.join(root, "spec/lessons")))}, severity="LOW")

# ----------------------------------------------------------------------------------------------- refinements / additions
@scenario
def HV01_embedder_replaceable_at_query_time():
    """Decisive form: a plugin embedder = reference hashed-ngram with the vector REVERSED. If the core embeds the query with the
    pinned plugin, an exact-title query ranks its own record first (cosine 1.0). If the core embeds the query with the builtin
    (unreversed) embedder, the ranking equals cosine(builtin(q), stored) which we replicate offline."""
    root = fixture("greenfield", "hv01b"); g = Gov(root)
    g.ok("init", "--name", "hv01", "--alias", "hv01-alias", "--skip-index")
    plug = os.path.join(root, "rev_embed.py")
    wr(root, "rev_embed.py", "import sys, json\nsys.path.insert(0, %r)\nfrom govos_capabilities.embedder_hashed_ngram import HashedNgramEmbedder\nreq = json.loads(sys.stdin.read())\ndim = int(req['inputs'].get('dimensions', 64))\ne = HashedNgramEmbedder(dim=dim, version='1')\nvecs = [list(reversed(e.embed(t))) for t in req['inputs']['texts']]\nprint(json.dumps({'protocol': 'gov-capability/1', 'ok': True, 'provider': {'id': 'reversed-hashed-ngram', 'version': '1'}, 'outputs': {'vectors': vecs, 'dim': dim}}))\n" % os.path.join(CANON, "capabilities/python"))
    wy(root, "governance/project/plugins/rev.yaml", {"plugin_id": "reversed-hashed-ngram", "capability": "embed", "version": "1", "command": ["python3", plug], "languages": []})
    pp = ry(root, "governance/project/PROJECT_POLICY.yaml"); pp["policy_overrides"] = {"MEMORY_POLICY.embedding.provider": "reversed-hashed-ngram", "MEMORY_POLICY.embedding.dimensions": 8}; wy(root, "governance/project/PROJECT_POLICY.yaml", pp)
    titles = ["Order totals are exact integer cents", "Ledger rejects duplicate order identifiers", "Clerk appends two orders and reads the total", "Gateway retries are capped at five attempts"]
    for i, t in enumerate(titles, 1):
        wy(root, f"spec/requirements/REQ-{i:04d}.yaml", {"id": f"REQ-{i:04d}", "type": "requirement", "title": t, "status": "ACTIVE", "kind": "functional", "acceptance_criteria": [t + " and nothing else matters here"]})
    r = g.ok("rebuild-memory"); m = rj(root, "governance/generated/index-manifest.json")
    con = db(root); rows = con.execute("SELECT chunk_id, artifact_id, vec FROM vectors").fetchall(); con.close()
    e = HashedNgramEmbedder(dim=8, version="1")
    outcomes = []
    for i, q in enumerate(titles, 1):
        res = g.ok("memory", "query", q, "--route", "semantic", "--k", "8")
        gov_rank = [h["artifact_id"] for h in res["hits"]]
        builtin_q = e.embed(q); plugin_q = list(reversed(builtin_q))
        rank_builtin = [aid for s_, cid, aid in sorted(((cosine(builtin_q, json.loads(v)), cid, aid) for cid, aid, v in rows), key=lambda x: (-x[0], x[1])) if s_ > 0]
        rank_plugin = [aid for s_, cid, aid in sorted(((cosine(plugin_q, json.loads(v)), cid, aid) for cid, aid, v in rows), key=lambda x: (-x[0], x[1])) if s_ > 0]
        def dedup(l):
            o = []; [o.append(x) for x in l if x not in o]; return o
        outcomes.append({"query": q, "expected": f"REQ-{i:04d}", "gov_top": dedup(gov_rank)[:3], "if_query_used_builtin": dedup(rank_builtin)[:3], "if_query_used_pinned_plugin": dedup(rank_plugin)[:3],
                         "gov_matches_builtin": dedup(gov_rank)[:3] == dedup(rank_builtin)[:3], "gov_matches_plugin": dedup(gov_rank)[:3] == dedup(rank_plugin)[:3], "expected_first_in_gov": (dedup(gov_rank)[:1] == [f"REQ-{i:04d}"])})
    used_builtin = all(o["gov_matches_builtin"] for o in outcomes) and not all(o["gov_matches_plugin"] for o in outcomes)
    record("HV-01", "embedding model replaceable at query time: index built by the pinned plugin, query embedded with the same model?", "FAIL" if used_builtin else "PASS",
           {"manifest_embedder": m["embedder"], "exact_title_queries_rank_own_record_first": sum(o["expected_first_in_gov"] for o in outcomes), "of": len(outcomes), "outcomes": outcomes,
            "conclusion": "the core embeds every query with the built-in hashed-ngram embedder (retrieval/mod.rs:108) regardless of the pinned plugin; semantic retrieval compares two different vector spaces" if used_builtin else "query embedded with pinned embedder"}, severity="CRITICAL" if used_builtin else None)

@scenario
def HV07_embedder_pin_change_invalidates_index():
    root = fixture("greenfield", "hv07b"); g = Gov(root)
    g.ok("init", "--name", "hv07", "--alias", "hv07-alias")
    pp = ry(root, "governance/project/PROJECT_POLICY.yaml"); pp["policy_overrides"] = {"MEMORY_POLICY.embedding.dimensions": 64, "MEMORY_POLICY.embedding.version": "2"}; wy(root, "governance/project/PROJECT_POLICY.yaml", pp)
    fr = g.ok("memory", "freshness")
    r = g.ok("rebuild-memory", "--incremental")
    m2 = rj(root, "governance/generated/index-manifest.json")["embedder"]
    con = db(root); dims = con.execute("SELECT dim, COUNT(*) FROM vectors GROUP BY dim").fetchall(); con.close()
    fr2 = g.ok("memory", "freshness"); ok10, msg10, dv = doctor(g, "D010"); ok12, msg12, _ = doctor(g, "D012")
    code, e = g.run("audit", "--no-persist"); au = e["result"] if e.get("ok") else e["error"]["details"]
    q = g.ok("memory", "query", "orders ledger total cents", "--route", "semantic", "--k", "5")
    mixed = len(dims) > 1
    record("HV-07", "an embedder pin change (version/dimensions) forces a full re-index; incremental rebuild must not leave a mixed-embedder index that the manifest misreports", "FAIL" if mixed else "PASS",
           {"stale_only_because_overlay_file_changed": [x for x in fr["stale"]], "manifest_embedder_after_incremental": m2, "vector_dims_in_db": dims, "fresh_after": fr2["fresh"], "doctor_D010": (ok10, msg10), "doctor_D012": ok12, "audit_verdict": au["verdict"], "audit_recovery_rebuild_family": au["families"]["recovery_rebuild"], "semantic_query_hits": len(q["hits"])}, severity="HIGH" if mixed else None)

@scenario
def HV33_symbol_route_bare_identifier():
    root = fixture("brownfield", "hv33"); g = Gov(root); g.ok("init", "--name", "hv33", "--alias", "hv33-alias")
    con = db(root); syms = con.execute("SELECT COUNT(*) FROM symbols WHERE name='with_retry'").fetchone()[0]; con.close()
    a = g.ok("memory", "query", "with_retry", "--route", "symbol", "--k", "5"); b = g.ok("memory", "query", "with_retry", "--k", "5"); c = g.ok("memory", "query", "def with_retry", "--route", "symbol", "--k", "5")
    record("HV-33", "symbol route resolves a bare identifier query (the common form of a code-symbol question)", "PASS" if a["hits"] else "FAIL",
           {"symbols_named_with_retry": syms, "explicit_symbol_route_hits": [h["artifact_id"] for h in a["hits"]], "auto_routes_for_bare_identifier": b["routes"], "auto_hits": [h["artifact_id"] for h in b["hits"]][:3], "def_prefixed_symbol_route_hits": [h["artifact_id"] for h in c["hits"]]}, severity="MEDIUM" if not a["hits"] else None)

@scenario
def HV34_cit_propose_stores_unscanned_content():
    root = fixture("greenfield", "hv34"); g = Gov(root); g.ok("init", "--name", "hv34", "--alias", "hv34-alias")
    mf = os.path.join(root, ".governance-runtime/m.json"); open(mf, "w").write(json.dumps([{"op": "write_file", "path": "src/keys.rs", "content": "pub const K: &str = \"AKIAIOSFODNN7EXAMPLE\";\n"}]))
    c = g.ok("cit", "propose", "--proposal", "add key", "--trigger", "editorial", "--manifest", mf)
    on_disk = "AKIAIOSFODNN7EXAMPLE" in rd(root, f"spec/decisions/{c['id']}.yaml")
    ok11, msg11, dv = doctor(g, "D011")
    record("HV-34", "cit propose scans the proposal/mutation manifest before persisting it as a governed record (secret lands in spec/decisions/CIT-*.yaml otherwise)", "FAIL" if on_disk else "PASS",
           {"secret_in_cit_record_on_disk": on_disk, "doctor_D011": (ok11, msg11, dv)}, severity="MEDIUM" if on_disk else None)

@scenario
def HV35_heldout_file_indexed_leaks_into_results():
    root = fixture("greenfield", "hv35"); g = Gov(root); g.ok("init", "--name", "hv35", "--alias", "hv35-alias")
    wy(root, "spec/decisions/D-0001.yaml", {"id": "D-0001", "type": "decision", "title": "Use integer cents", "status": "ACTIVE", "question": "money type?", "chosen_option": "A", "rationale": "no floating point", "human_approved": True})
    wy(root, "governance/tests/memory/heldout.yaml", {"version": "1", "queries": [{"id": "HQ-001", "query": "Use integer cents", "expected_refs": ["D-0001"], "forbidden": [], "k": 3}]})
    g.ok("rebuild-memory"); q = g.ok("memory", "query", "Use integer cents", "--k", "3")
    hits = [h["artifact_id"] for h in q["hits"]]
    record("HV-35", "the held-out regression file is not itself indexed (test-set leakage into the retrieval index)", "FAIL" if "file:governance/tests/memory/heldout.yaml" in hits else "PASS", {"hits": hits}, severity="LOW")

@scenario
def HV39_implementation_task_requires_scenarios_and_tests():
    root = fixture("greenfield", "hv39"); g = Gov(root); g.ok("init", "--name", "hv39", "--alias", "hv39-alias")
    t = g.ok("task", "create", "--class", "implementation", "--objective", "ship feature without any scenario or acceptance test", "--status", "READY", "--allowed", "src/**")
    rp = g.ok("task", "replan"); c = g.ok("continue")
    record("HV-39", "TEST_POLICY.implementation_task_requires [scenarios_present, acceptance_tests_declared] gates implementation tasks that have no feature (readiness gating only applies via a feature)", "FAIL" if c.get("task") == t["id"] else "PASS",
           {"runnable": rp["runnable"], "continue_picked": c.get("task"), "policy_key_read_by_core": "implementation_task_requires grep=0"}, severity="MEDIUM" if c.get("task") == t["id"] else None)


@scenario
def HV36_plugin_host_deadlocks_on_large_response():
    root = fixture("greenfield", "hv36"); g = Gov(root); g.ok("init", "--name", "hv36", "--alias", "hv36-alias", "--skip-index")
    plug = os.path.join(root, "big.py")
    wr(root, "big.py", "import sys, json\nreq = json.loads(sys.stdin.read())\nn = int(req['inputs'].get('n', 1))\nvecs = [[0.123456]*512 for _ in range(n)]\nsys.stdout.write(json.dumps({'protocol': 'gov-capability/1', 'ok': True, 'provider': {'id': 'big', 'version': '1'}, 'outputs': {'vectors': vecs, 'dim': 512}}))\n")
    wy(root, "governance/project/plugins/big.yaml", {"plugin_id": "big", "capability": "embed", "version": "1", "command": ["python3", plug], "languages": []})
    t0 = time.time(); code, e = g.run("capabilities", "invoke", "--plugin", "big", "--inputs", '{"n": 4}'); small = (time.time() - t0, e.get("ok") or e["error"]["code"])   # ~ 20 KB response
    t0 = time.time(); code, e = g.run("capabilities", "invoke", "--plugin", "big", "--inputs", '{"n": 64}'); big = (time.time() - t0, e.get("ok") or e["error"]["code"])     # ~ 300 KB response (> 64 KiB pipe buffer)
    record("HV-36", "capability plugin host (API-0001) handles responses larger than the OS pipe buffer (a 512-dim embedder answering a 256-text batch produces ~1 MB)", "FAIL" if big[1] != True else "PASS",
           {"small_response_20KB": {"seconds": round(small[0], 1), "result": small[1]}, "large_response_300KB": {"seconds": round(big[0], 1), "result": big[1]}, "cause": "runtime/src/capabilities/host.rs polls child.try_wait() until exit before reading stdout; the child blocks on a full pipe -> deadlock until PLUGIN_TIMEOUT"}, severity="CRITICAL" if big[1] != True else None)

if __name__ == "__main__":
    only = sys.argv[1:]
    for name, fn in list(globals().items()):
        if name.startswith("HV") and callable(fn) and (not only or any(name.startswith(o) for o in only)):
            t0 = time.time(); fn(); print(f"   ({time.time()-t0:.1f}s)")
    json.dump({"work_dir": WORK, "results": RESULTS}, open(os.path.join(OUT_DIR, "results.json" if not only else "results-rerun.json"), "w"), indent=2)
    print("\nWORK:", WORK)
    print("SUMMARY:", {v: sum(1 for r in RESULTS if r["verdict"] == v) for v in ["PASS", "FAIL", "INFO", "ERROR"]})

