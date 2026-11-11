---
id: DAEO-ylsh
status: open
deps: [DAEO-ecac, DAEO-r30l]
links: [DAEO-ecac, DAEO-cv58]
created: 2026-11-11T01:20:16Z
type: task
priority: 2
assignee: engineer
external-ref: W2-156
tags: [wave-2, implementation, standard, after-the-lift, launch, spend]
wbs_id: W2-156
title: 'The runaway brake in the product: a ticket whose measured cost passes twice its projection holds its next launch and goes to the inbox once; usage stays record-only (EMERGENCY-TOOLS-1 D2; DEC-1091 (2), DEC-1119 (5))'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-ecac
- DAEO-r30l
allowed_paths:
- src/gov/spend/**
- src/gov/launch/launcher.py  # the one call that refuses a braked ticket's launch, after the gate's call
- src/gov/check/commands.py  # the one line that records `spend` (the precedent: W2-20's `resources`)
- tests/unit/spend/**
- tests/unit/launch/test_w2_156*
- docs/changes/W2-156-evidence.md
reads:
- src/gov/launch/**
- src/gov/telemetry/**
- governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md
needs:
- src/gov/launch/launcher.py
- src/gov/check/commands.py
waits_on:
- ref: DEC-1091
  reason: 'DEC-1091 (2) states the brake for experiments; the owner confirms it holds for every ticket of an adopted product before this is built'
kpis:
  success:
  - 'S1 A ticket''s running cost is the sum of the measured cost of its launched sessions'' records (W2-60b''s session record, keyed by the ticket) since its first launch or since the last clear; a session whose cost the record gives as not measured is counted as unknown and named in the sum, never as zero. Verify: planted session records for one ticket (three measured, one not measured): `gov spend sum` prints the total of the three, "1 unknown", the projection and the brake state, one line per ticket [DEC-1091 (2), DEC-1119 (5), DEC-655]'
  - 'S2 `gov spend check` brakes a ticket whose running cost is more than twice its latest projection (the projection a launch records, W2-60a''s launch record): it writes one brake record, one marker file for that ticket and one item in the project''s inbox folder naming the ticket, the cost and the projection, once per ticket until it is cleared. Verify: planted records at 1.99 times the projection give no brake; at 2.01 times, one record, one marker, one inbox item; a second `check` writes none [DEC-1091 (2), DEC-1119 (5)]'
  - 'S3 `gov launch` refuses a new session for a ticket that has a brake marker, naming the marker, the cost and the projection (error SPEND_BRAKED), after the resource gate''s check and before anything starts; a ticket with no marker launches as before. Verify: a launcher unit test with a planted marker (refused, nothing started) and without (started) [DEC-1091 (2), DEC-1119 (5)]'
  - 'S4 A ticket with no projection is never braked: `check` names it "no projection" and writes nothing. Verify: planted records with a large cost and no projection: no marker, no inbox item [DEC-1091 (2)]'
  - 'S5 `gov spend clear <ticket> [--projection-usd N] --note <text>` removes the marker and restarts the ticket''s count from that moment, with the note and the new projection (if given) in the brake record; a cost before the clear is no longer counted. Verify: after a planted brake, `clear` then `launch` starts, and `sum` shows the cost since the clear only [DEC-1091 (2)]'
  - 'S6 Usage stays record-only: the brake only holds a new launch and writes its one inbox item; it stops no running session, sends no notification outside the project''s inbox, and raises no alarm about usage. Verify: a planted braked ticket with a running stand-in session: the session''s process is untouched after `check`, and a notifier stub is never called [DEC-1089 (3), DEC-1091 (2)]'
  failure:
  - 'A running session stopped by the brake, or a push or alarm sent about usage.'
  - 'A not-measured cost counted as zero, or a ticket with no projection braked.'
  - 'A launch for a braked ticket that starts.'
  - 'Any change outside the paths above.'
profile: STANDARD
sources:
- DEC-1091
- DEC-1089
- DEC-1112
- DEC-1119
- DEC-1120
- DEC-655
- DEC-1109
- DAEO-cv58  # W2-60a
- DAEO-ecac  # W2-60b
- DAEO-r30l  # W2-20
est_loc: 220
acceptance_tests:
  path: tests/acceptance/W2-156/
  author: 'independent-test-designer (MR-3), from these KPI lines; planted session records and a planted launcher, never a live session'
track: A
list_rows: []
---
# W2-156 The runaway brake in the product

Filed by the product-spec helper of the night audit (DAEO-sdxk's anti-drift audit (d), 2026-11-11) on EMERGENCY-TOOLS-1 row D2; **after the lift**, **before EXAMIN's copy** (§2 item 4: "no ticket holds the runaway brake").

- **Problem.** The CTO's `spend.py` (the spend log and the brake: `.gov-runtime/scratch/orchestrator/tools/spend.py`, DEC-1091 (2)) brakes a ticket at twice its projection. It is a scratch tool, on no branch of the product. An adopted product's launches have no brake, and W2-60b's session record holds cost but no projection and no refusal.
- **Approach.** A `spend` module reads W2-60b's session records, keeps a marker per braked ticket, and `gov launch` refuses a braked ticket. The brake's rule is `spend.py`'s: twice the latest projection, counted from the first launch or the last clear. Alternatives: a field on W2-60b's record (rejected: the brake is a rule on many records, not a field); a brake in the dispatcher alone (rejected: a hand launch would bypass it).
- **Interface.** `gov spend check | clear <ticket> | sum`. The marker and the brake record live in the project's runtime folder (`.gov-runtime/spend/`); the inbox is the project's inbox folder (W2-121's, a configured path). Both are the simplest reading and are named in `docs/changes/W2-156-evidence.md`.
- **Non-goals.** No budget cap, no usage ping (DEC-1089 (3)); the spend log's own schema (the CTO's RUBRIC-2 keys `model`, `class`, `tier`, `promoted`) stays W2-60b's to hold; no change to the CTO's `spend.py`.
- **Rabbit holes.** Reading a session's log text (counts only, as W2-60b); a brake on a reviewer's session of the same ticket (it counts, it is not exempt).

[DEC-1091 (2), DEC-1089 (3), DEC-1119 (5)]
