#!/usr/bin/env bash
# P2-AR-0035 (WS-4, repair-1 round 3) — measure the END STATE the round-3 coordination on CIT sealing aims at, in a
# private scratch clone (never in this worktree; a clone, not an export, because two certification tests rebuild
# released versions from their commits and need the history): this branch's commit, plus
#   (1) the gates.rs re-seal offered to WS-3 as IP-R3-WS04-01 (evidence/IP-R3-WS04-01.gates-reseal.patch), and
#   (2) `"cit"` added to `t2::SEALED_RECORD_TYPES` (WS-5 IP-R3-2, WS-3's file),
# then run `cargo test --lib`, the whole certification suite and the ignored IP-R3-WS04-01 test. Evidence only: it
# shows the integrator that the two WS-3 changes complete the sealing without regressing any suite.
#
# Usage: P2AR0035_SCRATCH=<dir> run-endstate.sh <commit> prepare|cert
#   prepare  clone (a local branch in the scratch clone only) + patch + build + lib tests;   cert  the certification suite (split so each step stays short)
# Output: evidence/observe/endstate-<commit>.out (appended by each step)
set -u
COMMIT="${1:?commit}"; STEP="${2:?prepare|cert}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(git -C "$HERE" rev-parse --show-toplevel)"
SCR="${P2AR0035_SCRATCH:?set P2AR0035_SCRATCH}/endstate-clone-$COMMIT"
OUT="$HERE/../observe/endstate-$COMMIT.out"
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=2 CARGO_TARGET_DIR="$SCR/target"
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
case "$STEP" in
  prepare)
    mkdir -p "$SCR" "$HERE/../observe"
    git clone -q --no-checkout "$WT" "$SCR/tree" && git -C "$SCR/tree" checkout -q -b "p2ar0035-endstate-probe" "$COMMIT"
    {
      echo "# P2-AR-0035 end-state measurement: commit=$(git -C "$WT" rev-parse "$COMMIT") + IP-R3-WS04-01 + cit in SEALED_RECORD_TYPES"
      echo "# scratch $SCR"
      echo "# date $(date -u +%FT%TZ)"
    } > "$OUT"
    ( cd "$SCR/tree" && patch -p1 < "$HERE/../IP-R3-WS04-01.gates-reseal.patch" ) >> "$OUT" 2>&1 || { echo "[patch failed]" >> "$OUT"; exit 3; }
    sed -i 's/^pub const SEALED_RECORD_TYPES: &\[&str\] = &\["human-gate"\];/pub const SEALED_RECORD_TYPES: \&[\&str] = \&["human-gate", "cit"];/' "$SCR/tree/runtime/src/t2.rs"
    ( diff -u <(git -C "$WT" show "$COMMIT:runtime/src/t2.rs") "$SCR/tree/runtime/src/t2.rs" ) >> "$OUT"
    ( cd "$SCR/tree" && cargo build --tests -q 2>&1 | tail -20 ) >> "$OUT"
    echo "## cargo test --lib" >> "$OUT"
    ( cd "$SCR/tree" && cargo test -q --lib 2>&1 | grep -E "test result|FAILED|panicked" ) >> "$OUT"
    ;;
  cert)
    echo "## cargo test --test certification -- --include-ignored (the IP-R3-WS04-01 test included)" >> "$OUT"
    ( cd "$SCR/tree" && timeout 3000 cargo test -q --test certification -- --include-ignored 2>&1 | grep -E "test result|FAILED|panicked|^failures|^    " ) >> "$OUT"
    echo "[endstate cert exit=$?]" >> "$OUT"
    ;;
esac
tail -5 "$OUT"
