# P2-AR-0053: continuation of P2-AR-0043 (repair iteration 1, round 4, residual integration points)

| Field | Value |
|---|---|
| Run | P2-AR-0053, role `capability-repair`. Model: Claude Opus 5 (1M context), `claude-opus-5[1m]`. Fresh context |
| Handoff | P2-HO-0048 (continuation), through it P2-HO-0042; rules from P2-HO-0031, P2-HO-0020, P2-HO-0010 |
| Continues | **P2-AR-0043**, terminated mid-run by a weekly model usage limit. Its work is in my base and is not redone |
| Branch / base | `phase2/repair-1-r4-residual-b`, from `55af199` (P2-AR-0043's tip: its five product commits, its report and its evidence) |
| Work commit | `ab0a075` (R4-O1), then the commit that adds this report, `claims.yaml` and my evidence (no product file) |
| Product identity | at `ab0a075`: `product_code_digest dcf4c59101a9442ccf56e3c6c02c760b0225c54cb5fd6725a31dc3ad36ab0a13`, `governed_state_digest c88c0bf1…5f70`. Base `34e3725`/`55af199`: `1eb1564c…9a87` |
| Verdict | **`OWNER_DECISION_REQUIRED`**, for item 1 (R4-O1) alone and for one precise question (§2.5). Items 2, 3 and 4 are delivered; everything P2-HO-0042 routed is claimed in `claims.yaml` |

This is builder evidence (Contract v3 O3). Nothing in it is an acceptance, and I grade no one's work, P2-AR-0043's or my
own included. Where a status comes from P2-AR-0043's report I say so and do not restate its evidence as mine.

---

## 1. What I verified of the recovered work

**I re-ran every suite myself, on my own final tree, at `ab0a075`.** P2-AR-0043's recorded runs were made at `34e3725`,
before my change; they are not carried forward. My numbers are below and my raw outputs are in
`evidence/regression-0053/` and `evidence/r1-heldout-0053/` (P2-AR-0043's own directories, `evidence/regression/` and
`evidence/r1-heldout/`, are untouched).

| What | P2-AR-0043 at `34e3725` | **P2-AR-0053 at `ab0a075`** | Evidence (`evidence/…`) |
|---|---|---|---|
| `cargo build --release` | 0 warnings | **0 warnings** | `regression-0053/cargo-build-release.ab0a075.out` |
| debug build + every test target | 0 warnings | **0 warnings** | `regression-0053/warnings-check.ab0a075.out` |
| `cargo test --lib` | 265 / 0 | **266 passed / 0 failed** (+1 new) | `regression-0053/cargo-test-lib.ab0a075.out` |
| `cargo test --test certification` | 198 / 0 / 0 | **200 passed / 0 failed / 0 ignored** (+2 new) | `regression-0053/cert-c{1..9}.ab0a075.out`, `regression-0053/cargo-test-certification.SUMMARY.out` |
| Python plugin tests | 4 passed | **4 passed** | `regression-0053/python-plugin-tests.ab0a075.out` |
| rustfmt `--check`, each changed file | clean | **clean** | `regression-0053/rustfmt-check.ab0a075.out` |
| R1 held-out suites (all four, unedited, private path) | at baseline | **all four at baseline**; census 123 files / 2340 functions; 0 §6 violations | `r1-heldout-0053/r1-heldout-final-ab0a075.out` |

`CARGO_BUILD_JOBS=2` for every build. No `GOV_*` variable was set for any suite. The certification suite was chunked as
P2-AR-0043 chunked it (nine module chunks, each inside the tool's ten-minute limit); **every chunk ran at `ab0a075`
with a clean product tree**, and the union of the chunks equals the full test list (200 = 200, empty difference —
`cargo test --test certification -- --list` against the passed lines of the nine chunk outputs).

This is a stronger statement than "P2-AR-0043's runs reproduce": its product commits are in my tree, my change sits on
top of them, and the whole suite is green on the result. I did not re-derive its claims item by item; `claims.yaml`
attributes each of them to it, with the section of its report that records them.

### 1.1 R1 held-out suites at `ab0a075`

Run unedited through the private root `<worktree>/target/P2-AR-0053/r1-P2-AR-0053-private`; `wt/srr1-r1-verify{,-2,-3,-4}`
are symlinks to this worktree only; 26 `identical` `cmp` lines; the tree's own debug `gov`. The runner is a copy of
P2-AR-0043's, changed only in the run id (the diff of the two scripts after substituting the run id back is empty, and
the script's header says so).

| Suite | Baseline | This tree `ab0a075` | Failing tests |
|---|---|---|---|
| AR-0027 | 26/3 | **26/3** | `heldout_srr2` b1, b2; `heldout_srr3` d3 |
| AR-0029 | 26/2, `ho_f` does not compile | **26/2**, `ho_f_preservation` does not compile | `ho_b` b3, b6 |
| AR-0031 | 27/7 | **27/7** | `hx_a` a1, a5, a8; `hx_b` b6; `hx_c` c2, c3; `hx_d` d2 |
| AR-0033 | 30/1 | **30/1** | `hv_a` a1 only: the size pin (84 files / 740 functions) |

Every suite is exactly at its recorded baseline, failing test for failing test.

- **Census** (AR-0033 `hv_a::a1`'s own independent walk of this tree): **123 files, 2340 functions**. P2-AR-0043
  reported 123 / 2329 at `34e3725`; the eleven more are the installation's new helpers in `tools.rs`
  (`prepare_installation`, `installation_op`, `installation_proposal`, `installation_gate_package`, `install_write`,
  `apply_installation`, `registry_path`, `install_authority_roles`), `cit/mod.rs` (`host_op_of`,
  `propose_installation`) and `cit/materiality.rs` (`is_tool_installation_path`). The six generalised `cit` helpers
  are renames, not additions, and no file was added or removed (123 files, unchanged).
- **S1**, AR-0033's census with only its two size assertions printed instead of asserted, in the labelled copy
  `r1-heldout-0053/hv_a_derivation.a1-unpinned.P2-AR-0053.rs.txt` (byte-identical to P2-AR-0043's; its printed label
  still reads P2-AR-0032). It **passes**. Per activity (derived / writers / exempt / **violations**):
  human_gate_create 50/45/1/**0**; human_gate_approve 1/1/0/**0**; release_certification 1/1/0/**0**;
  trust_policy_mutation 8/1/0/**0**; **privileged_plugin_acquisition 11/2/0/0** (P2-AR-0043: 10/2/0/0 — the new match
  is `tools::install_write`, which is also the writer that replaces `tools::install` in the writer set, so the count
  of writers is unchanged and both still ask the sink); floor_lower_or_reset 4/1/0/**0**;
  present_below_floor_release_as_current 1/1/0/**0**.
- **S2**, AR-0033's own `derive.py` with only its ROOT line substituted: the same census (123 / 2340) and **0
  violations** in all three splitter configurations.
- **Normalised failure messages** of the unedited suites (P2-AR-0043's `failure_messages.py`, copied byte-identically,
  `cmp`-verified): 42 lines, **identical** to P2-AR-0043's run at `34e3725` (empty diff). See
  `r1-heldout-0053/failure-messages-vs-P2-AR-0043.txt`, which is transitively identical to the round-3 integration's,
  since P2-AR-0043 showed an empty diff against it.
- **R1-sensitive files touched.** No file under `runtime/src/srr/` changed (`git diff 55af199..ab0a075 --
  runtime/src/srr` is empty). `tools::install` keeps its operation-level guard and its unconditional
  `guard_acquisition_below_floor` call; the write moved into `tools::install_write`, which asks the sink at the
  instant of its write (§2.2 item 5) — the same shape P2-AR-0043 gave the registration writer. `guard_acquisition(`
  is still called only from `capabilities/governance.rs`, which is `hx_a::a6`'s sink-caller set.

---

## 2. Item 1 — R4-O1: does a task close treat a `gov tools install` write as it treated the plugin descriptor?

This is the check P2-AR-0043 was starting when it stopped, and it recorded it as R4-O1 in its §7.

### 2.1 The probe, and what it establishes

`evidence/r4-o1/tools_install_task_close.py` (mine; it imports WS-7's round-3 probe helper read-only for the project
harness, the owner-signed channel and the receipt shape). Three observations, each on a fresh project:

- **O1** an installation approved through its own tool-installation gate, made inside a claimed tooling task whose
  allowed paths include `governance/project/tools/**`, and the task then closed;
- **O2** the same with the descriptor's path **not** declared in the task's allowed paths;
- **O3** the control: the same installation with no task claimed.

**On the unchanged base** (`tools_install_task_close.base-55af199.out`, release `gov` `ebcf748d…`):

| | result |
|---|---|
| O1 | installed, one gate answered, **no change transaction at all** (`cit list: []`); close **refused `MATERIAL_CHANGE_REQUIRES_CIT`**, `refused: [{path: governance/project/tools/TOOL-R4O1.yaml, class: governance_change, rule: governance path}]` |
| O2 | installed; close refused `MUTATION_SCOPE_VIOLATION`, `undeclared: [governance/project/tools/TOOL-R4O1.yaml]`, "outside allowed_paths and not governed by a CIT executed while this task was claimed" |
| O3 | installed; nothing refuses it, because nothing closes |

So the answer is: **yes — exactly as INT3-O1, and refused rather than let through.** The write is attributed to the
worker and the close refuses it as a material change made outside change control, whatever the owner approved. It is
not an unattributed write that slips past: no path lets a `tools install` close.

**Census of the writers.** `governance/project/tools/<id>.yaml` has exactly one writer in the product — `tools::install`
(`runtime/src/tools.rs`, the only `p.overlay_dir().join("tools")` write; `runtime/build.rs` walks the repository
`tools/` directory, a different path). The tool registry it also rewrites is
`governance/generated/tool-registry.json`, which materiality excludes (`governance/generated/**`) and task close treats
as OS-managed. No other writer of these prefixes exists, so closing `tools::install` closes the class.

### 2.2 The mechanism (the same one INT3-O1 was closed with)

Contract v3 **K3** (impact simulation auto-triggers for material security and governance/policy changes) and **F4**
(elevated permissions reference an authoritative gate or decision; the descriptor cannot authorise itself). Both hold
for an installation, for the same reasons they hold for a registration, so the mechanism is extended, not copied:

1. **The registration helpers are generalised to host-proposed transactions.** `cit::HOST_PROPOSED_OPS`, `host_op_of`,
   `host_transactions`, `close_host_requests`, `note_host_gate`, `host_gate_state`, `execute_host_op` now serve both
   `register_plugin` and the new `install_tool`. No behaviour of the registration path changes (its certification and
   `ws07` tests pass unchanged); only the names and one parameter do.
2. **`gov tools install` derives the request and proposes the transaction itself** (`tools::prepare_installation`,
   `cit::propose_installation`): `origin: system`, `system.kind: tool-installation`, one `install_tool` operation
   carrying the descriptor as given, the installation subject, the installing role and whether the install command
   runs; declared trigger `security_change`; derived materiality `governance_change` **and** `security_change`; radius
   R5 by `CHANGE_POLICY.radius_rules.governance_paths_radius`. CIT-P is simulated automatically (K3).
3. **The installation's own approval is unchanged** (BC-P2-41): when an auto-install condition fails, a Human Decision
   Gate raised for exactly the installation subject, now naming the transaction and its gate
   (`subject.change_transaction`), and the transaction journals the gate raised for its subject. **The two approvals
   name each other**, and neither answer stands in for the other.
4. **Only CIT-E writes the descriptor** (`tools::apply_installation`): it re-derives the request from the descriptor
   the transaction carries, requires exactly the approved subject (else `TOOL_INSTALLATION_STALE`), re-verifies the
   installation approval where a condition failed (else `TOOL_NOT_APPROVED`), and refuses an acting role that holds no
   installation authority (`AUTHORITY_DENIED`), so `gov cit execute` is not a way round
   `TOOL_PERMISSIONS.install_authority_roles`. CIT-E records per-path writes, so the close accepts the installation on
   them — including when `governance/project/tools/**` is not in the task's allowed paths.
5. **`tools::install_write` is the one writer.** It composes the tools directory itself and calls
   `srr::plugins::guard_acquisition_below_floor("tools install")` immediately before writing, so the derived §6 census
   (`breakglass::SECTION_6_SIGNATURES`, bullet 5) still finds every writer of a capability registry asking the sink —
   the regression P2-AR-0043 hit in its §1.4 and closed the same way for the registration writer. `tools::install`
   keeps its operation-level guard and its own unconditional sink call.
6. **`--execute` is part of what the approval binds.** The install command now runs *inside* the transaction, so a
   failing command rolls the change back; and a repeated request that flips the flag is told to repeat it as proposed
   or to `gov cit reject` the transaction, rather than borrowing an approval of different content.
7. **Materiality**: a tool installation descriptor is derived as a security change as well as a governance change
   (`cit::materiality::is_tool_installation_path`), for the reason a plugin registration is — the install command the
   OS runs, the permission classes the tool is acquired with and the roles it is exposed to (Contract v3 F4, BC-P2-41).

**After the change**, the same probe (`tools_install_task_close.wip-1.out`, release `gov` at the change):
O1 and O2 both **close DONE**; `CIT-0001` is COMMITTED, `origin: system`, kind `tool-installation`, effective triggers
`[governance_change, security_change]`, radius R5; the close's evidence lists the descriptor under `cit_covered`.

### 2.3 Tests

New (both in `tests/certification/r4_residual.rs`, plus one lib test):

| Test | What it proves |
|---|---|
| cert `r4_residual::a_tool_installed_inside_a_claimed_task_closes_on_its_os_proposed_change_transaction` | K3 (auto-proposed, simulated, both triggers, the acting role recorded) and F4 (separate installation gate) both hold; nothing written before both answers; CIT-E's writes cover the descriptor; the task closes DONE **with the tool path outside its allowed paths**; a repeat is `unchanged` and proposes nothing; a later hand edit inside another task is refused `MATERIAL_CHANGE_REQUIRES_CIT` |
| cert `r4_residual::an_installation_change_approved_without_its_installation_approval_writes_nothing` | F4 direction: CIT-E refuses `TOOL_NOT_APPROVED` and rolls back; a new transaction after the installation approval; `gov cit execute` by a role without installation authority is `AUTHORITY_DENIED` and rolls back |
| lib `cit::materiality::tests::a_tool_installation_descriptor_is_a_governance_and_a_security_change` | The derivation: governance **and** security, by the `tool installation` rule; the generated tool registry is not a governance change |

Changed (neither renamed, removed nor `#[ignore]`d; see §2.5 for the second one):

| Test | Change | Reason |
|---|---|---|
| cert `ws07::a_tool_installation_is_approved_only_for_that_installation` | Every request of the one installation gives `--execute` (it is part of what the approval binds); after the installation gate is answered the descriptor is asserted **still unwritten** until the change gate is answered too; then installed, with the descriptor recording both the gate and the transaction | R4-O1 (strengthened in the same way P2-AR-0043 strengthened the registration equivalent) |
| cert `ws07::a_governed_security_review_by_another_role_lets_the_installation_proceed` | "no gate is raised" becomes "no gate is raised **for the installation subject**"; the transaction's own gate is asserted to be the only one, and answering it installs with `approval.mode: autonomous` | R4-O1 — **and this change is the owner decision in §2.5** |

### 2.4 Availability rule (P2-HO-0031) and G0

- **Installation.** It now passes G0 through its transaction (`cit propose|approve|execute` with the installation's
  paths). A block refuses it only where its scope reaches, or globally for a critical block, exactly as for a
  registration (BC-P2-06). Refusals stay typed; FREEZE/PAUSE refuse it as before through the unchanged
  `guard_write(p, "tools install")`.
- **No new subcommand.** `gov tools install` keeps its `COMMAND_GUARDS` entry (`install_tool`, Write) and its `g0_label`;
  the internal write guards use the existing `cit propose|approve|execute` labels.
  `ws03::every_cli_command_label_is_classified_by_g0` passes.
- **No new finding** and no new hard block. No refusal a repair-delta class requires was reopened.

### 2.5 The owner decision this item returns

**The mechanism above conflicts with an accepted requirement, and no accepted source resolves the conflict.**

- Contract v3 **K3** and the product's own kernel-floor materiality make a tool installation a material governance and
  security change, so it completes through change control.
- The shipped `CHANGE_POLICY` lists `governance_change` in `human_gate_triggers` (and sets
  `governance_paths_radius: R5` against `auto_approve_max_radius: R1`), so **that transaction needs a human gate**.
- **IP-W7-1 / BC-P2-41**, confirmed by WS-7 in round 3, says a governed security review of the tool identity and
  version, by another author, satisfies `licence_and_security_satisfied` **"without the owner's gate"**, and its
  certification test asserts that such an installation completes with **"no gate raised"** at all.

All three cannot hold for the review-evidenced path. Something must give, and the choice is not mine:

- **(a) Accept the narrowing.** IP-W7-1 means no gate for the **installation subject**; the change transaction's gate
  stands, as it does for every other governance change, and the owner answers one gate where they previously answered
  none. This is what the branch implements, and it is the only reading under which K3 and IP-W7-1 can both be true.
  Its cost is one owner answer per review-evidenced installation — real, and visible in
  `ws07::a_governed_security_review_by_another_role_lets_the_installation_proceed`, whose assertion I changed.
- **(b) Keep IP-W7-1 literally.** Then the OS needs a rule no source states: either `CHANGE_POLICY` gains a
  pre-authorisation for this change class (an installation whose `auto_install_conditions` all held, the security one
  evidenced by a governed review, is auto-approvable), or tool descriptors stop being a material governance change.
  The first is a policy/kernel-floor change; the second contradicts the close's own rule that a material change
  completes only through change control whatever task it is made in.

I implemented (a) so that the owner can see the whole mechanism and its cost, and so that the rest of the round is
verifiable on a green tree. **If the owner chooses (b), the integrator drops `ab0a075` and R4-O1 returns to the routing
list with the policy question attached**; nothing else in this run depends on it. Two facts are worth having in front
of the decision:

- For an installation made **inside a claimed task** — the defect itself — the owner gate is *already* unavoidable
  today: the close tells the worker to propose a CIT for that path, and that CIT is a `governance_change` too. The
  change removes the hand-filing, not an approval.
- The only case that loses autonomy is a review-evidenced installation made **outside** any claimed task, which is
  exactly the case IP-W7-1's test measures.

I did not weaken `TOOL_POLICY` to sidestep this: narrowing `auto_install_conditions` through `policy_overrides` is
refused by the precedence rules, correctly.

---

## 3. Item 2 — `claims.yaml`

`release/capability-baseline/repair-1/r4-residual/claims.yaml` covers every item P2-HO-0042 routed — INT3-O1, INT3-O2,
the WS-3/4/6/7/8/9 integration points, WS-2's IP-R3-WS02-10, and the whole optional list — plus R4-O1. Each claim
carries `source: P2-AR-0043` or `source: P2-AR-0053` and points at the section of the report that records it.
Statuses for P2-AR-0043's items are derived from its report; its evidence is not restated as mine.

Summary: 24 claims — 16 `REPAIRED_CLAIMED`, 1 `CONFIRMED` (IP-R3-WS03-9, a probe-premise item), 2 optional `DONE`, 4 optional
`NOT_DONE` with reasons, 1 `OWNER_DECISION_REQUIRED` (R4-O1).

---

## 4. Files changed by this run (`55af199` → `ab0a075`)

**Runtime:** `tools.rs` (the installation: `prepare_installation`, `installation_op`, `installation_proposal`,
`installation_gate_package`, `install_write`, `apply_installation`, `install`), `cit/mod.rs` (the host-proposed
transaction helpers, `propose_installation`, the `install_tool` dispatch in `manifest_paths`, the dependents walk, the
snapshot's created paths and `apply_op`), `cit/materiality.rs` (`is_tool_installation_path` and the rule),
`capabilities/governance.rs` (calls the generalised helpers; `change_view` is `pub(crate)`).

**Framework:** `schemas/cit.schema.json` (op `install_tool` and its fields; `x-schema-version` 1.3.0),
`KERNEL.yaml` (`cit: 1.3.0`).

**Docs:** `docs/ARCHITECTURE.md`, `docs/COMMANDS.md`.

**Tests:** `tests/certification/r4_residual.rs` (two new tests and their helpers), `tests/certification/ws07.rs` (two
tests changed, §2.3).

**Not touched:** P2-AR-0042's round-4 files (`runtime/src/contracts.rs`, `framework/contracts/**`, the acceptance
schema, `tests/governance/capability-evidence-map.yaml`, `docs/generated/**`); `release/verification/`,
`release/root-of-trust/`, `release/releases/`, `release/orchestration/phase-1/`,
`release/capability-baseline/audit-0/`, other workstreams' `repair-1/` directories; Contract v3 and the frozen gate
contract (`4c2df291…`, `d2f33e89…`); P2-AR-0043's report and its evidence directories. See
`evidence/identity-and-scope-0053.out`.

Six non-test helpers in `cit/mod.rs` were renamed as part of the generalisation (listed at the end of
`identity-and-scope-0053.out`). No test referenced any of them, at the base or at final.

---

## 5. Remaining integration points for the round-4 integrator

Carried from P2-AR-0043's §7, unchanged unless noted:

| Id | For | What |
|---|---|---|
| R4-IP-1 | verifiers and probe authors | Any probe that registers an executable plugin by answering only the first gate must also answer `change_transaction.human_gate` (INT3-O1). **And now: any probe or test that installs a tool must answer the installation's change gate too** — including one that relies on a governed security review, which previously needed no answer at all. Labelled derived copies exist for WS-7's IP probe and named checks; my own R4-O1 probe answers whatever gates the installation returns |
| R4-IP-2 | WS-1 evidence map (P2-AR-0042 or its successor) | Owners for P2-AR-0043's twelve new tests (its §4 table). **Plus mine**: K3/F4/BC-P2-13 in-task and BC-P2-41 → the two `r4_residual` tool-installation tests; BC-P2-13 materiality → the new `cit::materiality` lib test |
| R4-O1 | **owner, then routing** | **Now claimed with an owner decision attached (§2.5).** The mechanism is on the branch at `ab0a075`; the decision is whether IP-W7-1's "no gate raised" narrows to "no gate for the installation subject" |
| R4-O2 | routing / verifier | `gov plugins unregister` still writes the sealed registry directly, not through a change transaction; it is the fail-safe direction and the registry is OS-managed and sealed, so a close accepts it. Whether K3 wants impact simulation for de-registration is not stated by the sources. **The same question now applies to a tool: nothing uninstalls one, so there is no matching path today** |
| R4-O3 | WS-8 (probe maintenance) | WS-8's `r1-invariants.sh` line "floors_path( outside state.rs = 1" stays at 1 (INT3-O3 not done) |
| R4-O4 | routing (new) | `install_tool` widens the CIT manifest vocabulary a second time (`cit` schema 1.3.0). A migration that carries the schema version to adopted projects is not part of this run; `M-4.1.5-4.1.6` already delivers the kernel manifest, and the op is additive (an older transaction never carries it), but an integrator should confirm the schema-version handling with WS-9 |

Also carried from integration-3 and not reopened: INT3-O4 and R3-WS5-11.

**Not done by P2-AR-0043, from its own report** (§5): INT3-O3, IP-R3-WS04-03, IP-R3-WS04-06, IP-R3-WS02-11 — each with
its reason, all four optional. Nothing P2-HO-0042 required is left undone.

---

## 6. Process disclosures

- Model: Claude Opus 5 (1M context), `claude-opus-5[1m]`. Fresh context. No sub-agents. The owner was not contacted.
  I read no session or agent transcript, no task-output store and no user auto-memory.
- I read P2-HO-0048 through `git show release/4.1.6-rc1:…` because it was committed after my base; I checked out,
  merged, rebased, tagged and pushed nothing, and touched no branch but my own.
- `rm` is denied in this environment and was not used. My scratch trees are under `target/P2-AR-0053/`.
- Long certification chunks that exceeded the tool's ten-minute foreground limit were moved to the background by the
  harness; their output went to the chunk files named in the summary, which I read. The task-output store was not read.
- P2-AR-0043's report, `evidence/regression/`, `evidence/r1-heldout/`, `evidence/int3-o1/` and
  `evidence/audit-probes/` are unchanged. My evidence is in `evidence/r4-o1/`, `evidence/regression-0053/`,
  `evidence/r1-heldout-0053/` and `evidence/identity-and-scope-0053.out`.
- The machine may have been shared with other work during the runs; timings are indicative only.
