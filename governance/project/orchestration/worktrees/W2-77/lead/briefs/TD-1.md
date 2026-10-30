You are a fresh independent test designer (MR-3). Ticket: `DAEO-b6hm` (W2-77), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-77` on branch `w2/W2-77`. You write the ticket's acceptance tests from its KPI lines and its sources, before the implementation, and you show them red. Your time budget is about 90 minutes.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-b6hm','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return, saying which.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-b6hm`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-77` and `w2/W2-77`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-77/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-77/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree. No push, merge or tag.
- **Reads (DEC-820, Policy 2):** you read freely: the whole repository, git history, other worktrees. Refused to you: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read, print, search, diff or copy it, never type its path; never read or name the qualification oracle); (c) **the counterpart's work on this ticket: you never read this ticket's implementation** (the files `git diff --name-only w2/integrate...HEAD` names, other than your own tests; today there is none, and you write before it exists); (d) the hidden half of any evaluation set, by whoever is measured by it.
- **Guard read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count every refusal you meet and give the count in your return. Never read `.claude/settings.json`. Name files under `governance/project/` one by one.
- **Memory (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-77/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Say in your return whether you used `gov retrieve`, and how often.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target (use literal paths); no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; put anything longer in a script file under your own temp folder with the Write tool, and run that file. Write files with the Write and Edit tools and literal absolute paths. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree add` of this repository, `git clone` of it) anywhere. A test that needs a repository builds a temporary one from scratch (inside the test's own `tmp_path`); a throwaway stand-in copies single named files, never `governance/project/`. No clone, copy or programme file under any `.gov-runtime/` folder. Never write in `~/gov-os-workbench`; never list, glob or search it.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- **Never run `python3 -m gov.close.nightly`, `python3 -m gov.close.batch`, `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree** (DEC-915 item 4). Your tests run them only against temporary repositories they build.
- No subagents that write. Install nothing: a tool you need is returned as a package. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- **Disk (DEC-898):** the lead's budget for the ticket is 20 GB and 1,000,000 files and folders outside the tracked tree; **your share is 5 GB and 250,000 files and folders.** Keep pytest's own temp retention (never `--basetemp`), run with `-o tmp_path_retention_policy=failed`, and remove every temporary repository your tests make when they end (pytest's `tmp_path` does that with the retention option). Do not set `TMPDIR`: keep the sandbox's own temp folder. Measure your temp use at the end (`du -sh` and `du -s --inodes` of your temp folder) and give the figures in your return.
- **Machine quiet windows (DEC-933, DEC-780):** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` or `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` exists, run no suite (at most a single test file); check before each run with `ls`, and wait with short checks until it is gone.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` and in your return, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Files held by other tickets running now:** `tests/unit/close/**` (W2-67), `src/gov/**/*.py` (W2-05), `src/gov/secrets/**`, `tests/unit/secrets_check/**`, `src/gov/retrieval/measure.py`, `src/gov/launch/**`. You write none of them.
- **The git hooks are uninstalled until W2-08:** before your commit check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`.
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package.

## What you read

- The ticket file `.tickets/DAEO-b6hm.md` (read-only): its KPI lines, its `allowed_paths` and its sources; its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-77"), and section 0 ("Rules for every ticket").
- Row W2-M406 in `docs/plan/WAVE_2_LIST.md`.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-939 (item 5), DEC-915 (item 4), DEC-890, DEC-803, DEC-866, DEC-941, DEC-905, DEC-820, DEC-462, DEC-221, DEC-491.
- W2-68's probe record `docs/probes/DAEO-2gc7/PR-DAEO-2gc7.md`, finding F1 (the fixture that reproduced the loss), and W2-66's probe record `docs/probes/DAEO-c1uz/PR-DAEO-c1uz.md` (its R8).
- The public interfaces you test, as they stand on the base (`git show w2/integrate:<path>` if you want the base's text): the nightly command `python3 -m gov.close.nightly <branch> --root <project> [--coverage] --json` (its envelope, exit codes and its record `docs/close/nightly/NR-<stamp>-<head12>.json`, as `src/gov/close/nightly.py`'s module text and W2-66's README describe them), and the batch command `python3 -m gov.close.batch run <ticket>...` (W2-68's README). W2-66's and W2-68's acceptance folders (`tests/acceptance/W2-66/`, `tests/acceptance/W2-68/`) hold fixture projects and helpers you may import (never copy) to build a project the nightly and the batch can run on, with a tiny suite so that a night runs in seconds.

## The behaviour to test (the lead's design note, as text)

The KPI lines (the ticket file):
- S1: After its run, gov.close.nightly removes only its own clone, by its exact path (`git worktree remove --force <that path>`), and never runs a repo-wide `git worktree prune` [DEC-939 item 5, row W2-M406].
- S2: A second worktree of the project whose folder is hidden or unreadable while the nightly runs (unmounted, permission-denied, moved and restored) keeps its registration and its staged index afterwards; the fixture that reproduced W2-68's reviewer's F1 now keeps them [DEC-939 item 5, P-W2-68-PRUNE].
- S3: If the removal of its own clone fails, the nightly removes only that clone's own administrative entry (by its exact name under the common git directory), or reports the failure in its record; it never touches another worktree's entry [DEC-939 item 5, DEC-866].
- S4: Everything else the nightly does is unchanged: its selection, its runs, its record and its verdict [DEC-915, DEC-890].
- F: Any repo-wide prune left in the nightly; another worktree's registration or index lost; a clone's failed removal hidden.

The design note (the behaviour the implementation will have):

1. **Only the clone, by its exact path.** The clone the nightly adds (a detached worktree of the branch's head, a folder named `tree` inside a fresh temporary folder) is removed by that exact path, `git worktree remove --force <that path>`, and by nothing else.
2. **No repo-wide prune.** No `git worktree prune` runs anywhere in the nightly or in anything it calls, and nothing in the nightly prunes or removes worktree entries by pattern, by age or by a missing folder.
3. **Its own entry, known from the clone itself.** The clone's administrative entry is known from the clone's own `.git` file (`gitdir: <common dir>/worktrees/<name>`), never guessed from the folder's name: every clone is a folder called `tree`, and git may give a later one another entry name (`tree1`, ...) while some other worktree holds `tree`.
4. **If the removal fails** (git's exit is not 0, or the entry is still there afterwards): only that clone's own administrative entry goes, and only when that entry is confirmed to be the clone's (directly under the common directory's `worktrees/`, its own `gitdir` file naming the clone's `.git`). No other entry is touched in any case.
5. **A failure is never hidden.** Whenever the removal by path did not succeed (whether or not 4 then removed the entry), the night's record carries a `cleanup` key: `{"ok": false, "clone": <the clone's path>, "entry": <the entry's path, or null when unknown>, "entry_removed": true|false, "error": <git's message or the reason>}`, and one line naming the clone and the failure goes to standard error. A night that ends in an exception (no record written) still writes that line.
6. **Nothing else changes:** the selection, the runs, the bisect, the record (no `cleanup` key when the removal succeeded, every other key as today), the verdict, the exit code and the envelope. A failed clean-up does not change the verdict. The batch's record, built from the night's, carries the same `cleanup` key when present.

## The cases the lead asks for (at least these; FULL is thorough, but no combinatorial expansion)

All in temporary repositories built from scratch, with a tiny suite so that a night runs in seconds.

- One case per KPI line (S1 to S4 and F).
- **W2-68's F1 as a case:** a second worktree of the project holding a staged change has its folder moved aside while the nightly runs, then restored; and separately its folder made unreadable (permission denied), then restored. Afterwards its registration (`git worktree list --porcelain` of the main repository), its administrative folder and its staged index (the staged change, seen from inside it) are kept. Restore permissions in a `finally`, so pytest can remove the folder.
- **A failed removal of the clone:** the clone's removal by path is made to fail (one fixture that makes git's single `--force` removal fail is a clone that is locked, e.g. by a test of the tiny suite that runs `git worktree lock` on the worktree it runs in; another is a stand-in `git` first on `PATH` that fails only `worktree remove` and passes everything else to the real git; choose what is deterministic). Then: no other worktree's entry is touched — **including a registered worktree whose folder is also called `tree`, registered before the night so that it holds the entry name `tree`** and the clone gets another — and the failure is in the night's record (the `cleanup` key of item 5) and on standard error; the clone's own entry is gone or the record says it is not (`entry_removed`).
- **No repo-wide prune, shown by behaviour:** a stale registration of a missing folder (a worktree added, its folder deleted), planted before the run, is still registered after it.
- **The batch's route** (`python3 -m gov.close.batch run <ticket>`), which reaches the nightly, also keeps a hidden second worktree's registration, administrative folder and staged index (F1's own fixture, through W2-68's support).
- **The nightly's selection, runs, record and verdict are unchanged** on the same fixture: on a green night and on a red one, the record's keys are exactly today's keys (no `cleanup` key when the removal succeeds), the verdict, the exit code and the envelope are as today, and the clone is gone afterwards (its folder and its registration).

## What you write

- Only inside `tests/acceptance/W2-77/` (a new folder). No throwaway implementation is left in the tree. Edit no other file, `tests/acceptance/serial-only.txt` included unless a case truly cannot run in parallel (then say so in the README and the return).
- Behaviour through public interfaces (the two commands, their records, git's own view of the repository), never internals. Deterministic, no network.
- A `README.md` that maps each KPI line to its tests, gives the expected red reason of each (and names any case expected green before the implementation, as a guard of unchanged behaviour), and says how the suite runs this worktree's own `src/` (the `gov.__file__` check).
- Red first: run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-77/src python3 -m pytest tests/acceptance/W2-77 -q -p no:cacheprovider -o tmp_path_retention_policy=failed` to the end (never `-x`); the cases fail for the reason the README states. Give the counts and the time it took.
- An ambiguous KPI line or a dispute is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

Commit only `tests/acceptance/W2-77/`, in one commit, with the trailers in the final block:

    git commit -m "<subject>" --trailer "Task: DAEO-b6hm" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-939, DEC-915" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then check `git log --oneline -2` and `git status --short`.

## Return

Your commit's hash (12 digits); the test count; the KPI lines with their tests; the red reason as you saw it, per case; the `gov.__file__` line; every earlier test you rewrote (expected: none); any package; your sandbox check; your guard refusals count; whether you used `gov retrieve`; your temp-folder figures.

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

Your return gives these twelve fields first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.
