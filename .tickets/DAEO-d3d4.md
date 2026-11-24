---
id: DAEO-d3d4
status: in_progress
deps: [DAEO-zflj, DAEO-siiz]
links: [DAEO-zflj, DAEO-siiz, DAEO-l78m, DAEO-cdoi]
created: 2026-11-22T14:30:00Z
type: task
priority: 1
assignee: engineer
external-ref: W2-210
tags: [adoption, verdict, lite, emergency-2, release-0.1.6]
wbs_id: W2-210
title: "The lite adoption verdict stage (CAP-44.h): gov adopt --lite --stage VERDICT computes the lite conditions by code, gives one of the three verdicts, writes the adoption-verdict record; only the owner accepts an exception"
class: implementation
state_class: AUTHORITATIVE
role: engineer
profile: STANDARD
depends_on:
- DAEO-zflj
- DAEO-siiz
waits_on: []
closes: [CAP-44.h]
allowed_paths:
- src/gov/adopt/**
- tests/unit/adopt/**
- tests/acceptance/W2-210/**
- tests/acceptance/W2-81/**
est_loc: 500
kpis:
  success:
  - 'V1 `gov adopt --lite --stage VERDICT` (the stage is in `gov.adopt.command.STAGES`, after A10) computes every lite condition of CAP-44.h by code from the repository and commits `governance/adoption/VERDICT-lite.md` with each condition recorded `met` or `not met` and its evidence (the command run and its exit code, or the record read, and the path). The conditions, each named: A0, A1, A2, A3, A4, A5, A6 and A8, each with its stage record committed and standing on the record before it as that record now is (a missing or unreadable record is `not met` and named, never skipped); the A5 review still holds (the verdict A5 accepted is the committed Independent Auditor record, its sha256 as A5 recorded it); the native package layout kept (no A6 move leaves a native layout of CAP-44.j without both grounds); the lite A7 gate and the lite A10 gate each recorded with `result: pass` and standing on the A6 and A8 records as they now are; the pinned, hash-verified release (`gov doctor`''s `framework_lock` part says MATCH); `gov doctor` exits 0; `gov check` reports no RED family; one ticket closed through the landing at exit 0 with the repository''s own test command (a ticket `closed` in `.tickets/` whose close record `docs/close/<ticket>/CL-<ticket>.md` is a record of type `close` with no failure, no test failed or in error, and at least one test passed). Verify: a synthetic adopted repository under `~/gov-os-runs/d1/` with every stage run, both gates passed and a closed ticket gives every condition `met`; for each condition one planted failure (a stage record removed, one that no longer stands on the one before, an A5 verdict changed, a move out of a native layout, an A7 record with `result: fail`, `gov doctor` DRIFT, `gov doctor` exit 3, a RED family, no closed ticket, a close record with a failed test) makes exactly that condition `not met`, names it, and leaves the others as they were; the same planted failure with the checks of the live tools stood in (`gov.adopt.verdict.compute(root, session, tools=...)`; the command line never takes a stand-in) gives the same answer. [CAP-44.h; DEC-1227 D1 (a); DEC-1231; DAEO-l78m]'
  - 'V2 The verdict is ADOPTED_HEALTHY when every lite condition is met; ADOPTED_WITH_ACCEPTED_EXCEPTIONS when every condition not met is accepted by name in the owner''s exceptions file `governance/project/adoption-exceptions.yaml` (a list of `{condition: <the condition''s name as VERDICT-lite.md gives it>, decision: DEC-n}`), which the stage reads only when the last commit that touched the file carries the trailer `Role: owner` and no other Role (a commit with `Role: owner`, as `gov.release`''s authority file is read: the file gives the machine-readable name, the commit gives the owner; the file stays out of the adoption''s own records, `governance/adoption/`, which agents write); otherwise NOT_ADOPTED_HEALTHY. An accepted condition is recorded `accepted` with `owner_entry: DEC-n` (the W2-02 schema''s form); an entry for a condition that is met, or for no condition, is recorded as unused and changes nothing. Verify: the repository of V1 with A7 not met and no exceptions file gives NOT_ADOPTED_HEALTHY; the same with the file naming that condition and a last commit with `Role: owner` gives ADOPTED_WITH_ACCEPTED_EXCEPTIONS with the condition `accepted` and its `owner_entry`; with two conditions not met and the file naming one, NOT_ADOPTED_HEALTHY; with every condition met and an exceptions file, ADOPTED_HEALTHY; the stage re-run after the owner''s commit replaces the earlier record (`supersedes` names its sha256; git keeps the old one). A NOT_ADOPTED_HEALTHY verdict is committed as a record and the command exits non-zero (`ADOPT_NOT_ADOPTED`, the conditions not met named), as the lite gates do; the other two exit 0. [CAP-44.h; DEC-741 answer F]'
  - 'V3 The record is of type `adoption-verdict` and valid under the schema of W2-02 (`gov rebuild` lists it among none invalid): `verdict`, `conditions` (name, source, state, `owner_entry` where accepted; each also with its `evidence`: `command`, `exit`, `path`), and, beside them, `lite: true`; `adopted_healthy_conditions`, the ten ADOPTED_HEALTHY conditions of Adoption Protocol v3.0 section 20 as CAP-44.h numbers them, each with its number, its name, its wave marking (`W2` or `W3`) and its lite part (the lite conditions that check it, or none); and `conditions_not_checked`, naming each condition the verdict does not check (the W3 conditions with no lite part, (2), (7), (8) and (10), and the W3 part of (1), (4), (5), (6) and (9), A9 and A11, the certification by qualification, a separate verifier role). The record stands on the A10 record''s sha256 as it now is and names the commit it was computed at. Verify: the record of V1 read back: `lite` is true; the ten entries are there with the markings CAP-44.h gives ((3) W2, the others W3); `conditions_not_checked` names (2), (7), (8) and (10); the schema check and `gov rebuild` accept it. [CAP-44.h; DEC-722; W2-02]'
  - 'V4 The verdict is computed by code alone; no model and no session''s word enters it. The independence CAP-44.h asks for is carried by the three Independent Auditor records the stage already depends on: A5''s, A7''s and A10''s. The stage re-reads each by code (the commit that brought it carries `Role: independent-auditor` alone and wrote nothing of the adoption''s folder; its `auditor_session` is named and differs from the sessions that ran the stages and from this one) and lists them in the record under `auditors` (path, sha256, commit, session, role); a stage whose auditor record fails that re-read has its condition `not met`. Verify: the record of V1 lists the three auditors; an A7 auditor record brought by a commit with another Role, and one whose `auditor_session` equals a stage''s session, each give A7''s condition `not met` and the verdict NOT_ADOPTED_HEALTHY. [CAP-44.h ("from a fresh Independent Auditor"); lite_gates.AUDITOR]'
  - 'V5 W2-81''s judge reads the verdict stage: with `VERDICT` in `gov.adopt.command.STAGES` its `built_today()` counts it built (as A7 and A10 are), and a stage record at `governance/adoption/VERDICT-lite.md` is PRESENT when it exists and is well formed (`verdict` one of the three, `lite` true, `conditions` a list of mappings with `name` and `state`, `conditions_not_checked` a list, and the verdict agrees with the conditions as V2 states); a missing record stays ABSENT and a malformed one MALFORMED, each a reason of `overall` as today. The judge''s capability table and the README''s VERDICT row no longer say not built. Verify: the judge over a stand-in adoption with a well-formed verdict record has no VERDICT reason; with the record absent, one reason; with ADOPTED_HEALTHY over a condition `not met`, with `lite` false and with no `conditions_not_checked`, each MALFORMED; the W2-81 judge self-tests stay green. [DAEO-l78m; W2-81 analysis R7 and A5]'
  failure:
  - 'F1 A verdict record the stage did not produce is refused: `governance/adoption/VERDICT-lite.md` carries `produced_by`, a sha256 over the record''s body as the stage wrote it (without that field); `gov.adopt.verdict.check_record(root)` (and the stage when it replaces a record) refuses, naming the cause, a record that lacks it, whose digest does not match the body, that stands on another A10 record than the one now committed, that was not committed by a commit whose subject is the stage''s (`gov adopt --lite VERDICT: ...`) touching that record alone, or whose verdict does not agree with its conditions (V2). Fails if a hand-written record, or a produced one edited by hand, is read as a verdict. Verify: the produced record, a copy with the verdict changed, one with a condition''s state changed, one with the digest removed, one committed by an ordinary commit, and one written before an A10 record that has since changed: each refused, the produced one accepted. [CAP-44.h]'
  - 'F2 ADOPTED_HEALTHY with any condition not met is impossible, and an exception accepted by anyone but the owner is refused: with an exceptions file whose last commit carries `Role: engineer`, `Role: independent-auditor`, `Role: orchestrator`, no Role, or `Role: owner` together with another, or with the file modified and not committed, the stage refuses before it computes anything (`ADOPT_EXCEPTIONS_NOT_OWNERS`, the file and the commit named) and writes no record; a verdict of ADOPTED_HEALTHY over a condition not met, or of ADOPTED_WITH_ACCEPTED_EXCEPTIONS over one not accepted, fails `check_record`. Fails if any such record is committed by the stage or read by `check_record` or the judge as a verdict. Verify: the exceptions file committed by each of the roles above, and uncommitted: refused, the tree and the refs as before; each impossible record built by hand: refused by `check_record` and MALFORMED to the judge. [CAP-44.h; DEC-741 answer F]'
non_goals:
- 'The ten ADOPTED_HEALTHY conditions in full, A9, A11 and findings (CAP-44.g, CAP-44.k, CAP-44.l): Wave 3; the record names them as not checked.'
- 'The adopt skill''s text and the adoption brief template: kernel and instruction text, the CTO''s (EMERGENCY-2 3.5); the CTO adds the VERDICT step after this lands.'
- 'A separate confirmation session of the Independent Auditor after the stage (V4: the three gate records carry the independence); a change to the W2-02 schema unless V1 cannot be carried by it.'
- 'Reading the owner''s exceptions by the W2-81 judge''s `overall` (the judge''s own owner-exceptions input, T3): that stays W2-81''s.'
sources: [DEC-1227, DEC-1231, CAP-44.h, DAEO-zflj, DAEO-l78m, DEC-722, DEC-741, DEC-1225, EMERGENCY-2 8.2]
acceptance_tests:
  path: tests/acceptance/W2-210/
  author: independent-test-designer (MR-3); written before implementation
track: A
---
# W2-210: the lite adoption verdict stage (CAP-44.h)

A new feature (DEC-1227 D1 (a); DEC-1231: it rides in release 0.1.6). CAP-44.h, W2: "Adoption verdict, lite:
ADOPTED_HEALTHY / ADOPTED_WITH_ACCEPTED_EXCEPTIONS / NOT_ADOPTED_HEALTHY ... against the lite conditions". W2-02 built the
record type (`adoption-verdict`) and W2-52 the A7 and A10 gates; nothing wrote or checked a verdict, and W2-52's third
KPI line ("the verdict reads both records as named conditions") was not delivered. The 0.1.4 proving run lost six
reasons to it (`docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md`, R7, A5, D1).

## Problem

An adopter, the owner and the proving run have no computed answer to "is this repository adopted and healthy". An agent
can write an `adoption-verdict` file by hand and nothing refuses it. The judge counts a stage that is not PRESENT as a
reason, so the missing verdict is a reason on every repository.

## Approach

`src/gov/adopt/verdict.py` (new): `compute(root, session, tools=None)`, the conditions as functions in the form of
`lite_gates._check`, each returning `met` / `not met` with its evidence; `stage(run)` the stage; `check_record(root)`.
`gov.adopt.command.STAGES` gains `VERDICT` after `A10` (and before `MA`); `gov.adopt.stages.run` sends it to the stage
as the lite gates are sent, with no chain (it reads the records it stands on, A10's last). The stage needs a clean tree;
it commits `governance/adoption/VERDICT-lite.md` with the subject `gov adopt --lite VERDICT: lite adoption verdict`. The
live tools (`gov doctor`, `gov check`) run as child `gov` processes of the same interpreter from the repository root;
`tools=` is the self-tests' seam beside them, as `_release_test` is the release's, never reachable from the command line.
The stage reuses the checks that exist (`stages._verdict` for A5, `project.chain`, `stages._native`, the gates' own
re-read of an auditor record) and does not re-implement them. The condition names are fixed once, in `verdict.CONDITIONS`
(the test designer's README names them; the engineer follows), and the record's `conditions[].name` is that name.

## The owner's exceptions (V2): why a file and a Role: owner commit

CAP-44.h: "accepted by name in an owner decision (Role: owner)". The W2-02 schema wants `owner_entry` to be a decision id
(`DEC-n`), so an accepted condition must name one. A bare commit with `Role: owner` carries no machine-readable
condition name; a bare file carries no owner. The exceptions file names each condition and its decision, and the stage
reads it only when its last commit says the owner made it: the same two-part reading the release's authority file has
(`Decided-by: owner`). It is the project's file (`governance/project/`), not the adoption's, which agents write.

## Test data

Synthetic adopted repositories under `~/gov-os-runs/d1/` (the W1-41 "harbour" project run through A0 to A10 by the
W2-52 support), planted per condition; the self-tests stand in the live tools through `tools=`.
