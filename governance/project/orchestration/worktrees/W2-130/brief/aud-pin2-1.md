Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief: independent auditor, W2-130 (DAEO-q8cl): the narrow independent check of pin run 2 (a test revision)

You are a fresh independent auditor (role independent-auditor), ticket DAEO-q8cl (W2-130), profile STANDARD, class
C2. Read-only: you write no file in any repository and make no commit; your scratch is your sandbox's own `$TMPDIR`.
Headless: only your last message is read; the lead commits it as the probe record
`docs/probes/DAEO-q8cl/PR-DAEO-q8cl-pin2.md`, so make it complete.

## Where things are
| what | path |
|---|---|
| the tree (read only) | /home/usain/gov-os-worktrees/W2-130 |
| the head you audit | `a300346eb04be6980e0d38e72aca4e630dc992b5` (the lead's merge of w2/W2-130-tests; the tree is checked out there) |
| the revision under check (narrow: this revision only, since 67364dbea) | test designer commit `ed0e54dfecfb6b1f6dfebefcfec360f599923f10` (read its body); base `67364dbea2fb` |
| the ticket (S4's and S8's Verify; its last paragraph "Reopened 2026-11-14") | `.tickets/DAEO-q8cl.md` |
| pin run 1's narrow check (its F1 and F4 are what this revision answers) | `docs/probes/DAEO-q8cl/PR-DAEO-q8cl-pin.md` |
| W2-130's record (not edited) | `docs/research/W2-130-link-cleanup.md`, blocks `w2-130:counts-after` (its `measured_at`), `w2-130:left`, `w2-130:dec-1123-linked` |
| the README map `gov accept` reads; the runner | `tests/acceptance/W2-130/README.md`; `src/gov/accept/runner.py` |
| the lead's pre-brief probe (judge the tests, not the script) | `.gov-runtime/scratch/lead/run6/probe_pinned_tool.py` and `.out` |

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
- **How reviews converge (owner, standing, DEC-1010 item 1; in force for the CTO, every lead, reviewer and QA engineer):**
  - **A moderator, not a circle of reviewers:** the QA engineer (or the Senior Engineer; until the three layers start, the CTO) triages every finding against the ticket's own scope and KPIs. A finding outside the scope, or one that needs an unusual construction, becomes a Wave 3 row, never a round.
  - **A finding blocks only if it is in scope, reachable in ordinary work, and fails open or loses work.** Everything else lands as a recorded row.
  - **At most two review rounds.** If something still blocks after that, it goes to the owner once, with options; no more routine exceptions.
  - **READY is computed by code, not declared by an agent:** each reviewer returns a structured verdict per KPI line, a fenced `verdict` block in the probe record: `{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`; the close (and the merge queue's pre-check) computes READY from it: no finding that is in scope, ordinary work yes and fails open or loses work. A lead never writes a verdict over a reviewer's.

## The background
W2-130 (a records clean-up) landed and closed on 2026-11-14 and was reopened by the CTO under DEC-1164 (18) and
DEC-1156 (7) for decided-behaviour test revisions. Pin run 1 (`35b6ac6ba`, `6a0b84a81`, checked PASS at `36d4539db`)
pinned S8's two cases to the record's `counts-after.measured_at` (6b62de94e). Its check left F1 (the measured_at pin)
and F4 (the tool not pinned) to the CTO, and the lead brought S4's three HEAD-reading cases (red at HEAD after the
CTO's ce8ae4353) as package P-W2-130-PIN-S4. The CTO's answers (listed for the owner's reading):
- **F1 confirmed:** the pin is `counts-after.measured_at` (6b62de94e), as S8's Verify reads ("at the record's last commit").
- **P-W2-130-PIN-S4: (a).** The three S4 cases that read HEAD
  (`test_s4_every_unlinked_id_on_an_open_or_in_progress_ticket_at_head_is_listed_with_its_dec_1123_2_form`,
  `test_s4_each_dec_1123_linked_entry_is_of_its_form_at_head`,
  `test_s4_dec_1123_linked_lists_only_unlinked_ids_gov_links_reports_at_head_on_open_or_in_progress_tickets`) are
  pinned at `counts-after.measured_at`, as S8 now is. S4's Verify "on HEAD" is re-baselined to the record's measured
  tree under DEC-1156 (7). Live tickets' links stay `gov links`'s own job and D-9's.
- **F4: pin the tool too.** Every pinned case runs `gov links` from the pinned tree's own `src` (the clone at
  `measured_at`, `PYTHONPATH=<clone>/src`), so a later change to `gov links` cannot move a pinned count. The case
  names the README map uses are kept.

## What you check (narrow: this revision only)
1. **Confined:** `git diff 67364dbea2fb a300346eb04be6980e0d38e72aca4e630dc992b5` changes only
   `tests/acceptance/W2-130/{conftest.py,test_w2_130_record.py,test_w2_130_sources.py,w2_130_support.py}`; no
   record, README, ticket, source or other test change. `ed0e54dfe` carries `Task: DAEO-q8cl`,
   `Role: independent-test-designer`, `Rewrite-Reason: DEC-1156 (7), DEC-1164 (18) (W2-130 pin run 2)` in one final
   trailer paragraph, and its body says which cases now run the pinned tool.
2. **S4 pinned:** the three S4 cases no longer read `head_findings`/`head_tree`; they run `gov links` on a clone at
   `counts-after.measured_at` and read ticket statuses and files in that same tree; `measured_at` is checked (full
   hash, `counts-after.head` or a descendant, ancestor of HEAD). Each is green at the audited head.
3. **Tool pinned:** every case pinned to a commit (the three S4 cases, S8's counts and left cases, S8's before-counts
   case at 232efc47d, the two propose-sources cases) runs `gov links` with `PYTHONPATH=<clone>/src`; the HEAD-wide
   cases still run the branch's tool. Confirm by reading the code and by your own run: e.g. a scratch copy of `src`
   under `$TMPDIR` whose `gov links` differs, first on PYTHONPATH; the pinned cases keep the pinned tree's counts and
   a HEAD-wide case moves. Judge the test designer's choice to leave `variant_findings` (F3) on the branch's tool.
4. **No case lost its point:** in a scratch copy under `$TMPDIR` (a `git clone --shared` of the tree, records edited
   in the clone only), plant a wrong count in `counts-after`, a wrong path count in `left`, and in `dec-1123-linked`
   drop one entry, add one pair that is no UNLINKED_ID at `measured_at`, and change one entry's `via`; each revised
   case fails, naming the disagreement.
5. **The map still holds:** every node id the README map names in `test_w2_130_sources.py` and
   `test_w2_130_record.py` collects (`--collect-only`), and no unmapped case was added.
6. **Out of scope, judge only whether it should go to the CTO:** the test designer reports that two S4 cases still
   read HEAD (`test_s4_closed_missing_lists_per_closed_ticket_the_ids_its_sources_lack`,
   `test_s4_no_record_lists_per_ticket_ids_that_name_no_record`) and can be turned red by a ticket closed or reopened
   after the land, or a new unknown id on a live ticket. Confirm or refute; do not judge a fix.

Run the folders like this (they clone into `$TMPDIR`; the tree is never written):
`env PYTHONUSERBASE=/home/usain/.local HOME=<an empty folder under $TMPDIR> PYTHONPATH=/home/usain/gov-os-worktrees/W2-130/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <folder or node> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
and `gov links` as `PYTHONPATH=<src> python3 -m gov.cli.main links --all --json --root <clone>` with HOME an empty
folder. Every pytest goes through heavy_slot.sh. A resource gate's refusal is a wait.

## Return (your last message)
1. A header: `Independent auditor, <ISO 8601 date and time with zone, from date -Is>, at a300346eb04be6980e0d38e72aca4e630dc992b5, W2-130 pin run 2 narrow check.`
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
