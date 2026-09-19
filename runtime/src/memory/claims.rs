//! Session claims are deterministic concurrency state (framework §11.1): they live in their own store
//! (`.governance-runtime/claims.db`) that derived-memory rebuilds never delete.
//!
//! **Atomicity (Contract v3:389, BC-P2-15).** Every read-decide-write on the claims table runs inside one
//! `BEGIN IMMEDIATE` transaction: SQLite grants the write lock to one connection at a time, across processes, so
//! the check ("is the task held? does the budget allow another session? does the mutation scope overlap a live
//! claim?") and the insert can never interleave with another claimant's. A concurrent claimant waits on the lock
//! (busy timeout) and then sees the committed winner, receiving `TASK_CLAIMED`.
//!
//! **Layout.** The `claims` table keeps its original five columns (task, session, role, claimed_at, expires_at), so
//! tools and fault-injection harnesses that write it positionally keep working. What a claim adds — its unit of
//! isolation and its mutation scope — lives in `claim_isolation`, bound to the exact claim instance
//! (task, session, claimed_at): a row written into `claims` by anything else carries no isolation record and is read
//! as an unknown worktree with an unrestricted scope (the conservative reading).
//!
//! **One store per repository, not per checkout.** Linked git worktrees of one repository share the claims store
//! of the main worktree (see [`ClaimsStore::path_for`]), so a claim made from one worktree is visible — and
//! collides — in every other; the claim records which worktree it was made from (its unit of isolation).
use crate::util::now_iso;
use crate::{GovError, Project, Result};
use rusqlite::{params, Connection, OptionalExtension, Transaction, TransactionBehavior};
use serde_json::{json, Value};
use std::path::{Path, PathBuf};
use std::time::Duration;

pub const DEFAULT_LEASE_SECS: i64 = 4 * 3600;
/// How long a claimant waits for another claimant's transaction before failing (typed `CLAIMS_BUSY`).
pub const BUSY_TIMEOUT: Duration = Duration::from_secs(20);

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

/// The unit of isolation a claim is made from (Contract v3:388 "Sessions/worktrees/tasks can be claimed").
#[derive(Debug, Clone, Default)]
pub struct Isolation {
    /// Canonical root of the working tree the session mutates (one per git worktree).
    pub worktree: String,
    /// The worktree's own git dir (distinguishes linked worktrees of one repository).
    pub git_dir: String,
    pub branch: String,
    pub head: String,
}

/// Everything a claim decision needs, decided atomically by [`ClaimsStore::claim_exclusive`].
pub struct ClaimRequest<'a> {
    pub task_id: &'a str,
    pub session: &'a str,
    pub role: &'a str,
    pub isolation: &'a Isolation,
    /// The task's mutation scope (allowed path patterns; `**` = unrestricted).
    pub scope: &'a [String],
    pub lease_secs: Option<i64>,
    /// BUDGET_POLICY.defaults.max_parallel_agents; `None` applies no budget.
    pub max_parallel_sessions: Option<usize>,
}

pub struct ClaimsStore {
    pub conn: Connection,
    pub path: PathBuf,
}

/// The claim with its isolation record (joined on the exact claim instance).
const SELECT_CLAIMS: &str = "SELECT c.task_id, c.session_id, c.role, c.claimed_at, c.expires_at, i.worktree, i.git_dir, i.branch, i.head, i.scope FROM claims c LEFT JOIN claim_isolation i ON i.task_id = c.task_id AND i.session_id IS c.session_id AND i.claimed_at IS c.claimed_at";

fn row_to_value(r: &rusqlite::Row) -> rusqlite::Result<Value> {
    let opt = |i: usize| -> rusqlite::Result<Option<String>> { r.get::<_, Option<String>>(i) };
    let scope: Value = opt(9)?
        .and_then(|s| serde_json::from_str(&s).ok())
        .unwrap_or(Value::Null);
    Ok(json!({
        "task_id": r.get::<_, String>(0)?, "session_id": opt(1)?.unwrap_or_default(), "role": opt(2)?.unwrap_or_default(),
        "claimed_at": opt(3)?.unwrap_or_default(), "expires_at": opt(4)?.unwrap_or_default(),
        "worktree": opt(5)?, "git_dir": opt(6)?, "branch": opt(7)?, "head": opt(8)?, "scope": scope,
    }))
}
fn is_live(c: &Value, now: i64) -> bool {
    from_iso(c["expires_at"].as_str().unwrap_or("")) > now
}
fn busy(e: rusqlite::Error, what: &str) -> GovError {
    let s = e.to_string();
    if s.contains("locked") || s.contains("busy") {
        GovError::new(
            "CLAIMS_BUSY",
            format!("the claims store stayed locked by another session for {}s while {what}; retry the command", BUSY_TIMEOUT.as_secs()),
        )
    } else {
        GovError::new("DB_ERROR", format!("claims store: {what}: {s}"))
    }
}

impl ClaimsStore {
    /// The repository's claims store. For a project in the main worktree (or outside git) this is
    /// `.governance-runtime/claims.db` under the project root. For a project in a **linked** git worktree it is the
    /// same project's store in the repository's main worktree (or, for a bare repository, a store inside the git
    /// common dir), so every worktree of one repository claims against one table.
    pub fn path_for(p: &Project) -> PathBuf {
        shared_runtime_dir(&p.root)
            .unwrap_or_else(|| p.runtime_dir())
            .join("claims.db")
    }
    pub fn open(p: &Project) -> Result<ClaimsStore> {
        if let Some(shared) = shared_runtime_dir(&p.root) {
            if !shared.exists() {
                std::fs::create_dir_all(&shared)?;
                // the store of a linked worktree lives in another checkout: keep it out of that tree's git status
                let _ = std::fs::write(shared.join(".gitignore"), "*\n");
            }
        }
        Self::open_at(&Self::path_for(p))
    }
    pub fn open_at(path: &Path) -> Result<ClaimsStore> {
        if let Some(d) = path.parent() {
            std::fs::create_dir_all(d)?;
        }
        let conn = Connection::open(path)?;
        conn.busy_timeout(BUSY_TIMEOUT)?;
        // WAL lets readers proceed while one claimant holds the write lock; switching modes needs a lock of its
        // own, so a transient busy result is retried and a persistent one leaves the (still correct) rollback journal.
        for _ in 0..20 {
            match conn.query_row("PRAGMA journal_mode=WAL", [], |r| r.get::<_, String>(0)) {
                Ok(_) => break,
                Err(_) => std::thread::sleep(Duration::from_millis(50)),
            }
        }
        let exists = |c: &Connection, t: &str| -> Result<bool> {
            Ok(c.query_row(
                "SELECT count(*) FROM sqlite_master WHERE type='table' AND name=?1",
                params![t],
                |r| r.get::<_, i64>(0),
            )? > 0)
        };
        if !exists(&conn, "claims")? || !exists(&conn, "claim_isolation")? {
            // create under the write lock so concurrent first opens serialise
            let tx = Transaction::new_unchecked(&conn, TransactionBehavior::Immediate)
                .map_err(|e| busy(e, "initialising the schema"))?;
            tx.execute_batch("CREATE TABLE IF NOT EXISTS claims (task_id TEXT PRIMARY KEY, session_id TEXT, role TEXT, claimed_at TEXT, expires_at TEXT);
                CREATE TABLE IF NOT EXISTS claim_isolation (task_id TEXT PRIMARY KEY, session_id TEXT, claimed_at TEXT, worktree TEXT, git_dir TEXT, branch TEXT, head TEXT, scope TEXT);")?;
            tx.commit()?;
        }
        Ok(ClaimsStore {
            conn,
            path: path.to_path_buf(),
        })
    }
    pub fn integrity_ok(&self) -> bool {
        self.conn
            .query_row("PRAGMA integrity_check", [], |r| r.get::<_, String>(0))
            .map(|s| s == "ok")
            .unwrap_or(false)
    }
    fn all_rows(conn: &Connection) -> Result<Vec<Value>> {
        let mut stmt = conn.prepare(&format!("{SELECT_CLAIMS} ORDER BY c.task_id"))?;
        let rows = stmt.query_map([], row_to_value)?;
        let mut out = vec![];
        for r in rows {
            out.push(r?);
        }
        Ok(out)
    }

    /// Legacy form: claim with an unknown isolation unit, an unrestricted scope and no budget (atomic).
    pub fn claim(
        &self,
        task_id: &str,
        session: &str,
        role: &str,
        lease_secs: Option<i64>,
    ) -> Result<Value> {
        let iso = Isolation::default();
        let scope = vec!["**".to_string()];
        self.claim_exclusive(&ClaimRequest {
            task_id,
            session,
            role,
            isolation: &iso,
            scope: &scope,
            lease_secs,
            max_parallel_sessions: None,
        })
    }

    /// **Grant a claim to exactly one session.** In one `BEGIN IMMEDIATE` transaction:
    /// 1. a live claim on the task held by another session → `TASK_CLAIMED`;
    /// 2. the same session holding it live from a different worktree → `CLAIM_WORKTREE_MISMATCH`;
    /// 3. a new session beyond `max_parallel_sessions` → `BUDGET_EXCEEDED` (the caller raises the gate);
    /// 4. a live claim of another session whose mutation scope may share a path with this one →
    ///    `CLAIM_SCOPE_CONFLICT`;
    /// 5. otherwise the row is written (a renewal keeps its original `claimed_at`) and the transaction commits.
    pub fn claim_exclusive(&self, req: &ClaimRequest) -> Result<Value> {
        let lease = req.lease_secs.unwrap_or(DEFAULT_LEASE_SECS);
        let tx = Transaction::new_unchecked(&self.conn, TransactionBehavior::Immediate)
            .map_err(|e| busy(e, &format!("claiming {}", req.task_id)))?;
        let now = now_epoch();
        let rows = Self::all_rows(&tx)?;
        let existing = rows.iter().find(|c| c["task_id"] == req.task_id).cloned();
        let mut renewal = false;
        let mut claimed_at = now_iso();
        if let Some(e) = &existing {
            let holder = e["session_id"].as_str().unwrap_or("");
            let live = is_live(e, now);
            if holder != req.session && live {
                return Err(GovError::new(
                    "TASK_CLAIMED",
                    format!(
                        "{} is claimed by session {holder} until {}",
                        req.task_id, e["expires_at"]
                    ),
                )
                .with_details(e.clone()));
            }
            if holder == req.session {
                let wt = e["worktree"].as_str().unwrap_or("");
                if live
                    && !wt.is_empty()
                    && !req.isolation.worktree.is_empty()
                    && wt != req.isolation.worktree
                {
                    return Err(GovError::new("CLAIM_WORKTREE_MISMATCH", format!("session {} already holds {} from worktree {wt}; a claim is bound to the working tree it was made from — release it there (`gov task release {}`) before claiming from {}", req.session, req.task_id, req.task_id, req.isolation.worktree)).with_details(e.clone()));
                }
                renewal = true;
                if live {
                    claimed_at = e["claimed_at"].as_str().unwrap_or(&claimed_at).to_string();
                }
            }
        }
        let live_rows: Vec<&Value> = rows.iter().filter(|c| is_live(c, now)).collect();
        if let Some(max) = req.max_parallel_sessions {
            let mut sessions: Vec<String> = live_rows
                .iter()
                .filter_map(|c| c["session_id"].as_str().map(|s| s.to_string()))
                .collect();
            sessions.sort();
            sessions.dedup();
            if !sessions.iter().any(|s| s == req.session) && sessions.len() >= max {
                return Err(GovError::new(
                    "BUDGET_EXCEEDED",
                    format!(
                        "max_parallel_agents ({max}) reached: {} active session(s)",
                        sessions.len()
                    ),
                )
                .with_details(json!({"active_sessions": sessions})));
            }
        }
        let conflicts: Vec<Value> = live_rows
            .iter()
            .filter(|c| c["task_id"] != req.task_id && c["session_id"].as_str() != Some(req.session))
            .filter(|c| {
                crate::orchestration::claims::scopes_overlap(
                    req.scope,
                    &crate::orchestration::claims::scope_of_claim(c),
                )
            })
            .map(|c| json!({"task_id": c["task_id"], "session_id": c["session_id"], "scope": crate::orchestration::claims::scope_of_claim(c), "worktree": c["worktree"], "expires_at": c["expires_at"]}))
            .collect();
        if !conflicts.is_empty() {
            let desc: Vec<String> = conflicts
                .iter()
                .map(|c| {
                    format!(
                        "{} (session {}, scope {})",
                        c["task_id"].as_str().unwrap_or("?"),
                        c["session_id"].as_str().unwrap_or("?"),
                        crate::orchestration::claims::describe_scope(
                            &crate::orchestration::claims::scope_of_claim(c)
                        )
                    )
                })
                .collect();
            return Err(GovError::new("CLAIM_SCOPE_CONFLICT", format!("{}: its mutation scope {} overlaps live claim(s) of other sessions: {}; parallel work is permitted only on disjoint mutation scopes — wait for them to close or release, or narrow the task's allowed_paths", req.task_id, crate::orchestration::claims::describe_scope(req.scope), desc.join("; "))).with_details(json!({"task_id": req.task_id, "requested_scope": req.scope, "conflicts": conflicts})));
        }
        let expires_at = to_iso(now + lease);
        let scope_text = serde_json::to_string(req.scope)?;
        tx.execute(
            "INSERT OR REPLACE INTO claims(task_id, session_id, role, claimed_at, expires_at) VALUES (?1,?2,?3,?4,?5)",
            params![req.task_id, req.session, req.role, claimed_at, expires_at],
        )?;
        tx.execute(
            "INSERT OR REPLACE INTO claim_isolation(task_id, session_id, claimed_at, worktree, git_dir, branch, head, scope) VALUES (?1,?2,?3,?4,?5,?6,?7,?8)",
            params![
                req.task_id,
                req.session,
                claimed_at,
                req.isolation.worktree,
                req.isolation.git_dir,
                req.isolation.branch,
                req.isolation.head,
                scope_text
            ],
        )?;
        tx.commit().map_err(|e| busy(e, "committing the claim"))?;
        Ok(
            json!({"task_id": req.task_id, "session_id": req.session, "role": req.role, "claimed_at": claimed_at,
            "expires_at": expires_at, "renewed": renewal, "worktree": req.isolation.worktree, "git_dir": req.isolation.git_dir,
            "branch": req.isolation.branch, "head": req.isolation.head, "scope": req.scope, "store": self.path.display().to_string()}),
        )
    }
    pub fn get(&self, task_id: &str) -> Result<Option<Value>> {
        Ok(self
            .conn
            .query_row(
                &format!("{SELECT_CLAIMS} WHERE c.task_id=?1"),
                params![task_id],
                row_to_value,
            )
            .optional()?)
    }
    pub fn holder(&self, task_id: &str) -> Result<Option<Value>> {
        Ok(self.get(task_id)?.filter(|c| is_live(c, now_epoch())))
    }
    pub fn release(&self, task_id: &str, session: &str, force: bool) -> Result<bool> {
        Ok(self.release_row(task_id, session, force)?.is_some())
    }
    /// Release atomically: the row read and the row deleted are the same row (a claim re-granted to another session
    /// between a stale read and the delete can no longer be deleted by the previous holder).
    pub fn release_row(&self, task_id: &str, session: &str, force: bool) -> Result<Option<Value>> {
        let tx = Transaction::new_unchecked(&self.conn, TransactionBehavior::Immediate)
            .map_err(|e| busy(e, &format!("releasing {task_id}")))?;
        let existing = tx
            .query_row(
                &format!("{SELECT_CLAIMS} WHERE c.task_id=?1"),
                params![task_id],
                row_to_value,
            )
            .optional()?;
        let Some(existing) = existing else {
            return Ok(None);
        };
        let holder = existing["session_id"].as_str().unwrap_or("").to_string();
        if holder != session && !force {
            return Err(GovError::new("TASK_CLAIMED", format!("{task_id} is held by {holder}; releasing another session's claim requires --force (L3+)")));
        }
        tx.execute(
            "DELETE FROM claims WHERE task_id=?1 AND session_id IS ?2 AND claimed_at IS ?3",
            params![task_id, holder, existing["claimed_at"].as_str()],
        )?;
        tx.execute(
            "DELETE FROM claim_isolation WHERE task_id=?1",
            params![task_id],
        )?;
        tx.commit()?;
        Ok(Some(existing))
    }
    pub fn list(&self) -> Result<Vec<Value>> {
        let now = now_epoch();
        let mut out = Self::all_rows(&self.conn)?;
        for c in out.iter_mut() {
            c["expired"] = json!(!is_live(c, now));
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
    /// Delete only the rows that are expired at sweep time, in one transaction (a claim renewed or re-granted
    /// concurrently is never swept).
    pub fn sweep_expired(&self) -> Result<usize> {
        let tx = Transaction::new_unchecked(&self.conn, TransactionBehavior::Immediate)
            .map_err(|e| busy(e, "sweeping expired claims"))?;
        let now = now_epoch();
        let expired: Vec<Value> = Self::all_rows(&tx)?
            .into_iter()
            .filter(|c| !is_live(c, now))
            .collect();
        let mut n = 0;
        for c in &expired {
            let d = tx.execute(
                "DELETE FROM claims WHERE task_id=?1 AND expires_at IS ?2",
                params![c["task_id"].as_str(), c["expires_at"].as_str()],
            )?;
            if d > 0 {
                tx.execute(
                    "DELETE FROM claim_isolation WHERE task_id=?1",
                    params![c["task_id"].as_str()],
                )?;
            }
            n += d;
        }
        tx.commit()?;
        Ok(n)
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

/// For a project inside a **linked** git worktree, the runtime directory the repository's worktrees share: the same
/// project path in the main worktree, or a directory inside the git common dir when the repository is bare. `None`
/// for the main worktree, a plain checkout, a submodule or a project outside git — they use their own runtime dir.
/// Pure filesystem reads (no git subprocess): a linked worktree's `.git` is a file `gitdir: <dir>` whose `commondir`
/// names the shared git dir.
pub fn shared_runtime_dir(root: &Path) -> Option<PathBuf> {
    let mut top = root.to_path_buf();
    let dotgit = loop {
        let g = top.join(".git");
        if g.is_dir() {
            return None;
        }
        if g.is_file() {
            break g;
        }
        if !top.pop() {
            return None;
        }
    };
    let text = std::fs::read_to_string(&dotgit).ok()?;
    let gitdir = text.lines().find_map(|l| l.strip_prefix("gitdir:"))?.trim();
    let gitdir = if Path::new(gitdir).is_absolute() {
        PathBuf::from(gitdir)
    } else {
        top.join(gitdir)
    };
    let common = std::fs::read_to_string(gitdir.join("commondir")).ok()?;
    let common = common.trim();
    let common = if Path::new(common).is_absolute() {
        PathBuf::from(common)
    } else {
        gitdir.join(common)
    };
    let common = common.canonicalize().ok()?;
    let rel = root.strip_prefix(&top).ok()?.to_path_buf();
    if common.file_name().map(|n| n == ".git").unwrap_or(false) {
        let main = common.parent()?.to_path_buf();
        Some(main.join(rel).join(crate::RUNTIME_DIR))
    } else {
        Some(common.join("governance-runtime").join(rel))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::{Arc, Barrier};

    fn tmp(name: &str) -> PathBuf {
        let d =
            std::env::temp_dir().join(format!("gov-claims-{name}-{}", crate::util::short_uuid()));
        std::fs::create_dir_all(&d).unwrap();
        d
    }
    fn req<'a>(
        task: &'a str,
        session: &'a str,
        iso: &'a Isolation,
        scope: &'a [String],
    ) -> ClaimRequest<'a> {
        ClaimRequest {
            task_id: task,
            session,
            role: "backend-engineer",
            isolation: iso,
            scope,
            lease_secs: None,
            max_parallel_sessions: Some(8),
        }
    }
    fn iso(w: &str) -> Isolation {
        Isolation {
            worktree: w.into(),
            ..Default::default()
        }
    }

    /// Many connections (each with its own locks, like separate processes) race for one task: exactly one wins,
    /// every other attempt is told TASK_CLAIMED, and the store holds the winner.
    #[test]
    fn concurrent_claims_of_one_task_grant_exactly_one() {
        let dir = tmp("race");
        let path = dir.join("claims.db");
        ClaimsStore::open_at(&path).unwrap();
        for trial in 0..10 {
            let task = format!("TASK-R{trial}");
            let n = 6;
            let barrier = Arc::new(Barrier::new(n));
            let handles: Vec<_> = (0..n)
                .map(|i| {
                    let (path, task, barrier) = (path.clone(), task.clone(), barrier.clone());
                    std::thread::spawn(move || {
                        let store = ClaimsStore::open_at(&path).unwrap();
                        let scope = vec!["**".to_string()];
                        let is = iso("/w");
                        let session = format!("S-{i}");
                        barrier.wait();
                        store
                            .claim_exclusive(&req(&task, &session, &is, &scope))
                            .map(|_| session)
                            .map_err(|e| e.code)
                    })
                })
                .collect();
            let results: Vec<_> = handles.into_iter().map(|h| h.join().unwrap()).collect();
            let winners: Vec<&String> = results.iter().filter_map(|r| r.as_ref().ok()).collect();
            assert_eq!(winners.len(), 1, "trial {trial}: {results:?}");
            assert!(
                results
                    .iter()
                    .filter_map(|r| r.as_ref().err())
                    .all(|c| c == "TASK_CLAIMED"),
                "{results:?}"
            );
            let store = ClaimsStore::open_at(&path).unwrap();
            assert_eq!(
                store.get(&task).unwrap().unwrap()["session_id"],
                json!(winners[0])
            );
            store.release(&task, winners[0], false).unwrap();
        }
        let _ = std::fs::remove_dir_all(&dir);
    }

    /// Child half of [`concurrent_processes_claiming_one_task_grant_exactly_one`]: a no-op unless launched by it.
    #[test]
    fn claims_child_process() {
        let Ok(db) = std::env::var("GOV_CLAIMS_CHILD_DB") else {
            return;
        };
        let task = std::env::var("GOV_CLAIMS_CHILD_TASK").unwrap();
        let session = std::env::var("GOV_CLAIMS_CHILD_SESSION").unwrap();
        let start: i64 = std::env::var("GOV_CLAIMS_CHILD_START")
            .unwrap()
            .parse()
            .unwrap();
        let store = ClaimsStore::open_at(Path::new(&db)).unwrap();
        let wait = start - chrono::Utc::now().timestamp_millis();
        if wait > 0 {
            std::thread::sleep(Duration::from_millis(wait as u64));
        }
        let scope = vec!["**".to_string()];
        let is = iso("/w");
        let r = store.claim_exclusive(&req(&task, &session, &is, &scope));
        println!(
            "CLAIM-RESULT {}",
            r.map(|_| "OK".to_string()).unwrap_or_else(|e| e.code)
        );
    }

    /// Real OS processes (this test binary re-executed) race for one task on one store: exactly one is granted.
    #[test]
    fn concurrent_processes_claiming_one_task_grant_exactly_one() {
        if std::env::var("GOV_CLAIMS_CHILD_DB").is_ok() {
            return;
        }
        let dir = tmp("procs");
        let db = dir.join("claims.db");
        ClaimsStore::open_at(&db).unwrap();
        let exe = std::env::current_exe().unwrap();
        for trial in 0..5 {
            let start = chrono::Utc::now().timestamp_millis() + 1500;
            let kids: Vec<_> = (0..5)
                .map(|k| {
                    std::process::Command::new(&exe)
                        .args([
                            "--exact",
                            "memory::claims::tests::claims_child_process",
                            "--nocapture",
                            "--test-threads",
                            "1",
                        ])
                        .env("GOV_CLAIMS_CHILD_DB", &db)
                        .env("GOV_CLAIMS_CHILD_TASK", format!("TASK-P{trial}"))
                        .env("GOV_CLAIMS_CHILD_SESSION", format!("S-{trial}-{k}"))
                        .env("GOV_CLAIMS_CHILD_START", start.to_string())
                        .stdout(std::process::Stdio::piped())
                        .stderr(std::process::Stdio::null())
                        .spawn()
                        .unwrap()
                })
                .collect();
            let results: Vec<String> = kids
                .into_iter()
                .map(|c| {
                    let out =
                        String::from_utf8_lossy(&c.wait_with_output().unwrap().stdout).to_string();
                    out.split("CLAIM-RESULT ")
                        .nth(1)
                        .and_then(|rest| rest.split_whitespace().next())
                        .map(|s| s.to_string())
                        .unwrap_or_else(|| format!("NO-RESULT: {out}"))
                })
                .collect();
            assert_eq!(
                results.iter().filter(|r| *r == "OK").count(),
                1,
                "trial {trial}: {results:?}"
            );
            assert!(
                results.iter().all(|r| r == "OK" || r == "TASK_CLAIMED"),
                "trial {trial}: {results:?}"
            );
            let store = ClaimsStore::open_at(&db).unwrap();
            let task = format!("TASK-P{trial}");
            let winner = store.get(&task).unwrap().unwrap()["session_id"]
                .as_str()
                .unwrap()
                .to_string();
            store.release(&task, &winner, false).unwrap();
        }
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn overlapping_scopes_of_other_sessions_are_refused_and_disjoint_ones_granted() {
        let dir = tmp("scope");
        let s = ClaimsStore::open_at(&dir.join("claims.db")).unwrap();
        let w = iso("/w");
        let src = vec!["src/**".to_string()];
        let docs = vec!["docs/**".to_string()];
        let lib = vec!["src/lib.rs".to_string()];
        let all = vec!["**".to_string()];
        s.claim_exclusive(&req("T1", "S-a", &w, &src)).unwrap();
        let e = s.claim_exclusive(&req("T2", "S-b", &w, &lib)).unwrap_err();
        assert_eq!(e.code, "CLAIM_SCOPE_CONFLICT");
        assert_eq!(e.details["conflicts"][0]["task_id"], "T1");
        s.claim_exclusive(&req("T3", "S-b", &w, &docs)).unwrap();
        assert_eq!(
            s.claim_exclusive(&req("T4", "S-c", &w, &all))
                .unwrap_err()
                .code,
            "CLAIM_SCOPE_CONFLICT"
        );
        // the same session may hold overlapping claims (one agent works sequentially)
        s.claim_exclusive(&req("T5", "S-a", &w, &lib)).unwrap();
        // an expired claim no longer constrains anyone
        s.insert_raw(
            "T6",
            "S-dead",
            "x",
            "2020-01-01T00:00:00Z",
            "2020-01-01T01:00:00Z",
        )
        .unwrap();
        s.release("T1", "S-a", false).unwrap();
        s.release("T5", "S-a", false).unwrap();
        s.claim_exclusive(&req("T7", "S-c", &w, &src)).unwrap();
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn budget_is_decided_in_the_same_transaction() {
        let dir = tmp("budget");
        let s = ClaimsStore::open_at(&dir.join("claims.db")).unwrap();
        let w = iso("/w");
        let a = vec!["a/**".to_string()];
        let b = vec!["b/**".to_string()];
        let mut r = req("T1", "S-a", &w, &a);
        r.max_parallel_sessions = Some(1);
        s.claim_exclusive(&r).unwrap();
        let mut r2 = req("T2", "S-b", &w, &b);
        r2.max_parallel_sessions = Some(1);
        let e = s.claim_exclusive(&r2).unwrap_err();
        assert_eq!(e.code, "BUDGET_EXCEEDED");
        assert_eq!(e.details["active_sessions"], json!(["S-a"]));
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn a_claim_is_bound_to_its_worktree_and_renewal_keeps_claimed_at() {
        let dir = tmp("wt");
        let s = ClaimsStore::open_at(&dir.join("claims.db")).unwrap();
        let (w1, w2) = (iso("/w1"), iso("/w2"));
        let sc = vec!["src/**".to_string()];
        let first = s.claim_exclusive(&req("T1", "S-a", &w1, &sc)).unwrap();
        assert_eq!(first["renewed"], false);
        assert_eq!(s.get("T1").unwrap().unwrap()["worktree"], "/w1");
        assert_eq!(
            s.claim_exclusive(&req("T1", "S-a", &w2, &sc))
                .unwrap_err()
                .code,
            "CLAIM_WORKTREE_MISMATCH"
        );
        let again = s.claim_exclusive(&req("T1", "S-a", &w1, &sc)).unwrap();
        assert_eq!(again["renewed"], true);
        assert_eq!(again["claimed_at"], first["claimed_at"]);
        assert_eq!(
            s.claim_exclusive(&req("T1", "S-b", &w2, &sc))
                .unwrap_err()
                .code,
            "TASK_CLAIMED"
        );
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn release_and_sweep_only_touch_the_rows_they_decided_on() {
        let dir = tmp("rel");
        let s = ClaimsStore::open_at(&dir.join("claims.db")).unwrap();
        let w = iso("/w");
        let sc = vec!["x/**".to_string()];
        s.claim_exclusive(&req("T1", "S-a", &w, &sc)).unwrap();
        assert_eq!(
            s.release_row("T1", "S-b", false).unwrap_err().code,
            "TASK_CLAIMED"
        );
        assert_eq!(
            s.release_row("T1", "S-b", true).unwrap().unwrap()["session_id"],
            "S-a"
        );
        assert!(s.get("T1").unwrap().is_none());
        s.insert_raw(
            "T2",
            "S-dead",
            "x",
            "2020-01-01T00:00:00Z",
            "2020-01-01T01:00:00Z",
        )
        .unwrap();
        s.claim_exclusive(&req("T3", "S-a", &w, &sc)).unwrap();
        assert_eq!(s.sweep_expired().unwrap(), 1);
        assert!(s.get("T3").unwrap().is_some());
        let _ = std::fs::remove_dir_all(&dir);
    }

    /// A database written by the previous schema gains the isolation table; old rows (and rows any other writer
    /// inserts positionally into the unchanged five-column `claims` table) read as an unrestricted scope with an
    /// unknown worktree.
    #[test]
    fn legacy_store_is_migrated() {
        let dir = tmp("legacy");
        let path = dir.join("claims.db");
        {
            let c = Connection::open(&path).unwrap();
            c.execute_batch("CREATE TABLE claims (task_id TEXT PRIMARY KEY, session_id TEXT, role TEXT, claimed_at TEXT, expires_at TEXT); INSERT INTO claims VALUES ('T0','S-old','r','2020-01-01T00:00:00Z','2999-01-01T00:00:00Z');").unwrap();
        }
        let s = ClaimsStore::open_at(&path).unwrap();
        let row = s.get("T0").unwrap().unwrap();
        assert_eq!(row["scope"], Value::Null);
        assert_eq!(
            crate::orchestration::claims::scope_of_claim(&row),
            vec!["**".to_string()]
        );
        let w = iso("/w");
        let sc = vec!["a/**".to_string()];
        assert_eq!(
            s.claim_exclusive(&req("T1", "S-new", &w, &sc))
                .unwrap_err()
                .code,
            "CLAIM_SCOPE_CONFLICT"
        );
        // the five-column layout still accepts positional writers; an isolation record never leaks onto a claim
        // instance it was not written for
        s.conn
            .execute("DELETE FROM claims WHERE task_id='T0'", [])
            .unwrap();
        s.claim_exclusive(&req("T2", "S-a", &w, &sc)).unwrap();
        assert_eq!(s.get("T2").unwrap().unwrap()["worktree"], "/w");
        s.conn
            .execute("INSERT OR REPLACE INTO claims VALUES ('T2','S-ghost','r','2026-01-01T00:00:00Z','2999-01-01T00:00:00Z')", [])
            .unwrap();
        let ghost = s.get("T2").unwrap().unwrap();
        assert_eq!(ghost["session_id"], "S-ghost");
        assert_eq!(ghost["worktree"], Value::Null);
        assert_eq!(ghost["scope"], Value::Null);
        let _ = std::fs::remove_dir_all(&dir);
    }

    /// Linked worktrees resolve to the main worktree's store; the main worktree and plain directories keep their own.
    #[test]
    fn linked_worktrees_share_the_main_worktree_store() {
        let d = tmp("git");
        let main = d.join("main");
        std::fs::create_dir_all(main.join(".git/worktrees/wt2")).unwrap();
        std::fs::write(main.join(".git/worktrees/wt2/commondir"), "../..\n").unwrap();
        let wt2 = d.join("wt2");
        std::fs::create_dir_all(wt2.join("proj")).unwrap();
        std::fs::write(
            wt2.join(".git"),
            format!("gitdir: {}\n", main.join(".git/worktrees/wt2").display()),
        )
        .unwrap();
        assert_eq!(shared_runtime_dir(&main), None);
        let main_c = main.canonicalize().unwrap();
        assert_eq!(
            shared_runtime_dir(&wt2),
            Some(main_c.join(crate::RUNTIME_DIR))
        );
        assert_eq!(
            shared_runtime_dir(&wt2.join("proj")),
            Some(main_c.join("proj").join(crate::RUNTIME_DIR))
        );
        assert_eq!(shared_runtime_dir(&d.join("nowhere")), None);
        let _ = std::fs::remove_dir_all(&d);
    }
}
