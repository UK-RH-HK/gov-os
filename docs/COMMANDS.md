# gov command reference

Global flags: `--root <path>` (default: discovered upwards from cwd), `--json` (envelope `{ok, command, result|error, session}`),
`--session <id>` (or `$GOV_SESSION`), `--role <role>` (or `$GOV_ROLE`). Exit codes (API-0002): 0 ok · 1 governance error ·
2 usage · 3 verification failed/unhealthy · 4 blocked by control state or human gate.

**Acting role.** `--role`, else `GOV_ROLE`, else *undeclared*: an undeclared invocation carries L0 (no privileged
authority); a declared `human` role also carries L0 (human answers are owner-signed). A stage role flag
(`--reviewer-role`, `--verifier-role`) declares the role when nothing else does and must agree with a declared one
(`ROLE_CONFLICT`); a `--role` written after the subcommand is the same global flag, so one invocation has one role. Every command is classified by G0 before it runs (`G0_UNCLASSIFIED` for a command nobody classified):
writes are refused under FREEZE_WRITES (`FROZEN`) and PAUSE (`PAUSED`) except the listed recovery operations (the
emergency controls, `cit rollback`, `telemetry emit`, `rebuild-memory`/`memory rebuild`, and under PAUSE `gate
present`), and the role must meet the command's authority class (`AUTHORITY_DENIED`, `details.cause` =
`ROLE_UNDECLARED` | `HUMAN_ROLE_CLAIM` | `LEVEL_TOO_LOW`; `UNKNOWN_ROLE`). `task create|claim|close`, `cit propose` and
`handoff create` are also refused while a health hard-block governs them (`HEALTH_HARD_BLOCK`; see `gov health status`).

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
| `gov trust provision --anchor <root.json>` | Administrator: install this machine's Signed Release Root (from the administrator domain, never repository content: `SRR_ANCHOR_FROM_REPOSITORY_REFUSED`; once only: `SRR_ALREADY_PROVISIONED`). The documented first run is provision, then install |
| `gov trust status \| root-update --anchor f \| break-glass \| recover-transactions` | Posture, anchor, floors and any `DEGRADED — RECOVERY ONLY` marking; root succession; where an owner-signed break-glass authorisation goes; replay interrupted install transactions |
| `gov init [--source] [--name] [--alias] [--intent] [--force] [--skip-index] [--channel] [--break-glass]` | Greenfield onboarding: kernel, lock, overlay, roots, `.gitignore`, held-out file, registry, adapters, index, doctor, conformance audit |
| `gov adopt baseline\|inventory\|classify\|map\|plan\|test-design\|review\|migrate\|verify-migration\|extract-legacy\|build-memory\|verify-memory\|audit\|status\|rollback` | Stages A0–A11 (`gov migrate …` is an alias); A3/A4 record the declared session and role as producer |
| `gov update --check [--source]` / `--apply [--source] [--approve] [--by]` / `--rollback [--break-glass] [--reason]` | Versioned, impact-checked kernel update; `--apply` needs the framework-update gate answered by the human (owner-signed); below-floor rollback needs break-glass |
| `gov doctor` | Health checks with remediation; HEALTHY/DEGRADED/UNHEALTHY |
| `gov rebuild-memory [--incremental]` | Rebuild derived memory; writes index/memory manifests (available under FREEZE_WRITES and PAUSE) |
| `gov recover [--dry-run]` | Classify interrupted mutations (CIT, migration batch, corrupt DB, claims), repair, checkpoint, freeze on UNKNOWN |
| `gov kernel verify \| trust \| override [--reason] \| reinstall [--source] [--break-glass]` | Kernel verification, trust verdict, L4 override gate, restore of the pinned release (`KERNEL_MISMATCH`, `KERNEL_PIN_REWRITTEN`) |
| `gov release build --version V [--out] [--certification S] [--evidence] [--canonical]` / `verify <dir>` | Immutable release payload + manifest |
| `gov upstream prepare <L-id>` / `submit <PKT-id> --destination <…/lessons/inbox> --approved-by <human>` | Export gate |

## Work system
`gov task create|list|show|status|claim|release|close|dag|replan` · `gov readiness check|plan <F-id>` ·
`gov gate create --question … --fields <package json> | present <HDG> | list | show <HDG> | revoke <HDG> [--reason]` ·
`gov handoff create|return` · `gov checkpoint create|latest|watchdog` · `gov claims list|sweep` ·
`gov context compile|manifest|verify [--hash]|show [--hash]|receipt --file f <TASK>` · `gov artefact show <id> | check |
lineage <id> [--direction down|up] [--depth n]` · `gov skills list|resolve <TASK>` ·
`gov route [--task|--class] [--radius] | --record <file> | --report` · `gov telemetry summary|emit`

## Health, change control and memory
`gov health run [--tier G1..G6] [--check c]… [--changed p]… [--event e] [--no-cache] [--deep] [--no-persist] | status |
checks | history [--limit n] | show <HR-id> | guard <op> [--paths p]… | currency | product [--family f]… |
skills [--skill s] [--record] [--include-deferred] | close-check <TASK> --report f` ·
`gov cit propose --proposal … [--trigger] [--targets a,b] [--manifest ops.json] | simulate|approve|reject|execute|rollback|list|show <CIT>` ·
`gov memory query "<q>" [--k] [--route] [--include-historical] | verify | freshness | rebuild | graph <node> | impact <ids>` ·
`gov memory miss --query "<q>" [--expected id]… [--detail t]` (an agent-reported retrieval miss; L1) · `gov memory failures` ·
`gov memory benchmark --candidate <c> --candidate <c> [--heldout f] [--record]` (candidates: `current`, `builtin[:dim]`,
`plugin:<id>[:dim]`, any `+rerank:<id>`) · `gov memory select <candidate> [--research RES-x] [--by who]` ·
`gov memory heldout-starter [--force]` · `gov lessons cluster [--inbox d] [--proposals d] [--write]` ·
`gov capabilities serve-embed [--reverse] [--id]` (the binary acting as an embed plugin) ·
`gov plugins register --descriptor f | unregister <id> | registry | list | health [--ping]` ·
`gov policy overrides | effective <POLICY>` · `gov adapters generate|verify` ·
`gov tools list|registry|resolve --capability c [--role r]|install --descriptor f [--execute]|health` ·
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

Mutation manifest ops (CIT): `set_status`, `set_field`, `mark_stale`, `write_file`, `move_file`, `delete_file`,
`append_record`, `regenerate_views`. Framework migration ops: `add_overlay_file_from_template`, `rename_overlay_file`,
`set_overlay_key`, `rename_overlay_key`, `delete_overlay_key`, `set_lock_field`, `require_index_rebuild`,
`regenerate_adapters`, `note`.
