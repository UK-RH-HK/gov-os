Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-136/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-136 — the independent review (DAEO-p3ln), one round

You are a fresh, read-only independent reviewer. Review **W2-136** (`.tickets/DAEO-p3ln.md`: read it in full, with its
TESTS-READY and D-1 notes): `gov plan` (the dependency map, the launch batches) and `gov launch`'s check of a lead
against the approved plan (DEC-1088; `governance/project/orchestration/packages/LIFT-1/DEPENDENCY-MAP-1.md`).

## What to review
- **The branch:** `w2/W2-136` in `/home/usain/gov-os-worktrees/W2-136`, against `w2/integrate` (`git diff w2/integrate...w2/W2-136`):
  - `src/gov/plan/**`, `src/gov/launch/plan_check.py`, `src/gov/launch/launcher.py`;
  - the unit tests under `tests/unit/plan/` and `tests/unit/launch/test_w2_136*`;
  - the designer's `tests/acceptance/W2-136/`;
  - `docs/changes/W2-136-evidence.md`.
- **The CTO's settlements on the second pass:**
  - (1) the launcher never checks the calling session's own `GOV_TICKET`, only the `role` and `ticket_id` it launches;
  - (2) an admitted lead (`orchestrator` or `lead`) starts with `build_lead_settings`: `GOV_ROLE=orchestrator`, `GOV_TICKET`, no sandbox, as the dispatcher's `launch_now.sh` starts a lead today. Worker launches are unchanged.
- **The engineer's runs:** `gov accept W2-136` 76/76 with and without `GOV_ROLE=orchestrator GOV_TICKET=DAEO-sdxk`; the unit tests 154/154 both ways.

## Check, against each KPI line S1 to S10 (S11, the timing, is the CTO's)
- **S3:** overlap errs toward overlap. Can two tickets whose writes the guard would let both touch ever land in one batch?
- **S4:** the output is deterministic in any file order.
- **S7:** nothing is written without `--ready`.
- **S9:**
  - a lead outside the batches, or with unmet waits, starts nothing, and the refusal names what it waits for;
  - an override is logged;
  - **a worker launch never consults the plan, from any caller**, including a session with `GOV_ROLE=orchestrator` and a `GOV_TICKET` set;
  - does the new lead path weaken any worker launch's settings or checks? Does it start a lead with anything more than the dispatcher's lead line gives it?
- **S10:** no close, landing, claim, readiness or hook module imports `gov.plan`.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.

## Write and return
- **Write** your record at `/home/usain/gov-os-worktrees/W2-136/docs/probes/W2-136/review.md` (inside the worktree; create the folder). It is the only file you write; do not commit. End it with the fenced `verdict` block, `{"kpis": [{"kpi": "S1", ...}, ... "S10"]}`.
- **Run** nothing that writes elsewhere. You may run the tests read-only through the heavy slot. No GPU. Use single simple Bash commands (DEC-1080). The hidden-half rule holds. Every run you start has finished before you end.
- **Return** the twelve fields: your verdict per line, and every finding with its two lines.
