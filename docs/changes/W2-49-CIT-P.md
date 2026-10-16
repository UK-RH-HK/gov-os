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
review_round: 'reviewed at 9dd15777 by a fresh, read-only independent auditor, recommendation ACCEPT_WITH_FINDINGS; this revision is the one answer round, and section 12 records how each finding was answered'
decisions_carried: [DEC-722]
decisions_read: [DEC-006, DEC-058, DEC-064, DEC-090, DEC-092, DEC-105, DEC-614, DEC-620, DEC-712, DEC-714, DEC-718, DEC-720, DEC-721, DEC-723, DEC-724, DEC-727, DEC-728, DEC-729]
decisions_staged: ['DEC-737 (owner, 2026-10-16; staged for the owner''s commit, not yet in this worktree''s register)']
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
| **Apply now, lite** (the owner's choice, DEC-722) | Contract 4.1 → 4.2. CAP-44.h, the A7 and A10 gates of CAP-44.f and the manifest and file hashes of CAP-43.b move to Wave 2 in a lite form. What stays is kept in Wave 3 (§4). | Cost, itemised in the table below: **one new ticket at most, ≈ 3 to 4 agent days in all (≈ 4.2 under Question H (i), ≈ 2.7 under H (ii)), one owner turnaround on the copy path, and 0 days on the critical path** (under Question I (ii)). The build work is otherwise already in the approved plan: W2-02, W2-16, W2-18, W2-27 to W2-30. |
| **Defer** (record it and continue) | Contract stays 4.1. The lite parts are built by the plan but checked against no Wave 2 item. | Cost: **no new ticket, ≈ 2 agent days saved** (W2-49's apply round and the regeneration), **0 days saved on either path** (W2-16, W2-18 and W2-27 to W2-30 are built anyway), and **one owner package** to revise the approved plan (DEC-729). Exit criterion 6 ("against Contract v4.2's lite CAP-44.h") and exit criterion 7 ("Contract v4.2's lite items") would have nothing to point at. W2-16's KPI `[CAP-43.b lite]` would cite a Wave 3 item, and so would W2-24's. The verdicts of W2-28 and W2-30 would rest on no Wave 2 condition, or Track B's verdict would wait for Wave 3. |
| **Re-baseline** (reopen and re-plan) | Reopen CAP-44, CAP-43, CAP-47 and CAP-02 whole. Re-plan adoption and releases across Waves 2 and 3, and retire the work this invalidates. | Cost: the largest. **At least four new tickets** (A9, A11, the role separation of CAP-47.a, the signed tag of CAP-02.c with an owner signing key, whose package Q-5 DEC-722 item 4 dropped), plus CAP-44.g, CAP-44.i and the rest of CAP-43.b if CAP-43 and CAP-44 reopen whole. No source sizes them. At §4's rate for a FULL engineer ticket (≈ 2 to 3 days each) the four alone are **≥ 8 to 12 agent days, more with the rest, much of it on the copy path** (W2-49 → W2-16 → W2-18 → W2-23 → W2-27 → W2-28), and a re-plan for the owner. DEC-722 chose lite, so nothing in the evidence calls for it. |

**The apply-now cost, item by item** (durations by WBS §4's method: ≈ 1 day plus 1 day per 150 est. LOC, plus half a
day for FULL; integration 1 day; an owner turnaround ≈ 1 day on each package a path waits for. These are estimates for
the comparison, not plan figures.)

| Item | Tickets | Agent days | On which path |
|---|---|---|---|
| This CIT-P, its independent review, the apply round on the two Contract files, the CIT-E | W2-49 (in the plan) | ≈ 1 (STANDARD, 0 est. LOC) | the copy path (W2-16 needs W2-49 first) |
| The owner's approval (Q-14), with answers to Questions A–J | — | — (≈ 1 day of owner turnaround) | the copy path |
| Regenerating the 273 capability records, with no generator in the repository (a script under DEC-614's terms), and the source-map rows (§8) | none new: the orchestrator | ≈ 1 (integration) | neither |
| Building the lite A7 and A10 stage records (finding F-1) | +1 under Question H (i), or none under H (ii) | ≈ 2.2 under H (i) (FULL, an assumed ≈ 100 est. LOC, a figure of this CIT-P's for the cost only); ≈ +0.7 to W2-23 under H (ii) | H (i): neither, if it closes before W2-23 starts; H (ii): the copy path |
| The plan validator's Wave 2 form (P-W2-11) | not set here | not sized by any source | — (the validator is red at the base already, whatever v4.2 does: §8) |
| Answers to Questions F, G, I and J | none | ≈ 0: text in CAP-44.h, a list edit, a reading of W2-02's KPI | neither under I (ii); the critical path under I (i), if Q-14 comes late |

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
conditions a lite verdict checks and does not check are these (the rows marked Question G are open for the owner):

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
| `gov doctor` green (exit 0), not only its MATCH line | W2-27 and W2-29 KPIs; exit criterion 3 ("on EXAMIN"); CAP-54's acceptance ("passes `gov doctor` at the minimal level", W1) | W1 | **Question G** |
| `gov check` with no RED family | W2-27 and W2-29 KPIs | — (a plan check, no Contract item) | **Question G** |
| One ticket closed by `gov close` at exit 0 with the repository's own test command | W2-27 and W2-29 KPIs; exit criterion 1's close form | — (a plan check) | **Question G** |
| The HEALTHY definition of a repository (authority, freshness, retrieval thresholds, readiness, task states, suite green, derived memory rebuildable, …) | CAP-48.b | W3 | does not check: CAP-48 is W3 and DEC-722 does not bring it forward |
| A9 new knowledge fabric | CAP-44.f | W3 | does not check |
| A11 full audit | CAP-44.f | W3 | does not check |
| A7 and A10 beyond their lite form | CAP-44.f; CAP-47.a | W3 | does not check |
| Remediation, finding states, human gates during adoption | CAP-44.g | W3 | does not check |
| Interrupted-session recovery and freeze during adoption | CAP-44.i | W3 | does not check |
| Signed release tag, verified by `git tag -v` | CAP-02.c; DEC-722 item 2 | W3 | does not check |

**Who gives it.** A fresh independent auditor (W2-28 on the copy, W2-30 on the real repository: WBS §2 and exit
criterion 6). The Wave 1 Independent Auditor role exists (CAP-47.b, W1). The full adoption and audit role separation
(CAP-47.a) stays in Wave 3.

**What yields each verdict (Question F, §7).** The table above lists the conditions behind ADOPTED_HEALTHY. No source
says what yields ADOPTED_WITH_ACCEPTED_EXCEPTIONS rather than NOT_ADOPTED_HEALTHY, which conditions may be excepted, or
who accepts an exception. What the sources do fix:
- remediation, finding states and human gates during adoption stay in Wave 3 (CAP-44.g);
- the owner is the final authority, and agents hold no approval authority (MR-6; Charter v5, "Authority");
- anything short of ADOPTED_HEALTHY on the copy goes to the owner before W2-29 (the W2-28 card);
- exit criterion 6 needs ADOPTED_HEALTHY on the real repository (W2-30).

So the auditor does not decide what an accepted exception is. The rule for each verdict is put to the owner as
Question F.

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
  - the derived state rebuilt from git (CAP-20, W1);
  - the zero-result canary of each index (CAP-55, W1: "canaries per index"; a canary miss yields FACET_UNAVAILABLE).

  It leaves A10's own stage record. The source map names A10's role "Role F — Independent Memory Verifier/Test Author",
  carried by "CAP-44 covers A10 + CAP-47 … + CAP-49" (`SOURCE_MAP.csv` row 237), and the stage itself "CAP-44 covers
  A10 (W3, with CAP-47) + CAP-55 canaries" (row 283). CAP-55 is W1 and delivered, so the lite A10 includes its canaries.
  - *This reading is the CIT-P's, for the owner's approval.* A10 verifies memory, and with A9 in Wave 3 the memory that
    exists after a Wave 2 adoption is A8's result and the rebuilt index.
  - **What of A10 stays for Wave 3:** verification of the A9 knowledge fabric (A9 is W3), the qualification run's
    memory checks (CAP-49, W3), and the separate role under CAP-47.a.
  - **Role F's "Test Author" part stays for Wave 3:** a separate author of memory tests is part of the role separation
    of CAP-47.a (W3), which row 237 names as its carrier. The lite A10 is a check by the Wave 1 Independent Auditor and
    writes no tests of its own; the ticket that builds the A7 and A10 stage records gets its acceptance tests from the
    independent test designer (MR-3), as every ticket does.
- **A9 and A11 stay in Wave 3 in full** (DEC-722 names only A7 and A10; DEC-090; the W2-49 card).

### 3.3 CAP-43.b, lite: the manifest and the file hashes

CAP-43.b lists the release contents: "semantic version, manifest, file hashes, supported migrations, schema versions,
CLI/runtime versions, adapter/capability versions, release notes, affected indexes, required human decisions, rollback
procedure" (Contract v3 S2; Framework v4.1.2 §75D).

CAP-43.b, lite, holds **the manifest and the file hashes**, and nothing else. A Wave 2 release is pinned and
hash-verified, not signed. Sources: DEC-722 item 1 ("release contents: a manifest and file hashes"), DEC-722 item 2,
and KPI line 2.

**What the lite item adds to Wave 1.** Wave 1 already has a file-hash manifest, on the install side:
- CAP-02.a (W1): "File-hash manifest in framework.lock; gov doctor MATCH/DRIFT";
- CAP-43's acceptance (W1): "`framework.lock` records the template tag, commit and file-hash manifest".

Both are the **lock** a repository keeps of what it installed. CAP-43.b is "Release contents": what a **release**
holds. The lite CAP-43.b is therefore the release's own manifest and file hashes, built by the release step and shipped
with the release, against which an install, an update and `gov doctor` verify (W2-16's KPIs: `gov release <version>`
builds the manifest; a release whose files or manifest do not match their hashes is refused by `gov install`,
`gov update` and `gov doctor`; `framework.lock` records the release version and manifest hash). The Wave 1 lock does
not deliver it, and an exit auditor (W2-47) should not read it as delivered in Wave 1. The proposed item text (§6.1)
says so.

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
| **W2-02** record types (product-spec) | Gains the source for its adoption-verdict type: "the three CAP-44.h verdicts and the conditions behind them, in the lite form Contract v4.2 states". Depends on v4.2's CAP-44.h text for those conditions. §1's table gives W2-02 no dependency on W2-49, its ticket file depends only on W2-01, and it is `in_progress` (finding F-2; Question I). |
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
  both ways"). It gains three Wave 2 covers items: CAP-44.f, CAP-44.h and CAP-43.b, so 17 become 20 (two, so 19, under
  Question A (a3)).
  - With the split form recommended in §7 (Question A), each of these has one wave. The two-way check can then read
    `wave` alone.
  - The check itself needs the plan validator's Wave 2 form, which is with the owner (P-W2-11; KPI line 3). No test is
    written for it yet (`tests/acceptance/W2-49/README.md`).
  - Finding F-1 (§10): no ticket delivers the lite A7 and A10 gates (Question H).

### 5.3 The list row W2-I017

W2-I017, "Independent adoption gates A7, A10, A11 and the final verdict (Wave 3)", closes when "A7, A10 and A11 run, and
an adoption verdict is issued" (`WAVE_2_LIST.md`). Its triage: "A7, A10 and the verdict come into Wave 2, lite, by
Contract v4.2 (DEC-722); A11 stays in Wave 3."

After v4.2, A7, A10 and the verdict come into Wave 2, lite (CAP-44.f, CAP-44.h). They are delivered when W2-27 to
W2-30 have run. A11, and A7 and A10 in full, stay in Wave 3. The orchestrator keeps the list (DEC-718; WBS §0 rule 10).

**The row's state is not settled by a source.** WBS rule 10 marks a row a ticket closes as closed with its commit, and
exit criterion 10 allows three states: closed, carried to Wave 3 or the backlog with its reason, or an exception the
owner accepts. No rule defines a row "marked in part". The row's own close criterion ("A7, A10 and A11 run") cannot be
met in Wave 2, because A11 stays in Wave 3 (DEC-722). W2-49 claims the row in its `list_rows`, but nothing runs at
W2-49's close: the lite delivery is the gate-building ticket (Question H) and W2-27 to W2-30. The owner moves rows
(Q-12). Who closes the row, and in which state, is Question J (§7).

### 5.4 Other specification text

| Text | Impact |
|---|---|
| CAP-44 `wave_note` and `provider` | Today they say "the independent gates A7, A10, A11 and the final verdict are W3 with CAP-47 (DEC-090)" and "W3: A7/A10/A11 gates + verdict". Both are reworded (§6). CAP-44's own `wave` stays W3, because its acceptance needs A0–A11. |
| CAP-47 `wave_note` | Says "full independent adoption/audit roles and the A7, A10, A11 gates W3". Reworded so that the lite A7 and A10 are W2 (§6). CAP-47's `wave` stays W3. |
| CAP-43 `wave_note`, `sources` | DEC-722 is added, and a note says that release contents of CAP-43.d built before Wave 3 are ahead of their wave, without naming a ticket, so the Contract carries no plan content that would go stale (§6). CAP-43's `wave` stays W1. |
| CAP-45.a (W2, W2-17) | Its text includes "authenticated source (signed tag)". The signed tag stays W3 (CAP-02.c, DEC-722 item 2), and W2-17's KPIs verify manifest and file hashes only. Question D, §7. |
| Contract §1 Counts | Unchanged: the table counts capabilities, and none changes wave. |
| DEC-090 | It says the gates A7, A10 and A11 are Wave 3 and "the verdict is issued from Wave 3". DEC-722 changes that in part, but does not name DEC-090. No ACCEPTED entry is edited. Question E, §7. |
| Charter v5 | **No change.** The precedence is Charter v5 → Contract v4 (CAP-01). The Charter keeps Release 1 as "a signed `v1.0.0` tag" (§1), which CAP-02.c in Wave 3 respects. Finding F-3 (§10) concerns a Charter line this change sits beside but does not touch. |

### 5.5 Tests, code and radius (CAP-33's acceptance)

CAP-33's acceptance asks a CIT-P to list "the affected specs, decisions, tickets, tests and code … with a radius".
Specifications, decisions and tickets are in §5.1 to §5.4 and §8. Computed impact (`gov impact`, CAP-33.b and
CAP-33.g) is W2-37's and not built at this base, so the lists below were made by hand, by a search of `tests/` and
`src/` for readers of the two Contract files.

- **Tests.**
  - `tests/acceptance/W2-49/` (76 tests): the 24 CIT-P tests pass on this text; the 42 Contract tests and the 10
    CIT-E tests stay red until the owner approves and the change is applied.
  - `tests/acceptance/W1-48/` reads `contract.yaml` for CAP-61's provider line only, which v4.2 does not touch.
    `tests/acceptance/W1-41/` names the path as a string in a fixture and reads nothing from it.
  - No other Wave 2 acceptance tests exist at this base. The tests of W2-02, W2-16, W2-27 to W2-30 and of the ticket
    of Question H will be written against v4.2 when those tickets are taken up (MR-3).
- **Code.** This change edits no code. Code that will read the lite items, all in tickets not yet built here: W2-02's
  schemas (the verdict type, Question I), W2-16's `src/gov/release/**`, W2-18's `src/gov/install/**`, and
  `src/gov/adopt/**` and the adopt skill for the A7 and A10 stage records (Question H). The plan validator
  `docs/plan/tools/validate_s1.py` reads the Contract (§8).
- **Radius.** Three covers items change wave (CAP-44.f, CAP-44.h, CAP-43.b) and three are added (two under A (a3));
  three capability wave notes are reworded (CAP-43, CAP-44, CAP-47); no capability changes wave. Eight tickets depend on
  or cite the moved ids, and two more name the lite items (W2-46, W2-47; §5.1), two exit criteria (6 and 7), one list row (W2-I017), the 273 derived capability records,
  eight source-map rows and one validator (§8). That is a specification-only change with a bounded reach, which fits the
  ticket's STANDARD profile.

## 6. The proposed v4.2 text

This text is proposed, and applied only after the owner's approval. It uses the split form recommended in Question A,
with CAP-43.b lite as in Question B, and writes CAP-44.h with the recommended answers to Questions F and G (marked in a
comment). If the owner answers any question differently, the apply step follows the answer, and the CIT-E lists the
difference.

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
    DEC-722); release contents of CAP-43.d built before W3 are delivered ahead of that item''s wave'
  sources: [ … as 4.1 …, DEC-722]
  covers:
  - id: CAP-43.b
    item: 'Release contents, lite: the release''s own manifest and file hashes, built with the release (the lock on the
      install side is CAP-02.a, W1); a release is pinned and hash-verified, not signed'
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
      reviewed at A5; A10 checks the A8 legacy memory extraction and retirement, the derived state rebuilt from git and
      the canary of each index (CAP-55)'
    source: Adoption Protocol v3.0 §12, §15; Distribution Protocol v1.2 §10; DEC-722
    wave: W2
  - id: CAP-44.h            # written with the recommended answers F (i) and G (i)
    item: 'Adoption verdict, lite: ADOPTED_HEALTHY / ADOPTED_WITH_ACCEPTED_EXCEPTIONS / NOT_ADOPTED_HEALTHY from a fresh
      Independent Auditor against the lite conditions: A0–A6 and A8 with their stage records and the A5 review, the native
      layout kept, the lite A7 and A10 gates passed, the pinned, hash-verified release (gov doctor MATCH), gov doctor
      green, gov check with no RED family, and one ticket closed by gov close at exit 0 with the repository''s own test
      command; ADOPTED_HEALTHY when every lite condition is met; ADOPTED_WITH_ACCEPTED_EXCEPTIONS when each condition not
      met is accepted by name in an owner decision (Role: owner); otherwise NOT_ADOPTED_HEALTHY; the auditor accepts no
      exception; the verdict record names itself lite and names the conditions it does not check'
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
ticket that delivers lite A7 and A10 (CAP-44.f, finding F-1, Question H), and `[W2-30]` (CAP-44.h) only if the owner's answer to
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
  - `` `CAP-43.b` [W2] Release contents, lite: the release's own manifest and file hashes, built with the release (the lock on the install side is CAP-02.a, W1); a release is pinned and hash-verified, not signed — Contract v3 S2; Framework v4.1.2 §75D; DEC-722 ``
  - `` `CAP-43.d` [W3] Release contents beyond the lite manifest and file hashes of CAP-43.b: … — Contract v3 S2; Framework v4.1.2 §75D; DEC-722 ``
  - `` `CAP-44.f` [W2] A7 independent migration verification and A10 independent memory verification, lite: … — Adoption Protocol v3.0 §12, §15; Distribution Protocol v1.2 §10; DEC-722 ``
  - `` `CAP-44.h` [W2] Adoption verdict, lite: ADOPTED_HEALTHY / ADOPTED_WITH_ACCEPTED_EXCEPTIONS / NOT_ADOPTED_HEALTHY … — Adoption Protocol v3.0 §20; Distribution Protocol v1.2 §18; DEC-006; DEC-722 ``
  - `` `CAP-44.k` [W3] A9 new knowledge fabric; A11 full audit; … — Adoption Protocol v3.0 §12, §14–§16; Distribution Protocol v1.2 §10; DEC-722 ``
  - `` `CAP-44.l` [W3] Final verdict … with the ten ADOPTED_HEALTHY conditions, after A0–A11 — Adoption Protocol v3.0 §20; Distribution Protocol v1.2 §18; DEC-006; DEC-722 ``

  The `…` stands for the full YAML text.
- **§1 Counts:** unchanged.

### 6.3 Version

The version becomes 4.2. The file names and the id `CONTRACT-v4` are unchanged, as at 4.1. Covers items by wave go
from W1 149 / W2 17 / W3 38 / NONE 7 to W1 149 / W2 20 / W3 38 / NONE 7 (211 → 214). Under Question A (a3) they go to
W1 149 / W2 19 / W3 38 / NONE 7 (211 → 213).

## 7. Questions for the owner (with the approval of this CIT-P, Q-14)

**A. The form of a split item.** CAP-44.f (A7 and A10 move, A9 and A11 stay) and CAP-43.b (manifest and file hashes
move, the rest stays) each straddle two waves. So does CAP-44.h (the lite verdict moves, the verdict with the ten
conditions stays). No source fixes the form.

| Option | For exit criterion 7 (each lite item delivered by a closed ticket and cited by a test, checked both ways) | Cost |
|---|---|---|
| **(a1) Split; the original id carries the lite W2 part, a new id the W3 rest** (recommended) | Each id has one wave, so the validator's two-way check reads `wave` and nothing else. The ids the plan and five ticket files already cite in the lite sense keep pointing at the W2 item: W2-02, W2-16, W2-24, W2-28 and W2-30 cite `CAP-43.b lite` or `CAP-44.h (lite)`. | Three new ids (CAP-43.d, CAP-44.k, CAP-44.l) and three new generated records. The three original ids have narrower text in 4.2 than in 4.1, and the 4.1 meaning stays in the change log and in git (CAP-33.e). No ticket or card changes. |
| (a2) Split; the original id keeps the W3 meaning, new ids for the lite parts | The same one-wave-per-id benefit. | The five ticket files and the WBS cards re-cite new ids, and the approved plan (DEC-729) is the owner's to change. |
| (a3) The lite A7 and A10 become conditions inside the lite CAP-44.h; CAP-44.f stays W3 whole, with a note that A7 and A10 run lite in W2 as conditions of CAP-44.h (DEC-722); CAP-44.h and CAP-43.b split as in (a1) | It matches DEC-722's title ("two Wave 3 items") and exit criterion 7's grouping ("CAP-44.h with A7 and A10, CAP-43.b"). The validator sees two lite items, each with one wave; A7 and A10 are checked through CAP-44.h, not by an id of their own. The acceptance tests' A7 and A10 placement tests are met by CAP-44.h's text alone (the reviewer's check). | Two new ids (CAP-43.d, CAP-44.l), not three; CAP-44.f's text and record are unchanged but for the note; W2 items 17 → 19, not 20 (§6.3). No ticket cites CAP-44.f but W2-49, so nothing is re-cited. The A7 and A10 stage records still have to be built (Question H): their ticket then closes CAP-44.h's A7 and A10 conditions, not CAP-44.f. The W2-49 card's KPI names "the A7 and A10 gates of CAP-44.f, lite": the CIT-P still says what each gate checks (§3.2). The W2-47 exit audit gives the gates no finding row of their own. |
| (b) Move the item whole to W2, with a note on what stays | A validator reading `wave` would require A9, A11 and the nine other release contents in Wave 2. It must parse free-text notes to tell them apart, which is fragile. | Smallest text change; the largest validator change. |
| (c) Keep it in W3, with a note on what moves | The validator sees no W2 item, so the lite items are invisible to the two-way check unless it parses notes. | Same as (b). |

*Recommendation:* (a1). *Confidence:* medium. Nothing a source says decides between (a1), (a2) and (a3). (a1) is
cheaper than (a2) and matches every existing citation. Against (a3), (a1) gives each lite gate an id of its own, so the
validator's two-way check and the W2-47 exit audit (exit criterion 11, "every … Contract v4.2 lite item") see A7 and
A10 by id, as the W2-49 card's KPI names them. (a3) follows the owner's own grouping more closely and needs one id
fewer; if the owner prefers it, the apply step drops CAP-44.k, keeps CAP-44.f as at 4.1 with the note, and moves §6.1's
CAP-44.f text into CAP-44.h. DEC-092 ("nothing is dropped by the compression") is why the W3 rest gets a covers item of
its own, rather than living only in a wave note.

**B. What CAP-43.b, lite, holds.** W2-16's manifest holds the semantic version and the commit, every shipped file with
its sha256, the wheel hash, the CLI version, the schema versions, the release notes, and the manifest's own hash.

| Part W2-16 builds | Where it sits in the Contract |
|---|---|
| The manifest; every shipped file with its sha256 | The lite CAP-43.b: "the manifest and file hashes" |
| The wheel hash; the manifest's own hash | This CIT-P reads both as file hashes within the lite manifest, for the owner's approval: the wheel is a shipped file, and the manifest's hash is the manifest's own integrity |
| The commit | Already in CAP-43's W1 acceptance ("template tag, commit and file-hash manifest") |
| The semantic version, CLI version, schema versions, release notes | The W3 rest of CAP-43.b (CAP-43.d under A (a1)) |
| The vendored skills' licence and version in the release (W2-16's fifth KPI, list rows W2-L002, W2-L014) | This CIT-P reads the version part as "adapter/capability versions", in the W3 rest (CAP-43.d), delivered ahead of its wave. The licence is no release content CAP-43.b lists; it sits with the list rows that W2-16 closes, not with CAP-43.b. For the owner's approval. |

- *Options:*
  - (i) Lite CAP-43.b is only the manifest and the file hashes. W2-16's further content is recorded as delivered ahead
    of its wave, in CAP-43's wave note, which names the contents' item (CAP-43.d) and no ticket.
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
- **DEC-006's status.** The register still marks DEC-006 PROPOSED. CAP-54.a is Contract text sourced to it, and DEC-090,
  which is ACCEPTED, refines DEC-006 and keeps the three verdicts. The reasoning below does not change, but the owner
  may wish to settle DEC-006's status in the same entry.
- *Options:*
  - (i) The owner's approval entry for Q-14 records that it amends DEC-090 in part. The lite verdict record names itself
    lite and the conditions it does not check (§6.1). CAP-54.a stays as written, because its target is the W3 verdict
    (CAP-44.l).
  - (ii) Leave both texts as they are, and read DEC-722 as overriding.
- *Recommendation:* (i). No ACCEPTED entry is edited, so the amendment is the owner's new entry. Its wording is the
  owner's.
- *Confidence:* medium.

**F. What yields each of the three lite verdicts, and who accepts an exception** (§3.1; review MAJOR-1).
- *Why it is the owner's.* No source says what yields ADOPTED_WITH_ACCEPTED_EXCEPTIONS rather than NOT_ADOPTED_HEALTHY.
  Remediation, finding states and human gates stay in Wave 3 (CAP-44.g). The owner is the final authority and agents
  hold no approval authority (MR-6; Charter v5, "Authority"). W2-02 must type "the conditions behind them", and W2-28
  and W2-30 must choose among the three. Without a rule, the auditor in effect decides what an accepted exception is.
- *A precedent the owner set:* at the Wave 1 exit the auditor's FAIL became PASS WITH ACCEPTED EXCEPTIONS by one owner
  decision, committed with `Role: owner`, that named each exception with what closes it (DEC-718 item 1).
- *Options:*
  - (i) The auditor reports each lite condition as met or not met. **ADOPTED_HEALTHY:** every lite condition is met.
    **ADOPTED_WITH_ACCEPTED_EXCEPTIONS:** one or more are not met, and the owner has accepted each by name, with what
    closes it, in an owner decision committed with `Role: owner` (DEC-724). **NOT_ADOPTED_HEALTHY:** any condition not
    met and not so accepted. The auditor accepts nothing; until the owner answers, the verdict is NOT_ADOPTED_HEALTHY
    with the unmet conditions listed. Any lite condition may be put to the owner.
  - (ii) As (i), but some conditions can never be excepted, so failing them is always NOT_ADOPTED_HEALTHY: the A0
    safety baseline, the A5 review before any move, the A6 rollback of a failed batch, and the pinned, hash-verified
    release (the safety-critical work of DEC-727 and WBS rule 7).
  - (iii) No rule in the Contract: W2-28 and W2-30 judge, and escalate.
- *Cost:* (i) and (ii): one clause in CAP-44.h's lite text (§6.1 shows (i)); W2-02's verdict type gains a state per
  condition (met, not met, accepted with the owner entry's id); no ticket and no day. (iii): nothing now, an open
  question at each verdict, and the auditor deciding an owner matter.
- *Note:* exit criterion 6 and the W2-30 card ask for ADOPTED_HEALTHY on the real repository. Under every option an
  ADOPTED_WITH_ACCEPTED_EXCEPTIONS there is a named failure of exit criterion 6, unless the owner accepts that too.
- *Recommendation:* (i). The owner stays the only one who accepts an exception, and stays free to refuse one case by
  case, which makes (ii)'s fixed list unnecessary; if the owner wants the safety conditions fixed in advance, (ii).
- *Confidence:* medium-high.

**G. Which operational checks are lite healthy conditions** (§3.1; review MAJOR-2).
- *Why it is the owner's.* The proposed conditions held one operational check, `gov doctor` MATCH for the pinned
  lock. The plan's own adoption steps ask for more on EXAMIN: `gov doctor` and `gov check` green, and a first ticket
  closed by `gov close` at exit 0 (W2-27, W2-29); exit criterion 3 asks for `gov doctor` green on EXAMIN; CAP-54's
  acceptance asks for "passes `gov doctor` at the minimal level". The healthy-repository definition of CAP-48.b is W3.
  Without them, ADOPTED_HEALTHY could be issued with `gov check` red, and the owner's go for the real repository (Q-9)
  rests on W2-28's verdict.
- *Options:*
  - (i) Three lite conditions are added: `gov doctor` green (exit 0); `gov check` with no RED family; one ticket closed
    by `gov close` at exit 0 with the repository's own test command. CAP-48.b stays W3 and is named in the verdict
    record as not checked.
  - (ii) MATCH stays the only operational condition. The verdict record names `gov doctor` green, `gov check` and the
    first close as not checked by the verdict, with the reason that W2-27's and W2-29's KPIs and exit criterion 3 check
    them.
  - (iii) As (i), plus the parts of CAP-48.b a Wave 2 command can show (suite green, derived memory rebuildable).
- *Cost:* (i): three clauses in CAP-44.h's lite text (§6.1 shows them); W2-28 and W2-30 read three results W2-27 and
  W2-29 produce anyway; no ticket, no day. (ii): none; the verdict can be healthy while `gov check` is red. (iii): moves
  part of a W3 item DEC-722 does not name, so a further CIT-P line and approval.
- *Recommendation:* (i). It makes the verdict agree with the plan's own steps and with exit criterion 3, and moves
  nothing DEC-722 does not cover.
- *Confidence:* medium-high.

**H. Which ticket builds the lite A7 and A10 stage records** (finding F-1, §10; review MAJOR-3).
- *Why it is the owner's.* No ticket's KPI adds A7 or A10 stage records to `gov adopt` or to the adopt skill. W2-27 is
  an orchestrator integration ticket with 0 est. LOC; W2-23 holds `src/gov/adopt/**` but its KPIs do not name A7 or
  A10; no ticket but W2-49 cites CAP-44.f; the list row W2-I017 names the role "engineer". Exit criterion 7 needs each
  lite item "delivered by a closed ticket and cited by an acceptance test". New work that breaks an exit criterion goes
  to the owner as a package (WBS §6).
- *Options:*
  - (i) **A new ticket** (its W2 id the orchestrator's to give), FULL, engineer, with a product-spec worker for the
    adopt skill as W2-21 pairs them; the independent test designer first (MR-3). It starts after W2-49's apply, builds
    the A7 and A10 stage records and their evidence in `gov adopt` and the adopt skill, and closes CAP-44.f (lite).
  - (ii) **W2-23 grows:** its KPIs gain the A7 and A10 stage records and its paths the adopt skill.
  - (iii) **No code:** W2-27 and W2-29 run the A7 and A10 checks as auditor sessions and file the stage records by hand.
- *Cost* (by WBS §4's method, on an assumed ≈ 100 est. LOC, a figure of this CIT-P's for the cost only):
  - (i): +1 ticket, ≈ 2.2 agent days. It runs beside W2-16 and W2-18 and can close at ≈ day 6, about two days before
    W2-23 starts at ≈ day 8 (owner waits not counted, as in WBS §3), so 0 days on the copy path when a slot is free. It shares `src/gov/adopt/**` with W2-23, so if it slips,
    W2-23 waits.
  - (ii): no new ticket, ≈ +0.7 day on the copy path (W2-23 is on it), and a change to an approved card (DEC-729).
  - (iii): no build; but no ticket with an acceptance test delivers the lite gates, so exit criterion 7 fails for them
    unless the owner accepts that exception.
- *Under A (a3)* the build is the same; the ticket then closes CAP-44.h's A7 and A10 conditions.
- *Recommendation:* (i). It keeps the copy path as planned and gives the lite gates the closed ticket and acceptance
  test exit criterion 7 asks for.
- *Confidence:* medium.

**I. W2-02's order against W2-49** (finding F-2, §10; review MAJOR-3).
- *Why it is the owner's.* W2-02 is `in_progress`, depends only on W2-01, and is on the critical path (W2-01 → W2-02 →
  W2-03 → …). Its KPI types the verdict "in the lite form Contract v4.2 states", which exists only after Q-14 and the
  apply round. W2-02 can close before then. The order of tickets in the approved plan is the owner's (DEC-729).
- *Options:*
  - (i) W2-02 closes after W2-49's CIT-E: a close-order dependency, the form DEC-737 (staged) gives W2-49's own
    dependency on W2-01.
  - (ii) W2-02 types the verdict with its three values, which DEC-722 item 1 and DEC-090 already fix, and with a list of
    named conditions, each with its source item and its state (met, not met, accepted by an owner entry). It closes on
    its own. The v4.2 conditions are then data the verdict record carries (W2-28, W2-30), not schema: the KPI's "in the
    lite form Contract v4.2 states" is read as that form.
  - (iii) The verdict type leaves W2-02 for the ticket of Question H (or another after W2-49).
- *Cost:* (i): 0 days if Q-14 is answered and applied before W2-02 is otherwise ready to close; each day of waiting
  after that is a day on the critical path. (ii): 0 days; a reading of W2-02's KPI for the owner to approve; later
  answers to C, F and G change data, not the schema. (iii): 0 days on the critical path; a KPI moves between approved
  cards (DEC-729).
- *Recommendation:* (ii). It keeps Q-14 off the critical path, and the type then holds whatever the owner answers to C,
  F and G.
- *Confidence:* medium.

**J. Who closes the list row W2-I017, and in which state** (§5.3; review MINOR-7).
- *Why it is the owner's.* The row's close criterion ("A7, A10 and A11 run, and an adoption verdict is issued") cannot
  be met in Wave 2, because A11 stays W3 (DEC-722). The triage gives the row to W2-49, and W2-49 claims it in its
  `list_rows`, but nothing runs at W2-49's close. Exit criterion 10 allows closed, carried with its reason, or an
  exception the owner accepts. The owner moves rows (Q-12); the orchestrator keeps the list (DEC-718).
- *Options:*
  - (i) At W2-30's close, the orchestrator records the row as carried to Wave 3, with the reason "A11, and A7, A10 and
    the verdict in full, stay in Wave 3 (DEC-722); the lite A7, A10 and verdict delivered by" the commits of the ticket
    of Question H, W2-28 and W2-30.
  - (ii) The row closes at W2-30's close for the lite part, and a new row (DEC-718: new items go into the list) carries
    A11 and the full gates to Wave 3 with its reason.
  - (iii) W2-49's close closes the row.
- *Cost:* (i) and (ii): one list edit by the orchestrator at W2-30's close; W2-49's close then leaves the row open,
  which the owner's answer records against W2-49's `list_rows`. (iii): none, but the row would be closed at a commit
  where its close criterion is false.
- *Recommendation:* (i). One row stays in one state that exit criterion 10 allows, and the reason names the lite
  delivery.
- *Confidence:* medium.

## 8. Other files the v4.2 change touches

| File | Change | Who changes it | In W2-49's `allowed_paths`? | What the owner's approval needs to cover |
|---|---|---|---|---|
| `docs/contract/contract.yaml`, `docs/contract/CONTRACT_v4.md` | The v4.2 text (§6) | W2-49, the apply round | yes | The text, and the answers to A–J |
| `docs/changes/W2-49-CIT-E.md` | What was done, and each difference from this CIT-P | W2-49, the apply round | yes | — |
| `docs/contract/capabilities/CAP-43.b.md`, `CAP-44.f.md`, `CAP-44.h.md` | Rewritten: new title, item and wave | The orchestrator, by the script of DEC-614 (the records were made in `d8534afe` under DEC-614 and DEC-620); no generator was found in `src/`, `docs/` or `tests/` | no | A regeneration, in its own commit, from the approved `contract.yaml` |
| `CAP-43.d.md`, `CAP-44.k.md`, `CAP-44.l.md` (new, under A (a1)) | New records for the split | Same | no | Same |
| `CAP-43.md`, `CAP-44.md` | Their "Covers:" lists gain the new ids | Same | no | Same |
| The other 268 records under `docs/contract/capabilities/` | Each says "Contract v4, version 4.1" in its body. All 273 do today. | Same | no | Whether every record is regenerated to cite 4.2 (recommended: they are DERIVED), or only the changed ones |
| `docs/plan/tools/validate_s1.py` (the Wave 1 plan validator; read here, never run) | **It is already red at the base, whatever v4.2 does** (read from the code, not run): line 72 expects exactly W1-01 to W1-50 among the work-breakdown ids of all `.tickets/*.md`, and at the base `.tickets/` holds 102 files, 50 of them Wave 2 tickets; its "every W1 ticket …" checks also run over the Wave 2 tickets. **On 4.2** its check "Contract is version 4.1 in both files, with a change log" (lines 236–237: `['4.0', '4.1']`, `\| 4.1 \| 2026-10-03 \|`) fails too. Its yaml/markdown agreement check and its id form (`CAP-nn.<letter>`) hold for the text of §6. **Its inputs outside the tree:** by default it reads `~/gov-os-workbench` (line 20, `GOV_OS_WORKBENCH`, read at lines 59, 158, 207 and 216), which DEC-723 forbids agents to list or search, and it reads an original under `docs/source/` through `git show` (lines 192–193), which `docs/SOURCES.md` excludes from agents. So no agent may run it as it stands. No test and no `gov check` family was found that runs it (a search of `src/`, `tests/`, `template/`). | Whoever the owner's answer to P-W2-11 names; it is in no Wave 2 ticket's paths | no | The validator's Wave 2 form under P-W2-11, which must also stop reading the workbench and `docs/source/` by default before an agent can run it. An accepted red would cover the whole validator, not only the version check. KPI line 3 and the failure KPI wait for P-W2-11 too (F-5). |
| `docs/contract/SOURCE_MAP.csv` | Eight rows state that the moved parts are W3: rows 235 (Role D, A7) and 237 (Role F, A10); rows 248 (Adoption Protocol §12, A7), 251 (§15, A10) and 256 (§20, the verdict); rows 280 (Distribution Protocol Stage A7) and 283 (Stage A10); row 292 (Distribution Protocol §18, the verdict set). Rows 252 (§16, A11) and 282 (Stage A9) say W3 and stay right, since A9 and A11 do not move. | The orchestrator, or W2-49 if the approval adds the path | no | Whether these eight rows follow 4.2. The S2 change left the source map alone because it maps the originals, but these rows also state waves. |
| `docs/plan/WAVE_2_LIST.md` (row W2-I017) | Its state, as the owner answers Question J (§5.3) | The orchestrator (DEC-718; WBS §0 rule 10), at W2-30's close under J (i) or (ii) | no | Question J |
| `.tickets/` and the WBS cards of W2-02, W2-23 and the new ticket | Only if the owner answers H (i) or (ii), I (i) or (iii), or J so that a ticket changes | The orchestrator, after the owner's answer (DEC-729: the plan is the owner's) | no | Questions H, I and J |
| `docs/DECISION_REGISTER.md` | The owner's entry for Q-14, with the answers to A–J, the DEC-090 amendment if E (i), and DEC-006's status if the owner settles it | The owner, with `Role: owner` (DEC-724) | no | The entry itself |
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

**What a revert of the two commits does not undo by itself.**

| Thing changed with or after the approval | How it is reversed |
|---|---|
| The owner's entry for Q-14, the DEC-090 amendment (Question E (i)) and any change to DEC-006's status | Not by a git revert: no ACCEPTED entry is edited. The owner commits a new entry, with `Role: owner` (DEC-724), that withdraws them |
| A CAP-45.a rewording (Question D (ii)) | In the apply commit, so reverted with it |
| The eight source-map rows, if they were changed (§8) | Their own commit is reverted too, by the same route |
| The state of the list row W2-I017 (Question J) | The orchestrator restores the row's state in `WAVE_2_LIST.md`, in a new commit |
| Ticket files or WBS cards changed under Questions H, I or J | The orchestrator restores them after the owner's decision (DEC-729: the plan is the owner's) |
| W2-02's verdict type, if built against the lite text | Under I (ii) the type holds a list of named conditions and survives as it is; under I (i) its conditions part follows the Contract back, by a change ticket |
| The lite A7 and A10 stage records (Question H) | The code stays, delivered ahead of its wave, with no Wave 2 item to cite |

## 10. Findings made while listing the impact

- **F-1. No ticket builds the lite A7 and A10 gates.**
  - W2-27 runs them on the copy, W2-29 on the real repository, and W2-28 and W2-30 judge them. But no implementation
    or skill ticket has a KPI that adds A7 and A10 stage records to `gov adopt` or to the adopt skill.
  - W2-23 holds `src/gov/adopt/**`, but its KPIs do not name A7 or A10. W2-24's fixture adoption stops at A0–A6 and A8.
  - Exit criterion 7 needs each lite item "delivered by a closed ticket and cited by an acceptance test".
  - Also verified by the review: no ticket but W2-49 cites CAP-44.f; W2-27 is an orchestrator integration ticket with
    0 est. LOC; W2-I017's list row names the role "engineer".
  - **Put to the owner as Question H (§7).**
- **F-2. W2-02 reads v4.2's lite text but does not depend on W2-49.** Its KPI types the verdict "in the lite form
  Contract v4.2 states". §1 gives it no dependency, its ticket file depends only on W2-01, it is `in_progress`, and it
  is on the critical path. It can close before Q-14. **Put to the owner as Question I (§7).**
- **F-3. The Charter on adoption before Release 1.** Charter v5 §1 and DEC-064 say "Adoption into product repositories
  starts only after Release 1". The Wave 2 plan adopts EXAMIN's real repository (W2-29) and issues its verdict (W2-30),
  under DEC-712, DEC-714, DEC-718 and DEC-727, all the owner's. This change does not touch the Charter, and no entry
  read here amends that line. The Charter outranks the Contract (CAP-01), so it is named for the owner.
- **F-4. The two Contract files differ in status.** `contract.yaml` says `status: PROPOSED`, and `CONTRACT_v4.md`'s
  frontmatter says `status: ACCEPTED` (DEC-718's version row says the Contract is ACCEPTED). Not part of this change.
  The apply round leaves it as it is, unless the owner says otherwise.
- **F-5. P-W2-11 is not on record here, and the validator it concerns is red and unrunnable by agents.** The package
  that holds the validator's Wave 2 form is named by this ticket's brief and by the acceptance tests' README. It is not
  found in `docs/plan/WAVE_2_WBS.md` or in the register at this base. What P-W2-11 has to answer is larger than the
  version check (§8):
  - the validator is red at the base, before any v4.2 change, because it expects exactly W1-01 to W1-50 among all the
    ticket files and `.tickets/` now holds the Wave 2 tickets too (line 72);
  - by default it reads `~/gov-os-workbench` (DEC-723) and an original under `docs/source/` (excluded by
    `docs/SOURCES.md`), so no agent may run it as it stands;
  - on 4.2 its version check fails as well.
  Exit criterion 7's two-way check and this ticket's KPI line 3 and failure line need that Wave 2 form.

## 11. The route from here (CAP-33)

1. **Independent review** of this CIT-P by a fresh, read-only independent auditor (CAP-33.d, CAP-47.b). Done at
   `9dd15777`, recommendation ACCEPT_WITH_FINDINGS; this revision answers each finding (§12).
2. **The owner's approval** (Q-14), with answers to Questions A–J. The owner commits the approval entry with
   `Role: owner` (DEC-724).
3. **Versioned promotion:** a fresh W2-49 lead applies the approved text to `contract.yaml` and `CONTRACT_v4.md` as
   version 4.2 (DEC-737, staged). The orchestrator regenerates the capability records (§8).
4. **The CIT-E** (`docs/changes/W2-49-CIT-E.md`) records what was done, and either that it matches this CIT-P or each
   difference.

Order: W2-49 runs in layer 2, **beside W2-01, and closes after W2-01's close.** DEC-721's "W2-01 goes first, alone"
binds the closes, not the work, and W2-49's paths do not overlap W2-01's; W2-49's `tk` dependency on W2-01 reads
"closes after W2-01", not "starts after" (DEC-737, the owner's of 2026-10-16, staged for the owner's commit and not yet
in this worktree's register). After the owner approves this CIT-P, a fresh lead applies it; the ticket is then held for
the close order. The copy path waits on W2-49: W2-49 → W2-16 → W2-18 → W2-23 → W2-27 (WBS §3).

## 12. Review and answers

**The review.** A fresh, read-only independent auditor reviewed this CIT-P at `9dd15777`, as CAP-33.d requires before
the owner's approval, and recommended **ACCEPT_WITH_FINDINGS**: three MAJOR findings, eight MINOR, four NOTE. This
revision is the one answer round. Each finding is answered once, below: *changed* where a named source settles it, *put
to the owner* where none does. No finding is left untaken. The acceptance tests are not touched (MR-3).

| Finding | How it was answered | Where |
|---|---|---|
| MAJOR-1: the lite verdict defines one outcome, not three | **Put to the owner** (the rule for each verdict, which conditions may be excepted, the owner as the only one who accepts an exception); the sources that bound it are stated in §3.1, and §6.1's CAP-44.h text shows the recommended answer | Question F; §3.1 "What yields each verdict"; §6.1 CAP-44.h |
| MAJOR-2: the lite healthy conditions are narrower than the plan's checks | **Put to the owner** (`gov doctor` green, `gov check` with no RED, the first close at exit 0); **changed:** §3.1's table lists the three checks as open and CAP-48.b as not checked (W3), and §6.1 shows the recommended answer | Question G; §3.1 table; §6.1 CAP-44.h |
| MAJOR-3: F-1 and F-2 found but not put to the owner | **Put to the owner**, each with options, costs and a recommendation | Questions H (F-1) and I (F-2); §10 F-1, F-2; §5.1 W2-02 row |
| MINOR-1: CAP-43.b lite overlaps Wave 1 | **Changed:** the distinction between the release's own manifest (CAP-43.b, "Release contents") and the install-side lock (CAP-02.a; CAP-43's acceptance) is stated, and the proposed item text carries it | §3.3 "What the lite item adds to Wave 1"; §6.1 and §6.2 CAP-43.b |
| MINOR-2: the lite A10 leaves out the CAP-55 canaries and Role F's Test Author part | **Changed:** the canaries are in the lite A10 (source-map row 283; CAP-55 is W1); the Test Author part is named as staying for Wave 3, with the reason (CAP-47.a, W3, row 237) | §3.2 A10; §6.1 CAP-44.f |
| MINOR-3: §8's source-map rows are incomplete | **Changed:** all eight rows that state the moved parts are W3 are listed by number (235, 237, 248, 251, 256, 280, 283, 292), and the two W3 rows that stay right (252, 282) are named | §8 `SOURCE_MAP.csv` row |
| MINOR-4: §8 understates the validator's state | **Changed:** the validator is red at the base (line 72), reads the workbench by default (DEC-723) and `docs/source/` through `git show`, so no agent may run it; this is folded into the P-W2-11 point | §8 validator row; §10 F-5 |
| MINOR-5: Question A is missing an option | **Changed:** option (a3) added with its cost (two new ids, 17 → 19); the recommendation stays (a1) with the reason, and confidence lowered to medium | §7 A; §5.2; §5.5; §6.3 |
| MINOR-6: the DEC-105 costs are qualitative | **Changed:** each option costed in tickets and days by WBS §4's method; the apply-now cost itemised, including the A7 and A10 build, the regeneration with no generator and the source map | §2 |
| MINOR-7: "marks the row in part" is no defined state | **Changed:** the undefined state removed; **put to the owner:** who closes W2-I017 and in which state | §5.3; Question J; §8 list row |
| MINOR-8: §9's reversal is partial | **Changed:** a second table covers the owner's entries, CAP-45.a, the source map, W2-I017, ticket files and cards, W2-02's schema and the A7 and A10 code | §9 |
| NOTE-1: the CAP-43 wave note names W2-16 | **Changed:** the note names the item (CAP-43.d) and no ticket; Question B's table gains the vendored skills' licence and version | §5.4; §6.1 CAP-43; §7 B |
| NOTE-2: no tests, code or radius | **Changed:** a hand-made list of tests and code, and a stated radius | §5.5 |
| NOTE-3: DEC-006 is still PROPOSED | **Changed:** the status is named in Question E, with DEC-090 (ACCEPTED) as its refinement | §7 E |
| NOTE-4: the header's `decisions_read` is incomplete | **Changed:** DEC-058, DEC-620, DEC-712, DEC-714, DEC-720 and DEC-724 added, with DEC-723 (now cited in §8); DEC-737 recorded as staged, not as a register entry | frontmatter |

Also in this round, as the brief asked: §11's order line follows DEC-737 (staged).

**The owner's questions after this round** (with Q-14): A (the form of a split item), B (what CAP-43.b lite holds),
C (the ten ADOPTED_HEALTHY conditions), D (CAP-45.a's signed tag), E (DEC-090 and CAP-54.a), F (the rule for each
verdict, and who accepts an exception), G (which operational checks are lite conditions), H (which ticket builds the
lite A7 and A10 stage records), I (W2-02's order against W2-49), J (who closes W2-I017, and how).
