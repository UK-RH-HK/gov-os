Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

You are a fresh Independent Auditor, read-only. Ticket: DAEO-2bdu (W2-88, "Memory for any repository"), profile FULL, class C2. Review rounds are spent (round 2, the last, failed on RV2-1 and RV2-2; DEC-1010). The owner decided P1-W2-88-RV2-1 (a): fix both in this ticket, then **a narrow independent check of that change only** (DEC-1154's practice). You are that check. You probe the head **8f9571c7919d512cc4928b9bbafd4e19a67b6460** of branch `w2/W2-88` in `/home/usain/gov-os-worktrees/W2-88`. You write nothing in any repository; your return is your check.

Your budget: about 1 hour.

## Step 0, before any work (report it first in your return)
The sandbox check in the launcher's step-0 file beside this brief. Then `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-2bdu`), `git -C /home/usain/gov-os-worktrees/W2-88 rev-parse HEAD` (expect 8f9571c7919d512cc4928b9bbafd4e19a67b6460) and `git -C /home/usain/gov-os-worktrees/W2-88 status --porcelain` (expect empty). If anything differs, stop and say so. Check the head and the empty status again at the end.

## What you judge (only this)
**The change since a15de913e8c4**: `git -C /home/usain/gov-os-worktrees/W2-88 diff a15de913e8c4 8f9571c7919d512cc4928b9bbafd4e19a67b6460` — the engineer's commit af046b331e27 (`src/gov/adopt/fabric.py`, `src/gov/adopt/refactor_plan.py`, `tests/unit/adopt/test_w2_88_rv2.py`) and the test designer's cases merged at 8f9571c7919d (`tests/acceptance/W2-88/test_w2_88_rv2_undo.py`, `standin_rv2/`, two cases in `test_w2_88_s2_plan.py`, the README's "Run 5 revisions"). Judge it against RV2-1's and RV2-2's stated behaviour: round 2's record `/home/usain/gov-os-worktrees/W2-88/docs/probes/DAEO-2bdu/PR-DAEO-2bdu-round-2.md` (the findings RV2-1 and RV2-2, each "Behaviour it should have") and the binding interface the pair built to, below. Nothing else of the ticket is re-judged (round 2 passed every other line).

1. **RV2-1, fixed or not, probed:** on planted repositories in your TMPDIR, reproduce round 2's two cases (an edit during the run then a refusal or Ctrl-C; a commit during the run then a refusal) and the interface's other items: a staged file kept staged, an untracked file kept, a copy changed during the run left as it is, a replaced tracked file put back (never deleted), a copy committed during the run left, empty folders only removed, `HEAD_MOVED`'s message and details, a refusal with HEAD unmoved keeping its own code, no `reset` in the reflog. Read the code path: `install`'s failure path as well as `a9`'s.
2. **RV2-2, fixed or not:** the partial list on its own lines after `Unscanned paths:`; the one-line `all <n> tracked files` form unchanged.
3. **Fail-open or lost work brought in by the change:** any path where the new undo deletes or unstages something A9 did not write or stage, leaves A9's copies behind on a refusal with HEAD unmoved, swallows a refusal into ok, or turns an interrupt into a silent exit. W2-23's `project.restore` must be unchanged (`git diff a15de913e8c4 8f9571c7919d512cc4928b9bbafd4e19a67b6460 -- src/gov/adopt/project.py` empty).
4. **The tests:** do the acceptance cases and the unit tests assert the stated behaviour (not the code's accidents)? Do the README map rows name existing cases?
5. **Scope of the change:** each non-merge commit since a15de913e8c4 changes only the ticket's `allowed_paths`, carries `Task: DAEO-2bdu`, and its `Implements:` lists only ids from the ticket's `sources:` (`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-2bdu.md`).

## What the lead already knows (judge them; do not re-derive the decision)
- The lead's `gov accept W2-88` on 8f9571c7919d512cc4928b9bbafd4e19a67b6460: outcome pass, every KPI line pass, 214 passed, 0 failed, 0 skipped (log/accept-5.txt). The lead's scoped lead_verify runs beside you; its result goes into the record beside your check.
- The engineer names a risk outside the change: W2-23's `project.commit` still runs `git reset --hard` if A9's own record commit fails, and commits whatever is staged (including a file someone staged during the run); the window is the commit only, and `project.py` is not in this run's paths. Classify it under the rules below (a finding in scope of this change, or a note / row).
- Decided, not to re-open: the copy step at A9 and its files (B-1.1, B-1.3); the review rounds are spent; the interface's `HEAD_MOVED` name and details are the lead's statement under DEC-1052.

## The interface for run 5 (binding; the owner's decision P1-W2-88-RV2-1 (a), via the CTO; the behaviours are review round 2's, RV2-1 and RV2-2, `docs/probes/DAEO-2bdu/PR-DAEO-2bdu-round-2.md`; stated by the lead, DEC-1052, DEC-136)

Names below are the interface; nothing else about the code is promised. "The start commit" is the commit HEAD named when A9 began (before its copy step).

- **RV2-1, A9's undo (success-16; reached through success-3's refusals).** When A9 refuses or is interrupted (any exception, Ctrl-C included) **after** its copy step (the kernel files written and staged), its undo touches only what A9 itself did:
  1. **The index:** it removes from the index only the paths A9 staged, and only where the index entry is still the blob A9 staged. A path someone else staged during the run (a new file, or a re-staged edit) stays staged.
  2. **The tree:** it deletes only the files A9 wrote whose bytes are still the bytes A9 wrote, and then the folders A9 made, only when they are empty. A file A9 wrote whose bytes were changed during the run is left as it is. (Where a copy replaced a file the start commit tracks and its bytes are still A9's, that file's content at the start commit is put back; it is never deleted.)
  3. **Nothing else:** no `git reset --hard`, no checkout of any other path. A tracked file edited during the run keeps its edit; an untracked file made during the run stays; the branch is never moved by the undo.
  4. **HEAD moved:** if HEAD no longer names the start commit when the undo runs, A9 refuses with **`HEAD_MOVED`**, whose message names the start commit and the new commit (both as full or abbreviated hashes) and says nothing was reset; its details hold `{started: <start commit>, now: <new commit>, cause: <the original refusal's code, or the exception's class name, e.g. "KeyboardInterrupt">}`. The branch stays at the new commit. Steps 1 to 3 still run, judged against the new HEAD: a copy the new HEAD tracks (committed during the run) is left in the index and the tree as it is.
  5. When HEAD did not move, the refusal keeps its own code (e.g. `REBUILD_FAILED`, `FABRIC_INCOMPLETE`, `DIGESTS_INCOMPLETE`; an interrupt stays an interrupt), as today.
  6. W2-23's `project.restore` is unchanged (the other stages keep it); only A9's undo changes.
  - **Plant (the review's cases):** A9 run in a subprocess on a planted adoption (as the suite's A9 cases do), with a stand-in for `gov.rebuild.command.run` (I3: A9 "runs `gov.rebuild.command.run` in full"), installed first on the child's `PYTHONPATH`, that acts on the planted repository and then raises.
    - **Case A:** the stand-in rewrites a tracked file (bytes of the case's choosing) and stages a new file, then raises (a `GovError` such as `REBUILD_FAILED`, and, as a second parameter, `KeyboardInterrupt`). Afterwards: the refusal is the stand-in's own code (or the interrupt); HEAD is the start commit; the edited file holds the edited bytes; the new file is still staged; none of A9's copies (`.claude/skills/retrieval/…`, `.claude/skills/discovery/…`, `governance/kernel/templates/brief.md`, `governance/kernel/templates/role-cto.md`, and `governance/project/retrieval.yaml` where the repository tracked none) is in the tree or the index; `git status --porcelain` shows exactly the edit and the staged file.
    - **Case B:** the stand-in commits a new file (`git commit -- notes.md`), then raises. Afterwards: A9 is refused `HEAD_MOVED`, naming that commit; the branch head is that commit; `notes.md` is in the tree; A9's copies are in neither the tree nor the index; the reflog's newest entry is the stand-in's commit (no `reset`).
- **RV2-2, PLAN.md's unscanned list (success-2).** When the secrets scan skipped some paths (not all), `refactor-plan/PLAN.md` holds the line `Unscanned paths:` alone, and the paths follow as a list starting on the next line, each `` - `path` `` at the start of its own line. The form `Unscanned paths: all <n> tracked files` (no scan at all) stays one line. **Plant:** MA with gitleaks on `PATH` and two tracked text blobs over `assess.SCAN_LIMIT_BYTES` (RV1-3's plant); each skipped path is a `` - `path` `` line after the `Unscanned paths:` line, and no path stands on that line.

## The rules you judge by (governance/project/briefs/JUDGEMENT.md, word for word)

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

## How to probe
- Read freely: the ticket, the register by id (`/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md`), the code, the tests, the workers' logs under `/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/log/` (eng-4, td-7). Search with the Read and Grep tools (no `gov retrieve`, no `gov context` in the sandbox, DEC-1065); search again once in your own, different words; then answer from both or say "not found".
- Probe by Bash into your own TMPDIR only (DEC-1144 (7)): plant small repositories there and run the head's code with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-88/src`. Every pytest through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with `TMPDIR` your sandbox temp folder, `HOME=/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/empty-home`, `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`. A resource gate's refusal is a wait (DEC-1146). Never `-x`.
- Never write in `/home/usain/gov-os-worktrees/W2-88` or any repository; never run `gov rebuild`, `gov adopt`, `gov close` against a real repository or worktree (on a planted repository in your TMPDIR it is the probe); never touch `~/gov-os-workbench/examin/`; never open the evaluation sets' root or any hidden or memory-verdict folder. Policy 2 (DEC-820): secrets never printed; held-out qualification material's contents never read.
- No shell variable as a write target; no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces (keep commands short). **Refused twice for the same call: stop and say so** (DEC-1142 (9)). A refused form is not retried in another disguise.

## Return
One message, your last. The twelve fields first, each a labelled line; then your check in this form (the lead copies it unchanged into the probe record):

```
task: / status: (DONE, with one line) / work_completed: / files_changed: none / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

Then:
- `# W2-88 (DAEO-2bdu): narrow independent check of the RV2-1/RV2-2 fix` with `probed_commit:`, `base: a15de913e8c4`;
- `## Sandbox and identity` (step 0, head and status at start and end);
- `## RV2-1 and RV2-2` (a table: item of the stated behaviour, fixed | not fixed | partly, file:line, how you probed it);
- `## What I probed and found sound` (numbered, each with the command or file:line and the result);
- `## Findings` (new ones: id NC-n, the KPI line, severity blocker | major | minor, what is wrong, how to reproduce, the behaviour it should have, and the two lines the rules above require);
- `## Notes, not findings`;
- a fenced block tagged `verdict` holding one JSON object, in the rules' form: `{"kpis": [{"kpi": "success-2" | "success-3" | "success-16", "verdict": "pass" | "fail", "findings": [{"id": "NC-n" | "RV2-n", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}], "overall": "pass" | "fail"}`, one entry for each of success-2, success-3 and success-16 (the lines the change touches).

Refused twice for the same call: stop and say so.
