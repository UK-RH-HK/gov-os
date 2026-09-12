# V-H3 evidence — `gov update` / `gov init` do not authenticate the update SOURCE payload

Reproduced independently (fresh clones; 4.1.4 binary to create the consumer, 4.1.5 candidate binary to update).

## Setup
- Consumer created by the 4.1.4 binary from the greenfield fixture (`framework.lock.version = 4.1.4`).
- Tampered copy of the immutable `release/releases/4.1.5` payload: removed `restricted` from
  `kernel/policies/SECURITY_POLICY.yaml` `never_index_classes`. The copy's own `manifest.json` and
  `kernel/KERNEL_MANIFEST.json` were left STALE (they still describe the original bytes).

## Detection that EXISTS but is not invoked by the update flow
- `gov release verify <tampered-source>` → `ok:false, modified:["policies/SECURITY_POLICY.yaml"]`  (CATCHES it)
- `gov update --check --source <tampered-source>` → no integrity signal; `release_hash: null`, `source_release_hash: null`

## The bypass
- `gov update --apply --approve` (properly gated: gate raised, presented, decided A) → `applied: true`, installs 4.1.5.
- Installed `never_index_classes = ['secret']`  (the `restricted` floor is gone).
- `gov kernel trust` → `verified: true` ("installed kernel 4.1.5 verified against KERNEL_MANIFEST.json and framework.lock").
- doctor D003/D004/D029 → all ok.
- `framework.lock.release_hash = 47d080e48cb663f393349995ec530460f4a9d5ea242398fdaf0a1c644de2d1d6`
  vs published 4.1.5 `release_hash = 962f98480fc311c5857e7eef6f951f5713c3e62e4b1e9703c8c5d1f5c74a314b`  → DOES NOT MATCH
  (the anchor is recomputed from the tampered bytes; release_commit is copied from the source manifest and still matches).

## Confirmed harm (constitutional security floor removed)
Restricted MATERIAL record `spec/decisions/D-SECRET.yaml` (classified `restricted` via DATA_SENSITIVITY):
- TAMPERED-but-"verified" kernel: `rebuild-memory` excluded:[] → `memory query PROPRIETARYMARKER` returns
  `spec/decisions/D-SECRET.yaml` (RETRIEVABLE).
- INTACT kernel (control): excluded `[{path: spec/decisions/D-SECRET.yaml, reason: sensitivity:restricted}]` →
  not retrievable.

## `gov init` shares the gap
`gov init --source <tampered-4.1.5/kernel>` → init ok, `kernel trust verified: true`, installed
`never_index_classes = ['secret']`.

## Root cause (source)
`update::apply_update` → `install_kernel(src)` (`kernel.rs`) stages the source bytes and REGENERATES
`KERNEL_MANIFEST.json` via `build_manifest`; `lock::write_lock` then sets `kernel_manifest_hash` and `release_hash`
from that regenerated manifest. Neither `update::check`/`apply_update` nor `init::init` verifies the source `kernel/`
against the source's shipped release `manifest.json` `file_hashes`/`release_hash` (the `release::verify` logic), and
neither compares the source's DECLARED release_hash to the recomputed one. `kernel_trust` (V-H2) therefore attests
only INTERNAL self-consistency of the installed files, not the AUTHENTICITY of the source they came from.
