//! Skill registry: kernel skills (framework/skills) + project skills (governance/project/skills).
//!
//! **Skill regression (Contract v3:399-402, :774; framework §27; BC-P2-42).**
//!
//! * *A version identifies its content.* A skill's content digest is the SHA-256 of its canonical JSON form. The
//!   first content seen for `id@version` is bound — in the tracked, OS-written `governance/registry/skill-bindings.json`
//!   (`gov health skills --record`) and, on every machine that evaluates the skill, in the machine-local observation
//!   ledger. Different content under an already-bound or already-observed version is reported: the method changed
//!   without a version change.
//! * *Validation scenarios are executed.* A scenario is executable when it carries a `check` (project skills inline;
//!   kernel skills through the kernel's `health/SKILL_SCENARIO_CHECKS.yaml`, bound to the scenario's exact statement).
//!   A check is a list of steps — `gov` invocations with expectations, file writes, YAML edits — run by the `gov`
//!   binary itself against a **disposable copy of the project** (never the live repository). A failed expectation
//!   is a finding; a scenario with no executable check and no declared execution mode cannot pass and is reported.
//!   Scenarios that need an agent (or the G6 qualification harness) must say so (`execution: agent|qualification`
//!   with a reason) and are listed as not executed.
use crate::util::{hash_value, now_iso, read_json, read_yaml, write_json};
use crate::{GovError, Project, Result};
use serde_json::{json, Map, Value};
use std::path::{Path, PathBuf};
use std::time::{Duration, Instant};

pub fn list_skills(p: &Project) -> Vec<Value> {
    let mut out = vec![];
    for (dir, source) in [
        (p.kernel_dir().join("skills"), "kernel"),
        (p.overlay_dir().join("skills"), "project"),
    ] {
        let Ok(rd) = std::fs::read_dir(&dir) else {
            continue;
        };
        let mut paths: Vec<_> = rd
            .filter_map(|e| e.ok())
            .map(|e| e.path())
            .filter(|x| x.extension().map(|e| e == "yaml").unwrap_or(false))
            .collect();
        paths.sort();
        for path in paths {
            if let Ok(mut v) = read_yaml(&path) {
                let digest = content_sha256(&v);
                v["_source"] = json!(source);
                v["_path"] = json!(path
                    .strip_prefix(&p.root)
                    .unwrap_or(&path)
                    .to_string_lossy());
                v["_content_sha256"] = json!(digest);
                out.push(v);
            }
        }
    }
    out
}

pub fn find_skill(p: &Project, id: &str) -> Option<Value> {
    list_skills(p)
        .into_iter()
        .find(|s| s["id"].as_str() == Some(id))
}

/// Canonical content digest of a skill (annotations added by this module are excluded).
pub fn content_sha256(skill: &Value) -> String {
    let mut v = skill.clone();
    if let Some(o) = v.as_object_mut() {
        o.retain(|k, _| !k.starts_with('_'));
    }
    hash_value(&v)
}

fn version_id(s: &Value) -> String {
    format!(
        "{}@{}",
        s["id"].as_str().unwrap_or("?"),
        s["version"].as_str().unwrap_or("?")
    )
}

/// Resolve skills for a task: by required_skills, else by task class + role. Every resolved skill carries its
/// content digest, so an execution record captures the exact skill version used (framework §27).
pub fn resolve(p: &Project, task: &Value) -> Result<Value> {
    let skills = list_skills(p);
    let required: Vec<String> = task
        .get("required_skills")
        .and_then(|v| v.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default();
    let class = task
        .get("class")
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .to_string();
    let role = task
        .get("role")
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .to_string();
    let mut resolved = vec![];
    let mut missing = vec![];
    for r in &required {
        match skills
            .iter()
            .find(|s| s["id"].as_str() == Some(r) && s["status"].as_str() == Some("ACTIVE"))
        {
            Some(s) => resolved.push(json!({"id": s["id"], "version": s["version"], "source": s["_source"], "content_sha256": s["_content_sha256"]})),
            None => missing.push(r.clone()),
        }
    }
    let candidates: Vec<Value> = skills
        .iter()
        .filter(|s| {
            s["status"].as_str() == Some("ACTIVE")
                && s["task_classes"]
                    .as_array()
                    .map(|a| a.iter().any(|c| c.as_str() == Some(&class)))
                    .unwrap_or(false)
                && (role.is_empty()
                    || s["roles"]
                        .as_array()
                        .map(|a| {
                            a.iter()
                                .any(|c| c.as_str() == Some(&role) || c.as_str() == Some("all"))
                        })
                        .unwrap_or(false))
        })
        .map(|s| json!({"id": s["id"], "version": s["version"], "source": s["_source"], "content_sha256": s["_content_sha256"]}))
        .collect();
    Ok(
        json!({"task": task["id"], "resolved": resolved, "missing": missing, "candidates_by_class_role": candidates, "capability_gap": !missing.is_empty()}),
    )
}

/// Static problems (schema, missing scenarios). Kept for callers that only need the structural view.
pub fn validate_all(p: &Project) -> Vec<String> {
    let mut problems = vec![];
    for s in list_skills(p) {
        let id = s["id"].as_str().unwrap_or("?").to_string();
        let mut plain = s.clone();
        if let Some(o) = plain.as_object_mut() {
            o.retain(|k, _| !k.starts_with('_'));
        }
        if let Ok(errs) = p.schemas().errors("skill", &plain) {
            for e in errs.iter().take(3) {
                problems.push(format!("{id}: {e}"));
            }
        }
        if s["validation_scenarios"]
            .as_array()
            .map(|a| a.is_empty())
            .unwrap_or(true)
        {
            problems.push(format!("{id}: no validation scenarios"));
        }
    }
    problems
}

// ------------------------------------------------------------------------------------------ version binding

/// Where the tracked, OS-written skill content bindings belong (BC-P2-31; WS-6 IP-R3-WS06-7): the kernel's store
/// declaration `paths::OS_STORES` `skill-bindings`, beside the plugin registry and outside the regenerable views.
pub const BINDINGS_REL: &str = crate::paths::SKILL_BINDINGS_PATH;
/// Where writers before round 4 kept them (inside `governance/generated/`, which the product regenerates).
pub const LEGACY_BINDINGS_REL: &str = "governance/generated/skill-bindings.json";

/// Where bindings are written: the store location (`paths::store_path`).
pub fn bindings_path(p: &Project) -> PathBuf {
    crate::paths::store_path(&p.root, "skill-bindings").unwrap_or_else(|| p.root.join(BINDINGS_REL))
}

/// Where bindings are read from: the store location, or — only while nothing is there — the legacy location an
/// earlier release wrote. Reading never moves anything (read-only commands stay read-only); the next binding write
/// moves the legacy file ([`relocate_bindings`]).
pub fn bindings_read_path(p: &Project) -> PathBuf {
    let at = bindings_path(p);
    let legacy = p.root.join(LEGACY_BINDINGS_REL);
    if !at.exists() && legacy.exists() {
        legacy
    } else {
        at
    }
}

/// Move bindings kept at the legacy location to where they belong, bytes unchanged (`paths::relocate_legacy`). When
/// the location already holds bindings and the legacy file differs, the location is authoritative and the legacy file
/// is left in place (never read again, never overwritten or deleted by the OS; `paths::misplaced_os_state` reports
/// it). Called before every binding write and by the upgrade path. Idempotent.
pub fn relocate_bindings(p: &Project) -> Result<Vec<Value>> {
    match crate::paths::relocate_legacy(&p.root, "skill-bindings") {
        Ok(v) => Ok(v),
        Err(e) if e.code == "STATE_LOCATION_CONFLICT" => Ok(vec![json!({
            "store": "skill-bindings", "from": LEGACY_BINDINGS_REL, "to": BINDINGS_REL, "action": "left in place",
            "reason": "bindings already exist where they belong and the legacy file differs; the location is authoritative and the legacy file is never read"})]),
        Err(e) => Err(e),
    }
}
pub fn observations_path(p: &Project) -> PathBuf {
    p.runtime_dir().join("health").join("skills-observed.json")
}

fn load_obj(path: &Path) -> Map<String, Value> {
    read_json(path)
        .ok()
        .and_then(|v| v.get("versions").and_then(|x| x.as_object()).cloned())
        .unwrap_or_default()
}

fn save_obj(path: &Path, versions: &Map<String, Value>, note: &str) -> Result<()> {
    if let Some(d) = path.parent() {
        std::fs::create_dir_all(d)?;
    }
    write_json(
        path,
        &json!({"schema": "gov.skill-bindings/1", "note": note, "versions": versions}),
    )
}

// ------------------------------------------------------------------------------------------ scenarios

/// The statement a scenario asserts (its `given` and `expect`), which an executable check is bound to.
pub fn statement_sha256(sc: &Value) -> String {
    hash_value(
        &json!({"given": sc.get("given").cloned().unwrap_or(Value::Null), "expect": sc.get("expect").cloned().unwrap_or(Value::Null)}),
    )
}

/// The kernel-skill scenario checks this runtime ships (`framework/health/SKILL_SCENARIO_CHECKS.yaml`). Each entry is
/// bound to the exact statement of the scenario it checks, so a kernel whose scenario text differs is never checked
/// against the wrong expectation.
pub const EMBEDDED_SCENARIO_CHECKS: &str =
    include_str!("../../framework/health/SKILL_SCENARIO_CHECKS.yaml");

/// Executable checks for kernel-skill scenarios: the installed (verified) kernel's `health/SKILL_SCENARIO_CHECKS.yaml`
/// when the kernel ships one, otherwise the copy compiled into this runtime.
pub fn kernel_scenario_checks(p: &Project) -> Vec<Value> {
    let path = crate::kernel_trust::trusted_root(p)
        .join("health")
        .join("SKILL_SCENARIO_CHECKS.yaml");
    read_yaml(&path)
        .ok()
        .or_else(|| serde_yaml::from_str::<Value>(EMBEDDED_SCENARIO_CHECKS).ok())
        .and_then(|v| v["checks"].as_array().cloned())
        .unwrap_or_default()
}

/// How a scenario will be evaluated.
#[derive(Debug, Clone)]
pub enum ScenarioPlan {
    Executable(Value),
    /// Not executed by the suite; `check` is the executable form of a `deferred` scenario, if the entry carries one.
    Declared {
        mode: String,
        reason: String,
        check: Option<Value>,
    },
    Unexecutable(String),
}

pub fn scenario_plan(skill: &Value, sc: &Value, kernel_checks: &[Value]) -> ScenarioPlan {
    let source = skill["_source"].as_str().unwrap_or("project");
    if source == "kernel" {
        let sid = skill["id"].as_str().unwrap_or("");
        let scid = sc["id"].as_str().unwrap_or("");
        let Some(entry) = kernel_checks
            .iter()
            .find(|c| c["skill"].as_str() == Some(sid) && c["scenario"].as_str() == Some(scid))
        else {
            return ScenarioPlan::Unexecutable(
                "the kernel supplies no executable check or declared execution mode for this scenario".into(),
            );
        };
        if entry["statement_sha256"].as_str() != Some(statement_sha256(sc).as_str()) {
            return ScenarioPlan::Unexecutable("the kernel's check was written for a different statement of this scenario (statement changed without the check)".into());
        }
        let mode = entry["mode"].as_str().unwrap_or("");
        return match mode {
            "executable" if entry["check"].is_object() => {
                ScenarioPlan::Executable(entry["check"].clone())
            }
            "agent" | "qualification" | "deferred" => ScenarioPlan::Declared {
                mode: mode.into(),
                reason: entry["reason"].as_str().unwrap_or("").into(),
                check: if mode == "deferred" && entry["check"].is_object() {
                    Some(entry["check"].clone())
                } else {
                    None
                },
            },
            _ => {
                ScenarioPlan::Unexecutable(format!("kernel check entry has unusable mode '{mode}'"))
            }
        };
    }
    if sc["check"].is_object() {
        return ScenarioPlan::Executable(sc["check"].clone());
    }
    match sc["execution"].as_str() {
        Some(m @ ("agent" | "qualification")) => ScenarioPlan::Declared {
            mode: m.into(),
            reason: sc["reason"].as_str().unwrap_or("").into(),
            check: None,
        },
        _ => ScenarioPlan::Unexecutable("the scenario has no executable `check` and declares no execution mode (`execution: agent|qualification` with a reason)".into()),
    }
}

/// The `gov` executable that runs scenario steps: this process's own binary. A cargo test harness is not the CLI,
/// so scenario execution is unavailable in-process there (reported, never faked).
pub fn gov_binary() -> Option<PathBuf> {
    let exe = std::env::current_exe().ok()?;
    let in_deps = exe
        .parent()
        .and_then(|d| d.file_name())
        .map(|n| n == "deps")
        .unwrap_or(false);
    if in_deps {
        None
    } else {
        Some(exe)
    }
}

const STEP_TIMEOUT: Duration = Duration::from_secs(120);

fn subst(s: &str, vars: &Map<String, Value>) -> String {
    let mut out = s.to_string();
    for (k, v) in vars {
        let val = v
            .as_str()
            .map(|x| x.to_string())
            .unwrap_or_else(|| v.to_string());
        out = out.replace(&format!("${{{k}}}"), &val);
    }
    out
}

fn subst_value(v: &Value, vars: &Map<String, Value>) -> Value {
    match v {
        Value::String(s) => Value::String(subst(s, vars)),
        Value::Array(a) => Value::Array(a.iter().map(|x| subst_value(x, vars)).collect()),
        Value::Object(o) => Value::Object(
            o.iter()
                .map(|(k, x)| (k.clone(), subst_value(x, vars)))
                .collect(),
        ),
        other => other.clone(),
    }
}

/// Resolve a dotted path in a JSON envelope. `body` is the result when ok, else the error details. A segment
/// `name[key=value]` selects the first array element whose `key` equals `value`.
/// Split a dotted path on the dots that are not inside a `[...]` selector.
fn split_path(path: &str) -> Vec<String> {
    let mut out = vec![];
    let mut cur = String::new();
    let mut depth = 0;
    for c in path.chars() {
        match c {
            '[' => {
                depth += 1;
                cur.push(c);
            }
            ']' => {
                depth -= 1;
                cur.push(c);
            }
            '.' if depth == 0 => out.push(std::mem::take(&mut cur)),
            _ => cur.push(c),
        }
    }
    out.push(cur);
    out
}

pub fn lookup<'a>(env: &'a Value, path: &str) -> Option<&'a Value> {
    let mut cur = env;
    let parts = split_path(path);
    let mut segs = parts.iter().map(|s| s.as_str()).peekable();
    if segs.peek() == Some(&"body") {
        segs.next();
        cur = if env["ok"].as_bool().unwrap_or(false) {
            &env["result"]
        } else {
            &env["error"]["details"]
        };
    }
    for seg in segs {
        if let Some((name, sel)) = seg.split_once('[') {
            let sel = sel.trim_end_matches(']');
            let (k, v) = sel.split_once('=')?;
            let arr = if name.is_empty() { cur } else { cur.get(name)? };
            cur = arr.as_array()?.iter().find(|e| {
                e.get(k)
                    .map(|x| match x.as_str() {
                        Some(s) => s == v,
                        None => serde_json::from_str::<Value>(v)
                            .map(|pv| pv == *x)
                            .unwrap_or(false),
                    })
                    .unwrap_or(false)
            })?;
        } else {
            cur = cur.get(seg)?;
        }
    }
    Some(cur)
}

fn check_expect(env: &Value, expect: &Value) -> std::result::Result<(), String> {
    if let Some(ok) = expect.get("ok").and_then(|v| v.as_bool()) {
        if env["ok"].as_bool() != Some(ok) {
            return Err(format!(
                "expected ok={ok}, got ok={} ({})",
                env["ok"],
                env["error"]["code"].as_str().unwrap_or("")
            ));
        }
    }
    if let Some(codes) = expect.get("error_code") {
        let want: Vec<String> = match codes {
            Value::String(s) => vec![s.clone()],
            Value::Array(a) => a
                .iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect(),
            _ => vec![],
        };
        let got = env["error"]["code"].as_str().unwrap_or("");
        if !want.iter().any(|w| w == got) {
            return Err(format!("expected error code in {want:?}, got '{got}'"));
        }
    }
    if let Some(eq) = expect.get("equals").and_then(|v| v.as_object()) {
        for (path, want) in eq {
            let got = lookup(env, path).cloned().unwrap_or(Value::Null);
            if &got != want {
                return Err(format!("expected {path} = {want}, got {got}"));
            }
        }
    }
    if let Some(one) = expect.get("one_of").and_then(|v| v.as_object()) {
        for (path, choices) in one {
            let got = lookup(env, path).cloned().unwrap_or(Value::Null);
            if !choices
                .as_array()
                .map(|a| a.contains(&got))
                .unwrap_or(false)
            {
                return Err(format!("expected {path} in {choices}, got {got}"));
            }
        }
    }
    if let Some(ne) = expect.get("nonempty").and_then(|v| v.as_array()) {
        for path in ne.iter().filter_map(|x| x.as_str()) {
            let got = lookup(env, path);
            let empty = match got {
                None | Some(Value::Null) => true,
                Some(Value::String(s)) => s.is_empty(),
                Some(Value::Array(a)) => a.is_empty(),
                Some(Value::Object(o)) => o.is_empty(),
                _ => false,
            };
            if empty {
                return Err(format!("expected {path} to be non-empty"));
            }
        }
    }
    Ok(())
}

fn safe_rel(root: &Path, rel: &str) -> std::result::Result<PathBuf, String> {
    if rel.is_empty() || rel.starts_with('/') || rel.split('/').any(|s| s == "..") {
        return Err(format!(
            "step path '{rel}' must be relative to the sandbox and stay inside it"
        ));
    }
    Ok(root.join(rel))
}

fn run_gov(
    gov: &Path,
    root: &Path,
    session: &str,
    role: &str,
    args: &[String],
) -> std::result::Result<Value, String> {
    let mut child = std::process::Command::new(gov)
        .args(["--json", "--root"])
        .arg(root)
        .args(["--session", session, "--role", role])
        .args(args)
        .current_dir(root)
        .env(crate::scheduler::sandbox::SANDBOX_ENV, "1")
        .env_remove("GOV_ROLE")
        .env_remove("GOV_SESSION")
        .stdin(std::process::Stdio::null())
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::piped())
        .spawn()
        .map_err(|e| format!("cannot start {}: {e}", gov.display()))?;
    let t0 = Instant::now();
    loop {
        match child.try_wait() {
            Ok(Some(_)) => break,
            Ok(None) if t0.elapsed() > STEP_TIMEOUT => {
                let _ = child.kill();
                return Err(format!("step timed out after {}s", STEP_TIMEOUT.as_secs()));
            }
            Ok(None) => std::thread::sleep(Duration::from_millis(5)),
            Err(e) => return Err(e.to_string()),
        }
    }
    let out = child.wait_with_output().map_err(|e| e.to_string())?;
    let text = String::from_utf8_lossy(&out.stdout).to_string();
    serde_json::from_str(&text).map_err(|_| {
        format!(
            "step output is not a JSON envelope (exit {:?}): {}",
            out.status.code(),
            text.chars().take(300).collect::<String>()
        )
    })
}

/// Execute a scenario check in a fresh sandbox copy of the project. Returns `(passed, transcript)`.
pub fn execute_check(p: &Project, gov: &Path, label: &str, check: &Value) -> Result<(bool, Value)> {
    let sb = crate::scheduler::sandbox::Sandbox::create(
        p,
        &format!("skill-{label}"),
        crate::scheduler::sandbox::SandboxOptions {
            runtime: true,
            git: true,
        },
    )?;
    let session = format!("S-skill-{}", crate::util::short_uuid());
    let mut vars = Map::new();
    vars.insert("root".into(), json!(sb.root.to_string_lossy()));
    let mut transcript = vec![];
    let steps = check["steps"].as_array().cloned().unwrap_or_default();
    if steps.is_empty() {
        return Ok((false, json!([{"error": "check has no steps"}])));
    }
    for (i, step) in steps.iter().enumerate() {
        let outcome: std::result::Result<Value, String> = (|| {
            if let Some(args) = step.get("gov").and_then(|a| a.as_array()) {
                let argv: Vec<String> = args
                    .iter()
                    .map(|a| subst(a.as_str().unwrap_or(&a.to_string()), &vars))
                    .collect();
                let role = step["role"].as_str().unwrap_or("orchestrator");
                let env = run_gov(gov, &sb.root, &session, role, &argv)?;
                let expect = step.get("expect").cloned().unwrap_or(json!({"ok": true}));
                check_expect(&env, &expect)?;
                if let Some(save) = step.get("save").and_then(|s| s.as_object()) {
                    for (name, path) in save {
                        let v = lookup(&env, path.as_str().unwrap_or(""))
                            .cloned()
                            .ok_or_else(|| format!("cannot save {name}: {path} not in output"))?;
                        vars.insert(name.clone(), v);
                    }
                }
                Ok(json!({"step": i, "gov": argv, "ok": env["ok"], "code": env["error"]["code"]}))
            } else if let Some(w) = step.get("write") {
                let rel = subst(w["path"].as_str().unwrap_or(""), &vars);
                let dst = safe_rel(&sb.root, &rel)?;
                if let Some(d) = dst.parent() {
                    std::fs::create_dir_all(d).map_err(|e| e.to_string())?;
                }
                // `text_parts` are joined at run time, so a probe value the scenario plants (e.g. a secret-like
                // literal) never exists whole in a kernel file the kernel's own scanner reads (WS-8 IP-R2-WS08-6)
                let body = if let Some(t) = w.get("text").and_then(|t| t.as_str()) {
                    subst(t, &vars)
                } else if let Some(parts) = w.get("text_parts").and_then(|t| t.as_array()) {
                    subst(
                        &parts
                            .iter()
                            .filter_map(|x| x.as_str())
                            .collect::<Vec<_>>()
                            .concat(),
                        &vars,
                    )
                } else {
                    serde_json::to_string_pretty(&subst_value(&w["json"], &vars))
                        .map_err(|e| e.to_string())?
                };
                std::fs::write(&dst, body).map_err(|e| e.to_string())?;
                Ok(json!({"step": i, "write": rel}))
            } else if let Some(y) = step.get("yaml_set") {
                let rel = subst(y["path"].as_str().unwrap_or(""), &vars);
                let dst = safe_rel(&sb.root, &rel)?;
                let mut doc = read_yaml(&dst).unwrap_or(json!({}));
                let keys: Vec<String> = y["key"]
                    .as_array()
                    .map(|a| {
                        a.iter()
                            .filter_map(|x| x.as_str().map(|s| s.to_string()))
                            .collect()
                    })
                    .unwrap_or_default();
                if keys.is_empty() {
                    return Err("yaml_set needs a non-empty key path".into());
                }
                let mut cur = &mut doc;
                for k in &keys[..keys.len() - 1] {
                    if !cur.get(k).map(|v| v.is_object()).unwrap_or(false) {
                        cur[k.as_str()] = json!({});
                    }
                    cur = &mut cur[k.as_str()];
                }
                cur[keys[keys.len() - 1].as_str()] = subst_value(&y["value"], &vars);
                crate::util::write_yaml(&dst, &doc).map_err(|e| e.to_string())?;
                Ok(json!({"step": i, "yaml_set": rel, "key": keys}))
            } else {
                Err(format!("unknown step kind: {step}"))
            }
        })();
        match outcome {
            Ok(t) => transcript.push(t),
            Err(why) => {
                transcript.push(json!({"step": i, "failed": why}));
                return Ok((false, anonymise(&json!(transcript), &sb.root)));
            }
        }
    }
    Ok((true, anonymise(&json!(transcript), &sb.root)))
}

/// Transcripts name the disposable sandbox as `<sandbox>`, never as a live path.
fn anonymise(v: &Value, sandbox_root: &Path) -> Value {
    crate::scheduler::sandbox::relocate_paths(v, sandbox_root, Path::new("<sandbox>"))
}

/// Execute scenario checks concurrently (each in its own sandbox and processes), at most four at a time.
fn run_checks(
    p: &Project,
    gov: &Path,
    jobs: Vec<(String, Value)>,
) -> std::collections::BTreeMap<String, Result<(bool, Value)>> {
    use std::sync::Mutex;
    let queue = Mutex::new(jobs);
    let out = Mutex::new(std::collections::BTreeMap::new());
    let (root, session, role) = (p.root.clone(), p.session_id.clone(), p.role.clone());
    let n = queue.lock().map(|q| q.len()).unwrap_or(0).min(4);
    std::thread::scope(|s| {
        for w in 0..n {
            let (queue, out, root, session, role) = (&queue, &out, &root, &session, &role);
            let _ = std::thread::Builder::new()
                .name(format!("gov-skill-{w}"))
                .spawn_scoped(s, move || loop {
                    let job = queue.lock().ok().and_then(|mut q| q.pop());
                    let Some((label, check)) = job else { break };
                    let tp =
                        Project::open(root).with_session(Some(session.clone()), Some(role.clone()));
                    let r = execute_check(&tp, gov, &label, &check);
                    if let Ok(mut o) = out.lock() {
                        o.insert(label, r);
                    }
                });
        }
    });
    // anything a worker could not take (spawn failure) runs here
    let rest: Vec<(String, Value)> = queue.into_inner().unwrap_or_default();
    let mut out = out.into_inner().unwrap_or_default();
    for (label, check) in rest {
        let r = execute_check(p, gov, &label, &check);
        out.insert(label, r);
    }
    out
}

/// Options for [`regression`].
#[derive(Debug, Clone, Default)]
pub struct RegressionOptions {
    /// Execute executable scenarios (false: plan only).
    pub execute: bool,
    /// Limit to one skill id.
    pub only: Option<String>,
    /// Record the first-seen content of each version in the machine-local observation ledger.
    pub observe: bool,
    /// Also execute the executable form of `deferred` scenarios (reported, never counted as passing or failing).
    pub include_deferred: bool,
}

/// The skill-regression evaluation behind the `skill_regression` family and `gov health skills`.
pub fn regression(p: &Project, opts: &RegressionOptions) -> (Vec<Value>, Value) {
    let fam = "skill_regression";
    let mut findings = vec![];
    let f = |sev: &str, msg: String, path: Option<String>| json!({"severity": sev, "family": fam, "message": msg, "path": path});
    let skills: Vec<Value> = list_skills(p)
        .into_iter()
        .filter(|s| {
            opts.only
                .as_deref()
                .map(|o| s["id"].as_str() == Some(o))
                .unwrap_or(true)
        })
        .collect();
    let bindings = load_obj(&bindings_read_path(p));
    let mut observed = load_obj(&observations_path(p));
    let mut observed_changed = false;
    let kernel_checks = kernel_scenario_checks(p);
    let runner = if opts.execute && !crate::scheduler::sandbox::inside_sandbox() {
        gov_binary()
    } else {
        None
    };
    // every executable check (and, on request, every deferred one) runs first, concurrently
    let mut jobs: Vec<(String, Value)> = vec![];
    if runner.is_some() {
        for s in &skills {
            let id = s["id"].as_str().unwrap_or("?");
            let active = matches!(s["status"].as_str(), Some("ACTIVE") | Some("VALIDATED"));
            for sc in s["validation_scenarios"]
                .as_array()
                .cloned()
                .unwrap_or_default()
            {
                let scid = sc["id"].as_str().unwrap_or("?");
                match scenario_plan(s, &sc, &kernel_checks) {
                    ScenarioPlan::Executable(check) if active => {
                        jobs.push((format!("{id}-{scid}"), check))
                    }
                    ScenarioPlan::Declared {
                        check: Some(check), ..
                    } if opts.include_deferred => {
                        jobs.push((format!("{id}-{scid}-deferred"), check))
                    }
                    _ => {}
                }
            }
        }
    }
    let mut results = match &runner {
        Some(gov) if !jobs.is_empty() => run_checks(p, gov, jobs),
        _ => Default::default(),
    };
    let mut rows = vec![];
    let (mut passed, mut failed, mut declared, mut unexecutable, mut not_run) = (0, 0, 0, 0, 0);
    for s in &skills {
        let id = s["id"].as_str().unwrap_or("?").to_string();
        let path = s["_path"].as_str().map(|x| x.to_string());
        let vid = version_id(s);
        let digest = s["_content_sha256"].as_str().unwrap_or("").to_string();
        let source = s["_source"].as_str().unwrap_or("project").to_string();
        let mut plain = s.clone();
        if let Some(o) = plain.as_object_mut() {
            o.retain(|k, _| !k.starts_with('_'));
        }
        if let Ok(errs) = p.schemas().errors("skill", &plain) {
            for e in errs.iter().take(3) {
                findings.push(f("medium", format!("{id}: {e}"), path.clone()));
            }
        }
        // ---- version ↔ content
        let mut binding_state = "unbound";
        if let Some(b) = bindings.get(&vid) {
            if b["content_sha256"].as_str() == Some(digest.as_str()) {
                binding_state = "bound";
            } else {
                binding_state = "conflict";
                findings.push(f("high", format!("{vid}: content changed without a version change (bound content {} recorded {}, now {}); bump the version and re-validate", short(b["content_sha256"].as_str().unwrap_or("")), b["bound_at"].as_str().unwrap_or("?"), short(&digest)), path.clone()));
            }
        }
        match observed.get(&vid) {
            Some(o) if o["content_sha256"].as_str() != Some(digest.as_str()) => {
                findings.push(f("high", format!("{vid}: content changed without a version change since this machine first observed it ({} at {}, now {}); bump the version", short(o["content_sha256"].as_str().unwrap_or("")), o["first_seen"].as_str().unwrap_or("?"), short(&digest)), path.clone()));
            }
            Some(_) => {}
            None if opts.observe => {
                observed.insert(
                    vid.clone(),
                    json!({"content_sha256": digest, "first_seen": now_iso(), "source": source}),
                );
                observed_changed = true;
            }
            None => {}
        }
        // ---- scenarios
        let scenarios = s["validation_scenarios"]
            .as_array()
            .cloned()
            .unwrap_or_default();
        if scenarios.is_empty() {
            findings.push(f(
                "medium",
                format!("{id}: no validation scenarios"),
                path.clone(),
            ));
        }
        let active = matches!(s["status"].as_str(), Some("ACTIVE") | Some("VALIDATED"));
        let mut sc_rows = vec![];
        for sc in &scenarios {
            let scid = sc["id"].as_str().unwrap_or("?").to_string();
            let row = match scenario_plan(s, sc, &kernel_checks) {
                ScenarioPlan::Executable(check) => {
                    if !active {
                        json!({"scenario": scid, "status": "skipped (skill not ACTIVE/VALIDATED)"})
                    } else if runner.is_some() {
                        let _ = &check;
                        match results.remove(&format!("{id}-{scid}")).unwrap_or_else(|| {
                            Err(GovError::new(
                                "SCENARIO_NOT_RUN",
                                "the scenario was not scheduled",
                            ))
                        }) {
                            Ok((true, t)) => {
                                passed += 1;
                                json!({"scenario": scid, "status": "passed", "transcript": t})
                            }
                            Ok((false, t)) => {
                                failed += 1;
                                findings.push(f("medium", format!("{id} {scid}: validation scenario FAILED — given '{}', expected '{}': {}", sc["given"].as_str().unwrap_or(""), sc["expect"].as_str().unwrap_or(""), t.as_array().and_then(|a| a.last()).map(|x| x["failed"].to_string()).unwrap_or_default()), path.clone()));
                                json!({"scenario": scid, "status": "failed", "transcript": t})
                            }
                            Err(e) => {
                                failed += 1;
                                findings.push(f(
                                    "medium",
                                    format!(
                                        "{id} {scid}: validation scenario could not run: [{}] {}",
                                        e.code, e.message
                                    ),
                                    path.clone(),
                                ));
                                json!({"scenario": scid, "status": "error", "error": e.code})
                            }
                        }
                    } else {
                        not_run += 1;
                        let why = if crate::scheduler::sandbox::inside_sandbox() {
                            "not run inside a health sandbox (no nested scenario execution)"
                        } else if !opts.execute {
                            "planning only"
                        } else {
                            "no gov executable available in this process (a test harness is not the CLI)"
                        };
                        findings.push(f(
                            "low",
                            format!("{id} {scid}: executable scenario not run: {why}"),
                            path.clone(),
                        ));
                        json!({"scenario": scid, "status": "not-run", "reason": why})
                    }
                }
                ScenarioPlan::Declared {
                    mode,
                    reason,
                    check,
                } => {
                    declared += 1;
                    findings.push(f("low", format!("{id} {scid}: not executed by the governance suite — declared {mode}: {reason}"), path.clone()));
                    let mut row = json!({"scenario": scid, "status": format!("declared-{mode}"), "reason": reason});
                    if let (true, Some(_), Some(_)) = (opts.include_deferred, check, &runner) {
                        row["deferred_check"] = match results
                            .remove(&format!("{id}-{scid}-deferred"))
                            .unwrap_or_else(|| {
                                Err(GovError::new(
                                    "SCENARIO_NOT_RUN",
                                    "the scenario was not scheduled",
                                ))
                            }) {
                            Ok((ok, t)) => {
                                json!({"executed_on_request": true, "expectation_met": ok, "transcript": t})
                            }
                            Err(e) => json!({"executed_on_request": true, "error": e.code}),
                        };
                    }
                    row
                }
                ScenarioPlan::Unexecutable(why) => {
                    unexecutable += 1;
                    findings.push(f("medium", format!("{id} {scid}: validation scenario cannot be executed, so skill regression cannot pass — {why}"), path.clone()));
                    json!({"scenario": scid, "status": "unexecutable", "reason": why})
                }
            };
            sc_rows.push(row);
        }
        rows.push(json!({"skill": id, "version": s["version"], "source": source, "content_sha256": digest, "binding": binding_state, "scenarios": sc_rows}));
    }
    if observed_changed {
        let _ = save_obj(
            &observations_path(p),
            &observed,
            "machine-local first-seen content per skill version (derived; the tracked binding is governance/registry/skill-bindings.json)",
        );
    }
    let detail = json!({"skills": rows, "executed_passed": passed, "executed_failed": failed, "declared_not_executed": declared, "unexecutable": unexecutable, "not_run": not_run, "runner": runner.map(|r| r.to_string_lossy().to_string())});
    (findings, detail)
}

fn short(s: &str) -> String {
    s.chars().take(12).collect()
}

/// `gov health skills --record`: execute every executable scenario and bind each skill version whose scenarios all
/// pass to its content in the tracked `skill-bindings.json`. A version already bound to different content is refused.
pub fn record(p: &Project, only: Option<&str>) -> Result<Value> {
    crate::orchestration::control::guard_write(p, "skills record")?;
    // binding a version to its content is a governed write to OS-written state: the `record_skill_binding` operation
    // class is declared in AUTHORITY_POLICY at L3 (integration P2-AR-0022, `38811b8`)
    crate::authority::require(p, "record_skill_binding")?;
    let (findings, detail) = regression(
        p,
        &RegressionOptions {
            execute: true,
            only: only.map(|s| s.to_string()),
            observe: true,
            include_deferred: false,
        },
    );
    // the bindings move to where they belong before they are written (IP-R3-WS06-7)
    relocate_bindings(p)?;
    let mut bindings = load_obj(&bindings_path(p));
    let mut bound = vec![];
    let mut refused = vec![];
    for row in detail["skills"].as_array().cloned().unwrap_or_default() {
        let vid = format!(
            "{}@{}",
            row["skill"].as_str().unwrap_or("?"),
            row["version"].as_str().unwrap_or("?")
        );
        let digest = row["content_sha256"].as_str().unwrap_or("").to_string();
        let all_pass = row["scenarios"]
            .as_array()
            .map(|a| {
                a.iter().all(|x| {
                    x["status"] == "passed"
                        || x["status"]
                            .as_str()
                            .map(|s| s.starts_with("declared-"))
                            .unwrap_or(false)
                })
            })
            .unwrap_or(false);
        match bindings.get(&vid) {
            Some(b) if b["content_sha256"].as_str() != Some(digest.as_str()) => {
                refused.push(json!({"version": vid, "reason": "already bound to different content; bump the version"}));
            }
            Some(_) => {}
            None if all_pass => {
                bindings.insert(vid.clone(), json!({"content_sha256": digest, "source": row["source"], "bound_at": now_iso(), "bound_by": {"role": p.role, "session": p.session_id},
                    "runtime_binary_sha256": crate::verification::currency::runtime_identity()["binary_sha256"],
                    "scenarios": row["scenarios"].as_array().map(|a| a.iter().map(|x| json!({"scenario": x["scenario"], "status": x["status"]})).collect::<Vec<_>>())}));
                bound.push(vid);
            }
            None => refused.push(json!({"version": vid, "reason": "not every validation scenario passed or is declared"})),
        }
    }
    if !bound.is_empty() {
        save_obj(
            &bindings_path(p),
            &bindings,
            "OS-written: each skill version bound to the content whose validation scenarios passed (gov health skills --record)",
        )?;
    }
    if !refused.iter().all(|r| {
        r["reason"]
            .as_str()
            .map(|s| s.starts_with("not every"))
            .unwrap_or(false)
    }) {
        return Err(GovError::new("SKILL_VERSION_CONTENT_CONFLICT", "a skill version is already bound to different content: a changed method needs a new version").with_details(json!({"refused": refused, "bound": bound, "findings": findings})));
    }
    Ok(json!({"bound": bound, "refused": refused, "findings": findings, "detail": detail}))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn content_digest_ignores_annotations_and_detects_method_changes() {
        let a = json!({"id": "SKL-A", "version": "1.0.0", "method": [{"step": "do"}]});
        let mut b = a.clone();
        b["_source"] = json!("project");
        assert_eq!(content_sha256(&a), content_sha256(&b));
        let mut c = a.clone();
        c["method"] = json!([{"step": "do-something-else"}]);
        assert_ne!(content_sha256(&a), content_sha256(&c));
    }

    #[test]
    fn scenario_plans() {
        let proj = json!({"id": "SKL-P", "_source": "project"});
        assert!(matches!(
            scenario_plan(&proj, &json!({"id": "V1", "expect": "x"}), &[]),
            ScenarioPlan::Unexecutable(_)
        ));
        assert!(matches!(
            scenario_plan(
                &proj,
                &json!({"id": "V1", "expect": "x", "check": {"steps": []}}),
                &[]
            ),
            ScenarioPlan::Executable(_)
        ));
        assert!(matches!(
            scenario_plan(
                &proj,
                &json!({"id": "V1", "expect": "x", "execution": "agent", "reason": "r"}),
                &[]
            ),
            ScenarioPlan::Declared { .. }
        ));
        let kern = json!({"id": "SKL-K", "_source": "kernel"});
        let sc = json!({"id": "V1", "given": "g", "expect": "e"});
        let entry = json!({"skill": "SKL-K", "scenario": "V1", "statement_sha256": statement_sha256(&sc), "mode": "executable", "check": {"steps": [{"gov": ["status"]}]}});
        assert!(matches!(
            scenario_plan(&kern, &sc, &[entry.clone()]),
            ScenarioPlan::Executable(_)
        ));
        let changed = json!({"id": "V1", "given": "g", "expect": "something else"});
        assert!(matches!(
            scenario_plan(&kern, &changed, &[entry]),
            ScenarioPlan::Unexecutable(_)
        ));
    }

    #[test]
    fn every_kernel_scenario_has_a_bound_check_or_declared_mode() {
        let doc: Value = serde_yaml::from_str(EMBEDDED_SCENARIO_CHECKS).unwrap();
        let checks = doc["checks"].as_array().unwrap().clone();
        let dir = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../framework/skills");
        let mut n = 0;
        for e in std::fs::read_dir(&dir).unwrap() {
            let path = e.unwrap().path();
            if path.extension().map(|x| x != "yaml").unwrap_or(true) {
                continue;
            }
            let mut skill = crate::util::read_yaml(&path).unwrap();
            skill["_source"] = json!("kernel");
            for sc in skill["validation_scenarios"]
                .as_array()
                .cloned()
                .unwrap_or_default()
            {
                n += 1;
                let plan = scenario_plan(&skill, &sc, &checks);
                assert!(
                    !matches!(plan, ScenarioPlan::Unexecutable(_)),
                    "{} {}: {plan:?}",
                    skill["id"],
                    sc["id"]
                );
            }
        }
        assert!(n >= 14, "kernel scenarios found: {n}");
    }

    #[test]
    fn lookup_and_expectations() {
        let env = json!({"ok": false, "error": {"code": "UNHEALTHY", "details": {"checks": [{"id": "D012", "ok": true}]}}});
        assert_eq!(lookup(&env, "body.checks[id=D012].ok"), Some(&json!(true)));
        assert!(check_expect(&env, &json!({"equals": {"body.checks[id=D012].ok": true}})).is_ok());
        assert!(check_expect(&env, &json!({"ok": true})).is_err());
        assert!(check_expect(&env, &json!({"error_code": ["UNHEALTHY", "X"]})).is_ok());
        assert!(check_expect(&env, &json!({"nonempty": ["body.missing"]})).is_err());
        let env2 = json!({"ok": true, "result": {"findings": [{"path": "spec/research/RES-1.yaml", "severity": "high"}]}});
        assert_eq!(
            lookup(
                &env2,
                "body.findings[path=spec/research/RES-1.yaml].severity"
            ),
            Some(&json!("high"))
        );
    }
}
