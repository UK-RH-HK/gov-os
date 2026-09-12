//! JSON Schema (draft 2020-12) validation against the installed kernel's schemas.
use crate::util::read_json;
use crate::{GovError, Result};
use serde_json::Value;
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::sync::Mutex;

pub struct SchemaRegistry {
    pub schema_dir: PathBuf,
    cache: Mutex<BTreeMap<String, Value>>,
}

impl SchemaRegistry {
    pub fn new(schema_dir: &Path) -> Self {
        SchemaRegistry { schema_dir: schema_dir.to_path_buf(), cache: Mutex::new(BTreeMap::new()) }
    }
    pub fn has(&self, name: &str) -> bool {
        self.schema_dir.join(format!("{name}.schema.json")).exists()
    }
    pub fn get(&self, name: &str) -> Result<Value> {
        if let Some(v) = self.cache.lock().unwrap().get(name) {
            return Ok(v.clone());
        }
        let p = self.schema_dir.join(format!("{name}.schema.json"));
        if !p.exists() {
            return Err(GovError::new("SCHEMA_NOT_FOUND", format!("schema not found: {name} ({})", p.display())));
        }
        let v = read_json(&p)?;
        self.cache.lock().unwrap().insert(name.to_string(), v.clone());
        Ok(v)
    }
    pub fn errors(&self, name: &str, data: &Value) -> Result<Vec<String>> {
        let schema = self.get(name)?;
        let compiled = jsonschema::JSONSchema::options()
            .with_draft(jsonschema::Draft::Draft202012)
            .compile(&schema)
            .map_err(|e| GovError::new("SCHEMA_COMPILE", format!("{name}: {e}")))?;
        let mut out = vec![];
        if let Err(errs) = compiled.validate(data) {
            for e in errs {
                let loc = e.instance_path.to_string();
                out.push(format!("{}: {}", if loc.is_empty() { "<root>".to_string() } else { loc }, e));
            }
        }
        out.sort();
        Ok(out)
    }
    pub fn validate(&self, name: &str, data: &Value, context: &str) -> Result<()> {
        let errs = self.errors(name, data)?;
        if errs.is_empty() {
            Ok(())
        } else {
            Err(GovError::new("SCHEMA_INVALID", format!("schema validation failed for {name} {context}: {}", errs.iter().take(6).cloned().collect::<Vec<_>>().join("; ")))
                .with_details(serde_json::json!({"errors": errs})))
        }
    }
    pub fn names(&self) -> Vec<String> {
        let mut v: Vec<String> = std::fs::read_dir(&self.schema_dir).map(|rd| rd.filter_map(|e| e.ok()).filter_map(|e| {
            let n = e.file_name().to_string_lossy().to_string();
            n.strip_suffix(".schema.json").map(|s| s.to_string())
        }).collect()).unwrap_or_default();
        v.sort();
        v
    }
}
