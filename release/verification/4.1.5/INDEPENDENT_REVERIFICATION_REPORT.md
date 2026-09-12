# Independent OS Re-Verification Report — agentic-engineering-os repair candidate 4.1.5

| | |
|---|---|
| **Verdict** | **OS_RELEASE_CANDIDATE_REJECTED** (repairable; one new HIGH trust-boundary defect — builder repair delta in §12) |
| Verifier | Independent Governance OS Verifier and Test Author — fresh session, no builder context, no continuation of any previous verifier session (Claude Opus 4.8 / Opus 5, 1M) |
| Date | 2026-09-12 |
| Candidate | branch `release/4.1.5-rc1`, tag `v4.1.5-rc1`, commit `da9c8518d3fddba6f37bafb4d046ca313335ec1f`; payload `release/releases/4.1.5/` (release_commit `25dac6ef…dcaf`, release_hash `962f9848…a314b`) |
| Toolchain | rustc/cargo 1.98.1, clippy 0.1.98, rustfmt 1.9.0, Python 3.12.3 (harnesses only), git 2.43.0, Linux x86_64 WSL2 (`evidence/toolchain.txt`) |
| Independence | Nothing in the builder's or the three previous verifiers' reports was taken on trust. All builds and suites ran from **fresh `git clone`s of the candidate tag** (4.1.5), the 4.1.2 runtime (`8ad06be`) and the 4.1.4 tag. All three previous held-out harnesses were re-run **byte-identical** (sha256 confirmed against verifier commits `9563192` / `9cb05d8` / `f4b3429`). A **fourth held-out harness (`heldout-wv/harness_wv.py`, WV-01…WV-06)** and an independent update/migration/rollback chain execution were authored in this session, unknown to the builder and to the three previous verifiers. |
| Artefacts | `heldout-wv/` (new harness + results), `evidence/` (V-H3 reproduction, migration-chain report, three prior-harness reruns, WV run, toolchain), `VERDICT.md` |
| Not modified | No implementation/runtime/kernel source, kernel data, fixture, builder test, released payload, or previous-verifier artefact was modified. The only additions are under `release/verification/4.1.5/`. The 4.1.5 manifest certification block was **not** edited by this session (same convention as 4.1.3/4.1.4); `VERDICT.md` carries the exact block for the release owner. |

## 0. Summary

The third repair iteration is **substantially successful**. Every finding of the 4.1.4 re-verification —
**V-H1** (a plugin descriptor authorising itself), **V-H2** (constitutional floors read from an unverified installed
kernel) and **V-M1** (self-attested policy exceptions) — is **genuinely repaired at the root cause** and survived a
fresh, independently authored attack set. The intermittent **ETXTBSY** plugin-spawn race is repaired and holds under
repeated concurrent execution. Every CRITICAL/HIGH finding of the 4.1.2, 4.1.3 and 4.1.4 verifications remains repaired;
no independently confirmed repair has regressed. All three previous harnesses reproduce exactly, with only
frozen-input/identity failures. The 4.1.5 release payload is internally sound: byte-identical to `framework/` at its
release commit, reproduces to the same `release_hash`, refuses in-place rebuild, carries no duplicate kernel YAML keys,
and its migration `M-4.1.4-4.1.5` truthfully declares its (empty) overlay changes. The architecture is materially
complete: the deterministic core is Rust-only with no Python/Node runtime dependency, memory is a genuine multi-layer
fabric, all derived state deletes and rebuilds deterministically across machines, and model/component choices are pinned
and replaceable. Six architecture pillars that were PARTIAL at 4.1.4 are now PRESENT_AND_SUBSTANTIAL.

The candidate is nevertheless **rejected** because one **new HIGH trust-boundary defect** was found by held-out testing:

> **V-H3 — `gov update` and `gov init` do not authenticate the update/install SOURCE payload before adopting it, and
> then re-mint the V-H2 trust anchor from the (possibly tampered) source.** A release payload with one kernel policy
> file altered to remove a constitutional security floor (`SECURITY_POLICY.never_index_classes`) — with its shipped
> `manifest.json`/`KERNEL_MANIFEST.json` left stale — installs cleanly through a properly answered update gate. Afterward
> `gov kernel trust` reports **`verified: true`**, doctor is clean, and a **restricted material record becomes indexed
> and retrievable** (proven against an intact-kernel control where the same record is excluded `sensitivity:restricted`).
> `gov release verify` detects the tampered source and the resulting `framework.lock.release_hash` diverges from the
> published release_hash, but **nothing in the update/init flow performs or prompts either check**. This is the
> install/update-time instance of exactly the pattern D-0007 was written to close — a lower-trust input (the source the
> operator points `--source` at) manufacturing a higher-trust fact (a "verified" kernel and its constitutional floors).

V-H3 is repairable within the existing architecture (§12). It is, however, the **fourth consecutive iteration** in which
a trust-anchor-authenticity defect of the same family has surfaced, so §13 records a root-cause escalation
recommendation for the owner alongside the ordinary-iteration repair delta.

## 1. Reproduction of builder evidence (fresh clone, clean build)

Executed in `scratchpad/clone415`, a `git clone` checked out at `v4.1.5-rc1`
(`git rev-parse HEAD = da9c8518…ec1f`, `git status --porcelain` empty).

| Suite | Builder claim | This session | Evidence |
|---|---|---|---|
| `cargo build --release` (fresh clone) | PASS | **PASS**, exit 0, 0 warnings, ~72 s | `evidence` |
| Rust unit tests (gov-runtime) | 19 passed / 0 | **19 passed / 0** | `evidence/harness reruns log`, cargo-test |
| Certification suite | 49 passed / 0 | **49 passed / 0**, 6.19 s | cargo-test |
| Python capability plugin tests | 4 passed | **4 passed** | pytest |
| Clippy `--workspace --all-targets` | 0 warnings | **exit 0, 0 warnings** | clippy |
| `cargo fmt --all -- --check` | PASS | **exit 0, no diff** | fmt |
| `gov release verify release/releases/4.1.5` | ok | **ok**: 0 modified/missing/added; certification `READY_FOR_INDEPENDENT_REVERIFICATION` | §5 |
| `ldd target/release/gov` | libc-only | **`libgcc_s`, `libm`, `libc`, `ld-linux` only** | arch survey |

Every implementer claim reproduced. The binary reports version/cli/runtime `4.1.5`, index `4.1.5-idx3`.

## 2. Previous held-out harnesses — unchanged reruns

All three harnesses executed unmodified (sha256 identical to the verifier commits), with `GOV_VERIFIER_OUT` redirected
so no previous-verifier artefact was written. Harness v2 was given a 4.1.2 binary built from `8ad06be`.

| Harness | Verifier's original run | Builder's 4.1.5 rerun (claimed) | **This session (4.1.5)** |
|---|---|---|---|
| First (`4.1.2/heldout/harness.py`, 38 scenarios) | 12 / 25 / 1 / 0 | 36 / 1 / 1 / 0 | **36 PASS / 1 FAIL (HV-08b) / 1 INFO / 0 ERROR** |
| Second (`4.1.3/heldout-new/harness_v2.py`, 15) | 6 / 9 / 0 / 0 | 13 / 2 / 0 / 0 | **13 PASS / 2 FAIL (NV-09, NV-19) / 0 ERROR** |
| Third (`4.1.4/heldout-v3/harness_v3.py`, 16) | 13 / 3 / 0 / 0 | 14 / 2 / 0 / 0 | **14 PASS / 2 FAIL (VV-05, VV-07) / 0 ERROR** |

**The three findings that carried the 4.1.4 rejection — VV-03, VV-04 and VV-14 — all now PASS** in the third harness.
No previously passing scenario regressed. The four residual failures are confirmed candidate-identity/history artefacts
(§4), not open defects.

## 3. Previous-finding repair matrix (independently re-derived and attacked)

Each row was verified by reading the implementation and attacking it with the new WV harness (`heldout-wv/`) and manual
probes the builder did not have.

| ID | Claimed repair | Independently observed | Independent attack result | Verdict |
|---|---|---|---|---|
| **V-H1** plugin descriptor self-authorises | Authority floor from verified kernel applies to **every** execution; `approved_roles`/`provenance`/`status` in the descriptor are advisory; registration is an OS-written `governance/generated/plugin-registry.json` binding id+version+descriptor-sha256+impl-sha256; edited/re-versioned/id-spoofing descriptors fail `PLUGIN_REGISTRY_MISMATCH` | `governance.rs::authorize` (`runtime/src/capabilities/governance.rs:227`) + `registry.rs`. **WV-01 all clean:** L0 with `approved_roles:["all"]`+forged `provenance`+`status:active` → not usable, no command executed during `rebuild-memory`; a **hand-forged registry entry** keyed to the real descriptor bytes → still not usable at L0 or L1 (floor read from verified kernel, not the registry); a genuinely-registered plugin is **not** executed during an L0 rebuild (floor applies to every execution); an edited descriptor after registration → `PLUGIN_REGISTRY_MISMATCH`, not usable | **REPAIRED** (robust) |
| **V-H2** floors read from an unverified installed kernel | `kernel_trust` authenticates the installed payload against `KERNEL_MANIFEST.json` **and** the manifest against `framework.lock.kernel_manifest_hash`; on failure the embedded baseline is substituted explicitly and every mutating op fails `KERNEL_TAMPERED` until reinstall or an L4+ fingerprint-bound gated override | `kernel_trust.rs`; `guard_write`/`rebuild` call `kernel_trust::guard`. **WV-02 all clean:** tampering the installed `POLICY_PRECEDENCE.yaml` → `verified:false`, weakening override **not applied**, `task create` (L0 and L4), `rebuild-memory` and `cit propose` all refused `KERNEL_TAMPERED`; read paths still work from the embedded baseline and surface the substitution (`policy overrides.kernel_trust.verified=false`, doctor D029 CRITICAL); L3 override denied, L4 override raises a gate, refused until answered, allowed after; a **different subsequent tamper re-refuses** (fingerprint-bound) | **REPAIRED** (robust) — but the *install/update-time* authenticity of the anchor is not established: **V-H3, §11** |
| **V-M1** exceptions are self-attested | An exception applies only when `decision` resolves to an existing ACTIVE, non-superseded/revoked/expired decision, approved at `grant_policy_exception` (or human), that names the exception id or its policy key, scoped to this project; never for security/authority keys | `exceptions.rs::validate` + `policy.rs`. **WV-03 all clean (10 cases):** fabricated / wrong-type / wrong-scope / superseded / revoked / expired / insufficient-authority all refused; a valid, human-approved, in-scope exception on a relaxable key **applies**; a **valid decision aimed at a SECURITY or AUTHORITY key is still refused** (precedence `exception_relaxable` gate holds) | **REPAIRED** (robust) |
| **ETXTBSY** plugin spawn race | `host::invoke` retries the spawn on `os error 26` for ~0.5 s | `host.rs:198`. **WV-05:** 24 concurrent write-then-exec invocations, **0** `PLUGIN_SPAWN_FAILED`/ETXTBSY; concurrent content rewrites correctly refused `PLUGIN_PIN_MISMATCH` (a governance decision, not a spawn race) | **REPAIRED** |
| **D-0007 new finding** tool-install self-attested `security_review` | `tools::install` counts `security_review:passed` only when `security_review_record` resolves to a governed record | `tools.rs:377`. **WV-04:** self-attested → not installed (gate); fabricated record id → not installed (gate); real governed record → condition satisfied | **REPAIRED** |
| 4.1.2/4.1.3/4.1.4 CRITICAL/HIGH (C-N1, H-N1/2, C1/C2, H1–H7, M-N*) | preserved | Architecture survey + WV-06 + prior-harness reruns: **none regressed; six pillars upgraded PARTIAL→P&S** | | **PRESERVED** |

## 4. HV-08b, NV-09, NV-19, VV-05, VV-07 — independently confirmed as identity/history artefacts

- **HV-08b (FAIL by construction).** The bundled `hashed-ngram` baseline embedder has no paraphrase/morphology
  capability; framework §14.3 forbids hard-coding an embedder, so the deliverable is the benchmark-and-select
  *mechanism*, recorded in D-0006 / RES-0001. The mechanism is executable and independently exercised: `gov memory
  benchmark` compared candidates and `gov memory verify` reported recall@k 1.0 / MRR 1.0 / stale 0.0 / superseded 0.0.
  **Non-blocker, unchanged.**
- **NV-09 (reads the immutable 4.1.3 payload).** The sole duplicate kernel YAML key (`release-manifest`) lives in the
  frozen, rejected 4.1.3 payload. Independently re-derived with a strict duplicate-key loader over **all** `framework/`
  and `release/releases/4.1.5/` YAML → **no duplicate keys**. Repaired; the FAIL cannot change without mutating a
  released payload.
- **NV-19 (reads the immutable 4.1.3 migration).** 4.1.5 equivalent independently confirmed: `M-4.1.4-4.1.5` truthfully
  declares `overlay_template_changes: []` and the 4.1.4→4.1.5 overlay templates are **byte-identical** (so an empty
  declaration is honest); the three released prior migrations are byte-identical between the 4.1.4 and 4.1.5 payloads.
- **VV-05 / VV-07 (pinned to the 4.1.4 candidate identity).** VV-05 requires the released `KERNEL.yaml` to equal the
  working-tree `framework/KERNEL.yaml` and VV-07 requires HEAD to carry `v4.1.4-rc1` — necessarily false for a 4.1.5
  candidate. The **4.1.5 equivalents pass independently** (§5): released `KERNEL.yaml` == `framework/KERNEL.yaml`,
  `framework/`+`migrations/`+`tools/` unchanged since release commit `25dac6e`, `release verify` ok, reproduces the same
  `release_hash`, in-place rebuild refused.

## 5. 4.1.5 release identity, reproduction, immutability (VV-05/VV-07 equivalents) — PASS

| Check | Observed |
|---|---|
| `framework/KERNEL.yaml` vs released 4.1.5 `KERNEL.yaml` | **identical** |
| `framework`/`migrations`/`tools` changed since release commit `25dac6e` | **none** (empty diff) |
| `gov release verify release/releases/4.1.5` | **ok**: 0 modified / 0 missing / 0 added |
| `gov release build --version 4.1.5` into a temp dir | reproduces `release_hash 962f9848…a314b` (== manifest) |
| in-place rebuild | refused `RELEASE_IMMUTABLE` |
| duplicate kernel YAML keys across `framework/` + 4.1.5 payload | **none** |
| tag / branch | `v4.1.5-rc1` at HEAD; branch `release/4.1.5-rc1`; `main` untouched |
| certification status in manifest | `READY_FOR_INDEPENDENT_REVERIFICATION`, verifier empty (no self-certification) |

The 61 schema files that differ from the 4.1.4 payload are dominated by the `$id` version stamp
(`…/4.1.4/…` → `…/4.1.5/…`) plus the genuine `decision.schema.json` additions (`authorises_exceptions`,
`permits_policy_keys`, `applies_to_project`) — expected and benign for a version bump.

## 6. Migration / update / rollback chain through 4.1.5 (independently executed)

A consumer genuinely created by the **4.1.2 binary** was driven by the 4.1.5 candidate binary. Steps 1–7 all PASS
(evidence: `evidence/migration-chain-REPORT.md`):

- per-hop gates enforced (`--approve` before an answered gate → `applied:false`, INV-008); a gate answered for one hop
  does not authorise the next; `kernel trust verified:true` at every version; overlays and `spec/` byte-identical across
  the chain and restored byte-identical on rollback; ledger entries in `spec/reports/framework-updates.jsonl`; third
  rollback refused `SNAPSHOT_MISSING`; re-apply → `up_to_date`; older release → `downgrade`, refused; multi-hop
  4.1.2→4.1.5 supported with all three migrations under one gate; machine-B manifest_hash identical; a 4.1.4 consumer's
  hand-declared plugin and its (now-validated) exception survive update and rollback.

**Step 8 FAIL** is the V-H3 finding (§11), reproduced independently below.

## 7. New held-out test register (authored this session)

`heldout-wv/harness_wv.py` — black-box through `gov --json`; unknown to the builder and the three previous verifiers.
**6 PASS / 0 FAIL** (`heldout-wv/wv-results.json`).

| ID | Attack | Result |
|---|---|---|
| WV-01 | V-H1: L0 self-declared `approved_roles`/`provenance`/`status`; a hand-forged plugin-registry entry keyed to the real bytes; an L0 rebuild of a genuinely-registered plugin; an edited descriptor after registration | **PASS** (no execution below the floor; forged registry cannot lower the floor; edited descriptor → `PLUGIN_REGISTRY_MISMATCH`) |
| WV-02 | V-H2: tamper installed `POLICY_PRECEDENCE`; mutation refusal (L0/L4/rebuild/cit); read-path survival + substitution surfacing; L3 vs L4 override; fingerprint re-binding on a new tamper | **PASS** (all mutations `KERNEL_TAMPERED`; override fingerprint-bound) |
| WV-03 | V-M1: 10 exception cases incl. valid-apply and valid-decision-on-a-security/authority-key | **PASS** (only the genuine, in-scope, relaxable-key exception applies) |
| WV-04 | D-0007: tool-install `security_review` self-attestation vs fabricated record vs real governed record | **PASS** |
| WV-05 | ETXTBSY: 24 concurrent write-then-exec plugin invocations | **PASS** (0 spawn failures) |
| WV-06 | Regression: L0 authority, restricted exclusion, CIT decline finality, fresh-agent deterministic reconstruction across a clone | **PASS** |

Plus the independent update/migration/rollback chain (§6) and the V-H3 reproduction (§11).

## 8. Architecture completeness (independently re-surveyed)

Materially complete and improved over 4.1.4. Rust-only deterministic core (73 source files, ~22.8k lines; `ldd`
libc-only; init/rebuild/status/context run with a PATH containing only git + coreutils — no Python/Node). Memory is a
genuine multi-layer fabric (FTS5/BM25 `porter unicode61` pinned; SQLite vectors with brute-force cosine; 20-type edge
graph; regex code-intel + `code_intel` plugins; RRF fusion; parent/graph expansion; reranker hook; authority/stale/
superseded filtering; 8-layer bounded context compiler). Derived state deletes and rebuilds to an identical
`manifest_hash` across machines. Six pillars upgraded PARTIAL→P&S versus 4.1.4 (authority/policy engine, policy
precedence, capability/tool registry, role separation, sensitive-path handling, privilege gates) — the V-H1/V-H2/V-M1
repairs. Unchanged acceptable PARTIALs (all MEDIUM/LOW, none release-blocking): vector/graph stores fixed to SQLite (no
trait), regex code-intel (no bundled LSP/SCIP), no per-record git lineage, protocol-order migration batching,
token-level metrics proxied by characters/cost. ABSENT-with-a-decision: MCP (D-0004), bundled paraphrase embedder
(D-0006), JSON-RPC/HTTP transports. Nothing UNCLEAR. **No pillar that was P&S at 4.1.4 regressed.**

## 9. Answers to the mandatory questions (deltas from the 4.1.4 report)

1. **Architecture substantially complete?** Yes, materially, and improved.
2. **PARTIAL/ABSENT/UNCLEAR pillars?** As §8; none load-bearing for the release except that the trust-boundary is
   incomplete at the install/update ingress (V-H3).
3. **Deterministic core language?** Rust (`runtime/` + `cli/`; embedded kernel via `build.rs`).
4. **Rust-first exceptions?** None in the core; only optional capability plugins behind API-0001 (D-0002 §4).
5. **Core without Python?** Yes (`ldd` libc-only; restricted-PATH run succeeds).
6. **Non-Rust / mixed-language projects?** Yes (ecosystems for rust/python/node/go/… detected; language-tagged registry
   resolved against the governed project; mixed brownfield fixture preserved).
7–15. Structured state SQLite; lexical FTS5/BM25; vector SQLite brute-force cosine; graph SQLite BFS 20 edge types;
   code-intel regex+plugins; embedder builtin `hashed-ngram` (D-0006); reranker none-by-default + plugins; alternatives
   benchmarked (RES-0001 + verifiers); metrics recall@k/MRR/precision/stale/superseded/symbol/latency. **All pinned and
   replaceable; unchanged from 4.1.4 and re-confirmed.**
16–19. Routing tier-based, no provider name in the kernel; choices pinned/replaceable; all derived state deletes and
   rebuilds; a fresh agent reconstructs an identical `deterministic_hash` across a clone (WV-06).
20. **Top gap preventing release:** **V-H3** — the update/install path does not authenticate the source payload, so the
   V-H2 "verified kernel" guarantee is about internal self-consistency, not authenticity, for any kernel obtained via
   `gov update`/`gov init` from an unverified source.

Additional: **Are the previous CRITICAL/HIGH findings genuinely repaired?** V-H1, V-H2, V-M1 — yes, at the root cause,
robust under fresh attack. **New regressions/contradictions?** No behavioural regression; one new HIGH (V-H3). **Is
commit `da9c851` suitable for release certification (Prompt 3)?** **No** — not until V-H3 is repaired.

## 10. What is verified sound — do not regress

Rust-only deterministic core with an embedded kernel and no Python/Node dependency; the plugin authority floor from
verified kernel policy + the OS-written plugin registry (descriptor content and a forged registry cannot lower it); the
verified-kernel trust root refusing all mutations `KERNEL_TAMPERED` under a tampered installed kernel, fingerprint-bound
overrides, embedded-baseline substitution surfaced everywhere; governed policy exceptions resolved against real,
current, in-scope, sufficiently-approved decisions and never reaching security/authority keys; tool-install
security-review evidence; the ETXTBSY spawn-race retry; the full 4.1.2→…→4.1.5 upgrade with per-hop gates, byte-identical
overlay/`spec` preservation, ledgered rollbacks, snapshot consumption, downgrade refusal and identical multi-machine
manifest hash; release identity, reproduction and immutability; fresh-agent reconstruction; CIT gate integrity and
authority enforcement.

## 11. Critical Gap Register

### CRITICAL — none.

### HIGH

| ID | Gap | Evidence | Affected architecture | Risk | Required repair | Acceptance test |
|---|---|---|---|---|---|---|
| **V-H3** | `gov update` / `gov init` install the **source payload without authenticating it against its shipped release manifest**, then regenerate `KERNEL_MANIFEST.json` and `framework.lock.kernel_manifest_hash` from the installed bytes — so `kernel_trust` (V-H2) attests only internal self-consistency, not source authenticity. A source with `SECURITY_POLICY.never_index_classes` stripped of `restricted` (its `manifest.json`/`KERNEL_MANIFEST.json` left stale) installs through a properly answered gate; afterward `kernel trust` → `verified:true`, doctor clean, and a restricted **material** record is indexed and retrievable | `evidence/V-H3-update-source-not-authenticated.md`: `gov release verify` on the source → `modified:["policies/SECURITY_POLICY.yaml"]`, but `update --check` shows no integrity signal; post-install `never_index_classes=['secret']`, `kernel trust verified:true`, `lock.release_hash 47d080e4… ≠ published 962f9848…`; restricted `D-SECRET` retrievable vs excluded `sensitivity:restricted` on an intact-kernel control; `gov init` from the tampered `kernel/` also → `verified:true`. Migration-chain Step 8 independently reached the same result | A authority/policy engine; J sensitive-path handling / security boundaries; the entire V-H2 trust model (INV-006/INV-007); `update.rs`, `kernel.rs::install_kernel`, `init.rs`, `lock.rs` | anyone controlling the update/install source (compromised mirror, MITM without TLS, malicious shared release dir, insider) removes a constitutional floor and the OS blesses the result as "verified"; the security guarantee V-H2 advertises is void for any kernel that arrived via update/init from an unverified source | In `update::check`/`apply_update` **and** `init::init`, verify the source `kernel/` against its shipped release `manifest.json` `file_hashes` and `release_hash` (the `release::verify` logic already exists) **before** staging; refuse (or raise a gate) on any mismatch; record the source's **declared** `release_hash`/`release_commit` and refuse when the recomputed `release_hash` disagrees with the declared one; where a trusted release registry or signature is available, compare against it. Do not derive "verified" from a manifest the OS just generated from unauthenticated bytes | a new WV-07 scenario: a tampered-source `update`/`init` is refused (or gated and, if forced, reported `kernel trust verified:false` / `KERNEL_SOURCE_UNVERIFIED`), and the restricted record stays excluded |

### MEDIUM / LOW

Carried forward from the 4.1.4 report and re-confirmed as unchanged and non-blocking: vector/graph stores fixed to
SQLite with no trait (V-M2); no per-record git lineage, regex-only code intelligence, protocol-order migration batching
(V-M3); schema-invalid sensitivity rule does not fail closed (V-L1); `update` refusals return `ok:true, applied:false`
(V-L2); absolute-path snapshot/`source` fields (V-L3/V-L4); caller-declared acting role as a documented adapter boundary
(V-L5); `.gitignore`d paths invisible to the mutation check (V-L6); no token-level metrics (V-L7).

## 12. Builder repair delta (ordered)

1. **V-H3 — authenticate the update/install source before adopting it.**
   (a) In `update::check` and `apply_update`, run the `release::verify` logic on the resolved source (`kernel/` vs its
   shipped `manifest.json` `file_hashes`, and `payload_hash`/`release_hash`) before `install_kernel`; refuse with a typed
   `KERNEL_SOURCE_UNVERIFIED` (or raise a gate) on any mismatch. (b) Record the source's **declared** `release_hash` and
   `release_commit`, and refuse when the recomputed `release_hash` (what `install_kernel` produces) disagrees with the
   declared value — so a stale-manifest tamper cannot be laundered into a "verified" lock. (c) Apply the same check to
   `init::init` for a built-release source (a raw `framework/` source has no manifest and is the developer path — treat
   it explicitly, e.g. an `--unverified-source` acknowledgement rather than silent acceptance). (d) Surface the source
   verdict in `update --check` output and the ledger. Acceptance: a tampered-source `update`/`init` is refused or
   reported `verified:false`, and the restricted record stays excluded (new WV-07).
2. **Evidence hygiene** (carried from the 4.1.4 delta, still applicable): record NV-09/NV-19 (frozen to the 4.1.3
   payload) and VV-05/VV-07 (pinned to the 4.1.4 identity) as identity/history failures in the 4.1.5 evidence with a
   pointer to §4/§5, so the harness totals are not read as open defects.
3. Because the fix set touches the update/install path (and possibly a typed error code + a `manifest.json` field), ship
   the repaired candidate as a new immutable PATCH release **4.1.6** with migration `M-4.1.5-4.1.6` on
   `release/4.1.6-rc1` tagged `v4.1.6-rc1`; 4.1.5 stays immutable and REJECTED. Re-run the builder suite, **all three**
   previous harnesses unchanged **and** `heldout-wv/harness_wv.py`, clippy and rustfmt; regenerate evidence; leave
   certification pending.

## 13. Root-cause escalation note (directive §9)

V-H3 is, by itself, a bounded and repairable implementation gap (§12). But it is the **fourth consecutive iteration** in
which a defect of the same family — *an authenticity/authorisation fact derived from an unauthenticated lower-trust
artifact* — has surfaced (4.1.3: ungoverned plugin descriptors; 4.1.4: V-H1 descriptor self-authorisation + V-H2
unverified installed kernel; 4.1.5: V-H3 unverified install/update source). D-0007 adopted at 4.1.5 states the correct
general rule ("a lower-trust input may never manufacture a higher-trust fact") and closed the **use-time** and
**post-install** instances well (WV-01/02/03). It did **not** close the **install/update-time ingress**, because D-0007's
own T1 definition ("an installed kernel whose payload matches `KERNEL_MANIFEST.json` **and** whose manifest matches
`framework.lock.kernel_manifest_hash`") is **circular at install time**: all three anchors are written by the OS from the
source it is installing. The only genuinely independent root of trust — the kernel payload embedded in the signed
binary, or an out-of-band signature / release registry — is consulted at *use* time (as the fail-closed baseline) but
**not** to authenticate an incoming source.

**Recommendation for the owner (not performed here):** treat V-H3's repair as the ordinary-iteration fix, but recognise
the recurrence as a signal that the trust model needs a *single, artifact-independent root of trust at every ingress*
rather than another point patch. Concretely: (i) authenticate every kernel ingress (`init`, `update`, `kernel
reinstall`) against the embedded baseline's known release identity and/or a signature chain, so "verified" always means
"matches a trusted external anchor," never "internally self-consistent"; (ii) add a conformance test family that
enumerates **every** path that writes `framework.lock`/`KERNEL_MANIFEST.json` and asserts each authenticates its source;
(iii) consider a release-signing key as the durable fix for the acknowledged "no signature chain" residual. This is the
architectural hardening the pattern points to; a further ordinary iteration that only patches the update call site risks
a fifth instance elsewhere.

## 14. Certification block for the release owner

This session did not edit `release/releases/4.1.5/manifest.{yaml,json}` or `release/CERTIFICATION_STATUS.md` (same
convention as 4.1.3/4.1.4). `VERDICT.md` carries the exact block to transcribe verbatim; the kernel payload and
`file_hashes` must stay untouched, and `gov release verify release/releases/4.1.5` remains ok because only `kernel/` is
hashed.

## 15. Verdict

**OS_RELEASE_CANDIDATE_REJECTED** for commit `da9c8518d3fddba6f37bafb4d046ca313335ec1f` (repair candidate 4.1.5).

Rejection trigger met (directive §10): an independently authored held-out test exposed an unresolved **HIGH**
trust-boundary defect (V-H3), and the security boundary is in consequence materially incomplete at the install/update
ingress. No critical architectural pillar is absent; memory is a genuine multi-layer fabric; authoritative truth does not
depend on opaque derived indexes; component choices are recorded, pinned and replaceable; derived indexes rebuild
deterministically; the OS is not tied to one governed-project language; and the deterministic core does not contradict
the Rust-first architecture. V-H1, V-H2 and V-M1 are genuinely repaired and robust under fresh attack, the ETXTBSY race
is fixed, no confirmed repair regressed, and the repair delta in §12 is bounded — but the recurrence documented in §13
should be weighed by the owner before the next iteration.
