Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-126-d10-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list: W1-19's parallel-only red, and W2-54's `shared_gpu` case (W2-126, DAEO-jpr0)

You are a fresh **independent test designer**, launched under W2-126's ticket (`.tickets/DAEO-jpr0.md`: the
machine-wide vector cache, and the query embedder's emergency patch's unit tests). Both cases below are on D-10's
red-fix list. DEC-1109 (2) asks that the list be ready before D-10's full run. Two small revisions, one session.

## Item A: W1-19, red only when other W1-19 tests ran first in the same process
- **The case:** `tests/acceptance/W1-19/test_w1_19_embedding_policy.py::test_only_the_namespace_that_says_embedded_reaches_the_vectors`.
- **Its results:**
  - it passes alone;
  - it fails under `-n auto` over `tests/acceptance/W1-19` (the CTO's run tonight at integrate `b0bbd373f`: 1 failed
    with `'February' in ''`, i.e. the stand-in endpoint received no text);
  - it failed 3 of 3 in a serial folder run on 11-05.
- **The cause (the CTO's reading; confirm or refute it with a run):**
  - `tests/conftest.py` gives each test its own `GOV_VECTOR_CACHE_DIR` (W2-126, DEC-1042).
  - But W1-19's `Api.scratch_env` (`tests/acceptance/W1-19/w1_19_support.py`) builds the subprocess environment from
    nothing, so the variable is dropped.
  - The `api` fixture is session-scoped, so every W1-19 test in one process shares one empty HOME. The machine-wide
    cache therefore falls back to `<that HOME>/.cache/gov-os/vector-cache`, one per process.
  - An earlier test that embedded the same text leaves its vector there. This case's build is then served from the
    cache, and the stand-in never sees the orchard file's text.
- **The task:**
  - Make W1-19's scratch environment carry the running test's own cache folder. Read `GOV_VECTOR_CACHE_DIR` from
    `os.environ` when the environment is built, not at import. Keep a case that sets or unsets the variable itself
    working.
  - Check whether any other environment W1-19 builds from scratch (`env_without_sqlite_vec`, others) needs the same.
  - Lower no expectation: the case must still prove that the embedded namespace's text was sent.
  - Prove it: the case green under `-n auto` over the W1-19 folder, and in a serial run of the folder, with the
    folder's other counts unchanged.
- **Trailer:** `Rewrite-Reason: DEC-1042: W1-19's scratch environment dropped the test's own vector cache folder (W2-126), so a test was served another's cached vectors`.

## Item B: W2-54's `shared_gpu` case asserts the query embedder on the CPU
- **The case:** `tests/acceptance/W2-54/test_w2_54_shared_gpu.py::test_shared_gpu_the_shared_runner_keeps_the_model_on_the_gpu_and_the_cpu_embedder_holds_it_on_the_cpu`.
- **What it asserts:** the query embedder at its default address (`S.QUERY_HOST_DEFAULT`) holds the model with
  `size_vram == 0`, wholly on the CPU. That was DEC-798.
- **The decision now:** DEC-1033 **replaced** DEC-798. Its item (2)(b) reads: "a question's vector accepted from any
  device and the query server on the GPU". Read DEC-1033 in `docs/DECISION_REGISTER.md` and the W2-54 README's
  round 4.
- **What the machine shows (CTO, read-only `/api/ps`, tonight):** the query server on 127.0.0.1:11435 holds
  `qwen3-embedding:0.6b` with `size_vram == size` (2,370,652,077 bytes), wholly on the GPU. So the case is red
  against the decision in force.
- **The task:**
  - Revise the case, its name if it must change, its docstring, and the module docstring's "the CPU-only embedder
    holds the model on the CPU" to DEC-1033 (2)(b). Choose, and say why, between:
    - asserting the query server's model on the GPU;
    - asserting it served from any device.
  - Keep the rest: the shared runner on the GPU before and after, both at one revision, the printed line.
  - Update the README's rows for the case (lines near 634-635) in one line each.
  - **You cannot run it:** the sandbox blocks the GPU and the shared server. Collect it only:
    `python3 -m pytest tests/acceptance/W2-54/test_w2_54_shared_gpu.py --collect-only -q -m shared_gpu`.
    The CTO runs it outside the sandbox afterwards.
- **Trailer:** `Rewrite-Reason: DEC-1033 (2)(b) replaced DEC-798: the query server is on the GPU and a question's vector is accepted from any device`.
- Also sweep `tests/acceptance/W2-54/` for any other assertion of the CPU placement. Revise none, and name each.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-126-d10-tests`, branch `w2/W2-126-d10-tests`. It is integrate at
  `adec4718a`, plus the CTO's ticket commit `769f01577` (both files in W2-126's paths).
- Write only:
  - `tests/acceptance/W1-19/w1_19_support.py` (and the W1-19 README, one line);
  - `tests/acceptance/W2-54/test_w2_54_shared_gpu.py`;
  - `tests/acceptance/W2-54/README.md`.
- Do not read W2-126's implementation (`src/gov/retrieval/vector_cache.py`, `semantic.py`): DEC-820 (c). The variable's
  name and meaning are in `tests/conftest.py`'s header.
- Run through the heavy slot (`EMG-common.md`), with:
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-126-d10-tests/src` and `TMPDIR=/tmp/gov-os-emg-w126d10`;
  - `python3 -m pytest tests/acceptance/W1-19 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -n auto`,
    then the same without `-n auto`.
  - The `local_only` cases need the real models: do not run them. The one p95 timing case is on the
    `load_sensitive` list. Name it if it is red; do not fix it.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no model, no installs, never the full suite.
- Commit on `w2/W2-126-d10-tests` only:
  - one commit per item;
  - each with `--trailer "Task: DAEO-jpr0" --trailer "Implements: DEC-1109, DEC-1042, DEC-1033"`
    `--trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
    plus its own Rewrite-Reason trailer.
- Never merge, push, amend or rebase.
- Estimate: 40 minutes. Return the twelve fields, short:
  - A: the cause confirmed or refuted, and the counts before and after (parallel and serial);
  - B: the choice made and why, the collect-only line, and the other CPU assertions named;
  - the head commit.
