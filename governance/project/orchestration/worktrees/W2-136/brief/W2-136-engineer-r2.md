Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-136/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-136 — the engineer's second pass (DAEO-p3ln)

Your first pass is built (`69aa361a`; `gov accept W2-136` 74/76). The CTO ran the S9 cases and settles the two reds
(delegated, under DEC-1088 (5)(a)). The failures, as the CTO saw them (you still never read `tests/acceptance/W2-136/`):

- `test_s9_the_launcher_starts_a_lead_the_check_admits` and `test_s9_the_launcher_writes_an_override_in_the_launch_log`:
  `launcher.launch(root, "orchestrator", ticket, [])` passes the plan's check (the override line is written) and then
  stops at `launcher.py:321`: "'orchestrator' is not a worker role". **Settled:** a lead role (`orchestrator`, `lead`)
  admitted by the check goes on to the session start, with the lead's settings: `GOV_ROLE=orchestrator`,
  `GOV_TICKET=<ticket>`, no sandbox, as the dispatcher starts a lead today
  (`.gov-runtime/scratch/orchestrator/dispatch/launch_now.sh`: `claude -p --model claude-opus-5-5 --effort high
  --output-format json --permission-mode acceptEdits --settings '{"env":{"GOV_ROLE":"orchestrator","GOV_TICKET":...}}'`).
  If the settings builder (`build_settings`) cannot express a lead without weakening a worker's settings, build the
  lead's settings in a separate function and say so. Worker launches stay exactly as they are.
- `test_s9_guard_a_worker_launch_never_consults_the_plan` fails only when the calling session has `GOV_ROLE=orchestrator`
  and a `GOV_TICKET` (the CTO's own session: `DAEO-sdxk`): your `launch()` checks the **caller's** ticket
  (`launcher.py:309-310`). **Settled: remove that clause.** S9 is about the lead being launched (the `role` and
  `ticket_id` arguments), never the caller's environment: otherwise every worker the CTO or a lead launches would be
  refused (W2-00 is in no batch). A worker launch never consults the plan.

## Do
- The two changes in `src/gov/launch/launcher.py` (your paths); unit tests in `tests/unit/launch/test_w2_136*`: a lead
  admitted reaches the session start with the lead's env; a lead refused starts nothing; a worker launch from a session
  with `GOV_ROLE=orchestrator` and a `GOV_TICKET` set never consults the plan.
- Run your unit tests and `tests/unit/launch` through the heavy slot (once with `GOV_ROLE=orchestrator GOV_TICKET=DAEO-sdxk`
  in the environment, once without), then `gov accept W2-136` again.
- The exclusion rule for `tests/acceptance/W2-136/` in every search (DEC-1093 (2)). Every run you start has finished
  before you end. The rules of your first brief hold. Commit with
  `--trailer "Task: DAEO-p3ln" --trailer "Implements: DEC-1088" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

Return the twelve fields, short.
