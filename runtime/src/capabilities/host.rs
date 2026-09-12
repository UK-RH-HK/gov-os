//! Plugin host: spawns a declared command and exchanges one JSON request/response over pipes (API-0001).
//! stdin is written from its own thread and stdout/stderr are drained concurrently, so responses of any size cannot
//! deadlock on pipe capacity; a watchdog kills the child on timeout and the drain threads finish when the pipes close.
//! The core never links or imports plugins. A failing or missing plugin is an error for the caller to handle.
use super::protocol::{request, PluginDescriptor, PROTOCOL};
use crate::util::{read_yaml, short_uuid};
use crate::{GovError, Result};
use serde_json::Value;
use std::io::{Read, Write};
use std::path::Path;
use std::process::{Command, Stdio};
use std::time::{Duration, Instant};

#[derive(Debug, Clone, serde::Serialize)]
pub struct PluginOutcome { pub plugin_id: String, pub provider: Value, pub outputs: Value, pub stdout_bytes: usize, pub elapsed_ms: u128 }

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
            if let Ok(v) = read_yaml(&p) { if let Some(desc) = PluginDescriptor::from_value(&v, &p.to_string_lossy()) { out.push(desc); } }
        }
    }
    out
}

pub fn find(plugins: &[PluginDescriptor], capability: &str, language: Option<&str>, plugin_id: Option<&str>) -> Option<PluginDescriptor> {
    plugins.iter().find(|p| p.capability == capability && plugin_id.map(|id| p.plugin_id == id).unwrap_or(true) && language.map(|l| p.languages.is_empty() || p.languages.iter().any(|x| x == l)).unwrap_or(true)).cloned()
}

fn resolve_command(desc: &PluginDescriptor, project_root: &Path) -> Vec<String> {
    desc.command.iter().map(|c| c.replace("{project_root}", &project_root.to_string_lossy()).replace("{plugin_dir}", &Path::new(&desc.source).parent().map(|p| p.to_string_lossy().to_string()).unwrap_or_default())).collect()
}

const STDERR_RETAIN: usize = 64 * 1024;

/// Terminate the plugin and every process in its group (pipes held by grandchildren would otherwise keep the
/// drain threads alive after the timeout).
fn kill_tree(child: &mut std::process::Child) {
    #[cfg(unix)]
    unsafe { libc::kill(-(child.id() as i32), libc::SIGKILL); }
    let _ = child.kill();
    let _ = child.wait();
}

pub fn invoke(desc: &PluginDescriptor, project_root: &Path, inputs: Value, timeout: Duration) -> Result<PluginOutcome> {
    let started = Instant::now();
    let cmd = resolve_command(desc, project_root);
    let req = request(&desc.capability, &short_uuid(), inputs);
    let req_bytes = serde_json::to_vec(&req)?;
    let cwd = desc.cwd.as_ref().map(|c| project_root.join(c)).unwrap_or(project_root.to_path_buf());
    let mut command = Command::new(&cmd[0]);
    command.args(&cmd[1..]).current_dir(&cwd).stdin(Stdio::piped()).stdout(Stdio::piped()).stderr(Stdio::piped());
    #[cfg(unix)]
    { use std::os::unix::process::CommandExt; command.process_group(0); } // own process group: a timeout kills grandchildren too
    let mut child = command.spawn().map_err(|e| GovError::new("PLUGIN_SPAWN_FAILED", format!("{}: {e} (command: {})", desc.plugin_id, cmd.join(" "))))?;
    // stdin writer thread: a plugin that starts replying before reading everything must not block the host
    let mut stdin = child.stdin.take().ok_or_else(|| GovError::new("PLUGIN_IO", "no stdin"))?;
    let writer = std::thread::spawn(move || { let r = stdin.write_all(&req_bytes); drop(stdin); r.is_ok() });
    // concurrent drains: the child can never block on a full stdout/stderr pipe
    let mut stdout = child.stdout.take().ok_or_else(|| GovError::new("PLUGIN_IO", "no stdout"))?;
    let out_thread = std::thread::spawn(move || { let mut buf = Vec::new(); let _ = stdout.read_to_end(&mut buf); buf });
    let mut stderr = child.stderr.take().ok_or_else(|| GovError::new("PLUGIN_IO", "no stderr"))?;
    let err_thread = std::thread::spawn(move || {
        let mut retained: Vec<u8> = Vec::new(); let mut chunk = [0u8; 8192]; let mut total = 0usize;
        loop { match stderr.read(&mut chunk) { Ok(0) | Err(_) => break, Ok(n) => { total += n; retained.extend_from_slice(&chunk[..n]); if retained.len() > STDERR_RETAIN { let cut = retained.len() - STDERR_RETAIN; retained.drain(..cut); } } } }
        (retained, total)
    });
    // watchdog: poll for exit; kill on timeout (drains then finish because the pipes close)
    let mut timed_out = false;
    loop {
        match child.try_wait() {
            Ok(Some(_)) => break,
            Ok(None) => { if started.elapsed() > timeout { timed_out = true; kill_tree(&mut child); break; } std::thread::sleep(Duration::from_millis(5)); }
            Err(e) => { let _ = child.kill(); return Err(GovError::new("PLUGIN_IO", e.to_string())); }
        }
    }
    let stdout_bytes = out_thread.join().unwrap_or_default();
    let (stderr_tail, stderr_total) = err_thread.join().unwrap_or_default();
    let stdin_ok = writer.join().unwrap_or(false);
    let stderr_text = String::from_utf8_lossy(&stderr_tail).trim().to_string();
    if timed_out {
        return Err(GovError::new("PLUGIN_TIMEOUT", format!("{} exceeded {:?} and was terminated", desc.plugin_id, timeout)).with_details(serde_json::json!({"stdout_bytes": stdout_bytes.len(), "stderr_bytes": stderr_total, "stderr_tail": stderr_text.chars().rev().take(500).collect::<String>().chars().rev().collect::<String>()})));
    }
    let text = String::from_utf8_lossy(&stdout_bytes);
    let resp: Value = serde_json::from_str(text.trim()).map_err(|e| GovError::new("PLUGIN_BAD_RESPONSE", format!("{}: {e}; stdin_written={stdin_ok}; stdout_bytes={}; stderr_tail={}", desc.plugin_id, stdout_bytes.len(), stderr_text.chars().rev().take(300).collect::<String>().chars().rev().collect::<String>())))?;
    if resp.get("protocol").and_then(|v| v.as_str()) != Some(PROTOCOL) { return Err(GovError::new("PLUGIN_PROTOCOL_MISMATCH", format!("{}: response protocol is not {PROTOCOL}", desc.plugin_id))); }
    if !resp.get("ok").and_then(|v| v.as_bool()).unwrap_or(false) {
        let err = resp.get("error").cloned().unwrap_or(Value::Null);
        return Err(GovError::new("PLUGIN_ERROR", format!("{}: {}", desc.plugin_id, err.get("message").and_then(|m| m.as_str()).unwrap_or("unknown"))).with_details(err));
    }
    Ok(PluginOutcome { plugin_id: desc.plugin_id.clone(), provider: resp.get("provider").cloned().unwrap_or(Value::Null), outputs: resp.get("outputs").cloned().unwrap_or(Value::Null), stdout_bytes: stdout_bytes.len(), elapsed_ms: started.elapsed().as_millis() })
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    fn plugin(dir: &Path, name: &str, script: &str) -> PluginDescriptor {
        let p = dir.join(name); std::fs::write(&p, script).unwrap();
        use std::os::unix::fs::PermissionsExt; std::fs::set_permissions(&p, std::fs::Permissions::from_mode(0o755)).unwrap();
        PluginDescriptor { plugin_id: name.into(), capability: "embed".into(), command: vec![p.to_string_lossy().to_string()], version: "1".into(), languages: vec![], cwd: None, source: String::new() }
    }
    fn tmp() -> std::path::PathBuf { let d = std::env::temp_dir().join(format!("gov-host-{}-{}", std::process::id(), short_uuid())); std::fs::create_dir_all(&d).unwrap(); d }
    #[test]
    fn large_response_well_above_pipe_buffer_does_not_deadlock() {
        let d = tmp();
        // ~1.2 MB JSON response produced without reading stdin first (worst case for a naive host)
        let p = plugin(&d, "big.sh", "#!/usr/bin/env bash\nprintf '{\"protocol\":\"gov-capability/1\",\"ok\":true,\"provider\":{\"id\":\"big\",\"version\":\"1\"},\"outputs\":{\"vectors\":[['\nyes 0.123456 | head -n 150000 | paste -sd, -\nprintf ']],\"dim\":150000}}'\ncat >/dev/null\n");
        let t0 = Instant::now();
        let out = invoke(&p, &d, json!({"texts": ["x"]}), Duration::from_secs(30)).expect("large response must succeed");
        assert!(out.stdout_bytes > 1_000_000, "{}", out.stdout_bytes);
        assert_eq!(out.outputs["vectors"][0].as_array().unwrap().len(), 150000);
        assert!(t0.elapsed() < Duration::from_secs(20));
    }
    #[test]
    fn large_stdin_request_and_stderr_flood_are_drained() {
        let d = tmp();
        let p = plugin(&d, "flood.sh", "#!/usr/bin/env bash\nyes stderr-noise | head -n 60000 1>&2\nREQ=$(cat)\nn=${#REQ}\nprintf '{\"protocol\":\"gov-capability/1\",\"ok\":true,\"provider\":{\"id\":\"flood\",\"version\":\"1\"},\"outputs\":{\"received\":%s}}' \"$n\"\n");
        let big_text = "a".repeat(600_000);
        let out = invoke(&p, &d, json!({"texts": [big_text]}), Duration::from_secs(30)).expect("stderr flood + big stdin must succeed");
        assert!(out.outputs["received"].as_u64().unwrap() > 600_000);
    }
    #[test]
    fn timeout_kills_child_promptly() {
        let d = tmp();
        let p = plugin(&d, "slow.sh", "#!/usr/bin/env bash\nsleep 30\nprintf '{\"protocol\":\"gov-capability/1\",\"ok\":true,\"provider\":{\"id\":\"slow\",\"version\":\"1\"},\"outputs\":{}}'\n");
        let t0 = Instant::now();
        let e = invoke(&p, &d, json!({}), Duration::from_millis(400)).unwrap_err();
        assert_eq!(e.code, "PLUGIN_TIMEOUT");
        assert!(t0.elapsed() < Duration::from_secs(5), "child must be terminated at the timeout, not at its natural end");
    }
    #[test]
    fn bad_json_and_protocol_mismatch_are_reported() {
        let d = tmp();
        let p = plugin(&d, "bad.sh", "#!/usr/bin/env bash\ncat >/dev/null\necho 'not json'\n");
        assert_eq!(invoke(&p, &d, json!({}), Duration::from_secs(5)).unwrap_err().code, "PLUGIN_BAD_RESPONSE");
        let q = plugin(&d, "proto.sh", "#!/usr/bin/env bash\ncat >/dev/null\nprintf '{\"protocol\":\"other/1\",\"ok\":true}'\n");
        assert_eq!(invoke(&q, &d, json!({}), Duration::from_secs(5)).unwrap_err().code, "PLUGIN_PROTOCOL_MISMATCH");
    }
}
