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
pub mod doctor;
pub mod error;
pub mod graph;
pub mod init;
pub mod kernel;
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
pub mod records;
pub mod recovery;
pub mod release;
pub mod retrieval;
pub mod routing;
pub mod schemas;
pub mod security;
pub mod skills;
pub mod status;
pub mod tools;
pub mod update;
pub mod upstream;
pub mod util;
pub mod verification;

pub const FRAMEWORK_NAME: &str = "agentic-engineering-os";
pub const VERSION: &str = "4.1.4";
pub const CLI_VERSION: &str = "4.1.4";
pub const RUNTIME_VERSION: &str = "4.1.4";
pub const INDEX_VERSION: &str = "4.1.3-idx2";
pub const RUNTIME_DIR: &str = ".governance-runtime";

pub use error::{GovError, Result};
pub use project::Project;
