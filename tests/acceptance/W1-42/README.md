# W1-42 — Wave 1 exit run on the dev tiers: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPI lines of ticket `DAEO-gjjf` (W1-42),
`docs/plan/WAVE_1_WBS.md` section 4, and DEC-088, DEC-089, DEC-106, DEC-161, DEC-235, DEC-377, DEC-414, DEC-428,
DEC-467, DEC-472, DEC-511, DEC-522, DEC-537, DEC-651, DEC-655, DEC-658, DEC-660. Written before the exit report
exists. Profile FULL, in proportion (DEC-221): the work is a report, so one or a few cases per KPI line; 24 cases.
No earlier ticket's test was touched.

## Run

```sh
env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-42 -q -p no:cacheprovider -rs
```

`pytest` and the standard library. No network, no `gov` command, nothing written. The cases read the report, the
kept answers, the ticket files and `src/gov/cli/main.py` (the twelve reserved names), and ask git two read-only
questions (does a commit exist; is it in the history of another).

## The form of the report: `docs/plan/wave-1-exit/EXIT-REPORT.md`

Markdown. The cases read level-2 headings (`## <number>. <title>`, the number optional, the title beginning as
below), pipe tables found by their column names, and lines of the form `- **Key:** value`. Other text, other
columns and other sections are free. Rules that hold everywhere:

- **A path** is a backticked token beginning with `docs/`, `governance/`, `.tickets/`, `tests/`, `src/` or
  `template/`. Every path the report names must exist in this repository; no patterns (`*`, `?`, `<...>`).
- **An empty value** is an empty cell or one of: TBD, TODO, n/a, `?`, `-`, `—`, `...`, pending.
- **A reason** follows its words after a colon: `not reached: <reason>`, `not measured: <reason>`,
  `not recorded: <reason>`, `not done: <reason>`.

Before the first section: `- **Overall verdict:** MET` or `NOT MET`.

| Section title | What it must hold |
|---|---|
| `Exit criteria` | Table `Criterion \| Verdict \| Evidence`, eight rows in this order, each Criterion cell beginning with its key: `1`, `2`, `3`, `4`, `5`, `doctor`, `canaries`, `check-and-commands` (the five criteria and the three "also required" lines of WBS section 4). Verdict: `MET`, `NOT MET` or `NOT REACHED`. Evidence: never empty; a `MET` row names at least one path; another row gives its reason. |
| `Programme ORION` and `Programme ARGUS` (one section each, e.g. `## 2. Programme ORION (a-dev)`) | Lines `- **Feature:**`, `- **Adoption stage reached:**` (begins `A0` to `A8`; below `A8` a reason follows, DEC-658), `- **Close result:**`. Table `Step \| Result \| Ticket ids \| Evidence` with exactly these nine rows in this order: `discovery`, `closed specification`, `independent specification audit`, `linked gap tickets`, `independent tests`, `implementation`, `close`, `CI`, `merge`. Result is `done` or `not reached: <reason>`. A `done` row names at least one ticket id of the clone (`ORION-...`, `ARGUS-...`) and at least one path. **The `close` row is `done` only for a `gov close` that succeeded:** its Evidence names exactly one file under the evidence folder, the kept answer of that `gov close --json`, with `ok` true and `result.ticket` among the row's ticket ids, and `Close result` then holds the words `clean gov close`. A ticket closed another way (`tk close`, DEC-658) is `not reached: <reason>` in that row, and `Close result` says what was done without the words `clean gov close`. |
| `Clean close` | Lines `- **Ticket:**` (an `ORION-...` id, the implementation ticket of the ORION table, DEC-658), `- **Kept answer:**` (one path under the evidence folder: the `gov close --json` answer, `ok` true, no `error`, `result.ticket` equal to the ticket, `result.close_record` present), `- **Exception:** none`. |
| `Retrieval` | Table `Measure \| Figure \| Baseline \| Comparison` with a row beginning `mean hit@5` and a row beginning `callers/impact hit@5`; Figure and Baseline equal `retrieval-hit5.json`; Comparison begins `at or above` or `below`, as the two numbers say. Table `Query \| Kept bundles \| Batches \| Parent expansions \| Synthesis notes \| Stopping reason` with a row `RETR-A-04` and a row `RETR-X-02`: Kept bundles names the query's evidence file; the three counts begin with the number the file gives; Stopping reason is the last bundle's. |
| `gov check and the twelve commands` | The words `17 of 17` and the paths of `gov-check.json` and `gov-commands.json`. |
| `Worker sessions` | Table `Programme \| Role \| Session id \| Ticket \| Started through \| Sandbox \| Network profile \| Launch record`, one row per worker session, no empty cell, session ids unique. Programme begins `ORION`, `ARGUS` (or anything else for a session of this repository). Started through: `gov launch`. Sandbox: `sandboxed`. Launch record: one path under the evidence folder. Each of ORION and ARGUS has at least one row of each role `engineer`, `independent-test-designer`, `independent-auditor`, and its rows carry tickets of the clone. |
| `Governance share` | Table `Programme \| Share \| Cache reads \| Record`, a row beginning `ORION` and one beginning `ARGUS`. Share is a figure in `%` (`9.4 %`) or `not measured: <reason>`. With a figure, Record names the path that `governance-share.json` gives. |
| `MR-3` | Line `- **Breaches:** 0`, and the path of `mr3.json`. |
| `Learning metrics` | Table `Ticket \| KPI disputes \| Tests rewritten after implementation began \| Governance share`: exactly one row per Wave 1 ticket of `.tickets/` (50; the Ticket cell holds the `W1-NN` id). No empty cell. A metric that was not recorded says `not recorded: <reason>` or `not measured: <reason>`. A count of rewritten tests above 0 is followed by the reasons in the same cell (`2: DEC-497 changed the hook's exit code`). |
| `Parallel tickets` | Line `- **git worktree list:**` naming `git-worktree-list.txt`. Table `Ticket \| Worktree \| Branch \| Ticket lead \| Merged by \| Merge commit \| Suites re-run after the merge`, at least two rows, each a Wave 1 ticket run in the light form: Worktree holds the `W1-NN` id; Branch begins `w1/W1-NN`; Ticket lead not empty; Merged by holds `main orchestrator`; Merge commit is a commit in the history of this branch; the last cell names the path of the kept record of the suites run after that merge. |
| `Owner's steps` | Table `Step \| Result \| Record` with rows `B1`, `B2`, `B3` (DEC-660). Result is `done` (Record names a path) or `not done: <reason>`. |
| `Baseline and adoption` | Lines `- **Adoption complete at:**` and `- **Exit run started at:**`, each a commit of this repository, the first in the history of the second. Table `Fact \| Result \| Evidence` with rows beginning `gov adopt --lite run`, `gov check baseline empty`, `capability records present`; Result `yes`; Evidence names a path. |
| `How the run was run` | Lines `- **Orchestration skill:**` (one path, the kernel's `.../governance/kernel/skills/orchestration/...` file), `- **Brief templates:**` (paths `.../governance/kernel/templates/brief-*.md`, among them `brief-test-designer.md` and `brief-engineer.md`), `- **Kept briefs:**` (at least one brief of the run, kept under the evidence folder), `- **Repository orchestrator prompt:** not used`. |
| `Forbidden outcomes` | Line `- **Forbidden outcomes:** none`, or what happened. |

**The failure lines.** `Overall verdict` may be `MET` only when the rows `1`, `2`, `3`, `4`, `doctor`, `canaries`
and `check-and-commands` are all `MET` (row `5` is W1-43's audit and may be `NOT REACHED`), `Forbidden outcomes`
says `none`, and both shares are figures of at most 15 %. Row `4` may not be `MET` while a share is above 15 % or
not measured. A breach kept in `mr3.json` forbids `none` and a `MET` in row `3`.

## The form of the evidence: `docs/plan/wave-1-exit/evidence/`

Kept answers, as the commands printed them. Fixed names, except where the report names the file.

| File | What it must hold |
|---|---|
| `gov-check.json` | The answer of `gov check --json` on this repository at the exit run (the whole envelope). `ok` true; `result.families` has 17 entries, none RED, none with the reason `no registered check`; every family has at least one entry of `result.checks` (matched on the family name, lower case, non-alphanumerics as `-`); no check RED. |
| `gov-commands.json` | `{"<command>": {"argv": ["gov", "<command>", ...], "exit_code": <int>, "answer": <the answer as printed, parsed or as text>}}` with exactly the twelve reserved names: status, check, readiness, doctor, rebuild, context, closure, retrieve, checkpoint, close, adopt, pause. No `-h` or `--help` call. `NOT_IMPLEMENTED` appears nowhere. An answer taken on a clone or on a throwaway repository is fine. |
| the clean close's answer, and each programme's close answer (named by the report; they may be one file) | The answer of `gov close <ticket> --json`: `command` `close`, `ok` true, `result.ticket`, `result.close_record`. |
| `retrieval-hit5.json` | `{"dev_query_set": {"mean_hit_at_5": <0-100>, "baseline": 85, "queries": <int>}, "code_classes": {"callers_impact_hit_at_5": <0-100>, "baseline": <0-100>, "classes": ["..."], "queries": <int>, "baseline_source": "<the path of S0b2's codeintel.md report>"}}`. Percent, not fractions. |
| `RETR-A-04.json`, `RETR-X-02.json` | `{"query_id": "RETR-A-04", "bundles": [<each bundle as gov retrieve returned it>], "validator_errors": [], "packet_ceiling_exceeded": true or false, "synthesis_notes": ["<path of a note kept in this repository>"]}`. Over the bundles: at least two batches in all (the `batches` lists); every bundle a `stopping_reason` of the six fixed ones and evidence items each with `id` and a 64-hex `sha256`; at least one entry of `expansions`, each with `parent_id`. When the ceiling was exceeded at least one note is named; every named note is a file. |
| `governance-share.json` | `{"ORION": {"share_percent": <0-100>, "cache_read_tokens": <int>, "record": "<path under the evidence folder of the kept answer of the counter>"}, "ARGUS": {...}}`. Measured figures only: the file is not written while a share is not measured. |
| `mr3.json` | `{"breaches": [], "checked": [{"repository": "a-dev", "check": "...", "method": "...", "result": "..."}, ...]}`; at least one entry for `a-dev` and one for `b-dev`. |
| `git-worktree-list.txt` | The output of `git worktree list`, unchanged, taken when no ticket worktree is left: no line holds `gov-os-worktrees/` or `[w1/W1-`. |
| `owner-freeze-check.json` | `{"throwaway": {"repository": "...", "terminal": "plain", "steps": [{"command": "gov pause --json", "answer": ...}, {"command": "gov status --json", "answer": ...}, {"command": "gov pause --off", "answer": ...}, {"command": "gov status --json", "answer": ...}]}, "this": {the same, plus "refused_write": "<the text of the refusal of the one write tried under the freeze>"}}`. The answers as the owner reported them; the first `gov status` answer holds `"paused": true` and the second `"paused": false` (exactly one `paused` key in each). |

Anything else the report cites (launch records, kept briefs, regression records, counter answers, notes) is kept
under the same folder under a name of the lead's choice.

## KPI line → cases → red reason today

All cases are in `test_w1_42_exit_report.py`. Red run on `w1/W1-42` at `2853f74d`: **24 errors, 0 passed**; every
case stops in the `report` fixture with

> `docs/plan/wave-1-exit/EXIT-REPORT.md does not exist: the exit report has not been written`

| KPI line (ticket order) | Cases |
|---|---|
| WBS section 4, every criterion answered with evidence; every named path exists | `test_every_exit_criterion_is_answered_with_its_evidence`, `test_every_path_the_report_names_exists` |
| 1. The cycle on a-dev and b-dev (DEC-088, DEC-089, DEC-658) | `test_programme_cycle_is_stated_step_by_step[ORION]`, `[ARGUS]`; `test_programme_close_is_stated_as_the_kept_answer_says[ORION]`, `[ARGUS]` |
| 2. RETR-A-04 and RETR-X-02 | `test_retrieval_query_ran_with_bundles_expansions_notes_and_stopping_reason[RETR-A-04]`, `[RETR-X-02]` |
| 2. Governance share at most 15 % (DEC-655) | `test_governance_share_is_measured_and_at_most_15_percent_on_each_programme` (waits) |
| 2. Zero MR-3 breaches | `test_zero_mr3_breaches_with_what_was_checked` |
| 3. 17 of 17 families `[CAP-38.b]` | `test_gov_check_reports_17_of_17_families_with_an_executable_check` |
| 4. Twelve commands `[CAP-28.b]` | `test_all_twelve_wave_1_commands_are_implemented` |
| 5. Worker sessions through `gov launch` (DEC-161) | `test_worker_sessions_were_started_through_gov_launch` |
| 6. Three learning metrics per ticket (DEC-106) `[CAP-40.c]` | `test_learning_metrics_table_has_a_full_row_for_every_wave_1_ticket` |
| 7. Parallel tickets, light form (DEC-235) `[CAP-23.c]` | `test_parallel_tickets_ran_in_worktrees_and_were_merged_by_the_main_orchestrator`, `test_git_worktree_list_shows_no_ticket_worktree_left` (waits) |
| 8. callers/impact hit@5 (DEC-377) | `test_callers_impact_hit5_is_measured_on_the_code_classes` |
| 9. Mean hit@5 against 85 (DEC-414) | `test_dev_query_set_mean_hit5_is_remeasured_against_85` |
| 10. The owner's freeze, pause and lift (DEC-428, DEC-660) | `test_owner_steps_are_each_stated_with_their_result`, `test_owner_froze_paused_and_lifted_on_a_throwaway_repository_and_on_this_one` (waits) |
| 11. Baseline empty (DEC-467, DEC-472); 12. adoption complete before the run (DEC-511, DEC-522) | `test_baseline_is_empty_and_adoption_was_complete_before_the_exit_run` |
| 13. One clean `gov close` (DEC-511) | `test_one_real_ticket_closed_by_a_clean_gov_close` |
| 14. Run from the kernel's skill and briefs (DEC-537) | `test_exit_run_was_run_from_the_kernel_skill_and_brief_templates` |
| Failure lines | `test_a_forbidden_outcome_or_a_share_above_15_percent_is_never_reported_as_a_pass` |

## Cases that wait for a record

Red until the record exists, whatever the report says. None passes on a placeholder, on `not measured` or on a
missing file.

| Case | The record that turns it green |
|---|---|
| `test_governance_share_is_measured_and_at_most_15_percent_on_each_programme` | `evidence/governance-share.json` with a measured share for ORION and for ARGUS, each naming the kept answer of the counter, after the session-log reader's round on W1-31 is merged (DEC-655); the report's Share cells carry the same figures. It stays red on a share above 15 %: that is the ticket's failure line. |
| `test_git_worktree_list_shows_no_ticket_worktree_left` | `evidence/git-worktree-list.txt`, taken after this ticket's own worktree (`~/gov-os-worktrees/W1-42`) is removed, that is after the ticket's merge. Green in this worktree is impossible by construction; the main orchestrator supplies the file. |
| `test_owner_froze_paused_and_lifted_on_a_throwaway_repository_and_on_this_one` | `evidence/owner-freeze-check.json`, from the owner's step B2 in a plain terminal on the throwaway clone and on this repository (DEC-428, DEC-660), and the row `B2` of the report saying `done` with that path. |

With those three records missing and stated as missing, the other 21 cases can be green, and the report then
says `NOT MET` in row `4` and in `Overall verdict` (the failure-line case holds it to that).

## What these cases do not test

- **That a statement of the lead is true where no command answer exists.** "Sandboxed with its network profile",
  "merged by the main orchestrator", "every suite re-run after each merge", "the repository's orchestrator prompt
  was not used" and the MR-3 entries of `mr3.json` are held to their form and to a kept record that exists, not
  re-derived. W1-43's auditor reads the records themselves.
- **Criterion 5, `gov doctor` and the canaries** (WBS section 4) have no KPI line of their own on this ticket:
  they are held only to a verdict row with evidence.
- **A pass line for the two hit@5 figures.** The KPI lines say "re-measures ... and reports it" and "measures":
  the figures must be kept and compared truthfully with their baselines (`below` is said when it is below); a
  figure below its baseline does not fail a case.
- **The content of the clones.** The cases read this repository only; the clones' ticket ids are held to their
  prefix and to the kept answers copied here.
- **The per-ticket metrics against `governance/project/bootstrap.md`.** The residual sections there record them
  in free prose, differently per ticket; the cases hold the table to one full row per ticket, not to those
  sentences.
