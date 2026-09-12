//! Code-structural memory. Built-in generic extractor (many languages) + optional high-fidelity plugins (API-0001).
pub mod generic;

use crate::capabilities::host::{find, invoke};
use crate::capabilities::protocol::PluginDescriptor;
use serde_json::{json, Value};
use std::path::Path;
use std::time::Duration;

#[derive(Debug, Clone, serde::Serialize, Default)]
pub struct Symbol { pub name: String, pub qualname: String, pub kind: String, pub lineno: usize, pub end_lineno: usize, pub parent: Option<String>, pub signature: String }

#[derive(Debug, Clone, serde::Serialize, Default)]
pub struct CodeFacts { pub language: String, pub provider: String, pub symbols: Vec<Symbol>, pub imports: Vec<String>, pub calls: Vec<(String, String)>, pub units: Vec<(String, usize, usize)>, pub degraded: Option<String> }

pub fn analyze(path: &str, language: &str, source: &str, plugins: &[PluginDescriptor], project_root: &Path) -> CodeFacts {
    if let Some(desc) = find(plugins, "code_intel", Some(language), None) {
        match invoke(&desc, project_root, json!({"path": path, "language": language, "source": source}), Duration::from_secs(20)) {
            Ok(out) => {
                if let Some(f) = from_plugin(language, &out.plugin_id, &out.outputs) { return f; }
                let mut f = generic::analyze(path, language, source);
                f.degraded = Some(format!("plugin {} returned unusable output; used builtin", desc.plugin_id));
                return f;
            }
            Err(e) => {
                let mut f = generic::analyze(path, language, source);
                f.degraded = Some(format!("plugin {} failed ({}); used builtin", desc.plugin_id, e.code));
                return f;
            }
        }
    }
    generic::analyze(path, language, source)
}

fn from_plugin(language: &str, plugin_id: &str, outputs: &Value) -> Option<CodeFacts> {
    let syms = outputs.get("symbols")?.as_array()?;
    let mut symbols = vec![];
    for s in syms {
        symbols.push(Symbol {
            name: s.get("name")?.as_str()?.to_string(), qualname: s.get("qualname").and_then(|v| v.as_str()).unwrap_or("").to_string(),
            kind: s.get("kind").and_then(|v| v.as_str()).unwrap_or("symbol").to_string(), lineno: s.get("lineno").and_then(|v| v.as_u64()).unwrap_or(1) as usize,
            end_lineno: s.get("end_lineno").and_then(|v| v.as_u64()).unwrap_or(1) as usize, parent: s.get("parent").and_then(|v| v.as_str()).map(|x| x.to_string()),
            signature: s.get("signature").and_then(|v| v.as_str()).unwrap_or("").to_string(),
        });
    }
    let imports = outputs.get("imports").and_then(|v| v.as_array()).map(|a| a.iter().filter_map(|x| x.as_str().map(|s| s.to_string())).collect()).unwrap_or_default();
    let calls = outputs.get("calls").and_then(|v| v.as_array()).map(|a| a.iter().filter_map(|c| Some((c.get("from")?.as_str()?.to_string(), c.get("name")?.as_str()?.to_string()))).collect()).unwrap_or_default();
    let units = outputs.get("chunks").and_then(|v| v.as_array()).map(|a| a.iter().filter_map(|c| Some((c.get("qualname")?.as_str()?.to_string(), c.get("lineno")?.as_u64()? as usize, c.get("end_lineno")?.as_u64()? as usize))).collect()).unwrap_or_default();
    Some(CodeFacts { language: language.into(), provider: plugin_id.into(), symbols, imports, calls, units, degraded: None })
}
