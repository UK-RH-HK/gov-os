# E — Protected write paths

**Targets:**
- `governance/kernel/**`;
- `governance/trust/**`;
- `governance/framework.lock`;
- snapshots;
- recovery state;
- install journals.

**Method:**
- every file-mutation call site in `runtime/src` and `cli/src` (`fs::write|rename|remove_*|create_dir*|copy`,
  `OpenOptions`, `File::create`), 22 files;
- every subprocess spawn (`Command::new`, 11 sites);
- every git subcommand issued;
- the command register;
- external writers named by the threat model.

## 1. Inventory

Column legend: **K** kernel, **T** trust, **L** lock, **S** snapshots, **R** recovery state and journals. A cell marks
the targets the mechanism can write **without** an install-transaction token.

| # | Mechanism | 4.1.5 location | K | T | L | S | R | Revision 2 control | Gap |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Install transaction (init, adopt batch 0, update, rollback, reinstall, recover, uninstall, trust refresh, profile install) | `kernel.rs`, `lock.rs`, `update.rs`, `init.rs`, `adopt.rs` | tx | tx | tx | tx | tx | `InstallTxToken` (`18` §5) | exchanging the trust directory drops accumulated PTR statements (R2-M9) |
| 2 | CIT `write_file` / `move_file` / `delete_file` / `append_record` | `cit/mod.rs:700-745` (only `write_file` guards `governance/kernel/**`) | ✓ | ✓ | ✓ | — | — | planning refusal + GovernedFs | closed |
| 3 | CIT snapshot take and restore (`cit rollback`, `recover`) | `cit/mod.rs:586-660, 1124-1185` | ✓ | ✓ | ✓ | own | — | GovernedFs | closed |
| 4 | Adoption executor moves, deletes, `git mv -k`, `git rm --cached` | `migrations/executor.rs:19-31` | ✓ | ✓ | ✓ | — | — | classification + GovernedFs + git argument pre-validation | classification lacks `trust/` and `.tx/` today (`classify.rs:154-158`); revision 2 adds them |
| 5 | Adoption batch rollback (`adopt rollback`, `recover`) | `migrations/executor.rs:304-350` | ✓ | ✓ | ✓ | — | — | batch 0 = uninstall; batches ≥ 1 through GovernedFs | closed |
| 6 | `update --rollback` restoring from `.governance-runtime/update/<v>/` | `update.rs:348-420` | ✓ | — | ✓ | reads | — | restore pipeline (`20` §2) | **legacy `update/<v>/` snapshots stay on disk and are consumed by pre-RoT binaries** (R2-H4, P3) |
| 7 | `init --force` (kernel, lock, overlay templates) | `init.rs:217-240, 43-82` | ✓ | — | ✓ | — | — | transaction | closed for RoT-1; pre-RoT: R2-H4 |
| 8 | `kernel reinstall` | `cli/src/main.rs:853` | ✓ | — | — | — | — | transaction | closed; pre-RoT: R2-H4 |
| 9 | Migration operations including `set_lock_field` | `migrations/framework.rs`; `update.rs` `apply_update` | — | — | ✓ | — | — | lock operation removed; GovernedFs | closed |
| 10 | Indexer, adapters, tool and plugin registries, routing log, claims, telemetry, checkpoints, lessons, upstream, benchmark | `memory/indexer.rs`, `adapters.rs`, `tools.rs`, `capabilities/governance.rs`, `routing.rs:236-239`, `memory/claims.rs:36`, `observability.rs`, `lessons.rs`, `upstream.rs`, `memory/benchmark.rs` | computed paths | computed | computed | — | — | GovernedFs PPS refusal | closed |
| 11 | **Gate, decision and exception records** | `records.rs:320-328` → `spec/decisions/` (`records.rs:53`) | — | — | — | — | — | GovernedFs (outside the PPS) | **authorisation data that A2 commits and A3 or a plugin writes** (R2-M1, P2) |
| 12 | **Plugins** (subprocess, cwd = project root, no sandbox) | `capabilities/host.rs:175-190` | ✓ | ✓ | ✓ | ✓ | ✓ | none (VR-3); PPS changes detected by the next snapshot | also writes gate, decision and exception records, the overlay and the VTS — **none detected**. Plugins run *inside* `gov` commands. |
| 13 | **Tool install and uninstall commands** | `tools.rs:458-464, 503` via `util::run_cmd`, cwd = root | ✓ | ✓ | ✓ | ✓ | ✓ | none (I-46) | the commands come from the kernel tool registry and unfloored `TOOL_POLICY.auto_install_conditions` (R2-H1) |
| 14 | Product verification and test commands | `verification/` via `util::run_cmd` | ✓ | ✓ | ✓ | ✓ | ✓ | none (I-46) | as row 12 |
| 15 | Git operations by users and agents (checkout, merge, pull, reset, stash, revert) | none | ✓ | ✓ | ✓ | — | ✓ (if `.tx/` tracked) | evaluated at use (I-15) | no gate at use; stateless verifiers accept A2's choice (R2-H2); `.tx/` via Git (R2-M9) |
| 16 | External editors, agents and processes | — | ✓ | ✓ | ✓ | ✓ | ✓ | A2/A3 model; detection at the next snapshot | VR-1 |
| 17 | **Pre-RoT binaries 4.1.2–4.1.5** (their own rows 2–9) | legacy binaries | ✓ | leave in place | ✓ | ✓ | ✓ | trust-format boundary (`13` §3) | **executed: overwrite before or without refusal** (R2-H4) |
| 18 | VTS writes | `gov` (S10), A3 | — | — | — | — | — | account-database location | RS-3 / RR-3 |
| 19 | `gov kernel export <dir>` | proposed | — | — | — | — | — | output is an untrusted source | closed |
| 20 | `gov release build / attach-signature / promote` | `release.rs:9-45` | canonical repository only | | | | | producer rules (`07` §7) | out of consumer scope |

Read-only git spawns (`project.rs:248`, `kernel.rs:141`, `migrations/inventory.rs:288`) and `release.rs` `tar` do not
mutate consumer paths.

## 2. Per-target conclusion

| Target | Writers without a token | Revision 2 protection | Adequate? |
|---|---|---|---|
| `governance/kernel/**` | rows 12–17 | detection by the next snapshot → `KERNEL_TAMPERED` | yes for current binaries; **no for pre-RoT binaries** (H4) |
| `governance/trust/**` | rows 12–17; row 1 drops statements on exchange | signed content; deletion → `PARTIAL`/`STALE`/`HINT_MISMATCH` | deletion is the attack for stateless verifiers (H2); exchange loss (M9) |
| `framework.lock` | rows 12–17 | record cross-check | yes |
| Snapshots (`snapshots/<CI>/`; legacy `update/<v>/`) | anyone | authenticated and eligibility-checked on restore | yes for RoT-1. **Legacy `update/<v>/` is an active input for pre-RoT rollback** (H4) |
| Recovery state (`.tx/` journal, `.prev`, `overlay.prev`; CIT and adoption snapshots) | anyone | hints only; re-authentication | `overlay.prev` restore unguarded; `.tx/` Git status unspecified (M9) |
| Install journals | anyone | hints only | as above |

## 3. Assessment

The Protected Path Set with GovernedFs is a correct internal writer rule. RV-M1 is closed for every mechanism inside
`gov`. By design it does not constrain external processes, and the architecture relies on detection at the next snapshot.

That detection works for PPS content. It does not work for two classes of data that decide or bound trust decisions:
- **authorisation records** (gates, decisions, exceptions);
- **project-owned strengthening** (overlay).

Plugins and tool commands run inside `gov` commands and can write both undetected. Pre-RoT binaries write all of them
(R2-H4).
