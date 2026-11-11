#!/usr/bin/env bash
# Runs `gov brief lead <ticket> --run <kind>` for each step of BATCH-PREP.md; output (or the refusal) to briefs/.
# Read-only: gov brief writes nothing in the repository.
set -u
ROOT=/home/usain/Dynamic-Agentic-Engineering-OS
OUT=$ROOT/.gov-runtime/scratch/orchestrator/drafts/batch-prep/briefs
cd "$ROOT" || exit 1
while read -r w2 kind; do
  [ -z "$w2" ] && continue
  f="$OUT/$w2-$kind.md"
  gov brief lead "$w2" --run "$kind" >"$f.out" 2>"$f.err"
  rc=$?
  echo "$w2 $kind rc=$rc out=$(wc -c <"$f.out") err=$(wc -c <"$f.err")"
done <<'EOF'
W2-04 review
W2-105 tests
W2-11 resume
W2-66b tests
W2-66c tests
W2-81 land
W2-90b land
W2-94 build
W2-93 tests
W2-98 build
W2-40 build
W2-173 tests
EOF
