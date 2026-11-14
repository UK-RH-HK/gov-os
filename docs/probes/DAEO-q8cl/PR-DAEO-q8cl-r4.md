---
type: probe
task: DAEO-q8cl
reviewer_session: cab6a2fc-b250-4845-b936-77559cf905b6
implementer_session: this run's ticket lead (orchestrator, run 4)
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: a2671a340dda6b020e6e16099b51d535a2e408ae
decisions_applied: [DEC-1073, DEC-1010, DEC-1098, DEC-1088, DEC-1123]
---

# Probe record: W2-130 (DAEO-q8cl), run 4's narrow independent check of the record refresh

A fresh independent-auditor session (`cab6a2fc-b250-4845-b936-77559cf905b6`) ran on `claude-opus-5-5` at high effort, class C2, read-only, with
JUDGEMENT.md word for word in its brief. It probed head `a2671a340dda` of `w2/W2-130` and wrote nothing in the tree
(`git status --short` empty at its end; its tripwire's changes are other sessions' trees, W2-100 and W2-100-tests).
What it probed: the ticket lead's one commit of run 4, `a2671a340` (the record
`docs/research/W2-130-link-cleanup.md` refreshed at the merged head `6b62de94e`, the CTO's merge of `w2/integrate`
after the land's conflict on `.tickets/DAEO-aks1.md`). Run 3's record, `PR-DAEO-q8cl.md`, stays beside this one.

Its verdict is **PASS**: four items pass, three findings, none blocking (each in scope, ordinary work yes,
consequence other).

## The lead's judgement of the findings

- **F1** (`counts-before`'s command text now names the tool of `6b62de94e3fd`, not `57cbacfbfc86`; its counts are
  unchanged and the auditor reproduced all eight at `232efc47d` with HEAD's tool). Ordinary work: yes, because one
  builder fills both blocks. Consequence: other (a true wording change; nothing fails open, no work is lost). A row.
- **F2** (the `counts-after` command text says the merges of `w2/integrate` since `57cbacfbf` "change no clean-up
  line"; the merge `6b62de94e` took integrate's DAEO-aks1 whole, dropping the six ids `57cbacfbf` had added to its
  `sources:`, because DEC-1176 removed the KPI lines that cited them; `gov links` finds no unlinked id there).
  Ordinary work: yes, because a lead taking another ticket's file whole will not see a clean-up line go with it.
  Consequence: other (the merge commit's message states the drop; no count is wrong, no check fails open, and the ids
  went with the owner's DEC-1176 rewrite, so no work is lost). A row: the record's wording rides along in any later
  W2-130 resume (DEC-802); no round.
- **F3** (section 9's "(1355, listed above)" counts UNLINKED_ID findings on closed tickets, while `closed-missing`
  lists 669 distinct ticket and id pairs; carried over from run 3). Ordinary work: yes. Consequence: other (the block
  is exact; the prose count is of findings). A row, as F2.

## The auditor's return, word for word

**Sandbox check (step 0, `EMG-d4b-launched.md`):**
- **(a) passed.** Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-q8cl` failed with `OSError: [Errno 30] Read-only file system`, and no file exists there.
- **(b) passed.** `git hash-object -w --stdin` exited 0 (object `1ae28402a`) and `git update-index --refresh` exited 0.
- **`ps` check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` showed nothing.

- task: DAEO-q8cl (W2-130), run 4's narrow independent check of the record refresh `a2671a340`
- status: DONE. All four items pass, with three findings, all rows and none blocking.
- work_completed: checked items 1 to 4 below, using my own `gov links --all --json` runs on `git clone --shared` copies in `$TMPDIR` (at `a2671a340`, `6b62de94e` and `232efc47d`), my own script comparing the blocks, and the acceptance folder.
- files_changed: none. `git status --porcelain` of the tree is empty and HEAD is still `a2671a340`.
- evidence: the per-item findings below.
- tests: the W2-130 acceptance folder, run through `heavy_slot.sh` with the filter `-m "not local_only" -k "not real and not green_here and not time_limit"`, gave **81 passed in 52.52s** (exit 0). The filter left out any cases marked `local_only` or named with `real`, `green_here` or `time_limit`; the CTO runs those outside the sandbox.
- discoveries: F1, F2 and F3 below.
- risks: none new.
- lessons: a merge that takes another branch's ticket whole can drop a clean-up line. A record that says "no clean-up line changed" should be checked line by line against the clean-up commits' added lines.
- proposed_decisions: none.
- unresolved: none.
- recommended_next_action: commit this as the probe record and land. F1 to F3 are rows. If the ticket resumes anyway, their prose fixes ride along (DEC-802).

---

Independent auditor, 2026-11-14T01:36:29+00:00, at a2671a340dda6b020e6e16099b51d535a2e408ae, W2-130 run 4 narrow check.

## Item 1: the refresh commit changes only the refreshed blocks and their prose

**How I checked:**
- Ran `git show --stat a2671a340` and read the full diff.
- Parsed every fenced `w2-130:<name>` block at the parent `6b62de94e` and at `a2671a340` with a script, then compared them byte for byte.

**What I found:**
- The commit touches one file, `docs/research/W2-130-link-cleanup.md` (+31/−21). The register, the tickets and every other file are unchanged.
- Both revisions hold the same 24 blocks.
- Four blocks changed as expected: `closed-missing`, `counts-after`, `left` and `no-record`. `no-record`'s content is still `{}`; only the prose around it changed (36 → 35, "at the merged head").
- One block changed that the brief lists as byte-identical: in `counts-before`, the `command` string changed from "the tool of 57cbacfbfc86" to "the tool of 6b62de94e3fd". Its numbers did not change. This is F1.
- The other 19 blocks are byte-identical to the parent's: archive-13, audits, census, commits, comparison, dec-1123-linked, drift, drift-run, ids-87, judged-wrong, lessons, the six patch blocks, recount and trailer-residuals.
- The prose changes are where the brief says they should be: the header note, section 5's closed-missing and no-record sentences, section 9's table, sentences and new note, and section 10's new opening line and its D-9 total.

## Item 2: the refreshed blocks against the tool

**How I checked:** `gov links --all --json` on a clone at `a2671a340`. It returned 1735 findings, and its findings equal those of a separate run at `6b62de94e`, compared after sorting them as JSON. A script compared each block with that output.

**What I found:**
- **`counts-after`, all three maps equal my run:**
  - by_code: UNMARKED_CHANGE 8, UNKNOWN_ID 56, UNLINKED_ID 1420, NOT_IN_FORCE_AS_RULE 19, ENFORCES_SUPERSEDED 14, CLOSED_TICKET_EDITED 122, TICKET_CHANGE_UNMARKED 96.
  - by_code_role: equal.
  - unlinked_by_status: closed 1355, open 63, in_progress 2.
- **`left`, all three areas equal my run (path → role → count):**
  - D-5: `{}`, matching 0 findings.
  - D-6: 10 paths, 22 findings (ENFORCES_SUPERSEDED 14, UNKNOWN_ID 8).
  - D-9: 189 paths, 1674 findings (UNLINKED_ID 1420, CLOSED_TICKET_EDITED 122, TICKET_CHANGE_UNMARKED 96, UNKNOWN_ID 35, NOT_IN_FORCE_AS_RULE 1).
  - The path changes make sense. DAEO-drhj is now closed and has 3 UNLINKED_ID findings (DEC-1020, DEC-747), which also enter `closed-missing`. DAEO-6icv and DAEO-uw5h are new in-progress tickets whose acceptance-test paths do not exist yet (UNKNOWN_ID).
- **`closed-missing` equals the UNLINKED_ID findings on closed tickets, per ticket:** 143 tickets and 669 ids. Every ticket in it is closed at HEAD, and no listed id is already in that ticket's `sources:`.
- **`no-record`:** HEAD has 35 UNKNOWN_ID findings on tickets, and every one is a `tests/` path. `{}` therefore covers them all.
- **The section prose figures match:** 143 tickets, 35, 1355, 65, 22 and 1674.
- **`counts-before`:** with HEAD's tool on `232efc47d`, all eight by_code counts equal the block. The new command wording ("the tool of 6b62de94e3fd") is therefore true. `src/gov/links` has no commit after `8f8d707f0bd0` up to HEAD.

**Is the `counts-after` form fair?** Yes:
- `head: 57cbacfbf` is the last entry of `commits.cleanup`, as the test reads it.
- `measured_at: 6b62de94e` and the command's clone path name the tree that was actually counted.
- My count at `6b62de94e` equals the block, and the count at `a2671a340` is identical.
- Section 9's table header ("measured at 6b62de94e3fd, after the last clean-up commit 57cbacfbfc86") and its new note say the same thing.

**Two pieces of prose are imprecise:**
- The command string and the section 9 note say the merges since `57cbacfbf` "change no clean-up line" / "bring other tickets' commits only". I checked every line the six clean-up commits added that still stood at `57cbacfbf` (654 lines). One is gone at `6b62de94e`: W2-88b's (DAEO-aks1) `sources:` line, from which the merge removed the six ids `57cbacfbf` had added (CAP-10, CAP-19, DEC-1097, DEC-1098, DEC-833, DEC-860). One more changed but kept its content: DEC-954's status line gained a `Changed by: DEC-1176` mark. This is F2.
- Section 9's "(1355, listed above)" counts findings, but `closed-missing` lists 669 distinct (ticket, id) pairs. This wording was carried over from run 3. This is F3.

## Item 3: no sources follow-up was needed

**How I checked:** from my run at HEAD, I collected the UNLINKED_ID findings on tickets whose front matter says `open` or `in_progress` and compared them with the pairs in `dec-1123-linked`.

**What I found:** there are 65 such pairs and `dec-1123-linked` lists 65. The difference is empty in both directions. No unlinked id was added on a live ticket, so leaving out a sources commit was right. The acceptance cases for S4's form at HEAD also pass.

## Item 4: no history rewritten

**How I checked:** `git merge-base --is-ancestor`.

**What I found:** `798278be5` and `6b62de94e` are both ancestors of `a2671a340`, and `6b62de94e` is its direct parent. The first-parent history is `ba9f5ed4d → fcf5f5038 → 58b52ccb0 → 798278be5 → 6b62de94e → a2671a340`.

## Findings

- **F1 (item 1):** the brief lists `counts-before` as byte-identical, but its `command` string changed. It now names "the tool of 6b62de94e3fd" instead of 57cbacfbfc86, because run 4's `build_record.py` puts the measuring commit into both count blocks. Its numbers are unchanged, and I confirmed that HEAD's tool reproduces all eight counts at `232efc47d`, so the text is true. It would be reversed if the tool at `6b62de94e` gave different counts at `232efc47d`; it does not.
  - Ordinary work: yes, because a lead re-rendering the record from one builder changes every block that builder fills.
  - Consequence: other (a true wording change in a block that should not have moved; nothing fails open and no work is lost).
- **F2 (item 2, prose):** the record says the merges of `w2/integrate` after `57cbacfbf` "change no clean-up line, only other tickets' files". In fact merge `6b62de94e` replaced the clean-up's DAEO-aks1 `sources:` line with integrate's DEC-1176 version, which drops the six ids `57cbacfbf` added. The ids went because the KPI lines that cited them were removed, and `gov links` finds no unlinked id there. The merge commit's message states the drop, but the record does not; a reader of the record alone would think those six sources still stand. The counts are correct because they were measured at the merged head. It would be reversed if DAEO-aks1's `sources:` at `6b62de94e` still held those six ids; it holds `[DEC-1176, DEC-1150, DEC-996, DEC-954, DEC-1099, DEC-728]`.
  - Ordinary work: yes, because a lead who takes another ticket's file whole in a merge will not see that one of the clean-up's lines went with it.
  - Consequence: other (an incomplete statement of history; no figure is wrong, no check fails open, and the dropped ids were superseded by the owner's DEC-1176 rewrite, so no work is lost).
- **F3 (item 2, prose, carried over from run 3):** section 9 says "The UNLINKED_ID left are on closed tickets (1355, listed above)". 1355 is the number of findings, while `closed-missing` lists 669 distinct (ticket, id) pairs, because one id can be reported at several lines or commits. It would be reversed if `closed-missing` held 1355 entries.
  - Ordinary work: yes, because a reader matches the stated count against the list above it.
  - Consequence: other (a confusing count; the block itself is exact).

None of the findings is in scope, reachable in ordinary work and failing open or losing work, so none blocks.

```verdict
{"head": "a2671a340dda6b020e6e16099b51d535a2e408ae", "date": "2026-11-14T01:36:29+00:00", "kpis": [{"kpi": "1", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "2", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "3", "verdict": "pass", "findings": []}, {"kpi": "4", "verdict": "pass", "findings": []}]}
```
