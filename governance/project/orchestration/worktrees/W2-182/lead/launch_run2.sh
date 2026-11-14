#!/usr/bin/env bash
# Run 2: the test designer (tests worktree) and the product-spec worker (ticket tree), both Sonnet high, class C1.
T=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/launch_worker.sh
B=/home/usain/gov-os-worktrees/W2-182/.gov-runtime/scratch/lead/briefs
grep -n '{[A-Z_]*}' "$B/td-3.md" "$B/ps-1.md" && { echo "unfilled slot"; exit 2; }
cd /home/usain/gov-os-worktrees/W2-182-tests && LAUNCH_TICKET=DAEO-5y8d bash "$T" --model claude-sonnet-5-5 --class C1 independent-test-designer high "$B/td-3.md"
echo "td rc=$?"
cd /home/usain/gov-os-worktrees/W2-182 && LAUNCH_TICKET=DAEO-5y8d bash "$T" --model claude-sonnet-5-5 --class C1 product-spec high "$B/ps-1.md"
echo "ps rc=$?"
