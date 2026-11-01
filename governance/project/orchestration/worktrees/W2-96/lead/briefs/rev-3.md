# Brief: reviewer (FULL, read-only), W2-96 (DAEO-ouet), run 2's review (a new round under DEC-970; up to two reviews in this round, DEC-916)

You are a fresh reviewer. Ticket `DAEO-ouet` (W2-96, the opaque acceptance runner `gov accept`), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-96` on branch `w2/W2-96`, at the head `382e6d8fba8c`, and its acceptance tests pass. You probe **what run 2 changed** for behaviour the tests miss. You write nothing in the repository.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ouet','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (never delete such a file; name it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-ouet`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-96` and `w2/W2-96`) and `git rev-parse --short=12 HEAD` (expect `382e6d8fba8c`; the full id `git rev-parse HEAD` gives is the probe record's `probed_commit`). If anything differs, stop and say so.

**What run 2 changed** (over `549dd29b1c6f`, the head where run 2 started, which is run 1's code with `w2/integrate` merged in): the engineer's `41b9fdddf109` (R8 to R13: any failed case fails the run; SIGINT held during the clean-up with SIGTERM and SIGHUP; a removal without recursion; inherited ignores kept; exit 128+N; `accept` in `RECORDED_GOV_COMMANDS`) and `917aba42cd9c` (once a stop is decided the three signals are ignored, so a signal after the clean-up never kills `gov`); the test designer's `1bf0c1d2e18f` (`accept` in W1-07's and W1-32's command lists, `Rewrite-Reason: DEC-959 item 6`) and `a5ad2254e97b` (21 run-2 cases in `test_w2_96_at_run_2.py`, 7 run-1 cases revised for R8, `Rewrite-Reason: DEC-970 ...`), merged by the lead in `7bc8a0303e0d`; the lead's checkpoint record `382e6d8fba8c` (no code). `git diff --stat 549dd29b1c6f 382e6d8fba8c`: 14 files, +1052/-59.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. You write nothing, so no commit of yours will exist: return when your findings are complete.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no commit, no merge, no push, no tag. Write no file of the repository. No subagents that write. Install nothing.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src` set **per command** (never in a session's `--settings` env). Quote `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -c "import gov; print(gov.__file__)"`.
- **Policy 2 (DEC-820):** you read everything, tests and code alike. Refused to you: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read, print, search, diff or copy the held-out file under `governance/project/`, never type its path, never read or name the qualification oracle; a scan over READMEs that prints a line naming it: do not repeat it); (c) for the two workers, each other's work — not for you, the reviewer reads both; (d) the hidden half of any evaluation set.
- **DEC-849:** until W2-58 lands the guard still refuses some reads (searches starting at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form; search named folders instead, and count the refusals you met. Never read `.claude/settings.json`.
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src timeout 90 python3 -m gov.cli.main retrieve "<question>" --json` (inside the sandbox it can hang on the embedder's network call: try once, then read named files); never one giant query (DEC-860: batches with `--batch-size`, then `--continue <token>`); code questions by the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted (DEC-859).
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of it). A probe that needs a repository builds a temporary one from scratch in your temporary folder (the one the launcher set). Never write in `~/gov-os-workbench`. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. A probe script you need goes in your temporary folder (written with the Write tool at a literal absolute path), never in the repository. An inline command that names a path under `tests/acceptance/` may be refused as "may write the acceptance tests": put that read in a script file.
- **Row W2-L423's rule (DEC-911):** write commit hashes as 12 digits in your return, except `probed_commit`, which is the full id; never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- Never `cd` into a subfolder of the repository: the sandbox leaves a `.claude/` folder there (review 1 left one in `tests/acceptance/`). Work from the worktree's top with full paths. `rm` is refused by the permission layer in this non-interactive session: do not try it; name your probe folders in your return instead.
- **Tests run no more than this (DEC-959 item 1):** you re-run no suite; you read the tests, the code and the lead's results, and you run your own probes.
- Each Bash call runs in a PID namespace of its own: check processes within the same call that started them. A signal window that only an in-process placement can reach is evidence, marked "not ordinary".
- Budget: your share is 2 GB and 50,000 files and folders.
- If the guard or the sandbox refuses something you need, do not work around it: say so in your return. **Refused twice for the same call: stop and say so; no third try (AR-6).**

## What you read

- The ticket file `.tickets/DAEO-ouet.md`: its KPI lines, its `allowed_paths` (`src/gov/accept/**`, `tests/unit/accept/test_w2_96*`, `src/gov/check/commands.py` for the one `accept` line, and the test designer's `tests/acceptance/W2-96/`) and its body (DEC-970).
- The sources: DEC-970 (its W2-96 item), DEC-959 (items 6 and 7), DEC-957, DEC-820 (c), DEC-317, DEC-747, MR-3 in `docs/DECISION_REGISTER.md`; `src/gov/cli/main.py`'s docstring.
- The lead's design note and addenda: `/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/design.md`, `design-r1.md` (R1–R7), `design-r2.md` (run 2: R8–R13, repeated below).
- Review 2's record (a failing draft), for its findings N1 to N9: `/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/rev-2-result.md`.
- The change: `git diff 549dd29b1c6f HEAD -- src tests/unit tests/acceptance/W2-96 tests/acceptance/W1-07 tests/acceptance/W1-32`.
- The lead's results: the lead's red check of run 2's suite on run 1's code (the tests branch): 23 failed, 77 passed, each red for its README's reason (R8 exit or outcome, R9/R10 leftovers holding the marker, R11 a stop on an ignored signal, R12 death by the signal); the engineer's runs on this branch: `tests/unit/accept` 62 passed; the first `gov accept DAEO-ouet --json` after the merge exit 3 (2 failed, R9's Ctrl-C cases: a signal after the clean-up killed `gov`), fixed in `917aba42cd9c`; the second exit 0, `outcome: pass`, all nine lines pass, `unmapped` 20 passed, `totals` 100 passed; W1-07's, W1-32's and W1-26's recorded-command files 21 passed. The lead's rebuild and scoped run (select_tests.py, scope `scoped`, `core_changed` [`src/gov/check/commands.py`]) run beside you; they do not change the code you probe. The test designer kept one case of its own reading (P-W2-96-R11-GROUP, decided by the lead as P3: keep): R11's SIGHUP also sent to `gov`'s process group.

## Run 2's addendum (DEC-970), what you probe

- **R8 (any failed case fails the run; PKG-1 (a)).** `outcome: fail`, exit 3 when any collected case failed or errored, mapped or not; unmapped cases still only counted, never named; skipped never fails; pass and exit 0 need every mapped line passing and no failed or errored case anywhere.
- **R9 (Ctrl-C during the clean-up held back; N2).** A SIGINT during the clean-up is held back as SIGTERM and SIGHUP are: the clean-up finishes, nothing stays in the caller's `TMPDIR`, then `gov` ends. More signals during the clean-up change nothing.
- **R10 (clean-up without recursion; N5).** A chain of more than 1,100 nested folders (some without permissions) is removed; the run is reported as its results say, never `crash`.
- **R11 (inherited ignore kept; N7).** SIGHUP, SIGTERM or SIGINT ignored at start stays ignored: neither the run nor its child stops.
- **R12 (exit 128+N; N8).** A run ended by SIGINT, SIGTERM or SIGHUP (during the run, or held back and acted on after the clean-up) exits 130, 143 or 129, never death by the signal.
- **R13 (`accept` recorded; DEC-747).** `accept` in `RECORDED_GOV_COMMANDS` (one line), and in W1-07's and W1-32's lists (the test designer's revision, `Rewrite-Reason: DEC-959 item 6`).

Probe:
- each of R8 to R13 in ordinary use and at its edges (review 2's N1 forms with a failing test: W1-30's headerless one-row tables, a `Case | Clause` table; an unmapped error in setup; an unmapped skipped test; Ctrl-C twice during a long removal; SIGTERM twice; `nohup`; a deep chain after a pass and after a failure and at a timeout);
- whether the change opened a new path by which test content reaches the caller (stdout, stderr, the envelope, an error, a traceback — Ctrl-C's included — or a file left in the repository or the given `TMPDIR`), or a result that fails open (a failing or erroring test, mapped or not, reported with exit 0; a line with no test passing);
- **any write in the repository** (`git status --porcelain --ignored` of the planted project before and after);
- whether the `commands.py` change is the one `accept` line and nothing else, and whether W1-07's and W1-32's revisions lower anything beyond adding `accept`;
- whether the test designer's revisions of run 1's W2-96 cases lower any expectation beyond what R8 and R12 change;
- `gov accept DAEO-ouet --json` on this worktree, read-only, once: a sane result.

Not findings of this review (decided or recorded): review 2's rows N3 (microsecond signal windows), N4 (SIGKILL of `gov` alone), N6 (inherited test classes) and N9 (most of today's READMEs refuse or never pass; the map forms go into the brief change, KPI 6, the orchestrator's at merge), unless the head changed them; review 1's rows F4, F8, F9, F10. Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such.

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

For this ticket, "fails open" includes any test content reaching the caller in ordinary use (an engineer running `gov accept` on its own ticket), and a failing test hidden behind exit 0, since either silently defeats what the runner exists to enforce.

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

After the twelve fields, the probe record's content, in Markdown, ready for the lead to commit: the head you probed (full id), what you probed and found sound, and each finding as a described behaviour, never as code (DEC-136) — what was done, what happened, what should have happened, its severity, and its two lines (`Ordinary work: …`, `Consequence: …`) — and your verdict (pass: no finding is both "yes" and "fails open"/"loses work"; fail otherwise). Then a `brief_gaps:` section (or `brief_gaps: none`), and the guard refusals you met (read refusals counted; any other refusal with its command's form and reason).
