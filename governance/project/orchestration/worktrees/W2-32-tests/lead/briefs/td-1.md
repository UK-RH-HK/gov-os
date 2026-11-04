# W2-32 (DAEO-0pyc): independent test designer, round 1 (D-4b, DEC-1055; launched by the CTO, no lead)

You are the independent test designer for W2-32, "Retrieval components and bounded improvements", in the Gov OS
repository. Your worktree is `/home/usain/gov-os-worktrees/W2-32-tests` (branch `w2/W2-32-tests`). You run in the
launch sandbox under `GOV_ROLE=independent-test-designer`, `GOV_TICKET=DAEO-0pyc`: the guard refuses you the
engineer's new code (in `~/gov-os-worktrees/W2-32` and anything its commits carry into your tree), DEC-1063.

**Step 0, the sandbox check, reported first in your return:** (a)
`python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0pyc','w').write('x')"` must fail; (b)
`echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file
or (b) failed, stop and return.

Read first, whole: `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/EMG-common.md`
(your common rules; where it names a TMPDIR, use the sandbox's own), `governance/project/orchestration/INTENT-DEC-1052.md`,
the ticket `.tickets/DAEO-0pyc.md` (its KPI lines; the claim note at its end), and the W2-32 row of §3 in
`governance/project/orchestration/packages/LIFT-1/D4B-MEMORY-STAGE.md`. Read the integrated code freely (DEC-963:
this tree is `w2/integrate` at 9c468dbd; use `gov retrieve` from here only). Never the hidden half (`~/gov-os-eval`),
held-out material or secrets.

**Your task this round:** acceptance tests from W2-32's KPI lines **S1 to S5, S9 and F1** (the lines that do not wait for
D-4b measure 1's gaps; S6 to S8 come in a later round, once the owner approves at most three gaps), in
`tests/acceptance/W2-32/`, with a README mapping each KPI line to its case(s). Each case must fail on today's integrated
code wherever the line asks for something not built yet (show it red), and pass only when the behaviour the line states
exists. Use stand-ins (a planted project, a stand-in embedder or reranker), never the shared servers or real models;
keep each case fast. S9 (the escalation below 85 % after two rounds) and F1 (an improvement that lowers a baseline
figure beyond its noise band is reverted) are judged on the record the CTO keeps (the measure records under
`~/gov-os-runs/D4B/`) and the ticket's evidence file: test what a test can (the record's form, the revert rule as code
if W2-32 builds one), and say in the README what is judged by the record instead.

Commit with `Task: DAEO-0pyc`, `Implements: DEC-1055`, `Role: independent-test-designer`, `Co-Authored-By: Claude Opus
5.5 <noreply@anthropic.com>`; write only `tests/acceptance/W2-32/**`. Runs: your own tests only, with
`PYTHONPATH=/home/usain/gov-os-worktrees/W2-32-tests/src`. When done, write `TESTS-READY` at
`.gov-runtime/scratch/lead/TESTS-READY` with the commit.

**Return:** the twelve fields as labelled lines (task, status, work_completed, files_changed, evidence, tests,
discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action); the sandbox check first.
