# Brief: reviewer (FULL, read-only), W2-96 (DAEO-ouet), review 1

You are a fresh reviewer. Ticket `DAEO-ouet` (W2-96, the opaque acceptance runner `gov accept`), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-96` on branch `w2/W2-96`, at the head `6ec6cbd6e158`, and its acceptance tests pass. You probe that head for behaviour the tests miss. You write nothing in the repository.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ouet','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (never delete such a file; name it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-ouet`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-96` and `w2/W2-96`), and `git rev-parse --short=12 HEAD` (expect `6ec6cbd6e158`; the full id `git rev-parse HEAD` gives is the probe record's `probed_commit`). If anything differs, stop and say so. The head holds, over the base `ab1ea26c5585`: the engineer's commit `9859695c8fcc` (`src/gov/accept/`, `tests/unit/accept/test_w2_96_accept.py`), the test designer's `73e50896445c` (`tests/acceptance/W2-96/`) merged by the lead in `986fa7cf4b1e`, and the lead's checkpoint record `6ec6cbd6e158`.

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
- **Tests run no more than this (DEC-959 item 1):** you re-run no suite; you read the tests, the code and the lead's results, and you run your own probes.
- Budget: your share is 2 GB and 50,000 files and folders; clean up your probe folders.
- If the guard or the sandbox refuses something you need, do not work around it: say so in your return. **Refused twice for the same call: stop and say so; no third try (AR-6).**

## What you read

- The ticket file `.tickets/DAEO-ouet.md`: its KPI lines and its `allowed_paths` (`src/gov/accept/**`, `tests/unit/accept/test_w2_96*`, and the test designer's `tests/acceptance/W2-96/`).
- The sources: DEC-959 (items 6 and 7), DEC-957, DEC-820 (c), DEC-317, MR-3 in `docs/DECISION_REGISTER.md`; `governance/project/orchestration/packages/ROLES-RESEARCH-1.md` §2.7; `src/gov/cli/main.py`'s docstring (the command-module convention, the envelope, the exit codes).
- The lead's design note, given to both workers: `/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/design.md`.
- The code at the head (`git diff --stat ab1ea26c5585 6ec6cbd6e158`), its unit tests and the acceptance tests `tests/acceptance/W2-96/`.
- The lead's suite results: the test designer's red run on the base code (44 failed because `gov accept` did not exist, 10 premises passed); the second engineer's run on this branch (`tests/acceptance/W2-96`: 54 passed; `tests/unit/accept`: 25 passed); the first engineer's run of W1-07, W1-26 and W1-32's command-set cases (17 passed, 1 failed: W1-32's `test_the_command_set_is_the_twelve_and_the_three_recorded_ones`, red because `accept` is not yet recorded in the command list, which the lead returns as a package; not a finding of this review); the lead's whole-tree collection (17387/17389 collected, no error). The lead's scoped run (select_tests.py) waits for the machine's load and runs after you; it does not change the code you probe.

## What you probe for

This runner is the one mechanism that keeps the engineer from seeing the acceptance tests' content (DEC-957's "only pass or fail"). A leak is silent: it fails open on the work order's separation. Probe, by running the code on planted tickets of your own in a temporary repository (planted tests whose source, names, assertion values, prints, warnings and exception messages carry a marker string of yours), for **any path by which test content reaches the caller**:
- stdout and stderr of the child (and of `gov` itself), in text and `--json`, in pass, fail, every error kind and every refusal;
- a crash message or an uncaught traceback of the runner (an unreadable README, a README not UTF-8, a folder that cannot be listed, a JUnit file that is malformed or missing, a test that kills its process, a test that writes to the terminal or to `/dev/tty`, a test that closes or redirects file descriptors, an interrupt);
- a leftover file: the JUnit report, pytest's basetemp, `.pytest_cache`, `__pycache__`, anything under the `TMPDIR` given or in the repository after any outcome;
- a file name, test name, parameter id, path inside the acceptance folder or README text in any output, error or refusal;
- environment variables the caller sets that change what the child prints or where it writes (`PYTEST_ADDOPTS`, `PYTEST_PLUGINS`, `PYTHONSTARTUP`, a `pytest.ini`/`pyproject.toml` option in the planted project such as `addopts = -rA` or a `junit_logging`), and whether the runner's result can still be trusted;
- **any write in the repository** (the planted project's tree, ignored files included, before and after; `git status --porcelain --ignored`);
- results that fail open: a failing, erroring or uncollected test reported as pass; a mapped line with no test passing; an error kind reported as pass or fail; an exit code 0 when a line fails.

Also judge: does the README map reader read the form designers' READMEs use today (try three real READMEs from `tests/acceptance/`, read-only, by pointing a planted ticket at a copy of each single README file in your temporary folder), and does `gov accept DAEO-ouet` on this worktree itself (read-only) give a sane per-line result?

Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such.

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
