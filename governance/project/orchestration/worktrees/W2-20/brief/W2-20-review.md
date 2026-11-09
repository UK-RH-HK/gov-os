Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-20/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-20 — the independent review (DAEO-r30l), round 1

You are a fresh, read-only independent reviewer. Review **W2-20** (`.tickets/DAEO-r30l.md`: read it in full, every KPI
line S1 to S21 in order, the failure lines, and the body's sections "Entry criterion from W2-136's review", "The
designer's points settled" P-1 to P-8 and "The engineer's round-1 points"): the machine-wide resource gate, rebuilt to
its current lines (DEC-1097 (8)); the launch enforcement of DEC-1088 (5)(b); W2-136's F2 (S21); the DEC-1037 query
start (S20). Profile STANDARD, but it is the gate every launch passes after the lift: judge fail-open with care.

## What to review
- **The branch:** `w2/W2-20` in `/home/usain/gov-os-worktrees/W2-20`, against `w2/integrate`
  (`git diff w2/integrate...w2/W2-20`): `src/gov/resources/**`, `src/gov/launch/{gate,launcher,command,plan_check}.py`,
  `src/gov/rebuild/watch.py`, `src/gov/secrets/__init__.py`, `src/gov/codeintel/__init__.py`,
  `src/gov/retrieval/ollama.py`, `src/gov/check/commands.py`; the unit tests (`tests/unit/resources/**`,
  `tests/unit/rebuild/test_w2_20*`, `test_w2_76_*`, `tests/unit/secrets_check/test_w2_20_*`, the four launch unit
  tests' fixtures); the designer's cases `tests/acceptance/W2-20/` and its revisions of W1-07, W1-26, W1-32 and
  W2-136's launcher fixture; `docs/changes/W2-20-evidence.md`. The 10-17 build on `w2/W2-20-1017` is history only.
- **The CTO's runs outside the sandbox** are in the line at the end of this brief.
- **The machine:** the owner's operator applied ACT-GATE-CONFIG-1 (`d7490945`): `~/.gov-os/machine/gate.json` exists.
  Its working size (2.04 GiB) is below today's measured lead p95 (3.2 GB): `gov resources --remeasure` re-measures it
  after the merge. On WSL, `nvidia-smi` reports per-process GPU memory as `[N/A]`; round 2 was asked to fail closed on
  the GPU only when the total free memory says so: check what it did.

## Check
- Every KPI line and failure line, against the code and the cases: in particular that **no reading that cannot be
  taken opens the gate** (S8, F5), that a full set of slots never refuses a session while an unreadable slot reading
  does (P-2), that the launch refusal names the limit and its reading and the override is logged once to the launch
  log and standard error (S19, P-1), that the plan check follows the main tree (S21), that a worker's memory is never
  charged twice (F6), that no fixed session ceiling exists (F4), and that the thread budget and CPU set hold (S15, S17).
- **Ordinary work:** could an honest lead or worker launch be refused falsely on this machine as configured (a reading
  misparsed on WSL, the `[N/A]` GPU figures, a stale registry entry, the busy-cores sample)? Could a launch slip
  through with the gate shut?
- The DEC-1037 query start: does it carry the wrapper's caps (device, no thread-budget variables, its log, one caller
  line) without changing the shared server's start?

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.

## Write and return
- **You write nothing** in any tree; run nothing that writes, and nothing that writes under the real `~/.gov-os/`
  (tests read-only with `-p no:cacheprovider`, through the heavy slot; planted HOMEs only). No GPU job; never the
  Ollama servers or the reranker service. Single simple Bash commands (DEC-1080). The hidden-half rule holds: never
  open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder.
- **Search again once (DEC-1092 (1)):** if a search does not answer, search once more in your own words.
- **Your record is your session's final message**, in full (the launcher keeps it; the CTO transcribes it): the twelve
  labelled fields of `EMG-common.md` (sandbox and `ps` checks first), your verdict per line, every finding with its two
  lines and `scope: in|out`, and at the end the fenced `verdict` block, one entry per line S1 to S21 and F1 to F6:
  `{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ...]}`.

