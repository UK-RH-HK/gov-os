# W2-20 — the independent test designer's brief (DAEO-r30l), the revision round

You are the independent test designer for **W2-20** (`.tickets/DAEO-r30l.md`): the machine-wide resource gate. W2-20
was built on 2026-10-17 to its first KPI lines (branch `w2/W2-20`, held since). Its ticket has since gained and changed
many lines (the load and memory rules, disk and inodes, the heavy-job slots, the configuration file, the re-measure,
the GPU, the trip-wire, the embedding servers' CPU cap, the thread budget and CPU set, the pools, the launch
enforcement of DEC-1088 (5)(b), and today the DEC-1037 query-wrapper removal line). The owner's DEC-1097 (8) rebuilds
W2-20 to its current lines. **Your job: revise its acceptance tests for every new and changed KPI line.** Profile
STANDARD: every KPI line's success and failure, plus the key edge cases; no combinatorial expansion.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-20-tests`, branch `w2/W2-20-tests`, made from `w2/integrate` today.
- **First, bring the old cases:** the 10-17 acceptance tests exist only on `w2/W2-20`. Copy that folder, and only that
  folder, into your worktree with `git checkout w2/W2-20 -- tests/acceptance/W2-20` and commit it unchanged as its own
  commit ("the 10-17 cases brought from w2/W2-20"). Read nothing else from that branch.
- You write only `tests/acceptance/W2-20/`: the cases, `conftest.py`, `w2_20_support.py` and the `README.md` whose map
  the runner reads (header `| KPI line | Test (node id) | On integrate | Why |`, one KPI id per cell, the test in
  backticks with its full node id, as `tests/acceptance/W2-133/README.md`). Give each current KPI line an id (S1, S2,
  … in the ticket's order) and map every line. State there the interface the tests assume (commands, output fields,
  the configuration file's keys, exit codes, the launch refusal's wording and the override's log line), so the
  engineer builds to it.
- **Which lines are new or changed:** compare the old README's map with today's KPI lines; the ticket file's own
  history (`git log -p -- .tickets/DAEO-r30l.md`) shows when each line came. An old case whose line is unchanged and
  still right stays as it is; a case whose line changed is revised; a new line gets new cases. Every revision or
  deletion of an old case is its own commit with `--trailer "Rewrite-Reason: DEC-1097 (8)"` and listed in your return.
- **Your record:** write your return (the twelve fields below) also to
  `/home/usain/gov-os-worktrees/W2-20-tests/.gov-runtime/scratch/lead/W2-20-designer-return.md` (you cannot write the
  main tree's scratch).
- You may read any code on `w2/integrate`: `src/gov/launch/` (the launcher, W2-136's `plan_check.py`, how a refusal is
  raised and logged), `src/gov/retrieval/ollama.py` (`ensure_available`, `ensure_query_available`, `_config`,
  `_capped`, the gate file's `GATE_REL` and section, for the DEC-1037 line and the CPU-cap line),
  `src/gov/secrets/__init__.py` and `src/gov/codeintel/__init__.py` (their pools), `src/gov/rebuild/watch.py`,
  `src/gov/check/commands.py`, and the existing tests of those modules for their stand-ins. The interim wrapper the
  DEC-1037 line replaces is `/home/usain/.local/bin/ollama` (read it; never run it, never touch `~/.ollama`).

## What the cases must show
- Every current KPI line and failure line, as the ticket states it, each with its `Verify:` clause where it has one.
- **Planted machines only:** readings from planted `/proc`-like inputs or stand-in readers, a planted machine registry
  under a temporary HOME (never the real `~/.gov-os/machine/`), a stand-in `nvidia-smi` on PATH, a planted
  configuration file, stand-in executables that record their environment, CPU affinity and niceness; never the real
  embedding servers (ports 11434 and 11435), never the real GPU.
- **The launch line (DEC-1088 (5)(b)):** each reading planted shut refuses a `gov launch` of a lead and of a worker,
  naming the limit and its reading; the override `gate_override: <DEC-id>` starts it and is written in the launch log
  and the plan's output. Test the check through the launcher's refusal path with a stub session; no session starts.
- **The DEC-1037 line:** `ensure_query_available(start=True)` with a stand-in executable and no wrapper on PATH: the
  CPUs and niceness from the gate file, the device per the file (GPU visible by default; `CUDA_VISIBLE_DEVICES=-1` for
  the CPU), a malformed device value shutting the start with its name, no thread-budget variable inherited (planted
  `OMP_NUM_THREADS`, `GOMAXPROCS`, `GOV_HEAVY_THREAD_BUDGET` …), the output appended to the server's log, one start-log
  line with the time, the device and the caller.
- **The measured line** (a planted suite in one slot, busy cores within the share plus one, time within 20 %): write
  it as a `local_only` case the CTO runs outside the sandbox, and say so.
- W2-20's implementation is not on integrate, so nearly every case is red there: say for each case whether it is red
  on integrate for the right reason (and which reason: the module missing, the reading missing, the refusal missing),
  or a green guard.
- W2-136's F2 entry criterion (in the ticket's body, not a KPI line) is not yours to test; name it in `discoveries` if
  you think it needs a KPI line.

## Rules
- **Never read this ticket's implementation (G-14; DEC-820 (c)):** it exists, on the branch `w2/W2-20` and in the
  worktree `/home/usain/gov-os-worktrees/W2-20`. Never open that worktree; from the branch, take only
  `tests/acceptance/W2-20/` as above, never `git show`, `git diff` or `git log -p` of any other path on it (no
  `src/gov/resources/**`, no `src/gov/launch/gate*`, no `tests/unit/resources/**`, no `docs/changes/W2-20*`). You
  work from the ticket's KPI lines and today's integrate code only.
- **The exclusion line (DEC-1093 (2)), for you:** keep every Grep, Glob and recursive Bash search inside your own
  worktree, never from `/home/usain/gov-os-worktrees/` or `/home/usain/`, so no search can reach the W2-20 engineer
  worktree; if a search shows you a line of the implementation anyway, stop reading it and say so in your return.
- **Search again once (DEC-1092 (1)):** if what you searched (Grep and Read; no `gov retrieve` in the sandbox,
  `EMG-d4b-launched.md`) does not answer, or you can tell your answer may be incomplete, search once more in your own,
  different words; then answer from both searches and the files you read, with path and lines, or say "not found".
  Two searches in all.
- No GPU, no model, no network, no real servers.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- Run your cases through the heavy slot that `EMG-common.md` names (where the sandbox allows it), with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20-tests/src`, and run
  `python3 -m gov.cli.main accept W2-20 --root /home/usain/gov-os-worktrees/W2-20-tests` to show the runner reads
  your map.
- **DEC-1080:** read with the Read and Grep tools; one simple command per Bash call; no `cd … &&` chains; one line
  before any command that will ask for permission.
- **Commit** on `w2/W2-20-tests`, only `tests/acceptance/W2-20/`, with
  `--trailer "Task: DAEO-r30l" --trailer "Implements: DEC-1088, DEC-1037, DEC-1097" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`,
  and `--trailer "Rewrite-Reason: DEC-1097 (8)"` on every commit that revises or removes an old case.
- **Before you end your session,** make sure every test run you started has finished: do not end with a background
  run still going.

## Return
The twelve labelled fields of `EMG-common.md` (sandbox check and `ps` check first), with the case list (node id, KPI
line, red or green on integrate, and why), every old case kept, revised or removed (with its reason and commit), the
commits, `gov accept`'s counts, `TESTS-READY` text, and anything untestable or ambiguous as `discoveries` or a
decision package with your recommendation and confidence.
