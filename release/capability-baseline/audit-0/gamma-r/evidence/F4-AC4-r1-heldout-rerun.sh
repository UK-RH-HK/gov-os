#!/usr/bin/env bash
# P2-AR-0010 — AC-4 / F4: re-run the Phase-1 R1 iteration-4 held-out suite (AR-0033, release/verification/4.1.6-r1-4/
# evidence/heldout-tests/) UNEDITED against this candidate, following that directory's REPRODUCTION.md §5.
# The suite is copied verbatim into a scratch crate outside the product tree; the candidate worktree is exposed at the
# path its Cargo.toml expects (../wt/srr1-r1-verify-4). The release `gov` built from this worktree is used as
# AR0033_GOV_BIN (same product source as the debug binary REPRODUCTION.md builds).
set -u
SCR="${SCR:?set SCR to the scratch parent containing ho33/, wt/srr1-r1-verify-4 -> worktree, base/}"
WT="$(cd "$(dirname "$0")/../../../../.." && pwd)"
STRIP='env -u GOV_BREAK_GLASS -u GOV_BREAKGLASS -u GOV_TRUST_OVERRIDE -u GOV_SKIP_VERIFY -u GOV_ALLOW_UNSIGNED -u GOV_RELEASE_AUTHORITY -u GOV_HUMAN_GATE_APPROVED -u GOV_FLOOR_OVERRIDE -u GOV_MINIMUM_SECURE_RELEASE -u GOV_MACHINE_STATE_DIR -u GOV_ROLE -u GOV_SESSION -u GOV_CANONICAL_ROOT'
echo "candidate worktree: $WT  HEAD $(git -C "$WT" rev-parse HEAD)"
echo "product identity: $(python3 "$WT/release/orchestration/phase-2/tools/product_identity.py" HEAD | tr '\n' ' ')"
for f in "$SCR"/ho33/tests/hv_*.rs "$SCR"/ho33/tests/common/mod.rs "$SCR"/ho33/Cargo.toml; do
  b=$(basename "$f"); [ "$b" = mod.rs ] && b=common.rs; [ "$b" = Cargo.toml ] && b=Cargo.toml.txt
  if cmp -s "$f" "$WT/release/verification/4.1.6-r1-4/evidence/heldout-tests/$b"; then echo "unedited: $b"; else echo "DIFFERS: $b"; fi
done
cd "$SCR/ho33"
for t in hv_a_derivation hv_b_bullet7 hv_c_failclosed hv_d_sinks_and_preservation; do
  echo "=== cargo test --test $t"
  CARGO_TARGET_DIR="$SCR/target-ho33" AR0033_GOV_BIN="$WT/target/release/gov" AR0033_BASE_SRC="$SCR/base" \
    $STRIP "$HOME/.cargo/bin/cargo" test --test $t -- --test-threads=1 2>&1 | grep -E '^test |test result|panicked|FAILED|error(\[|:)'
done
