//! Governed records: YAML records and Markdown-with-frontmatter records under spec/ (and governance/project/).
use crate::util::{read_text, str_list, str_of, write_text, write_yaml};
use crate::{GovError, Result};
use regex::Regex;
use serde_json::{json, Value};
use std::path::Path;
use std::sync::OnceLock;

pub const RELATION_FIELDS: &[(&str, &str)] = &[
    ("depends_on", "DEPENDS_ON"),
    ("blocks", "BLOCKS"),
    ("implements", "IMPLEMENTS"),
    ("governed_by", "GOVERNED_BY"),
    ("validated_by", "VALIDATED_BY"),
    ("tests", "TESTS"),
    ("derived_from", "DERIVED_FROM"),
    ("affects", "AFFECTS"),
    ("supersedes", "SUPERSEDES"),
    ("requirements", "GOVERNED_BY"),
    ("decisions", "GOVERNED_BY"),
    ("scenarios", "VALIDATED_BY"),
    ("acceptance_tests", "VALIDATED_BY"),
    ("dependencies", "DEPENDS_ON"),
    ("feature", "REALISES"),
    ("task", "PRODUCES"),
    ("consumers", "CONSUMES"),
    ("producers", "PRODUCES"),
    ("required_skills", "USES"),
    ("required_tools", "USES"),
    ("interfaces", "USES"),
    ("lessons", "LEARNED_FROM"),
    ("sources", "DERIVED_FROM"),
    ("cit", "GENERATED_FROM"),
    ("scenario", "TESTS"),
    ("human_gate", "BLOCKS"),
    ("decision", "GOVERNED_BY"),
    ("targets", "AFFECTS"),
    ("blocks_tasks", "BLOCKS"),
];
pub const TYPE_DIR: &[(&str, &str)] = &[
    ("project", "spec/product"),
    ("feature", "spec/features"),
    ("requirement", "spec/requirements"),
    ("decision", "spec/decisions"),
    ("task", "spec/tasks"),
    ("scenario", "spec/scenarios"),
    ("test-obligation", "spec/tasks"),
    ("interface", "spec/interfaces"),
    ("experiment", "spec/experiments"),
    ("lesson", "spec/lessons"),
    ("report", "spec/reports"),
    ("research", "spec/research"),
    ("human-gate", "spec/decisions"),
    ("cit", "spec/decisions"),
    ("checkpoint", "spec/reports/checkpoints"),
    ("handoff", "spec/planning"),
    ("audit", "spec/audits"),
    ("architecture", "spec/architecture"),
    ("workflow", "spec/workflows"),
    ("legacy", "archive/governance"),
    ("data", "spec/data"),
    ("security", "spec/security"),
    ("performance", "spec/performance"),
];
pub const TYPE_PREFIX: &[(&str, &str)] = &[
    ("project", "PRJ"),
    ("feature", "F"),
    ("requirement", "REQ"),
    ("decision", "D"),
    ("task", "TASK"),
    ("scenario", "SCN"),
    ("test-obligation", "TST"),
    ("interface", "API"),
    ("experiment", "EXP"),
    ("lesson", "L"),
    ("report", "RPT"),
    ("research", "RES"),
    ("human-gate", "HDG"),
    ("cit", "CIT"),
    ("checkpoint", "CKPT"),
    ("handoff", "HND"),
    ("audit", "AUD"),
    ("architecture", "ARCH"),
    ("workflow", "WF"),
    ("legacy", "LEG"),
];

pub fn id_regex() -> &'static Regex {
    static RX: OnceLock<Regex> = OnceLock::new();
    RX.get_or_init(|| Regex::new(r"^[A-Z]{1,6}-[A-Za-z0-9._-]+$").unwrap())
}
fn frontmatter_regex() -> &'static Regex {
    static RX: OnceLock<Regex> = OnceLock::new();
    RX.get_or_init(|| Regex::new(r"(?s)\A---\s*\n(.*?)\n---\s*\n?(.*)\z").unwrap())
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum RecordFormat {
    Yaml,
    Md,
}

#[derive(Debug, Clone)]
pub struct Record {
    pub path: String,
    pub data: Value,
    pub body: String,
    pub format: RecordFormat,
    pub problems: Vec<String>,
}

impl Record {
    pub fn id(&self) -> String {
        str_of(&self.data, "id")
    }
    pub fn rtype(&self) -> String {
        str_of(&self.data, "type")
    }
    pub fn status(&self) -> String {
        let s = str_of(&self.data, "status");
        if s.is_empty() {
            "UNKNOWN".into()
        } else {
            s
        }
    }
    pub fn title(&self) -> String {
        for k in ["title", "objective", "name", "question"] {
            let v = str_of(&self.data, k);
            if !v.is_empty() {
                return v;
            }
        }
        if !self.id().is_empty() {
            self.id()
        } else {
            self.path.clone()
        }
    }
    pub fn get(&self, key: &str) -> String {
        str_of(&self.data, key)
    }
    pub fn list(&self, key: &str) -> Vec<String> {
        str_list(&self.data, key)
    }
    pub fn set(&mut self, key: &str, v: Value) {
        if let Some(m) = self.data.as_object_mut() {
            m.insert(key.to_string(), v);
        }
    }

    /// Indexable text: title + salient string fields + body.
    pub fn text(&self) -> String {
        let mut parts = vec![self.title()];
        for k in [
            "summary",
            "objective",
            "question",
            "proposal",
            "rationale",
            "problem_statement",
            "conclusion",
            "statement",
            "mission",
            "product_intent",
            "generic_failure_mode",
            "suggested_change",
            "work_completed",
        ] {
            let v = self.get(k);
            if !v.is_empty() {
                parts.push(v);
            }
        }
        if let Some(b) = self.data.get("body").and_then(|v| v.as_str()) {
            parts.push(b.to_string());
        }
        if !self.body.is_empty() {
            parts.push(self.body.clone());
        }
        for k in [
            "given",
            "when",
            "then",
            "acceptance_criteria",
            "outcomes",
            "options",
            "consequences",
            "discoveries",
            "risks",
        ] {
            if let Some(a) = self.data.get(k).and_then(|v| v.as_array()) {
                for x in a {
                    match x {
                        Value::String(s) => parts.push(s.clone()),
                        Value::Object(o) => parts.push(
                            o.get("description")
                                .and_then(|d| d.as_str())
                                .unwrap_or("")
                                .to_string(),
                        ),
                        _ => {}
                    }
                }
            }
        }
        parts
            .into_iter()
            .filter(|p| !p.is_empty())
            .collect::<Vec<_>>()
            .join("\n")
    }
    /// Long text fields usable as sections for chunking.
    pub fn text_fields(&self) -> Vec<(String, String)> {
        let mut out = vec![];
        if let Some(m) = self.data.as_object() {
            for (k, v) in m {
                if let Value::String(s) = v {
                    if s.len() >= 40 && k != "title" && k != "id" {
                        out.push((k.clone(), s.clone()));
                    }
                }
            }
        }
        out
    }
    pub fn relations(&self) -> Vec<(String, String)> {
        let mut out: Vec<(String, String)> = vec![];
        if let Some(rels) = self.data.get("relations").and_then(|v| v.as_array()) {
            for r in rels {
                if let (Some(t), Some(tg)) = (
                    r.get("type").and_then(|v| v.as_str()),
                    r.get("target").and_then(|v| v.as_str()),
                ) {
                    out.push((t.to_string(), tg.to_string()));
                }
            }
        }
        for (fld, etype) in RELATION_FIELDS {
            match self.data.get(*fld) {
                Some(Value::String(s)) if id_regex().is_match(s) => {
                    out.push((etype.to_string(), s.clone()))
                }
                Some(Value::Array(a)) => {
                    for x in a {
                        match x {
                            Value::String(s) if id_regex().is_match(s) => {
                                out.push((etype.to_string(), s.clone()))
                            }
                            Value::Object(o) => {
                                if let Some(Value::String(s)) = o.get("id") {
                                    if id_regex().is_match(s) {
                                        out.push((etype.to_string(), s.clone()));
                                    }
                                }
                            }
                            _ => {}
                        }
                    }
                }
                _ => {}
            }
        }
        out.sort();
        out.dedup();
        out
    }
}

pub fn parse_record_text(text: &str, path: &str) -> Option<Record> {
    if path.ends_with(".yaml") || path.ends_with(".yml") {
        return match serde_yaml::from_str::<Value>(text) {
            Ok(Value::Object(m)) if m.contains_key("id") && m.contains_key("type") => {
                Some(Record {
                    path: path.into(),
                    data: Value::Object(m),
                    body: String::new(),
                    format: RecordFormat::Yaml,
                    problems: vec![],
                })
            }
            Ok(_) => None,
            Err(e) => Some(Record {
                path: path.into(),
                data: json!({}),
                body: String::new(),
                format: RecordFormat::Yaml,
                problems: vec![format!("yaml error: {e}")],
            }),
        };
    }
    if path.ends_with(".md") {
        let caps = frontmatter_regex().captures(text)?;
        return match serde_yaml::from_str::<Value>(&caps[1]) {
            Ok(Value::Object(m)) if m.contains_key("id") => Some(Record {
                path: path.into(),
                data: Value::Object(m),
                body: caps[2].to_string(),
                format: RecordFormat::Md,
                problems: vec![],
            }),
            Ok(_) => None,
            Err(e) => Some(Record {
                path: path.into(),
                data: json!({}),
                body: String::new(),
                format: RecordFormat::Md,
                problems: vec![format!("frontmatter error: {e}")],
            }),
        };
    }
    None
}

pub fn load_record(root: &Path, relpath: &str) -> Result<Option<Record>> {
    let text = read_text(&root.join(relpath))?;
    Ok(parse_record_text(&text, relpath))
}

pub fn save_record(root: &Path, rec: &Record) -> Result<()> {
    let p = root.join(&rec.path);
    match rec.format {
        RecordFormat::Md => {
            let fm = serde_yaml::to_string(&rec.data)?;
            write_text(&p, &format!("---\n{fm}---\n{}", rec.body))
        }
        RecordFormat::Yaml => write_yaml(&p, &rec.data),
    }
}

pub fn record_dir_for(rtype: &str) -> Result<&'static str> {
    TYPE_DIR
        .iter()
        .find(|(t, _)| *t == rtype)
        .map(|(_, d)| *d)
        .ok_or_else(|| {
            GovError::new(
                "RECORD_TYPE_UNKNOWN",
                format!("no canonical directory for record type {rtype}"),
            )
        })
}
pub fn record_path_for(rtype: &str, id: &str) -> Result<String> {
    Ok(format!("{}/{}.yaml", record_dir_for(rtype)?, id))
}
pub fn prefix_for(rtype: &str) -> &'static str {
    TYPE_PREFIX
        .iter()
        .find(|(t, _)| *t == rtype)
        .map(|(_, p)| *p)
        .unwrap_or("REC")
}

/// Load all records under the given root (spec/, governance/project/, archive/ ...), sorted by path.
pub fn load_all_records(root: &Path, files: &[(std::path::PathBuf, String)]) -> Vec<Record> {
    let mut out = vec![];
    for (abs, rel) in files {
        if !(rel.ends_with(".yaml") || rel.ends_with(".yml") || rel.ends_with(".md")) {
            continue;
        }
        if let Ok(text) = read_text(abs) {
            if let Some(r) = parse_record_text(&text, rel) {
                out.push(r);
            }
        }
    }
    let _ = root;
    out
}

pub fn state_class_for(rec: &Record, authority_policy: &Value) -> String {
    let sc = rec.get("state_class");
    if !sc.is_empty() {
        return sc;
    }
    authority_policy
        .get("default_state_class_by_type")
        .and_then(|m| m.get(rec.rtype()))
        .and_then(|v| v.as_str())
        .unwrap_or("NARRATIVE")
        .to_string()
}

/// In-memory view of all governed records (spec/, governance/project/, archive/), indexed by id.
pub struct RecordStore {
    pub records: Vec<Record>,
    pub by_id: std::collections::BTreeMap<String, usize>,
    pub duplicates: Vec<(String, Vec<String>)>,
    pub problems: Vec<String>,
}

impl RecordStore {
    pub fn load(root: &Path) -> Self {
        let mut records = vec![];
        for sub in ["spec", "governance/project", "archive"] {
            let dir = root.join(sub);
            if !dir.exists() {
                continue;
            }
            let files = crate::paths::iter_repo_files(&dir, false);
            for (abs, rel) in files {
                if !(rel.ends_with(".yaml") || rel.ends_with(".yml") || rel.ends_with(".md")) {
                    continue;
                }
                let relp = format!("{sub}/{rel}");
                if let Ok(text) = read_text(&abs) {
                    if let Some(mut r) = parse_record_text(&text, &relp) {
                        if sub == "archive" {
                            r.problems.push("archived".into());
                        }
                        records.push(r);
                    }
                }
            }
        }
        let mut by_id = std::collections::BTreeMap::new();
        let mut seen: std::collections::BTreeMap<String, Vec<String>> =
            std::collections::BTreeMap::new();
        let mut problems = vec![];
        for (i, r) in records.iter().enumerate() {
            if !r.problems.is_empty() && r.id().is_empty() {
                problems.push(format!("{}: {}", r.path, r.problems.join("; ")));
                continue;
            }
            let id = r.id();
            if id.is_empty() {
                continue;
            }
            seen.entry(id.clone()).or_default().push(r.path.clone());
            // Non-archived records win over archived ones for the same id.
            let archived = r.problems.iter().any(|p| p == "archived");
            match by_id.get(&id) {
                None => {
                    by_id.insert(id, i);
                }
                Some(&j) => {
                    let prev_archived = records[j].problems.iter().any(|p| p == "archived");
                    if prev_archived && !archived {
                        by_id.insert(id, i);
                    }
                }
            }
        }
        let duplicates = seen
            .into_iter()
            .filter(|(_, paths)| paths.len() > 1)
            .collect();
        RecordStore {
            records,
            by_id,
            duplicates,
            problems,
        }
    }
    pub fn get(&self, id: &str) -> Option<&Record> {
        self.by_id.get(id).map(|&i| &self.records[i])
    }
    pub fn get_mut(&mut self, id: &str) -> Option<&mut Record> {
        let i = *self.by_id.get(id)?;
        Some(&mut self.records[i])
    }
    pub fn of_type(&self, t: &str) -> Vec<&Record> {
        self.records
            .iter()
            .filter(|r| r.rtype() == t && !r.problems.iter().any(|p| p == "archived"))
            .collect()
    }
    pub fn ids(&self) -> Vec<String> {
        self.by_id.keys().cloned().collect()
    }
    pub fn next_id(&self, rtype: &str) -> String {
        let prefix = prefix_for(rtype);
        let ids: Vec<String> = self.records.iter().map(|r| r.id()).collect();
        crate::util::next_id(prefix, &ids, 4)
    }
    pub fn active(&self, t: &str) -> Vec<&Record> {
        self.of_type(t)
            .into_iter()
            .filter(|r| r.status() == "ACTIVE" || r.status() == "PROVISIONAL")
            .collect()
    }
}

pub fn new_record(rtype: &str, id: &str, title: &str, fields: Value) -> Record {
    let mut data = json!({"id": id, "type": rtype, "title": title, "status": "ACTIVE", "created": crate::util::today()});
    if let (Some(m), Some(f)) = (data.as_object_mut(), fields.as_object()) {
        for (k, v) in f {
            m.insert(k.clone(), v.clone());
        }
    }
    Record {
        path: record_path_for(rtype, id).unwrap_or(format!("spec/{id}.yaml")),
        data,
        body: String::new(),
        format: RecordFormat::Yaml,
        problems: vec![],
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn parse_yaml_and_markdown_records() {
        let r = parse_record_text("id: D-0001\ntype: decision\ntitle: T\nstatus: ACTIVE\nsupersedes: [D-0000]\nrelations:\n  - {type: AFFECTS, target: F-0001}\nfeature: F-0002\n", "spec/decisions/D-0001.yaml").unwrap();
        assert_eq!(r.id(), "D-0001");
        let rel = r.relations();
        assert!(
            rel.contains(&("SUPERSEDES".into(), "D-0000".into()))
                && rel.contains(&("AFFECTS".into(), "F-0001".into()))
                && rel.contains(&("REALISES".into(), "F-0002".into()))
        );
        let m = parse_record_text(
            "---\nid: L-0001\ntype: lesson\nstatus: ACTIVE\n---\n# Body\ntext",
            "spec/lessons/L-0001.md",
        )
        .unwrap();
        assert_eq!(m.format, RecordFormat::Md);
        assert!(m.body.contains("Body"));
        assert!(parse_record_text("just: yaml\n", "x.yaml").is_none());
        assert_eq!(
            record_path_for("task", "TASK-0001").unwrap(),
            "spec/tasks/TASK-0001.yaml"
        );
    }
}
