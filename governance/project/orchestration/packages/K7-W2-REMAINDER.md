# K7-W2-REMAINDER: keystone 7's two Wave 2 items, in W2-27 (DEC-1089 (2))

For the owner. Written 2026-11-07 by the CTO (session `ad44f5fe`).

## 1. What the owner decided, and where it goes
- **Decided (DEC-1089 (2)):** K7 is done for Wave 2. The pin ladder stays by hand until Wave 3, and W2-17 and W2-18 stay in Wave 3.
- **Two items stay in Wave 2:**
  - (a) the first numbered, frozen release, cut and hash-checked, for EXAMIN's copy;
  - (b) exit criterion 7's paperwork for CAP-45.a.
- **The home: W2-27** (`DAEO-h4rh`, EXAMIN adoption on a copy; open, not started; K9 per `packages/LIFT-1/D9-FATES.md` §3).
  - It already installs "W2-16's numbered, frozen release, never this repository's branch" (its KPI line, DEC-954 Q8c).
  - DEC-941 item 3 puts the release path in K9.
- **Runner-up: W2-46** (`DAEO-nn1s`, the exit run). It checks criterion 7, but it runs last, which is too late for the release.

## 2. Item (a): the first numbered, frozen release
- **What exists:**
  - W2-16 is closed (`gov release`: immutable, hash-pinned releases).
  - W2-102's release skill is closed: freeze, version, changelog, provenance note, and the tag request to the owner.
  - The cut is the owner's alone, from a plain terminal, with a typed one-time code (DEC-772).
  - **No numbered release exists yet.** The only release tags are September's `v4.1.3-rc1` to `v4.1.5-rc1`.
- **When (proposed):** after the lift's re-pin, so that the release holds what K9 measures (W2-92, W2-32 S11 with the pool on, the reranker the owner chooses, W2-136 and W2-20). It must come **before** W2-81's proving-ground run and W2-27, since both install it (DEC-954 Q8c).
- **The steps:**
  1. The CTO runs W2-102's skill: the freeze, the version, the changelog, the provenance note and the tag request.
  2. The owner runs `gov release` in a plain terminal.
  3. **The hash check (the CTO):** two builds from the tagged commit give the same bytes; the wheel's sha256 equals the release manifest's; every file hash in the manifest matches. This is the same check re-pin window 4's part A made.
  4. The check's record goes in `docs/plan/wave-2/examin-copy/release-check.md`, under W2-27's id.
- **Cost:** about an hour of the CTO's time, and one owner act of a few minutes. No GPU.

## 3. Item (b): CAP-45.a and exit criterion 7
- **The state now:** CAP-45.a (`gov update`, the authenticated source) is still a **Wave 2** item in Contract v4.2. W2-49's CIT-P kept it in Wave 2, with a Wave 2 clause (`docs/changes/W2-49-CIT-P.md` §7 D (ii)).
- **What the WBS says:** exit criterion 7 (WBS §5) asks for "a CIT-P note moving it to Wave 3, or a named exception".

**Option A (recommended): a CIT-P note moving CAP-45.a to Wave 3.**
- **The note:** `docs/changes/W2-27-CIT-P.md`. Its draftsman is a product-spec agent (DEC-996 item 3 (D)), with one independent review. It goes to the owner under DEC-105 (apply now).
- **After the owner's approval:** the Contract edit is CAP-45.a's wave field in `contract.yaml`, its record `docs/contract/capabilities/CAP-45.a.md` regenerated, and a change-log row.
- **Cost:** about half a day of agent work on the CPU, beside the experiments, plus one owner reading.
- **The gain:** the Contract stops saying Wave 2 for work done in Wave 3, so the exit audit finds no drift.

**Option B: a named exception.**
- **What it is:** one line in W2-46's exit record, which the owner accepts at the exit.
- **Cost:** nothing now.
- **The catch:** the Contract keeps the drift until Wave 3, and the exit audit (W2-47) will name it.

**Either way:** the item touches nothing in EXAMIN's copy, so it can run now, before K9's entry criteria are met.

## 4. W2-27's changes (made in this commit, each marked DEC-1089; DEC-1088 (6) allows changes to an open ticket)
- **`allowed_paths`** gains `docs/changes/W2-27-CIT-P.md`. `docs/contract/**` is added only once the owner approves the note's Contract edit.
- **Two KPI lines:**
  - "The first numbered, frozen release is cut by the owner and hash-checked (two builds give the same bytes; the wheel and every file match the manifest), recorded in `docs/plan/wave-2/examin-copy/release-check.md`, before W2-81's proving-ground run and this ticket's adoption [DEC-1089, DEC-954 Q8c, DEC-772]."
  - "Exit criterion 7: CAP-45.a moved to Wave 3 by an approved CIT-P note (`docs/changes/W2-27-CIT-P.md`), or named as an exception the owner accepts [DEC-1089]."
- **The body:** a "DEC-1089" section stating that these two items run before K9's entry criteria, and why.

## 5. Also found (for the owner's view of the countdown)
`status_block.py` counts a keystone only from `keystone-N` tags on tickets.
- **K9 shows as done, but it is not.** Its one tagged ticket, W2-83a, is closed and has left K9. Most of K9's real list (D9-FATES §3) is open: W2-27, W2-28, W2-29, W2-30, W2-46, W2-47, W2-23, W2-88, W2-93, W2-94, W2-121, W2-124 and W2-115. W2-81, W2-52, W2-105, W2-110 and W2-90b are in flight.
- **K7 has no tag.** W2-16 is closed, and a closed ticket is never edited (DEC-1088 (6)), so it cannot be tagged now.
- **The CTO's fix:** tag K9's open tickets `keystone-9` (marked DEC-1083 and DEC-1089), and give the status tool a hand-kept fact for a keystone done by decision (K7, DEC-1089). The countdown then reads K9 "in progress".

## 6. For the owner
1. **Item (b):** option A (the CIT-P note, recommended) or option B (a named exception)?
2. **Item (a):** the release cut after the lift's re-pin and before W2-81's proving-ground run. Agreed?

**Basis:** question 1 (EXAMIN's copy runs one frozen, hash-checked release), question 2 (the Contract matches the waves, with no drift at the exit audit) and question 4 (no automation that saves only minutes).
