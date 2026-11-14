**Sandbox check (Step 0):** (a) the write to `/home/usain/gov-os-worktrees/.sandbox-trial-W2-185` failed as it should (`OSError: [Errno 30] Read-only file system`, and the file does not exist). (b) `echo sandbox-trial | git hash-object -w --stdin` worked and printed `1ae28402a109c3397a44b19239a00adfa9472eb0`; `git update-index --refresh` exited 0. **ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` printed nothing, at the start and at the end.

task: DAEO-qyt2 (W2-185)
status: PASS
work_completed: Independent STANDARD review, round 1, of `w2/W2-185` at head 1180e4ec5e13714ba70697ca77d95ff96c9294e4 (base 31eab2103). I read the ticket, the diff, DEC-1167 (4), DEC-971 item 3, DEC-805, DEC-1163 (6) and DEC-1156 (7). I ran every KPI Verify case and the S1, S3 and F1 plants in copies in `$TMPDIR`. I reproduced the six reds the lead listed, then looked for other reds this change causes and found twelve more. I classified all eighteen.
files_changed: none
evidence: Commands and result lines are under points 1 to 6 below. Copies used: `$TMPDIR/copy` (made with `git archive HEAD`); `$TMPDIR/copy-git` and `$TMPDIR/base-git` (the same at HEAD and at 31eab2103, each with `git init` because W2-59 and W2-90 need a repository); one plant copy per plant.
tests: Every KPI case is green unplanted (22 passed). Each plant turns its case red as it should. Across 23 hooks-related test files with the opt-in rows (`--optin lifted,breadth`): 25 failed, 392 passed. On the base copy, 7 of those 25 fail too, so 18 come from this change.
discoveries: (1) This change causes 18 reds outside `allowed_paths`, not 6. The default run's representative rule (`rep:` in `tests/conftest.py`) hides 12 of them; they show only with `--optin lifted,breadth`. All 18 are tests pinning the behaviour before DEC-1167 (4); none points to a defect. (2) Seven reds also fail on base 31eab2103 in this sandbox, so this change does not cause them: `test_w1_38_hooks_any_folder.py` PreCompact ×5 and `test_w1_38_rulesync.py::TestKernelAgainstAdapterSource` ×2.
risks: If the CTO revises only the six reds the lead listed, the land leaves 12 reds that appear in the next opt-in or nightly run (finding R1).
lessons: I ran the whole `tests/acceptance/W2-23/test_w2_23_space.py` once without `-m "not local_only"`, so its retrieve/context case ran. It ran against a planted HOME with no model reachable and passed, and no model process was left running; later folder runs carried the exclusion. Also, a pytest run without xdist over the four extra-red ids hung past its 20-minute background limit and was stopped; the same ids with `-n 4` finished in 2 s.
proposed_decisions: none
unresolved: My red scan covered only the test files that mention a hooks source, `_hooks_findings`, `LIFTED_HOOK`, `HOOK_SCRIPTS` or `context_watch`; it was not a whole-suite run.
recommended_next_action: Land on this check. The CTO revises all 18 reds under DEC-1156 (7) (the full list is under point 6), not only the six named, and confirms with `--optin lifted,breadth`.

### 1. S1: PASS
- **Byte-for-byte check:** the root's `context_watch.py` entry, with `template/governance/kernel/hooks/` replaced by `governance/kernel/hooks/`, equals the template's new entry as JSON (`True`) and as a text line (`diff` printed `LINE-IDENTICAL`). Matcher is `Bash`, timeout 10. The template's `posttooluse.py` entry is still there (`[True, False]`).
- **W2-23 S6, unplanted:** `tests/acceptance/W2-23/test_w2_23_space.py`, 4 passed, `test_s6_every_kernel_hook_exits_alike_with_a_space_in_the_project_dir` among them.
- **Plant:** an unwired `eighth.py` in `template/governance/kernel/hooks/` (copy `plant-s1`) makes S6 fail: `AssertionError: the settings' hook command lines do not reach the seven kernel hooks: ['eighth.py']` (line 108).

### 2. S2: PASS
- **Cases:** `test_program_env.py::test_this_repository_s_two_hooks_sources_agree`, `test_w2_05_hooks_source.py::test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources` and the 8 unit cases all pass (in the 22-passed run).
- **The exemption is per hook:**
  - It leaves out only the template's entries whose command contains `posttooluse.py`, and only in `postToolUse`/`postToolUseFailure`.
  - It applies in an event only while the root's source does not run `posttooluse.py` there; once the root runs it again, the event compares in full. That is a working version of DEC-971 item 3's "ending when they return with W2-08".
  - Both constants (`LIFTED_HOOK_EVENTS`, `LIFTED_HOOK`) and the docstring name DEC-971 item 3 and W2-08.
  - It leaves out strictly less than the old whole-event exemption did, so nothing that was compared before goes uncompared now.
- **Probed in copies:** changing the template's `context_watch` matcher to `Edit` gives `HOOKS_MATCHER_DIFFERS`. Adding `context_watch` to the template's `postToolUseFailure` gives `HOOKS_EVENT_DIFFERS`. Removing the root's `postToolUse` gives `HOOKS_EVENT_DIFFERS`.
- **Sound, not a finding:** changing the template's `posttooluse.py` matcher gives no finding. The root has no entry to compare it with; that is the exception DEC-971 item 3 decided, and the old exemption covered it too.

### 3. S3: PASS
- **Unplanted:** `test_w1_38_rulesync.py::TestHookStubs::test_hook_stubs_exist` and `test_w1_38_hooks_any_folder.py::TestABashCallAfterAChangeOfDirectory::test_an_ordinary_allowed_call_is_not_blocked` pass; `HOOK_SCRIPTS` holds the seven hooks.
- **Plant:** with `context_watch.py` removed from `HOOK_SCRIPTS` (copy `plant-s3`), both fail:
  - `AssertionError: hook scripts in .claude/settings.json do not exist: ['governance/kernel/hooks/context_watch.py']`
  - `… context_watch.py exit=2 … can't open file '…/governance/kernel/hooks/context_watch.py': [Errno 2] No such file or directory`

### 4. F1: PASS
Run with `_hooks_findings` over copies (script `$TMPDIR/f1.py`). Unplanted: `[]`.
- **Extra matcher on the root's `postToolUse`:** `HOOKS_MATCHER_DIFFERS … matchers ['Bash', 'Edit|Write'] here, ['Bash'] in template/.rulesync/hooks.jsonc`.
- **Template hook in another event (`notification`):** `HOOKS_EVENT_DIFFERS … hook event notification is only in template/.rulesync/hooks.jsonc`.
- **Extra template matcher in `preToolUse`:** `HOOKS_MATCHER_DIFFERS`.

### 5. Scope: PASS
- **Files:** `git diff --name-only 31eab2103..HEAD` lists eight files: `src/gov/adapters/portability.py`, `template/.rulesync/hooks.jsonc`, `tests/acceptance/W1-38/w1_38_support.py`, `tests/unit/adapters/test_w2_185_hooks_exemption.py`, and four files in `tests/acceptance/W2-185/`. All are in `allowed_paths` or the ticket's acceptance folder.
- **Non-goal:** the diff touches nothing under `.rulesync` or `.claude` (0 files).
- **Trailers:** every commit carries `Task: DAEO-qyt2`. The `Implements:` ids are DEC-1167, 1163, 971, 805 and 1156, all from the ticket's `sources:`. 58f95c15a carries `Rewrite-Reason: DEC-1167 (4)`.
- **Order:** the engineer's commit (a0558ff7d) comes before the test designer's cases (a3a97706d).
- **Tree:** `git status --porcelain` is empty at the end.

### 6. Reds outside the ticket's paths: all decided-behaviour revisions, no defect
Each id is red at HEAD and green at base (`$TMPDIR/base-git`). The two `postToolUse[1]` ids do not exist at base, where `postToolUse` has one entry.

**The six the lead named:**
- `test_hooks_lifted.py` `[lifted0]`, `[template]` and `test_the_finding_form_is_unchanged`. Revision: the lifted entries run a `posttooluse.py` command instead of the generic `python3 hook.py`. Under DEC-1167 (4) a generic hook in a lifted event is real drift.
- `test_w2_59_hook_lines.py::test_the_source_holds_the_seven_governance_hook_lines` (`holds 8 command entries; seven are expected`). Revision: expect 8 entries reaching the seven kernel hooks; `posttooluse.py` runs in two events.
- `test_w2_59_hook_lines.py::…imports_the_pin_s_package…[postToolUse[1]]` and `test_w2_59_hook_lines_worker_env.py::…runs_the_pin_s_code[postToolUse[1]]`. Revision: key the import expectation by program, not by event. `context_watch.py` imports only the standard library; its one sibling import (`precompact`) also imports no `gov` at top level and runs only when `GOV_ROLE` is orchestrator. So it should be measured like subagentStop (the pin's interpreter only).

**Twelve more the representative rule hid (finding R1):**
- `test_hooks_lifted.py` `[lifted1]`, `[lifted2]`, `[ours]`. Same revision as their sibling rows.
- `test_w1_38_hooks_any_folder.py` `[PostToolUse-root]`, `[PostToolUse-subfolder]`, `[PostToolUse-deep-subfolder]`, `[PostToolUse-outside]`, and `TestAProjectFolderWithASpace…[PostToolUse]` (`registers 2 guard hook entries under PostToolUse; one is expected`). Revision: pick the guard entry by its guard program (`posttooluse.py`), not by any kernel program.
- `test_w1_38_hooks_source.py::TestGeneratedGuardHooks…[PostToolUse]` (generated `[context_watch.py, posttooluse.py]` against `template/governance/kernel/settings.json`'s `[posttooluse.py]`). Revision: compare guard programs only. The kernel settings file holds only the three guard lines.
- `tests/unit/hooks/test_w2_106_template_hook_lines.py::test_the_settings_line_equals_its_rulesync_source[postToolUse]` (`postToolUse holds 2 command entries; one is expected`). Revision: `source_line` picks the entry running `posttooluse.py`.
- `test_w2_05_hooks_source.py::test_a_difference_that_is_not_drift_leaves_adapter_portability_green[only the command wrapper]` (`the template has not the repository's hooks of postToolUse`). Revision: pair entries by program and skip the exempt `posttooluse.py` entry, instead of pairing by position and count.

In every one of these the hook runs; the failure is a count or a pairing that assumed one entry in `postToolUse`.

### Findings
**Classification: one finding, out of scope, ordinary work yes, consequence other. No blocking finding; no round proposed.**

**R1 (out of scope: a row for the revision, not a KPI line).**
- **What happened:** the lead's whole-suite run named 6 reds outside the ticket's paths that the CTO is to revise. The change causes 18. The 12 others are parametrised rows that the default run leaves out (`rep:`) and that only the opt-in suites run.
- **What should happen:** the revision list given to the CTO under DEC-1156 (7) names all 18.
- Ordinary work: yes, because the CTO revising exactly the list it was given lands the branch with 12 reds that show up in the next `--optin lifted,breadth` or nightly run.
- Consequence: other (visible reds that fail closed; nothing fails open, no work is lost).
- **What would reverse it:** these 12 ids passing at HEAD with `--optin lifted,breadth`, or failing at 31eab2103.

Sound, probed: S1's byte equality and plant, S2's per-hook and conditional exemption, F1's drift cases, S3's fixture plant, scope, non-goals and trailers.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": [{"id": "R1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": []}]}
```

guard_refusals: none