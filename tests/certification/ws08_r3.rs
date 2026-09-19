//! Repair iteration 1, round 3, WS-8 (P2-AR-0039): the provisioning side of P2-ADJ-0002 (T2 facts honoured across the
//! owner's provisioned machines), kernel payload/version consistency, the scoped `update --apply` entry guard
//! (availability rule) and the BC-P2-31 move of update snapshots.
//!
//! Builder regression evidence (Contract v3 O3), not acceptance evidence. Every machine is provisioned the documented
//! way (`common::provision` / `clone_to_machine`); human answers come only through the owner-signed channel helper
//! (`ws03::human_decide`); every invocation declares its role.
#![allow(dead_code)]
use crate::common::*;
use serde_json::{json, Value};
use std::path::{Path, PathBuf};

fn write_exec(root: &Path, rel: &str, text: &str) {
    write(root, rel, text);
    use std::os::unix::fs::PermissionsExt;
    std::fs::set_permissions(root.join(rel), std::fs::Permissions::from_mode(0o755)).unwrap();
}

const EMBED_OK: &str = r#"{"protocol":"gov-capability/1","ok":true,"provider":{"id":"p","version":"1"},"outputs":{"vectors":[],"dim":8}}"#;

fn invoke(g: &Gov, id: &str) -> Out {
    g.run(&[
        "capabilities",
        "invoke",
        "--plugin",
        id,
        "--inputs",
        "{\"texts\": []}",
    ])
}

/// A CIT whose governance change needs a Human Decision Gate (returns the CIT id and its gate).
fn cit_with_gate(g: &Gov, root: &Path, tag: &str) -> (String, String) {
    let mf = root
        .join(".governance-runtime")
        .join(format!("r3-{tag}.json"));
    std::fs::create_dir_all(mf.parent().unwrap()).unwrap();
    std::fs::write(
        &mf,
        json!([{"op": "write_file", "path": format!("docs/{tag}.md"), "content": "x\n"}])
            .to_string(),
    )
    .unwrap();
    let c = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        &format!("change {tag}"),
        "--trigger",
        "governance_change",
        "--manifest",
        mf.to_str().unwrap(),
    ]);
    let cid = c["id"].as_str().unwrap().to_string();
    if c["cit_status"] != "SIMULATED" {
        g.ok(&["cit", "simulate", &cid]);
    }
    let gate = g.ok(&["cit", "show", &cid])["human_gate"]
        .as_str()
        .unwrap()
        .to_string();
    (cid, gate)
}

fn d033(g: &Gov) -> (bool, String) {
    doctor_check(g, "D033")
}

fn t2_of_gate(g: &Gov, gid: &str) -> Value {
    g.ok(&["gate", "show", gid])
}

// ============================================================================================ P2-ADJ-0002

/// P2-ADJ-0002: a T2 fact an OS operation writes on any machine provisioned for the owner — a gate and its owner
/// answer, the decision it records, a CIT's sealed state, a plugin registration, governed health evidence — is
/// honoured on the owner's other provisioned machine after a clone/pull. The same facts are refused, typed and
/// observable, on a machine provisioned from the owner's root but not authorised by the provisioning, on a machine
/// with no trust anchor and on another owner's machine; a record written on an unauthorised machine and pulled onto
/// an owner machine is refused there; a hand edit is refused everywhere. No key material reaches the repository.
#[test]
fn t2_facts_written_on_one_owner_machine_are_honoured_on_the_others_and_refused_elsewhere() {
    // ---- machine A: an owner machine (the documented provisioning: suite root + the owner's binding authority)
    let (a, ga) = setup_fixture("greenfield", "r3-t2-a", "S-A");
    ga.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "t2x",
        "--alias",
        "fx-t2x",
    ]);
    let ta = ga.ok(&["trust", "status"])["t2_binding"].clone();
    assert_eq!(ta["bound"], true, "{ta}");
    assert_eq!(ta["sealing_key_is_authority_active_key"], true, "{ta}");
    assert_eq!(ta["sealing_key_id"], json!(suite_binding().key_id));
    // (1) a gate raised on A and answered by the owner (owner-signed), which records a sealed decision
    let gid = ga.ok(&[
        "gate",
        "create",
        "--question",
        "Adopt the ledger format?",
        "--fields",
        &crate::ws03::package(json!({})),
    ])["id"]
        .as_str()
        .unwrap()
        .to_string();
    crate::ws03::human_decide(&ga, &gid, "A");
    // (2) CIT state: a governance change proposed, its gate answered and the CIT approved on A — executed on B
    let (cid, cgate) = cit_with_gate(&ga, &a, "crossmachine");
    crate::ws03::human_decide(&ga, &cgate, "A");
    let cc_a = ga.with_role("change-controller").with_session("S-cc-A");
    assert_eq!(
        cc_a.ok(&["cit", "approve", &cid, "--method", "human"])["human_approved"],
        true
    );
    // (3) a plugin registration approved through the owner's gate on A
    write_exec(
        &a,
        "tools/p.sh",
        &format!("#!/bin/sh\ncat >/dev/null\nprintf '%s\\n' '{EMBED_OK}'\n"),
    );
    write_yaml(
        &a,
        "governance/project/plugins/p1.yaml",
        &json!({"plugin_id": "p1", "capability": "embed", "version": "1", "command": ["sh", "tools/p.sh"]}),
    );
    let te_a = ga.with_role("tooling-engineer");
    crate::ws07::register_approved(&te_a, &a.join("governance/project/plugins/p1.yaml"));
    assert!(invoke(&te_a, "p1").ok());
    // (4) governed health evidence: a governance-suite audit record sealed by the health operation
    ga.ok(&["audit"]);
    git_commit_all(&a, "T2 facts written on machine A");
    // no binding key material anywhere in the repository (P2-ADJ-0002: no key or shared secret in any repository)
    let key_hex = hex::encode(suite_binding().key);
    let (_, grep) = git(&a, &["grep", "-l", &key_hex]);
    assert!(
        grep.is_empty(),
        "the binding key reached the repository: {grep}"
    );
    let (_, grep_all) = git(&a, &["log", "-p", "--all", "-S", &key_hex, "--oneline"]);
    assert!(grep_all.is_empty(), "the binding key reached the history");
    let (ok_a, msg_a) = d033(&ga);
    assert!(ok_a, "{msg_a}");
    assert!(msg_a.contains("0 record(s) not honoured"), "{msg_a}");

    // ---- machine C: provisioned from the owner's root, NOT authorised by the provisioning (no binding authority)
    let (c, gc) = clone_to_machine(&a, "r3-t2-c", "S-C", MachineKind::AnchorOnly);
    verify_pinned_release(&gc, None);
    let tc = gc.ok(&["trust", "status"])["t2_binding"].clone();
    assert_eq!(tc["bound"], false, "{tc}");
    assert_ne!(tc["sealing_key_id"], ta["sealing_key_id"], "{tc}");
    // not honoured: FOREIGN once C holds a machine-local key, KEY_UNAVAILABLE before C has sealed anything
    let sc = t2_of_gate(&gc, &gid);
    assert!(
        ["FOREIGN", "KEY_UNAVAILABLE"].contains(&sc["t2"]["binding"].as_str().unwrap()),
        "{sc}"
    );
    assert_eq!(sc["answer"]["verified"], false, "{sc}");
    let cc_c = gc.with_role("change-controller").with_session("S-cc-C");
    assert_eq!(
        cc_c.err(&["cit", "execute", &cid]).error_code(),
        "T2_UNBOUND"
    );
    assert!(!exists(&c, "docs/crossmachine.md"));
    let e = invoke(&gc.with_role("tooling-engineer"), "p1");
    assert!(
        !e.ok(),
        "a registration sealed under the owner's authority ran on an unauthorised machine: {}",
        e.envelope
    );
    let (_, msg_c) = d033(&gc);
    assert!(
        msg_c.contains(&gid) && !msg_c.contains("0 record(s) not honoured"),
        "C must disclose the records it does not honour: {msg_c}"
    );
    // C writes a T2 fact of its own (sealed with its machine-local key) and commits it
    let gid_c = gc.ok(&[
        "gate",
        "create",
        "--question",
        "A question raised on an unauthorised machine?",
        "--fields",
        &crate::ws03::package(json!({})),
    ])["id"]
        .as_str()
        .unwrap()
        .to_string();
    git_commit_all(&c, "a gate written on machine C");

    // ---- machine B: another owner machine (own XDG_STATE_HOME and HOME, same root, same binding authority); it
    // also pulls what the unauthorised machine C committed
    let (b, gb) = clone_to_machine(&a, "r3-t2-b", "S-B", MachineKind::Owner);
    verify_pinned_release(&gb, None);
    pull_from(&gb, &c);
    let tb = gb.ok(&["trust", "status"]);
    assert_ne!(
        tb["machine_id"],
        ga.ok(&["trust", "status"])["machine_id"],
        "B must be a different machine"
    );
    assert_eq!(tb["t2_binding"]["bound"], true);
    assert_eq!(tb["t2_binding"]["sealing_key_id"], ta["sealing_key_id"]);
    // (1) the gate, its owner answer and the decision are honoured on B
    let sb = t2_of_gate(&gb, &gid);
    assert_eq!(sb["t2"]["binding"], "VERIFIED", "{sb}");
    assert_eq!(sb["answer"]["verified"], true, "{sb}");
    // the record the unauthorised machine C wrote is refused on B, typed and listed
    let sbc = t2_of_gate(&gb, &gid_c);
    assert_eq!(sbc["t2"]["binding"], "FOREIGN", "{sbc}");
    let listed = gb.ok(&["gate", "list"]);
    assert!(
        listed
            .as_array()
            .unwrap()
            .iter()
            .any(|x| x["id"] == json!(gid_c) && x["honoured"] == false),
        "{listed}"
    );
    assert!(
        !listed
            .as_array()
            .unwrap()
            .iter()
            .any(|x| x["id"] == json!(gid) && x["honoured"] == false),
        "{listed}"
    );
    // (2) the CIT approved on A executes on B
    let cc_b = gb.with_role("change-controller").with_session("S-cc-B");
    assert_eq!(
        cc_b.ok(&["cit", "execute", &cid])["cit_status"],
        "COMMITTED"
    );
    assert!(exists(&b, "docs/crossmachine.md"));
    // (3) the registration made on A is honoured on B
    let te_b = gb.with_role("tooling-engineer");
    let inv = invoke(&te_b, "p1");
    assert!(inv.ok(), "{}", inv.envelope);
    // (4) every owner-written T2 record, the governed audit evidence included, is honoured on B; only C's is not
    let (ok_b, msg_b) = d033(&gb);
    assert!(ok_b, "{msg_b}");
    assert!(
        msg_b.contains("1 record(s) not honoured") && msg_b.contains(&gid_c),
        "{msg_b}"
    );

    // ---- machine D: no trust anchor at all
    let (_d, gd) = clone_to_machine(&a, "r3-t2-d", "S-D", MachineKind::Unprovisioned);
    let b1 = suite_binding();
    let e = gd.err(&[
        "trust",
        "bind",
        "--authority",
        b1.authority.to_str().unwrap(),
        "--key",
        b1.key_file.to_str().unwrap(),
    ]);
    assert_eq!(e.error_code(), "T2_BINDING_UNPROVISIONED", "{}", e.envelope);
    assert!(e.details()["remediation"]
        .to_string()
        .contains("gov trust provision"));
    let sd = gd.run(&["gate", "show", &gid]);
    if sd.ok() {
        assert_ne!(sd.result()["t2"]["binding"], "VERIFIED", "{}", sd.envelope);
        assert_eq!(sd.result()["answer"]["verified"], false);
    }
    assert_eq!(gd.ok(&["trust", "status"])["t2_binding"]["bound"], false);

    // ---- machine E: another owner's machine (another root, another binding authority)
    let (_e, ge) = clone_to_machine(&a, "r3-t2-e", "S-E", MachineKind::ForeignOwner);
    verify_pinned_release(&ge, Some(&foreign_owner().signed_source));
    assert_eq!(ge.ok(&["trust", "status"])["t2_binding"]["bound"], true);
    let se = t2_of_gate(&ge, &gid);
    assert_eq!(se["t2"]["binding"], "FOREIGN", "{se}");
    assert_eq!(
        ge.with_role("change-controller")
            .with_session("S-cc-E")
            .err(&["cit", "execute", &cid])
            .error_code(),
        "T2_UNBOUND"
    );
    // the owner's authority does not verify against another owner's root
    let e = ge.err(&[
        "trust",
        "bind",
        "--authority",
        b1.authority.to_str().unwrap(),
        "--key",
        b1.key_file.to_str().unwrap(),
    ]);
    assert_eq!(e.error_code(), "SRR_THRESHOLD_NOT_MET", "{}", e.envelope);

    // ---- a hand edit of an owner-sealed record is refused on the owner machines
    let path = format!("spec/decisions/{gid}.yaml");
    let mut rec = yaml(&b, &path);
    rec["question"] = json!("Adopt the ledger format? (edited by hand)");
    write_yaml(&b, &path, &rec);
    let sbe = t2_of_gate(&gb, &gid);
    assert_eq!(sbe["t2"]["binding"], "BROKEN", "{sbe}");
    assert_eq!(sbe["answer"]["verified"], false, "{sbe}");
}

/// P2-ADJ-0002, provisioning side: the owner's binding authority is installed only from the administrator domain,
/// only on a machine provisioned from a root that delegates `t2-binding`, only when signed by that role, unexpired,
/// not older than what the machine already accepted, naming this machine when it names machines, and authorising
/// exactly the key presented. Rotation keeps the retired key's standing; an older authority is refused (it could
/// re-enable a revoked key); nothing secret is ever printed.
#[test]
fn a_t2_binding_authority_installs_only_from_the_owners_provisioned_root() {
    use crate::srr_material::*;
    let (root, g) = setup_fixture_unprovisioned("greenfield", "r3-bind", "S-bind");
    let b1 = suite_binding();
    let bind = |g: &Gov, auth: &Path, key: &Path| -> Out {
        g.run(&[
            "trust",
            "bind",
            "--authority",
            auth.to_str().unwrap(),
            "--key",
            key.to_str().unwrap(),
        ])
    };
    // unprovisioned: refused
    assert_eq!(
        bind(&g, &b1.authority, &b1.key_file).error_code(),
        "T2_BINDING_UNPROVISIONED"
    );
    // a root that delegates no t2-binding role: refused, typed
    let (_r2, g2) = setup_fixture_unprovisioned("greenfield", "r3-bind-nodelegation", "S-bind2");
    let p = Publisher::new();
    let plain_root = admin_file("plain-root-1.json", &p.root_json(1, &far_future()));
    g2.ok(&[
        "trust",
        "provision",
        "--anchor",
        plain_root.to_str().unwrap(),
    ]);
    assert_eq!(
        bind(&g2, &b1.authority, &b1.key_file).error_code(),
        "T2_BINDING_NOT_DELEGATED"
    );
    // provision this machine from the owner's root (anchor only)
    provision_anchor_only(&g);
    let mid = g.ok(&["trust", "status"])["machine_id"]
        .as_str()
        .unwrap()
        .to_string();
    let exp = far_future();
    let k1 = b1.key;
    // signed by a key that is not the t2-binding role: refused
    let intruder = ephemeral_key();
    let forged = admin_file(
        "r3-forged-authority.json",
        &binding_authority_doc(
            "suite-owner",
            5,
            &exp,
            &[(&k1, "active")],
            None,
            &[&intruder],
        ),
    );
    assert_eq!(
        bind(&g, &forged, &b1.key_file).error_code(),
        "SRR_THRESHOLD_NOT_MET"
    );
    // modified after signing: refused
    let tampered_text = std::fs::read_to_string(&b1.authority)
        .unwrap()
        .replace("\"version\":1", "\"version\":9");
    let tampered = admin_file("r3-tampered-authority.json", &tampered_text);
    assert_eq!(
        bind(&g, &tampered, &b1.key_file).error_code(),
        "SRR_THRESHOLD_NOT_MET"
    );
    // expired: refused
    let expired = admin_file(
        "r3-expired-authority.json",
        &binding_authority_doc(
            "suite-owner",
            5,
            &past(),
            &[(&k1, "active")],
            None,
            &[binding_role_key()],
        ),
    );
    assert_eq!(
        bind(&g, &expired, &b1.key_file).error_code(),
        "T2_BINDING_AUTHORITY_EXPIRED"
    );
    // a key the authority does not authorise: refused
    let other = ephemeral_secret();
    let other_file = binding_key_file(&other, "r3-other-key");
    assert_eq!(
        bind(&g, &b1.authority, &other_file).error_code(),
        "T2_BINDING_KEY_NOT_AUTHORISED"
    );
    // an entry naming the key's id with another key's commitment: refused
    let mut doc: Value = serde_json::from_str(&binding_authority_doc(
        "suite-owner",
        5,
        &exp,
        &[(&k1, "active")],
        None,
        &[binding_role_key()],
    ))
    .unwrap();
    doc["signed"]["keys"][0]["commitment"] =
        json!(gov_runtime::srr::binding::commitment_of(&other));
    let mismatched = admin_file(
        "r3-mismatched-authority.json",
        &envelope(&doc["signed"], &[binding_role_key()]),
    );
    assert_eq!(
        bind(&g, &mismatched, &b1.key_file).error_code(),
        "T2_BINDING_KEY_MISMATCH"
    );
    // an authority that lists other machines only: refused
    let elsewhere = admin_file(
        "r3-other-machines-authority.json",
        &binding_authority_doc(
            "suite-owner",
            5,
            &exp,
            &[(&k1, "active")],
            Some(&["0123456789abcdef0123456789abcdef".to_string()]),
            &[binding_role_key()],
        ),
    );
    assert_eq!(
        bind(&g, &elsewhere, &b1.key_file).error_code(),
        "T2_BINDING_MACHINE_NOT_AUTHORISED"
    );
    // material from inside the repository: refused
    let inside = root.join("t2-authority.json");
    std::fs::copy(&b1.authority, &inside).unwrap();
    assert_eq!(
        bind(&g, &inside, &b1.key_file).error_code(),
        "T2_BINDING_FROM_REPOSITORY_REFUSED"
    );
    let inside_key = root.join("t2-key.json");
    std::fs::copy(&b1.key_file, &inside_key).unwrap();
    assert_eq!(
        bind(&g, &b1.authority, &inside_key).error_code(),
        "T2_BINDING_FROM_REPOSITORY_REFUSED"
    );
    // the environment cannot carry authority
    assert_eq!(
        g.with_env("GOV_TRUST_OVERRIDE", "1")
            .run(&[
                "trust",
                "bind",
                "--authority",
                b1.authority.to_str().unwrap(),
                "--key",
                b1.key_file.to_str().unwrap()
            ])
            .error_code(),
        "SRR_ENV_CANNOT_CREATE_AUTHORITY"
    );
    assert_eq!(g.ok(&["trust", "status"])["t2_binding"]["bound"], false);
    // a machine that sealed records before it was bound keeps its machine-local key (never destroyed)
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "bindx",
        "--alias",
        "fx-bindx",
    ]);
    let local = g.ok(&[
        "gate",
        "create",
        "--question",
        "Sealed before binding?",
        "--fields",
        &crate::ws03::package(json!({})),
    ])["id"]
        .as_str()
        .unwrap()
        .to_string();
    let local_key = g.ok(&["trust", "status"])["t2_binding"]["sealing_key_id"].clone();
    assert!(local_key.is_string());
    // the machine is authorised: the listed machine and the right key
    let listed = admin_file(
        "r3-listed-authority.json",
        &binding_authority_doc(
            "suite-owner",
            2,
            &exp,
            &[(&k1, "active")],
            Some(&[mid.clone()]),
            &[binding_role_key()],
        ),
    );
    let r = g.ok(&[
        "trust",
        "bind",
        "--authority",
        listed.to_str().unwrap(),
        "--key",
        b1.key_file.to_str().unwrap(),
    ]);
    assert_eq!(r["bound"], true, "{r}");
    assert_eq!(r["sealing_key_id"], json!(b1.key_id));
    assert_eq!(r["machine_local_key_kept"], local_key, "{r}");
    assert!(
        !r.to_string().contains(&hex::encode(k1)),
        "bind printed key material"
    );
    let st = g.ok(&["trust", "status"]);
    assert!(
        !st.to_string().contains(&hex::encode(k1)),
        "trust status printed key material"
    );
    let t2 = &st["t2_binding"];
    assert_eq!(t2["bound"], true);
    assert_eq!(t2["authority"]["version"], 2);
    assert!(t2["held_keys"]
        .as_array()
        .unwrap()
        .iter()
        .any(|h| h["key_id"] == local_key && h["standing"] == "NOT_AUTHORISED"));
    // the record sealed with the machine-local key is not an owner fact: not honoured once the machine is bound
    assert_ne!(g.ok(&["gate", "show", &local])["t2"]["binding"], "VERIFIED");
    // idempotent re-bind
    g.ok(&[
        "trust",
        "bind",
        "--authority",
        listed.to_str().unwrap(),
        "--key",
        b1.key_file.to_str().unwrap(),
    ]);
    // an older authority is refused (it could re-enable a revoked key); a different one at the same version too
    assert_eq!(
        bind(&g, &b1.authority, &b1.key_file).error_code(),
        "T2_BINDING_AUTHORITY_ROLLBACK"
    );
    let same_version = admin_file(
        "r3-same-version-authority.json",
        &binding_authority_doc(
            "suite-owner",
            2,
            &exp,
            &[(&k1, "active")],
            None,
            &[binding_role_key()],
        ),
    );
    assert_eq!(
        bind(&g, &same_version, &b1.key_file).error_code(),
        "T2_BINDING_AUTHORITY_CONFLICT"
    );
    // rotation: version 3 makes k2 active and retires k1; the machine seals with k2 and still knows k1 as RETIRED
    let k2 = ephemeral_secret();
    let k2_file = binding_key_file(&k2, "r3-rotated-key");
    let v3 = admin_file(
        "r3-rotated-authority.json",
        &binding_authority_doc(
            "suite-owner",
            3,
            &exp,
            &[(&k2, "active"), (&k1, "retired")],
            None,
            &[binding_role_key()],
        ),
    );
    let r3 = g.ok(&[
        "trust",
        "bind",
        "--authority",
        v3.to_str().unwrap(),
        "--key",
        k2_file.to_str().unwrap(),
    ]);
    let k2_id = gov_runtime::srr::binding::key_id_of(&k2);
    assert_eq!(r3["sealing_key_id"], json!(k2_id));
    let held = g.ok(&["trust", "status"])["t2_binding"]["held_keys"].clone();
    for (id, standing) in [(k2_id.as_str(), "ACTIVE"), (b1.key_id.as_str(), "RETIRED")] {
        assert!(
            held.as_array()
                .unwrap()
                .iter()
                .any(|h| h["key_id"] == json!(id) && h["standing"] == standing),
            "{id} {standing}: {held}"
        );
    }
    // and version 2 is now older than what the machine accepted
    assert_eq!(
        bind(&g, &listed, &b1.key_file).error_code(),
        "T2_BINDING_AUTHORITY_ROLLBACK"
    );
}

/// OWNER-DECISION-0006 §6 bullet 4: installing a binding authority is a trust-policy mutation, refused while the
/// machine is marked `DEGRADED — RECOVERY ONLY`.
#[test]
fn a_binding_authority_is_not_installed_below_floor() {
    let (_proj, g, prev) = installed_previous("r3-bind-bg");
    approve_update(&g);
    g.ok(&[
        "update",
        "--apply",
        "--source",
        signed_source(),
        "--approve",
        "--by",
        "owner",
    ]);
    // restore the release below the high-water under the owner's break-glass authorisation
    break_glass(&g, &prev, "r3-bind-bg");
    g.ok(&["update", "--rollback", "--break-glass"]);
    assert!(g.ok(&["trust", "status"])["degraded"].is_object());
    let k = crate::srr_material::ephemeral_secret();
    let auth = admin_file(
        "r3-bg-authority.json",
        &binding_authority_doc(
            "suite-owner",
            7,
            &crate::srr_material::far_future(),
            &[(&k, "active")],
            None,
            &[binding_role_key()],
        ),
    );
    let kf = binding_key_file(&k, "r3-bg-key");
    let e = g.err(&[
        "trust",
        "bind",
        "--authority",
        auth.to_str().unwrap(),
        "--key",
        kf.to_str().unwrap(),
    ]);
    assert_eq!(e.error_code(), "SRR_BELOW_FLOOR_REFUSED", "{}", e.envelope);
    // the machine still seals with the key it was bound to
    assert_eq!(
        g.ok(&["trust", "status"])["t2_binding"]["sealing_key_id"],
        json!(suite_binding().key_id)
    );
}

// ============================================================================================ kernel payload/version

/// Kernel payload/version consistency (WS-8 r2 IP-R2-WS08-6, WS-9 r2 IP-R2-3, WS-7 r2 IP-W7-5): the working tree is
/// the next release (4.1.6) — `release/releases/4.1.5` is immutable and its payload differs — and the schema versions
/// the payload declares are the schema files it ships. `release build` refuses a new release whose declared schema
/// versions drift from its files (either direction) or whose payload the kernel's own secret scanner flags.
#[test]
fn the_next_kernel_payload_is_version_consistent_and_release_build_refuses_drift() {
    let croot = canonical_root();
    let kernel: Value = gov_runtime::util::read_yaml(&croot.join("framework/KERNEL.yaml")).unwrap();
    assert_eq!(kernel["version"], gov_runtime::VERSION);
    assert_eq!(
        gov_runtime::VERSION,
        "4.1.6",
        "the recorded next version (M-4.1.5-4.1.6)"
    );
    assert_eq!(kernel["cli_version"], gov_runtime::CLI_VERSION);
    assert_eq!(kernel["runtime_version"], gov_runtime::RUNTIME_VERSION);
    assert_eq!(
        gov_runtime::kernel::embedded::version(),
        gov_runtime::VERSION,
        "the payload compiled into gov is the working tree's"
    );
    assert!(gov_runtime::kernel::schema_version_problems(&croot.join("framework")).is_empty());
    // the shipped 4.1.5 is untouched and differs from the next payload
    let shipped = json(&croot.join("release/releases/4.1.5"), "manifest.json");
    assert_eq!(shipped["version"], "4.1.5");
    let (_, next_hash, _, next_version) = crate::srr_material::measure(&croot.join("framework"));
    assert_eq!(next_version, gov_runtime::VERSION);
    assert_ne!(json!(next_hash), shipped["release_hash"]);
    // a canonical tree whose payload drifts is refused by `release build`
    let g = Gov::new(&croot, "S-r3-rel");
    let canon = |tag: &str| -> PathBuf {
        let d = tmp(tag);
        for sub in ["framework", "migrations", "tools"] {
            copy_dir(&croot.join(sub), &d.join(sub));
        }
        d
    };
    let build = |c: &Path, out: &Path| -> Out {
        g.run(&[
            "release",
            "build",
            "--version",
            gov_runtime::VERSION,
            "--canonical",
            c.to_str().unwrap(),
            "--out",
            out.to_str().unwrap(),
            "--certification",
            "READY_FOR_INDEPENDENT_REVERIFICATION",
        ])
    };
    // control: the unmodified payload builds and records its consistency
    let ok = canon("r3-canon-ok");
    let o = build(&ok, &ok.join("out"));
    assert!(o.ok(), "{}", o.envelope);
    assert_eq!(
        o.result()["pre_release_checks"]["kernel_payload"]["schema_versions_consistent"],
        true
    );
    // (a) a schema file changes version without KERNEL.yaml
    let a = canon("r3-canon-schema");
    let sp = a.join("framework/schemas/task.schema.json");
    let mut sch: Value = gov_runtime::util::read_json(&sp).unwrap();
    sch["x-schema-version"] = json!("9.0.0");
    std::fs::write(&sp, serde_json::to_string_pretty(&sch).unwrap()).unwrap();
    let e = build(&a, &a.join("out"));
    assert_eq!(
        e.error_code(),
        "RELEASE_KERNEL_INCONSISTENT",
        "{}",
        e.envelope
    );
    assert!(!a.join("out/releases").join(gov_runtime::VERSION).exists());
    // (b) KERNEL.yaml declares a version the file does not carry
    let b = canon("r3-canon-declared");
    let kp = b.join("framework/KERNEL.yaml");
    let text = std::fs::read_to_string(&kp)
        .unwrap()
        .replace("  decision: 1.2.0\n", "  decision: 1.1.0\n");
    std::fs::write(&kp, text).unwrap();
    assert_eq!(
        build(&b, &b.join("out")).error_code(),
        "RELEASE_KERNEL_INCONSISTENT"
    );
    // (c) a versioned schema the kernel does not declare
    let c = canon("r3-canon-undeclared");
    std::fs::write(
        c.join("framework/schemas/extra.schema.json"),
        "{\"$schema\": \"https://json-schema.org/draft/2020-12/schema\", \"x-schema-version\": \"1.0.0\", \"type\": \"object\"}",
    )
    .unwrap();
    assert_eq!(
        build(&c, &c.join("out")).error_code(),
        "RELEASE_KERNEL_INCONSISTENT"
    );
    // (d) a kernel file the kernel's own scanner flags (the literal is assembled here, never stored in a file)
    let d = canon("r3-canon-secret");
    let literal = format!("AKIA{}", "IOSFODNN7EXAMPLE");
    std::fs::write(
        d.join("framework/skills/NOTES.md"),
        format!("example: {literal}\n"),
    )
    .unwrap();
    let e = build(&d, &d.join("out"));
    assert_eq!(e.error_code(), "RELEASE_PAYLOAD_SECRET", "{}", e.envelope);
    assert!(
        !e.envelope.to_string().contains(&literal),
        "the refusal must not echo the secret"
    );
    // the shipped releases were never touched
    assert_eq!(
        git(&croot, &["status", "--porcelain", "--", "release/releases"]).1,
        ""
    );
}

/// The `framework/health` decision (WS-8 r2 IP-R2-WS08-6 / IP-WS02-16): the kernel-skill scenario checks ship in the
/// 4.1.6 payload (`health` in `payload_dirs`) **exactly when** the kernel's own secret scanner finds nothing in them.
/// Until WS-2 removes the planted `AKIA…EXAMPLE` literal (round 3), shipping them would make every installation carry
/// and flag it (D011 critical), so they stay out and the runtime's compiled copy serves the checks; once the file is
/// clean, this test fails until `health` is added — the integration step is enforced, not remembered.
#[test]
fn the_health_checks_ship_in_the_payload_exactly_when_the_kernel_scanner_finds_them_clean() {
    let croot = canonical_root();
    let kernel: Value = gov_runtime::util::read_yaml(&croot.join("framework/KERNEL.yaml")).unwrap();
    let shipped = kernel["payload_dirs"]
        .as_array()
        .unwrap()
        .iter()
        .any(|d| d == "health");
    // the scanner the payload itself would carry, over a payload that includes `health/`
    let staged = tmp("r3-health-payload");
    gov_runtime::kernel::stage_payload(&croot.join("framework"), &staged.join("kernel")).unwrap();
    copy_dir(
        &croot.join("framework/health"),
        &staged.join("kernel/health"),
    );
    let hits: Vec<Value> = gov_runtime::kernel::payload_secret_hits(&staged.join("kernel"))
        .into_iter()
        .filter(|h| h["path"].as_str().unwrap_or("").starts_with("health/"))
        .collect();
    if hits.is_empty() {
        assert!(
            shipped,
            "framework/health is clean under the kernel's own scanner: add `health` to framework/KERNEL.yaml payload_dirs (the 4.1.6 payload carries the scenario checks with the kernel skills they verify)"
        );
    } else {
        assert!(
            !shipped,
            "framework/health is flagged by the kernel's own scanner ({hits:?}) and must not ship in the payload"
        );
    }
    // either way the payload that ships is clean
    assert!(
        gov_runtime::kernel::payload_secret_hits(&croot.join("framework"))
            .iter()
            .filter(|h| {
                let p = h["path"].as_str().unwrap_or("");
                kernel["payload_dirs"]
                    .as_array()
                    .unwrap()
                    .iter()
                    .any(|d| p.starts_with(&format!("{}/", d.as_str().unwrap())))
            })
            .next()
            .is_none()
    );
}

// ============================================================================================ update: availability + BC-P2-31

fn installed_previous(tag: &str) -> (PathBuf, Gov, PathBuf) {
    let root = tmp(tag);
    let proj = root.join("project");
    std::fs::create_dir_all(&proj).unwrap();
    write(&proj, "README.md", "# upd project\n");
    git_init_commit(&proj);
    let g = Gov::new(&proj, "S-r3-upd");
    provision(&g);
    let prev = signed_copy(
        &canonical_root().join("fixtures/update/previous-release/4.1.1"),
        &format!("{tag}-4.1.1"),
        sequence_of("4.1.1"),
    );
    g.ok(&[
        "init",
        "--source",
        prev.to_str().unwrap(),
        "--name",
        "upd",
        "--alias",
        &format!("fx-{tag}"),
    ]);
    git_commit_all(&proj, "4.1.1 installed");
    (proj, g, prev)
}

fn approve_update(g: &Gov) {
    let e = g.err(&["update", "--apply", "--source", signed_source()]);
    assert_eq!(e.error_code(), "HUMAN_GATE_REQUIRED", "{}", e.envelope);
    let gid = e.details()["gate"].as_str().unwrap().to_string();
    crate::ws03::human_decide(g, &gid, "A");
}

/// The availability rule (P2-HO-0031) at `update --apply`'s entry guard (WS-8 r2 IP-R2-WS08-5): a hard-block whose
/// check reads nothing an update replaces (records) refuses the update at entry — typed, naming the block and its
/// scope, before a gate is raised; blocks the update is the remedy for (a 4.1.1 kernel's overlay deficit) do not
/// refuse it, and the update clears them. BC-P2-31: the rollback snapshot lives in the non-rebuildable state store,
/// survives the deletion of everything the product classifies derived, and a legacy snapshot is relocated.
#[test]
fn update_entry_guard_is_scoped_and_snapshots_survive_derived_state_deletion() {
    // ---- a block no update can repair: a record that does not parse (D023, records only)
    let (proj, g, _) = installed_previous("r3-upd-block");
    write(
        &proj,
        "spec/decisions/D-0777.yaml",
        "id: D-0777\ntype: decision\n  bad: [indent\n",
    );
    let _ = g.run(&["doctor"]);
    let gates_before = std::fs::read_dir(proj.join("spec/decisions"))
        .map(|rd| {
            rd.flatten()
                .filter(|e| e.file_name().to_string_lossy().starts_with("HDG-"))
                .count()
        })
        .unwrap_or(0);
    let e = g.err(&["update", "--apply", "--source", signed_source()]);
    assert_eq!(e.error_code(), "HEALTH_HARD_BLOCK", "{}", e.envelope);
    let d = e.details();
    assert_eq!(d["operation"], "update.apply");
    assert!(
        d["blocks"]
            .as_array()
            .unwrap()
            .iter()
            .any(|b| b["check"] == "D023" && b["scope"] == "global"),
        "{d}"
    );
    assert!(d["rule"].as_str().unwrap().contains("availability rule"));
    let gates_after = std::fs::read_dir(proj.join("spec/decisions"))
        .map(|rd| {
            rd.flatten()
                .filter(|e| e.file_name().to_string_lossy().starts_with("HDG-"))
                .count()
        })
        .unwrap_or(0);
    assert_eq!(
        gates_after, gates_before,
        "a gate was raised for an update the guard refuses"
    );
    assert_eq!(yaml(&proj, "governance/framework.lock")["version"], "4.1.1");

    // ---- the blocks an update is the remedy for do not refuse it: the 4.1.1 overlay/kernel deficit
    let (proj, g, prev) = installed_previous("r3-upd-remedy");
    let _ = g.run(&["doctor"]);
    let st = g.ok(&["health", "status"]);
    let blocking: Vec<String> = st["blocks"]
        .as_array()
        .unwrap()
        .iter()
        .filter(|b| {
            b["operations"]
                .as_array()
                .unwrap()
                .iter()
                .any(|o| o == "update.apply")
        })
        .map(|b| b["check"].as_str().unwrap().to_string())
        .collect();
    assert!(
        !blocking.is_empty(),
        "the fixture no longer carries a block governing update.apply: {st}"
    );
    for c in &blocking {
        assert!(gov_runtime::update::update_can_remedy(c), "{c}");
    }
    approve_update(&g);
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
    let remedied: Vec<String> = ap["details"]["remedied_blocks"]
        .as_array()
        .unwrap()
        .iter()
        .map(|b| b["check"].as_str().unwrap().to_string())
        .collect();
    assert!(!remedied.is_empty(), "{ap}");
    let after = g.ok(&["health", "status"]);
    assert!(
        !after["blocks"]
            .as_array()
            .unwrap()
            .iter()
            .any(|b| remedied.contains(&b["check"].as_str().unwrap().to_string())),
        "the update did not clear the blocks it was let through for: {after}"
    );

    // ---- BC-P2-31: the snapshot is in the state store, not in the derived runtime directory
    let snap = proj
        .join(".governance-state/update")
        .join(gov_runtime::VERSION);
    assert!(snap.join("snapshot.json").exists());
    assert!(!proj.join(".governance-runtime/update").exists());
    assert_eq!(
        git(&proj, &["status", "--porcelain", "--", ".governance-state"]).1,
        ""
    );
    // deleting everything the product classifies derived (the whole runtime directory) keeps the way back
    std::fs::remove_dir_all(proj.join(".governance-runtime")).unwrap();
    assert_eq!(
        g.err(&["update", "--rollback"]).error_code(),
        "SRR_BELOW_FLOOR"
    );
    break_glass(&g, &prev, "r3-upd-rollback");
    let rb = g.ok(&["update", "--rollback", "--break-glass"]);
    assert_eq!(rb["rolled_back_to"], "4.1.1");
    assert!(snap.join("consumed.json").exists());

    // ---- a snapshot an older gov left at the legacy location is relocated once, then used
    let (proj, g, _) = installed_previous("r3-upd-legacy");
    approve_update(&g);
    g.ok(&[
        "update",
        "--apply",
        "--source",
        signed_source(),
        "--approve",
        "--by",
        "owner",
    ]);
    let state = proj.join(".governance-state/update");
    let legacy = proj.join(".governance-runtime/update");
    std::fs::create_dir_all(proj.join(".governance-runtime")).unwrap();
    std::fs::rename(&state, &legacy).unwrap();
    // the relocation happens under the store API; a below-floor rollback is still refused by the floor, after it
    assert_eq!(
        g.err(&["update", "--rollback"]).error_code(),
        "SRR_BELOW_FLOOR"
    );
    assert!(state
        .join(gov_runtime::VERSION)
        .join("snapshot.json")
        .exists());
    assert!(!legacy.exists());
}
