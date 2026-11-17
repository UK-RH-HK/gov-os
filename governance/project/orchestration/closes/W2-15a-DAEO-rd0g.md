# W2-15a (DAEO-rd0g) closed: merged and closed in one step by the merge queue (DEC-989)

- Commit tested (the lead's final, verified result): f8404efe8942; merge 64dc878349b1; w2/integrate b183a850da7f -> 64dc878349b1 (fast-forward to the tested merge); profile FULL
- Queue record: /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/merge-queue/records/64dc878349b1.json; log /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/merge-queue/log/20261116-054547-536993
- Batch: W2-15a
- Run: skipped: the merged code is identical to f8404efe8942e0a278fbc26e5b864584d75b376c, W2-15a's approved commit, which its lead tested; governance paths left out of the comparison: .tickets/DAEO-6oj6.md, .tickets/DAEO-kfn1.md, .tickets/DAEO-l78m.md, governance/project/orchestration/packages/DECIDED-NOT-DONE.md (patterns: governance/project/briefs/**, governance/project/prompts/**, governance/project/orchestration/**, .gov-runtime/**, .tickets/**.md, docs/checkpoints/**.md, docs/close/**.md, docs/close/nightly/*.json, docs/probes/**.md, docs/DECISION_REGISTER.md, docs/plan/**.md, docs/plan/wave-1-exit/evidence/**.txt, docs/plan/wave-1-exit/evidence/**.json, governance/project/orchestration/**.md, governance/project/orchestration/packages/*.patch, governance/project/orchestration/packages/*.diff, governance/project/orchestration/packages/ACT-MSET-3/checker-settings.json, governance/project/orchestration/packages/ACT-MSET-3/writer-settings.json, governance/project/orchestration/packages/ACT-WSL-INTEROP-1/wsl-interop-binfmt.service, governance/project/orchestration/packages/ADR-0002-REFRESH/ADR-0002-architecture-and-stack.draft)
- Selected: 
- Reds caused by the change: none (the queue advances only then); flaky candidates: none
- Traced against: n/a (the head without the batch, once each way, the same failure; 3 rounds for the load-sensitive list's cases (Q-1, DEC-1050))
- Red on the head without the batch too, the same failure, not this change's (investigated by the CTO at once, DEC-968): none
- Acceptance tests' authors (G-1, DEC-1050): no commit changes tests/acceptance/
- Core changed (scoped, not full, DEC-968): none; unplaced: none
- Review: docs/probes/DAEO-rd0g/PR-DAEO-rd0g-close-narrow.md
- gitleaks: off by configuration (DEC-1045): the change was not scanned
- Queue run: 2026-11-16 05:45:47 to 2026-11-16 05:45:48
- Closed: 2026-11-16 05:45:48 GMT, by the orchestrator under DEC-953 items 1 and 5, DEC-989

## Final close (2026-11-16 16:52:33 GMT, by the CTO; DEC-1186 (3) Q2 (a), DEC-1206 (2))

- Kept open after the queue's close above (05:45:48) for P-W2-15A-CLOSE steps (3) and (4): the visible run and the owner's operator's walled run at one head holding 7041f086c.
- Visible half at 7041f086c2d4 (the CTO's run, ~/gov-os-runs/W2-00/w2-15a-close/): rerank 36 of 40 (90.0 %), fused 36, lexical 27, semantic 25; full evidence 36, 36, 31, 31 of 40.
- Hidden half at 7041f086c2d4 (JOB-20261116-02, 15:13:49 to 16:34:28 GMT, counts only): rerank 29 of 39 (74.4 %), fused 27 (69.2 %), lexical 24 (61.5 %), semantic 23 (59.0 %); full evidence 26, 26, 25, 24 of 39; 2 gold blocks unresolved in every mode. The pass line (rerank, 34 of 39): MISS.
- Closed on this measured record under the owner's Q2 (a) (DEC-1186 (3); confirmed 2026-11-16 16:45, DEC-1206 (2)). The record: docs/research/EXP-003/w2-15a-baseline.md section 11. S1's memory clause: "recorded against 34 of 39".
- Gaps to W2-15b (DAEO-swdu): (1) the hidden half's drop at the same commit, stale or unresolved gold first (DEC-1206 (3)'s operator job); (2) gold ranked just past 5; (3) full evidence in the stacked context.
- Status: closed.
