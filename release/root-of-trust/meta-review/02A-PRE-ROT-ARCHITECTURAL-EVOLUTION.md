# Pre-RoT architectural evolution

## 4.1.2: broad product, incomplete enforcement

The first candidate attempted nearly the entire original Governance OS at once. The independent review found genuine gaps: semantic plugin mismatch and deadlock, unenforced roles, mutation-scope gaps, sensitivity leakage, weak human-gate enforcement, inadequate reranking/benchmark selection, incomplete checkpoints and architecture evidence. These findings were anchored in the baseline or the Rust/polyglot amendment.

## 4.1.3: repairs exposed adjacent authorization flaws

The first repair fixed the original critical/high findings. Fresh tests then showed that:

- CIT could treat a presented or declined gate as approval;
- project policy could lower authority and security floors;
- a plugin descriptor could become executable authority;
- release/update provenance and mutation observation were incomplete.

These were not arbitrary goalposts. They were direct contradictions of baseline precedence, least authority, human-gate and release-update guarantees.

## 4.1.4: general trust-boundary hardening

The second repair added:

- authoritative gate derivation;
- kernel-owned policy precedence;
- governed plugin registration and byte binding;
- portable release identity;
- observed mutation scope;
- truthful migration/update ledgers.

The next review found a common remaining pattern: lower-trust artifacts still asserted their own authority or provenance. This led to D-0007.

## 4.1.5: D-0007 and the circular installation boundary

D-0007's principle is sound: an artifact cannot establish the authorization, verification or provenance fact that governs itself. Its post-install controls were materially successful:

- installed-kernel tampering failed closed;
- plugin descriptors could not authorize themselves;
- exceptions resolved to governed decisions;
- tool security reviews could not self-attest.

But D-0007 defined a trusted installed kernel using a manifest and lock that the installer could regenerate from the same untrusted source. V-H3 therefore showed that integrity was being mistaken for authenticity during init/update.

## The correct narrow inference from V-H3

V-H3 necessarily required an independent authenticity anchor for release ingress. It did not, by itself, require:

- custom first-contact source custodians;
- a separate compiled admitter;
- 24-hour mutable state currency;
- multi-axis compiler/environment reproduction;
- root-signed provenance ontologies;
- a complete decision register over every schema field.

Those later controls were alternative ways of increasing assurance. They became binding only when the owner adopted Contract A2 and the OP records.

## Controls to preserve

The pre-RoT cycle produced valuable, independently tested architecture. The rebase must preserve policy precedence, plugin governance, gate integrity, mutation observation, release immutability, update/rollback ledgers, sensitivity rules, rebuildability and the D-0007 trust-direction rule. See `14-EARLIER-CONTROLS-STILL-VALID.md`.
