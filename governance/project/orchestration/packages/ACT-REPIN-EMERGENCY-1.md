# ACT-REPIN-EMERGENCY-1: window 1 of the emergency re-pin, then ACT-QUERY-GPU-2 (DEC-1037 (1); the owner, ~17:00)

For the owner's operator, in a **plain terminal** (not inside a Claude session: it reinstalls gov, DEC-928 item 3).
The CTO has written `log/act-in-progress.txt` (DEC-1028 item 6: no CTO commit until the owner says the ACT is done).

## What it does
Installs gov from the wheel of `a7182f6c` (w2/integrate with DEC-1033's fix (b): a question's vector from any device)
beside the pinned `pin-5c401220`, checks it there, switches `~/.local/bin/gov` to it in one atomic rename, checks it
live, and records it in the tool registry (your commit, Role: owner). `pin-5c401220` stays for the rollback. W2-122
and W2-123 come with window 2 (the owner's order of ~17:00).

## Part 1: the re-pin (about 5-10 minutes)
```
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/pin/REPIN-COMMANDS-a7182f6c.sh 2>&1 | tee ~/repin-a7182f6c.log
```
- It stops at the first failure. **Before the switch** (sections 0, A, B, C) a failure prints `STOP: ...` and changes
  nothing that sessions use. **After the switch** (section D) a failed check switches straight back to the old pin by
  itself and prints `ROLLED BACK: ...`. Either way: tell the CTO, and do not run part 2.
- The CTO's dry run on the same commit: two builds agree (sha256 `9ed615a8b62231795d9846204b146a517b1756361130bdba4d4450a9694e211b`;
  section A checks it again); every check of section B passed on the dry install (the guard's: 54 planted cases
  PASS, 269 passed 1 skipped, the same as the old pin; the hook 0.1 s).
- Success ends with `RE-PIN DONE: pin-a7182f6c is live`.

## Part 2: ACT-QUERY-GPU-2 (about 5 minutes), right after
`governance/project/orchestration/packages/ACT-QUERY-GPU-2.md` (revision 2): its step 0 waits up to 5 minutes for
every process of the old pin to end, then the query server moves to the GPU through the wrapper set to `gpu`.

## Rollback (if anything goes wrong after part 1)
Undo ACT-QUERY-GPU-2 first if it ran (its "Undo"), then:
```
ln -s ~/.local/share/gov-os/pin-5c401220/bin/gov ~/.local/bin/gov.new && mv -Tf ~/.local/bin/gov.new ~/.local/bin/gov; hash -r
```
and revert the registry commit.

## After it
Tell the CTO "done" (it ends its hold, confirms the pin from its own session, sets the dispatcher to expect the query
server on the GPU, measures a question's time) and then the full suite runs on the re-pinned head.
