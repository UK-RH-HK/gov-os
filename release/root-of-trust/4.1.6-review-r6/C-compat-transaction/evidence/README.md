# AR-0017 evidence — independent compatibility & transaction review (C) of RoT-1 revision 6 (`4106885`)

All instruments are original to AR-0017. The revision-6 installation-state predicate `c6lib.state_r6` is **encoded from the
text** of `18` §9 (state table), §9.1 (closed entry sets, including the revision-6 `governance/trust/.gitattributes`
member), §9.2 (root discovery and working-directory refusal, including the transaction area) and §5.1 (honoured journals)
at `4106885`. It does **not** import or copy the architect's LAY6 `c5lib`, review r5 C's `c5lib.state_r5`, `ST5`, `LR2` or
any pack instrument. Where the state-table rows overlap, `state_r6` records **every** matching row so a text ambiguity is
visible rather than resolved by the instrument.

The command registers (`register6.py`) are derived **twice** — from each real binary's `--help` recursion and from its own
`cli/src/main.rs` clap enums at its release commit (`git show`) — and cross-checked.

## Hygiene

Every child process runs under `env -i` with a constructed environment: `PATH`, `HOME`, `XDG_*` and `GOV_KERNEL_CACHE` in
scratch; **no other `GOV_*` variable unless a probe sets it explicitly as the object of the test** (the `P-ENV` matrix rows).
Git runs with `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL` in scratch, `GIT_OPTIONAL_LOCKS=0`, `core.hooksPath=/dev/null`.
The canonical checkout `/home/usain/Dynamic-Agentic-Engineering-OS` and every other worktree were never written. Whole-tree
snapshots record **every** entry under the project root (work tree, `.governance-runtime/`, `.git/`), the child `HOME` and
the kernel cache, by type, mode, size, SHA-256 and link count; each matrix row records a before/after **whole-tree digest**,
never a named path (Forbidden assumption: a named-path digest does not show that no write happened). No `rm -rf`/`rm -f`
shell command was used. **Disclosure:** `matrix6.py` removes each per-row scratch copy of a tree and child `HOME` with
Python `shutil.rmtree` after the row's digests are recorded, and `gitops6.py` recreates its own scratch `gitops/` directory
the same way; every such path is a copy under the AR-0017 scratch root. `c6lib.restore_slot` (entry-by-entry restore) is
present but was not used by the reported run. The architect's LAY6 `matrix5.py`, re-run unmodified for reproduction, does
the same with `shutil.rmtree` in scratch. `__pycache__` is suppressed (`PYTHONDONTWRITEBYTECODE=1`, `sys.dont_write_bytecode`).

The legacy binaries are the real `gov-4.1.{2,3,4,5}` (SHA-256 in `REVIEWED-CONTENT-DIGESTS.txt`), copied read-only into
scratch. Legacy source is read via `git show <commit>:cli/src/main.rs` at `8ad06be`/`26ab5b6`/`47d8394`/`da9c851`.

## Files

| Probe (`probes/`) | Output (`outputs/`) | What it tests |
|---|---|---|
| `c6lib.py` | — | the revision-6 predicate library (state, root discovery, whole-tree snapshot, register-safe slot restore) |
| `register6.py` | `registers6.json` | each binary's full command register, derived twice and cross-checked |
| `build6.py` | (trees in scratch) | the revision-6 layout built from a real 4.1.5 project (`08`, `26`, `18` §5.1/§8/§9.1): trees R6, R6RES, R6CRASH, R6V, L0 |
| `gitops6.py` | `gitops6.json` | layout durability: clone/shallow/partial/sparse/archive/clean/stash/worktree/checkout/restore, the untracking idiom under every ignore source, `.gitattributes` member vs autocrlf/`text=auto`/`text eol=crlf` and the `.git/info/attributes` override, case-insensitive clone |
| `matrix6.py` | `matrix6-summary.json`, `matrix6-writing-rows.json.gz`, `matrix6-rows.jsonl.gz` | the independent pre-RoT command-register matrix on the revision-6 layout |
| `struct6.py` | `struct6.json` | structural tampering against the closed entry sets (symlink/type-swap/member deletion/kernel edit/occupation removal) |
| `attrprec6.py` | `attrprec6.json` | held-out RV6-C-A08: Git attribute-precedence attempts to override the `.gitattributes` member |
| `admtx6.py` | `admtx6.json` | admission/recovery as transactional state against the pack's own revision-6 reference executor (model evidence) |
| `crashmig6.py` | `crashmig6.json` | held-out RV6-C-A15: crash after every step of the first-install layout migration (two lock-removal orders), state with the journal honoured and after the documented recovery, then real legacy 4.1.5/4.1.2 commands on each recovered tree |
| (inline, `00-REPORT.md` §Method) | `ptid-duplication.json` | executed fact for RV6-C-A16: `project_trust_id` identical across R6, a second machine, a clone, a worktree and an archive at different paths |

`reproduction/` — re-runs of prior decisive and architect instruments against revision 6, unmodified, from a scratch
`git archive 4106885` mirror (so every canonical-root or source path those instruments resolve lies in scratch):
`rerun-ADM6-admission-transactions.json`, `rerun-UW6-user-writable-install.json` (architect r6),
`rerun-RV5-D-A03.json` (review r5 synthesis), `rerun-r5C-admit_tx.json` (review r5 C, the LAY6 copy), and
`LAY6-reproduction.json` (the architect's LAY6 chain `register5` → `build5` → `gitops5` → `matrix5 --focus --workers 16` →
`props6`, compared field by field with the committed LAY6 and review r5 C outputs).

`REVIEWED-CONTENT-DIGESTS.txt` — SHA-256 of every reviewed pack file (`release/root-of-trust/4.1.6/**`, `D-0008`,
`ARCH-0002`) as the git blob content at `4106885dadebac55596067a2586cf4d3097fc025`, plus the four legacy binary digests.

## Evidence classes

- **E** executed with the real 4.1.2–4.1.5 binaries and/or real Git 2.43.0.
- **M** the pack's own revision-6 reference executor `gov_admit_reference_r6.py` exercised (architecture evidence, not the
  product; the RoT-1 install/transaction machinery and `gov-admit` are unimplemented).
- **D** design reading of the pack at `4106885`.
