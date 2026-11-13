Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-177/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief eng-1: engineer for DAEO-1k7y (W2-177), profile FULL, class C2

You fix the six W2-96 signal reds in `gov accept`'s unit cases: diagnosis on record first (S1), then the smallest fix
(S2, S3). The lead has a diagnosis from probes (below); you confirm it with counts, record it, then fix.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-177 |
| branch | w2/W2-177 |
| allowed paths | src/gov/accept/**, tests/unit/accept/test_w2_96_run2.py, tests/unit/accept/test_w2_96_review3.py, tests/unit/accept/test_w2_96_review4.py, tests/unit/accept/w2_96_reap.py, tests/unit/accept/test_w2_177*, docs/changes/W2-177-evidence.md |
| ticket (KPIs S1-S3, F1-F2, non-goals) | the `gov context` packet at the end of this brief (its `ticket_text`) |
| code | src/gov/accept/runner.py (`_run`, line ~511-594), src/gov/accept/command.py |
| the test launcher | tests/unit/accept/w2_96_reap.py (`launch_gov`, line 132-157) |
| start-forms script (the lead's; run it, do not edit it) | /home/usain/gov-os-worktrees/W2-177/.gov-runtime/scratch/forms/run_forms.sh (+ inner.sh beside it) |
| W2-96 acceptance (read only; never edit) | tests/acceptance/W2-96/w2_96_support.py (`_popen`, line 1380), test_w2_96_at_run_2.py (premise R11, line 375), README.md lines 29-35, 455-456 |

## The six cases (red in 13 of 14 lead verifies and in the nightly 20261112-0404)
1. test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_clean_up_is_held_back[signals0]  (nightly: 2.4 s)
2. test_w2_96_run2.py::test_w2_96_r9_r12_a_signal_during_the_run_then_more_during_the_clean_up[2-more0]  (60 s, `started` never written)
3. test_w2_96_run2.py::test_w2_96_r9_r12_presses_until_gov_ends_never_kill_it[kinds0]  (2.4 s)
4. test_w2_96_run2.py::test_w2_96_r9_r12_ctrl_c_during_the_run_stops_it  (60 s)
5. test_w2_96_review3.py::test_w2_96_r14_a_stopped_run_keeps_128_plus_the_signal[True-2]  (60 s, gov never ends)
6. test_w2_96_review4.py::test_w2_96_r16_an_own_session_orphan_is_reaped_before_a_stopped_run_cleans_up[2]  (60 s)
The nightly's failing output: /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/nightly/20261112-0404/parallel.txt
(lines 270-560) and run.txt (lines 13-27). If you cannot read them there, the summary above is what they say.

## The lead's diagnosis (confirm or refute it with counts; never take it on trust)
(A) An empty HOME. `runner._run` (runner.py:539) builds the child's environment without every `PYTHON*` variable,
`PYTHONUSERBASE` included. pytest is installed in the user site (/home/usain/.local/lib/python3.12/site-packages), so
under an empty HOME the child `python3 -m pytest` cannot import pytest: the run ends at once as a crash, the planted
test never writes `started`, and the case's 60 s wait fails. The lead reproduced case 4 in the foreground with SIGINT
not ignored (`1 failed in 60.15s`, at `_wait_for(started)`). With the real HOME, `~/.local` is found and the cases
pass. W2-96's own acceptance README (lines 32-35, 455-456) gives the run `PYTHONUSERBASE` as the way pytest is found:
the runner dropping it is a defect of `gov accept`'s, so the fix is in the code: keep `PYTHONUSERBASE` in the child's
environment (nothing else of `PYTHON*` changes; `PYTHONDONTWRITEBYTECODE` and `PYTHONPATH` stay as they are).
(B) A background start. `lead_verify.sh` (line 30: `setsid bash ... &`) and the cron nightly (`nightly_restart.sh`
line 181: `bash -c '...' &`) start pytest as a background job of a non-interactive bash, which begins with SIGINT
(and SIGQUIT) ignored. `w2_96_reap.launch_gov`'s `preexec_fn` only sets the signals named in `ignore` to SIG_IGN; it
never sets the others back to SIG_DFL, so gov starts with SIGINT ignored, and gov keeps an inherited ignore (R11, by
design, `test_w2_96_r11_an_inherited_ignore_is_kept`): a SIGINT changes nothing, and the SIGINT cases fail. The
lead's probe: `python3 -c ... & wait` inside a bash script prints SIGINT ignored = 1; `setsid python3 ... & wait` = 1;
in the foreground = 0. The fix is in the tests' launcher: `launch_gov`'s `preexec_fn` sets each of SIGINT, SIGTERM
and SIGHUP to SIG_IGN when named in `ignore`, and to SIG_DFL otherwise. `gov accept` keeps the inherited ignore
unchanged (R11 must stay green).
The W2-96 acceptance support's `_popen` has the same gap as (B) (it only ignores, never resets): that is NOT yours.
Name it in the evidence and in `discoveries`; the lead packages it to the CTO for a test designer's revision.

## Steps (in this order; commit after each)
1. S1 baseline, before any change: `bash /home/usain/gov-os-worktrees/W2-177/.gov-runtime/scratch/forms/run_forms.sh before 2`
   (four forms: empty-home, real-home, setsid-bg, bg-job; two runs each; a red run takes about 5 min, so run it
   detached: `bash .../run_forms.sh before 2 > /home/usain/gov-os-worktrees/W2-177/.gov-runtime/scratch/forms/before.out 2>&1 &`
   and read `.gov-runtime/scratch/forms/before/counts.txt`; never a sleep loop: wait with
   `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/wait_for.sh <file>` if you
   have an exit file, else check the counts file between other work). Read which cases fail in each form from
   `.gov-runtime/scratch/forms/before/<form>-<i>.txt`.
   Write docs/changes/W2-177-evidence.md: the cause (A and B, each with its evidence: file and line, the probe, which
   of the six it explains in which form), the four start forms and each one's counts, why the W2-110 verify and the
   real-HOME alone runs passed (say "not established" where you cannot show it), the nightly's "alone at load 18"
   (nightly_alone.py runs inside the backgrounded nightly: check its start form and HOME, read-only), and whether
   W2-56's two SIGINT ending cases (tests/acceptance/W2-56/test_w2_56_endings.py, read only; a non-goal to fix)
   share cause (B). Commit the evidence alone, before any code or test change.
2. Red first: tests/unit/accept/test_w2_177_start_forms.py with (a) a case that `gov accept`'s child is given the
   caller's `PYTHONUSERBASE` (deterministic: capture the env `subprocess.Popen` receives in `runner._run`, or an
   equivalent that does not depend on where pytest is installed), and (b) a case that `launch_gov` starts gov with
   SIGINT, SIGTERM and SIGHUP at SIG_DFL when the caller (the test process) has them ignored and `ignore` is empty,
   and with the named ones ignored when given (restore the test process's handlers in a `finally`). See both red;
   commit.
3. Fix: runner.py (A), w2_96_reap.py (B). Smallest change. See step 2's cases green; commit the code and the test
   launcher separately; the launcher commit carries a trailer `Rewrite-Reason: <why: the launcher assumed the test
   process starts with SIGINT at its default; a background start ignores it>`.
4. S2: `bash .../run_forms.sh after 10` (all four forms, ten runs each; detached as in step 1). Every run in every form
   must be all passed, none skipped. Then the whole unit folder once:
   `env HOME=/home/usain/gov-os-worktrees/W2-177/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-177/src python3 -m pytest tests/unit/accept -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
   Add the after-counts per form, and that summary line, to the evidence; commit.

## Rules
- F1: never raise a timeout, add a skip, a marker, a deselect, or touch skip_known.json; no assertion in the W2-96
  unit cases is removed or loosened (S3). If a case still fails after the fix, report it; do not bend it.
- F2: change nothing outside the allowed paths. Never edit tests/acceptance/.
- If your counts refute the diagnosis, stop after step 1 and return PACKAGES with what you found.
- One-line commands; the Write and Edit tools for files in the allowed paths. Never touch .gov-runtime/scratch/lead/.
- Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-1k7y" --trailer "Role: engineer" --trailer "Implements: DEC-966, DEC-1050, DEC-866" -- <paths>`

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the before and after counts per form; the unit-folder summary line) /
tests / discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:`
(hash12, subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or
false-positive).

## The gov context packet (gov context DAEO-1k7y --role engineer --budget 8000)
```json
{
  "ticket": "DAEO-1k7y",
  "ticket_text": "---\nid: DAEO-1k7y\nstatus: in_progress\ndeps: []\nlinks: [DAEO-ouet, DAEO-cb2b, DAEO-wnnz]\ncreated: 2026-11-12T05:03:31Z\ntype: bug\npriority: 1\nassignee: engineer\nexternal-ref: W2-177\ntags: [wave-2, accept, signals, full, shared-red]\nwbs_id: W2-177\ntitle: 'The six W2-96 signal reds: gov accept''s clean-up under a signal, red in every tree''s verify and in the nightly of 11-12'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\nprofile: FULL\ndepends_on: []\nwaits_on: []\nallowed_paths:\n- src/gov/accept/**\n- tests/unit/accept/test_w2_96_run2.py\n- tests/unit/accept/test_w2_96_review3.py\n- tests/unit/accept/test_w2_96_review4.py\n- tests/unit/accept/w2_96_reap.py\n- tests/unit/accept/test_w2_177*\n- docs/changes/W2-177-evidence.md\nest_loc: 80\nkpis:\n  success:\n  - 'S1 The cause is named with evidence before any change: why the six cases (`tests/unit/accept/test_w2_96_run2.py` four, `test_w2_96_review3.py` one, `test_w2_96_review4.py` one) and the W2-96 acceptance cases of the same family fail in the empty-HOME verify form, under the nightly''s cron start, and alone at load 18, yet passed in one W2-110 verify and alone with the real HOME; in particular whether the process under test starts with SIGINT ignored (the nightly''s red premise case R11 says the start form differs from the one the tests assume). Verify: docs/changes/W2-177-evidence.md names the cause, the start forms tried (empty HOME, real HOME, cron-like `setsid` with SIGINT ignored, a background job) and each one''s counts [DEC-1050]'\n  - 'S2 With the fix, the six cases pass in every start form S1 tried, ten runs each, with no timeout raised and no case skipped. Verify: the ten-run counts per form in the evidence; `skip_known.json` unchanged [DEC-966, DEC-1050]'\n  - 'S3 If the cause is the test''s own start form, not `gov accept`, the unit cases change and the W2-96 acceptance cases of the same family go to an independent test designer''s revision with a Rewrite-Reason (the CTO adds their paths then); if it is `gov accept`''s clean-up, the code changes and no test''s assertion is weakened. Verify: the diff: no unit assertion removed or loosened; a test change carries its reason in the commit [DEC-866, DEC-966]'\n  failure:\n  - 'A red hidden instead of fixed: a case added to skip_known.json, a timeout raised, a signal case skipped or deselected. Verify: the diff of skip_known.json, the cases'' timeouts and their markers is empty'\n  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'\nnon_goals:\n- W2-56's two SIGINT ending cases (DAEO-wnnz, its own ticket), unless S1 finds the same cause, which the evidence then says\n- the latency reds of W1-19 and W2-13 (W2-155)\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-966, DEC-1050, DEC-866, DEC-1010, DEC-953]\nacceptance_tests:\n  path: tests/unit/accept/\n  author: 'the existing W2-96 cases are the acceptance (S2); a new case in test_w2_177* for the cause S1 names, written red first'\ntrack: A\nreads:\n- tests/acceptance/W2-96/test_w2_96_at_run_2.py\n- tests/acceptance/W2-96/test_w2_96_at_no_leak.py\nneeds:\n- src/gov/accept/runner.py\n- src/gov/accept/command.py\n---\n# W2-177 The six W2-96 signal reds\n\nThe CTO's ruling P-W2-121-5 (2026-11-12 03:20, delegated P2): six cases in `tests/unit/accept/test_w2_96_{run2,review3,review4}.py`\n(signals and timeouts in `gov accept`'s clean-up) are red in 13 of the 14 most recent lead verifies across eight trees\n(W2-23, W2-11, W2-52, W2-176, W2-110, W2-115, W2-173, W2-121) and in the nightly of 11-12 (run 20261112-0404, `red-alone`,\nwith five W2-96 acceptance cases of the same family, among them the premise case R11). They are shared base reds: named\nin every return, not blocking. This ticket fixes them. Class C2. Diagnosis first (S1), then the smallest fix; a test\nrevision of the acceptance folder is a test designer's, not the engineer's.\n",
  "authority": [
    {
      "id": "DEC-966",
      "sha256": "1a88776392ae3ef7540de64dabef936038b679629045776e45b588bf20ceeec3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1a88776392ae3ef7540de64dabef936038b679629045776e45b588bf20ceeec3",
      "reason": "declared in sources",
      "tokens": 607
    },
    {
      "id": "DEC-1050",
      "sha256": "5aa4028efb141b7a31de8938bdf16151d33934312265d1f2bdf217b3735b2a28",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5aa4028efb141b7a31de8938bdf16151d33934312265d1f2bdf217b3735b2a28",
      "reason": "declared in sources",
      "tokens": 936
    },
    {
      "id": "DEC-866",
      "sha256": "3fd0a96f9624051bf1c77dd154fff18e9c8c62e324c4ad73c0b25f8043e279a1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "3fd0a96f9624051bf1c77dd154fff18e9c8c62e324c4ad73c0b25f8043e279a1",
      "reason": "declared in sources",
      "tokens": 566
    },
    {
      "id": "DEC-1010",
      "sha256": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "reason": "declared in sources",
      "tokens": 964
    },
    {
      "id": "DEC-953",
      "sha256": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "reason": "declared in sources",
      "tokens": 2188
    }
  ],
  "mandatory": [
    {
      "id": "DEC-966",
      "sha256": "1a88776392ae3ef7540de64dabef936038b679629045776e45b588bf20ceeec3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1a88776392ae3ef7540de64dabef936038b679629045776e45b588bf20ceeec3",
      "reason": "declared in sources",
      "tokens": 607
    },
    {
      "id": "DEC-1050",
      "sha256": "5aa4028efb141b7a31de8938bdf16151d33934312265d1f2bdf217b3735b2a28",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5aa4028efb141b7a31de8938bdf16151d33934312265d1f2bdf217b3735b2a28",
      "reason": "declared in sources",
      "tokens": 936
    },
    {
      "id": "DEC-866",
      "sha256": "3fd0a96f9624051bf1c77dd154fff18e9c8c62e324c4ad73c0b25f8043e279a1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "3fd0a96f9624051bf1c77dd154fff18e9c8c62e324c4ad73c0b25f8043e279a1",
      "reason": "declared in sources",
      "tokens": 566
    },
    {
      "id": "DEC-1010",
      "sha256": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "reason": "declared in sources",
      "tokens": 964
    },
    {
      "id": "DEC-953",
      "sha256": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "reason": "declared in sources",
      "tokens": 2188
    }
  ],
  "supplementary": [],
  "supplementary_query": "The six W2-96 signal reds: gov accept's clean-up under a signal, red in every tree's verify and in the nightly of 11-12\nS1 The cause is named with evidence before any change: why the six cases (`tests/unit/accept/test_w2_96_run2.py` four, `test_w2_96_review3.py` one, `test_w2_96_review4.py` one) and the W2-96 acceptance cases of the same family fail in the empty-HOME verify form, under the nightly's cron start, and alone at load 18, yet passed in one W2-110 verify and alone with the real HOME; in particular whether the process under test starts with SIGINT ignored (the nightly's red premise case R11 says the start form differs from the one the tests assume). Verify: docs/changes/W2-177-evidence.md names the cause, the start forms tried (empty HOME, real HOME, cron-like `setsid` with SIGINT ignored, a background job) and each one's counts [DEC-1050]\nS2 With the fix, the six cases pass in every start form S1 tried, ten runs each, with no timeout raised and no case skipped. Verify: the ten-run counts per form in the evidence; `skip_known.json` unchanged [DEC-966, DEC-1050]\nS3 If the cause is the test's own start form, not `gov accept`, the unit cases change and the W2-96 acceptance cases of the same family go to an independent test designer's revision with a Rewrite-Reason (the CTO adds their paths then); if it is `gov accept`'s clean-up, the code changes and no test's assertion is weakened. Verify: the diff: no unit assertion removed or loosened; a test change carries its reason in the commit [DEC-866, DEC-966]\nA red hidden instead of fixed: a case added to skip_known.json, a timeout raised, a signal case skipped or deselected. Verify: the diff of skip_known.json, the cases' timeouts and their markers is empty\nAny change outside the paths above. Verify: `git diff --name-only` of the ticket's branch against its base lists only paths matched by the ticket's allowed_paths",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 6255,
  "budget": {
    "limit": 8000,
    "used": 6255
  },
  "hash": "3fa0333b19976a80fd5226ab8f206b38c96147ac3d13c38c0318458774d0b915"
}
```
