//! `gov doctor`: deterministic health checks with remediation. HEALTHY / DEGRADED / UNHEALTHY (framework §76).
use crate::kernel::{manifest_hash, verify_kernel};
use crate::lock::compatibility;
use crate::memory::db::RuntimeDb;
use crate::memory::manifest::freshness;
use crate::migrations::classify::legacy_mechanisms;
use crate::orchestration::{claims, control, gates};
use crate::records::RecordStore;
use crate::util::read_text;
use crate::{Project, Result, CLI_VERSION};
use serde_json::{json, Value};

pub struct Check {
    pub id: &'static str,
    pub name: &'static str,
    pub severity: &'static str,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct Report {
    pub verdict: String,
    pub checks: Vec<Value>,
    pub failed: usize,
    pub remediation: Vec<String>,
    pub framework_version: String,
    pub cli_version: String,
    pub root: String,
    /// `OWNER-DECISION-0006` §6 bullet 7: this machine's break-glass posture, carried beside `framework_version`
    /// and `verdict` (`AR31-B1`).
    ///
    /// **`verdict` and `release_trust.below_floor` are different predicates and must not be read as one.**
    /// `doctor`'s own `DEGRADED` verdict means "medium or low severity checks failed" — the word an operator
    /// scans for was already taken by an unrelated meaning, which is why this is a separate field rather than a
    /// verdict value. `release_trust.below_floor` is `true` when the machine carries the
    /// `DEGRADED — RECOVERY ONLY` marking, read through `crate::srr::breakglass` at the one §6 bullet 7 sink.
    /// A machine can be HEALTHY on every check and still be below floor; before this field it reported exactly
    /// that, with nothing to say so.
    pub release_trust: Value,
    /// The persisted health result of this run (`.governance-runtime/health/results/<id>.json`): tier, checks,
    /// inputs, runtime identity, repository state, actor and time (Contract v3:808), and the resulting health state.
    pub health_result: Value,
}

fn chk(
    id: &str,
    name: &str,
    ok: bool,
    severity: &str,
    message: String,
    remediation: Option<&str>,
) -> Value {
    let enforcement = crate::scheduler::catalogue::get(id)
        .map(crate::scheduler::catalogue::enforcement)
        .unwrap_or(json!({"mode": "warning", "refuses": []}));
    json!({"id": id, "name": name, "ok": ok, "severity": if ok { "info" } else { severity }, "message": message, "remediation": remediation, "enforcement": enforcement})
}

/// Canonical report order (the historical order, then the checks added later).
const ORDER: &[&str] = &[
    "D001", "D002", "D003", "D004", "D005", "D006", "D007", "D029", "D027", "D028", "D008", "D009",
    "D010", "D011", "D012", "D025", "D026", "D013", "D014", "D015", "D016", "D017", "D018", "D019",
    "D020", "D021", "D030", "D031", "D032", "D033", "D034", "D035", "D022", "D023", "D024",
];

fn order_of(c: &Value) -> usize {
    let id = c["id"].as_str().unwrap_or("");
    ORDER.iter().position(|x| *x == id).unwrap_or(ORDER.len())
}

pub fn run(p: &Project) -> Result<Report> {
    let mut checks = vec![];
    // D001 lock
    let lock_ok = p.lock_path().exists();
    checks.push(chk(
        "D001",
        "framework.lock present",
        lock_ok,
        "critical",
        if lock_ok {
            "present".into()
        } else {
            "missing".into()
        },
        Some("gov init / gov adopt"),
    ));
    if !lock_ok {
        return Ok(Report {
            verdict: "UNHEALTHY".into(),
            checks,
            failed: 1,
            remediation: vec!["gov init / gov adopt".into()],
            framework_version: String::new(),
            cli_version: CLI_VERSION.into(),
            root: p.root.display().to_string(),
            release_trust: crate::srr::present::presentation("doctor"),
            health_result: Value::Null,
        });
    }
    // G1 first (BC-P2-07): the mutations made since the last observation are observed and their G1 checks run, so the
    // repository verdict (D035) reads suite outcomes that include them
    let _ = crate::scheduler::observe(p);
    // Independent check groups run concurrently, each on its own project handle and database connection
    // (Contract v3:803). Every group is a pure reader of the live repository. Kernel trust is resolved once here, before
    // the groups start, so an embedded-baseline substitution is never materialised by two threads at once (see
    // `scheduler::run_suite`).
    let _ = crate::kernel_trust::trust(&p.root);
    let root = p.root.clone();
    let (session, role) = (p.session_id.clone(), p.role.clone());
    type Group = fn(&Project) -> Result<Vec<Value>>;
    let groups: [(&str, Group); 4] = [
        ("kernel-policy", group_kernel_policy),
        ("derived-runtime", group_runtime),
        ("tree-scan", group_tree),
        ("records-state", group_records_state),
    ];
    let (results, snap): (
        Vec<Result<Vec<Value>>>,
        Result<crate::verification::currency::Snapshot>,
    ) = std::thread::scope(|s| {
        let handles: Vec<_> = groups
            .iter()
            .map(|(name, f)| {
                let (root, session, role, f) = (&root, &session, &role, *f);
                std::thread::Builder::new()
                    .name(format!("gov-doctor-{name}"))
                    .spawn_scoped(s, move || {
                        let gp = Project::open(root)
                            .with_session(Some(session.clone()), Some(role.clone()));
                        f(&gp)
                    })
            })
            .collect();
        // the currency/health group runs here, on this thread, with the one input snapshot of this run
        let snap = crate::verification::currency::Snapshot::take(p);
        let own = match &snap {
            Ok(sn) => group_currency_health(p, sn),
            Err(e) => Err(e.clone()),
        };
        let mut out: Vec<Result<Vec<Value>>> = handles
            .into_iter()
            .map(|h| match h {
                Ok(h) => h.join().unwrap_or_else(|_| {
                    Err(crate::GovError::new(
                        "DOCTOR_GROUP_PANIC",
                        "a doctor check group panicked",
                    ))
                }),
                Err(e) => Err(crate::GovError::io("spawn doctor group", e)),
            })
            .collect();
        out.push(own);
        (out, snap)
    });
    for r in results {
        checks.extend(r?);
    }
    let snap = snap?;
    // D035 — the repository verdict (Contract v3:995-1008; BC-P2-44): the thirteen HEALTHY conditions from this run's
    // checks and the latest suite outcomes, and every Gate U SLO against its threshold
    checks.push(check_repository_healthy(p, &checks, &snap));
    checks.sort_by_key(order_of);
    let rem: Vec<String> = checks
        .iter()
        .filter(|c| !c["ok"].as_bool().unwrap_or(true))
        .filter_map(|c| c["remediation"].as_str().map(|s| s.to_string()))
        .collect();
    let failed = checks
        .iter()
        .filter(|c| !c["ok"].as_bool().unwrap_or(true))
        .count();
    let worst = checks
        .iter()
        .filter(|c| !c["ok"].as_bool().unwrap_or(true))
        .map(|c| c["severity"].as_str().unwrap_or("low"))
        .fold("none", |acc, s| {
            let rank = |x: &str| match x {
                "critical" => 4,
                "high" => 3,
                "medium" => 2,
                "low" => 1,
                _ => 0,
            };
            if rank(s) > rank(acc) {
                s
            } else {
                acc
            }
        })
        .to_string();
    let verdict = match worst.as_str() {
        "critical" | "high" => "UNHEALTHY",
        "medium" | "low" => "DEGRADED",
        _ => "HEALTHY",
    };
    let mut report = Report {
        verdict: verdict.into(),
        checks,
        failed,
        remediation: rem,
        framework_version: p.framework_version(),
        cli_version: CLI_VERSION.into(),
        root: p.root.display().to_string(),
        release_trust: crate::srr::present::presentation("doctor"),
        health_result: Value::Null,
    };
    // health-result provenance (Contract v3:808): every doctor run is recorded, and the hard-blocks its checks
    // declare are refreshed for the G0 guard
    report.health_result = crate::scheduler::record_doctor(
        p,
        &json!({"verdict": report.verdict, "checks": report.checks}),
        Some(&snap),
    )
    .unwrap_or_else(|e| json!({"error": e.code, "message": e.message}));
    Ok(report)
}

fn group_kernel_policy(p: &Project) -> Result<Vec<Value>> {
    let mut checks = vec![];
    let mut add = |c: Value| checks.push(c);
    let lock = p.lock()?.clone();
    let lerr = p
        .schemas()
        .errors("framework-lock", &lock)
        .unwrap_or_default();
    add(chk(
        "D002",
        "framework.lock schema",
        lerr.is_empty(),
        "high",
        if lerr.is_empty() {
            "valid".into()
        } else {
            lerr.join("; ")
        },
        Some("gov update --apply (migration) or repair lock"),
    ));
    // D003 kernel integrity
    match verify_kernel(&p.kernel_dir()) {
        Ok(v) => {
            add(chk(
                "D003",
                "kernel payload integrity",
                v.ok,
                "critical",
                if v.ok {
                    format!("intact ({})", v.version)
                } else {
                    format!(
                        "modified={:?} missing={:?} added={:?}",
                        v.modified, v.missing, v.added
                    )
                },
                Some("gov kernel reinstall --source <release> (kernel is immutable, INV-007)"),
            ));
        }
        Err(e) => add(chk(
            "D003",
            "kernel payload integrity",
            false,
            "critical",
            e.to_string(),
            Some("gov kernel reinstall --source <release>"),
        )),
    }
    let mh_ok = p
        .kernel_manifest()
        .map(|m| manifest_hash(m) == lock["kernel_manifest_hash"].as_str().unwrap_or(""))
        .unwrap_or(false);
    add(chk(
        "D004",
        "lock matches kernel manifest",
        mh_ok,
        "critical",
        if mh_ok {
            "match".into()
        } else {
            "framework.lock kernel_manifest_hash != installed kernel".into()
        },
        Some("gov update --apply or gov kernel reinstall"),
    ));
    let comp = compatibility(lock["version"].as_str().unwrap_or("0"), CLI_VERSION);
    add(chk(
        "D005",
        "CLI/kernel compatibility",
        comp.compatible && !comp.warning,
        if comp.compatible {
            "medium"
        } else {
            "critical"
        },
        comp.reason.clone(),
        Some("gov update --check"),
    ));
    // D006 overlay + policies
    let ov = p.overlay();
    add(chk(
        "D006",
        "project overlay",
        ov.problems.is_empty(),
        "high",
        if ov.problems.is_empty() {
            "7 overlay files valid".into()
        } else {
            ov.problems.join("; ")
        },
        Some("repair governance/project/*.yaml against kernel schemas"),
    ));
    let pol = p.policies();
    add(chk(
        "D007",
        "policies",
        pol.problems.is_empty(),
        "high",
        if pol.problems.is_empty() {
            format!(
                "{} policies loaded, {} overrides",
                pol.effective.len(),
                pol.applied_overrides.len()
            )
        } else {
            pol.problems.join("; ")
        },
        Some("repair policy overrides/exceptions"),
    ));
    // D029 constitutional policy source: enforcement must consume a kernel authenticated against the release identity
    let kt = crate::kernel_trust::trust(&p.root);
    add(chk(
        "D029",
        "constitutional policy read from a verified kernel",
        kt.verified,
        "critical",
        kt.summary(),
        Some("gov kernel verify; gov kernel reinstall (or `gov kernel override --reason ...` as an L4+ role, which raises a gate)"),
    ));
    // D032 installation authenticity (BC-P2-36; WS-8 IP-1): an installation whose release authenticity is not
    // established fails (medium), so the doctor verdict is never HEALTHY without disclosing it
    let mut d032 = crate::srr::installation::doctor_check(&p.root, "D032");
    d032["enforcement"] = crate::scheduler::catalogue::get("D032")
        .map(crate::scheduler::catalogue::enforcement)
        .unwrap_or(json!({"mode": "warning", "refuses": []}));
    add(d032);
    // D027 constitutional precedence: refused overrides/exceptions are a CRITICAL finding (verifier H-N1)
    let refused = pol.refused_overrides.len();
    add(chk("D027", "policy precedence respected (no override weakens security/authority/gate floors)", refused == 0, "critical", if refused == 0 { format!("{} override(s) applied within POLICY_PRECEDENCE; rules from {}", pol.applied_overrides.len(), pol.precedence.as_ref().and_then(|v| v["source"].as_str()).unwrap_or("?")) } else { format!("{refused} refused: {}", pol.refused_overrides.iter().map(|r| format!("{}.{} ({})", r["policy"].as_str().unwrap_or(""), r["key"].as_str().unwrap_or(""), r["reason"].as_str().unwrap_or(""))).collect::<Vec<_>>().join("; ")) }, Some("remove the weakening override from governance/project/PROJECT_POLICY.yaml or PROJECT_EXCEPTIONS.yaml; only strengthening overrides are applied")));
    // D028 plugin governance: invalid descriptors, denied/pinned plugins, pin drift (verifier H-N2)
    let pf = crate::capabilities::governance::findings(p);
    let high: Vec<&Value> = pf.iter().filter(|f| f["severity"] == "high").collect();
    add(chk("D028", "capability plugins governed (schema-valid, registered, pinned, authorised)", pf.is_empty(), if high.is_empty() { "medium" } else { "high" }, if pf.is_empty() { "no plugin problems".into() } else { pf.iter().map(|f| f["message"].as_str().unwrap_or("").to_string()).collect::<Vec<_>>().join("; ") }, Some("gov plugins list; fix or register the descriptor (gov plugins register --descriptor <file>)")));
    let fj = p.root.join("framework.json");
    let fj_ok = fj.exists()
        && crate::util::read_json(&fj)
            .map(|v| {
                v == p
                    .contract()
                    .to_framework_json(crate::FRAMEWORK_NAME, &p.framework_version())
            })
            .unwrap_or(false);
    add(chk(
        "D008",
        "framework.json in sync with repository contract",
        fj_ok,
        "medium",
        if fj_ok {
            "in sync".into()
        } else {
            "missing or stale".into()
        },
        Some("gov adapters generate"),
    ));
    Ok(checks)
}

fn group_runtime(p: &Project) -> Result<Vec<Value>> {
    let mut checks = vec![];
    let mut add = |c: Value| checks.push(c);
    // D009 runtime
    let db_path = p.db_path();
    let (runtime_ok, runtime_msg, db) = if !db_path.exists() {
        (false, "derived runtime absent".to_string(), None)
    } else {
        match RuntimeDb::open(&db_path) {
            Ok(d) => {
                let ok = d.has_schema() && d.integrity_ok();
                (
                    ok,
                    if ok {
                        format!("state.db ok ({} artefacts)", d.count("artifacts"))
                    } else {
                        "state.db corrupt or schemaless".into()
                    },
                    Some(d),
                )
            }
            Err(e) => (false, e.to_string(), None),
        }
    };
    add(chk(
        "D009",
        "derived runtime",
        runtime_ok,
        if db_path.exists() { "high" } else { "medium" },
        runtime_msg,
        Some("gov rebuild-memory"),
    ));
    let scanner = p.secret_scanner();
    if let Some(d) = &db {
        let leaked = d
            .query("SELECT chunk_id, text FROM chunks", &[])
            .unwrap_or_default()
            .into_iter()
            .filter(|r| {
                !scanner
                    .scan_text(r["text"].as_str().unwrap_or(""), "c")
                    .is_empty()
            })
            .count();
        let sec_art = d.count_where("artifacts", "path_class='secret'");
        add(chk(
            "D012",
            "no secrets in index",
            leaked == 0 && sec_art == 0,
            "critical",
            if leaked == 0 && sec_art == 0 {
                "clean".into()
            } else {
                format!("{leaked} chunk(s) with secret patterns, {sec_art} secret-class artefact(s) indexed (INV-009)")
            },
            Some("gov rebuild-memory (fail-closed re-index) and rotate the exposed secret"),
        ));
    }
    // D025 semantic index consistent with the pinned embedder/reranker (no mixed-embedder index)
    if let Some(d) = &db {
        let groups = d
            .query(
                "SELECT embedder, dim, COUNT(*) AS n FROM vectors GROUP BY embedder, dim",
                &[],
            )
            .unwrap_or_default();
        let live = crate::memory::indexer::live_pins(d);
        let expected = crate::memory::indexer::expected_pins(p);
        let diffs = crate::memory::indexer::pin_differences(&expected, &live);
        let rr_ok = live["reranker"].get("provider") == expected["reranker"].get("provider");
        let mixed = groups.len() > 1;
        let ok = !mixed && diffs.is_empty() && rr_ok;
        let msg = if mixed {
            format!(
                "heterogeneous semantic index: {} embedder/dimension groups {:?}",
                groups.len(),
                groups
                    .iter()
                    .map(|g| format!("{}@{}d×{}", g["embedder"], g["dim"], g["n"]))
                    .collect::<Vec<_>>()
            )
        } else if !diffs.is_empty() {
            format!("index pins differ from policy: {}", diffs.join("; "))
        } else if !rr_ok {
            format!(
                "reranker pinned as {} but index built with {}",
                expected["reranker"]["provider"], live["reranker"]["provider"]
            )
        } else {
            format!(
                "consistent: {} ({} vectors)",
                live["embedder"]["id"].as_str().unwrap_or("?"),
                groups
                    .first()
                    .map(|g| g["n"].as_i64().unwrap_or(0))
                    .unwrap_or(0)
            )
        };
        // WS-6 IP-R2-3: the embedding runtime the index was built with is the one that would run now (machine-local
        // drift is invisible to the manifest core), and the live retrieval profile is governed
        let mut drift: Option<String> = None;
        let governed = crate::capabilities::governance::plugin_set(p);
        let spec = crate::memory::embedder::EmbedSpec::from_policy(p);
        if let (Ok(emb), Some(rec)) = (
            crate::memory::embedder::Embedder::resolve(&spec, &governed),
            d.get_meta("embedder_identity"),
        ) {
            let cur = crate::memory::profile::embedder_identity(p, &emb, Some(&rec));
            if rec["runtime_digest"].as_str() != Some(cur.runtime_digest.as_str()) {
                drift = Some(format!(
                    "the embedding runtime changed since the index was built (recorded {}, now {}): vectors are not comparable with what would embed a query",
                    rec["runtime_digest"].as_str().map(|h| &h[..h.len().min(12)]).unwrap_or("unrecorded"),
                    &cur.runtime_digest[..cur.runtime_digest.len().min(12)]
                ));
            }
        }
        let prof = crate::memory::profile::status(p);
        let prof_problem = (prof["governed"] != true).then(|| {
            (
                prof["severity"].as_str().unwrap_or("medium").to_string(),
                format!(
                    "retrieval profile {}: {}",
                    prof["state"].as_str().unwrap_or("?"),
                    prof["message"].as_str().unwrap_or("")
                ),
            )
        });
        let ok_all = ok && drift.is_none() && prof_problem.is_none();
        let sev = if mixed {
            "critical".to_string()
        } else if !ok || drift.is_some() {
            "high".to_string()
        } else {
            prof_problem
                .as_ref()
                .map(|(s, _)| s.clone())
                .unwrap_or_else(|| "high".into())
        };
        let mut full = msg;
        if let Some(dr) = &drift {
            full.push_str(&format!("; {dr}"));
        }
        if let Some((_, m)) = &prof_problem {
            full.push_str(&format!("; {m}"));
        }
        let mut c = chk("D025", "semantic index consistent with pinned embedder/reranker; retrieval profile governed; embedding runtime unchanged", ok_all, &sev, full, Some("gov rebuild-memory (full rebuild re-embeds every chunk with the pinned implementation); govern a profile change with gov memory benchmark + gov memory select"));
        c["retrieval_profile"] = json!({"state": prof["state"], "governed": prof["governed"], "decision": prof["decision"]});
        add(c);
    }
    // D026 claims store (deterministic concurrency state outside the derived index)
    // WS-6 IP-R2-12: the store actually in use, and every non-rebuildable OS store still kept inside the derived
    // runtime or generated-views directory (disclosed: lost if that directory is deleted; the audit reports it through
    // `recovery_rebuild`; each writer relocates its store, `paths::relocate_legacy`)
    let misplaced = crate::paths::misplaced_os_state(&p.root);
    let misplaced_note = if misplaced.is_empty() {
        String::new()
    } else {
        format!(
            "; non-rebuildable OS state inside a derived directory: {}",
            misplaced
                .iter()
                .map(|m| format!(
                    "{} at {} (belongs at {})",
                    m["store"].as_str().unwrap_or("?"),
                    m["found_at"].as_str().unwrap_or("?"),
                    m["belongs_at"].as_str().unwrap_or("?")
                ))
                .collect::<Vec<_>>()
                .join(", ")
        )
    };
    match crate::memory::claims::ClaimsStore::open(p) {
        Ok(cs) => {
            let ok = cs.integrity_ok();
            let mut c = chk(
                "D026",
                "claims store present and intact",
                ok,
                "high",
                if ok {
                    format!("{}{misplaced_note}", cs.path.display())
                } else {
                    format!("claims.db corrupt{misplaced_note}")
                },
                Some("restore claims.db or gov claims sweep"),
            );
            c["misplaced_os_state"] = json!(misplaced);
            add(c);
        }
        Err(e) => add(chk(
            "D026",
            "claims store present and intact",
            false,
            "high",
            e.to_string(),
            Some("check .governance-runtime permissions"),
        )),
    }
    // D014 contradictions
    let store = RecordStore::load(&p.root);
    let conflicts = db
        .as_ref()
        .and_then(|d| d.get_meta("supersession_conflicts"))
        .and_then(|v| v.as_array().cloned())
        .unwrap_or_default();
    let dups = store.duplicates.len();
    let mut d014 = chk(
        "D014",
        "authority unambiguous (no supersession conflicts / duplicate ids)",
        conflicts.is_empty() && dups == 0,
        "high",
        format!(
            "{} supersession conflict(s), {} duplicate id(s)",
            conflicts.len(),
            dups
        ),
        Some("resolve via CIT: set superseded records to SUPERSEDED; remove duplicate ids"),
    );
    let mut subj: Vec<String> = vec![];
    for c in &conflicts {
        collect_ids(c, &mut subj);
    }
    for (id, paths) in &store.duplicates {
        subj.push(id.clone());
        subj.extend(paths.iter().cloned());
    }
    subj.sort();
    subj.dedup();
    d014["subjects"] = json!(subj);
    add(d014);
    // D015 graph (WS-6 IP-R2-1): the relationship graph through memory::integrity (orphan, dangling, stale, reversed,
    // ill-typed relationships, supersession cycles), records outside their canonical location (W1) and stale lineage
    // links of current work (W8) — each named. Fails on any finding above low. The AFFECTS link of a generated
    // investigation whose subject was retired is not a defect (O-1) and is listed apart.
    if let Some(d) = &db {
        let orph = crate::graph::orphan_nodes(d).unwrap_or_default();
        let misplaced = crate::graph::identity::misplaced_records(Some(p), &store);
        let stale = crate::verification::reporting::current_stale_links(&store);
        let mut named: Vec<String> = vec![];
        let mut resolved = 0usize;
        let mut counts: std::collections::BTreeMap<String, usize> =
            std::collections::BTreeMap::new();
        let mut failing = 0usize;
        let mut worst = "low";
        let mut subjects: Vec<String> = vec![];
        match crate::memory::integrity::check(p, &store, Some(d)) {
            Ok(gi) => {
                for x in &gi.findings {
                    let (src, et, dst) = (
                        x["edge"]["src"].as_str().unwrap_or(""),
                        x["edge"]["type"].as_str().unwrap_or(""),
                        x["edge"]["dst"].as_str().unwrap_or(""),
                    );
                    if x["kind"] == "dangling"
                        && crate::verification::lineage::is_resolved_investigation_edge(
                            p, &store, src, et, dst,
                        )
                    {
                        resolved += 1;
                        continue;
                    }
                    let kind = x["kind"].as_str().unwrap_or("?").to_string();
                    *counts.entry(kind.clone()).or_insert(0) += 1;
                    let sev = x["severity"].as_str().unwrap_or("medium");
                    if sev != "low" {
                        failing += 1;
                        if sev == "high" || sev == "critical" {
                            worst = "high";
                        } else if worst == "low" {
                            worst = "medium";
                        }
                        named.push(format!("{kind}: {}", x["message"].as_str().unwrap_or("")));
                        for v in [src, dst] {
                            if !v.is_empty() {
                                subjects.push(v.trim_start_matches("file:").to_string());
                            }
                        }
                    }
                }
            }
            Err(e) => {
                failing += 1;
                worst = "medium";
                named.push(format!(
                    "graph integrity could not be checked: {}",
                    e.message
                ));
            }
        }
        let list = |v: Vec<String>| -> String {
            let n = v.len();
            let mut s = v.into_iter().take(8).collect::<Vec<_>>().join("; ");
            if n > 8 {
                s.push_str(&format!(" (+{} more)", n - 8));
            }
            s
        };
        let ok = failing == 0 && misplaced.is_empty() && stale.is_empty();
        if (!misplaced.is_empty() || !stale.is_empty()) && worst == "low" {
            worst = "medium";
        }
        let mut msg = format!("{failing} relationship finding(s) above low {:?}", counts);
        if !named.is_empty() {
            msg.push_str(&format!(" [{}]", list(named)));
        }
        msg.push_str(&format!(", {} orphan record(s)", orph.len()));
        if !misplaced.is_empty() {
            msg.push_str(&format!(
                ", {} record(s) outside their canonical location [{}]",
                misplaced.len(),
                list(
                    misplaced
                        .iter()
                        .map(|m| format!(
                            "{} at {}",
                            m["id"].as_str().unwrap_or("?"),
                            m["path"].as_str().unwrap_or("?")
                        ))
                        .collect()
                )
            ));
        }
        if !stale.is_empty() {
            msg.push_str(&format!(
                ", {} stale lineage link(s) [{}]",
                stale.len(),
                list(
                    stale
                        .iter()
                        .map(|s| s["message"].as_str().unwrap_or("").to_string())
                        .collect()
                )
            ));
        }
        if resolved > 0 {
            msg.push_str(&format!(
                ", {resolved} link(s) of completed investigations to retired orphans (not defects)"
            ));
        }
        let mut c = chk(
            "D015",
            "graph integrity",
            ok,
            worst,
            msg,
            Some("fix references in records or add missing records; move misplaced records to their canonical directory; re-point or revalidate work linked to superseded records (through a CIT)"),
        );
        c["orphan_records"] = json!(orph);
        c["subjects"] = json!(subjects);
        add(c);
    }
    Ok(checks)
}

fn group_tree(p: &Project) -> Result<Vec<Value>> {
    let mut checks = vec![];
    let mut add = |c: Value| checks.push(c);
    let pol = p.policies();
    // D010 freshness
    let fr = freshness(p);
    add(chk(
        "D010",
        "index freshness",
        fr.manifest_present && fr.fresh && !fr.age_exceeded,
        "medium",
        if !fr.manifest_present {
            "no index manifest".into()
        } else if !fr.pin_mismatch.is_empty() {
            format!("pin mismatch: {}", fr.pin_mismatch.join("; "))
        } else if fr.age_exceeded {
            format!(
                "index older than MEMORY_POLICY.freshness.max_index_age_hours ({:.0} h)",
                fr.age_hours.unwrap_or(0.0)
            )
        } else if fr.fresh {
            format!("fresh ({} artefacts)", fr.checked)
        } else {
            format!(
                "stale: {} changed, {} added, {} removed",
                fr.stale.len(),
                fr.added.len(),
                fr.removed.len()
            )
        },
        Some("gov rebuild-memory (full when pins changed; --incremental otherwise)"),
    ));
    // D011 secrets outside secret class
    let contract = p.contract();
    let scanner = p.secret_scanner();
    let mut wrong = vec![];
    for (abs, rel) in crate::paths::iter_repo_files(&p.root, false) {
        let d = contract.decide(&rel);
        if d.is_secret() || scanner.path_is_secret(&rel) {
            continue;
        }
        if !scanner.scan_file(&abs, &rel).is_empty() {
            wrong.push(rel);
        }
    }
    let d011_sev = if pol.get_str(
        "SECURITY_POLICY",
        "on_secret_outside_secret_class",
        "block_index_and_report",
    ) == "block_index_and_report"
    {
        "critical"
    } else {
        "high"
    };
    let mut d011 = chk("D011", "secrets outside secret class", wrong.is_empty(), d011_sev, if wrong.is_empty() { "none".into() } else { format!("{} file(s) contain secret patterns but are not secret-class: {}", wrong.len(), wrong.join(", ")) }, Some("move to a secret-class path or add a secret rule in REPOSITORY_CONTRACT.yaml; indexing is blocked meanwhile"));
    // the files it names are the block's subjects: the work that moves or reclassifies them is its remedy
    d011["subjects"] = json!(wrong);
    add(d011);
    // D013 legacy mechanisms
    let store = RecordStore::load(&p.root);
    let legacy = legacy_mechanisms(&p.root);
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
    let unmarked: Vec<String> = legacy
        .iter()
        .filter(|l| !l.path.starts_with("archive/") && !registered.iter().any(|r| r == &l.path))
        .map(|l| l.path.clone())
        .collect();
    add(chk(
        "D013",
        "legacy governance mechanisms retired",
        unmarked.is_empty(),
        "high",
        if unmarked.is_empty() {
            format!(
                "{} legacy mechanism(s), all marked LEGACY/archived",
                legacy.len()
            )
        } else {
            format!("{} legacy mechanism(s) in the active tree without LEGACY registration (INV-004): {}", unmarked.len(), unmarked.join(", "))
        },
        Some("gov adopt (A2/A8) or register a LEGACY record / move to archive/"),
    ));
    // D022 ecosystems / capability gaps
    let db = if p.db_path().exists() {
        RuntimeDb::open(&p.db_path()).ok()
    } else {
        None
    };
    let eco = db
        .as_ref()
        .and_then(|d| d.get_meta("capability.ecosystems"))
        .unwrap_or_else(|| {
            crate::capabilities::ecosystems::detect(&p.root, &[contract.root("product")])
        });
    let gaps: Vec<String> = eco["ecosystems"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter(|e| !e["available"].as_bool().unwrap_or(true))
                .map(|e| {
                    format!(
                        "{} ({})",
                        e["id"].as_str().unwrap_or(""),
                        e["required_binary"].as_str().unwrap_or("")
                    )
                })
                .collect()
        })
        .unwrap_or_default();
    add(chk(
        "D022",
        "native toolchains for detected ecosystems",
        gaps.is_empty(),
        "low",
        if gaps.is_empty() {
            format!("{} ecosystem(s) detected, tools available", eco["count"])
        } else {
            format!("capability gap: {}", gaps.join(", "))
        },
        Some("install the native toolchain or raise a tooling task (never a crash)"),
    ));
    // D024 gitignore
    let gi = read_text(&p.root.join(".gitignore"))
        .map(|t| {
            t.lines()
                .any(|l| l.trim() == ".governance-runtime/" || l.trim() == ".governance-runtime")
        })
        .unwrap_or(false);
    add(chk(
        "D024",
        ".governance-runtime ignored by git",
        gi,
        "low",
        if gi {
            "ignored".into()
        } else {
            ".gitignore lacks .governance-runtime/".into()
        },
        Some("add .governance-runtime/ to .gitignore"),
    ));
    Ok(checks)
}

fn group_records_state(p: &Project) -> Result<Vec<Value>> {
    let mut checks = vec![];
    let mut add = |c: Value| checks.push(c);
    // D016 interrupted transactions
    let inter = crate::cit::interrupted(p);
    let mut inter_subjects: Vec<String> = vec![];
    for c in &inter {
        collect_ids(c, &mut inter_subjects);
    }
    add(with_subjects(
        chk(
            "D016",
            "no interrupted transactions",
            inter.is_empty(),
            "high",
            if inter.is_empty() {
                "none".into()
            } else {
                format!(
                    "{} CIT(s) left EXECUTING: {}",
                    inter.len(),
                    inter
                        .iter()
                        .map(|c| c["id"].as_str().unwrap_or("").to_string())
                        .collect::<Vec<_>>()
                        .join(", ")
                )
            },
            Some("gov recover (classifies and rolls back/finishes interrupted mutations)"),
        ),
        inter_subjects,
    ));
    // D017 claims
    {
        let cl = claims::list(p).unwrap_or_default();
        let exp = cl
            .iter()
            .filter(|c| c["expired"].as_bool().unwrap_or(false))
            .count();
        // name the store actually in use: a linked worktree shares its main worktree's store (WS-5 IP-7)
        let store_path = crate::memory::claims::ClaimsStore::path_for(p);
        let shown = store_path
            .strip_prefix(&p.root)
            .map(|r| r.display().to_string())
            .unwrap_or_else(|_| store_path.display().to_string());
        add(chk(
            "D017",
            "session claims",
            exp == 0,
            "low",
            format!(
                "{} claim(s), {exp} expired (claims store: {shown}, survives rebuilds)",
                cl.len()
            ),
            Some("gov claims sweep"),
        ));
    }
    // D018 control
    let ctl = control::state(p);
    let running =
        ctl["mode"].as_str() == Some("RUNNING") && !ctl["writes_frozen"].as_bool().unwrap_or(false);
    add(chk(
        "D018",
        "control state",
        running,
        "medium",
        format!(
            "mode {} writes_frozen {}",
            ctl["mode"], ctl["writes_frozen"]
        ),
        Some("gov resume (only after the reason for the pause/freeze is resolved)"),
    ));
    // D019 gates surfaced to the human (INV-008), with WS-3's presentation rule: `gov gate present` RENDERS the
    // decision package to the human channel; a gate is PRESENTED only on the owner's signed receipt or signed answer.
    // A gate never rendered exists only in files — the OS's duty is undone (fails). A rendered gate awaiting the
    // owner's receipt or answer is not yet evidenced as presented, but nothing is left for the OS to do: it is
    // reported, not failed (integration observation O-2).
    let pend = gates::pending(p);
    let id_of = |g: &Value| g["id"].as_str().unwrap_or("").to_string();
    let unrendered: Vec<String> = pend
        .iter()
        .filter(|g| {
            !g["rendered"].as_bool().unwrap_or(false)
                && !g["presented_in_chat"].as_bool().unwrap_or(false)
        })
        .map(id_of)
        .collect();
    let awaiting: Vec<String> = pend
        .iter()
        .filter(|g| {
            g["rendered"].as_bool().unwrap_or(false)
                && !g["presented_in_chat"].as_bool().unwrap_or(false)
        })
        .map(id_of)
        .collect();
    let presented = pend.len() - unrendered.len() - awaiting.len();
    let awaiting_note = if awaiting.is_empty() {
        String::new()
    } else {
        format!(
            "; {} rendered to the human channel and awaiting the owner's signed receipt or answer (not yet evidenced as presented): {}",
            awaiting.len(),
            awaiting.join(", ")
        )
    };
    add(chk(
        "D019",
        "human gates surfaced to the human (presented = owner-signed receipt or answer)",
        unrendered.is_empty(),
        "medium",
        if unrendered.is_empty() {
            format!(
                "{} pending gate(s): {presented} presented (owner-signed receipt or answer){awaiting_note}",
                pend.len()
            )
        } else {
            format!(
                "{} gate(s) never rendered to the human channel exist only in files and are not presented (INV-008): {}{awaiting_note}",
                unrendered.len(),
                unrendered.join(", ")
            )
        },
        Some("gov gate present <id> renders the decision package to the human channel; the gate is presented when the owner signs a receipt or an answer (`gov trust human-channel`)"),
    ));
    // D020 adapters
    let av =
        crate::adapters::verify(p).unwrap_or(json!({"ok": false, "problems": ["verify failed"]}));
    add(chk(
        "D020",
        "adapters current and conformant",
        av["ok"].as_bool().unwrap_or(false),
        "medium",
        if av["ok"].as_bool().unwrap_or(false) {
            format!("{} adapters verified", av["adapters_checked"])
        } else {
            av["problems"]
                .as_array()
                .map(|a| {
                    a.iter()
                        .map(|x| x.as_str().unwrap_or("").to_string())
                        .collect::<Vec<_>>()
                        .join("; ")
                })
                .unwrap_or_default()
        },
        Some("gov adapters generate"),
    ));
    // D023 records
    let store = RecordStore::load(&p.root);
    let rec_problems: Vec<String> = store.problems.clone();
    let problem_paths: Vec<String> = rec_problems
        .iter()
        .filter_map(|x| x.split(':').next().map(|s| s.trim().to_string()))
        .filter(|s| s.contains('/') || s.ends_with(".yaml") || s.ends_with(".md"))
        .collect();
    add(with_subjects(
        chk(
            "D023",
            "records parse",
            rec_problems.is_empty(),
            "high",
            if rec_problems.is_empty() {
                format!("{} records", store.records.len())
            } else {
                rec_problems.join("; ")
            },
            Some("fix YAML/frontmatter errors"),
        ),
        problem_paths,
    ));
    // D033 T2 binding (WS-3 IP-5): OS-written state that no gov operation on this machine produced as it stands,
    // with the suite's severities (`verification::reporting::t2_severity`): tampering (BROKEN) and an unsealed gate in
    // force fail; legacy or hand-written approval claims the OS does not honour, and records sealed on another machine
    // (a clone), are reported without failing — they are simply not honoured.
    let t2 = crate::t2::audit(p);
    let unhonoured_evidence = crate::verification::currency::unhonoured_health_outputs(&store);
    let mut failing: Vec<(String, &'static str, String)> = vec![];
    let mut disclosed: Vec<String> = vec![];
    for r in &t2 {
        let id = r["id"].as_str().unwrap_or("?").to_string();
        let rec = store.get(&id);
        let (sev, what) = crate::verification::reporting::t2_severity(
            r["t2"]["binding"].as_str().unwrap_or("?"),
            rec.map(|x| x.rtype() == "human-gate").unwrap_or(false),
            rec.map(crate::verification::reporting::t2_in_force)
                .unwrap_or(false),
            &r["t2"],
        );
        if sev == "low" {
            disclosed.push(id);
        } else {
            failing.push((id, sev, what));
        }
    }
    for h in &unhonoured_evidence {
        let id = h["id"].as_str().unwrap_or("?").to_string();
        if h["t2"]["binding"] == "BROKEN" {
            failing.push((
                id,
                "high",
                "health evidence modified after the health operation sealed it".into(),
            ));
        } else {
            disclosed.push(id);
        }
    }
    // plugin-registry entries (WS-7; WS-2 R3-11), change-control state (WS-4) and the adoption record (WS-9 IP-R2-4)
    for (id, b) in crate::verification::reporting::plugin_registry_unbound(p) {
        let code = b["binding"].as_str().unwrap_or("?");
        match code {
            "BROKEN" => failing.push((
                format!("plugin-registry entry {id}"),
                "high",
                "modified after gov sealed the registration".into(),
            )),
            "UNSEALED" => failing.push((
                format!("plugin-registry entry {id}"),
                "medium",
                "not written by gov (hand-written registration)".into(),
            )),
            _ => disclosed.push(format!("plugin-registry entry {id} ({code})")),
        }
    }
    for c in crate::cit::bindings(p) {
        if c["state"]["binding"] == "VERIFIED" || c["cit_status"] == "PROPOSED" {
            continue;
        }
        let id = c["id"].as_str().unwrap_or("?").to_string();
        // state sealed on another machine is not honoured here and is disclosed, as for every other T2 record
        // (P2-ADJ-0002; `t2_severity` FOREIGN); modified, hand-written or copied state in force fails
        if matches!(
            c["cit_status"].as_str(),
            Some("APPROVED") | Some("EXECUTING")
        ) && !crate::cit::binding::sealed_elsewhere(&c["state"])
        {
            failing.push((
                id,
                "high",
                format!(
                    "change-control state not as gov sealed it ({}), in force",
                    c["state"]["code"].as_str().unwrap_or("UNBOUND")
                ),
            ));
        } else {
            disclosed.push(id);
        }
    }
    if let Some((b, rel)) = crate::verification::reporting::adoption_baseline_binding(p) {
        match b.code() {
            "VERIFIED" => {}
            "BROKEN" => failing.push((rel, "high", "the adoption record was modified after gov adopt sealed it (stage order, authorship and verdicts not honoured)".into())),
            other => disclosed.push(format!("{rel} ({other})")),
        }
    }
    let worst = if failing.iter().any(|(_, s, _)| *s == "high") {
        "high"
    } else {
        "medium"
    };
    add(chk(
        "D033",
        "OS-written records bound to gov operations (T2)",
        failing.is_empty(),
        worst,
        if failing.is_empty() {
            format!(
                "no tampered OS state and no unsealed gate in force; {} record(s) not honoured on this machine (legacy, hand-written approval claims, or sealed elsewhere){}",
                disclosed.len(),
                if disclosed.is_empty() { String::new() } else { format!(": {}", disclosed.iter().take(10).cloned().collect::<Vec<_>>().join(", ")) }
            )
        } else {
            format!(
                "{}; the OS does not honour them (D-0007 rule 2)",
                failing
                    .iter()
                    .map(|(id, _, w)| format!("{id} {w}"))
                    .collect::<Vec<_>>()
                    .join("; ")
            )
        },
        Some("restore tampered records from version control; withdraw hand-written gates and raise them through gov (`gov gate list` shows what is unverified)"),
    ));
    // D034 failure memory (WS-6 IP-2): open failure records awaiting follow-up. An open tool failure (a capability the
    // product needed failed) degrades; open retrieval-miss events are memory-quality evidence, reported only.
    let open = crate::memory::failures::open_failures(p);
    let tool_open: Vec<String> = open
        .iter()
        .filter(|f| f["failure_kind"] == "tool-failure")
        .map(|f| f["id"].as_str().unwrap_or("?").to_string())
        .collect();
    add(chk(
        "D034",
        "failure memory followed up",
        tool_open.is_empty(),
        "low",
        if open.is_empty() {
            "no open failure records".into()
        } else {
            format!(
                "{} open failure record(s) awaiting follow-up ({} tool failure(s){}): {}",
                open.len(),
                tool_open.len(),
                if tool_open.is_empty() { "" } else { ": capability degraded" },
                open.iter()
                    .take(10)
                    .map(|f| format!("{} ({})", f["id"].as_str().unwrap_or("?"), f["failure_kind"].as_str().unwrap_or("?")))
                    .collect::<Vec<_>>()
                    .join(", ")
            )
        },
        Some("investigate the failure and link its follow-up task (memory::failures::link_follow_up); repair or replace the failing tool"),
    ));
    Ok(checks)
}

/// Record ids and paths named anywhere in a JSON value (`id`, `task`, `targets`, `members`, `paths`, …).
fn collect_ids(v: &Value, out: &mut Vec<String>) {
    match v {
        Value::String(s) => {
            if crate::records::id_regex().is_match(s) || s.contains('/') {
                out.push(s.clone());
            }
        }
        Value::Array(a) => a.iter().for_each(|x| collect_ids(x, out)),
        Value::Object(m) => m.values().for_each(|x| collect_ids(x, out)),
        _ => {}
    }
}

fn with_subjects(mut c: Value, subjects: Vec<String>) -> Value {
    c["subjects"] = json!(subjects);
    c
}

/// **D035 — the repository verdict** (Contract v3:995-1008 "A repository is HEALTHY only when"; BC-P2-44). The
/// thirteen conditions from this doctor run's checks and the latest governance-suite outcomes, and every Gate U SLO
/// against its declared threshold (`verification::slo`). The message states the verdict and every failing condition
/// and crossed SLO. The check fails for what the doctor's own checks do not already fail on: a condition failing
/// through a governance-suite outcome (at that outcome's severity, at most high — the owning check carries its own
/// critical severity), an SLO whose owner is not a doctor check, or a condition no owning check has evaluated on this
/// machine (low: HEALTHY is not established for it). With the doctor's own failures, the doctor verdict is therefore
/// HEALTHY only when the repository verdict is.
fn check_repository_healthy(
    p: &Project,
    doctor_now: &[Value],
    snap: &crate::verification::currency::Snapshot,
) -> Value {
    let st = crate::scheduler::store::load_state(p);
    let store = RecordStore::load(&p.root);
    let db = if p.db_path().exists() {
        RuntimeDb::open(&p.db_path()).ok()
    } else {
        None
    };
    let slos = crate::verification::slo::evaluate(&crate::verification::slo::SloCtx {
        p,
        store: &store,
        db: db.as_ref(),
        snapshot: Some(snap),
        state: &st,
    });
    let conds = crate::verification::slo::conditions(&st, Some(doctor_now), None);
    let v = crate::verification::slo::repository_verdict(&conds, &slos);
    let failing: Vec<&Value> = conds.iter().filter(|c| c["status"] == "FAILS").collect();
    let unknown: Vec<&Value> = conds.iter().filter(|c| c["status"] == "UNKNOWN").collect();
    let crossed: Vec<Value> = v["crossed_slos"].as_array().cloned().unwrap_or_default();
    let rank = crate::scheduler::catalogue::rank;
    // what the doctor did not already know: a condition failing through a governance-suite outcome, or an SLO whose
    // owner is not one of this run's doctor checks (a failing doctor check already fails on its own)
    let doctor_id = |x: &Value| {
        let id = x.as_str().unwrap_or("");
        id.starts_with('D') && id.len() == 4
    };
    let mut worst = if unknown.is_empty() { "none" } else { "low" };
    let mut beyond = !unknown.is_empty();
    for c in &failing {
        for f in c["failing"].as_array().cloned().unwrap_or_default() {
            if doctor_id(&f["check"]) {
                continue;
            }
            beyond = true;
            let s = f["severity"].as_str().unwrap_or("medium");
            let s = if rank(s) >= 3 {
                "high"
            } else if rank(s) == 2 {
                "medium"
            } else {
                "low"
            };
            if rank(s) > rank(worst) {
                worst = s;
            }
        }
    }
    for x in &crossed {
        // an SLO another check owns is reflected through that check's condition (above), at its owner's severity
        if x["owner"] != crate::verification::slo::FAMILY {
            continue;
        }
        beyond = true;
        let s = x["severity"].as_str().unwrap_or("medium");
        let s = if rank(s) >= 3 { "high" } else { "medium" };
        if rank(s) > rank(worst) {
            worst = s;
        }
    }
    let ok = !beyond;
    let all_hold = failing.is_empty() && unknown.is_empty() && crossed.is_empty();
    let msg = if all_hold {
        "HEALTHY: all thirteen conditions hold and every Gate U SLO is within its threshold"
            .to_string()
    } else {
        let mut parts = vec![];
        if !failing.is_empty() {
            parts.push(format!(
                "condition(s) failing: {}",
                failing
                    .iter()
                    .map(|c| format!(
                        "{} {} ({})",
                        c["id"].as_str().unwrap_or("?"),
                        c["title"].as_str().unwrap_or(""),
                        c["failing"]
                            .as_array()
                            .map(|a| a
                                .iter()
                                .map(|f| format!(
                                    "{} {}",
                                    f["check"].as_str().unwrap_or("?"),
                                    f["severity"].as_str().unwrap_or("")
                                ))
                                .collect::<Vec<_>>()
                                .join(", "))
                            .unwrap_or_default()
                    ))
                    .collect::<Vec<_>>()
                    .join("; ")
            ));
        }
        if !crossed.is_empty() {
            parts.push(format!(
                "SLO threshold(s) crossed: {}",
                crossed
                    .iter()
                    .map(|x| format!(
                        "{} = {} (threshold {})",
                        x["slo"].as_str().unwrap_or("?"),
                        x["value"],
                        x["threshold"]
                    ))
                    .collect::<Vec<_>>()
                    .join("; ")
            ));
        }
        if !unknown.is_empty() {
            parts.push(format!(
                "not established on this machine (no owning check evaluated): {}",
                unknown
                    .iter()
                    .map(|c| format!(
                        "{} {}",
                        c["id"].as_str().unwrap_or("?"),
                        c["title"].as_str().unwrap_or("")
                    ))
                    .collect::<Vec<_>>()
                    .join(", ")
            ));
        }
        format!(
            "repository verdict {}: {}",
            v["verdict"].as_str().unwrap_or("?"),
            parts.join(" | ")
        )
    };
    let mut c = chk(
        "D035",
        "repository HEALTHY: the thirteen Gate U conditions and the framework-health SLOs",
        ok,
        if ok { "info" } else { worst },
        msg,
        Some("repair the failing owning checks; `gov health status` shows every condition, SLO and threshold; `gov health run` re-evaluates the suite"),
    );
    c["repository"] = json!({"verdict": v["verdict"], "failing_conditions": v["failing_conditions"], "unknown_conditions": v["unknown_conditions"], "crossed_slos": crossed});
    c
}

fn group_currency_health(
    p: &Project,
    snap: &crate::verification::currency::Snapshot,
) -> Result<Vec<Value>> {
    let mut checks = vec![];
    // D021 governance suite currency: the green record is current only while every evidence input class is unchanged
    let cur = crate::verification::currency::Currency::evaluate(p, snap);
    let mut c = chk(
        "D021",
        "governance suite green and current",
        cur.current,
        "medium",
        cur.message(),
        Some("gov health run (re-checks only the checks the changed inputs impact; gov audit runs the full suite)"),
    );
    c["currency"] = cur.to_value();
    checks.push(c);
    // D030 product tests: recorded per-family evidence, current and passing (Contract v3:751-761, :980, :1004)
    let (pf, detail) = crate::verification::product::health_findings(p, Some(snap));
    let failing: Vec<&Value> = pf.iter().filter(|f| f["severity"] == "high").collect();
    let mut c = chk(
        "D030",
        "product tests pass (recorded per-family evidence)",
        failing.is_empty(),
        "high",
        if !detail["applicable"].as_bool().unwrap_or(false) {
            "no product test command configured or detectable".into()
        } else if pf.is_empty() {
            format!(
                "{} famil(ies) recorded passing and current",
                detail["families"].as_object().map(|m| m.len()).unwrap_or(0)
            )
        } else {
            // failing families first; stale or missing evidence is reported but is not a failure
            let mut v: Vec<&Value> = failing.clone();
            v.extend(pf.iter().filter(|f| f["severity"] != "high"));
            v.iter()
                .map(|f| f["message"].as_str().unwrap_or("").to_string())
                .collect::<Vec<_>>()
                .join("; ")
        },
        Some("gov verify product (records per-family results as governed evidence)"),
    );
    if let Some(f) = failing.first() {
        c["covers"] = f["covers"].clone();
    }
    c["product_tests"] = detail;
    checks.push(c);
    // D031 hard-blocks recorded by governance-suite checks (doctor-origin blocks are the failing checks above)
    let st = crate::scheduler::store::load_state(p);
    let (fam_blocks, stale_blocks) = crate::scheduler::suite_blocks(p, snap);
    let mut c = chk(
        "D031",
        "no active health hard-block from the governance suite",
        fam_blocks.is_empty(),
        "high",
        if fam_blocks.is_empty() {
            format!("health state {}", crate::scheduler::health_state(&st))
        } else {
            fam_blocks
                .iter()
                .map(|b| format!("{} ({}) refuses {}: {}", b["check"].as_str().unwrap_or("?"), b["severity"].as_str().unwrap_or("?"), b["operations"], b["message"].as_str().unwrap_or("")))
                .collect::<Vec<_>>()
                .join("; ")
        },
        Some("repair the failing check; `gov health status` lists the blocks, `gov health run` re-evaluates"),
    );
    c["blocks"] = json!(fam_blocks);
    c["stale_blocks"] = json!(stale_blocks);
    checks.push(c);
    Ok(checks)
}

impl RuntimeDb {
    pub fn count_where(&self, table: &str, cond: &str) -> i64 {
        self.conn
            .query_row(
                &format!("SELECT COUNT(*) FROM {table} WHERE {cond}"),
                [],
                |r| r.get(0),
            )
            .unwrap_or(0)
    }
}
