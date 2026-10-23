# W2-66 (DAEO-c1uz) lead checkpoint

## State
- Run 1. Started 2026-10-23. Base head c2d539c6 on w2/W2-66, tree clean at start.
- Identity checked: GOV_ROLE=orchestrator, GOV_TICKET=DAEO-c1uz, worktree /home/usain/gov-os-worktrees/W2-66.
- pytest-timeout NOT installed at start (`import pytest_timeout` fails): the per-test limit KPI goes PACKAGES if still missing when the engineer reaches it (DEC-892 b).

## Decided (by the brief / register)
- W2-07 merges first; this ticket returns DONE unmerged; run 2 merges w2/integrate back, re-verifies, fresh FULL probe.
- Never write governance/project/path-map.yaml; its test_inputs key moves into the test map; its removal is the orchestrator's edit (name in return).
- Designer's W1-30 file: the ticket names `tests/acceptance/W1-30/test_w1_30_regression*`, but the named test
  `test_regression_includes_other_acceptance_folders` lives in `tests/acceptance/W1-30/test_w1_30_close.py:369`
  (discovery to report). W2-07's designer also revises `test_collection_error_refuses_close` in that same file.
- Interface: the designer fixes the observable interface (test-map keys, evidence block fields, nightly command, base record)
  and returns it; the lead passes the interface (not test code) to the engineer.

## Next
1. td-1 (independent-test-designer, xhigh, sandboxed via gov launch): brief .gov-runtime/scratch/lead/briefs/td-1.md, log log/td-1.json, tripwire-before-1.json.
2. Red check; 3. engineer; 4. verify; 5. review (A3, max); 6. fixture trial in docs/research/W2-66-scoped-close.md; 7. return.

## Loop count
- 0

## Workers
- (none yet)

## Guard read refusals counted
- lead: 0
