# BR-HO-0015: bounded repair B6R2, populating section G (code/test/enforcement surfaces) as §7.2 specifies (run BR-AR-0015)

**This brief is `HANDOFFS/BR-HO-TEMPLATE-builder.md` (read it first; its rules bind you) plus the section below.**

| Field | Value |
|---|---|
| Run | `BR-AR-0015`. You are a **fresh** builder. |
| Worktree | `/home/usain/Dynamic-Agentic-Engineering-OS/.claude/worktrees/br-ar-0015`, branch **`bridge/b6r2-0015`** |
| Model | spawned `model: sonnet` |
| Mutation scope | `release/orchestration/phase-2-context-bridge/govbridge/compile/**`, `…/govbridge/route/**`, `…/config/budgets.yaml`, `…/tests/compile/**`, `…/tests/fixtures/compile/**` and `…/AGENT_RUNS/BR-AR-0015.*`. **Do not edit** `govbridge/{core,authority,graph,code,lexical,semantic}/**`: use their public APIs. `compile/validate.py` is near-frozen. Any change to it must be listed and justified, and **none** may weaken the section-A re-derivation, the admissibility checks or the ordering invariant. |

## The defect, found by the orchestrator before the demonstration

The orchestrator compiled `ARCHITECTURE/demonstration-task.yaml` with real routes at the frozen view. The evidence is
`DEMONSTRATION/run-0-predispatch-g-empty/`, on branch `bridge/demo-0011`. **Section G came out empty.** H had 87
items, and 11 of those were `runtime/` code hits. ARCHITECTURE.md §7.2 defines G as:

> "code route at the canonical product ref: **seed symbols**, their callers/callees, `READS_KEY` consumers, `TESTS`;
> evidence probes"

It fills from the code route, and it admits `RetrievedItem`/`DerivedItem` with resolution labels. Three things cause
the empty section:

1. In the seed pass (`packet.py` near line 487), `c.routes.run("code", seeds=[seed])` is given **record IDs** such
   as `P2-AR-0097#F2`. The code route only resolves symbols, so it returns nothing. **Nothing derives seed symbols
   from record seeds.**
2. In the query pass, the code route runs only for symbol-shaped tokens (`router.select_routes`). Task queries
   phrased by function never contain one.
3. Placement looks at `(class, lifecycle, delivery)` only. A retrieved hit whose canonical occurrence is product
   code or a test lands in H, because §5.1 classes such files as `EVIDENCE`.

## What to change. It must be generic (OC-BR-02): no Review-8 IDs, paths or symbols in code.

1. **Derive seed symbols from record seeds, deterministically.** Every task seed resolves to a record or section. A
   record's text cites code by `path:line`, by `path:line-line`, by path-qualified symbol (`module::fn`), or by bare
   symbol in backticks, and B5's graph may already hold `CODE_CITES`/`MENTIONS` edges for these. For each such
   citation, resolve the **enclosing symbol at the view's canonical product ref** using the B3 code tables
   (`govbridge.code.symbols` and its public API). Label every resolution (`EXACT_PATH`, `HEURISTIC_*` and so on), and
   **never** report a heuristic resolution as exact. Where a cited line has no enclosing symbol, keep an
   occurrence-level G item for that line.
2. **Expand from those seed symbols** within the profile's budget: callers and callees; the `READS_KEY` consumers of
   any literal key read at a seed symbol; `TESTS` edges; and evidence probes cited by the seed record. Use the
   existing graph/code APIs, and label every edge.
3. **Placement.** A RETRIEVED or DERIVED item whose canonical occurrence is a **code or test surface** goes to **G**,
   not H. Code or test surfaces are decided from a small **config list** of source kinds and test path patterns
   (add it to `config/budgets.yaml`, or a new key there). Retrieved non-code items still go to H. **Authority rules
   are unchanged:** A is still resolver-only, D.1/D.2/D.3/E/F placements are unchanged, and nothing retrieved enters
   A or D.1.
4. **Budget.** G gets its budget from `config/budgets.yaml`. Record drops in the manifest as for every other
   section.

## Acceptance checks (one checkpoint entry each)

Use `GOVBRIDGE_STORE=$HOME/.cache/gov-bridge/store-BR-AR-0010` **read-only** for the real-view checks. It is the
frozen-view demonstration store. **Do not run `index update`/`rebuild` against it.** For fixture tests, use your own
store, `…/store-BR-AR-0015`.

1. Run `cd $D && $PY -m pytest tests -q` (plain collection). **Everything must pass.** The six named invariant tests,
   the import-boundary test and the class-table test must pass **unmodified**.
2. **Fixture test.** A seed record cites `src/x.rs:N` and a backticked symbol. G must contain the enclosing symbol
   (labelled), a caller, a `TESTS` edge target and the cited evidence probe. The same code hit via lexical retrieval
   lands in G, not H. A retrieved non-code hit stays in H. Nothing retrieved is in A or D.1.
3. **Real view, the demonstration task.** Compile `ARCHITECTURE/demonstration-task.yaml` with real routes, **twice**:
   * the packets are byte-identical;
   * `packet verify` passes;
   * **G is non-empty**;
   * section A's item set and order are identical to the run-0 packet's section A. Compare the `unit.id` sequence
     from `DEMONSTRATION/run-0-predispatch-g-empty/packet/manifest.json` on `bridge/demo-0011`.

   Print G's items: path, line, symbol, label and route.
4. **Real view, the control (OC-BR-02).** Compile a task spec **you write in `tests/fixtures/compile/`**, seeded with
   an **unrelated** record: `D-0006`, the capability-plugin decision. G must be non-empty with labelled code
   surfaces from that subsystem, and `packet verify` must pass.
5. **Invariants.** Hand-move a G item into A: `packet verify` must FAIL. Hand-move a retrieved G item into D.1:
   `packet verify` must FAIL.

**Never** look at `DEMONSTRATION/oracle*`, or at any directory named `govbridge-sealed-*`. You never see the oracle.
