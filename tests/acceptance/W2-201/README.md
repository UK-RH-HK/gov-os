# W2-201 (DAEO-k1us) acceptance tests: the rubric in code (K1, RT-8) and audit 09's usage rules held by code

Written by the independent test designer from the ticket's KPI lines S1 to S8 and F1 to F3, each with its Verify, and
its `## Interface` section, before the implementation (MR-3). Sources read: DEC-1212, DEC-1214 (K1), audit 4's Table 3
(`docs/emergency-2/audits/04-tickets-and-rubric.md` lines 170-195), audit 09, the night's common brief, and the code
on the base as it stands (`gov.launch.role`, `gov.launch.criticality`, the launcher's signatures, the hook). Nothing of
the engineer's work on this ticket was read (there was none on the branch beyond the ticket).

## How the tests reach the product

* **Role files (S1, F3):** `gov.launch.role.launch_default` and `read_by_criticality`, on each of this repository's role
  files (`template/governance/kernel/roles/`) and generated copies (`.rulesync/subagents/`,
  `template/.rulesync/subagents/`, `.claude/agents/`), each copy planted alone in a temporary tree where the reader reads
  a role file. The expected values are `w2_201_support.TABLE`, S1 word for word (C0 `claude-haiku-5-5`, effort low,
  "as today").
* **Criticality (S2, S5's table):** `gov.launch.criticality.ticket_criticality` on this repository's own
  `governance/project/criticality.yaml`, with a ticket built as a front-matter map (profile STANDARD unless named).
* **`gov launch` (S3, S4, S7, S8, F2):** W2-184's support module and, through it, W2-60a's: a temporary HOME, an open
  resource gate, a fixture git project, the stand-in CLI at `~/.local/bin/claude` that records its arguments, process
  environment and `--settings`, and the launch record folder. S3 plants this repository's own kernel role file for the
  role launched (with fixture copies of the skills it names, the kernel's `judging-work` and a template copy); S4, S7,
  S8 and F2 use W2-184's fixture role tables. The lead of S7 is started by `gov launch lead <ticket>` through the console
  script, admitted by a planted ready list (`governance/project/orchestration/ready.txt`, line form `<W2> <id> <brief>
  <log>`); no private function is called.
* **The hook (S5, S6, F1):** `python3 -I .claude/hooks/agent_model.py` (the command `.claude/settings.json` runs) as a
  subprocess, one PreToolUse event as JSON on stdin, `CLAUDE_PROJECT_DIR` a project planted in `tmp_path` (fixture
  tickets, a fixture rubric: C3 `src/critical/*`, C2 `src/*`, C1 `docs/*`, FULL at least C2; an exceptions file listing
  the four roles on `opus` with `class: C3`), its working folder another, empty one. A refusal is exit 2 with a reason on
  stderr; let through is exit 0 with nothing on stdout. S5's last case copies the real rubric and exceptions files into
  the project and compares the hook's outcome with `ticket_criticality`'s class (outcomes only; the hook stays
  standalone).

## Words pinned (where the ticket states them) and left open

* Hook, class refusal: the ticket id, its class and `C3 work only`. No `Task:` line or two different ids: `Task:`. Fork:
  `a fresh helper from a written brief` and `DEC-1212 (4)`. A missing ticket, an unlisted type and F1's faults: exit 2
  and a non-empty reason, no words pinned (the ticket names none).
* Launcher (S4): `LAUNCH_REFUSED` (exit 1, no session, no record) naming the model asked for (`claude-opus-5-5`), the
  class and `governance/project/model-exceptions.yaml`; for an unusable exceptions file, the file. S8: `LAUNCH_REFUSED`
  naming the settings file and the command's key words (`stop_waiter_check`, `stop_idle_check`, `gov session-watch`,
  `gov msg wait`).
* Records: `model_source` `exception` and `exception` = the entry's `decided` text (S4), `exception` null otherwise;
  `cache_ttl` `5m` (S7); S3's keys are RT-8's (`model`, `model_source`, `effort`, `effort_source`, `criticality`,
  `rubric`). No key order, no other wording.

## The tests per KPI line (each item is a test function; `gov accept` counts every parametrised case of it)

The folder: 188 cases, 106 red and 82 green on the base (146ad302e). A green case on the base is a guard: the part of the
line that already holds there (named in the last column), kept so that the change cannot break it.

S9 was added after DEC-1215 by a second designer (one file, `test_w2_201_s9_substitution.py`; helpers appended to
`w2_201_support.py`, none changed): 40 cases, 15 red and 25 green on the base (864861428), beside the count above.

| KPI | tests | cases | expected red reason (on the base) |
|---|---|---|---|
| S1 | `test_w2_201_s1_role_files.py::test_s1_each_role_file_and_copy_gives_the_table_s_model_and_effort_per_class`; `test_w2_201_s1_role_files.py::test_s1_the_kernel_folder_holds_the_nine_roles_of_the_table` | 36 (9 roles x the kernel folder and 3 copies) + 1 | orchestrator and senior-engineer read Sonnet, not Opus; independent-auditor reads an Opus default and no table line; qa-engineer's C2 on FULL reads Opus (16 red). engineer, independent-test-designer, ticket-lead, product-spec and research already match (20 guards); the roster case is a guard |
| S2 | `test_w2_201_s2_criticality.py::test_s2_a_ticket_on_a_listed_path_is_c3`; `test_w2_201_s2_criticality.py::test_s2_a_ticket_on_the_retired_machinery_is_not_c3`; `test_w2_201_s2_criticality.py::test_s2_other_src_is_c2_docs_c1_and_a_full_ticket_at_least_c2` | 16 + 8 + 4 | close, accept, queue, landing, tasks queue, merge queue, memaudit, `fixtures/evaluation/**`, release, update, lock give C2 (C1 for the merge queue), not C3 (11 red; kernel, governance kernel, Contract, landing check and path map are C3 already: 5 guards); the guard, hooks, settings, local settings, secrets, walls, held-out and operator paths are still C3 (8 red); C2, C1 and the FULL floor are guards (4) |
| S3 | `test_w2_201_s3_launch_rubric.py::test_s3_engineer_and_test_designer_run_opus_on_c3_and_sonnet_on_c2`; `test_w2_201_s3_launch_rubric.py::test_s3_independent_auditor_runs_sonnet_on_c2_and_opus_on_c3`; `test_w2_201_s3_launch_rubric.py::test_s3_qa_engineer_runs_sonnet_on_a_full_c2_ticket`; `test_w2_201_s3_launch_rubric.py::test_s3_without_a_criticality_file_the_role_default_applies_and_rubric_is_null` | 4 + 2 + 1 + 2 | the auditor runs Opus with source `role default` (its kernel file has no table); the QA engineer runs Opus on a FULL C2 ticket; without a criticality file the auditor's default is Opus (4 red). The engineer and test designer cases and the engineer's no-file case are guards (5) |
| S4 | `test_w2_201_s4_exceptions.py::test_s4_an_engineer_asking_opus_on_a_c2_ticket_is_refused_naming_model_class_and_exceptions_file`; `test_w2_201_s4_exceptions.py::test_s4_an_exceptions_file_with_no_entry_for_the_role_still_refuses`; `test_w2_201_s4_exceptions.py::test_s4_an_entry_for_the_engineer_and_opus_starts_it_on_opus_and_records_the_exception`; `test_w2_201_s4_exceptions.py::test_s4_an_entry_with_class_c3_lifts_the_refusal_on_a_c3_ticket`; `test_w2_201_s4_exceptions.py::test_s4_an_entry_with_class_c3_does_not_lift_the_refusal_on_a_c2_ticket`; `test_w2_201_s4_exceptions.py::test_s4_the_exception_key_is_null_in_a_launch_that_takes_no_exception`; `test_w2_201_s4_exceptions.py::test_s4_an_unusable_exceptions_file_refuses_a_launch_asking_another_model`; `test_w2_201_s4_exceptions.py::test_s4_an_unusable_exceptions_file_does_not_touch_a_launch_asking_no_model` | 1 + 1 + 2 + 1 + 1 + 1 + 5 + 5 | the refusal (W2-184's) does not name `governance/project/model-exceptions.yaml`; a launch with an entry is refused (no exceptions route); the record has no `exception` key (all 17 red) |
| S5 | `test_w2_201_s5_hook_class.py::test_s5_an_opus_spawn_for_a_c3_ticket_is_let_through_for_each_of_the_four_roles`; `test_w2_201_s5_hook_class.py::test_s5_an_opus_spawn_for_a_c2_ticket_is_refused_naming_the_ticket_its_class_and_c3_work_only`; `test_w2_201_s5_hook_class.py::test_s5_a_claude_opus_model_id_is_judged_as_opus`; `test_w2_201_s5_hook_class.py::test_s5_an_opus_spawn_for_a_c1_or_full_docs_ticket_is_refused`; `test_w2_201_s5_hook_class.py::test_s5_the_ticket_s_class_key_is_never_read`; `test_w2_201_s5_hook_class.py::test_s5_the_highest_matching_rule_gives_the_class`; `test_w2_201_s5_hook_class.py::test_s5_an_entry_without_a_class_is_not_limited_to_c3`; `test_w2_201_s5_hook_class.py::test_s5_the_task_tool_name_is_judged_as_the_agent_tool`; `test_w2_201_s5_hook_class.py::test_s5_an_opus_spawn_with_no_task_line_is_refused_naming_the_task_line`; `test_w2_201_s5_hook_class.py::test_s5_an_opus_spawn_with_two_task_lines_naming_different_ids_is_refused`; `test_w2_201_s5_hook_class.py::test_s5_two_task_lines_naming_the_same_id_are_one_ticket`; `test_w2_201_s5_hook_class.py::test_s5_an_opus_spawn_naming_a_ticket_with_no_file_is_refused`; `test_w2_201_s5_hook_class.py::test_s5_an_opus_spawn_for_a_type_with_no_exception_is_refused`; `test_w2_201_s5_hook_class.py::test_s5_a_sonnet_or_no_model_spawn_is_let_through_whatever_the_ticket`; `test_w2_201_s5_hook_class.py::test_s5_the_real_exceptions_file_lists_the_four_roles_on_opus_for_c3_by_dec_1214_k1`; `test_w2_201_s5_hook_class.py::test_s5_the_hook_and_ticket_criticality_give_the_same_class_on_the_real_rubric` | 4 + 4 + 1 + 2 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 12 + 1 + 26 | the hook reads no ticket: it lets a listed type's Opus spawn through on a C2, C1 or unreadable ticket, and does not match `opus` to `claude-opus-5-5`; the real exceptions file lists two roles without `class`; on the real rubric it lets the engineer through on non-C3 rows and refuses the QA engineer (32 red). Let through on C3, the highest rule, an entry without a class, the same id twice, an unlisted type refused, Sonnet or no model, and the engineer's C3 rows of the table are guards (27) |
| S6 | `test_w2_201_s6_hook_fork.py::test_s6_a_fork_spawn_is_refused_naming_a_fresh_helper_from_a_written_brief`; `test_w2_201_s6_hook_fork.py::test_s6_an_exceptions_entry_for_fork_lifts_the_refusal`; `test_w2_201_s6_hook_fork.py::test_s6_an_entry_for_every_type_does_not_lift_the_fork_refusal`; `test_w2_201_s6_hook_fork.py::test_s6_a_general_purpose_spawn_is_judged_as_before` | 4 + 1 + 1 + 2 | a fork with no model or Sonnet is let through; a fork on Opus is refused by the model rule without the fork words; a `*` entry lets a Sonnet fork through (5 red). The fork entry's lift and the general-purpose cases are guards (3) |
| S7 | `test_w2_201_s7_cache.py::test_s7_a_worker_launch_sets_the_5_minute_cache_in_settings_environment_and_record`; `test_w2_201_s7_cache.py::test_s7_a_lead_started_by_the_launcher_does_not_get_the_5_minute_cache` | 6 (engineer, test designer, auditor, QA engineer, product-spec, research) + 1 | revised for the ticket's new S7 (7bba0fdb1): the variable is `CLAUDE_CODE_PROMPT_CACHE_TTL=5m`, and `FORCE_PROMPT_CACHING_5M` is in neither the settings' env block nor the CLI's environment. On the base the variable is already set for workers, and the record has no `cache_ttl` (6 red). The lead case (neither variable, no launch record) is a guard |
| S8 | `test_w2_201_s8_wake_hooks.py::test_s8_a_shipped_hooks_file_holds_no_wake_up_hook`; `test_w2_201_s8_wake_hooks.py::test_s8_a_worker_launch_with_a_wake_up_hook_in_the_repository_settings_is_refused`; `test_w2_201_s8_wake_hooks.py::test_s8_a_worker_launch_with_the_kernel_hooks_only_starts_and_its_settings_hold_no_wake_up_hook` | 4 + 4 + 1 | a worker launch whose settings hold a `Stop`, `SubagentStop` or `UserPromptSubmit` wake-up hook starts (4 red). The shipped files and the kernel-hooks launch are guards (5) |
| S9 | `test_w2_201_s9_substitution.py::test_s9_hook_active_a_fable_spawn_for_a_c3_ticket_is_let_through`; `test_w2_201_s9_substitution.py::test_s9_hook_active_a_fable_spawn_for_a_c2_ticket_is_refused_as_opus_is`; `test_w2_201_s9_substitution.py::test_s9_hook_active_a_fable_spawn_with_no_task_line_is_refused_naming_the_task_line`; `test_w2_201_s9_substitution.py::test_s9_hook_active_an_entry_without_a_class_lets_fable_through_with_no_task_line`; `test_w2_201_s9_substitution.py::test_s9_hook_active_an_opus_spawn_is_refused_with_the_fable_hint`; `test_w2_201_s9_substitution.py::test_s9_hook_active_a_fork_is_refused_as_in_s6`; `test_w2_201_s9_substitution.py::test_s9_hook_active_a_sonnet_or_no_model_spawn_is_let_through`; `test_w2_201_s9_substitution.py::test_s9_hook_not_active_a_fable_spawn_is_refused`; `test_w2_201_s9_substitution.py::test_s9_hook_not_active_an_opus_spawn_for_a_c3_ticket_is_let_through`; `test_w2_201_s9_substitution.py::test_s9_hook_not_active_an_opus_spawn_for_a_c2_ticket_is_refused_as_s5_says`; `test_w2_201_s9_substitution.py::test_s9_launch_active_an_engineer_on_a_c3_ticket_runs_fable`; `test_w2_201_s9_substitution.py::test_s9_launch_active_an_engineer_on_a_c2_ticket_still_runs_sonnet`; `test_w2_201_s9_substitution.py::test_s9_launch_active_a_caller_s_fable_with_an_opus_entry_starts_on_the_exception`; `test_w2_201_s9_substitution.py::test_s9_launch_active_an_entry_with_class_c3_does_not_lift_the_refusal_on_a_c2_ticket`; `test_w2_201_s9_substitution.py::test_s9_launch_active_an_entry_with_class_c3_lifts_the_refusal_on_a_c3_ticket`; `test_w2_201_s9_substitution.py::test_s9_launch_not_active_a_caller_s_fable_is_refused_even_with_the_opus_entry`; `test_w2_201_s9_substitution.py::test_s9_launch_not_active_an_engineer_on_a_c3_ticket_runs_opus` | 2 + 2 + 2 + 2 + 2 + 3 + 6 + 6 + 2 + 2 + 1 + 1 + 1 + 1 + 1 + 3 + 3 | with the substitution active the hook reads no ticket: it lets a Fable spawn through on a C2 ticket or with no `Task:` line (4 red); a fork with no model is let through and a fork on Fable or Opus is refused by the model rule without the fork words (3 red); with the substitution inactive or past its `until` an Opus spawn on a C2 ticket is let through (2 red); the launcher has no exceptions route, so a caller's `--model claude-fable-5-2` is refused with an entry that covers it (2 red) and its refusal does not name `governance/project/model-exceptions.yaml` (4 red): 15 red. Guards (25), DEC-1215's layer as it stands on the base: Fable let through on a C3 ticket and on an entry with no class (4), Opus refused with the Fable hint (2), Sonnet or no model (6), Fable refused with no file, `active: false` or a past `until` (6), Opus let through on C3 then (2), the C3 launch on Fable and the C2 launch on Sonnet (2), the C3 launch on Opus with no substitution in force (3) |
| F1 | `test_w2_201_f1_hook_unreadable.py::test_f1_a_fault_refuses_opus_and_lets_sonnet_and_no_model_through`; `test_w2_201_f1_hook_unreadable.py::test_f1_an_event_that_is_not_json_or_for_another_tool_exits_0` | 5 + 3 | with a criticality file that does not parse or is missing, a ticket whose front matter cannot be read, or no `.tickets`, the hook lets a listed Opus spawn through (4 red). The unparsable exceptions file (the base reads it as no exception and refuses) and the three events are guards (4) |
| F2 | `test_w2_201_f2_no_usage_brake.py::test_f2_a_worker_launch_with_plan_readings_at_100_percent_starts_with_the_same_record`; `test_w2_201_f2_no_usage_brake.py::test_f2_neither_the_launcher_nor_the_hook_names_a_usage_file` | 1 + 1 | guards (2): the line holds on the base and must keep holding |
| F3 | `test_w2_201_f3_line_checks.py::test_f3_a_missing_or_malformed_line_is_refused_by_the_role_reader` | 5 | guards (5): the reader refuses a missing, malformed or doubled default line and a table line without its C0 or C1 entry. The Verify's own cases are W2-33's F2 (`tests/acceptance/W2-33/test_w2_33_planted.py`, revised for DEC-1214 K1) and W2-184's line cases (`test_w2_184_s1_table.py`, `test_w2_184_s1_no_criticality_file.py`), run by their own folders |

## Readings (where the ticket is silent) and what is judged elsewhere

1. **S1, the copies.** A copy is read by planting it alone as the kernel file (the reader reads only that path); its
   values are compared with the table, so a copy that differs from the kernel file fails. W2-153's routed cases keep the
   byte-for-byte equality of the lines.
2. **S2, the not-C3 list.** The Verify names three paths; the same sentence's other old entries (local settings,
   secrets, walls, held-out, an operator file other than `landing_check.py`) are cases too. Not C3 is asserted, not
   the exact class (the default rule decides it).
3. **S4, the class-limited entry.** Shown with the test designer given a fixture role file with no table line and a
   Sonnet default, so Opus is another model in every class (on the fixture engineer's C3 entry Opus is the table's own
   model, which asks for no exception). An unusable exceptions file's refusal must name the file. "The trial and
   promotion routes of W2-184 stay as they are": W2-184's own cases (`test_w2_184_s2_model_and_trial.py`,
   `test_w2_184_s5_promotion.py`).
4. **S5, an entry with no `class`.** Not limited to C3, so a C2 ticket's Opus spawn passes; whether such an entry still
   needs a `Task:` line is left open (no case).
5. **S6, the fork entry.** Its lift is shown with a Sonnet fork and an entry `{subagent_type: fork, model: sonnet}`, true
   whether or not the entry's model must match; a `*` entry is not "an entry for `subagent_type: fork`".
6. **S7, the lead.** `gov launch lead` starts a lead on the stand-in when the ready list names the ticket; it gets neither
   cache variable and its launch writes no launch record. The QA engineer's worker launch is S3's (the kernel role file
   planted, an engineer's C2 ticket).
7. **F2.** The same record means: every key equal but the session's own (its id, times and process).
8. **S9.** The substitution file is planted in the real file's form with a fixed `until` (2099 for active and for
   `active: false`, 2020 for the passed one). Words pinned: S5's and S6's for Fable; for Opus while it is active,
   `DEC-1215` and `fable` (the hint). Fable refused without a substitution: exit 2 and a reason, no words. An `opus` entry
   with no `class` lets Fable through with no `Task:` line (the lead's reading for S9; reading 4 leaves the same open
   for Opus). The class-limited launcher cases use S4's test designer with no table line (reading 3); a caller's Fable
   refused: `LAUNCH_REFUSED` naming the exceptions file (and the class in the class-limited case), the model id not
   pinned. The launch on a substituted table entry pins `--model` and the record's `model` only.

## Run

```
TMPDIR=$(mktemp -d) PYTHONPATH=<tree>/src:<tree>/src/gov/close/pytest_plugin \
  bash <main tree>/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest tests/acceptance/W2-201 -q -p no:cacheprovider
```

About 35 s on the base. No network, no model, no store; each case builds what it needs in `tmp_path`.
