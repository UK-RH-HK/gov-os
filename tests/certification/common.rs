#![allow(dead_code)]
use serde_json::Value;
use std::path::{Path, PathBuf};
use std::process::Command;

pub fn gov_bin() -> PathBuf {
    PathBuf::from(env!("CARGO_BIN_EXE_gov"))
}
pub fn canonical_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("..")
        .canonicalize()
        .unwrap()
}
pub fn fixture(name: &str) -> PathBuf {
    canonical_root().join("fixtures").join(name).join("project")
}

/// Unique scratch dir under the OS temp dir (kept on failure as evidence).
pub fn tmp(name: &str) -> PathBuf {
    let d = std::env::temp_dir().join(format!("gov-cert-{}-{}", name, uuid_like()));
    std::fs::create_dir_all(&d).unwrap();
    d.canonicalize().unwrap()
}
fn uuid_like() -> String {
    format!(
        "{:x}{:x}",
        std::process::id(),
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos() as u64
    )
}

/// Per-scenario simulated machine: same repository root ⇒ same machine; different roots ⇒ different machines.
/// This is the value of `XDG_STATE_HOME`, from which the runtime derives its default protected state path.
pub fn machine_state_home(root: &Path) -> PathBuf {
    let key = gov_runtime::util::sha256_text(&root.display().to_string());
    std::env::temp_dir()
        .join("gov-cert-machine")
        .join(&key[..16])
}

/// The protected state root the runtime will resolve for that simulated machine.
pub fn machine_state_dir(root: &Path) -> PathBuf {
    machine_state_home(root)
        .join("governance-os")
        .join("machine")
}

pub fn copy_dir(src: &Path, dst: &Path) {
    gov_runtime::util::copy_dir(src, dst).unwrap();
}
pub fn read(root: &Path, rel: &str) -> String {
    std::fs::read_to_string(root.join(rel)).unwrap_or_else(|e| panic!("read {rel}: {e}"))
}
pub fn write(root: &Path, rel: &str, text: &str) {
    gov_runtime::util::write_text(&root.join(rel), text).unwrap();
}
pub fn exists(root: &Path, rel: &str) -> bool {
    root.join(rel).exists()
}
pub fn yaml(root: &Path, rel: &str) -> Value {
    gov_runtime::util::read_yaml(&root.join(rel)).unwrap_or_else(|e| panic!("yaml {rel}: {e}"))
}
pub fn json(root: &Path, rel: &str) -> Value {
    gov_runtime::util::read_json(&root.join(rel)).unwrap_or_else(|e| panic!("json {rel}: {e}"))
}
pub fn write_yaml(root: &Path, rel: &str, v: &Value) {
    gov_runtime::util::write_yaml(&root.join(rel), v).unwrap();
}
pub fn tree_hash(root: &Path, exclude: &[&str]) -> String {
    let mut ex = vec![".git/**", ".governance-runtime/**"];
    ex.extend_from_slice(exclude);
    gov_runtime::util::hash_tree(root, &ex).unwrap().0
}

pub fn git(root: &Path, args: &[&str]) -> (i32, String) {
    let o = Command::new("git")
        .args(args)
        .current_dir(root)
        .output()
        .unwrap();
    (
        o.status.code().unwrap_or(-1),
        String::from_utf8_lossy(&o.stdout).trim().to_string(),
    )
}
pub fn git_init_commit(root: &Path) {
    git(root, &["init", "-q"]);
    git(root, &["config", "user.email", "cert@example.invalid"]);
    git(root, &["config", "user.name", "cert"]);
    git(root, &["add", "-A"]);
    git(root, &["commit", "-q", "-m", "fixture baseline"]);
}
pub fn git_commit_all(root: &Path, msg: &str) {
    git(root, &["add", "-A"]);
    git(root, &["commit", "-q", "-m", msg]);
}

pub struct Out {
    pub code: i32,
    pub envelope: Value,
    pub stdout: String,
    pub stderr: String,
}
impl Out {
    pub fn ok(&self) -> bool {
        self.envelope["ok"].as_bool().unwrap_or(false)
    }
    pub fn result(&self) -> Value {
        self.envelope["result"].clone()
    }
    pub fn error_code(&self) -> String {
        self.envelope["error"]["code"]
            .as_str()
            .unwrap_or("")
            .to_string()
    }
    pub fn details(&self) -> Value {
        self.envelope["error"]["details"].clone()
    }
}

#[derive(Clone)]
pub struct Gov {
    pub root: PathBuf,
    pub session: String,
    pub role: String,
    pub env: Vec<(String, String)>,
}
impl Gov {
    pub fn new(root: &Path, session: &str) -> Self {
        Gov {
            root: root.to_path_buf(),
            session: session.into(),
            role: "orchestrator".into(),
            env: vec![],
        }
    }
    pub fn with_session(&self, s: &str) -> Self {
        let mut g = self.clone();
        g.session = s.into();
        g
    }
    pub fn with_role(&self, r: &str) -> Self {
        let mut g = self.clone();
        g.role = r.into();
        g
    }
    pub fn with_env(&self, k: &str, v: &str) -> Self {
        let mut g = self.clone();
        g.env.push((k.into(), v.into()));
        g
    }
    pub fn run(&self, args: &[&str]) -> Out {
        let mut c = Command::new(gov_bin());
        c.arg("--json")
            .arg("--root")
            .arg(&self.root)
            .arg("--session")
            .arg(&self.session)
            .arg("--role")
            .arg(&self.role)
            .args(args);
        c.env("GOV_CANONICAL_ROOT", canonical_root());
        // Signed Release Root v1: the protected machine state is a property of the MACHINE, not of a project, so
        // each certification scenario gets its own simulated machine keyed by its repository root. Without this the
        // suite would share one machine's floors across unrelated scenarios (and pollute the developer's own).
        //
        // This relocates the OS state home, so the runtime resolves its DEFAULT protected path — the same code path
        // a real installation takes. `GOV_MACHINE_STATE_DIR` is deliberately left unset, so the tests that probe the
        // override are probing a genuine override rather than the mechanism the whole suite depends on.
        c.env("XDG_STATE_HOME", machine_state_home(&self.root));
        c.env_remove("GOV_SESSION");
        c.env_remove("GOV_ROLE");
        for (k, v) in &self.env {
            c.env(k, v);
        }
        let o = c.output().expect("spawn gov");
        let stdout = String::from_utf8_lossy(&o.stdout).to_string();
        let stderr = String::from_utf8_lossy(&o.stderr).to_string();
        let envelope: Value = serde_json::from_str(stdout.trim()).unwrap_or_else(|_| serde_json::json!({"ok": false, "error": {"code": "NO_JSON", "message": stderr.clone()}}));
        Out {
            code: o.status.code().unwrap_or(-1),
            envelope,
            stdout,
            stderr,
        }
    }
    pub fn ok(&self, args: &[&str]) -> Value {
        let o = self.run(args);
        assert!(
            o.ok(),
            "gov {} failed (exit {}): {}\nstderr: {}",
            args.join(" "),
            o.code,
            o.envelope["error"],
            o.stderr
        );
        o.result()
    }
    pub fn err(&self, args: &[&str]) -> Out {
        let o = self.run(args);
        assert!(
            !o.ok(),
            "gov {} unexpectedly succeeded: {}",
            args.join(" "),
            o.envelope["result"]
        );
        o
    }
}

/// Copy a fixture project into a scratch dir, git-init and commit, and **provision the scenario's machine** with the
/// suite's throw-away root ([`provision`]); returns (root, gov). The fixture's first install is then the documented
/// path, "provision, then install": `init --source` [`signed_source`] (OWNER-DECISION-P2-0002).
pub fn setup_fixture(fixture_name: &str, test_name: &str, session: &str) -> (PathBuf, Gov) {
    let root = tmp(test_name);
    copy_dir(&fixture(fixture_name), &root);
    git_init_commit(&root);
    let g = Gov::new(&root, session);
    provision(&g);
    (root, g)
}

/// [`setup_fixture`] **without** provisioning, for a scenario that is about the unprovisioned posture itself (the
/// bootstrap installation of the binary's embedded payload, or the refusal of external-source ingress). Such a
/// scenario says so where it calls this.
pub fn setup_fixture_unprovisioned(
    fixture_name: &str,
    test_name: &str,
    session: &str,
) -> (PathBuf, Gov) {
    let root = tmp(test_name);
    copy_dir(&fixture(fixture_name), &root);
    git_init_commit(&root);
    let g = Gov::new(&root, session);
    (root, g)
}

// ================================================================================ provisioning (OWNER-DECISION-P2-0002)
//
// OWNER-DECISION-P2-0002 (Option A): a machine with no administrator-provisioned trust anchor refuses kernel
// material from any external source, and "dev/test machines provision a throw-away root ... so the documented
// first-run path is 'provision, then install'". The certification suite follows that path. Every scenario machine
// that installs a kernel is provisioned, explicitly, with the suite's THROW-AWAY TEST ROOT and installs releases
// signed under it:
//
// * the root is `srr_material::Publisher`'s published-seed key set (TEST MATERIAL ONLY: 2-of-3 root, release,
//   snapshot, timestamp and recovery roles), with the `human-gate` role delegated to the test owner key
//   (`ws03::owner`), because on a provisioned machine the authenticated human channel is that delegation (BC-P2-10);
// * [`provision`] anchors one simulated machine on it (`gov trust provision --anchor`, from an administrator-domain
//   directory outside every project);
// * [`signed_source`] is the current framework payload signed at [`CURRENT_SEQUENCE`]; [`signed_copy`] signs any
//   other kernel payload (a historical release, a synthetic previous release) at a chosen, lower sequence;
// * [`break_glass`] drops an owner-signed `recovery` authorisation into a machine's protected inbox — on a
//   provisioned machine a rollback below the release high-water is below-floor recovery (ARCH-0003 §7,
//   OWNER-DECISION-0006), and this is how the owner authorises it.
//
// A scenario that is *about* the unprovisioned posture says so and does not call [`provision`].

/// The sequence the suite signs the current framework release at. Historical and synthetic releases the suite
/// signs sit below it, in version order, so an update is an upgrade and a rollback is below the high-water.
pub const CURRENT_SEQUENCE: u64 = 100;
/// Sequences for the older payloads the suite installs (synthetic 4.1.1; shipped 4.1.2-4.1.4).
pub fn sequence_of(version: &str) -> u64 {
    match version {
        "4.1.1" => 11,
        "4.1.2" => 12,
        "4.1.3" => 13,
        "4.1.4" => 14,
        _ => CURRENT_SEQUENCE,
    }
}

/// The suite's throw-away test root publisher (published seeds; never a production key).
pub fn suite_publisher() -> crate::srr_material::Publisher {
    crate::srr_material::Publisher::new()
}

/// A directory in the simulated *administrator domain*: outside every project, and outside any path the product
/// treats as repository content (no `.git`, no `governance` component).
fn admin_domain() -> PathBuf {
    let d = std::env::temp_dir().join(format!("gov-cert-admin-domain-{}", std::process::id()));
    std::fs::create_dir_all(&d).unwrap();
    d.canonicalize().unwrap()
}

/// The suite root metadata (version 1), written once per test process into the administrator domain.
pub fn suite_root_file() -> PathBuf {
    static F: std::sync::OnceLock<PathBuf> = std::sync::OnceLock::new();
    F.get_or_init(|| {
        use crate::srr_material::*;
        let p = suite_publisher();
        let mut doc = root_doc(
            1,
            &far_future(),
            &[&p.root_a, &p.root_b, &p.root_c],
            2,
            &[&p.release],
            &p.snapshot,
            &p.timestamp,
            Some(&p.recovery),
        );
        let owner = crate::ws03::owner();
        let (kid, entry) = key_entry(&owner);
        doc["keys"][kid.as_str()] = entry;
        doc["roles"]["human-gate"] =
            serde_json::json!({"keyids": [owner.keyid.clone()], "threshold": 1});
        let f = admin_domain().join("suite-root-1.json");
        std::fs::write(&f, envelope(&doc, &[&p.root_a, &p.root_b])).unwrap();
        f
    })
    .clone()
}

/// Is the simulated machine `g` runs on provisioned?
pub fn is_provisioned(g: &Gov) -> bool {
    machine_state_dir(&g.root)
        .join("trust")
        .join("provisioned.json")
        .exists()
}

/// **Provision the simulated machine `g` runs on** with the suite's throw-away root (idempotent). This is the
/// administrator step of the documented first-run path; nothing is installed by it.
pub fn provision(g: &Gov) {
    if is_provisioned(g) {
        return;
    }
    let f = suite_root_file();
    let o = g.run(&["trust", "provision", "--anchor", f.to_str().unwrap()]);
    assert!(
        o.ok() || o.error_code() == "SRR_ALREADY_PROVISIONED",
        "provisioning the scenario machine failed: {}",
        o.envelope
    );
}

/// Sign the payload `<dir>/kernel` under the suite root at `sequence` (metadata version = sequence, so metadata
/// high-water follows install order). Returns `<dir>/kernel`, the path an ingress is given as `--source`.
pub fn sign_release(dir: &Path, sequence: u64) -> PathBuf {
    suite_publisher().publish(
        dir,
        sequence,
        sequence,
        "stable",
        &crate::srr_material::far_future(),
        "",
        0,
    );
    dir.join("kernel")
}

/// Stage the kernel payload at `src` (a framework tree or an installed/released `kernel/`) into a fresh release
/// directory and sign it at `sequence`. Returns the signed `<dir>/kernel`.
pub fn signed_copy(src: &Path, tag: &str, sequence: u64) -> PathBuf {
    let dir = tmp(&format!("signed-{tag}"));
    gov_runtime::kernel::stage_payload(src, &dir.join("kernel")).unwrap();
    sign_release(&dir, sequence)
}

/// The current framework payload (this checkout's `framework/`, byte-identical to the payload embedded in the
/// `gov` under test), signed under the suite root at [`CURRENT_SEQUENCE`]. Built once per test process.
pub fn signed_source() -> &'static str {
    static S: std::sync::OnceLock<String> = std::sync::OnceLock::new();
    S.get_or_init(|| {
        signed_copy(
            &canonical_root().join("framework"),
            "current",
            CURRENT_SEQUENCE,
        )
        .to_string_lossy()
        .to_string()
    })
    .as_str()
}

/// The owner authorises below-floor recovery on `g`'s machine: a `recovery`-role token bound to this machine, a
/// single-use `nonce` and the digests of `recovery_kernel` (the release the recovery restores), dropped into the
/// machine's protected inbox out of band (OWNER-DECISION-0006 §2).
pub fn break_glass(g: &Gov, recovery_kernel: &Path, nonce: &str) {
    use crate::srr_material::*;
    let p = suite_publisher();
    let inbox = PathBuf::from(
        g.ok(&["trust", "break-glass"])["inbox"]
            .as_str()
            .unwrap()
            .to_string(),
    );
    let mid = g.ok(&["trust", "status"])["machine_id"]
        .as_str()
        .unwrap()
        .to_string();
    let (_, payload_hash, kmh, ver) = measure(recovery_kernel);
    let tok = break_glass_doc(
        &mid,
        nonce,
        "certification scenario: owner-authorised recovery below the release high-water",
        &far_future(),
        &ver,
        &payload_hash,
        &kmh,
    );
    std::fs::write(
        inbox.join(format!("{nonce}.json")),
        envelope(&tok, &[&p.recovery]),
    )
    .unwrap();
}

pub fn readiness_all_present_except(missing: &[&str], na: &[(&str, &str)]) -> Value {
    let dims = gov_runtime::util::read_yaml(
        &canonical_root().join("framework/taxonomy/READINESS_DIMENSIONS.yaml"),
    )
    .unwrap();
    let mut m = serde_json::Map::new();
    for d in dims["dimensions"].as_array().unwrap() {
        let id = d["id"].as_str().unwrap();
        if missing.contains(&id) {
            m.insert(id.into(), Value::String("MISSING".into()));
        } else if let Some((_, reason)) = na.iter().find(|(k, _)| *k == id) {
            m.insert(
                id.into(),
                serde_json::json!({"status": "N/A_WITH_REASON", "reason": reason}),
            );
        } else {
            m.insert(id.into(), Value::String("PRESENT".into()));
        }
    }
    Value::Object(m)
}

pub fn doctor_check(g: &Gov, id: &str) -> (bool, String) {
    let o = g.run(&["doctor"]);
    let r = if o.ok() { o.result() } else { o.details() };
    let c = r["checks"]
        .as_array()
        .unwrap()
        .iter()
        .find(|c| c["id"] == id)
        .unwrap_or_else(|| panic!("doctor check {id} missing"));
    (
        c["ok"].as_bool().unwrap(),
        c["message"].as_str().unwrap_or("").to_string(),
    )
}
pub fn doctor_verdict(g: &Gov) -> String {
    let o = g.run(&["doctor"]);
    let r = if o.ok() { o.result() } else { o.details() };
    r["verdict"].as_str().unwrap_or("").to_string()
}

pub fn db(root: &Path) -> gov_runtime::memory::db::RuntimeDb {
    gov_runtime::memory::db::RuntimeDb::open(&root.join(".governance-runtime/state.db")).unwrap()
}
pub fn chunk_texts(root: &Path) -> Vec<String> {
    db(root)
        .query("SELECT text FROM chunks", &[])
        .unwrap()
        .into_iter()
        .map(|r| r["text"].as_str().unwrap_or("").to_string())
        .collect()
}
pub fn indexed_paths(root: &Path) -> Vec<String> {
    db(root)
        .query("SELECT path FROM artifacts", &[])
        .unwrap()
        .into_iter()
        .map(|r| r["path"].as_str().unwrap_or("").to_string())
        .collect()
}
pub fn write_report(
    root: &Path,
    name: &str,
    work: &str,
    files: &[&str],
    tests_status: &str,
) -> String {
    let p = root.join(".governance-runtime").join("reports");
    std::fs::create_dir_all(&p).unwrap();
    let f = p.join(format!("{name}.json"));
    let v = serde_json::json!({"work_completed": work, "files_changed": files, "tests": {"status": tests_status, "reason": "certification"}, "outcome": "success", "evidence": []});
    std::fs::write(&f, serde_json::to_string(&v).unwrap()).unwrap();
    f.to_string_lossy().to_string()
}

/// Brownfield adoption through A6 (all batches; destructive entries stay gated). Returns (root, planner, executor).
pub fn run_brownfield_to_a6(tag: &str) -> (PathBuf, Gov, Gov) {
    let (root, planner) = setup_fixture("brownfield", tag, "S-planner");
    let sql = read(&root, "memory/chat_history.sql");
    let dbf =
        gov_runtime::memory::db::RuntimeDb::open(&root.join("memory/chat_history.sqlite")).unwrap();
    dbf.conn
        .execute_batch(&format!("PRAGMA journal_mode=DELETE; {sql}"))
        .unwrap();
    drop(dbf);
    std::fs::remove_file(root.join("memory/chat_history.sql")).unwrap();
    git_commit_all(&root, "with chat db");
    for s in [
        "baseline",
        "inventory",
        "classify",
        "map",
        "plan",
        "test-design",
    ] {
        planner.ok(&["adopt", s]);
    }
    crate::migration::reviewer_authors_tests(&root); // BC-P2-34: the reviewer approves with tests of its own
    planner
        .with_session("S-reviewer")
        .with_role("migration-reviewer")
        .ok(&["adopt", "review", "--verdict", "MIGRATION_PLAN_APPROVED"]);
    let executor = planner
        .with_session("S-executor")
        .with_role("migration-executor");
    executor.ok(&[
        "adopt",
        "migrate",
        "--source",
        signed_source(),
        "--name",
        "shipping-quotes",
        "--alias",
        "fx-brown",
    ]);
    (root, planner, executor)
}
