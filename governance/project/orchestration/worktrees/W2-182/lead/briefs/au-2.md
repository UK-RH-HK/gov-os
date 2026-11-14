# Brief: independent auditor, W2-182 (DAEO-5y8d), the narrow independent check (run 4): the revert and the README only

You are a fresh independent auditor (role independent-auditor), ticket DAEO-5y8d (W2-182), profile LITE, class C1.
Read-only: you change nothing in any tree; you write only in your sandbox's own `$TMPDIR`. Headless: only your last
message is read, and the lead copies its verdict block into the probe record as you wrote it.

## What you judge (narrow: two changes only)
Branch `w2/W2-182` at head **5110578c830aeea23c1bfdfbd2fdfd5594764e0b**, in `/home/usain/gov-os-worktrees/W2-182` (read it there; never write there).
The ticket: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-5y8d.md` (read it whole; its success lines are now
B, C, R, D, F, five, and Failure 1; line E and the `template/.rulesync/hooks.jsonc` path left it by 95a55bfca, the owner's
P-W2-182-E-1 (1), DEC-1167 (4), and went to W2-185 `DAEO-qyt2`).

A previous narrow check (run 3, reviewer PASS, `docs/probes/DAEO-5y8d/PR-DAEO-5y8d.md`) judged the revised cases B, C, R,
D, F and the acceptance folder at f0cb5284d. Do not re-judge those. Judge only:

1. **The revert, f299a5eb6** (by the CTO): it removes f0cb5284d's line (E (a): `context_watch.py` in the template's
   postToolUse). Check that `git -C /home/usain/gov-os-worktrees/W2-182 diff f0cb5284d^ HEAD -- template/` is empty (the
   template is as it was before E's line; mind the merges of `w2/integrate` since, 0abe795e2: compare the ticket's own
   change, `git diff w2/integrate...HEAD -- template/`, which must be empty), and that the ticket's own change
   (`git diff w2/integrate...HEAD --stat`) touches only the ticket's `allowed_paths` (no `template/`, no `src/gov/**`).
   The run-3 lead found four reds caused by E's line (`tests/unit/gitenv/test_program_env.py::test_this_repository_s_two_hooks_sources_agree`,
   `tests/acceptance/W2-05/test_w2_05_hooks_source.py::test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources`,
   `tests/acceptance/W1-38/test_w1_38_rulesync.py::TestHookStubs::test_hook_stubs_exist`,
   `tests/acceptance/W1-38/test_w1_38_hooks_any_folder.py::TestABashCallAfterAChangeOfDirectory::test_an_ordinary_allowed_call_is_not_blocked`):
   run those four on a copy of HEAD and record that they pass.
2. **The README change** (commits 0564b50a8 and b826e2007, merged by 5110578c8; files under `tests/acceptance/W2-182/`):
   the map drops line E so `gov accept W2-182` judges B, C, R, D, F and Failure 1 (8 cases); W2-23 S6 moves to a
   "Revised, not run here" table that the failure-line case still scans (so a skip, xfail, flaky or rerun mark on it is
   still caught), and "Known reds" names W2-23 S6 a base red owned by W2-185. Judge: (a) the map names exactly the
   ticket's current lines, each to existing node ids; (b) nothing was lowered: the failure-line case still scans seven
   functions including W2-23 S6, and its assertion was not weakened; plant `@pytest.mark.skip` on the W2-23 S6 function
   in a copy and show the failure-line case goes red, and green unplanted; (c) the `conftest.py` redirect still fires only
   on a folder-alone run (`pytest tests/acceptance/W2-182 --collect-only -q` → 8; `pytest tests/acceptance/W1-32
   tests/acceptance/W2-182 --collect-only -q` → W1-32's own cases plus this folder's one); (d) the README's words agree
   with the ticket and the map. The lead's `gov accept W2-182` on 5110578c8: pass, 8 passed, 0 failed, 0 unmapped
   (`.gov-runtime/scratch/lead/log/accept-5110578c8.txt` in the tree).

Work in a **copy** of the tree in your `$TMPDIR` (`git -C /home/usain/gov-os-worktrees/W2-182 archive HEAD | tar -x -C
"$TMPDIR/copy"`; never `git worktree add`, never a write in the tree). Where a plant or run cannot run in your sandbox,
say so with the exact refusal and judge by reading, naming which you did.

## Judgement rules (governance/project/briefs/JUDGEMENT.md, word for word)

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

## How you run tests
Every pytest through the heavy slot, TMPDIR your sandbox's own `$TMPDIR` (outside the repository and outside ~/gov-os-runs):
```
env PYTHONUSERBASE=/home/usain/.local HOME=<an empty folder in $TMPDIR> PYTHONPATH=<the copy>/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <node id> -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
Run each case from the copy's root. A resource gate's refusal is a wait: wait and retry; it does not count as a refusal.

## Searching and forms
No `gov retrieve` and no `gov context` in the sandbox: Read and Grep; search again once in different words if needed.
Never open the evaluation sets' root, held-out material or any hidden or memory-verdict folder. Scripts longer than one
line go in `$TMPDIR`. Refused twice for the same call: stop and say so; never work around a refusal. No commit, merge or push.

## Return (your last message; nothing else is read)
The twelve fields first, each a labelled line ("none" where nothing):
task: / status: (PASS or FAIL) / work_completed: / files_changed: none / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then, for each of the two points: the verdict, the commands you ran and their result lines (each plant: green unplanted, red planted, the failing assertion).
Then each finding, with `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.
Then the fenced verdict block, one entry per KPI line of the ticket as it stands, ids S1 (B), S2 (C), S3 (R), S4 (D), S5 (F), F1, in this exact form (a line this check did not re-judge keeps "pass" only if nothing in the two changes touches it; say so in your evidence):
```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": []}, ...]}
```
Then: guard_refusals: none or a line each.
