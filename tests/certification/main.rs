//! Implementer certification harness for the Governance OS release candidate (framework §75C, protocol §7).
//! Black-box: every scenario drives the `gov` binary through its JSON contract (API-0002); assertions inspect the
//! resulting repository, runtime and evidence tree. Independent verification is NOT performed here (release stays
//! READY_FOR_INDEPENDENT_OS_VERIFICATION until a separate verifier certifies it).
mod common;
mod arch;
mod greenfield;
mod brownfield;
mod migration;
mod update;
mod upstream;
mod multi_machine;
mod failure_injection;
