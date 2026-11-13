---
id: W2-27-CIT-E
type: change-execution-record
status: APPLIED
date: 2026-11-09
branch: w2/W2-139
base: 2d9115ce5 (Contract 4.2; docs/contract/ is unchanged from the note's base 95eec049 to this base)
ticket: DAEO-ongl (W2-139, the apply ticket of the note's Question R)
proposal: W2-27-CIT-P
approved_revision: 33f72aab2 (the CIT-P as answered after its review; its sections 1 to 12 are unchanged from there to this record)
author: product-spec (W2-139, single author)
review: the CIT-P was reviewed at 4bebfe6bb by a fresh, read-only independent auditor (CAP-33.d), READY with F1 to F12, answered once at 33f72aab2 (CIT-P §12); its record governance/project/orchestration/reviews/w2-27-citp.md
decisions_carried: [DEC-1089, DEC-1090]
decisions_approving: [DEC-1093]
state_class: EVIDENCE
---

# W2-27 — Change-execution record (CIT-E) for Contract v4.3

This records what the apply of W2-27's specification change did, against its proposal `docs/changes/W2-27-CIT-P.md`
(W2-27-CIT-P), as the owner approved it in DEC-1093 (1). The change carries DEC-1089 (2) and DEC-1090 (5) into the
Contract: `gov update` is built in Wave 3, so CAP-45.a moves from Wave 2 to Wave 3, and CAP-45 with it; the Wave 2
clause of version 4.2 is withdrawn, and the manifest and file hashes stay part of CAP-45.a's authenticated source,
beside the signed tag.

CAP-33's acceptance asks that "the CIT-E record matches the proposal or lists the differences". §3 confirms each part
of the CIT-P's §5 against the diff, section by section; §5 lists each difference from the note with its reason.

## 1. Summary

| Item | Before (base, Contract 4.2) | After (Contract 4.3) |
|---|---|---|
| Contract version | 4.2, revised 2026-10-17 | 4.3, revised 2026-11-09; change-log entry and change row 4.3; 4.0, 4.1 and 4.2 unchanged |
| Capabilities | 62: W1 42 / W2 7 / W3 11 / NONE 2 | 62: W1 42 / W2 6 / W3 12 / NONE 2 (CAP-45 to W3) |
| Covers items | 214: W1 149 / W2 20 / W3 38 / NONE 7 | 214: W1 149 / W2 19 / W3 39 / NONE 7 (CAP-45.a to W3) |
| CAP-45.a's text | "authenticated source (the signed tag in W3, CAP-02.c) … ; in Wave 2 the authenticated source is the release's manifest and file hashes (CAP-43.b, lite); the signed tag goes with CAP-02.c (W3), DEC-722" | "authenticated source (the signed tag, CAP-02.c, and the release's manifest and file hashes, CAP-43.b) …"; source gains DEC-1090 |
| Capability records (`docs/contract/capabilities/`) | 276, each "(Contract v4, version 4.2)" once | 276, each "(Contract v4, version 4.3)" once; CAP-45.a.md and CAP-45.md as §5.3 |
| `docs/contract/SOURCE_MAP.csv` | rows 107, 224, 286 "wave W2" | the same three rows "wave W3"; row 222 and every other row unchanged |
| Master-rule records (`docs/contract/master-rules/`) | "(Contract v4, version 4.1)" | not touched (CIT-P §4 row 6) |

The apply touched specification files only: the two Contract files, the 276 capability records, the source map, the
CIT-P and this record. No code, no test, no ticket, no plan file, no register entry.

## 2. The owner's approval before the change (CAP-33)

| Step of CAP-33.d | Where |
|---|---|
| Evidence | DEC-953 item 10, DEC-954, DEC-941 item 3 (CIT-P §1, triggers T1 to T6) |
| Corroboration | DEC-1089 (2), DEC-1090 (5); no `gov update` code at the base (CIT-P §2) |
| Proposal | W2-27-CIT-P on `w2/W2-27-citp` |
| Independent review | a fresh, read-only independent auditor at `4bebfe6bb`, READY with F1 to F12; answered once at `33f72aab2` (CIT-P §12) |
| **Owner approval** | **DEC-1093 (1), the owner's, 2026-11-07, in the register (`docs/DECISION_REGISTER.md`, `### DEC-1093`): the note approved, apply now, with V (i), A (i), C (i), R (a) (this ticket, W2-139, `DAEO-ongl`), T (i) (W2-140, `DAEO-5ce2`) and N (b)** |
| Versioned promotion | `22860a07e` (§3); Contract 4.2 stays in git and in the change log as a kept version (CAP-33.e; DEC-105) |
| The CIT-E | this record, with this commit |

No Contract file was edited before the approval: DEC-1093 is in the base's register, and the first commit on this
branch that changes `docs/contract/` is `22860a07e`.

## 3. What changed: `22860a07e`, the note's §5 against the diff

`22860a07e` (2026-11-09; `Task: DAEO-ongl`, `Implements: DEC-1093`, `Role: product-spec`) changes 279 Contract files
(the two Contract files, the 276 capability records, the source map) and adds the approved CIT-P. In the patch,
`DEC-OWNER` is DEC-1093 and `APPLY_DATE` is 2026-11-09, the commit's date.

### 3.1 §5.1 `docs/contract/contract.yaml`

| CIT-P §5.1 part | Proposed | Applied | Match |
|---|---|---|---|
| header | `version: '4.3'`; `date: '2026-09-30'` kept; `revised: 'APPLY_DATE'` | `version: '4.3'`; `date` kept; `revised: '2026-11-09'` | matches |
| change log | a 4.3 entry after the 4.2 entry, with §5.1's text; 4.0, 4.1 and 4.2 unchanged | the entry, word for word and line for line, `DEC-OWNER` → DEC-1093, `APPLY_DATE` → 2026-11-09; the three earlier entries unchanged | matches |
| CAP-45 `wave`, `wave_note` | `W3`; "gov update and the first real `copier update` are W3 (DEC-1089, DEC-1090); the pending-update report of `gov doctor` is W3 (DEC-165)" | as proposed, with the same line break | matches |
| CAP-45 `provider` | `'W3: gov update --check'`; the other two entries kept | as proposed | matches |
| CAP-45 `sources` | `- DEC-1090` appended after DEC-165 | as proposed | matches |
| CAP-45.a `item` | the C (i) wording, three lines, `''` quoting | as proposed, the same three lines | matches |
| CAP-45.a `source` | "…; DEC-722; DEC-1090" | as proposed | matches |
| CAP-45.a `wave` | `W3` | `W3` | matches |
| anything else | nothing | nothing else in the file changed (the diff has the four hunks above only) | matches |

The file loads with `yaml.safe_load` after the edit: version `'4.3'`, revised `'2026-11-09'`, change-log versions
4.0, 4.1, 4.2, 4.3.

### 3.2 §5.2 `docs/contract/CONTRACT_v4.md`

| CIT-P §5.2 part | Proposed | Applied | Match |
|---|---|---|---|
| frontmatter | `version: "4.3"`; `revised: APPLY_DATE`; `decisions` gains DEC-1089 and DEC-1090 only (not the approving entry, 4.2's precedent) | `version: "4.3"`; `revised: 2026-11-09`; `[… , DEC-174, DEC-722, DEC-1089, DEC-1090]` | matches |
| title | "(version 4.3)" | as proposed | matches |
| version line | "**Version 4.3** (APPLY_DATE)." | "**Version 4.3** (2026-11-09)." | matches |
| change table | a `\| 4.3 \|` row after the 4.2 row, the 4.3 change-log text on one line with `''` written `'` | as proposed; the 4.0, 4.1 and 4.2 rows unchanged | matches |
| §1 Counts | W2 7 → 6; W3 11 → 12 | `\| W2 \| 6 \| 0 \| 0 \| 6 \|`, `\| W3 \| 12 \| 0 \| 0 \| 12 \|`; the W1, NONE and All rows unchanged | matches |
| CAP-45 block | the Wave, Provider and Sources lines and the CAP-45.a covers line of §5.2 | as proposed, word for word | matches |
| anything else | nothing | nothing else in the file changed | matches |

### 3.3 §5.3 the derived records

| CIT-P §5.3 part | Proposed | Applied | Match |
|---|---|---|---|
| `CAP-45.a.md` | title, heading, version line, `Item:` and `Wave: W3` as §5.3's diff; every other line unchanged | as proposed; the title, heading and `Item:` equal `contract.yaml`'s CAP-45.a item (checked) | matches; method: difference (a) |
| `CAP-45.md` | version line 4.3; `Wave: W3`; every other line unchanged | as proposed | matches |
| the other 274 records | the one occurrence of `(Contract v4, version 4.2)` becomes `(Contract v4, version 4.3)`, nothing else | counted first: all 276 records held it exactly once; replaced by a throwaway script (not committed) that required exactly one occurrence per record; after: 0 occurrences of 4.2, all 276 hold 4.3 exactly once; `git diff --numstat` shows one line removed and one added in each of the 274 | matches |
| master-rule records | not touched | not touched (outside this ticket's paths) | matches |

Every capability record's wave agrees with `contract.yaml` after the edit (276 of 276, checked).

### 3.4 §5.4 `docs/contract/SOURCE_MAP.csv`

| CIT-P §5.4 part | Proposed | Applied | Match |
|---|---|---|---|
| row 107 (Contract v3, S5) | "wave W2" → "wave W3" | as proposed | matches |
| row 224 (Framework v4.1.2, 82) | "wave W2" → "wave W3" | as proposed | matches |
| row 286 (Distribution Protocol v1.2, 12) | "wave W2" → "wave W3" | as proposed | matches |
| row 222 and every other row | unchanged | unchanged (the diff has the three rows only) | matches |

### 3.5 §5.5 the version it makes

Contract v4, version 4.3; the file names and the id `CONTRACT-v4` unchanged. Counted from `contract.yaml` after the
edit: capabilities W1 42 / W2 6 / W3 12 / NONE 2 (62); covers items W1 149 / W2 19 / W3 39 / NONE 7 (214), as §5.5
states. The two Contract forms agree on the wave of every capability and every covers item (276 of 276, checked).

### 3.6 This commit: the CIT-E

- `docs/changes/W2-27-CIT-E.md` (new): this record.

The CIT-P as approved went in with the Contract edit, `22860a07e`, so that the 4.3 change-log entry's reference to it
resolves at the commit that makes 4.3: `docs/changes/W2-27-CIT-P.md` is the note at `33f72aab2` with its frontmatter
`status:` ACCEPTED, an `accepted:` line (the owner, 2026-11-07, DEC-1093 (1), apply now) and a closing section, "13. The
owner's answers (DEC-1093)", which records V (i), A (i), C (i), R (a) with W2-139 (`DAEO-ongl`), T (i) with W2-140
(`DAEO-5ce2`), and N (b). Nothing else in its body changed; every patch block stays a `diff` block, and it holds no
`yaml` block (CIT-P §4 row 19, §9 F-3).

## 4. The owner's answers (DEC-1093 (1)) and how each was applied

| Q | Answer | How it was applied |
|---|---|---|
| V | **(i)** version 4.3 | `22860a07e`: both Contract files at 4.3 with the 4.3 entry and row; the 276 capability records cite 4.3 |
| A | **(i)** CAP-45 moves to Wave 3 with CAP-45.a | `22860a07e`: CAP-45's wave, wave note, provider and sources; §1 Counts; `CAP-45.md`; SOURCE_MAP rows 107, 224, 286 |
| C | **(i)** the "in Wave 2" clause withdrawn; the manifest and file hashes kept beside the signed tag | `22860a07e`: CAP-45.a's item in both Contract files and its record, §5.1's wording exactly |
| R | **(a)** a separate apply ticket: W2-139 (`DAEO-ongl`) | this ticket; it merges and closes in one batch with W2-140 (§6) |
| T | **(i)** a test-revision ticket by an independent test designer: W2-140 (`DAEO-5ce2`) | not in this ticket's paths; its revised cases were merged into this branch before the apply (`2d9115ce5`) and judge it (§6) |
| N | **(b)** DEC-841's nine items left to P1-11, named as exceptions in W2-46's record if P1-11 is not applied by then | nothing in this apply: the nine stay W2 in 4.3 (they are among the 19 Wave 2 items) |

**It supersedes W2-49-CIT-P §7 D (ii)'s clause** (CIT-P §4 row 8). The Wave 2 clause that D (ii) added to CAP-45.a
in Contract 4.2 ("in Wave 2 the authenticated source is the release's manifest and file hashes (CAP-43.b, lite); the
signed tag goes with CAP-02.c (W3)") is withdrawn by this change. `docs/changes/W2-49-CIT-P.md` and
`docs/changes/W2-49-CIT-E.md` are approved records and stay as they are; this record is where the supersession is
stated.

## 5. Differences from the CIT-P

Every part of §5 is applied as written (§3); the Contract text has no difference from the note. One difference in
method:

| # | Difference | Reason |
|---|---|---|
| (a) | CAP-45.a's record was not regenerated by a throwaway generator that first reproduced the unchanged records byte for byte (CIT-P §4 row 3's method); §5.3's diff was applied to it line by line. | §5.3 gives the record's every changed line in full, and every other line is unchanged; applying it exactly gives the same file a generator would. The result was checked against `contract.yaml`: the record's title, heading and `Item:` equal CAP-45.a's item, and its wave is W3 (§3.3). The brief for this ticket names §5.3's records "as given" |

## 6. Against the KPI lines and the acceptance tests

| KPI line | State |
|---|---|
| S1 The note as approved, applied exactly | `22860a07e` (§3); the diff holds §5's lines and nothing else (failure line A: no Contract change the note does not name) |
| S2 This record lists each difference with its reason, or states there is none | §5 |
| S3 One merge-queue batch with W2-140, on one green run of `tests/acceptance/W2-49/` and the plan validator over the combined candidate, outside an experiment window | **the CTO's**, at the merge; not this ticket's to do |

**W2-140's suite, before the commit, on the working tree equal to `22860a07e`:** `gov accept W2-140 --root
<this worktree>` with `GOV_TESTS_OPTIN=breadth,lifted` (the three named cases opted in), through the heavy-job gate:
outcome pass; success-1 14 passed, success-2 15 passed, success-3 160 passed; unmapped 0; totals 160 passed, 0 failed,
0 skipped. This worker never read `tests/acceptance/W2-49/` (DEC-820 (c), DEC-1056); only the run's result was read.

**The plan validator** (`python3 docs/plan/tools/validate_w2.py`, advisory until P1-11 re-runs it, CIT-P §9 F-2), after
the edit:
- its Wave 2 set is 19 items, CAP-45.a not among them: CAP-04.a, CAP-04.d, CAP-10.b, CAP-17.b, CAP-19.a, CAP-19.c,
  CAP-22.b, CAP-22.c, CAP-30.c, CAP-30.g, CAP-32.d, CAP-33.b, CAP-33.g, CAP-37.e, CAP-43.b, CAP-44.f, CAP-44.h, CAP-53.b,
  CAP-61.f;
- `contract-items-delivered`: FAIL, "no Wave 2 ticket delivers: CAP-22.c, CAP-44.f";
- `contract-items-cited-by-tests`: FAIL, "no acceptance test cites: CAP-04.a, CAP-04.d, CAP-22.b, CAP-22.c, CAP-30.g,
  CAP-32.d, CAP-33.b, CAP-33.g, CAP-37.e, CAP-53.b";
- `cit-p-moved-items`: PASS, "3 items moved to Wave 2, each with a CIT-P line";
- `cit-p-lines-applied`: PASS, "6 CIT-P lines, each applied in the Contract", none of them W2-27's (its note holds no
  `yaml` block);
- the other lines (`wave2-tickets`, `ticket-contract-ids-exist`, `triage-counts` FAIL; `list-counts` PASS; five NOT
  RUN) read the tickets, the WBS, the list and the triage, not the Contract's waves;
- `RESULT: 5 FAIL, 5 NOT RUN`, exit 1. None of the listed items is CAP-45 or CAP-45.a.

## 7. What stays open

- **S3, the batch merge:** the CTO merges this ticket and W2-140 in one merge-queue batch, on one green run of
  `tests/acceptance/W2-49/` and the plan validator over the combined candidate, outside an experiment window (DEC-988
  (3), DEC-989 (2), DEC-1093 (1); CIT-P §4 row 27: the apply rewrites 279 Contract files and moves `contract.yaml`'s and
  `CONTRACT_v4.md`'s later line numbers).
- **The orchestrator's edits after the approval** (CIT-P §4 rows 9, 10, 12, 14, 16, 24: WBS §5 item 7 and W2-17's card,
  W2-17's, W2-27's and W2-47's tickets, W2-47's card, the register's in-force list): not this ticket's.
- **N (b):** DEC-841's nine items stay Wave 2 in 4.3 until P1-11.

## 8. How it is reversed

As CIT-P §10 states: this ticket's merge and W2-140's are reverted together, by a new commit; nothing on `w2/integrate`
is amended. Reverting `22860a07e` restores Contract 4.2 in both files, CAP-45 and CAP-45.a at W2 with 4.2's CAP-45.a
text, the 276 records citing 4.2, the three source-map rows at W2, and removes the approved CIT-P from this branch;
reverting this commit removes this record. The 4.3 text stays in git as a kept version (CAP-33.e). DEC-1093 is withdrawn
only by a new owner entry.
