# W2-120 acceptance tests: the skill validator refuses a skill whose front matter carries a permission field

Ticket DAEO-i89t (W2-120), profile STANDARD, run 2 (run 1 stopped at the interface check; the owner decided the
interface, DEC-1156 (2)). Written by the independent test designer (MR-3) from the ticket's KPI line `success-1` and its
`## Interface` section I1 to I4, before any implementation, reading the ticket, the decisions it names, the validator
and the three skill-regression check files as they stand at the base, and the live skill folders. The engineer's work
on `src/gov/check/skill_validator.py` was not read.

The lifted lines (the "no output class" half, the brief-template twelve-field rule, the reserved command list, the old F1)
are **not** tested. In particular **a skill with no `output` key is not refused by this ticket** (the ticket's
"Deferred" line): KPI `success-1`'s "planted skills: one with no output class" is therefore tested as *a skill with no
`output`, otherwise clean, gives no refusing finding and exit 0* (`test_deferred_a_skill_with_no_output_key_is_not_refused`).

## How they run

    PYTHONPATH=<worktree>/src python3 -m pytest tests/acceptance/W2-120 -q -p no:cacheprovider \
      -o tmp_path_retention_policy=failed

About 2 s, 32 cases. No model, network or store. Every case plants a small project in `tmp_path` (never the live
tree) and runs the validator **as a process with that project as the working folder**, with the `src` of the repository
this folder lies in on `PYTHONPATH`; so merged into the ticket's worktree the cases judge that worktree's code.
`w2_120_support.py` holds the planting and the running; `conftest.py` puts this folder on the import path.

## How "gov check refuses" is judged (I1, I3)

`gov check` runs the `command:` of a check file from the project's root (`python3 -m gov.check.skill_validator
--both-layouts template/governance/kernel/skills/<skill> ...`, `src/gov/check/runner.py`, `cwd` the root). The cases run
exactly that form: the support module reads the `command:` of `skill-regression-a.yaml` from the repository, asserts it
still starts `python3 -m gov.check.skill_validator --both-layouts`, and swaps only the folder list for the planted
skill's folder (run by this interpreter with `-P`, as `gov check` runs it). One case
(`test_i3_gov_check_runs_the_check_file_and_refuses_the_planted_key`) runs `gov check --json` itself on a planted project
holding one skill-regression check file, and reads the check's entry: red, a finding naming the generated file and the key.

- **Refusal** = exit 1 and a finding of four fields (`code`, `file`, `key`, `message`, I1) whose `file` is the planted
  file and whose `key` is the planted key, and whose `code` is not `SKILL_VENDORED_KEY` (a named-only finding is not a
  refusal, I4). **Pass** = exit 0 and `{"findings": []}`.
- A finding's `file` is judged as a path: resolved against the project and compared with the planted file's resolved
  path, never a text search of a temporary path (DEC-1155). The cases name no particular `code` for a refusal and
  no wording of a `message`.
- The cases pin no particular form of a path (absolute or relative to the project) in `file`.

## Readings of what the interface leaves open

1. **I2's `.claude/skills/` list.** "For the generated copies under `.claude/skills/` the list is name, description and
   metadata (rulesync drops the other top-level keys)." So a `.claude` copy with exactly those keys is clean (the live
   ones carry no `version` or `output`, so the validator reads them without its kernel rule that `version` is
   required), and one that also carries `version` or `output` is refused, naming the `.claude` file and that key
   (`test_i2_a_generated_claude_copy_*`). `metadata`'s own sub-keys are not pinned (the live openspec copies carry
   `metadata.author`).
2. **The two `.rulesync` folders' list** is not stated in I2 beyond "on every copy read". The cases plant them as the
   live tree holds them (name, version, description, metadata; no `output`, which is deferred) and refuse them only for
   `allowed-tools`, `model`, `effort` or `targets` (vendored), keys outside any plausible list.
3. **I4's root.** The openspec-* skills lie only in the generated folders (`.claude/skills/openspec-*`,
   `.rulesync/skills/openspec-*`) and `superpowers/*` only in the kernel, and the check files name kernel skill folders
   (never `superpowers/*` or openspec-*). So I4 is judged **where the kernel skills root is given**
   (`--both-layouts template/governance/kernel/skills`): the validator then reads the kernel skills below it, and the
   generated folders as I3 says. A single-skill folder is not pinned for I4, and whether a single-skill run also reads
   unrelated skills in the generated folders is not pinned either (I3 does not state it).
4. **A vendored skill** is a skill in the kernel under `superpowers/`, or named `openspec-*` in any folder. The vendored
   cases plant otherwise clean skills (a vendored `.rulesync` copy holds `version`, a `.claude` copy does not), so how a
   vendored skill's other fields are handled is not pinned; the cases only need the named key and the exit.
5. **"Clean skill"** (I2) is a skill with exactly name, version, description, output and `metadata.version`; the
   planted project carries the skill clean in the kernel folder and in the three generated folders (as the live
   tree does), so a validator that also read the generated copies passes it.
6. **I1's "each finding with code, file, key and message"** is read for every finding, a key finding or not
   (`test_i1_every_finding_carries_code_file_key_and_message`): the four names are present; the value of `key` for a
   finding about no key (a missing description) is not pinned.
7. **The installed twin.** `--both-layouts` maps `template/<path>` to `<path>` when its folder exists (today's
   behaviour); I2 says the key rule holds "on every copy read", so a skill planted at `governance/kernel/skills/<x>`
   with a refused key is refused naming that file (`test_i3_the_installed_twin_*`).

## KPI map

| KPI line | Tests (node ids) | Red reason on the base `32d10098b6a1` (today's validator) |
|---|---|---|
| success-1 | `test_w2_120_i2_keys.py::test_i2_a_kernel_skill_with_a_listed_permission_key_is_refused_naming_file_and_key` (7 cases: allowed-tools, permissions, paths, sandbox, network, model, effort)<br>`test_w2_120_i2_keys.py::test_i2_a_kernel_skill_with_any_other_key_is_refused_naming_file_and_key` (license, colour)<br>`test_w2_120_i2_keys.py::test_i2_two_refused_keys_in_one_skill_are_each_named`<br>`test_w2_120_i2_keys.py::test_i1_every_finding_carries_code_file_key_and_message`<br>`test_w2_120_i2_keys.py::test_i2_a_generated_claude_copy_with_a_kernel_only_key_is_refused` (version, output)<br>`test_w2_120_i3_copies.py::test_i3_a_refused_key_in_a_generated_copy_is_read_and_names_the_generated_file` (.rulesync, template/.rulesync, .claude)<br>`test_w2_120_i3_copies.py::test_i3_kernel_and_a_generated_copy_both_carrying_the_key_are_both_named` (3 folders)<br>`test_w2_120_i3_copies.py::test_i3_every_copy_carrying_a_key_is_named_once_each`<br>`test_w2_120_i3_copies.py::test_i3_the_installed_twin_of_the_kernel_folder_is_read_too`<br>`test_w2_120_i3_copies.py::test_i3_gov_check_runs_the_check_file_and_refuses_the_planted_key`<br>`test_w2_120_i4_vendored.py::test_i4_a_vendored_kernel_superpowers_skill_with_allowed_tools_is_named_and_the_exit_stays_0`<br>`test_w2_120_i4_vendored.py::test_i4_a_vendored_claude_openspec_skill_with_allowed_tools_and_license_is_named_and_the_exit_stays_0`<br>`test_w2_120_i4_vendored.py::test_i4_a_vendored_rulesync_openspec_skill_with_targets_is_named_and_the_exit_stays_0` (2 folders)<br>`test_w2_120_i4_vendored.py::test_i4_a_vendored_named_finding_beside_a_refused_non_vendored_key_gives_exit_1_and_both_findings`<br>`test_w2_120_i4_vendored.py::test_i4_a_non_vendored_skill_with_allowed_tools_is_refused_not_merely_named` | **28 cases red.** Today's validator has no key check (a planted `allowed-tools`, `model`, `targets` ... gives exit 0 and `{"findings": []}`), its findings have no `file` and no `key`, it reads one place per path (no `.rulesync`, `template/.rulesync` or `.claude` copy), and it has no `SKILL_VENDORED_KEY`. Each fails on "exit 0, no finding names the file and key" (the `gov check` case: the entry is green, `findings` empty), none on a collection, import or fixture error |
| success-1 | `test_w2_120_i2_keys.py::test_i2_a_clean_kernel_skill_passes_with_no_findings`<br>`test_w2_120_i2_keys.py::test_deferred_a_skill_with_no_output_key_is_not_refused`<br>`test_w2_120_i2_keys.py::test_i2_a_generated_claude_copy_of_name_description_and_metadata_passes`<br>`test_w2_120_i3_copies.py::test_i3_the_three_check_files_still_run_the_validator_over_kernel_skill_folders` | **4 cases green on the base, kept as guards** (each still needed): "a clean skill passes" (KPI), the deferred half (a skill with no `output` is not refused), a clean generated `.claude` copy (name, description, metadata) passes once copies are read, and the three check files keep their `--both-layouts` form over kernel skill folders (I3: no edit to them) |

## Checking the checks (scratch, never committed)

`w2_120_support.py` has a switch: `W2_120_VALIDATOR_MODULE` (default `gov.check.skill_validator`) names the module run as
`python3 -m <module>`, and `W2_120_STANDIN_DIR` is a folder put first on `PYTHONPATH`. Unset, the real validator runs
(the `gov check` case skips under the switch: the check file names the real validator). The designer ran the suite
against a stand-in written to I1 to I4: 31 passed, 1 skipped; and against the stand-in with one rule omitted each time
(no generated copies; no installed twin; vendored refusing; every skill vendored; the `.claude` list as the kernel's;
`sandbox` or `effort` allowed; one finding per key; no key check; no file or key in findings; `.claude` copies held to
the required `version`): each variant failed the cases meant for it and no others (the return lists them).

## Limits

- The cases pin no `code` of a refusal other than "not `SKILL_VENDORED_KEY`", no message wording, no order of findings.
- A project with no generated folders at all is not pinned here (the existing W1-26 layout suite plants such projects).
- The path of the branch's own changes (allowed_paths) is not judged here (not required).

## Files

- `w2_120_support.py`: the paths, the planting, the check run as a process, the file-and-key reading.
- `conftest.py`: puts this folder on the import path.
- `test_w2_120_i2_keys.py` (I1, I2 and the deferred half), `test_w2_120_i3_copies.py` (I3, the check files, `gov check`),
  `test_w2_120_i4_vendored.py` (I4).
