---
type: probe
task: DAEO-1k7y
reviewer_session: 9d33c85b-9d9d-4712-a363-74c1e8bb4c9a
implementer_session: 2e88c74b-6fd2-4476-bd00-c6985e19bc36
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 170cae9b18368922f33122846c8d1c2dc6665ed6
decisions_applied: [DEC-966, DEC-1050, DEC-866, DEC-1010, DEC-953]
---

# Probe record: W2-177, the six W2-96 signal reds

A fresh independent-auditor session (`9d33c85b-9d9d-4712-a363-74c1e8bb4c9a`) ran on Opus at high effort, class C2 on
FULL, with read-only tools. It probed head `170cae9b1836` of `w2/W2-177` and wrote nothing in the tree. The tree was
clean when it started and when it finished, and the tripwire shows no change in it. The implementers were:
- engineer eng-1 (`2e88c74b-6fd2-4476-bd00-c6985e19bc36`): S1's evidence (49eb39a9e), the red-first cases (3f1401596),
  cause (A) in `runner.py` (0ca819544), cause (B) in the unit launcher `w2_96_reap.launch_gov` (003f3d84e,
  `Rewrite-Reason`), and S2's counts (f5f050c87);
- test designer td-1 (`a0cc944e-c34e-427b-b311-6532d82128bc`): the revision P-W2-177-1 (a) of the W2-96 and W2-56
  acceptance supports (8f40881d9, `Rewrite-Reason` naming DAEO-1k7y and DEC-866).

This is review round 1 [DEC-1010], and its verdict is **PASS**: 2 findings, both minor, neither blocking.

## What was probed

- **Cause (A), product code (`runner._run`).** The child keeps the caller's `PYTHONUSERBASE`, and every other `PYTHON*`
  variable stays dropped. The drop came in with 9859695c8 (W2-96), so that the caller cannot steer the run or its
  caches. Keeping the user base leaks nothing the drop was there to stop: `HOME`, which is passed through, already
  selects that site.
  - Unset: nothing is added, and a unit case covers it.
  - Empty: `site` treats `""` as unset, the same as before the change.
- **Cause (B), the unit launcher and the new cases.**
  - Mutant B (the launcher fix reverted alone, real-home background form) fails all six cases and the two launcher
    cases.
  - Mutant A (the runner fix reverted alone, empty HOME) fails 4 of the six, R11's three parameters and new case (A).
  - The base before the fix, with the new file added, fails the six and 3 of the 5 new cases, so the new cases were
    red first.
- **The revision.** The reviewer ran R11's premise case, R11 and R12 in a non-interactive background job (SIGINT
  ignored, empty HOME):
  - On the support before the revision (ee18860f7): 2 failed. The premise case got `'1 1 0'` where it expects
    `'1 0 0'`, the nightly's output, and R12[SIGINT] also failed.
  - On the head: 8 passed.

  The premise case still proves that an ignore given at the start is inherited across `exec`. It is now stricter: it
  also proves that the other two signals are at default. No assertion, timeout, marker, skip or parameter changed.
- **S1.** The cause is named with counts per start form (empty HOME, real HOME, `setsid` background, background job,
  real-HOME background). The reviewer reproduced (B) on its own.
- **S2.** The head was run in setsid-bg (1 run), real-home-bg (3), empty-home (3) and bg-job (3): every run 14 passed,
  none skipped or deselected. The evidence's ten runs per form are on disk for the lead's four forms.
- **S3 / F1.** The diff from c62b66bb4 weakens no assertion. `skip_known.json` was last modified 2026-10-27 and has no
  W2-96 or W2-56 entry. Both test rewrites carry a `Rewrite-Reason`. The S1 evidence commit comes before the first
  code or test change.
- **F2.** `git diff --name-only c62b66bb4 170cae9b1` lists 6 paths, all in allowed_paths.
- **Commits.** Each carries `Task: DAEO-1k7y`, and `Implements:` uses only ids from the ticket's sources.

## What it found (2, both minor; none blocking, none fail open, none lose work)

| id | KPI | where | finding | the lead's triage |
|---|---|---|---|---|
| m1 | S2 | `tests/unit/accept/w2_96_reap.py:150-151` | `_ignore` sets the named signals to SIG_IGN twice: once in the loop over the three, again in the old loop over `ignore`. | No effect for any caller today, and the old loop is what keeps a named signal outside the three ignored. No change in this ticket. A follow-up row if wanted: a comment, or keep the old loop only for signals outside the three. |
| m2 | S1/S2 | `.gov-runtime/scratch/acc-forms/lead-after/counts.txt:1-3` (scratch, not committed) | Three runs labelled "fg" began with SIGINT ignored: the lead started the whole script detached, so they were background starts. | The evidence's fg row correctly cites `lead-after-fg/` (SIGINT at default). This is a scratch label only; the evidence says it. No change. |

Out of scope, named by the reviewer as a risk: `_popen` now always passes a `preexec_fn`. In a multi-threaded process,
fork plus a hook could in theory hang. The unit launcher always used one, and the verify's 4270 tests ran green under
xdist.

## Verification at the probed head's parent (`7cde9429ea0c`; 170cae9b1 changes only the evidence)

- `lead_verify.sh` (a `setsid` background start, empty HOME): `RED parallel exit 1 in 1045 s (4270 tests 1 failed 0
  errors 10 skipped)`.
  - Run 1's five reds pass: the four W2-96 acceptance cases and W2-02's core-schema case.
  - The one red, `tests/unit/orchestration/test_w2_149_indep_launch.py::test_f6_a_failed_canary_keeps_its_16_and_counts_its_trace`
    (`14 == 16`), is outside this ticket's paths. It passes alone in the foreground and in the background form, both on
    this head and on w2/integrate 6c9a5bb52: load-sensitive, not a shared base red. It is not in `skip_known.json`.
- `gov accept W2-177`: `ACCEPT_NO_MAP`, because `tests/unit/accept/` has no README map and none is in allowed_paths.
  The ticket's acceptance is the named cases (S2).
- `gov accept W2-96`: pass, 251/0/0.
- `gov accept W2-56` (DAEO-wnnz): 292 passed, 0 failed, 4 skipped. Its one failing line, success-13, holds only the
  real-sandbox case, which is skipped here by design.
- The acceptance start forms after the revision, 3 runs each: fg, setsid-bg and bg-job all 29 passed in every run.
  Before the revision, setsid-bg had 6 failed.

## Judgement

PASS. The diagnosis is reproduced, both fixes are caught by their mutants, the revision does not weaken R11's premise,
and F1 and F2 hold. The head to land is this record's commit on `w2/W2-177`.
