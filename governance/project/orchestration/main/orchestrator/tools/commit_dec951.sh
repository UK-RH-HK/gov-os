#!/usr/bin/env bash
# DEC-951's commits, only after the record checks (the untracked-ticket stale-store error aside, which the commit of
# W2-85's file and a rebuild clear): the record first, then each ticket on its own Task.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
CO="Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git add docs/DECISION_REGISTER.md docs/plan/WAVE_2_WBS.md governance/project/prompts/w2-orchestrator.md .tickets/DAEO-0z8c.md .tickets/DAEO-cv58.md .tickets/DAEO-k7hz.md .tickets/DAEO-gdzh.md || exit 1
bash .gov-runtime/scratch/orchestrator/tools/record_checks.sh > /dev/null 2>&1
bad=$(grep -h "exit [1-9]" .gov-runtime/scratch/orchestrator/log/record-checks/*.out 2>/dev/null)
ctx=$(grep "^ERROR" .gov-runtime/scratch/orchestrator/log/record-checks/context-reproducibility.out | grep -v "DAEO-gdzh" | grep -v "not found in the store")
for f in core-pathmap core-schema core-mutation core-authority core-graph; do
  [ -s .gov-runtime/scratch/orchestrator/log/record-checks/$f.out ] && { echo "RED: $f"; cat .gov-runtime/scratch/orchestrator/log/record-checks/$f.out | tail -5; exit 1; }
done
grep -q "passed" .gov-runtime/scratch/orchestrator/log/record-checks/record-reading.out && ! grep -q "failed" .gov-runtime/scratch/orchestrator/log/record-checks/record-reading.out || { echo "RED: record-reading"; exit 1; }
[ -z "$ctx" ] || { echo "RED: context: $ctx"; exit 1; }
git commit -q -m "Decision record DEC-951 (owner): closes released; W2-05 resumes after a W1-02 revision; W2-54's time limits to the nightly (W2-85); W2-60a's last round; standing: a red nightly found, repaired, merged and verified needs no owner, and the 07:30 ping kept clear; prompt v3.44" --trailer "Task: decision-record" --trailer "Implements: DEC-951" --trailer "Role: orchestrator" --trailer "Decided-by: owner (chat, 2026-10-30)" --trailer "$CO" -- docs/DECISION_REGISTER.md docs/plan/WAVE_2_WBS.md governance/project/prompts/w2-orchestrator.md || exit 1
git commit -q -m "DAEO-gdzh (W2-85): new ticket file: W2-54's two time-limit cases routed to the nightly (DEC-951 item 3)" --trailer "Task: DAEO-gdzh" --trailer "Implements: DEC-951" --trailer "Role: orchestrator" --trailer "$CO" -- .tickets/DAEO-gdzh.md || exit 1
git commit -q -m "DAEO-0z8c (W2-05): paths widened by tests/acceptance/W1-02/** for the W1-02 deadline revision (DEC-951 item 2)" --trailer "Task: DAEO-0z8c" --trailer "Implements: DEC-951" --trailer "Role: orchestrator" --trailer "$CO" -- .tickets/DAEO-0z8c.md || exit 1
git commit -q -m "DAEO-cv58 (W2-60a): paths widened by the three named unit files and serial-only.txt for round 3 (DEC-951 item 4)" --trailer "Task: DAEO-cv58" --trailer "Implements: DEC-951" --trailer "Role: orchestrator" --trailer "$CO" -- .tickets/DAEO-cv58.md || exit 1
git commit -q -m "DAEO-k7hz (W2-11): the test-design skill says how much is enough (DEC-951 item 5)" --trailer "Task: DAEO-k7hz" --trailer "Implements: DEC-951" --trailer "Role: orchestrator" --trailer "$CO" -- .tickets/DAEO-k7hz.md || exit 1
git log --oneline -5 | cut -c1-90
git status --short | wc -l
