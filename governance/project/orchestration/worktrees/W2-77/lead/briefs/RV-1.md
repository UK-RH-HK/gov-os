You are a fresh reviewer. Ticket `DAEO-b6hm` (W2-77), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-77` on branch `w2/W2-77`, at the head `e96abbef2597`, and its acceptance tests pass. You probe that head for behaviour the tests miss. You write nothing. **A fault here loses work.**

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-b6hm','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return, saying which.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-b6hm`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-77` and `w2/W2-77`), and `git rev-parse --short=12 HEAD` (expect `e96abbef2597`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-77/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-77/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. You write nothing, so no commit of yours will exist: return when your findings are complete. Your time budget is about 90 minutes.
- Write no file of the repository and make no commit. No `git checkout` of another commit, no `git reset`, no `git clean` in this worktree. No subagents that write. Install nothing. No push, merge, rebase or tag.
- **Reads (DEC-820, Policy 2):** you read everything, tests and code alike. Refused to you: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read, print, search, diff or copy it, never type its path; never read or name the qualification oracle); (c) the counterpart's work applies to the test designer and the engineer, not to you: reviewers read everything; (d) the hidden half of any evaluation set, by whoever is measured by it.
- **Guard read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count every refusal you meet and give the count in your return. Never read `.claude/settings.json`. Name files under `governance/project/` one by one.
- **Memory (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-77/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Say in your return whether you used `gov retrieve`, and how often.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target (use literal paths); no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces. You have no Write tool: keep probe scripts short, or write them with plain shell into your own temp folder using literal paths. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree add` of this repository, `git clone` of it) anywhere. A probe that needs a repository builds a temporary one from scratch in your temporary folder (you may import the acceptance support `tests/acceptance/W2-77/w2_77_support.py` and W2-66's and W2-68's support, never copy them), and removes it at its end. No clone, copy or programme file under any `.gov-runtime/` folder. Never write in `~/gov-os-workbench`; never list, glob or search it.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- **Never run `python3 -m gov.close.nightly`, `python3 -m gov.close.batch`, `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree** (DEC-915 item 4). Only your temporary repositories.
- **Disk (DEC-898):** the lead's budget for the ticket is 20 GB and 1,000,000 files and folders outside the tracked tree; **your share is 3 GB and 150,000 files and folders.** Keep pytest's own retention, run with `-o tmp_path_retention_policy=failed`, remove every temporary repository as soon as you are done with it. Do not set `TMPDIR`. Measure your temp use at the end and give the figures.
- **Machine quiet windows (DEC-933, DEC-780):** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` or `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` exists, run no suite (at most a single test file); wait with short checks until it is gone.
- **Row W2-L423's rule (DEC-911):** in your return, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return.

## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines.

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

From brief A3 (reviewer), word for word:
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.

## What you read

- The ticket file `.tickets/DAEO-b6hm.md`: its KPI lines and its `allowed_paths` (`src/gov/close/nightly.py`, the clean-up only; `tests/unit/close/test_nightly_cleanup*`); its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-77").
- The sources: row W2-M406 (`docs/plan/WAVE_2_LIST.md`); W2-68's probe `docs/probes/DAEO-2gc7/PR-DAEO-2gc7.md` (F1) and W2-66's `docs/probes/DAEO-c1uz/PR-DAEO-c1uz.md` (R8).
- The decisions in `docs/DECISION_REGISTER.md`: DEC-939 (item 5), DEC-915 (item 4), DEC-890, DEC-803, DEC-866, DEC-413, DEC-500, ADR-0001 (`docs/adr/ADR-0001-threat-model.md`).
- The change: `git diff w2/integrate...HEAD` (the acceptance tests and README in `tests/acceptance/W2-77/`, the clean-up in `src/gov/close/nightly.py`, the builder tests in `tests/unit/close/test_nightly_cleanup*`), and the code it calls: `src/gov/close/batch.py`'s route into `nightly.night`, `src/gov/close/repo.py`'s git helper, `src/gov/close/command.py`'s test runs.

## The design note (the lead's, as text)

Ticket `DAEO-b6hm` (W2-77), row W2-M406, DEC-939 item 5, DEC-915 item 4. A plan in behaviour, not code.

## Today

`python3 -m gov.close.nightly <branch> --root <project>` adds a detached worktree of the branch's head (the
"clone", a folder named `tree` inside a fresh temporary folder), runs the night there, and at its end removes
the clone with `git worktree remove --force <clone>`, deletes its temporary folder, and then runs a repo-wide
`git worktree prune`. That prune drops the registration and the administrative folder (with its index) of every
worktree of the repository whose folder the process cannot see at that moment (moved, unmounted, unreadable).
W2-68's batch (`python3 -m gov.close.batch run`) reaches the same code (W2-68's probe, F1).

## After this ticket

1. **Only the clone, by its exact path.** The clone the nightly adds is removed by that exact path,
   `git worktree remove --force <that path>`, and by nothing else.
2. **No repo-wide prune.** No `git worktree prune` runs anywhere in the nightly or in anything it calls, and
   nothing in the nightly prunes or removes worktree entries by pattern, by age or by a missing folder.
3. **Its own entry, known from the clone itself.** The clone's administrative entry is known from the clone's
   own `.git` file (`gitdir: <common dir>/worktrees/<name>`), read when the clone has been added, never guessed
   from the folder's name: every clone is a folder called `tree`, and git may give a later one another entry
   name (`tree1`, ...) while some other worktree holds `tree`.
4. **If the removal fails** (git's exit is not 0, or the entry is still there afterwards, so its result cannot
   be confirmed): only that clone's own administrative entry goes, the exact folder read in 3, and only when that
   entry is confirmed to be the clone's (it lies directly under the common directory's `worktrees/`, and its own
   `gitdir` file names the clone's `.git`). No other entry is touched in any case. If the entry cannot be read,
   cannot be confirmed as the clone's, or is still there after its removal, nothing more is removed.
5. **A failure is never hidden.** Whenever the removal by path did not succeed (whether or not 4 then removed
   the entry), the night's record carries a `cleanup` key: `{"ok": false, "clone": <the clone's path>,
   "entry": <the entry's path, or null when unknown>, "entry_removed": true|false, "error": <git's message or the
   reason>}`, and one line naming the clone and the failure goes to standard error. A night that ends in an
   exception (no record written) still writes that line, and the exception is kept unchanged.
6. **Nothing else changes:** the selection, the runs, the bisect, the record (no `cleanup` key when the removal
   succeeded, every other key as today), the verdict, the exit code and the envelope. A failed clean-up does not
   change the verdict. The batch's record, built from the night's, carries the same `cleanup` key when present.
7. **Unchanged on purpose, outside the clean-up:** the `git worktree add --detach --force <fresh path> <head>`
   (its path is new in a fresh temporary folder), the bisect's `start`/`run`/`reset` inside the clone (bisect
   state is per worktree), and how the nightly's git calls build their environment (W2-05's ground).

## Where

`src/gov/close/nightly.py`, the clean-up of `night` only; builder tests in new files
`tests/unit/close/test_nightly_cleanup*`. About 20 lines.

## What you probe for

Above all, **any path that prunes, or removes, another worktree's registration, administrative folder or index.** Probe each, running the code on temporary repositories:

- the clean-up and its fallback;
- a failed or partial removal (git fails, the folder half gone, the `.git` file missing or unreadable, the entry already gone, the entry's `gitdir` naming something else);
- a removal by a guessed name (a worktree whose folder is also called `tree`, an earlier dead clone's entry, entry names `tree`, `tree1`, ...);
- `git worktree add --force` at the start;
- the bisect's start and reset in the clone;
- the batch's route into the nightly (`python3 -m gov.close.batch run`);
- every other git command the nightly runs against the shared repository.

Also: a failed removal that is hidden (no record line, no standard-error line, an exception that swallows it); anything else of the night changed (the selection, the runs, the record, the verdict, the exit code, the envelope); and the ordinary cases a worktree is hidden (moved, unmounted, permission-denied) while a night runs.

**A finding that shows one of the ticket's failure lines fails the review:** any repo-wide prune left; another worktree's registration or index lost; a clone's failed removal hidden.

Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such. Run `tests/acceptance/W2-77` and the builder tests once yourself, to their end, and give the counts.

## Return

The head you probed, and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and its two lines (`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`). Say also what you probed and found sound. You repair nothing (MR-4).

Then **the probe record's content**, ready for the lead to write to `docs/probes/DAEO-b6hm/PR-DAEO-b6hm.md`, in the form of `docs/probes/DAEO-2gc7/PR-DAEO-2gc7.md` (read it for the form; the probe gate reads it): a title, the verdict line (`**Verdict: pass.**` or `**Verdict: fail.**`, with the classification of the findings on one line), the head probed, the method (read, ran, probed), the findings with their two lines each, what was found sound, and notes for the lead and the auditor. Use your session id as that record does.

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

Your return gives these twelve fields first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them (the probe record's content goes after them). Refused twice for the same call: stop and say so.
