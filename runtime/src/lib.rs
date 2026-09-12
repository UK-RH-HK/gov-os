//! Governance OS deterministic core (D-0002: Rust-first control plane, polyglot capabilities behind API-0001).
//!
//! Logical layout mapping: `runtime/` (this crate) = memory, retrieval, graph, code-intelligence, context, CIT,
//! orchestration, checkpoints, observability, lifecycle operations; `cli/` = the `gov` binary.

pub mod error;
pub mod util;
pub mod paths;
pub mod kernel;
pub mod lock;
pub mod schemas;
pub mod policy;
pub mod records;
pub mod project;
pub mod security;
pub mod memory;
pub mod code_intelligence;
pub mod capabilities;
pub mod graph;
pub mod retrieval;
pub mod context;
pub mod orchestration;
pub mod checkpoints;
pub mod cit;
pub mod routing;
pub mod skills;
pub mod tools;
pub mod observability;
pub mod adapters;
pub mod doctor;
pub mod verification;
pub mod init;
pub mod migrations;
pub mod adopt;
pub mod update;
pub mod release;
pub mod upstream;
pub mod recovery;
pub mod status;

pub const FRAMEWORK_NAME: &str = "agentic-engineering-os";
pub const VERSION: &str = "4.1.2";
pub const CLI_VERSION: &str = "4.1.2";
pub const RUNTIME_VERSION: &str = "4.1.2";
pub const INDEX_VERSION: &str = "4.1.2-idx1";
pub const RUNTIME_DIR: &str = ".governance-runtime";

pub use error::{GovError, Result};
pub use project::Project;
