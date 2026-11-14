---
type: probe
task: DAEO-q8cl
reviewer_session: d3d0e1a8-5ce7-46c1-a360-fed6cc5771d3
implementer_session: "independent-test-designer session 37c7bdce-0b08-42f6-b1eb-800d3e4170c9 (commit ed0e54dfecfb6b1f6dfebefcfec360f599923f10)"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: a300346eb04be6980e0d38e72aca4e630dc992b5
decisions_applied: [DEC-1156, DEC-1164, DEC-1073, DEC-1010]
---

# Probe record: W2-130 (DAEO-q8cl), pin run 2's narrow independent check (a decided-behaviour test revision)

A fresh independent-auditor session (`d3d0e1a8-5ce7-46c1-a360-fed6cc5771d3`) ran on `claude-opus-5-5` at high effort, class C2, read-only, with
JUDGEMENT.md word for word in its brief. It probed head `a300346eb04b` of `w2/W2-130` (the lead's merge of
`w2/W2-130-tests`), narrow: this revision only, since `67364dbea`. It wrote nothing (`git status` empty; sandbox trial
file absent; its tripwire's only changes are the CTO's commit `1d5af6d75` (P1-MORNING-20261114, Role orchestrator) on
the main tree and the store trees following it, made by other sessions while it ran).

What it probed: the CTO's answers under DEC-1164 (18) and DEC-1156 (7) (listed for the owner's reading): F1 confirmed
(the pin is the record's `counts-after.measured_at`, 6b62de94e); P-W2-130-PIN-S4 (a) (S4's three HEAD-reading cases
pinned at `counts-after.measured_at`, S4's Verify "on HEAD" re-baselined to the record's measured tree); F4 (every
pinned case runs `gov links` from the pinned tree's own `src`). One independent test designer commit, `ed0e54dfe`:
the three S4 cases on `pinned_findings(measured_at)`; one `measured_at` check in `w2_130_support.py`; `child_env`,
`run_links`, `links_json` with an optional `src`; the pinned tool for the three S4 cases, S8's counts and left cases
(at `measured_at`), S8's before-counts case (at 232efc47d) and the two propose-sources cases (at each commit's parent).
No record, README, ticket or source was edited; every README-mapped case name kept.

Its verdict is **PASS**: five items pass, two findings, none blocking (neither in scope with ordinary work yes and
fails open or loses work).

## The lead's judgement of the findings

- **F1** (out of scope: the F3 cases' `variant_findings` still runs the branch's `gov links` on fixed historical trees;
  the README and `test_w2_130_audit.py` say "HEAD's tool", both outside this run's paths). Ordinary work: yes, because
  changes to `gov links` are planned under D-6. Consequence: other (a false red or a weaker check over a fixed history;
  nothing fails open, nothing is lost). A row, brought to the CTO in the lead's return.
- **F2** (out of scope, item 6: `test_s4_closed_missing_lists_per_closed_ticket_the_ids_its_sources_lack` and
  `test_s4_no_record_lists_per_ticket_ids_that_name_no_record` still read HEAD's tickets and HEAD's tool; a ticket
  closed or reopened after the land, or a new unknown id on a live ticket, turns them red; reproduced in a scratch
  clone). Ordinary work: yes, because tickets are closed and reopened routinely. Consequence: other (a false red on a
  re-run of `gov accept W2-130`; fails closed). Brought to the CTO as a package in the lead's return, shaped like
  P-W2-130-PIN-S4.

The lead's own runs at `a300346eb04b`: the two changed record and sources files 24 passed; `gov accept W2-130` 81
passed, 0 failed (all twelve lines); `gov accept W2-175` 51 passed, 0 failed; the scoped run (DEC-968) of
`tests/acceptance/W2-130` and `tests/acceptance/W2-175` 132 passed.

## The auditor's return, word for word

**Step 0, the sandbox check (launch_worker.sh):** passed.
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-q8cl` failed with `OSError: [Errno 30] Read-only file system`, and no such file exists.
- (b) `echo sandbox-trial | git hash-object -w --stdin` returned `1ae28402a…` (exit 0), and `git update-index --refresh` exited 0.
- Environment: `GOV_TICKET=DAEO-q8cl`, `GOV_ROLE=independent-auditor`.
- **ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing.
- `git -C /home/usain/gov-os-worktrees/W2-130 status --porcelain` is empty at the end. I wrote nothing in the tree; all scratch work was under `$TMPDIR/aud`.

- task: DAEO-q8cl (W2-130), the narrow independent check of pin run 2 (`ed0e54dfe`, merged as `a300346eb`)
- status: done. PASS on items 1 to 5; item 6 confirmed (out of scope)
- work_completed: read the diff, the commit bodies and the trailers; ran the folder at the head; ran a modified-tool check and a control at the base; planted 11 wrong record values; collected the README map; ran item 6's two cases after a scratch reopen and a scratch unknown id
- files_changed: none
- evidence: listed under each item below
- tests: `tests/acceptance/W2-130`, 81 collected, 81 passed. The exclusion `-m "not local_only" -k "not real and not green_here and not time_limit"` left nothing out of this folder (81 collected without it).
- discoveries: F1 (the F3 cases still run the branch's tool) and F2 (two S4 cases still read HEAD, confirmed)
- risks: F1 and F2. Neither fails open or loses work.
- lessons: none new
- proposed_decisions: F2 goes to the CTO as a package shaped like P-W2-130-PIN-S4. F1 is a row the CTO may fold into it.
- unresolved: none
- recommended_next_action: the lead commits this record; the CTO decides F2 (and F1).

---

Independent auditor, 2026-11-14T09:08:07+00:00, at a300346eb04be6980e0d38e72aca4e630dc992b5, W2-130 pin run 2 narrow check.

## Item 1: Confined (PASS)
- **Files changed:** `git diff --name-only 67364dbea2fb ed0e54dfe` lists only `tests/acceptance/W2-130/{conftest.py,test_w2_130_record.py,test_w2_130_sources.py,w2_130_support.py}` (108 lines added, 48 removed).
- **The merge added nothing:** `git diff ed0e54dfe a300346eb` is empty.
- **Nothing else moved:** the record, the README, the ticket and `src` are unchanged.
- **Trailers:** `git interpret-trailers --parse` on `ed0e54dfe` reads one final paragraph: `Task: DAEO-q8cl`, `Role: independent-test-designer`, `Implements: DEC-1073, DEC-1010`, `Rewrite-Reason: DEC-1156 (7), DEC-1164 (18) (W2-130 pin run 2)`, `Co-Authored-By`.
- **Body:** it lists by node id and commit the 8 cases that now run the pinned tool. It also names what was left on the branch's tool on purpose: `variant_findings`, and the HEAD-wide S2, S6 and S7 cases.

## Item 2: S4 pinned (PASS)
- **No HEAD reads left:** the three named S4 cases no longer take `head_findings` or `head_tree`. Each calls `_pinned(record, pinned_findings)`, which is `pinned_findings(s.measured_at(record))` (`test_w2_130_sources.py:66-109`).
- **Same tree for tickets and files:** statuses come from `unlinked_on_live(findings, tree)` (`w2_130_support.py:379-389`). Ticket files, `list_rows`, the `wbs_id` aliases and `sources:` come from `linked_form_problem(tree, …)` (`:391-431`). Both use that same clone.
- **One measured_at check, not copied:** it now lives in `w2_130_support.measured_at` (`:622-636`): a full 40-hex hash through `need_hash`, `counts-after.head` or a descendant of it, and an ancestor of HEAD. `test_w2_130_record.py:_measured_at` calls it.
- **Green at the head:** all three cases pass at `a300346eb`. The record's `measured_at` is `6b62de94e3fd67505998c69d3de68b937d60406b`, an ancestor of HEAD.
- **Each measured_at check bites.** I planted each value in a scratch clone's record; each turned all five revised cases red:

| planted `measured_at` | message |
|---|---|
| `6b62de94e3fd` (abbreviated) | "is not a full 40-hex commit hash" |
| `11c4d7a5a` (the parent of `counts-after.head`) | "is not counts-after.head or a descendant of it" |
| `1d5af6d75` (not in HEAD's history) | "is not an ancestor of HEAD" |

## Item 3: Tool pinned (PASS)
**By reading the code:**
- `child_env`, `run_links` and `links_json` take an optional `src`; None means the branch's `src_dir()` (`w2_130_support.py:590-618`).
- `pinned_src(tree)` returns `<clone>/src`.
- `pinned_findings` runs `links_json(tree, home, src=pinned_src(tree))` (`conftest.py:56-69`).
- `start_findings` is `pinned_findings(START)[1]`.
- `propose_sources_at` passes `src=pinned_src(tree)` (`conftest.py:105`).
- `head_findings` and `variant_findings` keep the branch's tool.

**Module resolution:** I used a clone at `measured_at` with `PYTHONPATH=<clone>/src`. There, `gov`, `gov.links` and `gov.cli.main` all load from `<clone>/src`, and no `gov` is installed in the user site.

**My own run:**
- I made a copy of `src` under `$TMPDIR` whose `gov links` drops two UNLINKED_ID findings (the first one, and DAEO-057v's W2-H021) and adds an UNMARKED_CHANGE DEC-1/DEC-2. At `measured_at` it gives UNLINKED_ID 1418 and UNMARKED_CHANGE 9, against the real tool's 1420 and 8.
- With that copy first on PYTHONPATH, the whole folder at the head gives 79 passed and 2 failed.
  - **All 8 pinned cases pass:** the 3 S4 cases, S8 counts, S8 left, S8 before-counts and both propose-sources cases.
  - **The 2 failures are HEAD-wide cases:** `test_s2_gov_links_reports_no_unmarked_change_but_the_eight_pairs_the_auditor_judged_wrong` and `test_s4_closed_missing_…`. HEAD-wide cases still run the branch's tool.
- **Control:** the same modified tool against the base commit's tests (a clone at `67364dbea`) turns 6 of those 8 cases red: S8 counts, S8 left, S8 before-counts, S4 cases 1 and 3, and propose-sources at e12f8a30c. So the modification is one that would have shown before, and the pinning is what now holds the counts.

**The choice to leave `variant_findings` on the branch's tool:** this is defensible within this run. `README.md:60-62` and the `test_w2_130_audit.py` module docstring both say "HEAD's tool", and neither file is in this run's paths. The brief's list of pinned cases does not include the F3 cases. The cost is that F3's free-text set can still move with a later `gov links` change (F1 below).

## Item 4: No case lost its point (PASS)
I made a scratch clone at the head (`$TMPDIR/aud/p`), edited only that clone's record for each plant, and restored it after each. I ran the five revised cases each time. Each plant turned exactly one case red, the one it targets, and the other four stayed green:

| plant | case that failed | message |
|---|---|---|
| counts-after `by_code.UNKNOWN_ID` 56→57 | S8 counts | "by_code differs from gov links at measured_at" |
| `by_code_role.UNKNOWN_ID.owner` 1→2 | S8 counts | "by_code_role differs …" |
| `unlinked_by_status.in_progress` 2→3 | S8 counts | "unlinked_by_status differs …" |
| left D-6 `tests/unit/impact/test_impact.py` 2→3 | S8 left | "left.D-6 differs from the findings at measured_at" |
| dec-1123-linked: DAEO-057v W2-M279 dropped | S4 case 1 | "1 UNLINKED_ID … at measured_at that dec-1123-linked does not list: [('DAEO-057v', 'W2-M279')]" |
| added DAEO-057v W2-L047 (in its `list_rows`, but not an UNLINKED_ID at measured_at) | S4 case 3 only | "1 entries are no UNLINKED_ID gov links reports at measured_at …: [('DAEO-057v', 'W2-L047')]" |
| `via` W2-L172→W2-L173 | S4 case 2 | "via 'W2-L173' is not the id as it stands in list_rows (W2-L172)" |
| `wbs` `via` DAEO-t8mp→DAEO-ts4y | S4 case 2 | "via DAEO-ts4y is no ticket with wbs_id W2-128 (those are ['DAEO-t8mp'])" |

The W2-L047 plant isolates case 3 from case 2: case 2 stays green because the id is in the ticket's `list_rows`.

## Item 5: The map still holds (PASS)
- The README is unchanged since `67364dbea`.
- The README map names 24 node ids in `test_w2_130_sources.py` and `test_w2_130_record.py`. `--collect-only` collects exactly those 24 ids, with nothing missing either way.
- The `def test_*` names in both files are identical at the base and the head, so no case was added or renamed.

## Item 6 (out of scope): the two S4 cases that still read HEAD (CONFIRMED)
- **They read HEAD:** `test_s4_closed_missing_lists_per_closed_ticket_the_ids_its_sources_lack` and `test_s4_no_record_lists_per_ticket_ids_that_name_no_record` still take `head_findings` and `head_tree` (`test_w2_130_sources.py:187-219`).
- **A reopen turns one red:** in the scratch clone I committed a reopen of DAEO-03dg (`status: closed` → `open`). `closed_missing` fails ("DAEO-03dg is not a closed ticket").
- **A new unknown id turns the other red:** I committed DEC-99999 added to open DAEO-057v's `sources:`. `no_record` fails ("gov links reports unknown ids the record does not list per ticket: [('DAEO-057v', 'DEC-99999')]").
- **The pinned cases are unaffected:** in both runs the five pinned S4 and S8 cases stay green.
- **They also move with the tool:** under the modified tool in item 3, `closed_missing` failed too.
- **Recommendation:** this is the same kind of exposure P-W2-130-PIN-S4 (a) closed for the other three cases. It should go to the CTO as a package; I judge no fix.

## Findings

**F1: the F3 cases (`variant_findings`) still run the branch's `gov links`.** A later change to how `gov links` sets `text: true` can move which marks count as free text in the historical marks commits. The record's own `left` D-6 already names such a change: how the loader reads a verbless `Changed by:`. The test designer followed the README and the audit module's "HEAD's tool", and the brief's list of pinned cases does not include these cases. This is a row for the CTO, not a block for this revision.
- Ordinary work: yes, because changes to `gov links` are planned under D-6, and the F3 cases read the branch's tool on fixed historical trees.
- Consequence: other (the F3 cases can turn red, or become weaker, over a fixed history; no live work is let through and none is lost).

**F2 (item 6, out of scope): two S4 cases still read HEAD's tickets and HEAD's tool.** A ticket closed or reopened after the land, or a new unknown id on a live ticket, turns them red. I reproduced both triggers in a scratch clone.
- Ordinary work: yes, because tickets are closed and reopened routinely (CLOSED_TICKET_EDITED went from 122 to 124 in five hours) and live tickets gain ids.
- Consequence: other (false red on re-runs of `gov accept W2-130`; nothing fails open, no work is lost).

Classification: F1 and F2 are both ordinary work yes, consequence other. Neither blocks. F2 goes to the CTO as a package; F1 is a row.

What evidence would reverse each:
- F1 falls if the ticket or the CTO states that F3 is judged by the branch's tool on purpose.
- F2 falls if the CTO's P-W2-130-PIN-S4 answer was meant to leave these two cases on HEAD as live checks.

```verdict
{"head": "a300346eb04be6980e0d38e72aca4e630dc992b5", "date": "2026-11-14T09:08:07+00:00", "kpis": [{"kpi": "1-confined", "verdict": "pass", "findings": []}, {"kpi": "2-s4-pinned", "verdict": "pass", "findings": []}, {"kpi": "3-tool-pinned", "verdict": "pass", "findings": [{"id": "F1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "4-no-case-lost-its-point", "verdict": "pass", "findings": []}, {"kpi": "5-map-holds", "verdict": "pass", "findings": []}]}
```
