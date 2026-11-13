# Review 1 of W2-181 (DAEO-ywb5), a test revision of W2-157's F4 path case: a fresh, read-only LITE review

Budget: projection 3 USD.

You are a fresh, read-only independent reviewer (role `independent-auditor`, class C1, Opus at effort high, RUBRIC-2). You read everything and change nothing. You probe the head of `/home/usain/gov-os-worktrees/W2-181` against the ticket's KPI lines S1, F1 and F2. LITE profile: one round.

## Step 0, before any work: the sandbox check, reported first in your return
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ywb5','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` (both in `/home/usain/gov-os-worktrees/W2-181`) must work.
If (a) wrote the file or (b) failed, stop there and return. Then: `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-ywb5`).

## The head you probe
`499543a836d3` on branch `w2/W2-181`. `git -C /home/usain/gov-os-worktrees/W2-181 rev-parse HEAD` must begin with it **at your start and at your end**; if it differs, stop and say so. Base: `1f626332fde0` (the merge-base with `w2/integrate`). The change: one independent test designer commit, `120474643433` (Sonnet high), merged by the lead with `--no-ff` (`499543a836d3`). `git -C /home/usain/gov-os-worktrees/W2-181 diff --name-only 1f626332fde0...HEAD` should list only `tests/acceptance/W2-157/test_w2_157_nothing_else.py` and `tests/acceptance/W2-157/README.md`.

## The defect the revision answers (facts)
W2-157's `test_f4_the_branch_changes_only_the_tickets_allowed_paths` diffed whatever branch the suite ran on against its
merge-base with `w2/integrate` and judged the names against **W2-157's own** ticket paths (`.tickets/DAEO-ozyt.md`). So it
was red on every later ticket's branch that changes other paths (the next in `src/gov/resources/` is W2-121c) and on the
merge queue's candidate merge of such a ticket (a detached HEAD); W2-157 itself was ejected from a batch at 07:46 on the
same form (DECIDED-NOT-DONE row 171). W2-180 (DAEO-weh2) fixed W2-170's F5 and W2-173's F3/F4 the same way; this is the
last such case found on integrate. The ruling: the case judges only `w2/W2-157` and is skipped, with its reason named
(the branch found, or "detached HEAD"), on any other branch, a candidate merge, `w2/integrate` or a clone's checkout.

## What you judge
- The ticket `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-ywb5.md`: S1, F1, F2, non-goals. Sources DEC-866 (the Rewrite-Reason), DEC-253, DEC-966, DEC-989: read each by id in `/home/usain/gov-os-worktrees/W2-181/docs/DECISION_REGISTER.md`.
- `tests/acceptance/W2-157/test_w2_157_nothing_else.py` (`judge_f4_paths`, `allowed_paths`, the real case and the six planted cases) and the README's changed lines; `w2_157_support.py` (`ROOT`, `SAFE_PATH`) as context. The form it copies: `git -C /home/usain/gov-os-worktrees/W2-181 show w2/W2-180:tests/acceptance/W2-170/test_w2_170_f5_paths.py`.
- The questions: on `w2/W2-157`, is the judgement exactly the earlier one (same base, diff, allowed set from the ticket's `allowed_paths` with comments dropped, fnmatch matcher, the acceptance folder prefix, asserts), so a change outside the paths still fails (F1)? Is every other checkout skipped with its reason, never red and never passed silently (S1)? How is the branch read (from the repository the test file sits in, not the current directory or an environment variable)? Do the planted cases really prove each outcome (fail on w2/W2-157 with an outside path; pass with an inside one; skip on w2/W2-121c, on a detached candidate merge and on w2/integrate)? Are the S5 cases in the file unchanged? Does the commit carry `Task: DAEO-ywb5`, `Implements:` from the ticket's sources and a `Rewrite-Reason:` naming this ticket?
- **Out of this review:** W2-157's code under test, the other cases of the folder (unchanged), other tickets' path cases (the ticket's non-goal), and anything that needs a deliberate construction: a row, not a round.

## What the lead ran (do not re-run these)
- td-1's folder run of `tests/acceptance/W2-157`: 121 passed, 1 skipped (the real F4, on `w2/W2-181-tests`: "F4 judges only the branch w2/W2-157; this is the branch w2/W2-181-tests: not judged here"); its scratch mutation (branch check removed) turned the three skip cases red.
- The lead's `gov accept W2-181` on the head: 121 passed, 1 skipped, 0 failed (record `/home/usain/gov-os-worktrees/W2-181/.gov-runtime/scratch/lead/log/accept-1.txt`).
- The lead's `lead_verify` on the head (record `/home/usain/gov-os-worktrees/W2-181/.gov-runtime/scratch/lead/log/verify/summary.txt`) and its re-run of eight timing-sensitive unit cases alone (`.../lead/log/rerun-reds.txt`).
- A clone check under `/tmp`, the head checked out as `w2/W2-157` (clean, then with a change outside its paths), as `w2/W2-121c` and as a detached candidate merge: record `/home/usain/gov-os-worktrees/W2-181/.gov-runtime/scratch/lead/log/clone-check.txt` (read it).

## How you work
- Read with the Read and Grep tools; one simple command per Bash call; no `cd … &&` chains (use `git -C` or full paths); no here-documents, backticks or `$(…)`; anything longer goes in a script file under your sandbox's TMPDIR, run by its path. **`gov retrieve` is not available in your sandbox** (DEC-1064/1065): if a search does not answer, or your answer may be incomplete, search once more in your own, different words with Read and Grep; then answer from both, or say "not found".
- **Re-run nothing the lead ran.** Run code only to probe a finding: you may import `judge_f4_paths` and call it on planted `git init` repositories under your sandbox's TMPDIR; every Python process with `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-181/src` per command, `HOME` an empty folder under your TMPDIR, no network, no real embedder or model. Any pytest goes through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest … -p no:cacheprovider -o tmp_path_retention_policy=failed` with `TMPDIR` outside the repository and outside ~/gov-os-runs and `PYTHONUSERBASE=/home/usain/.local`.
- **You write nothing in any tree.** `git -C /home/usain/gov-os-worktrees/W2-181 status --porcelain` must be empty when you finish. Clean your TMPDIR as you go. Budget: 2 GB and 100,000 files and folders (DEC-898); report `du -sh` and `du -s --inodes` of your TMPDIR in `evidence`.
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
- `task: DAEO-ywb5` and `decisions:` (the ids your findings rest on); `probed_commit: <the full id of 499543a836d3>`.
- **Scope** and **Method** (what you planted and ran, how many times).
- **Probed and found sound**, per question above.
- **Findings**, each described as behaviour (what was done, what happened, what should have happened), never as code (DEC-136), each with `scope: in|out`, `Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`, and what evidence would reverse it (DEC-1014). Name both ids where a superseded or PROPOSED rule is in use (DEC-1073).
- The classification on one line (counts of yes/fails open or loses work; yes/other; rows).
- At the end, the fenced block, one entry per KPI line, ids exactly `S1`, `F1`, `F2`, each finding listed under the line it concerns (a finding on no line goes under the nearest one, `scope: out`). Name your own findings `RV1`, `RV2` … so they are not confused with the KPI ids:
```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "RV1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```
Refused twice for the same call: stop and say so.
