# W2-104 acceptance tests: the skill evaluation harness (`gov skilleval`)

Ticket `DAEO-drhj` (W2-104), profile STANDARD. Written by the independent test designer (MR-3) from the ticket's
KPI lines, its sources (DEC-959 items 5 and 7, DEC-820, ROLES-RESEARCH-1 §5.3 item 13) and the public contract
the lead set for the designer and the engineer, in parallel with the implementation (DEC-959 item 7). The
designer read no part of the implementation (DEC-820 (c)).

## How the tests find the code under test

`w2_104_support.py` sets `REPO_ROOT = Path(__file__).resolve().parents[3]`: the repository this suite sits in.
Every case runs `python3 -m gov.cli.main skilleval …` as a process, with `PYTHONPATH=<REPO_ROOT>/src` set in a
child environment built from scratch (PATH, an empty HOME, TMPDIR, locale, PYTHONPATH, a bytecode cache
outside the sources). No installed `gov`, no fixed path and nothing of the calling session's environment is
used. Merged into the ticket's worktree, the suite runs that worktree's `src/`.

Run it from the repository root:

    TMPDIR=<a writable temp folder> PYTHONPATH=<repository>/src python3 -m pytest tests/acceptance/W2-104 -q \
        -p no:cacheprovider -o tmp_path_retention_policy=failed

## What the cases use

- **A temporary project** under pytest's `tmp_path`, built from scratch (a git repository with a gitignore and a
  readme), with planted skill folders: `SKILL.md` (front matter with `name` and `version`) and `scenarios.md` in
  W2-11's form (`## <n>. <title>` and the bullets `- **Situation:**`, `- **Expected:**`, `- **Pass line:**`).
- **A stub model:** a Python script named `claude`, alone in a folder that is first on a `PATH` holding only it
  and `/usr/bin`, `/bin`. Each case first checks that no `claude` is in the system folders, so no case can reach
  the real program. The stub reads its prompt from standard input. A prompt that holds the session-reply token
  (`STUBREPLYW2104`) is a judgement's; any other is a session's. It logs each call (arguments, working folder,
  standard input, the session folder's `.claude/skills/` and any `scenarios.md` under it) as one JSON file, and
  answers by marker words planted in a scenario's text:

  | Marker (in) | Stub behaviour |
  |---|---|
  | none (Situation) | the session answers `STUBREPLYW2104 <tag> done as the skill says.`, cost 0.25 |
  | `SESSIONW2104_EXITNONZERO` | the session exits 7 |
  | `SESSIONW2104_BADJSON` | the session prints text that is not JSON |
  | `SESSIONW2104_ISERROR` | the session answers with `is_error: true` |
  | `SESSIONW2104_SLEEP` | the session sleeps 30 s, then answers |
  | `SESSIONW2104_SAYSPASS` | the session's own reply ends with `VERDICT: PASS` |
  | `SESSIONW2104_LEAK{STDERR,STDOUT,ERROR}` | the session prints the planted values on stderr (exit 1), as non-JSON stdout, or in an `is_error` reply |
  | none (Pass line) | the judgement answers `… VERDICT: PASS`, cost 0.05 |
  | `JUDGEW2104_FAIL` | the judgement answers `VERDICT: FAIL` |
  | `JUDGEW2104_NOVERDICT` | the judgement's reply has no verdict line |
  | `JUDGEW2104_PASSTHENFAIL` / `JUDGEW2104_FAILTHENPASS` | two verdict lines, the last FAIL / PASS |
  | `JUDGEW2104_EXITNONZERO` | the judgement exits 9 |

- **Planted secrets:** two made-up strings, built at run time (`planted_values()`, `w2104-planted-…-not-real-…`),
  one in the environment as `ANTHROPIC_API_KEY`, one in the project's `.env`. Nothing real is planted.

Nothing reaches the network, and no real model is called.

## The KPI lines and their cases

Every case fails on the base for one reason: **`gov` has no `skilleval` command.** `python3 -m gov.cli.main
skilleval …` ends with argparse's usage error (exit 2, `invalid choice: 'skilleval'`), so each case fails at its
first check of the exit code or the envelope. The one help case fails with `gov --help does not offer skilleval`.

The map below is in `gov accept`'s form (W2-96, DEC-959 item 6): a `KPI line` column and a `Tests` column whose
code spans each name one case as `<file>::<function>` (a parametrized function covers all its variants). The
`What the cases hold` column is notes for the reader; the runner does not read it.

| KPI line | What the cases hold | Tests | Red reason on the base |
|---|---|---|---|
| **Success 1:** three committed scenarios, each on a fresh session with only that skill loaded, model and effort from the role defaults, judged against the pass line, a scenario record (skill version, scenario, verdict, cost, time) beside the skill | the command and its help; a skill that cannot be evaluated ends 5 with nothing run or recorded (6 variants: no SKILL.md, no version, no scenarios.md, two or four scenarios, a scenario without its Pass line); the envelope; the record's entries, appended; one new session per scenario in a new folder outside the project with only the evaluated skill and no scenarios.md; new processes with the default model and effort; the judgement a separate process given the Pass line, the Expected text and the reply; the options; W2-11's wrapped form; absolute and root-relative skill paths | `test_w2_104_command.py::test_gov_help_offers_skilleval_and_its_help_names_it`, `test_w2_104_command.py::test_a_skill_that_cannot_be_evaluated_ends_5_runs_nothing_and_records_nothing`, `test_w2_104_run.py::test_a_passing_skill_ends_0_with_three_passes_in_the_envelope`, `test_w2_104_run.py::test_the_record_beside_the_skill_has_one_entry_per_scenario`, `test_w2_104_run.py::test_a_second_run_appends_and_keeps_the_earlier_entries`, `test_w2_104_run.py::test_each_scenario_runs_on_a_fresh_session_with_only_that_skill_loaded`, `test_w2_104_run.py::test_every_model_process_is_new_and_uses_the_default_model_and_effort`, `test_w2_104_run.py::test_the_judgement_is_a_separate_process_given_the_pass_line_the_expected_and_the_reply`, `test_w2_104_run.py::test_model_and_effort_options_replace_the_defaults`, `test_w2_104_run.py::test_a_skill_in_w2_11s_form_with_wrapped_bullets_is_evaluated`, `test_w2_104_run.py::test_a_skill_named_by_an_absolute_path_from_a_folder_outside_the_project` | help: gov --help does not offer skilleval; the others: exit 2, invalid choice: 'skilleval' |
| **Success 2:** an import is adopted only with source, version, licence and licence verdict recorded in governance/project/skill-imports.yaml and three passing scenarios; refused otherwise | adopted with a full allowing record and three passes, other entries unchanged; refused (exit 6, ends adopted false) for each gap in the record (7 variants), no entry, no record file, or not three passes (3 variants); without --adopt nothing changes adopted (2 variants) | `test_w2_104_imports.py::test_a_recorded_allowed_import_whose_three_scenarios_pass_is_adopted`, `test_w2_104_imports.py::test_an_import_without_a_full_allowing_licence_record_is_refused`, `test_w2_104_imports.py::test_an_import_with_no_entry_is_refused`, `test_w2_104_imports.py::test_an_import_with_no_import_record_file_is_refused`, `test_w2_104_imports.py::test_an_import_with_a_full_licence_record_but_not_three_passes_is_refused`, `test_w2_104_imports.py::test_without_adopt_the_harness_never_changes_adopted` | exit 2, invalid choice: 'skilleval' |
| **Success 3:** a run that cannot reach a model is recorded as not run with its cause, never a pass; no secret read or printed | not run, with a one-line cause and no cost, for a session that exits non-zero, prints no JSON or reports is_error; a judgement that exits non-zero; no claude on the PATH; a session past --timeout; a fail beside a not-run ends 3; and the secrets cases of F3 | `test_w2_104_not_run.py::test_a_session_that_fails_answers_badly_or_reports_an_error_is_not_run`, `test_w2_104_not_run.py::test_a_judgement_that_fails_leaves_its_scenario_not_run`, `test_w2_104_not_run.py::test_no_claude_on_the_path_leaves_every_scenario_not_run`, `test_w2_104_not_run.py::test_a_session_past_the_timeout_is_not_run`, `test_w2_104_not_run.py::test_a_failed_scenario_beside_a_not_run_one_ends_3`, `test_w2_104_secrets.py::test_a_stub_that_prints_the_key_and_fails_leaks_nothing_through_gov`, `test_w2_104_secrets.py::test_a_passing_run_prints_and_records_no_planted_secret`, `test_w2_104_secrets.py::test_the_harness_does_not_read_a_secrets_file_in_the_project` | exit 2, invalid choice: 'skilleval' |
| **Success 4:** planted skills with a passing and a failing scenario give the expected verdicts, temporary project, stub model | a passing skill gives three passes; a FAIL and an unanswered judgement give fail; the last verdict line of the judgement's reply decides, and the session's own verdict line is not read (every case uses a planted skill in a temporary project and the stub) | `test_w2_104_run.py::test_a_passing_skill_ends_0_with_three_passes_in_the_envelope`, `test_w2_104_run.py::test_a_failing_and_an_unanswered_judgement_give_fail_and_exit_3`, `test_w2_104_run.py::test_the_verdict_is_the_last_verdict_line_of_the_judgements_reply_only` | exit 2, invalid choice: 'skilleval' |
| **F1:** a scenario reported as passing that did not run, or failed | did not run: each not-run case (the stub's judgement would say PASS if asked); failed: a FAIL or no verdict line, PASS then FAIL last, a session that says PASS itself | `test_w2_104_not_run.py::test_a_session_that_fails_answers_badly_or_reports_an_error_is_not_run`, `test_w2_104_not_run.py::test_a_judgement_that_fails_leaves_its_scenario_not_run`, `test_w2_104_not_run.py::test_no_claude_on_the_path_leaves_every_scenario_not_run`, `test_w2_104_not_run.py::test_a_session_past_the_timeout_is_not_run`, `test_w2_104_not_run.py::test_a_failed_scenario_beside_a_not_run_one_ends_3`, `test_w2_104_run.py::test_a_failing_and_an_unanswered_judgement_give_fail_and_exit_3`, `test_w2_104_run.py::test_the_verdict_is_the_last_verdict_line_of_the_judgements_reply_only` | exit 2, invalid choice: 'skilleval' |
| **F2:** an import marked adopted with no licence record or a failing scenario | each gap in the licence record (7 variants: empty source, version or licence, no licence key, verdict denied or unknown, no verdict key; each entry starts adopted true and must end false); no entry; no record file; not three passes (3 variants: a fail, no verdict, not run); --adopt on a skill that cannot be evaluated | `test_w2_104_imports.py::test_an_import_without_a_full_allowing_licence_record_is_refused`, `test_w2_104_imports.py::test_an_import_with_no_entry_is_refused`, `test_w2_104_imports.py::test_an_import_with_no_import_record_file_is_refused`, `test_w2_104_imports.py::test_an_import_with_a_full_licence_record_but_not_three_passes_is_refused`, `test_w2_104_command.py::test_adopt_on_a_skill_that_cannot_be_evaluated_ends_5_and_adopts_nothing` | exit 2, invalid choice: 'skilleval' |
| **F3:** a secret read or printed | the stub prints the planted values on stderr, as non-JSON stdout or in an is_error reply (2 variants: --json and text); a passing run; the .env made unreadable, so a harness that opens it fails | `test_w2_104_secrets.py::test_a_stub_that_prints_the_key_and_fails_leaks_nothing_through_gov`, `test_w2_104_secrets.py::test_a_passing_run_prints_and_records_no_planted_secret`, `test_w2_104_secrets.py::test_the_harness_does_not_read_a_secrets_file_in_the_project` | exit 2, invalid choice: 'skilleval' |

43 cases in all.

## What the cases hold, and what they leave open

Held, as the contract states: the exit codes 0, 3, 4, 5 and 6; with `--json`, `result` with `skill`,
`skill_version`, `scenarios` (each with `scenario`, `title`, `verdict`, `cause`, `cost_usd`, `seconds`), `record`
and `adopted` (null without `--adopt`). `scenario-records.yaml` beside the skill, a map with `records`, with
entries appended and earlier ones kept as written, each with the contract's fields: `cause` null for a pass, a
string for a fail, one non-empty line for a not-run; `cost_usd` a number for a pass or fail, null when not run;
`run_at` an ISO 8601 UTC string within the run. Each session runs in a new folder outside the project, whose
`.claude/skills/` holds exactly one folder with the evaluated skill's `SKILL.md`, and no `scenarios.md` under it.
Each prompt goes on standard input, `-p --model --effort --output-format json` are among the arguments, and no
`--resume`, `--continue`, `-r` or `-c` is passed. The judgement is a separate process whose prompt holds the Pass
line, the Expected text and the session's reply. Whitespace is compared collapsed, because W2-11's bullets wrap.

Left open, so not tested: the cost's make-up (session, judgement or both), the cause's wording, how the session
folder's skill folder is named, whether scenarios run before a licence refusal, whether the import record is
created when it is missing, the order of the record's entries within one run, the judgement's working folder,
the default timeout of 900 s, and whether the environment is stripped.

## The revision of earlier suites (DEC-747)

A new `gov` command is recorded in the tests' command list (DEC-747; the way `1bf0c1d2` recorded `accept`). In a
commit of its own, with `Rewrite-Reason: DEC-747: the new gov command skilleval is recorded in the tests' command
list`:

- `tests/acceptance/W1-07/w1_07_support.py`: `skilleval` added to `RECORDED_GOV_COMMANDS`;
- `tests/acceptance/W1-07/test_w1_07_recorded_commands.py`: the pinned sorted list gains `skilleval`;
- `tests/acceptance/W1-07/README.md`: the line naming the list;
- `tests/acceptance/W1-32/test_w1_32_command_set.py`: the pinned set gains `skilleval`.

No other suite holds the set as an exact list. `tests/acceptance/W1-26/test_w1_26_recorded_commands.py` reads
W1-07's list, so it gains `[skilleval]` variants. These hold the product's own list, `RECORDED_GOV_COMMANDS` in
`src/gov/check/commands.py`, which is not in this ticket's `allowed_paths` (package P-W2-104-CMDLIST, in the
designer's return).
