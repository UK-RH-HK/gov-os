# Lead checkpoint — DAEO-9nys (W2-67), run 3 (rounds 2 and 3, DEC-914)

## RESUME HERE
- State (2026-10-24): run 3 started. Merge 6d44fc80 of w2/integrate (6f94b16f), tree equal to git's merge-tree; merge touches none of the ticket's own files (DEC-895: no probe redo). Rebuild-4 green (exit 0, log/rebuild-4.json).
- W1-05's nested run (DEC-914 item 3, DEC-718): gone, retired by W2-70's f409ad97; the only `pytest` left in W1-05 is a guard-input string (test_w1_05_live_hooks.py:145), never run. No row.
- The 13 W1-30 cases: I2 §2.7 weak-test table (disposition x2, close.py trailer x2, acceptance x2, containment, task-exact, regression x3, receipt hash, owner decision checker). test_close_runs_containment_check is P-I2-5 (retire, undecided): left.
- W2-50: the acceptance file is unchanged since W2-50 (878467c9); W2-69 changed the scan code and the unit scale cases. Limit is src constant _TIMEOUT_S=60 (+len/_FLOOR) in src/gov/secrets/__init__.py: no declared short limit in code; a test-only means or a package.
- Ride-alongs: TD4-A = review F3 (KPI 4 static guard f-string, acceptance W1-27) → td-6; P1 option A (time-limit case's own TMPDIR) → engineer; TD1C-A (fixtures remove /tmp/gov-cbm-<uid>/<sha256(root)[:16]> folders they make) → an old-form test designer (td-8) since the sandbox has /tmp/gov-cbm read-only.
- Plan: td-6 (sandboxed, xhigh): W1-30's 13 + W2-L420 + TD4-A + rm plant. td-7 (sandboxed, xhigh): W2-50's large-store and hang cases. td-8 (old form): TD1C-A. Red check. eng-4 (sandboxed, high): 15 nested-run functions + P1. Verify (verify.sh, label r3). No review (P-W2-67-R23).
- Loop count: 0 implementer iterations in run 3.
- Next: tripwire snapshot 12, launch td-6.
