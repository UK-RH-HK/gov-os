# P-W2-111-MEASURE-1, round 2: form B on the CTO's full benchmark (owner's item; short form)

**The question.** You chose (a), form B, on run 2's figures (DEC-1163 (3)). The CTO's full benchmark of form B has
now run, and W2-57's case failed once under real contention. Do we land W2-111 as decided, or change something first?

**Why now.** W2-111 (`DAEO-qvff`, head `3da7242f4461`, DONE) is held unlanded until you answer. Holding it costs nothing
else: no other ticket waits on it.

**What form B judges** (unchanged): each round's CPU p95 of the hook and its children, less the median CPU of a stub
hook timed beside each call, against 100 ms; 40 samples a round; a case passes when one of its 3 rounds is under 100 ms.

**The benchmark** (`.gov-runtime/scratch/orchestrator/drafts/w2-111-bench/formB/`: `bench.sh`, `bench.out`, a `.log`
and a `.figs` file per run), 2026-11-13 11:48-12:47 UTC. These are the 15 revised cases (W1-02 ×5, W1-05 ×9, W2-57 ×1):

| run | load (1-min, start → end) | result |
|---|---|---|
| quiet | 13 → 7 | 15/15 pass (raw hook CPU p95 at most 65 ms) |
| load 20 (22 busy loops) | 20 → 37 (W2-88's full suite ran too) | **14/15**: W2-57 red in all 3 rounds |
| load 20, planted 150 ms hook | 37 → 30 | 15/15 fail (good) |
| load 50 (56 busy loops) | 51 → 79 | 15/15 pass |
| load 50, planted 150 ms hook | 79 → 24 | 15/15 fail (good) |

- **W2-57's red** (a test designer's read on a branch with changes): judged 172.5, 138.8 and 104.0 ms against 100.
  The raw CPU p95 was 201.6, 163.4 and 131.0; the stub's median 29.1, 24.6 and 27.0; the wall p95 505, 330 and 332.
  At load 50 it passed in round 1 (raw CPU 117.4 ms, so judged about 90 ms). Quiet, it was 64.6 raw.
- **The reading:** 59 of 60 unplanted runs pass, and the plant is caught 60 of 60 times. W2-57's hook path is the
  heaviest. It runs git on a branch with changes, so its CPU rises with disk and process contention. The stub is
  pure Python and does not feel that contention, so the subtraction does not cancel it. W2-57 sits near the bound
  under load (about 90 ms at load 50) and goes over when a full suite runs beside it.

**The options.**
- **(a) Land form B as decided** (about 10 minutes: merge the tests branch and `gov accept`, then the land). W2-57's
  case stays load-sensitive: when a full suite runs beside it, it can go red in a landing check or the nightly. The
  nightly re-runs every red alone, and the landing check's triage does the same. Cost: an occasional red on W2-57
  to triage.
- **(b) Land form B and give W2-57 alone more evidence per round:** 80 samples instead of 40, 100 ms unchanged.
  Cost: a W2-111 round 3, about 2 hours, and the benchmark again. Risk: a larger sample narrows the noise, but it
  does not fix a hook that really is slow under contention.
- **(c) Land form B, and speed up the guard's designer-read path** (the git work on a branch with changes, for example
  computed once a session rather than on every call). This is a new product ticket, yours to file. Cost: about half a
  day. It removes the cause rather than measuring around it.
- **(d) Re-baseline S2** (DEC-105). Not recommended: S2 holds for 14 of the 15 cases at every load.

**Recommendation: (a) now, plus (c) filed as a small ticket** (I do not file it without your word, DEC-974).
Confidence: medium. The figures support form B (no false pass at any load), and W2-57's margin is a real property of
its hook path, not of the measure.

Your line: `W2-111 (a)` (or `(a)+(c)`, `(b)`, `(d)`).
