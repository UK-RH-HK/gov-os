# P-ADOPT-SPEC-AUDIT-1: a spec audit as a standard adoption stage

Drafted 2026-11-16 14:0x for the owner (to be recorded once the 0.1.1 hold ends).

## 1. Today: no spec audit in the adoption practice
- The adopt skill (`template/governance/kernel/skills/adopt/SKILL.md`) lists A0-A10 and MA: A1 cold inventory, A2
  classification of artefacts, A3 the target path map, A4 the plan, A5 its independent review, A6 the migration, A7 and
  A10 independent verifications, A8 legacy memory, A9 the memory practice. None of them compares specs with code.
- The Contract's CAP-44 (`docs/contract/CONTRACT_v4.md:690-712`) has no spec-to-code stage either; the nearest is A11's
  full audit, a Wave 3 item (CAP-44.k). A2 classes a spec file as a document; nothing asks whether it is built.
- So the practice does not include your step 3 today.

## 2. Proposed: stage AS, the spec audit
- **Place:** after A2 (classification) and before A3 (the path map), so the path map and A5's review see which specs
  are alive; it reads A1's inventory and A2's classes.
- **Produces** a record `governance/adoption/AS-spec-audit.md`: every spec found (path, title, its wave or status if it
  states one); for each, built, partly built or not built, with evidence (code paths, tests, commits); the tickets
  found, done or not, by wave; specs with no code; code with no spec (modules no spec names); and each gap as one
  question to the owner, with the owner's answer recorded beside it when it comes (how and when the spec is
  established, or the code retired).
- **Checked:** lite first, by the product's own record checks (every spec and every top-level code module appears;
  every gap carries a question); the independent check comes with A5 (the path map's reviewer reads the AS record), so
  no new auditor session is needed in the lite form.
- **Changes in the product:** `gov adopt`'s stage list gains AS (`src/gov/adopt/command.py` STAGES, a stage function,
  its record schema), the adopt skill's text gains the stage (a kernel change: a CIT-P with its review and your
  approval), and the Contract gains the line (CAP-44, a specification change).

## 3. Options
| | (a) a standard stage now | (b) a lite practice in the skill only | (c) per repository by its CTO |
|---|---|---|---|
| What | AS in `gov adopt` and the skill, by CIT-P, in the release after 0.1.1 | the skill tells the CTO to write the AS record by hand; no stage, no check | each product CTO does it as EXAMIN's does now, no product change |
| Every repository inherits it | yes, checked | yes, unchecked | no |
| Cost | about 1 to 1.5 days (ticket, TD, engineer, review, CIT-P), your approval of the skill text | about half a day (the skill's text, a CIT-P) | none now |
| EXAMIN now | does step 3 by hand meanwhile; the stage arrives for later repositories | the same | the same |

**Recommendation: (a).** Your direction makes it standard for every repository; a stage with its record and check is
what makes later adoptions inherit it, and EXAMIN's hand-made audit becomes its first worked example. Confidence:
medium-high.

**Your line:** `P-ADOPT-SPEC-AUDIT-1 (a)`, `(b)` or `(c)` (a new ticket for (a) or (b) on your P1, DEC-974).
