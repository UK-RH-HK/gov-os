---
id: W2-27-CIT-P
type: change-impact-proposal
status: ACCEPTED
accepted: owner, 2026-11-07 (DEC-1093 (1), apply now, with the answers V, A, C, R, T and N recorded in section 13; applied by W2-139, DAEO-ongl, its record docs/changes/W2-27-CIT-E.md)
date: 2026-11-07
branch: w2/W2-27-citp
base: 95eec049
ticket: DAEO-h4rh (W2-27)
author: product-spec (single author, DEC-996 item 3 (D))
review: one independent review, then the owner (governance/project/orchestration/packages/K7-W2-REMAINDER.md §3)
review_round: 'reviewed at 4bebfe6bb by a fresh, read-only independent auditor, READY (C1 to C6 pass) with findings F1 to F12; this revision is the one answer round, and section 12 records how each finding was answered'
decisions_carried: [DEC-1089, DEC-1090]
decisions_read: [DEC-105, DEC-722, DEC-741, DEC-750, DEC-841, DEC-880, DEC-941, DEC-953, DEC-954, DEC-974, DEC-988, DEC-989, DEC-1083, DEC-1084, DEC-1088]
state_class: EVIDENCE
---

# W2-27: change-impact proposal (CIT-P) moving CAP-45.a to Wave 3

This change carries the owner's DEC-1089 (2) and DEC-1090 (5) into the Contract. `gov update` (W2-17) is built in
Wave 3, so CAP-45.a, the covers item W2-17 delivers, moves from Wave 2 to Wave 3. The Wave 2 clause that W2-49's CIT-P
added to CAP-45.a (`docs/changes/W2-49-CIT-P.md` §7 D (ii), applied in Contract 4.2) is withdrawn with it. This is
option A of `governance/project/orchestration/packages/K7-W2-REMAINDER.md` §3, and it meets Wave 2's exit criterion 7
for CAP-45.a (`docs/plan/WAVE_2_WBS.md` §5 item 7).

It follows CAP-33's route (CAP-33.d): evidence → corroboration → proposal → independent review → owner approval →
versioned promotion.
- **Evidence:** the deferral of W2-17 and W2-18 (DEC-953 item 10, DEC-954) and of K7's rest (DEC-941 item 3).
- **Corroboration:** the owner's two later entries, DEC-1089 (2) and DEC-1090 (5), and the code read at the base:
  no `gov update` exists (§2).
- **Proposal:** this record.
- **Independent review:** done at `4bebfe6bb`, answered here (§12).
- **Owner approval and versioned promotion:** §11.

**Nobody edits `docs/contract/**` before the owner approves.** The apply is a ticket of its own (Question R), and its
record is `docs/changes/W2-27-CIT-E.md`. W2-27 keeps only this note.

Everything here comes from a named source. Where no source settles a point, it is a **question for the owner** (§7),
with a recommendation. The patch in §5 is written with the recommended answers. **Several recommended answers go
beyond the edit option A described; §3.1 lists them, with the cost of the smallest honest set.**

## 1. What triggers the change

| # | Trigger | Source | State at the base (`95eec049`, Contract 4.2) |
|---|---|---|---|
| T1 | W2-17 (`gov update`) and W2-18 (the pinned install) are deferred to Wave 3. W2-17's stated reason: "CAP-45.a needs a CIT-P note" | DEC-953 item 10 asked for the deferrals; DEC-954 approved "its 19 deferrals to Wave 3"; `packages/PLAN-W2-DEC953.md` §3 (rows W2-17, W2-18) and §6 item 5 | W2-17 (`DAEO-sdhj`) is open, tagged `wave-3, deferred` |
| T2 | The rest of K7 after W2-16 goes to Wave 3. A release path is an entry criterion for EXAMIN's real repository, not for its copy | DEC-941 item 3 | DEC-1089 changes item 3's K7 part |
| T3 | K7 is done for Wave 2, and W2-17 and W2-18 stay in Wave 3. Exit criterion 7's paperwork for CAP-45.a is one of the two items left, and it sits in W2-27 | DEC-1089 (2) (b) | W2-27's ticket has the KPI line "Exit criterion 7: CAP-45.a moved to Wave 3 by an approved CIT-P note … [DEC-1089]" |
| T4 | CAP-45.a takes option A: a CIT-P note moving it to Wave 3 | DEC-1090 (5), under DEC-105 | No note yet |
| T5 | Exit criterion 7 reads "CAP-45.a (W2-17) moves to Wave 3 by a CIT-P note, or is a named exception" | WBS §5 item 7 (DEC-953, DEC-954) | Not met |
| T6 | W2-17 keeps its Wave 3 status after the re-plan | DEC-1083 (D9-FATES). W2-17's ticket: "Wave 3 by DEC-1083 … the status is kept" | — |

## 2. The text today

`docs/contract/contract.yaml`, lines 2721–2756, the parts this change touches. Lines 2738–2745 (`scenarios`,
`disposition`) are left out, at the `…` line, and `sources` is shown on one line. Everything else is quoted exactly.

```text
- id: CAP-45
  title: gov update lifecycle
  outcome: The owner can update the Gov OS in a repository without losing overlay configuration.
  acceptance: '`gov update --check` reports the version change and migrations; `copier update` applies them with the overlay
    files unchanged and `gov doctor` green.'
  wave: W2
  wave_note: 'first real `copier update` in W2; the pending-update report of `gov doctor` is W3 (DEC-165)'
  provider:
  - Copier 9.18.2
  - 'W2: gov update --check'
  - 'W3: gov doctor pending-update report'
  sources: [Contract v3 Gate S5, Framework v4.1.2 §82, Distribution Protocol v1.2 §12, DEC-023, DEC-165]   # one per line in the file
  …  # lines 2738–2745: scenarios and disposition, unchanged
  covers:
  - id: CAP-45.a
    item: 'gov update: check/impact, authenticated source (the signed tag in W3, CAP-02.c), compatibility/migration, overlay
      preserved, adapters regenerated, affected indexes rebuilt, verify, rollback, ledger/provenance; in Wave 2 the authenticated
      source is the release''s manifest and file hashes (CAP-43.b, lite); the signed tag goes with CAP-02.c (W3), DEC-722'
    source: Contract v3 S5; Framework v4.1.2 §82; Distribution Protocol v1.2 §12; DEC-722
    wave: W2
  - id: CAP-45.b
    item: 'In every repository, `gov doctor` compares the installed release with the latest and reports pending updates and their highest lesson severity at session start; the owner decides when to run `gov update`'
    source: 'DEC-165'
    wave: W3
```

`docs/contract/CONTRACT_v4.md`, lines 712–723:

```text
### CAP-45 — gov update lifecycle

- **Outcome:** The owner can update the Gov OS in a repository without losing overlay configuration.
- **Acceptance:** `gov update --check` reports the version change and migrations; `copier update` applies them with the overlay files unchanged and `gov doctor` green.
- **Wave:** W2 (first real `copier update` in W2; the pending-update report of `gov doctor` is W3 (DEC-165))
- **Provider:** Copier 9.18.2, W2: gov update --check, W3: gov doctor pending-update report
- **Disposition:** KEPT
- **Sources:** Contract v3 Gate S5; Framework v4.1.2 §82; Distribution Protocol v1.2 §12; DEC-023; DEC-165
- **Covers:**
  - `CAP-45.a` [W2] gov update: check/impact, authenticated source (the signed tag in W3, CAP-02.c), compatibility/migration, overlay preserved, adapters regenerated, affected indexes rebuilt, verify, rollback, ledger/provenance; in Wave 2 the authenticated source is the release's manifest and file hashes (CAP-43.b, lite); the signed tag goes with CAP-02.c (W3), DEC-722 — Contract v3 S5; Framework v4.1.2 §82; Distribution Protocol v1.2 §12; DEC-722
  - `CAP-45.b` [W3] In every repository, `gov doctor` compares the installed release with the latest and reports pending updates and their highest lesson severity at session start; the owner decides when to run `gov update` — DEC-165
- **Scenarios:** dev CHAOS-A-10, CHAOS-X-01 · qual CHAOS-X-Q01
```

`docs/contract/capabilities/CAP-45.a.md` is DERIVED, generated from `contract.yaml` at version 4.2. Its `title`,
heading and `Item:` line hold the item text above. Its last line is `- **Wave:** W2`.

**What else the base shows.** These were read from the files, not run:
- No `src/gov/update/` exists, and the CLI has no `update` command.
- `contract.yaml` holds 20 Wave 2 covers items and 7 Wave 2 capabilities (counted from the file).
- CAP-45.a is CAP-45's only Wave 2 item. CAP-45.b is already W3 (DEC-165).

## 3. The change

1. **CAP-45.a: `wave: W2` → `wave: W3`.** Its source gains DEC-1090.
2. **The Wave 2 clause is withdrawn.** It reads "in Wave 2 the authenticated source is the release's manifest and file
   hashes (CAP-43.b, lite); the signed tag goes with CAP-02.c (W3)". A Wave 3 item that describes its own Wave 2 form
   contradicts itself.
   - The manifest and file hashes stay part of the authenticated source, beside the signed tag.
   - Reason: W2-16 built them (CAP-43.b, lite, closed), and W2-17's own KPI checks them ("verifies the target release's
     manifest and file hashes").
   - Question C (§7) gives the other wordings.
3. **CAP-45 itself moves to W3 with it** (recommended; Question A).
   - Its acceptance is `gov update --check` plus a real `copier update`, and only W2-17 builds those.
   - The Contract's own field rule says `wave` is "the wave in which the acceptance check must pass".
   - Its wave note and provider follow.
4. **The Contract becomes version 4.3** (recommended; Question V). Both files get a change-log entry, and §1 Counts
   follows Question A.
5. **The derived capability records follow.** CAP-45.a's record is regenerated, and CAP-45's record follows Question A.
   Every capability record's version line follows Question V. The six master-rule records under
   `docs/contract/master-rules/` say "(Contract v4, version 4.1)", which 4.2 did not change; this change leaves them as
   they are.
6. **Two new tickets carry the work:** an apply ticket and a test-revision ticket (Questions R and T). Both are proposed
   to the owner with this note, because a new ticket is the owner's before it is filed (DEC-974 item 2).

### 3.1 What goes beyond option A as the owner chose it

K7-W2-REMAINDER §3 described option A's Contract edit as "CAP-45.a's wave field in `contract.yaml`, its record
`docs/contract/capabilities/CAP-45.a.md` regenerated, and a change-log row", for "about half a day". DEC-1090 (5) chose
option A on that description. The recommended answers go further:

| Recommended answer | What it adds beyond option A's description | Why it is recommended |
|---|---|---|
| A (i): CAP-45 itself to W3 | A capability-level move, §1 Counts, three source-map rows | Otherwise the capability's acceptance check is one no Wave 2 ticket can pass |
| V (i): version 4.3 | A version change touching every capability record's version line, plus the W2-49 suite's version gate | One version per text keeps W2-47's reference exact |
| C (i): the item reworded | The withdrawn clause and a new wording of the authenticated source | Some rewording is needed under any honest answer (C (iii) contradicts itself) |
| R and T: two new tickets | An apply ticket and a test-revision ticket | Needed under every answer: W2-49's suite goes red at any apply, and W2-27 cannot carry the apply (Question R) |

**The smallest honest set is V (ii), A (ii), C (i), with R and T.** It contains:
- one wave change and one text change, as a "same version" amendment to the 4.2 entry and row;
- `CAP-45.a.md` regenerated;
- five W2-49 functions revised.

Its cost is about half a day in all, which matches the package's estimate plus the two small tickets. The recommended
set costs about one agent day (§6).

## 4. The impact set

How it was found: `grep` over the tree and `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store` (the store
at integrate's head, which equals this worktree's base), then reading each hit.
- "The apply" means the apply ticket of Question R, after the owner's approval.
- A closed ticket is never edited (DEC-1088 (6)). An open ticket changes only with the deciding entry marked on it.

| # | Place | What it says now | What changes at the apply | Who changes it |
|---|---|---|---|---|
| 1 | `docs/contract/contract.yaml`: header, `change_log`, CAP-45 and CAP-45.a | 4.2. CAP-45 and CAP-45.a are `W2` (§2) | The patch of §5.1 | The apply ticket (product-spec, Question R) |
| 2 | `docs/contract/CONTRACT_v4.md`: frontmatter, title, version line, change table, §1 Counts, the CAP-45 block | The same content (§2). §1 Counts: W2 7, W3 11 | The patch of §5.2 | Same |
| 3 | `docs/contract/capabilities/CAP-45.a.md` | Title, heading and `Item:` hold 4.2's item. `Wave:` W2 | Regenerated from the approved `contract.yaml` (§5.3) by a throwaway generator. The generator first reproduces the unchanged records byte for byte, as W2-49's CIT-E did | Same |
| 4 | `docs/contract/capabilities/CAP-45.md` | `Wave:` W2 | `Wave:` W3 under A (i); unchanged under A (ii) | Same |
| 5 | The other 274 capability records under `docs/contract/capabilities/` (276 in all) | Each says "(Contract v4, version 4.2)" once | Only that occurrence changes, to 4.3, under V (i) (DEC-741 K (1)'s precedent). Nothing changes under V (ii) | Same |
| 6 | `docs/contract/master-rules/MR-1.md` to `MR-6.md` | "(Contract v4, version 4.1)" | **Unchanged.** 4.2 left them at 4.1, and this change touches no master rule | Nobody |
| 7 | `docs/contract/SOURCE_MAP.csv` rows 107, 224, 286 (Contract v3 S5, Framework §82, Distribution Protocol §12) | "Contract v4 CAP-45 (KEPT, wave W2)" | "wave W3" under A (i) (§5.4); unchanged under A (ii). Row 222 (Framework §80) names CAP-45 with no wave and stays as it is | The apply ticket |
| 8 | `docs/changes/W2-49-CIT-P.md` §7 D (ii) and §13 D; `W2-49-CIT-E.md` | The approved Wave 2 clause and its apply | **Unchanged.** Both are approved records. This note supersedes D (ii)'s clause, and the CIT-E of this change says so | Nobody |
| 9 | `docs/plan/WAVE_2_WBS.md` §5 item 7 (lines 1864–1865) | "CAP-45.a (W2-17) moves to Wave 3 by a CIT-P note, or is a named exception". Its list of "eight" items includes CAP-45.a. Its clause "the other nine moved to Wave 3 through W2-49's CIT-P" is **false against the Contract**: all nine are still W2 (§9 F-1) | Marked met for CAP-45.a, with the approving entry and the apply commit. CAP-45.a leaves the list, which becomes seven. The false clause is corrected to "the other nine decided for Wave 3 by DEC-841, not yet in the Contract", plus what the owner answers to Question N | The orchestrator, after the approval (the plan is the owner's, DEC-729; the approval covers this edit) |
| 10 | WBS §2, W2-17's card (line 559) | "CAP-45.a moves to Wave 3 by a CIT-P note, or is a named exception" | "CAP-45.a moved to Wave 3 by W2-27's CIT-P", with the approving entry | The orchestrator |
| 11 | WBS §1, "The Contract's 17 Wave 2 items, by ticket" (lines 250–264, with the line "CAP-45.a → W2-17"), and §1's table row W2-17 (line 143, already "Wave 3") | Revision 3's baseline | **Unchanged.** `validate_w2.py`'s `cit-p-moved-items` reads this list as the baseline for judging moves into Wave 2 (`wbs()`). Editing it would change that baseline, and a move out of Wave 2 needs no baseline change | Nobody |
| 12 | `.tickets/DAEO-sdhj.md` (W2-17, **open**, Wave 3) | Body: "CAP-45.a moves to Wave 3 by a CIT-P note or is a named exception". `closes: [CAP-45.a, AR-10]`. KPI `[CAP-45.a, W2-M176]` | The body line says the move is done, marked with the approving entry. `closes`, KPIs and `sources` are unchanged: W2-17 still delivers CAP-45.a, now in its own wave | The orchestrator (DEC-1088 (6): an open ticket, marked) |
| 13 | `.tickets/DAEO-0mab.md` (W2-24, **closed**, retired by DEC-1083) | KPI line 48: "`gov update` moves the fixture to a second release and back [CAP-45.a]". Its body names the step a Wave 3 line | **Not edited** (DEC-1088 (6)). This KPI was not among the lines moved to W2-46 (W2-24's body moves S5 and F1). `DAEO-nn1s` line 103 names "the AR lines whose tickets moved to Wave 3" in general, not `gov update`. So W2-46's record names `gov update` as Wave 3 by deduction, through AR-10 (`WAVE_2_LIST.md` line 146 heading, line 149) | Nobody |
| 14 | `.tickets/DAEO-h4rh.md` (W2-27, **open**) | `allowed_paths`: `docs/plan/wave-2/examin-copy/**` and `docs/changes/W2-27-CIT-P.md`. Its DEC-1089 section: "`docs/contract/**` joins the paths only once the owner approves its edit". KPI line 87 (exit criterion 7). KPI line 69: "the lite A7 and A10 gates of Contract v4.2" | **`allowed_paths` unchanged:** W2-27 keeps only this note (Question R). The DEC-1089 section's path line gets a marked note that the apply belongs to the apply ticket, with the approving entry. KPI line 87 is met when the apply ticket closes. Line 69 stays true, because CAP-44.f is unchanged | The orchestrator |
| 15 | `.tickets/DAEO-nn1s.md` (W2-46, open) | AR lines whose tickets moved to Wave 3 are named Wave 3 in its record | **No ticket change.** Its record names CAP-45.a as moved by this change | W2-46's run |
| 16 | `.tickets/DAEO-jip3.md` (W2-47, open), and **its WBS §2 card (line 1455)** | Both read "a finding row to every Wave 2 covers item, every Contract v4.2 lite item … against Contract v4.2 and the decisions" | Under V (i), ticket and card both read "against Contract v4.3", each marked with the approving entry. "Contract v4.2 lite item" stays, since the lite items are unchanged. WBS §5 item 11 (line 1871, "Contract v4.2 lite item") stays true and unchanged. Under V (ii), nothing changes | The orchestrator |
| 17 | Tickets citing "Contract v4.2": `DAEO-csj8` (W2-28, open), `DAEO-siiz` (W2-52, in progress), `DAEO-zflj` (W2-02, closed), `DAEO-49o5` (W2-16, closed), `DAEO-egsy` (W2-51, closed), `DAEO-ha8z` (W2-49, closed), `DAEO-6b2q` (W2-109, closed) | They cite v4.2's CAP-44.h, CAP-44.f, CAP-43.b, its lite items, or the version itself | **No change.** CAP-43 and CAP-44 are untouched, so each reference stays true in 4.3. The closed tickets are never edited. W2-109's "v4.3" for DEC-841's nine is a retired ticket's KPI (Question N) | Nobody |
| 18 | `tests/acceptance/W2-49/` (W2-49 is **closed**) | Pins the Contract at 4.2 (the helper `require_v42`, called by 32 test functions); holds CAP-45.a at W2; fixes the covers counts and the source map against their bases; has a validator edge case built on CAP-45.a | Red at the apply (read, not run). Under **V (i), A (i)**: the helper (which fixes its 32 callers in one place) and **ten functions with new content**: `test_w2_49_contract.py:69` (`test_yaml_version_is_4_2_with_a_change_log_entry_citing_dec_722`) and `:77` (`test_yaml_change_log_keeps_every_earlier_version_unchanged`), both asserting `version == "4.2"` directly; the "exactly" tests `test_no_other_covers_item_changes_wave` and `test_no_capability_is_added_removed_or_changes_wave`; the D (ii) tests `test_cap_45a_stays_w2_with_the_release_manifest_and_hashes_as_its_wave_2_source` and `test_cap_45a_names_no_signed_tag_as_a_wave_2_requirement`; `test_w2_49_owner_answers.py:143` (`test_covers_count_by_wave_is_w1_149_w2_20_w3_38_none_7`, red under any V: the counts become W2 19 / W3 39); K (1)'s `test_every_capability_record_cites_contract_version_4_2`; `test_w2_49_source_map.py:115` (`test_source_map_no_row_but_the_eight_differs_from_before_this_ticket`, red under A (i): rows 107, 224 and 286 differ from `ffc60703e373`); and `test_w2_49_validator_lines.py:182`, which injects "CAP-45.a, wave W3" and expects it **unapplied**. Under **V (ii)**: seven functions with A (i) (the two "exactly", the two D (ii), the counts, the source map, the edge case), five with A (ii) | The test-revision ticket (Question T), role independent-test-designer (MR-3; DEC-1088 (6), since W2-49 is closed). Each case is revised with a `Rewrite-Reason:` naming the approving entry |
| 19 | `docs/plan/tools/validate_w2.py` (W2-51's validator; W2-51 closed) | `contract-items-delivered` and `contract-items-cited-by-tests` read every `W2` item of `contract.yaml`. `cit-p-lines-applied` reads every `- id:` / `wave:` pair inside a ```` ```yaml ```` block of `docs/changes/*-CIT-P.md` | **No code change.** After the apply, both two-way checks list 19 Wave 2 items, without CAP-45.a. **This note's patches are ```` ```diff ```` blocks on purpose.** A ```` ```yaml ```` line "CAP-45.a, wave W3" would make `cit-p-lines-applied` fail on the tree until the apply, and W2-49's "both checks pass on this tree" case with it | Nobody |
| 20 | `docs/plan/tools/validate_s1.py` (Wave 1's validator) | Checks that CAP-45.b is W3 (line 341) | **Unchanged.** It is Wave 1's record, and its CAP-45.b check holds | Nobody |
| 21 | `docs/plan/WAVE_2_LIST.md` (AR-10, lines 146–158) and `WAVE_2_TRIAGE.md` row W2-M176 (triaged to W2-17) | `gov update (CAP-45.a)` as part of AR-10; W2-M176 triaged to W2-17 | **No text change by this note.** The row follows W2-17 to Wave 3 in exit criterion 10's accounting | The orchestrator, at exit criterion 10 |
| 22 | History and packages that name CAP-45 or CAP-45.a: `WAVE_2_REVISED_PLAN.md` 315 and 469; `WAVE_1_WBS.md` 221 and 235; WBS 563 (W2-17's card KPI) and 813 (W2-24's retired card); `packages/PLAN-W2-DEC953.md`, `K7-W2-REMAINDER.md`, `REPLAN-W2.md` 45, `COMPANY-MAP-2026-10-29.md` 22, `LIFT-1/pat/A-findings.md` 42, `LIFT-1/pat/B-findings.md` 71; `S2-CIT-P.md`, `S2-CIT-E.md`; `docs/assessment/2026-10/*` | Records of their time | **Unchanged** | Nobody |
| 23 | `governance/adoption/A1-inventory.md`, `A2-classification.md`, `A3-target-path-map.md` | They list the CAP-45 record paths | **Unchanged** (pinned evidence, DEC-718) | Nobody |
| 24 | `docs/DECISION_REGISTER.md`; `governance/project/orchestration/DECISIONS-IN-FORCE.md` | DEC-1089, DEC-1090 | The owner's approving entry, recorded by the orchestrator (`Decided-by: owner`), and its line in the in-force list | The orchestrator |
| 25 | `src/` | `gov links` (`src/gov/links/check.py`) reads Contract ids, not waves | **No change.** No code reads CAP-45.a's wave, and no `gov update` code exists | Nobody |
| 26 | `docs/contract/readiness-dimensions.yaml`, `docs/spec/gov-os/READINESS.md` | No CAP-45 entry | No change | Nobody |
| 27 | The memory store and the measure | The store indexes `docs/contract/**`. The measure's labels can anchor on the Contract's lines | Under V (i) and A (i), the apply rewrites 279 files under `docs/contract/` (276 records, the two Contract files, the source map). It also adds about ten lines to `contract.yaml` and one row to `CONTRACT_v4.md`, so later line numbers move. The integration store re-indexes and re-embeds them at its next rebuild. The measure runs on pinned clones, so it sees the change only at the next re-pin, and then re-anchors its labels in memory (DEC-1084). **Recommended:** the batch merges outside an experiment window | The CTO places the merge |

**Radius.** The change touches:
- one covers item's wave (two Contract lines per file), and one capability with it under A (i);
- one item's text and the change log;
- three source-map rows (A (i));
- 276 derived version lines (V (i)) or none (V (ii));
- the text of two open tickets (W2-17, W2-47) and of W2-47's card;
- two WBS §5 and §2 lines;
- the acceptance suite of one closed ticket, revised under a new ticket.

No code changes. No exit criterion other than 7 is touched.

## 5. The Contract edit (applied only after the owner's approval)

Written with the recommended answers: V (i), A (i), C (i). In the patch, `APPLY_DATE` stands for the date of the apply
commit and `DEC-OWNER` for the owner's approving entry; the apply ticket fills both. If the owner answers otherwise,
the apply follows the answer, and the CIT-E lists each difference.

### 5.1 `docs/contract/contract.yaml`

```diff
@@ header @@
-version: '4.2'
+version: '4.3'
 date: '2026-09-30'
-revised: '2026-10-17'
+revised: 'APPLY_DATE'
@@ change_log: a new entry after the 4.2 entry (4.0, 4.1 and 4.2 unchanged) @@
+- version: '4.3'
+  date: 'APPLY_DATE'
+  change: 'W2-27 specification change (docs/changes/W2-27-CIT-P.md, W2-27-CIT-E.md), approved by the owner (DEC-OWNER).
+    Carries DEC-1089 (2) and DEC-1090 (5): gov update is built in Wave 3, so CAP-45.a moves from Wave 2 to Wave 3, and
+    CAP-45 with it, since no Wave 2 part of it remains. The Wave 2 clause of version 4.2 (in Wave 2 the authenticated
+    source is the release''s manifest and file hashes, DEC-741 D) is withdrawn; the manifest and file hashes stay part
+    of the authenticated source, beside the signed tag (CAP-02.c). 62 capabilities (W2 7 → 6, W3 11 → 12); 214 covers
+    items (W2 20 → 19, W3 38 → 39).'
@@ CAP-45 @@
-  wave: W2
-  wave_note: 'first real `copier update` in W2; the pending-update report of `gov doctor` is W3 (DEC-165)'
+  wave: W3
+  wave_note: 'gov update and the first real `copier update` are W3 (DEC-1089, DEC-1090); the pending-update report of
+    `gov doctor` is W3 (DEC-165)'
   provider:
   - Copier 9.18.2
-  - 'W2: gov update --check'
+  - 'W3: gov update --check'
   - 'W3: gov doctor pending-update report'
   sources:
   - Contract v3 Gate S5
   - Framework v4.1.2 §82
   - Distribution Protocol v1.2 §12
   - DEC-023
   - DEC-165
+  - DEC-1090
@@ CAP-45.a @@
   - id: CAP-45.a
-    item: 'gov update: check/impact, authenticated source (the signed tag in W3, CAP-02.c), compatibility/migration, overlay
-      preserved, adapters regenerated, affected indexes rebuilt, verify, rollback, ledger/provenance; in Wave 2 the authenticated
-      source is the release''s manifest and file hashes (CAP-43.b, lite); the signed tag goes with CAP-02.c (W3), DEC-722'
-    source: Contract v3 S5; Framework v4.1.2 §82; Distribution Protocol v1.2 §12; DEC-722
-    wave: W2
+    item: 'gov update: check/impact, authenticated source (the signed tag, CAP-02.c, and the release''s manifest and file
+      hashes, CAP-43.b), compatibility/migration, overlay preserved, adapters regenerated, affected indexes rebuilt, verify,
+      rollback, ledger/provenance'
+    source: Contract v3 S5; Framework v4.1.2 §82; Distribution Protocol v1.2 §12; DEC-722; DEC-1090
+    wave: W3
```

### 5.2 `docs/contract/CONTRACT_v4.md`

In the `decisions` line, only DEC-1089 and DEC-1090 are appended. The approving entry is not added there, following
4.2, which added the decision it carried (DEC-722) but not its approval (DEC-741). The rest of the list stays as it is
and is written `[…]` below. The change-table row is the 4.3 `change_log` text on one line, with `''` written `'`.

```diff
@@ frontmatter @@
-version: "4.2"
-revised: 2026-10-17
+version: "4.3"
+revised: APPLY_DATE
-decisions: [… , DEC-174, DEC-722]
+decisions: [… , DEC-174, DEC-722, DEC-1089, DEC-1090]
@@ title and version line @@
-# Governance OS — Capability Acceptance Contract v4 (version 4.2)
+# Governance OS — Capability Acceptance Contract v4 (version 4.3)
-**Version 4.2** (2026-10-17). The file names and the id `CONTRACT-v4` are unchanged.
+**Version 4.3** (APPLY_DATE). The file names and the id `CONTRACT-v4` are unchanged.
@@ change table: a new row after the 4.2 row (the 4.0, 4.1 and 4.2 rows unchanged) @@
+| 4.3 | APPLY_DATE | W2-27 specification change (docs/changes/W2-27-CIT-P.md, W2-27-CIT-E.md), approved by the owner (DEC-OWNER). Carries DEC-1089 (2) and DEC-1090 (5): gov update is built in Wave 3, so CAP-45.a moves from Wave 2 to Wave 3, and CAP-45 with it, since no Wave 2 part of it remains. The Wave 2 clause of version 4.2 (in Wave 2 the authenticated source is the release's manifest and file hashes, DEC-741 D) is withdrawn; the manifest and file hashes stay part of the authenticated source, beside the signed tag (CAP-02.c). 62 capabilities (W2 7 → 6, W3 11 → 12); 214 covers items (W2 20 → 19, W3 38 → 39). |
@@ §1 Counts @@
-| W2 | 7 | 0 | 0 | 7 |
-| W3 | 11 | 0 | 0 | 11 |
+| W2 | 6 | 0 | 0 | 6 |
+| W3 | 12 | 0 | 0 | 12 |
@@ CAP-45 block @@
-- **Wave:** W2 (first real `copier update` in W2; the pending-update report of `gov doctor` is W3 (DEC-165))
-- **Provider:** Copier 9.18.2, W2: gov update --check, W3: gov doctor pending-update report
+- **Wave:** W3 (gov update and the first real `copier update` are W3 (DEC-1089, DEC-1090); the pending-update report of `gov doctor` is W3 (DEC-165))
+- **Provider:** Copier 9.18.2, W3: gov update --check, W3: gov doctor pending-update report
 - **Disposition:** KEPT
-- **Sources:** Contract v3 Gate S5; Framework v4.1.2 §82; Distribution Protocol v1.2 §12; DEC-023; DEC-165
+- **Sources:** Contract v3 Gate S5; Framework v4.1.2 §82; Distribution Protocol v1.2 §12; DEC-023; DEC-165; DEC-1090
 - **Covers:**
-  - `CAP-45.a` [W2] gov update: check/impact, authenticated source (the signed tag in W3, CAP-02.c), compatibility/migration, overlay preserved, adapters regenerated, affected indexes rebuilt, verify, rollback, ledger/provenance; in Wave 2 the authenticated source is the release's manifest and file hashes (CAP-43.b, lite); the signed tag goes with CAP-02.c (W3), DEC-722 — Contract v3 S5; Framework v4.1.2 §82; Distribution Protocol v1.2 §12; DEC-722
+  - `CAP-45.a` [W3] gov update: check/impact, authenticated source (the signed tag, CAP-02.c, and the release's manifest and file hashes, CAP-43.b), compatibility/migration, overlay preserved, adapters regenerated, affected indexes rebuilt, verify, rollback, ledger/provenance — Contract v3 S5; Framework v4.1.2 §82; Distribution Protocol v1.2 §12; DEC-722; DEC-1090
```

### 5.3 The derived records

`CAP-45.a.md` in full after the apply. Every line not shown in the diff below is unchanged:

```diff
@@ docs/contract/capabilities/CAP-45.a.md @@
-title: 'gov update: check/impact, authenticated source (the signed tag in W3, CAP-02.c), compatibility/migration, overlay preserved, adapters regenerated, affected indexes rebuilt, verify, rollback, ledger/provenance; in Wave 2 the authenticated source is the release''s manifest and file hashes (CAP-43.b, lite); the signed tag goes with CAP-02.c (W3), DEC-722'
+title: 'gov update: check/impact, authenticated source (the signed tag, CAP-02.c, and the release''s manifest and file hashes, CAP-43.b), compatibility/migration, overlay preserved, adapters regenerated, affected indexes rebuilt, verify, rollback, ledger/provenance'
-# CAP-45.a: gov update: check/impact, authenticated source (the signed tag in W3, CAP-02.c), compatibility/migration, overlay preserved, adapters regenerated, affected indexes rebuilt, verify, rollback, ledger/provenance; in Wave 2 the authenticated source is the release's manifest and file hashes (CAP-43.b, lite); the signed tag goes with CAP-02.c (W3), DEC-722
+# CAP-45.a: gov update: check/impact, authenticated source (the signed tag, CAP-02.c, and the release's manifest and file hashes, CAP-43.b), compatibility/migration, overlay preserved, adapters regenerated, affected indexes rebuilt, verify, rollback, ledger/provenance
-A covers item of CAP-45 (gov update lifecycle). Generated from `docs/contract/contract.yaml` (Contract v4, version 4.2), which is the authority (DEC-614).
+A covers item of CAP-45 (gov update lifecycle). Generated from `docs/contract/contract.yaml` (Contract v4, version 4.3), which is the authority (DEC-614).
-- **Item:** gov update: check/impact, authenticated source (the signed tag in W3, CAP-02.c), compatibility/migration, overlay preserved, adapters regenerated, affected indexes rebuilt, verify, rollback, ledger/provenance; in Wave 2 the authenticated source is the release's manifest and file hashes (CAP-43.b, lite); the signed tag goes with CAP-02.c (W3), DEC-722
+- **Item:** gov update: check/impact, authenticated source (the signed tag, CAP-02.c, and the release's manifest and file hashes, CAP-43.b), compatibility/migration, overlay preserved, adapters regenerated, affected indexes rebuilt, verify, rollback, ledger/provenance
-- **Wave:** W2
+- **Wave:** W3
@@ docs/contract/capabilities/CAP-45.md @@
-Generated from `docs/contract/contract.yaml` (Contract v4, version 4.2), which is the authority; this record exists so that the id resolves (DEC-614).
+Generated from `docs/contract/contract.yaml` (Contract v4, version 4.3), which is the authority; this record exists so that the id resolves (DEC-614).
-- **Wave:** W2
+- **Wave:** W3
```

In each of the other 274 capability records, the one occurrence of `(Contract v4, version 4.2)` becomes
`(Contract v4, version 4.3)`, and nothing else changes. All 276 hold exactly one occurrence at the base (counted). The
six master-rule records are not touched (§4 row 6).

### 5.4 `docs/contract/SOURCE_MAP.csv`

```diff
-Contract v3,S5. `gov update`,OK,"Contract v4 CAP-45 (KEPT, wave W2) — sub-requirements in each capability's covers list (DEC-092)"
+Contract v3,S5. `gov update`,OK,"Contract v4 CAP-45 (KEPT, wave W3) — sub-requirements in each capability's covers list (DEC-092)"
-Framework v4.1.2,82. `gov update`,OK,"Contract v4 CAP-45 (KEPT, wave W2) — sub-requirements in each capability's covers list (DEC-092)"
+Framework v4.1.2,82. `gov update`,OK,"Contract v4 CAP-45 (KEPT, wave W3) — sub-requirements in each capability's covers list (DEC-092)"
-Distribution Protocol v1.2,12. `gov update`,OK,"Contract v4 CAP-45 (KEPT, wave W2) — sub-requirements in each capability's covers list (DEC-092)"
+Distribution Protocol v1.2,12. `gov update`,OK,"Contract v4 CAP-45 (KEPT, wave W3) — sub-requirements in each capability's covers list (DEC-092)"
```

### 5.5 The version it makes

**Contract v4, version 4.3** (V (i)). The file names and the id `CONTRACT-v4` are unchanged.

| | Before | After |
|---|---|---|
| Capabilities | W1 42 / W2 7 / W3 11 / NONE 2 (62) | W1 42 / W2 6 / W3 12 / NONE 2 (62) |
| Covers items | W1 149 / W2 20 / W3 38 / NONE 7 (214) | W1 149 / W2 19 / W3 39 / NONE 7 (214) |

Under A (ii), the capability counts stay as they are. Under V (ii), the version stays 4.2, and the change is a "same
version" amendment appended to the 4.2 entry and row.

## 6. The three options (DEC-105)

DEC-105 and CAP-33.e ask a CIT-P that changes a closed specification to give three options with their costs. The owner
has already chosen one: DEC-1090 (5), option A, the note. They are restated here for the record.

| Option | What it means here | Cost |
|---|---|---|
| **Apply now** (the owner's choice) | This note, its review and answer round, the owner's approval, the apply ticket (§5 and the CIT-E) and the test-revision ticket, merged in one batch. The Contract then says Wave 3 for the work Wave 3 does | **Recommended set: ≈ 1 agent day in all, 0 days on any critical path.** It runs on the CPU beside the experiments and touches nothing in EXAMIN's copy. The parts: this note, its review and the answer round (≈ 4 h); one owner reading (≈ 15 min); the apply ticket (≈ 1–2 h); the test-revision ticket (≈ 3 h under V (i) and A (i): the helper and ten functions; ≈ 1 h under V (ii)) with a scoped run of `tests/acceptance/W2-49/`; the orchestrator's edits (§4 rows 9, 10, 12, 14, 16, 24; ≈ 30 min); one merge-queue batch. **Smallest honest set** (V (ii), A (ii), C (i), §3.1): ≈ half a day, as option A was described, plus the two small tickets |
| **Defer** (record it and continue) | The Contract keeps CAP-45.a in Wave 2. Exit criterion 7 is met only by a named exception in W2-46's record, which the owner accepts at the exit (K7-W2-REMAINDER §3, option B) | **Nothing now.** One owner act at the exit. The Contract says Wave 2 for Wave 3 work until Wave 3, and the exit audit (W2-47) names the drift as a finding. CAP-45's capability wave (W2) drifts with it |
| **Re-baseline** (reopen and re-plan) | Reopen CAP-45 whole together with the release-and-update work (K7's rest: W2-17, W2-18, CAP-02.c, CAP-43.c and .d), re-plan it for Wave 3, and carry it in P1-11's single Contract re-baseline (`packages/LIFT-1/P1-PLAN.md`, P1-11: "One CIT-P/CIT-E and the Contract re-baseline", last), beside DEC-841's nine items (K-2) | **No separate round now, but a larger one later.** P1-11 is estimated at "half a day of product-spec plus one review plus ~30 min of the owner" for its present content, and more with CAP-45 and K7's rest re-planned. The re-plan of W2-17 and W2-18 is the owner's (DEC-729). P1-11 runs "last", after the rows and switches are decided. If it lands after W2-46 starts, exit criterion 7 fails for CAP-45.a unless it is named as an exception. Nothing in the evidence calls for reopening the update lifecycle: DEC-1089 only moves its wave |

**Recommendation: apply now**, as the owner chose (DEC-1090 (5)). It is the cheapest option that leaves no drift at the
exit audit (DEC-1090 (5)'s basis: "the Contract matches the waves"), and it does not wait on P1-11's timing.
*Confidence:* high.

## 7. Questions for the owner (with the approval of this note)

V, A and C decide how far the edit goes (§3.1 lists what goes beyond option A). R and T are the two new tickets
(DEC-974 item 2). N is DEC-841's nine items.

**V. The version.** CAP-33.d asks for "versioned promotion", and CAP-33.e and DEC-105 say "every version is kept".
Version 4.1 has precedents for owner-decided amendments made "same version", including a wave move (CAP-41.f to W1,
DEC-168) and new covers items (DEC-235, DEC-248, DEC-255).

- (i) **Version 4.3** (recommended; beyond option A's description).
  - Every capability record's version line is regenerated (a script, minutes).
  - W2-49's suite gets its version gate read as "4.2 or later" in the helper, plus ten functions with new content
    (§4 row 18; ≈ 3 h of a test designer, Question T). That revision also serves P1-11's later re-baseline, which will
    change the version again.
  - W2-47's ticket and card name 4.3 (§4 row 16).
- (ii) **Same version 4.2.** The move is appended to the 4.2 entry and row as a "same version" amendment, as in 4.1.
  - No record's version line changes.
  - W2-49 needs seven functions revised under A (i), five under A (ii) (≈ 1 h).
  - The catch: "Contract v4.2", which W2-28, W2-47 and W2-52 cite, then names two texts, and the exit audit has to
    tell them apart by commit.
- *Recommendation:* (i). A wave move changes what the exit audit checks, and one version per text keeps W2-47's
  reference exact. *Confidence:* medium.

**A. CAP-45 itself.** The owner's words move CAP-45.a. CAP-45's own `wave` is W2. Its acceptance (`gov update
--check`; `copier update` with the overlay unchanged and `gov doctor` green) can pass only once W2-17 is built. CAP-45.b
is already W3.

- (i) **CAP-45 moves to W3 with CAP-45.a** (recommended; beyond option A's description).
  - Its wave note, provider and sources follow (§5.1), and §1 Counts goes W2 7 → 6, W3 11 → 12.
  - Three source-map rows change (§5.4).
  - Two more W2-49 cases need revising: `test_no_capability_is_added_removed_or_changes_wave` and
    `test_source_map_no_row_but_the_eight_differs_from_before_this_ticket`.
- (ii) **CAP-45 stays W2.** It then has no Wave 2 covers item, and an acceptance check no Wave 2 ticket can pass.
- *Recommendation:* (i). The Contract's field rule makes `wave` "the wave in which the acceptance check must pass".
  Under (ii) the drift the owner's choice removes stays, one level up. *Confidence:* high.

**C. The Wave 2 clause (DEC-741 D (ii)).**

- (i) **Withdraw the "in Wave 2" clause and keep the manifest and file hashes inside the authenticated source,**
  beside the signed tag (recommended, §5.1). This matches what W2-16 built and what W2-17's KPI checks.
- (ii) **Restore 4.1's wording,** "authenticated source (signed tag)", and drop the manifest and file hashes from the
  item. This loses a check that W2-17's KPI already has.
- (iii) **Keep the item text as it is** and change only the wave. The item would then describe its own Wave 2 form
  while it sits in Wave 3.
- *Recommendation:* (i). *Confidence:* medium-high.

**R. How the apply reaches `w2/integrate`.** Two standing rules apply. Only a ticket's final, verified result merges
(DEC-988 item 3). A ticket's merge and its close are one step (DEC-989 item 2). W2-27 is EXAMIN's adoption on a copy:
it cannot close until K9's entry criteria are met and the adoption is done.

- (a) **A separate apply ticket** (recommended).
  - Role product-spec, profile STANDARD.
  - Paths: `docs/contract/contract.yaml`, `docs/contract/CONTRACT_v4.md`, `docs/contract/capabilities/**`,
    `docs/contract/SOURCE_MAP.csv` and `docs/changes/W2-27-CIT-E.md`.
  - KPIs: §5 applied as approved, with each difference in the CIT-E. It is judged by W2-49's suite as the
    test-revision ticket leaves it.
  - It merges and closes **in one merge-queue batch with the test-revision ticket**, on one green run of the queue over
    the combined candidate. W2-27 keeps only this note, its paths stay as they are, and its KPI line 87 is met when the
    apply ticket closes.
  - Cost: one small ticket, ≈ 1–2 h, and no exception to either rule.
- (b) **An orchestrator record commit.** This works only if the Contract files count as record-only paths, and no
  decision says they do. The apply would also get no ticket of its own to close.
- (c) **Held on W2-27's branch until W2-27 closes.** The Contract drifts until then, exit criterion 7 waits on K9, the
  test-revision ticket sits open, and an adoption ticket holds `docs/contract/**` for the rest of its life.
- *Recommendation:* (a). *Confidence:* high.

**T. Who revises W2-49's acceptance tests.** W2-49 is closed, so revising its suite is new work (DEC-1088 (6)). Only an
independent test designer writes under `tests/acceptance/` (MR-3).

- (i) **A new ticket** (recommended): role independent-test-designer, paths `tests/acceptance/W2-49/**`.
  - Each red case of §4 row 18 is revised with a `Rewrite-Reason:` naming the approving entry. No expectation is
    lowered beyond the owner's change: every 4.2 lite check is kept.
  - Under V (i): `require_v42` reads "4.2 or later". `:69` and `:77` require the 4.2 entry to be kept and the version to
    be 4.2 or later. K (1) requires every capability record to cite the version in force.
  - The covers counts become W1 149 / W2 19 / W3 39 / NONE 7 (214).
  - The two "exactly" tests name CAP-45.a, and CAP-45 under A (i), as moved by the approving entry.
  - The D (ii) tests become: CAP-45.a is W3 by the approving entry, and its authenticated source names the signed tag
    and the manifest and file hashes.
  - The source-map test names rows 107, 224 and 286 as moved by the approving entry (A (i)).
  - The validator edge case uses another item that stays in Wave 2 (for example CAP-61.f).
  - The tests are written against the approved text before the apply. They stay red until the apply ticket's change
    and merge in the same batch (Question R), with a scoped run of `tests/acceptance/W2-49/` on the merged commit.
- (ii) **Name the reds in the nightly** until P1-11 revises the suite. Each nightly red starts an investigation
  (DEC-953 item 3), so this costs more than (i).
- *Recommendation:* (i). *Confidence:* high.

**N. DEC-841's nine items** (§9 F-1). These are CAP-04.a, CAP-04.d, CAP-22.b, CAP-22.c, CAP-30.c, CAP-30.g, CAP-32.d,
CAP-37.e and CAP-53.b. They are still W2 in the Contract, and exit criterion 7 counts them as moved. W2-109's KPI called
their change "v4.3", so if this note takes 4.3, P1-11's version becomes 4.4. W2-109 is closed, so nothing breaks.

- (a) **Leave them to P1-11** (its K-2), and accept the timing risk. If P1-11 lands after W2-47 starts, the audit finds
  them as drift.
- (b) **As (a), with a fallback** (recommended): if P1-11 is not applied when W2-46 starts, W2-46's record names the
  nine as exceptions for the owner to accept at the exit. Cost: one line in W2-46's record, and one owner act at the
  exit if P1-11 is late.
- (c) **Carry the seven mechanical ones in this change** (all but CAP-53.b, whose split with W2-66 follows DEC-880,
  and CAP-22.b, carried lite in W2-33, `DAEO-lrre`).
  - Cost: seven more wave lines in each Contract file, seven records, three more source-map checks, and the same W2-49
    revision widened (≈ +2 h).
  - It needs owner scope beyond DEC-1090 (5). CAP-22.c's place also depends on the roles spec (`DAEO-lrre`: "Wave 3
    rows unless the roles spec places them").
  - It splits P1-11's single re-baseline (DEC-105 (c), K-1) in two.
- *Recommendation:* (b). It keeps this note to the owner's scope and P1-11 whole, and the exit still has an answer if
  P1-11 is late. *Confidence:* medium.

## 8. How the exit audit (W2-47) checks it

W2-47 gives a finding row to every Wave 2 covers item. For this change, the auditor checks, read-only:

1. `contract.yaml` and `CONTRACT_v4.md` both have:
   - CAP-45.a at W3 (and CAP-45 at W3 under A (i));
   - the item text of §5.1;
   - the version of Question V;
   - a change-log entry and row citing the approving entry and this note.

   The two forms agree (W2-49's agreement test, revised, green).
2. `CAP-45.a.md` and `CAP-45.md` match `contract.yaml` (W2-49's record tests, revised, green). Every **capability**
   record cites the version in force. The master-rule records are not part of this check (§4 row 6).
3. `docs/changes/W2-27-CIT-E.md` names the apply commit, and says the apply matches this note or lists each difference.
4. `python3 docs/plan/tools/validate_w2.py`:
   - `contract-items-delivered` and `contract-items-cited-by-tests` list 19 Wave 2 items, CAP-45.a not among them;
   - `cit-p-lines-applied` lists no line of this note.

   The validator is advisory until P1-11 re-runs it (§9 F-2), so the auditor reads its lines, not its exit.
5. Exit criterion 7 and W2-17:
   - WBS §5 item 7 is marked met for CAP-45.a, with the approving entry and the apply commit;
   - its clause on the nine follows Question N;
   - W2-17's ticket and card say the move is done;
   - W2-17 is open in Wave 3 and still `closes` CAP-45.a.
6. CAP-45.a's finding row reads "moved to Wave 3 by the approving entry (W2-27-CIT-P, W2-27-CIT-E, the apply commit)".
   It is not a Wave 2 finding. W2-46's record names `gov update` as a Wave 3 line of AR-10, by deduction through AR-10
   (§4 row 13).
7. The apply ticket and the test-revision ticket are both closed, by one green queue run on the merged commit.
8. DEC-841's nine are handled as the owner answers Question N.

If the owner chooses to defer instead, W2-47 checks that W2-46's record holds the named exception and the owner's
acceptance.

## 9. Findings made while listing the impact

- **F-1. DEC-841's nine items are still Wave 2 in the Contract.**
  - DEC-841 moved CAP-04.a, CAP-04.d, CAP-22.b, CAP-22.c, CAP-30.c, CAP-30.g, CAP-32.d, CAP-37.e and CAP-53.b to Wave 3
    "through W2-49's CIT-P". That CIT-P's approval (DEC-741) came first.
  - W2-109 (`DAEO-6b2q`) was filed to carry them as Contract v4.3. DEC-1083 retired it into P1-11's re-baseline (K-2),
    and it built nothing.
  - So `contract.yaml` holds 20 Wave 2 items, while exit criterion 7 names eight plus the lite items, and its clause
    "the other nine moved to Wave 3 through W2-49's CIT-P" is false (§4 row 9).
  - **Put to the owner as Question N.**
- **F-2. Exit criterion 7's own two-way check is advisory.** P1-PLAN K-3 keeps `validate_w2.py` advisory until it is
  re-run after K-1. §8 step 4 reads its lines and does not depend on its exit.
- **F-3. The validator reads a CIT-P's ```` ```yaml ```` wave lines as soon as the file exists.** `cit-p-lines-applied`
  reads every `*-CIT-P.md`, approved or not. So a proposal written in W2-49's form turns that check red from its first
  commit until its apply. This note uses ```` ```diff ```` blocks for that reason (§4 row 19). A later CIT-P that moves
  an item out of Wave 2 should do the same, or the validator should read only approved notes. The second is a matter for
  P1-11 or a Wave 3 row, not for this note.

## 10. How it is reversed

The apply ticket's merge and the test revision are reverted together, by a new commit; nothing on `w2/integrate` is
amended. The revert restores:
- Contract 4.2, with CAP-45.a and CAP-45 at W2;
- the records citing 4.2;
- W2-49's suite as it was.

The 4.3 text stays in git as a kept version (CAP-33.e). Git cannot revert the owner's approving entry: a new owner entry
withdraws it. The orchestrator restores the WBS lines, W2-47's card and the open tickets' marked lines (W2-17, W2-27,
W2-47) in a new commit. With CAP-45.a back in Wave 2, exit criterion 7 is open for it again.

## 11. The route from here (CAP-33)

1. **One independent review** by a fresh, read-only auditor (CAP-33.d; K7-W2-REMAINDER §3). Done at `4bebfe6bb`:
   READY, with F1 to F12. This revision is the one answer round (§12).
2. **The owner's approval** under DEC-105 (apply now). It answers V, A, C, R, T and N, and approves the two new tickets
   before they are filed (DEC-974 item 2). It is recorded as an owner entry.
3. **The CTO files the two tickets.** The test-revision ticket's designer writes against the approved text, before the
   apply.
4. **The apply ticket** (product-spec) applies §5, regenerates the records and writes `docs/changes/W2-27-CIT-E.md`.
5. **Both tickets merge and close in one merge-queue batch,** on one green run over the combined candidate (DEC-988
   item 3, DEC-989 item 2), outside an experiment window (§4 row 27). The run includes a scoped run of
   `tests/acceptance/W2-49/`.
6. **The orchestrator's edits** follow (§4 rows 9, 10, 12, 14, 16, 24). W2-27's KPI line for exit criterion 7 is met.

## 12. Review and answers

**The review.** A fresh, read-only independent auditor reviewed this note at `4bebfe6bb`. Its record is
`.gov-runtime/scratch/orchestrator/reviews/w2-27-citp.md`. It found the note READY (C1 to C6 pass), with twelve
findings, all in scope, ordinary work, consequence "other", none blocking. This revision is the one answer round, with
the CTO's settlements for F1 to F4.

| Finding | How it was answered | Where |
|---|---|---|
| F1: three W2-49 red cases missing; two cost lines low | **Changed.** `test_w2_49_owner_answers.py:143`, `test_w2_49_source_map.py:115` and `test_w2_49_contract.py:77` added to the red list. The list restated as the helper plus ten functions (V (i), A (i)), seven (V (ii), A (i)) or five (V (ii), A (ii)). The V (ii) and A (i) costs corrected, and T (i)'s recipe given in full | §4 row 18; §7 V, A, T; §6 |
| F2: the apply's route to `w2/integrate` under one merge per ticket | **Changed** (CTO's settlement): a separate apply ticket (product-spec, the Contract files and `W2-27-CIT-E.md`), merged in one batch with the test-revision ticket under DEC-988 item 3 and DEC-989 item 2. Both are proposed to the owner with the note (DEC-974). W2-27's path widening for the Contract is removed | §3 item 6; §4 rows 1–7, 14; §7 R; §11 |
| F3: the recommended set goes beyond option A, unstated | **Changed.** §3.1 lists each part beyond option A's description, with the smallest honest set and its cost. V and A are marked "beyond option A's description" | §3.1; §6; §7 |
| F4: F-1 not an owner question; WBS §5 item 7's false clause | **Changed.** Question N added, with options, costs and a recommendation. §4 row 9 corrects the clause "the other nine moved to Wave 3 through W2-49's CIT-P" | §7 N; §4 row 9; §9 F-1; §8 step 8 |
| F5: W2-47's WBS card missing | **Changed.** The card (line 1455) changes with the ticket under V (i). §5 item 11 (line 1871) stays true | §4 row 16; §10 |
| F6: row 12 said W2-46's ticket names `gov update` | **Changed.** It now says the line is deduced through AR-10, and that W2-24's `gov update` KPI was not moved to W2-46 | §4 row 13; §8 step 6 |
| F7: "every record" includes the six master-rule records at 4.1 | **Changed.** "Every capability record" throughout. The MR records are named unchanged | §3 item 5; §4 rows 5, 6; §5.3; §8 step 2 |
| F8: mentions not in the impact set | **Changed.** The CAP-45 mentions and the tickets citing v4.2 added, each with no change | §4 rows 7, 14, 17, 22 |
| F9: the store and the measure | **Changed.** The 279 rewritten files, the shifted line numbers, the store's rebuild, the measure's re-anchoring at the next re-pin (DEC-1084), and the merge placed outside an experiment window | §4 row 27; §11 step 5 |
| F10: §2's excerpt left out eight lines | **Changed.** Lines 2738–2745 marked with `…`, and the omission stated | §2 |
| F11: two patch parts described rather than given | **Changed.** The change-table row and the removed record lines given in full. The 274 version lines given as an exact one-occurrence rule. `DEC-OWNER` dropped from the `decisions` list, following 4.2's precedent | §5.2; §5.3 |
| F12: corroboration missing from the CAP-33.d route | **Changed.** The route stated in full, with what corroborates the change | Introduction |

**The owner's questions after this round:** V (the version), A (CAP-45 itself), C (the Wave 2 clause), R (the apply
ticket), T (the test-revision ticket) and N (DEC-841's nine).

## 13. The owner's answers (DEC-1093)

The owner approved this CIT-P on 2026-11-07 (DEC-1093 (1)), apply now, with this CIT-P's recommended answer to each
question. Sections 1 to 12 are the reviewed text, kept as approved at `33f72aab2`. What was applied, and each
difference from it, is in `docs/changes/W2-27-CIT-E.md`.

- **V (i):** version 4.3.
- **A (i):** CAP-45 moves to Wave 3 with CAP-45.a.
- **C (i):** the "in Wave 2" clause is withdrawn; the manifest and file hashes stay part of the authenticated source,
  beside the signed tag.
- **R (a):** a separate apply ticket: **W2-139 (`DAEO-ongl`)**, product-spec. It is the ticket §3, §4, §7 R and §11
  call "the apply ticket".
- **T (i):** a new test-revision ticket by an independent test designer: **W2-140 (`DAEO-5ce2`)**. It is the ticket
  §4 row 18, §7 T and §11 call "the test-revision ticket".
- **N (b):** DEC-841's nine items are left to P1-11; if P1-11 is not applied when W2-46 starts, W2-46's record names
  them as exceptions for the owner.

W2-139 and W2-140 merge and close in one merge-queue batch, on one green run, outside an experiment window.
