# W2-92 memory measure: W2-61's 20-question measure after the record and code routes, visible half

- **Ticket:** DAEO-n0wb (W2-92), profile STANDARD. Written by the engineer from the outputs of the measures its lead ran: run 1 at `fb0c8c430171`, then run 2 at `d72c96fc029c` after DEC-1006. **The ticket's figures are run 2's;** run 1's stay as history.
- **Date:** 2026-11-01.
- **Sources:** DEC-957 (memory's target of 95 %; the record and code routes), DEC-1006 (P-1 the record graph's absence fails only the record and closure routes; P-3 the cue gate; P-4 one code-graph tool session per process), DEC-833 (both figures, always together; the kept control), DEC-860 (retrieval in batches, ranked and stacked), DEC-859 (a code question takes the code-graph tool's own traversal), DEC-941 item 1 (the measure re-run beside W2-61's baseline), CAP-10 (the floor of 85 for hit@5); the ticket's KPI 5 and its failure line. The figures beside these are `docs/research/W2-61-baseline.md` (§5 and §8) and W2-86's record (`docs/research/W2-86-memory-measure.md` on `w2/integrate`).

This record holds scores: ids, counts, ranks, digests and pass or fail. It quotes no gold answer and no text of a retrieved item. Of the questions' text it names only the ids, titles and words that the two new routes' rules take (§6). The hidden half of the set was neither read nor run.

## 1. What was measured, and where

- **The three clones,** each `git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS <path>`, left detached:

  | Clone | Commit | What it is |
  |---|---|---|
  | `/home/usain/gov-os-runs/W2-92/base` | `7ca16b19df3f` | the ticket's base; the tree measured as the control. Unchanged since run 1: its stores and its record are reused (DEC-833's kept control) |
  | `/home/usain/gov-os-runs/W2-92/head` | run 2: `d72c96fc029c` (`rebuild-head2.commit`); run 1: `fb0c8c430171` (`rebuild-head.commit`) | the ticket's final code commit at each run; the tree measured as the head |
  | `/home/usain/gov-os-runs/W2-92/measure` | run 2: `160736409bc4`; run 1: `c38a5b49bc86` | `w2/integrate`'s head when fetched: the measure's code and the visible set only. `git diff --stat c38a5b49bc86 160736409bc4 -- src/gov/retrieval/measure.py fixtures/evaluation/memory-retrieval/visible` is empty: the measure and the set are the same in both runs |

- **What differs, base to head:** `git diff --stat 7ca16b19df3f d72c96fc029c` gives 13 files: the code `src/gov/retrieval/code_route.py` (new, 175 lines), `src/gov/retrieval/graph_route.py` (new, 93 lines) and `src/gov/retrieval/retrieve.py` (47 lines), the ticket's tests, its checkpoint and this record (run 1's form). The base is an ancestor of the head.
- **What differs, run 1's head to run 2's:** `git diff --stat 264a9965ca4e d72c96fc029c -- src` gives three files, 86 lines in and 25 out, in two commits (`39e8c599`, `d72c96fc`):
  - `code_route.py`: the cue gate (P-3). A plain word joins the code route only when the question has a code cue (`_CUE`, in any case: call, calls, called, calling, caller(s), callee(s), define(s), defined, definition(s), function(s), method(s), class(es), or backticks or a call anywhere); a word shaped as code (`_CODE_SHAPED`: in backticks, called, or with an underscore or a capital inside it) still joins without one; a cue word is never itself taken. One session of the code-graph tool per process and code index (`_session`, P-4), ended at exit, started anew when the index's file changes or a question fails.
  - `graph_route.py`: a per-process cache of the records' parsed front matter (`_parsed`, keyed by file, size and time), and a plain substring test before the title's word-bounded match. The route's rule is unchanged.
  - `retrieve.py`: a store whose record graph is missing or unreadable gives the closure facet unavailable and no record route; the other routes still answer (P-1). An absent store is still refused.
- **The retrievers: each clone's own code.** The change is code, so the code under test builds the stores and answers the questions. Each retriever is the pinned launcher's body under a first line that sets `PYTHONPATH` to that clone's `src/`:
  - **control:** `/tmp/gov-os-lead-W2-92/bin/gov-base`, first line `#!/usr/bin/env -S PYTHONPATH=/home/usain/gov-os-runs/W2-92/base/src /usr/bin/python3`. The record's `retriever.version`: `gov 0.1.0 (commit 7ca16b19df3f)`; `retriever.gov_file`: `/home/usain/gov-os-runs/W2-92/base/src/gov/__init__.py`.
  - **head:** `/tmp/gov-os-lead-W2-92/bin/gov-head`, first line `#!/usr/bin/env -S PYTHONPATH=/home/usain/gov-os-runs/W2-92/head/src /usr/bin/python3`. Run 2's record's `retriever.version`: `gov 0.1.0 (commit d72c96fc029c)` (run 1's: `fb0c8c430171`; the record holds the full hash, given here as 12 digits); `retriever.gov_file`: `/home/usain/gov-os-runs/W2-92/head/src/gov/__init__.py`.
- **The measure:** `src/gov/retrieval/measure.py` from the measure clone (last changed at `289b9314a763`), run with `PYTHONPATH` set to that clone's `src/` and `GOV_TICKET` removed; the retrieving process is the `--gov` given.
- **The set:** `memory-retrieval`, the visible half only (`--part visible`): Q01 to Q20, read from the measure clone (`--sets-root`); the visible set last changed at `80c96c44bdcf`.
- **The budgets:** the measure's defaults, `--batch-size 10`, `--bundle-budget 6000`, `--stack-budget 24000` (each record's `budget`), as in W2-61's baseline and W2-86's record.

## 2. The stores' fingerprint

Each clone's stores were built in that clone by that clone's own code, with embeddings, as `env -u GOV_TICKET TMPDIR=/tmp/gov-os-lead-W2-92 flock /tmp/gov-os-rebuild.lock <gov-base|gov-head> rebuild --json`, after the disk gate (`rebuild-base.sh`, `rebuild-head.sh`, `rebuild-head2.sh`). Times UTC, 2026-11-01. "Start" is when the command began to wait on the shared lock; the lock's own times and the length are the JSON's.

| | base (control) | head, run 1 (`fb0c8c430171`) | **head, run 2 (`d72c96fc029c`)** |
|---|---|---|---|
| Disk gate | not logged | not logged | open: 849 GiB free, 64,374,650 inodes free (`rebuild-head2.disk`) |
| Start (waiting on the lock) | 12:39:37 | 15:08:36 | 20:33:30 |
| Lock taken and released (`result.lock`) | 13:14:37 to 13:30:44 | 15:12:34 to 15:29:13 | 20:33:30 to 20:34:52 (waited 0.0 s) |
| End | 13:32:29 | 15:30:44 | 20:34:52 |
| Length (`timing.total_s`) | 967.4 s (semantic 930.5, lexical 10.5, code index 18.1) | 999.1 s (semantic 963.1, lexical 9.5, code index 20.0) | **81.5 s** (semantic 44.2, lexical 2.0, code index 28.0; record 4.4, secrets 7.7, compaction 2.8) |
| Exit code; stderr | 0 (`ok: true`); empty | 0 (`ok: true`); empty | 0 (`ok: true`, `slow: false`, no watchdog fault); empty |
| Stores (`lexical`, `semantic`, `codeintel`) | each `recreated` | each `recreated` | each `recreated` |
| Files compacted | `store.db`, `codeintel/home/_config.db`, `codeintel/home/code.db` | the same three | the same three and `query-vector-cache.db` |
| Secrets scan (`secrets_counts`) | content 12 scanned, 5,602 remembered; paths 0 and 2,801 | content 16 scanned, 5,618 remembered; paths 3 and 2,808 | content 13 scanned, 2,814 remembered; paths 1 and 2,812 |

Run 2's rebuild took 81.5 s against run 1's 999.1 s, nearly all of it in the semantic step (44.2 s against 963.1 s), and its secrets scan remembered about half as many contents. The rebuild's JSON does not say why; it is not explained here.

**The digest each rebuild records** (`result.digest`; `result.store.digest` is the same value, with no invalid entries):

- base (control): `632ae8729926f639a07f2a9e11073710d61341680cb4aac4dec7766449cc24fc`
- head, run 1: `a97f01cfdd9e1d43298ded415dfe41187a7ba4335d5de28cad178c2551ce1a3d`
- **head, run 2: `5fbf5947dd75eb0eb81312af4831ede296311eafbaf781a450c2e3fe62f2b464`**

**The sha256 of each store file** (read with `sha256sum`; no store was opened for writing). The base's were read again after run 2 and are the same as after run 1. Run 1's head files were replaced by run 2's rebuild; their hashes are as run 1 read them.

| Store file | base (control) | head, run 1 | **head, run 2** (read 20:53, after run 2's measure) |
|---|---|---|---|
| `.gov-runtime/store.db` | `aacb41d66c5f43881563ca452427ec2facb4ed63458c061bc80037538b7975a0` | `f8f591b9285a1959198f75ba4d1a466a112d2f28b4418e5bb8067ec1f19e0d29` | `e05f1acee0f18d575e8379b3fd9035b1a00ef45e92f29e5a97607e4b0417cd24` |
| `.gov-runtime/codeintel/home/code.db` | `fbbe7d44144a49f16fab5f970e3670bd4b79a8c3db949bf7206ec99287654133` | `b3f63ff3f38e447145801e3cd36c4280a05747e9c460403128f1affca40bfab9` | `6307419869dc8ebb7fcecdf00f3934336de6e353230138cab98e2e02ecf57490` |
| `.gov-runtime/codeintel/home/_config.db` | `6881a590e961b4c4faff0180c79e87d6af9c34a9367e12cf28bbe2dbc4028cf8` | the same (also W2-61's and W2-86's) | the same |

The digests differ because the record graph differs (each head holds the ticket's commits; the digest covers the record graph only, as W2-86's §2 says). Run 2's head store holds 1,863 records and 2,770 paths with chunks, 150 of them code files (`.py`, no test) that the code route's rule reads (§6).

## 3. The runs

Each run measured the visible half. Times UTC, 2026-11-01.

| Run | Tree | Retriever (`--gov`) | Start | End | Length | Exit | stderr | Record | `--compare` |
|---|---|---|---|---|---|---|---|---|---|
| control | base `7ca16b19df3f` | `gov-base` (the base's own code) | 13:47:34 | 14:00:24 | 770 s (12 min 50 s) | 0 | empty | `measure-memory-retrieval-visible-20261101T140024036524Z.json` | — |
| head, run 1 (history) | head `fb0c8c430171` | `gov-head` (the head's own code) | 15:31:01 | 16:13:33 | 2,552 s (42 min 32 s) | 0 | empty | `measure-memory-retrieval-visible-20261101T161333491429Z.json` | the control's record |
| **head, run 2** | head `d72c96fc029c` | `gov-head` (the head's own code) | 20:37:37 | 20:50:24 | **767 s (12 min 47 s)** | 0 | empty | `measure-memory-retrieval-visible-20261101T205024907715Z.json` | the control's record |

The records are under `/home/usain/gov-os-runs/W2-92/records/`; each is byte-identical to its run's stdout (`/tmp/gov-os-lead-W2-92/log/measure-base.json`, `measure-head.json`, `measure-head2.json`; run 2's checked with `cmp`). A comparison covers five fields per question: hit@5, in the bundle, full evidence, the first gold rank and the stacked digest (the paths and line spans of the stacked context, in order). Pieces found is not one of them.

**The run's length.** Run 2 took 767 s, as long as the control (770 s) and 0.30 times run 1's (2,552 s). It made 53 calls against the control's 52 and run 1's 72; the one extra call against the control is Q11's (2 → 3, as in run 1). Each call took 14.5 s on average, against the control's 14.8 s and run 1's 35.4 s. Run 2's code route takes words in 4 questions where run 1's took them in 15 (§6), and each process starts the code-graph tool once, not once per call. The records hold no time per call, so how much of the drop the cue gate gave, how much the single session and how much the front-matter cache is not shown.

**The context-reproducibility check** at `d72c96fc029c`, alone, as the runner runs it (`ctx-head2.sh`: `python3 -m gov.context.context_check` under `timeout 3000`, in this worktree, whose `src/` is the same as `d72c96fc029c`'s): 20:39:15 to 20:44:08, **293 s**, exit 0, `context-reproducibility: green`; its limit is 600 s. Run 1's checks, which ran side by side from 17:49: the head's 17:49:32 to 18:18:54 (1,762 s by its start and end files, which keep whole seconds; printed green but over the limit) and the base's 17:49:33 to 17:57:29 (476 s). The engineer who built P-4 counted, during building: 180 tickets, 2 context questions on the code route (code-shaped words), one tool session for the process. That count is the building engineer's, not a record's.

## 4. The totals: both figures together

| | hit@5, against CAP-10's floor of 85 and the owner's target of 95 % (DEC-957) | Full evidence, against the owner's target of 99 % | In the bundle |
|---|---|---|---|
| W2-61 baseline (`23079f92a6fa`, pinned gov `5c40122014da`) | 8 of 20 (40 %), short of 85 by 45 points, of 95 by 55 | 12 of 20 (60 %), short by 39 points | 14 of 20 |
| W2-86 head (`338c14fa6475`, pinned gov; W2-86's result) | 7 of 20 (35 %), short of 85 by 50 points, of 95 by 60 | 11 of 20 (55 %), short by 44 points | 13 of 20 |
| W2-86 head, tree code (`338c14fa6475`, its own code; W2-86's supplementary run) | 11 of 20 (55 %), short of 85 by 30 points, of 95 by 40 | 11 of 20 (55 %), short by 44 points | 15 of 20 |
| control (`7ca16b19df3f`, its own code) | 11 of 20 (55 %), short of 85 by 30 points, of 95 by 40 | 11 of 20 (55 %), short by 44 points | 15 of 20 |
| head, run 1 (`fb0c8c430171`, its own code; history) | 10 of 20 (50 %), short of 85 by 35 points, of 95 by 45 | 12 of 20 (60 %), short by 39 points | 15 of 20 |
| **head, run 2 (`d72c96fc029c`, its own code; the ticket's figures)** | **11 of 20 (55 %), short of 85 by 30 points, of 95 by 40** | **13 of 20 (65 %), short by 34 points** | **16 of 20** |

**Run 2's head against the control** (the like-for-like pair: each tree answered by its own code, on stores its own code built): hit@5 stays at 11 of 20, full evidence goes from 11 to 13 of 20, and in the bundle from 15 to 16 of 20. Two questions gained full evidence (Q10, Q11), one entered the bundle (Q10), none lost a figure; Q08's first gold rank fell one place (10 → 11).

**Run 2's head against run 1's head:** hit@5 goes from 10 to 11 of 20 and full evidence from 12 to 13 of 20; in the bundle goes from 15 to 16 of 20. Q17 is back in the first five and in the bundle, Q09 has its evidence back, and Q10 and Q11 keep what they gained.

Both figures are still far from their targets: hit@5 at 55 %, 30 points short of the floor of 85 and 40 short of 95; full evidence at 65 %, 34 points short of 99.

## 5. Per question, visible half

Each cell gives, in order: hit@5, first gold rank, in the bundle, full evidence (pieces found of needed). "First gold rank" is the rank, in the stacked context, of the first item that matches a gold source; "in the bundle" means an item of the first call matches one. W2-61's baseline is its §5. "Calls" is the control's, run 1's head's, then run 2's head's. "Run 2 against control" is run 2's `--compare`; "run 2 against run 1" compares the same five fields of the two head records.

| Q | W2-61 baseline | control | head, run 1 | **head, run 2** | Calls | Run 2 against control | Run 2 against run 1 |
|---|---|---|---|---|---|---|---|
| Q01 | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | 5 → 5 → 5 | stacked digest | stacked digest |
| Q02 | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | 2 → 5 → 2 | same | stacked digest |
| Q03 | yes, 4, yes, yes (1/1) | yes, 2, yes, yes (1/1) | yes, 2, yes, yes (1/1) | yes, 2, yes, yes (1/1) | 2 → 2 → 2 | same | same |
| Q04 | yes, 3, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | 2 → 3 → 2 | stacked digest | stacked digest |
| Q05 | yes, 2, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | 2 → 2 → 2 | same | same |
| Q06 | no, 9, yes, yes (2/2) | no, 7, yes, yes (2/2) | no, 7, yes, yes (2/2) | no, 7, yes, yes (2/2) | 3 → 3 → 3 | same | stacked digest |
| Q07 | no, 12, yes, yes (1/1) | no, 6, yes, yes (1/1) | no, 6, yes, yes (1/1) | no, 6, yes, yes (1/1) | 5 → 5 → 5 | same | stacked digest |
| **Q08** | no, 9, yes, yes (1/1) | no, 10, yes, yes (1/1) | no, 8, yes, yes (1/1) | **no, 11, yes, yes (1/1)** | 2 → 3 → 2 | first gold rank, stacked digest | first gold rank, stacked digest |
| **Q09** | no, 60, no, yes (1/1) | no, 44, no, yes (1/1) | no, none, no, no (0/1) | **no, 44, no, yes (1/1)** | 4 → 5 → 4 | same | full evidence, first gold rank, stacked digest |
| **Q10** | no, 25, no, no (1/2) | no, none, no, no (0/2) | no, 6, yes, yes (2/2) | **no, 8, yes, yes (2/2)** | 2 → 2 → 2 | in the bundle, full evidence, first gold rank, stacked digest | first gold rank, stacked digest |
| **Q11** | yes, 4, yes, no (1/2) | yes, 4, yes, no (1/2) | yes, 4, yes, yes (2/2) | **yes, 5, yes, yes (2/2)** | 2 → 3 → 3 | full evidence, first gold rank, stacked digest | first gold rank, stacked digest |
| Q12 | yes, 2, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | 2 → 2 → 2 | stacked digest | stacked digest |
| Q13 | no, 6, yes, no (1/2) | yes, 1, yes, no (1/2) | yes, 1, yes, no (1/2) | yes, 1, yes, no (1/2) | 2 → 2 → 2 | stacked digest | same |
| **Q14** | no, 16, yes, no (7/9) | no, 17, yes, no (4/9) | no, 16, yes, no (3/9) | **no, 17, yes, no (4/9)** | 5 → 5 → 5 | stacked digest | first gold rank, stacked digest |
| Q15 | yes, 4, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | 2 → 2 → 2 | stacked digest | same |
| Q16 | no, 7, yes, yes (1/1) | no, none, no, no (0/1) | no, none, no, no (0/1) | no, none, no, no (0/1) | 2 → 6 → 2 | same | stacked digest |
| **Q17** | no, 21, no, no (1/2) | yes, 2, yes, no (1/2) | no, 21, no, no (1/2) | **yes, 2, yes, no (1/2)** | 2 → 5 → 2 | stacked digest | hit@5, in the bundle, first gold rank, stacked digest |
| **Q18** | no, none, no, no (0/2) | no, none, no, no (0/2) | no, 61, no, no (1/2) | **no, none, no, no (0/2)** | 2 → 5 → 2 | stacked digest | first gold rank, stacked digest |
| Q19 | no, none, no, no (0/1) | no, none, no, no (0/1) | no, none, no, no (0/1) | no, none, no, no (0/1) | 2 → 5 → 2 | same | stacked digest |
| Q20 | no, 21, no, no (1/2) | yes, 2, yes, no (1/2) | yes, 2, yes, no (1/2) | yes, 2, yes, no (1/2) | 2 → 2 → 2 | same | same |

**The control against W2-86's head with tree code** (each tree answered by its own code; the trees differ, `338c14fa6475` and `7ca16b19df3f`): the same totals (11, 11 and 15 of 20) and the same cells, but Q08's first gold rank (11 there, 10 here). Calls are the same in both for every question.

**What changed, control to run 2's head:** hit@5, in the bundle or full evidence differ for 2 questions, both up: Q10 (in the bundle and full evidence) and Q11 (full evidence). Q08, Q10 and Q11 moved in rank. Nine questions are the same as the control in all five fields, the stacked digest included: Q02, Q03, Q05, Q06, Q07, Q09, Q16, Q19 and Q20. The stacked digest differs for 11 of 20 (against 17 of 20 in run 1). Pieces found moved for Q10 (0 → 2 of 2) and Q11 (1 → 2 of 2) only.

**What changed, run 1's head to run 2's:** Q17 (hit@5 and in the bundle back), Q09 (full evidence back, rank none → 44), Q14 (3 → 4 of 9, rank 16 → 17), Q18 (1 → 0 of 2, rank 61 → none), Q08 (rank 8 → 11), Q10 (rank 6 → 8) and Q11 (rank 4 → 5). Q03, Q05, Q13, Q15 and Q20 are the same in all five fields in both heads.

## 6. The graph and code-graph questions

**How the routes were read.** The records hold, per question, the five compared fields, the pieces and the number of calls; they hold no item, no route and no facet. So what each route did is read from run 2's own rules applied to the questions' text, read-only: `graph_route._named`, `W2_ID`, `_wbs_ids` and `_title` (with run 2's substring test) against run 2's head store's `records` and `register_entries` (the store opened immutable), and `code_route._CUE`, `_CODE_SHAPED`, `_WORD` and `_defined`'s pattern against the 150 code files of that store (`/tmp/gov-os-lead-W2-92/eng7/routes2.py`, run with `PYTHONPATH` set to this worktree's `src/`, the same as `d72c96fc029c`'s). Neither route was run and no question was retrieved. Whether the code-graph tool holds a symbol of a taken word (and so whether the route gives spans) is not shown; where the calls or the digest say something about it, it is given.

**The record route** (`graph_route.start_ids`: a record's id, a W2 id resolved to its ticket, or a record's title, found whole in the question) takes the same four questions as in run 1; its rule did not change:

| Q | What it names | Already a start id at the control? | Run 2 against control, and against run 1 |
|---|---|---|---|
| Q01 | `DEC-782`, by id | no: the question has no `ticket` or `ids`, so the record closure of DEC-782 is a new route at the head | hit@5 yes and full evidence 1 of 1 (rank 1) in all three; the stacked digest differs from the control's and from run 1's |
| Q06 | W2 id `W2-54` → `DAEO-0rfi` | yes (`--ticket DAEO-0rfi`) | hit@5 no (rank 7) and full evidence 2 of 2 in all three; **the stacked digest is the control's**, so the route adds nothing new |
| Q07 | the title of `DAEO-0mab` (the Track A gate run), found whole | yes (`--ticket DAEO-0mab`) | hit@5 no (rank 6) and full evidence 1 of 1 in all three; **the stacked digest is the control's**: nothing new |
| Q14 | W2 id `W2-03` → `DAEO-ym8a` | yes (`--ticket DAEO-ym8a`, radius 1) | hit@5 no and full evidence no: rank 17 and 4 of 9, as the control (run 1: 16 and 3 of 9); the digest differs from the control's |

So on this set the record route gives a new start only for Q01, whose figures were already at their best. For Q06 and Q07 run 2 shows what run 1 could only infer: with no code route word in them, their stacked contexts are the control's to the digest, so the record route that finds the given ticket adds nothing. None of the four moved on the record route's account.

**The code route at run 2's code** takes a word in 4 of the 20 questions (run 1: 15). Two have a code cue and a plain word that a code file defines; two have a word shaped as code and no cue. The other 16 have no cue and no shaped word, so no plain word joins and the code index is not asked.

| Q | Cue | Words run 2's rule takes | Calls (control → run 1 → run 2) | Run 2 against control, and against run 1 |
|---|---|---|---|---|
| Q10 | `calls` | `indexable` (plain; `src/gov/secrets/__init__.py`, line 311), as well as `--id indexable` | 2 → 2 → 2 | hit@5 no → no; rank none → 8 (run 1: 6); in the bundle no → yes; full evidence 0 → 2 of 2 (gained, as in run 1) |
| Q11 | `calls` | `rrf` (plain; `src/gov/retrieval/fusion.py`, line 25), as well as `--id rrf` | 2 → 3 → 3 | hit@5 yes → yes; rank 4 → 5 (run 1: 4); full evidence 1 → 2 of 2 (gained, as in run 1) |
| Q12 | none | `CONTINUATION_INVALID` (shaped: an underscore inside) | 2 → 2 → 2 | hit@5 yes and full evidence 1 of 1 (rank 1) in all three; the digest differs from the control's and from run 1's |
| Q18 | none | `PreCompact` (shaped: a capital inside) | 2 → 5 → 2 | hit@5 no and full evidence no in all three; pieces 0 of 2 and no gold ranked, as the control (run 1: 1 of 2 at rank 61); the digest differs from both |

**The questions run 1's code route took and run 2's does not** (no code cue, so their plain words no longer join): Q02, Q04, Q05, Q06, Q07, Q08, Q09, Q14, Q16, Q17 and Q19. Of these, Q02, Q05, Q06, Q07, Q09, Q16 and Q19 are now the control's in all five fields, the digest included; Q04, Q08, Q14 and Q17 differ from the control in the digest (and Q08 in rank).

**Why each moved, as far as the records show:**

- **Q10 and Q11 (the callers' questions) stay up.** The cue `calls` lets the plain names join, as run 1's rule let them without a cue, so both gain what they gained in run 1: both gold pieces of each are the calling lines, and the code route gives each caller's whole span (run 1's §6 gives the callers: `indexable` inside the lexical index's function and `gov.codeintel.index`; `rrf` inside `fusion.search` and `retrieve.retrieve`). Against the control, Q10 went from no piece to both, entered the bundle, its first piece at rank 8, and Q11 gained its second piece. Each fell in rank against run 1 (Q10 6 → 8, Q11 4 → 5) with the same words taken; the tree and its stores differ between the two heads (`git diff --stat fb0c8c430171 d72c96fc029c`: 8 files, among them `retrieve.py`, one of `rrf`'s callers, the unit and acceptance tests, a checkpoint and this record's run 1 text), but the records do not show which items now rank above the gold, so why they fell is not shown. Q10's hit@5 is still no (rank 8) with full evidence yes; Q11's hit@5 stays yes, with full evidence yes.
- **Q17 is back in the first five** (hit@5 yes, rank 2, in the bundle; full evidence no, 1 of 2: the control's figures; run 1: rank 21, out of the bundle). Its plain words `search` and `embedded` name functions but the question has no code cue, so at run 2 the code route takes nothing. Between run 1 and run 2 the code route is the one route that changed for Q17, and with it gone the figures are the control's: this supports run 1's likely cause (the code route's hits pushed the gold down). The digest still differs from the control's; neither route takes a word, so the difference comes from the tree and its stores, and the records do not show which items.
- **Q09 has its evidence back** (hit@5 no, rank 44, out of the bundle, full evidence 1 of 1: the control's figures; run 1: rank none, 0 of 1). Its plain word `context` no longer joins without a cue; the record route takes nothing (the question gives its ticket). Its stacked context is the control's to the digest, over the same 4 calls: run 1's loss came with the code route's items for `gov.context.context`.
- **Q08 fell one rank against the control** (10 → 11; run 1: 8; hit@5 no and full evidence 1 of 1 in all three). The code route no longer takes `commit` and `index`, so run 1's two-place rise went with it. Rank 11 is also W2-86's tree-code head's figure. Neither route takes a word at run 2, so the place lost against the control comes from the tree and its stores; the records do not show which item came ahead of the gold.
- **Q14 is back at the control's figures** (rank 17, 4 of 9; hit@5 no and full evidence no; run 1: 16 and 3 of 9). The record route adds nothing (the ticket was given) and the code route no longer takes `tickets`. All three runs stopped at 5 calls with the stack budget reached; run 1's lost piece went with the code route's items, which took the stack's room. Which piece that was is not shown. The digest still differs from the control's (the tree and its stores).
- **Q18 lost run 1's piece** (1 → 0 of 2, rank 61 → none; hit@5 no and full evidence no in all three). Run 1's code route took the plain `write` (`gov.checkpoint.record.write`, called by the PreCompact hook's `main` at the gold line); at run 2 `write` does not join without a cue, and the piece is gone. This supports run 1's likely cause. The shaped word `PreCompact` still joins; whether the tool holds a symbol of that name is not shown. The digest differs from the control's and from run 1's, so something entered the stacked context, none of it gold.
- **Q12** keeps its figures in all three runs (rank 1); the shaped `CONTINUATION_INVALID` joins in both heads, and the digest moved each time. Whether the route gave spans is not shown.
- **Unchanged figures with a moved digest and no route** (Q04, Q13, Q15): neither route takes a word at run 2, so the digest's move comes from the tree and its stores. Q13's and Q15's digests are the same as run 1's head's (neither route took a word in run 1 either); Q04's differs from both. The records do not show which items.

## 7. Deviations and what they mean

1. **The retriever is each clone's own code, not the pinned gov** that W2-61's §8 names. The change is code, so the pinned gov would not measure it.
   - **What it means:** the pairs head against control are like for like. W2-61's baseline and W2-86's head (pinned gov) are not; W2-86's supplementary head with tree code is the nearest earlier figure, and the control equals it but for one rank (§5).
2. **The control was not run again for run 2** (DEC-833's kept control): its tree, stores and record are run 1's, and its store files hash the same after run 2 (§2).
   - **What it means:** the control's figures are from 13:47 to 14:00; run 2's head was measured from 20:37 to 20:50 with the same measure code and set (§1).
3. **The context check ran beside run 2's measure:** 20:39:15 to 20:44:08, inside the measure's 20:37:37 to 20:50:24. Both ran on the same machine for 293 s of the measure's 767 s.
   - **What it means:** run 2's length (767 s) was taken with the check's load beside it for part of the run; it is still the control's length. The check's 293 s was taken with the measure beside it.
4. **Run 1's head rebuild's first try exited 69** (`rebuild-head-try1.exit`, 15:07). Only its exit code was kept; the records do not say why. Run 1's head rebuild is the second try. Run 2's rebuild succeeded on its first try.
5. **Run 2's rebuild took 81.5 s against run 1's 999.1 s** (§2); its JSON does not say why.
6. **One run each, no repeat:** W2-61's §8 step 4 (a repeat on the same index and after a rebuild) was not run. The checks of stability are the control's agreement with W2-86's tree-code head on a different tree (§5), and run 2's agreement with the control to the digest on the nine questions that no route touches differently (§5).
7. **The disk gate's readings were logged for run 2 only, and the load not at all.** The base rebuild waited 35 minutes on the shared lock (12:39:37 to 13:14:37) and ran to its end.
8. **The routes' work is read from their rules, not from the records** (§6): the measure keeps no items or facets, so "the likely cause" is said where the records do not show one.

## 8. Scope

The visible half only. The cue gate (P-3) was tuned on the visible half; DEC-1006 has it judged again on W2-61h's enlarged set, which is not measured here. The hidden half was neither read nor run. On this set only Q10 and Q11 are callers' questions and only Q01, Q06, Q07 and Q14 name a record, so this measure says little about how the two routes do on the questions they were built for.

## 9. How to repeat it

W2-61's §8, with these changes:

1. **Three clones by exact path,** each `git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS <path>`, detached: `/home/usain/gov-os-runs/W2-92/base` at `7ca16b19df3f`, `/home/usain/gov-os-runs/W2-92/head` at `d72c96fc029c` (fetched from `w2/W2-92`; run 1: `fb0c8c430171`), and `/home/usain/gov-os-runs/W2-92/measure` at `160736409bc4` (run 1: `c38a5b49bc86`; the measure and the visible set are the same at both).
2. **Two retrievers,** the pinned launcher's body under a first line `#!/usr/bin/env -S PYTHONPATH=<clone>/src /usr/bin/python3`: `gov-base` and `gov-head` (§1).
3. **The stores,** in each clone by its own retriever, with embeddings, after the disk gate: `env -u GOV_TICKET TMPDIR=/tmp/gov-os-lead-W2-92 flock /tmp/gov-os-rebuild.lock <gov-base|gov-head> rebuild --json` (`/tmp/gov-os-lead-W2-92/bin/rebuild-base.sh`; `rebuild-head2.sh <commit>`, which fetches, detaches and rebuilds the head clone). Record its `digest` and the sha256 of `.gov-runtime/store.db`, `.gov-runtime/codeintel/home/code.db` and `.gov-runtime/codeintel/home/_config.db`.
4. **The measure,** first the control, then the head with `--compare` the control's record (`measure-base.sh`, `measure-head2.sh`):

   ```
   env -u GOV_TICKET TMPDIR=/tmp/gov-os-lead-W2-92 PYTHONPATH=/home/usain/gov-os-runs/W2-92/measure/src python3 -m gov.retrieval.measure memory-retrieval \
     --root /home/usain/gov-os-runs/W2-92/<base|head> --sets-root /home/usain/gov-os-runs/W2-92/measure --part visible \
     --gov /tmp/gov-os-lead-W2-92/bin/gov-<base|head> --out /home/usain/gov-os-runs/W2-92/records --json \
     [--compare <the control's record>]
   ```

   The budgets are the measure's defaults: `--batch-size 10 --bundle-budget 6000 --stack-budget 24000`.
5. **The context check,** alone and not beside the measure (deviation 3): `TMPDIR=/tmp/gov-os-lead-W2-92 PYTHONPATH=<the head's src> timeout 3000 python3 -m gov.context.context_check` (`ctx-head2.sh`); its limit is 600 s.
6. **The routes' reading** (§6): apply `graph_route`'s and `code_route`'s rules, the cue gate included, to the questions' text against the head store opened immutable (`/tmp/gov-os-lead-W2-92/eng7/routes2.py <head clone> <visible set>`); run no route and retrieve no question.
7. **Never `--part hidden`.**

## 10. Drift before and after the stated links (S10, DEC-1072 (1), DEC-1073 (2))

- **The question:** of the decisions current though the register states them changed, how many does a search that reaches the decision also reach a changer of?
- **The definitions are the census's** (`docs/research/D4B-link-census.py`, `3d1c459e`). A statement is a register label, its free text, the change log or ARCHIVE-SUPERSEDED §A. The register's statements come from `loader.register_statements`, which gives the census's 3,171 statements one for one on this repository's register (S7; `tests/unit/store/test_w2_92_links.py`). Current means status ACCEPTED and no SUPERSEDES edge in `edges`. DEC-1073 (2): the decisions ARCHIVE-SUPERSEDED §B calls spent are listed apart for a status reconciliation and are not counted; a decision that is not ACCEPTED (PROPOSED above all) is never current and is counted apart, by status.
- **Before:** a one-hop SUPERSEDES edge in `edges` from a changer to the decision (all the graph held). **After:** the same, or an AMENDS or SUPERSEDES row of `stated_links`. **Reached by the hop:** `graph_route.follow` from the decision and its closure at R0/R1, within its bound of 12 records.
- **The command** (read-only; no model, no network, no GPU; writes nothing but `<out.json>`), on the rebuilt store:

  ```
  PYTHONPATH=<tree>/src python3 docs/research/W2-92-proto-drift.py <tree> <out.json>
  ```

  `--from-head` reads the records and links from HEAD by the loader's own rule, with no store.

| Figure | On the rebuilt store (the CTO) |
|---|---:|
| Store head, fingerprints row | `d9d48449` (the measure clone `~/gov-os-runs/D4B/w4-92`, rebuilt 2026-11-05) |
| Stated links by type (CITES, OF_TASK, UNDER, AMENDS, SUPERSEDES) | 1,679; 381; 2,481; 388; 7 |
| Drifted current, spent included (the census's count) | 221 |
| Drifted current (counted) / of them with no hint in their own entry | 190 / 83 |
| Spent, for the status reconciliation (of them stated changed) | 110 (31) |
| Stated changed but not ACCEPTED, by status | PROPOSED 12, SUPERSEDED 7, DONE 1 |
| **Before:** one-hop edge to a changer | 0 |
| **After:** one-hop link to a changer / to every changer | 190 / 184 |
| **After:** reached by the hop, a changer / every changer | 190 / 184 (not joined: none) |
| Changer pairs / joined after | 325 / 312 |

The engineer's reading with `--from-head` at the ticket's head (`5a9e36c07571` plus W2-92 S7), not the figure of record: links CITES 1,679, OF_TASK 381, UNDER 2,481, AMENDS 388, SUPERSEDES 7; drifted current 221 with the spent and 190 counted (83 with no hint), 110 spent for the reconciliation (31 of them stated changed); not ACCEPTED: PROPOSED 12, SUPERSEDED 7, DONE 1. **Before 0, after 190 of 190** joined to a changer (184 to every changer); reached by the hop 190 (184 every changer); changer pairs 325, 312 joined.

**The CTO's measure of the build (DEC-1071's rule, DEC-1074 (5); 2026-11-05):** the harness's v456 on the build
(`d9d48449`) against the same on integrate's head (`5a9e36c0`, the control), one run each, counts only. The 79: 67
against 67, visible 33 and hidden 34 on both (the halves' gap −4.7 on both), MRR over the 79 0.6306 against 0.6242:
**adopted by the rule** (the 79 not lower, the gap not wider, MRR higher). Beside it, the 138 (with the spent 59): 106
against 105, the spread between the three sets 21.1 against 22.8. Records `~/gov-os-runs/D4B/w4-i-rx`, `w4-92-rx`.
