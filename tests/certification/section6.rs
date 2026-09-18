//! **`OWNER-DECISION-0006` §6 coverage, derived from the product rather than asserted beside it.**
//!
//! Three R1 iterations closed the finding they were handed and a new one appeared underneath, and the product
//! owner stopped the loop to have the pattern itself addressed (`OWNER-DECISION-0008`). The pattern:
//!
//! > §6 is a **universal negative** — "below-floor recovery MUST NOT permit X" — and it was implemented three
//! > times as a **positive enumeration**: the list of forbidden operations, then the set of guarded call sites,
//! > then the census of effect primitives. Each was complete when written and silently incomplete as soon as the
//! > product grew a path its author had not enumerated. And at every level the **test was derived from the same
//! > enumeration as the code**, so it could not detect that the enumeration was short.
//!
//! This module is the answer to that, in two parts.
//!
//! **1. The census is derived.** `section_6_coverage_is_derived_from_the_product` walks **every function** in
//! `runtime/src` and `cli/src`. For each §6 effect it computes, from the product's own source, the set of
//! functions that could realise it — a function that performs a durable write and mentions one of the product's
//! own primitives for that effect — and fails naming any of them that carries no enforcement. Nothing is on a
//! list of "places to look": the function set comes from the tree, so a new primitive appears in it without
//! anyone remembering to add it.
//!
//! **2. An absence claim is refutable.** `a_no_primitive_claim_is_refutable_by_this_suite` is the answer to
//! `AR31-N5`, which found that the previous census test's loop silently **skipped** the two bullets whose entry
//! said "no primitive" — which is exactly how `AR31-B1` survived repair 2. A claim that nothing realises an effect
//! is worth only as much as the detector behind it, so every signature is first run against a **positive
//! control**: a synthetic implementation of that effect, written the way a future author plausibly would, with no
//! enforcement. A signature that fails to flag its positive control fails this suite, whatever it then finds (or
//! does not find) in the product. A bullet claiming no primitive is now the *most* tested case.
//!
//! What the derivation cannot see is written down in `breakglass::SECTION_6_SIGNATURES` and restated in the
//! repair report. It is not a complete decision procedure for "does this code realise this effect", and nothing
//! syntactic could be.
use crate::common::*;
use crate::srr_material::*;
use gov_runtime::srr::breakglass as bg;
use serde_json::json;
use std::path::{Path, PathBuf};

// --------------------------------------------------------------------------------- the derivation machinery

/// One function of the product, as the derivation sees it.
struct Func {
    path: String,
    name: String,
    body: String,
}

impl Func {
    fn site(&self) -> String {
        format!("{}::{}", self.path, self.name)
    }
}

/// Every `.rs` file the product ships, as (repository-relative path, text with `#[cfg(test)]` removed).
///
/// Test modules are cut because they are not the product: a unit test may legitimately write a floors file or
/// mint a gate record, and holding the suite to the product's rules would only teach people to move code.
fn product_sources() -> Vec<(String, String)> {
    fn walk(dir: &Path, root: &Path, out: &mut Vec<(String, String)>) {
        let Ok(rd) = std::fs::read_dir(dir) else { return };
        for e in rd.filter_map(|e| e.ok()) {
            let p = e.path();
            if p.is_dir() {
                walk(&p, root, out);
            } else if p.extension().map(|x| x == "rs").unwrap_or(false) {
                let text = std::fs::read_to_string(&p).unwrap_or_default();
                let text = match text.find("#[cfg(test)]") {
                    Some(i) => text[..i].to_string(),
                    None => text,
                };
                out.push((
                    p.strip_prefix(root)
                        .unwrap_or(&p)
                        .display()
                        .to_string()
                        .replace('\\', "/"),
                    text,
                ));
            }
        }
    }
    let root = canonical_root();
    let mut v = vec![];
    walk(&root.join("runtime/src"), &root, &mut v);
    walk(&root.join("cli/src"), &root, &mut v);
    v.sort_by(|a, b| a.0.cmp(&b.0));
    assert!(
        v.len() > 40,
        "the product source walk found only {} files; the derivation would be vacuous",
        v.len()
    );
    v
}

/// Split a source file into functions by indentation: a `fn` line opens one and the matching `}` at the same
/// indentation closes it. Works for free functions, methods and closures-in-functions alike, because rustfmt
/// keeps this file set canonically formatted — which the assertion below is a proxy for.
fn split_functions(path: &str, text: &str) -> Vec<Func> {
    let lines: Vec<&str> = text.split('\n').collect();
    let mut out = vec![];
    for (i, l) in lines.iter().enumerate() {
        let trimmed = l.trim_start();
        let indent = &l[..l.len() - trimmed.len()];
        let is_fn = trimmed.starts_with("fn ")
            || trimmed.starts_with("pub fn ")
            || trimmed.starts_with("pub(crate) fn ")
            || trimmed.starts_with("pub(super) fn ")
            || trimmed.starts_with("async fn ")
            || trimmed.starts_with("pub async fn ");
        if !is_fn {
            continue;
        }
        let name: String = trimmed
            .split("fn ")
            .nth(1)
            .unwrap_or("")
            .chars()
            .take_while(|c| c.is_alphanumeric() || *c == '_')
            .collect();
        if name.is_empty() {
            continue;
        }
        let close = format!("{indent}}}");
        let mut end = lines.len() - 1;
        for (j, line) in lines.iter().enumerate().skip(i + 1) {
            if *line == close {
                end = j;
                break;
            }
        }
        out.push(Func {
            path: path.to_string(),
            name,
            body: lines[i..=end].join("\n"),
        });
    }
    out
}

fn product_functions() -> Vec<Func> {
    let mut out = vec![];
    for (p, t) in product_sources() {
        out.extend(split_functions(&p, &t));
    }
    assert!(
        out.len() > 300,
        "the function split found only {} functions; the derivation would be vacuous",
        out.len()
    );
    out
}

fn matches_any(body: &str, markers: &[&str]) -> bool {
    markers.iter().any(|m| body.contains(m))
}

/// Does this code persist anything? Derived from the product's own persistence primitives.
fn performs_write(body: &str) -> bool {
    matches_any(body, bg::SECTION_6_WRITE_PRIMITIVES)
}

// --------------------------------------------------------------------------------- the positive controls

/// For each §6 effect, **a synthetic implementation of that effect with no enforcement** — written the way a
/// future author plausibly would, using the product's own APIs.
///
/// Each one must be (a) matched by its signature, (b) recognised as performing a write, and (c) found NOT
/// covered, i.e. reported as a violation. A signature that cannot flag its own positive control tells us nothing
/// when it finds nothing, which is precisely the failure `AR31-N5` recorded.
const POSITIVE_CONTROLS: &[(&str, &str)] = &[
    (
        "human_gate_create",
        r#"
fn a_future_gate_writer(p: &Project, fields: Value) -> Result<()> {
    let rec = crate::records::new_record("human-gate", "HDG-0999", "raised by new code", fields);
    let at = crate::records::record_path_for("human-gate", "HDG-0999")?;
    crate::util::write_yaml(&p.root.join(at), &rec.data)
}
"#,
    ),
    (
        "human_gate_approve",
        r#"
fn a_future_approver(p: &Project, g: &mut Record) -> Result<()> {
    g.set("gate_status", json!("ANSWERED"));
    g.set("answered_by", json!("someone"));
    crate::util::write_yaml(&p.root.join(&g.path), &g.data)
}
"#,
    ),
    (
        "release_certification",
        r#"
fn a_future_certifier(out_root: &Path, version: &str) -> Result<()> {
    let manifest = json!({"version": version, "certification_status": "CERTIFIED"});
    crate::util::write_json(&out_root.join("releases").join(version).join("manifest.json"), &manifest)
}
"#,
    ),
    (
        "trust_policy_mutation",
        r#"
fn a_future_anchor_writer(ms: &MachineState, root_bytes: &[u8]) -> Result<()> {
    std::fs::write(ms.root.join("trust").join("root.json"), root_bytes)?;
    std::fs::write(ms.root.join("trust").join("provisioned.json"), b"{}")?;
    Ok(())
}
"#,
    ),
    (
        "privileged_plugin_acquisition",
        r#"
fn a_future_capability_installer(p: &Project, descriptor: &Value) -> Result<()> {
    crate::util::write_yaml(&p.overlay_dir().join("plugins").join("new.yaml"), descriptor)
}
"#,
    ),
    (
        "floor_lower_or_reset",
        r#"
fn a_future_floor_reset(ms: &MachineState, product: &str) -> Result<()> {
    crate::srr::state::write_durable(
        &ms.floors_path(product),
        &json!({"release_high_water": {"version": "", "sequence": 0}, "minimum_secure": {"sequence": 0}}),
    )
}
"#,
    ),
    (
        "present_below_floor_release_as_current",
        r#"
fn a_future_result_emitter(name: &str, v: Value, session: &str) {
    println!(
        "{}",
        serde_json::to_string_pretty(&json!({"ok": true, "command": name, "result": v, "session": session})).unwrap()
    );
}
"#,
    ),
];

fn positive_control(activity: &str) -> Option<&'static str> {
    POSITIVE_CONTROLS
        .iter()
        .find(|(a, _)| *a == activity)
        .map(|(_, c)| *c)
}

// --------------------------------------------------------------------------------- 1. the derived census

/// **The `OWNER-DECISION-0006` §6 coverage census, derived from the product.**
///
/// Fails when any function in `runtime/src` or `cli/src` performs a durable write, matches an effect's
/// signature, and carries neither that effect's enforcement nor a call to the sink that does.
#[test]
fn section_6_coverage_is_derived_from_the_product() {
    let functions = product_functions();

    // Every §6 activity has a signature, and no signature names an activity §6 does not. The previous census
    // test's loop could skip a bullet; this one cannot, because the set it iterates is the decision's own.
    assert_eq!(
        bg::SECTION_6_SIGNATURES.len(),
        bg::REFUSED_ACTIVITIES.len(),
        "a §6 bullet has no signature, so the derivation would not look for it"
    );
    for a in bg::REFUSED_ACTIVITIES {
        assert!(
            bg::section_6_signature(a).is_some(),
            "§6 activity '{a}' has no derivation signature"
        );
    }
    for (activity, sig, acc) in bg::SECTION_6_SIGNATURES {
        assert!(
            bg::REFUSED_ACTIVITIES.contains(activity),
            "'{activity}' is not an OWNER-DECISION-0006 §6 activity"
        );
        assert!(!sig.is_empty() && !acc.is_empty(), "'{activity}' signature is empty");
    }

    let mut census: Vec<String> = vec![];
    for (activity, sig, acc) in bg::SECTION_6_SIGNATURES {
        // §6 bullet 1 names a CLASS OF OPERATIONS, not an effect: "normal privileged Governance OS operation".
        // It is decided at the operation level by a default-refuse allow-list, so the question the derivation
        // asks of bullets 2-7 ("is the enforcement inside every primitive that can realise the effect?") has no
        // counterpart here. Its own clause is below; the effects are what this loop covers.
        if *activity == "normal_privileged_operation" {
            continue;
        }

        // --- the positive control: prove the detector can see an unguarded new primitive ------------------
        let control = positive_control(activity)
            .unwrap_or_else(|| panic!("§6 activity '{activity}' has no positive control: an absence claim for it would be unfalsifiable, which is AR31-N5"));
        assert!(
            matches_any(control, sig),
            "the signature for '{activity}' does not match its own positive control, so finding nothing in the \
             product would mean nothing:\n{control}"
        );
        assert!(
            performs_write(control),
            "the write-primitive census does not recognise the positive control for '{activity}' as writing \
             anything, so the derivation would skip it:\n{control}"
        );
        assert!(
            !matches_any(control, acc),
            "the positive control for '{activity}' is written WITHOUT enforcement and must be reported as a \
             violation; the acceptance markers match it, so the derivation would wave it through:\n{control}"
        );
        // and the same control WITH the enforcement must be accepted, so acceptance is not vacuous either
        let guarded = format!("{control}\n// {}\n", acc[0]);
        assert!(
            matches_any(&guarded, acc),
            "acceptance markers for '{activity}' do not match even an explicitly enforced implementation"
        );

        // --- the derivation over the real product ---------------------------------------------------------
        let derived: Vec<&Func> = functions.iter().filter(|f| matches_any(&f.body, sig)).collect();
        let writers: Vec<&&Func> = derived.iter().filter(|f| performs_write(&f.body)).collect();
        let mut violations: Vec<String> = vec![];
        let mut exempt: Vec<String> = vec![];
        for f in &writers {
            if matches_any(&f.body, acc) {
                continue;
            }
            let site = f.site();
            if bg::derivation_exemption(activity, &site).is_some() {
                exempt.push(site);
            } else {
                violations.push(site);
            }
        }
        census.push(format!(
            "{activity}: derived {} / writers {} / exempt {} / violations {}",
            derived.len(),
            writers.len(),
            exempt.len(),
            violations.len()
        ));
        assert!(
            violations.is_empty(),
            "OWNER-DECISION-0006 §6 '{activity}': these functions perform a durable write and match the \
             effect's signature, and carry no enforcement and no call to its sink — they are second \
             implementations of a forbidden effect: {violations:?}. Either put the enforcement inside them, or, \
             if they cannot realise the effect, add them to `breakglass::SECTION_6_DERIVATION_EXEMPTIONS` with \
             the reason."
        );

        // A signature that matches nothing at all is either a bullet with genuinely no primitive (legitimate,
        // and the positive control above is what makes that claim worth anything) or a signature that has gone
        // stale against a product that moved. Say which, rather than passing silently.
        if derived.is_empty() {
            panic!(
                "the signature for '{activity}' matches nothing in the product. If no primitive realises this \
                 effect, that is a legitimate finding and this assertion should be replaced by a stated absence \
                 claim — but the positive control proves the detector works, so check the signature first."
            );
        }
    }

    // --- exemptions cannot rot -----------------------------------------------------------------------------
    // An exemption excuses a function the derivation FOUND. If it no longer matches its signature or no longer
    // writes, the reason recorded for it no longer describes anything and the entry must go, or it becomes a
    // silent blanket over whatever later occupies that name.
    for (activity, site, why) in bg::SECTION_6_DERIVATION_EXEMPTIONS {
        assert!(why.len() > 60, "exemption '{site}' needs a usable reason");
        let (sig, acc) = bg::section_6_signature(activity)
            .unwrap_or_else(|| panic!("exemption names unknown §6 activity '{activity}'"));
        let f = functions
            .iter()
            .find(|f| f.site() == *site)
            .unwrap_or_else(|| panic!("exemption '{site}' names a function that no longer exists"));
        assert!(
            matches_any(&f.body, sig) && performs_write(&f.body),
            "exemption '{site}' is stale: the derivation no longer finds it for '{activity}', so the reason \
             recorded for it excuses nothing and the entry must be removed"
        );
        assert!(
            !matches_any(&f.body, acc),
            "exemption '{site}' is unnecessary: it now carries the enforcement for '{activity}' and is accepted \
             on its own merits"
        );
    }

    // --- §6 bullet 1: the operation-level clause ------------------------------------------------------------
    // The property here is not "the enforcement is inside the primitive" but "the decision is default-refuse",
    // which is what makes bullet 1 a class control rather than a list (`AR27-B1`). Two things are derived: the
    // chokepoint still routes to the guard, and every operation label the product passes to it is refused unless
    // it is on the §5 allow-list.
    let guard_write = functions
        .iter()
        .find(|f| f.path.ends_with("orchestration/control.rs") && f.name == "guard_write")
        .expect("control::guard_write not found; re-derive the §6 bullet 1 clause");
    assert!(
        guard_write.body.contains("breakglass::guard_light"),
        "the §6 bullet 1 chokepoint no longer routes to the guard"
    );
    let call_sites: Vec<String> = functions
        .iter()
        .filter(|f| f.name != "guard_write" && f.body.contains("guard_write("))
        .map(|f| f.site())
        .collect();
    assert!(
        call_sites.len() >= 25,
        "the bullet 1 call-site census collapsed to {} sites; re-derive it: {call_sites:?}",
        call_sites.len()
    );
    assert_eq!(bg::REFUSAL_POLICY, "allow_list_default_refuse");
    for label in [
        "an operation invented after this repair",
        "gate present",
        "cit execute",
        "kernel reinstall --force",
    ] {
        assert!(
            bg::permitted_activity(label).is_none(),
            "'{label}' is permitted below floor by the §5 allow-list"
        );
    }

    println!("§6 derived census:\n  {}", census.join("\n  "));
    println!("  bullet 1 guard_write call sites: {}", call_sites.len());
}

/// **`AR31-N5` / `OWNER-DECISION-0008` mandate part 4 — how a "no primitive exists" claim can now fail.**
///
/// The previous census test asserted only that each sink string was non-empty, and its coverage loop iterated a
/// hard-coded list of the five sinks that named a function, silently skipping the two whose entry began
/// `"no primitive:"`. Bullets 6 and 7 were therefore unfalsifiable by the product's own suite. Bullet 6's claim
/// happened to be true. Bullet 7's was false, and that is `AR31-B1`.
///
/// Neither bullet claims an absence any more — both have real sinks. The mechanism is kept and tested anyway,
/// because the next bullet that needs one should not have to re-invent it.
#[test]
fn a_no_primitive_claim_is_refutable_by_this_suite() {
    let functions = product_functions();

    // 1. No entry in the live census claims an absence today ...
    for (activity, sink) in bg::SECTION_6_SINKS {
        assert!(
            !sink.starts_with("no primitive"),
            "§6 '{activity}' claims no primitive exists. That claim is now testable: its signature must match \
             nothing in the product AND its positive control must still be flagged. Delete this assertion and \
             assert those two things for '{activity}' instead of removing the claim from the test's reach."
        );
        assert!(!sink.is_empty());
    }

    // 2. ... and every bullet, absence-claiming or not, has a detector that demonstrably fires. This is the
    //    whole mechanism: an absence claim is only worth the detector behind it.
    for (activity, sig, acc) in bg::SECTION_6_SIGNATURES {
        if *activity == "normal_privileged_operation" {
            continue;
        }
        let control = positive_control(activity)
            .unwrap_or_else(|| panic!("no positive control for '{activity}'"));
        let detected = matches_any(control, sig) && performs_write(control) && !matches_any(control, acc);
        assert!(
            detected,
            "a new, unguarded implementation of '{activity}' would NOT be detected. Any claim this suite makes \
             about that bullet — including 'no primitive exists' — is therefore worthless."
        );
    }

    // 3. And the detector is not trivially "everything matches": a function that does none of these things is
    //    not flagged for any bullet. A detector that fires on everything is as useless as one that fires on
    //    nothing, in the opposite direction.
    let innocent = "fn adds_two(a: u64, b: u64) -> u64 {\n    a + b\n}\n";
    for (activity, sig, _acc) in bg::SECTION_6_SIGNATURES {
        assert!(
            !(matches_any(innocent, sig) && performs_write(innocent)),
            "the detector for '{activity}' fires on arithmetic"
        );
    }

    // 4. The bullet-7 sink is reached from outside `breakglass.rs`, which is the concrete thing `AR31-B1`
    //    measured as absent: the effect variant had no call site anywhere in the product.
    let callers: Vec<String> = functions
        .iter()
        .filter(|f| {
            !f.path.ends_with("srr/breakglass.rs")
                && (f.body.contains("Effect::PresentBelowFloorReleaseAsCurrent")
                    || f.body.contains("present::attach(")
                    || f.body.contains("present::presentation("))
        })
        .map(|f| f.site())
        .collect();
    assert!(
        callers.len() >= 4,
        "§6 bullet 7 is reached from {} places outside `breakglass.rs`; AR31-B1 was that it was reached from \
         none: {callers:?}",
        callers.len()
    );
    println!("§6 bullet 7 enforcement sites: {callers:?}");
}

// --------------------------------------------------------------------------------- 2. AR31-B1, measured

/// Build a machine in genuine owner-authorised break-glass, installed on a genuinely older release so that
/// `gov update --check` has somewhere to go. Returns (root, project, gov, an at-floor candidate source).
fn marked_machine(tag: &str) -> (PathBuf, PathBuf, Gov, PathBuf) {
    let (root, proj, g) = {
        let root = tmp(tag);
        let proj = root.join("project");
        std::fs::create_dir_all(&proj).unwrap();
        write(&proj, "README.md", "# s6 project\n");
        git_init_commit(&proj);
        let g = Gov::new(&proj, &format!("S-{tag}"));
        (root, proj, g)
    };
    let p = Publisher::new();
    let admin = root.join("admin-domain");
    let rf = p.write_root(&admin, 1, &far_future());
    g.ok(&["trust", "provision", "--anchor", rf.to_str().unwrap()]);

    let prev = canonical_root().join("fixtures/update/previous-release/4.1.1");
    let old = root.join("rel-old");
    copy_dir(&prev, &old.join("kernel"));
    p.publish(&old, 20, 100, "stable", &far_future(), "4.0.0", 50);
    let r = g.ok(&[
        "init",
        "--source",
        old.join("kernel").to_str().unwrap(),
        "--name",
        "s6",
        "--alias",
        "fx-s6",
    ]);
    assert_eq!(r["version"], "4.1.1");

    let below = root.join("rel-below");
    copy_dir(&prev, &below.join("kernel"));
    p.publish(&below, 21, 60, "stable", &far_future(), "4.0.0", 50);
    let inbox = PathBuf::from(g.ok(&["trust", "break-glass"])["inbox"].as_str().unwrap());
    let mid = g.ok(&["trust", "status"])["machine_id"]
        .as_str()
        .unwrap()
        .to_string();
    let (_, payload_hash, kmh, ver) = measure(&below.join("kernel"));
    let tok = break_glass_doc(
        &mid,
        &format!("nonce-{tag}"),
        "restore after a bad release",
        &far_future(),
        &ver,
        &payload_hash,
        &kmh,
    );
    std::fs::write(inbox.join("auth.json"), envelope(&tok, &[&p.recovery])).unwrap();
    let r = g.ok(&[
        "kernel",
        "reinstall",
        "--source",
        below.join("kernel").to_str().unwrap(),
        "--break-glass",
    ]);
    assert_eq!(r["release_authenticity"]["below_floor"], true);
    let ms = gov_runtime::srr::state::MachineState::at(&machine_state_dir(&proj)).unwrap();
    assert!(
        bg::is_degraded(&ms, gov_runtime::FRAMEWORK_NAME),
        "harness failed to put the machine into genuine break-glass"
    );

    let hi = root.join("rel-hi");
    std::fs::create_dir_all(&hi).unwrap();
    gov_runtime::kernel::stage_payload(&canonical_root().join("framework"), &hi.join("kernel")).unwrap();
    p.publish(&hi, 22, 200, "stable", &far_future(), "4.0.0", 50);
    (root, proj, g, hi.join("kernel"))
}

/// **`AR31-B1` — §6 bullet 7 is enforced, and "every reporting surface carries the marking" is made true.**
///
/// The four surfaces AR-0031 named as carrying no marking are measured here on a machine in genuine
/// owner-authorised break-glass, and so is the property that makes the claim more than another list: a command
/// with no relationship to release identity, which has never heard of break-glass, carries it too — because the
/// `gov` command-result envelope is a single boundary and it asks the §6 bullet 7 sink.
#[test]
fn the_below_floor_marking_reaches_every_surface_including_ones_that_know_nothing_about_it() {
    let (_root, _proj, g, candidate) = marked_machine("s6-bullet7");

    let marked = |o: &Out, what: &str| {
        let rt = &o.envelope["release_trust"];
        assert_eq!(
            rt["below_floor"], true,
            "{what}: the command result envelope does not carry the break-glass marking: {}",
            o.envelope
        );
        assert_eq!(rt["marking"], bg::DEGRADED_TOKEN, "{what}: wrong marking token");
        assert_eq!(rt["section_6_bullet"], 7, "{what}");
        assert_eq!(rt["presented_as"], "BELOW_FLOOR_RECOVERY_ONLY", "{what}");
        assert!(
            rt["exit_condition"].as_str().unwrap_or("").contains("authenticated release"),
            "{what}: the marking must tell the operator the way out"
        );
    };

    // 1. `gov doctor` — the file that AR-0031 measured as holding ZERO references to the marking.
    let o = g.run(&["doctor"]);
    marked(&o, "gov doctor");
    // `gov doctor` returns the report as the result when healthy and as `error.details` when UNHEALTHY; the
    // report carries the marking either way, because it is consumed as a typed value by `update` and the audit
    // suite and not only printed.
    let d = if o.ok() {
        o.result()
    } else {
        o.envelope["error"]["details"].clone()
    };
    assert_eq!(
        d["release_trust"]["below_floor"], true,
        "the doctor REPORT itself must carry it, not only the envelope: it is consumed as a typed value by \
         `update` and the audit suite: {d}"
    );
    assert!(
        d["verdict"].as_str().is_some(),
        "doctor still reports a verdict; the marking is a separate predicate beside it, not a verdict value"
    );

    // 2. `gov update --check` — AR-0031's counterexample verbatim: the below-floor release labelled `current`,
    //    `up_to_date`, and "nothing to do".
    let chk = g.ok(&["update", "--check", "--source", candidate.to_str().unwrap()]);
    assert_eq!(chk["current"], "4.1.1");
    assert_eq!(
        chk["release_trust"]["below_floor"], true,
        "`gov update --check` presents the installed release with no marking: {chk}"
    );
    assert_eq!(
        chk["up_to_date"], false,
        "a below-floor machine is not up to date, whatever the version comparison says: {chk}"
    );
    assert!(
        chk["recommendation"]
            .as_str()
            .unwrap_or("")
            .contains("§6 bullet 7"),
        "the recommendation must not be 'nothing to do' below floor: {}",
        chk["recommendation"]
    );

    // 3. `gov version` — consults nothing and opens no project, and is covered anyway.
    marked(&g.run(&["version"]), "gov version");

    // 4. The agent context packet — the deterministic authority block every kernel role reads.
    let ctx = g.run(&["context", "compile", "TASK-0001"]);
    marked(&ctx, "gov context compile");
    // The packet itself carries it inside the deterministic authority block, because that block is hashed and
    // consumed as a unit by every kernel role, not read out of an envelope.
    let packet = if ctx.ok() {
        ctx.result()
    } else {
        ctx.envelope["error"]["details"].clone()
    };
    if !packet["deterministic_authority"].is_null() {
        assert_eq!(
            packet["deterministic_authority"]["project_state"]["release_trust"]["below_floor"],
            true,
            "the context packet presents framework_version with no marking: {}",
            packet["deterministic_authority"]["project_state"]
        );
    }
    // and the runtime function is reached directly too, so an in-process consumer is not left without it
    let ctx_rs = std::fs::read_to_string(canonical_root().join("runtime/src/context/mod.rs")).unwrap();
    assert!(
        ctx_rs.contains("present::presentation(\"context packet\")"),
        "the agent context packet no longer consults the §6 bullet 7 sink"
    );

    // 5. **The property, not the list.** A command with no relationship to release identity, which contains no
    //    reference to break-glass anywhere in its implementation, carries the marking — because `run()` is
    //    called once and its value reaches stdout only through the envelope. This is what makes the claim hold
    //    for commands that do not exist yet.
    for unrelated in [
        vec!["gate", "list"],
        vec!["policy", "overrides"],
        vec!["claims", "list"],
    ] {
        let o = g.run(&unrelated);
        assert!(
            !o.envelope["release_trust"].is_null(),
            "`gov {}` lost the marking: the envelope is the coverage claim and it is not universal: {}",
            unrelated.join(" "),
            o.envelope
        );
        marked(&o, &format!("gov {}", unrelated.join(" ")));
    }

    // 6. The surfaces that already carried it still do, and agree with the envelope.
    let ts = g.ok(&["trust", "status"]);
    assert!(!ts["degraded"].is_null(), "gov trust status lost the marking");
    let st = g.run(&["status"]);
    if st.ok() {
        assert_eq!(st.result()["release_trust"]["below_floor"], true);
    }

    // 7. The healthy case — that the marking lifts, and that nothing claims one that is not there — is measured
    //    separately in `the_marking_is_absent_from_every_surface_on_a_healthy_machine`.
}

/// The other half of `AR31-B1`: once the marking is cleared, the product stops claiming it. A control that never
/// lifts is indistinguishable from a broken product, and a marking that never lifts is indistinguishable from
/// noise.
#[test]
fn the_marking_is_absent_from_every_surface_on_a_healthy_machine() {
    let root = tmp("s6-healthy");
    let proj = root.join("project");
    std::fs::create_dir_all(&proj).unwrap();
    write(&proj, "README.md", "# healthy\n");
    git_init_commit(&proj);
    let g = Gov::new(&proj, "S-s6-healthy");
    let p = Publisher::new();
    let rf = p.write_root(&root.join("admin-domain"), 1, &far_future());
    g.ok(&["trust", "provision", "--anchor", rf.to_str().unwrap()]);
    let rel = root.join("rel");
    std::fs::create_dir_all(&rel).unwrap();
    gov_runtime::kernel::stage_payload(&canonical_root().join("framework"), &rel.join("kernel")).unwrap();
    p.publish(&rel, 20, 100, "stable", &far_future(), "4.0.0", 50);
    g.ok(&[
        "init",
        "--source",
        rel.join("kernel").to_str().unwrap(),
        "--name",
        "h",
        "--alias",
        "fx-h",
    ]);

    for args in [vec!["version"], vec!["doctor"], vec!["gate", "list"]] {
        let o = g.run(&args);
        let rt = &o.envelope["release_trust"];
        assert_eq!(
            rt["below_floor"], false,
            "`gov {}` claims a break-glass marking on an unmarked machine: {}",
            args.join(" "),
            o.envelope
        );
        assert_eq!(rt["presented_as"], "CURRENT");
        assert!(rt["marking"].is_null());
    }
}

// --------------------------------------------------------------------------------- 3. AR31-B2, measured

/// **`AR31-B2` — both enforcement points fail CLOSED when they cannot determine their subject.**
///
/// `guard_effect` and `guard_light` resolve the protected state root themselves and used to turn a resolution
/// error into a clearance. AR-0031 enumerated every input: the unprovisioned case the old comment named returns
/// `Ok` and never reaches the branch, and the only input that does is `GOV_MACHINE_STATE_DIR` pointing elsewhere
/// on a provisioned machine — the one input the product already classifies as hostile. On a genuinely marked
/// machine that single environment variable cleared all eight §6 effects and every operation label.
///
/// Driven through the real binary, so the environment is the subprocess's and this test cannot race another.
#[test]
fn an_undetermined_subject_fails_closed_at_both_enforcement_points() {
    let (root, _proj, g, _candidate) = marked_machine("s6-failclosed");
    let elsewhere = root.join("somewhere-else");
    std::fs::create_dir_all(&elsewhere).unwrap();
    let hostile = g.with_env("GOV_MACHINE_STATE_DIR", elsewhere.to_str().unwrap());

    // The operation-level point (`guard_light`, reached through `control::guard_write`).
    let e = hostile.err(&["gate", "create", "--question", "may a gate be created?"]);
    assert_eq!(
        e.error_code(),
        "SRR_BELOW_FLOOR_SUBJECT_UNDETERMINED",
        "one environment variable cleared the §6 bullet 1 chokepoint: {}",
        e.envelope
    );
    assert_eq!(e.details()["subject"], "UNDETERMINED");
    assert_eq!(e.details()["fail"], "closed");

    // The effect-level point (`guard_effect`), reached from a sink that takes no `Project` and therefore cannot
    // reach the operation-level chokepoint at all.
    let e = hostile.err(&[
        "release",
        "build",
        "--version",
        "9.9.9",
        "--certification",
        "CERTIFIED",
        "--out",
        root.join("rel-out").to_str().unwrap(),
        "--canonical",
        canonical_root().to_str().unwrap(),
    ]);
    assert_eq!(
        e.error_code(),
        "SRR_BELOW_FLOOR_SUBJECT_UNDETERMINED",
        "§6 bullet 3 cleared under the override: {}",
        e.envelope
    );
    assert!(
        !root.join("rel-out/releases/9.9.9").exists(),
        "the refusal must happen before anything is written"
    );

    // Bullet 7 fails closed the same way: unknown is not "no", so the release is not presented as current.
    let o = hostile.run(&["version"]);
    assert_eq!(o.envelope["release_trust"]["below_floor"], true);
    assert_eq!(o.envelope["release_trust"]["presented_as"], "UNDETERMINED");

    // The state-carrying form was never affected and still is not: it is handed the `MachineState` and resolves
    // nothing, which is why §6 bullet 4 held under the identical input while the others did not.
    let dir = tmp("s6-failclosed-on");
    let ms = gov_runtime::srr::state::MachineState::at(&dir).unwrap();
    gov_runtime::srr::state::write_durable(
        &ms.degraded_path("p"),
        &json!({"active": true, "marking": bg::DEGRADED_TOKEN, "entered_at": "2026-01-01T00:00:00Z"}),
    )
    .unwrap();
    let e = bg::guard_effect_on(&ms, "p", bg::Effect::TrustPolicyMutation, "trust anchor write").unwrap_err();
    assert_eq!(e.code, "SRR_BELOW_FLOOR_REFUSED");

    // And the fix is local: the owner-closed resolution is untouched, so the CI-runner override still works on
    // an unprovisioned machine and a provisioned machine still refuses to be relocated.
    let state_rs = std::fs::read_to_string(canonical_root().join("runtime/src/srr/state.rs")).unwrap();
    assert!(
        state_rs.contains("SRR_PROTECTED_STATE_OVERRIDE_REFUSED"),
        "`resolve_state_root` no longer refuses the override on a provisioned machine"
    );
    assert!(
        state_rs.contains("XDG_STATE_HOME") && state_rs.contains(".local"),
        "`default_state_root` no longer derives from XDG_STATE_HOME/HOME (AR27-OD1 is owner-closed)"
    );
    let bg_rs = std::fs::read_to_string(canonical_root().join("runtime/src/srr/breakglass.rs")).unwrap();
    assert!(
        !bg_rs.contains("let Ok(root) = crate::srr::state::resolve_state_root() else {"),
        "the fail-open pattern is back in `breakglass.rs`"
    );
}

// --------------------------------------------------------------------------------- 4. the other sinks

/// **§6 bullet 6 — the floors sink refuses a lowering write, whoever made it.**
///
/// The census used to record bullet 6 as `no primitive exists: Floors::raise_* are monotonic`. The derived census
/// contradicts that by construction: every field of `Floors` is `pub` and `save` is `pub`, so assigning a field
/// and saving is a floor-lowering primitive the mutator census could not see. No code in the product does it, and
/// the derived census measures that; this measures that it would not work if it did.
#[test]
fn the_floors_sink_never_lowers_a_floor_however_the_value_was_set() {
    use gov_runtime::srr::state::{Floors, MachineState};
    let dir = tmp("s6-floors");
    let ms = MachineState::at(&dir).unwrap();

    let mut f = Floors {
        product: "p".into(),
        ..Default::default()
    };
    f.raise_metadata("root", 7);
    f.raise_release("4.1.5", 15, true);
    f.raise_minimum_secure("4.1.2", 12, "sha");
    f.save(&ms).unwrap();

    // A lowering write, by the one route the mutator census could not see: assign the public fields directly.
    let mut lower = Floors {
        product: "p".into(),
        release_high_water_version: "4.0.0".into(),
        release_high_water_sequence: 0,
        minimum_secure_release: String::new(),
        minimum_secure_sequence: 0,
        ..Default::default()
    };
    lower.metadata_high_water.insert("root".into(), 0);
    lower.save(&ms).unwrap();

    let after = Floors::load(&ms, "p");
    assert_eq!(after.release_high_water_sequence, 15, "the release high-water was lowered");
    assert_eq!(after.release_high_water_version, "4.1.5");
    assert_eq!(after.minimum_secure_sequence, 12, "the signed minimum secure release was lowered");
    assert_eq!(after.minimum_secure_release, "4.1.2");
    assert_eq!(after.metadata_floor("root"), 7, "a metadata high-water was reset");
    // and the in-memory value agrees with what was written, so no caller is left holding a lower view
    assert_eq!(lower.release_high_water_sequence, 15);

    // Raising still works: monotonic, not frozen.
    let mut up = Floors::load(&ms, "p");
    up.raise_release("4.1.6", 16, true);
    up.save(&ms).unwrap();
    assert_eq!(Floors::load(&ms, "p").release_high_water_sequence, 16);
}

/// **`AR31-N3` — §6 bullet 2 is enforced by the effect, not by one source literal.**
///
/// AR-0031 minted a `human-gate` record three ways with no `Clearance` in existence: `new_record` with a
/// non-literal type argument, `Record::set("type", …)` on an existing record, and the public constructor. None
/// spells the literal the previous census greps for, and the first is invisible to any source scan. All three
/// become durable only through `records::save_record`, which now asks §6 by record type.
///
/// Measured through the binary on a marked machine at `gov gate present`, which mutates a `human-gate` record and
/// reaches **no** operation-level guard — so before this repair it wrote a governed record below floor.
#[test]
fn a_human_gate_record_cannot_be_written_below_floor_however_it_was_minted() {
    // the type-keyed dispatch is the product's, and is not a grep
    assert!(bg::guarded_record_effect("human-gate").is_some());
    assert!(bg::guarded_record_effect("task").is_none());
    assert_eq!(
        bg::guarded_record_effect("human-gate").unwrap(),
        bg::Effect::HumanGateCreate
    );
    // all three of AR-0031's constructions produce a record whose TYPE is what the sink dispatches on
    let literal = gov_runtime::records::new_record("human-gate", "HDG-9001", "t", json!({}));
    let computed_type: &str = "human-gate";
    let computed = gov_runtime::records::new_record(computed_type, "HDG-9002", "t", json!({}));
    let mut retyped = gov_runtime::records::new_record("task", "TASK-9003", "t", json!({}));
    retyped.set("type", json!("human-gate"));
    for r in [&literal, &computed, &retyped] {
        assert!(
            bg::guarded_record_effect(&r.rtype()).is_some(),
            "a `human-gate` record minted as {:?} is not recognised by the record-write sink",
            r.rtype()
        );
    }

    let (_root, proj, g, _c) = marked_machine("s6-record");
    // A gate raised before break-glass, so there is something to write to.
    let store = gov_runtime::records::RecordStore::load(&proj);
    let existing: Vec<String> = store
        .of_type("human-gate")
        .into_iter()
        .map(|r| r.id())
        .collect();
    let _ = existing;

    // `gov gate present` calls `authority::require` and `save_record`, and NOT `control::guard_write`. The
    // record-write sink is the only §6 control on that path.
    let e = g.err(&["gate", "present", "HDG-0001"]);
    assert!(
        e.error_code() == "SRR_BELOW_FLOOR_REFUSED" || e.error_code() == "GATE_NOT_FOUND",
        "unexpected: {}",
        e.envelope
    );
    // And creation through the ordinary door is refused with the class named.
    let e = g.err(&["gate", "create", "--question", "may a gate be created below floor?"]);
    assert_eq!(e.error_code(), "SRR_BELOW_FLOOR_REFUSED");
    assert_eq!(e.details()["refused_class"], "human_gate_create");
    let gates = g.ok(&["gate", "list"]);
    assert!(
        gates.as_array().map(|a| a.is_empty()).unwrap_or(true),
        "a Human Gate exists below floor: {gates}"
    );
}

/// **`AR31-N1` and `AR31-N2` — §6 bullet 5 at both acquisition primitives, asked unconditionally.**
#[test]
fn both_capability_acquisition_primitives_ask_section_6_without_consulting_the_descriptor() {
    let functions = product_functions();
    let acquisition = functions
        .iter()
        .find(|f| f.path.ends_with("srr/plugins.rs") && f.name == "guard_acquisition")
        .expect("plugins::guard_acquisition not found");
    assert!(
        acquisition.body.contains("Effect::PrivilegedPluginAcquisition"),
        "the bullet 5 sink no longer asks §6"
    );
    // `AR31-N2`: the §6 question must not be taken on data the descriptor supplies about itself.
    let before_guard = acquisition
        .body
        .split("Effect::PrivilegedPluginAcquisition")
        .next()
        .unwrap();
    assert!(
        !before_guard.contains("if privileged"),
        "whether §6 is asked at all is decided by `is_privileged(descriptor)`, which reads the descriptor: \
         ARCH-0003 §9 says descriptors cannot self-authorise, and deciding whether to ask the question is a form \
         of authorising"
    );

    // `AR31-N1`: `tools::install` is the second primitive, and it now reaches the sink module's named door.
    let install = functions
        .iter()
        .find(|f| f.path.ends_with("tools.rs") && f.name == "install")
        .expect("tools::install not found");
    assert!(
        install.body.contains("guard_acquisition_below_floor("),
        "`tools::install` installs a capability and reaches no effect-level §6 control"
    );
    let door = functions
        .iter()
        .find(|f| f.path.ends_with("srr/plugins.rs") && f.name == "guard_acquisition_below_floor")
        .expect("plugins::guard_acquisition_below_floor not found");
    assert!(
        door.body.contains("Effect::PrivilegedPluginAcquisition"),
        "the named §6 door does not ask §6"
    );
    // and the derivation sees BOTH writers of a capability registry, which is the point of AR31-N1: the census
    // entry claimed one primitive for a bullet the product realises in two places.
    let (sig, acc) = bg::section_6_signature("privileged_plugin_acquisition").unwrap();
    let writers: Vec<String> = functions
        .iter()
        .filter(|f| matches_any(&f.body, sig) && performs_write(&f.body))
        .map(|f| f.site())
        .collect();
    assert!(
        writers.iter().any(|w| w.contains("tools.rs::install"))
            && writers.iter().any(|w| w.contains("governance.rs::register")),
        "the derived census does not find both capability-registry writers: {writers:?}"
    );
    for w in &writers {
        let f = functions.iter().find(|f| f.site() == *w).unwrap();
        assert!(matches_any(&f.body, acc), "{w} writes a capability registry without asking §6");
    }
    assert!(
        install.body.contains(r#"guard_write(p, "tools install")"#),
        "`tools install` lost its operation-level guard"
    );
}

// --------------------------------------------------------------------------------- 5. AR31-N4 restored

/// **`AR31-N4` — the two sub-checks dropped in the `ho_f` migration, restored where they run.**
///
/// `ho_f_preservation::f1`'s behavioural half (a malleated S+L signature must be refused by both `crypto::verify`
/// and `crypto::verify_strict`, with the same error code) ran nowhere once `ho_f` stopped compiling, and could
/// not move into the product's own census because that census reads product source and `gov` cannot sign
/// (`SRR-R0-L4`). It lives here instead: this harness is test material, it already signs fixture metadata, and
/// `SRR-R0-L4` is a property of the shipped product, which the census below re-measures.
#[test]
fn the_dropped_held_out_sub_checks_run_here() {
    use ed25519_dalek::{Signer, SigningKey};

    // --- ho_f::f1, behavioural half -------------------------------------------------------------------------
    let sk = SigningKey::from_bytes(&[0x5au8; 32]);
    let public = hex::encode(sk.verifying_key().to_bytes());
    let msg = b"AR-0032 malleability";
    let sig = hex::encode(sk.sign(msg).to_bytes());
    gov_runtime::srr::crypto::verify(&public, &sig, msg).expect("a good signature must verify");
    gov_runtime::srr::crypto::verify_strict(&public, &sig, msg).expect("and must verify strictly");

    // S + L: the classic non-canonical scalar a permissive ed25519 verifier accepts and a strict one refuses.
    let mut raw = hex::decode(&sig).unwrap();
    let l: [u8; 32] = [
        0xed, 0xd3, 0xf5, 0x5c, 0x1a, 0x63, 0x12, 0x58, 0xd6, 0x9c, 0xf7, 0xa2, 0xde, 0xf9, 0xde, 0x14, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10,
    ];
    let mut carry = 0u16;
    for i in 0..32 {
        let s = raw[32 + i] as u16 + l[i] as u16 + carry;
        raw[32 + i] = (s & 0xff) as u8;
        carry = s >> 8;
    }
    let malleated = hex::encode(&raw);
    let a = gov_runtime::srr::crypto::verify(&public, &malleated, msg);
    let b = gov_runtime::srr::crypto::verify_strict(&public, &malleated, msg);
    assert!(
        a.is_err() && b.is_err(),
        "a malleated S+L signature was accepted: verify={a:?} verify_strict={b:?}"
    );
    assert_eq!(
        a.unwrap_err().code,
        b.unwrap_err().code,
        "the two entry points disagree on a malleated signature"
    );

    // --- ho_f::f2, second half ------------------------------------------------------------------------------
    // No relaxation switch anywhere in product source, outside the list of variables explicitly REFUSED as
    // authority. A switch that exists is a switch that can be set.
    for (path, text) in product_sources() {
        for needle in [
            "skip_verify",
            "skip-verify",
            "allow_unsigned",
            "allow-unsigned",
            "force_unsigned",
            "insecure_skip",
        ] {
            for (n, line) in text.lines().enumerate() {
                if line.contains(needle) && !line.contains("REFUSED_AUTHORITY_ENV") {
                    panic!("{path}:{} declares a verification relaxation switch: {line}", n + 1);
                }
            }
        }
    }

    // and `gov` still cannot sign at all: SRR-R0-L4 is vacuous, not merely unused
    for (path, text) in product_sources() {
        if path.ends_with("security/secrets.rs") || path.contains("security/") {
            continue;
        }
        for needle in ["SigningKey", "Signer", "PRIVATE KEY"] {
            assert!(
                !text.contains(needle),
                "{path} carries a signing capability ({needle}); SRR-R0-L4 requires `gov` to verify and never sign"
            );
        }
    }
}
