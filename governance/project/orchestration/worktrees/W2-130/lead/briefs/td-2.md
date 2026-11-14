# Brief: independent test designer, W2-130 (DAEO-q8cl), run 3 batch 2: S4's cases revised to the re-baselined line (P-W2-130-4 (a))

You are a fresh independent test designer (role independent-test-designer), ticket DAEO-q8cl (W2-130), profile
STANDARD, class C2. Headless: only your last message is read.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-130-tests |
| branch | w2/W2-130-tests (from 11c4d7a5a) |
| your context packet (gov context output, JSON: the ticket, KPIs, sources) | /home/usain/gov-os-worktrees/W2-130-tests/.gov-runtime/scratch/brief/td-context.md |
| the ticket (read it in your tree) | /home/usain/gov-os-worktrees/W2-130-tests/.tickets/DAEO-q8cl.md |
| the cases to revise | /home/usain/gov-os-worktrees/W2-130-tests/tests/acceptance/W2-130/test_w2_130_sources.py (and README.md, w2_130_support.py, conftest.py if needed) |
| the decision the line now rests on | DEC-1123 (2) in /home/usain/gov-os-worktrees/W2-130-tests/docs/DECISION_REGISTER.md (grep by id) and the commit that applied it, `66303c373` |
| the CTO's re-baseline | commit `c2d10bb45` (the ticket's KPI 4 Verify line) |
| scratch | your sandbox's own `$TMPDIR` only |

Your allowed paths: `tests/acceptance/W2-130/**` only. Nothing else.

The implementer (the lead, an orchestrator session) works on the same ticket in `/home/usain/gov-os-worktrees/W2-130`
at the same time: never read that tree or its branch's commits after 11c4d7a5a (the counterpart's work, DEC-820).
History up to 11c4d7a5a is open to you.

## What changed
S4's Verify (the ticket's fourth success line) was re-baselined by the CTO to DEC-1123 (2) (P-W2-130-4 (a)):
"0 UNLINKED_ID on any open or in-progress ticket **other than the ids the record lists, per ticket, as linked by
DEC-1123 (2)'s forms** (a backlog row in list_rows, a WBS id whose ticket id is in sources:, DEC-798 through its live
DEC-1033), each with how it is linked"; and the follow-up sources commit's ids "equal gov links --propose-sources'
output at its parent, **less the DEC-1123 (2) forms the record lists**". The line ends `[S4 re-baselined to DEC-1123
(2), the CTO, P-W2-130-4 (a)]`. Read the whole line in the ticket; it is the spec.

The cases written in run 2 (merged in 94baaafa8) read the old line: `test_s4_gov_links_reports_no_unlinked_id_on_an_
open_or_in_progress_ticket_at_head` wants 0, and `test_s4_the_follow_up_ids_equal_patch_sources_2_and_gov_links_
propose_sources_at_its_parent` wants the follow-up's ids equal to the whole proposal. Revise those cases (and any other
S4 case the new line changes) to the new line, nothing else. Keep every other case as it is.

## The interface addition (the lead's layout for the new list; the rest of the record's layout is in README.md and unchanged)
- `yaml w2-130:dec-1123-linked` — mapping ticket id (`DAEO-…`) -> list of `{id: <the id gov links reports
  UNLINKED_ID>, form: list_rows|wbs|dec-798, via: "<what links it>"}`. It holds every UNLINKED_ID that `gov links
  --all --json` reports at HEAD on an open or in-progress ticket and that one of DEC-1123 (2)'s forms links, and nothing
  else: `form: list_rows` — the id is a backlog row (`W2-H…`, `W2-M…`, `W2-L…`) that is in the ticket's `list_rows`
  (`via`: the id as it stands there); `form: wbs` — the id is a WBS id (some ticket's `wbs_id`) whose ticket's id
  (`via`: that `DAEO-…` id) is in the ticket's `sources:`; `form: dec-798` — the id is DEC-798 and `via` is `DEC-1033`,
  which is in the ticket's `sources:`.
- Every other UNLINKED_ID on an open or in-progress ticket is added to its `sources:` by the follow-up sources commit,
  from `gov links --propose-sources`.
- The follow-up sources commit is the last clean-up commit (after the R-12, lessons and marks follow-ups already in
  history: 8d245901b, 8f8d707f0, bce798c3a); `commits.cleanup` is in ancestry order; `commits.sources` is
  [e12f8a30c, the follow-up].
- `diff w2-130:patch-sources-2` stays `gov links --propose-sources --all` at the follow-up's parent, the open and
  in-progress tickets' sections, byte for byte (the form ids included). The ids the follow-up adds equal that patch's
  ids less `dec-1123-linked`'s (ticket, id) pairs, and equal `gov links --propose-sources` at the follow-up's parent
  less the same pairs. A ticket whose proposed ids are all form ids is not changed (so it has no entry in the commit's
  added ids; compare without empty entries).

What a case should check, from the line: at HEAD every UNLINKED_ID on an open or in-progress ticket is listed for that
ticket in `dec-1123-linked`; each listed entry really is of its form at HEAD (read the ticket's `list_rows` and
`sources:`, and the WBS id's ticket); every entry is an UNLINKED_ID gov links reports at HEAD; and the follow-up's ids
equal the patch and the proposal at its parent, less the listed pairs. How you judge each form from the files is yours;
say in the README how you read it.

## The work
1. Revise the S4 cases and the README's S4 lines (and the record's block list: add `dec-1123-linked`). If a support
   helper must change, change it without changing what other cases check.
2. Run `tests/acceptance/W2-130/test_w2_130_sources.py` at your branch head (11c4d7a5a). The revised cases are red
   there (no record yet): record each S4 case's result with its red reason. Run the whole folder once and quote the
   count line; a case outside S4 whose result changed from run 2's (26 passed, 53 failed at bce798c3a) is a finding.
3. Lower nothing else; add no skip, xfail, flaky or rerun mark. Prove one planted break is caught in a scratch copy
   under `$TMPDIR` (never in your commits): a `dec-1123-linked` entry whose form is false (e.g. a backlog row the
   ticket's `list_rows` does not hold) must fail the revised head case. Show it, then discard.
4. Commit with `Rewrite-Reason: P-W2-130-4 (a)` among the trailers, then return.

## How you run tests
Every pytest through the heavy slot, TMPDIR your sandbox's own `$TMPDIR`:
```
env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-130-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-130-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <file or folder>[::<test>] -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
A whole-folder run adds `-m "not local_only" -k "not real and not green_here and not time_limit"`; name no case
`real`, `green_here` or `time_limit` and mark none `local_only`. A resource gate's refusal is a wait (relaunch when it
opens). Quote the count lines in your return.

## Searching
Read and Grep only; no `gov retrieve` or `gov context` in the sandbox. Search once, then once more in other words; answer
from what you read with path and line, or say "not found". Never open the evaluation sets' root, held-out material or any
hidden or memory-verdict folder.

## Forms that work
Write and edit with the Write and Edit tools and absolute paths. Anything longer than one line of shell goes in a script
under your `$TMPDIR`, run with `bash <file>`. Refused twice for the same call by the guard, the sandbox or a hook: stop and
say so; never work around a refusal. No merge, no push.

## Commit (your paths only; one or more commits)
```
git -C /home/usain/gov-os-worktrees/W2-130-tests commit -m "<subject>" --trailer "Task: DAEO-q8cl" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1073, DEC-1098, DEC-1088" --trailer "Rewrite-Reason: P-W2-130-4 (a)" -- tests/acceptance/W2-130
```
Trailers in one final paragraph. Never `Role: owner` or `Decided-by:`. Before you return: tracked `git status --short` empty.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: commits: <hash12> <subject> | trailers as committed; each S4 case with its result on the base; any place where the
ticket or the interface was unclear and how you read it; guard_refusals: none or a line each.
