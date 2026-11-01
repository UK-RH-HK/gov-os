# Brief: reviewer (FULL, read-only), W2-96 (DAEO-ouet), review 5: the third review, of the subreaper change alone (DEC-987, the owner's exception to DEC-916)

You are a fresh reviewer. Ticket `DAEO-ouet` (W2-96, the opaque acceptance runner `gov accept`), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-96` on branch `w2/W2-96`, at the head `90122df096e7`. Review 4 failed on one finding (W1). The owner decided (DEC-987, in `docs/DECISION_REGISTER.md`): fix it now, two cases first, then **a third review of that change alone**, which is you. **You judge only the subreaper change and the two new cases, against KPI 2 and the two judgement questions.** Everything else was probed by reviews 1 to 4 and is out of scope unless this change broke it. There is no further review: if you fail it, the owner decides. You write nothing in the repository.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ouet','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (never delete such a file; name it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-ouet`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-96` and `w2/W2-96`) and `git rev-parse --short=12 HEAD` (expect `90122df096e7`; the full id `git rev-parse HEAD` gives is the probe record's `probed_commit`). If anything differs, stop and say so.

**What changed since review 4's head `0e0883b80397`:**
- `w2/integrate` merged in by the orchestrator (`943543cea0e8`: decisions DEC-983 to DEC-987; nothing under `src/gov/accept/`);
- the test designer's `4b9353954f88` (review 4's W1 cases, R16: `tests/acceptance/W2-96/test_w2_96_at_review_4.py`, additions to `w2_96_support.py` and the README), merged by the lead in `9d2d27e2b5bd`;
- the engineer's `44dbc90ee340` (R16: the subreaper, and every process of the run stopped and reaped before the clean-up);
- a second test designer's `d19019ca483e`, merged by the lead in `d86588d5`: one constant of the R16 support code renamed (`R16_TOKEN_KEY` to `R16_RUN_VAR`, 4 lines, value unchanged), because gitleaks' `generic-api-key` rule took its name for a key and turned the product's `secrets-indexing` check red; `Rewrite-Reason` in that commit; the whole W2-96 folder passed 109/109 after it. A first launch of this review on the head before that rename was stopped by the lead before it returned anything, so that this review judges the final head;
- the lead's checkpoint records (no code).

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. You write nothing, so no commit of yours will exist: return when your findings are complete.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no commit, no merge, no push, no tag. Write no file of the repository. No subagents that write. Install nothing.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src` set **per command** (never in a session's `--settings` env). Quote `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -c "import gov; print(gov.__file__)"`.
- **Policy 2 (DEC-820):** you read everything, tests and code alike. Refused to you: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read, print, search, diff or copy the held-out file under `governance/project/`, never type its path, never read or name the qualification oracle; a scan over READMEs that prints a line naming it: do not repeat it); (c) for the two workers, each other's work — not for you, the reviewer reads both; (d) the hidden half of any evaluation set, by whoever is measured by it.
- **DEC-849:** until W2-58 lands the guard still refuses some reads (searches starting at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form; search named folders instead, and count the refusals you met. Never read `.claude/settings.json`.
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src timeout 90 python3 -m gov.cli.main retrieve "<question>" --json` (inside the sandbox it can hang on the embedder's network call: try once, then read named files); never one giant query (DEC-860: batches with `--batch-size`, then `--continue <token>`); code questions by the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph (DEC-859).
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of it). A probe that needs a repository builds a temporary one from scratch in your temporary folder (the one the launcher set). Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file, and placeholder dotfiles (`.bashrc`, `.gitconfig`, `.mcp.json` and others, character devices) show as untracked at the worktree's top: conclude nothing from them.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. A probe script you need goes in your temporary folder (written with the Write tool at a literal absolute path), never in the repository. An inline command that names a path under `tests/acceptance/` may be refused as "may write the acceptance tests": put that read in a script file.
- **Row W2-L423's rule (DEC-911):** write commit hashes as 12 digits in your return, except `probed_commit`, which is the full id; never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- Never `cd` into a subfolder of the repository: the sandbox leaves a `.claude/` folder there (review 1 left one in `tests/acceptance/`). Work from the worktree's top with full paths. `rm` is refused by the permission layer in this non-interactive session: do not try it; name your probe folders in your return instead.
- **Tests run no more than this (DEC-959 item 1):** you re-run no suite; you read the tests, the code and the lead's results, and you run your own probes.
- Each Bash call runs in a PID namespace of its own: check processes within the same call that started them, and make sure every process a probe starts is gone before that call ends. A signal window that only an in-process placement can reach is evidence, marked "not ordinary".
- Budget (DEC-898): your share of the ticket's 20 GB / 1,000,000 files and folders is 2 GB and 50,000 files and folders, in your temporary folder, counting the peak of your one allowed `gov accept DAEO-ouet` run (about 26,000): run it first, before your probes fill the folder; measure (`du -sh`, `du -s --inodes`) at the end and give the figures.
- Protected material: never read the held-out material's contents and never print a secret; never read or name the qualification oracle.
- If the guard or the sandbox refuses something you need, do not work around it: say so in your return. **Refused twice for the same call: stop and say so; no third try (AR-6).**

## What you read

- The ticket file `.tickets/DAEO-ouet.md`: its KPI lines (KPI 2 above all), its `allowed_paths` and its body.
- The sources: DEC-987, DEC-916, DEC-959 (items 6 and 7), DEC-957, DEC-820 (c), DEC-317 in `docs/DECISION_REGISTER.md`.
- Review 4's record (a failing draft), for W1 to W3: `/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/probes/PR-DAEO-ouet-review-4-DRAFT-fail.md`; review 4's full return: `/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/rev-4-result.md`.
- The lead's addenda for background (R1 to R15): `/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/design.md`, `design-r1.md`, `design-r2.md`, `design-r3.md`; R16 below.
- The change: `git diff 9d2d27e2b5bd 44dbc90ee340 -- src tests/unit` (the engineer's) and `git show 4b9353954f88 --stat` with its files (the two cases), and `git show d19019ca483e` (the rename).
- The lead's results:
  - The test designer's red runs of the two cases on the code before the fix (`943543cea0e8`): red in 4 of 4 runs of the new file; the whole folder 2 failed / 107 passed. Reasons: 2 processes of the run (the nested `gov accept` and its pytest) still alive when the outer `gov` ended; 6 entries, the last carrying the marker, in the given TMPDIR 8.4–9.0 s after `gov` ended (none when it ended).
  - The lead's own red check on the merged head `9d2d27e2b5bd` (this worktree's code): the whole folder 2 failed (both R16 cases, for those reasons) / 107 passed, 162 s.
  - The engineer's builder tests `tests/unit/accept`: 95 passed at `44dbc90ee340` (14 in `test_w2_96_review4.py`, 6 of them red before the fix); `gov accept DAEO-ouet --json` once after its commit: exit 0, `outcome: pass`, all nine lines pass (success 1–5: 14/22/23/11/36; failure 1–4: 18/23/11/31), `unmapped` 23, `totals` 109 passed (106 earlier cases, the two R16 cases and their premise).
  - The engineer's statements you may probe: `gov` becomes a subreaper just before starting the child, noting the children it already had; in the `finally`, after the main child's own status is taken, it reads its children from `/proc/<gov>/task/*/children`, leaves out those that were there before, sends SIGKILL to the rest and reaps each by pid, every 2 ms until none is left or a 5 s bound ends; then it puts the previous subreaper setting back and removes its private folder. Where `prctl` is unavailable it keeps the old behaviour (a kill of the child's process group). Its stated risks: in-process callers' other threads' children would count as the run's; a process that forks and exits faster than a 2 ms pass could escape until the bound; a signal between the `prctl` call and the assignment leaves the setting unrestored.
  - The lead's rebuild and scoped run (select_tests.py) run beside you; they do not change the code you probe.

## R16 (review 4's W1; DEC-987), what you probe

- **R16 (no process of the run outlives `gov`; nothing of the run appears in the caller's `TMPDIR` afterwards).** Before its clean-up, in every path (a pass, a failure, an error, a stop by SIGINT, SIGTERM or SIGHUP), `gov accept` stops every process the run started, **whatever its session or process group**, and waits until none is left; only then does it remove its private folder. Once `gov` has ended, no process of the run is alive, and nothing of the run appears in the caller's `TMPDIR` later. Exit codes, the envelope, R9's held signals, R12's 128 plus the signal, R14's tolerant removal and R15's linear time are unchanged; nothing from the child is printed. The owner named the mechanism: on Linux, a subreaper (`prctl(PR_SET_CHILD_SUBREAPER)`), then stop and wait for every descendant.

Probe (run the code; do not judge it by reading alone):
- **W1 again, as review 4 did it, and wider:** a nested `gov accept` in a session of its own (W2-96's harness form), the nested test sleeping or writing, and a stop to the outer `gov` alone (SIGTERM, Ctrl-C once and twice, SIGHUP, coreutils `timeout`) at a random time and while the nested pytest runs; a planted test that starts such a run and does not wait for it, with no stop; a daemon-style double fork; a writer that recreates its folders; a process that keeps forking while it is being stopped. Check the given `TMPDIR` when `gov` ends **and again after the orphan would have written**, and whether any process of the run is alive once `gov` has ended. Count the runs: exit code, `error_kind`, what stays (names and contents).
- **Does the change harm anything outside the run:** does `gov` ever stop or reap a process it did not start (one started beside it, its own parent, a sibling in the caller's shell, a process of another `gov accept` running at the same time)? Does the subreaper setting leak out of `gov accept` (other commands, the caller)? Does reaping ever take the main child's exit status, so that a failing run is reported as a pass or an error (a failing test hidden behind exit 0 fails open)?
- **Bounds and fall-backs:** a descendant that cannot be stopped at once (it ignores SIGTERM, or keeps forking): does `gov` end within its stated bound, with the right exit code, holding R9's signals; what happens where the subreaper is unavailable (as the engineer states it).
- **No regression of R9, R12, R14, R15** in the changed path (spot checks, not a full re-run): R9's held signals, R12's 128+N, R14's tolerant removal, R15's time on 8,000 sibling folders.
- whether the change opened a new path by which test content reaches the caller (stdout, stderr, the envelope, an error, a traceback, or a file left in the repository or the given `TMPDIR`);
- **any write in the repository** (`git status --porcelain --ignored` of the planted project before and after);
- whether `4b9353954f88`'s two cases test R16 as stated and lower no earlier expectation, and whether `d19019ca483e` is a rename only;
- `gov accept DAEO-ouet --json` on this worktree, read-only, once: a sane result (108 cases).

Not findings of this review (decided or recorded): review 4's rows W2 (silent give-up after a lasting error) and W3 (a link put in place of the private folder); review 3's V3; review 2's rows N3, N4, N6 and N9; review 1's rows F4, F8, F9, F10; anything outside the subreaper change and the two cases, unless this change broke it. A finding you could not reproduce is marked as such.

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

After the twelve fields, the probe record's content, in Markdown, ready for the lead to commit: the head you probed (full id), what you probed and found sound, and each finding as a described behaviour, never as code (DEC-136) — what was done, what happened, what should have happened, its severity, and its two lines (`Ordinary work: …`, `Consequence: …`) — the classification of the findings on one line (DEC-809), and your verdict (pass: no finding is both "yes" and "fails open"/"loses work"; fail otherwise). Then a `brief_gaps:` section (or `brief_gaps: none`), and the guard refusals you met (read refusals counted; any other refusal with its command's form, its reason and the time).
