#!/usr/bin/env bash
# P2-AR-0019 — AC-14 / R1 preservation regression: re-run the four Phase-1 R1 held-out suites UNEDITED against this
# worktree, following release/verification/4.1.6-r1-4/evidence/REPRODUCTION.md §5-§6 (copy byte-identically, expose the
# worktree at the ../wt/<name> paths their Cargo.toml files expect by symlink, run each test binary single-threaded).
set -u
WT="$(cd "$(dirname "$0")/../../../../.." && pwd)"
SCR="${SCR:?set SCR to an empty scratch directory}"
V=$WT/release/verification
STRIP='env -u GOV_BREAK_GLASS -u GOV_BREAKGLASS -u GOV_TRUST_OVERRIDE -u GOV_SKIP_VERIFY -u GOV_ALLOW_UNSIGNED -u GOV_RELEASE_AUTHORITY -u GOV_HUMAN_GATE_APPROVED -u GOV_FLOOR_OVERRIDE -u GOV_MINIMUM_SECURE_RELEASE -u GOV_MACHINE_STATE_DIR -u GOV_ROLE -u GOV_SESSION -u GOV_CANONICAL_ROOT'
export CARGO_BUILD_JOBS=2
mkdir -p "$SCR/wt" "$SCR/ho27/tests/common" "$SCR/ho29/tests/common" "$SCR/ho31/tests/common" "$SCR/ho33/tests/common" "$SCR/base"
for n in srr1-r1-verify srr1-r1-verify-2 srr1-r1-verify-3 srr1-r1-verify-4; do ln -sfn "$WT" "$SCR/wt/$n"; done
# AR-0027
cp "$V/4.1.6-r1/evidence/heldout-tests/Cargo.toml.txt" "$SCR/ho27/Cargo.toml"
cp "$V/4.1.6-r1/evidence/heldout-tests/forge.rs" "$SCR/ho27/tests/common/forge.rs"
cp "$V"/4.1.6-r1/evidence/heldout-tests/heldout_srr*.rs "$SCR/ho27/tests/"
# AR-0029
cp "$V/4.1.6-r1-2/evidence/heldout-tests/Cargo.toml.txt" "$SCR/ho29/Cargo.toml"
cp "$V/4.1.6-r1-2/evidence/heldout-tests/mint.rs" "$SCR/ho29/tests/common/mint.rs"
printf 'pub mod mint;\n' > "$SCR/ho29/tests/common/mod.rs"
cp "$V"/4.1.6-r1-2/evidence/heldout-tests/ho_*.rs "$SCR/ho29/tests/"
# AR-0031
cp "$V/4.1.6-r1-3/evidence/heldout-tests/Cargo.toml.txt" "$SCR/ho31/Cargo.toml"
cp "$V/4.1.6-r1-3/evidence/heldout-tests/bench.rs" "$SCR/ho31/tests/common/bench.rs"
printf 'pub mod bench;\n' > "$SCR/ho31/tests/common/mod.rs"
cp "$V"/4.1.6-r1-3/evidence/heldout-tests/hx_*.rs "$SCR/ho31/tests/"
# AR-0033
cp "$V/4.1.6-r1-4/evidence/heldout-tests/Cargo.toml.txt" "$SCR/ho33/Cargo.toml"
cp "$V/4.1.6-r1-4/evidence/heldout-tests/common.rs" "$SCR/ho33/tests/common/mod.rs"
cp "$V"/4.1.6-r1-4/evidence/heldout-tests/hv_*.rs "$SCR/ho33/tests/"
git -C "$WT" archive 30aa98a10fd7f5ed85439b0d676761080519ceed runtime/src cli/src | tar -x -C "$SCR/base"
echo "worktree: $WT HEAD $(git -C "$WT" rev-parse HEAD) (uncommitted changes: $(git -C "$WT" status --porcelain -- runtime cli capabilities framework | wc -l) paths)"
for d in ho27 ho29 ho31 ho33; do
  echo "################ suite $d"
  cd "$SCR/$d"
  for t in tests/*.rs; do
    b=$(basename "$t" .rs)
    echo "=== cargo test --test $b"
    CARGO_TARGET_DIR="$SCR/target-$d" AR0033_GOV_BIN="$WT/target/release/gov" AR0033_BASE_SRC="$SCR/base" \
      $STRIP "$HOME/.cargo/bin/cargo" test --test "$b" -- --test-threads=1 2>&1 | grep -E '^test |test result|panicked|FAILED|^error(\[|:)'
  done
done
