# W1-48 — Claude Code version pin: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-0qs5` (W1-48), CAP-25 / CAP-25.d
and CAP-61 / CAP-61.e of Contract v4, DEC-083, DEC-141, DEC-153, DEC-157, DEC-196, DEC-197, DEC-199 to DEC-207,
DEC-209 to DEC-211, DEC-214, the "Installs" rule of `docs/plan/WAVE_1_WBS.md` and the "Interim install rule" of
`governance/project/bootstrap.md`.

Three batches:

- **Batch 1** (commit `532ab854`, 66 cases), written before implementation. It raised the packages DP-1 and DP-2.
- **Batch 2** (commit `57827aee`, 170 cases), written **after** implementation (registry commit `66498e9c`), from the
  owner's answers DEC-210 (DP-1) and DEC-211 (DP-2) and the rewording DEC-209. Every existing case it changed or
  removed is a rewrite after implementation; they are listed under "Rewrites of batch 2". It raised the package DP-3.
- **Batch 3** (this one, 172 cases), also written **after** implementation, from the owner's answer DEC-214 (DP-3)
  and the reworded second success line of the ticket. Its rewrites are listed under "Rewrites of batch 3". No other
  ticket's test was rewritten in any batch.

The approach is that of `tests/acceptance/W1-06/`. Its helpers are repeated in `w1_48_support.py`, so that this suite
runs on its own and W1-06's files stay untouched.

## Run

```sh
python3 -m pytest tests/acceptance/W1-48 -q -p no:cacheprovider
```

`pytest`, the standard library and PyYAML (the project's declared dependency, used only to parse the registry). No
network. **No test installs, downloads, updates or uninstalls anything, runs an install command, or starts a Claude
Code session.** The tests read the committed registry, its schema, the decision register and the contract, and ask git
whether the registry is committed.

Eight cases are marked `local_only`. They fail, not skip, when the tool is absent, because on this machine it must be
there. Deselect them elsewhere with `-m "not local_only"` (164 cases remain).

- 2 (the CLI): they look at the file `~/.local/bin/claude` (DEC-205) and run it with `--version`. `claude` is never
  looked up through `PATH`.
- 3 (the active VS Code extension, DEC-210): they read `~/.vscode-server/extensions/extensions.json`, the
  `package.json` of the folder its `anthropic.claude-code` row points at, and run that folder's bundled binary with
  `--version`.
- 1 (the machine against the record, DEC-210, DEC-214): it does both of the above, and hashes the two binaries.
- 2 (bubblewrap, socat): they run `bwrap --version` and `socat -V`.

A tool asked for its version is run with `PATH=/usr/bin:/bin` and a 30 s limit.

## State today

Run on `w1/integrate` at `ac4d0fa8`, the implementation committed: **172 cases (66 test functions): 172 passed, 0
failed.** No case is red, and none is expected to be red. `tests/acceptance/W1-06`, unchanged: 96 passed.

Batch 1's red run, before implementation, at `30660355`: 66 cases, 40 failed, 26 passed; all 40 failed because none
of the three entries was in the registry.

## KPI → tests → state today

| KPI line | Test file | Test functions | State today |
|---|---|---|---|
| **Success 1.** Claude Code is recorded, pinned at 2.1.285 or later, with install and uninstall commands, date and approving decision; the upgrade is installed by the owner, or by the orchestrator under DEC-083, and in both cases recorded with its owner approval (DEC-157, DEC-203, DEC-209) **[CAP-25.d]** | `test_w1_48_claude_code.py`, `test_w1_48_registry.py`, `test_w1_48_cli_path.py` | `test_claude_code_is_recorded_in_the_registry` · `test_claude_code_is_pinned_to_one_exact_version` · `test_the_claude_code_pin_is_2_1_285_or_later` · `test_the_recorded_install_command_installs_the_pinned_version` · `test_the_recorded_uninstall_command_removes_claude_code` · `test_claude_code_carries_a_sha256_digest` · `test_claude_code_carries_a_calendar_date` · `test_claude_code_was_approved_by_an_owner_decision_of_the_register` · `test_the_approval_names_claude_code_and_the_pinned_version` · `test_the_approval_is_made_under_dec_083` · `test_the_approval_is_claude_codes_own` · `test_claude_code_is_not_dated_before_its_approval` · `test_an_entry_of_this_ticket_states_every_fact_the_schema_requires[claude code]` · `test_the_registry_as_read_is_the_committed_one` · **new, DEC-209:** `test_an_install_recorded_with_its_owner_approval_is_accepted_whoever_installed[2]` · `test_an_install_without_a_recorded_owner_approval_is_refused_whoever_installed[6]` · `test_an_install_that_cites_no_register_entry_is_refused_whoever_installed[2]` · **new, DEC-211:** the cases of `test_w1_48_cli_path.py` (below) | Green |
| **Success 2** (reworded, DEC-214). The CLI used for headless runs and the active VS Code extension's bundled version are both at or above the minimum, 2.1.285, and the registry record states both; a difference between them, or from the registry's record, is drift that gov doctor reports, not a failure, except that the CLI at the recorded version with another sha256 is a failure (DEC-210, DEC-214) **[CAP-61.e]** | `test_w1_48_cli.py`, `test_w1_48_drift.py` | `test_the_record_is_about_the_cli_at_local_bin_claude` (DEC-205) · `test_the_record_states_the_vs_code_extensions_bundled_version` (revised) · `test_the_record_states_no_extension_version_below_the_minimum` (revised) · `test_the_cli_at_local_bin_claude_is_installed` (`local_only`) · `test_the_cli_for_headless_runs_is_2_1_285_or_later` (`local_only`) · **new:** `test_vs_code_has_a_claude_code_extension_active_that_bundles_a_cli` (`local_only`) · `test_the_active_vs_code_extension_is_2_1_285_or_later_by_its_package_json` (`local_only`) · `test_the_active_vs_code_extension_bundles_a_cli_at_2_1_285_or_later` (`local_only`) · `test_this_machine_compared_with_the_record_shows_no_hard_failure` (`local_only`, revised in batch 3) · the 57 cases of `test_w1_48_drift.py` (fixed sample values). **By clause of the line:** "both at or above the minimum" — the two CLI and three extension `local_only` cases, the machine case, `test_a_cli_or_an_active_extension_below_the_minimum_is_a_hard_failure[11]`; "the registry record states both" — the three `test_the_record_…` cases; "a difference … is drift … not a failure" — `test_a_cli_and_an_active_extension_at_or_above_the_minimum_are_no_hard_failure[13]`, `test_a_difference_at_or_above_the_minimum_is_reported_as_drift[13]`, `test_the_extensions_binary_at_the_recorded_version_with_another_digest_is_drift` (new, batch 3); "except that the CLI at the recorded version with another sha256 is a failure" — `test_the_cli_at_the_recorded_version_with_another_digest_is_a_hard_failure`, `test_both_binaries_at_the_recorded_version_with_another_digest_are_one_failure_and_one_drift`, `test_the_clis_digest_fails_whatever_the_extension_is` (new, batch 3), and the machine case | Green: the CLI, the active extension's `package.json` and its bundled binary are all 2.1.288, and both binaries have the recorded sha256 |
| **Success 3.** bubblewrap 0.9.0 and socat 1.8.0.0 are recorded as owner installs, with version, install and uninstall commands, date and approving decision (DEC-141) | `test_w1_48_sandbox_prereqs.py`, `test_w1_48_registry.py` | `test_a_sandbox_prerequisite_is_recorded_at_the_version_the_owner_installed[2]` · `test_a_sandbox_prerequisite_cites_dec_141[2]` · `test_dec_141_is_an_owner_decision_that_names_the_prerequisite_and_its_version[2]` · `test_the_install_command_of_a_sandbox_prerequisite_is_the_owners[2]` · `test_the_uninstall_command_of_a_sandbox_prerequisite_is_the_owners[2]` · `test_a_sandbox_prerequisite_carries_a_sha256_digest[2]` · `test_a_sandbox_prerequisite_carries_a_calendar_date[2]` · `test_the_sandbox_prerequisite_on_this_machine_is_the_recorded_version[2]` (`local_only`) · `test_an_entry_of_this_ticket_states_every_fact_the_schema_requires[bubblewrap, socat]` | Green (unchanged in batch 2) |
| **Failure 1.** A headless run uses a CLI below 2.1.285 | `test_w1_48_cli.py`, `test_w1_48_claude_code.py`, `test_w1_48_drift.py` | `test_the_cli_for_headless_runs_is_2_1_285_or_later` (`local_only`) · `test_this_machine_compared_with_the_record_shows_no_hard_failure` (`local_only`) · `test_the_claude_code_pin_is_2_1_285_or_later` · `test_a_cli_or_an_active_extension_below_the_minimum_is_a_hard_failure[11]` · `test_a_version_below_the_minimum_fails_even_when_the_registry_records_it` · `test_the_failure_names_what_is_below_the_minimum` | Green |
| **Failure 2.** bubblewrap or socat is missing from the registry while gov launch depends on it | `test_w1_48_sandbox_prereqs.py` | `test_a_sandbox_prerequisite_is_recorded_in_the_registry[2]` · `test_the_registry_records_the_prerequisites_the_contract_names_for_the_sandbox` | Green (unchanged in batch 2) |
| **Failure 3.** The pin is raised without a recorded owner approval | `test_w1_48_claude_code.py` | `test_the_pin_as_recorded_has_a_recorded_owner_approval` · `test_a_raised_pin_is_not_covered_by_the_approval_of_the_recorded_one` · the five approval cases of success 1 · the ten DEC-209 sample cases | Green |
| **DEC-205** (owner). The pinned CLI is the one at `~/.local/bin/claude` | `test_w1_48_cli.py`, `test_w1_48_cli_path.py` | `test_the_record_is_about_the_cli_at_local_bin_claude` · `test_the_cli_at_local_bin_claude_is_installed` (`local_only`) · the DEC-211 cases · the digest comparison of DEC-214 (below) | Green |
| **DEC-207** (owner). Every Node 22 install command carries the PATH prefix | `test_w1_48_node22_prefix.py` | `test_every_node_22_command_of_the_registry_carries_the_path_prefix` · `test_the_check_sees_the_node_22_commands_the_registry_has[2]` · `test_the_check_refuses_a_node_22_command_without_the_prefix[8]` · `test_the_check_accepts_a_node_22_command_with_the_prefix[5]` · `test_the_check_leaves_other_commands_alone[5]` | Green (21 cases, unchanged in batch 2) |
| **DEC-209** (owner). The upgrade is installed by the owner, or by the orchestrator under DEC-083, in both cases recorded with its owner approval | `test_w1_48_claude_code.py` | the approval cases of success 1 (the registry's entry) · the ten sample cases named there (both installers) | Green |
| **DEC-210** (owner, DP-1). The active extension; below the minimum fails, drift does not | `test_w1_48_cli.py`, `test_w1_48_drift.py` | the four `local_only` cases marked new under success 2 · `test_a_cli_or_an_active_extension_below_the_minimum_is_a_hard_failure[11]` · `test_a_version_below_the_minimum_fails_even_when_the_registry_records_it` · `test_the_failure_names_what_is_below_the_minimum` · `test_a_cli_and_an_active_extension_at_or_above_the_minimum_are_no_hard_failure[13]` · `test_a_difference_at_or_above_the_minimum_is_reported_as_drift[13]` · `test_a_record_written_with_a_leading_v_is_the_same_version` · `test_a_failure_and_drift_are_told_apart_in_one_look` · `test_a_newer_binary_with_another_digest_is_drift_by_its_version_alone` · `test_the_recorded_digest_is_compared_without_case` · `test_the_active_extension_is_the_row_of_extensions_json` · `test_the_extension_id_is_compared_without_case` · `test_an_index_without_a_claude_code_row_gives_no_active_extension[6]` · `test_the_folder_of_a_row_is_its_location` · `test_the_folder_of_a_row_without_a_location_is_its_relative_location_under_the_extensions_folder` | Green |
| **DEC-211** (owner, DP-2). Registry commands carry the CLI's absolute path; a bare `claude` is refused | `test_w1_48_cli_path.py` | `test_no_registry_command_runs_a_bare_claude` · `test_the_claude_code_install_command_runs_no_bare_claude` · `test_the_check_refuses_a_claude_that_is_not_run_by_its_absolute_path[19]` · `test_the_check_accepts_the_cli_run_by_its_absolute_path[8]` · `test_the_check_leaves_a_command_alone_that_runs_no_claude[9]` | Green: the registry's install command is `$HOME/.local/bin/claude install 2.1.288`, and its uninstall command runs `ln` and `rm` |
| **DEC-214** (owner, DP-3). The recorded version with another sha256: a hard failure for the CLI at `~/.local/bin/claude`, drift for the active extension's bundled binary | `test_w1_48_drift.py`, `test_w1_48_cli.py` | `test_the_cli_at_the_recorded_version_with_another_digest_is_a_hard_failure` · `test_the_extensions_binary_at_the_recorded_version_with_another_digest_is_drift` · `test_both_binaries_at_the_recorded_version_with_another_digest_are_one_failure_and_one_drift` · `test_the_clis_digest_fails_whatever_the_extension_is` · `test_this_machine_compared_with_the_record_shows_no_hard_failure` (`local_only`) · unchanged beside them: `test_a_newer_binary_with_another_digest_is_drift_by_its_version_alone` · `test_the_recorded_digest_is_compared_without_case` | Green: `~/.local/bin/claude` is 2.1.288 with the recorded sha256 `0298068b…640c`, and so is the active extension's bundled binary |

**Count.** KPI lines with tests: 6 of 6 (3 success, 3 failure). Covers ids with tests: 2 of 2 (CAP-25.d, CAP-61.e).
Owner decisions with tests: 6 of 6 (DEC-205, DEC-207, DEC-209, DEC-210, DEC-211, DEC-214). Packages: DP-1, DP-2 and
DP-3 answered; none open.

**Cases per file.** `test_w1_48_claude_code.py` 24 · `test_w1_48_cli.py` 9 · `test_w1_48_cli_path.py` 38 ·
`test_w1_48_drift.py` 57 · `test_w1_48_node22_prefix.py` 21 · `test_w1_48_registry.py` 4 ·
`test_w1_48_sandbox_prereqs.py` 19.

## Batch 3: new and revised cases, and their state

From the owner's answer DEC-214 on DP-3. Every case below is **green today**; none is red. The four sample cases are
green because `compare_with_record` now puts the CLI's digest difference on the failure side and the extension's on
the drift side. The machine case is green because `~/.local/bin/claude` prints 2.1.288, the recorded version, and
has the recorded sha256; the active extension's bundled binary has it too, so there is no drift either.

The machine case was also given, in memory, this machine's readings against a changed record: with another recorded
sha256 it reports one failure (the CLI) and one drift (the extension), so the case would be red; with only the
extension's digest changed it reports no failure and one drift, so the case would stay green. Nothing was written.

### Rewrites of batch 3 (existing cases changed or removed after implementation): 3

| # | Case | What changed | Reason |
|---|---|---|---|
| 1 | `test_the_recorded_version_with_another_digest_is_noticed[cli_sha]` | **Replaced** by `test_the_cli_at_the_recorded_version_with_another_digest_is_a_hard_failure`. Was: the difference is noticed, neither failure nor drift asserted. Now: exactly one hard failure, which names the CLI and both digests, and no drift. | Owner decision, DEC-214. |
| 2 | `test_the_recorded_version_with_another_digest_is_noticed[extension_sha]` | **Replaced** by `test_the_extensions_binary_at_the_recorded_version_with_another_digest_is_drift`. Was: as 1. Now: no failure, and exactly one drift, which names the bundled binary and both digests. | Owner decision, DEC-214. |
| 3 | `test_this_machine_compared_with_the_record_shows_no_hard_failure` (`local_only`) | **Behaviour changed, name kept.** Was: fails only below the minimum; a digest difference at the recorded version did not fail. Now: it also fails when the CLI at `~/.local/bin/claude` prints the recorded version and has another sha256 than the registry's. The assertion line is the same (`verdict.failures == ()`); the rule behind it, the docstring and the failure message changed. The extension's digest difference still does not fail it. | Owner decision, DEC-214. |

Also changed, not cases: `w1_48_support.compare_with_record` and the comments of `Verdict` (a digest difference is
now also put in `failures` for the CLI and in `drift` for the extension; `digests` still lists both), the module
docstrings of `w1_48_support.py`, `test_w1_48_cli.py` (it quotes the reworded KPI line and DEC-214) and
`test_w1_48_drift.py`, and two section comments. No other case's text or result changed.

### Added in batch 3: 2 cases (2 test functions), beside the 2 replacements

| File | Case | For |
|---|---|---|
| `test_w1_48_drift.py` | `test_both_binaries_at_the_recorded_version_with_another_digest_are_one_failure_and_one_drift` | DEC-214: the same difference on both binaries at once goes to its own side for each |
| `test_w1_48_drift.py` | `test_the_clis_digest_fails_whatever_the_extension_is` | DEC-214 with DEC-210: a newer extension is drift and does not turn the CLI's digest failure into drift |

170 − 2 replaced + 2 replacements + 2 added = 172.

## Batch 2: new and revised cases, and their state

*As written at batch 2 (170 cases); `test_the_recorded_version_with_another_digest_is_noticed[2]`, counted below, is
replaced in batch 3.*

Every case below is **green today**. None is red, because the registry as implemented already meets the owner's
answers: its install command carries `$HOME/.local/bin/claude` (DEC-211), and the CLI and the active extension are
both 2.1.288, above the minimum (DEC-210).

Each case that reads the registry was also run once, in memory, against a changed copy of it, to see it turn red:
a bare `claude install 2.1.288` (both DEC-211 registry cases red), the extension named with 2.1.284 (red), the
extension named with 2.1.290 (green: drift), no clause naming the extension (red). Nothing was written.

### Rewrites of batch 2 (existing cases changed or removed after implementation): 6

| # | Case | What changed | Reason |
|---|---|---|---|
| 1 | `test_the_cli_for_headless_runs_is_the_pinned_version` (`local_only`) | **Removed.** It asserted that the CLI's version equals the pin, so a newer CLI failed. | Owner decision, DEC-210: a CLI newer than the record is drift, not a failure. "At or above the minimum" stays tested by `test_the_cli_for_headless_runs_is_2_1_285_or_later`. |
| 2 | `test_the_pinned_binary_is_the_one_at_local_bin_claude` (`local_only`) | **Removed.** It asserted that the registry's sha256 equals the digest of `~/.local/bin/claude`, so a newer CLI failed. The comparison is now made in `test_this_machine_compared_with_the_record_shows_no_hard_failure`, where it does not fail. | Owner decision, DEC-210: the sha256 is "compared", and only below the minimum is a hard failure. What the comparison means at the recorded version is DP-3. |
| 3 | `test_a_vs_code_extension_at_the_pinned_version_bundles_the_pinned_cli` (`local_only`) | **Removed.** It asserted that an extension folder at the pin is on disk and bundles a CLI at the pin. Replaced by the three cases on the active extension. | Owner decision, DEC-210: the extension is the one VS Code has active, and it is tested against the minimum, not the pin. |
| 4 | `test_the_record_states_the_vs_code_extensions_bundled_version` | **Assertion changed.** Was: a clause holds "extension" and the pinned version. Now: a clause holds "extension" and a version. | Owner decision, DEC-210: "not equal to the pin"; the owner re-records drift when convenient, so the record may state another version for the extension. |
| 5 | `test_the_record_states_no_other_version_for_the_extension` | **Renamed and changed** to `test_the_record_states_no_extension_version_below_the_minimum`. Was: an extension clause names no version but the pin. Now: it names no version below 2.1.285. | Owner decision, DEC-210, as for 4. |
| 6 | `test_the_approval_is_made_under_dec_083` | **Docstring only.** It quoted the old KPI wording ("through a DEC-083 decision package"). The assertion is unchanged. | Owner decision, DEC-209 (KPI line reworded). |

Also changed, not cases: the module docstrings of `test_w1_48_claude_code.py` and `test_w1_48_cli.py` (they quote the
KPI line and DEC-210), a section comment, and `w1_48_support.py` (the helper `extension_folders` of the removed case 3
is replaced by the DEC-210 and DEC-211 helpers).

### Added in batch 2: 107 cases (27 test functions)

| File | Cases | For |
|---|---|---|
| `test_w1_48_cli.py` | 4, all `local_only` | DEC-210 on this machine |
| `test_w1_48_drift.py` | 55 | DEC-210 on fixed sample values: 14 on the failure side, 31 on the drift side, 10 on reading `extensions.json` |
| `test_w1_48_cli_path.py` | 38 | DEC-211: 2 on the registry, 36 on fixed sample commands |
| `test_w1_48_claude_code.py` | 10 | DEC-209 on fixed sample register entries, for both installers |

66 − 3 removed + 107 added = 170.

## Readings the sources do not spell out

Readings 1 to 7 and 14 to 22 are those of batch 1. Readings 4, 6 and 8 to 13 are changed by the owner's answers of
batch 2; 23 to 26 were new in batch 2. Batch 3 (DEC-214) changes readings 11 and 26 and adds 27.

1. **Entry names** are compared without case. Accepted: `claude code` / `claude-code` / `claude`; `bubblewrap` /
   `bwrap`; `socat`. **Note for the implementer:** W1-06's
   `test_every_entry_outside_the_stack_cites_a_decision_that_names_the_tool` looks for the entry's name, as written,
   in the cited decision. DEC-203 holds "Claude Code" and `claude`, not `claude-code`, so the name `claude-code` would
   pass here and fail there. `claude code` and `claude` pass both.
2. **One entry per tool, one exact version.** `version` is digits and dots (an optional leading `v` and suffix are
   allowed by the form test, but the comparison with 2.1.285 needs digits and dots only).
3. **"2.1.285 or later"** is a comparison of the dotted numbers as integers: 2.1.285, 2.1.288, 2.1.1000, 2.10.0 and
   2.2.0 pass; 2.1.284 fails. The pin's version is not fixed to 2.1.288 in any test, so a later raise needs no new
   test.
4. **"With install and uninstall commands"** for Claude Code: `install` names `claude` and the pinned version;
   `uninstall` is not blank, is not the install command, and names `claude`. What the uninstall command must be
   (remove the binary, or go back to an earlier version) is not tested. A `claude` that a command runs is written
   with the CLI's absolute path (DEC-211, reading 23).
5. **"Date"** is a string that starts with a real `YYYY-MM-DD` date. For Claude Code it is not before the date of the
   approving decision (DEC-083: installs only after approval). For bubblewrap and socat no order is tested: DEC-141 is
   the record of an owner action already made.
6. **"Installed by the owner, or by the orchestrator under DEC-083, and in both cases recorded with its owner
   approval" (DEC-209).** The registry does not say who ran the command, and no test asks. What is tested is the same
   in both cases: the cited decision is an entry of the register whose status starts `ACCEPTED (owner` and holds
   `DEC-083`, whose own text names "Claude Code" and exactly the registry's version, and which no other registry entry
   cites (DEC-197: "its own register entry"). `DEC-083` is asked of an owner install too: DEC-197, which requires the
   register entry, stands under DEC-083, and DEC-203 (an owner install) carries it. In the register as it stands only
   DEC-203 fits Claude Code 2.1.288. No test names DEC-203. On fixed sample entries, an owner install and an
   orchestrator install with an owner-accepted entry both pass, and both are refused when the cited entry is only
   proposed, is accepted by the orchestrator, has no status line, or is not in the register.
7. **A decision's own text** is its heading and its lines up to the next `## ` heading or table row, as in W1-06
   (its reading 16): without that cut the last entry of a section would hold the section's change-log row.
8. **"The pin is raised without a recorded owner approval" (failure 3)** is tested in two ways. (i) The entry as it
   stands meets every condition of reading 6 at once. (ii) The same entry with its version one patch higher is
   refused, because the cited decision does not name that version: raising the *registry's* version needs a new
   register entry. **Changed by DEC-210:** batch 1's third way, "a CLI newer than the record is a raise that nobody
   recorded", is withdrawn. A newer CLI or extension on the machine is drift that `gov doctor` reports; the owner
   re-records when convenient, and the re-record is then held to (i) and (ii).
9. **"The CLI used for headless runs"** is the file `~/.local/bin/claude` (DEC-205: every headless worker is started
   with that absolute path). Its version is what `~/.local/bin/claude --version` prints first (`2.1.288 (Claude
   Code)`). No test resolves `claude` through `PATH`. **Not tested:** that a given headless run was in fact started
   with that path. Until W1-46's launcher exists the command is typed by the orchestrator, and no committed file this
   ticket may change holds it.
10. **"A headless run uses a CLI below 2.1.285" (failure 1)** is tested as: the file of reading 9 is 2.1.285 or later
    (read from the machine alone), and the registry's pin is 2.1.285 or later. **Changed by DEC-210:** the two are no
    longer required to be equal. The minimum is 2.1.285 itself, not the registry's record: a machine at 2.1.284 fails
    even against a record of 2.1.284.
11. **The registry's sha256 for Claude Code** is the sha256 of a single-file binary (DEC-196; DEC-203 records the
    value). **Changed by DEC-210:** it is *compared* with the digest of the file `~/.local/bin/claude` resolves to and
    with the digest of the active extension's bundled binary. Where the version differs from the record, the digest
    differs by itself and counts as that drift. **Changed by DEC-214:** where the version equals the record and the
    digest differs, it is a hard failure for the CLI at `~/.local/bin/claude` and drift for the extension's bundled
    binary (reading 27).
12. **"The registry record states both."** `version` is the CLI's version. The record is about `~/.local/bin/claude`
    when some fact of the entry (the note, a command, or another key) holds `~/.local/bin/claude`,
    `$HOME/.local/bin/claude`, `${HOME}/.local/bin/claude` or `/home/<user>/.local/bin/claude`. The extension's
    version is stated when one clause of the entry, outside `version`, `install` and `uninstall`, holds the word
    "extension" and a three-part version. A clause ends at `. `, `; `, `: ` or a line end; a key and its value form one
    statement (`<key>: <value>`), so a key such as `extension_version` counts too (the schema allows extra keys).
    **Changed by DEC-210:** the version in that clause need not be the pin; every version in a clause that holds
    "extension" is 2.1.285 or later. So a record that states the CLI at 2.1.288 and the extension at 2.1.290 passes.
    See "Wording that lags the answers" below.
13. **The VS Code extension on this machine (DEC-210)** is each row of
    `~/.vscode-server/extensions/extensions.json` whose `identifier.id` is `anthropic.claude-code` (compared without
    case). Its folder is the row's `location.path`, else its `relativeLocation` under the extensions folder. Folders
    that are only on disk (2.1.283 to 2.1.286 today) and the file `.obsolete` are not read. Its bundled version is
    read twice: the `version` of the folder's `package.json`, and what `resources/native-binary/claude --version`
    prints. Each of the two must be 2.1.285 or later; so if they disagree, the lower one decides. If VS Code had more
    than one such row, each is held to the minimum. **A reading:** when the file, the row, the folder, the
    `package.json` or the bundled binary is absent, or a version cannot be read, the `local_only` cases fail: the
    extension cannot be shown to be at or above the minimum. On a machine without VS Code they are deselected with
    the other `local_only` cases.
14. **"Recorded as owner installs"** for bubblewrap and socat: `install` is a `sudo apt-get install` (or `sudo apt
    install`) that names the package, `uninstall` is a `sudo apt-get remove`, `purge` or `autoremove` that names it,
    and `approved_by` is exactly `DEC-141`. A `sudo` command is an owner action (no agent session runs sudo), as
    PyYAML's entry has it (DEC-201). The entry is not required to hold the word "owner", and a version in the install
    command (`bubblewrap=0.9.0-…`) is allowed, not required.
15. **The versions of the two prerequisites are fixed**: `0.9.0` and `1.8.0.0`, as the KPI and DEC-141 give them, not
    the distribution's package version (`0.9.0-1ubuntu0.3`).
16. **Their sha256** is tested by form only (64 hexadecimal characters). DEC-196 makes it the digest of the
    distribution package, which is not on this machine; recomputing it would need a download.
17. **"While gov launch depends on it" (failure 2).** `gov launch` is W1-46 and does not exist yet. The dependency is
    read from the contract: CAP-61 names its provider "Claude Code sandbox (bubblewrap 0.9.0, socat 1.8.0.0)". The
    tests require both entries without condition, and require every tool and version in that provider line to be a
    registry entry at that version.
18. **On this machine** `bwrap --version` and the first two lines of `socat -V` must hold the recorded version. Both
    are found through `PATH`; DEC-205's rule is about `claude` only. DEC-210's "dynamic, not exact" is about Claude
    Code only; these two cases stay exact.
19. **"Every Node 22 install command" (DEC-207)** is every `install` and `uninstall` command of the registry (DEC-202:
    "The ccusage commands carry the prefix") that runs a Node package manager (`npm`, `npx`, `pnpm`, `yarn` or
    `corepack`, by its bare name or any path) or any program from `.nvm/versions/node/v22.23.3/bin/`. The registry has
    one Node for tools (ADR-0002 §2), so every package-manager command is a Node 22 command. Installing Node itself
    (`nvm install 22.23.3`) is not one. Today: the openspec and ccusage commands, four in all.
20. **"Carries the prefix"**: the word `PATH=<home>/.nvm/versions/node/v22.23.3/bin:$PATH` stands in the command
    before its first package manager or Node 22 program. `<home>` is `$HOME` (the registry's spelling), `~` (DEC-202's)
    or `${HOME}`; `${PATH}` and double quotes round the value are accepted. An absolute home path is not.
21. **"Recorded" means committed**: git tracks the registry and the working-tree file equals `HEAD`'s.
22. **CAP-25.d, "worker roles never install system-wide"** is the guard's install rule (W1-04, W1-47), not this ticket;
    no test here covers it. This ticket's part of CAP-25.d is the entry, its floor and the approval of a raise.
23. **"Registry commands" (DEC-211)** are the `install` and `uninstall` commands of *every* entry of the registry,
    not only Claude Code's. The owner chose option (a) of DP-2, which named the Claude Code entry; the decision's text
    says "registry commands", and no other entry runs `claude` today, so the two are the same now.
24. **"A bare `claude`" (DEC-211)** is a *command word*: the program a simple command runs. A command line is cut at
    `&&`, `||`, `;`, `|`, `&`, a line end, `(`, `)`, a backquote and the quoted text after a `-c` flag (`bash -c
    '…'`); in each piece, variable assignments (`PATH=…`), the wrapper words `sudo`, `env`, `exec`, `command`, `nohup`,
    `time`, `xargs` and their flags are passed over, and the next word is the command word. A command word whose last
    path part is `claude`, `claude.exe` or `claude.cmd` must be the CLI's absolute path, spelled
    `$HOME/.local/bin/claude` (the decision's spelling), `${HOME}/…`, `~/…` (DEC-205's) or `/home/<user>/…`, with or
    without quotes. So a bare `claude` is refused, and so is any other path to a `claude` (the Windows-side copy,
    `/usr/local/bin/claude`, `./claude`): the decision says the commands "carry the absolute path". `claude` as an
    argument (`rm -f ~/.local/bin/claude`, `ln … $HOME/.local/bin/claude`), in a package name
    (`@anthropic-ai/claude-code`) or in another path (`~/.local/share/claude/versions/…`) is left alone. **Limits:** a
    wrapper's flag that takes a value (`sudo -u name claude`) and a runner such as `npx claude` are not understood.
25. **A command is not required to run the CLI.** DEC-211 is tested as a refusal only. An install command that runs
    no `claude` at all (an install script fetched with `curl`, say) passes this check; the first install on a machine
    with no `~/.local/bin/claude` needs such a command.
26. **Failure or drift (DEC-210, DEC-214)**, as `w1_48_support.compare_with_record` decides it and
    `test_w1_48_drift.py` tests it on fixed values. Three versions are looked at: the CLI's, the active extension's
    `package.json`, and its bundled binary's. **A hard failure:** one of the three is below 2.1.285, or gives no
    version that can be compared with it (nothing printed, or text that is not digits and dots); or (DEC-214) the CLI
    prints the recorded version and has another sha256 than the registry's. **Drift, not a failure:** one of the
    three differs from the registry's version, newer *or older* (down to 2.1.285); the CLI differs from either
    reading of the extension; the extension's two readings differ; or (DEC-214) the extension's bundled binary prints
    the recorded version and has another sha256 than the registry's. Equal versions with the recorded digest are
    neither. The tests assert that the failure side fails, that the drift side does not, and that drift is named, so
    that W1-27's `gov doctor` has a rule to report from. No test fails or warns on drift.
27. **"The recorded version with a different sha256" (DEC-214).** "The recorded version" is the registry's `version`
    compared as numbers (a leading `v` dropped), against what the binary prints with `--version`: for the CLI,
    `~/.local/bin/claude --version`; for the extension, its bundled binary's `--version`, not its `package.json`
    (the digest is the binary's, so the binary's own version decides). The digest is that of the file the path
    resolves to (links followed), compared with the registry's `sha256` without case. A binary at **any other**
    version is not held to the digest: for the CLI too, that is drift by its version alone (DEC-210), so the CLI's
    digest failure can arise only while the CLI prints exactly the recorded version. An automatic update therefore
    cannot trip it: it changes the version as well. On the machine both digests are always taken; in the rule, a
    digest that is not given (`None`) is not compared, which only fixed sample values can produce.

## Wording that lags the answers (for the orchestrator, no test depends on it)

- **KPI success 2** — settled. The ticket line was reworded under DEC-214 (commit `d93a9e2c`) and now reads as
  DEC-210 and DEC-214 are tested; the KPI map quotes the new wording.
- **CAP-61.e** says the CLI "is aligned with" the extension's bundled version. Under DEC-210 a difference between
  the two is reported, not failed, so within this ticket "aligned" has no failing test; it becomes W1-27's report.
- **W1-27 (`gov doctor`)** is where DEC-210 puts the drift report. Its ticket now carries that as a KPI line
  (DEC-214, commit `9a24311e`); the drift side of readings 26 and 27 is what this suite expects it to report,
  the extension's digest difference included.

## Decision packages

### DP-1 — Which extension folder is "the VS Code extension", and what its "bundled version" is (ANSWERED: DEC-210)

The owner chose option (a) with (iii), with a change: the extension is the one VS Code has active, read from its
`extensions.json`; its bundled version is read from both its `package.json` and its bundled binary's `--version`, and
the binary's sha256 is compared with the registry; the check is dynamic, not exact. It is a hard failure only if the
CLI or the active extension is below the minimum, 2.1.285. A difference between the CLI and the extension, or either
being newer than the record, is drift that `gov doctor` reports. Tested by readings 10 to 13 and 26. The package's
text is in batch 1's README (commit `532ab854`).

### DP-2 — May the recorded install command start with a bare `claude` (ANSWERED: DEC-211)

The owner chose option (a): registry commands carry the absolute path (`$HOME/.local/bin/claude`), and a test refuses
a bare `claude`. Tested by readings 23 to 25. The package's text is in batch 1's README (commit `532ab854`).

### DP-3 — The recorded version with another digest: a failure, or drift (ANSWERED: DEC-214)

The owner chose option (c): for the CLI at `~/.local/bin/claude`, the recorded version with a different sha256 is a
hard failure; for the active extension's bundled binary it is drift, reported by `gov doctor`. Everything else of
DEC-210 stands. Tested by readings 11, 26 and 27 and the cases of the DEC-214 row of the KPI map. The package as it
was put, kept for the record:

- **Question.** DEC-210 says the bundled binary's sha256 "is compared with the registry", and that it is a hard
  failure "only if the CLI or the active extension is below the minimum". When a binary has a *different version*
  from the record, its digest differs by itself, and that is drift. But when the CLI at `~/.local/bin/claude`, or the
  active extension's bundled binary, prints *exactly the recorded version* and has *another sha256* than the
  registry's: is that a hard failure, or drift?
- **Why now.** Batch 1's `test_the_pinned_binary_is_the_one_at_local_bin_claude` failed on any digest difference; it
  was DEC-205's "check that the pinned CLI is the one at `~/.local/bin/claude`" in its strongest form. DEC-210 removes
  it for a newer CLI, and its word "only" reads as removing it altogether; DEC-196 and DEC-205 read the other way.
  The suite now makes the comparison and fails on nothing, which is the letter of DEC-210 and is not a choice of this
  batch that should stand unasked.
- **Options.**
  - (a) Drift for both binaries. The digest is reported by `gov doctor` (DEC-196 already gives it the hash re-check
    for single-file binaries) and no test fails on it.
  - (b) A hard failure for both: the recorded version with other bytes is not the recorded binary.
  - (c) A hard failure for the CLI at `~/.local/bin/claude` only (the binary headless workers run, DEC-205); drift for
    the extension's bundled binary.
- **Impact.** (a) keeps the suite free of machine-state failures above the minimum, as DEC-210 intends; a replaced or
  damaged binary at the recorded version is then caught only when W1-27 exists. (b) and (c) keep a test that tells
  "the same number" from "the same bytes"; an automatic update cannot trip it, because an update changes the version
  too. (b) assumes the extension always bundles the same build as the standalone CLI of that version; that holds
  today (both are `0298068b…640c`) and nothing in the sources guarantees it. (c) does not need that assumption.
- **Reversibility.** High. `compare_with_record` already keeps these differences in a list of their own (`digests`);
  the answer moves that list to the failure side or the drift side, for one binary or both.
- **Cost.** (a) one line: the two "noticed" sample cases assert drift. (b), (c) about five lines, and the two sample
  cases assert a failure for the binaries the answer names. No change to the registry under any option.
- **Recommendation.** (c).
- **Confidence.** Medium-low. (a) is the plainest reading of DEC-210's "only"; (c) is recommended because it keeps
  the check DEC-205 asked for at no cost in false alarms.
- **Until answered** (batch 2's state, now replaced). `test_the_recorded_version_with_another_digest_is_noticed[2]`
  asserted only that the difference is noticed, and
  `test_this_machine_compared_with_the_record_shows_no_hard_failure` did not fail on it, which was option (a) in
  effect. Batch 3 replaces both with option (c).
