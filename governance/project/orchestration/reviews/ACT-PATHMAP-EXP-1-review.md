# Review: ACT-PATHMAP-EXP-1 (`experiments/**` added to `namespaces.doc-records.paths`)

**Reviewer:** independent-auditor, fresh read-only session (GOV_TICKET DAEO-6ox0), 2026-11-11.
**Verdict:** pass. READY, no round. Three findings, all recorded rows and none blocking.

## What was checked
- **Hashes:** every hash in the package, `list.txt` and `manifest.json` recomputed and matching. Manifest `9a945c99201d…`; before `5654eca4c139` is REDS-1's after; after `d50884e3633e`. The chain runs f4029cfb4942, then 0ec1d20da86a, then 5654eca4c139, then d50884e3633e, and the live map is `f4029cfb4942`.
- **Diff:** exactly one added line, `      - "experiments/**"`, under `doc-records.paths`.
- **Fix confirmed on newer code:** `w2/integrate` moved to `792b92923`. In a fresh clone with W2-40 `29753c768def` merged, both named tests and `gov.check.pathmap` were red without the ACT and green with it.
- **Independent walk:** of 4090 tracked paths, 16 change namespace, all `experiments/` and all from none to `doc-records`. With the ACT, every path is in exactly one namespace.
- **What `doc-records` grants:** no write and no read. The guard reads no namespace, and `permitted_roles` is the same in all 18.
- **What the ACT changes for retrieval:** the 16 files become keyword-indexable (governance memory under the secrets filter) and stay out of the vector index.
- **Class:** (b) is correct by the `path-map` row (not an `only_added` refusal addition, no ratchet list touched). `9a945c99` matches the manifest's sha8.
- **`apply.sh`:** wrong order refused at both f4029cfb4942 and 0ec1d20da86a with nothing touched. Apply only from before, mode 644, temp file from `mktemp` in the map's folder, links refused, no backup, no commit. Undo is byte for byte from after only.
- **Rehearsal:** a fair reading. Path-map compliance is the only `gov check` line that changes; the other four reds come from the fresh clone having no store.

## Findings
| id | scope | ordinary work | consequence | summary |
|---|---|---|---|---|
| F1 | out | yes | other | The whole-root glob keyword-indexes any future file under `experiments/` by default. Measure-derived output there would need a `not indexed` namespace; that is an entry criterion for the ticket that first writes it (DEC-803). |
| F2 | in | yes | other | Rehearsal part J says the four steady reds "do not read namespaces". Rebuild and the keyword index do read them, but the conclusion (red because no store is built, the same in both runs) holds. |
| F3 | in | yes | other | Experiment files fall in the `middle` authority tier while `docs/probes/**` is in `reports`, and the comment above `doc-records` does not mention experiments. Ranking and documentation only. |

**Classification:** 0 blocking, 2 in scope with consequence "other", 1 out of scope.

## Hygiene
- No tree written, the live map untouched, the clone removed.
- Scratch: 199M and 9643 inodes.
- `ps` showed no ollama or llama-server process.
