# W2-149 — the engineer's brief, round 2: the review's blocking finding F1 and four rows (DAEO-52ku)

You are the engineer for **W2-149** (`.tickets/DAEO-52ku.md`), round 2. Round 1 built
`governance/project/orchestration/tools/indep_launch.py` (head `8d4569bfef3c` on `w2/W2-149`): `gov accept W2-149`
77 passed, 0 failed, 3 live skipped; the CTO ran the 3 live cases outside the sandbox: 3 passed. The independent review
(round 1 of at most two, DEC-1010) passed every KPI line but **S12**, on **F1**, and listed rows. Read the ticket, then
`docs/changes/W2-149-evidence.md` and the script: you change only what is below. Profile FULL.

## The review's findings you fix (the reviewer's words, shortened)
- **F1 (blocks; S12, code 22): for a stopped session the trace check returns 0 without running.** `count_traces`
  returns 0 when the session id is None (`indep_launch.py:845-847`), and `read_session` returns None whenever the
  session's output does not parse (:826-827); a `claude -p --output-format json` killed by `timeout` writes nothing, so
  every timeout reports `traces: 0` unchecked, though a killed process is the likeliest to leave `session-env/` or
  `todos/` behind. **The CTO's fix (settled, DEC-1101 (2)-(3)):** the script draws the session's id itself
  (`str(uuid.uuid4())`) and passes it with `--session-id <uuid>` (a flag Claude Code 2.1.318 offers; S10 says the line
  "carries" its flags, so one more closing flag amends nothing); it records the drawn id only as the trace check's key
  (never printed: the counts stay counts). `traces` = the entries named by the drawn id **plus** those named by the
  id the session reports, when it reports a valid one that differs (count each entry once). So the check always runs.
- **F6 (S12): the canary's own traces are never counted.** Do the same for the canary: draw its id, pass
  `--session-id`, count its traces (drawn and reported ids) into the same `traces` total. A canary trace makes the run
  report 22 as a session trace does (the canary's own code 16 still wins when the canary fails).
- **F3 (S4/S5): `GOV_INDEP_TEST_HOOK` runs in real runs and leaves no record.** Record it: `WALL.json` gains
  `"test_hook": true|false` and `launch.log` a line `test_hook set` when it is set. (No refusal: the cases use it in
  real runs on planted roots.)
- **F5 (S14/S16): a rejected run can leave an empty folder.** The labeller's `labels/` folder in the sealed folder and
  writer round 1's set folder are made only after every check of the delivery has passed (:954, :1011-1018), so a
  rejection leaves nothing.
- **F8: the result and counts schemas are read from the working tree.** Record each schema's sha256 in `WALL.json`
  (`schema_sha256: {file: sha256}` for the counts schema and the brief's result schema), read once and used from those
  bytes.

Not in this round (rows for the CTO, do not change): F4 (the expected-file count), F7, F9, F10, F12; F2 and F11 are
outside this ticket.

## Constraints
- **The acceptance cases must stay green:** `gov accept W2-149` 77 passed, 0 failed (3 live skipped). The stub
  `claude` in the cases already parses `--session-id` as a value flag but reports its own session id (planted or
  random), not the one passed: so the "plus the reported id" rule is what keeps S12's planted-trace case at 1.
- Add unit tests for each fix to `tests/unit/orchestration/test_w2_149_indep_launch.py`: a session that times out with
  a trace planted under the drawn id (22, `traces` 1); a timed-out session with none (0, checked); a canary trace;
  `test_hook` recorded; a rejected labeller and writer leaving no folder; the schema hashes in `WALL.json`.
- Update `docs/changes/W2-149-evidence.md` with a "Round 2" section: each finding, the fix, the tests.

## Where you work
- `/home/usain/gov-os-worktrees/W2-149`, branch `w2/W2-149`. Your paths: the ticket's `allowed_paths`
  (`indep_launch.py`, `indep-schemas/**`, `tests/unit/orchestration/test_w2_149*`, `docs/changes/W2-149-evidence.md`).
- **You never read `tests/acceptance/W2-149/`** (G-14; DEC-820 (c)): only `gov accept`'s results. The exclusion line
  (DEC-1093 (2)) by base name: `--exclude-dir=W2-149` for grep, `!tests/acceptance/W2-149/**` for Grep and Glob,
  `-path '*/W2-149' -prune` for find; searches from relative paths inside the worktree. If a search shows you a line
  of the cases anyway, stop reading it and say so in your return.
- The template folder `governance/project/indep-walls/`: read it with the Read tool; never name it in a Bash line.

## Verify
- Through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
  with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-149/src`: your unit tests (with `--optin=lifted --optin=breadth`, so
  every parametrized row runs); then `python3 -m gov.cli.main accept W2-149 --root /home/usain/gov-os-worktrees/W2-149`.
- Commit as you go.

## Rules
- The hidden-half rule: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, `~/gov-os-wall-trees/`,
  `~/.claude/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder of a real tree. No real `claude`
  session, no GPU, no model, no network, no installs.
- DEC-1080: Read and Grep tools; one simple command per Bash call; no `cd … &&` chains.
- Do not merge `w2/integrate`. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- Waits and stops by pid or pgid only, never a name match (L-0075).
- **Commit** on `w2/W2-149` with
  `--trailer "Task: DAEO-52ku" --trailer "Implements: DEC-1101" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished. Keep to the estimate: a short round (about an hour).

## Return
Your whole return is your session's **final message**, in full (the launcher keeps it in this worktree's log): the
twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first), each finding's fix with its lines, `gov
accept W2-149`'s counts, the unit counts, your head commit, and every red named.
