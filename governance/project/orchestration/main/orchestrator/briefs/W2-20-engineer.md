# W2-20 — the engineer's brief, the rebuild (DAEO-r30l)

You are the engineer for **W2-20** (`.tickets/DAEO-r30l.md`): the machine-wide resource gate, rebuilt to its current
KPI lines (the owner's DEC-1097 (8)). Read the ticket in full first: every KPI line, its failure lines, and the body's
sections "Entry criterion from W2-136's review" and "The designer's points settled" (P-1 to P-8, W2-136's fixture).

## Where you work
- **Your worktree:** `/home/usain/gov-os-worktrees/W2-20`, branch `w2/W2-20`: today's `w2/integrate` with the
  designer's cases merged in. (The 10-17 build, made to the ticket's first four lines, is kept on the branch
  `w2/W2-20-1017`.)
- **Your earlier build:** you may reuse it. Read or copy only its code and unit tests:
  `git show w2/W2-20-1017:<path>` or `git checkout w2/W2-20-1017 -- <path>` for `src/gov/resources/**`,
  `src/gov/launch/gate*`, `tests/unit/resources/**`, and its one line in `src/gov/check/commands.py`
  (`RECORDED_GOV_COMMANDS` gains `resources`, beside today's `accept`). **Never** take or read anything under
  `tests/acceptance/` from that branch. Much of it predates the current lines (DEC-742's weights and session ceiling are
  gone: DEC-983); judge each piece against today's lines.
- **Your paths** (the ticket's `allowed_paths`): `src/gov/resources/**`, `src/gov/check/commands.py`,
  `src/gov/launch/gate*`, `src/gov/launch/plan_check.py`, `src/gov/launch/launcher.py`, `src/gov/launch/command.py`,
  `src/gov/rebuild/watch.py`, `src/gov/secrets/__init__.py`, `src/gov/codeintel/__init__.py`,
  `src/gov/retrieval/ollama.py`, `tests/unit/resources/**`, `tests/unit/rebuild/test_w2_20*`,
  `tests/unit/secrets_check/test_w2_20_*`, and `docs/changes/W2-20-evidence.md` (one row per KPI line, S1 to S21 in
  the ticket's order; S16's measured line "the CTO's run outside the sandbox").
- **You never read `tests/acceptance/W2-20/`** (DEC-820 (c), DEC-1056), on any branch, nor the cases this ticket's
  designer revised for it (`tests/acceptance/W1-07/`, `W1-26/`, `W1-32/`, and W2-136's launcher fixture): run them only
  through `gov accept` and read only the results. Every Grep or Glob call that could reach `tests/acceptance/` carries
  `!tests/acceptance/**`, and every recursive Bash search the matching exclusion (`grep -r --exclude-dir=acceptance`).

## The work, in order of risk
1. The configuration file (one file, every value dated and sourced, a missing or malformed value shuts the gate named;
   `gov resources --init-config`, P-3), the readings (memory, load, busy cores, the servers' p95, disk and inodes, the
   GPU on a declared need), the machine-wide registry and the stale-entry clearing.
2. The launch enforcement (DEC-1088 (5)(b), P-1, P-2): every `gov launch`, lead or worker, runs the start check;
   `--gate-override DEC-NNN` logged to `~/.gov-os/machine/launch.log` and standard error.
3. W2-136's F2 line (S21): the plan check reads the main tree's tickets and ready list from a lead worktree, and a plan
   override is written to the launch log too.
4. Heavy-job slots with their thread budget and CPU set, the pools sized to the CPU set (`gov.secrets`, the code
   index), the re-measure with the rebuild peak (P-5, P-7), the trip-wire, the GPU shares.
5. The DEC-1037 line: `ensure_query_available(start=True)` carries the interim wrapper's caps (device from the gate
   file, no thread-budget variables inherited, its own log, one start-log line naming the caller).
Never make a gate reading fail open: a reading that cannot be taken shuts the gate, named.

## Tests and evidence
- **Unit tests** in your test paths, planted machines only: stand-in `/proc` readers, a planted registry under a
  temporary HOME (never the real `~/.gov-os/`), a stand-in `nvidia-smi`, stand-in executables that record their
  environment, affinity and niceness. Never the real embedding servers (11434, 11435), never the GPU.
- **Every test run** through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh <command>`
  (where the sandbox allows it), with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src` and
  `-m "not local_only" -k "not real and not green_here and not time_limit"` on whole folders.
- **Report progress by commits:** commit each step above as it passes its unit tests, so a session that ends early
  leaves its work committed.
- **When your unit tests pass:** `python3 -m gov.cli.main accept W2-20 --root /home/usain/gov-os-worktrees/W2-20`
  (and `accept W2-136`, `accept W1-07`, `accept W1-32`), report the counts; then `tests/unit/resources tests/unit/launch
  tests/unit/retrieval tests/unit/secrets_check tests/unit/rebuild`, and list every red with its cause.

## Rules
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **The machine is the owner's:** never touch the Ollama servers, the reranker service, `~/.local/bin`, `~/.ollama`,
  `~/.gov-os/` or any service. No GPU job.
- **Search again once (DEC-1092 (1)):** if a search (Grep and Read; no `gov retrieve` in the sandbox) does not answer,
  search once more in your own, different words; then answer from both, with path and lines, or say "not found".
- **DEC-1080:** Read and Grep tools; one simple command per Bash call; no `cd … &&` chains.
- **Do not merge `w2/integrate` yourself.** Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-20`, only your paths, with
  `--trailer "Task: DAEO-r30l" --trailer "Implements: DEC-1088, DEC-1037, DEC-1097" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- **Before you end your session,** make sure every test run you started has finished.

## Return
Your whole return is your session's **final message**, in full (the launcher keeps it in this worktree's log; it is
the record): the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first), the diff's size, what you
reused from the 10-17 build, the unit tests' outcome, `gov accept`'s counts per ticket, and the regression run's counts
with every red named; if you stop before every line is built, say which lines are done (committed) and which are not.
