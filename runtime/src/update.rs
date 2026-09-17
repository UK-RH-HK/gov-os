//! `gov update` (framework §82, protocol §12): versioned, impact-checked kernel replacement with migrations,
//! overlay preservation, adapter regeneration, index rebuild, verification and CIT-E commit or rollback.
use crate::kernel::{
    install_kernel, release_commit_for_source, resolve_kernel_source, source_label, KERNEL_MANIFEST,
};
use crate::lock::{compare_versions, write_lock};
use crate::memory::db::RuntimeDb;
use crate::migrations::framework::{
    apply, load_migrations, path as migration_path, reconcile_overlay_defaults, MigrationOutcome,
};
use crate::orchestration::{control, gates};
use crate::util::{
    copy_dir, hash_tree, now_iso, read_json, read_yaml, remove_dir_if_exists, write_json,
};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};
use std::path::Path;

fn migrations_for_source(src: &Path) -> Vec<Value> {
    let m = load_migrations(src);
    if !m.is_empty() {
        return m;
    }
    src.parent()
        .map(|p| load_migrations(p.join("migrations").parent().unwrap_or(p)))
        .unwrap_or_default()
}

fn source_manifest(src: &Path) -> Result<Value> {
    // A built release dir has manifest.json next to kernel/; a raw framework/ dir has KERNEL.yaml only.
    if let Some(parent) = src.parent() {
        let m = parent.join("manifest.json");
        if m.exists() {
            return read_json(&m);
        }
    }
    let meta = read_yaml(&src.join("KERNEL.yaml"))?;
    let migs = migrations_for_source(src);
    let ver = meta["version"].as_str().unwrap_or("0").to_string();
    Ok(
        json!({"version": ver, "supported_from_versions": meta["supported_from_versions"], "migration_ids": migs.iter().filter(|m| m["to_version"].as_str() == Some(&ver)).map(|m| m["id"].clone()).collect::<Vec<_>>(), "breaking_changes": migs.iter().filter(|m| m["breaking"].as_bool().unwrap_or(false)).map(|m| m["description"].clone()).collect::<Vec<_>>(), "human_gates": migs.iter().filter_map(|m| m["human_gate"].as_str().filter(|g| *g != "none").map(|s| json!(s))).collect::<Vec<_>>(), "required_index_rebuilds": [], "release_notes": "(unreleased framework source)", "certification": {"status": "UNCERTIFIED"}}),
    )
}

/// CIT-P for a framework update against this project.
pub fn check(p: &Project, source: Option<&str>) -> Result<Value> {
    p.require_installed()?;
    let src = resolve_kernel_source(source.map(Path::new))?;
    let avail = source_manifest(&src)?;
    let current = p.framework_version();
    let target = avail["version"].as_str().unwrap_or("0").to_string();
    let ord = compare_versions(&current, &target);
    let supported: Vec<String> = avail["supported_from_versions"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default();
    let migs = migrations_for_source(&src);
    let chain = migration_path(&migs, &current, &target);
    let compatible = supported.iter().any(|s| s == &current) || current == target;
    let mut dry = MigrationOutcome::default();
    for m in &chain {
        let _ = apply(p, m, &src, true, &mut dry);
    }
    let breaking: Vec<Value> = chain
        .iter()
        .filter(|m| m["breaking"].as_bool().unwrap_or(false))
        .map(|m| m["description"].clone())
        .collect();
    let human_gates: Vec<Value> = chain
        .iter()
        .filter_map(|m| {
            m["human_gate"]
                .as_str()
                .filter(|g| *g != "none")
                .map(|s| json!(s))
        })
        .collect();
    let cert = avail["certification"]["status"]
        .as_str()
        .unwrap_or("UNCERTIFIED")
        .to_string();
    let radius = if !breaking.is_empty() {
        "R5"
    } else if !dry.overlay_keys_changed.is_empty() {
        "R4"
    } else {
        "R3"
    };
    let human_gate_required =
        !breaking.is_empty() || !human_gates.is_empty() || cert != "CERTIFIED";
    let impact = json!({"radius": radius, "overlay_changes": dry.overlay_keys_changed, "index_rebuild": dry.index_rebuild, "regenerate_adapters": dry.regenerate_adapters, "notes": dry.notes, "breaking_changes": breaking, "human_gates": human_gates, "consequences": [
        format!("kernel {current} → {target} ({} migration step(s))", chain.len()), "spec/ and product/ are not touched (INV-013)", if dry.index_rebuild { "all derived indexes are rebuilt after install" } else { "no index rebuild required" },
        if cert == "CERTIFIED" { "target release is certified" } else { "target release is NOT certified: human approval required" }]});
    Ok(
        json!({"current": current, "available": target, "source": src.display().to_string(), "up_to_date": ord != std::cmp::Ordering::Less, "downgrade": ord == std::cmp::Ordering::Greater, "compatible": compatible, "migration_path": chain.iter().map(|m| m["id"].clone()).collect::<Vec<_>>(), "migration_path_complete": !chain.is_empty() || current == target,
        "certification": cert, "impact": impact, "human_gate_required": human_gate_required, "recommendation": if ord != std::cmp::Ordering::Less { "nothing to do" } else if !compatible { "unsupported upgrade path: adopt an intermediate release" } else if human_gate_required { "review impact; approve with `gov update --apply --approve --by <human>`" } else { "safe: `gov update --apply`" }}),
    )
}

fn snapshot_dir(p: &Project, target: &str) -> std::path::PathBuf {
    p.runtime_dir().join("update").join(target)
}

/// The gate raised for updating to `target`, if any.
fn update_gate(p: &Project, target: &str) -> Option<crate::records::Record> {
    let store = crate::records::RecordStore::load(&p.root);
    store
        .of_type("human-gate")
        .into_iter()
        .rfind(|g| g.get("trigger") == "framework_update" && g.get("update_target") == target)
        .cloned()
}

pub fn apply_update(
    p: &mut Project,
    source: Option<&str>,
    approve: bool,
    by: &str,
) -> Result<Value> {
    apply_update_opts(p, source, approve, by, None, false)
}

/// `update` ingress with the Signed Release Root request fields.
pub fn apply_update_opts(
    p: &mut Project,
    source: Option<&str>,
    approve: bool,
    by: &str,
    channel: Option<String>,
    break_glass: bool,
) -> Result<Value> {
    control::guard_write(p, "update --apply")?;
    crate::authority::require(p, "update_apply")?;
    let chk = check(p, source)?;
    if chk["up_to_date"].as_bool().unwrap_or(false) {
        return Ok(json!({"applied": false, "reason": "already up to date", "check": chk}));
    }
    if !chk["compatible"].as_bool().unwrap_or(false)
        || !chk["migration_path_complete"].as_bool().unwrap_or(false)
    {
        return Err(GovError::new(
            "UPDATE_UNSUPPORTED",
            "no supported migration path from the installed version",
        )
        .with_details(chk));
    }
    let target_v = chk["available"].as_str().unwrap_or("").to_string();
    if chk["human_gate_required"].as_bool().unwrap_or(true) {
        // INV-008: approval means a presented, answered gate record — never a CLI flag alone (verifier M3 / HV-11)
        let gate = match update_gate(p, &target_v) {
            Some(g) => g,
            None => {
                let g = gates::create_system(
                    p,
                    json!({"question": format!("Approve framework update {} → {}?", chk["current"], chk["available"]), "why_now": "gov update --apply requested", "current_state": format!("installed {}", chk["current"]), "options": [{"id": "A", "description": "approve update"}, {"id": "B", "description": "stay on current release"}], "impact": chk["impact"]["consequences"].to_string(), "reversibility": "gov update --rollback restores kernel/overlay/lock", "recommendation": "A after reviewing release notes", "confidence": 0.7, "trigger": "framework_update", "update_target": target_v, "impact_radius": chk["impact"]["radius"]}),
                )?;
                let gid = g["id"].as_str().unwrap_or("").to_string();
                if !approve {
                    return Err(GovError::new("HUMAN_GATE_REQUIRED", format!("update requires human approval: gate {gid} created; present it (`gov gate present {gid}`), record the answer (`gov decide {gid} --option A --by <human>`), then re-run `gov update --apply --approve`")).with_details(json!({"gate": gid, "check": chk})));
                }
                crate::records::RecordStore::load(&p.root)
                    .get(&gid)
                    .cloned()
                    .unwrap()
            }
        };
        let answered_yes = gate.get("gate_status") == "ANSWERED"
            && gate.data["answer"]["option"].as_str() == Some("A")
            && gate
                .data
                .get("presented_in_chat")
                .and_then(|v| v.as_bool())
                .unwrap_or(false);
        if !answered_yes {
            return Ok(
                json!({"applied": false, "reason": "human gate not presented/answered (INV-008): --approve is not a substitute for an answered gate record", "human_gate": gate.id(), "gate_status": gate.get("gate_status"), "presented_in_chat": gate.data.get("presented_in_chat"), "next": [format!("gov gate present {}", gate.id()), format!("gov decide {} --option A --by <human>", gate.id()), "gov update --apply --approve"], "check": chk}),
            );
        }
        if gate.get("gate_status") == "ANSWERED"
            && gate.data["answer"]["option"].as_str() == Some("B")
        {
            return Ok(
                json!({"applied": false, "reason": "human declined the update", "human_gate": gate.id()}),
            );
        }
    }
    let target = chk["available"].as_str().unwrap_or("").to_string();
    let src = Path::new(chk["source"].as_str().unwrap_or(""));
    let db = RuntimeDb::open(&p.db_path())?;
    db.init_schema()?;
    let ck = crate::checkpoints::create(p, &db, json!({"trigger": "before_model_switch", "next_action": format!("gov update --apply to {target}"), "last_completed_step": "pre-update checkpoint"})).ok();
    // snapshot kernel + overlay + lock + generated
    let snap = snapshot_dir(p, &target);
    remove_dir_if_exists(&snap)?;
    for sub in ["kernel", "project", "generated"] {
        let s = p.governance_dir().join(sub);
        if s.exists() {
            copy_dir(&s, &snap.join(sub))?;
        }
    }
    std::fs::copy(p.lock_path(), snap.join("framework.lock"))?;
    write_json(
        &snap.join("snapshot.json"),
        &json!({"from": chk["current"], "to": target, "at": now_iso(), "checkpoint": ck.as_ref().map(|c| c["id"].clone()), "migrations": chk["migration_path"], "by": by, "session": p.session_id, "role": p.role, "source": source_label(src), "release_commit": release_commit_for_source(src)}),
    )?;
    let (overlay_before, _) = hash_tree(&p.overlay_dir(), &[])?;
    // Privileged lifecycle ingress `update`: the one verification policy. Admission happens BEFORE any protected
    // write, and the floor check inside it binds this ingress exactly as it binds `rollback`.
    let auth = crate::srr::admit(
        crate::srr::AdmissionRequest::new(crate::srr::Ingress::Update, src)
            .with_channel(channel)
            .with_break_glass(break_glass)
            .with_reason(Some(format!("gov update --apply to {target}"))),
    )?;
    let result: Result<Value> = (|| {
        let manifest = install_kernel(&auth, &p.governance_dir())?;
        let migs = load_migrations(&p.kernel_dir());
        let chain = migration_path(&migs, chk["current"].as_str().unwrap_or(""), &target);
        let mut out = MigrationOutcome::default();
        for m in &chain {
            p.schemas().validate("migration", m, "(migration)")?;
            apply(p, m, &p.kernel_dir(), false, &mut out)?;
        }
        // template-default reconciliation (verifier M-N3): untouched overlay defaults follow the new kernel templates
        let reconciled = reconcile_overlay_defaults(
            &p.overlay_dir(),
            &snap.join("kernel").join("overlay-templates"),
            &p.kernel_dir().join("overlay-templates"),
            false,
        )?;
        out.overlay_keys_changed.extend(reconciled.clone());
        // lock provenance (verifier M-N1/M-N2): the release's commit and a logical source label, never machine state
        let consumer_commit = p.git_commit();
        write_lock(
            &p.lock_path(),
            &manifest,
            &source_label(src),
            Some(&release_commit_for_source(src)),
            Some(&consumer_commit),
        )?;
        for m in &chain {
            for op in m["operations"].as_array().cloned().unwrap_or_default() {
                if op["op"] == "set_lock_field" {
                    let mut lock = read_yaml(&p.lock_path())?;
                    lock[op["key"].as_str().unwrap_or("x")] = op["value"].clone();
                    crate::util::write_yaml(&p.lock_path(), &lock)?;
                }
            }
        }
        p.invalidate();
        // overlay preservation: only migration-declared changes may differ
        let (overlay_after, _) = hash_tree(&p.overlay_dir(), &[])?;
        if overlay_after != overlay_before && out.overlay_keys_changed.is_empty() {
            return Err(GovError::new(
                "OVERLAY_CLOBBERED",
                "project overlay changed without a declaring migration (INV-013)",
            ));
        }
        if !p.overlay().problems.is_empty() {
            return Err(GovError::new(
                "OVERLAY_INVALID",
                format!(
                    "overlay invalid after migration: {}",
                    p.overlay().problems.join("; ")
                ),
            ));
        }
        crate::tools::generate_registry(p)?;
        crate::adapters::generate(p)?;
        let rebuilt = if out.index_rebuild || !chk["impact"]["index_rebuild"].is_null() {
            Some(
                crate::memory::indexer::rebuild(
                    p,
                    crate::memory::indexer::IndexOptions {
                        incremental: !out.index_rebuild,
                        ..Default::default()
                    },
                )?
                .manifest_hash,
            )
        } else {
            None
        };
        let doc = crate::doctor::run(p)?;
        let critical: Vec<Value> = doc
            .checks
            .iter()
            .filter(|c| !c["ok"].as_bool().unwrap_or(true) && c["severity"] == "critical")
            .cloned()
            .collect();
        if !critical.is_empty() {
            return Err(GovError::new(
                "VERIFICATION_FAILED",
                format!(
                    "doctor reports critical findings after update: {}",
                    critical
                        .iter()
                        .map(|c| c["id"].as_str().unwrap_or("").to_string())
                        .collect::<Vec<_>>()
                        .join(", ")
                ),
            )
            .with_details(json!(critical)));
        }
        let audit = crate::verification::audit(
            p,
            &crate::verification::SuiteOptions {
                deep: false,
                families: vec![
                    "schema_invariants".into(),
                    "mutation_scope".into(),
                    "adapter_portability".into(),
                    "secrets_sensitivity_indexing".into(),
                ],
            },
            false,
        )?;
        if audit["counts"]["critical"].as_u64().unwrap_or(0) > 0 {
            return Err(GovError::new(
                "VERIFICATION_FAILED",
                "governance suite reports critical findings after update",
            )
            .with_details(audit));
        }
        // Transaction step (9), SRR-R0-L5: the floors advance only after the atomic commit and its verification,
        // and only after the post-install governance suite has accepted the result.
        let protected = crate::srr::record_installed(&auth)?;
        Ok(
            json!({"migrations": chain.iter().map(|m| m["id"].clone()).collect::<Vec<_>>(), "operations": out.applied, "overlay_keys_changed": out.overlay_keys_changed, "overlay_reconciled": reconciled, "index_manifest": rebuilt, "doctor": doc.verdict, "audit": audit["verdict"], "lock": {"release_commit": release_commit_for_source(src), "source": source_label(src)}, "release_authenticity": auth.to_value(), "protected_state": protected}),
        )
    })();
    match result {
        Ok(v) => {
            let ledger = p.root.join("spec/reports/framework-updates.jsonl");
            let mut text = crate::util::read_text(&ledger).unwrap_or_default();
            text.push_str(&serde_json::to_string(&json!({"at": now_iso(), "event": "update", "from": chk["current"], "to": target, "by": by, "session": p.session_id, "role": p.role, "result": "committed", "release_commit": release_commit_for_source(src), "source": source_label(src), "details": v}))?);
            text.push('\n');
            crate::util::write_text(&ledger, &text)?;
            let db2 = RuntimeDb::open(&p.db_path())?;
            let _ = crate::checkpoints::create(
                p,
                &db2,
                json!({"trigger": "accepted_cit", "next_action": "gov status", "last_completed_step": format!("framework updated to {target}")}),
            );
            Ok(
                json!({"applied": true, "from": chk["current"], "to": target, "details": v, "rollback": "gov update --rollback"}),
            )
        }
        Err(e) => {
            // Transaction abort, not a backward ingress: the floors were never advanced (step (9) is unreached),
            // so restoring the pre-update installation puts the machine back exactly at its current floor and
            // crosses no ingress boundary. `SRR-R0-L5` is what makes this safe and is why the ordering is fixed.
            crate::srr::staging::abandon(
                &auth.machine,
                &auth.staged,
                "update aborted; transaction rolled back",
            );
            let rb = rollback_internal(
                p,
                Some(&target),
                Some(&format!("automatic: {} ({})", e.code, e.message)),
                true,
                false,
            )?;
            Err(
                GovError::new(&e.code, format!("{} — update rolled back", e.message))
                    .with_details(json!({"rollback": rb, "details": e.details})),
            )
        }
    }
}

/// Restore kernel, overlay, generated and lock from the update snapshot; rebuild indexes. The rollback itself is
/// authoritative evidence (verifier L-N2 / directive §7): a ledger entry records source and target versions, the
/// initiating identity and authority, the reason, the migrations reverted, the resulting lock and the verification
/// result; the consumed snapshot is marked so it cannot be silently re-applied.
pub fn rollback(p: &mut Project, target: Option<&str>, reason: Option<&str>) -> Result<Value> {
    rollback_opts(p, target, reason, false)
}

/// Operator-initiated `rollback` ingress.
///
/// `OWNER-DECISION-0006` §9 — "the floor rule must govern `recovery`, `rollback` and every other backward-capable
/// privileged lifecycle ingress consistently". A rollback to a release below the machine's protected floors is
/// therefore refused by default and is admissible only under owner-authorised break-glass. The *transaction abort*
/// path inside [`apply_update_opts`] is different and does not cross this boundary: it restores the installation
/// the floors already describe, because step (9) never ran.
pub fn rollback_opts(
    p: &mut Project,
    target: Option<&str>,
    reason: Option<&str>,
    break_glass: bool,
) -> Result<Value> {
    rollback_internal(p, target, reason, false, break_glass)
}

fn rollback_internal(
    p: &mut Project,
    target: Option<&str>,
    reason: Option<&str>,
    transaction_abort: bool,
    break_glass: bool,
) -> Result<Value> {
    crate::authority::require(p, "update_apply")?;
    if !transaction_abort {
        crate::srr::breakglass::guard(
            &crate::srr::state::MachineState::open()?,
            crate::FRAMEWORK_NAME,
            "update --rollback",
        )?;
    }
    let base = p.runtime_dir().join("update");
    let dir = match target {
        Some(t) => base.join(t),
        None => {
            let mut dirs: Vec<_> = std::fs::read_dir(&base)
                .map(|rd| {
                    rd.filter_map(|e| e.ok())
                        .map(|e| e.path())
                        .filter(|x| {
                            x.join("snapshot.json").exists() && !x.join("consumed.json").exists()
                        })
                        .collect()
                })
                .unwrap_or_default();
            dirs.sort_by_key(|d| {
                std::fs::metadata(d.join("snapshot.json"))
                    .and_then(|m| m.modified())
                    .ok()
            });
            dirs.pop().ok_or_else(|| GovError::new("SNAPSHOT_MISSING", "no unconsumed update snapshot under .governance-runtime/update/ (every rollback consumes its snapshot; see spec/reports/framework-updates.jsonl)"))?
        }
    };
    if dir.join("consumed.json").exists() {
        return Err(GovError::new("SNAPSHOT_CONSUMED", format!("update snapshot {} was already rolled back (see spec/reports/framework-updates.jsonl)", dir.display())).with_details(read_json(&dir.join("consumed.json")).unwrap_or(Value::Null)));
    }
    let meta = read_json(&dir.join("snapshot.json"))?;
    let version_before = p.framework_version();
    let level = crate::authority::level_of(p, &p.role).unwrap_or(0);
    // Privileged lifecycle ingress `rollback`: the one verification policy. The snapshot's kernel payload is the
    // candidate; it is staged privately, measured, and checked against the machine's floors like any other
    // candidate. A snapshot on disk is *content*, and content never establishes its own admissibility.
    let auth = if transaction_abort {
        None
    } else {
        Some(crate::srr::admit(
            crate::srr::AdmissionRequest::new(crate::srr::Ingress::Rollback, &dir.join("kernel"))
                .with_break_glass(break_glass)
                .with_reason(reason.map(|r| r.to_string())),
        )?)
    };
    for sub in ["project", "generated"] {
        let s = dir.join(sub);
        let d = p.governance_dir().join(sub);
        if s.exists() {
            remove_dir_if_exists(&d)?;
            copy_dir(&s, &d)?;
        }
    }
    match auth.as_ref() {
        // Verified bytes in, verified bytes installed, atomically.
        Some(a) => {
            crate::kernel::install_kernel(a, &p.governance_dir())?;
        }
        // Transaction abort: restore the tree the floors already describe.
        None => {
            let s = dir.join("kernel");
            let d = p.governance_dir().join("kernel");
            if s.exists() {
                remove_dir_if_exists(&d)?;
                copy_dir(&s, &d)?;
            }
        }
    }
    std::fs::copy(dir.join("framework.lock"), p.lock_path())?;
    p.invalidate();
    let ok = p.kernel_dir().join(KERNEL_MANIFEST).exists()
        && crate::kernel::verify_kernel(&p.kernel_dir())
            .map(|v| v.ok)
            .unwrap_or(false);
    let r = crate::memory::indexer::rebuild(
        p,
        crate::memory::indexer::IndexOptions {
            incremental: false,
            ..Default::default()
        },
    )?;
    let doc = crate::doctor::run(p)
        .map(|d| d.verdict)
        .unwrap_or_else(|e| format!("doctor failed: {e}"));
    let lock = read_yaml(&p.lock_path()).unwrap_or(Value::Null);
    let lock_hash = crate::util::hash_value(&lock);
    let entry = json!({"at": now_iso(), "event": "rollback", "from": version_before, "to": meta["from"], "rolled_back_update": {"from": meta["from"], "to": meta["to"], "applied_at": meta["at"], "migrations": meta["migrations"], "by": meta["by"], "session": meta["session"]},
        "by": p.session_id, "session": p.session_id, "role": p.role, "authority_level": format!("L{level}"), "reason": reason.unwrap_or("not given"), "migrations_reverted": meta["migrations"],
        "resulting_lock": {"version": lock["version"], "release_hash": lock["release_hash"], "release_commit": lock["release_commit"], "source": lock["source"], "lock_hash": lock_hash},
        "verification": {"kernel_ok": ok, "doctor": doc, "index_manifest": r.manifest_hash}, "result": "rolled_back", "snapshot": dir.display().to_string()});
    let ledger = p.root.join("spec/reports/framework-updates.jsonl");
    let mut text = crate::util::read_text(&ledger).unwrap_or_default();
    text.push_str(&serde_json::to_string(&entry)?);
    text.push('\n');
    crate::util::write_text(&ledger, &text)?;
    write_json(
        &dir.join("consumed.json"),
        &json!({"consumed_at": now_iso(), "by": p.session_id, "role": p.role, "reason": reason, "ledger": "spec/reports/framework-updates.jsonl"}),
    )?;
    let protected = match auth.as_ref() {
        Some(a) => crate::srr::record_installed(a)?,
        None => Value::Null,
    };
    Ok(
        json!({"rolled_back_to": meta["from"], "from": version_before, "kernel_ok": ok, "doctor": entry["verification"]["doctor"], "index_manifest": r.manifest_hash, "ledger_entry": entry, "snapshot_consumed": true, "release_authenticity": auth.as_ref().map(|a| a.to_value()), "protected_state": protected}),
    )
}
