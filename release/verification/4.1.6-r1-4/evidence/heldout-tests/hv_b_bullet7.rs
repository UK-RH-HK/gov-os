//! **AR-0033 held-out verification — `AR31-B1`, §6 bullet 7, in both directions.**
//!
//! A below-floor machine must not read as current. An unmarked machine must not be spuriously marked. And the
//! universality claim — "`run(&cli)` is called once and its value reaches stdout through one envelope" — is a
//! claim about the CLI boundary, so it is tested at the boundary with the real binary.
//!
//! Run single-threaded: these tests set process-wide environment for the in-process half.
mod common;
use common::*;
use gov_runtime::srr::present;
use serde_json::Value;

fn with_state<T>(m: &Machine, f: impl FnOnce() -> T) -> T {
    let old_home = std::env::var_os("HOME");
    let old_xdg = std::env::var_os("XDG_STATE_HOME");
    let old_dir = std::env::var_os("GOV_MACHINE_STATE_DIR");
    std::env::set_var("HOME", &m.home);
    std::env::set_var("XDG_STATE_HOME", &m.home);
    std::env::remove_var("GOV_MACHINE_STATE_DIR");
    let r = f();
    match old_home { Some(v) => std::env::set_var("HOME", v), None => std::env::remove_var("HOME") }
    match old_xdg { Some(v) => std::env::set_var("XDG_STATE_HOME", v), None => std::env::remove_var("XDG_STATE_HOME") }
    if let Some(v) = old_dir { std::env::set_var("GOV_MACHINE_STATE_DIR", v) }
    r
}

/// **b1 — below floor, the sink refuses and the refusal IS the presentation.**
#[test]
fn b1_a_below_floor_machine_does_not_read_as_current() {
    let m = machine("b1-marked");
    m.mark();
    let v = with_state(&m, || present::presentation("held-out"));
    println!("{}", serde_json::to_string_pretty(&v).unwrap());
    assert_eq!(v["below_floor"], true, "a marked machine presents itself as current");
    assert_eq!(v["presented_as"], present::PRESENTED_BELOW_FLOOR);
    assert_eq!(v["marking"], gov_runtime::srr::breakglass::DEGRADED_TOKEN);
    assert_eq!(v["section_6_bullet"], 7);
    assert_eq!(v["refused_class"], "present_below_floor_release_as_current");
    assert!(
        v["exit_condition"].as_str().unwrap_or("").contains("authenticated release"),
        "the marking must tell the operator the way out"
    );
    assert_eq!(v["entered_at"], "2026-09-18T00:00:00Z", "the refusal loses the entry time");
    assert!(!with_state(&m, || present::may_present_as_current("held-out")));

    // and the demotion is done by the sink, not by the caller
    let mut report = serde_json::json!({"current": "4.1.1", "up_to_date": true, "recommendation": "nothing to do"});
    with_state(&m, || present::attach("held-out", &mut report));
    assert_eq!(report["up_to_date"], false, "an affirmative currency claim survived below floor");
    assert!(
        report["recommendation"].as_str().unwrap().contains("§6 bullet 7"),
        "'nothing to do' survived below floor: {}", report["recommendation"]
    );
    assert_eq!(report[present::PRESENTATION_KEY]["below_floor"], true);
}

/// **b2 — the other direction: an unmarked machine is not spuriously marked, and the marking LIFTS.**
#[test]
fn b2_an_unmarked_machine_is_not_marked_and_a_cleared_marking_lifts() {
    let m = machine("b2-clean");
    let v = with_state(&m, || present::presentation("held-out"));
    assert_eq!(v["below_floor"], false, "an unmarked machine claims a break-glass marking");
    assert_eq!(v["presented_as"], present::PRESENTED_CURRENT);
    assert!(v["marking"].is_null(), "an unmarked machine carries a marking token");
    assert!(with_state(&m, || present::may_present_as_current("held-out")));

    // a report with an affirmative claim is left alone
    let mut report = serde_json::json!({"up_to_date": true, "recommendation": "nothing to do"});
    with_state(&m, || present::attach("held-out", &mut report));
    assert_eq!(report["up_to_date"], true, "an unmarked machine had a true currency claim demoted");
    assert_eq!(report["recommendation"], "nothing to do");

    // mark, then clear the way `try_exit` does, and check the marking really lifts rather than sticking
    m.mark();
    assert_eq!(with_state(&m, || present::presentation("x"))["below_floor"], true);
    let ms = m.ms();
    let mut rec = gov_runtime::srr::breakglass::Degraded::load(&ms, PRODUCT).unwrap().record;
    rec["active"] = serde_json::json!(false);
    gov_runtime::srr::state::write_durable(&ms.degraded_path(PRODUCT), &rec).unwrap();
    let after = with_state(&m, || present::presentation("x"));
    assert_eq!(after["below_floor"], false, "a cleared marking does not lift: recovery would be unexitable");
    assert_eq!(after["presented_as"], present::PRESENTED_CURRENT);
    assert!(after["marking"].is_null());
}

/// **b3 — a machine with no HOME and no XDG_STATE_HOME is not spuriously marked.**
///
/// `presentation()` is now on every command's path, so a benign failure to resolve the state root would mark
/// every healthy machine. `default_state_root` must fall back rather than error.
#[test]
fn b3_a_machine_with_no_home_is_not_spuriously_marked() {
    let probe = scratch("b3-tmp");
    let old_home = std::env::var_os("HOME");
    let old_xdg = std::env::var_os("XDG_STATE_HOME");
    let old_tmp = std::env::var_os("TMPDIR");
    std::env::remove_var("HOME");
    std::env::remove_var("XDG_STATE_HOME");
    std::env::remove_var("GOV_MACHINE_STATE_DIR");
    std::env::set_var("TMPDIR", &probe);
    let v = present::presentation("no-home");
    match old_home { Some(x) => std::env::set_var("HOME", x), None => {} }
    match old_xdg { Some(x) => std::env::set_var("XDG_STATE_HOME", x), None => {} }
    match old_tmp { Some(x) => std::env::set_var("TMPDIR", x), None => std::env::remove_var("TMPDIR") }
    println!("no HOME / no XDG_STATE_HOME: {v}");
    assert_eq!(
        v["below_floor"], false,
        "a machine that merely has no HOME is presented as below floor, which would mark every healthy machine"
    );
}

/// **b4 — the CLI boundary claim, tested at the boundary.**
///
/// The claim is that every command result carries the marking because `run()` is called once and its value
/// reaches stdout through one envelope. Commands with no relationship to release identity are the real test.
#[test]
fn b4_every_command_result_carries_the_marking_through_the_envelope() {
    let m = machine("b4-cli");
    let proj = m.home.join("proj");
    std::fs::create_dir_all(&proj).unwrap();
    m.mark();

    for args in [
        vec!["--json", "version"],
        vec!["--json", "doctor"],
        vec!["--json", "gate", "list"],
        vec!["--json", "policy", "overrides"],
        vec!["--json", "claims", "list"],
        vec!["--json", "plugins", "list"],
    ] {
        let r = gov(&m, &proj, &[], &args);
        let v = r.json();
        assert!(
            !v.is_null(),
            "`gov {}` did not emit a JSON envelope at all: stdout={:?} stderr={:?}",
            args.join(" "), r.stdout, r.stderr
        );
        let rt = &v["release_trust"];
        assert!(
            !rt.is_null(),
            "`gov {}` lost the §6 bullet 7 marking: {v}", args.join(" ")
        );
        assert_eq!(rt["below_floor"], true, "`gov {}`: {v}", args.join(" "));
        assert_eq!(rt["marking"], gov_runtime::srr::breakglass::DEGRADED_TOKEN);
        assert_eq!(rt["presented_as"], "BELOW_FLOOR_RECOVERY_ONLY");
    }

    // the same commands on an unmarked machine must not claim a marking
    let clean = machine("b4-clean");
    let cproj = clean.home.join("proj");
    std::fs::create_dir_all(&cproj).unwrap();
    for args in [vec!["--json", "version"], vec!["--json", "gate", "list"]] {
        let v = gov(&clean, &cproj, &[], &args).json();
        assert_eq!(v["release_trust"]["below_floor"], false, "spurious marking: {v}");
        assert_eq!(v["release_trust"]["presented_as"], "CURRENT");
        assert!(v["release_trust"]["marking"].is_null());
    }
}

/// **b5 — find a reporting path that does NOT go through the CLI envelope.**
///
/// `DERIVATION.md` §4 limit 10 says two non-result print sites exist in `cli/src/main.rs` and that "the
/// derivation finds them; they are accounted for here rather than silently excluded". I test both halves: that a
/// stdout path bypassing the envelope exists, and whether the derivation actually finds it.
#[test]
fn b5_a_stdout_path_bypasses_the_command_result_envelope() {
    let m = machine("b5-bypass");
    let proj = m.home.join("proj");
    std::fs::create_dir_all(&proj).unwrap();
    m.mark();

    // `gov capabilities serve-embed` prints its response and calls `std::process::exit(0)` from inside `run()`,
    // so control never reaches the `match result` that attaches the presentation.
    let mut c = std::process::Command::new(gov_bin());
    c.current_dir(&proj)
        .args(["--json", "capabilities", "serve-embed", "--id", "probe"])
        .stdin(std::process::Stdio::piped())
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::piped());
    for k in STRIPPED {
        c.env_remove(k);
    }
    c.env("HOME", &m.home).env("XDG_STATE_HOME", &m.home);
    let mut child = c.spawn().expect("spawn serve-embed");
    {
        use std::io::Write;
        let stdin = child.stdin.as_mut().unwrap();
        stdin
            .write_all(br#"{"protocol":"gov-capability/1","inputs":{"texts":["hello"],"dimensions":8}}"#)
            .unwrap();
    }
    let out = child.wait_with_output().unwrap();
    let text = String::from_utf8_lossy(&out.stdout).to_string();
    println!("serve-embed stdout on a MARKED machine: {text}");
    let v: Value = serde_json::from_str(text.trim()).expect("serve-embed emitted no JSON");
    assert_eq!(v["ok"], true, "the probe did not exercise the success path: {v}");
    assert!(
        v["release_trust"].is_null(),
        "if this now carries the marking the finding is closed; re-derive it"
    );
    println!(
        "FOUND: `gov capabilities serve-embed` writes to stdout and calls std::process::exit(0) from inside \
         run(), so the command-result envelope is never reached. The claim that run()'s value reaches stdout \
         ONLY through one envelope is false as written."
    );

    // Does the derivation find it? Limit 10 says it does.
    let funcs = product_functions(true);
    let (sig, acc) = gov_runtime::srr::breakglass::section_6_signature(
        "present_below_floor_release_as_current",
    )
    .unwrap();
    let derived: Vec<String> = funcs
        .iter()
        .filter(|f| any(&f.body, sig) && is_write(&f.body))
        .map(|f| f.site())
        .collect();
    println!("bullet 7 derived writers: {derived:?}");
    let run_fn = funcs
        .iter()
        .find(|f| f.file.ends_with("cli/src/main.rs") && f.name == "run")
        .expect("cli::run not found");
    assert!(
        run_fn.body.contains("std::process::exit(0)") && run_fn.body.contains("println!"),
        "the bypass is no longer inside `run`; re-derive this scenario"
    );
    let run_is_derived = any(&run_fn.body, sig);
    println!(
        "does the bullet-7 signature derive `cli/src/main.rs::run`, which holds both non-envelope print sites? \
         {run_is_derived}"
    );
    assert!(
        !run_is_derived,
        "if the signature now derives `run` then limit 10's claim is true and this finding is closed"
    );
    assert!(
        !any(&run_fn.body, acc),
        "`run` carries no bullet-7 acceptance marker either, so it is neither derived nor enforced"
    );
    println!(
        "MEASURED: `cli/src/main.rs::run` holds both non-envelope stdout writes and is NOT in the bullet-7 \
         derived set. DERIVATION.md §4 limit 10's statement that 'the derivation finds them' is inaccurate: \
         they are accounted for in prose only."
    );
}

/// **b6 — the human-readable (non-JSON) surface carries the marking too.**
#[test]
fn b6_the_non_json_surface_carries_the_marking() {
    let m = machine("b6-human");
    let proj = m.home.join("proj");
    std::fs::create_dir_all(&proj).unwrap();
    m.mark();
    let r = gov(&m, &proj, &[], &["version"]);
    let joined = format!("{}{}", r.stdout, r.stderr);
    println!("stdout:\n{}\nstderr:\n{}", r.stdout, r.stderr);
    assert!(
        joined.contains(gov_runtime::srr::breakglass::DEGRADED_TOKEN),
        "the human-readable surface of a marked machine carries no marking: {joined}"
    );
    let clean = machine("b6-clean");
    let cproj = clean.home.join("proj");
    std::fs::create_dir_all(&cproj).unwrap();
    let r2 = gov(&clean, &cproj, &[], &["version"]);
    assert!(
        !format!("{}{}", r2.stdout, r2.stderr).contains(gov_runtime::srr::breakglass::DEGRADED_TOKEN),
        "an unmarked machine prints the marking banner"
    );
}

/// **b7 — an in-process consumer of `gov_runtime` (limit 9 / defeat 2).**
///
/// Bullet 7's universality is a property of the CLI boundary. An embedder calling a reporting function directly
/// gets the marking only from surfaces that carry it in their own payload. Measure which do.
#[test]
fn b7_in_process_reporting_surfaces_are_covered_only_where_they_carry_it_themselves() {
    let funcs = product_functions(true);
    let carries = |site: &str| {
        funcs
            .iter()
            .find(|f| f.site() == site)
            .map(|f| {
                f.body.contains("present::presentation(")
                    || f.body.contains("present::attach(")
                    || f.body.contains("Degraded::load")
                    || f.body.contains("is_degraded")
            })
            .unwrap_or(false)
    };
    for site in [
        "runtime/src/doctor.rs::run",
        "runtime/src/update.rs::check",
        "runtime/src/context/mod.rs::compile",
    ] {
        assert!(carries(site), "{site} does not carry the marking in its own payload");
    }
    // The raw accessor that every reporting surface reads the version from carries nothing, and cannot: it is a
    // lock accessor. This is the shape a fifth in-process reporting surface would take.
    let fv = funcs.iter().find(|f| f.name == "framework_version").map(|f| f.site());
    println!("the raw installed-release accessor: {fv:?} (carries no marking, by design)");
    println!(
        "CONFIRMED (disclosed limit 9): bullet 7 is universal at the `gov` boundary and enumerated in-process. \
         An in-process reporting function written tomorrow gets the marking only if its author adds it."
    );
}
