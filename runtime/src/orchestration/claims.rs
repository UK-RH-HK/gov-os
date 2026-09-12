//! Session claims with leases (concurrency/session claim governance test family).
use crate::memory::db::RuntimeDb;
use crate::util::now_iso;
use crate::{GovError, Result};
use serde_json::{json, Value};

pub const DEFAULT_LEASE_SECS: i64 = 4 * 3600;

fn now_epoch() -> i64 { chrono::Utc::now().timestamp() }
fn to_iso(epoch: i64) -> String { chrono::DateTime::<chrono::Utc>::from_timestamp(epoch, 0).map(|d| d.format("%Y-%m-%dT%H:%M:%SZ").to_string()).unwrap_or_default() }
fn from_iso(s: &str) -> i64 { chrono::DateTime::parse_from_rfc3339(s).map(|d| d.timestamp()).unwrap_or(0) }

pub fn claim(db: &RuntimeDb, task_id: &str, session: &str, role: &str, lease_secs: Option<i64>) -> Result<Value> {
    let lease = lease_secs.unwrap_or(DEFAULT_LEASE_SECS);
    if let Some(existing) = db.query_one("SELECT * FROM claims WHERE task_id=?1", &[&task_id])? {
        let holder = existing["session_id"].as_str().unwrap_or("");
        let expires = from_iso(existing["expires_at"].as_str().unwrap_or(""));
        if holder != session && expires > now_epoch() {
            return Err(GovError::new("TASK_CLAIMED", format!("{task_id} is claimed by session {holder} until {}", existing["expires_at"])).with_details(existing));
        }
    }
    let claimed_at = now_iso();
    let expires_at = to_iso(now_epoch() + lease);
    db.exec("INSERT OR REPLACE INTO claims(task_id, session_id, role, claimed_at, expires_at) VALUES (?1,?2,?3,?4,?5)", &[&task_id, &session, &role, &claimed_at, &expires_at])?;
    Ok(json!({"task_id": task_id, "session_id": session, "role": role, "claimed_at": claimed_at, "expires_at": expires_at}))
}

pub fn release(db: &RuntimeDb, task_id: &str, session: &str, force: bool) -> Result<bool> {
    if let Some(existing) = db.query_one("SELECT * FROM claims WHERE task_id=?1", &[&task_id])? {
        let holder = existing["session_id"].as_str().unwrap_or("");
        if holder != session && !force { return Err(GovError::new("TASK_CLAIMED", format!("{task_id} is held by {holder}; use --force (L3+) to release"))); }
        db.exec("DELETE FROM claims WHERE task_id=?1", &[&task_id])?;
        return Ok(true);
    }
    Ok(false)
}

pub fn holder(db: &RuntimeDb, task_id: &str) -> Result<Option<Value>> {
    Ok(db.query_one("SELECT * FROM claims WHERE task_id=?1", &[&task_id])?.filter(|c| from_iso(c["expires_at"].as_str().unwrap_or("")) > now_epoch()))
}

pub fn list(db: &RuntimeDb) -> Result<Vec<Value>> {
    let mut out = db.query("SELECT * FROM claims ORDER BY task_id", &[])?;
    for c in out.iter_mut() { let exp = from_iso(c["expires_at"].as_str().unwrap_or("")); c["expired"] = json!(exp <= now_epoch()); }
    Ok(out)
}

pub fn sweep_expired(db: &RuntimeDb) -> Result<usize> {
    let expired: Vec<String> = list(db)?.into_iter().filter(|c| c["expired"].as_bool().unwrap_or(false)).map(|c| c["task_id"].as_str().unwrap_or("").to_string()).collect();
    for t in &expired { db.exec("DELETE FROM claims WHERE task_id=?1", &[t])?; }
    Ok(expired.len())
}
