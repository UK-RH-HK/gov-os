//! Fixture 5 — upstream lesson export gate: sanitisation, fail-closed scans, approval, outbound allowlist, ledger.
use crate::common::*;
use serde_json::json;

#[test]
fn upstream_export_gate_fails_closed_and_sanitises() {
    let root = tmp("upstream");
    let proj = root.join("project");
    std::fs::create_dir_all(&proj).unwrap();
    write(&proj, "README.md", "# shipping-quotes internal\n");
    git_init_commit(&proj);
    let g = Gov::new(&proj, "S-up");
    g.ok(&["init", "--name", "shipping-quotes", "--alias", "proj-alpha"]);
    let mut ds = yaml(&proj, "governance/project/DATA_SENSITIVITY.yaml");
    ds["identifiers_to_strip"] = json!(["Acme Freight Ltd", "shipping-quotes"]);
    write_yaml(&proj, "governance/project/DATA_SENSITIVITY.yaml", &ds);
    for l in ["L-0001", "L-0002", "L-0003", "L-0004"] {
        std::fs::copy(
            canonical_root().join(format!("fixtures/upstream-learning/lessons/{l}.yaml")),
            proj.join(format!("spec/lessons/{l}.yaml")),
        )
        .unwrap();
    }
    // planted files that must never leave (negative controls)
    write(
        &proj,
        "product/api/gateway.py",
        "API_KEY = 'AKIAIOSFODNN7EXAMPLE'\n",
    );
    let inbox = root.join("canonical").join("lessons").join("inbox");
    std::fs::create_dir_all(&inbox).unwrap();
    // --- L-0001: clean framework lesson with synthetic reproducer ---
    let p1 = g.ok(&["upstream", "prepare", "L-0001"]);
    assert_eq!(p1["export_allowed"], true);
    assert_eq!(p1["packet_id"], "PKT-0001");
    let packet_path = p1["path"].as_str().unwrap().to_string();
    let e = g.err(&[
        "upstream",
        "submit",
        "PKT-0001",
        "--destination",
        inbox.to_str().unwrap(),
    ]);
    assert_eq!(
        e.error_code(),
        "HUMAN_GATE_REQUIRED",
        "human approval is required by LEARNING_POLICY"
    );
    let e2 = g.err(&[
        "upstream",
        "submit",
        "PKT-0001",
        "--destination",
        "https://example.invalid/inbox",
        "--approved-by",
        "owner",
    ]);
    assert_eq!(e2.error_code(), "REMOTE_TRANSPORT_NOT_CONFIGURED");
    let e3 = g.err(&[
        "upstream",
        "submit",
        "PKT-0001",
        "--destination",
        root.to_str().unwrap(),
        "--approved-by",
        "owner",
    ]);
    assert_eq!(e3.error_code(), "UPSTREAM_DESTINATION");
    let s = g.ok(&[
        "upstream",
        "submit",
        "PKT-0001",
        "--destination",
        inbox.to_str().unwrap(),
        "--approved-by",
        "owner",
    ]);
    assert_eq!(s["approved_by"], "owner");
    let dest = std::path::PathBuf::from(s["destination"].as_str().unwrap());
    assert!(dest.join("packet.yaml").exists() && dest.join("fixture/scenario.yaml").exists());
    let sent: Vec<String> = gov_runtime::paths::iter_repo_files(&dest, false)
        .into_iter()
        .map(|(_, r)| r)
        .collect();
    assert_eq!(
        sent.len(),
        2,
        "outbound allowlist: only packet.yaml + declared synthetic fixture files: {sent:?}"
    );
    assert!(read(&proj, "spec/reports/upstream-ledger.jsonl").contains("PKT-0001"));
    assert_eq!(
        yaml(&proj, "spec/lessons/L-0001.yaml")["lifecycle"],
        "promoted"
    );
    let pk = gov_runtime::util::read_yaml(&dest.join("packet.yaml")).unwrap();
    assert_eq!(pk["scope"], "FRAMEWORK");
    assert_eq!(pk["source_project_alias"], "proj-alpha");
    assert_eq!(pk["raw_product_code_included"], false);
    assert!(pk["payload_hash"].as_str().unwrap().len() == 64);
    let _ = packet_path;
    // --- L-0002: project scope is never eligible ---
    assert_eq!(
        g.err(&["upstream", "prepare", "L-0002"]).error_code(),
        "UPSTREAM_SCOPE"
    );
    // --- L-0003: secrets + customer + raw code + product path → fail closed ---
    let b = g.err(&["upstream", "prepare", "L-0003"]);
    assert_eq!(b.error_code(), "UPSTREAM_BLOCKED");
    let reasons = b.details()["reasons"].to_string();
    assert!(
        reasons.contains("secret pattern") && reasons.contains("code line"),
        "{reasons}"
    );
    let blocked_dir = proj.join(".governance-runtime/outbound/PKT-0002");
    assert!(blocked_dir.join("blocked.json").exists() && !blocked_dir.join("packet.yaml").exists());
    // --- L-0004: identifiers redacted ---
    let p4 = g.ok(&["upstream", "prepare", "L-0004"]);
    assert!(
        p4["scans"]["identifiers_redacted"].as_u64().unwrap() >= 2,
        "{}",
        p4["scans"]
    );
    let text = read(&proj, ".governance-runtime/outbound/PKT-0003/packet.yaml");
    assert!(
        !text.contains("Acme") && !text.contains("shipping-quotes"),
        "identifiers must be redacted: {text}"
    );
    g.ok(&[
        "upstream",
        "submit",
        "PKT-0003",
        "--destination",
        inbox.to_str().unwrap(),
        "--approved-by",
        "owner",
    ]);
    // --- inbox never contains secrets, customer or project identifiers, or product code ---
    for (abs, rel) in gov_runtime::paths::iter_repo_files(&inbox, false) {
        let t = std::fs::read_to_string(&abs).unwrap();
        for bad in ["AKIA", "Acme", "shipping-quotes", "gateway.py", "sk_live"] {
            assert!(!t.contains(bad), "{rel} leaked '{bad}'");
        }
    }
    // --- fixture file under a forbidden outbound path is blocked ---
    let mut l5 = yaml(&proj, "spec/lessons/L-0001.yaml");
    l5["id"] = json!("L-0005");
    l5["synthetic_reproducer"]["files"] = json!({"product/api/leak.py": "print(1)"});
    write_yaml(&proj, "spec/lessons/L-0005.yaml", &l5);
    let b5 = g.err(&["upstream", "prepare", "L-0005"]);
    assert_eq!(b5.error_code(), "UPSTREAM_BLOCKED");
    assert!(b5.details()["reasons"]
        .to_string()
        .contains("forbidden outbound path"));
}

/// Repair-1 WS-11 regression (builder evidence, not acceptance), BC-P2-50: the export gate fails closed on what would
/// leave — repository content (renamed, re-indented with CRLF, excerpted, hex-encoded, raw spec) and derived-index data
/// (chunk ids, a short run of a stored embedding, an embedding-length number array) — whatever the fixture is called and
/// although it declares `synthetic: true`; a genuinely synthetic fixture still passes; a packet edited after prepare
/// cannot be submitted; the approval is recorded as the unauthenticated channel it is, bound to the packet.
#[test]
fn export_gate_fails_closed_on_content_whatever_the_name() {
    let root = tmp("upstream-content");
    let proj = root.join("project");
    std::fs::create_dir_all(&proj).unwrap();
    write(&proj, "README.md", "# svc\n");
    write(
        &proj,
        "src/billing.rs",
        "pub fn quote_cents(weight_grams: u64, zone: char) -> u64 {\n    let base = match zone { 'A' => 350, 'B' => 420, _ => 610 };\n    base + weight_grams / 100 * 17\n}\n\npub fn surcharge_for_remote_postcodes(postcode: &str) -> u64 {\n    if postcode.starts_with(\"IV\") || postcode.starts_with(\"HS\") { 250 } else { 0 }\n}\n",
    );
    write(
        &proj,
        "spec/requirements/REQ-0001.yaml",
        "id: REQ-0001\ntype: requirement\ntitle: Remote postcode surcharge\nstatus: ACTIVE\nstatement: Deliveries to Highlands and Islands postcodes carry a 2.50 surcharge on every quote.\n",
    );
    git_init_commit(&proj);
    let g = Gov::new(&proj, "S-up");
    g.ok(&["init", "--name", "svc", "--alias", "proj-beta"]);
    g.ok(&["rebuild-memory"]);
    let lesson = |id: &str, files: serde_json::Value| {
        json!({"id": id, "type": "lesson", "title": "t", "status": "ACTIVE", "scope": "FRAMEWORK", "lifecycle": "corroborated", "category": "c",
            "problem_statement": "p", "generic_failure_mode": "g", "impact": "i", "suggested_change": "s", "sources": ["RPT-1"],
            "synthetic_reproducer": {"synthetic": true, "description": "d", "files": files}})
    };
    let src = read(&proj, "src/billing.rs");
    let db = gov_runtime::memory::db::RuntimeDb::open(&proj.join(".governance-runtime/state.db"))
        .unwrap();
    let chunk_id = db
        .query(
            "SELECT chunk_id FROM chunks WHERE chunk_id LIKE 'file:src/%' LIMIT 1",
            &[],
        )
        .unwrap()[0]["chunk_id"]
        .as_str()
        .unwrap()
        .to_string();
    let vec: Vec<f64> = serde_json::from_str(
        db.query(
            "SELECT vec FROM vectors WHERE chunk_id LIKE 'file:src/%' LIMIT 1",
            &[],
        )
        .unwrap()[0]["vec"]
            .as_str()
            .unwrap(),
    )
    .unwrap();
    // the 12-value window of the stored vector with the most non-zero components (short of the length rule)
    let best = (0..vec.len().saturating_sub(12))
        .max_by_key(|i| vec[*i..*i + 12].iter().filter(|x| **x != 0.0).count())
        .unwrap();
    let window: Vec<String> = vec[best..best + 12]
        .iter()
        .map(|x| format!("{x}"))
        .collect(); // zeros print as `0`
    let hex: String = src.bytes().map(|b| format!("{b:02x}")).collect();
    let excerpt: String = src.lines().skip(5).take(3).collect::<Vec<_>>().join("\n");
    let many: Vec<String> = (0..96).map(|i| format!("0.{:03}", i * 7 % 997)).collect();
    let cases: Vec<(&str, serde_json::Value, &str)> = vec![
        (
            "L-0101",
            json!({"example.txt": src.clone()}),
            "copy of project file",
        ),
        (
            "L-0102",
            json!({"repro/billing.rs": src.replace('\n', "\r\n").replace("    ", "\t")}),
            "raw project content",
        ),
        (
            "L-0103",
            json!({"snippet.rs": excerpt}),
            "raw project content",
        ),
        (
            "L-0104",
            json!({"req.yaml": read(&proj, "spec/requirements/REQ-0001.yaml")}),
            "project",
        ),
        ("L-0105", json!({"blob.txt": hex}), "opaque"),
        (
            "L-0106",
            json!({"ids.txt": format!("see {chunk_id} for context")}),
            "chunk id",
        ),
        (
            "L-0107",
            json!({"vec.json": format!("[{}]", window.join(", "))}),
            "embedding vector",
        ),
        (
            "L-0108",
            json!({"numbers.json": format!("[{}]", many.join(","))}),
            "numbers",
        ),
    ];
    for (id, files, why) in &cases {
        write_yaml(
            &proj,
            &format!("spec/lessons/{id}.yaml"),
            &lesson(id, files.clone()),
        );
        let o = g.err(&["upstream", "prepare", id]);
        assert_eq!(o.error_code(), "UPSTREAM_BLOCKED", "{id}");
        let reasons = o.details()["reasons"].to_string();
        assert!(reasons.contains(why), "{id}: expected '{why}' in {reasons}");
    }
    // control: a genuinely synthetic reproducer passes
    write_yaml(
        &proj,
        "spec/lessons/L-0110.yaml",
        &lesson(
            "L-0110",
            json!({"scenario.yaml": "steps:\n  - create a record and index it\n  - change the record after indexing\n  - attempt to close the task\n"}),
        ),
    );
    let ok = g.ok(&["upstream", "prepare", "L-0110"]);
    let pkt = ok["packet_id"].as_str().unwrap().to_string();
    // a packet edited after prepare is refused at submission
    let inbox = root.join("canonical").join("lessons").join("inbox");
    std::fs::create_dir_all(&inbox).unwrap();
    let pp = format!(".governance-runtime/outbound/{pkt}/packet.yaml");
    let original = read(&proj, &pp);
    let mut tampered = yaml(&proj, &pp);
    tampered["synthetic_fixture"]["files"]["scenario.yaml"] = json!(src.clone());
    write_yaml(&proj, &pp, &tampered);
    let e = g.err(&[
        "upstream",
        "submit",
        &pkt,
        "--destination",
        inbox.to_str().unwrap(),
        "--approved-by",
        "owner",
    ]);
    assert_eq!(e.error_code(), "UPSTREAM_BLOCKED");
    write(&proj, &pp, &original);
    let s = g.ok(&[
        "upstream",
        "submit",
        &pkt,
        "--destination",
        inbox.to_str().unwrap(),
        "--approved-by",
        "owner",
    ]);
    assert_eq!(s["approval"]["authenticated"], false);
    assert_eq!(s["approval"]["binds"]["packet_id"], pkt.as_str());
    assert_eq!(s["approval"]["binds"]["payload_hash"], s["payload_hash"]);
}
