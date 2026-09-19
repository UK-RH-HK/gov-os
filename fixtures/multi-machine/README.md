# Fixture 6 — Multi-machine clone / rebuild

Machine A: `gov init` on the greenfield Rust crate, add records and tasks, run `gov continue`, commit.
Machine B: `git clone` (no `.governance-runtime/`), `gov doctor` (reports the absent runtime with remediation),
`gov rebuild-memory`.

Proved: B's `governance/generated/index-manifest.json` hash equals A's tracked manifest; `gov status` on B yields the
same task counts and next action as on A; the deterministic block of the context packet for the next task has the
same hash on both machines; no opaque runtime binaries were synchronised.

**First-run path: provision, then install (OWNER-DECISION-P2-0002).** The harness provisions each scenario machine with the certification suite's throw-away test root (`tests/certification/common.rs::provision`, published-seed keys — never a production root) and installs a release signed under it (`gov init --source <signed release>`; `common::signed_source`). A machine with no trust anchor refuses kernel material from any external source; only the `gov` binary's own embedded payload may be installed there, as a marked bootstrap installation that is never presented as current, verified or certified.

Machine B is a different machine: its administrator provisions it and it verifies the release the clone pins (`gov kernel reinstall --source <signed release>`, ARCH-0003 §8) before relying on the installed kernel. The verification re-commits byte-identical files, so the clone's working tree is unchanged.
