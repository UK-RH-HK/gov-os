//! Session claims with leases (concurrency/session claim governance test family). Backed by the claims store,
//! which is separate from the rebuild-deleted derived index (framework §11.1 deterministic memory).
//!
//! **What a claim is** (Contract v3:388-392, BC-P2-15). A claim grants one task to exactly one session. It records
//! the session's *unit of isolation* — the working tree the session mutates (canonical root, git dir, branch, HEAD)
//! — and the task's *mutation scope* (its `allowed_paths`; a task that declares none may mutate anything, so its
//! scope is the whole repository, `**`). The grant is decided inside one `BEGIN IMMEDIATE` transaction of the
//! claims store ([`ClaimsStore::claim_exclusive`]), so concurrent processes serialise: at most one session is ever
//! told it holds a task, and a claim whose mutation scope overlaps a live claim of another session is refused
//! (`CLAIM_SCOPE_CONFLICT`) — parallel work proceeds only where the mutation scopes are provably disjoint.
use crate::memory::claims::{ClaimRequest, ClaimsStore, Isolation};
use crate::records::Record;
use crate::util::glob_match;
use crate::{Project, Result};
use serde_json::Value;

/// The universal mutation scope: a task without `allowed_paths` may mutate any path.
pub const UNRESTRICTED: &str = "**";

/// Legacy entry point (kept for API stability): claim `task_id` for `session`, deriving the isolation unit from the
/// project and the mutation scope from the task record. No parallelism budget is applied here; the governed path is
/// [`crate::orchestration::tasks::claim`].
pub fn claim(
    p: &Project,
    task_id: &str,
    session: &str,
    role: &str,
    lease_secs: Option<i64>,
) -> Result<Value> {
    let store = crate::records::RecordStore::load(&p.root);
    let scope = store
        .get(task_id)
        .map(scope_of_task)
        .unwrap_or_else(|| vec![UNRESTRICTED.to_string()]);
    let iso = isolation(p);
    claim_with(
        p,
        &ClaimRequest {
            task_id,
            session,
            role,
            isolation: &iso,
            scope: &scope,
            lease_secs,
            max_parallel_sessions: None,
        },
    )
}
/// Atomic claim with every constraint decided in one transaction (see [`ClaimsStore::claim_exclusive`]).
pub fn claim_with(p: &Project, req: &ClaimRequest) -> Result<Value> {
    ClaimsStore::open(p)?.claim_exclusive(req)
}
pub fn release(p: &Project, task_id: &str, session: &str, force: bool) -> Result<bool> {
    ClaimsStore::open(p)?.release(task_id, session, force)
}
/// Release and return the row that was released (None when there was no claim).
pub fn release_row(
    p: &Project,
    task_id: &str,
    session: &str,
    force: bool,
) -> Result<Option<Value>> {
    ClaimsStore::open(p)?.release_row(task_id, session, force)
}
/// The live (unexpired) claim on a task, if any.
pub fn holder(p: &Project, task_id: &str) -> Result<Option<Value>> {
    ClaimsStore::open(p)?.holder(task_id)
}
/// The claim row on a task whether or not its lease has expired.
pub fn get(p: &Project, task_id: &str) -> Result<Option<Value>> {
    ClaimsStore::open(p)?.get(task_id)
}
pub fn list(p: &Project) -> Result<Vec<Value>> {
    ClaimsStore::open(p)?.list()
}
/// Unexpired claims only.
pub fn live(p: &Project) -> Result<Vec<Value>> {
    Ok(list(p)?
        .into_iter()
        .filter(|c| !c["expired"].as_bool().unwrap_or(true))
        .collect())
}
pub fn sweep_expired(p: &Project) -> Result<usize> {
    ClaimsStore::open(p)?.sweep_expired()
}
pub fn active_sessions(p: &Project) -> Result<Vec<String>> {
    ClaimsStore::open(p)?.active_sessions()
}

/// The unit of isolation this process mutates: the canonical project root (one per git worktree), the worktree's
/// own git dir, its branch and HEAD. Without git the root alone identifies the working tree.
pub fn isolation(p: &Project) -> Isolation {
    let (c, gd, _) = p.git(&["rev-parse", "--absolute-git-dir"]);
    let git_dir = if c == 0 { gd } else { String::new() };
    let (branch, head) = if git_dir.is_empty() {
        (String::new(), String::new())
    } else {
        (p.git_branch(), p.git_commit())
    };
    Isolation {
        worktree: worktree_id(p),
        git_dir,
        branch,
        head,
    }
}
/// The identity of the working tree a claim was made from and must be closed in.
pub fn worktree_id(p: &Project) -> String {
    p.root.display().to_string()
}

/// A task's mutation scope: its `allowed_paths`, or the whole repository when it declares none.
pub fn scope_of_task(t: &Record) -> Vec<String> {
    let allowed: Vec<String> = t
        .list("allowed_paths")
        .into_iter()
        .map(|s| s.trim().to_string())
        .filter(|s| !s.is_empty())
        .collect();
    if allowed.is_empty() {
        vec![UNRESTRICTED.to_string()]
    } else {
        allowed
    }
}
/// The scope recorded on a claim row; a row without one (written by an older store) is treated as unrestricted.
pub fn scope_of_claim(c: &Value) -> Vec<String> {
    let v: Vec<String> = c["scope"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default();
    if v.is_empty() {
        vec![UNRESTRICTED.to_string()]
    } else {
        v
    }
}
/// Human-readable scope: `unrestricted (no allowed_paths)` or the pattern list.
pub fn describe_scope(scope: &[String]) -> String {
    if scope.iter().any(|s| s == UNRESTRICTED) {
        "unrestricted (the task declares no allowed_paths)".into()
    } else {
        format!("{scope:?}")
    }
}
/// Does `path` fall inside `scope`?
pub fn path_in_scope(scope: &[String], path: &str) -> bool {
    scope
        .iter()
        .any(|pat| pat == UNRESTRICTED || glob_match(pat, path))
}

/// **May two mutation scopes share a path?** Sound (never answers `false` for scopes that can both match one path)
/// and deliberately conservative: when it cannot prove two patterns disjoint it answers `true`, so the cost of
/// imprecision is serialisation, never a double grant of the same path.
pub fn scopes_overlap(a: &[String], b: &[String]) -> bool {
    a.iter()
        .any(|x| b.iter().any(|y| patterns_may_overlap(x, y)))
}

/// Pattern-level overlap under [`crate::util::glob_match`] semantics: `*` and `?` stay inside one path segment,
/// `**` spans segments, a trailing `/` means "everything below", and a pattern without `/` also matches that
/// basename in any directory.
pub fn patterns_may_overlap(a: &str, b: &str) -> bool {
    let alts = |p: &str| -> Vec<String> {
        let p = p.trim();
        let p = p.strip_prefix("./").unwrap_or(p);
        let mut base = p.to_string();
        if base.ends_with('/') {
            base.push_str("**");
        }
        let mut v = vec![base.clone()];
        if !p.trim_end_matches('/').contains('/') {
            v.push(format!("**/{base}"));
        }
        v
    };
    alts(a).iter().any(|x| {
        alts(b)
            .iter()
            .any(|y| segs_overlap(&split(x), &split(y), 0))
    })
}

fn split(p: &str) -> Vec<&str> {
    p.split('/').filter(|s| !s.is_empty()).collect()
}
fn has_wild(s: &str) -> bool {
    s.contains('*') || s.contains('?')
}
/// Segment-wise intersection test. A whole-segment `**` matches zero or more segments; a `**` embedded in a
/// segment (e.g. `src**`) can cross `/`, so it is decided conservatively (overlap).
fn segs_overlap(a: &[&str], b: &[&str], depth: usize) -> bool {
    if depth > 64 {
        return true;
    }
    match (a.first(), b.first()) {
        (None, None) => true,
        (Some(&"**"), _) => {
            segs_overlap(&a[1..], b, depth + 1)
                || (!b.is_empty() && segs_overlap(a, &b[1..], depth + 1))
        }
        (_, Some(&"**")) => {
            segs_overlap(a, &b[1..], depth + 1)
                || (!a.is_empty() && segs_overlap(&a[1..], b, depth + 1))
        }
        (None, Some(_)) | (Some(_), None) => false,
        (Some(x), Some(y)) => {
            if x.contains("**") || y.contains("**") {
                return true;
            }
            seg_compatible(x, y) && segs_overlap(&a[1..], &b[1..], depth + 1)
        }
    }
}
/// Can one path segment match both single-segment patterns `x` and `y`?
fn seg_compatible(x: &str, y: &str) -> bool {
    match (has_wild(x), has_wild(y)) {
        (false, false) => x == y,
        (true, false) => crate::util::glob_to_regex(x).is_match(y),
        (false, true) => crate::util::glob_to_regex(y).is_match(x),
        (true, true) => {
            // literal prefix / suffix up to the first / after the last wildcard must be compatible
            let pre = |s: &str| s[..s.find(['*', '?']).unwrap_or(s.len())].to_string();
            let suf = |s: &str| s[s.rfind(['*', '?']).map(|i| i + 1).unwrap_or(0)..].to_string();
            let (px, py, sx, sy) = (pre(x), pre(y), suf(x), suf(y));
            (px.starts_with(&py) || py.starts_with(&px)) && (sx.ends_with(&sy) || sy.ends_with(&sx))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn s(v: &[&str]) -> Vec<String> {
        v.iter().map(|x| x.to_string()).collect()
    }

    #[test]
    fn disjoint_directories_do_not_overlap() {
        assert!(!scopes_overlap(&s(&["src/a/**"]), &s(&["src/b/**"])));
        assert!(!scopes_overlap(&s(&["src/**"]), &s(&["docs/**"])));
        assert!(!scopes_overlap(
            &s(&["src/**", "tests/**"]),
            &s(&["spec/**", "docs/*.md"])
        ));
        assert!(!patterns_may_overlap("src/lib.rs", "src/main.rs"));
        assert!(!patterns_may_overlap("docs/*.md", "docs/*.txt"));
        assert!(!patterns_may_overlap("a/*/c", "a/b/d"));
    }

    #[test]
    fn nested_equal_and_wildcard_scopes_overlap() {
        assert!(scopes_overlap(&s(&["src/**"]), &s(&["src/**"])));
        assert!(scopes_overlap(&s(&["src/**"]), &s(&["src/lib.rs"])));
        assert!(scopes_overlap(&s(&["src/**"]), &s(&["src/extra/m2.rs"])));
        assert!(scopes_overlap(&s(&["**"]), &s(&["docs/x.md"])));
        assert!(scopes_overlap(&s(&["src/**"]), &s(&["**/*.rs"])));
        // a pattern without `/` matches that basename anywhere
        assert!(patterns_may_overlap("README.md", "docs/**"));
        assert!(patterns_may_overlap("*.rs", "src/**"));
        assert!(patterns_may_overlap("src/", "src/x/y.rs"));
        assert!(patterns_may_overlap("src/*.rs", "src/lib.rs"));
        assert!(patterns_may_overlap("src/a*", "src/ab*"));
        // embedded `**` crosses segments: decided conservatively
        assert!(patterns_may_overlap("src**", "src/x/y"));
    }

    /// Soundness against the matcher itself: whenever one concrete path matches both patterns, the overlap test
    /// must say so.
    #[test]
    fn overlap_is_sound_against_glob_match() {
        let pats = [
            "src/**",
            "src/a/**",
            "src/*.rs",
            "*.rs",
            "docs/*.md",
            "**/*.md",
            "README.md",
            "src/lib.rs",
            "tests/",
            "**",
            "a/*/c",
            "a/b/*",
            "spec/**",
            "src/**/mod.rs",
            "**/x/**",
        ];
        let paths = [
            "src/lib.rs",
            "src/a/b.rs",
            "src/a/x/mod.rs",
            "docs/a.md",
            "README.md",
            "docs/README.md",
            "tests/t.rs",
            "a/b/c",
            "spec/r.yaml",
            "x/y.md",
            "p/x/q.rs",
            "src/x/mod.rs",
        ];
        for a in pats {
            for b in pats {
                for path in paths {
                    if path_in_scope(&s(&[a]), path) && path_in_scope(&s(&[b]), path) {
                        assert!(patterns_may_overlap(a, b), "{a} and {b} both match {path}");
                    }
                }
            }
        }
    }

    #[test]
    fn unrestricted_scope_is_described_and_contains_everything() {
        assert!(path_in_scope(&s(&[UNRESTRICTED]), "anything/at/all"));
        assert!(describe_scope(&s(&[UNRESTRICTED])).contains("unrestricted"));
        assert_eq!(scope_of_claim(&serde_json::json!({})), s(&[UNRESTRICTED]));
    }
}
