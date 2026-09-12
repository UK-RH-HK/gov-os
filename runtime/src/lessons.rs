//! Framework lesson intake (protocol §15): cluster inbox packets, apply LEARNING_POLICY.release_triggers and emit
//! Framework Change Proposal records. Runs in the canonical repository (no governed project required).
use crate::util::{now_iso, read_yaml, write_yaml};
use crate::{GovError, Result};
use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::path::Path;

fn key_of(pk: &Value) -> String {
    let cat = pk["category"].as_str().unwrap_or("uncategorised").to_lowercase();
    let mut toks: Vec<String> = crate::memory::embeddings::tokenize(pk["generic_failure_mode"].as_str().unwrap_or("")).into_iter().filter(|t| t.len() > 3).collect();
    toks.sort(); toks.dedup(); toks.truncate(6);
    format!("{cat}|{}", toks.join(","))
}

pub fn cluster(inbox: &Path, proposals_dir: &Path, learning_policy: &Value, write: bool) -> Result<Value> {
    let Ok(rd) = std::fs::read_dir(inbox) else { return Err(GovError::new("USAGE", format!("inbox {} not found", inbox.display()))) };
    let mut packets = vec![];
    let mut dirs: Vec<_> = rd.filter_map(|e| e.ok()).map(|e| e.path()).filter(|d| d.join("packet.yaml").exists()).collect();
    dirs.sort();
    for d in dirs { if let Ok(pk) = read_yaml(&d.join("packet.yaml")) { packets.push((d.file_name().unwrap().to_string_lossy().to_string(), pk)); } }
    let mut clusters: BTreeMap<String, Vec<(String, Value)>> = BTreeMap::new();
    for (name, pk) in packets { clusters.entry(key_of(&pk)).or_default().push((name, pk)); }
    let triggers = learning_policy.get("release_triggers").cloned().unwrap_or(json!({}));
    let mut out = vec![]; let mut written = vec![];
    let existing = std::fs::read_dir(proposals_dir).map(|rd| rd.filter_map(|e| e.ok()).filter(|e| e.file_name().to_string_lossy().starts_with("FCP-")).count()).unwrap_or(0);
    let mut n = existing;
    for (key, items) in &clusters {
        let projects: std::collections::BTreeSet<String> = items.iter().filter_map(|(_, pk)| pk["source_project_alias"].as_str().map(|s| s.to_string())).collect();
        let strengths: Vec<String> = items.iter().map(|(_, pk)| pk["evidence_strength"].as_str().unwrap_or("low").to_string()).collect();
        let critical = items.iter().any(|(_, pk)| pk["impact"].as_str().map(|s| s.to_lowercase().contains("critical") || s.to_lowercase().contains("credential")).unwrap_or(false));
        let (trigger, action) = if critical { ("critical_defect", triggers["critical_defect"].as_str().unwrap_or("immediate_patch_candidate")) } else if projects.len() >= 2 { ("cross_project_repeat", triggers["cross_project_repeat"].as_str().unwrap_or("strong_change_candidate")) } else if items.len() >= 3 { ("repeated_low_level", triggers["repeated_low_level"].as_str().unwrap_or("batched_minor_release")) } else { ("single_lesson", "accumulate") };
        let confidence = if strengths.iter().any(|s| s == "high") { 0.8 } else if strengths.iter().any(|s| s == "medium") { 0.6 } else { 0.4 };
        let mut entry = json!({"cluster": key, "packets": items.iter().map(|(n, _)| n).collect::<Vec<_>>(), "projects": projects.len(), "severity": strengths, "trigger": trigger, "release_action": action, "confidence": confidence, "suggested_change": items[0].1["suggested_framework_change"]});
        if write && action != "accumulate" {
            n += 1;
            let id = format!("FCP-{n:04}");
            let rec = json!({"id": id, "type": "framework-change-proposal", "title": format!("{}: {}", items[0].1["category"].as_str().unwrap_or("change"), items[0].1["problem_statement"].as_str().unwrap_or("").chars().take(80).collect::<String>()), "status": "PROVISIONAL", "state_class": "AUTHORITATIVE", "created": crate::util::today(), "cluster_key": key, "packets": items.iter().map(|(n, _)| n).collect::<Vec<_>>(), "source_projects": projects.len(), "trigger": trigger, "release_action": action, "confidence": confidence, "problem_statement": items[0].1["problem_statement"], "generic_failure_mode": items[0].1["generic_failure_mode"], "suggested_framework_change": items[0].1["suggested_framework_change"], "evidence_strength": strengths, "next": "implement in the canonical repository, add a synthetic regression fixture, independent review, release", "created_at": now_iso()});
            std::fs::create_dir_all(proposals_dir)?;
            write_yaml(&proposals_dir.join(format!("{id}.yaml")), &rec)?;
            entry["proposal"] = json!(id); written.push(id);
        }
        out.push(entry);
    }
    Ok(json!({"inbox": inbox.display().to_string(), "clusters": out, "proposals_written": written}))
}
