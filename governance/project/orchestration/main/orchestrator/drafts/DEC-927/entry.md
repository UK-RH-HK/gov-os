
### DEC-927 — P-TRACE-IMPL-1: the 39 commits whose `Implements:` names a role are accepted as history, by the owner's own commit; briefs fill `Implements:` with ids only
- **Status:** ACCEPTED (owner, 2026-10-27, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-27)`) · **Under:** DEC-734, DEC-891, DEC-895, DEC-862 (a), DEC-925 item 2, DEC-861 · **Basis:** package P-TRACE-IMPL-1 (`governance/project/orchestration/packages/P-TRACE-IMPL-1.md`). After W2-70's close (2026-10-27, exit 0), gate (b) went red on product traceability: closed tickets' commits must name ids the store resolves, and seven of W2-70's carry `Implements: independent-test-designer`. The lead briefs' `IMPL` slot had been filled with a role, so leads and their workers wrote a role there in 39 commits of seven tickets.
- **Decision:**
  1. **These 39 commits are accepted as history,** each `{commit: <full id>, decision: DEC-927}` in the path map's `accepted_history`, by the owner's own `Role: owner` commit (26 change only records, 13 change code, tests or notes; DEC-891). Validated with the pinned judge's readers before the ACT (DEC-895). The commits, with their changed paths (`git show --name-only`):
       - `09c327d2172662a166fa10dd593b8c74eabdca74` (DAEO-9nys, Role: orchestrator, `Implements: engineer`; record-only): `docs/probes/DAEO-9nys/PR-DAEO-9nys.md`
       - `60f71c4298bc38cb01bc37a2e6cd0406de8fdaa4` (DAEO-9nys, Role: orchestrator, `Implements: engineer`; record-only): `docs/checkpoints/DAEO-9nys/CP-DAEO-9nys-0004.md`
       - `915a764dd660d1ff2d08944042dd05c6fc02a6a4` (DAEO-9nys, Role: orchestrator, `Implements: engineer`; record-only): `docs/checkpoints/DAEO-9nys/CP-DAEO-9nys-0012.md`
       - `f1c743b3ee92b95b31a5c29cde2e756c9ace969b` (DAEO-9nys, Role: orchestrator, `Implements: engineer`; record-only): `docs/checkpoints/DAEO-9nys/CP-DAEO-9nys-0008.md`
       - `1475b46c9186bf2201023a4ba658b2ee3f3449a6` (DAEO-c1uz, Role: orchestrator, `Implements: engineer`; record-only): `docs/checkpoints/DAEO-c1uz/CP-DAEO-c1uz-0002.md`
       - `5634d4305a7c4f9b677bed6a6cea26ea53c96c94` (DAEO-c1uz, Role: orchestrator, `Implements: engineer`; record-only): `docs/checkpoints/DAEO-c1uz/CP-DAEO-c1uz-0011.md`
       - `9174e358d77bbb0829a3c6ea9694026018686e9b` (DAEO-c1uz, Role: orchestrator, `Implements: engineer`; record-only): `docs/checkpoints/DAEO-c1uz/CP-DAEO-c1uz-0007.md`
       - `ba38ab8d758b3ab9147c951f30aaafbe9b80eaeb` (DAEO-c1uz, Role: orchestrator, `Implements: engineer`; record-only): `docs/checkpoints/DAEO-c1uz/CP-DAEO-c1uz-0004.md`
       - `20d72c1936118e06b86b5eef16c3157e83e6aa94` (DAEO-e82f, Role: orchestrator, `Implements: engineer`; record-only): `docs/checkpoints/DAEO-e82f/CP-DAEO-e82f-0004.md`
       - `33401f46ad00189bbab9584138888f44f543c57e` (DAEO-e82f, Role: orchestrator, `Implements: engineer`; record-only): `docs/checkpoints/DAEO-e82f/CP-DAEO-e82f-0002.md`
       - `04878e23252ad3b32c6308ed2ced6db72a062ab6` (DAEO-e82f, Role: engineer, `Implements: engineer`; code, tests or notes): `src/gov/hooks/subagentstop.py`, `template/governance/kernel/hooks/subagentstop.py`
       - `9e2b97758e2474d8c4b61a3ec54aad724c786965` (DAEO-e82f, Role: engineer, `Implements: engineer`; code, tests or notes): `.rulesync/hooks.jsonc`, `src/gov/hooks/subagentstop.py`, `template/.rulesync/hooks.jsonc`, `template/governance/kernel/hooks/subagentstop.py`, `tests/unit/hooks/test_w29_hooks.py`
       - `44062fecf53bdcda83cb3c4bfc668945be5c8709` (DAEO-r9ss, Role: orchestrator, `Implements: engineer`; record-only): `docs/checkpoints/DAEO-r9ss/CP-DAEO-r9ss-0005.md`
       - `614817ec7d6c7a3a9fcf55849c40f414006905b2` (DAEO-r9ss, Role: orchestrator, `Implements: engineer`; record-only): `docs/checkpoints/DAEO-r9ss/CP-DAEO-r9ss-0010.md`
       - `80ec31ab61b844888ddc05470aa12ce3d768e908` (DAEO-r9ss, Role: orchestrator, `Implements: engineer`; record-only): `docs/checkpoints/DAEO-r9ss/CP-DAEO-r9ss-0011.md`
       - `8e9ce18db1c52f1861ce5e579ca4298d0833ea13` (DAEO-r9ss, Role: orchestrator, `Implements: engineer`; record-only): `docs/checkpoints/DAEO-r9ss/CP-DAEO-r9ss-0007.md`
       - `d2eee219625e620b75b118c109c3778a2aa21a37` (DAEO-r9ss, Role: orchestrator, `Implements: engineer`; record-only): `docs/checkpoints/DAEO-r9ss/CP-DAEO-r9ss-0008.md`
       - `e8ad70b51c91b274dfdbb29e57bd15ccdcd9c08c` (DAEO-r9ss, Role: orchestrator, `Implements: engineer`; record-only): `docs/checkpoints/DAEO-r9ss/CP-DAEO-r9ss-0002.md`
       - `34e1c59f06e6a158bfd0cf0e00c2d83633d69647` (DAEO-rmbe, Role: orchestrator, `Implements: engineer`; record-only): `docs/probes/DAEO-rmbe/PR-DAEO-rmbe.md`
       - `3fd2b5a1e664d7c987a2c9a3ffaafd99f4c60a01` (DAEO-rmbe, Role: orchestrator, `Implements: engineer`; record-only): `docs/checkpoints/DAEO-rmbe/CP-DAEO-rmbe-0004.md`
       - `527345b7bf43b8f05d9ccb16e39d0c79c0a02563` (DAEO-rmbe, Role: orchestrator, `Implements: engineer`; record-only): `docs/checkpoints/DAEO-rmbe/CP-DAEO-rmbe-0003.md`
       - `cfea8a26e668c49f60f1fa936b6295d661f47dc5` (DAEO-rmbe, Role: orchestrator, `Implements: engineer`; record-only): `docs/checkpoints/DAEO-rmbe/CP-DAEO-rmbe-0006.md`
       - `e00fd14a26be19069aeb904418d2dfa7ac868dcb` (DAEO-rmbe, Role: orchestrator, `Implements: engineer`; record-only): `docs/checkpoints/DAEO-rmbe/CP-DAEO-rmbe-0008.md`
       - `e4687ef4cf5631d91b8672d6e139a9a244b6e68f` (DAEO-rmbe, Role: orchestrator, `Implements: engineer`; record-only): `docs/checkpoints/DAEO-rmbe/CP-DAEO-rmbe-0002.md`
       - `0808dbb6e8ffb9dab21e991689adea990323f8a6` (DAEO-rmbe, Role: engineer, `Implements: engineer`; code, tests or notes): `src/gov/secrets/__init__.py`
       - `2f03393d848672981c0071ecaa18e08cb3a78977` (DAEO-rmbe, Role: engineer, `Implements: engineer`; code, tests or notes): `src/gov/secrets/__init__.py`, `tests/unit/secrets_check/test_stored_forms.py`
       - `6b1d54fe6cc03ce8899912726799457157a17e01` (DAEO-rmbe, Role: engineer, `Implements: engineer`; code, tests or notes): `src/gov/rebuild/command.py`, `src/gov/secrets/__init__.py`, `tests/unit/secrets_check/__init__.py`, `tests/unit/secrets_check/test_scan_scale.py`, `tests/unit/secrets_check/test_secrets.py`, `tests/unit/secrets_check/test_token_rule.py`
       - `6ebc7cf7f74c1c0bbd03a763a7e1d84f7a88fc21` (DAEO-rmbe, Role: engineer, `Implements: engineer`; code, tests or notes): `docs/research/W2-69-secrets-scan.md`
       - `6f2ec438a6fa9b28b703609ff2c96f7855158c5a` (DAEO-rmbe, Role: engineer, `Implements: engineer`; code, tests or notes): `docs/research/W2-69-secrets-scan.md`
       - `8663196dd9445d990f68faaaa34729ec520889e9` (DAEO-rmbe, Role: engineer, `Implements: engineer`; code, tests or notes): `docs/research/W2-69-secrets-scan.md`, `src/gov/rebuild/command.py`, `src/gov/secrets/__init__.py`, `tests/unit/rebuild/test_compaction.py`, `tests/unit/secrets_check/test_stored_forms.py`
       - `9d22d9807a440c02ee0a20d4dbf249837183bae3` (DAEO-rmbe, Role: engineer, `Implements: engineer`; code, tests or notes): `tests/unit/rebuild/test_compaction.py`
       - `dc05ffe45ee2fccb9f8bf90ec4df6f9e4c033e54` (DAEO-rmbe, Role: engineer, `Implements: engineer`; code, tests or notes): `docs/research/W2-69-secrets-scan.md`
       - `5baafb04661140673a70e246b61d4ab2a064e0b7` (DAEO-uzme, Role: orchestrator, `Implements: independent-test-designer`; record-only): 
       - `8b318157db948890ede906618e6b31732e915ea6` (DAEO-uzme, Role: orchestrator, `Implements: independent-test-designer`; record-only): `docs/checkpoints/DAEO-uzme/CP-DAEO-uzme-0002.md`
       - `e04e6ee6effecd971eb7b3021762fd4a8d40769a` (DAEO-uzme, Role: orchestrator, `Implements: independent-test-designer`; record-only): `docs/checkpoints/DAEO-uzme/CP-DAEO-uzme-0003.md`
       - `e052b7b5a8539c1cd9fbd734164e9d28b28d4c1f` (DAEO-uzme, Role: orchestrator, `Implements: independent-test-designer`; record-only): `docs/checkpoints/DAEO-uzme/CP-DAEO-uzme-0005.md`
       - `39574e4ee5151dedc5742a89dea75a5a37c37c31` (DAEO-uzme, Role: independent-test-designer, `Implements: independent-test-designer`; code, tests or notes): `tests/acceptance/W1-01/test_w1_01_integration_merges.py`, `tests/acceptance/W1-01/w1_01_support.py`
       - `78522dea7ce462aca566a7db23565a5c0dc248d9` (DAEO-uzme, Role: independent-test-designer, `Implements: independent-test-designer`; code, tests or notes): `tests/acceptance/W1-01/test_w1_01_history.py`, `tests/acceptance/W1-01/w1_01_support.py`
       - `f409ad97575a32f6aab96e6ee6bcb4b7bc008691` (DAEO-uzme, Role: independent-test-designer, `Implements: independent-test-designer`; code, tests or notes): `tests/acceptance/W1-05/README.md`, `tests/acceptance/W1-05/test_w1_05_switch_over_record.py`, `tests/acceptance/W1-05/w1_05_support.py`, `tests/acceptance/W1-30/test_w1_30_r11_declared_here.py`, `tests/acceptance/W1-47/README.md`, `tests/acceptance/W1-47/test_w1_47_session_role.py` and 1 more
  2. **Briefs fill `Implements:` with ids only:** `tools/build_lead_brief.py` refuses an `IMPL` that is not a decision or Contract id. W2-57's two lead commits with `Implements: engineer` are listed by a further entry when W2-57 merges.
- **Where it goes:** this register; the path map (the owner's commit); `tools/build_lead_brief.py`; RESUME HERE; the daily digest.
- Next free id: DEC-928.

| Version | Date | Change |
|---|---|---|
| 0.313 | 2026-10-27 | Owner (recorded by the orchestrator, DEC-861): DEC-927 (P-TRACE-IMPL-1: 39 commits whose Implements names a role accepted as history by the owner's commit; briefs fill Implements with ids only). Next free id: DEC-928. |
