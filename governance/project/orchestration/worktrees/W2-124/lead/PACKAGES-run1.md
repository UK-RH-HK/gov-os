task: DAEO-mb2t (W2-124) · run 1 (build) · lead return PACKAGES before any worker (DEC-1052)

## P1 — the ticket states no Interface (DEC-1052)
Missing: the gate's function in src/gov/close/rebuild_gate.py; the adoption finding's shape and what "the adoption
report" is (no such artefact exists in src/gov/adopt today); when the semantic store is "asked for"; the rebuild order
in A6 (stages.rebuild runs after run.finish has committed the A6 record, so the record cannot hold the finding as built).
Proposal (a), accept in one line:
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
Cost: none beyond the ticket. Confidence: high. Blocks: every worker.

## P2 — S2 and S5 contradict on a repository with no path map (DEC-105)
S2: no path map -> `gov rebuild` exits 0 and prints ok. S5: no path map (or no .gitleaks.toml, or a store the path map
calls for not built) -> result not ok (W2-26 finding 2: an unadopted clone builds nothing and says "ok": true).
Ground: 104 test files call rebuild; only 43 mention path-map and 25 mention .gitleaks.toml. Those files are outside
this ticket's allowed_paths, and the ticket gives the designer only tests/acceptance/W2-124/.
Options:
- (a) S5 wins: S2 keeps only "path map names no embedded namespace"; no path map / no .gitleaks.toml / a called-for store
  not built -> REBUILD_FAILED naming each store and reason; --no-embeddings ok, saying it skipped the vectors. Cost: likely
  tens of earlier suites turn red (same kind as W2-122's 100); needs a Rewrite-Reason grant over tests/acceptance/** and
  tests/unit/** for the designer, about +1 designer run (~USD 3 to 6), est_loc well over 80.
- (b) Both kept, S5 read in the result: exit 0 and "ok": true stay, and the result carries `complete: false` and
  `not_built: [{store, reason}]` for each store not built (S2's no-path-map run says no semantic store). Cost: none
  beyond the ticket; W2-26 finding 2's "ok": true envelope stays (named, not refused).
- (c) Re-baseline: S5 back to its own ticket (needs the owner's P1, DEC-974). Cost: one more ticket; this one lands S1-S4.
Recommendation: (a) for .gitleaks.toml missing and a called-for store not built, with (b) for no path map only (S2's
line stands; the result names `not_built` with `complete: false`). If one letter: (b). Confidence: medium.
Blocks: the designer's S2/S5 cases and the engineer's result shape.

## P3 — the earlier suites' revision has no paths
The ticket asks the designer to revise earlier suites that rebuild for real (Rewrite-Reason: DEC-1027 C), but its
allowed_paths name only tests/unit/{rebuild,adopt}/test_w2_124* and acceptance_tests tests/acceptance/W2-124/.
Options: (a) grant the designer those suites' files under Rewrite-Reason: DEC-1027 C, named once the first red run lists
them (cost ~USD 2, one batch); (b) leave them as the queue's reds for each owner ticket (cost: blocked landing).
Recommendation: (a). Confidence: high. Blocks: green verification (DOD), not the start.
