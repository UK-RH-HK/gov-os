# Trust-domain decomposition

The target architecture should not use one protocol to solve every trust problem. Each domain has a different authority, threat model, evidence and lifecycle.

| Domain | Authority / anchor | Required guarantee | Not guaranteed |
|---|---|---|---|
| Product governance | owner-approved constitution, decisions and contract | deterministic precedence; no lower layer weakens it | identity of a remote human unless adapter authenticates them |
| Release publication | offline root and delegated release-signing keys | downloaded release metadata and payload bytes are authorized and untampered | build process was honest |
| Local installation | installed trust root, local operator/admin policy, atomic installer | verified bytes are installed/used; rollback policy enforced | global knowledge of unseen revocations while offline |
| Build provenance | CI identities, source/input lock, attestations, reproducible build evidence | trace source/inputs/builders to artifacts | absence of compiler backdoors without stronger bootstrap evidence |
| Independent certification | fresh verifier evidence and owner release decision | candidate meets declared tests and support envelope | cryptographic authenticity of distribution by itself |
| Project repository | kernel release pin plus project overlay | project cannot weaken kernel floors; native layout preserved | repository writer is trusted to publish framework releases |
| Tool/plugin execution | kernel policy plus OS-written registry | descriptor cannot authorize itself; permissions and bytes bound | plugin output is truthful |
| Knowledge/retrieval | authoritative records plus derived indexes | deterministic inputs outrank retrieval; rebuildable and freshness-aware | semantic relevance makes content authoritative |
| Operational currency | signed metadata plus trusted-enough local time/refresh path | bounded freshness when fresh data is actually obtained | knowledge of data never received |
| Organizational custody | named roles, hardware tokens and ceremony evidence | policy-defined separation and dual control | genuine human independence solely from key IDs/signatures |

## Boundary rules

1. Release authenticity must not depend on project repository files, `framework.lock`, an unsigned manifest or data generated from the source being judged.
2. Build provenance is evidence about how bytes were produced; it is not the distribution root.
3. Certification is an owner/reviewer decision over evidence; it is not a substitute for release signatures.
4. Local authorization is not transferable through a repository record.
5. Freshness is conditional on receiving signed current metadata and having an adequate time/sequence basis.
6. Retrieval and model outputs remain advisory.
7. The implementation can compose domains, but the acceptance contract must test each separately.

## How CP-1 blurred the domains

CP-1 bound release registration, reproducibility, compiler provenance, build environment, first-contact publication, mutable trust state, revocation, local gates, binary admission and policy eligibility into one custom acceptance predicate. This made a failure in any domain invalidate the entire Phase-1 architecture and made each input a new selector requiring proof.

The recommended architecture uses a small distribution root and treats higher-assurance build/certification evidence as signed, policy-evaluated attestations layered above it.
