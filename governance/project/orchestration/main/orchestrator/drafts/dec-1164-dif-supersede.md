# DEC-1164 draft: the DIF sweep's supersede entry (DEC-1157 (16), DEC-1163 (9))

Drafted 2026-11-13 by a helper of the CTO (read-only; this file is the only write). Sources read: `drafts/dif-sweep-20261113.md`
(the sweep; its rows are cited below as A1-A16 and B1-B27 in table order), `docs/DECISION_REGISTER.md` at `df9d442e8`
(DEC-1163 recorded), DEC-866, DEC-1157, DEC-1158, DEC-1159, `governance/project/orchestration/DECISIONS-IN-FORCE.md` at
`fb96ea563`, `governance/project/prompts/w2-orchestrator.md` at `e93d846a8`, `START-NEXT-SESSION.md`, the crontab (read only),
`acts/ACT-OPERATOR-HOURS-3.package.md`, `nightly/quiet_check.py`, `nightly/nightly.sh`.

**What changed since the sweep was written (so this entry is smaller than the sweep's 38):**
- DEC-1158 (00:30) lifted the emergency: rows A1-A6, A8, A9 are done and marked (status lines checked: DEC-1032, DEC-1033,
  DEC-1047, DEC-1049, DEC-1050, DEC-1051, DEC-1037, DEC-1039 all carry their DEC-1158 marks).
- DEC-1159 (1) put the nightly beside the leads: row B3 is done (DEC-1132 marked).
- `84cc42343` marked DEC-1140 (2), (5) and `fb96ea563` refreshed the DIF: row B5 is done. The same commit rewrote
  START-NEXT-SESSION: row B27 is done (two stale lines remain, part 3c).
- DEC-1158 (4) already decided the prompt's §0 bullet (row B15); its text is `drafts/PROMPT-s0-dec1158.md`, not yet applied
  (prompt line 52 unchanged at `e93d846a8`). It is carried in (21) so the owner's operator makes one prompt edit.
- DEC-1163 (5) gave `yes ACT-OPERATOR-HOURS-3 716da9dc`, so row B1 can be marked now (it did not add the marks: its commit
  changed no earlier status line).

**Line numbers** are at `df9d442e8`. DEC-1163 sits at register line 722 (before "## 12. Change log"), not after DEC-1162 at the
end; if it is moved to the end, every register line number below falls by 16. Each mark also names its entry's heading, so
`grep -n '^### DEC-<n> '` finds it either way.

---

## 1. The entry, as it would be appended (after DEC-1163, before the version table)

### DEC-1164 — The DIF sweep decided: the holds it found that no entry lifted are superseded, spent or amended; DEC-946's priorities and the operator's night sleep superseded; thirteen rules amended; the prompt's lifted and spent holds removed (standing for (4), (5), (9)-(19))
- **Status:** PROPOSED (the CTO, 2026-11-13, for the owner's acceptance; on acceptance it reads: ACCEPTED (owner, 2026-11-13, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-13)`); (4), (5), (9)-(19) standing) · **Under:** DEC-1157 (14), (16), DEC-1158, DEC-1163 (9), DEC-866, DEC-1052 (the basis) · **Supersedes:** DEC-946 (items 1-6, 8, 9), DEC-1141 (6), DEC-1142 (5), DEC-1064 (2)'s hold until W2-127 · **Changes:** DEC-1018 (1), DEC-1028 (6), DEC-1038 (4), DEC-979 (D1), DEC-1039 (1b), DEC-1053 (6), DEC-1057 (5), DEC-925 (2), DEC-1058 (b), DEC-1067 (GPU safety), DEC-902 (1), DEC-991 (3), DEC-1088 (6), DEC-989 (2), DEC-1104 (2), DEC-1157 (2) · **Changes (spent):** DEC-1052 (the plan bullet and "Tonight"), DEC-1055 (its order, (8)-(10)), DEC-1086 (D), DEC-1087 (1)-(11), DEC-1097 (1)(g), (9), DEC-1098 (6), DEC-1115 (4), DEC-1122 (3) · **Marks corrected:** DEC-847, DEC-949, DEC-1122 (2)
- **Context:** the CTO's sweep of DECISIONS-IN-FORCE, the prompt and START-NEXT-SESSION (DEC-1157 (16), `.gov-runtime/scratch/orchestrator/drafts/dif-sweep-20261113.md`): 43 rows, 38 still holding or slowing work, 5 kept. Why they stood: holds "until the owner lifts it" with no lift recorded; end conditions met but never written back; DEC-866 marks only for the parts a decision named; the prompt's holds outside the list; the weekly basis review (D-11) deferred behind the lift. DEC-1158, DEC-1159 and the DIF refresh of `fb96ea563` settled 11 rows; this entry settles the rest.
- **Decision:**
  - (1) **Traceability (no new mark for these):** the sweep's 43 rows are disposed as follows. Already settled: A1-A6 (DEC-1032 (2), (3)(v), DEC-1033 (1), (4), DEC-1047 (1), (2), DEC-1051, DEC-1049, DEC-1050 (5): DEC-1158 (1)); A8, A9 (DEC-1037 (3), DEC-1039 (3), (3b), (4) spent: DEC-1158 (2)); B3 (DEC-1132 (4) and `quiet_check`: DEC-1159 (1)); B5 (DEC-1140 (2), (5) and DEC-1138: DEC-1157 (2), (8), marks `84cc42343`, the DIF `fb96ea563`); B27 (START-NEXT-SESSION rewritten, `fb96ea563`). Superseded or spent here: A7 (2), A15 (3), B1 (4), B6 (6), B26 (7). Amended here: B4 (5), A10 (8), A11 with B20 (9), A12 (10), A13 (11), A14 (12), A16 (13), B2 (14), B9 (15), B13 (16), B17 (17), B18 (18), B19 (19). A4's open half: (20). The prompt's rows B7, B8, B10, B11, B12, B14, B15, B16: (21). **Kept, untouched** (they protect the machine or the governance): B21 the ready list and committed claims (DEC-1007, DEC-1012 (1), DEC-999); B22 the disk gate (DEC-898); B23 set-up A's 100 % bar (DEC-1128 (2), DEC-1133 (2)); B24 narrow checks and the land pre-check (DEC-1154, DEC-802); B25 the ACT exemption commit and the rehearsal (DEC-1136 (2), DEC-1057); and DEC-1157 (14)'s whole list. **Also kept:** DEC-1093 (1)'s close form for W2-139 and W2-140 (both still open, so not spent); DEC-1159 (1)'s "nightly.sh takes the heavy slots and the rebuild lock itself" (decided after the sweep, which proposed dropping that lock: not done here).
  - (2) **Spent: the lift's plan (row A7).** DEC-1052's "The plan, updated" and "Tonight" bullets and DEC-1055's order with its (8), (9) and (10) (window 3 before D-5, M-5 held, the machine split of D-4 and D-4b) are spent: D-4 to D-10 are done and the lift is recorded (DEC-1126 (1), (7), DEC-1158). Kept: DEC-1052's basis, rows, templates, test-suite cut and homes, and DEC-1055's other items as product record. **D-11 stands as its own line:** the weekly basis review of everything in force, with each item's measured cost, the lift-or-remove list to the owner first (DEC-1052's basis, trigger 3); this sweep counts as its first run.
  - (3) **Met: DEC-1064 (2)'s hold (row A15).** "Sandboxed workers run no `gov retrieve` and no real-model test until W2-127" is closed as met (W2-127, `DAEO-1vka`, closed); sandboxed searches are unranked, named and counted (DEC-1114 (3)), and the cache's write by its ACT (DEC-1163 (9)). Its other half, no private embedder or model on the CPU in the sandbox, stays as DEC-1065's line.
  - (4) **Superseded: the operator agent's night sleep (row B1), standing.** DEC-1141 (6) (the operator asleep while the nightly runs, from 03:00), DEC-1142 (5) (ACT-OPERATOR-HOURS-1 "keep `0210`" and -2, which built that rule) and DEC-1104 (2)'s hours as DEC-1141 (6) changed them are superseded: **the operator agent is launched every 10 minutes at every hour**, and G9's two time holds (02:10 to 03:09; 03:10 to 07:59 unless the night-hold file says `false`) are removed, by ACT-OPERATOR-HOURS-3 (`yes` in DEC-1163 (5); Part B by the owner's operator, Part A by the CTO). G9's other holds stay as built (the NIGHTLY-RUNNING flag, an explicit `nightly_window`, the close queue, `log/act-in-progress.txt` as amended by (14), the operator's commit freeze, an unreadable clock). DEC-1157 (2)'s interim "until then the operator does not launch from 02:10 to 08:00" is spent once both parts are applied.
  - (5) **Changed: the main tree before the nightly (row B4; the sweep proposed superseding), standing.** DEC-1018 (1)'s "the night session makes no commit and leaves no file in the main tree from 03:15 until then" now reads: **"from 03:55 until the nightly has started (its `NIGHTLY-RUNNING` marker), the CTO makes no commit on `w2/integrate` and leaves the main tree clean."** Reason: the dispatcher's landing hold is already gone (DEC-1157 (2)), but `quiet_check.py --beside-leads` (DEC-1159 (1)) still waits for a clean main tree and a head at least 5 minutes old, so a commit at 03:58 could make the night refuse (a MISSED P1); 03:15 to 03:55 holds nothing the check reads.
  - (6) **Superseded: DEC-946's priorities (row B6).** DEC-946 items 1-6, 8 and 9 ("finish before you start", the speed and memory order of 10-29, "nothing else starts", the staggered launches, the nightly frozen) are superseded: leads start from `dispatch/ready.txt` in `gov plan`'s order (DEC-1088, DEC-1110 (3)), a ticket on EXAMIN's critical path first and never waiting (DEC-1157 (8)); a new ticket or split stays the owner's (DEC-974, DEC-1142 (8)). Kept: item 7 (if 18 November is at risk, bring what to cut, not a later date). Item 10 (ACT-RUNS-SWEEP-1) was done on 10-29.
  - (7) **Spent: sequencing tied to events that are over (row B26).** DEC-1086 D ("neither re-pin window 4 nor any experiment starts until the owner has read the seven answers": window 4 done, DEC-1089); DEC-1087 (1)-(11) (the items before re-pin window 4, the parallel-agents test, the experiments' order: all done; its (13), the three layers in Wave 2, stays); DEC-1097 (1)(g)'s "no commit, rebuild or GPU window during the run" and "the CTO's hold on W2-139 and W2-140 until after the 80", and (9)'s "no commit on integrate during the 80's run" (the 80 ran, DEC-1098 (1)); DEC-1098 (6) (the work restarts in the CTO's order up to the lift: the lift is recorded); DEC-1115 (4) ("standing until the lift": spent at the lift, already report-only by DEC-1149 (3)); DEC-1122 (3) (D-10's go: D-10 done, DEC-1126 (7)). Their DIF lines move to `ARCHIVE-SUPERSEDED.md`.
  - (8) **Changed: DEC-1039 (1b) (row A10).** Its words "keeping the embedders and rerankers on the GPU within its budget, even if that limits leads to two or three" now read **"keeping the embedders and rerankers on the GPU within its budget; memory admits each start (DEC-1157 (8))."** Kept: the GPU budget and the no-spill rule (DEC-1158 (3)).
  - (9) **Changed: the heavy-job slots (rows A11 and B20), standing.** DEC-1038 (4)'s last sentence "Every heavy job goes through the gate, the CTO's own agents included (…): none starts past it except on the owner's explicit order" now reads: **"Every heavy job goes through the heavy-job slots, the CTO's own agents included; the number of slots is set from the machine (DEC-1037 (4)) and re-sized by the CTO within the week from DEC-1157 (13)'s heavy-slot wait log and the load, a P2 listed in the digest; when the wait log shows a slot held with no heavy work running while jobs wait, the CTO may release it (a P2, listed)."** DEC-979 D1's slots follow the same re-size. Kept: the standing targets and "a breach over 15 minutes is an incident"; a land holds at most two slots (DEC-1157 (10)); landings take the next free slot first (DEC-1011 (3)).
  - (10) **Changed: settings ACTs after D-10 (row A12), standing.** DEC-1057 (5) ("until D-10, a settings change runs its own scoped tests on a clone instead of the full suite") and DEC-925 item 2's "after D-10, a full run in the close's form on a clone" now read: **"A settings change runs its own scoped tests and the DEC-866 sweep for every test that depends on what changes, on a clone, permanently; the full suite runs only in the nightly (DEC-968), never per settings ACT."**
  - (11) **Changed: (b) ACTs in the quiet hours (row A13), standing.** DEC-1058 (b)'s "and any (b) ACT in the quiet hours but an emergency's rollback" now reads: **"and, in the quiet hours, any (b) ACT but an emergency's rollback or a (b) ACT a lead waits on whose owner's yes is recorded (DEC-1157 (1))."**
  - (12) **Changed: the branches that waited for D-9 (row A14).** DEC-1053 (6) "`w2/W2-78` and the in-flight tickets' branches with unmerged work wait for D-9's fates" now reads: **"the CTO disposes of `w2/W2-78` and each in-flight branch with unmerged work now (a P2, listed in the next digest); a branch whose disposal could lose work goes to the owner first."**
  - (13) **Changed: GPU safety and the commit freeze (row A16), standing.** DEC-1067's "a measure or a store rebuild never runs beside an experiment" now reads **"a measure and a store rebuild never use the GPU at the same time"**; the 15.5 GB backstop, the spill and lost-layer pauses and "the GPU back in its budget between" stay. Prompt rule 8's "no commit on `w2/integrate` during a GPU measure or a hold" is removed (it would freeze commits and lands at every Monday memory audit, DEC-1126 (5); "a hold" has had no referent since the night hold went).
  - (14) **Changed: G9 and the act-in-progress file (row B2), standing.** DEC-1028 (6) keeps its path freeze (no CTO commit touching the paths of an ACT being applied, named in `log/act-in-progress.txt`); the operator's G9 holds only a queued ACT whose paths overlap those the file names, not every queued ACT. G9's change is operator code: an ACT (class (O)) built, rehearsed and reviewed for the owner's yes; until it is applied, the CTO holds the queue for a by-hand ACT with an empty `land.txt`, not with that file (ACT-CLAUDE-COPIES-6's F2).
  - (15) **Changed: the weekly sweep (row B9), standing.** DEC-902 (1)'s condition "only in a quiet moment: no lead, close, nightly run or trial running" is deleted: **the sweep runs weekly (Monday) and whenever the disk gate nears its floor, at any time;** its other conditions protect running work and stay (nothing modified in the last 24 hours, nothing held open (`lsof`), nothing cited as evidence, never a live session's or the live daemon's folder, never `~/.cache`, a ticket in progress's run folder, the record worktree, EXAMIN's copy or the workbench).
  - (16) **Changed: the package cap (row B13; its origin is not traced, so no register mark), standing.** The prompt's "At most five packages at a time; a P1 may bypass the cap" now reads **"At most five packages at a time; a P1, and any package a lead waits on (DEC-1157 (1)), bypasses the cap."**
  - (17) **Changed: calls that may ask, at night (row B17), standing.** DEC-991 item 3 ("in the quiet hours never run such a command; queue it for 09:00") now reads: **"In the quiet hours (02:00 to 07:30) such a command is queued for the 09:00 package, unless a lead waits on it: then the CTO pushes the owner (DEC-1157 (1)) and runs it, the owner approving through Remote Control."** DEC-1144 (7) (reviewers' read-only probes) stands. If the quiet-hours hook (DIF O-5) refuses such a call, its change is an ACT.
  - (18) **Changed: defects in closed tickets (row B18), standing.** DEC-1088 (6)'s "a closed ticket is never edited; any bug fix, new spec or upgrade to its work is a new ticket" now reads: **"a closed ticket is never edited, except that a defect inside its own scope and allowed paths is reopened and fixed by the CTO (a P2, listed for the owner's reading, landed on a narrow independent check, DEC-1154); any new spec, new scope or upgrade is a new ticket, the owner's (DEC-974, DEC-1142 (8))."**
  - (19) **Changed: the queue's order (row B19), standing.** DEC-989 (2) is kept (merge and close one step, through the queue); added: **the merge queue takes a ticket on EXAMIN's critical path ahead of the others** (as DEC-1157 (8) does for starts).
  - (20) **The 09:30 runs sweep (row A4's open half).** The crontab's `runs_sweep.sh` line, commented out by ACT-SCHEDULE-STOP-2 under DEC-1051 (4) and DEC-1050 (5) (both superseded by DEC-1158 (1)), returns by a crontab ACT (class (b)) built, rehearsed and reviewed for the owner's yes line; if the owner says no, the line stays commented with this item as its recorded reason (DEC-866 (3)).
  - (21) **The owner's prompt edit** (`governance/project/prompts/w2-orchestrator.md`, the owner's alone, prompt line 7), made by the owner's operator in one commit (`Role: owner`, `Decided-by: owner (chat, 2026-11-13)`, `Implements: DEC-1158, DEC-1164`): the eight rows B7 (DEC-942 items 1, 4, 5), B8 (the verify and rebuild locks, DEC-904/905, DEC-939 (2), DEC-929 (2)), B10 (close windows and the pre-close gate, DEC-780, DEC-868, DEC-896 (4)), B11 (night P1s, DEC-949, DEC-1021), B12 (the red-nightly hold, DEC-951 A), B14 (usage, DEC-1115 (4), DEC-847), B15 (§0's emergency bullet, DEC-1158 (4)) and B16 (the spent "until" clauses naming closed W2 tickets), plus the lines (5), (6), (10), (11), (13), (14), (15), (16) and B3 change, word for word as listed in this entry's package (`drafts/dec-1164-dif-supersede.md` §4).
  - (22) **Follow-ons:** the DEC-866 marks in this entry's commit (§2 of the package), with three missed marks corrected: DEC-847's usage limit (changed by DEC-1149 (3)), DEC-949 items 1-2 (changed by DEC-1157 (1)), DEC-1122 (2) (ended by DEC-1126 (2)); DECISIONS-IN-FORCE brought to this entry (its twenty "(the 09:00 sweep: …)" markers replaced) and the spent lines moved to `ARCHIVE-SUPERSEDED.md`; START-NEXT-SESSION's next free id and sweep line; DECIDED-NOT-DONE rows for G9's ACT (14), the runs-sweep ACT (20), the slot re-size (9) and the quiet-hours hook check (17); the DEC-866 (2) sweep of code and briefs by id and value (`heavy_slot.sh`'s slot count, G9 in `opcommon.py`, the lead and helper briefs carrying prompt rule 8's freeze), listed in the next digest.
- **Basis:** the CTO's sweep (DEC-1157 (16)) and DEC-1163 (9) ("The CTO brings the DIF sweep's supersede entry"); questions 2 and 4 of DEC-1052's basis (nothing here lets ordinary work fail open or lose work; each removed hold cost lead-hours or would freeze work). The owner's acceptance, quoted, goes here when given.

**The version table row** (after 0.544):

| 0.545 | 2026-11-13 | Owner (recorded by the orchestrator, DEC-861): DEC-1164 (the DIF sweep decided: DEC-946's priorities and the operator's night sleep superseded; thirteen rules amended; the spent sequencing archived; the prompt's lifted holds removed; DEC-866 marks on 30 entries). Next free id: DEC-1165. |

---

## 2. The DEC-866 marks (in the same commit as the ACCEPTED record)

Each line is appended to the **end of the entry's status line** (the line after its heading). Where the status line already
ends in a `**Changed by:**` list, the text starts with `, `; otherwise with ` · `. Lines at `df9d442e8`.

| Item | Entry (heading) | Status line | Append exactly |
|---|---|---|---|
| (2) | DEC-1052 | 13041 | `, DEC-1164 (2) (the plan bullet and "Tonight" spent; D-11 its own line)` |
| (2) | DEC-1055 | 13076 | ` · **Changed by:** DEC-1164 (2) (its order and (8)-(10) spent: D-4 to D-10 done)` |
| (3) | DEC-1064 | 13157 | ` · **Changed by:** DEC-1164 (3) (item (2)'s hold until W2-127 met; no private embedder stays as DEC-1065)` |
| (4) | DEC-1141 | 14649 | ` · **Superseded by:** DEC-1164 (4) (item (6): the operator runs every hour, ACT-OPERATOR-HOURS-3)` |
| (4) | DEC-1142 | 14670 | ` · **Superseded by:** DEC-1164 (4) (item (5): HOURS-1 and -2's hours, retired by ACT-OPERATOR-HOURS-3)` |
| (4) | DEC-1104 | 14042 | `, DEC-1164 (4) (the operator's hours: every hour, ACT-OPERATOR-HOURS-3)` |
| (4) | DEC-1157 | 14880 | ` · **Changed by:** DEC-1164 (4) (item (2)'s interim operator sleep, spent once ACT-OPERATOR-HOURS-3 is applied)` |
| (5) | DEC-1018 | 12735 | `, DEC-1164 (5) (item 1's no commit and no file: from 03:55, not 03:15)` |
| (6) | DEC-946 | 11710 | ` · **Superseded by:** DEC-1164 (6) (items 1-6, 8, 9; item 7 kept; item 10 done)` |
| (7) | DEC-1086 | 13615 | `, DEC-1164 (7) (D spent: window 4 done, DEC-1089)` |
| (7) | DEC-1087 | 13631 | ` · **Changed by:** DEC-1164 (7) ((1)-(11) spent; (13) stays)` |
| (7) | DEC-1097 | 13867 | ` · **Changed by:** DEC-1164 (7) ((1)(g)'s and (9)'s holds for the 80 spent)` |
| (7) | DEC-1098 | 13922 | ` · **Changed by:** DEC-1164 (7) ((6) spent at the lift)` |
| (7) | DEC-1115 | 14197 | `; item (4) spent at the lift, DEC-1164 (7)` |
| (7), (22) | DEC-1122 | 14321 | ` · **Changed by:** DEC-1126 (2) ((2): usage (A) ended at the lift; marked by DEC-1164 (22)), DEC-1164 (7) ((3) spent: D-10 done)` |
| (8) | DEC-1039 | 12923 | `, DEC-1164 (8) (item 1b's "even if that limits leads to two or three" deleted)` |
| (9) | DEC-1038 | 12911 | `, DEC-1164 (9) (item 4's last sentence: slots from the machine, re-sized from the wait log)` |
| (9) | DEC-979 | 12299 | `, DEC-1164 (9) (D1's slots re-sized from the wait log; a starved slot released by the CTO)` |
| (10) | DEC-1057 | 13094 | ` · **Changed by:** DEC-1164 (10) (item (5): scoped tests permanently, no full run per settings ACT)` |
| (10) | DEC-925 | 11070 | `, DEC-1164 (10) (item 2's full run after D-10)` |
| (11) | DEC-1058 | 13103 | ` · **Changed by:** DEC-1164 (11) ((b)'s quiet hours: a (b) ACT a lead waits on, the yes recorded)` |
| (12) | DEC-1053 | 13058 | ` · **Changed by:** DEC-1164 (12) (item (6): the CTO disposes of the branches now)` |
| (13) | DEC-1067 | 13180 | `, DEC-1164 (13) (GPU safety: a measure and a rebuild never use the GPU at the same time)` |
| (14) | DEC-1028 | 12816 | `, DEC-1164 (14) (item 6: G9 holds only an ACT whose paths overlap)` |
| (15) | DEC-902 | 10434 | ` · **Changed by:** DEC-1164 (15) (item 1: the sweep at any time)` |
| (17) | DEC-991 | 12446 | `, DEC-1164 (17) (item 3: a call a lead waits on runs at any hour after a push)` |
| (18) | DEC-1088 | 13690 | `, DEC-1164 (18) (item (6): a defect inside a closed ticket's own scope reopened by the CTO)` |
| (19) | DEC-989 | 12425 | `; DEC-1164 (19) (item 2: a critical-path ticket lands first)` |
| (22) | DEC-847 | 9226 | ` · **Changed by:** DEC-1149 (3) (the usage-limit bullet: usage never holds a lead; marked by DEC-1164 (22))` |
| (22) | DEC-949 | 11786 | `, DEC-1157 (1) (items 1-2: a decision that stops or delays a lead goes at any hour; marked by DEC-1164 (22))` |

That is 30 rows on 30 entries (DEC-1122 carries two marks in one row). No mark is needed for DEC-780, DEC-868 or DEC-929
(each already reads "Lifted by: DEC-953"), DEC-942 (4), (5) (DEC-961), DEC-939 (2) (DEC-1001), DEC-905 (DEC-962), DEC-951 A
(DEC-953), DEC-1132 (DEC-1159), DEC-1140 (`84cc42343`), DEC-1021 (DEC-1157 (1)), or the DEC-1158 set (all present).
DEC-1144 (7) and DEC-1011 are named but not changed.

---

## 3. DECISIONS-IN-FORCE lines to change (at `fb96ea563`)

### 3a. Replacements (old text exact; line numbers at `fb96ea563`)

**Line 4 (header):**
```dif-old
and to DEC-1159 on 2026-11-13 (DEC-1158 (4): the emergency of 2026-11-02 lifted, its section moved to "Lifted"; DEC-1157's and DEC-1159's changes marked; register v0.540; items the CTO's sweep `drafts/dif-sweep-20261113.md` only recommends are marked, not removed).
```
```dif-new
to DEC-1159 on 2026-11-13 (DEC-1158 (4): the emergency of 2026-11-02 lifted, its section moved to "Lifted"; DEC-1157's and DEC-1159's changes marked; register v0.540), and to DEC-1164 on 2026-11-13 (the sweep `drafts/dif-sweep-20261113.md` decided: its markers replaced by the decided words; register v0.545).
```

**Line 29 (row B4, item (5)):**
```dif-old
the GPU budget and no spill (DEC-1039 (1b), DEC-1158 (3)); the nightly in its capped unit beside the leads (DEC-1159 (1)).
```
```dif-new
the GPU budget and no spill (DEC-1039 (1b), DEC-1158 (3)); the nightly in its capped unit beside the leads (DEC-1159 (1)),
  the CTO making no commit on `w2/integrate` and leaving the main tree clean from 03:55 until it starts (DEC-1018 (1) as
  changed by DEC-1164 (5)).
```

**Line 42 (row B17, item (17)):**
```dif-old
quiet hours, DEC-1144 (7)). The quiet-hours ban on a call a lead waits on: (the 09:00 sweep: recommended to amend)
```
```dif-new
quiet hours, DEC-1144 (7)). A call a lead waits on is not queued: the CTO pushes the owner and runs it at any hour
  (DEC-1164 (17), DEC-1157 (1)).
```

**Lines 47-48 (row B18, item (18)):**
```dif-old
  within a ticket's own purpose are the CTO's, listed for the owner's reading (DEC-1157 (12)). A defect inside a
  closed ticket's scope reopened by the CTO (DEC-1088 (6)): (the 09:00 sweep: recommended to amend)
```
```dif-new
  within a ticket's own purpose are the CTO's, listed for the owner's reading (DEC-1157 (12)). A defect inside a
  closed ticket's own scope and paths is reopened and fixed by the CTO, a P2 listed, landed on a narrow check
  (DEC-1088 (6) as changed by DEC-1164 (18)); new scope is a new ticket, the owner's.
```

**Lines 54-58 (row A12, item (10)):**
```dif-old
  `.claude/` settings and hooks; exact commands, check and undo (DEC-925 (2)). No ACT for records. Until D-10, a
  settings change runs its own scoped tests on a clone, not the full suite (owner, D-3 answer 5). **Every ACT is
```
```dif-new
  `.claude/` settings and hooks; exact commands, check and undo (DEC-925 (2)). No ACT for records. A settings change
  runs its own scoped tests and the DEC-866 sweep on a clone, never the full suite, which runs only in the nightly
  (DEC-1057 (5), DEC-925 (2), as changed by DEC-1164 (10)). **Every ACT is
```
```dif-old
  over; its stated counts are the rehearsal's (owner, standing, 2026-11-03).** After D-10, a full run per settings ACT
  (DEC-1057 (5), DEC-925 (2)): (the 09:00 sweep: recommended to amend)
```
```dif-new
  over; its stated counts are the rehearsal's (owner, standing, 2026-11-03).**
```

**Lines 63-64 (row A13, item (11)):**
```dif-old
  Never the CTO's: `sudo`, `git push`, installs, irreversible deletion, secrets, its own permissions, quiet hours.
  (b) in the quiet hours once a lead waits and the owner's yes is recorded: (the 09:00 sweep: recommended to amend)
```
```dif-new
  Never the CTO's: `sudo`, `git push`, installs, irreversible deletion, secrets, its own permissions; in the quiet
  hours only an emergency's rollback or a (b) ACT a lead waits on, once the owner's yes is recorded (DEC-1164 (11)).
```

**Lines 65-66 (row B2, item (14)):**
```dif-old
- DEC-1028 (6), scoped by O-6: while an ACT is applied, no commit touches its paths (`log/act-in-progress.txt`). G9
  holding every queued ACT on that file: (the 09:00 sweep: recommended to amend)
```
```dif-new
- DEC-1028 (6), scoped by O-6: while an ACT is applied, no commit touches its paths (`log/act-in-progress.txt`); the
  operator's G9 holds only a queued ACT whose paths overlap that file's (DEC-1164 (14); G9's change by its own ACT,
  class (O); until then a by-hand ACT holds the queue with an empty `land.txt`).
```

**Line 70 (rows A11, B20, item (9)):**
```dif-old
  (each wait logged, DEC-1157 (13)). The fixed three slots and "only the owner may override": (the 09:00 sweep: recommended to amend)
```
```dif-new
  (each wait logged, DEC-1157 (13)); the slot count from the machine, re-sized by the CTO within the week from the wait
  log and the load; a slot held with no heavy work while jobs wait released by the CTO, a P2 (DEC-1164 (9)).
```

**Lines 71-72 (row A10, item (8)):**
```dif-old
- DEC-1039 (1b), (6), DEC-1037 (4), (5), O-A1, O-10 (DEC-1039 (1b)'s CPU term removed by DEC-1157 (5); its GPU budget
  and no-spill kept and its "two or three leads" obsolete, DEC-1158 (3)): admission by the Load Balancer's forecast (`gate_check.py`
```
```dif-new
- DEC-1039 (1b), (6), DEC-1037 (4), (5), O-A1, O-10 (DEC-1039 (1b)'s CPU term removed by DEC-1157 (5); its GPU budget
  and no-spill kept; its "two or three leads" deleted, DEC-1158 (3), DEC-1164 (8)): admission by the Load Balancer's forecast (`gate_check.py`
```

**Lines 83-84 (row A15, item (3)):**
```dif-old
  DEC-1064: sandboxed workers run no `gov retrieve` and no real-model test until then (W2-127 closed; DEC-1114 holds): (the 09:00 sweep: recommended to supersede)
```
```dif-new
  Sandboxed workers search unranked, named and counted (DEC-1114 (3)); DEC-1064 (2)'s hold until W2-127 met (DEC-1164 (3)).
```

**After line 92 (row B9, item (15); DEC-902 had no line, so by R-9 it did not exist for a fresh session), add:**
```dif-new
- DEC-902 (1) (standing; changed by DEC-1164 (15)): the sweep (`.gov-runtime/scratch/orchestrator/tools/sweep.py`)
  weekly (Monday) and whenever the disk gate nears its floor, at any time; never anything modified in the last 24 hours,
  held open (`lsof`) or cited as evidence, a live session's or daemon's folder, `~/.cache`, a ticket in progress's
  `~/gov-os-runs/` folder, the record worktree, EXAMIN's copy or the workbench. The 09:30 runs sweep back in the crontab
  by its ACT (DEC-1164 (20)).
```

**Lines 103-104 (row B19, item (19)):**
```dif-old
  Lands in batches of two or three tickets with disjoint paths; no commit freeze during lands (DEC-1157 (4), (7)). A
  critical-path ticket landing first: (the 09:00 sweep: recommended to amend)
```
```dif-new
  Lands in batches of two or three tickets with disjoint paths; no commit freeze during lands (DEC-1157 (4), (7)); a
  ticket on EXAMIN's critical path lands first (DEC-989 (2) as changed by DEC-1164 (19)).
```

**Line 123 (row A14, item (12)):**
```dif-old
- DEC-1053: D-0 done; `w2/W2-78` and the in-flight branches with unmerged work wait for D-9. (the 09:00 sweep: recommended to amend)
```
```dif-new
- DEC-1053 (changed by DEC-1164 (12)): D-0 done; the CTO disposes of `w2/W2-78` and each in-flight branch with unmerged
  work now (a P2, listed); one whose disposal could lose work goes to the owner first.
```

**Lines 124-126 (row A7, item (2)):**
```dif-old
- DEC-1052, DEC-1055: the plan (`packages/LIFT-1/P1-PLAN.md`): G-14, D-3, D-4 beside D-4b (memory, as refactoring
  work, no leads; D-4 two heavy slots, D-4b one and the rebuild lock), the final memory measure, re-pin window 3 and
  the integration store, D-5 to D-9, D-10, the lift. No run the old way. D-4 to D-10 done; D-11 (the weekly basis review) not started: (the 09:00 sweep: recommended to supersede)
```
```dif-new
- D-11 (DEC-1052's basis, trigger 3; DEC-1164 (2)): weekly, a basis review of everything in force with each item's
  measured cost; the lift-or-remove list to the owner first; the sweep of 2026-11-13 was its first run. (The plan's
  D-4 to D-10 and the lift are done: DEC-1052's plan bullet and DEC-1055's order spent.)
```

**Line 180 (row A16, item (13)):**
```dif-old
GPU safety for experiments (the 15.5 GB backstop; no measure or
  rebuild beside one; the GPU back in budget between); no install until the owner decides the bigger models. GPU safety's "no measure or rebuild beside one" (with prompt rule 8's commit freeze): (the 09:00 sweep: recommended to amend)
```
```dif-new
GPU safety for experiments (the 15.5 GB backstop; a measure and a
  rebuild never use the GPU at the same time; the GPU back in budget between; no commit freeze during a measure,
  DEC-1164 (13)); no install until the owner decides the bigger models.
```

**Lines 288-292 (DEC-1086; row B26, item (7)): delete the whole bullet** (from `- DEC-1086 (2026-11-06; its C's cap changed by DEC-1091 (1): no cap)` to `(the 09:00 sweep: recommended to supersede)`); it moves to the archive (3b). Its A and B are ticket records (W2-32 S11, W2-135).

**Lines 293-306 (DEC-1087; row B26, item (7)): replace the whole bullet** (from `- DEC-1087 (2026-11-06): before re-pin window 4, all done and tested:` to `The spent "before re-pin window 4" list: (the 09:00 sweep: recommended to supersede)`) with:
```dif-new
- DEC-1087 (13) (2026-11-06): the three layers (the CTO as master, a Senior Engineer per stream, its leads and agents)
  stay in Wave 2 (DEC-1156 (3)); its (1)-(11), the items before re-pin window 4 and the experiments' order, are spent
  (DEC-1164 (7)). Basis: 1.
```

**Lines 319-320 (DEC-1088; row B18):**
```dif-old
  with the decision that made it, and `gov links` flags a change without one. Basis: 2. The standing "a closed ticket
  is never edited" for a defect inside its own scope: (the 09:00 sweep: recommended to amend)
```
```dif-new
  with the decision that made it, and `gov links` flags a change without one; a defect inside a closed ticket's own
  scope and paths is reopened and fixed by the CTO (DEC-1164 (18)). Basis: 2.
```

**Line 347 (DEC-1093; kept, item (1)):**
```dif-old
  Basis: 2. The spent W2-139/W2-140 sequencing: (the 09:00 sweep: recommended to supersede)
```
```dif-new
  Basis: 2. (W2-139 and W2-140 are still open, so their close form stands: DEC-1164 (1).)
```

**Lines 379-380 (DEC-1097; items (7), (13)):**
```dif-old
  with its commit when done. Basis: 1 and 2. The spent "W2-139 and W2-140 held": (the 09:00 sweep: recommended to
  supersede); "no commit … during the run" as carried by prompt rule 8: (the 09:00 sweep: recommended to amend)
```
```dif-new
  with its commit when done. Basis: 1 and 2. (Its holds for the 80's run, on commits, rebuilds, GPU windows and W2-139
  and W2-140, spent with the 80: DEC-1164 (7); prompt rule 8's general freeze removed: DEC-1164 (13).)
```

**Lines 389-391 (DEC-1098; item (7)):**
```dif-old
  first). ADR-0002 accepted, re-read at the lift's re-pin. The work in order: item 8, Q07/Q14, W2-139/W2-140, the
  sitting, D-5 and D-6 part 2, D-10 on the owner's word, the lift. Basis: 1, 2 and 4. The spent "the work in order":
  (the 09:00 sweep: recommended to supersede)
```
```dif-new
  first). ADR-0002 accepted, re-read at the lift's re-pin. Basis: 1, 2 and 4. (Its (6), the work in order to the lift,
  spent: DEC-1164 (7).)
```

**Lines 485-487 (DEC-1115; item (7)):**
```dif-old
  `yes ACT-<id> <manifest sha8>` on its own line); TPL-6's Appendix A applied now. **Standing until the lift: past 80 %
  of the week's usage, only the lift's critical path runs; the rest waits for the reset.** Basis: 2 and 4. (Its (4)
  changed by DEC-1149 (3): usage never stops a lead or a worker.) The spent (4): (the 09:00 sweep: recommended to supersede)
```
```dif-new
  `yes ACT-<id> <manifest sha8>` on its own line); TPL-6's Appendix A applied now. Basis: 2 and 4. (Its (4) spent at
  the lift, DEC-1164 (7); usage never stops a lead or a worker, DEC-1149 (3).)
```

**Lines 537-540 (DEC-1122; item (7)):**
```dif-old
- DEC-1122 (2026-11-10): the ticket template 1.0.1 approved (`bbfc068e58e2`); **usage (A) from now until the reset
  11-15 09:00: only the lift's critical path runs** (DEC-1115 (4) brought forward; **(A) ended at the lift, DEC-1126 (2)**); D-10 goes once ACT-PATHMAP-NS-2 is
  committed and gov check is green, the triage of the first run's reds to the owner; a fresh CTO session at the next
  quiet point. Basis: 1 and 2. The spent usage (A) and D-10 go: (the 09:00 sweep: recommended to supersede)
```
```dif-new
- DEC-1122 (2026-11-10): the ticket template 1.0.1 approved (`bbfc068e58e2`); its usage (A) ended at the lift (DEC-1126
  (2)) and its D-10 go spent (DEC-1164 (7)). Basis: 1 and 2.
```

**Lines 617-620 (DEC-1141; row B1, item (4)):**
```dif-old
  read-first line (DEC-1118 (A) replaced entirely; DEC-1140 (4) corrected); hand merges of W2-175 and W2-176 tonight; **the operator
  agent asleep only during the nightly** (by ACT at 08:00; with the night hold gone, DEC-1157 (2): until its crontab ACT
  the operator does not launch from 02:10 to 08:00). Basis: questions 2 and 4. (6), with DEC-1104 (2)'s G9 and
  ACT-OPERATOR-HOURS-1/2: (the 09:00 sweep: recommended to supersede)
```
```dif-new
  read-first line (DEC-1118 (A) replaced entirely; DEC-1140 (4) corrected); hand merges of W2-175 and W2-176 tonight.
  Basis: questions 2 and 4. (Its (6), the operator asleep during the nightly, superseded by DEC-1164 (4): the operator
  runs every hour, ACT-OPERATOR-HOURS-3, DEC-1163 (5).)
```

**Lines 688-689 (DEC-1157's summary line; item (4)):**
```dif-old
  (`night_hold.py` stopped; the operator's cron line still sleeps 02:10-08:00 until its crontab ACT, class (b)); (3) the
```
```dif-new
  (`night_hold.py` stopped; the operator runs every hour by ACT-OPERATOR-HOURS-3, DEC-1164 (4)); (3) the
```

### 3b. Additions

**In "Lifted", after line 168 (the DEC-1159 bullet):**
```dif-new
- DEC-1164 (2026-11-13), the sweep decided: **DEC-946**'s priorities (items 1-6, 8, 9: "finish before you start", the
  order of 10-29, "nothing else starts", staggered launches, the nightly frozen; its item 7 kept); **DEC-1141 (6)** and
  ACT-OPERATOR-HOURS-1/2's night sleep (DEC-1142 (5); G9's two time holds); **DEC-1064 (2)**'s hold until W2-127 (met);
  DEC-1039 (1b)'s "even if that limits leads to two or three"; the prompt's DEC-942 load wait, verify and rebuild locks,
  close windows and pre-close gate, red-nightly hold, night wait for lead-stopping P1s, usage limits and spent "until
  a closed W2 ticket" holds (the owner's prompt edit, DEC-1164 (21)). **Spent:** DEC-1052's plan bullet and DEC-1055's order (D-4 to
  D-10 and the lift done); DEC-1086 D; DEC-1087 (1)-(11); DEC-1097 (1)(g) and (9)'s holds for the 80; DEC-1098 (6);
  DEC-1115 (4); DEC-1122 (3).
```

**At the end (after line 716), the entry's own line:**
```dif-new
- DEC-1164 (2026-11-13, (4), (5), (9)-(19) standing): **the DIF sweep decided** (`drafts/dif-sweep-20261113.md`): DEC-946
  (1-6, 8, 9), DEC-1141 (6), DEC-1142 (5) and DEC-1064 (2)'s hold superseded; the operator runs every hour (HOURS-3);
  no CTO commit from 03:55 until the nightly starts; heavy slots from the machine, re-sized from the wait log, a starved
  slot released by the CTO; settings ACTs on scoped tests only; a (b) ACT a lead waits on at night once the yes is
  recorded; the D-9 branches disposed by the CTO; a measure and a rebuild never share the GPU, no commit freeze during a
  measure; G9 holds only overlapping ACTs; the sweep at any time; packages a lead waits on bypass the cap; a call a lead
  waits on runs at night after a push; a defect in a closed ticket's own scope reopened by the CTO; critical-path
  tickets land first; the runs sweep back by ACT; spent sequencing archived; the prompt's lifted holds removed. Basis:
  the owner's acceptance of the sweep.
```

DEC-1160 to DEC-1163 are also missing from the DIF (it was brought to DEC-1159); that refresh is the CTO's, outside this entry.

### 3c. Beside the DIF

**`ARCHIVE-SUPERSEDED.md`: a new section at its end:**
```dif-new
## D. Spent or superseded after DEC-951 (DEC-1164, 2026-11-13)
- DEC-946 items 1-6, 8, 9: superseded by DEC-1164 (6) (gov plan's order, the critical path first). Item 7 in force; item 10 done.
- DEC-1052's "The plan, updated" and "Tonight"; DEC-1055's order and (8)-(10): spent, D-4 to D-10 and the lift done (DEC-1164 (2)).
- DEC-1064 (2)'s hold until W2-127: met (DEC-1164 (3)).
- DEC-1086: A and B product record (W2-32 S11, W2-135); C changed by DEC-1091; D spent at window 4 (DEC-1089; DEC-1164 (7)).
- DEC-1087 (1)-(11): spent, window 4 and the experiments done (DEC-1164 (7)); (13) in force.
- DEC-1097 (1)(g), (9): the holds for the 80's run, spent (DEC-1164 (7)).
- DEC-1098 (6): the work in order to the lift, spent (DEC-1164 (7)).
- DEC-1115 (4), DEC-1122 (2), (3): usage (A) ended at the lift (DEC-1126 (2)); D-10's go spent (DEC-1164 (7)).
- DEC-1141 (6), DEC-1142 (5): the operator's night sleep, superseded by DEC-1164 (4) (ACT-OPERATOR-HOURS-3).
```

**`START-NEXT-SESSION.md`:** line 6 `**Next free id: DEC-1160.**` becomes `**Next free id: DEC-1165.**`; lines 24-27 (item 2, "The
sweep's recommendations … the owner decided only the emergency's …") become one line: `2. **The sweep is decided** (DEC-1164):
the follow-ons are its item (22) and DECIDED-NOT-DONE's rows.`

---

## 4. The owner's prompt edit (item (21)), `governance/project/prompts/w2-orchestrator.md` at `e93d846a8`

For the owner's operator, one commit. "Replace exactly" means the old text occurs once in the file. Lines too long to quote
are given by their first and last words and the sha256 of the whole line.

### The eight rows

**P0, the version line (line 1), at its end:**
```prompt-old
O-5, O-6, O-11 (D-3): §0 a pointer to DECISIONS-IN-FORCE)
```
```prompt-new
O-5, O-6, O-11 (D-3): §0 a pointer to DECISIONS-IN-FORCE; v3.73: DEC-1158 (4), DEC-1164 (21): the lifted and spent holds removed)
```

**P1, row B15 (DEC-1158 (4); text from `drafts/PROMPT-s0-dec1158.md`), line 52, the whole line:**
```prompt-old
- **The emergency (DEC-1047, DEC-1049, DEC-1051, DEC-1052), until the owner lifts it:** only the plan's steps run (`governance/project/orchestration/packages/LIFT-1/P1-PLAN.md`, its DEC-1052 section first), with in-session agents of their role, scoped test runs through `tools/heavy_slot.sh`, record commits and the restarts on the list's class list. No lead, landing or queue run; nothing scheduled but the dispatcher, with its ready list empty; no nightly and no full suite until the owner's word (D-10); no `gov close`; no gitleaks scan (DEC-1045). Where each stopped item resumes: `.gov-runtime/scratch/orchestrator/log/emergency-stops-20261102.md`.
```
```prompt-new
- **The emergency of 2026-11-02 is lifted (DEC-1158, 2026-11-13):** DEC-1032's freeze, DEC-1033 (1) and (4), DEC-1047 (1) and (2), DEC-1049, DEC-1050 (5) and DEC-1051 are superseded; leads, landings, the queue, closes, the nightly (beside the leads, DEC-1159 (1)) and the full suite run as DECISIONS-IN-FORCE states. What still holds or delays work is only what protects the machine and the governance (DEC-1157 (14)): the memory floor, the 5 GB hold, `mem_guard` and the OOM trip; the guard's refusals; the spend brake; the brief checks; review rounds, the kernel gate and the owner's approval of kernel bytes; new tickets and splits to the owner; the idle check's record. The gitleaks scan stays off by configuration (DEC-1045) until the owner decides otherwise.
```

**P2, row B7 (DEC-942 items 1, 4, 5), inside line 100:**
```prompt-old
If the load stays above the gate for more than 15 minutes, launch nothing new until it falls; never stop a running lead for load. **Closes first (DEC-942 item 4):** while a ticket is ready to close (`CLOSE-PENDING`), launch no new lead until its close (or batch) has started; running leads continue; the queue takes the verification lock and waits for quiet at most 20 minutes, so it never starves. The locks and windows stay (item 5): one verification run at a time until its trial after W2-67, the close lock, no starts between 00:30 and 05:30.
```
```prompt-new
Never stop a running lead for load: memory admits each start and heavy steps wait for a heavy-job slot (DEC-979, DEC-1157 (5), (8)); DEC-942's load wait, close-first hold, locks and 00:30-05:30 window have ended (DEC-961, DEC-1164 (21)).
```

**P3, row B8 (the verify and rebuild locks, DEC-904/905, DEC-939 (2)), line 341, the whole line:**
```prompt-old
  - **One store rebuild at a time (owner, standing, DEC-939 item 2, until W2-76 lands):** every rebuild runs under `flock /tmp/gov-os-rebuild.lock`: yours, the leads' and the nightly's. Yours runs through `tools/rebuild_diag.sh`, which samples it per stage. A rebuild that passes 30 minutes is flagged in the next package.
```
```prompt-new
  - **Rebuilds (DEC-1001 (d), ending DEC-939 item 2):** a rebuild takes a heavy-job slot like a test run; each tree has its own rebuild lock, and the nightly takes the heavy slots and its rebuild lock itself (DEC-1159 (1)). Yours runs through `tools/rebuild_diag.sh`, which samples it per stage. A rebuild that passes 30 minutes is flagged in the next package.
```
inside line 344:
```prompt-old
The lock stays until W2-67 lands, then the resource gate decides (DEC-906 item 3), and a session's `TMPDIR` stays short (at most `/tmp/gov-os-lead-<W2 id>`), so the launcher's sandbox can make its sockets. What follows is the record of the bridge:
```
```prompt-new
The verification lock has ended (W2-67 closed; DEC-906 item 3, DEC-962): the resource gate and the heavy-job slots decide, and a session's `TMPDIR` stays short (at most `/tmp/gov-os-lead-<W2 id>`), so the launcher's sandbox can make its sockets. Kept from the bridge:
```
and delete lines 345, 346 and 348 (line 347, the lead temp-folder clean-up, stays):
```prompt-old
  - **The cap:** 6,000,000 files and folders and 60 GB per verification run (a lead's full run, the nightly run, a trial). The disk floor still holds across all sessions.
  - **One verification run at a time:** each takes `flock /tmp/gov-os-verify.lock` around its full run and waits while another holds it.
```
```prompt-old
  - **The trial** (`-o tmp_path_retention_policy=failed`, measured: peak inodes and size, time, results unchanged, a failing test's folder kept) runs under the same lock. If it holds, the option becomes the default for the close, the nightly run and the leads.
```
(DEC-929 (2)'s record-commit wait while a queue runs is inside line 361, removed by P4.)

**P4, row B10 (close windows and the pre-close gate, DEC-780, DEC-868, DEC-896 (4); lifted by DEC-953), line 83:**
```prompt-old
  - **never during a close's quiet window** (DEC-780); one writing worker per worktree;
```
```prompt-new
  - one writing worker per worktree (close windows lifted, DEC-953);
```
inside line 338:
```prompt-old
not bundled; never during a close queue or a close's quiet window.
```
```prompt-new
not bundled; never during a close queue.
```
line 360, the whole line:
```prompt-old
- **Closes (DEC-780, DEC-867; DEC-883, DEC-884).** Until W2-66 lands, the queue runs as today, one close at a time; the re-pin waits for DEC-884's ladder. A close runs in a quiet window. First write a fresh `gov checkpoint --ticket <id>` record for the ticket being closed (the close refuses a stale one: `CHECKPOINT_STALE`) and your own checkpoint, then rebuild immediately before the close, with no commit between (a commit makes the store stale).
```
```prompt-new
- **Closes (DEC-953, DEC-989, DEC-1132 (1)).** A ticket merges and closes in one step through the merge queue (`tools/land.py`), or closes by DEC-953's practice (`tk close` and a close record). The close windows, the per-close checkpoint and rebuild, the pre-close gate (a) to (h), `close_queue.sh`'s gates (the secrets check's chance red, DEC-897, and the interim skip guard, DEC-899 item 7, among them) and the record-commit wait while a queue runs (DEC-929 item 2) are lifted on this repository (DECISIONS-IN-FORCE, "Lifted"); they stay built and tested in the product.
```
line 361: **delete the whole line**, the bullet that begins `- **The pre-close gate (owner, standing, DEC-868), until W2-07 builds it into \`gov close\`:**` and ends `is never committed as a clean close.` (3,357 characters; sha256 of the line `6fb1d6f5741c1a3c…`).

**P5, row B11 (night P1s, DEC-949, DEC-1021; changed by DEC-1157 (1)), inside line 230:**
```prompt-old
is sent at once as a package (`packages/<id>.md`, six parts) with a ping, between 07:30 and 02:00 (DEC-1021); from 02:00 to 07:30 it waits for the morning package.
```
```prompt-new
is sent at once as a package (`packages/<id>.md`, six parts) with a ping. Every decision that stops or delays a lead goes at once, at any hour (DEC-1157 (1)); any other blocking P1 goes between 07:30 and 02:00 (DEC-1021) and from 02:00 to 07:30 waits for the morning package.
```
inside line 215:
```prompt-old
From the end of the owner's day to 07:30, nothing pings.
```
```prompt-new
From the end of the owner's day to 07:30, nothing pings but a decision that stops or delays a lead (DEC-1157 (1)) and an emergency.
```

**P6, row B12 (the red-nightly hold, DEC-951 A; ended by DEC-953), line 222, the whole line:**
```prompt-old
  - **Hold only what an item blocks:** a red nightly holds all closes until the owner answers, unless (owner, standing, DEC-951 A) its cause is found, repaired, merged and verified in the main tree (the repaired tests pass, nothing else red): then release the closes yourself and report it in the package as a delegated decision; hold for the owner only a red that is unexplained, unrepaired, or in the judge's own core; a ticket whose close was refused waits; everything else keeps running.
```
```prompt-new
  - **Hold only what an item blocks:** a red nightly holds no close (the red-nightly hold ended, DEC-953); a ticket whose close was refused waits; everything else keeps running.
```

**P7, row B14 (usage, DEC-1115 (4), DEC-847; DEC-1149 (3)), lines 26-28:**
```prompt-old
6. **Spend:** usage recorded only, never an alarm; no budget cap; a runaway brake at twice each projection (DEC-1089 (3),
   DEC-1091). **Before the lift, if the week's usage passes 80 %, the lift's critical path comes first and work outside
   it waits for the weekly reset (DEC-1115 (4)).**
```
```prompt-new
6. **Spend:** usage recorded only, never an alarm; no budget cap; a runaway brake at twice each projection (DEC-1089 (3),
   DEC-1091). **Usage never holds a lead or a worker (DEC-1149 (3)); the runaway brake stays a stop.**
```
line 82:
```prompt-old
  - **the owner's usage limits:** keep the pace sustainable for the week; the daily digest says how much of the daily and weekly allowance is used (`~/.local/bin/claude -p "/usage"`);
```
```prompt-new
  - **usage:** never a limit (DEC-1149 (3)); the digests say how much of the daily and weekly allowance is used (`~/.local/bin/claude -p "/usage"`);
```
inside line 228:
```prompt-old
and whether the owner's plan's usage limits are close; ping the owner before they are.
```
```prompt-new
and the week's usage, a report only (DEC-1149 (3); the 99 % push stays a report, DEC-1140 (6)).
```

**P8, row B16 (the spent "until" clauses naming closed tickets; W2-21, W2-50, W2-66, W2-67, W2-76 closed; W2-67 and W2-76 are in P2 and P3), line 74, the whole line:**
```prompt-old
- **The durable scratch root (DEC-728).** Until W2-50 closes, neither the guard nor the launcher's sandbox lets a session write in ~/gov-os-runs, so no ticket that clones there starts before W2-50 closes (W2-14, W2-15a, W2-15b, W2-24, W2-27). W2-26 alone runs before it, with its throwaway clone in a folder of its own under /tmp, by literal path (/tmp/gov-os-W2-26/examin/), and its results committed to docs/research/EXP-003/examin/. After W2-50, a session writes only under ~/gov-os-runs/<its own ticket>/; another ticket's folder and the root itself stay refused.
```
```prompt-new
- **The durable scratch root (DEC-728).** A session writes only under ~/gov-os-runs/<its own ticket>/; another ticket's folder and the root itself stay refused (W2-50 closed).
```
inside line 85 (delete; the line keeps its two leading spaces and goes on with `**Every countdown reports`):
```prompt-old
Until the path-scoped close (W2-66) lands, prefer fewer leads, so finished tickets don't pile up behind serial closes (DEC-880; W2-48's cache was withdrawn); after it lands, raise parallelism as far as the gate and the limits allow. 
```
line 144, the whole line:
```prompt-old
- **Until W2-21 closes, every lead starts in the owner's launch form (DEC-715), exactly:**
```
```prompt-new
- **A lead started by hand uses the owner's launch form (DEC-715), exactly** (W2-21 is closed; the dispatcher starts leads from `dispatch/ready.txt` through `launch_now.sh`, DEC-1007, DEC-1161 (2)):
```
optional, beyond the sweep's named list (W2-56 closed on 11-13 at 07:27, after the sweep was written), inside line 149:
```prompt-old
the others start in the old form above with their own role in --settings, and with DEC-789's tripwire around them, until W2-56 closes.
```
```prompt-new
the others, until their suites run in the sandbox, start in the old form above with their own role in --settings and DEC-789's tripwire around them (W2-56 is closed: its S13 runs the code-graph suites inside the sandbox).
```

### The lines that follow the register items (same commit)

**Item (5) and row B3 (DEC-1018 (1), DEC-1159 (1)), inside line 339:**
```prompt-old
(the dispatcher holds landings from 03:15 until it starts, DEC-1018; no close or merge in progress, the main tree clean, `w2/integrate`'s head stable)
```
```prompt-new
(beside the leads, DEC-1159 (1), with no landing hold, DEC-1157 (2): no landing, close or queue run in progress, the main tree clean and `w2/integrate`'s head at least 5 minutes old; the CTO makes no commit from 03:55 until it starts, DEC-1018 (1) as changed by DEC-1164 (5))
```
inside line 342:
```prompt-old
every night, in a quiet window and never during a close,
```
```prompt-new
every night, beside the leads (DEC-1159 (1)) and never during a close,
```

**Item (6) (DEC-946), lines 86-92, the whole bullet** (lines 86-91 as quoted; line 92 begins `  **Nothing else starts.**` and
ends `unless it breaks.`, 475 characters, sha256 `70e56280d3bff98d…`):
```prompt-old
- **Standing priorities until EXAMIN's copy starts (owner, DEC-946; they order everything below):**
  1. finish before you start: closing merged or built work comes before starting a new ticket (W2-57, W2-67, W2-71, the held merge-backs);
  2. speed: W2-77, then the batch switched on and measured; W2-78; W2-76;
  3. memory, the critical path: W2-61's baseline, then W2-03, W2-55, W2-64, W2-04, W2-05 and W2-06, W2-13, W2-15a, with the measure repeated after each;
  4. K3 and K6 in parallel: W2-60a and W2-60b, W2-56, W2-21, W2-20;
  5. the rest of EXAMIN's minimum: W2-81, W2-82 (light), W2-83a.
```
```prompt-new
- **Order (DEC-1088, DEC-1110 (3), DEC-1157 (8); DEC-946's priorities superseded by DEC-1164 (6)):** leads start from `dispatch/ready.txt` in `gov plan`'s order, a ticket on EXAMIN's critical path first and never waiting. A new ticket or split is filed only on the owner's decision (DEC-974, DEC-1142 (8)); an idea not filed goes to `docs/plan/WAVE_3_PARKING.md`. If 18 November is at risk, bring what to cut, not a later date (DEC-946 item 7).
```

**Item (10) (DEC-1057 (5), DEC-925 (2)), inside line 163:**
```prompt-old
- **Settings changes (owner, standing, DEC-925 item 2; until D-10, owner D-3 answer 5).**
```
```prompt-new
- **Settings changes (owner, standing, DEC-925 item 2, DEC-1057 (5), as changed by DEC-1164 (10)).**
```
```prompt-old
and sweep for every test that depends on what changes (DEC-866); after D-10, a full run in the close's form on a clone. Report both in the ACT.
```
```prompt-new
and sweep for every test that depends on what changes (DEC-866); the full suite runs only in the nightly (DEC-968), never per settings change. Report both in the ACT.
```

**Item (13) (rule 8), lines 32-33:**
```prompt-old
   `wait_for.sh` on an exit file; never the Monitor tool, which asks the owner each time, and never a name match); no
   commit on `w2/integrate` during a GPU measure or a hold. Every helper's brief says so.
```
```prompt-new
   `wait_for.sh` on an exit file; never the Monitor tool, which asks the owner each time, and never a name match); a
   measure and a store rebuild never use the GPU at the same time (DEC-1067, DEC-1164 (13)). Every helper's brief says so.
```

**Item (15) (DEC-902), line 357:**
```prompt-old
  - **Only in a quiet moment:** no lead, close, nightly run or trial running.
```
```prompt-new
  - **At any time** (DEC-1164 (15)): the "never" list below protects running work.
```

**Item (16) (row B13), inside line 207:**
```prompt-old
At most five packages at a time; a P1 may bypass the cap.
```
```prompt-new
At most five packages at a time; a P1, and any package a lead waits on (DEC-1157 (1)), bypasses the cap.
```

**Item (11) (DEC-1058 (b)), inside line 211:**
```prompt-old
never yours: `sudo`, `git push`, installs, irreversible deletion, secrets, your own permissions, the quiet hours;
```
```prompt-new
never yours: `sudo`, `git push`, installs, irreversible deletion, secrets, your own permissions; in the quiet hours only an emergency's rollback or a (b) ACT a lead waits on, once the owner's yes is recorded (DEC-1164 (11));
```

**Item (14) (DEC-1028 (6)), inside line 214:**
```prompt-old
named in `log/act-in-progress.txt` when you hand it over; every other commit goes on.
```
```prompt-new
named in `log/act-in-progress.txt` when you hand it over; every other commit goes on. The operator's G9 holds only a queued ACT whose paths overlap that file's (DEC-1164 (14), once G9's ACT is applied).
```

**Check after the edit (the operator):**
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
grep -c "The emergency of 2026-11-02 is lifted (DEC-1158" governance/project/prompts/w2-orchestrator.md   # expect 1
grep -c "the 09:00 sweep\|until W2-21 closes\|Until W2-50 closes\|no starts between 00:30\|The pre-close gate (owner" governance/project/prompts/w2-orchestrator.md   # expect 0
grep -c "DEC-1164" governance/project/prompts/w2-orchestrator.md   # expect 9 (lines)
git diff --stat   # 1 file changed
```

---

## 5. Not settled here (for the CTO)

1. **Row B4:** the sweep said supersede DEC-1018 (1)'s rest; DEC-1159 (1), decided after the sweep, keeps the nightly waiting
   for a clean main tree and a head 5 minutes old, so (5) amends it to "from 03:55" instead. The owner may prefer supersede.
2. **Row B8:** the sweep proposed dropping `nightly.sh`'s global `flock /tmp/gov-os-rebuild.lock` (now line 134, not 124);
   DEC-1159 (1) decided "nightly.sh takes … the rebuild lock itself", so this entry leaves it. Tonight's nightly waited 1,702 s on
   locks (P1-MORNING): a reviewed nightly commit, if wanted, is a separate package.
3. **Row B26, DEC-1093:** W2-139 and W2-140 are `in_progress` (W2-139 partly merged), so their sequencing is kept, not spent.
4. **Row A4's runs sweep (20):** the sweep left it open; the item proposes its return by ACT. DEC-946 (10) names a 06:15 line,
   DEC-1051 (4) and the crontab a 09:30 line; the ACT should confirm which.
5. **P8's line 144 and line 149:** the new words are the helper's reading of how leads and workers start today
   (`launch_now.sh`, W2-56's S13); the owner may prefer to delete the clauses only.
6. **Lines 5 and 157 of the prompt** ("until W2-11 brings the skill up to date"; the twelve fields "until W2-10 and W2-11
   pass"): both tickets are closed, but each clause sets precedence or a return form, not a hold; left out as outside the sweep.
7. **DEC-1163's place:** it was inserted at register line 722, before "## 12. Change log", not after DEC-1162; DEC-1164 is
   drafted to follow it at the end once moved.
8. **Prompt line 162** ("any owner commit that touches tests is validated with a full run in the close's form before the ACT
   ping", DEC-906) is another full-run rule beside (10); the sweep did not list it, so it is left.
