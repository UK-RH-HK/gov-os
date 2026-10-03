---
id: S2-CIT-P
type: change-impact-proposal
status: ACCEPTED
accepted: owner, 2026-10-03 (answers recorded as DEC-156…DEC-162)
date: 2026-10-03
branch: s2/spec
base: w1/integrate @ 442e9c3
author: product-spec (S2, single author)
audit: S2-A, a fresh Independent Auditor (DEC-088)
decisions_carried: [DEC-102, DEC-103, DEC-104, DEC-105, DEC-106, DEC-119, DEC-136, DEC-137, DEC-138, DEC-147]
decisions_recorded: [DEC-150, DEC-151, DEC-152, DEC-153, DEC-154, DEC-155, DEC-156, DEC-157, DEC-158, DEC-159, DEC-160, DEC-161, DEC-162]
repair: after the S2-A round-1 audit (ACCEPT_WITH_FINDINGS), DEC-163…DEC-171, see S2-CIT-E §6; after the round-2 audit (ACCEPT_WITH_FINDINGS), DEC-172 and DEC-173, see §7 and S2-CIT-E §7; at the round-3 closure check, DEC-174, see §7 and S2-CIT-E §8
---

# S2 — Change-impact proposal (CIT-P) on the Gov OS specification

This change brings the closed Gov OS specification up to date with decisions the owner took during the Wave 1
bootstrap, and with the result of the sandbox experiment EXP-001. It changes specification files only: the register,
Contract v4, ADR-0001, ADR-0002, the Wave 1 WBS, tickets, `bootstrap.md` and the plan validator. It changes no code,
hook, settings file or test.

The owner answered the open questions on 2026-10-03 (§5). This record is updated to match those answers; where an
answer changed the impact first listed, the row now states the answered impact.

## 1. What triggers the change

| # | Trigger | Source | State before this change |
|---|---|---|---|
| A1 | Experiments are part of discovery | DEC-102 | In the register; not in Contract v4 or the WBS |
| A2 | The order of specification work | DEC-103 | Same |
| A3 | UX before build, with visual testing | DEC-104 | Same |
| A4 | Evidence-triggered change, three options | DEC-105 | Same |
| A5 | Wave 1 learning metrics | DEC-106 | Same |
| A6 | Probe findings feed the independent suite | DEC-136 | Same |
| A7 | Independent post-green probe for FULL tickets | DEC-137 | Same |
| A8 | Sandbox spike, now with its outcome | DEC-138, DEC-147, EXP-001 | Decision in the register; outcome not recorded |
| B1 | Orchestrator write scope (DP-7 option (b) extended, then corrected by the owner) | Owner, S2 brief; DEC-150, DEC-156 | New |
| B2 | Two confirmations from W1-05 | Owner, S2 brief | New |
| B3 | EXP-001 accepted as ADOPT-PARTIAL | Owner, S2 brief; `spike-sandbox/EVIDENCE.md` | New |
| B4 | W1-05 provides the minimal role definitions first | Owner, S2 brief; DEC-119 | DEC-119 left it for this change |
| B5 | Scope and extension of `validate_s1.py` | Owner, S2 brief | New |
| C | Four open points from EVIDENCE §4 and §5.5, one found here, and one left by the answers (where the oracle is hidden from the orchestrator) | §5 below | Answered: DEC-156…DEC-162 |

## 2. The three options (DEC-105)

| Option | What it means here | Cost |
|---|---|---|
| **Apply now** (chosen by the owner in the S2 brief) | Contract v4 becomes v4.1; four new Wave 1 tickets; 39 open tickets keep their KPIs except the five named in §3.4 | This change, one audit (S2-A), about 280 LOC of new Wave 1 glue (370 after the repair, §6). W1-45 changes the guard code of W1-02 and W1-03, and the acceptance tests of those two closed tickets that assert the old orchestrator rule are revised by the Independent Test Designer (§3.7) |
| Defer | Record EXP-001 and continue Wave 1 on the guard alone | No work now. The opaque-write and install residuals stay open; DEC-102…DEC-106, DEC-136 and DEC-137 stay outside the Contract while acceptance tests are written against it |
| Re-baseline | Reopen the enforcement part of the specification and re-plan W1-02…W1-05 around the sandbox | Retires working, tested guard code that EXP-001 shows is still needed for the file tools. Not justified by the evidence |

## 3. Impact

### 3.1 Decision register

| Item | Change | Why |
|---|---|---|
| New section 26 (register v0.26) | Six decisions for the brief (DEC-150…DEC-155), then seven owner answers (DEC-156…DEC-162) | The brief asks for each as a new DEC, `ACCEPTED (owner, 2026-10-03)` |
| DEC-083 | **Not amended.** DEC-157 confirms it: the orchestrator installs, the guard asks, the owner approves in chat. Added only: worker roles never install system-wide | P-1 answered (d); the orchestrator's session is not sandboxed (DEC-156) |
| DEC-138 | Outcome recorded by the new EXP-001 decision | The spike has a verdict |
| DEC-123, DEC-147 | Their residuals are closed for Bash in launched worker sessions (DEC-152, DEC-161); they stay open for the orchestrator's own session | EVIDENCE §5.1, P-5 |
| DEC-108 (kernel scratch set) | Untouched. The orchestrator's checkpoint lives in `.gov-runtime/scratch/orchestrator/` until W1-25 (DEC-150, DEC-156) | B1 |
| DEC-112 | Untouched: the allowed-paths rule holds for every other role | B1 |
| DEC-119 | Its "for the post-bootstrap spec change" note is carried out | B4 |

No ACCEPTED or DONE entry is edited; amendments are new entries that name what they amend.

### 3.2 Contract v4 → v4.1 (`CONTRACT_v4.md` and `contract.yaml`)

| Item | Change | Why |
|---|---|---|
| Frontmatter, title line | Version 4.1, change log, decisions list | The brief |
| §1 Counts | 60 → 62 capabilities; W1 KEPT 36 → 38 | Two capabilities added |
| §2 Envelope, "Boundary" | Adds the containment layers: the OS sandbox for Bash in launched worker sessions, the guard and permission rules for the file tools and for the orchestrator's session; neither is a security boundary (ADR-0001 unchanged in substance) | B3 |
| §2 Envelope, "Tool installs" | **Unchanged** (DEC-157). One sentence added: worker roles never install system-wide | P-1 |
| MR-3 | Acceptance adds the orchestrator exception: the orchestrator may write anywhere in the repository, and `tests/acceptance/**` stays closed to it as to every role but the test designer; provider W1-45 added | B1, DEC-156 |
| MR-1 | Acceptance unchanged; DEC-103 is carried in CAP-30 | A2 |
| **CAP-58** Path guards | Claim split: in a launched worker session a Bash write outside the repository is stopped by the OS sandbox; a file-tool write is stopped by permission rules and the guard; inside the repository the guard and the containment check hold. New `covers` items: the sandbox wall for a worker's Bash (W1-46); the orchestrator's write scope (W1-45); the containment check also runs on `PostToolUseFailure` (W1-47). New providers W1-45, W1-46, W1-47 | B1, B3, EVIDENCE §5.4, DEC-156, DEC-161 |
| **CAP-61** (new, W1) | The launcher starts worker sessions only (engineer, test designer, auditor, research or experiment). It refuses to start one unless the sandbox is on, strict and fail-closed; it builds per-role `--settings` with the role's network profile (DEC-158) and `Edit` deny rules, sets `GOV_ROLE`, `GOV_TICKET` and a per-session temp directory (DEC-159); configuration never comes from the repository; Claude Code is pinned at 2.1.285 or later | B3, EVIDENCE §5.2–5.4, DEC-158, DEC-159, DEC-161 |
| **CAP-62** (new, W1) | The guard denies any Bash call carrying `dangerouslyDisableSandbox: true` | B3, EVIDENCE §5.4 |
| CAP-49 Qualification oracle | Acceptance: hidden from a worker's Bash by the sandbox (silently: the directory looks empty), and from every session started in the repository root by a `Read` deny rule in the committed `.claude/settings.json` and by the guard denying any tool call that names the oracle path. New W1 `covers` items for the hiding; the qualification run stays W3. Providers W1-46, W1-47 | B3, EVIDENCE §5.4, DEC-162 |
| CAP-25 Tool registry and installs | Install path **unchanged** (DEC-157). New W1 `covers` item: Claude Code joins the registry pins at 2.1.285 or later, CLI aligned with the VS Code extension (W1-48). Worker roles never install system-wide; in a worker session the sandbox stops what the install classifier misses | B3, P-1 |
| CAP-22 Roles | Providers add W1-05; `CAP-22.a` is delivered first by W1-05 (minimal definitions), then replaced by W1-33 | B4, DEC-119 |
| CAP-32 Research and experiments | New W1 `covers` item: experiments run in sandboxes outside production paths, leave an evidence record, and change a closed specification only through CIT-P. Wave stays W3 for the full lifecycle | A1 |
| CAP-30 Readiness | New `covers` items: the order of specification work (W1); the UX row closes only on owner-approved, scenario-derived designs, and acceptance tests include visual checks (W2, with the UX role) | A2, A3 |
| CAP-33 Change impact | New W1 `covers` item: a contradicting finding opens a CIT-P with three costed options (apply now, defer, re-baseline); the owner chooses; every version is kept | A4 |
| CAP-40 Telemetry | New W1 `covers` item: per ticket, KPI disputes, acceptance tests rewritten after implementation began (with reason) and governance share; all three reported at the Wave 1 exit. Provider W1-42 added | A5 |
| CAP-38 Verification | New W1 `covers` items: probe findings reach the test designer as described behaviours, never code; a FULL ticket's post-green probe is done by a fresh reviewer that writes nothing | A6, A7 |
| CAP-37 Checkpoints | Wave note only (no acceptance change): until W1-25, the orchestrator's checkpoint lives in `.gov-runtime/scratch/orchestrator/` | B1 |

Capabilities read and found not affected: CAP-03 (secrets: the deny rules are unchanged), CAP-05, CAP-21, CAP-34,
CAP-39, CAP-47, CAP-59. `readiness-dimensions.yaml` and `SOURCE_MAP.csv` are not changed: the 26 rows are verbatim
from the Framework, and the source map maps the originals, which this change does not touch.

### 3.3 ADRs and Charter

| File | Clause | Change | Why |
|---|---|---|---|
| ADR-0002 | §1 Layers, L3 Enforcement | Adds the OS sandbox as the outer layer for a worker session's Bash, `PostToolUseFailure`, the escape-hatch denial and the oracle rule | B3, DEC-161, DEC-162 |
| ADR-0002 | §1 Layers, L4 `gov` CLI | Adds `launch` | B3 |
| ADR-0002 | §2 Stack | Adds Claude Code (≥ 2.1.285, CLI aligned with the VS Code extension), bubblewrap 0.9.0 and socat 1.8.0.0 (DEC-141) | B3 |
| ADR-0002 | §6 Operating model | Orchestrator write scope (DEC-156); worker sessions start through the launcher, in-session subagents stay for read-only work (DEC-161). Install lines unchanged | B1, B3, P-5 |
| ADR-0002 | Consequences; frontmatter; "More Information" | New glue figure; decisions list and range | New tickets |
| ADR-0001 | Decision Outcome, "Guardrails, not a boundary" | One sentence: the sandbox is a stronger guardrail for Bash, still not a boundary against the owner's own privileges (hooks, MCP servers, the file tools and the orchestrator's own session run outside it). "Tool installs" unchanged | B3, P-1 |
| Charter v5 | All sections | **No change at all** (P-1 answered (d), so the install bullet of §6 stands). Principle 7 (default-deny allow-lists) and the threat model hold as written; the sandbox is one more guardrail | — |

### 3.4 Wave 1 WBS and tickets

New tickets (numbers follow the last existing one, W1-44):

| W1 | Title | Role | Profile | Depends on | est. LOC | Why |
|---|---|---|---|---|---|---|
| W1-45 | Orchestrator write scope | engineer | FULL | W1-05 | 40 | B1, DEC-156. A guard change: for the orchestrator the guard enforces only the `tests/acceptance/**` exclusion. Created `in_progress`; bootstrapped as DEC-150 states |
| W1-46 | Worker session launcher (`gov launch`) | engineer | FULL | W1-07, W1-48 | 180 | B3 ticket 1; DEC-158, DEC-159, DEC-161 (network profiles, per-session temp directory, the three required tests) |
| W1-47 | Guard hardening: escape hatch, failed commands, oracle path | engineer | FULL | W1-45 | 60 | B3 ticket 2; DEC-162 (the committed `Read` deny rule and the guard rule on the oracle path). Follows W1-45 because both change the same guard files |
| W1-48 | Claude Code version pin | orchestrator | LITE | W1-06 | 10 | B3 ticket 3. Needs the tool registry of W1-06 |

Existing tickets changed:

| Ticket | Status | Change | Why |
|---|---|---|---|
| W1-05 `DAEO-m7u4` | closed | Its five role-definition KPI lines cite `[CAP-22.a]`; `CAP-22` added to sources. No status change, no new work | B4, DEC-119 |
| W1-04 `DAEO-78bn` | closed | No KPI change. A note records that the sandbox now backs its misses | B3 |
| W1-30 `DAEO-2lwj` | open | KPI: closing a FULL ticket needs a post-green probe record from a session other than the implementer | A7 |
| W1-31 `DAEO-6mk8` | open | KPI: the close record carries the three learning metrics | A5 |
| W1-33 `DAEO-xog0` | open | KPI: replaces W1-05's minimal definitions, and the orchestrator definition states its write scope (DEC-156); `.claude/agents/**` added to its `allowed_paths` so it can replace them. No install rewording | B1, B4 |
| W1-35 `DAEO-0i6h` | open | KPIs: experiments and their evidence record; order of specification work; three-option CIT-P; test design takes probe findings as described behaviours | A1, A2, A4, A6 |
| W1-42 `DAEO-gjjf` | open | Depends also on W1-46 and W1-47; the exit run starts its sessions through the launcher; reports the three learning metrics | A5, B3 |

WBS sections: frontmatter decisions; rules (installs, bootstrap); §1 table; §2 layers and critical path; §3 size;
§4 exit criterion 3 (containment now names the sandbox); §5 source merge; §6 Wave 2 (the untested sandbox cases, UX
visual testing).

**Critical path.** Expected unchanged in its tickets: the new tickets hang off W1-05, W1-06 and W1-07 and rejoin at
W1-42, and the longest chain still runs through retrieval, context and adoption. The apply step recomputes it.

**Size.** Implementation +280 LOC (5,090 → 5,370); ops/config +10. (Before the answers: +240.)

### 3.5 `governance/project/bootstrap.md`

| Residual | Change |
|---|---|
| Outside-repository writes through opaque Bash forms (DEC-123) | Closed for Bash in launched worker sessions; open for the orchestrator's own session (guard alone) |
| Install misses of W1-04 (prefix commands, subshell downloads, unlisted managers, evasive spellings, option-before-`-m`) | Closed for Bash in launched worker sessions, by the write wall and the network wall; open for the orchestrator's own session. The false asks stay |
| File-tool reads and writes | Restated: guard and permission rules only |
| Anything a hook or MCP server does | Restated: outside the sandbox |
| The shared `$TMPDIR` | The launcher sets a per-session temp directory (DEC-159); it becomes a residual only if W1-46's acceptance test shows it can't be overridden |
| The qualification oracle (DEC-162) | New: hidden by the committed `Read` deny rule and the guard rule (W1-47); an opaque Bash read in the orchestrator's own session is an accepted residual |
| The untested sandbox cases (DEC-160) | New: residuals until the Wave 2 experiment |
| The guard's quoting limit (DEC-128), W1-03's residuals (DEC-134, DEC-144), the DEC-135 edge cases | Unchanged; they concern writes inside the repository |

Also recorded there: the two W1-05 confirmations (B2), and the orchestrator checkpoint location (B1).

### 3.6 Plan validator

`docs/plan/tools/validate_s1.py`: the "writes only under docs/ and .tickets/" check is scoped to the S1 branch;
counts move to 62 capabilities and 48 tickets; new checks cover every item in §3.1–3.5. It stays runnable from the
repository root.

### 3.7 Tests and code

| Area | Impact |
|---|---|
| Code | None in this change. W1-45, W1-46 and W1-47 will change `src/gov/guard/**`, the hook entries, the committed `.claude/settings.json` (the oracle `Read` deny rule, W1-47) and add `src/gov/launch/**` |
| `tests/acceptance/W1-01` | Skips after the switch-over, by design (B2). No change |
| `tests/acceptance/W1-02`, `W1-03` | **Affected** (corrected after S2-A round 1, F-01). DEC-156 replaces the orchestrator rule these tests assert (the orchestrator held to its active ticket's `allowed_paths`). Those tests are revised by the Independent Test Designer under W1-45, as rewrites after implementation (reason: owner correction, DEC-156; counted under DEC-106). The KPI text of W1-02 and W1-03 is unchanged, and holds as written for every other role |
| `tests/acceptance/W1-04`, `W1-05` | Not affected by DEC-156. W1-04's tests still pass after W1-46 adds the research role's install exception (DEC-163); W1-46 carries that as a KPI |
| New acceptance tests | `tests/acceptance/W1-45/` … `W1-48/`, written by the Independent Test Designer before each implementation |

## 4. Findings made while listing the impact

1. **`PostToolUseFailure` is already wired.** W1-05 registered the containment check on `PostToolUseFailure` for Bash
   in this repository's settings (`bootstrap.md`, "Switch-over"). W1-47 therefore adds no hook entry here; its KPI
   makes the registration a tested requirement, in this repository and in the kernel template.
2. **The CLI is below the pin.** The spike ran on CLI 2.1.284; the pin is 2.1.285 or later. Raising it is an
   install, done by the orchestrator under DEC-083 (DEC-157).
3. **The launcher does not reach an interactive VS Code session.** `--settings` is a command-line flag. Asked as
   P-5 and answered by DEC-156 and DEC-161: the orchestrator's interactive session is not sandboxed; the launcher
   serves worker sessions only.
4. **Where the oracle is hidden from the unsandboxed orchestrator** was left open by DEC-161. Answered by DEC-162.

## 5. Questions asked, and the owner's answers

Asked in chat as decision packages P-1…P-5 (MR-6, DEC-093). All are answered; the apply step follows the answers.

| Package | Question | Recommendation | Owner's answer | Decision |
|---|---|---|---|---|
| DP-7 | The orchestrator's standing rights | (brief: standing paths plus a commit rule) | Corrected: the orchestrator may write anywhere in the repository except `tests/acceptance/**`; its session is not sandboxed | DEC-156 |
| P-1 | How do approved installs happen under a strict sandbox with no network? | (a) the owner executes at the operator console | (d), the owner's own: installs stay as DEC-083; worker roles never install system-wide | DEC-157 |
| P-2 | The network allowlist per role | Empty for every role in Wave 1 | Orchestrator unrestricted; research and experiment work gets a broad, owner-extensible allowlist; engineer, test designer and auditor empty | DEC-158 |
| P-3 | The shared `$TMPDIR` | A per-session temp directory set by the launcher | As recommended, for worker sessions; a residual if it can't be overridden | DEC-159 |
| P-4 | The untested sandbox cases | A Wave 2 experiment | As recommended | DEC-160 |
| P-5 | How the interactive orchestrator session gets the sandbox configuration | Start it through the launcher from a terminal | The sandbox applies to launched worker sessions only | DEC-161 |
| — | Where the oracle's `Read` deny rule lives for the unsandboxed orchestrator | (none given) | The committed `.claude/settings.json` plus a guard rule on the oracle path, both from W1-47; an opaque Bash read in the orchestrator's session is an accepted residual | DEC-162 |

## 6. Repair after the S2-A round-1 audit

S2-A's round-1 verdict was ACCEPT_WITH_FINDINGS. The owner answered its two decision packages and added three
decisions in the same message. The impact of each is listed here; the execution is in `S2-CIT-E.md` §6.

| Decision | Subject | Impact |
|---|---|---|
| DEC-163 (DP-1) | A minimal research role in the Wave 1 roster | Charter v5 §6 roster row; Contract envelope "Tool installs", CAP-22 (`CAP-22.d`), CAP-25 (acceptance, `CAP-25.e`), CAP-32 wave note; W1-46 (role file, guard change, +40 LOC, now depends also on W1-47); W1-33 and W1-04 (a KPI and a note); ADR-0002 §1 and §6; WBS; `bootstrap.md` |
| DEC-164 (DP-2) | Subagents in a sandboxed worker and `excludedCommands` are open residuals, in EXP-002; the launcher sets no `excludedCommands` | `CAP-61.a`, `CAP-61.f`; W1-46 KPIs; ADR-0002 §6; WBS §6; `bootstrap.md` |
| DEC-165 | The lite upstream lesson loop (Wave 3) | Charter v5 §7 non-goal row; CAP-41 (wave note, `CAP-41.e` reworded, `CAP-41.f`…`CAP-41.j`), `CAP-45.b`, `CAP-58.g`; ADR-0002 §6; WBS §7. No Wave 1 ticket changes |
| DEC-166 | `gov discover` (Wave 2) | `CAP-32.d`; ADR-0002 §1 L4 and §6; WBS §6. No Wave 1 ticket changes |
| DEC-167 | A plain-language impact question triggers the impact assessment | `CAP-33.f` (W1, W1-35), `CAP-33.g` (W2); one KPI on W1-35; WBS rules and §6 |
| DEC-168 | Scope and severity in the Wave 1 lesson schema | `CAP-41.f` moves to W1 on W1-08; one KPI on W1-08, the failure KPI of W1-44; WBS §5 and §7 |
| DEC-169 | The validator's fingerprint fallback and S2 scope check (S2A-F-08) | `validate_s1.py` only |
| DEC-170 | Sandbox instruction tokens are reported apart from the governance share (S2A-F-07) | One KPI on W1-31, with `CAP-40.d` (added in the round-2 repair); ADR-0002 "Consequences"; WBS §1, §3; `bootstrap.md` |
| DEC-171 | An orchestrator change outside its ticket's paths is a record, not a containment finding (S2A-F-01) | `CAP-58.e`; W1-45 (KPI, source, body); ADR-0002 §6; WBS rules; `bootstrap.md` |

DEC-170 and DEC-171 are the owner's confirmations on S2A-F-07 and S2A-F-01. The audit's other findings (S2A-F-01, F-03, F-04, F-06, F-07, F-09, F-10) change ticket KPIs, estimates (W1-30, W1-31:
+50 LOC), `CAP-49.c`, `CAP-58.a`, `CAP-58.b`, `CAP-58.e`, `CAP-61.c`, ADR-0002 and `bootstrap.md`; S2-CIT-E §6.1 lists
them one by one.

The three options of DEC-105 were not re-asked: the owner gave these as decisions to apply in this change.

## 7. Repair after the S2-A round-2 audit

S2-A's round-2 verdict was ACCEPT_WITH_FINDINGS: no BLOCKER, 1 MAJOR, 5 MINOR. The owner answered its two decision
packages. The impact is listed here; the execution is in `S2-CIT-E.md` §7.

| Decision or finding | Subject | Impact |
|---|---|---|
| DEC-172 (DP-3, S2A-F-11) | The install and download ask rules leave the committed `.claude/settings.json`; the guard's install rule stands alone. Withdraws the settings second line of DEC-120 and DEC-151 | New `CAP-25.f` (W1, W1-47), CAP-25 provider and sources; W1-47 (one KPI, one failure KPI, sources, body); W1-46 (the install KPI, one failure KPI, source, body); a note on W1-04; ADR-0002 §6; WBS rules, §1, §3, §5; `bootstrap.md` |
| DEC-173 (DP-4, S2A-F-12) | Charter §6's install sentence names the research exception | Charter v5 §6, one line, and its frontmatter; `validate_s1.py` (five Charter lines); S2-CIT-E §6.3 |
| S2A-F-12 | Three more sentences said that only the orchestrator installs | ADR-0001 "Tool installs"; ADR-0002 §6 orchestrator bullet; W1-33 KPI 2 |
| S2A-F-13 | The launcher's deny list is computed at launch; later paths; exceptions | `CAP-61.c`, `CAP-25.e`; W1-46 (KPI, failure KPI, body); ADR-0002 §6; WBS rules; `bootstrap.md` |
| S2A-F-14 | Where the oracle path is held | `CAP-49.c`; W1-47 (KPI, body); ADR-0002 §6; `bootstrap.md` |
| S2A-F-15 | DEC-170 had no Contract item | New `CAP-40.d` (W1, W1-31), CAP-40 sources; the W1-31 KPI cites it |
| S2A-F-16 | This record and the WBS header stopped short | §6 above (DEC-170, DEC-171); WBS opening paragraph and frontmatter |
| DEC-174 (round-3 closure check, S2A-F-17) | W1-47 extends the guard's install rule to `uv add`, `uv sync`, `uv run --with` and `uvx` | New `CAP-25.g` (W1, W1-47), CAP-25 sources; W1-47 (one KPI, one failure KPI, sources, `tests/unit/install/**` in `allowed_paths`, body); W1-46 (the install KPI names the four forms); ADR-0002 §6; WBS rules, §1, §3, §5; `bootstrap.md` |
| S2A-F-17, S2A-F-18, O-12 (round-3 closure check) | The full list of commands that lose their settings prompt, from a run of the classifier; W1-46 failure KPI 4 narrowed; `.git/hooks` and `.git/config` | `bootstrap.md`; S2-CIT-E §7.4 point 3 and §8; W1-46 |

The three options of DEC-105 were not re-asked: the owner gave both answers as decisions to apply in this change.
