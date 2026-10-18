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
