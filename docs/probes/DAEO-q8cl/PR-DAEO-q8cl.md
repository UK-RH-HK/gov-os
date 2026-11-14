---
type: probe
task: DAEO-q8cl
reviewer_session: 0dfdfb5a-a925-4018-b073-c4ac514a0807
implementer_session: f86ed606-307a-47bd-a3bf-db5ccd3f4625
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 58b52ccb011973e7c7c521ef1b65f6196dc8e55d
decisions_applied: [DEC-1073, DEC-1098, DEC-1088, DEC-1123, DEC-866, DEC-927, DEC-861, DEC-1010]
---

# Probe record: W2-130 (DAEO-q8cl), run 3's narrow independent check

A fresh independent-auditor session (`0dfdfb5a-a925-4018-b073-c4ac514a0807`) ran on `claude-opus-5-5` at high
effort, class C2, read-only, with JUDGEMENT.md word for word in its brief. It probed head `58b52ccb0119` of
`w2/W2-130` and wrote nothing in the tree (`git status --porcelain` empty at its end; its tripwire's changes are other
sessions' trees). The implementers of what it probed were:
- the ticket lead (orchestrator, `f86ed606-307a-47bd-a3bf-db5ccd3f4625`): the merge of `w2/integrate` (11c4d7a5a), the
  sources follow-up (57cbacfbf), the record and LINK-RECONCILIATION.md (fcf5f5038), the merges of the tests
  (ba9f5ed4d, 58b52ccb0);
- independent test designer td-2 (`f96af315-5d4c-4c98-aab9-420ea8d82dc8`): S4 revised to DEC-1123 (2) (d5b07cc72,
  `Rewrite-Reason: P-W2-130-4 (a)`);
- independent test designer td-3 (`ef44fc05-b1d1-4788-9353-ffad4ed90279`): five marks cases cut back to their Verify
  lines (a606a530f, `Rewrite-Reason` naming the lead's run-3 findings).

This is the narrow independent check the CTO's run-3 brief asks for (P-W2-130-4 (a), DEC-1010). Its verdict is
**PASS**: five items pass, one finding (F1).

## The lead's judgement of the finding

- **F1** (c4420040f's `free_text` list omits DEC-040<-DEC-083, which `gov links` flags as free text when read at
  that commit's parent rather than on its own register with its marks taken off). Ordinary work: yes, because a lead
  building the record by its stated definition files the pair this way. Consequence: other (the classification of
  one checked, right, owner-ruled mark; nothing fails open and no work is lost). A row: its one-line note rides along
  in any later W2-130 resume (DEC-802); no round.
- **The auditor's discovery on the audit times:** the record's times 2026-11-08T01:35:59Z and 2026-11-09T00:41:51Z
  are the first writes of each verdict in the earlier auditor's session transcript (session ad44f5fe, subagent
  agent-abeeaeb52fe9d7a0a), as the record's `audit_source` names; the review file itself carries dates only.
- **W3-P09** (the auditor's observation, no finding): read as a list row under DEC-1123 (2), as `gov links` and the
  test designer's case read it.

## The auditor's return, word for word

## Return

**Step 0, sandbox check: passed.**
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-q8cl` failed with `OSError: [Errno 30] Read-only file system`, and no file exists there.
- (b) `echo sandbox-trial | git hash-object -w --stdin` worked (`1ae28402a109c3397a44b19239a00adfa9472eb0`, which leaves one unreferenced loose object in the shared `.git`; that is this session's only write outside `$TMPDIR`). `git update-index --refresh` exited 0.

**`ps` check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing. **Tree:** `git status --porcelain` is empty at the end, and HEAD is `58b52ccb011973e7c7c521ef1b65f6196dc8e55d`.

- task: DAEO-q8cl (W2-130), the independent auditor's narrow check of run 3's follow-ups (items 1 to 5 of the brief)
- status: done. All five items pass. One finding (F1): ordinary work yes, consequence other. It is a row, not a round.
- work_completed:
  - Re-ran `gov links --propose-sources --all` at 11c4d7a5a and `gov links --all --json` at 58b52ccb0, 232efc47d, 2fcfea4d8 and 8f8d707f0, each on a `git clone --shared` in `$TMPDIR` with HEAD's tool.
  - Checked the follow-up commit `57cbacfbf` field by field.
  - Checked every one of the 65 `dec-1123-linked` entries against the ticket files at HEAD.
  - Re-ran the record's `drift` block at HEAD and its `recount` block at 232efc47d.
  - Compared `counts-before`, `counts-after`, `left`, `closed-missing`, `no-record`, `lessons`, `judged-wrong`, `audits` and `comparison` with my own runs and with the audit texts.
  - Compared LINK-RECONCILIATION.md with the sitting file at 2f9c80b1f, row by row.
  - Read both test-designer revisions against S1, S2 and S4.
  - Checked that the three merges carry no hand edits (`git show --remerge-diff`).
  - Ran the acceptance folder.
- files_changed: none
- evidence: the paths and commands are named under each item below.
- tests: the acceptance folder `tests/acceptance/W2-130` with `-m "not local_only" -k "not real and not green_here and not time_limit"` gave **81 passed in 49.87 s**. The exclusion deselected nothing that ran here; the folder has no real-model cases. The heavy-slot script could not write its wait log (`heavy-slot-waits.jsonl: Read-only file system`, the sandbox), and the run went ahead anyway.
- discoveries:
  - **The audit times are not checkable from the texts named.** The record's audit times (2026-11-08T01:35:59Z, 2026-11-09T00:41:51Z) are hard-coded in `lead/rec/build_record.py`. The audit texts I was given (`ref/w2-130-marks.md`) give only the dates, which match. I could not confirm the times.
  - **The guard refused two of my calls.** Each was a different call and neither was repeated:
    - `git grep` on a revision ("could not decide: git cannot say whether a revision holds the hidden part"). I read the ticket files from the clones' checked-out trees instead.
    - An unpathed `git show --remerge-diff`. I re-ran it limited to named paths.
  - **The recount ran with one change.** The `recount` block uses `git grep <rev>` internally. I ran it with that one line replaced by a read of the `.tickets/` files in a clone checked out at 232efc47d, so nothing the guard refused ran inside an interpreter.
- risks: none beyond F1.
- lessons: an S3 "derived from free text" set depends on which register is read. The commit's own register with its marks taken off and the commit's parent give different answers when the commit also writes decided statuses.
- proposed_decisions: none
- unresolved: the two audit times above, which I could not verify from the texts named.
- recommended_next_action: commit this record. Fold F1's one-line fix (a note in `audits`/`comparison`) into any later W2-130 resume (DEC-802). No round is needed.

---

Independent auditor, 2026-11-14T01:16:50+00:00, at 58b52ccb011973e7c7c521ef1b65f6196dc8e55d, W2-130 run 3 narrow check.

### Item 1: the sources follow-up `57cbacfbf`: pass

**Which tickets and lines it changes.**
- Its parent is 11c4d7a5a. It changes 12 files, all `.tickets/*.md`. Each ticket was `open` or `in_progress` at the parent.
- I parsed each file's front matter at the parent and at the commit:
  - every field other than `sources:` is equal;
  - the body is byte-identical;
  - each `sources:` list is the old list with ids appended.
- A line-level diff shows no changed line other than `sources:` lines and `- <id>` items.
- No other file changes.

**The ids it adds.**
- `gov links --propose-sources --all` at 11c4d7a5a, run by me, proposes ids for 167 tickets. 25 of them are open or in progress, with 97 (ticket, id) pairs.
- 97 less the record's 65 `dec-1123-linked` pairs gives 32 ids on 12 tickets. That equals, per ticket, exactly what the commit adds.
- The record's `patch-sources-2` equals my proposal's open and in-progress sections, id for id.

**The forms at HEAD.**
- Each of the 65 entries is of its form: 53 `list_rows`, 11 `wbs`, 1 `dec-798`.
  - `list_rows`: the id is in the ticket's `list_rows` and `via` is the id.
  - `wbs`: `via` is the ticket whose `wbs_id` is the id, and `via` is in `sources:`.
  - `dec-798`: DEC-1033 is in DAEO-swdu's `sources:` and is not reported NOT_IN_FORCE_AS_RULE.
- Every listed ticket is open or in progress.
- `gov links --all --json` at HEAD reports UNLINKED_ID on open or in-progress tickets for exactly those 65 pairs: none missing and none extra.

**The record's two choices.**
- **W2-H046 on DAEO-6w5n: right.**
  - DAEO-6w5n has no `list_rows` and no ticket has W2-H046 as its `wbs_id`, so no form applies.
  - S4's line asks for the id from `--propose-sources`, and putting it in `list_rows` would change a field other than `sources:` (F1 of the ticket).
  - It is the only W-row id the commit adds. W2-60a and W2-56 are WBS ids whose tickets (DAEO-cv58, DAEO-wnnz) are not in the receiving ticket's `sources:`, so they are correctly added rather than listed as forms.
- **W3-P09 on DAEO-ecac: defensible.**
  - It is in DAEO-ecac's `list_rows` (`docs/plan/WAVE_3_PARKING.md:7`).
  - S4 says "a backlog row in list_rows". W3-P09 is a parking-list row, and the record says so openly ("a plan row").
  - `gov links` treats every plan list file's rows alike (`src/gov/links/check.py:262-271`), and so does the test designer's case (`BACKLOG_ROW = ^W[0-9]+-[A-Z][0-9]+$`).
  - I take "backlog row" to cover any plan list row. If the CTO reads it as Wave 2 lists only, W3-P09 would need a sources commit, and S4 allows at most one follow-up. I record this judgement but do not raise it as a finding.

### Item 2: the record's blocks against git and the tools: pass, with F1

**`commits`.**
- All hashes are full and resolve.
- e12f8a30c's parent is 232efc47d.
- 34eed411a, 3679ca0ba and 2f9c80b1f are ancestors of e12f8a30c.
- 9546edd61 is an ancestor of c4420040f and not of e12f8a30c.
- The order of `cleanup` matches the commits' topology and dates: e12f8a30c, c4420040f, 8d245901b, 8f8d707f0, bce798c3a, 57cbacfbf.
- The lists match what each commit changes:
  - marks: e12f8a30c and c4420040f (register lines), bce798c3a (2 register lines);
  - sources: e12f8a30c (50 tickets) and 57cbacfbf;
  - status and r12: c4420040f, and 8d245901b (one DECISIONS-IN-FORCE line);
  - lessons: 8f8d707f0 (5 `docs/lessons` files).

**`audits`.**
- Heads match the texts: 2f9c80b1f807 (`ref/w2-130-marks.md:14`), ce7f10eb8a2a (`:307`), 09542040f (aud-marks-1, header and verdict block).
- Dates match: 2026-11-08, 2026-11-09, 2026-11-13T22:46:14+00:00. The first two times are not in the texts (see discoveries).
- Sources are named correctly.
- I rebuilt each commit's added (changed, changer) pairs from its register diff: e12f8a30c 139, bce798c3a 2. I set them against `gov links` UNMARKED_CHANGE `text: true` at each commit's parent (HEAD's tool):
  - **e12f8a30c:** all 8 committed free-text pairs are in `free_text` with verdict right.
  - **bce798c3a:** no free-text pairs. The two labelled marks' `committed_mark` texts equal the appended text, byte for byte, and equal aud-marks-1's `commit_as`.
  - **c4420040f:** see F1.
- No committed pair is judged wrong in any audit. No `dropped` pair is committed, and every `committed` pair is committed.

**`judged-wrong`.**
- The 19 verdicts and fates match aud-marks-1's B table (8 pairs) and C table (11 pairs), pair for pair (`lead/aud-marks-1-return.md:44-67`).
- The earlier F1, F2, F3, F4 and F14 references match `ref/w2-130-marks.md`.
- The 8 pairs marked `in_gov_links: true` equal exactly the 8 UNMARKED_CHANGE that `gov links --all --json` reports at HEAD.

**`trailer-residuals`.** The `recount` block at 232efc47d gives 13 values (8 `Task:`, 5 `Implements:`). That is the same set as the record's `values`, with identical commit lists. Each value has `should_have_named`.

**`drift`.** Re-run at HEAD it gives `count: 6`, the same 6 pairs as `drift-run`. All 6 are in `judged-wrong`, so the count after setting them aside is 0. `drift-run` was taken at 57cbacfbf, and the register has not changed since.

**`counts-after` and `counts-before`.** My `gov links --all --json` at HEAD and at 232efc47d equal the blocks' `by_code`, `by_code_role` and `unlinked_by_status` exactly (after: UNLINKED_ID 1417 = closed 1352 + open 63 + in progress 2; STATUS_CONFLICT 0).

**The other blocks.**
- `left`: D-5 is 0, D-6 is 22 findings across 10 paths, D-9 is 1672. Each equals HEAD's findings by path and role.
- `closed-missing`: 142 closed tickets with exactly their UNLINKED_ID ids.
- `no-record`: `{}`. All 36 ticket UNKNOWN_ID are `acceptance_tests.path` values.
- `lessons`: the five lessons' `sources:` match what the block says, each agrees with its own **Source:** line, and `gov links` reports no finding on `docs/lessons/`.

### Item 3: LINK-RECONCILIATION.md: pass

- The sitting file is unchanged between 2f9c80b1f and HEAD.
- I parsed its groups A to F: 150 rows (A 19, B 13, C 8, D 90, E 13, F 7).
- LINK-RECONCILIATION.md holds exactly those 150 ids, each with the same group, the Proposal (without `**`) and the Evidence column verbatim. There are 0 differences and no extra rows.
- Every row reads "accepted as proposed (DEC-1098 (3))". That matches DEC-1098 (3) ("W2-130's sitting accepted as proposed: groups A to G; H1 (b) …"), committed in 9546edd61.
- The header names `W2-130-SITTING.md` (2f9c80b1f) and DEC-1098 (3).

### Item 4: the test designer's revisions: pass

**d5b07cc72 (S4).** The three head cases check, in order:
- every UNLINKED_ID on an open or in-progress ticket is listed;
- each entry is of its form, read from the files at HEAD (DEC-1033's liveness through `gov links`);
- the list holds only reported pairs, with no duplicates.

The follow-up case requires the commit's added ids to equal both `patch-sources-2` and `--propose-sources` at its parent, each less the forms. A form id that was also added to `sources:` would fail it. The case that the follow-up "changes only `sources:` of live tickets and no other file" is unchanged. This is all S4's re-baselined line states.

**a606a530f (S1, S2).**
- **Finding 1 (patch a0):** the union of the a0 to a2 pairs must still equal the marks e12f8a30c adds, after the drops. The revision adds a check that the patches touch only files the commit changes. That is stronger, not weaker.
- **Findings 3 and 4 (the two follow-up marks):** the case still requires the following:
  - one marks commit named in the record, after both clean-up commits;
  - an append that makes the line name the changer in a **Changed by:** field;
  - the audit's right verdict at an ancestor head, dated before the commit.

  Only the exact wording is dropped, and the auditor corrected that wording under S3.
- **Finding 5 (the 215):** "named on its own status line" is now read as `gov links` reads it. S1's case still checks the **Changed by:** / SUPERSEDED by form for the 87.
- **Finding 2 (marks on the 87 after e12f8a30c):** outside a marks commit, an append that adds no census pair is now allowed. The literal line ("a mark on one of the 87 added after e12f8a30c is in c4420040f or a follow-up marks commit") is broader. But the line is about the clean-up's marks, and taken literally it would turn red on every later DEC-866 mark another ticket makes (518772b5c, DEC-989<-DEC-1141). A census pair appended outside a marks commit, or a mid-line edit, still fails. I judge this not weakened below the line's intent, and record it here as an observation.

### Item 5: no other register or ticket text changed: pass

- `git diff 11c4d7a5a 58b52ccb0 -- docs/DECISION_REGISTER.md .tickets/` is byte-identical to `git diff 11c4d7a5a 57cbacfbf` on the same paths.
- `git show --remerge-diff` of 11c4d7a5a, ba9f5ed4d and 58b52ccb0 (limited to docs, tests, `.tickets`, governance, src) is empty. The merges hold no hand edits, so 11c4d7a5a brought only what `w2/integrate` had.
- fcf5f5038 adds only the record and LINK-RECONCILIATION.md. d5b07cc72 and a606a530f touch only `tests/acceptance/W2-130/`.

### Findings

**F1: c4420040f's `free_text` list in `audits` (and its `comparison` count, 2) leaves out one owner-ruled mark that `gov links` flags as free text at that commit's parent.**
- **What happens:** `gov links --all --json` (HEAD's tool) at 2fcfea4d8, c4420040f's parent, reports DEC-040<-DEC-083 with `text: true` ("text: amended by"). c4420040f commits it as `**Changed by:** DEC-083 (installs: owner approval per tool)`. The record lists it under `labelled`, verdict right, so `free_text_committed` for c4420040f reads 2 where reading at the parent gives 3.
- **Why it matters little:** the mark is one of the 13 group B marks DEC-1098 (3) ruled. The part 2 auditor checked those against the rulings (`ref/w2-130-marks.md:324`), and it is in the check with verdict right. So F3's substance (0 unchecked, 0 wrong) holds.
- **Why the two readings differ:** by the record's own stated definition (the commit's register with its marks taken off), the pair is not flagged. c4420040f's decided status text itself contains "DEC-083".
- **What should happen:** a one-line note in `audits` or `comparison` naming the pair and why it is filed as labelled.
- **Evidence that would reverse it:** a ruling that S3's "derived from free text" is read on the commit's own register with its marks taken off, as the record and the test designer's README define it. Under that reading the record is exact.
- Ordinary work: yes, because a lead building the record by its stated definition would file the pair exactly this way.
- Consequence: other (the classification of one checked, right, owner-ruled mark; nothing fails open and no work is lost).

**Classification:** one finding, ordinary work yes, consequence other. It is a recorded row, not a round (DEC-801, DEC-802).

**What I probed and found sound:**
- The follow-up's ids, fields and files.
- All 65 forms, and the completeness of the UNLINKED_ID set at HEAD.
- Commit ancestry and order.
- Drift: 6 pairs, 0 after setting aside the judged-wrong ones.
- The 8 judged-wrong pairs against `gov links`.
- The trailer recount.
- Counts before and after, and the `left`, `closed-missing`, `no-record` and `lessons` blocks.
- The 150 reconciliation rows.
- The merges' cleanliness.
- The test revisions' fidelity to their lines.
- 81 of 81 acceptance cases passing.

```verdict
{"head": "58b52ccb011973e7c7c521ef1b65f6196dc8e55d", "date": "2026-11-14T01:16:50+00:00", "kpis": [{"kpi": "1 sources follow-up 57cbacfbf (S4)", "verdict": "pass", "findings": []}, {"kpi": "2 record blocks against git and the tools", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "3 LINK-RECONCILIATION.md (S6)", "verdict": "pass", "findings": []}, {"kpi": "4 test designer's revisions d5b07cc72, a606a530f (S1, S2, S4)", "verdict": "pass", "findings": []}, {"kpi": "5 no other register or ticket text changed in run 3 (F1)", "verdict": "pass", "findings": []}]}
```
