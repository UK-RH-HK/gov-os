//! Plugin host: spawns a declared command, exchanges one JSON request/response. Never links or imports plugins.
//! A failing plugin is reported as a degradation; callers fall back to built-in capabilities.
use super::protocol::{request, PluginDescriptor, PROTOCOL};
use crate::util::{read_yaml, short_uuid};
use crate::{GovError, Result};
use serde_json::Value;
use std::io::Write;
use std::path::Path;
use std::process::{Command, Stdio};
use std::time::Duration;

#[derive(Debug, Clone, serde::Serialize)]
pub struct PluginOutcome {
    pub plugin_id: String,
    pub provider: Value,
    pub outputs: Value,
}

/// Discover plugin descriptors: governance/project/plugins/*.yaml (project overlay) and $GOV_PLUGINS_DIR/*.yaml.
pub fn discover(project_root: &Path) -> Vec<PluginDescriptor> {
    if std::env::var("GOV_DISABLE_PLUGINS").map(|v| v == "1").unwrap_or(false) { return vec![]; }
    let mut dirs = vec![project_root.join("governance").join("project").join("plugins")];
    if let Ok(d) = std::env::var("GOV_PLUGINS_DIR") { dirs.push(std::path::PathBuf::from(d)); }
    let mut out = vec![];
    for d in dirs {
        let Ok(rd) = std::fs::read_dir(&d) else { continue };
        let mut entries: Vec<_> = rd.filter_map(|e| e.ok()).map(|e| e.path()).filter(|p| p.extension().map(|x| x == "yaml" || x == "yml").unwrap_or(false)).collect();
        entries.sort();
        for p in entries {
            if let Ok(v) = read_yaml(&p) {
                if let Some(desc) = PluginDescriptor::from_value(&v, &p.to_string_lossy()) { out.push(desc); }
            }
        }
    }
    out
}

pub fn find(plugins: &[PluginDescriptor], capability: &str, language: Option<&str>, plugin_id: Option<&str>) -> Option<PluginDescriptor> {
    plugins.iter().find(|p| {
        p.capability == capability
            && plugin_id.map(|id| p.plugin_id == id).unwrap_or(true)
            && language.map(|l| p.languages.is_empty() || p.languages.iter().any(|x| x == l)).unwrap_or(true)
    }).cloned()
}

fn resolve_command(desc: &PluginDescriptor, project_root: &Path) -> Vec<String> {
    desc.command.iter().map(|c| c.replace("{project_root}", &project_root.to_string_lossy()).replace("{plugin_dir}", &Path::new(&desc.source).parent().map(|p| p.to_string_lossy().to_string()).unwrap_or_default())).collect()
}

pub fn invoke(desc: &PluginDescriptor, project_root: &Path, inputs: Value, timeout: Duration) -> Result<PluginOutcome> {
    let cmd = resolve_command(desc, project_root);
    let req = request(&desc.capability, &short_uuid(), inputs);
    let cwd = desc.cwd.as_ref().map(|c| project_root.join(c)).unwrap_or(project_root.to_path_buf());
    let mut child = Command::new(&cmd[0]).args(&cmd[1..]).current_dir(&cwd).stdin(Stdio::piped()).stdout(Stdio::piped()).stderr(Stdio::piped()).spawn()
        .map_err(|e| GovError::new("PLUGIN_SPAWN_FAILED", format!("{}: {e}", desc.plugin_id)))?;
    {
        let mut stdin = child.stdin.take().ok_or_else(|| GovError::new("PLUGIN_IO", "no stdin"))?;
        stdin.write_all(serde_json::to_string(&req)?.as_bytes())?;
    }
    let started = std::time::Instant::now();
    loop {
        match child.try_wait() {
            Ok(Some(_)) => break,
            Ok(None) => {
                if started.elapsed() > timeout {
                    let _ = child.kill();
                    return Err(GovError::new("PLUGIN_TIMEOUT", format!("{} exceeded {:?}", desc.plugin_id, timeout)));
                }
                std::thread::sleep(Duration::from_millis(10));
            }
            Err(e) => return Err(GovError::new("PLUGIN_IO", e.to_string())),
        }
    }
    let out = child.wait_with_output()?;
    let text = String::from_utf8_lossy(&out.stdout);
    let resp: Value = serde_json::from_str(text.trim()).map_err(|e| GovError::new("PLUGIN_BAD_RESPONSE", format!("{}: {e}; stderr={}", desc.plugin_id, String::from_utf8_lossy(&out.stderr).trim())))?;
    if resp.get("protocol").and_then(|v| v.as_str()) != Some(PROTOCOL) {
        return Err(GovError::new("PLUGIN_PROTOCOL_MISMATCH", format!("{}: response protocol is not {PROTOCOL}", desc.plugin_id)));
    }
    if !resp.get("ok").and_then(|v| v.as_bool()).unwrap_or(false) {
        let err = resp.get("error").cloned().unwrap_or(Value::Null);
        return Err(GovError::new("PLUGIN_ERROR", format!("{}: {}", desc.plugin_id, err.get("message").and_then(|m| m.as_str()).unwrap_or("unknown"))).with_details(err));
    }
    Ok(PluginOutcome { plugin_id: desc.plugin_id.clone(), provider: resp.get("provider").cloned().unwrap_or(Value::Null), outputs: resp.get("outputs").cloned().unwrap_or(Value::Null) })
}
