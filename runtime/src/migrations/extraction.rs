//! A8 legacy knowledge extraction — R1 "extract useful decisions/lessons/skills/evidence/research", R2 "unique
//! durable knowledge extracted" (framework §69, §70; Contract v3:876, :883; BC-P2-33).
//!
//! Extraction is **not gated on cue words**. Every substantive knowledge unit of a legacy store is either distilled
//! into a governed PROVISIONAL record of the kind it most plausibly is — decision, lesson, skill candidate, research
//! note, evidence claim — or listed verbatim in the store's residual-knowledge register (a PROVISIONAL report record)
//! for human review. Nothing unique is silently lost when the store is retired: a unit that is neither distilled nor
//! registered does not exist. Units carrying secret material are never copied anywhere; the register records only
//! how many were withheld.
//!
//! Classification is a heuristic and says so: every record carries `extraction.kind_basis` and stays PROVISIONAL
//! (lessons are evidence, not authority; research and evidence claims are NARRATIVE until a governed record with
//! method, sources and uncertainty confirms them).
use super::identity;
use crate::records::{new_record, save_record, Record};
use crate::util::read_text;
use crate::Result;
use serde_json::{json, Value};
use std::collections::HashSet;
use std::path::Path;

/// Minimum length of a knowledge unit (shorter strings are identifiers, roles, timestamps).
pub const MIN_UNIT_CHARS: usize = 21;

const DECISION_CUES: &[&str] = &[
    "decision:",
    "decided",
    "we will ",
    "we chose",
    "agreed to",
    "must use",
    "policy:",
];
const LESSON_CUES: &[&str] = &[
    "lesson:",
    "learned",
    "lesson learned",
    "in future",
    "root cause",
    "never again",
    "mistake",
    "retrospective",
    "postmortem",
    "post-mortem",
];
const SKILL_CUES: &[&str] = &[
    "procedure",
    "runbook",
    "playbook",
    "checklist",
    "how to ",
    "how-to",
    "steps:",
    "step 1",
    "to release",
    "to deploy",
];
const RESEARCH_CUES: &[&str] = &[
    "research",
    "benchmark",
    "measured",
    "measurement",
    "experiment",
    "we tested",
    "latency",
    "throughput",
    "p95",
    "p99",
    " rps",
    "per second",
    "profil",
    "we found",
    "study",
];
const EVIDENCE_CUES: &[&str] = &[
    "evidence",
    "test report",
    "load test",
    "report shows",
    "shows zero",
    "verified",
    "audit",
    "incident",
    "log shows",
    "confirmed by",
];

/// The kind a knowledge unit most plausibly is, and the cue that decided it.
pub fn classify_unit(s: &str) -> (&'static str, String) {
    let low = s.to_lowercase();
    let cue = |cues: &[&str]| {
        cues.iter()
            .find(|c| low.contains(*c))
            .map(|c| c.to_string())
    };
    if let Some(c) = cue(DECISION_CUES) {
        return ("decision", format!("cue '{c}'"));
    }
    if let Some(c) = cue(LESSON_CUES) {
        return ("lesson", format!("cue '{c}'"));
    }
    let numbered = regex::Regex::new(r"(?m)(^|\s)(1[.)]|step\s*1)\s")
        .unwrap()
        .is_match(&low)
        && regex::Regex::new(r"(^|\s)2[.)]\s").unwrap().is_match(&low);
    if numbered {
        return ("skill", "numbered procedure steps".into());
    }
    if let Some(c) = cue(SKILL_CUES) {
        return ("skill", format!("cue '{c}'"));
    }
    if let Some(c) = cue(RESEARCH_CUES) {
        return ("research", format!("cue '{c}'"));
    }
    if let Some(c) = cue(EVIDENCE_CUES) {
        return ("evidence", format!("cue '{c}'"));
    }
    let trimmed = s.trim();
    if trimmed.ends_with('?') && trimmed.len() < 160 {
        return ("question", "a question, not an assertion".into());
    }
    ("fact", "no cue: unique statement kept for review".into())
}

fn extract_strings_from_sqlite(path: &Path) -> Vec<String> {
    let mut out = vec![];
    let Ok(conn) =
        rusqlite::Connection::open_with_flags(path, rusqlite::OpenFlags::SQLITE_OPEN_READ_ONLY)
    else {
        return out;
    };
    let tables: Vec<String> = conn
        .prepare("SELECT name FROM sqlite_master WHERE type='table'")
        .ok()
        .and_then(|mut s| {
            s.query_map([], |r| r.get::<_, String>(0))
                .ok()
                .map(|it| it.filter_map(|x| x.ok()).collect())
        })
        .unwrap_or_default();
    for t in tables {
        let Ok(mut stmt) = conn.prepare(&format!(
            "SELECT * FROM \"{}\" LIMIT 20000",
            t.replace('"', "")
        )) else {
            continue;
        };
        let n = stmt.column_count();
        let Ok(rows) = stmt.query_map([], |r| {
            let mut v = vec![];
            for i in 0..n {
                if let Ok(s) = r.get::<_, String>(i) {
                    v.push(s);
                }
            }
            Ok(v)
        }) else {
            continue;
        };
        for r in rows.flatten() {
            for s in r {
                if s.len() >= MIN_UNIT_CHARS {
                    out.push(s);
                }
            }
        }
    }
    out
}

fn push_json_strings(v: &Value, out: &mut Vec<String>) {
    match v {
        Value::String(s) if s.len() >= MIN_UNIT_CHARS => out.push(s.clone()),
        Value::Array(a) => a.iter().for_each(|x| push_json_strings(x, out)),
        Value::Object(o) => {
            for (k, x) in o {
                // identifiers, roles and timestamps are not knowledge; every other string field is a candidate
                if matches!(
                    k.as_str(),
                    "id" | "role" | "session" | "ts" | "timestamp" | "created" | "time" | "uuid"
                ) {
                    continue;
                }
                push_json_strings(x, out);
            }
        }
        _ => {}
    }
}

fn extract_strings_from_json(text: &str) -> Vec<String> {
    let mut out = vec![];
    if let Ok(v) = serde_json::from_str::<Value>(text) {
        push_json_strings(&v, &mut out);
    } else {
        for l in text.lines() {
            match serde_json::from_str::<Value>(l) {
                Ok(v) => push_json_strings(&v, &mut out),
                Err(_) if l.trim().len() >= MIN_UNIT_CHARS => out.push(l.trim().to_string()),
                Err(_) => {}
            }
        }
    }
    out
}

/// String literals of a SQL text dump (`'...'` with `''` escapes).
fn extract_strings_from_sql(text: &str) -> Vec<String> {
    let mut out = vec![];
    let b: Vec<char> = text.chars().collect();
    let mut i = 0;
    while i < b.len() {
        if b[i] == '\'' {
            let mut s = String::new();
            i += 1;
            while i < b.len() {
                if b[i] == '\'' {
                    if i + 1 < b.len() && b[i + 1] == '\'' {
                        s.push('\'');
                        i += 2;
                        continue;
                    }
                    break;
                }
                s.push(b[i]);
                i += 1;
            }
            if s.len() >= MIN_UNIT_CHARS {
                out.push(s);
            }
        }
        i += 1;
    }
    out
}

/// Paragraphs of a text/markdown document, with bullet lists split into one unit per item and headings dropped.
fn extract_units_from_text(text: &str) -> Vec<String> {
    let mut out = vec![];
    let bullet = regex::Regex::new(r"^\s*(?:[-*+]|\d+[.)])\s+").unwrap();
    for para in text.split("\n\n") {
        let lines: Vec<&str> = para
            .lines()
            .filter(|l| !l.trim().is_empty() && !l.trim_start().starts_with('#'))
            .collect();
        if lines.is_empty() {
            continue;
        }
        let bullets = lines.iter().filter(|l| bullet.is_match(l)).count();
        if bullets >= 2 && bullets * 2 >= lines.len() {
            // a list of separate statements unless it is a numbered procedure (kept whole as one skill candidate)
            let numbered = lines
                .iter()
                .filter(|l| {
                    l.trim_start()
                        .chars()
                        .next()
                        .map(|c| c.is_ascii_digit())
                        .unwrap_or(false)
                })
                .count();
            if numbered >= 2 {
                out.push(lines.join("\n"));
            } else {
                for l in &lines {
                    out.push(bullet.replace(l, "").trim().to_string());
                }
            }
        } else {
            out.push(lines.join("\n").trim().to_string());
        }
    }
    out.into_iter()
        .filter(|s| s.len() >= MIN_UNIT_CHARS)
        .collect()
}

/// Knowledge units of a legacy store, with the store kind used to read it.
pub fn store_units(abs: &Path, rel: &str) -> (&'static str, Vec<String>) {
    let low = rel.to_lowercase();
    if !abs.exists() {
        return ("NOT_FOUND", vec![]);
    }
    let is_sqlite = std::fs::read(abs)
        .map(|b| b.starts_with(b"SQLite format 3"))
        .unwrap_or(false);
    if is_sqlite || low.ends_with(".db") || low.ends_with(".sqlite") || low.ends_with(".sqlite3") {
        return ("sqlite", extract_strings_from_sqlite(abs));
    }
    let Ok(text) = read_text(abs) else {
        return ("binary", vec![]);
    };
    if low.ends_with(".jsonl") || low.ends_with(".json") {
        ("jsonl", extract_strings_from_json(&text))
    } else if low.ends_with(".sql") {
        ("sql_dump", extract_strings_from_sql(&text))
    } else {
        ("text", extract_units_from_text(&text))
    }
}

/// Outcome of extracting one store.
#[derive(Debug, Default, Clone, serde::Serialize)]
pub struct StoreExtraction {
    pub units: usize,
    pub distilled: usize,
    pub registered_for_review: usize,
    pub withheld_secret: usize,
    pub duplicates: usize,
    pub by_kind: std::collections::BTreeMap<String, usize>,
    pub records: Vec<String>,
    pub register: Option<String>,
}

fn title_of(s: &str) -> String {
    s.lines().next().unwrap_or("").chars().take(90).collect()
}

fn base_fields(kind: &str, basis: &str, source: &str, store_kind: &str, ordinal: usize) -> Value {
    json!({"status": "PROVISIONAL", "legacy_source": source,
        "provenance": {"extracted_from": source, "store_kind": store_kind, "unit": ordinal, "extracted_at": crate::util::now_iso(), "method": "gov adopt extract-legacy (A8)",
            "authority_note": "extracted from a legacy store being retired; PROVISIONAL until confirmed (INV-004, framework §69-70)"},
        "extraction": {"kind": kind, "kind_basis": basis}, "tags": ["legacy-extraction", "chat-derived", kind]})
}

fn record_for(
    kind: &str,
    basis: &str,
    text: &str,
    source: &str,
    store_kind: &str,
    ordinal: usize,
) -> Option<Record> {
    let title = title_of(text);
    let body: String = text.chars().take(4000).collect();
    let mut f = base_fields(kind, basis, source, store_kind, ordinal);
    let (rtype, id) = match kind {
        "decision" => {
            f["state_class"] = json!("AUTHORITATIVE");
            f["question"] = json!(title);
            f["chosen_option"] = json!("as-recorded-in-legacy-store");
            f["rationale"] = json!(body);
            f["human_approved"] = json!(false);
            ("decision", identity::extracted_record_id("D", source, text))
        }
        "lesson" => {
            f["state_class"] = json!("EVIDENCE");
            f["scope"] = json!("PROJECT");
            f["lifecycle"] = json!("candidate");
            f["problem_statement"] = json!(title);
            f["body"] = json!(body);
            f["evidence_strength"] = json!("low");
            ("lesson", identity::extracted_record_id("L", source, text))
        }
        "skill" => {
            // a procedure is a skill *candidate*: a governed skill needs validation scenarios (framework §67 lesson →
            // rule/skill proposal), so it enters as a PROJECT lesson carrying the proposed method
            let steps: Vec<Value> = text
                .lines()
                .map(|l| l.trim())
                .filter(|l| !l.is_empty())
                .flat_map(|l| {
                    regex::Regex::new(r"\s*\d+[.)]\s+")
                        .unwrap()
                        .split(l)
                        .map(|x| x.trim().to_string())
                        .filter(|x| !x.is_empty())
                        .collect::<Vec<_>>()
                })
                .map(|x| json!({"step": x}))
                .collect();
            f["state_class"] = json!("EVIDENCE");
            f["scope"] = json!("PROJECT");
            f["lifecycle"] = json!("candidate");
            f["category"] = json!("skill-candidate");
            f["problem_statement"] = json!(title);
            f["body"] = json!(body);
            f["evidence_strength"] = json!("low");
            f["proposed_skill"] = json!({"name": title, "method": steps, "validation_scenarios": [], "status": "DRAFT"});
            ("lesson", identity::extracted_record_id("L", source, text))
        }
        "research" => {
            f["state_class"] = json!("NARRATIVE");
            f["question"] = json!(format!(
                "What does this legacy measurement establish, and does it still hold? ({title})"
            ));
            f["measurements"] = json!({"as_recorded": body});
            f["method"] = json!("not recorded in the legacy store");
            f["body"] = json!(body);
            f["completeness"] = json!({"governed_evidence": false, "missing": ["method", "sources", "uncertainty", "conclusion", "confidence"], "note": "held as reference-only narrative until a governed research record confirms it"});
            (
                "research",
                identity::extracted_record_id("RES", source, text),
            )
        }
        "evidence" => {
            f["state_class"] = json!("NARRATIVE");
            f["summary"] = json!(title);
            f["evidence_claim"] = json!(body);
            f["body"] = json!(body);
            f["completeness"] = json!({"governed_evidence": false, "note": "a claim about evidence recorded in a legacy store; locate and link the evidence itself before relying on it"});
            ("report", identity::extracted_record_id("RPT", source, text))
        }
        _ => return None,
    };
    let mut rec = new_record(rtype, &id, &title, f);
    rec.path = format!(
        "{}/{}.yaml",
        crate::records::record_dir_for(rtype).unwrap_or("spec/reports"),
        id
    );
    Some(rec)
}

/// Extract every knowledge unit of one store: distil it into a record or list it in the store's register.
pub fn extract_store(
    root: &Path,
    source: &str,
    read_from: &str,
    scanner: &crate::security::secrets::SecretScanner,
    seen: &mut HashSet<String>,
) -> Result<(String, StoreExtraction)> {
    let (store_kind, units) = store_units(&root.join(read_from), read_from);
    let mut x = StoreExtraction {
        units: units.len(),
        ..Default::default()
    };
    let mut register: Vec<Value> = vec![];
    for (i, u) in units.iter().enumerate() {
        if !scanner.scan_text(u, source).is_empty() {
            x.withheld_secret += 1;
            continue;
        }
        if !seen.insert(identity::normalise_text(u)) {
            x.duplicates += 1;
            continue;
        }
        let (kind, basis) = classify_unit(u);
        *x.by_kind.entry(kind.to_string()).or_insert(0) += 1;
        match record_for(kind, &basis, u, source, store_kind, i + 1) {
            Some(rec) => {
                save_record(root, &rec)?;
                x.records.push(rec.path.clone());
                x.distilled += 1;
            }
            None => {
                register.push(json!({"id": identity::knowledge_unit_id(source, u), "unit": i + 1, "kind_guess": kind, "kind_basis": basis, "text": u}));
                x.registered_for_review += 1;
            }
        }
    }
    if !register.is_empty() || x.withheld_secret > 0 {
        let id = format!(
            "RPT-LK{}",
            &crate::util::sha256_text(&format!("governance-os/legacy-register\n{source}"))[..10]
        );
        let body = register
            .iter()
            .map(|u| {
                format!(
                    "- [{}] ({}) {}",
                    u["id"].as_str().unwrap_or(""),
                    u["kind_guess"].as_str().unwrap_or(""),
                    u["text"].as_str().unwrap_or("")
                )
            })
            .collect::<Vec<_>>()
            .join("\n");
        let mut f = base_fields(
            "register",
            "units not distilled into a typed record",
            source,
            store_kind,
            0,
        );
        f["state_class"] = json!("NARRATIVE");
        f["summary"] = json!(format!("{} knowledge unit(s) from {source} that were not distilled into a typed record; review each before the archived store is relied on (framework §70 'export any unique durable knowledge')", register.len()));
        f["review_required"] = json!(true);
        f["units"] = json!(register);
        f["withheld_secret_units"] = json!(x.withheld_secret);
        f["body"] = json!(body);
        let mut rec = new_record(
            "report",
            &id,
            &format!("Residual legacy knowledge from {source} (review required)"),
            f,
        );
        rec.path = format!("spec/reports/{id}.yaml");
        save_record(root, &rec)?;
        x.register = Some(rec.path.clone());
    }
    Ok((store_kind.to_string(), x))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn units_are_classified_without_requiring_decision_or_lesson_cues() {
        assert_eq!(
            classify_unit("Decision: cache quotes for 10 minutes").0,
            "decision"
        );
        assert_eq!(
            classify_unit("Lesson learned: pool connections").0,
            "lesson"
        );
        assert_eq!(
            classify_unit("Procedure for releasing: 1) freeze 2) smoke 3) flip").0,
            "skill"
        );
        assert_eq!(
            classify_unit("Research: we benchmarked the gateway; p95 latency was 180 ms").0,
            "research"
        );
        assert_eq!(
            classify_unit("Evidence: the load test report LT-1 shows zero drops").0,
            "evidence"
        );
        assert_eq!(
            classify_unit("The staging host gw-stg-7.internal requires mutual TLS").0,
            "fact"
        );
        assert_eq!(
            classify_unit("What did we decide about retries?").0,
            "question"
        );
    }

    #[test]
    fn sql_dump_literals_are_read() {
        let v = extract_strings_from_sql(
            "INSERT INTO m VALUES (1, 'user', 'it''s a long enough message text', 'x');",
        );
        assert_eq!(v, vec!["it's a long enough message text".to_string()]);
    }

    #[test]
    fn bullet_lists_split_but_numbered_procedures_stay_whole() {
        let u = extract_units_from_text("# Rules\n\n- Never use tabs; use 4 spaces always.\n- Retries: exactly 5 as per requirements.\n\n1. freeze the quote cache now\n2. run the smoke suite on staging\n");
        assert_eq!(u.len(), 3, "{u:?}");
        assert!(u[2].contains("freeze") && u[2].contains("smoke"));
    }
}
