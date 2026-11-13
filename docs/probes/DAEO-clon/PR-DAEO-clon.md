---
type: probe
task: DAEO-clon
reviewer_session: not known
implementer_session: not recorded
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 2ef060a65c7712c11556b82eb8931f9b7222e32f
---

# Probe record: W2-112 (DAEO-clon) One reranker serves every session, FULL review of the merged code (DEC-1010, DEC-1131)

## The lead's judgement

- **Who probed.** A fresh read-only reviewer launched from W2-20's lead worktree (log `~/gov-os-worktrees/W2-20/.gov-runtime/scratch/lead/log/W2-112-A3-probe.json`), FULL review of the merged code at `w2/integrate` `2ef060a65c77` (the brief named `7b5c3cb94fd9`; the reviewer found the judged paths and the three unit files unchanged between them). Recorded by the CTO (session b2f0511f, 2026-11-11), who did not re-run it.
- **READY, by code.** All ten KPI lines pass; no finding is in scope, ordinary work yes and fails open or loses work (DEC-1010, DEC-1131).
- **Rows.** FR-1 to FR-5 go to the row ledger (two ordinary no, three ordinary yes with consequence other); FR-5, the research document's §1 and §2 to match W2-145, is the follow-up most worth a small ticket.
- **Judgement: pass.**

## The reviewer's record (as returned)

Every one of the ten KPI lines passes at `2ef060a65c77`, and nothing blocks. The shared service starts once under its lock. It listens only on a 0600 socket in a 0700 folder under the user's home, holds every GPU slot, refuses to start below its GPU share and never runs on the CPU. It answers each caller on that caller's own connection, releases GPU memory after every answer, and ends after its idle time. Every way it can fail leaves the search unranked and named, inside fixed time bounds, with one FALLBACK line that `gov status` counts.

Five findings land as rows; none is a round:
- the fallback count misses a repeated question in one process (FR-1);
- a search arriving during the idle-end drain goes unranked (FR-2);
- a socket file removed by hand under a live service makes each search wait the start bound (FR-3);
- the service's single thread lets a stalled caller or a stalled model call hold the others up to their bounds (FR-4);
- the research document's design sections still describe the private fallback that W2-145 removed (FR-5).

```
task: DAEO-clon
status: DONE
work_completed: FULL read-only review of W2-112's merged code at w2/integrate 2ef060a65c77 against its 10 KPI lines; scoped acceptance and unit tests run through the heavy-job gate; 11 stand-in probes (3 in-process, 8 end-to-end with the real rerank_service.py over the suite's Unix-over-TCP stand-in)
files_changed: none
evidence: step 0 (a) refused (EROFS), (b) worked; no ollama/llama-server process; clone head 2ef060a65c77, scoped paths unchanged since 7b5c3cb94fd9; main tree clean; scratch peak 115M / 5205 inodes, removed (28K / 10 after)
tests: acceptance 27 passed, 24 failed, 8 deselected (with the opt-in set: 31 passed, 27 failed, 1 deselected); unit files 53 passed, 21 failed; every failure is the sandbox refusing socket(AF_UNIX) (EPERM), none a code failure; the CTO's 59/59 outside the sandbox stands for them
discoveries: the research document's sections 1 and 2 predate W2-145 (FR-5); the 48-question half sits in S3's text and waits on W2-61h (in progress)
risks: none that blocks; the live-service cases were judged by code, stand-in probes and the CTO's 59/59
lessons: this sandbox refuses AF_UNIX and ends a Bash call's processes with it; probe the service over the TCP stand-in, each scenario in one call
proposed_decisions: none
unresolved: S3's 48 questions after W2-61h (known open point)
recommended_next_action: commit this record and close W2-112; FR-1 to FR-5 to the row ledger, FR-5 as a small document follow-up
```

task: DAEO-clon
decisions: DEC-979, DEC-374, DEC-397, DEC-1032, DEC-1033, DEC-1034, DEC-1036, DEC-1046, DEC-1048, DEC-1068, DEC-1090, DEC-1010, DEC-1131, DEC-801, DEC-808
probed_commit: 2ef060a65c77

**Scope.**
- The ticket's allowed paths at the head of `w2/integrate` (`2ef060a65c77`; no change since `7b5c3cb94fd9` in them):
  - `src/gov/retrieval/rerank.py`, `rerank_worker.py`, `rerank_service.py` and `retrieve.py` (its rerank parts);
  - `src/gov/status/command.py`;
  - the three unit files and `tests/unit/retrieval/test_w2_112_shared_reranker.py`;
  - `docs/research/W2-112-shared-reranker.md`.
- Judged only on the ticket's ten KPI lines. W2-145 (`DAEO-2tfd`) is applied as context with the CTO's reading of S4, S6 and S7: a missing private fallback is not a failure. I agree with that reading.

**Method.**
- Read the ticket whole, the code in scope, the acceptance README and every case name, and DEC-1034, DEC-1036, DEC-1046 and DEC-1048.
- Tests through the heavy-job gate with `-m "not local_only" -k "not real and not green_here and not time_limit"`:
  - acceptance: 27 passed, 24 failed, 8 deselected; with `GOV_TESTS_OPTIN=lifted,breadth`, 31 passed, 27 failed, 1 deselected;
  - the four unit files (with the opt-in set): 53 passed, 21 failed.
- Every failure is the launch sandbox refusing `socket(AF_UNIX)` with EPERM, each one a search unranked with `PermissionError: [Errno 1]` or a stand-in service that could not be made. These cases rest on the CTO's 59/59 run outside the sandbox.
- 11 probes of my own:
  - In-process: P1 (the fallback count for repeated questions), P2 (a socket removed under a live service) and P6 (a search during the idle drain).
  - End-to-end: the real `rerank_service.py` started by `rerank._start` through a wrapper interpreter, with a fake torch and CrossEncoder whose scores are deterministic hashes, and the acceptance suite's Unix-over-TCP stand-in. These were P3a (eight searches start together), P3b (20 concurrent searches checked against a direct reference), P3c (idle end and restart), P4 (slots held while the service runs), P4b (kill -9 mid-request with five searches in flight, then recovery), P5 (a caller that connects and sends nothing), P5b (the time limit), P5c (below its GPU share) and P5d (both slots held by another process).

**Probed and found sound.**
1. **S1, F2: one service, started under the lock.**
   - Code: `rerank.py:111-131`, `_start` (flock `LOCK_EX|LOCK_NB` on `rerank.lock`, the fd handed over with `pass_fds` and held for the service's life, `rerank_service.py:186`); `rerank.py:134-170`, `_connect` (a waiter never starts a second service).
   - P3a: eight searches started together gave one model load, one service process, eight scores and eight releases.
   - The same pinned `MODEL`/`REVISION`, `-I`, the reranker-venv interpreter and `HF_HUB_OFFLINE=1` (`rerank.py:29-32, 125-129`).
2. **S1, F2: a socket only the user can open.**
   - Code: the bind under `umask 0177` (`rerank_service.py:199-204`); the folder set to 0700 by every caller (`rerank.py:139-140`); AF_UNIX only, no AF_INET anywhere in the service.
   - P3a: socket 600, lock 600, folder 700.
   - A second service from another HOME would still meet the GPU slots the first one holds and end named (P5d's path).
3. **S1: the idle end.**
   - Code: `rerank_service.py:215-227` (removes the socket, drains, ends).
   - P3c: an `END pid … idle 3 s` line, the socket gone, the slots freed, and the next search started a fresh service.
4. **S2, F1: own scores, arrival order, cap, time limit.**
   - One connection per request, one request at a time in kernel accept order; the answer is written on the caller's own connection (`rerank_service.py:168-182`).
   - P3b: 20 concurrent searches answered by one process, 20 of 20 matching a direct reference's order and scores; p50 2.05 s, max 3.04 s.
   - The cap: the client sends at most 64 texts and `MAX_REQUEST_CHARS` (`rerank.py:44-50, 258-274`); the service refuses more than 512 and names the count (`rerank_service.py:138-140`).
   - The time limit: `GOV_RERANK_TIMEOUT_S` (`rerank.py:210`). P5b: a 4 s request given up at 1.5 s, unranked and named.
5. **S3, F3: the same answers.**
   - The service calls the worker's own `scores` (`rerank_worker.py:65-66`); `rerank()` puts each score back by index and sorts stably, so ties keep the given order (`rerank.py:301-318`).
   - §4 of the research document: 20 of 20 questions in identical order, largest difference 0.
   - The 48-question half: see the closing note.
6. **S4, F1: down means unranked and named, never failed or hung.**
   - Every exception in `_ask` is caught in `score` (`rerank.py:243-250`), and `rerank()` catches the rest (`rerank.py:314-317`).
   - P4b: kill -9 mid-request; all five in-flight searches came back in 2.5 s, unranked, each named (`ConnectionResetError` or "closed the connection without an answer"), five FALLBACK lines. The next search replaced the stale socket with one new service.
   - The bundle carries `rerank: {by: unavailable, reason}` and `merge.reranked` false (`retrieve.py:574-580, 731-735`).
   - `gov status` counts FALLBACK and REFUSED lines (`rerank.py:87-94`, `command.py:172-176, 197`).
   - The bounds: 2 s to connect (`CONNECT_S`), 60 s to start (`START_S`), 30 s per request; these follow DEC-1034 T3's reading of "about 2 s".
7. **S6: the GPU only, within budget.**
   - Code: `take_slot` before anything else (`rerank_service.py:189`), then `gpu_short`, the 3.5 GiB share plus 2 GiB headroom (`rerank_service.py:117-125`), then `hold_every_slot` (`rerank_service.py:90-108, 196`).
   - P4: both slots held while the service ran.
   - P5c: 1 GiB free gave a REFUSED line ("1.0 GiB free, under the 5.5 GiB needed"), no model load, and the search unranked and named.
   - P5d: both slots held elsewhere; the service waited 3 s and ended with exit 75 ("no GPU slot freed within its wait"), named.
   - No CPU path exists: `allow_cpu` is ignored and a hidden GPU gives exit 76 (`rerank_worker.py:26-36`).
   - §4 measures the embedder plus the service under 20 searches: peak 6,429 MiB.
8. **S6 and the DEC-1068 note: the memory release.**
   - The release runs after the answer is sent, on failed requests too, and neither a failed release nor an unwritable log ends the service (`rerank_service.py:146-182`).
   - P3a, P3b and P4b: one release per request, each after its score.
9. **S7: the stopgap stays, and nothing runs on the CPU.**
   - §5 of the research document (lines 175-209) records that the module and its `.pth` stay as the machine-wide guard, are not retired by an ACT now, and are retired only when old code fails closed by construction, in a later ticket. It also says never to remove the slot lock files.
   - `rerank_worker.py` run as a program ends at once with exit 69 (`rerank_worker.py:73-76`).
   - The four `test_w2_112_retirement_act.py` cases passed here.
10. **S5: the measurements.**
    - §4 gives memory with 10 concurrent searches before and after (one private reranker about 1.7 GiB RSS and 3.3 GB of GPU each, up to 10 at once, against CAPACITY-1's 9 at once and 9.4 GiB; after, one process of 1.69 GiB RSS and a GPU peak of 6,428 MiB), and the searches' times (after: p50 1.09 s, p95 2.13 s; before: a 4.18 s load plus 0.20 s per question).
    - It states plainly "After W2-61h: the 48 questions, not yet measured".
    - The measurement is from `775c58eda031`. The later memory release can only lower the figures, and the 30-text requests measured still go in one request under today's 64-text cap.

**Findings**

- **FR-1 (S4): the fallback count misses some unranked searches.**
  - Within `RECALL_S` (10 s), a second, separate search with the same question in the same process gets the remembered reason and goes unranked without writing a FALLBACK line (`rerank.py:238-242`, from W2-145's F1 fix `1be3e47debb4`).
  - P1: three searches, q1, q1 and q2, with the service down. All three were unranked; the FALLBACK count after each was 1, 1, 2.
  - Likewise, a HOME with no reranker environment gives `unavailable` with no line (`rerank.py:233-235`), which the research document gives as by design.
  - `scope: in`
  - Ordinary work: yes, because a long-lived process that runs the same question twice within 10 s while the service is down, or a session whose HOME holds no reranker environment, is ordinary (narrowly: the CLI runs one search per process).
  - Consequence: other (`gov status` counts low; each search's bundle still names its outcome, and nothing is ranked wrongly or lost).
  - Reversed by: the KPI read as one line per search for the service's failures, which `RECALL_S` keeps within one search, or evidence that no caller runs repeated questions in one process.

- **FR-2 (S1): a search that arrives during the idle-end drain goes unranked.**
  - After the idle timeout, the service removes its socket and still holds the lock while it drains (`rerank_service.py:219-227`).
  - A search arriving then finds no socket. Its `_start` finds the lock held, waits, and once the lock frees, raises "the service this search waited for ended before it listened (rerank.log)" (`rerank.py:121-122`), instead of starting a fresh service.
  - P6: unranked after 0.30 s, with that reason. The reason reads like a refusal to start.
  - `scope: in`
  - Ordinary work: yes, because a search can land in the drain window (about 0.2 s after 15 minutes idle), rarely.
  - Consequence: other (one search unranked, named and counted; the next search starts the service).
  - Reversed by: evidence that the window cannot be hit, or the KPI read as satisfied by a named fallback in that window.

- **FR-3 (F1): a socket file removed by hand under a live service.**
  - Each later search finds no socket and finds the lock held. It waits `START_S` (60 s) and goes unranked, until the orphaned service's idle end (900 s).
  - That idle end then raises `FileNotFoundError` at the unguarded `os.unlink(path)` (`rerank_service.py:220`) and exits without its END line.
  - If the whole `~/.cache/gov-os` folder is removed instead, a second service starts, waits 20 s for slots the first one holds, and ends with exit 75, named.
  - P2: the next search took 3.0 s (START_S set to 3) and was unranked with "did not listen within 3 s"; the service exited 1 with the traceback at line 220.
  - `scope: in`
  - Ordinary work: no, because nothing in the product, its documents or ordinary work removes the live service's socket or its folder by hand.
  - Consequence: other (bounded waits, each search unranked, named and counted; no CPU use, no second model on the GPU).
  - Reversed by: a documented step or tool that clears `~/.cache/gov-os` while the service runs.

- **FR-4 (S2): one thread, so one stalled peer holds the rest up to their bounds.**
  - A caller that connects and sends nothing holds every queued search for `READ_S` (10 s) (`rerank_service.py:174-175`). P5: a concurrent search waited 9.55 s and was still answered by the service.
  - A model call that hangs holds each search to its 30 s request limit.
  - `CONNECT_S` cannot measure "being accepted" on a Unix socket, since connect returns once the connection is queued. The docstring (`rerank.py:36`) and research document line 39 say "accepted".
  - `scope: in`
  - Ordinary work: no, because a caller that stays alive but stalls between connect and send, or a model call that hangs, needs an unusual fault (a dead caller's socket closes and is answered at once).
  - Consequence: other (delays inside the stated bounds; no search fails or hangs past them).
  - Reversed by: an ordinary path that leaves a live caller connected without sending.

- **FR-5 (S5): the research document's §1 and §2 predate W2-145 and W2-137.** It still describes:
  - a private reranker as the fallback (lines 65-66, 88-100, 122-124);
  - `GOV_RERANK_ALLOW_CPU=1` allowing the CPU, and exit 78 (lines 53, 83-84, 120, 125);
  - "at most one private reranker runs beside it" (line 51), where the service now holds every slot;
  - a search past 512 texts reranking through the private fallback (lines 37-38), where the client now splits requests at 64;
  - `by: private` (line 103), and a FALLBACK line ending `private | unavailable` (line 98), where the code writes `unranked`;
  - and it does not describe the DEC-1068 memory release.

  The code matches none of this. It has no private reranker and no CPU path (`rerank_worker.py:26-36, 73-76`; `rerank.py:8-14`). The document was last changed 2026-11-02, while the code changed through 2026-11-09. §4 and §5 are accurate.
  - `scope: in`
  - Ordinary work: yes, because operators and agents read this design record and could act on the private fallback or the CPU switch it describes.
  - Consequence: other (the code fails closed whatever the text says; nothing loads on the CPU and no private reranker runs).
  - Reversed by: the text brought up to date with W2-145, or a note that §1 and §2 describe the design as first built.

- **Rows already carried, met again:** `rerank.log` is never trimmed (it now gains a MEMORY line per request) and `gov status` reads it whole. The multi-line error and sticky CUDA error rows were seen only in the code. None shows a worse consequence.

- **Note on the 48-question half:** it is in S3's text ("after W2-61h, the 48"), not S5's. W2-61h (`DAEO-h2k3`) is still in progress and the document says the 48 are not yet measured. This is a known open point, not a finding.

**Classification:** 0 yes / fails open or loses work; 3 yes / other (FR-1, FR-2, FR-5); 2 rows marked no (FR-3, FR-4).

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "FR-2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S2", "verdict": "pass", "findings": [{"id": "FR-4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": [{"id": "FR-1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S5", "verdict": "pass", "findings": [{"id": "FR-5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S6", "verdict": "pass", "findings": []}, {"kpi": "S7", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": [{"id": "FR-3", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "F2", "verdict": "pass", "findings": []}, {"kpi": "F3", "verdict": "pass", "findings": []}]}
```
