# D9-FATES-AUDIT: the independent audit of the 792 KPI lines (DEC-1083 (1)), before any edit

- **By:** an independent auditor (read-only), 2026-11-06. **Verdict:** DONE_WITH_FINDINGS. The counts are exact, and
  the draft needs 40 corrections before it is applied, 7 of them high severity.
- **Counts (confirmed):**
  - 94 tickets and 759 lines, plus W2-129's 21 and W2-130's 12: 792 in all.
  - Every per-ticket count, DAEO id and status matches the front matter.
  - No ticket has two fates.
  - The six repair tickets (23 lines) are outside the count; all their parents are closed.
- **Ticket fates (confirmed):** keep 19/157, re-scope 21/229, merge 7/59, close formally 16/126, retire 22/131, Wave 3
  9/57.
- **Line fates as counted:**
  - met with evidence 116; met in part or evidence missing 12; built on a branch, not merged 4;
  - open 383;
  - moved to a named live ticket 45; moved, home not settled 16;
  - lifted or dropped 27; Wave 3 61; retired 128.
- **Commits:** every cited met commit is on `w2/integrate`. `1aeae788` (W2-32 S11) and `9e85fb97` (W2-61h S7) are
  branch tips, as the draft says.
- **Dependencies:** acyclic after §3's edits. W2-27's 46 → 44 holds, and every K9 ticket is in the new list.

## The 40 corrections
1. **[high] W2-111, all 7 lines.**
   - Draft: "met by D-4's cut (`6008a41f`)".
   - True: not met. `6008a41f` touches only the READMEs of W1-02, W1-05 and W2-57.
   - There is no `tests/acceptance/W2-111/`, no `Rewrite-Reason: DEC-979`, and no CPU-time or load code.
   - Fix: not a formal close. **The owner decides:** keep it open, or retire it with a reason.
2. **[high] W2-55 S1.** Only the validator half is met. LINK-INTEGRITY.md:314: `TAG_MISSING` gives 1,069 lines until
   the backfill is accepted. **The owner decides** the re-word.
3. **[medium] W2-55 S6.** No measure was recorded after the merge (README:45).
4. **[medium] W2-55 S8.** Only `--in-force` is built; the hook half is the owner's CIT-P.
5. **[medium] W2-55 S5.**
   - The amendments of S5 and F3 in LINK-INTEGRITY §6.1 (lines 421–422) are not applied.
   - S5's second half is W2-130's clean-up.
6. **[low] W2-55 S4.** It is built (`docs/research/W2-55-backfill.md`, `e0cb7d13`), not lifted. F4 follows S4.
7. **[medium] W2-15a S3.** The lighter reranker was "not run (not installed)". D4B-TRIAL-W4 trialled only larger
   ones.
8. **[medium] W2-96.** It landed at `107514f5`. S6 is half met: `brief-engineer.md` does not name `gov accept`.
9. **[medium] W2-131.** S1–S3, F1 and F2 are met at `03336f19` (`gov accept` 29/29); only S4 is open.
10. **[medium] W1-01b.** Already met by `10025b21` (W1-01 README:155), so it closes now, not at D-10.
11. **[high] W2-66b.**
    - Not built: `CODE_SUFFIXES` at `test_w2_66_live_test_map.py:34` has no `.ps1`.
    - D-10's full run cannot show it: its row is the last of seven under `rep:` (`optin-lifted-breadth.txt:1133`;
      `conftest.py:46-48`).
12. **[high] W2-90c.** W1-05's orchestrator-asks case and four W2-59 `[stop[0]]` rows sit in `optin-lifted-guard.txt`
    (lines 276 and 427–430), which run report-only in D-10.
13. **[medium] W2-92 S6.**
    - 14/15 at `88748f99`; green only at `3679ca0b`.
    - The 1.2 s median is recorded nowhere (evidence:120).
14. **[low] W2-91.**
    - S6 and F4 say "not run here" (evidence 342, 346): cite D-4b measure 1.
    - S1's re-word after D-7 (`27a80411`) is not applied.
15. **[low] W2-13 S6.** Add `27a80411`.
16. **[low] W2-61h.**
    - S4 and F3 were red at `cd8e5420` until the re-pin, and no green commit is cited.
    - S1 and S3 state 24 hidden; DEC-1069 made it 40.
17. **[low] W2-112 S3.** The 48-question half is "not yet measured" (research:173).
18. **[low] W2-122 S3.** The "alone" measure was not taken (evidence:60).
19. **[low] W2-126 S6.** The per-day "after" figure was not measured (evidence:81–82).
20. **[low] W2-04.** The basis is DEC-1052 M-1 only. Run `gov accept` once for the close.
21. **[medium] W2-20 S12 → W2-123.** The admission half stays with W2-20.
22. **[medium] W2-20 S6, S9 and S11.** "To W2-121 or lifted" is not one fate.
23. **[medium] W2-21.**
    - S1–S4 and F1 are unmapped.
    - S2 duplicates W2-33 S2, and S3 and S4 overlap W2-60a.
    - The rows receiving them do not show them as incoming.
24. **[medium] W2-117 S7** folds into W2-115 S11 (W-2), so W2-115 is 19 + 8.
25. **[low] W2-118 F2** belongs to S2, so it goes to Wave 3 with S2.
26. **[medium] W2-06 → W2-116 and W2-122.**
    - There is no per-line split.
    - W2-122 is a formal close that `5543a03a` does not meet.
27. **[medium] W2-24 and W2-25.**
    - Their lines are both retired and moved.
    - Move only W2-24 S5 and F1 and W2-25 S1, and retire the rest (W-4).
28. **[high] W2-99's 13 lines.** DEC-1083 (6): the template and brief lines go to W2-128, and the rest are retired.
    - **The CTO's split:** S1, F1, F2, S3, F4, S6 and F7 go into W2-128.
    - S2, F3, S4, F5, S5 and F6 are retired.
29. **[high] W2-32 S6 and R2-F1.**
    - DEC-1083 (3): S6 is dropped, and R2-F1 goes to the Wave 3 parking list.
    - Decide R2-F1's strict-xfail case.
30. **[medium] K9 bar's home.**
    - The draft puts the fresh-80 verdict lines in W2-15b, which leaves K9.
    - §3 item 1 lacks DEC-1083 (2)'s reranker and the 95 % target.
    - The bar needs a line inside W2-27's dependencies (W2-32 S9).
31. **[medium] W2-133** (W2-131's follow-up, DEC-1083) is missing from §2.
32. **[low] DEC-1083 (8).** Mark the six repair tickets retired; their 23 lines go with them.
33. **[low] TPL-5 and the `core.bare` half** are settled by DEC-1083. Remove them from "Not settled".
34. **[low] DEC-1083 (4), (5), (7) and (9)** are reflected already. Mark §5 decided. W2-42a's new lines are still to
    be written.
35. **[medium] "3 approved lines not yet applied" undercounts.** Also missing:
    - D-11's two lines;
    - W2-42a's, W2-115's Q-2–Q-11 and T-9, and W2-121's O-12;
    - W2-11b S2 into W2-128;
    - the re-wordings in findings 5, 14 and 16.
36. **[low] W2-11 S13's fate under W-10** is not stated. The row says met; §4 counts it open.
37. **[low] W-3's lifts are not applied line by line.** "About 34 lifted" names only 14.
38. **[low] Dependencies.**
    - W2-40 depends on W2-21 (merged) and W2-45 on W2-08 (retired), and neither is edited.
    - W2-46's new list is missing.
    - `deps` and `depends_on` differ in W2-55 and W2-60b.
39. **[low] READY has three homes** (W2-82, W2-128 S10, W2-115 S11); W-2 requires one.
40. **[low] The header's W2-131 note is stale** (it merged at 11:40).

**Risks if applied as written:**
- 15 lines would be recorded as met that are not.
- Lines moved into formal closes (W2-122, W2-123) may be lost.
- D-10's green run cannot evidence cases that D-4 moved into opt-in lists.

**Unresolved:**
- Whether W2-61h S4 and F3 turned green after the re-pin.
- Which four W2-59 cases W2-90 named.
- The lines not yet written (finding 35), which are outside the 792 and need the second pass.
