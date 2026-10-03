---
id: S2-CIT-E
type: change-execution-record
status: APPLIED
date: 2026-10-03
branch: s2/spec
base: w1/integrate @ 442e9c3
proposal: S2-CIT-P
author: product-spec (S2, single author)
audit: S2-A, a fresh Independent Auditor (DEC-088)
decisions_recorded: [DEC-150, DEC-151, DEC-152, DEC-153, DEC-154, DEC-155, DEC-156, DEC-157, DEC-158, DEC-159, DEC-160, DEC-161, DEC-162, DEC-163, DEC-164, DEC-165, DEC-166, DEC-167, DEC-168, DEC-169, DEC-170, DEC-171]
repair: after the S2-A round-1 audit (ACCEPT_WITH_FINDINGS), §6
decisions_carried: [DEC-102, DEC-103, DEC-104, DEC-105, DEC-106, DEC-119, DEC-136, DEC-137, DEC-138, DEC-147]
---

# S2 — Change-execution record (CIT-E) on the Gov OS specification

This records what the S2 specification change did, file by file, against the proposal `docs/changes/S2-CIT-P.md`.
The owner chose "apply now" (DEC-105) and answered the open questions on 2026-10-03 (DEC-156…DEC-162). The change
touched specification files only: no code, hook, settings file or test.

§1 to §5 record the first application. §6 records the repair after the S2-A round-1 audit, and gives the figures as
they stand now. Where the repair corrected a statement in §1 to §5, the statement is corrected in place and marked.

## 1. Summary

| Item | Before | After |
|---|---|---|
| Register | v0.25, last entry DEC-149 | v0.26, DEC-150…DEC-162 (13 decisions) |
| Contract | v4, 60 capabilities | v4.1, 62 capabilities (CAP-61, CAP-62 added) |
| Contract items changed | — | MR-3; envelope "Boundary" and "Tool installs"; CAP-22, 25, 30, 32, 33, 37, 38, 40, 49, 58 |
| `covers` items | — | 20 added (18 in Wave 1, each with a provider ticket; 2 in Wave 2); 1 reworded (CAP-22.a) |
| Wave 1 tickets | 44 | 48 (W1-45…W1-48) |
| Wave 1 glue (class implementation) | ≈ 5,090 LOC | ≈ 5,370 LOC (+280) |
| Critical path | W1-01 → … → W1-43 | Unchanged |
| Charter v5 | — | Not changed in the first application. The repair changes four lines (§6) |

Of the 20 new `covers` items, 18 are Wave 1 and name a provider ticket; CAP-30.g (UX, DEC-104) and CAP-61.f (untested
sandbox cases, DEC-160) are Wave 2.

## 2. What changed, file by file

### `docs/DECISION_REGISTER.md`

Section 26 appended (register v0.26). No earlier entry was edited.

| Decision | Subject |
|---|---|
| DEC-150 | DP-7: the orchestrator's standing rights, as given in the brief (amended by DEC-156) |
| DEC-151 | Two confirmations from W1-05 |
| DEC-152 | EXP-001 accepted as ADOPT-PARTIAL |
| DEC-153 | New Wave 1 tickets: launcher, guard hardening, Claude Code pin |
| DEC-154 | The W1-05 provider change |
| DEC-155 | The plan validator after S1 |
| DEC-156 | DP-7 corrected: the orchestrator writes anywhere except `tests/acceptance/**`; its session is not sandboxed |
| DEC-157 | P-1: installs stay as DEC-083; worker roles never install system-wide |
| DEC-158 | P-2: network profiles per role |
| DEC-159 | P-3: per-session temp directory for worker sessions |
| DEC-160 | P-4: the untested sandbox cases go to a Wave 2 experiment |
| DEC-161 | P-5: the sandbox applies to launched worker sessions only |
| DEC-162 | The oracle is hidden from every session started in the repository root (committed `Read` deny rule plus a guard rule, both from W1-47) |

### `docs/contract/CONTRACT_v4.md` and `docs/contract/contract.yaml`

Both files carry the same content; the validator now checks that. The file names and the id `CONTRACT-v4` are kept.

| Item | Change | Decisions |
|---|---|---|
| Version | 4.1, with a change log (4.0, 4.1); decisions list extended | — |
| §1 Counts | W1 KEPT 36 → 38; all 60 → 62 | DEC-152, DEC-153 |
| §2 Boundary | Two guardrail layers stated: the OS sandbox for a launched worker's Bash; the guard and permission rules for the file tools and for the orchestrator's unsandboxed session | DEC-152, DEC-156, DEC-161 |
| §2 Tool installs | The DEC-083 sentence is unchanged. Added: worker roles never install system-wide | DEC-157 |
| MR-3 | Acceptance adds the orchestrator exception; provider W1-45 | DEC-150, DEC-156 |
| CAP-22 | `CAP-22.a` delivered first by W1-05, then W1-33; provider W1-05 added | DEC-119, DEC-154 |
| CAP-25 | New `CAP-25.d` (Claude Code pin in the registry, W1-48). Acceptance, lite form and `CAP-25.b` unchanged | DEC-153, DEC-157 |
| CAP-30 | New `CAP-30.f` (order of specification work, W1, W1-35) and `CAP-30.g` (UX before build with visual checks, W2) | DEC-103, DEC-104 |
| CAP-32 | New `CAP-32.c` (experiments are part of discovery, W1, W1-35); wave note; provider W1-35 | DEC-102 |
| CAP-33 | New `CAP-33.e` (three costed options, W1, W1-35) | DEC-105 |
| CAP-37 | Wave note: the orchestrator's checkpoint location until W1-25 | DEC-150, DEC-156 |
| CAP-38 | New `CAP-38.e` (probe findings as described behaviours, W1-35) and `CAP-38.f` (post-green probe by a fresh reviewer, W1-30) | DEC-136, DEC-137 |
| CAP-40 | New `CAP-40.c` (three learning metrics, W1-31 and W1-42); provider W1-42 | DEC-106 |
| CAP-49 | Acceptance extended; new `CAP-49.b` (hidden from a worker's Bash by the sandbox, W1-46) and `CAP-49.c` (committed `Read` deny rule plus guard rule for every root session, W1-47). The qualification run stays W3 | DEC-152, DEC-161, DEC-162 |
| CAP-58 | Outcome and acceptance split the claim; new `CAP-58.d` (sandbox wall, W1-46), `CAP-58.e` (orchestrator write scope, W1-45), `CAP-58.f` (`PostToolUseFailure`, W1-47) | DEC-152, DEC-153, DEC-156, DEC-161 |
| **CAP-61** (new) | Worker session launcher and OS sandbox: six `covers` items (start refusal; per-role settings and `GOV_ROLE`/`GOV_TICKET`; network profiles; per-session temp directory; Claude Code pin; the Wave 2 experiment) | DEC-152, DEC-153, DEC-158…DEC-161 |
| **CAP-62** (new) | Sandbox escape hatch denied (W1-47) | DEC-153 |

### `docs/adr/ADR-0002-architecture-and-stack.md`

- Frontmatter decisions extended.
- §1 L3: the OS sandbox layer, `PostToolUseFailure`, the escape-hatch denial, the oracle rule. L4: `launch`.
- §2 Stack: Claude Code (≥ 2.1.285) and the sandbox prerequisites (bubblewrap 0.9.0, socat 1.8.0.0, DEC-141).
- §6 Operating model: orchestrator write scope; worker sessions and the sandbox; network profiles; the oracle; the
  Wave 2 experiment. The install lines are unchanged.
- Consequences: glue figure ≈ 5,370 LOC; one new "good" and one new "bad" line.
- More Information: decision range extended.

### `docs/adr/ADR-0001-threat-model.md`

One sentence under "Guardrails, not a boundary": the sandbox is a stronger guardrail, still not a boundary.
Frontmatter and sources list extended. "Tool installs" is unchanged.

### `docs/plan/WAVE_1_WBS.md`

- Frontmatter decisions; intro; rules (installs, orchestrator write scope and the W1-45 bootstrap, worker sessions,
  experiments, order of specification work, probes, learning metrics).
- §1: four new rows; rows of W1-05, W1-30, W1-31, W1-33, W1-35 and W1-42 updated (sources, dependencies).
- §2: layers 5, 6 and 7 gain the new tickets; the critical path was recomputed and is unchanged.
- §3: implementation 5,090 → 5,370; ops 60 → 70; total 7,130 → 7,420.
- §4: exit criteria 3 and 4.
- §5: register decisions and an EXP-001 row.
- §6: the sandbox experiment and UX before build.

### `.tickets/`

New, created with `tk`:

| W1 | Ticket | Title | Role | Profile | Depends on | Layer | est. LOC | Status |
|---|---|---|---|---|---|---|---|---|
| W1-45 | `DAEO-6cc2` | Orchestrator write scope | engineer | FULL | W1-05 | 5 | 40 | in_progress |
| W1-46 | `DAEO-jdqr` | Worker session launcher (`gov launch`) | engineer | FULL | W1-07, W1-48 | 7 | 180 | open |
| W1-47 | `DAEO-o4fg` | Guard hardening: escape hatch, failed commands, oracle path | engineer | FULL | W1-45 | 6 | 60 | open |
| W1-48 | `DAEO-0qs5` | Claude Code version pin | orchestrator | LITE | W1-06 | 6 | 10 | open |

Edited:

| Ticket | Status | Change |
|---|---|---|
| W1-04 `DAEO-78bn` | closed | A note only |
| W1-05 `DAEO-m7u4` | closed | Its five role-definition KPI lines now end with `[CAP-22.a]`; `CAP-22` and `DEC-119` added to sources. No status change |
| W1-30 `DAEO-2lwj` | open | One KPI (`CAP-38.f`) |
| W1-31 `DAEO-6mk8` | open | One KPI (`CAP-40.c`) |
| W1-33 `DAEO-xog0` | open | One KPI (`CAP-22.a`); `.claude/agents/**` added to `allowed_paths` |
| W1-35 `DAEO-0i6h` | open | Four KPIs (`CAP-32.c`, `CAP-30.f`, `CAP-33.e`, `CAP-38.e`); `CAP-32` added to sources |
| W1-42 `DAEO-gjjf` | open | Depends also on W1-46 and W1-47; two KPIs (launcher use; `CAP-40.c`) |

### `governance/project/bootstrap.md`

New section "After the sandbox experiment (S2, 2026-10-03)": the residuals closed for Bash in launched worker sessions;
those still open for the orchestrator's own session, with the oracle residual of DEC-162; those open for every
session; the `$TMPDIR` rule; the two W1-05 confirmations; the orchestrator's write scope and checkpoint location. No
existing text was changed.

### `docs/plan/tools/validate_s1.py`

- Counts: 62 capabilities, 48 tickets.
- The S1 write-scope check runs on branch `s1/spec` only (DEC-155). On `s2/spec` an S2 write-scope check runs instead.
- New section 3e: 26 checks covering the items above.
- The S1-A fingerprint check accepts `PROMPT.retired.md` for `PROMPT.md` when the hash matches (see §4, point 5).

### `docs/changes/S2-CIT-P.md`

Updated to the owner's answers and set to ACCEPTED: §1 row C, §2 cost, §3.1–§3.5, findings 3 and 4, and §5 as an
answered table.

## 3. What did not change

- **Charter v5:** no change in the first application. P-1 was answered (d), so the install bullet of §6 stands. The
  repair changes the roster table and one non-goal row (§6).
- **Install wording:** Contract §2 (first sentence), `CAP-25.b`, the CAP-25 lite form, ADR-0001 "Tool installs",
  ADR-0002's orchestrator role line, W1-04 and W1-06 are as they were (DEC-157).
- **DEC-083, DEC-108, DEC-112:** not amended.
- **`readiness-dimensions.yaml`, `SOURCE_MAP.csv`, `docs/spec/gov-os/READINESS.md`:** not changed.
- **Code, hooks, `.claude/`, `tests/`:** not touched. The oracle `Read` deny rule and the guard rule are delivered by
  W1-47, not by this change.
- **KPIs of closed tickets:** unchanged in substance. W1-05's lines gained an item id only.
- **Acceptance tests of closed tickets** (corrected after S2-A round 1, F-01): this change edits no test file, but it
  does affect existing tests. The tests of W1-02 and W1-03 that assert the old orchestrator rule are revised by the
  Independent Test Designer under W1-45, as rewrites after implementation (reason: owner correction, DEC-156). The
  first version of this record and of the proposal wrongly said no closed ticket's tests were affected.
- **The other 34 open tickets** of the 39 that were open: unchanged.

## 4. Differences from the proposal, and points for the auditor

1. **Sizes differ from the first proposal.** The proposal first gave +240 LOC. The answers changed three tickets:
   W1-45 60 → 40 (the commit rule was dropped, DEC-156), W1-46 150 → 180 (network profiles, temp directory, three
   required tests, DEC-158, DEC-159, DEC-161), W1-47 30 → 60 (the two oracle layers, DEC-162). The total is +280.
2. **W1-47 may edit `.claude/settings.json`.** DEC-162 puts the oracle's `Read` deny rule in the committed settings
   and assigns it to the guard-hardening ticket, so the path is in its `allowed_paths`.
3. **The acceptance tests of W1-46 and W1-47 use a stand-in directory.** A test that named the real oracle would be
   refused by the rule it tests, and would break the held-out rule. Both tickets say so; W1-47 makes the oracle path
   a guard configuration value.
4. **`gov launch` is not counted among the twelve governance operations** of `CAP-28.b`. It is a start command; the
   count in W1-07 and W1-42 is unchanged. The auditor may prefer it counted; that would change CAP-28, W1-07 and
   W1-42.
5. **A check that failed before this change was repaired.** The S1-A fingerprint check failed on the base branch
   because the owner retired the `s1a` session (DEC-101) and its `PROMPT.md` became `PROMPT.retired.md`. The content
   hash is unchanged, so the check now accepts the renamed file.
6. **CAP-61 and CAP-62 have no scenario ids.** `COVERAGE_MATRIX.md` has no sandbox or launcher scenario, and this
   change does not edit the synthetic pack. Their evidence is the acceptance tests of W1-46 and W1-47.
7. **W1-33 gained `.claude/agents/**` in its `allowed_paths`.** DEC-119 says W1-33 replaces W1-05's definitions,
   which live there; the proposal did not list this path.
8. **The sandbox prerequisites** (bubblewrap, socat) are listed in ADR-0002 §2 as going into the tool registry when
   W1-06 creates it, as `bootstrap.md` already says. No ticket KPI was added for that.
9. **`CAP-58.b` is unchanged.** It denies network classes "unless the role definition grants them"; the research
   network profile of DEC-158 is delivered by the launcher (`CAP-61.c`), not by a role definition. If the auditor
   reads this as a gap, W1-33 would need a KPI.
10. **Nothing in the S2 scratch folder or the oracle was read** beyond `PROMPT.md` and `CHECKPOINT.md`;
    `qualification-oracle/` and `s0b2/probe/` were not opened.

## 5. Validation

`python3 docs/plan/tools/validate_s1.py`, run from the repository root on `s2/spec`: all checks pass. Two are skipped:
the Framework §37 comparison (its input in `docs/source/` is archived) and the S1 write-scope check (branch `s1/spec`
only, DEC-155).

## 6. Repair after the S2-A round-1 audit (2026-10-03)

S2-A's round-1 verdict was ACCEPT_WITH_FINDINGS: no BLOCKER, 4 MAJOR, 6 MINOR. The owner directed the repair, answered
the audit's packages DP-1 and DP-2, and added decisions. The repair was made in two passes on the same day; this
section records the result of both. Nothing under `~/gov-os-workbench/s2a/` was written. The audit files were read
from the copy the owner placed in `~/gov-os-workbench/s2/round1-audit/`.

### 6.1 Findings repaired

| Finding | Severity | Repair | Files |
|---|---|---|---|
| S2A-F-01 | MAJOR | W1-45: the W1-02 and W1-03 tests still pass for every role other than the orchestrator; their orchestrator cases are revised by the Independent Test Designer in W1-45's test design batch, as rewrites after implementation (reason: owner correction, DEC-156). Notes on W1-02 and W1-03 name DEC-156. `CAP-58.a` says "except the orchestrator (`CAP-58.e`)". An orchestrator change outside its ticket's paths is a record, not a containment finding; a change under `tests/acceptance/**` stays a finding. Both CIT records are corrected | `DAEO-6cc2`, `DAEO-emkd`, `DAEO-8qvp`; `CAP-58.a`, `CAP-58.e`; `S2-CIT-P.md` §2, §3.7; this record §3; WBS rules; `bootstrap.md` |
| S2A-F-02 | MAJOR | Answered by DEC-163 (DP-1): a sixth, minimal role. A research or experiment session runs as `GOV_ROLE=research`. The install rule lets that role's install commands through, and the write fence decides where they land. A launched worker's network grant comes from the launcher's profile, which the role definition names: stated in `CAP-58.b` and as the W1-33 KPI that §4 point 9 anticipated | Contract §2 "Tool installs"; `CAP-22.d`, `CAP-25.e`, CAP-25 acceptance, `CAP-58.b`; `DAEO-jdqr`, `DAEO-xog0`, a note on `DAEO-78bn`; Charter §6; ADR-0002 §1, §6 |
| S2A-F-03 | MINOR | The mechanism is named: the sandbox leaves the working directory writable, so the launcher generates at launch an `Edit` deny rule for every other path of the repository (EXP-001 §3.4, §5.3). W1-46 has an acceptance test that a research session's Bash write to a sibling directory fails. The work is inside W1-46's new estimate of 220 | `CAP-61.c`, `CAP-25.e`; `DAEO-jdqr`; WBS rules; ADR-0002 §6 |
| S2A-F-04 | MAJOR | The oracle path is held in one file, `governance/project/held-out.yaml`, added to W1-47's `allowed_paths`. The committed rule is tested statically: the test reads the configured value and asserts that the rule in `.claude/settings.json` is present and built from it, so no test carries a literal path. The guard is tested against a stand-in. W1-47's failure KPIs: any allowed tool call naming the oracle path, whatever the tool; a missing or wrong committed rule; a test that reads or names the oracle. The launcher takes the path from the same file, and W1-46 depends on W1-47. The validator checks both stand-in sentences | `DAEO-o4fg`, `DAEO-jdqr`; `CAP-49.c`; ADR-0002 §6; `bootstrap.md`; `validate_s1.py` |
| S2A-F-05 | MAJOR | Answered by DEC-164 (DP-2), option (b) with one addition: both cases are open residuals in EXP-002, and the launcher sets no `excludedCommands` | `CAP-61.a`, `CAP-61.f`; `DAEO-jdqr`; ADR-0002 §6; WBS §6; `bootstrap.md` "Open for every session" |
| S2A-F-06 | MINOR | `bootstrap.md` restates the closure with EXP-001's qualifier: installs that write outside the repository are closed; for engineer, test designer and auditor the empty allowlist also blocks downloads; a research session can install inside the repository from an allowlisted index, confined to its experiment folder by DEC-163 | `bootstrap.md` |
| S2A-F-07 | MINOR | The two measured figures (about +65 ms per command; about +3,250 input tokens per session, +7 %) are in ADR-0002 "Consequences" and `bootstrap.md`. W1-31 reports the sandbox tokens as a separate line, outside the governance share; whether they count toward it is decided at the Wave 1 exit (DEC-170) | ADR-0002; `bootstrap.md`; `DAEO-6mk8` |
| S2A-F-08 | MINOR | The rename fallback applies to `PROMPT.md` only. The S2 write-scope check excludes `docs/SOURCES.md`. Recorded as DEC-169, extending DEC-155 | `validate_s1.py`; register |
| S2A-F-09 | MINOR | W1-30 200 → 220 and W1-31 120 → 150. WBS §3 states that the KPIs added to W1-33 and W1-35 fit their estimates, and why | `DAEO-2lwj`, `DAEO-6mk8`; WBS §1, §3; ADR-0002 |
| S2A-F-10 | MINOR | W1-48 has a KPI recording bubblewrap 0.9.0 and socat 1.8.0.0 in the tool registry as owner installs (DEC-141), and a failure KPI | `DAEO-0qs5`; WBS §1, §5 |

The audit's observations O-1…O-6 needed no change. On O-6: W1-47's guard KPI now covers a call of any tool that names
the oracle path; DEC-162's list (Read, Grep, Glob, Bash) is kept in the text as the named cases.

### 6.2 Decisions recorded and carried

Register v0.27 (section 27), v0.28 (section 28) and v0.29 (section 29). No entry made before this repair was edited.

| Decision | Subject | Carried into |
|---|---|---|
| DEC-163 (DP-1) | A minimal research role in the Wave 1 roster, delivered with W1-46. Installs only inside its experiment folder; the sandbox's write fence enforces it. Research allowlist of DEC-158. The full lifecycle stays Wave 3 | Charter §6 roster; Contract envelope "Tool installs"; `CAP-22.d`, `CAP-25.e`, CAP-25 acceptance, `CAP-58.b`, `CAP-61.c`, CAP-32 wave note; W1-46, W1-33, W1-04 (note); ADR-0002 §1 L3, §6; WBS; `bootstrap.md` |
| DEC-164 (DP-2) | Subagents inside a sandboxed worker session, and `excludedCommands`, are open residuals in EXP-002 (Wave 2). The launcher sets no `excludedCommands` | `CAP-61.a`, `CAP-61.f`, CAP-61 wave note; W1-46; ADR-0002 §6; WBS rules and §6; `bootstrap.md` |
| DEC-165 | The lite upstream lesson loop, Wave 3; reverses DEC-053 Q7 for framework lessons only | Charter §7 non-goal row; CAP-41 (wave note, provider, `CAP-41.e` reworded, `CAP-41.g`…`CAP-41.j`); `CAP-45.b`; `CAP-58.g`; ADR-0002 §6; WBS §5 and §7 |
| DEC-166 | `gov discover`, Wave 2 | `CAP-32.d`; ADR-0002 §1 L4 and §6; WBS §5 and §6 |
| DEC-167 | A plain-language impact question triggers the impact assessment | `CAP-33.f` (W1, W1-35), `CAP-33.g` (W2), CAP-33 wave note; W1-35; ADR-0002 §6; WBS rules, §5 and §6 |
| DEC-168 | Scope and severity are in W1-08's lesson schema in Wave 1; the loop stays Wave 3 | `CAP-41.f` (W1, W1-08), CAP-41 wave note; W1-08 (one KPI), W1-44 (failure KPI); ADR-0002 §6; WBS §5 and §7 |
| DEC-169 | The validator: fingerprint fallback for `PROMPT.md` only; `docs/SOURCES.md` excluded from the S2 scope check. Confirmed by the owner as the owner's decision | `validate_s1.py` |
| DEC-170 | Sandbox instruction tokens are a separate line in W1-31, outside the governance share; whether they count toward the 15 % is decided at the Wave 1 exit, using measured figures | W1-31 (KPI, source); ADR-0002 "Consequences"; `bootstrap.md`; WBS §1, §3 |
| DEC-171 | An orchestrator change outside its ticket's paths is a record, not a containment finding | `CAP-58.e`, CAP-58 sources; W1-45 (KPI, source, body); ADR-0002 §6; WBS rules, §1 |

The owner also confirmed, without a new decision: the Charter change, limited to the lines DEC-163 and DEC-165
require; DEC-158 as the citation in DEC-163; W1-46's size and its dependency on W1-47.

### 6.3 Figures after the repair

| Item | After the first application | After the repair |
|---|---|---|
| Register | v0.26, DEC-150…DEC-162 (13) | v0.29, DEC-150…DEC-171 (22) |
| Contract | v4.1, 62 capabilities | v4.1, 62 capabilities; the 4.1 change-log line names the repair |
| Contract items changed in the repair | — | Envelope "Tool installs"; CAP-22, 25, 32, 33, 41, 45, 49, 58, 61 |
| `covers` items | 20 added, 1 reworded | 12 more added: 4 in Wave 1 (`CAP-22.d` and `CAP-25.e` on W1-46, `CAP-33.f` on W1-35, `CAP-41.f` on W1-08), 2 in Wave 2, 6 in Wave 3. 8 more reworded: `CAP-41.e`, `CAP-49.c`, `CAP-58.a`, `CAP-58.b`, `CAP-58.e`, `CAP-61.a`, `CAP-61.c`, `CAP-61.f` |
| Wave 1 tickets | 48 | 48. W1-46 180 → 220 and depends also on W1-47; W1-30 200 → 220; W1-31 120 → 150 |
| Wave 1 glue (class implementation) | ≈ 5,370 LOC | ≈ 5,460 LOC (+370 for the whole S2 change) |
| Layers | W1-46 in layer 7 | Unchanged |
| Critical path | Unchanged | Unchanged |
| Charter v5 | Not changed | Four lines: frontmatter decisions; §6 roster rows for Wave 1 and Wave 3; §7 non-goal row on the upstream lesson loop |

Tickets edited in the repair:

| Ticket | Status | Change |
|---|---|---|
| W1-45 `DAEO-6cc2` | in_progress | F-01: KPIs, source DEC-106, body |
| W1-46 `DAEO-jdqr` | open | DEC-163, DEC-164, F-02, F-03, F-04: KPIs, six `allowed_paths`, sources, `est_loc` 180 → 220, dependency on W1-47, body |
| W1-47 `DAEO-o4fg` | open | F-04: KPIs, `governance/project/held-out.yaml` in `allowed_paths`, body |
| W1-48 `DAEO-0qs5` | open | F-10: one success and one failure KPI, source DEC-141 |
| W1-08 `DAEO-uudf` | open | DEC-168: one KPI, one source |
| W1-44 `DAEO-wqd6` | open | DEC-168: failure KPI names severity, one source |
| W1-30 `DAEO-2lwj` | open | F-09: `est_loc` 200 → 220 |
| W1-31 `DAEO-6mk8` | open | F-07, F-09: one KPI, source DEC-138, `est_loc` 120 → 150 |
| W1-33 `DAEO-xog0` | open | F-02, DEC-163: the `CAP-58.b` KPI names the launcher's network profile; one KPI on leaving W1-46's research role in place; two sources |
| W1-35 `DAEO-0i6h` | open | DEC-167: one KPI, one source |
| W1-02 `DAEO-emkd`, W1-03 `DAEO-8qvp`, W1-04 `DAEO-78bn` | closed | A note each. No KPI or status change |

`validate_s1.py`: the F-08 changes; section 3f, fourteen checks for the repair; the S2 write-scope check allows the
Charter's four changed lines and nothing else there.

### 6.4 Points for the auditor

1. **The DP-1 answer differs from the audit's options.** The audit recommended running research as `product-spec`.
   The owner chose a new, minimal sixth role, with the sandbox's write fence as the enforcement. The guard change
   (the role is known; its install commands are let through) is placed in W1-46, not in a repair ticket for W1-04.
   W1-46 carries the KPI that W1-04's acceptance tests still pass.
2. **The DP-2 answer is option (b), not the recommended (a).** No subagent test was added to W1-46. Until EXP-002,
   the wall claim of Contract §2 and `CAP-58.d` is not shown for a subagent of a launched worker; `bootstrap.md` says
   so under "Open for every session".
3. **Sandbox tokens and governance share (F-07).** Now an owner decision, DEC-170: the tokens are reported as a
   separate line in W1-31, not inside the governance share. Whether they count toward the 15 % is decided at the
   Wave 1 exit, using measured figures. W1-31 and ADR-0002 say this and no more.
4. **"Record, not a finding" (F-01).** Now an owner decision, DEC-171: a change the orchestrator makes outside its
   ticket's paths is a record, not a containment finding. `CAP-58.e` and W1-45 cite it.
5. **`governance/project/held-out.yaml` is a new file name chosen here** (F-04). It holds the real path, as the
   committed deny rule must. No test may name the path; the two files that carry it are named in W1-47's failure KPI.
6. **`CAP-25.b` still says "denied for other roles".** It is delivered by the closed W1-04 and was left as written.
   `CAP-25.e`, the CAP-25 acceptance check and the envelope state the research exception.
7. **The research write fence depends on generated deny rules** (F-03). EXP-001 tested deny rules on two directories,
   not a generated list over a whole repository. W1-46's sibling-directory test is what shows it.
8. **The lessons inbox widens DEC-156.** `CAP-58.g` records the one path outside the repository the orchestrator may
   write. It is Wave 3 and has no ticket yet. ADR-0001 was not changed.
9. **The Contract version stays 4.1.** The repair belongs to the same, not yet accepted, change.
10. **CAP-41 stays KEPT.** The lite loop is carried as Wave 3 `covers` items; `CAP-41.e` keeps the full export gate
    and FCP loop a non-goal.
11. **F-09 is repaired in part by statement.** W1-33 and W1-35 were not re-estimated; WBS §3 says why.

### 6.5 Validation

`python3 docs/plan/tools/validate_s1.py`, run from the repository root on `s2/spec` after the repair: 89 PASS, 2 SKIP,
0 FAIL. The two skipped are the same as in §5.
