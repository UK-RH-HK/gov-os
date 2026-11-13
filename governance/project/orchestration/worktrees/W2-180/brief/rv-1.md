# Review 1 of W2-180 (DAEO-weh2), a test revision of W2-170's F5 path case and W2-173's F3/F4 branch-names cases: a fresh, read-only LITE review

Budget: projection 3 USD.

You are a fresh, read-only independent reviewer (role `independent-auditor`, class C1, Opus at effort high, RUBRIC-2). You read everything and change nothing. You probe the head of `/home/usain/gov-os-worktrees/W2-180` against the ticket's KPI lines S1, F1 and F2 (and its section "Widened"). LITE profile: one round.

## Step 0, before any work: the sandbox check, reported first in your return
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-weh2','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` (both in `/home/usain/gov-os-worktrees/W2-180`) must work.
If (a) wrote the file or (b) failed, stop there and return. Then: `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-weh2`).

## The head you probe
`0d98914dc37f` on branch `w2/W2-180`. `git -C /home/usain/gov-os-worktrees/W2-180 rev-parse HEAD` must begin with it **at your start and at your end**; if it differs, stop and say so. Base: `6c9a5bb525ee` (the merge-base with `w2/integrate`, which holds the widened ticket). The change: two independent test designer commits, `e3ff31fc5f87` (W2-170's F5, batch 1) and `56f401a86c90` (W2-173's F3/F4, batch 2), each merged by the lead. Read `git -C /home/usain/gov-os-worktrees/W2-180 diff 6c9a5bb525ee 0d98914dc37f` first.

## The defect the revision answers (facts)
W2-170's `test_f5_the_branch_changes_only_paths_the_ticket_allows` and W2-173's `test_f3_...`/`test_f4_...` diffed whatever
branch the suite ran on against its merge-base with `w2/integrate` and judged the names against **their own** ticket's
paths. So they were red on every later ticket's branch that changes other paths (W2-171, W2-178) and on the merge queue's
candidate merge of such a ticket (a detached HEAD), attributed to that ticket's batch: this morning the queue ejected W2-121
and W2-179 on W2-170's F5. The CTO's ruling (PKG-W2-171-F5-1 in `.tickets/DAEO-k1e2.md`; this ticket's "Widened" section):
each case judges only its own ticket's branch (`w2/W2-170`, `w2/W2-173`) and is skipped, with its reason named, on any other
branch, a candidate merge, `w2/integrate` or a clone's checkout.

## What you judge
- The ticket `/home/usain/gov-os-worktrees/W2-180/.tickets/DAEO-weh2.md`: S1, F1, F2, "Widened". Sources DEC-866 (the Rewrite-Reason), DEC-253, DEC-966, DEC-989: read each by id in `docs/DECISION_REGISTER.md`.
- `tests/acceptance/W2-170/test_w2_170_f5_paths.py` (`judge_f5_paths` and its planted cases), `tests/acceptance/W2-173/test_w2_173_unchanged.py` (`_skip_unless_own_branch`, `judge_f3_paths`, `judge_f4_paths`, the planted cases), both READMEs' changed lines; `w2_170_world.py` (`TREE`, `git`) and `w2_173_support.py` / its `support` (`TREE`, `git`) as context.
- The questions: on the own branch, is the judgement exactly the earlier one (same base, fallback, diff, allowed set, matcher, asserts), so a change outside the paths still fails (F1)? Is every other checkout skipped with its reason, never red and never passed silently (S1)? How is the branch read (from the test file's own repository, not the current directory or an environment variable), and can the skip fire on the own ticket's real branch in ordinary work (e.g. a worktree, a branch with the own name checked out under another spelling), which would let a real breach through (fails open)? Do the planted cases exercise the same functions the real cases call, and would they catch a revision that skipped everywhere or judged everywhere? Is anything else loosened, removed or skipped (F2)? Does the branch diff list only the four allowed paths (F2)? Are both commits' Rewrite-Reason trailers present (DEC-866)?
- **Out of this review:** the code under test of W2-170 and W2-173, the other cases of both folders (unchanged), other tickets' path cases (the ticket's non-goal), and anything that needs a deliberate construction: a row, not a round.

## What the lead ran (do not re-run these)
- td-1's folder run of `tests/acceptance/W2-170`: 184 passed, 1 skipped (the real F5, on `w2/W2-180-tests`). td-2's: W2-173 91 passed, 2 skipped (the real F3, F4); W2-170 184 passed, 1 skipped.
- The lead's `lead_verify` on the head (the scoped run plus the wider net) and a spot check in a clone under `/tmp`, the head checked out as the branch `w2/W2-170`, as `w2/W2-173` and detached: record `/home/usain/gov-os-worktrees/W2-180/.gov-runtime/scratch/lead/log/clone-check.txt` (read it).

## How you work
- Read with the Read and Grep tools; one simple command per Bash call; no `cd … &&` chains (use `git -C` or full paths); no here-documents, backticks or `$(…)`; anything longer goes in a script file under your sandbox's TMPDIR, run by its path. **`gov retrieve` is not available in your sandbox** (DEC-1064/1065): if a search does not answer, or your answer may be incomplete, search once more in your own, different words; then answer from both with path and lines, or say "not found". Two searches in all. Read the register only by id.
- **Re-run nothing the lead ran.** Run code only to probe a finding: you may import the judgement functions and call them on planted `git init` repositories under your sandbox's TMPDIR; every Python process with `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-180/src` per command, `HOME` an empty folder under your TMPDIR, no network, no real embedder or model, never the full suite, no installs. A pytest run, if you need one, of one file only, through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with `TMPDIR` your sandbox's TMPDIR, `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`. Show the code under test once: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/usain/gov-os-worktrees/W2-180/src python3 -c "import gov; print(gov.__file__)"`.
- **You write nothing in any tree.** `git -C /home/usain/gov-os-worktrees/W2-180 status --porcelain` must be empty when you finish. Clean your TMPDIR as you go. Budget: 2 GB and 100,000 files and folders (DEC-898); report `du -sh` and `du -s --inodes` of your TMPDIR in `evidence`.
- **Read refusals (DEC-849):** take a refusal, never look for another form. Count the refusals you met in your return.
- **Protected material (DEC-820, DEC-1097):** never read secrets or keys; never open or list the real sets root `~/gov-os-eval` or the real run folders `~/gov-os-runs`; never read or name the qualification oracle; never write in `~/gov-os-workbench`.
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
- `task: DAEO-weh2` and `decisions:` (the ids your findings rest on); `probed_commit: <the full id of 0d98914dc37f>`.
- **Scope** and **Method** (what you planted and ran, how many times).
- **Probed and found sound**, per question above.
- **Findings**, each described as behaviour (what was done, what happened, what should have happened), never as code (DEC-136), each with `scope: in|out`, `Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`, and what evidence would reverse it (DEC-1014). Name both ids where a superseded or PROPOSED rule is in use (DEC-1073).
- The classification on one line (counts of yes/fails open or loses work; yes/other; rows).
- At the end, the fenced block, one entry per KPI line, ids exactly `S1`, `F1`, `F2`, each finding listed under the line it concerns (a finding on no line goes under the nearest one, `scope: out`). Name your own findings `RV1`, `RV2` … so they are not confused with the KPI ids:
```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "RV1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```
Refused twice for the same call: stop and say so.
