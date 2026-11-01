# P1-DEC995-APPLY — your role rule applied: the splits, the policy gaps it exposed, and the roles KPI edits

Evidence: two read-only reviews of 2026-11-01 (all 87 open tickets swept; ROLES-SPEC-1 and the roles tickets
checked line by line). Full texts: `.gov-runtime/scratch/orchestrator/drafts/dec991/SWEEP-DEC995.md` and
`ROLESPEC-DEC995-review.md` (record branch).

## 1. Context
DEC-995: a role is what it may read and write; a skill never widens that; a mixed ticket is split before it starts;
W2-82's Definition of Ready refuses mixed tickets. What each role may write today: engineer and product-spec, their
own ticket's paths (the difference is by kind: code and its unit tests vs schemas, templates, skills, role files,
briefs, docs, `.rulesync` sources, CIT-Ps); the test designer `tests/acceptance/**`; auditors and reviewers only
`docs/probes`, `docs/audit`, `docs/assessment` (guard rule 5); research exactly one folder under `experiments/`;
generated `.claude/` copies: no worker (the CTO, with your approval, DEC-991).

## 2. What the sweep found
- **Mixed, needing a child ticket (13 tickets):** W2-83a (its playbook entry in `gov check`'s schema map is code),
  W2-113 (its role-file sentences are W2-33's), W2-21 (one role file path), W2-88 (the adopt skill text and its
  proofs on GitHub clones), W2-82 (a template and a schema), W2-109 (one check in code), W2-35, W2-55, W2-19, W2-78,
  W2-34 (a schema or template each), W2-52 and W2-60a (in progress), W2-96 (merged; its kernel brief half is already
  done inside W2-11's resume). W2-11 itself: decided (W2-120).
- **Single-role:** W2-33 (but its paths miss `.rulesync/subagents/**` and the roster, and its role files need a CTO
  copy step; one optional engineer child if a handoff record must be refused by `gov check`), the rest (about 60).
- **Copies only** (`.claude/` generated copies, the CTO's step): W2-98 to W2-103, W2-60b, W2-23, W2-33, W2-83a.
- **Role and path conflicts that no split fixes (policy gaps):**
  - A. Nine engineer tickets write their measurement records under `docs/research/`, which only research may write.
  - B. Three auditor tickets (W2-93, W2-94, W2-61h) author evaluation sets in `fixtures/evaluation/**`, which rule 5
    refuses an auditor.
  - C. W2-40, W2-15a, W2-15b (research) name two folders; the launcher allows one.
  - D. Who writes a ticket's CIT-P and CIT-E, and whether kernel check YAML, maps, registries, lefthook and workflows
    are engineer config.
- **The roles spec:** ROLES-SPEC-1 still calls frontend, DevOps and UX Wave 3 *roles* (§3.10), keeps skill packs in
  Wave 3, has no machine-readable `Reads`/`Writes`/`Skills` per role, and gives the CTO every skill on demand
  (test-design included, whose output it may not write). W2-60a's reader (in progress) lets a session load every skill,
  not only its role's; six vendored openspec skills carry `allowed-tools` (a permission field in a skill).

## 3. Why it matters
Mixed tickets are where leads stall (W2-11 today: a refused launch); a skill that carries permissions breaks the
rule silently; EXAMIN's adopted product inherits the roles spec as written.

## 4. Options and recommendations (each needs your yes; P1 under DEC-974 for new tickets)
1. **The splits.** (a) Approve the 13 children as a list now; I file each one when its parent is next to be claimed
   (the WBS does not grow for tickets weeks away), parent and child in the order the sweep gives (e.g. W2-83a's
   schema before its code child). (b) File all now (about 124 to 137 tickets). (c) Approve only the near ones (W2-83a,
   W2-113, W2-33's gaps, W2-82) and bring the rest at their claim. **Rec (a).**
2. **W2-52** (in progress, DEC-738 item 1 contradicts DEC-995; DEC-105): apply now (its adopt-skill clause moves to
   W2-83a; its lead is not running) / defer / re-baseline. **Rec apply now.**
3. **Gap A, measurement records:** a ticket's measurement of its own change is the implementer's evidence, kept at
   `docs/changes/<id>-evidence.md`; research stays for work needing the network, a venv or an open question. **Rec yes.**
4. **Gap B, evaluation sets:** (a) the test designer's writes gain `fixtures/evaluation/**` (it is never the measured
   party, and never reads the implementation); (b) rule 5 lets an auditor write its own ticket's evaluation folder
   (loosens a guard rule). **Rec (a).**
5. **Gap C:** research tickets name one folder with their record inside it (W2-40, W2-15a, W2-15b paths fixed). Mine
   to do (P2) unless you object.
6. **Gap D:** a ticket's CIT-E is written by the role that made the change; a CIT-P goes to the product-spec child
   when there is one, else the lead drafts it; kernel check YAML, maps, registries, lefthook and workflows are engineer
   config; schemas, templates and `.rulesync` sources are product-spec. **Rec yes.**
7. **The roles KPI edits** (exact lines in the review): W2-33 (each role file: reads, writes as path classes, the
   closed list of skills it may load; no role lists a skill whose output its writes do not hold; domain work an
   engineer skill); W2-60a (a role loads only its listed skills; a skill with a permission field refuses the launch);
   W2-60b (session settings from the role file and ticket alone; a planted skill naming wider tools leaves them
   byte-identical); W2-11 round 2 (the skill template's front matter closed to name, version, description and output;
   no permission field); W2-120 (the validator refuses a skill with a permission key, plus the twelve-field line);
   W2-82 (a seventh readiness condition, ROLE_SCOPE: a ticket whose paths or KPI-named paths need another role's
   writes is NOT_READY, naming that role). Plus a product-spec pass on ROLES-SPEC-1 (nine section edits). **Rec yes.**
8. **The six openspec skills' `allowed-tools`:** strip it from our copies (vendored: recorded in the tool registry) /
   exempt them by name. **Rec strip.**

## 5. Confidence
Medium-high for 1, 3, 6, 7; medium for 4 (either option works; (a) keeps the guard's rules as they are).

## 6. What it blocks, and what waiting costs
W2-33 and W2-83a do not start until decided (they wait for W2-11 anyway, a day or so). W2-82 waits. Nothing running
now is blocked.
