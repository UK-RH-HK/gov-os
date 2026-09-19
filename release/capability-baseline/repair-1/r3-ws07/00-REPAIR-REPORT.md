# WS-7 repair report: repair iteration 1, round 3 (P2-AR-0038)

| | |
|---|---|
| Run | P2-AR-0038, role `capability-repair`, model Claude Opus 5 (1M context), `claude-opus-5[1m]` |
| Handoffs | P2-HO-0037 (WS-7 round 3), P2-HO-0031 (round-3 common, incl. the availability rule), P2-HO-0020, P2-HO-0010 |
| Branch / base | `phase2/repair-1-r3-ws07` from `53897c1a44157e5af81b176017bc7ded6a63b9cd` (integrated round-2 tree) |
| Work commits | `222da4e` (registry move, model/runtime artefacts, T2-audit rows, pin cache, tests), `18127a5` (legacy-location anomaly disclosed at `low`), `0393bca` (bound plugin files' digests never leave the process — §4.3), then the commit adding this report and `evidence/` |
| Product identity | at `0393bca`: `product_code_digest` `82de1a979e56017ce8218d92317a96223efe5a43bd3f35e8169681ebf0f2acc4`; `governed_state_digest 8f191e39…948f` (unchanged from base). Base `797da37c…1fe1` |
| Items | BC-P2-31 plugin-registry move (WS-6 IP-R2-9) `REPAIRED_CLAIMED` · IP-R2-13 model/runtime artefacts `REPAIRED_CLAIMED` · WS-2 R3-11 T2-audit rows `REPAIRED_CLAIMED` (API; WS-3 wires `t2::audit`) · pin re-hash cost `REPAIRED_CLAIMED` · IP-W7-1 `CONFIRMED` (no change needed) |
| Verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION` — every routed item claimed; no owner decision needed |

**Status of these claims.** They come from the builder, and the evidence is regression evidence only (Contract v3 O3).
Nothing here says a class is accepted, verified or closed; that belongs to the independent verifiers.

---

## 0. Evidence index and regression

| What | Where | Result |
|---|---|---|
| `cargo test --lib` | `evidence/regression/cargo-test-lib.0393bca.out` | **218 / 0** (207 at base + 5 `pincache`, 4 `registry`, 2 `binding`) |
| `cargo test --test certification` (includes `section6.rs`) | `evidence/regression/cargo-test-certification.0393bca.out` | **140 / 0** (136 at base + 4 new `ws07`; `section6::*` 9/9) |
| rustfmt `--check` (edition 2021) on every touched Rust file; build warnings | — | 0 hunks (all were clean at base); 0 warnings |
| R1 held-out suites, all four rounds, **unedited**, private scratch paths, before (export of the base) and after (this worktree) | `evidence/r1-heldout/r1-heldout-base-53897c1.out`, `…-final-0393bca.out`, runner `run-r1-heldout.sh` | identical before and after: AR-0027 26/3, AR-0029 26/2 (`ho_f` does not compile, as recorded), AR-0031 27/7, AR-0033 30/1 (`hv_a::a1` size pin only); census 118/1991 → 119/2025; 0 violations in every §6 activity (§6) |
| WS-7 round-3 named checks (legitimate paths; base is the negative control) | `evidence/ws07_r3_named_checks.py`; `evidence/probes/ws07-r3-named-checks.{base-53897c1,final-0393bca}.out` | base **0 of 11** discriminating checks pass (the negative control); final **11 of 11**; every control holds on final |
| Audit-of-record probes, unedited, direct and through the round-2 integration's derived owner-channel adapter (shim) | `evidence/run-probes.sh`; `evidence/probes/{base-53897c1,final-0393bca}/`; pairing `evidence/COMPARE-probes.out` (`compare_probes.py`) | no round-2 WS-7 line regressed, in either mode (the 4 FAIL lines are direct-mode F3 (b) lines that need an owner answer and fail identically on both trees, as in round 2); LEAD-X4 (shim) 4/4 on both; D6 and AC16-X2 stop at their task-claim setup on both trees (§1) |
| gamma-r F4 through a labelled derived copy aiming the registry forgery at the new location | `evidence/derived/F4-plugins.registry-path.P2-AR-0038.sh`, runner `derived/run-derived-f4.sh`; `evidence/probes/final-0393bca/derived.gamma-r.F4-plugins.registry-path.shim.out` | every F4 line PASS on final; the forged entry at the new location is refused `PLUGIN_REGISTRATION_UNBOUND` and reported by `plugin_governance` |
| Round-2 WS-7 named checks (the round-2 integration's derived copy, unedited), on the final binary | `evidence/probes/r2-ws07-named-checks.derived.final-0393bca.out` | **26 / 26** (the round-2 integration recorded 26/26) |
| Pin-cache timing (debug `gov` as an OS capability-server plugin), base vs final | `evidence/timing_pin_cache.py`; `evidence/timing/pin-cache-timing.{base-53897c1,final-0393bca}.out`; `timing/benchmark-test.*` | per `gov` process with the plugin declared: base 3.4–6.8 s and 193 MB RSS on every call; final 0.12–0.77 s and 27 MB after the first call (§4.5) |
| Integration point IP-W7R3-1 measured (registration inside a claimed task, then close) | `evidence/ip_task_close_registration.py`; `evidence/integration-points/ip-task-close-registration.{base-53897c1,final-0393bca}.out` | final: close refused `MUTATION_SCOPE_VIOLATION` for `governance/registry/plugin-registry.json`; base: that stage passes (the close stops later, `GOVERNANCE_SUITE_MISSING`, unrelated) |

Binaries measured: base release `gov` sha256 `5ff6ce9c…6b82` (release build of the base export — the same digest the
round-2 integration recorded for `7491c5c`), final release `gov` `47a0ab59…22e3` (release build of `0393bca`). Every output records the binary it drove.

---

## 1. BC-P2-31 — the plugin registry moves out of the regenerable views (WS-6 IP-R2-9)

**Requirement** (repair-delta §1 BC-P2-31; Contract v3 B1:188 "Generated/runtime state is distinguished from
authoritative tracked state", B3:202 "Deleting derived state cannot delete project truth", D6:352; D-0007 T2 "the plugin
registry" is OS-written state; A0-D6-02): OS plugin registration survives deletion of every path the product classifies
derived or generated. WS-6 (round 2) declared the store and its location (`paths::OS_STORES` `plugin-registry`,
`PLUGIN_REGISTRY_PATH = governance/registry/plugin-registry.json`, class `authoritative`, tracked) and routed the writer
move here: resolve the location with `paths::store_path`, move an existing registry with `relocate_legacy`. The handoff
adds: the move must not let a relocated or cloned registry become honoured without its seal.

**Changes** (`runtime/src/capabilities/registry.rs`; messages in `governance.rs`):

- `registry::path(p)` is `paths::store_path(root, "plugin-registry")`; `REGISTRY_PATH` is `paths::PLUGIN_REGISTRY_PATH`.
  Every registration and unregistration writes there.
- **Reading** (`source`, `load`): the registry is read from where it belongs. Only while *no* registry exists there is
  a registry at the legacy location (`LEGACY_REGISTRY_PATH`, `governance/generated/plugin-registry.json`, where an
  earlier release wrote it) read — entry by entry under exactly the same T2 seal rule. Reading never moves or writes
  anything, so read-only commands stay read-only (G0) and a project upgraded from 4.1.5 keeps its registrations until
  its next registry write. `paths::misplaced_os_state` keeps reporting a registry still at the legacy location.
- **Moving** (`relocate`, called first by `record` and `remove`, the only registry writers; also the API for the
  upgrade path, IP-W7R3-5): `paths::relocate_legacy` moves the file **as it is** — the bytes, every entry's seal and the
  document seal. Nothing is re-sealed, so an entry that was not honoured before the move (hand-written, edited,
  legacy-unsealed, foreign) is not honoured after it. When a registry already exists where it belongs and the legacy
  file differs (`STATE_LOCATION_CONFLICT`), the location is authoritative: the legacy file is left in place, never read,
  never overwritten or deleted by the OS, and disclosed (next bullet); an identical copy is removed.
- **Cloned or copied registries.** The registry was already tracked (`governance/generated/` is not git-ignored), so a
  clone carries it, now at the new location. Honouring stays per entry and per seal: a clone on a machine that does not
  hold this machine's binding key sees `FOREIGN`/`KEY_UNAVAILABLE` entries, never honoured; a registry copied into the
  location by hand is honoured only for entries whose seal verifies here. (P2-ADJ-0002, WS-3/WS-8's round-3 item, will
  let *provisioned* machines of the same owner verify each other's T2 seals; the registry uses `t2::seal_value` /
  `t2::verify_value` and inherits that without change. The ws07 clone checks use an unprovisioned clone machine, which
  the adjudication keeps refused.)
- **The document seal is written only over OS-written content** (`seal_document`): only when every entry in the file
  verifies. Before, any registry write re-sealed the whole document, including an entry a worker had planted, so
  `t2::classify_path` would have called the file an OS write. The entries themselves were never honoured; now the file is
  not blessed either. Unregistering the planted entry through `gov` seals the document again.
- **A differing file left at the legacy location** (`location_findings` → `governance::findings` → doctor D028 and the
  `plugin_governance` family): `PLUGIN_REGISTRY_LOCATION_CONFLICT`, severity **low**. It is never read, so no
  authorisation relies on it; under the availability rule (P2-HO-0031) a finding that governs no reliance must not
  degrade the suite and refuse unrelated work (`18127a5`; the first cut used `medium`). D028 (a warning-mode check)
  still reports it.
- Messages name the file the registry is actually read from (`registry::shown_path`); `registry::report` adds
  `read_from`, `location` and `location_findings` (for WS-3's optional IP-W7-4 view).
- `TOOL_POLICY.plugins.registry_path` (informational; immutable under POLICY_PRECEDENCE) now states the new location;
  the plugin-registry schema description and `capabilities/PROTOCOL.md` say where it lives and why.

**Product check / tier.** Structural at every registry write (G2 of the writing operation); detection by doctor D028 and
the `plugin_governance` family (G4-G6) for the location anomaly and for every unbound entry (existing, BC-P2-09).

**Tests.** Certification `ws07::the_plugin_registry_survives_deleting_the_generated_views_and_moves_only_as_written`:
(1) a governed registration is written at the new location, sealed, not reported misplaced; (2) deleting the whole
`governance/generated/` keeps it — the plugin still runs; (3) a registry moved back to the legacy location is honoured
as it stands, and `plugins list`, `plugins registry`, doctor, the `plugin_governance` audit and an execution never move
it; a worker's unsealed entry added there is refused `PLUGIN_REGISTRATION_UNBOUND`; (4) the next registration moves
the file: the sealed entry still runs, the planted entry is still refused, and the document carries no seal until
`plugins unregister` removes the planted entry; (5) after the move, a registry planted at the legacy location that
would unregister everything is never read (the plugin still runs), D028 reports it, and a registry write neither reads,
overwrites nor deletes it; (6) a clone carries the registry at the new location and its unprovisioned machine refuses
this machine's seals. Lib `registry::tests` (4): the location is the kernel's store declaration; legacy read only while
none exists at the location; relocation moves bytes unchanged, never overwrites, removes an identical copy; T2-audit
rows (§3).

**Probes** (`COMPARE-probes.out`, named checks):

| Line | Base | Final |
|---|---|---|
| W7R3-31.a the OS writes the registry outside the regenerable views | FAIL (`governance/generated/`) | **PASS** (`governance/registry/`) |
| W7R3-31.b deleting `governance/generated/` keeps the registration (A0-D6-02) | FAIL (`PLUGIN_NOT_APPROVED`, registration lost) | **PASS** (the plugin runs) |
| W7R3-31.d the next write moves the legacy registry unchanged; the planted entry stays refused; no document seal over it | FAIL | **PASS** (moved; p1 runs; n1 `PLUGIN_REGISTRATION_UNBOUND` before and after; no document seal) |
| W7R3-31.e after the move a registry planted at the legacy location is ignored and reported | FAIL (the planted file is read: the plugin is refused) | **PASS** (the plugin runs; D028 reports the legacy file) |
| W7R3-31.c / .f controls: legacy registry honoured and never moved by reads; the planted entry never ran | not reachable on base (the registration was lost at 31.b) | hold |
| beta-r `D6-rebuild-guarantee` (direct and shim) | stops at its task-claim setup (`TASK_NOT_RUNNABLE`, WS-5's DAG rules) | same stop — not discriminating on this tree |
| synthesis `AC16-X2` `X2-B1B3-*` (direct and shim) | not reached (task-claim setup) | not reached. Its check reads the overlay template's rules for the three literal legacy paths — IP-R2-11 (template, WS-6/WS-9), not the writer |
| gamma-r F4 `F4.b2.x` unedited (shim) | the forged entry is read and refused `PLUGIN_REGISTRATION_UNBOUND` | the probe's forger opens `governance/generated/plugin-registry.json`, finds nothing, and writes no entry: the line reads PASS for a reason the probe did not intend |
| gamma-r F4 `F4.b2.x` through the labelled derived copy (only the registry path changed) (shim) | — | **refused** `PLUGIN_REGISTRATION_UNBOUND` for `tooling-engineer` and `orchestrator`; `plugin_governance` reports the entry |

**Limits.** (a) Until a registry write (or IP-W7R3-5's migration step) moves it, an upgraded project's registry stays
at the legacy location, where deleting the whole `governance/generated/` directory would still lose it (reported by
`misplaced_os_state`). (b) Concurrent registry writers still race read-modify-write (as before this change). (c) The
T2 rollback limit stated in round 2 stands: a sealed entry restored from history runs its approved bytes until its gate
is revoked. (d) The task-close classification of the new location is WS-5's file — IP-W7R3-1 is required at
integration (measured, §8).

---

## 2. IP-R2-13 — model and runtime artefacts a descriptor declares

**Requirement** (WS-6 round-2 IP-R2-13 for BC-P2-30, Contract v3 D4 "embedding model / embedding runtime / reranker
independently identifiable", D5 "selected revisions are pinned … fail closed on mismatch"; with BC-P2-40, Contract v3
F4:428-429): an embed/rerank plugin must be able to declare model and runtime artefacts that live outside its own
directory, so BC-P2-30's component identity can bind them; the kernel schema rejected any such field
(`additionalProperties: false`).

**Changes.**
- `plugin-descriptor.schema.json` 1.4.0: `model: {id?, revision?, artefacts: [path…]}` and `runtime: {id?, artefacts:
  [path…]}` (each `artefacts` non-empty; no other keys).
- `PluginDescriptor::declared_paths(field)` (the paths as written) and `binding::declared_paths(desc, root)` → one
  `DeclaredPath {role: declared|model|runtime, declared, abs, in_repository}` per path: `{project_root}`/`{plugin_dir}`
  substituted, a relative path taken from the project root (as `implementation:` already was), `in_repository` saying
  whether it is repository content (portable: the index manifest's hashed core) or machine-local (runtime meta) — the
  split IP-R2-13 asked for.
- **For an executable plugin the declared artefacts are bound by the registration** (`binding::resolve`, roles `model`
  / `runtime`, directories as whole trees): their bytes are part of the implementation identity and of the
  registration subject the owner approves; a changed model or runtime byte fails closed (`PLUGIN_PIN_MISMATCH`, the file
  named, and D028 reports it); a declared artefact that does not exist is refused before any gate
  (`PLUGIN_IMPLEMENTATION_UNRESOLVED`). A model file can carry executable content (pickled weights) and a runtime is
  code, so binding them is F4:428's reading, not an optional extra.
- The registration gate package names the declared model and runtime artefacts beside the full bound-file list.

**Tests.** Certification `ws07::declared_model_and_runtime_artefacts_are_part_of_what_the_owner_approves` (schema admits
the fields; the gate names the artefacts; roles bound; changed model byte and changed runtime byte refused; D028 names
the file; missing artefact refused before any gate); lib
`binding::tests::declared_model_and_runtime_artefacts_are_bound_with_their_roles`.

**Probes.** Named checks W7R3-13.a–e: base FAIL ×5 (the schema rejects the fields: `SCHEMA_INVALID` /
`PLUGIN_DESCRIPTOR_INVALID`) → final **PASS ×5**.

**Consequence and limit.** A model upgrade of an executable plugin needs a new registration approval (owner gate) as
well as the governed profile change BC-P2-30 requires — the same fail-closed stance round 2 took for an interpreter
upgrade. A model tree larger than 20 000 files is refused, not truncated. The retrieval-profile identity is WS-6's code:
IP-W7R3-6 routes the consumption.

---

## 3. WS-2 R3-11 — registry entries in the T2 audit

**Requirement** (WS-2 round-2 R3-11): with the registry sealed (round 2), include its entries in `t2::audit` so the
`os_binding_integrity` family, doctor D033 and the `t2_bindings` currency class cover it. `t2.rs` is WS-3's file; WS-7
exposes the rows.

**Change.** `capabilities::registry::t2_audit(p) -> Vec<Value>` in `t2::audit`'s row shape (`id`, `type`, `path`,
`t2`, plus `plugin_id`): one row per entry that does not verify (`id: plugin-registry:<plugin_id>`, `type:
plugin-registration`), and one `plugin-registry` document row when the document carries a seal that no longer verifies
while every entry does (a top-level edit). A registry read from the legacy location is audited there. Nothing is listed
for an absent registry or for verified entries.

**Tests.** Lib `registry::tests::t2_audit_rows_name_every_entry_the_os_did_not_write` (an unsealed entry → `UNSEALED`,
an entry recorded under another plugin's id → `BROKEN`; no machine key needed). The call itself: IP-W7R3-2.

---

## 4. Plugin authorisation without re-hashing unchanged files — and without weakening the pin

### 4.1 The problem, measured

`governance::authorize` recomputes the implementation (every bound file's sha256) at every execution and every
`plugin_set` classification. With the ~170 MB debug `gov` as an OS capability-server plugin, each `gov` process hashed
it (unoptimised sha2 in debug builds): at base, `gov plugins list` takes 2.46 s against 0.09 s with plugins disabled,
and `memory freshness` 6.2 s against 0.38 s (WS-6's profile identity hashes the same binary again). Peak RSS 193 MB
(the file was read whole).

### 4.2 Design (`runtime/src/capabilities/pincache.rs`)

A digest is reused only under the file's full **stat key** — device, inode, size, mtime, **ctime**, mode, owner — and
only when reuse cannot return the digest of other bytes:
- **ctime** is set by the kernel on every change of a file's bytes (`write`, `truncate`, the first store through a new
  shared mapping) and cannot be set by an unprivileged process (resetting mtime with `touch -d` moves ctime to now);
  replacing a file changes the inode.
- **Quiescence** (the round-2 defect was a same-size rewrite inside one timestamp tick): a digest is kept only when the
  file last changed at least 3 s before its bytes are read, so any later change is stamped differently.
- **No writer**: a digest is kept only when the OS proves no process holds the file open for writing at that moment —
  a Linux read lease cannot be granted then (`fcntl(F_SETLEASE, F_RDLCK)` fails `EAGAIN`; released at once, a break
  routed to `SIGURG`, ignored by default) — or the file is root-owned and writable by nobody else. This closes the
  already-dirty shared-mapping case, where bytes change without a new timestamp until write-back.
- **Stable read**: the stat is repeated after hashing; a file that changed while being read is never kept.
- **Kernel-maintained local filesystem** (ext2/3/4, XFS, Btrfs, F2FS, ZFS, tmpfs, ramfs, overlayfs by `statfs` magic):
  on NFS, SMB, FUSE (sshfs) or 9p/drvfs the times come from elsewhere (a remote `touch -d` can leave ctime untouched), so
  nothing there is ever kept.
- Hashing now streams (1 MiB buffer): peak RSS no longer grows with the program's size.

### 4.3 Where digests are kept — and the correction made in this run (`0393bca`)

The first cut (`222da4e`) persisted every kept digest in the machine's protected state. Reviewing it against the threat
model, that weakened the pin: the machine state root is writable by a process running with the operator's own
account, and a digest planted there for a tampered bound file would make the OS report the owner-approved
implementation for changed bytes — turning the owner-signed approval of exact bytes (which holds even against an
operator-privileged process: the answer is signed by a key the machine does not hold) into a detection-grade check.
The design is therefore:
- **A bound plugin file's digest is reused only from the memory of the `gov` process that computed it**
  (`pincache::sha256_of`). No file, store or earlier process ever supplies it.
- **Only the digest labelling the running `gov` executable is kept across processes** (`running_binary_sha256`,
  `<state root>/plugin-pin-cache/cache.json`, at most 64 entries), used only where the program a plugin runs *is* the
  running file (same device and inode). What executes there is the running image whatever digest labels it (an
  executable cannot be open for writing while it runs), so a stored label can change how the program is named, never
  which bytes run.
- The **byte-identical-copy test** — a *different* file claiming to be this binary, which decides the `OS_PROVIDED`
  class — compares with the running image as this process reads it (`fresh_sha256`), never with a stored digest.
- `binding::content_sha256(p)` is the shared entry point (the running binary by inode, everything else through the
  in-process memo) for other components identifying the same files (IP-W7R3-6).

### 4.4 A strengthening found on the way (BC-P2-40)

A symlink inside a bound tree was bound by its **target text** only, so the bytes it points at could change unseen, and
a symlinked directory inside a package was not entered. Now a symlink binds its target text **and** the bytes it
resolves to, and a symlinked directory is followed (each directory entered once; cycles end there). Base executed
changed bytes behind a bound symlink (named check W7R3-PC.d: base `code: null`, the plugin ran). Existing registrations
whose bound trees contain symlinks re-register (fail closed).

### 4.5 Evidence

| | Base | Final |
|---|---|---|
| `gov plugins list` / `plugins health`, debug `gov` as an OS capability-server plugin, 4 runs each (`timing/pin-cache-timing.*`) | 3.4–6.8 s on every call, peak RSS 193 MB (back-to-back run 2; run 1: 2.7–11.7 s) | first call 12.0 s (heavily loaded; it hashes the binary and keeps its label), then 0.12–0.77 s, peak RSS 27 MB (run 1: 6.3 s, then 0.25–0.46 s with one 3.7 s outlier) |
| certification `repair::benchmark_records_evidence_and_selection_pins_through_decision`, base and final run alternately under the same (heavily loaded) machine (`timing/benchmark-test.interleaved.out`) | 42.8, 67.4, 44.7, 45.1 s | 119.1, 28.8, 25.8, 61.5 s — **inconclusive** under this load (medians ≈ 45 s on both sides): the test's remaining large-binary hashing is WS-6's profile identity (IP-W7R3-6) |
| indicative only, at low load before any commit of this run (`timing/benchmark-test.base-53897c1-and-ws6-experiment.out`): base; the pre-commit state that became `222da4e`; that state with WS-6's profile hashing routed through `content_sha256` (reverted experiment; IP-W7R3-6) | 33.0 s | 22.2 s; 17.4 s |
| W7R3-PC.a running binary's label kept across processes; no bound plugin file's digest leaves the process | FAIL (no store) | **PASS** |
| W7R3-PC.d a change to the file a bound symlink points at is refused | **FAIL (changed bytes ran)** | **PASS** (`PLUGIN_PIN_MISMATCH`) |
| W7R3-PC.b/.c/.g/.f controls: no cache in the repository; same-size rewrite with mtime put back refused; **a forged machine-store entry naming the approved digest for the tampered file does not make it run**; only approved executions ran | PC.b/.c/.g hold (no store exists); **PC.f BROKEN**: 3 executions, the changed symlink target ran | all hold (2 approved executions only) |

**Tests.** Lib `pincache::tests` (5): quiescence boundaries; the store format round-trips; a file written just now is
hashed again on every call (the round-2 defect); a kept digest is never returned for changed bytes even with mtime put
back, and a file held open for writing is never kept (real lease probe); procfs is never cached. Lib
`binding::tests::symlinked_files_and_directories_inside_a_bound_tree_are_bound_by_content`. Certification
`ws07::a_cached_pin_never_approves_changed_bytes` (the running binary's label is kept; no plugin file digest is; a
same-size rewrite with mtime restored, a forged store entry, a changed symlink target and a renamed-over file are all
refused).

**Limits.** Bytes changed after authorisation and before the plugin process loads them remain outside what any
hash-then-execute design sees (unchanged). The in-process memo helps repeated classifications inside one `gov` process;
each new process reads a plugin's files once. Debug-build hashing itself stays slow: IP-W7R3-10 (dev-profile
optimisation of `sha2`, a workspace-manifest change outside WS-7) would remove most of the remaining cost for every
component.

---

## 5. IP-W7-1 — confirmed: sealed close reports are governed security reviews

**Requirement** (BC-P2-41; Contract v3 F3:416-423, F4:431; round-2 limit): a governed security review of the tool
identity and version, by another author, satisfies the security part of `licence_and_security_satisfied` without the
owner's gate. Round 2 routed the missing piece to WS-5: seal the close report.

**Finding.** WS-5 round 2 did it: `orchestration::tasks::close` writes the report with `session`/`role` of the closing
session and seals it (`t2::seal_record(&mut rec, "task close")`), and records `closed_by_report` on the task. The report
schema admits the `security_review` block. `tools::security_review_evidence` therefore accepts a security-class close
report written by another session and role, naming exactly the tool and version with `verdict: passed`. **No product
change was needed**; `tools.rs`'s module documentation now says so.

**Tests.** Certification `ws07::a_governed_security_review_by_another_role_lets_the_installation_proceed`: a
`security`-class task claimed and closed by `security-engineer` (another session) with a consumption receipt carrying the
review → the close report is sealed; `tools install` by `tooling-engineer` citing it installs with **no gate raised**;
the same review does not cover another version; the reviewing role's own install is refused as self-attested. Named
checks W7R3-41.a/.b hold on base and final alike (the property is already true on the integrated base).

---

## 6. R1 preservation

`srr/plugins.rs` (the `guard_acquisition` sink) and `tools::install` (the second acquisition primitive) are §6 effect
sites examined at R1. **`runtime/src/srr/` is not changed** (`git diff 53897c1 -- runtime/src/srr` is empty).
`tools.rs` changed only in its module documentation; `tools::install` and `governance::register` are byte-identical to
base (`register` still reaches `guard_acquisition` before any write; the relocation runs inside `registry::record`, after
it). No new function matches a §6 signature: the pin cache's store writer names no plugin or tool directory and no
floor or trust path, and no `resolve_state_root() else` fail-open pattern was introduced (`hv_c::c6`'s census).

| Suite (unedited, private scratch path) | Recorded baseline | Before: export of `53897c1` | After: this worktree at `0393bca` |
|---|---|---|---|
| AR-0027 | 26 / 3 (`b1`, `b2`, `d3`) | 26 / 3, same tests | **26 / 3**, same tests |
| AR-0029 | 26 / 2 (`b3`, `b6`); `ho_f` does not compile | 26 / 2, same; `ho_f` does not compile | **26 / 2**, same tests; `ho_f` does not compile |
| AR-0031 | 27 / 7 (`a1`, `a5`, `a8`, `b6`, `c2`, `c3`, `d2`) | 27 / 7, same tests | **27 / 7**, same tests |
| AR-0033 | 31 / 0 (30 / 1 on any larger tree) | 30 / 1: `hv_a::a1` only | **30 / 1**: `hv_a_derivation::a1` only |

- **Census** (AR-0033's walk): before **118 files / 1991 functions** (matches the round-2 integration), after
  **119 files / 2025 functions** (+1 file: `capabilities/pincache.rs`).
- **Unpinned copy** (`hv_a_derivation.a1-unpinned.P2-AR-0038.rs.txt`, only the two size assertions replaced by printed
  values) and AR-0033's own `derive.py` (ROOT line only), all three splitters: **0 violations in every §6 activity**,
  identical per-activity counts before and after — `human_gate_create` 47/42/1, `human_gate_approve` 1/1, 
  `release_certification` 1/1, `trust_policy_mutation` 8/1, `privileged_plugin_acquisition` 9/2, `floor_lower_or_reset`
  3/1, `present_below_floor_release_as_current` 1/1 (derived/writers/exempt).
- **Normalised failure messages** (the round-2 integration's `failure_messages.py`, unedited): 42 lines each, identical before and after, and identical to the round-2 integration's recorded run (`r1-heldout/failure-messages-base-vs-final.txt`).
- `tests/certification/section6.rs`: 9/9 at `0393bca`.
- The runs measure the intended tree: the header records the measured tree and commit, `product files differing: 0`
  (after) or an empty difference list against the commit (before, a `git archive` export), private symlinks
  `…/p2ar0038/r1-P2-AR-0038-private-<label>/wt/srr1-r1-verify{,-2,-3,-4}` to that tree, and 26 `identical` cmp lines
  for the copied suites.

---

## 7. Existing builder tests changed, and why

No assertion was weakened.

| Test | Change | Reason |
|---|---|---|
| `repair3::plugin_descriptors_can_never_authorise_themselves` (3 reads) | reads the registry at `governance/registry/plugin-registry.json` | BC-P2-31: the registry's writer moved (the forged-registry step that *writes* the legacy path is unchanged: with no registry at the location the legacy file is read, under the same seal rule, and the assertion holds) |
| `ws06::deleting_everything_classified_derived_keeps_claims_control_and_registration` | the registry is no longer asserted "misplaced while its writer keeps it in the legacy location"; it is asserted **not** misplaced and present at `PLUGIN_REGISTRY_PATH`; the post-deletion read uses that path. The claims and control assertions are unchanged | the test's premise for the registry no longer holds (IP-R2-9 moved the writer); the property it protects — registration survives deleting everything classified derived — is kept, and `ws07` now also shows it for the whole `governance/generated/` directory |
| `ws07::*` (this workstream's file) | two reads use the new location; four tests added | BC-P2-31 |

---

## 8. New integration points (for the round-3 integration / round 4)

| IP | Owner / file | Exact change | Why |
|---|---|---|---|
| **IP-W7R3-1 (required at integration)** | WS-5 `runtime/src/orchestration/tasks.rs` `OS_MANAGED_PREFIXES` (P2-HO-0033 also asks WS-3 to "treat `governance/registry/` as OS-managed") | add `"governance/registry/"` | Measured (`integration-points/`): a tooling task that registers a plugin while claimed, declaring and allowing the plugin's own files, is refused at close `MUTATION_SCOPE_VIOLATION` for `governance/registry/plugin-registry.json` on the final tree; on the base the same change (under the OS-managed `governance/generated/`) was classified by its seal and passed that stage. With the prefix, `classify_os_path` sees the sealed registry as the OS's own write |
| IP-W7R3-2 | WS-3 `runtime/src/t2.rs` `audit` | `out.extend(crate::capabilities::registry::t2_audit(p));` | WS-2 R3-11: `os_binding_integrity`, D033 and the `t2_bindings` currency class then cover the registry. A 4.1.5 registry's entries are `UNSEALED` (legacy): WS-2's `reporting::t2_severity` decides their severity as for other legacy T2 records |
| IP-W7R3-3 | WS-2 `runtime/src/verification/currency.rs` class `tools_plugins` | add `"governance/registry/plugin-registry.json"` (keep the legacy pattern) | the new path otherwise falls into class `source`: still a currency input, but mislabelled |
| IP-W7R3-4 | WS-4 `runtime/src/cit/materiality.rs` (governance_change rule); WS-5's round-3 close-time materiality hook | treat a change of `crate::paths::PLUGIN_REGISTRY_PATH` that `t2::classify_path` verifies as the OS's own write (like other OS-written T2 stores), not a worker's `governance/**` change needing a CIT | the registry now matches `governance/**` (it no longer sits under the excluded `governance/generated/**`); its writes are already owner-gated by `plugins register` |
| IP-W7R3-5 | WS-9 `migrations/M-4.1.5-4.1.6.yaml` and an op in `migrations/framework.rs`; WS-8 `update` | a migration op that relocates OS stores for installed projects; for the registry, call `crate::capabilities::registry::relocate(p)` | an upgraded project's registry then moves at upgrade rather than at its next registry write |
| IP-W7R3-6 | WS-6 `runtime/src/memory/profile.rs` | (a) in `file_id`, hash with `crate::capabilities::binding::content_sha256(abs)` instead of `sha256_file` (and drop the size+mtime query-time shortcut); (b) take the model/runtime identity from `crate::capabilities::binding::declared_paths(desc, &p.root)`: role `model` → `model.declared: true`, `in_repository` → manifest core, otherwise runtime meta; role `runtime` → runtime identity | (a) measured on a reverted experiment: the benchmark certification test 22.2 s → 17.4 s; the profile then identifies the runtime by the same digest the pin uses. (b) IP-R2-13's consumer side |
| IP-W7R3-7 | WS-3 `cli/src/main.rs` `PluginsCmd::Registry` | the doc comment names `governance/generated/plugin-registry.json`: update it; optionally (IP-W7-4) show `registry::report(&p)`, which now includes `read_from`, `location`, `location_findings` | truthful help text |
| IP-W7R3-8 | WS-8 `framework/KERNEL.yaml` `schema_versions` | `plugin-descriptor: 1.4.0` (with IP-W7-5's `plugin-registry: 1.1.0`, `tool: 1.3.0`) | metadata |
| IP-W7R3-9 | WS-3 `docs/ARCHITECTURE.md` (§4.3 registry); WS-6/WS-9 IP-R2-11 template | state the registry's location (tracked OS-written T2 state at `governance/registry/`, not a regenerable view); a template rule for `governance/registry/**` (authoritative, not indexed, os-only) | documentation and overlay truthful (AC16-X2 reads the template) |
| IP-W7R3-10 (optional) | owner of the workspace `Cargo.toml` | `[profile.dev.package.sha2] opt-level = 3` | debug-build hashing ~20× faster for every component (T2 seals, manifests, pins); no behaviour change |

**Observations for routing (nothing changed for them).**
- O-W7R3-1 (WS-2/WS-5, availability rule): `plugin_governance` is a warning-mode family, but its `medium` findings
  (e.g. a hand-declared executable plugin that is not registered and not pinned — it is already refused at execution)
  make the suite DEGRADED, which WS-5's close gate turns into refusing every governance-affecting close. The severities
  are round 2's and were left as they are; how a warning-mode family's status maps to close refusals is WS-2/WS-5's
  round-3 availability work.
- O-W7R3-2 (verifiers / probe authors): beta-r D6 and gamma-r F4 `F4.b2.x` read or write the registry at the literal
  legacy path; on the repaired tree they no longer exercise the registry (F4.b2.x's forger writes nothing). The labelled
  derived F4 copy in `evidence/derived/` shows the same attack against the new location.

No CLI subcommand, flag or authority class was added (no `g0_label` / `COMMAND_GUARDS` change); no line of
`cli/src/main.rs`, `runtime/src/lib.rs` or any file outside WS-7's ownership was edited except the builder-test updates
of §7. The new module `capabilities/pincache.rs` is registered in `capabilities/mod.rs` (WS-7's).

## 9. Earlier WS-7 integration points

| IP | Status |
|---|---|
| IP-W7-1 | confirmed this round (§5) |
| IP-W7-2 (indexer degradation for a refused `code_intel` plugin) | routed to WS-6 round 3 (P2-HO-0036) |
| IP-W7-3, IP-W7-4, IP-W7-6 | routed to WS-3 round 3 (P2-HO-0033); IP-W7-4 now also covers IP-W7R3-7 |
| IP-W7-5 | routed to WS-8 round 3 (P2-HO-0038); extended by IP-W7R3-8 |
| IP-W7-7 | still true: `ws07::register_approved` answers only through `ws03::human_decide` |
| IP-W7-8 | superseded by IP-W7R3-1 (the registry is no longer under `governance/generated/`) |

## 10. What this run did not do

- It did not move claims, control state or snapshots (other owners' BC-P2-31 writers) or change the overlay template
  (IP-R2-11), so beta-r D6 and AC16-X2 remain for the integrated tree; neither is reachable on this tree anyway (§1).
- It did not wire `t2::audit`, `tasks.rs`, `currency.rs`, `materiality.rs`, the migration, `profile.rs`, the CLI help
  text, `KERNEL.yaml`, docs or `Cargo.toml` (§8).
- It changed no file under `runtime/src/srr/`, and no function body of `tools::install` or `governance::register`.
- It edited no file under `release/verification/`, `release/root-of-trust/`, `release/releases/`,
  `release/orchestration/phase-1/`, `release/capability-baseline/audit-0/`, another workstream's `repair-1/` directory,
  or the Contract v3 source. Probes and held-out suites ran unedited; the derived F4 copy and the `hv_a` copy are
  separate, labelled files in `evidence/`.

## 11. Owner-decision questions

None. Every change stays inside ARCH-0001/ARCH-0003 and the active decisions: no trust boundary moved, no new external
dependency (the lease probe and `statfs` use the existing `libc` dependency), no language runtime in the core, no
owner-controlled material touched.

## 12. Process disclosures

- Model Claude Opus 5 (1M context), `claude-opus-5[1m]`; fresh context; no sub-agents; the product owner was not
  contacted; no session or agent transcripts, task-output stores or user auto-memory were read. Long runs were started
  detached with their output redirected into this run's own `evidence/` or scratch files, which were read directly.
  `CARGO_BUILD_JOBS=2` throughout.
- The machine was heavily loaded by parallel builders during most runs (load average 40-100); timings in §4.5 were
  therefore taken base and final back to back or interleaved, and are noisy.
- A certification run at `222da4e` was stopped after 27 tests (0 failures) to fold in the severity change (`18127a5`),
  and the full evidence set measured at `18127a5` (lib 218/0, certification 140/0, R1 identical to base, named checks
  11/11) was superseded by the correction of §4.3 (`0393bca`); both were moved to scratch, not kept in `evidence/`.
  Every recorded run is at `0393bca`, at the base export, or labelled otherwise.
- The permission system denied one shell command containing `rm -f` (removing superseded outputs); it was not retried
  — the files were moved to scratch instead. A `__pycache__` directory that a Python import wrote into `evidence/`
  was moved to scratch the same way.
- One reverted experiment (WS-6's `profile.rs` hashing through `content_sha256`, §4.5) was made to size IP-W7R3-6; it
  was measured and reverted with `git checkout` before any commit (`git status` recorded clean for that file).
- My own probe drafts had defects fixed before the recorded runs: a miscounted execution total in two checks, a missing
  index build before a close, and a comma-separated `--allowed` list.
