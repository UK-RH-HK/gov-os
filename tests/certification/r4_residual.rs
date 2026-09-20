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

/// The family `id` of a `--family <id>` audit run (result or refusal details), with the run's findings of that
/// family as `findings`.
fn suite_family(g: &Gov, id: &str) -> Value {
    let o = g.run(&["audit", "--no-persist", "--family", id]);
    let r = if o.ok() { o.result() } else { o.details() };
    let mut fam = match &r["families"] {
        Value::Array(a) => a
            .iter()
            .find(|f| f["id"] == id)
            .cloned()
            .unwrap_or(Value::Null),
        Value::Object(m) => m.get(id).cloned().unwrap_or(Value::Null),
        _ => Value::Null,
    };
    assert!(!fam.is_null(), "no {id} family in {r}");
    if fam["findings"].as_array().is_none() {
        fam["findings"] = json!(r["findings"]
            .as_array()
            .cloned()
            .unwrap_or_default()
            .into_iter()
            .filter(|f| f["family"] == id)
            .collect::<Vec<_>>());
    }
    fam
}

fn binding_family(g: &Gov) -> Value {
    suite_family(g, "os_binding_integrity")
}

/// **WS-3 IP-R3-WS03-6 and WS-8 IP-R3-WS08-3 (P2-ADJ-0002 observability).** Doctor D033 and the
/// `os_binding_integrity` family report this machine's T2 binding status (`t2::binding_status()`): on the owner's
/// bound machine the sealing is portable and nothing is raised; on a machine provisioned from the owner's root but not
/// given the binding authority, the machine-scope sealing is disclosed (low: what it writes is honoured there only),
/// D033 still passes, and the family names the scope and why. (The medium cases — an installed authority not honoured
/// now, a bound machine not sealing with the active key — are the lib test
/// `verification::reporting::tests::binding_status_findings_raise_an_unhonoured_authority_and_disclose_machine_scope`.)
#[test]
fn the_t2_binding_status_is_reported_and_machine_scope_sealing_on_a_provisioned_machine_is_disclosed(
) {
    let (root, g) = fresh("r4-t2status");
    git_commit_all(&root, "baseline");
    // the owner's machine: bound, portable
    let (ok, msg) = doctor_check(&g, "D033");
    assert!(ok, "{msg}");
    assert!(msg.contains("T2 sealing: portable"), "{msg}");
    let fam = binding_family(&g);
    let st = &fam["detail"]["binding_status"];
    assert_eq!(
        (st["bound"].as_bool(), st["portable"].as_bool()),
        (Some(true), Some(true)),
        "{fam}"
    );
    assert!(
        !fam["findings"].to_string().contains("machine scope"),
        "{fam}"
    );
    // IP-R3-WS03-8: the fresh agent's view (`gov status`) carries the sealing scope
    assert_eq!(g.ok(&["status"])["t2_sealing"]["scope"], "provisioned");
    // a machine provisioned from the owner's root without the binding authority: machine scope, disclosed
    let (_c, gc) = clone_to_machine(&root, "r4-t2status-c", "S-C", MachineKind::AnchorOnly);
    verify_pinned_release(&gc, None);
    let (ok_c, msg_c) = doctor_check(&gc, "D033");
    assert!(ok_c, "a disclosure does not fail D033: {msg_c}");
    assert!(
        msg_c.contains("T2 sealing: machine scope")
            && msg_c.contains("honoured on this machine only"),
        "{msg_c}"
    );
    let fam_c = binding_family(&gc);
    let st_c = &fam_c["detail"]["binding_status"];
    assert_eq!(
        (
            st_c["bound"].as_bool(),
            st_c["provisioned"].as_bool(),
            st_c["portable"].as_bool()
        ),
        (Some(false), Some(true), Some(false)),
        "{fam_c}"
    );
    assert_eq!(st_c["sealing"]["scope"], "machine", "{fam_c}");
    let sc = gc.ok(&["status"])["t2_sealing"].clone();
    assert_eq!(
        (sc["scope"].as_str(), sc["portable"].as_bool()),
        (Some("machine"), Some(false)),
        "{sc}"
    );
    let disclosure = fam_c["findings"]
        .as_array()
        .unwrap()
        .iter()
        .find(|f| {
            f["message"]
                .as_str()
                .unwrap_or("")
                .contains("seals T2 facts in its own machine scope")
        })
        .cloned()
        .unwrap_or(Value::Null);
    assert_eq!(disclosure["severity"], "low", "{fam_c}");
}

/// **WS-6 IP-R3-WS06-4 (with WS-2 IP-R3-WS02-10).** A repository-contract rule that never decides a path — a later
/// rule matches every path it matches and applies something else (last-match; WS-6 r2 O-1, detected generally by
/// `RepositoryContract::shadowed_rules`) — is reported by the `path_map_compliance` family, low, naming the dead rule
/// and the rule that overrides it. The shipped contract has none.
#[test]
fn a_repository_contract_rule_that_never_decides_is_reported() {
    let (root, g) = fresh("r4-shadowed");
    let rel = "governance/project/REPOSITORY_CONTRACT.yaml";
    let fam = suite_family(&g, "path_map_compliance");
    assert_eq!(fam["detail"]["shadowed_rules"], json!([]), "{fam}");
    // list the refining rule before the general rule it refines: `product/tests/**` then never decides
    let mut c = yaml(&root, rel);
    let rules = c["paths"].as_array_mut().unwrap();
    let i = rules
        .iter()
        .position(|r| r["pattern"] == "product/tests/**")
        .unwrap();
    let tests_rule = rules.remove(i);
    let j = rules
        .iter()
        .position(|r| r["pattern"] == "product/**")
        .unwrap();
    rules.insert(j, tests_rule);
    write_yaml(&root, rel, &c);
    let fam = suite_family(&g, "path_map_compliance");
    let shadowed = fam["detail"]["shadowed_rules"].as_array().unwrap().clone();
    assert_eq!(shadowed.len(), 1, "{fam}");
    assert_eq!(shadowed[0]["rule"], "product/tests/**");
    assert_eq!(shadowed[0]["overridden_by"], "product/**");
    let f = fam["findings"]
        .as_array()
        .unwrap()
        .iter()
        .find(|f| {
            f["message"]
                .as_str()
                .unwrap_or("")
                .contains("never decides")
        })
        .cloned()
        .unwrap_or(Value::Null);
    assert_eq!(f["severity"], "low", "{fam}");
    assert_eq!(f["path"], rel, "{f}");
}

/// **WS-7 IP-W7R3-5 with WS-6 IP-R3-WS06-7 (brownfield projects must not lose registrations).** Upgrading a project an
/// earlier release installed moves the tracked OS stores it kept in the regenerable views — the plugin registry and
/// the skill content bindings — to `governance/registry/`, bytes unchanged (migration op `relocate_os_stores`), so
/// they survive deleting `governance/generated/` from the moment of the upgrade; `gov update --rollback` restores the
/// layout the previous release reads, byte for byte (the update snapshot covers `governance/registry/`).
#[test]
fn an_update_moves_the_tracked_os_stores_and_a_rollback_restores_the_previous_layout() {
    let root = tmp("r4-update-stores");
    let proj = root.join("project");
    std::fs::create_dir_all(&proj).unwrap();
    write(&proj, "README.md", "# stores project\n");
    git_init_commit(&proj);
    let g = Gov::new(&proj, "S-r4-upd");
    provision(&g);
    let prev = canonical_root().join("fixtures/update/previous-release/4.1.1");
    let prev = signed_copy(&prev, "r4-update-4.1.1", sequence_of("4.1.1"));
    g.ok(&[
        "init",
        "--source",
        prev.to_str().unwrap(),
        "--name",
        "stores-project",
        "--alias",
        "fx-stores",
    ]);
    // what an earlier release wrote in the regenerable views
    let (reg_legacy, bind_legacy) = (
        "governance/generated/plugin-registry.json",
        "governance/generated/skill-bindings.json",
    );
    write(
        &proj,
        reg_legacy,
        "{\"schema_version\": \"1.1.0\", \"plugins\": {}}\n",
    );
    write(
        &proj,
        bind_legacy,
        "{\"schema\": \"gov.skill-bindings/1\", \"note\": \"4.1.1\", \"versions\": {}}\n",
    );
    let (reg_bytes, bind_bytes) = (
        std::fs::read(proj.join(reg_legacy)).unwrap(),
        std::fs::read(proj.join(bind_legacy)).unwrap(),
    );
    g.ok(&["rebuild-memory"]);
    git_commit_all(&proj, "4.1.1 state with stores in the generated views");
    let e = g.err(&["update", "--apply", "--source", signed_source()]);
    assert_eq!(e.error_code(), "HUMAN_GATE_REQUIRED", "{}", e.envelope);
    let gid = e.details()["gate"].as_str().unwrap().to_string();
    g.ok(&["gate", "present", &gid]);
    crate::ws03::human_decide(&g, &gid, "A");
    let ap = g.ok(&[
        "update",
        "--apply",
        "--source",
        signed_source(),
        "--approve",
        "--by",
        "owner",
    ]);
    assert_eq!(ap["applied"], true, "{ap}");
    // moved at the upgrade, bytes unchanged
    assert_eq!(
        std::fs::read(proj.join("governance/registry/plugin-registry.json")).unwrap(),
        reg_bytes
    );
    assert_eq!(
        std::fs::read(proj.join("governance/registry/skill-bindings.json")).unwrap(),
        bind_bytes
    );
    assert!(!exists(&proj, reg_legacy) && !exists(&proj, bind_legacy));
    // they survive deleting the regenerable views
    std::fs::remove_dir_all(proj.join("governance/generated")).unwrap();
    assert!(exists(&proj, "governance/registry/plugin-registry.json"));
    assert!(exists(&proj, "governance/registry/skill-bindings.json"));
    git(&proj, &["checkout", "--", "governance/generated"]);
    g.ok(&["rebuild-memory"]);
    // rollback: the layout the previous release reads, byte for byte
    break_glass(&g, &prev, "r4-update-stores-rollback");
    let rb = g.ok(&["update", "--rollback", "--break-glass"]);
    assert_eq!(rb["rolled_back_to"], "4.1.1", "{rb}");
    assert_eq!(std::fs::read(proj.join(reg_legacy)).unwrap(), reg_bytes);
    assert_eq!(std::fs::read(proj.join(bind_legacy)).unwrap(), bind_bytes);
    assert!(
        !proj.join("governance/registry").exists(),
        "the registry directory the update created is not left behind"
    );
}

/// **WS-6 IP-R3-WS06-7 (BC-P2-31, writer side).** The first-seen skill content bindings are OS-written tracked state
/// that cannot be rebuilt: they are written where the kernel's store declaration puts them (`governance/registry/`,
/// `paths::OS_STORES` `skill-bindings`), a file an earlier release kept in `governance/generated/` is read as it is
/// until the next binding write moves it (bytes and entries unchanged), and reading never moves anything.
#[test]
fn skill_bindings_are_written_where_they_belong_and_a_legacy_file_moves_on_the_next_write() {
    let (root, g) = fresh("r4-skill-bindings");
    let legacy = "governance/generated/skill-bindings.json";
    let planted = json!({"schema": "gov.skill-bindings/1", "note": "written by an earlier release",
        "versions": {"SKL-PLANTED@1": {"content_sha256": "0".repeat(64)}}});
    write(&root, legacy, &planted.to_string());
    // reading (the regression without --record) moves nothing
    let _ = g.run(&["health", "skills", "--skill", "SKL-IMPACT-ANALYSIS"]);
    assert!(exists(&root, legacy));
    assert!(!exists(&root, "governance/registry/skill-bindings.json"));
    // the next binding write moves the file first, keeping what it held, then writes there
    let _ = g.run(&[
        "health",
        "skills",
        "--record",
        "--skill",
        "SKL-IMPACT-ANALYSIS",
    ]);
    assert!(!exists(&root, legacy), "the legacy file was moved");
    let b = json(&root, "governance/registry/skill-bindings.json");
    assert!(
        b["versions"].get("SKL-PLANTED@1").is_some(),
        "the moved bindings keep their entries: {b}"
    );
}

/// **WS-4 IP-R3-WS04-11 (availability rule, end to end).** Under a critical block — a secret in product source — the
/// handoff of the remediation the OS generated (it declares the blocking checks among its `remedies`, and its subjects
/// reach the leaking file) is admitted as the block's remedy and says so; handing off unrelated work is refused,
/// typed, naming the block. (Before, the generic whole-operation guard refused both.)
#[test]
fn the_remediation_handoff_stays_available_under_the_block_it_repairs() {
    let (root, g) = fresh("r4-handoff-remedy");
    let other = create(&g, "documentation", "unrelated docs", "docs/**");
    write(
        &root,
        "src/creds.rs",
        "pub const K: &str = \"AKIAIOSFODNN7EXAMPLE\";\npub const S: &str = \"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\";\n",
    );
    let a = g.run(&["audit"]);
    assert!(
        !a.ok(),
        "a secret in product source is unhealthy: {}",
        a.envelope
    );
    let mut remediation: Option<Value> = None;
    for e in std::fs::read_dir(root.join("spec/tasks"))
        .unwrap()
        .flatten()
    {
        let n = e.file_name().to_string_lossy().to_string();
        if !n.starts_with("TASK-") {
            continue;
        }
        let t = yaml(&root, &format!("spec/tasks/{n}"));
        if t["generation"]["source"] == "security-finding"
            && t["allowed_paths"].to_string().contains("src/creds.rs")
        {
            remediation = Some(t);
        }
    }
    let rem = remediation.expect("the security finding generated its remediation");
    assert!(!rem["remedies"].as_array().unwrap().is_empty(), "{rem}");
    let rid = rem["id"].as_str().unwrap().to_string();
    // unrelated work is not handed off under the block
    let e = g.err(&[
        "handoff",
        "create",
        "--to-role",
        "backend-engineer",
        "--task",
        &other,
    ]);
    assert_eq!(e.error_code(), "HEALTH_HARD_BLOCK", "{}", e.envelope);
    // the remediation is: handed off as the block's remedy
    let h = g.ok(&[
        "handoff",
        "create",
        "--to-role",
        "security-engineer",
        "--task",
        &rid,
    ]);
    let remedied = h["availability"]["remedied_blocks"].as_array().unwrap();
    assert!(!remedied.is_empty(), "{h}");
    for b in remedied {
        assert!(
            rem["remedies"].as_array().unwrap().contains(&b["check"]),
            "{h}"
        );
    }
}

fn set_policy_overrides(root: &Path, over: Value) {
    let mut pp = yaml(root, "governance/project/PROJECT_POLICY.yaml");
    let mut cur = pp
        .get("policy_overrides")
        .cloned()
        .filter(|v| v.is_object())
        .unwrap_or(json!({}));
    for (k, v) in over.as_object().unwrap() {
        cur[k] = v.clone();
    }
    pp["policy_overrides"] = cur;
    write_yaml(root, "governance/project/PROJECT_POLICY.yaml", &pp);
}

/// **WS-7 IP-W7R3-6 (IP-R2-13's consumer side; Contract v3 D4, D1).** The model and runtime artefacts an embed
/// plugin declares — the files its registration binds — are part of the retrieval profile's component identity: a
/// declared model artefact inside the repository is in the model identity the index manifest pins (portable), one
/// outside it and every declared runtime artefact are in the machine-local runtime identity; the profile hashes them
/// with the digest the registration pin uses. A changed declared model artefact is a pin mismatch the freshness check
/// reports, and nothing is served under it.
#[test]
fn declared_model_and_runtime_artefacts_are_part_of_the_retrieval_profile_identity() {
    let (root, g) = fresh("r4-profile-declared");
    write_exec(
        &root,
        "tools/emb/echo_embedder.sh",
        &read(&canonical_root(), "capabilities/shell/echo_embedder.sh"),
    );
    write(&root, "models/mini/weights.bin", "weights v1\n");
    let cache = tmp("r4-profile-runtime"); // a machine-local runtime installation, outside the repository
    std::fs::create_dir_all(&cache).unwrap();
    std::fs::write(cache.join("libinfer.so"), "runtime v1").unwrap();
    let rel = "governance/project/plugins/echo-local.yaml";
    write_yaml(
        &root,
        rel,
        &json!({"plugin_id": "echo-local", "capability": "embed", "version": "1", "command": ["tools/emb/echo_embedder.sh"], "languages": [],
            "model": {"id": "mini-embed", "revision": "2026-09", "artefacts": ["models/mini"]},
            "runtime": {"id": "infer-1", "artefacts": [cache.join("libinfer.so").to_str().unwrap()]}}),
    );
    crate::ws07::register_approved(&g, &root.join(rel));
    set_policy_overrides(
        &root,
        json!({"MEMORY_POLICY.embedding.provider": "echo-local", "MEMORY_POLICY.embedding.dimensions": 8}),
    );
    git_commit_all(&root, "a local embedder declaring its model and runtime");
    let r = g.ok(&["rebuild-memory"]);
    let e = &r["embedder"];
    assert_eq!(e["model"]["id"], "mini-embed", "{e}");
    assert_eq!(e["model"]["declared"], true, "{e}");
    assert_eq!(e["runtime"]["declared_id"], "infer-1", "{e}");
    let m = json(&root, "governance/generated/index-manifest.json");
    let comp = &m["components"]["embedder"];
    let arts = comp["model"]["artefacts"].to_string();
    assert!(
        arts.contains("models/mini/weights.bin") && arts.contains("\"declared\":true"),
        "the declared in-repository model artefact is in the pinned model identity: {comp}"
    );
    assert!(
        !arts.contains("libinfer.so"),
        "a machine-local artefact never enters the portable model identity: {comp}"
    );
    assert_eq!(g.ok(&["memory", "freshness"])["fresh"], true);
    // a changed declared model artefact is not served under the pinned identity
    write(&root, "models/mini/weights.bin", "weights v2\n");
    let fr = g.ok(&["memory", "freshness"]);
    assert_eq!(fr["fresh"], false, "{fr}");
    assert!(
        !g.run(&["memory", "query", "totals", "--route", "semantic"])
            .ok(),
        "the changed model artefact was served"
    );
}

// ==================================================================================================== R4-O1

/// A schema-valid tool descriptor at `.r4-tool-<name>.json`, with `extra` merged over it. Its automatic
/// installation conditions cannot all hold (no governed security review of this tool identity and version), so the
/// installation needs a gate raised for exactly it.
fn tool_descriptor(root: &Path, name: &str, extra: Value) -> PathBuf {
    let mut d = json!({"tool_id": "TOOL-R4", "name": "r4", "type": "CLI", "capabilities": ["lint"],
        "version": "1.0", "version_pin": "1.0.0", "required_permission_classes": ["READ_REPO"], "license": "MIT",
        "reversible": true, "cost_usd": 0, "install_command": ["true"], "uninstall_command": ["true"],
        "health_check": {"kind": "command", "command": ["true"], "expect_exit": 0}});
    for (k, v) in extra.as_object().cloned().unwrap_or_default() {
        d[k] = v;
    }
    // inside `tools/`, so a task that installs it can declare the request file it wrote
    let rel = format!("tools/r4-tool-{name}.json");
    write(root, &rel, &d.to_string());
    root.join(rel)
}

fn install(g: &Gov, df: &Path) -> Value {
    g.ok(&["tools", "install", "--descriptor", df.to_str().unwrap()])
}

/// **R4-O1 (the path adjacent to INT3-O1, WS-7 × WS-5).** `gov tools install` writes its descriptor under
/// `governance/project/tools/`, which the kernel-floor materiality classifies exactly as it classifies a plugin
/// descriptor — so before this repair an installation made inside a claimed task was refused at the close with
/// `MATERIAL_CHANGE_REQUIRES_CIT`, whatever the owner had approved. Contract v3 K3 and F4 now both hold here too:
/// the OS proposes and simulates the installation's change transaction itself (the worker files none), raises the
/// installation gate naming that transaction and its gate, writes nothing until **both** are answered, and then
/// writes the descriptor only by executing the transaction (CIT-E). The task then closes on the transaction's
/// recorded writes — including when the tool path is not in the task's allowed paths, because a CIT that governs
/// exactly that content covers it. Bound to content: a later hand edit of the installed descriptor inside another
/// task is refused at that close.
#[test]
fn a_tool_installed_inside_a_claimed_task_closes_on_its_os_proposed_change_transaction() {
    let (root, g) = fresh("r4-tool-close");
    let te = g.with_role("tooling-engineer").with_session("S-tool");
    let t = create(&g, "tooling", "install the r4 tool", "tools/**");
    te.ok(&["task", "claim", &t]);
    let df = tool_descriptor(&root, "a", json!({}));
    let rel = "governance/project/tools/TOOL-R4.yaml";

    // 1. the request: the OS proposes and simulates the change transaction (K3) and raises the installation gate
    let r = install(&te, &df);
    assert_eq!(r["installed"], false, "{r}");
    let inst_gate = r["human_gate"].as_str().unwrap().to_string();
    let ct = &r["change_transaction"];
    let cit = ct["cit"].as_str().unwrap().to_string();
    let change_gate = ct["human_gate"].as_str().unwrap().to_string();
    assert_ne!(inst_gate, change_gate, "{r}");
    assert_eq!(
        ct["cit_status"], "SIMULATED",
        "CIT-P ran automatically: {r}"
    );
    let trig = ct["effective_triggers"].to_string();
    assert!(
        trig.contains("governance_change") && trig.contains("security_change"),
        "an installation is a material governance and security change: {r}"
    );
    let c = yaml(&root, &format!("spec/decisions/{cit}.yaml"));
    assert_eq!(c["origin"], "system", "{c}");
    assert_eq!(c["system"]["kind"], "tool-installation", "{c}");
    assert_eq!(c["mutation_manifest"][0]["op"], "install_tool", "{c}");
    assert_eq!(
        c["mutation_manifest"][0]["subject_sha256"], r["installation_sha256"],
        "the change transaction carries exactly the installation subject: {c}"
    );
    assert_eq!(
        c["mutation_manifest"][0]["role"], "tooling-engineer",
        "the conditions were evaluated for the acting role: {c}"
    );
    assert_eq!(c["impact"]["human_gate_required"], true, "{c}");
    // the two approvals name each other
    let ig = yaml(&root, &format!("spec/decisions/{inst_gate}.yaml"));
    assert_eq!(ig["subject"]["kind"], "tool-installation", "{ig}");
    assert_eq!(
        ig["subject"]["change_transaction"]["cit"],
        json!(cit),
        "{ig}"
    );
    assert_eq!(
        ig["subject"]["change_transaction"]["human_gate"],
        json!(change_gate),
        "{ig}"
    );
    assert!(
        c["journal"].to_string().contains(&inst_gate),
        "the transaction records the installation approval gate: {c}"
    );
    assert!(!exists(&root, rel), "written before either approval");

    // 2. the installation approval alone does not stand in for change control
    crate::ws03::human_decide(&g, &inst_gate, "A");
    let r = install(&te, &df);
    assert_eq!(r["installed"], false, "{r}");
    assert_eq!(r["human_gate"], json!(change_gate), "{r}");
    assert!(
        !exists(&root, rel),
        "written before the change was approved"
    );

    // 3. both approved: repeating the install approves and executes the transaction (CIT-E)
    crate::ws03::human_decide(&g, &change_gate, "A");
    let r = install(&te, &df);
    assert_eq!(r["installed"], true, "{r}");
    assert_eq!(r["change_transaction"]["cit"], json!(cit), "{r}");
    assert_eq!(r["change_transaction"]["cit_status"], "COMMITTED", "{r}");
    let c = yaml(&root, &format!("spec/decisions/{cit}.yaml"));
    let writes = c["execution"]["writes"].to_string();
    let now = sha256_file(&root, rel);
    assert!(
        writes.contains(rel) && writes.contains(&now),
        "CIT-E recorded the descriptor it wrote: {writes}"
    );
    let d = yaml(&root, rel);
    assert_eq!(d["approval"]["gate"], json!(inst_gate), "{d}");
    assert_eq!(d["approval"]["change_transaction"], json!(cit), "{d}");
    // repeating an installation already in force changes nothing and proposes nothing
    let r = install(&te, &df);
    assert_eq!(
        (r["installed"].as_bool(), r["unchanged"].as_bool()),
        (Some(true), Some(true)),
        "{r}"
    );
    assert_eq!(
        g.ok(&["cit", "list"]).as_array().unwrap().len(),
        1,
        "a repeat raised a second transaction"
    );

    // 4. the task closes on the transaction's writes although `governance/project/tools/**` is not allowed to it
    g.ok(&["rebuild-memory", "--incremental"]);
    write(&root, "tools/note.txt", "installed\n");
    let rep = receipt(
        &te,
        &root,
        &t,
        &t,
        "installed the r4 tool",
        &["tools/note.txt", "tools/r4-tool-a.json"],
        "not_applicable_with_reason",
    );
    let closed = te.ok(&["task", "close", &t, "--report", &rep]);
    assert_eq!(closed["task_status"], "DONE", "{closed}");
    git_commit_all(&root, "r4 tool installed");

    // 5. bound to content: a hand edit of the installed descriptor inside another task is refused at its close
    let t2 = create(
        &g,
        "tooling",
        "retune the r4 tool by hand",
        "tools/**,governance/project/tools/**",
    );
    te.ok(&["task", "claim", &t2]);
    let mut d = yaml(&root, rel);
    d["capabilities"] = json!(["lint", "format"]);
    write_yaml(&root, rel, &d);
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

/// **R4-O1, the other direction (F4), and the autonomous path.** The change approval does not stand in for the
/// installation approval: a transaction approved and executed directly (`gov cit approve` / `gov cit execute`)
/// before the installation gate is answered writes nothing — CIT-E re-verifies it, refuses `TOOL_NOT_APPROVED` and
/// rolls back. `gov cit execute` is not a way round `TOOL_PERMISSIONS.install_authority_roles` either. (The
/// review-evidenced path, where no installation gate is asked at all, is covered by
/// `ws07::a_governed_security_review_by_another_role_lets_the_installation_proceed`.)
#[test]
fn an_installation_change_approved_without_its_installation_approval_writes_nothing() {
    let (root, g) = fresh("r4-tool-f4");
    let te = g.with_role("tooling-engineer").with_session("S-tool");
    let df = tool_descriptor(&root, "b", json!({}));
    let rel = "governance/project/tools/TOOL-R4.yaml";
    let r = install(&te, &df);
    let inst_gate = r["human_gate"].as_str().unwrap().to_string();
    let cit = r["change_transaction"]["cit"].as_str().unwrap().to_string();
    let change_gate = r["change_transaction"]["human_gate"]
        .as_str()
        .unwrap()
        .to_string();

    // the change alone: approve its gate and drive the transaction from the CIT commands
    crate::ws03::human_decide(&g, &change_gate, "A");
    g.ok(&["cit", "approve", &cit, "--method", "human"]);
    let e = g.err(&["cit", "execute", &cit]);
    assert_eq!(e.error_code(), "TOOL_NOT_APPROVED", "{}", e.envelope);
    assert!(!exists(&root, rel), "the descriptor was written anyway");
    assert_eq!(
        yaml(&root, &format!("spec/decisions/{cit}.yaml"))["cit_status"],
        "ROLLED_BACK"
    );

    // once the installation gate is answered, a repeated install raises a new transaction (a rolled-back one is
    // finished) and completes through it
    crate::ws03::human_decide(&g, &inst_gate, "A");
    let r = install(&te, &df);
    let cit2 = r["change_transaction"]["cit"].as_str().unwrap().to_string();
    assert_ne!(cit2, cit, "a rolled-back transaction is finished: {r}");
    crate::ws03::human_decide(
        &g,
        r["change_transaction"]["human_gate"].as_str().unwrap(),
        "A",
    );
    // nor is `gov cit execute` a way round TOOL_PERMISSIONS.install_authority_roles: a CIT role that holds no
    // installation authority cannot drive the installation, and the transaction rolls back
    let cc = g.with_role("change-controller").with_session("S-cc");
    cc.ok(&["cit", "approve", &cit2, "--method", "human"]);
    let e = cc.err(&["cit", "execute", &cit2]);
    assert_eq!(e.error_code(), "AUTHORITY_DENIED", "{}", e.envelope);
    assert!(!exists(&root, rel), "the descriptor was written anyway");

    // the installing role repeats the request once more and it completes
    let r = install(&te, &df);
    let cit3 = r["change_transaction"]["cit"].as_str().unwrap().to_string();
    assert_ne!(cit3, cit2, "{r}");
    crate::ws03::human_decide(
        &g,
        r["change_transaction"]["human_gate"].as_str().unwrap(),
        "A",
    );
    let r = install(&te, &df);
    assert_eq!(r["installed"], true, "{r}");
    assert_eq!(yaml(&root, rel)["approval"]["gate"], json!(inst_gate));
    assert_eq!(
        yaml(&root, rel)["approval"]["change_transaction"],
        json!(cit3)
    );
}
