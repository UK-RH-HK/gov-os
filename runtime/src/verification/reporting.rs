//! The **reporting side** of checks other workstreams built (repair iteration 1, round 2, WS-2): every product check
//! that a round-1 repair exposed as an API is run by the governance suite at its tier and reported as named findings,
//! so it is owned by the health scheduler rather than run only on demand (repair-delta §0.2c).
//!
//! | family / hook | owner API | requirement |
//! |---|---|---|
//! | `lineage_orphans` | [`super::lineage`] over `graph::lineage` (WS-4) | W7 orphan and unexplained-output detection + remediation (BC-P2-22) |
//! | `graph_integrity` (+) | `graph::identity::misplaced_records`, `graph::lineage::stale_links` (WS-4), `dag.dangling_blocks` (WS-5) | W1 canonical path, W8 stale lineage links, `blocks` naming no task (ws04 IP-7, ws05 IP-2) |
//! | `product_traceability` (+) | `context::receipt::untraceable_closed_tasks` (WS-4) | W5 untraceable implementation reported by the audit (ws04 IP-8) |
//! | `context_reproducibility` (+) | `context::compile` + `context::verify_delivery` (WS-4) | W4/W12 G5 delivered inputs against the declared manifest, for every dispatchable task (ws04 IP-9) |
//! | `path_map_compliance` (+) | `qualification_oracle::is_hidden_oracle_material` (WS-1/12) | hidden-oracle material inside a governed repository (Contract v3:1014, :1062; ws01-12 IP-5) |
//! | `os_binding_integrity` | `t2::audit`, `gates::unverified` (WS-3), [`super::currency::unhonoured_health_outputs`] | T2 facts no OS operation produced (ws03 IP-5, ws02 IP-WS02-22) |
//! | `installation_authenticity` | `srr::installation::posture_of` (WS-8) | BC-P2-36: audit discloses an installation whose authenticity is not established (ws08 IP-2) |
//! | `contract_binding` | `contracts::verify` (WS-1) | BC-P2-01's check runs at G5 (ws01-12 IP-1) |
//! | `index_content_coverage` | `memory::coverage::verify` (WS-6) | BC-P2-25 whole-index content coverage at G1/G5 (ws06 IP-2) |
//! | `task_contract_integrity` | `orchestration::tasks::production_merge_findings` (WS-5) | experimental output detected in the production tree (ws05 IP-2) |
use super::Family;
use crate::memory::db::RuntimeDb;
use crate::records::RecordStore;
use crate::Project;
use serde_json::{json, Value};
use std::path::PathBuf;

fn finding(sev: &str, family: &str, msg: String, path: Option<String>) -> Value {
    json!({"severity": sev, "family": family, "message": msg, "path": path})
}

fn names(v: &[String], max: usize) -> String {
    let mut s = v.iter().take(max).cloned().collect::<Vec<_>>().join(", ");
    if v.len() > max {
        s.push_str(&format!(" (+{} more)", v.len() - max));
    }
    s
}

// ------------------------------------------------------------------------------------------- lineage_orphans

/// W7 (BC-P2-22): every orphan by name, and the baseline code not yet linked to an active specification as one
/// disclosure.
pub fn lineage_orphans(p: &Project, store: &RecordStore, db: Option<&RuntimeDb>, f: &mut Family) {
    let fam = f.id.clone();
    let report = super::lineage::detect(p, store, db);
    let investigations = super::lineage::investigations(store);
    for o in &report.orphans {
        let mut x = o.finding(&fam);
        if let Some((task, status)) = investigations.get(&o.key()) {
            x["orphan"]["remediation_task"] = json!({"task": task, "task_status": status});
        }
        f.findings.push(x);
    }
    if !report.baseline_unlinked.is_empty() {
        f.findings.push(finding(
            "low",
            &fam,
            format!(
                "{} source/test file(s) predate governance (governance baseline) and are not yet linked to an active requirement/decision/spec: {} (W7 baseline code; adopted as it was, not produced by governed work)",
                report.baseline_unlinked.len(),
                names(&report.baseline_unlinked, 10)
            ),
            None,
        ));
    }
    f.detail = report.detail;
}

// -------------------------------------------------------------------------------- graph_integrity additions

/// Misplaced records (W1 line 1072), stale lineage links (W8 line 1151) and `blocks` entries naming no task.
pub fn graph_lineage_findings(
    p: &Project,
    store: &RecordStore,
    dag: &crate::orchestration::dag::DagView,
    fam: &str,
) -> (Vec<Value>, Value) {
    let mut out = vec![];
    let misplaced = crate::graph::identity::misplaced_records(Some(p), store);
    for m in &misplaced {
        out.push(finding(
            "medium",
            fam,
            format!(
                "{} (W1 canonical path)",
                m["message"]
                    .as_str()
                    .unwrap_or("record outside its canonical location")
            ),
            m["path"].as_str().map(|s| s.to_string()),
        ));
    }
    let stale = current_stale_links(store);
    for s in &stale {
        out.push(finding(
            "medium",
            fam,
            format!(
                "stale lineage link: {} (W8 stale lineage link)",
                s["message"].as_str().unwrap_or("")
            ),
            s["path"].as_str().map(|x| x.to_string()),
        ));
    }
    for b in &dag.dangling_blocks {
        out.push(finding(
            "medium",
            fam,
            format!(
                "{} declares `blocks: {}`, which names no task",
                b["task"].as_str().unwrap_or("?"),
                b["blocks"]
            ),
            None,
        ));
    }
    (
        out,
        json!({"misplaced_records": misplaced.len(), "stale_links": stale.len(), "dangling_blocks": dag.dangling_blocks.len()}),
    )
}

/// `graph::lineage::stale_links` without the links of completed change transactions to the records they changed: a
/// COMMITTED (or rolled-back / rejected) CIT's `targets` are the subjects of the change itself — superseding D-0001
/// through a CIT is how currency is expressed, not a stale link from current work (WS-4 IP recorded in the report).
pub fn current_stale_links(store: &RecordStore) -> Vec<Value> {
    crate::graph::lineage::stale_links(store)
        .into_iter()
        .filter(|s| {
            let src = s["record"].as_str().unwrap_or("");
            !store
                .get(src)
                .map(|r| {
                    r.rtype() == "cit"
                        && matches!(
                            r.get("cit_status").as_str(),
                            "COMMITTED" | "ROLLED_BACK" | "REJECTED"
                        )
                })
                .unwrap_or(false)
        })
        .collect()
}

// ---------------------------------------------------------------------------- product_traceability additions

/// DONE tasks whose implementation does not trace (W5 line 1122; W8 missing lineage link).
///
/// Severity follows whether the close could have required the trace: a task closed under the consumption-receipt
/// contract (its closing report carries `receipt_validation`, `context::receipt::require_valid`) and still untraced
/// bypassed traceability — `medium`, health is not HEALTHY. A task closed before the receipt contract was enforced
/// (no `receipt_validation`: legacy or pre-receipt close) cannot be re-traced by any governed operation on a closed
/// task; it is disclosed (`low`) and its re-validation is governed work, not a permanent health failure.
pub fn untraceable_findings(p: &Project, store: &RecordStore, fam: &str) -> (Vec<Value>, Value) {
    let un = crate::context::receipt::untraceable_closed_tasks(p, store);
    let mut rows = vec![];
    let out = un
        .iter()
        .map(|u| {
            let under_contract = store
                .get(u["closed_by_report"].as_str().unwrap_or(""))
                .map(|r| r.data.get("receipt_validation").is_some())
                .unwrap_or(false);
            rows.push(json!({"task": u["task"], "closed_under_receipt_contract": under_contract}));
            finding(
                if under_contract { "medium" } else { "low" },
                fam,
                format!(
                    "untraced implementation: {} — what it produced has no lineage link to the requirements/scenarios it implements (W5 untraceable implementation; W8 missing lineage link){}",
                    u["message"].as_str().unwrap_or(""),
                    if under_contract { "" } else { "; closed before the consumption-receipt contract was enforced" }
                ),
                store
                    .get(u["task"].as_str().unwrap_or(""))
                    .map(|t| t.path.clone()),
            )
        })
        .collect();
    (out, json!(rows))
}

// ---------------------------------------------------------------------------- context_reproducibility additions

/// Task statuses whose context packet must be dispatchable (the task is offered or held as runnable work).
pub const DISPATCHABLE_STATUSES: &[&str] = &["READY", "CLAIMED", "IN_PROGRESS", "REVIEW"];

/// For every dispatchable task: compile its packet and verify the delivered inputs against the declared manifest
/// (`context::verify_delivery`). A dispatchable task whose packet is BLOCKED, or whose delivery does not verify, is
/// a finding naming the task and the inputs.
pub fn delivery_findings(
    p: &Project,
    db: &RuntimeDb,
    store: &RecordStore,
    fam: &str,
) -> (Vec<Value>, Value) {
    let mut out = vec![];
    let mut rows = vec![];
    for t in store.of_type("task") {
        let st = t.get("task_status");
        if !DISPATCHABLE_STATUSES.contains(&st.as_str()) {
            continue;
        }
        let id = t.id();
        let packet = match crate::context::compile(p, db, &id) {
            Ok(pk) => pk,
            Err(e) => {
                out.push(finding(
                    "high",
                    fam,
                    format!(
                        "{id} ({st}): its context packet cannot be compiled: [{}] {}",
                        e.code, e.message
                    ),
                    Some(t.path.clone()),
                ));
                continue;
            }
        };
        match crate::context::verify_delivery(p, &packet) {
            Ok(v) => {
                if packet["delivery_state"] != "COMPLETE" {
                    let missing: Vec<String> = v["missing_inputs_now"]
                        .as_array()
                        .map(|a| {
                            a.iter()
                                .map(|x| {
                                    x["id"]
                                        .as_str()
                                        .map(|s| s.to_string())
                                        .unwrap_or_else(|| x.to_string())
                                })
                                .collect()
                        })
                        .unwrap_or_default();
                    let viol: Vec<String> = v["input_violations_now"]
                        .as_array()
                        .map(|a| a.iter().map(|x| x.to_string()).collect())
                        .unwrap_or_default();
                    out.push(finding("medium", fam, format!("{id} is {st} but its context packet is BLOCKED: declared mandatory input(s) not delivered{}{} (W4 missing required input; `gov context manifest {id}`)", if missing.is_empty() { String::new() } else { format!(": missing input {}", names(&missing, 8)) }, if viol.is_empty() { String::new() } else { format!("; violations {}", names(&viol, 4)) }), Some(t.path.clone())));
                } else if !v["ok"].as_bool().unwrap_or(false) {
                    out.push(finding("high", fam, format!("{id} ({st}): the delivered inputs do not verify against its declared manifest (deterministic hash verified: {}, undelivered: {}, stale: {})", v["deterministic_hash_verified"], v["undelivered_inputs"], v["stale_inputs"]), Some(t.path.clone())));
                }
                rows.push(json!({"task": id, "task_status": st, "delivery_state": packet["delivery_state"], "declared_inputs": v["declared_inputs"], "ok": v["ok"]}));
            }
            Err(e) => out.push(finding(
                "high",
                fam,
                format!(
                    "{id} ({st}): delivery verification failed: [{}] {}",
                    e.code, e.message
                ),
                Some(t.path.clone()),
            )),
        }
    }
    (out, json!(rows))
}

// ---------------------------------------------------------------------------- path_map_compliance additions

/// Is this repository file hidden Qualification Oracle material (Contract v3:1014 verifier-owned hidden oracle,
/// :1062 kept separate from the qualification repository)?
pub fn hidden_oracle_material(abs: &std::path::Path) -> bool {
    if std::fs::metadata(abs)
        .map(|m| m.len() > 8 * 1024 * 1024)
        .unwrap_or(true)
    {
        return false;
    }
    let Ok(bytes) = std::fs::read(abs) else {
        return false;
    };
    let text = String::from_utf8_lossy(&bytes);
    let q = &crate::qualification_oracle::FORMAT;
    if !(text.contains(q)
        || crate::qualification_oracle::HIDDEN_ORACLE_RECORD_TYPES
            .iter()
            .any(|t| text.contains(t)))
    {
        return false;
    }
    let parsed: Option<Value> = if abs.extension().map(|e| e == "md").unwrap_or(false) {
        crate::records::parse_record_text(&text, "x.md").map(|r| r.data)
    } else {
        serde_yaml::from_str::<Value>(&text).ok()
    };
    parsed
        .map(|v| crate::qualification_oracle::is_hidden_oracle_material(&v))
        .unwrap_or(false)
}

// ------------------------------------------------------------------------------------ os_binding_integrity

/// T2 facts no OS operation produced (WS-3 IP-5) and health-system records the OS does not honour (IP-WS02-22).
pub fn os_binding_integrity(p: &Project, store: &RecordStore, f: &mut Family) {
    let fam = f.id.clone();
    let mut counts = std::collections::BTreeMap::<String, usize>::new();
    for r in crate::t2::audit(p) {
        let id = r["id"].as_str().unwrap_or("?").to_string();
        let path = r["path"].as_str().map(|s| s.to_string());
        let b = r["t2"]["binding"].as_str().unwrap_or("?").to_string();
        *counts.entry(b.clone()).or_insert(0) += 1;
        let rec = store.get(&id);
        let is_gate = rec.map(|x| x.rtype() == "human-gate").unwrap_or(false);
        let (sev, what) = t2_severity(&b, is_gate, rec.map(t2_in_force).unwrap_or(false), &r["t2"]);
        f.findings.push(finding(
            sev,
            &fam,
            format!(
                "{id} ({}) {what}; the OS does not honour it (D-0007 rule 2, T2 binding)",
                r["type"].as_str().unwrap_or("record")
            ),
            path,
        ));
    }
    let gates_unverified = crate::orchestration::gates::unverified(p).len();
    for h in super::currency::unhonoured_health_outputs(store) {
        let b = h["t2"]["binding"].as_str().unwrap_or("?").to_string();
        *counts.entry(format!("health-output:{b}")).or_insert(0) += 1;
        let sev = if b == "BROKEN" { "high" } else { "low" };
        f.findings.push(finding(
            sev,
            &fam,
            format!(
                "{} ({} record{}) is not honoured as health evidence: binding {b}{}",
                h["id"].as_str().unwrap_or("?"),
                h["scope"].as_str().unwrap_or(""),
                if h["green"].as_bool().unwrap_or(false) {
                    ", claims green"
                } else {
                    ""
                },
                if b == "BROKEN" {
                    " — modified after the health operation sealed it"
                } else {
                    " — not written by a gov health operation on this machine as it stands"
                }
            ),
            h["path"].as_str().map(|s| s.to_string()),
        ));
    }
    // the plugin registry (WS-7 seals every entry and the document; WS-2 R3-11): an entry the OS did not write as it
    // stands is not honoured (plugin_governance/D028 refuse its use); here it is reported as T2 state
    for (id, b) in plugin_registry_unbound(p) {
        let code = b["binding"].as_str().unwrap_or("?").to_string();
        *counts.entry(format!("plugin-registry:{code}")).or_insert(0) += 1;
        let sev = registry_severity(&code);
        let mut x = finding(
            sev,
            &fam,
            format!("plugin-registry entry {id} is not the registration gov wrote on this machine (binding {code}{}); it is not honoured (D-0007 rule 2)", b["reason"].as_str().map(|r| format!(": {r}")).unwrap_or_default()),
            Some(crate::capabilities::registry::path(p).strip_prefix(&p.root).map(|r| r.to_string_lossy().to_string()).unwrap_or_default()),
        );
        x["subjects"] = json!([id]);
        f.findings.push(x);
    }
    // CIT state (WS-4 `cit::binding`): a transaction whose sealed state does not verify is not honoured
    for c in crate::cit::bindings(p) {
        if c["state"]["binding"] == "VERIFIED" || c["cit_status"] == "PROPOSED" {
            continue;
        }
        let id = c["id"].as_str().unwrap_or("?").to_string();
        let st = c["cit_status"].as_str().unwrap_or("?").to_string();
        *counts
            .entry(format!(
                "cit:{}",
                c["state"]["code"].as_str().unwrap_or("UNBOUND")
            ))
            .or_insert(0) += 1;
        let in_force = matches!(st.as_str(), "APPROVED" | "EXECUTING");
        let mut x = finding(
            if in_force { "high" } else { "low" },
            &fam,
            format!(
                "{id} ({st}): its change-control state is not the state gov sealed ({}): {}; the OS does not honour it{}",
                c["state"]["code"].as_str().unwrap_or("UNBOUND"),
                c["state"]["message"].as_str().unwrap_or(""),
                if in_force { " and it is in force (an approval or execution relies on it)" } else { " (history)" }
            ),
            store.get(&id).map(|r| r.path.clone()),
        );
        x["subjects"] = json!([id]);
        f.findings.push(x);
    }
    // the adoption record (WS-9 IP-R2-4): stage order, authorship and verdicts are honoured only as gov wrote them
    if let Some((b, rel)) = adoption_baseline_binding(p) {
        let code = b.code().to_string();
        if code != "VERIFIED" {
            *counts
                .entry(format!("adoption-baseline:{code}"))
                .or_insert(0) += 1;
            let mut x = finding(
                if code == "BROKEN" { "high" } else { "low" },
                &fam,
                format!("the adoption record {rel} is not the record gov adopt wrote (binding {code}): its stage order, authorship and independent verdicts are not honoured (adoption integrity){}", if code == "BROKEN" { " — it was modified after gov sealed it; restore it from version control" } else { "" }),
                Some(rel.clone()),
            );
            x["subjects"] = json!([rel, crate::adopt::BASELINE_ID]);
            f.findings.push(x);
        }
    }
    f.detail = json!({"unverified_by_binding": counts, "gates_unverified": gates_unverified, "binding_key": crate::t2::binding_key_id()});
}

fn registry_severity(code: &str) -> &'static str {
    match code {
        "BROKEN" => "high",
        "UNSEALED" => "medium",
        _ => "low",
    }
}

/// Plugin-registry entries whose T2 binding does not verify, and the document binding when it does not (WS-7 API).
pub fn plugin_registry_unbound(p: &Project) -> Vec<(String, Value)> {
    let mut out: Vec<(String, Value)> = crate::capabilities::registry::unbound_entries(p)
        .into_iter()
        .map(|(id, b)| (id, b.to_value()))
        .collect();
    if crate::capabilities::registry::path(p).exists() {
        let d = crate::capabilities::registry::document_binding(p);
        if !d.is_verified() {
            out.push(("(registry document)".into(), d.to_value()));
        }
    }
    out.sort_by(|a, b| a.0.cmp(&b.0));
    out
}

/// The T2 binding of the adoption record `spec/audits/GOVERNANCE-ADOPTION/00-BASELINE.yaml`, when it exists.
pub fn adoption_baseline_binding(p: &Project) -> Option<(crate::t2::Binding, String)> {
    let rel = format!("{}/00-BASELINE.yaml", crate::adopt::EVIDENCE);
    let abs = p.root.join(&rel);
    if !abs.exists() {
        return None;
    }
    let b = match crate::util::read_yaml(&abs) {
        Ok(v) => crate::t2::verify_value(&v, ""),
        Err(e) => crate::t2::Binding::Broken {
            reason: format!("{rel} is unreadable: {e}"),
        },
    };
    Some((b, rel))
}

/// Is a T2 record in force as authority? A gate that is open or answered (its answer authorises work), or an ACTIVE
/// decision. REJECTED / SUPERSEDED decisions and revoked or closed gates are history.
pub fn t2_in_force(r: &crate::records::Record) -> bool {
    matches!(
        r.get("gate_status").as_str(),
        "PENDING" | "PRESENTED" | "ANSWERED"
    ) || (r.rtype() == "decision" && r.status() == "ACTIVE")
}

/// Severity of a T2 record the OS does not honour, and what to say about it:
/// * BROKEN (sealed here, then modified) — tampering with OS-written state: `high` while in force, `medium` as history;
/// * UNSEALED **gate** in force — gates are written only by gov (every gate write is sealed), so an unsealed one is a
///   hand-written (forged) gate or pre-T2 state: `medium`;
/// * UNSEALED decision — a legacy (pre-T2 / adopted) or hand-written approval claim the OS does not honour: `low`
///   (disclosed; its human approval is simply not honoured);
/// * FOREIGN / KEY_UNAVAILABLE — sealed by another machine (a clone): `low`.
pub fn t2_severity(
    binding: &str,
    is_gate: bool,
    in_force: bool,
    t2: &Value,
) -> (&'static str, String) {
    match binding {
        "BROKEN" => (
            if in_force { "high" } else { "medium" },
            format!(
                "was modified after the gov operation that wrote it sealed it ({}){} — restore it from version control",
                t2["reason"].as_str().unwrap_or(""),
                if in_force { " and is in force: tampered OS-written state" } else { "; it is history" }
            ),
        ),
        "UNSEALED" if is_gate && in_force => (
            "medium",
            "is an open or answered gate that no gov operation produced as it stands (UNSEALED: hand-written, forged, or written before the T2 primitive)".to_string(),
        ),
        "UNSEALED" if in_force => (
            "low",
            "claims human approval / gate derivation but no gov operation on this machine produced it (UNSEALED: legacy or hand-written); its approval is not honoured".to_string(),
        ),
        "UNSEALED" => ("low", "is history no gov operation on this machine produced (UNSEALED: legacy or hand-written)".to_string()),
        "FOREIGN" => ("low", "was sealed by another machine's binding key (a clone): not verifiable here".to_string()),
        other => ("low", format!("cannot be verified on this machine ({other})")),
    }
}

// ------------------------------------------------------------------------------- installation_authenticity

/// BC-P2-36 (audit side): an installation whose release authenticity is not established is disclosed. On a machine
/// with no trust anchor (bootstrap mode, OWNER-DECISION-P2-0002 item 2) the disclosure is `low` — governance
/// evidence is not a release-authenticity claim — and it is `medium` on a provisioned machine that cannot establish
/// it. Doctor (`D032`) fails in both cases, so the doctor verdict is never HEALTHY without it.
pub fn installation_authenticity(p: &Project, f: &mut Family) {
    let fam = f.id.clone();
    let pst = crate::srr::installation::posture_of(&p.root);
    if pst["installed"] == true && pst["authenticity_established"] != true {
        let sev = if pst["machine_posture"] == "UNPROVISIONED" {
            "low"
        } else {
            "medium"
        };
        f.findings.push(finding(
            sev,
            &fam,
            format!(
                "installation authenticity not established ({} machine; admission {}): {}",
                pst["machine_posture"].as_str().unwrap_or("?"),
                pst["admission"]["mode"]
                    .as_str()
                    .or_else(|| pst["admission"].as_str())
                    .unwrap_or("not recorded"),
                pst["disclosure"].as_str().unwrap_or("")
            ),
            Some("governance/framework.lock".into()),
        ));
    }
    f.detail = pst;
}

// ------------------------------------------------------------------------------------------ contract_binding

/// Where the owner-source contract chain lives: the audited repository itself when it carries it, else the
/// developer checkout named by `GOV_CANONICAL_ROOT`. `None` for a consumer project (the chain is the OS's).
pub fn contract_root(p: &Project) -> Option<PathBuf> {
    if p.root.join(crate::contracts::SOURCE_LOCK).exists() {
        return Some(p.root.clone());
    }
    crate::kernel::canonical_root().filter(|r| r.join(crate::contracts::SOURCE_LOCK).exists())
}

/// The files `contracts::verify` binds (for the cache key of `contract_binding`).
pub fn contract_files() -> [&'static str; 7] {
    [
        crate::contracts::OWNER_SOURCE,
        crate::contracts::CANONICAL_IMPORT,
        crate::contracts::COMPILED,
        crate::contracts::SOURCE_LOCK,
        crate::contracts::SCHEMA,
        crate::contracts::EVIDENCE_MAP,
        crate::contracts::GENERATED_VIEW,
    ]
}

/// BC-P2-01 at G5: `gov contract verify` over the contract chain; any `CONTRACT_*` divergence is HIGH.
pub fn contract_binding(p: &Project, f: &mut Family) {
    let fam = f.id.clone();
    match contract_root(p) {
        None => {
            f.detail = json!({"applicable": false, "reason": "the audited repository carries no owner-source contract chain and GOV_CANONICAL_ROOT names no OS checkout"});
        }
        Some(root) => match crate::contracts::verify(&root) {
            Ok(v) => {
                f.detail = json!({"applicable": true, "root": root.display().to_string(), "verdict": v["verdict"], "owner_source_sha256": v["owner_source_sha256"]});
            }
            Err(e) => {
                let diffs = e.details["differences"].clone();
                f.findings.push(finding(
                    "high",
                    &fam,
                    format!(
                        "contract binding broken: [{}] {} (BC-P2-01; `gov contract verify`)",
                        e.code, e.message
                    ),
                    None,
                ));
                f.detail = json!({"applicable": true, "root": root.display().to_string(), "code": e.code, "differences": diffs});
            }
        },
    }
}

// ------------------------------------------------------------------------------------ index_content_coverage

/// BC-P2-25 (WS-6 IP-2): every governed record's content and every non-empty line of indexed code is held by a chunk.
pub fn index_content_coverage(p: &Project, db: Option<&RuntimeDb>, f: &mut Family) {
    let fam = f.id.clone();
    let Some(db) = db else {
        f.findings.push(finding(
            "medium",
            &fam,
            "runtime DB missing; run gov rebuild-memory".into(),
            None,
        ));
        return;
    };
    match crate::memory::coverage::verify(p, db) {
        Ok(mut v) => {
            if !v["complete"].as_bool().unwrap_or(false) {
                let contract = p.contract();
                let mut confirmed: Vec<Value> = vec![];
                let mut artefacts: Vec<Value> = vec![];
                for g in v["gaps"].as_array().cloned().unwrap_or_default() {
                    if gap_is_heading_marker_artefact(p, db, &g) {
                        artefacts.push(g);
                    } else {
                        confirmed.push(g);
                    }
                }
                let listed: u64 = v["gaps"]
                    .as_array()
                    .map(|a| a.iter().map(|g| g["count"].as_u64().unwrap_or(0)).sum())
                    .unwrap_or(0);
                let unlisted = v["uncovered_lines"].as_u64().unwrap_or(0) > listed;
                let shown = |g: &Value| {
                    format!(
                        "{} ({} line(s))",
                        g["path"].as_str().unwrap_or("?"),
                        g["count"]
                    )
                };
                let historical = |g: &&Value| {
                    contract.decide(g["path"].as_str().unwrap_or("")).class() == "historical"
                };
                // a gap in current material (records, code, docs retrieved by default) degrades health; a gap only in
                // historical material (archive: excluded from default retrieval) is disclosed without degrading
                let current: Vec<String> = confirmed
                    .iter()
                    .filter(|g| !historical(g))
                    .map(shown)
                    .collect();
                let old: Vec<String> = confirmed.iter().filter(historical).map(shown).collect();
                if !current.is_empty() || unlisted {
                    f.findings.push(finding("medium", &fam, format!("index content coverage incomplete: indexed line(s) of current material held by no chunk: {}{} (BC-P2-25; rebuild the index: `gov rebuild-memory`; a gap that survives a full rebuild is a chunker defect)", names(&current, 6), if unlisted { " (more gaps beyond the listed ones)" } else { "" }), None));
                }
                if !old.is_empty() {
                    f.findings.push(finding("low", &fam, format!("index content coverage incomplete in historical (archived) material only: {} (BC-P2-25; excluded from default retrieval)", names(&old, 6)), None));
                }
                v["verifier_heading_marker_artefacts"] = json!(artefacts);
                v["confirmed_gaps"] = json!(confirmed.len());
            }
            f.detail = v;
        }
        Err(e) => f.findings.push(finding(
            "medium",
            &fam,
            format!(
                "index coverage could not be checked: [{}] {}",
                e.code, e.message
            ),
            None,
        )),
    }
}

/// `memory::coverage::verify` compares a Markdown heading line with its `#` markers removed against chunk lines, but a
/// chunk may hold the heading **with** its markers (e.g. consecutive heading lines with no body between them); such a
/// line is held, not missing (WS-6 integration point recorded in the report). A gap row is a verifier artefact when,
/// re-checking the artefact's whole current content the way the verifier does but with heading markers removed on
/// both sides, every non-empty line is held by one of its chunks. Anything else is a confirmed gap.
fn gap_is_heading_marker_artefact(p: &Project, db: &RuntimeDb, g: &Value) -> bool {
    let norm = |l: &str| -> String {
        let t = l.trim().trim_start_matches('#');
        t.split_whitespace().collect::<Vec<_>>().join(" ")
    };
    let aid = g["artifact_id"].as_str().unwrap_or("");
    let rel = g["path"].as_str().unwrap_or("");
    let Ok(text) = crate::util::read_text(&p.root.join(rel)) else {
        return false;
    };
    let is_record = db
        .query(
            "SELECT record_type FROM artifacts WHERE artifact_id=?1",
            &[&aid],
        )
        .ok()
        .and_then(|r| r.first().map(|x| x["record_type"].as_str() != Some("file")))
        .unwrap_or(false);
    let expected = crate::memory::coverage::expected_content(rel, &text, is_record);
    let chunks: Vec<String> = db
        .query("SELECT text FROM chunks WHERE artifact_id=?1", &[&aid])
        .unwrap_or_default()
        .iter()
        .map(|r| r["text"].as_str().unwrap_or("").to_string())
        .collect();
    if chunks.is_empty() {
        return false;
    }
    let held: std::collections::HashSet<String> = chunks
        .iter()
        .flat_map(|c| c.lines().map(norm).collect::<Vec<_>>())
        .collect();
    expected.lines().all(|l| {
        let n = norm(l);
        if n.is_empty() || held.contains(&n) {
            return true;
        }
        // a long line may be split across chunks: the verifier accepts it when a chunk holds its head
        let head: String = l.trim().chars().take(300).collect();
        l.trim().chars().count() > 600 && chunks.iter().any(|c| c.contains(&head))
    })
}

// ------------------------------------------------------------------------------------ task_contract_integrity

/// Experimental output that reached the production tree (Contract v3:614; ws05 IP-2).
pub fn task_contract_integrity(p: &Project, store: &RecordStore, f: &mut Family) {
    let fam = f.id.clone();
    let pm = crate::orchestration::tasks::production_merge_findings(p, store);
    for x in &pm {
        f.findings.push(finding(
            "high",
            &fam,
            format!(
                "production merge detected: {} (Contract v3:614 production merge prohibited where experimental)",
                x["message"].as_str().unwrap_or("")
            ),
            store
                .get(x["task"].as_str().unwrap_or(""))
                .map(|t| t.path.clone()),
        ));
    }
    f.detail = json!({"production_merge_violations": pm});
}

// ======================================================================= round 3 (WS-2): tier duties, Gate U

/// Is a record marked invalidated by an upstream change and not yet revalidated (`cit::propagation` markers)?
pub fn stale_marked(r: &crate::records::Record) -> bool {
    r.data["retest_required"] == true
        || r.data["revalidation_required"] == true
        || (r.data["staleness"].is_object()
            && r.data["staleness"]["stale"] != false
            && r.data["staleness"]["resolved"].is_null())
}

/// **G1/G4 dependency and lineage invalidation** (Contract v3:794 "index invalidation", W12 :1187 "G1 invalidates
/// affected dependency/lineage evidence after material mutations", :1190 "G4 runs wider staleness/impact
/// propagation", W6 :1134-1136; WS-4 R2-7 `propagation::detect`):
/// * an authoritative input changed since dependent work consumed it and the change was **not propagated** (made
///   outside change control, not yet detected by `gov cit propagate`) — medium, naming the task and the input;
/// * **completed work invalidated** by a propagated upstream change and not yet revalidated (a DONE task, or its
///   closing report, still carrying the staleness marker) — medium: its green evidence cannot stand merely because
///   it closed (W6 :1135-1136);
/// * open work marked for retest — disclosed (low): its close already requires evidence against the current inputs.
pub fn upstream_change_propagation(p: &Project, store: &RecordStore, f: &mut Family) {
    let fam = f.id.clone();
    let pending = crate::cit::propagation::detect(p, store);
    for (task, changes) in &pending {
        let ids: Vec<String> = changes.iter().map(|c| c.id.clone()).collect();
        let mut x = finding(
            "medium",
            &fam,
            format!(
                "{task} consumed {} which changed since (content hash {}); the upstream change has not been propagated to it — dependent evidence, packets and rework are not yet invalidated (W6; G1 dependency invalidation). Run `gov cit propagate`",
                ids.join(", "),
                changes
                    .iter()
                    .map(|c| format!("{}: {} → {}", c.id, c.from.as_deref().map(|h| &h[..h.len().min(12)]).unwrap_or("absent"), c.to.as_deref().map(|h| &h[..h.len().min(12)]).unwrap_or("absent")))
                    .collect::<Vec<_>>()
                    .join("; ")
            ),
            store.get(task).map(|t| t.path.clone()),
        );
        // the work that relied on the changed inputs is what this governs (its close); work consuming the inputs at
        // their current version is not affected
        x["subjects"] = json!([task]);
        x["changed_inputs"] = json!(ids);
        f.findings.push(x);
    }
    let mut invalidated_done = vec![];
    let mut retest_open = vec![];
    for t in store.of_type("task") {
        if t.get("task_status") == "CANCELLED" || !stale_marked(t) {
            continue;
        }
        let changed: Vec<String> = t.data["staleness"]["inputs_changed"]
            .as_array()
            .map(|a| {
                a.iter()
                    .filter_map(|c| {
                        c["id"]
                            .as_str()
                            .or_else(|| c.as_str())
                            .map(|s| s.to_string())
                    })
                    .collect()
            })
            .unwrap_or_default();
        if t.get("task_status") == "DONE" {
            invalidated_done.push(t.id());
            let mut x = finding(
                "medium",
                &fam,
                format!(
                    "{} is DONE but an upstream change invalidated it{}: its implementation/test evidence is stale until it is revalidated (W6 :1134-1136, `COMPLETE` does not imply permanently valid)",
                    t.id(),
                    if changed.is_empty() { String::new() } else { format!(" ({} changed)", changed.join(", ")) }
                ),
                Some(t.path.clone()),
            );
            let mut subj = vec![t.id(), t.get("closed_by_report")];
            subj.retain(|s| !s.is_empty());
            x["subjects"] = json!(subj);
            x["changed_inputs"] = json!(changed);
            f.findings.push(x);
        } else {
            retest_open.push(t.id());
            f.findings.push(finding(
                "low",
                &fam,
                format!(
                    "{} ({}) is marked for retest after an upstream change{}: its close requires evidence against the current inputs",
                    t.id(),
                    t.get("task_status"),
                    if changed.is_empty() { String::new() } else { format!(" ({} changed)", changed.join(", ")) }
                ),
                Some(t.path.clone()),
            ));
        }
    }
    let stale_reports: Vec<String> = store
        .of_type("report")
        .into_iter()
        .filter(|r| stale_marked(r))
        .map(|r| r.id())
        .collect();
    f.detail = json!({"unpropagated": pending.iter().map(|(t, cs)| json!({"task": t, "inputs": cs.iter().map(|c| json!({"id": c.id, "consumed": c.from, "current": c.to})).collect::<Vec<_>>()})).collect::<Vec<_>>(),
                      "invalidated_completed_tasks": invalidated_done, "retest_open_tasks": retest_open, "stale_reports": stale_reports});
}

/// **HEALTHY 1 / Gate U "unresolved contradictions"** (Contract v3:985, :996; W3 :1100; BC-P2-18 detection, WS-4 R2-7
/// `contradictions::detect_all`): every contradiction between current authoritative records that no honoured answer
/// resolved is named (medium; a held contradiction — the answer holds dependent work — is named too).
pub fn authority_unambiguous(p: &Project, store: &RecordStore, f: &mut Family) {
    let fam = f.id.clone();
    let all = crate::context::contradictions::detect_all(store);
    let mut rows = vec![];
    for c in &all {
        let r = crate::context::contradictions::resolution(p, store, c);
        rows.push(json!({"contradiction": c.to_value(), "resolution": r.to_value()}));
        if r.blocks() {
            let mut x = finding(
                "medium",
                &fam,
                format!(
                    "unresolved contradiction ({}) between {} on {}: {} (authority ambiguous; resolve it through the contradiction gate or a CIT)",
                    c.kind,
                    c.members.join(", "),
                    c.subject,
                    match &r {
                        crate::context::contradictions::Resolution::Unresolved { gate: Some(g) } => format!("awaiting gate {g}"),
                        crate::context::contradictions::Resolution::Unresolved { gate: None } => "no gate has been raised yet".to_string(),
                        crate::context::contradictions::Resolution::Held { gate, .. } => format!("held by the answer to {gate} until the records are revised"),
                        _ => String::new(),
                    }
                ),
                c.members
                    .first()
                    .and_then(|m| store.get(m))
                    .map(|r| r.path.clone()),
            );
            x["subjects"] = json!(c.members);
            f.findings.push(x);
        }
    }
    f.detail =
        json!({"contradictions": rows.len(), "unresolved": f.findings.len(), "detail": rows});
}

/// **HEALTHY 2 "no accidental legacy authority"** (Contract v3:997; INV-004): a legacy governance mechanism (provider
/// rules files, legacy agent instructions or memory) in the active tree without LEGACY registration is high — the
/// same rule doctor D013 applies, now owned by the suite as well.
pub fn legacy_authority(p: &Project, store: &RecordStore, f: &mut Family) {
    let fam = f.id.clone();
    let legacy = crate::migrations::classify::legacy_mechanisms(&p.root);
    let registered: Vec<String> = store
        .records
        .iter()
        .filter(|r| r.status() == "LEGACY" || r.rtype() == "legacy")
        .flat_map(|r| {
            let mut v = r.list("paths");
            v.push(r.get("legacy_source"));
            v.push(r.get("current_path"));
            v
        })
        .filter(|s| !s.is_empty())
        .collect();
    let mut unmarked = vec![];
    for l in &legacy {
        if l.path.starts_with("archive/") || registered.iter().any(|r| r == &l.path) {
            continue;
        }
        unmarked.push(l.path.clone());
        f.findings.push(finding(
            "high",
            &fam,
            format!(
                "legacy governance mechanism {} ({}) is in the active tree without LEGACY registration: it may be read as authority (INV-004; retire it through adoption A8 or register it LEGACY / move it to archive/)",
                l.path, l.kind
            ),
            Some(l.path.clone()),
        ));
    }
    f.detail = json!({"legacy_mechanisms": legacy.len(), "unmarked": unmarked});
}

/// **HEALTHY 7 "feature readiness explicit"** (Contract v3:1002; framework §76.7): every ACTIVE feature states its
/// readiness — a `readiness` block with at least one stated cell and no silent N/A or invalid cell
/// (`orchestration::readiness`). The coverage of what it states is the Gate U SLO `feature_readiness_coverage`.
pub fn feature_readiness(p: &Project, store: &RecordStore, f: &mut Family) {
    let fam = f.id.clone();
    let mut rows = vec![];
    for fe in store.of_type("feature") {
        if fe.status() != "ACTIVE" || fe.problems.iter().any(|x| x == "archived") {
            continue;
        }
        let stated = fe.data["readiness"]
            .as_object()
            .map(|m| m.len())
            .unwrap_or(0);
        let v = crate::orchestration::readiness::evaluate(p, fe);
        let problem = if fe
            .data
            .get("readiness")
            .map(|x| x.is_null())
            .unwrap_or(true)
        {
            Some("states no readiness at all".to_string())
        } else if stated == 0 {
            Some("states an empty readiness block (no dimension stated)".to_string())
        } else if !v.invalid.is_empty() {
            Some(format!(
                "has invalid or silent N/A readiness cells: {}",
                v.invalid.join("; ")
            ))
        } else {
            None
        };
        if let Some(why) = &problem {
            let mut x = finding(
                "medium",
                &fam,
                format!("feature {} {why}: its readiness status is not explicit (Contract v3:1002; `gov readiness check {}`)", fe.id(), fe.id()),
                Some(fe.path.clone()),
            );
            x["subjects"] = json!([fe.id()]);
            f.findings.push(x);
        }
        rows.push(json!({"feature": fe.id(), "stated_cells": stated, "coverage": v.coverage, "pre_implementation_ok": v.pre_implementation_ok, "gaps": v.gaps.len(), "explicit": problem.is_none()}));
    }
    f.detail = json!({"active_features": rows.len(), "features": rows});
}

/// Health-system output scopes are the suite's own results; every other audit record is an audit of record.
fn resolved_finding(x: &Value) -> bool {
    let st = x["status"]
        .as_str()
        .or_else(|| x["resolution_status"].as_str())
        .unwrap_or("")
        .to_ascii_uppercase();
    matches!(
        st.as_str(),
        "RESOLVED" | "CLOSED" | "FIXED" | "ACCEPTED" | "WAIVED" | "SUPERSEDED" | "WITHDRAWN"
    ) || x["resolved"] == true
        || !x["resolution"].is_null()
}

/// **HEALTHY 11 "no unresolved critical audit finding"** (Contract v3:1006): every current audit record other than
/// the suite's own results (independent full audits, imported audits, adoption audits) is read for critical findings
/// that are not resolved (`status: RESOLVED|CLOSED|…`, `resolved: true` or a `resolution`); each is high and refuses a
/// release. The suite's own critical findings are its current outcome (they count through the repository verdict).
pub fn unresolved_audit_findings(store: &RecordStore, f: &mut Family) {
    let fam = f.id.clone();
    let mut rows = vec![];
    for a in store.of_type("audit") {
        if super::currency::HEALTH_OUTPUT_SCOPES.contains(&a.get("scope").as_str())
            || a.problems.iter().any(|x| x == "archived")
            || !matches!(a.status().as_str(), "ACTIVE" | "PROVISIONAL" | "")
        {
            continue;
        }
        for x in a.data["findings"].as_array().cloned().unwrap_or_default() {
            if x["severity"]
                .as_str()
                .map(|s| s.eq_ignore_ascii_case("critical"))
                != Some(true)
                || resolved_finding(&x)
            {
                continue;
            }
            let fid = x["id"].as_str().unwrap_or("?").to_string();
            rows.push(json!({"audit": a.id(), "finding": fid, "scope": a.get("scope")}));
            let mut y = finding(
                "high",
                &fam,
                format!(
                    "{} ({}) records an unresolved critical finding {fid}: {} (Contract v3:1006; resolve it and record the resolution on the finding)",
                    a.id(),
                    a.get("scope"),
                    x["message"].as_str().or_else(|| x["title"].as_str()).unwrap_or("")
                ),
                Some(a.path.clone()),
            );
            y["subjects"] = json!([a.id()]);
            f.findings.push(y);
        }
    }
    f.detail = json!({"unresolved_critical": rows});
}

/// **J1/J2/H4 lifecycle findings at a G-tier** (WS-10 IP-WS10-06): `lifecycle::suite_findings` (research and
/// experiment evidence completeness, reliance on ungoverned evidence, influence backlinks, irreproducible
/// experiments, the scenario → data → test-data chain) and `lifecycle::experiment::task_merge_findings`
/// (experimental task output in the production tree), each at the severity its owner declares.
pub fn research_experiment_data_lifecycle(p: &Project, store: &RecordStore, f: &mut Family) {
    let fam = f.id.clone();
    let mut codes: std::collections::BTreeMap<String, usize> = std::collections::BTreeMap::new();
    let mut all = crate::lifecycle::suite_findings(p, store);
    all.extend(crate::lifecycle::experiment::task_merge_findings(p, store));
    for x in all {
        let code = x["code"].as_str().unwrap_or("LIFECYCLE").to_string();
        *codes.entry(code.clone()).or_insert(0) += 1;
        let mut y = finding(
            x["severity"].as_str().unwrap_or("medium"),
            &fam,
            format!("[{code}] {}", x["message"].as_str().unwrap_or("")),
            x["path"].as_str().map(|s| s.to_string()),
        );
        if let Some(r) = x["record"].as_str() {
            y["subjects"] = json!([r]);
        }
        f.findings.push(y);
    }
    f.detail = json!({"by_code": codes});
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::records::{parse_record_text, Record};
    use std::collections::BTreeMap;

    fn store(recs: &[(&str, &str)]) -> RecordStore {
        let records: Vec<Record> = recs
            .iter()
            .map(|(y, p)| parse_record_text(y, p).unwrap())
            .collect();
        let mut by_id = BTreeMap::new();
        for (i, r) in records.iter().enumerate() {
            by_id.insert(r.id(), i);
        }
        RecordStore {
            records,
            by_id,
            duplicates: vec![],
            problems: vec![],
        }
    }

    #[test]
    fn t2_severity_separates_tampering_forged_gates_and_legacy_claims() {
        let t2 = json!({"reason": "edited"});
        assert_eq!(t2_severity("BROKEN", true, true, &t2).0, "high");
        assert_eq!(t2_severity("BROKEN", false, false, &t2).0, "medium");
        assert_eq!(t2_severity("UNSEALED", true, true, &t2).0, "medium");
        assert_eq!(t2_severity("UNSEALED", false, true, &t2).0, "low");
        assert_eq!(t2_severity("UNSEALED", true, false, &t2).0, "low");
        assert_eq!(t2_severity("FOREIGN", true, true, &t2).0, "low");
        let s = store(&[
            (
                "id: HDG-0001\ntype: human-gate\nstatus: ACTIVE\ngate_status: ANSWERED\n",
                "spec/decisions/HDG-0001.yaml",
            ),
            (
                "id: HDG-0002\ntype: human-gate\nstatus: ACTIVE\ngate_status: REVOKED\n",
                "spec/decisions/HDG-0002.yaml",
            ),
            (
                "id: D-0001\ntype: decision\nstatus: REJECTED\n",
                "spec/decisions/D-0001.yaml",
            ),
            (
                "id: D-0002\ntype: decision\nstatus: ACTIVE\n",
                "spec/decisions/D-0002.yaml",
            ),
        ]);
        assert!(t2_in_force(s.get("HDG-0001").unwrap()));
        assert!(!t2_in_force(s.get("HDG-0002").unwrap()));
        assert!(!t2_in_force(s.get("D-0001").unwrap()));
        assert!(t2_in_force(s.get("D-0002").unwrap()));
    }

    #[test]
    fn a_coverage_gap_is_confirmed_unless_every_line_is_held_with_its_heading_markers() {
        let dir = std::env::temp_dir().join(format!("gov-cov-{}", crate::util::short_uuid()));
        std::fs::create_dir_all(&dir).unwrap();
        std::fs::write(dir.join("a.md"), "# no input change\n# second heading\n").unwrap();
        std::fs::write(
            dir.join("b.md"),
            "# held heading\nbody line no chunk holds\n",
        )
        .unwrap();
        let p = Project::open(&dir);
        let db = RuntimeDb::open_memory().unwrap();
        db.init_schema().unwrap();
        for (aid, text) in [
            ("file:a.md", "a.md\n# no input change\n# second heading"),
            ("file:b.md", "b.md\n# held heading"),
        ] {
            db.exec(
                "INSERT INTO artifacts(artifact_id, path, record_type, status) VALUES (?1, ?2, 'file', 'ACTIVE')",
                &[&aid, &aid.trim_start_matches("file:")],
            )
            .unwrap();
            db.exec(
                "INSERT INTO chunks(chunk_id, artifact_id, text) VALUES (?1, ?1, ?2)",
                &[&aid, &text],
            )
            .unwrap();
        }
        let a = json!({"artifact_id": "file:a.md", "path": "a.md", "count": 2, "lines": [{"line": 1, "text": "no input change"}]});
        assert!(gap_is_heading_marker_artefact(&p, &db, &a));
        let b = json!({"artifact_id": "file:b.md", "path": "b.md", "count": 1, "lines": [{"line": 2, "text": "body line no chunk holds"}]});
        assert!(!gap_is_heading_marker_artefact(&p, &db, &b));
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn a_completed_change_transaction_is_not_a_stale_link_to_what_it_changed() {
        let s = store(&[
            ("id: REQ-0001\ntype: requirement\nstatus: SUPERSEDED\nsuperseded_by: REQ-0002\n", "spec/requirements/REQ-0001.yaml"),
            ("id: REQ-0002\ntype: requirement\nstatus: ACTIVE\nsupersedes: [REQ-0001]\n", "spec/requirements/REQ-0002.yaml"),
            ("id: CIT-0001\ntype: cit\nstatus: ACTIVE\ncit_status: COMMITTED\ntargets: [REQ-0001]\n", "spec/decisions/CIT-0001.yaml"),
            ("id: CIT-0002\ntype: cit\nstatus: ACTIVE\ncit_status: PROPOSED\ntargets: [REQ-0001]\n", "spec/decisions/CIT-0002.yaml"),
            ("id: TASK-0001\ntype: task\nstatus: ACTIVE\ntask_status: DONE\nrequirements: [REQ-0001]\n", "spec/tasks/TASK-0001.yaml"),
        ]);
        let st: Vec<String> = current_stale_links(&s)
            .iter()
            .map(|x| x["record"].as_str().unwrap().to_string())
            .collect();
        assert!(st.contains(&"TASK-0001".to_string()), "{st:?}");
        assert!(st.contains(&"CIT-0002".to_string()), "{st:?}");
        assert!(!st.contains(&"CIT-0001".to_string()), "{st:?}");
    }
}
