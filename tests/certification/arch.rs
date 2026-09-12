//! Architectural coupling tests (D-0002 §2/§3, TASK-0008): the Governance OS core must not depend on or assume the
//! governed project's language or toolchain.
use crate::common::*;
use serde_json::json;

#[test]
fn core_crates_have_no_python_or_node_bindings() {
    for crate_toml in ["runtime/Cargo.toml", "cli/Cargo.toml", "Cargo.toml"] {
        let t = read(&canonical_root(), crate_toml).to_lowercase();
        for forbidden in [
            "pyo3",
            "cpython",
            "python3-sys",
            "napi",
            "neon",
            "rustpython",
            "inline-python",
        ] {
            assert!(
                !t.contains(forbidden),
                "{crate_toml} depends on {forbidden}"
            );
        }
    }
}

#[test]
fn kernel_data_contains_no_language_or_toolchain_assumptions() {
    let root = canonical_root().join("framework");
    let rx = regex_lite(&[
        "python",
        "pytest",
        "cargo",
        "npm ",
        "node_modules",
        "rustc",
        "pip ",
        "maven",
        "gradle",
    ]);
    let mut hits = vec![];
    for sub in [
        "constitution",
        "policies",
        "skills",
        "adapters",
        "roles",
        "taxonomy",
        "commands",
        "overlay-templates",
        "schemas",
    ] {
        for (abs, rel) in gov_runtime::paths::iter_repo_files(&root.join(sub), false) {
            let t = std::fs::read_to_string(&abs)
                .unwrap_or_default()
                .to_lowercase()
                .replace("python-2.0", "")
                .replace("psf-2.0", "");
            for w in &rx {
                if t.contains(w) {
                    hits.push(format!("{sub}/{rel}: '{w}'"));
                }
            }
        }
    }
    assert!(hits.is_empty(), "kernel data must be language-agnostic (INV-005); ecosystem knowledge belongs in tools/registry: {hits:?}");
}
fn regex_lite(words: &[&str]) -> Vec<String> {
    words.iter().map(|w| w.to_string()).collect()
}

#[test]
fn rust_sources_never_hardcode_external_language_runtimes() {
    for dir in ["runtime/src", "cli/src"] {
        for (abs, rel) in gov_runtime::paths::iter_repo_files(&canonical_root().join(dir), false) {
            let t = std::fs::read_to_string(&abs).unwrap();
            for lit in [
                "Command::new(\"python",
                "Command::new(\"node",
                "Command::new(\"cargo",
                "Command::new(\"npm",
                "Command::new(\"pip",
            ] {
                assert!(
                    !t.contains(lit),
                    "{dir}/{rel} spawns a hard-coded toolchain: {lit}"
                );
            }
        }
    }
}

/// The core runs a governed Rust project and a governed Python project with NO python/cargo/npm on PATH.
#[test]
fn core_runs_without_any_governed_toolchain_on_path() {
    let bindir = tmp("nopath-bin");
    let git = which("git").expect("git required for the harness");
    std::os::unix::fs::symlink(&git, bindir.join("git")).unwrap();
    for (fx, lang, ext) in [("greenfield", "rust", "rs"), ("migration", "python", "py")] {
        let (root, g) = setup_fixture(fx, &format!("nopath-{fx}"), "S-nopath");
        let g = g
            .with_env("PATH", bindir.to_str().unwrap())
            .with_env("GOV_DISABLE_PLUGINS", "1");
        let r = g.ok(&["init", "--name", fx, "--alias", "alias-x"]);
        assert!(r["index"]["artifacts"].as_u64().unwrap() > 0);
        let eco = g.ok(&["capabilities", "ecosystems"]);
        let ecos = eco["ecosystems"].as_array().unwrap();
        assert!(
            !ecos.is_empty(),
            "ecosystem must still be detected without the toolchain"
        );
        assert!(
            ecos.iter()
                .all(|e| e["available"] == false || e["required_binary"] == "git"),
            "toolchains must be reported unavailable: {eco}"
        );
        assert!(ecos.iter().any(|e| e["gap"]
            .as_str()
            .map(|s| s.contains("capability gap"))
            .unwrap_or(false)));
        let d = db(&root);
        let n: i64 = d
            .conn
            .query_row(
                "SELECT COUNT(*) FROM symbols WHERE language=?1",
                [lang],
                |r| r.get(0),
            )
            .unwrap();
        assert!(
            n > 0,
            "builtin code intelligence must index .{ext} symbols without external tools"
        );
        let (ok, _) = doctor_check(&g, "D022");
        assert!(
            !ok,
            "doctor must report the toolchain capability gap (never a crash)"
        );
        g.ok(&["verify", "product"]); // returns not_applicable_with_reason instead of crashing
        assert!(!doctor_verdict(&g).is_empty());
    }
}
fn which(name: &str) -> Option<std::path::PathBuf> {
    std::env::split_paths(&std::env::var_os("PATH")?)
        .map(|d| d.join(name))
        .find(|p| p.is_file())
}

/// A plugin written in bash satisfies the embed contract: the protocol is language-neutral (API-0001).
#[test]
fn plugin_protocol_is_language_neutral_bash_embedder() {
    let (root, g) = setup_fixture("greenfield", "bash-plugin", "S-plug");
    g.ok(&[
        "init",
        "--name",
        "plug",
        "--alias",
        "plug-alias",
        "--skip-index",
    ]);
    let sh = canonical_root().join("capabilities/shell/echo_embedder.sh");
    write_yaml(
        &root,
        "governance/project/plugins/echo.yaml",
        &json!({"plugin_id": "echo-embedder-sh", "capability": "embed", "version": "1", "command": [sh.to_string_lossy()], "languages": []}),
    );
    let mut pp = yaml(&root, "governance/project/PROJECT_POLICY.yaml");
    pp["policy_overrides"] = json!({"MEMORY_POLICY.embedding.provider": "echo-embedder-sh", "MEMORY_POLICY.embedding.dimensions": 8});
    write_yaml(&root, "governance/project/PROJECT_POLICY.yaml", &pp);
    let r = g.ok(&["rebuild-memory"]);
    assert_eq!(
        r["embedder"]["id"], "echo-embedder-sh",
        "manifest must pin the plugin embedder: {}",
        r["embedder"]
    );
    assert_eq!(r["embedder"]["source"], "plugin");
    assert!(
        r["degradations"].as_array().unwrap().is_empty(),
        "{:?}",
        r["degradations"]
    );
    let m = json(&root, "governance/generated/index-manifest.json");
    assert_eq!(m["embedder"]["id"], "echo-embedder-sh");
    let d = db(&root);
    let dim: i64 = d
        .conn
        .query_row("SELECT dim FROM vectors LIMIT 1", [], |r| r.get(0))
        .unwrap();
    assert_eq!(dim, 8);
    let plugins = g.ok(&["capabilities", "plugins"]);
    assert_eq!(plugins[0]["plugin_id"], "echo-embedder-sh", "{plugins}");
    assert_eq!(plugins[0]["status"], "usable");
}

/// Cross-implementation determinism: the Rust built-in embedder equals the Python reference plugin bit-for-bit.
#[test]
fn builtin_embedder_matches_python_reference_plugin() {
    let Some(py) = which("python3") else {
        eprintln!("python3 not on PATH; skipping cross-implementation check");
        return;
    };
    let texts = [
        "The agent session is not the source of truth",
        "gov rebuild-memory after path stabilisation",
        "CamelCaseIdentifier snake_case_name 42",
    ];
    let req = json!({"protocol": "gov-capability/1", "capability": "embed", "inputs": {"texts": texts, "dimensions": 64}});
    let mut c = std::process::Command::new(py);
    c.arg("-m")
        .arg("govos_capabilities.embedder_hashed_ngram")
        .current_dir(canonical_root().join("capabilities/python"))
        .env("PYTHONPATH", canonical_root().join("capabilities/python"));
    c.stdin(std::process::Stdio::piped())
        .stdout(std::process::Stdio::piped());
    let mut child = c.spawn().unwrap();
    use std::io::Write;
    child
        .stdin
        .take()
        .unwrap()
        .write_all(req.to_string().as_bytes())
        .unwrap();
    let out = child.wait_with_output().unwrap();
    let resp: serde_json::Value = serde_json::from_slice(&out.stdout).unwrap();
    assert_eq!(resp["ok"], true, "{resp}");
    let e = gov_runtime::memory::embeddings::HashedNgramEmbedder::new(64, "1");
    for (i, t) in texts.iter().enumerate() {
        let rust = e.embed(t);
        let pyv: Vec<f64> = resp["outputs"]["vectors"][i]
            .as_array()
            .unwrap()
            .iter()
            .map(|x| x.as_f64().unwrap())
            .collect();
        assert_eq!(rust.len(), pyv.len());
        for (a, b) in rust.iter().zip(pyv.iter()) {
            assert!(
                (a - b).abs() < 1e-9,
                "vector mismatch for '{t}': {a} vs {b}"
            );
        }
    }
}

#[test]
fn ecosystem_resolution_follows_the_governed_project_not_the_os() {
    let (_r, g) = setup_fixture("greenfield", "eco-rust", "S-eco");
    let e = g.ok(&["capabilities", "ecosystems"]);
    assert!(e["ecosystems"]
        .as_array()
        .unwrap()
        .iter()
        .any(|x| x["id"] == "rust-cargo" && x["test"]["command"][0] == "cargo"));
    let (_r2, g2) = setup_fixture("migration", "eco-py", "S-eco");
    let e2 = g2.ok(&["capabilities", "ecosystems"]);
    let ids: Vec<String> = e2["ecosystems"]
        .as_array()
        .unwrap()
        .iter()
        .map(|x| x["id"].as_str().unwrap().to_string())
        .collect();
    assert!(
        ids.contains(&"python".to_string()) && ids.contains(&"node-npm".to_string()),
        "{ids:?}"
    );
}

#[test]
fn schemas_policies_and_registries_validate_against_kernel_schemas() {
    let root = canonical_root();
    let reg = gov_runtime::schemas::SchemaRegistry::new(&root.join("framework/schemas"));
    for name in reg.names() {
        let s = reg.get(&name).unwrap();
        assert!(s.get("$id").is_some(), "{name} missing $id");
    }
    let pairs = [
        (
            "framework/constitution/HARD_INVARIANTS.yaml",
            "hard-invariants",
        ),
        ("framework/roles/ROLES.yaml", "roles"),
        (
            "framework/commands/COMMAND_CONTRACT.yaml",
            "command-contract",
        ),
        (
            "framework/taxonomy/READINESS_DIMENSIONS.yaml",
            "readiness-dimensions",
        ),
        ("tools/mcp/registry.yaml", "mcp-registry"),
        ("migrations/M-4.1.1-4.1.2.yaml", "migration"),
    ];
    for (f, s) in pairs {
        let v = gov_runtime::util::read_yaml(&root.join(f)).unwrap();
        let e = reg.errors(s, &v).unwrap();
        assert!(e.is_empty(), "{f}: {e:?}");
    }
    for p in gov_runtime::policy::POLICY_NAMES {
        let v = gov_runtime::util::read_yaml(&root.join(format!("framework/policies/{p}.yaml")))
            .unwrap();
        let e = reg.errors(&format!("policy-{p}"), &v).unwrap();
        assert!(e.is_empty(), "{p}: {e:?}");
    }
    for (abs, rel) in gov_runtime::paths::iter_repo_files(&root.join("framework/skills"), false) {
        let v = gov_runtime::util::read_yaml(&abs).unwrap();
        let e = reg.errors("skill", &v).unwrap();
        assert!(e.is_empty(), "{rel}: {e:?}");
    }
    let tools = gov_runtime::util::read_yaml(&root.join("tools/registry/TOOLS.yaml")).unwrap();
    for t in tools["tools"].as_array().unwrap() {
        let e = reg.errors("tool", t).unwrap();
        assert!(e.is_empty(), "{}: {e:?}", t["tool_id"]);
    }
    // the canonical repository's own governed records
    let store = gov_runtime::records::RecordStore::load(&root);
    assert!(
        store.get("D-0002").is_some()
            && store.get("ARCH-0001").is_some()
            && store.get("API-0001").is_some()
    );
    assert!(
        store.problems.is_empty(),
        "canonical records must parse: {:?}",
        store.problems
    );
    for r in &store.records {
        let t = r.rtype();
        let s = if reg.has(&t) {
            t.clone()
        } else {
            "record".into()
        };
        let e = reg.errors(&s, &r.data).unwrap();
        assert!(e.is_empty(), "{}: {e:?}", r.path);
    }
    assert_eq!(store.get("D-0001").unwrap().status(), "SUPERSEDED");
}
