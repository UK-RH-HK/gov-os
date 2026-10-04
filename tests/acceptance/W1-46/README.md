# W1-46 acceptance tests: worker session launcher (`gov launch`)

Ticket `DAEO-jdqr`, profile FULL. Written before implementation by the Independent Test Designer (MR-3, DEC-069),
proportional to the profile (DEC-221): every KPI line, success and failure, and every covers id has at least one test.
Batch 2 revised the suite, still before implementation, for the decisions on batch 1's seven packages (DEC-231 to
DEC-234, DEC-240 to DEC-242). Batch 3 added tests after implementation, from seven behaviours a review described
(DEC-136); see "Batch 3" below. Batch 4 added and revised tests after implementation for the decisions on every open
package (DEC-271 to DEC-273, DEC-311 to DEC-317) and for the new success line (DEC-315); see "Batch 4" below.
Batch 5 added tests after implementation, from two behaviours a review described (DEC-136); see "Batch 5" below.
Batch 6 added tests after implementation for the delegated decision on batch 5's two packages (DEC-334); see
"Batch 6" below. Batch 7 added tests after implementation, from one behaviour a review described (DEC-136); see
"Batch 7" below.

```
python3 -m pytest tests/acceptance/W1-46 -q -p no:cacheprovider                      # everything (starts two real sessions once gov launch exists)
python3 -m pytest tests/acceptance/W1-46 -q -p no:cacheprovider -m "not local_only"  # no session, no network, no cost
```

494 tests: 458 start nothing, 36 are `local_only`. After implementation: 45 were added in batch 3; batch 4 added 132
(129 that start nothing, 3 `local_only`), rewrote 12 (10 that start nothing, 2 `local_only`) and removed one
`local_only` case (the host DEC-316 drops); batch 5 added 15 that start nothing; batch 6 added 15 that start nothing; batch 7 added 7 that start nothing.

## How the tests see what the launcher builds

The command line is `gov launch <role> <ticket> [-- <CLI arguments>]` (DEC-231): the role and the ticket are
positional, and everything after `--` goes to the CLI unchanged. The whole suite uses that form, through one helper
(`support.launch`) and one line of the live tests.

The launcher starts the CLI by its absolute path `~/.local/bin/claude` (DEC-205). Each test runs `gov launch` with a
temporary `HOME` whose `.local/bin/claude` is a stand-in program the test writes. The stand-in starts no session: it
records its arguments, its environment and the content of every `--settings` value, and ends. What it recorded is what
a worker session would have been started with. A second stand-in, first on `PATH` under the bare name `claude`,
records a launcher that did not use the absolute path. The stand-in answers `--version` with the version the tool
registry records. No dry-run option is needed, and no internal is imported.

`gov launch` runs in a temporary project: this repository's `src/gov`, kernel template, role files, committed
settings, `pyproject.toml` and `governance/project/research-allowlist.yaml` (once it exists), copied from git's
listing, plus fixture tickets (engineer `DAEO-zz90`, auditor `DAEO-zz94`, research `DAEO-zz97` with `allowed_paths:
experiments/spikes/exp-901/**`), sibling experiments, and a `.gov-runtime/` with findings, records, snapshots and
scratch. Nothing is installed; `gov` is run the way W1-07's suite runs it.

The guard is asked through the PreToolUse commands the project's committed settings register, run through the shell
as the harness runs them, with `GOV_ROLE`, `GOV_TICKET` and the session's `cwd`. No tool call is made.

**The held-out path.** `governance/project/held-out.yaml` is not copied, and the copy of `.claude/settings.json`
leaves out the `Read` rules with an absolute path. Every project gets a `held-out.yaml` the test writes, naming a
stand-in directory it made (DEC-218), as in W1-47. One static test reads the committed list at run time through
W1-47's `load_configured`, to check that no file of the ticket repeats a value; a value is never shown.

## KPI lines, tests and red reasons

Red reason **L**: `gov launch` is not a command yet (`gov launch --help` ends with exit code 2); the `launcher`
fixture stops the test, which pytest reports as an error. Red reason **R**: the guard does not know the role
`research`, so it denies the call. Red reason **F**: the file does not exist.

| KPI line | Tests | Red |
|---|---|---|
| Success 1 [CAP-61.a], failures 1, 2, 8 | `test_w1_46_sandbox_settings.py`: strict sandbox for each of the four roles; no `excludedCommands`; one `--settings` argument; **refusal when the repository's settings carry a `sandbox` key** (committed, local, local linked to scratch; a strict block and an empty one too) (DEC-233); refusal when the caller hands over a weaker sandbox (five forms); only the four worker roles are launched; the absolute CLI path (DEC-205); the session starts in the repository root; the settings come from a place no worker can write (DEC-136) | L |
| Success 2 [CAP-61.b] | `test_w1_46_role_settings.py`: `GOV_ROLE` and `GOV_TICKET` per role; both in the settings `env` block; the guard decides as that role on that ticket with the values the session was given. Live: `test_the_role_and_the_ticket_reach_the_session_and_its_hooks`, and the sandbox tests of the engineer session | L |
| Success 3 [CAP-61.c] | `test_w1_46_role_settings.py`: empty allowlist for three roles. `test_w1_46_research_allowlist.py` (DEC-241): the project file exists and is a list of hosts; the built research allowlist carries the sixteen starting hosts (DEC-316) and the `*.readthedocs.io` entry, and not `cdn-lfs.huggingface.co`; it is a list of named domains; a host added to the project file is in the next launch's allowlist, and the starting hosts stay; the file does not reach the three other roles; a malformed file refuses the launch (seven forms); the list is under `hosts`, and a project without the file launches on the kernel default (DEC-272). Live: the empty list refuses a connection; the sandbox accepts a connection to each of the sixteen starting hosts and to `docs.readthedocs.io`, and refuses `example.com` | L; F for the file |
| Success 4 [CAP-61.c], failures 4, 5 | `test_w1_46_research_fence.py`: every other top-level entry and sibling along the path is denied; the folder stays writable; `.git` is left out; glob-named entries are left out; a path that does not exist at launch is not listed; the list is computed at each launch; the guard refuses a research write to a new path. `test_w1_46_launch_refusals.py` (DEC-242): a research ticket that is not exactly one experiment folder refuses the launch (five forms); a second research ticket gets its own fence. Live: sibling write fails; new path refused or reported | L (guard tests green already) |
| Success 5 [CAP-22.d] | `test_w1_46_research_role.py`: role file, its six parts, the agent definition, the roster entry; writes inside the folder allowed, outside denied; no scope on another role's ticket; no network decision by the guard | F, R |
| Success 6 [CAP-25.e], failures 6, 7 | `test_w1_46_research_installs.py`: 11 install forms let through in the folder (the four `uv` forms, three value options of DEC-216, `uv pip install`, venv `pip`, `npm install`), below it, after `cd` into it (DEC-240), in every permission mode; no ask rule in the committed or the built settings; denied outside the folder, after `cd` into another folder, on another ticket, with `sudo`; denied for the three other roles. Live: the install succeeds into a venv in the folder; one outside the repository fails. W1-04's suite: run as it stands | R, L |
| Success 7 [CAP-61.d] | `test_w1_46_role_settings.py`: a temp directory of the session's own, which exists; two launches get two. Live: `mktemp` in each session, asserted (DEC-234) | L |
| Success 8 [CAP-58.d] | Live: interpreter one-liner, command substitution, here-string, and a Write-tool call. `test_w1_46_research_role.py`: the guard refuses a file-tool write outside the repository for the four roles | L (guard tests green already) |
| Success 9 [CAP-49.b], failure 9 | `test_w1_46_held_out.py`: the `Read` rule per role; one per configured path; read at each launch; refusal on a missing key, an empty list, a key without a value, invalid YAML, a list at the top level, an empty file; **a project with no `held-out.yaml` launches, strictly sandboxed, with no held-out rule** (DEC-242, DEC-223); no file of the ticket names a held-out path. Live: the stand-in looks empty | L |
| Success 10 (DEC-180, DEC-311) | `test_w1_46_role_settings.py`: the built rules cover the freeze flag, findings, records, snapshots and a new entry, and not scratch; the guard refuses the file tools. `test_w1_46_runtime_and_ln.py` (batch 4): a literal rule per name that exists at launch, plus the freeze flag; the guard refuses `.gov-runtime/` outside scratch to every role, and `ln` to a destination the role may not write. `test_w1_46_links_and_cp_targets.py` (batch 5): a link and a write through it in one command, and `cp` with the target directory in an option. `test_w1_46_hard_links_mv_and_install.py` (batch 6, DEC-334): a hard link to a file the role may not write, `mv --target-directory=` and `install`. `test_w1_46_options_after_the_destination.py` (batch 7): `install`, `cp` and `ln` with an option and its value after the destination. Live: opaque Bash writes fail, `ln` onto and into a name that exists at launch fails, scratch is writable | L |
| Success 11 (DEC-315) | `test_w1_46_protected_trees.py` (batch 4): `Edit` deny rules cover `tests/acceptance/**` for engineer, auditor and research, and `.tickets/**` and `.claude/**` for the four roles; the test designer's settings carry no rule for the acceptance tests; a ticket that names a path there keeps the rules; the guard refuses the file tools. Live: three opaque Bash writes fail in the engineer session | see Batch 4 |
| Failure 3 (a worker role installs system-wide) | the denials of success 6, `test_sudo_stays_denied_to_the_research_role`, live `test_a_research_install_outside_the_repository_fails_at_the_write_fence` | green / L |
| DEC-242 (no KPI line of its own; refusals in the words of success 1) | `test_w1_46_launch_refusals.py`: an unknown ticket (engineer, research); a ticket that is `open` or `closed`, with the same ticket `in_progress` launching; a ticket of another role (research on an engineer's ticket, engineer on a research ticket, engineer on an auditor's ticket) | L |

| DEC-271, DEC-273 (refusals in the words of success 1) | `test_w1_46_launch_refusals.py`: the two independent roles on a ticket of any role, and not on one that is not `in_progress`. `test_w1_46_experiment_folder.py`: a research ticket whose folder is not under `experiments/` | see Batch 4 |
| DEC-313, DEC-314 (refusals in the words of success 1; success 2 and 8) | `test_w1_46_bypass_and_added_directories.py`, `test_w1_46_guard_wiring.py` | see Batch 4 |
| DEC-317 (no KPI line; CAP-27, CAP-28) | `test_w1_46_exit_codes.py`; W1-07's suite, re-run as it stands | green |

Covers ids: CAP-61.a, CAP-61.b, CAP-61.c, CAP-61.d, CAP-22.d, CAP-25.e, CAP-58.d, CAP-49.b. Each has tests above.
Success 10 and success 11 end with no covers id in the ticket.

## The red result before implementation

`-m "not local_only"`: **31 failed, 122 errors, 94 passed** (247 tests). The 34 `local_only` tests are errors too,
with reason L: they stop at the `launcher` fixture and start nothing.

- 122 errors: all reason L.
- 31 failures: 26 with reason R (the research role's installs and writes inside its folder, scratch), 5 with reason
  F (the role file, its six parts, the agent definition, the roster entry, `research-allowlist.yaml`).

New and revised tests of batch 2, and their red reason:

| Test | Decision | Red |
|---|---|---|
| `test_the_launcher_refuses_when_the_repositorys_settings_carry_a_sandbox_key` (6), revised from "changes nothing the launcher builds" | DEC-233 | L |
| `test_the_key_itself_refuses_the_launch_whatever_it_holds` (2) | DEC-233 | L |
| `test_w1_46_research_allowlist.py` (13; two of them moved from `test_w1_46_role_settings.py` and revised) | DEC-241 | L; `test_this_repository_has_the_research_allowlist_file`: F |
| `test_the_sandbox_accepts_a_connection_to_a_starting_host_of_the_research_allowlist` (18, was 6), `local_only` | DEC-241 | L |
| `test_w1_46_launch_refusals.py` (14) | DEC-242 | L |
| `test_a_project_without_a_held_out_file_launches_with_no_held_out_rule` (2) | DEC-242, DEC-223 | L |
| `test_a_research_install_after_cd_into_another_folder_is_denied` (1) | DEC-240 | green already (the role is unknown) |
| removed: the `uv --directory` and `uv --project` cases (14: 2 let through, 6 outside the folder, 6 for the other roles) | DEC-240 | (6 + 6 were green) |

## Batch 3: tests added after implementation (DEC-136)

The ticket was implemented in `c70bbb69`. A review after it described seven behaviours, A to G, that the suite
missed. Each was decided from the specification: a test where a KPI line, a Contract item or a decision answers it, a
package where none does. Where a package is open, the test asserts only what every answer shares. 45 tests in four
new files, all without a session; they count as tests added after implementation (DEC-106).

| Behaviour | Tests | Line or decision | Red reason |
|---|---|---|---|
| A. Arguments after `--` that take the guard away | `test_w1_46_guard_wiring.py`: `test_the_launcher_refuses_the_argument_that_skips_the_hooks` (3: `--bare` alone, after and before the ordinary arguments); `test_no_session_is_started_without_the_projects_settings_unless_the_launcher_wires_the_guard` (3: `--setting-sources user`, joined with `=`, empty) | Success 2 [CAP-61.b] "both variables reach the guard"; success 8 [CAP-58.d]; MR-3; DEC-135; DEC-231 | `gov launch` ends with exit code 0 and starts the session; the built settings register no PreToolUse command |
| A, control | `test_a_headless_workers_ordinary_arguments_pass_unchanged` (2) | DEC-231, DEC-183 | green already |
| B. The guard is not wired | `test_no_session_is_started_in_a_project_that_does_not_wire_the_guard` (5: no settings file, no `hooks` block, no PreToolUse command, `disableAllHooks: true` committed and local); `test_a_research_session_is_not_started_without_the_guard_either` (1) | Success 2 [CAP-61.b], success 8 [CAP-58.d], success 4 (the fence leans on the guard); DP-11 | as A: exit code 0, a session, no guard registered by the launcher |
| B, control | `test_hooks_left_on_explicitly_do_not_refuse_the_launch` (1) | | green already |
| C. Opaque Bash writes to acceptance tests, tickets and `.claude` | none | no line of the ticket asks for it: DP-12 | |
| D. Any directory as the experiment folder | `test_w1_46_experiment_folder.py`: `test_a_research_ticket_on_the_acceptance_tests_refuses_the_launch` (2) | MR-3; DEC-242 | exit code 0, a session whose fence leaves `tests/acceptance` open |
| D | `test_the_guard_refuses_a_research_write_to_an_acceptance_test_on_a_ticket_that_names_them` (2), `..._bash_write_...` (1) | MR-3 | green already: the guard refuses the research role there, whatever the ticket names |
| D | `test_a_research_ticket_on_the_runtime_directory_opens_nothing_there` (1) | Success 10 (DEC-180) | the launch keeps the runtime rules, but the guard allows a research Write to `.gov-runtime/freeze` on that ticket |
| D | `test_an_entry_with_dot_dot_is_refused_or_the_fence_and_the_guard_hold_the_same_folder` (1) | Success 4 and 5: the fence and the guard's allow-list speak of one folder | launched with the fence built around the sibling, while the guard denies a write there |
| D, the other directories | none | DP-13 | |
| E. `held_out_paths` written twice | `test_w1_46_duplicate_keys.py`: `test_no_session_is_started_without_a_read_rule_for_a_path_named_under_a_repeated_key` (2); `test_the_guard_does_not_let_a_read_of_the_directory_named_first_through` (1); `test_a_broken_first_value_is_not_hidden_from_the_launcher_by_a_valid_second_one` (4); `..._from_the_guard_...` (4) | Success 9 [CAP-49.b]; DEC-218; the guard's side is W1-47's [CAP-49.c] | the last value wins: a session with no `Read` rule for the first path; the guard allows a Read of it; a broken first value launches and the guard does not fail closed |
| F. The allowlist's key written twice | `test_a_malformed_first_list_is_not_hidden_by_a_valid_second_one` (4); `test_a_first_list_of_hosts_is_not_dropped_silently` (1) | Success 3 [CAP-61.c]; DEC-241 | the last list wins: exit code 0; the first list's host is not in the built allowlist |
| G. `uv run -w<package>` | `test_w1_46_install_spellings.py`: denied for the three other roles (3) and for research outside its folder (1); the orchestrator is asked (1) | Failure 7; DEC-174; DEC-216 ("plus `uv run -w`") | the guard allows the command, and asks nothing |
| G, controls | research in its folder (1); `uv run script.py -wide` is no install (1) | DEC-163, DEC-240 | green already |

**Red result after batch 3**, `-m "not local_only"`: **38 failed, 0 errors, 254 passed** (292 tests). 37 of the
failures are batch 3's, grouped above: A 6, B 6, D 4, E 11, F 5, G 5. The other one is
`test_the_research_role_is_a_session_role_definition_like_the_others`, an open question with the owner. 8 tests of
batch 3 are green already (the controls, and the guard's refusal of a research write to an acceptance test). The
`local_only` tests were not run in batch 3.

**Readings of batch 3.**

- A and B. The CLI's help (2.1.288) says `--bare` is "Minimal mode: skip hooks (those defined in settings …)": no
  settings can bring the guard back, and DEC-231 lets the launcher drop no argument, so the launch is refused.
  `--setting-sources` and an unwired project can be answered two ways (DP-11), so those tests accept a refusal, or
  a `--settings` value that registers a PreToolUse command for `Write`, `Edit` and `Bash` (and carries
  `disableAllHooks: false` where the repository switched the hooks off).
- A and B, not tested in batch 3: `--dangerously-skip-permissions`, `--allow-dangerously-skip-permissions`,
  `--permission-mode bypassPermissions`, `--add-dir`, `permissions.defaultMode` and
  `permissions.additionalDirectories` (DP-10). Decided by DEC-313 and tested in batch 4. DP-11 is decided by
  DEC-314: the tests of `--setting-sources` and of B now assert the refusal only.
- E. A key written twice is not judged as "valid" or "invalid" YAML. The tests hold under both readings: refuse, or
  honour both values. A first value that DEC-218 refuses on its own refuses under both.
- F. As E. The key is read from the project's file; the tests are skipped if the file holds its list without a key.
- G. Tested: `uv run -w<package>` only. Left as residuals, not tested: the prefixes `env` and `command` (recorded
  in `governance/project/bootstrap.md` at W1-04's close as "A prefix command (`env`, `command`, `nohup`, `time`,
  `xargs`) hides `sudo` or an install from the rule", under DEC-135 and Contract item CAP-25.c), and `exec`, `nice`,
  `time`, `xargs`, `bash -c '…'`, `python3 -mpip`, `uv pip sync`, `uv tool run`, `npm ci`, `npx`, `yarn add`,
  `pnpm add`, `pipx run`, `cargo add`, `go get`, and a pipe into a shell. No KPI line and neither DEC-174 nor
  DEC-216 names them. In a launched session of the three other roles the empty allowlist blocks the download, and
  the sandbox stops a write outside the repository; none of them lets an implementer change an acceptance test.

## Batch 4: tests added and revised after implementation, for the decisions on every package

The owner decided DP-10, DP-11, DP-12, DP-14, DP-15 and DP-16 (DEC-311 to DEC-316) and W1-25's DP-1 (DEC-317); the
orchestrator decided DP-8, DP-9 and DP-13 under delegation (DEC-271 to DEC-273). A revised test is a rewrite after
implementation, reason "owner decision". A new case is a test added after implementation, reason "owner decision"
(DEC-311 to DEC-317) or "delegated decision" (DEC-271 to DEC-273) (DEC-106).

| Decision | Tests | Added | Rewritten | Red reason today |
|---|---|---|---|---|
| DEC-311, `.gov-runtime/` and `ln` | `test_w1_46_runtime_and_ln.py`: a literal `Edit` rule per name at launch (4), for the freeze flag when it does not exist (4), computed at each launch (1), none on scratch (4); the guard refuses `.gov-runtime/` outside scratch to the orchestrator and product-spec by file tool (2) and to the six roles by a plain Bash write (6); scratch writable for the six roles (6); `ln` symbolic and hard to a destination the role may not write (6), forced onto or into a name that exists, and after `cd` (4), for the orchestrator and research (2), research held to its folder (1); the control, `ln` to a writable destination (4). Live: `test_ln_into_gov_runtime_fails` (2), now `ln -sf` onto the findings file and `ln` into the snapshots directory | 44 | 2 (live) | 13 red: the guard does not read `ln`, so it allows the command. 31 green: the literal rules and the guard's refusal to every role are built. Live: green |
| DEC-313, bypass and added directories | `test_w1_46_bypass_and_added_directories.py`: four arguments in four positions (16), two joined spellings (2), the research role (1), two keys in the committed and the local settings (4); controls: `acceptEdits` as an argument (2) and as `permissions.defaultMode` (2), an argument's name in the prompt (1) | 28 | 0 | 23 red: `gov launch` ends with exit code 0 and starts the session. 5 controls green |
| DEC-314, guard wiring | `test_w1_46_guard_wiring.py`: `--setting-sources` (3), an unwired project (5), research (1) now assert the refusal only; added: `--setting-sources` naming the project's settings (2), the built settings carry no `hooks` and no `disableAllHooks` (4) | 6 | 9 | green: built as decided |
| DEC-315, success 11 | `test_w1_46_protected_trees.py`: acceptance tests (3 roles), tickets (4), `.claude` (4), the test designer's settings (1) and on an auditor's ticket (1), a ticket that names such paths (1), the guard and the file tools (8). Live: `test_an_opaque_bash_write_to_the_acceptance_tests_the_tickets_and_dot_claude_fails` (3) | 22 + 3 live | 0 | 10 red: the built settings carry no such rule for engineer, test designer and auditor. 12 green: research has the rules through its fence; the guard refuses; the test designer has no rule yet. Live: 2 red (the write lands), 1 green (`.claude/settings.json`) |
| DEC-316, the dropped host | `test_the_host_the_owner_dropped_is_not_in_the_built_allowlist` (1); `test_the_research_allowlist_carries_the_starting_hosts` counts sixteen; the live host list loses one case (17 remain, unchanged) | 1 | 1 | 1 red: the kernel default and the project's file still name the host |
| DEC-271, tickets per role | `test_w1_46_launch_refusals.py`: test designer and auditor on an engineer's, an auditor's and a research ticket (6), refused on an `open` or `closed` ticket (4), research on an auditor's ticket (1) | 11 | 0 | green: built |
| DEC-272, the key `hosts` | `test_w1_46_research_allowlist.py`: this repository's file (1), a list under another key or at the top level refuses (2), a project without the file (1) | 4 | 0 | green: built |
| DEC-273, the experiments root | `test_w1_46_experiment_folder.py`: `.claude`, `.tickets`, `governance/project`, `src`, `.git`, `docs/experiments/exp-1`, `spikes/exp-1` (7) | 7 | 0 | 7 red: exit code 0, a research session fenced around that directory |
| DEC-317, exit codes | `test_w1_46_exit_codes.py`: `gov launch` ends with the session's exit code 3, 4, 42 (3) and 0 (1); a refusal is exit code 1 (1); no arguments is exit code 2 (1). W1-07's suite re-run as it stands: 228 passed | 6 | 0 | green today; they hold the behaviour through the change in `main.py` |

Totals: 132 added (110 "owner decision", of them 3 live; 22 "delegated decision"), 12 rewritten ("owner decision": 9
for DEC-314, 1 for DEC-316, 2 live for DEC-311), one live case removed (DEC-316).

**Red result after batch 4**, `-m "not local_only"`: **55 failed, 366 passed** (421 tests). 54 are batch 4's: DEC-313
23, DEC-311 13, DEC-315 10, DEC-273 7, DEC-316 1. The other one is
`test_the_role_file_states_the_six_parts_the_kpi_names` (it finds none of the six parts in the committed
`.claude/agents/research.md`; red before batch 4 too, and not a batch 4 test). That one was a fault of the test,
corrected after implementation ("test error"): it kept its result per file under the base name, and the kernel role
file and the agent definition are both `research.md`, so the agent definition's result replaced the kernel role
file's, which states all six parts. The result is now kept under the path; the assertion and the counts are
unchanged. The `local_only` tests were run once in batch 4,
before the engineer's round: **2 failed, 34 passed** (36 tests); the two are DEC-315's acceptance test and ticket.

**Readings of batch 4.**

- DEC-311. A literal rule names one path and holds no `*`, `?` or `[`. "Every name that exists under
  `.gov-runtime/`" is read as the entries of that directory itself: a rule on `snapshots` holds for what is under
  it. A name created there at the OS level after launch is a recorded residual and is not tested as refused, in
  the settings or live. `ln` is tested as `ln [-s] [-f] <target> <destination>`, with a directory as destination
  and after `cd`. Not tested: `ln -t <directory>`, `ln <target>` alone, several targets, and what a hard link in a
  writable place lets a session do to the file it links to (reading 16).
- DEC-313. "The matching settings keys" are tested in `.claude/settings.json` and `.claude/settings.local.json`,
  the two files DEC-233 names. Not tested: `additionalDirectories` with an empty list, user or managed settings.
- DEC-315. The rules are read by what they cover (reading 4), so a rule on `.claude` or a pattern both pass; the
  live assertions show that the rule binds Bash. Each live assertion needs the write itself to fail (its exit
  code), because the containment check restores an acceptance test afterwards (DEC-143). The package left out a
  path the ticket's own `allowed_paths` names; the decision as taken does not, so the rule stays and no exception
  is asserted. This ticket's `.claude/agents/research.md` was committed by the owner (DEC-312). The live
  `.claude/settings.json` case is green before the rule exists: in the one live run the write already failed in
  the sandbox (why was not looked into). It stays as a regression case; the built-rules test covers `.claude/`.
- DEC-273. Only the default root is tested: no decision says how a project names another one (DP-18).
- DEC-317. See DP-17. Nothing is asserted about `main.py` or about the names a command module exposes.

## Batch 5: tests added after implementation (DEC-136)

A review described two behaviours of the guard that the suite missed. Both were decided from the specification and
became tests: 15 cases in `test_w1_46_links_and_cp_targets.py`, none with a session, all tests added after
implementation, reason "review finding (DEC-136)". Only the guard's decision on the command is asserted, never a
reason text or a mechanism; an engineer is the role in every case, on its ticket `src/gov/guard/**`.

| Behaviour | Tests | Line or decision | Red reason today |
|---|---|---|---|
| 1. A link and a write through it, in one command | `test_the_guard_refuses_a_link_and_a_write_through_it_in_one_command` (5): a symbolic link from a name in the engineer's paths to the acceptance-test directory, then a redirect (`&&`), `touch` (`;`) or `cp` through it; a hard link to an acceptance test that exists, then a redirect onto the link; a symbolic link to the freeze flag, then `touch` | MR-3; DEC-135; DEC-311; success 10 ("through ln") | 5 red: the guard allows the command. The link's destination is in the engineer's paths, and the second write resolves there because the link does not exist yet |
| 1, as two calls | `test_the_guard_refuses_the_write_when_the_symbolic_link_was_made_by_an_earlier_call` (1) | as above | green already; kept as a regression case |
| 1, control | `test_the_guard_does_not_refuse_a_link_whose_source_and_destination_are_inside_the_roles_paths` (2: symbolic, hard) | DEC-311 | green already |
| 2. `cp` with the target directory in an option | `test_the_guard_refuses_cp_with_the_acceptance_tests_as_the_target_directory_option` (4: `-t <dir>`, `-t<dir>`, `--target-directory=<dir>`, `--target-directory <dir>`); `test_the_guard_refuses_cp_with_the_tickets_as_the_target_directory_option` (2: `-t <dir>`, `--target-directory=<dir>`) | MR-3; DEC-135; the ticket's `allowed_paths` | 6 red: the guard allows the command; it takes the last operand, the engineer's own file, as the destination |
| 2, control | `test_cp_with_the_destination_as_the_last_operand_is_judged_as_before` (1: allowed inside the engineer's paths; refused onto an acceptance test, into that directory and onto a ticket) | | green already |

**Red result after batch 5**, `-m "not local_only"`: **11 failed, 425 passed** (436 tests). The 11 are batch 5's: 5 for
behaviour 1, 6 for behaviour 2. The 4 other cases of batch 5 are green already (the controls and the two-call case).
Every test of the earlier batches passes. The `local_only` tests were not run in batch 5.

**Readings of batch 5.**

- The controls are forms that are plainly inside the role's paths, because a guard that refuses a form it cannot
  judge is a correct guard: the link alone (no write after it), and `cp` with its destination last. Not asserted as
  allowed: a link and a write through it that both stay inside the role's paths, a link followed by an unrelated
  write, and `cp -t` with a directory the role may write. An engineer may refuse those.
- The symbolic link's target is written as an absolute path, so that it names the same place whether a reader
  resolves it from the working directory or from the link's directory.
- "The same holds as two calls" is true for the symbolic link only. For the hard link the brief's statement does
  not hold: with the hard link on disk, the guard allows the redirect onto it today. The one-command hard-link case
  is a test (the brief's expectation, and DEC-135); the two-call case is DP-19.
- Not tested: separators other than `&&` and `;` (a pipe, a newline, a subshell), a link made by another program
  (`cp -s`, `cp -l`, an interpreter), a write through the link by an opaque form, a chain of two links, the other
  roles, `.tickets/` and the other names of `.gov-runtime/` for behaviour 1, `.gov-runtime/` for behaviour 2
  (DEC-221: one other protected tree per behaviour).
- Seen while the red result was taken, outside the two described behaviours and not tested: DP-20.

## Batch 6: tests added after implementation, for the decision on DP-19 and DP-20 (DEC-334)

The orchestrator decided DP-19 and DP-20 under delegation (DEC-334, option (a) of each, stricter-only). 15 cases in
`test_w1_46_hard_links_mv_and_install.py`, none with a session, all tests added after implementation, reason
"delegated decision" (DEC-106). Only the guard's decision on the command is asserted, never a reason text or a
mechanism. An engineer on its ticket `src/gov/guard/**` is the role, except in the one control on the test designer.

| Part of DEC-334 | Tests | Red reason today |
|---|---|---|
| 1. A hard link, alone in its command, whose source the role may not write | `test_the_guard_refuses_a_hard_link_to_a_file_the_role_may_not_write` (4): `ln` and `cp -l` from an acceptance test that exists, `link` from the engineer's ticket file, `ln` from the freeze flag; the destination is a new name inside the engineer's paths | 4 red: the guard allows the command; it judges the destination only |
| 1, control on the spelling | `test_the_guard_does_not_refuse_a_hard_link_between_two_names_inside_the_roles_paths` (2: `link`, `cp -l`); `ln` has its control in batch 5 | green already |
| 1, control on the role | `test_the_test_designer_may_hard_link_one_acceptance_test_to_another_name_there` (1) | green already |
| 2. `mv --target-directory=<dir>` | `test_the_guard_refuses_mv_with_a_protected_directory_as_the_target_directory_option` (2: the acceptance-test directory, `.tickets`), the one operand the engineer's own file | 2 red: the guard allows the command |
| 2, control | `test_the_guard_does_not_refuse_mv_with_a_target_directory_inside_the_roles_paths` (1): a directory that exists inside the engineer's paths | green already |
| 3. `install` | `test_the_guard_refuses_install_into_the_acceptance_tests_and_the_tickets` (4): `install -t <dir> <file>` into the acceptance tests, `install <file> <destination>` onto an acceptance test and onto a ticket, `install -D <file> <destination path>` under `.tickets/` | 4 red: the guard allows the command; it does not judge `install` as a write |
| 3, control | `test_the_guard_does_not_refuse_install_to_a_destination_inside_the_roles_paths` (1): the plain form, to a new name beside the source | green already |

**Red result after batch 6**, `-m "not local_only"`: **10 failed, 441 passed** (451 tests). The 10 are batch 6's: 4
hard links, 2 `mv`, 4 `install`. The 5 controls are green already. Every test of the earlier batches passes, batch
5's eleven included. The `local_only` tests were not run in batch 6.

**Readings of batch 6.**

- "A file the role may not write" is judged by its path. The freeze flag does not exist in the fixture project (the
  test asserts it): a project that is frozen could be refused for that reason alone, and the case would show
  nothing. The acceptance test and the ticket file exist.
- The controls are forms plainly inside the role's paths: both names of the link are the engineer's own (or, for
  the test designer, both acceptance tests of its ticket), and the destination of `mv` and `install` is inside
  `src/gov/guard/`. The `mv` control's directory is made by the test, so that the option names a directory.
- Not tested (DEC-221, DEC-135): the other spellings of the target-directory option for `mv` and `install`
  (`--target-directory <dir>`, `-t<dir>`; `cp` has the four in batch 5), `ln -t` and `ln` with several sources,
  `ln -f`, `cp --link` and `cp -al`, a hard link made by another program, a hard link whose source is under
  `.claude/` or one of the other names of `.gov-runtime/`, the auditor and the research role, `install -d`,
  `install` with several sources, `install -D` together with `-t`, and the write through a hard link that is already
  on disk (DEC-334 refuses the link, not the later write).

## Batch 7: tests added after implementation (DEC-136)

A review described one behaviour of the guard that batches 5 and 6 miss. It was decided from the specification and
became tests: 7 cases in `test_w1_46_options_after_the_destination.py`, none with a session, all tests added after
implementation, reason "review finding (DEC-136)". Only the guard's decision on the command is asserted, never a
reason text or a mechanism; an engineer is the role in every case, on its ticket `src/gov/guard/**`.

**The behaviour.** `install`, `cp` and `ln` accept an option after their operands. In `install <file> <destination>
-m 644` the file lands on `<destination>`; the guard takes the option's value as the last operand. With the working
directory inside the engineer's paths (the session's `cwd` is `src/gov/guard`, or the command starts with
`cd src/gov/guard &&`) that value is a name the engineer may write, and the command is allowed.

| Part | Tests | Line or decision | Red reason today |
|---|---|---|---|
| The described forms | `test_the_guard_refuses_a_write_onto_a_protected_file_with_an_option_after_the_destination`, 4 of its 5 cases: `install … -m 644` onto an acceptance test (`cwd` inside the paths); `cp … -S bak` onto an acceptance test (after `cd`); `cp … --suffix bak` onto an acceptance test (`cwd` inside); `install … --mode 644` onto the engineer's ticket file (after `cd`) | MR-3; DEC-135; DEC-334 (`install`); the ticket's `allowed_paths`; batch 5's `cp` control | 4 red: the guard allows the command; it judges the option's value, not the destination |
| The same form with `ln` | the fifth case: `ln -sf <own file> <an acceptance test> -S bak` (`cwd` inside) | DEC-311 ("the destination of `ln` is a write target"); MR-3 | 1 red: the guard allows the command, for the same reason |
| Control, the usual spelling | `test_the_guard_does_not_refuse_install_with_its_option_before_the_operands` (1): `install -m 644 <own file> <new name beside it>`, from the repository root | DEC-334 | green already |
| Control, the working directory | `test_the_guard_does_not_refuse_cp_between_two_names_of_the_working_directory_inside_the_roles_paths` (1): `cp decide.py w1_46_copy.py` with `cwd` inside the paths | | green already |

**Red result after batch 7**, `-m "not local_only"`: **5 failed, 453 passed** (458 tests). The 5 are batch 7's: the
five refusals. The 2 controls are green already. Every test of the earlier batches passes, batch 6's ten included.
The `local_only` tests were not run in batch 7.

**Readings of batch 7.**

- The destination is written relative to the working directory (`../../../tests/acceptance/W1-90/test_fixture.py`):
  the same path without the trailing option is refused today, so the option alone makes the difference.
- `ln` was not in the review's description. It was seen while the red result was taken: `ln -s` and `ln -sf` with
  `-S bak` or `--suffix bak` after the destination, and `ln` (hard) with `--suffix bak`, are allowed today onto an
  acceptance test. DEC-311 decides it, so it is one test and not a package. `mv` in that form is refused today
  (`-S bak` and `--suffix bak`) and has no case.
- Spellings seen as refused today and not tested: the joined ones, `-m644`, `--mode=644`, `--suffix=bak`, and an
  option without a value after the destination (`cp <file> <destination> -p`).
- The cp control of batch 5 runs from the repository root; this batch's control has the session's `cwd` inside the
  role's paths, so that a guard which refuses every command from there does not pass. Not asserted as allowed: the
  trailing-option form with a destination inside the role's paths (`install <own file> <new name> -m 644`, allowed
  today). An engineer may refuse it.
- Not tested (DEC-221, DEC-135): the other options with a value (`-o`, `-g`, `--owner`, `--group`, `-t` after the
  operands), two such options after the destination, `.gov-runtime/` and `.claude/` as the destination, the other
  roles, and other programs that write and accept options after operands (`touch -d`, `tee`, `rsync`, `dd`).

## Green before implementation (94 tests), and why

- The three older roles already behave as the KPI says (42 cases): installs denied for engineer, test designer and
  auditor, also on the research ticket; file-tool writes outside the repository and under `.gov-runtime/` refused.
- The research role's **denials** are green for another reason: the guard denies an unknown role. They are kept
  because they must still hold once the guard knows the role (48 cases: writes outside the folder, installs outside
  the folder and after `cd` into another folder, new paths, another role's ticket, `sudo`, file tools outside the
  repository and under `.gov-runtime/`).
- `test_the_guard_grants_the_research_role_no_network_and_asks_nothing_for_it`: the guard allows a Bash command with
  no write target before it looks at the role.
- Static facts that hold today: no sandbox block in the repository's settings (DEC-161); no install ask rule in the
  committed settings (DEC-172); no file of the ticket names a held-out path.

## The `local_only` tests: cost and needs

`test_w1_46_live_sessions.py`, 36 tests over **two** real headless sessions per run (DEC-232), started through
`gov launch` with the CLI at `~/.local/bin/claude` and the caller's credentials (`-p`, `--permission-mode
acceptEdits`, `--model haiku`, `--max-turns 8`, `--allowedTools Bash,Write`). They are not behind an opt-in
variable, so the ticket cannot close on skipped tests. A run in which the model does not execute the stated command
fails with that reason and is repeated; it is not a finding against the launcher.

| Session | Model work | Needs |
|---|---|---|
| engineer | one Bash call (a probe script in scratch) and one Write call | `bwrap`, `socat`; no network (the connection must be refused) |
| research | two Bash calls: the install, then a probe script in the experiment folder | `bwrap`, `socat`, `uv`, and the network: one `curl` to each of the sixteen starting hosts (DEC-241, DEC-316) and to `docs.readthedocs.io` |

The install uses a wheel the test builds by hand (`--offline --no-index`), so nothing is downloaded. The "system-wide"
install targets a temporary directory outside the repository, so a failing sandbox pollutes nothing. Each session is
told its exact commands; a session that leaves no complete result file fails every test with that reason. Until
`gov launch` exists the tests stop at the `launcher` fixture and start nothing. Batches 1 to 3 could not run them.
Batch 4 ran them once, with the revised probe (36 tests: 34 passed, 2 failed, see "Batch 4"). A starting host that is down, or that does not
answer `https://<host>/`, fails its one test with `curl`'s exit code and the HTTP status in the message.

## Readings

1. `spike-sandbox/EVIDENCE.md` is not in the repository (no commit ever held it). The sandbox key names are the KPI's
   and the Contract's: `sandbox.enabled`, `failIfUnavailable`, `allowUnsandboxedCommands`, `excludedCommands`,
   `sandbox.network.strictAllowlist`, `sandbox.network.allowedDomains`. All six names occur in the installed CLI.
2. "Empty allowlist": `sandbox.network.allowedDomains` is `[]` or absent.
3. `GOV_ROLE` and `GOV_TICKET` must be in the `env` block of the built settings (DEC-183: it "overrides the env block
   in `.claude/settings.local.json`", which in this repository names the orchestrator).
4. `Edit` and `Read` deny rules are read by what they cover, not by their spelling: `//absolute`, `~/`, or relative to
   the project; `*`, `?`, `[...]`, `**`; a rule on a directory covers what is under it. "`.gov-runtime/**` except
   `.gov-runtime/scratch/**`" therefore means: no deny rule covers scratch.
5. The `Read` rule has the form W1-47 accepts: `Read(/<path>)`, with `/` or `/**` after it.
6. The research hosts are DEC-241's, copied from the register, less the one DEC-316 drops: each of the sixteen named
   hosts is an entry of the built allowlist under its own name. "The subdomains of `readthedocs.io`" is the entry `*.readthedocs.io`: the
   installed CLI (2.1.288) accepts a host entry or a `*.` entry, and a `*.` entry matches subdomains only, not the
   bare domain. Nothing found before implementation says the sandbox refuses that form, so there is no package on
   it; the live research session is the proof (`docs.readthedocs.io`).
7. A sandbox key refuses whatever it holds (DEC-233: "carries a `sandbox` key"): a strict block and an empty one too.
8. The experiment folder is the research ticket's single `allowed_paths` entry without its `/**` (DEC-242). "Not
   exactly one experiment folder" is tested with: two entries, no entry, `**`, a pattern over several folders
   (`experiments/spikes/exp-*/**`), and a file. Not tested: a folder that does not exist at launch, an entry without
   `/**`, and where in the repository an experiment folder may be (batch 3: DP-13, and three cases other lines
   decide, in `test_w1_46_experiment_folder.py`).
9. A missing `held-out.yaml` launches with no held-out rule (DEC-242, DEC-223): the built settings differ from the
   same launch with the file by exactly the held-out `Read` rule. A file that exists and is empty is a broken file
   and refuses (DEC-218), as the guard reads it.
10. "Inside its experiment folder" (DEC-240): the hook input's `cwd` is the folder or below it, or the command starts
    with `cd <folder> &&`. `uv --directory` and `uv --project` occur in no test; a reviewer probes them (DEC-136).
11. "A ticket of another role" (DEC-242) is tested where the ticket's `role` is a worker role other than the one
    launched and no rule gives that role work on the ticket. The test designer is launched on the engineer's ticket
    it writes tests for (MR-3; this suite was written that way), so that launch must succeed. DP-8 is decided by
    DEC-271: engineer and research only on a ticket of their own role, the two independent roles on any
    `in_progress` ticket.
12. The project allowlist file holds its YAML list of host names under the key `hosts` (DEC-272, on DP-9); a list
    under another key or at the top level refuses, and a project without the file launches on the kernel default.
    Malformed: invalid YAML, a word where the list is, an entry that is a number, a mapping, empty, a URL, or `*`.
13. The role file may be `template/governance/kernel/roles/research*` or `.claude/agents/research.md`; one of them
    states all six parts, found by their words. The roster entry is any key or value `research` in
    `governance/project/roster.yaml`.
14. `product-spec` is not a worker role of the launcher: its experiments run as `research` (KPI success 2).
15. The launcher is not expected to check the CLI binary (digest, signature); the stand-in would not pass one.
16. Not tested, being residuals for EXP-002: subagents in a sandboxed session, what `bypassPermissions` does inside
    the sandbox (the launcher refuses it, DEC-313), hard-link and symlink tricks beyond the `ln` cases of DEC-311,
    `denyWrite` on a path that does not exist, and a new name created under `.gov-runtime/` at the OS level after
    launch (DEC-311: a residual in `bootstrap.md`).

## W1-07's registry test

`tests/acceptance/W1-07/test_w1_07_registry.py` has no `NOT_IMPLEMENTED` case for `launch`: `RESERVED_COMMANDS` holds
the twelve operations and `launch` is not one. Checked again in batch 2; nothing was revised, so no "planned: command
implemented" revision (DEC-190) is recorded. No earlier suite was changed.

## Decision packages

### Batch 1: all seven decided

| Package | Decided by | Decision | In the suite |
|---|---|---|---|
| DP-1, the command line | DEC-231 | `gov launch <role> <ticket> [-- <CLI arguments>]` | used as written; nothing changed |
| DP-2, real sessions | DEC-232 | two short real sessions, `local_only`, no opt-in variable | nothing changed |
| DP-3, a sandbox block in the repository's settings | DEC-233 | refuse | the test became a refusal test; two cases added |
| DP-4, inside the experiment folder | DEC-240 | `cwd` in the folder, or `cd` into it first; `--directory` and `--project` not followed | their 14 cases removed; one `cd` denial added |
| DP-5, the owner-extensible allowlist | DEC-241 | `governance/project/research-allowlist.yaml` extends the kernel default; eighteen starting entries | `test_w1_46_research_allowlist.py`; 18 live host tests |
| DP-6, the temp directory | DEC-234 | the assertion stays | nothing changed |
| DP-7, open cases | DEC-242 | refuse an unknown ticket, one not `in_progress`, one of another role, a research ticket that is not one folder; a missing `held-out.yaml` launches | `test_w1_46_launch_refusals.py`; two held-out tests |

### Batch 4: the packages of batches 2 and 3 are decided; two new ones

| Package | Decided by | Decision | In the suite |
|---|---|---|---|
| DP-8, tickets per role | DEC-271 (delegated) | engineer and research on a ticket of their own role; test designer and auditor on any `in_progress` ticket | 11 cases added |
| DP-9, the allowlist's key | DEC-272 (delegated) | the key is `hosts`; no file means no extension | 4 cases added |
| DP-10, bypass and added directories | DEC-313 (owner) | refuse the four arguments and the two settings keys | 28 cases added |
| DP-11, who wires the guard | DEC-314 (owner) | refuse; the launcher registers no hook | 9 rewritten, 6 added |
| DP-12, the three trees | DEC-315 (owner) | `Edit` deny rules; new success line | 22 cases added, 3 live |
| DP-13, the experiment folder | DEC-273 (delegated) | under a root the project names, `experiments/` by default | 7 cases added |
| DP-14, `.gov-runtime/` and `ln` (the engineer's) | DEC-311 (owner) | literal rules for the names at launch; `ln` judged by the guard | 44 cases added, 2 live rewritten |
| DP-15, the host that does not resolve | DEC-316 (owner) | dropped | 1 added, 1 rewritten, 1 live case removed |
| W1-25 DP-1, the registry | DEC-317 (owner) | each command's handler, arguments, act paths and exit codes from its own module | 6 cases added; W1-07 re-run |

**DP-17 (P3). The exit code of `gov launch` when the session it started ends with a code of its own.**
- Question: does `gov launch` end with the worker session's exit code, whatever it is?
- Why now: DEC-317 asks that a command-defined exit code beyond 0 and 1 ends the process. `gov launch` is the one
  command of today's `gov` with such a code: as built it returns the CLI's exit code. No decision says so, and
  API-0002 gives 1 to a governance error, 2 to a usage error, 3 to "verification failed" and 4 to "blocked by
  control state": a session that ends with 1 to 4 reads as one of those.
- Options: (a) as built: the session's exit code is `gov launch`'s; (b) `gov launch` ends with 0 when it started
  the session and reports the session's code in its output; (c) the session's code, except that 1 to 4 are mapped
  to a code outside API-0002's range.
- Impact: `test_gov_launch_ends_with_the_exit_code_of_the_session_it_started` (3 cases: 3, 4, 42) asserts (a). Under
  (b) or (c) those cases are revised; the three other cases of the file hold under every option.
- Reversibility: high. Cost: a few lines and three cases.
- Recommendation: (a); a ticket lead needs the worker's own exit code, and a refusal is told apart by its message
  and by nothing having started. Confidence: medium.

**DP-18 (P3). How a project names another root for its experiment folders.**
- Question: where does a project name the root of DEC-273, when it is not `experiments/`?
- Why now: DEC-273 says "a root the project names, `experiments/` by default" and names no file or key. The suite
  tests the default only.
- Options: (a) no other root in Wave 1: `experiments/` is fixed; (b) a key in a project file the engineer chooses,
  with one test once it is named; (c) a key the owner names now.
- Impact: (a) nothing changes. (b) and (c): two cases (a folder under the named root launches; one under
  `experiments/` then does not, or still does, as decided).
- Reversibility: high. Cost: two cases.
- Recommendation: (a) for Wave 1. Confidence: medium.

### Batch 5: two new packages, decided in batch 6 (DEC-334)

| Package | Decided by | Decision | In the suite |
|---|---|---|---|
| DP-19, a hard link to a protected file | DEC-334 (delegated, stricter-only) | option (a): the guard refuses `ln` without `-s`, `link` and `cp -l` when the source is a file the role may not write | 7 cases added (4 refusals, 3 controls) |
| DP-20, `mv --target-directory` and `install` | DEC-334 (delegated, stricter-only) | option (a): their destination is a write target, as for `mv -t` and `cp -t` | 8 cases added (6 refusals, 2 controls) |

Batch 6 opened no package. DP-17 and DP-18 are decided by DEC-332 and DEC-333, as built; nothing changed in the suite.

Batch 7 opened no package: MR-3, DEC-334 and DEC-311 decide the described behaviour and its `ln` form.

**DP-19 (P2). A hard link to a protected file, made by one call, and a write through it by a later call.**
- Question: does the guard refuse an engineer's hard link whose source is a file the role may not write (an
  acceptance test, a ticket, a name under `.gov-runtime/` outside `scratch/`), or the later write through such a
  link, or neither?
- Why now: today the guard allows `ln <acceptance test> <name in the engineer's paths>`, and with that link on disk
  it allows `echo x > <that name>`: the acceptance test changes. The review's brief assumed the second call is
  refused; it is for a symbolic link, not for a hard link. DEC-311 makes only the destination of `ln` a write
  target. DEC-135 asks to fix what lets an implementer change acceptance tests. Reading 16 and `bootstrap.md` list
  hard-link tricks as residuals for EXP-002. The three do not agree, so no test was written.
- Options: (a) the guard refuses a hard link whose source the role may not write (one check at `ln`; it also
  closes the one-command case); (b) the guard refuses a write to a name whose file has another name in a protected
  tree (a link count and an inode search at every write); (c) a residual: the post-command containment check
  restores an acceptance test (DEC-143), and EXP-002 shows whether the sandbox lets such a link be made at all.
- Impact: (a) two or three cases (hard link from an acceptance test, from a ticket, from the findings; the control
  of batch 5 stays). (b) one case, and more guard code. (c) none; for `.gov-runtime/` nothing catches the write
  outside a launched session.
- Reversibility: high. Cost: (a) a few lines in the guard's `ln` rule.
- Recommendation: (a). An engineer has no use for a second name of a file it may not write. Confidence: medium-high.

**DP-20 (P2). `mv` with the target directory in a long option, and `install`.**
- Question: do `mv --target-directory=<dir>`, and `install` in any form, become refusals of the guard in this
  ticket, or residuals?
- Why now: seen while batch 5's red result was taken (not part of the two described behaviours, so not tested).
  For an engineer, with the acceptance-test directory or an acceptance test as the place written: `mv -t <dir>
  <own file>` is refused; `mv --target-directory=<dir> <own file>` is allowed; `install -t <dir> <own file>` and
  `install <own file> <acceptance test>` are allowed: the guard does not judge `install` as a write.
- Options: (a) both in this ticket's round, with the `cp` change: the target-directory option read for `cp`, `mv`
  and `install` in its four spellings, and `install`'s last operand a write target; (b) `mv` only, `install` a
  residual in `bootstrap.md`; (c) both residuals.
- Impact: (a) about five cases (`mv` long option; `install` with the option, with a destination, and a control).
  (b) one or two cases. (c) none. In a launched session the `Edit` deny rules of DEC-315 stop these writes at the
  OS level, and the containment check restores an acceptance test; a session not started by `gov launch` has the
  guard alone.
- Reversibility: high. Cost: a few lines beside the `cp` change.
- Recommendation: (a); DEC-135 names exactly this class of finding, and the option parser is the same one.
  Confidence: medium.

### Batch 2: two packages, decided in batch 4 (DEC-271, DEC-272)

**DP-8 (P2). "A ticket of another role" for the test designer and the auditor.**
- Question: on which tickets may `independent-test-designer` and `independent-auditor` be launched?
- Why now: DEC-242 refuses "a ticket of another role", but a test designer always works on a ticket whose `role` is
  another one (this session: `GOV_TICKET=DAEO-jdqr`, a ticket with `role: engineer`). A launcher that compares the two
  role names would refuse every test designer.
- Options: (a) engineer and research need a ticket of their own role; the test designer and the auditor may be
  launched on any `in_progress` ticket; (b) as (a), but the auditor only on a ticket whose `role` is
  `independent-auditor` (DEC-088's audit ticket); (c) as (a), but the two independent roles not on a research ticket.
- Impact: the suite fixes only what every option shares: the test designer launches on an engineer's ticket, the
  auditor on an auditor's ticket, and three refusals (research on an engineer's ticket, engineer on a research
  ticket, engineer on an auditor's ticket). The decided option adds two or three cases.
- Reversibility: high. Cost: a few lines and cases.
- Recommendation: (a); a FULL ticket's reviewer and its test designer both work on the implementation ticket.
  Confidence: medium.

**DP-9 (P3). The shape of `research-allowlist.yaml`, and a project without it.**
- Question: which key holds the list, and does a project with no such file launch a research session on the kernel
  default alone?
- Why now: DEC-241 names the file and its hosts, not its key; the tests change "the list the file holds" and require
  the file in this repository, and leave the missing file untested.
- Options: (a) a top-level key chosen by the engineer, entries as plain host names, and a missing file means no
  extension (as DEC-242 decided for `held-out.yaml`); (b) a fixed key, for example `allowed_domains`, and a missing
  file refuses.
- Impact: under (a) nothing changes but one added test (a missing file launches with the kernel default). Under (b)
  the helper `rewrite_allowlist` names the key and one refusal test is added.
- Reversibility: high. Cost: one test.
- Recommendation: (a). Confidence: medium.

### Batch 3: four packages, decided in batch 4 (DEC-313, DEC-314, DEC-315, DEC-273)

**DP-10 (P1). Permission bypass and added directories, as arguments and as repository settings.**
- Question: does `gov launch` refuse `--dangerously-skip-permissions`, `--allow-dangerously-skip-permissions`,
  `--permission-mode bypassPermissions` and `--add-dir` after `--`, and a repository whose `.claude/settings.json`
  or `.claude/settings.local.json` carries `permissions.defaultMode: bypassPermissions` or
  `permissions.additionalDirectories`?
- Why now: the review reports that such a session keeps the sandbox but loses the permission checks, or gains
  writable directories. The specification does not settle it: Contract item CAP-61.f lists "`bypassPermissions`
  mode" among the sandbox cases that stay open residuals until EXP-002, and no line says whether the sandbox lets
  Bash write to an added directory. KPI success 8 ("a Bash write outside the repository ... fails at the OS level,
  and a file-tool write outside it is refused by the permission rules and the guard") is at stake if it does.
- Options: (a) refuse all of them, as DEC-233 refuses a `sandbox` key; (b) refuse `--add-dir` and
  `additionalDirectories` only, and leave the bypass mode to EXP-002; (c) refuse nothing and record both as
  residuals.
- Impact: (a) about eight refusal cases (six argument spellings, two settings keys), no change to the tests that
  exist; a ticket lead can no longer start a worker in bypass mode, which DEC-183 does not use (`acceptEdits`).
  (b) four cases. (c) none.
- Reversibility: high; a refusal is lifted by removing a check. Cost: a few lines in the launcher, four to eight
  cases.
- Recommendation: (a). It fails closed, and the residual of CAP-61.f stays an experiment question instead of a
  running risk. Confidence: medium-high.

**DP-11 (P1). Who wires the guard into a launched session.**
- Question: when the project's settings do not register the guard (no `.claude/settings.json`, no PreToolUse
  command, `disableAllHooks: true`, or `--setting-sources` without `project`), does the launcher refuse, or does it
  register the guard itself in the settings it builds?
- Why now: today such a launch succeeds and the session has no guard. KPI success 2 says both variables "reach
  the guard", but no line says whose job the wiring is. DEC-233 answers the same question for the sandbox only.
- Options: (a) refuse, non-zero exit and a named reason, as DEC-233; (b) the launcher puts the PreToolUse and
  post-command hooks in its `--settings` value, with `disableAllHooks: false`, and the repository's hooks no longer
  matter for a worker; (c) both: wire them, and refuse what cannot be overridden.
- Impact: batch 3's twelve tests accept (a) and (b). Under (a) they can be tightened to a plain refusal. Under (b)
  the guard runs twice in a wired project unless the launcher checks first, and a live test must show that
  `--settings` wins over `disableAllHooks: true` in the local settings.
- Reversibility: high. Cost: (a) about ten lines; (b) more, and one more live assertion.
- Recommendation: (a). Confidence: medium-high.

**DP-12 (P1). `Edit` deny rules for acceptance tests, tickets and `.claude` in launched worker sessions.**
- Question: do the settings built for a worker role carry `Edit` deny rules for `tests/acceptance/**` (every role
  but the test designer), `.tickets/**` and `.claude/**` (every worker role)?
- Why now: the review reports that in a launched engineer session an opaque Bash write (interpreter one-liner,
  `sh -c`, here-string) to those paths lands: the guard cannot parse it and the working directory is writable in
  the sandbox. No line of the ticket asks for such rules: "the role's Edit deny rules" (success 2) are, by the
  other lines, `.gov-runtime/**` (DEC-180) and the research fence. MR-3 and CAP-58 give an opaque write to an
  acceptance test to the post-command containment check, which restores it (DEC-143). The gap is a file git
  ignores, such as `.claude/settings.local.json`: the containment check does not see it, and it can switch the
  hooks off for the next session. So this is a specification gap, not a missing test, and nothing was added.
- Options: (a) all three rules, as DEC-180 did for `.gov-runtime/**`, with a new KPI line; a ticket whose
  `allowed_paths` names a path under `.claude/` (this ticket names `.claude/agents/research.md`) needs that path
  left out of the rule; (b) `.claude/**` only, the one place the containment check cannot see, and the rest stays
  with the containment check; (c) no rule; record the residual, and rely on DP-11 (a) to refuse the next launch.
- Impact: (a) one KPI line, about twelve cases (three paths, four roles) and three live assertions in the engineer
  session; the research role already has these rules through its fence. (b) one line, four cases, one live
  assertion. (c) none.
- Reversibility: high. Cost: (a) about fifteen lines in the launcher.
- Recommendation: (a). DEC-135 asks to fix what could let an implementer change acceptance tests, and one `Edit`
  rule binds the file tools and Bash at OS level (CAP-58.d). Confidence: medium.

**DP-13 (P2). What makes a directory an experiment folder.**
- Question: which directory may be the one folder of a research ticket's `allowed_paths` (DEC-242)?
- Why now: a research ticket whose single entry is `.claude/**`, `.tickets/**`, `governance/project/**`, `src/**`
  or `.git/**` launches, and the research role may then write and install there. DEC-242 says "exactly one
  experiment folder" and nothing says where one may be. Batch 3 tests only what other lines decide:
  `tests/acceptance/**` (MR-3), `.gov-runtime/**` (DEC-180), and an entry with `..`.
- Options: (a) a folder under a root the project names, `experiments/**` by default; everything else refuses;
  (b) any directory except a protected list: `.git`, `.claude`, `.tickets`, `.gov-runtime`, `governance`, `src`,
  `template`, `tests`, `docs`, and anything above or around them; (c) as today, with the owner's review of the
  ticket as the control.
- Impact: (a) five to seven refusal cases and one control; the fixture's folder, `experiments/spikes/exp-901`,
  already fits. (b) the same cases, and a list to maintain. (c) none. Under (a) and (b) an entry with `..` is
  best refused outright; the test accepts that.
- Reversibility: high. Cost: a few lines in the launcher and the guard's folder check.
- Recommendation: (a). Experiments "run outside production paths" (DEC-102), and one root is simpler to check
  than a list. Confidence: medium.
