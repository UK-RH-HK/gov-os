//! Fixture 3 — path migration with independent review/verification, reference rewrites, rollback and memory rebuild.
use crate::common::*;

#[test]
fn path_migration_with_rollback_and_memory_rebuild() {
    let (root, planner) = setup_fixture("migration", "migration", "S-planner");
    let b = planner.ok(&["adopt", "baseline"]);
    assert_eq!(b["stage"], "A0");
    assert_eq!(b["interrupted"], false);
    let inv = planner.ok(&["adopt", "inventory"]);
    assert!(inv["summary"]["files"].as_u64().unwrap() >= 15);
    let cls = planner.ok(&["adopt", "classify"]);
    assert!(cls["classified"].as_u64().unwrap() >= 15);
    let lines: Vec<serde_json::Value> = read(
        &root,
        "spec/audits/GOVERNANCE-ADOPTION/02-CLASSIFICATION.jsonl",
    )
    .lines()
    .map(|l| serde_json::from_str(l).unwrap())
    .collect();
    let find = |p: &str| {
        lines
            .iter()
            .find(|x| x["path"] == p)
            .unwrap_or_else(|| panic!("{p} not classified"))
            .clone()
    };
    assert_eq!(find("notes/api-spec.md")["class"], "SPEC_AUTHORITATIVE");
    assert_eq!(find("docs/helpers_test.py")["class"], "PRODUCT_TEST");
    assert!(find("docs/helpers_test.py")["reasons"]
        .to_string()
        .contains("misplaced"));
    assert_eq!(find("docs/old/legacy_decisions.md")["class"], "DECISION");
    assert_eq!(find("lib/core/engine.py")["class"], "PRODUCT_SOURCE");
    let map = planner.ok(&["adopt", "map"]);
    assert_eq!(map["unknown_blocking_destructive"], 0);
    let cat: Vec<serde_json::Value> = read(
        &root,
        "spec/audits/GOVERNANCE-ADOPTION/04-TARGET-PATH-MAP.jsonl",
    )
    .lines()
    .map(|l| serde_json::from_str(l).unwrap())
    .collect();
    let entry = |p: &str| cat.iter().find(|x| x["current_path"] == p).unwrap().clone();
    // verifier M13: catalogue references/imports come from the import graph, not empty placeholders
    assert!(
        cat.iter().any(|e| !e["imports"]
            .as_array()
            .map(|a| a.is_empty())
            .unwrap_or(true)),
        "some catalogue entry must list its imports"
    );
    assert!(
        cat.iter().any(|e| !e["references"]
            .as_array()
            .map(|a| a.is_empty())
            .unwrap_or(true)),
        "some catalogue entry must list files referencing it"
    );
    assert!(
        entry("web/src/util/http.ts")["references"]
            .to_string()
            .contains("client.ts")
            || entry("lib/core/helpers.py")["references"]
                .as_array()
                .map(|a| !a.is_empty())
                .unwrap_or(false),
        "{}",
        entry("web/src/util/http.ts")
    );
    assert_eq!(entry("notes/api-spec.md")["action"], "MOVE");
    assert_eq!(
        entry("notes/api-spec.md")["target_path"],
        "spec/requirements/api-spec.md"
    );
    assert_eq!(entry("docs/helpers_test.py")["action"], "MOVE");
    assert_eq!(
        entry("docs/helpers_test.py")["target_path"],
        "tests/helpers_test.py"
    );
    assert_eq!(entry("docs/old/legacy_decisions.md")["action"], "EXTRACT");
    assert_eq!(entry("lib/core/engine.py")["action"], "KEEP_IN_PLACE");
    planner.ok(&["adopt", "plan"]);
    assert!(exists(
        &root,
        "spec/audits/GOVERNANCE-ADOPTION/05-ADOPTION-MIGRATION-PLAN.md"
    ));
    planner.ok(&["adopt", "test-design"]);
    // independence: the planner may not approve its own plan
    let e = planner.err(&["adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED"]);
    assert_eq!(e.error_code(), "INDEPENDENCE");
    let e2 = planner.err(&["adopt", "migrate"]);
    assert_eq!(e2.error_code(), "VERDICT_REQUIRED");
    let reviewer = planner
        .with_session("S-reviewer")
        .with_role("migration-reviewer");
    // BC-P2-34: an approval records tests the reviewer authored (the planner's scaffold is regression evidence)
    assert_eq!(
        reviewer
            .err(&["adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED"])
            .error_code(),
        "INDEPENDENT_TESTS_REQUIRED"
    );
    reviewer_authors_tests(&root);
    reviewer.ok(&[
        "adopt",
        "review",
        "--verdict",
        "MIGRATION_PLAN_APPROVED_WITH_AMENDMENTS",
        "--notes",
        "added native-layout preservation tests",
    ]);
    // --- controlled migration, batch by batch, with a rollback proof ---
    let executor = planner
        .with_session("S-executor")
        .with_role("migration-executor");
    executor.ok(&[
        "adopt", "migrate", "--batch", "0", "--name", "libcore", "--alias", "fx-mig",
    ]);
    assert!(exists(&root, "governance/framework.lock"));
    let contract = yaml(&root, "governance/project/REPOSITORY_CONTRACT.yaml");
    assert!(
        contract["paths"]
            .as_array()
            .unwrap()
            .iter()
            .any(|r| r["pattern"] == "lib/**" && r["class"] == "source"),
        "native layout must be mapped, not moved: {}",
        contract["capability_roots"]
    );
    executor.ok(&["adopt", "migrate", "--batch", "1"]);
    let before = tree_hash(
        &root,
        &[
            "spec/audits/**",
            "spec/reports/**",
            "governance/generated/**",
        ],
    );
    let b2 = executor.ok(&["adopt", "migrate", "--batch", "2"]);
    assert!(exists(&root, "spec/requirements/api-spec.md") && !exists(&root, "notes/api-spec.md"));
    assert!(
        exists(&root, "spec/architecture/architecture.md")
            && !exists(&root, "docs/architecture.md"),
        "architecture doc normalised into spec/architecture"
    );
    assert!(
        read(&root, "spec/architecture/architecture.md").contains("](../requirements/api-spec.md)"),
        "link to the moved spec must be rewritten relative to the new location: {}",
        read(&root, "spec/architecture/architecture.md")
    );
    assert!(
        read(&root, "spec/requirements/api-spec.md").contains("](../architecture/architecture.md)"),
        "links inside the moved file must be re-relativised: {}",
        read(&root, "spec/requirements/api-spec.md")
    );
    // BC-P2-21: extracted records carry content-derived ids (stable across re-runs and processing order), so they are
    // found by prefix rather than by a positional number
    let extracted = |root: &std::path::Path| -> Vec<String> {
        let mut v: Vec<String> = std::fs::read_dir(root.join("spec/decisions"))
            .map(|rd| {
                rd.filter_map(|e| e.ok())
                    .map(|e| e.file_name().to_string_lossy().to_string())
                    .filter(|n| n.starts_with("D-L") && n.ends_with(".yaml"))
                    .collect()
            })
            .unwrap_or_default();
        v.sort();
        v
    };
    let recs = extracted(&root);
    assert_eq!(recs.len(), 2, "legacy decisions extracted: {b2}");
    let statuses: Vec<String> = recs
        .iter()
        .map(|n| {
            yaml(&root, &format!("spec/decisions/{n}"))["status"]
                .as_str()
                .unwrap_or("")
                .to_string()
        })
        .collect();
    assert!(
        statuses.contains(&"PROVISIONAL".to_string())
            && statuses.contains(&"SUPERSEDED".to_string()),
        "{statuses:?}"
    );
    // BC-P2-33: the architecture doc (active, now spec/architecture/architecture.md) cites the legacy decisions log, so
    // the dependency proof found an active reference: the knowledge is extracted, but the original is NOT archived
    // and the citation is NOT re-pointed at archived material; its retirement waits for a Human Decision Gate
    assert!(
        exists(&root, "docs/old/legacy_decisions.md")
            && !exists(
                &root,
                "archive/spec/legacy-docs/docs__old__legacy_decisions.md"
            ),
        "a cited legacy document is not retired without an answered gate"
    );
    assert!(
        read(&root, "spec/architecture/architecture.md")
            .contains("](../../docs/old/legacy_decisions.md)"),
        "the citation still resolves to the original, never to the archive: {}",
        read(&root, "spec/architecture/architecture.md")
    );
    let cat_b2: Vec<serde_json::Value> = read(
        &root,
        "spec/audits/GOVERNANCE-ADOPTION/04-TARGET-PATH-MAP.jsonl",
    )
    .lines()
    .map(|l| serde_json::from_str(l).unwrap())
    .collect();
    let legacy_entry = cat_b2
        .iter()
        .find(|e| e["current_path"] == "docs/old/legacy_decisions.md")
        .unwrap();
    assert_eq!(legacy_entry["requires_human_gate"], true);
    assert!(legacy_entry["gate_reasons"]
        .to_string()
        .contains("active_references"));
    assert!(legacy_entry["dependency_proof"]["active_references"]
        .to_string()
        .contains("docs/architecture.md"));
    let rb = executor.ok(&["adopt", "rollback", "--batch", "2"]);
    assert!(rb["restored"].as_array().unwrap().len() >= 2);
    assert_eq!(
        tree_hash(
            &root,
            &[
                "spec/audits/**",
                "spec/reports/**",
                "governance/generated/**"
            ]
        ),
        before,
        "rollback must restore a byte-identical tree (checkpoints are evidence, not mutation)"
    );
    assert!(
        exists(&root, "notes/api-spec.md")
            && exists(&root, "docs/architecture.md")
            && !exists(&root, "spec/requirements/api-spec.md")
            && extracted(&root).is_empty()
    );
    executor.ok(&["adopt", "migrate", "--batch", "2"]);
    for b in ["3", "4", "5", "6", "7"] {
        executor.ok(&["adopt", "migrate", "--batch", b]);
    }
    assert!(exists(&root, "tests/helpers_test.py") && !exists(&root, "docs/helpers_test.py"));
    assert!(read(
        &root,
        "spec/audits/GOVERNANCE-ADOPTION/migration-ledger.jsonl"
    )
    .contains("batch_complete"));
    // destructive entries (heuristic dead code) carry gate records; the operator keeps them (option B) => nothing deleted
    let cat_after: Vec<serde_json::Value> = read(
        &root,
        "spec/audits/GOVERNANCE-ADOPTION/04-TARGET-PATH-MAP.jsonl",
    )
    .lines()
    .map(|l| serde_json::from_str(l).unwrap())
    .collect();
    for e in cat_after
        .iter()
        .filter(|e| e["requires_human_gate"] == true)
    {
        let gid = e["human_gate"]
            .as_str()
            .expect("gate record for destructive entry");
        executor.ok(&["gate", "present", gid]);
        crate::ws03::human_decide(&executor, gid, "B");
        assert!(exists(&root, e["current_path"].as_str().unwrap()));
    }
    // --- independent verification against reality ---
    let e3 = executor.err(&["adopt", "verify-migration"]);
    assert_eq!(e3.error_code(), "INDEPENDENCE");
    let verifier = planner
        .with_session("S-verifier")
        .with_role("migration-verifier");
    let v = verifier.ok(&["adopt", "verify-migration"]);
    assert_eq!(v["verdict"], "MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD", "{v}");
    assert!(
        v["broken_links"].as_array().unwrap().is_empty()
            && v["legacy_in_active_tree"].as_array().unwrap().is_empty()
    );
    assert_eq!(v["tests"]["fail"], 0);
    // --- legacy extraction, memory on stable paths, independent memory verification, audit ---
    executor.ok(&["adopt", "extract-legacy"]);
    let m = executor.ok(&["adopt", "build-memory"]);
    assert!(m["counts"]["symbols"].as_u64().unwrap() > 0);
    let manifest = json(&root, "governance/generated/index-manifest.json");
    let keys: Vec<&String> = manifest["artifacts"].as_object().unwrap().keys().collect();
    assert!(
        keys.iter()
            .any(|k| k.as_str() == "spec/requirements/api-spec.md")
            && !keys.iter().any(|k| k.starts_with("notes/")),
        "index must reference canonical paths only"
    );
    let e4 = executor.err(&["adopt", "verify-memory"]);
    assert_eq!(e4.error_code(), "INDEPENDENCE");
    // BC-P2-34: A10 is the designated memory verifier's, on held-out queries it authored
    let memverifier = planner
        .with_session("S-memverifier")
        .with_role("memory-verifier");
    assert_eq!(
        memverifier.err(&["adopt", "verify-memory"]).error_code(),
        "INDEPENDENT_HELDOUT_REQUIRED"
    );
    assert!(verifier_authors_heldout(&root) >= 5);
    let mv = memverifier.ok(&["adopt", "verify-memory"]);
    assert_eq!(mv["verdict"], "MEMORY_ACCEPTED_FOR_V4_AUDIT", "{mv}");
    assert_eq!(mv["reproducible"], true);
    assert_eq!(
        executor.err(&["adopt", "audit"]).error_code(),
        "INDEPENDENCE"
    );
    let au = planner
        .with_session("S-auditor")
        .with_role("independent-auditor")
        .ok(&["adopt", "audit"]);
    assert!(
        au["verdict"] == "ADOPTED_HEALTHY" || au["verdict"] == "ADOPTED_WITH_ACCEPTED_EXCEPTIONS",
        "{au}"
    );
    assert_eq!(au["findings"]["critical"], 0);
    let st = executor.ok(&["adopt", "status"]);
    assert_eq!(st["next_stage"], serde_json::Value::Null);
}

fn catalogue(root: &std::path::Path) -> Vec<serde_json::Value> {
    read(
        root,
        "spec/audits/GOVERNANCE-ADOPTION/04-TARGET-PATH-MAP.jsonl",
    )
    .lines()
    .map(|l| serde_json::from_str(l).unwrap())
    .collect()
}

/// The independent migration reviewer (Role B, `migration-reviewer`) authors acceptance tests of its own before it
/// approves (A5; adoption protocol §10): here, that native-layout product files the plan keeps in place are still
/// present after migration. Returns the number of tests added. (Test harness standing in for the reviewer.)
pub fn reviewer_authors_tests(root: &std::path::Path) -> usize {
    let tf = "spec/audits/GOVERNANCE-ADOPTION/06-migration-tests.yaml";
    let mut t = yaml(root, tf);
    let keep: Vec<String> = catalogue(root)
        .iter()
        .filter(|e| {
            e["action"] == "KEEP_IN_PLACE"
                && e["requires_human_gate"] != true
                && e["sensitivity"] != "secret"
                && matches!(
                    e["current_class"].as_str().unwrap_or(""),
                    "PRODUCT_SOURCE" | "PRODUCT_TEST"
                )
        })
        .filter_map(|e| e["current_path"].as_str().map(String::from))
        .take(2)
        .collect();
    assert!(
        !keep.is_empty(),
        "no kept product file to write a reviewer test for"
    );
    for (i, path) in keep.iter().enumerate() {
        t["tests"].as_array_mut().unwrap().push(serde_json::json!({"id": format!("RT-{:03}", i + 1), "kind": "path_present", "path": path,
            "description": "reviewer: the native product layout the plan keeps in place survives the migration"}));
    }
    write_yaml(root, tf, &t);
    keep.len()
}

/// The independent memory verifier (Role F, `memory-verifier`) authors held-out queries of its own before A10
/// (adoption protocol §15): exact-path queries for indexed files the builder's starter set does not ask about.
/// Returns the number of queries added. (Test harness standing in for the verifier.)
pub fn verifier_authors_heldout(root: &std::path::Path) -> usize {
    let hf = "governance/tests/memory/heldout.yaml";
    let mut h = yaml(root, hf);
    let asked: Vec<String> = h["queries"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|q| q["query"].as_str().map(String::from))
                .collect()
        })
        .unwrap_or_default();
    let db = gov_runtime::memory::db::RuntimeDb::open(&root.join(".governance-runtime/state.db"))
        .unwrap();
    let rows = db
        .query("SELECT artifact_id, path FROM artifacts WHERE record_type='file' AND path_class IN ('source','test','authoritative','evidence') ORDER BY path DESC LIMIT 60", &[])
        .unwrap();
    drop(db);
    let mut n = 0;
    for r in rows {
        let path = r["path"].as_str().unwrap_or("").to_string();
        if path.is_empty() || asked.contains(&path) || n >= 6 {
            continue;
        }
        n += 1;
        h["queries"].as_array_mut().unwrap().push(serde_json::json!({"id": format!("VQ-{n:03}"), "category": "exact_path", "query": path,
            "expected_refs": [r["artifact_id"]], "forbidden": [], "k": 8, "route": "path", "author": "independent memory verifier"}));
    }
    write_yaml(root, hf, &h);
    n
}

/// Repair-1 WS-9 regression (builder evidence, not acceptance): the path map represents document citations
/// (BC-P2-52); every retirement is preceded by a dependency proof over code, configuration and docs, is gated while
/// active references exist and never re-points them (BC-P2-33); the plan and the independent tests must agree before
/// approval (BC-P2-33); knowledge without cue words is kept for review (BC-P2-33); ids, lineage and plan versions
/// survive a re-run, and the Governance OS's own generated adapter is never legacy (BC-P2-21, BC-P2-33).
#[test]
fn adoption_dependency_proof_citations_and_rerun_identity() {
    use serde_json::json;
    let root = tmp("adopt-deps");
    write(
        &root,
        "README.md",
        "# svc\nSee the [login spec](docs/spec-login.md) and <a href=\"docs/ops.md\">ops</a>.\n\n[notes]: docs/notes.md\n",
    );
    write(
        &root,
        "docs/spec-login.md",
        "# Login\nRequirement: users log in with email.\n",
    );
    write(&root, "docs/ops.md", "# Ops runbook\n");
    write(&root, "docs/notes.md", "notes about the service\n");
    write(&root, "src/app/__init__.py", "");
    write(
        &root,
        "src/app/main.py",
        "from app.rules import load\n\n\ndef main():\n    return load()\n",
    );
    write(
        &root,
        "src/app/rules.py",
        "def load():\n    with open('.cursorrules') as f:\n        return f.read()\n",
    );
    write(
        &root,
        "config/settings.yaml",
        "assistant:\n  history_db: memory/chat_history.jsonl\n",
    );
    write(
        &root,
        ".cursorrules",
        "Always use tabs. These rules are authoritative.\n",
    );
    write(
        &root,
        "memory/chat_history.jsonl",
        "{\"content\": \"Decision: we decided to cache quotes for ten minutes.\"}\n{\"content\": \"The staging host requires mutual TLS with the ops client certificate.\"}\n",
    );
    write(
        &root,
        "CLAUDE.md",
        "Legacy agent instructions that nothing refers to any more.\n",
    );
    git_init_commit(&root);
    let planner = Gov::new(&root, "S-plan");
    for s in [
        "baseline",
        "inventory",
        "classify",
        "map",
        "plan",
        "test-design",
    ] {
        planner.ok(&["adopt", s]);
    }
    let cat = catalogue(&root);
    let e = |p: &str| {
        cat.iter()
            .find(|x| x["current_path"] == p)
            .unwrap_or_else(|| panic!("{p} not catalogued"))
            .clone()
    };
    // BC-P2-52: markdown, HTML and reference-style citations, represented at both ends
    let cites = e("README.md")["citations"].to_string();
    for t in ["docs/spec-login.md", "docs/ops.md", "docs/notes.md"] {
        assert!(cites.contains(t), "README.md citations lack {t}: {cites}");
    }
    assert!(e("docs/spec-login.md")["references"]
        .to_string()
        .contains("README.md"));
    assert!(e("docs/spec-login.md")["cited_by"]
        .to_string()
        .contains("README.md"));
    // BC-P2-33: dependency proofs over code, configuration and docs
    assert_eq!(e(".cursorrules")["requires_human_gate"], true);
    assert!(e(".cursorrules")["dependency_proof"]["active_references"]
        .to_string()
        .contains("src/app/rules.py"));
    assert!(
        e("memory/chat_history.jsonl")["dependency_proof"]["active_references"]
            .to_string()
            .contains("config/settings.yaml")
    );
    assert_eq!(
        e("CLAUDE.md")["dependency_proof"]["result"],
        "NO_ACTIVE_REFERENCES"
    );
    assert_eq!(e("CLAUDE.md")["batch"], 1);
    // BC-P2-21: W1 identity of catalogue entries and of the plan
    for x in &cat {
        assert!(
            x["artifact_id"].as_str().unwrap().starts_with("ART-"),
            "{x}"
        );
        assert_eq!(x["type"], "migration-catalogue-entry");
        assert!(x["entry_hash"].is_string() && x["producer"]["stage"] == "A3");
    }
    let plan = yaml(&root, "spec/audits/GOVERNANCE-ADOPTION/05-plan.yaml");
    assert_eq!(plan["id"], "MPLAN-GOVERNANCE-ADOPTION");
    assert_eq!(plan["type"], "migration-plan");
    assert_eq!(plan["version"], 1);
    // plan/test agreement: a test contradicting the plan's disposition blocks approval
    let tf = "spec/audits/GOVERNANCE-ADOPTION/06-migration-tests.yaml";
    let original = yaml(&root, tf);
    let mut t = original.clone();
    t["tests"].as_array_mut().unwrap().push(json!({"id": "MT-R1", "kind": "path_absent", "path": ".cursorrules", "after_batch": 1, "description": "reviewer expects the rules gone after batch 1"}));
    write_yaml(&root, tf, &t);
    let reviewer = planner
        .with_session("S-review")
        .with_role("migration-reviewer");
    assert_eq!(
        reviewer
            .err(&["adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED"])
            .error_code(),
        "PLAN_TEST_DISAGREEMENT"
    );
    write_yaml(&root, tf, &original);
    reviewer_authors_tests(&root);
    reviewer.ok(&["adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED"]);
    let executor = planner
        .with_session("S-exec")
        .with_role("migration-executor");
    let rules_before = read(&root, "src/app/rules.py");
    let settings_before = read(&root, "config/settings.yaml");
    executor.ok(&["adopt", "migrate", "--name", "svc", "--alias", "fx-deps"]);
    assert!(
        !exists(&root, "CLAUDE.md") && exists(&root, "archive/governance/legacy-rules/CLAUDE.md")
    );
    assert!(
        exists(&root, ".cursorrules"),
        "a legacy file live code reads is not retired without an answered gate"
    );
    assert_eq!(
        read(&root, "src/app/rules.py"),
        rules_before,
        "live code is never rewritten to read archived legacy material"
    );
    let cat2 = catalogue(&root);
    for g in cat2.iter().filter(|x| x["requires_human_gate"] == true) {
        let gid = g["human_gate"].as_str().expect("gate per gated entry");
        executor.ok(&["gate", "present", gid]);
        // BC-P2-10 (WS-3): the human's answer comes through the owner-signed channel, not `--by owner`
        crate::ws03::human_decide(&executor, gid, "B");
    }
    executor.ok(&["adopt", "migrate", "--batch", "7"]);
    let v = planner
        .with_session("S-verify")
        .with_role("migration-verifier")
        .ok(&["adopt", "verify-migration"]);
    assert_eq!(v["verdict"], "MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD", "{v}");
    assert!(v["legacy_kept_by_decision"]
        .to_string()
        .contains(".cursorrules"));
    let a8 = executor.ok(&["adopt", "extract-legacy"]);
    let store = a8["stores"]
        .as_array()
        .unwrap()
        .iter()
        .find(|s| s["path"] == "memory/chat_history.jsonl")
        .unwrap()
        .clone();
    assert_ne!(store["disposition"], "RETIRE", "{store}");
    assert!(exists(&root, "memory/chat_history.jsonl"));
    assert_eq!(read(&root, "config/settings.yaml"), settings_before);
    assert!(
        a8["created_records"]
            .to_string()
            .contains("spec/reports/RPT-LK"),
        "a unit without cue words is registered for review: {a8}"
    );
    // a new adoption pass: ids stable, the OS's own adapter current (never legacy), moved artefacts keep lineage
    git_commit_all(&root, "after first adoption pass");
    for s in ["baseline", "inventory", "classify", "map"] {
        planner.ok(&["adopt", s]);
    }
    let cat3 = catalogue(&root);
    for x in &cat {
        if let Some(y) = cat3.iter().find(|y| y["current_path"] == x["current_path"]) {
            assert_eq!(x["artifact_id"], y["artifact_id"], "{}", x["current_path"]);
        }
    }
    let adapter = cat3
        .iter()
        .find(|y| y["current_path"] == "governance/generated/adapters/ide/RULES.md")
        .unwrap();
    assert_eq!(adapter["action"], "KEEP_IN_PLACE");
    assert_eq!(adapter["authority"], "ACTIVE");
    let moved = cat3
        .iter()
        .find(|y| y["current_path"] == "archive/governance/legacy-rules/CLAUDE.md")
        .unwrap();
    assert_eq!(
        moved["lineage"]["migrated_from"]["artifact_id"],
        e("CLAUDE.md")["artifact_id"]
    );
    planner.ok(&["adopt", "plan"]);
    let plan2 = yaml(&root, "spec/audits/GOVERNANCE-ADOPTION/05-plan.yaml");
    assert_eq!(plan2["version"], 2);
    assert_eq!(plan2["supersedes"][0], "MPLAN-GOVERNANCE-ADOPTION@v1");
    assert_eq!(
        json(
            &root,
            "spec/audits/GOVERNANCE-ADOPTION/05-plan.versions/v0001.json"
        )["status"],
        "SUPERSEDED"
    );
}

/// Repair-1 round-2 WS-9 regression (builder evidence, not acceptance), BC-P2-34 adoption side: every independent
/// adoption stage (A5, A7, A10, A11) is performed only by its designated kernel role, declared, in a declared session
/// that authored no planner/executor/memory-builder stage, and a session keeps one role; the A5 approval requires
/// reviewer-authored tests and binds the catalogue, plan and tests it approved, so post-approval edits (tests emptied,
/// a KEEP turned into an ungated DELETE, a plan batch dropped) are refused before anything executes; the adoption
/// record is honoured only as gov wrote it (T2); a gate answer authorises only the catalogue entry it was raised for;
/// A7 never accepts with zero executed tests; A10's held-out queries come from the memory verifier, not the builder;
/// A11 is the G5 full suite run by a fresh independent auditor.
#[test]
fn adoption_independence_is_bound_to_declared_roles_and_approved_artefacts() {
    use serde_json::json;
    let root = tmp("adopt-indep");
    write(
        &root,
        "README.md",
        "# ledger\nSee [the ledger spec](docs/spec-ledger.md).\n",
    );
    write(
        &root,
        "docs/spec-ledger.md",
        "# Ledger\nRequirement: totals are integer cents.\n",
    );
    write(&root, "src/ledger/__init__.py", "");
    write(
        &root,
        "src/ledger/core.py",
        "from ledger.util import cents\n\n\ndef total(xs):\n    return sum(cents(x) for x in xs)\n",
    );
    write(
        &root,
        "src/ledger/util.py",
        "def cents(x):\n    return int(round(x * 100))\n",
    );
    write(
        &root,
        "src/ledger/old_report.py",
        "def monthly_report_unused():\n    return 'report'\n",
    );
    write(
        &root,
        "src/ledger/old_export.py",
        "def csv_export_unused():\n    return 'csv'\n",
    );
    write(
        &root,
        "tests/test_core.py",
        "from ledger.core import total\n\n\ndef test_total():\n    assert total([1.0]) == 100\n",
    );
    write(
        &root,
        ".cursorrules",
        "Use spaces. These rules are authoritative.\n",
    );
    git_init_commit(&root);
    let ev = "spec/audits/GOVERNANCE-ADOPTION";
    let (tf, cf, pf, bf) = (
        format!("{ev}/06-migration-tests.yaml"),
        format!("{ev}/04-TARGET-PATH-MAP.jsonl"),
        format!("{ev}/05-plan.yaml"),
        format!("{ev}/00-BASELINE.yaml"),
    );
    let planner = Gov::new(&root, "S-plan");
    for s in [
        "baseline",
        "inventory",
        "classify",
        "map",
        "plan",
        "test-design",
    ] {
        planner.ok(&["adopt", s]);
    }
    let cause = |o: &Out| o.details()["cause"].as_str().unwrap_or("").to_string();
    let review = |g: &Gov| g.run(&["adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED"]);
    // --- A5 is the designated reviewer's, declared, in a session that authored no builder stage
    let o = review(&planner);
    assert_eq!(
        (o.error_code(), cause(&o)),
        ("INDEPENDENCE".into(), "ROLE_NOT_DESIGNATED".into()),
        "{}",
        o.envelope
    );
    let o = review(&planner.with_session("S-r").with_role("migration-executor"));
    assert_eq!(cause(&o), "ROLE_NOT_DESIGNATED");
    let o = review(&planner.with_role("migration-reviewer"));
    assert_eq!(
        (o.error_code(), cause(&o)),
        ("INDEPENDENCE".into(), "SAME_SESSION_AS_BUILDER".into()),
        "{}",
        o.envelope
    );
    let o = review(&planner.with_session("").with_role("migration-reviewer"));
    assert_eq!(
        o.error_code(),
        "ADOPTION_SESSION_UNDECLARED",
        "{}",
        o.envelope
    );
    let o = planner
        .with_session("S-r")
        .with_role("migration-reviewer")
        .run(&[
            "adopt",
            "review",
            "--verdict",
            "MIGRATION_PLAN_APPROVED",
            "--reviewer-session",
            "S-other",
        ]);
    assert_eq!(o.error_code(), "SESSION_CONFLICT", "{}", o.envelope);
    let reviewer = planner
        .with_session("S-rev")
        .with_role("migration-reviewer");
    // --- the planner's scaffold is not the reviewer's tests, relabelled or not
    let scaffold = read(&root, &tf);
    assert_eq!(review(&reviewer).error_code(), "INDEPENDENT_TESTS_REQUIRED");
    let mut t = yaml(&root, &tf);
    t["tests"][0]["id"] = json!("RT-RELABELLED");
    t["tests"][0]["description"] = json!("reviewer: kernel pinned");
    write_yaml(&root, &tf, &t);
    assert_eq!(review(&reviewer).error_code(), "INDEPENDENT_TESTS_REQUIRED");
    write(&root, &tf, &scaffold);
    let mut t = yaml(&root, &tf);
    t["tests"]
        .as_array_mut()
        .unwrap()
        .push(json!({"id": "RT-BAD", "kind": "looks_fine", "path": "README.md"}));
    write_yaml(&root, &tf, &t);
    assert_eq!(review(&reviewer).error_code(), "INDEPENDENT_TESTS_INVALID");
    write(&root, &tf, &scaffold);
    assert!(reviewer_authors_tests(&root) >= 1);
    let a5 = reviewer.ok(&["adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED"])["verdict"]
        .clone();
    assert_eq!(a5["role"], "migration-reviewer");
    assert_eq!(a5["session"], "S-rev");
    assert_eq!(a5["independence"]["established"], true);
    assert!(a5["reviewer_tests_count"].as_u64().unwrap() >= 1);
    for k in ["catalogue_sha256", "plan_sha256", "tests_sha256"] {
        assert_eq!(a5[k].as_str().map(|x| x.len()), Some(64), "{k}: {a5}");
    }
    // --- execution is bound to exactly what was approved (alpha-r [N2])
    let executor = planner
        .with_session("S-exec")
        .with_role("migration-executor");
    let approved_tests = read(&root, &tf);
    let mut t = yaml(&root, &tf);
    t["tests"] = json!([]);
    write_yaml(&root, &tf, &t);
    let o = executor.run(&[
        "adopt", "migrate", "--name", "ledger", "--alias", "fx-indep",
    ]);
    assert_eq!(o.error_code(), "APPROVAL_STALE", "{}", o.envelope);
    assert!(o.details()["changed"].to_string().contains("tests"));
    assert!(
        !exists(&root, "governance/framework.lock"),
        "nothing executed"
    );
    write(&root, &tf, &approved_tests);
    let approved_catalogue = read(&root, &cf);
    let cat: Vec<serde_json::Value> = catalogue(&root)
        .into_iter()
        .map(|mut e| {
            if e["current_path"] == "src/ledger/util.py" {
                assert_eq!(e["action"], "KEEP_IN_PLACE");
                e["action"] = json!("DELETE_FROM_ACTIVE_TREE");
                e["batch"] = json!(2);
                e["requires_human_gate"] = json!(false);
            }
            e
        })
        .collect();
    write(
        &root,
        &cf,
        &cat.iter().map(|e| format!("{e}\n")).collect::<String>(),
    );
    let o = executor.run(&[
        "adopt", "migrate", "--name", "ledger", "--alias", "fx-indep",
    ]);
    assert_eq!(o.error_code(), "APPROVAL_STALE", "{}", o.envelope);
    assert!(o.details()["changed"].to_string().contains("catalogue"));
    write(&root, &cf, &approved_catalogue);
    let approved_plan = read(&root, &pf);
    let mut plan = yaml(&root, &pf);
    plan["batches"].as_array_mut().unwrap().pop();
    write_yaml(&root, &pf, &plan);
    let o = executor.run(&[
        "adopt", "migrate", "--name", "ledger", "--alias", "fx-indep",
    ]);
    assert_eq!(o.error_code(), "APPROVAL_STALE", "{}", o.envelope);
    assert!(o.details()["changed"].to_string().contains("plan"));
    write(&root, &pf, &approved_plan);
    // --- the adoption record is honoured only as gov wrote it (T2)
    let record = read(&root, &bf);
    let mut b = yaml(&root, &bf);
    b["verdicts"]["A5"]["tests_sha256"] = json!("0".repeat(64));
    write_yaml(&root, &bf, &b);
    assert_eq!(
        executor
            .run(&["adopt", "migrate", "--name", "ledger", "--alias", "fx-indep"])
            .error_code(),
        "T2_UNBOUND"
    );
    write(&root, &bf, &record);
    let mig = executor.ok(&[
        "adopt", "migrate", "--name", "ledger", "--alias", "fx-indep",
    ]);
    assert_eq!(mig["approval"]["tests_sha256"], a5["tests_sha256"]);
    // --- a gate answer authorises only the entry it was raised for
    let cat = catalogue(&root);
    let dead: Vec<serde_json::Value> = cat
        .iter()
        .filter(|e| e["requires_human_gate"] == true && e["action"] == "DELETE_FROM_ACTIVE_TREE")
        .cloned()
        .collect();
    assert!(dead.len() >= 2, "{dead:?}");
    let (e1, e2) = (&dead[0], &dead[1]);
    let (g1, g2) = (
        e1["human_gate"].as_str().unwrap().to_string(),
        e2["human_gate"].as_str().unwrap().to_string(),
    );
    crate::ws03::human_decide(&executor, &g1, "A");
    crate::ws03::human_decide(&executor, &g2, "B");
    let own = read(&root, &cf);
    let swapped: String = cat
        .iter()
        .map(|e| {
            let mut e = e.clone();
            if e["artifact_id"] == e2["artifact_id"] {
                e["human_gate"] = json!(g1);
            }
            format!("{e}\n")
        })
        .collect();
    write(&root, &cf, &swapped);
    executor.ok(&["adopt", "migrate", "--batch", "7"]);
    assert!(
        !exists(&root, e1["current_path"].as_str().unwrap()),
        "answered A for its own entry: executed"
    );
    assert!(
        exists(&root, e2["current_path"].as_str().unwrap()),
        "another entry's answered gate authorises nothing"
    );
    write(&root, &cf, &own);
    // --- A7: the designated verifier only; a session keeps its role; no acceptance from zero tests
    assert_eq!(
        cause(&executor.run(&["adopt", "verify-migration"])),
        "ROLE_NOT_DESIGNATED"
    );
    assert_eq!(
        planner
            .with_session("S-v")
            .with_role("backend-engineer")
            .run(&["adopt", "verify-migration"])
            .error_code(),
        "INDEPENDENCE"
    );
    assert_eq!(
        planner
            .with_session("S-rev")
            .with_role("migration-verifier")
            .run(&["adopt", "verify-migration"])
            .error_code(),
        "ADOPTION_ROLE_INCONSISTENT"
    );
    let verifier = planner
        .with_session("S-ver")
        .with_role("migration-verifier");
    let mut t = yaml(&root, &tf);
    t["tests"] = json!([]);
    write_yaml(&root, &tf, &t);
    let o = verifier.run(&[
        "adopt",
        "verify-migration",
        "--verdict",
        "MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD",
    ]);
    assert_eq!(o.error_code(), "VERDICT_CONFLICT", "{}", o.envelope);
    let v = verifier.ok(&["adopt", "verify-migration"]);
    assert_eq!(v["verdict"], "MIGRATION_REJECTED_NEEDS_REPAIR");
    assert!(
        v["approval_problems"]
            .to_string()
            .contains("no independent test was executed"),
        "{v}"
    );
    write(&root, &tf, &approved_tests);
    let v = verifier.ok(&["adopt", "verify-migration"]);
    assert_eq!(v["verdict"], "MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD", "{v}");
    assert!(v["tests"]["executed"].as_u64().unwrap() >= 1);
    executor.ok(&["adopt", "extract-legacy"]);
    executor.ok(&["adopt", "build-memory"]);
    // --- A10: held-out queries authored by the memory verifier; the builder's starter set, relabelled, is not
    let mv = planner.with_session("S-memv").with_role("memory-verifier");
    assert_eq!(
        mv.run(&["adopt", "verify-memory"]).error_code(),
        "INDEPENDENT_HELDOUT_REQUIRED"
    );
    let hf = "governance/tests/memory/heldout.yaml";
    let starter = read(&root, hf);
    let mut h = yaml(&root, hf);
    let copies: Vec<serde_json::Value> = h["queries"]
        .as_array()
        .unwrap()
        .iter()
        .filter(|q| q["pending"] != true)
        .enumerate()
        .map(|(i, q)| {
            let mut c = q.clone();
            c["id"] = json!(format!("VQ-COPY-{i}"));
            c["k"] = json!(5);
            c["category"] = json!("verifier");
            c
        })
        .collect();
    h["queries"].as_array_mut().unwrap().extend(copies);
    write_yaml(&root, hf, &h);
    assert_eq!(
        mv.run(&["adopt", "verify-memory"]).error_code(),
        "INDEPENDENT_HELDOUT_REQUIRED"
    );
    write(&root, hf, &starter);
    assert!(verifier_authors_heldout(&root) >= 5);
    let m = mv.ok(&["adopt", "verify-memory"]);
    assert_eq!(m["verdict"], "MEMORY_ACCEPTED_FOR_V4_AUDIT", "{m}");
    assert!(m["independent_heldout"]["queries"].as_u64().unwrap() >= 5);
    // --- A11: a fresh independent auditor, as the G5 full suite
    assert_eq!(
        cause(&executor.run(&["adopt", "audit"])),
        "ROLE_NOT_DESIGNATED"
    );
    assert_eq!(
        cause(
            &planner
                .with_session("S-exec")
                .with_role("independent-auditor")
                .run(&["adopt", "audit"])
        ),
        "SAME_SESSION_AS_BUILDER"
    );
    let au = planner
        .with_session("S-aud")
        .with_role("independent-auditor")
        .ok(&["adopt", "audit"]);
    assert_eq!(au["tier"], "G5", "{au}");
    assert!(au["audit"].as_str().map(|a| !a.is_empty()).unwrap_or(false));
    assert!(au["checks"]
        .as_array()
        .unwrap()
        .iter()
        .any(
            |c| c["criterion"] == "comprehensive audit by a fresh independent auditor"
                && c["ok"] == true
        ));
    let st = planner.ok(&["adopt", "status"]);
    assert_eq!(st["honoured"], true);
    for (stage, role) in [
        ("A5", "migration-reviewer"),
        ("A7", "migration-verifier"),
        ("A10", "memory-verifier"),
        ("A11", "independent-auditor"),
    ] {
        let s = st["stages"]
            .as_array()
            .unwrap()
            .iter()
            .find(|s| s["stage"] == stage)
            .unwrap()
            .clone();
        assert_eq!(s["by"]["role"], role, "{s}");
        assert_eq!(s["by"]["independence_established"], true, "{s}");
    }
}
