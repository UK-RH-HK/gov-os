---
id: DAEO-6oj6
wbs_id: W2-190
external-ref: W2-190
title: "A3 refuses DELETE_FROM_ACTIVE_TREE of a file another tracked file references, or one classed superseded"
type: task
class: implementation
role: engineer
profile: STANDARD
status: closed
state_class: AUTHORITATIVE
priority: 1
created: 2026-11-16T05:39:29Z
deps: [DAEO-2bdu]
links: []
tags: [wave-2, adoption]
allowed_paths:
- src/gov/adopt/stages.py
- tests/unit/adopt/test_w2_190*
reads:
- src/gov/adopt/**
- src/gov/records/**
- governance/project/orchestration/packages/P-W2-81-VERDICT-1.md
needs:
- src/gov/adopt/stages.py
waits_on:
- ref: DAEO-2bdu
  reason: W2-88 holds src/gov/adopt/stages.py's A3 as merged; closed
est_loc: 80
kpis:
  success:
  - line: "S1 `gov adopt --lite --stage A3 --map <proposal>` refuses the proposal as a whole (`PROPOSAL_REFUSED`, as its other refusals) when an artefact's action is DELETE_FROM_ACTIVE_TREE and its repository-relative path appears in the text of another tracked file; the problem for that path carries the code `DELETE_REFERENCED` and names each referencing file; no A3 record is written [DEC-1197 (2)(ii)]"
    verify: "tests/unit/adopt/test_w2_190_referenced.py: a fixture repository with docs/plans/0003-storage-migration.md and docs/plans/0007-storage-migration.md whose text says it supersedes plan 0003 (`docs/plans/0003-storage-migration.md`); a proposal deleting 0003 is refused with DELETE_REFERENCED naming 0007, and governance/adoption/ holds no A3 record"
  - line: "S2 The same refusal, with the code `DELETE_SUPERSEDED`, for a file classed superseded: the target of a SUPERSEDES edge in the repository's record graph, or a file whose front matter status is superseded (any case) [DEC-1197 (2)(ii), CAP-08]"
    verify: "tests/unit/adopt/test_w2_190_superseded.py: one fixture with a record whose front matter says status: SUPERSEDED, one with a SUPERSEDES edge naming the target; deleting either is refused with DELETE_SUPERSEDED"
  - line: "S3 RETIRE or KEEP of the same file is accepted, and DELETE_FROM_ACTIVE_TREE of a file that no other tracked file names and that is not superseded is accepted as today [DEC-1197 (2)(ii)]"
    verify: "tests/unit/adopt/test_w2_190_referenced.py: the S1 fixture with RETIRE (kind given) for 0003 records A3; a third, unreferenced file deleted records A3 with its batch"
  failure:
  - line: "F1 A delete of a referenced or superseded file recorded at A3 or executed by an A6 batch [DEC-1197 (2)(ii)]"
    verify: "tests/unit/adopt/test_w2_190_referenced.py: after the refusal no A3 record exists, so A6 refuses for want of it; the file is still tracked"
  - line: "F2 Over-refusal: a mention inside the file itself, inside governance/adoption/ (the adoption's own records), or in a file the same proposal also deletes, counted as a reference; or a path that only shares a suffix with the deleted one (docs/a/x.md against x.md) counted [DEC-1197 (2)(ii)]"
    verify: "tests/unit/adopt/test_w2_190_scope.py: one case each is accepted"
non_goals:
- no change to A6's execution, the path map's schema or the adopt skill's text (a kernel path; a skill line comes back as a package)
- no classing of documents by their content; superseded is read only from the record graph and front matter
- no change to the MOVE, RENAME, SPLIT or MERGE checks
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1197, DEC-974, CAP-06.b, CAP-08, DAEO-2bdu, DAEO-l78m]
acceptance_tests: {path: tests/acceptance/W2-190/}
---
# W2-190 A3 refuses DELETE_FROM_ACTIVE_TREE of a file another tracked file references, or one classed superseded

Filed 2026-11-16 by the CTO on the owner's word (DEC-1197 (2)(ii), P-W2-81-VERDICT-1 (b)).

**Problem.** In W2-81's full run on 0.1.0, secret-history's adoption took two DELETE_FROM_ACTIVE_TREE actions of
superseded documents, `docs/plans/0003-storage-migration.md` and `docs/specs/upload-limit.md`; their successors still
name them (`0007-storage-migration.md`: "This plan supersedes plan 0003 (`docs/plans/0003-storage-migration.md`)";
`upload-limit-revised.md`: "This revision replaces `docs/specs/upload-limit.md`"). The judge's rule for a superseded plan
is "never deleted", and the read marked two hidden variants MISHANDLED. A3 (`src/gov/adopt/stages.py` `_entry`, `a3`)
accepted the deletes: it checks a delete's batch only, and finds dependents (`_dependents`) only for moves.

**Approach.** In A3, before the record is written, for each DELETE_FROM_ACTIVE_TREE entry: search the other tracked
files' text (outside `governance/adoption/` and outside files the same proposal deletes) for the entry's exact
repository-relative path, and read the record graph and front matter for superseded; a hit is a problem of the
proposal, refused as a whole as A3's other problems are.

**Rabbit holes.** Do not build a content classifier. Do not match bare file names (a suffix match would refuse
unrelated deletes). Binary files are skipped in the text search.
