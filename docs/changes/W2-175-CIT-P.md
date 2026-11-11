---
id: W2-175-CIT-P
type: change-impact-proposal
status: PROPOSED
state_class: EVIDENCE
date: 2026-11-11
branch: w2/W2-175
ticket: DAEO-wahn (W2-175)
author: product-spec (W2-175, round 1)
review: one read-only independent reviewer, reading the delta only (CAP-33, DEC-1116's route)
decisions_read: [DEC-1137, DEC-820, DEC-861, DEC-1116, DEC-1121, DEC-1050, DEC-105, DEC-957, DEC-963, DEC-1073, DEC-315]
decisions_carried: [DEC-1137, DEC-820, DEC-861, DEC-957, DEC-963, DEC-1116]
state: draft (round 1, the text; the review, the approval and the promotion are pending)
---

# W2-175: change-impact proposal (CIT-P) on the seven role templates

The seven kernel role templates (`template/governance/kernel/templates/role-*.md`, version 1.0.0 as approved by DEC-1116)
gain the lines below and go to version 1.0.1. They are kernel files, so the change goes through CIT-P under CAP-33, by
DEC-1116's route: a template delta, its independent review, the owner's approval of the new bytes.

Base commit (the commit the ticket's branch starts from): `7709021ad6cc26aa24ca00a3285e58afde299f65`.

## 1. Evidence

| # | Trigger | Source |
|---|---|---|
| E1 | The owner decided (2026-11-11) that the role templates carry Policy 2's four refusals (DEC-820), DEC-861's record rule and the stop after two refusals, in a small ticket that lands before EXAMIN's copy; W2-27 depends on it | DEC-1137 (2), (3) |
| E2 | A launched session reads its role template as its system prompt, so a rule that is in no template is a rule that session never sees | W2-153 (the launch delivery); DEC-1116 |
| E3 | At the base, `role-engineer.md` and four others state none of Policy 2's refusals; `role-test-designer.md` holds only the counterpart half in one line (its item 4); only `role-cto.md` states DEC-861's record rule (its line 29); the stop after two refusals is in `brief.md`'s return section and in no role template | `governance/project/orchestration/packages/P1-W2-11-BRIEFS.md`; the seven files at the base |
| E4 | The wording is DEC-820 item 2 (a) to (d) and item 3, the engineer's and the designer's halves of (c) from DEC-820 item 2 (c) with DEC-957 and DEC-963, DEC-861 item 2 for the record rule, and `brief.md` line 62 for the stop | the ticket's Interface section; the register entries |

Corroboration: DEC-820 (the owner's own words of 2026-10-19), DEC-1137 (the owner's answer of 2026-11-11) and the package
`P1-W2-11-BRIEFS.md` name the same three rules and the same gap.

## 2. Proposal

Additions only. No rule a template already carries is reworded and no rule beyond the three the owner named is added
(DEC-1137 (2)); a statement is one paragraph on one line and ends with its decision id in brackets. `version` goes from
1.0.0 to 1.0.1 in each file and no other front matter key changes. `role-cto.md`'s decision-record line (file line 29 at
the base) is unchanged byte for byte and `role-cto.md` gets no new record line. `role-test-designer.md`'s item 4 is kept as
it is; the designer's (c) statement is added beside it with the half it lacked.

The statements added (the words of the ticket's Interface section):

- P2: "Reads are open: the whole repository, other worktrees, git history and what your searches return. Refuse only four things: secrets and keys (never printed); the held-out qualification material's contents (its file names may be seen); the counterpart's work on the same ticket; the hidden half of an evaluation set [DEC-820]."
- C-E (engineer): "Never read this ticket's acceptance-test code; run its cases and read their names, pass or fail and failure messages [DEC-820, DEC-957]."
- C-D (designer): "Never read this ticket's implementation (what its branch changes other than your own tests); work from the specification, the KPI lines and the existing code [DEC-820, DEC-963]."
- C-R (reviewer): "You read everything, tests and code alike [DEC-820]."
- REC (the six non-CTO templates): "The owner's decisions are recorded by the orchestrator's decision-record commits; never put `Role: owner` or `Decided-by:` on a commit of yours [DEC-861]."
- STOP (all seven, copied from `brief.md` line 62): "Refused twice for the same call: stop and say so. Never work around a refusal: report it. [DEC-1137]"

| File | Base sha256 | New sha256 | Statements added |
|---|---|---|---|
| `template/governance/kernel/templates/role-cto.md` | `1b1745571c511037bf12cd3b5ddfe246606963a4216a58044855ddf349198ce8` | `013d4d85bc5d55b2d858f6f07f10f949bccdc85e20458c2c45e4c3d6cfd67abd` | P2, STOP (2) |
| `template/governance/kernel/templates/role-engineer.md` | `7f18eebbe71129b504b51e01c921f9a2ca125e157db9fbdbae7bc56d738622b3` | `6775f2d9b99ee96f10653a12da24a34cbf282da9312b37b4e714206ef333889b` | P2, C-E, REC, STOP (4) |
| `template/governance/kernel/templates/role-lead.md` | `8279168522102c64a9f4b4ef5b7f4abe489499adcb34c43403a98e7fc0ce6c7e` | `4e8e46b097797d13f70c8828f41562b768bfb19f06160dac87ee7e308aa590a9` | P2, REC, STOP (3) |
| `template/governance/kernel/templates/role-product-spec.md` | `66d556c0ff90ba9d2bc9516c2151ce87590aaf8a789705b097929daf1f844d10` | `5683e56fab5b7d44923557a4d7a54255ff7bb6c5e4ad88fd54e466ee5a822b5f` | P2, REC, STOP (3) |
| `template/governance/kernel/templates/role-research.md` | `6f63e5b23b213a5f88894303cd685c2f2e819f158da01aee14ba653960656b3b` | `fc41bfc1cf3bd5576080739b16cac992bb9ae912a6519b74b560b6d3af0c5799` | P2, REC, STOP (3) |
| `template/governance/kernel/templates/role-reviewer.md` | `bec50839cad9cea5f5470f52d6b4856ea0d28c080810dbf6beff0c82e94e19f0` | `eff256eb02771c1edf8433dc563f190df56df509d2cc8076b91cd6e97bdb65b7` | P2, C-R, REC, STOP (4) |
| `template/governance/kernel/templates/role-test-designer.md` | `3a0bfd4abbeef355f230350913236b1d9f7071cfac36f24768c758d4f211cad3` | `c1f449fbe338fc32ebc583e7e6ce57afb690bf4339cd7bf41b30a0f52fb8b990` | P2, C-D, REC, STOP (4) |

The base sha256 values are those of the files at the base commit; the new values are `sha256sum` of each file after the
last template edit (they must equal `sha256sum` at the ticket's head).

The CTO's scope amendment (P-2 (a)) added these six byte-determined compositions; the root `.rulesync/` copies follow by the copies ACT after the owner's approval.

| File | Base sha256 | New sha256 | Statements added |
|---|---|---|---|
| `template/.rulesync/subagents/engineer.md` | `be528c5a52019183df147c5a640aaf347433c293c0184f528c8fc193a9bc6d2d` | `33155d8015ac24a628a771596a3a7cb093526ef95821616a0e87564fc8ae9d86` | composed by `compose()` from the role's template (W2-153 S3) |
| `template/.rulesync/subagents/independent-auditor.md` | `f4fcb152cfaff5ece77bde9706cf8fc93aa63ef1b32f43b247bc14d2a24b6437` | `6bd4dfd519f18b3af142b30ce47ffefe1ada25206d86cb09d7314f0ea3a4e08e` | composed by `compose()` from the role's template (W2-153 S3) |
| `template/.rulesync/subagents/independent-test-designer.md` | `04cc3f44f5c32fd7584debae544d80a9b567053f58477fdabe5f9b64329f2599` | `42fae108dda88dd8c42feffe95e3cc75a4496d25be019471ddd4866aabb24c68` | composed by `compose()` from the role's template (W2-153 S3) |
| `template/.rulesync/subagents/orchestrator.md` | `b2f717c4ecca3d7ae6ea0b4eda6de5021f9425961a4ab1a9c29cc832c71aee54` | `692efdee2df95685d9a405c0c835a9b9cfe141ccbeb65b75250bad8ebac40333` | composed by `compose()` from the role's template (W2-153 S3) |
| `template/.rulesync/subagents/product-spec.md` | `c8c04a03bfc75dd9a8172b65be01652aa3b627b2d130d2f24e013e711275597d` | `787f5a04bad04dba13957c9bf321fb607f331a56620e6fa822e8d28a7bc566fa` | composed by `compose()` from the role's template (W2-153 S3) |
| `template/.rulesync/subagents/research.md` | `2b8e2b217397d4b91ce51cfd5d03b8cc9757d2b20ec5f55fb944bf9347fe674f` | `3b9d6a3d28b5320ad23344afe44b43498c6d3bf66d61d48c2d1cdda3bbb1e13a` | composed by `compose()` from the role's template (W2-153 S3) |

Prose size (W2-128's `prose()` measure) against the budget of `governance/project/facts.yaml`:

| Template | Base | New | Budget |
|---|---|---|---|
| role-cto | 3177 | 3605 | 6000 |
| role-engineer | 1204 | 1926 | 3500 |
| role-lead | 4604 | 5188 | 8000 |
| role-product-spec | 1553 | 2137 | 3500 |
| role-research | 1344 | 1928 | 3500 |
| role-reviewer | 2550 | 3188 | 3500 |
| role-test-designer | 1832 | 2595 | 3500 |

The three options (DEC-105):

| Option | What it means here | Cost |
|---|---|---|
| **Apply now** (the owner's decision, DEC-1137 (2), (3)) | The lines above land in the seven templates as version 1.0.1, before EXAMIN's copy | This ticket's one product-spec round, its acceptance tests, one delta review, the owner's approval, one copies ACT |
| Defer | Keep the templates at 1.0.0 | A launched session keeps lacking the three rules (E2, E3); W2-27 stays blocked (DEC-1137 (3)) |
| Re-baseline | Put the rules in `brief.md` only | Set aside in the ticket: every session reads `brief.md`, but a role's system prompt would still lack them, and the owner asked for the templates |

Not changed: `brief.md`, the five `brief-*.md` pointers, `keys.yaml`, `facts.yaml`, any skill, any file under `roles/`, the root
`.rulesync/`, any `.claude/` path.

The `.claude/templates/role-*.md` copies are not written here: the copies ACT writes them after the owner's approval
(DEC-315). Until it runs, `python3 -m gov.adapters.portability` reports `TEMPLATE_COPY_DIFFERS` for the seven files (as
after W2-128); this ticket's close names that finding and does not fix it.

## 3. Independent review

Pending. The lead fills this section after one read-only independent review of the delta (`git diff 7709021ad6cc..HEAD`
on the seven templates), with its READY from the verdict block (DEC-1010).

## 4. Owner's approval

Pending. Not filled by the product-spec session: the owner approves the new bytes (the sha256 column of section 2) by the
route of DEC-1116.

## 5. Versioned promotion

Pending. On the owner's approval the kernel template set is promoted at the approved bytes: the seven role templates
from 1.0.0 to 1.0.1; this record's `status` becomes ACCEPTED only then; the `.claude/templates/` copies follow by the
copies ACT.
