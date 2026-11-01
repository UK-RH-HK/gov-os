# Brief: reviewer (FULL, read-only), W2-96 (DAEO-ouet), review 4: the second and last review of run 2's round (DEC-916)

You are a fresh reviewer. Ticket `DAEO-ouet` (W2-96, the opaque acceptance runner `gov accept`), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-96` on branch `w2/W2-96`, at the head `0e0883b80397`, and its acceptance tests pass. Review 3 failed on one finding (V1); its fix and its new cases are now in. You probe **what changed since review 3's head `382e6d8fba8c`** for behaviour the tests miss. You are the last review of this round: there is no further round. You write nothing in the repository.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ouet','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (never delete such a file; name it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-ouet`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-96` and `w2/W2-96`) and `git rev-parse --short=12 HEAD` (expect `0e0883b80397`; the full id `git rev-parse HEAD` gives is the probe record's `probed_commit`). If anything differs, stop and say so.

**What changed since review 3's head `382e6d8fba8c`:**
- the engineer's `b3dd46f82321` (R14: the clean-up tolerates concurrent changes, up to 20 removal passes that never raise; R15: each pass linear in its entries; and, found by the engineer, a check of every move up through `..` against the parent's device and inode, so a folder moved away during the removal cannot lead it outside the private folder, which the old code allowed);
- the test designer's `588e43ae11ff` (review 3's cases: R14, R15) and `c348af6bc9ae` (run 2's R9 two-press case tied to the clean-up's progress on disk, not to elapsed time; `Rewrite-Reason: P-W2-96-R9-PREMISE (a)`, a P3 the lead decided), merged by the lead in `a1d14a3f`;
- `w2/integrate` merged in by the orchestrator (`064c69f8b785`: W2-107, the secrets cache, and decisions DEC-974 to DEC-979; nothing under `src/gov/accept/`);
- the engineer's acceptance run after the merge of review 3's cases made no change (106/106 on the first run; no commit);
- the lead's checkpoint records (no code).

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. You write nothing, so no commit of yours will exist: return when your findings are complete.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no commit, no merge, no push, no tag. Write no file of the repository. No subagents that write. Install nothing.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src` set **per command** (never in a session's `--settings` env). Quote `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -c "import gov; print(gov.__file__)"`.
- **Policy 2 (DEC-820):** you read everything, tests and code alike. Refused to you: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read, print, search, diff or copy the held-out file under `governance/project/`, never type its path, never read or name the qualification oracle; a scan over READMEs that prints a line naming it: do not repeat it); (c) for the two workers, each other's work — not for you, the reviewer reads both; (d) the hidden half of any evaluation set.
- **DEC-849:** until W2-58 lands the guard still refuses some reads (searches starting at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form; search named folders instead, and count the refusals you met. Never read `.claude/settings.json`.
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src timeout 90 python3 -m gov.cli.main retrieve "<question>" --json` (inside the sandbox it can hang on the embedder's network call: try once, then read named files); never one giant query (DEC-860: batches with `--batch-size`, then `--continue <token>`); code questions by the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph (DEC-859).
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of it). A probe that needs a repository builds a temporary one from scratch in your temporary folder (the one the launcher set). Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file, and placeholder dotfiles (`.bashrc`, `.gitconfig`, `.mcp.json` and others, character devices) show as untracked at the worktree's top: conclude nothing from them.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. A probe script you need goes in your temporary folder (written with the Write tool at a literal absolute path), never in the repository. An inline command that names a path under `tests/acceptance/` may be refused as "may write the acceptance tests": put that read in a script file.
- **Row W2-L423's rule (DEC-911):** write commit hashes as 12 digits in your return, except `probed_commit`, which is the full id; never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- Never `cd` into a subfolder of the repository: the sandbox leaves a `.claude/` folder there (review 1 left one in `tests/acceptance/`). Work from the worktree's top with full paths. `rm` is refused by the permission layer in this non-interactive session: do not try it; name your probe folders in your return instead.
- **Tests run no more than this (DEC-959 item 1):** you re-run no suite; you read the tests, the code and the lead's results, and you run your own probes.
- Each Bash call runs in a PID namespace of its own: check processes within the same call that started them. A signal window that only an in-process placement can reach is evidence, marked "not ordinary".
- Budget (DEC-898): your share of the ticket's 20 GB / 1,000,000 files and folders is 2 GB and 50,000 files and folders, in your temporary folder; measure it (`du -sh`, `du -s --inodes`) at the end and give the figures.
- Protected material: never read the held-out material's contents and never print a secret; never read or name the qualification oracle.
- If the guard or the sandbox refuses something you need, do not work around it: say so in your return. **Refused twice for the same call: stop and say so; no third try (AR-6).**

## What you read

- The ticket file `.tickets/DAEO-ouet.md`: its KPI lines, its `allowed_paths` (`src/gov/accept/**`, `tests/unit/accept/test_w2_96*`, `src/gov/check/commands.py` for the one `accept` line, and the test designer's `tests/acceptance/W2-96/`) and its body.
- The sources: DEC-970 (its W2-96 item), DEC-976, DEC-959 (items 6 and 7), DEC-916, DEC-957, DEC-820 (c), DEC-317 in `docs/DECISION_REGISTER.md`.
- The lead's design note and addenda: `/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/design.md`, `design-r1.md` (R1–R7), `design-r2.md` (R8–R13), `design-r3.md` (R14, R15, repeated below).
- Review 3's record (a failing draft), for V1 to V3: `/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/probes/PR-DAEO-ouet-review-3-DRAFT-fail.md`; review 3's full return: `/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log/rev-3-result.md`.
- The change: `git diff 382e6d8fba8c HEAD -- src tests/unit tests/acceptance/W2-96`.
- The lead's results: the test designer's red runs of review 3's cases on run 2's code (`382e6d8fba8c`): the whole folder 102 passed / 4 failed, twice; the lead's own red check, the same (whole folder 4 failed / 102 passed; the new file alone 4 failed and its 2 premises passed), each red for its README's reason (R14's races: `crash`, exit 4, and leftovers in the given TMPDIR; R15: the clean-up of 8,000 sibling folders took 6.8 s to 7.1 s against the 3 s bound); the engineer's builder tests `tests/unit/accept` 81 passed at `b3dd46f82321` (including 19 for R14/R15 and the `..` check); its timings of the removal against a plain recursive removal: 1k 0.03/0.02 s, 2k 0.07/0.05 s, 4k 0.11/0.15 s, 8k 0.28/0.21 s; `gov accept DAEO-ouet --json` before review 3's cases were merged: exit 0, 100/100; after the merge, on this branch, once: exit 0, `outcome: pass`, all nine lines pass, `unmapped` 22 passed, `totals` 106 passed. The engineer states two risks you may probe: a clean-up meeting an error that never goes away waits about 4 s over its 20 passes, with the signals held, before passing it over; a process that keeps writing after the last pass, or recreates folders, can still leave entries. The lead's rebuild and scoped run (select_tests.py) run beside you; they do not change the code you probe.

## Review 3's addendum (behaviour only), what you probe

- **R14 (the clean-up tolerates concurrent changes; review 3's V1).** The private folder is removed in every path even when a process the run cannot stop (one a test started in a session of its own, such as a nested `gov accept`) changes it meanwhile, or removes it first: an entry already gone is passed over, a folder found not empty is emptied again, and no single entry stops the removal of the rest (a bounded number of passes, then whatever error remains is passed over too). A run stopped by SIGINT, SIGTERM or SIGHUP still ends with 128 plus the signal (R12) whatever the clean-up met; a run that was not stopped is reported as its results say, never turned into `crash` by an entry another process removed. Nothing of the run stays in the caller's `TMPDIR`. Depth still never matters (R10), and the three signals are still held during the clean-up (R9).
- **R15 (the clean-up's time grows with the entries; review 3's V2, riding along).** Removing a folder whose thousands of sibling folders sit side by side takes time in proportion to the number of entries, not its square: 8,000 empty sibling folders are removed in a few seconds at most, comparable to a plain recursive removal.

Probe:
- **V1 again, as review 3 did it, and wider:** a stop (SIGTERM, Ctrl-C, SIGHUP; once, twice; to `gov` alone and to the whole process tree at once) that lands while **processes started outside the child's process group** change the private folder: a nested `gov accept` in a session of its own (as W2-96's own harness starts them), a plain writer started with `start_new_session`, a daemon-style double fork, a process that outlives the test and keeps writing after the run ends, a process that removes entries (racing the clean-up) and one that adds them; at a random time and timed by what is on disk; and the same at the end of a run that was **not** stopped. Count the runs: exit code, `error_kind`, what stays in the given `TMPDIR` (names and contents).
- **The engineer's `..` escape fix:** a folder inside the private folder moved elsewhere (inside and outside the private folder; to the given TMPDIR; to the planted project) while the removal empties it: nothing outside the private folder is removed or changed, ever; a symbolic link at any depth (to a folder outside, to the project, to `/`) is removed, never followed; files without permissions, folders without read or execute permission, a folder replaced by a file and a file by a folder between passes.
- **The cost of the passes:** an error that never goes away (a folder made unremovable by permissions the run cannot change, an entry on a read-only mount if you can make one in your temp folder) — how long the clean-up holds the three signals, whether `gov` then ends, its exit code and envelope, and whether it says something left the private folder or stays silent (judge silence by R14's text and KPI 2).
- **R15:** timings on 1,000 to 8,000 sibling folders and on a mix of deep and wide, against a plain recursive removal.
- **No regression of R8 to R13** in the changed code paths (spot checks, not a full re-run): R9's held signals during the now longer clean-up, R10's deep chain, R12's 128+N after a clean-up that met errors.
- whether the change opened a new path by which test content reaches the caller (stdout, stderr, the envelope, an error, a traceback, or a file left in the repository or the given `TMPDIR`), or a result that fails open (a failing or erroring test, mapped or not, reported with exit 0; a line with no test passing);
- **any write in the repository** (`git status --porcelain --ignored` of the planted project before and after);
- whether the test designer's `c348af6bc9ae` lowers any expectation beyond tying the second press to the clean-up, and whether `588e43ae11ff`'s cases test R14 and R15 as stated;
- `gov accept DAEO-ouet --json` on this worktree, read-only, once: a sane result.

Not findings of this review (decided or recorded): review 3's rows V2 (now R15: probe it) and V3 (short windows at the ends, fails closed); review 2's rows N3, N4, N6 and N9; review 1's rows F4, F8, F9, F10; unless the head changed them. Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such.

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
