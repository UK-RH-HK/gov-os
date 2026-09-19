//! Human Decision Gates (framework §50-54, HUMAN_GATE_POLICY). INV-008: a gate that exists only in a file is not
//! presented; answers are recorded only for presented gates, by a human or (within `agent_resolvable_when`) by an
//! L3+ agent.
//!
//! ## What this module guarantees (repair iteration 1, WS-3)
//!
//! * **Package (BC-P2-49).** A gate is raised only with substantive content for every
//!   `HUMAN_GATE_POLICY.decision_package_fields` entry and at least one option; nothing defaults to "not assessed".
//!   The exact permitted next actions are derived by the OS for *this* gate (no `<gate>` placeholders). An answer is
//!   always one of the offered options.
//! * **T2 binding (BC-P2-09).** Every gate and every decision this module writes is sealed ([`crate::t2`]); a gate
//!   or decision whose bytes are not what a gov operation wrote is never honoured (not answerable, not presentable,
//!   not an approval, not an authorisation for blocked work).
//! * **Human channel (BC-P2-10).** A human answer is an owner-signed document verified against the
//!   administrator-provisioned `human-gate` anchor ([`crate::human_channel`]); `--by`, `--role human`, `GOV_ROLE`,
//!   defaults and files cannot produce one. Only a signed answer or signed receipt marks a gate presented to the
//!   human; rendering to an agent's stdout does not.
//! * **Answer side of task blocking (BC-P2-12).** Blocked work becomes READY only on an *authorising* answer; a
//!   declining answer, a revocation or a withdrawal leaves / returns it BLOCKED; [`task_gate_authorisation`] is the
//!   single decision the DAG and task close must consult.
//! * **Agent resolution rules (BC-P2-18).** An agent may resolve only when impact radius, reversibility and
//!   confidence are *assessed* and within policy, with a recorded rationale, and when the assessment does not rest
//!   solely on the resolving session's own declaration.
use crate::authority;
use crate::human_channel;
use crate::orchestration::control;
use crate::records::{new_record, save_record, Record, RecordStore};
use crate::util::{canonical_json, now_iso, sha256_hex, today};
use crate::{GovError, Project, Result};
use serde_json::{json, Map, Value};

fn radius_rank(r: &str) -> u8 {
    r.strip_prefix('R')
        .and_then(|n| n.parse().ok())
        .unwrap_or(5)
}

fn valid_radius(r: &str) -> bool {
    r.len() == 2 && r.starts_with('R') && matches!(&r[1..], "0" | "1" | "2" | "3" | "4" | "5")
}

/// Who raised a gate, which decides where its assessment comes from.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Origin {
    /// `gov gate create` / an agent-invoked operation: the assessment is the raising session's declaration.
    Agent,
    /// Raised by the OS itself from values the OS computed (budget, update, migration, kernel, tool, plugin triggers).
    System,
}

/// Fields only the OS writes on a gate record; a caller supplying them is ignored (they are stripped).
const OS_OWNED_FIELDS: &[&str] = &[
    "gate_status",
    "presented_in_chat",
    "presented_at",
    "presented_by",
    "presentation",
    "presentation_receipt",
    "answer",
    "gate_instance",
    "raised_by",
    "assessment",
    "revoked",
    "priority_score",
    crate::t2::SEAL_FIELD,
];

/// Fields a gate may ask the human to approve as the scope of the resulting decision (`decision_scope`), copied into
/// the decision on an answer. They are inside the signed package digest.
pub const DECISION_SCOPE_FIELDS: &[&str] = &[
    "authorises_exceptions",
    "permits_policy_keys",
    "applies_to_project",
    "expires",
    "affects",
];

fn package_fields(p: &Project) -> Vec<String> {
    let f = p
        .policies()
        .get_list("HUMAN_GATE_POLICY", "decision_package_fields");
    if f.is_empty() {
        [
            "question",
            "why_now",
            "current_state",
            "options",
            "impact",
            "reversibility",
            "cost_rework",
            "recommendation",
            "confidence",
            "permitted_next_actions",
        ]
        .iter()
        .map(|s| s.to_string())
        .collect()
    } else {
        f
    }
}

/// Gate triggers that are human decisions by their nature (framework §51: governance/framework change, destructive
/// data action, security/privilege, spend and new executable capability): never agent-resolvable — refused when an
/// agent answers ([`answer`]) **and** refused when a consumer reads the answer ([`verified_answer_in`]), so a record
/// that claims an agent resolution of such a gate is not honoured even when its T2 seal verifies. This is the kernel
/// floor; `HUMAN_GATE_POLICY.human_only_triggers` may add to it (POLICY_PRECEDENCE `additive`), never remove from it.
///
/// Round 3: `upstream_export` (WS-9/11 r2 IP-R2-5 — an export of lessons out of the project is irreversible and is
/// already approved only by an owner-signed answer bound to the packet, `upstream::resolve_export_approval`) and
/// `experiment_promotion` (WS-10 r2 IP-WS10-15 — experimental output entering production; promotion already honours
/// only `human_approval_for`) join the floor, so an agent resolution of either is refused at answer time as well.
pub const HUMAN_ONLY_TRIGGERS: &[&str] = &[
    "framework_update",
    "destructive_migration",
    "privilege_elevation",
    "kernel_integrity_override",
    "tool_install",
    "budget_threshold",
    "upstream_export",
    "experiment_promotion",
];

/// Whether gates raised for `trigger` may only be answered by the human (see [`HUMAN_ONLY_TRIGGERS`]).
pub fn human_only_trigger(p: &Project, trigger: &str) -> bool {
    !trigger.is_empty()
        && (HUMAN_ONLY_TRIGGERS.contains(&trigger)
            || p.policies()
                .get_list("HUMAN_GATE_POLICY", "human_only_triggers")
                .iter()
                .any(|t| t == trigger))
}

fn non_substantive(p: &Project) -> Vec<String> {
    let mut v: Vec<String> = p
        .policies()
        .get_list("HUMAN_GATE_POLICY", "package_non_substantive_values")
        .into_iter()
        .map(|s| s.trim().to_lowercase())
        .collect();
    for d in ["", "not assessed"] {
        if !v.iter().any(|x| x == d) {
            v.push(d.into());
        }
    }
    v
}

fn substantive(v: &Value, placeholders: &[String]) -> bool {
    v.as_str()
        .map(|s| !placeholders.contains(&s.trim().to_lowercase()))
        .unwrap_or(false)
}

/// Complete a **system-raised** gate's package from the kernel policy's standard content for its trigger
/// (`HUMAN_GATE_POLICY.system_gate_package.<trigger>.<field>`), for fields the raising code did not supply. This is
/// framework-authored content for that decision class, not a placeholder; a field neither supplied nor defined for
/// the trigger stays missing and the gate is refused.
fn complete_system_package(p: &Project, o: &mut Map<String, Value>) {
    let trigger = o
        .get("trigger")
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .to_string();
    if trigger.is_empty() {
        return;
    }
    let placeholders = non_substantive(p);
    // a project installed from an older release may lack the table: this binary's embedded kernel supplies it
    let embedded: Value = crate::kernel::embedded::files()
        .iter()
        .find(|(r, _)| *r == "policies/HUMAN_GATE_POLICY.yaml")
        .and_then(|(_, b)| serde_yaml::from_slice(b).ok())
        .unwrap_or(Value::Null);
    for f in package_fields(p) {
        if f == "options" || f == "permitted_next_actions" || f == "confidence" {
            continue;
        }
        let present = o
            .get(&f)
            .map(|v| substantive(v, &placeholders))
            .unwrap_or(false);
        if !present {
            let key = format!("system_gate_package.{trigger}.{f}");
            if let Some(v) = p
                .policies()
                .get("HUMAN_GATE_POLICY", &key)
                .or_else(|| crate::util::deep_get(&embedded, &key).cloned())
            {
                o.insert(f, v);
            }
        }
    }
}

/// **BC-P2-49**: every package field substantive, at least one option, unique option ids, a numeric confidence.
fn validate_package(p: &Project, o: &mut Map<String, Value>, origin: Origin) -> Result<()> {
    let placeholders = non_substantive(p);
    let mut missing: Vec<String> = vec![];
    let mut invalid: Vec<String> = vec![];
    for f in package_fields(p) {
        match f.as_str() {
            "options" => {
                let opts = o
                    .get("options")
                    .and_then(|v| v.as_array())
                    .cloned()
                    .unwrap_or_default();
                if opts.is_empty() {
                    missing.push("options (at least one option the human can choose)".into());
                    continue;
                }
                let mut seen = std::collections::BTreeSet::new();
                for (i, opt) in opts.iter().enumerate() {
                    let id = opt
                        .get("id")
                        .and_then(|v| v.as_str())
                        .unwrap_or("")
                        .trim()
                        .to_string();
                    if id.is_empty() || id.contains(char::is_whitespace) {
                        invalid.push(format!("options[{i}].id must be a non-empty token"));
                    } else if !seen.insert(id.clone()) {
                        invalid.push(format!("options[{i}].id '{id}' is duplicated"));
                    }
                    if !opt
                        .get("description")
                        .map(|v| substantive(v, &placeholders))
                        .unwrap_or(false)
                    {
                        invalid.push(format!(
                            "options[{i}].description must say what the option does"
                        ));
                    }
                }
            }
            "confidence" => match o.get("confidence") {
                Some(Value::Number(n))
                    if n.as_f64()
                        .map(|c| (0.0..=1.0).contains(&c))
                        .unwrap_or(false) => {}
                Some(_) => invalid.push("confidence must be a number in [0, 1]".into()),
                None => missing
                    .push("confidence (an explicit assessment; it is never defaulted)".into()),
            },
            "permitted_next_actions" => {
                // derived by the OS for this exact gate; caller-supplied entries are checked below
                if let Some(extra) = o.get("permitted_next_actions") {
                    let bad: Vec<String> = extra
                        .as_array()
                        .cloned()
                        .unwrap_or_else(|| vec![extra.clone()])
                        .iter()
                        .filter(|a| {
                            a.as_str()
                                .map(|s| s.trim().is_empty() || s.contains('<') || s.contains('>'))
                                .unwrap_or(true)
                        })
                        .map(|a| a.to_string())
                        .collect();
                    if !bad.is_empty() {
                        if origin == Origin::Agent {
                            invalid.push(format!("permitted_next_actions must be exact actions for this gate; placeholders are not actions: {bad:?}"));
                        } else {
                            o.remove("permitted_next_actions");
                        }
                    }
                }
            }
            other => {
                if !o
                    .get(other)
                    .map(|v| substantive(v, &placeholders))
                    .unwrap_or(false)
                {
                    missing.push(other.to_string());
                }
            }
        }
    }
    if let Some(r) = o.get("impact_radius").and_then(|v| v.as_str()) {
        if !valid_radius(r) {
            invalid.push(format!("impact_radius '{r}' is not one of R0..R5"));
        }
    }
    if missing.is_empty() && invalid.is_empty() {
        return Ok(());
    }
    Err(GovError::new(
        "GATE_PACKAGE_INCOMPLETE",
        format!("a Human Decision Gate is raised only with a complete decision package (Contract v3 L2; HUMAN_GATE_POLICY.decision_package_fields). Missing: {missing:?}. Invalid: {invalid:?}. Supply them in --fields; nothing is defaulted to 'not assessed'."),
    )
    .with_details(json!({"missing": missing, "invalid": invalid, "required_fields": package_fields(p), "non_substantive_values": placeholders})))
}

/// Does choosing `option` authorise the work this gate blocks? Declared per option (`authorises_blocked_work`); an
/// option that does not declare it authorises only if its id is `A` (the product-wide approve convention).
fn option_authorises(options: &Value, option: &str) -> bool {
    options
        .as_array()
        .and_then(|a| a.iter().find(|o| o["id"].as_str() == Some(option)))
        .map(|o| {
            o.get("authorises_blocked_work")
                .and_then(|v| v.as_bool())
                .unwrap_or(option == "A")
        })
        .unwrap_or(false)
}

/// The exact permitted next actions for gate `id` (BC-P2-49): derived by the OS, one line per real action.
fn next_actions(id: &str, o: &Map<String, Value>) -> Vec<Value> {
    let mut v: Vec<Value> = vec![json!(format!(
        "gov gate present {id} — surface this package in the active human interface"
    ))];
    for opt in o
        .get("options")
        .and_then(|x| x.as_array())
        .cloned()
        .unwrap_or_default()
    {
        let oid = opt["id"].as_str().unwrap_or("");
        v.push(json!(format!(
            "gov decide {id} --option {oid} — record the owner-signed human answer choosing {oid} ({}) from the human channel",
            opt["description"].as_str().unwrap_or("")
        )));
    }
    let blocks: Vec<String> = o
        .get("blocks_tasks")
        .and_then(|x| x.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|t| t.as_str().map(String::from))
                .collect()
        })
        .unwrap_or_default();
    if !blocks.is_empty() {
        let auth: Vec<String> = o
            .get("options")
            .and_then(|x| x.as_array())
            .map(|a| {
                a.iter()
                    .filter(|x| {
                        x.get("authorises_blocked_work")
                            .and_then(|b| b.as_bool())
                            .unwrap_or(false)
                    })
                    .filter_map(|x| x["id"].as_str().map(String::from))
                    .collect()
            })
            .unwrap_or_default();
        v.push(json!(format!(
            "tasks {} stay blocked until an answer authorises them (authorising option(s): {})",
            blocks.join(", "),
            if auth.is_empty() {
                "none".to_string()
            } else {
                auth.join(", ")
            }
        )));
    }
    if let Some(c) = o
        .get("cit")
        .and_then(|x| x.as_str())
        .filter(|c| !c.is_empty())
    {
        v.push(json!(format!(
            "after an authorising answer: gov cit approve {c}, then gov cit execute {c}"
        )));
    }
    v.push(json!(format!(
        "gov gate revoke {id} — withdraw the question (L4)"
    )));
    v.push(json!(format!(
        "continue independent runnable work that {id} does not block"
    )));
    v
}

fn classify_reversibility(o: &Map<String, Value>) -> Option<bool> {
    if let Some(b) = o.get("reversible").and_then(|v| v.as_bool()) {
        return Some(b);
    }
    let t = o
        .get("reversibility")
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .trim()
        .to_lowercase();
    if t.is_empty() || t == "not assessed" || t == "unknown" {
        return None;
    }
    if t == "low"
        || [
            "irreversible",
            "not reversible",
            "cannot be undone",
            "can't be undone",
            "one-way",
            "permanent",
        ]
        .iter()
        .any(|w| t.contains(w))
    {
        return Some(false);
    }
    if [
        "reversible",
        "rollback",
        "roll back",
        "revert",
        "undo",
        "restore",
    ]
    .iter()
    .any(|w| t.contains(w))
    {
        return Some(true);
    }
    None
}

/// **The `OWNER-DECISION-0006` §6 bullet 2 (creation) sink.**
///
/// This is the only constructor of a `human-gate` record in the product, so every path that can raise a new Human
/// Gate — `gov gate create`, the system triggers in `update`, `kernel_trust`, `tasks`, `tools`, `adopt`,
/// `routing` and `capabilities`, and any path written after this code — passes through it.
///
/// The `&Clearance` parameter is not decoration: [`crate::srr::breakglass::Clearance`] has private fields and no
/// public constructor, so this function **cannot be called** without [`crate::srr::breakglass::guard_effect`]
/// having run and returned `Ok`. `AR29-B2` was `create_system` quietly saving a gate record with no guard; a guard
/// call added to `create_system` would have closed that one caller. A parameter the compiler demands closes the
/// class: a new gate-raising function inside this module does not compile until it has asked §6.
fn build(
    p: &Project,
    _clearance: &crate::srr::breakglass::Clearance,
    mut fields: Value,
    origin: Origin,
) -> Result<crate::records::Record> {
    let store = RecordStore::load(&p.root);
    if !fields.is_object() {
        return Err(GovError::new("USAGE", "gate fields must be an object"));
    }
    let chosen = fields
        .get("id")
        .and_then(|v| v.as_str())
        .map(|s| s.to_string());
    if let Some(c) = &chosen {
        if store.get(c).is_some() {
            return Err(GovError::new(
                "GATE_EXISTS",
                format!(
                    "{c} already exists; a gate id is never reused (answers and evidence bind it)"
                ),
            ));
        }
    }
    let id = chosen.unwrap_or_else(|| store.next_id("human-gate"));
    let question = fields
        .get("question")
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .to_string();
    if question.trim().is_empty() {
        return Err(GovError::new("USAGE", "a human gate needs a question"));
    }
    let o = fields.as_object_mut().unwrap();
    for k in OS_OWNED_FIELDS {
        o.remove(*k);
    }
    o.insert("gate_status".into(), json!("PENDING"));
    o.insert("presented_in_chat".into(), json!(false));
    o.entry("blocks_tasks").or_insert(json!([]));
    if origin == Origin::System {
        complete_system_package(p, o);
    }
    validate_package(p, o, origin)?;
    // options state explicitly whether choosing them authorises the blocked work (BC-P2-12)
    if let Some(opts) = o.get_mut("options").and_then(|v| v.as_array_mut()) {
        for opt in opts.iter_mut() {
            let oid = opt["id"].as_str().unwrap_or("").to_string();
            if opt
                .get("authorises_blocked_work")
                .and_then(|v| v.as_bool())
                .is_none()
            {
                opt["authorises_blocked_work"] = json!(oid == "A");
            }
        }
    }
    let extra: Vec<Value> = o
        .get("permitted_next_actions")
        .and_then(|v| v.as_array())
        .cloned()
        .unwrap_or_default();
    let mut actions = next_actions(&id, &*o);
    for a in extra {
        if !actions.contains(&a) {
            actions.push(a);
        }
    }
    o.insert("permitted_next_actions".into(), json!(actions));
    // BC-P2-18: the assessment agent resolution is judged on, and where it came from
    let radius = o
        .get("impact_radius")
        .and_then(|v| v.as_str())
        .filter(|r| valid_radius(r))
        .map(String::from);
    let reversible = classify_reversibility(o);
    let confidence = o.get("confidence").cloned().unwrap_or(Value::Null);
    o.insert(
        "assessment".into(),
        json!({
            "impact_radius": radius,
            "reversible": reversible,
            "confidence": confidence,
            "source": if origin == Origin::System { "os" } else { "declared" },
            "declared_by": {"session": p.session_id, "role": p.role},
        }),
    );
    o.insert(
        "raised_by".into(),
        json!({"kind": if origin == Origin::System { "system" } else { "agent" }, "session": p.session_id, "role": p.role, "at": now_iso()}),
    );
    o.insert(
        "gate_instance".into(),
        json!(uuid::Uuid::new_v4().simple().to_string()),
    );
    // HUMAN_GATE_POLICY.prioritisation: ordered criteria weighted by position
    let crit = p.policies().get_list("HUMAN_GATE_POLICY", "prioritisation");
    let weight = |name: &str| {
        crit.iter()
            .position(|c| c == name)
            .map(|i| (crit.len() - i) as f64)
            .unwrap_or(1.0)
    };
    let blocked = o
        .get("blocks_tasks")
        .and_then(|v| v.as_array())
        .map(|a| a.len())
        .unwrap_or(0) as f64;
    let radius = radius_rank(
        o.get("impact_radius")
            .and_then(|v| v.as_str())
            .unwrap_or("R1"),
    ) as f64;
    let irreversible = if reversible == Some(false) { 1.0 } else { 0.0 };
    let time_sensitive = if o
        .get("time_sensitive")
        .and_then(|v| v.as_bool())
        .unwrap_or(false)
    {
        1.0
    } else {
        0.0
    };
    o.insert(
        "priority_score".into(),
        json!(
            blocked * weight("tasks_blocked")
                + blocked * weight("critical_path_effect") * 0.5
                + radius * weight("impact_radius")
                + irreversible * weight("irreversibility") * 2.0
                + time_sensitive * weight("time_sensitivity")
        ),
    );
    o.remove("id");
    let title = o
        .get("title")
        .and_then(|v| v.as_str())
        .unwrap_or(&question)
        .to_string();
    o.remove("title");
    let rec = new_record("human-gate", &id, &title, Value::Object(o.clone()));
    p.schemas()
        .validate("human-gate", &rec.data, &format!("({id})"))?;
    Ok(rec)
}

/// Point the tasks a new gate blocks at it. A task record whose T2 seal verified before this write is re-sealed after
/// it (WS-5 r2 IP-R3-1, gates side): the OS keeps its own sealed records verifiable, and never blesses a record whose
/// seal did not verify ([`crate::t2::seal_if_verified`]).
fn block_tasks(p: &Project, rec: &crate::records::Record) -> Result<()> {
    let mut store2 = RecordStore::load(&p.root);
    for t in rec.data["blocks_tasks"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        if let Some(tr) = t.as_str().and_then(|s| store2.get_mut(s)) {
            let was_verified = crate::t2::verify_record(tr).is_verified();
            tr.set("human_gate", json!(rec.id()));
            if tr.get("task_status") != "DONE" {
                tr.set("task_status", json!("WAITING_HUMAN"));
            }
            crate::t2::seal_if_verified(tr, was_verified, "gate create (blocks task)")?;
            save_record(&p.root, tr)?;
        }
    }
    Ok(())
}

/// The research / experiment evidence a gate or an answer cites: `derived_from` and `evidence_refs` of `v`, plus
/// `extra` (an answer's `--evidence`), deduplicated in order.
fn cited_evidence_ids(v: &Value, extra: &[String]) -> Vec<String> {
    let mut out: Vec<String> = vec![];
    for k in ["derived_from", "evidence_refs"] {
        let items: Vec<String> = match v.get(k) {
            Some(Value::Array(a)) => a
                .iter()
                .filter_map(|x| x.as_str().map(String::from))
                .collect(),
            Some(Value::String(s)) if !s.is_empty() => vec![s.clone()],
            _ => vec![],
        };
        for i in items {
            if !out.contains(&i) {
                out.push(i);
            }
        }
    }
    for e in extra {
        if !out.contains(e) {
            out.push(e.clone());
        }
    }
    out
}

/// J1/J2 influence backlink (WS-10 r2 IP-WS10-02): the cited research/experiment records name `influenced`. The
/// record that cites them is already persisted, so a failure here is reported beside the result rather than
/// undoing it.
fn record_influence_reported(p: &Project, cited: &[String], influenced: &str) -> Value {
    if cited.is_empty() {
        return Value::Null;
    }
    match crate::lifecycle::record_influence(p, cited, influenced) {
        Ok(updated) => json!({"recorded": updated}),
        Err(e) => json!({"error": {"code": e.code, "message": e.message}}),
    }
}

/// Create a gate on behalf of an acting role (authority-checked). Its assessment is the acting session's
/// declaration (BC-P2-18 counts it as such).
pub fn create(p: &Project, fields: Value) -> Result<Value> {
    control::guard_write(p, "gate create")?;
    authority::require(p, "create_gate")?;
    let clearance = crate::srr::breakglass::guard_effect(
        crate::srr::breakglass::Effect::HumanGateCreate,
        "gate create",
    )?;
    // J1 (WS-10 r2 IP-WS10-02): a gate may rest only on governed research/experiment evidence
    let cited = cited_evidence_ids(&fields, &[]);
    if !cited.is_empty() {
        crate::lifecycle::require_citable(p, &RecordStore::load(&p.root), &cited)?;
    }
    let mut rec = build(p, &clearance, fields, Origin::Agent)?;
    crate::t2::seal_record(&mut rec, "gate create")?;
    save_record(&p.root, &rec)?;
    block_tasks(p, &rec)?;
    let influence = record_influence_reported(p, &cited, &rec.id());
    let mut out = rec.data;
    if !influence.is_null() {
        out["evidence_influence"] = influence;
    }
    Ok(out)
}

/// Create a gate raised by the system itself (budget/threshold/update/migration triggers) — not subject to the
/// acting role's authority, because the gate is the mechanism that stops the acting role.
///
/// It is **not** exempt from `OWNER-DECISION-0006` §6 bullet 2. Not being subject to the acting role's authority
/// is a statement about *who* may raise the gate; §6 is a statement about *whether a Human Gate may be created at
/// all* while the machine is marked `DEGRADED — RECOVERY ONLY`, and the answer is no, whoever is asking.
pub fn create_system(p: &Project, fields: Value) -> Result<Value> {
    let clearance = crate::srr::breakglass::guard_effect(
        crate::srr::breakglass::Effect::HumanGateCreate,
        "gate create (system)",
    )?;
    let mut rec = build(p, &clearance, fields, Origin::System)?;
    crate::t2::seal_record(&mut rec, "gate create (system)")?;
    save_record(&p.root, &rec)?;
    block_tasks(p, &rec)?;
    Ok(rec.data)
}

/// The canonical decision package of a gate record — the exact bytes the OS renders, writes to the human-channel
/// outbox, and whose SHA-256 an owner-signed answer or receipt must bind. Returns (package, sha256, bytes).
pub fn package_of(p: &Project, data: &Value) -> (Value, String, Vec<u8>) {
    let mut pkg = Map::new();
    for f in package_fields(p) {
        pkg.insert(f.clone(), data.get(&f).cloned().unwrap_or(Value::Null));
    }
    let doc = json!({
        "product": crate::FRAMEWORK_NAME,
        "gate": data["id"],
        "gate_instance": data["gate_instance"],
        "package": Value::Object(pkg),
        "context": {"blocks_tasks": data.get("blocks_tasks"), "cit": data.get("cit"), "impact_radius": data.get("impact_radius"), "trigger": data.get("trigger"), "subject": data.get("subject"), "decision_scope": data.get("decision_scope")},
    });
    let bytes = canonical_json(&doc).into_bytes();
    let digest = sha256_hex(&bytes);
    (doc, digest, bytes)
}

fn expected_for(p: &Project, data: &Value) -> human_channel::Expected {
    let (_, digest, _) = package_of(p, data);
    human_channel::Expected {
        gate: data["id"].as_str().unwrap_or("").to_string(),
        gate_instance: data["gate_instance"].as_str().unwrap_or("").to_string(),
        package_sha256: digest,
        options: data["options"]
            .as_array()
            .map(|a| {
                a.iter()
                    .filter_map(|o| o["id"].as_str().map(String::from))
                    .collect()
            })
            .unwrap_or_default(),
    }
}

/// `HUMAN_GATE_POLICY.human_channel.standalone_anchor_when_unprovisioned` (a kernel switch a project may only
/// tighten to `false`). P2-ADJ-0001: off unless the verified kernel explicitly turns it on — a kernel that predates
/// the key (the shipped 4.1.4/4.1.5) does not declare it, and its silence never enables a second authority domain.
pub fn standalone_anchor_allowed(p: &Project) -> bool {
    p.policies().get_bool(
        "HUMAN_GATE_POLICY",
        "human_channel.standalone_anchor_when_unprovisioned",
        false,
    )
}

fn render(p: &Project, d: &Value, digest: &str, outbox: Option<&std::path::Path>) -> String {
    let id = d["id"].as_str().unwrap_or("");
    let mut text = format!(
        "HUMAN DECISION GATE {id}\nQuestion: {}\nWhy now: {}\nCurrent state: {}\n",
        d["question"].as_str().unwrap_or(""),
        d["why_now"].as_str().unwrap_or("-"),
        d["current_state"].as_str().unwrap_or("-")
    );
    if let Some(opts) = d["options"].as_array() {
        text.push_str("Options:\n");
        for o in opts {
            text.push_str(&format!(
                "  [{}] {} {}\n",
                o["id"].as_str().unwrap_or("?"),
                o["description"].as_str().unwrap_or(""),
                o.get("impact")
                    .and_then(|v| v.as_str())
                    .map(|s| format!("(impact: {s})"))
                    .unwrap_or_default()
            ));
        }
    }
    text.push_str(&format!(
        "Impact: {}\nReversibility: {}\nCost/rework: {}\nRecommendation: {}\nConfidence: {}\nPermitted next actions:\n",
        d["impact"].as_str().unwrap_or("-"),
        d["reversibility"].as_str().unwrap_or("-"),
        d["cost_rework"].as_str().unwrap_or("-"),
        d["recommendation"].as_str().unwrap_or("-"),
        d["confidence"]
    ));
    for a in d["permitted_next_actions"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        text.push_str(&format!("  - {}\n", a.as_str().unwrap_or("")));
    }
    text.push_str(&format!(
        "Package SHA-256: {digest}\nGate instance: {}\nHuman answer: the product owner signs a `{}` document (role `{}`) binding this gate, instance and package digest and one option, and places it in {}{}\n",
        d["gate_instance"].as_str().unwrap_or(""),
        human_channel::ANSWER_TYPE,
        human_channel::ROLE,
        human_channel::inbox_dir().map(|x| x.display().to_string()).unwrap_or_default(),
        outbox.map(|o| format!(" (exact package bytes: {})", o.display())).unwrap_or_default()
    ));
    let _ = p;
    text
}

/// Render the decision package for the active interface and record that the OS rendered it.
///
/// Rendering is **not** presentation to the human: `presented_in_chat` stays `false` until an owner-signed receipt
/// ([`acknowledge`]) or an owner-signed answer binds this package's digest (BC-P2-10). The record keeps what the OS
/// rendered (`presentation.package_sha256`), which is what a later signed document must match.
pub fn present(p: &Project, id: &str) -> Result<(Value, String)> {
    authority::require(p, "present_gate")?;
    let mut store = RecordStore::load(&p.root);
    let g = store
        .get_mut(id)
        .ok_or_else(|| GovError::new("GATE_NOT_FOUND", format!("{id} not found")))?;
    if g.rtype() != "human-gate" {
        return Err(GovError::new("USAGE", format!("{id} is not a human gate")));
    }
    crate::t2::require_verified(g, "a gate that can be presented")?;
    if !matches!(g.get("gate_status").as_str(), "PENDING" | "PRESENTED") {
        return Err(GovError::new(
            "USAGE",
            format!(
                "{id} is {}; only an open gate can be presented",
                g.get("gate_status")
            ),
        ));
    }
    let (_, digest, bytes) = package_of(p, &g.data);
    if g.get("gate_status") == "PENDING" {
        g.set("gate_status", json!("PRESENTED"));
    }
    g.set("presented_at", json!(now_iso()));
    g.set(
        "presented_by",
        json!({"session": p.session_id, "role": p.role}),
    );
    g.set(
        "presentation",
        json!({"rendered_at": now_iso(), "rendered_by": {"session": p.session_id, "role": p.role}, "package_sha256": digest,
               "note": "rendered by the OS to the invoking interface; this is not a human receipt (presented_in_chat is set only by an owner-signed receipt or answer)"}),
    );
    crate::t2::seal_record(g, "gate present")?;
    save_record(&p.root, g)?;
    let instance = g.get("gate_instance");
    let outbox = human_channel::write_outbox(id, &instance, &bytes).ok();
    let mut d = g.data.clone();
    let text = render(p, &d, &digest, outbox.as_deref());
    d["package_sha256"] = json!(digest);
    d["human_channel"] = json!({"inbox": human_channel::inbox_dir().ok().map(|x| x.display().to_string()), "outbox_file": outbox.map(|x| x.display().to_string()), "answer_type": human_channel::ANSWER_TYPE, "receipt_type": human_channel::RECEIPT_TYPE});
    Ok((d, text))
}

fn rendered_digest_matches(p: &Project, g: &Record) -> Option<String> {
    let (_, digest, _) = package_of(p, &g.data);
    let rendered = g.data["presentation"]["package_sha256"]
        .as_str()
        .unwrap_or("");
    if g.get("gate_status") == "PRESENTED" && rendered == digest {
        Some(digest)
    } else {
        None
    }
}

/// Apply an owner-signed **presentation receipt**: the human acknowledges that the exact rendered package reached
/// them. This, or a signed answer, is the only thing that sets `presented_in_chat`.
pub fn acknowledge(p: &Project, id: &str, receipt_file: Option<&std::path::Path>) -> Result<Value> {
    authority::require(p, "present_gate")?;
    let mut store = RecordStore::load(&p.root);
    let g = store
        .get_mut(id)
        .ok_or_else(|| GovError::new("GATE_NOT_FOUND", format!("{id} not found")))?;
    if g.rtype() != "human-gate" {
        return Err(GovError::new("USAGE", format!("{id} is not a human gate")));
    }
    crate::t2::require_verified(g, "a gate presentation receipt")?;
    if rendered_digest_matches(p, g).is_none() {
        return Err(GovError::new("GATE_NOT_PRESENTED", format!("{id} has not been rendered by the OS in its current form; run `gov gate present {id}` first")));
    }
    let anchor = human_channel::anchor(standalone_anchor_allowed(p))?;
    let exp = expected_for(p, &g.data);
    let s = human_channel::find(&anchor, human_channel::RECEIPT_TYPE, &exp, receipt_file)?;
    g.set("presented_in_chat", json!(true));
    g.set(
        "presentation_receipt",
        json!({"kind": "receipt", "acknowledged_by": s.by, "package_sha256": exp.package_sha256, "evidence": s.evidence()}),
    );
    crate::t2::seal_record(g, "gate acknowledge")?;
    save_record(&p.root, g)?;
    human_channel::consume(&s, id)?;
    Ok(
        json!({"gate": id, "presented_in_chat": true, "acknowledged_by": s.by, "signed_by_key_ids": s.key_ids}),
    )
}

/// Open gates the OS honours (T2-verified), highest priority first.
pub fn pending(p: &Project) -> Vec<Value> {
    let store = RecordStore::load(&p.root);
    let batch_low = p
        .policies()
        .get_bool("HUMAN_GATE_POLICY", "batch_low_priority", true);
    let mut v: Vec<Value> = store
        .of_type("human-gate")
        .into_iter()
        .filter(|g| matches!(g.get("gate_status").as_str(), "PENDING" | "PRESENTED"))
        .filter(|g| crate::t2::verify_record(g).is_verified())
        .map(|g| {
            let score = g.data.get("priority_score").and_then(|v| v.as_f64()).unwrap_or(0.0);
            json!({"id": g.id(), "question": g.get("question"), "gate_status": g.get("gate_status"),
                   "rendered": g.data.get("presentation").map(|x| !x.is_null()).unwrap_or(false),
                   "presented_in_chat": g.data.get("presented_in_chat").and_then(|v| v.as_bool()).unwrap_or(false),
                   "priority_score": score, "batchable": batch_low && score < 3.0, "blocks_tasks": g.list("blocks_tasks"), "cit": g.get("cit"), "trigger": g.get("trigger")})
        })
        .collect();
    v.sort_by(|a, b| {
        b["priority_score"]
            .as_f64()
            .partial_cmp(&a["priority_score"].as_f64())
            .unwrap_or(std::cmp::Ordering::Equal)
    });
    v
}

/// Gate records in an open status that the OS does **not** honour, because no gov operation produced them as they
/// stand (T2 binding not verified). For `gov gate list`, doctor and the suite.
pub fn unverified(p: &Project) -> Vec<Value> {
    let store = RecordStore::load(&p.root);
    store
        .of_type("human-gate")
        .into_iter()
        .filter_map(|g| {
            let b = crate::t2::verify_record(g);
            (!b.is_verified()).then(|| json!({"id": g.id(), "gate_status": g.get("gate_status"), "honoured": false, "path": g.path, "t2": b.to_value()}))
        })
        .collect()
}

/// `gov gate show`: the record, whether the OS honours it (T2), what it authorises for blocked work, and whether its
/// answer verifies — the operator's view of exactly what the consumers below will decide.
pub fn inspect(p: &Project, id: &str) -> Result<Value> {
    let store = RecordStore::load(&p.root);
    let g = store
        .get(id)
        .filter(|g| g.rtype() == "human-gate")
        .ok_or_else(|| {
            GovError::new("GATE_NOT_FOUND", format!("{id} is not a human gate record"))
        })?;
    let answer = match verified_answer_in(p, &store, id) {
        Ok(a) => {
            let mut v = a.to_value();
            v["verified"] = json!(true);
            v
        }
        Err(e) => json!({"verified": false, "code": e.code, "message": e.message}),
    };
    Ok(json!({
        "gate": g.data,
        "t2": crate::t2::verify_record(g).to_value(),
        "authorisation": task_gate_authorisation_in(p, &store, id).to_value(),
        "answer": answer,
        "package_sha256": package_of(p, &g.data).1,
    }))
}

// ------------------------------------------------------------------------------------ honouring an answer

/// A gate answer the OS honours: T2-bound, answered, and (for a human answer) re-verified against the owner's key.
#[derive(Debug, Clone)]
pub struct VerifiedAnswer {
    pub gate: String,
    pub option: String,
    /// `human` (owner-signed) or `agent` (resolved within policy).
    pub by_kind: String,
    pub answered_by: String,
    pub decision: Option<String>,
    pub authorises_blocked_work: bool,
    pub human_evidence: Option<Value>,
    pub record: Record,
}

impl VerifiedAnswer {
    pub fn to_value(&self) -> Value {
        json!({"gate": self.gate, "option": self.option, "by_kind": self.by_kind, "answered_by": self.answered_by, "decision": self.decision, "authorises_blocked_work": self.authorises_blocked_work, "human_evidence": self.human_evidence.as_ref().map(|e| json!({"signed_by_key_ids": e["signed_by_key_ids"], "anchor": e["anchor"], "envelope_sha256": e["envelope_sha256"]}))})
    }
}

/// **The consumer API for a recorded answer (BC-P2-09/10).** CIT approval/execution, update, adoption, plugin
/// registration and every other consumer must honour a gate answer only through this function (or
/// [`is_answered_yes`] / [`answered_option`], which call it). It refuses, typed:
/// `GATE_NOT_FOUND`, `GATE_MISMATCH`, `T2_UNBOUND` (record not written by a gov operation as it stands),
/// `GATE_NOT_ANSWERED`, `GATE_REVOKED`, `GATE_STATE_INVALID`, `HUMAN_ANSWER_UNVERIFIED`.
pub fn verified_answer(p: &Project, gate_id: &str) -> Result<VerifiedAnswer> {
    let store = RecordStore::load(&p.root);
    verified_answer_in(p, &store, gate_id)
}

pub fn verified_answer_in(
    p: &Project,
    store: &RecordStore,
    gate_id: &str,
) -> Result<VerifiedAnswer> {
    let g = store.get(gate_id).ok_or_else(|| {
        GovError::new(
            "GATE_NOT_FOUND",
            format!("human gate {gate_id} does not exist"),
        )
    })?;
    if g.rtype() != "human-gate" {
        return Err(GovError::new(
            "GATE_MISMATCH",
            format!("{gate_id} is not a human gate"),
        ));
    }
    crate::t2::require_verified(g, "a recorded Human Decision Gate answer")?;
    match g.get("gate_status").as_str() {
        "ANSWERED" => {}
        "PENDING" | "PRESENTED" => {
            return Err(GovError::new(
                "GATE_NOT_ANSWERED",
                format!("human gate {gate_id} has no recorded answer"),
            ));
        }
        other => {
            return Err(GovError::new("GATE_REVOKED", format!("human gate {gate_id} is {other}")).with_details(json!({"gate": gate_id, "gate_status": other, "revoked": g.data.get("revoked")})));
        }
    }
    let answer = g.data.get("answer").cloned().unwrap_or(Value::Null);
    let option = answer["option"].as_str().unwrap_or("").to_string();
    let offered: Vec<String> = g.data["options"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|o| o["id"].as_str().map(String::from))
                .collect()
        })
        .unwrap_or_default();
    if !offered.contains(&option) {
        return Err(GovError::new(
            "GATE_STATE_INVALID",
            format!("human gate {gate_id} records answer '{option}', which it does not offer"),
        ));
    }
    let kind = answer["by_kind"].as_str().unwrap_or("").to_string();
    let mut human_evidence = None;
    match kind.as_str() {
        "human" => {
            let anchor = human_channel::anchor(standalone_anchor_allowed(p)).map_err(|e| {
                GovError::new(
                    "HUMAN_ANSWER_UNVERIFIED",
                    format!(
                        "the human answer on {gate_id} cannot be re-verified: {}",
                        e.message
                    ),
                )
                .with_details(e.details)
            })?;
            let exp = expected_for(p, &g.data);
            human_channel::reverify(
                &anchor,
                &answer["human_channel"],
                human_channel::ANSWER_TYPE,
                &exp,
                Some(&option),
            )?;
            if !g
                .data
                .get("presented_in_chat")
                .and_then(|v| v.as_bool())
                .unwrap_or(false)
                || g.data["presentation_receipt"]["kind"].as_str() == Some("agent_resolution")
            {
                return Err(GovError::new(
                    "GATE_STATE_INVALID",
                    format!("human gate {gate_id} is answered but carries no presentation receipt"),
                ));
            }
            human_evidence = Some(answer["human_channel"].clone());
        }
        "agent" => {
            if answer
                .get("agent_resolution")
                .map(|v| v.is_null())
                .unwrap_or(true)
            {
                return Err(GovError::new("GATE_STATE_INVALID", format!("human gate {gate_id} records an agent answer without its resolution record")));
            }
            // use-time rule, independent of the seal: a human-only gate is never honoured on an agent's answer
            let trigger = g.get("trigger");
            if human_only_trigger(p, &trigger) {
                return Err(GovError::new("GATE_STATE_INVALID", format!("human gate {gate_id} (trigger '{trigger}') records an agent resolution, but gates raised for '{trigger}' are human decisions (framework §51); only an owner-signed human answer is honoured")).with_details(json!({"gate": gate_id, "trigger": trigger, "rule": "HUMAN_GATE_POLICY.human_only_triggers"})));
            }
        }
        other => {
            return Err(GovError::new(
                "GATE_STATE_INVALID",
                format!("human gate {gate_id} records an answer of unknown kind '{other}'"),
            ));
        }
    }
    let decision = store
        .of_type("decision")
        .into_iter()
        .filter(|d| d.list("derived_from").iter().any(|x| x == gate_id))
        .find(|d| crate::t2::verify_record(d).is_verified());
    if let Some(d) = decision {
        if d.status() != "ACTIVE" {
            return Err(GovError::new(
                "GATE_REVOKED",
                format!(
                    "decision {} for gate {gate_id} is {}; it no longer authorises anything",
                    d.id(),
                    d.status()
                ),
            ));
        }
    }
    Ok(VerifiedAnswer {
        gate: gate_id.to_string(),
        authorises_blocked_work: option_authorises(&g.data["options"], &option),
        option,
        by_kind: kind,
        answered_by: answer["by"].as_str().unwrap_or("").to_string(),
        decision: decision.map(|d| d.id()),
        human_evidence,
        record: g.clone(),
    })
}

/// **Consumer precheck (BC-P2-09)** for a consumer that reads a gate answer itself and has not yet adopted
/// [`verified_answer`] (CIT approval/execution, framework update): refuse when the answer it would read is not what
/// gov wrote or no longer verifies. Ordinary states (not answered, withdrawn, declined, missing) pass, so the
/// consumer still reports its own typed refusal for them.
pub fn require_honoured_answers(p: &Project, gate_ids: &[String]) -> Result<()> {
    let store = RecordStore::load(&p.root);
    for gid in gate_ids.iter().filter(|g| !g.is_empty()) {
        if let Err(e) = verified_answer_in(p, &store, gid) {
            if matches!(
                e.code.as_str(),
                "T2_UNBOUND" | "HUMAN_ANSWER_UNVERIFIED" | "GATE_STATE_INVALID"
            ) {
                return Err(e);
            }
        }
    }
    Ok(())
}

/// Every gate raised for `trigger` that records an answer (for consumers that select a gate by trigger).
pub fn answered_gates_for_trigger(p: &Project, trigger: &str) -> Vec<String> {
    RecordStore::load(&p.root)
        .of_type("human-gate")
        .into_iter()
        .filter(|g| g.get("trigger") == trigger && g.get("gate_status") == "ANSWERED")
        .map(|g| g.id())
        .collect()
}

/// The recorded, verified answer of a gate (`Some(option)`), or `None` while it is pending, never presented,
/// withdrawn, or not verifiable (T2 / human channel).
pub fn answered_option(p: &Project, gate_id: &str) -> Option<String> {
    verified_answer(p, gate_id).ok().map(|a| a.option)
}

/// A verified answer choosing option `A`.
pub fn is_answered_yes(p: &Project, gate_id: &str) -> bool {
    verified_answer(p, gate_id)
        .map(|a| a.option == "A")
        .unwrap_or(false)
}

/// **Human approval bound to a subject** (for consumers that must record "approved by a human": upstream export,
/// retrieval-profile selection, plugin registration, framework update). Succeeds only for a verified,
/// owner-signed, authorising answer on a gate whose `subject.sha256` equals `subject_sha256`.
pub fn human_approval_for(
    p: &Project,
    gate_id: &str,
    subject_sha256: &str,
) -> Result<VerifiedAnswer> {
    let a = verified_answer(p, gate_id)?;
    if a.by_kind != "human" {
        return Err(GovError::new("HUMAN_APPROVAL_REQUIRED", format!("gate {gate_id} was resolved by an agent; this action requires an owner-signed human answer")));
    }
    if !a.authorises_blocked_work {
        return Err(GovError::new(
            "GATE_DECLINED",
            format!(
                "gate {gate_id} was answered '{}', which does not authorise the action",
                a.option
            ),
        ));
    }
    let bound = a.record.data["subject"]["sha256"].as_str().unwrap_or("");
    if bound != subject_sha256 {
        return Err(GovError::new(
            "APPROVAL_STALE",
            format!("gate {gate_id} approved subject sha256 '{bound}', not '{subject_sha256}'"),
        ));
    }
    Ok(a)
}

/// What a task's human gate says about running the blocked work — **the single decision** the DAG (runnable set,
/// replan) and task close must consult (BC-P2-12, DAG side in WS-5).
#[derive(Debug, Clone, PartialEq)]
pub enum GateAuthorisation {
    Authorised { option: String, by_kind: String },
    Pending { presented: bool },
    Declined { option: String },
    Withdrawn,
    Missing,
    Unverified { reason: Value },
}

impl GateAuthorisation {
    pub fn authorises(&self) -> bool {
        matches!(self, GateAuthorisation::Authorised { .. })
    }
    /// Why the work is not runnable, or `None` when it is authorised.
    pub fn blocking_reason(&self, gate: &str) -> Option<String> {
        match self {
            GateAuthorisation::Authorised { .. } => None,
            GateAuthorisation::Pending { .. } => Some(format!("waiting on human gate {gate}")),
            GateAuthorisation::Declined { option } => Some(format!("human gate {gate} was answered '{option}', which does not authorise this work")),
            GateAuthorisation::Withdrawn => Some(format!("human gate {gate} was withdrawn/revoked: its authorisation no longer exists")),
            GateAuthorisation::Missing => Some(format!("human gate {gate} does not exist: a reference to a missing gate blocks")),
            GateAuthorisation::Unverified { .. } => Some(format!("human gate {gate} is not an OS-written record as it stands (T2) or its answer does not verify")),
        }
    }
    pub fn to_value(&self) -> Value {
        match self {
            GateAuthorisation::Authorised { option, by_kind } => {
                json!({"state": "AUTHORISED", "option": option, "by_kind": by_kind})
            }
            GateAuthorisation::Pending { presented } => {
                json!({"state": "PENDING", "presented_in_chat": presented})
            }
            GateAuthorisation::Declined { option } => {
                json!({"state": "DECLINED", "option": option})
            }
            GateAuthorisation::Withdrawn => json!({"state": "WITHDRAWN"}),
            GateAuthorisation::Missing => json!({"state": "MISSING"}),
            GateAuthorisation::Unverified { reason } => {
                json!({"state": "UNVERIFIED", "reason": reason})
            }
        }
    }
}

pub fn task_gate_authorisation(p: &Project, gate_id: &str) -> GateAuthorisation {
    let store = RecordStore::load(&p.root);
    task_gate_authorisation_in(p, &store, gate_id)
}

pub fn task_gate_authorisation_in(
    p: &Project,
    store: &RecordStore,
    gate_id: &str,
) -> GateAuthorisation {
    let Some(g) = store.get(gate_id).filter(|g| g.rtype() == "human-gate") else {
        return GateAuthorisation::Missing;
    };
    let b = crate::t2::verify_record(g);
    if !b.is_verified() {
        return GateAuthorisation::Unverified {
            reason: b.to_value(),
        };
    }
    match g.get("gate_status").as_str() {
        "PENDING" | "PRESENTED" => GateAuthorisation::Pending {
            presented: g
                .data
                .get("presented_in_chat")
                .and_then(|v| v.as_bool())
                .unwrap_or(false),
        },
        "ANSWERED" => match verified_answer_in(p, store, gate_id) {
            Ok(a) if a.authorises_blocked_work => GateAuthorisation::Authorised {
                option: a.option,
                by_kind: a.by_kind,
            },
            Ok(a) => GateAuthorisation::Declined { option: a.option },
            Err(e) if e.code == "GATE_REVOKED" => GateAuthorisation::Withdrawn,
            Err(e) => GateAuthorisation::Unverified {
                reason: json!({"code": e.code, "message": e.message}),
            },
        },
        _ => GateAuthorisation::Withdrawn,
    }
}

/// A decision the OS honours: T2-bound, ACTIVE, and — when it asserts `human_approved` — derived from a gate whose
/// owner-signed answer verifies and chose `chosen_option`. For consumers of decisions (policy exceptions, CIT).
pub fn verified_decision(p: &Project, decision_id: &str) -> Result<Record> {
    let store = RecordStore::load(&p.root);
    let d = store
        .get(decision_id)
        .filter(|d| d.rtype() == "decision")
        .ok_or_else(|| {
            GovError::new(
                "DECISION_NOT_FOUND",
                format!("decision {decision_id} does not exist"),
            )
        })?;
    crate::t2::require_verified(d, "a governing decision")?;
    if d.data
        .get("human_approved")
        .and_then(|v| v.as_bool())
        .unwrap_or(false)
    {
        let gate = d
            .list("derived_from")
            .into_iter()
            .find(|g| g.starts_with("HDG-"))
            .ok_or_else(|| {
                GovError::new(
                    "HUMAN_ANSWER_UNVERIFIED",
                    format!(
                        "decision {decision_id} asserts human approval but derives from no gate"
                    ),
                )
            })?;
        let a = verified_answer_in(p, &store, &gate)?;
        if a.by_kind != "human" || a.option != d.get("chosen_option") {
            return Err(GovError::new("HUMAN_ANSWER_UNVERIFIED", format!("decision {decision_id} asserts human approval of '{}', but gate {gate} records {} answer '{}'", d.get("chosen_option"), a.by_kind, a.option)));
        }
    }
    Ok(d.clone())
}

// ------------------------------------------------------------------------------------ answering

/// What the caller asks `gov decide` to record. Only `by` naming a kernel *agent* role requests agent resolution;
/// every other request is for a human answer, whose authority is an owner-signed document — never these fields.
#[derive(Debug, Clone, Default)]
pub struct AnswerRequest {
    pub option: Option<String>,
    pub by: Option<String>,
    pub rationale: Option<String>,
    pub answer_file: Option<std::path::PathBuf>,
    pub evidence: Vec<String>,
}

fn move_tasks(
    p: &Project,
    gate_id: &str,
    from: &[&str],
    to: &str,
    note: &str,
    operation: &str,
) -> Result<Vec<String>> {
    let mut moved = vec![];
    let mut store = RecordStore::load(&p.root);
    let ids: Vec<String> = store
        .of_type("task")
        .into_iter()
        .filter(|t| t.get("human_gate") == gate_id)
        .map(|t| t.id())
        .collect();
    for tid in ids {
        if let Some(tr) = store.get_mut(&tid) {
            if from.contains(&tr.get("task_status").as_str()) {
                // WS-5 r2 IP-R3-1 (gates side): keep an OS-sealed task record verifiable; never bless an unverified one
                let was_verified = crate::t2::verify_record(tr).is_verified();
                tr.set("task_status", json!(to));
                tr.set("status_note", json!(note));
                tr.set("updated", json!(today()));
                crate::t2::seal_if_verified(tr, was_verified, operation)?;
                save_record(&p.root, tr)?;
                moved.push(tid);
            }
        }
    }
    Ok(moved)
}

/// Answer a gate. A human answer is an owner-signed document (BC-P2-10); an agent answer is a resolution within
/// `HUMAN_GATE_POLICY.agent_resolvable_when` by the L3+ acting role itself, with a rationale, on an assessment that
/// does not rest solely on its own declaration (BC-P2-18).
pub fn answer(p: &Project, id: &str, req: &AnswerRequest) -> Result<Value> {
    control::guard_write(p, "gate answer")?;
    // **The OWNER-DECISION-0006 §6 bullet 2 (approval) sink.** `gov decide` and `gov gate answer` both land here,
    // and this is the only function that moves a gate to ANSWERED. The operation-level guard above already
    // refuses the label below floor; this refuses the *effect*, so the property survives a future caller that
    // reaches approval by some other label.
    let _clearance = crate::srr::breakglass::guard_effect(
        crate::srr::breakglass::Effect::HumanGateApprove,
        "gate answer",
    )?;
    let pol = p.policies();
    let mut store = RecordStore::load(&p.root);
    let g = store
        .get_mut(id)
        .ok_or_else(|| GovError::new("GATE_NOT_FOUND", format!("{id} not found")))?;
    if g.rtype() != "human-gate" {
        return Err(GovError::new("USAGE", format!("{id} is not a human gate")));
    }
    let binding = crate::t2::verify_record(g);
    if !binding.is_verified() {
        // The presentation and status fields of this record are not what a gov operation wrote, so the OS has no
        // presentation of this gate it can stand behind (INV-008 / BC-P2-09).
        return Err(GovError::new("GATE_NOT_PRESENTED", format!("{id} cannot be answered: its record is not what gov wrote (T2 binding {}), so no OS-attested presentation exists. Restore it from version control or withdraw it (`gov gate revoke {id}`) and raise it again.", binding.code()))
            .with_details(json!({"gate": id, "cause": "T2_UNBOUND", "t2": binding.to_value()})));
    }
    if !matches!(g.get("gate_status").as_str(), "PENDING" | "PRESENTED") {
        return Err(GovError::new(
            "USAGE",
            format!("{id} is {}", g.get("gate_status")),
        ));
    }
    // INV-008 (HUMAN_GATE_POLICY.must_be_presented_in_chat, constitutionally true): the OS must have rendered this
    // exact package; a human answer must additionally bind its digest (the owner's receipt of what was shown).
    let must_present = pol.get_bool("HUMAN_GATE_POLICY", "must_be_presented_in_chat", true);
    let rendered = rendered_digest_matches(p, g);
    if must_present && rendered.is_none() {
        return Err(GovError::new("GATE_NOT_PRESENTED", format!("{id} has not been presented in its current form (INV-008); run `gov gate present {id}` and show it to the human first")));
    }
    let digest = rendered.unwrap_or_else(|| package_of(p, &g.data).1);
    let offered: Vec<String> = g.data["options"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|o| o["id"].as_str().map(String::from))
                .collect()
        })
        .unwrap_or_default();
    if let Some(o) = &req.option {
        if !offered.contains(o) {
            return Err(GovError::new(
                "GATE_OPTION_INVALID",
                format!("'{o}' is not an option of {id}; the answer must be one of {offered:?}"),
            )
            .with_details(json!({"offered": offered})));
        }
    }
    for e in &req.evidence {
        if store.get(e).is_none() {
            return Err(GovError::new(
                "USAGE",
                format!("evidence reference {e} does not resolve to a governed record"),
            ));
        }
    }
    // J1 (WS-10 r2 IP-WS10-02): the decision an answer mints may rest only on governed research/experiment evidence —
    // what the answer cites and what the gate itself was derived from
    let cited = cited_evidence_ids(&store.get(id).unwrap().data, &req.evidence);
    if !cited.is_empty() {
        crate::lifecycle::require_citable(p, &store, &cited)?;
    }
    let g = store.get_mut(id).unwrap();
    let by_is_agent = req
        .by
        .as_deref()
        .map(|b| b != "human" && authority::is_kernel_role(p, b))
        .unwrap_or(false);
    let acting = authority::level_of(p, &p.role)?;
    let (kind, option, by, rationale, evidence, signed): (
        &str,
        String,
        String,
        Option<String>,
        Value,
        Option<human_channel::Signed>,
    ) = if by_is_agent {
        let by = req.by.clone().unwrap_or_default();
        // agent-resolvable contradictions only (framework §50): assessed low impact, high confidence, reversible;
        // an L3+ acting role resolving as itself, with a recorded rationale, on an assessment it did not solely make
        let max_r = pol.get_str(
            "HUMAN_GATE_POLICY",
            "agent_resolvable_when.max_radius",
            "R1",
        );
        let min_c = pol.get_f64(
            "HUMAN_GATE_POLICY",
            "agent_resolvable_when.min_confidence",
            0.8,
        );
        let need_rev = pol.get_bool(
            "HUMAN_GATE_POLICY",
            "agent_resolvable_when.reversible",
            true,
        );
        let need_assessed = pol.get_bool(
            "HUMAN_GATE_POLICY",
            "agent_resolvable_when.require_assessed",
            true,
        );
        let need_indep = pol.get_bool(
            "HUMAN_GATE_POLICY",
            "agent_resolvable_when.independent_assessment",
            true,
        );
        let a = g.data["assessment"].clone();
        let mut radius = a["impact_radius"].as_str().map(String::from);
        // a CIT-linked gate is judged on the larger of its declared and its simulated radius
        if let Some(cit) = g
            .data
            .get("cit")
            .and_then(|v| v.as_str())
            .filter(|c| !c.is_empty())
        {
            let s2 = RecordStore::load(&p.root);
            if let Some(sim) = s2
                .get(cit)
                .and_then(|c| c.data["impact"]["radius"].as_str().map(String::from))
            {
                radius = Some(match radius {
                    Some(r) if radius_rank(&r) >= radius_rank(&sim) => r,
                    _ => sim,
                });
            }
        }
        let reversible = a["reversible"].as_bool();
        let conf = a["confidence"].as_f64();
        let source = a["source"].as_str().unwrap_or("declared").to_string();
        let declared_by = a["declared_by"]["session"]
            .as_str()
            .unwrap_or("")
            .to_string();
        let mut why: Vec<String> = vec![];
        if acting < 3 {
            why.push(format!(
                "acting role {} is L{acting}; agent resolution requires an L3+ acting role",
                p.role
            ));
        }
        if by != p.role {
            why.push(format!(
                "an agent resolves as itself: --by '{by}' is not the acting role '{}'",
                p.role
            ));
        }
        if need_assessed && (radius.is_none() || reversible.is_none() || conf.is_none()) {
            why.push(format!("the assessment is incomplete (impact_radius {:?}, reversible {:?}, confidence {:?}); an unassessed value counts against agent resolution", radius, reversible, conf));
        }
        let r = radius.clone().unwrap_or_else(|| "R5".into());
        if radius_rank(&r) > radius_rank(&max_r) {
            why.push(format!("impact radius {r} exceeds {max_r}"));
        }
        if conf.unwrap_or(0.0) < min_c {
            why.push(format!("confidence {:?} is below {min_c}", conf));
        }
        if need_rev && reversible != Some(true) {
            why.push(format!(
                "the decision is not assessed reversible ({reversible:?})"
            ));
        }
        if need_indep && source != "os" && declared_by == p.session_id {
            why.push("the assessment rests solely on the resolving session's own declaration (it raised this gate); another session or the OS must have assessed it".into());
        }
        let trigger = g.get("trigger");
        if human_only_trigger(p, &trigger) {
            why.push(format!("gates raised for '{trigger}' are human decisions (framework §51; HUMAN_GATE_POLICY.human_only_triggers) and are never agent-resolvable"));
        }
        if !why.is_empty() {
            return Err(GovError::new("AUTHORITY_DENIED", format!("agent '{by}' may not resolve {id}: {} (HUMAN_GATE_POLICY.agent_resolvable_when; framework §50). It needs a human answer.", why.join("; "))).with_details(json!({"operation": "answer_gate_as_agent", "role": p.role, "level": format!("L{acting}"), "reasons": why, "assessment": a, "effective_radius": radius})));
        }
        let rationale = req.rationale.clone().filter(|r| !r.trim().is_empty()).ok_or_else(|| {
            GovError::new("USAGE", format!("an agent resolution of {id} must record its rationale (framework §50: 'agent resolves + records rationale'); pass --rationale"))
        })?;
        let option = req
            .option
            .clone()
            .ok_or_else(|| GovError::new("USAGE", "an agent resolution names its --option"))?;
        let evidence = json!({"agent_resolution": {"resolver": {"session": p.session_id, "role": p.role, "level": format!("L{acting}")}, "assessment": a, "effective_radius": radius, "assessment_source": source, "policy": {"max_radius": max_r, "min_confidence": min_c, "reversible": need_rev}}});
        ("agent", option, by, Some(rationale), evidence, None)
    } else {
        // a HUMAN answer: relayed by an L3+ role, authorised only by an owner-signed document
        let need = authority::required_level(p, "answer_gate");
        if acting < need {
            return Err(GovError::new("AUTHORITY_DENIED", format!("role '{}' (L{acting}) may not relay a human answer for {id} (requires L{need})", p.role)).with_details(json!({"operation": "answer_gate", "role": p.role, "level": format!("L{acting}"), "required": format!("L{need}")})));
        }
        let anchor = human_channel::anchor(standalone_anchor_allowed(p))?;
        let exp = expected_for(p, &g.data);
        let s = human_channel::find(
            &anchor,
            human_channel::ANSWER_TYPE,
            &exp,
            req.answer_file.as_deref(),
        )?;
        let option = s.option.clone().unwrap_or_default();
        if let Some(o) = &req.option {
            if o != &option {
                return Err(GovError::new("HUMAN_ANSWER_MISMATCH", format!("--option '{o}' is not the option the owner signed ('{option}'); the signed document is the answer")));
            }
        }
        let rationale = s.rationale.clone().or_else(|| req.rationale.clone());
        let evidence = json!({"human_channel": s.evidence()});
        ("human", option, s.by.clone(), rationale, evidence, Some(s))
    };
    let mut answer_obj = json!({"option": option, "by": by, "by_kind": kind, "acting_role": p.role, "acting_session": p.session_id, "at": now_iso(), "rationale": rationale, "requested_by": req.by});
    for (k, v) in evidence.as_object().cloned().unwrap_or_default() {
        answer_obj[k] = v;
    }
    g.set("gate_status", json!("ANSWERED"));
    g.set("answer", answer_obj);
    match &signed {
        Some(s) => {
            g.set("presented_in_chat", json!(true));
            g.set(
                "presentation_receipt",
                json!({"kind": "answer", "acknowledged_by": s.by, "package_sha256": digest, "envelope_sha256": s.envelope_sha256}),
            );
        }
        None => {
            // An agent resolution: the package was rendered to, and resolved in, the resolving agent's own
            // interface. No human receipt exists and none is claimed (`kind: agent_resolution`); human-approval
            // consumers require `by_kind: human`, which only an owner-signed answer produces.
            g.set("presented_in_chat", json!(true));
            g.set(
                "presentation_receipt",
                json!({"kind": "agent_resolution", "resolver": {"session": p.session_id, "role": p.role}, "package_sha256": digest,
                       "note": "resolved within HUMAN_GATE_POLICY.agent_resolvable_when; this is not a human receipt"}),
            );
        }
    }
    crate::t2::seal_record(g, "gate answer")?;
    let gdata = g.data.clone();
    save_record(&p.root, g)?;
    if let Some(s) = &signed {
        human_channel::consume(s, id)?;
    }
    let did = store.next_id("decision");
    let mut dec = new_record(
        "decision",
        &did,
        &format!("Decision for {id}: option {option}"),
        json!({"question": gdata["question"], "options": gdata["options"], "chosen_option": option, "rationale": rationale.clone().unwrap_or_default(), "approved_by": by, "approved_at": now_iso(), "human_approved": kind == "human", "impact_radius": gdata.get("impact_radius").cloned().unwrap_or(json!("R1")), "reversibility": gdata.get("reversibility").cloned().unwrap_or(json!("unknown")), "confidence": if kind == "human" { 1.0 } else { gdata.get("confidence").and_then(|v| v.as_f64()).unwrap_or(0.8) }, "derived_from": [id], "evidence_refs": req.evidence, "cit": gdata.get("cit").cloned().unwrap_or(Value::Null), "state_class": "AUTHORITATIVE"}),
    );
    if dec.data["cit"].is_null() {
        dec.data.as_object_mut().unwrap().remove("cit");
    }
    let authorises = option_authorises(&gdata["options"], &option);
    if !authorises {
        dec.set("status", json!("ACTIVE"));
        dec.set("declined", json!(true));
    }
    dec.set("approved_by_kind", json!(kind));
    dec.set("approved_by_role", json!(p.role));
    // What the decision governs is part of the package the human answered (its digest covers `decision_scope`),
    // so it is carried into the decision exactly as asked — e.g. the PROJECT_EXCEPTIONS it authorises.
    if let Some(scope) = gdata.get("decision_scope").and_then(|v| v.as_object()) {
        for k in DECISION_SCOPE_FIELDS {
            if let Some(v) = scope.get(*k) {
                dec.set(k, v.clone());
            }
        }
    }
    if let Some(s) = &signed {
        dec.set(
            "human_approval_evidence",
            json!({"gate": id, "envelope_sha256": s.envelope_sha256, "signed_by_key_ids": s.key_ids, "anchor": s.anchor}),
        );
    }
    crate::t2::seal_record(&mut dec, "gate answer")?;
    save_record(&p.root, &dec)?;
    let influence = record_influence_reported(p, &cited, &did);
    if let Some(cit_id) = gdata
        .get("cit")
        .and_then(|v| v.as_str())
        .filter(|c| !c.is_empty())
    {
        let mut sc = RecordStore::load(&p.root);
        if let Some(c) = sc.get_mut(cit_id) {
            // a CIT record the OS sealed stays verifiable after this write; an unverified one is not blessed
            let was_verified = crate::t2::verify_record(c).is_verified();
            if option == "A" {
                if c.get("decision").is_empty() {
                    c.set("decision", json!(did));
                }
            } else if matches!(
                c.get("cit_status").as_str(),
                "PROPOSED" | "SIMULATED" | "APPROVED"
            ) {
                // a decline is final for the transaction (verifier C-N1): it can never be executed
                c.set("cit_status", json!("REJECTED"));
                c.set("decision", json!(did));
                if c.data.get("approval").is_some() {
                    c.data.as_object_mut().unwrap().remove("approval");
                }
                if let Some(j) = c.data["journal"].as_array_mut() {
                    j.push(json!({"at": now_iso(), "event": "rejected_by_gate", "gate": id, "option": option, "by": by, "by_kind": kind}));
                }
            }
            crate::t2::seal_if_verified(c, was_verified, "gate answer (cit)")?;
            save_record(&p.root, c)?;
        }
    }
    // BC-P2-12 (answer side): only an authorising answer releases the blocked work; any other answer blocks it
    let (unblocked, blocked) = if authorises {
        (
            move_tasks(
                p,
                id,
                &["WAITING_HUMAN"],
                "READY",
                &format!("released by {id} (option {option})"),
                "gate answer (releases task)",
            )?,
            vec![],
        )
    } else {
        (
            vec![],
            move_tasks(
                p,
                id,
                &["WAITING_HUMAN", "READY"],
                "BLOCKED",
                &format!("{id} was answered '{option}', which does not authorise this work"),
                "gate answer (blocks task)",
            )?,
        )
    };
    let mut out = json!({"gate": id, "decision": did, "option": option, "answered_by_kind": kind, "answered_by": by, "authorises_blocked_work": authorises, "unblocked_tasks": unblocked, "blocked_tasks": blocked, "cit": gdata.get("cit")});
    if !influence.is_null() {
        out["evidence_influence"] = influence;
    }
    Ok(out)
}

/// Withdraw a gate (and any approval derived from it). The linked CIT returns to SIMULATED; the derived decision is
/// marked REJECTED with provenance; work the gate blocked (or had released) is BLOCKED again. Requires
/// AUTHORITY_POLICY.authority_levels_required.revoke_gate. Withdrawal is the fail-safe direction, so it is allowed
/// on a gate record that is not T2-bound (the binding state is recorded).
pub fn revoke(p: &Project, id: &str, reason: Option<&str>) -> Result<Value> {
    control::guard_write(p, "gate revoke")?;
    authority::require(p, "revoke_gate")?;
    let mut store = RecordStore::load(&p.root);
    let g = store
        .get_mut(id)
        .ok_or_else(|| GovError::new("GATE_NOT_FOUND", format!("{id} not found")))?;
    if g.rtype() != "human-gate" {
        return Err(GovError::new("USAGE", format!("{id} is not a human gate")));
    }
    if matches!(g.get("gate_status").as_str(), "WITHDRAWN" | "EXPIRED") {
        return Err(GovError::new(
            "USAGE",
            format!("{id} is already {}", g.get("gate_status")),
        ));
    }
    let binding = crate::t2::verify_record(g);
    let previous = g.get("gate_status");
    g.set("gate_status", json!("WITHDRAWN"));
    g.set("revoked", json!({"by_session": p.session_id, "by_role": p.role, "at": now_iso(), "reason": reason, "previous_status": previous, "t2_binding_before": binding.to_value()}));
    crate::t2::seal_record(g, "gate revoke")?;
    let gdata = g.data.clone();
    save_record(&p.root, g)?;
    let mut touched = json!({"cit": Value::Null, "decisions": []});
    let mut s2 = RecordStore::load(&p.root);
    let derived: Vec<String> = s2
        .of_type("decision")
        .into_iter()
        .filter(|d| d.list("derived_from").iter().any(|x| x == id))
        .map(|d| d.id())
        .collect();
    for did in &derived {
        if let Some(d) = s2.get_mut(did) {
            d.set("status", json!("REJECTED"));
            d.set("state_class", json!("HISTORICAL"));
            d.set("revoked_gate", json!(id));
            d.set("updated", json!(today()));
            crate::t2::seal_record(d, "gate revoke")?;
            save_record(&p.root, d)?;
        }
    }
    touched["decisions"] = json!(derived);
    if let Some(cit_id) = gdata
        .get("cit")
        .and_then(|v| v.as_str())
        .filter(|c| !c.is_empty())
    {
        let mut s3 = RecordStore::load(&p.root);
        if let Some(c) = s3.get_mut(cit_id) {
            let was_verified = crate::t2::verify_record(c).is_verified();
            if c.get("cit_status") == "APPROVED" {
                c.set("cit_status", json!("SIMULATED"));
            }
            if c.data.get("approval").is_some() {
                c.data.as_object_mut().unwrap().remove("approval");
            }
            if let Some(j) = c.data["journal"].as_array_mut() {
                j.push(json!({"at": now_iso(), "event": "approval_revoked", "gate": id, "reason": reason, "by_session": p.session_id}));
            }
            crate::t2::seal_if_verified(c, was_verified, "gate revoke (cit)")?;
            save_record(&p.root, c)?;
            touched["cit"] = json!({"id": cit_id, "cit_status": c.get("cit_status")});
        }
    }
    // BC-P2-12 (answer side): work blocked by, or released by, this gate is blocked again
    let blocked = move_tasks(
        p,
        id,
        &["WAITING_HUMAN", "READY", "IN_PROGRESS", "CLAIMED"],
        "BLOCKED",
        &format!("human gate {id} was withdrawn: the work it blocked is not authorised"),
        "gate revoke (blocks task)",
    )?;
    touched["blocked_tasks"] = json!(blocked);
    Ok(json!({"gate": id, "gate_status": "WITHDRAWN", "touched": touched}))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn reversibility_is_assessed_explicitly_or_not_at_all() {
        let m = |v: Value| v.as_object().cloned().unwrap();
        assert_eq!(
            classify_reversibility(&m(json!({"reversibility": "reversible"}))),
            Some(true)
        );
        assert_eq!(
            classify_reversibility(&m(json!({"reversibility": "snapshot rollback available"}))),
            Some(true)
        );
        assert_eq!(
            classify_reversibility(&m(json!({"reversibility": "irreversible"}))),
            Some(false)
        );
        assert_eq!(
            classify_reversibility(&m(json!({"reversibility": "low"}))),
            Some(false)
        );
        assert_eq!(
            classify_reversibility(&m(json!({"reversibility": "not assessed"}))),
            None
        );
        assert_eq!(classify_reversibility(&m(json!({}))), None);
        assert_eq!(
            classify_reversibility(&m(json!({"reversibility": "maybe"}))),
            None
        );
        assert_eq!(
            classify_reversibility(&m(json!({"reversibility": "maybe", "reversible": true}))),
            Some(true)
        );
    }

    #[test]
    fn options_authorise_blocked_work_explicitly_or_by_the_approve_convention() {
        let opts = json!([{"id": "A", "description": "go"}, {"id": "B", "description": "stop"}, {"id": "C", "description": "go too", "authorises_blocked_work": true}]);
        assert!(option_authorises(&opts, "A"));
        assert!(!option_authorises(&opts, "B"));
        assert!(option_authorises(&opts, "C"));
        assert!(!option_authorises(&opts, "Z"));
    }

    #[test]
    fn radii_are_validated() {
        for ok in ["R0", "R1", "R5"] {
            assert!(valid_radius(ok));
        }
        for bad in ["R6", "R", "r1", "R10", "high"] {
            assert!(!valid_radius(bad));
        }
    }
}
