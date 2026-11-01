# W2-122 (DAEO-blwa), run 1 — seeded rebuilds (STANDARD, engineer), at the front of the queue (DEC-1014)

**Why it matters:** today's slot waits come mostly from cold rebuilds (a new worktree's or a close copy's first rebuild
re-embeds the whole repository: 3,000 to 3,750 s when three run at once; SIZING-1). This ticket gives the product
`gov rebuild --seed <store folder>`: copy a warm base's stores in, then rebuild incrementally; the result must equal a
cold rebuild entry for entry. The warm base on this machine is the integration store (`~/gov-os-worktrees/W2-00-store`,
a link to `-a` or `-b`, refreshed by the CTO); the CTO wires the seed into its own tools separately (not your work).

**Do:** the parallel work order (DEC-959 item 7, DEC-963): a fresh independent test designer in a tests worktree from
the KPIs, and a fresh engineer here, at once; tests merged while no worker runs; `gov accept DAEO-blwa` once. Read
`src/gov/rebuild/command.py`, `watch.py`, the stores' layout under `.gov-runtime/` (`store.db*`, `codeintel/`,
`query-vector-cache.db*`), W2-107's secrets cache (`src/gov/secrets/cache.py`) and how the semantic stage decides what to
embed. Fail closed on any mismatch (code fingerprint, embedder model, schema). KPI 3's measure goes in
`docs/changes/W2-122-evidence.md` (the implementer's evidence, DEC-996 A). Every heavy step through a slot (the common
brief: `rebuild_slot.sh`, `verify_lock.sh`, `heavy_slot.sh`). Your scoped run once before you return; the merge queue
lands it (one merge per ticket). Return DONE with the exact head. Scratch budget: 20 GB and 1,000,000 files (DEC-898).
