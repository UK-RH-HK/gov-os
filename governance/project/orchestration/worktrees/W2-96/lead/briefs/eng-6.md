# Brief: engineer, W2-96 (DAEO-ouet), run 2, review 3's fix (DEC-970, DEC-916)

You are a fresh engineer. Ticket: `DAEO-ouet` (W2-96, the opaque acceptance runner `gov accept`), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-96` on branch `w2/W2-96`. You build the code to the specification and its KPIs, never to the tests (DEC-957); your test-driven development is your own unit tests.

**Where things stand.** Run 2 is built (`41b9fdddf109`, `917aba42cd9c`: R8 to R13), its 100 acceptance cases pass through `gov accept`, and the unit tests pass (62). Review 3 probed it and found one behaviour that fails open (V1): run 2's new removal, which replaced run 1's tolerant one, stops at its first error. The lead turned it into the addendum below. A test designer writes review 3's cases in parallel; the lead merges them after you return, then resumes this session for one acceptance run.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ouet','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (never delete such a file; name it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-ouet`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-96` and `w2/W2-96`), and `git rev-parse --short=12 HEAD` (expect `382e6d8fba8c`). If anything differs, stop and say so.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src` set **per command** (never in a session's `--settings` env). Show it once with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -c "import gov; print(gov.__file__)"` and quote the line.
- **Policy 2 (DEC-820):** reads are open, writes are closed. Refused to you: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read, print, search, diff or copy the held-out file under `governance/project/`, never type its path, never read or name the qualification oracle); **(c) this ticket's acceptance tests: you never read `tests/acceptance/W2-96/`** (here, in `/home/usain/gov-os-worktrees/W2-96-tests`, or on branch `w2/W2-96-tests`), by any tool — no `cat`, `Read`, `Grep`, `git show`, `git diff` of it; you may run them and see their names, results and failure messages; (d) the hidden half of any evaluation set.
- **DEC-849:** until W2-58 lands the guard still refuses some reads (searches starting at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form; search named folders instead, and count the refusals you met in your return. Never read `.claude/settings.json`.
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src timeout 90 python3 -m gov.cli.main retrieve "<question>" --json` (this worktree's store, rebuilt in run 1). Known: inside the sandbox that call can hang on the embedder's network call; try it once, and if it times out, say so and search named folders under `src/gov/` instead. Do not run `gov rebuild` yourself. Never one giant query or context (DEC-860): a large question in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph (DEC-859). Drop unread any result under `tests/acceptance/W2-96/`.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository); a test that needs a repository builds a temporary one from scratch. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only. No clone, copy or programme file under any `.gov-runtime/` folder. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Write files with the Write and Edit tools at literal absolute paths; put anything longer in a script file in your session's own temporary folder (the one the launcher set; `.gov-runtime/scratch/eng/` is refused to this role) and run it by its literal path; a command with `$TMPDIR` in it is refused, so write the path out. Never `cd` into a subfolder of the repository. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. No subagents that write. Install nothing (an install you need is a P1 escalation in your return).
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits, never 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Budget (DEC-898):** your share is 5 GB and 250,000 files and folders outside the tracked tree. Keep pytest's own temp retention (never a per-run `--basetemp` for your suite runs); run with `-o tmp_path_retention_policy=failed`. Your temp folder is the one the launcher set; clean up what you make as you go; measure at the end (`du -sh`, `du -s --inodes`) and give the figures.
- If the guard or the sandbox refuses something you need, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try (AR-6).**

## What you read

- The ticket file `.tickets/DAEO-ouet.md` (read-only): its KPI lines, its `allowed_paths` and its body (DEC-970).
- The code as it stands: `src/gov/accept/` (the clean-up's removal in `runner.py` above all), `tests/unit/accept/`.
- The lead's addenda: `/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/design.md`, `design-r1.md`, `design-r2.md` (R8 to R13), which still hold except where review 3's addendum below differs.

## Review 3's addendum (behaviour only; it overrides the earlier notes where they differ)

The design note, R1 to R7 and run 2's R8 to R13 still hold; where they differ, this holds.

- **R14 (the clean-up tolerates concurrent changes; review 3's V1).** The private folder is removed in every path even when a process the run cannot stop (one a test started in a session of its own, such as a nested `gov accept`) changes it meanwhile, or removes it first: an entry already gone is passed over, a folder found not empty is emptied again, and no single entry stops the removal of the rest (a bounded number of passes, then whatever error remains is passed over too). A run stopped by SIGINT, SIGTERM or SIGHUP still ends with 128 plus the signal (R12) whatever the clean-up met; a run that was not stopped is reported as its results say, never turned into `crash` by an entry another process removed. Nothing of the run stays in the caller's `TMPDIR`. Depth still never matters (R10), and the three signals are still held during the clean-up (R9).
- **R15 (the clean-up's time grows with the entries; review 3's V2, riding along).** Removing a folder whose thousands of sibling folders sit side by side takes time in proportion to the number of entries, not its square: 8,000 empty sibling folders are removed in a few seconds at most, comparable to a plain recursive removal.

How review 3 reproduced V1: a planted test runs a nested `gov accept` on a nested planted project in a session of its own (the acceptance harness starts nested runs this way; eight other suites here also start own-session processes); the nested test writes about 3,000 files and sleeps about 1 s; SIGTERM goes to the outer `gov` once the nested `gov`'s removal has begun, or to both `gov`s at once. In about one run in three the outer `gov` ended `crash`, exit 4, with test-named folders left in the caller's `TMPDIR`: the removal stopped at the first entry another process had removed ("file not found"). Run 1's removal, which passed over errors, gave 143 and nothing left in 12 of 12. Review 3 also measured the removal of 1,000 / 2,000 / 4,000 / 8,000 sibling folders at 0.39 / 2.48 / 8.99 / 22.66 s (quadratic).

Points that keep this failing closed: R8 to R13 unchanged; nothing printed from the child; a stopped run never exits 0.

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/accept/**` and `tests/unit/accept/test_w2_96*.py` (every new file's basename starts `test_w2_96_`). Not `src/gov/check/commands.py` this time.
- Never `src/gov/cli/main.py`, never `tests/acceptance/**` (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Proportion (DEC-135): only R14 and R15. Review 3's row V3 (signal windows at the very start and very end of `gov`) is a Wave 3 row: do not build it.
- Unit tests first (TDD): R14 (an entry removed by another process during the removal is passed over; a folder refilled meanwhile is emptied again; a stopped run keeps 128+N; an unstopped run is not turned into `crash`), R15 (8,000 sibling folders), with R10's deep chain still passing. Run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -m pytest tests/unit/accept -q -p no:cacheprovider -o tmp_path_retention_policy=failed` to the end, never `-x`.
- **Commit before any acceptance run.** Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. Trailers in the final block:

      git commit -m "W2-96 (DAEO-ouet): review 3, the clean-up tolerates concurrent changes and is linear in its entries (DEC-970)" --trailer "Task: DAEO-ouet" --trailer "Role: engineer" --trailer "Implements: DEC-970, DEC-959, DEC-317" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

  `Implements:` holds only ids the register holds (DEC-927). After every commit: `git log --oneline -2` and `git status --short`.

## Steps

1. Build R14 and R15 with unit tests, run your unit tests to the end, commit.
2. Run the current acceptance tests once as a regression check, reading results only: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -m gov.cli.main accept DAEO-ouet --json` (quote the JSON and the exit code). Review 3's new cases are not on this branch yet. If it does not pass, run the folder once through pytest for the failing names and one-line messages (`... -m pytest tests/acceptance/W2-96 -q -p no:cacheprovider -o tmp_path_retention_policy=failed --tb=line`), fix the code to the specification, commit, and run again; at most three acceptance runs in all.
3. Return. The lead resumes this session after merging review 3's acceptance cases, for one acceptance run.

## Return

Your last message, complete in itself. Refused twice for the same call: stop and say so. The twelve fields come first, each as a labelled line, any payload after them:

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

In `evidence` also: the sandbox check, your commits' 12-digit hashes, the `gov.__file__` line, the lines added and removed, whether you used `gov retrieve`, the guard read refusals you met (count), and your scratch measure. After the twelve fields, a `brief_gaps:` section (one line per thing you had to discover that this brief did not tell you, with minutes it cost, or `brief_gaps: none`).
