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
    reviewer.ok(&[
        "adopt",
        "review",
        "--verdict",
        "MIGRATION_PLAN_APPROVED_WITH_AMENDMENTS",
        "--notes",
        "added behaviour-preservation command test",
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
    let mv = verifier
        .with_session("S-memverifier")
        .ok(&["adopt", "verify-memory"]);
    assert_eq!(mv["verdict"], "MEMORY_ACCEPTED_FOR_V4_AUDIT", "{mv}");
    assert_eq!(mv["reproducible"], true);
    let au = executor.ok(&["adopt", "audit"]);
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
        executor.ok(&["decide", gid, "--option", "B", "--by", "owner"]);
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
