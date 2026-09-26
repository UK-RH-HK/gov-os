# run-0: compiled for the demonstration, never dispatched

The orchestrator compiled this packet at the frozen view `fa25492`, against store-BR-AR-0010, using real routes.
`packet verify` passed, and it places every mandatory authority class correctly. It was **not** given to a
demonstration agent, because **section G (code/test/enforcement surfaces) came out empty**.

The cause is generic and does not depend on Review 8:

* the seed pass runs the code route with **record IDs**, and the code route resolves only symbols;
* the query pass adds the code route only for symbol-shaped tokens;
* retrieved hits whose canonical occurrence is product code are placed by class alone, so they land in H.

ARCHITECTURE.md §7.2 defines G as "code route at the canonical product ref: seed symbols, their callers/callees,
READS_KEY consumers, TESTS; evidence probes". Deriving seed symbols from record seeds was never implemented.

The fix is BR-AR-0015. This directory is kept as evidence of the pre-repair compiler: `packet_sha256`
`18be7e6f…2025`; G 0 items; H 87 items; 11 of those H items are `runtime/` hits.
