
## W1-30 closed after the follow-up after W1-41 (2026-10-10; for the exit auditor)

**The escalation path, as it ran.** The first `gov close DAEO-2lwj` on the merge (`caa8ac5c`) answered `ESCALATION_BLOCKED` at once (exit code 4, nothing ran): the ticket's refused closes, each refused on this repository's baseline before adoption, had reached three and an escalation was in force. The owner lifted it the built way (P-36 a): the operator committed the register entry DEC-593 with `Role: owner` as the commit's only role (`700bb5b5`), and `gov close DAEO-2lwj --owner-decision DEC-593` then ran whole. The escalation file names `lifted_by: DEC-593`, the counter restarted, and DEC-593 is recorded as used. The path worked as built.

That close refused, as every close does until adoption (DEC-522); its output is kept by the orchestrator. Closed with the ticket tool under DEC-492, DEC-505, DEC-516, DEC-519, DEC-522, DEC-536, DEC-592 and DEC-594:

- **Tests:** the ticket's acceptance run 425 passed; the regression 11,739 passed, 1 failed, 29 skipped. The failed case, `tests/unit/close/test_follow_up.py::test_at_the_time_limit_the_processes_a_run_started_are_ended_with_it`, passes alone (a time-limit case in the parallel run). The orchestrator's direct regression on the same merge, in the close's form, was green (11,903 passed; 262 serial-only passed).
- **Probe gate:** "ticket commit `caa8ac5c` changes `src/gov/check/commands.py` after the probed commit". The merge holds that file exactly as the probed commit `83d11b2d` does. The ticket has three probe records (its first build, its earlier follow-up, this follow-up) and the gate asks every record everything and ends at its first finding: against an earlier round's probed commit, this round's merge is a later change. **Residual (Wave 2 list): a reopened FULL ticket with an earlier probe record always refuses at the probe gate.** What the gate answers for this round's record alone was not measured by the close.
- **Red checks:** the thirteen of the baseline; `core-schema` 11; `product-traceability-trailers` 294 with the base of DEC-482 in the path map; `secrets-indexing` timed out (the round of DEC-595).
- **Work without a task:** `7674efde`, `478a8ed0` as before, and `e0572d12` (a W1-36 commit of 2026-10-06 without trailers, now inside this ticket's widened paths).
- **Trailers:** 22 commits of the ticket lack `Implements:` (before DEC-476, and the named ones). **Containment:** `29af0646`, `148f7584` (merges, a W1-07 support file), as at this ticket's earlier close.
- **Checkpoint stale; context blocked** on a capability record not in the store (adoption brings them).
- **Repair ticket** `DAEO-fknh` opened by the refused close: not committed, kept by the orchestrator.
