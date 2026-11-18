# W2-195 acceptance tests: the judging-work skill preloaded, briefed, checked and shipped

Ticket `DAEO-d8df` (W2-195), profile FULL, class C3 (the kernel). Written by the independent test designer (MR-3) on
the base `06cd7f869` from the ticket's four success lines and its failure line, DEC-1204, `P-GOLDEN-RULE-1.md`
sections 2 to 4, the approved skill (`judging-work.SKILL.md`, sha256 `0fc1c502…`; re-pinned to the CTO's trim at `ef82e15fa`, EMERGENCY-2 §3.4/§3.6, A-13) and the lead's interface statement
(DEC-1157), with the integrated code the brief and launch work with (`src/gov/brief/`, `src/gov/launch/role.py`,
`src/gov/adopt/fabric.py`, `src/gov/adapters/` as they stand on the base). Nothing of this ticket's implementation was
read.

KPI cells use positions in the ticket: `success-N` is the n-th success line (S1 to S4), `failure-1` the failure line F1.

## How they run

    env HOME=<empty folder> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=<worktree>/src \
      python3 -m pytest tests/acceptance/W2-195 -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
      -m "not local_only" -k "not real and not green_here and not time_limit"

About 5 s on the base (45 cases). No model, no network, no store, no `gov retrieve`. No case is named `real`,
`green_here` or `time_limit` and none is marked: the exclusion leaves nothing out. Every case is of the acceptance
kind and under its 5 s limit on the base (the slowest: the kit case 1.3 s, the wheel case 0.9 s, each building from
HEAD; with the skill shipped they do a little more, the copier copy and `gov adapters generate` took about 2 s in the
designer's probe). The wheel and kit cases carry no marker, as W2-88's own wheel case carries none. The kit case
needs `copier` and `rulesync` on the PATH or in the user base's `bin` (`PYTHONUSERBASE`); without either it is
skipped, as W2-88's is.

## What the cases do

- **The skill's text is this folder's own copy:** `data/judging-work.kernel.SKILL.md`, the approved text as trimmed
  at `ef82e15fa` (its `description` value in double quotes): sha256
  `34ae6c218ab35191e3e5ac3e3443a0118b86017a91d94b8adb5919ce76f3a4d5`, 4135 bytes, version 1.1.0. Sections 1 to 3 are
  the bytes from the start of the line `## 1. The threat model` up to, not including, the line `## 4. Doing it` (sha256
  `9844057d…`). The brief, launch and F1 fixtures plant this copy, so their reds are about `gov brief` and
  `read_role`, never a missing kernel file; one S4 case checks the kernel file and its mirror equal it.
- **The preloaded copy** (`.claude/skills/judging-work/SKILL.md`) is planted in the form `gov adapters generate`
  writes (rulesync's): front matter `name`, `description` and `metadata.version` only (no top-level `version`), the
  blank line after it dropped, the body otherwise the kernel's. The designer observed this form by running copier and
  `gov adapters generate` on a kit holding the skill, and on this tree's own generated skills; a check that reads only
  a top-level `version` would fail on the real copy, and fails here too.
- **`gov brief`:** a fixture project under `tmp_path` holds this tree's kernel templates (copied at test time), this
  tree's facts file with `ready.new_since` set, one READY ticket (`DAEO-jw01`, W2-951), the kernel skill file
  (`template/governance/kernel/skills/judging-work/SKILL.md`, or `governance/kernel/...` with the templates under
  `governance/kernel/templates/` in the adopted layout) and the preloaded copy. `python3 -B -m gov.cli.main brief
  <role> DAEO-jw01 [--run review] --root <tmp> --json` runs as a child, with this tree's `src` first, an empty `HOME`,
  dead proxies. A judging brief: `independent-auditor`, `qa-engineer`, `lead --run review`.
- **`read_role`:** a root holding `template/governance/kernel/roles/<role>.md` (this tree's file; for S3 its
  `- **Skills:**` line set by the case), the kernel skill file, and under `.claude/skills/` a copy of each skill the
  line names (the kernel's folder for the others, the preloaded form for `judging-work`); `read_role_child.py` calls
  `gov.launch.role.read_role(root, role)` in a child and prints its `skills` or its `GovError` code.
- **The wheel:** `git archive HEAD` of `src/` and `git show HEAD:pyproject.toml` into tmp, `pip wheel -q --no-deps
  --no-build-isolation --no-index`, the wheel opened as a zip. **The kit:** `copier.yml` and `template/` of HEAD in a
  clone with a planted tag, `copier copy --trust --defaults --skip-tasks`, then `gov adapters generate --json`. Both
  read HEAD only: uncommitted work is not in them.

## The map

| KPI | Test | Expected red reason on the base |
|---|---|---|
| success-1 | `test_w2_195_s1_preload.py::test_s1_the_kernel_role_files_skills_line_names_judging_work` (4: independent-auditor, qa-engineer, orchestrator, ticket-lead) | `roles/<role>.md's Skills line names [...], not judging-work` |
| success-1 | `test_w2_195_s1_preload.py::test_s1_the_reviewer_templates_skills_list_holds_judging_work` | `role-reviewer.md's skills list is ['audit'], without judging-work` |
| success-1 | `test_w2_195_s1_preload.py::test_s1_the_rulesync_subagent_mirror_preloads_judging_work` (4: the same roles) | `the rulesync mirror <role>.md preloads [...], without judging-work` |
| success-1, success-3 | `test_w2_195_s1_preload.py::test_s1_s3_read_role_of_a_judging_role_carries_judging_work_named_with_its_version` (2: independent-auditor, qa-engineer) | `judging-work is loadable but not named by roles/<role>.md's Skills line, so the launch does not preload it` |
| success-2 | `test_w2_195_s2_brief.py::test_s2_a_judging_brief_holds_sections_1_to_3_byte_for_byte_and_names_the_version` (3: independent-auditor, qa-engineer, lead-review) | auditor and lead: `the <role> brief does not hold sections 1 to 3 of the installed judging-work skill, byte for byte`; qa-engineer: `gov brief did not succeed: exit 2` (argparse: invalid choice 'qa-engineer') |
| success-2 | `test_w2_195_s2_brief.py::test_s2_in_an_adopted_tree_the_auditor_brief_reads_governance_kernel` | `the auditor brief in an adopted tree does not hold sections 1 to 3` |
| success-2 | `test_w2_195_s2_brief.py::test_s2_a_non_judging_brief_holds_neither_the_sections_nor_the_version_line` (2: engineer, independent-test-designer) | `the contrast: the auditor brief on this fixture does not hold the sections, so nothing is shown` |
| success-3 | `test_w2_195_s3_check.py::test_s3_a_judging_brief_without_the_skill_or_with_another_version_is_refused_by_name` (9: three judging briefs, each with the kernel file removed, the preloaded copy removed, the preloaded copy at version 1.1.1) | auditor and lead: `gov brief did not refuse (exit 0): it printed a brief`; qa-engineer: `--json printed no JSON envelope (the refusal is not gov's): exit 2` (argparse) |
| success-3 | `test_w2_195_s3_check.py::test_s3_an_auditor_brief_whose_kernel_file_has_no_sections_1_to_3_is_refused_by_name` | `gov brief did not refuse (exit 0): it printed a brief` |
| success-3 | `test_w2_195_s3_check.py::test_s3_without_json_the_refusal_prints_no_brief_and_names_its_code` | `gov brief did not refuse: exit 0` |
| success-3 | `test_w2_195_s3_check.py::test_s3_a_judging_launch_without_the_skill_or_with_another_version_is_refused_by_name` (6: independent-auditor and qa-engineer, each with the Skills line lacking judging-work, the preloaded copy removed, the preloaded copy at 1.1.1) | line lacking and other version: `read_role(<role>) (...) was not refused: the launch would start without the rule`; copy removed: `is refused LAUNCH_REFUSED, not LAUNCH_JUDGING_RULE_MISSING` |
| success-4 | `test_w2_195_s4_shipped.py::test_s4_the_kernel_skill_and_its_mirror_are_the_approved_bytes` (2: kernel, rulesync-mirror) | `<rel> does not exist: the skill is not in the kernel` |
| success-4 | `test_w2_195_s4_shipped.py::test_s4_fabric_packaged_and_kernel_folders_name_the_skill_once` | `fabric.PACKAGED names template/governance/kernel/skills/judging-work 0 times` |
| success-4 | `test_w2_195_s4_shipped.py::test_s4_a_wheel_built_from_head_carries_the_skill_bytes` | `the wheel of HEAD does not carry gov/_shipped/template/governance/kernel/skills/judging-work/SKILL.md` |
| success-4 | `test_w2_195_s4_shipped.py::test_s4_the_kit_delivers_the_skill_and_adapters_generate_preloads_it` | `copier copy of the kit installed no governance/kernel/skills/judging-work/SKILL.md` |
| failure-1 | `test_w2_195_f1_text.py::test_f1_the_sections_a_brief_carries_hash_as_the_installed_files_sections` (6: three judging briefs, each with the approved 1.1.0 text and with a 1.1.1 copy whose section 2 has one word changed) | auditor and lead: `the brief carries no section 1 heading of judging-work`; qa-engineer: `gov brief did not succeed: exit 2` (argparse) |

**Red run on the base** (`heavy_slot.sh`, the sandbox's TMPDIR, an empty HOME, 2026-11-16): `tests/acceptance/W2-195`
**45 cases, 45 failed, each for the reason in the table, 0 passed, 0 skipped**; none is red by an import, a fixture
error or a missing data file. With `tests/acceptance/W2-88/test_w2_88_p1_shipped_bytes.py` beside it: 46 failed, 12
passed (W2-88's own items and its "only the copies" case, green as before).

**The pass half of success-3** ("the same roles with the skill pass") is shown by the S2 brief cases (each judging
brief on the fixture with the skill succeeds) and by `test_s1_s3_read_role_...` (this tree's role file with the skill
named, read_role not refused). A launch root whose Skills line names the skill already passes `read_role` on the base,
so no separate S3 "pass" case is written for the launch: it would be green on the base and show nothing new.

## W2-88's shipped list (success-4, outside this folder)

`tests/acceptance/W2-88/test_w2_88_p1_shipped_bytes.py`: `ITEMS` gains `"the-judging-work-skill":
"template/governance/kernel/skills/judging-work"`, its assertions otherwise unchanged. Red on the base:
`test_w2_88_p1_shipped_bytes.py::test_s24_each_shipped_copy_equals_its_source_byte_for_byte[the-judging-work-skill]`
(`the source template/governance/kernel/skills/judging-work is not in this checkout`). Its "only the copies" case
stays green (the new item lets the copy through once it exists). Both cases are mapped by node id in W2-88's README
(its success-24 rows), not in the table above: `gov accept W2-195` collects this folder only.

## Not covered, and why

- **`gov launch --plan` listing the skill** (S1's verify): `--plan` prints one line from `launcher.py` (DEC-1167
  (2)), W2-156's file, outside this ticket's paths (the lead's interface item 5). S1's launch half is shown through
  `read_role`'s `skills`, the list the launcher writes into the launch record. Taken to the CTO by the lead.
- **The generated copy's whole bytes.** The interface's item 7 asks `.claude/skills/judging-work/SKILL.md`, after
  `gov adapters generate`, to be the kernel bytes. rulesync rewrites a skill's front matter (the description folded,
  the top-level `version` dropped, only `metadata.version` kept) and drops the blank line after it: this tree's own
  `.claude/skills/{audit,retrieval,qa-review,test-design}/SKILL.md` differ from their kernel files the same way. No
  engineer can make the generated copy the kernel bytes, so the kit case asserts what holds: the copy exists, is named
  `judging-work`, carries version 1.1.0, its body (after the front matter, leading blank lines dropped) is the
  kernel's, and so it holds sections 1 to 3 byte for byte. The kernel file and the rulesync mirror the kit installs are
  asserted byte for byte.
