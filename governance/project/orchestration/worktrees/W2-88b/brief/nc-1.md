Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-88b/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Independent auditor brief: W2-88b (DAEO-aks1), the narrow independent check of the smoke run's record

You are a fresh **independent-auditor** session, read-only except for your own record. You ran no stage, wrote no part of the record, and are not the A5 auditors. Your one job: check `experiments/W2-88/smoke-run.md` (commit 9aa5957befb4f3b49f60889c5a63c20b07b8e616 on branch w2/W2-88b, worktree `/home/usain/gov-os-worktrees/W2-88b`) against the ticket's KPI lines S1 to S5 and failure lines F1 to F3, each by its own `Verify:` clause, and against the logs it cites. This is the narrow check of a research record (the CTO's instruction for this ticket); it is not a review of gov adopt's code and **not a validation of memory**.

## The ground
- The ticket: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-aks1.md` (S1 to S5, the `failure:` list as F1 to F3 in order, the body's "Re-scoped by the owner (DEC-1176)" part). The decision: DEC-1176 in `/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md` (line 15068; grep by id only). `gov context`'s packet for this ticket is stale (pre-DEC-1176): do not use it.
- The copies (read only; read-only git commands only): `/home/usain/gov-os-runs/W2-88b/redis/`, `/home/usain/gov-os-runs/W2-88b/grafana/`.
- The logs (read only): `/home/usain/gov-os-runs/W2-88b/<name>-logs/` (`stages.tsv`, `<label>.log` with `exit_code:` lines, `setup.log`, `post-driver.log`), gov's outputs `/home/usain/gov-os-runs/W2-88b/<name>-out/`.
- The driver that ran the stages: `/home/usain/gov-os-worktrees/W2-88b/.gov-runtime/scratch/lead/stages.sh`. A5's gate: `src/gov/adopt/stages.py:432-461`.
- The ticket's own commits on the branch start after `f2b1d38af` (`git log f2b1d38af..HEAD`). Two paths in that range are not the run's writes and are known to the lead: `.tickets/DAEO-aks1.md` (the CTO's ticket edit, commit c0cfe3099) and your own record under `docs/probes/DAEO-aks1/` (the CTO's instruction places it there). Judge S3's and F2's diff checks on the remaining paths, and say in your record that you did.

## What you check (each with the command you ran and its result)
1. **S1**: each section names the clone path under `~/gov-os-runs/W2-88b/`, a 40-hex commit, the tracked-file count and the licence; `git -C <copy> rev-parse HEAD` prints the commit the record says it prints; `git log --all -S'gov-os-runs/W2-88b/redis' --oneline` and the same for grafana, and `git ls-files | grep -E '^(redis|grafana)/'`, in this worktree, find no clone content (paths in the record's own text are expected; a clone's files are not).
2. **S2**: one row per stage MA, A0, A1, A2, A3, A4, A5, A6, A8, A9 per copy, each with command, exit code, start, end, outcome; each exit code equals its log's `exit_code:`; no recorded command carries `--questions`.
3. **S3**: every non-zero row has a findings entry naming stage, command, exit code, refusal code and error text; the stages after it are marked not reached naming it; both sections have an MA row; the diff check as above.
4. **S4**: each A5 row names the verdict file, its commit in the copy (check `git -C <copy> log -1 --format='%H %(trailers:key=Role,valueonly)' -- docs/audit/A5-path-map-verdict.md`: Role `independent-auditor` alone) and the auditor session id, which differs from the stages' session (`lead-ac1f3754-…`, in the stage records under `governance/adoption/` in the copy).
5. **S5 / F3**: the sentence "No questions, no measure, no validation." is present; `grep -inE 'hit@5|hit_at_5|right_e2e|right end to end|wrong claim|wrong_claims|mrr|recall|accuracy|query_ms|vector_scan_ms' experiments/W2-88/smoke-run.md` finds nothing; no question set, quality figure or claim that memory works; secrets named by path and rule id only; `gitleaks detect --no-git --source experiments/W2-88/smoke-run.md` (if gitleaks is missing in your sandbox, say so).
6. **F1**: no path under `~/gov-os-workbench/`, `~/workspace` (as a path: `/home/usain/workspace`, `~/workspace`) or `~/EXAMIN APP` in the record or in any log under `/home/usain/gov-os-runs/W2-88b/` (grep for the paths; never list or open those folders themselves).
7. **F2**: `git status --short` in this worktree lists nothing outside `experiments/W2-88/` (and your own record before you commit it).
8. Anything in the record that the logs contradict (a time, a figure, an outcome, a finding's text).

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

## What you write and commit (your only write)
One file, `/home/usain/gov-os-worktrees/W2-88b/docs/probes/DAEO-aks1/PR-DAEO-aks1-record-check.md`: front matter (`id: PR-DAEO-aks1-record-check`, `type: probe`, `status: ACTIVE`, `state_class: EVIDENCE`, `task: DAEO-aks1`, `record: experiments/W2-88/smoke-run.md`, `record_commit: <40 hex>`, `auditor_session: <printenv CLAUDE_CODE_SESSION_ID>`, `verdict: pass|fail`), then each check above with its command and result, each finding with its two lines (`Ordinary work: …`, `Consequence: …`), and a fenced `verdict` block in the form above, one entry per KPI line (S1 to S5, F1 to F3). Commit it alone, the trailers in one final paragraph:
```
git -C /home/usain/gov-os-worktrees/W2-88b add -- docs/probes/DAEO-aks1/PR-DAEO-aks1-record-check.md
git -C /home/usain/gov-os-worktrees/W2-88b commit -q -m "W2-88b (DAEO-aks1): the narrow independent check of experiments/W2-88/smoke-run.md" --trailer "Task: DAEO-aks1" --trailer "Role: independent-auditor" -- docs/probes/DAEO-aks1/PR-DAEO-aks1-record-check.md
git -C /home/usain/gov-os-worktrees/W2-88b log -1 --format='%H%n%(trailers)'
```
Write nothing else anywhere. Do not run gov adopt, gov rebuild or any stage; do not write in the copies.

## Rules
- Reads are open except: secrets (never printed), the held-out qualification material's contents, the counterpart's work, the hidden half of an evaluation set. Never read, list or stat `~/gov-os-workbench/`, `~/workspace`, `~/EXAMIN APP`, the evaluation sets' root or any hidden folder.
- No `gov retrieve` and no `gov context`; search with Read and Grep, and search again once in different words before you say "not found".
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so in your return; never work around a refusal.

## Return (your last message; only it is read)
The twelve fields, each a labelled line ("none" where nothing):
`task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:`
In `evidence`: your record's path and commit with its trailers as `git log` prints them, your session id, and the per-line verdicts. End with the fenced `verdict` block.
