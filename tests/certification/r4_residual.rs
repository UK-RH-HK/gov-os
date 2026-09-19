//! Repair iteration 1, round 4 (P2-AR-0043, handoff P2-HO-0042): the residual integration points over the round-3
//! integrated tree — INT3-O1 (a plugin registration inside a claimed task is carried out by a change transaction the
//! OS proposes, simulates and executes, so the close accepts it; Contract v3 K3 and F4 both hold), INT3-O2 (a direct
//! upstream change observed at an index rebuild is propagated there, G1), and the remaining builder IPs.
//!
//! Builder regression evidence (Contract v3 O3), not acceptance evidence. Black-box through the `gov` JSON contract on
//! the one provisioned-root harness; human answers only through the owner-signed channel (`ws03::human_decide`).
use crate::common::*;
use crate::ws05::receipt;
use serde_json::{json, Value};
use std::path::{Path, PathBuf};

fn fresh(tag: &str) -> (PathBuf, Gov) {
    let (root, g) = setup_fixture("greenfield", tag, "S-r4");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        tag,
        "--alias",
        &format!("a-{tag}"),
    ]);
    git_commit_all(&root, "after init");
    g.ok(&["rebuild-memory"]);
    (root, g)
}

fn create(g: &Gov, class: &str, objective: &str, allowed: &str) -> String {
    g.ok(&[
        "task",
        "create",
        "--class",
        class,
        "--objective",
        objective,
        "--status",
        "READY",
        "--allowed",
        allowed,
    ])["id"]
        .as_str()
        .unwrap()
        .to_string()
}

fn write_exec(root: &Path, rel: &str, text: &str) {
    write(root, rel, text);
    use std::os::unix::fs::PermissionsExt;
    std::fs::set_permissions(root.join(rel), std::fs::Permissions::from_mode(0o755)).unwrap();
}

const EMBED_OK: &str = r#"{"protocol":"gov-capability/1","ok":true,"provider":{"id":"p","version":"1"},"outputs":{"vectors":[],"dim":8}}"#;
const REGISTRY: &str = "governance/registry/plugin-registry.json";

/// An executable embed plugin at `tools/<id>.sh` and its hand-written descriptor at the registration location.
fn plugin(root: &Path, id: &str) -> PathBuf {
    write_exec(
        root,
        &format!("tools/{id}.sh"),
        &format!("#!/bin/sh\ncat >/dev/null\nprintf '%s\\n' '{EMBED_OK}'\n"),
    );
    let rel = format!("governance/project/plugins/{id}.yaml");
    write_yaml(
        root,
        &rel,
        &json!({"plugin_id": id, "capability": "embed", "version": "1", "command": ["sh", format!("tools/{id}.sh")]}),
    );
    root.join(rel)
}

fn register(g: &Gov, df: &Path) -> Value {
    g.ok(&["plugins", "register", "--descriptor", df.to_str().unwrap()])
}

fn sha256_file(root: &Path, rel: &str) -> String {
    gov_runtime::util::sha256_hex(&std::fs::read(root.join(rel)).unwrap())
}

/// **INT3-O1 (WS-5 × WS-7).** Contract v3 K3 ("auto-trigger for material security, governance/policy") and F4
/// ("elevated permissions reference an authoritative gate/decision; the descriptor cannot authorise itself") both
/// hold for a plugin registered inside a claimed task: `gov plugins register` proposes and simulates the
/// registration's change transaction itself (the worker files none), raises the execution approval gate naming that
/// transaction and its gate, writes nothing until **both** are answered, and then writes the registration only by
/// executing the transaction (CIT-E). The task then closes: its close accepts the descriptor on the transaction's
/// recorded writes. Bound to content: a later hand edit of the descriptor inside another task is refused at that
/// close as a material change outside change control.
#[test]
fn a_plugin_registered_inside_a_claimed_task_closes_on_its_os_proposed_change_transaction() {
    let (root, g) = fresh("r4-reg-close");
    let te = g.with_role("tooling-engineer").with_session("S-tool");
    let t = create(
        &g,
        "tooling",
        "register the p1 plugin",
        "tools/**,governance/project/plugins/**",
    );
    te.ok(&["task", "claim", &t]);
    let df = plugin(&root, "p1");
    let rel = "governance/project/plugins/p1.yaml";
    let hand_written = std::fs::read(&df).unwrap();

    // 1. the request: the OS proposes and simulates the change transaction (K3) and raises the execution approval
    let r = register(&te, &df);
    assert_eq!(r["registered"], false, "{r}");
    let exec_gate = r["human_gate"].as_str().unwrap().to_string();
    let ct = &r["change_transaction"];
    let cit = ct["cit"].as_str().unwrap().to_string();
    let change_gate = ct["human_gate"].as_str().unwrap().to_string();
    assert_ne!(exec_gate, change_gate, "{r}");
    assert_eq!(
        ct["cit_status"], "SIMULATED",
        "CIT-P ran automatically: {r}"
    );
    let trig = ct["effective_triggers"].to_string();
    assert!(
        trig.contains("governance_change") && trig.contains("security_change"),
        "a registration is a material governance and security change: {r}"
    );
    let c = yaml(&root, &format!("spec/decisions/{cit}.yaml"));
    assert_eq!(c["origin"], "system", "{c}");
    assert_eq!(c["system"]["kind"], "plugin-registration", "{c}");
    assert_eq!(c["mutation_manifest"][0]["op"], "register_plugin", "{c}");
    assert_eq!(
        c["mutation_manifest"][0]["subject_sha256"], r["registration_subject_sha256"],
        "the change transaction carries exactly the registration subject: {c}"
    );
    assert_eq!(c["impact"]["human_gate_required"], true, "{c}");
    // the two approvals name each other: the execution gate names the transaction and its gate; the transaction
    // journals the execution gate raised for its subject
    let eg = yaml(&root, &format!("spec/decisions/{exec_gate}.yaml"));
    assert_eq!(eg["subject"]["kind"], "plugin-registration", "{eg}");
    assert_eq!(
        eg["subject"]["change_transaction"]["cit"],
        json!(cit),
        "{eg}"
    );
    assert_eq!(
        eg["subject"]["change_transaction"]["human_gate"],
        json!(change_gate),
        "{eg}"
    );
    assert!(
        c["journal"].to_string().contains(&exec_gate),
        "the transaction records the execution approval gate: {c}"
    );
    let cg = yaml(&root, &format!("spec/decisions/{change_gate}.yaml"));
    assert_eq!(cg["cit"], json!(cit), "{cg}");
    assert!(
        cg["question"]
            .as_str()
            .unwrap_or("")
            .contains(r["registration_subject_sha256"].as_str().unwrap()),
        "the change gate names the registration subject: {cg}"
    );
    // nothing is written before approval: the descriptor is still the worker's, and there is no registry
    assert_eq!(std::fs::read(&df).unwrap(), hand_written);
    assert!(!exists(&root, REGISTRY));

    // 2. the execution approval alone does not stand in for the change control: still nothing written
    crate::ws03::human_decide(&g, &exec_gate, "A");
    let r = register(&te, &df);
    assert_eq!(r["registered"], false, "{r}");
    assert_eq!(r["human_gate"], json!(change_gate), "{r}");
    assert_eq!(std::fs::read(&df).unwrap(), hand_written);
    assert!(!exists(&root, REGISTRY));

    // 3. both approved: repeating the registration approves and executes the transaction (CIT-E)
    crate::ws03::human_decide(&g, &change_gate, "A");
    let r = register(&te, &df);
    assert_eq!(r["registered"], true, "{r}");
    assert_eq!(
        r["registry_entry"]["registration_gate"],
        json!(exec_gate),
        "{r}"
    );
    assert_eq!(r["change_transaction"]["cit"], json!(cit), "{r}");
    assert_eq!(r["change_transaction"]["cit_status"], "COMMITTED", "{r}");
    let c = yaml(&root, &format!("spec/decisions/{cit}.yaml"));
    let writes = c["execution"]["writes"].to_string();
    let now = sha256_file(&root, rel);
    assert!(
        writes.contains(rel) && writes.contains(&now),
        "CIT-E recorded the descriptor it wrote: {writes}"
    );
    assert_eq!(c["approval"]["gate"], json!(change_gate), "{c}");
    assert_eq!(
        yaml(&root, rel)["provenance"]["change_transaction"],
        json!(cit)
    );

    // 4. the task closes: the descriptor is accepted on the transaction's writes; nothing refuses it
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep = receipt(
        &te,
        &root,
        &t,
        &t,
        "registered the p1 plugin",
        &["tools/p1.sh", rel],
        "not_applicable_with_reason",
    );
    let closed = te.ok(&["task", "close", &t, "--report", &rep]);
    assert_eq!(closed["task_status"], "DONE", "{closed}");
    git_commit_all(&root, "p1 registered");

    // 5. bound to content, not location: a hand edit of the registered descriptor inside another task is refused
    let t2 = create(
        &g,
        "tooling",
        "retune the p1 plugin by hand",
        "tools/**,governance/project/plugins/**",
    );
    te.ok(&["task", "claim", &t2]);
    let mut d = yaml(&root, rel);
    d["required_permission_classes"] = json!(["NETWORK_READ"]);
    write_yaml(&root, rel, &d);
    assert_ne!(
        sha256_file(&root, rel),
        now,
        "the edit changes the descriptor"
    );
    g.ok(&["rebuild-memory", "--incremental"]);
    let rep = receipt(
        &te,
        &root,
        &t2,
        &t2,
        "edited the descriptor",
        &[rel],
        "not_applicable_with_reason",
    );
    let e = te.err(&["task", "close", &t2, "--report", &rep]);
    assert_eq!(
        e.error_code(),
        "MATERIAL_CHANGE_REQUIRES_CIT",
        "{}",
        e.envelope
    );
    assert!(e.envelope.to_string().contains(rel), "{}", e.envelope);
}

/// **INT3-O1, the other direction (F4).** The change approval does not stand in for the execution approval either:
/// a registration transaction approved and executed (`gov cit approve` / `gov cit execute`) before the plugin's
/// execution gate is answered writes nothing — CIT-E re-verifies the execution approval, refuses
/// `PLUGIN_NOT_APPROVED` and rolls back. Once the execution gate is answered, the repeated registration raises a
/// new transaction (a rolled-back one is finished) and completes through it.
#[test]
fn a_registration_change_approved_without_its_execution_approval_writes_nothing() {
    let (root, g) = fresh("r4-reg-f4");
    let te = g.with_role("tooling-engineer").with_session("S-tool");
    let df = plugin(&root, "p2");
    let r = register(&te, &df);
    let exec_gate = r["human_gate"].as_str().unwrap().to_string();
    let cit = r["change_transaction"]["cit"].as_str().unwrap().to_string();
    let change_gate = r["change_transaction"]["human_gate"]
        .as_str()
        .unwrap()
        .to_string();
    crate::ws03::human_decide(&g, &change_gate, "A");
    // the registration waits on the execution approval
    let r = register(&te, &df);
    assert_eq!(
        (r["registered"].as_bool(), r["human_gate"].as_str()),
        (Some(false), Some(exec_gate.as_str())),
        "{r}"
    );
    // an operator with CIT authority approves and executes the change directly: refused at CIT-E, rolled back
    g.ok(&["cit", "approve", &cit, "--method", "human"]);
    let e = g.err(&["cit", "execute", &cit]);
    assert_eq!(e.error_code(), "PLUGIN_NOT_APPROVED", "{}", e.envelope);
    assert_eq!(
        yaml(&root, &format!("spec/decisions/{cit}.yaml"))["cit_status"],
        "ROLLED_BACK"
    );
    assert!(!exists(&root, REGISTRY), "nothing was registered");
    assert!(
        yaml(&root, "governance/project/plugins/p2.yaml")["provenance"].is_null(),
        "the descriptor is still the hand-written one"
    );
    // the execution approval given, the repeated request raises a new transaction and completes through it
    crate::ws03::human_decide(&g, &exec_gate, "A");
    let r = register(&te, &df);
    assert_eq!(r["registered"], false, "{r}");
    let cit2 = r["change_transaction"]["cit"].as_str().unwrap().to_string();
    assert_ne!(cit2, cit, "{r}");
    crate::ws03::human_decide(
        &g,
        r["change_transaction"]["human_gate"].as_str().unwrap(),
        "A",
    );
    let r = register(&te, &df);
    assert_eq!(r["registered"], true, "{r}");
    assert_eq!(r["change_transaction"]["cit"], json!(cit2), "{r}");
    assert_eq!(
        r["registry_entry"]["registration_gate"],
        json!(exec_gate),
        "{r}"
    );
    // repeating an in-force registration changes nothing and raises nothing
    let before = std::fs::read_dir(root.join("spec/decisions"))
        .unwrap()
        .count();
    let r = register(&te, &df);
    assert_eq!(
        (r["registered"].as_bool(), r["unchanged"].as_bool()),
        (Some(true), Some(true)),
        "{r}"
    );
    assert_eq!(
        std::fs::read_dir(root.join("spec/decisions"))
            .unwrap()
            .count(),
        before
    );
}

fn system_transactions(g: &Gov) -> Vec<Value> {
    g.ok(&["cit", "list"])
        .as_array()
        .unwrap()
        .iter()
        .filter(|c| c["origin"] == "system")
        .cloned()
        .collect()
}

/// **INT3-O2 (WS-2; Contract v3 W6 "however made", O5/W12 G1 "invalidates affected dependency/lineage evidence after
/// material mutations").** A direct upstream change observed by an index rebuild a host runs as its own operation
/// (`gov rebuild-memory`, `gov memory rebuild`) is propagated when it is observed — the dependent work is marked for
/// re-test by one sealed system transaction — not only at the next claim. Idempotent: a rebuild that observes nothing
/// new records nothing. The propagation writes governed records, so under FREEZE_WRITES it is deferred (reported, the
/// rebuild itself stays available) and a later rebuild propagates.
#[test]
fn a_direct_upstream_change_observed_at_an_index_rebuild_is_propagated_there_once() {
    let (root, g) = fresh("r4-rebuild-prop");
    let inputs = crate::ws05::traceable_inputs(&root, "0901");
    git_commit_all(&root, "inputs");
    g.ok(&["rebuild-memory", "--incremental"]);
    let a = g.ok(&[
        "task",
        "create",
        "--class",
        "refactor",
        "--objective",
        "work on totals",
        "--status",
        "READY",
        "--allowed",
        "src/a/**",
        "--fields",
        &inputs.to_string(),
    ])["id"]
        .as_str()
        .unwrap()
        .to_string();
    g.ok(&["context", "compile", &a]);
    let rq = "spec/requirements/REQ-0901.yaml";
    // 1. under FREEZE_WRITES the rebuild runs, observes the direct change and defers its propagation
    g.ok(&["freeze-writes", "--reason", "incident"]);
    let mut r = yaml(&root, rq);
    r["statement"] = json!("totals are integer cents, rounded half-even");
    write_yaml(&root, rq, &r);
    git_commit_all(&root, "direct change 1");
    let rb = g.ok(&["rebuild-memory", "--incremental"]);
    let up = &rb["upstream_changes"];
    assert_eq!(up["propagated"], false, "{rb}");
    assert_eq!(up["deferred"]["code"], "FROZEN", "{up}");
    assert!(up["detected"].to_string().contains(&a), "{up}");
    assert!(system_transactions(&g).is_empty());
    assert_ne!(
        yaml(&root, &format!("spec/tasks/{a}.yaml"))["retest_required"],
        true
    );
    g.ok(&["resume"]);
    // 2. the next host-run rebuild propagates it: one sealed system transaction, the dependant marked for re-test
    let rb = g.ok(&["rebuild-memory", "--incremental"]);
    let up = &rb["upstream_changes"];
    assert_eq!(up["propagated"], true, "{rb}");
    let sys = system_transactions(&g);
    assert_eq!(sys.len(), 1, "{sys:?}");
    assert_eq!(up["cit"], sys[0]["id"], "{up}");
    let rec = g.ok(&["cit", "show", sys[0]["id"].as_str().unwrap()]);
    assert_eq!(rec["cit_status"], "COMMITTED", "{rec}");
    assert_eq!(rec["system"]["detected_by"], "index rebuild", "{rec}");
    assert_eq!(
        yaml(&root, &format!("spec/tasks/{a}.yaml"))["retest_required"],
        true
    );
    assert_eq!(
        g.ok(&["memory", "freshness"])["fresh"],
        true,
        "the index includes the marks"
    );
    // 3. idempotent: nothing new observed, nothing recorded
    let rb = g.ok(&["rebuild-memory", "--incremental"]);
    assert_ne!(rb["upstream_changes"]["propagated"], true, "{rb}");
    assert_eq!(system_transactions(&g).len(), 1);
    assert_eq!(g.ok(&["cit", "propagate", "--dry-run"])["changes"], 0);
    // 4. the same through `gov memory rebuild`
    g.ok(&["context", "compile", &a]);
    let mut r = yaml(&root, rq);
    r["statement"] = json!("totals are integer cents, rounded half-up");
    write_yaml(&root, rq, &r);
    git_commit_all(&root, "direct change 2");
    let mb = g.ok(&["memory", "rebuild", "--incremental"]);
    assert_eq!(mb["upstream_changes"]["propagated"], true, "{mb}");
    assert_eq!(system_transactions(&g).len(), 2);
}
