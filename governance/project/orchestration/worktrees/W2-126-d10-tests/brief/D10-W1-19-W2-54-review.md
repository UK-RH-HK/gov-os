Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-126-d10-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list: the review of W1-19's scratch environment and W2-54's `shared_gpu` case (W2-126, DAEO-jpr0)

You are a fresh, read-only independent reviewer. **Narrow scope: two small revisions.** READY is computed by
`verdict.py` from your block.

## What happened
- **A.** `tests/acceptance/W1-19/test_w1_19_embedding_policy.py::test_only_the_namespace_that_says_embedded_reaches_the_vectors`
  was red only when other W1-19 tests ran first in the same process (`'February' in ''`).
  - `tests/conftest.py` gives each test its own `GOV_VECTOR_CACHE_DIR` (W2-126, DEC-1042).
  - But `Api.scratch_env` builds the subprocess environment from nothing, and the session-scoped `api` shares one
    empty HOME. So a cached vector from an earlier test served this one.
- **B.** `tests/acceptance/W2-54/test_w2_54_shared_gpu.py`'s second case asserted the query embedder wholly on the
  CPU (DEC-798).
  - DEC-1033 replaced DEC-798. Its item (2)(b) reads: "a question's vector accepted from any device and the query
    server on the GPU".
  - The machine's query server (127.0.0.1:11435) holds the model with `size_vram == size`.

## What to review
- **The branch:** `w2/W2-126-d10-tests` in `/home/usain/gov-os-worktrees/W2-126-d10-tests`. Read
  `git -C /home/usain/gov-os-worktrees/W2-126-d10-tests diff adec4718a..8bb8182f1`.
  - `769f01577` is the CTO's ticket commit.
  - `498204460` is A: `w1_19_support.py` reads `os.environ["GOV_VECTOR_CACHE_DIR"]` when it builds the environment,
    plus a README line.
  - `8bb8182f1` is B: the case renamed to `…_the_query_server_hold_the_model_on_the_gpu_at_one_revision`, asserting
    the query server wholly on the GPU; the docstrings and README rows revised.
- **The designer's runs:** A: `-n auto` 1 failed, 24 passed → 25 passed; serial the same (with `-m "not local_only"`).
  B: collected only; the sandbox blocks the GPU.
- **The CTO's runs outside the sandbox, at `8bb8182f1`:**
  - A: W1-19 with `-n auto -m "not local_only"` gave 25 passed; serial gave 25 passed, 16 deselected.
  - B: `-m shared_gpu -s` on the real GPU gave 2 passed, printing: "the query server serves at 127.0.0.1:11435 …
    size 2370652077 … size_vram 2370652077; the shared runner at 127.0.0.1:11434: size 2370652077, size_vram
    2370652077; digest ['ac6da0df…']".

## Check
1. **A, no expectation lowered:** the case still proves that the embedded namespace's text was sent. With the
   variable unset, is the behaviour as before? Do other environments W1-19 builds from scratch drop per-test
   variables the conftest sets (`GOV_GUARD_CALLS_DIR` too)? Does the session-scoped `indexed` fixture's shared cache
   matter to any case?
2. **B, the choice:** the designer asserts the query server on the GPU rather than "any device", citing DEC-1033
   (2)(b) and DEC-1065 (1). Read both in `docs/DECISION_REGISTER.md`. Is the choice what the decisions say, or
   stricter than they allow? Is anything else the case checked lost (the shared runner before and after, one
   revision, the printed line)?
3. **Trailers:** Task, Role, Implements, a Rewrite-Reason per commit, and Co-Authored-By. Only the four named files
   changed, plus the CTO's ticket line.

KPI ids for the verdict block: `w1-19-vector-cache`, `w2-54-query-device`.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this revision.

## Write and return
- **You write nothing** in any tree.
- You may run the tests read-only (`-p no:cacheprovider -o tmp_path_retention_policy=failed`) through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=<the branch's worktree>/src`, a TMPDIR folder of your own under the sandbox's TMPDIR, and
  `PYTHONUSERBASE=/home/usain/.local` if you set an empty HOME (so pytest is found).
- No GPU, no installs, never the full suite. Single simple Bash commands (DEC-1080).
- The hidden-half rule holds: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **Your record is your session's final message**, in full:
  - the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first);
  - your answers to the checks;
  - every finding, with its two lines and its scope;
  - at the end, the fenced `verdict` block:
    `{"kpis": [{"kpi": "<id>", "verdict": "pass|fail", "findings": [...]}]}`, one entry per KPI id named above,
    each finding `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 15 minutes.
