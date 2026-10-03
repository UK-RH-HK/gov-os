# W1-45 Orchestrator write scope -- acceptance tests

Covers id: **CAP-58.e** (orchestrator write scope).
Ticket: DAEO-6cc2.  Sources: DEC-150, DEC-156, DEC-171, DEC-112, DEC-106, MR-3.

## KPI-to-test mapping

### Guard (PreToolUse) -- `test_w1_45_orchestrator_scope.py`

| KPI | Tests | Red reason (before implementation) |
|-----|-------|-------------------------------------|
| **Success 1.** Orchestrator writes anywhere except `tests/acceptance/**`, whatever the ticket, and with no ticket (DEC-156) | `test_orchestrator_can_write_outside_ticket_paths` (9 cases), `test_orchestrator_can_write_without_a_ticket` (4 cases), `test_orchestrator_bash_writes_outside_ticket_paths` (5 cases) | The guard denies orchestrator writes outside the ticket's `allowed_paths` |
| **Success 2.** Orchestrator denied under `tests/acceptance/**` (MR-3) | `test_orchestrator_cannot_write_under_acceptance_tests` (5 cases), `test_orchestrator_bash_write_under_acceptance_tests_is_denied` (3 cases) | Already passes (the guard already denies `tests/acceptance/**` for non-test-designer roles) |
| **Success 5.** Every other role unchanged (DEC-112) | `test_engineer_is_still_denied_outside_ticket_paths`, `test_product_spec_is_still_denied_outside_ticket_paths` | Already passes |
| **Success 7.** Orchestrator checkpoint at `.gov-runtime/scratch/orchestrator/` (DEC-150) | `test_orchestrator_can_write_its_checkpoint`, `test_orchestrator_checkpoint_works_without_a_ticket` | Already passes (scratch set is allowed for known roles) |
| **Failure 1.** Orchestrator writes `tests/acceptance/**` | `test_orchestrator_cannot_write_under_acceptance_tests`, `test_orchestrator_bash_write_under_acceptance_tests_is_denied` | Already passes |
| **Failure 2.** Another role gains a write outside its ticket paths | `test_engineer_is_still_denied_outside_ticket_paths`, `test_product_spec_is_still_denied_outside_ticket_paths` | Already passes |
| **Failure 3.** No-role or unknown role gains a write | `test_no_role_or_unknown_role_is_denied` (4 cases) | Already passes |

### Containment (PostToolUse) -- `test_w1_45_containment.py`

| KPI | Tests | Red reason (before implementation) |
|-----|-------|-------------------------------------|
| **Success 3.** Orchestrator commit of non-acceptance files passes | `test_orchestrator_commit_outside_ticket_paths_is_silent`, `test_orchestrator_commit_of_engineer_source_is_silent` | The containment check currently flags commits outside the ticket's `allowed_paths` |
| **Success 3 (negative).** Commit touching `tests/acceptance/**` is caught | `test_orchestrator_commit_touching_acceptance_is_caught` | Already passes |
| **Success 4.** Change outside ticket paths is a record, not a finding (DEC-171) | `test_orchestrator_change_outside_ticket_paths_is_a_record_not_a_finding` (5 cases) | The containment check currently catches every out-of-scope change as a finding |
| **Success 4.** In-scope change stays silent | `test_orchestrator_in_scope_change_is_still_silent` | Already passes |
| **Success 4 (negative).** Change under `tests/acceptance/**` stays a finding | `test_orchestrator_change_under_acceptance_stays_a_finding` | Already passes |
| **Success 5 / Failure 2.** Engineer containment unchanged | `test_engineer_change_outside_ticket_paths_is_still_caught` | Already passes |
| **Failure 1.** Orchestrator change under acceptance is caught | `test_orchestrator_change_under_acceptance_stays_a_finding`, `test_orchestrator_commit_touching_acceptance_is_caught` | Already passes |

### Subagent scope (PreToolUse + PostToolUse) -- `test_w1_45_subagent_scope.py`

| KPI | Tests | Red reason (before implementation) |
|-----|-------|-------------------------------------|
| **Failure 2.** Another role gains a write through an orchestrator subagent | `test_orchestrator_subagent_denied_outside_scope_in_non_orchestrator_session` (6 cases), `test_orchestrator_subagent_denied_outside_orchestrator_ticket_paths`, `test_orchestrator_subagent_bash_denied_in_non_orchestrator_session` (3 cases), `test_orchestrator_subagent_without_ticket_denied` (4 cases) | The orchestrator subagent may get the wide DEC-156 scope in a non-orchestrator session |
| **Failure 2 (positive).** Orchestrator subagent on its own ticket gets ticket paths | `test_orchestrator_subagent_allowed_on_orchestrator_ticket_paths` (2 cases), `test_orchestrator_subagent_can_write_to_scratch` | Already passes (ticket-path match, scratch) |
| **Failure 3.** No-role or unknown-role session orchestrator subagent is read-only | `test_no_role_session_orchestrator_subagent_is_read_only`, `test_unknown_role_session_orchestrator_subagent_is_read_only` | Already passes (DEC-125) |
| **Success 1.** In an orchestrator session the orchestrator subagent keeps the wide scope | `test_orchestrator_subagent_wide_scope_in_orchestrator_session` (8 cases), `test_orchestrator_subagent_bash_wide_scope_in_orchestrator_session` | The subagent may not get the wide scope at all (if the implementation is session-scoped both ways) |
| **Success 2.** Even the orchestrator subagent is denied under `tests/acceptance/**` | `test_orchestrator_subagent_acceptance_denied_in_orchestrator_session` | Already passes (MR-3 exclusion) |
| **Containment.** Orchestrator subagent in non-orchestrator session: change is a finding | `test_containment_catches_orchestrator_subagent_in_non_orchestrator_session` | The containment check may treat it as a DEC-171 record |
| **Containment (DEC-171).** Orchestrator subagent in orchestrator session: change is a record | `test_containment_silent_for_orchestrator_subagent_in_orchestrator_session` | Already passes (DEC-171) |

### Guard -- `.gov-runtime/` denied to the orchestrator (DEC-176) -- `test_w1_45_gov_runtime.py`

| KPI | Tests | Red reason (before implementation) |
|-----|-------|-------------------------------------|
| **DEC-176.** `.gov-runtime/` other than `scratch/**` denied to the orchestrator, file tools | `test_orchestrator_denied_gov_runtime_with_file_tools` (4 cases) | The guard does not yet deny `.gov-runtime/` other than `scratch/**` for the orchestrator (DEC-176 not implemented) |
| **DEC-176.** `.gov-runtime/` denied, Bash writes | `test_orchestrator_bash_denied_gov_runtime` (4 cases) | DEC-176 not implemented |
| **DEC-176.** `.gov-runtime/` denied with no active ticket | `test_orchestrator_denied_gov_runtime_without_ticket` (4 cases) | DEC-176 not implemented |
| **DEC-176.** `.gov-runtime/` denied while frozen | `test_orchestrator_denied_gov_runtime_while_frozen` (4 cases) | DEC-176 not implemented |
| **Success 7 (confirmation).** `scratch/**` stays writable | `test_scratch_stays_writable_for_orchestrator` | Already passes |

### Containment -- records.jsonl (DEC-177) -- `test_w1_45_records.py`

| KPI | Tests | Red reason (before implementation) |
|-----|-------|-------------------------------------|
| **Success 4 (DEC-177).** Out-of-scope orchestrator change writes one record | `test_orchestrator_change_outside_ticket_writes_a_record` (5 cases) | The containment check does not yet write to `.gov-runtime/records.jsonl` (DEC-177 not implemented) |
| **Success 4 (DEC-177).** The record has DEC-122's fields and `action: "recorded"` | `test_record_has_dec_122_fields_and_action_recorded` | DEC-177 not implemented |
| **Success 4 (DEC-177).** One record per call for multiple paths | `test_one_record_for_multiple_paths_changed` | DEC-177 not implemented |
| **Success 4 (negative).** In-scope change writes no record and no finding | `test_in_scope_change_writes_no_record` | Already passes (no record file, no finding) |
| **Success 4 (negative).** `tests/acceptance/**` stays a finding, not a record | `test_acceptance_change_writes_finding_not_record` | Already passes |
| **Success 5 / Failure 2.** Other roles' out-of-scope changes stay findings, never records | `test_engineer_change_outside_ticket_writes_finding_not_record` | Already passes |
| **Success 4 (DEC-177).** With no ticket, a change writes a record | `test_orchestrator_without_ticket_writes_a_record` | DEC-177 not implemented |
| **DEC-177 + DEC-178.** Orchestrator subagent in orchestrator session writes a record | `test_orchestrator_subagent_in_orchestrator_session_writes_a_record` | DEC-177 not implemented |

### Process KPIs

| KPI | Verification |
|-----|--------------|
| **Success 6.** W1-02, W1-03 and W1-04 tests revised by the Independent Test Designer, recorded as DEC-106 rewrites | The revisions are in the commit (Role: independent-test-designer), and each revision is recorded in the W1-02, W1-03 and W1-04 READMEs as "Rewrites after implementation" with reason "owner correction, DEC-156" |
| **Failure 4.** Tests revised by a non-test-designer, or a non-orchestrator test weakened | The commit metadata (Role: independent-test-designer) verifies authorship; the diffs show only orchestrator-related expectations changed |

## Revisions to W1-02 and W1-03 tests

Each revision is a rewrite after implementation with reason: **owner correction, DEC-156** (DEC-106).

### W1-02 `test_w1_02_allow_list.py`

| Case | Old expectation | New expectation | Reason |
|------|----------------|-----------------|--------|
| `OTHER_ROLES["orchestrator-neighbour-file"]` | denied (False) | allowed (True) | DEC-156: orchestrator writes anywhere except acceptance |
| `OTHER_ROLES["orchestrator-source"]` | denied (False) | allowed (True) | DEC-156 |
| `OTHER_ROLES["orchestrator-root-file"]` | denied (False) | allowed (True) | DEC-156 |
| `MISMATCHED["orchestrator-on-engineer-ticket"]` | denied | removed | DEC-156: the orchestrator writes regardless of ticket |
| `MISMATCHED["orchestrator-on-product-spec-ticket"]` | denied | removed | DEC-156 |

### W1-02 `test_w1_02_subagent.py`

| Case | Old expectation | New expectation | Reason |
|------|----------------|-----------------|--------|
| `"orchestrator-in-engineer-session-on-the-engineer-s-ticket"` | `ROLE_ALLOWS` (batch 2 revision) | `ROLE_DENIES` (denied) | DEC-136 batch 3: the wide DEC-156 scope does not reach an orchestrator subagent in a non-orchestrator session; batch 2 revision was incorrect |

### W1-03 `test_w1_03_out_of_scope.py`

| Case | Old expectation | New expectation | Reason |
|------|----------------|-----------------|--------|
| `test_each_ticket_role_is_compared_with_its_own_ticket` orchestrator case | README.md caught as finding | removed (now a record, not a finding) | DEC-156, DEC-171 |
| `NO_TICKET_PATHS["orchestrator-on-the-engineer-s-ticket"]` | every change reported (no ticket paths) | removed (orchestrator has paths regardless of ticket) | DEC-156 |

### W1-03 `test_w1_03_head_moves.py`

| Case | Old expectation | New expectation | Reason |
|------|----------------|-----------------|--------|
| `"orchestrator-on-the-engineer-s-ticket"` | `NOT_THEIR_PATH` (commit flagged) | `COMMITS_INSIDE` (commit silent) | DEC-156, DEC-171: the commit is a record, not a finding |

### W1-03 `test_w1_03_calls_known_to_be_over.py`

| Case | Old expectation | New expectation | Reason |
|------|----------------|-----------------|--------|
| `test_a_later_tool_call_of_its_actor_shows_the_call_is_over` ids `orchestrator-main-thread-then-an-engineer-subagent-bash-call-the-guard-denied` and `...-file-tool-call-the-guard-denied` | The denied later call writes `src/app/main.py` (denied under the old ticket-paths rule) | The denied later call writes `tests/acceptance/W1-90/test_fixture.py` (still denied: MR-3 exclusion) | DEC-156: `src/app/main.py` is no longer denied for the orchestrator |

## Revisions to W1-04 tests

Each revision is a rewrite after implementation with reason: **owner correction, DEC-156** (DEC-106, DEC-175).

### W1-04 `test_w1_04_only_escalates.py`

| Case | Old expectation | New expectation | Reason |
|------|----------------|-----------------|--------|
| `DENIED_BY_THE_GUARD["write-outside-the-ticket-paths"]` | `"pip install requests && touch src/app/main.py"` -- the guard denies `src/app/main.py` | Renamed to `"write-into-gov-runtime"`: `"pip install requests && touch .gov-runtime/findings.jsonl"` -- under DEC-176 `.gov-runtime/findings.jsonl` is denied | DEC-156: `src/app/main.py` is no longer denied for the orchestrator |
| `DENIED_BY_THE_GUARD["redirect-outside-the-ticket-paths"]` | `"npm install -g ccusage > README.md"` -- the guard denies the redirect to `README.md` | Renamed to `"redirect-into-gov-runtime"`: `"npm install -g ccusage > .gov-runtime/records.jsonl"` -- under DEC-176 `.gov-runtime/records.jsonl` is denied | DEC-156: `README.md` is no longer denied for the orchestrator |

The third entry `"write-into-the-acceptance-tests"` is correct under DEC-156 (acceptance is still denied).

Lines 88-89 (`test_the_guard_s_answers_on_file_writes_are_unchanged`): `governance/project/tool-registry.yaml` is inside the W1-04 orchestrator ticket's `governance/project/**` paths; this test is correct under both old and new rules.

### W1-05 (not revised)

No tests assert the old orchestrator path rule.  The orchestrator references in W1-05 test subagent definitions (DEC-119), install behaviour (W1-04), and live hook timing -- none depend on the orchestrator being confined to its ticket's `allowed_paths`.
