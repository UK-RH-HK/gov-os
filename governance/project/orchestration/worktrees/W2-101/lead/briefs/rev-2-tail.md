
- **How reviews converge (owner, standing, DEC-1010 item 1):** a finding blocks only if it is in scope, reachable in
  ordinary work, and fails open or loses work; everything else lands as a recorded row. At most two review rounds.
  READY is computed by code: you return a structured verdict per KPI line, a fenced `verdict` block:
  `{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`.
  A lead never writes a verdict over a reviewer's.

Every finding carries `scope: in` only if it concerns this ticket's change (the three skill folders, their copies, the
check script, scenarios, records and summaries) or the suite's fidelity to the KPI lines.

## Write and return
- You write nothing in any tree (your own TMPDIR only). Single simple Bash commands. No shell variable or `$(…)` as a
  write target, no here-document, no `bash -c`. Every wait by pid only.
- Reads (DEC-820): open, except secrets and keys (never read or printed), the held-out qualification material's
  contents, and the hidden half of any evaluation set: never open anything under `~/gov-os-eval/`, an evaluation set's
  root, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder. You search with the Read and Grep tools, naming
  the folder a search starts at; search once more in other words if the first does not answer, then say "not found".
- Refused twice for the same call: stop and say so; never work around a refusal by another tool or form.
- Commit hashes as 12 digits, never the full 40. There is no token cap.
- **Your record is your session's final message**, in full: the twelve labelled fields first (task, status,
  work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved,
  recommended_next_action), your session id and the probed commit in `evidence`; your answers to checks 1 to 6 (and 7
  if run); every finding with its two lines and scope; then `REVIEW_MD_BEGIN`, the review record in markdown,
  `REVIEW_MD_END`; at the end the fenced `verdict` block
  `{"kpis": [{"kpi": "w2-101-narrow-r2", "verdict": "pass|fail", "findings": [...]}]}`, each finding
  `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 30 minutes.
