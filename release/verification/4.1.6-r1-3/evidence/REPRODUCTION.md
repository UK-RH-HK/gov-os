# AR-0031 — reproducing this verification

## Pinned inputs

| Item | Value |
|---|---|
| Worktree HEAD verified | `26bfe9bbf9141a4d27126da0d09bbeceb4a395d7` (branch `phase1/srr1-r1-verify-3`) |
| Candidate tag | `srr1-r1-candidate-3` |
| Repair work commit | `748c5d3` (AR-0030) |
| Prior verifications | AR-0027 at `release/verification/4.1.6-r1/`, AR-0029 at `release/verification/4.1.6-r1-2/` |
| Toolchain | `cargo 1.98.1 (797e8a9bc 2026-08-05)` |

Throughout: `export PATH="$HOME/.cargo/bin:$PATH"` and `CARGO_TARGET_DIR` pointed into scratch. Every test run is
prefixed with `env -u` for the nine refused-authority variables **plus `GOV_MACHINE_STATE_DIR`**, so no ambient
environment can affect a result. `GOV_MACHINE_STATE_DIR` is stripped for the same reason the others are and is
then set *deliberately and locally* by the `hx_b` scenarios, which is the whole subject of `AR31-B2`.

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

Expected values in `../REVIEWED-CONTENT-DIGESTS.txt`. All six matched. A mismatch is a STOP condition.

## 2. Reproduce the regression

```bash
$STRIP cargo test --lib                  # 36 passed; 0 failed
$STRIP cargo test --test certification   # 70 passed; 0 failed
git diff --numstat 748c5d3~1 748c5d3     # tests/certification/srr.rs is 866 / 0
```

Captured in `REGRESSION.txt`.

## 3. Verify the owner-closed items are byte-identical across the repair

Compare each function body before and after the repair work commit rather than trusting the file-level diff, since
both containing files were edited:

```bash
python3 - <<'PY'
import subprocess
def body(text, name):
    i = text.find("fn %s(" % name)
    if i < 0: return None
    rest = text[text.rfind("\n", 0, i)+1:]
    depth, started = 0, False
    for k, c in enumerate(rest):
        if c == '{': depth += 1; started = True
        elif c == '}':
            depth -= 1
            if started and depth == 0: return rest[:k+1]
for f, fns in [("runtime/src/srr/state.rs", ["resolve_state_root", "default_state_root"]),
               ("runtime/src/srr/breakglass.rs", ["exit_satisfied", "exit_condition_description"])]:
    old = subprocess.run(["git","show",f"748c5d3~1:{f}"], capture_output=True, text=True).stdout
    new = open(f).read()
    for fn in fns:
        print(fn, "IDENTICAL" if body(old,fn) == body(new,fn) else "CHANGED")
PY
```

All four `IDENTICAL`. `EXIT_POLICY` and `REFUSED_AUTHORITY_ENV` likewise.

## 4. Lay out the worktree symlinks the prior suites expect

Both prior crates depend on `gov-runtime` by a fixed relative path. Symlinks let their evidence run against this
worktree without editing a line of either. (In this session both symlinks already existed but pointed at a removed
worktree, so they were repointed.)

```bash
ln -sfn srr1-r1-verify-3 <scratch>/wt/srr1-r1-verify
ln -sfn srr1-r1-verify-3 <scratch>/wt/srr1-r1-verify-2
```

## 5. Re-run AR-0027's held-out suite, unmodified

```bash
mkdir -p <scratch>/heldout-ar0027-rerun/tests/common
cp release/verification/4.1.6-r1/evidence/heldout-tests/Cargo.toml.txt <scratch>/heldout-ar0027-rerun/Cargo.toml
cp release/verification/4.1.6-r1/evidence/heldout-tests/forge.rs       <scratch>/heldout-ar0027-rerun/tests/common/forge.rs
cp release/verification/4.1.6-r1/evidence/heldout-tests/heldout_srr*.rs <scratch>/heldout-ar0027-rerun/tests/
cd <scratch>/heldout-ar0027-rerun
for t in heldout_srr heldout_srr2 heldout_srr3 heldout_srr4; do
  $STRIP cargo test --test $t -- --test-threads=1 --nocapture
done
```

Expected **26 passed, 3 failed**: `heldout_srr` 12/0, `heldout_srr2` 6/2, `heldout_srr3` 4/1, `heldout_srr4` 4/0.
The three failures are its `OBSERVED:` weakness assertions flipping. Captured in `AR-0027-HELD-OUT-RERUN.txt`.

## 6. Re-run AR-0029's held-out suite, unmodified

```bash
mkdir -p <scratch>/heldout-ar0029-rerun/tests/common
cp release/verification/4.1.6-r1-2/evidence/heldout-tests/Cargo.toml.txt <scratch>/heldout-ar0029-rerun/Cargo.toml
cp release/verification/4.1.6-r1-2/evidence/heldout-tests/mint.rs        <scratch>/heldout-ar0029-rerun/tests/common/mint.rs
cp release/verification/4.1.6-r1-2/evidence/heldout-tests/ho_*.rs        <scratch>/heldout-ar0029-rerun/tests/
printf '#![allow(dead_code, unused_imports)]\npub mod mint;\n' > <scratch>/heldout-ar0029-rerun/tests/common/mod.rs
cd <scratch>/heldout-ar0029-rerun
for t in ho_a_allowlist ho_b_coverage ho_c_deadlock ho_d_expiry ho_e_rootexpiry ho_f_preservation; do
  $STRIP cargo test --test $t -- --test-threads=1 --nocapture
done
```

Expected **26 passed, 2 failed**, with `ho_f_preservation` failing to COMPILE:

| group | result |
|---|---|
| `ho_a_allowlist` | 6 / 0 |
| `ho_b_coverage` | **4 / 2** — `b3` and `b6` now fail; both are the repair working |
| `ho_c_deadlock` | 5 / 0 — its two `OBSERVED` failures (`c3`, `c4`) flipped to passing |
| `ho_d_expiry` | 5 / 0 |
| `ho_e_rootexpiry` | 6 / 0 |
| `ho_f_preservation` | `error: cannot construct AuthenticatedRelease with struct literal syntax due to private fields` |

Captured in `AR-0029-HELD-OUT-RERUN.txt`. The exact new failure messages are
`root_update unexpectedly guards; re-derive this census` (`b3`) and
`a guard now sits between the allow-list entry and the gate creation` (`b6`).

## 7. Run this verifier's held-out suite

```bash
mkdir -p <scratch>/heldout-ar0031/tests/common
cp heldout-tests/Cargo.toml.txt <scratch>/heldout-ar0031/Cargo.toml
cp heldout-tests/bench.rs       <scratch>/heldout-ar0031/tests/common/bench.rs
cp heldout-tests/hx_*.rs        <scratch>/heldout-ar0031/tests/
printf '#![allow(dead_code, unused_imports)]\npub mod bench;\n' > <scratch>/heldout-ar0031/tests/common/mod.rs
cd <scratch>/heldout-ar0031
for t in hx_a_census hx_b_failopen hx_c_prior_evidence hx_d_acquisition_and_preservation; do
  $STRIP cargo test --test $t -- --test-threads=1 --nocapture
done
```

The crate's `Cargo.toml` depends on `../wt/srr1-r1-verify-3/runtime`, and `bench::wt()` resolves the same path;
adjust both together if the tree is laid out differently.

**`--test-threads=1` is required.** The `hx_b` scenarios set and clear `XDG_STATE_HOME` and
`GOV_MACHINE_STATE_DIR`, which are process-global. Every scenario isolates itself in a fresh directory under the
OS temp dir and strips every relevant variable first.

Expected: **26 passed, 8 failed** — `hx_a` 6/2, `hx_b` 3/3, `hx_c` 6/2, `hx_d` 11/1. Captured in
`AR-0031-HELD-OUT-OUTPUT.txt`.

| failing scenario | finding |
|---|---|
| `hx_a::a5` | `AR31-N3` — the bullet 2 census clause is a source-literal property |
| `hx_a::a8` | **`AR31-B1`** — §6 bullet 7 falsified |
| `hx_b::b2`, `::b3`, `::b4` | **`AR31-B2`** — both enforcement points fail open |
| `hx_c::c2`, `::c3` | `AR31-N4` — two `ho_f` sub-checks dropped in the migration |
| `hx_d::d3` | `AR31-N1` — a second primitive for §6 bullet 5 |

A **passing** test means the asserted behaviour is what candidate 3 does. Assertions whose message begins
`OBSERVED:` pin a weakness this verifier found rather than a behaviour the candidate should have, so they
**fail**. A failing `OBSERVED:` assertion is a finding, not a broken test.

## 8. Reproduce the census attack by hand

```bash
# bullet 2 — the only literal minting of a human-gate record
grep -rn 'new_record("human-gate"' runtime/src cli/src          # exactly 1, orchestration/gates.rs
grep -n  'fn build(' runtime/src/orchestration/gates.rs         # private, takes &Clearance

# bullet 3 — the only settable certification status, and the only caller
grep -rn '"certification": {"status": certification_status' runtime/src   # exactly 1, release.rs
grep -rn '"CERTIFIED"' runtime/src cli/src                      # only comparisons, in update.rs
grep -rn 'release::build(' runtime/src cli/src                  # exactly 1 caller

# bullet 4 — the only writer of trust/root.json
grep -rn 'root_metadata_path()' runtime/src cli/src             # 2 files: state.rs writes, verifier.rs reads
grep -rn 'trust_dir()' runtime/src cli/src                      # state.rs only

# bullet 5 — the sink's callers, and the second primitive
grep -rn 'guard_acquisition(' runtime/src cli/src               # 1 caller: capabilities/governance.rs
grep -n  'guard_write\|guard_acquisition' runtime/src/tools.rs  # install: operation guard only

# bullets 6 and 7 — the effect variants that are never used
grep -rn 'Effect::FloorLowerOrReset' runtime/src cli/src               # breakglass.rs only
grep -rn 'Effect::PresentBelowFloorReleaseAsCurrent' runtime/src cli/src  # breakglass.rs only

# bullet 7 — the surfaces that do not carry the marking
grep -c 'breakglass\|is_degraded\|Degraded\|below_floor' runtime/src/doctor.rs   # 0
sed -n '/pub fn check(/,/^}/p' runtime/src/update.rs | grep -c 'degraded'        # 0
```

## 9. Reproduce the fail-open by hand

```bash
# the ONLY error return in resolve_state_root, and what triggers it
sed -n '/pub fn resolve_state_root/,/^}/p' runtime/src/srr/state.rs

# the two fail-open sites, and nowhere else in the tree
grep -rn 'let Ok(root) = crate::srr::state::resolve_state_root() else {' runtime/src cli/src   # exactly 2

# the sink that is immune, because it takes the MachineState
grep -n 'guard_effect_on' runtime/src/srr/state.rs

# the gate-creation path with no operation-level guard
sed -n '/pub fn create_system/,/^}/p' runtime/src/orchestration/gates.rs   # no guard_write
```

## 10. Reproduce the preservation census

```bash
grep -rn 'srr::admit('    --include=*.rs runtime/src cli/src   # exactly 5
grep -rn 'install_kernel' --include=*.rs runtime/src cli/src   # exactly 5 call sites
grep -rn 'SigningKey'     --include=*.rs runtime/src cli/src   # none
grep -rn 'use ed25519_dalek.*Verifier' --include=*.rs runtime/src cli/src   # none
grep -rn 'skip_verify\|allow_unsigned\|force_unsigned' --include=*.rs runtime/src cli/src  # only REFUSED_AUTHORITY_ENV
sha256sum Governance_OS_Capability_Acceptance_Contract_v3.md \
          framework/contracts/source/GOVERNANCE_CAPABILITY_ACCEPTANCE_CONTRACT_v3.md   # identical
grep -rn 'reqwest\|https\?://\|TcpStream' runtime/src/srr/breakglass.rs   # none (SRR-R0-L7)
```
