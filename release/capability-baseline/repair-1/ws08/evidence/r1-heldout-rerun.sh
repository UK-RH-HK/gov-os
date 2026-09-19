#!/usr/bin/env bash
# P2-AR-0020 (WS-8) — re-run EVERY prior R1 held-out suite UNEDITED against this worktree.
#
# Follows release/verification/4.1.6-r1-4/evidence/REPRODUCTION.md §5-§6: each suite is copied byte-identically
# (cmp-verified) into a scratch crate; only the crate location is arranged (symlinks <scratch>/wt/srr1-r1-verify{,-2,-3,-4}
# -> this worktree) so that no line of any suite is edited. Each test binary runs separately, single-threaded, with the
# nine refused-authority variables and GOV_MACHINE_STATE_DIR stripped.
#
# Usage: r1-heldout-rerun.sh <label>   (writes r1-heldout-<label>.out beside this script)
set -u
LABEL="${1:?label}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../.." && pwd)"
SCR="${P2AR0020_SCRATCH:?set P2AR0020_SCRATCH to a scratch directory}"
OUT="$HERE/r1-heldout-$LABEL.out"
V="$WT/release/verification"
export CARGO_BUILD_JOBS=2
CARGO="${CARGO:-$HOME/.cargo/bin/cargo}"
STRIP=(env -u GOV_BREAK_GLASS -u GOV_BREAKGLASS -u GOV_TRUST_OVERRIDE -u GOV_SKIP_VERIFY -u GOV_ALLOW_UNSIGNED
       -u GOV_RELEASE_AUTHORITY -u GOV_HUMAN_GATE_APPROVED -u GOV_FLOOR_OVERRIDE -u GOV_MINIMUM_SECURE_RELEASE
       -u GOV_MACHINE_STATE_DIR)
mkdir -p "$SCR/wt"
for s in srr1-r1-verify srr1-r1-verify-2 srr1-r1-verify-3 srr1-r1-verify-4; do ln -sfn "$WT" "$SCR/wt/$s"; done
rm -rf "$SCR/ho27" "$SCR/ho29" "$SCR/ho31" "$SCR/ho33"
mkdir -p "$SCR/ho27/tests/common" "$SCR/ho29/tests/common" "$SCR/ho31/tests/common" "$SCR/ho33/tests/common"
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
# AR-0033 base export (candidate 3 source, graded by hv_a with the candidate's signatures)
rm -rf "$SCR/base"; mkdir -p "$SCR/base"
git -C "$WT" archive 30aa98a10fd7f5ed85439b0d676761080519ceed runtime/src cli/src | tar -x -C "$SCR/base"
{
  echo "# P2-AR-0020 R1 held-out re-run, label=$LABEL"
  echo "# worktree HEAD: $(git -C "$WT" rev-parse HEAD)  dirty-files: $(git -C "$WT" status --porcelain | wc -l)"
  echo "# date: $(date -u +%FT%TZ)"
  echo "# byte-identity of copied suites (cmp):"
  for f in "$V"/4.1.6-r1/evidence/heldout-tests/heldout_srr*.rs; do cmp "$f" "$SCR/ho27/tests/$(basename "$f")" && echo "  identical ho27/$(basename "$f")"; done
  cmp "$V/4.1.6-r1/evidence/heldout-tests/forge.rs" "$SCR/ho27/tests/common/forge.rs" && echo "  identical ho27/common/forge.rs"
  for f in "$V"/4.1.6-r1-2/evidence/heldout-tests/ho_*.rs; do cmp "$f" "$SCR/ho29/tests/$(basename "$f")" && echo "  identical ho29/$(basename "$f")"; done
  cmp "$V/4.1.6-r1-2/evidence/heldout-tests/mint.rs" "$SCR/ho29/tests/common/mint.rs" && echo "  identical ho29/common/mint.rs"
  for f in "$V"/4.1.6-r1-3/evidence/heldout-tests/hx_*.rs; do cmp "$f" "$SCR/ho31/tests/$(basename "$f")" && echo "  identical ho31/$(basename "$f")"; done
  cmp "$V/4.1.6-r1-3/evidence/heldout-tests/bench.rs" "$SCR/ho31/tests/common/bench.rs" && echo "  identical ho31/common/bench.rs"
  for f in "$V"/4.1.6-r1-4/evidence/heldout-tests/hv_*.rs; do cmp "$f" "$SCR/ho33/tests/$(basename "$f")" && echo "  identical ho33/$(basename "$f")"; done
  cmp "$V/4.1.6-r1-4/evidence/heldout-tests/common.rs" "$SCR/ho33/tests/common/mod.rs" && echo "  identical ho33/common/mod.rs"
} > "$OUT" 2>&1
# the candidate `gov` (debug) for AR-0033's CLI-boundary tests
( cd "$WT" && "$CARGO" build --bin gov ) >> "$OUT" 2>&1
GOVBIN="$WT/target/debug/gov"
run_suite() {  # run_suite <crate-dir> <suite-label> <test names...>
  local crate="$1" suite="$2"; shift 2
  for t in "$@"; do
    echo "===== $suite :: $t =====" >> "$OUT"
    ( cd "$crate" && CARGO_TARGET_DIR="$SCR/target-ho" AR0033_GOV_BIN="$GOVBIN" AR0033_BASE_SRC="$SCR/base" \
        "${STRIP[@]}" "$CARGO" test --test "$t" -- --test-threads=1 2>&1 | grep -v '^warning\|^ *|\|^ *=\|^ *-->\|^$' ) >> "$OUT"
  done
}
run_suite "$SCR/ho27" AR-0027 heldout_srr heldout_srr2 heldout_srr3 heldout_srr4
run_suite "$SCR/ho29" AR-0029 ho_a_allowlist ho_b_coverage ho_c_deadlock ho_d_expiry ho_e_rootexpiry ho_f_preservation
run_suite "$SCR/ho31" AR-0031 hx_a_census hx_b_failopen hx_c_prior_evidence hx_d_acquisition_and_preservation
run_suite "$SCR/ho33" AR-0033 hv_a_derivation hv_b_bullet7 hv_c_failclosed hv_d_sinks_and_preservation
# summary
python3 - "$OUT" <<'PY' >> "$OUT"
import re, sys
txt = open(sys.argv[1]).read()
blocks = re.split(r"^===== (.+?) :: (.+?) =====$", txt, flags=re.M)
agg = {}
print("\n# SUMMARY (per test binary)")
for i in range(1, len(blocks), 3):
    suite, test, body = blocks[i], blocks[i+1], blocks[i+2]
    m = re.findall(r"test result: \w+\. (\d+) passed; (\d+) failed", body)
    fails = re.findall(r"^test (\S+) \.\.\. FAILED", body, flags=re.M)
    comp = "error[E" in body or "could not compile" in body
    p = sum(int(a) for a, _ in m); f = sum(int(b) for _, b in m)
    a = agg.setdefault(suite, [0, 0, [], []])
    a[0] += p; a[1] += f; a[2] += fails
    if comp and not m: a[3].append(test)
    print(f"{suite:8s} {test:40s} passed={p:3d} failed={f:3d} {'DOES_NOT_COMPILE' if comp and not m else ''} {fails}")
print("\n# SUMMARY (per suite)")
for s, (p, f, fl, nc) in agg.items():
    print(f"{s}: {p} passed / {f} failed; failing={sorted(fl)}; not-compiling={nc}")
PY
# SUPPLEMENTARY (not a suite, not edited): AR-0033's own independent Python derivation (release/verification/4.1.6-r1-4/
# evidence/derive.py), copied to scratch with only its hard-coded ROOT line pointed at this worktree, so the substantive
# half of hv_a::a1 (zero independently derived §6 violations) is measured even though a1's first assertions pin the
# product tree's size (84 files / 740 functions) and therefore fail on any candidate that adds a function.
{
  echo; echo "# SUPPLEMENTARY: release/verification/4.1.6-r1-4/evidence/derive.py against this worktree (ROOT line only substituted)"
  sed "s|^ROOT = .*|ROOT = \"$WT\"|" "$V/4.1.6-r1-4/evidence/derive.py" > "$SCR/derive_ws08.py"
  if diff <(sed 1,2d "$V/4.1.6-r1-4/evidence/derive.py") <(sed 1,2d "$SCR/derive_ws08.py") >/dev/null; then echo "# derive.py copy differs from the evidence file only in its ROOT line"; fi
  ( cd "$SCR" && python3 derive_ws08.py )
} >> "$OUT" 2>&1
tail -8 "$OUT"
