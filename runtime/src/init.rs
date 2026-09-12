//! `gov init`: greenfield onboarding (framework §78, protocol §9).
use crate::kernel::{install_kernel, resolve_kernel_source};
use crate::lock::write_lock;
use crate::util::{read_text, read_yaml, today, write_text, write_yaml};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};
use std::path::Path;

pub const SPEC_DIRS: &[&str] = &["now", "product", "features", "requirements", "architecture", "workflows", "interfaces", "scenarios", "data", "security", "performance", "research", "experiments", "decisions", "planning", "tasks", "reports", "reports/checkpoints", "lessons", "audits"];
pub const ARCHIVE_DIRS: &[&str] = &["governance", "spec", "research", "code-reference"];

pub struct InitOptions { pub source: Option<String>, pub project_name: String, pub alias: String, pub mode: String, pub force: bool, pub intent: Option<String>, pub skip_index: bool }

pub fn write_overlay(root: &Path, kernel_dir: &Path, opts: &InitOptions, contract_override: Option<Value>) -> Result<Vec<String>> {
    let tdir = kernel_dir.join("overlay-templates");
    let odir = root.join("governance").join("project");
    std::fs::create_dir_all(&odir)?;
    let mut written = vec![];
    for fname in crate::policy::OVERLAY_FILES.iter().map(|(f, _)| *f) {
        let dest = odir.join(fname);
        if dest.exists() && !opts.force { continue; }
        if fname == "REPOSITORY_CONTRACT.yaml" { if let Some(c) = &contract_override { write_yaml(&dest, c)?; written.push(fname.to_string()); continue; } }
        let tpl = tdir.join(fname);
        if !tpl.exists() { continue; } // older kernels may not ship every template
        let mut text = read_text(&tpl)?;
        for (k, v) in [("{{project_name}}", opts.project_name.as_str()), ("{{project_alias}}", opts.alias.as_str()), ("{{today}}", &today()), ("{{mode}}", opts.mode.as_str())] { text = text.replace(k, v); }
        write_text(&dest, &text)?;
        written.push(fname.to_string());
    }
    Ok(written)
}

/// Map a project's native layout into the repository contract instead of moving it (framework §8.1).
pub fn native_layout_rules(root: &Path) -> Vec<Value> {
    let mut rules = vec![];
    let Ok(rd) = std::fs::read_dir(root) else { return rules };
    let mut dirs: Vec<String> = rd.filter_map(|e| e.ok()).filter(|e| e.path().is_dir()).map(|e| e.file_name().to_string_lossy().to_string()).collect();
    dirs.sort();
    for d in dirs {
        if d.starts_with('.') || crate::paths::ALWAYS_EXCLUDED_DIRS.contains(&d.as_str()) || ["governance", "spec", "archive", "product", "docs", "fixtures", "release", "lessons", "change-proposals"].contains(&d.as_str()) { continue; }
        let has_code = crate::paths::iter_repo_files(&root.join(&d), false).iter().take(400).any(|(_, rel)| Path::new(rel).extension().map(|e| crate::capabilities::ecosystems::language_for_ext(&e.to_string_lossy()).is_some()).unwrap_or(false));
        if !has_code { continue; }
        let is_test = matches!(d.as_str(), "tests" | "test" | "__tests__" | "spec_tests" | "e2e");
        rules.push(json!({"pattern": format!("{d}/**"), "class": if is_test { "test" } else { "source" }, "owner_role": if is_test { "independent-test-designer" } else { "backend-engineer" }, "semantic_index": true, "lexical_index": true, "graph_index": true, "code_index": true, "namespace": "product"}));
    }
    rules
}

pub fn contract_with_native_layout(kernel_dir: &Path, root: &Path) -> Result<Value> {
    let mut c = read_yaml(&kernel_dir.join("overlay-templates").join("REPOSITORY_CONTRACT.yaml"))?;
    let native = native_layout_rules(root);
    if let Some(arr) = c["paths"].as_array_mut() { let mut merged = native.clone(); merged.extend(arr.clone()); *arr = merged; }
    c["capability_roots"] = json!({"native_source": native.iter().filter(|r| r["class"] == "source").map(|r| r["pattern"].clone()).collect::<Vec<_>>(), "native_tests": native.iter().filter(|r| r["class"] == "test").map(|r| r["pattern"].clone()).collect::<Vec<_>>()});
    Ok(c)
}

pub fn ensure_roots(root: &Path) -> Result<()> {
    for d in SPEC_DIRS { let p = root.join("spec").join(d); std::fs::create_dir_all(&p)?; let keep = p.join(".gitkeep"); if !keep.exists() && std::fs::read_dir(&p)?.next().is_none() { write_text(&keep, "")?; } }
    // ARCHIVE_POLICY.archive_root / archive_subdirs decide the archive layout
    let pr = Project::open(root);
    let (archive_root, subdirs): (String, Vec<String>) = if pr.is_installed() { let pol = pr.policies(); let subs = pol.get_list("ARCHIVE_POLICY", "archive_subdirs"); (pol.get_str("ARCHIVE_POLICY", "archive_root", "archive"), if subs.is_empty() { ARCHIVE_DIRS.iter().map(|s| s.to_string()).collect() } else { subs }) } else { ("archive".into(), ARCHIVE_DIRS.iter().map(|s| s.to_string()).collect()) };
    for d in &subdirs { let p = root.join(&archive_root).join(d); std::fs::create_dir_all(&p)?; let keep = p.join(".gitkeep"); if !keep.exists() && std::fs::read_dir(&p)?.next().is_none() { write_text(&keep, "")?; } }
    std::fs::create_dir_all(root.join("product"))?;
    std::fs::create_dir_all(root.join("governance").join("generated"))?;
    let tests = root.join("governance").join("tests").join("memory");
    std::fs::create_dir_all(&tests)?;
    let held = tests.join("heldout.yaml");
    if !held.exists() { write_yaml(&held, &json!({"version": "1", "queries": []}))?; }
    let gi = root.join(".gitignore");
    let mut text = read_text(&gi).unwrap_or_default();
    if !text.lines().any(|l| l.trim() == ".governance-runtime/" || l.trim() == ".governance-runtime") { if !text.is_empty() && !text.ends_with('\n') { text.push('\n'); } text.push_str(".governance-runtime/\n"); write_text(&gi, &text)?; }
    let now = root.join("spec").join("now").join("NOW.md");
    if !now.exists() { write_text(&now, "# NOW\n\nCurrent focus pointer (narrative, not authoritative). Authoritative state lives in governed records: run `gov status`.\n")?; }
    Ok(())
}

pub fn init(root: &Path, opts: InitOptions) -> Result<Value> {
    let gov = root.join("governance");
    if gov.join("framework.lock").exists() && !opts.force { return Err(GovError::new("ALREADY_INSTALLED", format!("{} already has a Governance OS installation (use gov update, or --force to reinstall the kernel)", root.display()))); }
    { let p0 = Project::open(root); if p0.is_installed() { crate::authority::require(&p0, "install_kernel")?; } else if crate::authority::parse_level(&format!("L{}", 0)).is_some() { /* uninstalled repository: authority is checked against the kernel being installed below */ } }
    let src = resolve_kernel_source(opts.source.as_deref().map(Path::new))?;
    std::fs::create_dir_all(&gov)?;
    let manifest = install_kernel(Some(&src), &gov)?;
    let commit = Project::open(root).git_commit();
    let lock = write_lock(&gov.join("framework.lock"), &manifest, &crate::kernel::source_label(&src), Some(&commit))?;
    let contract = contract_with_native_layout(&gov.join("kernel"), root)?;
    let overlay = write_overlay(root, &gov.join("kernel"), &opts, Some(contract))?;
    ensure_roots(root)?;
    let mut p = Project::open(root);
    p.invalidate();
    crate::authority::require(&p, "install_kernel").inspect_err(|_e| { let _ = std::fs::remove_file(gov.join("framework.lock")); })?;
    if let Some(intent) = &opts.intent {
        let store = crate::records::RecordStore::load(root);
        if store.of_type("project").is_empty() {
            let rec = crate::records::new_record("project", "PRJ-0001", &opts.project_name, json!({"mission": intent, "product_intent": intent, "outcomes": [], "actors": [], "state_class": "AUTHORITATIVE"}));
            crate::records::save_record(root, &rec)?;
        }
    }
    let registry = crate::tools::generate_registry(&p)?;
    let adapters = crate::adapters::generate(&p)?;
    let mut index = Value::Null;
    let mut heldout_generated = 0usize;
    if !opts.skip_index {
        let r = crate::memory::indexer::rebuild(&p, crate::memory::indexer::IndexOptions { incremental: false, ..Default::default() })?;
        index = json!({"artifacts": r.counts["artifacts"], "manifest_hash": r.manifest_hash, "excluded": r.excluded.len(), "ecosystems": r.ecosystems["count"], "embedder": r.embedder});
        // a starter held-out set so that memory recall is measured from day one (framework §17; verifier HV-20)
        let held = root.join(p.policies().get_str("MEMORY_POLICY", "regression.heldout_file", "governance/tests/memory/heldout.yaml"));
        let existing = read_yaml(&held).ok().and_then(|h| h["queries"].as_array().map(|a| a.len())).unwrap_or(0);
        if existing == 0 { let db = crate::memory::db::RuntimeDb::open(&p.db_path())?; let set = crate::memory::heldout::generate_starter(&p, &db, "gov init")?; heldout_generated = set["queries"].as_array().map(|a| a.len()).unwrap_or(0); drop(db); write_yaml(&held, &set)?; let _ = crate::memory::indexer::rebuild(&p, crate::memory::indexer::IndexOptions { incremental: true, ..Default::default() })?; }
    }
    let conformance = crate::verification::audit(&p, &crate::verification::SuiteOptions { deep: false, families: vec![] }, true)?;
    if !opts.skip_index { let _ = crate::memory::indexer::rebuild(&p, crate::memory::indexer::IndexOptions { incremental: true, ..Default::default() })?; }
    let doctor = crate::doctor::run(&p)?; // reported on the final, fresh state
    Ok(json!({"root": root.display().to_string(), "version": lock["version"], "release_hash": lock["release_hash"], "source": lock["source"], "kernel_files": manifest["files"].as_object().map(|m| m.len()).unwrap_or(0), "overlay_written": overlay, "tools": registry["tools"].as_array().map(|a| a.len()).unwrap_or(0), "adapters": adapters["adapters"].as_object().map(|m| m.len()).unwrap_or(0), "index": index, "heldout_generated": heldout_generated, "doctor": doctor.verdict, "conformance": {"audit": conformance["audit"], "verdict": conformance["verdict"]}}))
}
