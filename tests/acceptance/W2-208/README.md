# W2-208 acceptance tests: the kit after Emergency 2

Ticket DAEO-kt8e (W2-208), profile FULL, class F. Written by the independent test designer (MR-3) from the ticket's six
success lines (K1 to K6), its two failure lines (F1, F2) and its `## Interface` section, before any implementation, on
the base `8e72e0228`. Sources read: the ticket, the lead's brief `docs/emergency-2/briefs/LEAD-kit-e2.md` (the head's
text), `NIGHT-COMMON.md`, `LEAD-COMMON.md`, EMERGENCY-2 sections 2 and 3, DEC-1217, and the integrated code the tests
drive (`gov adapters generate`, `gov update`, `python3 -m gov.adapters.portability`, W2-16's and W2-17's acceptance
support). Nothing of this ticket's implementation was read.

## How they run

    T=$(mktemp -d); TMPDIR=$T PYTHONPATH=<worktree>/src PATH=<node bin>:$PATH bash <heavy_slot.sh> \
      python3 -m pytest tests/acceptance/W2-208 -q -p no:cacheprovider -n auto; rm -rf $T

36 cases (24 functions), all of the acceptance kind but the three K6 cases, which are **repository-state** (they read
this repository's own `CLAUDE.md` and `AGENTS.md` against the base commit `8e72e0228`). No model, no network, never
the real `~/.gov-os`: every `gov` child runs with a fake `HOME` under pytest's temporary folder; `rulesync` (24.0.0)
and `copier` are the installed ones, node is found on `PATH`. A whole run takes about a minute.

## What is planted

- **A project adopted from the kit** (`w2_208_support.template_project`): this worktree's `template/` copied (its
  `.jinja` files left out), a git repository; optionally the held-out file `governance/project/held-out.yaml` of two
  absolute paths and the tool registry naming the installed rulesync. `gov adapters generate` runs there.
- **The planted source** (`build_source`, on W2-16's stand-in Gov OS repository and its owner-in-person release seam,
  imported from W2-16 and W2-17): release **A0** (0.9.0) stands for 0.1.0 (no permission source at all; the base's
  head, kernel settings and `judging-work` skill, kept in `data/legacy/`); **A1** (0.9.1) stands for 0.1.3 (as A0 plus
  the base's permission source: `Edit(.tickets/**)` and `sudo *` denied, `gov launch:*` allowed); **B** (0.9.2) is this
  worktree's kit with one marker line appended to the head, so B's head differs from A's whatever the worktree holds.
  Each is tagged `v<version>` on its record commit. No real 0.1.0 or 0.1.3 is needed.
- **The EXAMIN-like project** (`examin_013`): adopted at A1 by `copier copy` and `gov adapters generate` (W2-17's
  `adopt`), then planted as update 0.1.3 left EXAMIN: the held-out file, the legacy lines in `.claude/settings.json`
  (`Edit(.tickets/**)`, `Read(//srv/w2-208/eval-set/**)`, `Read(//srv/w2-208/workbench/**)`, the allow
  `Bash(gov launch:*)`), the owner's deny `Bash(rm -rf *)` and allow `Bash(npm test:*)`, and the project's own lines
  above the generated block of `CLAUDE.md` and `AGENTS.md`; committed. **`examin_010`**: adopted at A0, holding the
  held-out file and only the legacy lines.
- **The updates**, each in its own copy: `gov update 0.9.2 --json` from `examin_013` and from `examin_010`;
  `gov update 0.9.2 --check --json` then `--check` (text) from `examin_013`; and (F2) `gov update 0.9.2 --json` from
  `examin_013` with a fixture `rulesync` first on `PATH` that runs the real one and then, when its input root is the
  project's own `.rulesync/` (the project holds `governance/framework.lock`), rewrites the project's
  `permissions.deny` without `Bash(rm -rf *)`. Checked on the base: that rulesync does lose the line, and the base's
  update commits without it.
- **Shared across workers**: the source, the adoptions and the four updates are built once per run under a file lock
  in the run's common temporary folder; cases only read them. A fixture that cannot be built fails its cases with
  "W2-208 fixture could not be built (not the feature under test)".

## The map

KPI ids name the ticket's lines by position: success 1 to 6 are K1 to K6, failure 1 and 2 are F1 and F2. "Red on the
base": what fails on `8e72e0228`.

| KPI id | tests | expected red reason |
|---|---|---|
| S1 (K1) | `test_w2_208_k1_settings.py::test_k1_the_permission_source_holds_the_two_deny_lines_under_bash_and_nothing_else` | the source holds the `.tickets/**` edit deny and the `gov launch:*` allow, and no `git push *` |
| S1 (K1) | `test_w2_208_k1_settings.py::test_k1_the_kernel_settings_hold_no_allow_and_no_deny_but_the_two` | the kernel settings allow `Bash(gov launch:*)` |
| S1 (K1) | `test_w2_208_k1_settings.py::test_k1_a_project_adopted_from_the_kit_holds_exactly_the_two_deny_lines` | deny is `Bash(sudo *)`, `Edit(.tickets/**)` (no `git push`); with the held-out file, two `Read(` lines |
| S1 (K1) | `test_w2_208_k1_settings.py::test_k1_lines_the_owner_wrote_by_hand_are_kept_beside_the_two_by_a_second_generate` | deny holds `Edit(.tickets/**)` and the `Read(` lines, no `git push` |
| S1 (K1) | `test_w2_208_k1_settings.py::test_k1_a_project_adopted_by_copier_at_release_b_holds_exactly_the_two_deny_lines` | deny is `Bash(sudo *)`, `Edit(.tickets/**)` |
| S2 (K2) | `test_w2_208_k2_update.py::test_k2_update_from_0_1_3_leaves_the_two_deny_lines_and_the_owners_own_lines` | the update puts back `Edit(.tickets/**)` and keeps the `Read(` lines; no `git push` |
| S2 (K2) | `test_w2_208_k2_update.py::test_k2_the_report_and_the_record_list_the_four_removed_lines` | the report has no `settings` entry with `removed` |
| S2 (K2) | `test_w2_208_k2_update.py::test_k2_update_from_0_1_0_without_a_permission_source_ends_the_same` | the legacy lines stay (`Edit(.tickets/**)`, the `Read(` lines) |
| S2 (K2) | `test_w2_208_k2_update.py::test_k2_check_names_the_settings_change_and_writes_nothing` | the dry run's report has no `settings` entry with `removed` |
| S3 (K3) | `test_w2_208_k3_heldout.py::test_k3_write_read_rules_is_no_longer_defined` | `gov.util.heldout` still defines `write_read_rules` |
| S3 (K3) | `test_w2_208_k3_heldout.py::test_k3_load_held_out_still_returns_the_paths_and_refuses_a_malformed_file` | none: a guard, green on the base and to stay green (`load_held_out` and `HeldOutError` stay) |
| S3 (K3) | `test_w2_208_k3_heldout.py::test_k3_generate_with_a_held_out_file_writes_no_read_line_and_runs_no_held_out_step` | well-formed: two `Read(` lines written; malformed: `ADAPTERS_HELD_OUT_STEP_FAILED`, exit 1 |
| S3 (K3) | `test_w2_208_k3_heldout.py::test_k3_the_adapter_check_applies_no_held_out_step` | well-formed: `GENERATED_DIFFERS` on `.claude/settings.json` (the check adds the `Read` rules); malformed: `HELD_OUT_STEP_FAILED` |
| S3 (K3) | `test_w2_208_k3_heldout.py::test_k3_update_leaves_no_read_line_and_does_not_mention_the_held_out_step` | the two `Read(` lines are in the settings after the update |
| S4 (K4) | `test_w2_208_k4_head.py::test_k4_the_head_source_keeps_its_front_matter_and_holds_the_heads_text_then_the_roles` | the head source does not begin with the head's words (the old text) |
| S4 (K4) | `test_w2_208_k4_head.py::test_k4_adoption_generates_the_head_into_both_files_and_keeps_the_projects_own_lines` | the generated block holds the old head |
| S4 (K4) | `test_w2_208_k4_head.py::test_k4_a_project_adopted_by_copier_at_release_b_carries_bs_head` | the generated block holds the old head |
| S4 (K4) | `test_w2_208_k4_head.py::test_k4_after_the_update_the_block_is_bs_and_the_projects_own_lines_are_unchanged` | the block after the update holds the old head |
| S5 (K5) | `test_w2_208_k5_skill.py::test_k5_the_two_copies_are_byte_equal_shipped_carry_the_rules_and_raise_the_version` | the skill lacks `same-privilege adversary` and the Value-first rule (its version is still 1.1.0) |
| S5 (K5) | `test_w2_208_k5_skill.py::test_k5_the_skill_and_the_head_share_the_key_phrase_of_each_of_the_four_rules` | the head holds none of the key phrases; the skill lacks two |
| S5 (K5) | `test_w2_208_k5_skill.py::test_k5_after_adoption_the_generated_skill_is_the_templates` | the generated skill lacks `same-privilege adversary` and the Value-first rule |
| S5 (K5) | `test_w2_208_k5_skill.py::test_k5_after_the_update_the_generated_skill_is_the_templates` | as above, after the update |
| S6 (K6) | `test_w2_208_k6_instructions.py::test_k6_the_file_adds_the_value_first_line_in_its_golden_rule_section_and_removes_none` | `CLAUDE.md` and `AGENTS.md` add nothing to the base |
| S6 (K6) | `test_w2_208_k6_instructions.py::test_k6_the_two_files_golden_rule_sections_stay_equal` | the sections are equal but hold no Value first line |
| F1 | `test_w2_208_f1_kit_text.py::test_f1_a_head_naming_the_guard_sandbox_or_prompt_in_force_is_a_finding_by_name` | `gov.adapters.portability.kit_text_findings` does not exist (ImportError) |
| F1 | `test_w2_208_f1_kit_text.py::test_f1_the_kernel_copy_of_the_skill_is_in_the_checked_files` | `kit_text_findings` does not exist |
| F1 | `test_w2_208_f1_kit_text.py::test_f1_a_line_saying_they_are_retired_is_no_finding` | `kit_text_findings` does not exist |
| F1 | `test_w2_208_f1_kit_text.py::test_f1_the_shipped_head_and_skill_give_no_finding` | `kit_text_findings` does not exist |
| F2 | `test_w2_208_f2_owner_line.py::test_f2_an_update_that_loses_the_owners_deny_line_fails_naming_it_and_rolls_back` | `gov update` exits 0 and commits the settings without `Bash(rm -rf *)` |

Count per line: K1 5 functions (6 cases), K2 4, K3 5 (7 cases), K4 4, K5 4, K6 2 (3 cases), F1 4 (7 cases), F2 1.

Red run on the base (through the heavy slot, `-n auto`, at `8e72e0228` plus these tests): **35 failed, 1 passed in
47.50 s**. Every failure is for the reason in the map, none a fixture error; the one pass is K3's `load_held_out` guard.

## Readings where the ticket is open

- **"After `gov adopt`"** is read as the adoption a project gets: `copier copy` of the kit (or its `template/` copied)
  and `gov adapters generate`; `gov adopt --lite` stages do not generate adapters.
- **Exact lines**: "exactly two deny lines" is compared as a list with no line twice, in any order; "no allow line the
  kit wrote" is `permissions.allow` absent or empty (or the owner's lines alone where the owner wrote some). The kernel
  settings may hold the two deny lines or none.
- **The four removed lines** (K2) are compared as a set with `settings.removed` of the `--json` report and of
  `governance/updates/0.9.2.json`; the dry run's text form must name `settings` and each of the four lines.
- **The held-out step "mentioned"** (K3): the output matches neither `held-out step` (any separator) nor
  `HELD_OUT_STEP`. A malformed held-out file is no longer any step's business: `gov adapters generate` exits 0 and
  the check gives no `HELD_OUT_*` finding.
- **The head** (K4): compared with the brief's block (`data/head.md`, copied verbatim) with whitespace collapsed, so a
  rewrap is no difference. The roles after it: each of the nine names in bold (`**engineer**`); the role's one line is
  not compared. The old text: no `Guard` heading, no `under the guard`, `CIT-P`, `CIT-E`, `CAP-33` or `Proposing
  changes`. **AGENTS.md**: rulesync 24.0.0 writes a preamble of its own at the top of AGENTS.md ("# Additional
  Conventions Beyond the Built-in Functions" and one sentence), before the head; the block of each file is read from
  its first `# Governance` line, and the two blocks are compared from there. The project's own lines above the block:
  after `gov adapters generate` the own text stands unchanged before the block (the merge adds one blank line); after
  the update the text outside the block is byte-identical to before.
- **The skill** (K5): "equals the template's" is the body after the front matter (rulesync rewrites the front matter's
  quoting). The key phrases are matched case-insensitively with whitespace collapsed; the Value-first rule is `value
  first` and `tests and code that match the KPIs and the spec`. "Version raised" is `version` (and `metadata.version`
  where present) above 1.1.0, the base's.
- **K6** compares each file with the base by lines: none removed, and the added lines, joined, are the Value first
  bullet (whitespace collapsed), inside the `## Golden rule` section.
- **F1's file and line**: `file` is the path relative to the project (an absolute path ending in it is accepted), `line`
  the 1-based line number in the file, front matter counted. For the `## Guard` section either its heading or its
  sentence may be the line named. The function is called in a child process with the project's root as a `Path`.
- **F2**: the failure is read from the `--json` envelope: exit non-zero, the message and details naming
  `Bash(rm -rf *)` and `settings`, `details.rolled_back` true and the message saying it rolled back; HEAD and every file
  outside `.git` as before; the lock still naming A1. The fixture rulesync edits the project's settings during the
  pinned gov's `adapters generate`, before that command reads them; an implementation that rebuilt the settings from
  its own copy taken before the regeneration would not see the loss (then this case needs another plant).
- **Not tested here** (the lead's at the green step): K3's "the memaudit scan tests (`tests/unit/memaudit`) stay
  green", and K5's "after `gov adopt` and after `gov update`" for a project other than these fixtures.

## Earlier tests revised for this ticket

Each carries `Rewrite-Reason: DEC-1217 (6)` or `(7)` and the W2-208 line it follows, in its docstring or a comment
beside it; only the assertions that pinned the old behaviour changed.

- `tests/acceptance/W1-38/test_w1_38_test_folder_rule.py` (K1): the other rules of the permission source and of the
  generated settings are the two Bash deny lines, no allow; the ticket-folder case (id kept) holds the folder open.
- `tests/acceptance/W1-38/test_w1_38_heldout_step.py` (K3): the round of DEC-635 turned to "no held-out step".
- `tests/acceptance/W2-56/test_w2_56_template.py`, `tests/unit/launch/test_w2_56.py` (K1): no allow rule in the kernel
  settings, the permission source or a regeneration.
- `tests/unit/adapters/test_portability.py::TestHeldOutStep` (K3): no step, no `HELD_OUT_STEP_FAILED`,
  `write_read_rules` absent (`test_one_rule_lost_is_a_finding` retired with the step).
- `tests/acceptance/W2-195/test_w2_195_s4_shipped.py` (K5): the kernel skill and its mirror byte-equal with a version
  above 1.1.0; the wheel and the kit compared with the kernel file at HEAD.

Run on the base, those six files: **19 failed, 93 passed** (12.4 s); every failure asks for the decided state (the
held-out step, the allow rule, the ticket-folder rule or the 1.1.0 skill still there). The cases that stay as they
were are green.

## Fix MR-4 (the kit holds the model hook, the table and `defaultMode`; the root permission source matches; DEC-1246 (3)(b); under W2-208)

Written before the fix, red on the base (DEC-1246 (3)(b)). Map in the form `gov accept` reads; the KPI column names the fix line (success and failure lines of the ticket's section).

| KPI id | tests | expected red reason |
|---|---|---|
| MR-4 | `test_w2_208_mr4_kit.py::test_mr4_the_kit_holds_the_hook_file_byte_equal_to_gov_os_s_own`; `test_w2_208_mr4_kit.py::test_mr4_the_kit_holds_the_table_byte_equal_to_gov_os_s_own`; `test_w2_208_mr4_kit.py::test_mr4_the_kit_s_hook_source_has_one_pretooluse_entry_for_the_model_hook`; `test_w2_208_mr4_kit.py::test_mr4_the_root_permission_source_holds_the_kit_s_two_denies_and_nothing_else`; `test_w2_208_mr4_kit.py::test_mr4_an_adopted_project_has_the_hook_byte_equal_and_the_table`; `test_w2_208_mr4_kit.py::test_mr4_an_adopted_project_s_settings_hold_the_hook_line_once_and_default_mode`; `test_w2_208_mr4_kit.py::test_mr4_an_adopted_project_has_the_two_denies_and_no_edit_deny`; `test_w2_208_mr4_kit.py::test_mr4_the_adopted_hook_refuses_a_non_sonnet_helper_with_exit_2`; `test_w2_208_mr4_kit.py::test_mr4_the_adopted_hook_lets_a_sonnet_helper_through_with_exit_0`; `test_w2_208_mr4_kit.py::test_mr4_the_adopted_hook_writes_sonnet_into_a_spawn_with_no_model`; `test_w2_208_mr4_kit.py::test_mr4_gov_update_replaces_a_2124_byte_stand_in_byte_for_byte_and_a_second_update_changes_nothing` | the kit holds no hook file, table, `preToolUse` entry or `defaultMode` in the kit; the root permission source spells four forms; `gov update` leaves the stand-in. Guard, green: `test_mr4_gov_os_s_own_settings_are_not_changed_by_this_change` |
| MR-4 failure | `test_w2_208_mr4_kit.py::test_mr4_a_generation_in_a_scratch_repository_holds_the_hook_line_exactly_once_and_no_edit_deny` | no hook line and no `defaultMode` after generation in a scratch repository |

Uses the shared fixtures of this folder's `conftest.py` (`adopted_at_b`, `examin_013`) and `support.template_project`; never `gov adapters generate` on this repository's own tree (I-16).
