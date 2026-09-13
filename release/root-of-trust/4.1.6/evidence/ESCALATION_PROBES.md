# Escalation probes E1–E5 (root-of-trust architecture review, 2026-09-13)

Purpose: establish whether V-H3 is an isolated call-site defect or an instance of a wider trust-root failure, and whether
the bounded repair in `release/verification/4.1.5/INDEPENDENT_REVERIFICATION_REPORT.md` §12 would close it.

## Environment

- Repository HEAD `c8a138f` (verifier artefacts only on top of candidate `da9c851`; runtime/CLI/kernel identical).
- `cargo build --release` run immediately before the probes (the existing binary predated the candidate commit
  timestamp; the rebuild compiled HEAD). `gov version` → 4.1.5.
- All work in fresh scratch directories; `GOV_CANONICAL_ROOT`, `GOV_ROLE`, `GOV_SESSION`, `GOV_KERNEL_SOURCE` unset;
  `GOV_KERNEL_CACHE` pointed at the scratch directory. No repository file was written by the probes.
- Files: `probe.sh` (driver), `regen.py` (tamper + regenerate manifests exactly as `util::hash_tree`, `util::hash_value`
  and `kernel::manifest_hash` compute them), `probe-output.txt` (verbatim output; absolute scratch paths retained).
- Tamper used throughout: remove `restricted` from `SECURITY_POLICY.never_index_classes` — the same constitutional floor
  whose removal the 4.1.5 verifier showed makes a restricted material record indexed and retrievable.

## Results

| Probe | Steps | Observed | Meaning |
|---|---|---|---|
| E1a (V-H3 as reported) | copy `release/releases/4.1.5`; tamper; leave manifests stale; `gov release verify` | `result.ok: false`, `modified: [policies/SECURITY_POLICY.yaml]` | stale-manifest tampering is detectable |
| **E1b** | same tamper; regenerate `kernel/KERNEL_MANIFEST.json` and `manifest.json` (`file_hashes`, `release_hash`) | `result.ok: true`, `modified: []`, `release_hash_matches_kernel: true`; regenerated `release_hash aa8fb66a…` | report §12(a) and §12(b) are circular; the source supplies the reference |
| **E2** | E1b source additionally sets `manifest.json certification.status: CERTIFIED`; consumer created by the 4.1.5 binary from `release/releases/4.1.4`; `update --check --source`; `update --apply --source` **without `--approve`** | check: `certification: CERTIFIED`, `human_gate_required: false`, recommendation "safe: `gov update --apply`"; apply: `applied: true`; ledger `framework-updates.jsonl` entry `result: committed`; no gate record; `kernel trust verified: true`; lock `release_hash aa8fb66a…` (≠ published `962f9848…`), `release_commit 25dac6e…` copied from the forged manifest; installed `never_index_classes: [secret]` | an authorisation decision (gate required) is taken from the source; V-H3's gated precondition is not even needed |
| **E3a** | `gov init` (no `--source`) materialises the embedded kernel into `$GOV_KERNEL_CACHE/kernels/4.1.5-feea05613ddf`; tamper that cache; `gov init` a new consumer with no `--source` | `source: embedded:agentic-engineering-os@4.1.5`; `kernel trust verified: true`; installed `never_index_classes: [secret]` | the "embedded" anchor is a mutable directory reused on a marker; the provenance label is wrong |
| **E3b** | tamper an installed kernel (append a comment to `POLICY_PRECEDENCE.yaml`) in a consumer whose baseline cache is poisoned | `verified: false`, `substituted_embedded_baseline: true`, source "embedded baseline 4.1.5 substituted…"; `gov policy effective SECURITY_POLICY` → `never_index_classes: ['secret']` | the V-H2 fail-closed baseline is read from the poisoned cache |
| **E4** | consumer initialised from `release/releases/4.1.5`; tamper installed `SECURITY_POLICY`; `verified` → false; regenerate installed `KERNEL_MANIFEST.json` and lock `kernel_manifest_hash`/`release_hash` | `verified: true`, `substituted_embedded_baseline: false`; doctor D003 ok, D004 ok, D029 ok | a coherent replacement (the shape of a Git pull) is indistinguishable from a genuine install |
| **E5** | E2 consumer: tamper `.governance-runtime/update/4.1.5/kernel`, regenerate the snapshot manifest and snapshot lock; `gov update --rollback --reason probe` | `kernel_ok: true`, `rolled_back_to: 4.1.4`; `kernel trust verified: true`; installed `never_index_classes: [secret]`; ledger `event: rollback` | rollback is an unauthenticated privileged ingress |

## Conclusion

Five independent ingress routes (source directory, source self-certification, embedded cache, Git-shaped replacement,
rollback snapshot) all manufacture a `verified: true` kernel with a removed constitutional floor. The common cause is that
every reference value is produced by, or co-located with, the material it is supposed to authenticate. See
`../00-OVERVIEW.md` §4.
