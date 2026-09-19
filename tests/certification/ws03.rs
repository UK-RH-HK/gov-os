//! Repair iteration 1, WS-3 (P2-AR-0016): identity, authority, Human Decision Gates and policy precedence.
//!
//! Builder regression evidence (Contract v3 O3), not acceptance evidence. The helpers at the top are the test
//! harness's stand-in for the product owner: `gov` holds no signing key, so the owner's `human-gate` signatures are
//! produced here with a **published test seed** (TEST MATERIAL ONLY, like `srr_material`).
#![allow(dead_code)]
use crate::common::*;
use crate::srr_material::{envelope, far_future, key, key_entry, root_doc, Publisher, TestKey};
use serde_json::{json, Value};
use std::path::{Path, PathBuf};

/// The test owner's `human-gate` key. NOT A PRODUCTION KEY: derived from a published seed.
pub fn owner() -> TestKey {
    key(0x5a)
}

fn scratch_file(g: &Gov, name: &str, text: &str) -> PathBuf {
    let dir = g.root.parent().unwrap().join(format!(
        "hc-{}",
        gov_runtime::util::sha256_text(&g.root.display().to_string())[..8].to_string()
    ));
    std::fs::create_dir_all(&dir).unwrap();
    let p = dir.join(name);
    std::fs::write(&p, text).unwrap();
    p
}

/// A scratch directory beside the project, unique to this project root (never inside it).
pub fn scratch_dir(g: &Gov, name: &str) -> PathBuf {
    let d = scratch_file(g, ".scratch", "").parent().unwrap().join(name);
    std::fs::create_dir_all(&d).unwrap();
    d
}

/// **The authenticated human channel on this simulated machine** (idempotent).
///
/// P2-ADJ-0001 (following OWNER-DECISION-P2-0002 "provision, then work"): human answers derive only from a provisioned
/// Signed Release Root's `human-gate` delegation; the standalone anchor is off. A machine that already has that
/// channel (e.g. a harness-provisioned root delegating `human-gate` to [`owner`]) is used as it is. On a machine that
/// is not provisioned yet, this does what the administrator of a dev/test machine does: provision a throw-away root
/// ([`throwaway_root`]) that delegates `human-gate` to the test owner's key, then re-verify the kernel this machine
/// installed while unprovisioned against a signed release of the same payload ([`reanchor_installed_kernel`]), so
/// governed work continues on a kernel this machine has verified. A provisioned root that delegates no `human-gate`
/// role is a test set-up error.
pub fn human_channel(g: &Gov) {
    let st = g.run(&["trust", "human-channel"]);
    if st.ok() && st.result()["available"] == true {
        return;
    }
    let posture = g.run(&["trust", "status"]).result()["posture"].clone();
    assert_eq!(
        posture, "UNPROVISIONED",
        "this machine holds a trust root without a `human-gate` delegation to the test owner: provision a root that \
         delegates it (ws08 `provision_with_human_gate`, ws03 `throwaway_root`) — {}",
        st.envelope
    );
    let f = throwaway_root(g);
    g.ok(&["trust", "provision", "--anchor", f.to_str().unwrap()]);
    if exists(&g.root, "governance/framework.lock") {
        reanchor_installed_kernel(g);
    }
    let st = g.ok(&["trust", "human-channel"]);
    assert_eq!(st["available"], true, "{st}");
    assert_eq!(st["anchor"]["source"], "srr-root", "{st}");
}

/// A throw-away Signed Release Root for a dev/test machine (TEST MATERIAL ONLY: the `srr_material` Publisher's
/// published-seed keys at 2-of-3, plus the test owner's `human-gate` key). Written outside the project, as
/// administrator-domain material.
pub fn throwaway_root(g: &Gov) -> PathBuf {
    let p = Publisher::new();
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
    let o = owner();
    let (kid, entry) = key_entry(&o);
    doc["keys"][kid.as_str()] = entry;
    doc["roles"]["human-gate"] = json!({"keyids": [o.keyid.clone()], "threshold": 1});
    scratch_file(
        g,
        "throwaway-root-1.json",
        &envelope(&doc, &[&p.root_a, &p.root_b]),
    )
}

/// Provision this simulated machine with the throw-away root ([`throwaway_root`]) before anything is installed —
/// the documented first-run path "provision, then install" (OWNER-DECISION-P2-0002 req. 3).
pub fn provision(g: &Gov) {
    g.ok(&[
        "trust",
        "provision",
        "--anchor",
        throwaway_root(g).to_str().unwrap(),
    ]);
}

/// A signed release of the kernel source `src` at `<dir>/kernel`, published with the throw-away root's release keys
/// (TEST MATERIAL ONLY). On a provisioned machine every kernel ingress is a signed release; the metadata version
/// follows `sequence`, so releases published for one machine in sequence order stay monotonic.
pub fn signed_release(src: &Path, dir: &Path, sequence: u64) -> PathBuf {
    std::fs::create_dir_all(dir).unwrap();
    gov_runtime::kernel::stage_payload(src, &dir.join("kernel")).unwrap();
    Publisher::new().publish(dir, sequence, sequence, "stable", &far_future(), "", 0);
    dir.join("kernel")
}

/// The owner's break-glass authorisation (the throw-away root's `recovery` key) to restore `release_kernel` below
/// floor, placed in this machine's break-glass inbox (OWNER-DECISION-0006: below-floor restoration needs it).
pub fn break_glass_for(g: &Gov, release_kernel: &Path, nonce: &str) {
    let inbox = PathBuf::from(g.ok(&["trust", "break-glass"])["inbox"].as_str().unwrap());
    let mid = g.ok(&["trust", "status"])["machine_id"]
        .as_str()
        .unwrap()
        .to_string();
    let (_, payload_hash, kmh, ver) = crate::srr_material::measure(release_kernel);
    let tok = crate::srr_material::break_glass_doc(
        &mid,
        nonce,
        "restore the previous release (certification)",
        &far_future(),
        &ver,
        &payload_hash,
        &kmh,
    );
    std::fs::create_dir_all(&inbox).unwrap();
    std::fs::write(
        inbox.join(format!("{nonce}.json")),
        envelope(&tok, &[&Publisher::new().recovery]),
    )
    .unwrap();
}

/// On a machine provisioned after the project was installed, the installed kernel has never been verified here
/// (`KERNEL_UNANCHORED`): publish a signed release of exactly the payload framework.lock pins (the kernel compiled
/// from this repository, a shipped release, the synthetic previous release, or the installed copy — whichever
/// measures to the pin) with the throw-away root's release keys, and reinstall it through the product's verifier
/// (the declared administrator role performs the reinstall).
pub fn reanchor_installed_kernel(g: &Gov) {
    let pin = yaml(&g.root, "governance/framework.lock")["release_hash"]
        .as_str()
        .unwrap()
        .to_string();
    let mut candidates = vec![
        canonical_root().join("framework"),
        canonical_root().join("fixtures/update/previous-release/4.1.1"),
        g.root.join("governance/kernel"),
    ];
    for v in ["4.1.2", "4.1.3", "4.1.4", "4.1.5"] {
        candidates.push(canonical_root().join(format!("release/releases/{v}/kernel")));
    }
    let src = candidates
        .into_iter()
        .find(|c| c.exists() && crate::srr_material::measure(c).1 == pin)
        .unwrap_or_else(|| panic!("no known kernel source measures to the pinned payload {pin}"));
    let rel = scratch_file(g, "reanchor.marker", "")
        .parent()
        .unwrap()
        .join(format!("reanchor-{}", gov_runtime::util::short_uuid()));
    gov_runtime::kernel::stage_payload(&src, &rel.join("kernel")).unwrap();
    Publisher::new().publish(&rel, 1, 1, "stable", &far_future(), "", 0);
    g.with_role("orchestrator").ok(&[
        "kernel",
        "reinstall",
        "--source",
        rel.join("kernel").to_str().unwrap(),
    ]);
    assert_eq!(g.ok(&["kernel", "trust"])["verified"], true);
}

/// A `human-channel-anchor` document installing `installed`'s public key, signed by `signer`.
fn anchor_doc(installed: &TestKey, signer: &TestKey) -> String {
    let (kid, entry) = key_entry(installed);
    let signed = json!({"_type": "human-channel-anchor", "spec_version": "srr/1", "product": gov_runtime::FRAMEWORK_NAME,
        "version": 1, "expires": far_future(), "owner": "certification owner (published test seed)", "threshold": 1,
        "keys": {kid: entry}});
    envelope(&signed, &[signer])
}

/// Render the gate (the OS records what it showed) and return (gate_instance, package_sha256).
pub fn render(g: &Gov, gate: &str) -> (String, String) {
    let r = g.ok(&["gate", "present", gate]);
    (
        r["gate"]["gate_instance"].as_str().unwrap().to_string(),
        r["gate"]["package_sha256"].as_str().unwrap().to_string(),
    )
}

/// An owner-signed document for `gate` (answer when `option` is Some, receipt otherwise).
pub fn signed_doc(
    gate: &str,
    instance: &str,
    sha: &str,
    option: Option<&str>,
    nonce: &str,
    signer: &TestKey,
    expires: &str,
) -> String {
    let mut s = json!({"_type": if option.is_some() { "human-gate-answer" } else { "human-gate-receipt" },
        "spec_version": "srr/1", "product": gov_runtime::FRAMEWORK_NAME, "gate": gate, "gate_instance": instance,
        "package_sha256": sha, "nonce": nonce, "issued": "2026-09-19T00:00:00Z", "expires": expires});
    match option {
        Some(o) => {
            s["option"] = json!(o);
            s["answered_by"] = json!("certification owner");
            s["rationale"] = json!("owner decision (test)");
        }
        None => s["acknowledged_by"] = json!("certification owner"),
    }
    envelope(&s, &[signer])
}

/// **The human answers `gate` with `option`** — through the only channel that can produce a human answer: the owner
/// signs the exact rendered package and the relaying role applies the document. Returns the `decide` result.
pub fn human_decide(g: &Gov, gate: &str, option: &str) -> Value {
    human_channel(g);
    let (inst, sha) = render(g, gate);
    let nonce = format!("n-{gate}-{}", gov_runtime::util::short_uuid());
    let f = scratch_file(
        g,
        &format!("{gate}-{option}-{nonce}.json"),
        &signed_doc(
            gate,
            &inst,
            &sha,
            Some(option),
            &nonce,
            &owner(),
            &far_future(),
        ),
    );
    g.ok(&[
        "decide",
        gate,
        "--option",
        option,
        "--answer-file",
        f.to_str().unwrap(),
    ])
}

/// The human acknowledges that the rendered package reached them (owner-signed receipt).
pub fn human_receipt(g: &Gov, gate: &str) -> Value {
    human_channel(g);
    let (inst, sha) = render(g, gate);
    let nonce = format!("r-{gate}-{}", gov_runtime::util::short_uuid());
    let f = scratch_file(
        g,
        &format!("{gate}-receipt-{nonce}.json"),
        &signed_doc(gate, &inst, &sha, None, &nonce, &owner(), &far_future()),
    );
    g.ok(&[
        "gate",
        "present",
        gate,
        "--receipt-file",
        f.to_str().unwrap(),
    ])
}

/// A complete decision package (BC-P2-49) with `extra` merged over it, as a `--fields` JSON string.
pub fn package(extra: Value) -> String {
    let mut v = json!({"why_now": "the next task depends on this choice", "current_state": "two options analysed, none chosen",
        "options": [{"id": "A", "description": "proceed as proposed"}, {"id": "B", "description": "do not proceed"}],
        "impact": "the dependent tasks are re-planned", "reversibility": "reversible: the change can be rolled back",
        "cost_rework": "one task of rework if reversed", "recommendation": "A", "confidence": 0.6, "impact_radius": "R3"});
    for (k, x) in extra.as_object().cloned().unwrap_or_default() {
        v[k] = x;
    }
    v.to_string()
}

fn fresh(tag: &str) -> (PathBuf, Gov) {
    let (root, g) = setup_fixture("greenfield", tag, "S-ws3");
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        tag,
        "--alias",
        &format!("a-{tag}"),
    ]);
    git_commit_all(&root, "after init");
    (root, g)
}

/// [`fresh`] on a machine with NO Signed Release Root — for the scenario about the standalone human-channel anchor,
/// which exists only on such a machine (a provisioned machine's channel is its root's `human-gate` delegation). The
/// install is the binary's own embedded payload, the one kernel OWNER-DECISION-P2-0002 lets such a machine admit
/// (as a marked bootstrap installation).
fn fresh_unprovisioned(tag: &str) -> (PathBuf, Gov) {
    let (root, g) = setup_fixture_unprovisioned("greenfield", tag, "S-ws3");
    g.ok(&["init", "--name", tag, "--alias", &format!("a-{tag}")]);
    git_commit_all(&root, "after init");
    (root, g)
}

fn gate(g: &Gov, q: &str, extra: Value) -> String {
    g.ok(&[
        "gate",
        "create",
        "--question",
        q,
        "--fields",
        &package(extra),
    ])["id"]
        .as_str()
        .unwrap()
        .to_string()
}

fn record(root: &Path, rel: &str) -> Value {
    yaml(root, rel)
}

// ============================================================================================ BC-P2-08

/// Framework §23 / Contract v3:364: an invocation that declares no role carries no privileged authority, on every
/// command, lifecycle ingress included; the declared role is the one evaluated, by whichever documented means.
#[test]
fn an_undeclared_invocation_carries_no_privileged_authority_anywhere() {
    let (root, g) = setup_fixture("greenfield", "ws3-undeclared", "S-ws3");
    let none = g.with_role("");
    // first install: refused before anything is written
    let e = none.err(&["init", "--source", signed_source(), "--name", "u"]);
    assert_eq!(e.error_code(), "AUTHORITY_DENIED");
    assert_eq!(e.details()["cause"], "ROLE_UNDECLARED");
    assert!(!exists(&root, "governance/framework.lock") && !exists(&root, "governance/kernel"));
    // declared through the environment instead: the same resolution
    let env_l0 = g.with_role("").with_env("GOV_ROLE", "independent-auditor");
    assert_eq!(
        env_l0
            .err(&["init", "--source", signed_source(), "--name", "u"])
            .details()["cause"],
        "LEVEL_TOO_LOW"
    );
    g.ok(&[
        "init",
        "--source",
        signed_source(),
        "--name",
        "u",
        "--alias",
        "a-u",
    ]);
    // installed: every privileged path refuses the undeclared caller; reads still work
    for args in [
        vec!["gate", "revoke", "HDG-0001"],
        vec![
            "task",
            "create",
            "--class",
            "documentation",
            "--objective",
            "x",
        ],
        vec!["pause", "--reason", "x"],
        vec!["resume"],
        vec!["memory", "heldout-starter", "--force"],
        vec!["task", "replan"],
        vec!["init", "--source", signed_source(), "--force"],
    ] {
        let e = none.err(&args);
        assert_eq!(
            e.error_code(),
            "AUTHORITY_DENIED",
            "{args:?}: {}",
            e.envelope
        );
    }
    assert!(none.run(&["status"]).ok());
    assert!(none.run(&["gate", "list"]).ok());
    // --role on init / init --force is honoured exactly like GOV_ROLE (A0-E1-01, A0-S4-03)
    let e =
        g.with_role("independent-auditor")
            .err(&["init", "--source", signed_source(), "--force"]);
    assert_eq!(e.error_code(), "AUTHORITY_DENIED");
    let e = g
        .with_role("")
        .with_env("GOV_ROLE", "independent-auditor")
        .err(&["init", "--source", signed_source(), "--force"]);
    assert_eq!(e.error_code(), "AUTHORITY_DENIED");
    // a declared `human` role is a claim, not an identity: it carries L0
    let e = g.with_role("human").err(&["gate", "revoke", "HDG-0001"]);
    assert_eq!(e.details()["cause"], "HUMAN_ROLE_CLAIM");
    // two different declarations in one invocation are refused
    let e = g.with_role("orchestrator").err(&[
        "adopt",
        "review",
        "--verdict",
        "MIGRATION_PLAN_APPROVED",
        "--reviewer-role",
        "migration-reviewer",
    ]);
    assert_eq!(e.error_code(), "ROLE_CONFLICT");
}

/// Contract v3 O5 G0: nothing mutates under FREEZE_WRITES / PAUSE outside the explicit recovery allow-lists, and the
/// commands that had no authority class now have one (A0-A5-01, A0-O5-05, A0-E1-03).
#[test]
fn g0_freeze_and_pause_refuse_every_write_outside_the_listed_recovery_operations() {
    let (root, g) = fresh("ws3-g0");
    let gid = gate(&g, "Proceed with the migration?", json!({}));
    g.ok(&[
        "task",
        "create",
        "--id",
        "TASK-G0",
        "--class",
        "documentation",
        "--objective",
        "x",
        "--status",
        "READY",
    ]);
    let writes: Vec<Vec<&str>> = vec![
        vec!["gate", "present", &gid],
        vec!["audit"],
        vec!["verify", "governance"],
        vec!["verify", "product"],
        vec!["health", "run"],
        vec!["memory", "heldout-starter", "--force"],
        vec!["adapters", "generate"],
        vec!["tools", "registry"],
        vec!["context", "compile", "TASK-G0"],
        vec!["task", "replan"],
        vec!["task", "release", "TASK-G0"],
        vec!["continue"],
        vec!["init", "--source", signed_source(), "--force"],
    ];
    let snapshot = |r: &Path| tree_hash(r, &[".governance-runtime/**"]);
    for (mode, code) in [("freeze-writes", "FROZEN"), ("pause", "PAUSED")] {
        g.ok(&[mode, "--reason", "incident"]);
        for args in &writes {
            if mode == "pause" && args[0] == "gate" {
                continue; // presenting a pending question is on the PAUSE allow-list
            }
            let before = snapshot(&root);
            let e = g.err(args);
            assert_eq!(e.error_code(), code, "{mode}: {args:?}: {}", e.envelope);
            assert_eq!(
                snapshot(&root),
                before,
                "{mode}: {args:?} changed governed state"
            );
            assert_eq!(e.code, 4);
        }
        // the listed recovery operations stay available
        g.ok(&["telemetry", "emit", "--name", "incident.note"]);
        if mode == "pause" {
            g.ok(&["gate", "present", &gid]);
        }
        // round 2 (O-4): rebuilding derived index state is a recovery operation under both controls. It writes only
        // the derived index and its generated manifests: no authoritative, governed or evidence file changes
        let governed =
            |r: &Path| tree_hash(r, &[".governance-runtime/**", "governance/generated/**"]);
        let before = governed(&root);
        g.ok(&["rebuild-memory"]);
        g.ok(&["memory", "rebuild", "--incremental"]);
        assert_eq!(
            governed(&root),
            before,
            "{mode}: rebuild changed governed state"
        );
        // evidence-writing commands have non-persisting forms for diagnosis under the control (IP-WS02-09)
        let before = snapshot(&root);
        g.ok(&["health", "run", "--no-persist", "--tier", "G1"]);
        assert_eq!(
            snapshot(&root),
            before,
            "{mode}: a non-persisting health run wrote"
        );
        g.ok(&[mode, "--reason", "still"]);
        g.ok(&["resume"]);
    }
    // the allow-lists are explicit and every entry carries its reason
    for (label, why) in gov_runtime::orchestration::control::FROZEN_ALLOW_LIST
        .iter()
        .chain(gov_runtime::orchestration::control::PAUSED_ALLOW_LIST)
    {
        assert!(!label.is_empty() && why.len() > 10);
    }
    // L0 cannot regenerate the governed held-out set or rewrite task state through replan
    let aud = g.with_role("independent-auditor");
    assert_eq!(
        aud.err(&["memory", "heldout-starter", "--force"])
            .error_code(),
        "AUTHORITY_DENIED"
    );
    assert_eq!(
        aud.err(&["task", "replan"]).error_code(),
        "AUTHORITY_DENIED"
    );
    assert_eq!(
        aud.err(&["adopt", "baseline"]).error_code(),
        "AUTHORITY_DENIED"
    );
}

/// Every label the CLI can produce is classified in `COMMAND_GUARDS` (derived from the CLI source, not declared).
#[test]
fn every_cli_command_label_is_classified_by_g0() {
    let src = std::fs::read_to_string(canonical_root().join("cli/src/main.rs")).unwrap();
    let body = src
        .split("fn g0_label(cmd: &Cmd) -> String {")
        .nth(1)
        .expect("g0_label")
        .split("\n}\n")
        .next()
        .unwrap();
    let mut literals: Vec<String> = vec![];
    let mut rest = body;
    while let Some(i) = rest.find('"') {
        let compared = rest[..i].trim_end().ends_with("==");
        let after = &rest[i + 1..];
        let Some(j) = after.find('"') else { break };
        if !compared {
            literals.push(after[..j].to_string());
        }
        rest = &after[j + 1..];
    }
    let use_ = gov_runtime::orchestration::control::command_guard;
    let mut checked = 0;
    for l in literals {
        if l.contains('{') {
            continue;
        }
        checked += 1;
        assert!(
            use_(&l).is_some() || use_(&format!("adopt {l}")).is_some(),
            "CLI label '{l}' is not classified by G0"
        );
    }
    assert!(checked > 90, "the census collapsed to {checked} labels");
}

// ============================================================================================ BC-P2-10 / BC-P2-09

/// Contract v3:679, D-0007 rule 2, ARCH-0003 §8: a human answer comes only from an owner-signed document verified
/// against the administrator-provisioned anchor. Every local means an agent controls is refused.
#[test]
fn human_answers_come_only_from_the_owner_signed_channel() {
    let (root, g) = fresh_unprovisioned("ws3-hc");
    let gid = gate(&g, "Adopt vendor X?", json!({}));
    let (inst, sha) = render(&g, &gid);
    // P2-ADJ-0001: a machine with no Signed Release Root has no human channel — refused typed, with the remediation
    let e = g.err(&["decide", &gid, "--option", "A"]);
    assert_eq!(e.error_code(), "HUMAN_CHANNEL_UNAVAILABLE");
    assert_eq!(e.details()["cause"], "UNPROVISIONED", "{}", e.envelope);
    assert!(
        e.details()["provision_command"]
            .as_str()
            .unwrap()
            .starts_with("gov trust provision"),
        "{}",
        e.envelope
    );
    // a standalone anchor is not a source of Human Gate authority: even the owner's own self-signed anchor, supplied
    // from the administrator domain, is refused (and the status says the channel is unavailable, and why)
    let owner_anchor = scratch_file(&g, "anchor-owner.json", &anchor_doc(&owner(), &owner()));
    let e = g.err(&[
        "trust",
        "human-channel",
        "--provision",
        owner_anchor.to_str().unwrap(),
    ]);
    assert_eq!(e.error_code(), "HUMAN_CHANNEL_STANDALONE_DISABLED");
    assert_eq!(e.details()["cause"], "STANDALONE_ANCHOR_DISABLED");
    let st = g.ok(&["trust", "human-channel"]);
    assert_eq!(st["available"], false);
    assert_eq!(st["standalone_anchor_permitted_by_policy"], false);
    assert_eq!(
        st["unavailable_reason"]["code"],
        "HUMAN_CHANNEL_UNAVAILABLE"
    );
    // the trust anchor is administrator-domain material: never repository content
    let in_repo = root.join("governance").join("hc-root.json");
    std::fs::copy(throwaway_root(&g), &in_repo).unwrap();
    assert_eq!(
        g.err(&["trust", "provision", "--anchor", in_repo.to_str().unwrap()])
            .error_code(),
        "SRR_ANCHOR_FROM_REPOSITORY_REFUSED"
    );
    std::fs::remove_file(&in_repo).unwrap();
    human_channel(&g);
    // once anchored, the product never re-anchors: an agent cannot swap in its own key through the product
    let agent = key(0x66);
    let (akid, aentry) = key_entry(&agent);
    let agent_root = scratch_file(
        &g,
        "root-agent.json",
        &envelope(
            &json!({"_type": "root", "spec_version": "srr/1", "product": gov_runtime::FRAMEWORK_NAME, "version": 1,
                "expires": far_future(), "keys": {akid.clone(): aentry},
                "roles": {"root": {"keyids": [akid.clone()], "threshold": 1}, "release": {"keyids": [akid.clone()], "threshold": 1},
                          "snapshot": {"keyids": [akid.clone()], "threshold": 1}, "timestamp": {"keyids": [akid.clone()], "threshold": 1},
                          "human-gate": {"keyids": [akid], "threshold": 1}}}),
            &[&agent],
        ),
    );
    assert_eq!(
        g.err(&[
            "trust",
            "provision",
            "--anchor",
            agent_root.to_str().unwrap()
        ])
        .error_code(),
        "SRR_ALREADY_PROVISIONED"
    );
    let agent_anchor = scratch_file(&g, "anchor-agent.json", &anchor_doc(&key(0x66), &key(0x66)));
    assert_eq!(
        g.err(&[
            "trust",
            "human-channel",
            "--provision",
            agent_anchor.to_str().unwrap()
        ])
        .error_code(),
        "HUMAN_CHANNEL_STANDALONE_DISABLED"
    );
    // CLI metadata, defaults, role claims and the environment
    assert_eq!(
        g.err(&["decide", &gid, "--option", "A"]).error_code(),
        "HUMAN_ANSWER_UNAUTHENTICATED"
    );
    assert_eq!(
        g.err(&["decide", &gid, "--option", "A", "--by", "product-owner"])
            .error_code(),
        "HUMAN_ANSWER_UNAUTHENTICATED"
    );
    assert_eq!(
        g.with_role("human")
            .err(&["decide", &gid, "--option", "A", "--by", "human"])
            .error_code(),
        "AUTHORITY_DENIED"
    );
    assert_eq!(
        g.with_role("")
            .with_env("GOV_ROLE", "human")
            .err(&["decide", &gid, "--option", "A"])
            .error_code(),
        "AUTHORITY_DENIED"
    );
    assert_eq!(
        g.with_env("GOV_HUMAN_GATE_APPROVED", "1")
            .err(&["decide", &gid, "--option", "A"])
            .error_code(),
        "HUMAN_ANSWER_UNAUTHENTICATED"
    );
    // documents that are not the owner's answer to THIS package
    let bad = |name: &str, text: String| {
        let f = scratch_file(&g, name, &text);
        g.err(&["decide", &gid, "--answer-file", f.to_str().unwrap()])
            .error_code()
    };
    assert_eq!(
        bad(
            "impostor.json",
            signed_doc(
                &gid,
                &inst,
                &sha,
                Some("A"),
                "n1",
                &key(0x66),
                &far_future()
            )
        ),
        "HUMAN_ANSWER_UNAUTHENTICATED"
    );
    assert_eq!(
        bad(
            "other-pkg.json",
            signed_doc(&gid, &inst, "00", Some("A"), "n2", &owner(), &far_future())
        ),
        "HUMAN_ANSWER_UNAUTHENTICATED"
    );
    assert_eq!(
        bad(
            "other-inst.json",
            signed_doc(&gid, "x", &sha, Some("A"), "n3", &owner(), &far_future())
        ),
        "HUMAN_ANSWER_UNAUTHENTICATED"
    );
    assert_eq!(
        bad(
            "not-offered.json",
            signed_doc(&gid, &inst, &sha, Some("Z"), "n4", &owner(), &far_future())
        ),
        "HUMAN_ANSWER_UNAUTHENTICATED"
    );
    assert_eq!(
        bad(
            "expired.json",
            signed_doc(
                &gid,
                &inst,
                &sha,
                Some("A"),
                "n5",
                &owner(),
                "2000-01-01T00:00:00Z"
            )
        ),
        "HUMAN_ANSWER_UNAUTHENTICATED"
    );
    let unsigned = format!(
        "{{\"signed\":{},\"signatures\":[]}}",
        json!({"_type": "human-gate-answer"})
    );
    assert_eq!(
        bad("unsigned.json", unsigned),
        "HUMAN_ANSWER_UNAUTHENTICATED"
    );
    // a CLI --option that contradicts the signed option is refused
    let good = scratch_file(
        &g,
        "good.json",
        &signed_doc(
            &gid,
            &inst,
            &sha,
            Some("B"),
            "n-good",
            &owner(),
            &far_future(),
        ),
    );
    assert_eq!(
        g.err(&[
            "decide",
            &gid,
            "--option",
            "A",
            "--answer-file",
            good.to_str().unwrap()
        ])
        .error_code(),
        "HUMAN_ANSWER_MISMATCH"
    );
    // the owner's answer: accepted, recorded as human, bound to its evidence
    let d = g.ok(&["decide", &gid, "--answer-file", good.to_str().unwrap()]);
    assert_eq!(d["answered_by_kind"], "human");
    assert_eq!(d["option"], "B");
    let rec = record(&root, &format!("spec/decisions/{gid}.yaml"));
    assert_eq!(
        rec["presented_in_chat"], true,
        "a signed answer is the human's receipt of the package"
    );
    assert!(
        rec["answer"]["human_channel"]["envelope_hex"]
            .as_str()
            .unwrap()
            .len()
            > 100
    );
    let dec = record(
        &root,
        &format!("spec/decisions/{}.yaml", d["decision"].as_str().unwrap()),
    );
    assert_eq!(dec["human_approved"], true);
    assert!(dec["os_binding"]["mac"].is_string());
    // a signed document is bound to its gate, and its nonce is single-use
    let g2 = gate(&g, "Second question?", json!({}));
    let (inst2, sha2) = render(&g, &g2);
    assert_eq!(
        g.err(&["decide", &g2, "--answer-file", good.to_str().unwrap()])
            .error_code(),
        "HUMAN_ANSWER_UNAUTHENTICATED"
    );
    let replay = scratch_file(
        &g,
        "replay.json",
        &signed_doc(
            &g2,
            &inst2,
            &sha2,
            Some("A"),
            "n-good",
            &owner(),
            &far_future(),
        ),
    );
    let e = g.err(&["decide", &g2, "--answer-file", replay.to_str().unwrap()]);
    assert!(
        e.envelope.to_string().contains("nonce already consumed"),
        "{}",
        e.envelope
    );
    // the recorded answer is re-verified at use: `gate show` reports it verified and authorising nothing (B)
    let show = g.ok(&["gate", "show", &gid]);
    assert_eq!(show["t2"]["binding"], "VERIFIED");
    assert_eq!(show["answer"]["verified"], true);
    assert_eq!(show["answer"]["by_kind"], "human");
    assert_eq!(show["authorisation"]["state"], "DECLINED");
}

/// Contract v3:676 / framework §52: rendering to an agent's stdout (text or --json, or `gov continue`) is not
/// presentation; only an owner-signed receipt or answer sets `presented_in_chat`.
#[test]
fn presentation_is_recorded_only_from_an_owner_signed_receipt() {
    let (root, g) = fresh("ws3-present");
    let gid = gate(&g, "Ship the beta?", json!({}));
    g.ok(&["gate", "present", &gid]);
    let rec = record(&root, &format!("spec/decisions/{gid}.yaml"));
    assert_eq!(rec["gate_status"], "PRESENTED");
    assert_eq!(rec["presented_in_chat"], false);
    assert!(rec["presentation"]["package_sha256"].is_string());
    g.with_role("research-agent").ok(&["gate", "present", &gid]);
    assert_eq!(
        record(&root, &format!("spec/decisions/{gid}.yaml"))["presented_in_chat"],
        false
    );
    let r = human_receipt(&g, &gid);
    assert_eq!(r["receipt"]["presented_in_chat"], true);
    let rec = record(&root, &format!("spec/decisions/{gid}.yaml"));
    assert_eq!(rec["presented_in_chat"], true);
    assert!(rec["presentation_receipt"]["evidence"]["signed_by_key_ids"].is_array());
}

/// D-0007 T2 / Contract v3:365: a gate or decision record that no gov operation wrote as it stands is never honoured.
#[test]
fn hand_written_gate_and_decision_records_are_not_honoured() {
    let (root, g) = fresh("ws3-t2");
    let gid = gate(&g, "Approve the schema change?", json!({}));
    g.ok(&["gate", "present", &gid]);
    // a worker flips the presentation flag and writes an ANSWERED human answer by hand
    let path = format!("spec/decisions/{gid}.yaml");
    let mut rec = record(&root, &path);
    rec["presented_in_chat"] = json!(true);
    write_yaml(&root, &path, &rec);
    let e = g.err(&[
        "decide",
        &gid,
        "--option",
        "A",
        "--by",
        "orchestrator",
        "--rationale",
        "x",
    ]);
    assert_eq!(e.error_code(), "GATE_NOT_PRESENTED");
    assert_eq!(e.details()["cause"], "T2_UNBOUND");
    rec["gate_status"] = json!("ANSWERED");
    rec["answer"] = json!({"option": "A", "by": "owner", "by_kind": "human"});
    write_yaml(&root, &path, &rec);
    write_yaml(
        &root,
        "spec/decisions/D-0900.yaml",
        &json!({"id": "D-0900", "type": "decision", "title": "forged", "status": "ACTIVE", "chosen_option": "A", "human_approved": true, "approved_by_kind": "human", "derived_from": [gid]}),
    );
    let list = g.ok(&["gate", "list"]);
    let entry = list
        .as_array()
        .unwrap()
        .iter()
        .find(|x| x["id"] == gid.as_str())
        .unwrap();
    assert_eq!(entry["honoured"], false);
    assert_eq!(entry["t2"]["binding"], "BROKEN");
    let show = g.ok(&["gate", "show", &gid]);
    assert_eq!(show["answer"]["verified"], false);
    assert_eq!(show["answer"]["code"], "T2_UNBOUND");
    assert_eq!(show["authorisation"]["state"], "UNVERIFIED");
    // withdrawal is the fail-safe direction and works on the forged record
    g.ok(&["gate", "revoke", &gid, "--reason", "forged"]);
}

// ============================================================================================ BC-P2-12 (answer side)

#[test]
fn blocked_work_is_released_only_by_an_authorising_answer() {
    let (root, g) = fresh("ws3-block");
    let mut tasks = vec![];
    for n in 0..3 {
        let t = g.ok(&[
            "task",
            "create",
            "--class",
            "discovery",
            "--objective",
            &format!("t{n}"),
            "--status",
            "READY",
        ]);
        tasks.push(t["id"].as_str().unwrap().to_string());
    }
    let status = |t: &str| {
        record(&root, &format!("spec/tasks/{t}.yaml"))["task_status"]
            .as_str()
            .unwrap()
            .to_string()
    };
    let g_decl = gate(&g, "May t0 proceed?", json!({"blocks_tasks": [tasks[0]]}));
    let g_ok = gate(&g, "May t1 proceed?", json!({"blocks_tasks": [tasks[1]]}));
    let g_rev = gate(&g, "May t2 proceed?", json!({"blocks_tasks": [tasks[2]]}));
    for t in &tasks {
        assert_eq!(status(t), "WAITING_HUMAN");
    }
    let d = human_decide(&g, &g_decl, "B");
    assert_eq!(d["authorises_blocked_work"], false);
    assert_eq!(
        status(&tasks[0]),
        "BLOCKED",
        "a declining answer never releases the blocked work"
    );
    human_decide(&g, &g_ok, "A");
    assert_eq!(status(&tasks[1]), "READY");
    g.ok(&["gate", "revoke", &g_ok, "--reason", "approval withdrawn"]);
    assert_eq!(
        status(&tasks[1]),
        "BLOCKED",
        "revoking the authorising answer blocks the work again"
    );
    g.ok(&["gate", "revoke", &g_rev, "--reason", "question withdrawn"]);
    assert_eq!(status(&tasks[2]), "BLOCKED");
    let state = |gid: &str| {
        g.ok(&["gate", "show", gid])["authorisation"]["state"]
            .as_str()
            .unwrap()
            .to_string()
    };
    assert_eq!(state(&g_decl), "DECLINED");
    assert_eq!(state(&g_ok), "WITHDRAWN");
    assert_eq!(state(&g_rev), "WITHDRAWN");
    assert_eq!(
        g.err(&["gate", "show", "HDG-9999"]).error_code(),
        "GATE_NOT_FOUND"
    );
}

// ============================================================================================ BC-P2-18

/// Framework §50 / Contract v3:658: agent resolution only on an assessed, low-impact, reversible, high-confidence
/// question, with a rationale, and never on an assessment the resolving session made itself.
#[test]
fn agent_resolution_needs_an_assessed_and_independent_assessment() {
    let (_root, g) = fresh("ws3-agent");
    let low = json!({"impact_radius": "R0", "confidence": 0.95, "reversibility": "reversible"});
    // raised and resolved by the same session: refused (A0-L1-01 second limb)
    let own = gate(&g, "Keep retry limit 5?", low.clone());
    g.ok(&["gate", "present", &own]);
    let e = g.err(&[
        "decide",
        &own,
        "--option",
        "A",
        "--by",
        "orchestrator",
        "--rationale",
        "D-2 supersedes D-1",
    ]);
    assert_eq!(e.error_code(), "AUTHORITY_DENIED");
    assert!(e.envelope.to_string().contains("own declaration"));
    // raised by another session: resolvable, with a rationale
    let other = g.with_session("S-raiser");
    let gid = gate(
        &other,
        "Keep retry limit 5 (assessed elsewhere)?",
        low.clone(),
    );
    g.ok(&["gate", "present", &gid]);
    assert_eq!(
        g.err(&["decide", &gid, "--option", "A", "--by", "orchestrator"])
            .error_code(),
        "USAGE",
        "no rationale"
    );
    assert_eq!(
        g.err(&[
            "decide",
            &gid,
            "--option",
            "A",
            "--by",
            "change-controller",
            "--rationale",
            "x"
        ])
        .error_code(),
        "AUTHORITY_DENIED",
        "an agent resolves as itself"
    );
    let d = g.ok(&[
        "decide",
        &gid,
        "--option",
        "A",
        "--by",
        "orchestrator",
        "--rationale",
        "load-test evidence",
    ]);
    assert_eq!(d["answered_by_kind"], "agent");
    // an unassessed reversibility counts against agent resolution (A0-L1-01 first limb)
    let un = gate(
        &other,
        "Unassessed reversibility?",
        json!({"impact_radius": "R0", "confidence": 0.95, "reversibility": "depends on the vendor"}),
    );
    g.ok(&["gate", "present", &un]);
    let e = g.err(&[
        "decide",
        &un,
        "--option",
        "A",
        "--by",
        "orchestrator",
        "--rationale",
        "x",
    ]);
    assert_eq!(e.error_code(), "AUTHORITY_DENIED");
    assert!(
        e.envelope.to_string().contains("incomplete"),
        "{}",
        e.envelope
    );
    for (tag, f) in [
        ("R2", json!({"impact_radius": "R2"})),
        ("conf", json!({"confidence": 0.7})),
        ("irr", json!({"reversibility": "irreversible"})),
    ] {
        let mut v = low.clone();
        for (k, x) in f.as_object().unwrap() {
            v[k] = x.clone();
        }
        let gg = gate(&other, &format!("Contradiction {tag}?"), v);
        g.ok(&["gate", "present", &gg]);
        assert_eq!(
            g.err(&[
                "decide",
                &gg,
                "--option",
                "A",
                "--by",
                "orchestrator",
                "--rationale",
                "x"
            ])
            .error_code(),
            "AUTHORITY_DENIED",
            "{tag}"
        );
    }
    // framework §51: a gate raised for a human-only trigger is never agent-resolvable, however it is assessed
    let mut v = low.clone();
    v["trigger"] = json!("tool_install");
    let tool = gate(&other, "Install jq for the parser task?", v);
    g.ok(&["gate", "present", &tool]);
    let e = g.err(&[
        "decide",
        &tool,
        "--option",
        "A",
        "--by",
        "orchestrator",
        "--rationale",
        "x",
    ]);
    assert_eq!(e.error_code(), "AUTHORITY_DENIED");
    assert!(
        e.envelope.to_string().contains("never agent-resolvable"),
        "{}",
        e.envelope
    );
}

// ============================================================================================ BC-P2-49

#[test]
fn the_decision_package_is_enforced() {
    let (root, g) = fresh("ws3-pkg");
    let e = g.err(&["gate", "create", "--question", "Should we proceed?"]);
    assert_eq!(e.error_code(), "GATE_PACKAGE_INCOMPLETE");
    for f in [
        "why_now",
        "current_state",
        "impact",
        "reversibility",
        "cost_rework",
        "recommendation",
    ] {
        assert!(
            e.details()["missing"].to_string().contains(f),
            "{f}: {}",
            e.details()
        );
    }
    assert!(
        e.details()["missing"].to_string().contains("options")
            && e.details()["missing"].to_string().contains("confidence")
    );
    assert_eq!(
        g.err(&[
            "gate",
            "create",
            "--question",
            "q?",
            "--fields",
            &package(json!({"why_now": "not assessed"}))
        ])
        .error_code(),
        "GATE_PACKAGE_INCOMPLETE"
    );
    assert_eq!(
        g.err(&[
            "gate",
            "create",
            "--question",
            "q?",
            "--fields",
            &package(json!({"options": []}))
        ])
        .error_code(),
        "GATE_PACKAGE_INCOMPLETE"
    );
    assert_eq!(
        g.err(&[
            "gate",
            "create",
            "--question",
            "q?",
            "--fields",
            &package(json!({"permitted_next_actions": ["gov decide <gate> --option <id>"]}))
        ])
        .error_code(),
        "GATE_PACKAGE_INCOMPLETE"
    );
    assert_eq!(
        g.err(&[
            "gate",
            "create",
            "--question",
            "q?",
            "--fields",
            &package(json!({"confidence": "high"}))
        ])
        .error_code(),
        "GATE_PACKAGE_INCOMPLETE"
    );
    let gid = gate(&g, "Which vendor?", json!({}));
    let rec = record(&root, &format!("spec/decisions/{gid}.yaml"));
    let actions: Vec<String> = rec["permitted_next_actions"]
        .as_array()
        .unwrap()
        .iter()
        .map(|a| a.as_str().unwrap().to_string())
        .collect();
    assert!(
        actions.iter().all(|a| !a.contains('<') && !a.contains('>')),
        "{actions:?}"
    );
    assert!(
        actions
            .iter()
            .any(|a| a.starts_with(&format!("gov decide {gid} --option A"))),
        "{actions:?}"
    );
    // the answer is one of the offered options (agent path; the human path is covered above)
    g.ok(&["gate", "present", &gid]);
    assert_eq!(
        g.err(&[
            "decide",
            &gid,
            "--option",
            "Z",
            "--by",
            "orchestrator",
            "--rationale",
            "x"
        ])
        .error_code(),
        "GATE_OPTION_INVALID"
    );
    // a system-raised gate carries a complete package too (budget threshold via routing evidence)
    let ev = json!({"model": "m", "provider": "p", "task_class": "implementation", "reasoning_effort": "high", "cost": 99.0, "latency_ms": 1, "pass": true, "repair_count": 0, "reviewer_findings": 0});
    let f = root.parent().unwrap().join("ws3-ev.json");
    std::fs::write(&f, ev.to_string()).unwrap();
    let r = g.ok(&["route", "--record", f.to_str().unwrap()]);
    let bg = record(
        &root,
        &format!("spec/decisions/{}.yaml", r["human_gate"].as_str().unwrap()),
    );
    for k in [
        "why_now",
        "current_state",
        "impact",
        "reversibility",
        "cost_rework",
        "recommendation",
    ] {
        assert!(
            bg[k]
                .as_str()
                .map(|s| !s.is_empty() && s != "not assessed")
                .unwrap_or(false),
            "{k}: {bg}"
        );
    }
}

// ============================================================================================ BC-P2-45

/// Contract v3:134, :693-699, :522; D-0007 rule 3: every project overlay input goes through POLICY_PRECEDENCE.
#[test]
fn project_overlays_may_raise_floors_but_never_lower_them() {
    let (root, g) = fresh("ws3-overlay");
    let mut mro = yaml(&root, "governance/project/MODEL_ROUTING_OVERRIDES.yaml");
    mro["providers"] = json!([{"name": "prov", "models": [{"id": "light", "tier": "T1", "max_reasoning": "low", "cost_per_1k_in": 0.1}, {"id": "frontier", "tier": "T3", "max_reasoning": "extra_high", "cost_per_1k_in": 9.0}]}]);
    mro["task_class_overrides"] = json!({"security": "T1", "documentation": "T2"});
    mro["role_overrides"] = json!({"orchestrator": {"minimum_tier": "T1", "default_reasoning": "low"}, "backend-engineer": {"default_reasoning": "low"}});
    write_yaml(
        &root,
        "governance/project/MODEL_ROUTING_OVERRIDES.yaml",
        &mro,
    );
    let mut pp = yaml(&root, "governance/project/PROJECT_POLICY.yaml");
    pp["readiness"]["enforce_pre_implementation_cells"] = json!(false);
    write_yaml(&root, "governance/project/PROJECT_POLICY.yaml", &pp);
    let ov = g.ok(&["policy", "overrides"]);
    let refused: Vec<String> = ov["refused"]
        .as_array()
        .unwrap()
        .iter()
        .map(|r| {
            format!(
                "{}.{}",
                r["policy"].as_str().unwrap(),
                r["key"].as_str().unwrap()
            )
        })
        .collect();
    for k in [
        "MODEL_ROUTING_OVERRIDES.task_class_overrides.security",
        "MODEL_ROUTING_OVERRIDES.role_overrides.orchestrator.minimum_tier",
        "MODEL_ROUTING_OVERRIDES.role_overrides.orchestrator.default_reasoning",
        "MODEL_ROUTING_OVERRIDES.role_overrides.backend-engineer.default_reasoning",
        "PROJECT_POLICY.readiness.enforce_pre_implementation_cells",
    ] {
        assert!(
            refused.contains(&k.to_string()),
            "{k} not refused: {refused:?}"
        );
    }
    assert!(
        ov["applied"]
            .to_string()
            .contains("task_class_overrides.documentation"),
        "raising a floor applies: {}",
        ov["applied"]
    );
    assert_eq!(
        g.ok(&["route", "--class", "security"])["minimum_tier"],
        "T3"
    );
    assert_eq!(
        g.ok(&["route", "--class", "documentation"])["minimum_tier"],
        "T3",
        "orchestrator floor"
    );
    let r = g
        .with_role("routine-documentation")
        .ok(&["route", "--class", "documentation"]);
    assert_eq!(r["minimum_tier"], "T2", "the raised class floor applies");
    let t = g.ok(&[
        "task",
        "create",
        "--class",
        "implementation",
        "--objective",
        "hard",
        "--fields",
        r#"{"minimum_reasoning": "extra_high"}"#,
    ]);
    let r = g
        .with_role("backend-engineer")
        .ok(&["route", "--task", t["id"].as_str().unwrap()]);
    assert_eq!(
        r["reasoning"], "extra_high",
        "an overlay role default can never lower a task's declared minimum"
    );
    let t = g.ok(&[
        "task",
        "create",
        "--class",
        "documentation",
        "--objective",
        "ctx",
        "--status",
        "READY",
    ]);
    let ctx = g.ok(&["context", "compile", t["id"].as_str().unwrap()]);
    let layer3 = ctx["deterministic_authority"]["authority_layers"]
        .as_array()
        .unwrap()
        .iter()
        .find(|l| l["layer"] == 3)
        .unwrap()
        .clone();
    assert_eq!(
        layer3["readiness_enforced"], true,
        "readers of the project policy see the enforced value: {layer3}"
    );
    let (ok27, _) = doctor_check(&g, "D027");
    assert!(!ok27, "the refused weakening is reported");
    // round 2 (IP-WS02-08): the CRITICAL finding is a hard-block, and G0 (`control::guard_write`) refuses governed
    // work while it stands; removing the weakening repairs it and the guard re-evaluates and releases the block
    let e = g.err(&[
        "task",
        "create",
        "--class",
        "documentation",
        "--objective",
        "blocked",
    ]);
    assert_eq!(e.error_code(), "HEALTH_HARD_BLOCK", "{}", e.envelope);
    assert!(e.envelope.to_string().contains("D027"), "{}", e.envelope);
    let mut pp = yaml(&root, "governance/project/PROJECT_POLICY.yaml");
    pp["readiness"]["enforce_pre_implementation_cells"] = json!(true);
    write_yaml(&root, "governance/project/PROJECT_POLICY.yaml", &pp);
    let mut mro = yaml(&root, "governance/project/MODEL_ROUTING_OVERRIDES.yaml");
    mro["task_class_overrides"] = json!({"documentation": "T2"});
    mro["role_overrides"] = json!({});
    write_yaml(
        &root,
        "governance/project/MODEL_ROUTING_OVERRIDES.yaml",
        &mro,
    );
    g.ok(&[
        "task",
        "create",
        "--class",
        "documentation",
        "--objective",
        "unblocked",
    ]);
}

// ============================================================================================ decisions authorising exceptions

/// A PROJECT_EXCEPTIONS entry is authorised only by a decision a gov operation wrote (a human's signed answer to a
/// gate that asked for exactly that scope); a hand-written decision claiming human approval is refused.
#[test]
fn a_policy_exception_needs_a_decision_recorded_by_an_answered_gate() {
    let (root, g) = fresh("ws3-exc");
    write_yaml(
        &root,
        "spec/decisions/D-0500.yaml",
        &json!({"id": "D-0500", "type": "decision", "title": "forged", "status": "ACTIVE", "chosen_option": "A", "human_approved": true, "authorises_exceptions": ["EXC-0001"]}),
    );
    let set = |dec: &str| {
        let mut ex = yaml(&root, "governance/project/PROJECT_EXCEPTIONS.yaml");
        ex["exceptions"] = json!([{"id": "EXC-0001", "policy": "BUDGET_POLICY", "key": "defaults.max_parallel_agents", "value": 9, "decision": dec, "expires": "2999-01-01", "reason": "migration window"}]);
        write_yaml(&root, "governance/project/PROJECT_EXCEPTIONS.yaml", &ex);
    };
    set("D-0500");
    let ov = g.ok(&["policy", "overrides"]);
    assert!(ov["refused"].to_string().contains("T2 binding"), "{ov}");
    let gid = gate(
        &g,
        "Allow 9 parallel agents during the migration window?",
        json!({"decision_scope": {"authorises_exceptions": ["EXC-0001"]}}),
    );
    let d = human_decide(&g, &gid, "A");
    set(d["decision"].as_str().unwrap());
    let ov = g.ok(&["policy", "overrides"]);
    assert!(
        ov["applied"]
            .as_array()
            .unwrap()
            .iter()
            .any(|a| a["source"] == "EXC-0001"),
        "{ov}"
    );
}

// ============================================================================================ consumers of answers

fn cit_with_gate(g: &Gov, root: &Path, tag: &str, trigger: &str) -> (String, String) {
    let mf = root
        .join(".governance-runtime")
        .join(format!("ws3-{tag}.json"));
    std::fs::create_dir_all(mf.parent().unwrap()).unwrap();
    std::fs::write(
        &mf,
        json!([{"op": "write_file", "path": format!("docs/{tag}.md"), "content": "x\n"}])
            .to_string(),
    )
    .unwrap();
    let c = g.ok(&[
        "cit",
        "propose",
        "--proposal",
        &format!("change {tag}"),
        "--trigger",
        trigger,
        "--manifest",
        mf.to_str().unwrap(),
    ]);
    let cid = c["id"].as_str().unwrap().to_string();
    if c["cit_status"] != "SIMULATED" {
        g.ok(&["cit", "simulate", &cid]);
    }
    let gate = g.ok(&["cit", "show", &cid])["human_gate"]
        .as_str()
        .unwrap()
        .to_string();
    (cid, gate)
}

/// X2-L3xE1 / L3.b5.8 at the product surface: CIT approval and execution honour only a gate answer gov wrote; a
/// worker's hand-written ANSWERED gate + human_approved decision is refused (T2_UNBOUND) and nothing executes.
#[test]
fn cit_approval_consumes_only_honoured_gate_answers() {
    let (root, g) = fresh("ws3-cit");
    let (cid, gid) = cit_with_gate(&g, &root, "forged", "governance_change");
    let path = format!("spec/decisions/{gid}.yaml");
    let mut rec = record(&root, &path);
    rec["gate_status"] = json!("ANSWERED");
    rec["presented_in_chat"] = json!(true);
    rec["answer"] = json!({"option": "A", "by": "owner", "by_kind": "human", "acting_role": "human", "at": "2026-09-18T00:00:01Z"});
    write_yaml(&root, &path, &rec);
    write_yaml(
        &root,
        "spec/decisions/D-0990.yaml",
        &json!({"id": "D-0990", "type": "decision", "title": "forged", "status": "ACTIVE", "chosen_option": "A", "human_approved": true, "approved_by_kind": "human", "derived_from": [gid], "cit": cid}),
    );
    let cc = g.with_role("change-controller").with_session("S-cc");
    assert_eq!(
        cc.err(&["cit", "approve", &cid, "--by", "owner", "--method", "human"])
            .error_code(),
        "T2_UNBOUND"
    );
    assert_eq!(cc.err(&["cit", "execute", &cid]).error_code(), "T2_UNBOUND");
    assert!(!exists(&root, "docs/forged.md"));
    // the genuine path: an owner-signed answer approves and executes
    let (cid2, gid2) = cit_with_gate(&g, &root, "genuine", "governance_change");
    human_decide(&g, &gid2, "A");
    let ap = cc.ok(&["cit", "approve", &cid2, "--method", "human"]);
    assert_eq!(ap["human_approved"], true);
    assert_eq!(cc.ok(&["cit", "execute", &cid2])["cit_status"], "COMMITTED");
}

// ============================================================================================ round 2 (P2-AR-0024)

/// P2-ADJ-0001: the standalone human-gate anchor is off by default. On a machine with no Signed Release Root a human
/// answer is refused typed and observable (remediation: provision); a project cannot switch the anchor on; an anchor
/// file placed in machine state is not honoured; once the machine is provisioned with a root that delegates
/// `human-gate`, the same owner's signed answer is honoured and re-verifies against that root.
#[test]
fn the_standalone_human_gate_anchor_is_off_and_an_unprovisioned_machine_refuses_human_answers() {
    let (root, g) = fresh("ws3-adj1");
    let eff = g.ok(&["policy", "effective", "HUMAN_GATE_POLICY"]);
    assert_eq!(
        eff["kernel"]["human_channel"]["standalone_anchor_when_unprovisioned"], false,
        "kernel default: {eff}"
    );
    // a project may not switch it on (strengthen-only, strict value false)
    let mut pp = yaml(&root, "governance/project/PROJECT_POLICY.yaml");
    pp["policy_overrides"] =
        json!({"HUMAN_GATE_POLICY.human_channel.standalone_anchor_when_unprovisioned": true});
    write_yaml(&root, "governance/project/PROJECT_POLICY.yaml", &pp);
    let ov = g.ok(&["policy", "overrides"]);
    assert!(
        ov["refused"]
            .to_string()
            .contains("human_channel.standalone_anchor_when_unprovisioned"),
        "{ov}"
    );
    assert_eq!(
        g.ok(&["policy", "effective", "HUMAN_GATE_POLICY"])["effective"]["human_channel"]
            ["standalone_anchor_when_unprovisioned"],
        false
    );
    pp["policy_overrides"] = json!({});
    write_yaml(&root, "governance/project/PROJECT_POLICY.yaml", &pp);
    // observable before anything is attempted
    let st = g.ok(&["trust", "human-channel"]);
    assert_eq!(st["available"], false, "{st}");
    assert_eq!(st["standalone_anchor_permitted_by_policy"], false);
    assert!(
        st["unavailable_reason"]["message"]
            .as_str()
            .unwrap()
            .contains("gov trust provision"),
        "{st}"
    );
    // an anchor file the administrator (or anyone able to write machine state) placed there is not honoured
    let hc_dir = machine_state_dir(&root).join("human-channel");
    std::fs::create_dir_all(&hc_dir).unwrap();
    std::fs::write(hc_dir.join("anchor.json"), anchor_doc(&owner(), &owner())).unwrap();
    let gid = gate(&g, "Adopt the reconciliation window?", json!({}));
    let (inst, sha) = render(&g, &gid);
    let doc = scratch_file(
        &g,
        "adj1-answer.json",
        &signed_doc(
            &gid,
            &inst,
            &sha,
            Some("A"),
            "n-adj1",
            &owner(),
            &far_future(),
        ),
    );
    let e = g.err(&[
        "decide",
        &gid,
        "--option",
        "A",
        "--answer-file",
        doc.to_str().unwrap(),
    ]);
    assert_eq!(
        e.error_code(),
        "HUMAN_CHANNEL_UNAVAILABLE",
        "{}",
        e.envelope
    );
    assert_eq!(e.details()["cause"], "UNPROVISIONED");
    assert_eq!(e.details()["standalone_anchor_present"], true);
    assert!(e.details()["remediation"]
        .as_str()
        .unwrap()
        .contains("provision"));
    assert_ne!(
        record(&root, &format!("spec/decisions/{gid}.yaml"))["gate_status"],
        "ANSWERED",
        "nothing was recorded"
    );
    std::fs::remove_file(hc_dir.join("anchor.json")).unwrap();
    // provision, then work: the root's `human-gate` delegation is the channel, and the owner's answer is honoured
    human_channel(&g);
    let (inst, sha) = render(&g, &gid);
    let doc = scratch_file(
        &g,
        "adj1-answer-2.json",
        &signed_doc(
            &gid,
            &inst,
            &sha,
            Some("A"),
            "n-adj1-2",
            &owner(),
            &far_future(),
        ),
    );
    let d = g.ok(&[
        "decide",
        &gid,
        "--option",
        "A",
        "--answer-file",
        doc.to_str().unwrap(),
    ]);
    assert_eq!(d["answered_by_kind"], "human");
    let show = g.ok(&["gate", "show", &gid]);
    assert_eq!(show["answer"]["verified"], true, "{show}");
    assert_eq!(show["authorisation"]["state"], "AUTHORISED", "{show}");
}

/// Round-1 integration observation O-1 (Contract v3 S5 "preserve the project overlay"; A1 "weakening refused"): a
/// project on a shipped kernel whose precedence rules predate overlay-document evaluation (release 4.1.4, 4.1.5) keeps
/// its descriptive overlay keys, every floor is still enforced against it, doctor D027 stays clean, and a framework
/// update to shipped 4.1.5 is applied rather than rolled back. Provisioned machine, signed test releases of the shipped
/// kernels (OWNER-DECISION-P2-0002).
#[test]
fn a_project_on_a_shipped_older_kernel_keeps_descriptive_overlay_keys_and_every_floor() {
    let (root, g) = setup_fixture("greenfield", "ws3-oldk", "S-ws3");
    provision(&g);
    let signed = |ver: &str, seq: u64| -> PathBuf {
        signed_release(
            &canonical_root().join(format!("release/releases/{ver}/kernel")),
            &scratch_dir(&g, &format!("rel-{ver}")),
            seq,
        )
    };
    let r414 = signed("4.1.4", 14);
    let r415 = signed("4.1.5", 15);
    let r = g.ok(&[
        "init",
        "--source",
        r414.to_str().unwrap(),
        "--name",
        "oldk",
        "--alias",
        "oldk-a",
    ]);
    assert_eq!(r["version"], "4.1.4");
    git_commit_all(&root, "4.1.4 installed");
    let ov = g.ok(&["policy", "overrides"]);
    assert_eq!(
        ov["refused"],
        json!([]),
        "descriptive keys are descriptive: {ov}"
    );
    assert!(
        ov["precedence"]["governing_sets"].as_array().unwrap().len() == 2,
        "{ov}"
    );
    let (ok27, msg) = doctor_check(&g, "D027");
    assert!(ok27, "{msg}");
    // the floors still hold against the older kernel
    let mut pp = yaml(&root, "governance/project/PROJECT_POLICY.yaml");
    pp["readiness"]["enforce_pre_implementation_cells"] = json!(false);
    pp["project"]["name"] = json!("renamed");
    pp["policy_overrides"] = json!({"MEMORY_POLICY.failure_memory.retrieval_miss.enabled": false, "MEMORY_POLICY.retrieval.default_k": 5});
    write_yaml(&root, "governance/project/PROJECT_POLICY.yaml", &pp);
    let mut mro = yaml(&root, "governance/project/MODEL_ROUTING_OVERRIDES.yaml");
    mro["task_class_overrides"] = json!({"security": "T1"});
    mro["providers"] = json!([{"name": "p", "models": []}]);
    write_yaml(
        &root,
        "governance/project/MODEL_ROUTING_OVERRIDES.yaml",
        &mro,
    );
    let ov = g.ok(&["policy", "overrides"]);
    let refused: Vec<String> = ov["refused"]
        .as_array()
        .unwrap()
        .iter()
        .map(|r| {
            format!(
                "{}.{}",
                r["policy"].as_str().unwrap(),
                r["key"].as_str().unwrap()
            )
        })
        .collect();
    let mut want = vec![
        "PROJECT_POLICY.readiness.enforce_pre_implementation_cells".to_string(),
        "MODEL_ROUTING_OVERRIDES.task_class_overrides.security".to_string(),
        "MEMORY_POLICY.failure_memory.retrieval_miss.enabled".to_string(),
    ];
    let mut got = refused.clone();
    want.sort();
    got.sort();
    assert_eq!(got, want, "exactly the weakenings are refused: {ov}");
    assert!(
        ov["applied"].to_string().contains("MEMORY_POLICY"),
        "a legitimate override still applies: {ov}"
    );
    assert!(!doctor_check(&g, "D027").0);
    // back to the installed state, then update to the shipped 4.1.5 through its gate
    git(&root, &["checkout", "--", "governance/project"]);
    assert!(doctor_check(&g, "D027").0);
    let first = g.run(&["update", "--apply", "--source", r415.to_str().unwrap()]);
    assert!(!first.ok());
    let gid = first.details()["gate"].as_str().unwrap().to_string();
    human_decide(&g, &gid, "A");
    let ap = g.ok(&[
        "update",
        "--apply",
        "--source",
        r415.to_str().unwrap(),
        "--approve",
    ]);
    assert_eq!(ap["applied"], true, "{ap}");
    assert_eq!(yaml(&root, "governance/framework.lock")["version"], "4.1.5");
    assert_eq!(g.ok(&["policy", "overrides"])["refused"], json!([]));
    assert!(doctor_check(&g, "D027").0);
}

/// Round 2 call sites (BC-P2-08 and the routed IPs), each through the product surface:
/// * WS-9/11 IP-3 — the adoption catalogue and plan record the invocation's declared session and role as producer;
/// * BC-P2-08 — `tools install --role` is the acting role, never a second role for one invocation (ROLE_CONFLICT);
/// * WS-6 IP-6 — `gov memory miss` records an agent-reported retrieval miss (declared role; FREEZE_WRITES refuses it),
///   `gov memory failures` lists open failures;
/// * WS-4 IP-6 — `gov continue` with a damaged derived index is refused typed with the remediation, and
///   `gov rebuild-memory` (a recovery operation even under FREEZE_WRITES, O-4) restores it.
#[test]
fn round_two_call_sites_use_the_declared_role_and_typed_refusals() {
    // WS-9/11 IP-3
    let (root, planner) = setup_fixture("migration", "ws3-r2-adopt", "S-planner-r2");
    for s in ["baseline", "inventory", "classify", "map", "plan"] {
        planner.ok(&["adopt", s]);
    }
    let cat = read(
        &root,
        "spec/audits/GOVERNANCE-ADOPTION/04-TARGET-PATH-MAP.jsonl",
    );
    let first: Value = serde_json::from_str(cat.lines().next().unwrap()).unwrap();
    assert_eq!(first["producer"]["session"], "S-planner-r2", "{first}");
    assert_eq!(first["producer"]["role"], "orchestrator", "{first}");
    assert_eq!(first["producer"]["session_source"], "declared", "{first}");
    let plan = yaml(&root, "spec/audits/GOVERNANCE-ADOPTION/05-plan.yaml");
    assert_eq!(plan["producer"]["session"], "S-planner-r2", "{plan}");
    assert_eq!(plan["producer"]["role"], "orchestrator");

    let (root, g) = fresh("ws3-r2-sites");
    // BC-P2-08: one role per invocation — a `--role` given after `tools install` is the acting role itself (authority
    // and the auto-install conditions are evaluated for it), never a second role an orchestrator lends its authority to
    let d = scratch_file(
        &g,
        "tool.json",
        &json!({"tool_id": "t-r2", "name": "t", "type": "cli", "version": "1", "license": "MIT", "reversible": true}).to_string(),
    );
    let e = g.err(&[
        "tools",
        "install",
        "--descriptor",
        d.to_str().unwrap(),
        "--role",
        "backend-engineer",
    ]);
    assert_eq!(e.error_code(), "AUTHORITY_DENIED", "{}", e.envelope);
    assert_eq!(e.details()["role"], "backend-engineer", "{}", e.envelope);
    // WS-6 IP-6
    assert_eq!(
        g.with_role("")
            .err(&["memory", "miss", "--query", "where is the retry policy?"])
            .error_code(),
        "AUTHORITY_DENIED"
    );
    let m = g.with_role("backend-engineer").ok(&[
        "memory",
        "miss",
        "--query",
        "where is the retry policy?",
        "--expected",
        "D-0002",
    ]);
    assert_eq!(m["status"], "recorded", "{m}");
    let path = m["path"].as_str().unwrap().to_string();
    assert!(path.starts_with("spec/reports/memory-quality/"), "{path}");
    let again = g.with_role("backend-engineer").ok(&[
        "memory",
        "miss",
        "--query",
        "Where is the  retry policy?",
        "--expected",
        "D-0002",
    ]);
    assert_eq!(
        again["status"], "existing",
        "deduplicated by signature: {again}"
    );
    let open = g.ok(&["memory", "failures"]);
    assert!(
        open["open"].to_string().contains(m["id"].as_str().unwrap()),
        "{open}"
    );
    g.ok(&["freeze-writes", "--reason", "incident"]);
    assert_eq!(
        g.err(&["memory", "miss", "--query", "another question"])
            .error_code(),
        "FROZEN"
    );
    // WS-4 IP-6 with O-4: a damaged derived index, then its recovery under the freeze
    std::fs::write(
        root.join(".governance-runtime/state.db"),
        b"this is not a database",
    )
    .unwrap();
    let _ = std::fs::remove_file(root.join(".governance-runtime/state.db-wal"));
    let _ = std::fs::remove_file(root.join(".governance-runtime/state.db-shm"));
    g.ok(&["resume"]);
    let e = g.err(&["continue"]);
    assert_eq!(e.error_code(), "INDEX_UNAVAILABLE", "{}", e.envelope);
    assert_eq!(e.details()["remediation"], "gov rebuild-memory");
    g.ok(&["freeze-writes", "--reason", "repair the index"]);
    std::fs::remove_file(root.join(".governance-runtime/state.db")).unwrap();
    g.ok(&["rebuild-memory"]);
    g.ok(&["resume"]);
    g.ok(&["continue"]);
}
