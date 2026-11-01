# Brief: independent test designer, W2-108 (DAEO-zoex), resume under DEC-977

You are a fresh independent test designer (MR-3). Ticket: `DAEO-zoex` (`W2-108`, "Retrieval checks the stores' freshness once per run"), profile STANDARD. You work only in the tests worktree `/home/usain/gov-os-worktrees/W2-108-tests` on branch `w2/W2-108-tests` (DEC-963). You never write the ticket's own worktree (`/home/usain/gov-os-worktrees/W2-108`). This is a one-test rewrite: the ticket's code does not change.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-zoex','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK (run them in your worktree).
If (a) wrote the file or (b) failed, stop there and return, saying which.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-zoex`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-108-tests` and `w2/W2-108-tests`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-108/src` set **per command** (never in a session's `--settings` env). — For you, "this worktree" is the tests worktree: use `PYTHONPATH=/home/usain/gov-os-worktrees/W2-108-tests/src` per command.
- **Retrieval (DEC-836, DEC-963):** use `gov retrieve` for what you need to know before reading files at random, and only from the integration branch's store: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (a read). Never this ticket's worktree's store. For what changed on `w2/integrate` since the store's refresh, read `git show w2/integrate:<path>`. **Never one giant query or context (DEC-860):** take a large question in batches (`--batch-size`, then `--continue <token>`). **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph.
- **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths: `src/gov/retrieval/semantic.py`, `src/gov/retrieval/lexical.py`, `tests/unit/retrieval/test_w2_108*`, `docs/research/W2-108-freshness-once.md`. Name in your return every such result you were served (DEC-820 (c)).
- **Reads open, writes closed (DEC-820, Policy 2).** You read freely, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen; `governance/project/held-out.yaml` is a path you may name in code, not a file whose contents you need), and never read or name the qualification oracle; **(c) the counterpart's work on this ticket: you never read this ticket's implementation** — the files `git diff --name-only w2/integrate...w2/W2-108` names other than `tests/acceptance/W2-108/**`; you need none of them for this task; **(d) the hidden half of any evaluation set**, by whoever is measured by it. Other tickets' tests (W1-28's, W1-50's) are open to read.
- **Read refusals until W2-58 lands (DEC-849):** the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count the refusals you met and name them in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target; no here-document (`<<EOF`), no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; put anything longer in a script file under your scratch with the Write tool, and run that file. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository). Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Never write `.gov-runtime/**` outside `.gov-runtime/scratch/**`. No clone, copy or programme file under any `.gov-runtime/` folder (DEC-673). Install nothing (a tool you need is returned as a P1 package). No subagents that write.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token (call it "row W2-L423's rule").
- **Your scratch budget (DEC-898):** your share is 2 GB and 100,000 files and folders, outside the tracked tree. Use the sandbox's own temp folder where `gov launch` sets one (keep it and count it), else `TMPDIR=/tmp/gov-os-lead-W2-108`. Keep pytest's own retention (no `--basetemp`). Measure it (`du -s --inodes`, `du -sh`) at the end and give the figures in your return.
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package.
- Never ask or notify the owner (no question box, no `owner-ping`): a question is a package in your return.

## What is wrong (DEC-977)

The ticket's branch was merged, but its close was refused: one of its acceptance tests, `tests/acceptance/W2-108/test_w2_108_scope.py::test_w2_54_is_not_changed_by_this_ticket`, is read by W1-28's whole-tree copy check as a copy of the repository's whole tree that the check cannot run on a synthetic root. With it present these are red (the lead reproduced them at the current head; they pass without it):

- `tests/acceptance/W1-28/test_w1_28_fixture_copies.py::test_every_whole_tree_copy_is_made_by_a_fixture_the_check_runs` ("these functions copy the whole tree of the repository and cannot be run by the check: [...]. Make each a module-level function with a parameter `root=REPO_ROOT` that leaves governance/project/held-out.yaml out by its path, or limit it to named paths (DEC-385)");
- `tests/acceptance/W1-50/test_w1_50_freeze_fixture_settings.py::test_the_two_whole_tree_fixtures_are_found` ("these whole-tree copies cannot be run on a synthetic root"), and W1-50's four cases there parametrised on this test (they end in an `IndexError` in `w1_28_copy_check.run_copier`, because the test takes no root parameter).

The lead's reading (check it yourself in `tests/acceptance/W1-28/w1_28_copy_check.py`, `_analyse`): the test copies nothing. It only runs `git log` and `git status` limited to named paths. But its skip call `pytest.skip(f"{S.REPO_ROOT} is not a git worktree")` names the repository root and holds the words "git worktree", which the check's `_SHELL_ROUTE` pattern takes for a whole-tree route (`git worktree`). Read DEC-385 in `docs/DECISION_REGISTER.md`, W1-28's `w1_28_copy_check.py` and `test_w1_28_fixture_copies.py`, and W1-50's `test_w1_50_freeze_fixture_settings.py`, to see what they require.

## What you do

1. Rewrite that one test so that W1-28's and W1-50's checks no longer count it as a whole-tree copy, in DEC-385's form: it stays limited to the named paths it needs (W2-54's tests and the context check's declarations, as today), and nothing in it reads as a whole-tree route over the root. The smallest change that does this is preferred (for example, a skip message that no longer pairs the root with a route's words); if you judge a module-level function with `root=REPO_ROOT` that leaves `governance/project/held-out.yaml` out by its path is the right form instead, say why.
2. **The test keeps checking exactly what it checks today:** the same paths, the same `git log` and `git status` assertions, the same skip condition. Lower nothing. Touch no other test, in this folder or elsewhere; never W1-28's or W1-50's tests or check. If the README names the skip message or the test, update it to match.
3. If W1-28's check can only be satisfied by weakening the test, stop and return it as a package. If you judge W1-28's check itself is wrong to flag this (a false positive), name it in `discoveries` with the line it comes from; do not change it.
4. Run, to the end, never with `-x`, with `TMPDIR` as above:
   - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-108-tests/src python3 -m pytest tests/acceptance/W1-28/test_w1_28_fixture_copies.py tests/acceptance/W1-50/test_w1_50_freeze_fixture_settings.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed`: all green, and W1-50's parametrised cases no longer name the W2-108 test (or name it only if they pass);
   - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-108-tests/src python3 -m pytest tests/acceptance/W2-108/test_w2_108_scope.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed`: the rewritten test still passes or skips exactly as before (in this worktree it can run; note that your branch carries the ticket's history, so it should pass);
   - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-108-tests/src python3 -m pytest tests/acceptance/W2-108 --collect-only -q -p no:cacheprovider --no-header`: no collection error.
   Show `PYTHONPATH=/home/usain/gov-os-worktrees/W2-108-tests/src python3 -c "import gov; print(gov.__file__)"` in your return.

## Commit

Commit only your test paths, in one commit, with the trailers in the final block (DEC-182, DEC-476, DEC-491):

    git commit -m "W2-108: the W2-54 scope test in DEC-385's form (W1-28's whole-tree check)" --trailer "Task: DAEO-zoex" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-385, DEC-977" --trailer "Rewrite-Reason: DEC-385 (DEC-977)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then check `git log --oneline -2` and `git status --short` (your tree clean).

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

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

After the twelve fields: the sandbox check's result; your commit's 12-digit hash; the diff of the test, in words; the runs' counts; whether you used `gov retrieve` and how often; every P-R1 result you were served; the read refusals you met (DEC-849); a section `guard_refusals:` (one line per refusal: time | the command's form | the hook's reason | true or false-positive | minutes it cost), or `guard_refusals: none`; and your scratch measure. Refused twice for the same call: stop and say so.
