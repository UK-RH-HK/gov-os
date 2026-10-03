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

### Process KPIs

| KPI | Verification |
|-----|--------------|
| **Success 6.** W1-02 and W1-03 tests revised by the Independent Test Designer, recorded as DEC-106 rewrites | The revisions are in the commit (Role: independent-test-designer), and each revision is recorded in the W1-02 and W1-03 READMEs as "Rewrites after implementation" with reason "owner correction, DEC-156" |
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
| `"orchestrator-in-engineer-session-on-the-engineer-s-ticket"` | `ROLE_DENIES` (denied) | `ROLE_ALLOWS` (allowed) | DEC-156: the orchestrator subagent may write source regardless of ticket |

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

## W1-04 and W1-05 findings (not revised)

### W1-04 `test_w1_04_only_escalates.py`

Two entries in `DENIED_BY_THE_GUARD` (lines 54-58) assert the old orchestrator rule:

1. `"write-outside-the-ticket-paths"`: `"pip install requests && touch src/app/main.py"` -- under DEC-156 the guard no longer denies `src/app/main.py` for the orchestrator, so the guard's denial of the WRITE portion is gone; only the install portion's `ask` decision remains.
2. `"redirect-outside-the-ticket-paths"`: `"npm install -g ccusage > README.md"` -- under DEC-156 the guard no longer denies the redirect to `README.md` for the orchestrator.

The third entry `"write-into-the-acceptance-tests"` is correct under DEC-156 (acceptance is still denied).

Lines 88-89 (`test_the_guard_s_answers_on_file_writes_are_unchanged`): `governance/project/tool-registry.yaml` is inside the W1-04 orchestrator ticket's `governance/project/**` paths; this test is correct under both old and new rules.

### W1-05

No tests assert the old orchestrator path rule.  The orchestrator references in W1-05 test subagent definitions (DEC-119), install behaviour (W1-04), and live hook timing -- none depend on the orchestrator being confined to its ticket's `allowed_paths`.
