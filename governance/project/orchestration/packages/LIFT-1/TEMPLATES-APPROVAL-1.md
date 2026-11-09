# TEMPLATES-APPROVAL-1: the owner's approval of W2-128's templates (CAP-33; R2-3: product-spec writes, the owner approves)

- **For:** the owner. **By:** the CTO (orchestrator `DAEO-sdxk`), 2026-11-09. **Under:** DEC-1050 (TEMPLATES),
  DEC-1052 (the templates' four recommendations, READY and DONE by code), CAP-33 (a kernel change needs the owner's
  approval before its versioned promotion), W2-128's CIT-P KPI line. **Record:** `docs/changes/W2-128-CIT-P.md`
  (PROPOSED).
- **State:** round 1 merged at `c6aefae9`. Hashes below are at integrate `97f39dc4`. Review READY
  (`reviews/w2-128-r1.md`); the review's F1-F5 and F9 fixed before the merge. `gov accept W2-128`: 92/92.
  W1-35's brief cases 7/7; W1-30's template-ticket cases 13/13. Schema: 970 records valid.

## What you approve
The kernel's template set, version 1.0.0, as these bytes:

| what | file | version | sha256 |
|---|---|---|---|
| T-0 envelope | `template/governance/kernel/templates/brief.md` | 1.0.0 | `004ce0fc8f09dcc89a8ecda0b0a0ef813737323719aac3e469a1eac6ee4cfe6d` |
| T-1 ticket | `template/governance/kernel/templates/ticket.md` | 1.0.0 | `fd97779dc4987d0015c1f4615a82b7d6c9c8ff0e302bfcda89b7f6fc9e4af956` |
| T-2 research | `template/governance/kernel/templates/role-research.md` | 1.0.0 | `6f63e5b23b213a5f88894303cd685c2f2e819f158da01aee14ba653960656b3b` |
| T-3 product-spec | `template/governance/kernel/templates/role-product-spec.md` | 1.0.0 | `66d556c0ff90ba9d2bc9516c2151ce87590aaf8a789705b097929daf1f844d10` |
| T-4 test designer | `template/governance/kernel/templates/role-test-designer.md` | 1.0.0 | `3a0bfd4abbeef355f230350913236b1d9f7071cfac36f24768c758d4f211cad3` |
| T-5 engineer | `template/governance/kernel/templates/role-engineer.md` | 1.0.0 | `7f18eebbe71129b504b51e01c921f9a2ca125e157db9fbdbae7bc56d738622b3` |
| T-6 reviewer | `template/governance/kernel/templates/role-reviewer.md` | 1.0.0 | `bec50839cad9cea5f5470f52d6b4856ea0d28c080810dbf6beff0c82e94e19f0` |
| T-7 lead | `template/governance/kernel/templates/role-lead.md` | 1.0.0 | `8279168522102c64a9f4b4ef5b7f4abe489499adcb34c43403a98e7fc0ce6c7e` |
| T-8 CTO | `template/governance/kernel/templates/role-cto.md` | 1.0.0 | `1b1745571c511037bf12cd3b5ddfe246606963a4216a58044855ddf349198ce8` |
| the key list | `template/governance/kernel/templates/keys.yaml` | — | `91c4601e520cc64aeb1723416c6f3d8a96960dbc9ba7399d28961b9775a8cd25` |
| record template | `template/governance/kernel/templates/checkpoint.md` | — | `9c2de37e7bd88f7fc80035a4793cba0b30d7ffc70d49580b75f3efc7d81e96bb` |
| record template | `template/governance/kernel/templates/decision-record.md` | — | `ae7982e60db9fbf7580f6ea8d3e7b977d76fd97538ad16091c8400899dc6ef7d` |
| record template | `template/governance/kernel/templates/decision-package.md` | — | `2c8d46c21aa4b8f28451741bed15b9fb08bf9e9d6cef4857bf3aebbe0f5fa36f` |
| record template | `template/governance/kernel/templates/failure.md` | — | `324669e6791ac12a8fa05ee537a6900f0ad47ee5229a0d4a5eeb65d91b373428` |
| record template | `template/governance/kernel/templates/lesson.md` | — | `88a14217387f897a9deed6dc42cd0fd703e4fa41282330701baaa2da82809189` |
| record template | `template/governance/kernel/templates/research.md` | — | `9ec14b2ad4c233b4fb450046638617e0b2ad4689b8ff73cf795216b681234497` |
| schema | `template/governance/kernel/schemas/facts.schema.json` | — | `be3e204355c0dd4c98cc584b72a1cef5eaa4733ca9a7feec8684b728026af7a6` |
| schema | `template/governance/kernel/schemas/ticket.schema.json` | — | `18da2c0e761ae67cb9a03d9b9436ff1fec0856b4b3374402e3e502c92a38a196` |
| schema | `template/governance/kernel/schemas/lesson.schema.json` | — | `84ef434dfd391e936b81782f45e20169f7bdfd19288607118730403eda9a2631` |
| schema | `template/governance/kernel/schemas/failure.schema.json` | — | `3a0b6c57d6d8e31c3ead750b06270ce1daedb56170691ad879140c12194a3ad2` |
| schema | `template/governance/kernel/schemas/research.schema.json` | — | `1c6dbf370dbc0437b7ef7d7e42a62431088e7d6042908442541ed301c7cddec3` |
| role line 5 | `template/governance/kernel/roles/engineer.md` | — | `66c094102c731f9e5e4504af393fca5954c5fe8afdcc93eeba9f457367233c5f` |
| project facts (the CTO approves; listed for the record) | `governance/project/facts.yaml` | — | `9dd69dc23a56b1bf0dd523351d56d2f56cbbdb6841679d33b4615bd1e944a084` |

Approving them means:
1. The CIT-P record moves from PROPOSED to ACCEPTED, with your approval line.
2. The set is promoted as version 1.0.0 of the kernel templates.
3. The templates become the one source for briefs: the CTO prompt's Appendix A goes on your separate yes
   (`TPL6-APPENDIX-A.md`), and `LEAD-w2-common.md` already points at them (`15c606f6`).

## What is still open (it does not wait on this approval)
- **Round 2a (text, W2-128):** review F6 (the orchestration skill and `roles/orchestrator.md` still describe the
  retired brief texts), F7 (the test-design skill forbids the integrated code that T-4 and DEC-963 permit), and the
  `DAEO-0000` in `checkpoint.md`'s example. These are kernel skill and role edits, so they join this CIT-P.
- **The code half:** W2-152 (`gov brief`, the ready check) and W2-153 (delivery at launch), both engineer tickets.
- **The measures and the pilot:** TPL-7 and TPL-8 (M1 to M6 against R2's baselines). These show whether the
  templates are read and followed; the approval does not wait on them.

## Recommendation (the CTO's)
**One approval after round 2a merges**, with this table refreshed to that commit: one sitting, and every kernel line of
the CIT-P in it. If you prefer to approve the 1.0.0 set now, round 2a comes back as a 1.1.0 delta.

## What you say
"Templates approved at `<commit>`" (or "approve 1.0.0 now; round 2a as a delta").
