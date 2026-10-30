You are the ticket lead for ticket `DAEO-0uhh` (`W2-64`, core-schema validates every record through the pinned check-jsonschema; `docs/imported/` left out by name; the close schema states W2-66's evidence block). Profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-64` on branch `w2/W2-64`. **This is run 2, a resume:** read `.gov-runtime/scratch/lead/CHECKPOINT.md` in this worktree first and go on from it.

**The owner's answer to your package P-W2-64-1 (DEC-954, 2026-10-30): (a).** It is the owner's named decision under DEC-906:
- a **fresh independent test designer** corrects the earlier fixtures that the real schemas refuse (the 203 cases of your table: W1-30's shared fixture wbs ids and `DEC-earlier`; W2-57's one wbs id; W1-26's decision ids and `kpis` as an object; W2-54's support given the suite's check-jsonschema on its PATH and reading the dict output forms; the two unit tests `tests/unit/check/test_check.py::test_schema_clean_record` and `tests/unit/check/test_kernel_followup.py::test_a_probe_record_is_never_silent_where_its_schema_cannot_be_read`);
- **lowering no expectation**, each commit with `Rewrite-Reason: DEC-872 item 2` and naming DEC-954;
- the two unit tests are now in this ticket's paths (`b3888162` widened the ticket).
- **Verification, as the owner set it:** a scoped run of the corrected tests only (the files the test designer changed, in the close's form). If they turn green, that is enough. **No full run;** the nightly covers the rest. Run `gov check`'s `core-schema` once more and quote it.
- The ride-along you proposed (relax `skips[].reason` to a plain string) is accepted in this resume if it is a one-line schema change inside your paths with its builder test.

**First:** merge `w2/integrate` into this branch (`git merge --no-ff w2/integrate`, trailers `Task: DAEO-0uhh`, `Role: orchestrator`), so the widened ticket, DEC-953 and DEC-954 and the new common brief are here. Then the test designer, then the scoped run.

**Under DEC-953 and DEC-954 (the common brief's DEC-953 block holds where anything differs):** your ticket closes on the audit's 10 practices; the close is the orchestrator's. Lifted for you: the pre-close gate, re-probes after merges, the ratchet lists, the quiet windows and cut-offs, the 90-minute rule. A full run, if any, goes through `verify_lock.sh` (closes go first). The test designer's brief carries the counterpart rule (it never reads this ticket's implementation: `git diff --name-only w2/integrate...HEAD` names it, other than tests) and the scratch budget.

**Return:** the twelve fields, status DONE (with the scoped run's counts and core-schema's line) or PACKAGES. Name your temp folder for the orchestrator to remove.
