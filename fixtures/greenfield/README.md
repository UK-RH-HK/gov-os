# Fixture 1 — Greenfield (Rust governed project)

A brand-new Rust crate (`orders-ledger`) with no governance. Language deliberately differs from nothing in
particular: the Governance OS core is Rust too, but the fixture proves ecosystem resolution (Cargo) and native test
execution for a governed project, and every other fixture uses a different language (Python, TypeScript, mixed).

Exercised by `tests/certification/greenfield.rs`:
product ideation (PRJ) → scenarios → feature-readiness gaps → readiness planner generates research/data/test-design
tasks in the same DAG → implementation task stays BLOCKED until pre-implementation cells are PRESENT → independent
test author records a test obligation → CIT-P/CIT-E with human gate (interface change) → checkpoints → model/tool
routing → `gov verify product` runs `cargo test` → fresh-agent continuation from a new session.

**First-run path: provision, then install (OWNER-DECISION-P2-0002).** The harness provisions each scenario machine with the certification suite's throw-away test root (`tests/certification/common.rs::provision`, published-seed keys — never a production root) and installs a release signed under it (`gov init --source <signed release>`; `common::signed_source`). A machine with no trust anchor refuses kernel material from any external source; only the `gov` binary's own embedded payload may be installed there, as a marked bootstrap installation that is never presented as current, verified or certified.
