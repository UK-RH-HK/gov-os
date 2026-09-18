# AR-0032 — reproducing this repair

| Item | Value |
|---|---|
| Branch | `phase1/srr1-r1-repair-3` |
| Base commit | `30aa98a10fd7f5ed85439b0d676761080519ceed` |
| Toolchain | `cargo 1.98.1 (797e8a9bc 2026-08-05)` |

```bash
export PATH="$HOME/.cargo/bin:$PATH"
export CARGO_TARGET_DIR=<scratch>/cargo-target
STRIP='env -u GOV_BREAK_GLASS -u GOV_BREAKGLASS -u GOV_TRUST_OVERRIDE -u GOV_SKIP_VERIFY
       -u GOV_ALLOW_UNSIGNED -u GOV_RELEASE_AUTHORITY -u GOV_HUMAN_GATE_APPROVED
       -u GOV_FLOOR_OVERRIDE -u GOV_MINIMUM_SECURE_RELEASE -u GOV_MACHINE_STATE_DIR'
```

## 1. Regression

```bash
$STRIP cargo test --lib                 # 42 passed; 0 failed   (36 pre-existing + 6 new)
$STRIP cargo test --test certification  # 79 passed; 0 failed   (70 pre-existing + 9 new)
$STRIP cargo clippy --all-targets       # clean
git diff --numstat 30aa98a              # tests/certification/srr.rs is NOT in the diff
```

Captured in `REGRESSION-LIB.txt`, `REGRESSION-CERTIFICATION.txt`, `CLIPPY.txt`.

## 2. The structural work specifically

```bash
$STRIP cargo test --test certification section6:: -- --nocapture   # 9 tests; prints the derived census
$STRIP cargo test --lib srr::breakglass -- --nocapture
$STRIP cargo test --lib srr::present -- --nocapture
```

Captured in `DERIVED-CENSUS.txt`. The printed census at this commit:

```
human_gate_create: derived 35 / writers 32 / exempt 1 / violations 0
human_gate_approve: derived 1 / writers 1 / exempt 0 / violations 0
release_certification: derived 2 / writers 1 / exempt 0 / violations 0
trust_policy_mutation: derived 7 / writers 1 / exempt 0 / violations 0
privileged_plugin_acquisition: derived 9 / writers 2 / exempt 0 / violations 0
floor_lower_or_reset: derived 3 / writers 1 / exempt 0 / violations 0
present_below_floor_release_as_current: derived 1 / writers 1 / exempt 0 / violations 0
bullet 1 guard_write call sites: 27
§6 bullet 7 enforcement sites: ["cli/src/main.rs::main", "runtime/src/context/mod.rs::compile",
                               "runtime/src/doctor.rs::run", "runtime/src/srr/present.rs::presentation",
                               "runtime/src/update.rs::check"]
```

### Break the derivation on purpose, to see it fire

Any of these must fail `section_6_coverage_is_derived_from_the_product`:

```bash
# 1. a second, unguarded implementation of a §6 primitive
cat >> runtime/src/srr/state.rs <<'X'
pub fn reset_floors(ms: &MachineState, product: &str) -> Result<()> {
    write_durable(&ms.floors_path(product), &json!({"release_high_water": {"sequence": 0}}))
}
X
# 2. remove a positive control from tests/certification/section6.rs::POSITIVE_CONTROLS
# 3. put `("floor_lower_or_reset", "no primitive: ...")` back into SECTION_6_SINKS
#    -> a_no_primitive_claim_is_refutable_by_this_suite fails, and says what to assert instead
# 4. add an entry to SECTION_6_DERIVATION_EXEMPTIONS for a function the derivation does not find
```

## 3. Re-run AR-0027's held-out suite, unmodified

```bash
ln -sfn srr1-r1-repair-3 <scratch>/wt/srr1-r1-verify
mkdir -p <scratch>/heldout-ar0027/tests/common
cp release/verification/4.1.6-r1/evidence/heldout-tests/Cargo.toml.txt  <scratch>/heldout-ar0027/Cargo.toml
cp release/verification/4.1.6-r1/evidence/heldout-tests/forge.rs        <scratch>/heldout-ar0027/tests/common/forge.rs
cp release/verification/4.1.6-r1/evidence/heldout-tests/heldout_srr*.rs <scratch>/heldout-ar0027/tests/
printf '#![allow(dead_code, unused_imports)]\npub mod forge;\n' > <scratch>/heldout-ar0027/tests/common/mod.rs
cd <scratch>/heldout-ar0027
for t in heldout_srr heldout_srr2 heldout_srr3 heldout_srr4; do
  $STRIP cargo test --test $t -- --test-threads=1 --nocapture
done
```

Expected: **26 passed, 3 failed** — `heldout_srr2::b1`, `::b2`, `heldout_srr3::d3`. Identical to repair 2.
Captured in `AR-0027-HELD-OUT-RERUN.txt`.

## 4. Re-run AR-0029's held-out suite, unmodified

```bash
ln -sfn srr1-r1-repair-3 <scratch>/wt/srr1-r1-verify-2
mkdir -p <scratch>/heldout-ar0029/tests/common
cp release/verification/4.1.6-r1-2/evidence/heldout-tests/Cargo.toml.txt <scratch>/heldout-ar0029/Cargo.toml
cp release/verification/4.1.6-r1-2/evidence/heldout-tests/mint.rs        <scratch>/heldout-ar0029/tests/common/mint.rs
cp release/verification/4.1.6-r1-2/evidence/heldout-tests/ho_*.rs        <scratch>/heldout-ar0029/tests/
printf '#![allow(dead_code, unused_imports)]\npub mod mint;\n' > <scratch>/heldout-ar0029/tests/common/mod.rs
cd <scratch>/heldout-ar0029
for t in ho_a_allowlist ho_b_coverage ho_c_deadlock ho_d_expiry ho_e_rootexpiry ho_f_preservation; do
  $STRIP cargo test --test $t -- --test-threads=1 --nocapture
done
```

Expected: **6 / (4 pass, 2 fail) / 5 / 5 / 6 / does-not-compile**. Identical to repair 2.
Captured in `AR-0029-HELD-OUT-RERUN.txt`.

## 5. Re-run AR-0031's held-out suite, unmodified

```bash
ln -sfn srr1-r1-repair-3 <scratch>/wt/srr1-r1-verify-3
mkdir -p <scratch>/heldout-ar0031/tests/common
cp release/verification/4.1.6-r1-3/evidence/heldout-tests/Cargo.toml.txt <scratch>/heldout-ar0031/Cargo.toml
cp release/verification/4.1.6-r1-3/evidence/heldout-tests/bench.rs       <scratch>/heldout-ar0031/tests/common/bench.rs
cp release/verification/4.1.6-r1-3/evidence/heldout-tests/hx_*.rs        <scratch>/heldout-ar0031/tests/
printf '#![allow(dead_code, unused_imports)]\npub mod bench;\n' > <scratch>/heldout-ar0031/tests/common/mod.rs
cd <scratch>/heldout-ar0031
for t in hx_a_census hx_b_failopen hx_c_prior_evidence hx_d_acquisition_and_preservation; do
  $STRIP cargo test --test $t -- --test-threads=1 --nocapture
done
```

Expected: **27 passed, 7 failed** (baseline on candidate 3 was 26 / 8). Every flip is explained in
`HELD-OUT-FLIPS.md`. Captured in `AR-0031-HELD-OUT-RERUN.txt`.

`--test-threads=1` is required: `hx_*` mutates process environment variables.

## 6. Reproduce the §6 enforcement census by hand

```bash
# the sink table, the signature table, the write primitives, the exemptions
grep -n "SECTION_6_SINKS\|SECTION_6_SIGNATURES\|SECTION_6_WRITE_PRIMITIVES\|SECTION_6_DERIVATION_EXEMPTIONS\|GUARDED_RECORD_TYPES" \
     runtime/src/srr/breakglass.rs

# bullet 7: the primitive that did not exist, and its call sites
grep -rn "Effect::PresentBelowFloorReleaseAsCurrent\|present::attach\|present::presentation" --include=*.rs runtime/src cli/src
grep -n  "fn run(&cli)\|let result = run" cli/src/main.rs    # run() is called exactly once

# AR31-B2: fail closed, and the owner-closed resolution untouched
grep -n  "undetermined_subject" runtime/src/srr/breakglass.rs
grep -rn "let Ok(root) = crate::srr::state::resolve_state_root() else {" --include=*.rs runtime/src cli/src   # none
git diff 30aa98a -- runtime/src/srr/state.rs | grep -E "resolve_state_root|default_state_root"                # none

# AR31-N3: the record-write sink
grep -n  "guarded_record_effect" runtime/src/records.rs runtime/src/srr/breakglass.rs runtime/src/cit/mod.rs

# AR31-N1 / N2: two acquisition primitives, asked unconditionally
grep -n  "guard_acquisition_below_floor\|Effect::PrivilegedPluginAcquisition" runtime/src/srr/plugins.rs runtime/src/tools.rs

# bullet 6: the floors sink
sed -n '/pub fn save(&mut self, ms: &MachineState)/,/^    }/p' runtime/src/srr/state.rs
```

## 7. Preservation

```bash
cat evidence/PRESERVATION.txt
```

It compares the extracted bodies of `resolve_state_root`, `default_state_root` and `exit_satisfied` against the base
commit (all three **byte-identical**), counts the `admit` / `install_kernel` / `by_admit` / `Clearance` /
`AuthenticatedRelease` censuses, confirms the four-entry allow-list, confirms the Contract v3 digest
`4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3` on both copies, and confirms that
`release/verification/**`, `release/releases/**`, `release/root-of-trust/*-review*/**`, `GATES/`, `ESCALATION/` and
`HANDOFFS/` have **zero** modified or untracked entries.
