//! Repair iteration 1, round 3, WS-6 (P2-AR-0037): index freshness judges exactly what the indexer indexes (WS-4 R2-10),
//! a significant mutation observed at rebuild is a checkpoint boundary (R2-11), Markdown headings are held and compared
//! the same way on both sides (WS-2 R3-4), a refused code-intelligence adapter is a recorded degradation (WS-7
//! IP-W7-2), research/experiment standing in the index and the benchmark/select influence backlinks (WS-10
//! IP-WS10-03/04/05), and the repository contract's classification of the OS's own state (BC-P2-31).
//!
//! Builder regression evidence (Contract v3 O3), not acceptance evidence. Human answers go through WS-3's
//! owner-signed channel helper (`crate::ws03::human_decide`); every invocation declares its role.
use crate::common::*;
use serde_json::{json, Value};
use std::path::{Path, PathBuf};

fn init(tag: &str) -> (PathBuf, Gov) {
    let (root, g) = setup_fixture("greenfield", tag, "S-ws06r3");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        tag,
        "--alias",
        &format!("{tag}-alias"),
    ]);
    (root, g)
}

fn excluded_reason(report: &Value, path: &str) -> Option<String> {
    report["excluded"]
        .as_array()?
        .iter()
        .find(|e| e["path"] == path)
        .and_then(|e| e["reason"].as_str().map(String::from))
}

fn manifest_excluded(root: &Path, path: &str) -> Option<Value> {
    json(root, "governance/generated/index-manifest.json")["excluded"]
        .as_array()?
        .iter()
        .find(|e| e["path"] == path)
        .cloned()
}

fn list(v: &Value) -> Vec<String> {
    v.as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(String::from))
                .collect()
        })
        .unwrap_or_default()
}

fn artifact(root: &Path, id: &str) -> Option<Value> {
    db(root)
        .query(
            "SELECT path, state_class FROM artifacts WHERE artifact_id=?1",
            &[&id],
        )
        .unwrap()
        .into_iter()
        .next()
}

fn requirement(id: &str, title: &str) -> Value {
    json!({"id": id, "type": "requirement", "title": title, "status": "ACTIVE", "kind": "functional"})
}

/// An incremental build and a full build of the same tree produce the same index (manifest hash over the index
/// format, pins, every artefact with its derivation, and every exclusion with what decided it).
fn assert_incremental_equals_full(g: &Gov, incremental: &Value) {
    let full = g.ok(&["rebuild-memory"]);
    assert_eq!(full["mode"], "full");
    assert_eq!(
        incremental["manifest_hash"], full["manifest_hash"],
        "incremental equals full"
    );
}

/// R2-10 (pre-existing): a file the indexer skips must never read as "unindexed" to freshness, and an exclusion the
/// manifest records must never hide a file the index should hold. Every skip reason is covered: too large, not UTF-8,
/// secret content, a duplicate record id (the index holds the occurrence the record store resolves the id to), and a
/// path-map exclusion that is lifted.
#[test]
fn freshness_judges_exactly_what_the_indexer_indexes() {
    let (root, g) = init("ws06r3-fresh");
    let big = "a line of text the index would hold if it were not too large\n".repeat(36_000);
    assert!(big.len() > 2_000_000);
    write(&root, "product/big.txt", &big);
    std::fs::write(root.join("product/latin1.txt"), b"caf\xe9 au lait\n").unwrap();
    // an access-key-shaped literal, built at run time so no source file carries one
    let key = format!("AKIA{}", "Q7ZX4MPLE2RR3KT9");
    write(
        &root,
        "product/leak.txt",
        &format!("deploy notes\nkey = {key}\n"),
    );
    // four files declare REQ-0101: the record store resolves it to spec/ (not governance/project/, not archive/), in
    // walk order within spec/
    write_yaml(
        &root,
        "spec/requirements/REQ-0101.yaml",
        &requirement("REQ-0101", "Totals are exact"),
    );
    write_yaml(
        &root,
        "spec/requirements/zz/REQ-0101.yaml",
        &requirement("REQ-0101", "Totals are exact (copy under zz)"),
    );
    write_yaml(
        &root,
        "governance/project/extra/REQ-0101.yaml",
        &requirement("REQ-0101", "Totals are exact (governance copy)"),
    );
    write_yaml(
        &root,
        "archive/REQ-0101.yaml",
        &requirement("REQ-0101", "Totals are exact (archived copy)"),
    );
    write(
        &root,
        "product/data/customers.md",
        "# Customers\nACME ZULUQUARTZ9 account\n",
    );
    let mut ds = yaml(&root, "governance/project/DATA_SENSITIVITY.yaml");
    ds["classifications"] = json!([{"pattern": "product/data/**", "class": "restricted"}]);
    write_yaml(&root, "governance/project/DATA_SENSITIVITY.yaml", &ds);
    git_commit_all(&root, "files the indexer skips");

    let r = g.ok(&["rebuild-memory", "--incremental"]);
    assert_eq!(
        excluded_reason(&r, "product/big.txt").as_deref(),
        Some("too_large")
    );
    assert_eq!(
        excluded_reason(&r, "product/latin1.txt").as_deref(),
        Some("not_utf8")
    );
    assert_eq!(
        excluded_reason(&r, "product/leak.txt").as_deref(),
        Some("secret_content")
    );
    assert_eq!(
        excluded_reason(&r, "product/data/customers.md").as_deref(),
        Some("sensitivity:restricted")
    );
    for dup in [
        "spec/requirements/zz/REQ-0101.yaml",
        "governance/project/extra/REQ-0101.yaml",
        "archive/REQ-0101.yaml",
    ] {
        assert_eq!(
            excluded_reason(&r, dup).as_deref(),
            Some("duplicate_id"),
            "{dup}"
        );
        let m = manifest_excluded(&root, dup).unwrap();
        assert_eq!(m["id"], "REQ-0101");
        assert_eq!(m["kept"], "spec/requirements/REQ-0101.yaml");
        assert_eq!(m["content_hash"].as_str().unwrap().len(), 64, "{m}");
        assert!(m["derivation"].is_string(), "{m}");
    }
    assert_eq!(
        artifact(&root, "REQ-0101").unwrap()["path"],
        "spec/requirements/REQ-0101.yaml"
    );
    let m = manifest_excluded(&root, "product/leak.txt").unwrap();
    assert_eq!(m["content_hash"].as_str().unwrap().len(), 64);
    assert!(!json(&root, "governance/generated/index-manifest.json")
        .to_string()
        .contains(&key));
    let f = g.ok(&["memory", "freshness"]);
    assert_eq!(
        f["fresh"], true,
        "nothing the indexer skips reads as unindexed: {f}"
    );
    assert!(list(&f["added"]).is_empty(), "{f}");
    assert_incremental_equals_full(&g, &r);

    // the secret leaves the file: the exclusion no longer holds, the file must be indexed
    write(&root, "product/leak.txt", "deploy notes\nkey = rotated\n");
    let f = g.ok(&["memory", "freshness"]);
    assert_eq!(f["fresh"], false);
    assert!(
        list(&f["added"]).contains(&"product/leak.txt".to_string()),
        "{f}"
    );
    let r = g.ok(&["rebuild-memory", "--incremental"]);
    assert!(excluded_reason(&r, "product/leak.txt").is_none());
    assert_eq!(g.ok(&["memory", "freshness"])["fresh"], true);

    // the path map stops excluding a file: the manifest's old exclusion never hides it
    ds["classifications"] = json!([]);
    write_yaml(&root, "governance/project/DATA_SENSITIVITY.yaml", &ds);
    let f = g.ok(&["memory", "freshness"]);
    assert!(
        list(&f["added"]).contains(&"product/data/customers.md".to_string()),
        "{f}"
    );
    let r = g.ok(&["rebuild-memory", "--incremental"]);
    assert!(artifact(&root, "file:product/data/customers.md").is_some());
    assert_eq!(g.ok(&["memory", "freshness"])["fresh"], true);
    assert_incremental_equals_full(&g, &r);

    // a duplicate whose content changes is judged again
    write_yaml(
        &root,
        "spec/requirements/zz/REQ-0101.yaml",
        &requirement("REQ-0101", "Totals are exact (copy under zz, edited)"),
    );
    let f = g.ok(&["memory", "freshness"]);
    assert!(
        list(&f["added"]).contains(&"spec/requirements/zz/REQ-0101.yaml".to_string()),
        "{f}"
    );
    g.ok(&["rebuild-memory", "--incremental"]);
    assert_eq!(g.ok(&["memory", "freshness"])["fresh"], true);

    // the held occurrence is removed: the next one the record store resolves the id to is held (spec/ outranks
    // governance/project/ and archive/), incrementally exactly as a full build would
    std::fs::remove_file(root.join("spec/requirements/REQ-0101.yaml")).unwrap();
    let f = g.ok(&["memory", "freshness"]);
    assert!(
        list(&f["removed"]).contains(&"spec/requirements/REQ-0101.yaml".to_string()),
        "{f}"
    );
    let r = g.ok(&["rebuild-memory", "--incremental"]);
    assert_eq!(
        artifact(&root, "REQ-0101").unwrap()["path"],
        "spec/requirements/zz/REQ-0101.yaml"
    );
    assert_eq!(g.ok(&["memory", "freshness"])["fresh"], true);
    assert_incremental_equals_full(&g, &r);

    // a new occurrence that outranks the held one (walked earlier within spec/) takes the id in an incremental build
    // too — the choice is a function of the tree, not of which file the index met first
    write_yaml(
        &root,
        "spec/requirements/AAA-REQ-0101.yaml",
        &requirement("REQ-0101", "Totals are exact (earlier in spec/)"),
    );
    let r = g.ok(&["rebuild-memory", "--incremental"]);
    assert_eq!(
        artifact(&root, "REQ-0101").unwrap()["path"],
        "spec/requirements/AAA-REQ-0101.yaml"
    );
    assert_eq!(
        excluded_reason(&r, "spec/requirements/zz/REQ-0101.yaml").as_deref(),
        Some("duplicate_id")
    );
    assert_eq!(g.ok(&["memory", "freshness"])["fresh"], true);
    assert_incremental_equals_full(&g, &r);
}

/// R2-10's symptom: with a file the indexer skips in the tree, a change transaction's post-execution
/// `index_freshness` verification failed and every CIT-E rolled back. It now commits.
#[test]
fn a_change_transaction_commits_while_the_tree_holds_files_the_indexer_skips() {
    let (root, g) = init("ws06r3-cit");
    let big = "x".repeat(80) + "\n";
    write(&root, "product/big.txt", &big.repeat(26_000));
    std::fs::write(root.join("product/latin1.txt"), b"na\xefve\n").unwrap();
    git_commit_all(&root, "a too-large and a non-UTF-8 file");
    g.ok(&["rebuild-memory", "--incremental"]);
    let mf = root.join(".governance-runtime/ws06r3-m.json");
    std::fs::write(
        &mf,
        json!([{"op": "write_file", "path": "spec/now/NOW.md", "content": "# NOW\ngoverned while skipped files exist\n"}])
            .to_string(),
    )
    .unwrap();
    let c = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        "editorial update of NOW",
        "--trigger",
        "editorial",
        "--manifest",
        mf.to_str().unwrap(),
    ]);
    let cid = c["id"].as_str().unwrap().to_string();
    let sim = g.ok(&["cit", "simulate", &cid]);
    assert_eq!(sim["impact"]["human_gate_required"], false, "{sim}");
    g.ok(&["cit", "approve", &cid, "--by", "agent", "--method", "auto"]);
    let ex = g.run(&["cit", "execute", &cid]);
    assert!(ex.ok(), "{}", ex.envelope);
    assert_eq!(
        yaml(&root, &format!("spec/decisions/{cid}.yaml"))["cit_status"],
        "COMMITTED"
    );
    assert_eq!(g.ok(&["memory", "freshness"])["fresh"], true);
}

/// R2-11 (WS-4 BC-P2-05, Contract v3 N2 "significant mutation"): an operator's index rebuild that observes at least
/// `CHECKPOINT_POLICY.watchdog.max_operations_between_checkpoints` added/changed/removed artefacts writes a
/// `significant_mutation` checkpoint (carrying the next action forward); fewer changes write none; under FREEZE_WRITES
/// the rebuild (a recovery operation) still runs and the checkpoint it could not write is reported, typed.
#[test]
fn a_significant_mutation_observed_at_rebuild_is_a_checkpoint_boundary() {
    let (root, g) = init("ws06r3-boundary");
    g.ok(&[
        "checkpoint",
        "create",
        "--next-action",
        "implement the bulk import",
        "--step",
        "planned",
    ]);
    let n0 = g.ok(&["checkpoint", "latest"])["id"].clone();
    for i in 0..5 {
        write(&root, &format!("product/small_{i}.txt"), &format!("{i}\n"));
    }
    let r = g.ok(&["rebuild-memory", "--incremental"]);
    assert_eq!(
        r["boundaries"]["significant_mutation"], false,
        "{}",
        r["boundaries"]
    );
    assert_eq!(g.ok(&["checkpoint", "latest"])["id"], n0);
    for i in 0..30 {
        write(&root, &format!("product/bulk_{i}.txt"), &format!("{i}\n"));
    }
    let r = g.ok(&["rebuild-memory", "--incremental"]);
    let b = &r["boundaries"];
    assert_eq!(b["significant_mutation"], true, "{b}");
    assert!(b["changed_artifacts"].as_u64().unwrap() >= 30, "{b}");
    assert!(b.get("error").is_none(), "{b}");
    let latest = g.ok(&["checkpoint", "latest"]);
    assert_ne!(latest["id"], n0);
    assert_eq!(latest["trigger"], "significant_mutation", "{latest}");
    assert_eq!(latest["next_action"], "implement the bulk import");
    // written by the checkpoint subsystem's own boundary observation, or — when that does not see the mutation (it
    // counts files by modification time since the previous checkpoint) — by the rebuild, which measured it
    assert!(
        b["checkpoints"]
            .as_array()
            .unwrap()
            .iter()
            .any(|c| c["trigger"] == "significant_mutation" && c["checkpoint"] == latest["id"]),
        "{b}"
    );
    assert_eq!(
        g.ok(&["memory", "freshness"])["fresh"],
        true,
        "the rebuild still leaves the index current"
    );
    assert_eq!(
        r["manifest_hash"],
        json(&root, "governance/generated/index-manifest.json")["manifest_hash"]
    );
    // under FREEZE_WRITES the rebuild runs (recovery) and the boundary it could not record is reported, typed
    g.ok(&[
        "freeze-writes",
        "--reason",
        "ws06r3: rebuild stays a recovery operation",
    ]);
    for i in 0..30 {
        write(&root, &format!("product/frozen_{i}.txt"), &format!("{i}\n"));
    }
    let r = g.ok(&["rebuild-memory", "--incremental"]);
    assert_eq!(r["boundaries"]["significant_mutation"], true);
    assert!(
        r["boundaries"]["error"]["code"].is_string(),
        "{}",
        r["boundaries"]
    );
    assert!(
        r["problems"].to_string().contains("CHECKPOINT_NOT_WRITTEN"),
        "{}",
        r["problems"]
    );
    assert_eq!(
        g.ok(&["checkpoint", "latest"])["trigger"],
        "significant_mutation"
    );
    g.ok(&["resume"]);
}

/// WS-2 R3-4: Markdown headings — a title followed directly by a sub-heading, runs of headings, a trailing heading —
/// are held by the index, and the coverage check compares them the same way on both sides: no false gap.
#[test]
fn markdown_headings_are_held_and_coverage_reports_no_false_gap() {
    let (root, g) = init("ws06r3-headings");
    write(
        &root,
        "spec/notes/guide.md",
        "# Operating guide\n\n## Scope\nwhat the guide covers\n# Appendix\n## Glossary\n### Terms\n",
    );
    write(
        &root,
        "spec/decisions/D-0301.md",
        "---\nid: D-0301\ntype: decision\ntitle: Headings only\nstatus: ACTIVE\n---\n# Context\n# Decision\n## Consequences\nnone\n",
    );
    git_commit_all(&root, "heading-heavy documents");
    let r = g.ok(&["rebuild-memory"]);
    assert_eq!(r["coverage"]["complete"], true, "{}", r["coverage"]);
    assert_eq!(
        db(&root).get_meta("index_coverage").unwrap()["complete"],
        true
    );
    let texts = chunk_texts(&root).join("\n");
    for h in [
        "Operating guide",
        "Appendix",
        "Terms",
        "Context",
        "Decision",
    ] {
        assert!(
            texts.lines().any(|l| l.trim() == h),
            "heading {h} is held by a chunk"
        );
    }
    let a = g.run(&["audit", "--no-persist"]);
    let body = if a.ok() { a.result() } else { a.details() };
    let fam = body["families"]["index_content_coverage"].clone();
    assert_eq!(fam["detail"]["complete"], true, "{fam}");
    assert_eq!(
        fam["detail"]["verifier_heading_marker_artefacts"],
        Value::Null,
        "{fam}"
    );
}

/// WS-7 IP-W7-2 (D-0005): a declared `code_intel` adapter the product refuses to execute (here: never registered) is
/// a recorded degradation — every build names it while files of its language exist, and failure memory records it —
/// never a silent fallback to the built-in extractor.
#[test]
fn a_refused_code_intelligence_adapter_is_a_recorded_degradation() {
    let (root, g) = init("ws06r3-refused");
    write(
        &root,
        "product/app.py",
        "def total(lines):\n    return sum(lines)\n",
    );
    copy_dir(
        &canonical_root().join("capabilities/python/govos_capabilities"),
        &root.join("tools/pyplug/govos_capabilities"),
    );
    write_yaml(
        &root,
        "governance/project/plugins/python-ast.yaml",
        &json!({"plugin_id": "python-ast", "capability": "code_intel", "version": "1.0.0", "languages": ["python"],
            "command": ["python3", "-m", "govos_capabilities.code_intel_python_ast"], "cwd": "tools/pyplug"}),
    );
    git_commit_all(&root, "a declared, unregistered python adapter");
    let r = g.ok(&["rebuild-memory"]);
    let deg = r["degradations"].to_string();
    assert!(
        deg.contains("product/app.py: code_intel plugin python-ast refused ("),
        "{deg}"
    );
    assert!(
        deg.contains("python files are analysed by the built-in extractor"),
        "{deg}"
    );
    let fail = r["failures"]
        .as_array()
        .unwrap()
        .iter()
        .filter_map(|f| f["path"].as_str())
        .map(|p| yaml(&root, p))
        .find(|f| f.to_string().contains("python-ast"))
        .unwrap_or_else(|| {
            panic!(
                "no failure memory for the refused adapter: {}",
                r["failures"]
            )
        });
    assert_eq!(fail["failure_kind"], "tool-failure", "{fail}");
    assert!(fail.to_string().contains("code_intel"), "{fail}");
    // a later build that re-analyses nothing still states the standing degradation
    let r2 = g.ok(&["rebuild-memory", "--incremental"]);
    assert!(
        r2["degradations"]
            .to_string()
            .contains("code_intel plugin python-ast v1.0.0 refused"),
        "{}",
        r2["degradations"]
    );
    let prov: Vec<Value> = db(&root)
        .query(
            "SELECT DISTINCT provider FROM symbols WHERE path='product/app.py'",
            &[],
        )
        .unwrap();
    assert!(
        prov.iter()
            .all(|p| !p["provider"].as_str().unwrap_or("").contains("python-ast")),
        "the refused adapter never ran: {prov:?}"
    );
}

/// WS-10 IP-WS10-05: the index holds research and experiments at their evidence standing — non-governed evidence is
/// reference-only (NARRATIVE) — and a standing that changes while the record does not (an experiment's input drifts)
/// makes the index stale and is re-derived incrementally exactly as a full build derives it.
#[test]
fn the_index_holds_research_and_experiments_at_their_evidence_standing() {
    let (root, g) = init("ws06r3-standing");
    write_yaml(
        &root,
        "spec/research/RES-0101.yaml",
        &json!({"id": "RES-0101", "type": "research", "title": "Unsupported claim", "status": "ACTIVE",
            "question": "Does caching help?", "conclusion": "Caching halves latency.", "state_class": "EVIDENCE"}),
    );
    let complete = json!({"question": "Is the async client faster?", "reason": "choose a client", "method": "replay one day of traffic",
        "sources": ["staging traffic log"], "measurements": {"p95_ms": {"before": 40, "after": 18}}, "uncertainty": "one day of traffic",
        "conclusion": "the async client halves p95", "confidence": 0.7});
    let rr = g.ok(&["research", "record", "--fields", &complete.to_string()]);
    let rid = rr["research"]["id"].as_str().unwrap().to_string();
    write(&root, "fixtures/traffic.csv", "t,ms\n1,40\n2,18\n");
    git_commit_all(&root, "research and experiment inputs");
    let design = json!({"hypothesis": "an async client halves p95", "method": "replay one day of traffic",
        "inputs": [{"path": "fixtures/traffic.csv"}], "reproducibility": {"acceptance": {"mode": "tolerance", "relative": 0.05}}});
    let e = g.ok(&["experiment", "design", "--fields", &design.to_string()]);
    let eid = e["experiment"]["id"].as_str().unwrap().to_string();
    g.ok(&[
        "experiment",
        "run",
        &eid,
        "--results",
        &json!({"p95_ms": 18.0}).to_string(),
    ]);
    let conc = json!({"interpretation": "the async client helps at p95", "decision_influence": "supports adopting the async client",
        "confidence": 0.8, "reproducibility": {"procedure": "replay fixtures/traffic.csv", "environment": "staging"}});
    g.ok(&[
        "experiment",
        "conclude",
        &eid,
        "--fields",
        &conc.to_string(),
    ]);
    let rp = g.with_session("S-repro").ok(&[
        "experiment",
        "reproduce",
        &eid,
        "--results",
        &json!({"p95_ms": 18.4}).to_string(),
    ]);
    assert_eq!(rp["standing"]["standing"], "GOVERNED_EVIDENCE", "{rp}");
    let r = g.ok(&["rebuild-memory", "--incremental"]);
    assert_eq!(
        artifact(&root, "RES-0101").unwrap()["state_class"],
        "NARRATIVE"
    );
    assert_eq!(artifact(&root, &rid).unwrap()["state_class"], "EVIDENCE");
    assert_eq!(artifact(&root, &eid).unwrap()["state_class"], "EVIDENCE");
    let q = g.ok(&["memory", "query", "caching halves latency", "--k", "5"]);
    let hit = q["hits"]
        .as_array()
        .unwrap()
        .iter()
        .find(|h| h["artifact_id"] == "RES-0101")
        .cloned()
        .unwrap_or_else(|| panic!("{q}"));
    assert_eq!(hit["state_class"], "NARRATIVE", "{hit}");
    assert_eq!(g.ok(&["memory", "freshness"])["fresh"], true);
    assert_incremental_equals_full(&g, &r);
    // the experiment's input drifts: its record is unchanged, its standing is not
    write(&root, "fixtures/traffic.csv", "t,ms\n1,41\n2,18\n");
    let exp_path = artifact(&root, &eid).unwrap()["path"]
        .as_str()
        .unwrap()
        .to_string();
    let f = g.ok(&["memory", "freshness"]);
    assert_eq!(f["fresh"], false, "{f}");
    assert!(list(&f["reclassified"]).contains(&exp_path), "{f}");
    let r = g.ok(&["rebuild-memory", "--incremental"]);
    assert!(
        list(&r["rederived"]).contains(&exp_path),
        "{}",
        r["rederived"]
    );
    assert_eq!(artifact(&root, &eid).unwrap()["state_class"], "NARRATIVE");
    assert_eq!(g.ok(&["memory", "freshness"])["fresh"], true);
    assert_incremental_equals_full(&g, &r);
}

/// WS-10 IP-WS10-04/03: a recorded benchmark is concluded, governed research that names the task that commissioned
/// it; the governed profile change relies on it only as citable evidence and records the decision it influenced.
#[test]
fn the_benchmark_is_governed_research_and_the_profile_decision_is_recorded_as_its_influence() {
    let (root, g) = init("ws06r3-bench");
    let t = g.ok(&[
        "task",
        "create",
        "--class",
        "discovery",
        "--objective",
        "choose the retrieval profile",
        "--status",
        "READY",
    ]);
    let tid = t["id"].as_str().unwrap().to_string();
    assert_eq!(
        g.err(&[
            "memory",
            "benchmark",
            "--candidate",
            "current",
            "--candidate",
            "builtin:64",
            "--task",
            &tid
        ])
        .error_code(),
        "USAGE"
    );
    assert_eq!(
        g.err(&[
            "memory",
            "benchmark",
            "--candidate",
            "current",
            "--candidate",
            "builtin:64",
            "--record",
            "--task",
            "TASK-9999"
        ])
        .error_code(),
        "TASK_NOT_FOUND"
    );
    let b = g.ok(&[
        "memory",
        "benchmark",
        "--candidate",
        "current",
        "--candidate",
        "builtin:64",
        "--record",
        "--task",
        &tid,
    ]);
    let res = b["research_record"].as_str().unwrap().to_string();
    let rec = yaml(&root, &format!("spec/research/{res}.yaml"));
    assert_eq!(rec["research_state"], "CONCLUDED");
    assert_eq!(list(&rec["influences"]), vec![tid.clone()]);
    assert_eq!(rec["recorded_by"]["role"], "orchestrator");
    assert_eq!(rec["lifecycle"][0]["state"], "CONCLUDED");
    assert!(rec["os_binding"].is_object(), "{rec}");
    let show = g.ok(&["research", "show", &res]);
    assert_eq!(show["standing"]["standing"], "GOVERNED_EVIDENCE", "{show}");
    let pending = g.ok(&["memory", "select", "builtin:64", "--research", &res]);
    let gid = pending["human_gate"].as_str().unwrap().to_string();
    crate::ws03::human_decide(&g, &gid, "A");
    let sel = g.ok(&[
        "memory",
        "select",
        "builtin:64",
        "--research",
        &res,
        "--gate",
        &gid,
    ]);
    assert_eq!(sel["applied"], true, "{sel}");
    let did = sel["decision"].as_str().unwrap().to_string();
    assert_eq!(list(&sel["influence_recorded"]), vec![res.clone()]);
    let rec = yaml(&root, &format!("spec/research/{res}.yaml"));
    let infl = list(&rec["influences"]);
    assert!(infl.contains(&tid) && infl.contains(&did), "{infl:?}");
    // the backlink is an OS write: the research record's seal still verifies
    let show = g.ok(&["research", "show", &res]);
    assert_eq!(show["standing"]["standing"], "GOVERNED_EVIDENCE", "{show}");
    assert_eq!(show["t2"]["binding"], "VERIFIED", "{show}");
}

/// BC-P2-31: the repository contract an installation receives states where the OS keeps its non-rebuildable state —
/// under any reading of its rules no store location is derived or generated — the specific rules that refine a
/// general one take effect (evidence areas of spec/, product tests), retrieval-miss records are never indexed, and
/// framework.json projects the kernel's store classification.
#[test]
fn the_repository_contract_states_where_the_os_keeps_its_state() {
    let (root, g) = init("ws06r3-contract");
    let rc = yaml(&root, "governance/project/REPOSITORY_CONTRACT.yaml");
    let rules = rc["paths"].as_array().unwrap().clone();
    let any_match = |path: &str| -> Vec<String> {
        rules
            .iter()
            .filter(|r| {
                let pat = r["pattern"].as_str().unwrap_or("");
                gov_runtime::util::glob_match(pat, path)
                    || path.starts_with(
                        &(pat.trim_end_matches('*').trim_end_matches('/').to_string() + "/"),
                    )
            })
            .map(|r| r["class"].as_str().unwrap_or("").to_string())
            .collect()
    };
    for s in gov_runtime::paths::OS_STORES {
        for (legacy, target) in s.moves {
            for rel in [legacy, target] {
                // a directory store is probed through a file inside it
                let probe = if rel.rsplit('/').next().unwrap_or("").contains('.') {
                    rel.to_string()
                } else {
                    format!("{rel}/x.json")
                };
                let classes = any_match(&probe);
                assert!(
                    !classes.is_empty()
                        && classes
                            .iter()
                            .all(|c| !matches!(c.as_str(), "derived" | "generated" | "runtime")),
                    "{} at {probe}: rules matching it declare {classes:?}",
                    s.id
                );
            }
        }
    }
    let p = gov_runtime::Project::open(&root);
    let c = p.contract();
    for (path, class) in [
        ("spec/reports/checkpoints/CKPT-00001.yaml", "evidence"),
        ("spec/research/RES-0001.yaml", "evidence"),
        ("spec/audits/AUD-0001.yaml", "evidence"),
        ("spec/requirements/REQ-0001.yaml", "authoritative"),
        ("spec/decisions/D-0001.yaml", "authoritative"),
        ("product/tests/test_totals.py", "test"),
        ("product/app/totals.py", "source"),
        ("governance/registry/plugin-registry.json", "authoritative"),
        (".governance-state/claims.db", "operational"),
        (".governance-runtime/state.db", "derived"),
        ("governance/generated/index-manifest.json", "generated"),
    ] {
        assert_eq!(c.decide(path).class(), class, "{path}");
    }
    let mq = c.decide("spec/reports/memory-quality/FAIL-0001.yaml");
    assert_eq!(mq.class(), "evidence");
    assert!(
        !mq.flag("lexical_index") && !mq.flag("semantic_index") && !mq.flag("graph_index"),
        "{:?}",
        mq.attrs
    );
    let fj = json(&root, "framework.json");
    assert_eq!(
        fj["kernel_paths"][".governance-runtime/claims.db*"]["class"], "operational",
        "{fj}"
    );
    assert!(fj["precedence"].as_str().unwrap().contains("kernel_paths"));
    let (ok, msg) = doctor_check(&g, "D008");
    assert!(ok, "framework.json in sync: {msg}");
    // the overlay validates against its schema (the new class and mutation values are declared)
    let reg =
        gov_runtime::schemas::SchemaRegistry::new(&canonical_root().join("framework/schemas"));
    assert!(
        reg.errors("repository-contract", &rc).unwrap().is_empty(),
        "{:?}",
        reg.errors("repository-contract", &rc)
    );
}
