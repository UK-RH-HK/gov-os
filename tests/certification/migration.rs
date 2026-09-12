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
    assert!(
        exists(&root, "spec/decisions/D-L0001.yaml"),
        "legacy decisions extracted: {b2}"
    );
    assert_eq!(
        yaml(&root, "spec/decisions/D-L0001.yaml")["status"],
        "PROVISIONAL"
    );
    assert_eq!(
        yaml(&root, "spec/decisions/D-L0002.yaml")["status"],
        "SUPERSEDED"
    );
    assert!(exists(
        &root,
        "archive/spec/legacy-docs/docs__old__legacy_decisions.md"
    ));
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
            && !exists(&root, "spec/decisions/D-L0001.yaml")
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
        executor.ok(&["decide", gid, "--option", "B", "--by", "owner"]);
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
