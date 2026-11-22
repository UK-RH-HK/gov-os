# W2-22 acceptance tests: `gov doctor` and a patch-only Claude Code CLI/extension gap

Ticket `DAEO-xm6l` (W2-22, `gov doctor green`). **A fix, not a new ticket** (EMERGENCY-2 section 2): the owner's
DEC-1227 D6 (a). Context: `docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md`, rows P1 and A1. Written by the
independent test designer from the two fix lines below, before the implementation. The ticket's own status and KPIs
are history and are not changed; the lines of this fix are the two here, read by `gov accept` as `success-1` and
`success-2`.

- **A1 (success-1).** In `gov doctor`'s `claude_code` section a difference of the PATCH number only (same major and same
  minor) between the CLI and the VS Code extension is drift: reported, exit 0. With no registry entry for Claude Code
  (`pinned_version` null), a stand-in CLI 2.1.329 and extension 2.1.328: `gov doctor --json` exits 0 (`ok` true,
  `healthy` true), the section still says `status: drift`, `drift: true`, and an `issues` entry of type `drift` names
  both versions. The plain output (no `--json`, which prints the result as indented JSON on standard output when
  doctor is healthy) names both versions on one line and says drift. Both directions and a wide patch gap
  (2.1.329 against 2.1.300); equal versions are no drift (control).
- **A2 (success-2).** A larger gap still fails: exit 3, error code `DOCTOR_UNHEALTHY`, `claude_code` named. The minor
  differs (either way), the major differs (either way); a CLI below the minimum 2.1.285; a CLI whose sha256 differs
  from the registry's record at the CLI's own version. A patch-only gap beside another failure or drift in the same
  section (CLI sha256, extension below the minimum, both binaries newer than the registry's record) still exits 3.
- A3 is documentation only and is not tested.

## Run

    T=$(mktemp -d); TMPDIR=$T PYTHONPATH=<this worktree>/src bash <heavy_slot.sh> \
        python3 -m pytest tests/acceptance/W2-22 -q -p no:cacheprovider -n auto; chmod -R u+w $T; rm -rf $T

or `gov accept W2-22`. Every case builds a small committed git repository under `tmp_path`, a stand-in `claude` (a
shell script echoing a version) first on the `PATH` `gov` runs with, and a stand-in extension (`extensions.json`,
`package.json`, `resources/native-binary/claude`) under the case's own `HOME/.vscode-server/extensions`; it runs this
worktree's code through W1-07's launcher (DEC-732). The machine's own CLI, extension and home are never read or
touched; no network. The support file reuses W1-27's and W1-07's helpers (`w2_22_support.py`).

## Map

| KPI | Tests | Today (base), and why |
|---|---|---|
| success-1 (A1) | `test_w2_22_claude_code_drift.py::test_a_patch_only_gap_is_named_drift_and_doctor_exits_0[2.1.329-2.1.328]`, `[2.1.328-2.1.329]`, `[2.1.329-2.1.300]` | **red**: exit 3, `DOCTOR_UNHEALTHY` (a drift is counted as unhealthy), where exit 0 and `healthy` true are expected; the section itself (`drift` true, the drift issue naming both versions) is already as expected |
| success-1 (A1) | `test_w2_22_claude_code_drift.py::test_a_patch_only_gap_is_named_in_the_plain_output_too` | **red**: exit 3 and nothing on standard output (the plain error goes to standard error without the versions) |
| success-1 (A1), control | `test_w2_22_claude_code_drift.py::test_equal_versions_are_no_drift_and_doctor_exits_0` | green today (a guard: equal versions stay no drift and exit 0) |
| success-2 (A2) | `test_w2_22_claude_code_drift.py::test_a_gap_beyond_the_patch_number_fails_doctor[2.2.0-2.1.329]`, `[2.1.329-2.2.0]`, `[2.1.329-2.2.5]`, `[3.0.0-2.1.329]`, `[2.1.329-3.0.0]` | green today (guards against over-fixing: any gap is unhealthy today; they go red if the fix exempts more than the patch number) |
| success-2 (A2) | `test_w2_22_claude_code_drift.py::test_a_cli_below_the_minimum_fails_doctor[extension-also-below]`, `[extension-above]` | green today (guards) |
| success-2 (A2) | `test_w2_22_claude_code_drift.py::test_a_cli_with_another_sha256_than_the_record_fails_doctor` | green today (guard) |
| success-2 (A2) | `test_w2_22_claude_code_drift.py::test_a_patch_only_gap_does_not_mask_a_cli_sha256_failure`, `test_a_patch_only_gap_does_not_mask_an_extension_below_the_minimum`, `test_a_patch_only_gap_does_not_mask_drift_from_the_record` | green today (guards: a patch-only exemption that masks a real failure or the record's drift turns them red) |

Red run on the base (4 red, 12 green, the green ones being the guards above):
`4 failed, 12 passed`.

## Fix F2: `gov doctor` checks a tool installed in its own folder (audit 3, M-04; DEC-1232, DEC-1233)

Also a fix under this ticket (lead `fixes-015b`; the ticket's status and KPIs are not changed). Lines `success-3` to
`success-7` are this fix's, in `test_w2_22_tool_in_own_folder.py` (helpers `w2_22_tools_support.py`); `success-1` and
`success-2` above stay as they are.

- **success-3.** A second Node, registry name `node-22.23.5` pinned `v22.23.5`, installed under
  `<HOME>/.nvm/versions/node/v22.23.5/bin/node` (stand-in printing `v22.23.5`): `gov doctor --json`'s `tools` part
  reports it `ok` true, `found_version` v22.23.5.
- **success-4.** `rea-agents` pinned `6.10.1`, installed as `<folder>/node_modules/.bin/rea` where `<folder>` is the
  `cd <folder> && ...` of its install line (stand-in printing `6.10.1`): `ok` true, `found_version` 6.10.1.
- **success-5.** A tool at another version still fails (`ok` false); a tool whose binary is nowhere still fails.
- **success-6.** Never cross-answer: with `node` (v22.23.3, no prefix of its own) and `node-22.23.5` in one registry,
  the v22.23.5 prefix in rea-agents' install line before node's own place (and, in some cases, the v22.23.3 prefix in
  openspec's), a stand-in `node` printing v18.20.8 first on the `PATH`: both installed, both ok; only v22.23.5
  installed, `node` not ok and not read as v22.23.5, `node-22.23.5` ok; only v22.23.3 installed, `node-22.23.5` not ok
  and not read as v22.23.3, `node` ok.
- **success-7.** DEC-452 stays: `openspec` with no prefix of its own, a decoy `openspec` (another version) on the `PATH`,
  the right one under the prefix `ccusage`'s install line carries: found under it, ok.

No registry key is added or removed; every case builds its own HOME, repository, registry and stand-ins (shell scripts)
under `tmp_path`; no network. Two spellings of the places are run: `real` (`~` and `$HOME` in the install lines, as the
real registry has them) and `abs` (the sandbox home written out). The `real` cases need `~` and `$HOME` read from the
`HOME` the process runs with, not from the account's home (`_extract_path_prefix` reads the account's today).

| KPI | Tests | Today (base), and why |
|---|---|---|
| success-3 | `test_w2_22_tool_in_own_folder.py::test_a_second_node_in_its_own_nvm_folder_is_found_and_read` (the `real` and `abs` spellings) | **red**: `node-22.23.5` found nowhere (`ok` false, `found_version` null): doctor looks for a binary named `node-22.23.5` |
| success-4 | `test_w2_22_tool_in_own_folder.py::test_rea_agents_in_its_folders_node_modules_bin_is_found_and_read` (the `real` and `abs` spellings) | **red**: `rea-agents` found nowhere: doctor looks only under the `PATH=` prefix (the node folder) and the `PATH` |
| success-5 | `test_w2_22_tool_in_own_folder.py::test_a_second_node_at_another_version_still_fails`, `test_rea_agents_at_another_version_still_fails`, `test_tools_whose_binary_is_absent_still_fail` | green today (guards: a fix that passes a wrong version or an absent tool turns them red) |
| success-6 | `test_w2_22_tool_in_own_folder.py::test_each_node_is_judged_against_its_own_pin_only` (cases both-installed, only-22.23.5 and only-22.23.3, each in five registry layouts) | **red** in every layout but two: `node-22.23.5` is never found, and in the only-22.23.5 case the v22.23.5 binary answers for `node` (`found_version` v22.23.5, found through rea-agents' prefix) and in the only-22.23.3 case `node` is not found (the v22.23.3 place is no prefix of any install line); **green** (guards) for the only-22.23.3 case in the two layouts where openspec's install line carries the v22.23.3 prefix |
| success-7 | `test_w2_22_tool_in_own_folder.py::test_a_tool_without_a_prefix_is_still_found_under_another_entrys_prefix` | green today (guard for DEC-452) |

Red run on the base (17 red, 13 green): `17 failed, 13 passed`.

### Open points (F2)

- The `real` spelling can only pass when `~`, `$HOME` and the nvm place are read from the process's `HOME`.
- Where a stand-in prints a version doctor can read, a wrong binary is already refused by the version comparison; the
  cross-answer the cases catch is the one that decides which binary `node` is judged on (`found_version`).

## Open points (for the owner or the lead, not guessed)

- **Drift from the registry's record beside a patch-only gap.** `test_a_patch_only_gap_does_not_mask_drift_from_the_record`
  reads D6 (a) as exempting only the CLI-against-extension gap, so a CLI (and extension) newer than the registry's
  record still ends doctor with exit 3 (W1-27's `test_cli_newer_than_registry_is_drift` keeps its `drift` section).
  If the owner meant every drift in the section to stop counting, this one case changes.
- "Named in the plain output" is read as: one line of the output holds both versions, and the word drift appears.
