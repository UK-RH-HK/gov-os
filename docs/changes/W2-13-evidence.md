# W2-13 evidence: the ranked lexical route (BM25, SQLite FTS5) and RETR-X-02's stated gap (DAEO-zqvn; DEC-995, DEC-1055)

The ticket as built at `bdc4b7956a48` (lead resume 1, PACKAGES: waiting for W2-92; code head `febe5f6403d5`),
brought up to `w2/integrate` at `5522a603dead` (W2-92, W2-91, W2-61h merged; the CTO's P2 adding
`src/gov/retrieval/retrieve.py` to the ticket's paths) by the merge `b91e78b17cdb` (D-4b, DEC-1055). The merge had no
conflict; `src/gov/retrieval/lexical.py` auto-merged with DEC-1045's change on integrate (the secrets file among the
filter's judges). The one change W2-13 waited for is `3c0320080829`: `retrieve()` fuses each route's
`answer.get("ranked", answer["hits"])`, so the lexical route hands the fusion its ranked list beside the semantic one
(S2). W2-92's record and code routes, W2-112's `rerank` field and W2-126's cache are unchanged.

**Verified on:** the merge commit `b91e78b17cdb`, with the one line at `3c0320080829` (the worktree's store rebuilt
there with `--seed` under the D-4b lock, 2026-11-03: all three stores recreated, 57 s; seed: none, no warm base
configured) and the two builder tests fixed for the merge at `06e5ae70a4a7` (no code change; `gov accept` alone:
56 of 56, 6 of 6 lines). After the review: `3d1d1b34` (R4, a fused hit whose chunk the lexical index does not
hold is skipped), `ea486253` (R3's budget cut) and its revert `80cdd7ff` (DEC-419 DP-3, below); `gov accept` alone
on `80cdd7ff`: 56 of 56, 6 of 6 lines (load near 12); unit `tests/unit/retrieval` and `tests/unit/retrieve`: 300 passed, 1 skipped.

This record holds scores only: ids, counts and figures. It quotes no question's text and no gold answer. The
acceptance tests were run (pass or fail), never read.

## The KPI lines and how each is verified

`gov accept` = `PYTHONPATH=<tree>/src bash heavy_slot.sh python3 -m gov.cli.main accept W2-13 --json`, in the
worktree. Unit = `tests/unit/retrieval/test_w2_13_ranked.py`, `test_w2_13_id_boost.py`, `test_w2_13_rerank_work.py`,
`tests/unit/retrieve/test_w2_13_stated_gap.py` (in the scoped run, below).

| KPI | How it is verified | Command | Result | Verified on |
|---|---|---|---|---|
| S1 the ranked lexical route: FTS5, BM25 with id, title and body weights; an exact id first | `gov accept` line success-1; unit `test_w2_13_ranked.py`, `test_w2_13_id_boost.py` | `gov accept`; unit | pass, 13 of 13; unit pass | `06e5ae70a4a7` |
| S2 the fusion receives the ranked lexical list; the dev queryset's lexical-only hit@5 recorded | `gov accept` line success-2 (the `gov retrieve` case that waited for W2-92 now passes); the hit@5 below; the fusion's contribution: measure: D-4b measure 1 | `gov accept`; `lexical_hit5.py` (below); measure: D-4b measure 1 | pass, 3 of 3; hit@5 87.0 at the head (45 of 52), 0.0 at the base (0 of 52); the fusion's contribution: D-4b measure 1 | `06e5ae70a4a7` (`gov accept`); `3c0320080829` (hit@5) |
| S3 "unavailable" instead of raising; latency within the retrieve budget on the dev tiers | `gov accept` line success-3; the latency file alone; unit `test_w2_13_rerank_work.py` | `gov accept`; `pytest tests/acceptance/W2-13/test_w2_13_latency.py` through `heavy_slot.sh` | pass, 25 of 25 alone (load 1.6 at its start); under load (the scoped run beside it, load near 20): 24 of 25, the one red the load-sensitive latency case; the latency file alone: 2 of 2 (load 1.1 at its start; 261 s, the real-model case's call 14.2 s after a 189 s setup, the lexical case 57.7 s) | `06e5ae70a4a7` (`gov accept`); `3c0320080829` (latency alone) |
| S4 an id that exists nowhere: the stated gap | `gov accept` line success-4; unit `tests/unit/retrieve/test_w2_13_stated_gap.py` | `gov accept`; unit | pass, 8 of 8; unit pass (one case's double fixed for the merge, below) | `06e5ae70a4a7` |
| S5 search respects role separation (DEC-1065 (2)): every route of `gov retrieve` and `gov context`'s supplementary block filtered by the caller's role_paths; what is withheld named by count and rule; no section, no filter | `gov accept` line success-5 (the designer's tests at `5828714c`, merged by the CTO; not yet run); unit `tests/unit/guard/test_role_paths.py`, `tests/unit/retrieval/test_w2_13_role_filter.py` (S5 below) | `gov accept`, after the CTO's merge; unit: `PYTHONPATH=<tree>/src bash heavy_slot.sh python3 -m pytest tests/unit/guard/test_role_paths.py tests/unit/retrieval/test_w2_13_role_filter.py tests/unit/context tests/unit/retrieve` | unit pass: 30 of 30 for S5 (with review S5-F1's three, `6e6922439577`); with `tests/unit/context` and `tests/unit/retrieve`, 120 passed; `gov accept` (the CTO, outside the sandbox, on `78bf6b34`): 67 of 68, S5 11 of 12, the red `test_engineer_context_supplementary_holds_none_of_its_own_tickets_acceptance_tests[flag]` (`gov context --role`); fixed by `f54decffcaf3` (the role through `context()` to the block) and `23bef297a204` (`command.py` passes the parsed `--role`); `gov accept` re-run: the CTO's, outside the sandbox | `5b42e9810996`; `f54decffcaf3`; `23bef297a204` |
| S6 the keyword index honours the path map's `lexical_policy` (DEC-1066 (3), G4): `not indexed` keeps a namespace's files out (absent: indexed); the validators accept the field's two values; a file kept out is named in the rebuild's report | `gov accept` line success-6 (the designer's tests, once merged); unit `tests/unit/retrieval/test_w2_13_lexical_policy.py` (S6 below) | `gov accept`, after the CTO's merge; unit: `PYTHONPATH=<tree>/src python3 -m pytest tests/unit/retrieval/test_w2_13_lexical_policy.py --optin=lifted,breadth` | unit pass, 15 of 15, with `tests/unit/rebuild` 79 passed (the rebuild's report, S6 below); at `c134cf0e81dd`, `tests/unit/{retrieval,retrieve,check,secrets_check,rebuild,store,semantic}` through `heavy_slot.sh` (the real-model exclusion, `HOME` empty): 407 passed, 17 failed, all `test_w2_112_shared_reranker.py`, the same 17 red on the base `c2be9ccd` (the sandbox makes no reranker socket); `gov accept` (the designer's tests merged at `7a31f1e5`): the CTO's, outside the sandbox; the two `test_the_repository_marks_the_evaluation_sets_own_documents_not_indexed` cases stay red until D-7's path-map edit (the CTO's, after W2-13 merges) | `c134cf0e81dd`; the rebuild-report commit |
| F1 RETR-A-04's bundle unchanged | `gov accept` line failure-1 | `gov accept` | pass, 3 of 3 | `06e5ae70a4a7` |
| F2 the secrets filter on the FTS5 table: a planted canary never indexed | `gov accept` line failure-2, after DEC-1045's change to `lexical.py` on integrate (merged without conflict) | `gov accept` | pass, 4 of 4 (both runs) | `06e5ae70a4a7` |

The two builder tests changed for the merge (`06e5ae70a4a7`), each the smallest fix inside the ticket's paths:

- `tests/unit/retrieve/test_w2_13_stated_gap.py`, the no-database case: since W2-92, `retrieve()` keeps a record
  graph that cannot be read to the record and closure routes, so the semantic route is asked next; the case's double
  answered from a store that is no database, and the gathering met a chunk the lexical index did not hold
  (`KeyError`). The case now asks the real semantic route, which reads the store before any endpoint and fails as the
  real one does: `gov retrieve` exits 1 with `STORE_UNREADABLE` and no traceback, as before (also checked with the
  real CLI and no doubles on a tree whose store is no database).
- `tests/unit/retrieval/test_w2_92_routes.py`, the missing or unreadable record store case: the evidence's routes
  are now `["lexical", "code"]`, not `["code"]`: the ranked lexical route holds the question's word beside the code
  route's span (S2, the change this ticket makes).

## S5: search respects role separation (DEC-1065 (2); the round of 2026-11-03, `5b42e9810996`)

- **The matcher:** `src/gov/guard/role_paths.py`, the hook's path checks (`.claude/hooks/role_reads.py`: `section`,
  the placeholders `{ticket_tests}` with linked tests and `{ticket_impl}` with the (c3) shared files, `expand`,
  `Judge`, `judges`) as a product module; the hook's reading of shell commands is not in it, and the hook is
  unchanged (it may reuse the module later). The caller: `GOV_ROLE`, a `--role` beside it (it adds a filter, never
  lifts the session's), `GOV_TICKET`; the section from the main tree's path map, the ticket from the searched tree.
- **Where it applies:** in `retrieve()`, on every route's hits (lexical, semantic, closure, code) just before the
  fusion, rather than on the chunk list alone: the lexical and semantic lists are not built from that list, so a
  withheld hit would otherwise still take a rank and show its path in `gaps`. In `gov context`, in
  `supplementary._ranked`, before a chunk is ranked.
- **Named, never silent:** the bundle's `role_filter` (roles, ticket, rule, `withheld` paths and chunks, `by` rule
  and glob), also on the stated-gap bundle; the supplementary block's `role_filter` and one `dropped` entry with id
  `role_filter`, which the packet already carries. No section, no role the section names, or no rule the ticket
  fills: no filter and no `role_filter`, so today's bundles are unchanged.
- **`gov context --role` (the CTO's red on `78bf6b34`; `f54decffcaf3`):** `context(..., role=)` hands the role
  given to `_try_supplementary` and `supplementary.stack`, beside `GOV_ROLE` (it adds, never lifts); unit
  `test_gov_context_with_role_given_withholds_the_engineers_tests_and_names_it`. The parsed `--role` is on `args`
  only in `src/gov/context/command.py`'s `run`; once the CTO added it to the paths, its `context(...)` call passes
  `role=getattr(args, "role", None)` (`23bef297a204`); unit `test_gov_context_command_passes_role_through_to_the_block`.
- **Review S5-F1, the packet's own ticket (`6e6922439577`):** `gov context <ticket>` judges `<ticket>` as well as
  `GOV_TICKET` (`role_paths.caller(also=)`, `supplementary.stack(ticket=)`): the union of their rules, which can only
  add. A packet built from another ticket's session (the CTO's, under W2-00) or with no `GOV_TICKET`, for an
  engineer of `<ticket>`, now withholds `<ticket>`'s tests; a lead's own packet (`GOV_TICKET` is the packet's
  ticket) is judged once, as before. Unit `test_a_packet_built_from_another_tickets_session_judges_the_packets_own_ticket_too`,
  `test_a_leads_own_packet_is_unchanged_by_the_packets_ticket`, `test_the_tickets_also_judged_add_their_rules_and_never_lift_one`.
  `_try_supplementary` takes the ticket as a positional argument, as `tests/unit/context/test_all_external.py`'s
  stand-in (`lambda *args`) expects.
- **Fails closed:** a section or ticket that cannot be read stops `gov retrieve` with `ROLE_PATHS_UNREADABLE`; the
  supplementary block is then empty and its `dropped` says why.

## S6: the keyword index honours the path map's `lexical_policy` (DEC-1066 (3), G4)

- **The field:** a namespace's optional `lexical_policy`, `indexed` or `not indexed`; absent is `indexed`, as before.
  `gov.config.loader` refuses any other value (`CONFIG_INVALID`, in both forms of the path map) and `core-pathmap`
  (`gov.check.pathmap`, now 1.2.0) reports it as `PATH_MAP_INVALID`: a misspelt exclusion never leaves its files
  indexed. The path map itself is not changed here: which namespaces say `not indexed` (lens B's report,
  `fixtures/evaluation/**`) is D-7's, the CTO's.
- **The index (`src/gov/retrieval/lexical.py`):** `kept_out(root, paths)` names, for each path, the namespace saying
  `not indexed` that matches it (a link also by its target). `_update` asks it before the secrets filter, so a file
  kept out is neither given to the filter nor read. It is recorded in `lexical_file` with `indexed = 2` (`KEPT_OUT`;
  0 stays the filter's refusal). The path map is one of the filter's judges, so a change of policy judges every file
  again: a file newly kept out loses its chunks, and a file indexed again is chunked. The semantic vectors are built
  from the lexical chunks, so a file kept out reaches neither index.
- **The report:** `lexical.refresh()` returns `kept_out` (namespace to its sorted paths, every file kept out, not only
  this call's). **The rebuild's report** (`src/gov/rebuild/command.py`, added to the paths by the CTO's P2, `a3b4a817`):
  `stores["lexical"]` carries `kept_out` beside `"status": "recreated"`. One difference from the line as approved:
  `kept_out` is added only when a file is kept out, so where none is the report is exactly as before. The approved
  form (`lexical_refresh(root)["kept_out"]`, always present) turns four rebuild test files outside the paths red:
  `tests/unit/rebuild/test_compaction.py`, `test_w2_76_lock_override.py`, `test_w2_76_watch.py` and
  `test_no_embeddings.py` stand `refresh` in with `None`, and `test_no_embeddings.py` asserts the lexical store as
  `{"status": "recreated"}` exactly. The commit-time re-index (`src/gov/store/loader.py:444`) does not carry it; S6
  does not ask for that.
- **Unit tests** (`tests/unit/retrieval/test_w2_13_lexical_policy.py`, 15; stand-ins for the secrets filter, the
  record store and the code index; no model): the rebuild names each file kept out under its namespace, also on a
  rebuild of a fresh index, and its report is unchanged where nothing is kept out;
  a namespace `not indexed` keeps its files out, unread and not asked of the filter, and `refresh` names them; absent
  or `indexed` is indexed; a change of policy drops and restores the files; a link to a file kept out is kept out; an
  invalid value is `CONFIG_INVALID` and `search` answers `unreadable` instead of raising; both validators accept the
  two values and absence, and refuse five other values.
- **Builder fixtures:** `kept_out` validates only the namespaces' `lexical_policy` and reads the path map with
  `read_yaml` (not `load_config`): the secrets filter already loads and validates the whole path map for every file it
  judges, and the W2-87 and S5 fixtures plant a path map with no `namespaces` beside a stand-in filter.

## S2: the dev queryset's lexical-only hit@5

The lexical route alone, asked each of the dev queryset's 52 questions (`~/gov-os-workbench/synthetic/dev-queryset.yaml`,
tiers `a-dev` and `b-dev`, each cloned and adopted as `gov.retrieval.retrieve_check` does, the lexical index refreshed
only). hit@5: a `must_cite` path among the first five distinct paths of the list the route hands the fusion
(`ranked` where the code has one, else `hits`); the figure is the mean over the ten classes, as `retrieve_check`
computes it. The script is the lead's `.gov-runtime/scratch/lead/lexical_hit5.py` (in the worktree), run unchanged.

```
PYTHONPATH=<code> bash .gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
    python3 lexical_hit5.py ~/gov-os-worktrees/W2-13
```

| | Code (`PYTHONPATH`) | Questions hit | lexical-only hit@5 | Exact route (`hits`) only | Raised | p95 per question |
|---|---|---|---|---|---|---|
| base | `w2/integrate` at `5522a603dead` (`git archive 5522a603 src`) | 0 of 52 | 0.0 | 0.0 | 0 | 0.002 s |
| head | the worktree at `3c0320080829` | 45 of 52 | 87.0 | 0.0 | 0 | 0.003 s |

Head per class: decisions 100.0, failed-approaches 100.0, tests 80.0, stale-evidence 83.3, current-vs-superseded
100.0, deletable 60.0, callers-impact 100.0, where-defined 83.3, why 80.0, history 83.3. The lead's figure before the
merge was 85.0 (44 of 52, at `febe5f6403d5`). The base has no ranked list: its exact route hits no dev question in its
first five paths, as the head's `hits` alone do not either.

The fusion's contribution (lexical, semantic and the reranker each contributing, S2's other half) is not measured
here: measure: D-4b measure 1.

## The scoped run

`PYTHONPATH=<tree>/src python3 .gov-runtime/scratch/orchestrator/tools/select_tests.py <tree> W2-13 DAEO-zqvn`
(scope `scoped`, base `5522a603dead`, 90 targets), then `pytest tests <its pytest_options> -n auto -o
tmp_path_retention_policy=failed -p no:cacheprovider` through `heavy_slot.sh`, at `3c0320080829`: 5085 passed,
32 failed, 8 skipped, 20 errors in 1087 s, under load (`gov accept` beside it; load near 20).

- **Three reds were the merge's,** in two builder tests: fixed at `06e5ae70a4a7` (above); both files then pass,
  51 of 51.
- **The other 29 failed and 20 errors: 13 are W2-13's (corrected after the review, R2).** A first control re-ran
  their 18 files with `PYTHONPATH` swapped to `git archive` copies of the base's code and found the same 46. That
  control was invalid for W2-92, W2-87, W1-21, W1-19 and W1-28: their support modules start their children with
  their own tree's `src` (DEC-732), so all three runs ran the head's code there. The S2 hit@5 base figure above is
  not affected: `lexical_hit5.py` imports `gov` in its own process, with no child.
- **The control, redone against a real checkout:** the five suites (`tests/acceptance/W2-92`, `W2-87`, `W1-21`,
  `W1-19`, `W1-28`, `-n auto`, through `heavy_slot.sh`), run one after the other, in the worktree with its own
  `src`, and in a `git clone` of `w2/integrate` at `7524fa04` (its `src/` and these suites the same as at
  `5522a603dead`) with that clone's `src`:

  | tree | result | reds |
  |---|---|---|
  | `w2/integrate` `7524fa04` | 4 failed, 369 passed | integrate's own: W1-19 `embedding_policy`, `semantic_index`, the reranker-process case; W1-28's whole-tree copy case |
  | W2-13 head `80cdd7ff` | 17 failed, 356 passed | the same 4, plus the 13 below |

- **The 13 are W2-13's, by design:** S2 changes the lexical list the fusion takes. 11 pin the old lexical
  behaviour, and the test designer re-pins them next (MR-3):
  - W2-92 `test_w2_92_unchanged.py`: `test_u1_a_question_naming_no_record_or_symbol_gets_todays_bundle` `[plain]`,
    `[batched]`, `[unknown id]`, `[ticket]`; `test_u2_todays_bundle_is_the_plain_fused_order_of_todays_routes`.
  - W2-92 `test_w2_92_fail_closed.py`: `test_f4_a_question_naming_no_symbol_does_not_report_the_code_route_ok_or_fail`.
  - W2-87 `test_w2_87_authority.py`: `test_2b_a_lower_chunk_better_by_more_than_the_lift_keeps_its_place`,
    `test_3b_without_the_block_the_order_is_the_plain_fused_one`.
  - W1-21 `test_w1_21_family_check.py`: `test_the_check_is_red_when_the_dev_tiers_fail_the_baselines` (its
    premise, dev tiers below the 80 baseline, no longer holds: the ranked route lifts them over it).
  - W1-19 `test_w1_19_unavailable.py`: `test_a_reranker_that_cannot_be_loaded_leaves_the_fused_list_and_says_so`,
    `test_with_the_environment_and_no_snapshot_nothing_is_reranked_nothing_is_fetched_and_nothing_raises` (their
    reference order is built from `hits`, not `ranked`).

  The other 2 are the budget gap (review R3): W2-92
  `test_u4_a_batched_answer_with_a_new_route_continues_to_its_end_within_the_budget` and W1-21 `test_w1_21_expansion.py`
  `test_a_parent_that_does_not_fit_the_bundle_budget_is_not_expanded`. They are **not fixed on this head.** A cut of
  the gathered chunks to the budget (`ea486253`) made both pass, but it turned 11 W1-21 cases red
  (`test_w1_21_paging.py`: 8; `test_w1_21_merge.py`: 3). Those cases hold DEC-419 DP-3, W1-21's approved spec: "the
  bundle budget ... bounds parent expansion only; a child hit is never dropped for it". The cut was reverted
  (`80cdd7ff`), and the choice went to the CTO as a decision package (DEC-105).
- **Not re-run against a real checkout:** W2-108's 20 errors (its support takes `PYTHONPATH`, so the first control
  is valid for it: integrate's own), W2-55's 3 (red on clean `w2/integrate` in the review's run: integrate's own),
  W2-59's 4, W1-06's 1 and W2-54's 1 (attribution unverified).
