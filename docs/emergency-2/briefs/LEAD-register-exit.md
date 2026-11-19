# Lead brief: the old register archived and out of memory's index; the kept register in force (W2-203, a new feature)

Read `/home/usain/Dynamic-Agentic-Engineering-OS/docs/emergency-2/briefs/NIGHT-COMMON.md` first and follow it.
Branch `e2/register-exit` from `w2/integrate`, worktree `/home/usain/gov-os-worktrees/E2-register-exit`. **C3** (the path
map): the test designer and the engineer run Claude Fable 5.2 (`model: "fable"`). `Task: DAEO-<your new ticket id>`,
`Class: F`.

**Decided:** EMERGENCY-2 §11.3 ("After audit 8, the old register is archived read-only and excluded from memory's
index") and DEC-1214 G4 (a) (audit 8's classes, landed tonight: every entry from DEC-001 to DEC-1210 carries
`· **Class:** kept | superseded by DEC-n | retired | history` at the end of its status line; merge be38bcaee). Memory's
index must be clean before the first fresh-80 measure (DEC-1214 G1), which waits for this.

**Read:** audit 8 `docs/emergency-2/audits/08-register.md`, the section "Archiving the old register read-only and keeping
it out of memory's index (§11.3)" (where the include rules are, what else reads the register path, the seven steps);
`docs/emergency-2/audits/08-doubtful-settled.md`; the builder the G4 lead wrote, on its branch:
`git show e2/g4-g5:docs/emergency-2/audits/08-new-register.py` (it builds the new register from the classed one: the
kept entries plus DEC-1211 and later; copy it into your branch and make it take every entry from DEC-1211 on, whatever
the last id is: the CTO added DEC-1215 and DEC-1216 tonight and may add more while you work).

**The CTO's decisions on the audit's open points (do not reopen them):**
- Step 5, read-only: **(b)** the header line only. No new refusal rule (EMERGENCY-2 §10.1: no rule without an incident).
- Step 6, citations: **teach the code to read the archive for ids.** A decision id that lives only in the archive still
  resolves, as history: the citations check, `gov links`, `gov closure`, and whatever else resolves a decision id (find
  every caller through the path map's `decision_register` key and the hard-coded paths the audit lists) read the archive
  file for ids and headings only. The archive is never embedded, never in the keyword index, and its entries are not
  store records a search returns. The kept register's entries cite 366 archived ids from 139 entries: after your change
  none of them is a dangling finding.
- The archive's name: `docs/archive/DECISION_REGISTER-2026-11-19.md`. The path map names it under a new key beside
  `decision_register` (for example `decision_register_archive`), so no code hard-codes it.
- The new `docs/DECISION_REGISTER.md`: the kept entries verbatim (ids, headings, status lines with their class), then
  every entry from DEC-1211 on verbatim. New ids continue from the last one. A short head says what the file is, that
  the earlier decisions are in the archive by id, and names audit 8.

**Your feature (write it as a ticket first, wbs_id W2-203, status in_progress, KPI lines each observable with its
verify).** At least:
1. The old register is at the archive path with its first line saying archived and read-only; the path map has a
   namespace for `docs/archive/**` that is not embedded and not indexed (as `evaluation-sources` is); every tracked path
   still sits in exactly one namespace.
2. `docs/DECISION_REGISTER.md` is the kept register; the store loader reads it with no refusal; `gov doctor` lists the
   archive among its historical paths and is no less healthy than on the base.
3. After a rebuild, a search for a decision found only in the archive returns no chunk from `docs/archive/`, and a kept
   decision still resolves (acceptance on a fixture repository; no rebuild of the shared store).
4. An archived id cited from a kept entry, a ticket, a test or a document resolves (no finding from the citations check,
   `gov links` or `gov closure` that the base did not have); an id in neither file is still a finding.
5. Rebuilding the new register from the archive with the builder gives the committed file byte for byte (so the CTO can
   re-run it after a late register entry).
6. Failure lines: a kept entry missing from the new file, or an entry present in both files with different text, fails
   a check by name.

**Tests that read the live register.** Many tests name `docs/DECISION_REGISTER.md` (find them:
`grep -rl DECISION_REGISTER tests`). A test that asserts content now only in the archive (W2-130's marks cases read the
status lines and the git history of "the 87"; others pin single entries) is revised by the independent test designer to
read the archive, with a `Rewrite-Reason` naming EMERGENCY-2 §11.3 and DEC-1214 G4. A test that only needs a register is
left alone. List every file revised, and why, in your return.

**Flow:** test designer (Fable) writes `tests/acceptance/W2-203/` from your KPI lines, red on the base, and the
revisions above; engineer (Fable) builds until `gov accept W2-203` is green; then `tests/unit/store`, `tests/unit/check`,
`tests/unit/doctor`, `tests/unit/links`, `tests/unit/decisions`, `tests/unit/retrieval`, `tests/unit/plan`,
`tests/unit/memaudit`, `tests/acceptance/W2-130`, `W2-129`, `W2-51`, `W1-48`, `W2-49`, and every acceptance folder whose
test you revised. Run them with node on the PATH (`PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH`): without
it `openspec-validate` is red for a reason that is not yours.
**The last step before you return:** `git merge w2/integrate` into your branch, re-run the builder so the new register
holds every entry the integration branch has, commit, and re-run `tests/acceptance/W2-203` and `tests/unit/store`.

Keep out of `src/gov/close/**` (two leads work there tonight: M1 and L2) unless a decision-id lookup lives there; if it
does, make the smallest change and name it in your return. Do not touch `src/gov/memaudit/tables.py`'s live path (the
question writers' "decisions" domain reads the kept register, which is right).
