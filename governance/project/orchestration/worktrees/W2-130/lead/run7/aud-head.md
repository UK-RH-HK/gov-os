# Brief: independent auditor, W2-130 (DAEO-q8cl): the narrow independent check of pin run 3 (a test revision)

You are a fresh independent auditor (role independent-auditor), ticket DAEO-q8cl (W2-130), profile STANDARD, class
C2. Read-only: you write no file in any repository and make no commit; your scratch is your sandbox's own `$TMPDIR`.
Headless: only your last message is read; the lead commits it as the probe record
`docs/probes/DAEO-q8cl/PR-DAEO-q8cl-pin3.md`, so make it complete.

## Where things are
| what | path |
|---|---|
| the tree (read only) | /home/usain/gov-os-worktrees/W2-130 |
| the head you audit | `17487b4700861003d208de7f256a7d1e479c9562` (the lead's merge of w2/W2-130-tests; the tree is checked out there) |
| the revision under check (narrow: this revision only, since aafaf6259d10) | test designer commit `83285c3c52c32b7f96936b815e2656604a6d97cb` (read its body); base `aafaf6259d10` |
| the ticket (S3's, S4's and F3's Verify; its last paragraph) | `.tickets/DAEO-q8cl.md` |
| pin run 2's narrow check (its F1 and F2 are what this revision answers) | `docs/probes/DAEO-q8cl/PR-DAEO-q8cl-pin2.md` |
| W2-130's record (not edited) | `docs/research/W2-130-link-cleanup.md`, blocks `w2-130:counts-after` (its `measured_at`), `w2-130:closed-missing`, `w2-130:no-record` |
| the README map `gov accept` reads; the runner | `tests/acceptance/W2-130/README.md`; `src/gov/accept/runner.py` |
| W2-175's acceptance folder (read for item 6) | `tests/acceptance/W2-175/` |
| the lead's pre-brief probe (judge the tests, not the script) | `.gov-runtime/scratch/lead/run7/probe_pin3.py` and `.out` |

## Judgement rules (`governance/project/briefs/JUDGEMENT.md`, word for word)

