---
id: W2-49-CIT-E
type: change-execution-record
status: APPLIED
date: 2026-10-17
branch: w2/W2-49
base: a02e3485 (Contract 4.1; the apply round's diff base 1b43c73c holds the same two Contract files and the same 273 records)
proposal: W2-49-CIT-P
approved_revision: 0faa0664 (the CIT-P as answered after its review; its body is unchanged from there to this record)
author: product-spec (W2-49, single author)
review: the CIT-P was reviewed at 9dd15777 by a fresh, read-only independent auditor (CAP-33.d, CAP-47.b), recommendation ACCEPT_WITH_FINDINGS, answered once at 0faa0664 (CIT-P §12)
decisions_carried: [DEC-722]
decisions_staged: ['DEC-741 (owner, 2026-10-17; the approval of the CIT-P with the answers A to K; staged for the owner''s commit, not yet in this worktree''s register)', 'DEC-744 (the Wave 2 plan validator, W2-51; not yet in this worktree''s register)']
state_class: EVIDENCE
---

# W2-49 — Change-execution record (CIT-E) for Contract v4.2, lite

This records what the W2-49 specification change did, commit by commit, against its proposal
`docs/changes/W2-49-CIT-P.md` (W2-49-CIT-P). The change carries DEC-722 into the Contract: the adoption verdict
(CAP-44.h), the A7 and A10 gates of CAP-44.f and the manifest and file hashes of CAP-43.b come into Wave 2, lite;
CAP-02.c (signed release tags), A9, A11, the qualification certificate (CAP-43.c) and the rest of CAP-43.b stay in
Wave 3.

It followed CAP-33's route (CAP-33.d: evidence → corroboration → proposal → independent review → owner approval →
versioned promotion), and CAP-33's acceptance asks that "the CIT-E record matches the proposal or lists the
differences". It does both: §3 confirms each change the CIT-P proposed, section by section, and §6 lists each
difference from the CIT-P with its reason.

## 1. Summary

| Item | Before (base, Contract 4.1) | After (Contract 4.2) |
|---|---|---|
| Contract version | 4.1, revised 2026-10-03 | 4.2, revised 2026-10-17; change-log entry and change row 4.2; 4.0 and 4.1 unchanged |
| Contract status | `contract.yaml` PROPOSED, `CONTRACT_v4.md` ACCEPTED (CIT-P §10 F-4) | ACCEPTED in both (row W2-L343; DEC-741) |
| Capabilities | 62; none changes wave | 62; none changes wave; §1 Counts unchanged |
| Covers items | 211: W1 149 / W2 17 / W3 38 / NONE 7 | 214: W1 149 / W2 20 / W3 38 / NONE 7 (CIT-P §6.3) |
| Covers items moved W3 → W2 | — | CAP-43.b, CAP-44.f, CAP-44.h (each lite, each citing DEC-722) |
| Covers items added (W3) | — | CAP-43.d, CAP-44.k, CAP-44.l |
| Covers items reworded, wave kept | — | CAP-45.a (W2; Question D (ii)) |
| Capability wave notes reworded | — | CAP-43, CAP-44 (and its `provider`), CAP-47 |
| Capability records (`docs/contract/capabilities/`) | 273, each "(Contract v4, version 4.1)" | 276: the 273 cite version 4.2 (K (1)); eight rewritten or new by the K (2) reading |
| `docs/contract/SOURCE_MAP.csv` | — | not touched (§8) |

The change touched specification files only: the two Contract files, the capability records, the CIT-P and this
record. No code, no test, no ticket file (the plan commits of §4 are the orchestrator's, on `w2/integrate`).

## 2. The owner's approval before the change (CAP-33)

| Step of CAP-33.d | Where |
|---|---|
| Evidence | DEC-722 (owner, 2026-10-16), its basis and items 1 to 4; CIT-P §1 (triggers T1 to T5) |
| Proposal | W2-49-CIT-P, commit `9dd15777` |
| Independent review | a fresh, read-only independent auditor at `9dd15777`, ACCEPT_WITH_FINDINGS; answered once at `0faa0664` (CIT-P §12) |
| **Owner approval** | **DEC-741, the owner's, 2026-10-17: the CIT-P approved, apply now, with the CIT-P's recommended answer to each question (§4).** Staged for the owner's commit with `Role: owner` (DEC-724) and not yet in this worktree's register. Its first git trace is the orchestrator's ticket commit `1d5449eb` ("CIT-P approved A to J", `Implements: DEC-741`), merged into this branch at `1b43c73c`, before the first Contract commit |
| Versioned promotion | `90c4d20a`, `5a6a12f5`, `7f935156` (§3); Contract 4.1 stays in git and in the change log as a kept version (CAP-33.e; DEC-105: "every version is kept") |
| The CIT-E | this record, with this commit |

No Contract file was edited before the approval: the first commit that changes `docs/contract/` on this branch is
`90c4d20a`, after `1d5449eb`.

## 3. What changed, commit by commit

### 3.1 `90c4d20a` — Contract v4.2, lite, as the approved CIT-P (DEC-741)

Files: `docs/contract/contract.yaml`, `docs/contract/CONTRACT_v4.md`. `Implements: DEC-722, CAP-43.b, CAP-44.f,
CAP-44.h, CAP-45.a`.

| CIT-P section | Proposed | Applied | Match |
|---|---|---|---|
| §6.1 header | `version: '4.2'`, `revised:` the apply date | `version: '4.2'`, `revised: '2026-10-17'`; also `status: ACCEPTED` | matches; status: row W2-L343 (§4, difference (e)) |
| §6.1 change log | a 4.2 entry after 4.1; 4.0 and 4.1 unchanged | entry 4.2, date 2026-10-17; 4.0 and 4.1 unchanged | matches, with text added: difference (e) |
| §6.1 CAP-43 | `wave: W1` kept; wave note naming CAP-43.b lite and CAP-43.d, no ticket; DEC-722 in `sources` | as proposed | matches |
| §6.1 CAP-43.b | "Release contents, lite: the release's own manifest and file hashes …"; DEC-722 in its source; `wave: W2`; no provider | as proposed | matches |
| §6.1 CAP-43.c | unchanged, W3 | unchanged, W3 | matches |
| §6.1 CAP-43.d | new, W3: the nine other release contents | as proposed, placed after CAP-43.c | matches; placement: difference (d) |
| §6.1 CAP-44 | `wave: W3` kept; wave note and `provider` reworded; DEC-722 in `sources` | as proposed | matches |
| §6.1 CAP-44.f | A7 and A10, lite, each by a fresh Independent Auditor session and its own stage; what each checks; `wave: W2`; no provider | as proposed | matches |
| §6.1 CAP-44.h | the lite verdict with the lite conditions, the F (i) rules and the G (i) conditions; `wave: W2`; no provider | as proposed, with the ten conditions of Adoption Protocol v3.0 §20 added, each marked (§5) | differs: (a), (b), (g) |
| §6.1 CAP-44.k | new, W3: A9, A11, A7 and A10 beyond their lite form | as proposed, after CAP-44.j | matches; placement: difference (d) |
| §6.1 CAP-44.l | new, W3: the verdict with the ten conditions, after A0–A11 | as proposed, after CAP-44.k | matches; placement: difference (d) |
| §6.1 CAP-47 | `wave: W3` kept; wave note: the lite A7 and A10 gates W2 by the Independent Auditor role | as proposed | matches |
| §6.1 providers | none on the three W2 items | none | matches |
| §7 D (ii) CAP-45.a | the Wave 2 clause; the signed tag with CAP-02.c (W3), DEC-722 | applied (§6 was silent on CAP-45.a's text) | differs in form: (c) |
| §6.2 `CONTRACT_v4.md` | frontmatter `version: "4.2"`, `revised:`, DEC-722 in `decisions`; title line; "Version 4.2" line; a 4.2 change row; the CAP-43, CAP-44, CAP-47 blocks and the covers lines follow the YAML; §1 Counts unchanged | as proposed; the frontmatter `status` was already ACCEPTED | matches |
| §6.3 counts | 211 → 214: W1 149 / W2 20 / W3 38 / NONE 7 | the same (counted from both commits' `contract.yaml`) | matches |
| §4 what stays in Wave 3 | CAP-02.c, A9, A11, CAP-43.c, the rest of CAP-43.b | CAP-02.c and CAP-43.c unchanged at W3; A9 and A11 in CAP-44.k (W3); the rest of CAP-43.b in CAP-43.d (W3) | matches |
| §5.4 DEC-090, CAP-54.a, Charter v5 | no ACCEPTED entry edited; CAP-54.a as written; no Charter change | DEC-090 and CAP-54.a untouched; no Charter change | matches |

### 3.2 `5a6a12f5` — the capability records cite Contract version 4.2 (DEC-741 K (1))

The version line only: in each of the 273 records under `docs/contract/capabilities/`, "(Contract v4, version 4.1)"
becomes "(Contract v4, version 4.2)", by a throwaway script (not committed) that required exactly one occurrence per
record. 273 files, one line each; no title, item, wave, status or covers list changed. CIT-P §8 recommended this
("they are DERIVED"); DEC-741 K (1) is the owner's answer. The records were created from `contract.yaml` by script
(DEC-614); each states `state_class: DERIVED` and names `contract.yaml` as the authority.

### 3.3 `7f935156` — the records of the split and moved items follow Contract v4.2 (the K (2) reading)

Eight records, rewritten from the approved `contract.yaml` in the form of their sibling records, as CIT-P §8 names
them:
- `CAP-43.b.md`, `CAP-44.f.md`, `CAP-44.h.md`: new title, item and wave;
- `CAP-43.d.md`, `CAP-44.k.md`, `CAP-44.l.md`: new;
- `CAP-43.md`, `CAP-44.md`: their "Covers:" lists gain the new ids.

No status line and no other record changed. The commit states that its throwaway generator (not committed) first
reproduced 207 of the other 208 covers records byte for byte; the one that differs is CAP-45.a (§8).

This is **the orchestrator's reading of DEC-741 K (2), staged for the owner's commit to confirm or overturn.** It is a
commit of its own so that a revert drops it alone (§9). The acceptance tests of K (2) are a file of their own,
`tests/acceptance/W2-49/test_w2_49_capability_records.py`, which the suite's README says is dropped alone if the owner
overturns the reading.

### 3.4 This commit — the CIT-E, and the CIT-P records the owner's approval

- `docs/changes/W2-49-CIT-E.md` (new): this record.
- `docs/changes/W2-49-CIT-P.md`: the frontmatter `status:` becomes ACCEPTED, with an `accepted:` line (the owner,
  2026-10-17, DEC-741, staged) and the `pending:` line changed to match; a closing section, "13. The owner's answers
  (DEC-741)", records each answer A to K in one line and names W2-52 (DAEO-siiz) as the new ticket of Question H.
  Nothing else in its body changes: the reviewed text stays as approved.

**Resume round, DEC-745 item 2** (commit "the eight source-map rows follow Contract v4.2"): in `docs/contract/SOURCE_MAP.csv` only the `carried_by_or_disposition` cell of the eight rows CIT-P §8 names changed (rows 235, 237, 248, 251, 256, 280, 283, 292): each states its lite part W2 under v4.2's CAP-44.f (A7, A10) or CAP-44.h (the verdict), and its rest W3 under CAP-44.k or CAP-44.l, citing DEC-741 with DEC-722; rows 252 (A11) and 282 (A9) and every other row unchanged.

## 4. The owner's answers (DEC-741) and how each was applied

| Q | Answer | How it was applied |
|---|---|---|
| A | **(a1)** the split form; new ids CAP-43.d, CAP-44.k, CAP-44.l | `90c4d20a`: CAP-43.b, CAP-44.f, CAP-44.h keep their ids at W2; the three new ids carry the W3 rest; the records in `7f935156` (K (2)) |
| B | **(i)** lite CAP-43.b is the manifest and file hashes only | `90c4d20a`: CAP-43.b names only the manifest and file hashes; CAP-43's wave note names CAP-43.d and no ticket |
| C | **(i)** a named read of Adoption Protocol v3.0 §20 and Distribution Protocol v1.2 §18, with (ii) as fallback | the read was made (§5); `90c4d20a`: CAP-44.h lists the ten, each marked W2 or W3; (ii) was not needed |
| D | **(ii)** CAP-45.a's Wave 2 wording | `90c4d20a`: CAP-45.a, still W2, gains the Wave 2 clause; every mention of the signed tag carries W3 (CAP-02.c); difference (c) |
| E | **(i)** DEC-741 amends DEC-090 in part: A7, A10 and the verdict come into Wave 2, lite; A9, A11 and the rest stay in Wave 3 | the amendment is the owner's entry, DEC-741; no ACCEPTED entry is edited; CAP-44's wave note cites DEC-090 for the W3 part; CAP-44.h says the verdict record names itself lite and the conditions it does not check; CAP-54.a unchanged |
| F | **(i)** only the owner accepts an exception, by name, in a `Role: owner` entry; the auditor accepts nothing | `90c4d20a`: CAP-44.h states the three rules, "only the owner accepts an exception; the auditor accepts none" |
| G | **(i)** the lite healthy conditions add `gov doctor` green, `gov check` with no RED, a first `gov close` at exit 0 | `90c4d20a`: the three are lite conditions in CAP-44.h |
| H | **(i)** a new ticket builds the lite A7 and A10 stage records: **W2-52 (DAEO-siiz)**, FULL, engineer, layer 3; it starts after this apply round and closes before W2-27 | not in this ticket's paths; the orchestrator created W2-52 (`7de0e524`) and made W2-27 depend on it (`ed88d811`), both on `w2/integrate`, merged here at `1b43c73c` |
| I | **(ii)** W2-02 types the verdict with its three values and a list of named conditions (source item, state: met, not met, accepted by an owner entry) and closes on its own | not in this ticket's paths; the orchestrator's `d7c5f5f2` on W2-02's ticket, merged here at `1b43c73c` |
| J | **(i)** at W2-30's close the orchestrator records row W2-I017 as carried to Wave 3 | not yet: it happens at W2-30's close (§8) |
| K | **(1)** the version line in all 273 capability records, the owner's answer; **(2)** the records CIT-P §8 names as rewritten, the orchestrator's reading, staged for the owner to confirm or overturn | (1) `5a6a12f5` (§3.2); (2) `7f935156`, a commit of its own (§3.3) |

**Row W2-L343.** Both Contract files now state status ACCEPTED for v4.2. The CIT-P stated none (§10 F-4 left the
status as it was "unless the owner says otherwise"); ACCEPTED by the owner's approval, DEC-741.

**W2-52 (DAEO-siiz) builds the lite A7 and A10 stage records** of CAP-44.f, lite: the A7 and A10 stage records and
their evidence in `gov adopt` and the adopt skill (CIT-P §7 H (i)), which CIT-P finding F-1 found no ticket built. It
is FULL, engineer, layer 3; it starts after this apply round and closes before W2-27.

## 5. The named read (C (i)) and the ten ADOPTED_HEALTHY conditions

The read was made once each, by `git show bb6ec3a8d8242fda7a76f86f0f0eff46813bc65f:docs/source/<path>`, the files named
exactly from `docs/SOURCES.md` lines 149 and 150, after printing only their heading lines (the lead's statement; this
worker did not read them):

| File | Heading | Lines | Use |
|---|---|---|---|
| `docs/source/originals/GOVERNANCE_OS_ADOPTION_MIGRATION_AND_INDEPENDENT_AUDIT_PROTOCOL_v3.0.md` | "# 20. Final adoption verdict" | 591–613 | the source of the ten ADOPTED_HEALTHY conditions |
| `docs/source/originals/GOVERNANCE_OS_RELEASE_DISTRIBUTION_ADOPTION_AND_UPSTREAM_LEARNING_PROTOCOL_v1.2.md` | "# 18. Adoption acceptance" | 625–644 | 15 adoption acceptance conditions, used only to check the mapping |

The outcome, as CAP-44.h now states it: of the ten, only (3) is marked W2; the other nine are W3, five of them with a
named lite part that the lite conditions check.

| # | Condition (CAP-44.h's wording) | Mark | Lite part the lite conditions check |
|---|---|---|---|
| (1) | certified kernel pinned | W3 (the certification by qualification is CAP-43.c) | the pinned, hash-verified release (CAP-02.a, CAP-43.b) |
| (2) | project overlay separate | W3 | none |
| (3) | path mapping, with the A5 independent review passed | **W2** | the A3 path map, the A5 review and the native layout kept (CAP-44.b, CAP-44.c, CAP-44.j) |
| (4) | migration independently verified | W3 (a separate verifier role, CAP-47.a) | the lite A7 gate (CAP-44.f) |
| (5) | legacy authority retired | W3 (no accidental legacy authority, CAP-48.b) | A8's retirement of legacy memory (CAP-44.e) |
| (6) | memory independently verified | W3 (over the A9 knowledge fabric and by a separate role, CAP-44.k, CAP-47.a) | the lite A10 gate (CAP-44.f) |
| (7) | comprehensive v4 audit completed | W3 (A11, CAP-44.k) | none |
| (8) | critical/high unaccepted findings resolved | W3 (finding states and remediation, CAP-44.g, and the A11 audit) | none |
| (9) | runtime rebuildable | W3 (derived memory rebuildable, CAP-48.b) | the derived state rebuilt from git that the lite A10 gate checks (CAP-20) |
| (10) | clean-machine reconstruction demonstrated | W3 (CAP-48.b) | none |

## 6. Differences from the CIT-P

Each difference between what was applied and the CIT-P's text (§6 and §7), with its reason. Every other change is as
the CIT-P proposed (§3.1).

| # | Difference | Reason |
|---|---|---|
| (a) | CAP-44.h keeps §6.1's full list of lite conditions (A0–A6 and A8 with their stage records and the A5 review, the native layout, the lite A7 and A10 gates, the pinned, hash-verified release, and G's three) and adds the ten of §20, numbered (1) to (10) (§5). "Every lite condition" in the F rule means that full list. | C (i): the named read was allowed and made; CIT-P §7 C (i) says v4.2's CAP-44.h then "lists the ten conditions, each marked lite W2 or W3" |
| (b) | Condition (3) is worded "path mapping, with the A5 independent review passed", not the source's "path mapping accepted". | In a text whose rule is that only the owner accepts an exception (F (i)), "accepted" would read as an accepted exception; the acceptance test of F reads it so |
| (c) | CAP-45.a's "(signed tag)" now reads "(the signed tag in W3, CAP-02.c)", and the Wave 2 clause of §7 D (ii) follows; DEC-722 is added to CAP-45.a's source field, not to CAP-45's `sources`. | D (ii) gives the clause, not the edit; §6.1 shows no CAP-45.a text and names neither source field; every mention of the signed tag then carries W3 |
| (d) | The new ids sit after the last existing item of their capability: CAP-43.d after CAP-43.c; CAP-44.k and CAP-44.l after CAP-44.j. | §6.1's excerpt shows CAP-44.k and CAP-44.l right after CAP-44.h; placed after the last item, the ids of each capability read in letter order. The CIT-P gives no rule on placement |
| (e) | The 4.2 change-log entry and change row add to §6.1's text: the approval by the owner (DEC-741), the ten conditions from the named read (C), CAP-45.a's Wave 2 wording (D) and the status ACCEPTED in both files (row W2-L343). | the answers C, D and the row W2-L343 changed more than §6.1's entry named |
| (f) | CAP-45.a's capability record (`docs/contract/capabilities/CAP-45.a.md`) cites version 4.2 but keeps its 4.1 item text: it is DERIVED and now stale against `contract.yaml`. | it is in neither K (1) (the version line) nor the K (2) reading (the records CIT-P §8 names); open for the owner (§8) |
| (g) | Three wordings of CAP-44.h differ from §6.1's: "gov doctor green (exit 0)" for "gov doctor green"; "each lite condition not met" for "each condition not met"; "only the owner accepts an exception; the auditor accepts none" for "the auditor accepts no exception". | the wording of the answers themselves: "`gov doctor` green (exit 0)" is CIT-P §7 G (i)'s; "only the owner accepts an exception" is DEC-741 F (i)'s; "lite condition" is the term of (a) |

## 7. Against the KPI lines and the acceptance tests

| KPI line | State |
|---|---|
| 1. The CIT-P names each change, its source (DEC-722) and its impact | the CIT-P, approved (DEC-741) |
| 2. Contract v4.2 moves exactly those parts to Wave 2; CAP-02.c, A9, A11, the qualification certificate and the rest of CAP-43.b stay in Wave 3 | `90c4d20a` (§3.1) |
| 3. The plan validator's two-way check covers the moved parts | **open:** needs the Wave 2 plan validator, W2-51 (DAEO-egsy; DEC-744); no test yet |
| 4. The CIT-E record matches the CIT-P, or lists the differences | this record (§3, §6) |
| Failure line: a Contract item moved without a CIT-P line, or a CIT-P line with no change, fails the validator | **open:** the same validator, W2-51; no test yet |

The acceptance tests are `tests/acceptance/W2-49/` (129 tests, written by the independent test designer before the
implementation, MR-3). `docs/plan/tools/validate_s1.py` was not run (DEC-738).

## 8. What stays open

- **The eight rows of `docs/contract/SOURCE_MAP.csv`** that state W3 for the moved parts (rows 235, 237, 248, 251, 256,
  280, 283, 292; CIT-P §8): not decided by DEC-741, left as they are. **Applied** under DEC-745 item 2 in the resume round (§3, "Resume round, DEC-745 item 2").
- **CAP-45.a's capability record** (difference (f)): stale against `contract.yaml` (it still says "authenticated source
  (signed tag)", with no Wave 2 clause). For the owner: whether it is regenerated, and by which commit.
- **The validator lines (DEC-744):** KPI success line 3 and the failure line need the Wave 2 plan validator, ticket
  W2-51 (DAEO-egsy). This ticket closes after W2-51; no test is written for them yet.
- **Row W2-I017:** carried to Wave 3 at W2-30's close, by the orchestrator, under J (i). Nothing changes it at W2-49's
  close, although W2-49 lists it in its `list_rows`.
- **K (2):** the reading in `7f935156` waits for the owner to confirm or overturn it.
- **DEC-741** (and DEC-744) are not yet in this worktree's register: DEC-741 is staged for the owner's commit with
  `Role: owner` (DEC-724).
- **W2-52 (DAEO-siiz)** builds the lite A7 and A10 stage records; until it closes, CAP-44.f (lite) is delivered by no
  closed ticket (exit criterion 7).

## 9. How it is reversed

As CIT-P §9 states: a revert is a new commit, nothing is amended or rewritten (DEC-720 item 4; WBS §0 rule 2), and it
needs the owner's decision through the same CAP-33 route.

- Reverting `7f935156` alone drops the K (2) reading: the eight records return to their 4.1 text (the six that existed
  at the base) or are removed (CAP-43.d, CAP-44.k, CAP-44.l), with the version line of `5a6a12f5` kept; the K (2) test
  file is then dropped alone (the suite's README, §2a).
- Reverting `7f935156`, `5a6a12f5` and `90c4d20a` restores Contract 4.1 in both files, CAP-44.f, CAP-44.h and CAP-43.b
  at W3, CAP-43.d, CAP-44.k and CAP-44.l gone, CAP-45.a as at 4.1, the status of each file as it was, and the 273
  records citing 4.1. The 4.2 text stays in git as a kept version (CAP-33.e).
- Reverting this commit removes this record and returns the CIT-P to `status: PROPOSED` without §13.
- What a git revert does not undo by itself (DEC-741, W2-52 and its ticket files, W2-02's ticket, row W2-I017) is
  reversed as CIT-P §9's second table says.
