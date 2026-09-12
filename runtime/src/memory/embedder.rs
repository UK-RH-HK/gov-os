//! Embedding and reranking components (framework §14.2–14.3): the pinned implementation is a policy decision,
//! recorded in the index manifest and runtime meta, and used identically at index time and query time.
//! There is NO silent fallback: a declared implementation that is unavailable is an error.
use crate::capabilities::host::{discover, find, invoke};
use crate::capabilities::protocol::PluginDescriptor;
use crate::memory::db::RuntimeDb;
use crate::memory::embeddings::HashedNgramEmbedder;
use crate::{GovError, Project, Result};
use serde_json::{json, Value};
use std::path::Path;
use std::time::Duration;

pub const BUILTIN_ID: &str = "hashed-ngram";

#[derive(Debug, Clone, PartialEq, Eq, serde::Serialize)]
pub struct EmbedSpec { pub id: String, pub version: String, pub dimensions: usize, pub source: String }

impl EmbedSpec {
    pub fn from_policy(p: &Project) -> EmbedSpec {
        let pol = p.policies();
        let id = pol.get_str("MEMORY_POLICY", "embedding.provider", BUILTIN_ID);
        let version = pol.get_str("MEMORY_POLICY", "embedding.version", "1");
        let dimensions = pol.get_i64("MEMORY_POLICY", "embedding.dimensions", 512).max(8) as usize;
        let source = if id == BUILTIN_ID { "builtin" } else { "plugin" };
        EmbedSpec { id, version, dimensions, source: source.into() }
    }
    pub fn from_value(v: &Value) -> Option<EmbedSpec> {
        Some(EmbedSpec { id: v.get("id")?.as_str()?.to_string(), version: v.get("version").and_then(|x| x.as_str()).unwrap_or("1").to_string(),
            dimensions: v.get("dimensions").and_then(|x| x.as_u64()).unwrap_or(0) as usize, source: v.get("source").and_then(|x| x.as_str()).unwrap_or("builtin").to_string() })
    }
    pub fn to_value(&self) -> Value { json!({"id": self.id, "version": self.version, "dimensions": self.dimensions, "source": self.source}) }
    pub fn describe(&self) -> String { format!("{}@{} ({}-d, {})", self.id, self.version, self.dimensions, self.source) }
}

#[derive(Debug, Clone, PartialEq, Eq, serde::Serialize)]
pub struct RerankSpec { pub provider: String, pub version: String, pub candidates: usize }
impl RerankSpec {
    pub fn from_policy(p: &Project) -> RerankSpec {
        let pol = p.policies();
        RerankSpec { provider: pol.get_str("MEMORY_POLICY", "reranker.provider", "none"), version: pol.get_str("MEMORY_POLICY", "reranker.version", "0"), candidates: pol.get_i64("MEMORY_POLICY", "retrieval.rerank_candidates", 24).max(1) as usize }
    }
    pub fn enabled(&self) -> bool { self.provider != "none" && !self.provider.is_empty() }
    pub fn to_value(&self) -> Value { json!({"provider": self.provider, "version": self.version}) }
}

pub enum Embedder { Builtin(HashedNgramEmbedder), Plugin { desc: PluginDescriptor, spec: EmbedSpec } }

impl Embedder {
    /// Resolve the implementation for a spec. A declared plugin that cannot be found is an error (never a fallback).
    pub fn resolve(spec: &EmbedSpec, plugins: &[PluginDescriptor]) -> Result<Embedder> {
        if spec.source == "builtin" || spec.id == BUILTIN_ID {
            if spec.id != BUILTIN_ID { return Err(GovError::new("EMBEDDER_UNAVAILABLE", format!("builtin embedder '{}' unknown; only '{BUILTIN_ID}' is built in", spec.id))); }
            return Ok(Embedder::Builtin(HashedNgramEmbedder::new(spec.dimensions, &spec.version)));
        }
        match find(plugins, "embed", None, Some(&spec.id)) {
            Some(desc) => Ok(Embedder::Plugin { desc, spec: spec.clone() }),
            None => Err(GovError::new("EMBEDDER_UNAVAILABLE", format!("embedding implementation '{}' is pinned by MEMORY_POLICY.embedding but no `embed` plugin with that id is declared under governance/project/plugins/ (no silent fallback to the built-in embedder)", spec.id))
                .with_details(json!({"pinned": spec.to_value(), "declared_plugins": plugins.iter().map(|p| json!({"plugin_id": p.plugin_id, "capability": p.capability})).collect::<Vec<_>>()}))),
        }
    }
    pub fn spec(&self) -> EmbedSpec {
        match self { Embedder::Builtin(e) => EmbedSpec { id: BUILTIN_ID.into(), version: e.version.clone(), dimensions: e.dim, source: "builtin".into() }, Embedder::Plugin { spec, .. } => spec.clone() }
    }
    pub fn embed_batch(&self, texts: &[String], root: &Path) -> Result<Vec<Vec<f64>>> {
        match self {
            Embedder::Builtin(e) => Ok(texts.iter().map(|t| e.embed(t)).collect()),
            Embedder::Plugin { desc, spec } => {
                let out = invoke(desc, root, json!({"texts": texts, "dimensions": spec.dimensions}), Duration::from_secs(300))?;
                let vecs = out.outputs.get("vectors").and_then(|v| v.as_array()).ok_or_else(|| GovError::new("EMBEDDER_BAD_OUTPUT", format!("plugin {} returned no vectors", desc.plugin_id)))?;
                if vecs.len() != texts.len() { return Err(GovError::new("EMBEDDER_BAD_OUTPUT", format!("plugin {} returned {} vectors for {} texts", desc.plugin_id, vecs.len(), texts.len()))); }
                let mut out_v = Vec::with_capacity(vecs.len());
                for v in vecs {
                    let vec: Vec<f64> = v.as_array().map(|a| a.iter().filter_map(|x| x.as_f64()).collect()).unwrap_or_default();
                    if vec.len() != spec.dimensions { return Err(GovError::new("EMBEDDER_BAD_OUTPUT", format!("plugin {} returned a {}-d vector; pinned dimensionality is {}", desc.plugin_id, vec.len(), spec.dimensions))); }
                    out_v.push(vec);
                }
                Ok(out_v)
            }
        }
    }
    pub fn embed_one(&self, text: &str, root: &Path) -> Result<Vec<f64>> { Ok(self.embed_batch(&[text.to_string()], root)?.remove(0)) }
}

/// The embedder recorded for the live index (runtime meta), if any.
pub fn live_spec(db: &RuntimeDb) -> Option<EmbedSpec> { db.get_meta("embedder").and_then(|v| EmbedSpec::from_value(&v)) }

/// Query-time embedder: MUST be the implementation the live index was built with, and it must equal the policy pin.
pub fn for_query(p: &Project, db: &RuntimeDb) -> Result<Embedder> {
    let pinned = EmbedSpec::from_policy(p);
    let live = live_spec(db).ok_or_else(|| GovError::new("INDEX_MISSING", "no semantic index metadata; run gov rebuild-memory"))?;
    if live != pinned {
        return Err(GovError::new("EMBEDDER_MISMATCH", format!("the live index was built with {} but MEMORY_POLICY pins {}; run `gov rebuild-memory` (full) before querying", live.describe(), pinned.describe()))
            .with_details(json!({"live": live.to_value(), "pinned": pinned.to_value(), "remediation": "gov rebuild-memory"})));
    }
    let plugins = discover(&p.root);
    Embedder::resolve(&live, &plugins)
}

pub struct Reranker { pub desc: PluginDescriptor, pub spec: RerankSpec }
impl Reranker {
    /// None when no reranker is pinned; an error when one is pinned but unavailable.
    pub fn resolve(p: &Project, plugins: &[PluginDescriptor]) -> Result<Option<Reranker>> {
        let spec = RerankSpec::from_policy(p);
        if !spec.enabled() { return Ok(None); }
        match find(plugins, "rerank", None, Some(&spec.provider)) {
            Some(desc) => Ok(Some(Reranker { desc, spec })),
            None => Err(GovError::new("RERANKER_UNAVAILABLE", format!("MEMORY_POLICY.reranker.provider pins '{}' but no `rerank` plugin with that id is declared (no silent fallback)", spec.provider))),
        }
    }
    /// Returns (id, score) pairs; candidates without a score keep their fusion order after the scored ones.
    pub fn rerank(&self, query: &str, candidates: &[(String, String)], root: &Path) -> Result<Vec<(String, f64)>> {
        let out = invoke(&self.desc, root, json!({"query": query, "candidates": candidates.iter().map(|(id, text)| json!({"id": id, "text": text})).collect::<Vec<_>>()}), Duration::from_secs(120))?;
        Ok(out.outputs.get("scores").and_then(|s| s.as_array()).map(|a| a.iter().filter_map(|x| Some((x.get("id")?.as_str()?.to_string(), x.get("score")?.as_f64()?))).collect()).unwrap_or_default())
    }
}
