
## W1-29 residuals (session hooks, 2026-10-07)

- **Built:** SessionStart and PreCompact add W1-29's behaviour to W1-49's hooks (W1-49's suite unchanged and
  green); Stop and SubagentStop are new. SessionStart injects the `gov context --brief` text and the ready
  tickets for a session with a ticket, within the 10,000-character cap, optional parts cut first. PreCompact
  and Stop write a checkpoint record when the session has a ticket; a session with none writes nothing.
  SubagentStop refuses, once, a return that lacks any of the twelve fields or holds an empty one, in JSON or
  in text.
- **Stop and SubagentStop are not registered.** They run only once the owner adds them to the project's
  settings file (the lines are in the lead's return, `W1-29-lead-run3.json`, and were given to the owner).
  The installer may need the same lines for an installed project: for the adoption ticket.
- **KPI line 3 is not met in its literal reading.** "A checkpoint is written when the session's context
  utilisation passes the configured threshold": no hook receives the utilisation. What exists: a checkpoint at
  every stop (once Stop is registered) and at every compaction, and W1-25's watchdog marks a checkpoint stale
  on utilisation when a caller gives it the figure. For the owner.
- **The auto-compact threshold (DEC-208) is not set.** The Claude Code command line has `--autocompact` (seen
  in its help text by the orchestrator); the lead names a settings key `autocompact` with the value 300000,
  which nobody verified. The settings file is the owner's. Until it is set, the KPI's second half holds: the
  orchestrator's CONTEXT_CHECKPOINT stop stays.
- **Checkpoint records written by the hooks are untracked files** under `docs/checkpoints/(ticket)/`. No code
  commits them. A hook is a process of its own, not a tool call: its write is not decided by the guard, so a
  worker whose role may not write `docs/**` still gets these files written in its tree. What becomes of them
  (commit, ignore, clean at close) is open; `gov close` (W1-30) writes its closing checkpoint the same way.
- **"Preserves the open decisions and the loop counts" holds for the orchestrator only,** through W1-49's
  checkpoint file and its RESUME HERE section; a worker's checkpoint record holds its ticket and a next action.
  A session inside a loop never sees a count (DEC-096).
- **`src/gov/hooks/stop.py` and `subagentstop.py` are copies** of the two files under
  `template/governance/kernel/hooks/`; a case pins that they are identical.
- **A case's rewrite is labelled "owner correction"** (`test_auto_compact_threshold`): it was the
  orchestrator's finding that the case could not fail, not an owner's correction. The label stays in the test
  text (the orchestrator does not edit tests); this line corrects the record.
- **Records:** the merge commit `478a8ed0` on the branch carries no `Role:` trailer. Source S0a-G-09 was
  passed to the third start by the orchestrator (DEC-432).
- **Learning metrics:** three starts (the first replaced W1-49's hooks and returned DONE with 65 of W1-49's
  cases red; the second was accepted except six points found by reading each KPI clause against the case
  table); 33 cases; 1 case rewritten after implementation, 5 added after it; about 210 lines of source against
  an estimate of 180, plus 104 lines of copies; two reviews.
- **Regression at `ee5eaf40`:** every suite green. One W1-16 case
  (`test_this_repository_is_not_indexed_by_the_run`) failed in the full run because a tool call of the
  orchestrator's own session wrote a containment snapshot under `.gov-runtime/` while the case watched that
  folder; it passed alone. The real freeze-mirror folder was unchanged by the run.
