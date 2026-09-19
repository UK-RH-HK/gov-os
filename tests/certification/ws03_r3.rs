//! Repair iteration 1, round 3, WS-3 (P2-AR-0034): P2-ADJ-0002 (T2 facts portable across the owner's provisioned
//! machines; forged, unprovisioned, unauthorised and foreign records still refused), the T2 completeness items, the
//! BC-P2-31 control-state move and the routed integration points.
//!
//! Builder regression evidence (Contract v3 O3), not acceptance evidence. Every scenario drives the `gov` binary.
//! The owner's material is TEST MATERIAL ONLY: published seeds (`srr_material::key`) and a published 32-byte binding
//! key. Machines are the harness's simulated machines (one per repository root, `XDG_STATE_HOME`), each provisioned
//! explicitly here with the root the scenario needs — the suite root (`common::suite_root_file`) delegates no
//! `t2-binding` role in this tree (integration point for WS-8's harness helper).
#![allow(dead_code)]
use crate::common::*;
use crate::srr_material::{envelope, far_future, key, key_entry, past, root_doc, TestKey};
use serde_json::{json, Value};
use std::path::{Path, PathBuf};

// ============================================================================================ owner material

/// The owner's `t2-binding` role key. NOT A PRODUCTION KEY: derived from a published seed.
pub fn t2_role_key() -> TestKey {
    key(0x6b)
}

/// The owner's T2 binding key. NOT A PRODUCTION KEY: a published 32-byte value.
pub fn binding_key() -> Vec<u8> {
    vec![0x3c; 32]
}

/// A directory in the simulated administrator domain (outside every project, no `.git`/`governance` component).
pub fn admin_dir(tag: &str) -> PathBuf {
    let d = std::env::temp_dir().join(format!(
        "gov-cert-admin-t2-{tag}-{}-{}",
        std::process::id(),
        gov_runtime::util::short_uuid()
    ));
    std::fs::create_dir_all(&d).unwrap();
    d.canonicalize().unwrap()
}

fn write_admin(dir: &Path, name: &str, text: &str) -> PathBuf {
    let p = dir.join(name);
    std::fs::write(&p, text).unwrap();
    p
}

/// Root metadata of an owner: `root_keys` at 2-of-3, the suite's release/snapshot/timestamp/recovery keys (so the
/// releases the suite signs install), `human` as the `human-gate` key, and the `t2-binding` role delegated to `t2`
/// (none: the role is not delegated).
pub fn root_of(version: u64, root_keys: [&TestKey; 3], human: &TestKey, t2: &[&TestKey]) -> Value {
    let p = suite_publisher();
    let mut doc = root_doc(
        version,
        &far_future(),
        &root_keys,
        2,
        &[&p.release],
        &p.snapshot,
        &p.timestamp,
        Some(&p.recovery),
    );
    let (kid, e) = key_entry(human);
    doc["keys"][kid.as_str()] = e;
    doc["roles"]["human-gate"] = json!({"keyids": [human.keyid.clone()], "threshold": 1});
    if !t2.is_empty() {
        for k in t2 {
            let (kid, e) = key_entry(k);
            doc["keys"][kid.as_str()] = e;
        }
        doc["roles"]["t2-binding"] = json!({"keyids": t2.iter().map(|k| k.keyid.clone()).collect::<Vec<_>>(), "threshold": 1});
    }
    doc
}

/// The owner's root (the suite publisher's root keys; `human-gate` → `ws03::owner`; `t2-binding` → `t2`).
pub fn owner_root(version: u64, t2: &[&TestKey]) -> String {
    let p = suite_publisher();
    envelope(
        &root_of(
            version,
            [&p.root_a, &p.root_b, &p.root_c],
            &crate::ws03::owner(),
            t2,
        ),
        &[&p.root_a, &p.root_b],
    )
}

/// Another owner's root: other root keys, another human-gate key, another `t2-binding` key (same release keys, so the
/// suite's releases install on its machines).
pub fn foreign_root() -> String {
    let (a, b, c) = (key(0x81), key(0x82), key(0x83));
    envelope(
        &root_of(1, [&a, &b, &c], &key(0x8a), &[&key(0x8b)]),
        &[&a, &b],
    )
}

/// A `t2-binding-provisioning` bundle: the binding key and the owner-signed `t2-binding-authority` document.
pub fn bundle(binding: &[u8], signers: &[&TestKey], expires: &str) -> String {
    let signed = json!({"_type": "t2-binding-authority", "spec_version": "srr/1", "product": gov_runtime::FRAMEWORK_NAME,
        "version": 1, "authority_id": gov_runtime::t2::authority_id_of(binding),
        "key_commitment": gov_runtime::t2::key_commitment_of(binding), "issued": "2026-09-19T00:00:00Z",
        "expires": expires, "owner": "certification owner (published test seed)"});
    format!(
        "{{\"_type\":\"t2-binding-provisioning\",\"key_hex\":\"{}\",\"authority\":{}}}",
        hex::encode(binding),
        envelope(&signed, signers)
    )
}

/// The owner's administrator material for one scenario: the owner root (with the `t2-binding` delegation) and the
/// owner's binding bundle, in an administrator-domain directory.
pub struct OwnerMaterial {
    pub dir: PathBuf,
    pub root: PathBuf,
    pub bundle: PathBuf,
}

pub fn owner_material(tag: &str) -> OwnerMaterial {
    let dir = admin_dir(tag);
    let root = write_admin(&dir, "owner-root-1.json", &owner_root(1, &[&t2_role_key()]));
    let bundle = write_admin(
        &dir,
        "owner-t2-binding.json",
        &bundle(&binding_key(), &[&t2_role_key()], &far_future()),
    );
    OwnerMaterial { dir, root, bundle }
}

/// Provision `g`'s machine with `root_file` (administrator step).
pub fn provision_root(g: &Gov, root_file: &Path) {
    g.ok(&[
        "trust",
        "provision",
        "--anchor",
        root_file.to_str().unwrap(),
    ]);
}

/// Install the T2 binding bundle on `g`'s machine (administrator step).
pub fn install_binding(g: &Gov, bundle_file: &Path) -> Value {
    g.ok(&[
        "trust",
        "t2-binding",
        "--provision",
        bundle_file.to_str().unwrap(),
    ])
}

/// A clone of `src` at a new path — another simulated machine.
pub fn clone_of(src: &Path, tag: &str) -> (PathBuf, Gov) {
    let dir = tmp(tag);
    let dst = dir.join("repo");
    let (code, out) = git(
        src,
        &["clone", "-q", src.to_str().unwrap(), dst.to_str().unwrap()],
    );
    assert_eq!(code, 0, "{out}");
    git(&dst, &["config", "user.email", "cert@example.invalid"]);
    git(&dst, &["config", "user.name", "cert"]);
    let g = Gov::new(&dst, &format!("S-{tag}"));
    (dst, g)
}

/// Pull `from`'s commits into `into` (another machine's work arriving through Git).
pub fn pull(into: &Path, from: &Path) {
    let (code, out) = git(
        into,
        &["pull", "-q", "--no-rebase", from.to_str().unwrap(), "HEAD"],
    );
    assert_eq!(code, 0, "{out}");
}

// ============================================================================================ an independent seal check

fn hmac_sha256(key: &[u8], msg: &[u8]) -> Vec<u8> {
    assert!(key.len() <= 64);
    let mut k = [0u8; 64];
    k[..key.len()].copy_from_slice(key);
    let ipad: Vec<u8> = k.iter().map(|b| b ^ 0x36).collect();
    let opad: Vec<u8> = k.iter().map(|b| b ^ 0x5c).collect();
    let inner = hex::decode(gov_runtime::util::sha256_hex(
        &[ipad, msg.to_vec()].concat(),
    ))
    .unwrap();
    hex::decode(gov_runtime::util::sha256_hex(&[opad, inner].concat())).unwrap()
}

/// The canonical content a seal covers, re-implemented from the documented format (the record without its seal,
/// through the product's YAML writer and back, as canonical JSON; then the Markdown body).
fn canonical_content(data: &Value, body: &str) -> String {
    let mut d = data.clone();
    d.as_object_mut().unwrap().remove("os_binding");
    let text = gov_runtime::util::to_yaml(&d).unwrap();
    let rt: Value = serde_yaml::from_str(&text).unwrap();
    format!("{}\n{}", gov_runtime::util::canonical_json(&rt), body)
}

fn portable_mac(binding: &[u8], seal: &Value, content: &str) -> String {
    let s = |k: &str| seal[k].as_str().unwrap_or("").to_string();
    let msg = format!(
        "hmac-sha256/t2-v2\n{}\n{}\n{}\n{}\n{content}",
        s("authority"),
        s("machine"),
        s("operation"),
        s("at")
    );
    hex::encode(hmac_sha256(binding, msg.as_bytes()))
}

/// Does `data` carry a portable seal that verifies under the owner's binding key — computed here, independently of
/// the product? Returns the recorded operation.
pub fn owner_verifies(data: &Value) -> Option<String> {
    let seal = data.get("os_binding")?;
    if seal["alg"] != "hmac-sha256/t2-v2" {
        return None;
    }
    let want = portable_mac(&binding_key(), seal, &canonical_content(data, ""));
    (seal["mac"].as_str() == Some(want.as_str()))
        .then(|| seal["operation"].as_str().unwrap_or("").to_string())
}

/// Seal `data` as an OS writer holding the owner's binding authority would (the documented format), as `operation`.
pub fn owner_seal(data: &mut Value, operation: &str) {
    data.as_object_mut().unwrap().remove("os_binding");
    let aid = gov_runtime::t2::authority_id_of(&binding_key());
    let mut seal = json!({"alg": "hmac-sha256/t2-v2", "scope": "provisioned", "key_id": aid, "authority": aid,
        "machine": "certification-writer", "operation": operation, "at": "2026-09-19T00:00:00Z"});
    let mac = portable_mac(&binding_key(), &seal, &canonical_content(data, ""));
    seal["mac"] = json!(mac);
    data["os_binding"] = seal;
}

fn t2_of(g: &Gov, gate: &str) -> Value {
    g.ok(&["gate", "show", gate])["t2"].clone()
}

fn gate_with(g: &Gov, id: &str, q: &str, extra: Value) -> String {
    let mut fields: Value = serde_json::from_str(&crate::ws03::package(extra)).unwrap();
    fields["id"] = json!(id);
    g.ok(&[
        "gate",
        "create",
        "--question",
        q,
        "--fields",
        &fields.to_string(),
    ])["id"]
        .as_str()
        .unwrap()
        .to_string()
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

/// The T2 binding summary of the governance suite's `os_binding_integrity` family (per binding code).
fn binding_counts(g: &Gov) -> Value {
    let o = g.run(&["audit", "--no-persist", "--family", "os_binding_integrity"]);
    let r = if o.ok() { o.result() } else { o.details() };
    let fams = r["families"].clone();
    let fam = match &fams {
        Value::Array(a) => a
            .iter()
            .find(|f| f["id"] == "os_binding_integrity")
            .cloned()
            .unwrap_or(Value::Null),
        Value::Object(m) => m
            .get("os_binding_integrity")
            .cloned()
            .unwrap_or(Value::Null),
        _ => Value::Null,
    };
    assert!(!fam.is_null(), "no os_binding_integrity family in {r}");
    fam["detail"]["unverified_by_binding"].clone()
}

// ============================================================================================ P2-ADJ-0002

/// **P2-ADJ-0002.** A T2 fact written by an OS operation on one of the owner's provisioned machines is honoured on
/// every other such machine after a Git clone/pull — gates, decisions, CIT state, plugin registrations and governed
/// evidence — while a record written by anything else is refused, typed and observable: a hand edit (BROKEN), a
/// machine provisioned for the owner but not given the binding authority, an unprovisioned machine, and a machine of
/// another owner (FOREIGN). The seal format is re-derived here from its documentation, not taken from the product.
#[test]
fn os_written_facts_are_honoured_on_the_owners_other_provisioned_machines_and_nowhere_else() {
    let m = owner_material("x");
    // ---------------------------------------------------------------- machine A: provision, authority, install
    let (a, ga) = setup_fixture_unprovisioned("greenfield", "t2x-a", "S-A");
    provision_root(&ga, &m.root);
    let st = ga.ok(&["trust", "t2-binding"]);
    assert_eq!(st["portable"], false, "{st}");
    assert!(
        st["sealing"]["reason"]
            .as_str()
            .unwrap()
            .contains("no T2 binding authority is installed"),
        "{st}"
    );
    let inst = install_binding(&ga, &m.bundle);
    let aid = gov_runtime::t2::authority_id_of(&binding_key());
    assert_eq!(inst["authority_id"], json!(aid), "{inst}");
    assert_eq!(inst["action"], "installed");
    assert_eq!(inst["sealing"]["scope"], "provisioned", "{inst}");
    assert!(
        !inst.to_string().contains(&hex::encode(binding_key())),
        "the key is never printed"
    );
    // the authority id and commitment are derived as documented
    assert_eq!(
        aid,
        format!(
            "t2a-{}",
            &gov_runtime::util::sha256_hex(
                &[b"t2-binding-authority-id:".as_slice(), &binding_key()].concat()
            )[..16]
        )
    );
    assert_eq!(install_binding(&ga, &m.bundle)["action"], "unchanged");
    ga.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "t2x",
        "--alias",
        "t2x",
    ]);
    // spec for the CIT
    write_yaml(
        &a,
        "spec/features/F-0001.yaml",
        &json!({"id": "F-0001", "type": "feature", "title": "Totals", "status": "ACTIVE", "state_class": "AUTHORITATIVE", "requirements": ["REQ-0001"], "readiness": {"requirements": "PRESENT"}}),
    );
    write_yaml(
        &a,
        "spec/requirements/REQ-0001.yaml",
        &json!({"id": "REQ-0001", "type": "requirement", "title": "Totals are exact", "status": "ACTIVE", "state_class": "AUTHORITATIVE", "feature": "F-0001", "kind": "functional", "statement": "totals are integer cents", "acceptance_criteria": ["2 x 199 = 398"]}),
    );
    // a plugin (the implementation is inside the project, so its binding travels with it)
    write(
        &a,
        "tools/t2p.sh",
        &format!("#!/bin/sh\ncat >/dev/null\nprintf '%s\\n' '{EMBED_OK}'\n"),
    );
    write_yaml(
        &a,
        "governance/project/plugins/t2p.yaml",
        &json!({"plugin_id": "t2p", "capability": "embed", "version": "1", "command": ["sh", "tools/t2p.sh"]}),
    );
    git_commit_all(&a, "init, spec, plugin");
    ga.ok(&["rebuild-memory"]);

    // ---------------------------------------------------------------- T2 facts written on A
    // (1) a gate answered by the owner on A, and its decision
    let g1 = gate_with(&ga, "HDG-0101", "Adopt integer cents?", json!({}));
    let ans = crate::ws03::human_decide(&ga.with_role("orchestrator"), &g1, "A");
    let d1 = ans["decision"].as_str().unwrap().to_string();
    // (2) a gate raised on A, to be answered on another machine
    let g2 = gate_with(&ga, "HDG-0102", "Adopt the ledger layout?", json!({}));
    // (3) a CIT proposed and simulated on A (sealed CIT state), its gate answered by the owner on A
    let mf = a.parent().unwrap().join("t2x-manifest.json");
    std::fs::write(
        &mf,
        json!([{"op": "set_field", "target": "REQ-0001", "field": "statement", "value": "rounded half-even"}]).to_string(),
    )
    .unwrap();
    let c = ga.ok(&[
        "cit",
        "propose",
        "--proposal",
        "rounding",
        "--trigger",
        "behaviour_change",
        "--targets",
        "REQ-0001",
        "--manifest",
        mf.to_str().unwrap(),
    ]);
    let cid = c["id"].as_str().unwrap().to_string();
    let cgate = c["simulation"]["human_gate"].as_str().unwrap().to_string();
    crate::ws03::human_decide(&ga.with_role("orchestrator"), &cgate, "A");
    // (4) a plugin registration approved by the owner on A
    let te_a = ga.with_role("tooling-engineer");
    crate::ws07::register_approved(&te_a, &a.join("governance/project/plugins/t2p.yaml"));
    assert!(invoke(&te_a, "t2p").ok());
    // (5) governed evidence: a persisted governance-suite record
    let au = ga.run(&["audit"]);
    let _ = au;
    git_commit_all(&a, "T2 facts written on machine A");
    // every one of them is sealed under the owner's authority on A, and the seal is exactly the documented one
    let g1_rec = yaml(&a, &format!("spec/decisions/{g1}.yaml"));
    assert_eq!(
        owner_verifies(&g1_rec).as_deref(),
        Some("gate answer"),
        "{}",
        g1_rec["os_binding"]
    );
    assert_eq!(g1_rec["os_binding"]["scope"], "provisioned");
    let d1_rec = yaml(&a, &format!("spec/decisions/{d1}.yaml"));
    assert_eq!(owner_verifies(&d1_rec).as_deref(), Some("gate answer"));
    let cit_rec = yaml(&a, &format!("spec/decisions/{cid}.yaml"));
    assert!(
        owner_verifies(&cit_rec["os_state"]).is_some(),
        "{}",
        cit_rec["os_state"]
    );
    let reg = json(&a, "governance/generated/plugin-registry.json");
    assert_eq!(
        owner_verifies(&reg["plugins"]["t2p"]).as_deref(),
        Some("plugins register")
    );
    assert!(owner_verifies(&reg).is_some());
    assert_eq!(t2_of(&ga, &g1)["scope"], "provisioned");

    // ---------------------------------------------------------------- machine B: the owner's second machine
    let (b, gb) = clone_of(&a, "t2x-b");
    provision_root(&gb, &m.root);
    install_binding(&gb, &m.bundle);
    gb.with_role("orchestrator")
        .ok(&["kernel", "reinstall", "--source", signed_source()]);
    gb.ok(&["rebuild-memory"]);
    // gates and decisions written on A are honoured on B
    let s1 = gb.ok(&["gate", "show", &g1]);
    assert_eq!(s1["t2"]["binding"], "VERIFIED", "{}", s1["t2"]);
    assert_eq!(s1["t2"]["scope"], "provisioned");
    assert_eq!(s1["answer"]["verified"], true, "{}", s1["answer"]);
    assert!(
        gb.ok(&["gate", "list"])
            .as_array()
            .unwrap()
            .iter()
            .all(|x| x["honoured"] != false),
        "no gate is unverified on B"
    );
    let counts_b = binding_counts(&gb);
    assert!(
        counts_b.as_object().map(|o| o.is_empty()).unwrap_or(true),
        "every T2 record and every governed evidence record written on A is honoured on B: {counts_b}"
    );
    // a gate raised on A is answered by the owner on B
    let ans2 = crate::ws03::human_decide(&gb.with_role("orchestrator"), &g2, "A");
    assert_eq!(ans2["answered_by_kind"], "human");
    // the CIT simulated and answered on A is approved and executed on B
    gb.with_role("orchestrator")
        .ok(&["cit", "approve", &cid, "--method", "human"]);
    gb.with_role("orchestrator").ok(&["cit", "execute", &cid]);
    assert_eq!(
        yaml(&b, "spec/requirements/REQ-0001.yaml")["statement"],
        "rounded half-even"
    );
    // the plugin registered on A runs on B
    let te_b = gb.with_role("tooling-engineer");
    let inv = invoke(&te_b, "t2p");
    assert!(inv.ok(), "{}", inv.envelope);
    git_commit_all(&b, "T2 facts written on machine B");
    // ... and what B wrote is honoured on A after a pull
    pull(&a, &b);
    let s2a = ga.ok(&["gate", "show", &g2]);
    assert_eq!(s2a["t2"]["binding"], "VERIFIED", "{}", s2a["t2"]);
    assert_eq!(s2a["answer"]["verified"], true);
    let cit_a = ga.ok(&["cit", "show", &cid]);
    assert_eq!(cit_a["cit_status"], "COMMITTED", "{cit_a}");
    assert!(owner_verifies(&yaml(&a, &format!("spec/decisions/{g2}.yaml"))).is_some());

    // ---------------------------------------------------------------- a hand edit is refused everywhere
    let rel = format!("spec/decisions/{d1}.yaml");
    let good = read(&b, &rel);
    let mut forged = yaml(&b, &rel);
    forged["chosen_option"] = json!("B");
    write_yaml(&b, &rel, &forged);
    let counts = binding_counts(&gb);
    assert_eq!(counts["BROKEN"], 1, "{counts}");
    write(&b, &rel, &good);

    // ---------------------------------------------------------------- machine D: provisioned, not given the authority
    let (d, gd) = clone_of(&a, "t2x-d");
    provision_root(&gd, &m.root);
    gd.with_role("orchestrator")
        .ok(&["kernel", "reinstall", "--source", signed_source()]);
    let std_ = gd.ok(&["trust", "t2-binding"]);
    assert_eq!(std_["portable"], false);
    assert_eq!(std_["sealing"]["scope"], "machine");
    let t = t2_of(&gd, &g1);
    assert_eq!(t["binding"], "FOREIGN", "{t}");
    assert_eq!(t["scope"], "provisioned");
    assert_eq!(
        gd.with_role("orchestrator")
            .err(&["cit", "approve", &cid, "--method", "human"])
            .error_code(),
        "T2_UNBOUND"
    );
    assert_eq!(
        invoke(&gd.with_role("tooling-engineer"), "t2p").error_code(),
        "PLUGIN_REGISTRATION_UNBOUND"
    );
    let cd = binding_counts(&gd);
    assert!(cd["FOREIGN"].as_u64().unwrap_or(0) >= 3, "{cd}");
    // what D writes is machine-scope: refused on B
    let gdid = gate_with(
        &gd,
        "HDG-0801",
        "Written on an unauthorised machine?",
        json!({}),
    );
    let td = t2_of(&gd, &gdid);
    assert_eq!(
        (td["binding"].as_str(), td["scope"].as_str()),
        (Some("VERIFIED"), Some("machine"))
    );
    std::fs::copy(
        d.join(format!("spec/decisions/{gdid}.yaml")),
        b.join(format!("spec/decisions/{gdid}.yaml")),
    )
    .unwrap();
    let tb = t2_of(&gb, &gdid);
    assert_eq!(
        (tb["binding"].as_str(), tb["scope"].as_str()),
        (Some("FOREIGN"), Some("machine")),
        "{tb}"
    );
    let e = gb
        .with_role("orchestrator")
        .err(&["gate", "present", &gdid]);
    assert_eq!(e.error_code(), "T2_UNBOUND", "{}", e.envelope);

    // ---------------------------------------------------------------- machine U: unprovisioned
    let (_u, gu) = clone_of(&a, "t2x-u");
    let su = gu.ok(&["trust", "t2-binding"]);
    assert_eq!(su["provisioned"], false);
    assert!(
        su["sealing"]["reason"]
            .as_str()
            .unwrap()
            .contains("unprovisioned"),
        "{su}"
    );
    let e = gu.err(&[
        "trust",
        "t2-binding",
        "--provision",
        m.bundle.to_str().unwrap(),
    ]);
    assert_eq!(
        e.error_code(),
        "T2_AUTHORITY_UNPROVISIONED",
        "{}",
        e.envelope
    );
    assert_eq!(t2_of(&gu, &g1)["binding"], "FOREIGN");
    // a record an unprovisioned machine wrote (bootstrap installation of the embedded payload) is refused on B
    let (u2, gu2) = setup_fixture_unprovisioned("greenfield", "t2x-u2", "S-U2");
    gu2.ok(&["init", "--name", "u2", "--alias", "u2"]);
    let ugate = gate_with(
        &gu2,
        "HDG-0701",
        "Written on an unprovisioned machine?",
        json!({}),
    );
    std::fs::copy(
        u2.join(format!("spec/decisions/{ugate}.yaml")),
        b.join(format!("spec/decisions/{ugate}.yaml")),
    )
    .unwrap();
    assert_eq!(t2_of(&gb, &ugate)["binding"], "FOREIGN");

    // ---------------------------------------------------------------- machine F: another owner's machine
    let fdir = admin_dir("foreign");
    let froot = write_admin(&fdir, "foreign-root-1.json", &foreign_root());
    let fbundle = write_admin(
        &fdir,
        "foreign-t2.json",
        &bundle(&[0x5eu8; 32], &[&key(0x8b)], &far_future()),
    );
    let (f, gf) = setup_fixture_unprovisioned("greenfield", "t2x-f", "S-F");
    provision_root(&gf, &froot);
    // the owner's bundle is not authorised by another owner's root
    let e = gf.err(&[
        "trust",
        "t2-binding",
        "--provision",
        m.bundle.to_str().unwrap(),
    ]);
    assert_eq!(
        e.error_code(),
        "T2_AUTHORITY_UNAUTHORISED",
        "{}",
        e.envelope
    );
    install_binding(&gf, &fbundle);
    gf.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "f",
        "--alias",
        "f",
    ]);
    let fgate = gate_with(
        &gf,
        "HDG-0702",
        "Written on another owner's machine?",
        json!({}),
    );
    assert_eq!(t2_of(&gf, &fgate)["scope"], "provisioned");
    std::fs::copy(
        f.join(format!("spec/decisions/{fgate}.yaml")),
        b.join(format!("spec/decisions/{fgate}.yaml")),
    )
    .unwrap();
    let tf = t2_of(&gb, &fgate);
    assert_eq!(
        (tf["binding"].as_str(), tf["scope"].as_str()),
        (Some("FOREIGN"), Some("provisioned")),
        "{tf}"
    );
    let e = gb
        .with_role("orchestrator")
        .err(&["gate", "present", &fgate]);
    assert_eq!(e.error_code(), "T2_UNBOUND");
    // B still honours everything its owner's machines wrote
    assert_eq!(t2_of(&gb, &g1)["binding"], "VERIFIED");
}

/// P2-ADJ-0002 (provisioning side): the binding authority is admitted only from the administrator domain, only on a
/// provisioned machine, only when this machine's trusted root delegates `t2-binding` and the owner's authorisation
/// verifies at threshold, is unexpired, binds this product and commits to exactly the supplied key; and only while
/// the machine is not below floor. Each refusal is typed and writes nothing.
#[test]
fn a_t2_binding_authority_is_admitted_only_from_the_administrator_domain_under_this_machines_root()
{
    let m = owner_material("adm");
    let (root, g) = setup_fixture_unprovisioned("greenfield", "t2-adm", "S-adm");
    let dir = m.dir.clone();
    let authorities = machine_state_dir(&root)
        .join("t2-binding")
        .join("authorities");
    // unprovisioned
    assert_eq!(
        g.err(&[
            "trust",
            "t2-binding",
            "--provision",
            m.bundle.to_str().unwrap()
        ])
        .error_code(),
        "T2_AUTHORITY_UNPROVISIONED"
    );
    // a root that delegates no `t2-binding` role
    let bare = write_admin(&dir, "bare-root.json", &owner_root(1, &[]));
    provision_root(&g, &bare);
    let e = g.err(&[
        "trust",
        "t2-binding",
        "--provision",
        m.bundle.to_str().unwrap(),
    ]);
    assert_eq!(
        e.error_code(),
        "T2_AUTHORITY_ROLE_NOT_DELEGATED",
        "{}",
        e.envelope
    );
    let st = g.ok(&["trust", "t2-binding"]);
    assert_eq!(st["root_delegates_role"], false);
    assert!(!authorities.exists() || std::fs::read_dir(&authorities).unwrap().count() == 0);

    // a machine whose root delegates the role
    let (root2, g2) = setup_fixture_unprovisioned("greenfield", "t2-adm2", "S-adm2");
    provision_root(&g2, &m.root);
    let authorities2 = machine_state_dir(&root2)
        .join("t2-binding")
        .join("authorities");
    let refuse = |name: &str, text: String, code: &str| {
        let f = write_admin(&dir, name, &text);
        let e = g2.err(&["trust", "t2-binding", "--provision", f.to_str().unwrap()]);
        assert_eq!(e.error_code(), code, "{name}: {}", e.envelope);
        assert!(
            !authorities2.exists() || std::fs::read_dir(&authorities2).unwrap().count() == 0,
            "{name}: nothing installed"
        );
    };
    // signed by a key the root does not delegate for `t2-binding` (e.g. the human-gate key, or an agent's own key)
    refuse(
        "wrong-signer.json",
        bundle(&binding_key(), &[&crate::ws03::owner()], &far_future()),
        "T2_AUTHORITY_UNAUTHORISED",
    );
    refuse(
        "self-signed.json",
        bundle(&binding_key(), &[&key(0x99)], &far_future()),
        "T2_AUTHORITY_UNAUTHORISED",
    );
    // expired
    refuse(
        "expired.json",
        bundle(&binding_key(), &[&t2_role_key()], &past()),
        "T2_AUTHORITY_EXPIRED",
    );
    // the key is not the key the owner authorised
    let mut swapped: Value =
        serde_json::from_str(&bundle(&binding_key(), &[&t2_role_key()], &far_future())).unwrap();
    swapped["key_hex"] = json!(hex::encode([0x11u8; 32]));
    refuse(
        "swapped-key.json",
        swapped.to_string(),
        "T2_AUTHORITY_KEY_MISMATCH",
    );
    // a signature over other bytes than the document parsed
    let signed = json!({"_type": "t2-binding-authority", "spec_version": "srr/1", "product": gov_runtime::FRAMEWORK_NAME,
        "authority_id": gov_runtime::t2::authority_id_of(&binding_key()), "key_commitment": gov_runtime::t2::key_commitment_of(&binding_key()),
        "issued": "2026-09-19T00:00:00Z", "expires": far_future()});
    let other = json!({"_type": "t2-binding-authority", "note": "something else"});
    let env =
        crate::srr_material::envelope_with_foreign_signature(&signed, &other, &[&t2_role_key()]);
    refuse(
        "foreign-signature.json",
        format!(
            "{{\"_type\":\"t2-binding-provisioning\",\"key_hex\":\"{}\",\"authority\":{env}}}",
            hex::encode(binding_key())
        ),
        "T2_AUTHORITY_UNAUTHORISED",
    );
    // not a bundle
    refuse(
        "not-a-bundle.json",
        json!({"_type": "something", "key_hex": "00"}).to_string(),
        "T2_AUTHORITY_INVALID",
    );
    // a bundle inside the governed project (repository content) is refused before it is read
    let inrepo = root2.join("t2-bundle.json");
    std::fs::copy(&m.bundle, &inrepo).unwrap();
    let e = g2.err(&[
        "trust",
        "t2-binding",
        "--provision",
        inrepo.to_str().unwrap(),
    ]);
    assert_eq!(e.error_code(), "T2_AUTHORITY_FROM_REPOSITORY_REFUSED");
    // the administrator's genuine bundle
    let ok = install_binding(&g2, &m.bundle);
    assert_eq!(ok["action"], "installed");
    let aid = gov_runtime::t2::authority_id_of(&binding_key());
    let kf = authorities2.join(&aid).join("key.json");
    assert!(kf.exists());
    {
        use std::os::unix::fs::PermissionsExt;
        assert_eq!(
            std::fs::metadata(&kf).unwrap().permissions().mode() & 0o777,
            0o600
        );
    }
    let st = g2.ok(&["trust", "t2-binding"]);
    assert_eq!(st["portable"], true, "{st}");
    assert_eq!(st["authorities"][0]["authorised_by_trusted_root"], true);
    assert_eq!(st["authorities"][0]["seals_new_records"], true);
    // the owner re-signs the same key (e.g. the role's key rotated): the stored authorisation is replaced
    let resigned = write_admin(
        &dir,
        "resigned.json",
        &bundle(&binding_key(), &[&t2_role_key()], "2098-01-01T00:00:00Z"),
    );
    assert_eq!(
        install_binding(&g2, &resigned)["action"],
        "authorisation replaced (the same key, newly authorised)"
    );
    // G0: the report and the administrator write are machine-trust commands; the reseal is a project write (L4)
    for label in [
        "trust t2-binding",
        "trust t2-binding --provision",
        "trust t2-binding --reseal",
        "trust t2-binding --reseal --dry-run",
    ] {
        assert!(
            gov_runtime::orchestration::control::command_guard(label).is_some(),
            "{label}"
        );
    }
}

/// P2-ADJ-0002 (revocation): a root successor that no longer delegates the `t2-binding` key revokes the authority
/// on the machine that accepts it — records sealed under it become UNAUTHORISED there (typed) and new seals fall back
/// to the machine scope, stated in the status.
#[test]
fn root_succession_that_drops_the_binding_role_revokes_its_records_and_sealing_falls_back() {
    let m = owner_material("rev");
    let (root, g) = setup_fixture_unprovisioned("greenfield", "t2-rev", "S-rev");
    provision_root(&g, &m.root);
    install_binding(&g, &m.bundle);
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "rev",
        "--alias",
        "rev",
    ]);
    let g1 = gate_with(&g, "HDG-0301", "Before revocation?", json!({}));
    assert_eq!(t2_of(&g, &g1)["binding"], "VERIFIED");
    // the owner's root quorum signs version 2 without the `t2-binding` delegation
    let v2 = write_admin(&m.dir, "owner-root-2.json", &owner_root(2, &[]));
    g.ok(&["trust", "root-update", "--anchor", v2.to_str().unwrap()]);
    let t = t2_of(&g, &g1);
    assert_eq!(t["binding"], "UNAUTHORISED", "{t}");
    assert!(t["reason"].as_str().unwrap().contains("t2-binding"), "{t}");
    let st = g.ok(&["trust", "t2-binding"]);
    assert_eq!(st["portable"], false);
    assert_eq!(st["authorities"][0]["authorised_by_trusted_root"], false);
    assert_eq!(st["sealing"]["scope"], "machine");
    // new work keeps going on this machine, sealed in the machine scope
    let g2 = gate_with(&g, "HDG-0302", "After revocation?", json!({}));
    let t2 = t2_of(&g, &g2);
    assert_eq!(
        (t2["binding"].as_str(), t2["scope"].as_str()),
        (Some("VERIFIED"), Some("machine"))
    );
    let _ = root;
}

/// P2-ADJ-0002 continuity: `gov trust t2-binding --reseal` re-seals under the owner's authority exactly the records
/// this machine sealed while it was provisioned (keeping the recorded operation and time), so they are honoured on the
/// owner's other machines; a record sealed while the machine was unprovisioned, and a record whose seal does not
/// verify, are left as they are.
#[test]
fn reseal_makes_what_this_machine_sealed_while_provisioned_portable_and_nothing_else() {
    let m = owner_material("rs");
    // unprovisioned first: bootstrap installation of the embedded payload, a gate sealed while unprovisioned
    let (a, ga) = setup_fixture_unprovisioned("greenfield", "t2-rs", "S-rs");
    ga.ok(&["init", "--name", "rs", "--alias", "rs"]);
    let early = gate_with(&ga, "HDG-0401", "Sealed while unprovisioned?", json!({}));
    std::thread::sleep(std::time::Duration::from_millis(1100));
    // then provisioned (with the root only): the kernel is verified against a signed release, a gate sealed then
    provision_root(&ga, &m.root);
    crate::ws03::reanchor_installed_kernel(&ga);
    let mid = gate_with(
        &ga,
        "HDG-0402",
        "Sealed while provisioned, before the authority?",
        json!({}),
    );
    assert_eq!(t2_of(&ga, &mid)["scope"], "machine");
    // a hand-edited record never becomes portable
    let forged_rel = "spec/decisions/HDG-0403.yaml";
    let forged_id = gate_with(&ga, "HDG-0403", "To be edited", json!({}));
    let mut fv = yaml(&a, forged_rel);
    fv["question"] = json!("edited by hand");
    write_yaml(&a, forged_rel, &fv);
    // the authority arrives; nothing changed yet
    install_binding(&ga, &m.bundle);
    assert_eq!(t2_of(&ga, &mid)["scope"], "machine");
    let dry = ga
        .with_role("orchestrator")
        .ok(&["trust", "t2-binding", "--reseal", "--dry-run"]);
    let files: Vec<String> = dry["resealed_files"]
        .as_array()
        .unwrap()
        .iter()
        .map(|f| f["path"].as_str().unwrap().to_string())
        .collect();
    assert!(files.iter().any(|f| f.ends_with("HDG-0402.yaml")), "{dry}");
    assert!(!files.iter().any(|f| f.ends_with("HDG-0401.yaml")), "{dry}");
    assert!(!files.iter().any(|f| f.ends_with("HDG-0403.yaml")), "{dry}");
    assert_eq!(
        t2_of(&ga, &mid)["scope"],
        "machine",
        "a dry run writes nothing"
    );
    // an L2 role may not reseal; FREEZE_WRITES refuses it
    assert_eq!(
        ga.with_role("product-spec-agent")
            .err(&["trust", "t2-binding", "--reseal"])
            .error_code(),
        "AUTHORITY_DENIED"
    );
    let before_op = yaml(&a, "spec/decisions/HDG-0402.yaml")["os_binding"].clone();
    let r = ga
        .with_role("orchestrator")
        .ok(&["trust", "t2-binding", "--reseal"]);
    assert!(r["resealed_seals"].as_u64().unwrap() >= 1, "{r}");
    let after = yaml(&a, "spec/decisions/HDG-0402.yaml");
    assert_eq!(after["os_binding"]["scope"], "provisioned");
    assert_eq!(after["os_binding"]["operation"], before_op["operation"]);
    assert_eq!(after["os_binding"]["at"], before_op["at"]);
    assert!(owner_verifies(&after).is_some());
    assert_eq!(t2_of(&ga, &mid)["binding"], "VERIFIED");
    assert_eq!(t2_of(&ga, &early)["scope"], "machine");
    assert_eq!(t2_of(&ga, &forged_id)["binding"], "BROKEN");
    git_commit_all(&a, "resealed");
    // on the owner's second machine: the resealed gate is honoured; the unprovisioned-era one is not
    let (_b, gb) = clone_of(&a, "t2-rs-b");
    provision_root(&gb, &m.root);
    install_binding(&gb, &m.bundle);
    assert_eq!(t2_of(&gb, &mid)["binding"], "VERIFIED");
    assert_eq!(t2_of(&gb, &early)["binding"], "FOREIGN");
}

// ============================================================================================ T2 completeness

/// WS-5 r2 IP-R3-1 (gates side): when a gate operation rewrites a task record the OS sealed (block on create, release
/// on an authorising answer, block again on revoke), the record stays verifiable — re-sealed under the operation that
/// wrote it — while an unsealed task record stays unsealed and a record whose seal does not verify is never blessed.
#[test]
fn gate_operations_keep_os_sealed_task_records_verifiable_and_never_bless_others() {
    let m = owner_material("tk");
    let (root, g) = setup_fixture_unprovisioned("greenfield", "t2-tk", "S-tk");
    provision_root(&g, &m.root);
    install_binding(&g, &m.bundle);
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "tk",
        "--alias",
        "tk",
    ]);
    for id in ["TASK-0901", "TASK-0902", "TASK-0903"] {
        g.ok(&[
            "task",
            "create",
            "--class",
            "documentation",
            "--objective",
            &format!("write the notes for {id}"),
            "--id",
            id,
        ]);
    }
    // TASK-0901 carries a seal an OS writer holding the owner's authority made; TASK-0903 a seal that does not verify
    let sealed = "spec/tasks/TASK-0901.yaml";
    let mut v = yaml(&root, sealed);
    owner_seal(&mut v, "task create");
    write_yaml(&root, sealed, &v);
    assert!(owner_verifies(&yaml(&root, sealed)).is_some());
    let broken = "spec/tasks/TASK-0903.yaml";
    let mut w = yaml(&root, broken);
    owner_seal(&mut w, "task create");
    w["objective"] = json!("edited after sealing");
    write_yaml(&root, broken, &w);
    let gid = gate_with(
        &g,
        "HDG-0501",
        "May the notes be written?",
        json!({"blocks_tasks": ["TASK-0901", "TASK-0902", "TASK-0903"]}),
    );
    let t1 = yaml(&root, sealed);
    assert_eq!(t1["human_gate"], json!(gid));
    assert_eq!(
        owner_verifies(&t1).as_deref(),
        Some("gate create (blocks task)"),
        "{}",
        t1["os_binding"]
    );
    assert!(yaml(&root, "spec/tasks/TASK-0902.yaml")
        .get("os_binding")
        .is_none());
    assert_eq!(owner_verifies(&yaml(&root, broken)), None, "never blessed");
    crate::ws03::human_decide(&g.with_role("orchestrator"), &gid, "A");
    let t1 = yaml(&root, sealed);
    assert_eq!(t1["task_status"], "READY", "{t1}");
    assert_eq!(
        owner_verifies(&t1).as_deref(),
        Some("gate answer (releases task)")
    );
    g.with_role("orchestrator")
        .ok(&["gate", "revoke", &gid, "--reason", "withdrawn (test)"]);
    let t1 = yaml(&root, sealed);
    assert_eq!(t1["task_status"], "BLOCKED");
    assert_eq!(
        owner_verifies(&t1).as_deref(),
        Some("gate revoke (blocks task)")
    );
    assert_eq!(owner_verifies(&yaml(&root, broken)), None);
}

/// WS-2 r2 R3-11: the plugin registry is T2 state, so `t2::audit` — and through it the suite's
/// `os_binding_integrity` family and doctor D033 — covers its entries and the document: a hand-edited entry is BROKEN.
#[test]
fn the_t2_audit_covers_the_plugin_registry() {
    let (root, g) = setup_fixture("greenfield", "t2-reg", "S-reg");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "reg",
        "--alias",
        "reg",
        "--skip-index",
    ]);
    write(
        &root,
        "tools/rp.sh",
        &format!("#!/bin/sh\ncat >/dev/null\nprintf '%s\\n' '{EMBED_OK}'\n"),
    );
    write_yaml(
        &root,
        "governance/project/plugins/rp.yaml",
        &json!({"plugin_id": "rp", "capability": "embed", "version": "1", "command": ["sh", "tools/rp.sh"]}),
    );
    crate::ws07::register_approved(
        &g.with_role("tooling-engineer"),
        &root.join("governance/project/plugins/rp.yaml"),
    );
    assert!(binding_counts(&g)
        .as_object()
        .map(|o| o.is_empty())
        .unwrap_or(true));
    let reg_path = "governance/generated/plugin-registry.json";
    let mut reg = json(&root, reg_path);
    reg["plugins"]["rp"]["approved_roles"] = json!(["all", "backend-engineer"]);
    gov_runtime::util::write_json(&root.join(reg_path), &reg).unwrap();
    let counts = binding_counts(&g);
    assert!(counts["BROKEN"].as_u64().unwrap_or(0) >= 2, "{counts}");
    let au = g.run(&["audit", "--no-persist", "--family", "os_binding_integrity"]);
    let text = au.envelope.to_string();
    assert!(text.contains("plugin-registration:rp"), "{text}");
}

// ============================================================================================ BC-P2-31

/// BC-P2-31 (WS-6 r2 IP-R2-8): the emergency-control state lives in the OS's operational store, so deleting the
/// derived runtime directory never lifts a freeze; a legacy control file an older binary left behind is still honoured
/// (the stricter state wins), and the next control command moves the state and removes the legacy copy.
#[test]
fn emergency_control_state_lives_in_the_operational_store() {
    let (root, g) = setup_fixture("greenfield", "t2-ctl", "S-ctl");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "ctl",
        "--alias",
        "ctl",
        "--skip-index",
    ]);
    git_commit_all(&root, "installed");
    g.ok(&["freeze-writes", "--reason", "incident (test)"]);
    assert!(exists(&root, ".governance-state/control.json"));
    assert!(!exists(&root, ".governance-runtime/control.json"));
    assert!(gov_runtime::paths::misplaced_os_state(&root)
        .iter()
        .all(|m| m["store"] != "emergency-control"));
    // the state directory never shows as a change
    let (_, porcelain) = git(&root, &["status", "--porcelain"]);
    assert!(!porcelain.contains(".governance-state"), "{porcelain}");
    // deleting the whole derived runtime directory does not lift the freeze
    std::fs::remove_dir_all(root.join(".governance-runtime")).unwrap();
    assert_eq!(g.ok(&["status"])["control"]["writes_frozen"], true);
    assert_eq!(
        g.err(&["task", "create", "--objective", "x"]).error_code(),
        "FROZEN"
    );
    g.ok(&["resume"]);
    assert_eq!(g.ok(&["status"])["control"]["writes_frozen"], false);
    // a legacy freeze left by an older binary is honoured (the stricter state wins) ...
    write(
        &root,
        ".governance-runtime/control.json",
        &json!({"mode": "RUNNING", "writes_frozen": true, "agents_cancelled": false, "reason": "legacy freeze"}).to_string(),
    );
    assert_eq!(
        g.err(&["task", "create", "--objective", "x"]).error_code(),
        "FROZEN"
    );
    // ... and the next control command resolves it: one state, where it belongs
    g.ok(&["resume"]);
    assert!(!exists(&root, ".governance-runtime/control.json"));
    assert_eq!(g.ok(&["status"])["control"]["writes_frozen"], false);
    // an explicit move of a legacy file on its own (no store yet) is picked up by the next command as well
    std::fs::remove_file(root.join(".governance-state/control.json")).unwrap();
    write(
        &root,
        ".governance-runtime/control.json",
        &json!({"mode": "PAUSED", "writes_frozen": false, "agents_cancelled": false, "reason": "legacy pause"}).to_string(),
    );
    assert_eq!(
        g.err(&["task", "create", "--objective", "x"]).error_code(),
        "PAUSED"
    );
    g.ok(&["freeze-writes", "--reason", "tighten"]);
    assert!(!exists(&root, ".governance-runtime/control.json"));
    let s = json(&root, ".governance-state/control.json");
    assert_eq!(
        (s["mode"].as_str(), s["writes_frozen"].as_bool()),
        (Some("PAUSED"), Some(true)),
        "{s}"
    );
}

// ============================================================================================ gates: evidence, triggers

/// WS-10 r2 IP-WS10-02: a gate, and the decision an answer mints, may rest only on governed research — research that
/// is not complete governed evidence is refused (`EVIDENCE_NOT_CITABLE`) — and the research records the gate and the
/// decision it influenced.
#[test]
fn gates_cite_only_governed_research_and_record_its_influence() {
    let (_root, g) = setup_fixture("greenfield", "t2-res", "S-res");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "res",
        "--alias",
        "res",
        "--skip-index",
    ]);
    let draft = g.ok(&[
        "research",
        "record",
        "--draft",
        "--fields",
        &json!({"title": "Cache options", "question": "Which cache?", "reason": "latency"})
            .to_string(),
    ]);
    let draft_id = draft["research"]["id"].as_str().unwrap().to_string();
    let e = g.err(&[
        "gate",
        "create",
        "--question",
        "Adopt caching?",
        "--fields",
        &crate::ws03::package(json!({"derived_from": [draft_id]})),
    ]);
    assert_eq!(e.error_code(), "EVIDENCE_NOT_CITABLE", "{}", e.envelope);
    let done = g.ok(&[
        "research",
        "record",
        "--fields",
        &json!({"title": "Cache benchmark", "question": "Which cache?", "reason": "latency budget", "method": "benchmark A vs B",
                "sources": ["bench run 1"], "measurements": [{"name": "p95", "value": 12}], "uncertainty": "one machine",
                "conclusion": "A is faster", "confidence": 0.8}).to_string(),
    ]);
    let rid = done["research"]["id"].as_str().unwrap().to_string();
    let gate = g.ok(&[
        "gate",
        "create",
        "--question",
        "Adopt caching?",
        "--fields",
        &crate::ws03::package(json!({"derived_from": [rid.clone()]})),
    ]);
    let gid = gate["id"].as_str().unwrap().to_string();
    assert!(
        gate["evidence_influence"]["recorded"]
            .as_array()
            .unwrap()
            .iter()
            .any(|x| x == &json!(rid)),
        "{gate}"
    );
    let ans = crate::ws03::human_decide(&g.with_role("orchestrator"), &gid, "A");
    let did = ans["decision"].as_str().unwrap().to_string();
    let show = g.ok(&["research", "show", &rid]);
    let text = show.to_string();
    assert!(text.contains(&gid) && text.contains(&did), "{show}");
    // an answer citing non-governed evidence is refused before anything is written
    let g2 = g.ok(&[
        "gate",
        "create",
        "--question",
        "Adopt caching everywhere?",
        "--fields",
        &crate::ws03::package(json!({})),
    ])["id"]
        .as_str()
        .unwrap()
        .to_string();
    crate::ws03::render(&g, &g2);
    let e =
        g.with_role("orchestrator")
            .err(&["decide", &g2, "--option", "A", "--evidence", &draft_id]);
    assert_eq!(e.error_code(), "EVIDENCE_NOT_CITABLE", "{}", e.envelope);
}

/// WS-9/11 r2 IP-R2-5 and WS-10 r2 IP-WS10-15: an upstream export and an experiment promotion are human decisions —
/// an agent's resolution of a gate raised for either is refused even when every other agent-resolution condition
/// holds.
#[test]
fn upstream_export_and_experiment_promotion_gates_are_human_only() {
    let (_root, g) = setup_fixture("greenfield", "t2-ho", "S-raiser");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "ho",
        "--alias",
        "ho",
        "--skip-index",
    ]);
    for trigger in ["upstream_export", "experiment_promotion", "vendor_note"] {
        let id = g.ok(&[
            "gate",
            "create",
            "--question",
            &format!("resolve {trigger}?"),
            "--fields",
            &crate::ws03::package(
                json!({"trigger": trigger, "impact_radius": "R1", "confidence": 0.95,
                "reversibility": "reversible: revert the change"}),
            ),
        ])["id"]
            .as_str()
            .unwrap()
            .to_string();
        crate::ws03::render(&g, &id);
        let resolver = g.with_session("S-resolver").with_role("change-controller");
        let o = resolver.run(&[
            "decide",
            &id,
            "--option",
            "A",
            "--by",
            "change-controller",
            "--rationale",
            "low impact, reversible",
        ]);
        if trigger == "vendor_note" {
            assert!(
                o.ok(),
                "control: an agent-resolvable gate resolves: {}",
                o.envelope
            );
        } else {
            assert_eq!(
                o.error_code(),
                "AUTHORITY_DENIED",
                "{trigger}: {}",
                o.envelope
            );
            assert!(
                o.envelope.to_string().contains("human decisions"),
                "{}",
                o.envelope
            );
        }
    }
}

// ============================================================================================ adapters

/// WS-4 r2 R2-12: the generated adapters wire the checkpoint triggers a harness owns as provider hooks — a hook manifest
/// whose commands are gov's own checkpoint and session-close commands — and each hook command, run as written, records
/// the trigger.
#[test]
fn generated_provider_hooks_call_gov_checkpoint_and_session_close() {
    let (root, g) = setup_fixture("greenfield", "t2-hooks", "S-hooks");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "hooks",
        "--alias",
        "hooks",
        "--skip-index",
    ]);
    g.ok(&["adapters", "generate"]);
    assert_eq!(g.ok(&["adapters", "verify"])["ok"], true);
    let h = json(
        &root,
        "governance/generated/adapters/hooks/provider-hooks.json",
    );
    let hooks = h["hooks"].as_array().unwrap();
    let find = |ev: &str| {
        hooks
            .iter()
            .find(|x| x["event"] == ev)
            .unwrap_or_else(|| panic!("no {ev} hook: {h}"))
            .clone()
    };
    for (ev, trig) in [
        ("pre_compaction", "before_compaction"),
        ("session_end", "before_session_close"),
        ("model_switch", "before_model_switch"),
    ] {
        let hook = find(ev);
        assert_eq!(hook["checkpoint_trigger"], trig);
        let argv: Vec<String> = hook["command"]
            .as_array()
            .unwrap()
            .iter()
            .map(|x| x.as_str().unwrap().to_string())
            .collect();
        assert_eq!(argv[0], "gov");
        let args: Vec<&str> = argv[1..].iter().map(|s| s.as_str()).collect();
        g.with_role("backend-engineer").ok(&args);
        let recorded: Vec<String> = std::fs::read_dir(root.join("spec/reports/checkpoints"))
            .unwrap()
            .flatten()
            .filter(|e| e.file_name().to_string_lossy().starts_with("CKPT-"))
            .map(|e| {
                gov_runtime::util::read_yaml(&e.path()).unwrap()["trigger"]
                    .as_str()
                    .unwrap_or("")
                    .to_string()
            })
            .collect();
        assert!(recorded.iter().any(|t| t == trig), "{ev}: {recorded:?}");
    }
}
