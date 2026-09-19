//! Migration/adoption engine (framework §79, protocol stages A1-A7): inventory → classification → target path map →
//! batched execution with reference updates, ledger, snapshots and rollback → independent verification.
pub mod classify;
pub mod executor;
pub mod extraction;
pub mod framework;
pub mod identity;
pub mod inventory;
pub mod ownership;
pub mod planner;
pub mod references;
pub mod refs;
pub mod verify;
