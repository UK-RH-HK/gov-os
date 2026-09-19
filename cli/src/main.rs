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
    /// Acting role (default: $GOV_ROLE or orchestrator)
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
    /// Answer a Human Decision Gate
    Decide {
        gate: String,
        #[arg(long)]
        option: String,
        #[arg(long, default_value = "human")]
        by: String,
        #[arg(long)]
        rationale: Option<String>,
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
        #[arg(long, default_value = "human")]
        by: String,
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
    // ---- WS-2 (P2-AR-0015) additive block: Governance Health Scheduler (Gate O5), product tests, skill regression
    /// Governance Health Scheduler: tiered runs, health state, checks, history, G0 guard, currency, product tests, skills
    Health {
        #[command(subcommand)]
        op: HealthCmd,
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
        #[arg(long, default_value = "migration-reviewer")]
        reviewer_role: String,
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
        #[arg(long, default_value = "migration-verifier")]
        verifier_role: String,
    },
    ExtractLegacy,
    BuildMemory,
    VerifyMemory {
        #[arg(long)]
        verdict: Option<String>,
        #[arg(long, default_value = "memory-verifier")]
        verifier_role: String,
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
        #[arg(long, default_value = "human")]
        by: String,
        #[arg(long, default_value = "human")]
        method: String,
    },
    Reject {
        id: String,
        #[arg(long, default_value = "human")]
        by: String,
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
}
#[derive(Subcommand)]
enum ContextCmd {
    Compile { task: String },
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
    },
    /// Pin a benchmarked candidate through a decision record and a full rebuild
    Select {
        candidate: String,
        #[arg(long)]
        research: Option<String>,
        #[arg(long, default_value = "human")]
        by: String,
    },
    /// Generate a starter held-out set from the live index (only when the file has no queries)
    HeldoutStarter {
        #[arg(long)]
        force: bool,
    },
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
    },
    List,
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
    let p = Project::open(&root).with_session(cli.session.clone(), cli.role.clone());
    if need_install {
        p.require_installed()?;
    }
    Ok(p)
}
fn db(p: &Project) -> Result<RuntimeDb> {
    let d = RuntimeDb::open(&p.db_path())?;
    d.init_schema()?;
    Ok(d)
}

fn run(cli: &Cli) -> Result<Value> {
    let name = command_name(&cli.cmd);
    match &cli.cmd {
        Cmd::Version => Ok(json!({"framework": gov_runtime::FRAMEWORK_NAME, "version": gov_runtime::VERSION, "cli_version": gov_runtime::CLI_VERSION, "runtime_version": gov_runtime::RUNTIME_VERSION, "index_version": gov_runtime::INDEX_VERSION})),
        Cmd::Init { source, name: pname, alias, intent, force, skip_index, channel, break_glass } => {
            let root = cli.root.clone().unwrap_or(std::env::current_dir()?);
            let pn = pname.clone().unwrap_or_else(|| root.file_name().map(|f| f.to_string_lossy().to_string()).unwrap_or("project".into()));
            let al = alias.clone().unwrap_or_else(|| format!("project-{}", &gov_runtime::util::sha256_text(&pn)[..6]));
            gov_runtime::init::init(&root, gov_runtime::init::InitOptions { source: source.clone(), project_name: pn, alias: al, mode: "init".into(), force: *force, intent: intent.clone(), skip_index: *skip_index, channel: channel.clone(), break_glass: *break_glass })
        }
        Cmd::Status => { let p = open_project(cli, true)?; gov_runtime::status::status(&p) }
        Cmd::Continue { claim } => { let p = open_project(cli, true)?; let d = db(&p)?; gov_runtime::status::continue_work(&p, &d, *claim) }
        Cmd::Decide { gate, option, by, rationale } => { let p = open_project(cli, true)?; gov_runtime::orchestration::gates::answer(&p, gate, option, by, rationale.as_deref()) }
        Cmd::Audit { deep, family, no_persist } => { let p = open_project(cli, true)?; run_audit(&p, *deep, family.clone(), !no_persist) }
        Cmd::Verify { what } => { let p = open_project(cli, true)?; if what == "governance" { run_audit(&p, false, vec![], true) } else { gov_runtime::verification::product_suite(&p) } }
        Cmd::Pause { reason } => { let p = open_project(cli, true)?; gov_runtime::orchestration::control::set(&p, "PAUSE", reason.as_deref()) }
        Cmd::FreezeWrites { reason } => { let p = open_project(cli, true)?; gov_runtime::orchestration::control::set(&p, "FREEZE_WRITES", reason.as_deref()) }
        Cmd::CancelAgents { reason } => { let p = open_project(cli, true)?; gov_runtime::orchestration::control::set(&p, "CANCEL_AGENTS", reason.as_deref()) }
        Cmd::Resume => { let p = open_project(cli, true)?; gov_runtime::orchestration::control::set(&p, "RESUME", None) }
        Cmd::Doctor => { let p = open_project(cli, false)?; let r = gov_runtime::doctor::run(&p)?; let v = serde_json::to_value(&r)?; if r.verdict == "UNHEALTHY" { return Err(GovError::new("UNHEALTHY", format!("doctor: UNHEALTHY ({} failed checks)", r.failed)).with_details(v)); } Ok(v) }
        Cmd::RebuildMemory { incremental } => { let p = open_project(cli, true)?; let r = gov_runtime::memory::indexer::rebuild(&p, gov_runtime::memory::indexer::IndexOptions { incremental: *incremental, ..Default::default() })?; Ok(serde_json::to_value(&r)?) }
        Cmd::Recover { dry_run } => { let p = open_project(cli, true)?; if !*dry_run { gov_runtime::authority::require(&p, "recover")?; } gov_runtime::recovery::recover(&p, *dry_run) }
        Cmd::Adopt { stage } | Cmd::Migrate { stage } => {
            let root = cli.root.clone().unwrap_or(std::env::current_dir()?);
            let session = cli.session.clone().or(std::env::var("GOV_SESSION").ok()).unwrap_or_else(gov_runtime::util::new_session_id);
            use gov_runtime::adopt as a;
            match stage {
                AdoptCmd::Baseline => a::a0_baseline(&root, &session), AdoptCmd::Inventory => a::a1_inventory(&root), AdoptCmd::Classify => a::a2_classify(&root), AdoptCmd::Map => a::a3_map(&root), AdoptCmd::Plan => a::a4_plan(&root), AdoptCmd::TestDesign => a::a5_test_design(&root),
                AdoptCmd::Review { verdict, reviewer_session, reviewer_role, notes } => a::a5_review(&root, verdict, reviewer_session.as_deref().unwrap_or(&session), reviewer_role, notes.as_deref()),
                AdoptCmd::Migrate { batch, source, gate_answer, name: pn, alias } => { let pn2 = pn.clone().unwrap_or_else(|| root.file_name().map(|f| f.to_string_lossy().to_string()).unwrap_or("project".into())); let al = alias.clone().unwrap_or_else(|| format!("project-{}", &gov_runtime::util::sha256_text(&pn2)[..6])); a::a6_migrate(&root, *batch, source.as_deref(), gate_answer, &pn2, &al, &session) }
                AdoptCmd::VerifyMigration { verdict, verifier_role } => a::a7_verify_migration(&root, verdict.as_deref(), &session, verifier_role),
                AdoptCmd::ExtractLegacy => a::a8_extract_legacy(&root), AdoptCmd::BuildMemory => a::a9_build_memory(&root, &session),
                AdoptCmd::VerifyMemory { verdict, verifier_role } => a::a10_verify_memory(&root, verdict.as_deref(), &session, verifier_role),
                AdoptCmd::Audit { accept_exceptions } => a::a11_audit(&root, *accept_exceptions), AdoptCmd::Status => a::status(&root), AdoptCmd::Rollback { batch } => a::rollback_batch(&root, *batch),
            }
        }
        Cmd::Update { check, apply, rollback, channel, break_glass, source, approve, by, reason } => {
            let mut p = open_project(cli, true)?;
            if *rollback { return gov_runtime::update::rollback_opts(&mut p, None, reason.as_deref(), *break_glass); }
            if *apply { return gov_runtime::update::apply_update_opts(&mut p, source.as_deref(), *approve, by, channel.clone(), *break_glass); }
            let _ = check; gov_runtime::update::check(&p, source.as_deref())
        }
        Cmd::Trust { op } => {
            let project_root = cli.root.clone().or_else(|| std::env::current_dir().ok());
            match op {
                TrustCmd::Status => gov_runtime::srr::status(),
                TrustCmd::Provision { anchor } => gov_runtime::srr::provision::provision(Path::new(anchor), project_root.as_deref()),
                TrustCmd::RootUpdate { anchor } => gov_runtime::srr::provision::root_update(Path::new(anchor), project_root.as_deref()),
                TrustCmd::BreakGlass => gov_runtime::srr::provision::break_glass_status(),
                TrustCmd::RecoverTransactions => {
                    let ms = gov_runtime::srr::state::MachineState::open()?;
                    let r = gov_runtime::srr::staging::recover(&ms)?;
                    Ok(json!({"replayed": r}))
                }
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
                TaskCmd::Show { id } => { let s = gov_runtime::records::RecordStore::load(&p.root); s.get(id).map(|r| r.data.clone()).ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("{id} not found"))) }
                TaskCmd::Status { id, status, note } => t::set_status(&p, id, status, note.as_deref()),
                TaskCmd::Claim { id } => t::claim(&p, id),
                TaskCmd::Release { id, force } => Ok(json!({"released": t::release(&p, id, *force)?})),
                TaskCmd::Close { id, report, force } => { let d = db(&p)?; let r = load_file_value(report)?; t::close(&p, &d, id, r, *force) }
                TaskCmd::Dag => Ok(serde_json::to_value(gov_runtime::orchestration::dag::compute(&p)?)?),
                TaskCmd::Replan => gov_runtime::orchestration::dag::replan(&p),
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
                CitCmd::Approve { id, by, method } => c::approve(&p, id, by, method),
                CitCmd::Reject { id, by, reason } => c::reject(&p, id, by, reason.as_deref()),
                CitCmd::Execute { id } => { let d = db(&p)?; c::execute(&p, &d, id) }
                CitCmd::Rollback { id, reason } => c::rollback(&p, id, reason.as_deref()),
                CitCmd::List => Ok(json!(c::list(&p))),
                CitCmd::Show { id } => { let s = gov_runtime::records::RecordStore::load(&p.root); s.get(id).map(|r| r.data.clone()).ok_or_else(|| GovError::new("CIT_NOT_FOUND", format!("{id} not found"))) }
            }
        }
        Cmd::Context { op } => { let p = open_project(cli, true)?; let d = db(&p)?; match op { ContextCmd::Compile { task } => gov_runtime::context::compile(&p, &d, task) } }
        Cmd::Checkpoint { op } => {
            let p = open_project(cli, true)?; let d = db(&p)?;
            match op {
                CheckpointCmd::Create { next_action, task, trigger, step, tests_status } => gov_runtime::checkpoints::create(&p, &d, json!({"next_action": next_action, "task": task, "trigger": trigger, "last_completed_step": step, "tests_status": tests_status})),
                CheckpointCmd::Latest => Ok(gov_runtime::checkpoints::latest(&p).unwrap_or(Value::Null)),
                CheckpointCmd::Watchdog { utilisation, ops, task, next_action } => gov_runtime::checkpoints::watchdog(&p, &d, *utilisation, *ops, task.as_deref(), next_action),
            }
        }
        Cmd::Skills { op } => { let p = open_project(cli, true)?; match op { SkillsCmd::List => Ok(json!(gov_runtime::skills::list_skills(&p))), SkillsCmd::Resolve { task } => { let s = gov_runtime::records::RecordStore::load(&p.root); let t = s.get(task).map(|r| r.data.clone()).ok_or_else(|| GovError::new("TASK_NOT_FOUND", format!("{task} not found")))?; gov_runtime::skills::resolve(&p, &t) } } }
        Cmd::Tools { op } => {
            let p = open_project(cli, true)?;
            match op {
                ToolsCmd::List => { let mut t = gov_runtime::tools::kernel_tools(&p); t.extend(gov_runtime::tools::project_tools(&p)); Ok(json!({"tools": t, "mcp_servers": gov_runtime::tools::mcp_servers(&p)})) }
                ToolsCmd::Registry => gov_runtime::tools::generate_registry(&p),
                ToolsCmd::Resolve { role, capability } => gov_runtime::tools::resolve(&p, role.as_deref().unwrap_or(&p.role), capability),
                ToolsCmd::Install { descriptor, role, execute } => { let d = load_file_value(descriptor)?; gov_runtime::tools::install(&p, d, role.as_deref().unwrap_or(&p.role), *execute) }
                ToolsCmd::Health => Ok(json!(gov_runtime::tools::health(&p))),
            }
        }
        Cmd::Handoff { op } => { let p = open_project(cli, true)?; match op { HandoffCmd::Create { to_role, task, fields } => { let mut f = parse_json_arg(fields)?; if !f.is_object() { f = json!({}); } f["to_role"] = json!(to_role); f["task"] = json!(task); gov_runtime::orchestration::handoffs::create(&p, f) } HandoffCmd::Return { id, file } => gov_runtime::orchestration::handoffs::return_result(&p, id, load_file_value(file)?) } }
        Cmd::Memory { op } => {
            let p = open_project(cli, true)?;
            match op {
                MemoryCmd::Query { query, k, route, include_historical } => { let d = db(&p)?; let r = gov_runtime::retrieval::retrieve(&p, &d, query, gov_runtime::retrieval::RetrieveOptions { k: *k, route: route.clone(), include_historical: *include_historical, log: true, ..Default::default() })?; gov_runtime::observability::emit(&p, "retrieval", json!({"routes": r.routes, "hits": r.hits.len(), "latency_ms": r.latency_ms}))?; Ok(serde_json::to_value(&r)?) }
                MemoryCmd::Verify => { let d = db(&p)?; let hp = p.root.join(p.policies().get_str("MEMORY_POLICY", "regression.heldout_file", "governance/tests/memory/heldout.yaml")); let held = gov_runtime::util::read_yaml(&hp)?; let r = gov_runtime::retrieval::run_heldout(&p, &d, &held)?; if r["measured"].as_bool().unwrap_or(false) && !r["pass"].as_bool().unwrap_or(false) { return Err(GovError::new("VERIFICATION_FAILED", "held-out memory regression failed").with_details(r)); } Ok(r) }
                MemoryCmd::Benchmark { candidates, heldout, record } => gov_runtime::memory::benchmark::run(&p, candidates, heldout.clone(), *record),
                MemoryCmd::Select { candidate, research, by } => gov_runtime::memory::benchmark::select(&p, candidate, research.as_deref(), by),
                MemoryCmd::HeldoutStarter { force } => { let d = db(&p)?; let hp = p.root.join(p.policies().get_str("MEMORY_POLICY", "regression.heldout_file", "governance/tests/memory/heldout.yaml")); let existing = gov_runtime::util::read_yaml(&hp).ok().and_then(|h| h["queries"].as_array().map(|a| a.len())).unwrap_or(0); if existing > 0 && !force { return Err(GovError::new("USAGE", format!("{} already has {existing} queries (use --force to overwrite)", hp.display()))); } let set = gov_runtime::memory::heldout::generate_starter(&p, &d, "gov memory heldout-starter")?; gov_runtime::util::write_yaml(&hp, &set)?; Ok(json!({"path": hp.display().to_string(), "queries": set["queries"].as_array().map(|a| a.len()).unwrap_or(0)})) }
                MemoryCmd::Freshness => Ok(serde_json::to_value(gov_runtime::memory::manifest::freshness(&p))?),
                MemoryCmd::Rebuild { incremental } => Ok(serde_json::to_value(gov_runtime::memory::indexer::rebuild(&p, gov_runtime::memory::indexer::IndexOptions { incremental: *incremental, ..Default::default() })?)?),
                MemoryCmd::Graph { node, depth } => { let d = db(&p)?; Ok(json!(gov_runtime::graph::neighbours(&d, node, *depth)?)) }
                MemoryCmd::Impact { seeds, depth } => { let d = db(&p)?; Ok(json!(gov_runtime::graph::impact_set(&d, &csv(&Some(seeds.clone())), *depth)?)) }
            }
        }
        Cmd::Gate { op } => { let p = open_project(cli, true)?; match op { GateCmd::Create { question, fields } => { let mut f = parse_json_arg(fields)?; if !f.is_object() { f = json!({}); } f["question"] = json!(question); gov_runtime::orchestration::gates::create(&p, f) } GateCmd::Present { id } => { let (d, text) = gov_runtime::orchestration::gates::present(&p, id)?; if !cli.json { println!("{text}"); } Ok(json!({"gate": d, "chat_text": text})) } GateCmd::Revoke { id, reason } => gov_runtime::orchestration::gates::revoke(&p, id, reason.as_deref()), GateCmd::List => Ok(json!(gov_runtime::orchestration::gates::pending(&p))) } }
        Cmd::Readiness { op } => { let p = open_project(cli, true)?; match op { ReadinessCmd::Check { feature } => Ok(serde_json::to_value(gov_runtime::orchestration::readiness::check(&p, feature)?)?), ReadinessCmd::Plan { feature } => { gov_runtime::authority::require(&p, "readiness_plan")?; gov_runtime::orchestration::readiness::plan(&p, feature) } } }
        Cmd::Intent { text } => { let p = open_project(cli, true)?; gov_runtime::orchestration::intents::route(&p, text) }
        Cmd::Route { task, class, radius, record, report } => { let p = open_project(cli, true)?; if *report { return gov_runtime::routing::report(&p); }
            if let Some(r) = record { return gov_runtime::routing::record(&p, load_file_value(r)?); } let t = task.as_ref().and_then(|id| gov_runtime::records::RecordStore::load(&p.root).get(id).map(|r| r.data.clone())); gov_runtime::routing::route(&p, t.as_ref(), class.as_deref(), None, radius.as_deref()) }
        Cmd::Telemetry { op } => { let p = open_project(cli, true)?; match op { TelemetryCmd::Summary => gov_runtime::observability::summary(&p), TelemetryCmd::Emit { name, attrs } => gov_runtime::observability::emit(&p, name, parse_json_arg(attrs)?) } }
        Cmd::Adapters { op } => { let p = open_project(cli, true)?; match op { AdaptersCmd::Generate => gov_runtime::adapters::generate(&p), AdaptersCmd::Verify => { let v = gov_runtime::adapters::verify(&p)?; if !v["ok"].as_bool().unwrap_or(false) { return Err(GovError::new("VERIFICATION_FAILED", "adapter conformance failed").with_details(v)); } Ok(v) } } }
        Cmd::Release { op } => match op {
            ReleaseCmd::Build { version, out, certification, evidence, canonical } => { let croot = canonical.clone().or_else(gov_runtime::kernel::canonical_root).ok_or_else(|| GovError::new("KERNEL_SOURCE_NOT_FOUND", "canonical repository root not found (pass --canonical)"))?; let out = out.clone().unwrap_or(croot.join("release")); gov_runtime::release::build(&croot, version, &out, certification, evidence.as_deref()) }
            ReleaseCmd::Verify { dir } => gov_runtime::release::verify(dir),
        },
        Cmd::Kernel { op } => { let mut p = open_project(cli, true)?; match op { KernelCmd::Verify => { let v = serde_json::to_value(gov_runtime::kernel::verify_kernel(&p.kernel_dir())?)?; let t = gov_runtime::kernel_trust::trust(&p.root); Ok(json!({"ok": v["ok"], "modified": v["modified"], "missing": v["missing"], "added": v["added"], "payload_hash": v["payload_hash"], "version": v["version"], "trust": t.to_value()})) }
            KernelCmd::Trust => { let t = gov_runtime::kernel_trust::trust(&p.root); Ok(json!({"verified": t.verified, "summary": t.summary(), "trust": t.to_value()})) }
            KernelCmd::Override { reason } => gov_runtime::kernel_trust::request_override(&p, reason.as_deref()), KernelCmd::Reinstall { source, break_glass } => {
                gov_runtime::orchestration::control::guard_write(&p, "kernel reinstall")?;
                gov_runtime::authority::require(&p, "install_kernel")?;
                let lock = p.lock()?.clone();
                // Privileged lifecycle ingress `reinstall`: the one verification policy (ARCH-0003 §3.6).
                let src = gov_runtime::kernel::resolve_kernel_source(source.as_deref().map(Path::new).or_else(|| lock["source"].as_str().filter(|s| Path::new(s).exists()).map(Path::new)))?;
                let auth = gov_runtime::srr::admit(
                    gov_runtime::srr::AdmissionRequest::new(gov_runtime::srr::Ingress::Reinstall, &src)
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
            PluginsCmd::Registry => Ok(gov_runtime::capabilities::registry::load(&p)),
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
        Cmd::Health { .. } => "health", // WS-2 additive arm
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
                if banner["release_trust"]["below_floor"].as_bool().unwrap_or(true) {
                    println!(
                        "{}: {}",
                        banner["release_trust"]["marking"].as_str().unwrap_or(""),
                        banner["release_trust"]["operator_note"].as_str().unwrap_or("")
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
                if banner["release_trust"]["below_floor"].as_bool().unwrap_or(true) {
                    eprintln!(
                        "{}: {}",
                        banner["release_trust"]["marking"].as_str().unwrap_or(""),
                        banner["release_trust"]["operator_note"].as_str().unwrap_or("")
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
