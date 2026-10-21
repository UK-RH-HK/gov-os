# DEC-891: what to apply when queue run 6 ends (before W2-62's close)

1. Register: append `drafts/register-278-DEC-891.md`; version 0.278 (check the previous section is 277 and the version 0.277).
2. Path map, at the end of `accepted_history`:
   ```yaml
     - commit: "162f17ea9cafeec96687d2a83c43c060c08d3e1b"
       decision: DEC-891
   ```
3. Prompt §5, the decision-record bullet, after DEC-862 (a)'s exception sentence: "**Accepted history (owner, standing, DEC-891):** an `accepted_history` entry for a commit that changes only records or ticket files (`.tickets/`, `docs/checkpoints/`, `docs/close/`, `docs/probes/`, the register, the plan files, `governance/project/orchestration/`) you record from the owner's chat decision, naming the commit and listing its changed paths; an entry for any commit that changes code, tests or the kernel stays the owner's own `Role: owner` commit (prepare it, ping ACT), because it exempts that commit from traceability." Version line: v3.12: DEC-891.
4. W2-12's card (WBS) and `.tickets/DAEO-j8gn.md`: one line beside the ratchet entries and escalation lifts: "DEC-891: an accepted-history entry for a commit that changes code, tests or the kernel is in the same owner-only class until W2-12 moves it to the owner's push in git; entries for record-only commits are recorded by the orchestrator from the owner's decision."
5. `packages/P-W2-62-H.md` from `drafts/P-W2-62-H.md`.
6. LIST: mark W2-02's and W2-54's rows closed (their close commits `e52ad8a2`, `55162ea2`), and the rows of whichever of W2-63, W2-50, W2-58 close in run 6.
7. `tools/record_checks.sh`; commit (decision-record, Decided-by owner); sync to record/w2.
8. Then `tools/trailer_gate.py DAEO-juee` must pass; then `bash tools/close_queue.sh DAEO-juee`.
9. After it: remove the closed tickets' worktrees and branches (sync first).
