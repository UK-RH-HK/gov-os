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
decisions_recorded: [DEC-150, DEC-151, DEC-152, DEC-153, DEC-154, DEC-155, DEC-156, DEC-157, DEC-158, DEC-159, DEC-160, DEC-161, DEC-162]
decisions_carried: [DEC-102, DEC-103, DEC-104, DEC-105, DEC-106, DEC-119, DEC-136, DEC-137, DEC-138, DEC-147]
---

# S2 — Change-execution record (CIT-E) on the Gov OS specification

This records what the S2 specification change did, file by file, against the proposal `docs/changes/S2-CIT-P.md`.
The owner chose "apply now" (DEC-105) and answered the open questions on 2026-10-03 (DEC-156…DEC-162). The change
touched specification files only: no code, hook, settings file or test.

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
| Charter v5 | — | Not changed |

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

- **Charter v5:** no change. P-1 was answered (d), so the install bullet of §6 stands.
- **Install wording:** Contract §2 (first sentence), `CAP-25.b`, the CAP-25 lite form, ADR-0001 "Tool installs",
  ADR-0002's orchestrator role line, W1-04 and W1-06 are as they were (DEC-157).
- **DEC-083, DEC-108, DEC-112:** not amended.
- **`readiness-dimensions.yaml`, `SOURCE_MAP.csv`, `docs/spec/gov-os/READINESS.md`:** not changed.
- **Code, hooks, `.claude/`, `tests/`:** not touched. The oracle `Read` deny rule and the guard rule are delivered by
  W1-47, not by this change.
- **KPIs of closed tickets:** unchanged in substance. W1-05's lines gained an item id only.
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
