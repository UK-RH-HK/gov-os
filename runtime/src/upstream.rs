//! Upstream learning pipeline and Export Gate (framework §75E-G, protocol §13-14, INV-012 fail closed).
use crate::records::{save_record, RecordStore};
use crate::util::{glob_match, hash_value, now_iso, read_json, write_json, write_yaml};
use crate::{GovError, Project, Result};
use regex::Regex;
use serde_json::{json, Value};
use std::path::Path;

fn redact_identifiers(text: &str, identifiers: &[String]) -> (String, usize) {
    let mut out = text.to_string(); let mut n = 0;
    for id in identifiers { if id.len() < 3 { continue; } let rx = Regex::new(&format!("(?i){}", regex::escape(id))).unwrap(); let c = rx.find_iter(&out).count(); if c > 0 { n += c; out = rx.replace_all(&out, "[REDACTED]").to_string(); } }
    (out, n)
}

fn strip_paths(text: &str, forbidden: &[String]) -> (String, Vec<String>) {
    let rx = Regex::new(r"(?:/[\w.\-]+){2,}|(?:[\w.\-]+/){1,}[\w.\-]+\.[A-Za-z0-9]{1,6}").unwrap();
    let mut removed = vec![]; let mut out = text.to_string();
    for m in rx.find_iter(text) { let s = m.as_str(); if forbidden.iter().any(|f| glob_match(f, s.trim_start_matches('/'))) || s.starts_with('/') { removed.push(s.to_string()); } }
    for r in &removed { out = out.replace(r, "[PATH-REMOVED]"); }
    (out, removed)
}

fn code_lines(text: &str) -> usize {
    let mut n = 0; let mut in_fence = false;
    for l in text.lines() { if l.trim_start().starts_with("```") { in_fence = !in_fence; continue; } if in_fence { n += 1; } }
    n
}

pub fn outbound_dir(p: &Project) -> std::path::PathBuf { p.runtime_dir().join("outbound") }

/// `gov upstream prepare <lesson-id>`: build a sanitised packet or fail closed with reasons.
pub fn prepare(p: &Project, lesson_id: &str) -> Result<Value> {
    p.require_installed()?;
    let pol = p.policies();
    let store = RecordStore::load(&p.root);
    let lesson = store.get(lesson_id).ok_or_else(|| GovError::new("LESSON_NOT_FOUND", format!("{lesson_id} not found")))?;
    if lesson.rtype() != "lesson" { return Err(GovError::new("USAGE", format!("{lesson_id} is not a lesson"))); }
    let eligible = pol.get_list("LEARNING_POLICY", "upstream_eligible_scopes");
    let scope = lesson.get("scope");
    if !eligible.contains(&scope) { return Err(GovError::new("UPSTREAM_SCOPE", format!("lesson {lesson_id} has scope {scope}; only {eligible:?} lessons may be exported (framework §75E)"))); }
    let forbidden_paths = pol.get_list("LEARNING_POLICY", "upstream.forbidden_paths");
    let max_code = pol.get_i64("LEARNING_POLICY", "upstream.max_code_lines_unless_synthetic", 0) as usize;
    let metrics_enabled = pol.get_bool("LEARNING_POLICY", "upstream.aggregate_metrics_enabled", false);
    let mut identifiers: Vec<String> = p.secret_scanner().identifiers.clone();
    identifiers.push(p.project_name());
    identifiers.push(p.root.file_name().map(|f| f.to_string_lossy().to_string()).unwrap_or_default());
    let mut scans = json!({"identifiers_redacted": 0, "paths_removed": [], "secret_hits": [], "code_lines": 0, "blocked_reasons": []});
    let mut blocked: Vec<String> = vec![];
    let mut sanitize = |field: &str| -> String {
        let raw = lesson.get(field);
        let (t1, n) = redact_identifiers(&raw, &identifiers);
        scans["identifiers_redacted"] = json!(scans["identifiers_redacted"].as_u64().unwrap_or(0) + n as u64);
        let (t2, removed) = strip_paths(&t1, &forbidden_paths);
        for r in removed { scans["paths_removed"].as_array_mut().unwrap().push(json!(r)); }
        let hits = p.secret_scanner().scan_text(&t2, field);
        for h in hits { scans["secret_hits"].as_array_mut().unwrap().push(json!({"field": field, "pattern": h.pattern_id})); blocked.push(format!("secret pattern {} in field {field}", h.pattern_id)); }
        let cl = code_lines(&t2);
        scans["code_lines"] = json!(scans["code_lines"].as_u64().unwrap_or(0) + cl as u64);
        t2
    };
    let problem = sanitize("problem_statement"); let failure = sanitize("generic_failure_mode"); let impact = sanitize("impact"); let change = sanitize("suggested_change");
    let body = sanitize("body");
    let synthetic = lesson.data.get("synthetic_reproducer").cloned();
    let mut fixture: Option<Value> = None;
    if let Some(sf) = &synthetic {
        if sf.get("synthetic").and_then(|v| v.as_bool()) != Some(true) { blocked.push("synthetic_reproducer must declare synthetic: true".into()); }
        let mut files = serde_json::Map::new();
        for (name, content) in sf.get("files").and_then(|f| f.as_object()).cloned().unwrap_or_default() {
            let text = content.as_str().unwrap_or("").to_string();
            if forbidden_paths.iter().any(|f| glob_match(f, &name)) { blocked.push(format!("fixture file {name} matches a forbidden outbound path")); }
            let (t1, _) = redact_identifiers(&text, &identifiers);
            if !p.secret_scanner().scan_text(&t1, &name).is_empty() { blocked.push(format!("secret pattern in fixture file {name}")); }
            files.insert(name, json!(t1));
        }
        fixture = Some(json!({"synthetic": true, "description": sf.get("description").cloned().unwrap_or(json!("")), "files": files}));
    }
    let total_code = scans["code_lines"].as_u64().unwrap_or(0) as usize;
    if total_code > max_code && fixture.is_none() { blocked.push(format!("{total_code} raw code line(s) in lesson text exceed policy max {max_code}; provide a synthetic reproducer instead")); }
    if body.len() > 4000 { blocked.push("lesson body too long for an abstraction packet (>4000 chars): summarise".into()); }
    let metrics = if metrics_enabled { lesson.data.get("aggregate_metrics").cloned() } else { None };
    let existing = std::fs::read_dir(outbound_dir(p)).map(|rd| rd.count()).unwrap_or(0);
    let packet_id = format!("PKT-{:04}", existing + 1);
    let mut packet = json!({"packet_id": packet_id, "lesson_id": lesson_id, "scope": "FRAMEWORK", "category": lesson.get("category"), "problem_statement": problem, "generic_failure_mode": failure, "impact": impact,
        "evidence_strength": if lesson.get("evidence_strength").is_empty() { "low".to_string() } else { lesson.get("evidence_strength") }, "suggested_framework_change": change, "source_project_alias": p.project_alias(), "local_reference": lesson_id,
        "sensitive_content_removed": true, "raw_product_code_included": false, "raw_customer_data_included": false, "raw_spec_included": false, "synthetic_fixture": fixture, "metrics": metrics, "prepared_at": now_iso(), "framework_version": p.framework_version(), "approval": {"required": pol.get_str("LEARNING_POLICY", "upstream.approval", "human"), "approved_by": null}});
    if let Some(a) = packet["source_project_alias"].as_str() { if identifiers.iter().any(|i| i.eq_ignore_ascii_case(a)) { blocked.push("project alias equals a project identifier; set a non-identifying alias in PROJECT_POLICY".into()); } }
    scans["blocked_reasons"] = json!(blocked);
    packet["scans"] = scans.clone();
    let errs = p.schemas().errors("upstream-packet", &packet)?;
    let mut blocked_all = blocked.clone(); blocked_all.extend(errs.iter().map(|e| format!("schema: {e}")));
    let dir = outbound_dir(p).join(packet["packet_id"].as_str().unwrap_or("PKT"));
    std::fs::create_dir_all(&dir)?;
    if !blocked_all.is_empty() {
        write_json(&dir.join("blocked.json"), &json!({"lesson": lesson_id, "reasons": blocked_all, "scans": scans, "at": now_iso()}))?;
        return Err(GovError::new("UPSTREAM_BLOCKED", format!("export gate failed closed for {lesson_id}: {}", blocked_all.join("; "))).with_details(json!({"reasons": blocked_all, "scans": scans})));
    }
    let payload_hash = hash_value(&json!({"p": packet["problem_statement"], "f": packet["generic_failure_mode"], "i": packet["impact"], "c": packet["suggested_framework_change"], "x": packet["synthetic_fixture"], "m": packet["metrics"]}));
    packet["payload_hash"] = json!(payload_hash);
    write_yaml(&dir.join("packet.yaml"), &packet)?;
    write_json(&dir.join("scans.json"), &scans)?;
    Ok(json!({"packet_id": packet["packet_id"], "path": dir.join("packet.yaml").display().to_string(), "payload_hash": payload_hash, "scans": scans, "export_allowed": true, "approval_required": packet["approval"]["required"]}))
}

/// `gov upstream submit <packet-id> --destination <canonical lessons/inbox dir> --approved-by <human>`.
pub fn submit(p: &Project, packet_id: &str, destination: &str, approved_by: Option<&str>) -> Result<Value> {
    p.require_installed()?;
    let pol = p.policies();
    let dir = outbound_dir(p).join(packet_id);
    let packet_path = dir.join("packet.yaml");
    if !packet_path.exists() { return Err(GovError::new("PACKET_NOT_FOUND", format!("{packet_id} not prepared (run gov upstream prepare)"))); }
    let mut packet = crate::util::read_yaml(&packet_path)?;
    p.schemas().validate("upstream-packet", &packet, "(packet)")?;
    let scans = read_json(&dir.join("scans.json")).unwrap_or(json!({}));
    if !scans["blocked_reasons"].as_array().map(|a| a.is_empty()).unwrap_or(false) { return Err(GovError::new("UPSTREAM_BLOCKED", "packet has blocked reasons")); }
    // re-scan at submission (content could have been edited)
    for f in ["problem_statement", "generic_failure_mode", "impact", "suggested_framework_change"] { if !p.secret_scanner().scan_text(packet[f].as_str().unwrap_or(""), f).is_empty() { return Err(GovError::new("UPSTREAM_BLOCKED", format!("secret pattern in {f} at submission"))); } }
    for flag in ["raw_product_code_included", "raw_customer_data_included", "raw_spec_included"] { if packet[flag].as_bool() != Some(false) { return Err(GovError::new("UPSTREAM_BLOCKED", format!("{flag} must be false"))); } }
    let approval = pol.get_str("LEARNING_POLICY", "upstream.approval", "human");
    if approval == "human" && approved_by.map(|s| s.is_empty()).unwrap_or(true) { return Err(GovError::new("HUMAN_GATE_REQUIRED", "LEARNING_POLICY.upstream.approval=human: --approved-by <human> is required")); }
    if destination.starts_with("http://") || destination.starts_with("https://") || destination.starts_with("git@") { return Err(GovError::new("REMOTE_TRANSPORT_NOT_CONFIGURED", "remote destinations are not supported by this release; submit to a local clone of the canonical repository (lessons/inbox/)")); }
    let dest = Path::new(destination);
    if !dest.is_dir() || !dest.ends_with("inbox") { return Err(GovError::new("UPSTREAM_DESTINATION", format!("destination must be an existing lessons/inbox directory (got {destination})"))); }
    // outbound allowlist: exactly packet.yaml (+ fixture files embedded in the packet). Nothing else leaves.
    let allowed = pol.get_list("LEARNING_POLICY", "upstream.allowed_payload");
    if !allowed.iter().any(|a| a == "packet") { return Err(GovError::new("UPSTREAM_BLOCKED", "policy does not allow packet export")); }
    packet["approval"] = json!({"required": approval, "approved_by": approved_by, "approved_at": now_iso()});
    let target_dir = dest.join(packet_id.to_string() + "-" + p.project_alias().as_str());
    std::fs::create_dir_all(&target_dir)?;
    write_yaml(&target_dir.join("packet.yaml"), &packet)?;
    let mut sent = vec!["packet.yaml".to_string()];
    if let Some(fx) = packet["synthetic_fixture"].as_object() { if allowed.iter().any(|a| a == "synthetic_fixture") { for (name, content) in fx.get("files").and_then(|f| f.as_object()).cloned().unwrap_or_default() { let safe = name.replace("..", "_").trim_start_matches('/').to_string(); let path = target_dir.join("fixture").join(&safe); if let Some(d) = path.parent() { std::fs::create_dir_all(d)?; } crate::util::write_text(&path, content.as_str().unwrap_or(""))?; sent.push(format!("fixture/{safe}")); } } }
    let entry = json!({"at": now_iso(), "packet_id": packet_id, "lesson_id": packet["lesson_id"], "payload_hash": packet["payload_hash"], "destination": target_dir.display().to_string(), "approved_by": approved_by, "session": p.session_id, "files": sent});
    let ledger = p.root.join(pol.get_str("LEARNING_POLICY", "upstream.ledger", "spec/reports/upstream-ledger.jsonl"));
    let mut text = crate::util::read_text(&ledger).unwrap_or_default(); text.push_str(&serde_json::to_string(&entry)?); text.push('\n'); crate::util::write_text(&ledger, &text)?;
    let mut store = RecordStore::load(&p.root);
    if let Some(l) = store.get_mut(packet["lesson_id"].as_str().unwrap_or("")) { l.set("lifecycle", json!("promoted")); l.set("upstream", json!({"packet_id": packet_id, "payload_hash": packet["payload_hash"], "at": now_iso()})); save_record(&p.root, l)?; }
    Ok(entry)
}
