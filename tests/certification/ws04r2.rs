//! WS-4, repair iteration 1, round 2 (P2-AR-0025): builder regression tests for BC-P2-11 (CIT side), BC-P2-13
//! (CIT-P side), BC-P2-04, BC-P2-05 and BC-P2-18 (detection side). Black-box through the `gov` JSON contract; human
//! answers go through the owner-signed channel (`crate::ws03`). Regression evidence only (Contract v3 O3).
use crate::common::*;
use serde_json::{json, Value};
use std::path::Path;

fn spec(root: &Path, g: &Gov) {
    write_yaml(
        root,
        "spec/features/F-0001.yaml",
        &json!({"id": "F-0001", "type": "feature", "title": "Totals", "status": "ACTIVE", "state_class": "AUTHORITATIVE", "requirements": ["REQ-0001"], "scenarios": ["SCN-0001"], "readiness": {"requirements": "PRESENT"}}),
    );
    write_yaml(
        root,
        "spec/requirements/REQ-0001.yaml",
        &json!({"id": "REQ-0001", "type": "requirement", "title": "Totals are exact", "status": "ACTIVE", "state_class": "AUTHORITATIVE", "feature": "F-0001", "kind": "functional", "statement": "totals are integer cents", "acceptance_criteria": ["2 x 199 = 398"]}),
    );
    write_yaml(
        root,
        "spec/scenarios/SCN-0001.yaml",
        &json!({"id": "SCN-0001", "type": "scenario", "title": "Cart total", "status": "ACTIVE", "state_class": "AUTHORITATIVE", "feature": "F-0001", "requirements": ["REQ-0001"], "then": ["total is 398"]}),
    );
    git_commit_all(root, "spec");
    g.ok(&["rebuild-memory"]);
}

fn manifest(root: &Path, name: &str, ops: Value) -> String {
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

/// BC-P2-11 (CIT side): an approval binds the exact transaction content, its simulated impact and the CIT.
#[test]
fn cit_approval_binds_content_impact_and_transaction() {
    let (root, g) = setup_fixture("greenfield", "ws04r2-bind", "S-bind");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "b",
        "--alias",
        "b-alias",
    ]);
    spec(&root, &g);
    let mf = manifest(
        &root,
        "m1",
        json!([{"op": "set_field", "target": "REQ-0001", "field": "statement", "value": "rounded half-even"}]),
    );
    let c = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        "rounding",
        "--trigger",
        "behaviour_change",
        "--targets",
        "REQ-0001",
        "--manifest",
        &mf,
    ]);
    let cid = c["id"].as_str().unwrap().to_string();
    let gate = c["simulation"]["human_gate"].as_str().unwrap().to_string();
    let binding = c["simulation"]["impact"]["binding_sha256"]
        .as_str()
        .unwrap()
        .to_string();
    assert_eq!(
        g.ok(&["gate", "show", &gate])["gate"]["subject"]["sha256"],
        binding.as_str(),
        "the gate's subject (inside the signed package) is the transaction+impact digest"
    );
    crate::ws03::human_decide(&g, &gate, "A");
    // the manifest changes after the human answered: the answer does not approve it
    let rel = format!("spec/decisions/{cid}.yaml");
    edit(&root, &rel, |d| {
        d["mutation_manifest"]
            .as_array_mut()
            .unwrap()
            .push(json!({"op": "write_file", "path": "governance/project/X.md", "content": "x\n"}))
    });
    assert_eq!(
        g.err(&["cit", "approve", &cid, "--method", "human"])
            .error_code(),
        "APPROVAL_STALE"
    );
    // re-simulating the changed transaction raises a new gate: the old answer cannot approve it
    let sim = g.ok(&["cit", "simulate", &cid]);
    let gate2 = sim["human_gate"].as_str().unwrap().to_string();
    assert_ne!(gate2, gate, "{sim}");
    assert_eq!(sim["impact"]["radius"], "R5");
    assert_eq!(
        g.err(&["cit", "approve", &cid, "--method", "human"])
            .error_code(),
        "GATE_NOT_PRESENTED"
    );
    // answered and approved, then the recorded approval is replaced by hand: execution refuses and writes nothing
    crate::ws03::human_decide(&g, &gate2, "A");
    g.ok(&["cit", "approve", &cid, "--method", "human"]);
    edit(&root, &rel, |d| {
        d["approval"]["recorded_by"] = json!("someone else")
    });
    assert_eq!(
        g.err(&["cit", "execute", &cid]).error_code(),
        "APPROVAL_STALE"
    );
    assert!(!exists(&root, "governance/project/X.md"));
    // a transaction whose sealed state was removed is not one gov wrote
    edit(&root, &rel, |d| {
        d.as_object_mut().unwrap().remove("os_state");
    });
    assert_eq!(g.err(&["cit", "execute", &cid]).error_code(), "T2_UNBOUND");
}

/// BC-P2-13 (CIT-P side): materiality is derived from what a change touches; the label cannot lower it.
#[test]
fn materiality_is_derived_not_labelled() {
    let (root, g) = setup_fixture("greenfield", "ws04r2-mat", "S-mat");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "m",
        "--alias",
        "m-alias",
    ]);
    spec(&root, &g);
    write(
        &root,
        "src/auth.rs",
        "pub fn authorise(t: &str) -> bool { verify_signature(t) }\n",
    );
    write(
        &root,
        "infra/main.tf",
        "resource \"db\" { instance_class = \"small\" }\n",
    );
    git_commit_all(&root, "code");
    g.ok(&["rebuild-memory", "--incremental"]);
    for (tag, ops, class) in [
        (
            "sec",
            json!([{"op": "write_file", "path": "src/auth.rs", "content": "pub fn authorise(_t: &str) -> bool { true }\n"}]),
            "security_change",
        ),
        (
            "infra",
            json!([{"op": "write_file", "path": "infra/main.tf", "content": "resource \"db\" { instance_class = \"8xlarge\" }\n"}]),
            "infrastructure_cost",
        ),
        (
            "crit",
            json!([{"op": "set_field", "target": "SCN-0001", "field": "then", "value": ["total is 400"]}]),
            "acceptance_criteria_change",
        ),
    ] {
        let mf = manifest(&root, tag, ops);
        let c = g.ok(&[
            "cit",
            "propose",
            "--proposal",
            "tidy wording",
            "--trigger",
            "editorial",
            "--manifest",
            &mf,
        ]);
        assert!(
            c["materiality"]["derived_classes"]
                .as_array()
                .unwrap()
                .iter()
                .any(|x| x == class),
            "{tag}: {}",
            c["materiality"]
        );
        assert_eq!(
            c["auto_simulated"], true,
            "{tag}: a material change is simulated automatically whatever its label"
        );
        assert_eq!(
            c["simulation"]["impact"]["human_gate_required"], true,
            "{tag}: {}",
            c["simulation"]["impact"]
        );
    }
    let mf = manifest(
        &root,
        "doc",
        json!([{"op": "write_file", "path": "docs/guide.md", "content": "typo\n"}]),
    );
    let c = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        "typo",
        "--trigger",
        "editorial",
        "--manifest",
        &mf,
    ]);
    assert_eq!(c["materiality"]["derived_classes"], json!([]));
    // changes already performed in the working tree: the task-close detection API
    write(
        &root,
        "src/auth.rs",
        "pub fn authorise(t: &str) -> bool { !t.is_empty() }\n",
    );
    let r = g.ok(&["cit", "classify", "--paths", "src/auth.rs"]);
    assert!(
        r["materiality"]["requires_cit_in_task"]
            .as_array()
            .unwrap()
            .iter()
            .any(|f| f["class"] == "security_change"),
        "{r}"
    );
}

/// BC-P2-04: an upstream change reaches completed work, its evidence, packets and checkpoints, through CIT-E and
/// when made directly; propagation is idempotent.
#[test]
fn upstream_change_reaches_completed_work() {
    let (root, g) = setup_fixture("greenfield", "ws04r2-prop", "S-prop");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "p",
        "--alias",
        "p-alias",
    ]);
    spec(&root, &g);
    let fields = json!({"requirements": ["REQ-0001"], "scenarios": ["SCN-0001"]}).to_string();
    let done = g.ok(&[
        "task",
        "create",
        "--objective",
        "implement totals",
        "--class",
        "discovery",
        "--status",
        "READY",
        "--allowed",
        "src/**",
        "--fields",
        &fields,
    ])["id"]
        .as_str()
        .unwrap()
        .to_string();
    let open = g.ok(&[
        "task",
        "create",
        "--objective",
        "tune totals",
        "--class",
        "discovery",
        "--status",
        "READY",
        "--allowed",
        "src/**",
        "--fields",
        &fields,
    ])["id"]
        .as_str()
        .unwrap()
        .to_string();
    g.ok(&["context", "compile", &done]);
    g.ok(&["task", "claim", &done]);
    write(&root, "src/totals.rs", "pub fn t() -> i64 { 398 }\n");
    g.ok(&["rebuild-memory", "--incremental"]);
    // round-2 integration (P2-AR-0032): WS-5 (BC-P2-20) — the close report is the consumption receipt of the
    // packet's receipt_contract; with WS-2's close gate (BC-P2-43) a `passed` claim needs recorded product-test
    // evidence, which this scenario never runs, so the report states `not_applicable_with_reason` (WS-5's convention)
    let rep = crate::ws05::receipt(
        &g,
        &root,
        &done,
        "done",
        "totals",
        &["src/totals.rs"],
        "not_applicable_with_reason",
    );
    let closed = g.ok(&["task", "close", &done, "--report", &rep]);
    g.ok(&["context", "compile", &open]);
    let ck = g.ok(&[
        "checkpoint",
        "create",
        "--task",
        &open,
        "--next-action",
        "continue",
    ]);
    let mf = manifest(
        &root,
        "crit",
        json!([{"op": "set_field", "target": "REQ-0001", "field": "acceptance_criteria", "value": ["2 x 199 = 400"]}]),
    );
    let c = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        "round",
        "--trigger",
        "acceptance_criteria_change",
        "--targets",
        "REQ-0001",
        "--manifest",
        &mf,
    ]);
    let cid = c["id"].as_str().unwrap().to_string();
    crate::ws03::human_decide(&g, c["simulation"]["human_gate"].as_str().unwrap(), "A");
    g.ok(&["cit", "approve", &cid, "--method", "human"]);
    let ex = g.ok(&["cit", "execute", &cid]);
    let prop = &ex["propagation"];
    assert!(
        prop["revalidation_required"]
            .as_array()
            .unwrap()
            .iter()
            .any(|t| t == done.as_str()),
        "{prop}"
    );
    let reval = prop["revalidation_tasks"][0]["task"]
        .as_str()
        .unwrap()
        .to_string();
    assert_eq!(
        g.ok(&["task", "show", &reval])["revalidates"],
        done.as_str()
    );
    assert_eq!(g.ok(&["task", "show", &done])["retest_required"], true);
    assert_eq!(
        yaml(
            &root,
            &format!("spec/reports/{}.yaml", closed["report"].as_str().unwrap())
        )["staleness"]["stale"],
        true
    );
    assert_eq!(
        yaml(&root, "spec/scenarios/SCN-0001.yaml")["staleness"]["stale"],
        true,
        "validation evidence of the changed criterion is stale at R1"
    );
    assert_eq!(
        yaml(
            &root,
            &format!(
                "spec/reports/checkpoints/{}.yaml",
                ck["id"].as_str().unwrap()
            )
        )["staleness"]["stale"],
        true
    );
    assert!(
        !json(&root, &format!(".governance-runtime/context/{open}.json"))["invalidated"].is_null()
    );
    // idempotent: nothing left to propagate, nothing generated twice
    let n = g.ok(&["task", "list"]).as_array().unwrap().len();
    assert_eq!(g.ok(&["cit", "propagate"])["changes"], 0);
    assert_eq!(g.ok(&["task", "list"]).as_array().unwrap().len(), n);
    // a direct change, then an index rebuild: still detected from what the work consumed
    g.ok(&["context", "compile", &open]);
    edit(&root, "spec/requirements/REQ-0001.yaml", |d| {
        d["statement"] = json!("direct edit")
    });
    g.ok(&["rebuild-memory", "--incremental"]);
    let st = g.ok(&["context", "staleness", &open]);
    assert!(
        st["stale_inputs"]
            .as_array()
            .unwrap()
            .iter()
            .any(|x| x["id"] == "REQ-0001" && x["propagated"] == false),
        "{st}"
    );
    let pr = g.ok(&["cit", "propagate"]);
    assert_eq!(pr["propagated"], true, "{pr}");
    assert_eq!(
        g.ok(&["context", "staleness", &open])["stale_inputs"][0]["propagated"],
        true
    );
}

/// BC-P2-05: checkpoint staleness, handoff and session-close continuity, the watchdog observing boundaries itself.
#[test]
fn checkpoint_and_handoff_continuity() {
    let (root, g) = setup_fixture("greenfield", "ws04r2-cont", "S-cont");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "c",
        "--alias",
        "c-alias",
    ]);
    spec(&root, &g);
    let t1 = g.ok(&[
        "task",
        "create",
        "--objective",
        "totals",
        "--class",
        "discovery",
        "--status",
        "READY",
        "--allowed",
        "src/**",
        "--fields",
        &json!({"requirements": ["REQ-0001"]}).to_string(),
    ])["id"]
        .as_str()
        .unwrap()
        .to_string();
    let t2 = g.ok(&[
        "task",
        "create",
        "--objective",
        "refunds",
        "--class",
        "discovery",
        "--status",
        "READY",
        "--allowed",
        "src/**",
        "--fields",
        &json!({"requirements": ["REQ-9999"]}).to_string(),
    ])["id"]
        .as_str()
        .unwrap()
        .to_string();
    assert_eq!(
        g.err(&[
            "handoff",
            "create",
            "--to-role",
            "backend-engineer",
            "--task",
            &t2
        ])
        .error_code(),
        "HANDOFF_INPUTS_UNSATISFIED"
    );
    g.ok(&["context", "compile", &t1]);
    g.ok(&["task", "claim", &t1]);
    let ck = g.ok(&[
        "checkpoint",
        "create",
        "--task",
        &t1,
        "--next-action",
        "implement",
    ]);
    assert!(
        ck["inputs"]
            .as_array()
            .unwrap()
            .iter()
            .any(|i| i["id"] == "REQ-0001" && i["normative_hash"].is_string()),
        "{ck}"
    );
    assert!(ck["state_reference"]["governed_state_digest"].is_string());
    edit(&root, "spec/requirements/REQ-0001.yaml", |d| {
        d["statement"] = json!("changed after the packet")
    });
    assert_eq!(
        g.ok(&["checkpoint", "freshness", ck["id"].as_str().unwrap()])["state"],
        "STALE"
    );
    let h = g.ok(&[
        "handoff",
        "create",
        "--to-role",
        "backend-engineer",
        "--task",
        &t1,
    ]);
    assert_eq!(h["freshness"]["state"], "REFRESHED", "{h}");
    assert!(
        !h["degraded"].as_array().unwrap().is_empty(),
        "in-progress work on stale inputs: explicitly degraded"
    );
    assert_eq!(g.ok(&["task", "show", &t1])["retest_required"], true);
    assert_eq!(g.ok(&["checkpoint", "latest"])["trigger"], "before_handoff");
    let sc = g.ok(&["session", "close", "--task", &t2]);
    assert_eq!(sc["blocked"], false);
    assert!(!sc["degraded"].as_array().unwrap().is_empty(), "{sc}");
    for i in 0..26 {
        g.ok(&[
            "task",
            "create",
            "--objective",
            &format!("op {i}"),
            "--class",
            "discovery",
        ]);
    }
    let w = g.ok(&["checkpoint", "watchdog"]);
    assert_eq!(w["fired"], true, "{w}");
    assert!(w["observed"]["commands"].as_u64().unwrap() >= 25, "{w}");
}

/// BC-P2-18 (detection side): contradictions precedence cannot resolve are detected, never delivered as authority,
/// routed to a system gate, and resolved only by its verified answer.
#[test]
fn contradictions_are_blocked_and_routed() {
    let (root, g) = setup_fixture("greenfield", "ws04r2-contra", "S-contra");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "k",
        "--alias",
        "k-alias",
    ]);
    spec(&root, &g);
    write_yaml(
        &root,
        "spec/decisions/D-0103.yaml",
        &json!({"id": "D-0103", "type": "decision", "title": "Persist totals in Postgres", "status": "ACTIVE", "chosen_option": "postgres", "affects": ["F-0001"], "state_class": "AUTHORITATIVE"}),
    );
    write_yaml(
        &root,
        "spec/decisions/D-0104.yaml",
        &json!({"id": "D-0104", "type": "decision", "title": "Persist totals in MySQL", "status": "ACTIVE", "chosen_option": "mysql", "affects": ["F-0001"], "state_class": "AUTHORITATIVE"}),
    );
    git_commit_all(&root, "decisions");
    let t = g.ok(&[
        "task",
        "create",
        "--objective",
        "store totals",
        "--class",
        "discovery",
        "--status",
        "READY",
        "--feature",
        "F-0001",
    ])["id"]
        .as_str()
        .unwrap()
        .to_string();
    let m = g.ok(&["context", "manifest", &t]);
    assert_eq!(m["delivery_state"], "BLOCKED", "{m}");
    let pk = g.ok(&["context", "compile", &t]);
    let active: Vec<String> = pk["deterministic_authority"]["active_decisions"]
        .as_array()
        .unwrap()
        .iter()
        .map(|d| d["id"].as_str().unwrap().to_string())
        .collect();
    assert!(
        !active.contains(&"D-0103".to_string()) && !active.contains(&"D-0104".to_string()),
        "{active:?}"
    );
    let gate = pk["contradiction_routing"][0]["routed"]["gate"]
        .as_str()
        .unwrap()
        .to_string();
    assert_eq!(
        g.ok(&["gate", "show", &gate])["gate"]["trigger"],
        "contradiction"
    );
    assert!(
        g.ok(&["context", "compile", &t])
            .get("contradiction_routing")
            .is_none(),
        "routing is idempotent"
    );
    crate::ws03::human_decide(&g, &gate, "A");
    assert_eq!(
        g.ok(&["context", "manifest", &t])["delivery_state"],
        "COMPLETE"
    );
    let pk = g.ok(&["context", "compile", &t]);
    let active: Vec<String> = pk["deterministic_authority"]["active_decisions"]
        .as_array()
        .unwrap()
        .iter()
        .map(|d| d["id"].as_str().unwrap().to_string())
        .collect();
    assert!(
        active.contains(&"D-0103".to_string()) && !active.contains(&"D-0104".to_string()),
        "{active:?}"
    );
}
