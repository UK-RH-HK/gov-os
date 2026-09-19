#!/usr/bin/env bash
# P2-AR-0042 (BC-P2-02) — MUTATION evidence: for a sample of test owners (gates E, P, Q, V, W), break the capability in
# the product source and run the owner: it must fail on the mutant and pass on the unmutated tree.
#
# Builder evidence (Contract v3 O3), labelled MUTATION. Runs in a private copy of this commit's tree
# (`git archive HEAD` under target/P2-AR-0042/mutants/tree, its own CARGO_TARGET_DIR); the worktree is never mutated.
# Each mutation is one exact string replacement, applied, run and reverted; the unmutated run of the same owner is the
# negative control. Usage: product-mutations.sh <mutation-tree> <target-dir> <out-file>
set -u
TREE="$1"; TGT="$2"; OUT="$3"
export CARGO_BUILD_JOBS=2
CARGO="${CARGO:-$HOME/.cargo/bin/cargo}"
: > "$OUT"
run_owner() {  # run_owner <harness> <test path> → prints PASSED/FAILED and the result line
  local harness="$1" t="$2" log
  if [ "$harness" = lib ]; then
    log=$(cd "$TREE" && CARGO_TARGET_DIR="$TGT" "$CARGO" test --lib -- --exact "$t" 2>&1)
  else
    log=$(cd "$TREE" && CARGO_TARGET_DIR="$TGT" "$CARGO" test --test certification -- --exact "$t" 2>&1)
  fi
  local line; line=$(printf '%s\n' "$log" | grep -E '^test result:' | tail -1)
  if printf '%s\n' "$log" | grep -qE "^test $t \.\.\. ok"; then echo "PASSED | $line"; else
    echo "FAILED | $line | $(printf '%s\n' "$log" | grep -E "panicked at|assertion|left:|right:" | head -3 | tr '\n' ' ' | cut -c1-400)"; fi
}
mutate() {  # mutate <gate> <capability> <harness> <owner test> <file> <python-literal old> <python-literal new>
  local gate="$1" cap="$2" harness="$3" t="$4" file="$5" old="$6" new="$7"
  echo "===== MUTATION $gate $cap owner=test:$harness:$t file=$file" >> "$OUT"
  echo "control (unmutated): $(run_owner "$harness" "$t")" >> "$OUT"
  cp "$TREE/$file" "$TREE/$file.orig-p2ar0042"
  python3 - "$TREE/$file" "$old" "$new" <<'PY' >> "$OUT"
import sys
p, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(p).read()
n = s.count(old)
assert n == 1, f"mutation anchor found {n} times"
open(p, "w").write(s.replace(old, new))
print(f"applied: {old!r} -> {new!r}")
PY
  echo "mutant: $(run_owner "$harness" "$t")" >> "$OUT"
  mv "$TREE/$file.orig-p2ar0042" "$TREE/$file"
  echo "reverted: $(cmp -s "$TREE/$file" <(git -C "$(dirname "$0")" show HEAD:"$file" 2>/dev/null || cat "$TREE/$file") && echo identical-to-HEAD || echo restored-from-copy)" >> "$OUT"
}
echo "# tree $TREE (git archive of $(git -C "$(dirname "$0")" rev-parse HEAD)); target $TGT; $(date -u +%FT%TZ)" >> "$OUT"
mutate E E1 lib authority::tests::undeclared_is_level_zero_and_never_orchestrator runtime/src/authority.rs \
  $'    if role == UNDECLARED_ROLE {\n        return Ok(0);\n    }' $'    if role == UNDECLARED_ROLE {\n        return Ok(4);\n    }'
mutate V V1 lib qualification_oracle::tests::a_record_missing_any_v1_v4_field_is_rejected framework/qualification-oracle/qualification-oracle.schema.json \
  '"expected_detection", "expected_severity", ' '"expected_detection", '
mutate W W3 lib context::manifest::tests::absent_wrong_type_superseded_and_non_authoritative_inputs_block runtime/src/context/manifest.rs \
  'if !allowed_status.iter().any(|s| s == "SUPERSEDED") {' 'if false && !allowed_status.iter().any(|s| s == "SUPERSEDED") {'
mutate P P1 certification greenfield::greenfield_end_to_end runtime/src/observability.rs \
  $'    let path = path(p);\n    if !path.exists() {' $'    let path = path(p);\n    if true || !path.exists() {'
mutate Q Q4 certification upstream::export_gate_fails_closed_on_content_whatever_the_name runtime/src/upstream.rs \
  'if let Some(m) = blob_rx.find(text) {' 'if let Some(m) = blob_rx.find(text).filter(|_| false) {'
echo "# done $(date -u +%FT%TZ)" >> "$OUT"
grep -E '^(=====|control|mutant)' "$OUT"
