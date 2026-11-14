1
Step 0 and the `ps` check came first: the sandbox check passed, and no ollama or llama process of mine was running.

task: DAEO-qyt2 (W2-185), run 2 batch 3. I revised the 18 cases to the decided behaviour (DEC-1167 (4), DEC-1156 (7)) and fixed 5 more red cases the 18 did not cover.
status: done. The seven files and the support file are committed, one commit each. The tracked `git status --short` is empty.

**Step 0 (sandbox check, reported first):**
- (a) The write to `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-qyt2` failed with a read-only file system error, as required.
- (b) `git hash-object -w --stdin` and `git update-index --refresh` both worked.
- `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` showed nothing of mine.

work_completed:
- **Before** (my own run, because the lead's `reds-pre-0c7e4d68f.txt` was absent): `23 failed, 153 passed, 2 deselected in 119.30s`.
  - 18 of the 23 are the decided-behaviour reds:
    - `test_hooks_lifted.py`: 6
    - W2-59 hook lines: 3 (one in the worker-env file)
    - W1-38 `PostToolUse`: 5
    - W1-38 hooks-source: 2
    - `test_w2_106_template_hook_lines.py`: 1
    - W2-05: 1
  - The other 5 are W1-38 `PreCompact` (4 any-folder cases and 1 space case). They are red for a different cause: the `PreCompact` program now writes its read-first line as plain text before its JSON message (W2-176), so the support file's JSON reader returned nothing.
- **After:** `192 passed, 2 deselected in 141.83s (0:02:21)`, with the opt-in suites and the brief's `-m` and `-k`.
  - No case is gone: the diff deletes no `def test_`, adds no skip, xfail or flaky mark, and every parametrised id is kept.
  - 16 cases are added, so 176 became 192.
  - I assume the "before" run collected the old `test_hooks_lifted.py`; its failure list showed only the old test names.
- **`-k "not time_limit"` hides 2 cases that were also red:** `test_every_guard_hook_entry_of_the_source_carries_the_time_limit` and its generated-settings twin. The template's `context_watch.py` entry has timeout 10, so both would fail. I revised them (see below) and ran them separately: `2 passed`.
- **Plants** (in a scratch copy of HEAD under `$TMPDIR`, removed afterwards):
  - Template without `context_watch.py`:
    - the W2-59 seven-lines case goes red;
    - the `postToolUse` settings-versus-kernel case goes red;
    - the two W1-38 context-watch source cases go red;
    - the 5 W1-38 context-watch any-folder cases (4 folder kinds plus the space case) go red;
    - the W2-106 two-entries case goes red.
  - `context_watch.py` made to import the project's own `src/gov`: the W2-59 import case and the worker-env case, both `postToolUse[1]`, go red.
  - The kernel settings' `PostToolUse` command changed: W2-106 `test_the_settings_line_equals_its_rulesync_source[postToolUse]` goes red.
  - `LIFTED_PROGRAM` set to another program: 10 unit cases go red.
  - W2-05 expectation flipped for another matcher on the template's context watch, and the non-exempt extra entry removed: 3 cases go red.
  - Each plant was reverted by deleting the copy.
- `tests/acceptance/W2-185` plus `tests/unit/adapters/test_w2_185_hooks_exemption.py`: `21 passed in 0.16s`.

files_changed (8, one commit each):
- `tests/acceptance/W1-38/w1_38_hooks_support.py`
- `tests/acceptance/W1-38/test_w1_38_hooks_any_folder.py`
- `tests/acceptance/W1-38/test_w1_38_hooks_source.py`
- `tests/acceptance/W2-59/test_w2_59_hook_lines.py`
- `tests/acceptance/W2-59/test_w2_59_hook_lines_worker_env.py`
- `tests/unit/hooks/test_w2_106_template_hook_lines.py`
- `tests/acceptance/W2-05/test_w2_05_hooks_source.py`
- `tests/unit/gitenv/test_hooks_lifted.py`

evidence: the before and after count lines above, the plant results above, and the commit list below.

tests: all of the above ran through the heavy slot with `HOME` set to an empty scratch folder. The brief's `-m "not local_only"` and `-k "not real and not green_here and not time_limit"` left out the real-model cases and the two time-limit cases, which I ran by hand. I changed no ids, so the `rep:` lines in `tests/optin-lifted*.txt` should still match; I did not open those lists.

discoveries:
- The brief says `context_watch.py` imports only the standard library. It also does `from precompact import checkpoint_rel` for an orchestrator's session, and `precompact.py` imports `gov.checkpoint.record`. For an engineer session, which these cases use, it imports no `gov`. The cases therefore read "imports no package but the standard library and the kernel's own hook modules" from the program's syntax tree.
- The template's `context_watch.py` line is the same as the root's apart from the path, in the pinned form, so the old "template and root differ in wrapper for every entry" assertion could not hold for it. The W2-05 wrapper case now needs at least one differing wrapper and matches entries by program.
- The kernel `settings.json` registers no `context_watch.py`. The generated `PostToolUse` now equals the kernel's entry plus `("Bash", "context_watch.py", 10)`, and every other guard entry still carries 60.

risks:
- The `PreCompact` fix is outside DEC-1167 (4). It is in `w1_38_hooks_support.py`, an allowed path, and the case still asserts the program's own "no state block" message.
- The commits have no `Co-Authored-By` line, because the brief's trailer list did not include one. Say if you want it added.
- I could not read `portability.py`, so the unit cases assert the finding code only loosely where the exact code was unknown. The finding must name the event and is `HOOKS_EVENT_DIFFERS` or `HOOKS_MATCHER_DIFFERS`.

lessons:
- `-k "... not time_limit"` hides two reds that a context-watch timeout of 10 causes, so a clean count is not the whole picture.
- A `( cmd & )` background run was killed when the call ended. Use `run_in_background` for a run that may wait for a slot.

proposed_decisions: none.
unresolved: none.
recommended_next_action: the lead merges the 8 commits and runs the opt-in sets outside the sandbox, including the 2 `time_limit` cases and the real-model cases that were left out.

**commits:**

| hash12 | subject |
|---|---|
| `2ad99213c672` | W2-185 (DAEO-qyt2): W1-38's hooks support knows the context watch entry (its own limit 10, its own answer) and reads PreCompact's message from the last line |
| `8ee2c6dc422e` | W2-185 (DAEO-qyt2): W1-38 any-folder cases start the guard line by its program and the context watch from every folder |
| `6cb684972cdf` | W2-185 (DAEO-qyt2): W1-38 hooks-source cases hold the context watch to matcher Bash and limit 10 beside the guard's entries |
| `00b56d2f2a43` | W2-185 (DAEO-qyt2): W2-59 hook-line cases count the seven kernel programs in eight lines and judge a standard-library program by its interpreter |
| `80841a0c66b0` | W2-185 (DAEO-qyt2): W2-59 worker-environment case reads which programs import the pin's package from the program |
| `1689ecce8726` | W2-185 (DAEO-qyt2): W2-106 line cases find the guard's postToolUse line by its program and hold the context watch's line |
| `86a7e7480d95` | W2-185 (DAEO-qyt2): W2-05 portability cases wrap by program and keep the per-hook lift's opposite faces |
| `e54b383f882b` | W2-185 (DAEO-qyt2): the lift unit cases exempt the posttooluse.py entry per hook, never a whole event |

Every commit carries these trailers in one final paragraph: `Rewrite-Reason: DEC-1167 (4), DEC-1156 (7) (W2-185 run 2)`, `Task: DAEO-qyt2`, `Role: independent-test-designer`, `Implements: DEC-1167, DEC-1156`.

**Per case** (`<node id> | what it guards | revision`). Ids are kept; `[…]` stands for every parametrised id of the case.
- `test_hooks_lifted.py::test_a_lifted_event_in_the_template_only_is_no_finding[lifted0..2]` | a lifted entry is no finding | the template's lifted entries now run `posttooluse.py`.
- `test_hooks_lifted.py::test_any_other_event_in_one_source_only_is_still_a_finding_beside_the_lifted_ones[template|ours]` | another event in one source only is still a finding | same lifted-entry change.
- `test_hooks_lifted.py::test_the_finding_form_is_unchanged` | the finding form is unchanged | same lifted-entry change.
- `test_hooks_lifted.py::test_a_lifted_event_in_the_repository_only_is_still_a_finding[…]` and `…_back_in_both_sources_is_compared_as_any_other[…]` | direction and both-sources comparison | the root's entries run `posttooluse.py`; they were already green.
- `test_hooks_lifted.py` new cases:
  - `test_the_lift_is_the_posttooluse_entry_and_no_other_entry_of_the_event[…]`
  - `test_a_lifted_event_with_the_root_s_other_entry_is_compared_without_the_lifted_entry[…]`
  - The first pins that an entry beside the lifted one is still a finding; the second pins that the lifted entry beside the root's other entry compares green, and another matcher is a finding.
- `W2-59/test_w2_59_hook_lines.py::test_the_source_holds_the_seven_governance_hook_lines` | the seven hooks' lines | it now counts the seven kernel programs started, in eight lines, with `postToolUse` holding `posttooluse.py` and `context_watch.py`.
- `W2-59/test_w2_59_hook_lines.py::test_the_line_s_program_imports_the_pin_s_package_not_the_project_s_src[postToolUse[1]]` | the pin's package import | a program importing only the standard library plus the kernel's own modules is judged by the pin's interpreter and by `src/gov` staying out.
- `W2-59/test_w2_59_hook_lines_worker_env.py::test_with_a_worker_s_pythonpath_the_line_s_program_runs_the_pin_s_code[postToolUse[1]]` | the pin's code under a worker's `PYTHONPATH` | the same program-based reading, like subagentStop's.
- `W1-38/test_w1_38_hooks_any_folder.py::TestEveryEntryStartsFromAnyFolder::test_the_registered_command_starts_its_program[PostToolUse-*]` and `TestAProjectFolderWithASpace::…[PostToolUse]` | the guard entry's line in every folder | the guard line is found by its program, not by count.
- `W1-38/test_w1_38_hooks_any_folder.py` new cases: `TestTheContextWatchStartsFromAnyFolder::test_the_registered_command_starts_its_program[…]` and `TestAProjectFolderWithASpace::test_the_context_watch_command_starts_from_a_subfolder` | the new entry starts from any folder | they check its own answer, a reminder at 90 % of the window.
- `W1-38/test_w1_38_hooks_any_folder.py::…[PreCompact-*]` and `…[PreCompact]` (5 cases, not in the 18) | the program's own message | the support file now reads the JSON message from the last line.
- `W1-38/test_w1_38_hooks_source.py::TestGeneratedGuardHooks::test_the_generated_settings_register_what_the_kernel_template_s_settings_register[PostToolUse]` | settings line equals its source | generated equals the kernel's entry plus `("Bash", "context_watch.py", 10)`, for `PostToolUse` only.
- `W1-38/test_w1_38_hooks_source.py::TestRulesyncPassesBothThrough::test_a_limit_and_a_failed_tool_call_entry_of_the_source_reach_the_generated_settings` | rulesync carries the limit and the failed-call entry | the `postToolUse` entry is picked by program, not by count.
- `W1-38/test_w1_38_hooks_source.py::test_every_guard_hook_entry_of_the_source_carries_the_time_limit` and `TestGeneratedGuardHooks::test_every_guard_hook_entry_of_the_generated_settings_carries_the_time_limit` (the two cases `-k` hides) | every guard entry carries its limit | the context watch is held to 10 and every other entry to 60.
- `W1-38/test_w1_38_hooks_source.py` new cases:
  - `test_the_context_watch_entry_of_the_source_carries_its_own_limit_and_the_bash_matcher`
  - `test_the_context_watch_entry_with_the_guard_s_limit_is_found`
- `test_w2_106_template_hook_lines.py::test_the_settings_line_equals_its_rulesync_source[postToolUse]` | the settings line equals its source | the source line is found by program (`posttooluse.py`).
- `test_w2_106_template_hook_lines.py::test_post_tool_use_holds_the_guard_line_and_the_context_watch_line_and_no_other` (new) | the pair of entries | it pins two entries, with the context watch at matcher `Bash` and timeout 10.
- `W2-05/test_w2_05_hooks_source.py::test_a_difference_that_is_not_drift_leaves_adapter_portability_green[only the command wrapper]` | a non-drift difference leaves portability green | entries are matched by program; at least one wrapper must differ, since the context watch's line is the same in both sources.
- `W2-05/test_w2_05_hooks_source.py` new cases:
  - `test_a_template_entry_of_a_lifted_event_that_runs_another_program_is_a_finding[…]` pins that a non-exempt entry in the same event is a finding.
  - `test_the_template_s_context_watch_beside_the_lifted_entry_is_compared_as_any_other[…]` pins that the context watch beside the lifted entry is green with the same matcher and a finding with another.

guard_refusals:
- A `Read` of the probe record `docs/probes/DAEO-qyt2/PR-DAEO-qyt2.md` was refused as `{ticket_impl}` (`role_paths.independent-test-designer.reads_denied`). I did not retry or work around it. I derived the revisions from the red failures, the test files, the brief and DEC-1167 (4).
- One `Bash` call that named `template/.rulesync/hooks.jsonc` was refused for the same reason. I read the integrate version with `git show w2/integrate:template/.rulesync/hooks.jsonc`, the route the role file names. That version has no context watch, so I used it as the "context watch removed" plant.
