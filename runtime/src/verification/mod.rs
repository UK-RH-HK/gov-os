//! Governance verification suite (framework §63-64; Contract v3 Gate O2/O4/O5).
//!
//! The families are executed by the Governance Health Scheduler (`crate::scheduler`): dependency-aware selection,
//! concurrent execution, sandbox isolation for checks that write state, a cache keyed by the digests of each check's
//! declared inputs, and a ledger of every health result with provenance. A green governance-suite record is current
//! only while its `inputs_hash` equals the key over **every** Contract v3:97-109 input class ([`currency`]).
use crate::memory::db::RuntimeDb;
use crate::memory::manifest::freshness;
use crate::records::{new_record, save_record, RecordStore};
use crate::scheduler::{self, CacheMode, RecordPolicy, RunOptions, Selection, Tier, Trigger};
use crate::util::{now_iso, read_yaml};
use crate::{graph, Project, Result};
use serde_json::{json, Value};

pub mod currency;
pub mod families_ext;
pub mod lineage;
pub mod product;
pub mod reporting;

pub const KNOWN_CLI: &[&str] = &[
    "status",
    "continue",
    "decide",
    "audit",
    "pause",
    "freeze-writes",
    "cancel-agents",
    "resume",
    "doctor",
    "init",
    "adopt",
    "update",
    "rebuild-memory",
    "upstream",
    "recover",
    "task",
    "cit",
    "context",
    "checkpoint",
    "skills",
    "tools",
    "handoff",
    "memory",
    "gate",
    "readiness",
    "intent",
    "route",
    "telemetry",
    "adapters",
    "release",
    "migrate",
    "verify",
    "kernel",
    "capabilities",
    "claims",
    "version",
    "mcp",
    "lessons",
    "plugins",
    "policy",
    "health",
];

/// The suite-level currency key over every evidence input class (see [`currency`]).
pub fn inputs_hash(p: &Project) -> String {
    currency::inputs_hash(p)
}

/// The latest green governance-suite record.
pub fn latest_green(p: &Project) -> Option<Value> {
    currency::latest_green(p)
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct Family {
    pub id: String,
    pub ok: bool,
    pub findings: Vec<Value>,
    pub detail: Value,
}

fn finding(sev: &str, family: &str, msg: String, path: Option<String>) -> Value {
    json!({"severity": sev, "family": family, "message": msg, "path": path})
}

pub struct SuiteOptions {
    pub deep: bool,
    pub families: Vec<String>,
}

/// What a family executes against: a project (live, or a sandbox copy), its derived index and its records.
pub struct FamilyCtx<'a> {
    pub p: &'a Project,
    pub db: Option<&'a RuntimeDb>,
    pub store: &'a RecordStore,
    pub deep: bool,
    /// The run's input snapshot (shared by every family of one scheduler run).
    pub snapshot: Option<&'a currency::Snapshot>,
}

/// Execute one governance family. Called by the scheduler on a worker thread (or inside a sandbox).
pub fn run_family(ctx: &FamilyCtx, fam: &str) -> Result<Family> {
    let p = ctx.p;
    let store = ctx.store;
    let db = ctx.db;
    let pol = p.policies();
    let fam = fam.to_string();
    let opts = SuiteOptions {
        deep: ctx.deep,
        families: vec![],
    };
    {
        let mut f = Family {
            id: fam.clone(),
            ok: true,
            findings: vec![],
            detail: Value::Null,
        };
        match fam.as_str() {
            "schema_invariants" => {
                for pr in &p.overlay().problems {
                    f.findings.push(finding("high", &fam, pr.clone(), None));
                }
                for pr in &pol.problems {
                    f.findings.push(finding("high", &fam, pr.clone(), None));
                }
                if let Ok(inv) = read_yaml(
                    &p.kernel_dir()
                        .join("constitution")
                        .join("HARD_INVARIANTS.yaml"),
                ) {
                    if let Ok(e) = p.schemas().errors("hard-invariants", &inv) {
                        for x in e {
                            f.findings.push(finding("critical", &fam, x, None));
                        }
                    }
                } else {
                    f.findings.push(finding(
                        "critical",
                        &fam,
                        "HARD_INVARIANTS.yaml unreadable".into(),
                        None,
                    ));
                }
                let mut checked = 0;
                let statuses = pol.get_list("AUTHORITY_POLICY", "lifecycle_statuses");
                let classes = pol.get_list("AUTHORITY_POLICY", "state_classes");
                for r in &store.records {
                    if r.problems.iter().any(|x| x == "archived") {
                        continue;
                    }
                    let t = r.rtype();
                    // a governed record that is hidden Qualification Oracle material (an oracle document, a fault
                    // manifest, a hidden path-map or memory oracle): the verifier-owned oracle must never live in the
                    // governed repository (Contract v3:1014, :1062; ws01-12 IP-5)
                    if crate::qualification_oracle::is_hidden_oracle_material(&r.data) {
                        f.findings.push(finding("high", &fam, format!("{} ({t}) is hidden Qualification Oracle material inside the governed repository: the verifier-owned hidden oracle must stay in verifier custody, separate from the qualification repository (Contract v3:1014, :1062); remove it from the repository and its history, and re-seal the oracle", r.id()), Some(r.path.clone())));
                    }
                    let schema = if p.schemas().has(&t) {
                        t.clone()
                    } else {
                        "record".into()
                    };
                    match p.schemas().errors(&schema, &r.data) {
                        Ok(errs) => {
                            checked += 1;
                            for e in errs.iter().take(3) {
                                f.findings.push(finding(
                                    "high",
                                    &fam,
                                    format!("{} ({t}): {e}", r.id()),
                                    Some(r.path.clone()),
                                ));
                            }
                        }
                        Err(e) => f.findings.push(finding(
                            "medium",
                            &fam,
                            e.to_string(),
                            Some(r.path.clone()),
                        )),
                    }
                    if !statuses.is_empty() && !statuses.contains(&r.status()) {
                        f.findings.push(finding(
                            "high",
                            &fam,
                            format!(
                                "{} has status '{}' outside AUTHORITY_POLICY.lifecycle_statuses",
                                r.id(),
                                r.status()
                            ),
                            Some(r.path.clone()),
                        ));
                    }
                    let sc = r.get("state_class");
                    if !sc.is_empty() && !classes.is_empty() && !classes.contains(&sc) {
                        f.findings.push(finding(
                            "high",
                            &fam,
                            format!(
                                "{} has state_class '{sc}' outside AUTHORITY_POLICY.state_classes",
                                r.id()
                            ),
                            Some(r.path.clone()),
                        ));
                    }
                }
                for (id, paths) in &store.duplicates {
                    f.findings.push(finding(
                        "high",
                        &fam,
                        format!("duplicate record id {id} at {}", paths.join(", ")),
                        None,
                    ));
                }
                // authority must be unambiguous: a superseded record that is still ACTIVE is a contradiction
                let mut by_id: std::collections::BTreeMap<String, &crate::records::Record> =
                    std::collections::BTreeMap::new();
                for r in &store.records {
                    if !r.problems.iter().any(|x| x == "archived") {
                        by_id.insert(r.id(), r);
                    }
                }
                for r in &store.records {
                    for s in r.list("supersedes") {
                        if let Some(t) = by_id.get(&s) {
                            if t.status() == "ACTIVE" {
                                f.findings.push(finding("high", &fam, format!("{} is superseded by {} but still ACTIVE (UNKNOWN_OR_CONFLICTING authority)", s, r.id()), Some(t.path.clone())));
                            }
                        }
                    }
                }
                f.detail = json!({"records_checked": checked});
            }
            "graph_integrity" => {
                if let Some(db) = &db {
                    let d = graph::dangling_edges(db)?;
                    if !d.is_empty() {
                        f.findings.push(finding(
                            "medium",
                            &fam,
                            format!(
                                "{} dangling edge(s) reference unknown artefacts (e.g. {} {} {})",
                                d.len(),
                                d[0]["src"],
                                d[0]["type"],
                                d[0]["dst"]
                            ),
                            None,
                        ));
                    }
                    let o = graph::orphan_nodes(db)?;
                    f.detail = json!({"dangling": d.len(), "orphans": o.len(), "orphan_records": o, "dangling_edges": d.iter().take(20).collect::<Vec<_>>(), "edge_types": graph::edge_type_counts(db)?});
                } else {
                    f.findings.push(finding(
                        "medium",
                        &fam,
                        "runtime DB missing; run gov rebuild-memory".into(),
                        None,
                    ));
                }
                let dag = crate::orchestration::dag::compute(p)?;
                // W1 canonical path, W8 stale lineage links, `blocks` naming no task (ws04 IP-7, ws05 IP-2)
                let (lf, ld) = reporting::graph_lineage_findings(p, store, &dag, &fam);
                f.findings.extend(lf);
                if let Some(o) = f.detail.as_object_mut() {
                    o.insert("lineage".into(), ld);
                } else {
                    f.detail = json!({"lineage": ld});
                }
                if !dag.cycles.is_empty() {
                    f.findings.push(finding(
                        "high",
                        &fam,
                        format!("task DAG has cycles: {:?}", dag.cycles),
                        None,
                    ));
                }
                for m in &dag.missing_dependencies {
                    f.findings.push(finding(
                        "high",
                        &fam,
                        format!("task {} depends on missing {}", m["task"], m["dependency"]),
                        None,
                    ));
                }
            }
            "index_freshness" => {
                let fr = freshness(p);
                if !fr.manifest_present {
                    f.findings.push(finding(
                        "medium",
                        &fam,
                        "index manifest missing".into(),
                        None,
                    ));
                } else if !fr.fresh {
                    f.findings.push(finding(
                        "medium",
                        &fam,
                        format!(
                            "index stale: {} changed, {} added, {} removed",
                            fr.stale.len(),
                            fr.added.len(),
                            fr.removed.len()
                        ),
                        None,
                    ));
                }
                f.detail = json!({"checked": fr.checked, "stale": fr.stale, "added": fr.added, "removed": fr.removed});
            }
            "memory_retrieval_regression" => {
                let hp = p.root.join(pol.get_str(
                    "MEMORY_POLICY",
                    "regression.heldout_file",
                    "governance/tests/memory/heldout.yaml",
                ));
                if let (Some(db), true) = (&db, hp.exists()) {
                    let held = read_yaml(&hp)?;
                    let r = crate::retrieval::run_heldout(p, db, &held)?;
                    if !r["measured"].as_bool().unwrap_or(false) {
                        f.findings.push(finding("medium", &fam, format!("memory recall is UNMEASURED: {} held-out queries (< MEMORY_POLICY.regression.min_queries {}); a green suite with unmeasured recall is not healthy (framework §17)", r["queries"], r["min_queries"]), Some(hp.strip_prefix(&p.root).unwrap_or(&hp).to_string_lossy().to_string())));
                    } else if !r["pass"].as_bool().unwrap_or(false) {
                        f.findings.push(finding("high", &fam, format!("held-out retrieval regression failed: recall@k {:.2} mrr {:.2} stale {:.2} superseded {:.2} forbidden {}", r["recall_at_k"].as_f64().unwrap_or(0.0), r["mrr"].as_f64().unwrap_or(0.0), r["stale_hit_rate"].as_f64().unwrap_or(0.0), r["superseded_hit_rate"].as_f64().unwrap_or(0.0), r["forbidden_violations"]), None));
                    }
                    // the failing results travel with the result so a persisted run can record them in failure
                    // memory (memory::failures::record_heldout_misses, ws06 IP-2) — only `audit_with` persists them
                    let failing: Vec<Value> = r["results"].as_array().map(|a| a.iter().filter(|x| !x["pass"].as_bool().unwrap_or(false)).map(|x| json!({"id": x["id"], "query": x["query"], "expected": x["expected"], "got": x["got"], "recall": x["recall"], "routes": x["routes"], "forbidden_hits": x["forbidden_hits"], "pass": false})).collect()).unwrap_or_default();
                    f.detail = json!({"status": r["status"], "recall_at_k": r["recall_at_k"], "mrr": r["mrr"], "precision_at_k": r["precision_at_k"], "queries": r["queries"], "pending": r["pending_queries"], "failed": failing.iter().map(|x| x["id"].clone()).collect::<Vec<_>>(), "failed_results": failing});
                } else if !hp.exists() {
                    f.findings.push(finding(
                        "medium",
                        &fam,
                        format!("held-out memory tests missing at {}", hp.display()),
                        None,
                    ));
                } else {
                    f.findings
                        .push(finding("medium", &fam, "runtime DB missing".into(), None));
                }
            }
            "authority_role_limits" => {
                let roles = read_yaml(
                    &crate::kernel_trust::trusted_root(p)
                        .join("roles")
                        .join("ROLES.yaml"),
                )
                .unwrap_or(json!({}));
                let known: Vec<String> = roles["roles"]
                    .as_array()
                    .map(|a| {
                        a.iter()
                            .filter_map(|r| r["id"].as_str().map(|s| s.to_string()))
                            .collect()
                    })
                    .unwrap_or_default();
                for (role, _) in p.overlay().get("TOOL_PERMISSIONS.yaml")["roles"]
                    .as_object()
                    .cloned()
                    .unwrap_or_default()
                {
                    if !known.contains(&role) {
                        f.findings.push(finding(
                            "medium",
                            &fam,
                            format!("TOOL_PERMISSIONS role '{role}' is not a kernel role"),
                            None,
                        ));
                    }
                }
                for h in store.of_type("handoff") {
                    if h.get("to_role") == "orchestrator"
                        && !h
                            .data
                            .get("explicit_orchestrator_assignment")
                            .and_then(|v| v.as_bool())
                            .unwrap_or(false)
                    {
                        f.findings.push(finding("high", &fam, format!("{} hands orchestrator role to a worker without explicit assignment (INV-014)", h.id()), Some(h.path.clone())));
                    }
                }
                for t in store.of_type("task") {
                    if t.list("allowed_paths")
                        .iter()
                        .any(|a| crate::util::glob_match(a, "governance/kernel/x"))
                    {
                        f.findings.push(finding(
                            "critical",
                            &fam,
                            format!(
                                "{} allowed_paths include governance/kernel (INV-007)",
                                t.id()
                            ),
                            Some(t.path.clone()),
                        ));
                    }
                }
            }
            "mutation_scope" => {
                match crate::kernel::verify_kernel(&p.kernel_dir()) { Ok(v) if !v.ok => f.findings.push(finding("critical", &fam, format!("kernel payload modified in place (INV-007): modified {:?} missing {:?} added {:?}", v.modified, v.missing, v.added), None)), Err(e) => f.findings.push(finding("critical", &fam, e.to_string(), None)), _ => {} }
                for h in store.of_type("handoff") {
                    if let Some(v) = h.data.get("authority_violations") {
                        f.findings.push(finding(
                            "high",
                            &fam,
                            format!("{} returned with authority violations: {v}", h.id()),
                            Some(h.path.clone()),
                        ));
                    }
                }
            }
            "path_map_compliance" => {
                let contract = p.contract();
                let mut unknown = 0;
                let mut secrets_wrong = vec![];
                let mut oracle_material = vec![];
                let record_paths: std::collections::BTreeSet<&str> =
                    store.records.iter().map(|r| r.path.as_str()).collect();
                for (abs, rel) in crate::paths::iter_repo_files(&p.root, false) {
                    // hidden Qualification Oracle material must never live in a governed repository
                    // (Contract v3:1014, :1062; ws01-12 IP-5); governed records are checked by schema_invariants,
                    // every other file here
                    if !record_paths.contains(rel.as_str())
                        && reporting::hidden_oracle_material(&abs)
                    {
                        oracle_material.push(rel.clone());
                    }
                    let d = contract.decide(&rel);
                    if d.rule_pattern.is_none()
                        && (rel.starts_with("spec/")
                            || rel.starts_with("governance/")
                            || rel.starts_with("product/"))
                    {
                        unknown += 1;
                    }
                    if !d.is_secret()
                        && !p.secret_scanner().path_is_secret(&rel)
                        && !p.secret_scanner().scan_file(&abs, &rel).is_empty()
                    {
                        secrets_wrong.push(rel.clone());
                    }
                }
                if unknown > 0 {
                    f.findings.push(finding("low", &fam, format!("{unknown} file(s) under governed roots match no repository-contract rule"), None));
                }
                for s in &secrets_wrong {
                    f.findings.push(finding("critical", &fam, "secret content in a non-secret-class path (blocked from index; must be moved or classified secret)".into(), Some(s.clone())));
                }
                for m in &oracle_material {
                    f.findings.push(finding("high", &fam, format!("hidden Qualification Oracle material inside the governed repository at {m}: the verifier-owned hidden oracle must stay in verifier custody, separate from the qualification repository (Contract v3:1014, :1062); remove it from the repository and its history, and re-seal the oracle"), Some(m.clone())));
                }
                f.detail = json!({"unmatched": unknown, "secret_content_outside_secret_class": secrets_wrong, "hidden_oracle_material": oracle_material});
            }
            "context_reproducibility" => {
                if let Some(db) = &db {
                    if let Some(t) = store.of_type("task").first() {
                        let a = crate::context::compile(p, *db, &t.id())?;
                        let b = crate::context::compile(p, *db, &t.id())?;
                        if a["deterministic_hash"] != b["deterministic_hash"] {
                            f.findings.push(finding(
                                "high",
                                &fam,
                                format!(
                                    "deterministic authority block not reproducible for {}",
                                    t.id()
                                ),
                                None,
                            ));
                        }
                        // CONTEXT_POLICY.deterministic_authority_fields / retrieved_fields must all be present in the packet
                        for fld in pol.get_list("CONTEXT_POLICY", "deterministic_authority_fields")
                        {
                            if a["deterministic_authority"].get(&fld).is_none() {
                                f.findings.push(finding("medium", &fam, format!("context packet lacks deterministic field '{fld}' (CONTEXT_POLICY.deterministic_authority_fields)"), None));
                            }
                        }
                        for fld in pol.get_list("CONTEXT_POLICY", "retrieved_fields") {
                            if a["retrieved_intelligence"].get(&fld).is_none() {
                                f.findings.push(finding("low", &fam, format!("context packet lacks retrieved field '{fld}' (CONTEXT_POLICY.retrieved_fields)"), None));
                            }
                        }
                        for blk in pol.get_list("CONTEXT_POLICY", "packet_blocks") {
                            if a.get(&blk).is_none() {
                                f.findings.push(finding("medium", &fam, format!("context packet lacks block '{blk}' (CONTEXT_POLICY.packet_blocks)"), None));
                            }
                        }
                        f.detail = json!({"task": t.id(), "deterministic_hash": a["deterministic_hash"], "chars": a["chars"]});
                    }
                    // W4 / W12 G5: every dispatchable task's delivered inputs against its declared manifest (ws04 IP-9)
                    let (df, dd) = reporting::delivery_findings(p, db, store, &fam);
                    f.findings.extend(df);
                    if let Some(o) = f.detail.as_object_mut() {
                        o.insert("delivery".into(), dd);
                    } else {
                        f.detail = json!({"delivery": dd});
                    }
                } else {
                    f.findings
                        .push(finding("medium", &fam, "runtime DB missing".into(), None));
                }
            }
            "concurrency_claims" => {
                let cl = crate::orchestration::claims::list(p)?;
                let expired = cl
                    .iter()
                    .filter(|c| c["expired"].as_bool().unwrap_or(false))
                    .count();
                if expired > 0 {
                    f.findings.push(finding(
                        "low",
                        &fam,
                        format!("{expired} expired claim(s) not swept"),
                        None,
                    ));
                }
                for c in &cl {
                    if store.get(c["task_id"].as_str().unwrap_or("")).is_none() {
                        f.findings.push(finding(
                            "medium",
                            &fam,
                            format!("claim references unknown task {}", c["task_id"]),
                            None,
                        ));
                    }
                }
                f.detail = json!({"claims": cl.len(), "expired": expired});
            }
            "adapter_portability" => {
                let v = crate::adapters::verify(p)?;
                if !v["ok"].as_bool().unwrap_or(false) {
                    for pr in v["problems"].as_array().cloned().unwrap_or_default() {
                        f.findings.push(finding(
                            "medium",
                            &fam,
                            pr.as_str().unwrap_or("").to_string(),
                            None,
                        ));
                    }
                }
                f.detail = v;
            }
            "skill_regression" => {
                // version ↔ content binding and executed validation scenarios (each in its own sandbox)
                let (findings, detail) = crate::skills::regression(
                    p,
                    &crate::skills::RegressionOptions {
                        execute: true,
                        only: None,
                        observe: true,
                        include_deferred: false,
                    },
                );
                f.findings.extend(findings);
                f.detail = detail;
            }
            "command_contract_consistency" => {
                let c = read_yaml(
                    &p.kernel_dir()
                        .join("commands")
                        .join("COMMAND_CONTRACT.yaml"),
                )?;
                for op in c["internal_operations"]
                    .as_array()
                    .cloned()
                    .unwrap_or_default()
                {
                    let cli = op["cli"].as_str().unwrap_or("");
                    let head = cli.split_whitespace().next().unwrap_or("");
                    if !KNOWN_CLI.contains(&head) {
                        f.findings.push(finding(
                            "medium",
                            &fam,
                            format!(
                                "operation {} maps to unknown CLI command '{head}'",
                                op["operation"]
                            ),
                            None,
                        ));
                    }
                }
                for hs in c["human_surface"].as_array().cloned().unwrap_or_default() {
                    let cmd = hs["command"].as_str().unwrap_or("");
                    if !KNOWN_CLI.contains(&cmd) {
                        f.findings.push(finding(
                            "medium",
                            &fam,
                            format!("human-surface command '{cmd}' not implemented"),
                            None,
                        ));
                    }
                }
            }
            "secrets_sensitivity_indexing" => {
                if let Some(db) = &db {
                    let secret_arts = db.query("SELECT path FROM artifacts WHERE path_class='secret' OR namespace='secret'", &[])?;
                    for a in &secret_arts {
                        f.findings.push(finding(
                            "critical",
                            &fam,
                            "secret-class path present in index (INV-009)".into(),
                            a["path"].as_str().map(|s| s.to_string()),
                        ));
                    }
                    for cls in pol.get_list("SECURITY_POLICY", "never_index_classes") {
                        for a in
                            db.query("SELECT path FROM artifacts WHERE sensitivity=?1", &[&cls])?
                        {
                            f.findings.push(finding("critical", &fam, format!("{cls}-class artefact present in generic memory (SECURITY_POLICY.never_index_classes)"), a["path"].as_str().map(|s| s.to_string())));
                        }
                    }
                    let scanner = p.secret_scanner();
                    let mut leaked = 0;
                    for row in db.query("SELECT chunk_id, artifact_id, text FROM chunks", &[])? {
                        if !scanner
                            .scan_text(row["text"].as_str().unwrap_or(""), "chunk")
                            .is_empty()
                        {
                            leaked += 1;
                            f.findings.push(finding(
                                "critical",
                                &fam,
                                format!(
                                    "secret pattern found in indexed chunk {} (INV-009)",
                                    row["chunk_id"]
                                ),
                                row["artifact_id"].as_str().map(|s| s.to_string()),
                            ));
                        }
                    }
                    let vec_leak = db.query("SELECT v.chunk_id FROM vectors v JOIN artifacts a ON a.artifact_id=v.artifact_id WHERE a.path_class='secret'", &[])?.len();
                    if vec_leak > 0 {
                        f.findings.push(finding(
                            "critical",
                            &fam,
                            format!("{vec_leak} vector(s) derived from secret-class artefacts"),
                            None,
                        ));
                    }
                    // every secret-class path in the tree must be in the excluded list
                    let contract = p.contract();
                    let excluded: std::collections::HashSet<String> = db
                        .query("SELECT path FROM excluded", &[])?
                        .into_iter()
                        .filter_map(|r| r["path"].as_str().map(|s| s.to_string()))
                        .collect();
                    let mut missing_excl = vec![];
                    for (_, rel) in crate::paths::iter_repo_files(&p.root, false) {
                        if contract.decide(&rel).is_secret() && !excluded.contains(&rel) {
                            missing_excl.push(rel);
                        }
                    }
                    for m in &missing_excl {
                        f.findings.push(finding("high", &fam, "secret-class path not recorded as excluded (index may predate the file; rebuild)".into(), Some(m.clone())));
                    }
                    f.detail = json!({"secret_artifacts": secret_arts.len(), "leaked_chunks": leaked, "excluded": excluded.len()});
                } else {
                    f.findings
                        .push(finding("medium", &fam, "runtime DB missing".into(), None));
                }
            }
            "recovery_rebuild" => {
                if opts.deep {
                    let tracked = crate::memory::manifest::read_index_manifest(p)
                        .and_then(|m| m["manifest_hash"].as_str().map(|s| s.to_string()));
                    let first = crate::memory::indexer::rebuild(
                        p,
                        crate::memory::indexer::IndexOptions {
                            incremental: false,
                            ..Default::default()
                        },
                    )?;
                    let second = crate::memory::indexer::rebuild(
                        p,
                        crate::memory::indexer::IndexOptions {
                            incremental: false,
                            ..Default::default()
                        },
                    )?;
                    if first.manifest_hash != second.manifest_hash
                        && pol.get_bool(
                            "MEMORY_POLICY",
                            "rebuild.must_reproduce_manifest_hash",
                            true,
                        )
                    {
                        f.findings.push(finding(
                            "high",
                            &fam,
                            format!(
                                "two consecutive full rebuilds differ ({} → {})",
                                first.manifest_hash, second.manifest_hash
                            ),
                            None,
                        ));
                    }
                    f.detail = json!({"deep": true, "tracked_before": tracked, "rebuild_1": first.manifest_hash, "rebuild_2": second.manifest_hash, "duration_ms": first.duration_ms + second.duration_ms});
                } else if let Some(db) = &db {
                    let tracked = crate::memory::manifest::read_index_manifest(p)
                        .and_then(|m| m["manifest_hash"].as_str().map(|s| s.to_string()));
                    let live = db
                        .get_meta("index_manifest_hash")
                        .and_then(|v| v.as_str().map(|s| s.to_string()));
                    if tracked != live {
                        f.findings.push(finding("medium", &fam, "tracked index-manifest hash differs from live runtime (rebuild or commit manifests)".into(), None));
                    }
                    f.detail = json!({"deep": false, "tracked": tracked, "live": live});
                } else {
                    f.findings.push(finding(
                        "medium",
                        &fam,
                        "runtime DB missing (a clean machine must run gov rebuild-memory)".into(),
                        None,
                    ));
                }
            }
            "fresh_agent_reconstruction" => {
                let st = crate::status::status(p)?;
                let budget =
                    pol.get_i64("CONTEXT_POLICY", "fresh_agent_read_budget_files", 25) as usize;
                let needed = st["fresh_agent_reads"]
                    .as_array()
                    .map(|a| a.len())
                    .unwrap_or(0);
                if needed > budget {
                    f.findings.push(finding("medium", &fam, format!("fresh-agent reconstruction needs {needed} file reads > budget {budget}"), None));
                }
                let chars = serde_json::to_string(&st)?.len();
                let max = pol.get_i64("CONTEXT_POLICY", "max_packet_chars", 60000) as usize;
                if chars > max {
                    f.findings.push(finding(
                        "low",
                        &fam,
                        format!("status packet {chars} chars exceeds max_packet_chars {max}"),
                        None,
                    ));
                }
                f.detail = json!({"reads": needed, "budget": budget, "status_chars": chars, "next_action": st["next_action"]});
            }
            "policy_precedence" => {
                for r in &pol.refused_overrides {
                    f.findings.push(finding(
                        "critical",
                        &fam,
                        format!(
                            "override of {}.{} from {} refused by POLICY_PRECEDENCE: {}",
                            r["policy"].as_str().unwrap_or(""),
                            r["key"].as_str().unwrap_or(""),
                            r["source"].as_str().unwrap_or(""),
                            r["reason"].as_str().unwrap_or("")
                        ),
                        None,
                    ));
                }
                if pol.precedence.is_none() {
                    f.findings.push(finding("critical", &fam, "POLICY_PRECEDENCE rules unavailable: every override is refused (fail closed)".into(), None));
                }
                let kt = crate::kernel_trust::trust(&p.root);
                if kt.installed && !kt.verified {
                    f.findings.push(finding(
                        "critical",
                        &fam,
                        format!(
                            "constitutional policy is not being read from a verified kernel: {}",
                            kt.summary()
                        ),
                        Some("governance/kernel".into()),
                    ));
                }
                f.detail = json!({"applied": pol.applied_overrides, "refused": pol.refused_overrides, "precedence": pol.precedence});
            }
            "plugin_governance" => {
                for x in crate::capabilities::governance::findings(p) {
                    f.findings.push(finding(
                        x["severity"].as_str().unwrap_or("medium"),
                        &fam,
                        x["message"].as_str().unwrap_or("").to_string(),
                        x["path"].as_str().map(|s| s.to_string()),
                    ));
                }
                let set = crate::capabilities::governance::plugin_set(p);
                f.detail = json!({"role": p.role, "usable": set.usable.iter().map(|d| d.plugin_id.clone()).collect::<Vec<_>>(), "denied": set.denied.len(), "rejected": set.rejected.len()});
            }
            "policy_enforcement_coverage" => match crate::policy_coverage::report(p) {
                Ok(r) => {
                    for k in r["uncovered"].as_array().cloned().unwrap_or_default() {
                        f.findings.push(finding("high", &fam, format!("policy key {} is declared but neither enforced nor classified informational (ENFORCEMENT_MAP.yaml)", k.as_str().unwrap_or("")), None));
                    }
                    for k in r["map_entries_without_policy_key"]
                        .as_array()
                        .cloned()
                        .unwrap_or_default()
                    {
                        f.findings.push(finding(
                            "low",
                            &fam,
                            format!(
                                "ENFORCEMENT_MAP entry {} has no policy key",
                                k.as_str().unwrap_or("")
                            ),
                            None,
                        ));
                    }
                    f.detail = r;
                }
                Err(e) => f.findings.push(finding(
                    "high",
                    &fam,
                    format!("ENFORCEMENT_MAP.yaml unreadable: {e}"),
                    None,
                )),
            },
            "product_traceability" => {
                let tasks = store.of_type("task");
                let families = pol.get_list("TEST_POLICY", "product_families");
                let indep = pol.get_list("TEST_POLICY", "independent_test_author_required_for");
                for o in store.of_type("test-obligation") {
                    let fam_name = o.get("family");
                    if !families.is_empty() && !families.contains(&fam_name) {
                        f.findings.push(finding("medium", &fam, format!("{} declares test family '{fam_name}' outside TEST_POLICY.product_families", o.id()), Some(o.path.clone())));
                    }
                    if indep.contains(&fam_name)
                        && !o
                            .data
                            .get("independent_of_implementer")
                            .and_then(|v| v.as_bool())
                            .unwrap_or(false)
                    {
                        f.findings.push(finding("medium", &fam, format!("{} ({fam_name}) is not independent of the implementer (TEST_POLICY.independent_test_author_required_for)", o.id()), Some(o.path.clone())));
                    }
                }
                let done: Vec<_> = tasks
                    .iter()
                    .filter(|t| t.get("task_status") == "DONE")
                    .collect();
                let untraced: Vec<String> = done
                    .iter()
                    .filter(|t| {
                        t.get("closed_by_report").is_empty() && t.get("class") != "governance"
                    })
                    .map(|t| t.id())
                    .collect();
                let features = store.of_type("feature");
                let mut no_scn = vec![];
                let mut no_tests = vec![];
                for fe in &features {
                    if fe.list("scenarios").is_empty() {
                        no_scn.push(fe.id());
                    }
                    let has_test = store
                        .of_type("test-obligation")
                        .iter()
                        .any(|t| t.get("feature") == fe.id())
                        || !fe.list("acceptance_tests").is_empty();
                    if !has_test {
                        no_tests.push(fe.id());
                    }
                }
                for u in &untraced {
                    f.findings.push(finding(
                        "medium",
                        &fam,
                        format!("{u} is DONE without a closing report"),
                        None,
                    ));
                }
                for s in &no_scn {
                    f.findings.push(finding(
                        "low",
                        &fam,
                        format!("feature {s} has no scenarios"),
                        None,
                    ));
                }
                for s in &no_tests {
                    f.findings.push(finding(
                        "low",
                        &fam,
                        format!("feature {s} has no test obligations/acceptance tests"),
                        None,
                    ));
                }
                let pct = if tasks.is_empty() {
                    1.0
                } else {
                    tasks
                        .iter()
                        .filter(|t| !t.get("feature").is_empty())
                        .count() as f64
                        / tasks.len() as f64
                };
                // W5: DONE work whose implementation does not trace to its requirements (ws04 IP-8)
                let (uf, un) = reporting::untraceable_findings(p, store, &fam);
                f.findings.extend(uf);
                f.detail = json!({"tasks": tasks.len(), "done": done.len(), "task_traceability": pct, "features": features.len(), "untraceable_closed_tasks": un});
            }
            "audit_reproducibility" => {
                f.detail = json!({"note": "result hash compared across two consecutive in-process runs by `gov audit` (see audit record result_hash)"});
            }
            "product_test_health" => {
                let (findings, detail) = product::health_findings(p, ctx.snapshot);
                f.findings.extend(findings);
                f.detail = detail;
            }
            "human_gate_integrity" => families_ext::human_gate_integrity(store, &mut f),
            "change_control_integrity" => families_ext::change_control_integrity(p, store, &mut f),
            "continuity_checkpoint_handoff" => {
                families_ext::continuity_checkpoint_handoff(p, store, &mut f)
            }
            "model_routing_integrity" => families_ext::model_routing_integrity(p, store, &mut f),
            "lineage_orphans" => reporting::lineage_orphans(p, store, db, &mut f),
            "os_binding_integrity" => reporting::os_binding_integrity(p, store, &mut f),
            "installation_authenticity" => reporting::installation_authenticity(p, &mut f),
            "contract_binding" => reporting::contract_binding(p, &mut f),
            "index_content_coverage" => reporting::index_content_coverage(p, db, &mut f),
            "task_contract_integrity" => reporting::task_contract_integrity(p, store, &mut f),
            other => {
                f.findings.push(finding(
                    "low",
                    other,
                    "unknown governance family in TEST_POLICY".into(),
                    None,
                ));
            }
        }
        let _ = &opts;
        f.ok = !f.findings.iter().any(|x| {
            matches!(
                x["severity"].as_str(),
                Some("critical") | Some("high") | Some("medium")
            )
        });
        Ok(f)
    }
}

/// Compatibility entry point: execute the (selected) suite families through the scheduler without reading or writing
/// the cache or the ledger. Families run concurrently; state-writing families run in sandboxes.
pub fn run(p: &Project, opts: &SuiteOptions) -> Result<Vec<Family>> {
    let mut o = RunOptions::new(Tier::G5, Trigger::new("verification::run"));
    o.selection = if opts.families.is_empty() {
        Selection::All
    } else {
        Selection::Explicit(opts.families.clone())
    };
    o.cache = CacheMode::Off;
    o.deep = opts.deep;
    o.surface = "suite".into();
    o.record = RecordPolicy::Never;
    o.ledger = false;
    let out = scheduler::run_suite(p, &o)?;
    Ok(out.wanted_families())
}

fn result_hash(fams: &[Family]) -> String {
    crate::util::hash_value(&json!(fams
        .iter()
        .map(|f| json!({"id": f.id, "ok": f.ok, "findings": f.findings}))
        .collect::<Vec<_>>()))
}

/// `gov audit`: the full suite (G5) through the scheduler. Checks whose declared inputs are unchanged since their
/// cached result are served from the cache (`--no-cache` re-executes them); everything executed is shown
/// reproducible (double run or identical-key comparison). Persists a governance-suite record with provenance.
pub fn audit(p: &Project, opts: &SuiteOptions, persist: bool) -> Result<Value> {
    let mut o = RunOptions::new(Tier::G5, Trigger::new("gov audit"));
    o.selection = if opts.families.is_empty() {
        Selection::All
    } else {
        Selection::Explicit(opts.families.clone())
    };
    o.cache = CacheMode::Use;
    o.deep = opts.deep;
    o.surface = "audit".into();
    o.record = if persist {
        RecordPolicy::Always
    } else {
        RecordPolicy::Never
    };
    audit_with(p, &o)
}

/// Does this run produce W7 remediation (BC-P2-22 / Contract v3:1144)? Only a run that may persist evidence (not
/// `--no-persist`, not a G0 re-evaluation), at a tier that audits lineage and orphan states (G4-G6), and that selects
/// the lineage family.
fn generates_remediation(p: &Project, o: &RunOptions) -> bool {
    if o.record == RecordPolicy::Never || !matches!(o.tier, Tier::G4 | Tier::G5 | Tier::G6) {
        return false;
    }
    if !scheduler::suite_families(p)
        .iter()
        .any(|f| f == lineage::FAMILY)
    {
        return false;
    }
    match &o.selection {
        Selection::All => true,
        Selection::Tier(t) => scheduler::catalogue::get(lineage::FAMILY)
            .map(|d| d.tiers.contains(t))
            .unwrap_or(false),
        Selection::Explicit(ids) => ids.iter().any(|x| x == lineage::FAMILY),
    }
}

/// Run the suite under `o` and shape the result as an audit (the envelope every caller of [`audit`] relies on),
/// persisting a governance-suite record according to `o.record`.
///
/// Round-2 additions (WS-2):
/// * **W7 remediation** — before the run, every orphan without an investigation gets one linked governed
///   investigation task ([`lineage::generate_remediation`]); the run then evaluates the state that includes it, so
///   the evidence written is current for it (`--no-persist` and G0-G3 runs generate nothing);
/// * **stable finding ids** — one scheme for every finding the product mints: `migrations::identity::assign_finding_ids`
///   (family, message, path), shared with the adoption audit (ws04 IP-10 × ws09-11 IP-1);
/// * **T2-bound evidence** — the governance-suite record is sealed as written by this health operation
///   (`crate::t2`), and only sealed records are honoured as green evidence (IP-WS02-22);
/// * **failure memory** — a persisted run whose held-out retrieval regression failed records each missed query in
///   durable failure memory (`memory::failures::record_heldout_misses`, ws06 IP-2).
pub fn audit_with(p: &Project, o: &RunOptions) -> Result<Value> {
    let remediation = if generates_remediation(p, o) {
        let detected_by = format!("{} ({})", o.trigger.event, o.tier.as_str());
        Some(
            lineage::generate_remediation(p, &detected_by)
                .unwrap_or_else(|e| json!({"error": e.code, "message": e.message})),
        )
    } else {
        None
    };
    let mut out = scheduler::run_suite(p, o)?;
    let wanted = out.wanted_families();
    let mut findings: Vec<Value> = vec![];
    for f in &wanted {
        for x in &f.findings {
            let mut y = x.clone();
            if let Some(obj) = y.as_object_mut() {
                if obj.get("path").map(|v| v.is_null()).unwrap_or(false) {
                    obj.remove("path");
                }
                if obj.get("covers").map(|v| v.is_null()).unwrap_or(false) {
                    obj.remove("covers");
                }
            }
            findings.push(y);
        }
    }
    crate::migrations::identity::assign_finding_ids(&mut findings);
    let reproducible = !out.runs.iter().any(|r| r.reproducible == Some(false));
    let verdict = out.result["verdict"]
        .as_str()
        .unwrap_or("UNHEALTHY")
        .to_string();
    let complete = out.complete();
    let suite_verdict = out.result["suite_verdict"]
        .as_str()
        .unwrap_or("INCOMPLETE")
        .to_string();
    let green = complete && suite_verdict == "HEALTHY" && verdict == "HEALTHY";
    let families: serde_json::Map<String, Value> = out
        .runs
        .iter()
        .filter(|r| r.wanted)
        .filter_map(|r| {
            let f = r.family.as_ref()?;
            Some((
                f.id.clone(),
                json!({"ok": f.ok, "findings": f.findings.len(), "detail": f.detail, "status": match r.status { scheduler::Status::Executed => "executed", scheduler::Status::Reused => "reused", scheduler::Status::NotEvaluated => "not-evaluated" }, "cached_from": r.cached_from}),
            ))
        })
        .collect();
    let ih = out.snapshot.key();
    let h1 = result_hash(&wanted);
    let write = match o.record {
        RecordPolicy::Always => true,
        RecordPolicy::Never => false,
        RecordPolicy::WhenCompleteAndStale => {
            green
                && latest_green(p)
                    .map(|g| g["inputs_hash"].as_str() != Some(ih.as_str()))
                    .unwrap_or(true)
        }
    };
    let counts = json!({"critical": findings.iter().filter(|x| x["severity"] == "critical").count(), "high": findings.iter().filter(|x| x["severity"] == "high").count(), "medium": findings.iter().filter(|x| x["severity"] == "medium").count(), "low": findings.iter().filter(|x| x["severity"] == "low").count()});
    let provenance = json!({
        "tier": o.tier.as_str(), "trigger": o.trigger.to_value(), "health_result": out.result["id"],
        "checks": out.result["checks"], "run_summary": out.result["summary"], "parallelism": out.result["parallelism"],
        "cache_mode": o.cache.as_str(), "runtime": out.result["runtime"], "machine_trust": out.result["machine_trust"],
        "repository": out.result["repository"], "actor": out.result["actor"], "started_at": out.result["started_at"],
        "finished_at": out.result["finished_at"],
    });
    // failure memory: missed held-out queries of a persisted run whose regression executed now and failed
    let mut failure_memory = Value::Null;
    if o.record != RecordPolicy::Never {
        if let Some(r) = out.runs.iter().find(|r| {
            r.id == "memory_retrieval_regression" && r.status == scheduler::Status::Executed
        }) {
            // only a failing regression result is persisted into failure memory (WS-6 IP-2): individual misses of a
            // regression that meets its thresholds stay in the result detail
            if let Some(fam) = r.family.as_ref().filter(|f| !f.ok) {
                let failing = fam.detail["failed_results"].clone();
                if failing.as_array().map(|a| !a.is_empty()).unwrap_or(false) {
                    let recorded = crate::memory::failures::record_heldout_misses(
                        p,
                        &json!({"results": failing}),
                        &format!("health {} ({})", o.surface, o.tier.as_str()),
                    );
                    failure_memory =
                        json!(recorded.iter().map(|x| x.to_value()).collect::<Vec<_>>());
                }
            }
        }
    }
    let mut id = String::new();
    let mut record_binding = Value::Null;
    if write {
        let store = RecordStore::load(&p.root);
        id = store.next_id("audit");
        let mut fields = json!({"scope": "governance-suite", "auditor_role": p.role, "session": p.session_id, "families": families, "findings": findings, "verdict": verdict, "suite_verdict": suite_verdict, "complete": complete, "inputs_hash": ih, "inputs": out.snapshot.classes_value(), "result_hash": h1, "reproducible": reproducible, "green": green, "state_class": "EVIDENCE", "run_at": now_iso(), "deep": o.deep});
        if let (Some(m), Some(pv)) = (fields.as_object_mut(), provenance.as_object()) {
            for (k, v) in pv {
                m.insert(k.clone(), v.clone());
            }
        }
        if let Some(q) = &o.qualification {
            fields["qualification"] = q.clone();
        }
        if let Some(r) = &remediation {
            fields["remediation"] = r.clone();
        }
        let mut rec = new_record(
            "audit",
            &id,
            &format!("Governance suite audit {id} ({verdict})"),
            fields,
        );
        // T2: this record is honoured as evidence only while it is exactly what this health operation wrote
        record_binding = match crate::t2::seal_record(
            &mut rec,
            &currency::seal_operation("governance-suite"),
        ) {
            Ok(()) => json!({"sealed": true}),
            Err(e) => {
                json!({"sealed": false, "code": e.code, "message": e.message, "consequence": "the record is written but not honoured as green evidence on this machine"})
            }
        };
        save_record(&p.root, &rec)?;
        out.result["record"] = json!(id);
        if o.ledger {
            let _ = scheduler::store::save_result(p, &out.result);
        }
        // the audit record is evidence; keep the derived index fresh (verifier L4 / HV-28)
        if p.db_path().exists() {
            let _ = crate::memory::indexer::rebuild(
                p,
                crate::memory::indexer::IndexOptions {
                    incremental: true,
                    ..Default::default()
                },
            );
        }
    }
    Ok(json!({
        "audit": id, "verdict": verdict, "green": green, "families": families, "findings": findings,
        "inputs_hash": ih, "inputs": out.snapshot.classes_value(), "result_hash": h1, "reproducible": reproducible, "counts": counts,
        "complete": complete, "suite_verdict": suite_verdict,
        "health_result": out.result["id"], "tier": o.tier.as_str(), "summary": out.result["summary"],
        "parallelism": out.result["parallelism"], "cache_mode": o.cache.as_str(), "state": out.result["state"], "blocks": out.result["blocks"],
        "runtime": out.result["runtime"], "repository": out.result["repository"],
        "record_binding": record_binding, "remediation": remediation, "failure_memory": failure_memory,
        "qualification": o.qualification,
    }))
}

/// **The task-close health gate (integration point for `orchestration::tasks::close`, WS-5).** One call covering
/// the health duties of a close, in order:
///
/// 1. **G0** — `scheduler::guard("task.close", touched)`: an active hard-block governing the touched paths refuses;
/// 2. **G2 re-check** — stale evidence is re-checked before the close may rely on it (Contract v3:111). For a
///    governance-affecting task every stale suite check is re-executed (the rest are served from the cache) and a
///    governance-suite record is written when that re-establishes currency; otherwise the G2 checks run;
/// 3. **O4** — `currency::enforce_close`: governance-affecting work (by class or by governed inputs touched) cannot
///    close on stale or absent green evidence (`force` records the degradation instead);
/// 4. **O1/U** — `product::enforce_close`: the test outcome comes from recorded per-family evidence, not the report.
///
/// `touched` must be the union of the report's `files_changed` and the mutations observed since the claim.
/// Returns the notes to record as `degraded` on the report, and the G2 health result id.
pub fn close_gate(
    p: &Project,
    task: &Value,
    report: &Value,
    touched: &[String],
    force: bool,
) -> Result<Value> {
    scheduler::guard(p, scheduler::catalogue::ops::TASK_CLOSE, touched)?;
    let (affecting, reasons) = currency::governance_affecting(task, touched);
    let id = task["id"].as_str().unwrap_or("?");
    let mut o = RunOptions::new(Tier::G2, scheduler::Trigger::task_close(id, touched));
    o.surface = "task.close".into();
    if affecting {
        o.selection = Selection::All;
    }
    let g2 = audit_with(p, &o)?;
    let mut degraded = currency::enforce_close(p, task, touched, force)?;
    degraded.extend(product::enforce_close(p, task, report, touched)?);
    Ok(
        json!({"allowed": true, "governance_affecting": affecting, "reasons": reasons, "g2": {"health_result": g2["health_result"], "verdict": g2["verdict"], "record": g2["audit"], "summary": g2["summary"]}, "degraded": degraded}),
    )
}

/// `gov verify product`: run every product test family this project can run and record the results as governed,
/// freshness-bound evidence (see [`product`]). A failing family is returned as `PRODUCT_TESTS_FAILED`.
pub fn product_suite(p: &Project) -> Result<Value> {
    product::run(p, &[])
}
