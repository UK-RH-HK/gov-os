//! Session claims are deterministic concurrency state (framework §11.1): they live in their own store
//! (`.governance-runtime/claims.db`) that derived-memory rebuilds never delete.
use crate::util::now_iso;
use crate::{GovError, Project, Result};
use rusqlite::{params, Connection, OptionalExtension};
use serde_json::{json, Value};
use std::path::PathBuf;

pub const DEFAULT_LEASE_SECS: i64 = 4 * 3600;
fn now_epoch() -> i64 {
    chrono::Utc::now().timestamp()
}
fn to_iso(epoch: i64) -> String {
    chrono::DateTime::<chrono::Utc>::from_timestamp(epoch, 0)
        .map(|d| d.format("%Y-%m-%dT%H:%M:%SZ").to_string())
        .unwrap_or_default()
}
fn from_iso(s: &str) -> i64 {
    chrono::DateTime::parse_from_rfc3339(s)
        .map(|d| d.timestamp())
        .unwrap_or(0)
}

pub struct ClaimsStore {
    pub conn: Connection,
    pub path: PathBuf,
}

impl ClaimsStore {
    pub fn path_for(p: &Project) -> PathBuf {
        p.runtime_dir().join("claims.db")
    }
    pub fn open(p: &Project) -> Result<ClaimsStore> {
        let path = Self::path_for(p);
        if let Some(d) = path.parent() {
            std::fs::create_dir_all(d)?;
        }
        let conn = Connection::open(&path)?;
        conn.execute_batch("PRAGMA journal_mode=WAL; CREATE TABLE IF NOT EXISTS claims (task_id TEXT PRIMARY KEY, session_id TEXT, role TEXT, claimed_at TEXT, expires_at TEXT);")?;
        Ok(ClaimsStore { conn, path })
    }
    pub fn integrity_ok(&self) -> bool {
        self.conn
            .query_row("PRAGMA integrity_check", [], |r| r.get::<_, String>(0))
            .map(|s| s == "ok")
            .unwrap_or(false)
    }
    pub fn claim(
        &self,
        task_id: &str,
        session: &str,
        role: &str,
        lease_secs: Option<i64>,
    ) -> Result<Value> {
        let lease = lease_secs.unwrap_or(DEFAULT_LEASE_SECS);
        if let Some(existing) = self.get(task_id)? {
            let holder = existing["session_id"].as_str().unwrap_or("");
            let expires = from_iso(existing["expires_at"].as_str().unwrap_or(""));
            if holder != session && expires > now_epoch() {
                return Err(GovError::new(
                    "TASK_CLAIMED",
                    format!(
                        "{task_id} is claimed by session {holder} until {}",
                        existing["expires_at"]
                    ),
                )
                .with_details(existing));
            }
        }
        let claimed_at = now_iso();
        let expires_at = to_iso(now_epoch() + lease);
        self.conn.execute("INSERT OR REPLACE INTO claims(task_id, session_id, role, claimed_at, expires_at) VALUES (?1,?2,?3,?4,?5)", params![task_id, session, role, claimed_at, expires_at])?;
        Ok(
            json!({"task_id": task_id, "session_id": session, "role": role, "claimed_at": claimed_at, "expires_at": expires_at}),
        )
    }
    pub fn get(&self, task_id: &str) -> Result<Option<Value>> {
        Ok(self.conn.query_row("SELECT task_id, session_id, role, claimed_at, expires_at FROM claims WHERE task_id=?1", params![task_id], |r| Ok(json!({"task_id": r.get::<_, String>(0)?, "session_id": r.get::<_, String>(1)?, "role": r.get::<_, String>(2)?, "claimed_at": r.get::<_, String>(3)?, "expires_at": r.get::<_, String>(4)?}))).optional()?)
    }
    pub fn holder(&self, task_id: &str) -> Result<Option<Value>> {
        Ok(self
            .get(task_id)?
            .filter(|c| from_iso(c["expires_at"].as_str().unwrap_or("")) > now_epoch()))
    }
    pub fn release(&self, task_id: &str, session: &str, force: bool) -> Result<bool> {
        if let Some(existing) = self.get(task_id)? {
            let holder = existing["session_id"].as_str().unwrap_or("");
            if holder != session && !force {
                return Err(GovError::new("TASK_CLAIMED", format!("{task_id} is held by {holder}; releasing another session's claim requires --force (L3+)")));
            }
            self.conn
                .execute("DELETE FROM claims WHERE task_id=?1", params![task_id])?;
            return Ok(true);
        }
        Ok(false)
    }
    pub fn list(&self) -> Result<Vec<Value>> {
        let mut stmt = self.conn.prepare(
            "SELECT task_id, session_id, role, claimed_at, expires_at FROM claims ORDER BY task_id",
        )?;
        let rows = stmt.query_map([], |r| Ok(json!({"task_id": r.get::<_, String>(0)?, "session_id": r.get::<_, String>(1)?, "role": r.get::<_, String>(2)?, "claimed_at": r.get::<_, String>(3)?, "expires_at": r.get::<_, String>(4)?})))?;
        let mut out = vec![];
        for r in rows {
            let mut c = r?;
            c["expired"] = json!(from_iso(c["expires_at"].as_str().unwrap_or("")) <= now_epoch());
            out.push(c);
        }
        Ok(out)
    }
    pub fn active_sessions(&self) -> Result<Vec<String>> {
        let mut s: Vec<String> = self
            .list()?
            .into_iter()
            .filter(|c| !c["expired"].as_bool().unwrap_or(true))
            .filter_map(|c| c["session_id"].as_str().map(|x| x.to_string()))
            .collect();
        s.sort();
        s.dedup();
        Ok(s)
    }
    pub fn sweep_expired(&self) -> Result<usize> {
        let expired: Vec<String> = self
            .list()?
            .into_iter()
            .filter(|c| c["expired"].as_bool().unwrap_or(false))
            .map(|c| c["task_id"].as_str().unwrap_or("").to_string())
            .collect();
        for t in &expired {
            self.conn
                .execute("DELETE FROM claims WHERE task_id=?1", params![t])?;
        }
        Ok(expired.len())
    }
    /// Insert a raw claim (test/fixture use: e.g. an already-expired lease).
    pub fn insert_raw(
        &self,
        task_id: &str,
        session: &str,
        role: &str,
        claimed_at: &str,
        expires_at: &str,
    ) -> Result<()> {
        self.conn.execute("INSERT OR REPLACE INTO claims(task_id, session_id, role, claimed_at, expires_at) VALUES (?1,?2,?3,?4,?5)", params![task_id, session, role, claimed_at, expires_at])?;
        Ok(())
    }
}
