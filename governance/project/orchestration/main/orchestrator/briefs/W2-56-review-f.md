# W2-56 — the narrow review of the follow-ups R3 and R5 (DAEO-wnnz)

You are a fresh, read-only independent reviewer. **Narrow scope: R3 (under S1) and R5 (under S5)** of W2-56
(`.tickets/DAEO-wnnz.md`: read S1, S5, F3 and the notes at its end). The round-1 review that raised them is
`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/reviews/w2-56.md` (findings R3 and R5).
READY is computed by `verdict.py` from your block.

## What was decided (not findings against the engineer)
- **R3:** the next test run, when it starts, removes a killed run's per-run folders (the code-graph daemon folder,
  `gov-cbm-<uid>-*` or a launched session's short `c???` folder, and the `gov-path-*` links folders) whose owner is
  gone. The owner check must hold across pid namespaces (each sandboxed command runs in its own; the designer's D-15,
  settled (a) by the lead: a lock the kernel releases when the owner dies). Never a link or its target, a regular file,
  another user's folder, a folder of another name, the shared `/tmp/gov-cbm-<uid>` or anything in it,
  `/tmp/gov-launch-*`. A folder with no owner record is kept unless older than 24 hours (DEC-902). A clean-up that
  cannot remove never fails or delays the run.
- **R5:** a lead (`gov launch orchestrator|lead`) gets the launcher's own `GOV_STORE` exactly as a worker does (W2-116
  S3: the main repository's `integration_store`, as written; an unusable setting refuses the lead), never the parent's;
  `TERM` and `TMPDIR` are not passed (S5's list; `-p` sessions; DEC-743 item 7). Judged within S5's "the launcher's
  own values", so no DEC-105 package.

## What to review
- **The branch:** `w2/W2-56-f` in `/home/usain/gov-os-worktrees/W2-56-f`, head `HEAD_SHA`, from `w2/integrate` at
  `336828354`. Read `git diff 336828354..HEAD_SHA`: the designer's cases (`tests/acceptance/W2-56/`, `473e8ad828d5`:
  `test_w2_56_r3_sweep.py`, `test_w2_56_r5_lead_store.py`, the support and probe files, the README's new section) and
  the engineer's change (`src/gov/codeintel/__init__.py`, `tests/conftest.py`, `src/gov/launch/launcher.py`, the unit
  tests, the CIT-E).
- **The runs:** RUNS_LINE

## Check
1. **R3, nothing live is ever removed:** a live run's folder (same or another pid namespace, an xdist worker's, a
   nested run's, a run of older code without a record) cannot be taken for dead; the lock is held for the whole run
   (from before the folder could be swept until the run's own removal), and not lost when a child process exits or
   when the controlling process starts xdist workers. A race between two runs starting together.
2. **R3, only the right things are removed:** names, owner, links (no link followed, `lstat` before any removal), the
   shared places; and what a removal of a 0500 tree does.
3. **R3, the conftest change:** it reaches every run of the repository; does it cost a run measurable time, or change
   anything else a run does?
4. **R5:** the parent's `GOV_STORE` cannot reach a lead by any path; the lead's settings env is exactly role, ticket and
   (where set) the store; a worker's launch is unchanged; a lead launch that used to start and now refuses (an unusable
   setting) is the intended fail-closed.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`, and the evidence that would reverse it
(DEC-1014). A finding is `scope: in` only if it concerns R3 (S1) or R5 (S5).

## Write and return
- **You write nothing** in any tree; run nothing that writes outside your own temp folder (one test file at a time,
  read-only, `-p no:cacheprovider`, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-56-f/src`, the sandbox's short
  `TMPDIR`). Single simple Bash commands (DEC-1080). Never the full suite. The real cases need a session outside your
  sandbox: read the lead's results above instead.
- The hidden-half rule: never open the evaluation sets' hidden half or the run folders outside this repository, as
  `EMG-common.md` names them. No GPU, network or installs. Every wait and stop by pid only.
- **Search again once (DEC-1092 (1)).**
- **Your record is your session's final message**, in full: the twelve labelled fields of `EMG-common.md` (sandbox and
  `ps` checks first), your answers to checks 1-4, every finding with its lines and `scope: in|out`, and at the end the
  fenced `verdict` block in DEC-1010's form:
  `{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [...]}, {"kpi": "S5", "verdict": "pass|fail", "findings": [...]}]}`
