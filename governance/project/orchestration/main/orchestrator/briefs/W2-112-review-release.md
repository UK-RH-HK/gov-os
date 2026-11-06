# W2-112's review: the shared reranker releases its GPU memory after each request (DEC-1068, re-pin window 4)

You are an independent reviewer for the CTO. You read everything and change nothing: your one write is your record,
`.gov-runtime/scratch/orchestrator/reviews/w2-112-release.md` in the main tree. Read
`.gov-runtime/scratch/orchestrator/briefs/EMG-common.md` for the common rules.

**What to review:** branch `w2/W2-112` (worktree `/home/usain/gov-os-worktrees/W2-112`, integrate merged in) against
`w2/integrate`.
- **The engineer's commit:** `7448ce364`: `src/gov/retrieval/rerank_service.py` (+61/−11), its unit tests in
  `tests/unit/retrieval/test_w2_112_shared_reranker.py`, the evidence row.
- **The designer's acceptance cases:** `789abcfa7`.
- **The ticket:** `.tickets/DAEO-clon.md`. Judge **only** its DEC-1068 note for re-pin window 4:
  - the shared service releases the GPU memory a request used once it has answered (the PyTorch caching allocator's
    cache emptied after each request, or after each request whose padded size passed a named threshold; it states which
    and why);
  - its memory no longer climbs to its highest peak and stays there;
  - the client's padded request bound stays;
  - the service's memory after each request is logged in `rerank.log`, allocated and reserved MiB.

  The rest of W2-112 merged earlier and is not under review.

**Why it matters:** on 2026-11-04 the service climbed from 7.7 to 15.8 GB across experiments and twice tripped the GPU
backstop. Window 4 restarts the live service from this code (class 3), and the experiments run on it.

Check in particular:
- the release runs after the answer is sent, and never delays or breaks a request;
- an error during scoring still releases, and still answers or fails named as today;
- concurrent requests do not race the release;
- the log line's form and cost;
- nothing changes the scores or the order (the same answers as before);
- a machine with no CUDA (or a CPU device) does not fail.

**Facts the CTO has:** on the merged branch, `gov accept W2-112` 52/52, and the shared-reranker unit file 34 passed
(outside the sandbox, which refuses the service's socket). Re-run what you need through the heavy slot, outside the
sandbox for the socket cases. No GPU job and no real model: the tests use stand-ins.

**The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
`memory-verdict` or `memory-verdict-2` folder.

**DEC-1080:**
- read with the Read and Grep tools;
- one simple command per Bash call;
- no `cd … &&` chains and no `git -C`;
- one line before any command that will ask for permission.

**The judgement rules:** `governance/project/briefs/JUDGEMENT.md`, word for word. Each finding carries
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.

**Your record:** for the DEC-1068 note (as one KPI line, `dec-1068-release`) and W2-112's failure lines as they apply
to it, what you checked and the findings. End with the fenced `verdict` block:
`{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`.
Then return the record's path and the verdict block. Est.: 45 minutes.
