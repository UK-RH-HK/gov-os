# W2-64 lead checkpoint (DAEO-0uhh, run 1) — returned PACKAGES (P-W2-64-1)

## State
- **Branch** `w2/W2-64`, head after the final checkpoint commit (see `git log`); the code head is d1486eaa3c47.
- **Commits of this run:** 894b72782d8b, 4174f6631ae8 (independent-test-designer: tests and README);
  25318f976 merge of w2/integrate d5d7fac9cb90 (orchestrator; the engineer gate, W2-58 closed);
  d1486eaa3c47 (engineer: schema.py, close.schema.json, test_schema_shapes.py, test_schema_validator.py);
  a6e1c56d7e9d (orchestrator: CP-DAEO-0uhh-0003); a final orchestrator checkpoint commit.
- **Ticket's own suite:** 83 passed (close form). **core-schema** GREEN on this head (795 records validated,
  docs/imported/ named as left out, history, DEC-844; validator 0.38.2 = pin).
- **Full parallel run** (scope full, scoped_plan; log/parallel.xml): 200 failed, 16740 passed, 31 skipped,
  3 errors. All 203 are earlier tests whose fixtures the real schemas refuse or whose PATH lacks the tool:
  W1-30 180 (fixture tickets' wbs_id `W1-<word>`, e.g. W1-work, refused by `^W[0-9]+-[0-9]{2,}[a-z]?$`;
  one `DEC-earlier` madr id), W2-54 16 (test_w2_54_audit_report.py: PATH without check-jsonschema, list-only
  helper), W1-26 4 (test_w1_26_dec436.py REC-NEW-001; test_w1_26_installed_kernel.py kpis as a list, 3),
  unit 2 (test_check.py::test_schema_clean_record T-001; test_kernel_followup.py::
  test_a_probe_record_is_never_silent_where_its_schema_cannot_be_read expects SCHEMA_INVALID_FIELD),
  W2-57 1 (test_w2_57_nightly_route.py, wbs W1-w257).
- **Serial-only part: not run.** Queued on /tmp/gov-os-verify.lock 16:31-17:55 behind W2-76's full run
  (105 min) with W2-71's close also waiting; withdrawn at the 90-minute hold rule (DEC-943), closes first.
- **gov check** (load ~50): core-schema GREEN; RED context-reproducibility (its 600 s limit under load) and
  secrets-indexing (traceback; `python3 -m gov.secrets` alone exit 0); YELLOW core-decision-citations,
  openspec-validate.
- **Loop count:** 1.

## What a resume must do
1. Once P-W2-64-1 is decided: a fresh independent test designer revises the named earlier tests under the
   owner's named decision (Rewrite-Reason: DEC-872 item 2), lowering no expectation; the two unit tests by
   whoever the decision names (outside this ticket's allowed_paths).
2. Optional ride-along residual: skips[].reason minLength 1 in close.schema.json (an empty skip reason in a
   future close record would turn core-schema RED for everyone); relax to a plain string if the owner wants.
3. Re-verify in full (scope full), the serial-only part included, then gov check at low load; return DONE.
4. KPI line 5 (W2-61's measure after the merge) is the orchestrator's.

## Brief gaps (running list)
- check-jsonschema's -v JSON answer differs on pass and fail (checked_paths vs successes) | a tool | ~5 min
- how runner reads a check's stdout (success form needed for an informational output) | this ticket's part | ~5 min
- the card's "unknown type is SCHEMA_INVALID_TYPE" vs code's SCHEMA_UNKNOWN_TYPE | the ticket file | ~3 min
- the brief named "earlier tests that pin the subset" but not that W1-30's shared fixtures carry invalid
  wbs_ids (180 cases) | this ticket's part | ~20 min
- workers' Write to `.gov-runtime/scratch/td|eng/` refused (both used the session scratchpad) | common brief | ~5 min each, estimated
- the engineer's file share (400,000) is smaller than one W1-26 run's pytest temp (~354,000) plus others | common brief | ~10 min, estimated
- the verification lock held 105 min by another lead's full run, with a close waiting | a tool (lock queue) | 84 min
