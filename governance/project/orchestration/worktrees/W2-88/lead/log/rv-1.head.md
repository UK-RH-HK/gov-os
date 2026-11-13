---
type: probe
task: DAEO-2bdu
round: 1
reviewer_session: c168bd40-4462-4b61-9a70-0b7330fcf4c9
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: fail
probed_commit: 5b41893beb797072af8b6cad8e6c514cfee55fa4
decisions_applied: [DEC-1010, DEC-136, DEC-820, DEC-1052, DEC-1112, DEC-1144, DEC-1157]
---

# Probe record: W2-88 (DAEO-2bdu), review round 1 of at most 2 (DEC-1010): FAIL

## The lead's judgement and triage

- **Who probed.** A fresh, read-only Independent Auditor session (`c168bd40-4462-4b61-9a70-0b7330fcf4c9`, claude-opus-5-5, effort high, class C2), started through `launch_worker.sh` / `gov launch` under the OS sandbox on 2026-11-13 at 05:13. Step 0 held (the write outside the tree failed with a read-only file system; the index refresh worked). The head was 5b41893beb79 and `git status --porcelain` was empty at start and end. Its tripwire changes were in the CTO's store trees only (W2-00-store, W2-00-store-b).
- **Refusals the reviewer met, each once, none retried:** a Write under quiet hours (DEC-991), a Bash `find` in the pin's site-packages read by the hook as a hidden-set read, and a shell variable as a write target.
- **The lead's verification at the head** (lead_verify, scoped, outside the sandbox): parallel 6,043 tests, 6 failed, 8 skipped; serial 3 passed. The 6 are five W2-88 cases tied to package P-W2-88-B-1 (S16's copy step; the loader's `rerank`/`bundle` keys) and `tests/acceptance/W2-23/test_w2_23_space.py::test_s6_every_kernel_hook_exits_alike_with_a_space_in_the_project_dir`, which is red on the integrate tree too (W2-00-store at cb208f943: 1 failed), so it is integrate's, not this branch's.
- **The verdict stands as FAIL** (never decided away, DEC-1010). The triage of every finding:

| finding | severity | triage | the fix, as a described behaviour for the test designer (DEC-136) |
|---|---|---|---|
| RV1-1 tuned pool is no departure | blocker | fix; the reading goes to the CTO as P-W2-88-B-1 B-1.4 (recommended: the whole shipped block) | a `retrieval.yaml` whose pool is on but differs from the shipped `pool:` block in any key names `pool` with its value in `departures`; the stage is not ok without `--decision` |
| RV1-2 an unavailable vector scan is recorded as one | blocker | fix | when the semantic route answers unavailable or errors, `scale.vector_scan_ms` is null with the reason named (not measured), never compared as under budget; only the vector scan is compared with the budget (S5's text) |
| RV1-3 without gitleaks the plan says "no secret" | blocker | fix; the form goes to the CTO as B-1.5 (recommended: `SECRETS_UNSCANNED`) | when the secrets scan did not run, or skipped files, MA writes no `NOTHING-TO-REFACTOR.md` and its plan and result name the unscanned state |
| RV1-4 binaries listed refused while the store holds them | minor | fix | `refused` never holds a file the store holds; a binary the lexical store chunked is listed as indexed there |
| RV1-5 code graph lists, swallowed read error | minor | fix (the error part); language part with P-3 | a code graph that cannot be read is named in the record and the store is not ok, never 0 nodes and edges with ok; a file whose suffix the graph does not read is refused `unsupported-language` |
| RV1-6 a record load re-stamps a stale store | minor | fix | after `loader.load` on a stale store, `connect` still refuses it (or the load replaces it whole) |
| RV1-7 evidence calls an unrun scan a scan time | minor | fix with RV1-2 | the proof says no vector scan was measured (stand-in embedder), or gives the real figure from a run with the embedder |
| RV1-8 the no-route rule stated differs from the code | minor | fix | the evidence and `assess` state the same rule; a planted file with an unlisted code suffix lands where the rule says |
| RV1-9..11 = B-1.1..B-1.3 | package | the CTO | P-W2-88-B-1 |

- **Round 2** (the last, DEC-1010) waits for the CTO's answers to P-W2-88-B-1, so that one test-design batch and one fix carry both the findings and the decided package items.

