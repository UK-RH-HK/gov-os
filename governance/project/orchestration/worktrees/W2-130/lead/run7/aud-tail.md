
## The background
W2-130 (a records clean-up) landed and closed on 2026-11-14 and was reopened by the CTO under DEC-1164 (18) and
DEC-1156 (7) for decided-behaviour test revisions. Pin runs 1 and 2 pinned S8's cases and three S4 cases at the
record's `counts-after.measured_at` (6b62de94e) with the pinned tree's own `gov links` (checked PASS at `36d4539db` and
`a300346eb`). Pin run 2's check left F1 (`variant_findings`, used by the S3/F3 cases, still on the branch's tool) and F2
(`test_s4_closed_missing_lists_per_closed_ticket_the_ids_its_sources_lack` and
`test_s4_no_record_lists_per_ticket_ids_that_name_no_record` still reading HEAD) to the CTO. The CTO's answers (listed
for the owner's reading):
- **P-W2-130-PIN2-HEAD: (a).** The two S4 cases that still read HEAD are pinned at `counts-after.measured_at` with the
  pinned tree's own `gov links`, as S4's other three are. W2-130 lands once, after this pass, so no case that a ticket
  event can turn red reaches integrate.
- **Row F1 rides along:** `variant_findings` runs the pinned tree's own tool too (the commit's own tree, its appended
  marks taken off; its `src` is the commit's). `tests/acceptance/W2-130/README.md` (line 61) and
  `test_w2_130_audit.py` are in the ticket's own acceptance folder, so the test designer edits them.

## What you check (narrow: this revision only)
1. **Confined:** `git diff aafaf6259d10 17487b4700861003d208de7f256a7d1e479c9562` changes only files under
   `tests/acceptance/W2-130/` (the test designer touched `README.md`, `conftest.py`, `test_w2_130_audit.py`,
   `test_w2_130_sources.py`); no record, ticket, source or other test change; the merge adds nothing beyond
   `83285c3c5`. `83285c3c5` carries `Task: DAEO-q8cl`, `Role: independent-test-designer`,
   `Rewrite-Reason: DEC-1156 (7), DEC-1164 (18) (W2-130 pin run 3)` in one final trailer paragraph. The README's changes
   are prose only: no map row or node id changed; judge whether the prose it added beyond line 61 (S4's "at HEAD"
   re-baselined, S8's tool, a "Pin run 3" bullet) states what the tests do.
2. **S4 pinned:** the two named S4 cases no longer read `head_findings`/`head_tree`; they read findings, ticket statuses
   and files, register headings and ticket stems in the same `measured_at` clone, through the same `measured_at` check
   (full hash, `counts-after.head` or a descendant, ancestor of HEAD) and pinned tool as S4's other three. Each is green
   at the audited head; a ticket reopened, or a new unknown id put on a live ticket, after `measured_at` (committed in a
   scratch clone) leaves them green.
3. **Tool pinned:** `variant_findings` runs `gov links` with `PYTHONPATH=<variant clone>/src`, and the variant clone's
   `src` is the marks commit's own. Confirm by reading the code and by your own run (a scratch copy of `src` under
   `$TMPDIR` whose `gov links` differs, including in a `text: true` flag, first on PYTHONPATH: the S3/F3 cases and the
   five S4 cases keep the pinned trees' results, and a HEAD-wide case moves). Confirm the only cases left on the
   branch's tool are the HEAD-wide S2, S6 and S7 cases on `head_findings`, and that no other case runs `gov links` at a
   fixed commit on the branch's tool.
4. **No case lost its point:** in a scratch copy under `$TMPDIR` (a `git clone --shared` of the tree, records edited in
   the clone only), plant in `closed-missing` a dropped id and a ticket not closed at `measured_at`; in `no-record` an id
   that names a register heading (the block is `{}` at the head, so judge how its unlisted side can still be shown);
   and for F3 a free-text mark missing from the audit or judged wrong; each revised case fails, naming the disagreement.
5. **The map still holds:** every node id the README map names collects (`--collect-only` on `tests/acceptance/W2-130`),
   no unmapped case was added, and the `def test_*` names are unchanged from `aafaf6259d10`.
6. **The CTO asks, in scope:** does any W2-130 or W2-175 case still read a value that a later ticket event (a ticket
   closed, reopened, or its `sources:` changed) or an approved change (a register entry added or a status changed by a
   later decision, a lesson added, a change to `gov links`, the templates or records W2-175 reads) moves? List each such
   case by node id, what moves it, and whether that is the case's point (a HEAD-wide check meant to judge HEAD itself)
   or an exposure like F2 of pin run 2. Show at least one by a scratch commit if you claim it.

Run the folders like this (they clone into `$TMPDIR`; the tree is never written):
`env PYTHONUSERBASE=/home/usain/.local HOME=<an empty folder under $TMPDIR> PYTHONPATH=/home/usain/gov-os-worktrees/W2-130/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <folder or node> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
and `gov links` as `PYTHONPATH=<src> python3 -m gov.cli.main links --all --json --root <clone>` with HOME an empty
folder. Every pytest goes through heavy_slot.sh. A resource gate's refusal is a wait.

## Return (your last message)
1. A header: `Independent auditor, <ISO 8601 date and time with zone, from date -Is>, at 17487b4700861003d208de7f256a7d1e479c9562, W2-130 pin run 3 narrow check.`
2. Per item 1 to 6: what you checked, how, and what you found.
3. Each finding with its two lines `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.
4. Last, a fenced block opened by ```` ```verdict ```` holding one JSON object:
   `{"head": "<full hash>", "date": "<ISO>", "kpis": [{"kpi": "<item>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]} ...]}`
   with one entry per item 1 to 6.
Report step 0's sandbox check first. Put the twelve fields (task: / status: / work_completed: / files_changed: /
evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:)
in that same last message, before the header; your last message is the whole return, so do not end on a later note.

## Searching
Read and Grep only, and git show/log/diff; no `gov retrieve` or `gov context`. Search once, then once more in other
words; answer from what you read with path and line, or say "not found". Never open the evaluation sets' root,
held-out material or any hidden or memory-verdict folder. Refused twice for the same call by the guard, the sandbox or
a hook: stop and say so; never work around a refusal.
