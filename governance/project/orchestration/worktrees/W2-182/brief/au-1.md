Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-182/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief: independent auditor, W2-182 (DAEO-5y8d), the narrow independent check (run 3)

You are a fresh independent auditor (role independent-auditor), ticket DAEO-5y8d (W2-182), profile LITE, class C1.
Read-only: you change nothing in any tree; you write only in your sandbox's own `$TMPDIR`. Headless: only your last
message is read, and the lead copies it into the probe record as you wrote it.

## What you judge
The change on branch `w2/W2-182` since `2bf4430f4` (the ticket's start), at head **f0cb5284d117**, in
`/home/usain/gov-os-worktrees/W2-182` (read it there; never write there). The ticket is
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-5y8d.md` (read it whole: KPI lines B, C, R, D, E, F (Success 1
to 6) and Failure 1, the allowed paths, the non-goals).

`git diff 2bf4430f4..HEAD` also carries what came in by the merge of `w2/integrate` (23e7c4971: other tickets' work, such
as W2-88a and W2-153). The ticket's own change is the diff against its merge base with integrate:
`git -C /home/usain/gov-os-worktrees/W2-182 diff w2/integrate...HEAD` (merge base 4233668ea; 14 files). Its commits (no
merges): 6e3697785 (B, C, R, D, E revised, `Rewrite-Reason: DEC-1163 (6)`), 498968115 (F, `Rewrite-Reason: DEC-1163 (1)`),
cc7867f93 and 10213e3bb (the acceptance folder `tests/acceptance/W2-182/`: the README map, conftest redirect, support,
the no-lowering case), f0cb5284d (E (a): the template's hook line, written by the CTO under a delegated P3 because the
launcher refuses a product-spec worker on this test-designer ticket, `launcher.py:63`). Confirm this yourself.

## The four points (each a verdict with evidence)
1. **Each revised case still catches its planted break**, the break the ticket's Verify column names:
   - B: an unrecorded command name added to `gov --help` (in a stand-in) fails `tests/acceptance/W1-32/test_w1_32_command_set.py::test_the_command_set_is_the_twelve_and_the_three_recorded_ones`.
   - C: W1-18: a retrieval that starts the server fails `tests/acceptance/W1-18/test_w1_18_on_demand_start.py::test_with_the_server_not_answering_a_retrieval_answers_by_keywords_and_starts_nothing`; W2-123: a retry record that is not written fails `tests/acceptance/W2-123/test_w2_123_retry.py::test_after_the_last_failed_try_the_rebuild_states_the_tries_and_waits_and_no_partial_store_is_reported_built`.
   - R: a stand-in `gov dispatch status` that writes a file fails `tests/acceptance/W2-121/test_s1_lock_off_status.py::test_s1_status_runs_no_pass_and_writes_nothing`.
   - D: a planted module outside `plan/`, `launch/` and `session_watch/` calling gov plan fails `tests/acceptance/W2-136/test_w2_136_never_a_gate.py::test_s10_no_module_of_gov_outside_plan_and_launch_imports_or_calls_gov_plan`.
   - E: a planted eighth hook script with no wiring fails `tests/acceptance/W2-23/test_w2_23_space.py::test_s6_every_kernel_hook_exits_alike_with_a_space_in_the_project_dir`.
   - F: the line "Run `gov accept` for a ticket whose suites need the code index outside the sandbox, until W2-56" planted back into `template/governance/kernel/templates/role-lead.md` fails `tests/acceptance/W2-128/test_w2_128_rows.py::test_row_8_no_unit_carries_the_gov_accept_outside_the_sandbox_until_w2_56_line[role-lead]`.
   Plant each in a **copy** of the tree in your `$TMPDIR` (for example `git -C /home/usain/gov-os-worktrees/W2-182 archive HEAD | tar -x -C "$TMPDIR/copy"`; never `git worktree add`, never a write in the tree), run the case against the copy (its own `src` on `PYTHONPATH`), and record: green unplanted, red planted, with the failing line. Where a plant cannot run in your sandbox, say so with the exact refusal and judge by reading instead, naming which you did.
2. **No mark was added**: the ticket's diff adds no skip, skipif, xfail, flaky, rerun or importorskip (beyond what was there before), and lowers no assertion. `tests/acceptance/W2-182/test_w2_182_no_lowering.py` claims to check this; judge whether it does.
3. **Only the ticket's files changed**: every path in the ticket's own change is in its `allowed_paths`; no `src/gov/**` change (a non-goal); the commits carry `Task: DAEO-5y8d` and `Implements:` only ids from the ticket's `sources:`.
4. **The README maps every line, and E's line matches the root form**: `tests/acceptance/W2-182/README.md` maps each KPI line (Success 1 to 6, Failure 1) to existing node ids, and `gov accept W2-182` runs exactly those (the lead's run on this head: 9 passed, 0 failed, every line pass; `.gov-runtime/scratch/lead/log/accept-f0cb5284d.txt`). E: compare the new entry in `template/.rulesync/hooks.jsonc` with the `context_watch.py` entry of the root `.rulesync/hooks.jsonc` (event, matcher, timeout, command, with the path the adopted project holds, `governance/kernel/hooks/`); name any difference and whether it matters.
   E's Verify also says "`python3 -m gov.adapters.portability` exits 0 on the template". The CTO measured: run inside `template/`, it exits 1 with the same nine findings before and after the line (`RULESYNC_VERSION_UNKNOWN`, and eight `TEMPLATE_COPY_MISSING` that an adopted project would hold); the line adds none. Judge E's "exits 0" against those unchanged findings: run it yourself before (parent of f0cb5284d, in a copy) and after, compare, and name it plainly if you read the KPI otherwise.

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
Then, for each of the four points: the verdict, the commands you ran and their result lines (each plant: green unplanted, red planted, the failing assertion).
Then each finding, with `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.
Then the fenced verdict block, one entry per KPI line, ids S1 (B), S2 (C), S3 (R), S4 (D), S5 (E), S6 (F), F1, in this exact form:
```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": []}, ...]}
```
Then: guard_refusals: none or a line each.
