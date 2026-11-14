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

---

## Final patches (after the owner's sitting, DEC-1098 (3)): audit of 2026-11-09

Same auditor and the same rules: read-only on the repository, a throwaway `git clone --shared` in my scratch folder, no
commit in the repository.

**Head:** `w2/integrate` at `ce7f10eb8a2a`. The patches were built at `d4463749610c`; the two commits since then touch
only evaluation files and DECIDED-NOT-DONE, not the register, the archive or the tickets.

**Verdict: READY to commit f1, f2, f3 and f5 once one f5 mark is dropped: DEC-853 ← DEC-884 (F14).**

### What I checked

- **Apply:** `git apply --check` passes for f1, f2 and f3 at today's head. Applied in order, f5 applies on top.
  f4-in-force.patch is empty, which matches `in_force_clashes: []`.
- **The 150 rulings, all of them:** I parsed each row of W2-130-SITTING.md, groups A to F, then read the first status
  word of each entry from the patched register.
  - All 150 match: ACCEPTED 32, SUPERSEDED 5, WITHDRAWN 1, DEFERRED 2, DONE 103, and group F's 7 stay ACCEPTED.
  - Each SUPERSEDED, WITHDRAWN and DEFERRED names the settler the sitting names: DEC-002 by DEC-058 and DEC-064; DEC-043
    by DEC-064; DEC-045 and DEC-047 by DEC-058; DEC-013 by DEC-074; DEC-062 by DEC-842; DEC-018 and DEC-019 to Wave 3.
- **No substance changed:** 145 register lines changed, all of them `**Status:**` lines, and the line count is the same.
  - 143 lines carry the new word first, then the old status text whole after "; it was". Some add only the
    `· **Changed by:**` mark the ruling names, at the end.
  - The 13 marks the group B rulings name were applied as the rulings name them.
  - DEC-786 (DEC-942; DEC-847 is already on its line) and DEC-927 (DEC-1057 (item 2)) are pure appends.
- **f2, 7 archive lines:**
  - group F's three lines now agree with the rulings (DEC-729, DEC-786; DEC-912 and DEC-918; DEC-924, DEC-927, DEC-928);
  - DEC-501 and DEC-502 are split (H2);
  - the chain lines for DEC-038 and DEC-045 no longer read as changing their first id, and the facts are kept (each
    successor is on its own line).
- **f3 is marked as DEC-1088 (6) requires:** the changed KPI 4 line carries "[changed, DEC-1098 (3); DEC-1088 (6)]".
  - A DEC id in the changed lines marks the change even without a trailer. TICKET_CHANGE_UNMARKED stayed 93 in my clone,
    whose commit had no trailers.
  - DAEO-q8cl is open, so this is not a closed-ticket edit.
  - Its sources gain DEC-1098 and DEC-1088, the ids its bracket names.
- **f5, all 17 marks** checked against each changer's label or text (findings below).
- **Tests:** I ran the tests that read the real register on the patched clone: links, the store's links, retrieval,
  W2-55, W2-87, W2-129, W1-26 and the decisions unit tests. 377 pass and 4 fail.
  - 3 of the 4 fail the same way at today's head without the patches.
  - The 4th, `test_the_branch_changes_nothing_in_the_register_against_its_base`, compares HEAD with
    `merge-base(HEAD, w2/integrate)`. It fails only because my clone's commits sit ahead of w2/integrate. On
    w2/integrate itself the merge base is HEAD, so it passes.
- **Guard refusals:** 1. A piped `git diff` between two of my clone's commits got "could not decide". I took the
  refusal and read the patch file and the clone's working file instead.

### `gov links --all` at today's head (my clone)

| Code | before | f1 | f2 | f3 | f5 |
|---|---|---|---|---|---|
| ENFORCES_SUPERSEDED | 44 | 73 | 73 | 73 | 73 |
| NOT_IN_FORCE_AS_RULE | 142 | 20 | 20 | 20 | 20 |
| STATUS_CONFLICT | 116 | 13 | 6 | 6 | 6 |
| UNMARKED_CHANGE | 37 | 28 | 25 | 25 | 8 |
| UNLINKED_ID / UNKNOWN_ID / CLOSED_TICKET_EDITED / TICKET_CHANGE_UNMARKED | 1097 / 558 / 117 / 93 | same | same | same | same |
| **total** | 2204 | 1999 | 1989 | 1989 | 1972 |

- **The claim holds:** these are exactly final-check-report.md's figures.
- **What is left:**
  - STATUS_CONFLICT 6 is MR-1 to MR-6 (group G, for product-spec to regenerate).
  - UNMARKED_CHANGE 8 is the 3 pairs the audit dropped and the 5 misreads whose changer is older than its entry.
- **Once F14 is dropped,** UNMARKED_CHANGE after f5 is 9 and the total is 1973.

### Findings

**F13: The rise in ENFORCES_SUPERSEDED (44 → 73) is expected, but none of the 29 new findings is a real enforcement.**
- **Expected:** W2-55's `check_propagation` reports any line under `tests/` or `src/` that cites a superseded id in a
  file that cites none of its successors. Once DEC-002 and DEC-013 are SUPERSEDED, every such citation is reported.
  These are the 29: DEC-002 23, DEC-013 6. DEC-043, DEC-045 and DEC-047 are cited nowhere it searches.
- **Not real:** I read each of the 29 lines. All are synthetic fixture ids in test registers and records, for example:
  - `### DEC-002: The second decision` (W1-10);
  - `"### DEC-001 — The first\n- **Status:** SUPERSEDED by DEC-002"` (store);
  - `records/decisions/DEC-013.md` (W2-92);
  - `"DEC-013"` as an id shape in the W2-03 grammar.

  No test enforces Contract v3 or the old task DAG.
- **Why it is safe:** propagation is a notice, not a gate. It is outside `gov check`'s list, and the tests that run it
  use `tmp_path`.
- **The fix:** a `**Kept:**` reason on DEC-002 and DEC-013 ("fixture ids in tests, not citations"), or a W2-55 row that
  skips fixture literals. The CTO decides; it does not block.
- **Scope:** in.
- `Ordinary work: yes, because the notice shows 29 lines to anyone who reads it.`
- `Consequence: other (noise in a notice; nothing fails open).`

**F14: f5's DEC-853 ← DEC-884 (item 4) is wrong.**
- **The text:** DEC-884's `**Changes:**` reads "DEC-853 item 4 (the re-pin at a commit holding W2-50's fix): still
  holds, since the combined re-pin's commit holds it". DEC-884 confirms DEC-853 item 4; it does not change it.
- **Why it was proposed:** the label lists the id, so `--propose-marks` took it.
- **The fix:** drop this one mark from f5. DEC-853 is DONE now, so the cost is small.
- **Scope:** in.
- `Ordinary work: yes.`
- `Consequence: other.`

**The other 16 f5 marks are supported by their changer's own text:**
- DEC-005←085 (Amends, "readiness reduction")
- DEC-044←096 (Amends)
- DEC-034←396 (Amends)
- DEC-721←953 (Changes: exit criterion 1)
- DEC-761←772 (item 1). The free-text one: "This replaces DEC-761 item 1's line".
- DEC-884←918 and DEC-884←921 (item 3)
- DEC-891←924
- DEC-896←1057 (item 2)
- DEC-897←909 (item 1)
- DEC-899←902, 912 (item 2), 918 (item 4), 924 and 925 (item 4)
- DEC-914←916 (item 4, "answered")

**DEC-902's part, "(item 10: the proposal decided)",** is supported: DEC-902's `**Changes:**` reads "DEC-899 item 10
(the proposal decided)". As in F6, the item number is DEC-899's, but the words make that plain.

```verdict
{"kpis": [
 {"kpi": "f1 statuses: all 150 as ruled (DEC-1098 (3)); new word first, old status kept whole; no substance changed", "verdict": "pass", "findings": [
   {"id": "F13", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "f2 archive lines agree with the rulings and H2", "verdict": "pass", "findings": []},
 {"kpi": "f3 KPI 4 changed and marked under DEC-1088 (6)", "verdict": "pass", "findings": []},
 {"kpi": "f5 marks supported by the register's text (with DEC-853<-DEC-884 dropped)", "verdict": "pass", "findings": [
   {"id": "F14", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "clean apply at ce7f10eb8a2a; gov links 2204 -> 1972 as claimed", "verdict": "pass", "findings": []}
]}
```

**Evidence:** the scratch folder is `scratchpad/w2-130-audit/` (`links-*.json` for each stage, `fcheck.py` and
`fcheck.txt`, `reg2.py`). The disk gate was open (830 GiB free). The folder peaked at 36,002 inodes and 209 MB; after
the clone was removed it held 54 inodes and 12 MB.
