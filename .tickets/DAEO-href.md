---
id: DAEO-href
wbs_id: W2-183
external-ref: W2-183
title: gov close's context packet at a project setting; gov context's supplementary block capped at 6,000 tokens
type: task
class: implementation
role: engineer
profile: STANDARD
status: in_progress
state_class: AUTHORITATIVE
priority: 1
created: 2026-11-13
deps: []
allowed_paths:
- src/gov/context/__init__.py
- src/gov/close/command.py
- governance/project/facts.yaml
- tests/unit/context/test_w2_183_*.py
- tests/unit/close/test_w2_183_*.py
- tests/unit/close/test_context.py  # its :31 case pins build_context(ROOT, "T-1"); revised to the decided call with budget= (DEC-1165; CTO, DEC-1156 (7), DEC-1157 (12))
- docs/probes/DAEO-href/**  # the probe record
reads:
- src/gov/context/context_check.py
- src/gov/context/command.py
- src/gov/brief/build.py
- tests/acceptance/W1-24/**
- tests/acceptance/W2-04/**
- tests/unit/context/**
needs: []
waits_on: []
kpis:
  success:
  - 'S1: gov close builds the ticket''s context packet at the project''s setting `budgets.close_context_tokens` in governance/project/facts.yaml (65536 in this repository), not at gov context''s default of 6,000; with no setting, the default applies as today [DEC-1165 (1), DEC-1027 H] Verify: in a stand-in repository, a ticket whose own text and mandatory inputs come to about 10,000 tokens passes the close''s context step with the setting at 65536 and is refused CONTEXT_FAILED (context_error CONTEXT_OVER_CEILING) with the setting at 8000 or absent'
  - 'S2: gov context''s supplementary block holds at most 6,000 tokens whatever --budget is passed (its room is the smaller of the budget less the mandatory part, and 6,000); the close''s packet is capped the same way [DEC-1165 (2), DEC-860] Verify: in a stand-in with a store large enough to fill it, `gov context <ticket> --budget 60000` gives a supplementary block of at most 6,000 tokens; the same with the close''s setting at 65536'
  - 'S3: the mandatory part is never shortened, and a packet whose budget leaves under 6,000 tokens of room is unchanged: the same items and the same hash as before the change [DEC-1165 (3), CAP-15.d] Verify: a small stand-in ticket''s packet at the default budget has the hash it had before the change; a ticket whose mandatory part passes its ceiling is still refused CONTEXT_OVER_CEILING, named'
  failure:
  - 'A setting that is not a positive whole number refuses by name (never a silent default, never a crash). Verify: `budgets.close_context_tokens: 0`, `-5` and `"many"` each make the close''s context step refuse with a named finding'
non_goals:
- 'no trimming of any ticket''s own text or sources (W2-88''s mandatory part, about 61,500 tokens, stays as it is: that needs its text trimmed, which this ticket does not do)'
- 'no change to gov check''s context-reproducibility (it stays green while some tickets refuse over the ceiling, DEC-1025), to the brief builder (it reads only its own keys of `budgets:`) or to the kernel''s facts schema (`budgets:` already admits any key with a whole number)'
- 'no change to the default ceiling of 6,000 for gov context and briefs'
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1165, DEC-1027, DEC-860, CAP-15.d]
acceptance_tests: {path: tests/acceptance/W2-183/}
---

# W2-183 gov close's context packet at a project setting; the supplementary cap

The owner's DEC-1165 (2026-11-13, "add the supplementary cap"): gov context's ceiling (DEC-1027 H) refuses most tickets
(W2-88 at 56,284 tokens against 6,000; W2-113 8,440; W2-120 9,476; W2-98 9,828; W2-154 7,401), and every lead works
round it with `--budget`. Two changes:

- **The close's packet** (`_build_context`, `src/gov/close/command.py`) is built at a project setting,
  `budgets.close_context_tokens` in `governance/project/facts.yaml` (65536 here), so closes stop refusing on it.
- **The supplementary cap:** whatever `--budget` a lead passes, a packet carries at most 6,000 tokens of supplementary
  context above its mandatory part. W2-88's workers today get packets filled toward 60,000; under the cap they get the
  mandatory part plus at most 6,000. A ticket whose mandatory part is small is unchanged.

The mandatory part is never shortened (CAP-15.d). The key sits in `budgets:` because the kernel's facts schema (kernel bytes) admits no new top-level key and `budgets:`
already admits any key with a whole number; it counts tokens, not the prose characters of the template keys. A test designer writes the cases from these lines; an engineer builds; a STANDARD review; the land.
