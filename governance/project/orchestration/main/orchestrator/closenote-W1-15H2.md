
## W1-15 closed after its second run (2026-10-10; for the exit auditor; DEC-609, DEC-610)

`gov close DAEO-7nne` on the merge (`a766f1af`) refused, as every close does until adoption (DEC-522); its output is kept by the orchestrator. Closed with the ticket tool under DEC-492, DEC-505, DEC-516, DEC-519, DEC-522, DEC-536, DEC-609 and DEC-610:

- **Tests:** acceptance 124 passed; regression 11,893 passed, 30 skipped in parallel; serial-only 261 passed, 1 failed: `tests/acceptance/W1-46/test_w1_46_live_sessions.py::test_the_sandbox_accepts_a_connection_to_a_starting_host_of_the_research_allowlist[developer.mozilla.org]`, a case that reaches a host on the network. Run again alone, the file's seventeen such cases passed.
- **Probe gate:** "ticket commit `8ec40bef` changes `template/.rulesync/hooks.jsonc` after the probed commit". The merge holds that file exactly as this run's probed commit `ca734550` does; the gate asks the first round's record (`cddf5ee3`) too. The named residual: a reopened FULL ticket with an earlier probe record always refuses at the probe gate.
- **Red checks:** the thirteen of the baseline. `secrets-indexing` is red on the three scratch files the operator moves (DEC-604). `fresh-agent-reconstruction` now starts (`gov` is installed, DEC-605) and is red on its own content.
- **Trailers:** ten commits of the ticket lack `Implements:`, as at its last close; every commit of this run carries all three. **Work without a task:** `478a8ed0`. **Context blocked** on `G-12` (adoption brings it).
- **Repair ticket** `DAEO-hv7l` opened by the refused close: not committed, kept by the orchestrator.
- **Measured on a dev-tier clone (DEC-610):** after a `cd` into a subfolder a real session's failed command was followed by the containment check, reported and recorded under the project's root, and ordinary calls were not blocked.
