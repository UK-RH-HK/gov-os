//! A2 classification: every material artefact receives a class and an authority status. No files move here.
use crate::records::parse_record_text;
use crate::util::read_text;
use serde_json::{json, Value};
use std::collections::{HashMap, HashSet};
use std::path::Path;

#[derive(Debug, Clone, serde::Serialize)]
pub struct LegacyItem {
    pub path: String,
    pub kind: String,
}

/// Legacy governance/memory mechanisms in the active tree (used by A2 and `gov doctor`).
pub fn legacy_mechanisms(root: &Path) -> Vec<LegacyItem> {
    let mut out = vec![];
    for (abs, rel) in crate::paths::iter_repo_files(root, false) {
        if rel.starts_with("governance/") || rel.starts_with("archive/") || rel.starts_with("spec/")
        {
            continue;
        }
        let kinds = super::inventory::detect_kinds(&rel, &abs);
        for k in [
            "provider_rules",
            "chat_store",
            "index_store",
            "old_governance",
        ] {
            if kinds.contains(&k) {
                out.push(LegacyItem {
                    path: rel.clone(),
                    kind: k.into(),
                });
                break;
            }
        }
    }
    out
}

fn kinds(item: &Value) -> Vec<String> {
    item["kinds"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|k| k.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default()
}

/// Build a reverse import graph over source files to detect dead/unused modules (heuristic, low confidence).
/// Import graph over the inventory: (importer path, imported path) edges resolved loosely by module stem.
fn import_edges(root: &Path, items: &[Value]) -> Vec<(String, String)> {
    let mut edges: Vec<(String, String)> = vec![];
    let plugins: Vec<crate::capabilities::protocol::PluginDescriptor> = vec![];
    for it in items {
        let rel = it["path"].as_str().unwrap_or("");
        let k = kinds(it);
        if !(k.contains(&"source".into()) || k.contains(&"test".into()))
            || k.contains(&"secret".into())
        {
            continue;
        }
        let ext = Path::new(rel)
            .extension()
            .map(|e| e.to_string_lossy().to_lowercase())
            .unwrap_or_default();
        let Some(lang) = super::inventory::language(&ext) else {
            continue;
        };
        let Ok(src) = read_text(&root.join(rel)) else {
            continue;
        };
        let facts = crate::code_intelligence::analyze(rel, lang, &src, &plugins, root);
        for imp in facts.imports {
            // resolve loosely: any file whose stem matches the last import segment
            let last = imp
                .trim_start_matches('.')
                .rsplit(['.', '/', ':'])
                .next()
                .unwrap_or("")
                .to_string();
            if last.is_empty() {
                continue;
            }
            for other in items {
                let op = other["path"].as_str().unwrap_or("");
                let stem = Path::new(op)
                    .file_stem()
                    .map(|s| s.to_string_lossy().to_string())
                    .unwrap_or_default();
                if op != rel
                    && (stem == last
                        || (stem == "__init__" && op.contains(&format!("/{last}/"))
                            || op.ends_with(&format!("{last}/mod.rs"))
                            || op.ends_with(&format!("{last}/index.ts"))
                            || op.ends_with(&format!("{last}/index.js"))))
                {
                    let e = (rel.to_string(), op.to_string());
                    if !edges.contains(&e) {
                        edges.push(e);
                    }
                }
            }
        }
    }
    edges
}

pub fn classify_all(root: &Path, items: &[Value]) -> Vec<Value> {
    let edges = import_edges(root, items);
    let imported: HashSet<String> = edges.iter().map(|(_, to)| to.clone()).collect();
    let mut records: HashMap<String, Value> = HashMap::new();
    let mut supersedes: HashMap<String, String> = HashMap::new(); // superseded id -> superseder
    for it in items {
        let rel = it["path"].as_str().unwrap_or("");
        if (rel.ends_with(".yaml") || rel.ends_with(".yml") || rel.ends_with(".md"))
            && !kinds(it).contains(&"secret".into())
        {
            if let Ok(text) = read_text(&root.join(rel)) {
                if let Some(r) = parse_record_text(&text, rel) {
                    for s in r.list("supersedes") {
                        supersedes.insert(s, r.id());
                    }
                    records.insert(rel.to_string(), r.data.clone());
                }
            }
        }
    }
    let mut out = vec![];
    let mut n = 0usize;
    for it in items {
        n += 1;
        let rel = it["path"].as_str().unwrap_or("").to_string();
        let k = kinds(it);
        let has = |x: &str| k.iter().any(|y| y == x);
        let mut reasons = vec![];
        let (mut class, mut authority, mut confidence) =
            ("UNKNOWN", "UNKNOWN_OR_CONFLICTING", 0.4f64);
        let text_head = if !has("binary") && !has("secret") {
            read_text(&root.join(&rel))
                .map(|t| t.chars().take(4000).collect::<String>())
                .unwrap_or_default()
        } else {
            String::new()
        };
        let low = text_head.to_lowercase();
        if has("secret") {
            class = "SECRET";
            authority = "ACTIVE";
            confidence = 0.99;
            reasons.push("secret path pattern or secret content pattern".into());
        } else if rel.starts_with("governance/kernel/")
            || rel.starts_with("governance/project/")
            || rel == "governance/framework.lock"
        {
            class = "GOVERNANCE_CURRENT";
            authority = "ACTIVE";
            confidence = 0.99;
            reasons.push("installed Governance OS".into());
        } else if rel.starts_with("archive/") {
            class = "HISTORICAL";
            authority = "HISTORICAL";
            confidence = 0.95;
            reasons.push("under archive/".into());
        } else if has("provider_rules") {
            class = "GOVERNANCE_LEGACY";
            authority = "LEGACY";
            confidence = 0.95;
            reasons
                .push("provider/IDE-specific agent rule file (pre-v4 governance mechanism)".into());
        } else if has("chat_store") {
            class = "HISTORICAL";
            authority = "LEGACY";
            confidence = 0.9;
            reasons.push(
                "chat/session memory store; not active project memory (framework §70)".into(),
            );
        } else if has("index_store") {
            class = "GENERATED";
            authority = "LEGACY";
            confidence = 0.9;
            reasons
                .push("derived index/vector store; rebuildable, stale after path migration".into());
        } else if has("old_governance") && has("doc") {
            class = if low.contains("decision")
                || rel.to_lowercase().contains("decision")
                || rel.to_lowercase().contains("adr")
            {
                "DECISION"
            } else if low.contains("lesson") {
                "LESSON"
            } else {
                "GOVERNANCE_LEGACY"
            };
            authority = if low.contains("superseded")
                || low.contains("deprecated")
                || low.contains("obsolete")
            {
                "SUPERSEDED"
            } else {
                "LEGACY"
            };
            confidence = 0.75;
            reasons.push("legacy governance/decision document outside spec/; extract durable knowledge then retire".into());
        } else if let Some(rd) = records.get(&rel) {
            let t = rd["type"].as_str().unwrap_or("");
            let st = rd["status"].as_str().unwrap_or("ACTIVE");
            let id = rd["id"].as_str().unwrap_or("");
            class = match t {
                "decision" => "DECISION",
                "lesson" => "LESSON",
                "task" => "TASK",
                "report" | "audit" | "checkpoint" => "REPORT_EVIDENCE",
                "research" | "experiment" => "RESEARCH_EVIDENCE",
                _ => {
                    if rel.starts_with("spec/") {
                        "SPEC_AUTHORITATIVE"
                    } else {
                        "SPEC_DERIVED"
                    }
                }
            };
            authority = if supersedes.contains_key(id) && st == "ACTIVE" {
                reasons.push(format!(
                    "record is superseded by {} but still ACTIVE: contradiction",
                    supersedes[id]
                ));
                "UNKNOWN_OR_CONFLICTING"
            } else if supersedes.contains_key(id) {
                "SUPERSEDED"
            } else {
                match st {
                    "ACTIVE" => "ACTIVE",
                    "PROVISIONAL" => "PROVISIONAL",
                    "SUPERSEDED" => "SUPERSEDED",
                    "LEGACY" => "LEGACY",
                    "HISTORICAL" => "HISTORICAL",
                    "REJECTED" => "REJECTED",
                    _ => "UNKNOWN_OR_CONFLICTING",
                }
            };
            confidence = 0.9;
            reasons.push(format!("governed record type {t} status {st}"));
            reasons.push("record".into());
            if !rel.starts_with("spec/") && !rel.starts_with("governance/") {
                reasons.push("record located outside spec/ (misplaced)".into());
                confidence = 0.8;
            }
        } else if has("test") {
            class = "PRODUCT_TEST";
            authority = "ACTIVE";
            confidence = 0.9;
            reasons.push("test file by path/name convention".into());
            if rel.starts_with("docs/") || rel.starts_with("spec/") {
                reasons.push("test located under docs/spec (misplaced)".into());
            }
        } else if has("generated") {
            class = "GENERATED";
            authority = "HISTORICAL";
            confidence = 0.85;
            reasons.push("build output / generated artefact".into());
        } else if has("devops") {
            class = "DEVOPS";
            authority = "ACTIVE";
            confidence = 0.9;
            reasons.push("CI/CD or infrastructure definition".into());
        } else if has("source") {
            let entry = has("entrypoint")
                || rel.ends_with("__init__.py")
                || rel.ends_with("mod.rs")
                || rel.ends_with("lib.rs")
                || rel.ends_with("main.rs");
            if !entry && !imported.contains(&rel) && !has("package_manifest") {
                class = "DEAD_OR_UNUSED";
                authority = "UNKNOWN_OR_CONFLICTING";
                confidence = 0.5;
                reasons.push("no import/reference found from any other source or test (heuristic; requires human confirmation before removal)".into());
            } else {
                class = "PRODUCT_SOURCE";
                authority = "ACTIVE";
                confidence = 0.9;
                reasons.push("source code (native layout preserved)".into());
            }
            if rel.starts_with("docs/") || rel.starts_with("spec/") {
                reasons.push("source located under docs/spec (misplaced)".into());
            }
        } else if has("package_manifest") {
            class = "TOOLING";
            authority = "ACTIVE";
            confidence = 0.95;
            reasons.push("package/build manifest".into());
        } else if has("database") {
            class = "DATA_RUNTIME";
            authority = "ACTIVE";
            confidence = 0.6;
            reasons.push("database file (inspect for unique knowledge before retirement)".into());
        } else if has("data") {
            class = if rel.contains("test") || rel.contains("fixture") {
                "DATA_TEST"
            } else {
                "DATA_RUNTIME"
            };
            authority = "ACTIVE";
            confidence = 0.7;
            reasons.push("data file".into());
        } else if has("research") && has("doc") {
            class = "RESEARCH_EVIDENCE";
            authority = "ACTIVE";
            confidence = 0.7;
            reasons.push("research/experiment narrative".into());
        } else if has("report") && has("doc") {
            class = "REPORT_EVIDENCE";
            authority = "ACTIVE";
            confidence = 0.7;
            reasons.push("report/audit narrative".into());
        } else if has("spec_doc")
            || (has("doc")
                && (low.contains("requirement")
                    || low.contains("shall")
                    || low.contains("acceptance")))
        {
            class = "SPEC_AUTHORITATIVE";
            authority = if low.contains("superseded") || low.contains("deprecated") {
                "SUPERSEDED"
            } else {
                "PROVISIONAL"
            };
            confidence = 0.65;
            reasons.push(
                "specification-like document (provisional until normalised into spec/ records)"
                    .into(),
            );
            if !rel.starts_with("spec/") {
                reasons.push("located outside spec/ (misplaced)".into());
            }
        } else if has("doc") {
            class = "SPEC_DERIVED";
            authority = "ACTIVE";
            confidence = 0.6;
            reasons.push("narrative documentation".into());
        } else if has("config") {
            class = "TOOLING";
            authority = "ACTIVE";
            confidence = 0.7;
            reasons.push("configuration".into());
        } else if has("binary") {
            class = "DATA_RUNTIME";
            authority = "ACTIVE";
            confidence = 0.5;
            reasons.push("binary file".into());
        }
        let imports: Vec<&str> = edges
            .iter()
            .filter(|(from, _)| from == &rel)
            .map(|(_, to)| to.as_str())
            .collect();
        let references: Vec<&str> = edges
            .iter()
            .filter(|(_, to)| to == &rel)
            .map(|(from, _)| from.as_str())
            .collect();
        out.push(json!({"artifact_id": format!("ART-{n:05}"), "path": rel, "class": class, "authority": authority, "confidence": confidence, "reasons": reasons, "kinds": k, "git_tracked": it["git_tracked"], "size": it["size"], "hash": it["hash"], "imports": imports, "references": references}));
    }
    out
}

pub fn legacy_map_markdown(classified: &[Value]) -> String {
    let mut s = String::from("# 03 — Legacy governance map\n\nMechanisms that must not remain accidentally authoritative (INV-004). Each is retired or archived by the migration plan.\n\n| Path | Class | Authority | Reason |\n|---|---|---|---|\n");
    for c in classified.iter().filter(|c| {
        c["authority"] == "LEGACY"
            || c["class"] == "GOVERNANCE_LEGACY"
            || c["authority"] == "UNKNOWN_OR_CONFLICTING"
    }) {
        s.push_str(&format!(
            "| {} | {} | {} | {} |\n",
            c["path"].as_str().unwrap_or(""),
            c["class"].as_str().unwrap_or(""),
            c["authority"].as_str().unwrap_or(""),
            c["reasons"]
                .as_array()
                .map(|a| a
                    .iter()
                    .map(|r| r.as_str().unwrap_or("").to_string())
                    .collect::<Vec<_>>()
                    .join("; "))
                .unwrap_or_default()
        ));
    }
    s
}
