//! The health-check catalogue: for every check the scheduler can run or record, its declared input dependencies,
//! the key extras it reads outside the repository tree, its isolation need, its reproducibility treatment, the tiers
//! it belongs to and its **hard-block vs warning** semantics (Contract v3:801-808).
//!
//! The declarations are data, reviewable in one place and reported by `gov health checks`. A check's cache key is
//! derived from exactly the classes and extras declared here, so an undeclared dependency is a defect in this table,
//! not something the scheduler guesses.
use super::Tier;
use crate::verification::currency;
use serde_json::{json, Value};

/// Which surface implements the check.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Surface {
    /// A governance-suite family (`crate::verification`).
    Family,
    /// A `gov doctor` check (`crate::doctor`).
    Doctor,
}

/// State outside the repository tree that a check reads; each extra contributes its own digest to the cache key.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Extra {
    /// The derived index content (`state.db`: artefacts, chunks, vectors, edges, exclusions, meta).
    LiveIndex,
    /// The claims store (`claims.db`).
    Claims,
    /// The latest recorded product-test evidence (records excluded from the file classes as health outputs).
    ProductEvidence,
    /// This machine's skill-version observations (`.governance-runtime/health/skills-observed.json`).
    SkillObservations,
    /// This machine's plugin observations (`.governance-runtime/plugins/observed.json`).
    PluginObservations,
    /// The deep flag (a deep run measures something different from a normal run).
    DeepMode,
    /// The owner-source contract chain `contracts::verify` binds (in the audited repository or the developer checkout
    /// named by `GOV_CANONICAL_ROOT`), which may lie outside the project tree.
    ContractSource,
    /// The commits that define the governance baseline (version-control history, not tree content).
    GovernanceBaseline,
}

/// Where the check may run.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Isolation {
    /// Pure reader: runs in-process on the live project, concurrently with other readers.
    InProcess,
    /// Writes derived state (context packets, retrieval log, full index rebuilds): runs against a disposable copy
    /// of the project and its runtime state, never the live repository.
    Sandbox,
    /// Manages its own disposable sandboxes (one per executed scenario).
    OwnSandboxes,
}

/// How a result is shown to be reproducible.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Repro {
    /// Executed twice concurrently on identical inputs; different result hashes are an `audit_reproducibility` finding.
    DoubleRun,
    /// The check establishes reproducibility itself (e.g. compiles twice, rebuilds twice) or is not deterministic by
    /// design (time/machine-dependent); executed once.
    SelfChecked,
}

/// Whether a result may be served from the cache.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Cache {
    Cacheable,
    /// Time- or session-dependent: always executed (cheap).
    Never,
}

/// Governed operations a hard-block can refuse. The remedies (doctor, audit, health, recover, rebuild-memory,
/// resume/pause/freeze, kernel reinstall/verify, gate present/answer, checkpoint) are never in this vocabulary.
pub mod ops {
    pub const TASK_CREATE: &str = "task.create";
    pub const TASK_CLAIM: &str = "task.claim";
    pub const TASK_CLOSE: &str = "task.close";
    pub const CIT_PROPOSE: &str = "cit.propose";
    pub const CIT_APPROVE: &str = "cit.approve";
    pub const CIT_EXECUTE: &str = "cit.execute";
    pub const HANDOFF_CREATE: &str = "handoff.create";
    pub const RELEASE_BUILD: &str = "release.build";
    pub const UPDATE_APPLY: &str = "update.apply";
    pub const ADOPT_MIGRATE: &str = "adopt.migrate";
    pub const ALL: &[&str] = &[
        TASK_CREATE,
        TASK_CLAIM,
        TASK_CLOSE,
        CIT_PROPOSE,
        CIT_APPROVE,
        CIT_EXECUTE,
        HANDOFF_CREATE,
        RELEASE_BUILD,
        UPDATE_APPLY,
        ADOPT_MIGRATE,
    ];
}

/// Every governed-work operation: a critical integrity failure refuses all of them.
pub const GOVERNED_WORK: &[&str] = ops::ALL;
/// Operations that rely on the verified state of the repository (close, commit a change, ship).
pub const RELY_ON_STATE: &[&str] = &[
    ops::TASK_CLOSE,
    ops::CIT_EXECUTE,
    ops::RELEASE_BUILD,
    ops::UPDATE_APPLY,
];

/// How a failure is scoped when it blocks.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BlockScope {
    /// Every invocation of the listed operations.
    Global,
    /// Only invocations whose paths intersect the failing finding's `covers` globs (product-test families).
    CoveredPaths,
}

/// A hard-block rule: findings at or above `min_severity` refuse `operations`.
#[derive(Debug, Clone, Copy)]
pub struct BlockRule {
    pub min_severity: &'static str,
    pub operations: &'static [&'static str],
    pub scope: BlockScope,
}

#[derive(Debug, Clone, Copy)]
pub struct CheckDef {
    pub id: &'static str,
    pub surface: Surface,
    pub duty: &'static str,
    /// Input classes (`crate::verification::currency`) or groups (`@kernel`, `@overlay`, `@records`, `@files`).
    pub deps: &'static [&'static str],
    pub extras: &'static [Extra],
    pub isolation: Isolation,
    pub repro: Repro,
    pub cache: Cache,
    pub tiers: &'static [Tier],
    /// Empty = warning only (a failure lowers the verdict but refuses nothing).
    pub blocks: &'static [BlockRule],
}

/// Classes every check reads implicitly: the implementation, the constitutional policy/schema payload and the lock,
/// and the project policy overlay (effective policy = kernel + overlay).
pub const IMPLICIT_DEPS: &[&str] = &[
    currency::RUNTIME_IDENTITY,
    "kernel_policy",
    "kernel_schema",
    "kernel_other",
    "framework_lock",
    "project_policy",
];

const KERNEL: &[&str] = &[
    "kernel_policy",
    "kernel_schema",
    "kernel_migration",
    "kernel_skills",
    "kernel_tools",
    "kernel_other",
    "framework_lock",
];
const OVERLAY: &[&str] = &[
    "project_policy",
    "path_map",
    "sensitivity",
    "model_profile",
    "tools_plugins",
    "project_skills",
    "overlay_other",
];
const RECORDS: &[&str] = &[
    "spec_decisions",
    "spec_requirements",
    "spec_architecture",
    "spec_tasks",
    "research_experiments",
    "continuity_records",
    "evidence_records",
    "adoption_evidence",
    "spec_other",
    "archive",
];

/// Expand a check's declared dependencies (groups included) plus the implicit ones, sorted and de-duplicated.
pub fn expand_deps(def: &CheckDef) -> Vec<&'static str> {
    let mut out: Vec<&'static str> = IMPLICIT_DEPS.to_vec();
    for d in def.deps {
        match *d {
            "@kernel" => out.extend_from_slice(KERNEL),
            "@overlay" => out.extend_from_slice(OVERLAY),
            "@records" => out.extend_from_slice(RECORDS),
            "@files" => {
                for id in currency::all_class_ids() {
                    if !currency::NON_FILE_CLASSES.contains(&id) {
                        out.push(id);
                    }
                }
            }
            other => out.push(other),
        }
    }
    out.sort();
    out.dedup();
    out
}

const CRIT_ALL: BlockRule = BlockRule {
    min_severity: "critical",
    operations: GOVERNED_WORK,
    scope: BlockScope::Global,
};
const HIGH_RELY: BlockRule = BlockRule {
    min_severity: "high",
    operations: RELY_ON_STATE,
    scope: BlockScope::Global,
};

use Tier::*;

/// The catalogue. Order is the report order.
pub const CHECKS: &[CheckDef] = &[
    // ------------------------------------------------------------------ governance-suite families (TEST_POLICY)
    CheckDef {
        id: "schema_invariants",
        surface: Surface::Family,
        duty: "records and overlay valid against kernel schemas; lifecycle/state classes; duplicate ids; superseded-but-ACTIVE authority; no hidden Qualification Oracle record in the governed repository",
        deps: &["@kernel", "@overlay", "@records"],
        extras: &[],
        isolation: Isolation::InProcess,
        repro: Repro::DoubleRun,
        cache: Cache::Cacheable,
        tiers: &[G1, G2, G4, G5, G6],
        blocks: &[CRIT_ALL, HIGH_RELY],
    },
    CheckDef {
        id: "graph_integrity",
        surface: Surface::Family,
        duty: "relationship graph (dangling edges), records outside their canonical location (W1), stale lineage links (W8), task DAG (cycles, missing dependencies, `blocks` naming no task)",
        deps: &["@records", "index_manifest"],
        extras: &[Extra::LiveIndex],
        isolation: Isolation::InProcess,
        repro: Repro::DoubleRun,
        cache: Cache::Cacheable,
        tiers: &[G1, G2, G4, G5, G6],
        blocks: &[BlockRule {
            min_severity: "high",
            operations: &[ops::TASK_CLAIM, ops::TASK_CLOSE, ops::RELEASE_BUILD],
            scope: BlockScope::Global,
        }],
    },
    CheckDef {
        id: "index_freshness",
        surface: Surface::Family,
        duty: "tracked index manifest matches the working tree and the policy pins",
        deps: &["@files"],
        extras: &[],
        isolation: Isolation::InProcess,
        repro: Repro::DoubleRun,
        cache: Cache::Cacheable,
        tiers: &[G1, G2, G4, G5, G6],
        blocks: &[],
    },
    CheckDef {
        id: "memory_retrieval_regression",
        surface: Surface::Family,
        duty: "held-out retrieval regression (recall@k, MRR, stale/superseded/forbidden hits) against the live index",
        deps: &["governance_tests", "index_manifest", "@overlay"],
        extras: &[Extra::LiveIndex],
        isolation: Isolation::Sandbox,
        repro: Repro::DoubleRun,
        cache: Cache::Cacheable,
        tiers: &[G4, G5, G6],
        blocks: &[],
    },
    CheckDef {
        id: "authority_role_limits",
        surface: Surface::Family,
        duty: "tool permissions name kernel roles; no worker handed the orchestrator role; no task scoped into the kernel",
        deps: &["@kernel", "tools_plugins", "continuity_records", "spec_tasks"],
        extras: &[],
        isolation: Isolation::InProcess,
        repro: Repro::DoubleRun,
        cache: Cache::Cacheable,
        tiers: &[G3, G4, G5, G6],
        blocks: &[CRIT_ALL],
    },
    CheckDef {
        id: "mutation_scope",
        surface: Surface::Family,
        duty: "kernel payload unmodified (INV-007); returned handoffs carry no authority violations",
        deps: &["@kernel", "continuity_records"],
        extras: &[],
        isolation: Isolation::InProcess,
        repro: Repro::DoubleRun,
        cache: Cache::Cacheable,
        tiers: &[G2, G4, G5, G6],
        blocks: &[CRIT_ALL],
    },
    CheckDef {
        id: "path_map_compliance",
        surface: Surface::Family,
        duty: "every governed file matches a repository-contract rule; no secret content outside secret-class paths; no hidden Qualification Oracle material in any file",
        deps: &["@files"],
        extras: &[],
        isolation: Isolation::InProcess,
        repro: Repro::DoubleRun,
        cache: Cache::Cacheable,
        tiers: &[G1, G4, G5, G6],
        blocks: &[CRIT_ALL],
    },
    CheckDef {
        id: "context_reproducibility",
        surface: Surface::Family,
        duty: "deterministic authority block of a compiled context packet is reproducible and carries the policy fields; every dispatchable task's delivered inputs verify against its declared manifest (W4)",
        deps: &["@records", "@overlay", "index_manifest"],
        extras: &[Extra::LiveIndex],
        isolation: Isolation::Sandbox,
        repro: Repro::SelfChecked,
        cache: Cache::Cacheable,
        tiers: &[G4, G5, G6],
        blocks: &[],
    },
    CheckDef {
        id: "concurrency_claims",
        surface: Surface::Family,
        duty: "session claims reference known tasks; expired claims swept",
        deps: &["spec_tasks"],
        extras: &[Extra::Claims],
        isolation: Isolation::InProcess,
        repro: Repro::SelfChecked,
        cache: Cache::Never,
        tiers: &[G3, G4, G5, G6],
        blocks: &[],
    },
    CheckDef {
        id: "adapter_portability",
        surface: Surface::Family,
        duty: "generated provider adapters are current and carry the kernel invariants",
        deps: &["@kernel", "@overlay", "generated_other"],
        extras: &[],
        isolation: Isolation::InProcess,
        repro: Repro::DoubleRun,
        cache: Cache::Cacheable,
        tiers: &[G4, G5, G6],
        blocks: &[],
    },
    CheckDef {
        id: "skill_regression",
        surface: Surface::Family,
        duty: "skill schema; version identifies content (bindings and observations); validation scenarios executed in sandboxes",
        deps: &["@kernel", "@overlay"],
        extras: &[Extra::SkillObservations],
        isolation: Isolation::OwnSandboxes,
        repro: Repro::SelfChecked,
        cache: Cache::Cacheable,
        tiers: &[G5, G6],
        blocks: &[],
    },
    CheckDef {
        id: "command_contract_consistency",
        surface: Surface::Family,
        duty: "every command-contract operation maps to an implemented CLI command",
        deps: &["@kernel"],
        extras: &[],
        isolation: Isolation::InProcess,
        repro: Repro::DoubleRun,
        cache: Cache::Cacheable,
        tiers: &[G5, G6],
        blocks: &[],
    },
    CheckDef {
        id: "secrets_sensitivity_indexing",
        surface: Surface::Family,
        duty: "no secret-class artefact, secret pattern, never-index class or derived vector in the index",
        deps: &["@files"],
        extras: &[Extra::LiveIndex],
        isolation: Isolation::InProcess,
        repro: Repro::DoubleRun,
        cache: Cache::Cacheable,
        tiers: &[G1, G4, G5, G6],
        blocks: &[CRIT_ALL],
    },
    CheckDef {
        id: "recovery_rebuild",
        surface: Surface::Family,
        duty: "tracked manifest matches the live index; deep: two full rebuilds in a sandbox reproduce the manifest hash",
        deps: &["@files"],
        extras: &[Extra::LiveIndex, Extra::DeepMode],
        isolation: Isolation::Sandbox,
        repro: Repro::SelfChecked,
        cache: Cache::Cacheable,
        tiers: &[G4, G5, G6],
        blocks: &[],
    },
    CheckDef {
        id: "fresh_agent_reconstruction",
        surface: Surface::Family,
        duty: "a fresh agent reconstructs state within the read budget",
        deps: &["@files"],
        extras: &[Extra::Claims],
        isolation: Isolation::InProcess,
        repro: Repro::SelfChecked,
        cache: Cache::Never,
        tiers: &[G4, G5, G6],
        blocks: &[],
    },
    CheckDef {
        id: "product_traceability",
        surface: Surface::Family,
        duty: "test obligations within policy families and independence; DONE tasks closed by a report; features have scenarios/tests; DONE implementation traces to its requirements (W5/W8)",
        deps: &["@records", "@overlay"],
        extras: &[],
        isolation: Isolation::InProcess,
        repro: Repro::DoubleRun,
        cache: Cache::Cacheable,
        tiers: &[G2, G4, G5, G6],
        blocks: &[],
    },
    CheckDef {
        id: "audit_reproducibility",
        surface: Surface::Family,
        duty: "every check executed in this run reproduced its result (double run, or cached result under an identical key)",
        deps: &[],
        extras: &[],
        isolation: Isolation::InProcess,
        repro: Repro::SelfChecked,
        cache: Cache::Never,
        tiers: &[G4, G5, G6],
        blocks: &[],
    },
    CheckDef {
        id: "policy_enforcement_coverage",
        surface: Surface::Family,
        duty: "every kernel policy key is enforced or classified informational",
        deps: &["@kernel"],
        extras: &[],
        isolation: Isolation::InProcess,
        repro: Repro::DoubleRun,
        cache: Cache::Cacheable,
        tiers: &[G5, G6],
        blocks: &[],
    },
    CheckDef {
        id: "policy_precedence",
        surface: Surface::Family,
        duty: "no refused (weakening) override; precedence rules available; policy read from a verified kernel",
        deps: &["@kernel", "@overlay"],
        extras: &[],
        isolation: Isolation::InProcess,
        repro: Repro::DoubleRun,
        cache: Cache::Cacheable,
        tiers: &[G4, G5, G6],
        blocks: &[CRIT_ALL],
    },
    CheckDef {
        id: "plugin_governance",
        surface: Surface::Family,
        duty: "plugin descriptors valid, registered, pinned and authorised (records first governed use on this machine)",
        deps: &["@files"],
        extras: &[Extra::PluginObservations],
        isolation: Isolation::InProcess,
        repro: Repro::SelfChecked,
        cache: Cache::Cacheable,
        tiers: &[G4, G5, G6],
        blocks: &[],
    },
    CheckDef {
        id: "product_test_health",
        surface: Surface::Family,
        duty: "per-family product-test evidence: recorded, current for its inputs, passing (O1, U product-test health)",
        deps: &["source", "@overlay"],
        extras: &[Extra::ProductEvidence],
        isolation: Isolation::InProcess,
        repro: Repro::DoubleRun,
        cache: Cache::Cacheable,
        tiers: &[G2, G4, G5, G6],
        blocks: &[BlockRule {
            min_severity: "high",
            operations: &[ops::TASK_CLOSE],
            scope: BlockScope::CoveredPaths,
        }, BlockRule {
            min_severity: "high",
            operations: &[ops::RELEASE_BUILD, ops::UPDATE_APPLY],
            scope: BlockScope::Global,
        }],
    },
    CheckDef {
        id: "human_gate_integrity",
        surface: Surface::Family,
        duty: "answers are offered options of presented gates; no work completed past an unanswered blocking gate",
        deps: &["spec_decisions", "spec_tasks"],
        extras: &[],
        isolation: Isolation::InProcess,
        repro: Repro::DoubleRun,
        cache: Cache::Cacheable,
        tiers: &[G3, G4, G5, G6],
        blocks: &[BlockRule {
            min_severity: "high",
            operations: &[ops::TASK_CLOSE, ops::RELEASE_BUILD],
            scope: BlockScope::Global,
        }],
    },
    CheckDef {
        id: "change_control_integrity",
        surface: Surface::Family,
        duty: "no interrupted CIT; committed CITs carry an approval and, where required, an answered gate",
        deps: &["@records"],
        extras: &[],
        isolation: Isolation::InProcess,
        repro: Repro::DoubleRun,
        cache: Cache::Cacheable,
        tiers: &[G3, G4, G5, G6],
        blocks: &[BlockRule {
            min_severity: "high",
            operations: &[ops::CIT_PROPOSE, ops::CIT_EXECUTE, ops::TASK_CLOSE, ops::RELEASE_BUILD],
            scope: BlockScope::Global,
        }],
    },
    CheckDef {
        id: "continuity_checkpoint_handoff",
        surface: Surface::Family,
        duty: "handoffs and checkpoints reference known tasks; the latest-checkpoint pointer resolves",
        deps: &["continuity_records", "spec_tasks"],
        extras: &[],
        isolation: Isolation::InProcess,
        repro: Repro::DoubleRun,
        cache: Cache::Cacheable,
        tiers: &[G3, G4, G5, G6],
        blocks: &[],
    },
    CheckDef {
        id: "model_routing_integrity",
        surface: Surface::Family,
        duty: "every task class in use resolves to a routing tier; routing evidence names known task classes",
        deps: &["@kernel", "model_profile", "spec_tasks"],
        extras: &[],
        isolation: Isolation::InProcess,
        repro: Repro::DoubleRun,
        cache: Cache::Cacheable,
        tiers: &[G4, G5, G6],
        blocks: &[],
    },
    // ---------------------------------------- round-2 families: the reporting side of other workstreams' checks
    CheckDef {
        id: "lineage_orphans",
        surface: Surface::Family,
        duty: "W7: every orphan by name — unconsumed outputs, specs without implementation/test path, research never consumed by a decision, acceptance tests without requirement/scenario, code without active spec justification; generates linked investigation work",
        deps: &["@records", "@files"],
        extras: &[Extra::LiveIndex, Extra::GovernanceBaseline],
        isolation: Isolation::InProcess,
        repro: Repro::DoubleRun,
        cache: Cache::Cacheable,
        tiers: &[G4, G5, G6],
        blocks: &[],
    },
    CheckDef {
        id: "os_binding_integrity",
        surface: Surface::Family,
        duty: "T2: gate/decision records and health evidence that no gov operation on this machine produced as they stand are reported and not honoured; tampering with sealed OS state is high",
        deps: &["spec_decisions", "spec_tasks", currency::T2_BINDINGS],
        extras: &[],
        isolation: Isolation::InProcess,
        repro: Repro::SelfChecked,
        cache: Cache::Never,
        tiers: &[G1, G2, G3, G4, G5, G6],
        blocks: &[BlockRule {
            min_severity: "high",
            operations: &[ops::RELEASE_BUILD],
            scope: BlockScope::Global,
        }],
    },
    CheckDef {
        id: "installation_authenticity",
        surface: Surface::Family,
        duty: "BC-P2-36: an installation whose release authenticity is not established is disclosed (low on an unprovisioned bootstrap machine, medium on a provisioned one)",
        deps: &["@kernel", currency::MACHINE_TRUST],
        extras: &[],
        isolation: Isolation::InProcess,
        repro: Repro::SelfChecked,
        cache: Cache::Never,
        tiers: &[G1, G4, G5, G6],
        blocks: &[],
    },
    CheckDef {
        id: "contract_binding",
        surface: Surface::Family,
        duty: "BC-P2-01: the compiled contract views, evidence map and generated view are semantically identical to the owner source (`gov contract verify`), where the contract chain is present",
        deps: &[],
        extras: &[Extra::ContractSource],
        isolation: Isolation::InProcess,
        repro: Repro::SelfChecked,
        cache: Cache::Cacheable,
        tiers: &[G5, G6],
        blocks: &[BlockRule {
            min_severity: "high",
            operations: &[ops::RELEASE_BUILD],
            scope: BlockScope::Global,
        }],
    },
    CheckDef {
        id: "index_content_coverage",
        surface: Surface::Family,
        duty: "BC-P2-25: every governed record's content and every non-empty line of indexed code is held by at least one chunk of the live index",
        deps: &["@files"],
        extras: &[Extra::LiveIndex],
        isolation: Isolation::InProcess,
        repro: Repro::DoubleRun,
        cache: Cache::Cacheable,
        tiers: &[G1, G4, G5, G6],
        blocks: &[],
    },
    CheckDef {
        id: "task_contract_integrity",
        surface: Surface::Family,
        duty: "task contracts hold in the tree: output of a task whose contract forbids production merge (every experiment) is not in the production tree",
        deps: &["@files"],
        extras: &[Extra::Claims],
        isolation: Isolation::InProcess,
        repro: Repro::SelfChecked,
        cache: Cache::Never,
        tiers: &[G2, G4, G5, G6],
        blocks: &[BlockRule {
            min_severity: "high",
            operations: &[ops::RELEASE_BUILD],
            scope: BlockScope::Global,
        }],
    },
    // ------------------------------------------------------------------------------------------ doctor checks
    doctor("D001", "framework.lock present", &["framework_lock"], &[CRIT_ALL]),
    doctor("D002", "framework.lock schema", &["framework_lock"], &[HIGH_RELY]),
    doctor("D003", "kernel payload integrity", &["@kernel"], &[CRIT_ALL]),
    doctor("D004", "lock matches kernel manifest", &["@kernel"], &[CRIT_ALL]),
    doctor("D005", "CLI/kernel compatibility", &["@kernel"], &[CRIT_ALL]),
    doctor("D006", "project overlay", &["@overlay"], &[HIGH_RELY]),
    doctor("D007", "policies", &["@overlay"], &[HIGH_RELY]),
    doctor("D008", "framework.json in sync", &["path_map"], &[]),
    doctor("D009", "derived runtime", &["index_manifest"], &[]),
    doctor("D010", "index freshness", &["@files"], &[]),
    doctor("D011", "secrets outside secret class", &["@files"], &[CRIT_ALL]),
    doctor("D012", "no secrets in index", &["@files"], &[CRIT_ALL]),
    doctor("D013", "legacy governance mechanisms retired", &["@files"], &[]),
    doctor("D014", "authority unambiguous", &["@records"], &[HIGH_RELY]),
    doctor("D015", "graph integrity", &["@records"], &[]),
    doctor("D016", "no interrupted transactions", &["spec_decisions"], &[BlockRule {
        min_severity: "high",
        operations: &[ops::CIT_PROPOSE, ops::CIT_EXECUTE, ops::TASK_CLOSE],
        scope: BlockScope::Global,
    }]),
    doctor("D017", "session claims", &["spec_tasks"], &[]),
    doctor("D018", "control state", &["@overlay"], &[]),
    doctor("D019", "human gates presented", &["spec_decisions"], &[]),
    doctor("D020", "adapters current and conformant", &["generated_other", "@overlay"], &[]),
    doctor("D021", "governance suite green and current", &["@files"], &[]),
    doctor("D022", "native toolchains", &["source"], &[]),
    doctor("D023", "records parse", &["@records"], &[HIGH_RELY]),
    doctor("D024", ".governance-runtime ignored by git", &["source"], &[]),
    doctor("D025", "semantic index consistent with pins", &["index_manifest"], &[]),
    doctor("D026", "claims store present and intact", &[], &[]),
    doctor("D027", "policy precedence respected", &["@overlay"], &[CRIT_ALL]),
    doctor("D028", "capability plugins governed", &["tools_plugins"], &[]),
    doctor("D029", "constitutional policy read from a verified kernel", &["@kernel"], &[CRIT_ALL]),
    doctor("D030", "product tests pass (recorded evidence)", &["source", "@overlay"], &[BlockRule {
        min_severity: "high",
        operations: &[ops::TASK_CLOSE],
        scope: BlockScope::CoveredPaths,
    }, BlockRule {
        min_severity: "high",
        operations: &[ops::RELEASE_BUILD, ops::UPDATE_APPLY],
        scope: BlockScope::Global,
    }]),
    doctor("D031", "no active health hard-block", &[], &[]),
    doctor(
        "D032",
        "installation authenticity established (else disclosed)",
        &["@kernel", currency::MACHINE_TRUST],
        &[],
    ),
    doctor(
        "D033",
        "OS-written records bound to gov operations (T2)",
        &["spec_decisions", currency::T2_BINDINGS],
        &[],
    ),
    doctor("D034", "failure memory followed up", &["evidence_records"], &[]),
];

const fn doctor(
    id: &'static str,
    duty: &'static str,
    deps: &'static [&'static str],
    blocks: &'static [BlockRule],
) -> CheckDef {
    CheckDef {
        id,
        surface: Surface::Doctor,
        duty,
        deps,
        extras: &[],
        isolation: Isolation::InProcess,
        repro: Repro::SelfChecked,
        cache: Cache::Never,
        tiers: &[G1, G5],
        blocks,
    }
}

pub fn get(id: &str) -> Option<&'static CheckDef> {
    CHECKS.iter().find(|c| c.id == id)
}

/// Governance-suite families declared in the catalogue.
pub fn families() -> impl Iterator<Item = &'static CheckDef> {
    CHECKS.iter().filter(|c| c.surface == Surface::Family)
}

fn severity_rank(s: &str) -> u8 {
    match s {
        "critical" => 4,
        "high" => 3,
        "medium" => 2,
        "low" => 1,
        _ => 0,
    }
}

/// Does a finding of `severity` trigger `rule`?
pub fn triggers(rule: &BlockRule, severity: &str) -> bool {
    severity_rank(severity) >= severity_rank(rule.min_severity)
}

pub fn rank(s: &str) -> u8 {
    severity_rank(s)
}

/// The declared enforcement of a check, as carried beside every result (`mode`: `hard-block` or `warning`).
pub fn enforcement(def: &CheckDef) -> Value {
    if def.blocks.is_empty() {
        return json!({"mode": "warning", "refuses": []});
    }
    json!({
        "mode": "hard-block",
        "refuses": def.blocks.iter().map(|b| json!({"at_or_above": b.min_severity, "operations": b.operations, "scope": match b.scope { BlockScope::Global => "global", BlockScope::CoveredPaths => "covered-paths" }})).collect::<Vec<_>>(),
        "below_threshold": "warning",
    })
}

pub fn describe(def: &CheckDef) -> Value {
    json!({
        "id": def.id,
        "surface": match def.surface { Surface::Family => "governance-family", Surface::Doctor => "doctor" },
        "duty": def.duty,
        "depends_on": expand_deps(def),
        "extras": def.extras.iter().map(|e| format!("{e:?}")).collect::<Vec<_>>(),
        "isolation": format!("{:?}", def.isolation),
        "reproducibility": format!("{:?}", def.repro),
        "cache": format!("{:?}", def.cache),
        "tiers": def.tiers.iter().map(|t| t.as_str()).collect::<Vec<_>>(),
        "enforcement": enforcement(def),
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn every_policy_family_is_declared_and_every_dependency_is_a_known_class() {
        let known = currency::all_class_ids();
        for c in CHECKS {
            for d in expand_deps(c) {
                assert!(known.contains(&d), "{}: unknown class {d}", c.id);
            }
            for b in c.blocks {
                for op in b.operations {
                    assert!(ops::ALL.contains(op), "{}: unknown operation {op}", c.id);
                }
            }
        }
        let pol: serde_yaml::Value =
            serde_yaml::from_str(include_str!("../../../framework/policies/TEST_POLICY.yaml"))
                .unwrap();
        for f in pol["governance_families"].as_sequence().unwrap() {
            let id = f.as_str().unwrap();
            assert!(
                get(id)
                    .map(|c| c.surface == Surface::Family)
                    .unwrap_or(false),
                "TEST_POLICY family {id} has no catalogue declaration"
            );
        }
    }

    #[test]
    fn checks_that_write_derived_state_are_isolated() {
        for id in [
            "memory_retrieval_regression",
            "context_reproducibility",
            "recovery_rebuild",
        ] {
            assert_eq!(get(id).unwrap().isolation, Isolation::Sandbox, "{id}");
        }
        assert_eq!(
            get("skill_regression").unwrap().isolation,
            Isolation::OwnSandboxes
        );
    }

    #[test]
    fn hard_blocks_are_explicit() {
        let d011 = get("D011").unwrap();
        assert_eq!(enforcement(d011)["mode"], "hard-block");
        assert!(triggers(&d011.blocks[0], "critical"));
        assert!(!triggers(&d011.blocks[0], "high"));
        assert_eq!(
            enforcement(get("index_freshness").unwrap())["mode"],
            "warning"
        );
    }
}
