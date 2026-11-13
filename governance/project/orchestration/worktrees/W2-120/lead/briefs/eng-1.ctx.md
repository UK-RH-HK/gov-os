{
  "ticket": "DAEO-i89t",
  "ticket_text": "---\nid: DAEO-i89t\nstatus: in_progress\ndeps: [DAEO-k7hz]\nlinks: [DAEO-k7hz]\ncreated: 2026-11-01T15:16:06Z\ntype: task\npriority: 2\nassignee: engineer\nexternal-ref: W2-120\ntags: [wave-2, implementation, skills, standard]\nwbs_id: W2-120\ntitle: 'The skill validator refuses a brief without the twelve-field rule and a skill whose front matter carries a permission field (W2-11''s child engineer ticket, DEC-995)'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: [DAEO-k7hz]\nallowed_paths:\n- src/gov/check/skill_validator.py\n- tests/unit/check/test_w2_120*\nkpis:\n  success:\n  - 'gov check''s skill validator refuses a skill whose front matter carries a key outside the skill template''s list (the \"no output class\" half deferred, DEC-1156 (2)) (allowed-tools, permissions, paths, sandbox, network, model, effort or any other), naming the file and the key; it reads the kernel skills and every generated copy, and names each vendored skill so found Verify: planted skills: one with no output class, one with each of the listed keys (allowed-tools, permissions, paths, sandbox, network, model, effort) and one with another key: `gov check` refuses each, printing the file and the key; a planted vendored skill is named; a planted copy under the generated folders is read as well as the kernel one; a clean skill passes. [DEC-995, DEC-996, CAP-24.b]'\n  failure: []\n  lifted:\n  - 'The \"no output class\" half: gov check''s skill validator refuses a skill whose front matter has no output class [DEC-995, DEC-996] [deferred, DEC-1156 (2): waits for a product-spec follow-up that adds `output` to the 10 kernel skills in all three copies; this ticket names no missing output]'\n  - 'gov check''s skill validator refuses a brief template without the twelve-field rule (the twelve labelled return fields, the payload-after rule and the two-refusal stop), naming the file and what is missing; the kernel''s five brief templates as W2-11 leaves them pass [AR-5, AR-6, W2-L097, DEC-995] [lifted (was S1), DEC-1083: re-scoped to S3]'\n  - 'The validator checks every `gov` command a skill or brief names against the reserved command list, not the gov installed on the machine [W2-L097] [lifted (was S2), DEC-1083: re-scoped to S3]'\n  - 'A brief template without the twelve-field rule, or a skill with allowed-tools or another permission key in its front matter, that the validator passes [DEC-995] [lifted (was F1), DEC-1083: re-scoped to S3]'\nprofile: STANDARD\nsources:\n- DEC-995\n- DEC-996\n- DEC-992\n- CAP-24.b\n- DEC-718\n- DEC-1083\nest_loc: 80\nacceptance_tests:\n  path: tests/acceptance/W2-120/\n  author: independent-test-designer (MR-3)\ntrack: A\nlist_rows: [W2-L097]\n---\n# W2-120 The skill validator: the twelve-field rule and closed skill front matter\n\nThe owner's decision on P-W2-11-9 (c) (DEC-995, DEC-996): W2-11 (a product-spec ticket) cannot hold code, so its\nvalidator failure line and row W2-L097 move here, to an engineer, after W2-11 lands (W2-11's skill template and\nbriefs are what this validator checks). The closed skill front matter is DEC-996 item 4's line for this ticket.\n\n## Interface (DEC-1052; P-W2-120-1 (b), the owner, DEC-1156 (2), 2026-11-12)\n\n- **I1 Output:** the existing JSON on stdout, `{\"findings\": [...]}`, each finding with `code`, `file`, `key` and `message`; exit 1 when any finding refuses, 0 when clean (a named-only finding never changes the exit).\n- **I2 What is refused, on every copy read:** a permission key (allowed-tools, permissions, paths, sandbox, network, model, effort) or any key outside the skill template's list (`template/governance/kernel/templates/skill.md`: name, version, description, output, metadata.version). For the generated copies under `.claude/skills/` the list is name, description and metadata (rulesync drops the other top-level keys).\n- **I3 Which copies:** from the kernel folder it is given (`--both-layouts`), the validator itself finds the kernel source, `.rulesync/skills/`, `template/.rulesync/skills/` and `.claude/skills/`, so `gov check` reads them with no edit to the three skill-regression check files.\n- **I4 Vendored skills** (openspec-*, superpowers/*): named, `code` `SKILL_VENDORED_KEY` with file and key, exit unchanged, until DEC-996 item 5 strips them.\n- **Deferred:** a missing `output` is not refused by this ticket (its line is lifted above; W2-142 S1/S2 and the hard-block checks stay green).\n",
  "authority": [
    {
      "id": "DEC-995",
      "sha256": "b0543edf119247c03260286eb37528a0156ba8cbf7324a74d30ba078edf9bb11",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b0543edf119247c03260286eb37528a0156ba8cbf7324a74d30ba078edf9bb11",
      "reason": "declared in sources",
      "tokens": 660
    },
    {
      "id": "DEC-996",
      "sha256": "388151798cf1224477e5ac5e4ef28b9fe9abb1575c37dacf1bb52dae20baec22",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "388151798cf1224477e5ac5e4ef28b9fe9abb1575c37dacf1bb52dae20baec22",
      "reason": "declared in sources",
      "tokens": 610
    },
    {
      "id": "DEC-992",
      "sha256": "017dd84cad213843918b8b27a62d56ea5877eac9e9a2ec0eb5085d358e3a7100",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "017dd84cad213843918b8b27a62d56ea5877eac9e9a2ec0eb5085d358e3a7100",
      "reason": "declared in sources",
      "tokens": 466
    },
    {
      "id": "DEC-718",
      "sha256": "1934518e5b019b8a75d1943f41ee4552b3c806a8743b5417a822c4ef25febe48",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1934518e5b019b8a75d1943f41ee4552b3c806a8743b5417a822c4ef25febe48",
      "reason": "declared in sources",
      "tokens": 4248
    },
    {
      "id": "DEC-1083",
      "sha256": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "reason": "declared in sources",
      "tokens": 711
    },
    {
      "id": "CAP-24.b",
      "sha256": "097119caecfe83f8508d37fb60cd3a6900892716b3c9ddfeaea25f67c541ac95",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "097119caecfe83f8508d37fb60cd3a6900892716b3c9ddfeaea25f67c541ac95",
      "reason": "declared in sources",
      "tokens": 150
    },
    {
      "id": "DAEO-k7hz",
      "sha256": "6d163009510d2c629c67c492b4689479e81ca28488849a0136163ed238ea01c7",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "6d163009510d2c629c67c492b4689479e81ca28488849a0136163ed238ea01c7",
      "reason": "declared in sources",
      "tokens": 1533
    }
  ],
  "mandatory": [
    {
      "id": "DEC-995",
      "sha256": "b0543edf119247c03260286eb37528a0156ba8cbf7324a74d30ba078edf9bb11",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b0543edf119247c03260286eb37528a0156ba8cbf7324a74d30ba078edf9bb11",
      "reason": "declared in sources",
      "tokens": 660
    },
    {
      "id": "DEC-996",
      "sha256": "388151798cf1224477e5ac5e4ef28b9fe9abb1575c37dacf1bb52dae20baec22",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "388151798cf1224477e5ac5e4ef28b9fe9abb1575c37dacf1bb52dae20baec22",
      "reason": "declared in sources",
      "tokens": 610
    },
    {
      "id": "DEC-992",
      "sha256": "017dd84cad213843918b8b27a62d56ea5877eac9e9a2ec0eb5085d358e3a7100",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "017dd84cad213843918b8b27a62d56ea5877eac9e9a2ec0eb5085d358e3a7100",
      "reason": "declared in sources",
      "tokens": 466
    },
    {
      "id": "DEC-718",
      "sha256": "1934518e5b019b8a75d1943f41ee4552b3c806a8743b5417a822c4ef25febe48",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1934518e5b019b8a75d1943f41ee4552b3c806a8743b5417a822c4ef25febe48",
      "reason": "declared in sources",
      "tokens": 4248
    },
    {
      "id": "DEC-1083",
      "sha256": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "reason": "declared in sources",
      "tokens": 711
    },
    {
      "id": "CAP-24.b",
      "sha256": "097119caecfe83f8508d37fb60cd3a6900892716b3c9ddfeaea25f67c541ac95",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "097119caecfe83f8508d37fb60cd3a6900892716b3c9ddfeaea25f67c541ac95",
      "reason": "declared in sources",
      "tokens": 150
    },
    {
      "id": "DAEO-k7hz",
      "sha256": "6d163009510d2c629c67c492b4689479e81ca28488849a0136163ed238ea01c7",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "6d163009510d2c629c67c492b4689479e81ca28488849a0136163ed238ea01c7",
      "reason": "declared in sources",
      "tokens": 1533
    }
  ],
  "supplementary": [],
  "supplementary_query": "The skill validator refuses a brief without the twelve-field rule and a skill whose front matter carries a permission field (W2-11's child engineer ticket, DEC-995)\ngov check's skill validator refuses a skill whose front matter carries a key outside the skill template's list (the \"no output class\" half deferred, DEC-1156 (2)) (allowed-tools, permissions, paths, sandbox, network, model, effort or any other), naming the file and the key; it reads the kernel skills and every generated copy, and names each vendored skill so found Verify: planted skills: one with no output class, one with each of the listed keys (allowed-tools, permissions, paths, sandbox, network, model, effort) and one with another key: `gov check` refuses each, printing the file and the key; a planted vendored skill is named; a planted copy under the generated folders is read as well as the kernel one; a clean skill passes. [DEC-995, DEC-996, CAP-24.b]",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 9476,
  "budget": {
    "limit": 12000,
    "used": 9476
  },
  "hash": "0b9c4c752eb0a193edd9dc516e1ae68f63fc1311079141871705afb221cb71ac"
}
