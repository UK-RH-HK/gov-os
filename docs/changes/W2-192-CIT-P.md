---
id: W2-192-CIT-P
type: change-impact-proposal
status: PROPOSED
date: 2026-11-16
branch: w2/W2-192
base: 847619089c15
ticket: DAEO-mpq2 (W2-192)
author: orchestrator (the ticket lead of W2-192)
review: 'none yet: the ticket''s FULL independent review follows the owner''s approval of these bytes (the order of the build run)'
decisions_carried: [DEC-1200, DEC-974, DEC-105, DEC-614]
owner_approval: 'pending: "W2-192 CIT-P (A) approved" (the adopt skill) and/or "W2-192 CIT-P (B) approved" (CAP-44.m), section 6'
state_class: EVIDENCE
---

# W2-192: change-impact proposal (CIT-P) for stage AS in the adopt skill and in CAP-44

W2-192 builds adoption stage AS, the spec audit, in `gov adopt --lite` (DEC-1200 (4), P-ADOPT-SPEC-AUDIT-1 (a)). Two
texts must name the new stage, and neither is in the ticket's paths: the kernel's adopt skill (a kernel path) and the
Contract's CAP-44 (a specification). Each changes only on the owner's approval of its bytes (CAP-33, the ticket's
non-goals). This proposal gives both parts with their bytes. Part A is one kernel skill edit. Part B is a
specification change, CAP-44.m, as Contract version 4.4. The owner may approve either part alone.

## 1. What triggers the change

| # | Trigger | Source | State before |
|---|---|---|---|
| T1 | The spec audit becomes a standard adoption stage, AS, after A2 and before A3: its record, lite checks, the skill's text and CAP-44's line by CIT-P | DEC-1200 (4); `packages/P-ADOPT-SPEC-AUDIT-1.md` §2 | The adopt skill lists A0-A10 and MA; CAP-44 has no spec-to-code stage (A11's full audit is CAP-44.k, Wave 3) |
| T2 | The product now offers the stage: `gov adopt --lite --stage AS`; A3 refuses (`ADOPT_STAGE_MISSING`) until it is recorded; the lite checks are `ADOPT_SPEC_AUDIT_INCOMPLETE` and `ADOPT_GAP_WITHOUT_QUESTION` | W2-192 commits `6fc08f430a69` and `5ba664e6364b` (`src/gov/adopt/spec_audit.py`): AS is a side record of the chain (its own chain A0-A2, standing on A2's record); A3 requires it and records its sha256 (`spec_audit`); the stages after A3 and the gates never read it, so an adoption recorded before AS goes on | Built on the ticket branch; `gov accept W2-192` 30/30 green |
| T3 | A contradiction against a closed specification comes with three costed options | DEC-105 | — |

## 2. Part A: the adopt skill (kernel)

### 2.1 What changes

| File | Change |
|---|---|
| `template/governance/kernel/skills/adopt/SKILL.md` | A new section, "Stage AS: the spec audit (DEC-1200 (4))", after "Wave 1 scope" and before "Embedding policy"; version 1.1.0 → 1.2.0; DEC-1200 added to the governing sources. Nothing else changes |
| `.rulesync/skills/adopt/SKILL.md`, `template/.rulesync/skills/adopt/SKILL.md` | Byte-equal to the kernel source, as today |
| `.claude/skills/adopt/SKILL.md` | **Not in this change.** The CTO's copies ACT generates it from the kernel source (DEC-315, DEC-1112 (3)); until then the adapter check reports it as differing |

### 2.2 The bytes (unified diff against the base; the three files are byte-equal before and after)

```diff
@@ -1,7 +1,7 @@
 ---
 name: adopt
 description: Method for progressive adoption of the Gov OS into a repository through the A0-A11 transaction
-version: "1.1.0"
+version: "1.2.0"
 ---
 
 # Adopt
@@ -27,6 +27,16 @@
 
 Each stage writes an evidence record. `gov doctor` reports the current adoption level (CAP-54).
 
+## Stage AS: the spec audit (DEC-1200 (4))
+
+After A2 and before A3, `gov adopt --lite --stage AS` audits the repository's specs against its code, so that the path map and A5's review see which specs are alive. It reads A1's inventory and A2's classes and commits `governance/adoption/AS-spec-audit.md`, which stands on A2's record. A3 refuses to run before that record is committed, or when it no longer stands on A2's record as that record now is, and A3's record names the AS record it read. AS is a side record of the chain: the stages after A3 do not read it, so an adoption recorded before AS existed goes on, and AS can be run there at any time after A2.
+
+- **The record** lists every spec found (path, title, its stated wave or status); each spec built, partly built or not built, with its evidence (code paths, tests, commits); the tickets found, done or not, by wave; the specs with no code; the code with no spec (the top-level code modules no spec names); and each gap as one question to the owner, with a place for the answer.
+- **Built or not** is judged from code paths, tests and commits only, never by a model.
+- **The lite checks:** the record names every spec and every top-level code module the inventory holds, and every gap carries a question. A3 refuses a record that fails either, and records nothing.
+- **AS changes nothing else:** it writes only under `governance/adoption/`, changes no spec and no code, and closes no gap. A gap's answer is the owner's (how and when the spec is established, or the code retired), recorded beside its question when it comes.
+- **No auditor session in the lite form:** the path map's reviewer at A5 reads the AS record with the path map.
+
 ## Embedding policy (DEC-694, DEC-700)
 
 Every namespace of the target path map states its `embedding_policy`, as one of two values, written exactly so:
@@ -73,4 +83,4 @@
 
 ## Governing sources
 
-DEC-006, DEC-090, DEC-388, DEC-694, DEC-700, DEC-1050, DEC-1071, DEC-1072, DEC-1074, DEC-1083, DEC-1098, DEC-1101, DEC-1125, DEC-1130, DEC-1179, CAP-44, CAP-54.
+DEC-006, DEC-090, DEC-388, DEC-694, DEC-700, DEC-1050, DEC-1071, DEC-1072, DEC-1074, DEC-1083, DEC-1098, DEC-1101, DEC-1125, DEC-1130, DEC-1179, DEC-1200, CAP-44, CAP-54.
```

### 2.3 sha256, before and after

| File | Before (base `847619089c15`) | After | Lines |
|---|---|---|---|
| `template/governance/kernel/skills/adopt/SKILL.md` | `6a884cf1639f2e803400205ace80aeabe23badbd59be8df92c06e24cf9a29489` | `d331bbd25f2f9dedf0e19328ae1b2fe9033b248597b42c9a4cc201d7d41f592b` | 76 → 86 |
| `.rulesync/skills/adopt/SKILL.md` | `6a884cf1639f2e803400205ace80aeabe23badbd59be8df92c06e24cf9a29489` | `d331bbd25f2f9dedf0e19328ae1b2fe9033b248597b42c9a4cc201d7d41f592b` | 76 → 86 |
| `template/.rulesync/skills/adopt/SKILL.md` | `6a884cf1639f2e803400205ace80aeabe23badbd59be8df92c06e24cf9a29489` | `d331bbd25f2f9dedf0e19328ae1b2fe9033b248597b42c9a4cc201d7d41f592b` | 76 → 86 |

## 3. Part B: CAP-44 (Contract v4, version 4.3 → 4.4)

### 3.1 What changes

`docs/contract/contract.yaml` is the authority; `CONTRACT_v4.md` holds the same content, and the capability records
under `docs/contract/capabilities/` are generated from the yaml (DEC-614).

| File | Change |
|---|---|
| `docs/contract/contract.yaml` | CAP-44 gains one covers item, `CAP-44.m` [W2], after `CAP-44.l`; CAP-44's `wave_note`, `provider` and `sources` name it; `version` 4.4, `revised` 2026-MM-DD, one `change_log` entry. CAP-44 stays W3; 62 capabilities; covers items 214 → 215 (W2 19 → 20) |
| `docs/contract/CONTRACT_v4.md` | The same: the CAP-44.m line under CAP-44's **Covers**, the Wave and Provider lines, DEC-1200 in Sources, the version row 4.4 and the version line |
| `docs/contract/capabilities/CAP-44.m.md` (new), `CAP-44.md` | Generated from the yaml (DEC-614) |

### 3.2 The bytes

`contract.yaml`, the new covers item (after `CAP-44.l`, at its indent):

```yaml
  - id: CAP-44.m
    item: 'AS spec audit, lite: after A2 and before A3, `gov adopt --lite --stage AS` records every spec found (path, title,
      its stated wave or status), each built, partly built or not built with evidence (code paths, tests, commits), the
      tickets found done or not by wave, the specs with no code, the code with no spec (top-level code modules no spec
      names), and each gap as one question to the owner with a place for the answer; the lite checks (every spec and every
      top-level code module the inventory holds named, every gap with a question) refuse a record that fails either; A3
      refuses to run before AS is recorded; built or not is judged from code paths, tests and commits, never by a model;
      the path map''s reviewer at A5 reads the record'
    source: DEC-1200; P-ADOPT-SPEC-AUDIT-1
    wave: W2
    provider:
    - W2-192
```

`contract.yaml`, CAP-44's other fields (the added words in **bold** here only; plain in the file):

- `wave_note`: "… the lite A7 and A10 gates and the lite verdict are W2 (CAP-44.f, CAP-44.h; DEC-722)**; stage AS, the
  lite spec audit, is W2 (CAP-44.m; DEC-1200)**; A9, A11, …"
- `provider`: one entry added, `'W2: stage AS, the lite spec audit (W2-192, DEC-1200)'`
- `sources`: `DEC-1200` added after `DEC-722`

`contract.yaml`, the change log entry:

```yaml
- version: '4.4'
  date: '2026-MM-DD'
  change: 'W2-192 specification change (docs/changes/W2-192-CIT-P.md), approved by the owner (DEC-n). Carries DEC-1200
    (4): the spec audit is a standard adoption stage, AS, after A2 and before A3, lite (CAP-44.m, W2). CAP-44 stays W3.
    62 capabilities; 215 covers items (W2 19 → 20).'
```

`CONTRACT_v4.md`, under CAP-44's **Covers**, after `CAP-44.l`:

```markdown
  - `CAP-44.m` [W2] AS spec audit, lite: after A2 and before A3, `gov adopt --lite --stage AS` records every spec found (path, title, its stated wave or status), each built, partly built or not built with evidence (code paths, tests, commits), the tickets found done or not by wave, the specs with no code, the code with no spec (top-level code modules no spec names), and each gap as one question to the owner with a place for the answer; the lite checks (every spec and every top-level code module the inventory holds named, every gap with a question) refuse a record that fails either; A3 refuses to run before AS is recorded; built or not is judged from code paths, tests and commits, never by a model; the path map's reviewer at A5 reads the record — DEC-1200; P-ADOPT-SPEC-AUDIT-1 · delivered by W2-192
```

and the version row:

```markdown
| 4.4 | 2026-MM-DD | W2-192 specification change (docs/changes/W2-192-CIT-P.md), approved by the owner (DEC-n). Carries DEC-1200 (4): the spec audit is a standard adoption stage, AS, after A2 and before A3, lite (CAP-44.m, W2). CAP-44 stays W3. 62 capabilities; 215 covers items (W2 19 → 20). |
```

The date and the DEC id are filled in when the owner approves; the after hashes of the two contract files are taken
then, by the product-spec session that applies the change (with the generator for the capability records).

### 3.3 sha256 before (base `847619089c15`)

| File | Before |
|---|---|
| `docs/contract/contract.yaml` | `a5ef206c5e7ce0377277fca47ad420a1e44bc64cfc28814918dd7f2aebe149dd` |
| `docs/contract/CONTRACT_v4.md` | `5c0a503169dde5130bdb690642fb809b49aa92f25862b9b71a4dadfe77a141ec` |
| `docs/contract/capabilities/CAP-44.md` | `e8353fca43e1670c01aef5af65a314f56c589b99c0ef6dd2a9f2f75b5b1113e0` |

## 4. The three options (DEC-105), for each part

| Option | Part A (the skill) | Part B (CAP-44.m) |
|---|---|---|
| **Apply now** (recommended) | One edit to three byte-equal files and the copies ACT; about 15 minutes with the ACT | A product-spec session applies the yaml, the md and the generated records, and runs the Contract's suites (W1-48, W2-49, W2-51 read the Contract; any count of covers items there moves 214 → 215); about 1 to 2 hours |
| Defer | The product offers AS but the method does not name it: an adopter's CTO meets an A3 refusal the skill never mentions | The stage is built with no capability line: no readiness row and no verdict condition can name it |
| Re-baseline | Fold AS into A2's text instead of its own section | Put AS under CAP-44.b (W1, delivered) instead of a new W2 item: it changes a delivered W1 line |

**Recommendation:** apply both now. Confidence: high for part A, medium-high for part B (its count and the suites
that read the Contract are checked when it is applied).

## 5. Impact

| Area | Impact |
|---|---|
| Kernel skills | One skill text grows by one section (10 lines); no hook, role file or guard changes |
| Generated copies | `.rulesync` copies byte-equal; `.claude/skills/adopt/SKILL.md` by the copies ACT |
| Contract | One W2 covers item; no capability changes wave; CAP-44 stays W3 |
| Product | None: the code is W2-192's, built and tested on its own branch; neither part changes code |
| Other tickets | None of the skill's or the Contract's readers is in W2-192's paths; the suites named in §4 run when part B is applied |

## 6. The owner's line

`W2-192 CIT-P (A) approved` (the adopt skill, the bytes of §2.2) and/or `W2-192 CIT-P (B) approved` (CAP-44.m, the bytes of
§3.2), or `defer` / `re-baseline` for either.
