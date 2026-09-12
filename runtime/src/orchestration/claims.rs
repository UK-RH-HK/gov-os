//! Session claims with leases (concurrency/session claim governance test family). Backed by the claims store,
//! which is separate from the rebuild-deleted derived index (framework §11.1 deterministic memory).
use crate::memory::claims::ClaimsStore;
use crate::{Project, Result};
use serde_json::Value;

pub fn claim(
    p: &Project,
    task_id: &str,
    session: &str,
    role: &str,
    lease_secs: Option<i64>,
) -> Result<Value> {
    ClaimsStore::open(p)?.claim(task_id, session, role, lease_secs)
}
pub fn release(p: &Project, task_id: &str, session: &str, force: bool) -> Result<bool> {
    ClaimsStore::open(p)?.release(task_id, session, force)
}
pub fn holder(p: &Project, task_id: &str) -> Result<Option<Value>> {
    ClaimsStore::open(p)?.holder(task_id)
}
pub fn list(p: &Project) -> Result<Vec<Value>> {
    ClaimsStore::open(p)?.list()
}
pub fn sweep_expired(p: &Project) -> Result<usize> {
    ClaimsStore::open(p)?.sweep_expired()
}
pub fn active_sessions(p: &Project) -> Result<Vec<String>> {
    ClaimsStore::open(p)?.active_sessions()
}
