---
task: DAEO-03ub
decisions_applied: [DEC-1157, DEC-1180, DEC-1128, DEC-1133, DEC-136, DEC-968, DEC-1156, DEC-1010, DEC-1154]
---
STATE: narrow check a8n PASS (R4, R5, F3; 0 blocking, 6 rows); record committed 2376e2a33485 after merging w2/integrate 6ae3f8562cdd (0e5205dba); returned DONE | HEAD: 2376e2a33485 | NEXT: none (the queue lands 2376e2a33485) | WAITING ON: none
Workers: td-10 refused at launch (sonnet; promotion requires opus); td-10-2 16db6355-c339-435b-b7ba-74b7195f6355 done (e3e7badb255b); eng-7 7b7b090e-b078-44ba-9add-a30b5b4723d5 done (eca7a70176de); td-11 e4dcf49e-907d-4ff9-91cb-8d85add1d559 done (e4ed39ca725f); eng-8 2069394e-cb34-4091-a742-37e4e0dcda02 ended early (waited on a background run; nothing committed); eng-8r 22c393c8-d4ce-40a0-bafa-79094d18f99b done (b42e8628b835); a8 LAUNCH_REFUSED (round 3, DEC-1010); a8n e09466c3-7b39-4b10-b09d-ead3a7c4651d done (PASS, --owner-named DEC-1154)
Rounds: converged (two build iterations; the second from the lead's probe lead/r7/probe_failopen.py)
Decisions taken: the CTO's order; gov context --root W2-00-store --budget 20000 (main store lacks DEC-1180; ticket 18,203 tokens); workers on opus promoted (gov launch's promotion rule); td-10 P1 (a) (git show of a revision naming nothing pinned refused, the KPI text); iteration 2 for the probe's fail-opens and the same mechanism's older ones
Open packages: none (P-03ub-R4-1 answered (a): DEC-1154)
Paths: briefs lead/r7/td-10.md, eng-7.md, td-11.md, eng-8.md, eng-8r.md, a8.md; merges lead/r7/merge-*.txt; logs lead/log/r4-red.log, r4b-red.log, r4-accept.log, r4-scoped.log/.xml, verify/, r4-base-reds.log, r4-rerank-alone.log, eng-7.*, eng-8*.*, a8.*; td logs were in W2-42a-tests (worktree removed; branch w2/W2-42a-tests deleted, merged); TESTS-READY 4692b61ddac6
