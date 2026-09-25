# BR-HO-0014: bounded repair B3R, making the code layer build eagerly and deterministically (run BR-AR-0014)

**This brief is `HANDOFFS/BR-HO-TEMPLATE-builder.md` (read it first; its rules bind you) plus the section below.**

| Field | Value |
|---|---|
| Run | `BR-AR-0014`. You are a **fresh** builder, not the B3 builder. |
| Worktree | `/home/usain/Dynamic-Agentic-Engineering-OS/.claude/worktrees/br-ar-0014`, branch **`bridge/b3r-0014`** |
| Model | spawned `model: sonnet` |
| Mutation scope | `release/orchestration/phase-2-context-bridge/govbridge/code/**`, `…/tests/code/**`, `…/tests/fixtures/code/**` and `…/AGENT_RUNS/BR-AR-0014.*`. **Do not edit `govbridge/core/**`.** Use its public layer-builder and digest registration API. |

## The defect, found by the orchestrator in D1

The committed build manifest, `INDEX` from D1 at `cf7efe7`, has `layers.code = {rows: 0, blobs_parsed: 0, digest:
e3b0c442…b855}`. That digest is the sha256 of the empty string. The code layer is **lazy**: `govbridge/code/__init__.py`
says so, since it parses a blob only when a query first needs it. Three consequences:

1. The "two from-clean builds give an identical manifest" proof, and the "incremental ≡ full" proof, **never covered
   code rows**. ARCHITECTURE.md §8.1 requires the per-layer digests to cover the sorted `symbol`, `call_site` and
   `literal` rows.
2. The code layer's contents, and so any digest recomputed later, depend on **which queries happened to run**.
3. `_code_layer_digest` hashes **only** `code_symbol` rows. `call_site` and `literal` are not in the digest at all.

## What to change

1. **Eager build for the non-history refs.** Register a code-layer **builder** through core's existing
   `register_layer_builder` API. During `index rebuild`/`update`, it parses **every Rust blob** at every canonical-view
   ref whose role is not `history`. Today those are `records`, `product` and `evidence`. Derive the ref set from
   `canonical-view.yaml` roles generically. **Never** hard-code ref names or commits (OC-BR-02). The architecture
   costs this at about 1.5 s per commit (§12).
2. **The digest covers exactly the eager set.** Its contents are the sorted `code_symbol`, `code_call_site` and
   `code_literal` rows for blobs reachable at the eager refs. It must be **query-invariant**: lazily parsing a
   `history`-only blob at query time must not change the digest. Either keep lazy rows out of the digest by blob
   membership, or keep them in separate tables. **Report which you chose.**
3. **Incremental.** When an eager ref moves, parse only the new blobs. The result must equal a from-clean build.
4. **Queries stay unchanged.** Lazy parsing of history blobs keeps working for `history`/`callers --commit <history>`
   queries.

## Acceptance checks (one checkpoint entry each)

Use `GOVBRIDGE_STORE=$HOME/.cache/gov-bridge/store-BR-AR-0014`. For check 2, use a second store,
`…/store-BR-AR-0014b`.

1. `cd $D && $PY -m pytest tests -q`: plain, with no import-mode flag. **Everything passes.** Existing test files are
   frozen apart from assertions that encode the old lazy-digest behaviour. Quote any such before/after in your report.
2. Two from-clean builds of the **code layer only**, one into each store: `$PY -m govbridge index rebuild --layer
   code --from-clean`, or the CLI's equivalent. You may need the core layer first; if so, build it and state how. The
   two builds must give an **identical code digest**, with `rows > 0`, and `blobs_parsed` equal to the number of
   distinct `.rs` blobs across the eager refs. **Compute that number independently** with `git ls-tree -r --full-tree`
   at each eager ref's commit, and print both.
3. **Query-invariance.** Record the code digest. Run `$PY -m govbridge.code.symbols callers resolve_state_root --commit
   <a phase2/* history tip commit whose .rs blobs differ from the eager refs>`. Recompute the manifest's code digest:
   it must be **unchanged**.
4. **Incremental ≡ full**, on a fixture repo: build at commit C1, then update to C2, where C2 changes one `.rs` file.
   The code digest must equal a from-clean build at C2.
5. **Coverage of the three row kinds.** Show that the digest changes when a single `call_site` row, and separately a
   single `literal` row, differs. Use a fixture test.

No code may special-case Review 8, F1–F6, Phase 2 or particular symbols or file names (OC-BR-02).
