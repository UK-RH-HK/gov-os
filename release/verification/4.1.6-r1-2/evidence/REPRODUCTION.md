# AR-0029 — reproducing this verification

## Pinned inputs

| Item | Value |
|---|---|
| Worktree HEAD verified | `2baff074095532d0e7ff42dad2f6fa316f771207` (branch `phase1/srr1-r1-verify-2`) |
| Candidate tag | `srr1-r1-candidate-2` |
| Repair work commit | `4c7c40c` (AR-0028) |
| Prior verification | AR-0027 at `release/verification/4.1.6-r1/` |
| Toolchain | `cargo 1.98.1 (797e8a9bc 2026-08-05)`, `rustc 1.98.1 (48a229cea 2026-09-01)` |

Throughout: `export PATH="$HOME/.cargo/bin:$PATH"` and `CARGO_TARGET_DIR` pointed into scratch. Every test run is
prefixed with `env -u` for the nine refused-authority variables plus `GOV_MACHINE_STATE_DIR`, so no ambient
environment can affect a result.

```bash
STRIP='env -u GOV_BREAK_GLASS -u GOV_BREAKGLASS -u GOV_TRUST_OVERRIDE -u GOV_SKIP_VERIFY
       -u GOV_ALLOW_UNSIGNED -u GOV_RELEASE_AUTHORITY -u GOV_HUMAN_GATE_APPROVED
       -u GOV_FLOOR_OVERRIDE -u GOV_MINIMUM_SECURE_RELEASE -u GOV_MACHINE_STATE_DIR'
```

## 1. Verify the pinned digests

```bash
sha256sum release/root-of-trust/signed-release-root-v1/01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md \
          release/root-of-trust/signed-release-root-v1/00-ARCHITECTURE.md \
          release/orchestration/phase-1/GATES/OWNER-DECISION-0006-BELOW-FLOOR-RECOVERY.md \
          release/orchestration/phase-1/GATES/OWNER-DECISION-0007-R1-QUESTIONS.md \
          Governance_OS_Capability_Acceptance_Contract_v3.md
python3 -c "import yaml,hashlib;print(hashlib.sha256(yaml.safe_load(open('spec/architecture/ARCH-0003.yaml'))['body'].encode()).hexdigest())"
```

Expected values are in `../REVIEWED-CONTENT-DIGESTS.txt`. All six matched; a mismatch would be a STOP condition.

## 2. Reproduce the regression

```bash
$STRIP cargo test --lib                 # 31 passed; 0 failed
$STRIP cargo test --test certification  # 65 passed; 0 failed
git diff --numstat 4c7c40c~1 4c7c40c    # tests/certification/srr.rs is 177 / 0
```

Captured in `REGRESSION.txt`.

## 3. Re-run AR-0027's held-out suite unmodified

The crate expects the worktree at `../wt/srr1-r1-verify` relative to itself, so a symlink lets its evidence run
against this worktree without editing a line of it.

```bash
ln -sfn srr1-r1-verify-2 <scratch>/wt/srr1-r1-verify
mkdir -p <scratch>/heldout-ar0027-rerun/tests/common
cp release/verification/4.1.6-r1/evidence/heldout-tests/Cargo.toml.txt <scratch>/heldout-ar0027-rerun/Cargo.toml
cp release/verification/4.1.6-r1/evidence/heldout-tests/forge.rs       <scratch>/heldout-ar0027-rerun/tests/common/forge.rs
cp release/verification/4.1.6-r1/evidence/heldout-tests/heldout_srr*.rs <scratch>/heldout-ar0027-rerun/tests/
cd <scratch>/heldout-ar0027-rerun
for t in heldout_srr heldout_srr2 heldout_srr3 heldout_srr4; do
  $STRIP cargo test --test $t -- --test-threads=1 --nocapture
done
```

Expected: **26 passed, 3 failed** — `heldout_srr2::b1`, `heldout_srr2::b2`, `heldout_srr3::d3`, each an
`OBSERVED:` weakness assertion flipping. Captured in `AR-0027-HELD-OUT-RERUN.txt`.

## 4. Run AR-0029's own held-out suite

```bash
mkdir -p <scratch>/heldout-ar0029/tests/common
cp heldout-tests/Cargo.toml.txt <scratch>/heldout-ar0029/Cargo.toml
cp heldout-tests/mint.rs        <scratch>/heldout-ar0029/tests/common/mint.rs
cp heldout-tests/ho_*.rs        <scratch>/heldout-ar0029/tests/
printf '#![allow(dead_code, unused_imports)]\npub mod mint;\n' > <scratch>/heldout-ar0029/tests/common/mod.rs
cd <scratch>/heldout-ar0029
for t in ho_a_allowlist ho_b_coverage ho_c_deadlock ho_d_expiry ho_e_rootexpiry ho_f_preservation; do
  $STRIP cargo test --test $t -- --test-threads=1 --nocapture
done
```

The crate's `Cargo.toml` depends on `../wt/srr1-r1-verify-2/runtime`, and `wt()` / `candidate` helpers resolve
the same path; adjust both if you lay the tree out differently.

**`--test-threads=1` is required.** Several scenarios set `XDG_STATE_HOME`/`HOME`, which are process-global.
Every scenario isolates itself in a fresh directory under the OS temp dir and strips every `GOV_*` variable
first.

Expected: **6 / 4 / 3 / 5 / 6 / 7 = 31 passed, 4 failed.** The four failures are the `OBSERVED:` assertions:

| test | records |
|---|---|
| `ho_b_coverage::b1`, `::b2` | **`AR29-B1`** — `gov trust root-update` completes a trust-policy mutation below floor (blocking) |
| `ho_c_deadlock::c3`, `::c4` | `AR29-C1` — an unreadable marking cannot be cleared, and the machine reports the opposite of what it enforces (non-blocking) |

Captured in `HELD-OUT-TEST-OUTPUT.txt`.

## 5. Reproduce the §6 guard-coverage census by hand

```bash
grep -rn "guard_write(" --include=*.rs runtime/src cli/src | grep -v "pub fn guard_write"   # 27 labels
grep -rn "breakglass::guard" --include=*.rs runtime/src cli/src                              # + update.rs:410
sed -n '51,81p'   runtime/src/srr/provision.rs        # root_update: no guard on the path  (AR29-B1)
sed -n '143,149p' runtime/src/orchestration/gates.rs  # create_system: no guard             (AR29-B2)
grep -n  "gates::create_system" runtime/src/kernel_trust.rs runtime/src/update.rs
grep -n  "pub fn build" runtime/src/release.rs        # takes no Project, so cannot reach guard_write
```

## 6. Reproduce the preservation census

```bash
grep -rn "srr::admit("    --include=*.rs runtime/src cli/src   # exactly 5
grep -rn "install_kernel" --include=*.rs runtime/src cli/src   # exactly 5 call sites
grep -rn "Verifier"       --include=*.rs runtime/src cli/src   # no ed25519_dalek::Verifier import
grep -rn "SigningKey"     --include=*.rs runtime/src cli/src   # none
grep -n  "rollback_internal(" runtime/src/update.rs            # 2 callers, the fn is private
sha256sum Governance_OS_Capability_Acceptance_Contract_v3.md \
          framework/contracts/source/GOVERNANCE_CAPABILITY_ACCEPTANCE_CONTRACT_v3.md   # identical
```

## Reading the results

A **passing** test means the asserted behaviour is what candidate 2 does. Several assertions deliberately pin an
observed **weakness** rather than a desired behaviour; those carry `OBSERVED:` in the message and therefore
**fail**. A failing `OBSERVED:` assertion is a finding, not a broken test.
