# W2-122 evidence: KPI 3, seeded against cold on this repository

The implementer's evidence of KPI 3 (DEC-996 item 3 A), written from the ticket lead's measurements. The engineer
wrote this record; the lead ran every rebuild and took every figure.

## What KPI 3 asks

> Measured, in docs/changes/W2-122-evidence.md: a new worktree's first rebuild seeded from the integration store
> against a cold one, alone and with two others running, on this repository (the semantic stage's seconds and the
> embedding requests sent) [DEC-1014, DEC-996 item 3 A]

## How it was measured

- **Who and where:** the lead, in its own session (not a sandbox), on this repository.
- **The embedder:** the shared embedding server (127.0.0.1:11434, `qwen3-embedding:0.6b`, revision `ac6da0dfba84`,
  on the GPU).
- **The slot:** each rebuild ran through the machine's heavy-job slot (`rebuild_slot.sh`).
- **Embedding requests:** counted by a pass-through proxy in front of the server, one proxy per run, which logged
  every POST to `/api/embed` and its number of inputs.
- **The semantic stage's seconds:** read from the rebuild's own `timing.semantic_s`.
- **Other rebuilds beside each run:** sampled every 30 s from the process table.

## The figures

| run | tree | seed | semantic_s | total_s | embed requests | chunks embedded | other rebuilds beside it |
|---|---|---|---|---|---|---|---|
| cold | new worktree at `800cca6fba83`, empty `.gov-runtime/` | none | 4709.2 | 4761.6 | 1701 | 54,425 | two others 74 % of samples, one other 25 % (158 samples); never alone |
| seeded, nothing changed | this worktree at `800cca6fba83`, its first rebuild | `seeded` from the cold run's tree; copied `.gov-runtime/store.db` and the code-graph home | 0.7 | 30.8 | 0 | 0 | two others (1 sample) |
| seeded, one file changed | a throwaway worktree at `800cca6fba83` with `docs/plan/WAVE_2_WBS.md` edited (one line appended) and one untracked file added | `seeded` from the same base | 20.3 | 57.7 | 10 | 320 (exactly that file's 320 chunks; the untracked file is not indexed) | one other (1 sample) |
| cold, first attempt (failed) | new worktree at `dda239e827fc` | none | — | 3013 s wall before failing | 1023 before the failure | 32,736 | one rebuild (itself) in every sample |

The other stages, in seconds:

| stage | cold | seeded, nothing changed | seeded, one file changed |
|---|---|---|---|
| record | 6.2 | 4.0 | 5.1 |
| lexical | 17.4 | 0.6 | 2.0 |
| secrets | 15.2 | 7.2 | 9.3 |
| codeintel | 26.1 | 22.5 | 26.1 |
| compaction | 2.6 | 1.9 | 2.4 |

`total_s` is the rebuild's own time. The wall times also include the wait for a slot: for the cold run, 5942 s
wall, of which about 1,180 s was spent waiting; for the seeded run with one file changed, 475 s wall.

## KPI 1 on this repository

The lead compared this worktree's seeded store with the cold run's store, at the same commit. The rebuild digests
are equal (`b5408db1250c7b8a…`). All 54,425 chunk vectors are equal: each was joined on its chunk id, path and
lines, and the vectors were compared by their sha256. Because both stores are at the same commit, this is the
expected case. The planted-repository acceptance cases cover files added, changed and removed.

## Alone and with two others

At least one other rebuild ran on the machine throughout the measurement window (2026-11-01 23:00 to 2026-11-02
01:50), so no run was alone in the strict sense:

- The cold figure is a cold rebuild with two others beside it most of the time. That is the condition SIZING-1
  describes (3,000 to 3,750 s with three at once).
- The seeded figures were taken with one and with two others beside them.
- **A cold rebuild strictly alone was not measured.** It would need an idle machine and about 80 minutes of a
  slot. KPI 3's "alone" case is therefore open for the cold side.

The seed's base also departs from the KPI's wording. It was **the cold run's tree, not the integration store**
(`~/gov-os-worktrees/W2-00-store`). The cold run's tree was a base of the same kind, a fully rebuilt tree with its
stores record, at the same commit. A seed from the integration store itself is refused wherever that store's `gov`
code differs from this worktree's (see below).

## The failed first attempt

The shared server's runner was reloaded during the run. An embed request failed after 1,023 of about 1,700, and the
rebuild answered `REBUILD_FAILED` naming the semantic store. That is KPI 5 doing its work: before this ticket, the
rebuild would have answered ok over a partial store.

## What the figures mean

- **The semantic stage:** the seeded first rebuild's semantic stage took 0.7 s (nothing changed) and 20.3 s (one
  file changed), against 4,709 s cold. It sent 0 and 10 embedding requests, against 1,701.
- **The code graph:** it is rebuilt from scratch either way, in about 25 s. The indexer replaces the copied
  code-graph home, so copying it saves no time today.
- **When a seed is refused:** a seed is refused, and the rebuild runs cold, wherever the running `gov` code differs
  from the base's. The code fingerprint covers every file of the running `gov` package, gitleaks and the interpreter
  and SQLite versions. So in this repository, a worktree whose ticket changes `src/gov/**` does not seed. For
  example, the first attempt's base, at `dda239e827fc`, could not have seeded this worktree after the repair commit
  `800cca6fba83`.
