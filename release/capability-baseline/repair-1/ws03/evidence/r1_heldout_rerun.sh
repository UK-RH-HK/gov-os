#!/usr/bin/env bash
# P2-AR-0016 (WS-3) — AC-14 preservation evidence: re-run EVERY prior R1 held-out suite UNEDITED against a source
# tree, following each suite's REPRODUCTION.md layout (release/verification/4.1.6-r1*/evidence/).
#
#   TARGET_WT  the source tree under test (this worktree, or an export of the base commit for the baseline run)
#   GOV_BIN    the `gov` binary built from TARGET_WT (AR0033_GOV_BIN; only the r1-4 suite drives the binary)
#   SCR        a scratch directory (created)
#   BASE_SRC   export of 30aa98a runtime/src + cli/src (AR0033_BASE_SRC, used by hv_a/hv_c as REPRODUCTION.md says)
#
# The suites are copied verbatim; `cmp` against the committed files is printed for every copied file.
set -u
: "${TARGET_WT:?}" "${GOV_BIN:?}" "${SCR:?}" "${BASE_SRC:?}"
EVID="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$EVID/../../../../.." && pwd)"
V="$REPO/release/verification"
STRIP='env -u GOV_BREAK_GLASS -u GOV_BREAKGLASS -u GOV_TRUST_OVERRIDE -u GOV_SKIP_VERIFY -u GOV_ALLOW_UNSIGNED -u GOV_RELEASE_AUTHORITY -u GOV_HUMAN_GATE_APPROVED -u GOV_FLOOR_OVERRIDE -u GOV_MINIMUM_SECURE_RELEASE -u GOV_MACHINE_STATE_DIR -u GOV_ROLE -u GOV_SESSION -u GOV_CANONICAL_ROOT'
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS="${CARGO_BUILD_JOBS:-2}"
mkdir -p "$SCR/wt"
for n in srr1-r1-verify srr1-r1-verify-2 srr1-r1-verify-3 srr1-r1-verify-4; do ln -sfn "$TARGET_WT" "$SCR/wt/$n"; done
echo "TARGET_WT=$TARGET_WT"
echo "GOV_BIN=$GOV_BIN sha256=$(sha256sum "$GOV_BIN" | cut -c1-16)"

copy() { # copy <src> <dst>, then prove it is byte-identical
  mkdir -p "$(dirname "$2")"; cp "$1" "$2"
  if cmp -s "$1" "$2"; then echo "unedited: ${1#$REPO/}"; else echo "DIFFERS: $1"; fi
}
run() { # run <crate> <tests...>
  local crate="$1"; shift
  for t in "$@"; do
    echo "=== $(basename "$crate") :: $t"
    ( cd "$crate" && CARGO_TARGET_DIR="$SCR/target-$(basename "$crate")" AR0033_GOV_BIN="$GOV_BIN" AR0033_BASE_SRC="$BASE_SRC" \
      $STRIP cargo test --test "$t" -- --test-threads=1 2>&1 | grep -E '^test |test result|panicked at|^error' )
  done
}

# AR-0027 (4.1.6-r1)
C="$SCR/ho27"; S="$V/4.1.6-r1/evidence/heldout-tests"
copy "$S/Cargo.toml.txt" "$C/Cargo.toml"; copy "$S/forge.rs" "$C/tests/common/forge.rs"
for f in "$S"/heldout_srr*.rs; do copy "$f" "$C/tests/$(basename "$f")"; done
run "$C" heldout_srr heldout_srr2 heldout_srr3 heldout_srr4

# AR-0029 (4.1.6-r1-2)
C="$SCR/ho29"; S="$V/4.1.6-r1-2/evidence/heldout-tests"
copy "$S/Cargo.toml.txt" "$C/Cargo.toml"; copy "$S/mint.rs" "$C/tests/common/mint.rs"
for f in "$S"/ho_*.rs; do copy "$f" "$C/tests/$(basename "$f")"; done
printf '#![allow(dead_code, unused_imports)]\npub mod mint;\n' > "$C/tests/common/mod.rs"
run "$C" ho_a_allowlist ho_b_coverage ho_c_deadlock ho_d_expiry ho_e_rootexpiry ho_f_preservation

# AR-0031 (4.1.6-r1-3)
C="$SCR/ho31"; S="$V/4.1.6-r1-3/evidence/heldout-tests"
copy "$S/Cargo.toml.txt" "$C/Cargo.toml"; copy "$S/bench.rs" "$C/tests/common/bench.rs"
for f in "$S"/hx_*.rs; do copy "$f" "$C/tests/$(basename "$f")"; done
printf '#![allow(dead_code, unused_imports)]\npub mod bench;\n' > "$C/tests/common/mod.rs"
run "$C" hx_a_census hx_b_failopen hx_c_prior_evidence hx_d_acquisition_and_preservation

# AR-0033 (4.1.6-r1-4)
C="$SCR/ho33"; S="$V/4.1.6-r1-4/evidence/heldout-tests"
copy "$S/Cargo.toml.txt" "$C/Cargo.toml"; copy "$S/common.rs" "$C/tests/common/mod.rs"
for f in "$S"/hv_*.rs; do copy "$f" "$C/tests/$(basename "$f")"; done
run "$C" hv_a_derivation hv_b_bullet7 hv_c_failclosed hv_d_sinks_and_preservation
