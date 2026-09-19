# P2-AR-0022 — Repair iteration 1, round 1: integration report

| Field | Value |
|---|---|
| Run | P2-AR-0022, fresh `capability-repair` **integration builder**, model Claude Opus 5 (1M context), `claude-opus-5[1m]` |
| Handoffs | P2-HO-0019 (integration), P2-HO-0010 (common protocol); each round-1 builder's `repair-1/<ws>/00-REPAIR-REPORT.md` |
| Branch / base | `phase2/repair-1-integration` from `12c68d3094e5c211db137aad43f00174c43abffb` |
| Merged | `phase2/repair-1-ws03` `6853526`, `-ws04` `14c7f68`, `-ws05` `4a91c45`, `-ws06` `ffbe8c9`, `-ws08` `ea8efca`, `-ws09-11` `bc7c030`, `-ws02` `37bfcd1`, `-ws01-12` `0dc7798` (all from `c6b60bc`), in that order, `--no-ff` |
| Integrated product tip | `811317b5bbf93cd2a71c911d895c4ce67c44114a` — `product_code_digest b1ab1c8c0268adfec2cd857a94d79583efbbf30e3b547e2faf610aac0cbffbb1`, `governed_state_digest 4981437f0dca482b0d7d2aba2d48378260a93eaace20f1ea15bb5761ec4c227d` (`release/orchestration/phase-2/tools/product_identity.py`). The commit that adds this report and `evidence/` changes no product file, so it carries the same `product_code_digest`. |
| Verdict | **`READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`**: the integrated tree builds, `cargo test --lib` 146/0, `cargo test --test certification` 100/0, Python plugin tests 4/4, rustfmt clean on every touched file, every prior R1 held-out suite at its recorded baseline except the known AR-0033 `hv_a::a1` size pin (its census: 0 violations). No two repairs contradicted each other; nothing was stopped. |

This is an integration builder's record. It grades no repair and claims no class; every result below is regression evidence
(Contract v3 O3). Acceptance is for the fresh independent verifiers (AC-14 R1 preservation, AC-6 oracle-format review,
capability verification).

---

## 1. Merges

All eight branches merged with `git merge --no-ff` in the handoff order (WS-3 first). Three merges had textual conflicts;
each was resolved as the union of both sides, and nothing else was edited in a merge commit
(`evidence/merge-and-change-log.out` holds the `git show --cc` of each).

| Merge | Conflict | Resolution |
|---|---|---|
| `4e647ee` ws08 | `tests/certification/main.rs`: `mod ws03;` (WS-3) vs `mod ws08;` (WS-8) | both lines |
| `2b7aca7` ws02 | `cli/src/main.rs`: `Cmd::Artefact` (WS-4) vs `Cmd::Health` (WS-2) variants; their `command_name` arms | both variants, both arms |
| `badd915` ws01-12 | `cli/src/main.rs`: the two above vs `Cmd::Oracle` + `OracleCmd` (WS-1/12); `run()` arms `Health`/`Oracle`; `command_name` arms | all three variants, the `OracleCmd` enum, all arms |

Every other file merged cleanly, including the two disjoint `runtime/src/records.rs` regions (WS-4 relation fields,
WS-6 record text) and the `pub mod` lines of `runtime/src/lib.rs`.

## 2. Every change beyond the merges

Eight commits, ten files, +163/−18 (`git diff --stat badd915 811317b`). Each is the minimum I found for the union to be
correct; none loosens a schema, check or test, and none re-introduces a default role or an unauthenticated answer path.

| Commit | Files | Kind | Change and reason |
|---|---|---|---|
| `963e715` | `runtime/src/verification/mod.rs` | compile reconciliation | WS-2 made `FamilyCtx.db` an `Option<&RuntimeDb>` (so the family binds `&&RuntimeDb`); WS-4 made `context::compile` take `impl Into<IndexHandle>` (implemented for `&RuntimeDb`). `compile(p, *db, …)` — one dereference, no behaviour change. The union did not build without it. |
| `38811b8` | `cli/src/main.rs` (`g0_label`), `runtime/src/orchestration/control.rs` (`COMMAND_GUARDS`), `framework/policies/AUTHORITY_POLICY.yaml` | guard registration | §3. Every subcommand other workstreams added is classified; `verify product` is reclassified because WS-2 made it write governed evidence; `record_skill_binding: L3` is declared (the level `skills::record` already applied as the default for an undeclared class). |
| `6de7214` | `runtime/src/adopt.rs` | semantic reconciliation | §4.1 (MPLAN `consumers`). |
| `b683f77` | `runtime/src/context/mod.rs` | semantic reconciliation | §4.2 (`semantic_candidates`). |
| `488a735` | `runtime/src/migrations/refs.rs` | semantic reconciliation (found during integration) | §4.6a: the migration's reference re-pointing rewrote WS-3-sealed gate records, breaking their T2 binding. Sealed records are now never rewritten. |
| `875aac1` | `tests/certification/ws08.rs`, `tests/certification/migration.rs` | builder-test update | §4.3: WS-8's and WS-9's new tests answered gates with `gov decide --by owner`; they now answer through WS-3's owner-signed channel helper. |
| `2cafbdc` | `cli/src/main.rs` | formatting | rustfmt of the file: the only difference was the layout of WS-4's additive single-line `ContextCmd` variants. Whitespace only. |
| `811317b` | `runtime/src/verification/currency.rs` | R1 preservation (found during integration) | §4.6b: WS-2's currency key composed the trust-anchor path by hand, failing AR-0031 `hx_a::a4` on WS-2's branch alone. It now reads the anchor through `srr::verifier::trusted_root`. No SRR file changed. |

No file under `runtime/src/srr/**`, `kernel_trust.rs`, `kernel.rs`, `lock.rs`, `init.rs`, `update.rs`, `release.rs`,
`recovery.rs`, `records.rs` or `tools.rs`/`capabilities/**` was changed by the integration. Nothing under
`release/verification/`, `release/root-of-trust/`, `release/releases/`, `release/orchestration/phase-1/`,
`release/capability-baseline/audit-0/` or another workstream's `repair-1/` directory changed, and
`Governance_OS_Capability_Acceptance_Contract_v3.md` is byte-identical (`4c2df291…5ed3`).

## 3. G0 registration (handoff step 3)

WS-3 refuses any unclassified command (`G0_UNCLASSIFIED`). Merged as-is, `g0_label` also did not compile (non-exhaustive
over `Cmd::Artefact`/`Health`/`Oracle`). More importantly, WS-3's `Cmd::Context { .. } => "context compile"` mapped WS-4's
four new `context` subcommands onto the `compile_context` Write label, so FREEZE_WRITES would have refused reading a
manifest. The union's classification, now 146 labels (73 Write, 57 Read, 16 outside):

| Label(s) | Effect / authority class | Basis |
|---|---|---|
| `context manifest`, `context verify`, `context show`, `context receipt` | Read / `read` | resolution and verification against governed records and the packet history (`manifest::resolve_task`, `load_packet`, `verify_delivery`, `receipt::validate`; `receipt` is WS-4's documented dry run). None of them writes; the packet-history write belongs to `compile` only. Observed: no governed file and no runtime-dir file changes (`evidence/g0/new_labels_g0_probe.out`). |
| `artefact show`, `artefact check`, `artefact lineage` | Read / `read` | read records, VCS history and the index (as `memory graph`/`impact`, which WS-3 classed `read`) |
| `health run` | Write / `record_audit` | persists a governance-suite EVIDENCE audit record when it re-establishes currency — exactly what `audit` (Write, `record_audit`) does |
| `health run --no-persist` | Read / `read` | `RecordPolicy::Never`, as `audit --no-persist` |
| `health status`, `checks`, `history`, `show`, `guard`, `currency`, `skills` | Read / `read` | report and re-evaluate; they touch only derived, machine-local runtime state (cache, ledger, observation file), and scenario checks run in disposable sandboxes |
| `health product` | Write / `record_audit` | records a `scope: product-tests` EVIDENCE audit record (`verification::product::run` → `save_record`) |
| `health close-check` | Write / `record_audit` | runs the G2 tier through `audit_with` with the default record policy, which can persist a governance-suite record |
| `health skills --record` | Write / `record_skill_binding` (L3) | writes the tracked, OS-written `governance/generated/skill-bindings.json`; `skills::record` itself requires `record_skill_binding`. The class is now declared in `AUTHORITY_POLICY` at L3, the level `authority::required_level` already applied to it as an undeclared class; `ENFORCEMENT_MAP` covers it through `authority_levels_required.*`. |
| `oracle format`, `oracle validate` | outside (no project, no role) | WS-1/12's qualification tool reads verifier-custody documents and the format compiled into the binary; it opens no project and writes nothing — the same classification as `contract verify` |
| `verify product` (existing label, **reclassified** read → Write / `record_audit`) | | With WS-2 (BC-P2-43) `verify product` records a governed EVIDENCE audit record. Left as Read, G0 would have let it write governed state under FREEZE_WRITES and PAUSE; WS-3's own G0 matrix run on the integrated binary shows it now refused FROZEN/PAUSED (§7). |

`record_audit` is L0 by WS-3's policy (independent auditors record evidence). Under WS-3's design an undeclared
invocation carries L0, so it is treated exactly as for `audit`; `evidence/g0/new_labels_g0_probe.out` checks that parity.

Observed on the integrated binary (`evidence/g0/new_labels_g0_probe.py`, 9/9): under FREEZE_WRITES and PAUSE every new
Write label is refused (exit 4) and changes no governed file, and every new Read label runs and changes no governed file;
`health skills --record` is refused for an L0 role and for an undeclared invocation; `oracle format|validate` run with no
project and no role and write nothing. The certification test `ws03::every_cli_command_label_is_classified_by_g0` and the
unit tests `labels_are_unique_and_allow_lists_name_classified_writes` / `every_authority_class_exists_in_the_kernel_authority_policy`
pass.

A deliberate non-change: `memory query` stays Read. With WS-6 it may record a retrieval-miss failure record, but that write
goes through `control::guard_write` itself and is reported `not_recorded` (the query still answers) under FREEZE_WRITES
(WS-6 supplementary S3-frozen, 19/19 integrated). Classifying the query Write would refuse inspection under a freeze.

## 4. Semantic conflicts (handoff step 4)

### 4.1 `MPLAN-GOVERNANCE-ADOPTION.consumers` (WS-9 × WS-4) — reconciled (`6de7214`)

WS-4's `record.schema.json` makes `consumers` a relation field of record ids (`<id> CONSUMES <record>`), and
`graph::lineage::unconsumed_outputs` / `graph::identity` read it as such. WS-9 wrote the plan's W1 "expected consumers" there
as `{stage, role, artefact}` objects, so A11's `schema_invariants` raised three HIGH findings and adoption failed
(certification `brownfield_adoption_end_to_end`, 95/5 after the merges). The consumers are stage artefacts (evidence files),
not records, so they cannot be relation ids without creating dangling edges. The plan now declares them under the non-relation
key `expected_consumers` (the W1 attribute; zeta-r `W1-b9-migplan-consumers` accepts either name and passes). The schema and the
relation semantics are unchanged. BC-P2-21 still holds on both sides: WS-4's edge direction, and WS-9's plan identity (zeta-r
W01b 9/9 integrated; WS-9 builder S7 lines pass).

### 4.2 `semantic_candidates` (WS-4 packet × `CONTEXT_POLICY.retrieved_fields`) — reconciled (`b683f77`)

The packet's `retrieved_intelligence` block never carried `semantic_candidates`; the base lacked it too (A0-C9-02). Yet
`CONTEXT_POLICY.retrieved_fields` requires it, and framework §15.2 lists "semantic candidates" in the retrieved-intelligence
block, so dropping it from the policy would have weakened the policy against its normative source. The packet now carries
it: the admitted candidates the semantic route contributed, as references into `ranked_evidence` (same order, no content
repeated). It is present and empty when retrieval degrades, and it is the first slice dropped under `max_packet_chars`.
The policy is unchanged and the supplementary block is intact. `context_reproducibility` no longer reports it, and beta-r
`C9-b3-policy-fields` goes FAIL→PASS.

### 4.3 WS-3's role and human-answer changes in other workstreams' tests — updated (`875aac1`)

After the merges, three builder tests failed only because they relayed human answers with `gov decide … --by owner`:
`migration::adoption_dependency_proof_citations_and_rerun_identity` (WS-9) and two `ws08` tests. They now use
`crate::ws03::human_decide`, which renders the package, has the owner sign it and relays the document. The two WS-8 tests run
on an SRR-provisioned machine, where WS-3's channel is the root's `human-gate` delegation (standalone anchors are refused
there), so they provision a root that also delegates `human-gate` to the test owner key. The declared roles were already
explicit (`orchestrator`, `migration-executor`); no default role and no unauthenticated path were introduced, and no
assertion changed.

### 4.4 `framework/health` and the kernel payload — not registered (not needed)

The installed kernel does not carry `health/` (KERNEL.yaml `payload_dirs` is unchanged). The union does not need it for
installed projects: `skills::kernel_scenario_checks` falls back to the copy compiled into the runtime. Statement-hash binding
keeps a different kernel's scenarios from being checked against the wrong expectation. Measured (`evidence/g0/new_labels_g0_probe.out`
K1): in an installed project `KERNEL_MANIFEST.json` lists no `health/` file, `gov kernel verify` is ok, and `gov health
skills` executes the five executable kernel scenarios, 5 passed / 0 failed. No kernel payload changed, so kernel-manifest,
lock and `gov kernel verify` stay consistent. The only kernel-payload file the integration touched is `AUTHORITY_POLICY.yaml`
(§3). Registration remains IP-WS02-16 for the release/kernel owner (cross-version: a newer binary against an older kernel).

### 4.5 `kernel::embedded_kernel_dir` race — not tripped (`evidence/concurrency/`)

The root-cause fix is round 2 (WS-8). `evidence/concurrency/cold_cache_scheduler.py` runs isolated machines (private HOME,
XDG_STATE_HOME, XDG_CACHE_HOME; no GOV_*; embedded payload) in four scenarios: unprovisioned or provisioned (throw-away
test-material root), each with a trusted or an untrusted installed kernel. Each scenario runs 5 trials against a new empty
cache. A trial is 4 concurrent processes: 3 × `gov health run --no-cache --no-persist` (worker pools, sandboxed checks) and
1 × `gov doctor` (threaded groups). **17/17 checks pass.** In the untrusted scenarios the cache was materialised during
the concurrent runs in 5/5 trials each. Every cache entry was byte-identical to the embedded payload (127 files), with no
staging leftovers, and a later embedded `gov init` from that cache succeeded and its kernel verified. With a trusted kernel
nothing materialises, sandboxed copies included.

### 4.6 Found during integration (not in the handoff)

**a. T2 seal × migration reference re-pointing (WS-3 × WS-9) — reconciled (`488a735`).**
- **What happened.** In the union, A6 raises dependency-proof gates (WS-9) that WS-3 seals at creation. A later batch moved
  a dependant (`docs/architecture.md`), and `refs::update_references_in` rewrote every text file naming it, including the
  sealed gate's question. The binding broke, and `gov gate present` refused the gate (`T2_UNBOUND`, BROKEN), failing
  certification `path_migration_with_rollback_and_memory_rebuild`.
- **The rule now.** Any record carrying `t2::SEAL_FIELD` (a gate, a decision derived from its answer, future sealed state) is
  never rewritten by the migration's re-pointing. Its path mentions are what the OS recorded at the time; WS-9's own
  dependency proof already treats such records as history (`references::EVENT_RECORD_TYPES`). No seal is relaxed. The
  gate's `dependants_digest`, not its question text, is what WS-9's `proof_covered_by` matches.

**b. AR-0031 `hx_a::a4` (WS-2 alone; R1 preservation) — repaired (`811317b`).**
- **The failure.** The first integrated R1 run gave AR-0031 26/8: `a4_the_trust_anchor_sink_refuses_and_is_the_only_writer`
  failed with "the trust anchor path is composed by hand outside `state.rs`: [runtime/src/verification/currency.rs]".
  `currency::machine_trust_state` read `root.join("trust").join("root.json")`.
- **Attribution.** It reproduces on WS-2's branch alone: a byte-identical `hx_a_census.rs` run against a read-only
  `git archive` export of `37bfcd1` also fails `a4` (`evidence/r1-heldout/attribution-ws02-branch-alone.hx_a_census.out`).
- **Why WS-2 did not see it.** WS-2's recorded R1 run did not measure WS-2's tree. Its AR-0033 `hv_a` output walks "86
  files, 811 functions", which is WS-6's tree; WS-2's has 91 files. The builders' runners linked the same
  `…/scratchpad/r1/wt/srr1-r1-verify*` paths, so concurrent runs could re-point one another's symlinks.
- **The repair.** The currency key now takes the anchor digest from `srr::verifier::trusted_root` on a read-only
  `MachineState`: the same file digest for a verifying anchor, the refusal code otherwise. The provisioning latch and
  break-glass marking are unchanged. The trusted-root reader is what WS-3's `human_channel.rs` already calls from outside
  `srr/`. AR-0031 is back to 27/7 and `section6.rs` stays green. WS-2's own supplementary probe stays 42/42 (including
  `S-I.1` and the `machine_trust` staleness lines).

## 5. Regression (handoff step 5) — at `811317b`

| Suite | Result | Expected |
|---|---|---|
| `cargo test --lib` | **146 passed, 0 failed** | base 42 + WS-1/12 21 + WS-2 14 + WS-3 11 + WS-4 15 + WS-5 13 + WS-6 11 + WS-8 10 + WS-9/11 9 = 146 |
| `cargo test --test certification` | **100 passed, 0 failed** (191 s; includes `section6::*`, `srr::*`, `ws03::*`, `ws08::*`) | 79 + WS-3 12 + WS-8 7 + WS-9/11 2 = 100. Straight after the merges (`38811b8`): 95/5 (`evidence/regression/cargo-test-certification.after-merges-38811b8.out`) |
| Python plugin tests (`capabilities/tests`) | **4 passed** | 4 |
| `rustfmt --check` (edition 2021) on every file touched beyond the merges | 0 hunks in each | — |
| `cargo build` warnings | none | — |

`CARGO_BUILD_JOBS=4` throughout. Evidence: `evidence/regression/`.

## 6. R1 held-out suites, unedited (handoff step 5)

Run per `release/verification/4.1.6-r1-4/evidence/REPRODUCTION.md` §3-§6 by `evidence/r1-heldout/run-r1-heldout.sh`. Each
suite is copied byte-identically (`cmp` lines in the output) with its dependency satisfied by symlink to this worktree. Each
test binary runs single-threaded with the nine refused-authority variables and `GOV_MACHINE_STATE_DIR` stripped, and
AR-0033 is given the candidate `gov` and the candidate-3 base export.

| Suite | Recorded baseline | Integrated `811317b` |
|---|---|---|
| AR-0027 (`4.1.6-r1`) | 26 / 3 (`b1`, `b2`, `d3`) | **26 / 3**, same tests |
| AR-0029 (`4.1.6-r1-2`) | 26 / 2 (`b3`, `b6`); `ho_f_preservation` does not compile | **26 / 2**, same tests; `ho_f` does not compile (same error) |
| AR-0031 (`4.1.6-r1-3`) | 27 / 7 (`a1`, `a5`, `a8`, `b6`, `c2`, `c3`, `d2`) | **27 / 7**, same tests (at `2cafbdc` it was 26/8 with `a4`: §4.6b) |
| AR-0033 (`4.1.6-r1-4`) | 31 / 0 | **30 / 1**: `hv_a_derivation::a1` only — its pins (84 files / 740 functions) against 105 / 1457 |

**AR-0033 `hv_a::a1`, handled as the handoff says:**
- The derived copy `evidence/r1-heldout/hv_a_derivation.a1-unpinned.P2-AR-0022.rs.txt` changes nothing but the two size
  assertions (a `diff` in the output shows exactly those two lines). It runs from a separate scratch crate, and the held-out
  suite is never edited.
- It measures 105 files / 1457 functions, **0 violations in every §6 activity**: human_gate_create 43 derived / 38 writers /
  1 exempt; human_gate_approve 1/1; release_certification 1/1; trust_policy_mutation 8/1; privileged_plugin_acquisition 10/2;
  floor_lower_or_reset 3/1; present_below_floor_release_as_current 1/1.
- AR-0033's own `derive.py` (ROOT line only substituted) agrees under all three splitter configurations, with 0 violations.
- Outputs: `evidence/r1-heldout/r1-heldout-integrated-final.out` (final) and `r1-heldout-integrated-2cafbdc.out` (before
  §4.6b).

## 7. Round-1 builders' own probes against the integrated binary (handoff step 6)

`evidence/builder-probes/run-builder-probe.sh` runs each builder's own probe unedited from its `repair-1/<ws>/evidence/`
directory against `target/release/gov`, writing only to `evidence/builder-probes/`. Every run sets PYTHONDONTWRITEBYTECODE,
and WS-1/12's `oracle-format-checks.py`, which writes beside itself, runs as a `cmp`-verified copy from a scratch mirror.
`compare_builder_probes.py` → `COMPARE-builder-probes.out` pairs every verdict line with the builder's recorded after-run.

| Builder | Probe | Recorded (builder branch) | Integrated, unedited | Explained runs |
|---|---|---|---|---|
| WS-1/12 | `mutation-controls.py` | 20/20 | **20/20** | — |
| WS-1/12 | `oracle-format-checks.py` | 78/78 (71 distinct ids) | **78/78** | — |
| WS-1/12 | `probe-encoding-check.py` | — | output **identical** | — |
| WS-2 | `WS02-supplementary.py` | 42/42 | **42/42** | — |
| WS-3 | `ws03_named_checks.py` | 37/37 | **37/37** | — |
| WS-3 | `O5-G0-guard-matrix.derived.py` | matrix | identical except `verify product`: now FROZEN / PAUSED under the emergency controls (the §3 reclassification; before it, the union would have mutated there) | — |
| WS-4 | `ws04-scenarios.py` | 37/37 | **37/37** | — |
| WS-5 | `ws05_supplementary.py` | 22/22 | **22/22** | — |
| WS-6 | `SUPP-ws06-behaviours.py` | 19/19 | **19/19** | — |
| WS-8 | `WS08-P1..P4` | 45/45 | 7 PASS→FAIL, 36 not reached (setup refused for the undeclared role; P1, P3 and P4 stop early) | role shim (WS-3's `gov-role-shim.sh`): P2 8/8, P3 11/11, P4 4/11, P1 crash. **Derived owner-channel copies of P1/P4 + role shim: 45/45** |
| WS-9/11 | `B-ws0911-regression-probes.py` | 27/27 | 22/27 | **Derived owner-channel copy: 27/27** |

**Integration regressions: none.** Every line that passed on a builder's branch and fails integrated fails only on a path
WS-3 removed by design, and passes once the probe uses the legitimate path:
- **WS-8 P1** raises its fixture gate with a partial package (BC-P2-49 → `GATE_PACKAGE_INCOMPLETE`, then `gid=None`).
- **WS-8 P1-P4** declare no role (BC-P2-08 → L0).
- **WS-8 P4** answers gates with `decide --by product-owner`, and **WS-9/11** with `--role human --by owner`
  (BC-P2-10 → refused).

The derived copies are clearly labelled and change only those paths:
- `evidence/builder-probes/derived-ws08/` (header comments list each change): a root that also delegates `human-gate`; an
  owner-signed `gate_approve` (with a standalone anchor on an unprovisioned machine); complete packages for P1's three
  fixture gates; a relocation of the library path.
- `evidence/derived-B-ws0911-regression-probes.owner-channel.P2-AR-0022.py.txt`: `answer_all` only.

While deriving P4, the `update --apply --approve` path was observed without an answered gate. It correctly returned
`applied: false` ("--approve is not a substitute for an answered gate record", INV-008), and the lock was unchanged.

## 8. Audit-of-record probes the builders cited, re-run on the integrated binary

Beyond step 6, I re-ran the audit-of-record probe sets each builder cited as after-evidence to look for cross-workstream
interactions (`evidence/audit-probes/`). That is 152 probe runs over all six families plus synthesis: 86 through the
adapter, 49 unedited through my runner, 16 unedited through WS-4's own runner, and 1 raw-SQL variant. `integrated/` holds unedited
runs. `shim/` routes the same unedited probe files through `gov-owner-channel-shim.py`, reached via a scratch mirror root.
That evidence adapter changes only three things:
- it declares `--role orchestrator` where the probe declared no role (stage role flags count as a declaration);
- it turns a relayed human `decide` for a gate the OS has already rendered into an owner-signed answer (it never presents a
  gate itself);
- it fills absent gate-package fields.

`compare_audit_probes.py` compares the marked families (zeta-r `OBS`, beta-r `[PASS]`, delta-r `CHECK`, synthesis `X`) with
each builder's recorded after-run; `normdiff.py` gives a normalised diff for the unmarked ones (38 diffs in `normdiff/`),
each of which I reviewed.

- **Marked families (adapter runs): 4 PASS→FAIL, 24 FAIL→PASS.** The 24 FAIL→PASS are repairs landing in the union (e.g.
  WS-2 FR currency, WS-9 W01b, WS-5 W5-c2, `C9-b3-policy-fields` from §4.2). The four PASS→FAIL:
  - `L3.b3.1` (WS-5's recorded delta-r run): `gate present` alone no longer marks `presented_in_chat` (BC-P2-10:
    rendering is not presentation), so the CIT is refused `GATE_NOT_PRESENTED` instead of `GATE_NOT_ANSWERED`. It is still
    refused.
  - `L3.b4.s1` (same run): the probe hand-edits a sealed answer; T2 refuses it `T2_UNBOUND` before any staleness check.
    WS-3 recorded this stricter refusal for `repair2.rs`.
  - `F.impl.1` (WS-2's delta-r FRESH run): an adapter artefact. The probe copies and modifies the `gov` it was given, which
    here is the adapter's wrapper, not the binary. WS-2's own `S-I.1` (a modified binary stales the green record) passes on
    the integrated binary.
  - `C9-b4` (WS-6's beta-r run): the probe sets `max_packet_chars` to the deterministic block + 2500. In the union, WS-4's
    mandatory `input_manifest` and `receipt_contract` blocks exceed that. The packet still drops 25 supplementary slices
    first, keeps every mandatory input and warns explicitly; zeta-r `W4-b3-*` (supplementary dropped first, mandatory never
    displaced, over-budget explicit) all pass integrated. The fixture budget, not the property, changed (Observation O-3).
- **Unmarked families.** Every difference is one of:
  - an intended repair: WS-3 role, answer, package and T2 refusals; WS-5 designated role and claim scope; WS-2 skill
    regression and currency; WS-4 packet shape and the 20-field deterministic list, which makes an old 14-field override a
    refused weakening; WS-9/11's export content gate now blocking a verbatim copy;
  - additive output fields, race order or timing noise;
  - an adapter limit: on an SRR-provisioned probe machine whose root delegates no `human-gate`, no human answer can be
    produced, so alpha-r A2-02 updates stop at their gate (`applied: false`, nothing unsigned applied). The adapter also
    necessarily turns `--role human` relays into owner-signed answers, so lines that test what a role claim can do (e.g.
    gamma-r `E1.b3.c`) are measured by the unedited runs and WS-3's named checks, not by the adapter runs;
  - one of the observations in §9.

  WS-9's cited S4 outcome holds (A6 complete; A7 `MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD`, 40 pass / 0 fail; A8 and A11 run,
  in both the raw-SQL and prepared variants). WS-5's designated-role and claim lines match (gamma-r E1 `E1.b4.b`, E4, I1I2,
  I4, F2F3).

No audit-probe line showed a defect caused by combining two repairs. The one such defect (§4.6a) was found by the
certification suite and fixed before these runs.

## 9. Observations for routing (not integration regressions; nothing changed for them)

| Id | What | Attribution | Evidence |
|---|---|---|---|
| O-1 | A project whose installed kernel predates WS-3's POLICY_PRECEDENCE rules (the shipped `release/releases/4.1.4` and `4.1.5`) has its descriptive `PROJECT_POLICY` keys (`project.name/alias/created/onboarding_mode`) and `MODEL_ROUTING_OVERRIDES` keys (`schema_version`, `providers`, `preferences.*`) refused ("not declared overridable … deny by default"). D027 then goes CRITICAL and doctor reports UNHEALTHY, and an update 4.1.4 → shipped 4.1.5 is applied, then rolled back by its post-install verification (alpha-r `S5-update` [U2]; WS-8's branch applied it). | **WS-3 alone** (BC-P2-45 overlay evaluation against an older kernel's precedence file). Reproduced identically with a scratch build of `phase2/repair-1-ws03`. | `evidence/observations/old_kernel_overlay_precedence.{py,out}` |
| O-2 | Doctor D019 counts gates that were rendered (`gate present`) but not acknowledged by an owner-signed receipt or answer as "exist only in files (INV-008)". epsilon-r `U` baseline doctor moves HEALTHY → DEGRADED. The wording predates WS-3's distinction between rendering and presentation. | WS-3 semantics × doctor D019 (WS-2's file) | `evidence/audit-probes/normdiff/ws02.epsilon-r.U-slos-and-healthy.diff` |
| O-3 | beta-r `C9-b4`'s fixture budget (deterministic block + 2500) is below WS-4's mandatory packet blocks; the budget property holds (§8). | WS-4 packet shape × probe fixture | `evidence/audit-probes/integrated/beta-r.C9-context-packet.out` |
| O-4 | beta-r `D6-rebuild-guarantee` rebuilds derived state while FREEZE_WRITES is active; G0 refuses `rebuild-memory` (a Write outside the allow-list), so the probe stops. Whether derived-state rebuild should be a recovery allow-list entry is WS-3's to judge. | WS-3 G0 | `evidence/audit-probes/shim/beta-r.D6-rebuild-guarantee.out` |
| O-5 | WS-2's recorded R1 held-out run measured WS-6's tree (§4.6b). The builders shared the `…/scratchpad/r1/wt/` symlink paths, so an R1 figure from a round-1 builder is only as good as its runner's isolation. For verifiers: use a private scratch path per run. | process | `evidence/r1-heldout/attribution-ws02-branch-alone.hx_a_census.out` |
| O-6 | `runtime/src/skills.rs` still says `record_skill_binding` is "not yet declared in AUTHORITY_POLICY"; it is now declared at L3 (§3). The comment was left for WS-2 (not an integration need). | WS-2 comment | — |
| O-7 | Integration points still open (not wired: beyond "make the union build and its tests pass"). Among them: WS-3 IP-1/IP-2 (task close and DAG), IP-5 (suite reports `t2::audit`); WS-4 IP-1..IP-17 (including `INDEX_VERSION`); WS-2 IP-WS02-01..22 (host call sites); WS-8 IP-1..IP-5; WS-6 IP-1..IP-8; WS-9 IP-1..IP-6; WS-1/12 IP-1..IP-7; WS-5 IP-1..IP-9. | round 2 | the builders' reports |
| O-8 | P2-ADJ-0001 (standalone human-gate anchor default `false`) is routed to round 2 and was not applied. The integrated default is still WS-3's `true`, which is what the certification helpers and the adapter use on unprovisioned test machines. | round 2 (WS-3) | — |

## 10. Contradictions and stopped items

None. No two repairs required contradictory behaviour. Every conflict found (§4.1, §4.2, §4.6a) had a resolution that
keeps both sides' requirements. §4.6b is a single repair's R1 regression, repaired without touching an SRR file.

## 11. What I did not do

- I started no round-2 class and wired no integration point beyond what the union needed to build and pass.
- I edited no builder's claims or repair report. The builders' run reports arrived with the merges.
- I did not register `framework/health` in the kernel payload (§4.4) or change the human-channel default (O-8).
- I changed no probe, held-out suite or audit-of-record file. Derived copies and adapters live only under `evidence/` and
  are labelled.
- I did not rebase, tag or push, and touched no other branch or worktree. Other branches were read with `git show` /
  `git archive` into scratch.

## 12. Evidence index (`evidence/`)

| Path | Content |
|---|---|
| `merge-and-change-log.out` | merge commits and parents, merged tips, conflict resolutions (`git show --cc`), every integration commit's stat |
| `regression/` | final `cargo test --lib` (146/0), `--test certification` (100/0), Python plugin tests (4/4), rustfmt check, build warnings; the post-merge certification run (95/5) |
| `r1-heldout/` | `run-r1-heldout.sh`; `r1-heldout-integrated-final.out` (at `811317b`), `r1-heldout-integrated-2cafbdc.out` (before §4.6b); the a1-unpinned derived copy; WS-2 attribution run |
| `g0/` | `new_labels_g0_probe.{py,out}` — G0 registration and the `framework/health` check (9/9) |
| `concurrency/` | `cold_cache_scheduler.{py,out}` — cold-cache concurrency (17/17) |
| `builder-probes/` | `run-builder-probe.sh`, every builder probe's integrated (and role-shim) output, `derived-ws08/`, derived WS-9 output, `compare_builder_probes.py`, `COMPARE-builder-probes.out` |
| `derived-B-ws0911-regression-probes.owner-channel.P2-AR-0022.py.txt` | WS-9/11 probe with `answer_all` through the owner channel (kept at this depth so its worktree resolution is unchanged) |
| `audit-probes/` | `run-audit-probe.sh`, `gov-owner-channel-shim.py`, `integrated/`, `shim/`, `shim-raw-sql/`, `ws04-zeta/` (WS-4's runner), `compare_audit_probes.py`, `COMPARE-audit-probes.out`, `normdiff.py`, `normdiff/` |
| `observations/` | O-1 reproduction script and output (integrated binary and WS-3 branch alone) |

Outputs contain absolute scratch paths of this run. Scripts take `P2AR0022_SCRATCH` (and `GOV` where applicable) and write
only under this directory or the scratch directory.

## 13. Process disclosures

- Model Claude Opus 5 (1M context), `claude-opus-5[1m]`. No sub-agents; the product owner was not contacted; no session or
  agent transcripts, task-output stores or user auto-memory were read. Long commands ran in the foreground.
- Two shell commands that included `rm -rf` of scratch paths were denied by the permission system. They were not retried
  as written; the same steps were redone without deleting anything, in fresh scratch directories.
- The integration's own adapters had three defects, each found by reviewing their outputs, fixed and re-run before any
  result was taken. The owner-channel adapter first rendered gates itself, masking delta-r `L3.b1.*`; it then ignored
  adopt-stage role flags, causing `ROLE_CONFLICT`. The derived WS-8 `gate_approve` at first lacked an anchor on
  unprovisioned machines. `COMPARE-*` and the adapter outputs are from the corrected versions.
