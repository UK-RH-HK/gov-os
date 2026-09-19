//! P2-AR-0017 supplementary R1 check — NOT a held-out suite and NOT an edit of one.
//!
//! AR-0033's `hv_a_derivation::a1` pins the candidate-4 scale (84 product files / 740 functions) before it derives
//! the §6 census, so any product change that adds a function fails it at the pin and the census itself never runs.
//! This harness links AR-0033's own census machinery (`common.rs`, copied byte-identically as `tests/common/mod.rs`)
//! and runs a1's census loop — the same signatures, write primitives, acceptance markers and exemptions from the
//! product's `breakglass` tables — without the scale pin, reporting the scale it finds.
mod common;
use common::*;
use gov_runtime::srr::breakglass as bg;

#[test]
fn a1_census_without_the_scale_pin() {
    let files = product_files();
    let funcs = product_functions(true);
    println!(
        "independent walk: {} files, {} functions (candidate-4 pin: 84 / 740)",
        files.len(),
        funcs.len()
    );
    let mut report = vec![];
    let mut total_violations = vec![];
    for (activity, sig, acc) in bg::SECTION_6_SIGNATURES {
        if *activity == "normal_privileged_operation" {
            continue;
        }
        let derived: Vec<&Fun> = funcs.iter().filter(|f| any(&f.body, sig)).collect();
        let writers: Vec<&&Fun> = derived.iter().filter(|f| is_write(&f.body)).collect();
        let (mut viol, mut exempt) = (vec![], vec![]);
        for f in &writers {
            if any(&f.body, acc) {
                continue;
            }
            let s = f.site();
            if bg::derivation_exemption(activity, &s).is_some() {
                exempt.push(s);
            } else {
                viol.push(s);
            }
        }
        report.push(format!(
            "{activity}: derived {} / writers {} / exempt {} / violations {}",
            derived.len(),
            writers.len(),
            exempt.len(),
            viol.len()
        ));
        total_violations.extend(viol);
    }
    println!("independent §6 census (AR-0033 machinery, unpinned):\n  {}", report.join("\n  "));
    assert!(
        total_violations.is_empty(),
        "independently derived §6 violations: {total_violations:?}"
    );
}
