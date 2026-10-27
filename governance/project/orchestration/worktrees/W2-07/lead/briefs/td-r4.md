# Brief: independent test designer, W2-07 (DAEO-r9ss), round 2 (DEC-923, DEC-924): decision records and the owner-committed lists

You are a fresh independent test designer (MR-3). Ticket: `DAEO-r9ss` (W2-07, "gov close by ticket class; the commit gates before any test; complete, tracked repair tickets; a share for every close"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-07` on branch `w2/W2-07`.

Round 1 of this ticket is built and merged; its acceptance tests (`tests/acceptance/W2-07/`) pass. The owner has widened one rule for round 2 (DEC-923 item 2), and the ticket file's KPI 3 is amended and a round-2 KPI added. **Your job: revise the ticket's acceptance tests, chiefly `tests/acceptance/W2-07/test_w2_07_decision_records.py`, so that they state round 2's rule, one case per line of the rule, each change carried by a commit with `Rewrite-Reason: DEC-923`, with no expectation lowered; and show which cases are red against this worktree's code today, and why.** Tests first: nobody has implemented round 2 yet.

## Step 0, before any work: the sandbox check (report it first in your return)

1. `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-r9ss','w').write('x')"` must FAIL.
2. `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (1) wrote the file or (2) failed, stop there and return with status SANDBOX_FAILED, naming what happened (do not delete anything).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-r9ss`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-07` and `w2/W2-07`) and `git rev-parse --short=12 HEAD` (expect `b6bc7773` at its start). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
  W2-07's support already gives every process it starts this worktree's `src/` (its README, "How the tests run"); keep it that way and say so in your return.
- **Reads are open, writes are closed (Policy 2, DEC-820).** You read freely: the whole repository, git history, other worktrees, and what retrieval and search return. Refused to you: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen), and never read or name the qualification oracle; **(c) the counterpart's work on this ticket: you never read this ticket's implementation, that is, any file that `git diff --name-only w2/integrate...HEAD` names other than the acceptance tests under `tests/acceptance/W2-07/`** (today that list is empty: you read the code as it stands on `w2/integrate`; if the list is not empty when you look, the files it names are closed to you). You may run the implementation and read its output, refusals and failure messages: that is the public interface. **(d) the hidden half of any evaluation set, by whoever is measured by it.**
- **Guard read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take a refusal as a refusal, never look for another form or spelling; search named folders instead. **Count every such refusal and give the count in your return.**
- **Memory first (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: take a large question in batches (`--batch-size <N>`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. If that tool is not available to you, use Grep and Read on named files. Say in your return whether and how you used `gov retrieve` (if it answers `FACET_UNAVAILABLE`, say so and read named files).
- Run everything in the foreground, one command after another, each within the Bash tool's 10-minute foreground limit (`-n 6` is fine for W2-07). Nothing you start in the background is ever read. Your budget is about 90 minutes of work; commit as soon as your revision is done, before any long run. Return only after your commits exist.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no amend, no rebase in this worktree. No push, merge or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- Never read `.claude/settings.json`, in this worktree or anywhere.
- Never write in `~/gov-os-workbench`. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder; you never list, glob, search or write in the workbench yourself (DEC-723).
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository). A throwaway stand-in copies single named files, never `governance/project/`; a test that needs a repository builds a temporary one from scratch (as W2-07's support does). No clone, copy or file of a programme under any `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents, unresolvable variables and loop variables in Bash write targets and suite paths: write files with the Write and Edit tools and literal absolute paths; name each suite path literally. Never `python3 -c` with braces in its code (DEC-409): write a script file under `.gov-runtime/scratch/` instead. No subagents that write. Install nothing: a tool you need is returned as a package.
- **Row W2-L423's rule (owner, standing, DEC-911).** Under `.gov-runtime/` (your scratch files and your return, which the lead keeps there), write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule". (Full ids inside the temporary test repositories your tests build are fine; they never land under `.gov-runtime/`.)
- **Reports in commits of their own (DEC-924 item 2):** not your case (you commit tests only), but never mix a report into a commit.
- **Never ask or notify the owner** (no question box, never `owner-ping`). A question goes into your return as a package.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package.
- **Nobody runs `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree** (the fixtures run `gov close` in their own temporary projects; that is fine).
- **The machine (DEC-847, DEC-780):** before each run of more than a handful of test files, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` does not exist and that the 1-minute load is below 20 (`awk '{print $1}' /proc/loadavg`); if not, wait (`sleep 60` in a loop, inside one foreground command of at most 10 minutes, repeated). Never `-x`: every suite runs to its end.
- **Scratch budget (DEC-898):** the lead and all its workers together have 20 GB and 1,000,000 files and folders outside the tracked tree; **your share is 4 GB and 200,000 files and folders.** Keep the temp folder the sandbox gives you (its `TMPDIR`); do not set another one. Keep pytest's own retention (three base folders); never a per-run `--basetemp`. Pass `-o tmp_path_retention_policy=failed` on every pytest run (DEC-905: a passing test's temp folder is removed as it ends; it changes no result). Clean up as you go. Before every heavy run and at the end, measure your scratch (`du -s --inodes` and `du -sh` of your temp folder and of the worktree's untracked and ignored files) and give the figures in your return's `evidence` line. If you pass your share: stop the heavy work at once, clean what you can, and return with the measure and its cause.
- Your temporary folder may be removed when your session ends: everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-r9ss.md` (read-only): **KPI 3 as amended, the new round-2 KPI (the fourth success line), and failure lines 3 and 4.**
- The card, `docs/plan/WAVE_2_WBS.md` §2, W2-07: the "Round 2 (owner, DEC-923)" note.
- `docs/DECISION_REGISTER.md`: **DEC-923 (item 2, your mandate)**, DEC-924 (items 1 and 3), DEC-896 item 1 (changed by DEC-923), DEC-891 (which paths are records; which list entries are the owner's own), DEC-906 (the `acceptance_exemptions` list; a `Role: owner` trailer is only text until W2-44), DEC-734 (accepted history: an entry under an ACCEPTED owner decision that names the commit), DEC-866 (supersession propagates), DEC-491 (`Rewrite-Reason:`), DEC-221 (STANDARD proportion).
- The register's own status-line forms, which your fixtures should copy rather than invent: an owner decision (`ACCEPTED (owner, <date>, ...)`), a delegated one (for example DEC-903's or DEC-890's: `ACCEPTED (delegated, orchestrator, <date>, ...)`), a later-superseded one (for example DEC-876's: `SUPERSEDED by DEC-880 (<date>; it was ACCEPTED, owner, <date>, ...)`), an accepted one carrying a `· **Changed by:** DEC-n` note, and never-accepted ones (`PROPOSED`, `REJECTED (...)`).
- How the two owner-committed lists are read today, the readings DEC-923 tells gate (h) to follow:
  - `accepted_history`, as the close's trailer gate reads it (DEC-734): read `src/gov/close/history.py` as it stands on `w2/integrate` (`git show w2/integrate:src/gov/close/history.py`), the public reading of an entry: its commit, and its decision an ACCEPTED owner decision of the register whose text names the commit;
  - `acceptance_exemptions`, as W1-01 reads it: `tests/acceptance/W1-01/w1_01_support.py`, function `acceptance_exemptions` (an exact full commit id, a `DEC-<n>` decision).
- `tests/acceptance/W2-07/README.md` (round 1's designer's specification of the interface, accepted by the owner in DEC-904 item 7 and DEC-903; assumptions A4 and A5 on the accepting decision and on how a commit "names" a decision), `tests/acceptance/W2-07/test_w2_07_decision_records.py` and `w2_07_support.py`: how a fixture project reaches the work-without-a-task gate, how a decision-record commit is written there, and how a refusal is observed.
- Real commits of this repository that the rule judges, as examples of the shapes (read them with `git show --stat <commit>`): `8f56ada1bcbe` (a path-map record under a delegated decision), `65039414fb72` (a record naming a decision later superseded), `4166d8d9ca0b`, `b772b2fefeed`, `8d625805c343` (records that also change ticket files), `c9a086786444` (a `Role: owner` commit that also changes tests, named on `acceptance_exemptions`), `611955faffaa` (records plus `docs/assessment/`, not a record).

## The rule you test (DEC-923 item 2, as the ticket's KPI 3 and round-2 KPI state it)

The work-without-a-task gate of `gov close` refuses (`WORK_WITHOUT_TASK`, naming the commit) a commit in the ticket's range that names no task and changes the ticket's work (its acceptance tests, a path inside its allowed paths, its own ticket file). Round 2 says which such commits count as measured, and so are not refused:

1. **Measured by its decision:** a decision-record commit (`Task: decision-record`) that
   - changes **only governance records**: DEC-891's records (`.tickets/`, `docs/checkpoints/`, `docs/close/`, `docs/probes/`, the register the path map names, the plan files, `governance/project/orchestration/`) beside the prompts (`governance/project/prompts/`), the briefs (`governance/project/briefs/`) and the path map; and
   - **names an ACCEPTED decision**, the owner's or a delegated one, also when that decision was later superseded or changed. A decision never ACCEPTED does not count.
2. **Measured by an owner-committed list:** a commit that `acceptance_exemptions` or `accepted_history` names, each under its ACCEPTED owner decision, read as the trailer gate (for `accepted_history`) and W1-01 (for `acceptance_exemptions`) read them, whatever paths it changes.
3. **A `Role: owner` trailer alone measures nothing** (DEC-906: a trailer is only text until W2-44).
4. **Any other path** (code, tests, the kernel, `docs/assessment/`) keeps a decision-record commit unmeasured unless a list names it.

## Your batch (MR-3: only `tests/acceptance/W2-07/`)

One case per line of the rule, each in a temporary repository as the existing cases build them, through `gov close` only:

- **Measured (red today, expected green after round 2):**
  - a record-only decision-record commit under a **delegated** decision;
  - one under a decision **later superseded** (the register's `SUPERSEDED by DEC-n (...; it was ACCEPTED, ...)` form); a later-changed one (`· **Changed by:**`) if you judge it adds a line the others do not (say whether it is green already);
  - one that also changes **a ticket file** (`.tickets/<id>.md`, the closing ticket's own file is the telling shape: it is the ticket's work);
  - where you see value, one that changes another DEC-891 record folder (`docs/checkpoints/`, `docs/close/`, `docs/probes/`) or `governance/project/orchestration/`;
  - a commit named on **`accepted_history`** under its ACCEPTED owner decision, which changes a non-record path of the ticket's work (code or tests) and names no task;
  - a commit named on **`acceptance_exemptions`** under its ACCEPTED owner decision, likewise.
- **Unmeasured (they must still refuse `WORK_WITHOUT_TASK`, naming the commit):**
  - a decision-record commit under an ACCEPTED decision that also changes **any non-record path**: keep round 1's code, tests and kernel cases, and add `docs/assessment/` (the `611955faffaa` shape);
  - a **`Role: owner`** decision-record commit, with a non-record path, that **no list names** (failure line 4: measured by its trailer alone);
  - a decision **never ACCEPTED** (keep round 1's `PROPOSED` case; add `REJECTED` if you judge it adds a line);
  - where you see value, the list's own limits, as the two readings above state them: an entry whose decision is not an ACCEPTED owner decision (a delegated or a proposed one) measures nothing; for `acceptance_exemptions`, an abbreviated commit id measures nothing.
- **Revise round 1's cases where round 2 changes what they state** (for example, round 1's fixture puts `Role: owner` on every decision-record commit; the round-1 measured case must not now pass by that trailer): each revision with `Rewrite-Reason: DEC-923`, **no expectation lowered**. Every round-1 case that holds a limit of the rule stays (or is strengthened).
- **The README:** update the KPI map (KPI 3 as amended, the round-2 KPI, failure lines 3 and 4) with each new case and its expected red reason today; state any reading of the rule you had to choose (an assumption, numbered like the existing ones) and the source you read it from. Where the decision leaves a reading open and you could test either way, do not pin it: name it in the README and your return.
- **Behaviour and sources only:** your tests drive `gov close` and read its JSON result, the path map, the register and git. They name no function or module of the code to be written (DEC-462).
- If you find a case outside `tests/acceptance/W2-07/` that enforces a superseded part of DEC-896 item 1, do not change it: name it (old decision, new decision, file and test).
- If a line of the rule cannot be tested without lowering an expectation, or you find a dispute with a KPI, do not bend the test: return it as a package.

## Check and commit

- Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`.
- Commit with only your paths (`git add <named paths>`, then `git commit -m "<subject>" <trailers> -- <paths>`), the trailers in the final block:

      git commit -m "DAEO-r9ss (W2-07): <subject>" --trailer "Task: DAEO-r9ss" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-923, DEC-924" --trailer "Rewrite-Reason: DEC-923" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

  One commit, or one per file group if that reads better. After each commit, show `git log --oneline -2` and `git status --short`.
- **Run, each in its own process, after your commits** (CLOSE-RUNNING absent and load below 20 before each; each with `-o tmp_path_retention_policy=failed`):
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src python3 -m pytest tests/acceptance/W2-07 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs -n 6`;
  - once at the end: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header` (no collection error; quote its last line).
  Give the counts; for each red, its test id, its failure message's first line, and whether it is the red your README expects (the rule's new measured lines) or something else.

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

Put in them: the sandbox check's result (first, in `evidence`); your commits with their trailers (12-digit hashes); each case added or revised, one line each (what it asserts; revised cases: before and after); the readings you chose (assumptions) and any you left open; the W2-07 counts and every red with its reason; the `gov.__file__` line; the collect-only last line; other cases enforcing a superseded decision; the guard read refusals you met (count); whether you used `gov retrieve`; your scratch measure.

## The return block (word for word)

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

The twelve fields come first, each as a labelled line, with any payload after them. Refused twice for the same call: stop and say so.
