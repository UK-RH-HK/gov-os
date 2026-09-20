#!/usr/bin/env bash
# P2-AR-0045 — re-run every check of the AC-6 oracle-format review, from the Governance OS repository root.
# Requires: target/release/gov built in this worktree (CARGO_BUILD_JOBS=2 cargo build --release).
set -u
E=release/capability-baseline/verify-1/oracle-format/evidence
WSROOT="${1:-$(mktemp -d)}"
echo "=== 01 the format the product reports ==="
target/release/gov oracle format | head -8
echo
echo "=== 02 independent coverage of Contract v3 Gate V against the owner-source bytes ==="
python3 $E/02-coverage-crosswalk-check.py | tail -8
echo
echo "=== 03/04 regenerate the labelled sample corpus ==="
python3 $E/03-make-samples.py && python3 $E/04-make-report-samples.py
echo
echo "=== 05 attack matrix (valid and invalid samples per V1-V4 bullet) ==="
python3 $E/05-RUN-ALL-samples.py | tail -3
echo
echo "=== 06 physical separation attacks (Contract v3:1062) ==="
mkdir -p "$WSROOT/sep"; bash $E/06-separation-attacks.sh "$WSROOT/sep"
echo
echo "=== 07 the G6 entry point ==="
mkdir -p "$WSROOT/g6/proj"
( cd "$WSROOT/g6/proj" && git init -q . && "$OLDPWD/target/release/gov" --role orchestrator init \
    --name p2ar0045runall --source "$OLDPWD" --skip-index >/dev/null 2>&1 )
bash $E/07-g6-entry-point.sh "$WSROOT/g6"
echo
echo "=== 08 how deeply each V4 metric is bound to the oracle ==="
python3 $E/08-v4-binding-depth.py
echo
echo "=== 09 greenfield (Repo A) shape and the explicit-N/A rule ==="
python3 $E/09-greenfield-and-na.py
echo
echo "=== 11 evidence owners for V1-V4 (AC-10 slice) ==="
python3 $E/11-evidence-owners-v1-v4.py | tail -3
echo
echo "=== 12 hidden-oracle material inside a governed repository ==="
bash $E/12-governed-repo-record.sh "$WSROOT/g6/proj"
