//! `gov` — the Governance OS command-line control surface (API-0002 machine contract).
use clap::{Args, Parser, Subcommand};
use gov_runtime::memory::db::RuntimeDb;
use gov_runtime::{GovError, Project, Result};
use serde_json::{json, Value};
use std::path::{Path, PathBuf};

#[derive(Parser)]
#[command(name = "gov", version = gov_runtime::CLI_VERSION, about = "Governance OS control surface (agentic-engineering-os)")]
struct Cli {
    /// Repository root (default: discovered from the current directory)
    #[arg(long, global = true)]
    root: Option<PathBuf>,
    /// Structured JSON output envelope
    #[arg(long, global = true)]
    json: bool,
    /// Session id (default: $GOV_SESSION or a new id)
    #[arg(long, global = true)]
    session: Option<String>,
    /// Acting role, as assigned to this caller (else $GOV_ROLE). With neither, the invocation carries no privileged
    /// authority (L0). The `human` role is never conferred by a declaration: human answers are owner-signed.
    #[arg(long, global = true)]
    role: Option<String>,
    #[command(subcommand)]
    cmd: Cmd,
}

#[derive(Subcommand)]
enum Cmd {
    /// Print versions
    Version,
    /// Greenfield onboarding: install kernel, overlay, roots, adapters, runtime, conformance suite
    Init {
        #[arg(long)]
        source: Option<String>,
        #[arg(long)]
        name: Option<String>,
        #[arg(long)]
        alias: Option<String>,
        #[arg(long)]
        intent: Option<String>,
        #[arg(long)]
        force: bool,
        #[arg(long)]
        skip_index: bool,
        /// Requested release channel (matched against the signed `channel` field; it cannot create authority)
        #[arg(long)]
        channel: Option<String>,
        /// Request below-floor admission; the authority is an owner-signed token in protected machine state
        #[arg(long)]
        break_glass: bool,
    },
    /// Reconstruct current governed project state (no prior conversation needed)
    Status,
    /// Determine the correct next work and bounded authority
    Continue {
        #[arg(long)]
        claim: bool,
    },
    /// Answer a Human Decision Gate: apply an owner-signed human answer, or (--by <acting agent role>) resolve within
    /// HUMAN_GATE_POLICY.agent_resolvable_when
    Decide {
        gate: String,
        /// The option (must be one the gate offers; for a human answer it must equal the option the owner signed)
        #[arg(long)]
        option: Option<String>,
        /// Agent resolution: the acting agent role resolving as itself. Any other value is a request label, never
        /// an identity; a human answer's identity is the owner's signature.
        #[arg(long)]
        by: Option<String>,
        #[arg(long)]
        rationale: Option<String>,
        /// Owner-signed `human-gate-answer` document (default: the human-channel inbox)
        #[arg(long)]
        answer_file: Option<PathBuf>,
        /// Governed record ids the resolution relied on (repeatable)
        #[arg(long = "evidence")]
        evidence: Vec<String>,
    },
    /// Run the governance verification suite and record an audit
    Audit {
        #[arg(long)]
        deep: bool,
        #[arg(long)]
        family: Vec<String>,
        #[arg(long)]
        no_persist: bool,
    },
    /// Emergency: pause execution
    Pause {
        #[arg(long)]
        reason: Option<String>,
    },
    /// Emergency: freeze all writes
    FreezeWrites {
        #[arg(long)]
        reason: Option<String>,
    },
    /// Emergency: cancel agents (pause + cancel)
    CancelAgents {
        #[arg(long)]
        reason: Option<String>,
    },
    /// Lift pause/freeze
    Resume,
    /// Health checks with remediation
    Doctor,
    /// Rebuild derived memory from Git + authoritative records
    RebuildMemory {
        #[arg(long)]
        incremental: bool,
    },
    /// Interrupted-session recovery
    Recover {
        #[arg(long)]
        dry_run: bool,
    },
    /// Brownfield adoption stages A0-A11
    Adopt {
        #[command(subcommand)]
        stage: AdoptCmd,
    },
    /// Path-migration tooling (aliases of adopt stages)
    Migrate {
        #[command(subcommand)]
        stage: AdoptCmd,
    },
    /// Framework update: --check, --apply, --rollback
    Update {
        #[arg(long)]
        check: bool,
        #[arg(long)]
        apply: bool,
        #[arg(long)]
        rollback: bool,
        /// Requested release channel (matched against the signed `channel` field; it cannot create authority)
        #[arg(long)]
        channel: Option<String>,
        /// Request below-floor admission; the authority is an owner-signed token in protected machine state
        #[arg(long)]
        break_glass: bool,
        #[arg(long)]
        source: Option<String>,
        #[arg(long)]
        approve: bool,
        /// Recorded as who requested the apply (default: the acting role); approval itself comes only from the
        /// answered Human Decision Gate
        #[arg(long)]
        by: Option<String>,
        #[arg(long)]
        reason: Option<String>,
    },
    /// Upstream learning: prepare/submit sanitised framework lesson packets
    Upstream {
        #[command(subcommand)]
        op: UpstreamCmd,
    },
    /// Task operations
    Task {
        #[command(subcommand)]
        op: TaskCmd,
    },
    /// Change-Impact Transactions
    Cit {
        #[command(subcommand)]
        op: CitCmd,
    },
    /// Context packets
    Context {
        #[command(subcommand)]
        op: ContextCmd,
    },
    /// Checkpoints
    Checkpoint {
        #[command(subcommand)]
        op: CheckpointCmd,
    },
    /// Skills registry
    Skills {
        #[command(subcommand)]
        op: SkillsCmd,
    },
    /// Tool / MCP capability registry
    Tools {
        #[command(subcommand)]
        op: ToolsCmd,
    },
    /// Typed A2A handoffs
    Handoff {
        #[command(subcommand)]
        op: HandoffCmd,
    },
    /// Memory: query / verify / freshness
    Memory {
        #[command(subcommand)]
        op: MemoryCmd,
    },
    /// Human Decision Gates
    Gate {
        #[command(subcommand)]
        op: GateCmd,
    },
    /// Feature readiness
    Readiness {
        #[command(subcommand)]
        op: ReadinessCmd,
    },
    /// Natural-language intent routing
    Intent { text: String },
    /// Model routing
    Route {
        #[arg(long)]
        task: Option<String>,
        #[arg(long)]
        class: Option<String>,
        #[arg(long)]
        radius: Option<String>,
        #[arg(long)]
        record: Option<String>,
        #[arg(long)]
        report: bool,
    },
    /// Telemetry
    Telemetry {
        #[command(subcommand)]
        op: TelemetryCmd,
    },
    /// Provider adapters
    Adapters {
        #[command(subcommand)]
        op: AdaptersCmd,
    },
    /// Release build/verify (canonical repository)
    Release {
        #[command(subcommand)]
        op: ReleaseCmd,
    },
    /// Kernel verify/reinstall
    Kernel {
        #[command(subcommand)]
        op: KernelCmd,
    },
    /// Signed Release Root: machine trust anchor, protected floors, break-glass recovery (ARCH-0003)
    Trust {
        #[command(subcommand)]
        op: TrustCmd,
    },
    /// Capability Acceptance Contract v3: verify the hash-bound source chain, or recompile it
    Contract {
        #[command(subcommand)]
        op: ContractCmd,
    },
    /// Capability ecosystem: ecosystems, plugins, invoke
    Capabilities {
        #[command(subcommand)]
        op: CapCmd,
    },
    /// Session claims
    Claims {
        #[command(subcommand)]
        op: ClaimsCmd,
    },
    /// Verify governance (audit) or product suite
    Verify {
        #[arg(default_value = "governance")]
        what: String,
    },
    /// MCP server (planned)
    Mcp {
        #[arg(default_value = "serve")]
        op: String,
    },
    /// Framework lesson intake (canonical repository): cluster inbox packets into Framework Change Proposals
    Lessons {
        #[command(subcommand)]
        op: LessonsCmd,
    },
    /// Governed capability plugins: register / list / health
    Plugins {
        #[command(subcommand)]
        op: PluginsCmd,
    },
    /// Effective policy and precedence diagnostics
    Policy {
        #[command(subcommand)]
        op: PolicyCmd,
    },
    /// Artefact identity and lineage (Gate W W1/W8)
    Artefact {
        #[command(subcommand)]
        op: ArtefactCmd,
    },
    // ---- WS-2 (P2-AR-0015) additive block: Governance Health Scheduler (Gate O5), product tests, skill regression
    /// Governance Health Scheduler: tiered runs, health state, checks, history, G0 guard, currency, product tests, skills
    Health {
        #[command(subcommand)]
        op: HealthCmd,
    },
    /// Qualification Oracle format (Contract v3 Gate V, V1-V4): print the format, or validate an oracle / score report
    Oracle {
        #[command(subcommand)]
        op: OracleCmd,
    },
    // ---- WS-4 (P2-AR-0025, BC-P2-05) additive block: session boundary
    /// Session boundary: checkpoint before the session closes, degraded when its work's inputs are stale or missing
    Session {
        #[command(subcommand)]
        op: SessionCmd,
    },
    // ---- WS-10 (P2-AR-0031) additive block: research, experiment and test-data lifecycles (Gate J, Gate H4)
    /// Research outputs as governed evidence (Contract v3 J1): record, update, conclude, withdraw, show, check, sync
    Research {
        #[command(subcommand)]
        op: ResearchCmd,
    },
    /// Experiment lifecycle (Contract v3 J2): design, run, reproduce, conclude, promote, abandon, show, check
    Experiment {
        #[command(subcommand)]
        op: ExperimentCmd,
    },
    /// Data requirements and test datasets with provenance and recorded authorship (Contract v3 H4)
    Data {
        #[command(subcommand)]
        op: DataCmd,
    },
    /// The FEATURE → SCENARIOS → DATA → TEST DATA → SUCCESS/FAILURE → INDEPENDENT TESTS chain (Contract v3 H4)
    Scenario {
        #[command(subcommand)]
        op: ScenarioCmd,
    },
}
// ---- WS-4 (P2-AR-0025, BC-P2-05) additive block
#[derive(Subcommand)]
enum SessionCmd {
    /// Close the session: checkpoint every unobserved trigger, then write the before_session_close checkpoint and
    /// state the input freshness it closed under (never refused; explicitly degraded when inputs are stale/missing)
    Close {
        #[arg(long, default_value = "gov continue")]
        next_action: String,
        #[arg(long)]
        task: Option<String>,
    },
}
// ---- WS-10 (P2-AR-0031) additive block: lifecycle subcommands (runtime/src/lifecycle)
#[derive(Subcommand)]
enum ResearchCmd {
    /// Record a research output: complete → CONCLUDED (EVIDENCE); with --draft → FRAMED/IN_PROGRESS, held reference-only
    Record {
        /// The research fields (JSON/YAML, or @file): question, reason, method, sources|data, measurements, uncertainty, conclusion, confidence
        #[arg(long)]
        fields: String,
        #[arg(long)]
        draft: bool,
        /// The task the research was done for (recorded as influenced)
        #[arg(long)]
        task: Option<String>,
    },
    /// Update unfinished (FRAMED/IN_PROGRESS) research; it stays reference-only
    Update {
        id: String,
        #[arg(long)]
        fields: String,
    },
    /// FRAMED/IN_PROGRESS → CONCLUDED: every J1 field recorded; the research becomes EVIDENCE
    Conclude {
        id: String,
        #[arg(long)]
        fields: Option<String>,
    },
    /// FRAMED/IN_PROGRESS → WITHDRAWN
    Withdraw {
        id: String,
        #[arg(long)]
        reason: String,
    },
    /// A research record, its evidence standing, recorded and derived influences, T2 binding and identity
    Show { id: String },
    /// Standing of every research record and the research findings
    Check,
    /// Record every missing influence backlink on research and experiment records
    Sync,
}
#[derive(Subcommand)]
enum ExperimentCmd {
    /// Record an experiment in DESIGNED (hypothesis|question, method, data|data_provenance|inputs; outputs outside production)
    Design {
        #[arg(long)]
        fields: String,
    },
    /// Amend an experiment (its design only while DESIGNED)
    Update {
        id: String,
        #[arg(long)]
        fields: String,
    },
    /// DESIGNED → RUNNING: record the primary run's results; every input is bound by SHA-256
    Run {
        id: String,
        #[arg(long)]
        results: String,
        #[arg(long)]
        environment: Option<String>,
        #[arg(long)]
        task: Option<String>,
    },
    /// Record a reproduction run; the OS judges agreement and recomputes reproducibility
    Reproduce {
        id: String,
        #[arg(long)]
        results: String,
        #[arg(long)]
        environment: Option<String>,
    },
    /// RUNNING → CONCLUDED: interpretation, decision_influence, confidence, reproducibility procedure/environment
    Conclude {
        id: String,
        #[arg(long)]
        fields: String,
    },
    /// CONCLUDED → PROMOTED: without --gate raise the promotion gate; with --gate apply the owner-signed approval
    Promote {
        id: String,
        /// Comma-separated production paths the promotion approves
        #[arg(long)]
        paths: String,
        #[arg(long)]
        gate: Option<String>,
        #[arg(long)]
        cit: Option<String>,
    },
    /// Any non-final state → ABANDONED
    Abandon {
        id: String,
        #[arg(long)]
        reason: String,
    },
    /// An experiment, its standing, runs, reproducibility, input drift, influences and T2 binding
    Show { id: String },
    /// Standing of every experiment and the experiment findings (incl. production-merge detection)
    Check,
}
#[derive(Subcommand)]
enum DataCmd {
    /// Register a data requirement or a test dataset (provenance, content binding, OS-recorded authorship)
    Register {
        #[arg(long)]
        fields: String,
    },
    /// A data record: kind, provenance, authorship, what it realises, which tests use it, its gaps
    Show { id: String },
}
#[derive(Subcommand)]
enum ScenarioCmd {
    /// Trace a feature's or scenario's chain with every gap
    Trace { id: String },
    /// Every chain gap in the project
    Check,
}
fn lifecycle_arg(s: &Option<String>) -> Result<Value> {
    match s {
        None => Ok(Value::Null),
        Some(_) => parse_json_arg(s),
    }
}
fn lifecycle_cmd(cli: &Cli) -> Result<Value> {
    use gov_runtime::lifecycle::{experiment as ex, research as rs, scenario as sc};
    let p = open_project(cli, true)?;
    match &cli.cmd {
        Cmd::Research { op } => match op {
            ResearchCmd::Record {
                fields,
                draft,
                task,
            } => rs::record(
                &p,
                parse_json_arg(&Some(fields.clone()))?,
                *draft,
                task.as_deref(),
            ),
            ResearchCmd::Update { id, fields } => {
                rs::update(&p, id, parse_json_arg(&Some(fields.clone()))?)
            }
            ResearchCmd::Conclude { id, fields } => rs::conclude(&p, id, lifecycle_arg(fields)?),
            ResearchCmd::Withdraw { id, reason } => rs::withdraw(&p, id, reason),
            ResearchCmd::Show { id } => rs::show(&p, id),
            ResearchCmd::Check => rs::check(&p),
            ResearchCmd::Sync => gov_runtime::lifecycle::sync_influences(&p),
        },
        Cmd::Experiment { op } => match op {
            ExperimentCmd::Design { fields } => {
                ex::design(&p, parse_json_arg(&Some(fields.clone()))?)
            }
            ExperimentCmd::Update { id, fields } => {
                ex::update(&p, id, parse_json_arg(&Some(fields.clone()))?)
            }
            ExperimentCmd::Run {
                id,
                results,
                environment,
                task,
            } => ex::run(
                &p,
                id,
                parse_json_arg(&Some(results.clone()))?,
                lifecycle_arg(environment)?,
                task.as_deref(),
            ),
            ExperimentCmd::Reproduce {
                id,
                results,
                environment,
            } => ex::reproduce(
                &p,
                id,
                parse_json_arg(&Some(results.clone()))?,
                lifecycle_arg(environment)?,
            ),
            ExperimentCmd::Conclude { id, fields } => {
                ex::conclude(&p, id, parse_json_arg(&Some(fields.clone()))?)
            }
            ExperimentCmd::Promote {
                id,
                paths,
                gate,
                cit,
            } => ex::promote(
                &p,
                id,
                &csv(&Some(paths.clone())),
                gate.as_deref(),
                cit.as_deref(),
            ),
            ExperimentCmd::Abandon { id, reason } => ex::abandon(&p, id, reason),
            ExperimentCmd::Show { id } => ex::show(&p, id),
            ExperimentCmd::Check => ex::check(&p),
        },
        Cmd::Data { op } => match op {
            DataCmd::Register { fields } => {
                sc::register(&p, parse_json_arg(&Some(fields.clone()))?)
            }
            DataCmd::Show { id } => sc::show(&p, id),
        },
        Cmd::Scenario { op } => match op {
            ScenarioCmd::Trace { id } => sc::trace_cmd(&p, id),
            ScenarioCmd::Check => sc::check(&p),
        },
        _ => Err(GovError::new("USAGE", "not a lifecycle command")),
    }
}
// ---- end WS-10 additive block
/// `gov oracle` (P2-AR-0014, BC-P2-51). Read-only: it validates documents and changes no governed state.
#[derive(Subcommand)]
enum OracleCmd {
    /// Print the format definition, its digest and the crosswalk from every Contract v3 V1-V4 element to its field
    Format,
    /// Validate a qualification-oracle or qualification-score-report document (JSON or YAML); fails closed, typed
    Validate {
        /// The document to validate
        file: PathBuf,
        /// For a score report: the sealed oracle it was scored against (binding, fault coverage, arithmetic)
        #[arg(long)]
        oracle: Option<PathBuf>,
        /// Public qualification suite root: refuse an oracle stored inside it, or any trace of the oracle found in it
        #[arg(long = "public-suite")]
        public_suite: Vec<PathBuf>,
        /// Qualification repository root: refuse an oracle stored inside it, or any trace of the oracle found in it
        #[arg(long)]
        repository: Vec<PathBuf>,
    },
}
// ---- WS-2 (P2-AR-0015) additive block
#[derive(Subcommand)]
enum HealthCmd {
    /// Run the scheduler: checks whose declared inputs changed execute (concurrently; state-writing ones in sandboxes), the rest are served from the cache
    Run {
        /// Tier G1..G6 (default: every suite check, cache reused)
        #[arg(long)]
        tier: Option<String>,
        /// Run only these checks
        #[arg(long)]
        check: Vec<String>,
        /// Paths the triggering change touched (recorded as provenance)
        #[arg(long)]
        changed: Vec<String>,
        /// Triggering event label (recorded as provenance)
        #[arg(long)]
        event: Option<String>,
        /// Re-execute every selected check (reproducibility compared against the cache)
        #[arg(long)]
        no_cache: bool,
        #[arg(long)]
        deep: bool,
        /// Do not persist a governance-suite record even when the run re-establishes currency
        #[arg(long)]
        no_persist: bool,
    },
    /// RED/YELLOW/GREEN health state, active hard-blocks, failing and stale checks, suite currency, product tests
    Status,
    /// The check catalogue: tiers, declared inputs, isolation, cache, hard-block vs warning
    Checks,
    /// Recorded health results (newest first)
    History {
        #[arg(long, default_value_t = 20)]
        limit: usize,
    },
    /// One recorded health result with its provenance
    Show { id: String },
    /// G0: would this governed operation be refused by an active hard-block?
    Guard {
        operation: String,
        #[arg(long)]
        paths: Vec<String>,
    },
    /// The evidence currency key: per input class digests and what changed since the latest green record
    Currency,
    /// Run product test families and record per-family governed evidence
    Product {
        #[arg(long)]
        family: Vec<String>,
    },
    /// Skill regression: version/content binding and executed validation scenarios (--record binds passing versions)
    Skills {
        #[arg(long)]
        skill: Option<String>,
        #[arg(long)]
        record: bool,
        /// Also execute the executable form of deferred scenarios (reported only)
        #[arg(long)]
        include_deferred: bool,
    },
    /// The task-close health gate for a task and report, without closing it (G0 guard, G2 re-check, currency, product evidence)
    CloseCheck {
        task: String,
        #[arg(long)]
        report: String,
    },
    // WS-2 round 2 (P2-AR-0023) additive: the G6 entry point (ws01-12 IP-4)
    /// G6: record the health of a qualification run (synthetic repository, chaos, soak, hidden test) — only when its hidden oracle conforms and is separate, and its score report is bound to that oracle
    Qualify {
        /// synthetic-repository | chaos | soak | hidden-test
        #[arg(long, default_value = "synthetic-repository")]
        kind: String,
        /// The verifier-owned hidden oracle (qualification-oracle document)
        #[arg(long)]
        oracle: PathBuf,
        /// The candidate run's qualification-score-report, scored against that oracle
        #[arg(long)]
        report: PathBuf,
        /// Public qualification suite root the oracle must be kept out of
        #[arg(long = "public-suite")]
        public_suite: Vec<PathBuf>,
        /// Other qualification repository roots the oracle must be kept out of (this repository always is)
        #[arg(long)]
        repository: Vec<PathBuf>,
        #[arg(long)]
        run_id: Option<String>,
    },
}
fn health_cmd(cli: &Cli, op: &HealthCmd) -> Result<Value> {
    use gov_runtime::scheduler as sch;
    let p = open_project(cli, true)?;
    match op {
        HealthCmd::Run {
            tier,
            check,
            changed,
            event,
            no_cache,
            deep,
            no_persist,
        } => {
            let t = match tier {
                Some(t) => sch::Tier::parse(t)?,
                None => sch::Tier::G5,
            };
            let trig =
                sch::Trigger::new(event.as_deref().unwrap_or("gov health run")).with_paths(changed);
            let mut o = sch::RunOptions::new(t, trig);
            if tier.is_none() {
                o.selection = sch::Selection::All;
                o.cache = sch::CacheMode::Use;
            }
            if !check.is_empty() {
                o.selection = sch::Selection::Explicit(check.clone());
            }
            if *no_cache {
                o.cache = sch::CacheMode::Refresh;
            }
            o.deep = *deep;
            o.surface = "health-run".into();
            o.record = if *no_persist {
                sch::RecordPolicy::Never
            } else {
                sch::RecordPolicy::WhenCompleteAndStale
            };
            let r = gov_runtime::verification::audit_with(&p, &o)?;
            if r["verdict"] == "UNHEALTHY" {
                return Err(GovError::new(
                    "UNHEALTHY",
                    format!(
                        "health run UNHEALTHY: {} critical, {} high",
                        r["counts"]["critical"], r["counts"]["high"]
                    ),
                )
                .with_details(r));
            }
            Ok(r)
        }
        HealthCmd::Status => sch::status(&p),
        HealthCmd::Checks => Ok(sch::describe_catalogue()),
        HealthCmd::History { limit } => Ok(json!(sch::store::history(&p, *limit))),
        HealthCmd::Show { id } => sch::store::load_result(&p, id)
            .ok_or_else(|| GovError::new("NOT_FOUND", format!("no health result {id}"))),
        HealthCmd::Guard { operation, paths } => sch::guard(&p, operation, paths),
        HealthCmd::Currency => {
            let snap = gov_runtime::verification::currency::Snapshot::take(&p)?;
            let cur = gov_runtime::verification::currency::Currency::evaluate(&p, &snap);
            Ok(json!({"currency": cur.to_value(), "snapshot": snap.describe()}))
        }
        HealthCmd::Product { family } => gov_runtime::verification::product::run(&p, family),
        HealthCmd::CloseCheck { task, report } => {
            let s = gov_runtime::records::RecordStore::load(&p.root);
            let t = s
                .get(task)
                .map(|r| r.data.clone())
                .ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("{task} not found")))?;
            let rep = load_file_value(report)?;
            let mut touched: Vec<String> = rep["files_changed"]
                .as_array()
                .map(|a| {
                    a.iter()
                        .filter_map(|x| x.as_str().map(|s| s.to_string()))
                        .collect()
                })
                .unwrap_or_default();
            let (observed, _) = gov_runtime::orchestration::tasks::observed_mutations(&p, task);
            for f in observed {
                if !touched.contains(&f) {
                    touched.push(f);
                }
            }
            gov_runtime::verification::close_gate(&p, &t, &rep, &touched, false)
        }
        HealthCmd::Qualify {
            kind,
            oracle,
            report,
            public_suite,
            repository,
            run_id,
        } => sch::qualification_run(
            &p,
            &sch::QualificationRun {
                kind: kind.clone(),
                run_id: run_id.clone(),
                oracle: oracle.clone(),
                score_report: report.clone(),
                public_suites: public_suite.clone(),
                repositories: repository.clone(),
            },
        ),
        HealthCmd::Skills {
            skill,
            record,
            include_deferred,
        } => {
            if *record {
                gov_runtime::skills::record(&p, skill.as_deref())
            } else {
                let (findings, detail) = gov_runtime::skills::regression(
                    &p,
                    &gov_runtime::skills::RegressionOptions {
                        execute: true,
                        only: skill.clone(),
                        observe: true,
                        include_deferred: *include_deferred,
                    },
                );
                Ok(
                    json!({"findings": findings, "detail": detail, "ok": !findings.iter().any(|f| matches!(f["severity"].as_str(), Some("critical") | Some("high") | Some("medium")))}),
                )
            }
        }
    }
}
// ---- end WS-2 additive block
#[derive(Subcommand)]
enum PluginsCmd {
    Register {
        #[arg(long)]
        descriptor: String,
    },
    /// Remove a plugin's registration (the descriptor reverts to hand-declared standing)
    Unregister {
        plugin_id: String,
    },
    /// The authoritative plugin registry (governance/generated/plugin-registry.json)
    Registry,
    List,
    Health {
        #[arg(long)]
        ping: bool,
    },
}
#[derive(Subcommand)]
enum PolicyCmd {
    Overrides,
    Effective { policy: String },
}
#[derive(Subcommand)]
enum LessonsCmd {
    Cluster {
        #[arg(long)]
        inbox: Option<PathBuf>,
        #[arg(long)]
        proposals: Option<PathBuf>,
        #[arg(long)]
        write: bool,
    },
}

#[derive(Subcommand)]
enum AdoptCmd {
    Baseline,
    Inventory,
    Classify,
    Map,
    Plan,
    TestDesign,
    Review {
        #[arg(long)]
        verdict: String,
        #[arg(long)]
        reviewer_session: Option<String>,
        /// Must equal the declared acting role when both are given (one role per invocation); alone, it declares it
        #[arg(long)]
        reviewer_role: Option<String>,
        #[arg(long)]
        notes: Option<String>,
    },
    Migrate {
        #[arg(long)]
        batch: Option<i64>,
        #[arg(long)]
        source: Option<String>,
        /// Deprecated and ignored: destructive entries execute only with an answered Human Decision Gate record
        #[arg(long)]
        gate_answer: Vec<String>,
        #[arg(long)]
        name: Option<String>,
        #[arg(long)]
        alias: Option<String>,
    },
    VerifyMigration {
        #[arg(long)]
        verdict: Option<String>,
        /// Must equal the declared acting role when both are given (one role per invocation); alone, it declares it
        #[arg(long)]
        verifier_role: Option<String>,
    },
    ExtractLegacy,
    BuildMemory,
    VerifyMemory {
        #[arg(long)]
        verdict: Option<String>,
        /// Must equal the declared acting role when both are given (one role per invocation); alone, it declares it
        #[arg(long)]
        verifier_role: Option<String>,
    },
    Audit {
        #[arg(long)]
        accept_exceptions: bool,
    },
    Status,
    Rollback {
        #[arg(long)]
        batch: i64,
    },
}
#[derive(Subcommand)]
enum UpstreamCmd {
    Prepare {
        lesson: String,
    },
    Submit {
        packet: String,
        #[arg(long)]
        destination: String,
        #[arg(long)]
        approved_by: Option<String>,
    },
}
#[derive(Subcommand)]
enum TaskCmd {
    Create {
        #[arg(long)]
        class: Option<String>,
        #[arg(long)]
        objective: String,
        #[arg(long)]
        title: Option<String>,
        #[arg(long)]
        feature: Option<String>,
        #[arg(long)]
        deps: Option<String>,
        #[arg(long)]
        allowed: Option<String>,
        #[arg(long)]
        status: Option<String>,
        #[arg(long)]
        fields: Option<String>,
        #[arg(long)]
        id: Option<String>,
    },
    List {
        #[arg(long)]
        status: Option<String>,
    },
    Show {
        id: String,
    },
    Status {
        id: String,
        status: String,
        #[arg(long)]
        note: Option<String>,
    },
    Claim {
        id: String,
    },
    Release {
        id: String,
        #[arg(long)]
        force: bool,
    },
    Close {
        id: String,
        #[arg(long)]
        report: String,
        #[arg(long)]
        force: bool,
    },
    Dag,
    Replan,
    /// WS-5 (P2-AR-0036, BC-P2-24) additive: generate the governed, linked work the recorded events call for
    /// (`--dry-run` reports it and writes nothing)
    Generate {
        #[arg(long)]
        dry_run: bool,
    },
}
#[derive(Subcommand)]
enum CitCmd {
    Propose {
        #[arg(long)]
        proposal: String,
        #[arg(long)]
        trigger: Option<String>,
        #[arg(long)]
        targets: Option<String>,
        #[arg(long)]
        manifest: Option<String>,
        #[arg(long)]
        title: Option<String>,
    },
    Simulate {
        id: String,
    },
    Approve {
        id: String,
        /// Recorded as who applied the approval (default: the acting role); human approval is derived from the
        /// answered gate, never from this field
        #[arg(long)]
        by: Option<String>,
        #[arg(long, default_value = "human")]
        method: String,
    },
    Reject {
        id: String,
        /// Recorded as who rejected (default: the acting role)
        #[arg(long)]
        by: Option<String>,
        #[arg(long)]
        reason: Option<String>,
    },
    Execute {
        id: String,
    },
    Rollback {
        id: String,
        #[arg(long)]
        reason: Option<String>,
    },
    List,
    Show {
        id: String,
    },
    // ---- WS-4 (P2-AR-0025, BC-P2-13/04) additive variants
    /// Materiality of a CIT's manifest, or of changes already made to the given paths (read-only; BC-P2-13)
    Classify {
        /// a CIT id: classify its mutation manifest
        #[arg(long)]
        id: Option<String>,
        /// comma-separated repository paths: classify their change since --base (default HEAD)
        #[arg(long)]
        paths: Option<String>,
        #[arg(long)]
        base: Option<String>,
    },
    /// Detect upstream changes made outside change control and propagate them as CIT-E would (BC-P2-04)
    Propagate {
        #[arg(long)]
        dry_run: bool,
    },
}
#[derive(Subcommand)]
enum ContextCmd {
    Compile {
        task: String,
    },
    // ---- WS-4 (P2-AR-0017, BC-P2-17/19/20): input manifest, delivery verification, receipt validation
    /// Resolve the task's mandatory input manifest (W3): what is required, what each id resolved to, what blocks
    Manifest {
        task: String,
    },
    /// Verify a compiled packet still delivers the task's declared inputs at their current versions (W4/W10)
    Verify {
        task: String,
        /// packet_hash (or a prefix of >= 12 hex chars); default: the packet last compiled
        #[arg(long)]
        hash: Option<String>,
    },
    /// Show a compiled packet from the packet history
    Show {
        task: String,
        #[arg(long)]
        hash: Option<String>,
    },
    /// Validate a consumption receipt / worker return against the task's manifest (W5; dry run, writes nothing)
    Receipt {
        task: String,
        #[arg(long)]
        file: String,
    },
    // ---- WS-4 (P2-AR-0025, BC-P2-04) additive variant
    /// Derived staleness of a task: what its work consumed, which inputs changed since, whether that was propagated
    Staleness {
        task: String,
    },
}
// ---- WS-4 (P2-AR-0017, BC-P2-21): artefact identity and record-level lineage
#[derive(Subcommand)]
enum ArtefactCmd {
    /// The W1 identity of a governed artefact (id, type, canonical path, authority, lifecycle, version/hash,
    /// provenance, supersession lineage, expected and actual consumers)
    Show { id: String },
    /// Identity and lineage problems: misplaced records, duplicate ids, stale links, unconsumed outputs
    Check,
    /// Forward (impact) or reverse (upstream) lineage of an artefact over canonical edges
    Lineage {
        id: String,
        /// `down` (what depends on it) or `up` (what it traces back to)
        #[arg(long, default_value = "down")]
        direction: String,
        #[arg(long, default_value_t = 6)]
        depth: usize,
    },
}
#[derive(Subcommand)]
enum CheckpointCmd {
    Create {
        #[arg(long)]
        next_action: String,
        #[arg(long)]
        task: Option<String>,
        #[arg(long, default_value = "manual")]
        trigger: String,
        #[arg(long)]
        step: Option<String>,
        #[arg(long)]
        tests_status: Option<String>,
    },
    Latest,
    Watchdog {
        #[arg(long, default_value = "0")]
        utilisation: f64,
        #[arg(long, default_value = "0")]
        ops: i64,
        #[arg(long)]
        task: Option<String>,
        #[arg(long, default_value = "gov continue")]
        next_action: String,
    },
    // ---- WS-4 (P2-AR-0025, BC-P2-05) additive variant
    /// Whether a checkpoint (default: the latest) still describes the material state it captured
    Freshness {
        id: Option<String>,
    },
}
#[derive(Subcommand)]
enum SkillsCmd {
    List,
    Resolve { task: String },
}
#[derive(Subcommand)]
enum ToolsCmd {
    List,
    Registry,
    Resolve {
        #[arg(long)]
        role: Option<String>,
        #[arg(long)]
        capability: String,
    },
    Install {
        #[arg(long)]
        descriptor: String,
        #[arg(long)]
        role: Option<String>,
        #[arg(long)]
        execute: bool,
    },
    Health,
}
#[derive(Subcommand)]
enum HandoffCmd {
    Create {
        #[arg(long)]
        to_role: String,
        #[arg(long)]
        task: String,
        #[arg(long)]
        fields: Option<String>,
    },
    Return {
        id: String,
        #[arg(long)]
        file: String,
    },
}
#[derive(Subcommand)]
enum MemoryCmd {
    Query {
        query: String,
        #[arg(long, default_value = "0")]
        k: usize,
        #[arg(long)]
        route: Option<String>,
        #[arg(long)]
        include_historical: bool,
    },
    Verify,
    Freshness,
    Rebuild {
        #[arg(long)]
        incremental: bool,
    },
    Graph {
        node: String,
        #[arg(long, default_value = "1")]
        depth: usize,
    },
    Impact {
        seeds: String,
        #[arg(long, default_value = "2")]
        depth: usize,
    },
    /// Benchmark embedder/reranker candidates on the held-out set (evidence-based selection, framework 14.3)
    Benchmark {
        #[arg(long = "candidate")]
        candidates: Vec<String>,
        #[arg(long)]
        heldout: Option<PathBuf>,
        #[arg(long)]
        record: bool,
        /// With --record: the task that commissioned the benchmark (recorded among the work the research influenced)
        #[arg(long)]
        task: Option<String>,
    },
    /// Change the retrieval profile through the governed path (BC-P2-30): benchmark evidence (--research), the
    /// change-control gate for its radius (raised on the first call; --gate once an answer authorises it), a full
    /// re-index and a recorded held-out regression (rolled back when it does not hold)
    Select {
        candidate: String,
        #[arg(long)]
        research: Option<String>,
        /// Recorded as who selected (default: the acting role); it asserts no human approval
        #[arg(long)]
        by: Option<String>,
        /// The answered change-control gate raised for this exact change
        #[arg(long)]
        gate: Option<String>,
    },
    /// Graph integrity: orphan, dangling, stale, reversed and ill-typed relationships (BC-P2-28)
    Integrity,
    /// The retrieval profile: embedder and reranker component identities (adapter, model artefact, runtime) and
    /// whether a decision governs it (BC-P2-30)
    Profile,
    /// Generate a starter held-out set from the live index (only when the file has no queries)
    HeldoutStarter {
        #[arg(long)]
        force: bool,
    },
    /// Report a retrieval miss (framework §18): the query and the artefacts that should have answered it are
    /// recorded as a memory-quality failure event (deduplicated by signature, never indexed)
    Miss {
        #[arg(long)]
        query: String,
        /// Record ids or paths that should have been returned (repeatable)
        #[arg(long = "expected")]
        expected: Vec<String>,
        #[arg(long)]
        detail: Option<String>,
    },
    /// Failure records whose follow-up is not yet linked to governed work
    Failures,
}
#[derive(Subcommand)]
enum GateCmd {
    Create {
        #[arg(long)]
        question: String,
        #[arg(long)]
        fields: Option<String>,
    },
    Present {
        id: String,
        /// Owner-signed `human-gate-receipt` (the human acknowledges the rendered package); default: none. With
        /// `--receipt-inbox`, the human-channel inbox is searched.
        #[arg(long)]
        receipt_file: Option<PathBuf>,
        #[arg(long)]
        receipt_inbox: bool,
    },
    List,
    /// A gate as the OS sees it: T2 binding, what it authorises, whether its answer verifies
    Show {
        id: String,
    },
    Revoke {
        id: String,
        #[arg(long)]
        reason: Option<String>,
    },
}
#[derive(Subcommand)]
enum ReadinessCmd {
    Check { feature: String },
    Plan { feature: String },
}
#[derive(Subcommand)]
enum TelemetryCmd {
    Summary,
    Emit {
        #[arg(long)]
        name: String,
        #[arg(long)]
        attrs: Option<String>,
    },
}
#[derive(Subcommand)]
enum AdaptersCmd {
    Generate,
    Verify,
}
#[derive(Subcommand)]
enum ReleaseCmd {
    Build {
        #[arg(long)]
        version: String,
        #[arg(long)]
        out: Option<PathBuf>,
        #[arg(long, default_value = "READY_FOR_INDEPENDENT_OS_VERIFICATION")]
        certification: String,
        #[arg(long)]
        evidence: Option<String>,
        #[arg(long)]
        canonical: Option<PathBuf>,
    },
    Verify {
        dir: PathBuf,
    },
    /// Record this project's own product release (`REL-<version>` under spec/releases): derived from the work that
    /// produced it, validated by the evidence that accepted it (W8 forward lineage; WS-8 IP-R2-WS08-7)
    Record {
        #[arg(long)]
        version: String,
        #[arg(long)]
        title: String,
        /// Comma-separated task / report / feature / requirement / decision ids
        #[arg(long, value_delimiter = ',')]
        derived_from: Vec<String>,
        /// Comma-separated audit / report / test-obligation / scenario ids
        #[arg(long, value_delimiter = ',')]
        validated_by: Vec<String>,
        #[arg(long)]
        notes: Option<String>,
    },
}
#[derive(Subcommand)]
enum KernelCmd {
    Verify,
    Reinstall {
        #[arg(long)]
        source: Option<String>,
        /// Request below-floor admission; the authority is an owner-signed token in protected machine state
        #[arg(long)]
        break_glass: bool,
    },
    /// Trust verdict for the installed kernel (what constitutional policy is being read from)
    Trust,
    /// L4+: raise a gate to proceed on an installed kernel that failed verification
    Override {
        #[arg(long)]
        reason: Option<String>,
    },
}
#[derive(Subcommand)]
enum ContractCmd {
    /// Fail closed unless the canonical import, the source lock and the compiled form all bind the approved source
    Verify,
    /// Regenerate the compiled form, source lock, evidence map and generated view from the approved source
    Compile,
    /// P2-AR-0042 (BC-P2-02, frozen AC-10): the suite-to-contract matrix — every capability, its evidence owners,
    /// their tiers and their last-run evidence — generated from the evidence map after `contract verify` passes
    Matrix {
        /// `cargo test --lib` output to read the lib test owners' last runs from (repeatable)
        #[arg(long = "lib-results")]
        lib_results: Vec<String>,
        /// `cargo test --test certification` output (repeatable)
        #[arg(long = "certification-results")]
        certification_results: Vec<String>,
        /// Held-out re-run output with `===== <suite> :: <binary> =====` blocks (repeatable)
        #[arg(long = "heldout-results")]
        heldout_results: Vec<String>,
        /// `gov --json health run` or `gov --json doctor` output (repeatable)
        #[arg(long = "health-results")]
        health_results: Vec<String>,
        /// Write suite-to-contract.json and suite-to-contract.md into this directory
        #[arg(long)]
        out: Option<String>,
    },
}

#[derive(Subcommand)]
enum TrustCmd {
    /// Posture, trust anchor, protected floors, currency and any `DEGRADED — RECOVERY ONLY` marking
    Status,
    /// Administrator: install this machine's first trust anchor from the platform/admin domain
    Provision {
        /// Path to the public root metadata, supplied from the administrator domain (never from the repository)
        #[arg(long)]
        anchor: String,
    },
    /// Accept a successor root (one version at a time, outgoing and incoming quorums both required)
    RootUpdate {
        #[arg(long)]
        anchor: String,
    },
    /// Where an owner-signed break-glass authorisation must be placed, and what it must bind
    BreakGlass,
    /// Replay any interrupted install transaction and report what was done
    RecoverTransactions,
    /// Administrator (P2-ADJ-0002): install the owner's T2 binding authority on this provisioned machine, so T2 facts
    /// it writes are honoured on the owner's other provisioned machines
    Bind {
        /// Owner-signed `t2-binding-authority` document (signed by the root-delegated `t2-binding` role), from the
        /// administrator domain
        #[arg(long)]
        authority: String,
        /// A binding key the authority authorises (`key_hex`), from the administrator domain — never a repository
        #[arg(long)]
        key: String,
    },
    /// The authenticated human channel for Human Decision Gate answers: anchor, inbox, what a signed answer binds
    HumanChannel {
        /// Administrator: install the owner's public `human-gate` keys (a self-signed `human-channel-anchor`
        /// document from the administrator domain) on a machine without a Signed Release Root
        #[arg(long)]
        provision: Option<String>,
    },
    /// P2-ADJ-0002 continuity: re-seal, under the owner's T2 binding authority (`gov trust bind`), the records this
    /// machine sealed with its own key while it was provisioned (records sealed while unprovisioned, and records whose
    /// seal does not verify, are never re-sealed). The binding status is part of `gov trust status` (`t2_binding`).
    Reseal {
        /// Report what would be resealed and write nothing
        #[arg(long)]
        dry_run: bool,
    },
}

#[derive(Subcommand)]
enum CapCmd {
    Ecosystems,
    Plugins,
    Invoke {
        #[arg(long)]
        plugin: String,
        #[arg(long)]
        inputs: String,
    },
    /// Act as a gov-capability/1 `embed` plugin over stdin/stdout using the built-in embedder (reference plugin; --reverse yields a distinct vector space for tests)
    ServeEmbed {
        #[arg(long)]
        reverse: bool,
        #[arg(long, default_value = "gov-builtin-embed")]
        id: String,
    },
}
#[derive(Subcommand)]
enum ClaimsCmd {
    List,
    Sweep,
}

#[derive(Args)]
struct Empty {}

fn parse_json_arg(s: &Option<String>) -> Result<Value> {
    match s {
        None => Ok(json!({})),
        Some(t) => {
            if let Some(path) = t.strip_prefix('@') {
                let text = gov_runtime::util::read_text(Path::new(path))?;
                if path.ends_with(".yaml") || path.ends_with(".yml") {
                    Ok(serde_yaml::from_str(&text)?)
                } else {
                    Ok(serde_json::from_str(&text)?)
                }
            } else {
                serde_json::from_str(t)
                    .or_else(|_| serde_yaml::from_str(t))
                    .map_err(|e| GovError::new("USAGE", format!("invalid JSON/YAML argument: {e}")))
            }
        }
    }
}
fn csv(s: &Option<String>) -> Vec<String> {
    s.as_ref()
        .map(|x| {
            x.split(',')
                .map(|y| y.trim().to_string())
                .filter(|y| !y.is_empty())
                .collect()
        })
        .unwrap_or_default()
}
fn load_file_value(path: &str) -> Result<Value> {
    parse_json_arg(&Some(format!("@{path}")))
}

fn open_project(cli: &Cli, need_install: bool) -> Result<Project> {
    let root = match &cli.root {
        Some(r) => r.clone(),
        None => gov_runtime::project::find_root(&std::env::current_dir()?)
            .unwrap_or(std::env::current_dir()?),
    };
    // the acting role is the process-wide declaration installed by `run` (BC-P2-08)
    let p = Project::open(&root).with_session(cli.session.clone(), None);
    if need_install {
        p.require_installed()?;
    }
    Ok(p)
}
/// **BC-P2-08 — the one acting-role resolution for this invocation.** The global `--role` (else `GOV_ROLE`) is the
/// declaration; the adopt stages' own `--reviewer-role` / `--verifier-role` may declare it when nothing else does,
/// and must agree with it when both are given. Nothing declared means no privileged authority.
fn declared_role(cli: &Cli) -> Result<gov_runtime::authority::ActingRole> {
    let base = gov_runtime::authority::resolve_acting_role(cli.role.as_deref());
    let stage_flag = match &cli.cmd {
        Cmd::Adopt { stage } | Cmd::Migrate { stage } => match stage {
            AdoptCmd::Review { reviewer_role, .. } => reviewer_role.clone(),
            AdoptCmd::VerifyMigration { verifier_role, .. } => verifier_role.clone(),
            AdoptCmd::VerifyMemory { verifier_role, .. } => verifier_role.clone(),
            _ => None,
        },
        // the auto-install conditions (install authority, no privilege escalation) are the acting role's: a
        // subcommand `--role` is the same declaration, never a second role for one invocation
        Cmd::Tools {
            op: ToolsCmd::Install { role, .. },
        } => role.clone(),
        _ => None,
    }
    .filter(|f| !f.trim().is_empty());
    match stage_flag {
        Some(f) if base.is_declared() && f != base.id() => Err(GovError::new(
            "ROLE_CONFLICT",
            format!(
                "two different acting roles were declared for one invocation ('{}' via {} and '{f}' via the stage flag); declare one role",
                base.id(),
                base.source.as_str()
            ),
        )),
        Some(f) if !base.is_declared() => Ok(gov_runtime::authority::ActingRole {
            role: Some(f),
            source: gov_runtime::authority::RoleSource::Flag,
        }),
        _ => Ok(base),
    }
}

/// The producing actor of an adoption stage as the caller declared it (WS-9/11 IP-3): the session from `--session` or
/// `GOV_SESSION` and the acting role this process installed. `None` when no session was declared, so the stage can
/// record its documented fallback instead of an invented session.
fn adopt_actor(cli: &Cli) -> Option<gov_runtime::migrations::identity::Actor> {
    let session = cli
        .session
        .clone()
        .or_else(|| std::env::var("GOV_SESSION").ok())
        .filter(|s| !s.trim().is_empty())?;
    let role = gov_runtime::authority::installed_acting_role()
        .and_then(|r| r.role.clone())
        .or_else(|| gov_runtime::authority::resolve_acting_role(cli.role.as_deref()).role);
    Some(gov_runtime::migrations::identity::Actor::declared(
        &session,
        role.as_deref(),
    ))
}

/// The G0 label of an invocation (`orchestration::control::COMMAND_GUARDS`): every command maps to exactly one.
fn g0_label(cmd: &Cmd) -> String {
    let s = |x: &str| x.to_string();
    match cmd {
        Cmd::Version => s("version"),
        Cmd::Init { .. } => s("init"),
        Cmd::Status => s("status"),
        Cmd::Continue { claim } => s(if *claim {
            "continue --claim"
        } else {
            "continue"
        }),
        Cmd::Decide { .. } => s("gate answer"),
        Cmd::Audit { no_persist, .. } => s(if *no_persist {
            "audit --no-persist"
        } else {
            "audit"
        }),
        Cmd::Verify { what } => s(if what == "governance" {
            "verify governance"
        } else {
            "verify product"
        }),
        Cmd::Pause { .. } => s("pause"),
        Cmd::FreezeWrites { .. } => s("freeze writes"),
        Cmd::CancelAgents { .. } => s("cancel agents"),
        Cmd::Resume => s("resume"),
        Cmd::Doctor => s("doctor"),
        Cmd::RebuildMemory { .. } => s("rebuild-memory"),
        Cmd::Recover { dry_run } => s(if *dry_run {
            "recover --dry-run"
        } else {
            "recover"
        }),
        Cmd::Adopt { stage } | Cmd::Migrate { stage } => format!(
            "adopt {}",
            match stage {
                AdoptCmd::Baseline => "baseline",
                AdoptCmd::Inventory => "inventory",
                AdoptCmd::Classify => "classify",
                AdoptCmd::Map => "map",
                AdoptCmd::Plan => "plan",
                AdoptCmd::TestDesign => "test-design",
                AdoptCmd::Review { .. } => "review",
                AdoptCmd::Migrate { .. } => "migrate",
                AdoptCmd::VerifyMigration { .. } => "verify-migration",
                AdoptCmd::ExtractLegacy => "extract-legacy",
                AdoptCmd::BuildMemory => "build-memory",
                AdoptCmd::VerifyMemory { .. } => "verify-memory",
                AdoptCmd::Audit { .. } => "audit",
                AdoptCmd::Status => "status",
                AdoptCmd::Rollback { .. } => "rollback",
            }
        ),
        Cmd::Update {
            apply, rollback, ..
        } => s(if *rollback {
            "update --rollback"
        } else if *apply {
            "update --apply"
        } else {
            "update --check"
        }),
        Cmd::Trust { op } => s(match op {
            TrustCmd::Status => "trust status",
            TrustCmd::Provision { .. } => "trust provision",
            TrustCmd::RootUpdate { .. } => "trust root-update",
            TrustCmd::BreakGlass => "trust break-glass",
            TrustCmd::RecoverTransactions => "trust recover-transactions",
            TrustCmd::Bind { .. } => "trust bind",
            TrustCmd::HumanChannel { provision } => {
                if provision.is_some() {
                    "trust human-channel --provision"
                } else {
                    "trust human-channel"
                }
            }
            TrustCmd::Reseal { dry_run } => {
                if *dry_run {
                    "trust reseal --dry-run"
                } else {
                    "trust reseal"
                }
            }
        }),
        Cmd::Contract { op } => s(match op {
            ContractCmd::Verify => "contract verify",
            ContractCmd::Compile => "contract compile",
            ContractCmd::Matrix { .. } => "contract matrix",
        }),
        Cmd::Upstream { op } => s(match op {
            UpstreamCmd::Prepare { .. } => "upstream prepare",
            UpstreamCmd::Submit { .. } => "upstream submit",
        }),
        Cmd::Task { op } => s(match op {
            TaskCmd::Create { .. } => "task create",
            TaskCmd::List { .. } => "task list",
            TaskCmd::Show { .. } => "task show",
            TaskCmd::Status { .. } => "task status",
            TaskCmd::Claim { .. } => "task claim",
            TaskCmd::Release { force, .. } => {
                if *force {
                    "task release --force"
                } else {
                    "task release"
                }
            }
            TaskCmd::Close { force, .. } => {
                if *force {
                    "task close --force"
                } else {
                    "task close"
                }
            }
            TaskCmd::Dag => "task dag",
            TaskCmd::Replan => "replan",
            // WS-5 (P2-AR-0036) additive arm
            TaskCmd::Generate { dry_run } => {
                if *dry_run {
                    "task generate --dry-run"
                } else {
                    "task generate"
                }
            }
        }),
        Cmd::Cit { op } => s(match op {
            CitCmd::Propose { .. } => "cit propose",
            CitCmd::Simulate { .. } => "cit simulate",
            CitCmd::Approve { .. } => "cit approve",
            CitCmd::Reject { .. } => "cit reject",
            CitCmd::Execute { .. } => "cit execute",
            CitCmd::Rollback { .. } => "cit rollback",
            CitCmd::List => "cit list",
            CitCmd::Show { .. } => "cit show",
            CitCmd::Classify { .. } => "cit classify",
            CitCmd::Propagate { dry_run } => {
                if *dry_run {
                    "cit propagate --dry-run"
                } else {
                    "cit propagate"
                }
            }
        }),
        Cmd::Context { op } => s(match op {
            ContextCmd::Compile { .. } => "context compile",
            ContextCmd::Manifest { .. } => "context manifest",
            ContextCmd::Verify { .. } => "context verify",
            ContextCmd::Show { .. } => "context show",
            ContextCmd::Receipt { .. } => "context receipt",
            ContextCmd::Staleness { .. } => "context staleness",
        }),
        Cmd::Checkpoint { op } => s(match op {
            CheckpointCmd::Create { .. } | CheckpointCmd::Watchdog { .. } => "checkpoint",
            CheckpointCmd::Latest => "checkpoint latest",
            CheckpointCmd::Freshness { .. } => "checkpoint freshness",
        }),
        Cmd::Skills { op } => s(match op {
            SkillsCmd::List => "skills list",
            SkillsCmd::Resolve { .. } => "skills resolve",
        }),
        Cmd::Tools { op } => s(match op {
            ToolsCmd::List => "tools list",
            ToolsCmd::Registry => "tools registry",
            ToolsCmd::Resolve { .. } => "tools resolve",
            ToolsCmd::Install { .. } => "tools install",
            ToolsCmd::Health => "tools health",
        }),
        Cmd::Handoff { op } => s(match op {
            HandoffCmd::Create { .. } => "handoff create",
            HandoffCmd::Return { .. } => "handoff return",
        }),
        Cmd::Memory { op } => s(match op {
            MemoryCmd::Query { .. } => "memory query",
            MemoryCmd::Verify => "memory verify",
            MemoryCmd::Freshness => "memory freshness",
            MemoryCmd::Rebuild { .. } => "memory rebuild",
            MemoryCmd::Graph { .. } => "memory graph",
            MemoryCmd::Impact { .. } => "memory impact",
            MemoryCmd::Benchmark { record, .. } => {
                if *record {
                    "memory benchmark --record"
                } else {
                    "memory benchmark"
                }
            }
            MemoryCmd::Select { .. } => "memory select",
            MemoryCmd::HeldoutStarter { .. } => "memory heldout-starter",
            MemoryCmd::Miss { .. } => "memory miss",
            MemoryCmd::Failures => "memory failures",
            MemoryCmd::Integrity => "memory integrity",
            MemoryCmd::Profile => "memory profile",
        }),
        Cmd::Gate { op } => s(match op {
            GateCmd::Create { .. } => "gate create",
            GateCmd::Present { .. } => "gate present",
            GateCmd::List => "gate list",
            GateCmd::Show { .. } => "gate show",
            GateCmd::Revoke { .. } => "gate revoke",
        }),
        Cmd::Readiness { op } => s(match op {
            ReadinessCmd::Check { .. } => "readiness check",
            ReadinessCmd::Plan { .. } => "readiness plan",
        }),
        Cmd::Intent { .. } => s("intent"),
        Cmd::Route { record, report, .. } => s(if record.is_some() {
            "route --record"
        } else if *report {
            "route --report"
        } else {
            "route"
        }),
        Cmd::Telemetry { op } => s(match op {
            TelemetryCmd::Summary => "telemetry summary",
            TelemetryCmd::Emit { .. } => "telemetry emit",
        }),
        Cmd::Adapters { op } => s(match op {
            AdaptersCmd::Generate => "adapters generate",
            AdaptersCmd::Verify => "adapters verify",
        }),
        Cmd::Release { op } => s(match op {
            ReleaseCmd::Build { .. } => "release build",
            ReleaseCmd::Verify { .. } => "release verify",
            ReleaseCmd::Record { .. } => "release record",
        }),
        Cmd::Kernel { op } => s(match op {
            KernelCmd::Verify => "kernel verify",
            KernelCmd::Trust => "kernel trust",
            KernelCmd::Reinstall { .. } => "kernel reinstall",
            KernelCmd::Override { .. } => "kernel override",
        }),
        Cmd::Capabilities { op } => s(match op {
            CapCmd::Ecosystems => "capabilities ecosystems",
            CapCmd::Plugins => "capabilities plugins",
            CapCmd::Invoke { .. } => "capabilities invoke",
            CapCmd::ServeEmbed { .. } => "capabilities serve-embed",
        }),
        Cmd::Claims { op } => s(match op {
            ClaimsCmd::List => "claims list",
            ClaimsCmd::Sweep => "claims sweep",
        }),
        Cmd::Mcp { .. } => s("mcp"),
        Cmd::Lessons { .. } => s("lessons cluster"),
        Cmd::Plugins { op } => s(match op {
            PluginsCmd::Register { .. } => "plugins register",
            PluginsCmd::Unregister { .. } => "plugins unregister",
            PluginsCmd::Registry => "plugins registry",
            PluginsCmd::List => "plugins list",
            PluginsCmd::Health { ping } => {
                if *ping {
                    "plugins health --ping"
                } else {
                    "plugins health"
                }
            }
        }),
        Cmd::Policy { op } => s(match op {
            PolicyCmd::Overrides => "policy overrides",
            PolicyCmd::Effective { .. } => "policy effective",
        }),
        Cmd::Artefact { op } => s(match op {
            ArtefactCmd::Show { .. } => "artefact show",
            ArtefactCmd::Check => "artefact check",
            ArtefactCmd::Lineage { .. } => "artefact lineage",
        }),
        Cmd::Health { op } => s(match op {
            HealthCmd::Run { no_persist, .. } => {
                if *no_persist {
                    "health run --no-persist"
                } else {
                    "health run"
                }
            }
            HealthCmd::Status => "health status",
            HealthCmd::Checks => "health checks",
            HealthCmd::History { .. } => "health history",
            HealthCmd::Show { .. } => "health show",
            HealthCmd::Guard { .. } => "health guard",
            HealthCmd::Currency => "health currency",
            HealthCmd::Product { .. } => "health product",
            HealthCmd::Skills { record, .. } => {
                if *record {
                    "health skills --record"
                } else {
                    "health skills"
                }
            }
            HealthCmd::CloseCheck { .. } => "health close-check",
            HealthCmd::Qualify { .. } => "health qualify",
        }),
        Cmd::Oracle { op } => s(match op {
            OracleCmd::Format => "oracle format",
            OracleCmd::Validate { .. } => "oracle validate",
        }),
        // WS-4 (P2-AR-0025) additive arm
        Cmd::Session { op } => s(match op {
            SessionCmd::Close { .. } => "session close",
        }),
        // WS-10 (P2-AR-0031) additive arms
        Cmd::Research { op } => s(match op {
            ResearchCmd::Record { .. } => "research record",
            ResearchCmd::Update { .. } => "research update",
            ResearchCmd::Conclude { .. } => "research conclude",
            ResearchCmd::Withdraw { .. } => "research withdraw",
            ResearchCmd::Show { .. } => "research show",
            ResearchCmd::Check => "research check",
            ResearchCmd::Sync => "research sync",
        }),
        Cmd::Experiment { op } => s(match op {
            ExperimentCmd::Design { .. } => "experiment design",
            ExperimentCmd::Update { .. } => "experiment update",
            ExperimentCmd::Run { .. } => "experiment run",
            ExperimentCmd::Reproduce { .. } => "experiment reproduce",
            ExperimentCmd::Conclude { .. } => "experiment conclude",
            ExperimentCmd::Promote { .. } => "experiment promote",
            ExperimentCmd::Abandon { .. } => "experiment abandon",
            ExperimentCmd::Show { .. } => "experiment show",
            ExperimentCmd::Check => "experiment check",
        }),
        Cmd::Data { op } => s(match op {
            DataCmd::Register { .. } => "data register",
            DataCmd::Show { .. } => "data show",
        }),
        Cmd::Scenario { op } => s(match op {
            ScenarioCmd::Trace { .. } => "scenario trace",
            ScenarioCmd::Check => "scenario check",
        }),
    }
}

/// **G0 (Contract v3 O5; BC-P2-08)**: every invocation passes the guard for its label before anything runs —
/// emergency-control state (FREEZE_WRITES / PAUSE, with the explicit recovery allow-lists) and the authority class of
/// the command, evaluated for the role the caller declared (against the project's verified policy, or before the
/// first install against the kernel embedded in this binary).
fn g0(cli: &Cli) -> Result<()> {
    use gov_runtime::orchestration::control;
    let label = g0_label(&cli.cmd);
    let guard = control::command_guard(&label).ok_or_else(|| {
        GovError::new(
            "G0_UNCLASSIFIED",
            format!(
                "command '{label}' has no G0 classification; an unclassified command is refused"
            ),
        )
    })?;
    if let control::Scope::Outside(_) = guard.scope {
        return Ok(());
    }
    let p = match &cli.cmd {
        // lifecycle ingress into a repository that may have no installation yet: the command's own root
        Cmd::Init { .. } | Cmd::Adopt { .. } | Cmd::Migrate { .. } => {
            let root = cli.root.clone().unwrap_or(std::env::current_dir()?);
            Project::open(&root).with_session(cli.session.clone(), None)
        }
        _ => open_project(cli, false)?,
    };
    control::g0(&p, &label)?;
    Ok(())
}

/// BC-P2-09 at the product surface: CIT approval/execution reads its gate's answer itself, so the gate it names must
/// be one gov wrote and whose answer verifies (`gates::require_honoured_answers`).
fn cit_gate_precheck(p: &Project, cit_id: &str) -> Result<()> {
    let store = gov_runtime::records::RecordStore::load(&p.root);
    let gate = store
        .get(cit_id)
        .map(|c| c.get("human_gate"))
        .unwrap_or_default();
    gov_runtime::orchestration::gates::require_honoured_answers(p, &[gate])
}

/// `gov continue` with the derived index as the dispatch sees it (WS-4 IP-6). **Integration point (WS-5,
/// `status::continue_work`)**: once `continue_work` takes the handle (`db: impl Into<context::IndexHandle<'a>>`),
/// this body becomes the single call `gov_runtime::status::continue_work(p, index, claim)`. Until then an
/// unavailable index is refused typed, with its cause and the remediation, instead of failing inside the command.
fn continue_with_index(
    p: &Project,
    index: gov_runtime::context::IndexHandle,
    claim: bool,
) -> Result<Value> {
    match index {
        gov_runtime::context::IndexHandle::Open(d) => {
            gov_runtime::status::continue_work(p, d, claim)
        }
        gov_runtime::context::IndexHandle::Unavailable(e) => Err(GovError::new(
            "INDEX_UNAVAILABLE",
            format!("the derived index cannot be opened ({}: {}); the dispatch path that compiles the packet without it (IndexHandle::Unavailable) is not wired into `status::continue_work` in this build. Remediation: `gov rebuild-memory` rebuilds the derived index from Git and the authoritative records (it is permitted under FREEZE_WRITES/PAUSE)", e.code, e.message),
        )
        .with_details(json!({"cause": e.code, "message": e.message, "remediation": "gov rebuild-memory"}))),
    }
}

fn db(p: &Project) -> Result<RuntimeDb> {
    let d = RuntimeDb::open(&p.db_path())?;
    d.init_schema()?;
    Ok(d)
}

fn run(cli: &Cli) -> Result<Value> {
    let name = command_name(&cli.cmd);
    // BC-P2-08: resolve the acting role once and make it the role of every Project this process opens — including
    // those `init` and every `adopt`/`migrate` stage open internally — then pass the G0 guard.
    gov_runtime::authority::install_acting_role(declared_role(cli)?)?;
    // WS-9/11 r2 IP-R2-1 (BC-P2-08): the session this invocation declared (the global `--session`, else
    // GOV_SESSION) is installed once, as parsed here, so the runtime's adoption authorship reads the same declaration
    // the CLI resolved instead of re-parsing the process arguments
    gov_runtime::migrations::identity::install_declared_session(
        cli.session
            .clone()
            .or_else(|| std::env::var("GOV_SESSION").ok()),
    )?;
    g0(cli)?;
    let acting = gov_runtime::authority::default_role_id();
    match &cli.cmd {
        Cmd::Version => Ok(json!({"framework": gov_runtime::FRAMEWORK_NAME, "version": gov_runtime::VERSION, "cli_version": gov_runtime::CLI_VERSION, "runtime_version": gov_runtime::RUNTIME_VERSION, "index_version": gov_runtime::INDEX_VERSION})),
        Cmd::Init { source, name: pname, alias, intent, force, skip_index, channel, break_glass } => {
            let root = cli.root.clone().unwrap_or(std::env::current_dir()?);
            let pn = pname.clone().unwrap_or_else(|| root.file_name().map(|f| f.to_string_lossy().to_string()).unwrap_or("project".into()));
            let al = alias.clone().unwrap_or_else(|| format!("project-{}", &gov_runtime::util::sha256_text(&pn)[..6]));
            gov_runtime::init::init(&root, gov_runtime::init::InitOptions { source: source.clone(), project_name: pn, alias: al, mode: "init".into(), force: *force, intent: intent.clone(), skip_index: *skip_index, channel: channel.clone(), break_glass: *break_glass })
        }
        Cmd::Status => { let p = open_project(cli, true)?; gov_runtime::status::status(&p) }
        Cmd::Continue { claim } => {
            let p = open_project(cli, true)?;
            // WS-4 IP-6 / BC-P2-19 (W10): the derived index is optional for dispatch — it is opened here and handed on
            // as an `IndexHandle`, `Unavailable` (with the reason) when it cannot be opened, never a hard failure
            match gov_runtime::context::open_index(&p) {
                Ok(d) => continue_with_index(&p, gov_runtime::context::IndexHandle::Open(&d), *claim),
                Err(e) => continue_with_index(&p, gov_runtime::context::IndexHandle::Unavailable(e), *claim),
            }
        }
        Cmd::Decide { gate, option, by, rationale, answer_file, evidence } => { let p = open_project(cli, true)?; gov_runtime::orchestration::gates::answer(&p, gate, &gov_runtime::orchestration::gates::AnswerRequest { option: option.clone(), by: by.clone(), rationale: rationale.clone(), answer_file: answer_file.clone(), evidence: evidence.clone() }) }
        Cmd::Audit { deep, family, no_persist } => { let p = open_project(cli, true)?; run_audit(&p, *deep, family.clone(), !no_persist) }
        Cmd::Verify { what } => { let p = open_project(cli, true)?; if what == "governance" { run_audit(&p, false, vec![], true) } else { gov_runtime::verification::product_suite(&p) } }
        Cmd::Pause { reason } => { let p = open_project(cli, true)?; gov_runtime::orchestration::control::set(&p, "PAUSE", reason.as_deref()) }
        Cmd::FreezeWrites { reason } => { let p = open_project(cli, true)?; gov_runtime::orchestration::control::set(&p, "FREEZE_WRITES", reason.as_deref()) }
        Cmd::CancelAgents { reason } => { let p = open_project(cli, true)?; gov_runtime::orchestration::control::set(&p, "CANCEL_AGENTS", reason.as_deref()) }
        Cmd::Resume => { let p = open_project(cli, true)?; gov_runtime::orchestration::control::set(&p, "RESUME", None) }
        Cmd::Doctor => { let p = open_project(cli, false)?; let r = gov_runtime::doctor::run(&p)?; let v = serde_json::to_value(&r)?; if r.verdict == "UNHEALTHY" { return Err(GovError::new("UNHEALTHY", format!("doctor: UNHEALTHY ({} failed checks)", r.failed)).with_details(v)); } Ok(v) }
        Cmd::RebuildMemory { incremental } => { let p = open_project(cli, true)?; let r = gov_runtime::memory::indexer::rebuild(&p, gov_runtime::memory::indexer::IndexOptions { incremental: *incremental, observe_boundaries: true, ..Default::default() })?; Ok(serde_json::to_value(&r)?) }
        Cmd::Recover { dry_run } => { let p = open_project(cli, true)?; if !*dry_run { gov_runtime::authority::require(&p, "recover")?; } gov_runtime::recovery::recover(&p, *dry_run) }
        Cmd::Adopt { stage } | Cmd::Migrate { stage } => {
            let root = cli.root.clone().unwrap_or(std::env::current_dir()?);
            let session = cli.session.clone().or(std::env::var("GOV_SESSION").ok()).unwrap_or_else(gov_runtime::util::new_session_id);
            use gov_runtime::adopt as a;
            match stage {
                AdoptCmd::Baseline => a::a0_baseline(&root, &session), AdoptCmd::Inventory => a::a1_inventory(&root), AdoptCmd::Classify => a::a2_classify(&root),
                // WS-9/11 IP-3 (BC-P2-08): the producer recorded in the catalogue and the plan is the invocation's declared
                // session and role; with no declared session the stage falls back to the A0 planner session (recorded as such)
                AdoptCmd::Map => match adopt_actor(cli) { Some(actor) => a::a3_map_by(&root, &actor), None => a::a3_map(&root) },
                AdoptCmd::Plan => match adopt_actor(cli) { Some(actor) => a::a4_plan_by(&root, &actor), None => a::a4_plan(&root) },
                AdoptCmd::TestDesign => a::a5_test_design(&root),
                AdoptCmd::Review { verdict, reviewer_session, reviewer_role: _, notes } => a::a5_review(&root, verdict, reviewer_session.as_deref().unwrap_or(&session), &acting, notes.as_deref()),
                AdoptCmd::Migrate { batch, source, gate_answer, name: pn, alias } => { let pn2 = pn.clone().unwrap_or_else(|| root.file_name().map(|f| f.to_string_lossy().to_string()).unwrap_or("project".into())); let al = alias.clone().unwrap_or_else(|| format!("project-{}", &gov_runtime::util::sha256_text(&pn2)[..6])); a::a6_migrate(&root, *batch, source.as_deref(), gate_answer, &pn2, &al, &session) }
                AdoptCmd::VerifyMigration { verdict, verifier_role: _ } => a::a7_verify_migration(&root, verdict.as_deref(), &session, &acting),
                AdoptCmd::ExtractLegacy => a::a8_extract_legacy(&root), AdoptCmd::BuildMemory => a::a9_build_memory(&root, &session),
                AdoptCmd::VerifyMemory { verdict, verifier_role: _ } => a::a10_verify_memory(&root, verdict.as_deref(), &session, &acting),
                AdoptCmd::Audit { accept_exceptions } => a::a11_audit(&root, *accept_exceptions), AdoptCmd::Status => a::status(&root), AdoptCmd::Rollback { batch } => a::rollback_batch(&root, *batch),
            }
        }
        Cmd::Update { check, apply, rollback, channel, break_glass, source, approve, by, reason } => {
            let mut p = open_project(cli, true)?;
            if *rollback { return gov_runtime::update::rollback_opts(&mut p, None, reason.as_deref(), *break_glass); }
            let by = by.clone().unwrap_or_else(|| acting.clone());
            if *apply { gov_runtime::orchestration::gates::require_honoured_answers(&p, &gov_runtime::orchestration::gates::answered_gates_for_trigger(&p, "framework_update"))?; return gov_runtime::update::apply_update_opts(&mut p, source.as_deref(), *approve, &by, channel.clone(), *break_glass); }
            let _ = check; gov_runtime::update::check(&p, source.as_deref())
        }
        Cmd::Trust { op } => {
            let project_root = cli.root.clone().or_else(|| std::env::current_dir().ok());
            match op {
                TrustCmd::Status => gov_runtime::srr::status(),
                TrustCmd::Provision { anchor } => gov_runtime::srr::provision::provision(Path::new(anchor), project_root.as_deref()),
                TrustCmd::RootUpdate { anchor } => gov_runtime::srr::provision::root_update(Path::new(anchor), project_root.as_deref()),
                TrustCmd::BreakGlass => gov_runtime::srr::provision::break_glass_status(),
                TrustCmd::Bind { authority, key } => gov_runtime::srr::binding::bind(Path::new(authority), Path::new(key), project_root.as_deref()),
                TrustCmd::RecoverTransactions => {
                    let ms = gov_runtime::srr::state::MachineState::open()?;
                    let r = gov_runtime::srr::staging::recover(&ms)?;
                    Ok(json!({"replayed": r}))
                }
                TrustCmd::HumanChannel { provision } => {
                    // HUMAN_GATE_POLICY.human_channel.standalone_anchor_when_unprovisioned: the project's verified
                    // policy when there is one (a project may only tighten it), else the kernel compiled into this
                    // binary (P2-ADJ-0001: off)
                    let allowed = project_root
                        .as_deref()
                        .map(|r| Project::open(&gov_runtime::project::find_root(r).unwrap_or(r.to_path_buf())))
                        .filter(|p| p.is_installed())
                        .map(|p| gov_runtime::orchestration::gates::standalone_anchor_allowed(&p))
                        .unwrap_or_else(gov_runtime::human_channel::standalone_allowed_by_embedded_kernel);
                    match provision {
                        Some(f) => gov_runtime::human_channel::provision_standalone(Path::new(f), project_root.as_deref(), allowed),
                        None => gov_runtime::human_channel::status(allowed),
                    }
                }
                // P2-ADJ-0002 continuity under the owner's T2 binding authority (installed by `trust bind`)
                TrustCmd::Reseal { dry_run } => { let p = open_project(cli, true)?; gov_runtime::t2::reseal(&p, *dry_run) }
            }
        }
        Cmd::Contract { op } => {
            let repo = cli
                .root
                .clone()
                .or_else(gov_runtime::kernel::canonical_root)
                .or_else(|| std::env::current_dir().ok())
                .ok_or_else(|| GovError::new("USAGE", "no repository root"))?;
            match op {
                ContractCmd::Verify => gov_runtime::contracts::verify(&repo),
                ContractCmd::Compile => gov_runtime::contracts::generate(&repo),
                // P2-AR-0042 (BC-P2-02): the suite-to-contract matrix, from the map and the supplied run outputs
                ContractCmd::Matrix { lib_results, certification_results, heldout_results, health_results, out } => {
                    let paths = |v: &Vec<String>| v.iter().map(PathBuf::from).collect::<Vec<_>>();
                    let ev = gov_runtime::contracts::RunEvidence { lib: paths(lib_results), certification: paths(certification_results), heldout: paths(heldout_results), health: paths(health_results) };
                    match out {
                        Some(o) => gov_runtime::contracts::write_suite_to_contract(&repo, &ev, Path::new(o)),
                        None => gov_runtime::contracts::suite_to_contract(&repo, &ev).map(|(m, _)| m),
                    }
                }
            }
        }
        Cmd::Upstream { op } => { let p = open_project(cli, true)?; match op { UpstreamCmd::Prepare { lesson } => gov_runtime::upstream::prepare(&p, lesson), UpstreamCmd::Submit { packet, destination, approved_by } => gov_runtime::upstream::submit(&p, packet, destination, approved_by.as_deref()) } }
        Cmd::Task { op } => {
            let p = open_project(cli, true)?;
            use gov_runtime::orchestration::tasks as t;
            match op {
                TaskCmd::Create { class, objective, title, feature, deps, allowed, status, fields, id } => { let mut f = parse_json_arg(fields)?; if !f.is_object() { f = json!({}); } let o = f.as_object_mut().unwrap(); o.insert("objective".into(), json!(objective)); if let Some(c) = class { o.insert("class".into(), json!(c)); }
                    if let Some(x) = title { o.insert("title".into(), json!(x)); }
                    if let Some(x) = feature { o.insert("feature".into(), json!(x)); }
                    if deps.is_some() { o.insert("dependencies".into(), json!(csv(deps))); }
                    if allowed.is_some() { o.insert("allowed_paths".into(), json!(csv(allowed))); }
                    if let Some(s) = status { o.insert("task_status".into(), json!(s)); }
                    if let Some(i) = id { o.insert("id".into(), json!(i)); } t::create(&p, f) }
                TaskCmd::List { status } => Ok(json!(t::list(&p, status.as_deref()))),
                // R3-WS5-4: the record with its DAG evaluation, staleness and generation source (`tasks::show`)
                TaskCmd::Show { id } => t::show(&p, id),
                TaskCmd::Status { id, status, note } => t::set_status(&p, id, status, note.as_deref()),
                TaskCmd::Claim { id } => t::claim(&p, id),
                TaskCmd::Release { id, force } => Ok(json!({"released": t::release(&p, id, *force)?})),
                TaskCmd::Close { id, report, force } => { let d = db(&p)?; let r = load_file_value(report)?; t::close(&p, &d, id, r, *force) }
                TaskCmd::Dag => Ok(serde_json::to_value(gov_runtime::orchestration::dag::compute(&p)?)?),
                TaskCmd::Replan => gov_runtime::orchestration::dag::replan(&p),
                // WS-5 (P2-AR-0036, BC-P2-24) additive arm
                TaskCmd::Generate { dry_run } => gov_runtime::orchestration::generation::reconcile(&p, &gov_runtime::orchestration::generation::Options { trigger: "task generate".into(), dry_run: *dry_run }),
            }
        }
        Cmd::Cit { op } => {
            let p = open_project(cli, true)?;
            use gov_runtime::cit as c;
            match op {
                CitCmd::Propose { proposal, trigger, targets, manifest, title } => { let mut f = json!({"proposal": proposal}); if let Some(t) = trigger { f["trigger"] = json!(t); }
                    if targets.is_some() { f["targets"] = json!(csv(targets)); }
                    if let Some(m) = manifest { f["mutation_manifest"] = load_file_value(m)?; }
                    if let Some(t) = title { f["title"] = json!(t); } c::propose(&p, f) }
                CitCmd::Simulate { id } => { let d = db(&p)?; c::simulate(&p, &d, id) }
                CitCmd::Approve { id, by, method } => { cit_gate_precheck(&p, id)?; c::approve(&p, id, by.as_deref().unwrap_or(&acting), method) }
                CitCmd::Reject { id, by, reason } => c::reject(&p, id, by.as_deref().unwrap_or(&acting), reason.as_deref()),
                CitCmd::Execute { id } => { cit_gate_precheck(&p, id)?; let d = db(&p)?; c::execute(&p, &d, id) }
                CitCmd::Rollback { id, reason } => c::rollback(&p, id, reason.as_deref()),
                CitCmd::List => Ok(json!(c::list(&p))),
                CitCmd::Show { id } => { let s = gov_runtime::records::RecordStore::load(&p.root); s.get(id).map(|r| r.data.clone()).ok_or_else(|| GovError::new("CIT_NOT_FOUND", format!("{id} not found"))) }
                // WS-4 (P2-AR-0025) additive arms
                CitCmd::Classify { id, paths, base } => c::classify(&p, id.as_deref(), &csv(paths), base.as_deref()),
                CitCmd::Propagate { dry_run } => c::propagate_detected(&p, *dry_run),
            }
        }
        // WS-4 (P2-AR-0017): the context commands do not require the derived index — mandatory inputs are resolved
        // from governed records, and an absent or damaged index degrades only the supplementary block (W10).
        Cmd::Context { op } => {
            let p = open_project(cli, true)?;
            use gov_runtime::context as ctx;
            match op {
                ContextCmd::Compile { task } => ctx::compile_tolerant(&p, task),
                ContextCmd::Manifest { task } => { let s = gov_runtime::records::RecordStore::load(&p.root); Ok(ctx::manifest::resolve_task(&p, &s, task)?.to_value()) }
                ContextCmd::Verify { task, hash } => { let pk = ctx::load_packet(&p, task, hash.as_deref())?; ctx::verify_delivery(&p, &pk) }
                ContextCmd::Show { task, hash } => ctx::load_packet(&p, task, hash.as_deref()),
                ContextCmd::Receipt { task, file } => { let s = gov_runtime::records::RecordStore::load(&p.root); Ok(ctx::receipt::validate(&p, &s, task, &load_file_value(file)?)?.to_value()) }
                // WS-4 (P2-AR-0025) additive arm
                ContextCmd::Staleness { task } => { let s = gov_runtime::records::RecordStore::load(&p.root); gov_runtime::cit::propagation::task_staleness(&p, &s, task) }
            }
        }
        Cmd::Artefact { op } => {
            let p = open_project(cli, true)?;
            let s = gov_runtime::records::RecordStore::load(&p.root);
            match op {
                ArtefactCmd::Show { id } => gov_runtime::graph::identity::identity(&p, &s, id),
                ArtefactCmd::Check => Ok(gov_runtime::graph::identity::check(&p, &s)),
                ArtefactCmd::Lineage { id, direction, depth } => {
                    let d = db(&p)?;
                    let seeds = vec![id.clone()];
                    let reach = match direction.as_str() { "up" | "upstream" | "reverse" => gov_runtime::graph::upstream_set(&d, &seeds, *depth)?, "down" | "downstream" | "forward" | "impact" => gov_runtime::graph::impact_set(&d, &seeds, *depth)?, other => return Err(GovError::new("USAGE", format!("--direction must be up or down (got '{other}')"))) };
                    Ok(json!({"id": id, "direction": direction, "depth": depth, "reach": reach, "edges": gov_runtime::graph::canonical_edges(&d, id)?}))
                }
            }
        }
        Cmd::Checkpoint { op } => {
            let p = open_project(cli, true)?; let d = db(&p)?;
            match op {
                CheckpointCmd::Create { next_action, task, trigger, step, tests_status } => gov_runtime::checkpoints::create(&p, &d, json!({"next_action": next_action, "task": task, "trigger": trigger, "last_completed_step": step, "tests_status": tests_status})),
                CheckpointCmd::Latest => Ok(gov_runtime::checkpoints::latest(&p).unwrap_or(Value::Null)),
                CheckpointCmd::Watchdog { utilisation, ops, task, next_action } => gov_runtime::checkpoints::watchdog(&p, &d, *utilisation, *ops, task.as_deref(), next_action),
                // WS-4 (P2-AR-0025) additive arm
                CheckpointCmd::Freshness { id } => gov_runtime::checkpoints::freshness(&p, id.as_deref()),
            }
        }
        // WS-4 (P2-AR-0025, BC-P2-05) additive arm
        Cmd::Session { op } => {
            let p = open_project(cli, true)?; let d = db(&p)?;
            match op {
                SessionCmd::Close { next_action, task } => gov_runtime::checkpoints::session_close(&p, &d, next_action, task.as_deref()),
            }
        }
        Cmd::Skills { op } => { let p = open_project(cli, true)?; match op { SkillsCmd::List => Ok(json!(gov_runtime::skills::list_skills(&p))), SkillsCmd::Resolve { task } => { let s = gov_runtime::records::RecordStore::load(&p.root); let t = s.get(task).map(|r| r.data.clone()).ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("{task} not found")))?; gov_runtime::skills::resolve(&p, &t) } } }
        Cmd::Tools { op } => {
            let p = open_project(cli, true)?;
            match op {
                ToolsCmd::List => { let mut t = gov_runtime::tools::kernel_tools(&p); t.extend(gov_runtime::tools::project_tools(&p)); Ok(json!({"tools": t, "mcp_servers": gov_runtime::tools::mcp_servers(&p)})) }
                ToolsCmd::Registry => gov_runtime::tools::generate_registry(&p),
                ToolsCmd::Resolve { role, capability } => gov_runtime::tools::resolve(&p, role.as_deref().unwrap_or(&p.role), capability),
                // BC-P2-08: the conditions are evaluated for the acting role (`declared_role` reconciled any `--role` here)
                ToolsCmd::Install { descriptor, role: _, execute } => { let d = load_file_value(descriptor)?; gov_runtime::tools::install(&p, d, &p.role, *execute) }
                ToolsCmd::Health => Ok(json!(gov_runtime::tools::health(&p))),
            }
        }
        Cmd::Handoff { op } => { let p = open_project(cli, true)?; match op { HandoffCmd::Create { to_role, task, fields } => { let mut f = parse_json_arg(fields)?; if !f.is_object() { f = json!({}); } f["to_role"] = json!(to_role); f["task"] = json!(task); gov_runtime::orchestration::handoffs::create(&p, f) } HandoffCmd::Return { id, file } => gov_runtime::orchestration::handoffs::return_result(&p, id, load_file_value(file)?) } }
        Cmd::Memory { op } => {
            let p = open_project(cli, true)?;
            match op {
                MemoryCmd::Query { query, k, route, include_historical } => { let d = db(&p)?; let r = gov_runtime::retrieval::retrieve(&p, &d, query, gov_runtime::retrieval::RetrieveOptions { k: *k, route: route.clone(), include_historical: *include_historical, log: true, ..Default::default() })?; gov_runtime::observability::emit(&p, "retrieval", json!({"routes": r.routes, "hits": r.hits.len(), "latency_ms": r.latency_ms}))?; Ok(serde_json::to_value(&r)?) }
                MemoryCmd::Verify => { let d = db(&p)?; let hp = p.root.join(p.policies().get_str("MEMORY_POLICY", "regression.heldout_file", "governance/tests/memory/heldout.yaml")); let held = gov_runtime::util::read_yaml(&hp)?; let r = gov_runtime::retrieval::run_heldout(&p, &d, &held)?; if r["measured"].as_bool().unwrap_or(false) && !r["pass"].as_bool().unwrap_or(false) { return Err(GovError::new("VERIFICATION_FAILED", "held-out memory regression failed").with_details(r)); } Ok(r) }
                MemoryCmd::Benchmark { candidates, heldout, record, task } => gov_runtime::memory::benchmark::run_for(&p, candidates, heldout.clone(), *record, task.as_deref()),
                MemoryCmd::Select { candidate, research, by, gate } => gov_runtime::memory::benchmark::select(&p, candidate, research.as_deref(), gate.as_deref(), by.as_deref().unwrap_or(&acting)),
                MemoryCmd::Integrity => { let d = db(&p).ok(); let store = gov_runtime::records::RecordStore::load(&p.root); Ok(serde_json::to_value(gov_runtime::memory::integrity::check(&p, &store, d.as_ref())?)?) }
                MemoryCmd::Profile => { let mut v = gov_runtime::memory::profile::status(&p); v["live_index"] = db(&p).ok().map(|d| json!({"embedder": d.get_meta("embedder"), "reranker": d.get_meta("reranker"), "components": {"embedder": d.get_meta("embedder_identity"), "reranker": d.get_meta("reranker_identity")}})).unwrap_or(Value::Null); Ok(v) }
                MemoryCmd::HeldoutStarter { force } => { let d = db(&p)?; let hp = p.root.join(p.policies().get_str("MEMORY_POLICY", "regression.heldout_file", "governance/tests/memory/heldout.yaml")); let existing = gov_runtime::util::read_yaml(&hp).ok().and_then(|h| h["queries"].as_array().map(|a| a.len())).unwrap_or(0); if existing > 0 && !force { return Err(GovError::new("USAGE", format!("{} already has {existing} queries (use --force to overwrite)", hp.display()))); } let set = gov_runtime::memory::heldout::generate_starter(&p, &d, "gov memory heldout-starter")?; gov_runtime::util::write_yaml(&hp, &set)?; Ok(json!({"path": hp.display().to_string(), "queries": set["queries"].as_array().map(|a| a.len()).unwrap_or(0)})) }
                MemoryCmd::Miss { query, expected, detail } => {
                    // WS-6 IP-6: an agent-reported miss; the write passes guard_write inside `failures::record`, and a
                    // refused write is reported typed rather than as success
                    let ev = gov_runtime::memory::failures::retrieval_miss_event(query, expected, json!({"detail": detail}), vec!["reported by an agent (to be root-caused: chunking / metadata / routing / graph / lexical / stale index / knowledge gap)".into()], "memory miss", "reported");
                    let o = gov_runtime::memory::failures::record(&p, ev, false);
                    if o.status == "not_recorded" {
                        return Err(GovError::new("FAILURE_NOT_RECORDED", format!("the retrieval miss was not recorded: {}", o.reason.clone().unwrap_or_default())).with_details(o.to_value()));
                    }
                    Ok(o.to_value())
                }
                MemoryCmd::Failures => Ok(json!({"open": gov_runtime::memory::failures::open_failures(&p)})),
                MemoryCmd::Freshness => Ok(serde_json::to_value(gov_runtime::memory::manifest::freshness(&p))?),
                MemoryCmd::Rebuild { incremental } => Ok(serde_json::to_value(gov_runtime::memory::indexer::rebuild(&p, gov_runtime::memory::indexer::IndexOptions { incremental: *incremental, observe_boundaries: true, ..Default::default() })?)?),
                MemoryCmd::Graph { node, depth } => { let d = db(&p)?; Ok(json!(gov_runtime::graph::neighbours(&d, node, *depth)?)) }
                MemoryCmd::Impact { seeds, depth } => { let d = db(&p)?; Ok(json!(gov_runtime::graph::impact_set(&d, &csv(&Some(seeds.clone())), *depth)?)) }
            }
        }
        Cmd::Gate { op } => { let p = open_project(cli, true)?; match op { GateCmd::Create { question, fields } => { let mut f = parse_json_arg(fields)?; if !f.is_object() { f = json!({}); } f["question"] = json!(question); gov_runtime::orchestration::gates::create(&p, f) } GateCmd::Present { id, receipt_file, receipt_inbox } => { let (d, text) = gov_runtime::orchestration::gates::present(&p, id)?; if !cli.json { println!("{text}"); } let mut out = json!({"gate": d, "chat_text": text}); if receipt_file.is_some() || *receipt_inbox { out["receipt"] = gov_runtime::orchestration::gates::acknowledge(&p, id, receipt_file.as_deref())?; } Ok(out) } GateCmd::Revoke { id, reason } => gov_runtime::orchestration::gates::revoke(&p, id, reason.as_deref()), GateCmd::List => { let mut v = gov_runtime::orchestration::gates::pending(&p); v.extend(gov_runtime::orchestration::gates::unverified(&p)); Ok(json!(v)) } GateCmd::Show { id } => gov_runtime::orchestration::gates::inspect(&p, id) } }
        Cmd::Readiness { op } => { let p = open_project(cli, true)?; match op { ReadinessCmd::Check { feature } => Ok(serde_json::to_value(gov_runtime::orchestration::readiness::check(&p, feature)?)?), ReadinessCmd::Plan { feature } => { gov_runtime::authority::require(&p, "readiness_plan")?; gov_runtime::orchestration::readiness::plan(&p, feature) } } }
        Cmd::Intent { text } => { let p = open_project(cli, true)?; gov_runtime::orchestration::intents::route(&p, text) }
        Cmd::Route { task, class, radius, record, report } => { let p = open_project(cli, true)?; if *report { return gov_runtime::routing::report(&p); }
            if let Some(r) = record { return gov_runtime::routing::record(&p, load_file_value(r)?); } let t = task.as_ref().and_then(|id| gov_runtime::records::RecordStore::load(&p.root).get(id).map(|r| r.data.clone())); gov_runtime::routing::route(&p, t.as_ref(), class.as_deref(), None, radius.as_deref()) }
        Cmd::Telemetry { op } => { let p = open_project(cli, true)?; match op { TelemetryCmd::Summary => gov_runtime::observability::summary(&p), TelemetryCmd::Emit { name, attrs } => gov_runtime::observability::emit(&p, name, parse_json_arg(attrs)?) } }
        Cmd::Adapters { op } => { let p = open_project(cli, true)?; match op { AdaptersCmd::Generate => gov_runtime::adapters::generate(&p), AdaptersCmd::Verify => { let v = gov_runtime::adapters::verify(&p)?; if !v["ok"].as_bool().unwrap_or(false) { return Err(GovError::new("VERIFICATION_FAILED", "adapter conformance failed").with_details(v)); } Ok(v) } } }
        Cmd::Release { op } => match op {
            ReleaseCmd::Build { version, out, certification, evidence, canonical } => { let croot = canonical.clone().or_else(gov_runtime::kernel::canonical_root).ok_or_else(|| GovError::new("KERNEL_SOURCE_NOT_FOUND", "canonical repository root not found (pass --canonical)"))?; let out = out.clone().unwrap_or(croot.join("release")); gov_runtime::release::build(&croot, version, &out, certification, evidence.as_deref()) }
            ReleaseCmd::Verify { dir } => gov_runtime::release::verify(dir),
            // product-release records (IP-R3-WS03-5 / IP-R3-WS08-8 / IP-R3-WS04-07): WS-8's writer, WS-4's record type,
            // WS-3's G0 class (`release record`: Write / `record_release`)
            ReleaseCmd::Record { version, title, derived_from, validated_by, notes } => {
                let p = open_project(cli, true)?;
                gov_runtime::release::record_product_release(&p, &gov_runtime::release::ProductRelease { version: version.clone(), title: title.clone(), derived_from: derived_from.clone(), validated_by: validated_by.clone(), notes: notes.clone() })
            }
        },
        Cmd::Kernel { op } => { let mut p = open_project(cli, true)?; match op { KernelCmd::Verify => { let v = serde_json::to_value(gov_runtime::kernel::verify_kernel(&p.kernel_dir())?)?; let t = gov_runtime::kernel_trust::trust(&p.root); Ok(json!({"ok": v["ok"], "modified": v["modified"], "missing": v["missing"], "added": v["added"], "payload_hash": v["payload_hash"], "version": v["version"], "trust": t.to_value()})) }
            KernelCmd::Trust => { let t = gov_runtime::kernel_trust::trust(&p.root); Ok(json!({"verified": t.verified, "summary": t.summary(), "trust": t.to_value()})) }
            KernelCmd::Override { reason } => gov_runtime::kernel_trust::request_override(&p, reason.as_deref()), KernelCmd::Reinstall { source, break_glass } => {
                gov_runtime::orchestration::control::guard_write(&p, "kernel reinstall")?;
                gov_runtime::authority::require(&p, "install_kernel")?;
                let lock = p.lock()?.clone();
                // Privileged lifecycle ingress `reinstall`: the one verification policy (ARCH-0003 §3.6).
                let src = gov_runtime::kernel::resolve_kernel_source(source.as_deref().map(Path::new).or_else(|| lock["source"].as_str().filter(|s| Path::new(s).exists()).map(Path::new)))?;
                // BC-P2-38 (WS-8 IP-3): bind the request to the pinned payload, so a candidate that is not the pinned
                // release is refused right after measurement — before any floor, break-glass entry or owner
                // authorisation is consumed. The pin is bound only when it is unambiguous: framework.lock agrees with
                // this machine's protected record of what it committed into the project (BC-P2-35), or no such record
                // exists. When they disagree (a pin rewritten together with the kernel, or another machine's update
                // pulled in), the precise check inside `kernel::install_kernel` decides before anything moves
                // (KERNEL_PIN_REWRITTEN naming the values to restore, or the lock-pinned release admitted).
                let lock_pin = lock["release_hash"].as_str().map(String::from);
                let recorded_pin = gov_runtime::srr::installation::project_record(&p.root)
                    .and_then(|r| r.current)
                    .map(|c| c.payload_hash);
                let pin = match (&lock_pin, &recorded_pin) {
                    (Some(l), Some(r)) if l != r => None,
                    _ => lock_pin.clone(),
                };
                let auth = gov_runtime::srr::admit(
                    gov_runtime::srr::AdmissionRequest::new(gov_runtime::srr::Ingress::Reinstall, &src)
                        .with_pinned_payload(pin)
                        .with_break_glass(*break_glass)
                        .with_reason(Some("gov kernel reinstall".into())),
                )?;
                let m = gov_runtime::kernel::install_kernel(&auth, &p.governance_dir())?;
                if m["payload_hash"] != lock["release_hash"] { return Err(GovError::new("KERNEL_MISMATCH", "reinstalled payload hash differs from framework.lock release_hash; use gov update for a version change")); }
                p.invalidate();
                let protected = gov_runtime::srr::record_installed(&auth)?;
                Ok(json!({"reinstalled": true, "version": m["version"], "payload_hash": m["payload_hash"], "release_authenticity": auth.to_value(), "protected_state": protected}))
            } } }
        Cmd::Capabilities { op: CapCmd::ServeEmbed { reverse, id } } => {
            use std::io::Read; let mut raw = String::new(); std::io::stdin().read_to_string(&mut raw)?;
            let req: Value = serde_json::from_str(&raw).unwrap_or(json!({}));
            let resp = if req["protocol"] != "gov-capability/1" { json!({"protocol": "gov-capability/1", "ok": false, "provider": {"id": id, "version": "1"}, "error": {"code": "PROTOCOL_MISMATCH", "message": "expected gov-capability/1"}}) } else {
                let dim = req["inputs"]["dimensions"].as_u64().unwrap_or(512).max(8) as usize;
                let e = gov_runtime::memory::embeddings::HashedNgramEmbedder::new(dim, "1");
                let vecs: Vec<Vec<f64>> = req["inputs"]["texts"].as_array().cloned().unwrap_or_default().iter().map(|t| { let mut v = e.embed(t.as_str().unwrap_or("")); if *reverse { v.reverse(); } v }).collect();
                json!({"protocol": "gov-capability/1", "ok": true, "provider": {"id": id, "version": "1"}, "outputs": {"vectors": vecs, "dim": dim}}) };
            println!("{}", serde_json::to_string(&resp)?);
            std::process::exit(0);
        }
        Cmd::Capabilities { op } => { let p = open_project(cli, false)?; match op { CapCmd::ServeEmbed { .. } => unreachable!(), CapCmd::Ecosystems => Ok(gov_runtime::capabilities::ecosystems::detect(&p.root, &["product/".into()])),
            CapCmd::Plugins => { let set = gov_runtime::capabilities::governance::plugin_set(&p); let mut rows: Vec<Value> = set.usable.iter().map(|d| { let mut v = serde_json::to_value(d).unwrap_or(json!({})); v["status"] = json!("usable"); v["acting_role"] = json!(p.role); v }).collect(); for d in &set.denied { rows.push(json!({"plugin_id": d["plugin_id"], "capability": d["capability"], "version": d["version"], "source": d["source"], "status": "denied", "code": d["code"], "reason": d["reason"], "acting_role": p.role})); } for r in &set.rejected { rows.push(json!({"plugin_id": r["plugin_id"], "source": r["source"], "status": "rejected", "code": "PLUGIN_DESCRIPTOR_INVALID", "reason": r["reason"], "acting_role": p.role})); } Ok(json!(rows)) }
            CapCmd::Invoke { plugin, inputs } => {
                // no executable capability runs merely because a descriptor exists (verifier H-N2)
                gov_runtime::authority::require(&p, "execute_plugin")?;
                let set = gov_runtime::capabilities::governance::plugin_set(&p);
                let d = match set.usable.iter().find(|x| x.plugin_id == *plugin).cloned() { Some(d) => d, None => return Err(set.refusal(plugin).unwrap_or_else(|| GovError::new("PLUGIN_NOT_FOUND", format!("plugin {plugin} not declared")))) };
                let out = gov_runtime::capabilities::host::invoke(&d, &p.root, parse_json_arg(&Some(inputs.clone()))?, gov_runtime::capabilities::governance::invoke_timeout(&p))?; Ok(serde_json::to_value(&out)?) } } }
        Cmd::Plugins { op } => { let p = open_project(cli, true)?; match op {
            PluginsCmd::Register { descriptor } => gov_runtime::capabilities::governance::register(&p, load_file_value(descriptor)?),
            PluginsCmd::List => { let set = gov_runtime::capabilities::governance::plugin_set(&p); Ok(json!({"role": p.role, "usable": set.usable, "denied": set.denied, "rejected": set.rejected})) }
            PluginsCmd::Unregister { plugin_id } => gov_runtime::capabilities::governance::unregister(&p, plugin_id),
            // WS-7 r2 IP-W7-4: every entry with its T2 binding and whether it is honoured, and the document's binding
            PluginsCmd::Registry => Ok(gov_runtime::capabilities::registry::report(&p)),
            PluginsCmd::Health { ping } => Ok(json!(gov_runtime::capabilities::governance::health(&p, *ping))) } }
        Cmd::Policy { op } => { let p = open_project(cli, true)?; let pol = p.policies(); match op {
            PolicyCmd::Overrides => Ok(json!({"applied": pol.applied_overrides, "refused": pol.refused_overrides, "precedence": pol.precedence, "kernel_trust": pol.kernel_trust, "problems": pol.problems})),
            PolicyCmd::Effective { policy } => Ok(json!({"policy": policy, "effective": pol.effective.get(policy), "kernel": pol.raw.get(policy)})) } }
        Cmd::Claims { op } => { let p = open_project(cli, true)?; match op { ClaimsCmd::List => Ok(json!(gov_runtime::orchestration::claims::list(&p)?)), ClaimsCmd::Sweep => { gov_runtime::authority::require(&p, "sweep_claims")?; Ok(json!({"swept": gov_runtime::orchestration::claims::sweep_expired(&p)?})) } } }
        Cmd::Lessons { op } => match op { LessonsCmd::Cluster { inbox, proposals, write } => {
            let root = cli.root.clone().or_else(gov_runtime::kernel::canonical_root).unwrap_or(std::env::current_dir()?);
            let inbox = inbox.clone().unwrap_or(root.join("lessons").join("inbox"));
            let proposals = proposals.clone().unwrap_or(root.join("change-proposals"));
            let policy = gov_runtime::util::read_yaml(&root.join("framework/policies/LEARNING_POLICY.yaml")).or_else(|_| gov_runtime::util::read_yaml(&root.join("governance/kernel/policies/LEARNING_POLICY.yaml")))?;
            gov_runtime::lessons::cluster(&inbox, &proposals, &policy, *write)
        } },
        Cmd::Health { op } => health_cmd(cli, op), // WS-2 additive arm
        Cmd::Oracle { op } => match op {
            OracleCmd::Format => gov_runtime::qualification_oracle::format_definition(),
            OracleCmd::Validate {
                file,
                oracle,
                public_suite,
                repository,
            } => gov_runtime::qualification_oracle::validate_file(
                file,
                &gov_runtime::qualification_oracle::ValidateOptions {
                    oracle: oracle.clone(),
                    public_suites: public_suite.clone(),
                    repositories: repository.clone(),
                },
            ),
        },
        Cmd::Research { .. } | Cmd::Experiment { .. } | Cmd::Data { .. } | Cmd::Scenario { .. } => lifecycle_cmd(cli), // WS-10 additive arm
        Cmd::Mcp { .. } => Err(GovError::new("MCP_NOT_IMPLEMENTED", "the repository-intelligence MCP server (MCP-REPO-001) is registered as planned; this release exposes the same operations through the CLI JSON contract (API-0002)")),
    }.inspect(|_v| { let _ = name; })
}

fn run_audit(p: &Project, deep: bool, families: Vec<String>, persist: bool) -> Result<Value> {
    let r = gov_runtime::verification::audit(
        p,
        &gov_runtime::verification::SuiteOptions { deep, families },
        persist,
    )?;
    gov_runtime::observability::emit(
        p,
        "audit",
        json!({"verdict": r["verdict"], "audit": r["audit"]}),
    )?;
    if r["verdict"] == "UNHEALTHY" {
        return Err(GovError::new(
            "UNHEALTHY",
            format!(
                "governance suite UNHEALTHY: {} critical, {} high",
                r["counts"]["critical"], r["counts"]["high"]
            ),
        )
        .with_details(r));
    }
    Ok(r)
}

fn command_name(c: &Cmd) -> &'static str {
    match c {
        Cmd::Version => "version",
        Cmd::Init { .. } => "init",
        Cmd::Status => "status",
        Cmd::Continue { .. } => "continue",
        Cmd::Decide { .. } => "decide",
        Cmd::Audit { .. } => "audit",
        Cmd::Pause { .. } => "pause",
        Cmd::FreezeWrites { .. } => "freeze-writes",
        Cmd::CancelAgents { .. } => "cancel-agents",
        Cmd::Resume => "resume",
        Cmd::Doctor => "doctor",
        Cmd::RebuildMemory { .. } => "rebuild-memory",
        Cmd::Recover { .. } => "recover",
        Cmd::Adopt { .. } => "adopt",
        Cmd::Migrate { .. } => "migrate",
        Cmd::Update { .. } => "update",
        Cmd::Trust { .. } => "trust",
        Cmd::Contract { .. } => "contract",
        Cmd::Upstream { .. } => "upstream",
        Cmd::Task { .. } => "task",
        Cmd::Cit { .. } => "cit",
        Cmd::Context { .. } => "context",
        Cmd::Checkpoint { .. } => "checkpoint",
        Cmd::Skills { .. } => "skills",
        Cmd::Tools { .. } => "tools",
        Cmd::Handoff { .. } => "handoff",
        Cmd::Memory { .. } => "memory",
        Cmd::Gate { .. } => "gate",
        Cmd::Readiness { .. } => "readiness",
        Cmd::Intent { .. } => "intent",
        Cmd::Route { .. } => "route",
        Cmd::Telemetry { .. } => "telemetry",
        Cmd::Adapters { .. } => "adapters",
        Cmd::Release { .. } => "release",
        Cmd::Kernel { .. } => "kernel",
        Cmd::Capabilities { .. } => "capabilities",
        Cmd::Claims { .. } => "claims",
        Cmd::Verify { .. } => "verify",
        Cmd::Mcp { .. } => "mcp",
        Cmd::Lessons { .. } => "lessons",
        Cmd::Plugins { .. } => "plugins",
        Cmd::Policy { .. } => "policy",
        Cmd::Artefact { .. } => "artefact",
        Cmd::Health { .. } => "health", // WS-2 additive arm
        Cmd::Oracle { .. } => "oracle",
        Cmd::Session { .. } => "session", // WS-4 additive arm
        // WS-10 (P2-AR-0031) additive arms
        Cmd::Research { .. } => "research",
        Cmd::Experiment { .. } => "experiment",
        Cmd::Data { .. } => "data",
        Cmd::Scenario { .. } => "scenario",
    }
}

fn main() {
    let cli = Cli::parse();
    let name = command_name(&cli.cmd);
    let session = cli
        .session
        .clone()
        .or(std::env::var("GOV_SESSION").ok())
        .unwrap_or_default();
    let started = std::time::Instant::now();
    let result = run(&cli);
    // WS-5 (P2-AR-0036, BC-P2-24) additive block — **governed work generated when the event occurs.** After a
    // governed write command (its G0 class), the work its recorded events call for (failed tests, findings, health
    // failures, discoveries, human decisions, CIT effects, lessons, missing tools/skills, failures, performance
    // regressions) is generated into the task DAG, linked and idempotent (`orchestration::generation::after_command`).
    // It runs whether the command succeeded or failed (a failing run may have recorded its event) but not after a
    // refusal before dispatch, and not after any refusal of the guard (round-3 integration review, R3-WS5-1: the
    // write guard's kernel-trust, below-floor and emergency-control refusals and the availability rule's
    // `HEALTH_HARD_BLOCK` — a refused command recorded no event, and its refusal is not work to generate); it never
    // changes the command's result.
    if !matches!(
        result.as_ref().err().map(|e| e.code.as_str()),
        Some(
            "G0_UNCLASSIFIED"
                | "AUTHORITY_DENIED"
                | "FROZEN"
                | "PAUSED"
                | "USAGE"
                | "ROLE_UNDECLARED"
                | "HEALTH_HARD_BLOCK"
                | "KERNEL_TAMPERED"
                | "KERNEL_UNANCHORED"
                | "SRR_BELOW_FLOOR_REFUSED"
                | "SRR_BELOW_FLOOR_SUBJECT_UNDETERMINED"
        )
    ) {
        if let Ok(p) = open_project(&cli, true) {
            let _ = gov_runtime::orchestration::generation::after_command(&p, &g0_label(&cli.cmd));
        }
    }
    // telemetry span for every command when a project is available
    if let Ok(p) = open_project(&cli, true) {
        let _ = gov_runtime::observability::emit(
            &p,
            &format!("cli.{name}"),
            json!({"ok": result.is_ok(), "duration_ms": started.elapsed().as_millis() as u64, "error": result.as_ref().err().map(|e| e.code.clone())}),
        );
    }
    // **`OWNER-DECISION-0006` §6 bullet 7 — the one place a command result leaves this product** (`AR31-B1`).
    //
    // Repair 2 recorded bullet 7 as "no primitive: every reporting surface carries the marking". That was a list,
    // and AR-0031 showed the list was short: `gov doctor`, `gov update --check`, `gov version` and the agent
    // context packet all reported the installed release with no marking beside it, and nothing was ever refused
    // under bullet 7 because the effect had no call site.
    //
    // A longer list would fail the same way. `run()` is called exactly once and its value reaches stdout only
    // through the match below, so attaching the presentation to the envelope here covers **every command,
    // including ones that do not exist yet and ones that have never heard of break-glass**. That is measured by
    // the certification suite, which drives a command with no relationship to release identity on a marked
    // machine and asserts the marking is present.
    //
    // `srr::present::attach` is the sink: it asks `breakglass::guard_effect` for
    // `Effect::PresentBelowFloorReleaseAsCurrent` and reports the refusal instead of swallowing it. §5 keeps
    // inspection and diagnosis available below floor, so the enforcement is in what is said, not in refusing to
    // speak.
    let mark = |v: Value| {
        let mut v = v;
        gov_runtime::srr::present::attach(name, &mut v);
        v
    };
    match result {
        Ok(v) => {
            if cli.json {
                println!(
                    "{}",
                    serde_json::to_string_pretty(&mark(
                        json!({"ok": true, "command": name, "result": v, "session": session})
                    ))
                    .unwrap()
                );
            } else {
                let banner = mark(json!({}));
                if banner["release_trust"]["below_floor"]
                    .as_bool()
                    .unwrap_or(true)
                {
                    println!(
                        "{}: {}",
                        banner["release_trust"]["marking"].as_str().unwrap_or(""),
                        banner["release_trust"]["operator_note"]
                            .as_str()
                            .unwrap_or("")
                    );
                }
                print!(
                    "{}",
                    serde_yaml::to_string(&v).unwrap_or_else(|_| v.to_string())
                );
            }
        }
        Err(e) => {
            if cli.json {
                println!("{}", serde_json::to_string_pretty(&mark(json!({"ok": false, "command": name, "error": {"code": e.code, "message": e.message, "details": e.details}, "session": session}))).unwrap());
            } else {
                let banner = mark(json!({}));
                if banner["release_trust"]["below_floor"]
                    .as_bool()
                    .unwrap_or(true)
                {
                    eprintln!(
                        "{}: {}",
                        banner["release_trust"]["marking"].as_str().unwrap_or(""),
                        banner["release_trust"]["operator_note"]
                            .as_str()
                            .unwrap_or("")
                    );
                }
                eprintln!("error [{}]: {}", e.code, e.message);
                if !e.details.is_null() {
                    eprintln!("{}", serde_yaml::to_string(&e.details).unwrap_or_default());
                }
            }
            std::process::exit(e.exit_code());
        }
    }
}
