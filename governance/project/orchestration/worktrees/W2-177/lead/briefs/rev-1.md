# Brief rev-1: independent auditor for DAEO-1k7y (W2-177), profile FULL, class C2, review round 1

You are a fresh, read-only reviewer. You probe head 170cae9b18368922f33122846c8d1c2dc6665ed6 of branch w2/W2-177 against the ticket's KPIs and
return a verdict (PASS or FAIL) with findings. You write nothing in the tree; your return is the record (the lead
writes the probe record from it).

## Where things are
| what | path |
|---|---|
| the tree (read only) | /home/usain/gov-os-worktrees/W2-177 |
| the ticket's base (w2/integrate, merged in) | c62b66bb4 (the ticket diff: `git diff c62b66bb4 170cae9b18368922f33122846c8d1c2dc6665ed6`) |
| ticket (KPIs S1-S3, F1-F2, non-goals, the CTO's P-W2-177-1/2) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-1k7y.md |
| evidence | docs/changes/W2-177-evidence.md |
| the lead's verify of this head | .gov-runtime/scratch/lead/log/verify/ (summary.txt, parallel.txt, serial.txt) |
| start-form runs | .gov-runtime/scratch/forms/{before,after}/counts.txt (unit, eng-1), .gov-runtime/scratch/acc-forms/lead-after/counts.txt (acceptance, the lead) |

## What to probe (three changes)
1. Cause (A), product code: `src/gov/accept/runner.py` (`_run`, commit 0ca819544): `gov accept`'s child keeps the
   caller's `PYTHONUSERBASE`; every other `PYTHON*` variable stays dropped. Is it the smallest correct change; can it
   leak anything that the drop was there to stop (read why the `PYTHON*` drop exists: git log -S / blame on runner.py);
   does it hold when `PYTHONUSERBASE` is unset or empty?
2. Cause (B), unit test launcher: `tests/unit/accept/w2_96_reap.py` `launch_gov` (003f3d84e, Rewrite-Reason) and the
   new cases `tests/unit/accept/test_w2_177_start_forms.py` (3f1401596, red first). Note `_ignore` sets the three
   signals and then loops `ignore` again: harmless or not? Do the new cases fail on the code before the fix (check
   out the parents in a `git worktree add --detach` copy under /tmp or a `git archive` copy; never in the tree)?
3. The revision (P-W2-177-1 (a), 8f40881d9, a test designer's, Rewrite-Reason): `tests/acceptance/W2-96/w2_96_support.py`
   `_popen` and `tests/acceptance/W2-56/w2_56_support.py` `start_launch`: SIGINT, SIGTERM, SIGHUP to SIG_IGN when named,
   else SIG_DFL, always a `preexec_fn`. Does it weaken any assertion or change what any case proves (R11's premise
   case in particular: it must still prove an ignore given at the start is inherited)?

And across the ticket:
- S1: does the evidence name the cause with counts per start form (empty HOME, real HOME, `setsid` bg with SIGINT
  ignored, a bg job), and is the diagnosis right (reproduce one form yourself if you can, e.g. a background start)?
- S2: the six unit cases green in every form, ten runs each, no timeout raised, no case skipped.
- S3 / F1: `git diff c62b66bb4 170cae9b18368922f33122846c8d1c2dc6665ed6` changes no assertion, timeout, marker, skip or parameter of any case;
  skip_known.json (/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/skip_known.json)
  untouched; each test change carries a Rewrite-Reason in its commit.
- F2: `git diff --name-only c62b66bb4 170cae9b18368922f33122846c8d1c2dc6665ed6` lists only paths matching the ticket's allowed_paths.
- Commits: each non-merge commit's `Task: DAEO-1k7y`, and `Implements:` only ids from the ticket's `sources:`.

## How
- Read-only in the tree. Any run goes in a copy under /tmp (a `git worktree add --detach /tmp/...` or `git archive`),
  removed when done. Every pytest through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest ... -p no:cacheprovider -o tmp_path_retention_policy=failed`
  with TMPDIR outside the repository (e.g. `mktemp -d /tmp/...`) and PYTHONUSERBASE=/home/usain/.local; for an
  empty-HOME run also HOME=/home/usain/gov-os-worktrees/W2-177/.gov-runtime/scratch/empty-home. No other pytest form.
- Planted mutations are welcome (in the copy): e.g. revert each fix alone and see which cases catch it.
- Searches: the Read and Grep tools; search again once in different words if the first does not answer.
- A finding counts if an honest agent hits it in ordinary work and it fails open or loses work (blocking); else minor.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE) / work_completed /
files_changed (none) / evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then a fenced verdict block:
```
verdict: PASS | FAIL
probed_commit: <40-hex>
findings: <n> (<blocking n>, <minor n>)
```
then a findings table: id | KPI | file:line | finding | blocking or minor | a fix you would suggest. Then
`guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).

## The gov context packet (gov context DAEO-1k7y --role independent-auditor --budget 8000)
```json
{
  "ticket": "DAEO-1k7y",
  "ticket_text": "---\nid: DAEO-1k7y\nstatus: in_progress\ndeps: []\nlinks: [DAEO-ouet, DAEO-cb2b, DAEO-wnnz]\ncreated: 2026-11-12T05:03:31Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-177\ntags: [wave-2, accept, signals, full, shared-red]\nwbs_id: W2-177\ntitle: 'The six W2-96 signal reds: gov accept''s clean-up under a signal, red in every tree''s verify and in the nightly of 11-12'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\nprofile: FULL\ndepends_on: []\nwaits_on: []\nallowed_paths:\n- src/gov/accept/**\n- tests/unit/accept/test_w2_96_run2.py\n- tests/unit/accept/test_w2_96_review3.py\n- tests/unit/accept/test_w2_96_review4.py\n- tests/unit/accept/w2_96_reap.py\n- tests/unit/accept/test_w2_177*\n- docs/changes/W2-177-evidence.md\n- tests/acceptance/W2-96/w2_96_support.py  # P-W2-177-1 (a): _popen's signal start state, a test designer's revision (the CTO, 2026-11-12 07:05)\n- tests/acceptance/W2-56/w2_56_support.py  # P-W2-177-1 (a): start_launch's signal start state, the same revision\nest_loc: 80\nkpis:\n  success:\n  - 'S1 The cause is named with evidence before any change: why the six cases (`tests/unit/accept/test_w2_96_run2.py` four, `test_w2_96_review3.py` one, `test_w2_96_review4.py` one) and the W2-96 acceptance cases of the same family fail in the empty-HOME verify form, under the nightly''s cron start, and alone at load 18, yet passed in one W2-110 verify and alone with the real HOME; in particular whether the process under test starts with SIGINT ignored (the nightly''s red premise case R11 says the start form differs from the one the tests assume). Verify: docs/changes/W2-177-evidence.md names the cause, the start forms tried (empty HOME, real HOME, cron-like `setsid` with SIGINT ignored, a background job) and each one''s counts [DEC-1050]'\n  - 'S2 With the fix, the six cases pass in every start form S1 tried, ten runs each, with no timeout raised and no case skipped. Verify: the ten-run counts per form in the evidence; `skip_known.json` unchanged [DEC-966, DEC-1050]'\n  - 'S3 If the cause is the test''s own start form, not `gov accept`, the unit cases change and the W2-96 acceptance cases of the same family go to an independent test designer''s revision with a Rewrite-Reason (the CTO adds their paths then); if it is `gov accept`''s clean-up, the code changes and no test''s assertion is weakened. Verify: the diff: no unit assertion removed or loosened; a test change carries its reason in the commit [DEC-866, DEC-966]'\n  failure:\n  - 'A red hidden instead of fixed: a case added to skip_known.json, a timeout raised, a signal case skipped or deselected. Verify: the diff of skip_known.json, the cases'' timeouts and their markers is empty'\n  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'\nnon_goals:\n- W2-56's two SIGINT ending cases (DAEO-wnnz, its own ticket), unless S1 finds the same cause, which the evidence then says\n- the latency reds of W1-19 and W2-13 (W2-155)\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-966, DEC-1050, DEC-866, DEC-1010, DEC-953]\nacceptance_tests:\n  path: tests/unit/accept/\n  author: 'the existing W2-96 cases are the acceptance (S2); a new case in test_w2_177* for the cause S1 names, written red first'\ntrack: A\nreads:\n- tests/acceptance/W2-96/test_w2_96_at_run_2.py\n- tests/acceptance/W2-96/test_w2_96_at_no_leak.py\nneeds:\n- src/gov/accept/runner.py\n- src/gov/accept/command.py\n---\n# W2-177 The six W2-96 signal reds\n\nThe CTO's ruling P-W2-121-5 (2026-11-12 03:20, delegated P2): six cases in `tests/unit/accept/test_w2_96_{run2,review3,review4}.py`\n(signals and timeouts in `gov accept`'s clean-up) are red in 13 of the 14 most recent lead verifies across eight trees\n(W2-23, W2-11, W2-52, W2-176, W2-110, W2-115, W2-173, W2-121) and in the nightly of 11-12 (run 20261112-0404, `red-alone`,\nwith five W2-96 acceptance cases of the same family, among them the premise case R11). They are shared base reds: named\nin every return, not blocking. This ticket fixes them. Class C2. Diagnosis first (S1), then the smallest fix; a test\nrevision of the acceptance folder is a test designer's, not the engineer's.\n\n## P-W2-177-1 and P-W2-177-2 (the CTO, delegated P2, 2026-11-12 07:05)\n\n- **P-W2-177-1 (a):** an independent test designer's revision, with a Rewrite-Reason naming this ticket and DEC-866, of\n  `tests/acceptance/W2-96/w2_96_support.py`'s `_popen` and `tests/acceptance/W2-56/w2_56_support.py`'s `start_launch`: each of\n  SIGINT, SIGTERM and SIGHUP set to ignored when the case names it, otherwise to default, as `w2_96_reap.launch_gov` now does\n  (cause (B): a background start ignores SIGINT). Both paths are in allowed_paths for that revision only (dropped after the land).\n  No assertion is weakened. Not (b): the verify's and the nightly's start form stay as they are, so the tests own their start state.\n- **P-W2-177-2 (a):** done on w2/integrate (da6ba9c53): `type: task`.\n",
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
  "supplementary": [
    {
      "id": "45bb2f47deb4f335402e5fde",
      "path": "tests/unit/accept/test_w2_177_start_forms.py",
      "text": "\"\"\"W2-177 (DAEO-1k7y): the two causes of the six W2-96 signal reds, one case each (docs/changes/W2-177-evidence.md).\n\n(A) ``gov accept``'s child is given the caller's ``PYTHONUSERBASE`` (pytest is found through it under an empty HOME);\n    no other ``PYTHON*`` variable of the caller's reaches it.\n(B) the test launcher ``w2_96_reap.launch_gov`` starts gov with SIGINT, SIGTERM and SIGHUP at their default unless\n    the case names them to be ignored: a test process started as a background job (SIGINT ignored) must not pass\n    that on, or the signal cases test the start form, not gov.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport signal\nimport subprocess\nimport sys\nfrom pathlib import Path\n\nimport pytest\n\nfrom gov.accept import runner\nfrom w2_96_reap import launch_gov\n\nPROBE = (\n    \"import signal\\n\"\n    \"print(' '.join(str(int(signal.getsignal(s) == signal.SIG_IGN))\"\n    \" for s in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)))\\n\"\n    \"sys.exit(0)\\n\"\n)\nHANDLED = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)\n\n\n",
      "tokens": 257
    },
    {
      "id": "1bcb23e73088e3436d3fdf27",
      "path": "docs/probes/DAEO-ouet/PR-DAEO-ouet-d10.md",
      "text": "- **What was done:** I changed gov, in a scratch copy, so that it neither kills its pytest group nor reaps the run, then ran the reaper-using process cases.\n- **What happened:**\n  - Both `hop` variants passed while every other process check failed.\n  - The likely reason, from the planted program (`test_w2_96_review4.py:48-50`): each process in the chain records its pid only after a 5 ms pause, and the process recorded before it has already exited.\n  - The case judges only recorded pids (`:180-183`), so at most moments none of them is alive.\n  - The revision didn't touch these lines, so this was already true before it.\n- **What should have happened:** the cases should fail whenever the chain outlives gov, as the `breed` variants did.\n- **What would reverse it:** repeated runs of the two `hop` variants against the same mutant failing every time.\n- Ordinary work: no, because a gov that stops reaping is caught by the `breed` cases, the orphan cases and the acceptance R16 cases. Only a regression specific to fork-and-exit chains would depend on these two, and they would still catch it in some runs.\n- Consequence: other\n- Scope: out\n\n",
      "tokens": 287
    },
    {
      "id": "3340e01840319f368a0dc3bb",
      "path": "docs/changes/W2-173-evidence.md",
      "text": "| `gov accept W2-149` | 174 passed, 0 failed, 35 skipped; every line passes but success-26, whose only 2 cases are live (skipped without the CTO's `GOV_W2_149_LIVE=1`), as at run 1; run 1 was 168/6/35 |\n| `tests/acceptance/W2-149`, td-2, whole-folder form from a writable copy | 173 passed, 35 skipped, the same as base `2f98aecbc` in the same form |\n| `lead_verify` (whole suite, parallel) | 4065 tests, 8 failed, 41 skipped: W2-149's two unit cases below and six W2-96 signal cases |\n| `git diff --name-only` against the merge-base with `w2/integrate` (`70e5840d9`) | only the ticket's allowed paths and `tests/acceptance/W2-173/**` (F3, F4) |\n\nThe six W2-96 signal cases (`tests/unit/accept/test_w2_96_review3.py`, `_review4.py`, `_run2.py`) are not this ticket's:\nthe branch changes neither `src/` nor `tests/unit/accept/` against its merge-base with `w2/integrate`. They are red again\nwhen run alone with the empty HOME (13 failed, 7 passed over all their parameters); run 1 found them green alone with the real\nHOME.\n\nW2-149's two unit cases are in `tests/unit/orchestration/test_w2_149_indep_launch.py`, outside this ticket's paths, so they\n",
      "tokens": 287
    },
    {
      "id": "b28bc747ace76a086614d983",
      "path": "governance/project/orchestration/packages/INVENTORY-TESTS-CODE-1.md",
      "text": "| 12 | `tests/unit/accept/test_w2_96_accept.py` | 437 | 340 |\n| 13 | `tests/unit/guard/test_reads.py` | 431 | 351 |\n| 14 | `tests/unit/release/test_release.py` | 420 | 330 |\n| 15 | `tests/unit/orchestration/test_merge_queue_seed.py` | 418 | 322 |\n| 16 | `tests/unit/hooks/test_w29_hooks.py` | 392 | 317 |\n| 17 | `tests/unit/telemetry/test_counter.py` | 377 | 275 |\n| 18 | `tests/unit/containment/test_restore_verify_and_timeout.py` | 355 | 271 |\n| 19 | `tests/unit/accept/test_w2_96_review3.py` | 338 | 261 |\n| 20 | `tests/unit/check/test_check.py` | 336 | 218 |\n\n**acceptance tests (tests/acceptance/): the 20 largest files** (total lines / code lines)\n\n| # | File | Lines | Code |\n|---:|---|---:|---:|\n| 1 | `tests/acceptance/W1-02/README.md` | 2,667 | 2,237 |\n| 2 | `tests/acceptance/W1-30/README.md` | 2,349 | 1,948 |\n| 3 | `tests/acceptance/W2-96/w2_96_support.py` | 1,682 | 1,188 |\n| 4 | `tests/acceptance/W2-54/w2_54_support.py` | 1,616 | 1,061 |\n| 5 | `tests/acceptance/W1-31/w1_31_support.py` | 1,601 | 1,057 |\n| 6 | `tests/acceptance/W1-50/README.md` | 1,534 | 1,264 |\n| 7 | `tests/acceptance/W2-69/w2_69_support.py` | 1,307 | 967 |\n",
      "tokens": 286
    },
    {
      "id": "bad40599a9508d9d2dc93889",
      "path": "docs/probes/DAEO-61vm/PR-DAEO-61vm.md",
      "text": "- **The lead's own results, which the reviewer did not re-run.** The store was rebuilt at the head (exit 0). `gov accept W2-170` (the pinned judge) exited 0, outcome pass: 179 passed, 0 failed, 0 skipped, every line S1-S6 and F1-F5 its own pass. The engineer's unit folder `tests/unit/memaudit` gave 84 passed. `lead_verify` (the scoped run plus the wider net) gave 3,987 passed, 6 skipped and 6 failed, all six of them W2-96 signal cases that fail only in an empty-HOME, signal-ignoring shell (row 133's cause, not this ticket's).\n",
      "tokens": 133
    }
  ],
  "supplementary_query": "The six W2-96 signal reds: gov accept's clean-up under a signal, red in every tree's verify and in the nightly of 11-12\nS1 The cause is named with evidence before any change: why the six cases (`tests/unit/accept/test_w2_96_run2.py` four, `test_w2_96_review3.py` one, `test_w2_96_review4.py` one) and the W2-96 acceptance cases of the same family fail in the empty-HOME verify form, under the nightly's cron start, and alone at load 18, yet passed in one W2-110 verify and alone with the real HOME; in particular whether the process under test starts with SIGINT ignored (the nightly's red premise case R11 says the start form differs from the one the tests assume). Verify: docs/changes/W2-177-evidence.md names the cause, the start forms tried (empty HOME, real HOME, cron-like `setsid` with SIGINT ignored, a background job) and each one's counts [DEC-1050]\nS2 With the fix, the six cases pass in every start form S1 tried, ten runs each, with no timeout raised and no case skipped. Verify: the ten-run counts per form in the evidence; `skip_known.json` unchanged [DEC-966, DEC-1050]\nS3 If the cause is the test's own start form, not `gov accept`, the unit cases change and the W2-96 acceptance cases of the same family go to an independent test designer's revision with a Rewrite-Reason (the CTO adds their paths then); if it is `gov accept`'s clean-up, the code changes and no test's assertion is weakened. Verify: the diff: no unit assertion removed or loosened; a test change carries its reason in the commit [DEC-866, DEC-966]\nA red hidden instead of fixed: a case added to skip_known.json, a timeout raised, a signal case skipped or deselected. Verify: the diff of skip_known.json, the cases' timeouts and their markers is empty\nAny change outside the paths above. Verify: `git diff --name-only` of the ticket's branch against its base lists only paths matched by the ticket's allowed_paths",
  "further_batch": [
    {
      "id": "0fa4cbb15f4ba73bfb4fd935",
      "path": "docs/probes/DAEO-ouet/PR-DAEO-ouet-d10b.md"
    },
    {
      "id": "8071634a5dbc9b4d53f0c9c8",
      "path": "governance/project/orchestration/closes/W2-170-DAEO-61vm.md"
    },
    {
      "id": "89cfcc9fc5d326b00958cde0",
      "path": "governance/project/orchestration/closes/W2-81-DAEO-l78m.md"
    },
    {
      "id": "c50e8023b65666e1d87e3397",
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-NIGHT.md"
    },
    {
      "id": "19548cae28d964ed1fb5387a",
      "path": "governance/project/orchestration/reviews/D10-W2-96-review.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "45bb2f47deb4f335402e5fde",
          "path": "tests/unit/accept/test_w2_177_start_forms.py"
        },
        {
          "id": "1bcb23e73088e3436d3fdf27",
          "path": "docs/probes/DAEO-ouet/PR-DAEO-ouet-d10.md"
        },
        {
          "id": "3340e01840319f368a0dc3bb",
          "path": "docs/changes/W2-173-evidence.md"
        },
        {
          "id": "b28bc747ace76a086614d983",
          "path": "governance/project/orchestration/packages/INVENTORY-TESTS-CODE-1.md"
        },
        {
          "id": "bad40599a9508d9d2dc93889",
          "path": "docs/probes/DAEO-61vm/PR-DAEO-61vm.md"
        },
        {
          "id": "0fa4cbb15f4ba73bfb4fd935",
          "path": "docs/probes/DAEO-ouet/PR-DAEO-ouet-d10b.md"
        },
        {
          "id": "8071634a5dbc9b4d53f0c9c8",
          "path": "governance/project/orchestration/closes/W2-170-DAEO-61vm.md"
        },
        {
          "id": "89cfcc9fc5d326b00958cde0",
          "path": "governance/project/orchestration/closes/W2-81-DAEO-l78m.md"
        },
        {
          "id": "c50e8023b65666e1d87e3397",
          "path": "governance/project/orchestration/packages/LIFT-1/D4B-NIGHT.md"
        },
        {
          "id": "19548cae28d964ed1fb5387a",
          "path": "governance/project/orchestration/reviews/D10-W2-96-review.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "0fa4cbb15f4ba73bfb4fd935",
      "reason": "budget exceeded"
    },
    {
      "id": "19548cae28d964ed1fb5387a",
      "reason": "budget exceeded"
    },
    {
      "id": "8071634a5dbc9b4d53f0c9c8",
      "reason": "budget exceeded"
    },
    {
      "id": "89cfcc9fc5d326b00958cde0",
      "reason": "budget exceeded"
    },
    {
      "id": "c50e8023b65666e1d87e3397",
      "reason": "budget exceeded"
    }
  ],
  "tokens": 7765,
  "budget": {
    "limit": 8000,
    "used": 7765
  },
  "left_out": {
    "count": 3,
    "superseded": [
      "DEC-045",
      "DEC-875",
      "DEC-876"
    ],
    "done": []
  },
  "hash": "479896c3920e3a5b9135716826078297eb93d5864f6b9d033f6d5372cf722ea2"
}
```
