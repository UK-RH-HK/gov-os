# TEMPLATES-APPROVAL-1: the owner's approval of W2-128's templates (CAP-33; R2-3: product-spec writes, the owner approves)

- **For:** the owner. **By:** the CTO (orchestrator `DAEO-sdxk`), 2026-11-09. **Under:** DEC-1050 (TEMPLATES),
  DEC-1052 (the templates' four recommendations, READY and DONE by code), CAP-33 (a kernel change needs the owner's
  approval before its versioned promotion), W2-128's CIT-P KPI line. **Record:** `docs/changes/W2-128-CIT-P.md`
  (PROPOSED).
- **State (refreshed 2026-11-10 at integrate `1bf23a0b3e77`):**
  - All of W2-128's kernel text is merged: round 1 `c6aefae9`, round 2a `010ecbc5`, round 2b `f3c15908`. The code is
    merged too: W2-152 `b0bbd373`, W2-153 `27ab8f88`.
  - Reviews READY: round 1, round 2a, round 2b, W2-152 (round 2), W2-153.
  - `gov accept` on integrate: W2-128 121/121, W2-152 67/67, W2-153 51/51.
  - The generated copies: ACT-CLAUDE-COPIES-1 applied (`eb48fe2f`); ACT-CLAUDE-COPIES-2 ready for your yes. It
    touches no file in this table, so the table does not move with it.
  - One known follow-up, not in this approval: five test-design lines still cite CAP-38.b (DECIDED-NOT-DONE row 89),
    a 1.2.1 delta.

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
| record template | `template/governance/kernel/templates/checkpoint.md` | — | `1de5fff0a9e33818b03294afc6d0d08d651c6c2b908c1cf9949e4e41fb9661ad` |
| record template | `template/governance/kernel/templates/decision-record.md` | — | `ae7982e60db9fbf7580f6ea8d3e7b977d76fd97538ad16091c8400899dc6ef7d` |
| record template | `template/governance/kernel/templates/decision-package.md` | — | `2c8d46c21aa4b8f28451741bed15b9fb08bf9e9d6cef4857bf3aebbe0f5fa36f` |
| record template | `template/governance/kernel/templates/failure.md` | — | `324669e6791ac12a8fa05ee537a6900f0ad47ee5229a0d4a5eeb65d91b373428` |
| record template | `template/governance/kernel/templates/lesson.md` | — | `88a14217387f897a9deed6dc42cd0fd703e4fa41282330701baaa2da82809189` |
| record template | `template/governance/kernel/templates/research.md` | — | `9ec14b2ad4c233b4fb450046638617e0b2ad4689b8ff73cf795216b681234497` |
| schema | `template/governance/kernel/schemas/facts.schema.json` | — | `3141d5da38d7a2a1dcf654f83354f4fc6f2ce16bb383c03d6a906e221bd6448c` |
| schema | `template/governance/kernel/schemas/ticket.schema.json` | — | `18da2c0e761ae67cb9a03d9b9436ff1fec0856b4b3374402e3e502c92a38a196` |
| schema | `template/governance/kernel/schemas/lesson.schema.json` | — | `84ef434dfd391e936b81782f45e20169f7bdfd19288607118730403eda9a2631` |
| schema | `template/governance/kernel/schemas/failure.schema.json` | — | `3a0b6c57d6d8e31c3ead750b06270ce1daedb56170691ad879140c12194a3ad2` |
| schema | `template/governance/kernel/schemas/research.schema.json` | — | `1c6dbf370dbc0437b7ef7d7e42a62431088e7d6042908442541ed301c7cddec3` |
| role, line 5 (DEC-957) | `template/governance/kernel/roles/engineer.md` | — | `66c094102c731f9e5e4504af393fca5954c5fe8afdcc93eeba9f457367233c5f` |
| role, the lead's brief line (round 2a F6) | `template/governance/kernel/roles/orchestrator.md` | — | `4acff7e7ec8eaa289341d3ab452df814c18699df8abcffabaea7569d0b0f397c` |
| skill (rounds 2a, 2b) | `template/governance/kernel/skills/orchestration/SKILL.md` | 1.2.0 | `38933016185c63cc053c1fc1f2d25747d0b42c1ccdcbe082a78371bfb231c858` |
| skill (rounds 2a, 2b) | `template/governance/kernel/skills/test-design/SKILL.md` | 1.2.0 | `0428b9864d0a3c2f36532c241ad22c6369f05102c41ee99c532929edf5e9f60b` |
| project facts (the CTO approves; listed for the record) | `governance/project/facts.yaml` | — | `0f96904c561457f7f4b7dbf9595ef70feb35797d6e067caa78942693176e70d5` |

Approving them means:
1. The CIT-P record moves from PROPOSED to ACCEPTED, with your approval line.
2. The set is promoted as version 1.0.0 of the kernel templates.
3. The templates become the one source for briefs: the CTO prompt's Appendix A goes on your separate yes
   (`TPL6-APPENDIX-A.md`), and `LEAD-w2-common.md` already points at them (`15c606f6`).

## What is still open (it does not wait on this approval)
- **The test-design skill's five remaining CAP-38.b citations** (row 89), as a later 1.2.1 delta.
- **Round 2a (text, W2-128):** review F6 (the orchestration skill and `roles/orchestrator.md` still describe the
  retired brief texts), F7 (the test-design skill forbids the integrated code that T-4 and DEC-963 permit), and the
  `DAEO-0000` in `checkpoint.md`'s example. These are kernel skill and role edits, so they join this CIT-P.
- **The code half:** W2-152 (`gov brief`, the ready check) and W2-153 (delivery at launch), both engineer tickets.
- **The measures and the pilot:** TPL-7 and TPL-8 (M1 to M6 against R2's baselines). These show whether the
  templates are read and followed; the approval does not wait on them.

## Recommendation (the CTO's)
**Approve now, at this table:** rounds 1, 2a and 2b are all in it, and nothing in it moves with ACT-2.

## What you say
"Templates approved at `1bf23a0b3e77`".
