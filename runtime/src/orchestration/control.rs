//! Emergency controls (framework §74): PAUSE, FREEZE_WRITES, CANCEL_AGENTS, RESUME. Authority-checked; state lives in
//! the runtime directory (never inside the rebuild-deleted index) and is honoured by every mutating operation.
//!
//! ## G0 — the guard every command passes (Contract v3 O5 "G0 Guard — every privileged/mutating command"; BC-P2-08)
//!
//! [`COMMAND_GUARDS`] classifies **every `gov` command** (the CLI resolves each invocation to one label here before
//! dispatch; a label that is not classified is refused, so a command added later cannot run unguarded). Each entry
//! states:
//!
//! * the **authority class** (`AUTHORITY_POLICY.authority_levels_required.<class>`) the declared acting role must
//!   meet — every command that writes authoritative, governed or governed-test state has one;
//! * the **effect** — `Read` (no governed write), `Write` (refused while `FREEZE_WRITES` or `PAUSE` is in force),
//!   or one of the two explicit, listed recovery allow-lists ([`FROZEN_ALLOW_LIST`], [`PAUSED_ALLOW_LIST`]).
//!
//! Nothing changes governed state while `FREEZE_WRITES`/`PAUSE` forbids it except the operations those two lists name,
//! each with its reason (framework §74: the emergency controls themselves and `ROLLBACK_TRANSACTION`).
//!
//! The operation-level `guard_write` (kernel integrity, `OWNER-DECISION-0006` §6 bullet 1, emergency state) is
//! unchanged and still runs inside every runtime path that called it; G0 adds the emergency-state and authority
//! decision for every command *at the command boundary*, including the ones whose runtime path never called it.
use crate::authority;
use crate::util::{now_iso, read_json, write_json};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};

pub fn path(p: &Project) -> std::path::PathBuf {
    p.runtime_dir().join("control.json")
}

pub fn state(p: &Project) -> Value {
    read_json(&path(p)).unwrap_or(json!({"mode": "RUNNING", "writes_frozen": false, "agents_cancelled": false, "updated_at": null, "reason": null}))
}

pub fn set(p: &Project, mode: &str, reason: Option<&str>) -> Result<Value> {
    authority::require(
        p,
        if mode == "RESUME" {
            "resume_control"
        } else {
            "emergency_control"
        },
    )?;
    let mut s = state(p);
    match mode {
        "PAUSE" => {
            s["mode"] = json!("PAUSED");
        }
        "FREEZE_WRITES" => {
            s["writes_frozen"] = json!(true);
        }
        "CANCEL_AGENTS" => {
            s["agents_cancelled"] = json!(true);
            s["mode"] = json!("PAUSED");
        }
        "RESUME" => {
            s["mode"] = json!("RUNNING");
            s["writes_frozen"] = json!(false);
            s["agents_cancelled"] = json!(false);
        }
        _ => {
            return Err(GovError::new(
                "USAGE",
                format!("unknown control mode {mode}"),
            ))
        }
    }
    s["updated_at"] = json!(now_iso());
    s["reason"] = json!(reason);
    s["session"] = json!(p.session_id);
    s["role"] = json!(p.role);
    write_json(&path(p), &s)?;
    Ok(s)
}

/// Every mutating governance operation calls this first.
pub fn guard_write(p: &Project, operation: &str) -> Result<()> {
    // constitutional floors must come from a verified kernel before any governed mutation (verifier V-H2)
    crate::kernel_trust::guard(p, operation)?;
    // OWNER-DECISION-0006 §6: while this machine is marked `DEGRADED — RECOVERY ONLY`, normal privileged
    // Governance OS operation, Human Gate creation/approval, release certification, trust-policy mutation and
    // privileged plugin/profile acquisition are refused. Inspection, backup/export, diagnosis, repair,
    // uninstall/reinstall and restoration of an authenticated release stay available (§5).
    crate::srr::breakglass::guard_light(crate::FRAMEWORK_NAME, operation)?;
    guard_emergency_state(p, operation)
}

/// The emergency-control half of the guard: refuse `operation` while FREEZE_WRITES or PAUSE is in force.
pub fn guard_emergency_state(p: &Project, operation: &str) -> Result<()> {
    let s = state(p);
    if s["writes_frozen"].as_bool().unwrap_or(false) {
        return Err(frozen(operation, &s));
    }
    if s["mode"].as_str() == Some("PAUSED") {
        return Err(paused(operation, &s));
    }
    Ok(())
}

fn frozen(operation: &str, s: &Value) -> GovError {
    GovError::new("FROZEN", format!("writes are frozen (FREEZE_WRITES active); '{operation}' refused. Run `gov resume` (L4) to lift.")).with_details(json!({"operation": operation, "control": s, "allowed_while_frozen": FROZEN_ALLOW_LIST.iter().map(|(l, why)| json!({"operation": l, "reason": why})).collect::<Vec<_>>()}))
}

fn paused(operation: &str, s: &Value) -> GovError {
    GovError::new(
        "PAUSED",
        format!("execution is paused; '{operation}' refused. Run `gov resume` to continue."),
    )
    .with_details(json!({"operation": operation, "control": s, "allowed_while_paused": PAUSED_ALLOW_LIST.iter().map(|(l, why)| json!({"operation": l, "reason": why})).collect::<Vec<_>>()}))
}

// ------------------------------------------------------------------------------------------------ G0 guard table

/// What a command does to governed state.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Effect {
    /// Reads only (it may append to the telemetry/observability log, which every invocation does).
    Read,
    /// Writes authoritative, governed, governed-test, derived or evidence state: refused under FREEZE_WRITES and
    /// PAUSE unless the label is on the matching allow-list.
    Write,
}

/// Where the command operates.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Scope {
    /// A governed project: the G0 decision is made against the project's policy and control state (or, before the
    /// first install, against the kernel embedded in this binary).
    Project,
    /// Machine trust domain, canonical-repository release tooling or a capability protocol endpoint: no governed
    /// project exists to guard. Each such command carries its own control (`OWNER-DECISION-0006` §6 effect guards,
    /// the Signed Release Root verifier) and is listed so that its exemption is explicit, not accidental.
    Outside(&'static str),
}

#[derive(Debug, Clone, Copy)]
pub struct CommandGuard {
    pub label: &'static str,
    /// `AUTHORITY_POLICY.authority_levels_required` class the declared acting role must meet.
    pub authority: Option<&'static str>,
    pub effect: Effect,
    pub scope: Scope,
}

const fn g(label: &'static str, authority: &'static str, effect: Effect) -> CommandGuard {
    CommandGuard {
        label,
        authority: Some(authority),
        effect,
        scope: Scope::Project,
    }
}
const fn outside(label: &'static str, why: &'static str) -> CommandGuard {
    CommandGuard {
        label,
        authority: None,
        effect: Effect::Read,
        scope: Scope::Outside(why),
    }
}

use Effect::{Read, Write};

/// **Every `gov` command, classified.** The CLI maps each invocation to exactly one label (`cli/src/main.rs::g0_label`)
/// and calls [`g0`] before dispatch; the certification suite checks that every label the CLI can produce is here and
/// that every authority class named here exists in the kernel `AUTHORITY_POLICY`.
pub const COMMAND_GUARDS: &[CommandGuard] = &[
    outside("version", "prints build identity; touches nothing"),
    g("init", "install_kernel", Write),
    g("status", "read", Read),
    g("continue", "read", Write),
    g("continue --claim", "claim_task", Write),
    g("gate answer", "answer_gate", Write),
    g("audit", "record_audit", Write),
    g("audit --no-persist", "read", Read),
    g("verify governance", "record_audit", Write),
    // integration P2-AR-0022: with WS-2 (BC-P2-43) `verify product` records its per-family results as a governed
    // EVIDENCE audit record (`scope: product-tests`), so it is a write of the `record_audit` class like `audit`
    g("verify product", "record_audit", Write),
    g("pause", "emergency_control", Write),
    g("freeze writes", "emergency_control", Write),
    g("cancel agents", "emergency_control", Write),
    g("resume", "resume_control", Write),
    g("doctor", "read", Read),
    g("rebuild-memory", "rebuild_memory", Write),
    g("recover", "recover", Write),
    g("recover --dry-run", "read", Read),
    g("adopt baseline", "adoption_plan", Write),
    g("adopt inventory", "adoption_plan", Write),
    g("adopt classify", "adoption_plan", Write),
    g("adopt map", "adoption_plan", Write),
    g("adopt plan", "adoption_plan", Write),
    g("adopt test-design", "adoption_plan", Write),
    g("adopt review", "adoption_review", Write),
    g("adopt migrate", "migrate_execute", Write),
    g("adopt verify-migration", "adoption_review", Write),
    g("adopt extract-legacy", "migrate_execute", Write),
    g("adopt build-memory", "build_memory", Write),
    g("adopt verify-memory", "adoption_review", Write),
    g("adopt audit", "adoption_review", Write),
    g("adopt status", "read", Read),
    g("adopt rollback", "migrate_execute", Write),
    g("update --check", "read", Read),
    g("update --apply", "update_apply", Write),
    g("update --rollback", "update_apply", Write),
    outside("trust status", "machine trust domain: read-only posture report"),
    outside("trust provision", "machine trust domain (administrator): OWNER-DECISION-0006 §6 bullet 4 is enforced inside the trust-anchor write"),
    outside("trust root-update", "machine trust domain (administrator): succession requires the outgoing and incoming root quorums; §6 bullet 4 enforced inside the trust-anchor write"),
    outside("trust break-glass", "machine trust domain: read-only report of where an owner-signed authorisation must be placed"),
    outside("trust recover-transactions", "machine trust domain: replays interrupted install transactions (crash recovery of the verifier's own journal)"),
    outside("trust human-channel", "machine trust domain: read-only report of the authenticated human channel"),
    outside("trust human-channel --provision", "machine trust domain (administrator): the human-channel anchor write asks OWNER-DECISION-0006 §6 bullet 4 inside the write and refuses a provisioned or already-anchored machine"),
    outside("contract verify", "canonical-repository tooling: read-only"),
    outside("contract compile", "canonical-repository release tooling (regenerates the compiled contract views of the canonical repository, not a governed project)"),
    g("upstream prepare", "upstream_prepare", Write),
    g("upstream submit", "upstream_submit", Write),
    g("task create", "create_task", Write),
    g("task list", "read", Read),
    g("task show", "read", Read),
    g("task status", "mutate_task_status", Write),
    g("task claim", "claim_task", Write),
    g("task release", "release_task", Write),
    g("task release --force", "force_release_task", Write),
    g("task close", "close_task", Write),
    g("task close --force", "force_close_task", Write),
    g("task dag", "read", Read),
    g("replan", "replan_tasks", Write),
    g("cit propose", "propose_cit", Write),
    g("cit simulate", "simulate_cit", Write),
    g("cit approve", "approve_cit_auto", Write),
    g("cit reject", "reject_cit", Write),
    g("cit execute", "execute_cit", Write),
    g("cit rollback", "rollback_cit", Write),
    g("cit list", "read", Read),
    g("cit show", "read", Read),
    g("context compile", "compile_context", Write),
    // integration P2-AR-0022 (WS-4, BC-P2-17/19/20): resolution, verification and display of the manifest and of the
    // packet history, and a dry-run receipt validation — none of them writes
    g("context manifest", "read", Read),
    g("context verify", "read", Read),
    g("context show", "read", Read),
    g("context receipt", "read", Read),
    g("checkpoint", "checkpoint", Write),
    g("checkpoint latest", "read", Read),
    g("skills list", "read", Read),
    g("skills resolve", "read", Read),
    g("tools list", "read", Read),
    g("tools registry", "generate_tool_registry", Write),
    g("tools resolve", "read", Read),
    g("tools install", "install_tool", Write),
    g("tools health", "read", Read),
    g("handoff create", "create_handoff", Write),
    g("handoff return", "return_handoff", Write),
    g("memory query", "read", Read),
    g("memory verify", "read", Read),
    g("memory freshness", "read", Read),
    g("memory rebuild", "rebuild_memory", Write),
    g("memory graph", "read", Read),
    g("memory impact", "read", Read),
    g("memory benchmark", "memory_benchmark", Read),
    g("memory benchmark --record", "memory_benchmark", Write),
    g("memory select", "memory_select", Write),
    g("memory heldout-starter", "regenerate_heldout_set", Write),
    g("gate create", "create_gate", Write),
    g("gate present", "present_gate", Write),
    g("gate list", "read", Read),
    g("gate show", "read", Read),
    g("gate revoke", "revoke_gate", Write),
    g("readiness check", "read", Read),
    g("readiness plan", "readiness_plan", Write),
    g("intent", "read", Read),
    g("route", "read", Read),
    g("route --report", "read", Read),
    g("route --record", "record_routing_evidence", Write),
    g("telemetry summary", "read", Read),
    g("telemetry emit", "emit_telemetry", Write),
    g("adapters generate", "generate_adapters", Write),
    g("adapters verify", "read", Read),
    outside("release build", "canonical-repository release tooling: certification is refused below floor inside `release::build` (§6 bullet 3); it writes no governed project"),
    outside("release verify", "canonical-repository release tooling: read-only"),
    g("kernel verify", "read", Read),
    g("kernel trust", "read", Read),
    g("kernel reinstall", "install_kernel", Write),
    g("kernel override", "override_kernel_integrity", Write),
    g("capabilities ecosystems", "read", Read),
    g("capabilities plugins", "read", Read),
    g("capabilities invoke", "execute_plugin", Write),
    outside("capabilities serve-embed", "capability protocol endpoint (gov-capability/1 over stdin/stdout); it opens no project"),
    g("claims list", "read", Read),
    g("claims sweep", "sweep_claims", Write),
    g("mcp", "read", Read),
    outside("lessons cluster", "canonical-repository framework-lesson intake tooling, not a governed project"),
    g("plugins register", "register_plugin", Write),
    g("plugins unregister", "register_plugin", Write),
    g("plugins registry", "read", Read),
    g("plugins list", "read", Read),
    g("plugins health", "read", Read),
    g("plugins health --ping", "execute_plugin", Write),
    g("policy overrides", "read", Read),
    g("policy effective", "read", Read),
    // ---- integration P2-AR-0022: subcommands added by round-1 workstreams other than WS-3
    // WS-4 (BC-P2-21): artefact identity and lineage read governed records, VCS history and the index
    g("artefact show", "read", Read),
    g("artefact check", "read", Read),
    g("artefact lineage", "read", Read),
    // WS-2 (BC-P2-03/06/42/43): the health scheduler. A run persists a governance-suite EVIDENCE audit record when
    // it re-establishes currency (as `audit` does); `--no-persist` never does (as `audit --no-persist`). The
    // product-test run records a product-tests EVIDENCE audit record; the close check runs the G2 tier with the
    // same record policy as a run. `skills --record` binds skill versions in the tracked, OS-written
    // governance/generated/skill-bindings.json (`skills::record` requires `record_skill_binding`). The rest read
    // (their runtime-local cache, ledger and observation files are derived, machine-local state).
    g("health run", "record_audit", Write),
    g("health run --no-persist", "read", Read),
    g("health status", "read", Read),
    g("health checks", "read", Read),
    g("health history", "read", Read),
    g("health show", "read", Read),
    g("health guard", "read", Read),
    g("health currency", "read", Read),
    g("health product", "record_audit", Write),
    g("health skills", "read", Read),
    g("health skills --record", "record_skill_binding", Write),
    g("health close-check", "record_audit", Write),
    // WS-2 round 2 (P2-AR-0023): the G6 entry point validates the oracle/report (read-only) and records the
    // qualification run's health as a governance-suite EVIDENCE record, exactly as `health run` does
    g("health qualify", "record_audit", Write),
    // WS-1/12 (BC-P2-51): the Qualification Oracle format tool reads documents held in verifier custody and the
    // format compiled into this binary; it opens no project
    outside("oracle format", "qualification tooling: prints the Qualification Oracle format compiled into this binary; opens no project"),
    outside("oracle validate", "qualification tooling: read-only validation of verifier-custody oracle / score-report documents; opens no governed project"),
];

/// **The FREEZE_WRITES recovery allow-list** — the only writes permitted while writes are frozen, with the reason.
pub const FROZEN_ALLOW_LIST: &[(&str, &str)] = &[
    ("pause", "emergency control (framework §74): the human can always escalate a freeze to a pause"),
    ("freeze writes", "emergency control (framework §74): idempotent re-assertion of the freeze itself"),
    ("cancel agents", "emergency control (framework §74)"),
    ("resume", "emergency control (framework §74): the only way out of the freeze (L4, resume_control)"),
    ("cit rollback", "ROLLBACK_TRANSACTION (framework §74): restoring a transaction's pre-execution snapshot is an emergency control, not new work"),
    ("telemetry emit", "observability evidence: 'recovery from emergency controls is auditable' (Contract v3 A5); it appends to the telemetry log only"),
];

/// **The PAUSE recovery allow-list** — the only writes permitted while execution is paused, with the reason.
pub const PAUSED_ALLOW_LIST: &[(&str, &str)] = &[
    ("pause", "emergency control (framework §74): idempotent"),
    ("freeze writes", "emergency control (framework §74): a pause may be tightened into a freeze"),
    ("cancel agents", "emergency control (framework §74)"),
    ("resume", "emergency control (framework §74): the only way out of the pause (L4, resume_control)"),
    ("cit rollback", "ROLLBACK_TRANSACTION (framework §74)"),
    ("telemetry emit", "observability evidence (Contract v3 A5)"),
    ("gate present", "surfacing a pending question to the human is not agent work: the human must be able to see what the paused work is waiting on (it records the OS rendering of the package, nothing else)"),
];

/// Commands that exist to act on an unverified installed kernel: their own authority refusal is the one reported.
const KERNEL_REMEDIATION: &[&str] = &["kernel override"];

/// The classification of `label`, or `None` when the command is not classified (and must therefore be refused).
pub fn command_guard(label: &str) -> Option<&'static CommandGuard> {
    COMMAND_GUARDS.iter().find(|c| c.label == label)
}

fn allowed(list: &[(&str, &str)], label: &str) -> bool {
    list.iter().any(|(l, _)| *l == label)
}

/// **The G0 decision for one command invocation.**
///
/// 1. An unclassified label is refused (`G0_UNCLASSIFIED`): a command nobody classified must not run unguarded.
/// 2. On an installed project, a `Write` command is refused under FREEZE_WRITES / PAUSE unless its label is on the
///    matching allow-list.
/// 3. The declared acting role must meet the command's authority class — against the project's verified policy,
///    or, on a repository with no installed kernel (first `init`, pre-install `adopt` stages), against the kernel
///    embedded in this binary.
pub fn g0(p: &Project, label: &str) -> Result<&'static CommandGuard> {
    let guard = command_guard(label).ok_or_else(|| {
        GovError::new(
            "G0_UNCLASSIFIED",
            format!("command '{label}' has no G0 classification (orchestration::control::COMMAND_GUARDS); an unclassified command is refused rather than run unguarded"),
        )
    })?;
    if let Scope::Outside(_) = guard.scope {
        return Ok(guard);
    }
    let installed = p.is_installed();
    if installed && guard.effect == Effect::Write {
        let s = state(p);
        if s["writes_frozen"].as_bool().unwrap_or(false) && !allowed(FROZEN_ALLOW_LIST, label) {
            return Err(frozen(label, &s));
        }
        if s["mode"].as_str() == Some("PAUSED") && !allowed(PAUSED_ALLOW_LIST, label) {
            return Err(paused(label, &s));
        }
    }
    if let Some(class) = guard.authority {
        let decided = if installed {
            authority::require(p, class)
        } else {
            authority::require_with_embedded_kernel(&p.role, class)
        };
        if let Err(denied) = decided {
            // When the installed kernel cannot be verified, the authority levels themselves are unverified: the
            // more fundamental refusal (KERNEL_TAMPERED, with its remediation) is the one reported.
            if installed && guard.effect == Effect::Write && !KERNEL_REMEDIATION.contains(&label) {
                crate::kernel_trust::guard(p, label)?;
            }
            return Err(denied);
        }
    }
    Ok(guard)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn labels_are_unique_and_allow_lists_name_classified_writes() {
        let mut seen = std::collections::BTreeSet::new();
        for c in COMMAND_GUARDS {
            assert!(seen.insert(c.label), "duplicate G0 label {}", c.label);
            if c.effect == Effect::Write {
                assert!(
                    c.authority.is_some(),
                    "{} writes but has no authority class",
                    c.label
                );
            }
        }
        for (l, why) in FROZEN_ALLOW_LIST.iter().chain(PAUSED_ALLOW_LIST) {
            let c =
                command_guard(l).unwrap_or_else(|| panic!("allow-listed '{l}' is not classified"));
            assert_eq!(
                c.effect,
                Effect::Write,
                "{l} is allow-listed but is not a write"
            );
            assert!(why.len() > 10);
        }
    }

    #[test]
    fn every_authority_class_exists_in_the_kernel_authority_policy() {
        let doc: Value = serde_yaml::from_slice(
            crate::kernel::embedded::files()
                .iter()
                .find(|(r, _)| *r == "policies/AUTHORITY_POLICY.yaml")
                .map(|(_, b)| *b)
                .expect("embedded AUTHORITY_POLICY"),
        )
        .unwrap();
        for c in COMMAND_GUARDS {
            if let Some(class) = c.authority {
                assert!(
                    doc["authority_levels_required"][class].as_str().is_some(),
                    "G0 label '{}' names authority class '{class}', which AUTHORITY_POLICY does not declare",
                    c.label
                );
            }
        }
    }
}
