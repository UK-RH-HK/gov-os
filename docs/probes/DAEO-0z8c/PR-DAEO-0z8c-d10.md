---
type: probe
task: DAEO-0z8c
reviewer_session: 01d864df-7683-4975-80a6-2f3a0e1e2456
implementer_session: the D-10 red-fix list's test designer of `5e9cdcc8d` (tests/conftest.py and tests/unit/gitenv/test_w2_05_suite_git_env.py; its session log went with its removed worktree)
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 9ca161a6fe38b4dbac953841f4f76e5b91654cfa
---

# Fresh probe of W2-05 (DAEO-0z8c) at 9ca161a6fe38, after D-10's merge (DEC-895)

- **Why fresh:** `probe_impact.py` named it stale: the merge `384b2245b` (D-10's red-fix list item 1, the core.bare fix's tests' half) changed a judged file (`.tickets/DAEO-0z8c.md`, its paths).
- **Brief:** `.gov-runtime/scratch/orchestrator/briefs/D10-W2-05-probe.md`; a fresh, read-only independent reviewer, effort max, launched by the CTO's D-10 helper; verdict.py READY (no blocking finding); the orchestrator's judgement: pass.
- **The reviewer's record follows, as returned.**

sandbox_check: pass. (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0z8c` failed with `OSError: [Errno 30] Read-only file system`, and no file exists. (b) `git hash-object -w --stdin` returned `1ae28402a109`; that object was already in the store, the same one the D-10 review wrote. `git update-index --refresh` exited 0.

ps_check: nothing found. Each command here runs in its own PID namespace, and `ps -eo pid,args` showed only that command's own three processes. No ollama and no llama-server.

task: DAEO-0z8c (W2-05). A fresh FULL probe at integrate `9ca161a6fe38`, after D-10's red-fix item 1 (`384b2245b`: `5e9cdcc8d`, `b83e73b99`). KPI id `w2-05-full-probe`.

status: DONE. Judgement: **pass**.

work_completed:
- Read the brief, EMG-common, JUDGEMENT, the ticket at `9ca161a6fe38`, the D-10 diff, the whole `tests/conftest.py`, `src/gov/util/gitenv.py`, the new unit case and the D-10 review.
- Read the last probe record (dec971), the acceptance README and the sweep record.
- Checked the five files the sweep test names and every local `GIT_*` filter in `src/gov`.
- Looked at the other tickets' conftest changes (W2-56, W2-141) and W2-56's changes to `src/gov/codeintel/__init__.py`.
- Ran W2-05's acceptance and gitenv unit suites with both opt-ins, plus the one case the exclusion leaves out, by node id.
- Called the portability check's hooks, kernel and template comparisons directly over this tree, read-only.
- Reproduced the cause of the portability reds in my temp folder (F1).
- Checked the status of DEC-1074, DEC-1083, DEC-1109 and DEC-1065.

files_changed: none in any tree.
- `git status --porcelain` is empty.
- The ignored-file listing is identical before and after.
- Nothing in the tree is newer than my scratch folder except the root and `.gov-runtime/` folder times, which change with every sandboxed command (bubblewrap's mount points).
- Python ran with `PYTHONDONTWRITEBYTECODE=1`.

evidence:
- Probed commit `9ca161a6fe38` (HEAD of the probe tree). Session `01d864df-7683-4975-80a6-2f3a0e1e2456`. git 2.43.0.
- Scratch peaked at 85M and 15,168 inodes under `/tmp/gov-launch-w0v81iq0/claude-1000/w205probe`; now removed.
- The acceptance run waited for a heavy slot ("all 3 slots taken", 10:23:36), then ran in 110 s.

tests: all with `PYTHONPATH=<tree>/src`, an empty HOME, `PYTHONUSERBASE=/home/usain/.local`, my own TMPDIR, `-p no:cacheprovider -o tmp_path_retention_policy=failed --optin=lifted,breadth -m "not local_only" -k "not real and not green_here and not time_limit"`. Both suite runs went through `heavy_slot.sh`.
- `tests/acceptance/W2-05`: 27 failed, 38 passed, 0 skipped. The reds are named under check 3.
- `tests/unit/gitenv`: 60 passed, 1 deselected. All five rows of the new D-10 case passed, including the two breadth-only rows.
- What the exclusion left out, across both folders: only `tests/unit/gitenv/test_bisect_step.py::test_a_real_bisect_s_tests_get_only_the_run_s_environment` (a real `git bisect`, no model). Run alone by node id: 1 passed. Neither folder has any `local_only` case.

discoveries:
- **The wait on ACT-CLAUDE-COPIES-2 does not match these reds.** W2-05's 25 adapter-portability reds are not the ACT's (F1). The live tree's portability red is different: two skill sources, `.rulesync/skills/{orchestration,test-design}/SKILL.md`, which the ACT does fix.
- **The sweep red is hidden from default runs.** The sweep case is breadth-only (`tests/optin-lifted-breadth.txt:987`), so default runs and D10-REDS never show it (F2).
- **The code-index case now fails in a launched session for a different reason** than the README gives. `gov rebuild` cannot create its per-tree lock `/tmp/gov-os-rebuild-<hash>.lock`; the README names the daemon folder instead.
- **The brief's line that "DEC-1109 joined its sources" does not hold at `9ca161a6fe38`** (F4).
- The sandbox exports `GIT_CONFIG_COUNT` with four `safe.directory` keys and values, plus `GIT_CONFIG_PARAMETERS`. The conftest drops them from test processes. As the D-10 review found, this is harmless, because uid 1000 owns both the repository and the process.

risks:
- While F1 stands, W2-05's hooks comparison has no green acceptance case at integrate. My direct call and my reproduction stand in for them.
- Not checked: the strip follows whatever a newer git prints for `--local-env-vars`. If a later git listed a variable the runner sets on purpose (for example `GIT_NO_LAZY_FETCH`), test processes would lose it. Only git 2.43.0 is installed here.

lessons:
- Re-read a red's cause from its findings at each run. D10-REDS item 11's cause for W2-05's portability reds was true at `7b08bd12d`, but it changed by `9ca161a6fe38`.
- A raw `env` dump, used here to find the `GIT_*` names, also prints the session's proxy credentials. Use `printenv <names>` instead.

proposed_decisions: none.

unresolved:
- `test_w2_05_code_index_tool.py::test_the_code_index_tool_started_by_gov_rebuild_gets_no_inherited_git_variable` (S1's only full-run case) cannot be decided in the sandbox. It needs a run outside it.
- Whether ACT-CLAUDE-COPIES-2 changes F1. I read that it does not; the reversal evidence is in F1.

recommended_next_action:
- CTO: record the probe as pass.
- Run the code-index case outside the sandbox.
- Send F1 to W1-38's support owner or W2-153, not to the ACT: `build_project_from_template` should also copy `governance/kernel/templates/` and its `.claude/templates/` copies.
- F2 and F3 ride along in W2-05's next resume (DEC-802): sweep rows for the five files, and `role_paths.py` moved onto `git_env(root, pinned=True)`.
- F4 and F5 are record fixes, also riding along.

decisions: DEC-801, DEC-802, DEC-808, DEC-809, DEC-1010 (judgement); DEC-710, DEC-804 item 3, DEC-805, DEC-970, DEC-971 item 3 (KPI behaviours); DEC-1061 (opt-in suites); DEC-1074 (8), DEC-1083, DEC-1109 (2) (the change's grounds, all ACCEPTED, none superseded or proposed); DEC-927, DEC-1073 (F4).
template: role-reviewer@1.0.0
commits: none
brief_gaps: the brief gives ACT-CLAUDE-COPIES-2 as the cause of the portability reds; the run shows another cause (F1) | brief | 0 min. The estimate was 15 min; F1's reproduction and the sweep red took about 35 more.
guard_refusals: none

## Answers to the checks

**1. The success KPI (S1), with the conftest strip: met for this revision. Nothing in D-10 contradicts the one-helper rule for product code.**
- **What the strip does.** It acts only on the test processes' own environment (`tests/conftest.py:113-152`). It runs at import, in the controller before xdist starts and again in every worker.
  - It removes: the names git itself reports as repository-local; git 2.43's fifteen names, when git cannot answer; and every `GIT_CONFIG_KEY_n`/`VALUE_n`.
  - It keeps: identity, transport, trace, `GIT_CONFIG_GLOBAL` and `GIT_CONFIG_NOSYSTEM`.
- **No product process is touched.**
  - Nothing in `src/`, the template or the orchestrator tools imports the conftest or runs `pytest.main`, and no template conftest ships.
  - The close, the nightly and `gov ci checks` start tests through `runner_env`/`program_env`, so the strip changes nothing there. It matters only for a pytest started by hand, by `git bisect run`, or by a hook.
- **Why there is no contradiction.** The conftest's list is a second list, but it is test infrastructure, and it differs from the helper on purpose:
  - it must load without `gov`, because the nested runs have only `tests/` on the path;
  - it must keep `runner_env`'s generated `GIT_CONFIG_GLOBAL`, which the helper's `program_env` would drop (DEC-970);
  - it asks git for the names, so it cannot drift from git.
- **At integrate**, the KPI's record half is red from other tickets (F2), and one product file clears the variables by itself (F3). Neither comes from D-10. The behaviour half holds: all 22 planted cases pass.

**2. The DEC-710 case: unaffected and green.**
- The change acts at import on the test process only. The hooked-commit cases build lefthook's environment from nothing, and git exports `GIT_DIR`/`GIT_INDEX_FILE` to the hook itself, after the import.
- All 4 linked-worktree cases pass: the branch, index and reflog stay as the commit made them, through the retrieval check, through the refusing hook, and through lefthook with `gov ci checks G1 G2`.
- The 3 declared-check cases (F-A) pass.

**3. The runs and every red.**

| Case(s) | Red | Whose |
|---|---|---|
| `test_w2_05_hooks_source.py`, all | 24 | Not W2-05's. W2-153's composed template sources meet W1-38's support (F1). |
| `test_w2_05_settings.py::test_adapter_portability_stays_green_through_install_and_the_owner_s_uninstall_and_restore` | 1 | Same cause. The three byte-identical S3 cases pass. |
| `test_w2_05_sweep.py::test_every_file_of_the_source_that_starts_git_is_named_in_the_sweep` | 1 | W2-05's record, red from merges by W2-116, W2-129 and W2-150 (F2). |
| `test_w2_05_code_index_tool.py::test_the_code_index_tool_started_by_gov_rebuild_gets_no_inherited_git_variable` | 1 | The sandbox's: the rebuild lock under `/tmp` is read-only here. The code path under test (`_env` built from `git_env(root)`) is unchanged since `e122beca7ef7`; W2-56 only changed the daemon folder and the pool size. |

Green: 3 bisect, 3 declared-check, 4 linked-worktree, 22 planted, 3 settings and 3 sweep cases. The guard's freeze look-up answered in 15.2 s, inside its 14.5–18 s window.

**4. Judgement: pass.** No finding is in scope, reachable in ordinary work, and fails open or loses work.

## Findings

Classification (DEC-809): F1 out/yes/other; F2 out/yes/other; F3 out/yes/other; F4 in/yes/other; F5 in/yes/other. None blocks; all are rows.

**F1: W2-05's adapter-portability family is red for a reason the awaited ACT does not touch.**
- What was done: the 24 hooks-source cases and the S3 portability case ran at `9ca161a6fe38` with both opt-ins.
- What happened:
  - Each case stopped at its control. Portability was already red on the base pair before anything was planted.
  - The findings were six `SOURCE_DIFFERS`, one per `.rulesync/subagents/<role>.md` ("differs from …/roles/<role>.md"). None named a hooks source. That makes 150 findings, 6 in each of the 25 cases.
  - Cause: since W2-153, the template's six subagent sources are composed from `template/governance/kernel/templates/role-*.md`. I checked that their bodies equal the templates and not the role files.
  - W1-38's `build_project_from_template` copies only the kernel's hooks, roles and skills. With no templates in the project, the check falls back to the role files (`portability.py:241-243`).
  - I added `templates/` and its `.claude/templates/` copies to that project in my temp folder. The drift case `[an event in the template's source only]`, the case over this repository's two sources, and `…lifted…template_s_source_only…[both]` then passed.
  - ACT-CLAUDE-COPIES-2's ten files (`.claude/agents/*`, `.rulesync/skills/{orchestration,test-design}`, `.claude/skills/{…}`) are not read by these projects.
- What should have happened: the control is green, then each case runs its own assertion.
- Ordinary work: yes, because every run of these cases (and of W1-38's) builds the project this way.
- Consequence: other. The cases fail closed, and W2-05's comparison goes unexercised by them; nothing passes wrongly and nothing is lost.
- Scope: out (W2-153 and W1-38's support).
- Reversed by: these 25 cases going green after ACT-CLAUDE-COPIES-2 lands, with no change to W1-38's support or to `template/.rulesync/subagents/`.

**F2: The sweep record no longer names every git-starting file in `src/gov`, and only a breadth run shows it.**
- What was done: ran the sweep case with `--optin=breadth`.
- What happened: 5 of 33 files are unnamed.
  - `src/gov/links/command.py` (W2-129).
  - `src/gov/rebuild/command.py` and `src/gov/rebuild/integration.py` (W2-116).
  - `src/gov/util/gitrun.py` (W2-150: the close's git runner, sweep row 32, moved unchanged).
  - `src/gov/util/role_paths.py` (W2-150, moved from W2-13's `gov.guard.role_paths`).
  - Four of the five reach git through the one helper. `links` is pinned; the two `rebuild` files are unpinned for read-only lookups. The fifth is F3.
- What should have happened: each file gets a row (or a W2-05 round adds them) when it merges.
- Ordinary work: yes, because tickets add or move git-starting files in ordinary work, and the only check for it is breadth-only.
- Consequence: other. No inherited location variable reaches any of the five; this is the record only.
- Scope: out.
- Reversed by: this case green at integrate with `--optin=breadth`.

**F3: One product file clears git's variables by itself instead of through the one helper.**
- What was done: a role-filtered search (`gov retrieve`, or `gov context`'s block) finds the main tree and the changed files with git (`src/gov/util/role_paths.py:54-55`, 112, 175, 251, 268).
- What happened: those git calls get the caller's environment minus every `GIT_*`, from a function of the file's own. The configuration is not pinned, so a person's global settings, such as a trace2 target, are read. This is the same class as sweep row 61 (`guard/reads.py`, after W2-84).
- What should have happened: the calls use `git_env(root, pinned=True)` and the file has a sweep row.
- Ordinary work: yes, because every role-filtered search makes these calls.
- Consequence: other. The file clears more than the helper does, so no inherited `GIT_DIR` or index reaches the calls. At most a person's trace target gets events, as in R7-2.
- Scope: out (W2-13's code, moved by W2-150).
- Reversed by: the calls taking their environment from `gov.util.gitenv`, or a decision exempting the file as row 61 is exempted.

**F4: The ticket's `sources:` do not list the decisions the D-10 change rests on.**
- What was done: `b83e73b99` added `tests/conftest.py` to the paths, citing DEC-1074 (8), DEC-1083 and DEC-1109 (2) in the line's comment. `5e9cdcc8d` carries `Implements: DEC-1109, DEC-1074`.
- What happened: `sources:` at `9ca161a6fe38` lists none of the three. The brief's "DEC-1109 joined its sources" is true only of the comment.
- What should have happened: all three in `sources:`, as was done for W2-134 and W2-92 after gov links' notice.
- Ordinary work: yes, because agents and `gov links` read `sources:`, not path comments.
- Consequence: other. Traceability only; all three decisions are ACCEPTED.
- Scope: in.
- Reversed by: `sources:` holding the three at integrate, or `gov links` raising no notice for DAEO-0z8c.

**F5: The sweep record says nothing about the conftest's own git call and its own list.**
- What was done: D-10 gave the conftest a git call (`git rev-parse --local-env-vars`, from `/`, at import in every test process) and a fixed list of git's repository-local names.
- What happened: the record only says that test helpers outside `src/` (`tests/**/*support*.py`) are not Gov OS calls (`AR-2-git-sweep.md:198`).
- What should have happened: one line naming the strip, its call, and why it does not use the helper.
- Ordinary work: yes, because the record is where an agent looks for git calls and their environments.
- Consequence: other. Record only; the behaviour is right.
- Scope: in.
- Reversed by: a reading that the record covers only the Gov OS source (its own title says so). Under that reading this is no finding.

The D-10 review's rows F1 (two rows that run only with breadth) and F2 (the evidence line) are unchanged.

## Probed and found sound

- **The strip itself.** The nested case passes alone, under xdist, and with no git on PATH, where the fixed list is used. Workers inherit the cleaned environment and strip again.
  - `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_NOSYSTEM`, identity and trace are kept.
  - No process outside pytest imports the conftest.
  - No ordinary hook runs pytest directly; declared checks get `program_env`. So a stripped index cannot change what is scanned.
- **The conftest's own git call** is unpinned. In a run by hand, a person's global trace2 target gets one event per test process. Under the close or the nightly (`runner_env`, pinned) it gets none. The tests' own git calls already read that configuration in a run by hand, so this adds nothing new.
- **W2-05's hooks comparison.** Over this tree's two live sources, `_hooks_findings` returns no finding, with the DEC-971 item 3 exception. The three reproduced cases pass. The unit hooks cases pass.
- **Other tickets' conftest changes** do not touch git's variables or how git is found:
  - W2-56's PATH swap keeps the stand-ins in temp folders.
  - W2-141 adds only a per-test guard call-log folder.
  - `git_binary` uses fixed folders, not PATH.
- **The code-index tool's environment** is still built from `git_env(root)`.
- **All planted F1 cases are green:** the decoys are untouched, foreign indexes are refused and named, the trace and partial-clone cases pass, the guard uses git by absolute path, the 15 s limit holds, and the close's subprocesses get a sanitised environment.

```verdict
{"kpis": [{"kpi": "w2-05-full-probe", "verdict": "pass", "findings": [{"id": "F1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```
