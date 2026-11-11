# Review record: W2-27's CIT-P, CAP-45.a to Wave 3 (`docs/changes/W2-27-CIT-P.md` at 4bebfe6bb, branch w2/W2-27-citp)

Reviewer: independent, fresh, read-only auditor (MR-4, CAP-33.d), 2026-11-07. I wrote none of the audited files.
The record was asked for at `governance/project/orchestration/reviews/w2-27-citp.md`. The guard refused that path to
this role (DEC-953 item 2), so it is written here, in the review folder the guard allows.

Scope: the note as committed at 4bebfe6bb (base 95eec049), read in `/home/usain/gov-os-worktrees/W2-27-citp`, against
`contract.yaml`, `CONTRACT_v4.md`, `capabilities/CAP-45*.md`, `SOURCE_MAP.csv`, DEC-741, DEC-841, DEC-1083, DEC-1088 (6),
DEC-1089, DEC-1090, DEC-988 (3), DEC-989 (2), `packages/K7-W2-REMAINDER.md`, `packages/LIFT-1/P1-PLAN.md`, WBS §1, §2 and §5,
the tickets named, `docs/plan/tools/validate_w2.py` (read, not run), `validate_s1.py` (read, never run) and
`tests/acceptance/W2-49/` (read, not run). I opened nothing under `~/gov-os-eval/` and no hidden or memory-verdict folder.
Judged under JUDGEMENT.md (ADR-0001's threat model; the two questions; DEC-808's two lines; DEC-1010 item 1).
Verdict convention, as in the earlier review records: a check passes unless it has a finding that blocks (in scope,
ordinary work yes, fails open or loses work). The findings below that do not block still need fixing before the note
goes to the owner.

## What holds (checked, no finding)

- **C1, the quoted texts.** §2's CAP-45 and CAP-45.a text matches `contract.yaml` 2721–2756 and `CONTRACT_v4.md` 712–723 byte
  for byte. The description of `CAP-45.a.md` matches the file (title, heading and `Item:` = 4.2's item; `- **Wave:** W2`).
  The counts are right, recounted from `contract.yaml`: capabilities W1 42 / W2 7 / W3 11 / NONE 2 (62); covers items W1 149 /
  W2 20 / W3 38 / NONE 7 (214); CAP-45.a is CAP-45's only W2 item. No `src/gov/update/` exists and no `update` subcommand
  is registered.
- **C2, the two claims I was asked to check.**
  - `validate_w2.py` reads every `docs/changes/*-CIT-P.md`, approved or not. `cit_p_lines()` takes a `- id:` / `wave:` pair
    only inside a fence whose line is exactly ```` ```yaml ````. W2-49's validator tests copy every CIT-P into their trees
    (`cit_p_files()`). The note has no ```` ```yaml ```` fence (its blocks are `text` and `diff`), so merging it leaves
    `cit-p-lines-applied` and W2-49's validator cases green. After the apply, `cit-p-moved-items` still passes (the WBS
    baseline holds CAP-45.a; the three W2 lines of W2-49 stay applied), and the two two-way checks list 19 items.
  - `require_v42` is called by exactly **32 test functions** (13 in `test_w2_49_contract.py`, 15 in
    `test_w2_49_owner_answers.py`, 1 in `_cit_e.py`, 1 in `_records_v4_2.py`, 2 in `_capability_records.py`). The named cases
    exist. The edge case at `test_w2_49_validator_lines.py:182` injects "CAP-45.a, wave W3" and expects FAIL, so it goes red
    once CAP-45.a is W3.
  - W2-51's suite builds synthetic trees (`plan_v41`, `plan_v42`) and is not affected. No other suite reads the real
    Contract's version, its waves or its counts (W1-48, W2-04, W2-129, W2-134, W2-61h, W1-41 and W1-30 checked).
- **C3, the patches.** The headers, change-log entry, CAP-45 and CAP-45.a hunks of §5.1 apply to the file as it stands.
  The YAML stays valid (the `''` quoting is kept). The counts in the 4.3 entry and in §1 Counts are right: W2 KEPT 7 → 6,
  W3 11 → 12, "All 56 / 4 / 2 / 62" unchanged. The record patches give exactly what a regeneration in CAP-45.b's form gives,
  so W2-49's record-shape test still holds after its version gate. The three source-map rows are exact. Applied with the
  recommended answers, the two forms agree on every wave, the version line and the change log. I found no internal
  inconsistency.
- **C5, F-1 checked.** DEC-841 items 1 to 3 move the nine "through W2-49's CIT-P". DEC-741, which approves that CIT-P,
  predates DEC-841. All nine are still `wave: W2`. W2-109 (`DAEO-6b2q`) is closed; its body reads "Retired by DEC-1083
  (D9-FATES): it built nothing (W-6); K-2 is retired into P1-11's Contract re-baseline". P1-PLAN P1-11 and K-1 to K-3 read
  as quoted. CAP-53.b's split with W2-66 (DEC-880) and CAP-22.b carried lite (`DAEO-lrre`, W2-33) are right. F-2 (K-3: the
  validator advisory until it is re-run) and F-3 are right.
- **C6, the standing rules.** The note proposes no edit to a closed ticket. It leaves W2-24, W2-49, W2-51, W2-16 and W2-02
  untouched. The revision of the closed W2-49's suite goes to a new ticket (DEC-1088 (6)). W2-17, W2-27 and W2-47 are open,
  and each edit is marked with the approving entry. A scan for TODO, TBD, FIXME, XXX, `<placeholder>`, `???` and long
  hex strings finds nothing. The only stand-ins are the declared `APPLY_DATE` and `DEC-OWNER`. The frontmatter satisfies
  `change-impact-proposal.schema.json` (id, type, status, state_class).

## Findings

### F1: the list of W2-49 tests that go red at the apply misses three cases, so two cost lines are low

These cases go red and are not named in §4 row 17 or Question T:
- `test_covers_count_by_wave_is_w1_149_w2_20_w3_38_none_7` (`test_w2_49_owner_answers.py:143`, both sources). It is red
  under **any** V, because the counts become W2 19 / W3 39. Under V (i) it is a `require_v42` caller, but reading the gate
  as "4.2 or later" is not enough: it needs new expected numbers, and T (i)'s recipe does not say so.
- `test_source_map_no_row_but_the_eight_differs_from_before_this_ticket` (`test_w2_49_source_map.py:115`). It is red
  under A (i), because rows 107, 224 and 286 then differ from `ffc60703e373`. It is not a `require_v42` caller.
- `test_yaml_change_log_keeps_every_earlier_version_unchanged` (`test_w2_49_contract.py:77`). It is red under V (i): it
  asserts `version == "4.2"` directly, not through `require_v42`.

So under V (ii), seven functions go red with A (i) and five with A (ii), against the note's "about five" (four). Under A
(i), two more cases go red, not one (Question A says one). The fix is a correction to row 17, Question V (ii)'s and A
(i)'s costs and T (i)'s recipe (new counts; the three source-map rows named as moved by the approving entry).

- Ordinary work: yes, because the test designer and the owner work from row 17 and the costs as written.
- Consequence: other. T (i)'s scoped run of `tests/acceptance/W2-49/` on the merged commit catches any case left out, so
  nothing passes that should fail. The cost is a second revision pass and estimates that are a little low.

### F2: the route (§11) does not say how the apply reaches `w2/integrate` under one merge per ticket and merge-is-close

§11 steps 3 and 4 put the apply round in W2-27 and merge the test-revision ticket "in the same batch as the apply".
- DEC-988 item 3 (one merge per ticket: only a ticket's final, verified result merges) and DEC-989 item 2 (a ticket's
  merge and its close are one step) are both standing.
- W2-27 is EXAMIN's adoption on a copy. It cannot close until K9's entry criteria are met and the adoption is done.
- The test ticket's merge is its close, and its cases are red on any tree without the apply.

As written, the apply either waits on W2-27's branch until W2-27 closes, or needs an interim merge that the rules
forbid. If it waits, the Contract drifts until then, criterion 7 waits on K9, and the test ticket sits open. §4 row 13
also widens an adoption ticket's paths to `docs/contract/**` for the rest of its life. The note should name the
mechanism, and ask the owner only if it needs an exception. Options:
- (a) the apply as a small ticket of its own (product-spec, the Contract paths, this note's CIT-E), merged and closed with
  the test ticket in one queue batch;
- (b) an orchestrator record commit, if the Contract files count as record-only paths;
- (c) held until W2-27's close, with that cost stated.

- Ordinary work: yes, because the CTO reaches this at step 4 by following §11.
- Consequence: other. No work is lost and nothing fails open. It stalls the route or forces a rule exception.

### F3: the recommended set goes beyond what the owner chose in K7-W2-REMAINDER §3, and the note does not say so

K7-W2-REMAINDER §3 option A described the Contract edit as "CAP-45.a's wave field in `contract.yaml`, its record …
regenerated, and a change-log row", for "about half a day". DEC-1090 (5) chose option A on that description. The note's
recommended answers (V (i), A (i), C (i), T (i)) add a capability move, a rewording of the item, a version that touches 276
records, three source-map rows and a new test-designer ticket, ≈ 1 agent day (§6). Each extra is put to the owner as a
question, which is right. The note never says that together they go past the package's description, and it does not
give the cost of the smallest honest set (V (ii), A (ii), C (i): one wave and one text change, five W2-49 cases). One
line in §6 or §7 fixes this.

- Ordinary work: yes, because the owner reads the note against the package it decided on.
- Consequence: other (how the choice is framed; no work lost).

### F4: F-1 is an owner-level choice tied to this note, but it is not one of the owner questions

F-1 is told "for the owner" in §9, with no options and no place in §11 step 2's list of answers (V, A, C, T). It
interacts with this note. W2-109's own KPI named "v4.3" for the nine, so taking 4.3 here re-numbers P1-11's version. If
P1-11 lands after W2-47 starts, the nine become drift or named exceptions. Suggested question N:
- (a) leave the nine to P1-11 and accept the timing risk;
- (b) name the nine as exceptions in W2-46's record now;
- (c) carry the seven mechanical ones here, which needs new owner scope beyond DEC-1090 (5) and more W2-49 revisions.

Also, §4 row 8 shortens WBS §5 item 7's list to seven but leaves its clause "the other nine moved to Wave 3 through
W2-49's CIT-P", which F-1 shows is false. Row 8 should correct that clause or flag it.

- Ordinary work: yes, because the owner answers only the lettered questions, and the orchestrator edits only the rows
  listed.
- Consequence: other (drift that W2-47 finds; nothing fails open).

### F5: W2-47's WBS card is missing from row 15

Row 15 changes W2-47's ticket to "against Contract v4.3" under V (i). The WBS §2 card (line 1455) still reads "against
Contract v4.2 and the decisions", so the ticket and its card would disagree. Add the card line to row 15, marked with
the approving entry. The same check applies to §5 item 11 (line 1871, "Contract v4.2 lite item"), which stays true.

- Ordinary work: yes, because the orchestrator applies rows 8 to 23 as listed.
- Consequence: other (the plan and the ticket disagree; W2-47 reads its ticket).

### F6: row 12 says W2-46's ticket names `gov update`, and it does not

`DAEO-nn1s` line 103 names "the AR lines whose tickets moved to Wave 3" in general. Neither `gov update` nor CAP-45.a
appears in it. W2-24's `gov update` KPI (`DAEO-0mab` line 48) was not among the lines moved to W2-46 (its body says S5
and F1 moved). §8 step 6's expectation ("W2-46's record names `gov update` as a Wave 3 line of AR-10") still works as a
derived expectation through AR-10 (`WAVE_2_LIST.md` line 149). Row 12 should say that, not quote the ticket.

- Ordinary work: yes, because the exit auditor follows §8 step 6 and looks for the line.
- Consequence: other.

### F7: "every record" includes the six master-rule records, which cite version 4.1

`docs/contract/master-rules/MR-1.md` to `MR-6.md` are generated from `contract.yaml` too. They still say "(Contract v4,
version 4.1)", and 4.2 did not touch them. §3 item 5 ("every record's version line") and §8 step 2 ("every record cites
the version in force") include them on a literal reading, so §8 step 2 would fail on six files. Write "every capability
record" and state that the MR records are unchanged, or put them to the owner with V.

- Ordinary work: yes, because the apply round and the exit auditor read the steps literally.
- Consequence: other.

### F8: places that mention CAP-45 or Contract v4.2 but are not in the impact set

None of these needs a change, but the set should name them so it is complete:
- **CAP-45 mentions:** `WAVE_1_WBS.md` 221 and 235; `packages/REPLAN-W2.md` 45; `packages/LIFT-1/pat/A-findings.md` 42 and
  `B-findings.md` 71; `packages/COMPANY-MAP-2026-10-29.md` 22; `S2-CIT-P.md` and `S2-CIT-E.md`; WBS lines 563 and 813
  (W2-24's retired card); `SOURCE_MAP.csv` row 222 (CAP-45 with no wave).
- **Tickets citing v4.2 that are not in row 16:** `DAEO-egsy` (W2-51, closed), `DAEO-ha8z` (W2-49, closed), `DAEO-6b2q`
  (closed) and `DAEO-h4rh` line 69 (W2-27 itself).

- Ordinary work: yes, because a reader checks the set against a grep, as I did.
- Consequence: other.

### F9: the effect on the memory store and the measure is not stated

Under V (i), the apply rewrites 278 files under `docs/contract/`. It inserts about 10 lines into `contract.yaml` (the
4.3 entry, and CAP-45's wave note and sources) and one row into `CONTRACT_v4.md`, so every later line number moves. The
note does not mention the store's refresh and re-embedding of these files, or the measure's re-anchoring of labels on
the Contract's files (DEC-1084). It also does not place the apply relative to the experiment windows (E1 to E5, the
fresh 80 on a fixed pin). The measure runs on pinned clones, so this is probably harmless. One line in §4 settles it.
I opened no evaluation set.

- Ordinary work: yes, because the apply lands on integrate while the experiments run.
- Consequence: other.

### F10: §2's excerpt quietly leaves out eight lines

The block labelled "lines 2721–2756" leaves out lines 2738–2745 (`scenarios`, `disposition`) without an ellipsis. It
also puts `sources` on one line, but declares that. The text it does quote is exact.

- Ordinary work: yes, because a reader compares the line range with the file.
- Consequence: other.

### F11: two patch parts are described rather than given exactly

§5.2's change-table row is "(the text of the 4.3 change_log entry of §5.1, on one line)", and §5.3's removed lines use
"…". The note declares this only for the `decisions` line. The apply round has to derive these texts, including the
`''` → `'` conversion. Also, `DEC-OWNER` is added to `CONTRACT_v4.md`'s `decisions` list, but 4.2 did not add DEC-741
there. That is harmless, but it breaks with precedent.

- Ordinary work: yes, because the apply round works from §5.
- Consequence: other.

### F12: the CAP-33.d route as stated leaves out corroboration

§1 and §11 give the route as "evidence, proposal, one independent review, the owner's approval, then a versioned
promotion". CAP-33.d reads "evidence → corroboration → proposal → independent review → owner approval → versioned
promotion". W2-49's CIT-P also left it out. One line naming what corroborates the change (DEC-1089 and DEC-1090, the
DEC-953 and DEC-954 deferral, and the code read) closes this.

- Ordinary work: yes, because CAP-33's acceptance is read against the route as written.
- Consequence: other.

## Classification (DEC-809)

F1 to F12 are all in scope, ordinary work yes, consequence other. None blocks under DEC-1010 item 1, so READY is
computed as yes. Recommendation: the CTO fixes them in the note's one answer round before it goes to the owner. F1 to
F5 matter most: the correct red list and costs, the merge route, the scope delta, F-1 as a question, and W2-47's card.
F6 to F12 are one-line corrections.

```verdict
{"kpis": [
 {"kpi": "C1", "verdict": "pass", "findings": [
   {"id": "F10", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "C2", "verdict": "pass", "findings": [
   {"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F7", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F8", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F9", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "C3", "verdict": "pass", "findings": [
   {"id": "F11", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "C4", "verdict": "pass", "findings": [
   {"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F12", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "C5", "verdict": "pass", "findings": [
   {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "C6", "verdict": "pass", "findings": []}
]}
```
