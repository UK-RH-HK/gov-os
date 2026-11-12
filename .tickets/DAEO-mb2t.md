---
id: DAEO-mb2t
status: in_progress
deps: [DAEO-blwa]
links: [DAEO-blwa, DAEO-qzrq]
created: 2026-11-02T10:37:58Z
type: task
priority: 1
assignee: engineer
external-ref: W2-124
tags: [wave-2, implementation, rebuild, standard]
wbs_id: W2-124
title: 'A rebuild without its semantic store fails named, and adoption finishes and records it: KPI 5 split from W2-122 (DEC-1027 C)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-blwa
allowed_paths:
- src/gov/rebuild/command.py
- src/gov/adopt/stages.py
- src/gov/close/rebuild_gate.py
- tests/unit/rebuild/test_w2_124*
- tests/unit/adopt/test_w2_124*
- tests/acceptance/W2-32/test_w2_32_s2_fail_closed.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))
- tests/acceptance/W2-32/test_w2_32_s10_no_cpu_fallback.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))
- tests/acceptance/W2-13/test_w2_13_secrets.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))
- tests/acceptance/W2-13/test_w2_13_unavailable.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))
- tests/acceptance/W2-13/test_w2_13_latency.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))
- tests/acceptance/W2-76/test_w2_76_timings.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))
- tests/acceptance/W2-76/test_w2_76_unchanged.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))
- tests/acceptance/W2-116/test_w2_116_reindex.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))
- tests/acceptance/W1-41/test_w1_41_embedding_policy.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))
- tests/unit/rebuild/test_w2_116_integration.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))
- tests/unit/rebuild/test_no_embeddings.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))
- tests/unit/rebuild/test_w2_122_seed.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))
- tests/unit/retrieval/test_w2_32_rebuild_cut.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))
kpis:
  success:
  - '`gov rebuild` exits non-zero, named (`REBUILD_FAILED`, `store: semantic`), when the semantic store was asked for and not recreated (the embedder unavailable, hung or failing part way); only `--no-embeddings` skips it; never an ok answer over a partial store. Verify: a planted project that asks for a semantic store, with a stub embedder that is unavailable, one that hangs and one that fails part way: `gov rebuild` exits non-zero each time and prints `REBUILD_FAILED` and `store: semantic`; the same project with `--no-embeddings` exits 0; no run prints ok over a partial store [DEC-1015 item 4, DEC-1027 C]'
  - 'A project with nothing to embed (no path map, or no embedded namespace) is not asked for a semantic store, so its rebuild answers ok. Verify: two planted projects, one with no path map and one whose path map names no embedded namespace, with the embedder stub unavailable: `gov rebuild` exits 0 and prints ok for each, and names no semantic store [DEC-1027 C]'
  - 'Adoption never fails for a missing embedder: stage A6 finishes, and its record and the adoption report carry a named finding (the semantic store not recreated, with the reason) and the command to rebuild it later. Verify: a planted adoption run with the embedder stub unavailable: stage A6''s record shows it finished, and both that record and the adoption report hold one finding that names the semantic store, the reason and the rebuild command; the run does not exit with an error [DEC-1027 C]'
  - 'The close (and the merge queue''s prepare) treats a rebuild without its semantic store as failed, as the CTO''s `rebuild_slot.sh` does today (exit 75). Verify: a planted rebuild result with no semantic store: the close''s rebuild check and the merge queue''s prepare each report failed, and `rebuild_slot.sh` on the same planted result exits 75 [DEC-1015 item 4, DEC-1027 C]'
  - 'A store not built is never ok: gov rebuild on a repository where the path map or .gitleaks.toml is missing, or where a store the path map calls for was not built, names each store not built with its reason, and its result is not ok. A rebuild with --no-embeddings stays ok for the vectors it was told not to build, and says so. W2-26''s finding 2 is a planted case. Verify: planted repositories, one without the path map, one without .gitleaks.toml and one whose path map calls for a store that was not built: `gov rebuild` names each store not built with its reason and its result is not ok; a planted rebuild with `--no-embeddings` is ok and says it skipped the vectors; W2-26''s finding 2 planted case gives the not-ok result [DEC-954 Q9f, W2-26 finding 2, DEC-530] [moved from W2-88 S5, DEC-1083]'
  failure:
  - 'An ok answer, or a close, over a partial semantic store. Verify: the planted partial-store cases of S1 and S4: no `gov rebuild` run prints ok and no close or prepare check passes; any ok or pass there is this failure'
  - 'An adoption that fails, or reports success without the finding, when the embedder is unavailable. Verify: the planted adoption run of S3 with the embedder stub unavailable: the run exits without error and the A6 record and the report each hold the named finding; an error exit, or a record or report without the finding, is this failure'
profile: STANDARD
sources:
- DEC-1027
- DEC-1015
- DEC-1014
- DEC-1083
- DEC-530
- DEC-954
- DAEO-2ds6
- DAEO-2bdu
est_loc: 80
acceptance_tests:
  path: tests/acceptance/W2-124/
  author: independent-test-designer (MR-3)
track: A
list_rows: []
---
# W2-124 A rebuild without its semantic store fails named; adoption finishes and records it

The owner's DEC-1027 C (P-W2-122-K5 (c)): W2-122's KPI 5 turned 100 earlier cases red (adoption's A6 among them), so it
is split out and W2-122's seeding lands without it. This ticket brings it back with the owner's rule: `gov rebuild` and
the close fail on a missing semantic store; adoption does not, it records the gap as a named finding. Earlier suites
that build projects without an embedder are revised by the test designer where they rebuild for real
(`Rewrite-Reason: DEC-1027 C`); a project with nothing to embed is not asked for one. Until it lands, the CTO's
`tools/rebuild_slot.sh` enforces the rule here (exit 75). The close's gate file is named for the engineer to place;
if the close's own code must change instead, the lead returns a package (W2-115 holds `src/gov/close`).

## Interface (DEC-1052; run 1's P1 (a), the lead's proposal accepted as a whole; the CTO, 2026-11-12 14:02)

- Asked for = no --no-embeddings AND the path map has a namespace with `embedding_policy: embedded`. Otherwise
  stores.semantic = {status: not_recreated, requested: false, reason} and no embedder is called (S2).
- Asked for and not recreated (unavailable, hung past the endpoint timeout, failed part way): GovError REBUILD_FAILED,
  details {store: "semantic", reason, stores}, exit 1; no warm-base record (as today).
- src/gov/close/rebuild_gate.py: `semantic_failure(result: dict) -> str | None` (a gov rebuild --json envelope or its
  result; the rule of rebuild_semantic_check.py) and `check(result: dict) -> None` (raises the REBUILD_FAILED above).
  gov.rebuild.command calls check() on its result, so the close (close/batch.py _rebuild -> command.run) and the queue's
  prepare (rebuild_slot.sh -> gov rebuild --json) fail through it: no edit to other close files or merge_queue.py.
- Adoption: stages.rebuild catches REBUILD_FAILED with store "semantic" and finishes; the A6 record (as committed) and
  the stage's `gov adopt --lite --json` result ("the adoption report") each hold
  findings: [{code: SEMANTIC_NOT_RECREATED, store: semantic, reason, command: "gov rebuild"}]. The engineer orders
  rebuild and commit so the committed record holds it. Any other REBUILD_FAILED stays INDEX_REFRESH_FAILED.

## Run 1's P2 and P3 (the CTO, delegated P2, 2026-11-12 14:02)

- **P2 (b):** S2 and S5 both kept; S5 is read in the result: `gov rebuild` keeps exit 0 and `"ok": true`, and the result carries `complete: false` and `not_built: [{store, reason}]` for every store not built (no path map, no `.gitleaks.toml`, a store the path map calls for not built); adoption reads `not_built`. No earlier suite is rewritten for it. W2-26's finding 2 (`"ok": true` on an unadopted clone) stays, named in the result rather than refused.
- **P3:** with (b), earlier suites should not change; if any turns red, its files come back to the owner by name before any revision (widening is the owner's, DEC-1142 (8)).

## P1-L decided (the owner, DEC-1150 (3), 2026-11-12)

**(a): the 13 files are revised** by an independent test designer, one revision each, `Rewrite-Reason: DEC-1027 C` (the rebuild refuses an embedded namespace with no embedder): each case gets `--no-embeddings` or a healthy stand-in embedder, or reads `error.details.stores` where it checks a refusal. **Each revised case keeps what it was guarding** (W2-32's fail-closed cases above all: a case that proved a refusal still proves that refusal); nothing else in the files changes. **The reviewer checks, case by case, that no revised case loses its point** (its assertion still fails on the behaviour it guarded against), and names any that does as a blocking finding.

