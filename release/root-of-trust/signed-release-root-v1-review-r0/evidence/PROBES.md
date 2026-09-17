# Probe and reproduction record — AR-0023

All probes were run read-only inside the review worktree
`/…/scratchpad/wt/srr1-r0-review` at HEAD `166ac4cff484160c7176e0ce15b23e59820074f2`,
branch `phase1/srr1-r0-review`. No `GOV_*` environment variable was set and no
Governance OS binary was built or executed (none was required: this is an
architecture-document review). Nothing outside this worktree was written.

## PR-1 — Mandated hash verification (STOP-condition check)

```
$ sha256sum release/orchestration/phase-1/GATES/OWNER-DIRECTIVE-0004-SIGNED-RELEASE-ROOT-REBASE.md \
            release/root-of-trust/signed-release-root-v1/01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md \
            Governance_OS_Capability_Acceptance_Contract_v3.md
26243019d09e07617a63cf575c3e5e59cad307a7ac38100116dbbb3300f2a1ba  …/OWNER-DIRECTIVE-0004-SIGNED-RELEASE-ROOT-REBASE.md
70977d11b778c4a8391a65cb3e0f53103bcc1e565de595c1e83150797f1699c1  …/01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md
4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3  Governance_OS_Capability_Acceptance_Contract_v3.md
```

Result: **all three match the values supplied in the role instruction exactly.**
No STOP condition. Contract v3 was read from this verified file only; no contract
content was reconstructed from memory or from generated documentation.

## PR-2 — Candidate identity (are the seven reviewed inputs byte-identical at HEAD?)

Git blob ids compared between the reviewed-candidate commit `5fd8358` and HEAD `166ac4c`:

| Input | blob id | identical |
|---|---|---|
| OWNER-DIRECTIVE-0004 | `d7f27ca709eab9ac81b8256bb75dc76049af0e53` | yes |
| `spec/decisions/D-0009.yaml` | `de0788cf5376698d6c4fd70e2aa4877676f23a6f` | yes |
| `spec/architecture/ARCH-0003.yaml` | `af29e68aeb16428fbc309a3d235c96a10acd83ca` | yes |
| `…/00-ARCHITECTURE.md` | `b73973cad4dc9cdd240d8bd923b92e7bcc5c135b` | yes |
| `…/01-FROZEN-…-BOUNDARY.md` | `75ebcc0b2b049b5db26f6103f7029e8fb2924a75` | yes |
| `…/02-OP-1-OP-16-DISPOSITION.md` | `943ce3ca5b06d80f4c1e1cb35fa28f6420064d39` | yes |
| `…/03-TRANSITION-MAP.md` | `0135fc17e2ab5585ff4311a59c90059fb724300c` | yes |

`git diff --stat 5fd8358 166ac4c` touches only four orchestration files
(`AR-0023.run.yaml`, `AGENT_RUNS/README.md`, `ORCHESTRATOR_STATE.yaml`,
`PHASE_1_LEDGER.md`). The candidate-identity claim in the role instruction is
**confirmed**; reviewing at HEAD is equivalent to reviewing at `5fd8358`.

## PR-3 — Time/clock declaration sweep (basis for SRR-R0-M1)

Case-insensitive sweep over all seven candidate inputs for
`clock|time|wall|NTP` (excluding the compound words `timestamp`, `runtime`,
`lifetime`, `sometimes`):

```
(no matches)
```

Result: the candidate set contains **no statement of any kind about the local
clock or time source** — not as an assumption, not as a non-guarantee, and not as
a parameter. `timestamp` occurs only as the name of the TUF metadata role.

## PR-4 — Non-production trust-mode sweep (basis for SRR-R0-L4)

Sweep over the candidate inputs for
`dev_mode|dev-mode|insecure|unsigned|test mode|certified production|masquerad`:
only two hits, both in the opposite sense (no private key may reach an ordinary
developer workspace). Sweep over the shipped 4.1.5 product source
(`runtime/`, `cli/`, `framework/`, `spec/`) for
`dev_mode|dev-mode|insecure|unsigned|test_mode|GOV_TRUST|GOV_DEV|bootstrap_mode|trust_mode|allow_untrusted|skip_verify`:

```
(no matches)
```

Result: no dev/test/bootstrap trust mode exists either in the candidate
architecture or in the current implementation. Contract v3 A2 bullet 8 is
therefore **not falsified** by this candidate; it becomes an R1 obligation the
moment any non-production trust anchor is introduced. Recorded as SRR-R0-L4,
non-blocking.

## PR-5 — Floor/recovery scoping (basis for SRR-R0-H1)

Every occurrence of `high-water | floor | minimum secure` and every occurrence of
`recover` was enumerated across `00-ARCHITECTURE.md` and `ARCH-0003.yaml`.

Floor-bearing statements found:

- `ARCH-0003.yaml:86-87` — "Clients persist the highest valid root/metadata versions and minimum secure release they have observed. **Rollback** below those floors is refused."
- `00-ARCHITECTURE.md:32` (Security objective) — "**rollback** below known signed floors is refused"
- `00-ARCHITECTURE.md:79` (ingress table, **rollback** row) — required authenticated object: "signed release not below security/high-water floor"
- `00-ARCHITECTURE.md:103` — "A client never accepts an older **metadata** version than its protected high-water."
- `00-ARCHITECTURE.md:104` — "A signed minimum secure release prevents unsafe **rollback**…"

Recovery-bearing statements found:

- `00-ARCHITECTURE.md:80` (ingress table, **recovery** row) — required authenticated object: "authenticated recovery target **or installed valid recovery path**"; local authority: "bounded local recovery authority"; state effect: "restore one complete valid state". **No floor term appears in this row.**
- `ARCH-0003.yaml:91` — "A known revoked binary is limited to inspection, export, **recovery** and uninstall…"
- `ARCH-0003.yaml:47` — "One verifier evaluates the same policy for init, adopt, update, reinstall, rollback and **recovery**."

Result: **confirmed.** Every floor statement is lexically scoped to `rollback`;
the `recovery` ingress is the only one of the six whose required authenticated
object admits a non-metadata alternative, and it is the only backward-capable
ingress with no floor term. Line 103's floor binds *metadata* versions, which an
"installed valid recovery path" restore does not consult at all. See
`../10-BLOCKING-FINDINGS.md#srr-r0-h1` for the bounded counterexample.

## PR-6 — Privileged ingress enumeration against the product's real command surface

Command tokens extracted from `cli/src`: `init`, `adopt`, `update`, `migrate`,
`recover`, `release`, `tools`, `plugins`, `skills`, `verify`, `doctor`.

| Surface | Covered by the ARCH-0003 ingress table? | Disposition |
|---|---|---|
| `init`, `adopt`, `update`, `recover` | yes (plus `reinstall`, `rollback`) | covered |
| `migrate` | not listed as an ingress | no new external bytes; migration identities are bound in release/targets metadata and executed from already-verified installed bytes under D-0007. Not a gap. |
| `release` | publisher-side, not a client ingress | out of scope |
| `verify`, `doctor` | read-only | not privileged ingress |
| `tools`, `plugins`, `skills` | deliberately a separate trust domain | frozen boundary R0 item 11 scopes plugin/retrieval trust *out* of the release root; Contract v3 F2/F3/F4 govern it by hash pin, approval and kernel-owned registration. Recorded as SRR-R0-L6 (`NEW_OWNER_DECISION_REQUIRED`), non-blocking. |

The only network-capable module in the product source is `runtime/src/upstream.rs`
(the Q4 Upstream Export Gate, outbound).

## PR-7 — Non-mutation checks required by the role prohibitions

```
spec/decisions/D-0008.yaml    pre-rebase 09f8b4f = HEAD = ce163e786e81068cc732899db2a9ed9854b55b21
spec/architecture/ARCH-0002.yaml pre-rebase 09f8b4f = HEAD = cdc0d6864d3b258ca3959053402ce0ee70e31a2e
```

Both remain `status: PROVISIONAL`, `proposal_state: PROPOSED`, `in_effect: false`.
The rebase did not activate or mutate them, and this review does not. No file under
`release/verification/**`, `release/releases/**`, `release/root-of-trust/4.1.6*`,
`release/root-of-trust/meta-review/**` or any prior kernel payload was modified;
the sole directory written by this run is
`release/root-of-trust/signed-release-root-v1-review-r0/` plus the AR-0023 report.
