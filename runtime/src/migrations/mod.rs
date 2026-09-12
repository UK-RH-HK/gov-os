//! Migration/adoption engine (framework §79, protocol stages A1-A7): inventory → classification → target path map →
//! batched execution with reference updates, ledger, snapshots and rollback → independent verification.
pub mod inventory;
pub mod classify;
pub mod planner;
pub mod refs;
pub mod executor;
pub mod verify;
pub mod framework;
