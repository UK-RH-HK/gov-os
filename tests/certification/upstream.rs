//! Fixture 5 — upstream lesson export gate: sanitisation, fail-closed scans, approval, outbound allowlist, ledger.
use crate::common::*;
use serde_json::json;

#[test]
fn upstream_export_gate_fails_closed_and_sanitises() {
    let root = tmp("upstream");
    let proj = root.join("project"); std::fs::create_dir_all(&proj).unwrap();
    write(&proj, "README.md", "# shipping-quotes internal\n");
    git_init_commit(&proj);
    let g = Gov::new(&proj, "S-up");
    g.ok(&["init", "--name", "shipping-quotes", "--alias", "proj-alpha"]);
    let mut ds = yaml(&proj, "governance/project/DATA_SENSITIVITY.yaml");
    ds["identifiers_to_strip"] = json!(["Acme Freight Ltd", "shipping-quotes"]);
    write_yaml(&proj, "governance/project/DATA_SENSITIVITY.yaml", &ds);
    for l in ["L-0001", "L-0002", "L-0003", "L-0004"] { std::fs::copy(canonical_root().join(format!("fixtures/upstream-learning/lessons/{l}.yaml")), proj.join(format!("spec/lessons/{l}.yaml"))).unwrap(); }
    // planted files that must never leave (negative controls)
    write(&proj, "product/api/gateway.py", "API_KEY = 'AKIAIOSFODNN7EXAMPLE'\n");
    let inbox = root.join("canonical").join("lessons").join("inbox"); std::fs::create_dir_all(&inbox).unwrap();
    // --- L-0001: clean framework lesson with synthetic reproducer ---
    let p1 = g.ok(&["upstream", "prepare", "L-0001"]);
    assert_eq!(p1["export_allowed"], true); assert_eq!(p1["packet_id"], "PKT-0001");
    let packet_path = p1["path"].as_str().unwrap().to_string();
    let e = g.err(&["upstream", "submit", "PKT-0001", "--destination", inbox.to_str().unwrap()]);
    assert_eq!(e.error_code(), "HUMAN_GATE_REQUIRED", "human approval is required by LEARNING_POLICY");
    let e2 = g.err(&["upstream", "submit", "PKT-0001", "--destination", "https://example.invalid/inbox", "--approved-by", "owner"]);
    assert_eq!(e2.error_code(), "REMOTE_TRANSPORT_NOT_CONFIGURED");
    let e3 = g.err(&["upstream", "submit", "PKT-0001", "--destination", root.to_str().unwrap(), "--approved-by", "owner"]);
    assert_eq!(e3.error_code(), "UPSTREAM_DESTINATION");
    let s = g.ok(&["upstream", "submit", "PKT-0001", "--destination", inbox.to_str().unwrap(), "--approved-by", "owner"]);
    assert_eq!(s["approved_by"], "owner");
    let dest = std::path::PathBuf::from(s["destination"].as_str().unwrap());
    assert!(dest.join("packet.yaml").exists() && dest.join("fixture/scenario.yaml").exists());
    let sent: Vec<String> = gov_runtime::paths::iter_repo_files(&dest, false).into_iter().map(|(_, r)| r).collect();
    assert_eq!(sent.len(), 2, "outbound allowlist: only packet.yaml + declared synthetic fixture files: {sent:?}");
    assert!(read(&proj, "spec/reports/upstream-ledger.jsonl").contains("PKT-0001"));
    assert_eq!(yaml(&proj, "spec/lessons/L-0001.yaml")["lifecycle"], "promoted");
    let pk = gov_runtime::util::read_yaml(&dest.join("packet.yaml")).unwrap();
    assert_eq!(pk["scope"], "FRAMEWORK"); assert_eq!(pk["source_project_alias"], "proj-alpha"); assert_eq!(pk["raw_product_code_included"], false);
    assert!(pk["payload_hash"].as_str().unwrap().len() == 64);
    let _ = packet_path;
    // --- L-0002: project scope is never eligible ---
    assert_eq!(g.err(&["upstream", "prepare", "L-0002"]).error_code(), "UPSTREAM_SCOPE");
    // --- L-0003: secrets + customer + raw code + product path → fail closed ---
    let b = g.err(&["upstream", "prepare", "L-0003"]);
    assert_eq!(b.error_code(), "UPSTREAM_BLOCKED");
    let reasons = b.details()["reasons"].to_string();
    assert!(reasons.contains("secret pattern") && reasons.contains("code line"), "{reasons}");
    let blocked_dir = proj.join(".governance-runtime/outbound/PKT-0002");
    assert!(blocked_dir.join("blocked.json").exists() && !blocked_dir.join("packet.yaml").exists());
    // --- L-0004: identifiers redacted ---
    let p4 = g.ok(&["upstream", "prepare", "L-0004"]);
    assert!(p4["scans"]["identifiers_redacted"].as_u64().unwrap() >= 2, "{}", p4["scans"]);
    let text = read(&proj, ".governance-runtime/outbound/PKT-0003/packet.yaml");
    assert!(!text.contains("Acme") && !text.contains("shipping-quotes"), "identifiers must be redacted: {text}");
    g.ok(&["upstream", "submit", "PKT-0003", "--destination", inbox.to_str().unwrap(), "--approved-by", "owner"]);
    // --- inbox never contains secrets, customer or project identifiers, or product code ---
    for (abs, rel) in gov_runtime::paths::iter_repo_files(&inbox, false) {
        let t = std::fs::read_to_string(&abs).unwrap();
        for bad in ["AKIA", "Acme", "shipping-quotes", "gateway.py", "sk_live"] { assert!(!t.contains(bad), "{rel} leaked '{bad}'"); }
    }
    // --- fixture file under a forbidden outbound path is blocked ---
    let mut l5 = yaml(&proj, "spec/lessons/L-0001.yaml");
    l5["id"] = json!("L-0005"); l5["synthetic_reproducer"]["files"] = json!({"product/api/leak.py": "print(1)"});
    write_yaml(&proj, "spec/lessons/L-0005.yaml", &l5);
    let b5 = g.err(&["upstream", "prepare", "L-0005"]);
    assert_eq!(b5.error_code(), "UPSTREAM_BLOCKED");
    assert!(b5.details()["reasons"].to_string().contains("forbidden outbound path"));
}
