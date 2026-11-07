# G1's profile: where the time goes when 20 agents search at once (DEC-1094 (1))

The CTO, 2026-11-07, about 19:05, session `ad44f5fe`.
- **Script:** `profile_burst.py`, kept in `~/gov-os-runs/PAT-1/`.
- **Output:** `~/gov-os-runs/PAT-1/profile-1.json`.
- **Method:** three bursts of 20 searches at once (W2-112's 20 visible questions) against the integration store and the live shared reranker (`pin-bcea09060ebc`, the cap of 16), sampled every 100 ms:
  - the GPU's utilization and memory (`nvidia-smi -lms 100`);
  - the service process's CPU time (`/proc/<pid>/stat`);
  - the service's requests, counted from its MEMORY lines.
- **The limit:** the pinned service is not instrumented (that would be an ACT), so each request's split comes from these samples.

## Measured
| burst | wall | requests | s per request | GPU util mean (incl. 2 s idle margins) | GPU util median | samples with the GPU busy | service CPU mean / p90 | GPU peak |
|---|---|---|---|---|---|---|---|---|
| 1 | 17.42 s | 63 | 0.276 | 56.8 % | 81 % | 68.5 % | 0.79 / 1.2 cores | 9,457 MiB |
| 2 | 14.72 s | 63 | 0.234 | 57.8 % | 85 % | 80.5 % | 0.81 / 1.2 cores | 9,457 MiB |
| 3 | 14.53 s | 63 | 0.231 | 57.2 % | 75 % | 81.4 % | 0.79 / 1.2 cores | 9,457 MiB |

- **Within the burst itself** (the 1 s idle sampled before and after left out): the GPU runs a kernel in about **90 %** of samples, at about **65 %** mean utilization.
- **The service's CPU:** about **0.8 of one core**, its one Python thread mostly busy feeding the GPU.

## What it shows
- **The GPU is not mostly idle between requests.** It is busy most of the burst. Batching queued requests (option (b)) could recover at most the remaining gaps: about 10 to 35 %, so 14.5 s might come down to about 10 to 13 s at best.
- **Larger requests did not help** (W2-137's S5: 64 texts per request, 2.75 requests per search, 14.8 to 15.1 s). That fits a GPU bound by compute rather than by per-request overhead.
- **The work per search is the floor:** each search scores about 41 pairs (63 requests of about 13 texts for 20 searches), padded to long chunks. 20 searches is about 820 pairs through one model, about 14 s.
- **Under DEC-1094 (1)'s rule, this is the "saturated" branch.** The lever is fewer scored pairs or tokens per search: a lower rerank depth, a cap on each pair's characters (`fusion.RERANK_LIMIT_CHARS`), or a smaller or faster reranker. These are retrieval choices that move hit@5, so they come to the owner after E3 to E5, measured on the 138. (b) is not filed now.

## W2-137's cap of 64 at the lift
- **Today's three bursts at the cap of 16** took 14.5 to 17.4 s. S5's at the cap of 64 took 14.8 to 15.1 s, and PAT-1's at 16 took 13.4 to 13.9 s.
- **The spread between runs of the same cap** (13.4 to 17.4 s) is as wide as the difference between the caps, so the "slightly slower" reading is noise.
- **MRR 0.558 against 0.567** is 8 rank moves with hit@5 unchanged. It is within the bfloat16 batching noise W2-137's reviewer named.
- **Recommendation:** let W2-137 go live at the lift as it is.
  - Neither cost is real, and it keeps a pool of short candidates in one request.
  - It keeps the service's named refusal over its bound.
  - Setting it back would turn W2-137's own S1 cases red and need a new ticket, for no measured gain.

**Basis:** question 4 (the fix chosen on a measured cause, not a guess).
