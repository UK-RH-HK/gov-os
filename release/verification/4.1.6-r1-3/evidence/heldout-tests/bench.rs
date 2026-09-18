//! AR-0031 held-out harness. Independently authored for R1 verification iteration 3.
//!
//! Deliberately minimal: every scenario in this suite attacks the `OWNER-DECISION-0006` §6 enforcement points
//! directly through the library, so the harness only has to (a) make a fresh protected state root, (b) put a
//! genuine `DEGRADED — RECOVERY ONLY` marking on it in the exact shape every product reader accepts, and
//! (c) control the environment deterministically.
#![allow(dead_code)]

use gov_runtime::srr::breakglass as bg;
use gov_runtime::srr::state::MachineState;
use serde_json::json;
use std::path::{Path, PathBuf};

pub const PRODUCT: &str = gov_runtime::FRAMEWORK_NAME;

/// Every environment variable that could otherwise steer a result, cleared before each scenario.
pub const STRIP: &[&str] = &[
    "GOV_BREAK_GLASS",
    "GOV_BREAKGLASS",
    "GOV_TRUST_OVERRIDE",
    "GOV_SKIP_VERIFY",
    "GOV_ALLOW_UNSIGNED",
    "GOV_RELEASE_AUTHORITY",
    "GOV_HUMAN_GATE_APPROVED",
    "GOV_FLOOR_OVERRIDE",
    "GOV_MINIMUM_SECURE_RELEASE",
    "GOV_MACHINE_STATE_DIR",
];

pub fn strip_env() {
    for k in STRIP {
        std::env::remove_var(k);
    }
}

static COUNTER: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(0);

/// A fresh directory under the OS temp dir. Never inside the worktree.
pub fn scratch(tag: &str) -> PathBuf {
    let n = COUNTER.fetch_add(1, std::sync::atomic::Ordering::SeqCst);
    let d = std::env::temp_dir().join(format!(
        "ar0031-{tag}-{}-{}",
        std::process::id(),
        n
    ));
    let _ = std::fs::remove_dir_all(&d);
    std::fs::create_dir_all(&d).unwrap();
    d
}

/// Point the default state root (`XDG_STATE_HOME`) at a fresh directory and return the machine-state root that
/// `resolve_state_root()` will then produce.
pub fn isolated_default_root(tag: &str) -> (PathBuf, PathBuf) {
    strip_env();
    let xdg = scratch(tag);
    std::env::set_var("XDG_STATE_HOME", &xdg);
    let root = xdg.join("governance-os").join("machine");
    std::fs::create_dir_all(&root).unwrap();
    (xdg, root)
}

/// Write the provisioning latch, which is what `resolve_state_root` reads to decide a machine is provisioned.
pub fn set_provisioned(root: &Path) {
    let t = root.join("trust");
    std::fs::create_dir_all(&t).unwrap();
    std::fs::write(
        t.join("provisioned.json"),
        serde_json::to_string_pretty(
            &json!({"provisioned_at": "2026-01-01T00:00:00Z", "state_root": root.display().to_string(), "product": PRODUCT, "root_version": 1}),
        )
        .unwrap(),
    )
    .unwrap();
}

/// Put the machine into `DEGRADED — RECOVERY ONLY` for `product`, in the exact record shape `read_marking`
/// accepts, and assert every product reader agrees the machine is marked.
pub fn mark_degraded(root: &Path, product: &str) {
    let d = root.join("degraded");
    std::fs::create_dir_all(&d).unwrap();
    let rec = json!({
        "active": true,
        "marking": bg::DEGRADED_TOKEN,
        "product": product,
        "entered_at": "2026-01-01T00:00:00Z",
        "reason": "AR-0031 held-out scenario",
    });
    std::fs::write(
        d.join(format!("{product}.json")),
        serde_json::to_string_pretty(&rec).unwrap(),
    )
    .unwrap();
}

/// The marking as the product's own path builder spells it, so a scenario can never write to a path the guards
/// do not read.
pub fn mark_via_product_path(ms: &MachineState, product: &str) {
    let p = ms.degraded_path(product);
    std::fs::create_dir_all(p.parent().unwrap()).unwrap();
    let rec = json!({
        "active": true,
        "marking": bg::DEGRADED_TOKEN,
        "product": product,
        "entered_at": "2026-01-01T00:00:00Z",
        "reason": "AR-0031 held-out scenario",
    });
    std::fs::write(&p, serde_json::to_string_pretty(&rec).unwrap()).unwrap();
}

/// Absolute path to the worktree under verification.
pub fn wt() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../wt/srr1-r1-verify-3")
}

pub fn src(rel: &str) -> String {
    std::fs::read_to_string(wt().join(rel))
        .unwrap_or_else(|e| panic!("cannot read {rel}: {e}"))
}

/// Every product `.rs` file under `runtime/src` and `cli/src`.
pub fn product_sources() -> Vec<(String, String)> {
    let mut out = vec![];
    for base in ["runtime/src", "cli/src"] {
        walk(&wt().join(base), &mut out);
    }
    out.sort();
    out
}

fn walk(dir: &Path, out: &mut Vec<(String, String)>) {
    let Ok(rd) = std::fs::read_dir(dir) else {
        return;
    };
    for e in rd.filter_map(|e| e.ok()) {
        let p = e.path();
        if p.is_dir() {
            walk(&p, out);
        } else if p.extension().map(|x| x == "rs").unwrap_or(false) {
            let rel = p
                .strip_prefix(wt())
                .unwrap_or(&p)
                .to_string_lossy()
                .to_string();
            out.push((rel, std::fs::read_to_string(&p).unwrap_or_default()));
        }
    }
}

/// The body of `fn <name>` in `text`, from the signature to the matching close brace at the same indent.
pub fn fn_body(text: &str, name: &str) -> String {
    for pat in [
        format!("pub fn {name}("),
        format!("fn {name}("),
        format!("pub fn {name}<"),
    ] {
        if let Some(i) = text.find(&pat) {
            let rest = &text[i..];
            // find the opening brace of the body, then balance
            let mut depth = 0usize;
            let mut started = false;
            for (j, c) in rest.char_indices() {
                if c == '{' {
                    depth += 1;
                    started = true;
                } else if c == '}' {
                    depth -= 1;
                    if started && depth == 0 {
                        return rest[..=j].to_string();
                    }
                }
            }
        }
    }
    String::new()
}

/// All eight §6 effects, paired with the activity name the decision uses.
pub fn all_effects() -> Vec<(bg::Effect, &'static str)> {
    vec![
        (bg::Effect::NormalPrivilegedOperation, "normal_privileged_operation"),
        (bg::Effect::HumanGateCreate, "human_gate_create"),
        (bg::Effect::HumanGateApprove, "human_gate_approve"),
        (bg::Effect::ReleaseCertification, "release_certification"),
        (bg::Effect::TrustPolicyMutation, "trust_policy_mutation"),
        (bg::Effect::PrivilegedPluginAcquisition, "privileged_plugin_acquisition"),
        (bg::Effect::FloorLowerOrReset, "floor_lower_or_reset"),
        (
            bg::Effect::PresentBelowFloorReleaseAsCurrent,
            "present_below_floor_release_as_current",
        ),
    ]
}
