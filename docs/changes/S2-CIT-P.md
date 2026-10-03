---
id: S2-CIT-P
type: change-impact-proposal
status: PROPOSED
date: 2026-10-03
branch: s2/spec
base: w1/integrate @ 442e9c3
author: product-spec (S2, single author)
audit: S2-A, a fresh Independent Auditor (DEC-088)
decisions_carried: [DEC-102, DEC-103, DEC-104, DEC-105, DEC-106, DEC-119, DEC-136, DEC-137, DEC-138, DEC-147]
---

# S2 — Change-impact proposal (CIT-P) on the Gov OS specification

This change brings the closed Gov OS specification up to date with decisions the owner took during the Wave 1
bootstrap, and with the result of the sandbox experiment EXP-001. It changes specification files only: the register,
Contract v4, ADR-0001, ADR-0002, the Wave 1 WBS, tickets, `bootstrap.md` and the plan validator. It changes no code,
hook, settings file or test.

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
| B1 | Orchestrator standing rights (DP-7 option (b), extended) | Owner, S2 brief | New |
| B2 | Two confirmations from W1-05 | Owner, S2 brief | New |
| B3 | EXP-001 accepted as ADOPT-PARTIAL | Owner, S2 brief; `spike-sandbox/EVIDENCE.md` | New |
| B4 | W1-05 provides the minimal role definitions first | Owner, S2 brief; DEC-119 | DEC-119 left it for this change |
| B5 | Scope and extension of `validate_s1.py` | Owner, S2 brief | New |
| C | Four open points from EVIDENCE §4 and §5.5, plus one found here | §5 below | Open: asked as packages |

## 2. The three options (DEC-105)

| Option | What it means here | Cost |
|---|---|---|
| **Apply now** (chosen by the owner in the S2 brief) | Contract v4 becomes v4.1; four new Wave 1 tickets; 39 open tickets keep their KPIs except the six named in §3.4 | This change, one audit (S2-A), about 240 LOC of new Wave 1 glue. No closed ticket's code is invalidated |
| Defer | Record EXP-001 and continue Wave 1 on the guard alone | No work now. The opaque-write and install residuals stay open; DEC-102…DEC-106, DEC-136 and DEC-137 stay outside the Contract while acceptance tests are written against it |
| Re-baseline | Reopen the enforcement part of the specification and re-plan W1-02…W1-05 around the sandbox | Retires working, tested guard code that EXP-001 shows is still needed for the file tools. Not justified by the evidence |

## 3. Impact

### 3.1 Decision register

| Item | Change | Why |
|---|---|---|
| New section 26 (register v0.26) | Five decisions for B1–B5, then one per owner answer to §5 | The brief asks for each as a new DEC, `ACCEPTED (owner, 2026-10-03)` |
| DEC-083 | Amended only if package P-1 is answered (a) or (c): who executes an approved install | "The orchestrator installs" can't run under a sandbox with no network |
| DEC-138 | Outcome recorded by the new EXP-001 decision | The spike has a verdict |
| DEC-123, DEC-147 | Their residuals are closed for Bash by the new EXP-001 decision | EVIDENCE §5.1 |
| DEC-108 (kernel scratch set) | Refined: `.gov-runtime/scratch/**` is a standing orchestrator path, and its checkpoint lives in `.gov-runtime/scratch/orchestrator/` until W1-25 | B1 |
| DEC-119 | Its "for the post-bootstrap spec change" note is carried out | B4 |

No ACCEPTED or DONE entry is edited; amendments are new entries that name what they amend.

### 3.2 Contract v4 → v4.1 (`CONTRACT_v4.md` and `contract.yaml`)

| Item | Change | Why |
|---|---|---|
| Frontmatter, title line | Version 4.1, change log, decisions list | The brief |
| §1 Counts | 60 → 62 capabilities; W1 KEPT 36 → 38 | Two capabilities added |
| §2 Envelope, "Boundary" | Adds the containment layers: the OS sandbox for Bash, the guard and permission rules for the file tools; neither is a security boundary (ADR-0001 unchanged in substance) | B3 |
| §2 Envelope, "Tool installs" | Restated per the answer to P-1 | P-1 |
| MR-3 | Acceptance adds the orchestrator commit rule (`tests/acceptance/**` is never covered unless the committer is the test designer); providers add the new guard tickets | B1 |
| MR-1 | Acceptance unchanged; DEC-103 is carried in CAP-30 | A2 |
| **CAP-58** Path guards | Claim split: a Bash write outside the repository is stopped by the OS sandbox; a file-tool write is stopped by permission rules and the guard; inside the repository the guard and the containment check hold. New `covers` items: sandbox wall for Bash; orchestrator standing paths and commit rule; failed commands arrive as `PostToolUseFailure` and a call refused by a deny rule reaches no hook. New providers | B1, B3, EVIDENCE §5.4 |
| **CAP-61** (new, W1) | The launcher refuses to start a session unless the sandbox is on, strict and fail-closed; it builds per-role `--settings` and sets `GOV_ROLE` and `GOV_TICKET`; configuration never comes from the repository; Claude Code is pinned at 2.1.285 or later | B3, EVIDENCE §5.2–5.4 |
| **CAP-62** (new, W1) | The guard denies any Bash call carrying `dangerouslyDisableSandbox: true` | B3, EVIDENCE §5.4 |
| CAP-49 Qualification oracle | Acceptance: hidden from Bash by the sandbox and from the file tools by a `Read` deny rule; hiding is silent. New W1 `covers` item for the hiding itself; the qualification run stays W3 | B3, EVIDENCE §5.4 |
| CAP-25 Tool registry and installs | Install path restated per P-1; the sandbox, not the install classifier, is what stops an unapproved install from writing or reaching the network; Claude Code joins the registry pins | B3, P-1 |
| CAP-22 Roles | Providers add W1-05; `CAP-22.a` is delivered first by W1-05 (minimal definitions), then replaced by W1-33 | B4, DEC-119 |
| CAP-32 Research and experiments | New W1 `covers` item: experiments run in sandboxes outside production paths, leave an evidence record, and change a closed specification only through CIT-P. Wave stays W3 for the full lifecycle | A1 |
| CAP-30 Readiness | New `covers` items: the order of specification work (W1); the UX row closes only on owner-approved, scenario-derived designs, and acceptance tests include visual checks (W2, with the UX role) | A2, A3 |
| CAP-33 Change impact | New W1 `covers` item: a contradicting finding opens a CIT-P with three costed options (apply now, defer, re-baseline); the owner chooses; every version is kept | A4 |
| CAP-40 Telemetry | New W1 `covers` item: per ticket, KPI disputes, acceptance tests rewritten after implementation began (with reason) and governance share; all three reported at the Wave 1 exit. Provider W1-42 added | A5 |
| CAP-38 Verification | New W1 `covers` items: probe findings reach the test designer as described behaviours, never code; a FULL ticket's post-green probe is done by a fresh reviewer that writes nothing | A6, A7 |
| CAP-37 Checkpoints | Wave note only: until W1-25, the orchestrator's checkpoint lives in `.gov-runtime/scratch/orchestrator/` | B1 |

Capabilities read and found not affected: CAP-03 (secrets: the deny rules are unchanged), CAP-05, CAP-21, CAP-34,
CAP-39, CAP-47, CAP-59. `readiness-dimensions.yaml` and `SOURCE_MAP.csv` are not changed: the 26 rows are verbatim
from the Framework, and the source map maps the originals, which this change does not touch.

### 3.3 ADRs and Charter

| File | Clause | Change | Why |
|---|---|---|---|
| ADR-0002 | §1 Layers, L3 Enforcement | Adds the OS sandbox as the outer layer for Bash, and `PostToolUseFailure` | B3 |
| ADR-0002 | §1 Layers, L4 `gov` CLI | Adds `launch` | B3 |
| ADR-0002 | §2 Stack | Adds Claude Code (≥ 2.1.285, CLI aligned with the VS Code extension), bubblewrap 0.9.0 and socat 1.8.0.0 (DEC-141) | B3 |
| ADR-0002 | §6 Operating model | Orchestrator standing paths and commit rule; install path per P-1; sessions start through the launcher | B1, B3, P-1 |
| ADR-0002 | Consequences; frontmatter; "More Information" | New glue figure; decisions list and range | New tickets |
| ADR-0001 | Decision Outcome, "Guardrails, not a boundary" | One sentence: the sandbox is a stronger guardrail for Bash, still not a boundary against the owner's own privileges (hooks, MCP servers and the file tools run outside it). "Tool installs" per P-1 | B3, P-1 |
| Charter v5 | §6 Authority, the install bullet | Changed only if P-1 is answered (a) or (c) | P-1 |
| Charter v5 | §2 Threat model, §3 Principles, §4 Master rules, §5, §7, §8 | **No change.** Principle 7 (default-deny allow-lists) and the threat model hold as written; the sandbox is one more guardrail | — |

### 3.4 Wave 1 WBS and tickets

New tickets (numbers follow the last existing one, W1-44):

| W1 | Title | Role | Profile | Depends on | est. LOC | Why |
|---|---|---|---|---|---|---|
| W1-45 | Orchestrator standing rights and commit rule | engineer | FULL | W1-05 | 60 | B1. A guard change. Created `in_progress`; bootstrapped as the brief states |
| W1-46 | Session launcher (`gov launch`) | engineer | FULL | W1-07, W1-48 | 150 | B3 ticket 1 |
| W1-47 | Guard hardening: escape hatch and failed commands | engineer | FULL | W1-45 | 30 | B3 ticket 2. Follows W1-45 because both change the same guard files |
| W1-48 | Claude Code version pin | orchestrator | LITE | W1-06 | 10 | B3 ticket 3. Needs the tool registry of W1-06 |

Existing tickets changed:

| Ticket | Status | Change | Why |
|---|---|---|---|
| W1-05 `DAEO-m7u4` | closed | Its five role-definition KPI lines cite `[CAP-22.a]`; `CAP-22` added to sources. No status change, no new work | B4, DEC-119 |
| W1-04 `DAEO-78bn` | closed | No KPI change. A note records that the sandbox now backs its misses | B3 |
| W1-06 `DAEO-ipqy` | open | Install KPI wording per P-1 | P-1 |
| W1-30 `DAEO-2lwj` | open | KPI: closing a FULL ticket needs a post-green probe record from a session other than the implementer | A7 |
| W1-31 `DAEO-6mk8` | open | KPI: the close record carries the three learning metrics | A5 |
| W1-33 `DAEO-xog0` | open | KPI: replaces W1-05's minimal definitions; the orchestrator definition carries the standing paths; install wording per P-1 | B1, B4, P-1 |
| W1-35 `DAEO-0i6h` | open | KPIs: experiments and their evidence record; order of specification work; three-option CIT-P; test design takes probe findings as described behaviours | A1, A2, A4, A6 |
| W1-42 `DAEO-gjjf` | open | Depends also on W1-46 and W1-47; the exit run starts its sessions through the launcher; reports the three learning metrics | A5, B3 |

WBS sections: frontmatter decisions; rules (installs, bootstrap); §1 table; §2 layers and critical path; §3 size;
§4 exit criterion 3 (containment now names the sandbox); §5 source merge; §6 Wave 2 (the untested sandbox cases, UX
visual testing).

**Critical path.** Expected unchanged in its tickets: the new tickets hang off W1-05, W1-06 and W1-07 and rejoin at
W1-42, and the longest chain still runs through retrieval, context and adoption. The apply step recomputes it.

**Size.** Implementation +240 LOC (5,090 → 5,330); ops/config +10.

### 3.5 `governance/project/bootstrap.md`

| Residual | Change |
|---|---|
| Outside-repository writes through opaque Bash forms (DEC-123) | Closed for Bash, once sessions start through the launcher |
| Install misses of W1-04 (prefix commands, subshell downloads, unlisted managers, evasive spellings, option-before-`-m`) | Closed for Bash, by the write wall and the network wall. The false asks stay |
| File-tool reads and writes | Restated: guard and permission rules only |
| Anything a hook or MCP server does | Restated: outside the sandbox |
| The shared `$TMPDIR` | Restated, or closed, per P-3 |
| The guard's quoting limit (DEC-128), W1-03's residuals (DEC-134, DEC-144), the DEC-135 edge cases | Unchanged; they concern writes inside the repository |

Also recorded there: the two W1-05 confirmations (B2), and the orchestrator checkpoint location (B1).

### 3.6 Plan validator

`docs/plan/tools/validate_s1.py`: the "writes only under docs/ and .tickets/" check is scoped to the S1 branch;
counts move to 62 capabilities and 48 tickets; new checks cover every item in §3.1–3.5. It stays runnable from the
repository root.

### 3.7 Tests and code

| Area | Impact |
|---|---|
| Code | None in this change. W1-45, W1-46 and W1-47 will change `src/gov/guard/**`, the hook entries and add `src/gov/launch/**` |
| `tests/acceptance/W1-01` | Skips after the switch-over, by design (B2). No change |
| `tests/acceptance/W1-02…W1-05` | No KPI of a closed ticket changes, so no existing acceptance test is invalidated |
| New acceptance tests | `tests/acceptance/W1-45/` … `W1-48/`, written by the Independent Test Designer before each implementation |

## 4. Findings made while listing the impact

1. **`PostToolUseFailure` is already wired.** W1-05 registered the containment check on `PostToolUseFailure` for Bash
   in this repository's settings (`bootstrap.md`, "Switch-over"). W1-47 therefore adds no hook entry here; its KPI
   makes the registration a tested requirement, in this repository and in the kernel template.
2. **The CLI is below the pin.** The spike ran on CLI 2.1.284; the pin is 2.1.285 or later. Raising it is an
   install, so who does it follows P-1.
3. **The launcher does not reach an interactive VS Code session.** `--settings` is a command-line flag. The sources
   don't say how the orchestrator's interactive session gets the sandbox configuration. Asked as P-5.

## 5. Open questions for the owner

Asked in chat as decision packages P-1…P-5 (MR-6, DEC-093). Each answer becomes a new decision, and the apply step
follows it.

| Package | Rank | Question | Recommendation |
|---|---|---|---|
| P-1 | P1 | How do approved installs happen under a strict sandbox with no network? | (a) the orchestrator proposes, the owner executes at the operator console |
| P-2 | P2 | The network allowlist per role | Empty for every role in Wave 1 |
| P-3 | P2 | The shared `$TMPDIR` | A per-session temp directory set by the launcher |
| P-4 | P3 | The untested sandbox cases | A Wave 2 experiment |
| P-5 | P2 | How the interactive orchestrator session gets the sandbox configuration | Start it through the launcher from a terminal |
