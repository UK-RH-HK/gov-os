#!/usr/bin/env bash
# Dry run of rel_checks.sh's FIX-4 and FIX-3 comparisons (review F1; review r2 F7) on kept outputs, without re-running
# the suites: the blocks are cut from rel_checks.sh as it stands (by their marker lines), the suites' pytest calls left
# out, and run against copies of run-f7's outputs, unchanged (positive) and with one planted change each (negatives).
#     bash checks_dry.sh <rel_checks.sh> <run-f7's checks folder> <work dir>
set -uo pipefail
CH=$1; SRC=$2; D=$3
rm -rf "$D"; mkdir -p "$D"
BLK=$D/block.sh
{ sed -n '/^FIX4_ACCEPT=/,/^ok "test_guard_fix_4\.py/p' "$CH" | grep -v 'heavy_slot.sh' ; sed -n '/^# Under either pin the run must end/,/^ok "test_guard_fix_3\.py/p' "$CH"; } > "$BLK"
echo "== dry run of the FIX-4 and FIX-3 comparisons, $(date '+%F %T')"
echo "rel_checks.sh sha256 $(sha256sum < "$CH" | cut -c1-12); the block cut from it: $(wc -l < "$BLK") lines; the inputs: $SRC"
cat > "$D/run.sh" <<'EOF'
set -uo pipefail
S=$1
fail() { echo "CHECK FAILED: $1"; exit 1; }
ok() { echo "ok   $1"; }
source "$2"
EOF
mk() { rm -rf "$D/$1"; mkdir -p "$D/$1"; cp "$SRC"/{fix4.txt,fix3-new.txt,fix3-old.txt,fix3-new.failed,fix3-old.failed} "$D/$1/"; }
last_to() { local f=$1 new=$2; { sed '$d' "$f"; echo "$new"; } > "$f.x" && mv "$f.x" "$f"; }
before_last() { local f=$1 line=$2; { sed '$d' "$f"; echo "$line"; tail -1 "$f"; } > "$f.x" && mv "$f.x" "$f"; }
case_run() { echo "-- $1 (expect: $2)"; bash "$D/run.sh" "$D/$3" "$BLK"; echo "   exit $?"; }

mk pos
case_run "positive: run-f7's outputs unchanged" "two ok lines, the differing cases named" pos

mk n1
before_last "$D/n1/fix4.txt" "E       AssertionError: rule 5: a reviewer's record: want allow, got deny (planted)"
before_last "$D/n1/fix4.txt" "FAILED .gov-runtime/scratch/orchestrator/drafts/act-guard-fix-4/test_guard_fix_4.py::test_rules_1_and_5_judge_what_resolves[rule 5: a reviewer's record] - AssertionError"
last_to "$D/n1/fix4.txt" "3 failed, 464 passed in 9.0s"
case_run "FIX-4: an unnamed false refusal of ordinary work" "CHECK FAILED, not a named case" n1

mk n2
last_to "$D/n2/fix4.txt" "2 failed, 464 passed, 1 error in 9.0s"
case_run "FIX-4: a pytest error" "CHECK FAILED" n2

mk n3
echo 'FAILED test_guard_fix_3.py::test_case[fix3 plain echo to a reviewer record]' >> "$D/n3/fix3-new.failed"; sort -o "$D/n3/fix3-new.failed" "$D/n3/fix3-new.failed"
before_last "$D/n3/fix3-new.txt" "E   AssertionError: fix3 plain echo to a reviewer record: want allow, got deny"
case_run "FIX-3: an unnamed case failing only under the new pin, as a refusal" "CHECK FAILED, not a named case" n3

mk n4
sed -i 's/fix3 unterminated heredoc naming acceptance judged as before: want deny, got allow/fix3 unterminated heredoc naming acceptance judged as before: want allow, got deny/' "$D/n4/fix3-old.txt"
case_run "FIX-3: the named old-only case in the wrong direction" "CHECK FAILED, not now refused" n4

mk n5
last_to "$D/n5/fix3-new.txt" "49 failed, 235 passed, 1 skipped, 1 error in 30.0s"
case_run "FIX-3: one case errors under the new pin (review r2 F7)" "CHECK FAILED, under the new pin" n5

mk n6
last_to "$D/n6/fix3-old.txt" "49 failed, 235 passed, 1 skipped, 1 error in 30.0s"
case_run "FIX-3: one case errors under the old pin (review r2 F7)" "CHECK FAILED, under the old pin" n6
