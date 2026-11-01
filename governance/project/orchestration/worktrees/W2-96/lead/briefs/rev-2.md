# Brief: reviewer (FULL, read-only), W2-96 (DAEO-ouet), review 2 (the second and last, DEC-413)

You are a fresh reviewer. Ticket `DAEO-ouet` (W2-96, the opaque acceptance runner `gov accept`), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-96` on branch `w2/W2-96`, at the head `ea5728df2d9a`, and its acceptance tests pass. You probe that head for behaviour the tests miss. You write nothing in the repository.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ouet','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (never delete such a file; name it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-ouet`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-96` and `w2/W2-96`), and `git rev-parse --short=12 HEAD` (expect `ea5728df2d9a`; the full id `git rev-parse HEAD` gives is the probe record's `probed_commit`). If anything differs, stop and say so. Over review 1's head `6ec6cbd6e158` the head adds: the engineer's fixes `d8ac34ff71de` (review 1's addendum, below) and `720a26fd4d7d` (a line's counts are only of tests that ran), the lead's checkpoint record `ea5728df2d9a`, and, the test designer's review cases `3955f72177b6` merged by the lead in `382ef3b6`.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. You write nothing, so no commit of yours will exist: return when your findings are complete.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no commit, no merge, no push, no tag. Write no file of the repository. No subagents that write. Install nothing.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src` set **per command** (never in a session's `--settings` env). Quote `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -c "import gov; print(gov.__file__)"`.
- **Policy 2 (DEC-820):** you read everything, tests and code alike. Refused to you: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read, print, search, diff or copy the held-out file under `governance/project/`, never type its path, never read or name the qualification oracle); (c) for the two workers, each other's work — not for you, the reviewer reads both; (d) the hidden half of any evaluation set.
- **DEC-849:** until W2-58 lands the guard still refuses some reads (searches starting at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form; search named folders instead, and count the refusals you met. Never read `.claude/settings.json`.
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -m gov.cli.main retrieve "<question>" --json`; never one giant query (DEC-860: batches with `--batch-size`, then `--continue <token>`); code questions by the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted (DEC-859).
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of it). A probe that needs a repository builds a temporary one from scratch in your temporary folder (the one the launcher set). Never write in `~/gov-os-workbench`. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. A probe script you need goes in your temporary folder (written with the Write tool at a literal absolute path), never in the repository.
- **Row W2-L423's rule (DEC-911):** write commit hashes as 12 digits in your return, except `probed_commit`, which is the full id; never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- Never `cd` into a subfolder of the repository: the sandbox leaves a `.claude/` folder there (review 1 left one in `tests/acceptance/`). Work from the worktree's top with full paths. `rm` is refused by the permission layer in this non-interactive session: do not try it; name your probe folders in your return instead.
- **Tests run no more than this (DEC-959 item 1):** you re-run no suite; you read the tests, the code and the lead's results, and you run your own probes.
- Budget: your share is 2 GB and 50,000 files and folders; clean up your probe folders.
- If the guard or the sandbox refuses something you need, do not work around it: say so in your return. **Refused twice for the same call: stop and say so; no third try (AR-6).**

## What you read

- The ticket file `.tickets/DAEO-ouet.md`: its KPI lines and its `allowed_paths` (`src/gov/accept/**`, `tests/unit/accept/test_w2_96*`, and the test designer's `tests/acceptance/W2-96/`).
- The sources: DEC-959 (items 6 and 7), DEC-957, DEC-820 (c), DEC-317, MR-3 in `docs/DECISION_REGISTER.md`; `governance/project/orchestration/packages/ROLES-RESEARCH-1.md` §2.7; `src/gov/cli/main.py`'s docstring (the command-module convention, the envelope, the exit codes).
- The lead's design note, given to both workers: `/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/design.md`, and review 1's addendum, `/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/design-r1.md` (repeated below).
- Review 1's record (a failing draft): `/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/rev-1-result.md`.
- The code at the head (`git diff --stat ab1ea26c5585 ea5728df2d9a`; review 1's fixes: `git diff 6ec6cbd6e158 ea5728df2d9a -- src tests/unit`), its unit tests and the acceptance tests `tests/acceptance/W2-96/`.
- The lead's suite results: the fourth engineer's run on this branch after review 1 (`tests/acceptance/W2-96`: 79 passed, review 1's 18 cases and 7 premises included; `tests/unit/accept`: 41 passed); `gov accept DAEO-ouet --json` on this worktree: `outcome: pass`, all nine lines pass, `unmapped` 17 passed, `totals` 79 passed, exit 0; the test designer's run of review 1's cases on the base code (red: `gov accept` absent). The command-list red (W1-32, `accept` not recorded) is the lead's package, not a finding. The lead's scoped run (select_tests.py) waits for the machine's load and runs after you; it does not change the code you probe.

## What you probe for

Review 1 failed on F2 (SIGTERM or SIGHUP left the run's report in the caller's `TMPDIR`), F3 (map rows in forms the reader did not take were dropped, their failing tests hidden behind a pass) and F6 (a folder without permissions outlived the clean-up), and found F1 (`gov accept` crashed on every acceptance folder of this repository, whose `tests/conftest.py` refuses a per-run base folder). The lead's addendum, built by the engineer and tested by the designer:

## Review 1's addendum to the design note (behaviour only; it overrides the note where they differ)

- **R1 (no per-run base folder).** The runner never gives pytest a base folder of its own on the command line. The child's `TMPDIR` is a folder inside the private folder, so pytest's own default base folder, and every test's temporary folder, falls inside it and is removed with it. A project whose `conftest.py` refuses a run given a per-run base folder (as this repository's `tests/conftest.py` does) runs normally and is reported per line.
- **R2 (SIGTERM and SIGHUP).** A SIGTERM or SIGHUP sent to `gov accept` alone, during a run, ends it as an interrupt does: the child and everything it started are stopped, and the private folder is removed, before `gov` exits. Nothing of the run (no report, no test's temporary file) stays in the `TMPDIR` the caller gave, and nothing of the tests' content is printed; `gov` ends with exit code 128 plus the signal's number.
- **R3 (folders without permissions).** The private folder is removed even when a test left a folder or a file in it without read, write or execute permission, after a failure and after a timeout's kill alike: nothing stays in the caller's `TMPDIR`.
- **R4 (an unreadable map row refuses).** In a map table with a KPI column, a body row whose Test/File cell holds at least one backticked item while its KPI cell begins with no line name the reader takes (for example `Failure: …` with no number, `Success 3a`, `S8b`) makes the whole run refused before any test runs: `ACCEPT_MAP_UNREADABLE`, exit 1, `ok: false`, the refusal naming only the ticket and its declared path, never the row. The same holds for a Test/File table with no KPI column whose nearest heading begins with the word `success`, `failure` or `KPI` (any case) but names no line the reader takes. A table under any other heading still maps nothing, as before.
- **R5 (items).** An item holding `::` whose part before the `::` is empty or does not end in `.py` (`::test_x`, `every_form::test_x`) means every test of the folder whose function name is the part after the last `::`. An item that names a test — it holds `::`, or it begins with `test_` (a file `test_….py` included) — and matches no collected case makes its line fail (counted only; never named).
- **R6 (no log file).** No log file is written, whatever the project's pytest configuration says (`log_file`).
- **R7 (an exit that contradicts the report).** pytest ending with its "tests failed" exit code while the report holds no failed or errored case is a `crash`.
- **Unchanged (KPI 3 and 5):** a test the README never names is counted under `unmapped`, and unmapped cases never change the exit code. Whether they should is a question for the orchestrator (package), not for this round.


Probe the head for:
- whether each of F1, F2, F3 and F6 is closed, in ordinary use and at its edges (SIGTERM and SIGHUP at every phase of a run — before the child starts, while it runs, while the report is read, during the clean-up; a second signal; a folder without permissions at several depths; README rows in today's forms, the 70 acceptance READMEs of this repository read-only through copies of single README files);
- whether the fixes opened a new path by which test content reaches the caller (stdout, stderr, the envelope, an error, a traceback, a file left in the repository or the given `TMPDIR`), or a result that fails open (a failing, erroring or uncollected mapped test reported as pass; a line with no test passing; an exit code 0 when a mapped line fails);
- **any write in the repository** (`git status --porcelain --ignored` of the planted project before and after);
- `gov accept DAEO-ouet --json` on this worktree, read-only: a sane per-line result.

Not findings of this review (already with the orchestrator or recorded): the rule that a test the README never names never changes the exit code (KPI 3 and 5; package PKG-1 asks whether to change it); `gov accept` missing from the command list (package, DEC-747); review 1's rows F4, F8, F9, F10, unless the head changed them. Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such.

## Judgement rules (carried word for word from `governance/project/briefs/JUDGEMENT.md`)

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

For this ticket, "fails open" includes any test content reaching the caller in ordinary use (an engineer running `gov accept` on its own ticket), since that silently defeats the separation the runner exists to enforce.

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

After the twelve fields, the probe record's content, in Markdown, ready for the lead to commit: the head you probed (full id), what you probed and found sound, and each finding as a described behaviour, never as code (DEC-136) — what was done, what happened, what should have happened, its severity, and its two lines (`Ordinary work: …`, `Consequence: …`) — and your verdict (pass: no finding is both "yes" and "fails open"/"loses work"; fail otherwise). Then a `brief_gaps:` section (or `brief_gaps: none`).
