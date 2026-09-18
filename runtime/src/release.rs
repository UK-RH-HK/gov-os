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
    Ok(manifest)
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
    Ok(
        json!({"version": manifest["version"], "ok": modified.is_empty() && missing.is_empty() && added.is_empty() && hash_ok, "modified": modified, "missing": missing, "added": added, "release_hash_matches_kernel": hash_ok, "certification": manifest["certification"]}),
    )
}
