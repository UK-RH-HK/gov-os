//! Immutable releases (framework §75D, protocol §8): build a release payload + manifest; verify hashes.
use crate::kernel::{build_manifest, stage_payload, KERNEL_MANIFEST};
use crate::util::{hash_tree, now_iso, read_json, read_text, read_yaml, write_json, write_text};
use crate::{GovError, Result, CLI_VERSION, FRAMEWORK_NAME, RUNTIME_VERSION};
use serde_json::{json, Value};
use std::path::Path;

fn git_out(root: &Path, args: &[&str]) -> Option<String> {
    std::process::Command::new("git")
        .args(args)
        .current_dir(root)
        .output()
        .ok()
        .filter(|o| o.status.success())
        .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string())
        .filter(|s| !s.is_empty())
}

/// Materialise the kernel source tree (framework/, migrations/, tools/) of `commit` into `dest` via `git archive`.
fn checkout_kernel_source(canonical_root: &Path, commit: &str, dest: &Path) -> Result<()> {
    std::fs::create_dir_all(dest)?;
    let archive = std::process::Command::new("git")
        .args([
            "archive",
            "--format=tar",
            commit,
            "framework",
            "migrations",
            "tools",
        ])
        .current_dir(canonical_root)
        .output()
        .map_err(|e| GovError::new("IO_ERROR", format!("git archive: {e}")))?;
    if !archive.status.success() {
        return Err(GovError::new(
            "RELEASE_REPRODUCTION_FAILED",
            format!(
                "git archive {commit} failed: {}",
                String::from_utf8_lossy(&archive.stderr)
            ),
        ));
    }
    let mut tar = std::process::Command::new("tar")
        .args(["-x", "-C", &dest.to_string_lossy()])
        .stdin(std::process::Stdio::piped())
        .spawn()
        .map_err(|e| GovError::new("IO_ERROR", format!("tar: {e}")))?;
    {
        use std::io::Write;
        tar.stdin.take().unwrap().write_all(&archive.stdout)?;
    }
    let st = tar.wait()?;
    if !st.success() {
        return Err(GovError::new(
            "RELEASE_REPRODUCTION_FAILED",
            "tar extraction failed",
        ));
    }
    Ok(())
}

/// Build a release, recording its certification status.
///
/// **The `OWNER-DECISION-0006` §6 bullet 3 sink.** This is the only function that mints a release with a
/// certification status, and it takes no `Project`, so it structurally cannot reach
/// `control::guard_write` — exactly the shape that made `AR29-B1` and `AR29-B2` possible one bullet over. The §6
/// check is therefore taken inside the effect: while this machine is marked `DEGRADED — RECOVERY ONLY`, it
/// certifies nothing.
pub fn build(
    canonical_root: &Path,
    version: &str,
    out_root: &Path,
    certification_status: &str,
    evidence: Option<&str>,
) -> Result<Value> {
    crate::srr::breakglass::guard_effect(
        crate::srr::breakglass::Effect::ReleaseCertification,
        "release build",
    )?;
    // BC-P2-37 — minting a certification claim is an authority-gated act, and the authority is the owner's
    // `release`-role signing key (ARCH-0003 §4: signed release metadata binds certification evidence; §10: build
    // provenance and certification evidence never replace release signatures). `gov` verifies and never signs
    // (SRR-R0-L4), so it cannot mint an authenticated claim, and an unsigned one in `manifest.json` is exactly the
    // masquerade Contract v3:150 forbids — any role could produce it (A0-A2-04). The request is refused before
    // anything is written; non-certifying statuses (`READY_FOR_…`, `REJECTED`, `UNCERTIFIED`) are unaffected.
    if crate::update::claims_certification(certification_status) {
        return Err(GovError::new(
            "RELEASE_CERTIFICATION_REQUIRES_SIGNED_METADATA",
            format!("`--certification {certification_status}` refused: a certification claim is authenticated only by release metadata signed under the owner's `release` role (evidence.certification), and `gov` never signs. An unsigned certification written into manifest.json would be treated as uncertified everywhere and could only masquerade as certified production (Contract v3:150)."),
        )
        .with_details(json!({
            "requested_status": certification_status,
            "authority": "the `release` role of the administrator-provisioned trust root (ARCH-0003 §4)",
            "carrier": "signed release metadata: evidence.certification.status, verified by `gov update --check` against this machine's trusted root",
            "written": false,
        })));
    }
    // IP-2 (WS-1/12, BC-P2-01) — a release is built only from a canonical tree whose capability-contract chain is
    // bound to the owner's approved source: the canonical import, the compiled form, the evidence map, the generated
    // view and the source lock all verify (`contracts::verify`). Checked before anything is written.
    let contract = pre_release_contract(canonical_root, version)?;
    // IP-WS02-13 — G0 and G5 of the health tier contract before minting (Contract v3:798, BC-P2-07; A0-O5-09).
    let health = pre_release_health(canonical_root, version)?;
    let dir = out_root.join("releases").join(version);
    if dir.join("manifest.yaml").exists() {
        return Err(GovError::new(
            "RELEASE_IMMUTABLE",
            format!(
                "release {version} already exists at {} (releases are immutable; bump the version)",
                dir.display()
            ),
        ));
    }
    // Reproducibility (protocol §8): a version that already exists in the canonical release directory is rebuilt from
    // the kernel source tree at its recorded release_commit, never from the current working tree.
    let existing = canonical_root
        .join("release")
        .join("releases")
        .join(version)
        .join("manifest.json");
    let mut reproduced_from: Option<String> = None;
    let mut _scratch: Option<std::path::PathBuf> = None;
    let (framework, source_root): (std::path::PathBuf, std::path::PathBuf) = if existing.exists() {
        let m = read_json(&existing)?;
        let commit = m["release_commit"].as_str().unwrap_or("").to_string();
        let tmp = std::env::temp_dir().join(format!(
            "gov-release-reproduce-{}-{}",
            version,
            crate::util::short_uuid()
        ));
        checkout_kernel_source(canonical_root, &commit, &tmp)?;
        reproduced_from = Some(commit);
        _scratch = Some(tmp.clone());
        (tmp.join("framework"), tmp)
    } else {
        (
            canonical_root.join("framework"),
            canonical_root.to_path_buf(),
        )
    };
    if !framework.join("KERNEL.yaml").exists() {
        return Err(GovError::new(
            "KERNEL_SOURCE_NOT_FOUND",
            "canonical framework/ not found",
        ));
    }
    let meta = read_yaml(&framework.join("KERNEL.yaml"))?;
    if meta["version"].as_str() != Some(version) {
        return Err(GovError::new(
            "VERSION_MISMATCH",
            format!(
                "framework/KERNEL.yaml version {} != requested {version}",
                meta["version"]
            ),
        ));
    }
    let _ = &source_root;
    let kernel = dir.join("kernel");
    stage_payload(&framework, &kernel)?;
    let mut km = build_manifest(&kernel)?;
    km["built_at"] = json!(now_iso());
    write_json(&kernel.join(KERNEL_MANIFEST), &km)?;
    let migrations = crate::migrations::framework::load_migrations(&kernel);
    let mig_ids: Vec<String> = migrations
        .iter()
        .filter(|m| m["to_version"].as_str() == Some(version))
        .filter_map(|m| m["id"].as_str().map(|s| s.to_string()))
        .collect();
    let rebuilds: Vec<String> = migrations
        .iter()
        .filter(|m| m["to_version"].as_str() == Some(version))
        .flat_map(|m| {
            m["affected_indexes"]
                .as_array()
                .cloned()
                .unwrap_or_default()
        })
        .filter_map(|v| v.as_str().map(|s| s.to_string()))
        .collect::<std::collections::BTreeSet<_>>()
        .into_iter()
        .collect();
    let breaking: Vec<String> = migrations
        .iter()
        .filter(|m| {
            m["to_version"].as_str() == Some(version) && m["breaking"].as_bool().unwrap_or(false)
        })
        .map(|m| m["description"].as_str().unwrap_or("").to_string())
        .collect();
    let gates: Vec<String> = migrations
        .iter()
        .filter(|m| m["to_version"].as_str() == Some(version))
        .filter_map(|m| {
            m["human_gate"]
                .as_str()
                .filter(|g| *g != "none")
                .map(|s| s.to_string())
        })
        .collect();
    // Migration record integrity (verifier NV-19 / M-N3): every migration into this version must deliver, or
    // explicitly declare, the overlay-template changes between its source payload and this payload.
    let mut substance: Vec<String> = vec![];
    for m in migrations
        .iter()
        .filter(|m| m["to_version"].as_str() == Some(version))
    {
        let from = m["from_version"].as_str().unwrap_or("");
        let old_tpl = canonical_root
            .join("release")
            .join("releases")
            .join(from)
            .join("kernel")
            .join("overlay-templates");
        if old_tpl.is_dir() {
            substance.extend(crate::migrations::framework::check_substance(
                m,
                &old_tpl,
                &kernel.join("overlay-templates"),
            ));
        }
    }
    // a NEW version is refused; reproducing a historical version reports the problems its shipped migrations carried
    if !substance.is_empty() && reproduced_from.is_none() {
        let _ = std::fs::remove_dir_all(&dir);
        return Err(GovError::new(
            "MIGRATION_INCOMPLETE",
            format!("release {version} refused: {}", substance.join("; ")),
        )
        .with_details(json!({"problems": substance})));
    }
    let notes_path = canonical_root
        .join("release")
        .join("notes")
        .join(format!("{version}.md"));
    let notes = read_text(&notes_path)
        .unwrap_or_else(|_| format!("Release {version} of {FRAMEWORK_NAME}."));
    let commit = reproduced_from
        .clone()
        .or_else(|| git_out(canonical_root, &["rev-parse", "HEAD"]))
        .unwrap_or("unknown".into());
    let branch =
        git_out(canonical_root, &["rev-parse", "--abbrev-ref", "HEAD"]).unwrap_or("unknown".into());
    let (_, file_hashes) = hash_tree(&kernel, &[KERNEL_MANIFEST])?;
    let manifest = json!({
        "framework": FRAMEWORK_NAME, "version": version, "release_commit": commit, "release_hash": km["payload_hash"], "schema_versions": km["schema_versions"], "cli_version": CLI_VERSION, "runtime_version": RUNTIME_VERSION,
        "supported_from_versions": km["supported_from_versions"], "migration_ids": mig_ids, "adapter_versions": km["adapter_versions"], "required_index_rebuilds": rebuilds, "breaking_changes": breaking, "human_gates": gates,
        "file_hashes": file_hashes, "release_notes": notes, "rollback_procedure": "gov update --rollback restores the previous kernel, overlay snapshot and framework.lock from .governance-runtime/update/<version>/ and rebuilds indexes; spec/ and product/ are never modified by an update.",
        "certification": {"status": certification_status, "implementer_evidence": evidence.unwrap_or(""), "independent_verifier": "", "certified_at": ""}, "built_at": now_iso(), "immutable": true,
        "provenance": {"release_branch": branch, "release_tag": format!("v{version}-rc1"), "reproduced_from_commit": reproduced_from, "kernel_source": if reproduced_from.is_some() { "git archive of release_commit" } else { "working tree" }, "migration_substance_problems": substance},
    });
    let schemas = crate::schemas::SchemaRegistry::new(&kernel.join("schemas"));
    schemas.validate("release-manifest", &manifest, "(release manifest)")?;
    crate::util::write_yaml(&dir.join("manifest.yaml"), &manifest)?;
    write_json(&dir.join("manifest.json"), &manifest)?;
    write_text(&dir.join("RELEASE_NOTES.md"), &notes)?;
    write_text(
        &dir.join("ROLLBACK.md"),
        manifest["rollback_procedure"].as_str().unwrap_or(""),
    )?;
    if let Some(t) = _scratch {
        let _ = std::fs::remove_dir_all(t);
    }
    // The built release is verified as written — every payload file against the manifest's hashes, and the kernel
    // manifest against the release hash — before it is reported as built. A release that does not verify is removed.
    let built = verify(&dir)?;
    if built["ok"] != true {
        let _ = std::fs::remove_dir_all(&dir);
        return Err(GovError::new(
            "RELEASE_VERIFICATION_FAILED",
            format!("release {version} was written but does not verify against its own manifest; it has been removed"),
        )
        .with_details(built));
    }
    // The pre-release checks are evidence of how this release was built; they are kept beside the immutable
    // manifest (not inside it, so a reproduction of an earlier release still reproduces its manifest).
    // OWNER-DECISION-P2-0002 requirement 4: release-relevant evidence runs on provisioned machines. The build states
    // the posture of the machine it ran on, so evidence from a machine with no trust anchor cannot pass for it.
    let machine_posture = match crate::srr::state::resolve_state_root() {
        Ok(r) if crate::srr::state::MachineState::read_only(&r).is_provisioned() => "PROVISIONED",
        Ok(_) => "UNPROVISIONED",
        Err(_) => "UNDETERMINED",
    };
    let checks = json!({
        "version": version,
        "machine_posture": machine_posture,
        "release_evidence_eligible": machine_posture == "PROVISIONED"
            && contract["verdict"] == "CONTRACT_SOURCE_BOUND",
        "capability_contract": contract,
        "health": health,
        "built_release_verified": {"ok": true, "release_hash_matches_kernel": built["release_hash_matches_kernel"]},
        "checked_at": now_iso(),
    });
    write_json(&dir.join("PRE_RELEASE_CHECKS.json"), &checks)?;
    let mut out = manifest;
    out["pre_release_checks"] = checks;
    Ok(out)
}

/// IP-2 — the canonical tree's capability-contract binding, as `release::build` requires it.
///
/// The IP's purpose is that "a release must not ship derived contract views that diverge from the owner source".
/// A chain that is present and does not verify — the import, compiled form, evidence map, generated view, schema or
/// lock diverging from the approved source, or unreadable — refuses the build (`RELEASE_CONTRACT_NOT_BOUND`). A tree
/// that does not carry the whole chain (a payload-only canonical tree — framework/, migrations/, tools/ — which is how
/// release tooling and every root-of-trust probe builds releases) cannot ship a divergent view it does not have: that
/// is recorded as `INCOMPLETE_IN_THIS_TREE`, never as bound, and such a build is not release-evidence eligible. The
/// kernel payload itself carries no contract view (`framework/contracts` is not a payload directory).
fn pre_release_contract(canonical_root: &Path, version: &str) -> Result<Value> {
    match crate::contracts::verify(canonical_root) {
        Ok(v) if v["verdict"] == "CONTRACT_SOURCE_BOUND" => Ok(json!({"verdict": v["verdict"], "owner_source_sha256": v["owner_source_sha256"], "capability_count": v["capability_count"], "checklist_item_count": v["checklist_item_count"]})),
        Ok(v) => Err(GovError::new(
            "RELEASE_CONTRACT_NOT_BOUND",
            format!("release {version} refused: contracts::verify returned {} rather than CONTRACT_SOURCE_BOUND", v["verdict"]),
        )),
        Err(e) if e.code.ends_with("_MISSING") => Ok(json!({
            "verdict": "INCOMPLETE_IN_THIS_TREE",
            "missing": e.code,
            "message": e.message,
            "note": "the canonical tree does not carry the whole capability-contract chain, so no contract binding is claimed for this build; a present chain that diverges refuses the build",
        })),
        Err(e) => Err(GovError::new(
            "RELEASE_CONTRACT_NOT_BOUND",
            format!("release {version} refused: the canonical tree's capability-contract chain does not verify ({}: {}). A release must not be built from a tree whose derived contract views diverge from the owner's approved source.", e.code, e.message),
        )
        .with_details(json!({"contract_error": e.code, "contract_details": e.details, "remediation": "gov contract verify; regenerate the derived views from the approved source with gov contract compile"}))),
    }
}

/// IP-WS02-13 — the health tier contract at release build.
///
/// When the canonical root is a governed installation, G0 (`scheduler::guard("release.build")`) refuses under an
/// active hard-block and G5 runs the full governance suite, fresh; an `UNHEALTHY` verdict or a `RED` health state
/// refuses the build. When it is not — the Governance OS source repository is the framework's own source, not a
/// project governed by an installed kernel — the governed-project suite has no subject, and that is reported as
/// exactly that rather than as a pass; the release-level checks ([`pre_release_contract`] and the verification of
/// the built release) run instead.
fn pre_release_health(canonical_root: &Path, version: &str) -> Result<Value> {
    let p = crate::Project::open(canonical_root);
    if !p.is_installed() {
        return Ok(json!({
            "tier": "G5",
            "ran": false,
            "reason": "the canonical root is not a governed installation (no governance/framework.lock), so the governed-project suite has no subject there; the release-level checks ran instead: the capability-contract binding (contracts::verify) and the verification of the built release against its manifest",
        }));
    }
    crate::scheduler::guard(&p, crate::scheduler::catalogue::ops::RELEASE_BUILD, &[])?;
    let mut o = crate::scheduler::RunOptions::new(
        crate::scheduler::Tier::G5,
        crate::scheduler::Trigger::new("release.build").with_subject(version),
    );
    o.surface = "tier:G5".into();
    o.record = crate::scheduler::RecordPolicy::Never;
    let r = crate::verification::audit_with(&p, &o)?;
    let verdict = r["verdict"].as_str().unwrap_or("UNHEALTHY").to_string();
    let state = r["state"].as_str().unwrap_or("").to_string();
    if verdict == "UNHEALTHY" || state == "RED" || r["counts"]["critical"].as_u64().unwrap_or(0) > 0
    {
        return Err(GovError::new(
            "RELEASE_HEALTH_REFUSED",
            format!("release {version} refused: the G5 full governance suite on the canonical installation is not acceptable (verdict {verdict}, health {state})"),
        )
        .with_details(r));
    }
    Ok(
        json!({"tier": "G5", "ran": true, "verdict": verdict, "state": state, "health_result": r["health_result"], "counts": r["counts"]}),
    )
}

pub fn verify(release_dir: &Path) -> Result<Value> {
    let manifest = read_json(&release_dir.join("manifest.json"))
        .or_else(|_| read_yaml(&release_dir.join("manifest.yaml")))?;
    let kernel = release_dir.join("kernel");
    let (_, actual) = hash_tree(&kernel, &[KERNEL_MANIFEST])?;
    let expected: std::collections::BTreeMap<String, String> =
        serde_json::from_value(manifest["file_hashes"].clone()).unwrap_or_default();
    let modified: Vec<String> = expected
        .iter()
        .filter(|(k, v)| actual.get(*k) != Some(*v))
        .map(|(k, _)| k.clone())
        .collect();
    let missing: Vec<String> = expected
        .keys()
        .filter(|k| !actual.contains_key(*k))
        .cloned()
        .collect();
    let added: Vec<String> = actual
        .keys()
        .filter(|k| !expected.contains_key(*k))
        .cloned()
        .collect();
    let km = crate::kernel::read_manifest(&kernel)?;
    let hash_ok = km["payload_hash"] == manifest["release_hash"];
    // BC-P2-37: manifest.json is unsigned. Its certification block is reported as a claim; the effective status is
    // what this machine's trust root authenticates from the signed release metadata, otherwise uncertified.
    let basis = crate::srr::verifier::certification_of(&kernel);
    let effective = basis
        .authenticated_status
        .clone()
        .unwrap_or_else(|| crate::update::UNCERTIFIED.to_string());
    Ok(
        json!({"version": manifest["version"], "ok": modified.is_empty() && missing.is_empty() && added.is_empty() && hash_ok, "modified": modified, "missing": missing, "added": added, "release_hash_matches_kernel": hash_ok,
               "certification": {"effective_status": effective, "authenticated": basis.authenticated_status.is_some(), "basis": basis.basis, "unsigned_manifest_claim": manifest["certification"]}}),
    )
}
