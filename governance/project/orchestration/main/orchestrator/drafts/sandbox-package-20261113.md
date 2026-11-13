# SANDBOX-1: the workers' OS sandbox — what was decided, what removing it takes, what it protects, what it costs

Prepared 2026-11-13 by a read-only research helper for the Wave 2 CTO, for the owner. Nothing was changed. Paths are
relative to `/home/usain/Dynamic-Agentic-Engineering-OS` unless they start with `~`. "R:" means
`docs/DECISION_REGISTER.md:<line>`. **Measured** means a count or figure I made or found in a file. **Estimated** means
a lead's own guess or my inference, and is marked as such.

## 0. In one paragraph

`gov launch` puts every worker in Claude Code's bubblewrap sandbox. It confines writes to the worktree, the session's
own `/tmp/gov-launch-*` folder, its run folder and the reranker's log. It allows no network domain, refuses Unix
sockets, hides the held-out oracle from Bash, and runs each command in its own pid namespace. Since DEC-953 item 2
lifted the live guard to five rules, **the sandbox is the only wall for writes outside the worktree**. That covers
other worktrees, `~/workspace`, `~/EXAMIN APP`, `~/.local/bin/gov` (the guard's pinned judge), `~/.claude`, `.git/hooks`
and `/mnt/c`. It is also the only wall for network egress, for killing other processes and for opaque scripts.

The frictions are real but mostly cheap to fix:
- **Stated cost:** about 261 minutes of lead and worker time since 11-01, in 56 return rows, plus a few lost runs.
- **Most of it is a brief problem:** briefs name `/tmp/...` or `.gov-runtime/scratch/<role>/` instead of `$TMPDIR`
  (130 + 34 min).
- **The costly part is search quality.** 399 sandboxed searches went unranked from 11-09 to 11-13. Without the
  reranker, hit@5 on the 138 drops 107 → 95. **Measured.**

The ACT the owner approved this morning (DEC-1163 (9): the sandbox may write `~/.cache/gov-os`) **will not restore
ranked search**. The CTO's own probe shows that with that write allowed, the next error is `EPERM` on the socket
(§6.1).

**Recommendation:** (b) light. Fix the briefs now, probe a loopback route once, keep the sandbox. Confidence: high for
keeping the sandbox, medium for the loopback fix.

---

## 1. What the owner decided (exact lines)

Status as the register states it. "In force" means not superseded and not marked DONE.

| Id | Date | Status | The decision's own lines (quoted) | Changed or superseded? |
|---|---|---|---|---|
| DEC-152 (R:1391-1405) | 2026-10-03 | ACCEPTED, "Scoped by: DEC-161" | "The OS sandbox is the outer wall for everything a Bash command does: writes outside the repository, installs, network, and reads of hidden paths. Its configuration comes from the launcher through `--settings`, never from the repository: enabled, `failIfUnavailable: true`, `allowUnsandboxedCommands: false`, and network `strictAllowlist`." · "The qualification oracle is hidden from Bash by the sandbox, and from the file tools by a `Read` deny rule." | In force (scoped to workers by DEC-161) |
| DEC-153 (1) (R:1408-1411) | 2026-10-03 | ACCEPTED, "Changed by: DEC-209" | "**The launcher** (`gov launch`, or equivalent). It builds per-role `--settings` (sandbox block plus role `Edit` deny rules), sets `GOV_ROLE` and `GOV_TICKET`, and refuses to start unless the sandbox is on, strict and fail-closed." | In force for item (1) |
| DEC-158 (R:1441-1450) | 2026-10-03 | ACCEPTED | "Engineer, independent test designer and independent auditor get an empty allowlist." · "The orchestrator is unrestricted, being unsandboxed." · "WebSearch and WebFetch run outside the sandbox (EXP-001)" | In force |
| DEC-159 (R:1452-1455) | 2026-10-03 | ACCEPTED | "The launcher sets a per-session temp directory for worker sessions." | In force |
| DEC-161 (R:1462-1470) | 2026-10-03 | ACCEPTED, "Scopes: DEC-152, DEC-153" | "The launcher applies the sandbox to worker sessions only: engineer, independent test designer, independent auditor, and research or experiment work … The repository's settings carry no sandbox block." · "The launcher's acceptance tests must show: that a launched worker is sandboxed; that its network profile applies" | In force |
| DEC-233 (R:2218-2222) | 2026-10-04 | ACCEPTED (orchestrator, delegated) | "`gov launch` refuses to start … when the repository's `.claude/settings.json` or `.claude/settings.local.json` carries a `sandbox` key, because the CLI may merge repository settings into the ones the launcher builds." | In force |
| DEC-386 (R:3906-3911) | 2026-10-05 | ACCEPTED, "Changed by: DEC-392" | "The launcher gets a `product-spec` role with an empty network allowlist, so product-spec workers are sandboxed too." | In force |
| DEC-769 (R:8425-8431) | 2026-10-18 | ACCEPTED, "Changed by: DEC-953 (item 2)" | "**Then leads run sandboxed** … **The orchestrator's own session stays unsandboxed.**" | Effectively reversed for leads by DEC-1128 (4) ("the leads are not sandboxed") |
| DEC-779 (R:8532-8538) | 2026-10-18 | **DONE** (DEC-1098 (3)) | "Any further guard text-parsing finding becomes a list row, not a new round, unless a launched, sandboxed worker can reach it (a true fail-open through the operating-system sandbox)." | DONE: its rule rests on DEC-789 (3) below |
| DEC-789 (R:8654-8664) | 2026-10-18 | ACCEPTED | "(b) now … its lead confirms that the main tree, every other worktree and every acceptance folder are unchanged" (the tripwire) · "The next worker any lead starts is launched through `gov launch <role> <ticket>`, sandboxed." · "(3) DEC-779's 'launched, sandboxed worker' applies only to workers started through `gov launch`. Until all workers are, a guard hole that a worker can reach through a script is fixed, not rowed." | In force |
| DEC-794 (2) (R:8698-8704) | 2026-10-18 | **DONE** (DEC-1098 (3)) | "EXAMIN's copy adoption (W2-27) does not start unless sections (a) and (d) come back green: (a): workers sandboxed through `gov launch`" | DONE, but the gate is re-homed to W2-56's close and is in force through DEC-799 (4) and DEC-1083 D9-FATES (`docs/probes/DAEO-wnnz/PR-DAEO-wnnz.md:157-177`, judged **GREEN** 2026-11-13) |
| DEC-799 (R:8740-8749) | 2026-10-19 | ACCEPTED | "(1) … the sandbox's write list limited to the ticket's allowed paths plus git's folders; no placeholder file can reach a commit." · "(2) **Never option (b)** (adding `/tmp/gov-cbm-<uid>` to the sandbox's write list)." · "(3) … every worker whose suites do not need the code graph, test designers included, starts through `gov launch`, sandboxed. Only a worker whose suites need it falls back to the old launch form, with the tripwire" · "(4) **W2-27 starts only after W2-56 has closed** and section (a) of the quality-control check is green (DEC-794)." | Item (1)'s "write list = allowed paths" was not built: W2-56 S2 keeps "today's" list (`.tickets/DAEO-wnnz.md` KPI S2; DEC-1112 (1)). The rest is in force |
| DEC-820 (4) (R:8979) | 2026-10-19 | ACCEPTED, standing | "**Writes stay strictly limited,** by the sandbox and the guard, to the agent's own ticket paths." | In force. Its guard half is not live: the live hook has no allowed-paths rule since DEC-953 item 2 (§3) |
| DEC-873 (2) (R:9540-9545) | 2026-10-20 | ACCEPTED, "Changed by: DEC-953 (item 2)" | "The launcher adds no OS-level Read rule for (c) or (d), because running a test means reading it. **The held-out material's rules (b) stay in the sandbox as well**" | In force |
| DEC-953 item 2 (R:11865) | 2026-10-30 | ACCEPTED, standing | "**The guard keeps four rules:** an implementer never writes acceptance tests; no reads of the hidden half of an evaluation set or the held-out material; no reads of secrets; no installs without the owner. Everything else in the guard is lifted, the command forms included." | In force (the live hook has five rules plus 2b-2d, `.claude/hooks/pretooluse.py:1-44`) |
| DEC-1034 (1) (R:12851-12853) | 2026-11-02 | ACCEPTED (delegated) | "The `gov launch` sandbox refuses `socket(AF_UNIX)` (EPERM) … W2-112's engineer starts unsandboxed in that form … Not a new exception to the sandbox: the same class as the code graph's." | In force |
| DEC-1035 (2) (R:12859-12861) | 2026-11-02 | ACCEPTED | "P-W2-112-T2 (c) now: sandboxed sessions fall back (a GPU slot or unranked, named) while the shared reranker cannot be reached from the sandbox; and (a) as a follow-up ticket filed now, W2-127 (`DAEO-1vka`): the shared reranker's one socket path allowed in the launch sandbox, nothing else" | (a) built as W2-56 S8, inert on Linux; reach deferred by DEC-1114 |
| DEC-1064 (2) (R:13140-13142) | 2026-11-03 | ACCEPTED | "**No private embedder in the launch sandbox:** … so sandboxed workers run no `gov retrieve` (grep and the Read tool instead) and no test that starts a real embedder, reranker or model, until W2-127 makes the shared servers reachable from the sandbox" | In force. **It conflicts with practice:** 399 sandboxed searches ran from 11-09 to 11-13 (§5), and DEC-836 (2) puts `gov retrieve` in every worker brief (W2-152's return flags the conflict, `log/W2-152-A5-resume-1112.json`) |
| DEC-1065 (1) (R:13149-13151) | 2026-11-03 | ACCEPTED, standing | "when the shared GPU embedders cannot be reached (the launch sandbox included), the search reports its semantic part unavailable, named, and answers by keywords" | In force |
| DEC-1098 (4) (R:13920-13923) | 2026-11-09 | ACCEPTED | "**Sandboxing and the guard (K6, W2-56): an experiment before the leads are sandboxed.** The bar: every agent action judged right, no false refusal and no wrong allow, 100 %. Two set-ups … If the guard with the sandbox cannot reach the bar, the path-map guard alone is kept." | Narrowed by DEC-1112 (1) |
| DEC-1099 (1) (R:13934-13944) | 2026-11-09 | ACCEPTED | "Q4: the CTO's session stays unsandboxed, judged as in set-up A." · "Q9: the reranker socket and the WSL socket in the bar, web domains out." | Set-up B dropped by DEC-1128 (4) |
| DEC-1101 (2) (R:13983-13989) | 2026-11-09 | ACCEPTED, standing | "memory's own search, run outputs, the CTO's scratch and the other sessions' folders denied to them by their settings, the guard, and the sandbox once proven" | In force. The walls do not use the workers' sandbox today (§3) |
| **DEC-1112 (1)** (R:14134-14139) | 2026-11-09 | ACCEPTED; "Changed by: DEC-1128 (4) … DEC-1128 (2)" | "**The sandbox experiment: (a).** Set-up A (the path-map guard alone) measured fully, as declared, beside D-10; set-up B becomes a Wave 3 row, built by a different route. W2-56 builds on the path-map guard alone, with today's launcher sandbox for workers unchanged." | Changed by DEC-1128 (4): set-up B dropped |
| **DEC-1114 (1)** (R:14164-14171) | 2026-11-09 | ACCEPTED | "**(b).** S8's reach (a sandboxed session connecting to the shared reranker's one socket) and S10 (its measurement) are deferred to Wave 3, as a ticket to give sandboxed workers ranked search without opening every Unix socket (`docs/plan/WAVE_3_PARKING.md` W3-P28). S8's settings-level form (the one path, nothing wider) stays built, inert on Linux. Until then a sandboxed worker's search is unranked, named and counted (S11). S9 and F4 stand unchanged. The rest of W2-56 merges now; leads and in-session agents, which are not sandboxed, keep ranked search." | In force |
| **DEC-1128 (4)** (R:14412-14414) | 2026-11-11 | ACCEPTED, item (4) **standing** | "**No more sandbox work (DEC-1112 (1) changed):** set-up B is dropped entirely, not a Wave 3 row; the leads are not sandboxed; the path map and the guard are the controls. Set-up A (the guard alone) stays: it is the guard's measurement for the 100 % bar. The workers' existing launcher sandbox stays as it is." | In force. **The owner's latest standing word on the sandbox** |
| DEC-1142 (9) (R:14673-14674) | 2026-11-12 | ACCEPTED, standing | "**The two-refusal stop covers the same effect in another form** (standing): a session refused twice for an action stops and says so; it does not reach the same effect by another command, form or file." | Read with DEC-1146 (1) (R:14748-14749): "The two-refusal rule (DEC-1142 (9)) covers permission refusals: the guard, the sandbox, a hook." |
| DEC-1163 (9) (R:14935) | 2026-11-13 | ACCEPTED | "**Yes to two ACTs:** the sandbox's write to `~/.cache/gov-os` (sandboxed workers' unranked searches) and the dispatcher's outside-slot check …" | Approved, not applied. **The probe shows it will not give ranked search (§6.1)** |

**The plan's rows:**
- **W3-P28** (`docs/plan/WAVE_3_PARKING.md:34`): "**A ticket (DEC-1114 (1)).** Ranked search for sandboxed workers
  without opening every Unix socket … Routes to weigh: a TCP loopback port on the sandbox's allowed list, a broker the
  sandbox already allows, or the CLI fixed upstream."
- **W3-P29** (`:35`): "the CLI's own `.git/config.lock` placeholders … fail a git command in a concurrently sandboxed
  worker; (a) a clone per concurrently sandboxed worker, or (b) the CLI fixed upstream. Not reached today: the CTO
  launches workers one at a time."
  - **Its premise is out of date:** DEC-1157 removed the one-per-batch holds, so sandboxed workers now run
    concurrently.

**DECIDED-NOT-DONE** (`governance/project/orchestration/packages/DECIDED-NOT-DONE.md`):
- Rows 25, 28, 29 and 66 cover the sandbox-and-guard experiment; set-up A waits on ACT-W2-149-INSTALL-1 (`:107`).
- Row 80 is "W3-P28 … DONE (parked) 11-09" (`:129`).
- Row 81 holds W2-56's review rows, with R6 parked as W3-P29 (`:130`).
- The DEC-1163 (9) ACT has no row yet.

## 2. What removing it would take

### 2.1 Code and settings

| Where | What it does today | Change for removal |
|---|---|---|
| `src/gov/launch/launcher.py:212-218` (`build_settings`) | The `sandbox` block: enabled, `failIfUnavailable`, `allowUnsandboxedCommands: false`, `network` from `sandbox.network()` | Drop the block. Keep `permissions.deny` (`:186-198`), which binds the file tools without the sandbox |
| `launcher.py:461-464`, `:524-527` | `sandbox_faults` refuses a non-strict block, twice | Remove both refusals, or invert them to refuse a block |
| `launcher.py:465-471` | Writes the placeholder names into the shared `info/exclude` (W2-56 S4) | No longer needed |
| `launcher.py:520-524` | Per-session `TMPDIR`; `settings["sandbox"]["filesystem"] = sandbox.filesystem(...)` | Keep `TMPDIR` (DEC-159); drop the filesystem block |
| `src/gov/launch/sandbox.py` (231 lines) | `network`, `filesystem`, `faults`, placeholders | Mostly dead code. `faults()` refuses `allowAllUnixSockets` as an unknown key (`:221-223`) |
| `src/gov/launch/environ.py` | The cleaned environment (S5) | Keep. It is not part of the sandbox |
| `.gov-runtime/scratch/orchestrator/tools/launch_worker.sh` | Step 4 (`:18-20`): the step-0 line injected into every brief (`:157-159`); the refusal when a `.sandbox-trial-<ticket>` file already exists (`:162`); the `sandbox_faults` dry run (`:164-180`); "SANDBOX BREACH" after the session (`:58`) | All four go. Step 0 (a) would otherwise **succeed** and report a breach on every run. The tripwire (`:56-57`, DEC-789 (1)) stays. It is a committed tool: check `class-rules.yaml` for whether the edit goes by ACT |
| `.gov-runtime/scratch/orchestrator/briefs/EMG-d4b-launched.md:6-8` | Step 0: (a) a write to `~/gov-os-worktrees/.sandbox-trial-<id>` must fail | Delete |

Size, **estimated:** about 40-60 lines of product code, one FULL ticket (engineer plus independent test designer).

### 2.2 Tests that assert sandboxing (they go red and need a designer's revision)

These files reference `sandbox_faults`, `failIfUnavailable`, `allowUnsandboxedCommands`, `allowWrite`,
`allowUnixSockets` or `.sandbox-trial`. **Measured** by grep.
- **W1-46:**
  - `test_w1_46_sandbox_settings.py` (11 tests). README S1 and F1: "refuses … unless the settings it built have the
    sandbox enabled".
  - `test_w1_46_live_sessions.py` (15). These are live checks, for example S11: "an opaque bash write to the …"
    fails.
  - `_research_fence.py` (9), `_protected_trees.py` (7), `_runtime_and_ln.py` (12), `_role_settings.py` (9: the empty
    allowlist), `_research_allowlist.py` (11), `_held_out.py`, `_launch_refusals.py`, `_guard_wiring.py`,
    `_bypass_and_added_directories.py`, and `w1_46_support.py`.
- **W1-28:** `test_w1_28_launch_product_spec.py` (23 tests, 33 sandbox lines).
- **W2-50:** `test_w2_50_launcher.py` (10 tests, 76 sandbox lines: the run folder on the write list), plus the
  review-finding files.
- **W2-56:**
  - `test_w2_56_sandbox_block.py` (13).
  - `test_w2_56_real_sandbox.py` (4 real cases: S2 refused writes, S9 second socket, S7, S13).
  - `_session_reranker.py` (2), `_placeholders.py` (2), `_todays_refusals.py` (4), `w2_56_sandbox_support.py`.
- **W2-20:** `test_w2_20_launch.py`.
- **Unit tests:** `tests/unit/launch/test_launcher.py`, `test_w2_56.py`, `test_w1_28.py`, `test_runs.py`,
  `test_w2_136_plan_check.py`, and `tests/unit/resources/test_w2_20_round3.py`, `test_w2_20_unit_launch.py`.
- **Total, estimated:** about 60-90 acceptance cases across 6 folders.

**W2-56's KPI lines that state sandboxing** (`.tickets/DAEO-wnnz.md`, success and failure lists):
- S2: "The sandbox's write list stays today's".
- S4: placeholders.
- S7: start lock against `.git/*.lock`.
- S8, S9: "a planted sandboxed session that opens another Unix socket is refused".
- S10 (deferred), S11, S13, S15.
- F1, F2: "A launch whose sandbox cannot be built starts", F4, F5.
- W2-56 is closed. Its probe judged DEC-794's gate (a) GREEN on exactly these points
  (`docs/probes/DAEO-wnnz/PR-DAEO-wnnz.md:157-168`).

### 2.3 The Contract and the decisions that would need superseding

**Contract v4** (a closed specification, so DEC-105 applies: CIT-P, review and the owner):
- **CAP-61** "Worker session launcher and OS sandbox" (`docs/contract/CONTRACT_v4.md:932-937`): "`gov launch` refuses
  to start a worker session unless the sandbox is enabled, strict … and fail-closed".
- **CAP-49.b** (`:776`): the oracle "hidden from Bash by the sandbox".
- **CAP-58.d** (`:899`): "the OS sandbox stops a Bash write outside the repository".
- **CAP-25.e** (`:411`): the research install fence, which "the sandbox's write fence enforces".
- **CAP-25.f** (`:412`) and **CAP-40.d** (`:637`).

**Decisions:**
- **To supersede or amend:**
  - DEC-152 and DEC-161 (the outer wall and its scope).
  - DEC-153 (1): refuses unless the sandbox is on.
  - DEC-158: its empty allowlists are only enforced by the sandbox.
  - DEC-386.
  - DEC-820 (4): "by the sandbox and the guard".
  - DEC-873 (2): "held-out rules stay in the sandbox".
  - DEC-799 (3)-(4) and DEC-794 (2)(a): **W2-27's gate (a)**, "workers sandboxed through `gov launch`", for EXAMIN's
    copy.
  - DEC-1112 (1) and **DEC-1128 (4)**: "The workers' existing launcher sandbox stays as it is" (standing, 2026-11-11).
  - DEC-1101 (2): "the sandbox once proven".
- **Made moot:** DEC-1114 (1), W3-P28, W3-P29, DEC-1035 (2) and DEC-1163 (9)'s ACT.
- **Knock-on through DEC-789 (3):** every guard hole a worker can reach through a script becomes "fixed, not rowed".
  - The live guard lets every write it cannot resolve through, by design: ACT-GUARD-FIX-4,
    `.claude/hooks/pretooluse.py:48-53`.
  - So removing the sandbox reopens guard hardening for the six roles' workers. **Estimated:** several guard rounds,
    or an owner decision to accept those holes as rows.

## 3. What the sandbox protects, and which other wall also covers it

**The other walls today:**
- **The live guard** (`.claude/hooks/pretooluse.py:1-53`) has these rules:
  - rule 1: the implementer never writes acceptance tests;
  - rule 2: no reads of the hidden halves or held-out material;
  - 2b: the sets root's hidden folders;
  - 2c: named sessions' hidden folders;
  - 2d: the operator's folder and the call log, writes refused;
  - rule 5: reviewers write only their records;
  - rule 3: no reads of secrets;
  - rule 4: no installs without the owner;
  - catastrophic `rm`;
  - role reads from the path map.
- **What the guard does not do:**
  - It judges shell text. Rules 1 and 5 "judge only the writes it resolves: a write whose target the guard cannot
    work out is let through" (`:49-51`).
  - It has **no rule on writes outside a ticket's `allowed_paths`, no network rule and no kill rule** (grep of the
    hook: no `allowed_paths`, `network`, `kill`, `workspace` or `EXAMIN`). "The product's full guard … is not wired
    here" (`:45-47`).
  - This contradicts CLAUDE.md's "It refuses writes outside a ticket's scope". The live hook stopped doing that with
    DEC-953 item 2.
- **The worker's `--settings` permission denies** (`launcher.py:173-198`) bind the **file tools only** once the sandbox
  is off:
  - `Edit` on `.gov-runtime/` outside scratch, on `tests/acceptance/**` (all but the test designer), `.tickets/**` and
    `.claude/**`;
  - `Read` on the held-out paths.
  - The CLI turns a `Read` rule into an OS read denial for Bash only when the sandbox is on (DEC-873 basis,
    R:9541).
- **The repository's `.claude/settings.json` deny list:** `Bash(sudo:*)`; `Edit` on `*.key`, `*.pem`, `.env*` and
  `config/secrets*`; `Read` on the oracle.
- **Detective checks after the fact:**
  - the tripwire, which covers the main tree and `~/gov-os-worktrees/*` (HEAD, `git status`, acceptance hashes),
    `tools/tripwire.py:1-8`;
  - the landing check G-1, which requires `Role: independent-test-designer` on commits touching `tests/acceptance/`;
  - the close's tests in a clean clone, review, gitleaks;
  - the operator's freeze gate in `.git/hooks/reference-transaction:5-12`.

| Protection the sandbox gives a worker's Bash | Sandbox source | Other wall that also covers it | Without the sandbox |
|---|---|---|---|
| Writes outside the worktree (OS-level, opaque scripts included) | `sandbox.py:109-112`: allowWrite = temp, run folder, rerank.log; PR-DAEO-wnnz.md:62-64 (S2 real case: a script's write into a sibling worktree and `tests/acceptance/` refused) | Guard: none for scope. Catastrophic `rm` for `rm` forms only (`pretooluse.py:38-41`) | **None for writes: only the sandbox** |
| Other worktrees (write) | same | Guard rule 1 for their `tests/acceptance/` (resolved writes only); tripwire detects afterwards; review and landing | Detection only (tripwire), not prevention |
| Other worktrees (read) | Not covered: reads are open (DEC-820) | Guard role reads (G-14) for the counterpart's files | Unchanged |
| `~/workspace`, `~/EXAMIN APP` (the owner's repositories) | Write list | Catastrophic `rm` (text) only; the tripwire does not look there | **Only the sandbox** (for anything but a plain `rm`) |
| `~/.local/bin/gov` and its site-packages (the pinned judge the guard imports, `pretooluse.py:45`), `~/.local/bin/claude`, `~/.claude/settings.json`, `~/.bashrc`, `~/.gitconfig` | Write list | None | **Only the sandbox.** A worker's script could rewrite the guard's judge or add user-level hooks that affect every session, the CTO's included |
| The worktree's own `.claude/hooks/` (the guard's file), `.tickets/`, `.gov-runtime/` outside scratch | Literal `Edit` deny rules turned into read-only binds (`launcher.py:139-181`) | The same `Edit` denies bind the file tools; diffs show in review and landing | Bash writes free; a script could disable the session's own guard hook |
| `tests/acceptance/**` (MR-3) for the engineer | Read-only bind (S2 real case) | Guard rule 1 (resolved writes); `Edit` deny; tripwire; G-1 landing trailer | Opaque writes caught only after the fact, by tripwire and G-1. A forged `Role:` trailer is not caught by G-1 |
| Shared `.git` config and hooks (operator freeze gate `.git/hooks/reference-transaction`) | The CLI's own git-folder protection (its `.git/config.lock` placeholder, W2-56 P-S7, `.tickets/DAEO-wnnz.md:155`). `.git/hooks` was not verified here | None | **Only the sandbox** (inferred) |
| Network egress (curl, pip, git push, exfiltration) | `strictAllowlist: true`, `allowedDomains: []` for engineer, test designer, auditor and product-spec (`sandbox.py:104-106`, DEC-158) | Guard rule 4 refuses install commands (text); `Bash(sudo:*)`. WebFetch and WebSearch are not in workers' `--allowedTools` (`launch_worker.sh:45-48`) | **Only the sandbox** for a script's network use |
| Unix sockets (AF_UNIX refused, EPERM: `rerank.py:144`; S9 real case) | Seccomp filter; only the reranker's path is allowed, and that entry is inert on Linux | None | Open: the reranker (good), and also the WSL interop socket, ssh-agent and the CLI's sockets |
| WSL interop (running Windows `.exe`) and `/mnt/c` | AF_UNIX refusal plus write list; DEC-1099 Q9 put "the WSL socket in the bar". `/proc/sys/fs/binfmt_misc/WSLInterop` exists (checked) | None | **Only the sandbox.** An unsandboxed script can run Windows programs outside every Linux control |
| Killing other processes (CTO, dispatcher, reranker, Ollama, other leads) | Each sandboxed command runs in a pid namespace of its own (`tests/acceptance/W2-56/README.md:392-394`: "pids 4 and 5 seen here") | DEC-1073 (4) "waits and stops by process id only" is a rule for agents, not a wall | **Only the sandbox** |
| Held-out oracle (`~/gov-os-workbench/qualification-oracle`) against an opaque Bash read | `Read(/<path>/**)` becomes an OS read denial (`launcher.py:198`; CAP-49.b; DEC-873 (2)) | Guard rule 2 (text); `Read` deny in both settings files for the file tools | Opaque forms (a built path in a script) are caught only by text reading, which they evade |
| Hidden halves of evaluation sets, the sets root (2b), session-hidden folders (2c) | **Not covered:** DEC-873 (2), no OS Read rule for (c) and (d) | Guard rules 2, 2b, 2c (text) | Unchanged |
| Secrets (reads) | **Not covered:** no denyRead for secrets in the launcher's block | Guard rule 3 (text); `Edit` denies for writes; gitleaks at the close | Unchanged for reads. Exfiltration over the network loses its only wall (row "Network") |
| Operator folder `~/gov-os-operator`, call log `~/.gov-os/guard-calls` | Write list | Guard 2d (resolved writes; "one it cannot work out is let through", `pretooluse.py:23-29`) | Opaque scripts: none |
| Installs (pip `--user`, npm) | Write fence plus no network (CAP-25.e, DEC-163) | Guard rule 4 (text); `sudo` denied | Text rule only |
| The evaluation writers' walled sessions | Not the workers' sandbox: own `wall_hook.py` under restricted mode (`governance/project/path-map.yaml:636-641`) | Their walls | **Unchanged.** Removing the workers' sandbox does not touch them |
| Write scope inside the worktree (outside `allowed_paths`) | **Not covered:** the whole worktree is writable | None live. Review, landing and the close's scoped tests | Unchanged |

**Already accepted elsewhere:** leads (orchestrator sessions, Opus) run with exactly this exposure today, by decision
(DEC-1128 (4); `PR-DAEO-wnnz.md:170-173`). Removing the workers' sandbox would extend it to every worker. Under
RUBRIC-2 most workers now run on Sonnet (`launch_worker.sh:118-134`), and many run at once since DEC-1157.

## 4. What its frictions have cost (since 2026-11-01)

Sources:
- the 168 lead returns since 11-01 in `.gov-runtime/scratch/orchestrator/log/*.json`;
- the worktree worker logs;
- `~/.cache/gov-os/rerank.log`;
- the register and CHECKPOINT.

The minutes are each lead's own `brief_gaps` or refusal-row figure, summed by my script. They are **lead estimates,
recorded**. I excluded rows about harness or role permissions (for example "the reviewer was launched without
Write").

| Friction | Returns naming it (measured) | Minutes stated | Runs lost or moved (from the returns) | Example sources |
|---|---|---|---|---|
| `/tmp` and the brief's TMPDIR (`/tmp/gov-os-lead-<W2>` etc.) read-only; only the session's own `$TMPDIR` is writable | 41 returns, 29 tickets | 130 (27 rows, 20 tickets) | W2-170: "the engineer lost about two runs"; pytest junk written into worktrees (W2-97, W2-123, W2-55) | `log/W2-104-A5-run1-ten.json`, `W2-160-A5-run3.json` (10 min), `W2-126-A5-run1.json` (10), `W2-122-A5-r2-nok5.json` (10), `W2-97-A5-run1-dec979.json` (10) |
| Write tool refused on `.gov-runtime/scratch/<role>/` in the worktree, which briefs named. Leads attribute this to the sandbox; it may be the launcher's deny patterns (uncertain) | 9 rows, 6 tickets | 34 | W2-175: "ps-2's whole run" (20 min) | `W2-175-A5-run1.json`, `W2-11-A5-r6-resume.json`, `W2-86-A5-run1.json` |
| `gov retrieve` in the sandbox: the network proxy blocks `ollama.com`, so it hangs 2-5 min or the semantic route is "no embedder" | 14 returns, 11 tickets | 34 (9 rows) | Workers searched nothing (W2-97: "hung 2 to 5 minutes and returned nothing for both workers") | `W2-114-A5-run2-dec986.json`, `W2-97-A5-resume-dec985.json` (6 min, measured), `W2-13-A5-run1-dec991.json` (10, measured), `brief-gaps.md:10`, `CHECKPOINT.md:991`, `:1100` ("trace the sandbox's `ollama.com:443` denials") |
| AF_UNIX refused (reranker tests, stand-in sockets) | 6 returns (helper count) | 30 (W2-112) | W2-112's engineer moved unsandboxed (DEC-1034); W2-146 eng-1 saw "20 reds … the reranker socket was refused"; W2-145: `gov accept` 37 passed / 42 failed in the sandbox, rerun by the CTO outside (`docs/changes/W2-145-evidence.md:168-174`) | `W2-112-A5-run1.json`, `W2-146-A5-run2.json` |
| Real-model suites and `gov accept` cannot finish in the sandbox (590 s limit, no embedder) | 2 rows | 25 (W2-13: 15 estimated, 10 measured) | The CTO runs these outside: W2-145, W2-112, W2-32, W1-19, W2-137 (`W2-145-evidence.md:98`); D-10's W2-05 | `W2-13-A5-resume-dec1000.json` |
| Code graph `/tmp/gov-cbm-<uid>` read-only | 8 returns, 6 tickets | 1 | W2-122: "None ran sandboxed. All started in the old launch form" (11-01); W2-13: "9 errors caused by the sandbox". Fixed by W2-56 S1 (`PR-DAEO-wnnz.md:55-60`, `:166-168`) | `W2-122-A5-run1.json`, `W2-13-A5-run1-dec991.json`, `W2-23-A5-run1.json` |
| `.git/config.lock` placeholder (W3-P29) | 12 returns, 10 tickets | 1 | Mostly warnings. A stale read-only `config.lock` in the main `.git` was removed by the owner's operator (DEC-1142 (10), R:14675-14676); W2-56's S7 real case red once (`PR-DAEO-wnnz.md:40`) | `W2-110-A5-r2.json`, `W2-05-A5-resume-dec980.json` |
| Placeholder files (dotfiles, `/dev/null` mounts) shown as untracked | 16 returns, 13 tickets | 4 | none | `W2-04-A5-resume-ten.json`, `W2-104-A5-run2-dec1020.json` |
| Read-only mounts and `rm` of test-made read-only trees | 4 rows | 10 | none | `W2-96-A5-run3-dec987.json`, `W2-66c-A5-r2-tests.json` |
| **Total** | **168 returns scanned** | **≈261 min (4.4 h) stated, 56 rows** | at least 4 runs lost or blocked (W2-170 ×2, W2-175 ps-2, W2-11 round). Several workers moved unsandboxed (W2-122 all, W2-112) | |

**Not counted above (estimated):**
- the CTO's time running suites outside the sandbox;
- W2-56 itself (a FULL ticket of two rounds plus follow-ups, built mainly to make the sandbox usable);
- set-up B's three stopped fix passes (DEC-1112 source line, R:14135).

**Measured rate:** 261 min over 13 days, about 20 min per day of lead and worker time. It is front-loaded in the
TMPDIR class, which is still recurring on 11-13 (W2-113 run 3).

**Before 11-01:** 274 orchestrator-log files match the sandbox terms, against 149 since (the helper's count). That
period is dominated by the code graph and the old launch form (DEC-799).

## 5. Effect on workers' search quality

**How many searches went unranked (measured):**
- `~/.cache/gov-os/rerank.log` has 440 FALLBACK lines.
- 399 of them are `OSError: [Errno 30] Read-only file system: '/home/usain/.cache/gov-os'` (sandboxed sessions only):
  11-09 1, 11-11 7, 11-12 55, **11-13 336** (the last at 09:43 UTC).
- The other 41: 32 GPU-slot waits on 11-02 and 11-06, and 9 on 11-04.
- `docs/changes/W2-145-evidence.md:99` recorded 223 when it was written.
- The rate is rising with the number of sandboxed workers. A search whose session cannot write the log leaves no line
  (`docs/research/W2-112-shared-reranker.md:96-99`), so this is a lower bound.

**What "unranked" loses (measured, the closest comparisons):**

| Set | With the 0.6B reranker | Without (fused order) | Source |
|---|---|---|---|
| The 138 (79 + spent 59), hit@5 | **107** | **95** (−12, about −8.7 points) | `governance/project/orchestration/packages/LIFT-1/D4B-LEVERS.md:14` |
| The 138, MRR | 0.5567 | 0.4867 | `:15` |
| The 79: hit@5; halves' gap | 67; 0.4 | 63; 15.7 | `:16-17` |
| Spread across the three sets | 17.2 | 33.3 | `:19` |
| Exact McNemar | – | 9 gains / 21 losses, p 0.04 | `:20` |
| EXP-003 48 questions, hit@5 (pre-G1) | 28/48 (fused+rerank) | 25/48 (fused) | `docs/research/EXP-003/w2-15a-baseline.md:86-89` |
| End to end, agents right on the 138, one call | 114 (today's bundle) | 101 ("40 unranked", shuffled, no parent expansion: not identical to a worker's fallback) | `LIFT-1/E3-RESULT.md:13-14,22` |
| End to end, with up to two searches | 128 | 118 | `LIFT-1/E3-SA-RESULT.md` (helper's citation `:12-14,26`) |

**A worse case, not measured since 11-09:** the sandbox may also drop the semantic route.
- On 11-03/11-04 sandboxed `gov retrieve` "reaches for ollama.com and hangs past 120 s" (W2-114). W2-05 had "no
  embedder" (`brief-gaps.md:10`).
- DEC-1065 (1) presumes "keywords" in the sandbox.
- If so, a sandboxed search is keyword-only and unranked. EXP-003's lexical-only mode: hit@5 25/48 against 28/48, and
  full evidence 27/48 against 34/48 (`w2-15a-baseline.md:86,89`).
- A 10-minute probe (as in §6.1) would settle it.

**Caveat:** a hit@5 gain does not predict agent correctness one to one. E4 found better rerankers raised hit@5 but not
answers (`LIFT-1/E4-RESULT.md`). The end-to-end E3 figures are the better guide: about 10-13 of 138 answers.

## 6. The middle option: keep the sandbox, fix the frictions

### 6.1 The reranker (the costly one)

**What the CTO's probe shows** (`.gov-runtime/scratch/orchestrator/drafts/act-sandbox-cache-1/probe-results.txt`,
claude 2.1.323, 11-13 11:20):

```
A = the launcher's block as built (W2-56); B = A + allowWrite ~/.cache/gov-os; C = B + allowAllUnixSockets (refused by W2-56 S9/F4, DEC-1114)
A {"ranked": false, "error": "OSError: [Errno 30] Read-only file system: '/home/usain/.cache/gov-os'"}
B {"ranked": false, "error": "PermissionError: [Errno 1] Operation not permitted"}
C {"ranked": true, "scores": [5.375, -9.5], "device": "cuda:0"}
```

**Why the probe gives those results:**
- The EROFS comes from `folder.mkdir(parents=True, exist_ok=True)` (`src/gov/retrieval/rerank.py:139`). On a
  read-only bind, mkdir of an existing folder returns EROFS.
- With the write allowed, the next line fails: `socket.socket(socket.AF_UNIX, …)` (`:144`, whose comment says "a
  sandbox refuses this at once (EPERM)").
- **So DEC-1163 (9)'s ACT changes only the error text. It does not restore ranking.**
- A per-session socket inside an allowed folder fails the same way: the refusal is at `socket()`, before any path
  (D-13: a one-path `allowUnixSockets` stays refused on Linux, DEC-1114 source line).

| Route | Where it lives | Cost (estimated) | Risk |
|---|---|---|---|
| **R0. Don't apply DEC-1163 (9)'s cache ACT as a ranking fix** (or apply it only for the clearer error). Optionally a one-line product fix: skip the mkdir when the folder exists, so the log names the true cause (EPERM socket) | ACT withdrawn or kept; the one-liner is product code (W2-145's or a small ticket) | 0 to 1 h | none |
| **R1. Loopback TCP:** the reranker service also listens on `127.0.0.1:<port>` with a token file; the client connects through the sandbox's proxy; one loopback entry in the worker's `allowedDomains` | Product ticket (W3-P28 brought forward): `rerank.py`, `rerank_service.py`, `sandbox.py`; revisions of W2-56 S8-S10/F4 and W2-112/W2-145 cases. Owner decision amending DEC-158 (empty allowlist) and DEC-1035/DEC-1114 S9 | Probe 1 h; ticket 1-2 days plus review | **Unmeasured:** whether the CLI's proxy passes a CONNECT to localhost at all. A host-level entry probably opens every loopback port, including Ollama's API at 11434 (which can pull models from the internet and delete them). `sandbox.faults` does not check `allowedDomains` contents (W2-56 R4, `PR-DAEO-wnnz.md:107-110`). Also restores the semantic route, if Ollama is reached the same way |
| **R2. `allowAllUnixSockets: true`** | `sandbox.py` (`faults` refuses it today); the W2-56 S9 and F4 tests; supersede DEC-1114's "S9 and F4 stand unchanged" | 2-4 h plus test revision | **High.** It opens every Unix socket, the WSL interop one included (DEC-1099 Q9). An interop `.exe` runs outside the sandbox, so it is close to removing it |
| **R3. CLI upstream fix** of the one-path allow on Linux | Wait, and re-run the act-sandbox-cache-1 probe at each CLI re-pin | 15 min per re-pin | none; unknown date |
| **R4. Lead-side retrieval:** workers do not search (DEC-1064 (2) as written); the lead, unsandboxed and ranked, runs `gov retrieve` and puts the bundle in the brief, or answers a worker's question between rounds | Brief text and the brief builder (governance), no product code. Reconcile DEC-836 (2) with DEC-1064 (2) | about 1 h | Workers lose ad hoc search (grep and Read instead). Ends the 2-5 min hangs too |

### 6.2 The other frictions

| Friction | Smallest fix | Where | Cost (estimated) | Risk |
|---|---|---|---|---|
| `/tmp` and TMPDIR (130 min, the largest) | Worker briefs, facts and the heavy_slot pytest line name `$TMPDIR/<dir>` (the launcher's `/tmp/gov-launch-*`), never `/tmp/gov-os-lead-<W2>`. Or `launch_worker.sh` rewrites the lead's TMPDIR in the brief copy, as it already rewrites paths (`launch_worker.sh:144-161`). Not: adding the lead's folder to `allowWrite` (a product change that widens S2 and needs a test revision) | Brief templates and facts (CTO); `launch_worker.sh` by ACT if class (b) | 1 h | none |
| `.gov-runtime/scratch/<role>/` Write refused (34 min) | The same brief change: workers write scripts under `$TMPDIR` | Briefs | in the same hour | none |
| `gov retrieve` hang on `ollama.com` (34 min) | R4 now. Later, trace the `ollama.com:443` call (open since `CHECKPOINT.md:991`) and fail fast with a short connect timeout when the semantic route is unreachable (DEC-1065 (1) already names the answer: keywords, named) | Brief now; small product ticket later | 1 h, then about 0.5 day | low |
| AF_UNIX in test suites | Keep DEC-1034's practice: those suites run in the lead's or the CTO's session | none | 0 | none |
| `config.lock` (W3-P29), now reached because DEC-1157 lets workers run concurrently | Re-scope W3-P29's premise. A CTO sweep removes a stale zero-byte read-only `.git/config.lock` only when no sandboxed session runs and no process holds it (by pid, `/proc`) | CTO tool (class per `class-rules.yaml`) | 2 h | low-moderate: never remove a live git lock |
| Code graph | Done by W2-56 S1. `gov rebuild` inside the sandbox stays a Wave 3 row (W2-56 S13) | – | 0 | – |
| Placeholders | Done by W2-56 S4 (excluded from commits). Cosmetic in `git status` | – | 0 | – |

## 7. Options for the owner (DEC-105 form)

### (a) Remove the sandbox for workers (apply now)

- **Cost:**
  - one FULL ticket (about 40-60 lines; launcher, sandbox, `launch_worker.sh`, the step-0 brief);
  - test-designer revisions in W1-46, W1-28, W2-50, W2-56, W2-20 and the unit tests (about 60-90 cases);
  - a Contract CIT-P (CAP-61, CAP-49.b, CAP-58.d, CAP-25.e/f, CAP-40.d);
  - entries superseding DEC-152, DEC-153 (1), DEC-161, DEC-158 (as enforced), DEC-386, DEC-820 (4), DEC-873 (2),
    DEC-794 (2)(a) and DEC-799 (3)-(4) (W2-27's gate (a)), DEC-1112 (1) and DEC-1128 (4);
  - through DEC-789 (3), every script-reachable guard hole becomes "fixed, not rowed".
  - **Estimated:** 2-3 days of tickets and reviews, plus the guard work it reopens.
- **Gains:**
  - the about 20 min per day of stated friction goes;
  - ranked search, and probably the semantic route, for workers (+12/138 hit@5; +10-13/138 answers end to end);
  - real-model suites run by the workers themselves; no placeholders and no `config.lock` faults.
- **Loses (§3):**
  - the only wall against writes outside the worktree: the owner's repositories, other worktrees, the guard's own
    judge `~/.local/bin/gov`, `~/.claude`, `.git` hooks, `/mnt/c`;
  - the only network-egress wall;
  - pid isolation and WSL-interop isolation;
  - the held-out oracle against opaque Bash.
  - Each would rest on a text-reading guard that lets unresolvable writes through by design, or on nothing.

### (b) Keep it and fix the frictions (defer the deeper fix to a probe)

- **B1, now:** the brief, facts and pytest-line change to `$TMPDIR`, plus R4, workers' search through the lead
  (DEC-1064 (2) as written; DEC-836 (2) read for workers as "the lead's retrieve"). About 1 hour. It removes about
  200 of the 261 stated minutes and the retrieve hangs.
- **B2, now:** R0. Do not count on DEC-1163 (9)'s cache ACT for ranking. Either apply it with that stated, or withdraw
  it.
- **B3, now (1 h):** probe R1 (a loopback CONNECT through the sandbox's proxy to a port and to Ollama's 11434), in the
  act-sandbox-cache-1 form.
- **B4, if B3 shows a port-scoped path:** bring W3-P28 forward as one FULL ticket (1-2 days). It needs an owner
  decision amending DEC-158 for the one loopback entry. If B3 shows only host-wide loopback, stay on R4 and park R1.
- **B5:** W3-P29's premise re-stated, and the `config.lock` sweep (2 h).
- **Protects:** everything in §3 stays.
- **Loses:** until B4, workers' search stays unranked, mitigated by the lead's ranked search.

### (c) Keep it as is (W3-P28 and W3-P29 as decided)

- **Cost:** about 20 min per day of stated friction continues, and rises with concurrency. Unranked searches run at
  336 a day (11-13). DEC-1064 (2) and DEC-836 (2) stay in conflict.
- **Protects:** all of §3.

### Recommendation

**(b)**, with B1-B3 now and B4 only on B3's evidence.

**Confidence:**
- **High that the sandbox should stay.** Since DEC-953 item 2 the live guard has no write-scope rule, so for workers'
  scripts the sandbox is the only wall around the owner's repositories, the guard's own judge and the network
  (§3). DEC-1128 (4) is the owner's standing word to keep it.
- **High that B1 removes most of the measured friction:** 130 + 34 + 34 of 261 minutes are briefs and the retrieve
  hang.
- **Medium on B4's feasibility:** the proxy's handling of localhost is unmeasured.

## 8. Points for the CTO (found on the way)

1. **DEC-1163 (9)'s ACT will not give ranked search** (probe B). Say so before it is applied.
2. **DEC-1064 (2) and DEC-836 (2) conflict for sandboxed workers**, and 399 searches ran anyway.
3. **CLAUDE.md's "Guard … refuses writes outside a ticket's scope"** is not true of the live hook since DEC-953 item 2
   (`pretooluse.py:1-47`).
4. **W3-P29's "Not reached today: the CTO launches workers one at a time"** no longer holds after DEC-1157.
5. **DEC-794 is DONE, but its gate (a) is in force via DEC-799 (4)** (register hygiene row,
   `PR-DAEO-wnnz.md:174-177`).
6. **The semantic route inside the sandbox has not been checked since 11-09.** It is worth one probe with B3.
