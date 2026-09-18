//! AR-0033 held-out harness. Independently authored for R1 verification iteration 4.
//!
//! Three jobs only:
//!   (a) re-derive the `OWNER-DECISION-0006` §6 census from the product tree with MY OWN splitter, so the
//!       candidate's own `tests/certification/section6.rs` is under test rather than being reused;
//!   (b) make a protected machine state root and put a genuine `DEGRADED — RECOVERY ONLY` marking on it in the
//!       exact shape `breakglass::read_marking` accepts;
//!   (c) drive the real `gov` binary with a controlled environment, so the CLI boundary claim can be tested at
//!       the boundary rather than inside the library.
#![allow(dead_code)]

use serde_json::{json, Value};
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};

pub const PRODUCT: &str = gov_runtime::FRAMEWORK_NAME;

/// The candidate worktree this crate is compiled against.
pub fn product_root() -> PathBuf {
    let p = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("..")
        .join("wt")
        .join("srr1-r1-verify-4");
    std::fs::canonicalize(&p).unwrap_or(p)
}

/// The `gov` binary built from the candidate, supplied by the runner.
pub fn gov_bin() -> PathBuf {
    PathBuf::from(std::env::var("AR0033_GOV_BIN").expect("AR0033_GOV_BIN must point at the candidate `gov`"))
}

static N: AtomicU64 = AtomicU64::new(0);

pub fn scratch(tag: &str) -> PathBuf {
    let n = N.fetch_add(1, Ordering::SeqCst);
    let d = std::env::temp_dir()
        .join("ar0033")
        .join(format!("{tag}-{}-{n}", std::process::id()));
    let _ = std::fs::remove_dir_all(&d);
    std::fs::create_dir_all(&d).unwrap();
    d
}

/// Read one product file, relative to the candidate root.
pub fn src(rel: &str) -> String {
    std::fs::read_to_string(product_root().join(rel))
        .unwrap_or_else(|e| panic!("cannot read {rel}: {e}"))
}

// ------------------------------------------------------------------ my own product-source census machinery

/// Every `.rs` file under `runtime/src` and `cli/src`, as (relative path, full text).
/// **Not cut at `#[cfg(test)]`** — the cut is a property of the candidate's census that I want to be able to
/// measure separately, so it is applied explicitly by the caller when reproducing the candidate's numbers.
pub fn product_files() -> Vec<(String, String)> {
    fn walk(d: &Path, root: &Path, out: &mut Vec<(String, String)>) {
        let Ok(rd) = std::fs::read_dir(d) else { return };
        let mut entries: Vec<_> = rd.filter_map(|e| e.ok()).map(|e| e.path()).collect();
        entries.sort();
        for p in entries {
            if p.is_dir() {
                walk(&p, root, out);
            } else if p.extension().map(|x| x == "rs").unwrap_or(false) {
                out.push((
                    p.strip_prefix(root).unwrap_or(&p).display().to_string().replace('\\', "/"),
                    std::fs::read_to_string(&p).unwrap_or_default(),
                ));
            }
        }
    }
    let root = product_root();
    let mut v = vec![];
    walk(&root.join("runtime/src"), &root, &mut v);
    walk(&root.join("cli/src"), &root, &mut v);
    v
}

pub fn cut_tests(text: &str) -> String {
    match text.find("#[cfg(test)]") {
        Some(i) => text[..i].to_string(),
        None => text.to_string(),
    }
}

#[derive(Clone)]
pub struct Fun {
    pub file: String,
    pub name: String,
    pub body: String,
}

impl Fun {
    pub fn site(&self) -> String {
        format!("{}::{}", self.file, self.name)
    }
}

/// **My splitter, deliberately different from the candidate's.** The candidate closes a function at the first
/// line equal to its opening indent plus `}`; that assumes rustfmt. This one counts braces with string and
/// line-comment elision, so the two disagree wherever the tree is not canonically formatted — which is the point:
/// `evidence/DERIVATION.md` §4 limit 5 rests on a formatting assumption I intend to test rather than accept.
pub fn split(file: &str, text: &str) -> Vec<Fun> {
    let lines: Vec<&str> = text.split('\n').collect();
    let mut out = vec![];
    for (i, raw) in lines.iter().enumerate() {
        let t = raw.trim_start();
        let opens = ["fn ", "pub fn ", "pub(crate) fn ", "pub(super) fn ", "async fn ", "pub async fn "]
            .iter()
            .any(|p| t.starts_with(p));
        if !opens {
            continue;
        }
        let name: String = t
            .split("fn ")
            .nth(1)
            .unwrap_or("")
            .chars()
            .take_while(|c| c.is_alphanumeric() || *c == '_')
            .collect();
        if name.is_empty() {
            continue;
        }
        let mut depth: i64 = 0;
        let mut started = false;
        let mut end = i;
        for (j, l) in lines.iter().enumerate().skip(i) {
            let mut clean = String::with_capacity(l.len());
            let mut in_str = false;
            let mut prev = '\0';
            let mut chars = l.chars().peekable();
            while let Some(c) = chars.next() {
                if !in_str && c == '/' && chars.peek() == Some(&'/') {
                    break;
                }
                if c == '"' && prev != '\\' {
                    in_str = !in_str;
                    prev = c;
                    continue;
                }
                if !in_str {
                    clean.push(c);
                }
                prev = c;
            }
            for c in clean.chars() {
                if c == '{' {
                    depth += 1;
                    started = true;
                } else if c == '}' {
                    depth -= 1;
                }
            }
            end = j;
            if started && depth <= 0 {
                break;
            }
        }
        out.push(Fun {
            file: file.to_string(),
            name,
            body: lines[i..=end].join("\n"),
        });
    }
    out
}

pub fn product_functions(cut: bool) -> Vec<Fun> {
    let mut out = vec![];
    for (p, t) in product_files() {
        let t = if cut { cut_tests(&t) } else { t };
        out.extend(split(&p, &t));
    }
    out
}

pub fn any(body: &str, ms: &[&str]) -> bool {
    ms.iter().any(|m| body.contains(m))
}

pub fn is_write(body: &str) -> bool {
    any(body, gov_runtime::srr::breakglass::SECTION_6_WRITE_PRIMITIVES)
}

/// Count occurrences of `needle` in every product file, excluding the ones named in `skip`.
pub fn census(needle: &str, skip: &[&str]) -> Vec<(String, usize)> {
    product_files()
        .into_iter()
        .filter(|(p, _)| !skip.iter().any(|s| p.ends_with(s)))
        .map(|(p, t)| (p, t.matches(needle).count()))
        .filter(|(_, n)| *n > 0)
        .collect()
}

// ------------------------------------------------------------------ protected machine state + the marking

/// A protected machine state root under my control, relocated the owner-accepted way (`XDG_STATE_HOME`), so
/// nothing here depends on `GOV_MACHINE_STATE_DIR`, which is the subject of `AR31-B2` and must stay unset except
/// where a test sets it deliberately.
pub struct Machine {
    pub home: PathBuf,
    pub state: PathBuf,
}

pub fn machine(tag: &str) -> Machine {
    let home = scratch(tag);
    let state = home.join("governance-os").join("machine");
    std::fs::create_dir_all(&state).unwrap();
    Machine { home, state }
}

impl Machine {
    pub fn ms(&self) -> gov_runtime::srr::state::MachineState {
        gov_runtime::srr::state::MachineState::at(&self.state).unwrap()
    }
    /// Make this machine look provisioned, so `resolve_state_root` treats `GOV_MACHINE_STATE_DIR` as hostile.
    pub fn provision(&self) {
        let t = self.state.join("trust");
        std::fs::create_dir_all(&t).unwrap();
        std::fs::write(t.join("provisioned.json"), b"{\"provisioned\": true}").unwrap();
    }
    /// Write a genuine `DEGRADED — RECOVERY ONLY` marking in the shape every product reader accepts.
    pub fn mark(&self) {
        let ms = self.ms();
        gov_runtime::srr::state::write_durable(
            &ms.degraded_path(PRODUCT),
            &json!({
                "active": true,
                "marking": gov_runtime::srr::breakglass::DEGRADED_TOKEN,
                "entered_at": "2026-09-18T00:00:00Z",
                "product": PRODUCT,
                "reason": "AR-0033 held-out verification",
            }),
        )
        .unwrap();
        assert!(
            gov_runtime::srr::breakglass::is_degraded(&ms, PRODUCT),
            "the harness failed to mark the machine"
        );
    }
    pub fn is_marked(&self) -> bool {
        gov_runtime::srr::breakglass::is_degraded(&self.ms(), PRODUCT)
    }
}

// ------------------------------------------------------------------ driving the real binary

pub struct Run {
    pub status: i32,
    pub stdout: String,
    pub stderr: String,
}

impl Run {
    pub fn json(&self) -> Value {
        serde_json::from_str(&self.stdout).unwrap_or(Value::Null)
    }
}

/// The nine refused-authority variables plus `GOV_MACHINE_STATE_DIR`: stripped from every invocation so no
/// ambient environment can influence a result.
pub const STRIPPED: &[&str] = &[
    "GOV_BREAK_GLASS",
    "GOV_BREAKGLASS",
    "GOV_TRUST_OVERRIDE",
    "GOV_SKIP_VERIFY",
    "GOV_ALLOW_UNSIGNED",
    "GOV_RELEASE_AUTHORITY",
    "GOV_HUMAN_GATE_APPROVED",
    "GOV_FLOOR_OVERRIDE",
    "GOV_MINIMUM_SECURE_RELEASE",
    "GOV_MACHINE_STATE_DIR",
];

pub fn gov(m: &Machine, cwd: &Path, extra: &[(&str, &str)], args: &[&str]) -> Run {
    let mut c = std::process::Command::new(gov_bin());
    c.current_dir(cwd).args(args);
    for k in STRIPPED {
        c.env_remove(k);
    }
    c.env("HOME", &m.home);
    c.env("XDG_STATE_HOME", &m.home);
    for (k, v) in extra {
        c.env(k, v);
    }
    let o = c.output().expect("failed to run gov");
    Run {
        status: o.status.code().unwrap_or(-1),
        stdout: String::from_utf8_lossy(&o.stdout).to_string(),
        stderr: String::from_utf8_lossy(&o.stderr).to_string(),
    }
}
