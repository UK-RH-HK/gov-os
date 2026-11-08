# W2-130 (DAEO-q8cl): independent audit of the marks batches a1, a2 and the `sources:` patch b1

Independent auditor, 2026-11-08, for the Wave 2 CTO (DEC-1073 (5)(a), DEC-1097 (9), W2-130 KPI 3). This is a fresh
session that wrote none of the drafts. I worked read-only on the repository and applied nothing to the main tree. I
opened nothing under `~/gov-os-eval/`, made no commit in the repository, and used no GPU and no install. I followed
JUDGEMENT.md and AUDITOR-common.md.

**Verdict: READY to commit a1, a2 and b1 once 12 wrong marks are dropped and 2 mark texts are rewritten (F1 to F5).**
As drafted, a1 and a2 would commit 12 marks the register's text does not support. That breaks KPI 3 ("a wrong mark is
corrected or dropped, never committed"). b1 is ready as drafted.

## What I checked and how

- **Head:** `w2/integrate` at `2f9c80b1f807`. The drafts were built at `3552f0f59bb7`, and the one commit since then
  adds only `packages/W2-130-SITTING.md`.
  - I rebuilt the patches at today's head with a copy run of `build_patches.py`, its output sent to my scratch folder.
    a1, a2 and b1 come out byte-identical to the drafts.
  - The main tree's `git status` was the same before and after: the CTO's own 4 package files, no register or ticket
    change.
- **The clone:** a throwaway `git clone --shared` in my scratch folder (`scratchpad/w2-130-audit/clone`).
  - `git apply --check` passes for a1, a2 and b1 at today's head. Each was then applied and committed in order.
  - The pinned `gov links --root <clone> --all --json` was run before and after each stage.
- **Every mark:** all 151 pairs (a1 100, a2 51) were reconciled one to one with `marks-audit.md`. Nothing is in the patch
  that is not in the worksheet, and nothing the other way.
  - **The 19 marks derived from free text** (a1 4, a2 15): each read by hand against both entries, the change log and
    ARCHIVE-SUPERSEDED §A.
  - **The 132 labelled marks:** every one, not a sample, checked by script for the changer's own label (`Amends`,
    `Changes`, `Replaces`, `Narrows`, `Restores`, `Amended`, or "(amended here)") naming the marked entry. All 132 are
    present. I read each label value, with a second script pass for target ids inside parentheses or after "by". The
    worksheet's 20 drawn labelled marks are among them.
- **b1:** all 394 added (id, ticket) pairs were reconciled with the UNLINKED_ID findings they clear. I read a seeded
  sample of 52 against its source:
  - the KPI bracket, for 308 pairs;
  - the worker commit's `Implements:` under the ticket's `Task:`, for 65 pairs;
  - both, for 21 pairs.
- **Retrieval:** I used no `gov retrieve`. The audit is about the register's literal text, so I read the entries
  directly. The guard refused nothing (0 refusals).

### The guards (all hold)

| Check | Result |
|---|---|
| Register, a1 | 82 lines changed. Each is the old line plus an appended ` · **Changed by:** …` on the entry's `**Status:**` line. Line count unchanged. All 82 entries are ACCEPTED. |
| Register, a2 | 40 lines changed, the same form. 35 of them already held a `**Changed by:**` label (see F7). |
| Changers | All 151 are ACCEPTED. None is older than the entry it marks. |
| Substance | No decision text, title or other field touched (DEC-866). |
| Tickets (b1) | 50 files. Only `sources:` changed, with ids appended after the existing ones. Body and every other key byte-identical. No duplicates. |
| Closed tickets | Untouched: 28 open, 22 in progress, 0 closed (DEC-1088 (6)). CLOSED_TICKET_EDITED stays 117. |
| Other findings | No new finding of any code. UNKNOWN_ID moves by line number only (556 → 556). |

### `gov links --all` counts at today's head (my clone)

| Code | before | a1 | a2 | b1 | a1/a2 corrected (F1–F5), then b1 |
|---|---|---|---|---|---|
| UNMARKED_CHANGE | 185 | 85 | 34 | 34 | 86 → 46 → 46 |
| UNLINKED_ID | 1877 | 1877 | 1877 | 1097 | 1097 |
| NOT_IN_FORCE_AS_RULE | 141 | 141 | 141 | 143 | 143 |
| STATUS_CONFLICT / ENFORCES_SUPERSEDED / CLOSED_TICKET_EDITED / TICKET_CHANGE_UNMARKED / UNKNOWN_ID | 116 / 44 / 117 / 93 / 556 | same | same | same | same |
| **total** | 3129 | 3029 | 2978 | 2200 | 3030 → 2990 → 2212 |

- **As drafted:** these are exactly check-report.md's figures, so its claims hold at today's head.
- **With the corrections:** check.py's expectations become 86 (after a1) and 46 (after a2). After a3 the expected
  residual becomes 17, not 5, unless the archive line is rewritten (F4).
- **The archive rewrite:** I tested it in the clone, with the line rewritten one decision per line. It clears 9 of the
  12 and leaves 37 after a2.
- **check.py's head guard:** it fails at today's head only because build-summary.json still records `3552f0f59bb7`.
  Following the README (rebuild, then check) clears it. I did not write into the drafts folder.

## Findings

Each finding carries the two lines DEC-808 asks for.

**F1: a1, DEC-1050 ← DEC-1057 is wrong.**
- **The text:** DEC-1057's `**Changes:**` ends "DEC-991's `rm` ask (corrected by DEC-1050 (8))". DEC-1050 (8) is the
  decision that corrected DEC-991, and DEC-1057 lists it under its `**Under:**`. DEC-1057 rests on DEC-1050; it does
  not change it.
- **Drop:** the a1 hunk at register line 13005, ` · **Changed by:** DEC-1057 (8)`.
- **Kept:** DEC-991 ← DEC-1050 and DEC-991 ← DEC-1057 are label-supported.
- **Scope:** in.
- `Ordinary work: yes, because an agent asking about deletions gets DEC-1050 marked as partly changed.`
- `Consequence: other (an extra changer; nothing current hidden, nothing superseded shown current).`

**F2: a2, DEC-120 ← DEC-173 is wrong.**
- **The text:** the only text is the change-log row 0.30 inside DEC-173's span: "DEC-172 (DP-3: …; withdraws the
  settings second line of DEC-120 and DEC-151), DEC-173 (DP-4: …)". The withdrawal is DEC-172's clause.
- **DEC-173's own entry:** it amends only Charter §6's install sentence (the research exception).
- **Already marked:** DEC-120's status line already names DEC-172.
- **Drop:** the hunk at line 1100.
- **Scope:** in.
- `Ordinary work: yes, because install questions reach DEC-120.`
- `Consequence: other.`

**F3: a2, DEC-724 ← DEC-860 is wrong.**
- **The text:** change-log §252 says "The owner committed DEC-859 and DEC-860 (…) and set a standing rule that replaces
  DEC-724's …". The rule is DEC-861, whose `**Changes:**` names DEC-724.
- **Already marked:** DEC-724's status line already says "replaced by DEC-861".
- **DEC-860 itself:** it is the retrieval-batching rule.
- **Drop:** the hunk at line 7703.
- **Scope:** in.
- `Ordinary work: yes.`
- `Consequence: other.`

**F4: a2, the ARCHIVE §A line 34 cross product: 9 of its 12 marks are unsupported.**
- **The line:** "DEC-454, DEC-455, DEC-480, DEC-490, DEC-492: changed by DEC-868, DEC-899, DEC-904 and DEC-908" is the
  CTO's group summary. None of DEC-868, DEC-899, DEC-904 or DEC-908 names DEC-454, DEC-455 or DEC-480. DEC-868 and
  DEC-899 name none of the five.
- **What the register attributes:** it is already on the five status lines, and comes from DEC-908 item 2, DEC-904
  item 6 and the W2-07 run-1 marks.
- **Unsupported, drop (9):**
  - DEC-454 ← DEC-904
  - DEC-455 ← DEC-904
  - DEC-480 ← DEC-899
  - DEC-480 ← DEC-904
  - DEC-490 ← DEC-868
  - DEC-490 ← DEC-899
  - DEC-490 ← DEC-908
  - DEC-492 ← DEC-904. DEC-904 item 6 lists DEC-492 only as an expectation "marked `17e5c3a9`" by others; DEC-492 is
    not in DEC-904's `**Changes:**`.
  - DEC-492 ← DEC-908. DEC-908 names DEC-454, DEC-455 and DEC-480 only.
- **Supported in substance, keep (3):**
  - DEC-454 ← DEC-868. DEC-868 items 1 (b) and 3 change DEC-454's "stale evidence only when governance files change"
    and "every failed close counts". This is the same reading DEC-480's mark already takes, and DEC-908 item 1 routes
    DEC-454's W1-30 cases to DEC-868.
  - DEC-454 ← DEC-899 and DEC-455 ← DEC-899, medium confidence. P-IS-4 (a), confirmed by DEC-899, says commit-gate
    refusals spend no attempt. That is the precedent of DEC-492's existing mark "DEC-899 (P-IS-4 (a))".
- **Lines:**
  - drop the hunks at 5258 (DEC-480), 5369 (DEC-490) and 5401 (DEC-492);
  - rewrite 4965 (DEC-454) as ` · **Changed by:** DEC-868 (items 1 (b) and 3), DEC-899 (P-IS-4 (a))`;
  - rewrite 4992 (DEC-455) as ` · **Changed by:** DEC-899 (P-IS-4 (a))`.
- **Then rewrite the archive line one decision per line,** as sitting item H2 already recommends and within W2-130's
  allowed paths:
  - DEC-454: DEC-868, DEC-899, DEC-908
  - DEC-455: DEC-868, DEC-899, DEC-908
  - DEC-480: DEC-868, DEC-908
  - DEC-490: DEC-904
  - DEC-492: DEC-868, DEC-899

  Tested in the clone: it clears the 9 residual findings.
- **Scope:** in.
- `Ordinary work: yes, because close-gate questions reach these five entries.`
- `Consequence: other.`

**F5: Right changer, wrong or broken part: rewrite the text.**
- **a1, DEC-1084 (line 13528):** the drafted text is `DEC-1087 (W2-33's layer lines moved to Wave 3, W3-P23: reversed
  by (13)`. It is truncated, its parentheses are unbalanced, and it reads as if DEC-1087 moved the lines to Wave 3.
  DEC-1087 (13) keeps them in Wave 2. Write ` · **Changed by:** DEC-1087 (13) (W2-33's layer lines back in Wave 2)`,
  as on DEC-1083's line.
- **a2, DEC-941 (line 11511):** the drafted text is `DEC-946 (item 6))`. DEC-946 changes "DEC-941's blocks A to E
  (their order)", and says DEC-941 item 6 *stays*. Write ` · **Changed by:** DEC-946 (blocks A to E: their order)`.
- **Should fix, imprecise but not false:**
  - DEC-988 `DEC-989 (items)` → `DEC-989 (item 3's baseline)`;
  - DEC-1032 `DEC-1033 (items)` → `DEC-1033 (items 2 and 3)`.
- **Parsing:** in the clone, all four rewrites parse with no new finding.
- **Scope:** in.
- `Ordinary work: yes.`
- `Consequence: other (a reader is pointed at the wrong part; DEC-941's says a kept item changed).`

**F6: A part written after the changer can name the wrong decision's item.** About 25 marks copy the changed entry's
own item after the changer's id. Examples:
- DEC-968 `DEC-1049 (1)`
- DEC-1028 `DEC-1057 (6)`
- DEC-1038 `DEC-1057 (1)`
- DEC-1066 `DEC-1067 (2)`
- DEC-1074 `DEC-1087 (7)`
- DEC-971 `DEC-1001 (item 5)`
- DEC-880 `DEC-904 (item 2)`

The register's own form reads the number as the changer's item, for example DEC-1083's "DEC-1097 (1)(d)" and
"DEC-1087 (13)". So a reader may open the wrong item. Optional: write "(on its item n)". The changers are right.
- **Scope:** in.
- `Ordinary work: yes.`
- `Consequence: other.`
- **Class:** row.

**F7: A second `· **Changed by:**` label on 35 a2 lines.** `register.py` `_entry`, the loader and `gov links` read
both labels, as verified.
- **Scope:** in.
- `Ordinary work: yes.`
- `Consequence: other (style).`
- **Class:** row; merge into one label in a later pass.

**F8: KPI 1's "(the part)" is missing on about 70 marks.** `--propose-marks` has a part only where the changer's label
gives one. The changer is named, so nothing reads as wholly current.
- **Scope:** in.
- `Ordinary work: yes.`
- `Consequence: other.`
- **Class:** row.

**F9: b1 adds two ids that are not in force, faithfully to the brackets: +2 NOT_IN_FORCE_AS_RULE.**
- **DAEO-2bdu ← DEC-016** (PROPOSED), from `[DEC-954 Q9c, CAP-20, DEC-016]`. Sitting row A/B proposes ACCEPTED, which
  clears it.
- **DAEO-swdu ← DEC-798** (SUPERSEDED), from `[DEC-975, DEC-798]`. This is the decision W2-15b re-tests, and DEC-1033
  is already in its sources.
- **Recommendation:** keep both; the finding is the honest signal (DEC-866 item 3 belongs to the ticket's KPI).
- **Scope:** in.
- `Ordinary work: yes.`
- `Consequence: other.`

**F10: b1 rests on provenance brackets.**
- **The form:** "[moved from W2-118 S1, DEC-1083]", "[moved to W2-124, DEC-1083]", "[re-worded, DEC-1084]",
  "[lifted (was S7), DEC-1083 …]".
- **The coordination ticket DAEO-sdxk:** it gains 18 DEC ids from worker commits filed under its Task, for example
  D-4's cut and the emergency patches.
- **Judgement:** both are faithful to `gov links`' rule, but some are weak as "rests on".
- **Scope:** out (the bracket grammar is `gov links`' own).
- `Ordinary work: yes.`
- `Consequence: other.`
- **Class:** row for `gov links`: exempt the "moved/re-worded" markers.

**F11: Range ids are marked at their ends only.** "DEC-285 to DEC-290" (DEC-1045) and "DEC-030…DEC-037" (DEC-080)
mark the two ends only. DEC-286 to DEC-289 and DEC-031 to DEC-036 are not proposed. This is an omission, not a wrong
mark.
- **Scope:** out.
- `Ordinary work: no, because only a reader of those interior entries meets it.`
- `Consequence: other.`
- **Class:** row.

**F12: Supported marks that would read better with a part.**
- DEC-261 ← DEC-1033: through DEC-798, which DEC-261's status names. Suggest "(2)(b): the query server on the GPU,
  replacing DEC-798's CPU-only one".
- DEC-421 ← DEC-572: stated by DEC-586 DP-30. Suggest "(for ticket files)".
- DEC-513 ← DEC-536: a `Restores`. Suggest "(restored)".
- DEC-709 ← DEC-719: suspends it and replaces it once AR-3 is back. "Changed by" is right; not SUPERSEDED.
- **Scope:** in.
- `Ordinary work: yes.`
- `Consequence: other.`
- **Class:** row.

## Lines to drop or rewrite before the commits

| Patch | Register line | Entry | Action |
|---|---|---|---|
| a1 | 13005 | DEC-1050 | drop (F1) |
| a1 | 13528 | DEC-1084 | rewrite: ` · **Changed by:** DEC-1087 (13) (W2-33's layer lines back in Wave 2)` (F5) |
| a2 | 1100 | DEC-120 | drop (F2) |
| a2 | 7703 | DEC-724 | drop (F3) |
| a2 | 5258, 5369, 5401 | DEC-480, DEC-490, DEC-492 | drop (F4) |
| a2 | 4965 | DEC-454 | rewrite: ` · **Changed by:** DEC-868 (items 1 (b) and 3), DEC-899 (P-IS-4 (a))` (F4) |
| a2 | 4992 | DEC-455 | rewrite: ` · **Changed by:** DEC-899 (P-IS-4 (a))` (F4) |
| a2 | 11511 | DEC-941 | rewrite: ` · **Changed by:** DEC-946 (blocks A to E: their order)` (F5) |
| a2 | 12392, 12831 | DEC-988, DEC-1032 | rewrite (should): `DEC-989 (item 3's baseline)`, `DEC-1033 (items 2 and 3)` (F5) |
| b1 | none | none | commit as drafted |

**Wrong marks: 12.**
- DEC-1050←DEC-1057
- DEC-120←DEC-173
- DEC-724←DEC-860
- DEC-454←DEC-904
- DEC-455←DEC-904
- DEC-480←DEC-899
- DEC-480←DEC-904
- DEC-490←DEC-868
- DEC-490←DEC-899
- DEC-490←DEC-908
- DEC-492←DEC-904
- DEC-492←DEC-908

**Wrong parts:** 2 must be rewritten (DEC-1084, DEC-941) and 2 should be (DEC-988, DEC-1032). **Wrong b1 ids:** 0.

## For the CTO to decide (no owner package needed)

1. Whether to keep DEC-454←DEC-899 and DEC-455←DEC-899. They are supported at medium confidence, by analogy with
   DEC-492's existing mark.
2. Whether to rewrite ARCHIVE-SUPERSEDED line 34 in the same series. It clears 9 findings, and the sitting's H2
   recommends it.
3. Whether to keep DEC-016 and DEC-798 in b1 (F9). I recommend keeping them.
4. check.py's new expectations: 86 after a1 and 46 after a2 (37 with the archive rewrite). Rebuild, then re-run check,
   before applying.

```verdict
{"kpis": [
 {"kpi": "KPI1 a1 marks (with F1 dropped, F5 DEC-1084 rewritten)", "verdict": "pass", "findings": [
   {"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F8", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F11", "scope": "out", "ordinary_work": "no", "consequence": "other"},
   {"id": "F12", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "KPI2 a2 marks (with F2-F4 dropped/rewritten, F5 DEC-941 rewritten)", "verdict": "pass", "findings": [
   {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F7", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "KPI3 every free-text mark and the labelled marks checked; no wrong mark committed (holds only with the drops above)", "verdict": "pass", "findings": []},
 {"kpi": "KPI4 b1 sources on open and in-progress tickets only", "verdict": "pass", "findings": [
   {"id": "F9", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
   {"id": "F10", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "Guards: DEC-866 append-only status lines, DEC-1088 (6) closed tickets untouched, clean apply at 2f9c80b1f807, gov links counts as claimed", "verdict": "pass", "findings": []}
]}
```

## Evidence

- **Scratch folder:** `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/ad44f5fe-276d-46b7-85cd-df9f8d97a3ec/scratchpad/w2-130-audit/`.
  It holds `links-*.json` (each stage, as drafted and corrected), `marks.json`, `pairs.json`, `labels.txt`,
  `b1-added.json`, `b1sample.txt`, `b1kpi.txt`, `rebuild/` (the patches rebuilt at today's head) and the scripts.
- **Disk:** before the heavy runs the disk gate was open (839 GiB free) and the folder held 2 inodes and 8 KB. At the
  end it held 4,255 inodes and 59 MB; the clone was removed after this record.
