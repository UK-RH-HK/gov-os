# CIT-P: "one bar, two rounds" for every role (DEC-1131 (1), (2), (4))

Read `LIFT-common.md` first (scratch only). Role: product-spec helper, Sonnet high, class C2 (DEC-1120). Scratch
folder: `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/citp-one-bar/`; your temporary
folder is its `tmp/`. Save `CIT-P-ONE-BAR.md` early and extend it.

## Read first
DEC-1131 and DEC-1010 in `docs/DECISION_REGISTER.md`, word for word; `governance/project/orchestration/packages/DEC1010-REVIEW.md`
(§4.1 the rule's wording, §4.2 the changes by file, §4.4, §4.5); the CIT-P form and its precedents (search
`docs/changes/*CIT-P*`, e.g. `docs/changes/W2-82-CIT-P.md` if present, and CAP-33 in `docs/contract/`); the change skill
`template/governance/kernel/skills/change/`.

## Write the CIT-P (not the edits)
1. **What and why:** DEC-1131's rule, with the open point decided (an engineer pass that only fixes the findings the
   review marked blocking is the same round), option A (text now; the CTO's round ledger by hand; counting code after
   two weeks).
2. **Every change, by file and line, as the exact new text** (before → after): JUDGEMENT.md (find it); the brief
   templates (`.claude/templates/` sources under `template/governance/kernel/` and `governance/project/briefs/`, the lead
   brief `LEAD-w2-common.md`, the reviewer template); the role files (`template/governance/kernel/roles/`: reviewer,
   independent-auditor, independent-test-designer, engineer, product-spec, lead/orchestrator), including the
   contradictions DEC1010-REVIEW found (`role-reviewer.md` line 24 against DEC-096; `role-lead.md` "three iterations"
   line 42 against "never a third round" line 48); the kernel skills that state rounds (audit, test-design, change);
   the ticket template and schema: **a KPI id** on each KPI line (its form, e.g. `S3`, `F1`, how existing lines get
   one without editing reviewed tickets: say so), and the finding form "names the KPI line it fails, or is a row".
   Mark which files are kernel (CAP-33: CIT-P, independent review, owner approval, version) and which are project.
3. **The ledger by hand:** where it lives (propose `governance/project/orchestration/ROUND-LEDGER.md`), its columns
   (ticket, role, round, date, what was judged, verdict, KPI lines failed), who writes it (the CTO), and seeded with this
   week's counts from DEC1010-REVIEW §3.
4. **What it does not change:** the two code fixes (ACT-OPERATOR-ROUNDS-1, separate); the counting code (after two
   weeks; name the ticket that will hold it: propose a W2 id after W2-174).
5. **Risks and the review:** what could break (a real fail-open found late: DEC-957's P1 route), the independent
   reviewer's checks, the version bump.

Plain language. Return the twelve fields, short. Estimate 1.5 h.
