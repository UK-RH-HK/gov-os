
## `gov check` on this repository: the baseline of red checks (DEC-466, DEC-467, 2026-10-07)

Run at `46ec8da3`: exit 3. Thirteen hard-block checks are red, for reasons that lie in this repository's state
before its adoption (W1-39, W1-41), not in a ticket branch. A merge is blocked by any red outside this list
(DEC-467).

| Check | Reason at the baseline |
|---|---|
| `context-reproducibility` | unmeasured: no tickets in the record store |
| `core-graph` | the tickets' `depends_on` name W1 ids, which are not record ids |
| `core-schema` | records without `state_class` (for instance `docs/adr/ADR-0001-threat-model.md`) |
| `fresh-agent-reconstruction` | its command calls `gov`, which is not on PATH here (exit 127) |
| `index-freshness` | the lexical index is stale after every commit since the one rebuild (DEC-448) |
| `recovery-rebuild` | the store's digest differs from a rebuild's, for the same reason |
| `retrieval-regression` | unmeasured: the dev tiers are not configured |
| `secrets-indexing` | its command exceeds 60 seconds on this tree |
| `policy-security`, `policy-test`, `policy-change`, `policy-human_gate`, `policy-tool` | the policy key has no associated check |

Yellow at the baseline: `audit-reproducibility` (not applicable until the first audit), `core-commands`,
`openspec-validate`, `policy-memory`, `policy-checkpoint`, and the families adapter/model portability (no
registered check until W1-38) and product traceability. Green: `core-authority`, `core-claims`,
`core-mutation`, `core-pathmap`, `skill-regression-a`, `skill-regression-b1`, `skill-version`, `readiness`.
