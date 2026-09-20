# P2-AR-0055: OD-P2-03 — a tool installation needs the Human Gate only when it expands authority

| Field | Value |
|---|---|
| Run | P2-AR-0055, role `capability-repair`. Model: Claude Opus 5 (1M context), `claude-opus-5[1m]`. Fresh context |
| Handoff | P2-HO-0050, through it P2-HO-0048 and P2-HO-0042; rules from P2-HO-0031 (availability rule), P2-HO-0020, P2-HO-0010 |
| Specification | `release/orchestration/phase-2/GATES/OWNER-DECISION-P2-0003-TOOL-INSTALL-GATE.md` — owner decision **OD-P2-03**, "gate only elevated installs", answering owner gate HG-P2-0002. Its requirements 1–7 are the acceptance requirements |
| Continues | **P2-AR-0053**'s item R4-O1, which the owner has now decided. Its commit `ab0a075` implemented "always gate" and is superseded; its change-control machinery is kept |
| Branch / base | `phase2/repair-1-r4-residual-c`, from `d96c8ab` (P2-AR-0053's tip: P2-AR-0043's five product commits, P2-AR-0053's `ab0a075`, and both runs' reports and evidence) |
| Work commits | `55206af` (OD-P2-03), `6c42f34` (an approval binds the change-class verdict), `7da93a2` (two corrections to the envelope derivation), `4bd7468` (INV-005: the registry hostnames move to the kernel tool registry). Then the commit that adds this report, `claims.yaml` and `evidence/` (no product file) |
| Product identity | at `4bd7468`: `product_code_digest 2fbbbd6c995ab3aa57d0e03f93198535efd27f9612988dd229efe3a6dfab9d82`, `governed_state_digest 4bfc1ae8…e336`. Base `d96c8ab`: `dcf4c591…0a13` / `c88c0bf1…5f70`. Release `gov` sha256 `3f847ec2…fcc3` |
| Verdict | **`READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`**. Every requirement of OD-P2-03 is claimed. No further owner decision is needed (§9 states one question an integrator may wish to route, which the decision does not leave open) |

Everything here is builder evidence (Contract v3 O3). Nothing in it is an acceptance, and I grade no one's work — not
P2-AR-0043's, not P2-AR-0053's, not my own. The two earlier reports in this directory are untouched.

---

## 0. Regression and R1 (at the final product commit `4bd7468`)

| What | Result | Evidence (`evidence/…`) |
|---|---|---|
| `cargo build --release` | **0 warnings** | `regression-0055/cargo-build-release.4bd7468.out` |
| forced debug build of every test target + release build | **0 warnings** | `regression-0055/warnings-check.4bd7468.out` |
| `cargo test --lib` | **267 passed / 0 failed** (266 at the base; +1 new) | `regression-0055/cargo-test-lib.4bd7468.out` |
| `cargo test --test certification` | **203 passed / 0 failed / 0 ignored** (200 at the base; +3 new). Fourteen module chunks, all at `4bd7468` with a clean product tree (`dirty=0` in each chunk's own header); the union of the chunks equals the full test list (203 = 203, empty difference) | `regression-0055/cert-c{01..14}.out`, `regression-0055/cargo-test-certification.SUMMARY.out`, runner `regression-0055/cert-chunk.P2-AR-0055.sh` |
| Python plugin tests (`capabilities/tests`) | **4 passed** | `regression-0055/python-plugin-tests.4bd7468.out` |
| rustfmt (edition 2021) `--check`, each changed Rust file alone | **clean** (all five) | `regression-0055/rustfmt-check.4bd7468.out` |
| R1 held-out suites, all four, unedited, private path | every suite at its recorded baseline (below) | `r1-heldout-0055/r1-heldout-final-4bd7468.out`, runner `r1-heldout-0055/run-r1-heldout.P2-AR-0055.sh` |

`CARGO_BUILD_JOBS=2` for every build. No `GOV_*` variable was set for any suite.

**R1 held-out suites** — run unedited through the private root `<worktree>/target/P2-AR-0055/r1-P2-AR-0055-private`;
`wt/srr1-r1-verify{,-2,-3,-4}` are symlinks to this worktree only; 26 `identical` `cmp` lines; the tree's own
debug `gov`. The runner is a copy of P2-AR-0053's, changed only in the run id (substituting the run id back gives an
empty diff, shown in the command that produced it).

| Suite | Baseline | This tree `4bd7468` | Failing tests |
|---|---|---|---|
| AR-0027 | 26/3 | **26/3** | `heldout_srr2` b1, b2; `heldout_srr3` d3 |
| AR-0029 | 26/2, `ho_f` does not compile | **26/2**, `ho_f_preservation` does not compile | `ho_b` b3, b6 |
| AR-0031 | 27/7 | **27/7** | `hx_a` a1, a5, a8; `hx_b` b6; `hx_c` c2, c3; `hx_d` d2 |
| AR-0033 | 30/1 | **30/1** | `hv_a` a1 only: the size pin (84 files / 740 functions) |

Every suite is exactly at its recorded baseline, failing test for failing test.

- **Census** (AR-0033 `hv_a::a1`'s own independent walk of this tree): **123 files, 2356 functions**. P2-AR-0053
  measured 123 / 2340 at `ab0a075`; the sixteen more are this run's helpers in `tools.rs` (`envelope_list`,
  `network_allowlist`, `installation_commands`, `token_values`, `leaves_project`, `endpoint_host`,
  `matches_any_pattern`, `credential_names`, `finding`, `installation_authority`, `change_decision`,
  `installation_change_decision`, `authorised_by`), `cit/mod.rs` (`class_decision`, `class_pre_authorised`) and
  `cit/binding.rs` (`class_of`). No file was added or removed (123 files, unchanged).
- **S1**, AR-0033's census with only its two size assertions printed instead of asserted, in the labelled copy
  `r1-heldout-0055/hv_a_derivation.a1-unpinned.P2-AR-0055.rs.txt` (byte-identical to P2-AR-0053's and P2-AR-0043's;
  its printed label still reads P2-AR-0032, `cmp`-verified). It **passes**. Per activity
  (derived / writers / exempt / **violations**): human_gate_create 50/45/1/**0**; human_gate_approve 1/1/0/**0**;
  release_certification 1/1/0/**0**; trust_policy_mutation 8/1/0/**0**; **privileged_plugin_acquisition
  13/3/0/0**; floor_lower_or_reset 4/1/0/**0**; present_below_floor_release_as_current 1/1/0/**0**.
- **The acquisition activity's counts moved and its property did not.** P2-AR-0053 measured
  privileged_plugin_acquisition 11 derived / 2 writers; this tree gives 13 / 3 under `hv_a::a1`'s splitter and
  12 / 2 under S2's indentation splitter — the signature is `join("plugins") | join("tools") | guard_acquisition`,
  and `tools::network_allowlist` (which reads `tools/registry/TOOLS.yaml`) matches it, while the third "writer" is
  a function-boundary difference between the two splitters, not a new unguarded write. **Violations are 0 in every
  activity in every configuration**, and the product's own check of the same property —
  `section6::both_capability_acquisition_primitives_ask_section_6_without_consulting_the_descriptor`, which
  requires each derived capability-registry writer to call the sink and `tools install` to keep its operation-level
  guard — passes (chunk `cert-c05`).
- **S2**, AR-0033's own `derive.py` with only its ROOT line substituted: the same census (123 / 2356) and **0
  violations** in all three splitter configurations.
- **Normalised failure messages** of the unedited suites (P2-AR-0043's `failure_messages.py`, carried byte-identically
  through P2-AR-0053): 42 lines, **identical** to P2-AR-0053's run at `ab0a075` (empty diff), and so transitively
  identical to P2-AR-0043's and the round-3 integration's. See `r1-heldout-0055/failure-messages-vs-P2-AR-0053.txt`.
- **R1-sensitive files touched.** No file under `runtime/src/srr/` changed (`git diff d96c8ab..HEAD -- runtime/src/srr`
  is empty). `tools::install` keeps its operation-level `guard_write` and its unconditional
  `guard_acquisition_below_floor` call, and `tools::install_write` still asks the sink at the instant of its write
  (two calls in `tools.rs`, as before). `guard_acquisition(` is still called only from `capabilities/governance.rs`,
  which is `hx_a::a6`'s sink-caller set.

---

## 1. What the owner decided, and what this run did with it

**OD-P2-03.** A tool installation proceeds **without** a Human Gate when the tool is authenticated and pinned,
independently governed-reviewed, registered, reversible, and stays entirely inside the project's already-authorised
permission and trust envelope. A Human Gate **is required** when the installation **expands authority**: privilege
escalation; broader filesystem or project access; new secret or credential access; host-level authority; governance or
security-policy mutation; or a new or unrestricted network trust boundary. Ordinary network use already authorised by
project or tool policy does not by itself count as elevated. **Every** installation is recorded with its security and
CIT evidence, gated or not, and the recorded transaction states which branch applied and why.

R4-O1 (P2-AR-0053, `ab0a075`) had already made an installation a change transaction the OS proposes and simulates
(Contract v3 K3), which is what the decision assumes. What changed here is only **whether that transaction needs the
owner's gate**, and the answer is now governed data rather than the generic radius/trigger rules. Concretely:

1. the rule is in `CHANGE_POLICY.change_classes.tool_installation` with `TOOL_POLICY.installation_envelope`, and in
   the governed record `spec/decisions/D-0011.yaml` (§3);
2. the envelope is computed by `tools::installation_authority` from trusted OS state, never from the descriptor's
   declarations (§2);
3. everything that cannot be evaluated is an expansion and gates (§2.4);
4. `cit::simulate_inner` records the verdict in the transaction's **bound** impact and raises the transaction's gate
   only when it is required; `cit::approve_with` approves a pre-authorised transaction above
   `auto_approve_max_radius` only on that bound verdict; `tools::apply_installation` derives the verdict again at
   CIT-E (§4.3);
5. `ws07::a_governed_security_review_by_another_role_lets_the_installation_proceed` is back to asserting that **no
   gate is raised**, with its tool inside the envelope (§7).

**Requirement by requirement.**

| OD-P2-03 requirement | Where it is met |
|---|---|
| 1. An explicit governed rule in policy, with `TOOL_POLICY` supplying the envelope, plus a governed decision record, visible to `gov` policy inspection and to an auditor, never implicit in code | §3 |
| 2. The envelope computed from trusted OS state, never from the descriptor's declarations | §2 |
| 3. Fail closed and fail gated (envelope undeterminable, condition unevaluable, review missing/self-attested/unbound, pin unverifiable) | §2.4, §4.3 |
| 4. F4 still binds: elevated = the gated class; a non-elevated installation references this decision, the rule and the bound independent review in its recorded change transaction | §4.4 |
| 5. Recording unconditional; the transaction states which branch applied and why | §4.4 |
| 6. Round-3 behaviour restored for the non-elevated case; `ab0a075`'s machinery kept, its unconditional gating and its edit to that test dropped | §5, §7 |
| 7. Tests cover both branches, each trigger, and the allowlisted-network control | §7 |

---

## 2. How the envelope is computed, and from which trusted sources

`tools::installation_authority(p, descriptor, role, dest_rel, op)` answers one question: **would this installation
hold anything the project has not already authorised?** It returns the comparison, not a verdict about the tool.

### 2.1 The authorised side is trusted OS state only

`ENVELOPE_SOURCES` in `runtime/src/tools.rs` names them, and the same list is recorded in every verdict
(`authority_envelope.authorised_sources`) so an auditor reads it from the transaction rather than from the code:

- **`TOOL_PERMISSIONS.yaml` `roles.<acting role>`** — the permission classes the project has already authorised for
  the role that is installing. The acting role, never a caller-supplied one (D-0007 rule 2; `tools::install` already
  refuses `--role` naming another role).
- **`TOOL_PERMISSIONS.yaml` `install_authority_roles`** — who may install at all (re-checked at CIT-E).
- **`AUTHORITY_POLICY.authority_levels_required.install_tool`** — the authority class the operation runs under.
- **`REPOSITORY_CONTRACT.yaml`**, the path map (`p.contract().decide(path)`) — which paths may be mutated and how
  they are classified.
- **`DATA_SENSITIVITY.yaml` + `SECURITY_POLICY`** — sensitivity classes (`restricted`, `secret`) through the path
  map, and `secret_path_patterns`.
- **`TOOL_POLICY.installation_envelope`** — the host-authority, credential and network permission classes; the
  command-token floor for privilege and host authority; the credential-name patterns; the policy paths.
- **`tools/registry/TOOLS.yaml` `network_allowlist`** — the approved registries and allowlisted services. These are
  **ecosystem knowledge**, and `INV-005` (`arch::kernel_data_contains_no_language_or_toolchain_assumptions`) keeps
  kernel data under `framework/` free of language and toolchain assumptions, naming the tool registry as where such
  knowledge belongs; that is where the language-native tools already live. The registry is part of the verified
  kernel payload, so a project can no more alter it than the policy. (I put the hostnames in the policy first; the
  invariant's test caught it, and the placement — not the invariant — was what gave way. Commit `4bd7468`.)

Nothing a descriptor contains is ever added to this side. That is the whole point of Contract v3 F4 ("a descriptor
cannot authorise itself") and of BC-P2-39, whose defect was a *declaration* deciding whether approval was needed.

### 2.2 The demanded side is the request **plus** what the OS observes for itself

What the installation would hold is the union of

- what the descriptor asks for — `required_permission_classes`, `permissions.*`, `credential_scope` — which is a
  **request**: it can only ever *add* to the demand; and
- what the OS derives itself from the installation's own commands (`install_command`, `uninstall_command`,
  `health_check.command`): the program names, the flags, path tokens (including the value hidden in `--flag=value`),
  URL endpoints, and credential names given as `NAME=…`, `$NAME` or `${NAME}`.

So a descriptor that declares only `READ_REPO` and runs `sudo`, reaches `/opt`, passes `--token=$GITHUB_TOKEN`, edits
`framework/policies/SECURITY_POLICY.yaml`, names the plugin registry or fetches from an unlisted host expands
authority all the same. **Every** trigger variant in §4.2 is demonstrated exactly that way, on a descriptor that
declares nothing elevated at all.

**Stated plainly, because it matters for what this claim is worth:** the token and pattern lists are a **kernel
floor, not a safety proof**. The OS cannot confine a spawned process — `TOOL_POLICY.plugins` already says so for
capability plugins — so a determined command can do things the OS did not read in its argv. That is precisely why the
non-gated branch *also* requires an **independent governed security review** of that tool identity and version, and
why the owner's decision lists it among the five conditions. The floor catches what is mechanically visible; the
review carries what is not. `TOOL_POLICY.installation_envelope`'s comment says this in the policy itself.

### 2.3 The six triggers, and how each is derived

| Trigger | Demanded, as the OS derives it | Authorised |
|---|---|---|
| `privilege_escalation` | a `required_permission_classes` entry the acting role does not hold; `permissions.repo_write` without `WRITE_REPO_SCOPED`; a privilege-raising command token (`sudo`, `su`, `doas`, `pkexec`, `runas`, `setcap`, `setuid`, `chown`, `chmod`) | `TOOL_PERMISSIONS.roles.<role>` |
| `host_level_authority` | a `host_authority_classes` entry (`SYSTEM_INSTALL`, `DEPLOY_STAGING`, `DEPLOY_PRODUCTION`, `CLOUD_WRITE`); a system/package-manager token (`apt-get`, `yum`, `brew`, `systemctl`, `docker`, `kubectl`, …); a `host_scope_flags` argument (`-g`, `--global`, `--system`, `--user`) | nothing: no role's permission list authorises authority that reaches past the project |
| `broader_filesystem_or_project_access` | a path token that leaves the project (absolute, `~`, drive-qualified, or any `..` segment); an in-repo path whose path-map `mutation` is not `allowed` | the project root as the path map scopes it |
| `new_secret_or_credential_access` | a `credential_classes` entry (`SECRET_READ`); `permissions.secrets` or a `credential_scope`; an argument or environment name matching `credential_patterns`; a path matching `SECURITY_POLICY.secret_path_patterns`; a path the path map classifies `restricted` or `secret` | nothing: the project authorises no new credential access to an installed tool |
| `governance_or_security_policy_mutation` | a path token under `policy_paths` (`framework/**`, `governance/**`, `spec/decisions/**`, `.governance-state/**`) other than the two an installation writes; a manifest `path`/`registry` other than those two; a descriptor declaring `policy_overrides`, `governance_writes` or `exceptions` | exactly the installation's own descriptor and the generated tool registry |
| `new_or_unrestricted_network_trust_boundary` | network demanded (a `network_classes` entry, `permissions.network`, or any derived endpoint) **and** either the role holds no network class, or an endpoint is not in the tool registry's `network_allowlist`, or **no endpoint can be derived at all** | ordinary use of an approved registry or allowlisted service (`tools/registry/TOOLS.yaml` `network_allowlist`) by a role that already holds a network class |

The last row is the owner's own control, stated as a rule: ordinary allowlisted network use is *not* by itself
elevated, while an unbounded boundary is. §7's control test exercises all three of its states.

### 2.4 Fail closed, fail gated

Every one of these is an expansion, recorded in `authority_envelope.undetermined` or as an unmet condition:

- `TOOL_POLICY.installation_envelope` absent (an older kernel): the authorised envelope cannot be determined;
- `TOOL_PERMISSIONS` authorises no class for the acting role: nothing asked for is inside the envelope;
- the descriptor carries no command the OS can read: what it would do outside the project cannot be determined;
- `CHANGE_POLICY.change_classes.tool_installation` absent: no installation is pre-authorised at all;
- a condition `TOOL_POLICY.auto_install_conditions` does not declare: it was never evaluated, so it cannot hold;
- the installation request cannot be derived from the descriptor the transaction carries (`prepare_installation`
  fails): no condition can be evaluated.

The review and the pin are covered by the existing conditions, which the rule maps onto: `licence_and_security_satisfied`
already fails when the review is missing, self-attested, unbound to this tool identity and version, or not T2-verified
(`tools::security_review_evidence`, BC-P2-41), and `version_pinned_and_recorded` fails when nothing is pinned. A
failing condition means the branch is `gated`.

That is not only an argument from the mapping: `r4_residual::a_tool_installed_inside_a_claimed_task_closes_on_its_os_proposed_change_transaction`
— **unchanged this run** — installs a tool whose descriptor names no security review and whose envelope is otherwise
clean, and asserts `impact.human_gate_required: true`. A missing governed review gates, with nothing else differing.
`ws07::a_governed_security_review_by_another_role_lets_the_installation_proceed` covers the other two shapes the
condition refuses (a review of another version; a review the installing role wrote — self-attestation), and
`repair3::lower_trust_inputs_cannot_manufacture_higher_trust_facts` covers a descriptor's own `security_review:
passed`; all three leave the installation unwritten.

---

## 3. The rule as written in policy, and the governed record that carries it

### 3.1 `framework/policies/CHANGE_POLICY.yaml` (version 1.0.0 → 1.1.0)

A new top-level `change_classes` map — "a change class whose human-gate rule an owner decision settles, rather than
the radius and trigger rules above" — with one entry:

```yaml
change_classes:
  tool_installation:
    owner_decision: OD-P2-03
    decision_record: D-0011
    manifest_op: install_tool
    subject_paths: ["governance/project/tools/**"]
    non_gated_conditions:
      authenticated_and_pinned: version_pinned_and_recorded
      independently_governed_reviewed: licence_and_security_satisfied
      registered: tool_registered
      reversible: installation_reversible
      within_authorised_envelope: authority_envelope
    authority_expansion_triggers:
      - privilege_escalation
      - broader_filesystem_or_project_access
      - new_secret_or_credential_access
      - host_level_authority
      - governance_or_security_policy_mutation
      - new_or_unrestricted_network_trust_boundary
    envelope_sources: [TOOL_PERMISSIONS.yaml, AUTHORITY_POLICY, DATA_SENSITIVITY.yaml, SECURITY_POLICY,
                       REPOSITORY_CONTRACT.yaml, TOOL_POLICY.installation_envelope]
    fail_closed: true
```

Two properties of the mapping are worth naming.

- **Each of the owner's five conditions names the `TOOL_POLICY.auto_install_conditions` entry that decides it.** The
  rule is not a second, parallel set of checks that could drift from the installation's own.
- **A condition `auto_install_conditions` does not declare cannot hold.** So the rule can never be satisfied by
  *shortening* `auto_install_conditions`: removing `licence_and_security_satisfied` does not make a tool
  "independently governed-reviewed", it makes that condition unevaluated, and the installation gates. This is the
  direct answer to "do not weaken `TOOL_POLICY` to achieve this".

### 3.2 `framework/policies/TOOL_POLICY.yaml` (version 1.0.0 → 1.1.0)

A new `installation_envelope` block supplying the authorised envelope (§2.1), with the class lists, the command-token
floor, the credential-name patterns and the policy paths. Its comment states that it is only ever the authorised
side, that nothing a descriptor declares enters it, that the token lists are a kernel floor and not a safety proof,
and where the network allowlist lives and why.

**The approved registries and allowlisted services are not here**: they are in `tools/registry/TOOLS.yaml` under
`network_allowlist`, because registry hostnames are ecosystem knowledge and `INV-005` keeps it out of kernel policy
(§2.1). `tools/` is a kernel payload directory (`KERNEL.yaml` `payload_dirs`), so the allowlist ships, installs and
is hash-verified with the rest of the kernel, and no project overlay reaches it at all.

**`auto_install_conditions`, `approved_licences`, `health_check_required`, `mcp` and the whole `plugins` block are
untouched.** A parsed key-by-key comparison of both policies against the base is in
`evidence/identity-and-scope-0055.out`: `TOOL_POLICY` gains exactly one key (`installation_envelope`) and
`CHANGE_POLICY` exactly one (`change_classes`), each policy's own `version` moves 1.0.0 → 1.1.0, and **no other key
of either policy differs in any way**. Nothing was relaxed; two purely additive blocks were added.

### 3.3 Policy precedence: no project may weaken either

`POLICY_PRECEDENCE.yaml` was **not changed**. Its existing catch-alls `{key: CHANGE_POLICY.*, mode: immutable}` and
`{key: TOOL_POLICY.*, mode: immutable}` already cover every new key. Adding an explicit `additive`/`shrink_only` rule
so that a project could *tighten* these lists would have been a loosening of the precedence rules themselves, and I
did not make it; `immutable` is the stronger posture and needed no change.

**Asked of the product rather than argued from the rules** (`evidence/od-p2-03/policy-precedence-probe.out`, runner
beside it). On an installed, provisioned project, with the release `gov` of this tree, a
`PROJECT_POLICY.policy_overrides` block attempting four weakenings — emptying the host-authority token floor,
emptying the credential-name patterns, cutting the six expansion triggers to one, and repointing
`within_authorised_envelope` at a condition that always holds — is **refused in all four cases**:

```
applied:
refused:
  TOOL_POLICY.installation_envelope.host_authority_tokens  -> … POLICY_PRECEDENCE mode 'immutable', rule TOOL_POLICY.*
  TOOL_POLICY.installation_envelope.credential_patterns    -> … POLICY_PRECEDENCE mode 'immutable', rule TOOL_POLICY.*
  CHANGE_POLICY.change_classes.tool_installation.authority_expansion_triggers  -> … rule CHANGE_POLICY.*
  CHANGE_POLICY.change_classes.tool_installation.non_gated_conditions.within_authorised_envelope -> … rule CHANGE_POLICY.*
```

and `gov policy effective` afterwards still shows the six shipped triggers, `within_authorised_envelope ->
authority_envelope`, all 28 shipped host-authority tokens and all nine credential patterns. The same probe reads the
network allowlist out of that project's **installed kernel**
(`governance/kernel/tools/registry/TOOLS.yaml` `network_allowlist`), showing that it is payload rather than policy
and so out of a project overlay's reach entirely. The probe writes only into a scrap project left behind by an
already-finished certification scenario; nothing in the repository is touched.

### 3.4 `framework/policies/ENFORCEMENT_MAP.yaml`

Two entries, so the new keys are not "declared but does nothing" (verifier M12,
`repair::policy_enforcement_coverage_is_complete_and_honest`):

- `CHANGE_POLICY.change_classes.*` → `[cit::class_decision, tools::installation_change_decision]`;
- `TOOL_POLICY.installation_envelope.*` → `[tools::installation_authority]`.

### 3.5 The governed decision record: `spec/decisions/D-0011.yaml`

A `decision` record, `status: ACTIVE`, `chosen_option: B`, `human_approved: true`, `approved_by: human (product
owner, owner decision OD-P2-03 answering owner gate HG-P2-0002)`, `governed_by: [PRJ-0001, D-0002, D-0007, D-0010]`.
It states the question the three accepted sources could not all satisfy, both options, the owner's choice, what the
decision does **not** relax (K3's change transaction, the transaction's own simulation/binding/snapshot/rollback,
BC-P2-41's installation gate, F4's "the descriptor cannot authorise itself"), and five consequences: the policy rule,
the envelope block, the executable form, F4's continuing bind, and the consequences the owner accepted. Its header
comment points at the owner's own record,
`release/orchestration/phase-2/GATES/OWNER-DECISION-P2-0003-TOOL-INSTALL-GATE.md`.

### 3.6 Visible to `gov` policy inspection and to an auditor

- `gov policy effective CHANGE_POLICY` and `gov policy effective TOOL_POLICY` print the rule and the envelope, with
  any project override and any refusal (`gov policy overrides`). Both outputs are in
  `evidence/od-p2-03/policy-precedence-probe.out`, taken from a real project with the release `gov`.
- Every `gov tools install` answer carries `change_class`: the branch, why, the per-condition results, the
  per-trigger findings with what was demanded, where the OS read it and what is authorised.
- The change transaction's `impact.change_class` records the same, inside the impact an approval binds.
- The installed descriptor's `approval.authorised_by` carries it forward (§4.4).
- `docs/ARCHITECTURE.md` §4.7 states the rule and the derivation in prose; `docs/COMMANDS.md` states what
  `gov tools install` returns.

**No new subcommand and no new CLI surface**, so there is nothing to classify in `COMMAND_GUARDS` / `g0_label`;
`ws03::every_cli_command_label_is_classified_by_g0` is unaffected. No schema version changed, so nothing needed
mirroring in `framework/KERNEL.yaml` (the policy documents' own `version` fields are not the schema versions
`KERNEL.yaml` declares — `kernel::schema_version_problems` compares `schema_versions` against the
`x-schema-version` of each shipped schema file, and no schema file changed).

---

## 4. The two paths, end to end

### 4.1 Not gated

`gov tools install` derives the request, computes the branch, proposes the transaction, CIT-P simulates it
automatically (K3), the simulation raises **no** gate, `execute_host_op` approves it from the pre-authorisation and
CIT-E writes the descriptor — all in the one request, exactly the round-3 shape. The transaction is still a full
transaction: sealed, content- and impact-bound, snapshotted, verified, propagated, with per-path writes recorded, so
an installation made inside a claimed task still closes on those writes (INT3-O1's mechanism, unchanged).

Evidence: `ws07::a_governed_security_review_by_another_role_lets_the_installation_proceed` (no gate raised at all,
`gate_count` unchanged, `installed: true`, `approval.mode: autonomous`, transaction COMMITTED with
`impact.change_class.branch: not_gated` and `impact.human_gate_required: false` while
`impact.human_gate_by_radius_or_trigger: true` — the radius and trigger rules alone would have gated it, and the
owner's rule is what did not); and the control in
`r4_residual::a_tool_installation_is_gated_for_each_way_it_expands_authority`.

### 4.2 Gated, with evidence for every trigger

`r4_residual::a_tool_installation_is_gated_for_each_way_it_expands_authority` runs the same installation — one tool
identity, one governed security review of exactly that identity and version, pinned, reversible, registrable,
declaring nothing but `READ_REPO`, which the acting role already holds — seven times, once per trigger and twice for
the policy-mutation one, each time adding exactly one way of reaching past the envelope. For each it asserts: nothing written; `change_class.branch: gated`;
`unmet_conditions == ["within_authorised_envelope"]` (so the other four conditions held and the expansion is the only
cause); `triggers_fired == [<that trigger>]` (exactly one); the gate is the change transaction's own and the only one
raised; the gate's impact text names the trigger, so the owner is told why; and, once answered, the same install
proceeds and the descriptor records the branch, the trigger and the transaction.

| Trigger | What the variant adds | Declared by the descriptor? |
|---|---|---|
| `privilege_escalation` | `install_command: ["sudo", "true"]` | no — derived by the OS |
| `host_level_authority` | `install_command: ["apt-get", "install", "-y", "env-tool"]` | no — derived by the OS |
| `broader_filesystem_or_project_access` | `install_command: ["true", "/opt/env-tool/bin"]` | no — derived by the OS |
| `new_secret_or_credential_access` | `install_command: ["true", "--token=$GITHUB_TOKEN"]` | no — derived by the OS |
| `governance_or_security_policy_mutation` | `install_command: ["true", "framework/policies/SECURITY_POLICY.yaml"]` | no — derived by the OS |
| `governance_or_security_policy_mutation` (second variant) | `install_command: ["true", "governance/registry/plugin-registry.json"]` — the plugin registry is trusted OS state deciding which programs the OS executes, and an installation never writes it | no — derived by the OS |
| `new_or_unrestricted_network_trust_boundary` | `install_command: ["curl", "-sS", "https://tools.example.invalid/env-tool"]` | no — derived by the OS |

`r4_residual::ordinary_allowlisted_network_use_does_not_gate_but_a_new_boundary_does` is the owner's control, in its
three states: the same request to `https://pypi.org/simple/env-tool` with `NETWORK_READ`, which the acting role
already holds, **installs with no gate** (`network_endpoints: ["pypi.org"]`); the same request to
`https://packages.example.invalid/…` gates on exactly
`new_or_unrestricted_network_trust_boundary`; and a network class with no endpoint the OS can bound gates too, with
the finding naming "cannot determine".

Where an auto-install condition fails as well, BC-P2-41's own installation gate is raised beside the change gate, as
it was before: two approvals, each for what it approves, each naming the other, neither standing in for the other
(`r4_residual::a_tool_installed_inside_a_claimed_task_closes_on_its_os_proposed_change_transaction` and
`ws07::a_tool_installation_is_approved_only_for_that_installation`, both unchanged this run and still green).

### 4.3 The verdict is derived three times, and bound once

- **At the request** (`tools::install`), so the command's answer states the branch and why.
- **At CIT-P** (`cit::simulate_inner` → `cit::class_decision` → `tools::installation_change_decision`), from the
  descriptor the transaction carries — never a verdict handed to it — and recorded in `impact.change_class`. The
  gate is raised only if required: `human_gate_required = by_radius_or_trigger && !pre_authorised`, so the class rule
  can only ever *remove* the gate a pre-authorisation covers and never add one, and a transaction outside a governed
  change class is gated exactly as before (`class_decision` returns `Null`).
- **At CIT-E** (`tools::apply_installation`), from the descriptor the transaction carries and trusted OS state **as
  it stands at the write**. If the installation would now expand authority and no human gate approved the
  transaction, the write is refused `TOOL_INSTALL_ELEVATED` and the transaction rolls back. This closes the window
  between simulation and execution, and it is also what stops a hand-proposed `install_tool` transaction from
  installing an elevated tool on an automatic approval.

  `r4_residual::an_installation_whose_envelope_changed_after_simulation_is_refused_at_the_write` exercises it: a
  request whose only failing condition is `cost_within_budget` (which is *not* one of the owner's five, so the
  transaction is pre-authorised and gateless while the installation's own gate is pending), then the acting role's
  authorised permission classes are narrowed in `TOOL_PERMISSIONS.yaml`, then the installation approval is answered
  and the install repeated: `TOOL_INSTALL_ELEVATED`, nothing written, `cit_status: ROLLED_BACK`, and the refusal
  carries the re-derived verdict.

**Bound once**: `binding::impact_of` — the whitelist of impact fields an approval binds — now includes the
change-class verdict (class, rule, owner decision, governed record, branch, `gate_required`, why, unmet conditions,
triggers fired). It already bound `human_gate_required`; under this decision the class verdict is what decides that
field, and `cit::approve_with` reads it to allow approval above `auto_approve_max_radius`. So the branch a
transaction was approved under is as tamper-evident as the rest of its bound impact, and a re-simulation that lands
on the other branch does not inherit an earlier approval. The evidence detail around the verdict (per-finding prose,
the sources list) is left out of the binding, as prose consequences and semantic candidates already are.

### 4.4 Recording is unconditional, and an auditor can trace any installed tool

| Where | What it carries |
|---|---|
| `gov tools install` answer | `change_class` (branch, why, conditions, envelope findings) beside `checks`, `installation_sha256` and `change_transaction` |
| the change transaction's bound impact | `impact.change_class`, and `impact.human_gate_required` / `impact.human_gate_by_radius_or_trigger` |
| the gate's impact text (gated branch) | a consequence line naming the class, the rule and why |
| the auto-approval decision record (non-gated branch) | `rationale` naming the owner decision, the governed record and the rule; `change_class` as a field |
| the installed descriptor | `approval.authorised_by`: owner decision, governed record, rule, branch, why, the bound independent security review, the envelope verdict and its triggers, the change transaction — plus `approval.gate` where a gate authorised it, and the existing `security_review_evidence` and `installation_sha256` |

That is Contract v3 F4 requirement 4 in the decision's own terms: elevated permissions are exactly the gated class,
so they reference an actual gate; and a non-elevated installation references the decision, the rule and the bound
independent review.

---

## 5. What was kept and what was dropped from `ab0a075`

**Kept, unchanged** (the change-control machinery that serves Contract v3 K3):

- `cit::propose_installation` and the `install_tool` manifest operation (`cit` schema 1.3.0, `KERNEL.yaml`
  `cit: 1.3.0`), with `origin: system`, `system.kind: tool-installation`;
- the generalised host-proposed helpers `HOST_PROPOSED_OPS`, `host_op_of`, `host_transactions`,
  `close_host_requests`, `note_host_gate`, `host_gate_state`, `execute_host_op`, shared with the plugin
  registration; no registration behaviour changed;
- `tools::prepare_installation`, `installation_op`, `installation_gate_package`, and BC-P2-41's installation gate
  with the two approvals naming each other;
- `tools::apply_installation` as the CIT-E side: it re-derives the request from the bytes as they are, requires
  exactly the approved subject (`TOOL_INSTALLATION_STALE`), re-verifies the installation approval where a condition
  failed (`TOOL_NOT_APPROVED`), and refuses an acting role without installation authority (`AUTHORITY_DENIED`);
- `tools::install_write` as the **one** writer, composing the tools directory itself and calling
  `srr::plugins::guard_acquisition_below_floor("tools install")` immediately before its write — the §6 acquisition
  sink asked at the instant of the write — with `tools::install` keeping its operation-level `guard_write` and its
  own unconditional sink call;
- `--execute` as part of what the transaction's approval binds, with the install command running inside the
  transaction so a failure rolls back;
- `cit::materiality::is_tool_installation_path` and the `tool installation` rule (a descriptor is a governance
  **and** a security change), and the `install_tool` entries in `manifest_paths`, `changes_of_manifest`, the
  dependents walk, the snapshot's created paths and `apply_op`.

**Dropped:**

- the **unconditional gating**. Nothing in `ab0a075` explicitly forced a gate; the transaction was gated because the
  generic rules gate every `governance_change` at radius R5. That is now conditional on the governed class rule,
  through `human_gate_required = by_radius_or_trigger && !pre_authorised` in `cit::simulate_inner` and the matching
  pre-authorisation exception in `cit::approve_with`;
- **its edit to `ws07::a_governed_security_review_by_another_role_lets_the_installation_proceed`** (§7).

**Not done to achieve any of it:** `TOOL_POLICY.auto_install_conditions` unchanged; the `plugins` block unchanged;
`POLICY_PRECEDENCE.yaml` unchanged; no schema and no `KERNEL.yaml` entry changed; no test renamed, removed or
`#[ignore]`d; no protected round-4 file touched. `evidence/identity-and-scope-0055.out` shows all of it, including a
parsed key-by-key comparison of `TOOL_POLICY`, `CHANGE_POLICY` and `tools/registry/TOOLS.yaml` against the base
(one key added to each, two `version` bumps, nothing else) and the INV-005 word scan over `framework/` (no hits).

---

## 6. Files changed by this run (`d96c8ab` → `4bd7468`)

**Runtime** — `tools.rs` (the envelope and the branch decision: `ENVELOPE_SOURCES`, `envelope_list`,
`installation_commands`, `token_values`, `leaves_project`, `endpoint_host`, `matches_any_pattern`,
`credential_names`, `finding`, `network_allowlist`, `installation_authority`, `change_decision`,
`installation_change_decision`, `authorised_by`; wired into `install`, `apply_installation` and
`installation_proposal`), `cit/mod.rs`
(`class_decision`, `class_pre_authorised`, the gate decision and the impact block in `simulate_inner`, the
pre-authorisation exception and the named rationale in `approve_with`), `cit/binding.rs` (`class_of`, and
`change_class` in `impact_of`).

**Framework** — `policies/CHANGE_POLICY.yaml` (`change_classes.tool_installation`, version 1.1.0),
`policies/TOOL_POLICY.yaml` (`installation_envelope`, version 1.1.0), `policies/ENFORCEMENT_MAP.yaml` (two entries).
No schema file and no `KERNEL.yaml` entry changed.

**Kernel tool registry** — `tools/registry/TOOLS.yaml` (a new top-level `network_allowlist` key; the `tools` array
and every entry in it are untouched, and the document is not schema-validated at the top level — only each `tools[]`
entry is, against the `tool` schema).

**Governed records** — `spec/decisions/D-0011.yaml` (new).

**Docs** — `docs/ARCHITECTURE.md` §4.7, `docs/COMMANDS.md`.

**Tests** — `tests/certification/r4_residual.rs` (three new tests and their helpers),
`tests/certification/ws07.rs` (one test restored and strengthened), `runtime/src/tools.rs` (one new lib test).

**Not touched:** P2-AR-0042's round-4 files (`runtime/src/contracts.rs`, `framework/contracts/**`, the acceptance
schema, `tests/governance/capability-evidence-map.yaml`, `docs/generated/**`); `release/verification/`,
`release/root-of-trust/`, `release/releases/`, `release/orchestration/phase-1/`,
`release/capability-baseline/audit-0/`, other workstreams' `repair-1/` directories; Contract v3 and the frozen gate
contract (`4c2df291…`, `d2f33e89…`); P2-AR-0043's and P2-AR-0053's reports and evidence directories.

---

## 7. Tests added and changed

### Added

| Test | What it proves |
|---|---|
| cert `r4_residual::a_tool_installation_is_gated_for_each_way_it_expands_authority` | OD-P2-03 requirement 7, the gated branch: for **each** of the six authority-expansion triggers, on the same otherwise-qualifying installation (reviewed, pinned, reversible, registrable, declaring only a class the role holds), the descriptor is not written, the branch is `gated`, the **only** unmet condition is `within_authorised_envelope`, exactly one trigger fired, the change transaction's own gate is the only gate raised and its impact names the trigger, and answering it installs with the branch, trigger and transaction recorded in the descriptor. Seven variants: one per trigger, and a second policy-mutation one naming the plugin registry, which an installation never writes. Also the non-elevated control: the same tool with nothing elevated installs in one request with no gate. **Every** variant is found by the OS in a command the descriptor declares nothing about, which is F4 / BC-P2-39 made mechanical |
| cert `r4_residual::ordinary_allowlisted_network_use_does_not_gate_but_a_new_boundary_does` | OD-P2-03's own control, in three states: ordinary use of an approved registry by a role that already holds a network class is **not** elevated and does not gate; the same request to a host the policy does not authorise is a new network trust boundary and gates; a network class with no endpoint the OS can bound is unrestricted and gates (fail closed) |
| cert `r4_residual::an_installation_whose_envelope_changed_after_simulation_is_refused_at_the_write` | OD-P2-03 requirement 3 at the instant of the write: a pre-authorised transaction is not a licence to write later. The acting role's authorised classes are narrowed between the request and its execution; CIT-E derives the branch again from trusted state as it stands, refuses `TOOL_INSTALL_ELEVATED`, writes nothing, rolls back, and carries the re-derived verdict in the refusal. The same check is what stops a hand-proposed `install_tool` transaction installing an elevated tool on an automatic approval |
| lib `tools::tests::the_os_reads_an_installations_own_commands_for_what_it_would_hold` | The derivation the "descriptor cannot authorise itself" half rests on, at unit level: every command the installation carries is read (install, uninstall, health check), a `--flag=value` hides its value and the value is read too, paths that leave the project are recognised (absolute, `~`, drive-qualified, any `..` segment — normalised or not, because the OS does not resolve a path it will not execute), endpoint hosts are extracted with user and port stripped and case-folded, and credential names are found in both `NAME=…` and `${NAME}` forms |

### Changed (none renamed, removed or `#[ignore]`d)

| Test | Change | Reason |
|---|---|---|
| cert `ws07::a_governed_security_review_by_another_role_lets_the_installation_proceed` | P2-AR-0053's edit is dropped: the test asserts again that **no gate is raised** — `gate_count` unchanged, `human_gate` null, `installed: true` in the one request, `approval.mode: autonomous`. Added on top: the change transaction still happened and is COMMITTED with no gate of its own; `impact.change_class` records `branch: not_gated`, `owner_decision: OD-P2-03`, `decision_record: D-0011` and `expands_authority: false`; `impact.human_gate_required: false` while `impact.human_gate_by_radius_or_trigger: true`; the bound independent review is the report the security-class task close wrote; and the installed descriptor's `approval.authorised_by` names the owner decision, the branch, that review and the transaction | OD-P2-03 requirement 6. Its tool is inside the envelope by construction: `READ_REPO` for a role that holds it, `network: false`, and commands (`true`) that neither raise privilege nor leave the project |

Everything else in `ws07.rs`, including
`ws07::a_tool_installation_is_approved_only_for_that_installation` (P2-AR-0053's other edit, which belongs to the
kept change-control machinery: its descriptor fails a condition, so it is gated and answers both gates), is
unchanged this run.

---

## 8. Availability rule (P2-HO-0031), G0 and blocks

- **The change is in the available direction.** It removes a Human Gate from installations that stay inside the
  project's existing authority, and adds one only where authority expands. No refusal a repair-delta class requires
  was reopened, and no R1/§5/§6 property changed (§0).
- **The one new refusal is typed and scoped.** `TOOL_INSTALL_ELEVATED` refuses exactly the write of an elevated
  installation that no gate approved, names the rule, the owner decision and why, carries the re-derived verdict in
  its details, and tells the operator how to proceed (re-simulate to raise the gate, or install again for a new
  request). It rolls the transaction back rather than leaving it half-applied.
- **No new subcommand**, so `COMMAND_GUARDS` and `g0_label` are unchanged and
  `ws03::every_cli_command_label_is_classified_by_g0` is unaffected. The installation still passes G0 through its
  transaction (`cit propose|approve|execute` with the installation's paths), and FREEZE/PAUSE refuse it through the
  unchanged `guard_write(p, "tools install")`.
- **No new hard block and no new finding family.**

---

## 9. Remaining integration points for the round-4 integrator

Carried from P2-AR-0053's §5 and P2-AR-0043's §7, updated where this run changes them.

| Id | For | What |
|---|---|---|
| R4-IP-1 | verifiers and probe authors | **Revised by OD-P2-03.** P2-AR-0053's note said any probe that installs a tool must now answer the installation's change gate, "including one that relies on a governed security review". That is no longer true for a review-evidenced installation inside the envelope: it raises no gate at all and completes in one request, as it did in round 3. A probe that installs a tool which **expands authority** (or fails one of the five conditions) must answer the change gate; one that installs inside the envelope must not expect a gate. The plugin-registration half of the note stands unchanged: a probe registering an executable plugin must answer both its gates |
| R4-IP-2 | WS-1 evidence map (P2-AR-0042 or its successor) | Owners for the four tests added this run, in addition to P2-AR-0043's twelve and P2-AR-0053's three: BC-P2-41 / Contract v3 F3–F4 / K3 and OD-P2-03 → the three new `r4_residual` tests; F4 "descriptor cannot authorise itself" / BC-P2-39 → the new `tools` lib test. `ws07::a_governed_security_review_by_another_role_lets_the_installation_proceed` keeps its existing owners (IP-W7-1 / BC-P2-41) and now also evidences OD-P2-03's non-gated branch |
| R4-O1 | closed | **Answered by the owner (OD-P2-03) and implemented here.** No longer an open item |
| R4-O2 | routing / verifier | Unchanged: `gov plugins unregister` still writes the sealed registry directly, and nothing uninstalls a tool, so there is no de-installation path to govern. Whether K3 wants impact simulation for either is not stated by the sources read. OD-P2-03 does not speak to removal |
| R4-O3 | WS-8 (probe maintenance) | Unchanged: WS-8's `r1-invariants.sh` line "floors_path( outside state.rs = 1" stays at 1 (INT3-O3 not done) |
| R4-O4 | routing | Unchanged: `install_tool` widened the CIT manifest vocabulary (`cit` schema 1.3.0, mirrored in `KERNEL.yaml`) in `ab0a075`; an integrator should confirm the schema-version handling with WS-9. **This run changed no schema and no `KERNEL.yaml` entry** |
| R4-O5 | routing (new, optional) | The policy documents' own `version` fields moved to 1.1.0 for `CHANGE_POLICY` and `TOOL_POLICY`. These are not the schema versions `KERNEL.yaml` declares and nothing in the product reads them, but an adopted project installed from an older kernel has neither new key: it therefore gates **every** installation, which is the intended fail-closed default and needs no migration. An integrator may still wish to note the policy-version bump in the release manifest |
| R4-O6 | verifier (new, optional) | `gov tools install` is the only way to see an installation's envelope verdict, and its first call proposes a transaction. A read-only `gov tools envelope --descriptor f` (or a `--dry-run`) would let an auditor inspect the comparison without proposing anything. OD-P2-03 does not require it and it would add a subcommand to classify, so it is not in this run |

Also carried and not reopened: INT3-O4, R3-WS5-11, and the four optional items P2-AR-0043 did not do (INT3-O3,
IP-R3-WS04-03, IP-R3-WS04-06, IP-R3-WS02-11), each with its reason in its report.

---

## 10. Process disclosures

- Model: Claude Opus 5 (1M context), `claude-opus-5[1m]`. Fresh context. No sub-agents. The owner was not contacted;
  the owner's decision was read from the committed record named in the header.
- I read `OWNER-DECISION-P2-0003`, `P2-HO-0050`, `P2-HO-0048`, `P2-HO-0042`, `P2-HO-0031`, `P2-HO-0020` and
  `P2-HO-0010` through `git show release/4.1.6-rc1:…` where they postdate my base. I checked out, merged, rebased,
  tagged and pushed nothing, and touched no branch but `phase2/repair-1-r4-residual-c`. The main checkout at
  `/home/usain/Dynamic-Agentic-Engineering-OS` was not modified.
- I read no session or agent transcript, no task-output store and no user auto-memory.
- `rm` is denied in this environment and was not used. Superseded evidence was **moved aside** into this session's
  scratchpad (`scratchpad/aborted/`), never deleted, and is not part of the evidence set: the regression outputs
  taken at the two earlier product commits (`*.6c42f34.out`, two `*.wip.out`) and four aborted chunk outputs.
- **The certification suite was started three times and completed once, deliberately.** The first run was stopped
  when I decided the change-class verdict should be inside the approval binding (`binding.rs`, commit `6c42f34`);
  the second when the first chunk showed this machine running materially slower than P2-AR-0053's, so that a
  seven-module chunk would not fit the tool's ten-minute limit (hence fourteen smaller chunks at three threads
  instead of nine at two); the third when reviewing the envelope found the plugin registry wrongly counted among
  "what an installation writes" (commit `4bd7468`). Every chunk in `evidence/regression-0055/` was therefore run at
  `4bd7468` with a clean product tree — each chunk's own header records its commit and `dirty=0`, and the summary
  file states it.
- Long certification chunks that exceeded the tool's ten-minute foreground limit ran in the background; their output
  went to the chunk files named in the summary, which I read. The task-output store was not read.
- My scratch trees are under `target/P2-AR-0055/`.
- The machine may have been shared with other work during the runs; timings are indicative only.
