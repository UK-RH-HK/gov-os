# Fixture 1 — Greenfield (Rust governed project)

A brand-new Rust crate (`orders-ledger`) with no governance. Language deliberately differs from nothing in
particular: the Governance OS core is Rust too, but the fixture proves ecosystem resolution (Cargo) and native test
execution for a governed project, and every other fixture uses a different language (Python, TypeScript, mixed).

Exercised by `tests/certification/greenfield.rs`:
product ideation (PRJ) → scenarios → feature-readiness gaps → readiness planner generates research/data/test-design
tasks in the same DAG → implementation task stays BLOCKED until pre-implementation cells are PRESENT → independent
test author records a test obligation → CIT-P/CIT-E with human gate (interface change) → checkpoints → model/tool
routing → `gov verify product` runs `cargo test` → fresh-agent continuation from a new session.
