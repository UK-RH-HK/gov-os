# Brief A1: independent test designer, DAEO-8lmb (W2-90), profile LITE, a test revision

You are a fresh independent test designer (MR-3). Ticket: `DAEO-8lmb` (`W2-90`, "The 235 live-wiring tests judge the kernel's wiring"), profile LITE, a test-revision ticket under the owner's named decision (DEC-906, given in DEC-957: ACT 1 option (a)). You work only in the worktree `/home/usain/gov-os-worktrees/W2-90` on branch `w2/W2-90`. This ticket has no engineer and no code change: your revised tests are the whole of it.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-8lmb','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (twelve fields), naming what happened. Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-8lmb`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-90` and `w2/W2-90`). If anything differs, stop and say so.

## What happened, and what you do

- ACT 1 (commit `6c36c7b5`, DEC-953 item 2, DEC-954) switched **this repository's own** pre-tool hook from the kernel's full guard to a five-rule hook (`.claude/hooks/pretooluse.py`), and removed this repository's containment hooks (PostToolUse, PostToolUseFailure) from `.claude/settings.json` and `.rulesync/hooks.jsonc`. Read `git show 6c36c7b5` (two files) and `governance/project/orchestration/packages/ACT-1-GUARD.md` whole. Nothing was removed from the product: the kernel's full guard and its containment hooks stay built and shipped in `template/` (its `.rulesync/` sources, `template/governance/kernel/settings.json`, `template/governance/kernel/hooks/`) and in `src/gov/guard/`.
- 235 cases in 19 files asserted that *this repository's live wiring* runs the kernel's full guard and its containment hooks. They are red after ACT 1 and green before it (the base `aafd45c1`). The 235 ids, one per line: `/home/usain/gov-os-worktrees/W2-90/.gov-runtime/scratch/lead/briefs/W2-90-cases.txt`; the measurement: `/home/usain/gov-os-worktrees/W2-90/.gov-runtime/scratch/lead/briefs/act1-confirmed.json` (how it was measured: ACT-1-GUARD.md, "Tests").
- **Your job, case by case:** each of the 235 asserts the same behaviour, with the same expected verdict, **of the kernel's wiring** instead of this repository's live settings:
  - where a case read this repository's `.claude/settings.json` or `.rulesync/hooks.jsonc`, it reads the settings the kernel's template generates (rulesync output from the template's `.rulesync/` sources, or the template's shipped settings file), or those of a repository generated from the template in a temporary folder (Copier, as other suites already do: see how `tests/acceptance/W1-38/`, `W1-39/` and `W1-40/` build the template source and a generated project in a temporary folder, never using this repository as Copier's source or destination);
  - where a case ran the live pre-tool hook line (or a containment hook line), it runs the hook line those generated settings register, the way Claude Code runs it (`sh -c`, the event's JSON on stdin, `CLAUDE_PROJECT_DIR` set to the generated project);
  - a path the case named in this repository's form (e.g. a hook under `template/governance/kernel/hooks/`) is asserted in the generated project's form (`governance/kernel/hooks/` under `$CLAUDE_PROJECT_DIR`): that is the same expectation of the kernel, not a lowering.
- **Lowering nothing (MR-3, DEC-906):** no case deleted, skipped, xfailed, parametrization narrowed, threshold loosened, or its verdict weakened. Every refusal, hook line and registration a case asserted of this repository it now asserts of the kernel's wiring, with the same verdict. The case count among the 19 files stays the same (every one of the 235 still exists, by id or by your README's map).
- **A case that truly cannot be moved** (for example, the kernel's generated line does not do or carry what the case asserted of this repository's pre-ACT line; note that the template's hook lines are not character-for-character this repository's pre-ACT lines, so judge each assertion by what it asserts), is **left exactly as it stands in the file, unchanged**, named in the README with its reason and what you measured of the kernel's wiring, and returned as a package. Never bend the assertion to make it pass, and never change product code, the template or the live settings.
- **The other cases in the 19 files** (those not among the 235) must stay green and keep their expectations; touch them only if a shared fixture you move requires it, lowering nothing.
- **Helpers:** shared fixtures may move into `tests/acceptance/W1-05/conftest.py` or `tests/acceptance/W1-46/conftest.py`; a helper module may live under `tests/acceptance/W2-90/`. Importing another suite's existing support module unchanged is fine; a change needed in any other file is a package. Keep generation cheap: build the template source and a generated project once per session or module (a scoped fixture), not once per case.
- **Both heads:** the revised files must not depend on this repository's live settings, so they pass both on the head after ACT 1 and on `aafd45c1` (the lead runs that second check on a clean clone; you do not clone anything).

## Your paths (write nothing else)

The 19 files:
- tests/acceptance/W1-05/test_w1_05_live_hooks.py
- tests/acceptance/W1-05/test_w1_05_role_subagents.py
- tests/acceptance/W1-28/test_w1_28_launch_product_spec.py
- tests/acceptance/W1-46/test_w1_46_hard_links_mv_and_install.py
- tests/acceptance/W1-46/test_w1_46_install_spellings.py
- tests/acceptance/W1-46/test_w1_46_links_and_cp_targets.py
- tests/acceptance/W1-46/test_w1_46_live_sessions.py
- tests/acceptance/W1-46/test_w1_46_options_after_the_destination.py
- tests/acceptance/W1-46/test_w1_46_research_installs.py
- tests/acceptance/W1-46/test_w1_46_research_role.py
- tests/acceptance/W1-46/test_w1_46_role_settings.py
- tests/acceptance/W1-46/test_w1_46_runtime_and_ln.py
- tests/acceptance/W1-47/test_w1_47_failed_commands.py
- tests/acceptance/W1-49/test_w1_49_registration.py
- tests/acceptance/W1-50/test_w1_50_freeze_launcher.py
- tests/acceptance/W1-50/test_w1_50_freeze_live_pause.py
- tests/acceptance/W2-59/test_w2_59_hook_lines.py
- tests/acceptance/W2-59/test_w2_59_hook_lines_worker_env.py
- tests/acceptance/W2-65/test_w2_65_hook_lines.py

plus `tests/acceptance/W1-05/conftest.py`, `tests/acceptance/W1-46/conftest.py` and `tests/acceptance/W2-90/**`. Nothing under `src/`, `template/`, `.claude/`, `.rulesync/`, `.tickets/`, `docs/` or `governance/`.

## What you read

- The ticket file `.tickets/DAEO-8lmb.md` (read-only): its KPI lines and `allowed_paths`.
- In `docs/DECISION_REGISTER.md`: DEC-957 (the ACT 1 part), DEC-953 (item 2), DEC-954, DEC-955, DEC-906, DEC-866.
- `governance/project/orchestration/packages/ACT-1-GUARD.md`; `git show 6c36c7b5`.
- The kernel's wiring as the product ships it: `template/` (its `.rulesync/` sources and the settings it ships or generates), `template/governance/kernel/hooks/`, `copier.yml`, and the public behaviour of `src/gov/guard/` as the hook exposes it. The existing suites that already generate a project from the template (`tests/acceptance/W1-38/`, `W1-39/`, `W1-40/`).
- **Use memory first:** `PYTHONPATH=/home/usain/gov-os-worktrees/W2-90/src python3 -m gov.cli.main retrieve "<question>" --json` for what you need to know before reading files at random (DEC-836). Never one giant query or context (DEC-860): a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph (DEC-859). If retrieve answers STORE_MISSING, say so and read files directly.
- **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths (its `allowed_paths` outside `tests/acceptance/`: there are none for this ticket), and name in your return any such result you were served.

## Reads open, writes closed (DEC-820, Policy 2)

You read freely: the whole repository, git history, other worktrees. Only four things are refused:
- (a) secrets and keys, never printed;
- (b) the contents of the held-out qualification material (its file names may be seen); never read or name the qualification oracle;
- (c) the counterpart's work on this ticket: you never read this ticket's implementation (the files `git diff --name-only w2/integrate...HEAD` names, other than your own tests; for this ticket there is no implementation);
- (d) the hidden half of any evaluation set, by whoever is measured by it.

Until W2-58 lands, the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`) (DEC-849): take the refusal, never look for another form, search named folders instead, and **count the refusals you met** in your return. Writes stay inside your paths.

## The code under test (DEC-732, word for word)

**In this worktree, every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-90/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-90/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.

## Running the tests

- Run the 19 files, to the end, never with `-x`, from this worktree: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-90/src python3 -m pytest <the 19 files> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs` (add `-n 4` if it helps; the project has pytest-xdist). First run them **before** your change and record the red count (it should be 235 failures among them); then after it: all green. Do not set `TMPDIR` yourself (the sandbox sets it). Keep pytest's own retention; never `--basetemp`.
- Run everything in the foreground, one command after another; nothing started in the background is ever read. A run longer than about 9 minutes is split by file.
- **Commit before any long suite run**, so work is never lost.

## The README

`tests/acceptance/W2-90/README.md`:
- one table mapping each of the 235 ids (exactly as in the case list) to its revised case id (the same id where it did not change);
- per file, one line saying what it now reads (the template's generated settings, the template's shipped settings, or a generated project) and how it runs the hook line;
- the KPI lines of the ticket, each mapped to how it is met (LITE: one line each);
- how a run from this worktree exercises this worktree's code (the `PYTHONPATH` line);
- any case that could not be moved, with its reason and what you measured: or "none".

## Commits

Commit only your paths, with `git commit -m "<subject>" --trailer "Task: DAEO-8lmb" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-957, DEC-953, DEC-906" --trailer "Rewrite-Reason: DEC-953 item 2" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`. Every commit that changes an earlier ticket's test carries `Rewrite-Reason: DEC-953 item 2`. `Implements:` holds decision ids only. One commit or a few; no amend, no rebase, no reset, no `git checkout` of another commit, no `git clean`, no push, merge or tag. Before each commit, check `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. After each commit, `git log --oneline -2` and `git status --short`.

## Standing rules

- **Your scratch budget (DEC-898):** 15 GB and 750,000 files and folders, outside the tracked tree (the sandbox's temp folder and anything untracked). Clean up what you create as soon as it is no longer needed. Measure (`du -s --inodes`, `du -sh` of your temp folder) before your long runs and at the end, and give the figures in `evidence`. Passing the budget: stop the heavy work, clean what you can, return.
- **Protected material:** never read the held-out material's contents and never print a secret. Never write in `~/gov-os-workbench`; never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **Row W2-L423's rule (DEC-911):** anything you write under `.gov-runtime/` and your return use commit hashes of 12 digits, never the full 40, and never the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule".
- **No copy of the tree:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it. A template source for Copier is assembled file by file in a temporary folder from `copier.yml` and `template/`, as W1-39's support does; never `governance/project/`. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it. No file of a programme under any `.gov-runtime/` folder.
- **The guard's command forms:** no shell variable as a write target (use literal paths), no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; write anything longer as a script file with the Write tool (in your temp folder) and run that file. Write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is raised as a P1 in your return (DEC-957). Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- **Never** run `gov close`, `gov adopt`, `gov pause` or `gov rebuild`; never run `docs/plan/tools/validate_s1.py`. Never ask or notify the owner (no question box, no `owner-ping`).
- **On an authentication or access error** (401, 403, "Failed to authenticate"): stop and return with status `AUTH_REQUIRED`.
- **If the guard or the sandbox refuses something you needed**, do not disguise the same call: a false positive (the hook refused something none of its five rules is meant to stop, e.g. a read-only `grep` or `sed -n` over `tests/acceptance/` taken for a write) may be worked round only by an equivalent form that does what was meant (the Read/Grep tools, or a script file); a true refusal is taken and returned as a package. **Refused twice for the same call: stop and say so; no third try.**
- An ambiguous KPI line or a dispute is never a guess: return it as a package (context, what happened, why it matters, options with consequence/cost/risk, recommendation and confidence, what it blocks).

## Return

One message, your last, after your commit exists. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

In those fields give: the step 0 result; your commits (12-digit hashes) with their trailers; the `gov.__file__` line; the 19 files' counts before and after your change (passed/failed/skipped/xfailed, and the 235 among them); the README's path; every case not moved, with its reason; the count of guard read refusals (DEC-849); whether you used `gov retrieve` and what it served (P-R1); your scratch measures; any untracked scratch file you could not remove, with its path.

Right after the twelve fields, two sections:
- `brief_gaps:` one line per gap, or `brief_gaps: none`. A gap is anything you had to discover, look up or ask that this brief, the ticket or the skills you loaded did not tell you. Each line: `- <what was missing> | <where it belonged: common brief, this ticket's part, the ticket file, skill <name>, or a tool> | <minutes it cost, measured or estimated, so marked>`.
- `guard_refusals:` one line per refusal by the five-rule hook that you met, or `guard_refusals: none`. Each line: `- <time> | <the command's form, one line, no secret or file contents> | <the rule's reason as the hook gave it> | true or false-positive | <minutes it cost and what you did instead>`.

Refused twice for the same call: stop and say so.
