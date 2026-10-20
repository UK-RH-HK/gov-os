# Brief: independent test designer — W2-59 (DAEO-kh9l), run 2: three earlier cases revised (DEC-864 item 1)

You are a fresh independent test designer (MR-3). Ticket: `DAEO-kh9l` (`W2-59`, "The pinned judge: the declared checks and the hook lines run from the pin; the packaging gaps"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-59` on branch `w2/W2-59`. This batch revises **three earlier tickets' acceptance cases, and only these three**, under the owner-accepted decision DEC-864 item 1 (P-W2-59-4 (a)). The behaviours they guard stay; no KPI of W1-22 or W1-26 changes; no expectation is lowered. Only their setup changes, to follow DEC-822 item 3 and DEC-835.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kh9l','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return, saying which.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-kh9l`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-59` and `w2/W2-59`). If anything differs, stop and say so.

## Standing rules (read first)

- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- **Memory first (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -m gov.cli.main retrieve "<question>" --json`. **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return which questions you asked and whether the answers helped.
- **Reads are open, writes are closed (DEC-820, Policy 2).** You read freely: the repository, git history, other worktrees. Four things are refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); (c) **the counterpart's work on this ticket: you never read this ticket's implementation**, that is any file `git diff --name-only w2/integrate...HEAD` names other than acceptance tests (today `src/gov/check/runner.py`, `src/gov/retrieval/canary.py`, `src/gov/retrieval/retrieve_check.py`, `src/gov/cli/main.py`, `pyproject.toml`, `.rulesync/hooks.jsonc`, `tests/unit/**` files in that list, `docs/changes/W2-59-CIT-P.md`); read such a file as it stands on the base with `git show w2/integrate:<path>`. You may read `tests/acceptance/W2-59/` (this ticket's acceptance tests and their README, which state the judge's new behaviour), run any test, and see results and failure messages; (d) the hidden half of any evaluation set, by whoever is measured by it. Never read or name the qualification oracle.
- **DEC-849, read refusals until W2-58 lands:** the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. **Count every read refusal you meet and give the count in your return.** Never read `.claude/settings.json`.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you need, do not work around it: return it as a package.
- Run everything in the foreground, one command after another; give long commands the tool's longest timeout. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag. Install nothing. Never `sudo`.
- **No copy of the repository:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it. A throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. A test that needs a repository builds a temporary one from scratch (pytest's temporary folder, single named files copied in) or from the dev tiers.
- Nothing of a test goes under a `.gov-runtime/` folder (DEC-673), in `~/.local`, or in `~/gov-os-workbench`. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder; never list, glob, search or write in `~/gov-os-workbench` yourself.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools, with literal absolute paths. No subagents that write. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- Never ask the owner anything and never notify anyone (DEC-850, DEC-855): a question is a package in your return.
- You use your model's full window; nobody asks you to stop or compact early (DEC-838).
- Your temporary folder is removed when your session ends: everything the lead needs is in your final message.

## What you read

- DEC-864 item 1, DEC-822 (item 3: the judge runs every declared check with its own interpreter and package; the per-command `PYTHONPATH` chooses only the code under test), DEC-835 (modules find repository files from the project root, never from their install path), DEC-579 (the kernel's two layouts: `template/governance/kernel/` in this repository, `governance/kernel/` in an adopted project, carried there by the copier template), DEC-491 (a rewrite after implementation carries `Rewrite-Reason:`), DEC-221, DEC-462, all in `docs/DECISION_REGISTER.md`.
- `tests/acceptance/W2-59/README.md` and its tests: how the judge now behaves (what the project supplies, what comes from the judge).
- The two earlier suites: `tests/acceptance/W1-26/` (README, `conftest.py`, `w1_26_support.py`, `test_w1_26_planted_defects.py`) and `tests/acceptance/W1-22/` (README, `conftest.py`, `w1_22_support.py`, `test_w1_22_canaries.py`); W1-26's and W1-22's ticket KPIs (`.tickets/`, read-only; find them by their `wbs_id`).
- The code the cases judge, as it stands (the authority family's call of the decision checker, the canary runner): read it with `git show w2/integrate:<path>` where the file is in the list of (c) above, freely otherwise.

## The three cases (the behaviour each keeps)

1. **W1-26 `tests/acceptance/W1-26/test_w1_26_planted_defects.py::test_planted_authority_defect_decision_checker_exception_not_swallowed`.** Behaviour kept: when the decision checker raises while `gov check` judges a project, the authority/role-limits family is not GREEN (RED or YELLOW: the exception is never swallowed). Today the case plants a raising `src/gov/decisions/checker.py` **in the judged project**; under DEC-822 item 3 the judge no longer imports the judged project's `src/gov`, so the plant never runs and the family is GREEN. **Revise it so the raising checker is planted in the judge's own code** (the code that runs `gov check`), never in the judged project's `src/gov/`. You choose how, within the rules above (no copy of the tree; something in the test's temporary folder that makes the judge's own decision checker raise, for example). **The case must prove its plant ran:** the test must show the planted raise was reached by the judge (a marker, or the exception's text in the output, or another observable), so it can never pass because nothing was planted. Leave the judged project as the suite builds it. Keep the case's name.
2. **W1-22 `tests/acceptance/W1-22/test_w1_22_canaries.py::TestCanaryRunner::test_lexical_canary_hits_after_reindex`** and
3. **`::test_semantic_canary_hits_after_reindex`.** Behaviour kept: after a reindex, the lexical and the semantic canaries hit. Today the fixture project holds no canary declarations and the cases expect the ones of the Gov OS install, found from the install path; under DEC-835 the runner reads them from the project, so they now report `FACET_UNAVAILABLE, unreadable canary declaration`. **Revise them so their fixture project carries the kernel's canary declarations as an adopted project carries them through the copier template** (DEC-579: under `governance/kernel/`), copied as single named files from `template/governance/kernel/` (no folder copy). The other cases of the class and file keep their fixtures as they are (for example `test_empty_project_canaries_fail_as_facet_unavailable` keeps its empty project): change the shared fixture builder only in a way that leaves every other case's fixture unchanged. Keep the cases' names.

For all three: no assertion is weakened or removed; no expectation is lowered; nothing else in the two suites changes, except the lines of each suite's README that describe these three cases (say there, in one line each, what changed and why, citing DEC-864). Proportion: STANDARD (DEC-221). Deterministic; no network.

If a revision cannot keep its behaviour without lowering an expectation, or needs a write outside `tests/acceptance/W1-26/` and `tests/acceptance/W1-22/`, do not guess: return it as a package (context; what happened; why it matters; options with consequence, cost and risk; recommendation and confidence; what it blocks).

## Run them

This is a rewrite after the implementation exists: the revised cases must **pass** on this worktree's code, and each must still **fail** where its behaviour breaks. Show both where you can without editing code: for W1-26, the run shows the plant was reached (the marker or message) and the family is RED or YELLOW; for W1-22, the canaries hit. Then run each of the two whole suites to its end (never `-x`), each in its own process:

    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -m pytest tests/acceptance/W1-26 -q -p no:cacheprovider -rs
    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -m pytest tests/acceptance/W1-22 -q -p no:cacheprovider -rs

Commit before you run the long whole-suite runs. Report each suite's counts and every red by name with its reason (a red you did not cause: name it, change nothing for it). Inside the sandbox, `gov` runs a private Ollama on the CPU: the semantic case may be slow; that is expected.

## Commit

Commit only the two folders, in one commit (a second commit only to correct the first, never an amend), with the trailers in the final block:

    git commit -m "W2-59 (DAEO-kh9l): W1-26's planted checker in the judge's own code, W1-22's canary fixture carries the kernel's declarations (DEC-864)" --trailer "Task: DAEO-kh9l" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-864, DEC-822, DEC-835" --trailer "Rewrite-Reason: DEC-822 item 3, DEC-835 (DEC-864)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W1-26 tests/acceptance/W1-22

Check `git log --oneline -2` and `git status --short` after it.

## Return

Your last message, complete in itself. In `evidence`: the sandbox check's result (first), your commit hash with its trailers, the `gov.__file__` line, and for each of the three cases its result and the observable that shows its plant or declarations were used. In `tests`: each suite's counts and every red by name. In `discoveries`: anything else in W1-22 or W1-26 that rests on the removed assumptions (name it; do not change it). Also give: the number of guard read refusals you met, and the `gov retrieve` questions you asked.

**The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

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
