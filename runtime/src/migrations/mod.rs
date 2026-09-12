//! Migration/adoption engine (framework §79, protocol stages A1-A7): inventory → classification → target path map →
//! batched execution with reference updates, ledger, snapshots and rollback → independent verification.
pub mod classify;
pub mod executor;
pub mod framework;
pub mod inventory;
pub mod planner;
pub mod refs;
pub mod verify;
