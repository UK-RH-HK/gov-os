#!/bin/bash
# DEC-617, DEC-624: stages A5, A6 (with the rebuild that follows it) and A8. Stops at the first refusal.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log
for S in A5 A6 A8; do
  if [ "$S" = A5 ]; then
    PYTHONPATH=src python3 -m gov.cli.main adopt --lite --stage A5 --verdict docs/audit/wave-1/adoption-path-map-verdict.md --json --session 45f2a529-6746-474d-b738-e1df6781c663 > $L/adopt-$S.json 2> $L/adopt-$S.err
  else
    PYTHONPATH=src python3 -m gov.cli.main adopt --lite --stage $S --json --session 45f2a529-6746-474d-b738-e1df6781c663 > $L/adopt-$S.json 2> $L/adopt-$S.err
  fi
  code=$?
  echo "$S exit $code"
  head -c 700 $L/adopt-$S.json; echo
  [ $code -ne 0 ] && { head -c 600 $L/adopt-$S.err; exit 1; }
done
git log --oneline -6
git status --short
git ls-files cli | wc -l
