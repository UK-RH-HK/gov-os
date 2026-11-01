You are a fresh independent test designer (MR-3). Ticket: DAEO-tgk2 (W2-76), profile STANDARD, run 3. You work only in
the tests worktree `/home/usain/gov-os-worktrees/W2-76-tests` on branch `w2/W2-76-tests` (DEC-963: one writer per
worktree; the lead merges your commit into `w2/W2-76`). Your one task: in eight existing acceptance-test helpers, add
one pass-through line each, under DEC-964 and DEC-956 item 2 (read both in `docs/DECISION_REGISTER.md`), lowering no
expectation.

## Step 0: the sandbox check (before any work; report it first)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-tgk2','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return, naming any file you made outside this worktree.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-tgk2`) and
`git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-76-tests` and
`w2/W2-76-tests`). If anything differs, stop and say so.

## The behaviour (the specification)

- W2-76 makes every `gov rebuild` on the machine take one machine-wide rebuild lock (`/tmp/gov-os-rebuild.lock` by
  default). The environment variable `GOV_REBUILD_LOCK`, where set, names another lock file to use instead (DEC-956
  item 2). The test harness sets it, for each pytest process, to a lock file of that process's own, so a suite's
  rebuilds of its temporary projects never queue behind a real rebuild elsewhere on the machine.
- Eight helpers build their child processes' environment **from scratch** (a literal dict), so the variable never
  reaches the rebuilds they start: those rebuilds take the machine's real lock, and the suites wait behind any real
  rebuild and pass their time limits (run 1's reds in W1-07, W1-27, W1-41, W2-69, W1-30, W2-50, W2-54).
- DEC-964 decides: in each of these eight places, **pass `GOV_REBUILD_LOCK` through to the child's environment when it
  is set in the runner's environment** (its value unchanged; nothing added when it is not set). One line per site:
  - `tests/acceptance/W1-07/w1_07_support.py` line 442 (the dict in `run_gov_with_code`)
  - `tests/acceptance/W1-27/w1_27_support.py` line 79 (the dict in `run_gov_with_code`)
  - `tests/acceptance/W1-27/test_w1_27_rebuild_r8_no_embeddings.py` line 144 (the dict in the `gov` fixture)
  - `tests/acceptance/W1-30/w1_30_support.py` line 185 (`sandbox_env`)
  - `tests/acceptance/W1-41/w1_41_support.py` line 419 (the returned dict)
  - `tests/acceptance/W2-50/w2_50_support.py` line 205 (`base_environment`)
  - `tests/acceptance/W2-54/w2_54_support.py` line 114 (`env`). **W2-64 is also changing this file on its own
    branch: touch only the one line here**, nothing else in the file (the second to merge merges back).
  - `tests/acceptance/W2-69/w2_69_support.py` line 121 (`base_environment`)
- Line numbers are as of commit f73ac139735f; find each dict by reading the file. Match each file's own idiom and
  comment density (a short trailing comment naming DEC-956 item 2 / DEC-964 is enough). The same pass-through form in
  all eight is best, for example a `**({...} if os.environ.get(...) else {})` entry, or the file's equivalent; check
  `os` is imported where you use it.
- **Nothing else changes:** no other line, no other file, no expectation, no time limit, no test removed or skipped.
  A suite whose tests set their own `GOV_REBUILD_LOCK` or their own lock (none known) keeps its own: if you find a
  helper where passing it through would change what a test judges, say so and leave that site as a package.
- If you find a ninth helper that builds a rebuild's environment from scratch, name it in your return; do not change
  it (it is outside the ticket's paths).

## Standing rules (read first)

- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-76/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-76/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
  (Your tests worktree is at the same commit as `/home/usain/gov-os-worktrees/W2-76`; run your checks with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-76-tests/src` from your worktree and quote that `gov.__file__` line.)
- **Your retrieval (DEC-963, DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading
  files at random, from the integration branch's store only, never this ticket's worktree store:
  `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json`. A large question is taken in
  batches (`--batch-size`, then `--continue <token>`), never one giant query. A code question uses the code-graph
  tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole
  graph. **P-R1:** drop unread any result under `src/gov/rebuild/`, `tests/unit/rebuild/test_w2_76*` or
  `tests/conftest.py`, and name in your return each such result you were served. You will hardly need it: the task is
  named above.
- **DEC-820 (c) and (d), the counterpart rule:** (c) you never read this ticket's implementation: the files
  `git diff --name-only w2/integrate...HEAD` names, other than acceptance tests. They are `src/gov/rebuild/**`,
  `tests/unit/rebuild/test_w2_76*` and `tests/conftest.py`. You may read the eight helpers above (they are tests, and
  yours to edit), the existing code as it stands on `w2/integrate` (`git show w2/integrate:<path>`), and run tests
  and read their results. (d) you never read the hidden half of any evaluation set.
- **DEC-849:** the guard may refuse some reads (searches that start at the repository root, `governance/project/` or
  `.claude/`). Take the refusal, never look for another form; search named folders instead. Count the refusals you
  met, in your return. Never read `.claude/settings.json`.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing
  started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase.
- **Protected material (DEC-820):** never read, print, search, diff or copy the held-out material's contents, and never
  type its path; never read or name the qualification oracle; never print a secret. Never write in `~/gov-os-workbench`;
  dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder (you need none).
- **Never copy the repository** or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of
  it). Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target, no here-document (`<<EOF`),
  no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Write files with the Write and Edit tools
  at literal absolute paths, and run them. A refused form is not retried in another disguise.
- No subagents that write. Install nothing: the guard refuses installs; raise any you need as a P1 in your return.
  No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- **Row W2-L423's rule (DEC-911):** anything you write under `.gov-runtime/` gives commit hashes as 12 digits, never
  the full 40, and never names the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Scratch budget (DEC-898):** your share is 1 GB and 50,000 files and folders, outside the tracked tree (of the
  ticket's 20 GB and 1,000,000). Keep pytest's own retention (never `--basetemp`), add
  `-o tmp_path_retention_policy=failed`, remove what you make as you go, and measure your temp folder
  (`du -s --inodes` and `du -sh`) before your checks and at the end; give the figures in `evidence`. Keep the
  temporary folder the launcher set; never set `TMPDIR`. Passing the budget: stop and return.
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).

## Check and commit

- Do **not** run the eight suites (they rebuild real projects for many minutes; the lead runs them under a held lock,
  outside the sandbox). Check instead:
  - `python3 -m py_compile` on each of the eight files;
  - collection only of the eight suites, to its end:
    `PYTHONPATH=/home/usain/gov-os-worktrees/W2-76-tests/src python3 -m pytest tests/acceptance/W1-07 tests/acceptance/W1-27 tests/acceptance/W1-30 tests/acceptance/W1-41 tests/acceptance/W2-50 tests/acceptance/W2-54 tests/acceptance/W2-69 --collect-only -q -p no:cacheprovider`
    (report its last line);
  - for each helper you can call without a rebuild, a throwaway script in your temp folder (not committed) that calls
    it with `GOV_REBUILD_LOCK` set and unset and shows the variable present with the same value, and absent; for any
    you cannot call cheaply, say so and show the diff line instead.
- `git diff --stat` must show eight files, one line added each (a line changed only where the dict's form needs it;
  say so).
- Commit only those eight files, in one commit, with the trailers in the final block:

      git commit -m "W2-76: the rebuild-lock override passed through the eight helpers that build a rebuild's environment (DEC-964)" --trailer "Task: DAEO-tgk2" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-956, DEC-964" --trailer "Rewrite-Reason: DEC-956 item 2" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

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

Right after the twelve fields, a section headed `guard_refusals:`, one line per refusal by the five-rule hook that you
met, or `guard_refusals: none`. Each line: `- <time> | <the command's form, one line, no secret or file contents> |
<the rule's reason as the hook gave it> | true or false-positive | <minutes it cost and what you did instead>`. A false
positive (the hook refused something none of its five rules is meant to stop) is worked round only by an equivalent
form that does what was meant, such as a script file; a true refusal is taken (DEC-849).

Then a section headed `brief_gaps:`, one line per thing you had to discover that this brief did not tell you, or
`brief_gaps: none`.

Then: the sandbox check (step 0), your commit's hash (12 digits), the eight lines you added, the checks' results, the
guard read refusals you met (DEC-849), whether you used `gov retrieve` (and any P-R1 result you dropped), and your
scratch figures.
Refused twice for the same call: stop and say so.
