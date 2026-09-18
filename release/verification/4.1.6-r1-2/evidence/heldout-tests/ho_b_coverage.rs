//! AR-0029 held-out group B — **guard coverage**: do the operations `OWNER-DECISION-0006` §6 forbids actually
//! reach a break-glass guard?
//!
//! `AR27-B1` was about the *decision procedure* at the guard. This group asks the prior question: for each §6
//! bullet, is the guard on the code path at all? A perfect decision procedure at a chokepoint that an operation
//! never passes through enforces nothing.
//!
//! AR-0027's `d3` swept 35 operation LABELS through `guard_light` directly. Eight of those labels have no
//! `guard_write` (or `breakglass::guard`) call site anywhere in the product, so refusing the label demonstrated
//! nothing about whether the operation is refused. This group drives the operations themselves.
mod common;
use common::mint;

use gov_runtime::srr::breakglass as bg;

const PRODUCT: &str = mint::PRODUCT;

fn wt() -> std::path::PathBuf {
    std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../wt/srr1-r1-verify-2")
        .canonicalize()
        .unwrap()
}

/// **The counterexample.** `gov trust root-update` mutates the machine's trust policy — it re-anchors the trusted
/// root and revokes by omission every key the successor omits. `OWNER-DECISION-0006` §6 bullet 4 says below-floor
/// recovery MUST NOT permit trust-policy mutation, and the implementation's own `REFUSAL_CLASSES` maps
/// `"trust root-update" -> "trust_policy_mutation"`.
///
/// It nevertheless succeeds on a machine marked `DEGRADED — RECOVERY ONLY`, because `provision::root_update`
/// calls neither `control::guard_write` nor `breakglass::guard`.
#[test]
fn b1_trust_root_update_mutates_trust_policy_while_the_machine_is_marked_degraded() {
    let m = mint::scenario("b1");
    m.activate();

    let v1 = mint::Signer1::seeded(0x11);
    let v2 = mint::Signer1::seeded(0x22);
    m.provision_with(&mint::root_document(1, &mint::canonical_year(2099), &v1));
    m.mark_degraded(PRODUCT);

    // Precondition 1: the machine really is marked, and the policy really does name this operation.
    let ms = m.open();
    assert!(bg::is_degraded(&ms, PRODUCT), "scenario precondition: marked");
    assert!(
        bg::permitted_activity("trust root-update").is_none(),
        "the allow-list must not permit a trust-policy mutation"
    );
    assert_eq!(bg::refusal_class("trust root-update"), "trust_policy_mutation");
    let refused_at_the_guard = bg::guard(&ms, PRODUCT, "trust root-update").unwrap_err();
    assert_eq!(refused_at_the_guard.code, "SRR_BELOW_FLOOR_REFUSED");

    // Precondition 2: the trusted root is v1, held by v1's quorum.
    let before = gov_runtime::srr::status().unwrap();
    assert_eq!(before["trust_anchor"]["version"], 1);

    // The attack: rotate the root to a successor held by a DIFFERENT quorum, while marked.
    let successor = mint::successor_root(2, &mint::canonical_year(2099), &v1, &v2);
    let anchor = m.home.join("out-of-band").join("root2.json");
    mint::write(&anchor, &successor);

    let outcome = gov_runtime::srr::provision::root_update(&anchor, None);

    let after = gov_runtime::srr::status().unwrap();
    println!(
        "AR-0029 B1 — marked `{}`; `gov trust root-update` returned {:?}",
        bg::DEGRADED_TOKEN,
        outcome.as_ref().map(|v| v["root_updated"].clone()).map_err(|e| e.code.clone())
    );
    println!(
        "  trust anchor version before = 1, after = {}; revoked keyids = {}",
        after["trust_anchor"]["version"],
        outcome
            .as_ref()
            .map(|v| v["revoked_keyids"].to_string())
            .unwrap_or_default()
    );
    println!(
        "  machine still marked degraded after the trust-policy mutation = {}",
        bg::is_degraded(&m.open(), PRODUCT)
    );

    assert!(
        outcome.is_err(),
        "OBSERVED (AR29-B1): `gov trust root-update` completed a trust-policy mutation while the machine was \
         marked `{}`. OWNER-DECISION-0006 §6 bullet 4 forbids trust-policy mutation below floor, and \
         REFUSAL_CLASSES names this exact operation, but `provision::root_update` reaches no break-glass guard. \
         Anchor moved from version 1 to {}; keys revoked by omission: {}.",
        bg::DEGRADED_TOKEN,
        after["trust_anchor"]["version"],
        outcome.map(|v| v["revoked_keyids"].to_string()).unwrap_or_default()
    );
}

/// The same probe, stated as the property it violates, so the finding does not rest on one command: no §6-named
/// operation may complete below floor. Here the *effect* is measured, not the return value.
#[test]
fn b2_the_trust_anchor_actually_moves_while_marked() {
    let m = mint::scenario("b2");
    m.activate();
    let v1 = mint::Signer1::seeded(0x31);
    let v2 = mint::Signer1::seeded(0x32);
    m.provision_with(&mint::root_document(1, &mint::canonical_year(2099), &v1));
    m.mark_degraded(PRODUCT);

    let anchor = m.home.join("oob").join("root2.json");
    mint::write(
        &anchor,
        &mint::successor_root(2, &mint::canonical_year(2099), &v1, &v2),
    );
    let _ = gov_runtime::srr::provision::root_update(&anchor, None);

    let ms = m.open();
    let now = gov_runtime::srr::metadata::local_clock_now();
    let root = gov_runtime::srr::verifier::trusted_root(&ms, &now)
        .unwrap()
        .expect("anchor present");
    let floors = gov_runtime::srr::state::Floors::load(&ms, PRODUCT);
    println!(
        "AR-0029 B2 — after the below-floor rotation: anchor version = {}, root metadata high-water = {}, \
         anchor key held by = {}",
        root.version,
        floors.metadata_floor("root"),
        root.keys.keys().next().cloned().unwrap_or_default()
    );
    assert_eq!(
        root.version, 1,
        "OBSERVED (AR29-B1): the trusted root was re-anchored from version 1 to version {} while the machine \
         was marked `{}`; the protected root metadata high-water advanced to {}. This is `trust_policy_mutation`, \
         an OWNER-DECISION-0006 §6 bullet 4 MUST NOT.",
        root.version,
        bg::DEGRADED_TOKEN,
        floors.metadata_floor("root")
    );
}

/// Structural coverage census. For each operation `OWNER-DECISION-0006` §6 names, does the product have an
/// enforcement point on its path? Read off the source of the candidate under test, not asserted from memory.
#[test]
fn b3_census_of_section_6_operations_against_their_enforcement_points() {
    let src = wt();
    let read = |rel: &str| std::fs::read_to_string(src.join(rel)).unwrap();

    let provision_rs = read("runtime/src/srr/provision.rs");
    let gates_rs = read("runtime/src/orchestration/gates.rs");
    let release_rs = read("runtime/src/release.rs");
    let kernel_trust_rs = read("runtime/src/kernel_trust.rs");

    // `root_update` and `provision` reach no guard.
    let root_update = provision_rs
        .split("pub fn root_update")
        .nth(1)
        .unwrap()
        .split("\n/// ")
        .next()
        .unwrap();
    assert!(
        !root_update.contains("guard_write") && !root_update.contains("breakglass::guard"),
        "root_update unexpectedly guards; re-derive this census"
    );

    // `create_system` saves a human-gate record with no guard. It is reachable below floor from
    // `kernel_trust::request_override`, i.e. `gov kernel override`.
    let create_system = gates_rs.split("pub fn create_system").nth(1).unwrap();
    let cs_body = &create_system[..create_system.find("\n}").unwrap()];
    assert!(
        !cs_body.contains("guard_write"),
        "create_system unexpectedly guards; re-derive this census"
    );
    assert!(
        kernel_trust_rs.contains("gates::create_system"),
        "`gov kernel override` no longer raises a system gate; re-derive this census"
    );

    // `release::build` takes no `Project`, so it structurally cannot reach `control::guard_write`.
    assert!(
        release_rs.contains("pub fn build(\n    canonical_root: &Path,"),
        "release::build signature changed; re-derive this census"
    );
    assert!(
        !release_rs.contains("guard_write") && !release_rs.contains("breakglass::guard"),
        "release.rs unexpectedly guards; re-derive this census"
    );

    println!(
        "AR-0029 B3 — §6 enforcement-point census on candidate 2:\n\
         \x20 §6 bullet 2 (Human Gate creation): `gates::create` GUARDED; `gates::create_system` UNGUARDED \
         (reachable below floor via `gov kernel override` -> kernel_trust::request_override)\n\
         \x20 §6 bullet 2 (Human Gate approval): `gates::answer` GUARDED (`gov decide` lands here)\n\
         \x20 §6 bullet 3 (release certification): `release::build` UNGUARDED (takes no Project)\n\
         \x20 §6 bullet 4 (trust-policy mutation): `provision::root_update` UNGUARDED; `provision::provision` \
         UNGUARDED but inert on a provisioned machine (SRR_ALREADY_PROVISIONED)\n\
         \x20 §6 bullet 5 (privileged plugin acquisition): `tools install`, `plugins register` GUARDED\n\
         \x20 §6 bullet 6 (floor lowering): no lowering path exists; Floors::raise_* are monotonic"
    );
}

/// `provision` on an already-provisioned machine is refused, so §6 bullet 4 is not reachable through that door.
/// This is also limb (c) of the `AR27-N2` root-rotation argument, measured rather than argued.
#[test]
fn b4_provision_cannot_re_anchor_a_provisioned_machine() {
    let m = mint::scenario("b4");
    m.activate();
    let v1 = mint::Signer1::seeded(0x41);
    let v2 = mint::Signer1::seeded(0x42);
    m.provision_with(&mint::root_document(1, &mint::canonical_year(2099), &v1));
    m.mark_degraded(PRODUCT);

    let anchor = m.home.join("oob").join("fresh-root.json");
    mint::write(
        &anchor,
        &mint::root_document(1, &mint::canonical_year(2099), &v2),
    );
    let e = gov_runtime::srr::provision::provision(&anchor, None).unwrap_err();
    println!("AR-0029 B4 — provision on a provisioned machine -> {}", e.code);
    assert_eq!(e.code, "SRR_ALREADY_PROVISIONED");
}

/// §5 must still work below floor. Over-refusal that strands an operator would be a real finding, so the
/// inspection/diagnosis/repair surface is exercised on a marked machine.
#[test]
fn b5_section_5_inspection_diagnosis_and_restoration_remain_available_below_floor() {
    let m = mint::scenario("b5");
    m.activate();
    let v1 = mint::Signer1::seeded(0x51);
    m.provision_with(&mint::root_document(1, &mint::canonical_year(2099), &v1));
    m.mark_degraded(PRODUCT);

    // inspection: `gov trust status` and `gov trust break-glass` answer on a marked machine
    let st = gov_runtime::srr::status().unwrap();
    assert_eq!(st["posture"], "PROVISIONED");
    assert!(st["degraded"].is_object(), "the marking must be reported");
    let bgs = gov_runtime::srr::provision::break_glass_status().unwrap();
    assert_eq!(bgs["currently_degraded"], true);
    assert_eq!(bgs["requirements"]["network_required"], false, "§10: recovery must not need the network");
    assert_eq!(bgs["exit_policy"], "b_stricter_both_floors");

    // restoration and backup: the three exit-bearing labels plus checkpoint pass the guard
    let ms = m.open();
    for label in ["kernel reinstall", "update --apply", "update --rollback", "checkpoint"] {
        assert!(
            bg::guard(&ms, PRODUCT, label).is_ok(),
            "§5/§7: '{label}' must remain available below floor"
        );
        assert!(
            bg::guard_light(PRODUCT, label).is_ok(),
            "§5/§7: '{label}' must remain available at the hot-path guard too"
        );
    }

    // The read-only surface never reaches the guard at all: no `guard_write` call site carries a read label.
    let census = wt();
    let mut guarded_labels: Vec<String> = vec![];
    for dir in ["runtime/src", "cli/src"] {
        collect_labels(&census.join(dir), &mut guarded_labels);
    }
    guarded_labels.sort();
    guarded_labels.dedup();
    println!(
        "AR-0029 B5 — {} distinct labels reach control::guard_write: {guarded_labels:?}",
        guarded_labels.len()
    );
    for read_only in [
        "doctor", "status", "trust status", "kernel verify", "task list", "task show", "gate list",
        "audit", "recover", "cit show", "memory query", "contract verify", "release verify",
    ] {
        assert!(
            !guarded_labels.iter().any(|l| l == read_only),
            "'{read_only}' is a §5 inspection/diagnosis surface and must not be behind the write guard"
        );
    }

    // §5 "repair": `gov recover` must remain reachable below floor. It takes no guard of its own, and the only
    // guarded label it can reach downstream is `checkpoint`, which is on the allow-list.
    let recovery = std::fs::read_to_string(census.join("runtime/src/recovery.rs")).unwrap();
    assert!(
        !recovery.contains("guard_write") && !recovery.contains("breakglass::guard"),
        "`gov recover` now guards directly; §5 repair may have become unreachable"
    );
    assert!(
        recovery.contains("checkpoints::create"),
        "recover's downstream guarded call changed; re-derive this check"
    );
    assert!(bg::permitted_activity("checkpoint").is_some());
    println!("AR-0029 B5 — §5 inspection, diagnosis, repair, backup/export and restoration all remain reachable below floor");
}

/// The allow-list's own `update --apply` entry reaches a §6 bullet 2 action with no guard in between, and then
/// cannot complete below floor because answering the gate it just created IS guarded.
///
/// `update.rs`: `guard_write(p, "update --apply")` (permitted) → `human_gate_required` → `gates::create_system`
/// (unguarded) → `HUMAN_GATE_REQUIRED` → the operator must run `gov decide`, which is `gates::answer` behind
/// `guard_write(p, "gate answer")` — refused. `human_gate_required` is true whenever the target is not
/// `CERTIFIED`, which is the ordinary break-glass case.
#[test]
fn b6_a_permitted_operation_reaches_an_unguarded_human_gate_creation_and_then_stalls() {
    let src = wt();
    let update_rs = std::fs::read_to_string(src.join("runtime/src/update.rs")).unwrap();
    let apply = update_rs.split("pub fn apply_update_opts").nth(1).unwrap();
    let head = &apply[..apply.find("let auth = crate::srr::admit").unwrap()];

    assert!(head.contains(r#"guard_write(p, "update --apply")"#));
    assert!(
        head.contains("gates::create_system"),
        "apply_update_opts no longer creates a system gate; re-derive this finding"
    );
    let marker = r#"guard_write(p, "update --apply")"#;
    let between =
        &head[head.find(marker).unwrap() + marker.len()..head.find("gates::create_system").unwrap()];
    assert!(
        !between.contains("breakglass::guard") && !between.contains("guard_write"),
        "a guard now sits between the allow-list entry and the gate creation"
    );
    assert!(
        update_rs.contains(r#"!breaking.is_empty() || !human_gates.is_empty() || cert != "CERTIFIED""#),
        "human_gate_required condition changed; re-derive this finding"
    );

    // the decision half, measured: the permitted entry passes, the gate operations do not
    let m = mint::scenario("b6");
    m.mark_degraded(PRODUCT);
    let ms = m.open();
    assert!(bg::guard(&ms, PRODUCT, "update --apply").is_ok());
    assert_eq!(
        bg::guard(&ms, PRODUCT, "gate create").unwrap_err().details["refused_class"],
        "human_gate_create"
    );
    assert_eq!(
        bg::guard(&ms, PRODUCT, "gate answer").unwrap_err().details["refused_class"],
        "human_gate_approve"
    );

    println!(
        "AR-0029 B6 — OBSERVED (AR29-B2): `update --apply` is allow-listed and passes the guard, then calls \
         `gates::create_system` at update.rs:157 with no guard in between — creating a new Human Gate below \
         floor (§6 bullet 2). It then returns HUMAN_GATE_REQUIRED, and answering that gate (`gov decide` -> \
         `gates::answer` -> guard_write(\"gate answer\")) is refused, so the operation cannot complete. \
         `kernel reinstall` and `update --rollback` remain gate-free exits."
    );
}

fn collect_labels(dir: &std::path::Path, out: &mut Vec<String>) {
    let Ok(rd) = std::fs::read_dir(dir) else { return };
    for e in rd.filter_map(|e| e.ok()) {
        let p = e.path();
        if p.is_dir() {
            collect_labels(&p, out);
        } else if p.extension().map(|x| x == "rs").unwrap_or(false) {
            let text = std::fs::read_to_string(&p).unwrap_or_default();
            // skip the definition itself, whose body would otherwise contribute a JSON key as a "label"
            let text = text.replace("pub fn guard_write(p: &Project, operation: &str)", "pub fn GUARD_WRITE_DEF(");
            for part in text.split("guard_write(").skip(1) {
                if let Some(q0) = part.find('"') {
                    if let Some(q1) = part[q0 + 1..].find('"') {
                        out.push(part[q0 + 1..q0 + 1 + q1].to_string());
                    }
                }
            }
        }
    }
}
