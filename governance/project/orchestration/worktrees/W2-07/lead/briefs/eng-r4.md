# Brief: engineer, W2-07 (DAEO-r9ss), round 2 (DEC-923, DEC-924): what the work-without-a-task gate counts as measured

You are a fresh engineer. Ticket: `DAEO-r9ss` (W2-07, "gov close by ticket class; the commit gates before any test; complete, tracked repair tickets; a share for every close"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-07` on branch `w2/W2-07`. Round 1 is built and merged. **Your job: implement round 2's rule (DEC-923 item 2) in the close's work-without-a-task gate until the ticket's acceptance tests pass**, in about 30 to 60 lines.

## Step 0, before any work: the sandbox check (report it first in your return)

1. `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-r9ss','w').write('x')"` must FAIL.
2. `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (1) wrote the file or (2) failed, stop there and return with status SANDBOX_FAILED, naming what happened (do not delete anything).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-r9ss`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-07` and `w2/W2-07`) and `git rev-parse --short=12 HEAD` (expect `fe7b9ffe0d64` at your start). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- **Reads are open, writes are closed (Policy 2, DEC-820).** You read freely: the whole repository, git history, other worktrees, and what retrieval and search return. Refused to you: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen), and never read or name the qualification oracle; **(c) the counterpart's work on this ticket: you never read this ticket's acceptance-test code, that is, nothing under `tests/acceptance/W2-07/` (no file there, README, conftest and support included, by any tool, and not `git show`/`git diff` of it either).** You may run those tests and see their names, results and failure messages. **(d) the hidden half of any evaluation set, by whoever is measured by it.**
- **Guard read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take a refusal as a refusal, never look for another form or spelling; search named folders instead. **Count every such refusal and give the count in your return.**
- **Memory first (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: take a large question in batches (`--batch-size <N>`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. If that tool is not available to you, use Grep and Read on named files. Say in your return whether and how you used `gov retrieve` (if it answers `FACET_UNAVAILABLE`, say so and read named files).
- Run everything in the foreground, one command after another, each within the Bash tool's 10-minute foreground limit (split long suites by folder or file). Nothing you start in the background is ever read. **Time:** about 90 minutes. Commit your work before you run any long suite. If the work does not fit, commit what passes and return with what remains, precisely.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no amend, no rebase in this worktree. No push, merge or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree, and never `gov rebuild --no-embeddings`.
- Never read `.claude/settings.json`, in this worktree or anywhere.
- Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder (DEC-723).
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository); copy single named files only, never `governance/project/`; a test that needs a repository builds a temporary one from scratch. No clone, copy or file of a programme under any `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables (`$VAR`, loop variables) in Bash write targets and suite paths: write files with the Write and Edit tools and literal absolute paths; name each suite path literally. Never `python3 -c` with braces in its code (DEC-409): write a script file under `.gov-runtime/scratch/` instead. No subagents that write. Install nothing: a tool you need is returned as a package.
- **Row W2-L423's rule (owner, standing, DEC-911).** Under `.gov-runtime/` (your scratch files and your return, which the lead keeps there), write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule". In code and unit tests, never put such a keyword next to a full 40-hex id.
- **Reports in commits of their own (DEC-924 item 2):** you commit code and unit tests only; never mix a report into a commit.
- **Never ask or notify the owner** (no question box, never `owner-ping`). A question goes into your return as a package.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package.
- **The machine (DEC-847, DEC-780):** before each run of more than a handful of test files, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` does not exist and that the 1-minute load is below 20 (`awk '{print $1}' /proc/loadavg`); if not, wait (`sleep 60` in a loop, inside one foreground command of at most 10 minutes, repeated). Every suite runs to its end, never with `-x`.
- **Scratch budget (DEC-898):** the lead and all its workers together have 20 GB and 1,000,000 files and folders outside the tracked tree; **your share is 4 GB and 200,000 files and folders.** Keep the temp folder the sandbox gives you (its `TMPDIR`); do not set another one. Keep pytest's own retention (three base folders); never a per-run `--basetemp`. Pass `-o tmp_path_retention_policy=failed` on every pytest run (DEC-905: a passing test's temp folder is removed as it ends; it changes no result). Clean up as you go. Before every heavy run and at the end, measure your scratch (`du -s --inodes` and `du -sh` of your temp folder and of the worktree's untracked and ignored files) and give the figures in your return's `evidence` line. If you pass your share: stop the heavy work at once, clean what you can, and return with the measure and its cause.

## What you read

- The ticket file `.tickets/DAEO-r9ss.md` (read-only): **KPI 3 as amended, the round-2 KPI (the fourth success line), failure lines 3 and 4.**
- The card, `docs/plan/WAVE_2_WBS.md` §2, W2-07, its "Round 2 (owner, DEC-923)" note.
- `docs/DECISION_REGISTER.md`: **DEC-923 item 2 (the rule)**, **DEC-924 items 1 and 3 (your files)**, DEC-896 item 1 (changed by DEC-923), DEC-891 (the records), DEC-906 (`acceptance_exemptions`; a `Role: owner` trailer is only text until W2-44), DEC-734 (accepted history), DEC-490 and DEC-500 (work without a task), DEC-866 (supersession), DEC-135 (proportion).
- The code: `src/gov/close/gates.py` (round 1's rule, under "Decision records"), `src/gov/close/command.py` (gate (h): the line that computes `recorded` and the `gate(_check_unmeasured, ...)` call, and `_check_unmeasured`), `src/gov/close/history.py` (how the trailer gate reads `accepted_history`: `accepted_history`, `owner_decision`, `register_entries`, `judged_history`), `tests/acceptance/W1-01/w1_01_support.py` function `acceptance_exemptions` (how W1-01 reads that list), `tests/unit/close/test_decision_records.py` (round 1's unit tests of the rule; keep them green).
- The register's status-line forms the rule meets: `ACCEPTED (owner, ...)`, `ACCEPTED (delegated, ...)`, `ACCEPTED (orchestrator, delegated under ...)`, `ACCEPTED (...) · ... · **Changed by:** DEC-n`, `SUPERSEDED by DEC-n (<date>; it was ACCEPTED, owner, ...)` (DEC-876's), and never-accepted ones: `PROPOSED`, `REJECTED (...)`, a `SUPERSEDED by DEC-n (...)` that does not say it was ACCEPTED.
- Real commits of this repository that the rule judges (`git show --stat <commit>`): `8f56ada1bcbe` (path map, delegated DEC-903), `65039414fb72` (subject names DEC-876, later superseded), `4166d8d9ca0b`, `b772b2fefeed`, `8d625805c343` (records with ticket files), `c9a086786444` (`Role: owner`, tests; on `acceptance_exemptions`), `611955faffaa` (records plus `docs/assessment/`: unmeasured unless `accepted_history` names it).

## What to build: the rule (DEC-923 item 2)

The work-without-a-task gate (gate (h)) subtracts from the commits it judges those counted as measured. Round 1 counts a `Task: decision-record` commit that changes only `docs/plan/`, the prompts, the briefs, `governance/project/orchestration/`, the register and the path map, and names (subject or `Implements:`) an ACCEPTED **owner** decision not superseded. Round 2:

1. **Measured by its decision:** a decision-record commit (`Task: decision-record`) that
   - changes **only governance records**: DEC-891's records (`.tickets/`, `docs/checkpoints/`, `docs/close/`, `docs/probes/`, the register the path map names, the plan files, `governance/project/orchestration/`) beside the prompts, the briefs and the path map; and
   - **names an ACCEPTED decision, the owner's or a delegated one, also when that decision was later superseded or changed.** A decision never ACCEPTED does not count.
2. **Measured by an owner-committed list:** a commit that `acceptance_exemptions` or `accepted_history` names, each under its ACCEPTED owner decision, read as the trailer gate reads `accepted_history` and as W1-01 reads `acceptance_exemptions` (an exact full commit id), whatever paths it changes.
3. **A `Role: owner` trailer alone measures nothing** (DEC-906): never read the trailer as measuring.
4. **Any other path** (code, tests, the kernel, `docs/assessment/`) keeps a decision-record commit unmeasured unless a list names it.

Failure lines (each must still refuse; never make the gate fail open): a decision-record commit outside an ACCEPTED decision counted as measured; a commit counted as measured by its `Role: owner` trailer alone, or a code, test or kernel commit counted as measured that no owner-committed list names.

**Where the rule leaves a reading open, take the stricter one** (the one that keeps a commit unmeasured) and name it in your return. In particular: a commit that names several decisions; whether an `acceptance_exemptions` entry's decision must also name the commit; an `accepted_history` entry whose owner decision was later superseded (the trailer gate refuses it today; do not widen the trailer gate).

**One function the orchestrator calls (lead's constraint).** The orchestrator's gate-(h) tool (`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/unmeasured_gate.py`, read it) runs the pinned judge's `gov.close.gates.decision_records(root, others, settings)` and subtracts what it returns, as the close's gate (h) does. Keep that function and its signature (round 1's unit tests call it too), and make the set the close subtracts before `_check_unmeasured` and the set that one call returns the same, so the tool and the close cannot disagree. If you find a reason not to, say so plainly in your return.

## Where you write (DEC-924 item 3, an owner exception beside W2-57 in flight)

- **Only:** `src/gov/close/gates.py`; **gate (h)'s line in `src/gov/close/command.py`** (the `recorded` subtraction before `_check_unmeasured`, nothing else in that file); `src/gov/close/history.py` (its readers, only if needed); and **new** unit tests `tests/unit/close/test_w2_07_*.py`.
- **W2-57 owns `src/gov/close/serial.py` and `tests/unit/close/test_serial*`.** Never touch them, nor any other file of `src/gov/close/` or `tests/unit/close/` (round 1's `test_decision_records.py` included: if your change turns one of its cases red, do not edit it; name it with the KPI and decision that changes it, as a package).
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Proportion (DEC-135): about 30 to 60 lines of code; no code for edge cases beyond the rule. Say how far you are from it.

## Run

- The ticket's acceptance tests, until they pass: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src python3 -m pytest tests/acceptance/W2-07 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs -n 6`. Today 12 fail (all in `test_w2_07_decision_records.py`, each refused `WORK_WITHOUT_TASK`) and 57 pass.
- Then, to their end: `tests/unit/close` (with `-n 6`), and the acceptance suites that judge `gov close`'s commit gates: `tests/acceptance/W2-01`, `tests/acceptance/W2-53`, and `tests/acceptance/W1-30` in parts by file (with `-n 6`). Each with `-o tmp_path_retention_policy=failed`.
- **Your own check on this repository (no close):** write a script under `.gov-runtime/scratch/eng-r4/` that does what the orchestrator's tool does, from this worktree's `src` and with `root` this worktree, for `DAEO-5j8b`, `DAEO-pl6k` and `DAEO-r9ss`, and give each unmeasured count and commit. The lead expects 0, 0 and 1 (`611955faffaa`, until the owner's `accepted_history` entry for it lands).
- At the end: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header` ends with no collection error; quote its last line.

## Commit

Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. Commit only your paths (`git add <named paths>`, then `git commit ... -- <paths>`), with the trailers in the final block:

    git commit -m "DAEO-r9ss (W2-07): <subject>" --trailer "Task: DAEO-r9ss" --trailer "Role: engineer" --trailer "Implements: DEC-923, DEC-924" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After each commit, show `git log --oneline -2` and `git status --short`.

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

Put in them: the sandbox check's result (first, in `evidence`); your commits with their trailers (12-digit hashes); the lines added and removed against the estimate; each suite with its counts and every red with its cause; your check's three counts with the commits; the readings you took where the rule is open; whether `decision_records` and the close's subtraction are the same set; any superseded decision you met (old, new, file and test or line); the `gov.__file__` line; the collect-only last line; the guard read refusals you met (count); whether you used `gov retrieve`; your scratch measure.

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
