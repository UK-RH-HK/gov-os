# Brief: independent auditor, W2-185 (DAEO-qyt2), the narrow independent check (STANDARD review, round 1)

You are a fresh independent auditor (role independent-auditor), ticket DAEO-qyt2 (W2-185), profile STANDARD, class C2.
Read-only: you change nothing in any tree; you write only in your sandbox's own `$TMPDIR`. Headless: only your last
message is read, and the lead copies its verdict block into the probe record as you wrote it.

## What you judge
Branch `w2/W2-185` at head **1180e4ec5e13** (`git -C /home/usain/gov-os-worktrees/W2-185 rev-parse HEAD` gives the full
hash; quote it), in `/home/usain/gov-os-worktrees/W2-185` (read it there; never write there). The ticket's own change is
`git -C /home/usain/gov-os-worktrees/W2-185 diff 31eab2103..HEAD` (base 31eab2103: the claim). The ticket, read it whole:
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-qyt2.md` (S1, S2, S3, F1 with their Verify clauses; the
non-goals; `allowed_paths`). Decisions, grep the register by id only
(`/home/usain/gov-os-worktrees/W2-185/docs/DECISION_REGISTER.md`): DEC-1167 (4), DEC-971 item 3, DEC-805, DEC-1163 (6),
DEC-1156 (7).

Commits: a0558ff7d (engineer: S1 template line, S2 in `src/gov/adapters/portability.py`, unit cases
`tests/unit/adapters/test_w2_185_hooks_exemption.py`); 58f95c15a, a3a97706d, 2230cce50 (test designer: W1-38's
`HOOK_SCRIPTS` with seven hooks, `tests/acceptance/W2-185/`), merged by e062f921e and 1180e4ec5 (the lead).

Judge, each against its KPI line:
1. **S1:** the template's new `postToolUse` entry equals the root `.rulesync/hooks.jsonc`'s `context_watch.py` entry byte
   for byte except the path `governance/kernel/hooks/` (matcher `Bash`, timeout 10), and the `posttooluse.py` entry stays;
   W2-23 S6 (`tests/acceptance/W2-23/test_w2_23_space.py`) passes; a planted eighth hook script with no wiring fails it.
2. **S2:** the exemption is per hook, not per event. The engineer made it conditional: the template's entries running
   `posttooluse.py` in `postToolUse`/`postToolUseFailure` are left out only while the root's source does not run
   `posttooluse.py` in that event (its reason: W2-05's cases that a lifted event back in both sources compares as any
   other), matched by the substring `posttooluse.py` in the command. Judge it against the KPI line and DEC-971 item 3
   (an exception covering exactly what ACT 1 lifted, named in the comparison, ending when it returns with W2-08).
   `tests/unit/gitenv/test_program_env.py::test_this_repository_s_two_hooks_sources_agree`,
   `tests/acceptance/W2-05/test_w2_05_hooks_source.py::test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources`
   and the unit file pass.
3. **S3:** `HOOK_SCRIPTS` holds the seven kernel hooks; `tests/acceptance/W1-38/test_w1_38_rulesync.py::TestHookStubs::test_hook_stubs_exist`
   and `tests/acceptance/W1-38/test_w1_38_hooks_any_folder.py::TestABashCallAfterAChangeOfDirectory::test_an_ordinary_allowed_call_is_not_blocked`
   pass; with the fixture's six hooks (planted in a copy) they fail.
4. **F1:** in a copy, a planted extra matcher on the root's `postToolUse`, and a planted template hook in another event,
   each give a hooks finding (`python3 -m gov.adapters.portability` or `_hooks_findings` over the copy).
5. **Scope:** the change touches only `allowed_paths` plus the ticket's acceptance folder `tests/acceptance/W2-185/`;
   nothing of the root's `.rulesync/hooks.jsonc` or `.claude/` (a non-goal); trailers `Task: DAEO-qyt2` on each commit,
   `Implements:` ids from the ticket's `sources:` only; the W1-38 revision carries `Rewrite-Reason:`.
6. **The reds outside the ticket's paths.** The lead's whole-suite run on 1180e4ec5 had six reds this change causes, in
   files outside `allowed_paths` (the CTO revises them under DEC-1156 (7)); judge, for each, whether it is a test pinning
   the behaviour before DEC-1167 (4) (a decided-behaviour revision) or a sign of a defect in the change:
   - `tests/unit/gitenv/test_hooks_lifted.py::test_a_lifted_event_in_the_template_only_is_no_finding[lifted0]` (line 37),
     `::test_any_other_event_in_one_source_only_is_still_a_finding_beside_the_lifted_ones[template]` (line 43),
     `::test_the_finding_form_is_unchanged` (line 69): their lifted entries run a generic `python3 hook.py`.
   - `tests/acceptance/W2-59/test_w2_59_hook_lines.py::test_the_source_holds_the_seven_governance_hook_lines` (line 80:
     8 entries, seven expected), `::test_the_line_s_program_imports_the_pin_s_package_not_the_project_s_src[postToolUse[1]]`
     (line 123) and `tests/acceptance/W2-59/test_w2_59_hook_lines_worker_env.py::test_with_a_worker_s_pythonpath_the_line_s_program_runs_the_pin_s_code[postToolUse[1]]`:
     `context_watch.py` imports nothing of `gov` (stdlib only), while the case's `IMPORTS_GOV` is keyed by event (line 56).
   Say in one line each what the revision would be. (A seventh red, `tests/unit/retrieval/test_w2_112_shared_reranker.py::test_the_running_service_writes_one_memory_line_per_request`,
   passed alone: load; not yours to judge.)

The lead's `gov accept W2-185` on 1180e4ec5: pass, 18 passed, 0 failed, 0 unmapped (S1 3, S2 6, S3 3, F1 6)
(`.gov-runtime/scratch/lead/log/accept-1180e4ec5.txt` in the tree).

Work in a **copy** of the tree in your `$TMPDIR` (`git -C /home/usain/gov-os-worktrees/W2-185 archive HEAD | tar -x -C
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
Then, for each of the six points: the verdict, the commands you ran and their result lines (each plant: green unplanted, red planted, the failing assertion).
Then each finding, with `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.
Then the fenced verdict block, one entry per KPI line of the ticket, ids S1, S2, S3, F1, in this exact form:
```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": []}, ...]}
```
Then: guard_refusals: none or a line each.
