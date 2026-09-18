# AR-0030 — reproducing this repair

| Item | Value |
|---|---|
| Branch | `phase1/srr1-r1-repair-2` |
| Base commit | `f5717a9d92419f7588889e0ce5aa96bf641e3fb2` |
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
$STRIP cargo test --lib                 # 36 passed; 0 failed   (31 pre-existing + 5 new)
$STRIP cargo test --test certification  # 70 passed; 0 failed   (65 pre-existing + 5 new)
cargo clippy --all-targets              # clean
git diff --numstat f5717a9              # tests/certification/srr.rs is 866 / 0 — purely additive
```

Captured in `REGRESSION-LIB.txt` and `REGRESSION-CERTIFICATION.txt`.

## 2. The §6 coverage tests specifically

```bash
$STRIP cargo test --test certification section_6 -- --nocapture
$STRIP cargo test --test certification an_allow_listed -- --nocapture
$STRIP cargo test --test certification an_unreadable_marking -- --nocapture
$STRIP cargo test --test certification preservation_census -- --nocapture
$STRIP cargo test --lib srr::breakglass -- --nocapture
```

## 3. Re-run AR-0027's held-out suite, unmodified

```bash
ln -sfn srr1-r1-repair-2 <scratch>/wt/srr1-r1-verify
mkdir -p <scratch>/heldout-ar0027/tests/common
cp release/verification/4.1.6-r1/evidence/heldout-tests/Cargo.toml.txt <scratch>/heldout-ar0027/Cargo.toml
cp release/verification/4.1.6-r1/evidence/heldout-tests/forge.rs       <scratch>/heldout-ar0027/tests/common/forge.rs
cp release/verification/4.1.6-r1/evidence/heldout-tests/heldout_srr*.rs <scratch>/heldout-ar0027/tests/
cd <scratch>/heldout-ar0027
for t in heldout_srr heldout_srr2 heldout_srr3 heldout_srr4; do
  $STRIP cargo test --test $t -- --test-threads=1 --nocapture
done
```

Expected: **26 passed, 3 failed** — `heldout_srr2::b1`, `::b2` and `heldout_srr3::d3`, the same three `OBSERVED:`
assertions repair 1 flipped. Captured in `AR-0027-HELD-OUT-RERUN.txt`.

## 4. Re-run AR-0029's held-out suite, unmodified

```bash
ln -sfn srr1-r1-repair-2 <scratch>/wt/srr1-r1-verify-2
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

Expected: **6 / (4 pass, 2 fail) / 5 / 5 / 6 / does-not-compile**.

* `ho_b::b1`, `ho_b::b2`, `ho_c::c3`, `ho_c::c4` — AR-0029's four `OBSERVED:` failures, now **passing**.
* `ho_b::b3`, `ho_b::b6` — structural census tripwires that assert the *absence* of a guard. Both now fail with
  `re-derive this census` / `a guard now sits between the allow-list entry and the gate creation`. Both statements
  are true and are the repair.
* `ho_f_preservation` — **does not compile**: `cannot construct AuthenticatedRelease with struct literal syntax
  due to private fields`. Its `f4` is exactly the literal `AR29-N1` asked to be made impossible. The other six
  checks in that binary are reproduced as
  `tests/certification/srr.rs::the_no_bypass_and_no_signing_preservation_census_still_holds`.

Captured in `AR-0029-HELD-OUT-RERUN.txt`.

## 5. Reproduce the §6 enforcement census by hand

```bash
# the sink table, and the enforcement call inside each sink
grep -n "SECTION_6_SINKS" -A 30 runtime/src/srr/breakglass.rs
grep -n "guard_effect"          runtime/src/srr/state.rs runtime/src/orchestration/gates.rs \
                                runtime/src/release.rs runtime/src/srr/plugins.rs runtime/src/update.rs
grep -n "breakglass::guard("    runtime/src/srr/provision.rs

# the sealed witness: no construction outside breakglass, no public field
grep -rn "Clearance {"          runtime/src cli/src
grep -n  "pub struct Clearance" -A 5 runtime/src/srr/breakglass.rs

# the sealed AuthenticatedRelease (AR29-N1)
grep -rn "Admitted::by_admit()" runtime/src cli/src          # exactly 1
grep -rn "AuthenticatedRelease {" runtime/src cli/src        # 1 literal, 1 struct decl, 1 impl

# no second implementation of a §6 primitive
grep -rn 'new_record("human-gate"' runtime/src cli/src       # exactly 1, in gates.rs
grep -rn "root_metadata_path()"    runtime/src cli/src       # exactly 2 files: state.rs writes, verifier.rs reads
grep -n  "pub fn raise_\|pub fn "  runtime/src/srr/state.rs  # Floors has only monotonic raises

# one marking path, one reader (AR29-N3, AR29-C1)
grep -n "degraded_path_at"  runtime/src/srr/state.rs runtime/src/srr/breakglass.rs
grep -n "read_marking"      runtime/src/srr/breakglass.rs
```

## 6. Preservation census

```bash
grep -rn "srr::admit("    --include=*.rs runtime/src cli/src   # exactly 5
grep -rn "install_kernel" --include=*.rs runtime/src cli/src   # exactly 5 call sites
grep -rn "Verifier"       --include=*.rs runtime/src cli/src   # no ed25519_dalek::Verifier import
grep -rn "SigningKey"     --include=*.rs runtime/src cli/src   # none
sha256sum Governance_OS_Capability_Acceptance_Contract_v3.md \
          framework/contracts/source/GOVERNANCE_CAPABILITY_ACCEPTANCE_CONTRACT_v3.md   # identical, 4c2df291…
```

All of the above are asserted by
`tests/certification/srr.rs::the_no_bypass_and_no_signing_preservation_census_still_holds` and
`::section_6_effects_are_enforced_inside_their_sinks`, so a change that breaks them fails the suite rather than
only the greps.
