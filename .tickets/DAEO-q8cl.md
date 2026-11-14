---
id: DAEO-q8cl
status: in_progress
deps: [DAEO-q7lk, DAEO-n0wb]
links: []
created: 2026-11-06T13:56:01Z
type: task
priority: 1
assignee: orchestrator
external-ref: W2-130
tags: [wave-2, records, memory, links, standard]
wbs_id: W2-130
title: 'The link clean-up: every drifting decision marked in its own entry (the 87 with no hint first), tickets linked to the decisions they rest on, commit trailers'' residuals listed, and one status-reconciliation list for the owner (DEC-1073 (5)(a))'
class: ops
state_class: AUTHORITATIVE
role: orchestrator
depends_on: [DAEO-q7lk, DAEO-n0wb]
allowed_paths:
- docs/DECISION_REGISTER.md
- governance/project/orchestration/ARCHIVE-SUPERSEDED.md
- governance/project/orchestration/DECISIONS-IN-FORCE.md
- governance/project/orchestration/packages/LIFT-1/LINK-RECONCILIATION.md
- .tickets/*.md
- docs/lessons/*.md
- docs/research/W2-130-link-cleanup.md
- tests/acceptance/W2-175/test_w2_175_record.py
- tests/acceptance/W2-175/w2_175_support.py
kpis:
  success:
  - 'The 87 first: every decision the census found current, stated changed and with no hint in its own entry names each of its changers on its own status line (**Changed by:** DEC-n (the part), or SUPERSEDED by DEC-n for a whole supersession by ids alone), applied from gov links --propose-marks in a commit of its own [DEC-1073 (5)(a), DEC-866, DEC-825 item 4] [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: tests/acceptance/W2-130/ (written before this ticket''s follow-up commits): for each of the 87 ids the census''s script computes as current, stated changed and with no hint in its own entry (docs/research/D4B-link-census.py at 3d1c459e, run on 24f06026; the ids listed in the record), the entry''s own status line at HEAD names every changer the census states for it, as **Changed by:** DEC-n (the part), or SUPERSEDED by DEC-n for a whole supersession by ids alone, except a pair the independent auditor''s check (S3) judged wrong (DEC-853<-DEC-884, DEC-1050<-DEC-1057), each listed in the record with the auditor''s verdict; the record names e12f8a30c (batches a0, a1, a2 and b1; its parent 232efc47d is the clean-up''s starting head) as the commit that adds the 87''s marks, and every docs/DECISION_REGISTER.md hunk of e12f8a30c is a status-line append only (each removed line an existing entry''s **Status:** line, each added line that line kept whole with marks appended); the marks e12f8a30c adds equal the gov links --propose-marks output it applied (patches a0, a1 and a2, kept beside the record) after the auditor''s drops and rewrites (S3); a mark on one of the 87 added after e12f8a30c is in c4420040f or a follow-up marks commit named in the record, under the same append-only check'
  - 'Then the rest: after the clean-up, gov links --all reports no UNMARKED_CHANGE on this repository, so each of the census''s 215 drifting decisions names every changer the register or ARCHIVE-SUPERSEDED §A states, the 13 pairs stated only in the archive included; the drift count by docs/research/W2-92-proto-drift.py''s definitions, read from the entries'' own text, is 0 [DEC-1073 (5)(a), DEC-1072 (1)] [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: tests/acceptance/W2-130/: gov links --all --json on HEAD reports no UNMARKED_CHANGE other than exactly the 8 pairs the earlier independent auditor judged wrong (DEC-853<-DEC-884, DEC-1050<-DEC-1057, DEC-120<-DEC-173, DEC-724<-DEC-860, DEC-056<-DEC-017, DEC-072<-DEC-064, DEC-162<-DEC-156, DEC-1053<-DEC-880), each listed in the record with the auditor''s verdict (P-W2-130-2 (a)); DEC-1115<-DEC-1122 (4) and DEC-026<-DEC-086 are marked on their own status lines at HEAD, each by a follow-up marks commit named in the record that comes after an independent auditor''s check judging the mark right (S3); each of the census''s 215 drifting ids, and each of the 13 pairs stated only in ARCHIVE-SUPERSEDED §A, has every stated changer named on its own status line at HEAD, except a pair the independent auditor''s check judged wrong, each listed in the record with that verdict; docs/research/W2-92-proto-drift.py''s definitions, applied to the entries'' own text (not a store), give a drift count of 0 once those listed pairs are set aside, the command, its output and the pairs set aside kept in docs/research/W2-130-link-cleanup.md'
  - 'Checked where the patterns guess: before each marks commit, an independent auditor checks every mark derived from free text, and 20 labelled marks drawn at random, against both entries; a wrong mark is corrected or dropped, never committed; the check is in the record [DEC-1073, DEC-1010] [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: docs/research/W2-130-link-cleanup.md holds, for each marks commit (e12f8a30c, c4420040f and each follow-up marks commit named in the record), the independent auditor''s check, dated before that commit and made at a head that is an ancestor of it (e12f8a30c: the audit at 2f9c80b1f; c4420040f: the audit at ce7f10eb8a2a; both from reviews/w2-130-marks.md): every mark gov links derived from free text (its (text) findings) and 20 labelled marks drawn at random by a stated seed (every labelled mark where the commit adds 20 or fewer), each judged against both entries, with each wrong mark''s fate (corrected or dropped); a comparison of the check with the committed marks finds no committed mark that the check judged wrong and no committed free-text mark that the check does not list'
  - 'Tickets linked, open and in-progress tickets only: every id an open or in-progress ticket''s KPI brackets name and every Implements: id of its worker commits is in its sources:, from gov links --propose-sources, in one commit that changes no other field; gov links --all then reports no UNLINKED_ID on an open or in-progress ticket. A closed ticket is not edited: its missing ids are listed per ticket in the record. Ids that name no record are listed per ticket in the record, for D-9 [DEC-1073 (5)(a)] [changed, DEC-1098 (3); DEC-1088 (6)] [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: tests/acceptance/W2-130/: gov links --all --json on HEAD reports 0 UNLINKED_ID on any open or in-progress ticket other than the ids the record lists, per ticket, as linked by DEC-1123 (2)''s forms (a backlog row in list_rows, a WBS id whose ticket id is in sources:, DEC-798 through its live DEC-1033), each with how it is linked [S4 re-baselined to DEC-1123 (2), the CTO, P-W2-130-4 (a)]; the record names the sources commits: e12f8a30c (batch b1) and at most one follow-up commit for the UNLINKED_ID that arose after b1; in each, every changed ticket line belongs to the sources: field of a ticket open or in progress at that commit''s parent (every other field and the body of every ticket byte-identical to that commit''s parent), the follow-up changes no other file, and the ids each adds equal gov links --propose-sources'' output at its parent, less the DEC-1123 (2) forms the record lists (for e12f8a30c the b1 patch, kept beside the record); outside those two, a clean-up commit adds to sources: only the ids its owner-decided change names (c4420040f: DEC-1098 and DEC-1088 on this ticket); no closed ticket''s file is changed by a clean-up commit (e12f8a30c, c4420040f and the follow-ups named in the record); the record lists, per closed ticket, its missing ids, and, per ticket, the ids that name no record (for D-9)'
  - 'Commit trailers: history is not rewritten. Every Task: and Implements: value that names no record (the census counted 3,053 of 3,561 Task: values resolving, 496 of the rest decision-record, which is valid under DEC-861; and 4,187 of 4,246 Implements: values) is listed once in the record, with its ticket and the ids it should have named, as DEC-927 did for its 39 [DEC-927, DEC-861, DEC-1073] [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: docs/research/W2-130-link-cleanup.md lists each Task: and Implements: trailer value in the integration branch''s history at the clean-up''s starting head 232efc47d (e12f8a30c''s parent) that names no record (Task: decision-record excluded as valid under DEC-861) once, with its commit, its ticket and the ids it should have named; a recount over that history''s trailers by the command the record keeps gives the same set of values; 232efc47d is an ancestor of HEAD (git merge-base --is-ancestor), so no history was rewritten'
  - 'Status reconciliation, apart from drift: LINK-RECONCILIATION.md lists, for the owner, the 110 decisions ARCHIVE-SUPERSEDED §B calls spent while the register lists them current, the 40 PROPOSED entries, and every STATUS_CONFLICT gov links --all finds. Per id it gives the CTO''s proposal (done, in force, superseded by, accepted or rejected) with its reason. Nothing is applied before the owner decides; then the register carries each decided status (W2-55''s `· done` tag or the status word), and ARCHIVE-SUPERSEDED and DECISIONS-IN-FORCE agree with the register, so gov links --all reports no STATUS_CONFLICT on them [DEC-1073 (2), DEC-953 item 7] [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: governance/project/orchestration/packages/W2-130-SITTING.md (committed in 2f9c80b1f, an ancestor of the starting head 232efc47d) lists the 110 ids ARCHIVE-SUPERSEDED §B at 232efc47d calls spent while the register at 232efc47d lists them current, the 40 PROPOSED entries at 232efc47d and every STATUS_CONFLICT gov links --all reports at 232efc47d (that commit''s gov links, the command and its output kept in the record), each with the CTO''s proposal (done, in force, superseded by, accepted or rejected) and its reason; governance/project/orchestration/packages/LIFT-1/LINK-RECONCILIATION.md exists at HEAD, carries the sitting''s ids with the same proposals and points to W2-130-SITTING.md as the list the owner ruled on; the owner''s decision on the list is DEC-1098 (3), committed in 9546edd61, an ancestor of every clean-up commit that changes a status (c4420040f and any follow-up named in the record); after it, each decided id''s register status at HEAD carries the decision (the · done tag or the status word), and tests/acceptance/W2-130/ finds gov links --all --json on HEAD reporting 0 STATUS_CONFLICT on the decided ids between the register, ARCHIVE-SUPERSEDED and DECISIONS-IN-FORCE, after a follow-up commit named in the record rewords DECISIONS-IN-FORCE''s R-12 line so it does not read as listing DEC-896 in force (P-W2-130-3 (a))'
  - 'Lessons: each lesson in docs/lessons/ names the decision or failure it came from in a sources: key [DEC-1073 (5)(c)] Verify: tests/acceptance/W2-130/: every docs/lessons/*.md at HEAD has a front-matter sources: key naming at least one id, and gov links --all reports no UNKNOWN_ID on a lesson''s sources:; the record lists each lesson with the id its sources: names and the decision or failure its text says it came from, and the two agree'
  - 'The record, docs/research/W2-130-link-cleanup.md: the counts by finding code and role before and after, the commits, the auditor''s check, the trailer residuals, and what is left by path and role for D-5 (kernel texts), D-6 (code and tests) and D-9 (tickets) [DEC-1073] [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: docs/research/W2-130-link-cleanup.md exists at the close and holds: gov links --all''s counts by finding code and role at the clean-up''s starting head 232efc47d and at its last commit, each with its command; the commit ids of the marks, sources and status commits (e12f8a30c, c4420040f and each follow-up); the auditor''s check (S3); the trailer residuals (S5); and the findings left, by path and role, under D-5 (kernel texts), D-6 (code and tests) and D-9 (tickets); a re-run of gov links --all at the record''s last commit gives the record''s after counts'
  failure:
  - 'A register entry''s text changed other than its status line''s marks and the owner''s decided statuses; a ticket field other than sources: changed; history rewritten. [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: tests/acceptance/W2-130/: in the clean-up''s commits (e12f8a30c, c4420040f and the follow-ups named in the record), every changed line of docs/DECISION_REGISTER.md is an existing entry''s status line whose only change is added marks (the old line kept whole, marks appended) or a status DEC-1098 (3) names for that id on W2-130-SITTING.md (c4420040f: the new word first, the old status text kept); every ticket file''s front matter fields other than sources: and its body are byte-identical before and after each of those commits, except c4420040f''s edit of this ticket''s KPI 4 line, owner-decided by DEC-1098 (3) (H1 (b)) and marked [changed, DEC-1098 (3); DEC-1088 (6)]; the clean-up''s starting head 232efc47d is an ancestor of HEAD'
  - 'A status changed before the owner decides the reconciliation list; a spent or PROPOSED decision counted as drift. [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: no clean-up commit that does not have 9546edd61 (DEC-1098 (3), the owner''s decision on W2-130-SITTING.md, which LINK-RECONCILIATION.md copies and points to) as an ancestor changes a register status word or · done tag (e12f8a30c''s register hunks are status-line appends only; git merge-base --is-ancestor for the others); the drift list S2''s command counts at HEAD holds none of the 110 spent ids or the 40 PROPOSED ids that DEC-1098 (3) did not rule current, checked in tests/acceptance/W2-130/ against W2-130-SITTING.md''s ids and rulings'
  - 'A free-text mark committed unchecked; a wrong mark committed. [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: each mark a clean-up commit (e12f8a30c, c4420040f and each follow-up marks commit named in the record) adds that gov links flagged (text) appears in the auditor''s check (S3) with a verdict of right, dated before that commit and made at a head that is an ancestor of it; no committed mark is one the check judged wrong, among both the free-text marks and the labelled marks it judged; a comparison of the check with each marks commit''s diff, kept in docs/research/W2-130-link-cleanup.md, shows 0 unchecked and 0 wrong'
  - 'The clean-up started before W2-92''s links are adopted, or before W2-129 lands, without the owner''s word. [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: the record names the clean-up''s first commit, e12f8a30c, and W2-129''s landing commit (DAEO-q7lk, merge 34eed411a) and the commit that adopted W2-92''s stated links (DAEO-n0wb, merge 3679ca0ba) are both its ancestors (git merge-base --is-ancestor); the record also cites DEC-1097 (9), the owner''s decision that allowed the start'
profile: STANDARD
sources:
- DEC-1073
- DEC-1109
- DEC-1072
- DEC-866
- DEC-825
- DEC-927
- DEC-861
- DEC-953
- DEC-1010
- DEC-1098
- DEC-1088
- DEC-1123
est_loc: 0
acceptance_tests:
  path: tests/acceptance/W2-130/
  author: 'independent-test-designer (MR-3); written before the clean-up: repository-state cases that read HEAD only (seconds, record_reading). gov links --all on HEAD reports 0 UNMARKED_CHANGE and 0 UNLINKED_ID; the drift count by W2-92-proto-drift.py''s definitions from the entries'' text is 0; STATUS_CONFLICT is 0 on the ids the owner decided; every ticket''s field other than sources: is byte-identical to the clean-up''s starting head; the record lists the trailer residuals. The cases name the starting head; they never read the store of another tree.'
track: B
list_rows: []
---
# W2-130 The link clean-up (DEC-1073 (5)(a))

Card: from DEC-1073 (5)(a): "Clean up what is here: the 215 drifting decisions, the 87 with no hint in their own entry
first; tickets linked to the decisions they cite; commit trailers linked; the status conflicts." The owner's suggestion
for the time: right after the graph links are adopted. The plan is
`governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md` §3.

- **When:** right after re-pin window 4, once W2-92's stated links are in the product and W2-129 has landed.
- **What the graph already fixed:** retrieval reaches a changer for the 215 (209 to every changer, by the prototype's
  drift script). W2-92 S9 shows each register chunk's status and changers.
- **What this ticket adds:** the register's own text, which grep and the authority read; the tickets'
  `sources:`; and the status list.
- **Who does what:**
  - **The CTO** applies the patches. The register and the tickets are the orchestrator's (DEC-861).
  - **An independent auditor** checks the free-text marks.
  - **The owner** decides one list.
- **Est.:**
  - the CTO: half a day (215 marks at about 20 to 30 s each, plus two patches);
  - the auditor: about 1 h;
  - the owner: 20 to 30 min.
  - `est_loc` is 0: it changes records, about 260 lines, and no code.
- **What it does not do:**
  - It fixes no code or test. Those go to D-6.
  - It edits no KPI line. That goes to D-9.
  - It rewrites no commit.
  - It changes no status without the owner.

**Filed 2026-11-06 by the CTO** from LINK-INTEGRITY-tickets/W2-130-link-cleanup.md, approved by DEC-1074 (7); placed by D9-FATES (DEC-1083, DEC-1084).

**Reopened 2026-11-14 by the CTO under DEC-1164 (18) and DEC-1156 (7) (a P2 listed for the owner's reading): two decided-behaviour test revisions.** The nightly of 2026-11-14 (red 6, diagnosis `.gov-runtime/scratch/orchestrator/drafts/nightly-20261114/DIAG.md`) found tests that pin a value which moves after the close: W2-130's S8 cases run `gov links` at integrate's HEAD, so every close or reopen moves the counts (122 to 124 CLOSED_TICKET_EDITED in five hours); W2-175's S7 case hashes the templates in the working tree, though its Verify says "at the ticket's head", and an owner-approved change (b88a76172) moved them. Decided: W2-130's two S8 cases run `gov links` at the record's `counts-after.head`; W2-175's S7 case reads each template at W2-175's landing commit (61cae50dc). The paths are widened by W2-175's record test and its support module for that revision only (DEC-1156 (7)); neither record is edited. An independent test designer revises, then a narrow independent check.
