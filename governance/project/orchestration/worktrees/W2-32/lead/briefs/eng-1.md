# W2-32 (DAEO-0pyc): engineer, round 1 (D-4b, DEC-1055; launched by the CTO, no lead)

You are the engineer for W2-32, "Retrieval components and bounded improvements", in the Gov OS repository. Your
worktree is `/home/usain/gov-os-worktrees/W2-32` (branch `w2/W2-32`). You run in the launch sandbox under
`GOV_ROLE=engineer`, `GOV_TICKET=DAEO-0pyc`: the guard refuses you W2-32's acceptance tests wherever they sit
(DEC-1056); you build to the spec and its KPIs, never to the tests. When the test designer's tests are ready, the CTO
merges them into your tree and you run them with `gov accept W2-32` (pass or fail only).

**Step 0, the sandbox check, reported first in your return:** (a)
`python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0pyc','w').write('x')"` must fail; (b)
`echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file
or (b) failed, stop and return.

Read first, whole: `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/EMG-common.md`
(your common rules; where it names a TMPDIR, use the sandbox's own), `governance/project/orchestration/INTENT-DEC-1052.md`,
the ticket `.tickets/DAEO-0pyc.md` (its KPI lines, `allowed_paths`, the claim note at its end), and the W2-32 row of §3 in
`governance/project/orchestration/packages/LIFT-1/D4B-MEMORY-STAGE.md`. Never the hidden half (`~/gov-os-eval`),
held-out material or secrets.

**Your task this round:** build KPI lines **S1 to S5** (S9 and F1 are the CTO's records and rules; S6 to S8, the gap
rounds, come once the owner approves at most three gaps from D-4b measure 1): S1 a change of the embedder pin in
configuration triggers a full re-embed; S2 an unpinned or mismatched model fails closed with a named error; S3 a
retrieval miss is recorded as a memory-quality event with its root cause, its repair and a held-out regression case;
S4 a reranker that dies after loading is reported, not raised; S5 the fusion limit is honoured. Survey first what
exists (`MODEL` is hard-coded at `src/gov/retrieval/semantic.py:49`; there is no `src/gov/config/models*`; S4 and S5
may be partly met: say what is and is not, with evidence). Keep W2-13's ranked lexical route, W2-92's routes,
W2-112's shared reranker and W2-126's vector cache exactly as they are. **S5 and the bundle budget:** W1-21's approved
spec DEC-419 DP-3 says the budget bounds parent expansion only and never drops a child hit; whether a limit should bound
the whole bundle (DEC-860) is S5's question: survey the fusion limit as built, and if honouring S5 would change DP-3's
behaviour, stop and return PACKAGES with the options (do not change DP-3 on your own).

Your own unit tests (test-driven, under `tests/unit/retrieval/**` within your allowed paths); write
`docs/changes/W2-32-evidence.md` with one row per KPI line (how verified, command, result, commit). Commit with
`Task: DAEO-0pyc`, `Implements: DEC-1055`, `Role: engineer`, `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
Runs: your unit tests, plus the scoped set from
`PYTHONPATH=/home/usain/gov-os-worktrees/W2-32/src python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/select_tests.py /home/usain/gov-os-worktrees/W2-32 W2-32 DAEO-0pyc`
(its `pytest_options`), through `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`
if the sandbox allows it, else name what it refused. Inside the sandbox `gov` uses a private CPU embedder: no
real-embedder figure from you counts (the CTO measures).

**Return:** the twelve fields as labelled lines (task, status, work_completed, files_changed, evidence, tests,
discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action); the sandbox check first.
