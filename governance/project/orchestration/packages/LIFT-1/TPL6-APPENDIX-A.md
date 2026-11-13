# TPL6-APPENDIX-A: the CTO prompt's Appendix A cut to a pointer (W2-128 TPL-6 S1; for the owner)

- **For:** the owner. The prompt is the owner's text, so this is proposed, not applied (DEC-1112 (3): a change to
  the prompt the owner wrote).
- **By:** the CTO (orchestrator `DAEO-sdxk`), 2026-11-09.
- **Under:** DEC-1050 (TEMPLATES), DEC-1052 (the templates replace R-1 to R-5's brief text), W2-128's TPL-6 S1 KPI
  line ("Appendix A of `governance/project/prompts/w2-orchestrator.md` is a pointer to the templates under 600
  characters").

## What changes
`governance/project/prompts/w2-orchestrator.md` (sha256 `eaa616de7fcdea6a…`, last changed `0502db41`). Lines 363 to
422, "## Appendix A — briefs", 9,234 characters, are replaced by the text below.

Today's sections and where each one's content now lives (merged at `c6aefae9`):

| today | now |
|---|---|
| the return rule (head) | `brief.md` (T-0), "Return" |
| A1 independent test designer | `role-test-designer.md` (T-4) |
| A2 engineer | `role-engineer.md` (T-5) |
| A3 reviewer | `role-reviewer.md` (T-6), with JUDGEMENT's rules |
| A4 product-spec | `role-product-spec.md` (T-3) |
| A5 ticket lead | `role-lead.md` (T-7) |

## The proposed text (466 characters)

```markdown
## Appendix A — briefs

Briefs come from the kernel templates in `template/governance/kernel/templates/`: `brief.md` (the envelope and the
return form) and one `role-*.md` per role. They are filled from the ticket and `governance/project/facts.yaml` by
`gov brief <role> <ticket>` (W2-152), and by hand from the same templates until it lands. The role template goes as
the appended system prompt (W2-153). Nothing in this prompt overrides them [DEC-1050, DEC-1052].
```

## When
**Recommended: after W2-152 lands,** so the pointer names a command that exists. Applying it now is safe too, because
the hand-filled route is named. The CTO applies it on the owner's yes, in one commit
(`Implements: DEC-1050, DEC-1052`, `Decided-by: owner (chat, <date>)`). Then W2-128's S11 size test (round 2) checks it.

## What the owner says
One line: "Appendix A as proposed (now | after W2-152)", or a change to the text.
