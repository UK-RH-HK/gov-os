//! Implementer certification harness for the Governance OS release candidate (framework §75C, protocol §7).
//! Black-box: every scenario drives the `gov` binary through its JSON contract (API-0002); assertions inspect the
//! resulting repository, runtime and evidence tree. Independent verification is NOT performed here (release stays
//! READY_FOR_INDEPENDENT_OS_VERIFICATION until a separate verifier certifies it).
mod arch;
mod brownfield;
mod common;
mod failure_injection;
mod greenfield;
mod migration;
mod multi_machine;
mod repair;
mod repair2;
mod repair3;
mod section6;
mod srr;
mod srr_material;
mod update;
mod upstream;
mod ws03;
mod ws03_r3;
mod ws04r2;
mod ws04r3;
mod ws05;
mod ws05r3;
mod ws06;
mod ws06r3;
mod ws07;
mod ws08;
mod ws08_r2;
mod ws08_r3;
