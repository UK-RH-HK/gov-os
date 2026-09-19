//! `gov adopt`: staged, path-first, memory-safe brownfield adoption (framework §79, protocol A0-A11) with an
//! immutable evidence tree and independence enforced by session/role separation and verdict gates.
//!
//! ## Authorship and independence (BC-P2-34; Contract v3 T1/T2/O3; adoption protocol §3, §10-§16)
//!
//! Agent roles are adapter-declared (OWNER-DECISION-P2-0001): the OS does not issue agent credentials, so it binds
//! every adoption stage to **what the caller declared** and applies it consistently:
//!
//! * **Actor.** Every stage runs as the process's declared acting role (the one authority is evaluated against,
//!   `authority::installed_acting_role`) and a **declared session** (`--session`, `GOV_SESSION`, or
//!   `adopt review --reviewer-session`; [`identity::resolve_actor`]). A stage with no declared session refuses
//!   (`ADOPTION_SESSION_UNDECLARED`): authorship that is not recorded cannot establish independence.
//! * **Authorship log.** Each stage records its author (group, role, session, where each came from) in the adoption
//!   baseline. Within one adoption a session keeps the role it first acted under (`ADOPTION_ROLE_INCONSISTENT`).
//! * **Designated independent roles.** A5, A7, A10 and A11 are performed only by the kernel role designated for them
//!   ([`DESIGNATED_ROLES`]) in a session and role that authored no planner, executor or memory-builder stage
//!   (`INDEPENDENCE`, `details.cause`).
//! * **Verdicts bound to what was approved.** The A5 approval records digests of the catalogue, plan and tests it
//!   approved, and which tests the reviewer authored (the planner's scaffold is regression evidence, never the
//!   reviewer's); A6 refuses to execute anything once one of them changed (`APPROVAL_STALE`); A7 never accepts with
//!   zero executed tests or tests that are not the approved ones; A10 accepts only on held-out queries the memory
//!   verifier authored (the builder's starter set is regression evidence); A11 runs the G5 full suite.
//! * **T2.** The baseline that carries the log, the stage order and every verdict is OS-written state: it is sealed
//!   ([`crate::t2`]) whenever a stage writes it and honoured only when the seal verifies (`T2_UNBOUND`), so a verdict,
//!   an author entry or a bound digest edited by hand is never honoured.
use crate::kernel::{install_kernel, resolve_kernel_source};
use crate::lock::write_lock;
use crate::memory::db::RuntimeDb;
use crate::migrations::{
    classify, executor, extraction, identity, inventory, ownership, planner, references, verify,
};
use crate::records::{new_record, save_record};
use crate::util::{
    glob_match, now_iso, read_json, read_text, read_yaml, write_json, write_text, write_yaml,
};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};
use std::path::{Path, PathBuf};

pub const EVIDENCE: &str = "spec/audits/GOVERNANCE-ADOPTION";
pub const STAGES: &[&str] = &[
    "A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11",
];
/// The id under which T2 refusals name the adoption record.
pub const BASELINE_ID: &str = "ADOPTION-BASELINE";

fn ev(root: &Path) -> PathBuf {
    root.join(EVIDENCE)
}
fn baseline_path(root: &Path) -> PathBuf {
    ev(root).join("00-BASELINE.yaml")
}
fn load_baseline_raw(root: &Path) -> Result<Value> {
    read_yaml(&baseline_path(root)).map_err(|_| {
        GovError::new(
            "ADOPTION_NOT_STARTED",
            "run `gov adopt baseline` (A0) first",
        )
    })
}
/// The adoption record, honoured only as the OS wrote it (T2): stage order, authorship and every independent verdict
/// live here, so a hand-edited record decides nothing.
fn load_baseline(root: &Path) -> Result<Value> {
    let b = load_baseline_raw(root)?;
    let binding = crate::t2::verify_value(&b, "");
    if !binding.is_verified() {
        return Err(GovError::new(
            "T2_UNBOUND",
            format!(
                "{EVIDENCE}/00-BASELINE.yaml is not the adoption record gov wrote (binding {}): its stage order, authorship and verdicts are not honoured. Restore it from version control, or restart the adoption with `gov adopt baseline` (A0).",
                binding.code()
            ),
        )
        .with_details(json!({"record": BASELINE_ID, "path": format!("{EVIDENCE}/00-BASELINE.yaml"), "fact": "adoption stage order, authorship and independent verdicts", "t2": binding.to_value(),
            "remediation": "restore 00-BASELINE.yaml from version control, or run `gov adopt baseline` to start a new adoption pass"})));
    }
    Ok(b)
}
/// Persist the adoption record sealed as written by `adopt <op>` (T2).
fn save_baseline(root: &Path, b: &Value, op: &str) -> Result<()> {
    let mut v = b.clone();
    if let Some(o) = v.as_object_mut() {
        o.remove(crate::t2::SEAL_FIELD);
    }
    crate::t2::seal_value(&mut v, "", &format!("adopt {op}"))?;
    write_yaml(&baseline_path(root), &v)
}
fn set_stage(
    root: &Path,
    stage: &str,
    status: &str,
    extra: Option<(&str, Value)>,
) -> Result<Value> {
    let mut b = load_baseline(root)?;
    b["stage_status"][stage] = json!(status);
    b["stage_times"][stage] = json!(now_iso());
    if let Some((k, v)) = extra {
        b[k] = v;
    }
    save_baseline(root, &b, stage)?;
    Ok(b)
}
fn require_stage(b: &Value, stage: &str) -> Result<()> {
    if b["stage_status"][stage].as_str() != Some("done") {
        return Err(GovError::new(
            "STAGE_ORDER",
            format!("stage {stage} must be complete first (protocol order A0→A11)"),
        ));
    }
    Ok(())
}
fn require_verdict(b: &Value, key: &str, accepted: &[&str]) -> Result<()> {
    let v = b["verdicts"][key]["verdict"].as_str().unwrap_or("");
    if !accepted.contains(&v) {
        return Err(GovError::new(
            "VERDICT_REQUIRED",
            format!("independent verdict '{key}' must be one of {accepted:?} (current: '{v}')"),
        ));
    }
    Ok(())
}

// ---------------------------------------------------------------- authorship and independence (BC-P2-34)

/// The kernel role designated for each independent adoption stage (adoption protocol §3 roles B, D, F, G). These are
/// kernel role ids (`framework/roles/ROLES.yaml`); the stage is performed only by an invocation that declared exactly
/// that role.
pub const DESIGNATED_ROLES: &[(&str, &str, &str)] = &[
    (
        "A5",
        "migration-reviewer",
        "Role B — independent migration reviewer & test author",
    ),
    (
        "A7",
        "migration-verifier",
        "Role D — independent migration verifier",
    ),
    (
        "A10",
        "memory-verifier",
        "Role F — independent memory verifier / test author",
    ),
    (
        "A11",
        "independent-auditor",
        "Role G — comprehensive independent auditor",
    ),
];

/// The kernel role designated for independent stage `stage`, if it is one.
pub fn designated_role(stage: &str) -> Option<&'static str> {
    DESIGNATED_ROLES
        .iter()
        .find(|(s, _, _)| *s == stage)
        .map(|(_, r, _)| *r)
}

/// Authorship groups of the adoption protocol: the builders whose context an independent stage must not continue,
/// and the independent roles themselves.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Group {
    /// Role A: A0-A4 and the test scaffold.
    Planner,
    /// Role C: A6 batches, rollback, A8 extraction/retirement.
    Executor,
    /// Role E: A9.
    MemoryBuilder,
    /// Roles B, D, F, G: A5, A7, A10, A11.
    Independent,
}

impl Group {
    pub fn as_str(&self) -> &'static str {
        match self {
            Group::Planner => "planner",
            Group::Executor => "executor",
            Group::MemoryBuilder => "memory_builder",
            Group::Independent => "independent",
        }
    }
    fn is_builder(s: &str) -> bool {
        matches!(s, "planner" | "executor" | "memory_builder")
    }
}

struct StageSpec {
    stage: &'static str,
    command: &'static str,
    group: Group,
    /// AUTHORITY_POLICY class (the same one G0 evaluates for the command).
    class: &'static str,
}

const STAGE_SPECS: &[StageSpec] = &[
    StageSpec {
        stage: "A0",
        command: "baseline",
        group: Group::Planner,
        class: "adoption_plan",
    },
    StageSpec {
        stage: "A1",
        command: "inventory",
        group: Group::Planner,
        class: "adoption_plan",
    },
    StageSpec {
        stage: "A2",
        command: "classify",
        group: Group::Planner,
        class: "adoption_plan",
    },
    StageSpec {
        stage: "A3",
        command: "map",
        group: Group::Planner,
        class: "adoption_plan",
    },
    StageSpec {
        stage: "A4",
        command: "plan",
        group: Group::Planner,
        class: "adoption_plan",
    },
    StageSpec {
        stage: "A5",
        command: "test-design",
        group: Group::Planner,
        class: "adoption_plan",
    },
    StageSpec {
        stage: "A5",
        command: "review",
        group: Group::Independent,
        class: "adoption_review",
    },
    StageSpec {
        stage: "A6",
        command: "migrate",
        group: Group::Executor,
        class: "migrate_execute",
    },
    StageSpec {
        stage: "A6",
        command: "rollback",
        group: Group::Executor,
        class: "migrate_execute",
    },
    StageSpec {
        stage: "A7",
        command: "verify-migration",
        group: Group::Independent,
        class: "adoption_review",
    },
    StageSpec {
        stage: "A8",
        command: "extract-legacy",
        group: Group::Executor,
        class: "migrate_execute",
    },
    StageSpec {
        stage: "A9",
        command: "build-memory",
        group: Group::MemoryBuilder,
        class: "build_memory",
    },
    StageSpec {
        stage: "A10",
        command: "verify-memory",
        group: Group::Independent,
        class: "adoption_review",
    },
    StageSpec {
        stage: "A11",
        command: "audit",
        group: Group::Independent,
        class: "adoption_review",
    },
];

fn spec(command: &str) -> &'static StageSpec {
    STAGE_SPECS
        .iter()
        .find(|s| s.command == command)
        .expect("every adoption command has a stage spec")
}

/// The author of one adoption stage invocation, as the OS established it.
#[derive(Debug, Clone)]
pub struct StageActor {
    pub stage: &'static str,
    pub command: &'static str,
    pub group: Group,
    pub actor: identity::ResolvedActor,
    /// For an independent stage: the evidence that independence was established (designated role, builders judged).
    pub independence: Value,
}

impl StageActor {
    pub fn session(&self) -> String {
        self.actor.session_id()
    }
    pub fn role(&self) -> String {
        self.actor.role_id()
    }
}

/// Authority for a stage, evaluated for the declared role against the installed kernel's policy, or against the kernel
/// embedded in this binary when nothing is installed yet (BC-P2-08: every adopt stage, first install batch
/// included). The CLI's G0 guard makes the same decision; this keeps it for every caller of the runtime.
fn stage_authority(root: &Path, role: &str, class: &str) -> Result<()> {
    let p = Project::open(root);
    if p.is_installed() {
        let p = p.with_session(None, Some(role.to_string()));
        crate::authority::require(&p, class)?;
    } else {
        crate::authority::require_with_embedded_kernel(role, class)?;
    }
    Ok(())
}

fn independence_refusal(stage: &str, cause: &str, message: String, details: Value) -> GovError {
    let mut d = details;
    d["stage"] = json!(stage);
    d["cause"] = json!(cause);
    d["designated_role"] = json!(designated_role(stage));
    d["remediation"] = json!(format!(
        "run {stage} as the designated role '{}' in a fresh session that authored no planner, executor or memory-builder stage of this adoption (declare both: --role, --session / GOV_SESSION)",
        designated_role(stage).unwrap_or("-")
    ));
    GovError::new("INDEPENDENCE", message).with_details(d)
}

/// Resolve and check the actor of a stage against the adoption record `b` (None for A0, which starts one).
fn check_actor(
    root: &Path,
    s: &'static StageSpec,
    actor: &identity::Actor,
    stage_flag: Option<&str>,
    b: Option<&Value>,
) -> Result<StageActor> {
    let who = identity::resolve_actor(actor, stage_flag)?;
    let role = who.role_id();
    // independent stages: the designated role, declared (an undeclared invocation carries no role at all)
    if s.group == Group::Independent {
        let want = designated_role(s.stage).unwrap_or("");
        if !who.role_declared() {
            return Err(independence_refusal(s.stage, "ROLE_UNDECLARED", format!("{} ({}) is performed by the designated independent role '{want}'; this invocation declared no role", s.stage, s.command), json!({"actor": who.to_value()})));
        }
        if role != want {
            return Err(independence_refusal(s.stage, "ROLE_NOT_DESIGNATED", format!("{} ({}) is performed only by the role designated for it, '{want}'; this invocation declared '{role}'", s.stage, s.command), json!({"actor": who.to_value()})));
        }
    }
    stage_authority(root, &role, s.class)?;
    if !who.session_declared() {
        return Err(GovError::new(
            "ADOPTION_SESSION_UNDECLARED",
            format!(
                "adoption stage {} ({}) records its author, and this invocation declared no session{}; an undeclared (generated) session cannot establish or be judged for independence",
                s.stage,
                s.command,
                who.session.as_deref().map(|x| format!(" (the id '{x}' was not declared by the caller)")).unwrap_or_default()
            ),
        )
        .with_details(json!({"stage": s.stage, "actor": who.to_value(), "remediation": "declare the session you act in: the global --session <id> flag or GOV_SESSION (review: --reviewer-session)"})));
    }
    let session = who.session_id();
    let authors: Vec<Value> = b
        .and_then(|b| b["authors"].as_array().cloned())
        .unwrap_or_default();
    let mut independence = Value::Null;
    if s.group == Group::Independent {
        let builders: Vec<&Value> = authors
            .iter()
            .filter(|a| Group::is_builder(a["group"].as_str().unwrap_or("")))
            .collect();
        if let Some(a) = builders
            .iter()
            .find(|a| a["session"].as_str() == Some(session.as_str()))
        {
            return Err(independence_refusal(s.stage, "SAME_SESSION_AS_BUILDER", format!("{} must be performed in a fresh session: session '{session}' authored {} stage(s) {} of this adoption (protocol §3: independent roles do not continue builder/executor context)", s.stage, a["group"].as_str().unwrap_or(""), a["stages"]), json!({"actor": who.to_value(), "builder": a})));
        }
        if let Some(a) = builders
            .iter()
            .find(|a| a["role"].as_str() == Some(role.as_str()))
        {
            return Err(independence_refusal(
                s.stage,
                "SAME_ROLE_AS_BUILDER",
                format!(
                    "{}: role '{role}' authored {} stage(s) {} of this adoption",
                    s.stage,
                    a["group"].as_str().unwrap_or(""),
                    a["stages"]
                ),
                json!({"actor": who.to_value(), "builder": a}),
            ));
        }
        independence = json!({"established": true, "designated_role": designated_role(s.stage), "role": role, "session": session,
            "session_source": who.session_source.as_str(), "role_source": who.role_source,
            "judged_builders": builders.iter().map(|a| json!({"group": a["group"], "role": a["role"], "session": a["session"], "stages": a["stages"]})).collect::<Vec<_>>(),
            "basis": "declared role and session (adapter-declared identity, OWNER-DECISION-P2-0001) recorded against every builder author of this adoption"});
    }
    if let Some(a) = authors.iter().find(|a| {
        a["session"].as_str() == Some(session.as_str()) && a["role"].as_str() != Some(role.as_str())
    }) {
        return Err(GovError::new(
            "ADOPTION_ROLE_INCONSISTENT",
            format!(
                "session '{session}' authored {:?} of this adoption as '{}' and now declares '{role}'; within one adoption a session keeps the role it acts under (roles are adapter-declared: one agent session, one role)",
                a["stages"], a["role"].as_str().unwrap_or("")
            ),
        )
        .with_details(json!({"stage": s.stage, "actor": who.to_value(), "earlier": a, "remediation": "act in the session the role was assigned, or start a new session for the other role"})));
    }
    Ok(StageActor {
        stage: s.stage,
        command: s.command,
        group: s.group,
        actor: who,
        independence,
    })
}

/// Resolve the actor of a stage of an existing adoption and load the (verified) record.
fn begin_stage(
    root: &Path,
    command: &str,
    actor: &identity::Actor,
    stage_flag: Option<&str>,
) -> Result<(Value, StageActor)> {
    let s = spec(command);
    let b = load_baseline(root)?;
    let who = check_actor(root, s, actor, stage_flag, Some(&b))?;
    Ok((b, who))
}

/// Record `who` in the authorship log of `b` (one entry per group, session and role; the stages it performed).
fn record_author(b: &mut Value, who: &StageActor) {
    if !b["authors"].is_array() {
        b["authors"] = json!([]);
    }
    let now = now_iso();
    let arr = b["authors"].as_array_mut().unwrap();
    let key = (who.group.as_str(), who.session(), who.role());
    if let Some(a) = arr.iter_mut().find(|a| {
        a["group"].as_str() == Some(key.0)
            && a["session"].as_str() == Some(key.1.as_str())
            && a["role"].as_str() == Some(key.2.as_str())
    }) {
        let label = format!("{} {}", who.stage, who.command);
        if !a["stages"]
            .as_array()
            .map(|x| x.iter().any(|y| y == &json!(label)))
            .unwrap_or(false)
        {
            a["stages"].as_array_mut().map(|x| x.push(json!(label)));
        }
        a["last_at"] = json!(now);
        return;
    }
    arr.push(json!({"group": key.0, "role": key.2, "session": key.1, "session_source": who.actor.session_source.as_str(),
        "role_source": who.actor.role_source, "stages": [format!("{} {}", who.stage, who.command)], "first_at": now, "last_at": now}));
}

fn verdict_actor(who: &StageActor) -> Value {
    json!({"session": who.session(), "role": who.role(), "session_source": who.actor.session_source.as_str(), "role_source": who.actor.role_source})
}

/// Digest of the migration plan as approved (volatile regeneration stamps excluded).
fn plan_digest(plan: &Value) -> String {
    let mut m = plan.clone();
    if let Some(o) = m.as_object_mut() {
        for k in [
            "last_regenerated_at",
            "last_regenerated_by",
            crate::t2::SEAL_FIELD,
        ] {
            o.remove(k);
        }
    }
    identity::content_hash(&m)
}

/// The catalogue, plan and tests exactly as they stand now, digested the way an approval binds them.
fn current_bindings(root: &Path) -> Result<Value> {
    let catalogue = read_jsonl(&ev(root).join(format!("{CATALOGUE_STEM}.jsonl")))?;
    let plan = read_yaml(&ev(root).join(format!("{PLAN_STEM}.yaml"))).unwrap_or(Value::Null);
    let tests = read_yaml(&ev(root).join("06-migration-tests.yaml")).unwrap_or(Value::Null);
    Ok(
        json!({"catalogue_sha256": planner::catalogue_digest(&catalogue), "plan_sha256": plan_digest(&plan), "tests_sha256": verify::tests_digest(&tests),
        "catalogue_entries": catalogue.len(), "plan_version": plan["version"], "tests": tests["tests"].as_array().map(|a| a.len()).unwrap_or(0)}),
    )
}

/// Which of the artefacts `verdict` bound differ from what stands now.
fn binding_changes(verdict: &Value, now: &Value) -> Vec<String> {
    ["catalogue_sha256", "plan_sha256", "tests_sha256"]
        .iter()
        .filter(|k| verdict[**k].as_str().is_some() && verdict[**k] != now[**k])
        .map(|k| k.trim_end_matches("_sha256").to_string())
        .chain(
            ["catalogue_sha256", "plan_sha256", "tests_sha256"]
                .iter()
                .filter(|k| verdict[**k].as_str().is_none())
                .map(|k| {
                    format!(
                        "{} (not bound by the verdict)",
                        k.trim_end_matches("_sha256")
                    )
                }),
        )
        .collect()
}

/// **Execution bound to the approval (BC-P2-34).** Refuse unless the catalogue, plan and independent tests are exactly
/// those the A5 approval bound.
fn require_approved_artefacts(root: &Path, b: &Value, what: &str) -> Result<Value> {
    let a5 = &b["verdicts"]["A5"];
    let now = current_bindings(root)?;
    let changed = binding_changes(a5, &now);
    if !changed.is_empty() {
        return Err(GovError::new(
            "APPROVAL_STALE",
            format!(
                "{what} refused: the {} changed after the independent reviewer approved them (A5 by '{}', session '{}'); execution is bound to exactly the approved plan, catalogue and tests (protocol §3 Role C, §11 \"do not weaken tests\")",
                changed.join(", "),
                a5["role"].as_str().unwrap_or(""),
                a5["session"].as_str().unwrap_or("")
            ),
        )
        .with_details(json!({"changed": changed, "approved": {"catalogue_sha256": a5["catalogue_sha256"], "plan_sha256": a5["plan_sha256"], "tests_sha256": a5["tests_sha256"]}, "current": now,
            "remediation": "restore the approved artefacts, or have the independent reviewer review the changed plan/tests again (`gov adopt review`)"})));
    }
    Ok(now)
}

fn write_md(root: &Path, name: &str, text: &str) -> Result<String> {
    let p = ev(root).join(name);
    write_text(&p, text)?;
    Ok(format!("{EVIDENCE}/{name}"))
}
fn scanner_for(root: &Path) -> crate::security::secrets::SecretScanner {
    let p = Project::open(root);
    if p.is_installed() {
        return p.secret_scanner().clone();
    }
    match crate::kernel::canonical_root()
        .or_else(|| std::env::var("GOV_KERNEL_SOURCE").ok().map(PathBuf::from))
    {
        Some(r) => {
            let pol = read_yaml(
                &r.join("framework")
                    .join("policies")
                    .join("SECURITY_POLICY.yaml"),
            )
            .or_else(|_| read_yaml(&r.join("policies").join("SECURITY_POLICY.yaml")))
            .unwrap_or(json!({}));
            crate::security::secrets::SecretScanner::from_policies(&pol, &json!({}))
        }
        None => crate::security::secrets::SecretScanner::default_scanner(),
    }
}

// ---------------------------------------------------------------- A0
pub fn a0_baseline(root: &Path, session: &str) -> Result<Value> {
    a0_baseline_by(root, &identity::Actor::supplied(session, None))
}

/// A0 as `actor` (Role A, planner). Starts a new adoption record: its authorship log begins with the planner.
pub fn a0_baseline_by(root: &Path, actor: &identity::Actor) -> Result<Value> {
    let who = check_actor(root, spec("baseline"), actor, None, None)?;
    let session = who.session();
    let session = session.as_str();
    std::fs::create_dir_all(ev(root))?;
    let p = Project::open(root);
    let git = p.git_available();
    let dirty = if git { p.git_dirty_files() } else { vec![] };
    let mut interrupted = json!({"detected": false, "items": []});
    let partial_gov =
        root.join("governance").exists() && !root.join("governance/framework.lock").exists();
    if partial_gov {
        interrupted["detected"] = json!(true);
        interrupted["items"].as_array_mut().unwrap().push(json!({"kind": "partial_governance_dir", "classification": "PARTIAL_SHOULD_ROLL_BACK", "note": "governance/ exists without framework.lock"}));
    }
    if p.is_installed() {
        if let Ok(r) = crate::recovery::recover(&p, true) {
            if !r["items"].as_array().map(|a| a.is_empty()).unwrap_or(true) {
                interrupted["detected"] = json!(true);
                interrupted["items"] = r["items"].clone();
            }
        }
    }
    if baseline_path(root).exists() {
        if let Ok(prev) = read_yaml(&baseline_path(root)) {
            if let Some(st) = prev["stage_status"].as_object() {
                for (k, v) in st {
                    if v == "in_progress" {
                        interrupted["detected"] = json!(true);
                        interrupted["items"].as_array_mut().unwrap().push(json!({"kind": "adoption_stage", "stage": k, "classification": "UNKNOWN"}));
                    }
                }
            }
        }
    }
    // baseline tests via ecosystem detection (record, never fail)
    let eco = crate::capabilities::ecosystems::detect(root, &["product/".into()]);
    let mut baseline_tests =
        json!({"ran": false, "reason": "no runnable native test command detected"});
    if let Some(e) = eco["ecosystems"].as_array().and_then(|a| {
        a.iter()
            .find(|e| e["test"].is_object() && e["available"].as_bool().unwrap_or(false))
    }) {
        let cmd: Vec<String> = e["test"]["command"]
            .as_array()
            .unwrap()
            .iter()
            .filter_map(|x| x.as_str().map(|s| s.to_string()))
            .collect();
        let cwd = root.join(e["dir"].as_str().unwrap_or(""));
        if let Ok((code, out, err)) = crate::util::run_cmd(&cmd, &cwd) {
            baseline_tests = json!({"ran": true, "ecosystem": e["id"], "command": cmd, "dir": e["dir"].as_str().unwrap_or(""), "exit": code, "status": if code == 0 { "passed" } else { "failed" }, "stdout_tail": out.lines().rev().take(5).collect::<Vec<_>>().into_iter().rev().collect::<Vec<_>>().join("\n"), "stderr_tail": err.lines().rev().take(5).collect::<Vec<_>>().into_iter().rev().collect::<Vec<_>>().join("\n")});
        }
    }
    let mut b = json!({"adoption_id": format!("ADOPT-{}", crate::util::today()), "started_at": now_iso(), "session": session, "planner_session": session, "commit": if git { p.git_commit() } else { "no-git".into() }, "branch": if git { p.git_branch() } else { "no-git".into() },
        "dirty_files": dirty, "untracked_files": [], "baseline_tests": baseline_tests, "interrupted_work": interrupted, "ecosystems": eco, "stage_status": {"A0": "done"}, "stage_times": {"A0": now_iso()}, "verdicts": {}, "authors": []});
    record_author(&mut b, &who);
    save_baseline(root, &b, "A0")?;
    Ok(
        json!({"stage": "A0", "evidence": format!("{EVIDENCE}/00-BASELINE.yaml"), "commit": b["commit"], "dirty_files": b["dirty_files"].as_array().map(|a| a.len()).unwrap_or(0), "interrupted": b["interrupted_work"]["detected"], "baseline_tests": b["baseline_tests"]["status"], "freeze_advice": if b["interrupted_work"]["detected"].as_bool().unwrap_or(false) { "interrupted work detected: review items before A1; broad edits are frozen by protocol" } else { "clean baseline" }}),
    )
}

// ---------------------------------------------------------------- A1
pub fn a1_inventory(root: &Path) -> Result<Value> {
    a1_inventory_by(root, &identity::Actor::process())
}

pub fn a1_inventory_by(root: &Path, actor: &identity::Actor) -> Result<Value> {
    let (mut b, who) = begin_stage(root, "inventory", actor, None)?;
    require_stage(&b, "A0")?;
    record_author(&mut b, &who);
    save_baseline(root, &b, "A1")?;
    set_stage(root, "A1", "in_progress", None)?;
    let items = inventory::inventory(root, &scanner_for(root));
    let summary = inventory::summary(&items);
    let mut jl = String::new();
    for i in &items {
        jl.push_str(&serde_json::to_string(i)?);
        jl.push('\n');
    }
    write_text(&ev(root).join("01-COLD-INVENTORY.jsonl"), &jl)?;
    let mut md = format!("# 01 — Cold deterministic inventory\n\nFiles: {} · tracked: {} · bytes: {}\n\nNo semantic memory was consulted (protocol §6).\n\n## By kind\n\n| Kind | Count |\n|---|---|\n", summary["files"], summary["tracked"], summary["bytes"]);
    for (k, v) in summary["by_kind"].as_object().unwrap() {
        md.push_str(&format!("| {k} | {v} |\n"));
    }
    md.push_str("\n## Notable\n\n");
    for kind in [
        "package_manifest",
        "entrypoint",
        "provider_rules",
        "chat_store",
        "index_store",
        "old_governance",
        "database",
        "secret",
        "devops",
    ] {
        let ps: Vec<String> = items
            .iter()
            .filter(|i| {
                i["kinds"]
                    .as_array()
                    .map(|a| a.iter().any(|k| k == kind))
                    .unwrap_or(false)
            })
            .map(|i| i["path"].as_str().unwrap_or("").to_string())
            .collect();
        if !ps.is_empty() {
            md.push_str(&format!("- **{kind}**: {}\n", ps.join(", ")));
        }
    }
    write_md(root, "01-COLD-INVENTORY.md", &md)?;
    set_stage(
        root,
        "A1",
        "done",
        Some(("inventory_summary", summary.clone())),
    )?;
    Ok(
        json!({"stage": "A1", "summary": summary, "evidence": [format!("{EVIDENCE}/01-COLD-INVENTORY.md"), format!("{EVIDENCE}/01-COLD-INVENTORY.jsonl")]}),
    )
}

fn read_jsonl(p: &Path) -> Result<Vec<Value>> {
    Ok(read_text(p)?
        .lines()
        .filter_map(|l| serde_json::from_str(l).ok())
        .collect())
}

// ---------------------------------------------------------------- A2
pub fn a2_classify(root: &Path) -> Result<Value> {
    a2_classify_by(root, &identity::Actor::process())
}

pub fn a2_classify_by(root: &Path, actor: &identity::Actor) -> Result<Value> {
    let (mut b, who) = begin_stage(root, "classify", actor, None)?;
    require_stage(&b, "A1")?;
    record_author(&mut b, &who);
    save_baseline(root, &b, "A2")?;
    set_stage(root, "A2", "in_progress", None)?;
    let items = read_jsonl(&ev(root).join("01-COLD-INVENTORY.jsonl"))?;
    let classified = classify::classify_all(root, &items);
    let mut jl = String::new();
    for c in &classified {
        jl.push_str(&serde_json::to_string(c)?);
        jl.push('\n');
    }
    write_text(&ev(root).join("02-CLASSIFICATION.jsonl"), &jl)?;
    write_md(
        root,
        "03-LEGACY-GOVERNANCE-MAP.md",
        &classify::legacy_map_markdown(&classified),
    )?;
    let mut by_class: std::collections::BTreeMap<String, usize> = std::collections::BTreeMap::new();
    let mut by_auth: std::collections::BTreeMap<String, usize> = std::collections::BTreeMap::new();
    for c in &classified {
        *by_class
            .entry(c["class"].as_str().unwrap_or("").into())
            .or_insert(0) += 1;
        *by_auth
            .entry(c["authority"].as_str().unwrap_or("").into())
            .or_insert(0) += 1;
    }
    let unknown = by_class.get("UNKNOWN").copied().unwrap_or(0);
    let conflicting = by_auth.get("UNKNOWN_OR_CONFLICTING").copied().unwrap_or(0);
    set_stage(
        root,
        "A2",
        "done",
        Some((
            "classification_summary",
            json!({"by_class": by_class, "by_authority": by_auth, "unknown": unknown, "conflicting": conflicting}),
        )),
    )?;
    Ok(
        json!({"stage": "A2", "classified": classified.len(), "by_class": by_class, "by_authority": by_auth, "unknown": unknown, "conflicting": conflicting, "evidence": [format!("{EVIDENCE}/02-CLASSIFICATION.jsonl"), format!("{EVIDENCE}/03-LEGACY-GOVERNANCE-MAP.md")]}),
    )
}

fn native_test_dir(root: &Path) -> Option<String> {
    for d in ["tests", "test", "product/tests", "src/tests", "spec"] {
        if root.join(d).is_dir() && d != "spec" {
            return Some(d.into());
        }
    }
    None
}

// ---------------------------------------------------------------- A3
/// The archive root migrations retire material into.
pub const ARCHIVE_ROOT: &str = "archive";
/// Stable ids of the two versioned adoption planning artefacts (BC-P2-21, Contract v3:1080 "migration plans").
pub const CATALOGUE_ID: &str = "PMAP-GOVERNANCE-ADOPTION";
pub const PLAN_ID: &str = "MPLAN-GOVERNANCE-ADOPTION";
const CATALOGUE_STEM: &str = "04-TARGET-PATH-MAP";
const PLAN_STEM: &str = "05-plan";

fn catalogue_meta_path(root: &Path) -> PathBuf {
    ev(root).join(format!("{CATALOGUE_STEM}.meta.json"))
}

fn write_catalogue(root: &Path, catalogue: &[Value]) -> Result<()> {
    let mut jl = String::new();
    for e in catalogue {
        jl.push_str(&serde_json::to_string(e)?);
        jl.push('\n');
    }
    write_text(&ev(root).join(format!("{CATALOGUE_STEM}.jsonl")), &jl)
}

pub fn a3_map(root: &Path) -> Result<Value> {
    a3_map_by(root, &identity::Actor::process())
}

/// A3 with the producing actor recorded in every catalogue entry (W1 producer/provenance). The actor is the one the
/// caller declared ([`identity::resolve_actor`]); a supplied session nobody declared is refused.
pub fn a3_map_by(root: &Path, actor: &identity::Actor) -> Result<Value> {
    let (mut b, who) = begin_stage(root, "map", actor, None)?;
    require_stage(&b, "A2")?;
    record_author(&mut b, &who);
    save_baseline(root, &b, "A3")?;
    let actor = &who.actor.as_actor();
    set_stage(root, "A3", "in_progress", None)?;
    let classified = read_jsonl(&ev(root).join("02-CLASSIFICATION.jsonl"))?;
    // ARCHIVE_POLICY.unused_code_action of the kernel being adopted decides how dead code is treated
    let unused_action = {
        let p0 = Project::open(root);
        if p0.is_installed() {
            p0.policies().get_str(
                "ARCHIVE_POLICY",
                "unused_code_action",
                "remove_from_active_tree",
            )
        } else {
            crate::kernel::resolve_kernel_source(None)
                .ok()
                .and_then(|k| read_yaml(&k.join("policies").join("ARCHIVE_POLICY.yaml")).ok())
                .and_then(|v| v["unused_code_action"].as_str().map(|s| s.to_string()))
                .unwrap_or("remove_from_active_tree".into())
        }
    };
    let mut catalogue = planner::plan(
        root,
        &classified,
        native_test_dir(root).as_deref(),
        &unused_action,
    );
    // Dependency proof for every retirement, from a fresh scan of the tree as it is now (BC-P2-33).
    let index = references::build_fresh(root);
    let os = ownership::OsState::load(root);
    planner::apply_dependency_proofs(&mut catalogue, &index, root, &os, ARCHIVE_ROOT);
    // Stable identity, versions, producer and lineage (BC-P2-21).
    let previous =
        read_jsonl(&ev(root).join(format!("{CATALOGUE_STEM}.jsonl"))).unwrap_or_default();
    let prev_meta = read_json(&catalogue_meta_path(root)).unwrap_or(Value::Null);
    let prev_version = prev_meta["version"].as_u64().unwrap_or(0);
    let ledger = read_jsonl(&ev(root).join("migration-ledger.jsonl")).unwrap_or_default();
    let producer = identity::producer("A3", "gov adopt map", actor);
    let adoption = json!({"adoption_id": b["adoption_id"], "started_at": b["started_at"]});
    planner::finalise_identity(
        &mut catalogue,
        &previous,
        prev_version,
        &ledger,
        &producer,
        prev_version + 1,
        prev_meta["adoption"] == adoption,
    );
    let mut hashes: Vec<(String, String)> = catalogue
        .iter()
        .map(|e| {
            (
                e["artifact_id"].as_str().unwrap_or("").to_string(),
                e["entry_hash"].as_str().unwrap_or("").to_string(),
            )
        })
        .collect();
    hashes.sort();
    let content_hash = identity::content_hash(&json!(hashes));
    let unchanged = prev_meta["content_hash"].as_str() == Some(content_hash.as_str());
    let version = if unchanged {
        prev_version
    } else {
        prev_version + 1
    };
    for e in catalogue.iter_mut() {
        e["catalogue_version"] = json!(version);
    }
    let schemas = Project::open(root).schemas().schema_dir.clone();
    let reg = crate::schemas::SchemaRegistry::new(&schemas);
    let mut problems = vec![];
    for e in &catalogue {
        if reg.has("migration-catalogue-entry") {
            if let Ok(errs) = reg.errors("migration-catalogue-entry", e) {
                for x in errs {
                    problems.push(format!("{}: {x}", e["artifact_id"]));
                }
            }
        }
    }
    write_catalogue(root, &catalogue)?;
    let meta = if unchanged {
        let mut m = prev_meta.clone();
        m["last_regenerated_at"] = json!(now_iso());
        m["adoption"] = adoption.clone();
        m
    } else {
        let history = identity::version_file(&ev(root), CATALOGUE_STEM, version, "jsonl");
        if let Some(d) = history.parent() {
            std::fs::create_dir_all(d)?;
        }
        std::fs::copy(ev(root).join(format!("{CATALOGUE_STEM}.jsonl")), &history)?;
        json!({"id": CATALOGUE_ID, "type": "migration-catalogue", "title": "Adoption target path map (migration catalogue)", "version": version, "content_hash": content_hash,
            "entries": catalogue.len(), "producer": producer, "adoption": adoption,
            "supersedes": if prev_version > 0 { json!([{"version": prev_version, "content_hash": prev_meta["content_hash"], "snapshot": format!("{EVIDENCE}/{CATALOGUE_STEM}.versions/v{prev_version:04}.jsonl")}]) } else { json!([]) },
            "history": format!("{EVIDENCE}/{CATALOGUE_STEM}.versions/"), "created_at": now_iso()})
    };
    write_json(&catalogue_meta_path(root), &meta)?;
    let actions: std::collections::BTreeMap<String, usize> =
        catalogue
            .iter()
            .fold(std::collections::BTreeMap::new(), |mut m, e| {
                *m.entry(e["action"].as_str().unwrap_or("").into())
                    .or_insert(0) += 1;
                m
            });
    let unknown = catalogue
        .iter()
        .filter(|e| e["finding_state"] == "UNKNOWN")
        .count();
    let gated_retirements: Vec<Value> = catalogue
        .iter()
        .filter(|e| {
            e["dependency_proof"]["result"] == "ACTIVE_REFERENCES"
        })
        .map(|e| json!({"artifact_id": e["artifact_id"], "path": e["current_path"], "action": e["action"], "active_references": e["dependency_proof"]["active_references"]}))
        .collect();
    let citations: usize = catalogue
        .iter()
        .map(|e| e["citations"].as_array().map(|a| a.len()).unwrap_or(0))
        .sum();
    set_stage(
        root,
        "A3",
        "done",
        Some((
            "path_map_summary",
            json!({"actions": actions, "unknown": unknown, "catalogue_version": version, "gated_retirements": gated_retirements.len()}),
        )),
    )?;
    Ok(
        json!({"stage": "A3", "entries": catalogue.len(), "actions": actions, "unknown_blocking_destructive": unknown, "schema_problems": problems, "catalogue": {"id": CATALOGUE_ID, "version": version, "content_hash": content_hash, "regenerated_unchanged": unchanged},
            "citations_represented": citations, "retirements_with_active_references": gated_retirements, "evidence": format!("{EVIDENCE}/{CATALOGUE_STEM}.jsonl")}),
    )
}

/// Destructive catalogue entries (RETIRE / DELETE_FROM_ACTIVE_TREE / gated moves) get a Human Decision Gate record
/// each; the executor accepts only ANSWERED (option A), presented gates — never a CLI flag (INV-008, verifier H6).
pub fn ensure_destructive_gates(root: &Path, catalogue: &mut [Value]) -> Result<Vec<String>> {
    let p = Project::open(root);
    if !p.is_installed() {
        return Ok(vec![]);
    }
    let mut created = vec![];
    for e in catalogue.iter_mut() {
        if !e["requires_human_gate"].as_bool().unwrap_or(false) {
            continue;
        }
        if e.get("human_gate")
            .and_then(|v| v.as_str())
            .map(|g| !g.is_empty())
            .unwrap_or(false)
        {
            continue;
        }
        let aid = e["artifact_id"].as_str().unwrap_or("").to_string();
        let action = e["action"].as_str().unwrap_or("").to_string();
        let path = e["current_path"].as_str().unwrap_or("").to_string();
        let reasons: Vec<String> = e["gate_reasons"]
            .as_array()
            .map(|a| {
                a.iter()
                    .filter_map(|x| x.as_str().map(|s| s.to_string()))
                    .collect()
            })
            .unwrap_or_default();
        let dependants: Vec<String> = e["dependency_proof"]["active_references"]
            .as_array()
            .map(|a| {
                a.iter()
                    .map(|r| {
                        format!(
                            "{}:{} ({} {})",
                            r["from"].as_str().unwrap_or(""),
                            r["line"],
                            r["role"].as_str().unwrap_or(""),
                            r["kind"].as_str().unwrap_or("")
                        )
                    })
                    .collect()
            })
            .unwrap_or_default();
        let refs_gate = reasons.iter().any(|r| r == "active_references");
        let question = if refs_gate {
            format!("Adoption migration: {action} {path} ({aid}) although active files still refer to it: {}? {}", dependants.join(", "), e["reason"].as_str().unwrap_or(""))
        } else {
            format!(
                "Adoption migration: {action} {path} ({aid})? {}",
                e["reason"].as_str().unwrap_or("")
            )
        };
        let option_a = if refs_gate {
            format!("approve {action} anyway: the references listed are left exactly as they are (never re-pointed at the archived copy) and reported as dangling until fixed")
        } else {
            format!("approve {action}")
        };
        let option_b = if refs_gate {
            "keep in place: registered LEGACY; remove the references through governed work, then re-run gov adopt map/plan".to_string()
        } else {
            "keep in place (skip this entry)".to_string()
        };
        let g = crate::orchestration::gates::create_system(
            &p,
            json!({"question": question, "why_now": format!("migration action needing a human decision ({})", if reasons.is_empty() { "destructive or structural".to_string() } else { reasons.join(", ") }), "current_state": format!("present at {path}"),
                "options": [{"id": "A", "description": option_a}, {"id": "B", "description": option_b}], "impact": format!("target: {}; dependency proof: {} (dependants digest {})", e["target_path"].as_str().unwrap_or("removed from active tree"), e["dependency_proof"]["result"].as_str().unwrap_or("n/a"), e["dependency_proof"]["dependants_digest"].as_str().unwrap_or("-")),
                "reversibility": "batch snapshot + git history", "recommendation": if refs_gate { "B until the references are removed" } else { "A if no reference or unique data exists" }, "confidence": e["confidence"].as_f64().unwrap_or(0.5), "trigger": "destructive_migration", "impact_radius": "R2", "artifact_id": aid,
                "subject": {"kind": "adoption-catalogue-entry", "id": aid, "sha256": planner::gate_subject_sha256(e)}}),
        )?;
        let gid = g["id"].as_str().unwrap_or("").to_string();
        e["human_gate"] = json!(gid);
        created.push(gid);
    }
    if !created.is_empty() {
        write_catalogue(root, catalogue)?;
    }
    Ok(created)
}

/// The verified answer (`gates::verified_answer`) of the Human Decision Gate raised for catalogue entry `e` — only
/// when that gate was raised for this entry and its recorded subject is still exactly this entry's question
/// (artefact, path, action, target, reasons, dependants: [`planner::gate_subject_sha256`]). A gate id pointed at
/// another entry's answered gate, or an entry changed after its gate was answered, authorises nothing (BC-P2-11 for
/// adoption gates).
pub fn entry_gate_answer(p: &Project, e: &Value) -> Option<String> {
    let g = e["human_gate"].as_str().filter(|g| !g.is_empty())?;
    let a = crate::orchestration::gates::verified_answer(p, g).ok()?;
    let d = &a.record.data;
    if d["artifact_id"] != e["artifact_id"] || d["trigger"] != "destructive_migration" {
        return None;
    }
    if let Some(sha) = d["subject"]["sha256"].as_str() {
        if sha != planner::gate_subject_sha256(e) {
            return None;
        }
    }
    Some(a.option)
}

/// Artefact ids whose destructive gate has been presented and answered with option A.
pub fn answered_destructive(root: &Path, catalogue: &[Value]) -> Vec<String> {
    let p = Project::open(root);
    if !p.is_installed() {
        return vec![];
    }
    catalogue
        .iter()
        .filter(|e| e["requires_human_gate"].as_bool().unwrap_or(false))
        .filter(|e| entry_gate_answer(&p, e).as_deref() == Some("A"))
        .filter_map(|e| e["artifact_id"].as_str().map(|s| s.to_string()))
        .collect()
}

// ---------------------------------------------------------------- A4
pub fn a4_plan(root: &Path) -> Result<Value> {
    a4_plan_by(root, &identity::Actor::process())
}

/// The downstream consumers the migration plan declares (W1 "expected consumers", Contract v3:1076-1078). They are
/// stage artefacts (a stage, the role acting in it and the evidence file it reads the plan into), not governed records,
/// so the plan declares them under `expected_consumers`: `consumers` is the record relation field whose every entry is
/// the id of a record that consumes this one (`<id> CONSUMES <plan>`, `record.schema.json`; BC-P2-21 edge semantics).
fn plan_consumers() -> Value {
    json!([
        {"stage": "A5", "role": "independent migration reviewer / test author", "artefact": format!("{EVIDENCE}/06-migration-tests.yaml")},
        {"stage": "A6", "role": "migration executor", "artefact": format!("{EVIDENCE}/07-MIGRATION-EXECUTION-REPORT.md")},
        {"stage": "A6", "role": "migration executor", "artefact": format!("{EVIDENCE}/migration-ledger.jsonl")},
        {"stage": "A7", "role": "independent migration verifier", "artefact": format!("{EVIDENCE}/08-INDEPENDENT-MIGRATION-VERIFICATION.md")}
    ])
}

/// A4 with W1 identity: the plan is one artefact (`MPLAN-GOVERNANCE-ADOPTION`) with a type, status, content hash,
/// version, producer, declared consumers and supersession lineage; every version is kept in `05-plan.versions/`, so
/// re-planning never overwrites the plan a reviewer approved (BC-P2-21; Contract v3:1069-1080).
pub fn a4_plan_by(root: &Path, actor: &identity::Actor) -> Result<Value> {
    let (mut b, who) = begin_stage(root, "plan", actor, None)?;
    require_stage(&b, "A3")?;
    record_author(&mut b, &who);
    save_baseline(root, &b, "A4")?;
    let actor = &who.actor.as_actor();
    set_stage(root, "A4", "in_progress", None)?;
    let mut catalogue = read_jsonl(&ev(root).join(format!("{CATALOGUE_STEM}.jsonl")))?;
    let gates_created = ensure_destructive_gates(root, &mut catalogue)?;
    let batches = planner::batches(&catalogue);
    let unknown = catalogue
        .iter()
        .filter(|e| e["finding_state"] == "UNKNOWN")
        .count();
    let cat_meta = read_json(&catalogue_meta_path(root)).unwrap_or(Value::Null);
    let gated: Vec<Value> = catalogue
        .iter()
        .filter(|e| e["requires_human_gate"].as_bool().unwrap_or(false))
        .map(|e| json!({"artifact_id": e["artifact_id"], "path": e["current_path"], "action": e["action"], "gate_reasons": e["gate_reasons"], "dependants_digest": e["dependency_proof"]["dependants_digest"]}))
        .collect();
    let catalogue_ref = json!({"id": CATALOGUE_ID, "version": cat_meta["version"], "content_hash": cat_meta["content_hash"], "path": format!("{EVIDENCE}/{CATALOGUE_STEM}.jsonl")});
    let content = json!({"batches": batches, "unknown_blocking": unknown, "catalogue": catalogue_ref, "gated_entries": gated});
    let content_hash = identity::content_hash(&content);
    let plan_path = ev(root).join(format!("{PLAN_STEM}.yaml"));
    let prev = read_yaml(&plan_path).ok().filter(|v| v["id"] == PLAN_ID);
    let prev_version = prev
        .as_ref()
        .and_then(|p| p["version"].as_u64())
        .unwrap_or(0);
    let unchanged = prev
        .as_ref()
        .map(|p| p["content_hash"].as_str() == Some(content_hash.as_str()))
        .unwrap_or(false);
    let plan = if unchanged {
        let mut p = prev.clone().unwrap();
        p["last_regenerated_at"] = json!(now_iso());
        p["last_regenerated_by"] = identity::producer("A4", "gov adopt plan", actor);
        p
    } else {
        let version = prev_version + 1;
        // the previous version stays retrievable, marked superseded by this one
        if prev_version > 0 {
            let snap = identity::version_file(&ev(root), PLAN_STEM, prev_version, "json");
            let mut old = read_json(&snap).unwrap_or_else(|_| prev.clone().unwrap_or(Value::Null));
            old["status"] = json!("SUPERSEDED");
            old["superseded_by"] = json!(format!("{PLAN_ID}@v{version}"));
            old["superseded_by_detail"] = json!({"version": version, "content_hash": content_hash});
            write_json(&snap, &old)?;
        }
        let mut p = json!({"id": PLAN_ID, "type": "migration-plan", "title": "Adoption/migration plan", "status": "ACTIVE", "state_class": "DERIVED",
            "version": version, "content_hash": content_hash, "producer": identity::producer("A4", "gov adopt plan", actor), "expected_consumers": plan_consumers(),
            "supersedes": if prev_version > 0 { json!([format!("{PLAN_ID}@v{prev_version}")]) } else { json!([]) },
            "supersedes_detail": if prev_version > 0 { json!([{"version": prev_version, "content_hash": prev.as_ref().map(|p| p["content_hash"].clone()).unwrap_or(Value::Null), "snapshot": format!("{EVIDENCE}/{PLAN_STEM}.versions/v{prev_version:04}.json")}]) } else { json!([]) },
            "history": format!("{EVIDENCE}/{PLAN_STEM}.versions/"), "created_at": now_iso()});
        for (k, v) in content.as_object().unwrap() {
            p[k] = v.clone();
        }
        p
    };
    let version = plan["version"].as_u64().unwrap_or(1);
    let snap = identity::version_file(&ev(root), PLAN_STEM, version, "json");
    if let Some(d) = snap.parent() {
        std::fs::create_dir_all(d)?;
    }
    if !unchanged || !snap.exists() {
        write_json(&snap, &plan)?;
    }
    write_yaml(&plan_path, &plan)?;
    write_md(
        root,
        "05-ADOPTION-MIGRATION-PLAN.md",
        &format!(
            "{}\n## Identity\n\n- id: `{PLAN_ID}` (type migration-plan), version {version}, content hash `{}`\n- catalogue: `{CATALOGUE_ID}` version {}\n- history: `{EVIDENCE}/{PLAN_STEM}.versions/`\n",
            planner::plan_markdown(&catalogue, &batches, unknown),
            &content_hash[..16],
            cat_meta["version"]
        ),
    )?;
    set_stage(root, "A4", "done", None)?;
    Ok(
        json!({"stage": "A4", "plan": {"id": PLAN_ID, "version": version, "content_hash": content_hash, "regenerated_unchanged": unchanged}, "batches": batches.iter().map(|b| json!({"batch": b["batch"], "entries": b["entries"], "human_gate": b["requires_human_gate"]})).collect::<Vec<_>>(), "human_gates_created": gates_created, "evidence": [format!("{EVIDENCE}/05-ADOPTION-MIGRATION-PLAN.md"), format!("{EVIDENCE}/{PLAN_STEM}.yaml")]}),
    )
}

// ---------------------------------------------------------------- A5
/// The planner's scaffold for the current catalogue (deterministic: the same catalogue yields the same tests).
fn scaffold_for(root: &Path, b: &Value, catalogue: &[Value]) -> Value {
    let legacy: Vec<String> = classify::legacy_mechanisms(root)
        .into_iter()
        .map(|l| l.path)
        .collect();
    let cmd = b["baseline_tests"]["command"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect::<Vec<_>>()
        })
        .filter(|c| !c.is_empty() && b["baseline_tests"]["status"] == "passed")
        .map(|c| {
            (
                c,
                b["baseline_tests"]["dir"]
                    .as_str()
                    .unwrap_or("")
                    .to_string(),
            )
        });
    verify::scaffold_tests(catalogue, &legacy, cmd)
}

/// Adoption stages whose designated role's protocol duty is to execute the approved independent tests (adoption
/// protocol §3, Role D: "verifies the actual migrated repo and independently runs/extends tests").
const TEST_EXECUTION_DUTY: &[&str] = &["A7"];

/// The permission classes `role` holds for running tests at `stage`: its TOOL_PERMISSIONS entry (`listed`, read from
/// `source`) when the policy lists the role — an explicit entry decides, even an empty one; otherwise the classes the
/// adoption protocol's designated duty of `stage` needs, for its designated role only; otherwise none.
fn test_permissions(
    listed: Option<Vec<String>>,
    stage: &str,
    role: &str,
    source: &str,
) -> (Vec<String>, String) {
    match listed {
        Some(v) => (v, format!("TOOL_PERMISSIONS.roles.{role} ({source})")),
        None if TEST_EXECUTION_DUTY.contains(&stage) && designated_role(stage) == Some(role) => (
            vec!["READ_REPO".to_string(), verify::COMMAND_TEST_PERMISSION.to_string()],
            format!("adoption protocol: {stage} is performed by its designated role '{role}', whose duty is to run the approved independent tests (TOOL_PERMISSIONS does not list the role)"),
        ),
        None => (
            vec![],
            format!("TOOL_PERMISSIONS lists no permission classes for role '{role}'"),
        ),
    }
}

/// What a `command` migration test may execute when `role` runs the tests at `stage` (Contract v3 A3; see
/// `verify::CommandPolicy`): the project's governed test commands, and the permission classes of the executing role —
/// its `TOOL_PERMISSIONS.roles` entry (the installed overlay, or the template the first install writes) when the policy
/// lists it; for an unlisted role, the classes its designated adoption duty needs (A7: `READ_REPO`, `RUN_TESTS`).
fn command_policy(root: &Path, b: &Value, stage: &str, role: &str) -> verify::CommandPolicy {
    let p = Project::open(root);
    let listed: Option<Vec<String>> = {
        let doc = if p.is_installed() {
            p.overlay().get("TOOL_PERMISSIONS.yaml")
        } else {
            crate::kernel::embedded::files()
                .iter()
                .find(|(r, _)| *r == "overlay-templates/TOOL_PERMISSIONS.yaml")
                .and_then(|(_, bytes)| serde_yaml::from_slice::<Value>(bytes).ok())
                .unwrap_or(Value::Null)
        };
        doc["roles"].get(role).map(|v| {
            v.as_array()
                .map(|a| {
                    a.iter()
                        .filter_map(|x| x.as_str().map(String::from))
                        .collect()
                })
                .unwrap_or_default()
        })
    };
    let (permissions, basis) = test_permissions(
        listed,
        stage,
        role,
        if p.is_installed() {
            "governance/project/TOOL_PERMISSIONS.yaml"
        } else {
            "the kernel template the first install writes"
        },
    );
    verify::CommandPolicy {
        stage: stage.to_string(),
        role: role.to_string(),
        permissions,
        permission_basis: basis,
        governed: verify::governed_test_commands(root, b),
    }
}

fn test_identities(tests: &Value) -> Vec<String> {
    tests["tests"]
        .as_array()
        .map(|a| a.iter().map(verify::test_identity).collect())
        .unwrap_or_default()
}

pub fn a5_test_design(root: &Path) -> Result<Value> {
    a5_test_design_by(root, &identity::Actor::process())
}

/// A5 scaffold (Role A): the planner derives tests from the plan for the independent reviewer to review and extend.
/// Every scaffold this adoption generated is recorded (by test identity), so the scaffold is never counted as the
/// reviewer's own tests (O3: builder tests are regression evidence).
pub fn a5_test_design_by(root: &Path, actor: &identity::Actor) -> Result<Value> {
    let (mut b, who) = begin_stage(root, "test-design", actor, None)?;
    require_stage(&b, "A4")?;
    let catalogue = read_jsonl(&ev(root).join("04-TARGET-PATH-MAP.jsonl"))?;
    let tests = scaffold_for(root, &b, &catalogue);
    let path = ev(root).join("06-migration-tests.yaml");
    if !path.exists() {
        write_yaml(&path, &tests)?;
    }
    // the plan and the independent tests must agree on every artefact's disposition (Contract v3:928-929)
    let current = read_yaml(&path).unwrap_or(tests.clone());
    let conflicts = verify::plan_test_agreement(&catalogue, &current);
    let md = format!("# 06 — Independent migration test design\n\nAuthored by a fresh independent session (Role B). Scaffold generated by the planner; the reviewer must review classification, target map, destructive moves, unknown items, references/imports, authority changes, archive/delete decisions and old memory stores, then extend `06-migration-tests.yaml` with tests of their own and record a verdict with `gov adopt review` (as `migration-reviewer`, in a fresh session). Scaffolded tests are the planner's regression evidence; an approval requires at least one reviewer-authored test.\n\nTest families: path integrity · code integrity · governance integrity · behaviour preservation · rollback/recovery.\n\nScaffolded tests: {}\n\n## Verdicts\n\n", tests["tests"].as_array().map(|a| a.len()).unwrap_or(0));
    let p = ev(root).join("06-INDEPENDENT-MIGRATION-TEST-DESIGN.md");
    if !p.exists() {
        write_text(&p, &md)?;
    }
    let mut known: Vec<String> = b["test_design"]["scaffold_identities"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(String::from))
                .collect()
        })
        .unwrap_or_default();
    // the planner's: the scaffold it generated now, and every test the file holds when the planner runs test-design —
    // except tests an earlier independent approval recorded as the reviewer's own
    let reviewers: Vec<String> = b["verdicts"]["A5"]["reviewer_test_identities"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(String::from))
                .collect()
        })
        .unwrap_or_default();
    for i in test_identities(&tests)
        .into_iter()
        .chain(test_identities(&current))
    {
        if !known.contains(&i) && !reviewers.contains(&i) {
            known.push(i);
        }
    }
    b["test_design"] = json!({"scaffold_identities": known, "scaffold_sha256": verify::tests_digest(&tests), "scaffold_tests": tests["tests"].as_array().map(|a| a.len()).unwrap_or(0),
        "by": verdict_actor(&who), "at": now_iso()});
    record_author(&mut b, &who);
    save_baseline(root, &b, "A5 test-design")?;
    Ok(
        json!({"stage": "A5", "tests_file": format!("{EVIDENCE}/06-migration-tests.yaml"), "scaffolded_tests": tests["tests"].as_array().map(|a| a.len()).unwrap_or(0), "plan_test_disagreements": conflicts, "next": "the independent reviewer (role migration-reviewer, fresh session) reviews the plan, adds tests of their own to 06-migration-tests.yaml and runs `gov adopt review --verdict MIGRATION_PLAN_APPROVED`"}),
    )
}

pub fn a5_review(
    root: &Path,
    verdict: &str,
    reviewer_session: &str,
    reviewer_role: &str,
    notes: Option<&str>,
) -> Result<Value> {
    a5_review_by(
        root,
        verdict,
        &identity::Actor::supplied(reviewer_session, Some(reviewer_role)),
        notes,
    )
}

/// **A5 independent review (Role B).** Performed only by `migration-reviewer` in a fresh declared session. An
/// approval requires tests the reviewer authored (tests whose identity is not in any planner scaffold of this
/// adoption), all of an executable kind, agreeing with the plan; it binds the digests of the catalogue, plan and test
/// file it approved, which A6 and A7 enforce.
pub fn a5_review_by(
    root: &Path,
    verdict: &str,
    actor: &identity::Actor,
    notes: Option<&str>,
) -> Result<Value> {
    if ![
        "MIGRATION_PLAN_APPROVED",
        "MIGRATION_PLAN_APPROVED_WITH_AMENDMENTS",
        "MIGRATION_PLAN_REJECTED",
    ]
    .contains(&verdict)
    {
        return Err(GovError::new("USAGE", "verdict must be MIGRATION_PLAN_APPROVED | MIGRATION_PLAN_APPROVED_WITH_AMENDMENTS | MIGRATION_PLAN_REJECTED"));
    }
    let (b, who) = begin_stage(root, "review", actor, Some("--reviewer-session"))?;
    require_stage(&b, "A4")?;
    if !ev(root).join("06-migration-tests.yaml").exists() || !b["test_design"].is_object() {
        return Err(GovError::new("VERDICT_REQUIRED", "independent tests file 06-migration-tests.yaml or its recorded scaffold missing; run `gov adopt test-design` (planner) and author tests before a verdict"));
    }
    let tests = read_yaml(&ev(root).join("06-migration-tests.yaml"))?;
    let n = tests["tests"].as_array().map(|a| a.len()).unwrap_or(0);
    let catalogue = read_jsonl(&ev(root).join(format!("{CATALOGUE_STEM}.jsonl")))?;
    // what the planner generated (every scaffold of this adoption, and the scaffold of the catalogue as it is now)
    let mut scaffold: Vec<String> = b["test_design"]["scaffold_identities"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(String::from))
                .collect()
        })
        .unwrap_or_default();
    let latest = scaffold_for(root, &b, &catalogue);
    scaffold.extend(test_identities(&latest));
    let all: Vec<Value> = tests["tests"].as_array().cloned().unwrap_or_default();
    let reviewer_tests: Vec<&Value> = all
        .iter()
        .filter(|t| !scaffold.contains(&verify::test_identity(t)))
        .collect();
    let scaffold_kept = all.len() - reviewer_tests.len();
    let approved = verdict.starts_with("MIGRATION_PLAN_APPROVED");
    if approved {
        let conflicts = verify::plan_test_agreement(&catalogue, &tests);
        if !conflicts.is_empty() {
            return Err(GovError::new(
                "PLAN_TEST_DISAGREEMENT",
                format!("{} independent test(s) contradict the plan's disposition of an artefact; a plan cannot be approved against tests that contradict it — amend the plan (gov adopt map/plan) or the tests, or record MIGRATION_PLAN_REJECTED", conflicts.len()),
            )
            .with_details(json!({"conflicts": conflicts})));
        }
        if reviewer_tests.is_empty() {
            return Err(GovError::new(
                "INDEPENDENT_TESTS_REQUIRED",
                format!("an approval records the independent reviewer's own acceptance tests (adoption protocol §10: the reviewer authors tests before execution; Contract v3 O3: builder tests are regression evidence), but all {n} test(s) in 06-migration-tests.yaml are the planner's scaffold"),
            )
            .with_details(json!({"tests": n, "scaffold_tests": scaffold_kept, "remediation": "add tests of your own to spec/audits/GOVERNANCE-ADOPTION/06-migration-tests.yaml (path/code/governance integrity, behaviour preservation, rollback), then record the verdict", "test_kinds": verify::TEST_KINDS})));
        }
        let invalid: Vec<Value> = reviewer_tests
            .iter()
            .filter(|t| {
                !verify::TEST_KINDS.contains(&t["kind"].as_str().unwrap_or(""))
                    || t["id"]
                        .as_str()
                        .map(|x| x.trim().is_empty())
                        .unwrap_or(true)
            })
            .map(|t| json!({"id": t["id"], "kind": t["kind"]}))
            .collect();
        // Contract v3 A3: an approval never binds a command test the executing stages may not run. A7's designated
        // verifier executes every approved test; A6 re-checks against its own executor before anything moves.
        verify::refuse_unpermitted_command_tests(
            &tests,
            &command_policy(root, &b, "A7", designated_role("A7").unwrap_or("")),
            "adopt review (approval)",
        )?;
        if !invalid.is_empty() {
            return Err(GovError::new(
                "INDEPENDENT_TESTS_INVALID",
                format!("{} reviewer-authored test(s) have no id or a kind the executor cannot run; a test that cannot run cannot pass", invalid.len()),
            )
            .with_details(json!({"invalid": invalid, "test_kinds": verify::TEST_KINDS})));
        }
    }
    let bound = current_bindings(root)?;
    let plan = read_yaml(&ev(root).join(format!("{PLAN_STEM}.yaml"))).unwrap_or(Value::Null);
    let reviewer_ids: Vec<Value> = reviewer_tests.iter().map(|t| t["id"].clone()).collect();
    // scaffold tests the reviewer removed are recorded (visible to A7/A11), never silently dropped
    let present: Vec<String> = all.iter().map(verify::test_identity).collect();
    let removed: Vec<Value> = latest["tests"]
        .as_array()
        .cloned()
        .unwrap_or_default()
        .iter()
        .filter(|t| !present.contains(&verify::test_identity(t)))
        .map(|t| t["id"].clone())
        .collect();
    let mut entry = verdict_actor(&who);
    for (k, v) in json!({"verdict": verdict, "at": now_iso(), "tests": n, "notes": notes, "reviewer_tests": reviewer_ids, "reviewer_tests_count": reviewer_tests.len(),
        "reviewer_test_identities": reviewer_tests.iter().map(|t| verify::test_identity(t)).collect::<Vec<_>>(),
        "scaffold_tests": scaffold_kept, "scaffold_tests_removed": removed,
        "catalogue_sha256": bound["catalogue_sha256"], "catalogue_version": read_json(&catalogue_meta_path(root)).map(|m| m["version"].clone()).unwrap_or(Value::Null),
        "plan_id": plan["id"], "plan_version": plan["version"], "plan_sha256": bound["plan_sha256"], "tests_sha256": bound["tests_sha256"],
        "independence": who.independence}).as_object().unwrap() {
        entry[k] = v.clone();
    }
    let mut md =
        read_text(&ev(root).join("06-INDEPENDENT-MIGRATION-TEST-DESIGN.md")).unwrap_or_default();
    md.push_str(&format!("- {} — **{verdict}** by {} (session {}), {n} tests of which {} authored by the reviewer; bound to catalogue `{}`, plan `{}`, tests `{}`. {}\n", now_iso(), who.role(), who.session(), reviewer_tests.len(),
        &bound["catalogue_sha256"].as_str().unwrap_or("")[..12.min(bound["catalogue_sha256"].as_str().unwrap_or("").len())],
        &bound["plan_sha256"].as_str().unwrap_or("")[..12.min(bound["plan_sha256"].as_str().unwrap_or("").len())],
        &bound["tests_sha256"].as_str().unwrap_or("")[..12.min(bound["tests_sha256"].as_str().unwrap_or("").len())], notes.unwrap_or("")));
    write_text(
        &ev(root).join("06-INDEPENDENT-MIGRATION-TEST-DESIGN.md"),
        &md,
    )?;
    let mut b2 = b.clone();
    b2["verdicts"]["A5"] = entry.clone();
    b2["stage_status"]["A5"] = json!(if verdict == "MIGRATION_PLAN_REJECTED" {
        "rejected"
    } else {
        "done"
    });
    b2["stage_times"]["A5"] = json!(now_iso());
    record_author(&mut b2, &who);
    save_baseline(root, &b2, "A5 review")?;
    Ok(json!({"stage": "A5", "verdict": entry}))
}

// ---------------------------------------------------------------- A6
fn brownfield_contract(
    root: &Path,
    kernel_dir: &Path,
    classified: &[Value],
    catalogue: &[Value],
) -> Result<Value> {
    let mut c = read_yaml(
        &kernel_dir
            .join("overlay-templates")
            .join("REPOSITORY_CONTRACT.yaml"),
    )?;
    let mut extra = vec![];
    let mut src_dirs: std::collections::BTreeSet<String> = std::collections::BTreeSet::new();
    let mut test_dirs: std::collections::BTreeSet<String> = std::collections::BTreeSet::new();
    let mut secret_paths: Vec<String> = vec![];
    for e in classified {
        let path = e["path"].as_str().unwrap_or("");
        let top = path.split('/').next().unwrap_or("").to_string();
        if top.is_empty() || !path.contains('/') {
            continue;
        }
        match e["class"].as_str().unwrap_or("") {
            "PRODUCT_SOURCE" | "DEAD_OR_UNUSED" => {
                if !["spec", "governance", "archive", "product", "docs"].contains(&top.as_str()) {
                    src_dirs.insert(top);
                }
            }
            "PRODUCT_TEST" => {
                if !["spec", "governance", "archive", "product", "docs"].contains(&top.as_str()) {
                    test_dirs.insert(top);
                }
            }
            _ => {}
        }
    }
    // Everything carrying secret material is classified secret wherever it is now and wherever the plan retires it
    // to (a secret-bearing legacy store keeps its protection in the archive).
    for e in classified {
        let path = e["path"].as_str().unwrap_or("");
        if !path.is_empty()
            && (e["class"] == "SECRET" || e["sensitivity"] == "secret")
            && !secret_paths.contains(&path.to_string())
        {
            secret_paths.push(path.to_string());
        }
    }
    for e in catalogue.iter().filter(|e| e["sensitivity"] == "secret") {
        for k in ["current_path", "target_path"] {
            if let Some(t) = e[k].as_str().filter(|t| !t.is_empty() && !t.ends_with('/')) {
                if !secret_paths.contains(&t.to_string()) {
                    secret_paths.push(t.to_string());
                }
            }
        }
    }
    for d in &test_dirs {
        extra.push(json!({"pattern": format!("{d}/**"), "class": "test", "owner_role": "independent-test-designer", "semantic_index": true, "lexical_index": true, "graph_index": true, "code_index": true, "namespace": "product"}));
    }
    for d in &src_dirs {
        if test_dirs.contains(d) {
            continue;
        }
        extra.push(json!({"pattern": format!("{d}/**"), "class": "source", "owner_role": "backend-engineer", "semantic_index": true, "lexical_index": true, "graph_index": true, "code_index": true, "namespace": "product"}));
    }
    for s in &secret_paths {
        extra.push(json!({"pattern": s, "class": "secret", "semantic_index": false, "lexical_index": false, "graph_index": false, "code_index": false, "agent_read": "prohibited", "export": "denied", "namespace": "secret"}));
    }
    if let Some(arr) = c["paths"].as_array_mut() {
        let secrets_at_end: Vec<Value> = extra
            .iter()
            .filter(|r| r["class"] == "secret")
            .cloned()
            .collect();
        let others: Vec<Value> = extra
            .iter()
            .filter(|r| r["class"] != "secret")
            .cloned()
            .collect();
        let mut merged = others;
        merged.extend(arr.clone());
        merged.extend(secrets_at_end);
        *arr = merged;
    }
    c["capability_roots"] = json!({"native_source": src_dirs, "native_tests": test_dirs});
    let _ = root;
    Ok(c)
}

pub fn a6_migrate(
    root: &Path,
    batch: Option<i64>,
    source: Option<&str>,
    gate_answers: &[String],
    project_name: &str,
    alias: &str,
    session: &str,
) -> Result<Value> {
    a6_migrate_by(
        root,
        batch,
        source,
        gate_answers,
        project_name,
        alias,
        &identity::Actor::supplied(session, None),
    )
}

/// **A6 controlled migration (Role C).** Executes only the plan the independent reviewer approved: the catalogue,
/// plan and tests must be exactly those the A5 approval bound (`APPROVAL_STALE` otherwise). Health tiers: the G0
/// guard (`scheduler::guard`, operation `adopt.migrate`) before any batch of an installed project, and G4 (wider
/// staleness after migration changes) once the migration is complete.
pub fn a6_migrate_by(
    root: &Path,
    batch: Option<i64>,
    source: Option<&str>,
    gate_answers: &[String],
    project_name: &str,
    alias: &str,
    actor: &identity::Actor,
) -> Result<Value> {
    let (b, who) = begin_stage(root, "migrate", actor, None)?;
    let session = who.session();
    require_stage(&b, "A4")?;
    require_verdict(
        &b,
        "A5",
        &[
            "MIGRATION_PLAN_APPROVED",
            "MIGRATION_PLAN_APPROVED_WITH_AMENDMENTS",
        ],
    )?;
    let approved = require_approved_artefacts(root, &b, "adopt migrate")?;
    {
        let p0 = Project::open(root);
        if p0.is_installed() {
            crate::orchestration::control::guard_write(&p0, "adopt migrate")?;
            crate::authority::require(&p0, "migrate_execute")?;
        }
    }
    // the approved plan and its independent tests must agree before anything executes (Contract v3:928-929)
    if let Ok(t) = read_yaml(&ev(root).join("06-migration-tests.yaml")) {
        let cat0 = read_jsonl(&ev(root).join(format!("{CATALOGUE_STEM}.jsonl")))?;
        let conflicts = verify::plan_test_agreement(&cat0, &t);
        if !conflicts.is_empty() {
            return Err(GovError::new(
                "PLAN_TEST_DISAGREEMENT",
                format!("{} independent test(s) contradict the plan; nothing executed (a batch run against contradicting tests can only fail and roll back) — amend and re-review", conflicts.len()),
            )
            .with_details(json!({"conflicts": conflicts})));
        }
        // Contract v3 A3: every command test the batches will run must be one this executor may run
        verify::refuse_unpermitted_command_tests(
            &t,
            &command_policy(root, &b, "A6", &who.role()),
            "adopt migrate",
        )?;
    }
    let deprecated_flag_note = if gate_answers.is_empty() {
        Value::Null
    } else {
        json!(format!("--gate-answer {:?} ignored: a destructive entry executes only when its Human Decision Gate record is presented and answered (gov gate present / gov decide)", gate_answers))
    };
    let mut catalogue = read_jsonl(&ev(root).join("04-TARGET-PATH-MAP.jsonl"))?;
    let classified = read_jsonl(&ev(root).join("02-CLASSIFICATION.jsonl"))?;
    let plan = read_yaml(&ev(root).join("05-plan.yaml"))?;
    let batches: Vec<i64> = match batch {
        Some(n) => vec![n],
        None => plan["batches"]
            .as_array()
            .map(|a| a.iter().filter_map(|x| x["batch"].as_i64()).collect())
            .unwrap_or_default(),
    };
    // G0 (tier contract): an active hard-block governing `adopt.migrate` refuses before anything moves
    let touched: Vec<String> = catalogue
        .iter()
        .filter(|e| {
            e["batch"]
                .as_i64()
                .map(|n| batches.contains(&n))
                .unwrap_or(false)
                && e["action"] != "KEEP_IN_PLACE"
        })
        .flat_map(|e| {
            [e["current_path"].as_str(), e["target_path"].as_str()]
                .into_iter()
                .flatten()
                .filter(|x| !x.is_empty())
                .map(String::from)
                .collect::<Vec<_>>()
        })
        .collect();
    {
        let p0 = Project::open(root);
        if p0.is_installed() {
            crate::scheduler::guard(
                &p0,
                crate::scheduler::catalogue::ops::ADOPT_MIGRATE,
                &touched,
            )?;
        }
    }
    let ledger = ev(root).join("migration-ledger.jsonl");
    let tests_file = ev(root).join("06-migration-tests.yaml");
    let mut report = read_text(&ev(root).join("07-MIGRATION-EXECUTION-REPORT.md")).unwrap_or_else(|_| "# 07 — Migration execution report\n\nExecutor: Role C. Each batch: checkpoint → execute → update references → independent-authored tests + affected product tests → evidence → ledger.\n\n".into());
    let mut results = vec![];
    let mut b2 = b.clone();
    b2["executor_session"] = json!(session);
    b2["stage_status"]["A6"] = json!("in_progress");
    record_author(&mut b2, &who);
    save_baseline(root, &b2, "A6")?;
    let unknown = catalogue
        .iter()
        .filter(|e| e["finding_state"] == "UNKNOWN")
        .count();
    for n in batches {
        let mut entry = json!({"batch": n, "at": now_iso()});
        if n == 0 {
            let src = resolve_kernel_source(source.map(Path::new))?;
            let gov = root.join("governance");
            std::fs::create_dir_all(&gov)?;
            // Privileged lifecycle ingress `adopt`: the one verification policy. Brownfield adoption installs a
            // kernel exactly like `init` does, so it is admitted through the same verifier and bound by the same
            // floors (ARCH-0003 §3.6; OWNER-DECISION-0006 §9).
            let mut adopt_auth: Option<crate::srr::AuthenticatedRelease> = None;
            let manifest = if root.join("governance/framework.lock").exists() {
                crate::kernel::read_manifest(&gov.join("kernel"))?
            } else {
                let a = crate::srr::admit(
                    crate::srr::AdmissionRequest::new(crate::srr::Ingress::Adopt, &src)
                        .with_reason(Some("gov adopt migrate (batch 0)".into())),
                )?;
                let m = install_kernel(&a, &gov)?;
                adopt_auth = Some(a);
                m
            };
            if !root.join("governance/framework.lock").exists() {
                let consumer_commit = Project::open(root).git_commit();
                let release_commit = crate::kernel::release_commit_for_source(&src);
                write_lock(
                    &gov.join("framework.lock"),
                    &manifest,
                    &crate::kernel::source_label(&src),
                    Some(&release_commit),
                    Some(&consumer_commit),
                )?;
            }
            let contract = brownfield_contract(root, &gov.join("kernel"), &classified, &catalogue)?;
            let opts = crate::init::InitOptions {
                source: None,
                project_name: project_name.into(),
                alias: alias.into(),
                mode: "adopt".into(),
                force: false,
                intent: None,
                skip_index: true,
                channel: None,
                break_glass: false,
            };
            let written =
                crate::init::write_overlay(root, &gov.join("kernel"), &opts, Some(contract))?;
            crate::init::ensure_roots(root)?;
            let mut p = Project::open(root);
            p.invalidate();
            crate::tools::generate_registry(&p)?;
            crate::adapters::generate(&p)?;
            let gates_created = ensure_destructive_gates(root, &mut catalogue)?;
            // Transaction step (9): floors advance only after the install is committed and verified (SRR-R0-L5).
            let protected = match adopt_auth.as_ref() {
                Some(a) => crate::srr::record_installed(a)?,
                None => Value::Null,
            };
            entry["installed"] = json!({"version": manifest["version"], "overlay_written": written, "destructive_gates_created": gates_created, "release_authenticity": adopt_auth.as_ref().map(|a| a.to_value()), "protected_state": protected});
        } else {
            if n >= 6 && unknown > 0 {
                return Err(GovError::new(
                    "UNKNOWN_BLOCKS_DESTRUCTIVE",
                    format!(
                        "{unknown} UNKNOWN artefact(s) block destructive batch {n} (protocol §8)"
                    ),
                ));
            }
            let p = Project::open(root);
            if p.is_installed() {
                crate::orchestration::control::guard_write(&p, "adopt migrate")?;
                let db = RuntimeDb::open(&p.db_path())?;
                db.init_schema()?;
                let _ = crate::checkpoints::create(
                    &p,
                    &db,
                    json!({"trigger": "significant_mutation", "next_action": format!("execute migration batch {n}"), "last_completed_step": format!("pre-batch {n} checkpoint")}),
                );
            }
            let _ = ensure_destructive_gates(root, &mut catalogue)?;
            let answered = answered_destructive(root, &catalogue);
            let ctx = executor::BatchContext {
                archive_root: ARCHIVE_ROOT.into(),
                catalogue_version: read_json(&catalogue_meta_path(root))
                    .map(|m| m["version"].clone())
                    .unwrap_or(Value::Null),
                plan_version: plan["version"].clone(),
                scanner: scanner_for(root),
            };
            let mut r = executor::apply_batch(root, &catalogue, n, &answered, &ledger, &ctx)?;
            {
                let pj = Project::open(root);
                for sk in r.skipped.iter_mut() {
                    let aid = sk["artifact_id"].as_str().unwrap_or("").to_string();
                    if let Some(e) = catalogue
                        .iter()
                        .find(|e| e["artifact_id"].as_str() == Some(&aid))
                    {
                        if let Some(g) = e["human_gate"].as_str() {
                            match entry_gate_answer(&pj, e).as_deref() {
                                Some("A") => {}
                                Some(o) => {
                                    sk["reason"] = json!(format!(
                                        "human gate {g} answered {o}: kept in place by decision"
                                    ));
                                    sk["gate"] = json!(g);
                                }
                                None => {
                                    sk["reason"] = json!(format!("human gate {g} pending (present it in chat and decide; a CLI flag is not an answer)"));
                                    sk["gate"] = json!(g);
                                }
                            }
                        }
                    }
                }
            }
            entry["applied"] = json!(r.applied.len());
            entry["moves"] = json!(r.moves);
            entry["created"] = json!(r.created);
            entry["references_updated"] = json!(r.references_updated);
            entry["skipped"] = json!(r.skipped);
            entry["blocked"] = json!(r.blocked);
            entry["retired_with_active_references"] = json!(r.retired_with_active_references);
        }
        // post-batch tests
        let mut tests = json!({"ran": false});
        if tests_file.exists() {
            let t = verify::run_tests_file_as(
                root,
                &tests_file,
                Some(n),
                &command_policy(root, &b, "A6", &who.role()),
            )?;
            tests = t.clone();
            if !t["ok"].as_bool().unwrap_or(false) && n > 0 {
                let rb = executor::rollback_batch(root, n)?;
                entry["rolled_back"] = json!(rb);
                b2["stage_status"]["A6"] = json!("failed");
                save_baseline(root, &b2, "A6")?;
                report.push_str(&format!(
                    "## Batch {n} — FAILED tests, rolled back\n\n```json\n{}\n```\n\n",
                    serde_json::to_string_pretty(&t)?
                ));
                write_text(&ev(root).join("07-MIGRATION-EXECUTION-REPORT.md"), &report)?;
                return Err(GovError::new("MIGRATION_BATCH_FAILED", format!("batch {n}: {} independent test(s) failed; batch rolled back; downstream batches not executed", t["fail"])).with_details(t));
            }
        }
        entry["tests"] = tests;
        report.push_str(&format!(
            "## Batch {n}\n\n```json\n{}\n```\n\n",
            serde_json::to_string_pretty(&entry)?
        ));
        results.push(entry);
    }
    write_text(&ev(root).join("07-MIGRATION-EXECUTION-REPORT.md"), &report)?;
    if !deprecated_flag_note.is_null() {
        results.push(json!({"note": deprecated_flag_note}));
    }
    let all_done = batch.is_none()
        || plan["batches"]
            .as_array()
            .map(|a| {
                a.iter().all(|x| {
                    x["batch"].as_i64() == batch
                        || read_text(&ledger)
                            .map(|t| {
                                t.contains(&format!(
                                    "\"batch\":{},\"status\":\"batch_complete\"",
                                    x["batch"]
                                ))
                            })
                            .unwrap_or(false)
                        || x["entries"].as_u64() == Some(0)
                })
            })
            .unwrap_or(true);
    b2["stage_status"]["A6"] = json!(if all_done { "done" } else { "in_progress" });
    b2["stage_times"]["A6"] = json!(now_iso());
    b2["migration_execution"] = json!({"approved_catalogue_sha256": approved["catalogue_sha256"], "approved_plan_sha256": approved["plan_sha256"], "approved_tests_sha256": approved["tests_sha256"], "by": verdict_actor(&who), "at": now_iso()});
    save_baseline(root, &b2, "A6")?;
    // G4 (Contract v3:797): wider staleness/impact propagation after the migration changed the tree
    let health = if all_done {
        let p = Project::open(root);
        if p.is_installed() {
            let moved: Vec<String> = results
                .iter()
                .flat_map(|r| {
                    r["moves"]
                        .as_array()
                        .cloned()
                        .unwrap_or_default()
                        .into_iter()
                        .flat_map(|m| {
                            m.as_array()
                                .cloned()
                                .unwrap_or_default()
                                .into_iter()
                                .filter_map(|x| x.as_str().map(String::from))
                        })
                })
                .collect();
            tier_health(
                &p,
                crate::scheduler::Tier::G4,
                crate::scheduler::Trigger::new(crate::scheduler::catalogue::ops::ADOPT_MIGRATE)
                    .with_subject(b["adoption_id"].as_str().unwrap_or("adoption"))
                    .with_paths(&moved),
            )
        } else {
            Value::Null
        }
    } else {
        Value::Null
    };
    Ok(
        json!({"stage": "A6", "batches": results, "complete": all_done, "approval": {"verdict": b["verdicts"]["A5"]["verdict"], "reviewer": b["verdicts"]["A5"]["role"], "catalogue_sha256": approved["catalogue_sha256"], "plan_sha256": approved["plan_sha256"], "tests_sha256": approved["tests_sha256"]},
            "health": health, "evidence": format!("{EVIDENCE}/07-MIGRATION-EXECUTION-REPORT.md")}),
    )
}

/// Run health tier `tier` for an adoption event and summarise it. A tier run that cannot complete is reported (the
/// stage's own changes are already recorded); the independent verification of the next stage judges the tree.
fn tier_health(
    p: &Project,
    tier: crate::scheduler::Tier,
    trigger: crate::scheduler::Trigger,
) -> Value {
    match crate::scheduler::tier_run(p, tier, trigger) {
        Ok(r) => {
            json!({"tier": tier.as_str(), "verdict": r["verdict"], "health_result": r["health_result"], "state": r["state"], "findings": r["counts"], "blocks": r["blocks"]})
        }
        Err(e) => json!({"tier": tier.as_str(), "error": {"code": e.code, "message": e.message}}),
    }
}

pub fn rollback_batch(root: &Path, batch: i64) -> Result<Value> {
    rollback_batch_by(root, batch, &identity::Actor::process())
}

/// Roll back an executed batch (Role C). Recorded as executor authorship.
pub fn rollback_batch_by(root: &Path, batch: i64, actor: &identity::Actor) -> Result<Value> {
    let (mut b, who) = begin_stage(root, "rollback", actor, None)?;
    let r = executor::rollback_batch(root, batch)?;
    record_author(&mut b, &who);
    save_baseline(root, &b, "A6 rollback")?;
    Ok(r)
}

// ---------------------------------------------------------------- A7
pub fn a7_verify_migration(
    root: &Path,
    verdict: Option<&str>,
    session: &str,
    role: &str,
) -> Result<Value> {
    a7_verify_migration_by(
        root,
        verdict,
        &identity::Actor::supplied(session, Some(role)),
    )
}

/// **A7 independent migration verification (Role D).** Performed only by `migration-verifier` in a fresh declared
/// session. It verifies the tree against exactly what was approved: an acceptance needs the approved independent tests
/// (the digest A5 bound, reviewer-authored tests present), at least one executed test and no failure — an accept
/// with zero executed tests, or over tests emptied or changed after approval, is not computed and a claimed accept is
/// refused (`VERDICT_CONFLICT`).
pub fn a7_verify_migration_by(
    root: &Path,
    verdict: Option<&str>,
    actor: &identity::Actor,
) -> Result<Value> {
    let (b, who) = begin_stage(root, "verify-migration", actor, None)?;
    let (session, role) = (who.session(), who.role());
    require_stage(&b, "A6")?;
    let catalogue = read_jsonl(&ev(root).join("04-TARGET-PATH-MAP.jsonl"))?;
    let vc = verify::verify_catalogue(root, &catalogue);
    let tests_file = ev(root).join("06-migration-tests.yaml");
    let run_as = command_policy(root, &b, "A7", &role);
    if let Ok(t) = read_yaml(&tests_file) {
        // Contract v3 A3: refused before any test runs when a command test is one this verifier may not run
        verify::refuse_unpermitted_command_tests(&t, &run_as, "adopt verify-migration")?;
    }
    let tests = if tests_file.exists() {
        verify::run_tests_file_as(root, &tests_file, None, &run_as)?
    } else {
        json!({"ok": false, "reason": "no independent tests", "tests": 0, "pass": 0, "fail": 0})
    };
    // bound to the approval: the tests run are the approved ones, over the approved plan and catalogue
    let now = current_bindings(root)?;
    let a5 = &b["verdicts"]["A5"];
    let mut approval_problems: Vec<String> = binding_changes(a5, &now)
        .into_iter()
        .map(|c| format!("{c} differs from what the independent reviewer approved"))
        .collect();
    if !a5["verdict"]
        .as_str()
        .map(|v| v.starts_with("MIGRATION_PLAN_APPROVED"))
        .unwrap_or(false)
    {
        approval_problems.push("no independent approval (A5) of the plan".into());
    }
    if a5["reviewer_tests_count"].as_u64().unwrap_or(0) == 0 {
        approval_problems.push("the approval records no reviewer-authored test".into());
    }
    let executed = tests["tests"].as_u64().unwrap_or(0);
    if executed == 0 {
        approval_problems.push(
            "no independent test was executed: an acceptance is never computed from zero tests"
                .into(),
        );
    }
    let p = Project::open(root);
    let secrets_ok = p.is_installed() && {
        let sc = p.secret_scanner();
        let contract = p.contract();
        crate::paths::iter_repo_files(root, false)
            .into_iter()
            .all(|(abs, rel)| {
                contract.decide(&rel).is_secret()
                    || sc.path_is_secret(&rel)
                    || sc.scan_file(&abs, &rel).is_empty()
            })
    };
    let kernel_ok = p.is_installed()
        && crate::kernel::verify_kernel(&p.kernel_dir())
            .map(|v| v.ok)
            .unwrap_or(false);
    let computed = if vc["ok"].as_bool().unwrap_or(false)
        && tests["ok"].as_bool().unwrap_or(false)
        && approval_problems.is_empty()
        && secrets_ok
        && kernel_ok
    {
        "MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD"
    } else {
        "MIGRATION_REJECTED_NEEDS_REPAIR"
    };
    let final_verdict = verdict.unwrap_or(computed);
    if verdict.is_some()
        && verdict != Some(computed)
        && final_verdict == "MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD"
    {
        return Err(GovError::new(
            "VERDICT_CONFLICT",
            format!("verifier claims acceptance but evidence computes {computed}; repair first"),
        )
        .with_details(
            json!({"catalogue": vc, "tests": tests, "approval_problems": approval_problems}),
        ));
    }
    let n_of = |k: &str| vc[k].as_array().map(|a| a.len()).unwrap_or(0);
    let md = format!("# 08 — Independent migration verification\n\nVerifier: {role} (session {session}) at {}. Executor confidence statements ignored; actual paths inspected; dependency references re-derived from a fresh scan.\n\n- Catalogue vs reality: {} problem(s), {} broken link(s), {} legacy mechanism(s) still active\n- Legacy retirements awaiting a Human Decision Gate: {} · kept by decision: {}\n- Retired with active references accepted at a gate: {} · active citations of archived material: {}\n- Independent tests: {} executed, {} pass / {} fail ({} reviewer-authored in the approval)\n- Bound to the approval: {}\n- Secrets isolated: {secrets_ok}\n- Kernel intact: {kernel_ok}\n\n**Verdict: {final_verdict}**\n\n```json\n{}\n```\n", now_iso(), n_of("problems"), n_of("broken_links"), n_of("legacy_in_active_tree"), n_of("legacy_retirement_pending_gate"), n_of("legacy_kept_by_decision"), n_of("retired_with_accepted_active_references"), n_of("active_citations_of_archived_material"), executed, tests["pass"], tests["fail"], a5["reviewer_tests_count"], if approval_problems.is_empty() { "yes".to_string() } else { approval_problems.join("; ") }, serde_json::to_string_pretty(&json!({"catalogue": vc, "tests": tests, "approval_problems": approval_problems}))?);
    write_md(root, "08-INDEPENDENT-MIGRATION-VERIFICATION.md", &md)?;
    let mut b2 = b.clone();
    let mut entry = verdict_actor(&who);
    for (k, v) in json!({"verdict": final_verdict, "at": now_iso(), "tests": {"executed": executed, "pass": tests["pass"], "fail": tests["fail"], "deferred": tests["deferred"]},
        "catalogue_sha256": now["catalogue_sha256"], "plan_sha256": now["plan_sha256"], "tests_sha256": now["tests_sha256"], "approval_bound": approval_problems.is_empty(), "approval_problems": approval_problems,
        "independence": who.independence}).as_object().unwrap() {
        entry[k] = v.clone();
    }
    b2["verdicts"]["A7"] = entry;
    b2["stage_status"]["A7"] = json!(if final_verdict.starts_with("MIGRATION_ACCEPTED") {
        "done"
    } else {
        "rejected"
    });
    b2["stage_times"]["A7"] = json!(now_iso());
    record_author(&mut b2, &who);
    save_baseline(root, &b2, "A7")?;
    Ok(
        json!({"stage": "A7", "verdict": final_verdict, "catalogue_problems": vc["problems"], "broken_links": vc["broken_links"], "legacy_in_active_tree": vc["legacy_in_active_tree"],
            "legacy_retirement_pending_gate": vc["legacy_retirement_pending_gate"], "legacy_kept_by_decision": vc["legacy_kept_by_decision"], "retired_with_accepted_active_references": vc["retired_with_accepted_active_references"],
            "active_citations_of_archived_material": vc["active_citations_of_archived_material"], "tests": {"executed": executed, "pass": tests["pass"], "fail": tests["fail"]}, "approval_problems": approval_problems, "secrets_isolated": secrets_ok, "kernel_intact": kernel_ok}),
    )
}

// ---------------------------------------------------------------- A8
/// A8: extract every unit of unique durable knowledge from each legacy store (decisions, lessons, skill candidates,
/// research notes, evidence claims; everything else into a review register), then retire each store only after a
/// fresh dependency proof shows no active code, configuration or document depends on it — or under a Human Decision
/// Gate answered A for exactly the dependants found, leaving them as they are (framework §69-70; BC-P2-33).
pub fn a8_extract_legacy(root: &Path) -> Result<Value> {
    a8_extract_legacy_by(root, &identity::Actor::process())
}

/// A8 as `actor` (Role C). It acts on the catalogue the independent verifier accepted: a catalogue changed since A7
/// is refused (`APPROVAL_STALE`), and the G0 guard (`adopt.migrate`) applies to its retirements.
pub fn a8_extract_legacy_by(root: &Path, actor: &identity::Actor) -> Result<Value> {
    let (mut b, who) = begin_stage(root, "extract-legacy", actor, None)?;
    require_stage(&b, "A7")?;
    require_verdict(&b, "A7", &["MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD"])?;
    {
        let p0 = Project::open(root);
        crate::orchestration::control::guard_write(&p0, "adopt extract-legacy")?;
        crate::authority::require(&p0, "migrate_execute")?;
    }
    {
        let now = current_bindings(root)?;
        let a7 = &b["verdicts"]["A7"];
        if a7["catalogue_sha256"].as_str().is_none()
            || a7["catalogue_sha256"] != now["catalogue_sha256"]
        {
            return Err(GovError::new(
                "APPROVAL_STALE",
                "adopt extract-legacy refused: the migration catalogue changed after the independent migration verifier accepted the migration (A7); A8 acts only on the accepted catalogue",
            )
            .with_details(json!({"accepted_catalogue_sha256": a7["catalogue_sha256"], "current_catalogue_sha256": now["catalogue_sha256"], "remediation": "restore the accepted catalogue, or re-run the migration verification (`gov adopt verify-migration` as migration-verifier)"})));
        }
        let p0 = Project::open(root);
        crate::scheduler::guard(&p0, crate::scheduler::catalogue::ops::ADOPT_MIGRATE, &[])?;
    }
    record_author(&mut b, &who);
    save_baseline(root, &b, "A8")?;
    set_stage(root, "A8", "in_progress", None)?;
    let catalogue = read_jsonl(&ev(root).join(format!("{CATALOGUE_STEM}.jsonl")))?;
    let scanner = scanner_for(root);
    let answered = answered_destructive(root, &catalogue);
    let mut stores = vec![];
    let mut created = vec![];
    let mut registers = vec![];
    let mut retired = vec![];
    let mut retained = vec![];
    let mut seen: std::collections::HashSet<String> = std::collections::HashSet::new();
    let mut ledger_rows: Vec<Value> = vec![];
    // stores = legacy memory stores (EXTRACT → memory-stores) + legacy rule/governance files (wherever they are now)
    let mut sources: Vec<(&Value, bool)> = catalogue
        .iter()
        .filter(|e| {
            e["action"] == "EXTRACT"
                && e["target_path"]
                    .as_str()
                    .map(|t| t.contains("memory-stores"))
                    .unwrap_or(false)
        })
        .map(|e| (e, true))
        .collect();
    for e in catalogue
        .iter()
        .filter(|e| e["current_class"] == "GOVERNANCE_LEGACY" && e["action"] == "MOVE")
    {
        sources.push((e, false));
    }
    let needs_proof = sources
        .iter()
        .any(|(e, store)| *store && root.join(e["current_path"].as_str().unwrap_or("")).exists());
    let index = if needs_proof {
        references::build_fresh(root)
    } else {
        references::ReferenceIndex::default()
    };
    let os = ownership::OsState::load(root);
    let active = references::ActiveSet {
        root,
        os: &os,
        archive_root: ARCHIVE_ROOT.into(),
        leaving: planner::non_active_paths(&catalogue, ARCHIVE_ROOT, &answered),
    };
    for (e, is_store) in sources {
        let path = e["current_path"].as_str().unwrap_or("").to_string();
        let target = e["target_path"].as_str().unwrap_or("").to_string();
        let aid = e["artifact_id"].as_str().unwrap_or("").to_string();
        let at_source = root.join(&path).exists();
        let read_from = if at_source {
            path.clone()
        } else if !target.is_empty() && root.join(&target).exists() {
            target.clone()
        } else {
            path.clone()
        };
        let (kind, x) = extraction::extract_store(root, &path, &read_from, &scanner, &mut seen)?;
        created.extend(x.records.clone());
        if let Some(r) = &x.register {
            registers.push(r.clone());
            created.push(r.clone());
        }
        let mut proof = Value::Null;
        let disposition = if kind == "NOT_FOUND" {
            "NOT_FOUND".to_string()
        } else if !at_source {
            retired.push(read_from.clone());
            "RETIRE".to_string()
        } else if !is_store {
            // a legacy rule file its migration batch did not retire (gated or blocked): registered, not moved here
            let why = match entry_gate_answer(&Project::open(root), e) {
                Some(o) if o != "A" => "KEPT_BY_DECISION",
                _ => "RETIREMENT_PENDING_GATE",
            };
            retained.push(json!({"path": path, "artifact_id": aid, "disposition": why, "gate": e["human_gate"]}));
            why.to_string()
        } else {
            let p = references::dependency_proof(&index, &path, Some(target.as_str()), &active);
            let clean = references::proof_is_clean(&p);
            let gated = e["requires_human_gate"].as_bool().unwrap_or(false);
            let authorised = answered.contains(&aid);
            let gate_for_refs = e["gate_reasons"]
                .as_array()
                .map(|a| a.iter().any(|r| r == "active_references"))
                .unwrap_or(false);
            proof = p.clone();
            let outcome = if !clean
                && !(authorised
                    && gate_for_refs
                    && executor::proof_covered_by(&p, &e["dependency_proof"]))
            {
                "RETIREMENT_BLOCKED_ACTIVE_REFERENCES"
            } else if gated && !authorised {
                match entry_gate_answer(&Project::open(root), e) {
                    Some(_) => "KEPT_BY_DECISION",
                    None => "RETIREMENT_PENDING_GATE",
                }
            } else {
                "RETIRE"
            };
            if outcome == "RETIRE" {
                if let Some(d) = root.join(&target).parent() {
                    std::fs::create_dir_all(d)?;
                }
                let _ = std::process::Command::new("git")
                    .args(["mv", "-k", &path, &target])
                    .current_dir(root)
                    .output();
                if root.join(&path).exists() {
                    std::fs::rename(root.join(&path), root.join(&target))?;
                }
                retired.push(target.clone());
                // the ledger records store retirements too, so every later pass can re-check what depended on them
                let dangling = if clean {
                    Value::Null
                } else {
                    p["active_references"].clone()
                };
                ledger_rows.push(json!({"at": now_iso(), "stage": "A8", "artifact_id": aid, "action": "EXTRACT", "path": path, "status": "applied", "entry_hash": e["entry_hash"],
                    "result": {"to": target, "retired_with_active_references": dangling, "authorised_by_gate": if clean { Value::Null } else { e["human_gate"].clone() }},
                    "dependency_proof": {"result": p["result"], "dependants_digest": p["dependants_digest"], "active_references": p["active_references"]}}));
            } else {
                retained.push(json!({"path": path, "artifact_id": aid, "disposition": outcome, "gate": e["human_gate"], "dependency_proof": p}));
            }
            outcome.to_string()
        };
        stores.push(json!({"path": path, "artifact_id": aid, "kind": kind, "strings": x.units, "extracted": x.distilled, "registered_for_review": x.registered_for_review,
            "skipped_secret_strings": x.withheld_secret, "duplicates": x.duplicates, "by_kind": x.by_kind, "records": x.records, "register": x.register,
            "disposition": disposition, "archived_to": if disposition == "RETIRE" { json!(if at_source { target.clone() } else { read_from.clone() }) } else { Value::Null },
            "dependency_proof": proof, "retired_with_active_references": if disposition == "RETIRE" && !proof.is_null() && !references::proof_is_clean(&proof) { proof["active_references"].clone() } else { Value::Null }}));
    }
    if !ledger_rows.is_empty() {
        let lp = ev(root).join("migration-ledger.jsonl");
        let mut text = read_text(&lp).unwrap_or_default();
        for r in &ledger_rows {
            text.push_str(&serde_json::to_string(r)?);
            text.push('\n');
        }
        write_text(&lp, &text)?;
    }
    // LEGACY registration record: every legacy mechanism, where it went, and why any is still in the tree. A mechanism
    // still present after migration acceptance is held behind a gate (pending, or kept by the human's decision): it is
    // registered here whatever authority label classification gave it (a superseded decision log included).
    let mut legacy_paths: Vec<String> = catalogue
        .iter()
        .filter(|e| e["authority"] == "LEGACY")
        .map(|e| e["current_path"].as_str().unwrap_or("").to_string())
        .collect();
    for l in classify::legacy_mechanisms(root) {
        if !legacy_paths.contains(&l.path) {
            if !retained.iter().any(|r| r["path"] == l.path.as_str()) {
                let entry = catalogue
                    .iter()
                    .find(|e| e["current_path"].as_str() == Some(l.path.as_str()));
                retained.push(json!({"path": l.path, "artifact_id": entry.map(|e| e["artifact_id"].clone()), "disposition": "RETAINED_UNDER_GATE", "gate": entry.map(|e| e["human_gate"].clone()), "kind": l.kind}));
            }
            legacy_paths.push(l.path);
        }
    }
    let mut rec = new_record(
        "legacy",
        "LEG-0001",
        "Retired legacy governance and memory mechanisms",
        json!({"status": "LEGACY", "state_class": "HISTORICAL", "paths": legacy_paths, "archived": retired, "retained": retained, "body": "Legacy mechanisms inventoried in A2, retired in A6/A8 after a dependency proof. They carry no authority (INV-004). Unique durable knowledge was extracted into PROVISIONAL records with provenance; units not distilled into a typed record are listed in review registers. A mechanism still in the tree is listed under `retained` with its gate or blocking proof.", "extracted_records": created, "review_registers": registers}),
    );
    rec.path = "archive/governance/LEG-0001.yaml".into();
    save_record(root, &rec)?;
    let md = format!("# 09 — Legacy memory extraction\n\n| Store | Kind | Units | Distilled | For review | Secret withheld | Disposition |\n|---|---|---|---|---|---|---|\n{}\n\nCreated {} record(s): {}\n\nReview registers (units not distilled into a typed record — nothing unique is dropped): {}\n\nRetained in the active tree: {}\n\nRaw chat/session content was not imported into active semantic memory (§70, protocol §13). Each retirement was preceded by a fresh dependency proof over code, configuration and docs.\n",
        stores.iter().map(|s| format!("| {} | {} | {} | {} | {} | {} | {} |", s["path"].as_str().unwrap_or(""), s["kind"].as_str().unwrap_or(""), s["strings"], s["extracted"], s["registered_for_review"], s["skipped_secret_strings"], s["disposition"].as_str().unwrap_or(""))).collect::<Vec<_>>().join("\n"),
        created.len(), created.join(", "), if registers.is_empty() { "none".to_string() } else { registers.join(", ") },
        if retained.is_empty() { "none".to_string() } else { retained.iter().map(|r| format!("{} ({})", r["path"].as_str().unwrap_or(""), r["disposition"].as_str().unwrap_or(""))).collect::<Vec<_>>().join(", ") });
    write_md(root, "09-LEGACY-MEMORY-EXTRACTION.md", &md)?;
    set_stage(root, "A8", "done", None)?;
    Ok(
        json!({"stage": "A8", "stores": stores, "created_records": created, "review_registers": registers, "retired": retired, "retained": retained, "legacy_record": "archive/governance/LEG-0001.yaml"}),
    )
}

// ---------------------------------------------------------------- A9
pub fn a9_build_memory(root: &Path, session: &str) -> Result<Value> {
    a9_build_memory_by(root, &identity::Actor::supplied(session, None))
}

/// A9 as `actor` (Role E, memory builder). Every held-out query present after the build — the generated starter set
/// and anything that pre-existed — is recorded as the builder's regression set, so A10 can only accept on queries
/// the independent memory verifier authored afterwards.
pub fn a9_build_memory_by(root: &Path, actor: &identity::Actor) -> Result<Value> {
    let (b, who) = begin_stage(root, "build-memory", actor, None)?;
    let session = who.session();
    require_stage(&b, "A8")?;
    require_verdict(&b, "A7", &["MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD"])?;
    {
        let p0 = Project::open(root);
        crate::orchestration::control::guard_write(&p0, "adopt build-memory")?;
        crate::authority::require(&p0, "build_memory")?;
    }
    let mut b2 = b.clone();
    b2["memory_builder_session"] = json!(session);
    b2["stage_status"]["A9"] = json!("in_progress");
    record_author(&mut b2, &who);
    save_baseline(root, &b2, "A9")?;
    let mut p = Project::open(root);
    p.invalidate();
    p.require_installed()?;
    let r = crate::memory::indexer::rebuild(
        &p,
        crate::memory::indexer::IndexOptions {
            incremental: false,
            ..Default::default()
        },
    )?;
    // held-out template from governed records (only when none exist yet)
    let held_path = root.join(p.policies().get_str(
        "MEMORY_POLICY",
        "regression.heldout_file",
        "governance/tests/memory/heldout.yaml",
    ));
    let existing = read_yaml(&held_path)
        .ok()
        .and_then(|h| h["queries"].as_array().map(|a| a.len()))
        .unwrap_or(0);
    let mut generated = 0;
    if existing == 0 {
        let db = RuntimeDb::open(&p.db_path())?;
        let set = crate::memory::heldout::generate_starter(&p, &db, "gov adopt build-memory")?;
        generated = set["queries"].as_array().map(|a| a.len()).unwrap_or(0);
        drop(db);
        write_yaml(&held_path, &set)?;
        let _ = crate::memory::indexer::rebuild(
            &p,
            crate::memory::indexer::IndexOptions {
                incremental: true,
                ..Default::default()
            },
        );
    }
    // the builder's held-out set (regression evidence): every query present now, except those an earlier verified
    // A10 recorded as the memory verifier's own
    let verifier_owned: Vec<String> = b["verdicts"]["A10"]["verifier_query_identities"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(String::from))
                .collect()
        })
        .unwrap_or_default();
    let held = read_yaml(&held_path).unwrap_or(json!({"queries": []}));
    let builder_queries: Vec<String> = held["queries"]
        .as_array()
        .map(|a| {
            a.iter()
                .map(heldout_query_identity)
                .filter(|i| !verifier_owned.contains(i))
                .collect()
        })
        .unwrap_or_default();
    let heldout_rel = held_path
        .strip_prefix(root)
        .map(|x| x.to_string_lossy().replace('\\', "/"))
        .unwrap_or_default();
    let md = format!("# 10 — Memory implementation report\n\nBuilt after path stabilisation (A7 accepted) on canonical paths.\n\n- artefacts: {} · chunks: {} · vectors: {} · edges: {} · symbols: {}\n- excluded (secret/binary/large): {}\n- secret-content blocked: {}\n- embedder: {}\n- manifest hash: {}\n- degradations: {:?}\n- held-out queries generated: {generated}\n- builder held-out set (regression evidence, not independent): {} quer(ies) in `{heldout_rel}`; the independent memory verifier (A10) authors its own held-out queries\n", r.counts["artifacts"], r.counts["chunks"], r.counts["vectors"], r.counts["edges"], r.counts["symbols"], r.excluded.len(), r.secret_blocked.len(), r.embedder, r.manifest_hash, r.degradations, builder_queries.len());
    write_md(root, "10-MEMORY-IMPLEMENTATION-REPORT.md", &md)?;
    set_stage(
        root,
        "A9",
        "done",
        Some((
            "memory_build",
            json!({"heldout_file": heldout_rel, "builder_query_identities": builder_queries, "generated": generated, "manifest_hash": r.manifest_hash, "by": verdict_actor(&who), "at": now_iso()}),
        )),
    )?;
    // G4 (Contract v3:797): wider staleness/impact propagation after the memory change
    let health = tier_health(
        &p,
        crate::scheduler::Tier::G4,
        crate::scheduler::Trigger::new("adopt.build-memory")
            .with_subject(b["adoption_id"].as_str().unwrap_or("adoption")),
    );
    Ok(
        json!({"stage": "A9", "counts": r.counts, "manifest_hash": r.manifest_hash, "excluded": r.excluded.len(), "secret_blocked": r.secret_blocked, "heldout_generated": generated, "builder_heldout_queries": builder_queries.len(), "health": health}),
    )
}

/// What a held-out query asks and expects, independent of its label (`id`, `k`, `category`, notes): a starter query
/// relabelled is still the builder's.
pub fn heldout_query_identity(q: &Value) -> String {
    let norm = |v: &Value| -> Value {
        let mut a: Vec<String> = v
            .as_array()
            .map(|x| {
                x.iter()
                    .filter_map(|y| y.as_str().map(|s| s.trim().to_string()))
                    .collect()
            })
            .unwrap_or_default();
        a.sort();
        json!(a)
    };
    identity::content_hash(
        &json!({"query": q["query"].as_str().map(|s| s.trim()), "expected_refs": norm(&q["expected_refs"]), "forbidden": norm(&q["forbidden"]), "route": q["route"]}),
    )
}

// ---------------------------------------------------------------- A10
pub fn a10_verify_memory(
    root: &Path,
    verdict: Option<&str>,
    session: &str,
    role: &str,
) -> Result<Value> {
    a10_verify_memory_by(
        root,
        verdict,
        &identity::Actor::supplied(session, Some(role)),
    )
}

/// **A10 independent memory verification (Role F).** Performed only by `memory-verifier` in a fresh declared session.
/// The held-out tests are the verifier's own (adoption protocol §15; Contract v3 O3, T2): queries in the governed
/// held-out file that are neither in the builder's recorded set (A9) nor produced by the product's own starter
/// generator from this index. Without any, the stage refuses (`INDEPENDENT_HELDOUT_REQUIRED`); an acceptance needs
/// the verifier's set to pass on its own (a measured set: `MEMORY_POLICY.regression.min_queries`) as well as the
/// whole set, a reproducible rebuild and no secret in the index.
pub fn a10_verify_memory_by(
    root: &Path,
    verdict: Option<&str>,
    actor: &identity::Actor,
) -> Result<Value> {
    let (b, who) = begin_stage(root, "verify-memory", actor, None)?;
    let (session, role) = (who.session(), who.role());
    require_stage(&b, "A9")?;
    let mut p = Project::open(root);
    p.invalidate();
    let held_rel = p.policies().get_str(
        "MEMORY_POLICY",
        "regression.heldout_file",
        "governance/tests/memory/heldout.yaml",
    );
    let held = read_yaml(&root.join(&held_rel)).map_err(|_| {
        GovError::new(
            "INDEPENDENT_HELDOUT_REQUIRED",
            format!("the held-out set {held_rel} is missing; the independent memory verifier authors held-out queries there before A10"),
        )
    })?;
    // delete/rebuild guarantee (§19): two full rebuilds from Git + records at the same tree state must be identical
    let first = crate::memory::indexer::rebuild(
        &p,
        crate::memory::indexer::IndexOptions {
            incremental: false,
            ..Default::default()
        },
    )?;
    let before = Some(first.manifest_hash.clone());
    let rebuilt = crate::memory::indexer::rebuild(
        &p,
        crate::memory::indexer::IndexOptions {
            incremental: false,
            ..Default::default()
        },
    )?;
    let reproducible = before.as_deref() == Some(rebuilt.manifest_hash.as_str());
    let db = RuntimeDb::open(&p.db_path())?;
    // what the builder produced: its recorded set (A9) and whatever the product's own generator makes of this index
    let mut builder: Vec<String> = b["memory_build"]["builder_query_identities"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(String::from))
                .collect()
        })
        .unwrap_or_default();
    if let Ok(gen) = crate::memory::heldout::generate_starter(&p, &db, "A10 builder-set check") {
        builder.extend(
            gen["queries"]
                .as_array()
                .map(|a| a.iter().map(heldout_query_identity).collect::<Vec<_>>())
                .unwrap_or_default(),
        );
    }
    let all_queries: Vec<Value> = held["queries"].as_array().cloned().unwrap_or_default();
    let verifier_queries: Vec<Value> = all_queries
        .iter()
        .filter(|q| !q.get("pending").and_then(|v| v.as_bool()).unwrap_or(false))
        .filter(|q| !builder.contains(&heldout_query_identity(q)))
        .cloned()
        .collect();
    if verifier_queries.is_empty() {
        return Err(GovError::new(
            "INDEPENDENT_HELDOUT_REQUIRED",
            format!("A10 evaluates held-out queries the independent memory verifier authored (adoption protocol §15: \"fresh test author creates held-out tests independently\"); every query in {held_rel} is the builder's starter or pre-existing set (regression evidence only)"),
        )
        .with_details(json!({"heldout_file": held_rel, "queries": all_queries.len(), "builder_queries": all_queries.len(), "min_queries": p.policies().get_i64("MEMORY_POLICY", "regression.min_queries", 5),
            "remediation": "add held-out queries of your own (exact id/path, lexical, semantic paraphrase, graph, superseded-vs-active, symbol) with their expected references, then run A10"})));
    }
    let h = crate::retrieval::run_heldout(&p, &db, &held)?;
    let mut indep_set = held.clone();
    indep_set["queries"] = json!(verifier_queries);
    let hi = crate::retrieval::run_heldout(&p, &db, &indep_set)?;
    let secret_leak = db.count_where("artifacts", "path_class='secret'") > 0
        || db.query("SELECT text FROM chunks", &[])?.iter().any(|r| {
            !p.secret_scanner()
                .scan_text(r["text"].as_str().unwrap_or(""), "c")
                .is_empty()
        });
    let status = crate::status::status(&p)?;
    let computed = if h["pass"].as_bool().unwrap_or(false)
        && hi["pass"].as_bool().unwrap_or(false)
        && reproducible
        && !secret_leak
    {
        "MEMORY_ACCEPTED_FOR_V4_AUDIT"
    } else {
        "MEMORY_REJECTED_NEEDS_REPAIR"
    };
    let final_verdict = verdict.unwrap_or(computed);
    if final_verdict == "MEMORY_ACCEPTED_FOR_V4_AUDIT" && computed != final_verdict {
        return Err(
            GovError::new("VERDICT_CONFLICT", format!("evidence computes {computed}"))
                .with_details(
                    json!({"heldout": h, "independent_heldout": hi, "reproducible": reproducible, "secret_leak": secret_leak}),
                ),
        );
    }
    let md = format!("# 11 — Independent memory verification\n\nVerifier: {role} (session {session}) at {}.\n\n- independent held-out (authored by the verifier): {} quer(ies), recall@k {:.2}, MRR {:.2}, measured={} → pass={}\n- whole held-out set (verifier + builder regression): recall@k {:.2}, MRR {:.2}, stale-hit {:.2}, superseded-hit {:.2}, forbidden {} → pass={}\n- delete/rebuild reproducibility: {reproducible} (before {:?}, after {})\n- secret exclusion: leak={secret_leak}\n- fresh-agent reconstruction: status packet ok, next action: {}\n\n**Verdict: {final_verdict}**\n", now_iso(), verifier_queries.len(), hi["recall_at_k"].as_f64().unwrap_or(0.0), hi["mrr"].as_f64().unwrap_or(0.0), hi["measured"], hi["pass"], h["recall_at_k"].as_f64().unwrap_or(0.0), h["mrr"].as_f64().unwrap_or(0.0), h["stale_hit_rate"].as_f64().unwrap_or(0.0), h["superseded_hit_rate"].as_f64().unwrap_or(0.0), h["forbidden_violations"], h["pass"], before, rebuilt.manifest_hash, status["next_action"]);
    write_md(root, "11-INDEPENDENT-MEMORY-VERIFICATION.md", &md)?;
    let mut b2 = b.clone();
    let mut entry = verdict_actor(&who);
    for (k, v) in json!({"verdict": final_verdict, "at": now_iso(), "reproducible": reproducible, "heldout_file": held_rel, "heldout_sha256": identity::content_hash(&held),
        "verifier_queries": verifier_queries.iter().map(|q| q["id"].clone()).collect::<Vec<_>>(), "verifier_query_identities": verifier_queries.iter().map(heldout_query_identity).collect::<Vec<_>>(),
        "builder_queries": all_queries.len() - verifier_queries.len(), "independent_heldout": {"queries": hi["queries"], "measured": hi["measured"], "recall_at_k": hi["recall_at_k"], "mrr": hi["mrr"], "pass": hi["pass"]},
        "manifest_hash": rebuilt.manifest_hash, "independence": who.independence}).as_object().unwrap() {
        entry[k] = v.clone();
    }
    b2["verdicts"]["A10"] = entry;
    b2["stage_status"]["A10"] = json!(if final_verdict.starts_with("MEMORY_ACCEPTED") {
        "done"
    } else {
        "rejected"
    });
    b2["stage_times"]["A10"] = json!(now_iso());
    record_author(&mut b2, &who);
    save_baseline(root, &b2, "A10")?;
    let failed: Vec<Value> = h["results"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter(|x| !x["pass"].as_bool().unwrap_or(false))
                .cloned()
                .collect()
        })
        .unwrap_or_default();
    Ok(
        json!({"stage": "A10", "verdict": final_verdict, "heldout": {"recall_at_k": h["recall_at_k"], "mrr": h["mrr"], "pass": h["pass"], "queries": h["queries"], "stale_hit_rate": h["stale_hit_rate"], "superseded_hit_rate": h["superseded_hit_rate"], "forbidden_violations": h["forbidden_violations"], "failed": failed},
            "independent_heldout": {"queries": hi["queries"], "measured": hi["measured"], "recall_at_k": hi["recall_at_k"], "mrr": hi["mrr"], "pass": hi["pass"], "min_queries": hi["min_queries"]},
            "builder_queries": all_queries.len() - verifier_queries.len(), "reproducible": reproducible, "secret_leak": secret_leak}),
    )
}

// ---------------------------------------------------------------- A11
pub fn a11_audit(root: &Path, accept_exceptions: bool) -> Result<Value> {
    a11_audit_by(root, accept_exceptions, &identity::Actor::process())
}

/// **A11 comprehensive independent audit (Role G).** Performed only by `independent-auditor` in a fresh declared
/// session that authored no planner, executor or memory-builder stage. The audit is the G5 full suite of the health
/// scheduler's tier contract (every check, fresh, deep, recorded as a governance-suite audit record), plus the
/// adoption's own re-derived findings and the adoption acceptance criteria — which now include that every
/// independent verdict was given by its designated role in a fresh session and bound to what it judged.
pub fn a11_audit_by(
    root: &Path,
    accept_exceptions: bool,
    actor: &identity::Actor,
) -> Result<Value> {
    let (b, who) = begin_stage(root, "audit", actor, None)?;
    require_stage(&b, "A10")?;
    require_verdict(&b, "A10", &["MEMORY_ACCEPTED_FOR_V4_AUDIT"])?;
    let mut p = Project::open(root);
    p.invalidate();
    let _ = crate::memory::indexer::rebuild(
        &p,
        crate::memory::indexer::IndexOptions {
            incremental: true,
            ..Default::default()
        },
    )?; // audit a fresh index
        // G5 at adopt (Contract v3:798; tier contract `scheduler`): every check, executed fresh and compared with the
        // cache, deep, persisted as the adoption's audit record
    let mut g5 = crate::scheduler::RunOptions::new(
        crate::scheduler::Tier::G5,
        crate::scheduler::Trigger::new("adopt.audit")
            .with_subject(b["adoption_id"].as_str().unwrap_or("adoption")),
    );
    g5.deep = true;
    g5.surface = "adopt".into();
    g5.record = crate::scheduler::RecordPolicy::Always;
    let audit = crate::verification::audit_with(&p, &g5)?;
    let _ = crate::memory::indexer::rebuild(
        &p,
        crate::memory::indexer::IndexOptions {
            incremental: true,
            ..Default::default()
        },
    )?; // the audit record is evidence; keep the index fresh
    let doctor = crate::doctor::run(&p)?;
    // adoption's own findings, re-derived now (not taken from A7): legacy mechanisms still active, retirements that
    // left active references, and extracted knowledge awaiting review — each with a stable id (BC-P2-21)
    let catalogue =
        read_jsonl(&ev(root).join(format!("{CATALOGUE_STEM}.jsonl"))).unwrap_or_default();
    let vc = verify::verify_catalogue(root, &catalogue);
    let mut adoption_findings: Vec<Value> = vec![];
    for l in vc["legacy_in_active_tree"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        adoption_findings.push(json!({"severity": "high", "family": "adoption_legacy", "path": l, "message": format!("legacy mechanism {} is still active and unregistered (INV-004)", l.as_str().unwrap_or(""))}));
    }
    for g in vc["legacy_retirement_pending_gate"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        let deps: Vec<String> = g["dependency_proof"]
            .as_array()
            .map(|a| {
                a.iter()
                    .map(|r| format!("{}:{}", r["from"].as_str().unwrap_or(""), r["line"]))
                    .collect()
            })
            .unwrap_or_default();
        adoption_findings.push(json!({"severity": "high", "family": "adoption_legacy", "path": g["path"], "message": format!("legacy mechanism {} is still active: its retirement awaits Human Decision Gate {} ({}){}", g["path"].as_str().unwrap_or(""), g["gate"].as_str().unwrap_or("-"), g["gate_reasons"], if deps.is_empty() { String::new() } else { format!("; active references: {}", deps.join(", ")) })}));
    }
    for k in vc["legacy_kept_by_decision"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        adoption_findings.push(json!({"severity": "medium", "family": "adoption_legacy", "path": k["path"], "message": format!("legacy mechanism {} kept in the active tree by decision on {} (option {}); registered LEGACY, no authority", k["path"].as_str().unwrap_or(""), k["gate"].as_str().unwrap_or("-"), k["option"].as_str().unwrap_or(""))}));
    }
    for a in vc["retired_with_accepted_active_references"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        let r = &a["reference"];
        let live = r["role"] != "docs";
        adoption_findings.push(json!({"severity": if live { "high" } else { "medium" }, "family": "adoption_dependency", "path": r["from"],
            "message": format!("{} {}:{} still refers to retired {} ({} {}); retirement {}; the reference was not re-pointed at the archive — fix or remove it",
                r["role"].as_str().unwrap_or(""), r["from"].as_str().unwrap_or(""), r["line"], r["to"].as_str().unwrap_or(""), r["kind"].as_str().unwrap_or(""), r["resolution"].as_str().unwrap_or(""),
                a["gate"].as_str().map(|g| format!("authorised by gate {g}")).unwrap_or_else(|| "not gated".into()))}));
    }
    // path states after migration may legitimately change through governed work (A7 judged them at migration time);
    // what A11 re-derives is that nothing active depends on retired material
    for m in vc["dependency_problems"]
        .as_array()
        .cloned()
        .unwrap_or_default()
    {
        adoption_findings
            .push(json!({"severity": "high", "family": "adoption_dependency", "message": m}));
    }
    let store = crate::records::RecordStore::load(root);
    for r in store.records.iter().filter(|r| {
        r.rtype() == "report"
            && r.data["review_required"].as_bool().unwrap_or(false)
            && r.status() == "PROVISIONAL"
    }) {
        let n = r.data["units"].as_array().map(|a| a.len()).unwrap_or(0);
        adoption_findings.push(json!({"severity": "low", "family": "adoption_knowledge", "path": r.path, "message": format!("{n} legacy knowledge unit(s) extracted from {} await review in {}", r.get("legacy_source"), r.id())}));
    }
    identity::assign_finding_ids(&mut adoption_findings);
    let adoption_high = adoption_findings
        .iter()
        .filter(|f| f["severity"] == "high" || f["severity"] == "critical")
        .count();
    let legacy_retired = vc["legacy_kept_by_decision"]
        .as_array()
        .map(|a| a.is_empty())
        .unwrap_or(true)
        && vc["legacy_retirement_pending_gate"]
            .as_array()
            .map(|a| a.is_empty())
            .unwrap_or(true)
        && vc["legacy_in_active_tree"]
            .as_array()
            .map(|a| a.is_empty())
            .unwrap_or(true)
        && !vc["retired_with_accepted_active_references"]
            .as_array()
            .map(|a| a.iter().any(|x| x["reference"]["role"] != "docs"))
            .unwrap_or(false);
    let legacy_active = vc["legacy_in_active_tree"]
        .as_array()
        .map(|a| a.len())
        .unwrap_or(0)
        + vc["legacy_retirement_pending_gate"]
            .as_array()
            .map(|a| a.len())
            .unwrap_or(0);
    let inv_count = b["inventory_summary"]["files"].as_u64().unwrap_or(0);
    let class_count = read_jsonl(&ev(root).join("02-CLASSIFICATION.jsonl"))
        .map(|v| v.len() as u64)
        .unwrap_or(0);
    let checks = vec![
        (
            "migration baseline pinned",
            !b["commit"].as_str().unwrap_or("").is_empty(),
        ),
        (
            "every material artefact classified",
            class_count >= inv_count && inv_count > 0,
        ),
        (
            "target path map explicit",
            ev(root).join("04-TARGET-PATH-MAP.jsonl").exists(),
        ),
        (
            "migration plan independently reviewed",
            b["verdicts"]["A5"]["verdict"]
                .as_str()
                .map(|v| v.starts_with("MIGRATION_PLAN_APPROVED"))
                .unwrap_or(false)
                && independent_verdict(&b, "A5"),
        ),
        (
            "independent migration tests exist",
            ev(root).join("06-migration-tests.yaml").exists()
                && b["verdicts"]["A5"]["reviewer_tests_count"]
                    .as_u64()
                    .unwrap_or(0)
                    > 0,
        ),
        (
            "migration executed and verified against the approved plan and tests",
            b["verdicts"]["A7"]["approval_bound"] == true && independent_verdict(&b, "A7"),
        ),
        (
            "migrated paths/imports/links pass",
            b["verdicts"]["A7"]["verdict"] == "MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD",
        ),
        (
            "behaviour baseline preserved or changed by decision",
            b["baseline_tests"]["status"] != "failed"
                || b["verdicts"]["A7"]["verdict"] == "MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD",
        ),
        (
            "legacy governance has no accidental authority",
            legacy_active == 0,
        ),
        (
            "unique knowledge extracted from retired stores",
            ev(root).join("09-LEGACY-MEMORY-EXTRACTION.md").exists(),
        ),
        (
            "memory built on stable canonical paths",
            ev(root).join("10-MEMORY-IMPLEMENTATION-REPORT.md").exists(),
        ),
        (
            "independent memory verifier passed",
            b["verdicts"]["A10"]["verdict"] == "MEMORY_ACCEPTED_FOR_V4_AUDIT"
                && independent_verdict(&b, "A10")
                && b["verdicts"]["A10"]["verifier_queries"]
                    .as_array()
                    .map(|a| !a.is_empty())
                    .unwrap_or(false),
        ),
        (
            "comprehensive v4 audit completed",
            !audit["audit"].as_str().unwrap_or("").is_empty() && audit["tier"] == "G5",
        ),
        (
            "comprehensive audit by a fresh independent auditor",
            who.independence["established"] == true,
        ),
        (
            "installed release pinned in framework.lock",
            p.lock_path().exists(),
        ),
        (
            "project overlay separate from kernel",
            p.overlay_dir().exists()
                && crate::kernel::verify_kernel(&p.kernel_dir())
                    .map(|v| v.ok)
                    .unwrap_or(false),
        ),
        (
            "clean machine can reconstruct derived runtime",
            b["verdicts"]["A10"]["reproducible"]
                .as_bool()
                .unwrap_or(false),
        ),
    ];
    let all = checks.iter().all(|(_, ok)| *ok) && adoption_high == 0;
    let exceptions = p.overlay().get("PROJECT_EXCEPTIONS.yaml")["exceptions"]
        .as_array()
        .map(|a| a.len())
        .unwrap_or(0);
    // a legacy mechanism kept by an answered gate is an exception a human decided, not an unresolved finding
    let verdict = if all && audit["verdict"] == "HEALTHY" && doctor.verdict == "HEALTHY" {
        if legacy_retired {
            "ADOPTED_HEALTHY"
        } else {
            "ADOPTED_WITH_ACCEPTED_EXCEPTIONS"
        }
    } else if all
        && (accept_exceptions || exceptions > 0)
        && audit["counts"]["critical"].as_u64().unwrap_or(0) == 0
    {
        "ADOPTED_WITH_ACCEPTED_EXCEPTIONS"
    } else {
        "NOT_ADOPTED_HEALTHY"
    };
    // WS-2 R3-9: the verdict states why it is not ADOPTED_HEALTHY — and, on a machine whose installation authenticity
    // is not established (D032 its only doctor failure), names that posture as the reason
    let (reasons, posture_reason) = verdict_reasons(
        verdict,
        &checks,
        adoption_high,
        &audit,
        &doctor.verdict,
        &doctor.checks,
    );
    let why = if reasons.is_empty() {
        String::new()
    } else {
        format!(
            "\n## Why the verdict is {verdict}\n\n{}\n",
            reasons
                .iter()
                .map(|r| format!("- {}", r["message"].as_str().unwrap_or("")))
                .collect::<Vec<_>>()
                .join("\n")
        )
    };
    let md = format!("# 12 — Adoption final report\n\nAuditor: {} (session {}). Audit: {} (tier {}, verdict {}), doctor: {}\n\n| Acceptance criterion | OK |\n|---|---|\n{}\n\nOpen findings: critical {} · high {} · medium {} · low {}\n\n## Adoption findings (stable ids)\n\n| Id | Severity | Finding |\n|---|---|---|\n{}\n\n**Final verdict: {verdict}**\n{why}", who.role(), who.session(), audit["audit"], audit["tier"], audit["verdict"], doctor.verdict, checks.iter().map(|(n, ok)| format!("| {n} | {} |", if *ok { "✅" } else { "❌" })).collect::<Vec<_>>().join("\n"), audit["counts"]["critical"], audit["counts"]["high"], audit["counts"]["medium"], audit["counts"]["low"],
        adoption_findings.iter().map(|f| format!("| {} | {} | {} |", f["id"].as_str().unwrap_or(""), f["severity"].as_str().unwrap_or(""), f["message"].as_str().unwrap_or("").replace('|', "/"))).collect::<Vec<_>>().join("\n"));
    write_md(root, "12-ADOPTION-FINAL-REPORT.md", &md)?;
    let mut b2 = b.clone();
    let mut entry = verdict_actor(&who);
    for (k, v) in json!({"verdict": verdict, "audit": audit["audit"], "tier": audit["tier"], "health_result": audit["health_result"], "inputs_hash": audit["inputs_hash"], "at": now_iso(), "independence": who.independence,
        "reasons": reasons, "reason": posture_reason}).as_object().unwrap() {
        entry[k] = v.clone();
    }
    b2["verdicts"]["A11"] = entry;
    b2["stage_status"]["A11"] = json!("done");
    b2["stage_times"]["A11"] = json!(now_iso());
    b2["final_verdict"] = json!(verdict);
    record_author(&mut b2, &who);
    save_baseline(root, &b2, "A11")?;
    let mut messages: Vec<Value> = adoption_findings
        .iter()
        .map(|f| json!({"id": f["id"], "severity": f["severity"], "family": f["family"], "message": f["message"]}))
        .collect();
    messages.extend(audit["findings"].as_array().map(|a| a.iter().take(12).map(|f| json!({"severity": f["severity"], "family": f["family"], "message": f["message"]})).collect::<Vec<_>>()).unwrap_or_default());
    let doctor_failed: Vec<Value> = doctor
        .checks
        .iter()
        .filter(|c| !c["ok"].as_bool().unwrap_or(true))
        .map(|c| json!({"id": c["id"], "message": c["message"]}))
        .collect();
    Ok(
        json!({"stage": "A11", "verdict": verdict, "verdict_reasons": reasons, "verdict_reason": posture_reason, "audit": audit["audit"], "audit_verdict": audit["verdict"], "tier": audit["tier"], "health_result": audit["health_result"], "doctor": doctor.verdict, "checks": checks.iter().map(|(n, ok)| json!({"criterion": n, "ok": ok})).collect::<Vec<_>>(), "findings": audit["counts"], "adoption_findings": adoption_findings, "legacy_authority_retired": legacy_retired, "finding_messages": messages, "doctor_failed": doctor_failed, "evidence": format!("{EVIDENCE}/12-ADOPTION-FINAL-REPORT.md")}),
    )
}

/// **Why A11's verdict is not `ADOPTED_HEALTHY`** (WS-2 round-2 R3-9): every acceptance criterion that failed, the
/// adoption's own high/critical findings, a governance-suite or doctor verdict other than HEALTHY (naming the failing
/// checks). When the doctor's only failing check is D032 — the installation's release authenticity is not established
/// on this machine (an unprovisioned or bootstrap installation, OWNER-DECISION-P2-0002) — and nothing else stands
/// between the adoption and a healthy verdict (every criterion holds, no high adoption finding, and the audit is
/// HEALTHY or finds nothing above `low` outside its own installation-authenticity disclosure), that posture is **the**
/// reason: returned separately, with D032's disclosure and remediation. Empty for `ADOPTED_HEALTHY`.
fn verdict_reasons(
    verdict: &str,
    checks: &[(&str, bool)],
    adoption_high: usize,
    audit: &Value,
    doctor_verdict: &str,
    doctor_checks: &[Value],
) -> (Vec<Value>, Value) {
    if verdict == "ADOPTED_HEALTHY" {
        return (vec![], Value::Null);
    }
    let mut reasons = vec![];
    for (n, ok) in checks {
        if !*ok {
            reasons.push(json!({"kind": "acceptance_criterion", "criterion": n, "message": format!("acceptance criterion not met: {n}")}));
        }
    }
    if adoption_high > 0 {
        reasons.push(json!({"kind": "adoption_findings", "high_or_critical": adoption_high, "message": format!("{adoption_high} high/critical adoption finding(s) open (see Adoption findings)")}));
    }
    let serious =
        |f: &&Value| matches!(f["severity"].as_str(), Some("medium" | "high" | "critical"));
    let audit_findings: Vec<&Value> = audit["findings"]
        .as_array()
        .map(|a| a.iter().filter(serious).collect())
        .unwrap_or_default();
    if audit["verdict"] != "HEALTHY" {
        reasons.push(json!({"kind": "audit", "verdict": audit["verdict"], "counts": audit["counts"], "message": format!("the G5 governance suite's verdict is {} (critical {}, high {}, medium {})", audit["verdict"].as_str().unwrap_or("?"), audit["counts"]["critical"], audit["counts"]["high"], audit["counts"]["medium"])}));
    }
    let failed: Vec<&Value> = doctor_checks
        .iter()
        .filter(|c| !c["ok"].as_bool().unwrap_or(true))
        .collect();
    if doctor_verdict != "HEALTHY" || !failed.is_empty() {
        reasons.push(json!({"kind": "doctor", "verdict": doctor_verdict, "failed": failed.iter().map(|c| json!({"id": c["id"], "severity": c["severity"], "message": c["message"]})).collect::<Vec<_>>(),
            "message": format!("doctor verdict {doctor_verdict}: failing {}", failed.iter().map(|c| c["id"].as_str().unwrap_or("?").to_string()).collect::<Vec<_>>().join(", "))}));
    }
    let only_d032 = failed.len() == 1 && failed[0]["id"] == "D032";
    let rest_ok = checks.iter().all(|(_, ok)| *ok)
        && adoption_high == 0
        && (audit["verdict"] == "HEALTHY"
            || audit_findings
                .iter()
                .all(|f| f["family"] == "installation_authenticity"));
    if !(only_d032 && rest_ok) {
        return (reasons, Value::Null);
    }
    let d = failed[0];
    let posture = &d["posture"];
    let why = json!({"kind": "installation_authenticity", "check": "D032",
        "machine_posture": posture["machine_posture"], "authenticity": posture["authenticity"], "admission": posture["admission"],
        "disclosure": d["message"], "remediation": d["remediation"],
        "message": format!("every adoption acceptance criterion holds and the governance suite accepts the repository; the verdict is {verdict} only because this installation's release authenticity is not established on this machine (doctor D032: machine {}, authenticity {}, admission {}). {}",
            posture["machine_posture"].as_str().unwrap_or("?"), posture["authenticity"].as_str().unwrap_or("?"), posture["admission"].as_str().unwrap_or("?"),
            d["remediation"].as_str().map(|r| format!("Remedy: {r}; then run the audit again.")).unwrap_or_default())});
    // the posture is the reason: it leads, the doctor summary it explains stays listed
    reasons.insert(0, why.clone());
    (reasons, why)
}

/// Whether the recorded verdict of independent stage `stage` was given by its designated role with independence
/// established (the record is the verified baseline, so this is what the OS recorded).
fn independent_verdict(b: &Value, stage: &str) -> bool {
    let v = &b["verdicts"][stage];
    v["independence"]["established"] == true
        && v["role"].as_str().is_some()
        && v["role"].as_str() == designated_role(stage)
}

pub fn status(root: &Path) -> Result<Value> {
    let b = load_baseline_raw(root)?;
    let binding = crate::t2::verify_value(&b, "");
    let mut stages = vec![];
    for s in STAGES {
        stages.push(json!({"stage": s, "status": b["stage_status"][s].as_str().unwrap_or("pending"), "verdict": b["verdicts"][s]["verdict"],
            "by": if b["verdicts"][s].is_object() { json!({"role": b["verdicts"][s]["role"], "session": b["verdicts"][s]["session"], "designated_role": designated_role(s), "independence_established": b["verdicts"][s]["independence"]["established"]}) } else { Value::Null }}));
    }
    let next = STAGES
        .iter()
        .find(|s| b["stage_status"][s].as_str().unwrap_or("pending") != "done")
        .map(|s| s.to_string());
    Ok(
        json!({"adoption_id": b["adoption_id"], "commit": b["commit"], "stages": stages, "next_stage": next, "final_verdict": b["final_verdict"], "evidence_dir": EVIDENCE,
            "record_binding": binding.to_value(), "honoured": binding.is_verified(), "authors": b["authors"]}),
    )
}

pub fn glob_helper(pat: &str, path: &str) -> bool {
    glob_match(pat, path)
}
pub fn read_json_helper(p: &Path) -> Result<Value> {
    read_json(p)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_approval_digest_ignores_os_bookkeeping_but_not_what_happens_to_an_artefact() {
        let e = json!({"artifact_id": "ART-1", "current_path": "src/a.py", "action": "KEEP_IN_PLACE", "batch": 1, "requires_human_gate": false});
        let f = json!({"artifact_id": "ART-2", "current_path": "src/b.py", "action": "MOVE", "target_path": "lib/b.py", "batch": 2});
        let mut e_os = e.clone();
        e_os["human_gate"] = json!("HDG-0001");
        e_os["entry_version"] = json!(3);
        e_os["producer"] = json!({"stage": "A3"});
        let d = planner::catalogue_digest(&[e.clone(), f.clone()]);
        assert_eq!(d, planner::catalogue_digest(&[f.clone(), e_os]));
        let mut e_del = e.clone();
        e_del["action"] = json!("DELETE_FROM_ACTIVE_TREE");
        assert_ne!(d, planner::catalogue_digest(&[e_del, f.clone()]));
        let mut e_gate = e.clone();
        e_gate["requires_human_gate"] = json!(true);
        assert_ne!(d, planner::catalogue_digest(&[e_gate, f]));
    }

    #[test]
    fn a_verdict_is_stale_when_a_bound_artefact_changed_or_was_never_bound() {
        let v = json!({"catalogue_sha256": "a", "plan_sha256": "b", "tests_sha256": "c"});
        let same = json!({"catalogue_sha256": "a", "plan_sha256": "b", "tests_sha256": "c"});
        assert!(binding_changes(&v, &same).is_empty());
        let t = json!({"catalogue_sha256": "a", "plan_sha256": "b", "tests_sha256": "d"});
        assert_eq!(binding_changes(&v, &t), vec!["tests".to_string()]);
        assert_eq!(binding_changes(&json!({}), &same).len(), 3);
    }

    #[test]
    fn plan_digest_ignores_regeneration_stamps_only() {
        let p = json!({"id": PLAN_ID, "version": 1, "batches": [{"batch": 1}, {"batch": 2}]});
        let mut q = p.clone();
        q["last_regenerated_at"] = json!("2026-09-19T00:00:00Z");
        q["last_regenerated_by"] = json!({"stage": "A4"});
        assert_eq!(plan_digest(&p), plan_digest(&q));
        q["batches"].as_array_mut().unwrap().pop();
        assert_ne!(plan_digest(&p), plan_digest(&q));
    }

    #[test]
    fn a_relabelled_heldout_query_keeps_its_identity() {
        let q = json!({"id": "HQ-001", "category": "exact_path", "query": "src/a.py", "expected_refs": ["file:src/a.py"], "forbidden": [], "k": 8, "route": "path"});
        let r = json!({"id": "VQ-9", "category": "verifier", "query": " src/a.py ", "expected_refs": ["file:src/a.py"], "forbidden": [], "k": 3, "route": "path", "note": "mine"});
        assert_eq!(heldout_query_identity(&q), heldout_query_identity(&r));
        let mut s = q.clone();
        s["expected_refs"] = json!(["file:src/b.py"]);
        assert_ne!(heldout_query_identity(&q), heldout_query_identity(&s));
    }

    /// WS-2 R3-9: A11 states why its verdict is not ADOPTED_HEALTHY, and when the only thing between the adoption and
    /// a healthy verdict is D032 (installation authenticity not established on this machine), that posture is the
    /// reason, with D032's own disclosure and remediation. The D032 check is the real one for an unestablished
    /// installation (`srr::installation::doctor_check`).
    #[test]
    fn a11_names_the_installation_posture_when_it_is_the_only_reason() {
        let dir = std::env::temp_dir().join(format!("gov-a11-{}", crate::util::short_uuid()));
        std::fs::create_dir_all(&dir).unwrap();
        let mut d032 = crate::srr::installation::doctor_check(&dir, "D032");
        assert_eq!(d032["ok"], false);
        d032["posture"]["machine_posture"] = json!("UNPROVISIONED");
        d032["posture"]["admission"] = json!("BOOTSTRAP_EMBEDDED_PAYLOAD");
        let ok = |id: &str| json!({"id": id, "ok": true, "severity": "info", "message": "ok"});
        let checks: Vec<(&str, bool)> = vec![
            ("migration baseline pinned", true),
            ("independent memory verifier passed", true),
        ];
        let healthy = json!({"verdict": "HEALTHY", "counts": {"critical": 0, "high": 0, "medium": 0}, "findings": [
            {"family": "installation_authenticity", "severity": "low", "message": "bootstrap"}]});
        // healthy: nothing to explain
        let (r, why) = verdict_reasons(
            "ADOPTED_HEALTHY",
            &checks,
            0,
            &healthy,
            "HEALTHY",
            &[ok("D001")],
        );
        assert!(r.is_empty() && why.is_null());
        // D032 alone: the posture is the reason
        let (r, why) = verdict_reasons(
            "NOT_ADOPTED_HEALTHY",
            &checks,
            0,
            &healthy,
            "DEGRADED",
            &[ok("D001"), d032.clone()],
        );
        assert_eq!(why["kind"], "installation_authenticity");
        assert_eq!(why["machine_posture"], "UNPROVISIONED");
        assert_eq!(why["admission"], "BOOTSTRAP_EMBEDDED_PAYLOAD");
        assert_eq!(why["disclosure"], d032["message"]);
        assert_eq!(why["remediation"], d032["remediation"]);
        assert!(why["message"]
            .as_str()
            .unwrap()
            .contains("only because this installation's release authenticity is not established"));
        assert_eq!(r[0], why, "the posture leads the reasons");
        // the suite's own disclosure of the same posture (a medium installation_authenticity finding) does not hide it
        let disclosed = json!({"verdict": "DEGRADED", "counts": {"critical": 0, "high": 0, "medium": 1}, "findings": [
            {"family": "installation_authenticity", "severity": "medium", "message": "not established"}]});
        let (_, why) = verdict_reasons(
            "NOT_ADOPTED_HEALTHY",
            &checks,
            0,
            &disclosed,
            "DEGRADED",
            &[d032.clone()],
        );
        assert_eq!(why["kind"], "installation_authenticity");
        // anything else failing too: every reason is listed and the posture is not singled out
        let mut other = ok("D021");
        other["ok"] = json!(false);
        let (r, why) = verdict_reasons(
            "NOT_ADOPTED_HEALTHY",
            &checks,
            0,
            &healthy,
            "DEGRADED",
            &[d032.clone(), other],
        );
        assert!(why.is_null());
        assert_eq!(r.len(), 1);
        assert!(r[0]["message"].as_str().unwrap().contains("D032, D021"));
        let failing: Vec<(&str, bool)> = vec![("migrated paths/imports/links pass", false)];
        let (r, why) = verdict_reasons(
            "NOT_ADOPTED_HEALTHY",
            &failing,
            2,
            &healthy,
            "DEGRADED",
            &[d032],
        );
        assert!(why.is_null());
        let kinds: Vec<&str> = r.iter().map(|x| x["kind"].as_str().unwrap()).collect();
        assert_eq!(
            kinds,
            vec!["acceptance_criterion", "adoption_findings", "doctor"]
        );
        let _ = std::fs::remove_dir_all(&dir);
    }

    /// Contract v3 A3: who may run a command test is decided by policy for the executing role — its TOOL_PERMISSIONS
    /// entry when listed (an explicit entry is authoritative, even an empty one), the A7 designated verifier's
    /// protocol duty when it is not listed, and nothing for anyone else.
    #[test]
    fn command_test_permissions_come_from_policy_and_the_designated_duty() {
        let dir = std::env::temp_dir().join(format!("gov-cmdpol-{}", crate::util::short_uuid()));
        std::fs::create_dir_all(&dir).unwrap();
        let b = json!({"baseline_tests": {"command": ["python3", "-m", "pytest", "-q"], "dir": "", "status": "passed"}});
        let ex = command_policy(&dir, &b, "A6", "migration-executor");
        assert!(
            ex.permissions.contains(&"RUN_TESTS".to_string()),
            "{:?}",
            ex.permissions
        );
        assert!(ex
            .permission_basis
            .starts_with("TOOL_PERMISSIONS.roles.migration-executor"));
        assert_eq!(
            ex.governed.last().unwrap().command,
            vec!["python3", "-m", "pytest", "-q"]
        );
        let v = command_policy(&dir, &b, "A7", "migration-verifier");
        assert!(v.permissions.contains(&"RUN_TESTS".to_string()));
        assert!(v.permission_basis.contains("designated role"));
        let r = command_policy(&dir, &b, "A7", "migration-reviewer");
        assert!(r.permissions.is_empty(), "{:?}", r.permissions);
        let t =
            json!({"id": "RT-1", "kind": "command", "command": ["python3", "-m", "pytest", "-q"]});
        assert!(verify::command_test_refusal(&t, &v).is_none());
        assert!(verify::command_test_refusal(&t, &r).is_some());
        // an explicit TOOL_PERMISSIONS entry decides, even an empty one for the designated verifier
        let (p, basis) = test_permissions(Some(vec![]), "A7", "migration-verifier", "overlay");
        assert!(p.is_empty() && basis.starts_with("TOOL_PERMISSIONS.roles.migration-verifier"));
        let (p, _) = test_permissions(None, "A6", "migration-executor", "overlay");
        assert!(p.is_empty(), "no designated duty at A6");
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn every_designated_independent_role_is_a_read_only_kernel_role() {
        let roles: Value =
            read_yaml(&Path::new(env!("CARGO_MANIFEST_DIR")).join("../framework/roles/ROLES.yaml"))
                .unwrap();
        for (stage, role, _) in DESIGNATED_ROLES {
            let r = roles["roles"]
                .as_array()
                .unwrap()
                .iter()
                .find(|r| r["id"].as_str() == Some(role))
                .unwrap_or_else(|| panic!("{stage}: {role} is not a kernel role"));
            assert_eq!(
                r["level"], "L0",
                "{stage}: an independent role authors no builder stage"
            );
            assert_eq!(designated_role(stage), Some(*role));
        }
        assert!(designated_role("A6").is_none());
        // every adoption command is specified, and only the four independent stages are Independent
        for c in [
            "baseline",
            "inventory",
            "classify",
            "map",
            "plan",
            "test-design",
            "review",
            "migrate",
            "rollback",
            "verify-migration",
            "extract-legacy",
            "build-memory",
            "verify-memory",
            "audit",
        ] {
            let s = spec(c);
            assert_eq!(
                s.group == Group::Independent,
                designated_role(s.stage).is_some()
                    && c != "test-design"
                    && c != "rollback"
                    && c != "migrate",
                "{c}"
            );
        }
    }
}
