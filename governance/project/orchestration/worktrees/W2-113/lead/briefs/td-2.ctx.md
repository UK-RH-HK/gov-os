{
  "ticket": "DAEO-g29a",
  "ticket_text": "---\nid: DAEO-g29a\nstatus: in_progress\ndeps: [DAEO-3r1j, DAEO-siiz]\nlinks: [DAEO-3r1j]\ncreated: 2026-10-31T23:05:58Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-113\ntags: [wave-2, implementation, adoption, standard]\nwbs_id: W2-113\ntitle: 'An adopted product''s CTO is named at adoption: the adopt step writes the coordination-ticket key, the orchestrator role file states the CTO-only install rule, the refusal names GOV_TICKET (W2-110''s P-W2-110-2)'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on:\n- DAEO-3r1j\n- DAEO-siiz\nallowed_paths:\n- src/gov/adopt/stages.py\n- template/governance/kernel/hooks/permission_request.py\n- src/gov/guard/install.py\n- tests/unit/adopt/test_w2_113*\n- docs/probes/DAEO-g29a/**  # the probe record (the CTO, 2026-11-12)\nkpis:\n  success:\n  - 'Adoption writes the project''s `coordination_ticket` key from the coordination ticket it creates, so in a freshly adopted planted repository the orchestrator on that ticket is asked for an install and every other session is refused, with no hand edit Verify: a planted repository is adopted with no hand edit: the project''s config then holds `coordination_ticket` equal to the id of the coordination ticket adoption created; the guard decision for an install by the session on that ticket is ask, and for any other session is refuse. [DEC-971 item 4, DEC-982]'\n  - 'The refusal, when the rule cannot run (no key, or a key naming no ticket), names `GOV_TICKET` and says how to set the key, in words that are true in that case (W2-110''s review F5); it stays closed Verify: planted projects with no key and with a key naming no ticket: the install refusal text names `GOV_TICKET` and says how to set the key, the decision is still a refusal, and the text does not claim a key was set when none was. [DEC-971 item 4]'\n  failure:\n  - 'An adopted project whose CTO''s installs are refused until the key is written by hand. Verify: a freshly adopted planted repository: the CTO session''s install is asked at once (not refused) with no key edited by hand; a refusal there is the failure.'\n  - 'Any session but the CTO''s asked or let through. Verify: planted engineer, test-designer, auditor and a second orchestrator session on another ticket each attempt an install in the adopted planted repository: each is refused, none is asked or let through.'\n  moved:\n  - 'Both orchestrator role-file copies state the CTO-only install rule (was S2) and no copy keeps the old rule (was F2) [moved to W2-33, DEC-1156 (4): one writer for orchestrator.md, the product-spec role (DEC-995, DEC-996 (1))]'\n  lifted:\n  - 'The kernel ships a quiet-hours permission hook (the host''s PermissionRequest event; this repository''s `governance/project/orchestration/tools/permission_request.py` as the model): inside the configured quiet hours it refuses at once, with a message naming the morning package, and queues the call under `.gov-runtime/`; outside them it gives no answer (the normal prompt); any error inside them refuses; every prompt is recorded; adoption wires it into the adopted CTO''s local settings only, with onFailure block; in a freshly adopted planted repository a prompting call at a forced 03:00 is refused and queued, and at 12:00 is not [DEC-991, DEC-994 item 3] [lifted (was S4), DEC-1083: re-scoped by D9-FATES (INVESTIGATION-1 \u00a75)]'\nprofile: STANDARD\nsources:\n- DEC-971\n- DEC-957\n- DEC-982\n- DEC-974\n- DEC-1083\n- DEC-991\n- DEC-994\nest_loc: 60\nacceptance_tests:\n  path: tests/acceptance/W2-113/\n  author: independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer (DEC-963); a planted repository adopted from the template\ntrack: B\nlist_rows: []\n---\n# W2-113 An adopted product's CTO is named at adoption\n\nThe owner's decision on P1-NEW-TICKETS-2026-10-31 T1 (DEC-982), from W2-110's P-W2-110-2.\n\n- **Why:** W2-110 makes the kernel's guard ask the owner for an install only from the orchestrator on the project's coordination ticket (DEC-971 item 4), with the key \"set at adoption\", but nothing writes it at adoption; the role file still states the old rule (review F3) and the refusal's words mislead when the rule cannot run (F5).\n- **The work:** a product-spec worker rewrites the role file's lines (both copies), then an engineer makes the adopt step write the key and the refusal's words, one after the other.\n- **Order:** after W2-110 (`DAEO-3r1j`) and W2-52 (`DAEO-siiz`, which holds the adopt files); before EXAMIN's copy (W2-27). W2-33 holds the rest of the role file: this ticket changes only the install lines.\n\n## Interface (DEC-1052; PKG-1 (a), the owner, DEC-1156 (4), 2026-11-12)\n\n- **I1 Stage A0 creates it,** inside `src/gov/adopt/stages.py` only (no new flag): A0 creates the coordination ticket through `gov.tasks.tickets.create(root, \"<project> coordination\")` with `class: coordination`, writes `governance/project/roster.yaml` with a top-level `coordination_ticket: <new id>`, and records both in A0's record, committed in A0's commit with its set-up files (`safety.setup`).\n- **I2 The three defaults:** a roster that already names an existing ticket: A0 keeps it and creates nothing; a roster without the key: A0 adds the key and changes nothing else; `tk` missing: A0 completes without creating the ticket or the key, and its record says so; the guard stays closed (every install refused, the refusal naming `GOV_TICKET` and how to set the key) (PKG-3 (b), the owner, DEC-1157 (15); was: A0 refuses and writes nothing).\n- **I3 \"A planted repository adopted\"** for the tests: a planted git repository with the template copied in (copier, then `rulesync generate`, as in W2-110's suite), then `gov adopt --lite --stage A0`; then the guard's decisions for the orchestrator on that ticket (ask), and for an engineer, a test designer, an auditor and an orchestrator on another ticket (each refused).\n- **Note for W2-88 and W2-174:** A0 gains this output; keep it at merge.\n- **PKG-2 (b):** the role-file lines (was S2, F2) moved to W2-33; this ticket is engineer work only.\n- **The test designer's readings, confirmed by the CTO (DEC-1112 (3)):** `<project>` is the repository's folder name and the title is exact; a roster key may name its ticket by id or WBS id, as the guard resolves it; A0 keeps the roster's comments and line order. The refusal keeps the sentence \"Set the top-level key\" (W2-110's unit test at line 172).\n",
  "authority": [
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
      "id": "DEC-957",
      "sha256": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "reason": "declared in sources",
      "tokens": 2056
    },
    {
      "id": "DEC-982",
      "sha256": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "reason": "declared in sources",
      "tokens": 766
    },
    {
      "id": "DEC-974",
      "sha256": "de1682b7d5dab08c68e287f047f413be308cfe903a6d6e46b7825d53869a8058",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "de1682b7d5dab08c68e287f047f413be308cfe903a6d6e46b7825d53869a8058",
      "reason": "declared in sources",
      "tokens": 638
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
      "id": "DEC-991",
      "sha256": "f887ea1519992c853f1736d2dd0f650d88790308778f982ee6596fe9d7e4d362",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "f887ea1519992c853f1736d2dd0f650d88790308778f982ee6596fe9d7e4d362",
      "reason": "declared in sources",
      "tokens": 934
    },
    {
      "id": "DEC-994",
      "sha256": "cbbb35460c24cc4be24bf2a9eaf5c761f679e89b0b6b8768fadd14081933b5a2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "cbbb35460c24cc4be24bf2a9eaf5c761f679e89b0b6b8768fadd14081933b5a2",
      "reason": "declared in sources",
      "tokens": 637
    },
    {
      "id": "DAEO-3r1j",
      "sha256": "f0381273fe5f7506e7228a313302e4abc01c90befb9bae5edd14287f84d53a88",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "f0381273fe5f7506e7228a313302e4abc01c90befb9bae5edd14287f84d53a88",
      "reason": "declared in sources",
      "tokens": 390
    },
    {
      "id": "DAEO-siiz",
      "sha256": "b427572ba64180ae465a65d52c8a3294ba789fad240c734e815a66a795ce46a0",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "b427572ba64180ae465a65d52c8a3294ba789fad240c734e815a66a795ce46a0",
      "reason": "declared in sources",
      "tokens": 152
    }
  ],
  "mandatory": [
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
      "id": "DEC-957",
      "sha256": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "reason": "declared in sources",
      "tokens": 2056
    },
    {
      "id": "DEC-982",
      "sha256": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "reason": "declared in sources",
      "tokens": 766
    },
    {
      "id": "DEC-974",
      "sha256": "de1682b7d5dab08c68e287f047f413be308cfe903a6d6e46b7825d53869a8058",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "de1682b7d5dab08c68e287f047f413be308cfe903a6d6e46b7825d53869a8058",
      "reason": "declared in sources",
      "tokens": 638
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
      "id": "DEC-991",
      "sha256": "f887ea1519992c853f1736d2dd0f650d88790308778f982ee6596fe9d7e4d362",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "f887ea1519992c853f1736d2dd0f650d88790308778f982ee6596fe9d7e4d362",
      "reason": "declared in sources",
      "tokens": 934
    },
    {
      "id": "DEC-994",
      "sha256": "cbbb35460c24cc4be24bf2a9eaf5c761f679e89b0b6b8768fadd14081933b5a2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "cbbb35460c24cc4be24bf2a9eaf5c761f679e89b0b6b8768fadd14081933b5a2",
      "reason": "declared in sources",
      "tokens": 637
    },
    {
      "id": "DAEO-3r1j",
      "sha256": "f0381273fe5f7506e7228a313302e4abc01c90befb9bae5edd14287f84d53a88",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "f0381273fe5f7506e7228a313302e4abc01c90befb9bae5edd14287f84d53a88",
      "reason": "declared in sources",
      "tokens": 390
    },
    {
      "id": "DAEO-siiz",
      "sha256": "b427572ba64180ae465a65d52c8a3294ba789fad240c734e815a66a795ce46a0",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "b427572ba64180ae465a65d52c8a3294ba789fad240c734e815a66a795ce46a0",
      "reason": "declared in sources",
      "tokens": 152
    }
  ],
  "supplementary": [],
  "supplementary_query": "An adopted product's CTO is named at adoption: the adopt step writes the coordination-ticket key, the orchestrator role file states the CTO-only install rule, the refusal names GOV_TICKET (W2-110's P-W2-110-2)\nAdoption writes the project's `coordination_ticket` key from the coordination ticket it creates, so in a freshly adopted planted repository the orchestrator on that ticket is asked for an install and every other session is refused, with no hand edit Verify: a planted repository is adopted with no hand edit: the project's config then holds `coordination_ticket` equal to the id of the coordination ticket adoption created; the guard decision for an install by the session on that ticket is ask, and for any other session is refuse. [DEC-971 item 4, DEC-982]\nThe refusal, when the rule cannot run (no key, or a key naming no ticket), names `GOV_TICKET` and says how to set the key, in words that are true in that case (W2-110's review F5); it stays closed Verify: planted projects with no key and with a key naming no ticket: the install refusal text names `GOV_TICKET` and says how to set the key, the decision is still a refusal, and the text does not claim a key was set when none was. [DEC-971 item 4]\nAn adopted project whose CTO's installs are refused until the key is written by hand. Verify: a freshly adopted planted repository: the CTO session's install is asked at once (not refused) with no key edited by hand; a refusal there is the failure.\nAny session but the CTO's asked or let through. Verify: planted engineer, test-designer, auditor and a second orchestrator session on another ticket each attempt an install in the adopted planted repository: each is refused, none is asked or let through.",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 8584,
  "budget": {
    "limit": 9000,
    "used": 8584
  },
  "hash": "b5bc56211a206cb90fb854f15e188e11c97f5693274a2f210adfd6b78fded16a"
}
