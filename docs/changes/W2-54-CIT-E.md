---
id: W2-54-CIT-E
type: change-execution-record
status: APPLIED
date: 2026-10-18
branch: w2/W2-54
base: b644d28a
ticket: DAEO-0rfi (W2-54)
author: engineer (W2-54)
decisions_recorded: [DEC-768]
state_class: EVIDENCE
---

# W2-54: change-execution record (CIT-E)

This records the changes of W2-54 (DAEO-0rfi) under DEC-768, which approves the two kernel files below under CAP-33:
the `timeout-seconds` line of `template/governance/kernel/checks/context-reproducibility.yaml` and the new
`template/governance/kernel/schemas/audit-report.schema.json`. No other line of a kernel file is changed, and no
hard-block check is skipped, downgraded or excluded (DEC-768 item 4).

## 1. The changes

| # | File | Change | Evidence |
|---|---|---|---|
| 1 | `src/gov/context/__init__.py` | The packet's `dropped` list is sorted by `(id, reason)` before the packet is hashed. An entry holds exactly these two fields, so the key decides every pair of entries that differ; equal entries are equal whatever their order. What is kept in `supplementary` is still chosen in the retrieval's rank order, as before: the sort changes no item the packet holds, only the order of `dropped`. | `tests/unit/context/test_dropped_order.py` (5 cases); acceptance `tests/acceptance/W2-54/test_w2_54_dropped_order.py` |
| 2 | `template/governance/kernel/schemas/audit-report.schema.json` (new) | W2-02's file byte for byte, written from `git show 2a35fd7b:template/governance/kernel/schemas/audit-report.schema.json` (DEC-441's form: `milestone`, `commit`, `pack_sha256`). | `cmp` against that output: same |
| 3 | `src/gov/check/schema.py` | W2-02's lines for the `audit-report` type only: its `SCHEMA_MAP` entry, `STANDALONE_TYPES = ("probe", "audit-report")`, the audit-report folder `docs/audit` (`AUDIT_REPORT_DIR, AUDIT_REPORT_TYPE`) and the reading of a record there that states no `type` as an audit report. Nothing of `close` or `adoption-verdict`, and none of W2-02's other changes to the file. | `tests/unit/check/test_schema_audit_report.py` (10 cases); `python3 -m gov.check.schema` here exits 0 with `docs/audit/wave-1/W1-43-wave-1-exit-audit.md` untouched (sha256 `b14e17d6e71b2727c3cea123dec112fdccbeb27afc1f50b67f5e27294ecdac1d`) |
| 4 | `template/governance/kernel/checks/context-reproducibility.yaml` | One line added, `timeout-seconds: 600`; nothing else changed. | §2 |

## 2. The measurement and the declared limit

**Before** (the lead, in this worktree at `b644d28a`, fresh store): 128 seconds wall clock, a 1-minute load of
about 1.5 at the start on 20 processors; the check failed on 13 tickets (`FAIL: <ticket>: h1 != h2`). The
acceptance README records 164 seconds at a 1-minute load of 29 to 15 on 20 processors for the same commit.

**After** (this engineer), on the commit `4f753c72` (the code changes 1 to 3), after the full rebuild
`PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m gov.cli.main rebuild --json` (store digest
`6e3fda15127395fbeab00de11c665adf0c1c677d4b394ba48635ad9b01847e46`; lexical, semantic and codeintel recreated):

    uptime; nproc; /usr/bin/time -v env PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m gov.context.context_check; uptime

| Measure | Value |
|---|---|
| Wall clock | 130.07 seconds (2:10.07); user 75.39 s, system 20.22 s, 73% of one processor |
| Tickets measured | 106: the records of `.tickets/` the store holds, counted with `gov.context.context_check.project_tickets` (106 held, 0 unheld), the same as the 106 files `.tickets/*.md`; each computed twice, 212 context computations |
| Load before (1, 5, 15 minutes) | 26.97, 23.85, 22.49 |
| Load after | 8.47, 17.76, 20.42 |
| Processors | 20 |
| Maximum resident set | 80,888 kB |
| Exit | 1: 14 tickets failed (see §3) |

The run's time does not depend on whether it is green: every ticket's context is computed twice either way.

**Why 600 seconds.** The runner runs the checks one after another (`src/gov/check/runner.py`), so the check is
timed alone under whatever load the machine carries. The measured runs are 128 seconds (quiet), 130 seconds (load
27 to 8) and 164 seconds (load 29 to 15). 600 is 4.6 times this run and 3.7 times the loaded one, and the run grows
with the number of tickets (106 today, about 1.2 seconds a ticket), so the margin also covers the tickets of the
waves ahead. It is what the sibling G1 check over the same store, `retrieval-regression`, declares, and it stays
within the bound the acceptance README sets (above the runner's 60 seconds, DEC-595 and DEC-600; at most 600).
**It still catches a hang:** a check that runs past 600 seconds is stopped and RED, as before; nothing in the
runner is changed.

## 3. Finding: the check stays red here, for a reason outside this ticket's paths

After change 1, the run in §2 still failed on 14 tickets (`DAEO-0pyc`, `DAEO-1ve2`, `DAEO-32n6`, `DAEO-7nne`,
`DAEO-csj8`, `DAEO-ipqy`, `DAEO-jip3`, `DAEO-lrre`, `DAEO-nn1s`, `DAEO-o4fg`, `DAEO-sdxk`, `DAEO-xnbx`, `DAEO-xog0`,
`DAEO-zqvn`). The two computations do not hold the same items in two orders: they hold **different items**. For
`DAEO-0pyc`, one computation drops the chunk `9c72b932910f9822b3f7e8d6` where the other drops `CAP-18`.

Traced through the retrieval's routes (two computations of one ticket in one process): the lexical route and the
closure give the same hits; the **semantic route gives a different list** (other order, often another set of its
30 nearest chunks), so the fused scores shift and the retrieval's 20-slot cut takes a different 20th item. The
cause is the embedder: Ollama's vector for the same query text differs with the request that came before it (six
requests of one query in a row gave one vector; the same query after another query gave another, the components
differing by up to 3.9e-3). The check computes a ticket's context right after the previous ticket's, so its first
computation follows another query and its second follows its own.

So these 14 contexts really differ between two computations, and the check is right to fail them (failure line 1).
Nothing in `src/gov/context/` can make the retrieval return the same items without changing what the packet holds
or weakening the check; the fix belongs to the semantic route (`src/gov/retrieval/semantic.py`), outside this
ticket's `allowed_paths`. It is returned to the lead as a decision package.

## 4. Round 2: one query vector per text (owner, 2026-10-18, P-W2-30 (a))

*Round 3 changes parts of this section (the file's name, the key, how the vector is computed and why the stored one
is used); §5.4 lists each correction. The text below is round 2's, kept as it was.*

The owner widened the ticket for one more round (DEC-773, owner, 2026-10-18, staged for the owner's commit; the
ticket cites it as "owner, 2026-10-18, P-W2-30 (a)"), adding `src/gov/retrieval/semantic.py` and
`tests/unit/retrieval/**` to its paths. DEC-768's premise (the two computations differ only in the order of
`dropped`) is corrected by §3's finding; the stable sort of `dropped` (change 1) stays. The change is made under
CAP-33: evidence (§3 and §4.2), the owner's approval (DEC-773), tests first (`test_w2_54_query_vector.py`, 15 cases,
written by an independent test designer before this round's code), one review.

### 4.1 The cause

§3: the semantic route's vector for a question differs with the request the embedder answered just before it, so
two computations of one ticket's context, the first right after another ticket's and the second right after its
own, hold different nearest chunks and so different items (14 tickets red at `4f753c72`; components differing by
up to 3.9e-3 in that round's trace). The orchestrator reproduced it: the first embedding of "context" after another
text differed from its repeats by up to 0.001948 in a component.

### 4.2 The measurement, before the change: no embedder setting removes the variation

On this machine's Ollama (version 0.35.0, `qwen3-embedding:0.6b`, digest
`ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`, Q8_0; `/api/ps` reports `size_vram` equal to
`size`, the whole model in the GPU's memory; 20 processors), at `4844e124`, before any code change, through
`/api/embed` exactly as `semantic.py` sends a question (one request, `input: [INSTRUCTION + text]`) with the
setting's `options`.

**The protocol**, for each setting and each of two texts (`context`, and `The context packet's dropped list in a
stable order`): 6 runs; run *i* embeds a preceding text (cycling over three different ones: `who reads the harbour
tide tables`, `when are the pear trees pruned`, `the audit-report type exactly as W2-02 defines it`), then the text
once (the first embedding after another text), then the text 3 more times (its repeats). A warm-up request with the
setting's options comes first, since new options may reload the runner. Reported: the largest component difference
between the first embedding and its repeats, the largest between the repeats, and how many runs differed at all.

**The script** (`.gov-runtime/scratch/w2_54_embed_variation.py`, never committed; its core):

    def embed(text, options):
        body = {"model": MODEL, "input": [INSTRUCTION + text]}
        if options is not None:
            body["options"] = options
        ...  # POST http://127.0.0.1:11434/api/embed, no proxy; ["embeddings"][0]

    for run in range(6):
        embed(PRECEDING[run % 3], options)
        first = embed(target, options)
        repeats = [embed(target, options) for _ in range(3)]
        f = max(max(abs(x - y) for x, y in zip(first, r)) for r in repeats)
        r = max(max(abs(x - y) for x, y in zip(repeats[0], x2)) for x2 in repeats[1:])

**The command:** `uptime && time python3 .gov-runtime/scratch/w2_54_embed_variation.py && uptime` in the worktree
(11.5 seconds; load 2.28, 6.25, 11.98 before and 2.46, 6.16, 11.89 after).

**The figures** (raw, one line per setting and text; every run of a line gave the same two figures):

| Setting (`options`) | Text | Runs | Runs that differed | Largest first vs repeats | Largest between repeats |
|---|---|---|---|---|---|
| default (none) | `context` | 6 | 6 | 0.002887 | 0.000000 |
| default (none) | `The context packet's …` | 6 | 6 | 0.003281 | 0.000000 |
| `num_thread: 1` | `context` | 6 | 6 | 0.002887 | 0.000000 |
| `num_thread: 1` | `The context packet's …` | 6 | 6 | 0.003281 | 0.000000 |
| `num_thread: 20` (the processors) | `context` | 6 | 6 | 0.002887 | 0.000000 |
| `num_thread: 20` (the processors) | `The context packet's …` | 6 | 6 | 0.003281 | 0.000000 |
| `seed: 42` | `context` | 6 | 6 | 0.002887 | 0.000000 |
| `seed: 42` | `The context packet's …` | 6 | 6 | 0.003281 | 0.000000 |
| `num_thread: 1, seed: 42` | `context` | 6 | 6 | 0.002887 | 0.000000 |
| `num_thread: 1, seed: 42` | `The context packet's …` | 6 | 6 | 0.003281 | 0.000000 |

**The result:** no setting removes the variation, or changes it at all. In every run of every setting, the first
embedding of a text after a different text differs from its repeats, by the same amount whichever text came before;
the repeats are identical to each other. So a text has two vectors, one after any other text and one after itself.
(This fits the runner reusing the computed state of the prompt the previous request shares with it: the instruction
is a prefix every question shares. That is a reading of the figures, not measured here. With the model wholly in the
GPU's memory, a thread count is not expected to change the arithmetic, and an embedding samples nothing for a seed to
fix.) Ollama is shared by the sessions beside this one, so another session's request can also come "before" a
search: the variation is not a matter of one process's order alone. As DEC-773 says, the stored vectors are used
whatever this shows.

### 4.3 The change

| # | File | Change | Evidence |
|---|---|---|---|
| 5 | `src/gov/retrieval/semantic.py` | A question's vector is stored, keyed by the model (`MODEL`), **the digest Ollama's model list (`/api/tags`) reports at the time of the search** (DEC-374; not the index's revision, so a vector made by one build of the model is never another build's) and **the exact text sent** (the instruction and the question, as given: no case folding, no whitespace or Unicode normalisation, no stripping). A stored vector is used whenever its key matches, and only then. The first answer for a text is the embedder's vector, and the vector stored is those same bytes (the float32 BLOB the search compared with). A failed or partial embedding call stores nothing (the facet stays unavailable with no hit); without a digest in the model list there is no key, and the embedder's vector is used without storing. Concurrent searches: `INSERT OR IGNORE` on the key, then the stored row is read back and used, so when two processes compute one key the first write wins and every later search uses it; a write that loses gives the winner's vector, and one that fails (locked past 30 seconds, an unwritable folder) raises nothing and gives the stored vector if one can be read, else the embedder's. | `tests/unit/retrieval/test_semantic_query_vector.py` (11 cases); acceptance `tests/acceptance/W2-54/test_w2_54_query_vector.py` (15 cases, all green at `e8255c8a`, the real-embedder case included) |

**Where the vectors are kept:** `<root>/.gov-runtime/query-vectors.db` (`QUERY_VECTORS_REL`), a SQLite file of its
own, beside the store and not in it: one table `query_vector (model, revision, text, embedding)`, the key the
primary key. It is in the project's own runtime folder (ignored by git), so it is never under `HOME`, never shared
between projects or worktrees, and never in another project's store. It is written only once the vectors can be
answered from: a search that finds the lexical or semantic index missing, empty or stale returns before it and
writes nothing at all (W1-19's `test_a_search_that_may_not_write_reports_a_missing_index_and_writes_nothing` stays
green). **Why a file apart:** a vector kept in `store.db` would make every `gov context` and every context check, in
any role's session, a writer of the live store. Apart from it, storing a query vector changes nothing the store
holds: not the lexical or semantic index, not their freshness or status (computed from `store.db` and the tracked
files; the file is untracked), not the record graph, and not the store digest `gov rebuild` reports (computed over
the graph's tables in `store.db` alone). The facet's unavailable states (no `sqlite_vec`, no Ollama, no model, a
missing, empty or stale index) are unchanged, and no check is touched (DEC-768 item 4).

**DEC-379 and DEC-322 beside it** (returned by the lead to the owner as a text question; it does not stop this
work): DEC-322 says only orchestrator-role sessions write the live `.gov-runtime/store.db`; with the vectors in a file
of their own, `store.db` is still written only by the sessions that wrote it before, so DEC-322's words hold as
written. DEC-379 says "`refresh=False` never writes"; a `refresh=False` search now writes `query-vectors.db` (once
per new key) though it never writes the store. Read as "never writes the store or its indexes", DEC-379 holds; read
literally, the new line (DEC-773, "query vectors are stored") and DEC-379 differ, and `semantic.py`'s module text now
says "never write it [the store]". A sentence in DEC-379 (or DEC-773) naming the query-vector file as the one write a
`refresh=False` search makes would close the gap.

### 4.4 The context check after the change: green, and the declared limit still fits

On the commit `db9830d7` (change 5 and this record's §4.1 to §4.3), after the full rebuild
`PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m gov.cli.main rebuild --json` (store digest
`c1a9f0cc637049429d4bfb07d4dfb6c75208fed5bdd6b9d2c0d89e89e36aa8f7`; lexical, semantic and codeintel recreated; the
lexical index `fresh` and the semantic vectors answerable), with no `query-vectors.db` in the runtime folder before
the run (the first computation of every ticket's context embedded its question; the second used the stored vector):

    uptime; nproc; /usr/bin/time -v env PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m gov.context.context_check; uptime

| Measure | Value |
|---|---|
| Wall clock | 128.67 seconds (2:08.67); user 75.70 s, system 19.34 s, 73% of one processor |
| Tickets measured | 106 (`project_tickets`: 106 held, 0 unheld; 106 files `.tickets/*.md`), each computed twice |
| Load before (1, 5, 15 minutes) | 26.68, 18.15, 14.94 |
| Load after | 7.81, 13.85, 13.75 |
| Processors | 20 |
| Maximum resident set | 81,324 kB |
| Exit | 0: `context-reproducibility: green` (14 tickets red at `4f753c72`) |
| After the run | `query-vectors.db` holds 67 vectors (67 distinct question texts; one model, one revision `ac6da0df…`); the store digest is still `c1a9f0cc…`, and `store.db` was not written (its time is the rebuild's) |

The run takes the time round 1's did (130.07 seconds): a stored vector saves one embedding request and adds one
model-list request per search. **The declared `timeout-seconds: 600` stays**: it is 4.7 times this run.

## 5. Round 3: the query-vector cache, and a vector that does not depend on it (owner, 2026-10-18, P-W2-32 (a))

The owner allowed one more round: DEC-782 (owner, 2026-10-18, P-W2-32 (a); staged for the owner's commit, cited by
the ticket as "owner, 2026-10-18, P-W2-32 (a)") amends DEC-379 for one file only: a read command (`gov retrieve`,
`gov context`) may write the query-vector cache, and nothing else, within five limits. The ticket gains success
lines 3 and 4 (the cache; the same vector where it cannot be written) and 5 (W1-46's environment, DEC-784, a test
rewrite, no code here). The change is made under CAP-33 and DEC-768: evidence (round 2's verification, §5.1),
the owner's approval (DEC-782), tests first (`test_w2_54_query_cache.py` and `test_w2_54_sandboxed_worker.py`, 15
cases, 12 red at `3bee9a50`, written by an independent test designer before this round's code), one review. No
hard-block check is skipped, downgraded or excluded (DEC-768 item 4).

### 5.1 The cause

- **Round 2's five reds.** Round 2's code stores a question's vector at query time, so a read writes a file; five W1
  cases that held "a read writes nothing" turned red (W1-19's
  `test_the_vectors_are_in_the_shared_store_beside_the_lexical_index`; W1-21's
  `test_a_retrieval_writes_nothing[a question, a ticket, batches of one]` and `test_the_command_writes_nothing`).
  DEC-782 decides it: that one derived file may be written, and the W1 cases are rewritten to it (their READMEs'
  "Rewrite (W2-54, DEC-782, 2026-10-18)" sections).
- **The determinism finding.** In round 2 the vector a text got still depended on what was embedded before it; the
  cache only froze the first one. Where the cache cannot be written (a sandboxed worker, whose `.gov-runtime/` is
  read-only), every read embedded afresh and got whichever vector the request before it produced; a cold, a deleted
  or a full cache gave another text's drift; and six processes on a cold cache gave answers that depended on their
  interleaving (the acceptance README's round-3 table, 12 red). DEC-782: the computation itself must be
  deterministic, and the cache only saves time.

### 5.2 How the vector is the same without the cache

*Corrected after the lead's measurement at `b33ef9b3` (§5.5): the request shape below does not make the computation
deterministic on the real embedder. What holds now: the question's request names `options: {"num_gpu": 0}`
(`QUERY_OPTIONS`), so the question is embedded on the CPU, where its vector is one vector whatever was embedded before
it, by this process or another, whatever the request's shape (§5.5.2); the request is still
`[INSTRUCTION, INSTRUCTION + question]` and the second vector is used. The paragraph that follows is the first change
of round 3, kept as it was; its premise ("a request's inputs in order", "one vector whichever text came before") is
refuted by §5.5.1, items 1 to 3.*

`semantic.query_vector(root, question)` (now public; `search` calls it) sends **one request**,
`input: [INSTRUCTION, INSTRUCTION + question]`: the bare instruction, then the question with it, and uses **the
second vector**. Within that request the question always follows the same text, so its vector no longer depends on
the request that came before it, from this process or another. A computation split over two requests (the text, then
the text again) could be split by another process's request; one request cannot be split by a client of an embedder
that serves a request's inputs in order (the stand-in does; the real embedder is measured in §5.5). By §4.2, the real
embedder's vector for a text after any different instruction-prefixed text is one vector whichever text came before,
so the question after the bare instruction is expected to get that vector; §5.5 measures it, with a chunk without the
instruction, other questions and the question itself before the read. The cost: one short extra input per read that
the cache does not answer.

The cached vector is used whenever its key matches (it saves the request); since it is the vector the computation
gives, a cold, warm, deleted, full or unwritable cache gives the same bytes. Why not "the text twice, the repeat
used": the round-2 case `test_a_question_asked_for_the_first_time_gets_the_vector_the_embedder_returns_for_it`
holds that a question asked for the first time is sent to the embedder once; the bare instruction is not the question.

### 5.3 The five limits as built

| Limit (DEC-782) | As built in `src/gov/retrieval/semantic.py` |
|---|---|
| 1. One derived file under `.gov-runtime/`, nothing authoritative | `.gov-runtime/query-vector-cache.db` (`QUERY_VECTORS_REL`), a SQLite file of its own: not `store.db`, not tracked (the runtime folder is ignored by git), read by no check and outside the store digest. Rollback-journal mode, never WAL, so no `-wal` or `-shm` file stays beside it; the journal exists only during a write and is removed at its commit or rollback. Nothing is written when the lexical or semantic index is missing, empty or stale (the search returns before the vector is asked for), as round 2. |
| 2. Keyed by model, model revision and a hash of the exact text | Table `query_vector (model, revision, text_sha256, embedding)`, the three first the primary key: `MODEL`; the digest Ollama's model list reports at the time of the search (DEC-374, as round 2); the sha256 (hex) of the exact text sent, `INSTRUCTION + question` in UTF-8, with no case folding, no whitespace or Unicode normalisation and no stripping. The text is kept nowhere. Without a digest in the model list there is no key, and nothing is cached. |
| 3. Atomic, safe with several sessions at once | One `BEGIN IMMEDIATE` transaction per entry, `INSERT OR IGNORE` on the key, a busy timeout of 30 seconds; a read opens the file `mode=ro`. A transaction is all or nothing, so no entry is torn; concurrent writers of one key keep one entry, which is the same bytes either way. The locks are the operating system's advisory locks on the file, released when a process ends: none is left behind. Any SQLite error (a file or folder that cannot be read, written or created, a file that is not a database, a lock held past the timeout) is swallowed: the read uses the vector it computed, and its answer is the same. A failed or partial embedding call caches nothing, as round 2. |
| 4. Bounded in size | The setting `GOV_QUERY_VECTOR_CACHE_MAX_BYTES` bounds the file in bytes; its default is 67108864 bytes (64 MiB, `CACHE_BOUND`); a value that is not a whole number gives the default. |
| 5. Rebuildable from nothing | The file is derived: deleting it changes no answer (§5.2); the next reads fill it again. |

**What happens at the bound.** The size is checked inside the write's transaction (`page_count × page_size`, the
file's size once it commits). A write that would take the file past the bound is undone; it is then tried once more
in a new transaction that first deletes **the older half of the entries** (by the order they were written), whose
pages SQLite reuses, so the file does not grow; if the entry still does not fit (a bound smaller than one entry), that
is undone too and the entry is not kept. So the file never passes the bound, and it never shrinks (no `VACUUM`).
Reads at the bound are unchanged: an evicted text is computed again, to the same vector. Measured with 1024-number
vectors: about 4,805 bytes an entry (4,804,608 bytes for 1,000 entries), so the default holds about 13,900
questions; the context check over 106 tickets asks 67.

**Round 2's file.** `.gov-runtime/query-vectors.db` (round 2's name, which kept each text in clear) is no longer read
or written. It is derived; where it exists (this worktree's and the main tree's runtime folders, after round 2's
runs), deleting it changes nothing. This engineer wrote neither runtime folder; the lead deletes it.

**The tests.** `tests/unit/retrieval/test_semantic_query_vector.py` (21 cases, regression evidence only): the request
and the vector used; one text, one vector after other texts, in seven cache states (cold, warm, deleted, its folder
unwritable, its file unwritable, no folder, a file that is not a database); a cached vector used without a request;
the key a hash and no text in the file; the exact text; another revision; a failed embedding; no revision; the bound
(never passed, the newest entries kept, the older ones evicted and computed again to the same vector); an entry larger
than the bound; the setting's default; a search without an index writes nothing. Acceptance:
`test_w2_54_query_cache.py` and `test_w2_54_query_vector.py`, 29 cases: 28 green at `77bf7cc7` (the real-embedder
case included, §5.5), the 29th the bound's statement in this record.

### 5.4 Corrections to §4

- §4.3 change 5, "keyed by … the exact text sent": the key is now the sha256 of that text, and the text is kept
  nowhere. "the first write wins and every later search uses it": the vector no longer depends on which write won;
  every computation gives it (§5.2). "one request, `input: [INSTRUCTION + text]`" (§4.2's protocol, round 2's
  search): a search now sends `[INSTRUCTION, INSTRUCTION + text]`.
- §4.3 "Where the vectors are kept": the file is `.gov-runtime/query-vector-cache.db`, the table
  `query_vector (model, revision, text_sha256, embedding)`, bounded (§5.3). The rest holds.
- §4.3 "DEC-379 and DEC-322 beside it": settled by DEC-782 (the one file a read writes). DEC-322 holds as written:
  `store.db` is written by no read.
- §4.4: measured on round 2's code; this round's measurement is §5.5.

### 5.5 Measurement on the real embedder, and round 3's second change

Round 3's first change (§5.2's kept paragraph, `77bf7cc7`, `b33ef9b3`) passed its acceptance tests, but the lead's
measurement on this machine's shared embedder was red. The owner's limits stand (DEC-782, owner, 2026-10-18,
P-W2-32 (a)): the computation itself must be deterministic, and the cache only saves time. This second change is made
under CAP-33 and DEC-768: evidence (§5.5.1, §5.5.2), the owner's approval (DEC-782), the acceptance tests unchanged,
one review. No hard-block check, test or limit of the cache is weakened (DEC-768 item 4).

(The engineer of the first change ran the acceptance case
`test_with_the_real_embedder_one_question_gives_one_answer_whatever_was_asked_before` in a sandbox and it passed at
`77bf7cc7`. That Ollama was one `gov` started inside the sandbox (DEC-261), with this machine's executable and model
folder, not the shared server. §5.5.2 shows why that case passes there whatever the code does.)

#### 5.5.1 The lead's failing measurement at `b33ef9b3` (the shared Ollama, outside the sandbox)

**1. The first change's measurement script** (through `semantic.query_vector`; 6 texts, each read after another
question, after a chunk without the instruction, after the text alone and after a repeated read; cache cold, written
and unwritable). Ollama 0.35.0 at 127.0.0.1:11434; `qwen3-embedding:0.6b` digest
`ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`; bound 67108864 bytes.

| Text | cold: runs / differed / largest | written | unwritable |
|---|---|---|---|
| `context` | 12 / 2 / 0.002887 | 12 / 12 / 0.002887 | 12 / 2 / 0.002887 |
| `The context packet's dropped list in a s…` | 12 / 2 / 0.003281 | 12 / 0 / 0.000000 | 12 / 3 / 0.003281 |
| `who reads the harbour tide tables` | 12 / 1 / 0.002833 | 12 / 0 / 0.000000 | 12 / 2 / 0.002833 |
| `the audit-report type exactly as W2-02 d…` | 12 / 2 / 0.004074 | 12 / 12 / 0.004074 | 12 / 1 / 0.004074 |
| `how is a query vector cached` | 12 / 2 / 0.002609 | 12 / 0 / 0.000000 | 12 / 2 / 0.002466 |
| `café au lait` | 12 / 4 / 0.005548 | 12 / 0 / 0.000000 | 12 / 3 / 0.005548 |

All of the read's vectors: 216 runs, 50 differed from the text's first, the largest component difference 0.005548.
The embedder alone (first after another question against its repeat): 18 runs, 18 differed, the largest 0.004074.
7.3 seconds; the writable cache held 16384 bytes. With the cache cold or unwritable, one text got several vectors.

**2. The lead's probe of request shapes** (`T` = `how is a query vector cached`; 10 runs each, every second run
preceded by another question's request of the same shape; "differed" against run 0):

| Shape | Runs | Differed | Largest |
|---|---|---|---|
| `[I+t]` (round 2) | 10 | 4 | 0.002466 |
| `[I, I+t]`, the second (round 3's first change) | 10 | 8 | 0.002466 |
| `[I+t, I+t]`, the second | 10 | 3 | 0.002466 |
| `[I+t, I+t, I+t]`, the third | 10 | 2 | 0.002466 |
| `[t]`, bare | 10 | 4 | 0.001719 |
| `[X, I+t]`, the second, `X` unrelated | 10 | 1 | 0.002609 |

**3. The lead's probe of what decides the vector** (`[I+T]` alone, right after one request of the text named, three
rounds; the vector's sha256, first 10 characters):

| Vector | Cases that gave it |
|---|---|
| `0ffecdbdfe` | unrelated (shares I) #0, #1, #2 |
| `4332c41b1b` | shares I + `how is a` #0, #1, #2; shares I + `how is a query vector` #0, #1, #2 |
| `5a4fc29484` | shares nothing #0, #1, #2 |
| `d326dafe53` | itself (repeat) #0, #1, #2 |

The lead's reading: the vector is reproducible for a given prefix the text shares with the prompt computed just
before it, and differs between those cases, as if the embedder reused the computed prefix of the previous prompt; the
inputs of one request are not served in a guaranteed order (`[X, I+t]` still differed once in 10, with other sessions
using the shared server at the same time).

**4. The context check at `b33ef9b3`**, after a full rebuild (store digest
`b0d5f5ba40a60fa4a8ca03261d0cb5eb53a84fefc1300da5922229a2e9b61cd9`), the cache cold: `context-reproducibility: green`,
exit 0, 151.45 seconds (2:31.45) against the declared `timeout-seconds: 600` (a quarter of it), every ticket of this
repository, load 36.81 before and 14.84 after, 20 processors. It is green because each context's second computation
reads the vector its first one cached, not because the computation is deterministic.

#### 5.5.2 What this engineer measured

**Where.** Inside this engineer's sandbox (`gov launch`). The shared server is not reachable there (`curl
http://127.0.0.1:11434/api/version` exits 7). Each probe started an Ollama through `gov.retrieval.ollama.ensure_available`
(DEC-261), with this machine's executable (`ollama version is 0.35.0`) and model folder:
`qwen3-embedding:0.6b`, digest `ac6da0df…`. The sandbox blocks the GPU (`nvidia-smi`: "GPU access blocked by the
operating system"), so `/api/ps` reports `size 2371270737, size_vram 0`: the whole model on the **CPU**. On the shared
server `size_vram` equals `size`: the whole model on the GPU (§4.2). There are 20 processors, and the load was 1.7 to
16 during the probes. The probe scripts were throwaway, in the session's temporary folder; the measurement script for
the lead is described below.

| Probe | What | Result |
|---|---|---|
| 1 | `[I+T]` alone (T as in item 3), first in a fresh runner, then after each of 10 predecessors × 3 rounds: a chunk, `x`, `zebra ` × 200 (none shares a prefix), I + a short and I + a long other question, I + `how is a`, I + `how is a query vector`, I + `how is a query vector stored on disk forever`, the text itself, the bare I | **one vector** in 31 of 31 (`ad0ba0b6bb`) |
| 2 | 4 texts; for each, 3 processes × 15 reads (each read after a noise request of another kind), while a 4th process sends default-option requests of 3 inputs (chunk, `I + question`, `I + prefix`) without pause; then the shapes `[I+t]`, `[I, I+t]`, `[N, I+t, N']`, `[I+t, I+t]` × 3 each. All of it once with default options and once with `num_gpu: 0` | **one vector per text** in 60 of 60 reads, for each of the 4 texts and under both options; `num_gpu: 0` gives the default's vector here, since the CPU is the only device |
| 2′ | probe 2 again, the sandbox's daemon started with `OLLAMA_NUM_PARALLEL=4 OLLAMA_FLASH_ATTENTION=1` (gov's `env` argument; the shared server's own settings are not known here) | the same: one vector per text, **the same hashes** as probe 2 |
| 3 | `num_gpu: 0` with `num_thread` 1, 4, 20 and unset | the same 3 vectors for `context`, T and `café au lait` in every case; each change of options reloads the runner (first request 1.05 to 1.11 s) |
| 4 | a fresh daemon, short requests in turn: default, default, `num_gpu: 0`, `num_gpu: 0`, default, `num_gpu: 999`, default, `num_gpu: 0` | 1.093 s (the load), 0.020, **1.130 (reload)**, 0.022, **0.022 (no reload)**, 1.135 (reload), 0.020, 1.122 (reload): an explicit option different from the loaded runner's reloads it; a request without options never does, and is served by whichever runner is loaded |
| 5 | CPU costs | a question `[I, I+t]`: 0.02 to 0.06 s; 96 chunks of 512 characters in batches of 32: 36.63 s (0.38 s a chunk, load 11.2) |
| 6 | the measurement script for the lead (below), run here | one process: 324 reads (6 texts × 3 cache states × 9 kinds of predecessor × 2), **0 differed**; two processes at once with a third client: 96 reads, **0 differed** from the one-process reference; 70.8 s |

**What decides the vector.** The device does. On the CPU, with the same executable, model and digest as the shared
server, a text's vector is the same bytes whatever was embedded before it. That holds for a predecessor that shares
nothing, the instruction, a longer prefix or the whole text, for every request shape, with other processes asking at
the same time, with 1 or 4 parallel slots, with flash attention, and with any thread count. Across separate daemons
it is the same hash (`ad0ba0b6bb` for T in probes 1, 2, 2′ and 6). On the GPU (the shared server, §5.5.1) the vector
depends on the prompt computed just before it. The lead's reading of the mechanism (the runner reuses the computed
prefix of the previous prompt, and the GPU's arithmetic for the tokens left to compute differs from a computation
of the whole text) fits both sets of figures: on the CPU a reused prefix changes no number. It is not measured here,
since no GPU is reachable in this sandbox. **This also means that every embedding run in a sandbox is deterministic
whatever the code does**: the round-3 sandboxed case and the real-embedder case passing there are no evidence about
the GPU. The shared server is the evidence, and the lead runs it (below).

**Why no request shape could do it on the GPU.** A computation on the GPU depends on what the slot computed before
it, and any client's request can come first. A shape that puts a known text first in the same request needs the
inputs served in order on one slot, and item 2 shows they are not. Repeating the text and using the repeat freezes
the prefix as the first of the repeats computed it, after whatever came before. No embed option was found that
turns off the reuse of a computed prefix. Settings that only work at load time (the batch size, the context length)
would reload the shared runner for every client.

#### 5.5.3 The change

| # | File | Change | Evidence |
|---|---|---|---|
| 6 | `src/gov/retrieval/semantic.py` | `QUERY_OPTIONS = {"num_gpu": 0}`. A question's request (`query_vector`) names these options, so the question is embedded with no layer on the GPU. `_embed(texts, options=None)` adds `options` to the body only when given, so the index's chunks are embedded as before, with no options. The request stays `[INSTRUCTION, INSTRUCTION + question]` and uses the second vector. The cache is unchanged: its file, its key (model, revision, sha256 of the exact text), its atomic writes, its bound (`GOV_QUERY_VECTOR_CACHE_MAX_BYTES`, default 67108864 bytes, the older half evicted at the bound), and a cache that cannot be read, written or created is skipped silently. | `tests/unit/retrieval/test_semantic_query_vector.py` (23 cases; 2 new: the request bodies, a question's with `options: {"num_gpu": 0}` and a chunk's with none; and the same request computed again to the same bytes once the cache is deleted and its folder unwritable); acceptance `test_w2_54_query_cache.py` and `test_w2_54_query_vector.py`, 29 of 29 green (in the sandbox) |

**Why the computation is deterministic now.** A question's vector is computed on the CPU, where the vector of a text
depends on the text alone (§5.5.2). Every cache state therefore gives the same bytes: cold, written, full, deleted and
unwritable. A cache that answers saves one request and nothing else (DEC-782). **Why `[INSTRUCTION, INSTRUCTION +
question]` stays:** on the CPU the second vector is the vector of the question alone (the same hash, `ad0ba0b6bb`,
from `[I+T]` in probe 1 and from `query_vector` in probe 6). The acceptance suite's stand-in embedder models an
embedder that serves a request's inputs in order and moves a text's vector toward the one before it. Against that
stand-in this shape is what makes the vector deterministic, and dropping it would turn those cases red. Its cost is
one short extra input per read the cache does not answer.

**Fit for purpose.** The question's vector is still the model's: the same model and digest, the same instruction, the
instruction-prefixed question against chunk vectors made without it (DEC-406), as before. Only the device changes.
The index's vectors are made as before (by whichever runner is loaded). How far a CPU vector lies from a GPU one is
not measured here: no GPU is reachable. W1-21's hit@5 (pass line 80; 81.67 at `5f038b47`) runs on the real models
and the lead runs it.

**The cost on the shared server** (probe 4, Ollama 0.35.0). When the model is loaded on the GPU, the first question's
request reloads it on the CPU (about 1.1 s here). A request without options does not reload, so after that, every
client's default-option request is served by the CPU runner: other sessions' questions, `gov rebuild`'s chunks and
the index builds of other worktrees. This lasts until the model is unloaded after its idle keep-alive, or until a
client asks with explicit options again. In that window a rebuild embeds at the CPU's rate (0.38 s a chunk here, under
load 11). The lead's script prints where the model sits before and after. This is returned to the lead as a decision
(PKG-W2-54-R3-1).

**Vectors cached by the first change.** At `b33ef9b3` the cache file `.gov-runtime/query-vector-cache.db` (this
worktree's, after the lead's runs) holds vectors computed on the GPU, under the same key. Its use is unchanged; it is
derived (DEC-782 limit 5), and **the lead deletes it before measuring**, so that every vector in it is one this
change computed.

**Measurement after the change on the shared embedder (run by the lead):** *to be filled in: the command, the Ollama
version and model placement it prints, the figures (one process, two processes at once), and the context check's
seconds, tickets and load after a full rebuild with the cache deleted, against the declared `timeout-seconds: 600`.*

The command (the script is given to the lead with this engineer's return; it writes only in a temporary folder of
its own):

    PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 <the script>/eng4-measure.py

### 5.6 Round 4: the CPU-only query embedder on its own port (owner, 2026-10-19, P-W2-40 (b))

The lead's measurement after §5.5.3 was red on the shared server, and its package (PKG-W2-54-3) went to the owner.
The owner allowed one more round: DEC-798 (owner, 2026-10-19, P-W2-40 (b); staged, not yet in the register, cited by
the ticket as "owner, 2026-10-19, P-W2-40 (b)") and DEC-797 (delegated). The ticket gains success lines 5 and 6 and
the path `src/gov/retrieval/ollama.py` (the CPU-only embedder only). The change is made under CAP-33 and DEC-768:
evidence (§5.5.1, §5.5.2), the owner's approval (DEC-798), tests first (`test_w2_54_cpu_embedder.py`, 14 cases with
stand-ins, and `test_w2_54_shared_gpu.py`, 2 cases on the shared GPU, written by an independent test designer before
this round's code, `986353cc`, `cd363a8e`), one review. No hard-block check is skipped, downgraded or excluded
(DEC-768 item 4), and no limit of DEC-782 is loosened.

#### 5.6.1 The cause

- **The device decides the vector** (§5.5.1, §5.5.2). On the shared runner, whose model sits wholly on the GPU, a
  text's vector depends on the prompt that runner computed just before it, for any client, and no request shape
  removes it. On the CPU, with the same executable, model and digest, a text's vector is the same bytes whatever came
  before it, whatever the request's shape and whoever else asks at the same time.
- **Why §5.5.3's change no longer holds.** `num_gpu: 0` on a question's request to the shared runner gets the CPU's
  vector, but it moves that runner to the CPU for every client (§5.5.2, probe 4): an explicit option reloads the
  runner, and a request without options is served by whichever runner is loaded. Other sessions' questions,
  `gov rebuild`'s chunks and other worktrees' index builds would then run at the CPU's rate until the model is
  unloaded. **§5.5.3's change 6 (`QUERY_OPTIONS = {"num_gpu": 0}`) is replaced by this round's change**; §5.5 is kept as
  it was, as the record of that round.

#### 5.6.2 The owner's choice (DEC-798, owner, 2026-10-19, P-W2-40 (b))

1. A CPU-only embedder that `gov` starts on its own port answers query embeddings, and only those. The shared GPU
   runner keeps building the index. No request to the shared runner names `num_gpu: 0`.
2. The query-vector cache's key names the device that computed the vector, so a GPU-computed vector (such as those
   `b33ef9b3` cached in this worktree's `.gov-runtime/query-vector-cache.db`) is never served.
3. W1-21's hit@5 is measured again before this ticket merges, by the lead, on the real models, with the CPU query
   vectors against the GPU-built index. A figure below the pass line of 80 is a red for this ticket, not a rewrite.
4. The resource gate counts the CPU embedder's 2.4 GB as standing memory (the orchestrator's; nothing built here).
5. DEC-261 is amended: `gov` starts two daemons on demand and stops neither, the shared one and the CPU-only one on
   its own port.

DEC-797 (delegated): `GOV_QUERY_VECTOR_CACHE_MAX_BYTES` (default 67108864 bytes, 64 MiB) stays the public interface of
the cache's bound, as built in §5.3. DEC-782's limits stand as §5.3 states them, with the key now naming the device.

#### 5.6.3 The change

| # | File | Change | Evidence |
|---|---|---|---|
| 7 | `src/gov/retrieval/ollama.py` | The CPU-only embedder's address and start, nothing else: `query_host()` is the setting `GOV_QUERY_OLLAMA_HOST` (`QUERY_HOST_SETTING`, in `OLLAMA_HOST`'s form), else `127.0.0.1:11435` (`QUERY_DEFAULT_HOST`, the shared runner's default port plus one). `ensure_query_available()` is `ensure_available()` given the caller's environment with `OLLAMA_HOST` set to that address and `CUDA_VISIBLE_DEVICES=-1` (`NO_GPU`, an id that names no device: Ollama's documented way to use no GPU). So the executable is found as DEC-260 finds it (`GOV_OLLAMA_BIN`, `PATH`, `~/.local/ollama/bin/ollama`), started as `ollama serve` in its own session and never stopped (DEC-261 as amended). Two reads that find nothing there at once both start one; the second cannot take the address and ends, and both wait for the first to answer. `ensure_available()` and the shared runner's start are unchanged. | `tests/unit/retrieval/test_semantic_cpu_embedder.py` (the address and its default; the start's environment) |
| 8 | `src/gov/retrieval/semantic.py` | **The question.** `query_vector(root, question)` returns the vector and, when there is none, why. It asks the CPU embedder alone (`_ask`, `_embed` and `_revision` take a host; without one they ask the shared runner at `OLLAMA_HOST`, as before): its model list for the revision, then one request `[INSTRUCTION, INSTRUCTION + question]` (the second vector, as §5.5.3), **with no options**. **After** that request it reads the CPU embedder's `GET /api/ps` (`_on_cpu`): the vector is used only when the pinned model is listed with `size_vram` 0 and `size` above 0. Anything else (the model in GPU memory, partly there, not listed, only another model listed, no listing) gives no vector, the reason `NOT_ON_CPU`, nothing cached, and no request elsewhere. `search` (with or without `refresh`) makes the CPU embedder answer (`_ready(connection, ollama.ensure_query_available)`, starting it if needed) and no longer the shared runner. When the CPU embedder cannot be reached, its facet is unavailable with Ollama's warning as the reason, and the other routes answer. **The chunks.** `_build` (the semantic refresh, `gov rebuild`, a search with `refresh=True`) makes the shared runner answer as before and sends it every chunk, with no options. `QUERY_OPTIONS` is removed, and no request names `num_gpu` or any other option. **The cache.** The same file, `.gov-runtime/query-vector-cache.db`, now the table `device_query_vector (model, revision, device, text_sha256, embedding)`, the four first the primary key: `MODEL`, the digest the CPU embedder's model list reports at the time of the search, `DEVICE` (`cpu`, the only device a vector is used from) and the sha256 of the exact text sent. Round 3's table `query_vector`, keyed without the device, is never read; the first write drops it inside its own transaction, so the file stays one file and its pages are reused under the bound. Writes, bound, eviction and a cache that cannot be read or written are as §5.3 states. | `tests/unit/retrieval/test_semantic_query_vector.py` (23 cases: the question sent to the CPU embedder's address, no option in any request body, a chunk to the shared runner, the key with its device); `tests/unit/retrieval/test_semantic_cpu_embedder.py` (13 cases: the device listing read after the computation, each listing that is not wholly on the CPU refused, round 3's entries never served and dropped at the next write, a search makes the CPU embedder answer and not the shared runner); acceptance `test_w2_54_cpu_embedder.py` (§5.6.4) |

**Corrections.** §5.3 limit 2 ("Table `query_vector (model, revision, text_sha256, embedding)`") now reads
`device_query_vector`, keyed by model, revision, device and the sha256 of the exact text; the revision is the one the
CPU embedder's model list reports (both daemons read one model folder, so it is the shared runner's digest as well).
§5.5.3's "the cache is unchanged: … its key (model, revision, sha256 of the exact text)" and "the lead deletes it
before measuring" no longer apply: a vector cached by `b33ef9b3` or by §5.5.3's code is never served.

**Why the computation is deterministic now, and the shared runner untouched.** A question's vector is computed by a
daemon that has no GPU, and is used only once that daemon reports the model wholly on the CPU after computing it, so
every vector used is the CPU's vector of the text alone (§5.5.2). A cached vector was so checked when it was computed,
and its key says so. The shared runner is asked for chunks only, with no options, so its runner is never reloaded and
stays where it is loaded. The cost: the CPU embedder's memory while the model is loaded (about 2.4 GB, DEC-798 item 4;
Ollama unloads it after its idle keep-alive), its first load (about 1.8 s to start the daemon and 4.8 s for the first
question in this sandbox, under load), and 0.02 to 0.06 s a question after that (§5.5.2, probe 5).

#### 5.6.4 What was run here, and what the sandbox cannot measure

- **The acceptance cases with stand-ins** (`test_w2_54_cpu_embedder.py`, 14): 6 pass; 7 fail on two clauses of the
  cases that the code cannot meet without breaking another line, returned to the lead as packages (PKG-W2-54-4-1: the
  lexical route is an exact-phrase search and no note holds the cases' question, so "the lexical route gives
  evidence" cannot hold when the semantic facet is unavailable; PKG-W2-54-4-2: the first case's steps 5 and 6 repeat
  steps 1 and 2, whose vectors the cache then serves with no request, as KPI success 2 and round 3's cases require);
  the 14th is the figure the lead writes below. In a throwaway copy with only those two clauses varied, outside the
  tree, 13 of the 14 passed.
- **The measurement script for the lead, run once in this sandbox** against two daemons `gov` started there (the
  shared one through `ensure_available`, the CPU one through `ensure_query_available`): 360 reads in one process and
  96 in two processes at once with a third client, **0 differed**; the CPU embedder reported
  `size 2371270737, size_vram 0` and its vectors were used; `how is a query vector cached` gave `ad0ba0b6bb`, the
  CPU hash of §5.5.2. Its verdict there is RED for the reason it should be: the sandbox has no GPU, so the shared runner
  was on the CPU too. **None of it says anything about the shared GPU** (§5.5.2).
- **Not measurable in this sandbox:** the shared server (not reachable here); whether `CUDA_VISIBLE_DEVICES=-1` keeps
  a real GPU from the CPU embedder on this machine (the sandbox hides the GPU, so any daemon here is on the CPU; the
  check after the computation refuses a vector from GPU memory either way); the shared runner's placement after many
  reads; W1-21's real-models figure; the context check and `gov check` after a full rebuild; the CPU embedder's memory
  beside the shared runner's.

Measurement after the change on the shared GPU (run by the lead): *to be filled in: the command, the placement it
prints for the shared runner (`size_vram` against `size`) and the CPU embedder (its port, `size_vram`), the figures
(one process, two processes at once), the `shared_gpu` cases, and the context check's seconds, tickets and load after
a full rebuild with the cache deleted, against the declared `timeout-seconds: 600`.*

W1-21's hit@5 with CPU query vectors (run by the lead): *to be filled in.*

The script's command (the script is given to the lead with this engineer's return; it writes only in a temporary
folder of its own and never reads or deletes the worktree's cache file):

    env -u OLLAMA_HOST -u GOV_QUERY_OLLAMA_HOST PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src \
      python3 <the script>/eng5-measure.py

DEC-768, DEC-798 and CAP-33 govern this round; DEC-261 is read as DEC-798 amends it.
