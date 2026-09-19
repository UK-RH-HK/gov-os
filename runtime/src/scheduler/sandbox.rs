//! Disposable copies of a project for checks that write state (Contract v3:804 "isolated worktrees/processes where
//! required"). A sandbox is a byte copy of every repository file the suite reads (the same universe as
//! [`crate::paths::iter_repo_files`]) plus, on request, the derived runtime stores; it lives under the project's
//! runtime directory (never inside the governed tree) and is removed when dropped.
use crate::{Project, Result};
use std::path::{Path, PathBuf};

/// Environment variable set for every process started inside a sandbox. Nested sandboxes are not created from
/// inside one (a scenario that runs the suite does not re-run scenarios).
pub const SANDBOX_ENV: &str = "GOV_HEALTH_SANDBOX";

pub fn inside_sandbox() -> bool {
    std::env::var(SANDBOX_ENV)
        .map(|v| !v.is_empty() && v != "0")
        .unwrap_or(false)
}

/// Copy `src` to `dst` unless `src` is gone. Checks run concurrently: a file listed a moment ago may be removed before
/// it is copied (SQLite drops `-wal`/`-shm` when the last connection closes; an atomic writer renames its temporary
/// file). A file that no longer exists is not part of the state being isolated, so it is skipped instead of failing the
/// check that asked for the sandbox; every other I/O error is returned.
fn copy_if_present(src: &Path, dst: &Path) -> Result<()> {
    match std::fs::copy(src, dst) {
        Ok(_) => Ok(()),
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => Ok(()),
        Err(e) => Err(e.into()),
    }
}

#[derive(Debug, Clone, Copy, Default)]
pub struct SandboxOptions {
    /// Copy the derived runtime stores (`state.db`, its WAL, `claims.db`).
    pub runtime: bool,
    /// Initialise a fresh Git repository with the copied tree committed (for scenarios that observe mutations).
    pub git: bool,
}

pub struct Sandbox {
    pub root: PathBuf,
    pub live_root: PathBuf,
}

impl Sandbox {
    pub fn create(p: &Project, purpose: &str, opts: SandboxOptions) -> Result<Sandbox> {
        let base = p.runtime_dir().join("health").join("sandboxes");
        std::fs::create_dir_all(&base)?;
        let safe: String = purpose
            .chars()
            .map(|c| {
                if c.is_ascii_alphanumeric() || c == '-' {
                    c
                } else {
                    '-'
                }
            })
            .collect();
        let root = base.join(format!("{safe}-{}", crate::util::short_uuid()));
        std::fs::create_dir_all(&root)?;
        let sb = Sandbox {
            root: root.clone(),
            live_root: p.root.clone(),
        };
        for (abs, rel) in crate::paths::iter_repo_files(&p.root, false) {
            let dst = root.join(&rel);
            if let Some(d) = dst.parent() {
                std::fs::create_dir_all(d)?;
            }
            copy_if_present(&abs, &dst)?;
        }
        if opts.runtime {
            let rt = root.join(crate::RUNTIME_DIR);
            std::fs::create_dir_all(&rt)?;
            for name in [
                "state.db",
                "state.db-wal",
                "state.db-shm",
                "claims.db",
                "claims.db-wal",
                "claims.db-shm",
            ] {
                copy_if_present(&p.runtime_dir().join(name), &rt.join(name))?;
            }
        }
        if opts.git {
            let git = |args: &[&str]| {
                std::process::Command::new("git")
                    .args(args)
                    .current_dir(&root)
                    .env("GIT_AUTHOR_NAME", "gov-health")
                    .env("GIT_AUTHOR_EMAIL", "gov-health@localhost")
                    .env("GIT_COMMITTER_NAME", "gov-health")
                    .env("GIT_COMMITTER_EMAIL", "gov-health@localhost")
                    .output()
            };
            let _ = git(&["init", "-q"]);
            let _ = git(&["add", "-A"]);
            let _ = git(&[
                "commit",
                "-q",
                "--no-verify",
                "-m",
                "health sandbox baseline",
            ]);
        }
        Ok(sb)
    }

    /// Open the sandbox as a project with the caller's session and role.
    pub fn project(&self, like: &Project) -> Project {
        Project::open(&self.root)
            .with_session(Some(like.session_id.clone()), Some(like.role.clone()))
    }

    /// Replace the sandbox root with the live root in a result, so a result never names a disposable path.
    pub fn relocate(&self, v: &serde_json::Value) -> serde_json::Value {
        relocate_paths(v, &self.root, &self.live_root)
    }
}

impl Drop for Sandbox {
    fn drop(&mut self) {
        let _ = std::fs::remove_dir_all(&self.root);
    }
}

pub fn relocate_paths(v: &serde_json::Value, from: &Path, to: &Path) -> serde_json::Value {
    let (f, t) = (
        from.to_string_lossy().to_string(),
        to.to_string_lossy().to_string(),
    );
    match serde_json::to_string(v) {
        Ok(s) => serde_json::from_str(&s.replace(&f, &t)).unwrap_or_else(|_| v.clone()),
        Err(_) => v.clone(),
    }
}
