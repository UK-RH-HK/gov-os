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

S9 was added after DEC-1215 by a second designer (one file, `test_w2_201_s9_substitution.py`, deleted by the DEC-1225 revision below; helpers appended to
`w2_201_support.py`, none changed): 51 cases, 26 red and 25 green on the base (the tree of ae2b19ed7), beside the count
above; the last 11 (a caller's Opus) came with the ticket's S9 sentence of 7bba0fdb1. S7 was revised with it: 7 cases, 6
red and 1 green on the same base.

| KPI | tests | cases | expected red reason (on the base) |
|---|---|---|---|
| S1 | `test_w2_201_s1_role_files.py::test_s1_each_role_file_and_copy_gives_the_table_s_model_and_effort_per_class`; `test_w2_201_s1_role_files.py::test_s1_the_kernel_folder_holds_the_nine_roles_of_the_table` | 36 (9 roles x the kernel folder and 3 copies) + 1 | revised for DEC-1225 (R1): the table is Opus, high for orchestrator and senior-engineer and Sonnet, high with no table line for the other seven. On the base engineer, independent-test-designer, independent-auditor and qa-engineer carry a table line and read Opus at C3 (16 red: 4 roles x 4 places); the other 20 and the roster case are guards |
| S2 | `test_w2_201_s2_criticality.py::test_s2_a_ticket_on_a_listed_path_is_c3`; `test_w2_201_s2_criticality.py::test_s2_a_ticket_on_the_retired_machinery_is_not_c3`; `test_w2_201_s2_criticality.py::test_s2_other_src_is_c2_docs_c1_and_a_full_ticket_at_least_c2` | 16 + 8 + 4 | close, accept, queue, landing, tasks queue, merge queue, memaudit, `fixtures/evaluation/**`, release, update, lock give C2 (C1 for the merge queue), not C3 (11 red; kernel, governance kernel, Contract, landing check and path map are C3 already: 5 guards); the guard, hooks, settings, local settings, secrets, walls, held-out and operator paths are still C3 (8 red); C2, C1 and the FULL floor are guards (4) |
| S3 | `test_w2_201_s3_launch_rubric.py::test_s3_every_worker_runs_sonnet_high_at_every_class`; `test_w2_201_s3_launch_rubric.py::test_s3_qa_engineer_runs_sonnet_on_a_full_c2_ticket`; `test_w2_201_s3_launch_rubric.py::test_s3_without_a_criticality_file_the_role_default_applies_and_rubric_is_null` | 24 (6 worker roles x C3, C2, C1, C0) + 1 + 3 | revised for DEC-1225 (R2): every worker launches Sonnet, high at every class, the role file's default (this repository's kernel file planted); the source word is open. On the base the engineer, test designer, auditor and QA engineer run Opus at C3 and Haiku, low at C0 (8 red); the rest are guards |
| S4 | `test_w2_201_s4_exceptions.py::test_s4_an_engineer_asking_opus_on_a_c2_ticket_is_refused_naming_model_class_and_exceptions_file`; `test_w2_201_s4_exceptions.py::test_s4_an_exceptions_file_with_no_entry_for_the_role_still_refuses`; `test_w2_201_s4_exceptions.py::test_s4_an_entry_for_the_engineer_and_opus_starts_it_on_opus_and_records_the_exception`; `test_w2_201_s4_exceptions.py::test_s4_an_entry_with_class_c3_lifts_the_refusal_on_a_c3_ticket`; `test_w2_201_s4_exceptions.py::test_s4_an_entry_with_class_c3_does_not_lift_the_refusal_on_a_c2_ticket`; `test_w2_201_s4_exceptions.py::test_s4_the_exception_key_is_null_in_a_launch_that_takes_no_exception`; `test_w2_201_s4_exceptions.py::test_s4_an_unusable_exceptions_file_refuses_a_launch_asking_another_model`; `test_w2_201_s4_exceptions.py::test_s4_an_unusable_exceptions_file_does_not_touch_a_launch_asking_no_model` | 1 + 1 + 2 + 1 + 1 + 1 + 5 + 5 | the refusal (W2-184's) does not name `governance/project/model-exceptions.yaml`; a launch with an entry is refused (no exceptions route); the record has no `exception` key (all 17 red) |
| S5 | `test_w2_201_s5_hook_class.py::test_s5_an_opus_spawn_for_a_c3_ticket_is_let_through_for_each_of_the_four_roles`; `test_w2_201_s5_hook_class.py::test_s5_an_opus_spawn_for_a_c2_ticket_is_refused_naming_the_ticket_its_class_and_c3_work_only`; `test_w2_201_s5_hook_class.py::test_s5_a_claude_opus_model_id_is_judged_as_opus`; `test_w2_201_s5_hook_class.py::test_s5_an_opus_spawn_for_a_c1_or_full_docs_ticket_is_refused`; `test_w2_201_s5_hook_class.py::test_s5_the_ticket_s_class_key_is_never_read`; `test_w2_201_s5_hook_class.py::test_s5_the_highest_matching_rule_gives_the_class`; `test_w2_201_s5_hook_class.py::test_s5_an_opus_entry_without_a_class_or_any_limiter_lifts_nothing`; `test_w2_201_s5_hook_class.py::test_s5_the_task_tool_name_is_judged_as_the_agent_tool`; `test_w2_201_s5_hook_class.py::test_s5_an_opus_spawn_with_no_task_line_is_refused_naming_the_task_line`; `test_w2_201_s5_hook_class.py::test_s5_an_opus_spawn_with_two_task_lines_naming_different_ids_is_refused`; `test_w2_201_s5_hook_class.py::test_s5_two_task_lines_naming_the_same_id_are_one_ticket`; `test_w2_201_s5_hook_class.py::test_s5_an_opus_spawn_naming_a_ticket_with_no_file_is_refused`; `test_w2_201_s5_hook_class.py::test_s5_an_opus_spawn_for_a_type_with_no_exception_is_refused`; `test_w2_201_s5_hook_class.py::test_s5_a_sonnet_or_no_model_spawn_is_let_through_whatever_the_ticket`; `test_w2_201_s5_hook_class.py::test_s5_the_real_exceptions_file_holds_one_entry_the_auditor_on_opus_limited_by_dec_1230`; `test_w2_201_s5_hook_class.py::test_s5_the_hook_and_ticket_criticality_give_the_same_class_on_the_real_rubric` | 4 + 4 + 1 + 2 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 12 + 1 + 26 | the hook reads no ticket: it lets a listed type's Opus spawn through on a C2, C1 or unreadable ticket, and does not match `opus` to `claude-opus-5-5`; the real exceptions file lists two roles without `class`; on the real rubric it lets the engineer through on non-C3 rows and refuses the QA engineer (32 red on the original base; revised for DEC-1225: the Opus entry with no limiter now lifts nothing (red on this base), the real exceptions file holds one auditor entry limited by `decision: [DEC-1230]` (red), and the real-rubric parity cases copy the real rubric with the fixture entries (guards)). Let through on C3, the highest rule, an entry without a class, the same id twice, an unlisted type refused, Sonnet or no model, and the engineer's C3 rows of the table are guards (27) |
| S6 | `test_w2_201_s6_hook_fork.py::test_s6_a_fork_spawn_is_refused_naming_a_fresh_helper_from_a_written_brief`; `test_w2_201_s6_hook_fork.py::test_s6_an_exceptions_entry_for_fork_lifts_the_refusal`; `test_w2_201_s6_hook_fork.py::test_s6_an_entry_for_every_type_does_not_lift_the_fork_refusal`; `test_w2_201_s6_hook_fork.py::test_s6_a_general_purpose_spawn_is_judged_as_before` | 4 + 1 + 1 + 2 | a fork with no model or Sonnet is let through; a fork on Opus is refused by the model rule without the fork words; a `*` entry lets a Sonnet fork through (5 red). The fork entry's lift and the general-purpose cases are guards (3) |
| S7 | `test_w2_201_s7_cache.py::test_s7_a_worker_launch_sets_the_5_minute_cache_in_settings_environment_and_record`; `test_w2_201_s7_cache.py::test_s7_a_lead_started_by_the_launcher_does_not_get_the_5_minute_cache` | 6 (engineer, test designer, auditor, QA engineer, product-spec, research) + 1 | revised for the ticket's new S7 (7bba0fdb1): the variable is `CLAUDE_CODE_PROMPT_CACHE_TTL=5m`, and `FORCE_PROMPT_CACHING_5M` is in neither the settings' env block nor the CLI's environment. On the base the variable is already set for workers, and the record has no `cache_ttl` (6 red). The lead case (neither variable, no launch record) is a guard |
| S8 | `test_w2_201_s8_wake_hooks.py::test_s8_a_shipped_hooks_file_holds_no_wake_up_hook`; `test_w2_201_s8_wake_hooks.py::test_s8_a_worker_launch_with_a_wake_up_hook_in_the_repository_settings_is_refused`; `test_w2_201_s8_wake_hooks.py::test_s8_a_worker_launch_with_the_kernel_hooks_only_starts_and_its_settings_hold_no_wake_up_hook` | 4 + 4 + 1 | a worker launch whose settings hold a `Stop`, `SubagentStop` or `UserPromptSubmit` wake-up hook starts (4 red). The shipped files and the kernel-hooks launch are guards (5) |
| S9 | `test_w2_201_r3_limiters.py::test_r3_a_fable_spawn_is_refused_for_every_type_with_an_entry_naming_it`; `test_w2_201_r3_limiters.py::test_r3_a_planted_dec_1215_file_is_read_by_no_one`; `test_w2_201_r3_limiters.py::test_r3_a_fable_spawn_with_no_exceptions_file_is_refused_with_no_substitution_text`; `test_w2_201_r3_limiters.py::test_r3_a_launch_asking_fable_is_refused_with_an_opus_entry_whose_limiters_it_meets` | 10 + 2 + 2 + 2 | retired by DEC-1225 (R3): `test_w2_201_s9_substitution.py` is deleted (its 51 cases tested DEC-1215's substitution, whose file and readers are removed). What S9 kept true, that Fable is refused, is pinned for the hook and the launcher by these cases: an entry naming Fable lifts it on the base (10 red), the planted old file lets Fable through (2 red); with no file and for the launcher it is refused already (4 guards) |
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
   A caller's Opus while the substitution is active: `LAUNCH_REFUSED` naming `DEC-1215` and `fable`, with an entry
   (no class; `class: C3` on a C3 ticket), with no exceptions file, on a C2 and a C3 ticket, and for another
   `claude-opus-*` id (`claude-opus-4-7`). Without the substitution it is S4's, word for word.

## Fix: what becomes a ticket (DEC-1219 (5)), lines X1 to X5

Written by an independent test designer from the ticket's section `## Fix: what becomes a ticket (DEC-1219 (5))` (its
Interface paragraph and X1 to X5, each with its Verify), before the implementation (MR-3). Read besides: the base's
`gov launch` and `gov queue` code for their seams only (the stand-in CLI, the planted projects, the records, the
answer), W2-184's, W2-60a's, W2-202's and W2-115b's support modules, the kernel role files and the orchestration skill.
Nothing of the engineer's work on the fix was read. Five test files and two support modules beside the existing ones
(none of which is changed): `w2_201_x_support.py` (X1 to X3), `w2_201_x4_support.py` (X4).

**The map names X1 to X5 as `S10` to `S14`.** `gov accept` reads a KPI cell only as `success-N` / `failure-N`
(`S`, `F` or `K` and a number); a cell `X1` would refuse the whole map. So X1 is `success-10`, X2 `success-11`, X3
`success-12`, X4 `success-13` and X5 `success-14`, each row naming its X line in brackets.

**How the tests reach the product.**

* **X1 to X3:** `gov launch` through the console script on W2-184's fixture project and W2-60a's stand-in CLI (which
  records its arguments, the CLI process's environment and `--settings`), the launch record folder, W2-60a's open gate.
  The words of a launch are written as a caller writes them (the ticket optional, `--fix "<line>"` / `--chore
  "<line>"` before `--`). W2-184's fixture role files give every worker role the default (Sonnet, medium) and the
  engineer's table C3 (Opus, high), C2 (Sonnet, high): a fix's model and effort are told from its class, a chore's
  effort (medium) from any class's (high). A closed, open or in_progress ticket is W2-184's fixture ticket with its
  status line changed. The lead's plan is a committed ready list (S7's form) naming one in_progress ticket; the closed
  ticket is outside it. `gov pause` is run as the owner; the gate is shut by its memory reading (1 GiB available
  under the planted 3 GiB floor). A chore and a chore lead are launched with a caller's `GOV_TICKET` in `gov launch`'s
  own environment (a lead launching has one), so "absent, not empty" is shown against a value that could leak.
* **X4:** `gov queue <T>=<branch> ... [--dry-run] --json` on W2-115b's planted project (tickets with acceptance suites,
  `.tickets/**` record-only in the test map), each planted run built once per session under a lock with the fixtures'
  own check first (W2-206's way). The notices run lands A, B, C and E together, after a dry run of the same four: A
  adds `PROJ-nnew` (no `kpis.success` line with a verify, a blank body); B adds `PROJ-good` (a `{line, verify}` line)
  and `PROJ-strv` (a string line holding `Verify:`), each with a body; C edits D's existing ticket file into one with no
  verify and no body; E adds `PROJ-nobd` (verify, empty body), `PROJ-novf` (body, no verify), `PROJ-blnk` (a mapping
  line whose `verify` is blank) and `PROJ-unrd` (front matter that does not parse, a body). The plain run lands A with
  a widget change and no ticket file.
* **X5:** a repository-state case (it reads this repository's kernel files and copies, so it belongs to the
  record-reading set and runs after a record change): the `Tools:` line of `orchestrator.md`, `senior-engineer.md` and
  `ticket-lead.md` in `template/governance/kernel/roles/` and the `## Parallel tickets` section of
  `template/governance/kernel/skills/orchestration/SKILL.md`, and their copies.

**Words pinned and left open.** X1 to X3: the record's `kind` (`feature`, `fix`, `chore`), `kind_line` (the line as
given, null for a feature) and the keys X2 lists as null; `GOV_LAUNCH_KIND` and `GOV_LAUNCH_LINE` values; a chore lead's
`GOV_MSG_ADDRESS` `orchestrator:chore-<8 lower-case hex>` (today's address is `<GOV_ROLE>:<ticket>`, and X3 puts the
label "where the ticket would be"). A usage error: exit 2, no session, no record, and not argparse's `unrecognized
arguments` (on the base `--fix` and `--chore` are unknown options, which also end 2); no message words pinned. A
refusal that stays: `LAUNCH_REFUSED` (exit 1) with the words today's refusal has (`unknown ticket`, `is not
in_progress`, `another role`, the model and `governance/project/model-exceptions.yaml`); the pause names `paused`, the
gate `memory`. X4: the notice text whole, `NEW_TICKET_NOT_FEATURE <id>: ` and the missing parts joined by `; ` in the
ticket's order (`no kpis.success line with a verify` before `no spec (the ticket's body is empty)`); the entry's four
keys (`ticket` the landed candidate, `id` the new ticket, `code`, `notice`), other keys left open; the stderr line holds
the notice (any prefix). X5: `new ticket only for a new feature` in any letter case, `--fix` and `--chore` as written.

The fix's five files: 90 cases, 78 red and 12 green on the base (the tree of 8f9a4081a, through the heavy slot). A
green case is a guard: what holds today and must keep holding (named in the last column).

| KPI | tests | cases | expected red reason (on the base) |
|---|---|---|---|
| S10 (X1) | `test_w2_201_x1_fix.py::test_x1_an_engineer_launches_with_fix_on_its_ticket_whatever_its_status`; `test_w2_201_x1_fix.py::test_x1_the_same_launch_without_fix_is_refused_as_today`; `test_w2_201_x1_fix.py::test_x1_plan_with_fix_prints_the_role_s_default_line`; `test_w2_201_x1_fix.py::test_x1_plan_without_fix_on_a_closed_ticket_is_refused_as_today`; `test_w2_201_x1_fix.py::test_x1_tests_worktree_with_fix_makes_the_closed_ticket_s_tests_worktree`; `test_w2_201_x1_fix.py::test_x1_tests_worktree_without_fix_on_a_closed_ticket_is_refused_as_today`; `test_w2_201_x1_fix.py::test_x1_a_fix_on_an_unknown_ticket_is_refused`; `test_w2_201_x1_fix.py::test_x1_a_fix_keeps_the_role_to_its_own_ticket`; `test_w2_201_x1_fix.py::test_x1_a_fix_still_refuses_a_caller_s_other_model`; `test_w2_201_x1_fix.py::test_x1_a_fix_is_stopped_by_gov_pause`; `test_w2_201_x1_fix.py::test_x1_an_ordinary_launch_records_kind_feature_and_kind_line_null`; `test_w2_201_x1_fix.py::test_x1_a_usage_error_ends_2_before_the_launcher` | 4 (closed C3, closed C2, open C2, in_progress C2) + 2 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 2 (engineer, test designer) + 16 (8 usage cases x engineer, orchestrator) | `gov launch` has no `--fix`: argparse ends 2 with `unrecognized arguments: --fix ...`, so no fix starts, `--plan --fix` and `--tests-worktree --fix` print nothing, and the refusals that stay are exit 2, not `LAUNCH_REFUSED`; the usage cases end 2 as argparse's unknown option, not the usage rule; an ordinary record has no `kind` or `kind_line` (26 red). Guards (6): without `--fix` the launch, `--plan` and `--tests-worktree` on a closed ticket are refused `is not in_progress` (4); no flag and no ticket already ends 2 (2) |
| S11 (X2) | `test_w2_201_x2_chore.py::test_x2_a_chore_starts_with_no_ticket_on_the_role_default`; `test_w2_201_x2_chore.py::test_x2_another_ticket_s_record_in_the_folder_is_not_read_as_the_chore_s`; `test_w2_201_x2_chore.py::test_x2_an_exception_limited_to_c3_does_not_lift_a_chore_s_other_model`; `test_w2_201_x2_chore.py::test_x2_a_chore_asking_another_model_with_no_exceptions_file_is_refused`; `test_w2_201_x2_chore.py::test_x2_an_opus_exception_with_no_limiter_does_not_lift_a_chore_s_other_model`; `test_w2_201_x2_chore.py::test_x2_an_opus_exception_limited_by_decision_lifts_a_chore_s_other_model_when_the_launch_names_it`; `test_w2_201_x2_chore.py::test_x2_gov_pause_and_the_gate_stop_a_chore`; `test_w2_201_x2_chore.py::test_x2_the_planted_pause_and_gate_stop_an_ordinary_launch`; `test_w2_201_x2_chore.py::test_x2_plan_with_chore_prints_the_role_s_default_line`; `test_w2_201_x2_chore.py::test_x2_tests_worktree_does_not_take_chore` | 2 (engineer, test designer) + 1 + 1 + 1 + 1 + 2 (pause, gate) + 2 + 1 + 1 | `gov launch` has no `--chore` (argparse: `unrecognized arguments: --chore`): no chore starts, `--plan --chore` prints nothing, the S4 and stop refusals are exit 2 without `LAUNCH_REFUSED`, and `--tests-worktree --chore` is refused as an unknown option (10 red). Guards (2): the planted pause and gate stop an ordinary worker launch (the plants' own check) |
| S12 (X3) | `test_w2_201_x3_lead.py::test_x3_a_lead_launches_with_fix_on_a_closed_ticket_outside_the_ready_list`; `test_w2_201_x3_lead.py::test_x3_the_same_lead_without_fix_is_refused_by_the_plan`; `test_w2_201_x3_lead.py::test_x3_a_lead_fix_on_an_unknown_ticket_is_refused`; `test_w2_201_x3_lead.py::test_x3_a_lead_launches_with_chore_and_no_ticket`; `test_w2_201_x3_lead.py::test_x3_a_lead_launch_without_the_flags_is_unchanged`; `test_w2_201_x3_lead.py::test_x3_a_lead_s_refused_options_stay_refused_with_fix_and_chore`; `test_w2_201_x3_lead.py::test_x3_the_planted_pause_and_gate_stop_a_planned_lead`; `test_w2_201_x3_lead.py::test_x3_gov_pause_and_the_gate_stop_a_lead_fix_and_chore` | 2 (orchestrator, lead) + 1 + 1 + 1 + 1 + 8 (`--reason`, `--trial`, `--owner-named`, `--projection-usd` x fix, chore) + 2 (pause, gate) + 4 (pause, gate x fix, chore) | `gov launch` has no `--fix` or `--chore`: no fix or chore lead starts (so no `GOV_LAUNCH_KIND`, `GOV_LAUNCH_LINE` or chore address), the unknown ticket and the stops are exit 2 without `LAUNCH_REFUSED`, the refused lead options end 2 as argparse's unknown option (16 red). Guards (4): without `--fix` the closed ticket outside the ready list is refused by the plan; a planned lead without the flags starts with its `GOV_TICKET` and no `GOV_LAUNCH_*` key; the planted pause and gate stop a planned lead |
| S13 (X4) | `test_w2_201_x4_new_ticket_notice.py::test_x4_the_landing_lands_every_branch_and_answers_the_notices`; `test_w2_201_x4_new_ticket_notice.py::test_x4_a_new_feature_and_an_edited_existing_ticket_give_no_notice`; `test_w2_201_x4_new_ticket_notice.py::test_x4_queue_json_holds_the_answer_s_ticket_notices`; `test_w2_201_x4_new_ticket_notice.py::test_x4_the_dry_run_answers_the_same_notices_and_exit_code`; `test_w2_201_x4_new_ticket_notice.py::test_x4_the_landed_ticket_s_close_record_holds_its_notices`; `test_w2_201_x4_new_ticket_notice.py::test_x4_a_close_record_with_no_new_ticket_flagged_holds_no_notice`; `test_w2_201_x4_new_ticket_notice.py::test_x4_each_notice_is_one_line_on_stderr`; `test_w2_201_x4_new_ticket_notice.py::test_x4_a_branch_that_adds_no_ticket_file_answers_ticket_notices_empty` | 1 + 1 + 1 + 1 + 2 (A, E) + 2 (B, C) + 1 + 1 | the answer, `queue.json`, the dry run's answer and the close records have no key `ticket_notices`, and no notice is on stderr (10 red). Each case first asserts what holds on the base already (every branch landed, exit 0; the dry run moved nothing; the close records exist), so the red is the missing notice, never the plant |
| S14 (X5) | `test_w2_201_x5_words.py::test_x5_the_kernel_role_file_s_tools_line_names_the_three_statements`; `test_w2_201_x5_words.py::test_x5_each_role_copy_holds_the_kernel_tools_line`; `test_w2_201_x5_words.py::test_x5_one_line_of_the_skill_s_parallel_tickets_names_the_three_statements`; `test_w2_201_x5_words.py::test_x5_each_skill_copy_holds_the_kernel_section` | 3 (orchestrator, senior-engineer, ticket-lead) + 9 (3 roles x 3 copy folders) + 1 + 3 (3 copies) | no `Tools:` line and no line of `## Parallel tickets` holds `new ticket only for a new feature`, `--fix` and `--chore`; the copies equal the kernel lines already, so they fail on the same words (16 red) |

**Readings (where the section is silent).**

1. **X1, the usage errors' second fence** (`LAUNCH_REFUSED` from the launcher) has no public interface but the CLI,
   which stops first; it is not tested here. "Nothing read" is shown as nothing started and no record (and, for
   `--tests-worktree`, no tree made).
2. **X1, the statuses.** A fix on an `in_progress` ticket is a fix too (`kind` `fix`); `open` and `in_progress` run
   at C2 only. The role rule is shown with the engineer on a closed product-spec ticket; S4's refusal with Opus asked on
   a closed C2 ticket and no exceptions file; the gate and the one-writer check for a fix are left to X2 and X3's
   cases and today's suites.
3. **X2, "a second planted record of another ticket"** is a real earlier launch's record on a C3 ticket (Opus, by
   criticality) in the same folder: the chore's own record (by its session id) still says `ticket` null, the role
   default, `promotion` and `review_round` null, and the earlier record is unchanged.
4. **X2, S4 with no class to lift it.** An entry with `class: C3` does not lift a chore's Opus; with no exceptions
   file it is refused; an entry with no `class` (S4's unlimited entry) lifts it, recorded as `model_source`
   `exception` (a reading: S4 lets such an entry through on any class).
5. **X2, `--tests-worktree --chore`** is refused (non-zero, nothing made, nothing started); the exit code and words are
   left open, the Interface naming it only "does not".
6. **X2, the spend brake** ("no ticket-based spend brake") has no planted case: a chore has no ticket for the brake
   to read; the chore launches above show it is not refused.
7. **X3, the registry entry's label** is not read (the registry entry goes when the stand-in ends); the inbox address
   in the CLI process's environment is.
8. **X4, the unreadable front matter.** Its notice must start `NEW_TICKET_NOT_FEATURE PROJ-unrd: ` and hold
   `front matter unreadable`; whether the other parts are named beside it is left open (the KPIs cannot be read from
   it either). B's and C's close records may hold `ticket_notices` `[]` or no key.
9. **X5, the copies.** A role copy's `Tools:` line equals the kernel file's, byte for byte; a skill copy's `## Parallel
   tickets` section equals the kernel's. The whole-file copy checks are W1-28's, W1-33's and W2-153 S3's, in their own
   folders.

## Fix, part 2: a fix under a closed ticket lands, relaunches and has a run folder (DEC-1219 (5)), lines X6 to X8

Written by an independent test designer from the ticket's section `## Fix, part 2` (X6 to X8, each with its Verify;
the first part's Interface paragraph and X1 to X5 for context), before the implementation (MR-3). Read besides: the
base's `gov queue` (`gov.queue.command`, the close record writer of `gov.close.command`), `gov.dispatch.relaunch` and
the watch pass that calls it, the launcher's registry entry and run folder code (`gov.util.runs`), for their seams
only; W2-115b's, W2-202's, W2-205's, W2-121c's, W2-184's and W2-60a's support modules. Nothing of the engineer's work
on part 2 was read (there was none on the branch beyond the spec commit a6f02ff7a). Three test files and two support
modules beside the existing ones (none of which is changed): `w2_201_x6_support.py` (X6), `w2_201_x7_support.py` (X7);
X8 uses `w2_201_x_support.py`. X6 is `success-15` (`S15`), X7 `success-16` (`S16`), X8 `success-17` (`S17`).

**How the tests reach the product.**

* **X6:** `gov queue <T>=<branch> ... [--dry-run] --json` on W2-115b's planted project (tickets with acceptance
  suites, `.tickets/**` and `docs/close/**` record-only), each planted run built once per session under a lock, with
  a plain-pytest check of its branches first. A closed ticket is W2-115b's ticket file with `status: closed`; a first
  close's record is planted in the form `gov.close.command` writes one (its front matter, the queue's keys, the
  heading, one line of prose). Commits carry `Task:`, `Fix:` and `Role: engineer` trailers (`git commit --trailer`).
  The fix run: A (closed, with a record) on `topic/aa-fix1` (a commit with `Task: A` and no `Fix:`, then one with
  `Task: A` and `Fix:`), C (closed, no record) on `topic/cc-fix`, B (open) on an ordinary `topic/bb`; a dry run of the
  three, the landing of the three, then `topic/aa-fix2` from the new head and its landing. The refusal run: A (closed)
  with `topic/aa-plain` (`Task: A`, no `Fix:`) and `topic/aa-other` (`Task: B` and `Fix:`), then B (in_progress) on
  `topic/bb-fix` (`Task: B` and `Fix:`). The red run: C's fix breaks `mod_cc` (only C's acceptance suite guards it);
  A's fix breaks the widget, and A's acceptance suite passes whatever the widget holds, so A's red is the selected
  unit test `tests/unit/test_uses_widget.py` alone.
* **X7:** W2-205's fixture machine (`gov dispatch watch` as the pass, `{"relaunch": true}`, a dead registry entry
  planted in the launcher's form with a session id and the `kind` keys given). The relaunch's argv is read from a
  stand-in `gov`: a package `gov` planted in the entry's repository (the pass starts `python3 -m gov.cli.main` in that
  folder, which finds it first) and a `gov` on the pass's `PATH`; each records its argv and starts nothing. The
  registry entry of a real launch is read through W2-121c's `LaunchKit` (its stand-in CLI captures the entry when the
  session starts). The relaunched fix launch is W2-205's relaunch fixture: a real engineer session on an in_progress
  ticket, the ticket then closed, its dead entry a fix's; the pass's relaunch is a real `gov launch` that runs to the
  recording stand-in CLI, whose record is read.
* **X8:** `gov launch` through the console script on W2-184's fixture project and W2-60a's stand-in CLI, HOME the
  sandbox's, so the runs root is `<HOME>/gov-os-runs`; the folder's name is the ticket's `external-ref`
  (`W2-184-<id>`). Each case first launches an in_progress ticket's engineer and sees its folder made, so a red is the
  fix's missing folder, never a root that does not work in the sandbox.

**Words pinned and left open.** X6: the refusal `TICKET_CLOSED` with exit 1 and nothing changed (refs, HEAD, status,
tracked files); a fix landing's exit 0 and, for a red it causes, exit 3 with `culprits` the ticket and nothing landed
(as any candidate); the close commit's subject `fix: <ticket> (gov queue landed at <tested12>)`, one `Task: <ticket>`
trailer, its paths inside the ticket's own places (ticket file, `docs/close/<ticket>/`, `docs/checkpoints/<ticket>/`)
and the close record among them; `fixes` a list whose entries hold exactly `{line, branch, tip, tested, landed}`
(`line` the `Fix:` value, `branch` the name given to `gov queue`, `tip` the branch tip, `tested` the answer's `tested`,
`landed` a UTC time within a day of the run: an ISO 8601 text ending `Z` or `+00:00`, or the time YAML reads from one,
format otherwise open); the body line `- fix landed: <line> (<branch> @ <tip12>)` once per fix, the second after the
first; the rest of the record's front matter equal as YAML reads it (key order and quoting open) and its other body
lines kept in order (blank lines open); the `closes` entry's `fix: true` and `fix_line`, a feature's entry with neither
key; `queue.json`'s `closes` equal to the answer's. The dry run's answer carries `fix: true` and `fix_line` for each
fix (the lead's ruling, reading 7: in `closes`, the fixes' entries only); the case reads any map in its answer naming
the `ticket` with `fix: true`. Open: what else the record written for a ticket with none holds beside
`fixes` (the section says "with `fixes` only the way the landing writes a record, and nothing else of a first close":
not tested beyond `fixes` and the body line); whether a fix's close commit touches the ticket file (its status is
pinned `closed`, not its bytes). X7: in the spawned command, before `--`, the words less the option pairs are `launch
<role> <ticket>` for a fix and `launch <role>` for a chore (the label passed nowhere), `--fix` / `--chore` followed by
the line, `--root` followed by the entry's repository; after `--`, `--resume <session id>` and a text holding `Resume
at the recorded next step`; the order of the options before `--` and the rest of the text are open. The registry
entry's `kind` and `kind_line`; a feature's entry `feature` and null, or neither key. The relaunched record's `kind`
`fix`, `kind_line`, `ticket` and `resumes`. X8: the folder `<HOME>/gov-os-runs/<external-ref>`, a folder not a link,
its marker `.gov-os-repository` holding the real path of the project's git common directory and a newline; reuse with
no second folder, the planted file and the marker unchanged. "Handed to the session as an in_progress worker's": the
places (`--settings` env, other `--settings` keys, the CLI process's environment) whose value names the run folder are
the same for the fix as for an in_progress launch, and `GOV_TICKET` is the ticket in both env forms. On the base an
in_progress launch's settings and env name no run folder, so that comparison holds there; the case is red on the
folder.

The part's three files: 35 cases, 24 red and 11 green on the base (the tree of a6f02ff7a, through the heavy slot). A
green case is a guard: what holds today and must keep holding (named in the last column).

| KPI | tests | cases | expected red reason (on the base) |
|---|---|---|---|
| S15 (X6) | `test_w2_201_x6_fix_landing.py::test_x6_a_fix_branch_lands_with_exit_0_and_the_ticket_stays_closed`; `test_w2_201_x6_fix_landing.py::test_x6_a_fix_landing_runs_its_acceptance_folder_and_the_selected_tests`; `test_w2_201_x6_fix_landing.py::test_x6_the_fix_s_close_commit_is_named_fix_and_carries_task`; `test_w2_201_x6_fix_landing.py::test_x6_the_close_record_gains_one_fixes_entry_and_one_body_line_and_keeps_the_rest`; `test_w2_201_x6_fix_landing.py::test_x6_a_closed_ticket_with_no_close_record_gets_one_with_fixes`; `test_w2_201_x6_fix_landing.py::test_x6_the_answer_s_closes_entry_carries_fix_and_fix_line_and_a_feature_s_is_as_today`; `test_w2_201_x6_fix_landing.py::test_x6_queue_json_holds_the_answer_s_closes`; `test_w2_201_x6_fix_landing.py::test_x6_a_second_fix_on_the_same_ticket_appends_a_second_entry`; `test_w2_201_x6_fix_landing.py::test_x6_a_closed_ticket_s_branch_without_its_own_fix_trailer_is_refused_ticket_closed`; `test_w2_201_x6_fix_landing.py::test_x6_a_fix_that_breaks_a_test_is_not_landed`; `test_w2_201_x6_fix_landing.py::test_x6_the_dry_run_answers_the_same_and_changes_nothing`; `test_w2_201_x6_fix_landing.py::test_x6_a_fix_trailer_on_an_in_progress_ticket_closes_it_as_today` | 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 2 (plain, other) + 2 (acceptance-folder, selected-test) + 1 + 1 | `gov queue` refuses every branch of a closed ticket `TICKET_CLOSED` (exit 1, the batch refused as a whole), so no fix lands, no close commit, no `fixes` entry or body line, no `fix` / `fix_line`, the dry run is refused too, and a fix that breaks a test is refused before it runs instead of being its culprit (11 red; each case first asserts the answer is not `TICKET_CLOSED`, so the red names it). Guards (3): a closed ticket's branch with `Task:` and no `Fix:`, and one with `Fix:` under another ticket's `Task:`, are refused `TICKET_CLOSED`, exit 1, nothing changed; a `Fix:` branch on an in_progress ticket lands and closes it as today (`close:` commit, no `fixes`, no `fix` key) |
| S16 (X7) | `test_w2_201_x7_relaunch_kind.py::test_x7_the_pass_relaunches_a_fix_or_chore_entry_as_the_same_kind`; `test_w2_201_x7_relaunch_kind.py::test_x7_a_feature_entry_or_one_from_before_the_change_is_relaunched_as_today`; `test_w2_201_x7_relaunch_kind.py::test_x7_a_fix_or_chore_launch_s_registry_entry_holds_its_kind_and_line`; `test_w2_201_x7_relaunch_kind.py::test_x7_a_feature_launch_s_registry_entry_holds_feature_or_neither_key`; `test_w2_201_x7_relaunch_kind.py::test_x7_a_relaunched_fix_launch_is_not_refused_and_records_kind_fix_and_the_same_line` | 4 (fix, chore x engineer, orchestrator) + 4 (feature, old-form x engineer, orchestrator) + 4 (fix, chore x engineer, orchestrator) + 1 + 1 | the pass spawns `launch <role> <entry's ticket> --root <repository> -- --resume ...` whatever the entry's kind: no `--fix` / `--chore`, and a chore's label passed as a ticket; the launcher's registry entry has no `kind` or `kind_line`; the relaunched fix is refused `ticket '...' is not in_progress (status: closed)`, so no session starts (9 red). Guards (5): a feature entry and an entry with neither key are relaunched as today, for a worker and a lead (4); a feature launch's registry entry holds neither key (1) |
| S17 (X8) | `test_w2_201_x8_fix_run_folder.py::test_x8_a_fix_launch_gets_its_run_folder_with_the_marker`; `test_w2_201_x8_fix_run_folder.py::test_x8_the_same_fix_launch_repeated_reuses_the_folder_and_leaves_what_it_holds`; `test_w2_201_x8_fix_run_folder.py::test_x8_a_fix_reuses_the_folder_an_earlier_in_progress_launch_of_the_ticket_made`; `test_w2_201_x8_fix_run_folder.py::test_x8_the_fix_session_is_handed_its_folder_as_an_in_progress_worker_is`; `test_w2_201_x8_fix_run_folder.py::test_x8_a_feature_launch_on_a_closed_ticket_is_refused_and_gets_no_folder`; `test_w2_201_x8_fix_run_folder.py::test_x8_a_chore_makes_no_run_folder` | 2 (closed, open) + 1 + 1 + 1 + 1 + 1 | `runs.folder` gives no folder for a ticket that is not in_progress, so a fix launch on a closed or open ticket starts with no run folder under `<HOME>/gov-os-runs` (4 red; each case first sees an in_progress launch's folder made where it needs one). Guards (3): the folder an in_progress launch of the ticket made is there, untouched, after its fix (the launcher removes nothing); a feature launch on a closed ticket is refused `is not in_progress` and makes no folder; a chore makes none |

**Readings (where the section is silent), and one package.**

1. **X6, the fix line.** "The line is the first such commit's `Fix:` value": the planted branches have one commit with
   `Fix:` each (A's first branch has an earlier commit with `Task:` alone, which shows "at least one commit"), so which
   commit is "first" when two carry different lines (oldest or newest) is not tested.
2. **X6, a mixed batch.** The fixes land in one batch beside B's feature; B's close is as today (a `close:` commit, a
   closes entry with neither `fix` key, B closed). A second fix is landed from the head the first left.
3. **X6, (c).** "Not landed" is the landing's own outcome for a red: exit 3, `landed` empty, `culprits` the ticket, the
   broken test named (in `reds`, or the ticket's acceptance entry not `pass`), no ref moved, no tracked file changed,
   the ticket closed and A's record as planted.
4. **X7, the stand-in `gov`.** The base starts the relaunch as `python3 -m gov.cli.main` in the entry's repository;
   the planted package and the `PATH` stand-in see that and a start through the console script. A start in another
   folder, or one that does not take the working folder's package first (`-I`, `-P`), is seen by neither: the case
   then fails with no spawn recorded.
5. **X7, the lead.** A lead's registry entry has role `orchestrator` (the launcher's), so its relaunch is `gov launch
   orchestrator ...`; a lead launched as `lead` is read the same.
6. **X8, rules that stay** (the plain name, the root, the project not inside it, the name given once) are W2-50's and
   W2-60a's cases, in their own folders.
7. **Where the dry run says `fix: true`** (the lead's ruling on this designer's package). A dry run makes no close
   commit, and its `closes` stays empty for ordinary tickets (W2-206 requires it); it lists in `closes` only the
   entries the fixes would get, with `commit` and `close_record` null, each with `fix: true` and `fix_line`. The case
   reads any map in the dry run's answer naming the ticket with `fix: true` and its `fix_line`; W2-206's own cases
   hold the empty `closes` of a dry run with no fix.

The part alone (about 30 s on the base; the X6 runs take longer once fixes land and their tests run):

```
T=$(mktemp -d); TMPDIR=$T PYTHONPATH=<tree>/src:<tree>/src/gov/close/pytest_plugin \
  bash <main tree>/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest \
  tests/acceptance/W2-201/test_w2_201_x6_fix_landing.py tests/acceptance/W2-201/test_w2_201_x7_relaunch_kind.py \
  tests/acceptance/W2-201/test_w2_201_x8_fix_run_folder.py -q -p no:cacheprovider -n auto; chmod -R u+w $T; rm -rf $T
```

## Run

```
TMPDIR=$(mktemp -d) PYTHONPATH=<tree>/src:<tree>/src/gov/close/pytest_plugin \
  bash <main tree>/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest tests/acceptance/W2-201 -q -p no:cacheprovider
```

About 35 s on the base. No network, no model, no store; each case builds what it needs in `tmp_path`.

## Fix, part 3: the model rubric of DEC-1225 in code (a fix under W2-201), lines R1 to R5

Written by an independent test designer (Sonnet) from the ticket's section `## Fix, part 3` (R1 to R5, each with its
Verify), DEC-1225 and the code as it stands on `w2/integrate`'s base for the seams only (the stub CLI, the hook as a
subprocess, the records, the planted projects), before the implementation (MR-3). The engineer's work was not read.
The map names R1 to R4 as `S18` to `S21` (R5, the lead's listing of EXAMIN's copy, has no test: its Verify is the lead's
return and a folder left unwritten). New files: `test_w2_201_r1_role_files.py`, `test_w2_201_r2_launch_model.py`,
`test_w2_201_r3_limiters.py`, `test_w2_201_r4_memaudit_models.py`.

**Revised cases (each commit carries `Rewrite-Reason: DEC-1225: ...`, each case a comment saying what it pinned and
what it pins now).** In this folder: S1's `TABLE` (`w2_201_support.py`), S3 (whole file), S4's entries (a limiter
`task:` for the Opus entry that starts the engineer), S5 (the entry with no class now lifts nothing; the real
exceptions file's one entry; the real-rubric parity on the fixture entries), S9 (file deleted, replaced by R3's Fable
cases), F3 (the table line is planted, the file has none), X2 (an Opus entry with no limiter lifts nothing for a chore;
one limited by `decision` lifts it with `--owner-named`). Outside it, the cases that pinned the old table or the
promotion, probe, trial and substitution rules:

| where | what it pinned | what it pins now |
|---|---|---|
| `tests/acceptance/W2-184/` `s5_promotion`, `f1_failures`, `f1_tests_worktree`, `s3_record`, `s4_reviews` (2), `s1_max_equal` (probe) | a promotion or the probe launches Opus (`criticality.yaml`'s `opus`); a model after `--` other than Opus refused | the promotion and the probe keep their record, effort and round rules and launch the table's model (a fixture table's, Sonnet for the engineer's C2); another model after `--` is refused naming it and the session's model; the source word is `ANY` |
| `W2-184` `s2_model_and_trial`, `cli_options`, `s3_record`, `s1_max_equal`, `w2_184_support.trial_data` | a planted trial's model is Haiku | a trial's model is Sonnet (`TRIAL_MODEL`); the trial mechanism is shown with it; Haiku and Opus trials are R2's refusals |
| `W2-184` `s1_no_criticality_file` | the kernel engineer's and test designer's own table line launches on the default line | the kernel files have no table line; the line is optional there |
| `tests/unit/launch/` `test_w2_184_launch`, `test_w2_184_r_fixes`, `test_w2_184_role_line`, `test_w2_201_launch` | the same rules at the unit level; the four roles' real table lines; DEC-1215's substitution (S9) and `model_matches`' substituted case | as above; no table line in the real role files; the substitution cases and the `model_matches` table deleted (the R3 file runs the hook and the launcher on one table) |
| `tests/unit/hooks/` `test_w2_201_agent_model`, `..._worktree` | Fable judged as Opus under the substitution; the hook-launcher `model_matches` parity; the four-entry real file | Fable refused whatever the entries and a planted old file say; the decision and task limiters; the one-entry real file; the worktree cases spawn on Opus (class limiter) |
| `tests/unit/memaudit/` `test_judge`, `fakes.py` | reader and grader on Opus, the check on Sonnet; `FIGURES.json` without `models`; the second grader told by its model | all three Sonnet; `models` in `FIGURES.json`; the fake `claude` tells the check by `nth` (the second call of one prompt). These unit cases are in the `lifted` opt-in (run with `--optin=lifted`) |
| `tests/acceptance/W2-171/` `s3_judge`, `s6_figures` | the reader and grader on Opus; `FIGURES.json`'s exact keys | Sonnet; `models` read apart |
| `tests/acceptance/W2-33/` `w2_33_support.TABLE`, `test_w2_33_planted` | the table lines of four roles; the auditor's `Model tier: see Launch default`; five plants that edit those lines | no table line; the auditor's Model tier line names DEC-1225; the plants write the line back instead |
| `tests/acceptance/W2-60b/` `s11_rubric_keys`, `tests/acceptance/W2-104/` support, `tests/unit/skilleval/`, `tests/unit/orchestration/test_w2_149_setup_a.py` | a promotion's tier is `opus`; the skill harness's default model and the shipped kinds file's models are Opus | `sonnet` for the promotion's tier; Sonnet for both defaults |

**Readings (where the R lines leave a choice; the simplest taken).**

1. **A trial naming a model other than Sonnet** is refused (Opus and Haiku in the cases), as R2's body says; R2's Verify
   names Opus only. The trial's `reviewer` key (Opus by the trial file's own form) is not judged. A trial refusal names
   the word `trial` and the model; with an entry covering Opus (the class limiter) the trial starts on Opus.
2. **The limiter words.** A refusal "says which limiter is not met": the case accepts the key's word (`class` or `C3`,
   `task`, `decision` or `owner-named`) in the reason. A hook spawn whose entry has no `class` and no `task` needs no
   `Task:` line. `decision` and `task` given as one string equal a list of one. No case plants two `Decision:` lines.
3. **A lead and `--owner-named`.** `gov launch` refuses `--owner-named` for a lead (W2-184 R1), so a lead's Opus is
   refused with no entry able to lift it; the lead cases pin the `--model` the launcher adds (once, Sonnet), the refusal of
   another model naming DEC-1225 and `governance/project/model-exceptions.yaml`, and Fable refused with entries naming it.
4. **The source word of a model** that comes from the role file's default (no table line) is left open (`role default`
   or `by criticality`); so is a promotion's and a probe's. `rubric` of the record is not pinned.
5. **`FIGURES.json` `models`** is a map of three Sonnet entries with the keys `reader` and `grader` among them (the third
   is the checker's, its key name left open).
6. **The `Model tier` line of the auditor** holds `Opus`, `DEC-1225`, `exception`, `comprehensive` and `owner`
   (case-insensitive); `criticality.yaml`'s comments hold `DEC-1225` and a sentence with `class` and `model` and a
   negation, and `exception`; audit 4's Table 3 section holds `DEC-1225` and gives Opus or Haiku to no row that is not
   the CTO's. The role versions after the change: `engineer`, `independent-test-designer`, `independent-auditor` 1.2.0,
   `qa-engineer` 1.1.0, in the kernel files and the three copy folders.
7. **Out of this folder, left for the lead.** W2-153's, W2-60a's, W2-204's, W2-195's, W1-28's, W1-33's and
   `tests/unit/adapters` cases were green with the new role files (a sandbox copy of this tree with the role files'
   table lines taken out and the exceptions file replaced); they pin the generation and copy checks, which stay. The
   W2-104 acceptance run and the W2-81 runner cases were not run beyond the lines named above.

8. **The portability check is red on the base for another file.** `python3 -m gov.adapters.portability` reports `GENERATED_DIFFERS` for `.claude/settings.json` (the root's settings file holds hooks and deny rules that `.rulesync/` does not generate), whatever this ticket does; R1's Verify says the check is "green on the tree", which no change of the role files can make true. The R1 case judges the findings that name a role file or a copy; whether the settings finding is to be cleared is the lead's call.

| KPI | tests | cases | expected red reason (on the base) |
|---|---|---|---|
| S18 (R1) | `test_w2_201_r1_role_files.py::test_r1_the_opus_and_haiku_model_ids_are_left_only_in_the_two_opus_roles_default_line`; `test_w2_201_r1_role_files.py::test_r1_criticality_yaml_names_opus_only_in_its_opus_key_and_never_haiku`; `test_w2_201_r1_role_files.py::test_r1_criticality_yaml_s_comments_say_a_class_no_longer_picks_a_model`; `test_w2_201_r1_role_files.py::test_r1_the_auditor_s_model_tier_line_says_an_opus_audit_is_only_the_exceptions_file_s_entry`; `test_w2_201_r1_role_files.py::test_r1_each_changed_role_file_goes_up_by_one_minor`; `test_w2_201_r1_role_files.py::test_r1_a_copy_carries_the_kernel_file_s_launch_lines`; `test_w2_201_r1_role_files.py::test_r1_audit_4_table_3_carries_the_table_with_a_note_naming_dec_1225`; `test_w2_201_r1_role_files.py::test_r1_the_portability_check_has_no_finding_on_a_role_file_or_a_copy`; with S1's two cases above | 36 + 1 (S1) + 36 + 1 + 1 + 4 + 16 + 27 + 1 + 1 | S1's table (16 red, as above); the four roles' table lines name Opus and Haiku (16 red of 36); `criticality.yaml` has no DEC-1225 comment (1); the auditor's Model tier line is `see Launch default` (4); the four changed files keep their old versions (16); audit 4's table still gives Opus to the auditor rows and carries no DEC-1225 note (1): 54 red in all. Guards (48 of the folder's R1 cases): the scan's other 20 cases, the criticality file's `opus` key as the only Opus (1), the copies equal to their kernel files (27) and no portability finding on a role file or a copy (1) |
| S19 (R2) | `test_w2_201_r2_launch_model.py::test_r2_a_lead_is_started_with_model_sonnet_added`; `test_w2_201_r2_launch_model.py::test_r2_a_lead_asking_another_model_after_the_double_dash_is_refused`; `test_w2_201_r2_launch_model.py::test_r2_a_lead_asking_fable_is_refused_whatever_the_exceptions_file_holds`; `test_w2_201_r2_launch_model.py::test_r2_a_lead_asking_sonnet_after_the_double_dash_starts_with_one_model_flag`; `test_w2_201_r2_launch_model.py::test_r2_a_worker_asking_opus_after_the_double_dash_is_refused_naming_dec_1225_and_the_exceptions_file`; `test_w2_201_r2_launch_model.py::test_r2_a_worker_asking_fable_is_refused_also_with_an_entry_naming_it`; `test_w2_201_r2_launch_model.py::test_r2_a_worker_asking_sonnet_after_the_double_dash_starts_one_session_with_one_model_flag`; `test_w2_201_r2_launch_model.py::test_r2_a_trial_naming_a_model_other_than_sonnet_is_refused`; `test_w2_201_r2_launch_model.py::test_r2_a_trial_naming_sonnet_starts_and_is_recorded_as_a_trial`; `test_w2_201_r2_launch_model.py::test_r2_a_trial_naming_opus_starts_when_an_exceptions_entry_covers_it`; `test_w2_201_r2_launch_model.py::test_r2_a_promotion_on_an_auditor_launches_sonnet_and_keeps_its_record`; `test_w2_201_r2_launch_model.py::test_r2_the_second_review_of_a_full_ticket_is_the_probe_on_sonnet_at_max`; `test_w2_201_r2_launch_model.py::test_r2_the_skill_evaluation_harness_defaults_to_sonnet`; with S3's three cases above | 6 + 18 + 4 + 3 + 4 + 4 + 2 + 2 + 1 + 1 + 1 + 1 + 1 (+ S3's 28) | the launcher adds no `--model` for a lead (6 red) and judges none a lead gives, Opus or Haiku (18), or Fable with entries naming it (4); a worker asking Opus is refused without naming DEC-1225 (4), Fable likewise (4), and a C3 worker's `--model <sonnet>` is refused as the session is Opus there (2); a Haiku or Opus trial starts (2); a promotion launches Opus (1); round 2 launches Opus (1); the harness default is Opus (1): 43 red, and S3's 8. Guards (5): a lead's `--model <sonnet>` is not doubled (3), a Sonnet trial starts, a trial on Opus starts with a covering entry |
| S20 (R3) | `test_w2_201_r3_limiters.py::test_r3_an_auditor_spawn_carrying_decision_dec_1230_is_let_through`; `test_w2_201_r3_limiters.py::test_r3_an_auditor_spawn_with_no_decision_line_is_refused_naming_the_limiter`; `test_w2_201_r3_limiters.py::test_r3_an_auditor_spawn_naming_another_decision_is_refused`; `test_w2_201_r3_limiters.py::test_r3_an_auditor_spawn_with_a_task_line_only_is_refused`; `test_w2_201_r3_limiters.py::test_r3_any_other_type_naming_opus_is_refused_whatever_it_carries`; `test_w2_201_r3_limiters.py::test_r3_the_opus_refusal_carries_no_fable_hint_and_no_substitution_reading`; `test_w2_201_r3_limiters.py::test_r3_the_hook_lifts_or_refuses_by_the_entry_s_limiters`; `test_w2_201_r3_limiters.py::test_r3_the_launcher_lifts_or_refuses_by_the_entry_s_limiters`; `test_w2_201_r3_limiters.py::test_r3_a_chore_has_no_ticket_so_a_task_limiter_is_unmet`; `test_w2_201_r3_limiters.py::test_r3_an_auditor_with_owner_named_dec_1230_starts_on_opus_and_records_the_exception`; `test_w2_201_r3_limiters.py::test_r3_an_auditor_asking_opus_without_the_decision_is_refused_naming_the_limiter`; `test_w2_201_r3_limiters.py::test_r3_another_role_with_owner_named_dec_1230_is_refused_no_entry_names_it`; the S9 row's four Fable cases; `test_w2_201_r3_limiters.py::test_r3_the_substitution_file_is_deleted`; `test_w2_201_r3_limiters.py::test_r3_the_role_reader_has_no_substitution_function`; `test_w2_201_r3_limiters.py::test_r3_no_substitut_is_left_in_the_launcher_the_hook_or_the_cto_start_script`; `test_w2_201_r3_limiters.py::test_r3_no_file_of_src_gov_launch_names_a_substitution`; `test_w2_201_r3_limiters.py::test_r3_the_cto_start_script_starts_the_cto_on_claude_opus_5_5` | 2 + 2 + 2 + 2 + 4 + 1 + 15 + 15 + 1 + 1 + 2 + 2 + 16 + 1 + 1 + 5 + 1 + 1 | the base reads no `decision` or `task` limiter and an Opus entry with no `class` lifts what it names: the auditor spawn with no decision line, another decision or a `Task:` line only is let through (6 red), the hook's and the launcher's scenarios whose entry should refuse are let through or refused without the limiter's word (7 red each of 15), a launch with `--owner-named` other than DEC-1230, or none, and the engineer or test designer with DEC-1230 are not refused as R3 says (2 + 2 + 1 red); an entry naming Fable lifts it in the hook (10 red) and DEC-1215's planted file lets it through (2); `model-substitution.yaml`, `substitute`, `substitution_active` and every `substitut` of the launcher, role reader, exceptions reader, hook and `start_cto.sh` are still there (1 + 1 + 5 + 1 red), and `start_cto.sh` asks the role reader for the model (1): 46 red. Guards (28): the met scenarios (class, task, decision), a `Decision: DEC-1230` auditor spawn and launch, the other types refused (4), Fable with no exceptions file and from the launcher (4), the Opus refusal carrying no Fable hint (it has none while the substitution file is inactive) |
| S21 (R4) | `test_w2_201_r4_memaudit_models.py::test_r4_the_reader_the_grader_and_the_check_are_sonnet`; `test_w2_201_r4_memaudit_models.py::test_r4_no_file_of_src_gov_memaudit_names_claude_opus`; `test_w2_201_r4_memaudit_models.py::test_r4_no_shipped_brief_and_no_shipped_kinds_file_names_claude_opus`; `test_w2_201_r4_memaudit_models.py::test_r4_the_shipped_kinds_models_are_sonnet` | 1 + 38 + 4 + 1 | `READER` and `GRADER` are Opus (1); `judge.py` (1), the shipped briefs `auditor.md` and `checker.md` and the shipped `kinds.yaml` (3) name `claude-opus-5-5`, and the kinds' models are not Sonnet (1): 6 red on the base; the other 38 cases of the file are guards. The call-level and `FIGURES.json` cases are listed under the table as extra evidence (they are outside this folder, so `gov accept W2-201` does not run them) |

Extra evidence for S21 (R4), outside this folder and not in the map: `tests/unit/memaudit/test_judge.py::test_each_call_is_the_fresh_80s_argv_with_no_tools_and_the_models_of_item_7` and `::test_figures_json_holds_exactly_item_10s_keys_and_counts` (run with `--optin=lifted`), and W2-171's `test_s3_the_calls_carry_the_fresh_80s_prompts_models_budgets_and_flags` and `test_s6_figures_json_has_exactly_the_keys_of_item_10_and_the_planted_values` (with `--optin=lifted`): the reader, grader and check calls carry `--model claude-sonnet-5-5`, and `FIGURES.json` holds `models` with the three. W2-171's `fake_claude.py` tells the check from the grader by call order, as `tests/unit/memaudit/fakes.py` does, since the model no longer does.
