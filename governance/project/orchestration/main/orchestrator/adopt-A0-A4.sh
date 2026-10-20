#!/bin/bash
# DEC-617, DEC-624: stages A0 to A4 of this repository's adoption. Stops at the first refusal.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log
P=/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/45f2a529-6746-474d-b738-e1df6781c663/scratchpad/adopt-proposal.yaml
for S in A0 A1 A2 A3 A4; do
  if [ "$S" = A3 ]; then
    PYTHONPATH=src python3 -m gov.cli.main adopt --lite --stage A3 --map "$P" --json --session 45f2a529-6746-474d-b738-e1df6781c663 > $L/adopt-$S.json 2> $L/adopt-$S.err
  else
    PYTHONPATH=src python3 -m gov.cli.main adopt --lite --stage $S --json --session 45f2a529-6746-474d-b738-e1df6781c663 > $L/adopt-$S.json 2> $L/adopt-$S.err
  fi
  code=$?
  echo "$S exit $code"
  head -c 500 $L/adopt-$S.json; echo
  [ $code -ne 0 ] && { head -c 600 $L/adopt-$S.err; exit 1; }
done
git log --oneline -6
git status --short
sha256sum governance/adoption/A3-target-path-map.md
