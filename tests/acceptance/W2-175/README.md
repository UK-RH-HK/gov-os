# W2-175 acceptance tests: the role templates' Policy 2, record rule and stop lines

Ticket DAEO-wahn (W2-175), profile STANDARD. Written by the independent test designer (MR-3) before any
implementation, from the ticket's KPI lines and its "Interface" section (DEC-1109 (2)), reading the base templates
(this tree, equal to `w2/integrate` for `template/governance/kernel/templates/`), W2-128's cases and support module,
`docs/changes/W2-128-CIT-P.md` (the form of a CIT-P record), `governance/project/facts.yaml`, `keys.yaml` and
DEC-820, DEC-861, DEC-1116, DEC-1121 and DEC-1137 in the register. Nothing of this ticket's implementation
(`w2/W2-175`, its worktree) was read.

## How they run

    env HOME=<empty folder> PYTHONUSERBASE=$HOME/.local PYTHONPATH=<worktree>/src \
      python3 -m pytest tests/acceptance/W2-175 -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
      -m "not local_only" -k "not real and not green_here and not time_limit"

Under a second. No model, no network, no store. The cases need `git` (they read each template's base with
`git show`) and `PyYAML`; they import W2-128's support module (`tests/acceptance/W2-128/w2_128_support.py`) for its
statement reader, so W2-128's folder must be present.

## What the cases read, and how

- **A statement** is one of W2-128's `units` of the template's body (front matter left out): a paragraph, a list
  item or a table row, wrapped lines joined, a line ending with a bracketed decision id closing its unit. Needles
  are matched in it case-folded with white space collapsed (W2-128's `fold`). The Interface's exact wording is not
  required (a template may shorten a line), only the KPI line's needles, all in one statement.
- **"Ends with `[DEC-n]`"** reads: the statement's last bracket cites DEC-n, with a full stop or parenthesis after it
  allowed. `[DEC-820]` and `[DEC-820, DEC-957]` both end citing DEC-820.
- **Success 1** (seven cases): one statement holds `read`, `open`, `secret`, `held-out`, `counterpart` and
  `hidden half` and ends citing DEC-820.
- **Success 2** (three cases): the engineer's statement holds a negation (`never` or `not`), `acceptance`, `code`
  (or `source`, DEC-820's own word), `run`, `name`, `pass`, `fail` and `message`; the designer's holds a negation,
  `implementation` or `branch` (the base line's "what this ticket's branch changes", which the Interface says to
  keep), `specification`, `kpi` and `existing code`; the reviewer's holds `read`, `everything`, `tests` and `code`.
- **Success 3** (six cases and one guard): one statement holds `decision-record`, `owner`, `Role: owner` and
  `Decided-by` (the KPI line names both trailers), a negation from W2-128's set (`no`, `never`, `not`, …: the line
  says no worker or lead puts them), and ends citing DEC-861. The role-cto case reads the base's decision-record line
  (`Task: decision-record`, `Role: orchestrator`, `Decided-by: owner (chat, {DATE})`, `[DEC-861]`) from
  `git show a6c83d497035:template/governance/kernel/templates/role-cto.md` and finds it unchanged, byte for byte,
  as a line of today's file.
- **Success 4 and failure 1**: one helper (`w2_175_support.stop_problem`) checks that a text holds
  `Refused twice for the same call: stop and say so. Never work around a refusal: report it.` character for
  character, with runs of white space folded to one space (a line wrap changes no word). The same helper judges the
  seven templates, `brief.md` (the one source of the wording) and failure 1's planted copies.
- **Success 5**: each template's front matter parses, `version` is the string `1.0.1`, and every other key equals
  the base's. **The base** of each file is the last commit that changed it before this ticket, never an older one:
  `a6c83d497035` (W2-128 round 1) for role-cto, role-engineer, role-product-spec and role-reviewer; `baa2696f713f`
  (W2-128 round 1 fixes) for role-lead, role-research and role-test-designer (found with
  `git log -1 w2/integrate -- <path>`; both are version 1.0.0, approved by DEC-1116). The commits are pinned rather
  than read from `w2/integrate`, so the reading stays right after this ticket merges (integrate then holds the new
  bytes). Each case first checks the premise that the file at its base is the 1.0.0 template of its name.
- **Success 7**: `docs/changes/W2-175-CIT-P.md` as the tree holds it.
  - Front matter `decisions_read` and `decisions_carried` each cite DEC-1137, DEC-820 and DEC-861 (a list or a
    string; `DEC-1137 (2)` counts).
  - **A section per CAP-33 step**, read loosely: a heading (level 2 or more) or a table row's first cell (W2-128's
    record keeps its steps as rows of a "CAP-33's steps" table) names each step, each step its own section or row:
    evidence (`evidence` or `trigger`), proposal (`propos`, `what changes` or `delta`), independent review
    (`review`), owner's approval (`approv`), versioned promotion (`promot`). An honest writer using the five step
    names, as headings or as W2-128's table, passes.
  - `status` is PROPOSED, ACCEPTED or APPLIED; ACCEPTED or APPLIED only when an owner's-approval section or row
    records an approval (not empty, not "pending", naming a DEC id or a date). **The record is never required to be
    ACCEPTED**: the owner's approval follows the review, after the lead returns.
  - For each of the seven files, a table row naming `<stem>.md` holds the file's sha256 at the head (computed from
    the tree's bytes at run time) and its base sha256 (from `git show` of its base commit, the bytes the branch
    starts from, as the KPI line's "its base and new sha256").

## Cases of other folders this map relies on (named, not re-written)

`gov accept` collects only this folder, so these are named here as notes and not mapped (a mapped name with no
collected case would read "fail with 0 cases"). The lead runs them with the ticket's success 6 command.

- Success 2: `tests/acceptance/W2-128/test_w2_128_templates.py::test_s3_engineer_template_holds_no_instruction_to_read_the_acceptance_tests`
  still passes (the engineer's statement carries its negation).
- Success 5: `tests/acceptance/W2-128/test_w2_128_templates.py::test_s2_prose_is_within_r3_budget` (all seven
  parameters) and `::test_s5_every_key_placeholder_is_in_keys_yaml` pass.
- Failure 1: `tests/acceptance/W2-128/test_w2_128_templates.py::test_f7_every_bracketed_decision_id_in_a_template_is_accepted`
  passes for the seven files.

## KPI lines, tests and the outcome on the base

Red on the base means the case fails there for the reason given; green (guard) means it passes there by design and
must stay green.

### Success 1: reads open and the four refusals in each of the seven templates

| Test | On the base | Why |
|---|---|---|
| `test_w2_175_templates.py::test_s1_one_statement_says_reads_are_open_and_names_the_four_refusals[role-cto]` | red | no statement names the four refusals or ends citing DEC-820 |
| `test_w2_175_templates.py::test_s1_one_statement_says_reads_are_open_and_names_the_four_refusals[role-engineer]` | red | as above |
| `test_w2_175_templates.py::test_s1_one_statement_says_reads_are_open_and_names_the_four_refusals[role-lead]` | red | as above |
| `test_w2_175_templates.py::test_s1_one_statement_says_reads_are_open_and_names_the_four_refusals[role-product-spec]` | red | as above |
| `test_w2_175_templates.py::test_s1_one_statement_says_reads_are_open_and_names_the_four_refusals[role-research]` | red | as above |
| `test_w2_175_templates.py::test_s1_one_statement_says_reads_are_open_and_names_the_four_refusals[role-reviewer]` | red | as above |
| `test_w2_175_templates.py::test_s1_one_statement_says_reads_are_open_and_names_the_four_refusals[role-test-designer]` | red | its one DEC-820 line names only the counterpart half: no open reads, no secret, held-out or hidden half |

### Success 2: the counterpart refusal in each role's own half

| Test | On the base | Why |
|---|---|---|
| `test_w2_175_templates.py::test_s2_engineer_never_reads_the_acceptance_test_code_and_may_run_the_cases_and_see_results` | red | the engineer's line on the acceptance cases says "pass or fail per KPI line, never their text": no code, no names, no failure messages |
| `test_w2_175_templates.py::test_s2_test_designer_never_reads_the_implementation_and_works_from_specification_kpis_and_code` | red | the designer's line says only the first half: no specification, KPI lines or existing code |
| `test_w2_175_templates.py::test_s2_reviewer_reads_everything_tests_and_code_alike` | red | "you read everything" is in the title and "the tests, the code" in another line: no one statement holds both |

### Success 3: the record rule, and role-cto's decision-record line unchanged

| Test | On the base | Why |
|---|---|---|
| `test_w2_175_templates.py::test_s3_one_statement_says_owner_decisions_are_recorded_by_decision_record_commits[role-engineer]` | red | no statement cites DEC-861 or names decision-record commits |
| `test_w2_175_templates.py::test_s3_one_statement_says_owner_decisions_are_recorded_by_decision_record_commits[role-lead]` | red | as above |
| `test_w2_175_templates.py::test_s3_one_statement_says_owner_decisions_are_recorded_by_decision_record_commits[role-product-spec]` | red | as above |
| `test_w2_175_templates.py::test_s3_one_statement_says_owner_decisions_are_recorded_by_decision_record_commits[role-research]` | red | as above |
| `test_w2_175_templates.py::test_s3_one_statement_says_owner_decisions_are_recorded_by_decision_record_commits[role-reviewer]` | red | as above |
| `test_w2_175_templates.py::test_s3_one_statement_says_owner_decisions_are_recorded_by_decision_record_commits[role-test-designer]` | red | as above |
| `test_w2_175_templates.py::test_s3_role_cto_keeps_its_decision_record_commit_line_byte_for_byte` | green (guard) | the base's line is in the base's file; it must stay unchanged |

### Success 4: the stop sentence of brief.md, word for word, in each template

| Test | On the base | Why |
|---|---|---|
| `test_w2_175_templates.py::test_s4_template_holds_the_stop_sentence_word_for_word[role-cto]` | red | the sentence is in no role template |
| `test_w2_175_templates.py::test_s4_template_holds_the_stop_sentence_word_for_word[role-engineer]` | red | as above |
| `test_w2_175_templates.py::test_s4_template_holds_the_stop_sentence_word_for_word[role-lead]` | red | as above |
| `test_w2_175_templates.py::test_s4_template_holds_the_stop_sentence_word_for_word[role-product-spec]` | red | as above |
| `test_w2_175_templates.py::test_s4_template_holds_the_stop_sentence_word_for_word[role-research]` | red | as above |
| `test_w2_175_templates.py::test_s4_template_holds_the_stop_sentence_word_for_word[role-reviewer]` | red | as above |
| `test_w2_175_templates.py::test_s4_template_holds_the_stop_sentence_word_for_word[role-test-designer]` | red | as above |
| `test_w2_175_templates.py::test_s4_the_stop_sentence_is_brief_md_s_own` | green (guard) | brief.md's return section holds it; the ticket must not change brief.md |

### Success 5: version 1.0.1, every other front matter key the base's

| Test | On the base | Why |
|---|---|---|
| `test_w2_175_templates.py::test_s5_front_matter_is_version_1_0_1_and_otherwise_the_base_s[role-cto]` | red | version is 1.0.0 |
| `test_w2_175_templates.py::test_s5_front_matter_is_version_1_0_1_and_otherwise_the_base_s[role-engineer]` | red | version is 1.0.0 |
| `test_w2_175_templates.py::test_s5_front_matter_is_version_1_0_1_and_otherwise_the_base_s[role-lead]` | red | version is 1.0.0 |
| `test_w2_175_templates.py::test_s5_front_matter_is_version_1_0_1_and_otherwise_the_base_s[role-product-spec]` | red | version is 1.0.0 |
| `test_w2_175_templates.py::test_s5_front_matter_is_version_1_0_1_and_otherwise_the_base_s[role-research]` | red | version is 1.0.0 |
| `test_w2_175_templates.py::test_s5_front_matter_is_version_1_0_1_and_otherwise_the_base_s[role-reviewer]` | red | version is 1.0.0 |
| `test_w2_175_templates.py::test_s5_front_matter_is_version_1_0_1_and_otherwise_the_base_s[role-test-designer]` | red | version is 1.0.0 |

The budget and placeholder halves of this line are W2-128's cases (notes above).

### Success 6: the cases of the three earlier tickets still pass

No case here. The ticket's own command, run by the lead in the ticket's worktree through the heavy-job gate:
`PYTHONPATH=<worktree>/src python3 -m pytest tests/acceptance/W2-128 tests/acceptance/W2-152 tests/acceptance/W2-153 -q -p no:cacheprovider`
exits 0.

### Success 7: the CIT-P record

| Test | On the base | Why |
|---|---|---|
| `test_w2_175_record.py::test_s7_record_front_matter_cites_dec_1137_dec_820_and_dec_861[decisions_read]` | red | the record does not exist |
| `test_w2_175_record.py::test_s7_record_front_matter_cites_dec_1137_dec_820_and_dec_861[decisions_carried]` | red | the record does not exist |
| `test_w2_175_record.py::test_s7_record_has_an_entry_for_each_cap_33_step` | red | the record does not exist |
| `test_w2_175_record.py::test_s7_record_status_is_accepted_only_with_the_owner_s_approval` | red | the record does not exist |
| `test_w2_175_record.py::test_s7_record_sha256_of_each_template_is_its_sha256_at_the_head[role-cto]` | red | the record does not exist |
| `test_w2_175_record.py::test_s7_record_sha256_of_each_template_is_its_sha256_at_the_head[role-engineer]` | red | the record does not exist |
| `test_w2_175_record.py::test_s7_record_sha256_of_each_template_is_its_sha256_at_the_head[role-lead]` | red | the record does not exist |
| `test_w2_175_record.py::test_s7_record_sha256_of_each_template_is_its_sha256_at_the_head[role-product-spec]` | red | the record does not exist |
| `test_w2_175_record.py::test_s7_record_sha256_of_each_template_is_its_sha256_at_the_head[role-research]` | red | the record does not exist |
| `test_w2_175_record.py::test_s7_record_sha256_of_each_template_is_its_sha256_at_the_head[role-reviewer]` | red | the record does not exist |
| `test_w2_175_record.py::test_s7_record_sha256_of_each_template_is_its_sha256_at_the_head[role-test-designer]` | red | the record does not exist |
| `test_w2_175_record.py::test_s7_record_names_each_template_s_base_sha256[role-cto]` | red | the record does not exist |
| `test_w2_175_record.py::test_s7_record_names_each_template_s_base_sha256[role-engineer]` | red | the record does not exist |
| `test_w2_175_record.py::test_s7_record_names_each_template_s_base_sha256[role-lead]` | red | the record does not exist |
| `test_w2_175_record.py::test_s7_record_names_each_template_s_base_sha256[role-product-spec]` | red | the record does not exist |
| `test_w2_175_record.py::test_s7_record_names_each_template_s_base_sha256[role-research]` | red | the record does not exist |
| `test_w2_175_record.py::test_s7_record_names_each_template_s_base_sha256[role-reviewer]` | red | the record does not exist |
| `test_w2_175_record.py::test_s7_record_names_each_template_s_base_sha256[role-test-designer]` | red | the record does not exist |

### Failure 1: a stop sentence changed by one letter fails the check

| Test | On the base | Why |
|---|---|---|
| `test_w2_175_templates.py::test_f1_a_stop_sentence_changed_by_one_letter_fails_the_s4_check` | green (guard) | a planted copy of each template in tmp_path, its sentence changed by one letter, fails the helper; the same copy word for word passes |

The decision-id half of this line is W2-128's `test_f7` case (notes above).

### Failure 2: the ticket's diff names a file beyond its paths

No case here: a close-time check over the branch's diff against its base, which the tests cannot name stably. The
lead checks that
`git diff --name-only <BASE>..HEAD -- . ':!tests/acceptance/W2-175'`
lists only the seven `template/governance/kernel/templates/role-*.md` files and `docs/changes/W2-175-CIT-P.md`
(no `brief.md`, `brief-*.md`, `keys.yaml`, `facts.yaml`, skill, `roles/`, `.claude/` or `.rulesync/` path).

## Counts on the base

51 cases: 48 red, 3 green by design (success 3's role-cto line, success 4's brief.md source, failure 1's mutation).
