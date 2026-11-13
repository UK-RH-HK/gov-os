# Anti-drift audit (a): decisions since the emergency began (DEC-1125 (3) (iii) a)

Written 2026-11-11 by the CTO's helper (orchestrator role, Sonnet, effort high, class C1). Tree: `w2/integrate` at
`797495bdf`, with this audit's edits uncommitted for the CTO to check and commit. The script is
`/tmp/gov-os-emg-auditdec/audit.py` (and `tickets.py`); its output is `out.txt` (before the fixes) and `out2.txt` (after).

## Range and counts
- The emergency began with DEC-1033 (2026-11-02); DEC-1032 (the freeze) came the same hour. Range checked:
  **DEC-1032 to DEC-1125, 94 decisions**, every one has a register heading (no gaps). 85 are owner decisions and 9 are marked
  delegated (DEC-1043 and DEC-1048 hold both kinds of item).
- In `DECISIONS-IN-FORCE.md`: **86 of 94** have a line (was 83); 8 have none, with reasons below.
- In `DECIDED-NOT-DONE.md`: 66 of 94 are named in a row or a table line; of the other 28, 22 are named in
  DECISIONS-IN-FORCE only (standing rules, one-offs done, or superseded) and six in neither (DEC-1034, 1035, 1036,
  1041, 1042, 1044: one-offs applied in their tickets, below).
- DECIDED-NOT-DONE rows: **120 numbered rows** (was 118 with one duplicate number); one gap (54, never used).
- Register: the last version row is 0.509 (2026-11-11) and names DEC-1125; "Next free id: DEC-1126"; every decision in
  range has its own version row; no next-free-id step goes backwards. (iv) agrees.

## Checks (script, then reading)
(i) A line in DECISIONS-IN-FORCE: 86 of 94. No line, by reason:
- DEC-1034, DEC-1035, DEC-1036, DEC-1042, DEC-1046: delegated or one-off choices of W2-112's and W2-126's runs, applied
  in those tickets (cited in DAEO-clon, DAEO-1vka, DAEO-2tfd, DAEO-jpr0). What still holds of them is in DEC-1043 (2),
  DEC-1048 (the no-private-reranker rule) and rows 9 and 10 of DECIDED-NOT-DONE. No line needed.
- DEC-1041, DEC-1044: delegated one-offs of W2-20's and W2-42a's runs; the paths they added are in the tickets, but the
  tickets cite neither decision (gap G2 below).
- DEC-1066: partly replaced by DEC-1067 (2) and DEC-1070 to DEC-1074; DECIDED-NOT-DONE §1c lists it as superseded.
(ii) Changed or replaced decisions: 23 pairs where the script found no single line naming both. Reading them, 14 were
real marks missing in DECISIONS-IN-FORCE (fixed, see F-list); the rest name a changed item the list does not carry as in
force (DEC-1039 (3), DEC-1047 (2), DEC-1066, DEC-1084's W2-33 line), so nothing there misleads.
(iii) Pending actions: every decided item with a trigger in DEC-1100 to DEC-1125 has a row or a DONE mark, except three
(rows 119-121, added). DEC-1032 to DEC-1099 were read through the 11-08 audit's rows 0 to 0c and the tables; no item
without a row was found beyond the stale rows fixed below.
(iv) Version table and next free id agree (DEC-1126); the register's header block still reads "Version 0.307, 2026-10-20" (gap G1).

## Fixes made (only the two record files; each cites its source)
DECISIONS-IN-FORCE.md
- F1 header (lines 3-5): "to DEC-1122 on 2026-11-10" now also "to DEC-1125 on 2026-11-11". Source: register v0.509.
- F2 new line after G-14's: DEC-1063 (ACT-G14b, `e02d55e40424`): a `class: coordination` ticket has as its own tests only
  its own folder. Source: DEC-1063 (it had no line).
- F3 DEC-1057 cited at R-11/R-8, O-6, R-6, R-12 and the restart classes; DEC-1058 at P-ACT-SPLIT (and the shared servers
  now class (a), DEC-1104 (2)). Source: DEC-1057 (Changes, Decision (4), (6)), DEC-1058, DEC-1104 (2). Both had no id in
  the list although their rules were there by name.
- F4 marks of changed entries: DEC-1069 (12) by DEC-1076 (4) and DEC-1079; DEC-1070 (2)-(4) by DEC-1074 (1);
  DEC-1071 (3) by DEC-1074 (4); DEC-1073's "within 3 points" now 5 (DEC-1074 (4)); DEC-1074 (3) by DEC-1076 (1) and
  (7) O1 (A) by DEC-1087 (3); DEC-1075 (1) by DEC-1076 (1); DEC-1080 (2) by DEC-1081 (1) and its premise by DEC-1082 (0);
  DEC-1083's K9 bar by DEC-1097 (1)(d) and DEC-1098, W2-66b/W2-90c by DEC-1084, W2-33's layers by DEC-1087 (13);
  DEC-1086 C's cap by DEC-1091 (1); DEC-1067 (b) by DEC-1071 and (f) by DEC-1090/DEC-1095; DEC-1115 (4) by DEC-1122 (2);
  DEC-1119 (1) by DEC-1120. Source for each: the status line's "Changes" or "Changed by" in the register, and the
  version table. No decision's content was changed, only the marks.

DECIDED-NOT-DONE.md
- F5 row 43 (launch script): WAITS → DONE: W2-149 merged `b4de529b`, installed `baac0b2c2` (rows 67, 75).
- F6 row 44 (fixed briefs): WAITS → PARTLY: set-up A's five briefs approved 11-09 (DEC-1113); the memory audit's briefs
  wait for row 117.
- F7 row 45: "every two weeks" → weekly (DEC-1125 (2)); wait pointer corrected.
- F8 row 85: marked changed by DEC-1122 (2) (usage (A) in force from 11-10 until 11-15 09:00).
- F9 row 19 (W2-139, W2-140): "DUE NOW" → MERGED `fa2737766` (rows 36, 63).
- F10 row 21: next → DONE (rows 31, 32). Row 25 and row 29: "WAITS" → pointers to row 66 and the seal done (row 28).
  Row 30: R3 and R5 MERGED `4bc040898` (row 81). Row 52: operator agent built and applied (rows 56, 58, 59, 68, 76).
- F11 row 108 (template 1.0.1): DONE, merged `6cc09c7ea`, approval line `99419edb4`. The earlier second row numbered 108
  (ACT-WIN-TOAST-1) renamed 108a so each number is unique (the template row keeps 108: reviews cite it).
- F12 new rows: 119 (DEC-1117: the wake DONE `905b82a3b`; the spend-log unit not verified; the owner's phone check),
  120 (DEC-1104 (2): re-pins by the agent decided again after one rehearsed re-pin; pushes for (a) ACTs two weeks, to
  about 11-23), 121 (DEC-1103 (3): `~/gov-os-writer` and `~/gov-os-checker` retired once the launch script is the default).
- F13 a note under "## 1": sections 1 to 3 are the 11-08 audit's text, kept; section 0 holds where they differ.

## Gaps left, with a recommendation
- G1 (CTO): the register's header block says "Version 0.307, Date 2026-10-20"; the table's last row is 0.509, 2026-11-11.
  Recommend the CTO updates the header in its next decision commit (the register is the CTO's; I did not touch it).
- G2 (CTO): DEC-1041 and DEC-1044 are cited in no ticket file, but their changes are in DAEO-r30l (W2-20's allowed
  paths gain `src/gov/secrets/__init__.py` and `src/gov/codeintel/__init__.py`) and DAEO-03ub (W2-42a's
  `tests/unit/guard/test_decide.py`). DEC-1088's standing rule says an open ticket's change is marked with its
  decision and `gov links` flags one without. Recommend the CTO adds the two marks (ticket edits are the CTO's).
- G3 (ticket audit): no ticket exists for W2-143 and W2-144 (the glossary's build and its refresh, "proposed, not
  filed"; DEC-1097 (6) (b) builds only if the retest helps) and none for W2-132 (a split of W2-128 "by design"). The
  rows stand as notes; nothing is filed until the glossary retest (row 17). Recommend the ticket audit leaves them.
- G4 (CTO): row 72 ("a fresh CTO session ... the owner switches when ready") and rows 14 and 17 ("DUE NOW" since the
  80: rubric v3, the glossary retest) read stale. Under usage (A) (DEC-1122 (2)) they are not the lift's critical path
  and wait for the reset 11-15. Recommend the CTO re-labels them "held by usage (A) until 11-15" or runs them; I did
  not, because that is a judgement of the CTO's.
- G5 (CTO): rows 99 (the 5-minute cache), 100 (the daily cost job) and 119 (4) (the spend log in one unit) are NOT
  STARTED or unverified; git shows no commit for them. Both are after-the-lift items under usage (A).
- G6 (owner, standing): rows 106 (ACT-EFFORT-HIGH-2, waits for the owner's yes) and 109 (the template F4 delta, waits for
  the reset); row 120's first part has no event that triggers it (the lift's re-pin is by hand): recommend the owner
  closes it with "re-pins stay the owner's" at the next review.
- G7 (CTO): rows 38 (W2-66c "its test designer next"), 46 (weekly counts), 60 (live-hook suites' folder) show NOT STARTED
  in their last text; I did not find a commit that contradicts that, so I left them.
- No row has a missing home ticket: the home of rows 119-121 is DAEO-sdxk (W2-00, coordination), which exists.
- Not checked here: DEC-1032 to DEC-1099's trigger items beyond the rows listed above (about 40 rows' states were taken
  from the 11-08 and later edits, not re-verified against git one by one), and the CTO's scratch records (not in the tree).

## What I did not do
No register, ticket, src or test edit; no commit; nothing from `~/gov-os-eval/` or any hidden folder; no full suite;
no install. The script ran with `python3 -I` and wrote only to `/tmp/gov-os-emg-auditdec/`.
