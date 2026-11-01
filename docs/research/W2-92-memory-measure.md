# W2-92 memory measure: W2-61's 20-question measure after the record and code routes, visible half

- **Ticket:** DAEO-n0wb (W2-92), profile STANDARD. Written by the engineer from the outputs of the measure its lead ran.
- **Date:** 2026-11-01.
- **Sources:** DEC-957 (memory's target of 95 %; the record and code routes), DEC-833 (both figures, always together), DEC-860 (retrieval in batches, ranked and stacked), DEC-859 (a code question takes the code-graph tool's own traversal), DEC-941 item 1 (the measure re-run beside W2-61's baseline), CAP-10 (the floor of 85 for hit@5); the ticket's KPI 5 and its failure line. The figures beside these are `docs/research/W2-61-baseline.md` and W2-86's record (`docs/research/W2-86-memory-measure.md` on `w2/W2-86`, not yet on `w2/integrate`).

This record holds scores: ids, counts, ranks, digests and pass or fail. It quotes no gold answer and no text of a retrieved item. Of the questions' text it names only the ids, titles and words that the two new routes' rules take (§6). The hidden half of the set was neither read nor run.

## 1. What was measured, and where

- **The three clones,** each `git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS <path>`, left detached:

  | Clone | Commit | What it is |
  |---|---|---|
  | `/home/usain/gov-os-runs/W2-92/base` | `7ca16b19df3f` | the ticket's base; the tree measured as the control |
  | `/home/usain/gov-os-runs/W2-92/head` | `fb0c8c430171` | the ticket's final code commit (`rebuild-head.commit`); the tree measured as the head |
  | `/home/usain/gov-os-runs/W2-92/measure` | `c38a5b49bc86` | `w2/integrate`'s head when cloned: the measure's code and the visible set only |

- **What differs, base to head:** `git diff --stat 7ca16b19df3f fb0c8c430171` gives 11 files: the code `src/gov/retrieval/code_route.py` (new, 138 lines), `src/gov/retrieval/graph_route.py` (new, 78 lines) and `src/gov/retrieval/retrieve.py` (14 lines), and the ticket's tests. The base is an ancestor of the head.
- **The retrievers: each clone's own code.** The change is code, so the code under test builds the stores and answers the questions. Each retriever is the pinned launcher's body under a first line that sets `PYTHONPATH` to that clone's `src/`:
  - **control:** `/tmp/gov-os-lead-W2-92/bin/gov-base`, first line `#!/usr/bin/env -S PYTHONPATH=/home/usain/gov-os-runs/W2-92/base/src /usr/bin/python3`. The record's `retriever.version`: `gov 0.1.0 (commit 7ca16b19df3f)`; `retriever.gov_file`: `/home/usain/gov-os-runs/W2-92/base/src/gov/__init__.py`.
  - **head:** `/tmp/gov-os-lead-W2-92/bin/gov-head`, first line `#!/usr/bin/env -S PYTHONPATH=/home/usain/gov-os-runs/W2-92/head/src /usr/bin/python3`. The record's `retriever.version`: `gov 0.1.0 (commit fb0c8c430171)`; `retriever.gov_file`: `/home/usain/gov-os-runs/W2-92/head/src/gov/__init__.py`.
- **The measure:** `src/gov/retrieval/measure.py` from the measure clone (last changed at `289b9314a763`), run with `PYTHONPATH` set to that clone's `src/` and `GOV_TICKET` removed; the retrieving process is the `--gov` given.
- **The set:** `memory-retrieval`, the visible half only (`--part visible`): Q01 to Q20, read from the measure clone (`--sets-root`); the visible set last changed at `80c96c44bdcf`.
- **The budgets:** the measure's defaults, `--batch-size 10`, `--bundle-budget 6000`, `--stack-budget 24000` (each record's `budget`), as in W2-61's baseline and W2-86's record.

## 2. The stores' fingerprint

Each clone's stores were built in that clone by that clone's own code, with embeddings, as `env -u GOV_TICKET TMPDIR=/tmp/gov-os-lead-W2-92 flock /tmp/gov-os-rebuild.lock <gov-base|gov-head> rebuild --json`, after the disk gate (`rebuild-base.sh`, `rebuild-head.sh`). Times UTC, 2026-11-01. "Start" is when the command began to wait on the shared lock; the lock's own times and the length are the JSON's.

| | base (control) | head |
|---|---|---|
| Start (waiting on the lock) | 12:39:37 | 15:08:36 |
| Lock taken and released (`result.lock`) | 13:14:37 to 13:30:44 | 15:12:34 to 15:29:13 |
| End | 13:32:29 | 15:30:44 |
| Length (`timing.total_s`) | 967.4 s (semantic 930.5, lexical 10.5, code index 18.1) | 999.1 s (semantic 963.1, lexical 9.5, code index 20.0) |
| Exit code; stderr | 0 (`ok: true`); empty | 0 (`ok: true`); empty |
| Stores (`lexical`, `semantic`, `codeintel`) | each `recreated` | each `recreated` |
| Files compacted | `store.db`, `codeintel/home/_config.db`, `codeintel/home/code.db` | the same three |
| Secrets scan (`secrets_counts`) | content 12 scanned, 5,602 remembered; paths 0 and 2,801 | content 16 scanned, 5,618 remembered; paths 3 and 2,808 |

**The digest each rebuild records** (`result.digest`; `result.store.digest` is the same value, with no invalid entries):

- base (control): `632ae8729926f639a07f2a9e11073710d61341680cb4aac4dec7766449cc24fc`
- head: `a97f01cfdd9e1d43298ded415dfe41187a7ba4335d5de28cad178c2551ce1a3d`

**The sha256 of each store file** (read with `sha256sum` after both measures had run; no store was opened for writing):

| Store file | base (control) | head |
|---|---|---|
| `.gov-runtime/store.db` | `aacb41d66c5f43881563ca452427ec2facb4ed63458c061bc80037538b7975a0` | `f8f591b9285a1959198f75ba4d1a466a112d2f28b4418e5bb8067ec1f19e0d29` |
| `.gov-runtime/codeintel/home/code.db` | `fbbe7d44144a49f16fab5f970e3670bd4b79a8c3db949bf7206ec99287654133` | `b3f63ff3f38e447145801e3cd36c4280a05747e9c460403128f1affca40bfab9` |
| `.gov-runtime/codeintel/home/_config.db` | `6881a590e961b4c4faff0180c79e87d6af9c34a9367e12cf28bbe2dbc4028cf8` | the same (also W2-61's and W2-86's) |

The digests differ because the record graph differs (the head holds the ticket's commits; the digest covers the record graph only, as W2-86's §2 says). The head store holds 2,768 paths with chunks, 150 of them code files (`.py`, no test) that the code route's rule reads (§6).

## 3. The runs

Each run measured the visible half. Times UTC, 2026-11-01.

| Run | Tree | Retriever (`--gov`) | Start | End | Length | Exit | stderr | Record | `--compare` |
|---|---|---|---|---|---|---|---|---|---|
| control | base `7ca16b19df3f` | `gov-base` (the base's own code) | 13:47:34 | 14:00:24 | 770 s (12 min 50 s) | 0 | empty | `measure-memory-retrieval-visible-20261101T140024036524Z.json` | — |
| head | head `fb0c8c430171` | `gov-head` (the head's own code) | 15:31:01 | 16:13:33 | 2,552 s (42 min 32 s) | 0 | empty | `measure-memory-retrieval-visible-20261101T161333491429Z.json` | the control's record |

The records are under `/home/usain/gov-os-runs/W2-92/records/`; each is byte-identical to its run's stdout (`/tmp/gov-os-lead-W2-92/log/measure-base.json`, `measure-head.json`). A comparison covers five fields per question: hit@5, in the bundle, full evidence, the first gold rank and the stacked digest (the paths and line spans of the stacked context, in order). Pieces found is not one of them.

**The head run took 3.3 times the control's length** (2,552 s against 770 s). The records show two parts of it: the head made 72 calls against the control's 52 (1.38 times as many), and each took 35.4 s on average against 14.8 s (2.4 times as long). What the code shows of the cause: a continuation token is stateless (an offset, DEC-422), so every call, the first and every continuation page, runs `retrieve` again with all its routes, and the code route among them. On each call the code route reads the 150 code files of the store for the question's plain words (`code_route._defined`), and for the 15 questions where its rule takes a word (§6) it starts a session of the code-graph tool and asks `search_graph` and `query_graph`. The 20 extra calls are all in those 15 questions (they made 59 of the head's 72 calls). The records hold no time per call and no load reading, so how much of the length each of these took, and how much the machine's load added, is not shown.

## 4. The totals: both figures together

| | hit@5, against CAP-10's floor of 85 and the owner's target of 95 % (DEC-957) | Full evidence, against the owner's target of 99 % | In the bundle |
|---|---|---|---|
| W2-61 baseline (`23079f92a6fa`, pinned gov `5c40122014da`) | 8 of 20 (40 %), short of 85 by 45 points, of 95 by 55 | 12 of 20 (60 %), short by 39 points | 14 of 20 |
| W2-86 head, tree code (`338c14fa6475`, its own code; W2-86's supplementary run) | 11 of 20 (55 %), short of 85 by 30 points, of 95 by 40 | 11 of 20 (55 %), short by 44 points | 15 of 20 |
| control (`7ca16b19df3f`, its own code) | 11 of 20 (55 %), short of 85 by 30 points, of 95 by 40 | 11 of 20 (55 %), short by 44 points | 15 of 20 |
| **head (`fb0c8c430171`, its own code)** | **10 of 20 (50 %), short of 85 by 35 points, of 95 by 45** | **12 of 20 (60 %), short by 39 points** | **15 of 20** |

**Head against control** (the like-for-like pair: each tree answered by its own code, on stores its own code built): hit@5 11 → 10 of 20, and full evidence 11 → 12 of 20; in the bundle 15 → 15 of 20. One question left the first five (Q17), two gained full evidence (Q10, Q11) and one lost it (Q09). Both figures stay far from their targets: hit@5 at 50 % against 85 and 95, full evidence at 60 % against 99.

## 5. Per question, visible half

Each cell gives, in order: hit@5, first gold rank, in the bundle, full evidence (pieces found of needed). "First gold rank" is the rank, in the stacked context, of the first item that matches a gold source; "in the bundle" means an item of the first call matches one. W2-61's baseline is its §5; W2-86's is its supplementary head with tree code (its §5). "Calls" is the control's, then the head's. The last column is the head run's `--compare` against the control.

| Q | W2-61 baseline | W2-86 head, tree code | control | head | Calls | Head against control |
|---|---|---|---|---|---|---|
| Q01 | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | 5 → 5 | stacked digest |
| Q02 | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | 2 → 5 | stacked digest |
| Q03 | yes, 4, yes, yes (1/1) | yes, 2, yes, yes (1/1) | yes, 2, yes, yes (1/1) | yes, 2, yes, yes (1/1) | 2 → 2 | same |
| Q04 | yes, 3, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | 2 → 3 | stacked digest |
| Q05 | yes, 2, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | 2 → 2 | same |
| Q06 | no, 9, yes, yes (2/2) | no, 7, yes, yes (2/2) | no, 7, yes, yes (2/2) | no, 7, yes, yes (2/2) | 3 → 3 | stacked digest |
| Q07 | no, 12, yes, yes (1/1) | no, 6, yes, yes (1/1) | no, 6, yes, yes (1/1) | no, 6, yes, yes (1/1) | 5 → 5 | stacked digest |
| Q08 | no, 9, yes, yes (1/1) | no, 11, yes, yes (1/1) | no, 10, yes, yes (1/1) | no, 8, yes, yes (1/1) | 2 → 3 | first gold rank, stacked digest |
| **Q09** | no, 60, no, yes (1/1) | no, 44, no, yes (1/1) | no, 44, no, yes (1/1) | **no, none, no, no (0/1)** | 4 → 5 | full evidence, first gold rank, stacked digest |
| **Q10** | no, 25, no, no (1/2) | no, none, no, no (0/2) | no, none, no, no (0/2) | **no, 6, yes, yes (2/2)** | 2 → 2 | in the bundle, full evidence, first gold rank, stacked digest |
| **Q11** | yes, 4, yes, no (1/2) | yes, 4, yes, no (1/2) | yes, 4, yes, no (1/2) | **yes, 4, yes, yes (2/2)** | 2 → 3 | full evidence, stacked digest |
| Q12 | yes, 2, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | 2 → 2 | stacked digest |
| Q13 | no, 6, yes, no (1/2) | yes, 1, yes, no (1/2) | yes, 1, yes, no (1/2) | yes, 1, yes, no (1/2) | 2 → 2 | stacked digest |
| Q14 | no, 16, yes, no (7/9) | no, 17, yes, no (4/9) | no, 17, yes, no (4/9) | no, 16, yes, no (3/9) | 5 → 5 | first gold rank, stacked digest |
| Q15 | yes, 4, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | 2 → 2 | stacked digest |
| Q16 | no, 7, yes, yes (1/1) | no, none, no, no (0/1) | no, none, no, no (0/1) | no, none, no, no (0/1) | 2 → 6 | stacked digest |
| **Q17** | no, 21, no, no (1/2) | yes, 2, yes, no (1/2) | yes, 2, yes, no (1/2) | **no, 21, no, no (1/2)** | 2 → 5 | hit@5, in the bundle, first gold rank, stacked digest |
| Q18 | no, none, no, no (0/2) | no, none, no, no (0/2) | no, none, no, no (0/2) | no, 61, no, no (1/2) | 2 → 5 | first gold rank, stacked digest |
| Q19 | no, none, no, no (0/1) | no, none, no, no (0/1) | no, none, no, no (0/1) | no, none, no, no (0/1) | 2 → 5 | stacked digest |
| Q20 | no, 21, no, no (1/2) | yes, 2, yes, no (1/2) | yes, 2, yes, no (1/2) | yes, 2, yes, no (1/2) | 2 → 2 | same |

**The control against W2-86's head with tree code** (each tree answered by its own code; the trees differ, `338c14fa6475` and `7ca16b19df3f`): the same totals (11, 11 and 15 of 20) and the same cells, but Q08's first gold rank (11 there, 10 here). Calls are the same in both for every question.

**What changed, control to head:** hit@5, in the bundle or full evidence differ for 4 questions: Q09 (full evidence), Q10 (in the bundle and full evidence), Q11 (full evidence) and Q17 (hit@5 and in the bundle). Q08, Q14 and Q18 keep those three but their ranks or pieces moved. The stacked digest differs for 17 of 20; it is the same only for Q03, Q05 and Q20. Pieces found moved for Q10 (0 → 2 of 2), Q11 (1 → 2 of 2), Q09 (1 → 0 of 1), Q14 (4 → 3 of 9) and Q18 (0 → 1 of 2).

## 6. The graph and code-graph questions

**How the routes were read.** The records hold, per question, the five compared fields, the pieces and the number of calls; they hold no item, no route and no facet. So what each route did is read from the head code's own rules applied to the questions' text, read-only: `graph_route._named`, `W2_ID`, `_wbs_ids` and `_title` against the head store's `records` and `register_entries` (the store opened immutable), and `code_route._CODE_SHAPED`, `_WORD` and `_defined`'s pattern against the 150 code files of the head store (`/tmp/gov-os-lead-W2-92/eng4/routes.py`). Neither route was run and no question was retrieved. Whether the code-graph tool holds a symbol of a taken word (and so whether the route gives spans) is not shown; where the calls or the digest say something about it, it is given.

**The record route** (`graph_route.start_ids`: a record's id, a W2 id resolved to its ticket, or a record's title, found whole in the question) takes four questions:

| Q | What it names | Already a start id at the control? | Head against control |
|---|---|---|---|
| Q01 | `DEC-782`, by id | no: the question has no `ticket` or `ids`, so the record closure of DEC-782 is a new route at the head | hit@5 yes → yes and full evidence 1 → 1 of 1 (rank 1 both); the stacked digest moved, calls 5 → 5 |
| Q06 | W2 id `W2-54` → `DAEO-0rfi` | yes (`--ticket DAEO-0rfi`): the route adds nothing new | hit@5 no → no (rank 7 both) and full evidence 2 → 2 of 2; the digest moved (the code route takes words too, below) |
| Q07 | the title of `DAEO-0mab` (the Track A gate run), found whole | yes (`--ticket DAEO-0mab`): nothing new | hit@5 no → no (rank 6 both) and full evidence 1 → 1 of 1; the digest moved |
| Q14 | W2 id `W2-03` → `DAEO-ym8a` | yes (`--ticket DAEO-ym8a`, radius 1): nothing new | hit@5 no → no (rank 17 → 16) and full evidence no → no (4 → 3 of 9) |

So on this set the record route gives a new start only for Q01, whose figures were already at their best. The other three questions the set already asks with `--ticket`; the route finds the same ticket and adds nothing. None of the four moved on the record route's account.

**The code route** (`code_route.route`: a word shaped as code, or a plain word that a code file of the store, no test, defines with `def` or `class`) takes a word in 15 of the 20 questions. It takes none in Q01, Q03, Q13, Q15 and Q20.

| Q | Words the head code's rule takes | Calls | Head against control |
|---|---|---|---|
| Q02 | `command`, `read`, `write` (plain) | 2 → 5 | hit@5 yes → yes (rank 1) and full evidence 1 → 1 of 1 |
| Q04 | `context` (plain; `gov.context.context`) | 2 → 3 | hit@5 yes → yes (rank 1) and full evidence 1 → 1 of 1 |
| Q05 | `and` (plain; matched by a docstring line of `src/gov/cli/main.py`, line 5, that begins with the word "class") | 2 → 2 | hit@5 yes → yes (rank 1) and full evidence 1 → 1 of 1, with the stacked digest the same: the route added nothing (no function of that name exists) |
| Q06 | `allowed`, `and`, `sources` (plain) | 3 → 3 | hit@5 no → no (rank 7) and full evidence 2 → 2 of 2 |
| Q07 | `gate`, `run`, `tickets` (plain; `run` is defined in 24 files) | 5 → 5 | hit@5 no → no (rank 6) and full evidence 1 → 1 of 1 |
| Q08 | `commit`, `index` (plain) | 2 → 3 | hit@5 no → no, rank 10 → 8 (up), and full evidence 1 → 1 of 1 |
| Q09 | `context` (plain) | 4 → 5 | hit@5 no → no, rank 44 → none, and full evidence 1 → 0 of 1 (lost) |
| Q10 | `indexable` (plain; `gov.secrets.indexable`), as well as `--id indexable` | 2 → 2 | hit@5 no → no, rank none → 6, in the bundle no → yes, and full evidence 0 → 2 of 2 (gained) |
| Q11 | `rrf` (plain; `gov.retrieval.fusion.rrf`), as well as `--id rrf` | 2 → 3 | hit@5 yes → yes (rank 4), and full evidence 1 → 2 of 2 (gained) |
| Q12 | `CONTINUATION_INVALID` (shaped: an underscore inside) | 2 → 2 | hit@5 yes → yes (rank 1) and full evidence 1 → 1 of 1; the digest moved |
| Q14 | `tickets` (plain; `docs/plan/tools/validate_w2.py`) | 5 → 5 | hit@5 no → no, rank 17 → 16, and full evidence no → no (4 → 3 of 9) |
| Q16 | `gate`, `run` (plain) | 2 → 6 | hit@5 no → no and full evidence 0 → 0 of 1 (no gold ranked) |
| Q17 | `embedded`, `search` (plain; `search` is defined in `fusion.py`, `lexical.py` and `semantic.py`; `embedded` is a function nested in `semantic._wanted`) | 2 → 5 | hit@5 yes → no, rank 2 → 21, in the bundle yes → no, and full evidence no → no (1 of 2 both) |
| Q18 | `PreCompact` (shaped: a capital inside), `hook`, `write` (plain) | 2 → 5 | hit@5 no → no, rank none → 61, and full evidence no → no (0 → 1 of 2) |
| Q19 | `tests`, `write` (plain) | 2 → 5 | hit@5 no → no and full evidence 0 → 0 of 1 (no gold ranked) |

**Why each moved, as far as the records show:**

- **Q10 and Q11 (the callers' questions) moved up.** Both gold pieces of each are the calling lines. The code route asks the tool for the callers of the named function and gives each caller's whole span; in the head tree `indexable` is called inside the lexical index's function (`lexical.py`, line 123 at the head) and inside `gov.codeintel.index` (`codeintel/__init__.py`, line 188), and `rrf` inside `fusion.search` (line 62) and `retrieve.retrieve` (line 147). Each caller's span covers its calling line, which matches the two gold pieces. At the control the `--id` options found nothing (neither name is a record id). So Q10 went from no piece to both, its first one at rank 6, in the bundle, and Q11 gained its second piece; Q10's hit@5 is still no (rank 6), with full evidence yes, and Q11's hit@5 stays yes, with full evidence now yes. The records show the pieces, not the items; that the callers' spans are what matched is what the code and the gold lines show.
- **Q17 moved down** (hit@5 yes → no and full evidence no → no, 1 of 2 both; rank 2 → 21; out of the bundle). The question's plain words `search` and `embedded` are function names, so the code route took them: the three `search` functions, `embedded` if the tool holds the nested function, and their callers and callees joined the fusion as a fourth route. The first call then held no gold item; the first came at rank 21. The records do not show which items now rank above it, or which of the two pieces is the one found, so that the code route's hits pushed it down is the likely cause, not a shown one. Calls went 2 → 5.
- **Q09 lost its evidence** (hit@5 no → no and full evidence 1 → 0 of 1; rank 44 → none). The question's plain word `context` names `gov.context.context`, so the code route added that function and its callers and callees. At the control the one gold piece (the ticket's KPIs) came late, at rank 44 over 4 calls; at the head it is not in the stacked context of 5 calls, which ends at the stack budget. The records do not show what filled the stack ahead of it.
- **Q08 moved up two ranks** (10 → 8; hit@5 no → no and full evidence 1 → 1 of 1). The code route took `commit` and `index`; neither names the gold (a ticket and the WBS). The records do not show why the gold rose.
- **Q14 moved up one rank and lost a piece** (rank 17 → 16; hit@5 no → no and full evidence no → no, 4 → 3 of 9). The record route added nothing (the ticket was already given); the code route took `tickets`. Both runs stopped at 5 calls with the stack budget reached, so items the code route added may have taken the stack's room; the records do not show which piece was lost or why.
- **Q18 found a piece** (0 → 1 of 2, rank 61; hit@5 no → no and full evidence no → no). The code route took `write`, which names `gov.checkpoint.record.write`; the PreCompact hook's `main` (`template/governance/kernel/hooks/precompact.py`) imports it as `_rec_write` and calls it at line 112, the gold line of the second piece. If the tool holds that call, the hook's `main` is among `write`'s callers and its span covers line 112. The record does not name the piece found, so this is the likely one, not a shown one.
- **Unchanged figures with a moved digest** (Q01, Q02, Q04, Q06, Q07, Q12, Q13, Q15, Q16, Q19): items entered or moved in the stacked context, none of them changing a figure. For Q13 and Q15 neither route takes a word, so their moved digests come from the tree and its stores (the head holds the ticket's three code files and tests, and `retrieve.py`, Q13's gold file, changed); the records do not show which items.

## 7. Deviations and what they mean

1. **The retriever is each clone's own code, not the pinned gov** that W2-61's §8 names. The change is code, so the pinned gov would not measure it.
   - **What it means:** the pair head against control is like for like. W2-61's baseline (pinned gov) is not; W2-86's supplementary head with tree code is the nearest earlier figure, and the control equals it but for one rank (§5).
2. **The head rebuild's first try exited 69** (`rebuild-head-try1.exit`, 15:07). Only its exit code was kept; the records do not say why. The reported head rebuild is the second try, from 15:08:36, exit 0.
   - **What it means:** the stores measured are the second try's, whose digest and hashes are in §2.
3. **One run each, no repeat:** W2-61's §8 step 4 (a repeat on the same index and after a rebuild) was not run. The only check of stability is the control's agreement with W2-86's tree-code head, on a different tree (§5).
4. **The disk gate's readings and the load were not logged,** so they are not given here; the base rebuild waited 35 minutes on the shared lock (12:39:37 to 13:14:37) and ran to its end.
5. **The routes' work is read from their rules, not from the records** (§6): the measure keeps no items or facets, so "the likely cause" is said where the records do not show one.

## 8. Scope

The visible half only. W2-61h's enlarged set (its graph and code-graph categories) is not yet in, so the hidden half and the new categories are not measured here. On this set only Q10 and Q11 are callers' questions and only Q01, Q06, Q07 and Q14 name a record, so this measure says little about how the two routes do on the questions they were built for.

## 9. How to repeat it

W2-61's §8, with these changes:

1. **Three clones by exact path,** each `git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS <path>`, detached: `/home/usain/gov-os-runs/W2-92/base` at `7ca16b19df3f`, `/home/usain/gov-os-runs/W2-92/head` at `fb0c8c430171` (fetched from `w2/W2-92`), and `/home/usain/gov-os-runs/W2-92/measure` at `c38a5b49bc86`.
2. **Two retrievers,** the pinned launcher's body under a first line `#!/usr/bin/env -S PYTHONPATH=<clone>/src /usr/bin/python3`: `gov-base` and `gov-head` (§1).
3. **The stores,** in each clone by its own retriever, with embeddings, after the disk gate: `env -u GOV_TICKET flock /tmp/gov-os-rebuild.lock <gov-base|gov-head> rebuild --json` (`/tmp/gov-os-lead-W2-92/bin/rebuild-base.sh`, `rebuild-head.sh <commit>`). Record its `digest` and the sha256 of `.gov-runtime/store.db`, `.gov-runtime/codeintel/home/code.db` and `.gov-runtime/codeintel/home/_config.db`.
4. **The measure,** first the control, then the head with `--compare` the control's record (`measure-base.sh`, `measure-head.sh`):

   ```
   env -u GOV_TICKET PYTHONPATH=/home/usain/gov-os-runs/W2-92/measure/src python3 -m gov.retrieval.measure memory-retrieval \
     --root /home/usain/gov-os-runs/W2-92/<base|head> --sets-root /home/usain/gov-os-runs/W2-92/measure --part visible \
     --gov /tmp/gov-os-lead-W2-92/bin/gov-<base|head> --out /home/usain/gov-os-runs/W2-92/records --json \
     [--compare <the control's record>]
   ```

   The budgets are the measure's defaults: `--batch-size 10 --bundle-budget 6000 --stack-budget 24000`.
5. **The routes' reading** (§6): apply `graph_route`'s and `code_route`'s word rules to the questions' text against the head store opened immutable; run no route and retrieve no question.
6. **Never `--part hidden`.**
