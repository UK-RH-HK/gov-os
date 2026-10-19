
## 75. Delegated decisions on W1-17's packages (register v0.75, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the six packages the W1-17 (`DAEO-rxln`) ticket lead
returned. For each the test designer's, the lead's and the orchestrator's recommendations agree on option (a), the
confidence is medium or higher, and the choice is reversible until W1-20 consumes the interface. The tests already
encode these options.

### DEC-340 — W1-17 DP-1: the public interface of the lexical index
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-17 package DP-1 option (a); confidence medium-high · **Under:** CAP-18.b, CAP-11.a, DEC-322
- **Decision:** `gov.retrieval.lexical` exposes `refresh(root)`, `search(root, query, refresh=True)`,
  `freshness(root)`, `digest(root)`, `chunks(root, path=None)` and `parent(root, parent_id)`, with the return shapes
  the suite's README states. `search(..., refresh=False)` never writes, so a worker session can read a live store it
  may not write (DEC-322). W1-20 and W1-27 build on these names.

### DEC-341 — W1-17 DP-3: "2.8 s scale" bounds the incremental re-index, held to 10 s
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-17 package DP-3 option (a); confidence medium · **Under:** CAP-17.a
- **Decision:** The test times only the `search` that follows one edited, committed file on an a-dev clone, with a
  bound of 10 seconds; the full build is not timed. G-20 is in the S0b2 output and was not read: what it measured is
  to be confirmed if the owner allows that read, and the bound is one constant.

### DEC-342 — W1-17 DP-4 and DP-5: a missing, empty or stale index makes the whole facet unavailable, and the check is not green without an index
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-17 packages DP-4 option (a), confidence medium-high, and DP-5 option (a), confidence medium · **Under:** CAP-17.a, CAP-38.b
- **Decision:**
  - A `search` on a missing, empty or stale index returns the facet as unavailable (`FACET_UNAVAILABLE`), with the
    reason `missing`, `empty` or `stale` and no hits; it does not return hits from the fresh files only. A default
    `search` builds a missing index and refreshes a stale one first.
  - The index-freshness check is not green when no index exists; it prints each stale path, prints no traceback and
    never writes. So the check is red in a repository whose live store has no index yet, this one included, until
    an orchestrator-role session builds it (DEC-322). W1-26 and W1-27 take that into account.

### DEC-343 — W1-17 DP-6: Python chunks get a function parent through the standard library
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-17 package DP-6 option (a); confidence medium · **Under:** DEC-091, CAP-18.b
- **Decision:** A chunk's parent is the function for Python (through `ast`, no install), the module (the whole
  file) for other code, and the section for Markdown. The 40 to 60 lines this adds to the estimate are accepted.

### DEC-344 — W1-17 DP-7: the corpus is the working-tree content of tracked files
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-17 package DP-7 option (a); confidence medium-high · **Under:** CAP-03.d, CAP-17.a, DEC-285
- **Decision:** The index reads tracked files as they stand in the working tree, the same content the secret
  filter judges, not the blobs of `HEAD`. The index and the record graph (`gov.store.load` reads `HEAD`) can
  therefore describe different states of one file; that is a residual for W1-20.

| Version | Date | Change |
|---|---|---|
| 0.75 | 2026-10-04 | Delegated under DEC-220: DEC-340 (W1-17 DP-1: the lexical interface), DEC-341 (DP-3: the incremental re-index is timed, 10 s), DEC-342 (DP-4, DP-5: an unusable index makes the facet unavailable; the check is not green without an index), DEC-343 (DP-6: function parents for Python through `ast`), DEC-344 (DP-7: working-tree content of tracked files). |
