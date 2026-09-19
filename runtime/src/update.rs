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

/// The one spelling of the certified status. Only this file compares against it; `release::build` refuses to mint
/// it (`BC-P2-37`).
pub const CERTIFIED: &str = "CERTIFIED";
/// The status every unauthenticated certification claim is treated as.
pub const UNCERTIFIED: &str = "UNCERTIFIED";

/// Does a status string claim certification (`CERTIFIED`, any case, or a `CERTIFIED…` variant)?
pub fn claims_certification(status: &str) -> bool {
    status.trim().to_ascii_uppercase().starts_with(CERTIFIED)
}

/// The candidate's identity and compatibility, from the candidate **payload** — its `KERNEL.yaml` — and never from
/// the unsigned `manifest.json` a built release carries beside `kernel/` (`BC-P2-37`, D-0007 rule 2). These are the
/// bytes admission measures and, on a provisioned machine, binds to signed metadata; the decision taken here is
/// re-bound to the admitted release in [`bind_decision_to_admitted`].
fn candidate_identity(src: &Path) -> Result<Value> {
    let meta = read_yaml(&src.join("KERNEL.yaml"))?;
    let ver = match &meta["version"] {
        Value::String(v) => v.clone(),
        Value::Null => "0".into(),
        other => other.to_string(),
    };
    Ok(json!({"version": ver, "supported_from_versions": meta["supported_from_versions"]}))
}

/// CIT-P for a framework update against this project.
pub fn check(p: &Project, source: Option<&str>) -> Result<Value> {
    p.require_installed()?;
    let src = resolve_kernel_source(source.map(Path::new))?;
    let avail = candidate_identity(&src)?;
    // BC-P2-37: certification counts only when this machine's trust root authenticates it.
    let certification = crate::srr::verifier::certification_of(&src);
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
    // An unauthenticated certification is treated as uncertified everywhere (BC-P2-37; Contract v3:150, :161): the
    // unsigned manifest.json claim is reported in `certification_basis.unsigned_claim` and never decides anything.
    let cert = certification
        .authenticated_status
        .clone()
        .map(|s| s.trim().to_string())
        .unwrap_or_else(|| UNCERTIFIED.to_string());
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
    // OWNER-DECISION-P2-0002: whether this machine may install the candidate at all, stated before anyone decides.
    let admission = match crate::srr::verifier::refuse_external_source_if_unprovisioned(
        crate::srr::Ingress::Update,
        &src,
    ) {
        Ok(()) => {
            json!({"refused_before_staging": false, "decided_by": "the single verification policy at `gov update --apply` (signed release metadata on a provisioned machine)"})
        }
        Err(e) => {
            json!({"refused_before_staging": true, "code": e.code, "reason": e.message, "remediation": e.details["remediation"]})
        }
    };
    let mut out = json!({"current": current, "available": target, "source": src.display().to_string(), "admission": admission, "up_to_date": ord != std::cmp::Ordering::Less, "downgrade": ord == std::cmp::Ordering::Greater, "compatible": compatible, "migration_path": chain.iter().map(|m| m["id"].clone()).collect::<Vec<_>>(), "migration_path_complete": !chain.is_empty() || current == target,
        "certification": cert, "certification_basis": certification.to_value(), "impact": impact, "human_gate_required": human_gate_required, "recommendation": if ord != std::cmp::Ordering::Less { "nothing to do" } else if !compatible { "unsupported upgrade path: adopt an intermediate release" } else if human_gate_required { "review impact; approve with `gov update --apply --approve --by <human>`" } else { "safe: `gov update --apply`" }});
    // **`OWNER-DECISION-0006` §6 bullet 7** (`AR31-B1`). `gov update --check` used to emit
    // `{"current": <below-floor version>, "up_to_date": true, "recommendation": "nothing to do"}` on a machine
    // marked `DEGRADED — RECOVERY ONLY` — the bullet in the decision's own words, and the opposite of what is
    // true, since restoring an authenticated at-floor release is the only way out of break-glass. It is
    // read-only, so it never reaches `control::guard_write` and nothing refused it.
    //
    // `crate::srr::present::attach` is the §6 bullet 7 sink: it asks `crate::srr::breakglass::guard_effect` for
    // `Effect::PresentBelowFloorReleaseAsCurrent` and, when that refuses, rewrites the currency claim and carries
    // the marking rather than swallowing the refusal. Attaching the marking beside an affirmative `up_to_date`
    // would not have been enough — the claim itself is the forbidden presentation.
    crate::srr::present::attach("update --check", &mut out);
    Ok(out)
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
    // IP-WS02-12 asked also for the G0 hard-block guard (`scheduler::guard("update.apply")`) here, at entry. It is
    // deliberately not taken at entry: the blocks that govern `update.apply` include findings the update itself is
    // the remedy for — an older kernel's overlay deficit (D006 on a 4.1.1 installation, whose migration adds the
    // missing file) would refuse the only operation that repairs it. The purpose the IP states — no update applies
    // over a defect the full suite detects — is met after the install instead: the G5 run below re-executes every
    // check, fresh, against the updated installation, and an active hard-block (RED) or an UNHEALTHY verdict there
    // refuses the update and rolls it back.
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
    // OWNER-DECISION-P2-0002: on a machine with no trust anchor an external-source candidate is refused before a
    // Human Decision Gate is raised for it — nobody is asked to approve what admission will refuse.
    crate::srr::verifier::refuse_external_source_if_unprovisioned(
        crate::srr::Ingress::Update,
        Path::new(chk["source"].as_str().unwrap_or("")),
    )?;
    if chk["human_gate_required"].as_bool().unwrap_or(true) {
        // INV-008: approval means a presented, answered gate record — never a CLI flag alone (verifier M3 / HV-11)
        let gate = match update_gate(p, &target_v) {
            Some(g) => g,
            None => {
                // `AR29-B2` / `AR29-N4`. `update --apply` is on the OWNER-DECISION-0006 §5 allow-list as
                // restoration of an authenticated release, and §6 bullet 2 still forbids creating a new Human
                // Gate below floor. The refusal is taken here, at the same enforcement point the gate sink uses
                // and before any protected write, so the allow-list's promise and the reachable behaviour agree:
                // the operation completes below floor exactly when the target needs no gate, and the refusal
                // names `kernel reinstall` and `update --rollback`, which need none. An already-answered gate
                // (the `Some` arm) is neither a creation nor an approval and is unaffected.
                crate::srr::breakglass::guard_effect(
                    crate::srr::breakglass::Effect::HumanGateCreate,
                    "gate create (update --apply)",
                )?;
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
        // IP-7 (WS-3, BC-P2-08/09/10): the answer is honoured only through the one consumer API, which re-verifies
        // the T2 seal, the owner-signed human answer against the administrator-provisioned `human-gate` anchor and
        // its presentation receipt, refuses an agent resolution of this human-only trigger, and follows a revoked
        // decision. A field read of `gate_status`/`answer.option`/`presented_in_chat` could be satisfied by editing
        // the record.
        match gates::verified_answer(p, &gate.id()) {
            Ok(a) if a.authorises_blocked_work => {}
            Ok(a) => {
                return Ok(
                    json!({"applied": false, "reason": "human declined the update", "human_gate": gate.id(), "answer": a.to_value()}),
                );
            }
            Err(e) if e.code == "GATE_NOT_ANSWERED" => {
                return Ok(
                    json!({"applied": false, "reason": "human gate not presented/answered (INV-008): --approve is not a substitute for an answered gate record", "human_gate": gate.id(), "gate_status": gate.get("gate_status"), "presented_in_chat": gate.data.get("presented_in_chat"), "next": [format!("gov gate present {}", gate.id()), format!("gov decide {} --option A --answer-file <owner-signed answer>", gate.id()), "gov update --apply --approve"], "check": chk}),
                );
            }
            Err(e) => return Err(e),
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
    // BC-P2-38: this machine's protected record for the project, as it stands before the transaction; an abort puts
    // it back together with the bytes it describes.
    let prior_record = crate::srr::installation::read_project_record_raw(&p.root);
    // Privileged lifecycle ingress `update`: the one verification policy. Admission happens BEFORE any protected
    // write, and the floor check inside it binds this ingress exactly as it binds `rollback`.
    let auth = crate::srr::admit(
        crate::srr::AdmissionRequest::new(crate::srr::Ingress::Update, src)
            .with_channel(channel)
            .with_break_glass(break_glass)
            .with_reason(Some(format!("gov update --apply to {target}"))),
    )
    // A0-S5-01 / BC-P2-38: a refused update leaves nothing behind. The snapshot was taken for this attempt only;
    // left in place, `gov update --rollback` would "roll back" an update that never happened.
    .inspect_err(|_| {
        let _ = remove_dir_if_exists(&snap);
    })?;
    if let Err(e) = bind_decision_to_admitted(&chk, &auth, &target) {
        crate::srr::staging::abandon(&auth.machine, &auth.staged, &e.message);
        let _ = remove_dir_if_exists(&snap);
        return Err(e);
    }
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
        // IP-WS02-12 — G5 of the health tier contract ("Full Suite — adopt/update/release/full audit", Contract
        // v3:798): every governance check runs, fresh, against the updated installation, where a four-family subset
        // ran before (A0-O5-09: it applied over a defect only the full suite detects). An UNHEALTHY verdict or a RED
        // health state (an active hard-block) refuses the update, and the transaction below rolls it back. The run is
        // recorded in the health ledger with its tier and trigger; it writes no governed audit record, because the
        // update still writes its lock, ledger and checkpoint afterwards, so such a record would describe inputs the
        // transaction is about to change.
        let mut g5 = crate::scheduler::RunOptions::new(
            crate::scheduler::Tier::G5,
            crate::scheduler::Trigger::new("update.apply").with_subject(&target),
        );
        g5.surface = "tier:G5".into();
        g5.record = crate::scheduler::RecordPolicy::Never;
        let audit = crate::verification::audit_with(p, &g5)?;
        let suite_verdict = audit["verdict"].as_str().unwrap_or("UNHEALTHY");
        let health_state = audit["state"]
            .as_str()
            .or_else(|| audit["health_state"].as_str())
            .unwrap_or("");
        if suite_verdict == "UNHEALTHY"
            || health_state == "RED"
            || audit["counts"]["critical"].as_u64().unwrap_or(0) > 0
        {
            return Err(GovError::new(
                "VERIFICATION_FAILED",
                format!("the G5 full governance suite does not accept the updated installation (verdict {suite_verdict}, health {health_state})"),
            )
            .with_details(audit));
        }
        // Transaction step (9), SRR-R0-L5: the floors advance only after the atomic commit and its verification,
        // and only after the post-install governance suite has accepted the result.
        let protected = crate::srr::record_installed(&auth)?;
        Ok(
            json!({"migrations": chain.iter().map(|m| m["id"].clone()).collect::<Vec<_>>(), "operations": out.applied, "overlay_keys_changed": out.overlay_keys_changed, "overlay_reconciled": reconciled, "index_manifest": rebuilt, "doctor": doc.verdict, "audit": audit["verdict"], "lock": lock_identity_summary(p), "release_authenticity": auth.to_value(), "protected_state": protected}),
        )
    })();
    match result {
        Ok(v) => {
            let ledger = p.root.join("spec/reports/framework-updates.jsonl");
            let mut text = crate::util::read_text(&ledger).unwrap_or_default();
            let lk = lock_identity_summary(p);
            text.push_str(&serde_json::to_string(&json!({"at": now_iso(), "event": "update", "from": chk["current"], "to": target, "by": by, "session": p.session_id, "role": p.role, "result": "committed", "release_commit": lk["release_commit"], "source": lk["source"], "authenticity": lk["authenticity"], "details": v}))?);
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
            // The protected record that describes the pre-update bytes is put back FIRST (BC-P2-35/38): the abort
            // restores those bytes and then rebuilds and verifies against them, and post-install integrity must
            // measure the restored bytes against the record of them — not against the record of the aborted update,
            // which would make the restored kernel look rewritten and fail the abort itself.
            crate::srr::installation::restore_project_record(&p.root, prior_record.clone())?;
            crate::kernel_trust::clear();
            let rb = rollback_internal(
                p,
                Some(&target),
                Some(&format!("automatic: {} ({})", e.code, e.message)),
                true,
                false,
            )?;
            crate::kernel_trust::clear();
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
    // BC-P2-38 (failure atomicity): the verified kernel is committed FIRST. If that fails, the atomic transaction
    // has already put the previous tree back and nothing else has been touched yet, so the refused rollback leaves
    // the installation as it found it. The overlay, generated files and lock follow only once the kernel is in.
    match auth.as_ref() {
        // Verified bytes in, verified bytes installed, atomically.
        Some(a) => {
            crate::kernel::install_kernel(a, &p.governance_dir())?;
        }
        // Transaction abort: restore the tree the floors already describe (below).
        None => {}
    }
    for sub in ["project", "generated"] {
        let s = dir.join(sub);
        let d = p.governance_dir().join(sub);
        if s.exists() {
            remove_dir_if_exists(&d)?;
            copy_dir(&s, &d)?;
        }
    }
    if auth.is_none() {
        let s = dir.join("kernel");
        let d = p.governance_dir().join("kernel");
        if s.exists() {
            remove_dir_if_exists(&d)?;
            copy_dir(&s, &d)?;
        }
    }
    std::fs::copy(dir.join("framework.lock"), p.lock_path())?;
    crate::kernel_trust::clear();
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

/// `BC-P2-37` — the decision `check` took is bound to the release admission actually admitted.
///
/// `check` reads the candidate before admission stages it, so the candidate could change in between. Three facts the
/// decision rested on are re-established from the admitted release before a byte is installed:
/// * the version the impact check was taken for is the admitted version;
/// * if the Human Decision Gate was not required because the target is certified, the certification came from the
///   exact signed `release.json` admission verified (by its digest), and admission authenticated it;
/// * if the gate was not required, the admitted payload's own migrations still do not require one.
fn bind_decision_to_admitted(
    chk: &Value,
    auth: &crate::srr::AuthenticatedRelease,
    target: &str,
) -> Result<()> {
    if auth.release_version != target {
        return Err(GovError::new(
            "UPDATE_TARGET_CHANGED",
            format!("the impact check was taken for {target}, but admission admitted {}; re-run `gov update --check`", auth.release_version),
        ));
    }
    if chk["human_gate_required"].as_bool().unwrap_or(true) {
        return Ok(());
    }
    let bound_sha = chk["certification_basis"]["release_metadata_sha256"]
        .as_str()
        .unwrap_or("");
    if chk["certification"].as_str() != Some(CERTIFIED)
        || auth.authenticity != crate::srr::Authenticity::Authentic
        || bound_sha.is_empty()
        || auth.release_metadata_sha256 != bound_sha
    {
        return Err(GovError::new(
            "UPDATE_CERTIFICATION_NOT_BOUND",
            "the Human Decision Gate was waived for a certified target, but the admitted release is not the one whose signed metadata carried that certification; the gate is required",
        )
        .with_details(json!({"checked_release_metadata_sha256": bound_sha, "admitted_release_metadata_sha256": auth.release_metadata_sha256, "admitted_authenticity": auth.authenticity.as_str()})));
    }
    let migs = load_migrations(auth.verified_payload());
    let chain = migration_path(&migs, chk["current"].as_str().unwrap_or(""), target);
    let needs_gate = chain.iter().any(|m| {
        m["breaking"].as_bool().unwrap_or(false)
            || m["human_gate"]
                .as_str()
                .map(|g| g != "none")
                .unwrap_or(false)
    });
    if needs_gate {
        return Err(GovError::new(
            "UPDATE_GATE_CHANGED",
            "the admitted release's own migrations require a Human Decision Gate that the impact check did not; re-run `gov update --check`",
        ));
    }
    Ok(())
}

/// The identity the written `framework.lock` records (for results and the update ledger), rather than a
/// re-derivation from the source path.
fn lock_identity_summary(p: &Project) -> Value {
    let lock = read_yaml(&p.lock_path()).unwrap_or(Value::Null);
    json!({"release_commit": lock["release_commit"], "source": lock["source"], "authenticity": lock["authenticity"], "version": lock["version"]})
}

#[cfg(test)]
mod tests {
    use super::*;

    /// BC-P2-37: what counts as claiming certification (and so may be minted only through signed metadata).
    #[test]
    fn certification_claims_are_recognised_in_every_spelling() {
        for yes in ["CERTIFIED", "certified", " Certified ", "CERTIFIED_R2"] {
            assert!(claims_certification(yes), "{yes}");
        }
        for no in [
            "UNCERTIFIED",
            "READY_FOR_INDEPENDENT_OS_VERIFICATION",
            "REJECTED",
            "",
        ] {
            assert!(!claims_certification(no), "{no}");
        }
    }
}
