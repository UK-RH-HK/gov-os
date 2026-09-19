#!/usr/bin/env bash
# P2-AR-0017 (WS-4 repair builder): run every prior R1 held-out suite UNEDITED against a source tree, following
# release/verification/4.1.6-r1-4/evidence/REPRODUCTION.md §4-§6 (suites copied byte-identically; only the
# Cargo.toml dependency path is satisfied by a symlink named as each suite expects).
#
# usage: run-r1-heldout.sh <tree> <scratch-dir> <out-file> [phase ...]
#   <tree>         the product source tree under test (the repair worktree, or a clone of the base commit)
#   <scratch-dir>  a scratch directory (crates, symlinks, target dirs); reused across phases
#   <out-file>     where the combined output is appended
#   phase          any of: gov ho27 ho29 ho31 ho33 summary (default: all, in order). Phases exist only so each
#                  fits one foreground invocation; the suites and the order are REPRODUCTION.md's.
set -u
tree="$(cd "${1:?tree}" && pwd)"
scr="${2:?scratch}"
out="${3:?out-file}"
shift 3
phases="${*:-gov ho27 ho29 ho31 ho33 summary}"
want() { case " $phases " in *" $1 "*) return 0;; *) return 1;; esac; }
here="$(cd "$(dirname "$0")" && pwd)"
wt="$(cd "$here/../../../../.." && pwd)"
ver="$wt/release/verification"
mkdir -p "$scr/wt" "$scr/base30aa98a"
scr="$(cd "$scr" && pwd)"
for n in srr1-r1-verify srr1-r1-verify-2 srr1-r1-verify-3 srr1-r1-verify-4; do ln -sfn "$tree" "$scr/wt/$n"; done
export CARGO_BUILD_JOBS="${CARGO_BUILD_JOBS:-2}"
STRIP=(env -u GOV_BREAK_GLASS -u GOV_BREAKGLASS -u GOV_TRUST_OVERRIDE -u GOV_SKIP_VERIFY -u GOV_ALLOW_UNSIGNED
       -u GOV_RELEASE_AUTHORITY -u GOV_HUMAN_GATE_APPROVED -u GOV_FLOOR_OVERRIDE -u GOV_MINIMUM_SECURE_RELEASE
       -u GOV_MACHINE_STATE_DIR)
cargo="$HOME/.cargo/bin/cargo"
# AR-0033's derivation attack grades the pre-repair base (30aa98a) with the candidate's signatures
gov_bin="$scr/target-gov/debug/gov"
if want gov; then
  git -C "$wt" archive 30aa98a10fd7f5ed85439b0d676761080519ceed runtime/src cli/src | tar -x -C "$scr/base30aa98a"
  : > "$out"
  echo "tree under test: $tree" | tee -a "$out"
  echo "tree HEAD: $(git -C "$tree" rev-parse HEAD 2>/dev/null || echo 'n/a') dirty-product-files=$(git -C "$tree" status --porcelain -- runtime cli framework 2>/dev/null | wc -l)" | tee -a "$out"
  # the candidate gov binary (AR-0033's CLI-boundary tests drive the real binary)
  ( cd "$tree" && CARGO_TARGET_DIR="$scr/target-gov" "$cargo" build --bin gov ) >> "$out" 2>&1
  echo "gov binary: $gov_bin ($(test -x "$gov_bin" && echo present || echo MISSING))" | tee -a "$out"
fi

setup() { # <crate> <suite dir> <helper handling>
  local c="$scr/$1" s="$ver/$2/evidence/heldout-tests"
  mkdir -p "$c/tests/common"
  cp "$s/Cargo.toml.txt" "$c/Cargo.toml"
  cmp -s "$s/Cargo.toml.txt" "$c/Cargo.toml" || echo "COPY MISMATCH $s/Cargo.toml.txt" | tee -a "$out"
}
# AR-0027 (4.1.6-r1): forge.rs included by #[path = "common/forge.rs"]
setup ho27 4.1.6-r1
cp "$ver/4.1.6-r1/evidence/heldout-tests/forge.rs" "$scr/ho27/tests/common/forge.rs"
cp "$ver/4.1.6-r1/evidence/heldout-tests/"heldout_srr*.rs "$scr/ho27/tests/"
# AR-0029 (4.1.6-r1-2): mod common; pub mod mint;
setup ho29 4.1.6-r1-2
cp "$ver/4.1.6-r1-2/evidence/heldout-tests/mint.rs" "$scr/ho29/tests/common/mint.rs"
printf 'pub mod mint;\n' > "$scr/ho29/tests/common/mod.rs"
cp "$ver/4.1.6-r1-2/evidence/heldout-tests/"ho_*.rs "$scr/ho29/tests/"
# AR-0031 (4.1.6-r1-3): mod common; pub mod bench;
setup ho31 4.1.6-r1-3
cp "$ver/4.1.6-r1-3/evidence/heldout-tests/bench.rs" "$scr/ho31/tests/common/bench.rs"
printf 'pub mod bench;\n' > "$scr/ho31/tests/common/mod.rs"
cp "$ver/4.1.6-r1-3/evidence/heldout-tests/"hx_*.rs "$scr/ho31/tests/"
# AR-0033 (4.1.6-r1-4): common.rs is tests/common/mod.rs
setup ho33 4.1.6-r1-4
cp "$ver/4.1.6-r1-4/evidence/heldout-tests/common.rs" "$scr/ho33/tests/common/mod.rs"
cp "$ver/4.1.6-r1-4/evidence/heldout-tests/"hv_*.rs "$scr/ho33/tests/"

for c in ho27 ho29 ho31 ho33; do
  want "$c" || continue
  for t in "$scr/$c"/tests/*.rs; do
    b="$(basename "$t" .rs)"
    echo "===== $c/$b =====" | tee -a "$out"
    ( cd "$scr/$c" && CARGO_TARGET_DIR="$scr/target-$c" AR0033_GOV_BIN="$gov_bin" AR0033_BASE_SRC="$scr/base30aa98a" \
        "${STRIP[@]}" "$cargo" test --test "$b" -- --test-threads=1 ) >> "$out" 2>&1
    echo "exit=$?" >> "$out"
    grep -E "^test result|could not compile|^error\[" "$out" | tail -1
  done
done
want summary || exit 0
echo "==== SUMMARY (per test binary) ====" | tee -a "$out"
awk '/^===== /{name=$2} /^test result/{print name": "$0} /could not compile/{print name": DOES NOT COMPILE"}' "$out" | tee -a "$out"
echo "==== FAILING TESTS ====" | tee -a "$out"
grep -E "^test .* FAILED$" "$out" | sort -u | tee -a "$out"
