//! Code-structural memory (framework §11.5, Contract v3 C5). Language adapters are resolved through the capability
//! registry (API-0001: a `code_intel` plugin declared for the file's language); the built-in extractor
//! ([`generic`]) is the fallback for languages without an adapter and for an adapter that fails (recorded as a
//! degradation and in failure memory, never silent). No language runtime is hard-coded in the core (D-0002).
//!
//! Facts per file: symbols/definitions with spans, imports, calls, **inheritance/implementation relations**,
//! **route registrations** and **database models**. An adapter that predates relations/routes/models (its output
//! has none of those keys) is completed from the built-in extractor for those facts only, and the provider string
//! says so.
pub mod generic;

use crate::capabilities::host::{find, invoke};
use crate::capabilities::protocol::PluginDescriptor;
use serde_json::{json, Value};
use std::path::Path;
use std::time::Duration;

#[derive(Debug, Clone, serde::Serialize, Default)]
pub struct Symbol {
    pub name: String,
    pub qualname: String,
    pub kind: String,
    pub lineno: usize,
    pub end_lineno: usize,
    pub parent: Option<String>,
    pub signature: String,
}

/// A supertype relation: `from` (a type's qualified name in this file) `inherits` from or `implements` `name`
/// (the supertype's simple name, resolved to a defining artefact by the index).
#[derive(Debug, Clone, serde::Serialize, Default, PartialEq, Eq)]
pub struct Relation {
    pub kind: String,
    pub from: String,
    pub name: String,
    pub lineno: usize,
}

/// An HTTP route registration: method (`GET`, `GET|POST`, `ANY`), path as registered, and the handler's name when
/// the registration names or decorates one.
#[derive(Debug, Clone, serde::Serialize, Default, PartialEq, Eq)]
pub struct Route {
    pub method: String,
    pub path: String,
    pub handler: Option<String>,
    pub lineno: usize,
}

/// A database model (ORM entity): the type (or registered model name), its table when declared, and the evidence
/// the extractor read (a table declaration, column definitions, an entity annotation or an ORM base).
#[derive(Debug, Clone, serde::Serialize, Default, PartialEq, Eq)]
pub struct Model {
    pub name: String,
    pub qualname: String,
    pub table: Option<String>,
    pub lineno: usize,
    pub evidence: String,
}

#[derive(Debug, Clone, serde::Serialize, Default)]
pub struct CodeFacts {
    pub language: String,
    pub provider: String,
    pub symbols: Vec<Symbol>,
    pub imports: Vec<String>,
    pub calls: Vec<(String, String)>,
    pub units: Vec<(String, usize, usize)>,
    pub relations: Vec<Relation>,
    pub routes: Vec<Route>,
    pub models: Vec<Model>,
    pub degraded: Option<String>,
}

/// The adapter that will analyse files of `language` for this plugin set: the registered `code_intel` plugin for
/// the language (identity `plugin_id@version#pin`) or the built-in extractor. Part of each code artefact's
/// derivation key, so registering, replacing or removing an adapter re-derives the files it covers.
pub fn provider_identity(language: &str, plugins: &[PluginDescriptor]) -> String {
    match find(plugins, "code_intel", Some(language), None) {
        Some(d) => format!(
            "{}@{}#{}",
            d.plugin_id,
            d.version,
            d.pin_sha256.clone().unwrap_or_default()
        ),
        None => generic::EXTRACTOR_VERSION.to_string(),
    }
}

pub fn analyze(
    path: &str,
    language: &str,
    source: &str,
    plugins: &[PluginDescriptor],
    project_root: &Path,
) -> CodeFacts {
    if let Some(desc) = find(plugins, "code_intel", Some(language), None) {
        match invoke(
            &desc,
            project_root,
            json!({"path": path, "language": language, "source": source}),
            Duration::from_secs(20),
        ) {
            Ok(out) => {
                if let Some(mut f) = from_plugin(language, &out.plugin_id, &out.outputs) {
                    let has = |k: &str| out.outputs.get(k).map(|v| v.is_array()).unwrap_or(false);
                    if !(has("relations") && has("routes") && has("models")) {
                        let g = generic::analyze(path, language, source);
                        if !has("relations") {
                            f.relations = g.relations;
                        }
                        if !has("routes") {
                            f.routes = g.routes;
                        }
                        if !has("models") {
                            f.models = g.models;
                        }
                        f.provider = format!("{}+{}", f.provider, generic::EXTRACTOR_VERSION);
                    }
                    return f;
                }
                let mut f = generic::analyze(path, language, source);
                f.degraded = Some(format!(
                    "plugin {} returned unusable output; used builtin",
                    desc.plugin_id
                ));
                return f;
            }
            Err(e) => {
                let mut f = generic::analyze(path, language, source);
                f.degraded = Some(format!(
                    "plugin {} failed ({}); used builtin",
                    desc.plugin_id, e.code
                ));
                return f;
            }
        }
    }
    generic::analyze(path, language, source)
}

fn str_field(v: &Value, k: &str) -> String {
    v.get(k).and_then(|x| x.as_str()).unwrap_or("").to_string()
}

fn from_plugin(language: &str, plugin_id: &str, outputs: &Value) -> Option<CodeFacts> {
    let syms = outputs.get("symbols")?.as_array()?;
    let mut symbols = vec![];
    for s in syms {
        symbols.push(Symbol {
            name: s.get("name")?.as_str()?.to_string(),
            qualname: str_field(s, "qualname"),
            kind: s
                .get("kind")
                .and_then(|v| v.as_str())
                .unwrap_or("symbol")
                .to_string(),
            lineno: s.get("lineno").and_then(|v| v.as_u64()).unwrap_or(1) as usize,
            end_lineno: s.get("end_lineno").and_then(|v| v.as_u64()).unwrap_or(1) as usize,
            parent: s
                .get("parent")
                .and_then(|v| v.as_str())
                .map(|x| x.to_string()),
            signature: str_field(s, "signature"),
        });
    }
    let imports = outputs
        .get("imports")
        .and_then(|v| v.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default();
    let calls = outputs
        .get("calls")
        .and_then(|v| v.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|c| {
                    Some((
                        c.get("from")?.as_str()?.to_string(),
                        c.get("name")?.as_str()?.to_string(),
                    ))
                })
                .collect()
        })
        .unwrap_or_default();
    let units = outputs
        .get("chunks")
        .and_then(|v| v.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|c| {
                    Some((
                        c.get("qualname")?.as_str()?.to_string(),
                        c.get("lineno")?.as_u64()? as usize,
                        c.get("end_lineno")?.as_u64()? as usize,
                    ))
                })
                .collect()
        })
        .unwrap_or_default();
    let arr = |k: &str| {
        outputs
            .get(k)
            .and_then(|v| v.as_array())
            .cloned()
            .unwrap_or_default()
    };
    let relations = arr("relations")
        .iter()
        .filter_map(|r| {
            let kind = str_field(r, "kind");
            let name = str_field(r, "name");
            if !(kind == "inherits" || kind == "implements") || name.is_empty() {
                return None;
            }
            Some(Relation {
                kind,
                from: str_field(r, "from"),
                name,
                lineno: r.get("lineno").and_then(|v| v.as_u64()).unwrap_or(0) as usize,
            })
        })
        .collect();
    let routes = arr("routes")
        .iter()
        .filter_map(|r| {
            let path = str_field(r, "path");
            if path.is_empty() {
                return None;
            }
            let m = str_field(r, "method");
            Some(Route {
                method: if m.is_empty() { "ANY".into() } else { m },
                path,
                handler: r
                    .get("handler")
                    .and_then(|v| v.as_str())
                    .map(|s| s.to_string()),
                lineno: r.get("lineno").and_then(|v| v.as_u64()).unwrap_or(0) as usize,
            })
        })
        .collect();
    let models = arr("models")
        .iter()
        .filter_map(|m| {
            let name = str_field(m, "name");
            if name.is_empty() {
                return None;
            }
            Some(Model {
                qualname: {
                    let q = str_field(m, "qualname");
                    if q.is_empty() {
                        name.clone()
                    } else {
                        q
                    }
                },
                name,
                table: m
                    .get("table")
                    .and_then(|v| v.as_str())
                    .map(|s| s.to_string()),
                lineno: m.get("lineno").and_then(|v| v.as_u64()).unwrap_or(0) as usize,
                evidence: str_field(m, "evidence"),
            })
        })
        .collect();
    Some(CodeFacts {
        language: language.into(),
        provider: plugin_id.into(),
        symbols,
        imports,
        calls,
        units,
        relations,
        routes,
        models,
        degraded: None,
    })
}
