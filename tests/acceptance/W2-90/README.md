# W2-90 (DAEO-8lmb): the 235 live-wiring tests judge the kernel's wiring

Test revision under the owner's named decision (DEC-906, given in DEC-957: ACT 1 option (a)); profile LITE; every
revised file's commit carries `Rewrite-Reason: DEC-953 item 2`.

ACT 1 (`6c36c7b5c7fa`, DEC-953 item 2, DEC-954) switched this repository's own pre-tool hook to a five-rule hook
(`.claude/hooks/pretooluse.py`) and removed its containment hooks (PostToolUse, PostToolUseFailure). The kernel's guard
and containment check stay in the product: `template/` and `src/gov/guard/`. 235 cases in 19 files asserted that this
repository's live wiring runs them. Each now asserts the same behaviour, with the same verdict, of the kernel's
wiring. Seven could not be moved: they are left exactly as they stood (see "Cases not moved").

## How the kernel's wiring is reached

`w2_90_kernel_wiring.py` (this folder):

- **A generated project.** `copier.yml` and `template/` are assembled file by file into a temporary template source
  (W1-39's `assemble_source`; this repository is never Copier's source or destination). `copier copy --defaults
  --trust` creates a project from it (W1-39's `create_project_and_run`). `rulesync generate` then writes the project's
  `.claude/` from the project's `.rulesync/` (W1-38's `run_rulesync_generate`): the adapter generation step of the
  template's own update procedure. Generation costs about 4 s (Copier 3.0 s, rulesync 0.6 s, measured). It is done once
  per session or module (a scoped fixture), and the cases work on copies of that temporary folder.
- **The settings.** The project's `.claude/settings.json` is what a product of the kernel runs with: the seven hook
  lines of `template/.rulesync/hooks.jsonc` and the four deny rules of `template/.rulesync/permissions.jsonc`
  (`Bash(npm install*)`, `Bash(pip install*)`, `Bash(sudo *)`, `Edit(.tickets/**)`). The hook programs are at
  `governance/kernel/hooks/`, where Copier puts them.
- **The hook line runs as Claude Code runs it**, through the suites' own runners unchanged (W1-05's `pre_tool_use`,
  `post_bash` and `bash_call`, and W1-46's `ask_guard`): `sh -c <registered line>`, the event's JSON on standard input,
  `CLAUDE_PROJECT_DIR` set to the generated project, and the settings' `permissions.deny` before any hook. The kernel's
  line starts its program with the `python3` first on `PATH`, and a product has `gov` installed. Nothing is installed
  by a test: `install_gov_for(home)` writes a path file naming this worktree's `src` into the stand-in home's user site
  folder, as an editable install does (W1-38's `make_session_sandbox` does the same).
- **Fixture files.** Each suite plants what its cases name, and commits it:
  - W1-05 and W1-47: the fixture ticket `DAEO-zz90`, `README.md`, `src/gov/guard/decide.py`,
    `tests/acceptance/W1-02/README.md`.
  - W1-46, W1-28 and W1-50: W1-46's launch fixture project, built on the generated project with everything W1-46's
    `make_project` copies. The exceptions are this repository's `.claude/settings.json` and `.claude/agents/`; those are
    the generated project's. W1-28 adds its roster entry.
- **Moved cases** take `kernel_*` fixtures and name them by their old names in their first line. Their bodies,
  parameters and assertions are unchanged. The old fixtures stay as they were, for the cases outside the 235 and the
  seven not moved.

## Per file: what it now reads, and how it runs the hook line

| File | Reads | Runs |
|---|---|---|
| W1-05/test_w1_05_live_hooks.py | the generated project's `.claude/settings.json` (`kernel_settings`, `kernel_switched_over`); the history of the template's shipped `template/governance/kernel/settings.json` for the history case | the PreToolUse, PostToolUse and PostToolUseFailure lines those settings register, in a copy of the generated project (`kernel_live`, `kernel_scratch_copy`, `kernel_decide`) |
| W1-05/test_w1_05_role_subagents.py | the generated project's `.claude/agents/` (rulesync's output of the template's subagent sources) and settings | the PreToolUse line, with the definition's `name` as `agent_type` |
| W1-28/test_w1_28_launch_product_spec.py | W1-28's launch project on a generated project (`kernel_launch_base`) | `gov launch product-spec`, then the generated PreToolUse line with the identity the launcher gave |
| W1-46/test_w1_46_hard_links_mv_and_install.py | W1-46's launch project on a generated project (`kernel_project`) | the generated settings' deny rules, then their PreToolUse line (`kernel_guard`) |
| W1-46/test_w1_46_install_spellings.py | the same | the same |
| W1-46/test_w1_46_links_and_cp_targets.py | the same | the same |
| W1-46/test_w1_46_live_sessions.py | the same project (`kernel_launcher`) | a real session through `gov launch`: Claude Code itself runs the generated lines |
| W1-46/test_w1_46_options_after_the_destination.py | the same | `kernel_guard` |
| W1-46/test_w1_46_research_installs.py | the same | `kernel_guard` (the `npm-install` id stays on this repository's settings, not moved) |
| W1-46/test_w1_46_research_role.py | the same | `kernel_guard` |
| W1-46/test_w1_46_role_settings.py | the same | `gov launch` (`kernel_launch`), then `kernel_guard` with the launched identity |
| W1-46/test_w1_46_runtime_and_ln.py | the same | `kernel_guard` |
| W1-47/test_w1_47_failed_commands.py | the generated project's `.claude/settings.json` (`kernel_settings`) | one whole failed Bash call through the generated PreToolUse and PostToolUseFailure lines, in a copy of the generated project |
| W1-49/test_w1_49_registration.py | the `hooks` key of the generated project's `.claude/settings.json` (`kernel_hooks`); the program in the generated form `governance/kernel/hooks/posttooluse.py` | nothing is run (a registration case) |
| W1-50/test_w1_50_freeze_launcher.py | W1-46's launch project on a generated project (`kernel_freeze_launch_base`) | a real session through `gov launch` |
| W1-50/test_w1_50_freeze_live_pause.py | the same | a real session through `gov launch` |
| W2-59/test_w2_59_hook_lines.py | the generated project's `.rulesync/hooks.jsonc` (`kernel_entries`), for the seven-lines case | nothing is run by the moved case; the pin case stays on this repository's lines |
| W2-59/test_w2_59_hook_lines_worker_env.py | not moved: its three ids stay on this repository's lines | unchanged |
| W2-65/test_w2_65_hook_lines.py | the template's `.rulesync/hooks.jsonc` and the generated project's `.rulesync/hooks.jsonc` (`kernel_sources`) | nothing is run (a source case) |

## The ticket's KPI lines

- **Success 1** (each of the 235 passes after ACT 1 and judges the kernel's wiring): 228 are moved to the kernel's
  wiring, as described above. 7 cannot be moved (below). Of the 228, 184 pass in this worktree after ACT 1. Two groups
  could not be shown green here:
  - 38 real-session cases: this sandbox refuses `api.anthropic.com`, so the session ends at `ERR_PROXY_TUNNEL` before
    any tool call. The same happened before the revision.
  - the 9 latency cases (6 in the full run, 9 when run alone), red from machine load (see "Measured, not settled").
- **Success 2** (nothing lowered): no case was deleted, skipped, marked xfail or given a weaker verdict, and no bound
  was changed. Two functions were split by parameter, with every id kept (see "Split functions"). The 7 not moved stand
  unchanged, with the reason and the measurement below.
- **Success 3** (`Rewrite-Reason` on each commit; this map): every commit of W2-90 carries `Rewrite-Reason: DEC-953
  item 2`. The table below maps all 235.
- **Success 4** (green on the head after ACT 1 and on `aafd45c1`): no revised case reads this repository's live
  settings, so the result does not depend on the head. The run on `aafd45c1` is the lead's, on a clean clone.
- **Failure lines**: no moved case reads `.claude/settings.json` or `.rulesync/hooks.jsonc` of this repository. Nothing
  was deleted, skipped or marked xfail. Only the ticket's paths changed, and no code.

## This worktree's code

Every run uses this worktree's `src`:
`PYTHONPATH=/home/usain/gov-os-worktrees/W2-90/src python3 -m pytest <files> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`.
`gov.__file__` is `/home/usain/gov-os-worktrees/W2-90/src/gov/__init__.py`. Inside the cases, the kernel's hook
imports the same `src`, through the path file in the stand-in home. `gov launch` runs the project's copy of it.

## Cases not moved (7), left exactly as they stood

| Case | Why it cannot be moved | Measured of the kernel's wiring |
|---|---|---|
| `W1-05/...::test_an_install_by_the_orchestrator_asks_the_owner[pip install requests]` | The case asks that the owner be asked. Its docstring names exactly what stops that: "the interim deny rules on installs would stop the prompt from ever appearing". `template/.rulesync/permissions.jsonc` generates `Bash(pip install*)` into the product's `permissions.deny`. | `decision=deny (permissions.deny rule Bash(pip install*))` in default mode, where the case expects `ask` |
| `W1-05/...::test_an_install_by_the_orchestrator_asks_the_owner[npm install -g ccusage]` | The same, for `Bash(npm install*)` | `deny` by `Bash(npm install*)`, where `ask` is expected |
| `W1-46/...::test_a_research_install_inside_the_experiment_folder_is_let_through[npm-install]` | W1-46 KPI success 6 asks that the research install "is not denied ... and meets no settings ask rule". The generated `Bash(npm install*)` denies `npm install left-pad` before the hook. | `deny` by `permissions.deny` `Bash(npm install*)`; the other 10 forms are let through (moved, green) |
| `W2-59/test_w2_59_hook_lines.py::test_the_line_s_program_imports_the_pin_s_package_not_the_project_s_src[preToolUse[0]]` | The case asserts the line starts the pin's interpreter and package (DEC-822). The kernel's line `python3 "$h"` carries no pin. | Run through W2-59's own box, with the programs at `governance/kernel/hooks/`: the decoy `python3` first on `PATH` started, the pin's interpreter and package did not |
| `W2-59/test_w2_59_hook_lines_worker_env.py::test_the_guard_line_refuses_what_the_pin_s_guard_refuses_whatever_the_session_s_import_path[preToolUse[0]-worker-pythonpath]` | The same | With the worker's `PYTHONPATH`, the kernel's line imported the project's edited `gov` and let the refused write through (exit 0, no deny) |
| `W2-59/test_w2_59_hook_lines_worker_env.py::test_the_guard_line_refuses_what_the_pin_s_guard_refuses_whatever_the_session_s_import_path[preToolUse[0]-no-pythonpath]` | The same | Exit 2 (refused), but by the decoy `python3`; the pin's package was not imported |
| `W2-59/test_w2_59_hook_lines_worker_env.py::test_a_command_that_sets_pythonpath_itself_is_let_through_and_runs_the_tree_s_code[preToolUse[0]]` | The same | The decision came from the project's own `gov` through the decoy `python3`, not from the pin |

They stay red on the head after ACT 1, for the reason they were red before this revision. On `aafd45c1` they pass, as
before.

## Split functions (every id kept)

Two functions held both ids that could move and ids that could not:

- `test_an_install_by_the_orchestrator_asks_the_owner` (W1-05): keeps its two ids that cannot move, unchanged.
  `curl ... | sh` is asserted by `test_an_install_by_the_orchestrator_asks_the_owner_through_the_kernel_s_wiring`, with
  the same body (it asks, in all three modes).
- `test_a_research_install_inside_the_experiment_folder_is_let_through` (W1-46): keeps `npm-install`, unchanged. The
  other ten forms are asserted by `..._is_let_through_by_the_kernel_s_wiring`, with the same body.

W1-49's `test_the_guard_hooks_stay_registered` lost its two containment parameters to
`test_the_guard_hooks_stay_registered_in_the_kernel_s_wiring`. Its five guard parameters stay on this repository's
settings, where they hold. In all three, the parameters moved are asserted by the new function, so the count of cases
among the 19 files is unchanged: 493 before, 493 after.

## One more case revised: the 236th red of ACT 1

`W1-05/test_w1_05_live_hooks.py::test_the_hooks_stay_wired_in_every_later_commit` is not in the case list, but ACT 1
makes it red:

- through its fixture (`switched_over`);
- and through its own check: on `.claude/settings.json`'s first-parent history, `6c36c7b5c7fa` unwires the hooks.

It passes on `aafd45c1`, measured by replaying its logic. It is revised the same way: its fixture is
`kernel_switched_over`, and the history read is that of the kernel's shipped `template/governance/kernel/settings.json`
(wired since `a440e524d0c7`, never unwired since). Returned to the lead as a package.

## Measured, not settled

- **Latency (9 ids, the bound unchanged at 100 ms p95).** They run on the kernel's line and are red at this machine's
  load:
  - full run, load about 40: 6 of 9 red;
  - alone, load 39 to 42: all 9 at 180 to 470 ms.
  - Interleaved at load 41, in the same generated project: the kernel's line 305 to 364 ms, the base's own live line
    267 to 298 ms. Both miss the bound; the kernel's line is about 15 to 25 % slower (the system `python3` with this
    worktree's `src`, against the pin's `-E` interpreter and its compiled package).
  - To be judged at a quiet moment.
- **Real sessions (38 ids: 36 of W1-46, 2 of W1-50).** They need the CLI and `api.anthropic.com`, which this sandbox
  refuses (`ERR_PROXY_TUNNEL`). Their session environment carries `PYTHONPATH=<project>/src` (`gov launch` passes its
  environment on), which is how the kernel's `python3` line finds `gov` in a launched session. Not run green here.

## The table: each of the 235 ids and its revised case

| # | Case id (as in the case list) | Revised case id | |
|---|---|---|---|
| 1 | `W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Edit-engineer]` | same | moved |
| 2 | `W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Glob-engineer]` | same | moved |
| 3 | `W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Glob-no-role]` | same | moved |
| 4 | `W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Grep-engineer]` | same | moved |
| 5 | `W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Grep-no-role]` | same | moved |
| 6 | `W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[NotebookEdit-engineer]` | same | moved |
| 7 | `W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Read-engineer]` | same | moved |
| 8 | `W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Read-no-role]` | same | moved |
| 9 | `W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook[Write-engineer]` | same | moved |
| 10 | `W1-05/test_w1_05_live_hooks.py::test_a_hook_runs_after_every_bash_call[PostToolUseFailure]` | same | moved |
| 11 | `W1-05/test_w1_05_live_hooks.py::test_a_hook_runs_after_every_bash_call[PostToolUse]` | same | moved |
| 12 | `W1-05/test_w1_05_live_hooks.py::test_a_later_call_of_any_tool_shows_the_actor_s_unfinished_call_is_over[Agent]` | same | moved |
| 13 | `W1-05/test_w1_05_live_hooks.py::test_a_later_call_of_any_tool_shows_the_actor_s_unfinished_call_is_over[Glob]` | same | moved |
| 14 | `W1-05/test_w1_05_live_hooks.py::test_a_later_call_of_any_tool_shows_the_actor_s_unfinished_call_is_over[Grep]` | same | moved |
| 15 | `W1-05/test_w1_05_live_hooks.py::test_a_later_call_of_any_tool_shows_the_actor_s_unfinished_call_is_over[Read]` | same | moved |
| 16 | `W1-05/test_w1_05_live_hooks.py::test_a_later_call_of_any_tool_shows_the_actor_s_unfinished_call_is_over[mcp__github__create_issue]` | same | moved |
| 17 | `W1-05/test_w1_05_live_hooks.py::test_a_read_only_tool_goes_through_the_hook_and_is_allowed[Glob-engineer]` | same | moved |
| 18 | `W1-05/test_w1_05_live_hooks.py::test_a_read_only_tool_goes_through_the_hook_and_is_allowed[Glob-independent-auditor]` | same | moved |
| 19 | `W1-05/test_w1_05_live_hooks.py::test_a_read_only_tool_goes_through_the_hook_and_is_allowed[Glob-independent-test-designer]` | same | moved |
| 20 | `W1-05/test_w1_05_live_hooks.py::test_a_read_only_tool_goes_through_the_hook_and_is_allowed[Glob-no-role]` | same | moved |
| 21 | `W1-05/test_w1_05_live_hooks.py::test_a_read_only_tool_goes_through_the_hook_and_is_allowed[Glob-orchestrator]` | same | moved |
| 22 | `W1-05/test_w1_05_live_hooks.py::test_a_read_only_tool_goes_through_the_hook_and_is_allowed[Glob-product-spec]` | same | moved |
| 23 | `W1-05/test_w1_05_live_hooks.py::test_a_read_only_tool_goes_through_the_hook_and_is_allowed[Grep-engineer]` | same | moved |
| 24 | `W1-05/test_w1_05_live_hooks.py::test_a_read_only_tool_goes_through_the_hook_and_is_allowed[Grep-independent-auditor]` | same | moved |
| 25 | `W1-05/test_w1_05_live_hooks.py::test_a_read_only_tool_goes_through_the_hook_and_is_allowed[Grep-independent-test-designer]` | same | moved |
| 26 | `W1-05/test_w1_05_live_hooks.py::test_a_read_only_tool_goes_through_the_hook_and_is_allowed[Grep-no-role]` | same | moved |
| 27 | `W1-05/test_w1_05_live_hooks.py::test_a_read_only_tool_goes_through_the_hook_and_is_allowed[Grep-orchestrator]` | same | moved |
| 28 | `W1-05/test_w1_05_live_hooks.py::test_a_read_only_tool_goes_through_the_hook_and_is_allowed[Grep-product-spec]` | same | moved |
| 29 | `W1-05/test_w1_05_live_hooks.py::test_a_read_only_tool_goes_through_the_hook_and_is_allowed[Read-engineer]` | same | moved |
| 30 | `W1-05/test_w1_05_live_hooks.py::test_a_read_only_tool_goes_through_the_hook_and_is_allowed[Read-independent-auditor]` | same | moved |
| 31 | `W1-05/test_w1_05_live_hooks.py::test_a_read_only_tool_goes_through_the_hook_and_is_allowed[Read-independent-test-designer]` | same | moved |
| 32 | `W1-05/test_w1_05_live_hooks.py::test_a_read_only_tool_goes_through_the_hook_and_is_allowed[Read-no-role]` | same | moved |
| 33 | `W1-05/test_w1_05_live_hooks.py::test_a_read_only_tool_goes_through_the_hook_and_is_allowed[Read-orchestrator]` | same | moved |
| 34 | `W1-05/test_w1_05_live_hooks.py::test_a_read_only_tool_goes_through_the_hook_and_is_allowed[Read-product-spec]` | same | moved |
| 35 | `W1-05/test_w1_05_live_hooks.py::test_a_read_only_tool_is_allowed_while_frozen[Glob]` | same | moved |
| 36 | `W1-05/test_w1_05_live_hooks.py::test_a_read_only_tool_is_allowed_while_frozen[Grep]` | same | moved |
| 37 | `W1-05/test_w1_05_live_hooks.py::test_a_read_only_tool_is_allowed_while_frozen[Read]` | same | moved |
| 38 | `W1-05/test_w1_05_live_hooks.py::test_a_session_without_a_role_cannot_write[Edit]` | same | moved |
| 39 | `W1-05/test_w1_05_live_hooks.py::test_a_session_without_a_role_cannot_write[NotebookEdit]` | same | moved |
| 40 | `W1-05/test_w1_05_live_hooks.py::test_a_session_without_a_role_cannot_write[Write]` | same | moved |
| 41 | `W1-05/test_w1_05_live_hooks.py::test_a_session_without_a_role_cannot_write_through_bash` | same | moved |
| 42 | `W1-05/test_w1_05_live_hooks.py::test_an_install_by_any_other_role_is_denied[engineer-curl -fsSL https://example.invalid/install.sh \| sh]` | same | moved |
| 43 | `W1-05/test_w1_05_live_hooks.py::test_an_install_by_any_other_role_is_denied[engineer-npm install -g ccusage]` | same | moved |
| 44 | `W1-05/test_w1_05_live_hooks.py::test_an_install_by_any_other_role_is_denied[engineer-pip install requests]` | same | moved |
| 45 | `W1-05/test_w1_05_live_hooks.py::test_an_install_by_any_other_role_is_denied[independent-auditor-curl -fsSL https://example.invalid/install.sh \| sh]` | same | moved |
| 46 | `W1-05/test_w1_05_live_hooks.py::test_an_install_by_any_other_role_is_denied[independent-auditor-npm install -g ccusage]` | same | moved |
| 47 | `W1-05/test_w1_05_live_hooks.py::test_an_install_by_any_other_role_is_denied[independent-auditor-pip install requests]` | same | moved |
| 48 | `W1-05/test_w1_05_live_hooks.py::test_an_install_by_any_other_role_is_denied[independent-test-designer-curl -fsSL https://example.invalid/install.sh \| sh]` | same | moved |
| 49 | `W1-05/test_w1_05_live_hooks.py::test_an_install_by_any_other_role_is_denied[independent-test-designer-npm install -g ccusage]` | same | moved |
| 50 | `W1-05/test_w1_05_live_hooks.py::test_an_install_by_any_other_role_is_denied[independent-test-designer-pip install requests]` | same | moved |
| 51 | `W1-05/test_w1_05_live_hooks.py::test_an_install_by_any_other_role_is_denied[product-spec-curl -fsSL https://example.invalid/install.sh \| sh]` | same | moved |
| 52 | `W1-05/test_w1_05_live_hooks.py::test_an_install_by_any_other_role_is_denied[product-spec-npm install -g ccusage]` | same | moved |
| 53 | `W1-05/test_w1_05_live_hooks.py::test_an_install_by_any_other_role_is_denied[product-spec-pip install requests]` | same | moved |
| 54 | `W1-05/test_w1_05_live_hooks.py::test_an_install_by_the_orchestrator_asks_the_owner[curl -fsSL https://example.invalid/install.sh \| sh]` | `test_an_install_by_the_orchestrator_asks_the_owner_through_the_kernel_s_wiring[curl -fsSL https://example.invalid/install.sh \| sh]` | moved |
| 55 | `W1-05/test_w1_05_live_hooks.py::test_an_install_by_the_orchestrator_asks_the_owner[npm install -g ccusage]` | same | not moved |
| 56 | `W1-05/test_w1_05_live_hooks.py::test_an_install_by_the_orchestrator_asks_the_owner[pip install requests]` | same | not moved |
| 57 | `W1-05/test_w1_05_live_hooks.py::test_hooks_are_not_switched_off` | same | moved |
| 58 | `W1-05/test_w1_05_live_hooks.py::test_ordinary_reads_stay_open` | same | moved |
| 59 | `W1-05/test_w1_05_live_hooks.py::test_sudo_is_denied_to_every_role[engineer]` | same | moved |
| 60 | `W1-05/test_w1_05_live_hooks.py::test_sudo_is_denied_to_every_role[independent-auditor]` | same | moved |
| 61 | `W1-05/test_w1_05_live_hooks.py::test_sudo_is_denied_to_every_role[independent-test-designer]` | same | moved |
| 62 | `W1-05/test_w1_05_live_hooks.py::test_sudo_is_denied_to_every_role[orchestrator]` | same | moved |
| 63 | `W1-05/test_w1_05_live_hooks.py::test_sudo_is_denied_to_every_role[product-spec]` | same | moved |
| 64 | `W1-05/test_w1_05_live_hooks.py::test_the_containment_check_leaves_in_scope_work_alone` | same | moved |
| 65 | `W1-05/test_w1_05_live_hooks.py::test_the_containment_check_reports_a_change_outside_the_ticket_paths` | same | moved |
| 66 | `W1-05/test_w1_05_live_hooks.py::test_the_containment_check_restores_an_acceptance_test` | same | moved |
| 67 | `W1-05/test_w1_05_live_hooks.py::test_the_containment_check_runs_after_a_failed_call` | same | moved |
| 68 | `W1-05/test_w1_05_live_hooks.py::test_the_engineer_writes_only_inside_the_ticket_paths` | same | moved |
| 69 | `W1-05/test_w1_05_live_hooks.py::test_the_freeze_flag_stops_every_write` | same | moved |
| 70 | `W1-05/test_w1_05_live_hooks.py::test_the_test_designer_writes_only_acceptance_tests` | same | moved |
| 71 | `W1-05/test_w1_05_live_hooks.py::test_without_a_later_call_the_unfinished_call_still_blocks_the_restore` | same | moved |
| 72 | `W1-05/test_w1_05_role_subagents.py::test_the_engineer_subagent_can_work_on_an_engineer_ticket` | same | moved |
| 73 | `W1-05/test_w1_05_role_subagents.py::test_the_live_guard_takes_the_definition_s_type_name_as_the_role[engineer]` | same | moved |
| 74 | `W1-05/test_w1_05_role_subagents.py::test_the_live_guard_takes_the_definition_s_type_name_as_the_role[independent-auditor]` | same | moved |
| 75 | `W1-05/test_w1_05_role_subagents.py::test_the_live_guard_takes_the_definition_s_type_name_as_the_role[independent-test-designer]` | same | moved |
| 76 | `W1-05/test_w1_05_role_subagents.py::test_the_live_guard_takes_the_definition_s_type_name_as_the_role[orchestrator]` | same | moved |
| 77 | `W1-05/test_w1_05_role_subagents.py::test_the_live_guard_takes_the_definition_s_type_name_as_the_role[product-spec]` | same | moved |
| 78 | `W1-28/test_w1_28_launch_product_spec.py::test_the_guard_decides_by_the_identity_the_launcher_gave[Edit]` | same | moved |
| 79 | `W1-28/test_w1_28_launch_product_spec.py::test_the_guard_decides_by_the_identity_the_launcher_gave[Write]` | same | moved |
| 80 | `W1-46/test_w1_46_hard_links_mv_and_install.py::test_the_guard_does_not_refuse_a_hard_link_between_two_names_inside_the_roles_paths[cp -l]` | same | moved |
| 81 | `W1-46/test_w1_46_hard_links_mv_and_install.py::test_the_guard_does_not_refuse_a_hard_link_between_two_names_inside_the_roles_paths[link]` | same | moved |
| 82 | `W1-46/test_w1_46_hard_links_mv_and_install.py::test_the_guard_does_not_refuse_install_to_a_destination_inside_the_roles_paths` | same | moved |
| 83 | `W1-46/test_w1_46_hard_links_mv_and_install.py::test_the_guard_does_not_refuse_mv_with_a_target_directory_inside_the_roles_paths` | same | moved |
| 84 | `W1-46/test_w1_46_hard_links_mv_and_install.py::test_the_test_designer_may_hard_link_one_acceptance_test_to_another_name_there` | same | moved |
| 85 | `W1-46/test_w1_46_install_spellings.py::test_a_uv_run_whose_script_argument_starts_with_w_is_no_install` | same | moved |
| 86 | `W1-46/test_w1_46_install_spellings.py::test_the_orchestrator_is_asked_about_uv_run_w_with_its_value_joined` | same | moved |
| 87 | `W1-46/test_w1_46_install_spellings.py::test_uv_run_w_with_its_value_joined_is_denied_to_research_outside_its_folder` | same | moved |
| 88 | `W1-46/test_w1_46_install_spellings.py::test_uv_run_w_with_its_value_joined_is_let_through_for_research_in_its_folder` | same | moved |
| 89 | `W1-46/test_w1_46_install_spellings.py::test_uv_run_w_with_its_value_joined_stays_denied_for_the_other_worker_roles[engineer]` | same | moved |
| 90 | `W1-46/test_w1_46_install_spellings.py::test_uv_run_w_with_its_value_joined_stays_denied_for_the_other_worker_roles[independent-auditor]` | same | moved |
| 91 | `W1-46/test_w1_46_install_spellings.py::test_uv_run_w_with_its_value_joined_stays_denied_for_the_other_worker_roles[independent-test-designer]` | same | moved |
| 92 | `W1-46/test_w1_46_links_and_cp_targets.py::test_cp_with_the_destination_as_the_last_operand_is_judged_as_before` | same | moved |
| 93 | `W1-46/test_w1_46_links_and_cp_targets.py::test_the_guard_does_not_refuse_a_link_whose_source_and_destination_are_inside_the_roles_paths[hard]` | same | moved |
| 94 | `W1-46/test_w1_46_links_and_cp_targets.py::test_the_guard_does_not_refuse_a_link_whose_source_and_destination_are_inside_the_roles_paths[symbolic]` | same | moved |
| 95 | `W1-46/test_w1_46_live_sessions.py::test_a_bash_write_under_gov_runtime_fails_and_scratch_stays_writable` | same | moved |
| 96 | `W1-46/test_w1_46_live_sessions.py::test_a_file_tool_write_outside_the_repository_is_refused` | same | moved |
| 97 | `W1-46/test_w1_46_live_sessions.py::test_a_research_bash_write_to_a_sibling_directory_fails` | same | moved |
| 98 | `W1-46/test_w1_46_live_sessions.py::test_a_research_install_outside_the_repository_fails_at_the_write_fence` | same | moved |
| 99 | `W1-46/test_w1_46_live_sessions.py::test_a_research_install_succeeds_into_a_venv_inside_the_experiment_folder` | same | moved |
| 100 | `W1-46/test_w1_46_live_sessions.py::test_a_research_write_to_a_new_path_outside_the_folder_is_refused_or_reported` | same | moved |
| 101 | `W1-46/test_w1_46_live_sessions.py::test_an_opaque_bash_write_outside_the_repository_fails[here-string.txt]` | same | moved |
| 102 | `W1-46/test_w1_46_live_sessions.py::test_an_opaque_bash_write_outside_the_repository_fails[interpreter.txt]` | same | moved |
| 103 | `W1-46/test_w1_46_live_sessions.py::test_an_opaque_bash_write_outside_the_repository_fails[substitution.txt]` | same | moved |
| 104 | `W1-46/test_w1_46_live_sessions.py::test_an_opaque_bash_write_to_the_acceptance_tests_the_tickets_and_dot_claude_fails[a-ticket]` | same | moved |
| 105 | `W1-46/test_w1_46_live_sessions.py::test_an_opaque_bash_write_to_the_acceptance_tests_the_tickets_and_dot_claude_fails[an-acceptance-test]` | same | moved |
| 106 | `W1-46/test_w1_46_live_sessions.py::test_an_opaque_bash_write_to_the_acceptance_tests_the_tickets_and_dot_claude_fails[the-settings]` | same | moved |
| 107 | `W1-46/test_w1_46_live_sessions.py::test_each_session_uses_a_temp_directory_of_its_own` | same | moved |
| 108 | `W1-46/test_w1_46_live_sessions.py::test_ln_into_gov_runtime_fails[hardlink]` | same | moved |
| 109 | `W1-46/test_w1_46_live_sessions.py::test_ln_into_gov_runtime_fails[symlink]` | same | moved |
| 110 | `W1-46/test_w1_46_live_sessions.py::test_the_empty_allowlist_refuses_a_connection` | same | moved |
| 111 | `W1-46/test_w1_46_live_sessions.py::test_the_held_out_directory_looks_empty_from_the_sessions_bash` | same | moved |
| 112 | `W1-46/test_w1_46_live_sessions.py::test_the_research_allowlist_refuses_a_domain_that_is_not_on_it` | same | moved |
| 113 | `W1-46/test_w1_46_live_sessions.py::test_the_role_and_the_ticket_reach_the_session_and_its_hooks` | same | moved |
| 114 | `W1-46/test_w1_46_live_sessions.py::test_the_sandbox_accepts_a_connection_to_a_starting_host_of_the_research_allowlist[api.github.com]` | same | moved |
| 115 | `W1-46/test_w1_46_live_sessions.py::test_the_sandbox_accepts_a_connection_to_a_starting_host_of_the_research_allowlist[arxiv.org]` | same | moved |
| 116 | `W1-46/test_w1_46_live_sessions.py::test_the_sandbox_accepts_a_connection_to_a_starting_host_of_the_research_allowlist[codeload.github.com]` | same | moved |
| 117 | `W1-46/test_w1_46_live_sessions.py::test_the_sandbox_accepts_a_connection_to_a_starting_host_of_the_research_allowlist[crates.io]` | same | moved |
| 118 | `W1-46/test_w1_46_live_sessions.py::test_the_sandbox_accepts_a_connection_to_a_starting_host_of_the_research_allowlist[developer.mozilla.org]` | same | moved |
| 119 | `W1-46/test_w1_46_live_sessions.py::test_the_sandbox_accepts_a_connection_to_a_starting_host_of_the_research_allowlist[docs.python.org]` | same | moved |
| 120 | `W1-46/test_w1_46_live_sessions.py::test_the_sandbox_accepts_a_connection_to_a_starting_host_of_the_research_allowlist[docs.readthedocs.io]` | same | moved |
| 121 | `W1-46/test_w1_46_live_sessions.py::test_the_sandbox_accepts_a_connection_to_a_starting_host_of_the_research_allowlist[docs.rs]` | same | moved |
| 122 | `W1-46/test_w1_46_live_sessions.py::test_the_sandbox_accepts_a_connection_to_a_starting_host_of_the_research_allowlist[export.arxiv.org]` | same | moved |
| 123 | `W1-46/test_w1_46_live_sessions.py::test_the_sandbox_accepts_a_connection_to_a_starting_host_of_the_research_allowlist[files.pythonhosted.org]` | same | moved |
| 124 | `W1-46/test_w1_46_live_sessions.py::test_the_sandbox_accepts_a_connection_to_a_starting_host_of_the_research_allowlist[github.com]` | same | moved |
| 125 | `W1-46/test_w1_46_live_sessions.py::test_the_sandbox_accepts_a_connection_to_a_starting_host_of_the_research_allowlist[huggingface.co]` | same | moved |
| 126 | `W1-46/test_w1_46_live_sessions.py::test_the_sandbox_accepts_a_connection_to_a_starting_host_of_the_research_allowlist[objects.githubusercontent.com]` | same | moved |
| 127 | `W1-46/test_w1_46_live_sessions.py::test_the_sandbox_accepts_a_connection_to_a_starting_host_of_the_research_allowlist[pypi.org]` | same | moved |
| 128 | `W1-46/test_w1_46_live_sessions.py::test_the_sandbox_accepts_a_connection_to_a_starting_host_of_the_research_allowlist[raw.githubusercontent.com]` | same | moved |
| 129 | `W1-46/test_w1_46_live_sessions.py::test_the_sandbox_accepts_a_connection_to_a_starting_host_of_the_research_allowlist[registry.npmjs.org]` | same | moved |
| 130 | `W1-46/test_w1_46_live_sessions.py::test_the_sandbox_accepts_a_connection_to_a_starting_host_of_the_research_allowlist[static.crates.io]` | same | moved |
| 131 | `W1-46/test_w1_46_options_after_the_destination.py::test_the_guard_does_not_refuse_cp_between_two_names_of_the_working_directory_inside_the_roles_paths` | same | moved |
| 132 | `W1-46/test_w1_46_options_after_the_destination.py::test_the_guard_does_not_refuse_install_with_its_option_before_the_operands` | same | moved |
| 133 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_after_cd_into_another_folder_is_denied` | same | moved |
| 134 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_after_cd_into_the_experiment_folder_is_let_through` | same | moved |
| 135 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_below_the_experiment_folder_is_let_through[uv-add]` | same | moved |
| 136 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_below_the_experiment_folder_is_let_through[uv-run-with]` | same | moved |
| 137 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_below_the_experiment_folder_is_let_through[uv-sync]` | same | moved |
| 138 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_below_the_experiment_folder_is_let_through[uvx]` | same | moved |
| 139 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through[cache-dir-sync]` | `test_a_research_install_inside_the_experiment_folder_is_let_through_by_the_kernel_s_wiring[cache-dir-sync]` | moved |
| 140 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through[config-file-add]` | `test_a_research_install_inside_the_experiment_folder_is_let_through_by_the_kernel_s_wiring[config-file-add]` | moved |
| 141 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through[npm-install]` | same | not moved |
| 142 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through[python-m-pip-install]` | `test_a_research_install_inside_the_experiment_folder_is_let_through_by_the_kernel_s_wiring[python-m-pip-install]` | moved |
| 143 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through[run-w]` | `test_a_research_install_inside_the_experiment_folder_is_let_through_by_the_kernel_s_wiring[run-w]` | moved |
| 144 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through[uv-add]` | `test_a_research_install_inside_the_experiment_folder_is_let_through_by_the_kernel_s_wiring[uv-add]` | moved |
| 145 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through[uv-pip-install]` | `test_a_research_install_inside_the_experiment_folder_is_let_through_by_the_kernel_s_wiring[uv-pip-install]` | moved |
| 146 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through[uv-run-with]` | `test_a_research_install_inside_the_experiment_folder_is_let_through_by_the_kernel_s_wiring[uv-run-with]` | moved |
| 147 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through[uv-sync]` | `test_a_research_install_inside_the_experiment_folder_is_let_through_by_the_kernel_s_wiring[uv-sync]` | moved |
| 148 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through[uvx]` | `test_a_research_install_inside_the_experiment_folder_is_let_through_by_the_kernel_s_wiring[uvx]` | moved |
| 149 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through[venv-pip-install]` | `test_a_research_install_inside_the_experiment_folder_is_let_through_by_the_kernel_s_wiring[venv-pip-install]` | moved |
| 150 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_on_another_roles_ticket_is_denied` | same | moved |
| 151 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[cache-dir-sync-repository-root]` | same | moved |
| 152 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[cache-dir-sync-sibling-experiment]` | same | moved |
| 153 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[cache-dir-sync-source-tree]` | same | moved |
| 154 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[config-file-add-repository-root]` | same | moved |
| 155 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[config-file-add-sibling-experiment]` | same | moved |
| 156 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[config-file-add-source-tree]` | same | moved |
| 157 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[run-w-repository-root]` | same | moved |
| 158 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[run-w-sibling-experiment]` | same | moved |
| 159 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[run-w-source-tree]` | same | moved |
| 160 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[uv-add-repository-root]` | same | moved |
| 161 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[uv-add-sibling-experiment]` | same | moved |
| 162 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[uv-add-source-tree]` | same | moved |
| 163 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[uv-run-with-repository-root]` | same | moved |
| 164 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[uv-run-with-sibling-experiment]` | same | moved |
| 165 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[uv-run-with-source-tree]` | same | moved |
| 166 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[uv-sync-repository-root]` | same | moved |
| 167 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[uv-sync-sibling-experiment]` | same | moved |
| 168 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[uv-sync-source-tree]` | same | moved |
| 169 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[uvx-repository-root]` | same | moved |
| 170 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[uvx-sibling-experiment]` | same | moved |
| 171 | `W1-46/test_w1_46_research_installs.py::test_a_research_install_outside_the_experiment_folder_is_denied[uvx-source-tree]` | same | moved |
| 172 | `W1-46/test_w1_46_research_installs.py::test_another_role_on_the_research_ticket_gets_no_install_through[engineer]` | same | moved |
| 173 | `W1-46/test_w1_46_research_installs.py::test_another_role_on_the_research_ticket_gets_no_install_through[independent-auditor]` | same | moved |
| 174 | `W1-46/test_w1_46_research_installs.py::test_another_role_on_the_research_ticket_gets_no_install_through[independent-test-designer]` | same | moved |
| 175 | `W1-46/test_w1_46_research_installs.py::test_no_permission_mode_turns_the_research_install_into_a_prompt[acceptEdits]` | same | moved |
| 176 | `W1-46/test_w1_46_research_installs.py::test_no_permission_mode_turns_the_research_install_into_a_prompt[auto]` | same | moved |
| 177 | `W1-46/test_w1_46_research_installs.py::test_no_permission_mode_turns_the_research_install_into_a_prompt[bypassPermissions]` | same | moved |
| 178 | `W1-46/test_w1_46_research_installs.py::test_no_permission_mode_turns_the_research_install_into_a_prompt[default]` | same | moved |
| 179 | `W1-46/test_w1_46_research_installs.py::test_no_permission_mode_turns_the_research_install_into_a_prompt[dontAsk]` | same | moved |
| 180 | `W1-46/test_w1_46_research_installs.py::test_no_permission_mode_turns_the_research_install_into_a_prompt[plan]` | same | moved |
| 181 | `W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[cache-dir-sync-engineer]` | same | moved |
| 182 | `W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[cache-dir-sync-independent-auditor]` | same | moved |
| 183 | `W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[cache-dir-sync-independent-test-designer]` | same | moved |
| 184 | `W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[config-file-add-engineer]` | same | moved |
| 185 | `W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[config-file-add-independent-auditor]` | same | moved |
| 186 | `W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[config-file-add-independent-test-designer]` | same | moved |
| 187 | `W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[run-w-engineer]` | same | moved |
| 188 | `W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[run-w-independent-auditor]` | same | moved |
| 189 | `W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[run-w-independent-test-designer]` | same | moved |
| 190 | `W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[uv-add-engineer]` | same | moved |
| 191 | `W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[uv-add-independent-auditor]` | same | moved |
| 192 | `W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[uv-add-independent-test-designer]` | same | moved |
| 193 | `W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[uv-run-with-engineer]` | same | moved |
| 194 | `W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[uv-run-with-independent-auditor]` | same | moved |
| 195 | `W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[uv-run-with-independent-test-designer]` | same | moved |
| 196 | `W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[uv-sync-engineer]` | same | moved |
| 197 | `W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[uv-sync-independent-auditor]` | same | moved |
| 198 | `W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[uv-sync-independent-test-designer]` | same | moved |
| 199 | `W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[uvx-engineer]` | same | moved |
| 200 | `W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[uvx-independent-auditor]` | same | moved |
| 201 | `W1-46/test_w1_46_research_installs.py::test_the_same_commands_stay_denied_for_the_other_worker_roles[uvx-independent-test-designer]` | same | moved |
| 202 | `W1-46/test_w1_46_research_role.py::test_a_research_session_may_use_scratch` | same | moved |
| 203 | `W1-46/test_w1_46_research_role.py::test_a_research_session_may_write_inside_its_experiment_folder[Edit]` | same | moved |
| 204 | `W1-46/test_w1_46_research_role.py::test_a_research_session_may_write_inside_its_experiment_folder[Write]` | same | moved |
| 205 | `W1-46/test_w1_46_research_role.py::test_a_research_session_may_write_inside_its_experiment_folder_with_bash` | same | moved |
| 206 | `W1-46/test_w1_46_research_role.py::test_the_guard_grants_the_research_role_no_network_and_asks_nothing_for_it` | same | moved |
| 207 | `W1-46/test_w1_46_role_settings.py::test_both_variables_reach_the_guard[engineer]` | same | moved |
| 208 | `W1-46/test_w1_46_role_settings.py::test_both_variables_reach_the_guard[independent-auditor]` | same | moved |
| 209 | `W1-46/test_w1_46_role_settings.py::test_both_variables_reach_the_guard[independent-test-designer]` | same | moved |
| 210 | `W1-46/test_w1_46_role_settings.py::test_both_variables_reach_the_guard[research]` | same | moved |
| 211 | `W1-46/test_w1_46_runtime_and_ln.py::test_scratch_stays_writable_for_every_role[engineer]` | same | moved |
| 212 | `W1-46/test_w1_46_runtime_and_ln.py::test_scratch_stays_writable_for_every_role[independent-auditor]` | same | moved |
| 213 | `W1-46/test_w1_46_runtime_and_ln.py::test_scratch_stays_writable_for_every_role[independent-test-designer]` | same | moved |
| 214 | `W1-46/test_w1_46_runtime_and_ln.py::test_scratch_stays_writable_for_every_role[orchestrator]` | same | moved |
| 215 | `W1-46/test_w1_46_runtime_and_ln.py::test_scratch_stays_writable_for_every_role[product-spec]` | same | moved |
| 216 | `W1-46/test_w1_46_runtime_and_ln.py::test_scratch_stays_writable_for_every_role[research]` | same | moved |
| 217 | `W1-46/test_w1_46_runtime_and_ln.py::test_the_guard_does_not_refuse_ln_to_a_destination_the_role_may_write[inside-the-tickets-paths-hard]` | same | moved |
| 218 | `W1-46/test_w1_46_runtime_and_ln.py::test_the_guard_does_not_refuse_ln_to_a_destination_the_role_may_write[inside-the-tickets-paths-symbolic]` | same | moved |
| 219 | `W1-46/test_w1_46_runtime_and_ln.py::test_the_guard_does_not_refuse_ln_to_a_destination_the_role_may_write[scratch-hard]` | same | moved |
| 220 | `W1-46/test_w1_46_runtime_and_ln.py::test_the_guard_does_not_refuse_ln_to_a_destination_the_role_may_write[scratch-symbolic]` | same | moved |
| 221 | `W1-46/test_w1_46_runtime_and_ln.py::test_the_guard_holds_a_research_ln_to_the_experiment_folder` | same | moved |
| 222 | `W1-47/test_w1_47_failed_commands.py::test_a_failed_command_is_caught_through_the_committed_settings` | same | moved |
| 223 | `W1-47/test_w1_47_failed_commands.py::test_this_repository_registers_the_containment_check_after_bash[PostToolUseFailure]` | same | moved |
| 224 | `W1-47/test_w1_47_failed_commands.py::test_this_repository_registers_the_containment_check_after_bash[PostToolUse]` | same | moved |
| 225 | `W1-47/test_w1_47_failed_commands.py::test_this_repository_runs_the_same_check_after_a_failed_call` | same | moved |
| 226 | `W1-49/test_w1_49_registration.py::test_the_guard_hooks_stay_registered[PostToolUse-Bash-template/governance/kernel/hooks/posttooluse.py]` | `test_the_guard_hooks_stay_registered_in_the_kernel_s_wiring[PostToolUse-Bash-governance/kernel/hooks/posttooluse.py]` | moved |
| 227 | `W1-49/test_w1_49_registration.py::test_the_guard_hooks_stay_registered[PostToolUseFailure-Bash-template/governance/kernel/hooks/posttooluse.py]` | `test_the_guard_hooks_stay_registered_in_the_kernel_s_wiring[PostToolUseFailure-Bash-governance/kernel/hooks/posttooluse.py]` | moved |
| 228 | `W1-50/test_w1_50_freeze_launcher.py::test_a_launched_session_leaves_no_placeholder_at_the_flag_s_path` | same | moved |
| 229 | `W1-50/test_w1_50_freeze_live_pause.py::test_a_flag_put_over_the_placeholder_during_a_command_stays` | same | moved |
| 230 | `W2-59/test_w2_59_hook_lines.py::test_the_line_s_program_imports_the_pin_s_package_not_the_project_s_src[preToolUse[0]]` | same | not moved |
| 231 | `W2-59/test_w2_59_hook_lines.py::test_the_source_holds_the_seven_governance_hook_lines` | same | moved |
| 232 | `W2-59/test_w2_59_hook_lines_worker_env.py::test_a_command_that_sets_pythonpath_itself_is_let_through_and_runs_the_tree_s_code[preToolUse[0]]` | same | not moved |
| 233 | `W2-59/test_w2_59_hook_lines_worker_env.py::test_the_guard_line_refuses_what_the_pin_s_guard_refuses_whatever_the_session_s_import_path[preToolUse[0]-no-pythonpath]` | same | not moved |
| 234 | `W2-59/test_w2_59_hook_lines_worker_env.py::test_the_guard_line_refuses_what_the_pin_s_guard_refuses_whatever_the_session_s_import_path[preToolUse[0]-worker-pythonpath]` | same | not moved |
| 235 | `W2-65/test_w2_65_hook_lines.py::test_both_sources_hold_the_guard_and_the_containment_lines_and_the_guard_stays_recognisable` | same | moved |
