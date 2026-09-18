//! Governance OS deterministic core (D-0002: Rust-first control plane, polyglot capabilities behind API-0001).
//!
//! Logical layout mapping: `runtime/` (this crate) = memory, retrieval, graph, code-intelligence, context, CIT,
//! orchestration, checkpoints, observability, lifecycle operations; `cli/` = the `gov` binary.

pub mod adapters;
pub mod adopt;
pub mod authority;
pub mod capabilities;
pub mod checkpoints;
pub mod cit;
pub mod code_intelligence;
pub mod context;
/// Governance Capability Acceptance Contract v3: hash-bound source, compiled form and evidence map.
pub mod contracts;
pub mod doctor;
pub mod error;
pub mod exceptions;
pub mod graph;
pub mod init;
pub mod kernel;
pub mod kernel_trust;
pub mod lessons;
pub mod lock;
pub mod memory;
pub mod migrations;
pub mod observability;
pub mod orchestration;
pub mod paths;
pub mod policy;
pub mod policy_coverage;
pub mod policy_precedence;
pub mod project;
pub mod qualification_oracle;
pub mod records;
pub mod recovery;
pub mod release;
pub mod retrieval;
pub mod routing;
pub mod schemas;
pub mod security;
pub mod skills;
/// Signed Release Root v1 (`ARCH-0003`): signed metadata, the one verification policy, verified-byte binding,
/// protected floors and break-glass recovery.
pub mod srr;
pub mod status;
pub mod tools;
pub mod update;
pub mod upstream;
pub mod util;
pub mod verification;

pub const FRAMEWORK_NAME: &str = "agentic-engineering-os";
pub const VERSION: &str = "4.1.5";
pub const CLI_VERSION: &str = "4.1.5";
pub const RUNTIME_VERSION: &str = "4.1.5";
pub const INDEX_VERSION: &str = "4.1.5-idx3";
pub const RUNTIME_DIR: &str = ".governance-runtime";

pub use error::{GovError, Result};
pub use project::Project;
