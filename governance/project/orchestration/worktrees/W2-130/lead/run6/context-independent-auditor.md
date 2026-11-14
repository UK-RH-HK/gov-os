{
  "ticket": "DAEO-q8cl",
  "ticket_text": "---\nid: DAEO-q8cl\nstatus: in_progress\ndeps: [DAEO-q7lk, DAEO-n0wb]\nlinks: []\ncreated: 2026-11-06T13:56:01Z\ntype: task\npriority: 1\nassignee: orchestrator\nexternal-ref: W2-130\ntags: [wave-2, records, memory, links, standard]\nwbs_id: W2-130\ntitle: 'The link clean-up: every drifting decision marked in its own entry (the 87 with no hint first), tickets linked to the decisions they rest on, commit trailers'' residuals listed, and one status-reconciliation list for the owner (DEC-1073 (5)(a))'\nclass: ops\nstate_class: AUTHORITATIVE\nrole: orchestrator\ndepends_on: [DAEO-q7lk, DAEO-n0wb]\nallowed_paths:\n- docs/DECISION_REGISTER.md\n- governance/project/orchestration/ARCHIVE-SUPERSEDED.md\n- governance/project/orchestration/DECISIONS-IN-FORCE.md\n- governance/project/orchestration/packages/LIFT-1/LINK-RECONCILIATION.md\n- .tickets/*.md\n- docs/lessons/*.md\n- docs/research/W2-130-link-cleanup.md\n- tests/acceptance/W2-175/test_w2_175_record.py\n- tests/acceptance/W2-175/w2_175_support.py\nkpis:\n  success:\n  - 'The 87 first: every decision the census found current, stated changed and with no hint in its own entry names each of its changers on its own status line (**Changed by:** DEC-n (the part), or SUPERSEDED by DEC-n for a whole supersession by ids alone), applied from gov links --propose-marks in a commit of its own [DEC-1073 (5)(a), DEC-866, DEC-825 item 4] [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: tests/acceptance/W2-130/ (written before this ticket''s follow-up commits): for each of the 87 ids the census''s script computes as current, stated changed and with no hint in its own entry (docs/research/D4B-link-census.py at 3d1c459e, run on 24f06026; the ids listed in the record), the entry''s own status line at HEAD names every changer the census states for it, as **Changed by:** DEC-n (the part), or SUPERSEDED by DEC-n for a whole supersession by ids alone, except a pair the independent auditor''s check (S3) judged wrong (DEC-853<-DEC-884, DEC-1050<-DEC-1057), each listed in the record with the auditor''s verdict; the record names e12f8a30c (batches a0, a1, a2 and b1; its parent 232efc47d is the clean-up''s starting head) as the commit that adds the 87''s marks, and every docs/DECISION_REGISTER.md hunk of e12f8a30c is a status-line append only (each removed line an existing entry''s **Status:** line, each added line that line kept whole with marks appended); the marks e12f8a30c adds equal the gov links --propose-marks output it applied (patches a0, a1 and a2, kept beside the record) after the auditor''s drops and rewrites (S3); a mark on one of the 87 added after e12f8a30c is in c4420040f or a follow-up marks commit named in the record, under the same append-only check'\n  - 'Then the rest: after the clean-up, gov links --all reports no UNMARKED_CHANGE on this repository, so each of the census''s 215 drifting decisions names every changer the register or ARCHIVE-SUPERSEDED \u00a7A states, the 13 pairs stated only in the archive included; the drift count by docs/research/W2-92-proto-drift.py''s definitions, read from the entries'' own text, is 0 [DEC-1073 (5)(a), DEC-1072 (1)] [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: tests/acceptance/W2-130/: gov links --all --json on HEAD reports no UNMARKED_CHANGE other than exactly the 8 pairs the earlier independent auditor judged wrong (DEC-853<-DEC-884, DEC-1050<-DEC-1057, DEC-120<-DEC-173, DEC-724<-DEC-860, DEC-056<-DEC-017, DEC-072<-DEC-064, DEC-162<-DEC-156, DEC-1053<-DEC-880), each listed in the record with the auditor''s verdict (P-W2-130-2 (a)); DEC-1115<-DEC-1122 (4) and DEC-026<-DEC-086 are marked on their own status lines at HEAD, each by a follow-up marks commit named in the record that comes after an independent auditor''s check judging the mark right (S3); each of the census''s 215 drifting ids, and each of the 13 pairs stated only in ARCHIVE-SUPERSEDED \u00a7A, has every stated changer named on its own status line at HEAD, except a pair the independent auditor''s check judged wrong, each listed in the record with that verdict; docs/research/W2-92-proto-drift.py''s definitions, applied to the entries'' own text (not a store), give a drift count of 0 once those listed pairs are set aside, the command, its output and the pairs set aside kept in docs/research/W2-130-link-cleanup.md'\n  - 'Checked where the patterns guess: before each marks commit, an independent auditor checks every mark derived from free text, and 20 labelled marks drawn at random, against both entries; a wrong mark is corrected or dropped, never committed; the check is in the record [DEC-1073, DEC-1010] [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: docs/research/W2-130-link-cleanup.md holds, for each marks commit (e12f8a30c, c4420040f and each follow-up marks commit named in the record), the independent auditor''s check, dated before that commit and made at a head that is an ancestor of it (e12f8a30c: the audit at 2f9c80b1f; c4420040f: the audit at ce7f10eb8a2a; both from reviews/w2-130-marks.md): every mark gov links derived from free text (its (text) findings) and 20 labelled marks drawn at random by a stated seed (every labelled mark where the commit adds 20 or fewer), each judged against both entries, with each wrong mark''s fate (corrected or dropped); a comparison of the check with the committed marks finds no committed mark that the check judged wrong and no committed free-text mark that the check does not list'\n  - 'Tickets linked, open and in-progress tickets only: every id an open or in-progress ticket''s KPI brackets name and every Implements: id of its worker commits is in its sources:, from gov links --propose-sources, in one commit that changes no other field; gov links --all then reports no UNLINKED_ID on an open or in-progress ticket. A closed ticket is not edited: its missing ids are listed per ticket in the record. Ids that name no record are listed per ticket in the record, for D-9 [DEC-1073 (5)(a)] [changed, DEC-1098 (3); DEC-1088 (6)] [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: tests/acceptance/W2-130/: gov links --all --json on HEAD reports 0 UNLINKED_ID on any open or in-progress ticket other than the ids the record lists, per ticket, as linked by DEC-1123 (2)''s forms (a backlog row in list_rows, a WBS id whose ticket id is in sources:, DEC-798 through its live DEC-1033), each with how it is linked [S4 re-baselined to DEC-1123 (2), the CTO, P-W2-130-4 (a)]; the record names the sources commits: e12f8a30c (batch b1) and at most one follow-up commit for the UNLINKED_ID that arose after b1; in each, every changed ticket line belongs to the sources: field of a ticket open or in progress at that commit''s parent (every other field and the body of every ticket byte-identical to that commit''s parent), the follow-up changes no other file, and the ids each adds equal gov links --propose-sources'' output at its parent, less the DEC-1123 (2) forms the record lists (for e12f8a30c the b1 patch, kept beside the record); outside those two, a clean-up commit adds to sources: only the ids its owner-decided change names (c4420040f: DEC-1098 and DEC-1088 on this ticket); no closed ticket''s file is changed by a clean-up commit (e12f8a30c, c4420040f and the follow-ups named in the record); the record lists, per closed ticket, its missing ids, and, per ticket, the ids that name no record (for D-9)'\n  - 'Commit trailers: history is not rewritten. Every Task: and Implements: value that names no record (the census counted 3,053 of 3,561 Task: values resolving, 496 of the rest decision-record, which is valid under DEC-861; and 4,187 of 4,246 Implements: values) is listed once in the record, with its ticket and the ids it should have named, as DEC-927 did for its 39 [DEC-927, DEC-861, DEC-1073] [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: docs/research/W2-130-link-cleanup.md lists each Task: and Implements: trailer value in the integration branch''s history at the clean-up''s starting head 232efc47d (e12f8a30c''s parent) that names no record (Task: decision-record excluded as valid under DEC-861) once, with its commit, its ticket and the ids it should have named; a recount over that history''s trailers by the command the record keeps gives the same set of values; 232efc47d is an ancestor of HEAD (git merge-base --is-ancestor), so no history was rewritten'\n  - 'Status reconciliation, apart from drift: LINK-RECONCILIATION.md lists, for the owner, the 110 decisions ARCHIVE-SUPERSEDED \u00a7B calls spent while the register lists them current, the 40 PROPOSED entries, and every STATUS_CONFLICT gov links --all finds. Per id it gives the CTO''s proposal (done, in force, superseded by, accepted or rejected) with its reason. Nothing is applied before the owner decides; then the register carries each decided status (W2-55''s `\u00b7 done` tag or the status word), and ARCHIVE-SUPERSEDED and DECISIONS-IN-FORCE agree with the register, so gov links --all reports no STATUS_CONFLICT on them [DEC-1073 (2), DEC-953 item 7] [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: governance/project/orchestration/packages/W2-130-SITTING.md (committed in 2f9c80b1f, an ancestor of the starting head 232efc47d) lists the 110 ids ARCHIVE-SUPERSEDED \u00a7B at 232efc47d calls spent while the register at 232efc47d lists them current, the 40 PROPOSED entries at 232efc47d and every STATUS_CONFLICT gov links --all reports at 232efc47d (that commit''s gov links, the command and its output kept in the record), each with the CTO''s proposal (done, in force, superseded by, accepted or rejected) and its reason; governance/project/orchestration/packages/LIFT-1/LINK-RECONCILIATION.md exists at HEAD, carries the sitting''s ids with the same proposals and points to W2-130-SITTING.md as the list the owner ruled on; the owner''s decision on the list is DEC-1098 (3), committed in 9546edd61, an ancestor of every clean-up commit that changes a status (c4420040f and any follow-up named in the record); after it, each decided id''s register status at HEAD carries the decision (the \u00b7 done tag or the status word), and tests/acceptance/W2-130/ finds gov links --all --json on HEAD reporting 0 STATUS_CONFLICT on the decided ids between the register, ARCHIVE-SUPERSEDED and DECISIONS-IN-FORCE, after a follow-up commit named in the record rewords DECISIONS-IN-FORCE''s R-12 line so it does not read as listing DEC-896 in force (P-W2-130-3 (a))'\n  - 'Lessons: each lesson in docs/lessons/ names the decision or failure it came from in a sources: key [DEC-1073 (5)(c)] Verify: tests/acceptance/W2-130/: every docs/lessons/*.md at HEAD has a front-matter sources: key naming at least one id, and gov links --all reports no UNKNOWN_ID on a lesson''s sources:; the record lists each lesson with the id its sources: names and the decision or failure its text says it came from, and the two agree'\n  - 'The record, docs/research/W2-130-link-cleanup.md: the counts by finding code and role before and after, the commits, the auditor''s check, the trailer residuals, and what is left by path and role for D-5 (kernel texts), D-6 (code and tests) and D-9 (tickets) [DEC-1073] [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: docs/research/W2-130-link-cleanup.md exists at the close and holds: gov links --all''s counts by finding code and role at the clean-up''s starting head 232efc47d and at its last commit, each with its command; the commit ids of the marks, sources and status commits (e12f8a30c, c4420040f and each follow-up); the auditor''s check (S3); the trailer residuals (S5); and the findings left, by path and role, under D-5 (kernel texts), D-6 (code and tests) and D-9 (tickets); a re-run of gov links --all at the record''s last commit gives the record''s after counts'\n  failure:\n  - 'A register entry''s text changed other than its status line''s marks and the owner''s decided statuses; a ticket field other than sources: changed; history rewritten. [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: tests/acceptance/W2-130/: in the clean-up''s commits (e12f8a30c, c4420040f and the follow-ups named in the record), every changed line of docs/DECISION_REGISTER.md is an existing entry''s status line whose only change is added marks (the old line kept whole, marks appended) or a status DEC-1098 (3) names for that id on W2-130-SITTING.md (c4420040f: the new word first, the old status text kept); every ticket file''s front matter fields other than sources: and its body are byte-identical before and after each of those commits, except c4420040f''s edit of this ticket''s KPI 4 line, owner-decided by DEC-1098 (3) (H1 (b)) and marked [changed, DEC-1098 (3); DEC-1088 (6)]; the clean-up''s starting head 232efc47d is an ancestor of HEAD'\n  - 'A status changed before the owner decides the reconciliation list; a spent or PROPOSED decision counted as drift. [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: no clean-up commit that does not have 9546edd61 (DEC-1098 (3), the owner''s decision on W2-130-SITTING.md, which LINK-RECONCILIATION.md copies and points to) as an ancestor changes a register status word or \u00b7 done tag (e12f8a30c''s register hunks are status-line appends only; git merge-base --is-ancestor for the others); the drift list S2''s command counts at HEAD holds none of the 110 spent ids or the 40 PROPOSED ids that DEC-1098 (3) did not rule current, checked in tests/acceptance/W2-130/ against W2-130-SITTING.md''s ids and rulings'\n  - 'A free-text mark committed unchecked; a wrong mark committed. [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: each mark a clean-up commit (e12f8a30c, c4420040f and each follow-up marks commit named in the record) adds that gov links flagged (text) appears in the auditor''s check (S3) with a verdict of right, dated before that commit and made at a head that is an ancestor of it; no committed mark is one the check judged wrong, among both the free-text marks and the labelled marks it judged; a comparison of the check with each marks commit''s diff, kept in docs/research/W2-130-link-cleanup.md, shows 0 unchecked and 0 wrong'\n  - 'The clean-up started before W2-92''s links are adopted, or before W2-129 lands, without the owner''s word. [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: the record names the clean-up''s first commit, e12f8a30c, and W2-129''s landing commit (DAEO-q7lk, merge 34eed411a) and the commit that adopted W2-92''s stated links (DAEO-n0wb, merge 3679ca0ba) are both its ancestors (git merge-base --is-ancestor); the record also cites DEC-1097 (9), the owner''s decision that allowed the start'\nprofile: STANDARD\nsources:\n- DEC-1073\n- DEC-1109\n- DEC-1072\n- DEC-866\n- DEC-825\n- DEC-927\n- DEC-861\n- DEC-953\n- DEC-1010\n- DEC-1098\n- DEC-1088\n- DEC-1123\nest_loc: 0\nacceptance_tests:\n  path: tests/acceptance/W2-130/\n  author: 'independent-test-designer (MR-3); written before the clean-up: repository-state cases that read HEAD only (seconds, record_reading). gov links --all on HEAD reports 0 UNMARKED_CHANGE and 0 UNLINKED_ID; the drift count by W2-92-proto-drift.py''s definitions from the entries'' text is 0; STATUS_CONFLICT is 0 on the ids the owner decided; every ticket''s field other than sources: is byte-identical to the clean-up''s starting head; the record lists the trailer residuals. The cases name the starting head; they never read the store of another tree.'\ntrack: B\nlist_rows: []\n---\n# W2-130 The link clean-up (DEC-1073 (5)(a))\n\nCard: from DEC-1073 (5)(a): \"Clean up what is here: the 215 drifting decisions, the 87 with no hint in their own entry\nfirst; tickets linked to the decisions they cite; commit trailers linked; the status conflicts.\" The owner's suggestion\nfor the time: right after the graph links are adopted. The plan is\n`governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md` \u00a73.\n\n- **When:** right after re-pin window 4, once W2-92's stated links are in the product and W2-129 has landed.\n- **What the graph already fixed:** retrieval reaches a changer for the 215 (209 to every changer, by the prototype's\n  drift script). W2-92 S9 shows each register chunk's status and changers.\n- **What this ticket adds:** the register's own text, which grep and the authority read; the tickets'\n  `sources:`; and the status list.\n- **Who does what:**\n  - **The CTO** applies the patches. The register and the tickets are the orchestrator's (DEC-861).\n  - **An independent auditor** checks the free-text marks.\n  - **The owner** decides one list.\n- **Est.:**\n  - the CTO: half a day (215 marks at about 20 to 30 s each, plus two patches);\n  - the auditor: about 1 h;\n  - the owner: 20 to 30 min.\n  - `est_loc` is 0: it changes records, about 260 lines, and no code.\n- **What it does not do:**\n  - It fixes no code or test. Those go to D-6.\n  - It edits no KPI line. That goes to D-9.\n  - It rewrites no commit.\n  - It changes no status without the owner.\n\n**Filed 2026-11-06 by the CTO** from LINK-INTEGRITY-tickets/W2-130-link-cleanup.md, approved by DEC-1074 (7); placed by D9-FATES (DEC-1083, DEC-1084).\n\n**Reopened 2026-11-14 by the CTO under DEC-1164 (18) and DEC-1156 (7) (a P2 listed for the owner's reading): two decided-behaviour test revisions.** The nightly of 2026-11-14 (red 6, diagnosis `.gov-runtime/scratch/orchestrator/drafts/nightly-20261114/DIAG.md`) found tests that pin a value which moves after the close: W2-130's S8 cases run `gov links` at integrate's HEAD, so every close or reopen moves the counts (122 to 124 CLOSED_TICKET_EDITED in five hours); W2-175's S7 case hashes the templates in the working tree, though its Verify says \"at the ticket's head\", and an owner-approved change (b88a76172) moved them. Decided: W2-130's two S8 cases run `gov links` at the record's `counts-after.head`; W2-175's S7 case reads each template at W2-175's landing commit (61cae50dc). The paths are widened by W2-175's record test and its support module for that revision only (DEC-1156 (7)); neither record is edited. An independent test designer revises, then a narrow independent check.\n",
  "authority": [
    {
      "id": "DEC-1073",
      "sha256": "c35a4272874e4ccfb5fe307885c0fb94f9880677de63ca13352d31c0ec1d6852",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c35a4272874e4ccfb5fe307885c0fb94f9880677de63ca13352d31c0ec1d6852",
      "reason": "declared in sources",
      "tokens": 1047
    },
    {
      "id": "DEC-1109",
      "sha256": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "reason": "declared in sources",
      "tokens": 468
    },
    {
      "id": "DEC-1072",
      "sha256": "76ab4c349512b436a54241cb5817eddbcc072af662f52a31ac725b005c2d45e5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "76ab4c349512b436a54241cb5817eddbcc072af662f52a31ac725b005c2d45e5",
      "reason": "declared in sources",
      "tokens": 710
    },
    {
      "id": "DEC-866",
      "sha256": "3fd0a96f9624051bf1c77dd154fff18e9c8c62e324c4ad73c0b25f8043e279a1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "3fd0a96f9624051bf1c77dd154fff18e9c8c62e324c4ad73c0b25f8043e279a1",
      "reason": "declared in sources",
      "tokens": 566
    },
    {
      "id": "DEC-825",
      "sha256": "ce77921669f00332dfccc898eaba90bf1ae4f1d9e031ebc3719cdaa9e62446bf",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ce77921669f00332dfccc898eaba90bf1ae4f1d9e031ebc3719cdaa9e62446bf",
      "reason": "declared in sources",
      "tokens": 493
    },
    {
      "id": "DEC-927",
      "sha256": "50e3d8ca7bcb5b239b3e8f994f8d8ff83a705f6b06ded344544ea3c4a436f70e",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "50e3d8ca7bcb5b239b3e8f994f8d8ff83a705f6b06ded344544ea3c4a436f70e",
      "reason": "declared in sources",
      "tokens": 3883
    },
    {
      "id": "DEC-861",
      "sha256": "fcee7f0d5b136cb053b8bae93b299738d8ec278c6034a42037b3a892b4d27839",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "fcee7f0d5b136cb053b8bae93b299738d8ec278c6034a42037b3a892b4d27839",
      "reason": "declared in sources",
      "tokens": 569
    },
    {
      "id": "DEC-953",
      "sha256": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "reason": "declared in sources",
      "tokens": 2188
    },
    {
      "id": "DEC-1010",
      "sha256": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "reason": "declared in sources",
      "tokens": 964
    },
    {
      "id": "DEC-1098",
      "sha256": "22b7bed89cec9021080c8c4c93be6c7b4f029048034f8dcc94eba9004b56fe80",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "22b7bed89cec9021080c8c4c93be6c7b4f029048034f8dcc94eba9004b56fe80",
      "reason": "declared in sources",
      "tokens": 883
    },
    {
      "id": "DEC-1088",
      "sha256": "babbfcb83b2201ee2254f43f2fc13bf013207ed13e05caf2ae80c13d7c852f44",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "babbfcb83b2201ee2254f43f2fc13bf013207ed13e05caf2ae80c13d7c852f44",
      "reason": "declared in sources",
      "tokens": 769
    },
    {
      "id": "DEC-1123",
      "sha256": "1e42f7feb0377e9a30280e9c74bc116b387282689bc96e495fe2afb9ca34a40f",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1e42f7feb0377e9a30280e9c74bc116b387282689bc96e495fe2afb9ca34a40f",
      "reason": "declared in sources",
      "tokens": 603
    },
    {
      "id": "DAEO-q7lk",
      "sha256": "ba1a91df605c1fe131d4c51b1c6d1fafc309363be57b375535cc24e6e3248300",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "ba1a91df605c1fe131d4c51b1c6d1fafc309363be57b375535cc24e6e3248300",
      "reason": "declared in sources",
      "tokens": 2274
    },
    {
      "id": "DAEO-n0wb",
      "sha256": "afb7603d16208a09fd077a4216a949c2e143a5cd9f1efca5f22cc911c79efddf",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "afb7603d16208a09fd077a4216a949c2e143a5cd9f1efca5f22cc911c79efddf",
      "reason": "declared in sources",
      "tokens": 1353
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1073",
      "sha256": "c35a4272874e4ccfb5fe307885c0fb94f9880677de63ca13352d31c0ec1d6852",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c35a4272874e4ccfb5fe307885c0fb94f9880677de63ca13352d31c0ec1d6852",
      "reason": "declared in sources",
      "tokens": 1047
    },
    {
      "id": "DEC-1109",
      "sha256": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "reason": "declared in sources",
      "tokens": 468
    },
    {
      "id": "DEC-1072",
      "sha256": "76ab4c349512b436a54241cb5817eddbcc072af662f52a31ac725b005c2d45e5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "76ab4c349512b436a54241cb5817eddbcc072af662f52a31ac725b005c2d45e5",
      "reason": "declared in sources",
      "tokens": 710
    },
    {
      "id": "DEC-866",
      "sha256": "3fd0a96f9624051bf1c77dd154fff18e9c8c62e324c4ad73c0b25f8043e279a1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "3fd0a96f9624051bf1c77dd154fff18e9c8c62e324c4ad73c0b25f8043e279a1",
      "reason": "declared in sources",
      "tokens": 566
    },
    {
      "id": "DEC-825",
      "sha256": "ce77921669f00332dfccc898eaba90bf1ae4f1d9e031ebc3719cdaa9e62446bf",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ce77921669f00332dfccc898eaba90bf1ae4f1d9e031ebc3719cdaa9e62446bf",
      "reason": "declared in sources",
      "tokens": 493
    },
    {
      "id": "DEC-927",
      "sha256": "50e3d8ca7bcb5b239b3e8f994f8d8ff83a705f6b06ded344544ea3c4a436f70e",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "50e3d8ca7bcb5b239b3e8f994f8d8ff83a705f6b06ded344544ea3c4a436f70e",
      "reason": "declared in sources",
      "tokens": 3883
    },
    {
      "id": "DEC-861",
      "sha256": "fcee7f0d5b136cb053b8bae93b299738d8ec278c6034a42037b3a892b4d27839",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "fcee7f0d5b136cb053b8bae93b299738d8ec278c6034a42037b3a892b4d27839",
      "reason": "declared in sources",
      "tokens": 569
    },
    {
      "id": "DEC-953",
      "sha256": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "reason": "declared in sources",
      "tokens": 2188
    },
    {
      "id": "DEC-1010",
      "sha256": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "reason": "declared in sources",
      "tokens": 964
    },
    {
      "id": "DEC-1098",
      "sha256": "22b7bed89cec9021080c8c4c93be6c7b4f029048034f8dcc94eba9004b56fe80",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "22b7bed89cec9021080c8c4c93be6c7b4f029048034f8dcc94eba9004b56fe80",
      "reason": "declared in sources",
      "tokens": 883
    },
    {
      "id": "DEC-1088",
      "sha256": "babbfcb83b2201ee2254f43f2fc13bf013207ed13e05caf2ae80c13d7c852f44",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "babbfcb83b2201ee2254f43f2fc13bf013207ed13e05caf2ae80c13d7c852f44",
      "reason": "declared in sources",
      "tokens": 769
    },
    {
      "id": "DEC-1123",
      "sha256": "1e42f7feb0377e9a30280e9c74bc116b387282689bc96e495fe2afb9ca34a40f",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1e42f7feb0377e9a30280e9c74bc116b387282689bc96e495fe2afb9ca34a40f",
      "reason": "declared in sources",
      "tokens": 603
    },
    {
      "id": "DAEO-q7lk",
      "sha256": "ba1a91df605c1fe131d4c51b1c6d1fafc309363be57b375535cc24e6e3248300",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "ba1a91df605c1fe131d4c51b1c6d1fafc309363be57b375535cc24e6e3248300",
      "reason": "declared in sources",
      "tokens": 2274
    },
    {
      "id": "DAEO-n0wb",
      "sha256": "afb7603d16208a09fd077a4216a949c2e143a5cd9f1efca5f22cc911c79efddf",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "afb7603d16208a09fd077a4216a949c2e143a5cd9f1efca5f22cc911c79efddf",
      "reason": "declared in sources",
      "tokens": 1353
    }
  ],
  "supplementary": [
    {
      "id": "DRAFT-W2-130",
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY-tickets/W2-130-link-cleanup.md",
      "text": "---\nid: DRAFT-W2-130\nstatus: open\ndeps: [DRAFT-W2-129, DAEO-n0wb]\nlinks: []\ncreated: 2026-11-05T00:08:51Z\ntype: task\npriority: 1\nassignee: orchestrator\nexternal-ref: W2-130\ntags: [wave-2, records, memory, links, standard]\nwbs_id: W2-130\ntitle: 'The link clean-up: every drifting decision marked in its own entry (the 87 with no hint first), tickets linked to the decisions they rest on, commit trailers'' residuals listed, and one status-reconciliation list for the owner (DEC-1073 (5)(a))'\nclass: ops\nstate_class: AUTHORITATIVE\nrole: orchestrator\ndepends_on: [DRAFT-W2-129, DAEO-n0wb]\nallowed_paths:\n- docs/DECISION_REGISTER.md\n- governance/project/orchestration/ARCHIVE-SUPERSEDED.md\n- governance/project/orchestration/DECISIONS-IN-FORCE.md\n- governance/project/orchestration/packages/LIFT-1/LINK-RECONCILIATION.md\n- .tickets/*.md\n- docs/lessons/*.md\n- docs/research/W2-130-link-cleanup.md\nkpis:\n  success:\n",
      "tokens": 228
    },
    {
      "id": "WAVE-2-WBS",
      "path": "docs/plan/WAVE_2_WBS.md",
      "text": "#### W2-130 The link clean-up: every drifting decision marked in its own entry (the 87 with no hint first), tickets linked to the decisions they rest on, commit trailers' residuals listed, and one status-reconciliation list for the owner (DEC-1073 (5)(a)) (STANDARD, orchestrator)\n- **Ticket file:** `DAEO-q8cl` (open); its KPIs, paths and sources are there.\n\n",
      "tokens": 90
    },
    {
      "id": "dc19f31f307571825b836ab1",
      "path": "governance/project/orchestration/DECISIONS-IN-FORCE.md",
      "text": "- DEC-1072 (2026-11-04): D4B-STRUCTURE's order stands; its steps 5-7 are prototypes in measure clones only, back to\n  the owner with figures before any product change. **Step 7 covers every stated link:** a census of each kind of\n  relationship stated (records, front matter, trailers, text) against the graph's edges; the missing kinds built as\n  the evidence supports; a drift count (decisions retrievable as current though superseded or amended). **Memory-building\n  is a Wave 0 practice** for every adopted repository, kept in its ticket as D-4b goes, a kernel skill after the\n  refactoring.\n- DEC-1073 (2026-11-04; its \"within 3 points\" is now 5, DEC-1074 (4)): the measurement set is used once, **after the structure is final** (D4B-STRUCTURE steps 2 and\n  4-7 measured first), and only if the halves still agree within 3 points; otherwise to the owner. **Drift:** the\n  register is the authority. The archive's 110 \"spent\" decisions go to a separate status-reconciliation list. A\n  PROPOSED decision is not current, and retrieval must show its status. M5 is retested with the register links.\n",
      "tokens": 275
    },
    {
      "id": "224e24a22db4d9c55fd16f55",
      "path": "docs/research/W2-130-link-cleanup.md",
      "text": "DEC-1115's item, so the mark names DEC-1122 (2) with item (4) in words; F2: DEC-086 settles DEC-026 \"for Wave 1\").\nbce798c3a commits them in the corrected texts, after the check (2026-11-13T22:46:14Z, at 09542040f, an ancestor).\n\n**The drift count (S2).** `docs/research/W2-92-proto-drift.py`'s definitions, applied to the entries' own text\n(no store): 6 pairs at the last clean-up commit, every one of them a pair the auditor judged wrong,\nso the count after setting them aside is 0. None of the sitting's group C, D or E ids is current, so none is counted.\n\n```python w2-130:drift\n\"\"\"W2-130 S2: the drift count by docs/research/W2-92-proto-drift.py's definitions, read from the entries' own text.\n\nRun from the repository's root as `python3 -` (this script on stdin); no store is read and nothing is written.\nThe definitions are W2-92-proto-drift.py's (the census's, D4B-link-census.py at 3d1c459e): a statement is a register\nlabel, its free text or the change log (loader.register_statements) or an ARCHIVE-SUPERSEDED \u00a7A line read with the\nsame patterns; a decision is current when its status is ACCEPTED and no SUPERSEDES edge targets it (the records and\n",
      "tokens": 290
    },
    {
      "id": "f1accb5de52b7349303f228e",
      "path": "tests/acceptance/W2-92/test_w2_92_drift.py",
      "text": "\"\"\"KPI success 10 (DEC-1072 (1)): the drift count before and after, by the census's definitions.\n\nThe count itself (``docs/research/W2-92-proto-drift.py`` on the rebuilt store: of the decisions current though stated\nchanged, how many a search reaching the decision also reaches a changer of) is a measure on this repository's store,\nthe CTO's, verified by the evidence file. This case checks only that the measure record holds it: a section of\n``docs/research/W2-92-memory-measure.md`` whose heading names drift, giving a count before and a count after, and\nnaming the census whose definitions it uses (``D4B-link-census``).\n\"\"\"\n\nfrom __future__ import annotations\n\nimport re\n\nimport w2_92_support as support\n\nRECORD = support.REPO_ROOT / \"docs/research/W2-92-memory-measure.md\"\n\n\n",
      "tokens": 196
    },
    {
      "id": "734e3a8e27dd1507cb25e1c8",
      "path": "docs/research/W2-130-link-cleanup.md",
      "text": "## 2. The commits\n\n| commit | what | lists |\n|---|---|---|\n| `e12f8a30ca7d` | batches a1, a2 (the marks: the 87 first, then the rest), a0 (the archive's line 34, one decision per line), b1 (50 open and in-progress tickets' `sources:`) | marks, sources |\n| `c4420040f9b3` | after the owner's sitting (DEC-1098 (3)): the decided status words, the a3 marks, this ticket's KPI 4 line and its `sources:` DEC-1098 and DEC-1088 | marks, status |\n| `8d245901b239` | follow-up (2): DECISIONS-IN-FORCE's R-12 line reworded (P-W2-130-3 (a)) | status, r12 |\n| `8f8d707f0bd0` | follow-up (3): each lesson's `sources:` key (DEC-1073 (5)(c)) | lessons |\n| `bce798c3a911` | follow-up (4): the two marks the auditor passed, DEC-1115<-DEC-1122 and DEC-026<-DEC-086 | marks |\n| `57cbacfbfc86` | follow-up (1): the open and in-progress tickets' `sources:` from `gov links --propose-sources`, less DEC-1123 (2)'s forms (P-W2-130-4 (a)) | sources |\n\nThe follow-ups are numbered as the plan numbered them; (1) was made last, after the CTO's answer to P-W2-130-4. Each\nchanges one kind of file and nothing else. This record and LINK-RECONCILIATION.md are committed after them and are\nnot clean-up commits.\n\n",
      "tokens": 296
    },
    {
      "id": "248cda39bd7114c49564c18c",
      "path": "docs/research/W2-130-link-cleanup.md",
      "text": "## 7. The status reconciliation (S6, F2)\n\n- **The list:** `governance/project/orchestration/packages/W2-130-SITTING.md` (committed in 2f9c80b1f, an ancestor\n  of the starting head): the 110 decisions ARCHIVE-SUPERSEDED \u00a7B called spent while the register listed them\n  current, the 40 PROPOSED entries, and the STATUS_CONFLICT findings (116 at 232efc47d), each with the CTO's\n  proposal and its reason.\n- **The ruling:** DEC-1098 (3), committed in 9546edd61: groups A to G accepted as proposed; H1 (b); H2 as\n  recommended.\n- **Applied:** c4420040f writes each decided status (the new word first, the old status text kept); the archive and\n  DECISIONS-IN-FORCE agree; the R-12 follow-up (8d245901b) rewords the one line that read as listing the done\n  DEC-896 in force.\n- **After:** STATUS_CONFLICT 0.\n- LINK-RECONCILIATION.md (`governance/project/orchestration/packages/LIFT-1/`) carries the sitting's 150 rows with\n  their proposals, reasons and rulings.\n\n",
      "tokens": 240
    },
    {
      "id": "DRAFT-W2-130",
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY-tickets/W2-130-link-cleanup.md",
      "text": "  - 'Commit trailers: history is not rewritten. Every Task: and Implements: value that names no record (the census counted 3,053 of 3,561 Task: values resolving, 496 of the rest decision-record, which is valid under DEC-861; and 4,187 of 4,246 Implements: values) is listed once in the record, with its ticket and the ids it should have named, as DEC-927 did for its 39 [DEC-927, DEC-861, DEC-1073]'\n  - 'Status reconciliation, apart from drift: LINK-RECONCILIATION.md lists, for the owner, the 110 decisions ARCHIVE-SUPERSEDED \u00a7B calls spent while the register lists them current, the 40 PROPOSED entries, and every STATUS_CONFLICT gov links --all finds. Per id it gives the CTO''s proposal (done, in force, superseded by, accepted or rejected) with its reason. Nothing is applied before the owner decides; then the register carries each decided status (W2-55''s `\u00b7 done` tag or the status word), and ARCHIVE-SUPERSEDED and DECISIONS-IN-FORCE agree with the register, so gov links --all reports no STATUS_CONFLICT on them [DEC-1073 (2), DEC-953 item 7]'\n  - 'Lessons: each lesson in docs/lessons/ names the decision or failure it came from in a sources: key [DEC-1073 (5)(c)]'\n",
      "tokens": 295
    },
    {
      "id": "b4238c46c958a88187f73410",
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-RECONCILIATION.md",
      "text": "# LINK-RECONCILIATION: the status reconciliation the owner ruled on (W2-130, DEC-1073 (2), (5)(a))\n\n**The list the owner ruled on:** `governance/project/orchestration/packages/W2-130-SITTING.md` (committed in\n2f9c80b1f). **The ruling:** DEC-1098 (3) (the owner, 2026-11-09, committed in 9546edd61): groups A to G accepted as\nproposed; H1 (b), open and in-progress tickets only; H2 as recommended. **Applied:** c4420040f (the decided status\nwords, the archive, this ticket's KPI 4) and 8d245901b (DECISIONS-IN-FORCE's R-12 line). The record is\n`docs/research/W2-130-link-cleanup.md`.\n\nThe 150 rows below are the sitting's groups A to F, one per decision: the 40 PROPOSED entries (A, B, C) and the 110\nthe archive called spent while the register listed them current (D, E, F). The proposal and the reason are the\nsitting row's Proposal and Evidence columns, verbatim. Groups G (four rows the readiness review added, no status word\nchanged) and H (the two choices) carry no decision id; their rulings are in DEC-1098 (3) and in the sitting file.\n\n| Decision | Group | Proposal | Reason | Ruling |\n|---|---|---|---|---|\n",
      "tokens": 279
    },
    {
      "id": "DRAFT-W2-130",
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY-tickets/W2-130-link-cleanup.md",
      "text": "- DEC-866\n- DEC-825\n- DEC-927\n- DEC-861\n- DEC-953\n- DEC-1010\nest_loc: 0\nacceptance_tests:\n  path: tests/acceptance/W2-130/\n  author: 'independent-test-designer (MR-3); written before the clean-up: repository-state cases that read HEAD only (seconds, record_reading). gov links --all on HEAD reports 0 UNMARKED_CHANGE and 0 UNLINKED_ID; the drift count by W2-92-proto-drift.py''s definitions from the entries'' text is 0; STATUS_CONFLICT is 0 on the ids the owner decided; every ticket''s field other than sources: is byte-identical to the clean-up''s starting head; the record lists the trailer residuals. The cases name the starting head; they never read the store of another tree.'\ntrack: B\nlist_rows: []\n---\n",
      "tokens": 178
    },
    {
      "id": "c50c10082cbaa88cfe946b36",
      "path": "tests/acceptance/W2-130/README.md",
      "text": "| S6 | `test_w2_130_status.py::test_s6_the_r_12_commit_changes_only_decisions_in_force_and_only_its_r_12_line` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |\n| S6 | `test_w2_130_status.py::test_s6_linkreconciliation_names_the_sitting_file_and_dec_1098_3_and_carries_each_sitting_row` | red | LINK-RECONCILIATION.md does not exist at HEAD |\n| S7 | `test_w2_130_lessons.py::test_s7_every_lesson_at_head_has_a_front_matter_sources_key_naming_at_least_one_id` | red | none of the 5 lessons has a `sources:` key |\n| S7 | `test_w2_130_lessons.py::test_s7_gov_links_reports_no_unknown_id_with_a_lesson_s_path` | green | green by design: history only (the commits and the sitting file as they are in git) |\n| S7 | `test_w2_130_lessons.py::test_s7_the_record_lists_each_lesson_with_its_sources_and_the_place_it_says_it_came_from` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |\n",
      "tokens": 260
    }
  ],
  "supplementary_query": "The link clean-up: every drifting decision marked in its own entry (the 87 with no hint first), tickets linked to the decisions they rest on, commit trailers' residuals listed, and one status-reconciliation list for the owner (DEC-1073 (5)(a))\nThe 87 first: every decision the census found current, stated changed and with no hint in its own entry names each of its changers on its own status line (**Changed by:** DEC-n (the part), or SUPERSEDED by DEC-n for a whole supersession by ids alone), applied from gov links --propose-marks in a commit of its own [DEC-1073 (5)(a), DEC-866, DEC-825 item 4] [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: tests/acceptance/W2-130/ (written before this ticket's follow-up commits): for each of the 87 ids the census's script computes as current, stated changed and with no hint in its own entry (docs/research/D4B-link-census.py at 3d1c459e, run on 24f06026; the ids listed in the record), the entry's own status line at HEAD names every changer the census states for it, as **Changed by:** DEC-n (the part), or SUPERSEDED by DEC-n for a whole supersession by ids alone, except a pair the independent auditor's check (S3) judged wrong (DEC-853<-DEC-884, DEC-1050<-DEC-1057), each listed in the record with the auditor's verdict; the record names e12f8a30c (batches a0, a1, a2 and b1; its parent 232efc47d is the clean-up's starting head) as the commit that adds the 87's marks, and every docs/DECISION_REGISTER.md hunk of e12f8a30c is a status-line append only (each removed line an existing entry's **Status:** line, each added line that line kept whole with marks appended); the marks e12f8a30c adds equal the gov links --propose-marks output it applied (patches a0, a1 and a2, kept beside the record) after the auditor's drops and rewrites (S3); a mark on one of the 87 added after e12f8a30c is in c4420040f or a follow-up marks commit named in the record, under the same append-only check\nThen the rest: after the clean-up, gov links --all reports no UNMARKED_CHANGE on this repository, so each of the census's 215 drifting decisions names every changer the register or ARCHIVE-SUPERSEDED \u00a7A states, the 13 pairs stated only in the archive included; the drift count by docs/research/W2-92-proto-drift.py's definitions, read from the entries' own text, is 0 [DEC-1073 (5)(a), DEC-1072 (1)] [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: tests/acceptance/W2-130/: gov links --all --json on HEAD reports no UNMARKED_CHANGE other than exactly the 8 pairs the earlier independent auditor judged wrong (DEC-853<-DEC-884, DEC-1050<-DEC-1057, DEC-120<-DEC-173, DEC-724<-DEC-860, DEC-056<-DEC-017, DEC-072<-DEC-064, DEC-162<-DEC-156, DEC-1053<-DEC-880), each listed in the record with the auditor's verdict (P-W2-130-2 (a)); DEC-1115<-DEC-1122 (4) and DEC-026<-DEC-086 are marked on their own status lines at HEAD, each by a follow-up marks commit named in the record that comes after an independent auditor's check judging the mark right (S3); each of the census's 215 drifting ids, and each of the 13 pairs stated only in ARCHIVE-SUPERSEDED \u00a7A, has every stated changer named on its own status line at HEAD, except a pair the independent auditor's check judged wrong, each listed in the record with that verdict; docs/research/W2-92-proto-drift.py's definitions, applied to the entries' own text (not a store), give a drift count of 0 once those listed pairs are set aside, the command, its output and the pairs set aside kept in docs/research/W2-130-link-cleanup.md\nChecked where the patterns guess: before each marks commit, an independent auditor checks every mark derived from free text, and 20 labelled marks drawn at random, against both entries; a wrong mark is corrected or dropped, never committed; the check is in the record [DEC-1073, DEC-1010] [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: docs/research/W2-130-link-cleanup.md holds, for each marks commit (e12f8a30c, c4420040f and each follow-up marks commit named in the record), the independent auditor's check, dated before that commit and made at a head that is an ancestor of it (e12f8a30c: the audit at 2f9c80b1f; c4420040f: the audit at ce7f10eb8a2a; both from reviews/w2-130-marks.md): every mark gov links derived from free text (its (text) findings) and 20 labelled marks drawn at random by a stated seed (every labelled mark where the commit adds 20 or fewer), each judged against both entries, with each wrong mark's fate (corrected or dropped); a comparison of the check with the committed marks finds no committed mark that the check judged wrong and no committed free-text mark that the check does not list\nTickets linked, open and in-progress tickets only: every id an open or in-progress ticket's KPI brackets name and every Implements: id of its worker commits is in its sources:, from gov links --propose-sources, in one commit that changes no other field; gov links --all then reports no UNLINKED_ID on an open or in-progress ticket. A closed ticket is not edited: its missing ids are listed per ticket in the record. Ids that name no record are listed per ticket in the record, for D-9 [DEC-1073 (5)(a)] [changed, DEC-1098 (3); DEC-1088 (6)] [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: tests/acceptance/W2-130/: gov links --all --json on HEAD reports 0 UNLINKED_ID on any open or in-progress ticket other than the ids the record lists, per ticket, as linked by DEC-1123 (2)'s forms (a backlog row in list_rows, a WBS id whose ticket id is in sources:, DEC-798 through its live DEC-1033), each with how it is linked [S4 re-baselined to DEC-1123 (2), the CTO, P-W2-130-4 (a)]; the record names the sources commits: e12f8a30c (batch b1) and at most one follow-up commit for the UNLINKED_ID that arose after b1; in each, every changed ticket line belongs to the sources: field of a ticket open or in progress at that commit's parent (every other field and the body of every ticket byte-identical to that commit's parent), the follow-up changes no other file, and the ids each adds equal gov links --propose-sources' output at its parent, less the DEC-1123 (2) forms the record lists (for e12f8a30c the b1 patch, kept beside the record); outside those two, a clean-up commit adds to sources: only the ids its owner-decided change names (c4420040f: DEC-1098 and DEC-1088 on this ticket); no closed ticket's file is changed by a clean-up commit (e12f8a30c, c4420040f and the follow-ups named in the record); the record lists, per closed ticket, its missing ids, and, per ticket, the ids that name no record (for D-9)\nCommit trailers: history is not rewritten. Every Task: and Implements: value that names no record (the census counted 3,053 of 3,561 Task: values resolving, 496 of the rest decision-record, which is valid under DEC-861; and 4,187 of 4,246 Implements: values) is listed once in the record, with its ticket and the ids it should have named, as DEC-927 did for its 39 [DEC-927, DEC-861, DEC-1073] [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: docs/research/W2-130-link-cleanup.md lists each Task: and Implements: trailer value in the integration branch's history at the clean-up's starting head 232efc47d (e12f8a30c's parent) that names no record (Task: decision-record excluded as valid under DEC-861) once, with its commit, its ticket and the ids it should have named; a recount over that history's trailers by the command the record keeps gives the same set of values; 232efc47d is an ancestor of HEAD (git merge-base --is-ancestor), so no history was rewritten\nStatus reconciliation, apart from drift: LINK-RECONCILIATION.md lists, for the owner, the 110 decisions ARCHIVE-SUPERSEDED \u00a7B calls spent while the register lists them current, the 40 PROPOSED entries, and every STATUS_CONFLICT gov links --all finds. Per id it gives the CTO's proposal (done, in force, superseded by, accepted or rejected) with its reason. Nothing is applied before the owner decides; then the register carries each decided status (W2-55's `\u00b7 done` tag or the status word), and ARCHIVE-SUPERSEDED and DECISIONS-IN-FORCE agree with the register, so gov links --all reports no STATUS_CONFLICT on them [DEC-1073 (2), DEC-953 item 7] [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: governance/project/orchestration/packages/W2-130-SITTING.md (committed in 2f9c80b1f, an ancestor of the starting head 232efc47d) lists the 110 ids ARCHIVE-SUPERSEDED \u00a7B at 232efc47d calls spent while the register at 232efc47d lists them current, the 40 PROPOSED entries at 232efc47d and every STATUS_CONFLICT gov links --all reports at 232efc47d (that commit's gov links, the command and its output kept in the record), each with the CTO's proposal (done, in force, superseded by, accepted or rejected) and its reason; governance/project/orchestration/packages/LIFT-1/LINK-RECONCILIATION.md exists at HEAD, carries the sitting's ids with the same proposals and points to W2-130-SITTING.md as the list the owner ruled on; the owner's decision on the list is DEC-1098 (3), committed in 9546edd61, an ancestor of every clean-up commit that changes a status (c4420040f and any follow-up named in the record); after it, each decided id's register status at HEAD carries the decision (the \u00b7 done tag or the status word), and tests/acceptance/W2-130/ finds gov links --all --json on HEAD reporting 0 STATUS_CONFLICT on the decided ids between the register, ARCHIVE-SUPERSEDED and DECISIONS-IN-FORCE, after a follow-up commit named in the record rewords DECISIONS-IN-FORCE's R-12 line so it does not read as listing DEC-896 in force (P-W2-130-3 (a))\nLessons: each lesson in docs/lessons/ names the decision or failure it came from in a sources: key [DEC-1073 (5)(c)] Verify: tests/acceptance/W2-130/: every docs/lessons/*.md at HEAD has a front-matter sources: key naming at least one id, and gov links --all reports no UNKNOWN_ID on a lesson's sources:; the record lists each lesson with the id its sources: names and the decision or failure its text says it came from, and the two agree\nThe record, docs/research/W2-130-link-cleanup.md: the counts by finding code and role before and after, the commits, the auditor's check, the trailer residuals, and what is left by path and role for D-5 (kernel texts), D-6 (code and tests) and D-9 (tickets) [DEC-1073] [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: docs/research/W2-130-link-cleanup.md exists at the close and holds: gov links --all's counts by finding code and role at the clean-up's starting head 232efc47d and at its last commit, each with its command; the commit ids of the marks, sources and status commits (e12f8a30c, c4420040f and each follow-up); the auditor's check (S3); the trailer residuals (S5); and the findings left, by path and role, under D-5 (kernel texts), D-6 (code and tests) and D-9 (tickets); a re-run of gov links --all at the record's last commit gives the record's after counts\nA register entry's text changed other than its status line's marks and the owner's decided statuses; a ticket field other than sources: changed; history rewritten. [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: tests/acceptance/W2-130/: in the clean-up's commits (e12f8a30c, c4420040f and the follow-ups named in the record), every changed line of docs/DECISION_REGISTER.md is an existing entry's status line whose only change is added marks (the old line kept whole, marks appended) or a status DEC-1098 (3) names for that id on W2-130-SITTING.md (c4420040f: the new word first, the old status text kept); every ticket file's front matter fields other than sources: and its body are byte-identical before and after each of those commits, except c4420040f's edit of this ticket's KPI 4 line, owner-decided by DEC-1098 (3) (H1 (b)) and marked [changed, DEC-1098 (3); DEC-1088 (6)]; the clean-up's starting head 232efc47d is an ancestor of HEAD\nA status changed before the owner decides the reconciliation list; a spent or PROPOSED decision counted as drift. [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: no clean-up commit that does not have 9546edd61 (DEC-1098 (3), the owner's decision on W2-130-SITTING.md, which LINK-RECONCILIATION.md copies and points to) as an ancestor changes a register status word or \u00b7 done tag (e12f8a30c's register hunks are status-line appends only; git merge-base --is-ancestor for the others); the drift list S2's command counts at HEAD holds none of the 110 spent ids or the 40 PROPOSED ids that DEC-1098 (3) did not rule current, checked in tests/acceptance/W2-130/ against W2-130-SITTING.md's ids and rulings\nA free-text mark committed unchecked; a wrong mark committed. [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: each mark a clean-up commit (e12f8a30c, c4420040f and each follow-up marks commit named in the record) adds that gov links flagged (text) appears in the auditor's check (S3) with a verdict of right, dated before that commit and made at a head that is an ancestor of it; no committed mark is one the check judged wrong, among both the free-text marks and the labelled marks it judged; a comparison of the check with each marks commit's diff, kept in docs/research/W2-130-link-cleanup.md, shows 0 unchecked and 0 wrong\nThe clean-up started before W2-92's links are adopted, or before W2-129 lands, without the owner's word. [Verify re-baselined to history, the CTO, P-W2-130-1 (a)] Verify: the record names the clean-up's first commit, e12f8a30c, and W2-129's landing commit (DAEO-q7lk, merge 34eed411a) and the commit that adopted W2-92's stated links (DAEO-n0wb, merge 3679ca0ba) are both its ancestors (git merge-base --is-ancestor); the record also cites DEC-1097 (9), the owner's decision that allowed the start",
  "further_batch": [
    {
      "id": "0942897fa2557aa2d9329d86",
      "path": "tests/acceptance/W2-130/w2_130_support.py"
    },
    {
      "id": "DRAFT-W2-130",
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY-tickets/W2-130-link-cleanup.md"
    },
    {
      "id": "6586c146da60021c6fbf7e0f",
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md"
    },
    {
      "id": "1443c1945ce63aa586fa8f61",
      "path": "docs/research/W2-129-links.md"
    },
    {
      "id": "b2621875abddeae54674b370",
      "path": "docs/research/W2-92-proto-drift.py"
    },
    {
      "id": "c26e1529f1d64e14114fcb86",
      "path": "tests/acceptance/W2-129/README.md"
    },
    {
      "id": "301dc852a348c005826fa415",
      "path": "docs/research/W2-92-memory-measure.md"
    },
    {
      "id": "69701b7a8bfa9fadb4956894",
      "path": "docs/research/W2-92-proto-drift.py"
    },
    {
      "id": "76ace44025dd3adecea93ba0",
      "path": "docs/research/W2-129-links.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "DRAFT-W2-130",
          "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY-tickets/W2-130-link-cleanup.md"
        },
        {
          "id": "WAVE-2-WBS",
          "path": "docs/plan/WAVE_2_WBS.md"
        },
        {
          "id": "dc19f31f307571825b836ab1",
          "path": "governance/project/orchestration/DECISIONS-IN-FORCE.md"
        },
        {
          "id": "224e24a22db4d9c55fd16f55",
          "path": "docs/research/W2-130-link-cleanup.md"
        },
        {
          "id": "f1accb5de52b7349303f228e",
          "path": "tests/acceptance/W2-92/test_w2_92_drift.py"
        },
        {
          "id": "734e3a8e27dd1507cb25e1c8",
          "path": "docs/research/W2-130-link-cleanup.md"
        },
        {
          "id": "248cda39bd7114c49564c18c",
          "path": "docs/research/W2-130-link-cleanup.md"
        },
        {
          "id": "DRAFT-W2-130",
          "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY-tickets/W2-130-link-cleanup.md"
        },
        {
          "id": "b4238c46c958a88187f73410",
          "path": "governance/project/orchestration/packages/LIFT-1/LINK-RECONCILIATION.md"
        },
        {
          "id": "DRAFT-W2-130",
          "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY-tickets/W2-130-link-cleanup.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "c50c10082cbaa88cfe946b36",
          "path": "tests/acceptance/W2-130/README.md"
        },
        {
          "id": "0942897fa2557aa2d9329d86",
          "path": "tests/acceptance/W2-130/w2_130_support.py"
        },
        {
          "id": "DRAFT-W2-130",
          "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY-tickets/W2-130-link-cleanup.md"
        },
        {
          "id": "6586c146da60021c6fbf7e0f",
          "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md"
        },
        {
          "id": "1443c1945ce63aa586fa8f61",
          "path": "docs/research/W2-129-links.md"
        },
        {
          "id": "b2621875abddeae54674b370",
          "path": "docs/research/W2-92-proto-drift.py"
        },
        {
          "id": "c26e1529f1d64e14114fcb86",
          "path": "tests/acceptance/W2-129/README.md"
        },
        {
          "id": "301dc852a348c005826fa415",
          "path": "docs/research/W2-92-memory-measure.md"
        },
        {
          "id": "69701b7a8bfa9fadb4956894",
          "path": "docs/research/W2-92-proto-drift.py"
        },
        {
          "id": "76ace44025dd3adecea93ba0",
          "path": "docs/research/W2-129-links.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "0942897fa2557aa2d9329d86",
      "reason": "budget exceeded"
    },
    {
      "id": "1443c1945ce63aa586fa8f61",
      "reason": "budget exceeded"
    },
    {
      "id": "301dc852a348c005826fa415",
      "reason": "budget exceeded"
    },
    {
      "id": "6586c146da60021c6fbf7e0f",
      "reason": "budget exceeded"
    },
    {
      "id": "69701b7a8bfa9fadb4956894",
      "reason": "budget exceeded"
    },
    {
      "id": "76ace44025dd3adecea93ba0",
      "reason": "budget exceeded"
    },
    {
      "id": "DRAFT-W2-130",
      "reason": "budget exceeded"
    },
    {
      "id": "b2621875abddeae54674b370",
      "reason": "budget exceeded"
    },
    {
      "id": "c26e1529f1d64e14114fcb86",
      "reason": "budget exceeded"
    }
  ],
  "tokens": 23933,
  "budget": {
    "limit": 24000,
    "used": 23933
  },
  "left_out": {
    "count": 3,
    "superseded": [
      "DEC-869",
      "DEC-876",
      "DEC-960"
    ],
    "done": []
  },
  "hash": "45e9ba404d0b68fe656186c479da937bcd54ab4682d23755a79a2e32a0b3cf33"
}
