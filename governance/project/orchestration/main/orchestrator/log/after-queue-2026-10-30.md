# Due as soon as the close queue of 2026-10-30 (W2-03, W2-71, W2-77, W2-57, W2-26) ends — main-tree commits

1. **DEC-952** (owner, 2026-10-30): memory quick wins first, W2-86 (template/ indexed, the indexer honouring the path map) and W2-87 (rank by authority), each re-measured; W2-15a filed; memory not on the cutting list (cuts elsewhere or a later date, with figures); standing: leads' interim key results reported at once in the next status block (interim_watch.sh), and the memory-chain line in every status block (prompt's reporting rule, with DEC-948's block); W2-55 and W2-04 at the front of the lead queue with W2-64, stacked on W2-03.
1b. **DEC-952 also carries the owner's verification decision** (replacing DEC-880 item 2 (b)):
   - leads verify scoped, as a scoped close selects (`tools/scoped_plan.py`); the full suite only for the judge's own core;
   - the nightly is the integration check;
   - closes as one morning batch after a green nightly, citing the nightly's green run once W2-68's reuse is pinned;
   - re-pin 3's ACT the moment W2-71 and W2-77 close;
   - the verification lock for full runs only.

   Commit `drafts/LEAD-w2-common.dec952.md` as the common brief. Prompt §3/§7/§15 lines: the queue no longer holds the verification lock through scoped closes (closes: the lock only for a full close).
1c. **W2-86 is a path-map edit, by the orchestrator** (DEC-388's own fix):
   - the vendored paths get their own namespace (`not embedded`), and `kernel-template`'s policy becomes exactly `embedded`; `template/.rulesync/**` stays out of the embedding (generated copies);
   - then rebuild and re-measure the visible half with W2-61's measure, reporting both figures;
   - W2-86's and W2-87's ticket drafts are in `drafts/tickets/`; W2-86 as a ticket is unnecessary if the orchestrator makes the line, so say so in DEC-952.
1d. **Rows:**
   - `src/gov/check/pathmap.py` reads `namespaces` as a list, so on this map (a dict) the path-map check checks nothing (fails open);
   - `retrieve.py:52` `record_of` maps all 953 decisions to the register's single path, so every register chunk takes the newest entry's status (W2-87 takes it in);
   - W2-55's paths name `src/gov/retrieve/**`, but its KPI 3 lands in `src/gov/retrieval/retrieve.py`.
1e. **W2-15a is `DAEO-rd0g`,** open since 2026-10-16, so there is nothing to file. The draft body goes into it. Q-2 (the owner's approval of EXP-003's metric) is needed before its first run: a package.
1f. **ACT-TESTMAP-1** is sent (the owner's commit after the queue).
2. **Tickets:** file W2-86, W2-87, W2-15a (drafts from the helper); W2-55 (`DAEO-arrl`) + `template/governance/kernel/schemas/register-entry.schema.json`; W2-04 (`DAEO-u4oz`) + the W2-61 re-measure KPI and DEC-833, DEC-941 in sources.
3. **Claims (dor_hand.py, DEC-944; stacked on W2-03 for W2-55 and W2-04 if W2-03 closed):** W2-86, W2-87, W2-55, W2-04, W2-85; worktrees; briefs (W2-55-part-run1, W2-04-part-run1, W2-86/87-part-run1, W2-85-part-run1 with @@HEAD@@; W2-05-part-run4, W2-60a-part-run2 with their heads).
4. **Lead queue order (DEC-946 + owner 2026-10-30):** W2-86, W2-87, W2-55, W2-04, W2-64, W2-85, W2-05 (run 4), W2-60a (round 3), then W2-78, W2-76, W2-20, W2-81.
5. **Brief-gaps rows** for W2-71 run 3, W2-60a, W2-03, W2-26 returns into `governance/project/orchestration/brief-gaps.md`.
6. **ACT-REPIN-3** (W2-68, W2-71, W2-77) once W2-71 and W2-77 have closed.
7. **Refused close of W2-03:** write `.gov-runtime/scratch/orchestrator/REFUSED-DAEO-ym8a` so W2-55's and W2-04's briefs stop.
00. **Resume W2-84 FIRST** (P-W2-84-HOLD (a), delegated): brief briefs/W2-84-part-run1b.md, @@HEAD@@ = its worktree head; full run (guard = judge core) and FULL review; W2-61h waits on it.
0. **Merge W2-61** (DAEO-iw1f, DONE 10:45, head 6b517db940cf; the measure tool) first; then W2-61h waits for W2-84; the hidden half scored by the orchestrator on /home/usain/gov-os-runs/W2-61/repo (scores only).
9. **DEC-952 also carries the owner's items 5 and 6 (2026-10-30, standing):**
   - **(5) the rules-in-force digest:** `governance/project/orchestration/RULES-IN-FORCE.md` (draft in `drafts/RULES-IN-FORCE.md`; tool `tools/rules_digest.py [out path]`), generated from the register: ACCEPTED, standing, non-superseded, one line each, at most about 8,000 characters (53 rules, 6,558 characters on 2026-10-30). It is regenerated and committed with every register commit.
     - The session-start hook's injection of it is kernel code (`template/governance/kernel/hooks/sessionstart.py`, 10,000-character cap), so it needs a small CIT-P ticket. Ask the owner whether to file it now.
     - Until then, the first line of RESUME HERE names the digest, and the prompt §1 step 2 reads it.
   - **(6) a fresh session each morning:** after the 07:30 package, write the handover (checkpoint, RESUME HERE, the digest current), tell the owner it is ready, and stop; the owner starts a fresh session from it (the prompt §7).
   - **The first handover is today:** when the close queue ends, write the handover, ping ACT-TESTMAP-1 with "handover ready", and stop. The fresh session does this list after the owner's commit.
8. **Resume W2-67** (P-W2-67-HOLD5 (a), delegated: held past 90 min at 11:41): from its checkpoint, merge integrate once more, scoped verification per DEC-952 (likely full: tests/conftest.py is shared core), fresh probe (briefs/rev-4.md in its worktree); a slot that ends before 01:00 or after the nightly.
