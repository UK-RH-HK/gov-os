//! WS-4, repair iteration 1, round 3 (P2-AR-0035): builder regression tests for sealing and lineage completeness —
//! every CIT write sealed (WS-5 IP-R3-2), the OS re-seal rule for every OS write into a sealed record (integration
//! O-7, WS-2 R3-1, WS-5 IP-R3-1/-3), direct propagation recorded as a sealed system transaction, relationship
//! integrity at CIT-E (WS-6 IP-R2-2), rollback snapshots in the BC-P2-31 store (WS-6 IP-R2-10), experimental output
//! and CIT approval (WS-10 IP-WS10-09), the producer rule and non-governed evidence in the manifest (WS-5 IP-R3-4,
//! WS-10 IP-WS10-10) and untraceable implementation judged on what was produced (WS-5 IP-R3-5). Black-box through
//! the `gov` JSON contract; human answers go through the owner-signed channel (`crate::ws03`). Regression evidence
//! only (Contract v3 O3).
use crate::common::*;
use serde_json::{json, Value};
use std::path::Path;

fn fresh(tag: &str) -> (std::path::PathBuf, Gov) {
    let (root, g) = setup_fixture("greenfield", tag, "S-r3");
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

fn id(v: &Value) -> String {
    v["id"].as_str().unwrap().to_string()
}

/// The T2 binding of record `rid` as `gov artefact show` reports it: (`VERIFIED`|`BROKEN`|..., sealing operation).
fn seal(g: &Gov, rid: &str) -> (String, String) {
    let a = g.ok(&["artefact", "show", rid]);
    (
        a["t2_binding"]["binding"]
            .as_str()
            .unwrap_or("")
            .to_string(),
        a["t2_binding"]["operation"]
            .as_str()
            .unwrap_or("")
            .to_string(),
    )
}

/// `record_seal` of CIT `cid` in `gov cit list`.
fn cit_seal(g: &Gov, cid: &str) -> String {
    g.ok(&["cit", "list"])
        .as_array()
        .unwrap()
        .iter()
        .find(|c| c["id"] == cid)
        .map(|c| c["record_seal"].as_str().unwrap_or("").to_string())
        .unwrap_or_default()
}

/// Propose an editorial CIT writing `path` (R0: approvable on the automatic path) and approve it.
fn auto_cit(g: &Gov, root: &Path, tag: &str, path: &str, content: &str) -> (String, String) {
    let mf = manifest(
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
        &mf,
    ]);
    let cid = id(&c);
    assert_eq!(cit_seal(g, &cid), "VERIFIED", "propose seals the record");
    g.ok(&["cit", "simulate", &cid]);
    assert_eq!(
        cit_seal(g, &cid),
        "VERIFIED",
        "simulate re-seals the record"
    );
    let ap = g.ok(&["cit", "approve", &cid, "--method", "auto"]);
    assert_eq!(cit_seal(g, &cid), "VERIFIED", "approve re-seals the record");
    (cid, ap["decision"].as_str().unwrap().to_string())
}

/// Propose a CIT whose manifest is `ops`, answer its human gate and approve it.
fn gated_cit(g: &Gov, root: &Path, tag: &str, ops: Value) -> String {
    let mf = manifest(root, tag, ops);
    let c = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        &format!("change {tag}"),
        "--trigger",
        "behaviour_change",
        "--manifest",
        &mf,
    ]);
    let cid = id(&c);
    let gate = c["simulation"]["human_gate"]
        .as_str()
        .unwrap_or_else(|| panic!("{tag}: no gate raised: {c}"))
        .to_string();
    g.ok(&["gate", "present", &gate]);
    crate::ws03::human_decide(g, &gate, "A");
    g.ok(&["cit", "approve", &cid, "--method", "human"]);
    cid
}

/// WS-5 IP-R3-2, WS-2 R3-1, integration O-7: every CIT write seals the whole record; rollback re-seals the approval
/// decision it marks REJECTED — only when that decision's seal verified before; a hand edit is never re-sealed; the
/// secret-material flag is bound into the sealed state.
#[test]
fn every_cit_write_is_sealed_and_a_hand_edit_stays_broken() {
    let (root, g) = fresh("ws4r3-seal");
    // propose / simulate / approve (asserted in auto_cit) and execute
    let (c1, d1) = auto_cit(&g, &root, "c1", "docs/guide.md", "guide\n");
    assert_eq!(
        seal(&g, &d1).0,
        "VERIFIED",
        "the automatic approval decision is sealed"
    );
    let ex = g.ok(&["cit", "execute", &c1]);
    assert_eq!(ex["cit_status"], "COMMITTED", "{ex}");
    let (b, op) = seal(&g, &c1);
    assert_eq!(b, "VERIFIED");
    assert!(op.starts_with("cit execute"), "{op}");
    // R3-1: the rollback marks the approval decision REJECTED and re-seals it as its own write
    let rb = g.ok(&["cit", "rollback", &c1, "--reason", "test"]);
    assert_eq!(rb["approval_decision"]["resealed"], true, "{rb}");
    assert_eq!(
        yaml(&root, &format!("spec/decisions/{d1}.yaml"))["status"],
        "REJECTED"
    );
    assert_eq!(seal(&g, &d1), ("VERIFIED".into(), "cit rollback".into()));
    assert_eq!(cit_seal(&g, &c1), "VERIFIED");
    // a decision edited by hand before the rollback is marked REJECTED but never blessed
    let (c2, d2) = auto_cit(&g, &root, "c2", "docs/guide2.md", "guide 2\n");
    edit(&root, &format!("spec/decisions/{d2}.yaml"), |d| {
        d["rationale"] = json!("rewritten by hand")
    });
    assert_eq!(seal(&g, &d2).0, "BROKEN");
    g.ok(&["cit", "execute", &c2]);
    let rb2 = g.ok(&["cit", "rollback", &c2, "--reason", "test"]);
    assert_eq!(rb2["approval_decision"]["resealed"], false, "{rb2}");
    assert_eq!(
        yaml(&root, &format!("spec/decisions/{d2}.yaml"))["status"],
        "REJECTED"
    );
    assert_eq!(
        seal(&g, &d2).0,
        "BROKEN",
        "the OS does not bless a hand edit"
    );
    // a committed transaction's touched list edited by hand: the record is broken and no operation re-seals it
    let (c3, _) = auto_cit(&g, &root, "c3", "docs/guide3.md", "guide 3\n");
    g.ok(&["cit", "execute", &c3]);
    edit(&root, &format!("spec/decisions/{c3}.yaml"), |c| {
        c["execution"]["propagation"]["touched"]
            .as_array_mut()
            .unwrap()
            .push(json!("src/lib.rs"))
    });
    assert_eq!(cit_seal(&g, &c3), "BROKEN");
    g.ok(&["cit", "propagate"]);
    g.ok(&["rebuild-memory", "--incremental"]);
    assert_eq!(cit_seal(&g, &c3), "BROKEN");
    // the secret flag is sealed: removing it from the record by hand does not release the transaction
    let mf = manifest(
        &root,
        "sec",
        json!([{"op": "write_file", "path": "docs/keys.md", "content": "key AKIAIOSFODNN7EXAMPLE\n"}]),
    );
    let s = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        "keys",
        "--trigger",
        "editorial",
        "--manifest",
        &mf,
    ]);
    let cs = id(&s);
    assert_eq!(s["secret_flagged"], true, "{s}");
    g.ok(&["cit", "simulate", &cs]);
    g.ok(&["cit", "approve", &cs, "--method", "auto"]);
    edit(&root, &format!("spec/decisions/{cs}.yaml"), |c| {
        let o = c.as_object_mut().unwrap();
        o.remove("secret_flagged");
        o.remove("blocked_reasons");
    });
    assert_eq!(
        g.err(&["cit", "execute", &cs]).error_code(),
        "SECRET_IN_MANIFEST"
    );
    assert!(!exists(&root, "docs/keys.md"));
}

/// Integration O-7 (manifest ops): a governed change re-seals a sealed record it modifies when the OS may seal what
/// it wrote (a decision's lifecycle), and leaves unsealed — recorded in its touched list — a rewrite of how a
/// decision was derived.
#[test]
fn a_governed_change_reseals_only_what_the_os_may_seal() {
    let (root, g) = fresh("ws4r3-reseal");
    let (_, d1) = auto_cit(&g, &root, "a1", "docs/a1.md", "a1\n");
    let (_, d2) = auto_cit(&g, &root, "a2", "docs/a2.md", "a2\n");
    assert_eq!(seal(&g, &d1).0, "VERIFIED");
    // lifecycle: superseding the sealed decision is re-sealed as the transaction's write
    let cs = gated_cit(
        &g,
        &root,
        "sup",
        json!([{"op": "set_status", "target": d1, "value": "SUPERSEDED", "by": d2}]),
    );
    let ex = g.ok(&["cit", "execute", &cs]);
    let seals = &ex["propagation"]["t2_seals"];
    let p1 = format!("spec/decisions/{d1}.yaml");
    assert!(
        seals["resealed"]
            .as_array()
            .unwrap()
            .iter()
            .any(|x| x == p1.as_str()),
        "{seals}"
    );
    let (b, op) = seal(&g, &d1);
    assert_eq!(b, "VERIFIED");
    assert_eq!(op, format!("cit execute {cs}: set_status"));
    assert!(ex["propagation"]["touched"]
        .as_array()
        .unwrap()
        .iter()
        .any(|x| x == p1.as_str()));
    // derivation: rewriting the answer a sealed decision records is recorded, never sealed as the OS's own
    let cf = gated_cit(
        &g,
        &root,
        "opt",
        json!([{"op": "set_field", "target": d2, "field": "chosen_option", "value": "B"}]),
    );
    let ex = g.ok(&["cit", "execute", &cf]);
    let p2 = format!("spec/decisions/{d2}.yaml");
    assert!(
        ex["propagation"]["t2_seals"]["left_unsealed"]
            .as_array()
            .unwrap()
            .iter()
            .any(|x| x["path"] == p2.as_str()),
        "{ex}"
    );
    assert!(ex["propagation"]["touched"]
        .as_array()
        .unwrap()
        .iter()
        .any(|x| x == p2.as_str()));
    assert_eq!(seal(&g, &d2).0, "BROKEN");
}

/// WS-5 IP-R3-3 (direct path): propagating a change made outside CIT-E is recorded as a sealed system transaction
/// whose touched list and per-path writes cover what it marked, so a task claimed before the propagation closes with
/// its own work only; a sealed close report it marks is re-sealed; a second run records nothing.
#[test]
fn direct_propagation_is_a_sealed_system_transaction_that_covers_its_marks() {
    let (root, g) = fresh("ws4r3-direct");
    // an authored test obligation validating REQ-0001
    write_yaml(
        &root,
        "spec/tasks/TST-0001.yaml",
        &json!({"id": "TST-0001", "type": "test-obligation", "title": "totals unit tests", "status": "ACTIVE", "family": "unit", "scenario": "SCN-0001", "requirements": ["REQ-0001"]}),
    );
    git_commit_all(&root, "obligation");
    g.ok(&["rebuild-memory", "--incremental"]);
    // round-3 integration (P2-AR-0041): the work writes product source (`src/**`), so it is a source-changing class
    // (`refactor`), not `discovery` — WS-5's in-task material-change hook (BC-P2-13, `tasks::material_changes`) refuses
    // a behaviour change of product source by a class not contracted to change it, exactly as WS-5 updated
    // `ws04r2::upstream_change_reaches_completed_work`. What this test asserts (the system transaction and its
    // coverage) is unchanged.
    let task = |objective: &str, reqs: &[&str]| -> String {
        let f = json!({"requirements": reqs}).to_string();
        id(&g.ok(&[
            "task",
            "create",
            "--objective",
            objective,
            "--class",
            "refactor",
            "--status",
            "READY",
            "--allowed",
            "src/**",
            "--fields",
            &f,
        ]))
    };
    // completed work that consumed REQ-0001 (its close report is sealed)
    let a = task("totals", &["REQ-0001"]);
    g.ok(&["context", "compile", &a]);
    g.ok(&["task", "claim", &a]);
    write(&root, "src/totals.rs", "pub fn t() -> i64 { 398 }\n");
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep = crate::ws05::receipt(
        &g,
        &root,
        &a,
        "a",
        "totals",
        &["src/totals.rs"],
        "not_applicable_with_reason",
    );
    let closed = g.ok(&["task", "close", &a, "--report", &rep]);
    let rpt = closed["report"].as_str().unwrap().to_string();
    assert_eq!(seal(&g, &rpt).0, "VERIFIED");
    // an upstream change made outside change control, committed before other work starts
    edit(&root, "spec/requirements/REQ-0001.yaml", |d| {
        d["statement"] = json!("totals are integer cents, rounded half-even")
    });
    git_commit_all(&root, "direct edit");
    // round 4 (P2-AR-0043, INT3-O2): a direct change observed by a host-run index rebuild is propagated by that
    // rebuild (G1), when it is observed. The round-3 integration observed the next claim's propagation here, because
    // the rebuild did not propagate; now the rebuild does, recorded exactly as `gov cit propagate` records it: one
    // sealed system transaction. The pending change is visible beforehand (dry run), the rebuild reports it, every
    // property below is asserted on that transaction, the next claim finds nothing left to propagate (the claim-time
    // path is kept: `ws05r3::stale_inputs_are_seen_propagated_at_claim_and_cleared_only_by_retest_evidence`), and a
    // later `gov cit propagate` finds nothing either.
    let pending = g.ok(&["cit", "propagate", "--dry-run"]);
    assert!(pending["changes"].as_u64().unwrap_or(0) > 0, "{pending}");
    let rb = g.ok(&["rebuild-memory", "--incremental"]);
    assert_eq!(rb["upstream_changes"]["propagated"], true, "{rb}");
    let b = task("refund log", &["REQ-0002"]);
    g.ok(&["context", "compile", &b]);
    let cl = g.ok(&["task", "claim", &b]);
    assert_ne!(cl["upstream_changes"]["propagated"], true, "{cl}");
    let sys = g
        .ok(&["cit", "list"])
        .as_array()
        .unwrap()
        .iter()
        .find(|c| c["origin"] == "system")
        .map(|c| c["id"].as_str().unwrap().to_string())
        .expect("the rebuild's propagation is recorded as a sealed system transaction");
    assert_eq!(rb["upstream_changes"]["cit"], json!(sys), "{rb}");
    let rec = g.ok(&["cit", "show", &sys]);
    assert_eq!(rec["origin"], "system", "{rec}");
    assert_eq!(rec["cit_status"], "COMMITTED");
    assert_eq!(rec["mutation_manifest"], json!([]));
    assert_eq!(cit_seal(&g, &sys), "VERIFIED");
    let touched: Vec<String> = rec["execution"]["propagation"]["touched"]
        .as_array()
        .unwrap()
        .iter()
        .map(|x| x.as_str().unwrap().to_string())
        .collect();
    for want in [
        "spec/tasks/TST-0001.yaml",
        "spec/scenarios/SCN-0001.yaml",
        &format!("spec/reports/{rpt}.yaml"),
    ] {
        assert!(
            touched.iter().any(|t| t == want),
            "{want} not in {touched:?}"
        );
    }
    // the writes are content-bound: each recorded hash is the file's content now
    for w in rec["execution"]["writes"].as_array().unwrap() {
        let path = w["path"].as_str().unwrap();
        if let Some(h) = w["sha256"].as_str() {
            assert_eq!(
                gov_runtime::util::sha256_hex(&std::fs::read(root.join(path)).unwrap()),
                h,
                "{path}"
            );
        }
    }
    // the sealed close report marked stale is re-sealed as the propagation's write; the authored obligation is
    // marked but not sealed (the OS does not seal content it did not write)
    assert_eq!(
        yaml(&root, &format!("spec/reports/{rpt}.yaml"))["staleness"]["stale"],
        true
    );
    assert_eq!(
        seal(&g, &rpt),
        ("VERIFIED".into(), "cit propagation".into())
    );
    assert_eq!(
        yaml(&root, "spec/tasks/TST-0001.yaml")["staleness"]["stale"],
        true
    );
    assert_ne!(seal(&g, "TST-0001").0, "VERIFIED");
    // the task claimed after the propagation closes with its own work only: the OS's marks are not its mutations
    write(&root, "src/refunds.rs", "pub fn log() {}\n");
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep_b = crate::ws05::receipt(
        &g,
        &root,
        &b,
        "b",
        "refund log",
        &["src/refunds.rs"],
        "not_applicable_with_reason",
    );
    let cb = g.ok(&["task", "close", &b, "--report", &rep_b]);
    assert_eq!(cb["task_status"], "DONE", "{cb}");
    // idempotent: nothing left to propagate, no second transaction
    let again = g.ok(&["cit", "propagate"]);
    assert_eq!(again["changes"], 0, "{again}");
    let systems = g
        .ok(&["cit", "list"])
        .as_array()
        .unwrap()
        .iter()
        .filter(|c| c["origin"] == "system")
        .count();
    assert_eq!(systems, 1);
}

/// WS-6 IP-R2-2: CIT-E judges relationship integrity before and after the manifest. A relationship the transaction
/// itself declares in the wrong direction fails the verification and rolls back; a stale link of other work to a
/// record the transaction superseded is its propagation's consequence and does not.
#[test]
fn cit_e_rolls_back_relationships_it_introduces_but_not_their_consequences() {
    let (root, g) = fresh("ws4r3-integrity");
    write_yaml(
        &root,
        "spec/tasks/TST-0001.yaml",
        &json!({"id": "TST-0001", "type": "test-obligation", "title": "totals unit tests", "status": "ACTIVE", "family": "unit", "scenario": "SCN-0001"}),
    );
    git_commit_all(&root, "obligation");
    g.ok(&["rebuild-memory", "--incremental"]);
    // a requirement that "tests" a test obligation is a relationship recorded the wrong way round
    let bad = gated_cit(
        &g,
        &root,
        "rev",
        json!([{"op": "append_record", "record": {"id": "REQ-0003", "type": "requirement", "title": "Receipts", "status": "ACTIVE", "state_class": "AUTHORITATIVE", "kind": "functional", "statement": "receipts are printed", "tests": ["TST-0001"]}}]),
    );
    let e = g.err(&["cit", "execute", &bad]);
    assert_eq!(e.error_code(), "VERIFICATION_FAILED", "{}", e.envelope);
    assert!(
        e.envelope["error"]["message"]
            .as_str()
            .unwrap()
            .contains("relationship integrity"),
        "{}",
        e.envelope
    );
    assert!(!exists(&root, "spec/requirements/REQ-0003.yaml"));
    // superseding a requirement other work still names commits; the stale links are reported as consequences
    let f = json!({"requirements": ["REQ-0002"]}).to_string();
    let t = id(&g.ok(&[
        "task",
        "create",
        "--objective",
        "refunds",
        "--class",
        "discovery",
        "--fields",
        &f,
    ]));
    git_commit_all(&root, "task");
    let sup = gated_cit(
        &g,
        &root,
        "sup",
        json!([
            {"op": "append_record", "record": {"id": "REQ-0004", "type": "requirement", "title": "Refunds are logged and signed", "status": "ACTIVE", "state_class": "AUTHORITATIVE", "kind": "functional", "statement": "every refund is logged and signed", "supersedes": ["REQ-0002"]}},
            {"op": "set_status", "target": "REQ-0002", "value": "SUPERSEDED", "by": "REQ-0004"}
        ]),
    );
    let ex = g.ok(&["cit", "execute", &sup]);
    assert_eq!(ex["cit_status"], "COMMITTED", "{ex}");
    let ri = &ex["propagation"]["relationship_integrity"];
    assert_eq!(ri["introduced"], json!([]), "{ri}");
    assert!(
        ri["consequences"]
            .as_array()
            .unwrap()
            .iter()
            .any(|f| f["record"] == t.as_str()),
        "{ri}"
    );
}

/// BC-P2-31 (WS-6 IP-R2-10): rollback snapshots are non-rebuildable state in the OS store, a legacy snapshot tree is
/// relocated there, and deleting the derived runtime directory does not lose the rollback.
#[test]
fn rollback_snapshots_survive_deleting_the_derived_runtime_directory() {
    let (root, g) = fresh("ws4r3-snap");
    std::fs::create_dir_all(root.join(".governance-runtime/cit/CIT-0099/snapshot")).unwrap();
    write(
        &root,
        ".governance-runtime/cit/CIT-0099/snapshot.json",
        "{\"cit\": \"CIT-0099\", \"files\": [], \"created_paths\": []}\n",
    );
    let (c, _) = auto_cit(&g, &root, "s1", "docs/snap.md", "snap\n");
    g.ok(&["cit", "execute", &c]);
    assert!(exists(
        &root,
        &format!(".governance-state/cit/{c}/snapshot.json")
    ));
    assert!(exists(
        &root,
        ".governance-state/cit/CIT-0099/snapshot.json"
    ));
    assert!(!exists(&root, ".governance-runtime/cit"));
    let (_, st) = git(&root, &["status", "--porcelain"]);
    assert!(!st.contains(".governance-state"), "{st}");
    std::fs::remove_dir_all(root.join(".governance-runtime")).unwrap();
    let rb = g.ok(&[
        "cit",
        "rollback",
        &c,
        "--reason",
        "runtime directory deleted",
    ]);
    assert_eq!(rb["cit_status"], "ROLLED_BACK");
    assert!(!exists(&root, "docs/snap.md"), "{rb}");
}

/// WS-10 IP-WS10-09 (Contract v3 J2): a CIT that carries experimental output into the production tree is refused at
/// approve unless an approved promotion covers the path, whatever the gate answered.
#[test]
fn experimental_output_reaches_production_only_through_a_promotion() {
    let (root, g) = fresh("ws4r3-exp");
    let bytes = "def charge():\n    return 'async'\n";
    write(&root, "spec/experiments/EXP-0001/charge.py", bytes);
    write_yaml(
        &root,
        "spec/experiments/EXP-0001.yaml",
        &json!({"id": "EXP-0001", "type": "experiment", "title": "async charge", "status": "ACTIVE", "experiment_state": "DESIGNED", "state_class": "NARRATIVE",
            "hypothesis": "async halves p95", "method": "A/B on staging", "data_provenance": "staging traffic replay", "production_merge_allowed": false,
            "outputs": ["spec/experiments/EXP-0001/**"]}),
    );
    git_commit_all(&root, "experiment");
    g.ok(&["rebuild-memory", "--incremental"]);
    let cid = {
        let mf = manifest(
            &root,
            "exp",
            json!([{"op": "write_file", "path": "src/charge.py", "content": bytes}]),
        );
        let c = g.ok(&[
            "cit",
            "propose",
            "--proposal",
            "adopt async charge",
            "--trigger",
            "behaviour_change",
            "--manifest",
            &mf,
        ]);
        let gate = c["simulation"]["human_gate"].as_str().unwrap().to_string();
        g.ok(&["gate", "present", &gate]);
        crate::ws03::human_decide(&g, &gate, "A");
        id(&c)
    };
    let e = g.err(&["cit", "approve", &cid, "--method", "human"]);
    assert_eq!(e.error_code(), "EXPERIMENT_NOT_PROMOTED", "{}", e.envelope);
    assert!(!exists(&root, "src/charge.py"));
    // other bytes are not experimental output: the same path is approvable
    let other = gated_cit(
        &g,
        &root,
        "own",
        json!([{"op": "write_file", "path": "src/charge2.py", "content": "def charge():\n    return 'sync'\n"}]),
    );
    assert_eq!(g.ok(&["cit", "execute", &other])["cit_status"], "COMMITTED");
}

/// WS-5 IP-R3-4 and WS-10 IP-WS10-10: the manifest itself applies the producer rule, and flags research that is not
/// governed evidence.
#[test]
fn the_manifest_applies_the_producer_rule_and_flags_ungoverned_evidence() {
    let (root, g) = fresh("ws4r3-manifest");
    write_yaml(
        &root,
        "spec/features/F-0002.yaml",
        &json!({"id": "F-0002", "type": "feature", "title": "Refunds", "status": "ACTIVE", "state_class": "AUTHORITATIVE", "requirements": ["REQ-0002", "REQ-0999"], "readiness": {"requirements": "MISSING"}}),
    );
    write_yaml(
        &root,
        "spec/research/RES-0001.yaml",
        &json!({"id": "RES-0001", "type": "research", "title": "refund patterns", "status": "ACTIVE", "state_class": "NARRATIVE", "question": "how do others log refunds?"}),
    );
    git_commit_all(&root, "feature");
    let spec_task = id(&g.ok(&[
        "task",
        "create",
        "--objective",
        "write the missing refund requirements",
        "--class",
        "specification",
        "--feature",
        "F-0002",
        "--status",
        "READY",
        "--fields",
        &json!({"derived_from": ["RES-0001"]}).to_string(),
    ]));
    let m = g.ok(&["context", "manifest", &spec_task]);
    assert_eq!(m["delivery_state"], "COMPLETE", "{m}");
    let missing = m["inputs"]
        .as_array()
        .unwrap()
        .iter()
        .find(|e| e["id"] == "REQ-0999")
        .unwrap()
        .clone();
    assert_eq!(missing["required"], false, "{missing}");
    assert!(missing["problems"]
        .to_string()
        .contains("INHERITED_INPUT_UNSATISFIED"));
    let res = m["inputs"]
        .as_array()
        .unwrap()
        .iter()
        .find(|e| e["id"] == "RES-0001")
        .unwrap()
        .clone();
    assert_eq!(res["authority_flag"], "EVIDENCE_NOT_GOVERNED", "{res}");
    // the DAG agrees: the producer is stored READY, the feature's implementation work is not
    assert_eq!(g.ok(&["task", "show", &spec_task])["task_status"], "READY");
    let impl_task = g.ok(&[
        "task",
        "create",
        "--objective",
        "implement refunds",
        "--class",
        "implementation",
        "--feature",
        "F-0002",
        "--status",
        "READY",
    ]);
    assert_ne!(impl_task["task_status"], "READY", "{impl_task}");
    assert_eq!(
        g.ok(&["context", "manifest", &id(&impl_task)])["delivery_state"],
        "BLOCKED"
    );
}

/// WS-5 IP-R3-5 (W5 line 1125): untraceable implementation is judged on implementation that was produced, not on the
/// task's class alone.
#[test]
fn untraceable_implementation_is_judged_on_what_was_produced() {
    let (root, g) = fresh("ws4r3-trace");
    let t = id(&g.ok(&[
        "task",
        "create",
        "--objective",
        "spike",
        "--class",
        "implementation",
        "--allowed",
        "src/**",
    ]));
    let pk = g.ok(&["context", "compile", &t]);
    let receipt = |outputs: Value| -> String {
        let f = root.join(".governance-runtime").join(format!(
            "r-{}.json",
            outputs.as_array().map(|a| a.len()).unwrap_or(0)
        ));
        std::fs::write(
            &f,
            json!({"context_packet_hash": pk["packet_hash"], "inputs_consumed": [], "outputs_produced": outputs,
                "requirements_implemented": [], "scenarios_implemented": [], "decisions_applied": [], "acceptance_evidence": [],
                "deviations": ["no production change was needed"], "unresolved": []})
            .to_string(),
        )
        .unwrap();
        f.to_string_lossy().to_string()
    };
    let nothing = g.ok(&["context", "receipt", &t, "--file", &receipt(json!([]))]);
    assert!(
        !nothing["errors"]
            .to_string()
            .contains("UNTRACEABLE_IMPLEMENTATION"),
        "{nothing}"
    );
    assert!(nothing["warnings"]
        .to_string()
        .contains("NO_IMPLEMENTATION_PRODUCED"));
    let produced = g.ok(&[
        "context",
        "receipt",
        &t,
        "--file",
        &receipt(json!(["src/lib.rs"])),
    ]);
    assert!(
        produced["errors"]
            .to_string()
            .contains("UNTRACEABLE_IMPLEMENTATION"),
        "{produced}"
    );
}

/// **Integration point IP-R3-WS04-01 (WS-3, `gates.rs`)** — un-ignored at the round-3 integration (P2-AR-0041), with
/// `cit` in `t2::SEALED_RECORD_TYPES`. A gate operation that writes a CIT record (`gates::answer` records the decision
/// and marks a declined transaction REJECTED; `gates::revoke` returns it to SIMULATED) re-seals the record when its
/// seal verified before the write — WS-3's round-3 `t2::seal_if_verified(c, was_verified, "gate answer (cit)")`, the
/// same rule as `cit::binding::reseal_if_verified(c, was_verified, true, ..)` — as every other OS writer does (O-7).
/// So a CIT declined inside another task's claim window leaves a verifying seal on the OS-managed path, and that task's
/// close is not refused as a T2 violation it did not commit.
#[test]
fn a_cit_declined_during_another_tasks_claim_does_not_block_its_close() {
    let (root, g) = fresh("ws4r3-decline");
    let f = json!({"requirements": ["REQ-0002"]}).to_string();
    // the work writes product source: a source-changing class (WS-5's BC-P2-13 hook refuses `discovery` there)
    let t = id(&g.ok(&[
        "task",
        "create",
        "--objective",
        "refund log",
        "--class",
        "refactor",
        "--status",
        "READY",
        "--allowed",
        "src/**",
        "--fields",
        &f,
    ]));
    g.ok(&["context", "compile", &t]);
    g.ok(&["task", "claim", &t]);
    let mf = manifest(
        &root,
        "decline",
        json!([{"op": "set_field", "target": "REQ-0001", "field": "statement", "value": "totals are floats"}]),
    );
    let c = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        "floats",
        "--trigger",
        "behaviour_change",
        "--manifest",
        &mf,
    ]);
    let cid = id(&c);
    let gate = c["simulation"]["human_gate"].as_str().unwrap().to_string();
    g.ok(&["gate", "present", &gate]);
    crate::ws03::human_decide(&g, &gate, "B");
    assert_eq!(
        cit_seal(&g, &cid),
        "VERIFIED",
        "the gate's write re-sealed the CIT"
    );
    write(&root, "src/refunds.rs", "pub fn log() {}\n");
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep = crate::ws05::receipt(
        &g,
        &root,
        &t,
        "t",
        "refund log",
        &["src/refunds.rs"],
        "not_applicable_with_reason",
    );
    assert_eq!(
        g.ok(&["task", "close", &t, "--report", &rep])["task_status"],
        "DONE"
    );
}
