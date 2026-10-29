"""Replaces RESUME HERE's header line (line 3) with the state of 2026-10-29 12:55."""
import pathlib

CP = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CHECKPOINT.md")
NEW = ("## RESUME HERE (2026-10-29 12:55 GMT — OWNER ANSWERED P1-MORNING-2026-10-29 (DEC-939, drafted in "
       "drafts/DEC-939.md; all 7 items: 1a, 2 diag + rebuild lock + 30-min watchdog -> W2-76, 3a re-close W2-58, 4a, "
       "5b + W2-77 (W2-M406 fix) next free slot then measure the batch's gain, 6a + 01:00 cut-off for leads' full runs, "
       "7 Pushover for emergencies). QUEUE RUNNING (task bqt6uzib1): W2-75, W2-63, W2-07, W2-68 -> NO main-tree commits "
       "and no tk create (an untracked ticket stops gate (d)). LEADS: W2-71 run 2 (F1), W2-57 run 4 re-probe (both "
       "launched 12:24). WHEN THE QUEUE ENDS, in order: (1) append DEC-939 (mark DEC-938's status) + prompt v3.38 (§7: "
       "long commands background, 07:45 watchdog, 'background waits (tools/wake_at.sh)' not one-shot prompts, Pushover "
       "for emergencies; §15: 01:00 cut-off, rebuild lock) + LEAD-w2-common (rebuild under flock "
       "/tmp/gov-os-rebuild.lock; 01:00 cut-off) + rows W2-M408, W2-L451 + nightly folder from drafts/nightly-next2/ "
       "(36/36 tests, 4 mutation checks) + packages/ACT-PUSHOVER-1.md (drafts/) -> record checks -> commit; "
       "(2) tk create W2-76, W2-77 from drafts/ticket-W2-7[67].md (+ cards), commit each, rebuild, record checks; "
       "(3) queue W2-58 (its second close) [+ W2-57 if its re-probe is done and merged]; (4) leads W2-77 (first), "
       "W2-76; (5) ping ACT-PUSHOVER-1. Rebuilds: under flock /tmp/gov-os-rebuild.lock from now. Waits for 10-30: 05:37 "
       "(b1i68bdcz), 07:30 (b6l8spi3y), 07:45 (bttcl762a). Then ACT-REPIN-3 (W2-68 + W2-71 [+ W2-77]); ACT-W2-57-LS-2; "
       "W2-67, K4, K3; next DEC-940)")
lines = CP.read_text(encoding="utf-8").split("\n")
assert lines[2].startswith("## RESUME HERE")
lines[2] = NEW
CP.write_text("\n".join(lines), encoding="utf-8")
print("header replaced")
