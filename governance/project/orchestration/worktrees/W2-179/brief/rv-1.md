# Review 1 of W2-179 (DAEO-c9n8), a test revision of W2-170's F3 file-access case: a fresh, read-only LITE review

Budget: projection 3 USD.

You are a fresh, read-only independent reviewer (role `independent-auditor`, class C1, Opus at effort high, RUBRIC-2). You read everything and change nothing. You probe the head of `/home/usain/gov-os-worktrees/W2-179` against the ticket's KPI lines S1, F1 and F2. LITE profile: one round.

## Step 0, before any work: the sandbox check, reported first in your return
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-c9n8','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` (both in `/home/usain/gov-os-worktrees/W2-179`) must work.
If (a) wrote the file or (b) failed, stop there and return. Then: `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-c9n8`).

## The head you probe
`4a9d5d074834` on branch `w2/W2-179`. `git -C /home/usain/gov-os-worktrees/W2-179 rev-parse HEAD` must begin with it **at your start and at your end**; if it differs, stop and say so. Base `3eeb5cb2e98e`. The change: the independent test designer's one commit `3c1981b03b90` (two files), merged by the lead at `4a9d5d074834`. Read `git -C /home/usain/gov-os-worktrees/W2-179 diff 3eeb5cb2e98e 4a9d5d074834` first.

## The defect the revision answers (facts)
The nightly of 2026-11-12 (run 20261112-0404) was red on
`tests/acceptance/W2-170/test_w2_170_s4_map.py::test_f3_a_run_s_file_access_log_shows_no_open_of_the_true_sets_root_or_runs_folders`:
its `reached` list held 104 paths, every one a file or folder of the repository under test, because the nightly's clone
lives at `~/gov-os-runs/W2-00/nightly/<run>/`, inside the true runs folder the case watches. The code under test
(`src/gov/memaudit/**`, W2-170, closed) is not at fault and is out of this review.

## What you judge
- The ticket `/home/usain/gov-os-worktrees/W2-179/.tickets/DAEO-c9n8.md`: S1, F1, F2. Sources DEC-820 ((b), (d): held-out material and the hidden half), DEC-866 (the Rewrite-Reason), DEC-966, DEC-1101: read each by id in `docs/DECISION_REGISTER.md`.
- The revised case and its helper `_true_root_opens` in `tests/acceptance/W2-170/test_w2_170_s4_map.py`; the README lines changed; `tests/acceptance/W2-170/w2_170_world.py` (`HERE`, `TRUE_HOME`, `TRUE_SETS`, `TRUE_RUNS`, `at_or_under`) and `w2_170_open_log.py` (what the log records) as context.
- The questions: does the exclusion let through only the repository's own files (its root taken from the test file's place), wherever the repository lives? Can a true runs-folder or sets-root open outside the repository slip past it (F1): spelling (`..`, symlinks, a sibling folder with the same prefix), the normal form used on each side, the guard that the repository root is narrower than every true root? Is anything else of the case loosened, removed or skipped (F2)? Does the case still open nothing under the true roots (DEC-820)? Is the commit's Rewrite-Reason trailer present (DEC-866)?
- **Out of this review:** the memory audit's code, the other W2-170 cases (unchanged), and anything that needs a deliberate construction (a symlink planted on purpose inside the true runs folder pointing into the repository, and the like): a row, not a round.

## What the lead ran (do not re-run these)
- On head `4a9d5d074834`: in a fresh `--no-hardlinks` clone under `~/gov-os-runs/W2-179/clone` and in one under `/tmp`: the case as merged passed in both; the case with one synthetic log entry `~/gov-os-runs/W2-179/planted-outside/x.txt` (outside the clone, nothing opened) failed in both with that path alone in `reached`; with a synthetic entry of the clone's own `src/gov/memaudit/__init__.py` it passed in both; the pre-revision case in the clone under `~/gov-os-runs` failed with the repository's own files (the nightly's red reproduced). Both clones are removed. Record: `/home/usain/gov-os-worktrees/W2-179/.gov-runtime/scratch/lead/log/clone-check.txt`.
- The designer's folder run: 179 passed. The lead's `lead_verify` (the scoped run plus the wider net) beside you.

## How you work
- Read with the Read and Grep tools; one simple command per Bash call; no `cd … &&` chains (use `git -C` or full paths); no here-documents, backticks or `$(…)`; anything longer goes in a script file under your sandbox's TMPDIR, run by its path. **`gov retrieve` is not available in your sandbox** (DEC-1064/1065): if a search does not answer, or your answer may be incomplete, search once more in your own, different words; then answer from both with path and lines, or say "not found". Two searches in all. Read the register only by id.
- **Re-run nothing the lead ran.** Run code only to probe a finding: you may import the helper `_true_root_opens` (or reproduce its logic) and call it with synthetic path strings and substituted roots under your sandbox's TMPDIR; every Python process with `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-179/src` per command, `HOME` an empty folder under your TMPDIR, no network, no real embedder or model, never the full suite, no installs. Show the code under test once: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/usain/gov-os-worktrees/W2-179/src python3 -c "import gov; print(gov.__file__)"`.
- **You write nothing in any tree.** `git -C /home/usain/gov-os-worktrees/W2-179 status --porcelain` must be empty when you finish. Clean your TMPDIR as you go. Budget: 2 GB and 100,000 files and folders (DEC-898); report `du -sh` and `du -s --inodes` of your TMPDIR in `evidence`.
- **Read refusals (DEC-849):** take a refusal, never look for another form. Count the refusals you met in your return.
- **Protected material (DEC-820, DEC-1097):** never read secrets or keys; never open or list the real sets root `~/gov-os-eval` or the real run folders `~/gov-os-runs` (synthetic path strings only); never read or name the qualification oracle; never write in `~/gov-os-workbench`.
- **Row W2-L423's rule (DEC-911):** write commit hashes as 12 digits, never the full 40, except the one `probed_commit` line, and never write the keywords of the secrets rule that takes a bare 40-hex string; call it "row W2-L423's rule".
- **Refused twice for the same call: stop and say so; no third try.** Never work around a refusal.
- Estimate: about 15 minutes.

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
- **How reviews converge (owner, standing, DEC-1010 item 1; in force for the CTO, every lead, reviewer and QA engineer):**
  - **A moderator, not a circle of reviewers:** the QA engineer (or the Senior Engineer; until the three layers start, the CTO) triages every finding against the ticket's own scope and KPIs. A finding outside the scope, or one that needs an unusual construction, becomes a Wave 3 row, never a round.
  - **A finding blocks only if it is in scope, reachable in ordinary work, and fails open or loses work.** Everything else lands as a recorded row.
  - **At most two review rounds.** If something still blocks after that, it goes to the owner once, with options; no more routine exceptions.
  - **READY is computed by code, not declared by an agent:** each reviewer returns a structured verdict per KPI line, a fenced `verdict` block in the probe record: `{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`; the close (and the merge queue's pre-check) computes READY from it: no finding that is in scope, ordinary work yes and fails open or loses work. A lead never writes a verdict over a reviewer's.

## Your record (your session's final message, in full; you write no file)
The twelve fields first, each a labelled line ("none" where nothing):
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
Put step 0's result first in `evidence`, then the head at start and end, the `gov.__file__` line, your session id if you know it, your TMPDIR's measures, the read refusals counted.

Then the probe record body:
- `task: DAEO-c9n8` and `decisions:` (the ids your findings rest on); `probed_commit: <the full id of 4a9d5d074834>`.
- **Scope** and **Method** (what you planted and ran, how many times).
- **Probed and found sound**, per question above.
- **Findings**, each described as behaviour (what was done, what happened, what should have happened), never as code (DEC-136), each with `scope: in|out`, `Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`, and what evidence would reverse it (DEC-1014). Name both ids where a superseded or PROPOSED rule is in use (DEC-1073).
- The classification on one line (counts of yes/fails open or loses work; yes/other; rows).
- At the end, the fenced block, one entry per KPI line, ids exactly `S1`, `F1`, `F2`, each finding listed under the line it concerns (a finding on no line goes under the nearest one, `scope: out`). Name your own findings `RV1`, `RV2` … so they are not confused with the KPI ids:
```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "RV1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```
Refused twice for the same call: stop and say so.
