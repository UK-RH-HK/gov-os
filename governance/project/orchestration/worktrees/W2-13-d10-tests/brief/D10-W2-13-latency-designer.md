Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-13-d10-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list: W2-13's real-model latency case routed to the nightly (W2-13, DAEO-zqvn)

You are a fresh **independent test designer**, launched under W2-13's ticket (`.tickets/DAEO-zqvn.md`).

## Why
- **The case:** `tests/acceptance/W2-13/test_w2_13_latency.py::test_a_warm_retrieval_with_the_real_models_answers_within_the_budget`.
  It asks the real embedder (and reranker) and asserts W1-19's warm budget, p95 at most 0.5 s.
- **Its results:** red in the full run's form, and red alone. The CTO's helper's runs on 11-10:
  - 0.560 s at load 12.5;
  - 0.543 s starting at load 2;
  - 0.578 s at load 12.
- **The existing mechanism for such cases** is `tests/acceptance/serial-only.txt`, the project's routes (DEC-372,
  DEC-527, DEC-889 item 5).
  - Its kind `real-model` ("starts or asks a real model (the embedder, the reranker)") takes the route `nightly`: left
    out of both of the close's phases, and run in the nightly alone.
  - W1-19's real-model file (line 100), W2-54's real-embedder case (line 103) and W2-54's two time-limit cases (W2-85,
    `1a682b6a4`, DEC-951 item 3) are routed so.
  - This W2-13 case is not listed. It is a real-model case.
- **The CTO's instruction:** route it to the nightly by the existing mechanism, and **do not loosen the 0.5 s limit**.

## The task
1. Add one entry in `tests/acceptance/serial-only.txt`'s "real-model: routed to the nightly" block, in the file's own
   form (`<node id>  # nightly: real-model: <the reason in words>`).
   - The reason says what the case asks of the real models, and that it was red alone on 11-10 (0.543-0.578 s
     against 0.5 s). The latency itself is filed against W2-13, not excused.
2. Check whether `test_the_ranked_lexical_route_answers_a_warm_question_within_the_budget` (no model) is on the list
   as `serial: latency`. If not, and it asserts a time bound, add it to the latency block the same way. Say which.
3. Change nothing in `test_w2_13_latency.py`. The 0.5 s budget stays.
4. Check the readers still parse the file:
   - `tests/acceptance/W1-30` and `tests/acceptance/W2-57` read it (their serial-only cases), with both opt-ins;
   - `tests/unit/close/test_serial*` if present.
   - Report the counts.
5. One line in W2-13's README.
6. Every commit carries `--trailer "Rewrite-Reason: DEC-889 item 5: a real-model case takes serial-only.txt's nightly route; W2-13's warm p95 with the real models joins W1-19's"`.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-13-d10-tests`, branch `w2/W2-13-d10-tests`, at integrate `9ca161a6f`.
- Write only `tests/acceptance/serial-only.txt` and `tests/acceptance/W2-13/README.md`.
- Run through the heavy slot, with:
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-13-d10-tests/src`;
  - `TMPDIR` a folder of your own under the sandbox's TMPDIR;
  - `PYTHONUSERBASE=/home/usain/.local` if HOME is a scratch folder.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no model, no installs, never the full suite.
  Never run `git worktree prune`.
- Commit on `w2/W2-13-d10-tests` only, with `--trailer "Task: DAEO-zqvn" --trailer "Implements: DEC-1109, DEC-889"`
  `--trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
  plus the Rewrite-Reason trailer. Never merge, push, amend or rebase.
- Estimate: 15 minutes. Return the twelve fields, short: the entries, the readers' counts, the head commit.
