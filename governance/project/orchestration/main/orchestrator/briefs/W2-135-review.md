# W2-135's review: a cap per bundle item (DEC-1086 B, DEC-1087 (1))

You are an independent reviewer for the CTO. You read everything and change nothing: your one write is your record,
`.gov-runtime/scratch/orchestrator/reviews/w2-135.md` in the main tree. Read
`.gov-runtime/scratch/orchestrator/briefs/EMG-common.md` for the common rules.

**What to review:** branch `w2/W2-135` (worktree `/home/usain/gov-os-worktrees/W2-135`) against `w2/integrate`. The
engineer's commit changes `src/gov/retrieval/retrieve.py` (+8/−1), adds `tests/unit/retrieval/test_w2_135_item_cap.py`
and `docs/changes/W2-135-evidence.md`. The ticket is `.tickets/DAEO-c4pb.md`: judge against S1 to S3 and its two
failure lines, nothing else.

Check in particular:
- an item over 4,000 characters (characters, not bytes) is sent as its first 4,000 with `cut`, its path, lines, id,
  chunk id and sha256 unchanged;
- the pieces of an expanded parent are cut the same way;
- the budget's `used` is still counted on the full text, so no expansion changes;
- nothing reads an item's text in a way the cut would change: the reranker, `validate`, the pool, the continuation and
  any consumer of the bundle (the measure's matching is by lines);
- an item of exactly 4,000 characters is sent whole, with no key.

**Facts the CTO has:**
- `gov accept W2-135` 48/0/0;
- the unit tests, 12 passed;
- `tests/unit/retrieval` with `tests/acceptance/W2-32`: 705 passed, 18 failed. The 18 are only the W2-112 shared
  reranker's socket, refused by the sandbox; the CTO runs them outside it.

Re-run what you need through the heavy slot (`tools/heavy_slot.sh`). No GPU, no real model.

**The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
`memory-verdict` or `memory-verdict-2` folder.

**DEC-1080:**
- read with the Read and Grep tools;
- one simple command per Bash call;
- no `cd … &&` chains and no `git -C`;
- one line before any command that will ask for permission.

**The judgement rules:** `governance/project/briefs/JUDGEMENT.md`, word for word, applied to every finding. Each finding
carries `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.

**Your record:** for S1, S2, S3 and each failure line (`failure-1`, `failure-2`):
- what you checked and the findings;
- the fenced `verdict` block:
  `{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`.

Then return the record's path and the verdict block. Est.: 45 minutes.
