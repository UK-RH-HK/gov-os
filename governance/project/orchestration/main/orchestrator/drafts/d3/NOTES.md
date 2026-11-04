# D-3 items 11 and 12: notes on the drafts (product-spec, 2026-11-03)

Files in this folder: `prompt.patch` (a unified diff of `governance/project/prompts/w2-orchestrator.md`, made with
`diff -u` against `w2-orchestrator.edited.md`, 11 hunks; `git apply` gives the edited copy byte for byte),
`DECISIONS-IN-FORCE.md` (it replaces the live list, and `LIFTED-BY-DEC953.md` folds into it), and
`RESTART-CLASSES.md` (the class list proposed for O-6). Nothing outside this folder was written or committed. Base:
the prompt as of `fe68a5faf501`, the list as of `501d445c` (both unchanged at `2ae4e094162c`, with DEC-1055 and
DEC-1056 read in).

## The prompt patch, change by change (row, decision, basis)
| § | change | row / decision | basis |
|---|---|---|---|
| head | v3.72 added to the version line | — | — |
| 0 | 32 KB of per-decision paragraphs replaced by four bullets: the list overrides everything below; the emergency's state (what runs, what does not); the basis; what to read at start | R-9 (DEC-1052) | q4: one list, not 2 to 3 edits per decision; the paragraphs stay in the register |
| 1 (1b) | the heartbeat check and `cto-standby.txt` dropped; Remote Control, the test push and `cto-session.txt` kept (the sentinel watches that file) | O-5 (DEC-1052) | q4: the dispatcher's stale line already watches the sentinel |
| 1 (4) | the checkpoint is committed to `record/w2` hourly and at session end, not at every handover | R-10 (DEC-1052) | q3, q4: every commit moved the integration head |
| 5 | DEC-861's commits: one per batch, hourly or at the handover; the ratchet, history and validation exceptions marked as lifted here | R-10; O-6 (no ACT for records); DEC-953 | q4 |
| 7 | delegated choices: a line in the ticket's file or close record, not a register entry | R-8 (DEC-1050 (9)) | q4 |
| 7 | DEC-957's rubric moved here from §0, with "a class restart is not an ACT" | R-11 ("P1 only by DEC-957's rubric"), O-6 | q1, traffic: the rubric decides who decides |
| 7 | the six-part form only for a P1 that blocks work; the short form (question, options, recommendation) for the rest | R-11 (DEC-1050 (9)) | q4 |
| 7 | a ping only when work waits on the owner; two digests a day (09:00, 18:00); DEC-972's ping form folded in (it was in §0) | R-11 | q4: 21 to 28 pings a day, 24 of 86 gating nothing |
| 7 | ACTs only for machine changes; none for records or class restarts; the commit freeze only on the ACT's own paths | O-6 (DEC-1052), DEC-1028 (6) scoped | q4: 31 ACTs, 8 on 2 Nov; q2: the freeze still guards the paths the ACT changes |
| 7 | the morning package: 09:00 (DEC-973, was only in §0), at most one page, short form for non-blocking items | R-11, DEC-973 | q4 |
| 7 | "one daily document" becomes two digests; "only P1s and ACTs ping" becomes "only what work waits on"; leads' packages in either form | R-11 | q4 |
| 7 | DEC-851's "every place a session reads" narrowed: register plus one line in the list; templates carry a line only where it changes what is done | R-9; DEC-1052 templates (narrowing DEC-851 (1)) | q4 |
| 7 | the two-commit rule for ticket files lifted | R-12 (DEC-1052; DEC-896 (2)) | q4: the gate it fed is lifted (DEC-953) |
| 8 | the stop says "the ping", not `owner-ping` | R-11 | — |
| 10 | `Task:` and `Role:` kept; `Implements:` optional and never against the register | R-12 (DEC-927 (2)) | q4 (and q1: `Task:`/`Role:` stay as G-1's backstop) |
| 12 | "a ping or an `owner-ping`" carries no secret | R-11 | — |
| 15 | the two digests' contents (delegated lines, class restarts); `Implements:` optional; sync hourly; `--main` lifted | R-11, R-8, R-12, R-10, O-6 | q4 |
| A2, A4 | the commit lines: `Implements:` optional | R-12 | q4 |
| A5 | no committed `gov checkpoint` record per round; the prose checkpoint is the record | R-6 (DEC-1052; DEC-511 lifted) | q4: 345 files, 435 commits, read only by lifted gates |
| A5 | a lead's package: six parts only for a blocking P1 | R-11 | q4 |

**O-11 (DEC-1012 and DEC-1003 scoped)** lives only in the list (its "Rules about rules" section). Both rules stood
only in §0, which R-9 removes, so no prompt line remains to change.

**DEC-991's `rm` ask (corrected):** §0's "today: `rm` in any form and `owner-ping` ask" goes with §0. The list's
DEC-991 line now says `rm` is free except for the catastrophic (DEC-1050 (8), ACT-GUARD-FIX-4). The `rm` asks were
removed from `~/.claude/settings.json`.

## The list: what was kept, what left
- **Kept** if it still holds and changes what is done, emergency first (DEC-1047, DEC-1049, DEC-1051, DEC-1052,
  DEC-1053, DEC-1054, with DEC-1055 and DEC-1056, recorded while this was drafted). Any rule the prompt's body states
  correctly is left out, to stay near 8 KB: DEC-820/723 (§2, §12), DEC-962/963/966 (A1), DEC-898/902 (§3, §15),
  DEC-221/096/944 (§3, §6, §9), DEC-720/848/911 (§5, §12, §15), DEC-105 and the delegation rule (§7), DEC-836/859/
  860/838 (§4, §5), DEC-866 (§7). Basis q4 for each.
- **Dropped as spent or superseded** (they stay in the register; consider adding them to `ARCHIVE-SUPERSEDED.md`):
  DEC-955, DEC-975, DEC-971, DEC-953 (5) (the five closes), DEC-954's old order and P-W2-64-1, DEC-946 (6, 8, 9),
  DEC-952's memory order, DEC-983's order, DEC-979's order (item 2 kept), DEC-982's filings, DEC-990 to DEC-993 and
  DEC-997 (delegated), DEC-1018 (the main tree clean for the nightly), DEC-984, DEC-973's nightly times, DEC-934 and
  DEC-938's nightly lines (all under DEC-1049; they come back only with the owner's word), DEC-958 (its harvest and
  thresholds; replaced by DEC-1050 (6) and the basis's symptom trigger), DEC-949's every-item pings (R-11),
  DEC-953's milestones (replaced by DEC-1052's plan), DEC-1032 and DEC-1033 (named under DEC-1047/1051),
  DEC-1037 (1)-(3) (windows done), DEC-1039 (2)-(3b) (replaced by DEC-1052's plan).
- **Folded in:** `LIFTED-BY-DEC953.md` becomes the "Lifted" section (cited at `69a0e5d89f04`). The live change also
  deletes `LIFTED-BY-DEC953.md` (git keeps it). It is still referenced by `docs/plan/WAVE_2_WBS.md`,
  `.tickets/DAEO-03dg.md` and `ARCHIVE-SUPERSEDED.md`: change those three references to point at the list, or keep
  the file as a stub that does.
- **Size:** 8,683 bytes, against "at most about 8 KB"; the live list is 18,437 bytes, plus the lifted file's 7,563.
- **"Approved restarts by class (owner, O-6)":** empty. It points to `RESTART-CLASSES.md`.

## The restart classes
Five classes are proposed: the shared embedder :11434, the query server :11435, the shared reranker service, the
CTO's samplers and slot watcher, and the sentinel. Each comes from the commands already committed in
`MORNING-RESTART-2026-11-03.md`, ACT-OLLAMA-CAP-1 and ACT-QUERY-GPU-2. The dispatcher needs no class: cron runs it,
and its crontab line is an ACT. Basis q4 and q2.

## Not placed, or for the owner to settle
1. **The evening digest's time (18:00)** is the drafter's choice. DEC-1050 (9) says "two digests a day" and names no
   time; the 09:00 morning package is DEC-973's.
2. **Emergencies in the quiet hours:** DEC-973 says "emergencies excepted", but the prompt's §7 (DEC-938) still says
   that at night an emergency pings only at 07:30 unless the owner is active. The patch leaves both lines as they
   are: say which holds.
3. **Restarts before the class list is approved:** START-NEXT-SESSION §1 already reads "restarts of the repository's
   own servers from committed configs" as allowed. The draft list says that until classes are approved, a restart is
   an ACT. The owner's word decides it.
4. **The reranker's start command:** the form with `GOV_RERANK_IDLE_S=43200` is inferred (the service inherits the
   search's environment, `rerank.py` `_start`). The 13:45 start's exact command line is not on record.
5. **O-5 and `cto-standby.txt`:** the committed `deadman.py` still reads that file to stay quiet while the CTO stands
   by on purpose. With the ritual lifted, the sentinel pushes once on a deliberate stand-by longer than its stall
   window, a ping that gates nothing. P1-4 decides whether `deadman.py` drops it or the dispatcher's ready list stands
   in for it. START-NEXT-SESSION §7 step 2 still has the `mv cto-standby.txt` step, and §4 still has the heartbeat
   check, so the next handover needs the same edit.
6. **R-10 is beyond item 11's listed rows.** The plan puts it in P1-4 "(+ prompt)". Its prompt lines (§1 item 4, §5,
   §15) are in this patch so the owner gets one patch; the owner may drop those hunks. `sync_context.py`'s `--main`
   code goes with P1-4.
7. **R-11's "the CTO drafts at `high`"** is in the investigation's row, but DEC-1050 (9) quotes only the pings and the
   digests. It is left out, since DEC-1050 (10) asks for evidence before any cut to the CTO's way of working.
8. **R-9's status in P1-PLAN** still reads "PENDING (lifting the prompt's §0 is a prompt cut: DEC-1050 (10) asks for
   evidence first)". DEC-1052 approved R-9 later, so the plan's line is stale.
9. **DEC-925 item 2's "a settings change runs in full on a clone first"** (prompt §5) needs a full suite, which
   DEC-1049 forbids until D-10. It is not one of these rows: say what replaces it for `.claude/` ACTs, for example the
   guard's scoped tests, as ACT-GUARD-FIX-4 did.
10. **Text the patch leaves alone:** lines elsewhere that still name "the daily digest" (§3, §15's sweep), the
    nightly's §15 paragraphs and §3's gate and launch lines (`gate_check.py`, lifted by O-10). The pointer in §0
    covers them, and D-5's templates replace them.
11. **The placeholder scan** finds 0 hits in the list and the class list. In the patch it finds 73 angle-bracket slots
    (`<id>`, `<W2>`, …): all of them are the prompt's own command slots, present in the original. There is no
    unfilled time or date and no to-do marker. The keyword check (row W2-L423) finds nothing.
12. **Tests:** no test reads the live prompt's or list's content. W2-55's and W2-62's acceptance cases plant their
    own fixtures at those paths. `gov context --in-force` (the RULES-IN-FORCE generator, lifted by R-9) still exists
    in `src/` and is not touched.

## The owner's answers (2026-11-03) and what the CTO changed in the drafts after them
All eight as recommended. In the edited prompt: the stand-by file kept (answer 7, §1 1b); emergencies ping at any hour
(answer 3, §7's two lines); settings changes run their own scoped tests until D-10 (answer 5, §5); the rehearsal rule
(owner, standing) and P-ACT-SPLIT's who-runs-it (§7's ACT line). In the list: the same, the five restart classes
approved, `cto-standby.txt` out of the Lifted section, the D-1/D-4b merges as built, O-3's line. Records to commit with
D-3 when the ACT-G14 hold ends: the register entries for D-3's answers with the rehearsal rule, P-ACT-SPLIT, F4 and
ACT-G14's result; W2-61h's P-W2-61h-2 (a) as a line in its ticket (R-8).
