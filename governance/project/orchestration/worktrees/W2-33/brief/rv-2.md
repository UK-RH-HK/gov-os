Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-33/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief rv-2: narrow independent check for DAEO-lrre (W2-33), after review round 1, read-only

You are a fresh, read-only reviewer (role independent-auditor). **You write nothing**: no file, no commit. Your last
message is your report.

Review round 1 (another session) passed head `3b3a90d74c3e` of w2/W2-33 with 7 findings, none blocking. After it, two
commits landed on the branch, in /home/usain/gov-os-worktrees/W2-33:
- `c4b977161` (product-spec): a fix for three older-suite reds the change had caused. The CTO's file now names the
  kernel templates a lead's brief is built from. `engineer.md`'s Purpose moves to line 5, with the defaults lines
  after it.
- `1221ee0e4` (the lead): the CIT-P `docs/changes/W2-33-CIT-P.md` updated with the final hashes, the full list of reds
  the land brings until the copies ACT (round 1's R1), and the fix.

Check only `git diff 3b3a90d74c3e 1221ee0e4` (expect HEAD = `1221ee0e4`; if it is not, say so):
1. Does the fix change anything beyond what is stated? Is every line form still once, whole and at column 0 in
   `engineer.md` and `orchestrator.md`? Run `tests/acceptance/W2-33` read-only to check (see below).
2. Is the new sentence in `orchestrator.md` true? Check it against `template/governance/kernel/templates/`
   (`role-lead.md`, `brief.md`, `brief-lead.md`) and DEC-1050 in docs/DECISION_REGISTER.md (grep by id). Does
   `template/.rulesync/subagents/orchestrator.md` still equal
   `gov.adapters.portability.compose(root, 'orchestrator')`? Run the one-line Python check, read-only.
3. Does the fix bring any fail-open or work-losing statement?
4. Do the CIT-P's sha256 values equal the files at `3df1ac2deb1b` (before) and `c4b97716164e` (after)? Does its §4
   name every red the land brings? Compare with
   /home/usain/gov-os-worktrees/W2-33/.gov-runtime/scratch/lead/log/verify/parallel.xml (the full-suite run on
   `3b3a90d74c3e`: 50 failures). Three of those failures are W2-128's, which the fix turns green.

Run tests only read-only, through the gate, with the sandbox's own TMPDIR:
`bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-33/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-33/src python3 -m pytest tests/acceptance/W2-33 tests/acceptance/W2-128 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
Threat model (DEC-801, DEC-808): honest mistakes in ordinary work. A finding fails the check only when it is in scope,
reachable in ordinary work, and fails open or loses work. Anything else is a recorded row.

## Return (your last message)
The twelve fields, each a labelled line ("none" where nothing). Then the findings (N1..Nn: behaviour, path:line,
severity, in scope or a row, fails open or loses work), the answers to 1-4, then exactly:
```verdict
verdict: PASS or FAIL
probed_commit: <the full 40-character hash>
findings: <n>
```
and `guard_refusals:`.
