# ACT-REPIN-W2: re-pin window 2 (DEC-1052 D-1; P1-PLAN P1-3 (iii))

For the owner's operator, in a **plain terminal** (not inside a Claude session: it reinstalls gov, DEC-928 item 3).
The CTO writes `log/act-in-progress.txt` at the hand-over (DEC-1028 item 6: no CTO commit until the owner says done).

## What it does
Installs gov from the wheel of `9894b0cf` (`w2/integrate` after D-1: the memory branches merged as built, W2-122
seeded rebuilds, W2-123 parallel requests and the bounded retry, W2-126 the machine-wide vector cache with KPI 7,
W2-112 the shared reranker, W2-04 gov context; and `emg/noscan`, DEC-1045's product switch, and `emg/select`, T-4)
beside the live `pin-a7182f6c` (window 1), checks it there, switches `~/.local/bin/gov` to it in one atomic rename,
checks it live, and records it in the tool registry (your commit, `Role: owner`). `pin-a7182f6c` stays for the
rollback. Nothing else on the machine changes: the servers, the crontab and the dispatcher stay as they are; W2-112's
reranker service does not start.

## The commands (about 5-10 minutes)
```
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/pin/REPIN-COMMANDS-9894b0cf.sh 2>&1 | tee ~/repin-9894b0cf.log
```
- It stops at the first failure. **Before the switch** (sections 0, A, B, C) a failure prints `STOP: ...` and changes
  nothing that sessions use. **After the switch** (section D) a failed check switches straight back to
  `pin-a7182f6c` by itself and prints `ROLLED BACK: ...`. Either way: tell the CTO.
- Success ends with `RE-PIN DONE: pin-9894b0cf is live`.

## The CTO's dry run on the same commit
- Two builds from clean exports agree: sha256 `94931d3d6f836a24ae4a78aac6f03e2ab13b42a3ddcaf22390270537fe1525c2`
  (section A checks it again).
- Section B's checks on the dry install: ALL CHECKS PASS (`log/repin-w2-dry-checks-20261103-r2.txt`): gov imports
  from the pin; the commands listed; no CPU-only gate; the dependencies import; a search with both facets available
  (1.1 s, on the integration store refreshed at `9894b0cf`); `gov context`; the SessionStart, PreCompact and Stop hooks;
  the guard's planted cases PASS, ACT-GUARD-FIX-3's suite 269 passed 1 skipped (as window 1), the hook 0.1 s.
- One check fixture was corrected first: two of the guard's planted rule-2 cases named the W2-87 worktree and W2-61's
  run clone, which D-0 removed (DEC-1053); they now name W2-13's, and the live pin passes them as before.

## Rollback (if anything goes wrong after the switch)
```
ln -s ~/.local/share/gov-os/pin-a7182f6c/bin/gov ~/.local/bin/gov.new && mv -Tf ~/.local/bin/gov.new ~/.local/bin/gov; hash -r
```
and revert the registry commit.

## After it
Tell the CTO "done": it ends its hold (`mv`, never `rm`), confirms the pin from its own session and goes on with D-2.
The full suite on the refactored repository (P1-12, on the owner's word) verifies the merged branches.

**Basis:** question 1 (memory: the agents' hooks and searches run the merged memory code, not the old pin) and
question 2 (a rollback in one command; nothing switched unless every check passes).
