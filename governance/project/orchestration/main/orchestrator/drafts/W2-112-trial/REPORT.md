# W2-112's shared reranker: a short trial under real load (2026-11-03), for the owner

Ordered by the owner, 2026-11-03. Run by a research worker (scripted searches, two agent sessions) and the CTO (the
sandboxed worker). Raw data beside this file: `samples.jsonl` (472 samples, every 0.25 s), `searches.jsonl`,
`figures.txt`, `s1.json` to `s3.json`; the sandboxed worker's log in
`~/gov-os-worktrees/W2-112/.gov-runtime/scratch/lead/log/t2-trial.json`.

**Set-up:** the service started by the CTO at 13:45:09 with one search (READY pid 356621, `cuda:0`; cold search
14.2 s; idle end 43,200 s); the slot watcher (pid 8416) holding the other GPU reranker slot; gov = pin-9894b0cf; the
integration store at 9894b0cf514a; the 20 visible questions only.

## Ordinary sessions: it holds
- **61 of 61 searches** (5 alone, 10 at once, 20 at once, two batches of 10 beside two Haiku agent sessions, and the
  sessions' own six) came back `{"by": "service", "device": "cuda:0"}`, `merge.reranked` true. None unranked, none on
  the CPU, no private reranker started, no FALLBACK/REFUSED line added to `~/.cache/gov-os/rerank.log`.
- **The GPU slot:** in all 472 samples slot 0 was held by the service, slot 1 by the watcher.
- **Time per whole search** (CLI, query embedding, routes, rerank of up to 90 candidates):

  | phase | n | p50 | p95 | max |
  |---|---|---|---|---|
  | alone | 5 | 1.14 s | 1.26 s | 1.28 s |
  | 10 at once | 10 | 2.12 s | 2.68 s | 2.72 s |
  | 20 at once | 20 | 4.13 s | 5.33 s | 5.46 s |
  | 10 at once beside 2 agent sessions | 20 | 3.38 s | 4.73 s | 4.82 s |

  The service answers one request at a time (about 0.2 s each), so waits grow with the number at once; the slowest
  (5.5 s) is far inside the 30 s request limit. (2026-11-02's figures were rerank-only: not comparable one for one.)
- **GPU memory:** 8,764 MiB at the start, peak 9,816 MiB (20 at once), 9,653 MiB after; budget 14,255 MiB (13.9 GiB):
  4.4 GB under it. The service's RSS 1.66-1.68 GiB. About 900 MiB stayed after the trial, by process unknown (WSL's
  `nvidia-smi` shows no per-process figures): to re-read after an hour of real use.

## A sandboxed worker (P-W2-112-T2): unranked, named, never on the GPU or the CPU
`gov launch engineer DAEO-clon` (Haiku, 3 searches, writing nothing; the sandbox check passed; tripwire: no change).
Each search: `rerank` = `{"by": "unavailable", "device": null, "reason": "the shared reranker did not answer (OSError:
[Errno 30] Read-only file system: '/home/usain/.cache/gov-os'); the private reranker ended without the model (its GPU
slot check failed)"}`, `merge.reranked` false; 1.35-2.44 s. The sandbox also denied two `ollama.com:443` connections per
search (not the reranker's; to trace). Nothing reached the GPU or the CPU; no FALLBACK line could be written (the log
is under the read-only folder).
**Consequence:** sandboxed workers (test designers, engineers launched by `gov launch`) search without ranking today.
Its home is W2-127 (the reranker socket in the sandbox, filed 2026-11-02): the client needs `~/.cache/gov-os` (the
socket and its folder) reachable in the sandbox.

## Verdict
It holds for ordinary sessions: one process, ranked on the GPU, its slot held, no fallbacks, well inside the GPU
budget. **It keeps running** for the refactoring's searches (idle end 12 h). The sandboxed case fails safe (unranked
and named), and is W2-127's to fix.
