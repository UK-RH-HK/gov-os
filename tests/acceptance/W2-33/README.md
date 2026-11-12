# W2-33 (DAEO-lrre) acceptance tests: the three layers' role files and their machine-readable defaults

Written by the independent test designer from the ticket's KPI lines S1 to S9, F1 and F2 and its `## Interface`
section (DEC-1052, DEC-1156 (3), (4)), ROLES-SPEC-1 (§3.0 to §3.3, §3.8, §3.9, §5.1 and §5.2), RUBRIC-2-APPLY (lines
95 to 125) and the register's DEC-954, DEC-957, DEC-959, DEC-963, DEC-983, DEC-982, DEC-847, DEC-1010, DEC-1119,
DEC-1120, DEC-236, DEC-839, DEC-971. Nothing of the product-spec worker's work on this ticket was read (there is none
on w2/W2-33 beyond the brief's base).

## How the tests reach the files

Every test reads files and runs nothing: no child process, no network, no model, never the store. The repository is
found from `Path(__file__).resolve().parents[3]`. `w2_33_support.py` holds one checker, `role_faults(folder)`, which
returns the list of failures (each begins `"<file>: "` and names the rule and the missing or malformed line); the tests
call it on `template/governance/kernel/roles/` and, for F2, on copies planted in `tmp_path`.

* **The set of files.** The nine are required: `engineer`, `independent-auditor`, `independent-test-designer`,
  `orchestrator`, `product-spec`, `qa-engineer`, `research`, `senior-engineer`, `ticket-lead`. Every `*.md` the folder
  holds is a role file and gets its cases, so a tenth file is checked too (the parametrised cases are built from the
  folder's listing when pytest collects). A file named `README.md` (any case) is **not** a role file. `independent-reviewer.md`
  must not exist.
* **Line forms** are read as W2-60a's reader reads them (`src/gov/launch/role.py` on `w2/W2-60a`): the line is found by
  its head after `lstrip`, there must be exactly one, and the raw line must `fullmatch` the form, so it starts at
  column 0 and carries nothing after its value (no trailing full stop). Forms: `- **Version:** x.y.z`;
  `- **Launch default:** model <id>, effort <e>` (id `claude(-[a-z0-9]+)+`, effort `low|medium|high|xhigh|max`);
  `- **Skills:** a, b`; `- **Model tier:** see Launch default`; `- **Launch by criticality:** C3 model <id>, effort <e>;
  C2 ...; C1 ...; C0 ...` (the four entries in that order, separated by `; `; QA's C2 may be the full form).
* **The two sentences** (work order, one writer) must each be one line, at column 0, equal to the Interface's sentence
  (a trailing space is ignored), once per file.
* **Content statements** (S1, S3, S6, S8, S9) are judged by the KPI's own words: case-insensitive, whitespace folded,
  statements split after a full stop or a semicolon; strict on content (all the KPI's words must be there), tolerant of
  order and wording around them. Before it judges a file, each such test checks that its matcher accepts a sample
  statement written from the KPI (a fault there is the test's, not the work's).
* **Folder timing:** the whole folder runs in about a second.

## The cases per KPI line (full node ids; `[...]` ids are parametrised: a role file, a head or a planted case)

| KPI | tests | expected red reason (before the work) |
|---|---|---|
| S1 (ticket lead's file) | `test_w2_33_files.py::test_s1_ticket_lead_role_file_exists`; `test_w2_33_files.py::test_s1_ticket_lead_names_its_reads_writes_and_handover`; `test_w2_33_files.py::test_s1_orchestrator_no_longer_carries_the_ticket_lead_heading` | `ticket-lead.md` does not exist; `orchestrator.md` still has the heading `## The ticket lead` (1 line, not 0) |
| S2 (defaults per role) | `test_w2_33_lines.py::test_s2_role_file_has_version_launch_default_and_skills_lines[<role file>]` (nine); `test_w2_33_lines.py::test_s2_each_skill_a_role_file_names_exists[<role file>]` (nine); `test_w2_33_lines.py::test_s2_the_ctos_and_the_senior_engineers_file_give_effort_high[orchestrator\|senior-engineer]`; the planted file missing one key: F2 cases `version-line-removed`, `skills-line-removed`, `defaults-block-removed` | no file has a Version, Launch default or Skills line; three files do not exist |
| S3 (QA engineer) | `test_w2_33_files.py::test_s3_independent_reviewer_file_does_not_exist` (**green now**: guards that the file stays absent); `test_w2_33_files.py::test_s3_qa_engineer_role_file_exists`; `test_w2_33_files.py::test_s3_qa_engineer_reads_spec_kpis_tests_and_code_changes_none_writes_only_its_findings_report`; `test_w2_33_files.py::test_s3_qa_engineer_states_the_per_stream_rule`; `test_w2_33_files.py::test_s3_independent_auditor_still_names_the_milestone_audits` (**green now**: guards the auditor's file, which names the milestone it audits) | `qa-engineer.md` does not exist |
| S4 (work order) | `test_w2_33_lines.py::test_s4_role_file_states_the_work_order_word_for_word[<role file>]` (nine); `test_w2_33_lines.py::test_s4_allowed_paths_deny_reads_of_the_counterparts_work[engineer\|independent-test-designer]`; a planted file without it: F2 cases `work-order-altered`, `work-order-removed` | no file has the line; the two allowed-paths fields say nothing of reads of the counterpart's work |
| S5 (one writer) | `test_w2_33_lines.py::test_s5_role_file_states_one_writer_per_worktree_word_for_word[<role file>]` (nine); planted: F2 cases `one-writer-altered`, `one-writer-removed` | no file has the line |
| S6 (moderator) | `test_w2_33_files.py::test_s6_qa_engineer_states[Moderator\|Wave 3 row\|Verdict\|Rounds]` | `qa-engineer.md` does not exist |
| S7 (RUBRIC-2's table) | `test_w2_33_lines.py::test_s7_launch_lines_equal_the_table[<role file>]` (nine, and any tenth file: its Model tier line only); `test_w2_33_lines.py::test_s7_no_role_file_states_the_through_d10_rule`; planted: F2 cases `orchestrator-effort-medium`, `engineer-default-opus`, `product-spec-default-opus`, `test-designer-c3-sonnet`, `qa-c2-not-the-full-form`, `criticality-line-removed-where-it-varies`, `criticality-line-where-rubric-2-does-not-vary`, `c0-entry-malformed`, `criticality-entries-out-of-order`, `model-tier-line-changed` | no Launch default, Launch by criticality or `Model tier: see Launch default` line in any file (the Model tier line today says "standard ..." or names no tier); three files do not exist |
| S8 (senior engineer, CTO) | `test_w2_33_files.py::test_s8_senior_engineer_role_file_exists`; `test_w2_33_files.py::test_s8_senior_engineer_holds_reads_writes_skills_default_brief_and_handover`; `test_w2_33_files.py::test_s8_orchestrator_file_is_the_ctos_and_keeps_its_id` | `senior-engineer.md` does not exist; `orchestrator.md` never names the CTO |
| S9 (install rule, both copies) | `test_w2_33_install_rule.py::test_s9_the_copy_states_the_cto_only_install_rule_and_names_the_key_and_gov_ticket[<copy>]` (the kernel file and `template/.rulesync/subagents/orchestrator.md`) | neither copy states the rule; neither names `coordination_ticket` |
| F1 (old wording) | `test_w2_33_install_rule.py::test_f1_the_copy_does_not_say_the_guard_asks_on_every_install[<copy>]` | both copies say "The guard asks on every install command" (kernel file line 27, rulesync copy line 112) |
| F2 (planted departures) | `test_w2_33_planted.py::test_f2_a_planted_departure_fails_the_role_test_naming_the_file[<case>]`: 27 cases: a line form broken (8: `version-not-x-y-z`, `launch-default-without-comma`, `launch-default-with-a-full-stop`, `skills-line-indented`, `launch-default-twice`, `skills-names-a-skill-that-does-not-exist`, `model-tier-line-changed`, `criticality-entries-out-of-order`), the two sentences (4), a defaults block or a key removed (3), a value off the table (8), the roster of files (4) (`ticket-lead-file-missing`, `qa-engineer-file-missing`, `independent-reviewer-file-present`, `a-tenth-file-without-the-lines`) | the roles folder as it stands has faults, so no planted departure can be told from them (the control fails first) |

**How F2 works.** Each case runs twice. First on a planted control (`build_synthetic`: nine files that satisfy the line
rules and nothing else): the checker must pass it, then fail the plant with every failure naming the planted file
(and the failure naming the key or sentence). Then on a copy of the repository's roles folder: it must pass unplanted
(the control, red until the work is done) and then fail the plant the same way. "Fails the role test" means the line
rules and the roster of files (`role_faults`); the content statements of S1, S3, S6, S8, S9 have their own cases.

## Judged elsewhere (the role-file statement stays here)

* "The launcher's plan prints the file's model and effort" (S2): W2-60a.
* The guard's refusal of a planted QA write elsewhere (S3), the launcher's refusal of two writers in one worktree (S5):
  W2-60b.
* The planted review brief with one out-of-scope finding (S6): the reviewer's probe (`docs/probes/DAEO-lrre/`), not a
  deterministic case.
* The generated agents carrying the same lines (S7), "a role file edited by hand in the generated folder" (F2): W2-153's
  generation check, after the copies ACT.
* Fields of ROLES-SPEC-1 §5.2 that the Interface does not name (`Launch`, `Ticket`, `Network`, `Guard class`, `Writes`,
  `Tools`, `Brief template`, `Return`) are **not** required here: the Interface is the owner-approved form (DEC-1156 (3)).
* Non-goals, no test: `docs/changes/W2-33-CIT-P.md`, the handoff schema and template (Wave 3), `.claude/agents/**` and the
  other `.rulesync` copies, the launcher, the guard.

## Readings (where the ticket is silent)

1. **S1 / S8 heads.** The ticket gives no line heads for reads, writes, handover or the Senior Engineer's brief
   contents. Accepted heads (a `- **<head>:**` item at column 0, case-insensitive): reads `Reads` / `Reads and writes` /
   `Allowed paths`; writes `Writes` / `Reads and writes` / `Allowed paths`; handover `Handover` / `Handoff` /
   `Handoff format` / `Return` / `Returns`; brief contents `Brief` / `Brief contents` / `Its brief` / `Brief must contain`
   (not `Brief template`, which ROLES-SPEC-1 §5.2 uses for a file name). Each must carry at least five words (eight for
   the brief); the Senior Engineer's brief must mention its stream and its handover must name the CTO (ROLES-SPEC-1 §3.2).
2. **S2, skills exist.** Each skill a role file names must have a `SKILL.md` under `template/governance/kernel/skills/<name>/`,
   or `.../skills/superpowers/<name>/` (the three vendored skills) or `template/.rulesync/skills/<name>/` (the generated
   folder the launcher reads from `.claude/skills/`): the launcher refuses a skill with no SKILL.md. **Names ROLES-SPEC-1
   proposes but no folder has today** (`ticket-loop`, `stream-orchestration`, W2-11's new skills) fail this case: name
   only existing skills, or the case is the place to learn that W2-11 has not landed.
3. **S7, QA engineer's Launch default.** The ticket states QA's by-criticality values but not its default. The case
   requires a well-formed `Launch default` line and does not assert its value (the lead's suggestion, Sonnet high, the
   C1 value, is not required). **C0.** S7 gives no C0 value (RUBRIC-2-APPLY.md:23: "Haiku or deterministic"); the case
   requires the `C0` entry to be present and of the form `C0 model <id>, effort <e>` and asserts no value.
4. **S7, "absent".** For orchestrator, ticket-lead, senior-engineer, independent-auditor, product-spec and research a
   `Launch by criticality` line is a failure (the Interface: "only where RUBRIC-2 varies").
5. **S7, D-10.** A role file fails when one of its statements joins `D-10` to a model, Opus, Sonnet or a launch (the
   through-D-10 rule is the CTO's launch practice, in no role file). A bare mention of D-10 (a path map) passes.
6. **One line.** The work order and one-writer sentences must be one physical line (the KPI says "in one line"; the
   launcher's reader needs one line for its own forms).
7. **S4, denial of reads.** The `Allowed paths` item of each of the two files must hold one statement with "read", "work",
   a word for the other side (`counterpart` / `engineer` / `implement...` for the designer; `counterpart` / `test
   designer` / `acceptance tests` / `tests` for the engineer) and a denial word (`denied`, `refuse...`, `never`, `may
   not`, `must not`, `no reads`).
8. **S3, QA's statements.** Three statements, each by the KPI's words: it reads the spec, the KPIs, the tests and the
   code; it changes none of them; it writes only its findings report (all in the file; the first two may be one
   sentence). `Per stream` must carry: core, one by one, before they merge, the guard, the close, retrieval, fail open,
   batch, "up to about five" (or 5).
9. **S9, the statements.** each within three consecutive statements: (a) install, only, coordination ticket (or `coordination_ticket`),
   orchestrator or CTO, and ask; (b) install, refuse and "every/any/all other"; (c) install, `coordination_ticket`
   and `GOV_TICKET`. **F1's pattern** matches "the guard asks / prompts ... every /
   each / all (up to two words) install" and "every install ... is asked / prompted", across wrapped lines; it does not
   match "every other session is refused".
10. **README in the folder.** Not a role file (see above). A tenth `*.md` is checked like the nine.

## Run

```
TMPDIR=<outside the repository> bash .../heavy_slot.sh env HOME=<empty scratch> PYTHONPATH=<tree>/src python3 -m pytest \
  tests/acceptance/W2-33 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" \
  -k "not real and not green_here and not time_limit"
```

Nothing is left out by the exclusion: no case is marked `local_only` and none is named `real`, `green_here` or `time_limit`.
