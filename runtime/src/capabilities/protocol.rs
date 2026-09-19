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
    /// Governance fields (verifier H-N2): roles allowed to trigger execution, permission classes the plugin needs,
    /// declared content pin, and the raw descriptor (provenance, health_check, permissions).
    pub approved_roles: Vec<String>,
    pub required_permission_classes: Vec<String>,
    pub pin_sha256: Option<String>,
    pub raw: Value,
}

impl PluginDescriptor {
    /// The paths the descriptor declares under `field`, as written: `implementation` (a list), or `model` /
    /// `runtime` (`{artefacts: [...]}`, IP-R2-13). Resolution and binding: `capabilities::binding::declared_paths`.
    pub fn declared_paths(&self, field: &str) -> Vec<String> {
        let v = self.raw.get(field);
        let list = match field {
            "implementation" => v,
            _ => v.and_then(|m| m.get("artefacts")),
        };
        list.and_then(|a| a.as_array())
            .map(|a| {
                a.iter()
                    .filter_map(|s| s.as_str().map(|t| t.to_string()))
                    .collect()
            })
            .unwrap_or_default()
    }

    pub fn from_value(v: &Value, source: &str) -> Option<Self> {
        let plugin_id = v.get("plugin_id")?.as_str()?.to_string();
        let capability = v.get("capability")?.as_str()?.to_string();
        let command: Vec<String> = v
            .get("command")?
            .as_array()?
            .iter()
            .filter_map(|x| x.as_str().map(|s| s.to_string()))
            .collect();
        if command.is_empty() {
            return None;
        }
        let strs = |k: &str| {
            v.get(k)
                .and_then(|x| x.as_array())
                .map(|a| {
                    a.iter()
                        .filter_map(|s| s.as_str().map(|t| t.to_string()))
                        .collect::<Vec<String>>()
                })
                .unwrap_or_default()
        };
        Some(PluginDescriptor {
            plugin_id,
            capability,
            command,
            version: v
                .get("version")
                .and_then(|x| match x {
                    Value::String(s) => Some(s.clone()),
                    Value::Number(n) => Some(n.to_string()),
                    _ => None,
                })
                .unwrap_or_else(|| "0".to_string()),
            languages: strs("languages"),
            cwd: v.get("cwd").and_then(|x| x.as_str()).map(|s| s.to_string()),
            source: source.to_string(),
            approved_roles: strs("approved_roles"),
            required_permission_classes: strs("required_permission_classes"),
            pin_sha256: v
                .get("pin")
                .and_then(|x| x.get("sha256"))
                .and_then(|x| x.as_str())
                .map(|s| s.to_string()),
            raw: v.clone(),
        })
    }
}
