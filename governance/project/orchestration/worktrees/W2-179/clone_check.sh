#!/usr/bin/env bash
# W2-179 S1/F1: the revised F3 case in a clone under ~/gov-os-runs/W2-179/ (the nightly's place) and in one elsewhere;
# in each, the case as merged (expect pass), with a planted runs-folder entry outside the repository (expect FAIL),
# and with a planted entry of the repository's own file (expect pass). Synthetic log entries only: nothing is opened.
set -u
SRC=/home/usain/gov-os-worktrees/W2-179
HS=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
CASE=tests/acceptance/W2-170/test_w2_170_s4_map.py
K=test_f3_a_run_s_file_access_log_shows_no_open_of_the_true_sets_root_or_runs_folders
OUT=/home/usain/gov-os-worktrees/W2-179/.gov-runtime/scratch/lead/log/clone-check.txt
: > "$OUT"
run_case() {  # $1 clone, $2 label, $3 expected (pass|fail)
  local c=$1
  ( cd "$c" && env HOME="$c/.gov-runtime/scratch/empty-home" PYTHONUSERBASE=/home/usain/.local TMPDIR=/tmp \
      PYTHONPATH="$c/src" bash "$HS" python3 -m pytest "$CASE" -q -p no:cacheprovider \
      -o tmp_path_retention_policy=failed -k "$K" > "$c.$2.txt" 2>&1 )
  local rc=$? got=pass
  [ $rc = 0 ] || got=fail
  local verdict=OK; [ "$got" = "$3" ] || verdict=MISMATCH
  echo "$verdict | $c | $2 | expected $3 | got $got (rc $rc) | $(tail -1 "$c.$2.txt")" >> "$OUT"
  grep -m1 "AssertionError" "$c.$2.txt" | cut -c1-300 >> "$OUT"
}
for c in /home/usain/gov-os-runs/W2-179/clone /tmp/w2-179-else/clone; do
  rm -rf "$c"; mkdir -p "$(dirname "$c")"
  git clone -q --no-hardlinks --branch w2/W2-179 "$SRC" "$c" || { echo "clone failed $c" >> "$OUT"; continue; }
  echo "clone $c at $(git -C "$c" rev-parse HEAD)" >> "$OUT"
  mkdir -p "$c/.gov-runtime/scratch/empty-home"
  run_case "$c" merged pass
  cp "$c/$CASE" "$c/$CASE.orig"
  sed -i 's#^    every = entries + entries2 + entries3$#    every = entries + entries2 + entries3 + [("open", "/home/usain/gov-os-runs/W2-179/planted-outside/x.txt")]#' "$c/$CASE"
  grep -q planted-outside "$c/$CASE" || echo "sed 1 did not apply" >> "$OUT"
  run_case "$c" planted-outside fail
  cp "$c/$CASE.orig" "$c/$CASE"
  sed -i "s#^    every = entries + entries2 + entries3\$#    every = entries + entries2 + entries3 + [(\"open\", \"$c/src/gov/memaudit/__init__.py\")]#" "$c/$CASE"
  grep -q "memaudit/__init__.py\")\]" "$c/$CASE" || echo "sed 2 did not apply" >> "$OUT"
  run_case "$c" planted-own pass
  cp "$c/$CASE.orig" "$c/$CASE"
done
# the original (pre-revision) filter in the runs-folder clone: expect FAIL (the nightly's red reproduced)
c=/home/usain/gov-os-runs/W2-179/clone
git -C "$c" show 3eeb5cb2e:"$CASE" > "$c/$CASE"
run_case "$c" pre-revision fail
cat "$OUT"
