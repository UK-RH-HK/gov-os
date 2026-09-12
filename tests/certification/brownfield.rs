//! Fixture 2 — deliberately dirty brownfield adoption A0→A11 with independence gates, legacy retirement, secret
//! isolation, contradiction resolution through CIT and an audited remediation iteration.
use crate::common::*;
use serde_json::json;

fn build_chat_sqlite(root: &std::path::Path) {
    let sql = read(root, "memory/chat_history.sql");
    let db = gov_runtime::memory::db::RuntimeDb::open(&root.join("memory/chat_history.sqlite")).unwrap();
    db.conn.execute_batch(&format!("PRAGMA journal_mode=DELETE; {sql}")).unwrap();
    drop(db);
    std::fs::remove_file(root.join("memory/chat_history.sql")).unwrap();
}

#[test]
fn brownfield_adoption_end_to_end() {
    let (root, planner) = setup_fixture("brownfield", "brownfield", "S-planner");
    build_chat_sqlite(&root);
    git_commit_all(&root, "with chat db");
    // A0
    let b = planner.ok(&["adopt", "baseline"]);
    assert_eq!(b["baseline_tests"], "failed", "stale test must fail at baseline: {b}");
    // A1/A2
    planner.ok(&["adopt", "inventory"]);
    let cls = planner.ok(&["adopt", "classify"]);
    assert!(cls["conflicting"].as_u64().unwrap() >= 1);
    let lines: Vec<serde_json::Value> = read(&root, "spec/audits/GOVERNANCE-ADOPTION/02-CLASSIFICATION.jsonl").lines().map(|l| serde_json::from_str(l).unwrap()).collect();
    let c = |p: &str| lines.iter().find(|x| x["path"] == p).unwrap_or_else(|| panic!("{p} missing")).clone();
    for p in [".cursorrules", "AGENT_RULES_v2.md", ".github/copilot-instructions.md"] { assert_eq!(c(p)["class"], "GOVERNANCE_LEGACY"); assert_eq!(c(p)["authority"], "LEGACY"); }
    assert_eq!(c("memory/chat_history.sqlite")["authority"], "LEGACY"); assert_eq!(c(".chat/sessions.jsonl")["authority"], "LEGACY");
    assert_eq!(c(".index/vectors.json")["class"], "GENERATED"); assert_eq!(c(".index/vectors.json")["authority"], "LEGACY");
    for p in [".env", "config/secrets.yaml", "src/app/config.py"] { assert_eq!(c(p)["class"], "SECRET", "{p}"); assert_eq!(c(p)["hash"], "<not-hashed:secret>"); }
    assert_eq!(c("spec/decisions/D-0001.yaml")["authority"], "UNKNOWN_OR_CONFLICTING", "superseded-but-ACTIVE must be flagged");
    assert_eq!(c("src/app/old_export.py")["class"], "DEAD_OR_UNUSED");
    assert_eq!(c("docs/legacy_module.py")["class"], "DEAD_OR_UNUSED");
    assert_eq!(c("src/specs/feature-login.md")["class"], "SPEC_AUTHORITATIVE"); assert!(c("src/specs/feature-login.md")["reasons"].to_string().contains("misplaced"));
    assert_eq!(c("docs/test_utils.py")["class"], "PRODUCT_TEST");
    assert_eq!(c("docs/old/decision-2-copy.yaml")["class"], "DECISION");
    assert!(read(&root, "spec/audits/GOVERNANCE-ADOPTION/03-LEGACY-GOVERNANCE-MAP.md").contains(".cursorrules"));
    // A3/A4/A5
    let map = planner.ok(&["adopt", "map"]);
    assert_eq!(map["unknown_blocking_destructive"], 0, "{map}");
    let cat: Vec<serde_json::Value> = read(&root, "spec/audits/GOVERNANCE-ADOPTION/04-TARGET-PATH-MAP.jsonl").lines().map(|l| serde_json::from_str(l).unwrap()).collect();
    let e = |p: &str| cat.iter().find(|x| x["current_path"] == p).unwrap().clone();
    assert_eq!(e(".env")["action"], "KEEP_IN_PLACE"); assert_eq!(e(".env")["index_policy"]["export"], "denied");
    assert_eq!(e(".cursorrules")["action"], "MOVE"); assert!(e(".cursorrules")["target_path"].as_str().unwrap().starts_with("archive/governance/legacy-rules/"));
    assert_eq!(e("memory/chat_history.sqlite")["action"], "EXTRACT");
    assert_eq!(e(".index/vectors.json")["action"], "DELETE_FROM_ACTIVE_TREE");
    assert_eq!(e("src/app/old_export.py")["action"], "DELETE_FROM_ACTIVE_TREE", "ARCHIVE_POLICY.unused_code_action=remove_from_active_tree drives the planned action"); assert_eq!(e("src/app/old_export.py")["requires_human_gate"], true);
    assert_eq!(e("docs/old/decision-2-copy.yaml")["action"], "MOVE"); assert_eq!(e("docs/old/decision-2-copy.yaml")["target_path"], "spec/decisions/decision-2-copy.yaml");
    assert_eq!(e("src/app/retry.py")["action"], "KEEP_IN_PLACE");
    planner.ok(&["adopt", "plan"]); planner.ok(&["adopt", "test-design"]);
    let reviewer = planner.with_session("S-reviewer").with_role("migration-reviewer");
    reviewer.ok(&["adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED"]);
    // A6: everything except the destructive dead-code batch (needs an answered human gate) — dead code is skipped
    let executor = planner.with_session("S-executor").with_role("migration-executor");
    let mig = executor.ok(&["adopt", "migrate", "--name", "shipping-quotes", "--alias", "fx-brown"]);
    assert_eq!(mig["complete"], true, "{mig}");
    for p in [".cursorrules", "AGENT_RULES_v2.md", ".github/copilot-instructions.md", ".index/vectors.json", ".index/manifest.json", "src/specs/feature-login.md", "docs/test_utils.py"] { assert!(!exists(&root, p), "{p} should have left the active tree"); }
    assert!(exists(&root, "archive/governance/legacy-rules/.cursorrules") || exists(&root, "archive/governance/legacy-rules/__.cursorrules") || std::fs::read_dir(root.join("archive/governance/legacy-rules")).unwrap().count() >= 3);
    assert!(exists(&root, "tests/test_utils.py"));
    assert!(exists(&root, "src/app/old_export.py"), "dead code must not be deleted without a human gate");
    assert!(exists(&root, ".env") && exists(&root, "config/secrets.yaml") && exists(&root, "src/app/config.py"), "secrets are never moved by automation");
    // destructive entries carry gate records; the executor (L3) relays the human's answers, then batch 7 executes
    let cat2: Vec<serde_json::Value> = read(&root, "spec/audits/GOVERNANCE-ADOPTION/04-TARGET-PATH-MAP.jsonl").lines().map(|l| serde_json::from_str(l).unwrap()).collect();
    let gates: Vec<String> = cat2.iter().filter(|e| e["requires_human_gate"] == true).map(|e| e["human_gate"].as_str().expect("gate record per destructive entry").to_string()).collect();
    assert!(gates.len() >= 2, "{gates:?}");
    for gid in &gates { executor.ok(&["gate", "present", gid]); executor.ok(&["decide", gid, "--option", "A", "--by", "owner"]); }
    executor.ok(&["adopt", "migrate", "--batch", "7"]);
    assert!(!exists(&root, "src/app/old_export.py") && !exists(&root, "docs/legacy_module.py"), "answered gates => dead code removed from the active tree");
    assert!(exists(&root, "spec/decisions/decision-2-copy.yaml"));
    assert!(exists(&root, "memory/chat_history.sqlite"), "memory stores are inspected/extracted in A8, not retired blindly in A6");
    // A7 independent verification
    let verifier = planner.with_session("S-verifier").with_role("migration-verifier");
    let v = verifier.ok(&["adopt", "verify-migration"]);
    assert_eq!(v["verdict"], "MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD", "{v}");
    assert!(v["legacy_in_active_tree"].as_array().unwrap().is_empty());
    assert_eq!(v["secrets_isolated"], true);
    // A8 legacy memory extraction: decisions/lessons from chat, secret string skipped, stores retired
    let ex = executor.ok(&["adopt", "extract-legacy"]);
    let stores = ex["stores"].as_array().unwrap();
    let chat = stores.iter().find(|s| s["path"].as_str().unwrap().ends_with("chat_history.sqlite")).expect("chat store inspected");
    assert!(chat["extracted"].as_u64().unwrap() >= 2 && chat["skipped_secret_strings"].as_u64().unwrap() >= 1, "{chat}");
    assert_eq!(chat["disposition"], "RETIRE");
    assert!(!exists(&root, "memory/chat_history.sqlite") && exists(&root, "archive/governance/memory-stores/chat_history.sqlite"));
    assert!(exists(&root, "archive/governance/LEG-0001.yaml"));
    let (ok, msg) = doctor_check(&executor, "D013"); assert!(ok, "legacy mechanisms must be retired/registered (INV-004): {msg}");
    let created: Vec<String> = ex["created_records"].as_array().unwrap().iter().map(|x| x.as_str().unwrap().to_string()).collect();
    assert!(created.iter().any(|p| p.starts_with("spec/decisions/D-C")));
    for p in &created { let t = read(&root, p); assert!(!t.contains("sk_live_CHAT"), "leaked chat secret in {p}"); assert!(t.contains("legacy_source"), "provenance required in {p}"); assert!(t.contains("PROVISIONAL") || t.contains("SUPERSEDED")); }
    // A9 memory on stable paths; secrets never indexed
    let m = executor.ok(&["adopt", "build-memory"]);
    assert!(m["excluded"].as_u64().unwrap() >= 3, "{m}");
    let paths = indexed_paths(&root);
    for s in [".env", "config/secrets.yaml", "src/app/config.py"] { assert!(!paths.contains(&s.to_string()), "{s} indexed!"); }
    for t in chunk_texts(&root) { for bad in ["AKIAIOSFODNN7EXAMPLE", "sk_live", "Sup3rSecret", "hunter2"] { assert!(!t.contains(bad), "secret '{bad}' reached the index"); } }
    let manifest = json(&root, "governance/generated/index-manifest.json");
    let excluded = manifest["excluded"].to_string();
    assert!(excluded.contains(".env") && excluded.contains("src/app/config.py"));
    // A10 independent memory verification
    let mv = planner.with_session("S-memverifier").with_role("memory-verifier").ok(&["adopt", "verify-memory"]);
    assert_eq!(mv["verdict"], "MEMORY_ACCEPTED_FOR_V4_AUDIT", "{mv}");
    // A11 first audit: contradictions and the planted secret must block a healthy verdict
    let au1 = executor.ok(&["adopt", "audit"]);
    assert_eq!(au1["verdict"], "NOT_ADOPTED_HEALTHY", "{au1}");
    assert!(au1["findings"]["high"].as_u64().unwrap() >= 1, "supersession conflict and duplicate id must be high findings: {au1}");
    let (ok, msg) = doctor_check(&executor, "D014"); assert!(!ok && msg.contains("supersession"), "{msg}");
    // --- remediation iteration through CIT with human gates ---
    let mf = root.join(".governance-runtime/remediate.json");
    std::fs::write(&mf, json!([
        {"op": "set_status", "target": "D-0001", "value": "SUPERSEDED", "by": "D-0002"},
        {"op": "delete_file", "path": "spec/decisions/decision-2-copy.yaml", "reason": "duplicate id"},
        {"op": "write_file", "path": "src/app/config.py", "content": "\"\"\"Configuration (secret moved to config/secrets.yaml, read from environment).\"\"\"\nimport os\n\nGATEWAY_URL = \"https://gateway.example.internal\"\nGATEWAY_API_KEY = os.environ.get(\"GATEWAY_API_KEY\", \"\")\n"},
        {"op": "append_record", "record": {"id": "REQ-R1", "type": "requirement", "title": "Gateway calls are retried up to 5 times", "status": "ACTIVE", "state_class": "AUTHORITATIVE", "kind": "functional", "acceptance_criteria": ["with_retry attempts exactly 5 times before failing"], "provenance": {"extracted_from": "spec/requirements/requirements.md", "note": "resolves the dangling reference from D-0002"}}},
        {"op": "append_record", "record": {"id": "TASK-0100", "type": "task", "title": "Align MAX_RETRIES with D-0002", "status": "ACTIVE", "class": "repair", "task_status": "READY", "objective": "Code says 3, decision D-0002 says 5: align implementation and fix stale test", "decisions": ["D-0002"], "allowed_paths": ["src/**", "tests/**"], "forbidden_paths": ["governance/kernel/**"], "production_merge_allowed": true, "minimum_model_tier": "T2", "minimum_reasoning": "medium"}}
    ]).to_string()).unwrap();
    let cit = executor.ok(&["cit", "propose", "--proposal", "Resolve supersession conflict D-0001/D-0002, remove duplicate decision copy, move planted secret out of source, schedule retry alignment", "--trigger", "governance_change", "--targets", "D-0001,D-0002", "--manifest", mf.to_str().unwrap()]);
    let cid = cit["id"].as_str().unwrap().to_string();
    let sim = executor.ok(&["cit", "simulate", &cid]);
    assert_eq!(sim["impact"]["radius"], "R5"); assert_eq!(sim["impact"]["human_gate_required"], true);
    let gate = sim["human_gate"].as_str().unwrap().to_string();
    executor.ok(&["gate", "present", &gate]);
    executor.ok(&["decide", &gate, "--option", "A", "--by", "owner"]);
    executor.ok(&["cit", "approve", &cid, "--by", "owner", "--method", "human"]);
    let ex2 = executor.ok(&["cit", "execute", &cid]);
    assert_eq!(ex2["cit_status"], "COMMITTED", "{ex2}");
    assert_eq!(yaml(&root, "spec/decisions/D-0001.yaml")["status"], "SUPERSEDED");
    assert!(!exists(&root, "spec/decisions/decision-2-copy.yaml"));
    assert!(!read(&root, "src/app/config.py").contains("sk_live"));
    // retrieval now prefers the active decision and never returns the superseded one
    let q = executor.ok(&["memory", "query", "How many times should gateway calls be retried?", "--k", "5"]);
    let ids: Vec<String> = q["hits"].as_array().unwrap().iter().map(|h| h["artifact_id"].as_str().unwrap().to_string()).collect();
    assert!(ids.contains(&"D-0002".to_string()) && !ids.contains(&"D-0001".to_string()), "{ids:?}");
    // re-audit: remediated repository
    let au2 = executor.ok(&["adopt", "audit"]);
    assert!(au2["verdict"] == "ADOPTED_HEALTHY" || au2["verdict"] == "ADOPTED_WITH_ACCEPTED_EXCEPTIONS", "{au2}\nfindings: {}", au2["finding_messages"]);
    assert_eq!(au2["findings"]["critical"], 0); assert_eq!(au2["findings"]["high"], 0);
    assert!(doctor_check(&executor, "D014").0);
    // upstream: chat-derived lessons are PROJECT scope and never exportable
    let l = created.iter().find(|p| p.starts_with("spec/lessons/")).map(|p| p.trim_start_matches("spec/lessons/").trim_end_matches(".yaml").to_string());
    if let Some(l) = l { assert_eq!(executor.err(&["upstream", "prepare", &l]).error_code(), "UPSTREAM_SCOPE"); }
    // fresh agent can continue
    let fresh = planner.with_session("S-fresh");
    let st = fresh.ok(&["status"]);
    assert!(st["tasks"]["runnable"].as_array().unwrap().iter().any(|t| t == "TASK-0100"));
}
