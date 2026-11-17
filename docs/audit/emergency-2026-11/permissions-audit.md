---
milestone: "Emergency 2026-11 (DEC-1209): the permissions audit (every read and write permission and refusal, all session kinds)"
commit: 64af03362cfead73a6ccc517df5efa77be42927d
pack_sha256: "none: no context pack was handed over; the inputs are the repository at the commit above and the files listed in section 1"
---

# Permissions audit (the owner's request of 2026-11-16 17:36)

An independent, read-only auditor wrote this in a fresh session. It wrote none of the audited files. The owner asked for
four things, in these words: "every read and write permission and refusal across you, the leads, the workers, the product
CTOs and the operator"; "how each has affected the work (refusals, stalls, workarounds, my interruptions, time and cost)";
"which protect something under the golden rule and which only slow work"; and "the simplest set that keeps the walls I
want and removes the rest".

**Judgement.** Every row is judged by DEC-1204, the golden rule. The threat model is honest agent mistakes, plausible
accidents and drift, not a same-privilege adversary. Each finding carries "Ordinary work: yes|no, because …",
"Consequence: fails open|loses work|other" and "Reversed by". A path that needs a deliberate construction is a Wave 3
row.

**My own refusals while auditing: one.** I scanned the CTO's approval log with a `cat > file <<'EOF'` script. Its body
named the sets root inside a text label and also held a shell variable. Rule 2b-line refused it (DEC-1097 (2)). I did
not repeat the call. I wrote the script with the Write tool, without the label (the script reads no part of the sets
root), and ran it by path. This is a live example of finding F13.

---

## 1. What was read

Every read below was read-only. No held-out material, hidden folder, verdict folder, secret or key was opened. In
`~/gov-os-operator` I read only `queue/jobs/README.md`.

- **The guard:**
  - `.claude/hooks/pretooluse.py`: 1,830 lines. I read the docstring, `REVIEW_PATHS` (lines 80-85), `review_may_write`
    (555-568) and `main()` (1658-1820).
  - `.claude/hooks/bash_writes.py` (2,783 lines) and `role_reads.py` (951 lines), by size and role.
  - `governance/project/path-map.yaml`: `evaluation_sets`, `role_paths`, `sets_root_hidden`, `session_hidden` and
    `write_refused` (lines 542-668).
  - `governance/project/held-out.yaml`: one path name.
- **Claude Code settings:**
  - `.claude/settings.json`: the hooks, plus 6 deny rules.
  - `.claude/settings.local.json`: env, 42 allow rules, 4 deny rules, the PermissionRequest hook and the Stop hooks.
  - `~/.claude/settings.json`: allows `Bash(*)`, `Read(*)`, `Edit(*)`, `Write(*)`, `WebFetch(*)` and `WebSearch(*)`;
    asks for `owner-ping`; `defaultMode` is `acceptEdits`.
  - `governance/project/orchestration/tools/permission_request.py`.
- **Launch lines:**
  - `src/gov/launch/launcher.py`, at `BYPASS_FLAGS` and the refusals at lines 394-512.
  - `src/gov/launch/sandbox.py`, which today sets `allowWrite` only and no `denyRead` or `denyWrite`.
  - `src/gov/launch/role.py`.
  - `.gov-runtime/scratch/orchestrator/tools/launch_worker.sh`, `cli()` at lines 51-54: workers get 6 tools, the auditor
    4.
  - `governance/project/orchestration/tools/dispatch/launch_now.sh` (lines 45-50, the lead line).
  - `.gov-runtime/scratch/orchestrator/tools/adopter.sh`.
- **Role and agent files:**
  - `.claude/agents/*.md`: every agent lists Read, Write, Edit, Bash, Grep, Glob, WebSearch and WebFetch.
  - `template/governance/kernel/roles/`, as quoted in this session's role text.
- **The box:**
  - `.gov-runtime/scratch/orchestrator/drafts/session-sandbox/P-BOX-EXCEPTION-1.md` (round 2).
  - `governance/project/orchestration/packages/P-PERMISSIONS-1.md`.
  - DEC-1205, DEC-1207 (2) and DEC-1209 (6).
  - The box is not live: `~/.gov-os-owner/box` does not exist, so the owner's pin step has not run.
- **The operator:**
  - `governance/project/operator/`: `operator_run.py` (G1-G9, read through its docstring and the `Refused` sites),
    `class-rules.yaml` (rows and classes), `brief.md` and `landing_check.py` (by role).
  - `~/gov-os-operator/queue/jobs/README.md`.
  - `drafts/operator-full/OWNER-OPERATOR-FULL-1.md`.
- **Effects:**
  - `~/.gov-os/guard-calls/*.jsonl`: counts only, 144,349 lines from 2026-11-09 to 11-16.
  - `.gov-runtime/scratch/orchestrator/log/guard-refusals.jsonl`: 270 classified refusals.
  - `.gov-runtime/scratch/orchestrator/log/approval-queue.jsonl`: 780 permission prompts logged by the PermissionRequest
    hook, 2026-11-01 to 11-16.
  - The `permission_denials` of 1,020 headless result logs, from the orchestrator's `log/` and `adopters/` and the
    worktrees' lead logs.
  - The owner's messages in the main-tree CTO transcripts: 545 messages; 37 of them are about permissions.
  - The CTO's memory files.
  - Retrospective parts P1 to P5 and the short list, in this folder.
- **Scripts:** in `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/acd80751-ac8f-4230-9bae-15c678a54895/scratchpad/perm-audit/`
  (`gc3.py`, `gr.py`, `aq2.py`, `aqs.py`, `pd2.py` to `pd4.py`, `wait.py`, `owner.py`).

---

## 2. The permission layers as they are (2026-11-16, before the box)

Eight layers decide what a session may do. Each is listed with the sessions it binds.

| # | Layer | Where | Binds | Decides by |
|---|---|---|---|---|
| L1 | **The guard (PreToolUse hook)** | `.claude/hooks/pretooluse.py` with `bash_writes.py` and `role_reads.py`, run by the pinned `gov` interpreter | every Claude Code session started in a tree of this repository: the CTO, its subagents, leads, workers. Not adopters in their own repositories, which run their product's kernel guard. Not the operator, the sentinel or the walled writers | rules 1, 2, 2b, 2b-line, 2b-write, 2c, 2d, 3, 4, 5, g14, catastrophic rm, and fail-closed on errors |
| L2 | **The path map's guard sections** | `path-map.yaml`: `role_paths`, `sets_root_hidden`, `session_hidden`, `write_refused`, `evaluation_sets` | read by L1 from the main tree only | data for L1 |
| L3 | **Claude Code permission rules** | user `~/.claude/settings.json`; project `.claude/settings.json` (tracked, so in every worktree); `.claude/settings.local.json` (untracked, **main tree only**: no worktree has one, checked) | the CTO: all three. Leads: user and project, with no push deny and no quiet hook. Workers: project and local (`--setting-sources project,local`), plus the user file's ask and deny carried in by `role.py`. Adopters: their own repository's settings | allow, deny and ask lists; `defaultMode acceptEdits`; the CLI's built-in checks (paths outside the working folders, `rm` outside them, `.claude/` paths, tools no rule names, such as Monitor) |
| L4 | **Launch flags** | `launch_now.sh` (leads), `launch_worker.sh` and `gov launch` (workers), `adopter.sh` (adopters) | headless sessions | `-p --permission-mode acceptEdits --allowedTools …`. Leads: 6 tools, with `--add-dir` for their tests tree and the runs root. Workers: 6 tools, the auditor 4 (no Write, no Edit). DEC-313 refuses bypass and `--add-dir` for workers. In `-p`, any call that would prompt is refused at once |
| L5 | **SANDBOX-1** (OS sandbox of `gov launch`) | `src/gov/launch/sandbox.py` | launched workers | strict network allowlist (empty; research has its own), `allowWrite` for TMPDIR, the run folder and the reranker log. **No `denyRead` today** |
| L6 | **The quiet-hours hook** | `permission_request.py` (PermissionRequest) | sessions loading the main tree's `settings.local.json` | from 02:00 to 07:30 a prompt is refused and queued; by day the prompt is shown and logged |
| L7 | **The session box** | `drafts/session-sandbox/` (bwrap, seccomp, pinned copy) | ordered for the CTO, leads, adopters and the sentinel; **not live** | what is mounted, read-only or writable per scope |
| L8 | **The operator's gates** | `operator_run.py` G1-G9 and `APPROVED`; `class-rules.yaml`; `landing_check.py`; the job queue README; the walled agent session (`--restricted`, 5 tools, a 47-line deny, a wall hook, a canary); the console's 28-command ask list | ACTs and jobs applied on the owner's behalf; control-path commits | the owner's `yes ACT-<id> <sha8>` for class (b); (O) is the owner's own; reviewed and frozen bundles |

Also: the **landing's G-1** (`tools/land.py:54, 89`), which refuses a commit touching `tests/acceptance/` without
`Role: independent-test-designer` or `Role: owner`; and **`gov launch`'s quality refusals** (effort floor, model by
criticality, `--owner-named` past two rounds: P4 Q20). The second is launch policy, not a permission. It is left to P4.

---

## 3. What each layer did: counts

### 3.1 The guard (L1): real sessions only

The call log mixes replays with real work. 60,451 of its 144,349 lines come from replay and check sessions
(guard-fix-3/4/5, agf5, guard4-check, refusal-scan, walls-check), and those made 95 % of the denials. Only sessions with
a real session id are counted here. Between 11-09 and 11-16 there were **1,031 sessions, 83,899 calls, 306 denials
(0.36 %) and 1 ask**. The guard's own time: median 88 ms, p95 209 ms, p99 348 ms; **2.45 h** over 8 days, Bash calls
dearer at a 105 ms median.

| Rule | Real denials (11-09 to 16) | By role | Harvest verdicts (10-30 to 11-16; ~1 min per false positive) |
|---|---|---|---|
| fail-closed error | **70** (the largest class) | orchestrator 45, auditor 18, TD 5, engineer 1, product-spec 1 | not classified; cause not logged |
| 2-listing (names another command gives at run time) | 47 | orchestrator 35, auditor 9 | 52 FP / 4 true |
| 5 reviewers write only outcomes | 39 | auditor 19, orchestrator (auditor subagents) 20 | 37 FP / 9 true |
| g14 role separation | 35 | TD 21, engineer 14 | 12 FP / 8 true |
| 2b-line (sets root with a variable, glob or cd) | 24 | orchestrator 22 | 10 FP / 11 true |
| 3 secrets and keys | 21 | orchestrator 14 (11-16: 11 of 12 from CTO forks and heredoc text) | 13 FP / 1 true |
| 2-judge / revision (REV_REFUSAL) | 20 | orchestrator 14 | 10 FP |
| 2-hidden | 16 | orchestrator 8, auditor 6 | 12 FP / 8 true |
| catastrophic rm | 13 | orchestrator 11 | 3 FP / 2 true |
| 1 acceptance tests | 7 | engineer 4 | 66 FP / 8 true (the FPs nearly all before ACT-GUARD-FIX-6) |
| 4-sudo | 6 | | 1 FP / 2 true |
| 2d operator folder | 3 | | |
| 4-install | 2 (plus 1 ask) | | 3 true |
| 2-heldout | 2 | engineer 2 | 1 FP |
| 2c session_hidden | 1 | engineer (W2-56) | |

The harvest holds 270 refusals: **217 false positives and 53 true**, with about 163 min of logged workaround time.
Building the guard is the cost that matters. Security work took **$2,388 at CLI rates (19 %), 167 active hours and 105
owner messages** (P1 table and F3). It also took 9 ACT-GUARD-FIX bundles, and the parser grew from 1,551 to 2,783 lines
(P3 F3).

### 3.2 Claude Code's own prompts (L3, L6): not counted before this audit

P4 S21 says "not counted". The PermissionRequest hook logs every prompt the CLI is about to show:
**780 prompts from 2026-11-01 to 11-16 in 286 sessions.**

| Where | Prompts | What made them ask |
|---|---|---|
| Interactive (the CTO's sessions, 85 transcripts) | **509: 490 by day shown to the owner, 19 refused at night and queued** | `rm` with a path outside the working folders: 146. Write/Edit/Read in `/tmp` or `/dev/shm`: 126. **The Monitor tool (no allow rule names it): 49.** Reads of `~/gov-os-operator`: 47. Reads elsewhere in HOME (`~/.local`, `~/.cache`): 46. Worktrees and runs before `--add-dir`: 55. Under `.claude/`: 11. Other: 29 |
| Headless (`-p`, 199 sessions with the main tree's local settings) | 272, each **refused at once** (headless) | Monitor: 137. Write/Edit in `/tmp`: 100. `rm`: 28. Other: 7 |

**None of the 780 came from a rule the owner wrote.** Every one came from the CLI's built-in checks: working folders,
`rm` outside them, `.claude/` self-protection, and a tool with no allow rule. The `owner-ping` ask is the only owner-set
ask, and it is a tool the CTO calls on purpose.

- **Waiting time.** I matched 157 interactive prompts to their tool results: median under 1 s, p75 31 s, p90 105 s;
  1.5 h for those 157. Scaled to the 490 by-day prompts, that is about **4.5 h of a blocked CTO session**. In the 157
  matched prompts the owner refused none.
- **Before the quiet hook (DEC-991's context).** The CTO froze for **8 h 51 min** on 2026-11-01 (one `rm -rf /tmp/…`
  chained to a commit) and **7 h 45 min** on 2026-10-31 (`owner-ping`). That is 16.6 h lost to two prompts.
- **The owner's interruptions over permissions.** 37 of 545 owner messages are about permissions. Among them:
  - 2026-11-06 09:34: "I have been asked to approve many permission prompts in your session today, and it worries me".
    This led to ACT-PERMISSIONS-1/2.
  - 2026-11-15 23:50: "The way sessions run is stalling the work and making me the courier".
  - 2026-11-16 15:58: "I want you, the leads, every agent and my operator to stop asking me for permission". This led to
    DEC-1205.
  - 2026-11-16 17:36: "The audits are not landing: their writes are refused". This is F1.

### 3.3 Headless refusals in result logs (L3, L4)

| Era, kind | Runs | Runs with a denial | Denials |
|---|---|---|---|
| Wave 1 (to 10-31), leads | 278 | 169 | 333 |
| Wave 1, other workers and probes | 116 | 72 | 173 |
| Wave 2, leads | 276 | 38 | 47 |
| Wave 2, adopters | 60 | 11 | 30 (most in `examin-cto-1`: deliberate wall probes) |
| Wave 2, workers in the worktrees still present | 175 | 55 | 111 (TD 24, reviewers 19, engineers 2, other 66) |

Wave 2 denials by kind: `rm` 65; deliberate held-out and acceptance probes 55; git commands from the adopter 17; Monitor
16; Write/Edit in `/tmp` 14; other 21. Since the lift, `rm` and Monitor are the ordinary ones. One costly case is in
memory (`auditor-scratch-via-bash`). W2-178's auditor au-1, launched with no Write tool, reached for Write at 05:40; the
quiet hook refused it; its planted red runs were lost and had to be redone.

### 3.4 The operator (L8)

From P4, P1 and the commit log:

- 61 ACT bundles from 11-10 to 11-16, 18 applied by the operator agent, all class (b).
- 33 owner yes lines.
- **134 of 544 owner messages relay a job, ACT, commit or push** (P1 F2); 54 of them in W5's four days.
- **12 of the ACTs are ACT-CLAUDE-COPIES-1 to 12.** Each copies `.claude/agents`, `skills` or `templates` files that a
  generator makes from kernel sources already reviewed and merged, for example 18 files for W2-33's role files. Each took
  a reviewed bundle and the owner's yes, because `class-rules.yaml` puts all of `.claude/**` in (b).
- ACT-PERMISSIONS-1 to 3, ACT-QUIET-DENY-1 and ACT-LEADS-ADD-DIR-1 were settings changes. Each went through the same
  route.

---

## 4. One table: every permission or refusal source

Abbreviations:
- **Verdict:** P = protects (an honest agent in ordinary work would otherwise fail open or lose work); S = only slows;
  D = duplicated by another layer.
- **Roles:** C = CTO; Cs = CTO subagents and forks; L = leads; E, T, R = workers (engineer, test designer, reviewer or
  auditor); A = product CTOs and adopters; O = operator.
- **Fired:** real 11-09 to 16 unless stated. **FP** comes from the harvest.

| # | Layer: rule | Roles bound | What it protects | Fired | FP | Workarounds it caused | Owner interruptions | Time / cost | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 1 | L1 rule 1: only the TD writes `tests/acceptance/**` | C Cs L E R | MR-3: the builder editing its own tests | 7 | 66 (pre-GF-6) | brief builds moved into scripts | — | ~65 min FP; most of the parser's build cost | **P** (the wall); its Bash/code parsing is S once SANDBOX-1 carries it for engineers |
| 2 | Landing G-1 (Role trailer on acceptance commits) | every commit that lands | the same, for what the guard lets through | rare | 0 | the "trailers in one block" memory | — | seconds | **P** (the complete backstop) |
| 3 | L1 rule 2: held-out reads | all | DEC-820 (b) | 2 | 1 | — | — | negligible | P today; **D** once the box and SANDBOX-1 `denyRead` carry it |
| 4 | L3 deny `Read(…qualification-oracle/**)` (project) | Read tool only | the same | (not logged) | 0 | — | — | 0 | **D** of #3 |
| 5 | L1 rules 2 and 2b: hidden sets, in trees and under the sets root | all six roles | DEC-820 (d), DEC-1082 | 16 (+2b-write) | 12 | — | — | small | P today; **D** after the box and `denyRead` |
| 6 | L1 2b-line: sets root with a variable, glob or cd | C Cs E | paths built at run time into hidden folders | 24 | 10 | literal paths; scripts by the Write tool; refused this audit once | — | small | P today; **D** after the box |
| 7 | L3 local denies: 3 sets-root `Read` rules, `git push` | C only (main tree) | the same | not logged | 0 | the memory `hidden-probe-refused-by-settings`: a probe proves the settings layer, not the hook | — | 0 | **D** |
| 8 | L1 2c `session_hidden` (W2-56's tuner: the transcripts) | E on W2-56 | rebuilding the held-out half | 1 | 0 | — | — | 0 | P for W2-56 only; lift when it closes (DEC-803) |
| 9 | L1 2d: no writes into `~/gov-os-operator` (but `queue/`) or the call log | all | the operator's frozen install and ACTs | 3 | 0 | EXAMIN's CTO cannot queue jobs; the Gov OS CTO copies its job files (README) | — | small | P today; **D** once the box mounts them read-only |
| 10 | L1 rule 3: secrets and keys | all | DEC-820 (a) | 21 | 13 (heredoc and prose naming dotenv files, `~/.ssh`) | "write dotenv files as words"; scripts by the Write tool | — | ~13 min logged; recurring | P today; **D** after the box (keys not mounted, untracked dotenv files masked) and `denyRead` |
| 11 | L3 project denies `Edit(**/*.key, *.pem, .env*, config/secrets*)` | sessions in this repository | writing over a key | 0 | 0 | — | — | 0 | S (harmless; keep or drop) |
| 12 | L1 rule 5: reviewers write only outcomes (`REVIEW_PATHS`) | R, and auditor-type subagents | DEC-137: a reviewer fixing what it reviews | 39 | 37 | records written to `reviews/` and copied by the CTO; **this emergency's audits refused under `drafts/` (F1)** | the owner's 17:36 message | each case minutes, plus the CTO's copying | **P** (the wall); the hard-coded list is S (F1) |
| 13 | L4 auditor tool list (no Write, no Edit) | R (launched) | the same as #12 | many `-p` refusals | — | scratch files by Bash heredoc; quiet-hour loss (W2-178 au-1) | — | runs redone | **D** of #12, and S |
| 14 | L1 g14 role separation (`role_paths`) | E (ticket tests), T (ticket implementation) | DEC-820: the counterpart's work; parallel independence | 35 | 12 | — | — | small | **P** (no other layer can express it per ticket) |
| 15 | L1 2-listing: run-time file lists | all | a computed list reaching a walled folder | 47 | 52 (93 %) | one-file-per-call forms; scripts | — | ~32 min logged | S as scoped today; P only where the listing's root covers a walled folder |
| 16 | L1 REV_REFUSAL (unresolved revision) | all | `git show` of a hidden blob through a variable | 20 | 10 | literal hashes, one per call (memory `git-archive-base-export-form`) | — | small | S (GF-8 narrows it) |
| 17 | L1 catastrophic rm | all | the repository, a `.git`, tracked files, HOME, roots | 13 | 3 | a duplicate memory entry kept because deleting it was refused | — | 0 | **P** (loses work); in the box's CTO scope the main tree is writable, so only the guard covers it |
| 18 | L1 rule 4 sudo + L3 deny `Bash(sudo:*)` | all | root | 6 | 1 | — | — | 0 | P; the guard rule is **D** of the settings deny and of the box's no-new-privileges |
| 19 | L1 rule 4 installs: ask in the CTO's session, refused elsewhere | all | the shared machine (DEC-957) | 2 + 1 ask | 0 | the memory `launched-session-no-pip-install`; wheel comparisons | each install an ask | small | P today; **D** in the box (`~/.local` and the system read-only) |
| 20 | L1 fail closed (error or 20 s deadline) | all | a missed judgement | **70** | likely all | retries in other forms | — | the largest real class | P in principle; the causes are S (F7) |
| 21 | L1 call log (HMAC) | all | evidence | — | — | replays polluted it: 60k lines | — | 0 | S (F8) |
| 22 | L3 user allow `Bash(*)`, `Read(*)`, `Edit(*)`, `Write(*)`, Web | C L | — (lets work run) | — | — | — | — | — | needed until bypass |
| 23 | L3 local allow list (42 rules) | C | — | — | — | the CTO misread which commands ask (memory corrected 11-15) | the owner's 11-06 decision ("every other git command keeps asking") never in force, because user `Bash(*)` allows everything | 0 | **S, inert** (F4) |
| 24 | L3 built-in checks: outside working folders, `rm` outside, `.claude/`, Monitor | C Cs L A | the CLI's own safety; nothing the guard does not already judge | **780 prompts** (490 to the owner) | ~all | "one simple command per call, no cd && chains" (owner, 11-06); scoped `Read(//…/**)` allows for adopters; `--add-dir` | **490** | ~4.5 h by day; 16.6 h of frozen night before L6 | **S** (F2); one exception: the `.claude/settings*` self-protection, which is P until GF-9 and box fix 5 (F6) |
| 25 | L3 user ask `owner-ping` | C | a push to the owner's phone | rare | — | — | the ping itself | — | S (lift with bypass, or allow it) |
| 26 | L6 quiet-hours PermissionRequest hook | C (main tree) | a night freeze | 49 night refusals | — | queued calls redone at 09:00; one lost auditor run | 09:00 package lines | small | P while prompts exist; **D** under bypass |
| 27 | L4 lead allowedTools (6; no Monitor) | L | — | 16 Monitor refusals (W2) | all | polling loops | — | small | S |
| 28 | L4 DEC-313: no bypass, no `--add-dir`, guard registered, no `disableAllHooks` | E T R | a worker without its guard | rare | 0 | — | — | 0 | **P** (keep: it guards SANDBOX-1's integrity) |
| 29 | L5 SANDBOX-1 (network empty, `allowWrite` narrow) | E T R | writes outside the worktree; network | not logged | — | TMPDIR and `PYTHONUSERBASE` lines; config.lock placeholder; code-graph reds | — | small | **P**; it should also carry `denyRead` for the held-out material, the sets root and keys, and `denyWrite` of `tests/acceptance` for engineers |
| 30 | L7 the box | C L A (not live) | confinement per session: secrets, held-out material, protected branches, settings | — | — | — | 45 min of the owner's steps | P-BOX build | **P** (the owner's chosen wall) |
| 31 | L8 G1-G5, G7-G9 (frozen, decided, rehearsed, reviewed, same shas, live state, dry run, holds) | O | an ACT applied unreviewed, changed after review, or half-applied | — | — | — | — | per ACT | **P** |
| 32 | L8 G6: the owner's yes for (b) | O | the owner's control of control paths | 33 yes lines | — | — | 33 | per ACT | **P** (the owner's wall) |
| 33 | L8 `class-rules.yaml`: all of `.claude/**` in (b), generated copies included | C O | agent instructions | 12 CLAUDE-COPIES ACTs | 12 of 12 copies of merged, reviewed sources | — | 12 yes lines and their relays | ~12 bundles, reviews and applies | **S** for byte-identical generated copies (F11); P for the rest |
| 34 | L8 the walled operator agent (`--restricted`, 5 tools, deny list, wall hook, canary) | O | an injected instruction acting outside the operator's folder | — | — | — | — | — | the owner chose to remove it (DEC-1205 (5)); the program gates keep the yes |
| 35 | L8 operator console asks (28 commands) | O console | — | — | — | — | each a prompt to the owner | — | S; removed by OWNER-OPERATOR-FULL-1 |
| 36 | L8 job queue README (interim) | C, O console | the operator running only named, rehearsed commands | 7+ jobs | — | EXAMIN's job files copied in by the CTO | a relay per job (134 relays in all) | hours of latency | P now; **D** once the operator has full permission and its own yes path |
| 37 | Landing check P1 on control paths outside an ACT | C | control-path edits outside the route | 8 P1 | ~4 of them trailer form | trailer memory | — | low | P |
| 38 | Product kernel guard plus settings in adopted repositories | A | the product's walls | 30 W2 denials (mostly probes) | — | job files cannot reach the queue | 11-15: an adopter's held-out probe became a permission question, answered No | — | P for the product; the Gov OS sets root is the box's job (F14) |

---

## 5. Per role: what binds each session today

| Session | Layers today | What asks or refuses in ordinary work | Notes |
|---|---|---|---|
| **CTO** (interactive, main tree) | L1, L3 (user, project, local), L6 | ~31 prompts a day to the owner (L3 built-ins); guard denials ~10 a day (rules 3 and 2b-line false positives from heredoc text; 2-listing) | the only session with the push deny and the quiet hook |
| **CTO subagents and forks** | the parent's L1 and L3; L1 judges them by agent type (`acting_role`) | auditor-type subagents: rule 5; TD-type: g14 | F1 hit here: 7 rule-5 refusals on 11-16, 16:34 to 17:23 |
| **Leads** (`-p`, worktree) | L1; L3 user and project (no local); L4 (6 tools, `--add-dir`) | anything that would prompt is refused at once: `rm` outside, Monitor, `/tmp` writes outside the added folders | no push deny (L3 local is absent in worktrees); the GitHub SSH keys are reachable |
| **Engineers** | L1 (rule 1, g14 tests), L3 project+local, L4 6 tools, L5 SANDBOX-1, DEC-313 | g14 and rule 1 (true); 2-listing | the OS walls writes outside the tree and the network; reads are walled by L1 alone |
| **Test designers** | as engineers, but g14 on the implementation | g14 (21 real, 8 true in the log) | |
| **Reviewers and auditors** (launched) | as engineers, with 4 tools; L1 rule 5 | rule 5; the missing Write tool | rule 5 and the tool list duplicate each other |
| **Product CTOs and adopters** | their repository's kernel guard and settings; `adopter.sh -p acceptEdits` with 7 tools and `Read(/replies/**)` | reads outside their folder; git checkout | headless since 11-15 (P-SESSIONS-1); boxed once the pin exists |
| **Operator agent** (cron, ACTs) | L8 walled session, G1-G9, `APPROVED` | the wall refuses everything but its one command | to get full permission (OWNER-OPERATOR-FULL-1), with the gates kept |
| **Operator console** (the owner's job runner) | its own settings: 28 asks, a deny list | each ask is a prompt to the owner | the asks are removed by OWNER-OPERATOR-FULL-1 |
| **Sentinel** | interactive, outside the box | asks almost nothing | |

---

## 6. Findings

**Classification on one line:** F1, F2, F3, F4, F7, F8, F9, F11, F13 and F17 are "other". F10 "loses work" (small).
F6 "fails open" and is the entry criterion of the no-prompt switch (DEC-803), already first in DEC-1205's order. F5 is
other. F12 is other. F14 and F15 are Wave 3 rows. No finding blocks today's work. F6 blocks only the switch, as DEC-1205
already orders.

**F1: auditors could not write their reports under the CTO's drafts folder (the emergency's problem).**
- **What happened.** The CTO briefed independent auditors (subagents of type independent-auditor) to write the
  emergency's reports under `.gov-runtime/scratch/orchestrator/drafts/retro-2026-11/`. Rule 5 lets an auditor write only
  under `docs/probes/`, `docs/audit/`, `docs/assessment/`, `.gov-runtime/scratch/review/`,
  `.gov-runtime/scratch/audit/`, the CTO's `reviews/` folder, or `/tmp`. The list is hard-coded as `REVIEW_PATHS` at
  `pretooluse.py:80-85`. So the guard refused the writes: 7 rule-5 refusals between 16:34 and 17:23 on 11-16.
- **Effect.** P4 wrote its report to `reviews/` instead. The others returned their text, and the CTO copied it in. The
  owner saw "the audits are not landing" (17:36).
- **It has happened before.** The same brief error appears on 11-02 (rows 75-76, which gave ACT-GUARD-FIX-4 its
  `reviews/` allowance), 11-03, 11-07 and 11-11 (harvest notes: "the CTO's brief named a wrong place").
- **What should happen.** A brief names an output path the reviewer may write, and the writer and the guard read the
  same list.
- **Fix.**
  1. Done 11-16: briefs name `docs/audit/<topic>/` (README here; memory `audit-reports-docs-audit`).
  2. Move `REVIEW_PATHS` into the path map as one list (for example `review_outcomes:`), read by the guard and by the
     brief builders.
  3. Have the CTO's brief builder (`tools/build_lead_brief.py`, `gov brief`) refuse a reviewer or auditor brief whose
     named output path falls outside that list, so the error is caught before the launch, not at the write.
- **Do not widen rule 5 to all of `.gov-runtime/scratch/`.** It holds `tools/` (the executors cron runs) and `acts/`.
  `drafts/` alone could be added: packages are hash-pinned by the owner's yes and the operator's G1/G5. But `docs/audit/`
  is tracked, reviewed and already allowed, so it is the better home.
- Ordinary work: yes, because the CTO writes such briefs daily, and it happened five times this month.
- Consequence: other (honest work refused, then copied by hand; no report lost, because each was returned as text).
- Reversed by: an auditor refused under `docs/audit/`, which would show the rule itself wrong, or a report found lost
  because of it.

**F2: 780 Claude Code prompts in 16 days, none from a rule the owner wrote; 490 interrupted the owner.**
- The CLI's built-in checks asked for:
  - `rm` outside the working folders;
  - writes and reads in `/tmp` and `/dev/shm` (the scratch the briefs require);
  - reads of the operator folder and `~/.local`;
  - the Monitor tool (no allow rule names it).
- The guard had already judged each call. Not one of 157 matched prompts was answered No.
- Cost: ~4.5 h of a blocked CTO session by day; 16.6 h of night freezes before the quiet hook; the 11-06 rule "one
  simple command per call" as a lasting tax; and the owner's 11-06, 11-15 and 11-16 interventions.
- DEC-1205 removes all of it inside the box (bypass, with the guard deciding).
- Until then, three zero-risk lines would remove about 60 % of them: allow `Monitor`; add `/tmp`, `/dev/shm` and
  `~/gov-os-operator/queue` as additional working folders for the CTO's own start line (not in `settings.local.json`,
  which DEC-1161 cleared because workers inherit it); and allow `Read(//home/usain/.local/**)`. The guard's walls do not
  depend on any of them.
- Ordinary work: yes, because they come from the scratch folders and tools every brief prescribes.
- Consequence: other (the owner interrupted; the session blocked).
- Reversed by: a prompt the owner answered No that would otherwise have done harm in ordinary work.

**F3: headless sessions are refused whatever would prompt.**
- 272 such refusals appear in the hook's log (Monitor 137, `/tmp` writes 100).
- In Wave 2 result logs: 47 lead denials, 111 worker denials and 30 adopter denials.
- Leads have no Monitor tool in their allowedTools, so 16 polling calls failed.
- Fix: add Monitor to the lead and adopter `--allowedTools`. The box's bypass then makes the rest moot. Workers keep
  their walls under W-a.
- Ordinary work: yes. Consequence: other.
- Reversed by: a refused headless call that would have done harm.

**F4: the local allow list is inert, and one owner decision never took effect.**
- `settings.local.json` holds 42 allow rules. The user file's `Bash(*)`, `Read(*)`, `Edit(*)` and `Write(*)` already
  allow all of them.
- The owner's 11-06 correction to P-PERMISSIONS-1 was "allow only read-only git … every other git command keeps asking".
  It was never in force, because `Bash(*)` allows every git command. The CTO's memory recorded the wrong model until
  11-15 (`sessions-get-tools-at-start`, "CORRECTED").
- No wall depended on it: push is denied separately.
- Fix: delete the local allow list (DEC-1205 supersedes the intent).
- Ordinary work: yes (the CTO reasons from it). Consequence: other.
- Reversed by: a Claude Code version in which project allow rules narrow a user allow.

**F5: the push wall today covers the CTO only.**
- `Bash(git push *)` is denied only in the main tree's untracked `settings.local.json`. Leads run in worktrees, which
  have no local file. They have `Bash(*)`, and today the GitHub SSH remote's credentials are in reach.
- Workers are covered by SANDBOX-1's empty network.
- No agent pushed in ordinary work: the transcripts show only the rehearsal clones' pushes.
- The box carries this wall completely: HOME is a tmpfs, so there is no `~/.ssh`, no gh login and no `SSH_AUTH_SOCK`.
  The push belt in ACT-GUARD-FIX-9 duplicates it, by the owner's choice (P).
- Ordinary work: yes, plausibly (a lead "finishing" a branch). Consequence: other (a branch on the private remote, which
  can be reverted; nothing lost).
- Reversed by: a credential reachable inside a boxed lead.

**F6: no-prompt mode turns off the CLI's self-protection (from P-PERMISSIONS-1 §1, confirmed by reading).**
- Under `bypassPermissions`, a write of `.claude/settings.local.json` goes through, and the guard does not refuse it. The
  next session then starts with `disableAllHooks` and no guard.
- In `acceptEdits` today the CLI asks, which is item 24's one protective exception.
- Fix: ACT-GUARD-FIX-9 (writes to `**/.claude/settings*.json`, `**/.claude/hooks/**` and the home settings; no bypass
  outside the box) and box fix 5 (read-only binds). Both are already first in DEC-1205 (2).
- This is the entry criterion of ACT-PERMISSIONS-4 (DEC-803), not a round now.
- Ordinary work: yes, because a session adding an allow rule or a hook is routine. Consequence: fails open.
- Reversed by: a rehearsal showing a boxed, bypassed session refused that write without GF-9.

**F7: 70 real guard refusals were fail-closed errors, the largest real class, with no cause logged.**
- They hit the CTO (45) and auditors (18).
- Fix: record the exception's class in the call log (a field name, never content) and fix the top two causes.
- Ordinary work: yes. Consequence: other (honest calls refused).
- Reversed by: the causes turning out to be genuine 20-second timeouts under extreme load only.

**F8: the call log is 42 % replays.**
- 60,451 lines come from replays that did not set `GOV_GUARD_CALLS_DIR`. Any count from the live log, this audit's
  included, must filter them out.
- Fix: the replay tools set the variable by default.
- Ordinary work: yes. Consequence: other.
- Reversed by: the replays being meant as live evidence.

**F9: four walls are carried by two or three layers each.**
- Held-out reads: rule 2, the project deny and (soon) the box.
- Hidden sets: 2, 2b, 2b-line, 2b-write, three local denies and (soon) the box.
- sudo: rule 4, the settings deny and the box's no-new-privileges.
- The operator folder: rule 2d and the box's read-only mount.
- Each extra layer costs FP time (2b-line refused this audit's own script), memory entries
  (`hidden-probe-refused-by-settings`) and ACT churn.
- Ordinary work: yes. Consequence: other.
- Reversed by: a session kind the box and SANDBOX-1 do not cover that still needs the guard's copy. The list in
  section 7 keeps the guard where that is so.

**F10: the launched auditor's missing Write tool duplicates rule 5 and has lost work.**
- W2-178 au-1 reached for Write; the quiet hook refused it; its planted red runs were lost. Every auditor brief now
  carries a "make scratch files with Bash heredocs" line.
- Rule 5 already confines every write the auditor makes with a file tool.
- Fix: give launched auditors Write and Edit, and let rule 5 decide.
- Ordinary work: yes, because auditors plant reds on copies routinely. Consequence: loses work (scratch runs, redone).
- Reversed by: an auditor that, given Write, wrote outside its outcomes and was not refused by rule 5.

**F11: generated copies go through the full (b) route.**
- ACT-CLAUDE-COPIES-1 to 12 each copied generator output from kernel sources that were already reviewed and merged. Each
  needed a bundle, a review, the owner's yes and the operator's apply.
- Fix: one new `class-rules.yaml` row. It classes a touched file under `.claude/agents|skills|templates/**` as (a) when
  its bytes equal `gov adapters generate` output at a named merged commit, a check `act_class.py` can make in code.
  Everything else under `.claude/**` stays (b).
- This is an (O) change to the rule table: the owner's.
- Ordinary work: yes (every role or skill change). Consequence: other.
- Reversed by: a generated copy that differed from its source in a way only a review caught.

**F12: the quiet-hours hook earns its place only while prompts exist.**
- It turned 16.6 h of freezes into 49 queued refusals.
- Under bypass inside the box nothing prompts, so it becomes a duplicate. Remove it at the switch.
- Ordinary work: yes. Consequence: other.
- Reversed by: prompts still seen inside the box.

**F13: the guard's text reading refuses honest scripts.**
- Rules 3 and 2b-line judge the words in a heredoc. Examples:
  - 11 of 12 secret refusals on 11-16 came from CTO forks writing prose or scripts that name dotenv files or `~/.ssh`;
  - this audit's own counting script was refused for a label.
- P-GUARD-FP-1 (a) and GF-8 narrow this. Once the box and `denyRead` carry the static walls, these rules can go
  (section 7).
- Ordinary work: yes. Consequence: other.
- Reversed by: a true refusal among them that a mount would not have caught.

**F14: an adopter's read of a held-out file raised a permission question instead of a refusal (11-15 22:54).**
- The product's guard does not know Gov OS's sets root. The owner answered No.
- It was a deliberate precondition probe, and adopters' ordinary work never names the sets root. The box does not mount
  it.
- Wave 3 row.
- Ordinary work: no, because only a probe named that path. Consequence: fails open (if answered yes).
- Reversed by: an adopter's ordinary search reaching the sets root.

**F15: inside the box, an install into a private venv in `/tmp` would pass.**
- The box keeps `~/.local` and the system read-only, but the network is open for the CTO.
- It changes nothing shared, so it does not breach the wall's purpose (DEC-957: the shared machine). Row.
- Ordinary work: yes. Consequence: other.
- Reversed by: a venv install that changed a shared path.

**F17: rule 1's Bash and code parsing is the costliest part of the guard and can be replaced for the implementer.**
- Engineers always run under `gov launch`. Two lines in their launch profile would wall `tests/acceptance/**` at the OS
  and settings level for every tool and interpreter, with no parsing:
  - a SANDBOX-1 `denyWrite` (the key already exists in `FILESYSTEM_KEYS`);
  - an `Edit(//<tree>/tests/acceptance/**)` deny.
- Landing G-1 stays as the commit-level backstop.
- This needs a src ticket (launcher) after the emergency.
- Ordinary work: yes. Consequence: other (cost).
- Reversed by: an engineer flow that must write `tests/acceptance` (none: only the TD does).

---

## 7. The simplest set: each wall the owner stated, and the one layer that carries it

The walls come from DEC-953 item 2, DEC-954, DEC-820, DEC-1204, DEC-1205 and DEC-957. "Carrier" is the one layer that
should hold the wall. "Remove or simplify" lists every other layer now doing the same job. Everything not on this list
is removed (section 8).

| # | Wall (the owner's) | Carrier: the ONE layer | Remove or simplify |
|---|---|---|---|
| W1 | Acceptance tests are written only by the independent test designer (MR-3, DEC-906) | **Landing G-1**: no commit touching `tests/acceptance/` lands without the TD's role (complete, in code, at the only point where it matters). At session time for the implementer: **SANDBOX-1 `denyWrite` plus an `Edit` deny in the engineer's launch profile** (after the emergency; src ticket) | Guard rule 1: keep the file-tool path check only. Drop its Bash and code parsing once the launch profile lands. |
| W2 | The held-out material is never read (DEC-820 (b)) | **OS: not mounted in the box; SANDBOX-1 `denyRead` for workers** (`denyRead` is a launcher change) | Guard rule 2 and the project's `Read(…oracle/**)` deny: remove once the box is live and SANDBOX-1 has `denyRead`. Until then the guard rule is the carrier. |
| W3 | The hidden halves are never read by the sessions they measure (DEC-820 (d), DEC-1082) | **OS: the sets root is not mounted in the box; SANDBOX-1 `denyRead` of it for workers** | Guard 2b, 2b-line, 2b-write and 2c; the three local `Read` denies; the 2-listing and REV_REFUSAL machinery where it serves only these. Remove after the box and `denyRead`. Keep `evaluation_sets` hidden globs in trees only if a set returns into a tree. |
| W4 | Secrets and keys are never read (DEC-820 (a)) | **OS: key and credential files not mounted, HOME masked, untracked dotenv files masked (box); SANDBOX-1 `denyRead` of `~/.ssh`, `~/.config/gh` and key globs** | Guard rule 3 (the worst live FP source for the CTO): remove after the box. The `Edit(*.key …)` denies: harmless, but can go. |
| W5 | Reviewers and auditors write only their outcomes (DEC-954, DEC-137) | **Guard rule 5** (no OS layer separates a subagent from its parent), with **`REVIEW_PATHS` moved into the path map and checked by the brief builder** (F1) | The launched auditor's tool list without Write and Edit (F10): remove. Keep the git-status backstop (G-2). |
| W6 | The counterpart's work is not read (DEC-820; g14, DEC-1052) | **Guard g14** (`role_paths`): per-ticket paths no mount can express | Scope 2-listing and REV_REFUSAL to g14's walled folders only (P4 S12, S13). |
| W7 | No catastrophic deletes (DEC-1050 (8)) | **Guard rm rule** for the trees themselves (the box must leave the CTO's main tree writable); the box covers HOME and everything outside | Allow the CTO to delete its own memory files (P4 S16). Unresolved deletes stay Wave 3 rows (DEC-1205 (7)). |
| W8 | sudo is refused (DEC-953) | **OS: no-new-privileges (box and SANDBOX-1)**; the one-line settings deny `Bash(sudo:*)` stays as a zero-cost belt that holds in every mode | Guard rule 4-sudo: remove. |
| W9 | Installs ask the owner (DEC-957) | **The box**: `~/.local` and the system read-only, so an install cannot change the machine inside; installs go to the operator as a job on the owner's yes | Guard rule 4-install and 4-ask: remove once every CTO, lead and adopter is boxed. Workers already have no network. |
| W10 | The operator applies a control-path change only on the owner's yes (DEC-1104, DEC-1173) | **The operator program's gates G1 to G9** (G6 the yes) | `class-rules.yaml`: generated copies as (a) (F11). The walled agent session: removed by DEC-1205 (5). The console's ask list: removed (OWNER-OPERATOR-FULL-1). The job queue README: retire when the operator is full and has its own yes path. |
| W11 | Each session is confined by the box (DEC-1205 (1), DEC-1207 (2)) | **The box** (bwrap from the owner's pin) for the CTO, leads, adopters and the sentinel; **SANDBOX-1** for workers (W-a) | Guard 2d (operator folder, call log): remove for boxed sessions (mounted read-only). The quiet-hours hook, the user `owner-ping` ask, the lead and adopter `--allowedTools` lists and the local allow list: remove at the bypass switch (DEC-1205 (2)(iii)). |
| W12 | Only the owner pushes (DEC-1205 (3)) | **The box**: no credentials inside | The ACT-GUARD-FIX-9 push belt is a duplicate the owner chose: keep it as the belt, or drop it. The local deny `Bash(git push *)`: remove. |
| W13 | A session cannot switch its own guard off (DEC-1205 (2)(i), F6) | **ACT-GUARD-FIX-9 plus box fix 5** (read-only `settings.local.json` and the session's settings copies) | Nothing else. This is the switch's entry criterion. |

**Today, before the box.** The guard remains the carrier for W2, W3, W4, W9 and W12, and the owner's walls hold through
it. The removals in the "after the box" cells are not to be made before the box and `denyRead` are live and rehearsed.

---

## 8. What to remove, with its cost

Ordered by what each frees. Each removal is an ACT or ticket after the owner decides (DEC-1209 (7)).

1. **The Claude Code prompts (item 24, F2, F3).** Cost: 490 owner interruptions in 16 days (~31 a day), ~4.5 h blocked
   CTO time, 16.6 h of night freezes before DEC-991, and 272 headless refusals. Removed by DEC-1205's bypass inside the
   box. Before that, allow Monitor and add the CTO's scratch folders at its start line.
2. **The guard's text-reading rules for the static walls: 2b-line, 3, 2-hidden, 2b-write, 2c, 2d, 2-heldout, and
   2-listing and REV_REFUSAL outside g14 (items 3, 5, 6, 9, 10, 15, 16).** Cost: 113 of the 306 real refusals in 8 days,
   mostly false positives (rule 3 13:1, 2-listing 52:4, REV 10:0); P1 counts most of the $2,388 and 105 owner messages
   of security work; 9 GUARD-FIX ACTs; a dozen memory workarounds. Replaced by box mounts and SANDBOX-1 `denyRead`.
3. **The operator's (b) route for generated copies (item 33, F11), and the interim job queue (item 36).** Cost: 12
   bundles, reviews and yes lines for byte copies; 134 owner relay messages in all. Fixed by one (a) row and
   OWNER-OPERATOR-FULL-1.
4. **The duplicate settings rules and the inert allow list (items 4, 7, 23, 25, 27).** Cost: misled reasoning (F4), a
   probe proving the wrong layer, the owner's 11-06 decision silently not in force. Delete them.
5. **The launched auditor's no-Write tool list (item 13, F10), and the hard-coded `REVIEW_PATHS` (F1).** Cost: lost
   scratch runs, a standing workaround line in every brief, the CTO copying reports, and this emergency's "audits not
   landing". Give auditors Write; move the list into the path map; check briefs against it.

Kept, because each protects something under the golden rule: guard rules 1 (file tools), 5, g14 and catastrophic rm;
landing G-1; DEC-313 and SANDBOX-1; the box; G1 to G9; the settings deny `Bash(sudo:*)`; fail-closed, with its causes
fixed (F7).

---

## 9. item | class | evidence

| item | class | evidence |
|---|---|---|
| W1 acceptance tests by the TD only (MR-3, DEC-906) | OK | .claude/hooks/pretooluse.py, .gov-runtime/scratch/orchestrator/tools/land.py |
| W2 held-out material not read (DEC-820 (b)) | OK | .claude/hooks/pretooluse.py, governance/project/held-out.yaml, .claude/settings.json |
| W3 hidden halves not read (DEC-820 (d), DEC-1082) | OK | governance/project/path-map.yaml, .claude/hooks/pretooluse.py |
| W4 secrets and keys not read (DEC-820 (a)) | OK | .claude/hooks/pretooluse.py |
| W5 reviewers write only outcomes (DEC-954) | WEAKENED | .claude/hooks/pretooluse.py, docs/audit/emergency-2026-11/README.md |
| W6 counterpart's work not read (DEC-820, DEC-1052) | OK | governance/project/path-map.yaml, .claude/hooks/role_reads.py |
| W7 catastrophic deletes refused (DEC-1050 (8)) | OK | .claude/hooks/pretooluse.py |
| W8 sudo refused (DEC-953) | OK | .claude/hooks/pretooluse.py, .claude/settings.json |
| W9 installs ask the owner (DEC-957) | OK | .claude/hooks/pretooluse.py |
| W10 the operator's yes gates (DEC-1104, DEC-1173) | OK | governance/project/operator/operator_run.py, governance/project/operator/class-rules.yaml |
| W11 the box confining each session (DEC-1205 (1), DEC-1207 (2)) | MISSING | .gov-runtime/scratch/orchestrator/drafts/session-sandbox/P-BOX-EXCEPTION-1.md |
| W12 pushes by the owner only (DEC-1205 (3)) | WEAKENED | .claude/settings.local.json, governance/project/orchestration/packages/P-PERMISSIONS-1.md |
| W13 no session switches its own guard off (DEC-1205 (2)(i)) | WEAKENED | governance/project/orchestration/packages/P-PERMISSIONS-1.md |
| N1 the owner not asked for permission (the owner, 11-16 15:58; DEC-1205) | MISSING | .gov-runtime/scratch/orchestrator/log/approval-queue.jsonl, governance/project/orchestration/tools/permission_request.py |

Notes on the non-OK rows:
- **W11 MISSING:** ordered and not live. The owner's pin step has not run (DEC-1209 (6)).
- **W12 WEAKENED:** covered for the CTO only until the box (F5).
- **W13 WEAKENED:** holds today only because the CLI asks in acceptEdits; GF-9 and fix 5 are pending (F6).
- **N1 MISSING:** F2 and F3.

---

```verdict
{"kpis": [
 {"kpi": "W1 acceptance tests by the test designer only", "verdict": "pass", "findings": [{"id": "F17", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "W2 held-out material walled", "verdict": "pass", "findings": [{"id": "F9", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F14", "scope": "out", "ordinary_work": "no", "consequence": "fails open"}]},
 {"kpi": "W3 hidden sets walled", "verdict": "pass", "findings": [{"id": "F9", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F13", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "W4 secrets and keys walled", "verdict": "pass", "findings": [{"id": "F13", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "W5 reviewers write only outcomes", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F10", "scope": "in", "ordinary_work": "yes", "consequence": "loses work"}]},
 {"kpi": "W6 counterpart's work walled (g14)", "verdict": "pass", "findings": []},
 {"kpi": "W7 catastrophic deletes refused", "verdict": "pass", "findings": [{"id": "F7", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "W8 sudo refused", "verdict": "pass", "findings": [{"id": "F9", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "W9 installs ask the owner", "verdict": "pass", "findings": [{"id": "F15", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "W10 operator yes gates", "verdict": "pass", "findings": [{"id": "F11", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "W11 the box confining each session", "verdict": "fail", "findings": [{"id": "F12", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "W12 pushes by the owner only", "verdict": "fail", "findings": [{"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "W13 no session switches its own guard off", "verdict": "pass", "findings": [{"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]},
 {"kpi": "N1 the owner is not asked for permission", "verdict": "fail", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F8", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}
]}
```

W13 passes today only because bypass is off. F6 is the entry criterion of the no-prompt switch (DEC-803): ACT-GUARD-FIX-9
and box fix 5 come first, as DEC-1205 (2) orders.
