# AR-0027 — reproducing this verification

## Pinned inputs

| Item | Value |
|---|---|
| Worktree HEAD verified | `0ce7f9f0a7028d54bc5beef57f0ef35a935e244d` (branch `phase1/srr1-r1-verify`) |
| Candidate tag | `srr1-r1-candidate-1` → commit `229d1543be0357b52f7c7e6405918171bc8e6631` |
| Builder work commit | `949c4d343a6d5f203534afa6e3363992fee12488` |
| Base commit for the harness-history check | `1e31f6b` |
| Toolchain | `cargo 1.98.1 (e35f3d1c1 2025-03-11)` |

## 1. Verify the pinned digests

```bash
sha256sum release/root-of-trust/signed-release-root-v1/01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md \
          release/root-of-trust/signed-release-root-v1/00-ARCHITECTURE.md \
          release/orchestration/phase-1/GATES/OWNER-DECISION-0006-BELOW-FLOOR-RECOVERY.md \
          Governance_OS_Capability_Acceptance_Contract_v3.md
git show 2b36b44:spec/architecture/ARCH-0003.yaml | sha256sum     # 42681978...
python3 -c "import yaml,hashlib;print(hashlib.sha256(yaml.safe_load(open('spec/architecture/ARCH-0003.yaml'))['body'].encode()).hexdigest())"  # 093cb78e...
```

Expected values are tabulated in `../00-VERIFICATION-REPORT.md` and in `REVIEWED-CONTENT-DIGESTS.txt`.

## 2. Reproduce the regression

```bash
export PATH="$HOME/.cargo/bin:$PATH"
export CARGO_TARGET_DIR=/path/to/scratch/cargo-target
env -u GOV_BREAK_GLASS -u GOV_TRUST_OVERRIDE -u GOV_SKIP_VERIFY -u GOV_MACHINE_STATE_DIR \
    cargo test --lib                    # 26 passed; 0 failed
env -u GOV_BREAK_GLASS -u GOV_TRUST_OVERRIDE -u GOV_SKIP_VERIFY -u GOV_MACHINE_STATE_DIR \
    cargo test --test certification     # 64 passed; 0 failed
```

## 3. Run the held-out suite

The held-out crate is standalone and **outside** the product tree and its cargo workspace. It depends on `gov-runtime`
by path, so running it requires no modification to any product file.

```bash
mkdir -p /path/to/scratch/heldout/tests/common
cp heldout-tests/Cargo.toml.txt      /path/to/scratch/heldout/Cargo.toml
cp heldout-tests/forge.rs            /path/to/scratch/heldout/tests/common/forge.rs
cp heldout-tests/heldout_srr*.rs     /path/to/scratch/heldout/tests/
```

`Cargo.toml` expects the worktree at `../wt/srr1-r1-verify` relative to the crate; adjust the `gov-runtime` path
dependency and the `candidate_kernel()` helper in each test file if you lay it out differently.

```bash
cd /path/to/scratch/heldout
for t in heldout_srr heldout_srr2 heldout_srr3 heldout_srr4; do
  cargo test --test $t -- --test-threads=1 --nocapture
done
```

**`--test-threads=1` is required.** Several scenarios manipulate `XDG_STATE_HOME` and `GOV_*`, which are
process-global; running them in parallel makes them interfere. Each test isolates itself by stripping every `GOV_*`
variable and pointing `XDG_STATE_HOME` at a fresh directory under the OS temp dir.

Expected: **12 / 8 / 5 / 4 = 29 passed, 0 failed.** Captured output is in `HELD-OUT-TEST-OUTPUT.txt`.

Note on reading results: a passing test means "the asserted behaviour is what the candidate does". Several tests
deliberately assert an **observed weakness**; those assertions carry an `OBSERVED:` message in-source. The findings
they pin are `b1` → `AR27-N1`, `c4` → `AR27-OD1`, `d3` → **`AR27-B1` (blocking)**, `e1` → `AR27-N2`,
`e2` → `AR27-N3`.

## 4. Reproduce the certification-harness history check (disclosed residual 5)

```bash
git diff --stat 1e31f6b 949c4d3 -- tests/        # 2026 insertions, 0 deletions
git diff        1e31f6b 949c4d3 -- tests/certification/common.rs tests/certification/main.rs
grep -c '^#\[test\]' tests/certification/srr.rs  # 15  → 64 total - 15 = 49 pre-existing
```

## 5. Reproduce the ingress-set and transaction-abort structural proof

```bash
grep -rn "srr::admit("     --include=*.rs runtime/src cli/src   # exactly 5 sites
grep -rn "install_kernel"  --include=*.rs runtime/src cli/src   # exactly 5 call sites, all from an AuthenticatedRelease
grep -n  "rollback_internal\|^fn rollback_internal" runtime/src/update.rs
grep -n  "rollback" cli/src/main.rs                             # CLI lands on rollback_opts => transaction_abort=false
```

## 6. Reproduce the "gov never signs" check

```bash
grep -rn "SigningKey\|SecretKey\|PRIVATE KEY" --include=*.rs runtime/src cli/src
find . -not -path './target/*' -not -path './.git/*' \( -name '*.pem' -o -name '*.key' -o -name '*.p12' \)
```
