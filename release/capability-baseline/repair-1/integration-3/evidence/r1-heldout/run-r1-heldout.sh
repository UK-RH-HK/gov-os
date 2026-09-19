#!/usr/bin/env bash
# P2-AR-0041 (round-3 integration builder, repair iteration 1) — re-run EVERY prior R1 held-out suite UNEDITED against THIS worktree.
#
# Procedure: release/verification/4.1.6-r1-4/evidence/REPRODUCTION.md §3-§6, as in the integration builder's runner
# (repair-1/integration/evidence/r1-heldout/run-r1-heldout.sh), with one change required by P2-HO-0020 item 7:
# every path is PRIVATE to this run. The scratch root defaults to a directory named with this run id (P2-AR-0041), the
# symlinks <scratch>/wt/srr1-r1-verify{,-2,-3,-4} point at this worktree only, and the header records the worktree
# path, HEAD and the census the AR-0033 walk reports, so the run can be matched to this tree.
#
# Each suite is copied byte-identically (cmp-verified below) into a scratch crate; only the crate LOCATION is
# arranged, so no line of any suite is edited. Each test binary runs separately, single-threaded, with the nine
# refused-authority variables and GOV_MACHINE_STATE_DIR stripped.
#
# Supplementary, clearly separated from the suites:
#   (S1) AR-0033 hv_a::a1 with ONLY its two scale assertions (84 files / 740 functions) replaced by printed values —
#        the labelled derived copy hv_a_derivation.a1-unpinned.P2-AR-0041.rs.txt beside this script, run from a
#        separate scratch crate; the held-out suite itself is never edited.
#   (S2) AR-0033's own independent Python derivation (evidence/derive.py) with only its ROOT line pointed here.
#
# Usage: run-r1-heldout.sh <label>   (writes r1-heldout-<label>.out beside this script)
set -u
LABEL="${1:?label}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../../.." && pwd)"
SCR="${P2AR0041_SCRATCH:-/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/1b6c780e-2b37-439f-a969-a8d96b7ad35e/scratchpad/P2-AR-0041/r1-P2-AR-0041-private}"
OUT="$HERE/r1-heldout-$LABEL.out"
V="$WT/release/verification"
export CARGO_BUILD_JOBS=2
CARGO="${CARGO:-$HOME/.cargo/bin/cargo}"
STRIP=(env -u GOV_BREAK_GLASS -u GOV_BREAKGLASS -u GOV_TRUST_OVERRIDE -u GOV_SKIP_VERIFY -u GOV_ALLOW_UNSIGNED
       -u GOV_RELEASE_AUTHORITY -u GOV_HUMAN_GATE_APPROVED -u GOV_FLOOR_OVERRIDE -u GOV_MINIMUM_SECURE_RELEASE
       -u GOV_MACHINE_STATE_DIR)
mkdir -p "$SCR/wt"
for s in srr1-r1-verify srr1-r1-verify-2 srr1-r1-verify-3 srr1-r1-verify-4; do ln -sfn "$WT" "$SCR/wt/$s"; done
for c in ho27 ho29 ho31 ho33 ho33u base; do [ -d "$SCR/$c" ] && mv "$SCR/$c" "$SCR/.old-$c-$$-$(date +%s)"; done
mkdir -p "$SCR/ho27/tests/common" "$SCR/ho29/tests/common" "$SCR/ho31/tests/common" "$SCR/ho33/tests/common" "$SCR/ho33u/tests/common"
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
# (S1) the labelled derived copy of hv_a (same crate manifest and common module, byte-identical)
cp "$V/4.1.6-r1-4/evidence/heldout-tests/Cargo.toml.txt" "$SCR/ho33u/Cargo.toml"
cp "$V/4.1.6-r1-4/evidence/heldout-tests/common.rs" "$SCR/ho33u/tests/common/mod.rs"
cp "$HERE/hv_a_derivation.a1-unpinned.P2-AR-0041.rs.txt" "$SCR/ho33u/tests/hv_a_derivation_a1_unpinned.rs"
# AR-0033 base export (candidate 3 source, graded by hv_a with the candidate's signatures) — REPRODUCTION.md §3
mkdir -p "$SCR/base"
git -C "$WT" archive 30aa98a10fd7f5ed85439b0d676761080519ceed runtime/src cli/src | tar -x -C "$SCR/base"
{
  echo "# P2-AR-0041 R1 held-out re-run, label=$LABEL"
  echo "# worktree: $WT"
  echo "# worktree HEAD: $(git -C "$WT" rev-parse HEAD)"
  echo "# product files differing from HEAD (runtime/ cli/ framework/ migrations/ tools/ Cargo.*): $(git -C "$WT" status --porcelain -- runtime cli framework migrations tools Cargo.toml Cargo.lock | wc -l)"
  echo "# private scratch root: $SCR"
  for s in srr1-r1-verify srr1-r1-verify-2 srr1-r1-verify-3 srr1-r1-verify-4; do echo "#   $SCR/wt/$s -> $(readlink "$SCR/wt/$s")"; done
  echo "# tree census (.rs under runtime/src + cli/src): $(find "$WT/runtime/src" "$WT/cli/src" -name '*.rs' | wc -l) files"
  echo "# date: $(date -u +%FT%TZ)"
  echo "# byte-identity of copied suites (cmp):"
  for f in "$V"/4.1.6-r1/evidence/heldout-tests/heldout_srr*.rs; do cmp "$f" "$SCR/ho27/tests/$(basename "$f")" && echo "  identical ho27/$(basename "$f")"; done
  cmp "$V/4.1.6-r1/evidence/heldout-tests/forge.rs" "$SCR/ho27/tests/common/forge.rs" && echo "  identical ho27/common/forge.rs"
  cmp "$V/4.1.6-r1/evidence/heldout-tests/Cargo.toml.txt" "$SCR/ho27/Cargo.toml" && echo "  identical ho27/Cargo.toml"
  for f in "$V"/4.1.6-r1-2/evidence/heldout-tests/ho_*.rs; do cmp "$f" "$SCR/ho29/tests/$(basename "$f")" && echo "  identical ho29/$(basename "$f")"; done
  cmp "$V/4.1.6-r1-2/evidence/heldout-tests/mint.rs" "$SCR/ho29/tests/common/mint.rs" && echo "  identical ho29/common/mint.rs"
  cmp "$V/4.1.6-r1-2/evidence/heldout-tests/Cargo.toml.txt" "$SCR/ho29/Cargo.toml" && echo "  identical ho29/Cargo.toml"
  for f in "$V"/4.1.6-r1-3/evidence/heldout-tests/hx_*.rs; do cmp "$f" "$SCR/ho31/tests/$(basename "$f")" && echo "  identical ho31/$(basename "$f")"; done
  cmp "$V/4.1.6-r1-3/evidence/heldout-tests/bench.rs" "$SCR/ho31/tests/common/bench.rs" && echo "  identical ho31/common/bench.rs"
  cmp "$V/4.1.6-r1-3/evidence/heldout-tests/Cargo.toml.txt" "$SCR/ho31/Cargo.toml" && echo "  identical ho31/Cargo.toml"
  for f in "$V"/4.1.6-r1-4/evidence/heldout-tests/hv_*.rs; do cmp "$f" "$SCR/ho33/tests/$(basename "$f")" && echo "  identical ho33/$(basename "$f")"; done
  cmp "$V/4.1.6-r1-4/evidence/heldout-tests/common.rs" "$SCR/ho33/tests/common/mod.rs" && echo "  identical ho33/common/mod.rs"
  cmp "$V/4.1.6-r1-4/evidence/heldout-tests/Cargo.toml.txt" "$SCR/ho33/Cargo.toml" && echo "  identical ho33/Cargo.toml"
  echo "# (S1) derived copy vs the held-out hv_a_derivation.rs (the ONLY difference must be the two scale assertions):"
  diff "$V/4.1.6-r1-4/evidence/heldout-tests/hv_a_derivation.rs" "$SCR/ho33u/tests/hv_a_derivation_a1_unpinned.rs"
} > "$OUT" 2>&1
# the candidate `gov` (debug) for AR-0033's CLI-boundary tests — REPRODUCTION.md §4 — built from THIS worktree
( cd "$WT" && "$CARGO" build --bin gov 2>&1 | tail -1 ) >> "$OUT" 2>&1
GOVBIN="$WT/target/debug/gov"
echo "# candidate gov: $GOVBIN sha256 $(sha256sum "$GOVBIN" | cut -c1-64)" >> "$OUT"
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
# summary of the four suites
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
cen = re.findall(r"independent walk: (\d+) files, (\d+) functions", txt)
if cen:
    print(f"\n# CENSUS reported by AR-0033 hv_a::a1 (independent walk of THIS worktree): {cen[0][0]} files, {cen[0][1]} functions")
PY
# (S1) supplementary: the labelled unpinned copy of hv_a::a1 only
{
  echo; echo "===== SUPPLEMENTARY (S1) :: hv_a_derivation_a1_unpinned (derived copy P2-AR-0041 (byte-identical to P2-AR-0032's); scale pins printed, not asserted) ====="
  ( cd "$SCR/ho33u" && CARGO_TARGET_DIR="$SCR/target-ho" AR0033_GOV_BIN="$GOVBIN" AR0033_BASE_SRC="$SCR/base" \
      "${STRIP[@]}" "$CARGO" test --test hv_a_derivation_a1_unpinned -- --test-threads=1 --nocapture a1_ 2>&1 \
      | grep -v '^warning\|^ *|\|^ *=\|^ *-->\|^$\|Compiling\|Locking\|Adding\|Updating' )
} >> "$OUT" 2>&1
# (S2) supplementary: AR-0033's own independent Python derivation, ROOT line only substituted
{
  echo; echo "===== SUPPLEMENTARY (S2) :: release/verification/4.1.6-r1-4/evidence/derive.py (ROOT line only substituted) ====="
  sed "s|^ROOT = .*|ROOT = \"$WT\"|" "$V/4.1.6-r1-4/evidence/derive.py" > "$SCR/derive_p2ar0041.py"
  echo "# diff of the copy against the evidence file:"; diff "$V/4.1.6-r1-4/evidence/derive.py" "$SCR/derive_p2ar0041.py"
  ( cd "$SCR" && python3 derive_p2ar0041.py )
} >> "$OUT" 2>&1
grep -A6 '^# SUMMARY (per suite)' "$OUT"; grep '^# CENSUS' "$OUT"
