# Brief A1: independent test designer, DAEO-4eux (W2-114), profile LITE, a test revision

You are a fresh independent test designer (MR-3). Ticket: `DAEO-4eux` (`W2-114`, "W1-28's whole-tree copy check reads code, not message text"), profile LITE, a test-revision ticket under the owner's named decision (DEC-906; the owner's named decision for this revision is DEC-982; its scope DEC-986). You work only in the worktree `/home/usain/gov-os-worktrees/W2-114` on branch `w2/W2-114`, and you are the only writer here. This ticket has no engineer and no product-code change: your revised test files are the whole of it.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-4eux','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (twelve fields), naming what happened. Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-4eux`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-114` and `w2/W2-114`). If anything differs, stop and say so.

## What happened

- W1-28's KPI success 4 (DEC-385) has a reading route: `whole_tree_copiers()` in `tests/acceptance/W1-28/w1_28_copy_check.py` parses every Python source under `tests/acceptance/` and reports each function that copies the whole tree of the repository (a whole listing followed by a copy, or a whole-tree route such as `copytree`, `git clone`, `git archive`, `git worktree`, `cp -r`, `rsync`, `tar` with the repository root as its source). W1-28's `test_w1_28_fixture_copies.py` and W1-50's `tests/acceptance/W1-50/test_w1_50_freeze_fixture_settings.py` both use it.
- On 2026-10-31 it refused a batch of six for nothing (DEC-977): W2-108's scope test, which copies nothing, held `pytest.skip(f"{REPO_ROOT} is not a git worktree")`. The module's `_analyse` takes any call whose arguments hold the root, then searches **every string constant inside that call** for a route word; the message's text " is not a git worktree" matched "git worktree", so the function was reported as a whole-tree copy. W2-108 changed its own message (commit `6c8afc7fd29a`); the check still reads message text, so the next such message refuses a close again.

## What you do (the ticket's KPI lines, in `.tickets/DAEO-4eux.md`)

1. **The module reads code, not message text.** In `w1_28_copy_check.py` (`_analyse` and what it calls), the text of `pytest.skip`, `pytest.fail` and assertion messages is no longer read as code: route words are looked for only in argument lists and in `subprocess`, `os.system` and copy calls. A test whose message names the repository root and the words of a route is not reported (DEC-982, DEC-385). How you read "argument lists" and the call set is yours, judged by the next point; an ambiguity that would make you choose between a false hit and a dropped true copy is a package, never a guess.
2. **Nothing lowered (DEC-906).** Every true whole-tree copy the check finds today it still finds. Measure it, before and after your change, on the real tree: the labels `whole_tree_copiers()` and `copiers()` return for `tests/acceptance/` (a small script file in your temp folder that imports the module and prints the sorted labels). The sets must be the same, except a function reported only because of message text, which you name with the message's line. Any other difference is a package. A form of these routes that the check does not find today (e.g. `cp -r` given as separate argv items) may be added if it lowers nothing and keeps the real tree's sets as above; name each such widening in the README.
3. **Planted cases, in W1-28's test file** (in the way its existing planted cases are built: a synthetic `tests/acceptance/W1-99/` folder under `tmp_path`): each of a `cp -r` of the root, a `shutil.copytree` of the root, a `git worktree add`, and a `git clone` of the repository, each in a test function, is still reported; and a function whose `pytest.skip` message names the root and the words "git worktree" (W2-108's old form: `pytest.skip(f"{REPO_ROOT} is not a git worktree")`) is not. A `pytest.fail` message and an `assert ..., <message>` naming the root and a route word, not reported, are welcome (one case may hold several; LITE: no combinatorial expansion).
4. **The README.** `tests/acceptance/W1-28/README.md` states what the reading route reads (which calls and which arguments) and why message text is left out, with `Rewrite-Reason: DEC-982`; it maps each of the ticket's three success KPI lines and two failure lines to its cases (one line each) and says how a run from this worktree exercises this worktree's code (the `PYTHONPATH` line). Nothing else in the README is lowered.
5. **Every existing case keeps its expectation.** No case deleted, skipped, xfailed, narrowed or loosened, in W1-28's or W1-50's files.

## Your paths (write nothing else)

- `tests/acceptance/W1-28/w1_28_copy_check.py`
- `tests/acceptance/W1-28/test_w1_28_fixture_copies.py`
- `tests/acceptance/W1-28/README.md`

Nothing else: not W1-50's file, not `tests/acceptance/W2-114/`, nothing under `src/`, `template/`, `.claude/`, `.rulesync/`, `.tickets/`, `docs/` or `governance/`. A change needed anywhere else is a package.

## What you read

- The ticket file `.tickets/DAEO-4eux.md` (read-only): its KPI lines and `allowed_paths`.
- In `docs/DECISION_REGISTER.md`: DEC-982, DEC-986, DEC-385, DEC-906, DEC-977, DEC-866.
- W1-28's folder (the module, the test file, the README, the conftest), W1-50's `test_w1_50_freeze_fixture_settings.py`, and `git show 6c8afc7fd29a` (W2-108's own fix, the old message in its diff).
- **Use memory first (DEC-836), from the integration branch's store only:** `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` for what you need to know before reading files at random; for what changed since that store's last refresh, `git show w2/integrate:<path>`. Never one giant query or context (DEC-860): a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph (DEC-859). If retrieve fails (STORE_MISSING, or the sandbox refuses the store), say so and read files directly.
- **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths (its `allowed_paths` outside `tests/acceptance/`: there are none for this ticket), and name in your return any such result you were served.

## Reads open, writes closed (DEC-820, Policy 2)

You read freely: the whole repository, git history, other worktrees. Only four things are refused:
- (a) secrets and keys, never printed;
- (b) the contents of the held-out qualification material (its file names may be seen); never read or name the qualification oracle; the check itself never opens, hashes or compares `governance/project/held-out.yaml`, and your change keeps it so;
- (c) the counterpart's work on this ticket: you never read this ticket's implementation (the files `git diff --name-only w2/integrate...HEAD` names, other than your own tests; for this ticket there is no implementation besides your own files);
- (d) the hidden half of any evaluation set, by whoever is measured by it.

Until W2-58 lands, the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`) (DEC-849): take the refusal, never look for another form, search named folders instead, and **count the refusals you met** in your return. Writes stay inside your paths.

## The code under test (DEC-732, word for word)

**In this worktree, every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-114/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-114/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.

## Running the tests

- Red first: before changing the module, add the planted cases and run W1-28's test file; the "not reported" planted case must fail for the reason it states (the message read as code), and the four true copies must pass. Record that.
- Then, after your change: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-114/src python3 -m pytest tests/acceptance/W1-28/test_w1_28_fixture_copies.py tests/acceptance/W1-50/test_w1_50_freeze_fixture_settings.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`, to the end, never with `-x`: every case green. Then W1-28's whole folder the same way (`tests/acceptance/W1-28`), to the end; report its counts and name any red, with whether it is red before your change too.
- Run everything in the foreground, one command after another; nothing started in the background is ever read. A run longer than about 9 minutes is split by file. Do not set `TMPDIR` yourself (the sandbox sets it). Keep pytest's own retention; never `--basetemp`.
- **Commit before any long suite run**, so work is never lost.

## Commits

Commit only your paths, with `git commit -m "<subject>" --trailer "Task: DAEO-4eux" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-986, DEC-982, DEC-385, DEC-906, DEC-977" --trailer "Rewrite-Reason: DEC-982" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`. `Implements:` holds decision ids only. One commit or a few; no amend, no rebase, no reset, no `git checkout` of another commit, no `git clean`, no push, merge or tag. Before each commit, check `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. After each commit, `git log --oneline -2` and `git status --short`.

## Standing rules

- **Your scratch budget (DEC-898):** 15 GB and 750,000 files and folders (your share of the ticket's 20 GB / 1,000,000), outside the tracked tree (the sandbox's temp folder and anything untracked). Clean up what you create as soon as it is no longer needed. Measure (`du -s --inodes`, `du -sh` of your temp folder) before your long runs and at the end, and give the figures in `evidence`. Passing the budget: stop the heavy work, clean what you can, return.
- **Protected material:** never read the held-out material's contents and never print a secret. Never write in `~/gov-os-workbench`; never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **Row W2-L423's rule (DEC-911):** anything you write under `.gov-runtime/` and your return use commit hashes of 12 digits, never the full 40, and never the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule".
- **No copy of the tree:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it. Your planted cases are source **text** written into a synthetic folder and parsed, never run against this repository. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it. No file of a programme under any `.gov-runtime/` folder.
- **The guard's command forms:** no shell variable as a write target (use literal paths), no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; write anything longer as a script file with the Write tool (in your temp folder) and run that file. Write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is raised as a P1 in your return (DEC-957). Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- **Never** run `gov close`, `gov adopt`, `gov pause` or `gov rebuild`; never run `docs/plan/tools/validate_s1.py`. Never ask or notify the owner (no question box, no `owner-ping`).
- **On an authentication or access error** (401, 403, "Failed to authenticate"): stop and return with status `AUTH_REQUIRED`.
- **If the guard or the sandbox refuses something you needed**, do not disguise the same call: a false positive (the hook refused something none of its five rules is meant to stop) may be worked round only by an equivalent form that does what was meant (the Read/Grep tools, or a script file); a true refusal is taken and returned as a package. **Refused twice for the same call: stop and say so; no third try.**
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

In those fields give: the step 0 result; your commits (12-digit hashes) with their trailers; the `gov.__file__` line; the red result before the module change; the real tree's `whole_tree_copiers()` and `copiers()` labels before and after (counts, and every difference with its reason); each run's counts (passed/failed/skipped); the README's path; every widening; the count of guard read refusals (DEC-849); whether you used `gov retrieve` and what it served (P-R1); your scratch measures; any untracked scratch file you could not remove, with its path.

Right after the twelve fields, two sections:
- `brief_gaps:` one line per gap, or `brief_gaps: none`. A gap is anything you had to discover, look up or ask that this brief, the ticket or the skills you loaded did not tell you. Each line: `- <what was missing> | <where it belonged: common brief, this ticket's part, the ticket file, skill <name>, or a tool> | <minutes it cost, measured or estimated, so marked>`.
- `guard_refusals:` one line per refusal by the five-rule hook that you met, or `guard_refusals: none`. Each line: `- <time> | <the command's form, one line, no secret or file contents> | <the rule's reason as the hook gave it> | true or false-positive | <minutes it cost and what you did instead>`.

Refused twice for the same call: stop and say so.
