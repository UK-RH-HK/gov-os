//! Emergency controls (framework §74): PAUSE, FREEZE_WRITES, CANCEL_AGENTS, RESUME. Authority-checked; state lives in
//! the runtime directory (never inside the rebuild-deleted index) and is honoured by every mutating operation.
use crate::authority;
use crate::util::{now_iso, read_json, write_json};
use crate::{GovError, Project, Result};
use serde_json::{json, Value};

pub fn path(p: &Project) -> std::path::PathBuf {
    p.runtime_dir().join("control.json")
}

pub fn state(p: &Project) -> Value {
    read_json(&path(p)).unwrap_or(json!({"mode": "RUNNING", "writes_frozen": false, "agents_cancelled": false, "updated_at": null, "reason": null}))
}

pub fn set(p: &Project, mode: &str, reason: Option<&str>) -> Result<Value> {
    authority::require(
        p,
        if mode == "RESUME" {
            "resume_control"
        } else {
            "emergency_control"
        },
    )?;
    let mut s = state(p);
    match mode {
        "PAUSE" => {
            s["mode"] = json!("PAUSED");
        }
        "FREEZE_WRITES" => {
            s["writes_frozen"] = json!(true);
        }
        "CANCEL_AGENTS" => {
            s["agents_cancelled"] = json!(true);
            s["mode"] = json!("PAUSED");
        }
        "RESUME" => {
            s["mode"] = json!("RUNNING");
            s["writes_frozen"] = json!(false);
            s["agents_cancelled"] = json!(false);
        }
        _ => {
            return Err(GovError::new(
                "USAGE",
                format!("unknown control mode {mode}"),
            ))
        }
    }
    s["updated_at"] = json!(now_iso());
    s["reason"] = json!(reason);
    s["session"] = json!(p.session_id);
    s["role"] = json!(p.role);
    write_json(&path(p), &s)?;
    Ok(s)
}

/// Every mutating governance operation calls this first.
pub fn guard_write(p: &Project, operation: &str) -> Result<()> {
    let s = state(p);
    if s["writes_frozen"].as_bool().unwrap_or(false) {
        return Err(GovError::new("FROZEN", format!("writes are frozen (FREEZE_WRITES active); '{operation}' refused. Run `gov resume` (L4) to lift.")));
    }
    if s["mode"].as_str() == Some("PAUSED") {
        return Err(GovError::new(
            "PAUSED",
            format!("execution is paused; '{operation}' refused. Run `gov resume` to continue."),
        ));
    }
    Ok(())
}
