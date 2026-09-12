# gov command reference

Global flags: `--root <path>` (default: discovered upwards from cwd), `--json` (envelope `{ok, command, result|error, session}`),
`--session <id>` (or `$GOV_SESSION`), `--role <role>` (or `$GOV_ROLE`). Exit codes (API-0002): 0 ok · 1 governance error ·
2 usage · 3 verification failed/unhealthy · 4 blocked by control state or human gate.

## Human surface (framework §34)
| Command | Purpose |
|---|---|
| `gov status` | Reconstruct current governed state for a fresh agent (framework, project, control, memory freshness, DAG, gates, open CITs, latest checkpoint, next action, read list) |
| `gov continue [--claim]` | Present pending gate text, pick the next runnable task (longest chain first), compile its context packet, resolve skills and routing; optionally claim |
| `gov decide <HDG> --option <id> [--by] [--rationale]` | Answer a presented gate → decision record, unblock tasks, link CIT |
| `gov audit [--deep] [--family f]… [--no-persist]` | Governance suite (17 families) → audit record with inputs/result hashes; exit 3 when UNHEALTHY |
| `gov pause` / `gov freeze-writes` / `gov cancel-agents` / `gov resume` | Emergency controls honoured by every mutating operation |
| `gov intent "<text>"` | Deterministic natural-language routing to a plan and concrete commands |

## Lifecycle
| Command | Purpose |
|---|---|
| `gov init [--source] [--name] [--alias] [--intent] [--force] [--skip-index]` | Greenfield onboarding: kernel, lock, overlay, roots, `.gitignore`, held-out file, registry, adapters, index, doctor, conformance audit |
| `gov adopt baseline|inventory|classify|map|plan|test-design|review|migrate|verify-migration|extract-legacy|build-memory|verify-memory|audit|status|rollback` | Stages A0–A11 (`gov migrate …` is an alias) |
| `gov update --check [--source]` / `--apply [--approve --by]` / `--rollback` | Versioned, impact-checked kernel update with declarative migrations |
| `gov doctor` | 24 health checks with remediation; HEALTHY/DEGRADED/UNHEALTHY |
| `gov rebuild-memory [--incremental]` | Rebuild derived memory; writes index/memory manifests |
| `gov recover [--dry-run]` | Classify interrupted mutations (CIT, migration batch, corrupt DB, claims), repair, checkpoint, freeze on UNKNOWN |
| `gov kernel verify|reinstall [--source]` | Kernel immutability check / restore |
| `gov release build --version V [--out] [--certification S] [--evidence] [--canonical]` / `verify <dir>` | Immutable release payload + manifest |
| `gov upstream prepare <L-id>` / `submit <PKT-id> --destination <…/lessons/inbox> --approved-by <human>` | Export gate |

## Work system
`gov task create|list|show|status|claim|release|close|dag|replan` · `gov readiness check|plan <F-id>` ·
`gov gate create|present|list` · `gov handoff create|return` · `gov checkpoint create|latest|watchdog` ·
`gov claims list|sweep` · `gov context compile <TASK>` · `gov skills list|resolve <TASK>` ·
`gov route [--task|--class] [--radius] | --record <file> | --report` · `gov telemetry summary|emit`

## Change control and memory
`gov cit propose --proposal … [--trigger] [--targets a,b] [--manifest ops.json] | simulate|approve|reject|execute|rollback|list|show <CIT>` ·
`gov memory query "<q>" [--k] [--route] [--include-historical] | verify | freshness | rebuild | graph <node> | impact <ids>` ·
`gov memory benchmark --candidate <c> --candidate <c> [--heldout f] [--record]` (candidates: `current`, `builtin[:dim]`,
`plugin:<id>[:dim]`, any `+rerank:<id>`) · `gov memory select <candidate> [--research RES-x] [--by who]` ·
`gov memory heldout-starter [--force]` · `gov lessons cluster [--inbox d] [--proposals d] [--write]` ·
`gov gate create --question … | present <HDG> | list` · `gov capabilities serve-embed [--reverse] [--id]` (the binary acting as an embed plugin) ·
`gov adapters generate|verify` · `gov tools list|registry|resolve --capability c [--role r]|install --descriptor f [--execute]|health` ·
`gov capabilities ecosystems|plugins|invoke --plugin id --inputs json` · `gov verify governance|product` · `gov version`

Authority: every mutating command checks the session role's level (L0–L5) against
`AUTHORITY_POLICY.authority_levels_required` and fails with `AUTHORITY_DENIED` (or `UNKNOWN_ROLE`). Gates are answered
only after `gov gate present` (`GATE_NOT_PRESENTED` otherwise); `gov adopt migrate --gate-answer` is deprecated and
ignored (a note is returned). `gov task close` refuses `MUTATION_SCOPE_VIOLATION`, `INDEX_PIN_MISMATCH` and
`INDEX_STALE`. Retrieval/index errors: `EMBEDDER_UNAVAILABLE`, `EMBEDDER_MISMATCH`, `EMBEDDER_BAD_OUTPUT`,
`RERANKER_UNAVAILABLE`, `RERANKER_MISMATCH`; plugin host: `PLUGIN_TIMEOUT`, `PLUGIN_BAD_RESPONSE`,
`PLUGIN_PROTOCOL_MISMATCH`, `PLUGIN_ERROR`.

Mutation manifest ops (CIT): `set_status`, `set_field`, `mark_stale`, `write_file`, `move_file`, `delete_file`,
`append_record`, `regenerate_views`. Framework migration ops: `add_overlay_file_from_template`, `rename_overlay_file`,
`set_overlay_key`, `rename_overlay_key`, `delete_overlay_key`, `set_lock_field`, `require_index_rebuild`,
`regenerate_adapters`, `note`.
