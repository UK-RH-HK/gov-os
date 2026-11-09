Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-145-d10-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list: W1-19's default-reranker case looks for a process the shared service never starts (W2-145, DAEO-2tfd)

You are a fresh **independent test designer**, launched under W2-145's ticket (`.tickets/DAEO-2tfd.md`: "no
private reranker beside the shared service"). The CTO found this red while it reproduced D-10's list tonight.
DEC-1109 (2) asks that the list be ready before D-10's full run.

## The red (measured by the CTO, outside the sandbox, at integrate `b0bbd373f`)
- **The case:** `tests/acceptance/W1-19/test_w1_19_real_models.py::test_the_default_reranker_is_a_process_of_its_own_started_from_the_reranker_environment`.
  It is marked `local_only` (the real reranker); the full run includes it.
- **Its results:**
  - In a first `-n auto` run of the W1-19 folder it passed. That run started the shared reranker service.
  - In a second run, with the service still up, it failed. Run alone with the service up, it failed again:
    `no process started with /home/usain/.local/share/gov-os/reranker-venv/bin/python was seen under the calling process (DEC-397): []`.
  - Everything before that assertion passed: the default reranker scored every candidate, in order, with "seam"
    first, and the caller loaded none of the reranker's libraries.
- **The cause:**
  - The case was written for DEC-397 and ADR-0002 §2, when the default reranker was a private child process of the
    caller.
  - Since DEC-982 (W2-112), one shared reranker service serves every session, and W2-145 removes the private
    reranker beside it.
  - A call made while the service is already running starts nothing under the caller, so the case is red whenever
    any session on the machine has the service up. On this machine that is most of the time.

## The task
1. Revise the case to today's decisions:
   - The default reranker scores in a process of its own, started from the reranker environment's interpreter
     (`support.reranker_python()`), never one of the workbench's.
   - That process is the shared service, whether this call started it or it was already running.
   - The calling process loads none of the reranker's libraries (keep that check as it is).
   - Keep every scoring check as it is.
   - Find the service's process from its public interface: its socket, or a pid or log file it documents. Read
     `docs/research/W2-112-shared-reranker.md` and W2-112's README.
   - Do not read W2-145's implementation (`src/gov/retrieval/rerank.py`, `rerank_worker.py`, `rerank_service.py`):
     DEC-820 (c). If the public interface does not say how to find the service's process, return PACKAGES with
     your recommendation; do not guess from the code.
   - Keep the case's failure when the reranker runs in the caller's own process, or under another interpreter.
2. Rename the case if its name no longer says what it checks. Add one line to W1-19's README, appended to the
   revision list (another branch adds a line there tonight; append, do not edit other lines).
3. Every commit carries `--trailer "Rewrite-Reason: DEC-982: one shared reranker service serves every session (W2-112; W2-145 removes the private one), so a call made while it runs starts no process under the caller"`.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-145-d10-tests`, branch `w2/W2-145-d10-tests`. It is integrate at
  `9f9809e09`, plus the CTO's ticket commit `c2dc4a563` (the file in W2-145's paths).
- Write only `tests/acceptance/W1-19/test_w1_19_real_models.py` and `tests/acceptance/W1-19/README.md`.
- **You may not be able to run the case:** it needs the real reranker and the shared service's socket. W2-127 lets
  the launch sandbox reach that one socket; try it once.
  - If it cannot run, collect it (`--collect-only -q`) and say so. The CTO runs it outside the sandbox, both with
    the service up and with it down.
- Run through the heavy slot (`EMG-common.md`), with:
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-145-d10-tests/src` and `TMPDIR` a folder of your own under the
    sandbox's TMPDIR;
  - `python3 -m pytest "tests/acceptance/W1-19/test_w1_19_real_models.py" -q -p no:cacheprovider -o tmp_path_retention_policy=failed`.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No installs, never the full suite. Use no GPU beyond
  the one case's reranker call, and never start or stop the shared service or Ollama yourself.
- Commit on `w2/W2-145-d10-tests` only, with `--trailer "Task: DAEO-2tfd" --trailer "Implements: DEC-1109, DEC-982"`
  `--trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
  plus the Rewrite-Reason trailer. Never merge, push, amend or rebase.
- Estimate: 30 minutes. Return the twelve fields, short:
  - how the service's process is found, and from which document;
  - the case before and after;
  - whether it ran here;
  - the head commit.
