# W1-48 — Claude Code version pin: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-0qs5` (W1-48), CAP-25 / CAP-25.d
and CAP-61 / CAP-61.e of Contract v4, DEC-083, DEC-141, DEC-153, DEC-157, DEC-196, DEC-197, DEC-199 to DEC-207, the
"Installs" rule of `docs/plan/WAVE_1_WBS.md` and the "Interim install rule" of `governance/project/bootstrap.md`.
Written before implementation. No earlier ticket's test was rewritten.

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

Seven cases are marked `local_only`. They fail, not skip, when the tool is absent, because on this machine it must be
there. Deselect them elsewhere with `-m "not local_only"`.

- 4 (the CLI): they look at the file `~/.local/bin/claude` (DEC-205), run it with `--version` and hash the binary it
  resolves to. `claude` is never looked up through `PATH`.
- 1 (the VS Code extension): it reads the `package.json` of the Claude Code extension folders under
  `~/.vscode-server/extensions/` and runs one folder's bundled binary with `--version`.
- 2 (bubblewrap, socat): they run `bwrap --version` and `socat -V`.

A tool asked for its version is run with `PATH=/usr/bin:/bin` and a 30 s limit.

## KPI → tests → red reason today

Red run on `w1/integrate` at `30660355`: **66 cases (39 test functions): 40 failed, 26 passed.**

All 40 fail because none of the three is in the registry yet:

- 39 with **`governance/project/tool-registry.yaml has no entry named …`** (`claude code / claude-code / claude`: 21
  cases; `bubblewrap / bwrap` and `socat`: 18 cases);
- 1 (`test_the_registry_records_the_prerequisites_the_contract_names_for_the_sandbox`) with **`the sandbox depends on
  tools the registry does not record as the contract names them: ['bubblewrap 0.9.0: not in the registry', 'socat
  1.8.0.0: not in the registry']`**.

| KPI line | Test file | Test functions | Red reason today |
|---|---|---|---|
| **Success 1.** Claude Code is recorded, pinned at 2.1.285 or later, with install and uninstall commands, date and approving decision; installed through a DEC-083 decision package (DEC-157) **[CAP-25.d]** | `test_w1_48_claude_code.py`, `test_w1_48_registry.py` | `test_claude_code_is_recorded_in_the_registry` · `test_claude_code_is_pinned_to_one_exact_version` · `test_the_claude_code_pin_is_2_1_285_or_later` · `test_the_recorded_install_command_installs_the_pinned_version` · `test_the_recorded_uninstall_command_removes_claude_code` · `test_claude_code_carries_a_sha256_digest` · `test_claude_code_carries_a_calendar_date` · `test_claude_code_was_approved_by_an_owner_decision_of_the_register` · `test_the_approval_names_claude_code_and_the_pinned_version` · `test_the_approval_is_made_under_dec_083` · `test_the_approval_is_claude_codes_own` · `test_claude_code_is_not_dated_before_its_approval` · `test_an_entry_of_this_ticket_states_every_fact_the_schema_requires[claude code]` · `test_the_registry_as_read_is_the_committed_one` (green today) | No Claude Code entry |
| **Success 2.** The CLI used for headless runs and the VS Code extension's bundled version are the same version, at or above the pin, and the registry record states both **[CAP-61.e]** | `test_w1_48_cli.py` | `test_the_record_is_about_the_cli_at_local_bin_claude` (DEC-205) · `test_the_record_states_the_vs_code_extensions_bundled_version` · `test_the_record_states_no_other_version_for_the_extension` · `test_the_cli_at_local_bin_claude_is_installed` (`local_only`, green today) · `test_the_cli_for_headless_runs_is_the_pinned_version` (`local_only`) · `test_the_pinned_binary_is_the_one_at_local_bin_claude` (`local_only`, DEC-205, DEC-196) · `test_a_vs_code_extension_at_the_pinned_version_bundles_the_pinned_cli` (`local_only`; as far as DP-1 leaves it clear) | No Claude Code entry |
| **Success 3.** bubblewrap 0.9.0 and socat 1.8.0.0 are recorded as owner installs, with version, install and uninstall commands, date and approving decision (DEC-141) | `test_w1_48_sandbox_prereqs.py`, `test_w1_48_registry.py` | `test_a_sandbox_prerequisite_is_recorded_at_the_version_the_owner_installed[2]` · `test_a_sandbox_prerequisite_cites_dec_141[2]` · `test_dec_141_is_an_owner_decision_that_names_the_prerequisite_and_its_version[2]` (green today) · `test_the_install_command_of_a_sandbox_prerequisite_is_the_owners[2]` · `test_the_uninstall_command_of_a_sandbox_prerequisite_is_the_owners[2]` · `test_a_sandbox_prerequisite_carries_a_sha256_digest[2]` · `test_a_sandbox_prerequisite_carries_a_calendar_date[2]` · `test_the_sandbox_prerequisite_on_this_machine_is_the_recorded_version[2]` (`local_only`) · `test_an_entry_of_this_ticket_states_every_fact_the_schema_requires[bubblewrap, socat]` | No bubblewrap entry, no socat entry |
| **Failure 1.** A headless run uses a CLI below 2.1.285 | `test_w1_48_cli.py`, `test_w1_48_claude_code.py` | `test_the_cli_for_headless_runs_is_2_1_285_or_later` (`local_only`, green today: the CLI is 2.1.288) · `test_the_cli_for_headless_runs_is_the_pinned_version` (`local_only`) · `test_the_claude_code_pin_is_2_1_285_or_later` | No Claude Code entry (the machine-only case is already green) |
| **Failure 2.** bubblewrap or socat is missing from the registry while gov launch depends on it | `test_w1_48_sandbox_prereqs.py` | `test_a_sandbox_prerequisite_is_recorded_in_the_registry[2]` · `test_the_registry_records_the_prerequisites_the_contract_names_for_the_sandbox` | No bubblewrap entry, no socat entry |
| **Failure 3.** The pin is raised without a recorded owner approval | `test_w1_48_claude_code.py`, `test_w1_48_cli.py` | `test_the_pin_as_recorded_has_a_recorded_owner_approval` · `test_a_raised_pin_is_not_covered_by_the_approval_of_the_recorded_one` · `test_the_cli_for_headless_runs_is_the_pinned_version` (`local_only`: a CLI newer than the record is an unrecorded raise) · and the five approval cases of success 1 | No Claude Code entry |
| **DEC-205** (owner, added to this batch). The pinned CLI is the one at `~/.local/bin/claude` | `test_w1_48_cli.py` | `test_the_record_is_about_the_cli_at_local_bin_claude` · `test_the_pinned_binary_is_the_one_at_local_bin_claude` (`local_only`) · `test_the_cli_for_headless_runs_is_the_pinned_version` (`local_only`) | No Claude Code entry |
| **DEC-207** (owner, added to this batch). Every Node 22 install command carries the PATH prefix | `test_w1_48_node22_prefix.py` | `test_every_node_22_command_of_the_registry_carries_the_path_prefix` · `test_the_check_sees_the_node_22_commands_the_registry_has[2]` · `test_the_check_refuses_a_node_22_command_without_the_prefix[8]` · `test_the_check_accepts_a_node_22_command_with_the_prefix[5]` · `test_the_check_leaves_other_commands_alone[5]` | **Green today** (21 cases): W1-06's registry already carries the prefix on its openspec and ccusage commands |

**Count.** KPI lines with tests: 6 of 6 (3 success, 3 failure). Covers ids with tests: 2 of 2 (CAP-25.d, CAP-61.e).
Owner additions with tests: 2 of 2 (DEC-205, DEC-207). Open decision packages: 2 (DP-1, DP-2), both about points no
test here decides.

**Green before implementation (26 cases).**

- 21 in `test_w1_48_node22_prefix.py` (DEC-207): the prefix is already on every Node 22 command; 18 of the 21 test the
  check itself on fixed sample commands and never read the registry.
- 2 in `test_w1_48_sandbox_prereqs.py`: `test_dec_141_is_an_owner_decision_that_names_the_prerequisite_and_its_version`
  reads only the register.
- 2 in `test_w1_48_cli.py`: `test_the_cli_at_local_bin_claude_is_installed` and
  `test_the_cli_for_headless_runs_is_2_1_285_or_later` read only the machine; the owner's install (DEC-203) is done.
- 1 in `test_w1_48_registry.py`: `test_the_registry_as_read_is_the_committed_one`. It turns red while the registry has
  uncommitted changes and green again once they are committed.

**Green path checked.** The 45 cases that read fixtures were run once, in memory, against the committed registry plus
three sample entries (Claude Code 2.1.288 citing DEC-203, bubblewrap 0.9.0 and socat 1.8.0.0 citing DEC-141): all
passed. Nothing was written to the registry.

## Readings the sources do not spell out

1. **Entry names** are compared without case. Accepted: `claude code` / `claude-code` / `claude`; `bubblewrap` /
   `bwrap`; `socat`. **Note for the implementer:** W1-06's
   `test_every_entry_outside_the_stack_cites_a_decision_that_names_the_tool` looks for the entry's name, as written,
   in the cited decision. DEC-203 holds "Claude Code" and `claude`, not `claude-code`, so the name `claude-code` would
   pass here and fail there. `claude code` and `claude` pass both.
2. **One entry per tool, one exact version.** `version` is digits and dots (an optional leading `v` and suffix are
   allowed by the form test, but the comparison with 2.1.285 needs digits and dots only).
3. **"2.1.285 or later"** is a comparison of the dotted numbers as integers: 2.1.285, 2.1.288 and 2.2.0 pass; 2.1.284
   fails. The pin's version is not fixed to 2.1.288 in any test, so a later raise needs no new test.
4. **"With install and uninstall commands"** for Claude Code: `install` names `claude` and the pinned version;
   `uninstall` is not blank, is not the install command, and names `claude`. What the uninstall command must be
   (remove the binary, or go back to an earlier version) is not tested. Whether `install` may start with a bare
   `claude` is DP-2.
5. **"Date"** is a string that starts with a real `YYYY-MM-DD` date. For Claude Code it is not before the date of the
   approving decision (DEC-083: installs only after approval). For bubblewrap and socat no order is tested: DEC-141 is
   the record of an owner action already made.
6. **"The upgrade is installed by the orchestrator through a DEC-083 decision package"** is tested as DEC-203 answers
   it: the recorded owner approval, not who ran the command. The cited decision must be an entry of the register whose
   status starts `ACCEPTED (owner` and holds `DEC-083`, whose own text names "Claude Code" and exactly the registry's
   version, and which no other registry entry cites (DEC-197: "its own register entry"). In the register as it stands
   only DEC-203 fits Claude Code 2.1.288. No test names DEC-203.
7. **A decision's own text** is its heading and its lines up to the next `## ` heading or table row, as in W1-06
   (its reading 16): without that cut the last entry of a section would hold the section's change-log row.
8. **"The pin is raised without a recorded owner approval"** is tested in three ways. (i) The entry as it stands meets
   every condition of reading 6 at once. (ii) The same entry with its version one patch higher is refused, because the
   cited decision does not name that version: a raise needs a new register entry. (iii) On this machine the CLI's
   version equals the pin exactly; a CLI newer than the record is a raise that nobody recorded. So **"at or above the
   pin" (success 2) is tested as "equal to the pin"** for the CLI. A CLI above the pin fails this suite until the
   registry and the register are updated.
9. **"The CLI used for headless runs"** is the file `~/.local/bin/claude` (DEC-205: every headless worker is started
   with that absolute path). Its version is what `~/.local/bin/claude --version` prints first (`2.1.288 (Claude
   Code)`). No test resolves `claude` through `PATH`. **Not tested:** that a given headless run was in fact started
   with that path. Until W1-46's launcher exists the command is typed by the orchestrator, and no committed file this
   ticket may change holds it.
10. **"A headless run uses a CLI below 2.1.285" (failure 1)** is therefore tested as: the file of reading 9 is 2.1.285
    or later (read from the machine alone), the registry's pin is 2.1.285 or later, and the two are equal.
11. **The registry's sha256 for Claude Code** is the sha256 of the file `~/.local/bin/claude` resolves to (DEC-196: a
    single-file binary; DEC-203 records the value). This is also the DEC-205 check that the pinned CLI is that file and
    not another copy.
12. **"The registry record states both."** `version` is the CLI's version. The record is about `~/.local/bin/claude`
    when some fact of the entry (the note, a command, or another key) holds `~/.local/bin/claude`,
    `$HOME/.local/bin/claude`, `${HOME}/.local/bin/claude` or `/home/<user>/.local/bin/claude`. The extension's
    version is stated when one clause of the entry, outside `version`, `install` and `uninstall`, holds the word
    "extension" and the pinned version. A clause ends at `. `, `; `, `: ` or a line end; a key and its value form one
    statement (`<key>: <value>`), so a key such as `extension_version` counts too (the schema allows extra keys). A
    clause that holds "extension" may name no other `2.x.y` version.
13. **The VS Code extension on this machine**, as far as it is clear without DP-1: a folder
    `anthropic.claude-code-<version>…` under `~/.vscode-server/extensions/` whose `package.json` gives the pinned
    version must exist, and its bundled binary `resources/native-binary/claude` must print the pinned version with
    `--version`. This is necessary under every option of DP-1; which folder is "the" extension is not decided here.
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
    are found through `PATH`; DEC-205's rule is about `claude` only.
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

## Decision packages

Two points are not tested, because the sources allow more than one reading. Both are open.

### DP-1 — Which extension folder is "the VS Code extension", and what its "bundled version" is (OPEN)

- **Question.** Five Claude Code extension folders are on disk under `~/.vscode-server/extensions/`: 2.1.283, 2.1.284,
  2.1.285, 2.1.286 and 2.1.288. Which one is "the VS Code extension" of KPI success 2 and CAP-61.e? And is its "bundled
  version" the version in its `package.json`, or the version its bundled binary
  (`resources/native-binary/claude`) prints?
- **Why now.** The KPI requires the CLI and the extension's bundled version to be the same. A test must pick one
  folder. Today every reading gives 2.1.288, so the choice changes nothing now; it decides when the suite turns red
  after VS Code updates the extension by itself, which it does without an install command and without an approval.
- **Options.**
  - (a) The folder VS Code has active: the `anthropic.claude-code` row of `~/.vscode-server/extensions/extensions.json`
    (today 2.1.288). Folders listed in `.obsolete` are ignored.
  - (b) The highest version among the folders on disk.
  - (c) Every folder not listed in `~/.vscode-server/extensions/.obsolete` (today only 2.1.288 is not listed).
  - (d) No machine check of the extension at all: the registry's statement is the record, and the owner aligns the two
    by hand.
  - For (a) to (c), the bundled version is either (i) the folder's `package.json` version, or (ii) what the bundled
    binary prints with `--version`, or (iii) both, and the binary's sha256 equals the registry's.
- **Impact.** (a) follows what VS Code runs, and reads two of VS Code's own bookkeeping files, whose format is not a
  public contract. (b) needs no bookkeeping file, but a folder that VS Code has downloaded and not yet activated, or
  never removes, decides the result. (c) is close to (a) and depends on one file only. (d) leaves the failure "the
  extension moved ahead of the CLI" to the owner's eye. Under (a), (b) and (c) alike, an automatic extension update
  turns the suite red until the CLI is raised through a new approval; that is the alignment CAP-61.e asks for, and it
  also means the orchestrator's interactive session can run on a version the registry does not pin until then.
  (iii) is the strongest: the same bytes, not only the same number; today the two files have the same sha256.
- **Reversibility.** High: one test.
- **Cost.** One `local_only` case of about fifteen lines for any of (a) to (c). For the owner: under (a) to (c), either
  turn off automatic updates of the extension or accept a red case after each update until the CLI follows.
- **Recommendation.** (a) with (iii). `test_a_vs_code_extension_at_the_pinned_version_bundles_the_pinned_cli` already
  tests what every option needs (a folder at the pin whose bundled binary prints the pin); the answer adds "and no
  other folder is the active one".
- **Confidence.** Medium.

### DP-2 — May the recorded install command start with a bare `claude` (OPEN)

- **Question.** DEC-203 records the owner's command as `claude install 2.1.288`. DEC-205 says a headless worker is
  never started with a bare `claude`, and the brief of this batch says the registry record must be about
  `~/.local/bin/claude`, never a bare `claude` resolved through `PATH`. Must the registry's `install` (and `uninstall`)
  command spell the path (`$HOME/.local/bin/claude install 2.1.288`), or is it the command as the owner ran it?
- **Why now.** The registry entry is written in this ticket. With a bare `claude`, whoever repeats the recorded
  command on a changed `PATH` could run the Windows-side copy; with the path spelled out, the record differs from the
  command DEC-203 records.
- **Options.** (a) Every `claude` command word in the entry's `install` and `uninstall` is written with the path
  `$HOME/.local/bin/claude`; a test refuses a bare one. (b) The commands are recorded as the owner ran them; the entry
  names `~/.local/bin/claude` elsewhere (already tested, reading 12). (c) As (a), and the test also covers every other
  registry entry.
- **Impact.** (a) the record cannot start the wrong copy and stays close to DEC-205; a first install on a machine with
  no `~/.local/bin/claude` cannot use it, so the command is a re-install or upgrade command only. (b) the record equals
  DEC-203's text, and the rule against a bare `claude` stays a rule for headless runs only. (c) no other entry runs
  `claude` today, so it equals (a).
- **Reversibility.** High: two strings of one entry.
- **Cost.** (a) one case of about ten lines. (b) none.
- **Recommendation.** (a).
- **Confidence.** Medium.
