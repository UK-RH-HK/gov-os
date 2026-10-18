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
