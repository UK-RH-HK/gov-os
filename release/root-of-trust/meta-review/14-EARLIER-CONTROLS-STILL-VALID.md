# Earlier controls still valid

The root-of-trust rebase must not regress the product controls already developed and independently exercised.

## Constitutional and authorization controls

- deterministic authority/policy precedence;
- project overlays may strengthen but not weaken protected floors;
- refused overrides/exceptions are observable;
- governed exceptions resolve to real, active, scoped, sufficiently approved decisions;
- human approval derives from a presented and answered gate, never a caller flag;
- decline/revoke/stale approval behavior remains fail-closed;
- authority checks exist on mutating paths.

## Plugin/tool controls

- descriptors are discovery, not authorization;
- OS-written registration binds descriptor and implementation bytes;
- kernel policy supplies the execution floor;
- descriptor roles may narrow only;
- elevated permissions require authoritative gate evidence;
- security review cannot self-attest;
- plugin drift, bad output, timeout and pin mismatch fail closed.

## Repository, update and mutation controls

- immutable released payloads and reproducible release identity;
- kernel/project-overlay separation;
- update preserves overlay/spec/product state;
- migration chain and rollback ledgers;
- rollback snapshot consumption and downgrade refusal;
- observed mutation scope rather than worker self-attestation;
- path-first brownfield adoption with independent tests;
- `FREEZE_WRITES` and other emergency controls remain meaningful.

## Memory and data controls

- Git/governed records remain authoritative;
- SQLite/vector/graph/lexical/code stores remain derived and rebuildable;
- embedder/reranker pins and incompatible-index refusal;
- full rebuild staging/atomic swap;
- claims/control state survives memory rebuild;
- sensitivity/namespace exclusions and upstream export default-deny;
- deterministic authority context outranks retrieval;
- stale/superseded state is filtered and evidence freshness tracked.

## Product architecture controls

- Rust-first deterministic core without imposing Rust on governed projects;
- replaceable capability interfaces;
- language-native tooling through the registry;
- dynamic task DAG and readiness contracts;
- checkpoints/handoffs and fresh-session independent verification;
- CIT-P/CIT-E, observability and upstream learning.

## Preservation rule

The new root verifier may replace only the source-authentication and install-trust boundary. It must not rewrite unrelated Governance OS capabilities or invalidate established tests without an explicit, provenance-classified reason.
