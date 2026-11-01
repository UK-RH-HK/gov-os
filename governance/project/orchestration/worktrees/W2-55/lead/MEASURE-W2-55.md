# W2-55: W2-61's 20-question measure after the change (KPI 6; DEC-941, DEC-833 item 3)

Run by the lead, in its own session (not sandboxed: the shared embedder), 2026-11-01 04:20 to 04:31 GMT.

## Where

- **The tree measured:** a clone at `2281b081cc7d` (the ticket's code head before the repair batch; the repair
  `412ccd63cf5c` is a cache of the register's parse and changes no answer, and the later commits change only
  `tests/acceptance/W2-55/`), `/home/usain/gov-os-runs/W2-55/head`.
- **Its store:** built by the head's own code (`gov-head rebuild --json` under `flock /tmp/gov-os-rebuild.lock`):
  digest `b42d0a28259979840611b6e1179ebd66dc5a3dbde2643f921b31635c2d9aceec`, 1,829 records, 979 register entries,
  51,418 vectors. (A first store built by the pinned gov, digest `8a7b8528…`, held 64 vectors and a schema older than
  the base's code reads: `no such column: span`; the base's code answered `STORE_MISSING`. It was not used.)
- **The two code states,** each through a launcher under the pinned interpreter (W2-87's form), in the session
  scratchpad `bin/`:
  - control `gov-base`: `/home/usain/gov-os-runs/W2-55/base/src` at `84c1d4277b9c` (the ticket's base);
  - head `gov-head`: `/home/usain/gov-os-runs/W2-55/head/src` at `2281b081cc7d`.
- **The measure:** `gov.retrieval.measure` from `/home/usain/gov-os-runs/W2-55/measure` at `e55883ca02b5`
  (`w2/integrate`), visible half only (`--part visible`; the hidden half was not run), default budgets
  (`--batch-size 10 --bundle-budget 6000 --stack-budget 24000`).
- **Records:** `/home/usain/gov-os-runs/W2-55/records/measure-memory-retrieval-visible-20261101T042015457494Z.json`
  (control) and `…-20261101T043140266796Z.json` (head, `--compare` the control).

## Both figures together

| | hit@5 (CAP-10's floor 85) | full evidence (target 99 %) | in the bundle |
|---|---|---|---|
| W2-61's baseline (`23079f92a6fa`) | 8 of 20 (40 %) | 12 of 20 (60 %) | 14 of 20 |
| W2-87's head (`cffef92c8534`) | 11 of 20 (55 %) | 11 of 20 (55 %) | 15 of 20 |
| control: the base's code (`84c1d4277b9c`) on this tree | 11 of 20 (55 %) | 11 of 20 (55 %) | 15 of 20 |
| **head: W2-55's code (`2281b081cc7d`)** | **11 of 20 (55 %)** | **11 of 20 (55 %)** | **15 of 20** |

- Against CAP-10's floor of 85: short by 30 points. Against the 99 % target: short by 44 points.
- Per question, the head equals the control in hit@5, first gold rank, in the bundle and full evidence for 20 of 20.
  The stacked context differs for 3 (Q01, Q05, Q16); the filter is the only change of code between the two runs, so
  it left out register evidence of superseded entries there; no figure moved. Q18 and Q19: no hit, not in the bundle, not full, in both.
- What it means: on today's register (8 entries superseded, none yet marked done) leaving entries out costs the
  set nothing and gains nothing. Its effect grows when the accepted backfill marks the done and superseded entries.
