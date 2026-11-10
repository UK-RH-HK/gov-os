# RUBRIC-1 — DEC-1119 (1): the owner's tiered rubric of model and effort, found (2026-11-10)

For the owner. Found by a research helper (Opus, high) and checked by the CTO against the sources. The CTO writes no
rubric (DEC-1119 (1)); the choice below is the owner's.

## 1. The rubric
**OWNER-DECISION-P2-0008 §11, "Routing"** (owner, accepted 2026-09-23; the policy first set 2026-09-21 as the Phase-2
ledger's "Owner routing policy"). Imported here at adoption (DEC-560) as `docs/imported/OWNER-DECISION-P2-0008.md`,
status **ACCEPTED**, state_class **HISTORICAL**, lines 182-186:

> Outer orchestrator, architecture/security adjudication, adversarial review and formal verification: **Opus 5**.
> Cross-cutting implementation: **Sonnet 5**. Genuinely mechanical work: **Haiku**. Build/test/schema: **deterministic
> T0**. Per-spawn selection; the outer orchestrator's model is not changed globally.

The ledger's fuller form (archive tag `archive/gov-os-v4-final`, `release/orchestration/phase-2/PHASE_LEDGER.md`
line 329) adds: "Defaults, not an inflexible rule — a task is promoted when evidence shows its tier inadequate. Effort
is chosen for the problem rather than front-loaded at maximum. Model selection is per spawn, never a global setting."

**Status in this repository:** it never entered the register. Contract v4's `docs/contract/SOURCE_MAP.csv` line 317
maps P2-0008's §1, §3-§7 and §9, not §11. DEC-058 (2026-09-29) kept the old documents as provenance and rebuilt their
wanted features in Charter v5 and Contract v4; §11 was not carried. Lens F (`docs/assessment/2026-10/F-models-context.md`)
and so DEC-839 rest on "no document maps models to tiers"; MODEL-TIERS-1 missed it too.

## 2. Where it differs from DEC-839 (as changed by DEC-957)
1. **Engineers:** Sonnet in the rubric ("cross-cutting implementation"); Opus in DEC-839 (1) (every role).
2. **Haiku:** any genuinely mechanical work in the rubric; DEC-839 only for live harness tests that check a hook fired.
3. **Effort:** the rubric chooses it by the problem, never maximum by default; DEC-839 (2) sets max for the auditor
   and synthesiser (and FULL probes) by default. The rubric gives no level per task, so DEC-839's table and
   DEC-1119 (4)'s default of high fill that gap unless the owner says otherwise.
4. **Per spawn, never global:** `CLAUDE_CODE_SUBAGENT_MODEL` set globally (DEC-839 (3)) goes against it.
5. **Promotion on evidence:** W2-60a refuses a model that is not the role's, which would block moving a task up a
   tier; DEC-1119 (2)'s trial exception is the opening this needs.
No conflict with DEC-957's work order or its effort floor of high.

## 3. Not covered by any owner decision
The test designer, research, product-spec and ticket lead are not named in §11 (closest: "adversarial review" for an
independent test designer, "cross-cutting implementation" for product-spec). These are the roles DEC-1119 (3)'s
trials (E, F) would cover after the lift.

## 4. The owner's choice (it changes a standing decision, DEC-839)
- **(a) Take §11 as the standing rubric:** recorded as a DEC that changes DEC-839 (1)-(3); engineers to Sonnet,
  Haiku for mechanical work, per-spawn models, effort by the problem with high as the default.
- **(b) Take it with changes** (for example engineers stay on Opus until a trial; Haiku only after one).
- **(c) Declare it ended by DEC-058;** DEC-839 stays the rule, and the trials decide the open roles.
Until the owner chooses, practice stays as it is: DEC-839's models and efforts, ACT-preparation helpers on Sonnet at
high (DEC-1119 (3)).

**CTO's recommendation: (b)**, with ACT preparation and mechanical helpers moved down at once, and engineers kept on
Opus through the lift. Why: the rubric is the owner's and it fits DEC-1119 (3). But changing the engineer's model in
the middle of D-10's fixes would change two things at once; a trial after the lift would settle it.
