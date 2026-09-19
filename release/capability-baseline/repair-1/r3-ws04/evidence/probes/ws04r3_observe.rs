//! P2-AR-0035 (WS-4, repair-1 round 3) — OBSERVATIONAL supplementary probe. EVIDENCE ONLY, not product code, not part
//! of the product's certification suite.
//!
//! It is compiled into a scratch copy of a tree's certification harness (`tests/certification/`, which it uses for
//! provisioning, signed installs and the owner-signed human channel) by `run-observe.sh`, and run against that tree's
//! own `gov` binary: once for the base tree (53897c1, the integrated round-2 tree) as the negative control and once
//! for this branch. It never asserts: every line is `OBSERVE <id> PASS|FAIL <detail>`, and each FAIL on the base with
//! a PASS on this branch is a before/after pair measured with the same code.
use crate::common::*;
use serde_json::{json, Value};
use std::path::Path;

fn obs(id: &str, pass: bool, detail: impl std::fmt::Display) {
    println!(
        "OBSERVE {id} {} {detail}",
        if pass { "PASS" } else { "FAIL" }
    );
}

fn fresh(tag: &str) -> (std::path::PathBuf, Gov) {
    let (root, g) = setup_fixture("greenfield", tag, "S-obs");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        tag,
        "--alias",
        &format!("a-{tag}"),
    ]);
    write_yaml(
        &root,
        "spec/features/F-0001.yaml",
        &json!({"id": "F-0001", "type": "feature", "title": "Totals", "status": "ACTIVE", "state_class": "AUTHORITATIVE", "requirements": ["REQ-0001"], "scenarios": ["SCN-0001"], "readiness": {"requirements": "PRESENT"}}),
    );
    write_yaml(
        &root,
        "spec/requirements/REQ-0001.yaml",
        &json!({"id": "REQ-0001", "type": "requirement", "title": "Totals are exact", "status": "ACTIVE", "state_class": "AUTHORITATIVE", "feature": "F-0001", "kind": "functional", "statement": "totals are integer cents", "acceptance_criteria": ["2 x 199 = 398"]}),
    );
    write_yaml(
        &root,
        "spec/requirements/REQ-0002.yaml",
        &json!({"id": "REQ-0002", "type": "requirement", "title": "Refunds are logged", "status": "ACTIVE", "state_class": "AUTHORITATIVE", "kind": "functional", "statement": "every refund is logged"}),
    );
    write_yaml(
        &root,
        "spec/scenarios/SCN-0001.yaml",
        &json!({"id": "SCN-0001", "type": "scenario", "title": "Cart total", "status": "ACTIVE", "state_class": "AUTHORITATIVE", "feature": "F-0001", "requirements": ["REQ-0001"], "then": ["total is 398"]}),
    );
    git_commit_all(&root, "spec");
    g.ok(&["rebuild-memory"]);
    (root, g)
}

fn mf(root: &Path, name: &str, ops: Value) -> String {
    let f = root
        .join(".governance-runtime")
        .join(format!("{name}.json"));
    std::fs::create_dir_all(f.parent().unwrap()).unwrap();
    std::fs::write(&f, ops.to_string()).unwrap();
    f.to_string_lossy().to_string()
}

fn edit(root: &Path, rel: &str, f: impl FnOnce(&mut Value)) {
    let mut v = yaml(root, rel);
    f(&mut v);
    write_yaml(root, rel, &v);
}

fn rid(v: &Value) -> String {
    v["id"].as_str().unwrap_or("").to_string()
}

fn auto_cit(g: &Gov, root: &Path, tag: &str, path: &str, content: &str) -> (String, String) {
    let m = mf(
        root,
        tag,
        json!([{"op": "write_file", "path": path, "content": content}]),
    );
    let c = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        &format!("docs {tag}"),
        "--trigger",
        "editorial",
        "--manifest",
        &m,
    ]);
    let cid = rid(&c);
    g.ok(&["cit", "simulate", &cid]);
    let ap = g.ok(&["cit", "approve", &cid, "--method", "auto"]);
    (cid, ap["decision"].as_str().unwrap_or("").to_string())
}

fn gated_cit(g: &Gov, root: &Path, tag: &str, ops: Value) -> String {
    let m = mf(root, tag, ops);
    let c = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        &format!("change {tag}"),
        "--trigger",
        "behaviour_change",
        "--manifest",
        &m,
    ]);
    let cid = rid(&c);
    let gate = c["simulation"]["human_gate"]
        .as_str()
        .unwrap_or("")
        .to_string();
    g.ok(&["gate", "present", &gate]);
    crate::ws03::human_decide(g, &gate, "A");
    g.ok(&["cit", "approve", &cid, "--method", "human"]);
    cid
}

fn sealed_field(root: &Path, rel: &str) -> bool {
    yaml(root, rel)["os_binding"].is_object()
}

/// The `os_binding_integrity` findings `gov audit` reports for `id`.
fn t2_findings(g: &Gov, id: &str) -> Vec<String> {
    let a = g.run(&["audit", "--no-persist"]);
    let res = if a.ok() { a.result() } else { a.details() };
    res["findings"]
        .as_array()
        .cloned()
        .unwrap_or_default()
        .iter()
        .filter(|f| f["family"] == "os_binding_integrity")
        .filter_map(|f| f["message"].as_str().map(String::from))
        .filter(|m| m.contains(id))
        .collect()
}

#[test]
fn obs_a_cit_records_and_rollback_decisions() {
    let (root, g) = fresh("obs-a");
    let (c1, d1) = auto_cit(&g, &root, "c1", "docs/guide.md", "guide\n");
    let r1 = format!("spec/decisions/{c1}.yaml");
    obs("A1-cit-record-sealed-after-approve", sealed_field(&root, &r1), format!("{r1} os_binding present: {}", sealed_field(&root, &r1)));
    g.ok(&["cit", "execute", &c1]);
    obs("A2-committed-cit-record-sealed", sealed_field(&root, &r1), format!("{r1} os_binding: {}", yaml(&root, &r1)["os_binding"]["operation"]));
    // WS-2 R3-1 on a gate-derived decision (the kind os_binding_integrity audits)
    let cg = gated_cit(
        &g,
        &root,
        "g1",
        json!([{"op": "set_field", "target": "REQ-0002", "field": "statement", "value": "every refund is logged with its reason"}]),
    );
    let dg = g.ok(&["cit", "show", &cg])["decision"].as_str().unwrap_or("").to_string();
    g.ok(&["cit", "execute", &cg]);
    let rb = g.run(&["cit", "rollback", &cg, "--reason", "observe"]);
    let st = yaml(&root, &format!("spec/decisions/{dg}.yaml"))["status"].clone();
    let f = t2_findings(&g, &dg);
    obs("A3-rollback-decision-rejected", st == "REJECTED", format!("{dg} status {st}; rollback ok={}", rb.ok()));
    obs("A4-rollback-decision-not-reported-as-tampering", f.is_empty(), format!("os_binding_integrity findings naming {dg}: {f:?}"));
    // the automatic approval decision after rollback
    let rb1 = g.run(&["cit", "rollback", &c1, "--reason", "observe"]);
    obs("A5-auto-decision-resealed-by-rollback", rb1.result()["approval_decision"]["resealed"] == true, format!("rollback result approval_decision: {}", rb1.result()["approval_decision"]));
    let _ = d1;
    // a hand-removed secret flag
    let m = mf(
        &root,
        "sec",
        json!([{"op": "write_file", "path": "docs/keys.md", "content": "key AKIAIOSFODNN7EXAMPLE\n"}]),
    );
    let s = g.ok(&["cit", "propose", "--proposal", "keys", "--trigger", "editorial", "--manifest", &m]);
    let cs = rid(&s);
    g.ok(&["cit", "simulate", &cs]);
    g.ok(&["cit", "approve", &cs, "--method", "auto"]);
    edit(&root, &format!("spec/decisions/{cs}.yaml"), |c| {
        let o = c.as_object_mut().unwrap();
        o.remove("secret_flagged");
        o.remove("blocked_reasons");
    });
    let e = g.run(&["cit", "execute", &cs]);
    obs("A6-hand-removed-secret-flag-still-refused", !e.ok() && e.error_code() == "SECRET_IN_MANIFEST" && !exists(&root, "docs/keys.md"),
        format!("execute ok={} code={} docs/keys.md written={}", e.ok(), e.error_code(), exists(&root, "docs/keys.md")));
}

#[test]
fn obs_b_direct_propagation_and_concurrent_close() {
    let (root, g) = fresh("obs-b");
    write_yaml(
        &root,
        "spec/tasks/TST-0001.yaml",
        &json!({"id": "TST-0001", "type": "test-obligation", "title": "totals unit tests", "status": "ACTIVE", "family": "unit", "scenario": "SCN-0001", "requirements": ["REQ-0001"]}),
    );
    git_commit_all(&root, "obligation");
    g.ok(&["rebuild-memory", "--incremental"]);
    let task = |objective: &str, reqs: &[&str]| -> String {
        let f = json!({"requirements": reqs}).to_string();
        rid(&g.ok(&["task", "create", "--objective", objective, "--class", "discovery", "--status", "READY", "--allowed", "src/**", "--fields", &f]))
    };
    let a = task("totals", &["REQ-0001"]);
    g.ok(&["context", "compile", &a]);
    g.ok(&["task", "claim", &a]);
    write(&root, "src/totals.rs", "pub fn t() -> i64 { 398 }\n");
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep = crate::ws05::receipt(&g, &root, &a, "a", "totals", &["src/totals.rs"], "not_applicable_with_reason");
    let closed = g.ok(&["task", "close", &a, "--report", &rep]);
    let rpt = closed["report"].as_str().unwrap_or("").to_string();
    edit(&root, "spec/requirements/REQ-0001.yaml", |d| {
        d["statement"] = json!("totals are integer cents, rounded half-even")
    });
    git_commit_all(&root, "direct edit");
    g.ok(&["rebuild-memory", "--incremental"]);
    let b = task("refund log", &["REQ-0002"]);
    g.ok(&["context", "compile", &b]);
    g.ok(&["task", "claim", &b]);
    let pr = g.run(&["cit", "propagate"]);
    let res = pr.result();
    obs("B1-direct-propagation-recorded-as-transaction", res["cit"].is_string(), format!("propagate ok={} cit={} touched={}", pr.ok(), res["cit"], res["touched"]));
    let rp = format!("spec/reports/{rpt}.yaml");
    let f = t2_findings(&g, &rpt);
    obs("B2-marked-sealed-report-not-reported-as-tampering", f.is_empty() && yaml(&root, &rp)["staleness"]["stale"] == true, format!("report stale={} findings={f:?}", yaml(&root, &rp)["staleness"]["stale"]));
    write(&root, "src/refunds.rs", "pub fn log() {}\n");
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep_b = crate::ws05::receipt(&g, &root, &b, "b", "refund log", &["src/refunds.rs"], "not_applicable_with_reason");
    let cb = g.run(&["task", "close", &b, "--report", &rep_b]);
    obs("B3-concurrent-close-not-charged-with-propagation-marks", cb.ok(), format!("close ok={} code={} details={}", cb.ok(), cb.error_code(), cb.details()["t2_violations"].to_string() + &cb.details()["violations"].to_string()));
}

#[test]
fn obs_c_snapshots_manifest_receipt_edges_links_materiality() {
    let (root, g) = fresh("obs-c");
    // C1 snapshots in the BC-P2-31 store; rollback after deleting the derived runtime directory
    let (c, _) = auto_cit(&g, &root, "s1", "docs/snap.md", "snap\n");
    g.ok(&["cit", "execute", &c]);
    obs("C1-snapshot-in-state-store", exists(&root, &format!(".governance-state/cit/{c}/snapshot.json")), format!("state store: {}, runtime dir: {}", exists(&root, &format!(".governance-state/cit/{c}/snapshot.json")), exists(&root, &format!(".governance-runtime/cit/{c}/snapshot.json"))));
    let _ = std::fs::remove_dir_all(root.join(".governance-runtime"));
    let rb = g.run(&["cit", "rollback", &c, "--reason", "observe"]);
    obs("C2-rollback-survives-deleting-runtime-dir", rb.ok() && !exists(&root, "docs/snap.md"), format!("rollback ok={} code={}", rb.ok(), rb.error_code()));
    g.ok(&["rebuild-memory"]);
    // C3 producer rule in the manifest; C4 non-governed evidence flagged
    write_yaml(&root, "spec/features/F-0002.yaml", &json!({"id": "F-0002", "type": "feature", "title": "Refunds", "status": "ACTIVE", "state_class": "AUTHORITATIVE", "requirements": ["REQ-0002", "REQ-0999"], "readiness": {"requirements": "MISSING"}}));
    write_yaml(&root, "spec/research/RES-0001.yaml", &json!({"id": "RES-0001", "type": "research", "title": "refund patterns", "status": "ACTIVE", "state_class": "NARRATIVE", "question": "how do others log refunds?"}));
    git_commit_all(&root, "feature");
    let st = rid(&g.ok(&["task", "create", "--objective", "write refund requirements", "--class", "specification", "--feature", "F-0002", "--fields", &json!({"derived_from": ["RES-0001"]}).to_string()]));
    let m = g.ok(&["context", "manifest", &st]);
    obs("C3-producer-manifest-complete", m["delivery_state"] == "COMPLETE", format!("delivery_state {} missing {}", m["delivery_state"], m["missing_inputs"]));
    let res = m["inputs"].as_array().cloned().unwrap_or_default().into_iter().find(|e| e["id"] == "RES-0001").unwrap_or(json!({}));
    obs("C4-ungoverned-research-flagged", res["authority_flag"] == "EVIDENCE_NOT_GOVERNED", format!("RES-0001 authority_flag {}", res["authority_flag"]));
    // C5 untraceable implementation judged on what was produced
    let t = rid(&g.ok(&["task", "create", "--objective", "spike", "--class", "implementation", "--allowed", "src/**"]));
    let pk = g.ok(&["context", "compile", &t]);
    let f = root.join(".governance-runtime/obs-r.json");
    std::fs::write(&f, json!({"context_packet_hash": pk["packet_hash"], "inputs_consumed": [], "outputs_produced": [], "requirements_implemented": [], "scenarios_implemented": [], "decisions_applied": [], "acceptance_evidence": [], "deviations": ["nothing needed"], "unresolved": []}).to_string()).unwrap();
    let r = g.ok(&["context", "receipt", &t, "--file", f.to_str().unwrap()]);
    obs("C5-no-output-not-untraceable", !r["errors"].to_string().contains("UNTRACEABLE_IMPLEMENTATION"), format!("errors {}", r["errors"]));
    // C6 relation edges: scenario -> data requirement, decision -> cited evidence
    write_yaml(&root, "spec/data/DATA-0001.yaml", &json!({"id": "DATA-0001", "type": "data", "title": "refund amounts", "status": "ACTIVE", "data_kind": "requirement"}));
    edit(&root, "spec/scenarios/SCN-0001.yaml", |s| { s["data_requirements"] = json!(["DATA-0001"]); });
    write_yaml(&root, "spec/decisions/D-0050.yaml", &json!({"id": "D-0050", "type": "decision", "title": "log format", "status": "ACTIVE", "chosen_option": "A", "evidence_refs": ["RES-0001"]}));
    let e1 = g.ok(&["artefact", "show", "SCN-0001"])["edges"].to_string();
    let e2 = g.ok(&["artefact", "show", "D-0050"])["edges"].to_string();
    obs("C6-scenario-consumes-data-requirement", e1.contains("\"CONSUMES\"") && e1.contains("DATA-0001"), format!("SCN-0001 edges {e1}"));
    obs("C7-decision-derived-from-cited-evidence", e2.contains("DERIVED_FROM") && e2.contains("RES-0001"), format!("D-0050 edges {e2}"));
    // C8 a finished transaction's links are not stale links
    write_yaml(&root, "spec/requirements/REQ-0077.yaml", &json!({"id": "REQ-0077", "type": "requirement", "title": "old", "status": "SUPERSEDED", "superseded_by": "REQ-0001", "state_class": "AUTHORITATIVE", "kind": "functional"}));
    write_yaml(&root, "spec/decisions/CIT-0099.yaml", &json!({"id": "CIT-0099", "type": "cit", "title": "retired REQ-0077", "status": "ACTIVE", "cit_status": "COMMITTED", "proposal": "retire", "mutation_manifest": [], "targets": ["REQ-0077"]}));
    let ck = g.ok(&["artefact", "check"]);
    let from_cit = ck["stale_links"].as_array().cloned().unwrap_or_default().iter().any(|s| s["record"] == "CIT-0099");
    obs("C8-finished-cit-links-not-stale", !from_cit, format!("stale links from CIT-0099: {from_cit}"));
    // C9 a retrieval-profile pin change is named in CIT-P materiality
    let pp = read(&root, "governance/project/PROJECT_POLICY.yaml").replace("policy_overrides: {}", "policy_overrides: {\"MEMORY_POLICY.embedding.provider\": \"plugin:local-embed\"}");
    write(&root, "governance/project/PROJECT_POLICY.yaml", &pp);
    let cl = g.ok(&["cit", "classify", "--paths", "governance/project/PROJECT_POLICY.yaml"]);
    obs("C9-retrieval-profile-pins-named", cl.to_string().contains("retrieval profile pins"), format!("findings {}", cl["materiality"]["findings"]));
    // C10 product release record type
    write_yaml(&root, "spec/releases/REL-0001.yaml", &json!({"id": "REL-0001", "type": "release", "title": "1.0.0", "status": "ACTIVE", "version": "1.0.0", "derived_from": [t], "validated_by": ["AUD-0001"]}));
    let a = g.ok(&["artefact", "show", "REL-0001"]);
    obs("C10-release-record-has-canonical-location", a["canonical_dir"] == "spec/releases", format!("canonical_dir {}", a["canonical_dir"]));
    // C11 checkpoint and handoff records are sealed
    let ckp = g.ok(&["checkpoint", "create", "--next-action", "observe"]);
    let path = format!("spec/reports/checkpoints/{}.yaml", ckp["id"].as_str().unwrap_or(""));
    obs("C11-checkpoint-sealed", sealed_field(&root, &path), format!("{path} os_binding present: {}", sealed_field(&root, &path)));
}

#[test]
fn obs_d_gated_integrity_and_experiment() {
    let (root, g) = fresh("obs-d");
    write_yaml(&root, "spec/tasks/TST-0001.yaml", &json!({"id": "TST-0001", "type": "test-obligation", "title": "totals unit tests", "status": "ACTIVE", "family": "unit", "scenario": "SCN-0001"}));
    let bytes = "def charge():\n    return 'async'\n";
    write(&root, "spec/experiments/EXP-0001/charge.py", bytes);
    write_yaml(&root, "spec/experiments/EXP-0001.yaml", &json!({"id": "EXP-0001", "type": "experiment", "title": "async charge", "status": "ACTIVE", "experiment_state": "DESIGNED", "state_class": "NARRATIVE",
        "hypothesis": "async halves p95", "method": "A/B on staging", "data_provenance": "staging traffic replay", "production_merge_allowed": false, "outputs": ["spec/experiments/EXP-0001/**"]}));
    git_commit_all(&root, "fixtures");
    g.ok(&["rebuild-memory", "--incremental"]);
    let bad = gated_cit(&g, &root, "rev", json!([{"op": "append_record", "record": {"id": "REQ-0003", "type": "requirement", "title": "Receipts", "status": "ACTIVE", "state_class": "AUTHORITATIVE", "kind": "functional", "statement": "receipts are printed", "tests": ["TST-0001"]}}]));
    let e = g.run(&["cit", "execute", &bad]);
    obs("D1-reversed-relationship-rolls-back", !e.ok() && e.error_code() == "VERIFICATION_FAILED" && !exists(&root, "spec/requirements/REQ-0003.yaml"),
        format!("execute ok={} code={} REQ-0003 present={}", e.ok(), e.error_code(), exists(&root, "spec/requirements/REQ-0003.yaml")));
    let m = mf(&root, "exp", json!([{"op": "write_file", "path": "src/charge.py", "content": bytes}]));
    let c = g.ok(&["cit", "propose", "--proposal", "adopt async charge", "--trigger", "behaviour_change", "--manifest", &m]);
    let gate = c["simulation"]["human_gate"].as_str().unwrap_or("").to_string();
    g.ok(&["gate", "present", &gate]);
    crate::ws03::human_decide(&g, &gate, "A");
    let ap = g.run(&["cit", "approve", &rid(&c), "--method", "human"]);
    let mut executed = false;
    if ap.ok() {
        executed = g.run(&["cit", "execute", &rid(&c)]).ok();
    }
    obs("D2-experimental-output-needs-promotion", !ap.ok() && ap.error_code() == "EXPERIMENT_NOT_PROMOTED",
        format!("approve ok={} code={}; executed={executed}; src/charge.py present={}", ap.ok(), ap.error_code(), exists(&root, "src/charge.py")));
}
