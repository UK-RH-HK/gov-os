# W2-87 memory measure: W2-61's 20-question measure after the register fix and the authority order, visible half

- **Ticket:** DAEO-s9qc (W2-87), profile STANDARD. Written by the engineer from the outputs of the measure its lead ran.
- **Date:** 2026-10-30.
- **Sources:** DEC-952 item 1 (memory's quick wins, each re-measured with W2-61's measure), DEC-941 item 1 (the measure re-run after each ticket of the memory chain, beside W2-61's baseline), DEC-833 item 3 (both figures, always together), DEC-877 (a bare `gov` is the pinned gov), CAP-10 (the floor of 85 for hit@5); the ticket's KPI line 6. The baseline beside these figures is `docs/research/W2-61-baseline.md`.

This record holds scores only: ids, counts, ranks, digests and pass or fail. It quotes no question's text, no gold answer and no text of a retrieved item.

## 1. What was measured, and where

- **The tree measured:** a clone at commit `cffef92c8534` (this ticket's head: the register fix, the authority order and the one-line fix), `/home/usain/gov-os-runs/W2-87/head`. Every run retrieved from this tree and its stores; each run's record gives `commit` `cffef92c8534`.
- **The three code states,** each the `src/` of its own clone (each `git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS <path>`, left detached):

  | Run | Code | Clone | What it is |
  |---|---|---|---|
  | control | `df0782fa4c4e` | `/home/usain/gov-os-runs/W2-87/base` | the ticket's base; only its `src/` is used |
  | batch 1 | `006ad0bb36ce` | `/home/usain/gov-os-runs/W2-87/register` | the register fix alone; only its `src/` is used |
  | head | `cffef92c8534` | `/home/usain/gov-os-runs/W2-87/head` | both parts and the one-line fix; also the tree measured and its stores |

- **The launchers** (`--gov`): each is the pinned launcher's body (import `main` from `gov.cli.main` and exit with it) under a first line that chooses the code:
  - control, `gov-base`: `#!/usr/bin/env -S PYTHONPATH=/home/usain/gov-os-runs/W2-87/base/src /home/usain/.local/share/gov-os/pin-5c401220/bin/python`
  - batch 1, `gov-reg`: `#!/usr/bin/env -S PYTHONPATH=/home/usain/gov-os-runs/W2-87/register/src /home/usain/.local/share/gov-os/pin-5c401220/bin/python`
  - head, `gov-head`: `#!/usr/bin/env -S PYTHONPATH=/home/usain/gov-os-runs/W2-87/head/src /home/usain/.local/share/gov-os/pin-5c401220/bin/python`

  They lived in the lead's session scratchpad (`/tmp/claude-1000/…/scratchpad/bin/`), because the guard refused the orchestrator role's writes under `~/gov-os-runs/W2-87/bin/`.
- **The retriever each run records** (`retriever`):

  | Run | `gov_file` | Version |
  |---|---|---|
  | control | `/home/usain/gov-os-runs/W2-87/base/src/gov/__init__.py` | `gov 0.1.0 (commit df0782fa4c4e)` |
  | batch 1 | `/home/usain/gov-os-runs/W2-87/register/src/gov/__init__.py` | `gov 0.1.0 (commit 006ad0bb36ce)` |
  | head | `/home/usain/gov-os-runs/W2-87/head/src/gov/__init__.py` | `gov 0.1.0 (commit cffef92c8534)` |

- **The measure:** `src/gov/retrieval/measure.py` from a fourth clone, `/home/usain/gov-os-runs/W2-87/measure`, at `e814289d58c4` (`w2/integrate`'s head when measured). The measure's code last changed at `289b9314`, and it and the visible set are unchanged since `df0782fa4c4e`. It ran with `PYTHONPATH` set to that clone's `src/` and `GOV_TICKET` removed; the retrieving process is the launcher's code.
- **The set:** `memory-retrieval`, the visible half only: the 20 questions Q01 to Q20, read from the measure clone (`--sets-root`). The hidden half was not measured.
- **The budgets:** the measure's defaults, `--batch-size 10`, `--bundle-budget 6000`, `--stack-budget 24000`, as in W2-61's baseline.

## 2. The stores' fingerprint

One set of stores, built once in the head clone at `cffef92c8534` and used by all three runs. They were built by the base's code (`gov-base`), not by the pinned gov (deviation 1, §7), with embeddings, as `env -u PYTHONPATH -u GOV_TICKET flock /tmp/gov-os-rebuild.lock <gov-base> rebuild --json`, after the disk gate.

| | The rebuild |
|---|---|
| Code | the base's, `df0782fa4c4e` (`gov-base`) |
| Gate at the start: disk | 875 GiB and 65,160,169 inodes free |
| End (UTC) | 21:20:11 on 2026-10-30 |
| Exit code | 0 |
| Stores (`lexical`, `semantic`, `codeintel`) | each `recreated` |
| Embeddings | built (never `--no-embeddings`) |

**The digest the rebuild records** (`result.digest`; `result.store.digest` is the same value, with no invalid entries):

- the stores' fingerprint: `0b7e7d00c83f52f5cd6772c95eb1ac7637b83c081f192699a68bd13bd63a35c5`

This worktree's own rebuild at the same commit, by its own code, gave the same digest.

**The sha256 of each store file after the rebuild:**

| Store file | sha256 |
|---|---|
| `.gov-runtime/store.db` | `bdb4572966a45eccbbfa7119b406b9ddc8b43cee509a71c44cc13c4d2e5d9070` |
| `.gov-runtime/codeintel/home/code.db` | `45073c6280bd8a7e32b3a054cbb0eeea3b91e5b8589cbcb11ee3ab7885a38c17` |
| `.gov-runtime/codeintel/home/_config.db` | `6881a590e961b4c4faff0180c79e87d6af9c34a9367e12cf28bbe2dbc4028cf8` (the same as W2-61's) |

**The pinned gov's rebuild, not used:** the pinned gov (`5c40122014da`) rebuilt the stores at `060e03ef57ea` with exit 0 and digest `522296ef1709a39100d8a8ce9ed9819bf1c548373c3f877d7fa1cc41361c6c2d`, but every retrieval from them refused with STORE_MISSING (deviation 1, §7).

## 3. The runs

Each run on 2026-10-30, from the head clone, on the stores of §2. Times UTC.

| Run | Code (`--gov`) | Ended | Length | Exit | Record (`--out`) | `--compare` |
|---|---|---|---|---|---|---|
| control | `gov-base` (`df0782fa4c4e`) | 21:38:41 | 1,088 s | 0 | `measure-memory-retrieval-visible-20261030T213841067037Z.json` | — |
| batch 1 | `gov-reg` (`006ad0bb36ce`) | 21:52:56 | 846 s | 0 | `measure-memory-retrieval-visible-20261030T215256578023Z.json` | the control |
| head | `gov-head` (`cffef92c8534`) | 22:11:54 | 1,129 s | 0 | `measure-memory-retrieval-visible-20261030T221154739899Z.json` | the control |

Each run's stderr was empty. The records are under `/home/usain/gov-os-runs/W2-87/records`. A comparison covers five fields per question: hit@5, in the bundle, full evidence, the first gold rank and the stacked digest (the paths and line spans of the stacked context, in order).

## 4. The totals: both figures together

| | hit@5 against CAP-10's floor of 85 | Full evidence against the owner's target of 99 % | In the bundle |
|---|---|---|---|
| W2-61 baseline (`23079f92a6fa`, pinned gov) | 8 of 20 (40 %) | 12 of 20 (60 %) | 14 of 20 |
| control (the base's code) | 7 of 20 (35 %) | 11 of 20 (55 %) | 13 of 20 |
| batch 1 (the register fix) | 7 of 20 (35 %) | 11 of 20 (55 %) | 13 of 20 |
| head (the register fix and the authority order) | 11 of 20 (55 %), floor 85: short by 30 points | 11 of 20 (55 %), target 99 %: short by 44 points | 15 of 20 |

## 5. Per question, visible half

Each cell gives, in order: hit@5, first gold rank, in the bundle, full evidence (pieces found of needed). "First gold rank" is the rank, in the stacked context, of the first item that matches a gold source; "in the bundle" means an item of the first call matches one. The baseline is W2-61's §5. Batch 1 equals the control in all five compared fields for 20 of 20 questions. The head differs from the control in the stacked digest for 20 of 20, and in the fields the last column names.

| Q | W2-61 baseline | control | batch 1 | head | The head differs from the control in |
|---|---|---|---|---|---|
| Q01 | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | same as the control | yes, 1, yes, yes (1/1) | stacked digest |
| Q02 | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | same as the control | yes, 1, yes, yes (1/1) | stacked digest |
| Q03 | yes, 4, yes, yes (1/1) | no, 6, yes, yes (1/1) | same as the control | yes, 2, yes, yes (1/1) | hit@5, first gold rank, stacked digest |
| Q04 | yes, 3, yes, yes (1/1) | yes, 3, yes, yes (1/1) | same as the control | yes, 1, yes, yes (1/1) | first gold rank, stacked digest |
| Q05 | yes, 2, yes, yes (1/1) | yes, 2, yes, yes (1/1) | same as the control | yes, 1, yes, yes (1/1) | first gold rank, stacked digest |
| Q06 | no, 9, yes, yes (2/2) | no, 9, yes, yes (2/2) | same as the control | no, 7, yes, yes (2/2) | first gold rank, stacked digest |
| Q07 | no, 12, yes, yes (1/1) | no, 12, yes, yes (1/1) | same as the control | no, 12, yes, yes (1/1) | stacked digest |
| Q08 | no, 9, yes, yes (1/1) | no, 9, yes, yes (1/1) | same as the control | no, 11, yes, yes (1/1) | first gold rank, stacked digest |
| Q09 | no, 60, no, yes (1/1) | no, 60, no, yes (1/1) | same as the control | no, 46, no, yes (1/1) | first gold rank, stacked digest |
| Q10 | no, 25, no, no (1/2) | no, 25, no, no (1/2) | same as the control | no, none, no, no (0/2) | first gold rank, stacked digest |
| Q11 | yes, 4, yes, no (1/2) | yes, 4, yes, no (1/2) | same as the control | yes, 4, yes, no (1/2) | stacked digest |
| Q12 | yes, 2, yes, yes (1/1) | yes, 2, yes, yes (1/1) | same as the control | yes, 1, yes, yes (1/1) | first gold rank, stacked digest |
| Q13 | no, 6, yes, no (1/2) | no, 6, yes, no (1/2) | same as the control | yes, 1, yes, no (1/2) | hit@5, first gold rank, stacked digest |
| Q14 | no, 16, yes, no (7/9) | no, 16, yes, no (6/9) | same as the control | no, 17, yes, no (6/9) | first gold rank, stacked digest |
| Q15 | yes, 4, yes, yes (1/1) | yes, 4, yes, yes (1/1) | same as the control | yes, 1, yes, yes (1/1) | first gold rank, stacked digest |
| Q16 | no, 7, yes, yes (1/1) | no, none, no, no (0/1) | same as the control | no, none, no, no (0/1) | stacked digest |
| **Q17** | no, 21, no, no (1/2) | no, 21, no, no (1/2) | same as the control | **yes, 2, yes, no (1/2)** | hit@5, in the bundle, first gold rank, stacked digest |
| Q18 | no, none, no, no (0/2) | no, none, no, no (0/2) | same as the control | no, none, no, no (0/2) | stacked digest |
| Q19 | no, none, no, no (0/1) | no, none, no, no (0/1) | same as the control | no, none, no, no (0/1) | stacked digest |
| **Q20** | no, 21, no, no (1/2) | no, 21, no, no (1/2) | same as the control | **yes, 2, yes, no (1/2)** | hit@5, in the bundle, first gold rank, stacked digest |

**Q17 and Q20,** whose first five in W2-61's baseline were tests and assessment reports (W2-61's §5): each moves from rank 21 to rank 2, into the first five and into the bundle; each still finds 1 of 2 needed pieces, so full evidence stays no for both.

**First gold ranks that changed, control to head:**

- **Better (10):** Q03 6 → 2, Q04 3 → 1, Q05 2 → 1, Q06 9 → 7, Q09 60 → 46, Q12 2 → 1, Q13 6 → 1, Q15 4 → 1, Q17 21 → 2, Q20 21 → 2.
- **Worse (3):** Q08 9 → 11, Q14 16 → 17, Q10 25 → none (its one found piece lost: 1 of 2 → 0 of 2; Q10 was not full in either).
- **Into the first five:** Q03, Q13, Q17, Q20 (hit@5 7 → 11 of 20). Of these four, full evidence: Q03 yes in both; Q13, Q17 and Q20 no in both (1 of 2). Out of the first five: none.
- **Into the bundle:** Q17, Q20 (13 → 15 of 20; full evidence 11 → 11 of 20, hit@5 7 → 11 of 20). Out of the bundle: none.
- **Full evidence changed for no question:** 11 of 20 in both (hit@5 7 → 11 of 20, in the bundle 13 → 15 of 20); Q10's pieces found fell from 1 to 0 of 2, not full in either.

## 6. What each part moved

The owner asked to see the effect of each step (DEC-952 item 1).

- **The register fix (batch 1, `006ad0bb36ce`):** nothing on this set. hit@5 7 → 7 of 20, full evidence 11 → 11 of 20, in the bundle 13 → 13 of 20; batch 1 equals the control in all five compared fields for 20 of 20 questions. The register's last entry (DEC-953) is current, so no register chunk was being dropped, and the six questions with a ticket gained no register chunk in their stacked context. Its effect is on a store whose last entry is superseded (where every register chunk was dropped) and on a closure that reaches an older entry; the acceptance tests show both.
- **The authority order (batch 2, measured at the head `cffef92c8534`):** hit@5 7 → 11 of 20; full evidence 11 → 11 of 20; in the bundle 13 → 15 of 20. Q17 and Q20, whose first five in W2-61's baseline were tests and assessment reports, now have a governing source at rank 2. Full evidence did not move: Q17 and Q20 still find 1 of 2 needed pieces, and Q10 lost its one piece.
- **Against W2-61's baseline:** hit@5 8 → 11 of 20 (40 % → 55 %, floor 85: short by 30 points); full evidence 12 → 11 of 20 (60 % → 55 %, target 99 %: short by 44 points); in the bundle 14 → 15 of 20. The control (the base's code on today's tree) is already 1 below the baseline on each figure (hit@5 7 of 20, full evidence 11 of 20, in the bundle 13 of 20): Q03 and Q16 changed with the tree and the store builder, not with this ticket.

## 7. Deviations and what they mean

1. **The store builder.** The brief named the pinned gov (`5c40122014da`). Its rebuild (exit 0, digest `522296ef1709a39100d8a8ce9ed9819bf1c548373c3f877d7fa1cc41361c6c2d`, at `060e03ef57ea`) writes a `register_entries` table with no `span` column. W2-03's queries, in the base's code as in batch 1's and the head's, select that column, so every retrieval refused with STORE_MISSING ("no such column: span"). The store code (`src/gov/store/**`, `src/gov/records/**`) is the same at the base, batch 1 and the head, so the lead built the stores with the base's code: one store, by code no run is testing, for all three runs.
   - **What it means:** W2-61's baseline was the pinned gov retrieving from the pinned gov's stores; the control here is the base's code on the head tree's stores. That is why the control and the baseline differ (Q03 and Q16; hit@5 8 → 7, full evidence 12 → 11, in the bundle 14 → 13 of 20). The three runs here differ only in the retrieving code.
2. **The tree.** The first measured tree was `060e03ef57ea` (the control there: hit@5 7, full evidence 11, in the bundle 13 of 20; record `measure-memory-retrieval-visible-20261030T204744666636Z.json`). The lead's verification then found that the visible set's Q11 names a line of `src/gov/retrieval/retrieve.py` that batch 2 had rewritten. The fix `cffef92c8534` keeps that line as it was and lifts on the next one, with no change of behaviour. The runs were stopped and redone on `cffef92c8534`, the tree reported here.
   - **What it means:** the control's figures were the same on both trees (hit@5 7, full evidence 11, in the bundle 13 of 20), and every figure in §3 to §6 is from `cffef92c8534`.
3. **The order of steps.** The owner asked for a re-measure after the register fix and again after the authority order. The lead ran both after the code was done, on one tree and one set of stores, with batch 1's code as its own launcher.
   - **What it means:** the same figures the step-by-step order would give for the code, with no difference of tree or store between the steps.

## 8. How to repeat it

W2-61's §8, with these changes:

1. **Three clones by exact path,** each `git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS <path>`, detached: `/home/usain/gov-os-runs/W2-87/base` at `df0782fa4c4e`, `/home/usain/gov-os-runs/W2-87/register` at `006ad0bb36ce`, `/home/usain/gov-os-runs/W2-87/head` at `cffef92c8534`; and the measure's own clone, `/home/usain/gov-os-runs/W2-87/measure` at `e814289d58c4`.
2. **The stores,** in the head clone, by the base's code (not the pinned gov, deviation 1), with embeddings, after the disk gate: `env -u PYTHONPATH -u GOV_TICKET flock /tmp/gov-os-rebuild.lock <gov-base> rebuild --json`. Record its `digest` and the sha256 of `.gov-runtime/store.db`, `.gov-runtime/codeintel/home/code.db` and `.gov-runtime/codeintel/home/_config.db`.
3. **Three launchers,** `gov-base`, `gov-reg` and `gov-head`, as in §1: the pinned launcher's body under a first line that sets `PYTHONPATH` to the clone's `src/`.
4. **The measure, three times on the same stores,** from the head clone:

   ```
   env -u GOV_TICKET PYTHONPATH=/home/usain/gov-os-runs/W2-87/measure/src python3 -m gov.retrieval.measure memory-retrieval \
     --root /home/usain/gov-os-runs/W2-87/head --sets-root /home/usain/gov-os-runs/W2-87/measure --part visible \
     --gov <launcher> --out /home/usain/gov-os-runs/W2-87/records --json [--compare <the control's record>]
   ```

   First with `gov-base` (the control), then `gov-reg` and `gov-head`, each with `--compare` the control's record. The budgets are the measure's defaults: `--batch-size 10 --bundle-budget 6000 --stack-budget 24000`.
5. **Never `--part hidden`.**
