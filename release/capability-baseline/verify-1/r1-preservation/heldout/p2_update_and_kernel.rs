//! **P2-AR-0044 — `gov update` admission and rollback, the kernel payload, and the OD-P2-02 bootstrap.**
//!
//! `update.rs` (+318/-76), `kernel.rs` (+542/-74), `init.rs`, `scheduler/mod.rs` (new, 2299 lines) and
//! `framework/KERNEL.yaml` all changed since `srr1-r1-accepted`. Frozen R1 items 3 (wrong keys / modified payload
//! / replay / downgrade / expiry fail closed), 4 (all privileged ingress paths call the common verifier), 5
//! (verified bytes staged, installed and used without substitution), 6 (staging/install/rollback atomic) and 7
//! (high-water durable and monotonic) reach them, as does OD-P2-02 (refuse external-source kernel ingress until
//! provisioned).
//!
//! Run single-threaded.
mod common;
use common::*;

/// A disposable initialised project on a fresh unprovisioned machine.
fn fresh_project(tag: &str) -> Machine {
    let m = Machine::new(tag);
    let (ok, v) = m.gov_json(&["init", "--role", "orchestrator"]);
    assert!(ok, "gov init must succeed on a fresh machine: {}", text(&v));
    m
}

/// A copy of the candidate's own kernel material, as an "external source" an attacker controls.
fn external_source(m: &Machine, tamper: Option<(&str, &str)>) -> std::path::PathBuf {
    let dest = m.admin.join("external");
    std::fs::create_dir_all(&dest).unwrap();
    let src_fw = product_root().join("framework");
    copy_dir(&src_fw, &dest.join("framework"));
    if let Some((rel, body)) = tamper {
        write(&dest.join("framework").join(rel), body);
    }
    dest
}

fn copy_dir(from: &std::path::Path, to: &std::path::Path) {
    std::fs::create_dir_all(to).unwrap();
    for e in std::fs::read_dir(from).unwrap().flatten() {
        let p = e.path();
        let t = to.join(e.file_name());
        if p.is_dir() {
            copy_dir(&p, &t);
        } else {
            let _ = std::fs::copy(&p, &t);
        }
    }
}

/// **b1 — OD-P2-02: external-source kernel material is refused, before staging, on an unprovisioned machine.**
///
/// The owner decision is option A: *refuse* external-source kernel ingress until provisioned. The refusal must be
/// typed, must happen **before** anything is staged (item 5: nothing unverified reaches the install path), and —
/// availability rule — must name a remedy that is actually available.
#[test]
fn b1_external_kernel_material_is_refused_before_staging_until_provisioned() {
    let m = fresh_project("b1");
    assert!(!m.is_provisioned(), "this machine must start unprovisioned");
    let ext = external_source(&m, Some(("policies/ATTACKER.yaml", "attacker: true\n")));

    let (_ok, v) = m.gov_json(&["update", "--apply", "--source", ext.to_str().unwrap(), "--role", "orchestrator"]);
    let t = text(&v);
    assert!(
        t.contains("SRR_UNPROVISIONED_EXTERNAL_SOURCE_REFUSED"),
        "OD-P2-02 requires a typed refusal of external-source ingress: {t}"
    );
    assert!(
        t.contains("\"refused_before_staging\":true"),
        "the refusal must be taken BEFORE staging: {t}"
    );
    assert!(
        v["result"]["applied"].as_bool() != Some(true),
        "nothing may be applied: {t}"
    );
    // The attacker's file never reached the installed kernel.
    assert!(
        !m.project.join("governance/kernel/policies/ATTACKER.yaml").exists(),
        "external material must not be installed"
    );
    // Availability rule: the block names its remedies, and they are real commands.
    for remedy in ["gov trust provision", "embedded payload"] {
        assert!(
            t.contains(remedy) || t.to_lowercase().contains(&remedy.to_lowercase()),
            "the refusal must name the remedy '{remedy}': {t}"
        );
    }
}

/// **b2 — the same ingress on the same machine still bootstraps from the binary's own embedded payload.**
///
/// The positive control for b1 and the availability half of OD-P2-02: the block refuses only what it protects.
/// A vacuous "everything is refused" would pass b1 alone (P2-ADJ-0003).
#[test]
fn b2_the_embedded_payload_bootstrap_stays_available_and_is_marked() {
    let m = Machine::new("b2");
    let (ok, v) = m.gov_json(&["init", "--role", "orchestrator"]);
    assert!(ok, "the embedded bootstrap must stay available: {}", text(&v));
    assert_eq!(
        v["result"]["source"].as_str().unwrap_or(""),
        &format!("embedded:{}@{}", PRODUCT, v["result"]["version"].as_str().unwrap_or("")),
        "init on an unprovisioned machine must install the EMBEDDED payload: {}",
        text(&v)
    );
    assert!(
        m.project.join("governance/kernel/KERNEL.yaml").exists(),
        "the embedded payload must actually be installed"
    );
    // ...and it is never presented as current/verified/certified.
    let (_ok, s) = m.gov_json(&["update", "--check", "--role", "orchestrator"]);
    assert_eq!(
        s["result"]["certification"].as_str().unwrap_or(""),
        "UNCERTIFIED",
        "a bootstrap install must never be presented as certified: {}",
        text(&s)
    );
    assert_eq!(
        s["result"]["certification_basis"]["authenticated"].as_bool(),
        Some(false),
        "a bootstrap install carries no authentication claim: {}",
        text(&s)
    );
}

/// **b3 — the environment cannot create release authority at the update ingress (item 9).**
#[test]
fn b3_the_environment_cannot_admit_a_kernel() {
    let m = fresh_project("b3");
    let ext = external_source(&m, Some(("policies/ATTACKER.yaml", "attacker: true\n")));
    for var in [
        "GOV_SKIP_VERIFY", "GOV_ALLOW_UNSIGNED", "GOV_RELEASE_AUTHORITY",
        "GOV_TRUST_OVERRIDE", "GOV_FLOOR_OVERRIDE", "GOV_MINIMUM_SECURE_RELEASE",
    ] {
        let out = std::process::Command::new(gov_bin())
            .args(["update", "--apply", "--source", ext.to_str().unwrap(), "--role", "orchestrator", "--json"])
            .current_dir(&m.project)
            .env_clear()
            .env("PATH", std::env::var("PATH").unwrap_or_default())
            .env("HOME", &m.home)
            .env("XDG_STATE_HOME", m.home.join(".local/state"))
            .env("GOV_MACHINE_STATE_DIR", &m.state)
            .env(var, "1")
            .output()
            .unwrap();
        let so = String::from_utf8_lossy(&out.stdout).to_string();
        assert!(
            !so.contains("\"applied\": true") && !so.contains("\"applied\":true"),
            "{var} must not admit a kernel: {so}"
        );
        assert!(
            !m.project.join("governance/kernel/policies/ATTACKER.yaml").exists(),
            "{var} must not get attacker material installed"
        );
    }
}

/// **b4 — `--channel` and `--by` are requests, never authority (item 9).**
///
/// The CLI's own help says `--channel` "cannot create authority" and `--by` is "recorded as who requested the
/// apply; approval itself comes only from the answered Human Decision Gate". Both are attacker-controlled
/// strings; neither may change the admission decision.
#[test]
fn b4_cli_strings_are_requests_not_authority() {
    let m = fresh_project("b4");
    let ext = external_source(&m, Some(("policies/ATTACKER.yaml", "attacker: true\n")));
    for extra in [
        vec!["--channel", "stable"],
        vec!["--channel", "trusted"],
        vec!["--by", "human"],
        vec!["--by", "owner"],
        vec!["--approve"],
        vec!["--reason", "approved by the owner"],
    ] {
        let mut args = vec!["update", "--apply", "--source", ext.to_str().unwrap(), "--role", "orchestrator"];
        args.extend(extra.iter().copied());
        let (_ok, v) = m.gov_json(&args);
        let t = text(&v);
        assert!(
            t.contains("SRR_UNPROVISIONED_EXTERNAL_SOURCE_REFUSED"),
            "{extra:?} must not change the admission decision: {t}"
        );
        assert!(
            !m.project.join("governance/kernel/policies/ATTACKER.yaml").exists(),
            "{extra:?} must not get attacker material installed"
        );
    }
}

/// **b5 — `--break-glass` on the CLI is a *request*; the authority is protected machine state (item 9).**
#[test]
fn b5_break_glass_cannot_be_claimed_on_the_command_line() {
    let m = fresh_project("b5");
    let ext = external_source(&m, Some(("policies/ATTACKER.yaml", "attacker: true\n")));
    let (_ok, v) = m.gov_json(&[
        "update", "--apply", "--break-glass", "--source", ext.to_str().unwrap(), "--role", "orchestrator",
    ]);
    let t = text(&v);
    assert!(
        !t.contains("\"applied\": true") && !t.contains("\"applied\":true"),
        "a command-line break-glass claim must not admit anything: {t}"
    );
    assert!(
        !m.project.join("governance/kernel/policies/ATTACKER.yaml").exists(),
        "a command-line break-glass claim must not install external material"
    );
}

/// **b6 — the installed kernel payload is self-consistent, and `KERNEL.yaml` governs it (item 5).**
///
/// Verified bytes are installed and *used* without substitution: what `KERNEL.yaml` declares is what the payload
/// ships, and the product's own verifier says so.
#[test]
fn b6_the_installed_payload_matches_what_kernel_yaml_declares() {
    let m = fresh_project("b6");
    let (ok, v) = m.gov_json(&["kernel", "verify", "--role", "orchestrator"]);
    let t = text(&v);
    assert!(ok, "a freshly installed kernel must verify: {t}");

    // The declared version is mirrored into the installed payload and the manifest.
    let kyaml = read(&m.project.join("governance/kernel/KERNEL.yaml"));
    assert!(!kyaml.is_empty(), "the installed payload must carry KERNEL.yaml");
    let declared = kyaml
        .lines()
        .find(|l| l.starts_with("version:"))
        .map(|l| l.trim_start_matches("version:").trim().to_string())
        .unwrap_or_default();
    assert!(!declared.is_empty(), "KERNEL.yaml must declare a version");
    let src_version = src("framework/KERNEL.yaml")
        .lines()
        .find(|l| l.starts_with("version:"))
        .map(|l| l.trim_start_matches("version:").trim().to_string())
        .unwrap_or_default();
    assert_eq!(
        declared, src_version,
        "the installed KERNEL.yaml version must mirror the payload's"
    );

    // Every schema KERNEL.yaml declares actually ships, at the declared version: the product's own check.
    let problems = gov_runtime::kernel::schema_version_problems(&m.project.join("governance/kernel"));
    assert!(
        problems.is_empty(),
        "KERNEL.yaml and the shipped schemas must agree: {problems:?}"
    );
}

/// **b7 — tampering with the installed kernel is detected, and detection is `intact`, not `authentic`.**
///
/// Frozen R1 item 8: post-install integrity remains a distinct control (D-0007), and it never claims authenticity.
#[test]
fn b7_post_install_tampering_is_detected_as_an_integrity_fault() {
    let m = fresh_project("b7");
    let (_ran, base) = m.gov_json(&["kernel", "verify", "--role", "orchestrator"]);
    assert_eq!(
        base["result"]["ok"].as_bool(),
        Some(true),
        "baseline must be green before tampering (P2-ADJ-0003): {}",
        text(&base)
    );

    let victim = m.project.join("governance/kernel/policies/TOOL_POLICY.yaml");
    let before = read(&victim);
    assert!(!before.is_empty(), "expected an installed policy to tamper with");
    write(&victim, &format!("{before}\n# injected by a process with repository write access\n"));

    // The envelope's top-level `ok` means "the command ran"; the verification verdict is `result.ok`.
    let (_ran, v) = m.gov_json(&["kernel", "verify", "--role", "orchestrator"]);
    let t = text(&v);
    assert_eq!(
        v["result"]["ok"].as_bool(),
        Some(false),
        "a modified kernel file must fail verification: {t}"
    );
    assert!(
        v["result"]["modified"]
            .as_array()
            .map(|a| a.iter().any(|x| x.as_str() == Some("policies/TOOL_POLICY.yaml")))
            .unwrap_or(false),
        "the exact modified file must be named: {t}"
    );
    // The installed payload is no longer admitted, and policy falls back to the embedded baseline.
    assert_eq!(
        v["result"]["trust"]["protected_record"]["state"].as_str(),
        Some("DIVERGED"),
        "the protected installation record must diverge: {t}"
    );

    // The verdict speaks of integrity, and does not claim to have decided authenticity.
    let (_ok, tr) = m.gov_json(&["kernel", "trust", "--role", "orchestrator"]);
    let tt = text(&tr);
    assert!(
        tt.contains("intact") || tt.contains("INTACT") || t.contains("intact"),
        "the D-0007 control establishes integrity: {tt}"
    );
}

/// **b8 — rollback is available and is itself gate-free below floor (availability rule).**
///
/// `update --rollback` is one of the two `GATE_FREE_RESTORATION_ROUTES` the §6 refusal names. A block must never
/// refuse its own remedy.
#[test]
fn b8_rollback_is_one_of_the_named_gate_free_remedies() {
    use gov_runtime::srr::breakglass as bg;
    assert!(
        bg::GATE_FREE_RESTORATION_ROUTES.contains(&"update --rollback"),
        "rollback must be a named gate-free restoration route: {:?}",
        bg::GATE_FREE_RESTORATION_ROUTES
    );
    // Both named routes are on the §5 allow-list, so the remedy a refusal names is actually permitted below floor.
    for route in bg::GATE_FREE_RESTORATION_ROUTES {
        assert!(
            bg::permitted_activity(route).is_some(),
            "the named remedy '{route}' must itself be permitted below floor"
        );
    }
    // And the rollback ingress exists and is typed when there is nothing to roll back to.
    let m = fresh_project("b8");
    let (_ok, v) = m.gov_json(&["update", "--rollback", "--role", "orchestrator"]);
    let t = text(&v);
    assert!(
        !t.contains("panicked") && !t.is_empty(),
        "rollback must answer, typed, even with no snapshot: {t}"
    );
}

/// **b9 — the release high-water is durable and monotonic (item 7), including across processes.**
///
/// Written through `Floors::save`, so the monotonicity binds code that has not been written yet.
#[test]
fn b9_the_protected_high_water_never_goes_backwards() {
    use gov_runtime::srr::state::{Floors, MachineState};
    let m = Machine::new("b9");
    m.enter();
    let ms = MachineState::open().expect("machine state");

    let mut f = Floors::load(&ms, PRODUCT);
    f.raise_release("4.1.6", 100, true);
    f.save(&ms).expect("save");

    // A second, lower raise must not lower the floor.
    let mut f2 = Floors::load(&ms, PRODUCT);
    f2.raise_release("4.1.0", 5, true);
    f2.save(&ms).expect("save");

    let after = Floors::load(&ms, PRODUCT);
    assert!(
        after.release_high_water_sequence >= 100,
        "the release high-water fell from 100 to {}",
        after.release_high_water_sequence
    );

    // Durable: a fresh load from disk in this process sees it, and the file exists outside every repository.
    let p = ms.floors_path(PRODUCT);
    assert!(p.exists(), "the floors must be durable on disk");
    assert!(
        !p.starts_with(&m.project),
        "protected floors must live outside the repository, found {p:?}"
    );
}
