# AR-0033 — reproducing this verification

## Pinned inputs

| Item | Value |
|---|---|
| Worktree HEAD verified | `84b9ee8b8a34c4308f25ed12af89b90344a3bcab` (branch `phase1/srr1-r1-verify-4`, tree clean) |
| Candidate tag | `srr1-r1-candidate-4` |
| Repair work commit | `cf52741` (AR-0032) |
| Base commit compared against | `30aa98a10fd7f5ed85439b0d676761080519ceed` (candidate 3) |
| Prior verifications | AR-0027 `release/verification/4.1.6-r1/`, AR-0029 `…-r1-2/`, AR-0031 `…-r1-3/` |
| Toolchain | `cargo 1.98.1 (797e8a9bc 2026-08-05)`, `rustc 1.98.1 (48a229cea 2026-09-01)` |

Throughout: `export PATH="$HOME/.cargo/bin:$PATH"` and `CARGO_TARGET_DIR` pointed into scratch. Every test run is
prefixed with `env -u` for the nine refused-authority variables **plus `GOV_MACHINE_STATE_DIR`**, so no ambient
environment can affect a result. `GOV_MACHINE_STATE_DIR` is stripped for the same reason the others are and is
then set *deliberately and locally* by `hv_c`, which is the subject of `AR31-B2`.

```bash
STRIP='env -u GOV_BREAK_GLASS -u GOV_BREAKGLASS -u GOV_TRUST_OVERRIDE -u GOV_SKIP_VERIFY
       -u GOV_ALLOW_UNSIGNED -u GOV_RELEASE_AUTHORITY -u GOV_HUMAN_GATE_APPROVED
       -u GOV_FLOOR_OVERRIDE -u GOV_MINIMUM_SECURE_RELEASE -u GOV_MACHINE_STATE_DIR'
```

## 1. Verify the pinned digests

```bash
sha256sum release/root-of-trust/signed-release-root-v1/01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md \
          release/orchestration/phase-1/GATES/OWNER-DECISION-0006-BELOW-FLOOR-RECOVERY.md \
          release/orchestration/phase-1/GATES/OWNER-DECISION-0008-CONVERGENCE-OPTION-B.md \
          Governance_OS_Capability_Acceptance_Contract_v3.md
```

Expected: `70977d11…`, `903407729…`, `aa541eab…`, `4c2df291…`. All matched. A mismatch is a STOP condition.
Full list in `../REVIEWED-CONTENT-DIGESTS.txt`.

## 2. Reproduce the product regression

```bash
$STRIP cargo test --lib                  # 42 passed; 0 failed
$STRIP cargo test --test certification   # 79 passed; 0 failed
git diff --numstat 30aa98a HEAD -- tests/certification/srr.rs   # empty: the file is not in the diff
cargo fmt --check                        # FAILS: 57 hunks, 8 files — see RUSTFMT-CHECK.txt (AR33-N5)
```

Captured in `REGRESSION.txt` and `RUSTFMT-CHECK.txt`.

## 3. Export the base commit, for the derivation attack

```bash
mkdir -p <scratch>/base
git archive 30aa98a10fd7f5ed85439b0d676761080519ceed runtime/src cli/src | tar -x -C <scratch>/base
```

This is the source that `hv_a::a2` and `hv_a::a5` grade with the **candidate's** signatures. It is what shows the
mechanism is not vacuous, and what exposes the acceptance-marker weakness.

## 4. Build the candidate `gov` binary (the CLI-boundary tests drive the real binary)

```bash
CARGO_TARGET_DIR=<scratch>/target cargo build --bin gov
```

## 5. Run my held-out suite

Lives outside the product tree and outside the cargo workspace; the product is not modified to run it.

```bash
mkdir -p <scratch>/wt <scratch>/ho33/tests/common
ln -sfn <this worktree> <scratch>/wt/srr1-r1-verify-4
cp release/verification/4.1.6-r1-4/evidence/heldout-tests/Cargo.toml.txt <scratch>/ho33/Cargo.toml
cp release/verification/4.1.6-r1-4/evidence/heldout-tests/common.rs      <scratch>/ho33/tests/common/mod.rs
cp release/verification/4.1.6-r1-4/evidence/heldout-tests/hv_*.rs        <scratch>/ho33/tests/
cd <scratch>/ho33
for t in hv_a_derivation hv_b_bullet7 hv_c_failclosed hv_d_sinks_and_preservation; do
  CARGO_TARGET_DIR=<scratch>/target-ho33 \
  AR0033_GOV_BIN=<scratch>/target/debug/gov \
  AR0033_BASE_SRC=<scratch>/base \
  $STRIP cargo test --test $t -- --test-threads=1 --nocapture
done
```

**`--test-threads=1` is required**: several tests set process-wide environment (`HOME`, `XDG_STATE_HOME`,
`GOV_MACHINE_STATE_DIR`) to control which protected machine state the library resolves. Running them in parallel
races and produces spurious results.

Expected: **31 passed / 0 failed** (10 + 7 + 6 + 8). Captured in `HELD-OUT-TEST-OUTPUT.txt`.

| file | what it attacks |
|---|---|
| `hv_a_derivation.rs` | the derivation itself: independent re-derivation, the pre-repair census, 9 plausible future primitives, the bullet-6 sink, acceptance markers, positive-control genuineness, the absence-claim mechanism, the rustfmt assumption, the `#[cfg(test)]` cut, the exemption |
| `hv_b_bullet7.rs` | `AR31-B1` in both directions, in-process and through the binary; the envelope bypass; the no-HOME false-positive path |
| `hv_c_failclosed.rs` | `AR31-B2` fail-closed at both points; §5 restoration unblocked; break-glass **exit**; unreadable marking; owner-closed byte-identity |
| `hv_d_sinks_and_preservation.rs` | the three derivation-found closures, `AR31-N1`–`N4`, and the frozen R1 preservation obligations |

## 6. Rerun the three prior held-out suites, unmodified

Copy each suite byte-identically (`cmp`-verify) and retarget only the `Cargo.toml` dependency path by symlink.
Each suite expects its helper module under `tests/common/`:

```bash
ln -sfn <this worktree> <scratch>/wt/srr1-r1-verify     # AR-0027
ln -sfn <this worktree> <scratch>/wt/srr1-r1-verify-2   # AR-0029
ln -sfn <this worktree> <scratch>/wt/srr1-r1-verify-3   # AR-0031

# AR-0027: forge.rs is included by #[path = "common/forge.rs"]
cp .../4.1.6-r1/evidence/heldout-tests/forge.rs   <scratch>/ho27/tests/common/forge.rs
# AR-0029 and AR-0031 use `mod common;` with a re-export
cp .../4.1.6-r1-2/evidence/heldout-tests/mint.rs  <scratch>/ho29/tests/common/mint.rs
printf 'pub mod mint;\n'                        > <scratch>/ho29/tests/common/mod.rs
cp .../4.1.6-r1-3/evidence/heldout-tests/bench.rs <scratch>/ho31/tests/common/bench.rs
printf 'pub mod bench;\n'                       > <scratch>/ho31/tests/common/mod.rs

# run each TEST BINARY separately, single-threaded
for b in <each .rs under tests/>; do $STRIP cargo test --test $b -- --test-threads=1; done
```

Expected:

| suite | figure | failing tests |
|---|---|---|
| AR-0027 | **26 passed / 3 failed** | `b1`, `b2`, `d3` |
| AR-0029 | **26 passed / 2 failed of 28 compiled**; `ho_f_preservation` does not compile (`cannot construct AuthenticatedRelease with struct literal syntax due to private fields` — `AR29-N1` closing) | `b3`, `b6` |
| AR-0031 | **27 passed / 7 failed** | `a1`, `a5`, `a8`, `b6`, `c2`, `c3`, `d2` |

Captured in `AR-002{7,9}-HELD-OUT-RERUN.txt` and `AR-0031-HELD-OUT-RERUN.txt`. Per-failure disposition is in
`../00-VERIFICATION-REPORT.md` §9.

## 7. The standalone derivation probe

`derive.py` and `future.py` are an independent Python re-implementation of
`section_6_coverage_is_derived_from_the_product`, used to explore the mechanism before the Rust suite pinned the
results. They agree with the Rust suite and with the candidate.

```bash
python3 derive.py    # 84 files / 740 functions / 0 violations, three splitter configurations
python3 future.py    # the plausible-future-primitive probes
```

Output captured in `DERIVATION-ATTACK.txt`. Both scripts hard-code the worktree path at the top; edit `ROOT`.

## Notes on what is NOT reproduced here

* No product source was modified, and nothing in this directory is product material.
* `release/verification/4.1.6-r1-4/` is the only directory this run created.
* The break-glass entry ceremony (owner-signed token, publisher, full `kernel reinstall --break-glass`) is
  exercised by the candidate's own `tests/certification/section6.rs::marked_machine`, which I ran as part of the
  79-test certification suite. My harness marks a machine by writing the marking record in the exact shape
  `breakglass::read_marking` accepts, which is the same approach AR-0031 used and is sufficient for every
  property under test here — each test asserts `is_degraded` is true before proceeding.
