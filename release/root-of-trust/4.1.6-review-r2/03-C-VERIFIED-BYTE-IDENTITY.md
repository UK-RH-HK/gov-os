# C — Verified-byte identity and TOCTOU

## 1. Proof sketch: enforced bytes = authenticated content identity (inside one `gov` process)

Assumptions:
- TA-1: the binary is genuine.
- TA-2: process memory is isolated.
- TA-3: SHA-256 and Ed25519 are sound.
- TA-6: the secure primitives of `18` §3 are present.

1. The statement payload `P` is decoded once. PAE verification and parsing use the same buffer (`18` §1), so `D =
   SHA-256(P)` binds everything parsed.
2. The installed tree is enumerated and each file is read **once** through `SecureDir`. That means `openat2` with
   `RESOLVE_BENEATH | RESOLVE_NO_SYMLINKS | RESOLVE_NO_MAGICLINKS | RESOLVE_NO_XDEV`, or component-wise `O_NOFOLLOW`
   with an `fstat` type check. Each buffer is digested and compared with `RCS(D)` (`18` §6 steps 3–5, VU-1).
3. The KernelSnapshot keeps exactly those buffers. VU-7 and the GovernedFs read guard make it the only source of kernel
   content in the process.
4. Enforcement is a function of the snapshot bytes, the TPS and the overlay. For every path, the enforced kernel bytes
   are therefore identical to the bytes whose digest is `RCS(D)[path]`, for the life of the snapshot. ∎

**Installation.** Files are staged from VerifiedBlobs (VU-3), read back through held handles (VU-4), exchanged
atomically (VU-5), and a post-commit snapshot must satisfy CI equality (VU-6). A divergence introduced anywhere between
buffer and commit is detected before the committed state is used. Automatic rollback is itself re-evaluated and fails
closed.

**The proof needs three conditions the pack does not state:**
- **(C1)** No unit of work may run against a snapshot whose identity has since been superseded or revoked. This is
  unstated for long-lived processes (R2-M7).
- **(C2)** Kernel content consumed **outside** `gov`, by agents reading kernel files and rendered adapters from disk,
  is not covered (R2-M8).
- **(C3)** Byte binding guarantees *the authentic bytes*, not *adequate policy*. Weak unfloored content in authentic
  bytes is R2-H1, not a byte-binding failure.

RV-H3, as reproduced by the prior review's R2b, is closed by design for the `gov` process.

## 2. Attacks

| # | Attack | Revision 2 control | Result | Finding |
|---|---|---|---|---|
| C-1 | Swap a source file after verification | read-once buffers; the source is never re-read (VU-1, VU-2) | closed | — |
| C-2 | Swap an installed file during use (R2b) | enforcement reads snapshot bytes only (VU-7) | closed for the `gov` process | — |
| C-3 | Replace a parent (`governance/`, `governance/kernel/`, `policies/`) with a symlink | `RESOLVE_NO_SYMLINKS` / per-component `O_NOFOLLOW`; the PPS includes the directory entries | closed. Ancestors above the repository root are pinned when the root handle is opened. | — |
| C-4 | Bind mount, mount or path substitution | `RESOLVE_NO_XDEV`; reparse-point refusal on Windows | Closed for mounts inside the tree. A user-namespace or FUSE filesystem at or above the root can serve different bytes to later readers that are not `gov`. Read-once still binds `gov`. Out of scope under TA-2; document it. | — |
| C-5 | Hard link to a staged file, written after read-back and before exchange | `O_NOFOLLOW` and `fstat` accept hard links; VU-6 detects the change after commit → automatic rollback | fails closed, but only after the exchange. An `st_nlink == 1` check on staged and installed files would detect it earlier. | R2-L2 |
| C-6 | Concurrent same-user mutation during a load | shared/exclusive advisory locks; identity checks | correct: A3 ignoring locks produces refusals only | — |
| C-7 | File changed between the final read-back and the atomic exchange | VU-6 CI equality → RB-1 | closed (fails closed) | — |
| C-8 | Crash during the transaction | journal phases, `IN_TRANSACTION`, `20` §5 | Closed on one machine. **`governance/.tx/` sits inside the Git-tracked `governance/` (`08` §2) and nothing excludes it from version control.** A committed journal puts every clone into `IN_TRANSACTION`. | R2-M9 |
| C-9 | Stale temporary tree | exclusive random `.tx/<TX>`; `IN_TRANSACTION` until `gov recover` | closed | — |
| C-10 | Manipulated recovery journal | `20` §5 re-authentication and downgrade policy against the lock and the VTS record | Closed where a VTS record exists. On a fresh clone, a forged `swapped` journal plus a lock naming the `.prev` identity exchanges back without a gate (this is RR-2). **`overlay.prev` is restored with no computed-weakening check.** | R2-H2, R2-M9 |
| C-11 | Concurrent installs | exclusive `flock` on `.tx/LOCK` | closed | — |
| C-12 | Runtime reading disk after the snapshot is built | VU-7; GovernedFs read guard; conformance by interception | Closed inside `gov`. The overlay and records are read at each use by design; they are T4 and strengthen-only for floored keys. Independence of the conformance evidence: see `07` §2. | — |
| C-13 | **Long-lived process** across an update, a TPS raise or a `refuse_operation` revocation | `18` §6 step 8 keeps the snapshot "for their lifetime". The shared lock is held only while loading. Writers of project state never compare their snapshot CI with the installed identity. | **open.** The planned MCP server (`cli/src/main.rs:234, 890`) would enforce a superseded or revoked policy root indefinitely. VR-1 ("the next process detects") has no next process. | R2-M7 |
| C-14 | **Agent consumption from disk** | none. Adapters tell agents "Canonical sources: governance/kernel/" (`framework/adapters/generic/template.md:4`). VU-8 stamps the CI in `governance/generated/adapter-manifest.json`, which A2 can rewrite together with the adapter body. | **open** for AS-4 content | R2-M8 |
| C-15 | Exchange of the whole trust directory during update or rollback | `18` §4 exchanges `governance/trust` with `trust.next`; RB-1 exchanges back with `trust.prev` | **Open.** Statements accepted into the PTR by the newer transaction disappear from `governance/trust/`, which contradicts R-RB-5 and RB-12 on every other clone. | R2-M9 |

## 3. Residual 2 (same-user modification after the snapshot)

Acceptable for short-lived CLI processes. Not bounded for C-13 and C-14. See `09` §1.
