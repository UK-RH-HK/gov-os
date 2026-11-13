# W2-116 acceptance tests: the integration branch's store, double-buffered, refreshed after every merge

Ticket DAEO-f58b (W2-116), profile STANDARD; this pass is DEC-1087 (3)'s: S1, S3 (widened to every worker), S4,
S5 and the three failure lines. S2 (the two daily times and `gov status`) is the next pass and has no case here.
Written by the independent test designer (MR-3) from the ticket's KPI lines and its DEC-1087 (3) note, before any
implementation, reading only the integrated code (`w2/integrate`, DEC-963): `gov rebuild` and its seed (W2-122),
`gov launch`, `gov retrieve` and the freshness checks of `lexical.py` and `semantic.py`, and the CTO's present
`refresh_integration_store.sh`, which the product replaces.

## How they run

    env HOME=<an empty folder> PYTHONUSERBASE=$HOME_REAL/.local PYTHONPATH=<worktree>/src TMPDIR=<scratch> \
      python3 -m pytest tests/acceptance/W2-116 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

About 45 s on integrate (most cases stop at the first `--integration` build); about 100 s once every case runs.
**The code under test is whatever `gov` the pytest process imports (DEC-732):** every command is a child
`sys.executable -m gov.cli.main ...` with the pytest process's `PYTHONPATH`. Cases skip where `git`, `gitleaks` or
`sqlite_vec` is missing.

- **The planted project** (`w2_116_support.make_project`, one per case, under `tmp_path`): a git repository whose
  branch `integrate` is checked out, with the template's path map plus an embedded `docs/**` namespace, the
  template's gitleaks rules, `governance/project/rebuild.yaml` (a temporary `lock`; `integration_store` an
  absolute path outside the project, `<box>/stores/integration`), three notes with words of their own (`kept.md`
  *quillwort*, `changed.md` *bergamot*, `other.md` *marjoram*), two in-progress tickets (`DAEO-w901`, role
  engineer; `DAEO-w902`, role product-spec) and a `.claude/settings.json` that wires the guard, so `gov launch`
  accepts the project. **H2** is a `--no-ff` merge into `integrate`: `changed.md` gains *tamarind* and `merged.md`
  (*fenugreek*) is added; `kept.md` and `other.md` are unchanged.
- **Two stand-in endpoints, no model:** the build's (`OLLAMA_HOST`) and the questions' (`GOV_QUERY_OLLAMA_HOST`),
  each Ollama's HTTP interface on a loopback port, reporting the pinned model on the GPU, with vectors made of the
  words of each text. The build's records every text it is asked to embed (the embedder's calls are counted
  there) and can **hold** its answers: a build is then half-way, in its semantic stage, past the record and lexical
  stages. "No model" is a loopback port where nothing listens. Each command gets a new, empty vector cache
  (W2-126), so a cold build is cold in the cache too.
- **A build killed half-way:** the held build's process, its group and every process under it get SIGKILL.
- **Searching through the link:** `gov retrieve --json --root <integration_store> <question>`; the cases read the
  evidence's paths and the `facets` (`lexical`, `semantic`: `available`, `reason`).
- **`gov launch` with a stand-in CLI** at `<HOME>/.local/bin/claude`: it applies the settings' `env` block to its
  environment, as the CLI does for the session and its commands, runs a plain `gov retrieve --json <question>`
  (no `--root`) in the folder it was started in, and records the answer. No session is started.
- **The hand-built store** (`w2_116_support.hand_built_store`): the integration store as the CTO's script makes
  it today, without the product (a detached worktree of the branch's head outside the project, a full
  `gov rebuild` in it, the link at `integration_store` to it). The S3 cases and two S4 seed cases read it, so their
  red is their own line's and not S1's missing command.

## The interface the cases assume (the engineer builds to these names)

1. **`gov rebuild --integration <branch>`**, run in the project, with `--json` as every rebuild. The link is the
   path `integration_store` names in `governance/project/rebuild.yaml` (W2-122's key, the same path the seed
   reads). Where the two halves live is the engineer's: the cases only ask that the link's target be a detached
   worktree of the project outside it, and that there be exactly two.
2. **A seed from a store behind the head:** the `seed` object of `gov rebuild --seed` names the base's head commit
   (its full id or at least its first 12 hex digits) and says `behind`; a seed from a store at the tree's head does
   not say `behind`.

Not named, the engineer's to choose: how `gov launch` passes the store (the cases ask only that a plain
`gov retrieve` run in the session, with the session's environment, answers from it: an environment variable in the
settings' `env` block works; a `--root` the agent would have to type does not); the halves' names; how a failed
build is reported (a non-zero exit, `ok: false`, or a result whose semantic store is not `recreated`, with the word
`semantic` in the output).

## KPI lines, tests, and the outcome on `w2/integrate`

Run in the launch sandbox through the heavy slot, with `-m "not local_only" -k "not real and not green_here and not
time_limit"` (it leaves none of these out), on the branch point `fc61f303d467` and again on integrate's head
`e3355def9f99` (its `src` exported to scratch; W2-32's retrieval changes since): **20 tests, 16 failed, 4 passed**,
the same on both. Every red fails on its line's behaviour or on the missing `--integration` option, none on a
planted premise.

| KPI line | Test (node id) | On integrate | Why |
|---|---|---|---|
| success-1 | `test_w2_116_double_buffer.py::test_s1_the_build_keeps_the_branch_head_in_a_detached_worktree_outside_the_project_behind_the_link` | red | `gov rebuild` takes no `--integration`: a usage error, exit 2 |
| success-1 | `test_w2_116_double_buffer.py::test_s1_the_next_build_goes_into_the_other_half_and_the_two_alternate` | red | as above |
| success-1 | `test_w2_116_double_buffer.py::test_s1_failure2_a_search_during_a_build_is_answered_from_the_ready_half` | red | as above |
| success-1 | `test_w2_116_double_buffer.py::test_s1_failure2_freshness_a_search_through_the_link_while_the_other_half_rebuilds_is_never_stale` | red | as above |
| success-1 | `test_w2_116_double_buffer.py::test_s1_failure2_failure3_a_build_killed_half_way_leaves_the_link_and_the_ready_store_answers` | red | as above |
| success-2 | next pass (DEC-1087 (3)): the two daily times and gov status; no case in this pass | — | — |
| success-3 | `test_w2_116_launch.py::test_s3_every_worker_session_searches_the_integration_store_from_a_worktree_with_none[engineer]` | red | the session's plain search answers `STORE_MISSING`: the launch sets only `GOV_ROLE`, `GOV_TICKET` and the temp folder |
| success-3 | `test_w2_116_launch.py::test_s3_every_worker_session_searches_the_integration_store_from_a_worktree_with_none[independent-auditor]` | red | as above |
| success-3 | `test_w2_116_launch.py::test_s3_every_worker_session_searches_the_integration_store_from_a_worktree_with_none[independent-test-designer]` | red | as above |
| success-3 | `test_w2_116_launch.py::test_s3_every_worker_session_searches_the_integration_store_from_a_worktree_with_none[product-spec]` | red | as above |
| success-3 | `test_w2_116_launch.py::test_s3_failure1_a_designer_never_reads_the_ticket_worktree_s_own_store` | red | the designer's search in a ticket worktree with its own store gives the engineer's new note (`docs/engineer-new.md`) |
| success-3 | `test_w2_116_launch.py::test_s3_guard_the_launched_session_keeps_its_role_and_ticket` | green (guard) | the session's `env` keeps `GOV_ROLE` and `GOV_TICKET` and starts in the worktree |
| success-4 | `test_w2_116_refresh.py::test_s4_after_a_merge_the_refresh_brings_the_store_to_the_new_head` | red | no `--integration` |
| success-4 | `test_w2_116_refresh.py::test_s4_at_an_unchanged_head_the_refresh_does_nothing` | red | no `--integration` |
| success-4 | `test_w2_116_refresh.py::test_s4_the_refresh_after_a_merge_re_embeds_only_what_the_merge_changed` | red | no `--integration` |
| success-4 | `test_w2_116_refresh.py::test_s4_the_integration_store_is_the_warm_base_gov_rebuild_seed_reads` | red | no `--integration` |
| success-4 | `test_w2_116_refresh.py::test_s4_a_seed_from_a_store_behind_the_integration_head_is_named` | red | the seed from the hand-built store at H1, into a tree at H2, is `seeded` with `base`, `reason`, `copied`: no head, no `behind` |
| success-4 | `test_w2_116_refresh.py::test_s4_guard_a_seed_from_a_store_behind_the_head_re_embeds_only_what_changed` | green (guard) | W2-122's seed: only `changed.md` and `merged.md` are embedded |
| success-4 | `test_w2_116_refresh.py::test_s4_guard_a_seed_from_a_store_at_the_head_does_not_say_behind` | green (guard) | the seed says no `behind` today; it must not start to at the head |
| success-5 | `test_w2_116_reindex.py::test_s5_failure2_failure3_a_model_less_re_index_of_the_integration_store_keeps_its_index_and_says_so` | red | no `--integration` |
| success-5 | `test_w2_116_reindex.py::test_s5_guard_a_model_less_re_index_of_a_tree_keeps_its_vectors_and_reports_the_facet_unavailable` | green (guard) | a plain model-less rebuild keeps every vector and reports `semantic: not_recreated` with `EMBEDDER_UNAVAILABLE` |
| failure-1 | `test_w2_116_launch.py::test_s3_failure1_a_designer_never_reads_the_ticket_worktree_s_own_store` | red | as in success-3 |
| failure-2 | `test_w2_116_double_buffer.py::test_s1_failure2_a_search_during_a_build_is_answered_from_the_ready_half` | red | no `--integration` |
| failure-2 | `test_w2_116_double_buffer.py::test_s1_failure2_freshness_a_search_through_the_link_while_the_other_half_rebuilds_is_never_stale` | red | no `--integration` |
| failure-2 | `test_w2_116_double_buffer.py::test_s1_failure2_failure3_a_build_killed_half_way_leaves_the_link_and_the_ready_store_answers` | red | no `--integration` |
| failure-2 | `test_w2_116_reindex.py::test_s5_failure2_failure3_a_model_less_re_index_of_the_integration_store_keeps_its_index_and_says_so` | red | no `--integration` |
| failure-3 | `test_w2_116_double_buffer.py::test_s1_failure2_failure3_a_build_killed_half_way_leaves_the_link_and_the_ready_store_answers` | red | no `--integration` |
| failure-3 | `test_w2_116_reindex.py::test_s5_failure2_failure3_a_model_less_re_index_of_the_integration_store_keeps_its_index_and_says_so` | red | no `--integration` |

**What each case asks once `--integration` exists:**
- *the build keeps …:* the link's target is outside the project, a detached worktree at the branch's head, and a
  search through the link answers with both facets available.
- *the next build …:* H2's build switches to the other half and leaves the first at H1; H3's goes back into the
  first; exactly two worktrees, both detached.
- *a search during a build …:* with H2's build held half-way, the link has not moved, a search through it answers
  `kept.md` with both facets available and never `merged.md` (only H2 holds it); released, the build succeeds,
  the link switches, and `merged.md` is answered.
- *freshness …:* three questions through the link during the held build: both facets available, no reason, no
  `stale`.
- *killed half-way:* the link, the ready half's head and its vector count are unchanged; the ready store answers,
  never `merged.md`; the next build recovers and switches.
- *after a merge / unchanged head:* the refresh moves the store to H2; run again at the same head it leaves the
  link, the worktrees and each half's `store.db` byte for byte, and embeds nothing.
- *re-embeds only what the merge changed:* the refresh after H2 sends no text of `kept.md` or `other.md`, and
  sends `merged.md`'s.
- *the warm base:* a ticket worktree at the store's head, `gov rebuild --seed` with no folder: `seeded`, `base` the
  link's half, nothing embedded.
- *model-less re-index:* the H2 refresh with no model does not report success with a recreated semantic store,
  names `semantic`, leaves the link, the ready half's head and its vectors, and the ready store answers; with the
  model back the next refresh switches.

**A check of the tests themselves** (a scratch copy of `src`, never committed): a sketch of about 60 lines
(`--integration` alternating two halves `<link>-a` / `<link>-b`, each built by a child `gov rebuild --seed <ready
half>`, the link replaced only when that child is ok with its semantic store recreated; the launcher putting
`integration_store` in the session's env and `gov retrieve` reading it when no `--root` is given; the seed adding
the base's `head` and a `behind` sentence) passes all 20. A mutant of it that builds into the half in use and
switches on a failed build fails five: the alternation, the search during a build (`semantic: stale`), the
freshness case, the killed build (the ready half moved) and the model-less re-index.

## Notes and limits

- **N-1. The refresh re-embeds only what changed.** S4 says "only what changed since is re-embedded" of the seed;
  `test_s4_the_refresh_after_a_merge_re_embeds_only_what_the_merge_changed` reads it of the refresh too (its warm
  base is the ready half, as the CTO's script seeds the standby half from it). A refresh that builds the standby
  half cold fails it.
- **N-2. "A failed build" is a build whose semantic store is not recreated** (the CTO's script: "ok" with the
  semantic store not recreated is a failure and the link stays), or one killed half-way. A build that raises is
  not planted separately.
- **N-3. A designer's search with an explicit `--root <ticket worktree>`** is the guard's (DEC-820, the
  counterpart's work), not this ticket's; the cases ask only the session's plain search.
- **N-4. The session's search writes the question's vector cache beside the store** (DEC-782): through the link,
  into the ready half. Whether a sandboxed session may write there is not tested here (the stand-in CLI runs no
  sandbox).
- **N-5. S2 is the next pass:** no case asks for the daily times or `gov status`.

## Files

- `w2_116_support.py`: the planted project and its landings, the two stand-in endpoints, the commands, the link,
  the hand-built store, the searches and the stand-in CLI for `gov launch`.
- `conftest.py`: the case's box, the two endpoints, the environment, the project.
- `test_w2_116_double_buffer.py` (S1, F2, F3, freshness), `test_w2_116_launch.py` (S3, F1),
  `test_w2_116_refresh.py` (S4), `test_w2_116_reindex.py` (S5, F2, F3).

**D-10's red fix (2026-11-10, W2-20 `DAEO-r30l`, DEC-1088 (5)(b), DEC-1109):** `w2_116_support.launch_and_search` plants an open gate (`plant_open_gate`, W2-136's form) in the box's HOME and adds its readings to the launch's environment. Its six launch cases stay red after it, for another reason reported to the CTO: the session's cleaned environment (W2-56 S5) no longer carries `W2_116_SESSION_LOG` to the stand-in CLI. The gate is W2-20's, not under test here; no expectation changes. W2-20 S19 runs the resource gate on every `gov launch`; with no `gate.json` in the case's HOME it shuts, and with the machine's own it shuts under load.

**D-10's red fix, the cleaned session environment (2026-11-10, W2-116 `DAEO-f58b`, DEC-1112 (3); Rewrite-Reason DEC-826 Q5, DEC-877 item 4):** W2-56 S5 gives a launched session a cleaned environment, so no parent variable reaches the stand-in CLI: not `W2_116_SESSION_LOG` (its `KeyError`), nor the question, the stand-in endpoints or `PYTHONPATH`. The stand-in now has its log, its question and the case's environment written into it when the case plants it (`install_cli`); its search runs with the case's environment beneath the session's own environment and the settings' `env` block, so whatever the launch gives the session wins, as before W2-56 (the case's environment names no store). The fixture project also plants the eight `.claude/templates/<stem>.md` copies (W2-153, DEC-1050; W1-46's and W2-56's form): without them `gov launch` refused every case with `LAUNCH_NO_TEMPLATE` before the session ran. No assertion changes. On integrate `9ca161a6f` the six launch cases (`test_w2_116_launch.py::test_s3_every_worker_session_searches_the_integration_store_from_a_worktree_with_none[engineer]`, `[independent-auditor]`, `[independent-test-designer]`, `[product-spec]`, `test_w2_116_launch.py::test_s3_failure1_a_designer_never_reads_the_ticket_worktree_s_own_store`, `test_w2_116_launch.py::test_s3_guard_the_launched_session_keeps_its_role_and_ticket`) pass.

## Pass 2b: S2 (the two daily times, `gov status`) and R2-F3 (the continuation token carries the half)

Written by the independent test designer (MR-3) from the KPI line S2 and the CTO's stated interface
(`P-W2-116-S2-INTERFACE` Q1 (a), Q2 (b), Q3 (a), DEC-1157 (12); the same text as the engineer's brief), before and without
reading this pass's implementation. Added beside pass 1's files, which are unchanged: `w2_116_s2_support.py` (the
configuration with `integration_refresh`, `GOV_NOW`, verdict files by `os.utime`, the record, `gov status`, two folders
at one commit and the link between them), and four test files. `conftest.py` and `w2_116_support.py` are untouched.

**The interface the cases assume** (all from the brief; nothing else is pinned): `rebuild.yaml`'s
`integration_refresh: {branch, after_nightly: {verdict, latest}, second}`; `gov rebuild --json --integration <branch>
--when-due` (result `integration.status` `switched`/`unchanged` with `integration.reason` `after_nightly`/`second`, or
`{"integration": {"status": "not_due", branch, link, last_refresh}}`); the record `<link>.refresh.json`
(`at`, `reason`, `head`, `status`, `branch`); `REBUILD_CONFIG_INVALID` with `details.key` / `details.value`;
`gov status --json` `result.integration_store`; `gov retrieve --continue <token>` and `CONTINUATION_INVALID` naming both
folders. The clock is `GOV_NOW`. Cases of the due rule use a fixed day (2026-06-10/11, offset +00:00) and tick the
command with `GOV_NOW` moved on; the status cases plant `GOV_NOW` and the times relative to the build's real
`written_at`, in the UTC offset where the real clock reads about 12:00 (so no planted time crosses a midnight of the wall
clock `GOV_NOW`'s offset states).

### Map (KPI line S2)

| KPI | Tests (node ids) | Expected red reason (old code) |
|---|---|---|
| S2: two times read from the configuration | `test_w2_116_s2_when_due.py::test_s2_success_the_two_times_are_read_from_the_planted_configuration` | `--when-due` unknown: usage error, exit 2 |
| S2: refresh after the verdict, with the record | `test_w2_116_s2_when_due.py::test_s2_success_a_refresh_runs_after_a_newer_verdict_file_and_writes_the_record`, `::test_s2_success_a_json_verdict_file_newer_than_the_last_refresh_is_due`, `::test_s2_success_the_verdict_glob_defaults_to_docs_close_nightly_nr_json` | as above |
| S2: a file without a verdict / an older verdict is not due | `test_w2_116_s2_when_due.py::test_s2_failure_a_file_without_a_verdict_or_an_older_verdict_does_not_make_a_refresh_due` | as above |
| S2: latest without a verdict; once a day | `test_w2_116_s2_when_due.py::test_s2_success_latest_passes_without_a_verdict_and_the_same_day_is_not_due_again`, `::test_s2_success_a_second_refresh_does_not_stand_in_for_the_after_nightly_one`, `::test_s2_success_when_both_are_due_one_refresh_runs_with_reason_after_nightly` | as above |
| S2: the second time, once | `test_w2_116_s2_when_due.py::test_s2_success_second_is_due_once_after_its_time_and_brings_the_store_to_the_branch_head` | as above |
| S2: a missing or invalid time refuses by name | `test_w2_116_s2_config.py::test_s2_failure_a_missing_or_invalid_setting_refuses_by_name_and_builds_nothing` for ids `second-missing`, `second-empty`, `second-not-a-string`, `second-9-5`, `second-10am`, `second-25-00`, `second-24-00`, `second-12-60`, `latest-missing`, `latest-25-00`, `latest-10am`, `latest-not-a-string`, `branch-missing`, `no-integration-refresh`; `::test_s2_failure_an_invalid_now_refuses_by_name_and_builds_nothing` | `--when-due` unknown: exit 2, no `REBUILD_CONFIG_INVALID` |
| S2: scope of `--when-due`, plain refresh, failed refresh | `test_w2_116_s2_config.py::test_s2_failure_when_due_is_only_valid_with_integration` (red: argparse's usage error, not `REBUILD_FAILED`), `::test_s2_failure_a_plain_refresh_leaves_the_record_as_it_was`, `::test_s2_failure_a_failed_refresh_refuses_and_leaves_the_record_so_the_next_tick_is_due_again` (red: first tick unknown option), `::test_s2_failure_the_times_are_not_read_without_when_due_and_no_record_is_written` (**green on the old code, a guard**: a plain refresh already ignores the times and writes no record; it must not start to) | as above |
| S2: `gov status` head, age, stale | `test_w2_116_s2_status.py::test_s2_success_status_names_the_integration_store_s_head_and_age_and_a_fresh_store_is_not_stale`, `::test_s2_success_a_store_behind_the_branch_is_stale_and_the_reason_names_both_heads`, `::test_s2_success_a_store_built_before_latest_fell_due_is_stale_and_the_reason_names_the_time`, `::test_s2_success_a_store_built_before_a_verdict_file_is_stale`, `::test_s2_success_a_latest_that_a_verdict_already_answered_does_not_make_the_store_stale` | no `integration_store` part in `result` (the first case also fails earlier at its `--when-due` tick) |
| S2: unread parts, exit 0 | `test_w2_116_s2_status.py::test_s2_failure_no_store_configured_or_no_link_gives_an_unread_part_and_status_still_exits_0`, `::test_s2_failure_without_a_refresh_configuration_the_store_is_named_and_the_stale_judgement_is_unread`, `::test_s2_failure_an_invalid_time_leaves_the_stale_judgement_unread_naming_the_key` | no `integration_store` part |

### The ride-along: the continuation token carries the half (not a KPI line)

| Ride-along | Test (node id) | Expected red reason (old code) |
|---|---|---|
| token and the half | `test_w2_116_r2f3_continuation.py::test_r2f3_a_token_made_on_one_folder_is_refused_on_another_at_the_same_commit`, `::test_r2f3_a_token_made_through_the_link_is_refused_once_the_link_points_at_the_other_half`, `::test_r2f3_a_token_made_through_the_link_is_refused_on_the_other_half_used_directly` | the token is accepted on the other folder at the same commit (`ok: true`, exit 0) |
| guard | `test_w2_116_r2f3_continuation.py::test_r2f3_guard_a_token_used_on_the_folder_it_was_made_on_pages` | **green on the old code, a guard** |

### Red record (old code, `w2/W2-116-tests` at e51b1fdf6, through the heavy slot): 40 cases, 38 failed, 2 passed

Every `--when-due` case fails on `gov: error: unrecognized arguments: --when-due` (exit 2): the first tick of each case,
or, for the refusal cases, the expected `REBUILD_CONFIG_INVALID` envelope. Every `gov status` case fails on
`gov status has no integration_store part: ['config_files', 'decision_packages', 'doctor', ...]`. The two token cases
fail with `a token made on <a> was not refused CONTINUATION_INVALID on <b>` (exit 0, `ok: true`, a page of `docs/other.md`
from the other folder). Raw log: scratch `red1.log`.

### Check of the cases themselves

A scratch sketch of this pass (about 150 lines in a copy of `src`, never committed: `--when-due`, the record, the status
part, the token's mark) was written from the brief's text alone to check that the cases pass against a correct reading
of the interface and that a failure is the case's. It passes all 40 cases (2 min 2 s through the heavy slot). Its after_nightly
fallback keeps the last after_nightly refresh's time in an extra field of the record, which is how P2b-1 below is resolved in the
sketch; no case pins that field.

### Notes and limits

- **P2b-1. The after_nightly fallback and a single record.** The brief says the fallback is due when "no scheduled
  refresh with reason `after_nightly` has an `at` on today's date", and the record holds only the last refresh. After
  `after_nightly` at 10:05 and `second` at 18:05 the record's reason is `second`, so read literally the fallback is due
  again at 18:10, and at every tick until midnight. The cases pin the intent (a tick after `second` is `not_due`:
  `test_s2_success_second_is_due_once_...`, brief item 4) and no case asks what the record holds beyond its stated fields.
  The case that ticks after `latest` when an `after_nightly` refresh ran earlier the same day from a verdict file (09:00,
  then 10:05) is not planted: the literal rule and the "record's `at` before today's `latest`" rule differ there.
- **P2b-2. "Past `second`" with no earlier tick.** With no record, a tick past both times is `after_nightly`
  (`test_s2_success_when_both_are_due_one_refresh_runs_with_reason_after_nightly`), so reason `second` needs the day's
  `after_nightly` slot used first (or `second` before `latest`): the cases plant it so.
- **P2b-3. Not pinned:** the text of `stale_reason` beyond its code and the names it must carry (12 hex digits of both
  heads; the time as `HH:MM` in `GOV_NOW`'s offset or in UTC); the key of `after_nightly` missing altogether; a token
  without the mark (its form is the implementation's, so no case forges one); the order in which two invalid keys are
  reported; running under cron (window 4).
- **P2b-4. Unquoted times.** `second: 1800` (a number) is planted as "not a string"; an unquoted `18:00` is not, since
  the YAML reader's reading of it is the reader's.
