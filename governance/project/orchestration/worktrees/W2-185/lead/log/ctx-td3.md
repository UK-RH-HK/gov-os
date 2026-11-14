{
  "ticket": "DAEO-qyt2",
  "ticket_text": "---\nid: DAEO-qyt2\nwbs_id: W2-185\nexternal-ref: W2-185\ntitle: \"Adopted projects get the context watch: the template wires context_watch.py, portability's lift exemption per hook, W1-38's fixture with seven hooks (W2-182's E gap)\"\ntype: task\nclass: implementation\nrole: engineer\nprofile: STANDARD\nstatus: in_progress\nstate_class: AUTHORITATIVE\npriority: 2\ncreated: 2026-11-13\ndeps: [DAEO-5y8d]\nallowed_paths:\n- template/.rulesync/hooks.jsonc\n- src/gov/adapters/portability.py\n- tests/unit/adapters/test_w2_185_*.py\n- tests/acceptance/W1-38/w1_38_support.py  # the fixture copies the seven kernel hooks; a test designer's revision (DEC-1156 (7))\n- docs/probes/DAEO-qyt2/**  # the probe record\n- tests/unit/gitenv/test_hooks_lifted.py\n- tests/acceptance/W2-59/test_w2_59_hook_lines.py\n- tests/acceptance/W2-59/test_w2_59_hook_lines_worker_env.py\n- tests/acceptance/W1-38/test_w1_38_hooks_any_folder.py\n- tests/acceptance/W1-38/test_w1_38_hooks_source.py\n- tests/acceptance/W1-38/w1_38_hooks_support.py\n- tests/unit/hooks/test_w2_106_template_hook_lines.py\n- tests/acceptance/W2-05/test_w2_05_hooks_source.py\nreads:\n- .tickets/DAEO-5y8d.md\n- .rulesync/hooks.jsonc\n- template/governance/kernel/hooks/**\n- tests/acceptance/W2-23/test_w2_23_space.py\n- tests/acceptance/W2-05/test_w2_05_hooks_source.py\n- tests/unit/gitenv/test_program_env.py\nneeds: []\nwaits_on: []\nkpis:\n  success:\n  - 'S1: the template''s hooks source `template/.rulesync/hooks.jsonc` wires `context_watch.py` in postToolUse (matcher Bash, timeout 10), in the root `.rulesync/hooks.jsonc`''s form with the adopted path `governance/kernel/hooks/` [DEC-1163 (6) E (a), DEC-1167] Verify: W2-23 S6 (`tests/acceptance/W2-23/test_w2_23_space.py`) passes, the settings'' hook lines reaching the seven kernel hooks; a planted eighth hook with no wiring fails it'\n  - 'S2: portability''s hooks comparison exempts the template''s `posttooluse.py` entry (DEC-971 item 3''s lift, per hook) rather than the whole postToolUse event, so the root''s and the template''s postToolUse compare on what both carry [DEC-971 item 3, DEC-805, DEC-1167] Verify: `tests/unit/gitenv/test_program_env.py::test_this_repository_s_two_hooks_sources_agree` and `tests/acceptance/W2-05/test_w2_05_hooks_source.py::test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources` pass with S1''s line; unit cases in `tests/unit/adapters/test_w2_185_*.py` for the exemption'\n  - 'S3: W1-38''s adopted-project fixture copies the seven kernel hooks (`w1_38_support.py` HOOK_SCRIPTS), so its generated settings name only scripts it copied [DEC-1167, DEC-1156 (7)] Verify: `tests/acceptance/W1-38/test_w1_38_rulesync.py::TestHookStubs::test_hook_stubs_exist` and `test_w1_38_hooks_any_folder.py`''s ordinary-call case pass with S1''s line; the fixture with six hooks fails them'\n  failure:\n  - 'F1: a hook that really drifts between the root and the template (another matcher or another event than the exempt `posttooluse.py` entry) is still a finding. Verify: a planted extra matcher on the root''s postToolUse, and a planted template hook in another event, each give a hooks finding'\nnon_goals:\n- 'not the root''s own hooks (`.rulesync/hooks.jsonc`, `.claude/`): no change to what this repository''s sessions run'\n- 'not W2-182''s other lines (B, C, R, D, F), which landed with W2-182'\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-1167, DEC-1163, DEC-971, DEC-805, DEC-1156]\nacceptance_tests: {path: tests/acceptance/W2-185/}\n---\n\n# W2-185 Adopted projects get the context watch (W2-182's E gap)\n\nThe owner's P-W2-182-E-1 (1) (DEC-1167): W2-182 lands without E; this ticket carries it as one piece. E's template line\nalone turned four cases red (W2-182 run 3, `log/W2-182-A5-run3.json`): portability's per-event lift exemption (DEC-971\nitem 3) let the root's and template's postToolUse match only by coincidence, and W1-38's fixture copies six hooks. A test\ndesigner writes W2-185's cases and revises W1-38's fixture; an engineer builds S1 and S2; a STANDARD review; the land.\n\n**Widened 2026-11-13 (P-W2-185-REDS-1 (a), the CTO under DEC-1156 (7)):** the eight test files holding the 18 cases that pin the behaviour before DEC-1167 (4), for one test-designer revision batch (each file one Rewrite-Reason, no case losing its point).\n",
  "authority": [
    {
      "id": "DEC-1167",
      "sha256": "d3c196337a6a1ef5fbcc55345eb477c5d04febd257b25a6f8934739b319812c6",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "d3c196337a6a1ef5fbcc55345eb477c5d04febd257b25a6f8934739b319812c6",
      "reason": "declared in sources",
      "tokens": 745
    },
    {
      "id": "DEC-1163",
      "sha256": "0a714eee77c47016c76087b707c8c056dbbffd2ffe4a59eeae59dc8436fe8729",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0a714eee77c47016c76087b707c8c056dbbffd2ffe4a59eeae59dc8436fe8729",
      "reason": "declared in sources",
      "tokens": 1014
    },
    {
      "id": "DEC-971",
      "sha256": "a942e33007c0cb90fa9a05a6327f9347068de27dd5fcfa6f6d14d26a1776d1f0",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a942e33007c0cb90fa9a05a6327f9347068de27dd5fcfa6f6d14d26a1776d1f0",
      "reason": "declared in sources",
      "tokens": 702
    },
    {
      "id": "DEC-805",
      "sha256": "f4d3e50ed399d3b5d3899871b01177b8abf6793f6ffef6222271dc438c433ced",
      "authority": "decision",
      "lifecycle": "DONE",
      "constraint": "f4d3e50ed399d3b5d3899871b01177b8abf6793f6ffef6222271dc438c433ced",
      "reason": "declared in sources",
      "tokens": 302
    },
    {
      "id": "DEC-1156",
      "sha256": "ae45fec87ddb5ad969cad9abbb5ec5ef4652208564394a7722aaf36c8b62db32",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ae45fec87ddb5ad969cad9abbb5ec5ef4652208564394a7722aaf36c8b62db32",
      "reason": "declared in sources",
      "tokens": 1068
    },
    {
      "id": "DAEO-5y8d",
      "sha256": "631367937ca0af0ea657fc1f50c6708396704fc8ac646ee614add91a0e21fc9d",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "631367937ca0af0ea657fc1f50c6708396704fc8ac646ee614add91a0e21fc9d",
      "reason": "declared in sources",
      "tokens": 623
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1167",
      "sha256": "d3c196337a6a1ef5fbcc55345eb477c5d04febd257b25a6f8934739b319812c6",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "d3c196337a6a1ef5fbcc55345eb477c5d04febd257b25a6f8934739b319812c6",
      "reason": "declared in sources",
      "tokens": 745
    },
    {
      "id": "DEC-1163",
      "sha256": "0a714eee77c47016c76087b707c8c056dbbffd2ffe4a59eeae59dc8436fe8729",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0a714eee77c47016c76087b707c8c056dbbffd2ffe4a59eeae59dc8436fe8729",
      "reason": "declared in sources",
      "tokens": 1014
    },
    {
      "id": "DEC-971",
      "sha256": "a942e33007c0cb90fa9a05a6327f9347068de27dd5fcfa6f6d14d26a1776d1f0",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a942e33007c0cb90fa9a05a6327f9347068de27dd5fcfa6f6d14d26a1776d1f0",
      "reason": "declared in sources",
      "tokens": 702
    },
    {
      "id": "DEC-805",
      "sha256": "f4d3e50ed399d3b5d3899871b01177b8abf6793f6ffef6222271dc438c433ced",
      "authority": "decision",
      "lifecycle": "DONE",
      "constraint": "f4d3e50ed399d3b5d3899871b01177b8abf6793f6ffef6222271dc438c433ced",
      "reason": "declared in sources",
      "tokens": 302
    },
    {
      "id": "DEC-1156",
      "sha256": "ae45fec87ddb5ad969cad9abbb5ec5ef4652208564394a7722aaf36c8b62db32",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ae45fec87ddb5ad969cad9abbb5ec5ef4652208564394a7722aaf36c8b62db32",
      "reason": "declared in sources",
      "tokens": 1068
    },
    {
      "id": "DAEO-5y8d",
      "sha256": "631367937ca0af0ea657fc1f50c6708396704fc8ac646ee614add91a0e21fc9d",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "631367937ca0af0ea657fc1f50c6708396704fc8ac646ee614add91a0e21fc9d",
      "reason": "declared in sources",
      "tokens": 623
    }
  ],
  "supplementary": [],
  "supplementary_query": "Adopted projects get the context watch: the template wires context_watch.py, portability's lift exemption per hook, W1-38's fixture with seven hooks (W2-182's E gap)\nS1: the template's hooks source `template/.rulesync/hooks.jsonc` wires `context_watch.py` in postToolUse (matcher Bash, timeout 10), in the root `.rulesync/hooks.jsonc`'s form with the adopted path `governance/kernel/hooks/` [DEC-1163 (6) E (a), DEC-1167] Verify: W2-23 S6 (`tests/acceptance/W2-23/test_w2_23_space.py`) passes, the settings' hook lines reaching the seven kernel hooks; a planted eighth hook with no wiring fails it\nS2: portability's hooks comparison exempts the template's `posttooluse.py` entry (DEC-971 item 3's lift, per hook) rather than the whole postToolUse event, so the root's and the template's postToolUse compare on what both carry [DEC-971 item 3, DEC-805, DEC-1167] Verify: `tests/unit/gitenv/test_program_env.py::test_this_repository_s_two_hooks_sources_agree` and `tests/acceptance/W2-05/test_w2_05_hooks_source.py::test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources` pass with S1's line; unit cases in `tests/unit/adapters/test_w2_185_*.py` for the exemption\nS3: W1-38's adopted-project fixture copies the seven kernel hooks (`w1_38_support.py` HOOK_SCRIPTS), so its generated settings name only scripts it copied [DEC-1167, DEC-1156 (7)] Verify: `tests/acceptance/W1-38/test_w1_38_rulesync.py::TestHookStubs::test_hook_stubs_exist` and `test_w1_38_hooks_any_folder.py`'s ordinary-call case pass with S1's line; the fixture with six hooks fails them\nF1: a hook that really drifts between the root and the template (another matcher or another event than the exempt `posttooluse.py` entry) is still a finding. Verify: a planted extra matcher on the root's postToolUse, and a planted template hook in another event, each give a hooks finding",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 5527,
  "budget": {
    "limit": 6000,
    "used": 5527
  },
  "hash": "71f87cdb231295ffc807779a914ad5ae33e6449f2ea3b7cbe6ffef46c6ca59a3"
}
