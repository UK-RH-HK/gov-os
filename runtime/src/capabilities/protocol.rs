//! gov-capability/1 request/response shapes (spec/interfaces/API-0001.yaml).
use serde_json::{json, Value};

pub const PROTOCOL: &str = "gov-capability/1";

pub fn request(capability: &str, request_id: &str, inputs: Value) -> Value {
    json!({"protocol": PROTOCOL, "capability": capability, "request_id": request_id, "inputs": inputs})
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct PluginDescriptor {
    pub plugin_id: String,
    pub capability: String,
    pub command: Vec<String>,
    pub version: String,
    pub languages: Vec<String>,
    pub cwd: Option<String>,
    pub source: String,
}

impl PluginDescriptor {
    pub fn from_value(v: &Value, source: &str) -> Option<Self> {
        let plugin_id = v.get("plugin_id")?.as_str()?.to_string();
        let capability = v.get("capability")?.as_str()?.to_string();
        let command: Vec<String> = v.get("command")?.as_array()?.iter().filter_map(|x| x.as_str().map(|s| s.to_string())).collect();
        if command.is_empty() { return None; }
        Some(PluginDescriptor {
            plugin_id, capability, command,
            version: v.get("version").and_then(|x| x.as_str()).unwrap_or("0").to_string(),
            languages: v.get("languages").and_then(|x| x.as_array()).map(|a| a.iter().filter_map(|s| s.as_str().map(|t| t.to_string())).collect()).unwrap_or_default(),
            cwd: v.get("cwd").and_then(|x| x.as_str()).map(|s| s.to_string()),
            source: source.to_string(),
        })
    }
}
