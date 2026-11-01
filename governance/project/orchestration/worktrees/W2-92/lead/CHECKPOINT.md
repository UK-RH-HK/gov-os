# W2-92 (DAEO-n0wb) lead checkpoint

## State (2026-11-01, run 1)
- Base / head: 7ca16b19df3f on w2/W2-92 (no ticket commits yet).
- Tests worktree: /home/usain/gov-os-worktrees/W2-92-tests on w2/W2-92-tests (from 7ca16b19df3f).
- Store rebuild 0 (this worktree, this code) running in background: log/rebuild-0.json, exit file log/rebuild-0.exit.
- Test designer td-1 launched (old form, not sandboxed: suites may need the code-graph daemon folder), log/td-1.json. Tripwire snapshot tripwire-before-1.json.
- Engineer eng-1: brief written (briefs/eng-1.md), launch waits for rebuild 0 (old form, same reason). Tripwire snapshot 2 to take before it.

## Update 13:10
- rebuild-0 exited 143 while waiting on the lock (killed by an unknown signal, empty log); restarted as rebuild-1 (log/rebuild-1.*), queued behind W2-13's rebuild. My kill of the queued base waiter was refused (approval prompt): base rebuild waiter (pid 1055389, /tmp/gov-os-lead-W2-92/log/rebuild-base.*) stays queued.
- td-1 DONE: tests commit 5679104a81d9 (trailers ok), 30 cases. Packages P-1..P-6 (P-1 missing record store: KPI 3 vs brief scope "retrieve.py route list only" -> f3 needs a change at the record-graph read / authority order).
- Merged into w2/W2-92 as 5b64b7d17a3a (--no-ff, Task/Role/Implements trailers). TESTS-READY written.
- Red check here (base code + tests, gov.__file__ in this worktree): 17 failed, 13 passed, as the README says.
- Tripwire 1: only W2-92-tests head and acceptance folder W2-92 from td-1; all other changes are other sessions' trees.
- Clones: /home/usain/gov-os-runs/W2-92/base (7ca16b19df3f), /measure (c38a5b49bc86). Launchers /tmp/gov-os-lead-W2-92/bin/gov-base, gov-head.
- Next: rebuild-1 done -> tripwire snapshot 2 -> launch eng-1.

## Update 13:45
- rebuild-0's 143: the W2-13 lead killed it by mistake while it waited on the lock (their message; nothing built).
- Base clone rebuild (base code): exit 0, 12:39-13:32 incl. lock wait, digest 632ae8729926.
- Worktree rebuild-1: exit 0, digest 93dc756b3485 (HEAD 5b64b7d17a3a).
- eng-1 launched ~13:45 (old form), tripwire-before-2.json, log/eng-1.json.
- Control measure running: /tmp/gov-os-lead-W2-92/bin/measure-base.sh -> /home/usain/gov-os-runs/W2-92/records, logs /tmp/gov-os-lead-W2-92/log/measure-base.*
- Package to return: P-1 (missing record store vs scope), f3 blocked on it.

## Update 14:35
- eng-1 returned (twelve fields ok): commit 46f40ded18a8 (trailers ok), gov accept 21/30. Its packages: P1 missing index for plain words, P2 STORE_MISSING (= TD's P-1), P3 noise of plain words.
- Control measure (base 7ca16b19df3f, base code): hit@5 11/20, full 11/20, in bundle 14/20, 13:47-14:00; record /home/usain/gov-os-runs/W2-92/records/measure-memory-retrieval-visible-20261101T140024036524Z.json, log /tmp/gov-os-lead-W2-92/log/measure-base.json.
- Lead's own acceptance run at 46f40ded: 9 failed. Diagnosis: r1[title] engineer defect (store titles only for register entries); c2/c3/c4 the qn_pattern follow-up search flagged by the tests' whole-graph proxy (names none of the question's symbols); c5[none] plain words searched; f1 x3 TEST DEFECT: asserts top.py in the lexical evidence for 'w92_leaf', but top.py never contains the word (base code gives leaf.py + middle.py x3 too; probe /tmp/gov-os-lead-W2-92/bin/probe_f1.py); f3 scope package.
- eng-2 (fresh repair engineer, brief eng-2.md) with the failure messages only.

## Update 14:40
- eng-2 returned (twelve fields ok; did not use gov retrieve): fedb871187f7 (trailers ok). Fixed record titles; restricted code route to code-shaped words (passes c5[none] but drops "Who calls rrf?" -> KPI 2 regression). Package P-W2-92-c2 (qn lookup counted whole-graph). Lead acceptance at fedb871187f7: 23 passed, 7 failed (c2,c3,c4,f1x3,f3).
- eng-3 (batch 3, fresh): restore plain-name symbols (KPI 2), keep c5[none], try targeted query_graph for spans (engineer's own option b), measure on this repo.

## Update 14:50
- eng-3 returned (twelve fields ok; gov retrieve not used): fb0c8c430171 (trailers ok) — the final code commit. Plain names defined by def/class in .py take the code route; targeted query_graph (CALLS into/out of one qn, max_rows 50, paged) gives spans. Real case: rrf 8.2 s, indexable 8.6 s. gov accept 26/4. Policy 2(c) incident self-reported: a probe regex-scan touched tests/acceptance/W2-92 paths (learned only that a def harbour exists in a test file).
- Lead acceptance at fb0c8c430171: 26 passed, 4 failed = f1 x3 (test defect, P-W2-92-2) + f3 (scope, P-W2-92-1). Converged otherwise.
- Head clone /home/usain/gov-os-runs/W2-92/head at fb0c8c430171, rebuild-head.sh running (lock queue), then measure-head.sh, then eng-4-record brief (written) -> record commit -> worktree rebuild -> scoped verification (select preview: scoped, core_changed retrieve.py, unplaced none, 37 targets).
- Packages draft: packages-draft.md.

## Decided
- Both workers in the old launch form with the tripwire (code graph needs /tmp/gov-cbm-<uid> writable).
- Budget shares: td 4 GB / 200k, eng 6 GB / 300k, lead the rest (measure clones).

## Next
1. Rebuild 0 done -> snapshot 2 -> launch eng-1.
2. td-1 returns -> twelve fields, tripwire, trailers -> merge w2/W2-92-tests (--no-ff, message file, Task/Role) when no worker runs here -> TESTS-READY -> red check on a scratch clone at 7ca16b19df3f with tests merged.
3. eng resume: gov accept once.
4. Re-measure (base, head, measure clones under /home/usain/gov-os-runs/W2-92/), record by a fresh engineer batch.
5. Scoped verification; return.

## Loop count: held by lead.

## Brief gaps (running)
- none yet

## Guard refusals (running)
- none yet
