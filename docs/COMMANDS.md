# gov command reference

Global flags: `--root <path>` (default: discovered upwards from cwd), `--json` (envelope `{ok, command, result|error, session}`),
`--session <id>` (or `$GOV_SESSION`; the declared session is installed once per invocation and is what adoption
records as authorship), `--role <role>` (or `$GOV_ROLE`). Exit codes (API-0002): 0 ok · 1 governance error ·
2 usage · 3 verification failed/unhealthy · 4 blocked by control state or human gate.

**Acting role.** `--role`, else `GOV_ROLE`, else *undeclared*: an undeclared invocation carries L0 (no privileged
authority); a declared `human` role also carries L0 (human answers are owner-signed). A stage role flag
(`--reviewer-role`, `--verifier-role`) declares the role when nothing else does and must agree with a declared one
(`ROLE_CONFLICT`); a `--role` written after the subcommand is the same global flag, so one invocation has one role. Every command is classified by G0 before it runs (`G0_UNCLASSIFIED` for a command nobody classified):
writes are refused under FREEZE_WRITES (`FROZEN`) and PAUSE (`PAUSED`) except the listed recovery operations (the
emergency controls, `cit rollback`, `telemetry emit`, `rebuild-memory`/`memory rebuild`, and under PAUSE `gate
present`), and the role must meet the command's authority class (`AUTHORITY_DENIED`, `details.cause` =
`ROLE_UNDECLARED` | `HUMAN_ROLE_CLAIM` | `LEVEL_TOO_LOW`; `UNKNOWN_ROLE`). `task create|claim|close`, `cit propose` and
`handoff create` are also refused while a health hard-block governs what they rely on (`HEALTH_HARD_BLOCK`, naming the
block and its scope; see `gov health status`); the work that remedies a block stays available (a change transaction on
its subjects; creating, claiming and handing off work that declares the block's check among its `remedies`).

## Human surface (framework §34)
| Command | Purpose |
|---|---|
| `gov status` | Reconstruct current governed state for a fresh agent (framework, project, control, memory freshness, DAG, gates, open CITs, latest checkpoint, next action, read list) |
| `gov continue [--claim]` | Present pending gate text, pick the next runnable task this session can take (longest chain first), compile its context packet, resolve skills and routing; optionally claim. A derived index that cannot be opened is refused `INDEX_UNAVAILABLE` (remediation `gov rebuild-memory`) |
| `gov gate present <HDG> [--receipt-file f \| --receipt-inbox]` | Render the decision package (records the package SHA-256, writes it to the human-channel outbox; rendering is not presentation). With an owner-signed `human-gate-receipt`, record that the package reached the human |
| `gov decide <HDG> [--option X] [--answer-file f]` | Apply the owner-signed `human-gate-answer` (the inbox, or `--answer-file`) → decision record, unblock or block tasks, link the CIT |
| `gov decide <HDG> --option X --by <acting role> --rationale … [--evidence id]…` | Agent resolution within `HUMAN_GATE_POLICY.agent_resolvable_when` (L3+, assessed by another session or the OS; never for human-only triggers) |
| `gov trust human-channel` | The human channel: anchor (the provisioned root's `human-gate` delegation), inbox/outbox, what a signed document binds, premise check |
| `gov audit [--deep] [--family f]… [--no-persist]` | Governance suite → audit record with inputs/result hashes; exit 3 when UNHEALTHY; `--no-persist` writes no record |
| `gov pause` / `gov freeze-writes` / `gov cancel-agents` / `gov resume` | Emergency controls honoured by every mutating operation |
| `gov intent "<text>"` | Deterministic natural-language routing to a plan and concrete commands |

## Lifecycle and trust
| Command | Purpose |
|---|---|
| `gov trust provision --anchor <root.json>` | Administrator: install this machine's Signed Release Root (from the administrator domain, never repository content: `SRR_ANCHOR_FROM_REPOSITORY_REFUSED`; once only: `SRR_ALREADY_PROVISIONED`). The documented first run is **provision, then install**: `gov trust provision --anchor <root metadata from the administrator domain>`, then `gov init --source <release signed under it> --name …`. A machine with no trust anchor refuses external-source kernel ingress (`SRR_UNPROVISIONED_EXTERNAL_SOURCE_REFUSED`) and installs only the binary's embedded payload, as a marked bootstrap installation never presented as current, verified or certified |
| `gov trust bind --authority <doc> --key <file>` | Administrator (P2-ADJ-0002, the one provisioning command): bind this provisioned machine to the owner's T2 binding authority — the owner-signed, versioned `t2-binding-authority` document and one binding key it authorises, both from the administrator domain; do the same on each of the owner's machines (a rotation binds the new version with its active key). Refused: `SRR_BELOW_FLOOR_REFUSED`, `SRR_ENV_CANNOT_CREATE_AUTHORITY`, `T2_BINDING_FROM_REPOSITORY_REFUSED`, `T2_BINDING_UNPROVISIONED`, `T2_BINDING_NOT_DELEGATED`, the root verifier's `SRR_*` below threshold, `T2_BINDING_AUTHORITY_EXPIRED`, `T2_BINDING_AUTHORITY_ROLLBACK`, `T2_BINDING_AUTHORITY_CONFLICT`, `T2_BINDING_MACHINE_NOT_AUTHORISED`, `T2_BINDING_KEY_NOT_AUTHORISED`, `T2_BINDING_KEY_MISMATCH`, `T2_BINDING_AUTHORITY_INVALID`, `T2_BINDING_KEY_INVALID`. `gov trust status` → `t2_binding` reports the binding |
| `gov trust reseal [--dry-run]` | L4: re-seal under the owner's active binding key the records this machine sealed with its own key while provisioned (continuity for records written before it was bound), keeping their operation and time; unprovisioned-era and unverified records are left as they are (`T2_BINDING_UNAVAILABLE` when the machine does not seal under the authority) |
| `gov trust status \| root-update --anchor f \| break-glass \| recover-transactions` | Posture, anchor, floors and any `DEGRADED — RECOVERY ONLY` marking; root succession; where an owner-signed break-glass authorisation goes; replay interrupted install transactions |
| `gov init [--source] [--name] [--alias] [--intent] [--force] [--skip-index] [--channel] [--break-glass]` | Greenfield onboarding: kernel, lock, overlay, roots, `.gitignore`, held-out file, registry, adapters (incl. the provider hooks), index, doctor, conformance audit. `--source` is a release signed under the provisioned root (on an unprovisioned machine: embedded payload only, BOOTSTRAP) |
| `gov adopt baseline\|inventory\|classify\|map\|plan\|test-design\|review\|migrate\|verify-migration\|extract-legacy\|build-memory\|verify-memory\|audit\|status\|rollback` | Stages A0–A11 (`gov migrate …` is an alias). Every stage needs a declared session (`--session`/`GOV_SESSION`, or `review --reviewer-session`) and records its declared role and session in the T2-sealed adoption record; A5/A7/A10/A11 are performed only by `migration-reviewer` / `migration-verifier` / `memory-verifier` / `independent-auditor` in a session and role that authored no planner, executor or builder stage; A5 needs reviewer-authored tests and binds catalogue, plan and tests (A6/A8 refuse `APPROVAL_STALE` after a change); A7 accepts only its computed verdict with ≥1 executed test; A10 needs verifier-authored held-out queries; A11 runs G5. `gov adopt status` shows authorship, verdicts and the record's binding |
| `gov update --check [--source]` / `--apply [--source] [--approve] [--by]` / `--rollback [--break-glass] [--reason]` | Versioned, impact-checked kernel update; `--apply` needs the framework-update gate answered by the human (owner-signed); it moves the tracked OS stores an earlier release kept in `governance/generated/` (plugin registry, skill bindings) to `governance/registry/`, and `--rollback` restores the earlier layout; below-floor rollback needs break-glass |
| `gov doctor` | Health checks with remediation; HEALTHY/DEGRADED/UNHEALTHY |
| `gov rebuild-memory [--incremental]` | Rebuild derived memory; writes index/memory manifests (available under FREEZE_WRITES and PAUSE). A direct upstream change it observes is propagated to its dependants (`upstream_changes`; a sealed system transaction), except under FREEZE_WRITES / PAUSE / below floor, where it is deferred and reported (`gov memory rebuild` likewise) |
| `gov recover [--dry-run]` | Classify interrupted mutations (CIT, migration batch, corrupt DB, claims), repair, checkpoint, freeze on UNKNOWN |
| `gov kernel verify \| trust \| override [--reason] \| reinstall [--source] [--break-glass]` | Kernel verification, trust verdict, L4 override gate, restore of the pinned release (`KERNEL_MISMATCH`, `KERNEL_PIN_REWRITTEN`) |
| `gov release build --version V [--out] [--certification S] [--evidence] [--canonical]` / `verify <dir>` | Immutable release payload + manifest |
| `gov upstream prepare <L-id>` / `submit <PKT-id> --destination <…/lessons/inbox>` | Export gate: `prepare` builds the sanitised packet and raises its export-approval gate (`upstream_export`, human-only, bound to the packet and payload hash); render it with `gov gate present`, the owner answers it (owner-signed), then `submit` exports. `--approved-by` is recorded as a claim and ignored |

## Work system
`gov task create|list|show|status|claim|release|close|dag|replan` · `gov readiness check|plan <F-id>` ·
`gov gate create --question … --fields <package json> | present <HDG> | list | show <HDG> | revoke <HDG> [--reason]` ·
`gov handoff create|return` · `gov checkpoint create [--trigger t]|latest|watchdog|freshness [<CKPT>]` ·
`gov session close [--next-action a] [--task T]` · `gov claims list|sweep` ·
`gov context compile|manifest|verify [--hash]|show [--hash]|receipt --file f|staleness <TASK>` · `gov artefact show <id> | check |
lineage <id> [--direction down|up] [--depth n]` · `gov skills list|resolve <TASK>` ·
`gov route [--task|--class] [--radius] | --record <file> | --report` · `gov telemetry summary|emit` ·
`gov research record --fields f [--draft] [--task T] | update <id> --fields f | conclude <id> [--fields f] | withdraw <id>
--reason r | show <id> | check | sync` · `gov experiment design --fields f | update <id> --fields f | run <id> --results f [--environment e] [--task T] |
reproduce <id> --results f [--environment e] | conclude <id> --fields f | promote <id> --paths a,b [--gate HDG] [--cit CIT] |
abandon <id> --reason r | show <id> | check` · `gov data register --fields f | show <id>` ·
`gov scenario trace <SCN> | check`

Lifecycle hooks: `gov adapters generate` writes `governance/generated/adapters/hooks/provider-hooks.json`, the commands
a harness wires to its own lifecycle events — `pre_compaction` → `gov checkpoint create --trigger before_compaction …`,
`session_end` → `gov session close …`, `model_switch` → `gov checkpoint create --trigger before_model_switch …` (run
with the session's `GOV_ROLE`/`GOV_SESSION`, L1+).

## Health, change control and memory
`gov plugins register --descriptor f` (install-authority role: returns the execution-approval gate `human_gate` and the
registration's change transaction `change_transaction` with its own gate; present and have the owner answer both, then
repeat: the transaction is approved and executed and alone writes the registration) · `gov plugins unregister <id> |
registry | list | health [--ping]` ·
`gov health run [--tier G1..G6] [--check c]… [--changed p]… [--event e] [--no-cache] [--deep] [--no-persist] | status |
checks | history [--limit n] | show <HR-id> | guard <op> [--paths p]… | currency | product [--family f]… |
skills [--skill s] [--record] [--include-deferred] | close-check <TASK> --report f | qualify --kind k --oracle f --report f
[--public-suite d]… [--repository d]… [--run-id id]` (G6 entry: oracle and score report validated, separate from the
public suites and repositories; the record keeps a commitment only) ·
`gov cit propose --proposal … [--trigger] [--targets a,b] [--manifest ops.json] | simulate|approve|reject|execute|rollback|list|show <CIT>
| classify [--id CIT] [--paths a,b] [--base c] | propagate [--dry-run]` ·
`gov memory query "<q>" [--k] [--route] [--include-historical] | verify | freshness | rebuild | graph <node> | impact <ids>` ·
`gov memory miss --query "<q>" [--expected id]… [--detail t]` (an agent-reported retrieval miss; L1) · `gov memory failures` ·
`gov memory benchmark --candidate <c> --candidate <c> [--heldout f] [--record]` (candidates: `current`, `builtin[:dim]`,
`plugin:<id>[:dim]`, any `+rerank:<id>`) · `gov memory select <candidate> --research RES-x [--gate HDG-x]` (governed:
evidence, the change gate for its radius, full re-index, recorded regression, rollback on regression) ·
`gov memory integrity` · `gov memory profile` ·
`gov memory heldout-starter [--force]` · `gov lessons cluster [--inbox d] [--proposals d] [--write]` ·
`gov capabilities serve-embed [--reverse] [--id]` (the binary acting as an embed plugin) ·
`gov plugins register --descriptor f | unregister <id> | registry | list | health [--ping]` (`registry` shows each entry's
T2 binding and whether it is honoured) ·
`gov policy overrides | effective <POLICY>` · `gov adapters generate|verify` ·
`gov tools list|registry|resolve --capability c [--role r]|install --descriptor f [--execute]|health`
(`install` returns the installation's change transaction `change_transaction`, and `change_class` — which branch of
`CHANGE_POLICY.change_classes.tool_installation` applies and why (OD-P2-03: an installation that stays inside the
project's already-authorised envelope needs no gate; one that expands authority does). A gate the request needs is
returned as `human_gate`: the transaction's own when the installation is elevated, the installation's own when an
auto-install condition failed, both when both. Present and have the owner answer what is returned, then repeat the
same install: the transaction is approved and executed and alone writes the descriptor. `--execute` is part of what
the transaction's approval binds, so every request of one installation gives it the same way) ·
`gov capabilities ecosystems|plugins|invoke --plugin id --inputs json` · `gov verify governance|product` ·
`gov oracle format | validate <file> [--oracle f] [--public-suite d]… [--repository d]…` · `gov contract verify|compile` ·
`gov version`

## Refusals
**Human Decision Gates.** Human approval is derived, never supplied. Package: `GATE_PACKAGE_INCOMPLETE`,
`GATE_OPTION_INVALID`. Presentation and answers: `GATE_NOT_PRESENTED`, `HUMAN_CHANNEL_UNAVAILABLE` (no authenticated
channel on this machine; `details.cause` `UNPROVISIONED` with the remediation *provision a Signed Release Root that
delegates `human-gate`*, `ROOT_DELEGATES_NO_HUMAN_GATE`, `NO_ANCHOR`, `MACHINE_STATE_UNRESOLVED`),
`HUMAN_CHANNEL_STANDALONE_DISABLED` (a standalone anchor is not a source of authority), `HUMAN_ANSWER_UNAUTHENTICATED`,
`HUMAN_RECEIPT_UNAUTHENTICATED`, `HUMAN_ANSWER_MISMATCH`, `HUMAN_ANSWER_UNVERIFIED` (stored evidence no longer verifies
against the current anchor), `T2_UNBOUND` (a gate/decision record gov did not write as it stands), `GATE_STATE_INVALID`
(an agent resolution of a human-only trigger). `gov cit approve` requires the CIT's gate presented and answered A
(`GATE_NOT_ANSWERED`, `GATE_DECLINED`, `GATE_REVOKED`, `GATE_MISMATCH`, `APPROVAL_METHOD_MISMATCH`) and `gov cit
execute` revalidates it (`APPROVAL_STALE`).

**Policy.** Overrides that weaken a floor — in `policy_overrides`, `PROJECT_EXCEPTIONS` or any key of
`PROJECT_POLICY.yaml` / `MODEL_ROUTING_OVERRIDES.yaml` — are refused and reported (`gov policy overrides`; doctor D027,
CRITICAL, which is a hard-block for new work). The installed kernel's precedence rules and the binary's both govern.

**Tasks and claims.** `TASK_CLAIMED`, `CLAIM_REQUIRED` (close needs the closing session's claim),
`CLAIM_WORKTREE_MISMATCH`, `CLAIM_SCOPE_CONFLICT` (overlapping mutation scope of another session's live claim),
`CLAIMS_BUSY`, `BUDGET_EXCEEDED`, `ROLE_NOT_DESIGNATED`, `UNKNOWN_ROLE` (on `task create` for a role the kernel does not
define), `MUTATION_SCOPE_VIOLATION` (only a CIT committed after the claim baseline covers an out-of-scope change),
`PRODUCTION_MERGE_NOT_ALLOWED`, `INDEX_PIN_MISMATCH`, `INDEX_STALE`, `GOVERNANCE_SUITE_STALE`,
`GOVERNANCE_SUITE_MISSING`, `HEALTH_HARD_BLOCK`.

**Kernel and releases.** `KERNEL_TAMPERED` (every mutating operation while the installed kernel fails verification;
`gov kernel trust`, doctor D029), `KERNEL_UNANCHORED` (a provisioned machine has not verified this installation),
`KERNEL_MISMATCH`, `KERNEL_PIN_REWRITTEN`, `SRR_RELEASE_UNVERIFIED`, `SRR_BELOW_FLOOR`, `SRR_BELOW_FLOOR_REFUSED`.
Rollback errors: `SNAPSHOT_MISSING`, `SNAPSHOT_CONSUMED`. Release build: `MIGRATION_INCOMPLETE`.

**Plugins and retrieval.** `PLUGIN_DESCRIPTOR_INVALID`, `PLUGIN_NOT_AUTHORIZED`, `PLUGIN_NOT_APPROVED`,
`PLUGIN_PIN_MISMATCH`, `PLUGIN_UNHEALTHY` (doctor D028), `PLUGIN_REGISTRY_MISMATCH` (a descriptor that no longer matches
its registration; a descriptor's `approved_roles`/`provenance` never grant authority), `EMBEDDER_UNAVAILABLE`,
`EMBEDDER_MISMATCH`, `EMBEDDER_BAD_OUTPUT`, `RERANKER_UNAVAILABLE`, `RERANKER_MISMATCH`; plugin host: `PLUGIN_TIMEOUT`,
`PLUGIN_BAD_RESPONSE`, `PLUGIN_PROTOCOL_MISMATCH`, `PLUGIN_ERROR`. `gov adopt migrate --gate-answer` is deprecated and
ignored (a note is returned).

**T2 binding and machines (BC-P2-09, P2-ADJ-0002).** A record gov did not write as it stands is `T2_UNBOUND`, with
`details.t2.binding`: `UNSEALED` (hand-written or legacy), `BROKEN` (edited after sealing), `FOREIGN` (sealed with a key
this machine does not hold — another machine's own key, an unprovisioned or unauthorised machine, or another owner's
binding authority), `UNAUTHORISED` (sealed under a binding authority this machine holds but its trusted root no longer
authorises) or `KEY_UNAVAILABLE`; a verified record reports `scope: provisioned` (portable across the owner's
provisioned machines) or `scope: machine`. Emergency-control state lives in `.governance-state/control.json`; a store
found at both its legacy and its proper location with different content is `STATE_LOCATION_CONFLICT`.

**Admission.** `SRR_UNPROVISIONED_EXTERNAL_SOURCE_REFUSED` (a machine with no trust anchor admits only the binary's
embedded payload, as BOOTSTRAP), `KERNEL_UNANCHORED` (kernel material this machine never admitted, or a provisioned
machine that has not verified this installation: provision, then `gov kernel reinstall --source <signed release>`).

**Work and close.** `TASK_NOT_RUNNABLE` (every DAG reason), `TASK_NOT_READY` (`task status READY` on work that is not
runnable), `TASK_STATUS_REQUIRES_OPERATION` (DONE/CLAIMED/IN_PROGRESS only through close/claim), `GATE_NOT_AUTHORISED`
(a governing gate does not authorise the work; `--force` never overrides it), `INDEPENDENCE_VIOLATION` (independence
is established from recorded authorship), `CLAIM_BASELINE_UNBOUND` (the sealed claim baseline was changed),
`RECEIPT_INVALID` (the close report is the consumption receipt; every validator error listed), `INPUTS_STALE`,
`RETEST_EVIDENCE_REQUIRED`, `PRODUCT_TEST_EVIDENCE_REQUIRED`, `PRODUCT_TEST_EVIDENCE_STALE`, `PRODUCT_TESTS_FAILED`,
`HANDOFF_INPUTS_UNSATISFIED`, `PACKET_BLOCKED`, `PACKET_INVALIDATED`, `MANIFEST_UNSATISFIED`. Explicit holds
(`task status X BLOCKED|WAITING_HUMAN`) stay until an explicit, DAG-checked READY.

**Change control.** `APPROVAL_STALE` (content or impact changed after the answer), `GATE_MISMATCH`, `CIT_STATE_MISMATCH`,
`T2_UNBOUND` (unsealed or copied CIT state), `SECRET_IN_MANIFEST`, `SCHEMA_INVALID` (an appended record invalid at
propose); contradictory authoritative inputs are flagged `CONTRADICTORY` and routed to a `contradiction` gate.

**Evidence and lifecycles.** `EVIDENCE_NOT_CITABLE` (a gate, answer or decision citing research/experiment evidence
that is not governed), `RESEARCH_INCOMPLETE`, `RESEARCH_TRANSITION_INVALID`, `RESEARCH_DRAFT_NOT_EVIDENCE`,
`EXPERIMENT_DESIGN_INCOMPLETE`, `EXPERIMENT_DESIGN_FROZEN`, `EXPERIMENT_ALREADY_RUN`, `EXPERIMENT_INPUT_MISSING`,
`EXPERIMENT_NOT_PROMOTABLE`, `EXPERIMENT_NOT_PROMOTED`, `EXPERIMENT_OUTPUT_IN_PRODUCTION`,
`EXPERIMENT_LIFECYCLE_REQUIRED`, `DATA_PROVENANCE_REQUIRED`, `DATA_REFERENCE_UNKNOWN`, `DATA_CHAIN_INCOMPLETE`,
`DATA_AUTHOR_NOT_INDEPENDENT`, `DATA_NOT_A_REQUIREMENT`; `gov research check` / `experiment check` / `scenario check` list
the lifecycle findings (`RESEARCH_*`, `EXPERIMENT_*`, `DATA_*`, `SCENARIO_*`).

**Adoption.** `ADOPTION_SESSION_UNDECLARED`, `SESSION_CONFLICT`, `ROLE_CONFLICT`, `ADOPTION_ROLE_INCONSISTENT`,
`INDEPENDENCE` (`details.cause` `ROLE_UNDECLARED` | `ROLE_NOT_DESIGNATED` | `SAME_SESSION_AS_BUILDER` |
`SAME_ROLE_AS_BUILDER`), `INDEPENDENT_TESTS_REQUIRED`, `INDEPENDENT_TESTS_INVALID`, `INDEPENDENT_HELDOUT_REQUIRED`,
`APPROVAL_STALE`, `VERDICT_CONFLICT`, `T2_UNBOUND` (a hand-edited adoption record). Export: `HUMAN_GATE_REQUIRED`,
`GATE_DECLINED`, `APPROVAL_STALE`, `HUMAN_APPROVAL_REQUIRED`.

**Plugins, tools and the retrieval profile.** Every executable plugin needs a registration approved by a gate raised
for exactly it (`PLUGIN_NOT_APPROVED`, `cause: UNREGISTERED_EXECUTABLE`); `PLUGIN_REGISTRATION_UNBOUND` (a registry entry
that does not verify), `PLUGIN_IMPLEMENTATION_UNRESOLVED`, `PLUGIN_REGISTRY_MISMATCH`, `PLUGIN_PIN_MISMATCH` (any bound
byte changed); a tool installation is approved only for that installation (`GATE_MISMATCH` for a gate raised for
anything else; `ROLE_CONFLICT`). `EMBEDDER_REVISION_MISMATCH`, `RERANKER_REVISION_MISMATCH`,
`PROFILE_EVIDENCE_REQUIRED|_UNBOUND|_STALE`, `PROFILE_IDENTITY_CHANGED`, `PROFILE_REGRESSION_FAILED|_UNMEASURED`.

Mutation manifest ops (CIT): `set_status`, `set_field`, `mark_stale`, `write_file`, `move_file`, `delete_file`,
`append_record`, `regenerate_views`. Framework migration ops: `add_overlay_file_from_template`, `rename_overlay_file`,
`set_overlay_key`, `rename_overlay_key`, `delete_overlay_key`, `set_lock_field`, `require_index_rebuild`,
`regenerate_adapters`, `note`.
