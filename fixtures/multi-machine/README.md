# Fixture 6 — Multi-machine clone / rebuild

Machine A: `gov init` on the greenfield Rust crate, add records and tasks, run `gov continue`, commit.
Machine B: `git clone` (no `.governance-runtime/`), `gov doctor` (reports the absent runtime with remediation),
`gov rebuild-memory`.

Proved: B's `governance/generated/index-manifest.json` hash equals A's tracked manifest; `gov status` on B yields the
same task counts and next action as on A; the deterministic block of the context packet for the next task has the
same hash on both machines; no opaque runtime binaries were synchronised.
