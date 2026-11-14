Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief: independent auditor, W2-130 (DAEO-q8cl): the narrow independent check of the pin run (a test revision)

You are a fresh independent auditor (role independent-auditor), ticket DAEO-q8cl (W2-130), profile STANDARD, class
C2. Read-only: you write no file in any repository and make no commit; your scratch is your sandbox's own `$TMPDIR`.
Headless: only your last message is read; the lead commits it as the probe record
`docs/probes/DAEO-q8cl/PR-DAEO-q8cl-pin.md`, so make it complete.

## Where things are
| what | path |
|---|---|
| the tree (read only) | /home/usain/gov-os-worktrees/W2-130 |
| the head you audit | `36d4539dbe433c4b27e94d7cb357ec8b79a5363f` (the lead's merge of w2/W2-130-tests; the tree is checked out there) |
| the revision under check | test designer commits `35b6ac6bacae9aad1c5277e0cb5ac2b9f8973cd0` and `6a0b84a81a5905d11bd105ba2c1459be3610cbb9` (read both bodies); base `f4511c72339e` (the merge of w2/integrate) |
| the ticket (its last paragraph "Reopened 2026-11-14" states the decided behaviour; S8's Verify) | `.tickets/DAEO-q8cl.md` |
| the CTO's diagnosis (sections "1-2" and "3-4") | /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/nightly-20261114/DIAG.md |
| W2-130's record (not edited) | `docs/research/W2-130-link-cleanup.md`, blocks `w2-130:counts-after` (near line 5473) and `w2-130:left` |
| W2-175's CIT-P record (not edited) and ticket | `docs/changes/W2-175-CIT-P.md`, `.tickets/DAEO-wahn.md` (its S7 Verify: "at the ticket's head") |
| the README maps `gov accept` reads | `tests/acceptance/W2-130/README.md`, `tests/acceptance/W2-175/README.md`; the runner `src/gov/accept/runner.py` |
| the lead's pre-brief probes | `.gov-runtime/scratch/lead/run5/probe_after.py`, `probe_s4.py` (judge the tests, not the scripts) |

## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines.

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

From brief A3 (reviewer), word for word:
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.

## The background
W2-130 (a records clean-up) landed and closed at 01:43 on 2026-11-14. The nightly found four cases that pin a value that
moves after the close. The CTO reopened the ticket under DEC-1164 (18) and DEC-1156 (7) for two decided-behaviour test
revisions:
1. W2-130 S8's `test_s8_gov_links_at_head_gives_the_after_counts` and
   `test_s8_left_holds_d_5_d_6_and_d_9_by_path_and_role_as_gov_links_finds_them_at_head` ran `gov links` at HEAD, so
   every ticket close or reopen moved the counts. Decided: run `gov links` at a commit the record pins, through the
   existing `clone_at` fixture. The CTO's text names `counts-after.head`.
2. W2-175's `test_s7_record_sha256_of_each_template_is_its_sha256_at_the_head[*]` hashed the working tree's templates;
   an owner-approved change (b88a76172) moved two after W2-175 closed. Decided: read each template at W2-175's landing
   commit 61cae50dc through git, as the base-sha256 case pins its bases. The CIT-P record is not edited.
**The lead's deviation (judge it):** the cases run `gov links` at the record's `counts-after.measured_at`
(6b62de94e), not at `counts-after.head` (57cbacfbf). The lead measured both with the cases' own counting: at 57cbacfbf
the counts differ from the record (UNLINKED_ID 1417 vs 1420; UNKNOWN_ID 57 vs 56; left.D-9 differs on five paths), so
that pin stays red with the record unedited; at 6b62de94e every count equals the record. The record's `command` says
it counted 6b62de94e; the ticket's S8 Verify says "a re-run of gov links --all at the record's last commit gives the
record's after counts" (the record's last commit a2671a340 has parent 6b62de94e and changes only the record). The
revised cases also assert `measured_at` is `counts-after.head` or a descendant of it and an ancestor of HEAD.
The first test designer renamed the cases; the README maps name the old ids, so a second test designer restored the
names (docstrings say what they read now) and folded a new unmapped case back into the parametrised one.

## What you check (narrow: this revision only)
1. **Confined:** `git diff f4511c72339e 36d4539dbe433c4b27e94d7cb357ec8b79a5363f` changes only
   `tests/acceptance/W2-130/test_w2_130_record.py`, `tests/acceptance/W2-175/test_w2_175_record.py`,
   `tests/acceptance/W2-175/w2_175_support.py`; no record, README, ticket, source or other test changes. Both test
   designer commits carry `Task: DAEO-q8cl`, `Role: independent-test-designer`, `Rewrite-Reason: DEC-1156 (7),
   DEC-1164 (18) (W2-130 pin run)` in one final trailer paragraph.
2. **Decided behaviour, W2-130:** the two cases no longer read HEAD's findings; they run `gov links` through
   `clone_at` at a pinned commit from the record. Judge the lead's choice of `measured_at` over `counts-after.head`
   against the decided behaviour's point and the ticket's S8 Verify; confirm the lead's measurement by your own
   `gov links --all --json` on `git clone --shared` clones at 57cbacfbf and 6b62de94e under `$TMPDIR`.
   The HEAD-wide "no UNMARKED_CHANGE but the 8 pairs" case and every other case are unchanged.
3. **Decided behaviour, W2-175:** the sha256 case reads each template at 61cae50dc through git (not the working tree),
   asserts 61cae50dc is an ancestor of HEAD, and 61cae50dc is W2-175's landing merge. All seven parametrised ids pass.
4. **No case lost its point:** in a scratch copy under `$TMPDIR` (a `git clone --shared` of the tree, records edited
   in the clone only), plant one wrong count in `counts-after`, one wrong path count in `left`, and one wrong sha256
   in the W2-175 record's role-lead row; each revised case fails, naming the disagreement. Also judge whether a
   record whose `measured_at` named some unrelated commit would be caught.
5. **The maps still hold:** every item the two README maps name in the two changed test files collects
   (`--collect-only`), so `gov accept` reads them.
6. **Out of scope, confirm only:** `test_w2_130_sources.py::test_s4_every_unlinked_id_on_an_open_or_in_progress_ticket_at_head_is_listed_with_its_dec_1123_2_form`
   is red at this head with three UNLINKED_ID (DAEO-6f0s W2-60a, DAEO-6w5n W2-H046, DAEO-sq3a W2-56), left by the CTO's
   ce8ae4353 on w2/integrate. Confirm it is red at the base f4511c72339e too (so not caused by this revision). The lead
   brings it to the CTO as a package; do not judge its fix.

Run the folders like this (they clone into `$TMPDIR`; the tree is never written):
`env PYTHONUSERBASE=/home/usain/.local HOME=<an empty folder under $TMPDIR> PYTHONPATH=/home/usain/gov-os-worktrees/W2-130/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <folder or node> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
and `gov links` as `PYTHONPATH=/home/usain/gov-os-worktrees/W2-130/src python3 -m gov.cli.main links --all --json --root <clone>` with HOME an empty folder.
Every pytest goes through heavy_slot.sh. A resource gate's refusal is a wait.

## Return (your last message)
1. A header: `Independent auditor, <ISO 8601 date and time with zone, from date -Is>, at 36d4539dbe433c4b27e94d7cb357ec8b79a5363f, W2-130 pin run narrow check.`
2. Per item 1 to 6: what you checked, how, and what you found.
3. Each finding with its two lines `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.
4. Last, a fenced block opened by ```` ```verdict ```` holding one JSON object:
   `{"head": "<full hash>", "date": "<ISO>", "kpis": [{"kpi": "<item>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]} ...]}`
   with one entry per item 1 to 5 (item 6 is out of scope; name it in the prose only).
Report step 0's sandbox check first.

## Searching
Read and Grep only, and git show/log/diff; no `gov retrieve` or `gov context`. Search once, then once more in other
words; answer from what you read with path and line, or say "not found". Never open the evaluation sets' root,
held-out material or any hidden or memory-verdict folder. Refused twice for the same call by the guard, the sandbox or
a hook: stop and say so; never work around a refusal.
