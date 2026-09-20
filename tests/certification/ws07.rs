//! Repair iteration 1 round 2, WS-7 (P2-AR-0028): plugin and tool trust — BC-P2-39 (elevation never decided by a
//! descriptor), BC-P2-40 (every executed byte bound), BC-P2-11 plugin side (a registration is approved only by a gate
//! raised for exactly it), BC-P2-09 registry side (registry entries honoured only as the OS wrote them), BC-P2-41
//! (tool review and approval bound to the installation), and WS-6 IP-3 (tool health failures in failure memory).
//!
//! Builder regression evidence (Contract v3 O3), not acceptance evidence. Human answers come only through WS-3's
//! owner-signed channel helper (`ws03::human_decide`); every invocation declares its role.
#![allow(dead_code)]
use crate::common::*;
use serde_json::{json, Value};
use std::path::{Path, PathBuf};

fn fresh(tag: &str) -> (PathBuf, Gov) {
    let (root, g) = setup_fixture("greenfield", tag, "S-ws7");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        tag,
        "--alias",
        &format!("a-{tag}"),
        "--skip-index",
    ]);
    git_commit_all(&root, "after init");
    (root, g)
}

fn write_exec(root: &Path, rel: &str, text: &str) {
    write(root, rel, text);
    use std::os::unix::fs::PermissionsExt;
    std::fs::set_permissions(root.join(rel), std::fs::Permissions::from_mode(0o755)).unwrap();
}

/// Where the OS writes the plugin registry (BC-P2-31, WS-7 round 3: tracked T2 state outside the regenerable views).
const REGISTRY: &str = "governance/registry/plugin-registry.json";
/// Where it was kept before BC-P2-31.
const LEGACY_REGISTRY: &str = "governance/generated/plugin-registry.json";

const EMBED_OK: &str = r#"{"protocol":"gov-capability/1","ok":true,"provider":{"id":"p","version":"1"},"outputs":{"vectors":[],"dim":8}}"#;

/// A shell plugin that records each execution in `marker` (and runs `extra`), so "did it run?" is observed.
fn marker_plugin(root: &Path, rel: &str, marker: &Path, extra: &str) {
    write_exec(
        root,
        rel,
        &format!(
            "#!/bin/sh\ncat >/dev/null\necho EXECUTED >> '{}'\n{extra}\nprintf '%s\\n' '{EMBED_OK}'\n",
            marker.display()
        ),
    );
}

fn runs(marker: &Path) -> usize {
    std::fs::read_to_string(marker)
        .map(|s| s.lines().filter(|l| l.contains("EXECUTED")).count())
        .unwrap_or(0)
}

fn invoke(g: &Gov, id: &str) -> Out {
    g.run(&[
        "capabilities",
        "invoke",
        "--plugin",
        id,
        "--inputs",
        "{\"texts\": []}",
    ])
}

fn set_overrides(root: &Path, over: Value) {
    let mut pp = yaml(root, "governance/project/PROJECT_POLICY.yaml");
    pp["policy_overrides"] = over;
    write_yaml(root, "governance/project/PROJECT_POLICY.yaml", &pp);
}

fn gate_count(root: &Path) -> usize {
    std::fs::read_dir(root.join("spec/decisions"))
        .map(|rd| {
            rd.flatten()
                .filter(|e| e.file_name().to_string_lossy().starts_with("HDG-"))
                .count()
        })
        .unwrap_or(0)
}

fn unrelated_answered_gate(g: &Gov) -> String {
    let id = g.ok(&[
        "gate",
        "create",
        "--question",
        "May we rename the docs folder?",
        "--fields",
        &crate::ws03::package(json!({})),
    ])["id"]
        .as_str()
        .unwrap()
        .to_string();
    crate::ws03::human_decide(g, &id, "A");
    id
}

/// **Register a plugin the governed way**: `gov plugins register` (as `g`'s role) raises a gate for exactly this
/// registration; the OS renders it and the product owner answers A through the owner-signed channel; the same
/// registration is run again and succeeds. Returns the final `plugins register` result.
///
/// INT3-O1 (round 4): a registration is also a material governance/security change, so the first request also
/// returns the change transaction the OS proposed for it (`change_transaction`, CIT-P simulated automatically) with
/// its own gate. The owner answers both — the execution approval (`human_gate`, subject `plugin-registration`) and
/// the change approval (the transaction's gate) — and the repeated registration executes the transaction (CIT-E).
/// For an OS-provided plugin there is no execution approval, so the only gate is the transaction's.
pub fn register_approved(g: &Gov, descriptor: &Path) -> Value {
    let mut r = g.ok(&[
        "plugins",
        "register",
        "--descriptor",
        descriptor.to_str().unwrap(),
    ]);
    let mut execution_gate: Option<String> = None;
    let mut answered: Vec<String> = vec![];
    for _ in 0..3 {
        if r["registered"] == true {
            break;
        }
        let mut gates: Vec<String> = vec![];
        if let Some(gid) = r["human_gate"].as_str() {
            gates.push(gid.to_string());
        }
        if let Some(gid) = r["change_transaction"]["human_gate"].as_str() {
            gates.push(gid.to_string());
        }
        gates.retain(|x| !answered.contains(x));
        assert!(
            !gates.is_empty(),
            "registration neither succeeded nor raised a gate: {r}"
        );
        for gid in gates {
            if execution_gate.is_none()
                && yaml(&g.root, &format!("spec/decisions/{gid}.yaml"))["subject"]["kind"]
                    == "plugin-registration"
            {
                execution_gate = Some(gid.clone());
            }
            crate::ws03::human_decide(&g.with_role("orchestrator"), &gid, "A");
            answered.push(gid);
        }
        r = g.ok(&[
            "plugins",
            "register",
            "--descriptor",
            descriptor.to_str().unwrap(),
        ]);
    }
    assert_eq!(r["registered"], true, "{r}");
    if let Some(gate) = execution_gate {
        assert_eq!(r["registry_entry"]["registration_gate"], json!(gate), "{r}");
    }
    // the registration was written by its change transaction, which committed
    if r["unchanged"] != true {
        assert_eq!(r["change_transaction"]["cit_status"], "COMMITTED", "{r}");
    }
    r
}

// ============================================================================================ BC-P2-39

/// Contract v3 F4:426/:430, ARCH-0003 §9: whether a plugin needs approval never rests on what its descriptor says.
/// A plugin that declares no elevated permission but writes files never runs unregistered — by any role, through any
/// path (invoke, a pinned embedder, a health ping). The OS's own capability server keeps D-0005's hand-declared
/// allowance, because its effects are the release's own and cannot exceed the non-elevated floor.
#[test]
fn an_executable_plugin_never_runs_on_its_own_declarations() {
    let (root, g) = fresh("ws07-elev");
    let marker = root.join("ws07-marker.txt");
    marker_plugin(
        &root,
        "tools/sneaky.sh",
        &marker,
        "echo undeclared > UNDECLARED_WRITE.txt",
    );
    write_yaml(
        &root,
        "governance/project/plugins/sneaky.yaml",
        &json!({"plugin_id": "sneaky", "capability": "embed", "version": "1", "command": ["sh", "tools/sneaky.sh"],
                "permissions": {"network": false, "filesystem_write": false}, "required_permission_classes": [],
                "health_check": {"kind": "protocol_ping"}}),
    );
    for role in ["product-spec-agent", "tooling-engineer", "orchestrator"] {
        let e = invoke(&g.with_role(role), "sneaky");
        assert_eq!(
            e.error_code(),
            "PLUGIN_NOT_APPROVED",
            "{role}: {}",
            e.envelope
        );
        assert_eq!(
            e.details()["details"]["cause"],
            "UNREGISTERED_EXECUTABLE",
            "{}",
            e.envelope
        );
    }
    // pinned as the embedder: the indexer refuses it too
    set_overrides(
        &root,
        json!({"MEMORY_POLICY.embedding.provider": "sneaky", "MEMORY_POLICY.embedding.dimensions": 8}),
    );
    assert_eq!(
        g.err(&["rebuild-memory"]).error_code(),
        "PLUGIN_NOT_APPROVED"
    );
    set_overrides(&root, json!({}));
    // a health ping never runs a plugin the acting role may not execute
    let h = g.ok(&["plugins", "health", "--ping"]);
    let row = h
        .as_array()
        .unwrap()
        .iter()
        .find(|r| r["plugin_id"] == "sneaky")
        .cloned()
        .unwrap();
    assert_eq!(row["ping"]["skipped"], true, "{row}");
    assert_eq!(runs(&marker), 0, "the under-declaring plugin executed");
    assert!(!exists(&root, "UNDECLARED_WRITE.txt"));
    let (ok28, msg28) = doctor_check(&g, "D028");
    assert!(!ok28 && msg28.contains("sneaky"), "{msg28}");

    // D-0005's allowance where the effects are non-elevated: this binary's own capability server, hand-declared
    let bin = gov_bin().to_string_lossy().to_string();
    write_yaml(
        &root,
        "governance/project/plugins/os-embed.yaml",
        &json!({"plugin_id": "os-embed", "capability": "embed", "version": "1", "command": [bin, "capabilities", "serve-embed", "--id", "os-embed"]}),
    );
    let out = g.with_role("product-spec-agent").ok(&[
        "capabilities",
        "invoke",
        "--plugin",
        "os-embed",
        "--inputs",
        "{\"texts\": [\"a\"]}",
    ]);
    assert_eq!(out["provider"]["id"], "os-embed", "{out}");
    // ... but the same binary asked to do anything else is an ordinary executable
    for cmd in [
        json!([
            bin,
            "capabilities",
            "serve-embed",
            "--id",
            "x",
            "--root",
            "/"
        ]),
        json!([bin, "plugins", "list"]),
    ] {
        write_yaml(
            &root,
            "governance/project/plugins/os-other.yaml",
            &json!({"plugin_id": "os-other", "capability": "embed", "version": "1", "command": cmd}),
        );
        assert_eq!(
            invoke(&g, "os-other").error_code(),
            "PLUGIN_NOT_APPROVED",
            "{cmd}"
        );
    }
    // a declared pin on the hand-declared server is checked against what it executes
    write_yaml(
        &root,
        "governance/project/plugins/os-embed.yaml",
        &json!({"plugin_id": "os-embed", "capability": "embed", "version": "1", "command": [bin, "capabilities", "serve-embed", "--id", "os-embed"], "pin": {"sha256": "0".repeat(64)}}),
    );
    assert_eq!(invoke(&g, "os-embed").error_code(), "PLUGIN_PIN_MISMATCH");
}

// ============================================================================================ BC-P2-11 (plugin side)

/// Contract v3:430, :678: an executable registration is authorised only by a presented, owner-answered A on a gate
/// raised for exactly that plugin identity, version, implementation and permission set — and only while it stays so.
#[test]
fn a_registration_is_approved_only_by_a_gate_raised_for_exactly_it() {
    let (root, g) = fresh("ws07-gate");
    let te = g.with_role("tooling-engineer");
    let marker = root.join("ws07-marker.txt");
    marker_plugin(&root, "tools/p.sh", &marker, "");
    let desc = json!({"plugin_id": "p1", "capability": "embed", "version": "1", "command": ["sh", "tools/p.sh"], "required_permission_classes": ["NETWORK_READ"]});
    let df = root.join("governance/project/plugins/p1.yaml");
    // an answered gate raised for another question never approves the registration
    let unrelated = unrelated_answered_gate(&g);
    let mut cited = desc.clone();
    cited["registration_gate"] = json!(unrelated);
    write_yaml(&root, "governance/project/plugins/p1.yaml", &cited);
    let r = te.ok(&["plugins", "register", "--descriptor", df.to_str().unwrap()]);
    assert_eq!(r["registered"], false, "{r}");
    assert!(
        r["gates_not_honoured"]
            .as_array()
            .unwrap()
            .iter()
            .any(|x| x["gate"] == json!(unrelated) && x["code"] == "GATE_MISMATCH"),
        "{r}"
    );
    let g1 = r["human_gate"].as_str().unwrap().to_string();
    assert_ne!(g1, unrelated);
    let gate1 = yaml(&root, &format!("spec/decisions/{g1}.yaml"));
    assert_eq!(gate1["trigger"], "privilege_elevation");
    assert_eq!(gate1["subject"]["kind"], "plugin-registration");
    assert_eq!(gate1["subject"]["sha256"], r["registration_subject_sha256"]);
    // pending: the same gate is returned, never a duplicate
    let before = gate_count(&root);
    let r = te.ok(&["plugins", "register", "--descriptor", df.to_str().unwrap()]);
    assert_eq!(
        (r["human_gate"].as_str(), r["state"].as_str()),
        (Some(g1.as_str()), Some("PENDING")),
        "{r}"
    );
    assert_eq!(gate_count(&root), before);
    // declined: the request ends; no new gate; the plugin never runs
    crate::ws03::human_decide(&g, &g1, "B");
    let r = te.ok(&["plugins", "register", "--descriptor", df.to_str().unwrap()]);
    assert_eq!(
        (r["declined"].as_bool(), r["human_gate"].as_str()),
        (Some(true), Some(g1.as_str())),
        "{r}"
    );
    assert_eq!(gate_count(&root), before);
    assert_eq!(invoke(&te, "p1").error_code(), "PLUGIN_NOT_APPROVED");
    // withdrawing the refusal lets the request be raised again; an A on the new gate registers it
    g.ok(&["gate", "revoke", &g1]);
    let r = te.ok(&["plugins", "register", "--descriptor", df.to_str().unwrap()]);
    let g2 = r["human_gate"].as_str().unwrap().to_string();
    assert_ne!(g2, g1);
    // INT3-O1 (round 4): the registration is also a material governance/security change; the OS proposed its change
    // transaction (CIT-P simulated automatically) with its own gate, and the execution approval does not stand in
    // for it — the registration stays unwritten until the change is approved too
    let ct_gate = r["change_transaction"]["human_gate"]
        .as_str()
        .unwrap()
        .to_string();
    assert_ne!(ct_gate, g2, "{r}");
    crate::ws03::human_decide(&g, &g2, "A");
    let r = te.ok(&["plugins", "register", "--descriptor", df.to_str().unwrap()]);
    assert_eq!(r["registered"], false, "{r}");
    assert_eq!(r["human_gate"], json!(ct_gate), "{r}");
    crate::ws03::human_decide(&g, &ct_gate, "A");
    let r = te.ok(&["plugins", "register", "--descriptor", df.to_str().unwrap()]);
    assert_eq!(r["registered"], true, "{r}");
    assert_eq!(r["change_transaction"]["cit_status"], "COMMITTED", "{r}");
    let e = &json(&root, REGISTRY)["plugins"]["p1"];
    assert_eq!(e["registration_gate"], json!(g2));
    assert_eq!(
        e["registration_subject_sha256"],
        yaml(&root, &format!("spec/decisions/{g2}.yaml"))["subject"]["sha256"]
    );
    te.ok(&[
        "capabilities",
        "invoke",
        "--plugin",
        "p1",
        "--inputs",
        "{\"texts\": []}",
    ]);
    assert_eq!(runs(&marker), 1);
    // the approval is bound to the subject: widening the permission set is a new request
    let saved = std::fs::read(&df).unwrap();
    let mut wider = yaml(&root, "governance/project/plugins/p1.yaml");
    wider["required_permission_classes"] = json!(["NETWORK_READ", "NETWORK_WRITE"]);
    write_yaml(&root, "governance/project/plugins/p1.yaml", &wider);
    assert_eq!(invoke(&g, "p1").error_code(), "PLUGIN_REGISTRY_MISMATCH");
    let r = g.ok(&["plugins", "register", "--descriptor", df.to_str().unwrap()]);
    assert_eq!(
        r["registered"], false,
        "a widened permission set rode on the old approval: {r}"
    );
    assert_ne!(r["human_gate"], json!(g2));
    std::fs::write(&df, &saved).unwrap();
    te.ok(&[
        "capabilities",
        "invoke",
        "--plugin",
        "p1",
        "--inputs",
        "{\"texts\": []}",
    ]);
    assert_eq!(runs(&marker), 2);
    // the approving gate of plugin p1 cannot be cited for another plugin
    marker_plugin(&root, "tools/q.sh", &marker, "");
    write_yaml(
        &root,
        "governance/project/plugins/q1.yaml",
        &json!({"plugin_id": "q1", "capability": "embed", "version": "1", "command": ["sh", "tools/q.sh"], "registration_gate": g2}),
    );
    let r = te.ok(&[
        "plugins",
        "register",
        "--descriptor",
        root.join("governance/project/plugins/q1.yaml")
            .to_str()
            .unwrap(),
    ]);
    assert_eq!(r["registered"], false, "{r}");
    assert!(
        r["gates_not_honoured"]
            .to_string()
            .contains("GATE_MISMATCH"),
        "{r}"
    );
    // approval derives from the live gate: revoking it stops the plugin at its next execution
    g.ok(&["gate", "revoke", &g2]);
    let e = invoke(&te, "p1");
    assert_eq!(e.error_code(), "PLUGIN_NOT_APPROVED", "{}", e.envelope);
    assert_eq!(
        e.details()["details"]["cause"],
        "GATE_REVOKED",
        "{}",
        e.envelope
    );
    assert_eq!(runs(&marker), 2);
    let (ok28, msg28) = doctor_check(&g, "D028");
    assert!(!ok28 && msg28.contains("p1"), "{msg28}");
}

// ============================================================================================ BC-P2-40

/// Contract v3 F4:428-429: every executable plugin's implementation and descriptor bytes — module-form and inline
/// commands included — are bound in OS-written registration state; any change fails closed at execution and is
/// reported; neither the caller's environment, a reset of machine-local state nor a fresh clone re-baselines them.
#[test]
fn every_byte_a_plugin_executes_is_bound() {
    if std::process::Command::new("python3")
        .arg("-c")
        .arg("pass")
        .output()
        .is_err()
    {
        eprintln!("python3 not on PATH; skipping the module-form binding check");
        return;
    }
    let (root, g) = fresh("ws07-bytes");
    let te = g.with_role("tooling-engineer");
    let marker = root.join("ws07-marker.txt");
    write(&root, "modplug/__init__.py", "");
    let main_ok = format!(
        "import sys\nsys.stdin.read()\nopen({:?}, 'a').write('EXECUTED\\n')\nprint({:?})\n",
        marker.display().to_string(),
        EMBED_OK
    );
    write(&root, "modplug/__main__.py", &main_ok);
    write_yaml(
        &root,
        "governance/project/plugins/modplug.yaml",
        &json!({"plugin_id": "modplug", "capability": "embed", "version": "1", "command": ["python3", "-m", "modplug"]}),
    );
    let df = root.join("governance/project/plugins/modplug.yaml");
    let r = register_approved(&te, &df);
    let files: Vec<String> = r["registry_entry"]["implementation_files"]
        .as_array()
        .unwrap()
        .iter()
        .map(|f| f.as_str().unwrap().to_string())
        .collect();
    assert!(
        files.contains(&"modplug/__init__.py".to_string())
            && files.contains(&"modplug/__main__.py".to_string()),
        "{files:?}"
    );
    assert!(
        files.iter().any(|f| f.contains("python")),
        "the interpreter is bound too: {files:?}"
    );
    assert_eq!(
        r["registry_entry"]["implementation_sha256"]
            .as_str()
            .unwrap()
            .len(),
        64
    );
    te.ok(&[
        "capabilities",
        "invoke",
        "--plugin",
        "modplug",
        "--inputs",
        "{\"texts\": []}",
    ]);
    assert_eq!(runs(&marker), 1);
    assert!(
        !exists(&root, "modplug/__pycache__"),
        "an execution must not rewrite its own bound tree"
    );
    // swap the module after approval
    write(
        &root,
        "modplug/__main__.py",
        &main_ok.replace("EXECUTED", "EXECUTED SWAPPED"),
    );
    let e = invoke(&te, "modplug");
    assert_eq!(e.error_code(), "PLUGIN_PIN_MISMATCH", "{}", e.envelope);
    assert!(e.envelope.to_string().contains("modplug/__main__.py"));
    let (ok28, msg28) = doctor_check(&g, "D028");
    assert!(!ok28 && msg28.contains("modplug/__main__.py"), "{msg28}");
    write(&root, "modplug/__main__.py", &main_ok);
    te.ok(&[
        "capabilities",
        "invoke",
        "--plugin",
        "modplug",
        "--inputs",
        "{\"texts\": []}",
    ]);
    // a new file in the package, and a planted byte-code cache, are changes too
    write(&root, "modplug/helper.py", "X = 1\n");
    assert_eq!(invoke(&te, "modplug").error_code(), "PLUGIN_PIN_MISMATCH");
    std::fs::remove_file(root.join("modplug/helper.py")).unwrap();
    write(
        &root,
        "modplug/__pycache__/__main__.cpython-399.pyc",
        "planted",
    );
    assert_eq!(invoke(&te, "modplug").error_code(), "PLUGIN_PIN_MISMATCH");
    std::fs::remove_dir_all(root.join("modplug/__pycache__")).unwrap();
    assert_eq!(runs(&marker), 2);
    // the caller's environment cannot substitute code: a sitecustomize on PYTHONPATH never runs inside the plugin
    let inject = root.join("inject");
    let marker2 = root.join("ws07-injected.txt");
    write(
        &root,
        "inject/sitecustomize.py",
        &format!(
            "open({:?}, 'w').write('INJECTED')\n",
            marker2.display().to_string()
        ),
    );
    te.with_env("PYTHONPATH", inject.to_str().unwrap()).ok(&[
        "capabilities",
        "invoke",
        "--plugin",
        "modplug",
        "--inputs",
        "{\"texts\": []}",
    ]);
    assert!(
        !marker2.exists(),
        "code injected through PYTHONPATH ran inside an approved plugin"
    );
    // a reset of machine-local runtime state does not re-baseline tampered bytes
    write(
        &root,
        "modplug/__main__.py",
        &main_ok.replace("EXECUTED", "EXECUTED TAMPERED"),
    );
    std::fs::remove_dir_all(root.join(".governance-runtime")).unwrap();
    assert_eq!(invoke(&te, "modplug").error_code(), "PLUGIN_PIN_MISMATCH");
    // nor does a fresh clone on another machine: the entry is not this machine's, and re-registering is a new
    // governed act whose gate tells the approver the implementation differs from the tracked registration
    git_commit_all(&root, "tampered plugin");
    let b = tmp("ws07-bytes-clone");
    let (code, out) = git(
        &root,
        &[
            "clone",
            "-q",
            root.to_str().unwrap(),
            b.join("repo").to_str().unwrap(),
        ],
    );
    assert_eq!(code, 0, "{out}");
    let broot = b.join("repo");
    let gb = Gov::new(&broot, "S-ws7-b").with_role("tooling-engineer");
    let e = invoke(&gb, "modplug");
    assert_eq!(
        e.error_code(),
        "PLUGIN_REGISTRATION_UNBOUND",
        "{}",
        e.envelope
    );
    let rb = gb.ok(&[
        "plugins",
        "register",
        "--descriptor",
        broot
            .join("governance/project/plugins/modplug.yaml")
            .to_str()
            .unwrap(),
    ]);
    assert_eq!(rb["registered"], false, "{rb}");
    let gate = yaml(
        &broot,
        &format!("spec/decisions/{}.yaml", rb["human_gate"].as_str().unwrap()),
    );
    assert!(
        gate["current_state"]
            .as_str()
            .unwrap()
            .contains("DIFFERENT implementation"),
        "{gate}"
    );
    assert_eq!(runs(&marker), 3);

    // inline code is bound through the descriptor
    let (root, g) = fresh("ws07-inline");
    let te = g.with_role("tooling-engineer");
    let marker = root.join("ws07-marker.txt");
    let code = format!(
        "cat >/dev/null; echo EXECUTED >> '{}'; printf '%s\\n' '{EMBED_OK}'",
        marker.display()
    );
    write_yaml(
        &root,
        "governance/project/plugins/inline.yaml",
        &json!({"plugin_id": "inline", "capability": "embed", "version": "1", "command": ["sh", "-c", code]}),
    );
    register_approved(&te, &root.join("governance/project/plugins/inline.yaml"));
    te.ok(&[
        "capabilities",
        "invoke",
        "--plugin",
        "inline",
        "--inputs",
        "{\"texts\": []}",
    ]);
    let mut d = yaml(&root, "governance/project/plugins/inline.yaml");
    d["command"][2] = json!(code.replace("EXECUTED", "EXECUTED EDITED"));
    write_yaml(&root, "governance/project/plugins/inline.yaml", &d);
    assert_eq!(
        invoke(&te, "inline").error_code(),
        "PLUGIN_REGISTRY_MISMATCH"
    );
    assert_eq!(runs(&marker), 1);
    // a helper the entry point loads is bound when the descriptor declares it
    write(
        &root,
        "tools/lib.sh",
        &format!("echo EXECUTED >> '{}'\n", marker.display()),
    );
    write_exec(&root, "tools/main.sh", &format!("#!/bin/sh\ncat >/dev/null\n. \"$(dirname \"$0\")/lib.sh\"\nprintf '%s\\n' '{EMBED_OK}'\n"));
    write_yaml(
        &root,
        "governance/project/plugins/withlib.yaml",
        &json!({"plugin_id": "withlib", "capability": "embed", "version": "1", "command": ["sh", "tools/main.sh"], "implementation": ["tools/lib.sh"]}),
    );
    let r = register_approved(&te, &root.join("governance/project/plugins/withlib.yaml"));
    assert!(
        r["registry_entry"]["implementation_files"]
            .to_string()
            .contains("tools/lib.sh"),
        "{r}"
    );
    te.ok(&[
        "capabilities",
        "invoke",
        "--plugin",
        "withlib",
        "--inputs",
        "{\"texts\": []}",
    ]);
    write(&root, "tools/lib.sh", "echo swapped\n");
    assert_eq!(invoke(&te, "withlib").error_code(), "PLUGIN_PIN_MISMATCH");
    // an implementation the OS cannot locate is refused before any gate
    write_yaml(
        &root,
        "governance/project/plugins/nomod.yaml",
        &json!({"plugin_id": "nomod", "capability": "embed", "version": "1", "command": ["python3", "-m", "no_such_module_ws07"]}),
    );
    let e = te.err(&[
        "plugins",
        "register",
        "--descriptor",
        root.join("governance/project/plugins/nomod.yaml")
            .to_str()
            .unwrap(),
    ]);
    assert_eq!(
        e.error_code(),
        "PLUGIN_IMPLEMENTATION_UNRESOLVED",
        "{}",
        e.envelope
    );
}

// ============================================================================================ BC-P2-09 (registry side)

/// D-0007 T2 / rule 2, Contract v3:427: a plugin registry entry is honoured only as `gov plugins register` wrote it
/// on this machine; a hand-written or edited entry is refused at execution and reported by doctor and the suite.
#[test]
fn registry_entries_are_honoured_only_as_the_os_wrote_them() {
    let (root, g) = fresh("ws07-registry");
    let te = g.with_role("tooling-engineer");
    let marker = root.join("ws07-marker.txt");
    marker_plugin(&root, "tools/p.sh", &marker, "");
    marker_plugin(&root, "tools/n.sh", &marker, "");
    write_yaml(
        &root,
        "governance/project/plugins/p1.yaml",
        &json!({"plugin_id": "p1", "capability": "embed", "version": "1", "command": ["sh", "tools/p.sh"]}),
    );
    register_approved(&te, &root.join("governance/project/plugins/p1.yaml"));
    te.ok(&[
        "capabilities",
        "invoke",
        "--plugin",
        "p1",
        "--inputs",
        "{\"texts\": []}",
    ]);
    let reg_path = REGISTRY;
    let good = json(&root, reg_path);
    assert!(
        good["plugins"]["p1"]["os_binding"]["mac"].is_string(),
        "{good}"
    );
    // a worker writes an entry for an unregistered plugin (copying the sealed entry of p1, and afresh)
    write_yaml(
        &root,
        "governance/project/plugins/n1.yaml",
        &json!({"plugin_id": "n1", "capability": "embed", "version": "1", "command": ["sh", "tools/n.sh"]}),
    );
    let dsha = gov_runtime::util::sha256_hex(
        &std::fs::read(root.join("governance/project/plugins/n1.yaml")).unwrap(),
    );
    for forged in [
        {
            let mut e = good["plugins"]["p1"].clone();
            e["plugin_id"] = json!("n1");
            e["descriptor_sha256"] = json!(dsha);
            e
        },
        json!({"plugin_id": "n1", "capability": "embed", "version": "1", "descriptor_sha256": dsha, "approved_roles": ["all"], "registered_by_role": "human", "registered_at": "2026-09-19T00:00:00Z", "method": "gov plugins register"}),
    ] {
        let mut reg = good.clone();
        reg["plugins"]["n1"] = forged;
        write_json(&root, reg_path, &reg);
        let e = invoke(&te, "n1");
        assert_eq!(
            e.error_code(),
            "PLUGIN_REGISTRATION_UNBOUND",
            "{}",
            e.envelope
        );
        let (ok28, msg28) = doctor_check(&g, "D028");
        assert!(!ok28 && msg28.contains("n1"), "{msg28}");
        let au = g.run(&["audit", "--no-persist", "--family", "plugin_governance"]);
        let f = if au.ok() { au.result() } else { au.details() };
        assert!(
            f["findings"].to_string().contains("n1"),
            "{}",
            f["findings"]
        );
    }
    // editing the sealed entry of a registered plugin (widening its roles) unbinds it
    let mut reg = good.clone();
    reg["plugins"]["p1"]["approved_roles"] = json!(["all", "backend-engineer"]);
    write_json(&root, reg_path, &reg);
    assert_eq!(
        invoke(&te, "p1").error_code(),
        "PLUGIN_REGISTRATION_UNBOUND"
    );
    // an entry with no descriptor that no gov operation wrote is reported as such
    let mut reg = good.clone();
    reg["plugins"]["ghost"] = json!({"plugin_id": "ghost", "capability": "embed", "version": "1"});
    write_json(&root, reg_path, &reg);
    let (ok28, msg28) = doctor_check(&g, "D028");
    assert!(!ok28 && msg28.contains("ghost"), "{msg28}");
    // the OS-written registry, restored, is honoured again
    write_json(&root, reg_path, &good);
    te.ok(&[
        "capabilities",
        "invoke",
        "--plugin",
        "p1",
        "--inputs",
        "{\"texts\": []}",
    ]);
    assert_eq!(runs(&marker), 2, "n1 never ran");
}

fn write_json(root: &Path, rel: &str, v: &Value) {
    std::fs::write(root.join(rel), serde_json::to_string_pretty(v).unwrap()).unwrap();
}

// ============================================================================================ BC-P2-41 + IP-3

fn tool_descriptor(root: &Path, name: &str, extra: Value) -> PathBuf {
    let mut d = json!({"tool_id": "TOOL-W7", "name": "w7", "type": "CLI", "capabilities": ["quantum_compile"], "version": "1.0",
        "version_pin": "1.0.0", "permissions": {"repo_write": false, "network": false}, "required_permission_classes": ["READ_REPO"],
        "license": "MIT", "reversible": true, "security_review": "passed", "cost_usd": 0, "install_command": ["true"],
        "uninstall_command": ["true"], "health_check": {"kind": "command", "command": ["true"], "expect_exit": 0}});
    for (k, v) in extra.as_object().cloned().unwrap_or_default() {
        d[k] = v;
    }
    let p = root.join(format!(".ws07-{name}.json"));
    std::fs::write(&p, d.to_string()).unwrap();
    p
}

fn security_check(r: &Value) -> Value {
    r["checks"]
        .as_array()
        .unwrap()
        .iter()
        .find(|c| c["condition"] == "licence_and_security_satisfied")
        .cloned()
        .unwrap()
}

/// Contract v3 F3:416-423, F4:431; D-0007 consequence 4: a security review is evidence only as a governed review of
/// that tool identity and version; an answered gate raised for exactly that installation lets the governed install
/// proceed, a decline ends it, and nothing else approves it. Tool health failures are durable failure records.
#[test]
fn a_tool_installation_is_approved_only_for_that_installation() {
    let (root, g) = fresh("ws07-tools");
    let te = g.with_role("tooling-engineer");
    // naming an unrelated record is not a security review of this tool
    let unrelated = unrelated_answered_gate(&g);
    let r = te.ok(&[
        "tools",
        "install",
        "--descriptor",
        tool_descriptor(&root, "a", json!({"security_review_record": unrelated}))
            .to_str()
            .unwrap(),
    ]);
    assert_eq!(r["installed"], false, "{r}");
    assert!(
        security_check(&r)["detail"]
            .as_str()
            .unwrap()
            .contains("not a security review report"),
        "{r}"
    );
    // nor is a hand-written report that claims to review it (reports are T2 state; this one no gov operation wrote)
    write_yaml(
        &root,
        "spec/reports/RPT-0901.yaml",
        &json!({"id": "RPT-0901", "type": "report", "title": "security review", "status": "ACTIVE",
        "state_class": "EVIDENCE", "task": "TASK-9001", "session": "S-sec", "role": "security-engineer", "outcome": "success",
        "security_review": {"tool_id": "TOOL-W7", "version": "1.0.0", "verdict": "passed"}}),
    );
    let r = te.ok(&[
        "tools",
        "install",
        "--descriptor",
        tool_descriptor(&root, "b", json!({"security_review_record": "RPT-0901"}))
            .to_str()
            .unwrap(),
    ]);
    assert!(
        security_check(&r)["detail"]
            .as_str()
            .unwrap()
            .contains("T2"),
        "{r}"
    );
    // the failed condition raises a gate for exactly this installation; asking again returns the same gate
    let d = tool_descriptor(&root, "c", json!({}));
    // `--execute` is part of what the transaction's approval binds, so every request of this installation gives it
    let install_c = [
        "tools",
        "install",
        "--descriptor",
        d.to_str().unwrap(),
        "--execute",
    ];
    let r = te.ok(&install_c);
    let gt = r["human_gate"].as_str().unwrap().to_string();
    let gate = yaml(&root, &format!("spec/decisions/{gt}.yaml"));
    assert_eq!(gate["trigger"], "tool_install");
    assert_eq!(gate["subject"]["kind"], "tool-installation");
    assert_eq!(gate["subject"]["sha256"], r["installation_sha256"]);
    // R4-O1: the installation is also a material governance and security change, carried out by a transaction the
    // OS proposed and simulated itself. This gate approves the installation; that transaction's own gate approves
    // the change. Each names the other, and neither answer stands in for the other.
    let cit = r["change_transaction"]["cit"].as_str().unwrap().to_string();
    let cgt = r["change_transaction"]["human_gate"]
        .as_str()
        .unwrap()
        .to_string();
    assert_ne!(cgt, gt);
    assert_eq!(gate["subject"]["change_transaction"]["cit"], json!(cit));
    let before = gate_count(&root);
    let r = te.ok(&install_c);
    assert_eq!(
        (r["human_gate"].as_str(), r["state"].as_str()),
        (Some(gt.as_str()), Some("PENDING")),
        "{r}"
    );
    assert_eq!(gate_count(&root), before);
    // the owner's A on the installation gate alone writes nothing: the change is not approved yet
    crate::ws03::human_decide(&g, &gt, "A");
    let r = te.ok(&install_c);
    assert_eq!(r["installed"], false, "{r}");
    assert_eq!(r["human_gate"], json!(cgt), "{r}");
    assert!(
        !root.join("governance/project/tools/TOOL-W7.yaml").exists(),
        "the descriptor was written before the change was approved"
    );
    // both answered: the same install proceeds, written by the transaction's execution (citing the gate is optional)
    crate::ws03::human_decide(&g, &cgt, "A");
    let r = te.ok(&install_c);
    assert_eq!(r["installed"], true, "{r}");
    assert_eq!(r["approval"]["mode"], "human_gate");
    assert_eq!(r["approval"]["gate"], json!(gt));
    assert_eq!(r["change_transaction"]["cit_status"], "COMMITTED", "{r}");
    let rec = yaml(&root, "governance/project/tools/TOOL-W7.yaml");
    assert_eq!(rec["approval"]["gate"], json!(gt));
    assert_eq!(rec["approval"]["change_transaction"], json!(cit));
    assert_eq!(rec["installation_sha256"], r["installation_sha256"]);
    // a changed installation is a new request; declining it ends it
    let d2 = tool_descriptor(&root, "d", json!({"version_pin": "1.0.1"}));
    let r = te.ok(&["tools", "install", "--descriptor", d2.to_str().unwrap()]);
    assert_eq!(r["installed"], false);
    let gt2 = r["human_gate"].as_str().unwrap().to_string();
    assert_ne!(gt2, gt);
    crate::ws03::human_decide(&g, &gt2, "B");
    let before = gate_count(&root);
    let r = te.ok(&["tools", "install", "--descriptor", d2.to_str().unwrap()]);
    assert_eq!(
        (r["installed"].as_bool(), r["declined"].as_bool()),
        (Some(false), Some(true)),
        "{r}"
    );
    assert_eq!(
        gate_count(&root),
        before,
        "a declined installation raised a new gate"
    );
    // a gate answered for anything else, cited in the descriptor, never approves an installation
    let d3 = tool_descriptor(
        &root,
        "e",
        json!({"tool_id": "TOOL-W7B", "approval_gate": unrelated}),
    );
    let r = te.ok(&["tools", "install", "--descriptor", d3.to_str().unwrap()]);
    assert_eq!(r["installed"], false, "{r}");
    assert!(
        r["gates_not_honoured"]
            .to_string()
            .contains("GATE_MISMATCH"),
        "{r}"
    );
    // WS-6 IP-3: a failing tool health check leaves a durable tool-failure record
    write_yaml(
        &root,
        "governance/project/tools/TOOL-BROKEN.yaml",
        &json!({"tool_id": "TOOL-BROKEN-001", "name": "broken", "type": "CLI",
        "capabilities": ["lint"], "status": "active", "version": "1", "approved_roles": ["all"],
        "health_check": {"kind": "command", "command": ["false"], "expect_exit": 0}, "required_permission_classes": []}),
    );
    let h = g.ok(&["tools", "health"]);
    let row = h
        .as_array()
        .unwrap()
        .iter()
        .find(|x| x["tool_id"] == "TOOL-BROKEN-001")
        .cloned()
        .unwrap();
    assert_eq!(row["ok"], false);
    assert!(
        matches!(
            row["failure_memory"]["status"].as_str(),
            Some("recorded") | Some("existing")
        ),
        "{row}"
    );
    let path = row["failure_memory"]["path"].as_str().unwrap();
    assert!(read(&root, path).contains("TOOL-BROKEN-001"));
}

// ============================================================================================ round 3 (P2-AR-0038)

fn invoke_ok(g: &Gov, id: &str) -> Value {
    g.ok(&[
        "capabilities",
        "invoke",
        "--plugin",
        id,
        "--inputs",
        "{\"texts\": []}",
    ])
}

fn set_old_mtime(path: &Path) {
    let old = std::time::SystemTime::now() - std::time::Duration::from_secs(3600);
    std::fs::File::options()
        .write(true)
        .open(path)
        .unwrap()
        .set_modified(old)
        .unwrap();
}

/// BC-P2-31 (Contract v3 B1:188, B3:202, D6:352; D-0007 T2; WS-6 IP-R2-9, A0-D6-02): the OS-written plugin registry
/// lives where deleting the regenerable views cannot lose it. A registry an earlier release kept among those views
/// is still honoured — entry by entry, only where its seal verifies — until the next registry write moves it;
/// reading never moves it; moving seals nothing (a forged entry stays refused, and the OS does not seal the document
/// over it); once moved, a file at the legacy location is never read and is reported; a clone carries the registry
/// where it belongs and another machine's seals are never honoured there.
#[test]
fn the_plugin_registry_survives_deleting_the_generated_views_and_moves_only_as_written() {
    let (root, g) = fresh("ws07-r3-move");
    let te = g.with_role("tooling-engineer");
    let marker = root.join("ws07-marker.txt");
    marker_plugin(&root, "tools/p.sh", &marker, "");
    write_yaml(
        &root,
        "governance/project/plugins/p1.yaml",
        &json!({"plugin_id": "p1", "capability": "embed", "version": "1", "command": ["sh", "tools/p.sh"]}),
    );
    register_approved(&te, &root.join("governance/project/plugins/p1.yaml"));
    // 1. written where it belongs, sealed; nothing among the generated views; not reported as misplaced
    assert!(exists(&root, REGISTRY) && !exists(&root, LEGACY_REGISTRY));
    assert!(json(&root, REGISTRY)["os_binding"]["mac"].is_string());
    assert!(gov_runtime::paths::misplaced_os_state(&root)
        .iter()
        .all(|m| m["store"] != "plugin-registry"));
    // 2. deleting the whole generated-views directory (framework §19) keeps the registration
    std::fs::remove_dir_all(root.join("governance/generated")).unwrap();
    invoke_ok(&te, "p1");
    assert_eq!(runs(&marker), 1);
    // 3. a registry an earlier release kept at the legacy location is honoured as it stands, and reading it — a
    //    listing, the registry view, doctor, the plugin_governance audit, an execution — never moves it
    std::fs::create_dir_all(root.join("governance/generated")).unwrap();
    std::fs::rename(root.join(REGISTRY), root.join(LEGACY_REGISTRY)).unwrap();
    let legacy_bytes = std::fs::read(root.join(LEGACY_REGISTRY)).unwrap();
    invoke_ok(&te, "p1");
    assert!(te.ok(&["plugins", "list"])["usable"]
        .to_string()
        .contains("p1"));
    te.ok(&["plugins", "registry"]);
    doctor_check(&g, "D028");
    g.run(&["audit", "--no-persist", "--family", "plugin_governance"]);
    assert!(!exists(&root, REGISTRY), "a read moved the registry");
    assert_eq!(
        std::fs::read(root.join(LEGACY_REGISTRY)).unwrap(),
        legacy_bytes
    );
    assert!(gov_runtime::paths::misplaced_os_state(&root)
        .iter()
        .any(|m| m["store"] == "plugin-registry"));
    // a worker adds an entry to the legacy registry: not honoured there
    marker_plugin(&root, "tools/n.sh", &marker, "");
    write_yaml(
        &root,
        "governance/project/plugins/n1.yaml",
        &json!({"plugin_id": "n1", "capability": "embed", "version": "1", "command": ["sh", "tools/n.sh"]}),
    );
    let dsha = gov_runtime::util::sha256_hex(
        &std::fs::read(root.join("governance/project/plugins/n1.yaml")).unwrap(),
    );
    let mut reg = json(&root, LEGACY_REGISTRY);
    reg["plugins"]["n1"] = json!({"plugin_id": "n1", "capability": "embed", "version": "1", "descriptor_sha256": dsha,
        "approved_roles": ["all"], "registered_by_role": "human", "registered_at": "2026-09-19T00:00:00Z", "method": "gov plugins register"});
    write_json(&root, LEGACY_REGISTRY, &reg);
    assert_eq!(
        invoke(&te, "n1").error_code(),
        "PLUGIN_REGISTRATION_UNBOUND"
    );
    // 4. the next registry write moves it, bytes as they are: p1 is still honoured, n1 still is not, and the OS
    //    does not seal the document over an entry it did not write
    marker_plugin(&root, "tools/q.sh", &marker, "");
    write_yaml(
        &root,
        "governance/project/plugins/q1.yaml",
        &json!({"plugin_id": "q1", "capability": "embed", "version": "1", "command": ["sh", "tools/q.sh"]}),
    );
    register_approved(&te, &root.join("governance/project/plugins/q1.yaml"));
    assert!(exists(&root, REGISTRY) && !exists(&root, LEGACY_REGISTRY));
    let moved = json(&root, REGISTRY);
    assert!(
        moved["plugins"]["n1"].is_object() && moved["plugins"]["q1"].is_object(),
        "{moved}"
    );
    assert!(
        moved["os_binding"].is_null(),
        "the OS sealed the registry document over a forged entry: {moved}"
    );
    invoke_ok(&te, "p1");
    invoke_ok(&te, "q1");
    assert_eq!(
        invoke(&te, "n1").error_code(),
        "PLUGIN_REGISTRATION_UNBOUND"
    );
    // removing the forged entry through gov lets the OS seal the document again
    te.ok(&["plugins", "unregister", "n1"]);
    assert!(json(&root, REGISTRY)["os_binding"]["mac"].is_string());
    // 5. after the move, a registry at the legacy location is never read (this one would unregister everything),
    //    is reported, and a registry write neither reads, overwrites nor deletes it
    write_json(
        &root,
        LEGACY_REGISTRY,
        &json!({"schema_version": "1.1.0", "plugins": {}}),
    );
    invoke_ok(&te, "p1");
    let (ok28, msg28) = doctor_check(&g, "D028");
    assert!(!ok28 && msg28.contains("legacy location"), "{msg28}");
    te.ok(&["plugins", "unregister", "q1"]);
    assert_eq!(json(&root, LEGACY_REGISTRY)["plugins"], json!({}));
    let now = json(&root, REGISTRY);
    assert!(now["plugins"]["p1"].is_object() && now["plugins"]["q1"].is_null());
    assert_eq!(runs(&marker), 5, "n1 ran");
    // 6. a clone carries the tracked registry where it belongs; this machine's seals are not the clone machine's
    std::fs::remove_file(root.join(LEGACY_REGISTRY)).unwrap();
    git_commit_all(&root, "registry where it belongs");
    let b = tmp("ws07-r3-move-clone");
    let (code, out) = git(
        &root,
        &[
            "clone",
            "-q",
            root.to_str().unwrap(),
            b.join("repo").to_str().unwrap(),
        ],
    );
    assert_eq!(code, 0, "{out}");
    let broot = b.join("repo");
    assert!(exists(&broot, REGISTRY));
    let gb = Gov::new(&broot, "S-ws7-b").with_role("tooling-engineer");
    assert_eq!(
        invoke(&gb, "p1").error_code(),
        "PLUGIN_REGISTRATION_UNBOUND"
    );
    assert_eq!(runs(&marker), 5);
}

/// IP-R2-13 (BC-P2-30 with BC-P2-40): an embed plugin declares the model and inference-runtime artefacts it loads
/// from outside its own directory. The kernel schema admits the declaration; the registration gate shows those
/// artefacts and the registration binds their bytes (roles `model` / `runtime`); a changed model or runtime byte stops
/// the plugin until a new approval and doctor names the file; a declared artefact that does not exist is refused
/// before any gate is raised.
#[test]
fn declared_model_and_runtime_artefacts_are_part_of_what_the_owner_approves() {
    let (root, g) = fresh("ws07-r3-model");
    let te = g.with_role("tooling-engineer");
    let marker = root.join("ws07-marker.txt");
    let cache = tmp("ws07-r3-model-cache"); // outside the repository: a model cache, a runtime installation
    std::fs::create_dir_all(cache.join("model")).unwrap();
    std::fs::write(cache.join("model/weights.bin"), [0u8, 1, 2, 3]).unwrap();
    std::fs::write(cache.join("model/tokenizer.json"), "{}").unwrap();
    std::fs::write(cache.join("libinfer.so"), "runtime").unwrap();
    marker_plugin(&root, "tools/m.sh", &marker, "");
    let df = root.join("governance/project/plugins/m1.yaml");
    write_yaml(
        &root,
        "governance/project/plugins/m1.yaml",
        &json!({"plugin_id": "m1", "capability": "embed", "version": "1", "command": ["sh", "tools/m.sh"],
            "model": {"id": "mini-embed", "revision": "2026-09", "artefacts": [cache.join("model").to_str().unwrap()]},
            "runtime": {"id": "infer-1", "artefacts": [cache.join("libinfer.so").to_str().unwrap()]}}),
    );
    // the kernel schema admits the declaration (it rejected any field it did not know)
    let l = te.ok(&["plugins", "list"]);
    assert!(!l["rejected"].to_string().contains("m1"), "{l}");
    // the gate shows what the plugin loads; the registration binds it
    let r = te.ok(&["plugins", "register", "--descriptor", df.to_str().unwrap()]);
    let gate = r["human_gate"].as_str().unwrap().to_string();
    let gy = yaml(&root, &format!("spec/decisions/{gate}.yaml"));
    let impact = gy["impact"].as_str().unwrap_or("");
    assert!(
        impact.contains("weights.bin") && impact.contains("libinfer.so"),
        "{impact}"
    );
    crate::ws03::human_decide(&g, &gate, "A");
    // INT3-O1 (round 4): the change transaction the OS proposed for the registration is approved through its own gate
    crate::ws03::human_decide(
        &g,
        r["change_transaction"]["human_gate"].as_str().unwrap(),
        "A",
    );
    let r = te.ok(&["plugins", "register", "--descriptor", df.to_str().unwrap()]);
    assert_eq!(r["registered"], true, "{r}");
    let bound = r["registry_entry"]["implementation"].to_string();
    for (role, file) in [
        ("model", "weights.bin"),
        ("model", "tokenizer.json"),
        ("runtime", "libinfer.so"),
    ] {
        assert!(
            r["registry_entry"]["implementation"]
                .as_array()
                .unwrap()
                .iter()
                .any(|f| f["role"] == role && f["path"].as_str().unwrap().ends_with(file)),
            "{role} {file} not bound: {bound}"
        );
    }
    invoke_ok(&te, "m1");
    assert_eq!(runs(&marker), 1);
    // a changed model byte stops the plugin, and doctor names the file
    std::fs::write(cache.join("model/weights.bin"), [0u8, 1, 2, 4]).unwrap();
    let e = invoke(&te, "m1");
    assert_eq!(e.error_code(), "PLUGIN_PIN_MISMATCH", "{}", e.envelope);
    assert!(e.envelope.to_string().contains("weights.bin"));
    let (ok28, msg28) = doctor_check(&g, "D028");
    assert!(!ok28 && msg28.contains("weights.bin"), "{msg28}");
    // the approved bytes run again; a changed runtime byte stops it as well
    std::fs::write(cache.join("model/weights.bin"), [0u8, 1, 2, 3]).unwrap();
    invoke_ok(&te, "m1");
    std::fs::write(cache.join("libinfer.so"), "runtimf").unwrap();
    assert_eq!(invoke(&te, "m1").error_code(), "PLUGIN_PIN_MISMATCH");
    assert_eq!(runs(&marker), 2);
    // a declared model artefact that does not exist is refused before any gate
    marker_plugin(&root, "tools/x.sh", &marker, "");
    write_yaml(
        &root,
        "governance/project/plugins/x1.yaml",
        &json!({"plugin_id": "x1", "capability": "embed", "version": "1", "command": ["sh", "tools/x.sh"],
            "model": {"artefacts": ["models/absent.bin"]}}),
    );
    let before = gate_count(&root);
    let e = te.err(&[
        "plugins",
        "register",
        "--descriptor",
        root.join("governance/project/plugins/x1.yaml")
            .to_str()
            .unwrap(),
    ]);
    assert_eq!(
        e.error_code(),
        "PLUGIN_IMPLEMENTATION_UNRESOLVED",
        "{}",
        e.envelope
    );
    assert!(e.envelope.to_string().contains("model artefact"));
    assert_eq!(gate_count(&root), before);
}

/// BC-P2-40, WS-7 round 3 (authorisation no longer re-hashes unchanged files, and the pin is not weakened): the
/// digest labelling the running `gov` binary is kept in the machine's protected state, so an OS capability-server
/// plugin does not re-read a large binary in every `gov` process; the digest of a bound plugin file never leaves the
/// process that computed it — nothing in any store, not even a forged entry naming the approved digest, makes changed
/// bytes run. A same-size rewrite with the modification time put back, a change to the file a bound symlink points
/// at, and a file replaced by another are all refused.
#[test]
fn a_cached_pin_never_approves_changed_bytes() {
    let (root, g) = fresh("ws07-r3-cache");
    let te = g.with_role("tooling-engineer");
    let marker = root.join("ws07-marker.txt");
    let outside = tmp("ws07-r3-cache-lib");
    std::fs::write(outside.join("helper.sh"), "HELPER=1\n").unwrap();
    std::fs::create_dir_all(root.join("tools/lib")).unwrap();
    std::os::unix::fs::symlink(outside.join("helper.sh"), root.join("tools/lib/helper.sh"))
        .unwrap();
    marker_plugin(
        &root,
        "tools/c.sh",
        &marker,
        ". \"$(dirname \"$0\")/lib/helper.sh\"",
    );
    write_yaml(
        &root,
        "governance/project/plugins/c1.yaml",
        &json!({"plugin_id": "c1", "capability": "embed", "version": "1", "command": ["sh", "tools/c.sh"], "implementation": ["tools/lib"]}),
    );
    // the OS's own capability server: its program is the running gov binary
    let gov = gov_bin().to_string_lossy().to_string();
    write_yaml(
        &root,
        "governance/project/plugins/os-embed.yaml",
        &json!({"plugin_id": "os-embed", "capability": "embed", "version": "1", "languages": [],
            "command": [gov, "capabilities", "serve-embed", "--id", "os-embed"]}),
    );
    // every bound file is quiescent before it is approved (the conditions under which a digest may be reused)
    set_old_mtime(&root.join("tools/c.sh"));
    set_old_mtime(&outside.join("helper.sh"));
    std::thread::sleep(
        gov_runtime::capabilities::pincache::QUIESCENCE + std::time::Duration::from_millis(300),
    );
    register_approved(&te, &root.join("governance/project/plugins/c1.yaml"));
    invoke_ok(&te, "c1");
    invoke_ok(&te, "os-embed");
    assert_eq!(runs(&marker), 1);
    let store = machine_state_dir(&root).join("plugin-pin-cache/cache.json");
    let stored = std::fs::read_to_string(&store).unwrap_or_default();
    let gov_c = std::fs::canonicalize(gov_bin()).unwrap();
    assert!(
        stored.contains(&*gov_c.to_string_lossy()),
        "the running gov binary's digest was not kept in the machine's protected state ({}): {stored}",
        store.display()
    );
    assert!(
        !stored.contains("c.sh") && !stored.contains("helper.sh"),
        "a bound plugin file's digest left the process: {stored}"
    );
    fn mentions(dir: &Path, needle: &str) -> bool {
        std::fs::read_dir(dir)
            .map(|rd| {
                rd.flatten().any(|e| {
                    e.file_name().to_string_lossy().contains(needle)
                        || (e.file_type().map(|t| t.is_dir()).unwrap_or(false)
                            && mentions(&e.path(), needle))
                })
            })
            .unwrap_or(false)
    }
    assert!(
        !mentions(&root, "plugin-pin-cache"),
        "a pin cache inside the repository"
    );
    // 1. same size, modification time put back
    let original = read(&root, "tools/c.sh");
    let approved = gov_runtime::util::sha256_hex(original.as_bytes());
    let tampered = original.replace("EXECUTED", "EXECUTEX");
    assert_eq!(tampered.len(), original.len());
    write(&root, "tools/c.sh", &tampered);
    set_old_mtime(&root.join("tools/c.sh"));
    assert_eq!(invoke(&te, "c1").error_code(), "PLUGIN_PIN_MISMATCH");
    // ... even when the machine's store is made to name the approved digest under the tampered file's present key
    // (what a process able to write the machine state could plant): no store supplies a bound file's digest
    {
        use std::os::unix::fs::MetadataExt;
        let m = std::fs::metadata(root.join("tools/c.sh")).unwrap();
        let key = json!({"dev": m.dev().to_string(), "ino": m.ino().to_string(), "size": m.size().to_string(),
            "mtime_ns": (m.mtime() * 1_000_000_000 + m.mtime_nsec()).to_string(),
            "ctime_ns": (m.ctime() * 1_000_000_000 + m.ctime_nsec()).to_string(), "mode": m.mode(), "uid": m.uid()});
        let mut doc: Value = serde_json::from_str(&stored).unwrap_or(json!({"entries": {}}));
        doc["entries"][format!("{}:{}", m.dev(), m.ino())] = json!({"key": key, "sha256": approved,
            "path": root.join("tools/c.sh").to_string_lossy(), "at": "2026-09-19T00:00:00Z"});
        std::fs::write(&store, doc.to_string()).unwrap();
    }
    assert_eq!(invoke(&te, "c1").error_code(), "PLUGIN_PIN_MISMATCH");
    write(&root, "tools/c.sh", &original);
    set_old_mtime(&root.join("tools/c.sh"));
    invoke_ok(&te, "c1");
    // 2. the file a bound symlink points at (outside the repository) changes
    std::fs::write(outside.join("helper.sh"), "HELPER=2\n").unwrap();
    set_old_mtime(&outside.join("helper.sh"));
    let e = invoke(&te, "c1");
    assert_eq!(e.error_code(), "PLUGIN_PIN_MISMATCH", "{}", e.envelope);
    std::fs::write(outside.join("helper.sh"), "HELPER=1\n").unwrap();
    invoke_ok(&te, "c1");
    // 3. the file is replaced by another one (renamed over it)
    write(&root, "tools/c.sh.new", &tampered);
    std::fs::rename(root.join("tools/c.sh.new"), root.join("tools/c.sh")).unwrap();
    set_old_mtime(&root.join("tools/c.sh"));
    assert_eq!(invoke(&te, "c1").error_code(), "PLUGIN_PIN_MISMATCH");
    assert_eq!(runs(&marker), 3, "changed bytes ran");
}

/// IP-W7-1 (BC-P2-41 with WS-5's sealed close reports; Contract v3 F3:416-423, F4:431): the report that closes a
/// security-class task — written by the OS at close (T2-sealed), by another session and role, naming exactly this
/// tool and version — is the governed security review that lets the installation proceed with no owner gate. It
/// does not review another version, and a review the installer's own role wrote does not count.
#[test]
fn a_governed_security_review_by_another_role_lets_the_installation_proceed() {
    let (root, g) = fresh("ws07-r3-review");
    let te = g.with_role("tooling-engineer");
    let sec = g.with_session("S-sec").with_role("security-engineer");
    g.ok(&["rebuild-memory"]);
    let t = g.ok(&[
        "task",
        "create",
        "--class",
        "security",
        "--objective",
        "Security review of TOOL-W7 1.0.0",
        "--status",
        "READY",
    ])["id"]
        .as_str()
        .unwrap()
        .to_string();
    sec.ok(&["task", "claim", &t]);
    sec.ok(&["rebuild-memory", "--incremental"]);
    let rep = crate::ws05::receipt_with(
        &sec,
        &root,
        &t,
        "ws07-sec-review",
        "reviewed TOOL-W7 1.0.0",
        &[],
        "not_applicable_with_reason",
        json!({"security_review": {"tool_id": "TOOL-W7", "version": "1.0.0", "verdict": "passed"}}),
    );
    let c = sec.ok(&["task", "close", &t, "--report", &rep]);
    let rpt = c["report"].as_str().unwrap().to_string();
    let rel = format!("spec/reports/{rpt}.yaml");
    let ry = yaml(&root, &rel);
    assert!(ry["os_binding"]["mac"].is_string(), "{ry}");
    assert_eq!(ry["security_review"]["verdict"], "passed");
    // installing exactly that tool and version, citing the review: no gate is raised FOR THE INSTALLATION — the
    // governed review stands in for the owner's answer to it (IP-W7-1, BC-P2-41).
    //
    // R4-O1 (round 4): the installation is also a material governance and security change, so it is carried out by
    // the change transaction the OS proposes for it, and under CHANGE_POLICY (`human_gate_triggers` includes
    // `governance_change`) that transaction's own gate is required, as it is for every other governance change.
    // That gate is the only one raised here, and it approves the change, not the installation. Whether the
    // review-evidenced path should keep completing with NO gate at all is an owner decision P2-AR-0053 states and
    // does not take (its report, item 1).
    let rvd = tool_descriptor(&root, "rv", json!({"security_review_record": rpt}));
    let install_rv = ["tools", "install", "--descriptor", rvd.to_str().unwrap()];
    let before = gate_count(&root);
    let r = te.ok(&install_rv);
    assert_eq!(security_check(&r)["ok"], true, "{r}");
    let cit = r["change_transaction"]["cit"].as_str().unwrap().to_string();
    let cg = r["human_gate"].as_str().unwrap().to_string();
    assert_eq!(
        r["change_transaction"]["human_gate"],
        json!(cg),
        "the only gate is the transaction's own: {r}"
    );
    assert_eq!(
        gate_count(&root),
        before + 1,
        "a gate was raised for the installation subject too: {r}"
    );
    assert_eq!(
        yaml(&root, &format!("spec/decisions/{cg}.yaml"))["cit"],
        json!(cit)
    );
    crate::ws03::human_decide(&g, &cg, "A");
    let r = te.ok(&install_rv);
    assert_eq!(r["installed"], true, "{r}");
    assert_eq!(r["approval"]["mode"], "autonomous", "{r}");
    assert_eq!(r["change_transaction"]["cit_status"], "COMMITTED", "{r}");
    // the review does not cover another version
    let r = te.ok(&[
        "tools",
        "install",
        "--descriptor",
        tool_descriptor(
            &root,
            "rv2",
            json!({"security_review_record": rpt, "tool_id": "TOOL-W7V", "version_pin": "1.0.1"}),
        )
        .to_str()
        .unwrap(),
    ]);
    assert_eq!(security_check(&r)["ok"], false, "{r}");
    assert_eq!(r["installed"], false, "{r}");
    // a review the installing role wrote is self-attestation
    let r = sec.ok(&[
        "tools",
        "install",
        "--descriptor",
        tool_descriptor(
            &root,
            "rv3",
            json!({"security_review_record": rpt, "tool_id": "TOOL-W7"}),
        )
        .to_str()
        .unwrap(),
    ]);
    assert_eq!(security_check(&r)["ok"], false, "{r}");
    assert!(
        security_check(&r)["detail"]
            .as_str()
            .unwrap()
            .contains("self-attested"),
        "{r}"
    );
}
