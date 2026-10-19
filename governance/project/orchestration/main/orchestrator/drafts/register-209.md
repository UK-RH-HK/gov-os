
## 209. The diagnostic of DEC-686 and the trace of DEC-688: what they show, and one delegated decision on a-dev's embedding policies (register v0.209, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-693 — a-dev's namespaces get valid embedding policies in the exit clone; the diagnostic's and the trace's results are recorded
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-14; told to the owner, who may replace it) · **Under:** DEC-380, DEC-381, DEC-388, DEC-686, DEC-688 · **Basis:** the orchestrator's read-only diagnostic of the a-dev exit clone at `30996b6` and of `src/gov/retrieval/semantic.py`, `src/gov/adopt/`, the adopt skill and the path-map schema; the two clones' containment findings files (`trace-restores.py`)
- **The diagnostic's result (DEC-686): the owner's reading is confirmed.**
  - In a-dev's path map, 20 of 21 namespaces say `embedding_policy: not stated by the programme`, and the namespace of the secret-named files says that nothing of them is embedded. No namespace says `embedded`.
  - The semantic index embeds only the chunks of a file whose every namespace says exactly `embedded` (DEC-381); any other value is "not embedded". So a rebuild embeds nothing there, answers "semantic: recreated", and retrieval answers `FACET_UNAVAILABLE` with an empty facet. No error and no finding is given anywhere.
  - The path map was written by the adoption repair worker (role product-spec, clone commits `9882a63` and `9b08f6f`). Nothing in `gov adopt`, in the adopt skill or in the path-map schema says which values the field takes: the schema asks for a text, and the field is optional in the loader.
  - **The product gap for the round of DEC-686:** adoption leaves a path map without one embedded namespace, and no check, stage or doctor section says so. The round's scope is put to the owner (it changes a kernel skill or a check, CAP-33).
- **The trace's result (DEC-688): no MR-3 breach; the eleven restores changed no acceptance test.**
  - Eleven findings "reverted: acceptance test restored from HEAD": five in a-dev (session `d6e1b5d3…`, role product-spec, ticket ORION-ad01), six in b-dev (session `94619988…`, role product-spec, ticket ARGUS-ad01), all between 09:27 and 09:40 UTC on 2026-10-12, all on Bash calls.
  - Each names one path, the folder `tests/acceptance` itself, never a file in it.
  - At that time neither clone held an acceptance test: the first ones were committed on 2026-10-13 (`930b197` in a-dev, `2db35a4` in b-dev). There was no acceptance test to change and none to restore.
  - Nine of the eleven commands only read (`cat`, `head`, `git log`, a listing, a search). The other two, in b-dev, edit files under `docs/` and commit the path map, the tool registry and legacy records; neither names the test folder.
  - Each clone's findings file also holds two "flagged" entries of the same sessions that name eleven dot-files of the project root (shell and editor files) as changes outside the allowed paths: the same names the reviewer of the W1-02 round saw appear in its worktree and took for the sandbox's mount points.
  - **Reading (not reproduced):** the launcher's rules deny a product-spec worker the acceptance-test folder; where that folder does not exist, the sandbox puts an empty entry at its place while a command runs, as it does for the dot-files. The post-command check sees a new path under the test folder, attributes it to the call and removes it. The lead of the next run confirms or refutes this in a stand-in project.
  - **Residual for the Wave 2 list:** the post-command check reports the sandbox's own placeholders as a worker's changes (as restores of acceptance tests, and as changes outside the allowed paths).
- **Decision** (P3, a synthetic programme's throwaway clone, reversible; confidence medium-high):
  - In the a-dev exit clone the namespaces that hold what a question in plain words is asked about say `embedded`: the programme's code, its specifications, its decisions, its documents, its interfaces, examples, benchmarks' and research's text, the tickets and the adoption records. The namespaces of the kernel, the project configuration, the generated agent files, CI, data sets and the root files say `not embedded`. The namespace of the secret-named files stays as it is (DEC-679).
  - The edit is made by the role the product's method gives the path map to, under a ticket, with the three trailers; the lead of the next run states which namespaces got which value.
  - Then `gov rebuild` with embeddings, the two scenario retrievals and the semantic canary are re-run (DEC-686).

| Version | Date | Change |
|---|---|---|
| 0.209 | 2026-10-14 | Orchestrator: DEC-693 (the diagnostic of DEC-686: no a-dev namespace says `embedded`, the adoption gives no valid value and nothing reports it; the trace of DEC-688: the eleven restores name the then non-existent test folder itself, on read commands, no MR-3 breach; delegated: valid embedding policies in the a-dev exit clone). Next free id: DEC-694. |
