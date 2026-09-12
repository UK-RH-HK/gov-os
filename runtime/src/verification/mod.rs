//! Governance verification suite (framework §63-64) producing a governed audit record whose green status is tied
//! to an inputs hash (a green record becomes stale when suite inputs change).
use crate::memory::db::RuntimeDb;
use crate::memory::manifest::freshness;
use crate::records::{new_record, save_record, RecordStore};
use crate::util::{hash_tree, hash_value, now_iso, read_yaml};
use crate::{graph, Project, Result};
use serde_json::{json, Value};

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
];

/// Hash of inputs relevant to the governance suite: kernel, overlay, governance tests, decisions.
pub fn inputs_hash(p: &Project) -> String {
    let mut parts = vec![];
    for sub in [
        "governance/kernel",
        "governance/project",
        "governance/tests",
        "spec/decisions",
        "governance/framework.lock",
    ] {
        let path = p.root.join(sub);
        if path.is_dir() {
            parts.push(json!({sub: hash_tree(&path, &[]).map(|(h, _)| h).unwrap_or_default()}));
        } else if path.is_file() {
            parts.push(json!({sub: crate::util::sha256_file(&path).unwrap_or_default()}));
        }
    }
    hash_value(&json!(parts))
}

pub fn latest_green(p: &Project) -> Option<Value> {
    let store = RecordStore::load(&p.root);
    let mut audits: Vec<&crate::records::Record> = store
        .of_type("audit")
        .into_iter()
        .filter(|a| {
            a.data["green"].as_bool().unwrap_or(false) && a.get("scope") == "governance-suite"
        })
        .collect();
    audits.sort_by_key(|a| a.id());
    audits.last().map(|a| a.data.clone())
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

pub fn run(p: &Project, opts: &SuiteOptions) -> Result<Vec<Family>> {
    let pol = p.policies();
    let want = pol.get_list("TEST_POLICY", "governance_families");
    let db_exists = p.db_path().exists();
    let db = if db_exists {
        Some(RuntimeDb::open(&p.db_path())?)
    } else {
        None
    };
    let store = RecordStore::load(&p.root);
    let mut out = vec![];
    for fam in want {
        if !opts.families.is_empty() && !opts.families.contains(&fam) {
            continue;
        }
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
                    f.detail = json!({"dangling": d.len(), "orphans": o.len(), "edge_types": graph::edge_type_counts(db)?});
                } else {
                    f.findings.push(finding(
                        "medium",
                        &fam,
                        "runtime DB missing; run gov rebuild-memory".into(),
                        None,
                    ));
                }
                let dag = crate::orchestration::dag::compute(p)?;
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
                    f.detail = json!({"status": r["status"], "recall_at_k": r["recall_at_k"], "mrr": r["mrr"], "precision_at_k": r["precision_at_k"], "queries": r["queries"], "pending": r["pending_queries"], "failed": r["results"].as_array().map(|a| a.iter().filter(|x| !x["pass"].as_bool().unwrap_or(false)).map(|x| x["id"].clone()).collect::<Vec<_>>())});
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
                let roles = read_yaml(&p.kernel_dir().join("roles").join("ROLES.yaml"))
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
                for (abs, rel) in crate::paths::iter_repo_files(&p.root, false) {
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
                f.detail = json!({"unmatched": unknown, "secret_content_outside_secret_class": secrets_wrong});
            }
            "context_reproducibility" => {
                if let Some(db) = &db {
                    if let Some(t) = store.of_type("task").first() {
                        let a = crate::context::compile(p, db, &t.id())?;
                        let b = crate::context::compile(p, db, &t.id())?;
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
                for pr in crate::skills::validate_all(p) {
                    f.findings.push(finding("medium", &fam, pr, None));
                }
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
                f.detail = json!({"tasks": tasks.len(), "done": done.len(), "task_traceability": pct, "features": features.len()});
            }
            "audit_reproducibility" => {
                f.detail = json!({"note": "result hash compared across two consecutive in-process runs by `gov audit` (see audit record result_hash)"});
            }
            other => {
                f.findings.push(finding(
                    "low",
                    other,
                    "unknown governance family in TEST_POLICY".into(),
                    None,
                ));
            }
        }
        f.ok = !f.findings.iter().any(|x| {
            matches!(
                x["severity"].as_str(),
                Some("critical") | Some("high") | Some("medium")
            )
        });
        out.push(f);
    }
    Ok(out)
}

fn result_hash(fams: &[Family]) -> String {
    hash_value(&json!(fams
        .iter()
        .map(|f| json!({"id": f.id, "ok": f.ok, "findings": f.findings}))
        .collect::<Vec<_>>()))
}

/// Run the suite (twice for reproducibility), write an audit record, return verdict.
pub fn audit(p: &Project, opts: &SuiteOptions, persist: bool) -> Result<Value> {
    let fams = run(p, opts)?;
    let h1 = result_hash(&fams);
    let fams2 = run(
        p,
        &SuiteOptions {
            deep: false,
            families: opts.families.clone(),
        },
    )?;
    let h2 = result_hash(&fams2);
    let mut findings: Vec<Value> = vec![];
    let mut n = 0;
    for f in &fams {
        for x in &f.findings {
            n += 1;
            let mut y = x.clone();
            y["id"] = json!(format!("GF-{n:04}"));
            if y["path"].is_null() {
                y.as_object_mut().unwrap().remove("path");
            }
            findings.push(y);
        }
    }
    let reproducible = h1 == h2 || opts.deep;
    if !reproducible {
        findings.push(json!({"id": format!("GF-{:04}", n + 1), "severity": "high", "family": "audit_reproducibility", "message": "governance suite results differ between two consecutive runs"}));
    }
    let has = |sev: &str| findings.iter().any(|x| x["severity"].as_str() == Some(sev));
    let verdict = if has("critical") || has("high") {
        "UNHEALTHY"
    } else if has("medium") {
        "DEGRADED"
    } else {
        "HEALTHY"
    };
    let green = verdict == "HEALTHY";
    let families: serde_json::Map<String, Value> = fams
        .iter()
        .map(|f| {
            (
                f.id.clone(),
                json!({"ok": f.ok, "findings": f.findings.len(), "detail": f.detail}),
            )
        })
        .collect();
    let ih = inputs_hash(p);
    let mut id = String::new();
    if persist {
        let store = RecordStore::load(&p.root);
        id = store.next_id("audit");
        let rec = new_record(
            "audit",
            &id,
            &format!("Governance suite audit {id} ({verdict})"),
            json!({"scope": "governance-suite", "auditor_role": p.role, "session": p.session_id, "families": families, "findings": findings, "verdict": verdict, "inputs_hash": ih, "result_hash": h1, "green": green, "state_class": "EVIDENCE", "run_at": now_iso(), "deep": opts.deep}),
        );
        save_record(&p.root, &rec)?;
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
    Ok(
        json!({"audit": id, "verdict": verdict, "green": green, "families": families, "findings": findings, "inputs_hash": ih, "result_hash": h1, "reproducible": reproducible, "counts": {"critical": findings.iter().filter(|x| x["severity"] == "critical").count(), "high": findings.iter().filter(|x| x["severity"] == "high").count(), "medium": findings.iter().filter(|x| x["severity"] == "medium").count(), "low": findings.iter().filter(|x| x["severity"] == "low").count()}}),
    )
}

/// Run the product test command declared in PROJECT_POLICY (or detected ecosystem) and record evidence.
pub fn product_suite(p: &Project) -> Result<Value> {
    let pp = p.project_policy();
    let mut cmd: Vec<String> = pp["tests"]["product_test_command"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default();
    let mut source = "PROJECT_POLICY.tests.product_test_command".to_string();
    if cmd.is_empty() {
        let eco = crate::capabilities::ecosystems::detect(&p.root, &[p.contract().root("product")]);
        if let Some(e) = eco["ecosystems"].as_array().and_then(|a| {
            a.iter()
                .find(|e| e["test"].is_object() && e["available"].as_bool().unwrap_or(false))
        }) {
            cmd = e["test"]["command"]
                .as_array()
                .unwrap()
                .iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect();
            source = format!("ecosystem:{}", e["id"].as_str().unwrap_or(""));
            if let Some(d) = e["dir"].as_str() {
                if !d.is_empty() {
                    return run_product_cmd(p, &cmd, &p.root.join(d), &source);
                }
            }
        }
    }
    if cmd.is_empty() {
        return Ok(
            json!({"ran": false, "reason": "no product test command configured or detectable (capability gap)", "status": "not_applicable_with_reason"}),
        );
    }
    run_product_cmd(p, &cmd, &p.root, &source)
}

fn run_product_cmd(
    p: &Project,
    cmd: &[String],
    cwd: &std::path::Path,
    source: &str,
) -> Result<Value> {
    let (code, out, err) = crate::util::run_cmd(cmd, cwd)?;
    let status = if code == 0 { "passed" } else { "failed" };
    let ev = json!({"ran": true, "command": cmd, "cwd": cwd.to_string_lossy(), "source": source, "exit": code, "status": status, "stdout_tail": out.lines().rev().take(20).collect::<Vec<_>>().into_iter().rev().collect::<Vec<_>>().join("\n"), "stderr_tail": err.lines().rev().take(20).collect::<Vec<_>>().into_iter().rev().collect::<Vec<_>>().join("\n"), "at": now_iso()});
    crate::observability::emit(p, "product.suite", ev.clone())?;
    Ok(ev)
}
