# WS-7 repair report: repair iteration 1, round 2 (P2-AR-0028)

| | |
|---|---|
| Run | P2-AR-0028, role `capability-repair`, model Claude Opus 5 (1M context), `claude-opus-5[1m]` |
| Handoffs | P2-HO-0026 (WS-7), P2-HO-0020 (round-2 common), P2-HO-0010 (common protocol) |
| Branch / base | `phase2/repair-1-r2-ws07` from `843d79c33e8a8db8b223611abc23d317edbc82a1` (integrated round-1 tree) |
| Work commits | `138472e` (repair, tests), `371794a` (no memoised hashes; running binary by inode), then the commit that adds this report and `evidence/` |
| Product identity at `371794a` | `product_code_digest e9ff786cbc6bac4fa8fea700950f888f1d79459f04478880bf2cf273947fcbcc`, `governed_state_digest 4981437f…c227d` (unchanged from base) |
| Classes | BC-P2-39, BC-P2-40, BC-P2-41, BC-P2-11 (plugin side), BC-P2-09 (registry side) — all `REPAIRED_CLAIMED` |
| Integration points | WS-3 IP-6 (registry sealing) implemented; WS-6 IP-3 (tool/plugin health failures) implemented |

**Status of these claims.** They come from the builder, and the evidence is regression evidence only (Contract v3 O3).
Nothing here says a class is accepted, verified or closed; that belongs to the independent verifiers.

---

## 0. Evidence index and regression

| What | Where | Result |
|---|---|---|
| `cargo test --lib` | `evidence/regression/cargo-test-lib.out` | **155 passed, 0 failed** (146 at base + 6 `capabilities::binding` + 3 `tools`) |
| `cargo test --test certification` (includes `section6.rs`, the §6 derivation) | `evidence/regression/cargo-test-certification.out` | **105 passed, 0 failed** (100 at base + 5 new in `ws07.rs`) |
| rustfmt on every touched Rust file, build warnings, Python plugin tests | `evidence/regression/fmt-build-python.out` | clean; 0 warnings; 4/4 |
| R1 held-out suites, all four rounds, **unedited**, private scratch path, before and after | `evidence/r1-heldout/r1-heldout-base-843d79c.out`, `r1-heldout-final-371794a.out`, runner `run-r1-heldout.sh` | identical before and after: AR-0027 26/3, AR-0029 26/2 (`ho_f` does not compile, as recorded), AR-0031 27/7, AR-0033 30/1 (`hv_a::a1` size pin only). §0.1 |
| AR-0033 census, size assertions removed (labelled copy) + `derive.py` | same files, `SUPPLEMENTARY (S1)/(S2)`; copy `r1-heldout/hv_a_derivation.a1-unpinned.P2-AR-0028.rs.txt` | before 105 files / 1457 functions, after **106 / 1494**; **0 violations in every §6 activity**, all three splitters |
| Audit-of-record probes named by the repair delta, unedited, before/after | `evidence/probes/{base-843d79c,final-371794a}-{unedited,shim}/`, runner `run-probes.sh`, pairing `COMPARE-probes.out` (`compare_probes.py`) | shim mode: every named line **FAIL → PASS**; LEAD-X4 **1/4 → 4/4**. §0.2 |
| WS-7 named checks (discriminating; legitimate paths; base is the negative control) | `evidence/ws07_named_checks.py`; `probes/ws07-named-checks.base-843d79c.out`, `…final-371794a.out` | base **3 of 24 pass** (21 FAIL); final **26 of 26 PASS** |
| Other families' probes whose fixtures declare plugins by hand (disclosure for integration) | `evidence/cross-family/`, runner `run-cross-family.sh`, adapter `gov-ws07-preregister.py`, summary `COMPARE-cross-family.out` | §8 |

Binaries measured: base `gov` sha256 `7095d188…0332` (release build of `843d79c`), final `ec2a76fe…31b4` (release build of
`371794a`). Every output records the sha256 of the binary it drove.

### 0.1 R1 preservation

`srr/plugins.rs` (the `guard_acquisition` sink) and `tools::install` (the second acquisition primitive) are §6 effect
sites examined at R1 (AR31-N1/N2, AR27-N6). **`runtime/src/srr/plugins.rs` is not changed** (`git diff 843d79c -- runtime/src/srr`
is empty). `tools::install` keeps, verbatim, `guard_write(p, "tools install")` and `guard_acquisition_below_floor("tools install")`
as its first statements, and still writes the capability registry, so the derivation still finds both writers
(`register`, `install`). `governance::register` still reaches `guard_acquisition` before any write. The held-out
`hv_d::d4` pin (`let privileged = is_privileged(descriptor);` inside `guard_acquisition`, and an unprivileged remote
acquisition admitted above floor) is untouched. `tests/certification/section6.rs` passes (9/9). The derived census
reports `privileged_plugin_acquisition` 9 derived / 2 writers / 0 violations (base: 10 / 2 / 0 — the removed TOFU
`observed_path` helper was one derived non-writer).

The R1 runs use a scratch directory private to this run (`…/scratchpad/p2ar0028/r1`, symlinks recorded in the output as
pointing at this worktree), record `worktree HEAD`, `product files differing from HEAD: 0`, and the census
`106 .rs files`, which matches this tree (P2-HO-0020 item 7).

### 0.2 Why two probe modes

The audit-of-record probes predate WS-3: unedited, they relay human answers with `decide --by owner`, which WS-3 refuses on
both trees, so every line that needs a human answer (F3 (b), F4.b5, F4.b5.x, LEAD-X4) is unreachable in `unedited` mode on
base and final alike. The `shim` mode reaches `gov` through the round-1 integration builder's evidence adapter
(`repair-1/integration/evidence/audit-probes/gov-owner-channel-shim.py`, used unmodified), which changes only the three paths
WS-3 removed by design (undeclared role, the `--by owner` relay → an owner-signed answer, absent package fields). The
probe files themselves are never edited. `COMPARE-probes.out` pairs each named line base/final in both modes.

---

## 1. BC-P2-39 — plugin elevation is not decided by self-declaration

**Requirement** (repair-delta §1; Contract v3 F4:426 "Descriptor cannot authorise itself", :430; ARCH-0003 §9 "Descriptors
cannot self-authorise"; synthesis `owner-decisions-required.md` row 2): whether a plugin's execution needs an
elevated-permission gate does not depend on the descriptor's own declarations — either declared permissions are enforced at
run time, or every executable plugin that can exceed the non-elevated floor requires registration and a specific gate;
D-0005's hand-declared allowance stays satisfiable for effects that are enforced or non-elevated. A design adding a new
external dependency class needs owner adoption.

**Design chosen (within the accepted architecture).** Enforcement at run time would need an OS sandbox (namespaces,
seccomp, Landlock, a container runtime) — a new external dependency class; **not chosen**. The second conforming design
is implemented: the OS classifies every plugin by **what its command executes**, never by what it declares
(`runtime/src/capabilities/binding.rs`, `ExecutionClass`):

- **`OS_PROVIDED`** — the command runs *this* `gov` binary (same device/inode as `/proc/self/exe`, or a byte-identical copy)
  as one of `OS_CAPABILITY_SERVERS` (today `capabilities serve-embed [--id X] [--reverse]`, which reads one request on stdin,
  writes one response on stdout and opens no project). Its effects are the release's own and cannot exceed the non-elevated
  floor, so it keeps **D-0005's hand-declared allowance** (roles at/above `TOOL_POLICY.plugins.min_authority`).
- **`EXECUTABLE`** — anything else (a script, an interpreter with a module or inline code, a binary, or the same binary
  asked to do anything else). It is an unsandboxed child process with the invoking account's authority, so it can exceed the
  floor whatever it declares. It runs **only** with an OS-written, T2-verified registration **and** a presented,
  owner-answered gate raised for exactly that plugin's registration subject (§4), re-verified at every execution.

Declared `permissions` / `required_permission_classes` still act, only in the direction that cannot widen anything: the
acting role must hold every declared class, the declarations are shown to the approver, and declared elevation raises the
gate's stated impact radius (R4). They never decide *whether* approval is needed. This narrows D-0005 consequence 3 to the
non-elevated remainder, as the synthesis adjudicated (row 2).

**Where it is enforced** (`capabilities::governance::authorize`, called by every execution path through `plugin_set`:
`capabilities invoke`, the indexer and embedder, retrieval/rerank, code intelligence, benchmarks): after standing, floor,
roles, permission classes and health, the implementation is resolved; an `EXECUTABLE` plugin without a registration is
refused `PLUGIN_NOT_APPROVED` with `cause: UNREGISTERED_EXECUTABLE`, remediation text, and the implementation it would have
run. `gov plugins health --ping` now pings only plugins the acting role may execute (before, it ran any descriptor declaring
`protocol_ping`, registered or not). Doctor D028 / suite family `plugin_governance` report every unregistered executable
plugin (medium; high when it is the pinned embedder/reranker).

**Probes** (`COMPARE-probes.out`; named checks)

| Line | Base | Final |
|---|---|---|
| gamma-r `F4.b1` UNDER-declaration (unedited and shim) | FAIL (`ok=True`, `UNDECLARED_WRITE.txt` written) | **PASS** (`PLUGIN_NOT_APPROVED`, no side effect) |
| W7-39.a–e: under-declaring plugin via invoke (L2, L4), pinned embedder (`rebuild-memory`), `plugins health --ping`; D028 | FAIL ×5 | **PASS ×5** |
| W7-39.C1 positive control: hand-declared OS capability server runs | holds | holds |

**Tests.** `ws07::an_executable_plugin_never_runs_on_its_own_declarations` (all three roles, pinned embedder, health ping, D028,
the OS-server allowance and its exact-flags boundary, declared-pin check); `binding::tests::the_os_capability_server_is_recognised_only_with_its_own_flags`.

**Owner question:** none. (If the owner ever wants hand-declared *scripts* to run again, that needs an OS sandbox
dependency class — an owner adoption, not a repair choice. The class does not depend on it.)

---

## 2. BC-P2-40 — plugin implementation bytes bound

**Requirement** (Contract v3 F4:428 "Descriptor/implementation bytes are hash-bound", :429 "Drift/tampering fails closed"):
every executable plugin's implementation and descriptor bytes — module-form and interpreter-only commands included — are
bound in tracked, OS-written registration state; any change fails closed at execution and is reported by health checks; a
reset of machine-local state or a fresh clone cannot re-baseline tampered bytes.

**Changes** (`binding::resolve`, `registry::record`, `governance::authorize`/`integrity`):

- The implementation is derived by the OS from the command vector: the **program** (resolved on `PATH` exactly as `exec`
  resolves it, symlinks followed), every **argument that names a file**, the **whole top-level package** of a
  `python3 [opts] -m pkg.mod` command (found by asking that interpreter for its search path from the plugin's working
  directory and applying Python's finder order: regular package → module file → namespace portions — `__pycache__`
  included, because a planted byte-code file with a matching source stamp is loaded instead of the source), and every path
  listed under the new descriptor field `implementation:`. Inline code (`sh -c`, `python3 -c`) lives in the descriptor,
  whose bytes the registration binds. A command whose implementation cannot be located is refused
  (`PLUGIN_IMPLEMENTATION_UNRESOLVED`) — nothing unbound runs.
- The registry entry records `implementation` (every bound file: role, path, sha256), `implementation_sha256` (never null),
  `program`, `command`, `cwd`, `execution_class` and the descriptor hash; `authorize` recomputes the implementation at every
  execution and refuses any difference `PLUGIN_PIN_MISMATCH`, with the changed/added/removed files in the details.
- **Trust-on-first-use is removed.** The machine-local `observed.json` is neither written nor read; an unregistered
  executable never runs (§1), so there is nothing a reset can re-baseline.
- The plugin runs without the caller's loader variables (`binding::LOADER_ENV_VARS`: `PYTHONPATH`, `PYTHONHOME`,
  `PYTHONSTARTUP`, `NODE_OPTIONS`, `LD_PRELOAD`, `LD_LIBRARY_PATH`, `BASH_ENV`, `PERL5LIB`, `RUBYOPT`, `CLASSPATH`, …) and
  with `PYTHONDONTWRITEBYTECODE=1` (`host::invoke` → `binding::apply_plugin_env`); module resolution runs under the same
  environment. So a caller cannot substitute code (a `sitecustomize` on `PYTHONPATH`, an `LD_PRELOAD`) without touching a
  bound byte, and an execution does not rewrite its own bound tree.
- **Fresh clone / other machine**: registry entries sealed on another machine are `Foreign` (or `KeyUnavailable`) and never
  honoured (§5). The tracked entry still carries the registered hashes: re-registering is a new governed act, and its gate
  package states whether the implementation differs from the tracked registration ("The tracked registry records a DIFFERENT
  implementation … approving re-baselines the plugin onto the bytes listed here").
- Health checks: `governance::integrity` (role-independent) reports implementation drift, descriptor mismatch, unbound
  entries and unapproved registrations to doctor D028 and the suite family, whatever the acting role.
- A defect found during this run and fixed (`371794a`): a per-process hash memo keyed by (size, mtime, inode) returned a stale
  digest when a bound file was rewritten with the same size inside one filesystem timestamp tick (caught by
  `binding::tests::a_script_binds_the_program_and_the_script_and_any_edit_changes_the_identity`). Bound files are now hashed
  afresh at every authorisation; the running binary is recognised by device/inode and hashed at most once per process.

**Probes**

| Line | Base | Final |
|---|---|---|
| synthesis `LEAD-X4` (shim): `X4-F4:428-implementation-pinned`, `X4-F4:429-drift-fails-closed`, `X4-F4-doctor-sees-drift` | FAIL ×3 (`implementation_sha256: null`, swapped code ran, D028 "no plugin problems") | **PASS ×3** (module tree + interpreter bound; `PLUGIN_PIN_MISMATCH`; D028 names `synthplug/__main__.py`) |
| gamma-r `F4.b3/b4` TOFU reset re-baselines drifted bytes | FAIL (`after reset: ok=True`) | **PASS** (refused) |
| gamma-r `F4.b3/b4` interpreter-only command runs with no pin | FAIL (`ok=True`, pin `None`) | **PASS** (refused until registered; registered inline code is bound through the descriptor, W7-40.e) |
| W7-40.a–g: module-form bound; module swap refused + D028; planted `.pyc` refused; `PYTHONPATH` sitecustomize never runs; inline-code edit refused; runtime-state reset; fresh clone | FAIL ×4, then the scenario could not complete on base | **PASS ×7** |

**Tests.** `ws07::every_byte_a_plugin_executes_is_bound` (module form incl. interpreter binding, swap/new file/planted
`.pyc`, `PYTHONPATH` injection, runtime-state reset, fresh clone with the re-registration package, inline code, declared
helper, unresolvable module); `binding::tests` (script identity, inline code in the subject, missing program/declared path,
Python name recognition, finder order).

**Limits.** (a) A static reading of a command cannot find code an implementation reads and evaluates from a location it does
not name (a script that `eval`s an arbitrary file, a module importing a sibling it is not packaged with). The gate package
lists the exact bound file set, and `implementation:` brings such code inside the binding. (b) The program is bound too, so
an interpreter or tool upgrade requires re-registration (fail closed by design). (c) The tracked entry contains
machine-local absolute paths (e.g. `/usr/bin/python3.12`); a clone re-registers anyway.

---

## 3. BC-P2-41 — tool review and approval bound to the installation

**Requirement** (Contract v3 F3:416-423, F4:431 "Security review cannot be self-attested"; D-0007 consequence 4): security-review
evidence is a governed security review of that tool identity/version; when approval is required, a presented, answered-A
gate raised for that exact installation lets the governed install proceed and a decline ends it.

**Changes** (`runtime/src/tools.rs`):

- **Security review** (`security_review_evidence`, pure core `review_verdict`): the named record must be a `report` that a gov
  operation wrote as it stands (**T2 `Verified`** — reports are T2 state under D-0007, so a hand-written or edited one is a
  request), ACTIVE with outcome `success`, closing a **`security`-class task** (`task.closed_by_report` names it), carrying a
  `security_review` block naming **exactly this `tool_id` and pinned version** with `verdict: passed`, and written by a
  **session and a role other than the installer's**. A descriptor's own `security_review: passed`, an unrelated record
  (a gate, a decision), or a hand-written report is not evidence; the detail says which rule failed.
- **Installation subject** (`installation_subject`): tool id, pinned version and the installation descriptor (commands,
  permissions, licence, cost, …) minus request/result fields (`human_gate`, `registration_gate`, `approval_gate`, `status`,
  `installed_*`, …), so citing a gate changes no installation and any real change is a new request.
- **Approval bound to the installation**: a failed condition raises `gates::create_system` with trigger `tool_install`
  (human-only) and `subject: {kind: tool-installation, id, version, sha256}`. On the next run the OS finds gates by that
  subject (a gate id cited in the descriptor is a candidate only; a cited gate raised for anything else is reported
  `GATE_MISMATCH` in `gates_not_honoured`) and evaluates them with WS-3's `gates::human_approval_for`: an owner-signed
  authorising answer → **the same install proceeds** (the tool record carries `approval` and `installation_sha256`);
  a decline → **`declined: true`, the request ends, no new gate**; pending → **the same gate is returned**, never a duplicate.
- The installer role is the acting role: a different role passed to `tools::install` is refused `ROLE_CONFLICT` (defensive —
  at the CLI `--role` is global, so the subcommand flag already sets the acting role).
- **WS-6 IP-3**: a failing tool health check (`tools health`, and the check after an install) is recorded with
  `memory::failures::record_tool_failure` (`tool_kind: tool`, code `TOOL_HEALTH_FAILED`), idempotent, `not_recorded` under
  FREEZE_WRITES/PAUSE; the row carries `failure_memory`.

**Probes**

| Line | Base | Final |
|---|---|---|
| gamma-r `F2F3-tools` F3 (b) (shim): owner answers the install gate A, the same install re-run | FAIL (`installed= False`, new gate each time) | **PASS** (`installed= True`, no new gate), also when citing the gate |
| gamma-r `F4.b6` (shim): an unrelated gate named as the security review | FAIL (`installed= True`) | **PASS** (`not a security review report`) |
| W7-41.a–f: unrelated record; hand-written report; pending returns the same gate; approved gate proceeds; decline ends; unrelated cited gate | FAIL ×5 (+ W7-41.f passes on base only because a gate was raised) | **PASS ×6** |
| W7-IP3: failing tool health check recorded | FAIL | **PASS** (`spec/reports/failures/FAIL-*.yaml`) |

**Tests.** `ws07::a_tool_installation_is_approved_only_for_that_installation`; `tools::tests` (a governed review of this
tool/version by another author is evidence; each shortfall is not; the installation subject ignores citations only).

**Limit — dependency on WS-5.** No gov operation seals task-close reports yet (`orchestration/tasks.rs` is WS-5's), so no
report can currently be a T2-verified security review, and **every tool installation that needs the security condition is
routed to the owner's gate** (fail-safe; autonomy returns when IP-W7-1 lands). The positive path is covered by
`tools::tests::a_governed_review_of_this_tool_and_version_by_another_author_is_evidence`.

---

## 4. BC-P2-11 (plugin side) — elevated registration authorised only by a gate raised for that plugin

**Requirement** (Contract v3:430, :678): an elevated plugin registration is authorised only by a presented, answered-A gate
raised for that plugin identity/version and permission set; any later change makes it stale.

**Changes** (`governance::register`, `approval_for_subject`, `authorize` step 8):

- `binding::registration_subject` is the approved subject: `{kind: plugin-registration, plugin_id, capability, version,
  descriptor (normalized: request/OS-copy fields removed, registration defaults applied), implementation (class, program,
  every bound file and hash)}` → `registration_subject_sha256`. The descriptor part covers the command, working directory,
  declared permissions and classes and approved roles, so widening any of them is a new subject.
- Registration raises `gates::create_system` with trigger `privilege_elevation` (a WS-3 human-only trigger: never
  agent-resolvable) and `subject: {kind: plugin-registration, id, version, sha256, implementation_sha256}`; the package lists
  the command, every bound file with its hash, the declared (unenforced) permissions and roles, and what the tracked registry
  says about earlier implementations.
- The next `gov plugins register` finds the gate by subject (`approval_for_subject`; a cited `registration_gate` is only a
  candidate) and honours it only through `gates::human_approval_for(p, gate, subject)` (T2-bound, presented, owner-signed,
  re-verified against the current anchor, authorising, bound to exactly this subject). Pending → the same gate is returned;
  declined → the request ends; an unrelated or another plugin's gate → reported `GATE_MISMATCH`, never honoured.
- **At every execution** `authorize` recomputes the subject from the current descriptor and implementation, requires it to
  equal the registry's `registration_subject_sha256`, and calls `human_approval_for` again: a revoked gate or withdrawn decision
  (`GATE_REVOKED`), a changed byte or a widened permission set stops the plugin.

**Probes**

| Line | Base | Final |
|---|---|---|
| gamma-r `F4.b5.x` (shim): unrelated answered gate registers a new network plugin; it runs | FAIL ×2 (`registered= True`, runs) | **PASS ×2** (new gate raised for the plugin; `PLUGIN_NOT_APPROVED`) |
| gamma-r `F4.b5` (shim): re-register while the gate is PENDING | FAIL (a second gate) | **PASS** (the same gate) |
| gamma-r `F4.b5` revoke → refused | refused | refused (`GATE_REVOKED`) |
| W7-11.a–e | FAIL ×3 (W7-11.b/d pass on base: no gate is raised at all / elevated revoke already refused) | **PASS ×5** |

**Tests.** `ws07::a_registration_is_approved_only_by_a_gate_raised_for_exactly_it` (unrelated gate, pending, decline,
revoke-then-re-raise, subject bound in the registry, permission widening, another plugin's gate, revocation at execution).

**Limit.** Unregistering does not withdraw the owner's approval: a sealed entry restored by hand (e.g. from version control)
for the *unchanged approved bytes* runs again until the gate is revoked (`gov gate revoke`). The approval never extends to
other bytes (§2) — this is the T2 rollback limit WS-3 stated for all sealed records.

---

## 5. BC-P2-09 (registry side) and WS-3 IP-6 — registry entries honoured only as the OS wrote them

**Requirement** (Contract v3:427 "Registration/provenance live in trusted OS state"; D-0007 T2 and rule 2; ARCH-0003 §9;
IP-6: seal registry entries with `t2::seal_value`, honour only `Verified`).

**Changes** (`capabilities/registry.rs`):

- `registry::record` seals **every entry** with `t2::seal_value(…, "plugins register")` and **the document as a whole**
  (`os_binding` at top level; re-sealed by `unregister`), so `t2::classify_path` sees the file as an OS write exactly when it
  is what gov wrote (for WS-5's task-close mutation scope).
- `registry::standing` returns `Registered` only for a `Verified` entry whose key equals its `plugin_id`; anything else is the
  new `Standing::Unbound { binding }` → refused `PLUGIN_REGISTRATION_UNBOUND` with the T2 details; legacy unsealed entries,
  hand-written or edited entries, and entries sealed on another machine are never honoured.
- `registry::unbound_entries` / `governance::integrity` / `governance::findings`: doctor D028 and suite family
  `plugin_governance` report every unbound entry (high), with or without a descriptor. `registry::report` and
  `registry::document_binding` expose the binding per entry and per file.
- The generated tool registry (`tools::plugin_tools`) takes registration, approval and provenance only from the verified
  registry: an unregistered executable is `status: unregistered` with no approved roles, a plugin failing integrity is
  `blocked`, approved roles are cut to the kernel floor (gamma-r A0-F2-02: an L0/L1 role is never offered a plugin execution
  would refuse).
- Plugin registry schema 1.1.0 records the new fields (`os_binding`, `implementation`, `registration_subject_sha256`,
  `execution_class`, …).

**Probes**

| Line | Base | Final |
|---|---|---|
| gamma-r `F4.b2.x` (shim): a worker's hand-written entry makes `netplug` run | FAIL (runs for tooling-engineer and orchestrator) | **PASS** (`PLUGIN_REGISTRATION_UNBOUND`) |
| gamma-r `F4.b2.x` suite `plugin_governance` reports it | FAIL (`findings mentioning netplug: []`) | **PASS** |
| gamma-r `F4.b2.x` doctor D028 line | not measurable in the probe (it prints the first 400 characters of D028, which other findings fill); W7-09.b shows D028 and the suite naming the forged entry | — |
| gamma-r `F2.b8.x`: a hand-declared plugin shown active/approved for all roles | FAIL | **PASS** (`status=unregistered`, `approved_roles=[]`, no role exposure) |
| gamma-r `FRESH.4` | the probe's green record is not green on either tree (an unrelated skill scenario makes the audit DEGRADED), so close is refused `GOVERNANCE_SUITE_STALE` on both: not discriminating here. The registry file is a WS-2 currency input (`verification/currency.rs`, class `tools_plugins`), and a forged entry now also produces a `plugin_governance` finding | — |
| W7-09.a/b | FAIL ×2 | **PASS ×2** |

**Tests.** `ws07::registry_entries_are_honoured_only_as_the_os_wrote_them` (a copied sealed entry, a fresh unsealed entry, an
edited entry, an orphan unsealed entry, restoration).

**Limits.** The seal is detection-grade against a process with the operator's full OS privileges (it can read the machine
key — WS-3's stated limit). For executable plugins the decisive binding is not the seal but the owner-signed answer bound to
the registration subject, which execution re-verifies: a forged-but-sealed entry still runs only bytes the owner approved.

---

## 6. Integration points implemented (routed to WS-7)

| IP | From | Status | How |
|---|---|---|---|
| IP-6 | WS-3 §9 | **implemented** | §5: entries and document sealed with `t2::seal_value`; only `Verified` entries honoured |
| IP-3 | WS-6 §8 | **implemented** | §3 (`tools health`, post-install check) and `governance::health` (static failure or failed ping of a plugin): `memory::failures::record_tool_failure` |

## 7. New integration points for round 3 (not implemented here: files owned elsewhere)

| IP | Owner / file | Exact change | Why |
|---|---|---|---|
| IP-W7-1 | WS-5, `runtime/src/orchestration/tasks.rs` close (the report writer, ~line 1049) | `crate::t2::seal_record(&mut rec, "task close")?;` immediately before `save_record(&p.root, &rec)` of the close report | A security-class task's close report can then be the governed security review `tools::security_review_evidence` accepts (T2 `Verified`); until then every tool install needing it is routed to the owner's gate (§3 limit). D-0007 already classes reports as T2 |
| IP-W7-2 | WS-6, `runtime/src/memory/indexer.rs` code-intel loop (~line 1265) | When `governed.denied` holds a `code_intel` descriptor for the file's language (match the descriptor's `languages` via `capabilities::host::discover_all`), push a degradation `"{rel}: plugin {id} refused ({code}); built-in extractor used"` and `note_tool_failure(tool_failure_from("code_intel", id, version, &refusal, "rebuild-memory"))` | D-0005: a code_intel degradation is recorded. With module-form binding a tampered adapter is now refused rather than run, and the indexer falls back silently (beta-r `C5-b8-degrade` in `cross-family/`) |
| IP-W7-3 | WS-3, `framework/policies/ENFORCEMENT_MAP.yaml` | Re-word `TOOL_POLICY.plugins.elevated_permission_classes` ("classifies DECLARED elevation shown in the registration gate, raising its impact radius; every executable plugin needs the gate whatever it declares — capabilities::governance::authorize, register"), `refuse_on_pin_drift` ("drift always fails closed, Contract v3 F4:429; a false value is reported, never obeyed"), `registration_binds` (add `registration_subject_sha256`, `registration_gate`) | Keep the map's descriptions true; the keys stay referenced (the builder test passes) |
| IP-W7-4 | WS-3, `cli/src/main.rs` `PluginsCmd::Registry` arm | `gov_runtime::capabilities::registry::report(&p)` instead of `registry::load(&p)` | Show each entry's T2 binding and the document binding (optional) |
| IP-W7-5 | release/kernel owner (WS-8), `framework/KERNEL.yaml` `schema_versions` | `plugin-descriptor: 1.3.0`, `plugin-registry: 1.1.0`, `tool: 1.3.0` | Metadata only; no check reads it |
| IP-W7-6 | record owner (orchestrator; unowned in repair-delta §3), `spec/interfaces/API-0001.yaml` governance clause, `spec/decisions/D-0005.yaml` consequence 3, `docs/` plugin sections | Amend through a governed change (CIT): every executable plugin needs a registration approved by a gate raised for it; only OS capability servers run hand-declared; implementation binding replaces the per-version first-observed hash | The normative sources (Contract v3 F4, ARCH-0003 §9) already determine this (synthesis row 2); the records still state the superseded behaviour. `capabilities/PROTOCOL.md` is updated here |
| IP-W7-7 | WS-3 (P2-ADJ-0001 follow-up) | none required; note: `tests/certification/ws07.rs::register_approved` answers gates only through `ws03::human_decide`, so it follows whatever WS-3's helper does when the standalone anchor default becomes `false` | test dependency |
| IP-W7-8 | WS-5 (WS-3 IP-1, task close `t2::classify_path`) | none beyond IP-1: the registry file carries a document-level seal, so a task that registers a plugin through gov is not flagged and a hand edit is | dependency note |

No new CLI subcommand, flag or authority class was added (no `g0_label` / `COMMAND_GUARDS` change needed); no line of
`cli/src/main.rs`, `runtime/src/lib.rs` or any file outside WS-7's ownership was edited except the declared additive test
registration `tests/certification/main.rs: mod ws07;` and the builder-test updates in §9.

---

## 8. Consequence for other families' probes (disclosure for integration and verifiers)

Several audit-of-record probes of other families use **hand-declared executable plugins as fixtures** (beta-r C5, C8, D4, D5,
D6; alpha-r A3; gamma-r F5; epsilon-r O4). Under BC-P2-39 those fixtures no longer run, so lines that relied on them change
(`cross-family/COMPARE-cross-family.out`, shim mode, base vs final):

- beta-r **C5-b8, C5-b8-degrade** PASS → FAIL; **D4** stops at setup (`PLUGIN_NOT_APPROVED`); **D5** b2/b5/b6-* PASS → not
  reached; **D6** reranker never registers (`RERANKER_UNAVAILABLE`); alpha-r **A3 C4** refusals now read `PLUGIN_NOT_APPROVED`;
  gamma-r **F5.b4(d)** cannot invoke its hand-declared plugin (probe parse error). C8 is unchanged (17/17).
- To show the capabilities those probes measure still work with governed plugins, `prereg` mode re-runs them through
  `gov-ws07-preregister.py` (labelled evidence adapter): it registers each **unregistered** fixture plugin the governed way
  (register → present → owner-signed A → register) and completes gates a probe's own `plugins register` raises; it never
  touches a registered, mismatched, unbound or otherwise refused plugin. Result: C5-b8 PASS again; D5 **20/4 vs base 16/8**
  (D5-b5-revision-bound and D5-b6-ungoverned become PASS because module-form embedders are now bound); D6 as base.
  Remaining differences are probes that **edit a registered descriptor** afterwards (D4-b1/b7/b10: now
  `PLUGIN_REGISTRY_MISMATCH`, i.e. a re-registration is required — intended) and **C5-b8-degrade** (IP-W7-2).

## 9. Existing builder tests changed, and why

No assertion was weakened; each change follows the new, intended behaviour.

| Test | Change | Reason |
|---|---|---|
| `arch::plugin_protocol_is_language_neutral_bash_embedder` | registers the bash embedder through `ws07::register_approved` (owner-answered gate), then removes the hand-written copy of the descriptor | BC-P2-39: an executable plugin runs only registered and approved |
| `repair::reranker_hook_invoked_and_never_silently_skipped`, `repair::plugin_host_large_response_through_cli` | same registration; the reranker test removes the registered descriptor (written under the plugin id) where it removed the hand-written one | BC-P2-39 |
| `repair2::plugins_are_governed_capabilities_not_arbitrary_commands` | "an L4 role may execute a valid hand-declared plugin" is now asserted **refused** (`PLUGIN_NOT_APPROVED`, not executed) and then registered; "a version bump re-pins the implementation" is now `PLUGIN_REGISTRY_MISMATCH` until an approved re-registration; the declared-pin edit of a registered descriptor is `PLUGIN_REGISTRY_MISMATCH` (the declared-pin check itself is covered on an OS capability server in `ws07`); the approved-roles narrowing is registered through a gate | BC-P2-39; BC-P2-40 (the version-bump re-pin was the machine-local re-baseline A0-F4-04 found) |
| `repair3::plugin_descriptors_can_never_authorise_themselves` step 4 | registration through `ws07::register_approved` | BC-P2-39 |

`srr::a_privileged_capability_acquired_from_outside_needs_a_delegated_signed_target` is unchanged: `plugins register` reports
its `acquisition` verdict also when it raises a gate.

## 10. What this run did not do

- It did not add an OS sandbox (would need owner adoption) and did not change `runtime/src/srr/plugins.rs`: the SRR-R0-L6
  delegation layer still classifies *privilege* by declaration (R1-accepted; held-out `hv_d::d4` pins it). What BC-P2-39
  addresses — whether the F4 approval is needed — no longer depends on it; every executable plugin needs the owner's gate.
- It did not seal task-close reports (WS-5), change the indexer (WS-6), `ENFORCEMENT_MAP.yaml`/`cli/src/main.rs` (WS-3),
  `KERNEL.yaml`, `API-0001`, `D-0005` or docs (§7).
- It did not change how hand-written project tool records under `governance/project/tools/` are honoured, nor tool-health
  command execution (gamma-r A0-F2-01/A0-F3-02, non-blocking and not assigned).
- It edited no file under `release/verification/`, `release/root-of-trust/`, `release/releases/`, `release/orchestration/phase-1/`,
  `release/capability-baseline/audit-0/`, another workstream's `repair-1/` directory, or the Contract v3 source. Probes and
  held-out suites were run unedited; adapters and the labelled `hv_a` copy are separate files in `evidence/`.

## 11. Owner-decision questions

None. BC-P2-39 is satisfied by a design inside the accepted architecture; the only design that would need owner adoption
(an OS sandbox, to let hand-declared scripts run with enforced permissions) was not chosen and is not needed.

## 12. Process disclosures

Model Claude Opus 5 (1M context), `claude-opus-5[1m]`; fresh context; no sub-agents; the product owner was not contacted;
no session or agent transcripts, task-output stores or user auto-memory were read; long commands ran in the foreground with
output redirected into `evidence/`. `CARGO_BUILD_JOBS=2` throughout. One shell command containing `rm -rf` was denied by the
permission system and not retried; superseded interim outputs were moved to scratch instead. Interim runs at `138472e`
(before the §2 hash-memo fix) are not in `evidence/`; every recorded run is at `371794a` or at base `843d79c`.
