---
id: DRAFT-W2-130
status: open
deps: [DRAFT-W2-129, DAEO-n0wb]
links: []
created: 2026-11-05T00:08:51Z
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
depends_on: [DRAFT-W2-129, DAEO-n0wb]
allowed_paths:
- docs/DECISION_REGISTER.md
- governance/project/orchestration/ARCHIVE-SUPERSEDED.md
- governance/project/orchestration/DECISIONS-IN-FORCE.md
- governance/project/orchestration/packages/LIFT-1/LINK-RECONCILIATION.md
- .tickets/*.md
- docs/lessons/*.md
- docs/research/W2-130-link-cleanup.md
kpis:
  success:
  - 'The 87 first: every decision the census found current, stated changed and with no hint in its own entry names each of its changers on its own status line (**Changed by:** DEC-n (the part), or SUPERSEDED by DEC-n for a whole supersession by ids alone), applied from gov links --propose-marks in a commit of its own [DEC-1073 (5)(a), DEC-866, DEC-825 item 4]'
  - 'Then the rest: after the clean-up, gov links --all reports no UNMARKED_CHANGE on this repository, so each of the census''s 215 drifting decisions names every changer the register or ARCHIVE-SUPERSEDED §A states, the 13 pairs stated only in the archive included; the drift count by docs/research/W2-92-proto-drift.py''s definitions, read from the entries'' own text, is 0 [DEC-1073 (5)(a), DEC-1072 (1)]'
  - 'Checked where the patterns guess: before each marks commit, an independent auditor checks every mark derived from free text, and 20 labelled marks drawn at random, against both entries; a wrong mark is corrected or dropped, never committed; the check is in the record [DEC-1073, DEC-1010]'
  - 'Tickets linked: every id a ticket''s KPI brackets name and every Implements: id of its worker commits is in its sources:, from gov links --propose-sources, in one commit that changes no other field; gov links --all then reports no UNLINKED_ID. Ids that name no record are listed per ticket in the record, for D-9 [DEC-1073 (5)(a)]'
  - 'Commit trailers: history is not rewritten. Every Task: and Implements: value that names no record (the census counted 3,053 of 3,561 Task: values resolving, 496 of the rest decision-record, which is valid under DEC-861; and 4,187 of 4,246 Implements: values) is listed once in the record, with its ticket and the ids it should have named, as DEC-927 did for its 39 [DEC-927, DEC-861, DEC-1073]'
  - 'Status reconciliation, apart from drift: LINK-RECONCILIATION.md lists, for the owner, the 110 decisions ARCHIVE-SUPERSEDED §B calls spent while the register lists them current, the 40 PROPOSED entries, and every STATUS_CONFLICT gov links --all finds. Per id it gives the CTO''s proposal (done, in force, superseded by, accepted or rejected) with its reason. Nothing is applied before the owner decides; then the register carries each decided status (W2-55''s `· done` tag or the status word), and ARCHIVE-SUPERSEDED and DECISIONS-IN-FORCE agree with the register, so gov links --all reports no STATUS_CONFLICT on them [DEC-1073 (2), DEC-953 item 7]'
  - 'Lessons: each lesson in docs/lessons/ names the decision or failure it came from in a sources: key [DEC-1073 (5)(c)]'
  - 'The record, docs/research/W2-130-link-cleanup.md: the counts by finding code and role before and after, the commits, the auditor''s check, the trailer residuals, and what is left by path and role for D-5 (kernel texts), D-6 (code and tests) and D-9 (tickets) [DEC-1073]'
  failure:
  - 'A register entry''s text changed other than its status line''s marks and the owner''s decided statuses; a ticket field other than sources: changed; history rewritten.'
  - 'A status changed before the owner decides the reconciliation list; a spent or PROPOSED decision counted as drift.'
  - 'A free-text mark committed unchecked; a wrong mark committed.'
  - 'The clean-up started before W2-92''s links are adopted, or before W2-129 lands, without the owner''s word.'
profile: STANDARD
sources:
- DEC-1073
- DEC-1072
- DEC-866
- DEC-825
- DEC-927
- DEC-861
- DEC-953
- DEC-1010
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
