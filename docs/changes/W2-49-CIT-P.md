---
id: W2-49-CIT-P
type: change-impact-proposal
status: PROPOSED
pending: the owner's approval (queued package Q-14), after an independent review (CAP-33)
date: 2026-10-16
branch: w2/W2-49
base: a02e3485
ticket: DAEO-ha8z (W2-49)
author: product-spec (W2-49, single author)
review: a fresh, read-only independent auditor (CAP-33.d, CAP-47.b)
decisions_carried: [DEC-722]
decisions_read: [DEC-006, DEC-064, DEC-090, DEC-092, DEC-105, DEC-614, DEC-718, DEC-721, DEC-727, DEC-728, DEC-729]
state_class: EVIDENCE
---

# W2-49 — Change-impact proposal (CIT-P) for Contract v4.2, lite

This change carries DEC-722 into the Contract. Three Wave 3 parts of Contract v4 (version 4.1) come into Wave 2 in a
lite form: the adoption verdict (CAP-44.h), the A7 and A10 gates of CAP-44.f, and the manifest and file hashes of
CAP-43.b. Signed release tags (CAP-02.c) stay in Wave 3.

It follows CAP-33's route (CAP-33.d): evidence, proposal, independent review, the owner's approval, versioned
promotion. This record is the proposal. **Nobody edits `contract.yaml` or `CONTRACT_v4.md` before the owner approves
it.** The owner's approval is queued as Q-14 (`docs/plan/WAVE_2_WBS.md` §7). The apply step and its record,
`docs/changes/W2-49-CIT-E.md`, come after it.

Everything here comes from a named source, given by id. Where no source settles a point, it is marked **Question for
the owner** and listed in §7. None of those answers is taken here.

## 1. What triggers the change

| # | Trigger | Source | State at the base (`a02e3485`, Contract 4.1) |
|---|---|---|---|
| T1 | The Wave 2 brief asks for an EXAMIN adoption with a healthy verdict, and for immutable, pinned releases | DEC-722 "Basis" | CAP-44.f, CAP-44.h, CAP-43.b and CAP-02.c are all `wave: W3` |
| T2 | The owner chose **apply now, lite**, by a CIT-P to Contract v4.2, through independent review and the owner's approval; W2-49 carries it | DEC-722 item 1, under DEC-105, DEC-718 and CAP-33 | No CIT-P yet |
| T3 | CAP-02.c (signed release tags) stays in Wave 3; Wave 2 releases are pinned and hash-verified, not signed | DEC-722 item 2 | CAP-02.c is `W3`, unchanged |
| T4 | Exit criterion 6 reads "EXAMIN runs a pinned, hash-verified Gov OS release" | DEC-722 item 3; WBS §5 | Already in the approved plan (DEC-729) |
| T5 | The list row W2-I017 comes in, lite, through W2-49 | `docs/plan/WAVE_2_TRIAGE.md` (row W2-I017) | Row open, triaged to W2-49 |

## 2. The three options (DEC-105)

DEC-105 and CAP-33.e require a CIT-P that changes a closed specification to give three options with their cost. The
owner has already chosen one (DEC-722: apply now, lite). The options are restated here for the review.

| Option | What it means here | Cost |
|---|---|---|
| **Apply now, lite** (the owner's choice, DEC-722) | Contract 4.1 → 4.2. CAP-44.h, the A7 and A10 gates of CAP-44.f and the manifest and file hashes of CAP-43.b move to Wave 2 in a lite form. What stays is kept in Wave 3 (§4). | Cost: this CIT-P, one independent review and the owner's approval (Q-14). Then one apply round on the two Contract files and the CIT-E, the regenerated capability records (§8), and an update to the validator's version check (P-W2-11). The build work is already in the approved plan: W2-02, W2-16, W2-18, W2-27 to W2-30. There is one gap with no ticket, finding F-1 in §10. |
| **Defer** (record it and continue) | Contract stays 4.1. The lite parts are built by the plan but checked against no Wave 2 item. | Cost: no Contract work now. Exit criterion 6 ("against Contract v4.2's lite CAP-44.h") and exit criterion 7 ("Contract v4.2's lite items") would have nothing to point at. W2-16's KPI `[CAP-43.b lite]` would cite a Wave 3 item, and so would W2-24's. The verdicts of W2-28 and W2-30 would rest on no Wave 2 condition. The approved plan (DEC-729) would have to be revised, or its Track B verdict would wait for Wave 3. |
| **Re-baseline** (reopen and re-plan) | Reopen CAP-44, CAP-43, CAP-47 and CAP-02 whole. Re-plan adoption and releases across Waves 2 and 3, and retire the work this invalidates. | Cost: the largest. It reopens A9, A11, the full verdict, the full adoption and audit roles (CAP-47.a) and the signed tag, none of which DEC-722 brings forward. The copy path (W2-49 → W2-16 → W2-18 → W2-23 → W2-27 → W2-28) and the critical path would be re-planned. DEC-722 chose lite, so nothing in the evidence calls for it. |

## 3. What moves to Wave 2, lite (source: DEC-722 item 1)

### 3.1 CAP-44.h, lite: the adoption verdict

CAP-44.h, lite, keeps the three verdicts of the Contract's own text: **ADOPTED_HEALTHY**, **ADOPTED_WITH_ACCEPTED_EXCEPTIONS** and **NOT_ADOPTED_HEALTHY** (DEC-722 item 1; CAP-44.h; CAP-44 acceptance; DEC-090).

**What the Contract says about the conditions.** CAP-44.h reads "Final verdict … with the ten ADOPTED_HEALTHY
conditions", with the sources "Adoption Protocol v3.0 §20; Distribution Protocol v1.2 §18; DEC-006". The Contract
names ten conditions but **does not list them**. Neither does the generated record `docs/contract/capabilities/CAP-44.h.md`,
nor the source map's rows for Adoption Protocol §20 and Distribution Protocol §18 (`SOURCE_MAP.csv`). The two protocols
are originals kept as provenance under `docs/source/` (DEC-058). `docs/SOURCES.md` says those originals are excluded
from agents. This CIT-P did not read them.

So the ten conditions cannot be mapped one by one here, from what an agent may read (Question C, §7). What the
Contract does state, item by item, is which adoption parts are delivered in which wave. From those items, the
conditions a lite verdict checks and does not check are these:

| Condition | Contract item and source | Wave in 4.2 | Lite verdict |
|---|---|---|---|
| A0 safety baseline, A1 inventory, A2 classification, A3 path map, A4 batched plan with rollback points, each with its stage record | CAP-44.b; CAP-44 acceptance ("one evidence record per stage") | W1 | checks |
| A5 independent review of the path map before any move | CAP-44.c; DEC-090 | W1 | checks |
| A6 controlled migration, failed batch rolled back, moves before new indexing | CAP-44.d | W1 | checks |
| A8 legacy memory extraction and retirement | CAP-44.e | W1 | checks |
| The path map keeps a healthy native layout | CAP-44.j | W1 | checks |
| A7 independent migration verification, lite | CAP-44.f (lite, §3.2) | W2 | checks |
| A10 independent memory verification, lite | CAP-44.f (lite, §3.2) | W2 | checks |
| The pinned, hash-verified release: `gov doctor` reports MATCH for the pinned `framework.lock` manifest | CAP-02.a (W1); CAP-43.b lite (§3.3); DEC-722 items 2 and 3; exit criterion 6 | W1, W2 | checks |
| A9 new knowledge fabric | CAP-44.f | W3 | does not check |
| A11 full audit | CAP-44.f | W3 | does not check |
| A7 and A10 beyond their lite form | CAP-44.f; CAP-47.a | W3 | does not check |
| Remediation, finding states, human gates during adoption | CAP-44.g | W3 | does not check |
| Interrupted-session recovery and freeze during adoption | CAP-44.i | W3 | does not check |
| Signed release tag, verified by `git tag -v` | CAP-02.c; DEC-722 item 2 | W3 | does not check |

**Who gives it.** A fresh independent auditor (W2-28 on the copy, W2-30 on the real repository: WBS §2 and exit
criterion 6). The Wave 1 Independent Auditor role exists (CAP-47.b, W1). The full adoption and audit role separation
(CAP-47.a) stays in Wave 3.

**Question for the owner (E, §7).** CAP-54.a (W1, DEC-006) says "A0–A11 remains the target for ADOPTED_HEALTHY". A lite
ADOPTED_HEALTHY issued without A9 and A11 could be read as meeting that target. The proposed text (§6) has the lite
verdict record name itself lite and name the conditions it does not check. That is a proposal for the owner's
approval, not a rule this CIT-P can make.

### 3.2 The A7 and A10 gates of CAP-44.f, lite

CAP-44.f reads: "A7 independent migration verification; A9 new knowledge fabric; A10 independent memory verification; A11
full audit" (Adoption Protocol v3.0 §12, §14–§16; Distribution Protocol v1.2 §10). DEC-722 brings A7 and A10 into Wave 2,
lite. A9 and A11 stay in Wave 3.

- **A7, lite: what it checks.** A fresh Independent Auditor session (the Wave 1 role, as DEC-090 uses it for A5) checks
  the A6 migration (CAP-44.d: moves per the batched plan, failed batches rolled back, moves before new indexing). It
  checks the migration against the A3 path map and the A4 plan that A5 reviewed (CAP-44.b, CAP-44.c), and leaves A7's
  own stage record (CAP-44 acceptance). The source map names A7's role "Role D — Independent Migration Verifier",
  carried by "CAP-44 covers A7 + CAP-47".
  - **What of A7 stays for Wave 3:** a separate verifier role under CAP-47.a's role separation, and anything in
    Adoption Protocol §12 beyond these checks. The protocol was not read here (Question C).
- **A10, lite: what it checks.** A fresh Independent Auditor session checks the memory that a Wave 2 adoption leaves:
  - the A8 legacy memory extraction and retirement (CAP-44.e);
  - the derived state rebuilt from git (CAP-20, W1).

  It leaves A10's own stage record. The source map names A10's role "Role F — Independent Memory Verifier/Test Author",
  carried by "CAP-44 covers A10 + CAP-47 … + CAP-49".
  - *This reading is the CIT-P's, for the owner's approval.* A10 verifies memory, and with A9 in Wave 3 the memory that
    exists after a Wave 2 adoption is A8's result and the rebuilt index.
  - **What of A10 stays for Wave 3:** verification of the A9 knowledge fabric (A9 is W3), the qualification run's
    memory checks (CAP-49, W3), and the separate role under CAP-47.a.
- **A9 and A11 stay in Wave 3 in full** (DEC-722 names only A7 and A10; DEC-090; the W2-49 card).

### 3.3 CAP-43.b, lite: the manifest and the file hashes

CAP-43.b lists the release contents: "semantic version, manifest, file hashes, supported migrations, schema versions,
CLI/runtime versions, adapter/capability versions, release notes, affected indexes, required human decisions, rollback
procedure" (Contract v3 S2; Framework v4.1.2 §75D).

CAP-43.b, lite, holds **the manifest and the file hashes**, and nothing else. A Wave 2 release is pinned and
hash-verified, not signed. Sources: DEC-722 item 1 ("release contents: a manifest and file hashes"), DEC-722 item 2,
and KPI line 2.

W2-16 builds more than this. That part is recorded as delivered ahead of its wave (Question B, §7).

## 4. What stays in Wave 3 (KPI line 2; DEC-722 item 2; the W2-49 card)

| Part | Item | Why it stays |
|---|---|---|
| Signed release tags | CAP-02.c "SSH-signed release tag, verified by `git tag -v`" stays W3 | DEC-722 item 2; CAP-02 acceptance ("at Release 1") |
| A9 new knowledge fabric | in CAP-44.f; stays W3 | DEC-722 names only A7 and A10; DEC-090 |
| A11 full audit | in CAP-44.f; stays W3 | Same; W2-I017 ("A11 stays in Wave 3") |
| The qualification certificate | CAP-43.c "Release certification by qualification" stays W3 | The W2-49 card |
| The rest of CAP-43.b | stays in Wave 3 | KPI line 2 |

**The qualification certificate.** No Contract item uses the term "qualification certificate". The only certification
item is CAP-43.c, "Release certification by qualification" (Framework v4.1.2 §75C; DEC-067). This CIT-P reads the
card's "qualification certificate" as CAP-43.c: the certification a release gets from the qualification run of DEC-067
(CAP-49, W3), before Release 1 (DEC-064). It stays in Wave 3.

**The rest of CAP-43.b, item by item.** Each of these stays in Wave 3:
- semantic version;
- supported migrations;
- schema versions;
- CLI/runtime versions;
- adapter/capability versions;
- release notes;
- affected indexes;
- required human decisions;
- rollback procedure.

## 5. Impact

### 5.1 Tickets (the W2-49 card's list, and the other tickets that cite the moved ids)

| Ticket | What it gains or now depends on |
|---|---|
| **W2-02** record types (product-spec) | Gains the source for its adoption-verdict type: "the three CAP-44.h verdicts and the conditions behind them, in the lite form Contract v4.2 states". Depends on v4.2's CAP-44.h text for those conditions. §1's table gives W2-02 no dependency on W2-49, and both are in layer 2 (finding F-2). |
| **W2-16** immutable, hash-pinned releases | Gains a Wave 2 item to deliver: its KPI `[CAP-43.b lite]` and its "Closes: CAP-43.b (lite, DEC-722)" point at CAP-43.b lite, `W2`. Depends on W2-49, as §1 already says. Its manifest also builds part of the W3 rest of CAP-43.b ahead of its wave (Question B). |
| **W2-18** pinned install | Gains a Wave 2 Contract basis for "a hash-verified release" (CAP-43.b lite, through W2-16). Its own citations (`[CAP-43]`, W1) are unchanged. It depends on W2-16 as before. |
| **W2-27** EXAMIN adoption on a copy | Gains the lite A7 and A10 gates of CAP-44.f to run ("the lite A7 and A10 gates of Contract v4.2"). It depends on W2-49 (as §1 says), on W2-16 and W2-18 for the pinned release, and on W2-50 for its clone folder (DEC-727, DEC-728). |
| **W2-28** verdict on the copy | Gains the lite conditions of CAP-44.h to judge against. Depends on v4.2's CAP-44.h text. |
| **W2-29** EXAMIN adoption on the real repository | The same lite A7 and A10 gates as W2-27, on the real repository, with only the pinned, hash-verified release. |
| **W2-30** healthy-adoption verdict | Gains the Wave 2 item it closes ("CAP-44.h (lite)"). Its ADOPTED_HEALTHY is the verdict of exit criterion 6. |
| W2-24 Track A gate run (also cites a moved id) | Its KPI `[AR-10, CAP-43.b lite]` points at CAP-43.b lite, `W2`. Its fixture adoption (A0 to A6, A8) runs no A7 or A10 gate; that is unchanged. |
| W2-46, W2-47 exit run and exit audit | W2-47 gives a finding row to "every Contract v4.2 lite item". With the form proposed in §6, those are CAP-44.f, CAP-44.h and CAP-43.b, each `W2`. |

In short: W2-02, W2-16, W2-18 and W2-27 to W2-30 each depend on Contract v4.2, as the W2-49 card says. W2-24, W2-46
and W2-47 cite it as well.

### 5.2 Exit criteria 6 and 7 (WBS §5)

- **Exit criterion 6** ("EXAMIN is adopted with a healthy verdict … against Contract v4.2's lite CAP-44.h. EXAMIN runs a
  pinned, hash-verified Gov OS release"). It now depends on v4.2's CAP-44.h, lite (§3.1), for the verdict's reference,
  and on CAP-43.b, lite (§3.3), for "pinned, hash-verified" (DEC-722 item 3).
- **Exit criterion 7** ("the Contract's 17 Wave 2 items, and Contract v4.2's lite items (CAP-44.h with A7 and A10,
  CAP-43.b), are each delivered by a closed ticket and cited by an acceptance test. The plan validator checks this
  both ways"). It gains three Wave 2 covers items: CAP-44.f, CAP-44.h and CAP-43.b, so 17 become 20.
  - With the split form recommended in §7 (Question A), each of these has one wave. The two-way check can then read
    `wave` alone.
  - The check itself needs the plan validator's Wave 2 form, which is with the owner (P-W2-11; KPI line 3). No test is
    written for it yet (`tests/acceptance/W2-49/README.md`).
  - Finding F-1 (§10): no ticket delivers the lite A7 and A10 gates.

### 5.3 The list row W2-I017

W2-I017, "Independent adoption gates A7, A10, A11 and the final verdict (Wave 3)", closes when "A7, A10 and A11 run, and
an adoption verdict is issued" (`WAVE_2_LIST.md`). Its triage: "A7, A10 and the verdict come into Wave 2, lite, by
Contract v4.2 (DEC-722); A11 stays in Wave 3."

After v4.2, A7, A10 and the verdict come into Wave 2, lite (CAP-44.f, CAP-44.h). They are delivered when W2-27 to
W2-30 have run. A11, and A7 and A10 in full, stay in Wave 3. The orchestrator keeps the list (DEC-718; WBS §0 rule 10).
It marks the row in part: the lite part with the commit that closes it, and the rest carried to Wave 3.

### 5.4 Other specification text

| Text | Impact |
|---|---|
| CAP-44 `wave_note` and `provider` | Today they say "the independent gates A7, A10, A11 and the final verdict are W3 with CAP-47 (DEC-090)" and "W3: A7/A10/A11 gates + verdict". Both are reworded (§6). CAP-44's own `wave` stays W3, because its acceptance needs A0–A11. |
| CAP-47 `wave_note` | Says "full independent adoption/audit roles and the A7, A10, A11 gates W3". Reworded so that the lite A7 and A10 are W2 (§6). CAP-47's `wave` stays W3. |
| CAP-43 `wave_note`, `sources` | DEC-722 is added, and a note says what W2-16 builds ahead of its wave (§6). CAP-43's `wave` stays W1. |
| CAP-45.a (W2, W2-17) | Its text includes "authenticated source (signed tag)". The signed tag stays W3 (CAP-02.c, DEC-722 item 2), and W2-17's KPIs verify manifest and file hashes only. Question D, §7. |
| Contract §1 Counts | Unchanged: the table counts capabilities, and none changes wave. |
| DEC-090 | It says the gates A7, A10 and A11 are Wave 3 and "the verdict is issued from Wave 3". DEC-722 changes that in part, but does not name DEC-090. No ACCEPTED entry is edited. Question E, §7. |
| Charter v5 | **No change.** The precedence is Charter v5 → Contract v4 (CAP-01). The Charter keeps Release 1 as "a signed `v1.0.0` tag" (§1), which CAP-02.c in Wave 3 respects. Finding F-3 (§10) concerns a Charter line this change sits beside but does not touch. |

## 6. The proposed v4.2 text

This text is proposed, and applied only after the owner's approval. It uses the split form recommended in Question A,
with CAP-43.b lite as in Question B. If the owner answers A or B differently, the apply step follows the answer, and
the CIT-E lists the difference.

### 6.1 `contract.yaml`

Header:

```yaml
version: '4.2'
revised: '<the apply date>'
```

New `change_log` entry, after 4.1 (4.0 and 4.1 unchanged; every version is kept, CAP-33.e):

```yaml
- version: '4.2'
  date: '<the apply date>'
  change: 'W2-49 specification change (docs/changes/W2-49-CIT-P.md, W2-49-CIT-E.md). Carries DEC-722: the adoption
    verdict (CAP-44.h) and the A7 and A10 gates of CAP-44.f come into Wave 2, lite; the release contents of CAP-43.b come
    into Wave 2, lite: the manifest and file hashes. What stays in Wave 3 is split into new covers items: CAP-44.k (A9,
    A11, and A7 and A10 beyond their lite form), CAP-44.l (the verdict with the ten ADOPTED_HEALTHY conditions) and
    CAP-43.d (the rest of the release contents). CAP-02.c (signed release tags) and CAP-43.c stay in Wave 3. Wave notes
    in CAP-43, CAP-44 and CAP-47. No capability changes wave; 62 capabilities; 211 → 214 covers items.'
```

CAP-43 (`wave: W1` unchanged):

```yaml
  wave_note: 'Release 1 tag at the end of qualification; the manifest and file hashes of a release are W2 (CAP-43.b, lite,
    DEC-722); W2-16 builds the semantic version, the CLI version, the schema versions and the release notes of CAP-43.d
    ahead of that item''s wave'
  sources: [ … as 4.1 …, DEC-722]
  covers:
  - id: CAP-43.b
    item: 'Release contents, lite: the manifest and the file hashes; a release is pinned and hash-verified, not signed'
    source: Contract v3 S2; Framework v4.1.2 §75D; DEC-722
    wave: W2
  - id: CAP-43.c            # unchanged, W3
  - id: CAP-43.d
    item: 'Release contents beyond the lite manifest and file hashes of CAP-43.b: semantic version, supported migrations,
      schema versions, CLI/runtime versions, adapter/capability versions, release notes, affected indexes, required human
      decisions, rollback procedure'
    source: Contract v3 S2; Framework v4.1.2 §75D; DEC-722
    wave: W3
```

CAP-44 (`wave: W3` unchanged):

```yaml
  wave_note: W1 delivers gov init (copier copy) and adoption stages A0-A6 and A8 with baseline, rollback points and the A5
    independent path-map review (W1-39, W1-41); the lite A7 and A10 gates and the lite verdict are W2 (CAP-44.f, CAP-44.h;
    DEC-722); A9, A11, the full A7 and A10 gates and the verdict with the ten ADOPTED_HEALTHY conditions are W3 with CAP-47
    (CAP-44.k, CAP-44.l; DEC-090)
  provider: [Copier 9.18.2, W1-39, W1-41, 'W2: lite A7/A10 gates + lite verdict (DEC-722)',
    'W3: A9/A11 + full A7/A10 gates + full verdict (with CAP-47)']
  sources: [ … as 4.1 …, DEC-722]
  covers:
  - id: CAP-44.f
    item: 'A7 independent migration verification and A10 independent memory verification, lite: each by a fresh Independent
      Auditor session and recorded as its own stage; A7 checks the A6 migration against the A3 path map and the A4 plan
      reviewed at A5; A10 checks the A8 legacy memory extraction and retirement and the derived state rebuilt from git'
    source: Adoption Protocol v3.0 §12, §15; Distribution Protocol v1.2 §10; DEC-722
    wave: W2
  - id: CAP-44.h
    item: 'Adoption verdict, lite: ADOPTED_HEALTHY / ADOPTED_WITH_ACCEPTED_EXCEPTIONS / NOT_ADOPTED_HEALTHY from a fresh
      Independent Auditor against the lite conditions: A0–A6 and A8 with their stage records and the A5 review, the native
      layout kept, the lite A7 and A10 gates passed, and the pinned, hash-verified release (gov doctor MATCH); the verdict
      record names itself lite and names the conditions it does not check'
    source: Adoption Protocol v3.0 §20; Distribution Protocol v1.2 §18; DEC-006; DEC-722
    wave: W2
  - id: CAP-44.k
    item: 'A9 new knowledge fabric; A11 full audit; A7 and A10 beyond their lite form in CAP-44.f (separate verifier roles,
      A10 over the A9 knowledge fabric)'
    source: Adoption Protocol v3.0 §12, §14–§16; Distribution Protocol v1.2 §10; DEC-722
    wave: W3
  - id: CAP-44.l
    item: Final verdict ADOPTED_HEALTHY / ADOPTED_WITH_ACCEPTED_EXCEPTIONS / NOT_ADOPTED_HEALTHY with the ten ADOPTED_HEALTHY
      conditions, after A0–A11
    source: Adoption Protocol v3.0 §20; Distribution Protocol v1.2 §18; DEC-006; DEC-722
    wave: W3
```

CAP-47 (`wave: W3` unchanged):

```yaml
  wave_note: Independent Test Designer and Independent Auditor roles in W1 (W1-33), including the A5 path-map review (DEC-090);
    the lite A7 and A10 gates W2 by that Independent Auditor role (CAP-44.f, DEC-722); full independent adoption/audit roles
    and the full A7, A10 and A11 gates W3
```

`provider` on the three W2 items: **none**, as for the 17 Wave 2 items of 4.1. They get `[W2-16]` (CAP-43.b), the
ticket that delivers lite A7 and A10 (CAP-44.f, finding F-1), and `[W2-30]` (CAP-44.h) only if the owner's answer to
P-W2-11 extends the Wave 1 provider rule to Wave 2.

What a provider is depends on P-W2-11. This CIT-P does not settle it.

### 6.2 `CONTRACT_v4.md`

`CONTRACT_v4.md` follows the YAML line for line ("Same content", the YAML's header). It changes:

- **Frontmatter:** `version: "4.2"`, `revised:` the apply date, and DEC-722 added to `decisions`.
- **Title line:** "(version 4.2)". The line "**Version 4.2** (<the apply date>)."
- **Change table:** a new row `| 4.2 | <the apply date> | <the change_log text above> |`. The 4.0 and 4.1 rows are
  unchanged.
- **CAP-43, CAP-44 and CAP-47 blocks:** the `Wave:`, `Provider:` and `Sources:` lines follow the YAML.
- **Covers lines,** in the form `` `id` [wave] item — source ``:
  - `` `CAP-43.b` [W2] Release contents, lite: the manifest and the file hashes; a release is pinned and hash-verified, not signed — Contract v3 S2; Framework v4.1.2 §75D; DEC-722 ``
  - `` `CAP-43.d` [W3] Release contents beyond the lite manifest and file hashes of CAP-43.b: … — Contract v3 S2; Framework v4.1.2 §75D; DEC-722 ``
  - `` `CAP-44.f` [W2] A7 independent migration verification and A10 independent memory verification, lite: … — Adoption Protocol v3.0 §12, §15; Distribution Protocol v1.2 §10; DEC-722 ``
  - `` `CAP-44.h` [W2] Adoption verdict, lite: ADOPTED_HEALTHY / ADOPTED_WITH_ACCEPTED_EXCEPTIONS / NOT_ADOPTED_HEALTHY … — Adoption Protocol v3.0 §20; Distribution Protocol v1.2 §18; DEC-006; DEC-722 ``
  - `` `CAP-44.k` [W3] A9 new knowledge fabric; A11 full audit; … — Adoption Protocol v3.0 §12, §14–§16; Distribution Protocol v1.2 §10; DEC-722 ``
  - `` `CAP-44.l` [W3] Final verdict … with the ten ADOPTED_HEALTHY conditions, after A0–A11 — Adoption Protocol v3.0 §20; Distribution Protocol v1.2 §18; DEC-006; DEC-722 ``

  The `…` stands for the full YAML text.
- **§1 Counts:** unchanged.

### 6.3 Version

The version becomes 4.2. The file names and the id `CONTRACT-v4` are unchanged, as at 4.1. Covers items by wave go
from W1 149 / W2 17 / W3 38 / NONE 7 to W1 149 / W2 20 / W3 38 / NONE 7.

## 7. Questions for the owner (with the approval of this CIT-P, Q-14)

**A. The form of a split item.** CAP-44.f (A7 and A10 move, A9 and A11 stay) and CAP-43.b (manifest and file hashes
move, the rest stays) each straddle two waves. So does CAP-44.h (the lite verdict moves, the verdict with the ten
conditions stays). No source fixes the form.

| Option | For exit criterion 7 (each lite item delivered by a closed ticket and cited by a test, checked both ways) | Cost |
|---|---|---|
| **(a1) Split; the original id carries the lite W2 part, a new id the W3 rest** (recommended) | Each id has one wave, so the validator's two-way check reads `wave` and nothing else. The ids the plan and five ticket files already cite in the lite sense keep pointing at the W2 item: W2-02, W2-16, W2-24, W2-28 and W2-30 cite `CAP-43.b lite` or `CAP-44.h (lite)`. | Three new ids (CAP-43.d, CAP-44.k, CAP-44.l) and three new generated records. The three original ids have narrower text in 4.2 than in 4.1, and the 4.1 meaning stays in the change log and in git (CAP-33.e). No ticket or card changes. |
| (a2) Split; the original id keeps the W3 meaning, new ids for the lite parts | The same one-wave-per-id benefit. | The five ticket files and the WBS cards re-cite new ids, and the approved plan (DEC-729) is the owner's to change. |
| (b) Move the item whole to W2, with a note on what stays | A validator reading `wave` would require A9, A11 and the nine other release contents in Wave 2. It must parse free-text notes to tell them apart, which is fragile. | Smallest text change; the largest validator change. |
| (c) Keep it in W3, with a note on what moves | The validator sees no W2 item, so the lite items are invisible to the two-way check unless it parses notes. | Same as (b). |

*Recommendation:* (a1). *Confidence:* medium-high. Nothing a source says decides between (a1) and (a2). (a1) is
cheaper and matches every existing citation. DEC-092 ("nothing is dropped by the compression") is why the W3 rest gets
a covers item of its own, rather than living only in a wave note.

**B. What CAP-43.b, lite, holds.** W2-16's manifest holds the semantic version and the commit, every shipped file with
its sha256, the wheel hash, the CLI version, the schema versions, the release notes, and the manifest's own hash.

| Part W2-16 builds | Where it sits in the Contract |
|---|---|
| The manifest; every shipped file with its sha256 | The lite CAP-43.b: "the manifest and file hashes" |
| The wheel hash; the manifest's own hash | This CIT-P reads both as file hashes within the lite manifest, for the owner's approval: the wheel is a shipped file, and the manifest's hash is the manifest's own integrity |
| The commit | Already in CAP-43's W1 acceptance ("template tag, commit and file-hash manifest") |
| The semantic version, CLI version, schema versions, release notes | The W3 rest of CAP-43.b (CAP-43.d under A (a1)) |

- *Options:*
  - (i) Lite CAP-43.b is only the manifest and the file hashes. W2-16's further content is recorded as delivered ahead
    of its wave, in CAP-43's wave note.
  - (ii) The lite item widens to what W2-16 builds.
- *Recommendation:* (i). KPI line 2 and DEC-722 item 1 are the owner's words ("a manifest and file hashes"; "the rest of
  CAP-43.b stays in Wave 3"). Option (ii) would move more than "exactly those parts". The acceptance tests
  (`test_rest_of_cap_43b_stays_in_wave_3`) hold the semantic version, schema versions, CLI/runtime versions and release
  notes in W3.
- *Confidence:* high.

**C. The ten ADOPTED_HEALTHY conditions.** The Contract names ten and lists none (§3.1). Their source text is excluded
from agents. A lite verdict needs a definite list, for three users: W2-02's verdict type, W2-28's verdict and W2-30's
verdict.

- *Options:*
  - (i) The owner allows a named read of Adoption Protocol v3.0 §20 and Distribution Protocol v1.2 §18 for the apply
    round. Then v4.2's CAP-44.h lists the ten conditions, each marked lite W2 or W3.
  - (ii) v4.2 states the lite conditions in terms of the Contract's own items, as in §3.1 and §6.1, and does not map
    them to the ten. The ten stay with CAP-44.l in W3.
  - (iii) The owner gives the ten.
- *Recommendation:* (i), with (ii) as the text if the owner declines the read. Without the list, a lite
  ADOPTED_HEALTHY cannot show which of the ten it leaves out.
- *Confidence:* medium.

**D. CAP-45.a's "authenticated source (signed tag)".** CAP-45.a is a W2 item (W2-17). The signed tag stays W3 (CAP-02.c,
DEC-722 item 2).

- *Options:*
  - (i) No change in v4.2. W2-17 verifies manifest and file hashes, and CAP-45.a's signed-tag part is named at the exit
    audit as checked with CAP-02.c in W3.
  - (ii) v4.2 adds to CAP-45.a: "in Wave 2 the authenticated source is the release's manifest and file hashes (CAP-43.b,
    lite); the signed tag with CAP-02.c (W3), DEC-722".
- *Recommendation:* (ii). It follows DEC-722 item 2 and keeps W2-17's closure honest. It is a rewording, not a move,
  but it goes beyond the three items DEC-722 names, so it is the owner's to approve.
- *Confidence:* medium.

**E. DEC-090 and CAP-54.a.**
- DEC-090 places A7, A10 and the verdict in Wave 3. DEC-722 brings them forward, lite, without naming DEC-090.
- CAP-54.a (DEC-006) keeps "A0–A11 … the target for ADOPTED_HEALTHY".
- *Options:*
  - (i) The owner's approval entry for Q-14 records that it amends DEC-090 in part. The lite verdict record names itself
    lite and the conditions it does not check (§6.1). CAP-54.a stays as written, because its target is the W3 verdict
    (CAP-44.l).
  - (ii) Leave both texts as they are, and read DEC-722 as overriding.
- *Recommendation:* (i). No ACCEPTED entry is edited, so the amendment is the owner's new entry. Its wording is the
  owner's.
- *Confidence:* medium.

## 8. Other files the v4.2 change touches

| File | Change | Who changes it | In W2-49's `allowed_paths`? | What the owner's approval needs to cover |
|---|---|---|---|---|
| `docs/contract/contract.yaml`, `docs/contract/CONTRACT_v4.md` | The v4.2 text (§6) | W2-49, the apply round | yes | The text, and the answers to A–E |
| `docs/changes/W2-49-CIT-E.md` | What was done, and each difference from this CIT-P | W2-49, the apply round | yes | — |
| `docs/contract/capabilities/CAP-43.b.md`, `CAP-44.f.md`, `CAP-44.h.md` | Rewritten: new title, item and wave | The orchestrator, by the script of DEC-614 (the records were made in `d8534afe` under DEC-614 and DEC-620); no generator was found in `src/`, `docs/` or `tests/` | no | A regeneration, in its own commit, from the approved `contract.yaml` |
| `CAP-43.d.md`, `CAP-44.k.md`, `CAP-44.l.md` (new, under A (a1)) | New records for the split | Same | no | Same |
| `CAP-43.md`, `CAP-44.md` | Their "Covers:" lists gain the new ids | Same | no | Same |
| The other 268 records under `docs/contract/capabilities/` | Each says "Contract v4, version 4.1" in its body. All 273 do today. | Same | no | Whether every record is regenerated to cite 4.2 (recommended: they are DERIVED), or only the changed ones |
| `docs/plan/tools/validate_s1.py` (the Wave 1 plan validator) | Its check "Contract is version 4.1 in both files, with a change log" (`['4.0', '4.1']`, `\| 4.1 \| 2026-10-03 \|`) fails on 4.2. Its yaml/markdown agreement check and its id form (`CAP-nn.<letter>`) hold for the text of §6. No test and no `gov check` family was found that runs it (a search of `src/`, `tests/`, `template/`). | Whoever the owner's answer to P-W2-11 names; it is in no Wave 2 ticket's paths | no | Either the validator's Wave 2 form under P-W2-11, or the version check named as an accepted red until then. KPI line 3 and the failure KPI wait for P-W2-11 too. |
| `docs/contract/SOURCE_MAP.csv` | The rows for Adoption Protocol §12, §15, §16, §20 and Distribution Protocol §18 say A7, A10 and the verdict are W3 | The orchestrator, or W2-49 if the approval adds the path | no | Whether these rows follow 4.2. The S2 change left the source map alone because it maps the originals, but these rows also state waves. |
| `docs/plan/WAVE_2_LIST.md` (row W2-I017) | Marked in part (§5.3) | The orchestrator (DEC-718; WBS §0 rule 10) | no | — (the orchestrator's) |
| `docs/DECISION_REGISTER.md` | The owner's entry for Q-14, and the DEC-090 amendment if E (i) | The owner, with `Role: owner` (DEC-724) | no | The entry itself |
| `governance/adoption/A1…A3` records | They list the three record paths; they are evidence and keep their pinned hashes (DEC-718) | Nobody | no | Nothing: they are not changed |

## 9. How it is reversed

A revert of the apply commit is a new commit: nothing on `w2/integrate` is amended or rewritten (DEC-720 item 4;
WBS §0 rule 2). Reverting it and the regeneration commit restores:
- Contract 4.1 in both files, with the 4.0 and 4.1 change-log rows as they are;
- CAP-44.f, CAP-44.h and CAP-43.b at `W3`, and CAP-43.d, CAP-44.k and CAP-44.l gone;
- the 273 records citing 4.1.

The 4.2 text stays in git as a kept version (CAP-33.e). A revert needs the owner's decision, through the same CAP-33
route.

| Ticket | What a revert does to it |
|---|---|
| W2-02 | Its verdict type loses "the lite form Contract v4.2 states" as its source |
| W2-16, W2-24 | Their `[CAP-43.b lite]` KPIs cite a W3 item again |
| W2-18 | No text change. Its hash-verified release loses its Wave 2 Contract basis |
| W2-27, W2-29 | The lite A7 and A10 gates have no Contract item |
| W2-28, W2-30 | Their verdicts have no Wave 2 conditions |
| W2-46, W2-47 | No v4.2 lite items to run or audit |

Exit criteria 6 and 7 lose their reference, and the plan would need the owner's revision (DEC-729). Work already
delivered stays delivered, now ahead of its wave. Nothing built is lost.

## 10. Findings made while listing the impact

- **F-1. No ticket builds the lite A7 and A10 gates.**
  - W2-27 runs them on the copy, W2-29 on the real repository, and W2-28 and W2-30 judge them. But no implementation
    or skill ticket has a KPI that adds A7 and A10 stage records to `gov adopt` or to the adopt skill.
  - W2-23 holds `src/gov/adopt/**`, but its KPIs do not name A7 or A10. W2-24's fixture adoption stops at A0–A6 and A8.
  - Exit criterion 7 needs each lite item "delivered by a closed ticket and cited by an acceptance test".
- **F-2. W2-02 reads v4.2's lite text but does not depend on W2-49.** Its KPI types the verdict "in the lite form
  Contract v4.2 states". §1 gives it no dependency, both are in layer 2, and W2-02 is on the critical path.
- **F-3. The Charter on adoption before Release 1.** Charter v5 §1 and DEC-064 say "Adoption into product repositories
  starts only after Release 1". The Wave 2 plan adopts EXAMIN's real repository (W2-29) and issues its verdict (W2-30),
  under DEC-712, DEC-714, DEC-718 and DEC-727, all the owner's. This change does not touch the Charter, and no entry
  read here amends that line. The Charter outranks the Contract (CAP-01), so it is named for the owner.
- **F-4. The two Contract files differ in status.** `contract.yaml` says `status: PROPOSED`, and `CONTRACT_v4.md`'s
  frontmatter says `status: ACCEPTED` (DEC-718's version row says the Contract is ACCEPTED). Not part of this change.
  The apply round leaves it as it is, unless the owner says otherwise.
- **F-5. P-W2-11 is not on record here.** The package that holds the validator's Wave 2 form is named by this
  ticket's brief and by the acceptance tests' README. It is not found in `docs/plan/WAVE_2_WBS.md` or in the register
  at this base.

## 11. The route from here (CAP-33)

1. **Independent review** of this CIT-P by a fresh, read-only independent auditor (CAP-33.d, CAP-47.b).
2. **The owner's approval** (Q-14), with answers to Questions A–E. The owner commits the approval entry with
   `Role: owner` (DEC-724).
3. **Versioned promotion:** W2-49 applies the approved text to `contract.yaml` and `CONTRACT_v4.md` as version 4.2.
   The orchestrator regenerates the capability records (§8).
4. **The CIT-E** (`docs/changes/W2-49-CIT-E.md`) records what was done, and either that it matches this CIT-P or each
   difference.

Order: W2-49 runs in layer 2, after W2-01, which goes first and alone (DEC-721). The copy path waits on it: W2-49 →
W2-16 → W2-18 → W2-23 → W2-27 (WBS §3).
