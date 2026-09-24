//! **P2-PROBE-OPTION-C — owner-ordered read/probe/design exercise, NOT product code, NOT a repair.**
//!
//! The owner provisionally aligned with Option C for 5A (replace `floor-reanchor`'s identity TRANSFER with a
//! delete-only stale-anchor operation) but required the proposed lifecycle be proved end-to-end first, because two
//! orchestrator statements must be shown compatible:
//!
//!   (i) `init`/`adopt` do not re-establish a floor after relocation (both gate on `!already_installed`);
//!  (ii) Option C claims "delete the stale entry, and the EXISTING onboarding/bootstrap path then succeeds".
//!
//! The delete-only operation is SIMULATED by removing the machine-store entry directory directly. Nothing named
//! `floor-forget` is built: per the owner, the operation must not be built merely to prove itself.
//!
//! The owner's target invariant:
//!   > relocation never transfers trusted identity between paths. A stale old binding may be invalidated/deleted.
//!   > A new location receives authority only through the normal authenticated adoption/onboarding transaction.
#![allow(dead_code)]
use crate::common::*;
use serde_json::Value;
use std::path::{Path, PathBuf};

const FLOOR_REL: &str = "governance/registry/project-adoption-floor.json";

fn store_entries(state_of: &Path) -> Vec<(String, u64, String)> {
    let dir = machine_state_dir(state_of).join("adoption-floors");
    let mut out = vec![];
    let Ok(rd) = std::fs::read_dir(&dir) else { return out };
    for e in rd.filter_map(|e| e.ok()) {
        if let Ok(v) = gov_runtime::util::read_json(&e.path().join("identity.json")) {
            out.push((
                v["project_identity"].as_str().unwrap_or("").to_string(),
                v["max_known_sequence"].as_u64().unwrap_or(0),
                v["minted_for_path"].as_str().unwrap_or("").to_string(),
            ));
        }
    }
    out.sort();
    out
}

fn anchor_key(p: &Path) -> String {
    let canon = std::fs::canonicalize(p).unwrap_or_else(|_| p.to_path_buf());
    gov_runtime::util::sha256_hex(canon.to_string_lossy().as_bytes())
}

fn refused_overrides(g: &Gov) -> Vec<Value> {
    g.ok(&["policy", "overrides"])["refused"].as_array().cloned().unwrap_or_default()
}
fn disclosures(g: &Gov) -> Vec<Value> {
    g.ok(&["policy", "overrides"])["disclosures"].as_array().cloned().unwrap_or_default()
}
fn floor_finding(g: &Gov) -> Option<Value> {
    refused_overrides(g).into_iter().find(|r| r["policy"] == "PROJECT_ADOPTION_FLOOR")
}
fn effective_class(g: &Gov, pattern: &str) -> Value {
    let eff = g.ok(&["policy", "effective", "REPOSITORY_CONTRACT.yaml"]);
    let arr = eff["effective"]["paths"].as_array().cloned().unwrap_or_default();
    arr.iter().rev().find(|r| r["pattern"] == pattern).map(|r| r["class"].clone()).unwrap_or(Value::Null)
}
fn doctor_d027(g: &Gov) -> (bool, String) {
    let r = g.run(&["doctor"]);
    let checks = r.envelope["result"]["checks"].as_array().cloned().unwrap_or_default();
    for c in checks {
        if c["id"].as_str() == Some("D027") {
            return (c["ok"].as_bool().unwrap_or(false), c["message"].as_str().unwrap_or("").to_string());
        }
    }
    (false, "<D027 absent>".into())
}

fn snap(tag: &str, g: &Gov, state_of: &Path) {
    let (ok, msg) = doctor_d027(g);
    eprintln!(
        "OC[{tag}] eff(src/**)={:?} finding={} d027_ok={} d027={:?} disclosures={:?}\nOC[{tag}] store={:?}",
        effective_class(g, "src/**"),
        floor_finding(g).is_some(),
        ok, msg, disclosures(g),
        store_entries(state_of),
    );
}

fn gov_on(root: &Path, state_of: &Path, session: &str) -> Gov {
    Gov::new(root, session).with_env("XDG_STATE_HOME", machine_state_home(state_of).to_str().unwrap())
}

fn fresh(tag: &str) -> (PathBuf, Gov) {
    let (root, g) = setup_fixture("greenfield", tag, "S-ocprobe");
    g.ok(&["init", "--source", signed_source(), "--name", tag, "--alias", &format!("a-{tag}"), "--skip-index"]);
    git_commit_all(&root, "after init");
    (root, g)
}

/// The full owner-specified Option-C lifecycle, observed at every step.
#[test]
fn p2probe_option_c_lifecycle_end_to_end() {
    let (root, g) = fresh("oclife");
    let machine = root.clone();
    eprintln!("OC ===== STEP 1: normally adopted repository =====");
    snap("1-adopted", &g, &machine);
    let identity_before = store_entries(&machine).first().map(|e| e.0.clone()).unwrap_or_default();
    let floor_doc_before = std::fs::read_to_string(root.join(FLOOR_REL)).unwrap_or_default();
    eprintln!("OC identity_before={identity_before:?}");

    eprintln!("OC ===== STEP 2: relocate the repository =====");
    let moved = root.parent().unwrap().join("oclife-relocated");
    let old_key = anchor_key(&root);
    std::fs::rename(&root, &moved).expect("relocate");
    let gm = gov_on(&moved, &machine, "S-ocprobe-moved");
    eprintln!("OC old_anchor_key={old_key}");
    snap("2-relocated", &gm, &machine);

    eprintln!("OC ===== STEP 3: SIMULATE the delete-only stale-anchor operation =====");
    let stale = machine_state_dir(&machine).join("adoption-floors").join(&old_key);
    eprintln!("OC stale_entry_exists_before_delete={}", stale.is_dir());
    let _ = std::fs::remove_dir_all(&stale);
    eprintln!("OC stale_entry_exists_after_delete={}", stale.is_dir());
    snap("3-after-forget", &gm, &machine);
    let after_forget = store_entries(&machine);
    eprintln!("OC IDENTITY_AFTER_FORGET={:?}", after_forget.first().map(|e| e.0.clone()));
    eprintln!(
        "OC INVARIANT_CHECK identity_unchanged_from_document={}",
        after_forget.first().map(|e| e.0.clone()).unwrap_or_default() == identity_before
    );
    eprintln!(
        "OC floor_document_unchanged={}",
        std::fs::read_to_string(moved.join(FLOOR_REL)).unwrap_or_default() == floor_doc_before
    );

    eprintln!("OC ===== STEP 4: can the EXISTING onboarding path run here at all? =====");
    for argv in [
        vec!["init", "--source", signed_source(), "--name", "oclife", "--alias", "a-oclife", "--skip-index"],
        vec!["adopt", "--help"],
    ] {
        let o = gm.run(&argv);
        eprintln!("OC existing-path {:?} -> code={} err={:?}", &argv[..1], o.code,
            o.envelope["error"]["code"].as_str().unwrap_or("-"));
    }
    eprintln!("OC framework_lock_present_at_new_path={}", moved.join("governance/framework.lock").is_file());
}

/// Does deleting a stale entry silently invalidate a SECOND, still-live checkout of the same project?
#[test]
fn p2probe_option_c_second_live_checkout_effect() {
    let (root, g) = fresh("oc2nd");
    let machine = root.clone();
    let second = root.parent().unwrap().join(format!("oc2nd-second-{}", gov_runtime::util::short_uuid()));
    // the realistic second working copy: an ordinary git clone, which is exactly the AR92-C3 / AR94-C4 scenario
    let o = std::process::Command::new("git")
        .args(["clone", "--quiet", &root.display().to_string(), &second.display().to_string()])
        .output().unwrap();
    assert!(o.status.success(), "git clone the second checkout: {}", String::from_utf8_lossy(&o.stderr));
    let g2 = gov_on(&second, &machine, "S-ocprobe-2nd");
    eprintln!("OC2 ===== both checkouts live =====");
    snap("first", &g, &machine);
    snap("second", &g2, &machine);
    eprintln!("OC2 ===== delete the FIRST checkout's entry (simulated forget) =====");
    let _ = std::fs::remove_dir_all(machine_state_dir(&machine).join("adoption-floors").join(anchor_key(&root)));
    snap("first-after", &g, &machine);
    snap("second-after", &g2, &machine);
}
