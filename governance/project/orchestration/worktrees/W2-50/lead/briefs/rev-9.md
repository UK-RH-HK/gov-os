# Brief: reviewer (FULL, read-only) — DAEO-kl5e (W2-50), run 9's fresh probe on the integrated head, after W2-58 changed the same files (DEC-894)

You are a fresh reviewer. Ticket DAEO-kl5e (W2-50, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`, at the head `HEAD_SHA` (check it with `git rev-parse HEAD`), and its acceptance tests pass. You probe that head for behaviour the tests miss: cases that could lose work, let a role write outside its scope, change acceptance tests, or make the guard fail open. You write nothing except what this brief names (nothing in any repository). Return each finding as a described behaviour, with its severity.

## Step 0, before any work: the sandbox check

Report it first in your return.
- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kl5e','w').write('x')"` must fail.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return.

## Why this probe

- W2-50 merged into `w2/integrate` on 2026-10-20 (`98effadc`) with a passing FULL probe (`docs/probes/DAEO-kl5e/PR-DAEO-kl5e-run-8.md`, probed `56240ffb7d02bf5dd0e841da8db10d9a4d177eca`). Its close on 2026-10-22 was refused `PROBE_INVALID`: "merge eb0f1454 holds the probed commit and its probed paths are not the probed code (git cannot compute its own merge of its parents)". `eb0f1454` is W2-58's merge of `w2/integrate` into its branch; it resolved a conflict, and W2-58 (Policy 2: reads open, four refusals; DEC-820, DEC-821, DEC-873, DEC-880) then rewrote files W2-50's review judged. W2-58 merged into `w2/integrate` as `4845b9b8`.
- **DEC-894 item 2** (delegated, 2026-10-22): a fresh FULL probe of W2-50's work as it stands on the merged head, W2-58's changes to the same files included. W2-50's code is not changed by this round.
- This run (run 9) did two things:
  1. **The merge** `95fb5070`: `w2/integrate` at `c4f2b303` merged into this branch, parents `b9a5e5cd` (the ticket's last head, already in `w2/integrate`) and `c4f2b303`; its tree equals `git merge-tree --write-tree HEAD^1 HEAD^2`. On the ticket's work it changed: `src/gov/guard/decide.py` (+51/−…), `src/gov/guard/protected.py` (268 lines changed), `src/gov/launch/launcher.py` (21), `tests/acceptance/W2-50/test_w2_50_one_reader.py` (40, rewritten by W2-58's test designer, `bfc290f3`, `Rewrite-Reason: DEC-821 item 3, DEC-857 item 3; DEC-821 item 4 for the second names`), `tests/unit/guard/test_protected.py` (194), `tests/unit/guard/test_protected_one_reader.py` (8). W2-58's commits on these files: `b9e03048`, `75b0a7b1`, `bf12ac1e`, `af5d1a25`, `841f8479` (a leading `~` judged as its expanded form on the file tools), `9b3f841c`, `bfc290f3`; W2-58 also added `src/gov/guard/reads.py`. `src/gov/secrets/__init__.py`, `src/gov/guard/runs.py` and the secrets check's declaration are unchanged since the last probe (check it: `git diff 56240ffb HEAD -- <path>`).
  2. **The lead's checkpoint record** at the head (`gov checkpoint`, `docs/checkpoints/DAEO-kl5e/`).
- Verification at this head (the lead's, outside the sandbox): VERIFICATION_SUMMARY

**The question:** does W2-50's work — the durable scratch root in the guard and the launcher's sandbox (DEC-728), and the secrets scan (DEC-853) — still hold as its KPIs say, now that W2-58 changed the same files?

## Rows already accepted (DEC-790: a finding already accepted as a row does not fail this probe)

W2-H062, W2-M368, W2-M369, W2-L354, W2-L350, W2-H055, W2-M359, W2-M362, W2-M363, W2-L349, W2-L342, W2-M386, W2-M387, W2-M388, W2-L364 to W2-L370, W2-M403 (`docs/plan/WAVE_2_LIST.md`). Run 8's F1 to F8 are those rows. Name a finding that matches one by its row id.

**DEC-779:** after run 7, any further guard text-parsing finding is a list row unless a launched, sandboxed worker can reach it. For each finding, say whether a launched, sandboxed worker could reach it, or only an unsandboxed session (the orchestrator, a ticket lead), or only with a precondition no session can create through the guard, with your reasons.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-kl5e`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-50` and `w2/W2-50`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- **Memory used (DEC-836):** use `gov retrieve` (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m gov.cli.main retrieve "<question>" --json`) for what you need to know before reading files at random. Say in your return which questions you asked and whether they helped. **DEC-860: never one giant query or context:** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **DEC-859: a code question** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap.
- **Reads open, writes closed (Policy 2, DEC-820).** You read everything, tests and code alike. Only these are refused: (a) secrets and keys, never printed (a canary included); (b) the contents of the held-out qualification material (its file names may be seen); (c) the counterpart's work on this ticket: the engineer never reads `tests/acceptance/W2-50/` (it may run those tests and see their names, results and failure messages), and the test designer never reads this ticket's implementation; this binds them, not you: you read both sides; (d) the hidden half of any evaluation set, by whoever is measured by it.
- **Read refusals (DEC-849):** the guard may still refuse some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count the refusals you met and give the count in your return.
- **Protected material (DEC-820).** Never read the held-out material's contents and never print a secret. Never read or name the qualification oracle. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. **Never create, write or remove anything in the real `~/gov-os-runs/` or in another worktree:** every probe of the guard's and the launcher's handling of `~/gov-os-runs` uses a temporary HOME you make in your session's temporary folder, as `tests/acceptance/W2-50/w2_50_support.py` does.
- **You write nothing in this worktree or any repository, and commit nothing** (DEC-137, DEC-826 Q3). `git status --short` must be the same before and after your probe (show both). **Never run the secrets check, `gov check` or `gov rebuild` in this worktree's root or the main tree's**: the check writes its record of clean results under the project's `.gov-runtime/`. Every probe that runs the scan runs it in a temporary project you build from scratch in your session's temporary folder (Python's `tempfile.gettempdir()`, which is your session's own; `/tmp` itself is read-only in the sandbox), with a canary of your own made at run time.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. A foreground command is killed after 10 minutes: run long files in separate commands. **Your budget is about 90 minutes**: a session past the two-hour limit is stopped and its return lost. Leave yourself time to write the return.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git merge`, no `git worktree`, no `git clone` of this repository. Read-only git (`log`, `show`, `diff`, `merge-base`, `merge-tree --write-tree`, `rev-parse`, `cat-file`) is yours. No subagents that write. Install nothing. No push, rebase or tag.
- Never copy the repository or a folder of it anywhere; copy single named files only, never `governance/project/`. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Do not run `docs/plan/tools/validate_s1.py` (DEC-738 item 2). Never run `gov close`, `gov adopt`, `gov pause` or `gov rebuild` (with or without `--no-embeddings`).
- Never ask or notify the owner (no question box, never `owner-ping`).
- **DEC-866:** if a test, a check or a KPI you look at still enforces a superseded decision, name it (old decision, new decision, file and test or line); do not judge the code against the superseded one.
- Your temporary folder is removed when your session ends (DEC-386): every finding is in your final message.
- If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return. **Refused twice for the same call: stop and say so; no third try** (AR-6). On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status AUTH_REQUIRED.

## Judgement rules (`governance/project/briefs/JUDGEMENT.md`, word for word)

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

- The ticket file `.tickets/DAEO-kl5e.md`: its KPI lines, its `allowed_paths` and its notes.
- DEC-728, DEC-743, DEC-751, DEC-778, DEC-779, DEC-785, DEC-790, DEC-801, DEC-820, DEC-821, DEC-853, DEC-873, DEC-880, DEC-894 in `docs/DECISION_REGISTER.md`; `docs/changes/W2-50-CIT-P.md`, `docs/changes/W2-50-CIT-E.md`, `docs/changes/W2-58-CIT-E.md`.
- The change since the last probe on W2-50's paths: `git diff 56240ffb HEAD -- src/gov/guard/decide.py src/gov/guard/protected.py src/gov/launch/launcher.py src/gov/guard/runs.py src/gov/secrets/__init__.py tests/acceptance/W2-50/ tests/unit/guard/test_protected.py tests/unit/guard/test_protected_one_reader.py tests/unit/guard/test_runs.py tests/unit/launch/`; W2-58's commits named above (`git show`); `src/gov/guard/reads.py` where it meets W2-50's rules; `git show --stat eb0f1454` and how it resolved its conflict.
- The probe gate in `src/gov/close/command.py` (`_check_probe`) and `src/gov/close/_history.py`.

## What you probe for

Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such.

1. **W2-50's guard rules after W2-58** (every KPI line, success and failure), above all a write that W2-50's rules refused and the head lets through (fails open), or a write into the session's own folder the head now refuses (loses work):
   - a session writes under `~/gov-os-runs/<its own ticket>/` (W2 id from the ticket's external-ref, or its tk id when it has none, from `GOV_TICKET`) with Write, Edit and judged Bash targets, the path given absolute, with a leading `~` (W2-58's `841f8479` now expands it on the file tools; and in Bash), with `$HOME`, and relative from a `cd`;
   - each refusal of the KPIs, with the guard's reason: another ticket's folder; the root itself (a file directly in it, removing it); a path outside reached by `..`, a symbolic link or a hard link; a session with no ticket; any path outside the repository other than the temp folder and the own folder; `~/gov-os-workbench` and other worktrees — each in the spellings W2-58 now judges differently (`~`, the expanded form, reads that also write);
   - **Policy 2's reads against W2-50's writes:** whether any command or tool that W2-58 now lets through as a read (`reads.py`, the read rules in `decide.py`) writes under `~/gov-os-runs` (another ticket's folder, the root), under `~/gov-os-workbench`, or at the own folder's marker, without W2-50's write judgement; whether a pipe, an `rg` fed by a pipe, an interpreter in-place edit, a shell glob or a symbolic-linking copy (W2-58's `75b0a7b1`, `bf12ac1e`) reaches a path W2-50 refuses;
   - **`protected.py` after W2-58's rewrite:** the protections W2-50 added or judged (the own folder's marker; the settings file's second names, W2-50's "one reader" rule; the link rule of DEC-743 §6.1 (i) and DEC-751 item 2) still refuse as before; and whether W2-58's rewrite of `tests/acceptance/W2-50/test_w2_50_one_reader.py` (`bfc290f3`, Rewrite-Reason DEC-821) still tests W2-50's KPIs, or lowers an expectation the KPIs or a decision in force need (DEC-866: name the decisions if so).
2. **The launcher's sandbox after W2-58** (`af5d1a25`, `b9e03048`, `75b0a7b1`): the write list holds exactly the session's own folder (not the root) and the temp folder; the own folder is created on first use; another ticket's folder, the root, `~/gov-os-workbench` and other worktrees stay outside the write list; W2-58's removed Read rules do not change the write list or the deny list W2-50 relies on (the marker, W2-M363 as already accepted). Build the settings with a temporary HOME; do not start a session.
3. **Never indexed and the secrets scan (DEC-728, DEC-853)**, briefly, since their code is unchanged: confirm with `git diff` that it is; that nothing under a temporary `~/gov-os-runs` is indexed or scanned; one canary run in a temporary project that the scan still names it, and that a clean result is still reused by its hash. Do not repeat run 8's full scan probe unless the diff shows a change.
4. **The merge and the probe gate:**
   - `95fb5070` keeps both sides: its tree equals `git merge-tree --write-tree b9a5e5cd c4f2b303`; nothing of the ticket's paths or of `w2/integrate` was dropped;
   - the ticket's merge into `w2/integrate` will be clean (`git merge-tree --write-tree w2/integrate HEAD`), and its result on the ticket's paths will be this head's;
   - reading the probe gate as it stands at this head (read-only: you may import `gov.close.command` and call its readers in a script in your temporary folder, as long as nothing writes): a passing record of this head, committed after it by the orchestrator role alone, makes the earlier records (probed `fc9e6a2a…`, `56240ffb…`) earlier rounds; `eb0f1454` and `4845b9b8` lie before this head and no longer hold a probed commit after them; nothing else on the ticket's paths lies after this head. Say whether you find anything in the gate that would refuse a passing record of this head, or let a stale probe pass.
5. **Suites, as far as your sandbox runs them:** `tests/acceptance/W2-50/` once to its end (its three large scan cases, `-k large`, in a command of their own), `tests/unit/guard`, `tests/unit/launch`, `tests/unit/secrets`, and `tests/acceptance/W2-58/`; report each count; name any you cannot run and why.

Out of scope (report only if they fail open in a way the accepted rows do not cover): W2-58's own Policy 2 read semantics where they do not meet W2-50's paths (W2-58's own reviews judged them); the sandbox itself (W2-21).

## Return

One message, your last, complete in itself, with no worker transcript. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

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

After the fields, the payload:
- the sandbox check (step 0); the full id of the head you probed; the `gov.__file__` line; `git status --short` before and after; the `gov retrieve` questions you asked; the guard read refusals you met (count);
- your judgement, `pass` or `fail`, under the judgement rules above and DEC-790 (a finding already accepted as a row does not fail it; only "Ordinary work: yes" with "Consequence: fails open" or "loses work" fails the probe);
- each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, whether you reproduced it, **the two lines `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`**, and whether a launched, sandboxed worker could reach it or only an unsandboxed session, or only with a precondition no session can create through the guard, with your reasons;
- what you probed and found sound;
- then the body of the probe record in Markdown, as you would have it committed: a "What was probed", "What it found" (each finding with its two lines), "Found sound" and "Judgement" list.

The lead writes the probe record from your return; you repair nothing (MR-4). Refused twice for the same call: stop and say so; no third try.
